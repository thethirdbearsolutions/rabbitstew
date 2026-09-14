"""What compass term did selection actually build, against the one that pays? (supersedes the
`sensor_influence` survey, which summed ABSOLUTE weights and so could not tell a compass from a
smell-gated pirouette)

RBT-61's correction fixes the quantity that matters on the Pioneer.  Both drive wheels hinge about
their own outward normals (world-frame axis dot product -1.0000), so the SUM of the two effector
commands is the steering axis and their DIFFERENCE is the throttle.  Write the signed linearised
gain from each wheel nose to the steering axis as

    s_i = g[n_i -> e1] + g[n_i -> e2]

and decompose the pair into the two terms that have opposite fates:

    a = (s1 - s2) / 2     the ANTISYMMETRIC term: puts a(n1 - n2) on the steering axis.  This is
                          the compass.  It is exactly RBT-61's k, which measured, by hand-install
                          on 7 robots x 64 paired seeds against a 1.516-item baseline:
                              a = 16  ->  +0.054  [-0.040, +0.158]   null
                              a = 32  ->  +0.246  [+0.147, +0.353]
                              a = 64  ->  +0.897  [+0.632, +1.176]   +59%, 7/7 robots
    c = (s1 + s2) / 2     the COMMON term: puts c(n1 + n2) on the steering axis -- turn harder when
                          anything smells, with no gradient in it.  This is what RBT-61's withdrawn
                          spike installed by mistake, and at w=32 it cost -1.502 items (0/7 robots).

A single wired nose gives |a| = |c|: half compass, half pirouette.  It is not a compass, and this is
the distinction the first survey could not draw.

Two gains are reported because they bracket the truth:
  DIRECT  -- weight on a nose->effector link only.  Exactly the quantity RBT-61 installed into, so
             directly comparable to the table above, with no linearisation at all.
  PATH    -- signed path sum to depth 4 through the whole network.  Counts routes through the global
             brain, but linearises tanh at the origin, and tanh only ever attenuates, so this is an
             UPPER bound on what those routes deliver.

File analysis only.  No simulation.  usage: steering_gain.py RUN LABEL
"""
import glob, json, os, sys

import numpy as np

from rabbitstew.genotype import Genotype, JointType
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize

DEPTH = 4
PAYS, HALF_PAYS, NULLS = 64.0, 32.0, 16.0  # RBT-61's measured points, in units of a


def terms(ph):
    n = len(ph.units)
    M = np.zeros((n, n))
    for s, d, w in ph.links:
        M[d, s] += w
    live = [i for i, ui in enumerate(ph.units)
            if ui.unit.kind == "effector" and ui.part in (1, 2)
            and ph.parts[ui.part].parent is not None
            and ph.parts[ui.part].joint_type != JointType.FIXED]
    nose = {ui.part: i for i, ui in enumerate(ph.units)
            if ui.unit.kind == "sensor" and ui.unit.source == "food" and ui.part in (1, 2)}
    if len(nose) < 2 or not live:
        return None
    direct, path = {}, {}
    for part, i in nose.items():
        direct[part] = float(M[live, i].sum())
        v = np.zeros(n); v[i] = 1.0; g = np.zeros(n)
        for _ in range(DEPTH):
            v = M @ v
            g += v
            if not v.any():
                break
        path[part] = float(g[live].sum())
    out = {}
    for tag, s in (("direct", direct), ("path", path)):
        out[tag] = ((s[1] - s[2]) / 2.0, (s[1] + s[2]) / 2.0)
        out[tag + "_wired"] = (abs(s[1]) > 1e-9, abs(s[2]) > 1e-9)
    return out


def survey(run, kind):
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    rows = [t for t in (terms(synthesize(Genotype.load(f), cfg.synthesis))
                        for f in sorted(glob.glob(f"{run}/{kind}/final/*.json"))) if t]
    return rows


def report(rows, tag):
    a = np.array([abs(r[tag][0]) for r in rows])
    c = np.array([abs(r[tag][1]) for r in rows])
    both = np.array([all(r[tag + "_wired"]) for r in rows])
    # a compass needs the gradient to dominate the pirouette
    clean = a > c
    print(f"    {tag.upper():7} |a| median {np.median(a):8.3f}  max {a.max():9.3f}    "
          f"both noses wired {int(both.sum()):2d}/{len(rows)}   |a|>|c| {int(clean.sum()):2d}/{len(rows)}")
    print(f"            a >= 16 (null) {int((a >= NULLS).sum()):2d}   "
          f">= 32 (+0.25) {int((a >= HALF_PAYS).sum()):2d}   >= 64 (+0.90) {int((a >= PAYS).sum()):2d}"
          f"    ... AND |a|>|c|: {int(((a >= HALF_PAYS) & clean).sum()):2d} / {int(((a >= PAYS) & clean).sum()):2d}")


run, label = sys.argv[1], sys.argv[2]
print(f"\n{label}  ({run})")
for kind in ("conventional", "holistic"):
    if not os.path.isdir(f"{run}/{kind}/final"):
        continue
    rows = survey(run, kind)
    if not rows:
        print(f"  {kind:12} no individual carries a food nose on both wheels")
        continue
    print(f"  {kind}  n={len(rows)}")
    report(rows, "direct")
    report(rows, "path")

# --- the joint question: magnitude AND gradient-dominance in the same individual ---
if os.environ.get("BEST"):
    for kind in ("conventional",):
        rows = survey(run, kind)
        for tag in ("direct", "path"):
            cand = [(abs(r[tag][0]), abs(r[tag][1])) for r in rows if abs(r[tag][0]) > abs(r[tag][1])]
            best = max(cand)[0] if cand else 0.0
            print(f"  {tag:6} gradient-dominant individuals: {len(cand):2d}/{len(rows)}   "
                  f"best |a| among them: {best:7.3f}   (needs 32 for +0.25 items, 64 for +0.90)")
