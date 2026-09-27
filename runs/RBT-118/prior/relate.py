"""RBT-118 prior (EXPLORATORY, descriptive only): the holistic fauna's success beside its body-model levers.

    python runs/RBT-118/prior/relate.py > runs/RBT-118/prior/relate.txt

Joins levers.tsv (levers.py, from ckpt restores) with pool.py's per-history measures and prints:
1. per snapshot season, both faunas' mean levers over the histories (mass, sum gear, gear / 4 x mass, ball-joint share,
   food, work, path, and net = food - 0.03 x work/1000, the lineage's own per-season yield);
2. per history, the holistic levers at seasons 0 (founders), 59 and the last, beside its success measures;
3. Spearman rank correlations between each holistic lever and each success measure, over the independent histories
   (RBT-90 + RBT-107 base).  These are descriptions of 29-30 points, with no test, no interval, and many comparisons;
   a registration would have to name one in advance.

Success measures (pool.py): fewest alive in seasons 0-59, H-D income over 0-59 and over the last 100, HOLD season.
"""
import csv
import os
import re
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pool  # noqa: E402

LEVERS = ("mass", "sum_gear", "gear_per_4mass", "ball_share", "food", "work_j", "path", "net")
SUCCESS = ("h_min_0_59", "early", "late", "hold")


def rank(x):
    x = np.asarray(x, float)
    order = x.argsort()
    r = np.empty(len(x))
    r[order] = np.arange(len(x))
    for v in np.unique(x):  # average ties
        r[x == v] = r[x == v].mean()
    return r


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5:
        return np.nan, int(ok.sum())
    return float(np.corrcoef(rank(a[ok]), rank(b[ok]))[0, 1]), int(ok.sum())


def load_levers():
    L = defaultdict(dict)  # (committed run) -> (season, fauna) -> dict
    for r in csv.DictReader(open(os.path.join(HERE, "levers.tsv")), delimiter="\t"):
        d = {k: (float(r[k]) if r.get(k) not in ("", None) else np.nan) for k in LEVERS if k != "net"}
        d["alive"] = int(r["alive"])
        d["net"] = d["food"] - 0.03 * d["work_j"] / 1000 if np.isfinite(d["food"]) else np.nan
        L[r["committed"]][(int(r["season"]), r["fauna"])] = d
    return L


def main():
    L = load_levers()
    print("# RBT-118 prior, relate.py: EXPLORATORY, descriptive only. No test; rank correlations over independent histories.")
    print("\n## 1. Mean levers of the living population, over histories (holistic | designed); n = histories with that fauna alive")
    snaps = sorted({s for v in L.values() for (s, f) in v if s in (0, 59, 299, 599)})
    for s in snaps + ["last"]:
        for fauna in ("holistic", "conventional"):
            vals = defaultdict(list)
            for run, v in L.items():
                key = (max(ss for ss, _ in v), fauna) if s == "last" else (s, fauna)
                if key in v and v[key]["alive"] > 0:
                    for k in LEVERS:
                        vals[k].append(v[key][k])
            n = len(vals["mass"])
            txt = "  ".join(f"{k} {np.nanmean(vals[k]):.3f}" if k not in ("work_j", "sum_gear") else f"{k} {np.nanmean(vals[k]):.1f}" for k in LEVERS) if n else ""
            print(f"  season {str(s):>4s} {('designed' if fauna == 'conventional' else fauna):9s} n={n:2d}  {txt}")

    indep = [r for r in L if re.fullmatch(r"runs/RBT-90/forage-\d+|runs/RBT-107/fresh/base-\d+", r)]
    reps = [r for r in L if r.startswith("runs/RBT-105/")]
    hist = {r: pool.history_row(r) for r in indep + reps}
    print("\n## 2. Per history: holistic levers (founders @0 | @59 | last) beside success")
    print(f"{'run':30s} {'gear/4m @0':>10s} {'@59':>6s} {'last':>6s} {'ball @last':>10s} {'path @59':>8s} {'path last':>9s} {'work last':>9s} | {'Hmin0-59':>8s} {'H-D 0-59':>8s} {'H-D last':>8s} {'HOLD':>5s}")
    for r in sorted(indep) + sorted(reps):
        v, h = L[r], hist[r]
        last = max(s for s, _ in v)
        g = lambda s, k: v.get((s, "holistic"), {}).get(k, np.nan)
        print(f"{r:30s} {g(0, 'gear_per_4mass'):10.3f} {g(59, 'gear_per_4mass'):6.3f} {g(last, 'gear_per_4mass'):6.3f} {g(last, 'ball_share'):10.3f} {g(59, 'path'):8.3f} {g(last, 'path'):9.3f} {g(last, 'work_j'):9.0f} | "
              f"{h['h_min_0_59']:8d} {h['early']:+8.3f} {h['late']:+8.3f} {str(h['hold'] if h['hold'] is not None else ''):>5s}")

    print("\n## 3. Spearman rho (n) between holistic levers and success, independent histories only (RBT-90 + RBT-107 base)")
    print("   levers at the founders (season 0) against early success; at season 59 against everything; at the last season against late success")
    for s, measures in ((0, ("h_min_0_59", "early", "late", "hold")), (59, SUCCESS), ("last", ("late", "hold"))):
        for k in LEVERS:
            xs = []
            for r in indep:
                last = max(ss for ss, _ in L[r])
                key = (last if s == "last" else s, "holistic")
                xs.append(L[r].get(key, {}).get(k, np.nan) if L[r].get(key, {}).get("alive", 0) > 0 else np.nan)
            cells = []
            for m in measures:
                ys = [hist[r][m] if hist[r][m] is not None else np.nan for r in indep]
                rho, n = spearman(xs, ys)
                cells.append(f"{m} {rho:+.2f} ({n})")
            print(f"  @{str(s):>4s} {k:15s} " + "   ".join(cells))
    print("\n  also, holistic minus designed at the last season, against late H-D income:")
    for k in ("food", "work_j", "path", "net"):
        xs, ys = [], []
        for r in indep:
            last = max(ss for ss, _ in L[r])
            h, d = L[r].get((last, "holistic"), {}), L[r].get((last, "conventional"), {})
            if h.get("alive", 0) and d.get("alive", 0):
                xs.append(h[k] - d[k]); ys.append(hist[r]["late"])
        rho, n = spearman(xs, ys)
        print(f"   H-D {k:8s}: median {np.median(xs):+.3f}; rho with late H-D income {rho:+.2f} ({n}); H>D on {sum(1 for x in xs if x > 0)}/{len(xs)}")


if __name__ == "__main__":
    main()
