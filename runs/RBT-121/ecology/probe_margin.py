"""RBT-121 audit C: the smell margins in auditor B's units (items per season, one 15 s bout = one season),
for B's threshold of about 0.1 (PR #395, finding 3).  Calibrated regime (turn 0.5 rad/s, noise 1.0), v = 0.25."""
import numpy as np
import probe_world as P
P.OMEGA, P.NOISE = 0.5, 1.0
n = 300
def m(w, c, k): return float(np.mean([P.bout(w, 0.25, c, k, 40000 + s) for s in range(n)]))
PW = dict(patches=2, patch_radius=0.4, smell="log", decay=1.5, regrow="delay", regrow_delay=60.0, radius=4.0)
print(f"# n = {n}; items per season; 'step' = one mutation-sized nose-gain step (+0.4)")
for name, w, g in (("committed uniform", P.World("W0"), 1.0), ("committed HP", P.World("HP", patches=3), 1.0), ("PW (gain 10)", P.World("PW", **PW), 10.0)):
    P.GAIN = g
    b = max(m(w, "straight", 0), m(w, "arc", 0))
    k = {kk: m(w, "smell", kk) for kk in (0.4, 1.0, 1.4, 2.0, 2.4, 6.0)}
    print(f"{name:18s} blind {b:5.2f}  k6 margin {k[6.0] - b:+.2f}  | first nose k0.4 - blind {k[0.4] - b:+.3f}  step k1->1.4 {k[1.4] - k[1.0]:+.3f}  step k2->2.4 {k[2.4] - k[2.0]:+.3f}", flush=True)
