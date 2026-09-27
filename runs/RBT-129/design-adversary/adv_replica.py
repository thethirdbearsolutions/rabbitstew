"""Shared helpers for the RBT-129 design-adversary probes.  Imports the design's own replica from ../power.py
(unchanged) and adds one hook: the merge-time composition (how many of each fauna are alive at the merge)."""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import power as P  # noqa: E402  the design's power.py, unchanged

Q = P.Q
t_crit = P.t_crit


def merged_history_k(rng, gH, gD, rule, keep_H=None, keep_D=None, merge=60, horizon=300, window=(240, 300), cap=60):
    """power.merged_history, except that at the merge only keep_H holistic / keep_D designed members survive
    (drawn at random).  Returns (window share, share at the merge, fixed)."""
    g_of = {0: gD, 1: gH}
    pops = {k: [[k, P.INIT, int(rng.integers(0, P.AGE))] for _ in range(cap)] for k in (0, 1)}
    for s in range(merge):
        for k in (0, 1):
            pops[k] = P._season(rng, pops[k], g_of)
            pops[k] = P._breed(rng, pops[k], cap, rule, (k,))
    for k, keep in ((1, keep_H), (0, keep_D)):
        if keep is not None and len(pops[k]) > keep:
            idx = rng.permutation(len(pops[k]))[:keep]
            pops[k] = [pops[k][i] for i in idx]
    pop = pops[0] + pops[1]
    s0 = sum(p[0] for p in pop) / max(1, len(pop))
    shares = []
    for s in range(merge, horizon):
        pop = P._season(rng, pop, g_of)
        pop = P._breed(rng, pop, 2 * cap, rule, (0, 1))
        if window[0] <= s < window[1]:
            shares.append(sum(p[0] for p in pop) / (2 * cap))
    fixed = (not any(p[0] == 1 for p in pop)) or (not any(p[0] == 0 for p in pop))
    return float(np.mean(shares)), s0, fixed


def t_stat(x):
    n = x.shape[-1]
    return x.mean(-1) / (x.std(-1, ddof=1) / math.sqrt(n) + 1e-12)


def win_rate(sh, n, alpha, sign=None, rng=None, B=4000):
    """P(two-sided t on (share - 0.5) rejects at alpha), resampling n seeds from the simulated distribution.
    sign=+1/-1 counts rejections in that direction only; None counts either."""
    rng = rng or np.random.default_rng(7)
    x = sh[rng.integers(0, len(sh), size=(B, n))] - 0.5
    t = t_stat(x)
    c = t_crit(alpha, n - 1)
    if sign is None:
        return float(np.mean(np.abs(t) > c))
    return float(np.mean(sign * t > c))


def tie_rate(sh, n, alpha, margin=0.10, rng=None, B=4000):
    """P(TOST at alpha: the (1 - 2 alpha) CI of mean(share - 0.5) lies inside +-margin), as power.tost."""
    rng = rng or np.random.default_rng(8)
    x = sh[rng.integers(0, len(sh), size=(B, n))] - 0.5
    m, se = x.mean(1), x.std(1, ddof=1) / math.sqrt(n)
    c2 = t_crit(2 * alpha, n - 1)
    return float(np.mean((m - c2 * se > -margin) & (m + c2 * se < margin)))
