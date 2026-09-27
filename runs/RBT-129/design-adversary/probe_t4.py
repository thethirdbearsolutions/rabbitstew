"""Probe 5: T4's power when the smell channel pays only where the world pays perception.

T4 (DESIGN §7.3): over the 9 matched c = 1 points (3 prices x U, HP, PW), a one-sample t on the 9 point values
v = mean over the two faunas of (f_G - f_L).  Per-seed noise from the design's own perception model (power.py part 3,
M 20, D 8, rho 0, tau_p 0.05): per-seed SD of f 0.183 (holistic) and 0.119 (designed); G and L are separate runs at
the same seeds, so the difference's SD is sqrt(2) larger; the fauna mean halves the sum of variances.
The alternative tests the same contrast at the seed level inside the layouts R4 says can pay (PW, or PW + HP).

python3 probe_t4.py
"""
import math

import numpy as np

import adv_replica as A

rng = np.random.default_rng(12906)
B, n = 40000, 8
sd_seed = math.sqrt((0.183 * math.sqrt(2)) ** 2 + (0.119 * math.sqrt(2)) ** 2) / 2
print(f"# per-seed SD of the fauna-mean G - L difference: {sd_seed:.3f}; per-point SE at n 8: {sd_seed / math.sqrt(n):.3f}")
print("# Delta = the fauna-mean (f_G - f_L) where the channel pays; 0 elsewhere.  Power at Holm's first step (0.05/4)")
print("# and last step (0.05).  Layout order of the 9 points: 3 x U, 3 x HP, 3 x PW")
for where, mask in (("PW only", [0] * 6 + [1] * 3), ("PW + HP", [0] * 3 + [1] * 6), ("all 9", [1] * 9)):
    mask = np.array(mask, bool)
    for delta in (0.10, 0.25, 0.40):
        mu = np.where(mask, delta, 0.0)
        x = rng.normal(mu[None, :, None], sd_seed, (B, 9, n))  # seeds within points
        pts = x.mean(2)
        t9 = A.t_stat(pts)
        pw_t4 = [float(np.mean(np.abs(t9) > A.t_crit(a, 8))) for a in (0.05 / 4, 0.05)]
        sub = x[:, mask, :].mean(1)  # per seed, averaged over the paying points
        ts = A.t_stat(sub)
        pw_alt = [float(np.mean(np.abs(ts) > A.t_crit(a, n - 1))) for a in (0.05 / 4, 0.05)]
        print(f"  {where:8s} Delta {delta:.2f} | T4 as registered: {pw_t4[0]:.2f} / {pw_t4[1]:.2f} | "
              f"seed-level test within the paying layouts: {pw_alt[0]:.2f} / {pw_alt[1]:.2f}")
