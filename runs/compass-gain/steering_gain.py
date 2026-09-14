"""What compass term did selection actually build, against the one that pays? (supersedes the
`sensor_influence` survey, which summed ABSOLUTE weights and so could not tell a compass from a
smell-gated pirouette)

RBT-61's correction fixes the quantity that matters on the Pioneer.  Both drive wheels hinge about
their own outward normals (world-frame axis dot product -1.0000), so the SUM of the two effector
commands is the steering axis and their DIFFERENCE is the throttle.  Write the signed gain from each
wheel nose to the steering axis as

    s_i = g[n_i -> e1] + g[n_i -> e2]

and decompose the pair into the two terms that have opposite fates:

    a = (s1 - s2) / 2     the ANTISYMMETRIC term: puts a(n1 - n2) on the steering axis.  This is
                          the compass.  It is exactly RBT-61's k, which measured, by hand-install
                          on 7 robots x 64 paired seeds against a 1.516-item baseline:
                              a = 16  ->  +0.054  [-0.040, +0.158]   null
                              a = 32  ->  +0.246  [+0.147, +0.353]
                              a = 64  ->  +0.897  [+0.632, +1.176]   +59%, 7/7 robots
                          and, past the top of that sweep, still rising at a = 384 (RBT-67).
    c = (s1 + s2) / 2     the COMMON term: puts c(n1 + n2) on the steering axis -- turn harder when
                          anything smells, with no gradient in it.  This is what RBT-61's withdrawn
                          spike installed by mistake, and at w=32 it cost -1.502 items (0/7 robots).

RBT-81 retired two things this script used to report, and the numbers below are computed by
``rabbitstew.analysis.steering_terms`` rather than here:

  * The gains are the DEPTH-1 terms -- the weight on the direct nose->effector links, exactly the
    quantity RBT-61 installed into, exact on every brain.  The old PATH column (signed path sum to
    depth 4 through the whole network) is still printed, but labelled for what it is: a truncation
    of a series that converges only if the recurrent core's spectral radius rho is below 1, and rho
    is above 1 on every committed Pioneer best (1.57-4.92; RBT-67's adversary).  Its value there is
    a property of where the counting stopped.  rho is printed beside it.
  * "|a| > |c|", reported as gradient-dominance, is algebraically s1 * s2 < 0: a sign test with no
    magnitude in it (RBT-78's adversary).  It is replaced by the BALANCE ratio
    r = min(|s1|, |s2|) / max(|s1|, |s2|) -- 1 for a true four-link motif, 0 for a single wired
    nose -- reported as a number, and by the SIGN of s1 * s2 reported separately.  No pass/fail
    threshold is defined on either.

A single wired nose gives |a| = |c| and r = 0: half compass, half pirouette.  It is not a compass,
and this is the distinction the first survey could not draw.

File analysis only.  No simulation.  usage: steering_gain.py RUN LABEL
"""
import glob, json, os, sys

import numpy as np

from rabbitstew.analysis import steering_terms
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize

DEPTH = 4  #: the depth the old PATH column was truncated at; printed for comparison, never used as a quantity
PAYS, HALF_PAYS, NULLS = 64.0, 32.0, 16.0  # RBT-61's measured points, in units of a


def terms(ph):
    """``steering_terms`` at depth 1, plus the depth-4 path term for the labelled comparison column."""
    return steering_terms(ph, depth=DEPTH)


def survey(run, kind):
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    rows = [t for t in (terms(synthesize(Genotype.load(f), cfg.synthesis))
                        for f in sorted(glob.glob(f"{run}/{kind}/final/*.json"))) if t]
    return rows


def report(rows):
    a = np.array([abs(r["a"]) for r in rows])
    both = np.array([r["s_left"] != 0.0 and r["s_right"] != 0.0 for r in rows])
    opposed = np.array([r["opposed"] < 0 for r in rows])
    r_ = np.array([r["balance"] for r in rows])
    print(f"    DIRECT  (depth 1, exact)   |a| median {np.median(a):8.3f}  max {a.max():9.3f}    "
          f"both noses wired {int(both.sum()):2d}/{len(rows)}   opposed sign (s1*s2<0) {int(opposed.sum()):2d}/{len(rows)}   "
          f"balance r median {np.median(r_):.3f}  IQR [{np.percentile(r_, 25):.3f}, {np.percentile(r_, 75):.3f}]")
    print(f"            |a| >= 16 (null) {int((a >= NULLS).sum()):2d}   "
          f">= 32 (+0.25) {int((a >= HALF_PAYS).sum()):2d}   >= 64 (+0.90) {int((a >= PAYS).sum()):2d}")
    ap = np.array([abs(r["path"]["a"]) for r in rows])
    rho = np.array([r["rho"] for r in rows])
    print(f"    PATH    (depth {DEPTH}, linearised; NOT a quantity where rho > 1)   |a| median {np.median(ap):8.3f}  max {ap.max():9.3f}    "
          f"rho median {np.median(rho):.2f}  range [{rho.min():.2f}, {rho.max():.2f}]   rho > 1: {int((rho > 1).sum()):2d}/{len(rows)}")


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
    report(rows)

# --- the joint question: magnitude AND the pair's balance in the same individual, no threshold ---
if os.environ.get("BEST"):
    for kind in ("conventional",):
        rows = survey(run, kind)
        if not rows:
            continue
        opp = [r for r in rows if r["opposed"] < 0]
        best = max(opp, key=lambda r: abs(r["a"])) if opp else None
        print(f"  opposed-sign pairs (s1*s2<0): {len(opp):2d}/{len(rows)}   "
              + (f"largest |a| among them: {abs(best['a']):7.3f} at balance r = {best['balance']:.3f}   "
                 f"median r among them {np.median([r['balance'] for r in opp]):.3f}" if opp else "none")
              + "   (RBT-61/67 payoff points: a = 32 -> +0.25 items, 64 -> +0.90, 384 -> +1.88, all at r = 1)")
