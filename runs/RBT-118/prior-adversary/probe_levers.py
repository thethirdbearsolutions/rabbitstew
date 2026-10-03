"""RBT-118 prior ADVERSARY probe (EXPLORATORY): recount claims 4 and 5 from PR #399's levers.tsv, and price the work lead.

    python runs/RBT-118/prior-adversary/probe_levers.py PATH/TO/levers.tsv > runs/RBT-118/prior-adversary/probe_levers.txt

Break-even work price: the price p (per kJ) at which the holistic net (food - p*kJ) equals the designed net, per history,
at the last snapshot: p* = (food_D - food_H) / (kJ_D - kJ_H).  Only meaningful where H eats less and works less.
"""
import csv
import sys
from collections import defaultdict

import numpy as np

rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
by = defaultdict(dict)
for r in rows:
    by[r["label"]][(int(r["season"]), r["fauna"])] = r
indep = [l for l in by if l.startswith("rbt-90-") or l.startswith("rbt-107-")]
print("# RBT-118 prior ADVERSARY, probe_levers.py: EXPLORATORY, descriptive only")
for group, labs in (("30 independent (RBT-90 + RBT-107 base)", indep), ("all 46 (with RBT-105 replicates)", list(by))):
    fH = fD = wH = wD = nH = 0; n = 0; pstar = []; ratio = []; decomp = []; gear_hi = []; gpm = []
    for l in labs:
        last = max(s for s, _ in by[l])
        h, d = by[l][(last, "holistic")], by[l][(last, "conventional")]
        if int(h["alive"]) == 0 or h["food"] == "":
            continue
        n += 1
        FH, FD, WH, WD = float(h["food"]), float(d["food"]), float(h["work_j"]) / 1000, float(d["work_j"]) / 1000
        fH += FH < FD; wH += WH < WD; nH += (FH - 0.03 * WH) > (FD - 0.03 * WD)
        ratio.append(WH / WD)
        decomp.append((FH - FD, -0.03 * (WH - WD)))
        if FH < FD and WH < WD:
            pstar.append((FD - FH) / (WD - WH))
        g = float(h["gear_per_4mass"]); gpm.append(g); gear_hi.append((g, l, last))
    dc = np.array(decomp)
    print(f"\n## {group}: {n} with a living holistic fauna at the last snapshot")
    print(f"  H eats less: {fH}/{n}; H works less: {wH}/{n}; H nets more (food - 0.03*kJ): {nH}/{n}")
    print(f"  H/D work ratio: median {np.median(ratio):.2f} (range {min(ratio):.2f}-{max(ratio):.2f})")
    print(f"  H-D net decomposed (medians): food term {np.median(dc[:, 0]):+.3f}, work term {np.median(dc[:, 1]):+.3f} items/season")
    print(f"  break-even work price p* where H's net lead vanishes: median {np.median(pstar):.4f}/kJ (range {min(pstar):.4f}-{max(pstar):.4f}; n={len(pstar)}); current 0.03")
    print(f"    p* < 0.03 on {sum(p < 0.03 for p in pstar)}/{len(pstar)}; p* < 0.015 (half price) on {sum(p < 0.015 for p in pstar)}/{len(pstar)}")
    print(f"  holistic gear/(4*mass) at last: median {np.median(gpm):.2f}, range {min(gpm):.2f}-{max(gpm):.2f}; >= 1.76 on {sum(g >= 1.76 for g in gpm)}/{n}: {[x for x in sorted(gear_hi)[::-1] if x[0] >= 1.76]}")
    print(f"    within 0.8-1.2 on {sum(0.8 <= g <= 1.2 for g in gpm)}/{n}; > 1.2 on {sum(g > 1.2 for g in gpm)}/{n}")
# founders -> last: how far did gear move along RBT-113's allowance channel?
g0 = [float(by[l][(0, "holistic")]["gear_per_4mass"]) for l in by]
gl = [float(by[l][(max(s for s, _ in by[l]), "holistic")]["gear_per_4mass"]) for l in by if by[l][(max(s for s, _ in by[l]), "holistic")]["gear_per_4mass"]]
print(f"\n## gear/(4*mass): founders median {np.median(g0):.2f} -> last median {np.median(gl):.2f} (x{np.median(gl) / np.median(g0):.1f}); rises on {sum(b > a for a, b in zip(g0, gl))}/{len(gl)}")
snaps = sorted({s for l in by for s, _ in by[l]})
print(f"snapshot seasons present: {snaps}")
