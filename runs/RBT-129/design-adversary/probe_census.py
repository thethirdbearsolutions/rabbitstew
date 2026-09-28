"""Probe 7: can a 3-seed, 60-season census classify habitability?

One fauna alone in its 60 slots (the design's replica demography, power.py: threshold 3, birth cost 1, max age 60,
initial energy 3, staggered ages, gain Poisson(g) - 0.1 - 0.25), at fixed mean gross income g near viability.
Printed: P(extinct by season 59) and by 299 per seed; then the census rule (EXCLUDED if extinct by 59 on >= 2 of 3
seeds) against Stage 1's rule (extinct by 299 on >= 5 of 8).  A fixed g has no evolution and no founding lottery;
the committed record's extinctions after a change of world came 67-146 seasons after the onset (RBT-118 prior §3),
all beyond a 60-season window.

python3 probe_census.py [reps]
"""
import sys
from math import comb

import numpy as np

import adv_replica as A

P = A.P
reps = int(sys.argv[1]) if len(sys.argv) > 1 else 400
rng = np.random.default_rng(12907)


def history(g, horizon=300, cap=60):
    pop = [[0, P.INIT, int(rng.integers(0, P.AGE))] for _ in range(cap)]
    ext = None
    for s in range(horizon):
        pop = P._season(rng, pop, {0: g})
        pop = P._breed(rng, pop, cap, "lottery", (0,))
        if not pop:
            return s
    return ext


def binom_ge(k, n, p):
    return sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


print(f"# probe_census: {reps} single-fauna replica histories per g")
print("# g | P(extinct by 59) | P(extinct by 299) | census EXCLUDED (>= 2/3 by 59) | Stage-1 EXCLUDED (>= 5/8 by 299)")
for g in (0.30, 0.35, 0.40, 0.45, 0.50, 0.60):
    ext = [history(g) for _ in range(reps)]
    p59 = np.mean([e is not None and e <= 59 for e in ext])
    p299 = np.mean([e is not None for e in ext])
    print(f"  g {g:.2f} | {p59:.2f} | {p299:.2f} | {binom_ge(2, 3, p59):.2f} | {binom_ge(5, 8, p299):.2f}", flush=True)
