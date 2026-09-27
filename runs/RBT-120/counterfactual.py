"""RBT-120 power-model input: RBT-113's holistic O-arm populations re-scored UNDER the budget, genomes unchanged.

    counterfactual.py [--workers W] SEED_DIR [SEED_DIR ...] > counterfactual.txt     (SEED_DIRs: runs/RBT-113/O*/<seed>)

For each restored O seed directory it re-scores the holistic founders and the U, D and C lines' generation-23 `final/`
populations solo on decompose.py's four fixed draws (RBT-113's `score`, unchanged), once with `--motor-budget 1.77`,
and prints them beside the same groups' registered, unbudgeted decompose.json.  This is the budget's immediate effect
on bodies that evolved without it (no re-adaptation): the FLOOR of the power model's down half (PREREGISTRATION.md §6).
It also prints each group's motor capacity (rabbitstew.motors) without and with the budget.  It uses RBT-113 data that
are already read and public (#393, #394); the rerun's arms are the unseen data.  Nothing here writes into a run.
"""
import argparse
import glob
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "RBT-113"))
sys.path.insert(0, HERE)
import world as W120  # noqa: E402  RBT-120's world.py (first on the path)
import decompose as D113  # noqa: E402  RBT-113's decompose.py, unchanged

from rabbitstew import motors  # noqa: E402
from rabbitstew.evolution import HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--json", default=os.path.join(HERE, "counterfactual.json"))
    ap.add_argument("seed_dirs", nargs="+")
    a = ap.parse_args(argv)
    pool = ProcessPoolExecutor(a.workers)
    out = {}
    print("# RBT-120 counterfactual: RBT-113 O-arm holistic populations re-scored under --motor-budget "
          f"{W120.MOTOR_BUDGET} on decompose.py's {len(D113.DRAWS)} fixed draws (genomes unchanged)")
    print("# per group: registered (unbudgeted) food / work / net from decompose.json -> budgeted food / work / net; "
          "motor capacity gear/(ms*mass) unbudgeted -> budgeted, free-spin ceiling (yield) unbudgeted -> budgeted")
    for d in a.seed_dirs:
        op, seed = D113.parse_seed_dir(d)
        assert op == "", f"{d}: O arms only"
        dec = json.load(open(os.path.join(d, "decompose.json")))["faunae"][HOLISTIC]
        cfg = W120.evolution_config("U", seed=seed)
        assert cfg.sim.world.motor_budget == W120.MOTOR_BUDGET
        cfg0 = W120.W113.evolution_config("U", seed=seed)
        sc_b, sc_0 = generation_sim(cfg, D113.DRAWS[0][0]), generation_sim(cfg0, D113.DRAWS[0][0])
        groups = {"founders": initial_population(HOLISTIC, cfg0, spawn_streams(seed, 0)[HOLISTIC]).members}
        for L in "UDC":
            groups[L] = [Genotype.load(p) for p in sorted(glob.glob(os.path.join(d, L, HOLISTIC, "final", "*.json")))]
            assert len(groups[L]) == 40, f"{d} {L}: restore the checkpoint"
        res = {}
        print(f"\n{d} holistic")
        for k, ms in groups.items():
            f, w, y = D113.score(pool, ms, cfg)
            c0 = motors.summarise([motors.capacity(g, sc_0) for g in ms])
            cb = motors.summarise([motors.capacity(g, sc_b) for g in ms])
            r = dec[k]
            res[k] = {"food0": r["food"], "work0": r["work"], "net0": r["net"], "food": float(f.mean()), "work": float(w.mean()),
                      "net": float(y.mean()), "work_max": float(w.max()), "ratio0": c0["ratio"], "ratio": cb["ratio"], "ceiling0": c0["ceiling_yield"],
                      "ceiling": cb["ceiling_yield"], "mass": cb["mass"], "over": cb["budgeted_share"]}
            q = res[k]
            print(f"  {k:9s} food {q['food0']:.3f} -> {q['food']:.3f}  work {q['work0']:.3f} -> {q['work']:.3f} (max member {q['work_max']:.3f})  net {q['net0']:+.3f} -> {q['net']:+.3f}"
                  f"   gear/(ms*mass) {q['ratio0']:.2f} -> {q['ratio']:.2f} ({q['over']:.0%} over)  ceiling {q['ceiling0']:.2f} -> {q['ceiling']:.2f}  mass {q['mass']:.2f}")
        out[str(seed)] = res
    pool.shutdown()
    print("\n# across seeds: mean (min, max)")
    for k in ("founders", "U", "D", "C"):
        for q in ("work0", "work", "net0", "net", "ceiling0", "ceiling"):
            v = np.array([out[s][k][q] for s in out])
            print(f"  {k:9s} {q:9s} {v.mean():+.3f} ({v.min():+.3f}, {v.max():+.3f})")
    for q0, q in (("net0", "net"),):
        cd0 = np.array([out[s]["C"][q0] - out[s]["D"][q0] for s in out])
        cdb = np.array([out[s]["C"][q] - out[s]["D"][q] for s in out])
        print(f"  C - D net: registered {cd0.mean():+.3f}, D line budgeted {cdb.mean():+.3f} (ratio {cdb.mean() / cd0.mean():.2f})")
    json.dump(out, open(a.json, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
