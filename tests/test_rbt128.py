"""RBT-128: the --fair preset and the missing-budget guard (RBT-121 R9).

The preset expands to exactly the ruled flags; the guard refuses a mixed-fauna run with neither --fair nor
--unfair-i-know, and is bypassed as specified; old configs (no fairness key) replay byte for byte.
"""
import json
import math
import os

import numpy as np
import pytest

from rabbitstew import fair
from rabbitstew.cli import build_parser, evolve_config, main
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.fixed import pioneer_genotype, quadruped_genotype
from rabbitstew.genotype import random_genotype

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RBT113 = ["--brain-model", "foraging", "--food-items", "12", "--food-radius", "3", "--eat-radius", "0.35", "--food-decay", "1.0",
          "--work-cost", "0.03", "--duration", "15", "--mass-budget", "15.34", "--conventional-topology", "--terrain", "random",
          "--random-start", "--score", "food"]
EXPLICIT = ["--mass-budget", "15.34", "--motor-budget", "1.77", "--ball-cone", repr(math.pi / 2), "--hinge-range", repr(math.pi / 2),
            "--settle-until-rest", "0.01", "--settle-max", "10"]


def cfg(sub, argv):
    return build_parser().parse_args([sub] + argv + (["--out", "/nonexistent"] if sub != "simulate" else []))


def flat(d, prefix=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flat(v, f"{prefix}{k}."))
        else:
            out[f"{prefix}{k}"] = v
    return out


def test_the_preset_is_exactly_the_ruled_set():
    assert [(d, v) for d, v, _ in fair.PRESET] == [("mass_budget", 15.34), ("motor_budget", 1.77), ("ball_cone", math.pi / 2),
                                                   ("hinge_range", math.pi / 2), ("settle_until_rest", 0.01), ("settle_max", 10.0)]
    assert not any(d in ("effector_bias_sigma", "cap_on_reachable") for d, _, _ in fair.PRESET)  # [OPEN] / not ruled in


def test_fair_expands_to_exactly_the_listed_flags_and_writes_them():
    """--fair's config is the plain config with the preset's flags given explicitly, plus "fairness": "fair", and it
    differs from the bare config in exactly the preset's keys and the marker."""
    for base in ([], RBT113):
        bare = flat(evolve_config(cfg("evolve", base)).to_dict())
        f = evolve_config(cfg("evolve", base + ["--fair"])).to_dict()
        explicit = flat(evolve_config(cfg("evolve", base + EXPLICIT)).to_dict())
        ff = flat(f)
        assert f["fairness"] == "fair" and {k: v for k, v in ff.items() if k != "fairness"} == explicit
        changed = {k for k in set(ff) | set(bare) if ff.get(k) != bare.get(k)}
        expected = {"fairness", "sim.world.motor_budget", "sim.world.ball_cone", "sim.world.hinge_range", "sim.settle_until_rest", "sim.settle_max"}
        if base != RBT113:
            expected.add("sim.synthesis.mass_budget")  # RBT-113's command line already sets it
        assert changed == expected, changed
        back = EvolutionConfig.from_dict(json.loads(json.dumps(f)))
        assert back.fairness == "fair" and back.sim.world.motor_budget == 1.77 and back.mutation.effector_bias_sigma is None


def test_fair_on_ecology_and_simulate():
    a = cfg("ecology", ["--fair"])
    assert fair.expand(a) == "fair" and a.mass_budget == 15.34 and a.motor_budget == 1.77 and a.settle_until_rest == 0.01
    s = build_parser().parse_args(["simulate", "g.json", "--fair"])
    assert fair.expand(s) == "fair" and s.ball_cone == math.pi / 2 and s.hinge_range == math.pi / 2


def test_fair_refuses_a_conflicting_flag_and_accepts_a_matching_one():
    with pytest.raises(SystemExit):
        fair.expand(cfg("evolve", ["--fair", "--mass-budget", "20"]))
    with pytest.raises(SystemExit):
        fair.expand(cfg("evolve", ["--fair", "--motor-budget", "2"]))
    with pytest.raises(SystemExit):
        fair.expand(cfg("evolve", ["--fair", "--unfair-i-know"]))
    assert fair.expand(cfg("evolve", ["--fair", "--mass-budget", "15.34"])) == "fair"
    a = cfg("evolve", ["--fair", "--effector-bias-sigma", "0"])  # outside the preset: the registrant's own flag
    assert fair.expand(a) == "fair" and evolve_config(a).mutation.effector_bias_sigma == 0.0


def test_the_preset_is_printed(tmp_path, capsys):
    run = str(tmp_path / "r")
    assert main(["evolve", "--fair", "--generations", "1", "--population", "3", "--champion-interval", "0", "--duration", "0.3", "--out", run]) == 0
    out = capsys.readouterr().out
    assert "--fair expands to: --mass-budget 15.34 --motor-budget 1.77 --ball-cone 1.5707963267948966 --hinge-range 1.5707963267948966 --settle-until-rest 0.01 --settle-max 10" in out
    d = json.load(open(os.path.join(run, "config.json")))
    assert d["fairness"] == "fair" and d["sim"]["synthesis"]["mass_budget"] == 15.34 and d["sim"]["world"]["ball_cone"] == math.pi / 2


def test_the_guard_fires_on_evolve_ecology_and_a_mixed_bout(tmp_path):
    with pytest.raises(SystemExit, match="neither --fair nor --unfair-i-know"):
        main(["evolve", "--generations", "1", "--population", "3", "--out", str(tmp_path / "e")])
    with pytest.raises(SystemExit, match="neither --fair nor --unfair-i-know"):
        main(["ecology", "--seasons", "1", "--capacity", "4", "--out", str(tmp_path / "c")])
    h, p = str(tmp_path / "h.json"), str(tmp_path / "p.json")
    random_genotype(np.random.default_rng(1)).save(h)
    pioneer_genotype(np.random.default_rng(0)).save(p)
    with pytest.raises(SystemExit, match="neither --fair nor --unfair-i-know"):
        main(["simulate", h, p, "--duration", "0.2"])
    assert not os.path.exists(tmp_path / "e" / "config.json") and not os.path.exists(tmp_path / "c" / "config.json")


def test_the_guard_is_bypassed_as_specified(tmp_path, capsys):
    h, p, q = str(tmp_path / "h.json"), str(tmp_path / "p.json"), str(tmp_path / "q.json")
    random_genotype(np.random.default_rng(1)).save(h)
    pioneer_genotype(np.random.default_rng(0)).save(p)
    random_genotype(np.random.default_rng(2)).save(q)
    assert main(["simulate", h, p, "--duration", "0.2", "--unfair-i-know"]) == 0
    assert "WITHOUT the fairness set" in capsys.readouterr().out
    assert main(["simulate", h, p, "--duration", "0.2", "--fair"]) == 0
    assert main(["simulate", h, q, "--duration", "0.2"]) == 0  # one fauna: exempt
    assert main(["simulate", p, p, "--duration", "0.2"]) == 0
    assert main(["simulate", h, "--duration", "0.2"]) == 0  # a solo run
    # ecology: one fauna alone is exempt
    assert main(["ecology", "--seasons", "1", "--capacity", "4", "--group-size", "2", "--duration", "0.2", "--only-fauna", "holistic",
                 "--out", str(tmp_path / "only")]) == 0
    assert "fairness" not in json.load(open(tmp_path / "only" / "config.json"))


def test_is_designed():
    assert fair.is_designed(pioneer_genotype(np.random.default_rng(3), rich=True))
    assert fair.is_designed(quadruped_genotype(np.random.default_rng(3)))
    assert not any(fair.is_designed(random_genotype(np.random.default_rng(s))) for s in range(20))


def test_the_bypass_writes_the_config_it_wrote_before(tmp_path):
    """--unfair-i-know adds nothing: RBT-113's registered command line with it builds the committed config.json of an
    RBT-113 arm (O1 seed 3, line D), key for key."""
    committed = json.load(open(os.path.join(ROOT, "runs", "RBT-113", "O1", "3", "D", "config.json")))
    argv = RBT113 + ["--population", "40", "--generations", "24", "--locomotion-phase", "24", "--elites", "0", "--champion-interval", "0",
                     "--draws", "2", "--workers", str(committed["workers"]), "--truncation", "0.25", "--line", "down", "--seed", "3"]
    a = cfg("evolve", argv + ["--unfair-i-know"])
    assert fair.expand(a) == "unfair"
    assert json.dumps(evolve_config(a).to_dict(), sort_keys=True) == json.dumps(committed, sort_keys=True)
    assert json.dumps(evolve_config(a).to_dict(), sort_keys=True) == json.dumps(evolve_config(cfg("evolve", argv)).to_dict(), sort_keys=True)


@pytest.mark.parametrize("path", ["runs/RBT-113/O1/3/D/config.json", "runs/RBT-120/B4/11/D/config.json"])
def test_old_configs_replay_byte_for_byte(path):
    """A config.json with no fairness key (RBT-113's, and an RBT-120 B arm's, which sets --motor-budget alone) loads
    and writes itself back byte for byte: resuming never meets the preset or the guard."""
    raw = open(os.path.join(ROOT, path)).read()
    d = json.loads(raw)
    assert "fairness" not in d
    back = EvolutionConfig.from_dict(d).to_dict()
    assert json.dumps(back, indent=2) == json.dumps(d, indent=2)  # json: the target tuple is written as the list it reads
    assert EvolutionConfig.from_dict(d).fairness == ""


def test_resume_needs_no_flag(tmp_path):
    """A run started under the bypass resumes with no fairness flag at all (the guard is only on a fresh start)."""
    run = str(tmp_path / "r")
    base = ["evolve", "--generations", "2", "--population", "3", "--champion-interval", "0", "--duration", "0.2", "--out", run]
    assert main(base + ["--unfair-i-know"]) == 0
    before = open(os.path.join(run, "config.json")).read()
    assert main(["evolve", "--resume", "--generations", "3", "--out", run]) == 0
    after = json.load(open(os.path.join(run, "config.json")))
    assert "fairness" not in after and dict(after, generations=2) == json.loads(before)  # only the extended horizon changes


def test_fair_composes_with_every_strip_and_leaves_the_world_alone():
    """--fair with RBT-125's perception/eating rules, RBT-126's breeding flags and RBT-130's obstacle radius: every
    strip's value is written, and --fair touches none of them (world settings are not body fairness)."""
    world = RBT113 + ["--smell-contrast", "2.5", "--eat-from", "root", "--obstacle-radius", "2.0"]
    f = flat(evolve_config(cfg("evolve", world + ["--fair"])).to_dict())
    plain = flat(evolve_config(cfg("evolve", world + EXPLICIT)).to_dict())
    assert f.pop("fairness") == "fair" and f == plain
    assert f["sim.food.smell_contrast"] == 2.5 and f["sim.food.eat_from"] == "root" and f["sim.world.random_radius"] == 2.0
    e = cfg("ecology", ["--fair", "--breed-rule", "energy", "--smell-contrast", "2.5"])
    assert fair.expand(e) == "fair" and e.breed_rule == "energy" and e.smell_contrast == 2.5 and e.mass_budget == 15.34
