"""RBT-121 adversary: sampling spread of audit B's 6-draw repeatability estimator, and B's own s(delta) on the
variance components re-estimated from 12 draws.  Reads the matrices noise_components.py saved.
    python runs/RBT-121/adversary/noise_resample.py > runs/RBT-121/adversary/noise_resample.txt"""
import itertools
import sys

import numpy as np

sys.path.insert(0, "/tmp/claude-0/adv_noise/ga"); sys.path.insert(0, "/home/user/rabbitstew/runs/RBT-113")
from noise import selection_s  # audit B's own Monte Carlo, unchanged  # noqa: E402


def b_estimator(A):  # audit B's noise.py lines, verbatim in effect
    k = A.shape[1]
    sw = np.sqrt((A - A.mean(axis=0)).var(axis=1, ddof=1).mean() * k / (k - 1))
    sb2 = max(A.mean(axis=1).var(ddof=1) - sw ** 2 / k, 0.0)
    return np.sqrt(sb2), sw, sb2 / (sb2 + sw ** 2 / 2)


for kind in ("holistic", "conventional"):
    A = np.load(f"/tmp/claude-0/adv_noise/noise_{kind}.npy")[..., 0]
    sb, sw, r = b_estimator(A)
    print(f"== {kind}: B's estimator on all 12 draws: between SD {sb:.3f}, member x draw SD {sw:.3f}, rep(2-draw) {r:.3f}; "
          f"total SD of the 2-draw fitness {np.sqrt(sb ** 2 + sw ** 2 / 2):.3f}")
    reps = [b_estimator(A[:, list(c)])[2] for c in itertools.combinations(range(12), 6)]
    print(f"   B's estimator on every 6-of-12 draw subset (n {len(reps)}): rep(2-draw) median {np.median(reps):.3f}, "
          f"5-95% [{np.percentile(reps, 5):.3f}, {np.percentile(reps, 95):.3f}], share exactly 0 {np.mean(np.array(reps) == 0):.2f}")
    for d in (0.02, 0.05, 0.1):
        print(f"   delta +{d}: s at 2 draws {selection_s(A.mean(), sb, sw, d):+.3f}  (analytic i*delta/sigma_P = {1.271 * d / np.sqrt(sb ** 2 + sw ** 2 / 2):.3f});"
              f"  same s with between SD set to 0: {selection_s(A.mean(), 0.0, sw, d):+.3f}")
