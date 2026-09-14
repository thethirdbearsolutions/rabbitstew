"""RBT-67 follow-up: the a = 64 anchor and baseline on the source's own seeds, 9000..9063.

The ladder ran on seeds 7000..7063 and read a W4b-801 baseline of 1.270 items where
``verify_independent.py`` read 1.516 on 9000..9063 -- a quarter of an item on 448 bouts.
This runs the ladder's own ``bout()`` (compass_dose_response.py, unchanged) at a = 0 and
a = 64 on the source's seeds.  If the harness agrees with verify_independent.py to three
decimals on its own seeds, the quarter item is the seed set and nothing else; if it does
not, the two harnesses differ and that is the finding.

Usage: python docs/artifacts/RBT-67/seedset_anchor.py [workers=4]
"""

import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "docs", "artifacts", "RBT-67"))

import numpy as np

import compass_dose_response as cdr

POP = "w4b"
SEEDS = list(range(9000, 9064))
SOURCE = {"baseline": 1.516, "delta": 0.897, "ci": (0.632, 1.176), "per_robot": [0.44, 0.47, 0.70, 1.09, 0.84, 1.23, 1.50]}


def main() -> None:
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    gens = cdr.POPULATIONS[POP]["gens"]
    jobs = [(POP, g, a, s) for g in gens for a in (0.0, 64.0) for s in SEEDS]
    with ProcessPoolExecutor(workers) as pool:
        rows = list(pool.map(cdr.bout, jobs, chunksize=8))
    by = {(r["gen"], r["a"], r["seed"]): r for r in rows}
    base = {g: float(np.mean([by[(g, 0.0, s)]["food"] for s in SEEDS])) for g in gens}
    per = [float(np.mean([by[(g, 64.0, s)]["food"] - by[(g, 0.0, s)]["food"] for s in SEEDS])) for g in gens]
    rng = np.random.default_rng(5)
    v = np.asarray(per)
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(20000)])
    lo, hi = np.percentile(m, 2.5), np.percentile(m, 97.5)
    L = [f"RBT-67 seed-set check: {POP}, {len(gens)} robots x {len(SEEDS)} seeds 9000..9063, a in (0, 64), {len(jobs)} bouts",
         f"baseline per robot: " + "  ".join(f"g{g}:{base[g]:.3f}" for g in gens),
         f"pooled baseline {np.mean(list(base.values())):.3f}   (verify_independent.py on the same seeds: {SOURCE['baseline']:.3f}; the ladder on seeds 7000+: 1.270)",
         f"a = 64: delta {v.mean():+.3f} [{lo:+.3f}, {hi:+.3f}], {int((v > 0).sum())}/7 improved   "
         f"(source: {SOURCE['delta']:+.3f} [{SOURCE['ci'][0]:+.3f}, {SOURCE['ci'][1]:+.3f}], 7/7; the ladder on 7000+: +1.018 [+0.600, +1.460])",
         f"per robot delta: {[round(x, 2) for x in per]}   (source: {SOURCE['per_robot']})"]
    text = "\n".join(L)
    print(text)
    out = os.path.join("docs", "artifacts", "RBT-67")
    with open(os.path.join(out, "seedset_anchor.txt"), "w") as f:
        f.write(text + "\n")
    with open(os.path.join(out, "seedset_anchor.json"), "w") as f:
        json.dump({"baseline": base, "per_robot_delta_64": per, "delta_64": [float(v.mean()), float(lo), float(hi)]}, f, indent=1)


if __name__ == "__main__":
    main()
