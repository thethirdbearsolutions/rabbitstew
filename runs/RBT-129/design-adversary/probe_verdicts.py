"""R2-CHECK probe: how easily does one false opposite-sign call flip EARNINGS DOMINATED into EARNINGS DEPEND?

r2 §8: EARNINGS DEPEND needs T1 to reject and >= 1 EARNS-H and >= 1 EARNS-D; EARNINGS DOMINATED (X) needs EARNS-X at
>= 1/3 of habitable points and no call of any kind for the other fauna.  A world where the holistic fauna truly
dominates (every true H - D >= 0) but some points sit near the boundary: how often does BH (q 0.10, two-sided,
|mean| >= 0.10) produce at least one EARNS-D anyway?

Scenario: 36 Stage-1 points; k0 of them have a true effect of exactly 0 (a break-even inside the grid), the rest
uniform on [0.15, 0.8]; per-seed SD 0.144 (c >= 1) or 0.334 (flat, 12 of 36 points); n 8.
Alternative rule printed: an opposite-sign call counts only if >= 2 of them, or if it survives BH at q = 0.05 ("a
replicated or stricter opposite call").

python3 probe_verdicts.py
"""
import math

import numpy as np

import adv_replica as A

rng = np.random.default_rng(12912)
B, K, n, q = 20000, 36, 8, 0.10
sd = np.array([0.334] * 12 + [0.144] * 24)
tc = {}


def t_p(t, df):
    return np.array([2 * A.P.t_sf(abs(v), df) for v in t])


def bh(p, q):
    o = np.argsort(p)
    ranks = np.arange(1, len(p) + 1)
    ok = p[o] <= q * ranks / len(p)
    rej = np.zeros(len(p), bool)
    if ok.any():
        kmax = np.max(np.where(ok)[0])
        rej[o[: kmax + 1]] = True
    return rej


print("# k0 | P(EARNS-H at >= 12 pts) | P(>= 1 EARNS-D) | P(>= 2 EARNS-D) | P(>= 1 EARNS-D at BH q 0.05)")
for k0 in (0, 3, 6, 12):
    res = []
    for _ in range(3000):
        mu = rng.uniform(0.15, 0.8, K)
        mu[rng.permutation(K)[:k0]] = 0.0
        x = rng.normal(mu[:, None], sd[:, None], (K, n))
        m, se = x.mean(1), x.std(1, ddof=1) / math.sqrt(n)
        p = t_p(m / se, n - 1)
        r10, r05 = bh(p, 0.10), bh(p, 0.05)
        H = np.sum(r10 & (m >= 0.10))
        D10 = np.sum(r10 & (m <= -0.10))
        D05 = np.sum(r05 & (m <= -0.10))
        res.append((H >= 12, D10 >= 1, D10 >= 2, D05 >= 1))
    r = np.mean(res, 0)
    print(f"  k0 {k0:2d} | {r[0]:.2f} | {r[1]:.3f} | {r[2]:.3f} | {r[3]:.3f}", flush=True)
