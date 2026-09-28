"""RBT-132 (the 07:10 ruling, item 1): the per-plant share K3 now counts as SEEN, in the design-stage caricature.

A plant is seen when, on its stage-2 battery, the veto passes (c3: paths differ on > 8 of 16 draws) and the ΔT lower
bound is > 0 (c2), and a second independent battery repeats c2 and c3.  F plays no part.  r5_probe.py's PW caricature
and call (design-adversary/r5_probe.py, unchanged), 25 genomes x 2 batteries per cell, as tau_probe.py; the confirmed
STEERS share (which also needs F) is printed beside it.  A caricature: its shares are priors for probe_power.py.

    python runs/RBT-116/k3_seen_probe.py > runs/RBT-116/k3_seen_probe.txt
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "design-adversary"))
import r5_probe as R  # noqa: E402
import steer_probe as S  # noqa: E402


def battery(ctrl, par, block):
    fi, fd, ti, td, diff = [], [], [], [], 0
    trng = np.random.default_rng(900000 + block)
    for k in range(16):
        seed = 10_000 * (block + 1) + k
        a, b = R.season(ctrl, par, seed, None), R.season(ctrl, par, seed, np.radians(trng.uniform(30, 330)))
        fi.append(a[0]); fd.append(b[0]); ti.append(a[1]); td.append(b[1])
        diff += int(np.abs(a[2] - b[2]).max() > 1e-9)
    dF, dT = np.array(fi, float) - fd, np.array(ti) - np.array(td)

    def lb(x):
        s = x.std(ddof=1)
        return x.mean() - S.T95_15 * s / 4 if s > 0 else x.mean()
    seen = bool(lb(dT) > 0 and diff > 8)
    ok = bool(dF.mean() >= 0.25 and lb(dF) > 0 and seen)
    return seen, ok


n = int(sys.argv[1]) if len(sys.argv) > 1 else 25
print(f"# k3_seen_probe.py: {n} genomes x 2 batteries per cell; r5_probe's caricature and call; G {R.G_TR}")
print("body          tau   seen (c2 & c3, repeated)   confirmed STEERS")
for lab, ctrl, par in (("steer2-k6", "steer2", 6.0), ("steer1-k32", "steer1", 32.0), ("steer1-k8", "steer1", 8.0)):
    for tau in (1.0, 2.0):
        R.TAU = tau
        r1 = [battery(ctrl, par, g) for g in range(n)]
        r2 = [battery(ctrl, par, 5000 + g) for g in range(n)]
        seen = np.mean([a[0] and b[0] for a, b in zip(r1, r2)])
        conf = np.mean([a[1] and b[1] for a, b in zip(r1, r2)])
        print(f"{lab:12s} {tau:4.1f}   {seen:24.2f}   {conf:16.2f}", flush=True)
