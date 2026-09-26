"""RBT-106: the patchy world is one field, the arms share RBT-104's command, and the "held" rule."""
import dataclasses
import importlib.util
import os
import re
import shlex

import numpy as np
import pytest

from rabbitstew.cli import _sim_config, build_parser
from rabbitstew.simulation import Simulation

HERE = os.path.dirname(__file__)
RUNS = os.path.join(HERE, "..", "runs")


def _load(name, *path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(RUNS, *path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cmd = _load("rbt106_command", "RBT-106", "command.py")


def _flat(d, p=""):
    out = {}
    for k, v in d.items():
        out.update(_flat(v, p + k + ".") if isinstance(v, dict) else {p + k: v})
    return out


def _sim(extra):
    args = build_parser().parse_args(cmd.part2() + ["--seed", "801", "--out", "/nonexistent"] + extra)
    return _sim_config(args)


def test_food_patches_is_one_field_of_the_sim_config():
    base, patchy = _flat(dataclasses.asdict(_sim([]))), _flat(dataclasses.asdict(_sim(["--food-patches", "3"])))
    diff = sorted(k for k in base if base[k] != patchy[k])
    assert diff == ["food.patches"]
    assert patchy["food.patches"] == 3 and patchy["food.regrow_delay"] == 0.0  # not the persistent world


def test_food_patches_zero_is_the_default():
    assert dataclasses.asdict(_sim(["--food-patches", "0"])) == dataclasses.asdict(_sim([]))


def test_uniform_world_draws_no_patch_centre():
    """patches = 0 consumes no food random number for centres, so the uniform world's food is as it was."""
    obj = Simulation.__new__(Simulation)  # the method alone: it reads only config.food and _food_rng
    obj.config = _sim([])
    obj._food_rng = np.random.default_rng(7)
    before = obj._food_rng.bit_generator.state
    assert Simulation._draw_patch_centres(obj).shape == (0, 2)
    assert obj._food_rng.bit_generator.state == before


def test_arm_commands_share_rbt104s_s1_command():
    """RBT-106's S1 is RBT-104's S1 line for line, but for the output and founders directories."""
    src = open(os.path.join(RUNS, "RBT-104", "run_arm.sh")).read()
    line = re.search(r"exec python -m rabbitstew\.cli (.*?) > \"\$OUT/run\.log\"", src, re.S).group(1)
    theirs = shlex.split(line.replace("\\\n", " ").replace('"${SEASONS:-600}"', "600").replace('"${WORKERS:-2}"', "2")
                         .replace('"$SEED"', "801").replace('"$OUT"', "OUT").replace('"${EXTRA[@]}"', ""))
    theirs += ["--from-conventional", "FOUNDERS"]
    ours = cmd.command("S1", 801, "OUT")[3:]
    i = ours.index("--from-conventional")
    ours[i + 1] = "FOUNDERS"
    assert ours == theirs


@pytest.mark.parametrize("a,b,flag", [("HU", "HP", ["--food-patches", "3"]), ("S1", "P1", ["--food-patches", "3"]),
                                      ("S8", "P8", ["--food-patches", "3"]), ("S1", "S8", ["--link-scale", "8"])])
def test_each_pair_differs_by_the_one_flag(a, b, flag):
    assert cmd.command(b, 4, "OUT") == cmd.command(a, 4, "OUT") + flag


def test_s8_is_rbt104s_s8_command():
    """The factorial's uniform K = 8 cell is RBT-104's S8: its S1 command plus --link-scale 8, as run_arm.sh has it."""
    src = open(os.path.join(RUNS, "RBT-104", "run_arm.sh")).read()
    assert 'S8) EXTRA=(--from-conventional "runs/RBT-104/founders-$SEED" --link-scale 8)' in src
    assert cmd.command("S8", 4, "OUT")[-2:] == ["--link-scale", "8"]


def test_h_and_p_pairs_differ_only_in_their_founders():
    h, p = cmd.command("HU", 4, "OUT"), cmd.command("S1", 4, "OUT")
    assert [x for x in h if "founders" not in x] == [x for x in p if "founders" not in x]


def test_held_criterion():
    held = _load("rbt106_held_rule", "RBT-106", "held.py")
    assert held.hit(13.0, +1.0, "pay32") and not held.hit(12.0, +1.0, "pay32")
    assert not held.hit(-30.0, +1.0, "pay32")               # wrong sign
    assert held.hit(-30.0, None, "pay32")                   # a bare-rooted carrier counts at either sign
    assert held.hit(0.01, -1.0, "same") is False and held.hit(-0.01, -1.0, "same")
    assert held.hit(None, +1.0, "same") is False
    assert held.CRITERION[(32.0, 1.0)][0] == "pay32" and held.CRITERION[(1.0, 1.0)][0] == "same"
    assert held.CRITERION[(1.0, 8.0)][0] == "pay64" and held.hit(25.0, 1.0, "pay64") and not held.hit(24.0, 1.0, "pay64")
