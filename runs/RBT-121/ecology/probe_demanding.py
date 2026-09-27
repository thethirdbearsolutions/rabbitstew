"""RBT-121 audit C: a perception-demanding world.  Candidate FoodConfig settings, evaluated with the
kinematic forager of probe_world.py under two steering regimes:

  ideal     turn limit 2 rad/s, no heading noise
  weak      turn limit 0.5 rad/s, heading noise 1 rad/sqrt(s): a lump that barely steers (probe_gradient.py)

For each world: blind-best (better of straight and arc) against smell at k = 6 (the evolved weight
ceiling), at v = 0.25 m/s; plus, in the weak regime, the marginal return of one mutation-sized step
in link gain (k 1.0 -> 1.4 and 2.0 -> 2.4) against +25% speed for the blind straight mover.

python3 runs/RBT-121/ecology/probe_demanding.py [n]
"""
import sys

import numpy as np

import probe_world as P

n = int(sys.argv[1]) if len(sys.argv) > 1 else 150

WORLDS = [
    P.World("W0 default uniform"),
    P.World("W0p RBT-106 HP (3 patches)", patches=3),
    P.World("W1 12 in 1 patch r0.5, log, decay 1.5, own-spot", patches=1, patch_radius=0.5, smell="log", decay=1.5, regrow="delay", regrow_delay=60.0),
    P.World("W2 12 in 2 patches r0.4, log, decay 1.5, own-spot", patches=2, patch_radius=0.4, smell="log", decay=1.5, regrow="delay", regrow_delay=60.0),
    P.World("W3 W2 in a 4 m disc", patches=2, patch_radius=0.4, smell="log", decay=1.5, regrow="delay", regrow_delay=60.0, radius=4.0),
    P.World("W4 W2 with eat_radius 0.2", patches=2, patch_radius=0.4, smell="log", decay=1.5, regrow="delay", regrow_delay=60.0, eat_radius=0.2),
    P.World("W5 6 uniform, log, decay 1.5, no regrow", items=6, smell="log", decay=1.5, regrow="none"),
]


def m(w, v, ctrl, k, seed0=9000):
    return float(np.mean([P.bout(w, v, ctrl, k, seed0 + s) for s in range(n)]))


print(f"# n = {n}; v = 0.25 m/s; items per 15 s solo bout; smell = k 6")
for w in WORLDS:
    row = [f"{w.name:52s}"]
    for regime, om, noise in (("ideal", 2.0, 0.0), ("weak", 0.5, 1.0)):
        P.OMEGA, P.NOISE = om, noise
        b = max(m(w, 0.25, "straight", 0), m(w, 0.25, "arc", 0))
        s = m(w, 0.25, "smell", 6.0)
        row.append(f"{regime}: blind {b:5.2f} smell {s:5.2f} x{s / max(b, 1e-9):4.1f}")
    P.OMEGA, P.NOISE = 0.5, 1.0
    b0, b1 = m(w, 0.25, "straight", 0), m(w, 0.3125, "straight", 0)
    k1a, k1b = m(w, 0.25, "smell", 1.0), m(w, 0.25, "smell", 1.4)
    k2a, k2b = m(w, 0.25, "smell", 2.0), m(w, 0.25, "smell", 2.4)
    row.append(f"weak marginal: +25% speed {100 * (b1 / max(b0, 1e-9) - 1):+4.0f}%  k1->1.4 {100 * (k1b / max(k1a, 1e-9) - 1):+4.0f}%  k2->2.4 {100 * (k2b / max(k2a, 1e-9) - 1):+4.0f}%")
    print("  |  ".join(row), flush=True)
