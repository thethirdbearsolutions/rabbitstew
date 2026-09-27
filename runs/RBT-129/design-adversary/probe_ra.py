"""Probe 4: does rule R-A refine the pairs that bracket a boundary?

R-A (DESIGN §4.2) adds a midpoint only when two adjacent Stage-1 points carry *different decided calls*
({H-WIN, D-WIN, TIE}, or WIN vs EXCLUDED of the winner).  Under the committed lottery most share calls are SATURATED
(power.txt §5), so R-A falls back to the income layer (EARNS-H / EARNS-D / EARNS-TIE).  A point near a break-even is
UNDECIDED by construction (its |H - D| is below the MDE), so a sign change between two coarse levels usually shows as
(EARNS-D, UNDECIDED, EARNS-H) along the row, and neither adjacent pair differs.

Model: the design's own prior map (power.py part 1): H - D = dfood(c) + p * dkJ, dfood(c) = -0.76 + 0.57 c, with
dkJ = 14.7 (pre-fairness) and 10, 6 (the fairness set cutting the bills, as §10 bounds it).  Per-seed SD 0.334 on
flat ground (c = 0) and 0.144 otherwise (power.py's floor and ceiling), n = 8.  Calls at alpha = q/2 (BH half) with
the design's |mean| >= 0.10 for EARNS and TOST +-0.15 for EARNS-TIE.

For every adjacent coarse pair whose true effects differ in sign (a boundary inside the bracket), printed:
P(R-A refines it) under the registered rule, and under an alternative rule "the two point estimates differ in sign,
or the decided calls differ".

python3 probe_ra.py
"""
import math

import numpy as np

import adv_replica as A

rng = np.random.default_rng(12905)
B, n = 20000, 8
alpha = A.Q / 2
c1 = A.t_crit(alpha, n - 1)
c2 = A.t_crit(2 * alpha, n - 1)


def calls(mu, sd):
    x = rng.normal(mu, sd, (B, n))
    m, se = x.mean(1), x.std(1, ddof=1) / math.sqrt(n)
    t = m / se
    call = np.full(B, "U", dtype=object)
    call[(m - c2 * se > -0.15) & (m + c2 * se < 0.15)] = "T"
    call[(t > c1) & (m >= 0.10)] = "H"
    call[(t < -c1) & (m <= -0.10)] = "D"
    return call, m


def dfood(c):
    return -0.76 + 0.57 * c


def sd_of(c):
    return 0.334 if c == 0 else 0.144


print("# probe_ra: R-A on the prior map, income-layer fallback, n 8, alpha q/2")
print("# axis  fixed  pair            true effects      | P(calls: first, second most common) | P(R-A refines) | P(alt rule refines)")
for dkj in (14.7, 10.0, 6.0):
    print(f"## dkJ = {dkj} (break-evens: c0 {0.76 / dkj:.3f}, c1 {0.19 / dkj:.3f} $/kJ)")
    prices, clutters = (0.01, 0.03, 0.08), (0, 1, 2)
    pairs = []
    for c in clutters:
        for a, b in zip(prices, prices[1:]):
            pairs.append(("price", f"c{c}", (c, a), (c, b)))
    for p in prices:
        for a, b in zip(clutters, clutters[1:]):
            pairs.append(("clutter", f"p{p}", (a, p), (b, p)))
    for axis, fixed, (ca, pa), (cb, pb) in pairs:
        mua, mub = dfood(ca) + pa * dkj, dfood(cb) + pb * dkj
        if np.sign(mua) == np.sign(mub):
            continue
        ka, ma = calls(mua, sd_of(ca))
        kb, mb = calls(mub, sd_of(cb))
        decided = {"H", "D", "T"}
        reg = np.array([(x in decided) and (y in decided) and x != y for x, y in zip(ka, kb)])
        alt = reg | (np.sign(ma) != np.sign(mb))
        def top(k):
            v, c = np.unique(k, return_counts=True)
            o = np.argsort(-c)
            return ",".join(f"{v[i]} {c[i] / B:.2f}" for i in o[:2])
        lab = f"({ca},{pa})-({cb},{pb})"
        print(f"  {axis:7s} {fixed:6s} {lab:22s} {mua:+.2f} / {mub:+.2f} | {top(ka):14s} ; {top(kb):14s} | "
              f"{reg.mean():.2f} | {alt.mean():.2f}")
    # the three-point row pattern D, U, H: a boundary is present but neither adjacent pair differs
    for c in clutters:
        mus = [dfood(c) + p * dkj for p in prices]
        ks = [calls(m, sd_of(c))[0] for m in mus]
        pat = np.mean([(a == "D") and (b not in ("H", "D", "T")) and (d == "H") for a, b, d in zip(*ks)])
        if pat > 0.01:
            print(f"  row c{c}: P(D-call, UNDECIDED, H-call along price) = {pat:.2f}: R-A adds no point in this row")
