"""Which quantity is RBT-61's dose-response calibrated in? (settles a discrepancy with RBT-45)

RBT-45's `runs/RBT-45/motif.py` recounts drift reachability against

    k = [P(n1->e1) + P(n1->e2)] - [P(n2->e1) + P(n2->e2)]   ==   s1 - s2

and compares it to thresholds 16 / 32 / 64 taken from RBT-61's hand-install dose-response.
Its docstring calls this "the coefficient on (n1 - n2) arriving at the steering axis e1 + e2".

But installing the 4-link antisymmetric motif at weight w gives s1 = +2w and s2 = -2w, so the
signal on the steering axis is 2w(n1 - n2): the coefficient on (n1 - n2) is 2w = (s1 - s2)/2,
while s1 - s2 = 4w.  RBT-61's verify_independent.py labels the w=8 row "k on steering axis = +16",
i.e. 2w.  So the two differ by a factor of two and the thresholds belong to (s1 - s2)/2.

This installs the motif at a known w and reads it back both ways.  No simulation.
"""
import glob, json
import numpy as np
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize

RUN = "runs/RBT-60/A30-801"
cfg = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
ph = synthesize(Genotype.load(sorted(glob.glob(f"{RUN}/conventional/final/*.json"))[0]), cfg.synthesis)

nose, eff = {}, {}
for i, u in enumerate(ph.units):
    if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "food":
        nose[u.part] = i
    if u.part in (1, 2) and u.unit.kind == "effector":
        eff[u.part] = i


def s_terms(links):
    """Each nose's signed gain onto the steering axis, path sum to depth 4, no clamp."""
    n = len(ph.units)
    M = np.zeros((n, n))
    for s, d, w in links:
        M[d, s] += w
    out = {}
    for part, si in nose.items():
        v = np.zeros(n); v[si] = 1.0; tot = np.zeros(n)
        for _ in range(4):
            v = M @ v
            tot += v
            if not v.any():
                break
        out[part] = tot
    return out[1][eff[1]] + out[1][eff[2]], out[2][eff[1]] + out[2][eff[2]]


b1, b2 = s_terms(ph.links)
for w in (8.0, 16.0, 32.0):
    motif = list(ph.links) + [(nose[1], eff[1], w), (nose[1], eff[2], w),
                              (nose[2], eff[1], -w), (nose[2], eff[2], -w)]
    m1, m2 = s_terms(motif)
    d1, d2 = m1 - b1, m2 - b2  # the motif's own contribution, baseline removed
    print(f"w={w:5g}   s1 {d1:+8.3f}  s2 {d2:+8.3f}   "
          f"(s1-s2)/2 = {(d1-d2)/2:+8.3f}   s1-s2 = {d1-d2:+8.3f}   "
          f"RBT-61 labels this row k={2*w:+.0f}")
