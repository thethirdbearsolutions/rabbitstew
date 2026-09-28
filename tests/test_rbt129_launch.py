"""RBT-129 launch readiness (runs/RBT-129/launch/): the world blocks, the pre-launch prints and the Stage P / Stage 0
launchers.  Nothing here runs a sweep arm: the runner is exercised on a tiny non-sweep world only."""
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "runs", "RBT-129", "launch"))
import blocks  # noqa: E402
import prints  # noqa: E402
import stages  # noqa: E402

from rabbitstew.ecology import Ecology  # noqa: E402
from rabbitstew.cli import build_parser, ecology_configs  # noqa: E402
from rabbitstew.world import Scenery, Shape  # noqa: E402
from rabbitstew import quat  # noqa: E402


def test_the_grid_is_150_unique_ids_that_parse_back():
    ids = blocks.all_ids()
    assert len(ids) == 150 == len(set(ids))
    for pid in ids:
        assert blocks.point_id(*blocks.parse_id(pid)) == pid
    assert "c1-p030-PW-G" in ids and "c05-p018-HP-L" in ids and "c15-p053-U-G" in ids
    assert set(blocks.PILOT) | set(blocks.ANCHORS) | set(blocks.PAYS_CELLS) <= set(ids)
    assert len(blocks.PAYS_CELLS) == 18 == len(set(blocks.PAYS_CELLS))


@pytest.mark.parametrize("layout,counts,radius", [("U", (0, 7, 14, 21, 28), 2.6), ("HP", (0, 7, 14, 21, 28), 2.6),
                                                  ("PW", (0, 16, 32, 48, 64), 3.6)])
def test_obstacle_counts_are_the_registered_free_area_counts(layout, counts, radius):
    for c, n in zip(blocks.CLUTTER, counts):
        argv = blocks.world_argv(blocks.point_id(c, 0.03, layout, "G"))
        args = build_parser().parse_args(["ecology", *argv])
        if n == 0:
            assert args.terrain == "flat"
        else:
            assert (args.terrain, args.obstacles, args.obstacle_radius) == ("random", n, radius)


def test_the_axes_reach_the_config():
    b = blocks.block("c2-p053-PW-G")["block"]
    assert b["sim.world.random_obstacles"] == 64 and b["sim.world.random_radius"] == 3.6
    assert b["sim.food.work_cost"] == 0.053 and b["sim.food.smell_contrast"] == 2.5 and b["sim.food.smell_tau"] == 2.0
    assert (b["sim.food.patches"], b["sim.food.patch_radius"], b["sim.food.radius"]) == (2, 0.4, 4.0)
    assert (b["sim.food.regrow_delay"], b["sim.food.smell"], b["sim.food.decay"]) == (60.0, "log", 1.5)
    assert b["sim.food.eat_from"] == "root" and b["ecology.sweep_log"] is True
    assert (b["ecology.living_cost"], b["ecology.initial_energy"], b["ecology.capacity"], b["ecology.group_size"]) == (0.25, 3.0, 60, 4)
    u = blocks.block("c1-p010-U-L")["block"]
    assert u["sim.food.patches"] == 0 and u["sim.food.radius"] == 3.0 and "sim.food.smell_contrast" not in u
    assert u["sim.world.terrain"] == "random" and u["sim.world.random_obstacles"] == 14 and u["sim.world.random_radius"] == 2.6
    assert blocks.block("c0-p030-U-L")["block"]["sim.world.terrain"] == "flat"
    for f in blocks.ARM_FIELDS:
        assert f not in u


def test_a_block_is_the_config_json_the_ecology_writes(tmp_path):
    """The export's block is read from the config.json that `ecology` itself writes for those flags (no season run)."""
    pid = "c1-p030-PW-G"
    exported = json.loads(open(blocks.export(str(tmp_path / "worlds"), [pid])[0]).read())
    assert exported["id"] == pid and exported["fair_pending"] is True and exported["argv"] == blocks.world_argv(pid)
    args = build_parser().parse_args(["ecology", *exported["argv"], "--seed", "129001", "--seasons", "300"])
    evo, eco = ecology_configs(args)
    Ecology(evo, eco, out_dir=str(tmp_path / "arm"), log=None)  # writes config.json at construction; runs nothing
    written = blocks._flatten(json.loads((tmp_path / "arm" / "config.json").read_text()))
    assert exported["block"] == {k: v for k, v in written.items() if k not in blocks.ARM_FIELDS}
    assert written["seed"] == 129001 and written["ecology.seasons"] == 300


def test_fair_flags_enter_argv_and_block():
    b = blocks.block("c1-p030-U-L", fair=["--motor-budget", "1.77"])
    assert b["fair_pending"] is False and b["argv"][-3:] == ["--motor-budget", "1.77", "--sweep-log"]
    assert b["block"]["sim.world.motor_budget"] == 1.77 and "sim.world.motor_budget" not in blocks.block("c1-p030-U-L")["block"]


def test_footprint_mask_on_constructed_obstacles():
    box = Scenery(Shape.BOX, (1.0, 0.2, 0.3), (0.0, 0.0, 0.15), tuple(quat.yaw(np.pi / 2)))  # long axis along y
    cyl = Scenery(Shape.CYLINDER, (0.3, 0.05), (2.0, 0.0, 0.025))  # 5 cm tall
    sph = Scenery(Shape.SPHERE, (0.5,), (-2.0, 0.0, -0.3))  # sunk: ground circle radius 0.4
    items = np.array([[0.0, 0.45], [0.45, 0.0], [2.0, 0.25], [2.0, 0.35], [-2.0, 0.39], [-2.0, 0.41], [5.0, 5.0]])
    assert prints.footprint_mask(items, [box, cyl, sph]).tolist() == [True, False, True, False, True, False, False]
    assert prints.footprint_mask(items, [box, cyl, sph], tall=0.1).tolist() == [True, False, False, False, True, False, False]


def test_unreachable_share_is_zero_on_flat_and_positive_in_clutter():
    assert prints.unreachable("c0-p030-U-L", 3)[:2] == (0.0, 0.0)
    share, tall, total = prints.unreachable("c2-p030-U-L", 10)
    assert total == 120 and 0.0 < tall <= share < 1.0


def test_food_per_new_cell_covers_ground():
    key, food, cells = prints.cell_season(("k", "c0-p030-U-L", "pioneer-drive", 1000, [], list(blocks.EAT_CANDIDATE)))
    assert key == "k" and cells > 20 and food >= 0.0


def test_the_committed_prints_are_the_prints_script():
    text = open(os.path.join(os.path.dirname(HERE), "runs", "RBT-129", "launch", "prints.txt")).read()
    assert "## unreachable items" in text and "## food per new cell" in text
    assert text.count("\n  ") == 15 + 30


def test_the_guards_refuse_on_this_tree(tmp_path):
    if "--fair" in stages.ecology_options():
        pytest.skip("RBT-128's --fair has merged: the guard now passes")
    with pytest.raises(SystemExit) as e:
        stages.check_fair(["--fair"])
    assert e.value.code == 4
    with pytest.raises(SystemExit):
        stages.check_fair([])
    with pytest.raises(SystemExit) as e:
        stages.emit(["P"], 10, str(tmp_path), ["--fair"], list(blocks.EAT_CANDIDATE))
    assert e.value.code == 4 and not (tmp_path / "lanes").exists()
    with pytest.raises(SystemExit) as e:
        stages.main(["prelaunch", "--fair=--fair", "--root", str(tmp_path)])
    assert e.value.code == 4
    stages.check_fair(["--motor-budget", "1.77"])  # a flag the tree has passes


def test_the_steer_guard_refuses_until_the_file_exists(tmp_path):
    missing = tmp_path / "steer.py"
    with pytest.raises(SystemExit) as e:
        stages.main(["probes", "--steer", str(missing), "--steer-cmd", "python {run}", "--root", str(tmp_path)])
    assert e.value.code == 6
    with pytest.raises(SystemExit) as e:
        stages.main(["pays", "--steer", str(missing), "--pays-cmd", "python {point}", "--root", str(tmp_path)])
    assert e.value.code == 6
    missing.write_text("# stand-in\n")
    with pytest.raises(SystemExit) as e:  # present, but no command template
        stages.main(["probes", "--steer", str(missing), "--root", str(tmp_path)])
    assert e.value.code == 6
    assert stages.main(["pays", "--steer", str(missing), "--pays-cmd", "steer {point} {world} {out}", "--root", str(tmp_path)]) == 0
    lines = (tmp_path / "lanes" / "pays.sh").read_text().splitlines()[2:]
    assert len(lines) == 18 and lines[0].startswith("steer c0-p030-U-L ")
    assert stages.main(["probes", "--steer", str(missing), "--steer-cmd", "steer {run} {season} {rng} {out}", "--root", str(tmp_path)]) == 0
    assert len((tmp_path / "lanes" / "probes.sh").read_text().splitlines()[2:]) == 4 * 4 * 2


def test_the_plan_is_the_design_and_within_budget(tmp_path):
    p = stages.plan(["P", "0"], 10, str(tmp_path))
    assert p["arm_seasons"]["P"] == 16 * (60 + 240 * 3) + 4 * (65 + 5)
    assert p["arm_seasons"]["0"] == 150 * 3 * 60
    (p20, p25), (c20, c25) = p["core_h"]["P"]["total"], p["core_h"]["0"]["total"]
    assert c20 == (195.0, 195.0) and c25[1] <= 232.5
    extras = 4 * stages.PLANTED_POINT + stages.core_h(4 * 70)[1]  # the planted set and K1, beyond the r4 line
    # the r4 table rounds its per-seed arm costs (1.67 + 1.33 + 1.33 core-h); 1 core-h covers that rounding
    assert p25[1] <= stages.BUDGET["P"][1][1] + extras + 1.0 and p20[1] <= stages.BUDGET["P"][0][1] + extras + 1.0
    total = stages.BUDGET["total"][1][1] + stages.BUDGET["anchor fallback"][1][1] + (p25[1] - stages.BUDGET["P"][1][1])
    assert total <= stages.BRIEF_ENVELOPE[1]


@pytest.mark.parametrize("which", [["P"], ["0"], ["P", "0"]])
def test_the_host_layout_places_every_unit_once_and_splits_seeds(tmp_path, which):
    units = stages.units_for(which, str(tmp_path))
    lanes = stages.layout(units, 10)
    names = [j["name"] for lane in lanes for u in lane for j in u["jobs"]]
    assert sorted(names) == sorted(j["name"] for u in units for j in u["jobs"])
    for h in range(10):
        a, b = lanes[2 * h], lanes[2 * h + 1]
        common = {u["seed"] for u in a} & {u["seed"] for u in b}
        # a seed on both lanes of a session is the split census seed: lane 1 holds only its census jobs, and runs them last
        assert all(u.get("shared") for u in b if u["seed"] in common)
        assert all(u.get("shared") or u["stage"] == "P" for u in a if u["seed"] in common)
        if any(u.get("shared") for u in a):
            k = max(i for i, u in enumerate(a) if u.get("shared"))
            assert all(u.get("shared") for u in a[:k + 1])  # lane 0 runs the shared seed first
        if any(u.get("shared") for u in b):
            k = min(i for i, u in enumerate(b) if u.get("shared"))
            assert all(u.get("shared") for u in b[k:])  # lane 1 runs it last
    loads = [sum(j["cost"] for u in lane for j in u["jobs"]) for lane in lanes]
    if "0" in which:
        assert max(loads) <= 1.05 * np.mean(loads)
    else:  # 16 pilot chains on 20 lanes: one chain a lane
        assert sorted(len(lane) for lane in lanes) == [0] * 4 + [1] * 16
    for u in units:
        if u["stage"] == "P":
            chain = [j["name"].split("/")[-1] for j in u["jobs"]]
            assert chain[:5] == ["S60", "ckpt60", "S", "M", "N"]
            n = next(j for j in u["jobs"] if j["name"].endswith("/N"))
            assert n["set"]["merge_null"] == ("holistic" if u["seed"] % 2 else "conventional")


TINY = ["--capacity", "4", "--challenge", "foraging", "--group-size", "2", "--brain-model", "foraging", "--food-items", "4",
        "--duration", "0.4", "--terrain", "flat", "--conventional-topology", "--score", "food", "--living-cost", "0.05",
        "--initial-energy", "2", "--birth-threshold", "0.5", "--birth-cost", "0.2", "--max-age", "6"]


def test_the_runner_forks_and_checks_k1_on_a_tiny_world(tmp_path, monkeypatch):
    """The lane runner's job kinds on a tiny non-sweep world: fresh to the checkpoint, snapshot, resume, the M and N
    forks, and K1 (a straight run against the fork with the merge unset)."""
    monkeypatch.setenv("NO_DURABLE", "1")
    monkeypatch.setenv("WORKERS", "1")
    worlds = tmp_path / "worlds"
    worlds.mkdir()
    (worlds / "tiny.json").write_text(json.dumps({"id": "tiny", "argv": TINY + ["--sweep-log"], "fair": ["--sweep-log"]}))
    d = tmp_path / "pt" / "7"
    base = {"worlds": str(worlds), "seed": 7}
    jobs = [
        {"job": "fresh", "name": "x/S60", "point": "tiny", "dir": f"{d}/S", "seasons": 3},
        {"job": "snapshot", "name": "x/ckpt60", "src": f"{d}/S", "dir": f"{d}/ckpt60", "season": 3},
        {"job": "resume", "name": "x/S", "dir": f"{d}/S", "seasons": 5},
        {"job": "fork", "name": "x/M", "src": f"{d}/ckpt60", "dir": f"{d}/M", "seasons": 5, "set": {"merge_after": 3, "pooled_capacity": 8}},
        {"job": "fork", "name": "x/N", "src": f"{d}/ckpt60", "dir": f"{d}/N", "seasons": 5,
         "set": {"merge_after": 3, "pooled_capacity": 8, "merge_null": "holistic"}},
        {"job": "fresh", "name": "x/K1ref", "point": "tiny", "dir": f"{d}/K1ref", "seasons": 5},
        {"job": "fork", "name": "x/K1fork", "src": f"{d}/ckpt60", "dir": f"{d}/K1fork", "seasons": 5, "set": {}},
        {"job": "k1", "name": "x/K1", "ref": f"{d}/K1ref", "dir": f"{d}/K1fork"},
    ]
    for j in jobs:
        stages.run_job({**base, **j})
    assert (d / "K1.txt").read_text().startswith("K1 PASS")
    for arm in ("S", "K1ref"):  # S itself (checkpoint, then resumed) is the straight run too
        assert (d / arm / "history.json").read_bytes() == (d / "K1ref" / "history.json").read_bytes()
    m = json.loads((d / "M" / "config.json").read_text())["ecology"]
    n = json.loads((d / "N" / "config.json").read_text())["ecology"]
    assert m["merge_after"] == 3 and "merge_null" not in m and n["merge_null"] == "holistic"
    assert json.loads((d / "ckpt60" / "config.json").read_text())["ecology"].get("merge_after") is None
    assert any(e.get("merged") for e in json.loads((d / "M" / "history.json").read_text())["history"])
    stages.run_job({**base, **jobs[2]})  # a finished job is skipped, not re-run
    assert (d / "S" / "command.txt").read_text().count("\n") == 2
    import shutil
    shutil.rmtree(d / "ckpt60")
    with pytest.raises(SystemExit, match="not the fork's 3"):  # S has moved on: the lost checkpoint is not faked
        stages.run_job({**base, **jobs[1]})
