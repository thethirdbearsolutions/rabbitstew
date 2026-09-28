"""Adversary: Stage-1 income power by exact noncentral-t integration (no simulation, no power.py), the effective-n
model for extinct holistic founder draws, and Stage-1 cost.  Pure stdlib."""
import math
from math import comb

def Phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))
def chi_pdf(v, k): return math.exp((k / 2 - 1) * math.log(v) - v / 2 - (k / 2) * math.log(2) - math.lgamma(k / 2)) if v > 0 else 0.0
def _grid(k, m=4000):
    hi = k + 40 * math.sqrt(2 * k) + 40; dv = hi / m
    return [((i + 0.5) * dv, chi_pdf((i + 0.5) * dv, k) * dv) for i in range(m)]
_G = {}
def tail(c, df, delta=0.0):
    """P(T > c), T noncentral t(df, delta)."""
    g = _G.setdefault(df, _grid(df))
    return sum(w * (1 - Phi(c * math.sqrt(v / df) - delta)) for v, w in g)
def tcrit(a2, df):
    lo, hi = 0.0, 50.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if 2 * tail(mid, df) > a2: lo = mid
        else: hi = mid
    return (lo + hi) / 2
def power(effect, sd, n, alpha=0.05):
    if n < 2: return 0.0
    df = n - 1; return tail(tcrit(alpha, df), df, effect / (sd / math.sqrt(n)))

SDS = (0.144, 0.275, 0.334)
print("## Stage-1 income power, |H-D| = 0.4, BH half (alpha 0.05 two-sided), exact noncentral t")
for sd in SDS:
    print(f"  sd {sd}: " + "  ".join(f"n{n} {power(0.4, sd, n):.3f}" for n in (2, 3, 4, 5, 6, 8, 12, 16)))

print("\n## Effective n (valid seeds for the income test: both faunas alive in S through season 239, DESIGN 6.1)")
print("# Known founder draws (holistic alive at 59 at c0-p030-U-L): 129001 yes, 129002 no, 129003 no, 129004 yes,")
print("#   129005 yes, 129006 yes, 129007 no, 129008 no  ->  4 of 8.  At the U-L pilot points every draw alive at 59")
print("#   was alive at 239 (4 of 4).  Unknown draws (129009+) modelled as Bernoulli(q).")
def dist_valid(n, known_valid_in_first8=4, q=0.5):
    """Distribution of valid seeds at a benign point (every draw that founds survives; designed alive)."""
    if n <= 8:
        # the first n registered seeds' known outcomes
        k = sum((1, 0, 0, 1, 1, 1, 0, 0)[:n]); return {k: 1.0}
    m = n - 8; return {known_valid_in_first8 + j: comb(m, j) * q ** j * (1 - q) ** (m - j) for j in range(m + 1)}
def exp_power(d, sd): return sum(p * power(0.4, sd, k) for k, p in d.items())
def p_excl(n, d):  # holistic extinct on >= 5 of 8 / >= 10 of 16 (scale: > 5/8 of n rounded as registered only for 8,16)
    thr = {8: 5, 16: 10}.get(n, math.ceil(5 * n / 8))
    return sum(p for k, p in d.items() if n - k >= thr)
CS = (23.3, 43.7)
def s_core_h(n, cs, seasons=300): return 36 * n * seasons * cs / 3600
def full_stage1(n, cs, probes=(0.46, 0.83)):  # power.py part 4's Stage-1 row (ungated: side + merged + half null + probes + plants)
    h = lambda s: s * cs / 3600
    return tuple(36 * (n * (h(300) + h(240) + 0.5 * h(240) * 0.85 + pr) + 0.8) for pr in probes)
rows = []
for n in (8, 12, 16):
    for q in ((0.5,) if n == 8 else (0.25, 0.5, 0.75)):
        d = dist_valid(n, q=q)
        ev = sum(k * p for k, p in d.items())
        rows.append((n, q, ev, exp_power(d, 0.334), exp_power(d, 0.275), p_excl(n, d)))
print("  n  q(new draw)  E[valid]  E[power] sd0.334  sd0.275  P(holistic EXCLUDED at a benign point)")
for n, q, ev, p1, p2, pe in rows:
    print(f"  {n:2d}  {q:.2f}        {ev:5.2f}     {p1:.3f}          {p2:.3f}    {pe:.2f}")
print("  (nominal: n valid = n)  " + "  ".join(f"n{n}: {power(0.4,0.334,n):.3f}/{power(0.4,0.275,n):.3f}" for n in (8, 12, 16)))
print("\n## Stage-1 cost (core-h)")
for n in (8, 12, 16):
    a = [s_core_h(n, cs) for cs in CS]; f = [full_stage1(n, cs) for cs in CS]
    # seeds 129001-3 resume from the census (240 seasons, not 300): credit
    cred = [36 * 3 * 60 * cs / 3600 for cs in CS]
    print(f"  n {n:2d}: S arms only (36 x n x 300 seasons) {a[0]:6.0f} (23.3) - {a[1]:6.0f} (43.7) core-h;"
          f" census-resume credit -{cred[0]:.0f}/-{cred[1]:.0f};  power.py-style Stage 1 (S+M+half N+probes, ungated)"
          f" {f[0][0]:.0f}-{f[0][1]:.0f} (23.3) / {f[1][0]:.0f}-{f[1][1]:.0f} (43.7)")
# check of the readout's programme totals at n 8 (power.py part 4 formula, re-implemented)
for cs in (23.35, 43.72):
    h = lambda s: s * cs / 3600
    for pr in (0.46, 0.83):
        side, merged, null = h(300), h(240), 0.5 * h(240) * 0.85; per = side + merged + null + pr
        pilot = 16 * (side + merged + h(240) * 0.85 + pr) + 3.2; census = 150 * 3 * h(60) + 45
        tot = pilot + census + 36 * (8 * per + 0.8) + 16 * (8 * per + 0.8) + 20 * 8 * per
        print(f"  programme total (ungated, power.py part 4 formula) @ {cs} core-s probes {pr}: {tot:.0f}")
