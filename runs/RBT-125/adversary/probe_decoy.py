"""RBT-125 adversary probe: does the patched rotated decoy stop smelling true food under G > 0, in the pool
the harness actually uses (fork), and does prize_gate.check_decoy() prove it?

A committed Pioneer body (runs/RBT-19/P-801/conventional/best_gen0590.json) with RBT-97's routed motif installed at w = 3 (a = 6),
in the registered PW-G2.5 and PW-G0 worlds (runs/RBT-125/gate/worlds), 15 s solo seasons from seeds 7000+.
Arms: base (w 0), motif (true smell), motif under the UNPATCHED RotatedSmell, motif under the PATCHED one.
Also: the check_decoy() assertion re-run with the patch REMOVED, to see whether it would have caught a missing patch.

    python runs/RBT-125/adversary/probe_decoy.py [N]
"""
import json
import os
import sys
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-125", "gate"))
import prize_gate  # noqa: E402  (applies the patch at import)

from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402

rp = prize_gate.rp
PATCHED = rp.mech.RotatedSmell._log_smell
UNPATCHED = Simulation._log_smell
CFG = {}
BODY = os.path.join(ROOT, "runs/RBT-19/P-801/conventional/best_gen0590.json")  # a committed P-801 designed body (RBT-97's)


def bout(task):
    cell, w, arm, seed = task
    cfg = CFG[cell]
    g = Genotype.load(BODY)
    if w:
        g = rp.routed.install(g, w, sign=+1.0)
    if arm == "true":
        sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    else:
        rp.mech.RotatedSmell._log_smell = PATCHED if arm == "patched" else UNPATCHED
        sim = rp.mech.RotatedSmell([g], cfg, spawns=spawn_layout(1, cfg, seed))
        sim._rot = float(np.random.default_rng([seed, 0, 97]).uniform(rp.mech.ROT_LO, rp.mech.ROT_HI))
    sim.set_food_seed(seed)
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
    rp.mech.RotatedSmell._log_smell = PATCHED
    return task, float(sim.food_eaten[0])


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    for cell in ("PW-G2.5", "PW-G0"):
        CFG[cell] = SimConfig.from_dict(json.load(open(os.path.join(ROOT, "runs/RBT-125/gate/worlds", cell, "config.json")))["sim"])
    # 1. would check_decoy() catch a missing patch?
    rp.mech.RotatedSmell._log_smell = UNPATCHED
    try:
        prize_gate.check_decoy()
        print("check_decoy() with the patch REMOVED: passes (it would NOT catch a missing patch)")
    except AssertionError as e:
        print(f"check_decoy() with the patch REMOVED: fails as it should ({e})")
    rp.mech.RotatedSmell._log_smell = PATCHED
    prize_gate.check_decoy()
    print("check_decoy() with the patch: passes")
    # 2. items per arm, in a fork pool (the harness's own start method)
    seeds = [7000 + i for i in range(n)]
    tasks = [(c, 0.0, "true", s) for c in CFG for s in seeds]
    tasks += [(c, 3.0, arm, s) for c in CFG for arm in ("true", "unpatched", "patched") for s in seeds]
    with get_context("fork").Pool(4) as pool:
        rows = pool.map(bout, tasks, chunksize=4)
    got = {t: v for t, v in rows}
    print(f"\nP-801 g590 (runs/RBT-19), a = 6 routed motif, {n} seasons from 7000; items per season (mean, sd)")
    for c in CFG:
        base = np.array([got[(c, 0.0, "true", s)] for s in seeds])
        print(f"{c:8s} base {base.mean():.3f} ({base.std(ddof=1):.3f})")
        for arm in ("true", "unpatched", "patched"):
            x = np.array([got[(c, 3.0, arm, s)] for s in seeds])
            d = x - base
            same = int(sum(got[(c, 3.0, arm, s)] == got[(c, 3.0, 'true', s)] for s in seeds))
            print(f"{c:8s} motif[{arm:9s}] {x.mean():.3f}  delta {d.mean():+.3f} (sd {d.std(ddof=1):.3f})  "
                  f"seasons identical to the true-smell motif: {same}/{n}")


if __name__ == "__main__":
    main()
