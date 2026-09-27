"""RBT-121 audit C: the path, not the peak.  probe_world.py shows a well-steered nose pays 2-5x a blind
forager of equal speed.  This asks what evolution sees from where the population actually is: a weak
link gain k (evolved weights top out at 4.65-6.11, paper 5), little turn authority, and a body that
cannot hold a heading (heading noise).  It reports the elasticity of intake to one mutation-sized step
in link gain (+0.4, the weight sigma) against one to +25% speed.

python3 runs/RBT-121/ecology/probe_gradient.py [n]
"""
import sys
from dataclasses import replace

import numpy as np

import probe_world as P

n = int(sys.argv[1]) if len(sys.argv) > 1 else 150


def mean(w, v, ctrl, k):
    return float(np.mean([P.bout(w, v, ctrl, k, 5000 + s) for s in range(n)]))


worlds = [P.World("default uniform (12, sum)"), P.World("RBT-106 HP (12 in 3 patches)", patches=3)]
print(f"# n = {n}; v = 0.25 m/s; items per 15 s solo bout")
print("## B. Turn authority and heading noise (k = 6, the evolved ceiling)")
for w in worlds:
    for noise in (0.0, 1.0):
        for om in (0.25, 0.5, 1.0, 2.0):
            P.OMEGA, P.NOISE = om, noise
            b = max(mean(w, 0.25, "straight", 0), mean(w, 0.25, "arc", 0))
            s6 = mean(w, 0.25, "smell", 6.0)
            print(f"{w.name:30s} noise {noise:.1f} omega {om:4.2f}: blind-best {b:5.2f}  smell-k6 {s6:5.2f}  ratio {s6 / max(b, 1e-9):4.2f}", flush=True)
print("## C. Marginal returns from a weak start (omega 0.5 rad/s, noise 1.0)")
P.OMEGA, P.NOISE = 0.5, 1.0
for w in worlds:
    base_blind = mean(w, 0.25, "straight", 0)
    fast_blind = mean(w, 0.3125, "straight", 0)
    print(f"{w.name:30s} blind straight v 0.25 -> 0.3125: {base_blind:5.2f} -> {fast_blind:5.2f}  (+{100 * (fast_blind / base_blind - 1):4.0f}%)", flush=True)
    for k0 in (0.4, 1.0, 2.0, 4.0):
        a, b = mean(w, 0.25, "smell", k0), mean(w, 0.25, "smell", k0 + 0.4)
        print(f"{w.name:30s} smell k {k0:.1f} -> {k0 + 0.4:.1f}: {a:5.2f} -> {b:5.2f}  (+{100 * (b / max(a, 1e-9) - 1):4.0f}%)", flush=True)
