"""RBT-97 adversary: does runs/RBT-97/mechanism.py's verdict line implement the pre-registered rule?

Pre-registration (RBT-97, 12:28 UTC), verbatim: "food-dependent if phantom retains under 25% of the
motif's pooled gain and the per-robot motif - phantom CI excludes zero; gait effect if phantom
retains 75% or more WITH ITS OWN CI EXCLUDING ZERO; unresolved at 64 seeds otherwise."

mechanism.py (origin/results/RBT-97-mechanism, 39cddff), verbatim:
    "GAIT EFFECT" if frac >= 0.75 and (dlo > 0) == (dhi > 0)
where [dlo, dhi] is the bootstrap CI of MOTIF - PHANTOM, not of phantom.  At full retention
motif - phantom is ~0, so this branch requires retention to be significantly DIFFERENT from 100%.

This scores both rules on synthetic arms built from RBT-67's committed P-801 per-seed noise, exactly
as adversary_band.py builds them (5 correctly signed robots, a = 64 and 384), with mechanism.py's
own statistics: per-robot mean deltas, bootstrap over robots, pooled retention = mean(phantom) /
mean(motif).  2,000 synthetic arms per true retention R, 2,000 bootstrap draws each.

Usage: python runs/RBT-97/adversary_verdict.py
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)
import numpy as np

CORRECT = (0, 200, 300, 500, 590)
RS = (0.0, 0.25, 0.5, 0.75, 0.9, 1.0, 1.1)
N_EXP, N_BOOT = 2000, 2000


def boot(v, rng):
    v = np.asarray(v, float)
    i = rng.integers(0, len(v), (N_BOOT, len(v)))
    m = v[i].mean(axis=1)
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def one(rng, motif, R):
    md = np.array([d.mean() for d in motif])  # the motif arm as observed
    pd_ = np.array([R * d.mean() + rng.choice(d - d.mean(), len(d)).mean() for d in motif])
    frac = pd_.mean() / md.mean()
    _, dlo, dhi = boot(md - pd_, rng)
    _, plo, phi = boot(pd_, rng)
    code = ("FOOD" if frac < 0.25 and dlo > 0 else
            "GAIT" if frac >= 0.75 and (dlo > 0) == (dhi > 0) else "UNRES")
    prereg = ("FOOD" if frac < 0.25 and dlo > 0 else
              "GAIT" if frac >= 0.75 and (plo > 0) == (phi > 0) else "UNRES")
    return code, prereg


def main():
    d = json.load(open("docs/artifacts/RBT-67/p801.json"))
    rng = np.random.default_rng(971)
    L = ["RBT-97 adversary: mechanism.py's verdict line against the pre-registered rule (synthetic, RBT-67 P-801 noise)", ""]
    for c in d["cells"]:
        if c["a"] not in (64.0, 384.0):
            continue
        motif = [np.asarray(r["diffs"], float) for r in c["robots"] if r["gen"] in CORRECT]
        L.append(f"a = {c['a']:.0f}, 5 correctly signed robots")
        L.append(f"   {'true R':>6s} | {'code: FOOD':>10s} {'UNRES':>6s} {'GAIT':>6s} | {'prereg: FOOD':>12s} {'UNRES':>6s} {'GAIT':>6s}")
        for R in RS:
            res = [one(rng, motif, R) for _ in range(N_EXP)]
            f = lambda k, j: sum(r[j] == k for r in res) / len(res)
            L.append(f"   {R:6.2f} | {f('FOOD', 0):10.2f} {f('UNRES', 0):6.2f} {f('GAIT', 0):6.2f} | "
                     f"{f('FOOD', 1):12.2f} {f('UNRES', 1):6.2f} {f('GAIT', 1):6.2f}")
        L.append("")
    sys.stdout.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
