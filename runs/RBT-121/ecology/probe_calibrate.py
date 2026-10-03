"""RBT-121 audit C: calibrate the kinematic model's steering regime to the one real-body measurement of what a
working nose pays, paper 10 / RBT-106's installed compass (a = 64): +0.844 on 1.308 in the uniform world
(x1.65) and +2.103 on 1.537 in the patchy one (x2.37), solo, 15 s.  Grid over turn limit and heading noise at
k = 64; the regime whose two ratios sit nearest the measured pair is the 'realistic' one used in AUDIT.md."""
import sys
import numpy as np
import probe_world as P
n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
U, H = P.World("uniform"), P.World("patchy", patches=3)
def m(w, v, c, k): return float(np.mean([P.bout(w, v, c, k, 20000 + s) for s in range(n)]))
print(f"# n = {n}; target ratios: uniform x1.65, patchy x2.37 (RBT-106 prize.txt)")
for om in (0.25, 0.5, 1.0):
    for noise in (0.0, 0.5, 1.0):
        P.OMEGA, P.NOISE = om, noise
        r = []
        for w in (U, H):
            b = max(m(w, 0.25, "straight", 0), m(w, 0.25, "arc", 0)); s = m(w, 0.25, "smell", 64.0); r.append(s / b)
        err = abs(np.log(r[0] / 1.65)) + abs(np.log(r[1] / 2.37))
        print(f"omega {om:4.2f} noise {noise:3.1f}: uniform x{r[0]:4.2f}  patchy x{r[1]:4.2f}  log-error {err:4.2f}", flush=True)
