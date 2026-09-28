"""RBT-124 design adversary: byte-identity when off, and the strips combined (RBT-120 merged, RBT-125 #414, RBT-126 #419).

    PYTHONPATH=<tree> combo.py <label> <outdir>

Run in each tree (integration e7606db, the PR 5c959ba, and a trial merge PR + #414 + #419).  Writes, per tree:
  cfg_*.json   the config.json a default `evolve` / `ecology` command line writes (the RBT-113 arm's, and a bare one);
  golden       sha256 of RBT-113's golden runs (tests/test_rbt113.py's A and B), with every flag this tree knows passed
               explicitly at its off value;
  pioneer      the Pioneer's MJCF digest, plain and under every physics flag the tree knows (cone, range, budget 1.77);
  all-on       a config with every flag the tree knows switched on: to_dict/from_dict round trip, and a 2 s simulate.
Compare the outputs across trees with diff.  Nothing is written into any run.
"""
import hashlib
import json
import math
import os
import sys
import tempfile

import numpy as np

from rabbitstew.cli import build_parser, evolve_config
from rabbitstew.evolution import Experiment
from rabbitstew.fixed import pioneer_genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
from rabbitstew.world import Spawn, WorldConfig, build_xml

label, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
P = build_parser()
opts = {a.dest for sp in P._subparsers._group_actions[0].choices.values() for a in sp._actions}
OFF = []  # every flag this tree knows, at its off value
for flag, dest, val in (("--ball-cone", "ball_cone", "0"), ("--hinge-range", "hinge_range", "0"), ("--settle-until-rest", "settle_until_rest", "0"),
                        ("--settle-max", "settle_max", "10"), ("--motor-budget", "motor_budget", "0"),
                        ("--smell-contrast", "smell_contrast", "0"), ("--eat-from", "eat_from", "any"), ("--eat-rule", "eat_rule", "centre"),
                        ("--clear-from", "clear_from", "root")):
    if dest in opts:
        OFF += [flag, val]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
res = {"tree": label, "off_flags": OFF}

A = "--generations 3 --population 6 --seed 11 --champion-interval 2 --duration 2".split()
FORAGE = ("--brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 --work-cost 0.03 "
          "--mass-budget 15.34 --conventional-topology --terrain random --random-start --score food").split()
B = "--generations 3 --population 6 --seed 12 --locomotion-phase 3 --duration 2".split() + FORAGE + ["--draws", "2"]
for name, argv in (("default", []), ("forage", FORAGE)):
    for extra, tag in (([], "bare"), (OFF, "offflags")):
        cfg = evolve_config(P.parse_args(["evolve"] + argv + extra + ["--out", "/x"]))
        s = json.dumps(cfg.to_dict(), indent=2, sort_keys=True)
        open(os.path.join(out, f"cfg_{name}_{tag}.json"), "w").write(s)
        res[f"cfg_{name}_{tag}"] = hashlib.sha256(s.encode()).hexdigest()[:16]
with tempfile.TemporaryDirectory() as t:
    for k, argv in (("a", A), ("b", B)):
        Experiment(evolve_config(P.parse_args(["evolve"] + argv + OFF + ["--out", os.path.join(t, k)])), out_dir=os.path.join(t, k), log=None).run()
    res["golden"] = {f"{k}/{f}": sha(os.path.join(t, k, f))[:16] for k in "ab" for f in ("config.json", "lineage.jsonl", "history.json", "state.json")}

wc = WorldConfig()
spawn = [Spawn()]
res["pioneer"] = {}
for rich in (False, True):
    ph = synthesize(pioneer_genotype(np.random.default_rng(3), rich=rich))
    plain = build_xml([ph], spawn, wc)
    kw = {k: v for k, v in dict(ball_cone=math.pi / 2, hinge_range=math.pi / 2, motor_budget=1.77).items() if hasattr(wc, k)}
    from dataclasses import replace
    allon = build_xml([ph], spawn, replace(wc, **kw))
    res["pioneer"][f"rich={rich}"] = {"plain": hashlib.sha256(plain.encode()).hexdigest()[:16], "all physics flags": hashlib.sha256(allon.encode()).hexdigest()[:16], "flags": sorted(kw)}

ON = []
for flag, dest, val in (("--ball-cone", "ball_cone", str(math.pi / 2)), ("--hinge-range", "hinge_range", str(math.pi / 2)), ("--settle-until-rest", "settle_until_rest", "0.01"),
                        ("--motor-budget", "motor_budget", "1.77"), ("--effector-bias-sigma", "effector_bias_sigma", "0"),
                        ("--smell-contrast", "smell_contrast", "2.5"), ("--eat-from", "eat_from", "root"), ("--eat-rule", "eat_rule", "surface"),
                        ("--clear-from", "clear_from", "geoms")):
    if dest in opts:
        ON += [flag, val]
cfg = evolve_config(P.parse_args(["evolve"] + FORAGE + ON + ["--out", "/x"]))
d = cfg.to_dict()
sc = SimConfig.from_dict(d["sim"])
res["all_on_flags"] = ON
res["all_on_roundtrip"] = sc.to_dict() == d["sim"]
from dataclasses import replace
sc = replace(sc, duration=2.0)
sim = Simulation([pioneer_genotype(np.random.default_rng(0))], sc, spawns=spawn_layout(1, sc, 5))
sim.run()
res["all_on_simulate"] = {"ok": True, "settle_s": getattr(sim, "settle_seconds", None), "exploded": bool(sim.exploded[0])}
print(json.dumps(res, indent=1))
json.dump(res, open(os.path.join(out, "combo.json"), "w"), indent=1)
