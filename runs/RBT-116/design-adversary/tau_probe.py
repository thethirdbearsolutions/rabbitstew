"""RBT-116 steer.py design adversary: does Amendment 1's tau = 2 s (was 1 s) move the design-stage priors?
Re-runs r5_probe.py's PW caricature (the r5 call: trajectory veto + confirmation) at tau = 1 and tau = 2, G = 2.5, for
the one-nose run-and-tumble route (R5-2's SENS_1 prior, power.py's SENS_C_ONE = 0.32) and the two-nose steerer
(SENS_C_TWO = 0.48).  A caricature, not W1: its numbers are priors, as Amendment 1 says; SENS_1 is measured at G8(f).
    python3 tau_probe.py [genomes] > tau_probe.txt
"""
import sys

import numpy as np

import r5_probe as R

n = int(sys.argv[1]) if len(sys.argv) > 1 else 25
print(f"# tau_probe.py: {n} genomes x 2 batteries per cell; r5_probe's caricature and call; G {R.G_TR}")
print("body          tau   single PASS   confirmed   mean F   mean dT")
for lab, ctrl, par in (("steer2-k6", "steer2", 6.0), ("steer1-k8", "steer1", 8.0), ("steer1-k32", "steer1", 32.0)):
    for tau in (1.0, 2.0):
        R.TAU = tau
        r1 = [R.passes(ctrl, par, g) for g in range(n)]
        r2 = [R.passes(ctrl, par, 5000 + g) for g in range(n)]
        p1 = np.mean([x[0] for x in r1]); pc = np.mean([a[0] and b[0] for a, b in zip(r1, r2)])
        print(f"{lab:12s} {tau:4.1f}   {p1:10.2f}   {pc:9.2f}   {np.mean([x[1] for x in r1]):+6.3f}  {np.mean([x[2] for x in r1]):+7.3f}", flush=True)
