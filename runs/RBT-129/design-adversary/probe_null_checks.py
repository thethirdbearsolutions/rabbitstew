"""Probe 3: CONTINGENT's F test, K2's per-point centring, and the pilot's null-SD check, at the design's n.

Normal approximations with the design's own replica SDs (power.txt §2): null share SD 0.149 (lottery) and 0.199
(energy); the per-seed share SD with a history-to-history edge spread tau = 0.1 is 0.29-0.46.  The N arm runs on
half the seeds, alternating kinds, so at n = 8 the null has 4 seeds (2 of each kind) and at n = 16 it has 8.

python3 probe_null_checks.py
"""
import numpy as np

rng = np.random.default_rng(12904)
B = 200000


def f_crit(d1, d2, p=0.99):
    a = rng.chisquare(d1, B) / d1
    b = rng.chisquare(d2, B) / d2
    return float(np.quantile(a / b, p))


print("## 1. CONTINGENT: F = var(y) / var(y_null) above its one-sided 0.99 point")
crit = {}
for n, nn in ((8, 4), (16, 8)):
    crit[n] = f_crit(n - 1, nn - 1)
    print(f"  n {n:2d}, null seeds {nn}: F(0.99; {n - 1}, {nn - 1}) = {crit[n]:.1f}")
print("  P(CONTINGENT fires) when the seeds' share SD is s_y and the null's is s_0 (normal seeds):")
for s0 in (0.149, 0.199):
    for sy in (0.29, 0.37, 0.46):
        row = []
        for n, nn in ((8, 4), (16, 8)):
            y = rng.normal(0, sy, (B // 10, n)).var(1, ddof=1)
            z = rng.normal(0, s0, (B // 10, nn)).var(1, ddof=1)
            row.append(f"n {n}: {np.mean(y / z > crit[n]):.2f}")
        print(f"    s_0 {s0:.3f} s_y {sy:.2f} (ratio of variances {sy ** 2 / s0 ** 2:4.1f}) | " + " | ".join(row))
print("  The null's seeds alternate kinds.  If the holistic-copy and designed-copy nulls centre differently (offset d")
print("  between kinds), var(y_null) is inflated and CONTINGENT gets harder still:")
for d in (0.0, 0.1, 0.2):
    for n, nn in ((8, 4), (16, 8)):
        y = rng.normal(0, 0.37, (B // 10, n)).var(1, ddof=1)
        z = rng.normal(0, 0.149, (B // 10, nn))
        z[:, : nn // 2] += d / 2
        z[:, nn // 2:] -= d / 2
        print(f"    d {d:.1f} n {n:2d}: P(CONTINGENT | s_y 0.37, s_0 0.149) = {np.mean(y / z.var(1, ddof=1) > crit[n]):.2f}")
print()

print("## 2. K2 per point: 'at no single point does the null's B-share differ from 0.5 by > 0.15' (point VOID)")
for s0 in (0.149, 0.199, 0.25):
    row = []
    for nn in (4, 8):
        p = float(np.mean(np.abs(rng.normal(0, s0, (B, nn)).mean(1)) > 0.15))
        row.append(f"null seeds {nn}: P(VOID) {p:.3f}; expected VOID of 36 points {36 * p:.1f}, of 52 {52 * p:.1f}; "
                   f"P(>= 1 of 36) {1 - (1 - p) ** 36:.2f}")
    print(f"  null SD {s0:.3f} | " + " | ".join(row))
print("  (s_0 = 0.25 stands for a real drift SD 1.25-1.7x the replica's; the pilot measures it.)")
print()

print("## 3. The pilot's null SD (open item 7): 3 points x 2 null seeds = 6 null runs")
for df in (5, 11):
    lo, hi = np.quantile(np.sqrt(rng.chisquare(df, B) / df), [0.05, 0.95])
    for true in (1.0, 1.5, 2.0):
        s = true * np.sqrt(rng.chisquare(df, B) / df)
        print(f"  df {df:2d}: 90% range of (sample SD / true SD) {lo:.2f}-{hi:.2f}; true ratio {true:.1f} -> "
              f"P(sample ratio > 1.5) {np.mean(s > 1.5):.2f}")
