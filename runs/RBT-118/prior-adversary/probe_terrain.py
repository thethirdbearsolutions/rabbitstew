"""RBT-118 prior ADVERSARY probe, after RBT-121 auditor D (H56 clutter tax, H53 same-season refill).

    python runs/RBT-118/prior-adversary/probe_terrain.py > runs/RBT-118/prior-adversary/probe_terrain.txt

1. Terrain of the 30 default-world histories (config).
2. Paired within-history clutter test: RBT-101 shift-s (terrain=flat from the onset) against RBT-90 forage-s, and
   RBT-107 shift-s against RBT-107 base-s. Same history up to the onset; the last 100 seasons compared per fauna.
   Income = the season table's mean_lifetime_score (a lifetime mean: after the onset it mixes pre-onset seasons in
   members born before it; by the last 100 seasons, 200+ seasons after the onset, no member alive predates it,
   max_age 60).
3. H53: `alive` is booked after same-season births. Pre-refill alive = alive - births; fewest of it in seasons 0-59.
"""
import json
import os

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
R90 = (1, 2, 3, 4, 7, 801, 804, 805, 806, 807)
R107 = tuple(range(11, 31))


def tab(run):
    t = {"holistic": {}, "conventional": {}}
    for l in open(os.path.join(ROOT, run, "seasons.txt")).read().splitlines()[1:]:
        r = l.split("\t")
        a = int(r[2])
        t[r[1]][int(r[0])] = (a, int(r[3]), int(r[4]), float(r[5]) if a > 0 else np.nan)
    s = sorted(t["holistic"])
    return np.array(s), np.array([t["holistic"][i] for i in s]), np.array([t["conventional"][i] for i in s])


print("# RBT-118 prior ADVERSARY, probe_terrain.py: EXPLORATORY, descriptive")
terr = {}
for run in [f"runs/RBT-90/forage-{s}" for s in R90] + [f"runs/RBT-107/fresh/base-{s}" for s in R107]:
    c = json.load(open(os.path.join(ROOT, run, "config.json")))
    terr[c["sim"]["world"].get("terrain")] = terr.get(c["sim"]["world"].get("terrain"), 0) + 1
print(f"\n## 1. terrain of the 30 default-world histories: {terr}")

print("\n## 2. Paired clutter test, last 100 seasons: base (random terrain) vs shift (flat from onset), same history")
print(f"{'pair':44s} {'onset':>5s} {'H rand':>7s} {'H flat':>7s} {'D rand':>7s} {'D flat':>7s} {'H-D rand':>8s} {'H-D flat':>8s}")
rows = []
for arm, base, seeds in (("RBT-101/shift-{}", "RBT-90/forage-{}", R90), ("RBT-107/fresh/shift-{}", "RBT-107/fresh/base-{}", R107)):
    for s in seeds:
        sp, bp = "runs/" + arm.format(s), "runs/" + base.format(s)
        if not os.path.exists(os.path.join(ROOT, sp, "seasons.txt")):
            continue
        c = json.load(open(os.path.join(ROOT, sp, "config.json")))["ecology"]
        _, Hb, Db = tab(bp); _, Hs, Ds = tab(sp)
        hb, hs, db, ds = (np.nanmean(x[-100:, 3]) for x in (Hb, Hs, Db, Ds))
        if not np.isfinite(hb):
            continue
        rows.append((hb, hs, db, ds))
        print(f"{arm.format(s):44s} {c['shift_at']:5d} {hb:7.3f} {hs:7.3f} {db:7.3f} {ds:7.3f} {hb - db:+8.3f} {hs - ds:+8.3f}")
a = np.array(rows)
n = len(a)
print(f"\n  pairs: {n}")
print(f"  H-D on random terrain: median {np.median(a[:, 0] - a[:, 2]):+.3f}, H higher on {int(((a[:, 0] - a[:, 2]) > 0).sum())}/{n}")
print(f"  H-D on flat terrain:   median {np.median(a[:, 1] - a[:, 3]):+.3f}, H higher on {int(((a[:, 1] - a[:, 3]) > 0).sum())}/{n}")
print(f"  flat minus random, designed: median {np.median(a[:, 3] - a[:, 2]):+.3f} (up on {int((a[:, 3] > a[:, 2]).sum())}/{n})")
print(f"  flat minus random, holistic: median {np.median(a[:, 1] - a[:, 0]):+.3f} (up on {int((a[:, 1] > a[:, 0]).sum())}/{n})")
print(f"  swing in H-D (flat - random): median {np.median((a[:, 1] - a[:, 3]) - (a[:, 0] - a[:, 2])):+.3f}; lead reverses on {int((((a[:, 0] - a[:, 2]) > 0) & ((a[:, 1] - a[:, 3]) < 0)).sum())}/{n}")

print("\n## 3. H53: alive is booked after same-season births. Pre-refill alive = alive - births, seasons 0-59, and late")
pre, post, dpre, late = [], [], [], []
for run in [f"runs/RBT-90/forage-{s}" for s in R90] + [f"runs/RBT-107/fresh/base-{s}" for s in R107]:
    s, H, D = tab(run)
    pre.append((H[:60, 0] - H[:60, 1]).min()); post.append(H[:60, 0].min()); dpre.append((D[:60, 0] - D[:60, 1]).min())
    m = (s >= 500) & (s < 600)
    if H[m, 0].sum():
        late.append(((H[m, 0] - H[m, 1]).min(), (D[m, 0] - D[m, 1]).min(), np.mean(H[m, 0] == 60), np.mean(D[m, 0] == 60)))
print(f"  holistic fewest alive 0-59: booked median {np.median(post):.0f}, pre-refill median {np.median(pre):.0f} (range {min(pre)}-{max(pre)})")
print(f"  designed fewest alive 0-59, pre-refill: median {np.median(dpre):.0f} (range {min(dpre)}-{max(dpre)})")
L = np.array(late)
print(f"  seasons 500-599: share of seasons booked at 60: H {np.median(L[:, 2]):.2f}, D {np.median(L[:, 3]):.2f}; pre-refill fewest: H median {np.median(L[:, 0]):.0f}, D median {np.median(L[:, 1]):.0f}")
