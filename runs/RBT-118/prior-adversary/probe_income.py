"""RBT-118 prior ADVERSARY probe (EXPLORATORY, descriptive): does claim 2's "behind early, ahead late" survive other
windows, fixed depths and the RBT-90 / RBT-107 split?  What does the season table's "income" measure, and what do the
two faunas' demographics look like late?  Reads only committed season tables.

    python runs/RBT-118/prior-adversary/probe_income.py [PR_ROOT] > runs/RBT-118/prior-adversary/probe_income.txt

PR_ROOT defaults to this checkout's root (the season tables are on the base branch; PR #399 adds none).
"""
import os
import sys
from math import comb

import numpy as np

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HIST = [f"runs/RBT-90/forage-{s}" for s in (1, 2, 3, 4, 7, 801, 804, 805, 806, 807)] + [f"runs/RBT-107/fresh/base-{s}" for s in range(11, 31)]


def table(run):
    t = {"holistic": {}, "conventional": {}}
    with open(os.path.join(ROOT, run, "seasons.txt")) as f:
        h = f.readline().rstrip("\n").split("\t")
        ix = {k: h.index(k) for k in ("season", "population", "alive", "births", "deaths", "mean_lifetime_score")}
        ix["mean_age"] = h.index("mean_age") if "mean_age" in h else None  # RBT-90's tables predate the column
        for line in f:
            r = line.rstrip("\n").split("\t")
            a = int(r[ix["alive"]])
            t[r[ix["population"]]][int(r[ix["season"]])] = (a, int(r[ix["births"]]), int(r[ix["deaths"]]),
                                                            float(r[ix["mean_lifetime_score"]]) if a > 0 else np.nan, float(r[ix["mean_age"]]) if ix["mean_age"] is not None else np.nan)
    s = np.array(sorted(t["holistic"]))
    H = np.array([t["holistic"][i] for i in s]); D = np.array([t["conventional"][i] for i in s])
    return s, H, D


def sign_p(k, n):
    """two-sided sign-test p (descriptive only)."""
    lo = min(k, n - k)
    return min(1.0, 2 * sum(comb(n, i) for i in range(lo + 1)) / 2 ** n)


def win(s, d, a, b):
    m = (s >= a) & (s < b)
    v = d[m]
    return np.nanmean(v) if m.any() and np.isfinite(v).any() else np.nan


data = {r: table(r) for r in HIST}
print("# RBT-118 prior ADVERSARY, probe_income.py: EXPLORATORY, descriptive; 'p' is a two-sided sign test, descriptive only")
print("\n## 1. The metric. mean_lifetime_score = mean over the LIVING of each member's lifetime-average gain (ecology.py:572),")
print("##    gain = food*value - work_cost*kJ (simulation.py:527), gross of living cost. It is a lagged, survivor-weighted stock, not a per-season flow.")
s0 = [(data[r][1][0, 3], data[r][2][0, 3]) for r in HIST]
print(f"season 0 (founders, one evaluation each): H median {np.median([a for a, _ in s0]):.3f}, D median {np.median([b for _, b in s0]):.3f}; H lower on {sum(a < b for a, b in s0)}/30")

print("\n## 2. Early window sensitivity: holistic LOWER on k/n (median H-D)")
for a, b in ((0, 1), (0, 11), (11, 60), (12, 60), (0, 30), (30, 60), (0, 60), (60, 120)):
    v = np.array([win(data[r][0], data[r][1][:, 3] - data[r][2][:, 3], a, b) for r in HIST]); v = v[np.isfinite(v)]
    k = int((v < 0).sum())
    print(f"  seasons {a:4d}-{b - 1:<4d}: {k:2d}/{len(v)}  median {np.median(v):+.3f}  p={sign_p(k, len(v)):.3g}")

print("\n## 3. First season from which H-D stays > 0 for 20 consecutive seasons (per-season table value)")
fc = []
for r in HIST:
    s, H, D = data[r]; d = H[:, 3] - D[:, 3]
    x = next((int(s[i]) for i in range(len(s) - 20) if np.all(d[i:i + 20] > 0)), None)
    fc.append(x)
ok = [x for x in fc if x is not None]
print(f"  found on {len(ok)}/30; median {np.median(ok):.0f}; quartiles {np.percentile(ok, 25):.0f}, {np.percentile(ok, 75):.0f}; <=59 on {sum(x <= 59 for x in ok)}; list {sorted(ok)}")

print("\n## 4. Late window at FIXED depths: holistic HIGHER on k/n surviving (median H-D). RBT-90 ends at 599.")
for a, b in ((100, 200), (200, 300), (300, 400), (400, 500), (500, 600), (1100, 1200)):
    for lab, sub in (("all", HIST), ("RBT-90", HIST[:10]), ("RBT-107", HIST[10:])):
        v = np.array([win(data[r][0], data[r][1][:, 3] - data[r][2][:, 3], a, b) for r in sub]); v = v[np.isfinite(v)]
        if not len(v):
            continue
        k = int((v > 0).sum())
        print(f"  seasons {a:4d}-{b - 1:<4d} {lab:8s}: {k:2d}/{len(v):<2d} median {np.median(v):+.3f}  p={sign_p(k, len(v)):.3g}")
v = np.array([win(data[r][0], data[r][1][:, 3] - data[r][2][:, 3], data[r][0][-100], 10 ** 9) for r in HIST]); v = v[np.isfinite(v)]
print(f"  'last 100' as in pool.py (mixes depth 500 and 1100): {int((v > 0).sum())}/{len(v)} median {np.median(v):+.3f}")

print("\n## 5. Late demography, seasons 500-599 (all 30 histories reach it): does the income lead show up in numbers?")
print(f"{'':10s} {'alive':>6s} {'births/s':>8s} {'deaths/s':>8s} {'mean age':>8s}")
for j, lab in ((1, "holistic"), (2, "designed")):
    rows = []
    for r in HIST:
        s, H, D = data[r]; X = (H, D)[j - 1]; m = (s >= 500) & (s < 600)
        if X[m, 0].sum() == 0:
            continue
        rows.append([X[m, 0].mean(), X[m, 1].mean(), X[m, 2].mean(), X[m, 4].mean()])
    a = np.array(rows)
    print(f"{lab:10s} {np.median(a[:, 0]):6.1f} {np.median(a[:, 1]):8.2f} {np.median(a[:, 2]):8.2f} {np.nanmedian(a[:, 3]):8.1f}   (medians over {len(a)} histories; min alive over histories {a[:, 0].min():.1f})")
lo = []
for r in HIST:
    s, H, D = data[r]; m = (s >= 500) & (s < 600)
    if H[m, 0].sum():
        lo.append((H[m, 2].mean() - D[m, 2].mean()))
print(f"  deaths/season H - D, 500-599: median {np.median(lo):+.2f}; H fewer deaths on {sum(x < 0 for x in lo)}/{len(lo)}")
print("  (max_age 60 => age-only turnover is 1.0 death/season per 60 alive; deaths above that are starvation)")

print("\n## 6. The founding bottleneck and the early window: H-D in 0-59 against the holistic fewest alive (survivor weighting)")
rows = []
for r in HIST:
    s, H, D = data[r]; d = H[:, 3] - D[:, 3]
    rows.append((int(H[:60, 0].min()), win(s, d, 0, 11), win(s, d, 12, 60), H[10, 3], H[13, 3]))
a = np.array(rows, float)
print(f"  holistic metric season 10 -> 13 (across the season-11 die-off): median {np.nanmedian(a[:, 3]):.3f} -> {np.nanmedian(a[:, 4]):.3f}; rises on {int(np.nansum(a[:, 4] > a[:, 3]))}/30")
from scipy.stats import spearmanr  # noqa: E402
ok = np.isfinite(a).all(1)
print(f"  Spearman(H fewest alive 0-59, H-D 12-59) = {spearmanr(a[ok, 0], a[ok, 2])[0]:+.2f} over {ok.sum()} (descriptive)")
