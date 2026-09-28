"""RBT-116 (FC-M2): do the SENS priors move under W1's surface eating?

power.py's SENS_C priors (two-nose 0.48, one-nose 0.32 at τ = 1 s) come from the r5 PW caricature
(design-adversary/r5_probe.py via tau_probe.py), whose mouth is a POINT eating within 0.35 m (centre rule).  Under
`--eat-from root --eat-rule surface` the mouth is the root's surface plus 0.35 m.  The caricature has no body, so this
widens its point mouth to the reach a surface rule gives a root of horizontal half-extent h: 0.35 + h, for the
Pioneer chassis (half-extents 0.208 x 0.176 m, so h ~ 0.19) and a larger root (h 0.35), with the 0.35 m centre rule as
the reference.  τ = 1 s, G 2.5, the r5 call; 25 genomes x 2 batteries per cell, as tau_probe.py.  A caricature: its
numbers are priors, and SENS is measured at the gate.

    python runs/RBT-116/prior_surface_probe.py [genomes] > runs/RBT-116/prior_surface_probe.txt
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "design-adversary"))
import r5_probe as R  # noqa: E402
import steer_probe as S  # noqa: E402

n = int(sys.argv[1]) if len(sys.argv) > 1 else 25
R.TAU = 1.0
print(f"# prior_surface_probe.py: {n} genomes x 2 batteries per cell; r5_probe's caricature and call; G {R.G_TR}, tau {R.TAU}")
print("body          mouth reach (m)   single PASS   confirmed   mean F   mean dT")
for reach, lab in ((0.35, "centre rule (reference)"), (0.54, "surface, Pioneer chassis"), (0.70, "surface, h 0.35 root")):
    for body, ctrl, par in (("steer2-k6", "steer2", 6.0), ("steer1-k32", "steer1", 32.0)):
        S.EAT = reach
        r1 = [R.passes(ctrl, par, g) for g in range(n)]
        r2 = [R.passes(ctrl, par, 5000 + g) for g in range(n)]
        p1 = np.mean([x[0] for x in r1]); pc = np.mean([a[0] and b[0] for a, b in zip(r1, r2)])
        print(f"{body:12s} {reach:5.2f} {lab:26s} {p1:6.2f}   {pc:9.2f}   {np.mean([x[1] for x in r1]):+6.3f}  {np.mean([x[2] for x in r1]):+7.3f}", flush=True)
