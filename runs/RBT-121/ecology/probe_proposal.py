"""RBT-121 audit C: the proposed perception-demanding world, against the committed ones, in the steering
regime calibrated to RBT-106's installed compass (probe_calibrate.py: turn limit 0.5 rad/s, heading noise
1.0 rad/sqrt(s)).  Link gain k = 6 (the evolved ceiling, paper 5).  Columns: blind-best and smell items per
15 s solo bout at v = 0.25 and their ratio; the marginal return of +25% speed (blind straight) against one
mutation-sized step in link gain (k 1.0 -> 1.4, k 2.0 -> 2.4) from a weak start; and the equal-income check:
smell at v = 0.25 against blind at v = 0.5 (twice the speed).

python3 runs/RBT-121/ecology/probe_proposal.py [n]
"""
import sys
import numpy as np
import probe_world as P
n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
P.OMEGA, P.NOISE = 0.5, 1.0
def m(w, v, c, k): return float(np.mean([P.bout(w, v, c, k, 30000 + s) for s in range(n)]))
def se(w, v, c, k):
    x = np.array([P.bout(w, v, c, k, 30000 + s) for s in range(n)], float); return x.mean(), x.std(ddof=1) / np.sqrt(n)
PROPOSED = dict(patches=2, patch_radius=0.4, smell="log", decay=1.5, regrow="delay", regrow_delay=60.0, radius=4.0)
CASES = [("W0 default uniform", P.World("W0"), 1.0), ("W0p RBT-106 HP", P.World("W0p", patches=3), 1.0),
         ("W0 + gain 10", P.World("W0"), 10.0), ("W0p + gain 10", P.World("W0p", patches=3), 10.0),
         ("PW world only (gain 1)", P.World("PW", **PROPOSED), 1.0),
         ("PW perception-demanding (gain 10)", P.World("PW", **PROPOSED), 10.0),
         ("PW gain 20", P.World("PW", **PROPOSED), 20.0)]
print(f"# n = {n}; regime: turn 0.5 rad/s, noise 1.0; k = 6; v = 0.25 unless stated")
for name, w, g in CASES:
    P.GAIN = g
    bs, bss = se(w, 0.25, "straight", 0); ba, bas = se(w, 0.25, "arc", 0)
    b, bse = (bs, bss) if bs >= ba else (ba, bas)
    s, sse = se(w, 0.25, "smell", 6.0)
    b2 = max(m(w, 0.5, "straight", 0), m(w, 0.5, "arc", 0))
    f0, f1 = bs, m(w, 0.3125, "straight", 0)
    k1a, k1b = m(w, 0.25, "smell", 1.0), m(w, 0.25, "smell", 1.4)
    k2a, k2b = m(w, 0.25, "smell", 2.0), m(w, 0.25, "smell", 2.4)
    print(f"{name:36s} blind {b:5.2f}±{bse:4.2f}  smell {s:5.2f}±{sse:4.2f}  x{s / b:4.2f}  | +25% speed {100 * (f1 / f0 - 1):+4.0f}%  k1->1.4 {100 * (k1b / k1a - 1):+4.0f}%  k2->2.4 {100 * (k2b / k2a - 1):+4.0f}%  | blind at 2x speed {b2:5.2f} (smell/2x-blind x{s / b2:4.2f})", flush=True)
