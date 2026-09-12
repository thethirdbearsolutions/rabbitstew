"""RBT-45: the comparison between what drift proposes and what the run holds.

The grid gives a probability per *lineage*.  The run's 60 saved genotypes are not
60 lineages -- coalescence.py counts how few they are -- so the binomial below is
computed at every plausible effective count rather than at 60.
"""

from __future__ import annotations

import json
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-45/cells.json"
d = json.load(open(PATH))
co = json.load(open("runs/RBT-45/coalescence.json"))["conventional"]


def cell(k, add=0.15, rem=0.1, kind="conventional"):
    for c in d["cells"]:
        if (c["kind"], c["add_link_rate"], c["remove_link_rate"], c["k"]) == (kind, add, rem, k):
            return c
    raise KeyError(k)


depth = d["lineage_depth"]["first_parent"]
print(f"realistic depth (first-parent chain, conventional): median {depth['median']}, max {depth['max']}, "
      f"IQR {depth['p25']}-{depth['p75']}")
print(f"the 60 alive at 599 descend from {co['distinct_founders_behind_them']} founders; along first-parent")
levels = {l["depth_back"]: l["distinct_ancestors"] for l in co["distinct_first_parent_ancestors_by_depth"]}
print(f"chains they collapse to {levels[5]} distinct ancestors 5 back, {levels[10]} at 10, {levels[19]} at 19.\n")

print("| metric | k | p per lineage | P(zero in 60) | P(zero in 22) | P(zero in 11) |")
print("|---|---|---|---|---|---|")
for metric in ("pair", "uncrossed", "crossed", "half"):
    for k in (19, 23):
        p = cell(k)[metric]
        row = [f"{(1 - p) ** m:.4f}" for m in (60, 22, 11)]
        print(f"| {metric.upper()} | {k} | {p:.4f} | " + " | ".join(row) + " |")

print("\nobserved in RBT-23 itself:")
ev = json.load(open("runs/RBT-45/evolved_wiring.json"))
for key in ("bests", "final_population"):
    s = ev[key + "_summary"]
    print(f"  {key}: n={s['n']} PAIR={s['pair']:.3f} HALF={s['half']:.3f} CHASSIS={s['chassis']:.3f} "
          f"uncrossed={s['uncrossed']:.3f} crossed={s['crossed']:.3f}")

c19, c200 = cell(19), cell(200)
print(f"\ndrift from the run's own population, default operator:")
print(f"  HALF  0.217 (k=0) -> {c19['half']:.3f} (k=19) -> {c200['half']:.3f} (k=200)")
print(f"  PAIR  0.000 (k=0) -> {c19['pair']:.3f} (k=19) -> {c200['pair']:.3f} (k=200)")
if "pair_at" in c19:
    print(f"\nstrength of the pairing when it arrives (k=19, default):")
    print(f"  PAIR >0 {c19['pair_at']['0.0']:.3f}  >0.1 {c19['pair_at']['0.1']:.3f}  "
          f"|>1 {c19['pair_at']['1.0']:.3f}  >10 {c19['pair_at']['10.0']:.3f}")
    print(f"  quartiles of pair strength when present: {c19['pair_strength_q']}")
    print(f"  mean chassis-nose influence in the same genotypes: {c19['mean_chassis_infl']}")
