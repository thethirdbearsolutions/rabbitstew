"""RBT-97 adversary, round 2: the phantom table re-derived from the author's committed readout.

Input: docs/artifacts/RBT-97-p801-mechanism.txt (PR #79).  The readout commits per-robot means to
three decimals, not per-seed rows, so what can be re-derived from it is everything pooled: the
per-rung means over robots, the retention, and intervals over robots.  Both the author's error term
(percentile bootstrap over robots, 20,000 draws) and a t-interval over robots (df n - 1) are shown,
because round 1 found the bootstrap anti-conservative at n = 5-7.

The verdict is scored three ways: the author's code line as merged, the pre-registered rule
(gait: phantom's OWN interval excluding zero), and the same with t-intervals.

Usage: python runs/RBT-97/adversary_round2.py [readout.txt]
"""
import math
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)
import numpy as np

T975 = {4: 2.776, 5: 2.571, 6: 2.447}
ROW = re.compile(r"^g(\d+)\s+([+-]1)\s+(\d+)\s+\|\s+([\d.]+)\s+([+-][\d.]+)\s+([+-][\d.]+)\s+([+-][\d.]+)\s+\|")


def tint(v):
    v = np.asarray(v, float)
    m = float(v.mean())
    h = T975[len(v) - 1] * float(v.std(ddof=1)) / math.sqrt(len(v))
    return m, m - h, m + h


def boot(v, rng, draws=20000):
    v = np.asarray(v, float)
    i = rng.integers(0, len(v), (draws, len(v)))
    m = v[i].mean(axis=1)
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def verdicts(frac, diff_ci, ph_ci):
    dlo, dhi = diff_ci
    plo, phi = ph_ci
    food = frac < 0.25 and dlo > 0
    code = "FOOD-DEPENDENT" if food else "GAIT EFFECT" if frac >= 0.75 and (dlo > 0) == (dhi > 0) else "UNRESOLVED"
    pre = "FOOD-DEPENDENT" if food else "GAIT EFFECT" if frac >= 0.75 and (plo > 0) == (phi > 0) else "UNRESOLVED"
    return code, pre


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "docs/artifacts/RBT-97-p801-mechanism.txt"
    rows = {}
    for line in open(path):
        m = ROW.match(line)
        if m:
            g, s, a = int(m.group(1)), int(m.group(2)), int(m.group(3))
            rows.setdefault(a, []).append({"gen": g, "sign": s, "base": float(m.group(4)),
                                           "motif": float(m.group(5)), "phantom": float(m.group(6)),
                                           "anti": float(m.group(7))})
    rng = np.random.default_rng(5)
    L = [f"RBT-97 adversary round 2: pooled phantom table re-derived from {path}", ""]
    for a, rs in sorted(rows.items()):
        n = len(rs)
        md = [r["motif"] for r in rs]
        pd_ = [r["phantom"] for r in rs]
        ad = [r["anti"] for r in rs]
        diff = [x - y for x, y in zip(md, pd_)]
        frac = float(np.mean(pd_)) / float(np.mean(md))
        L.append(f"a = {a}, n = {n} robots: " + ", ".join(f"g{r['gen']}" for r in rs))
        for name, v in (("motif", md), ("phantom", pd_), ("antimotif", ad), ("motif-phantom", diff)):
            bm, blo, bhi = boot(v, rng)
            tm, tlo, thi = tint(v)
            L.append(f"   {name:14s} {bm:+7.3f}  boot [{blo:+7.3f}, {bhi:+7.3f}]  t(df {n - 1}) [{tlo:+7.3f}, {thi:+7.3f}]"
                     f"  improved {sum(x > 0 for x in v)}/{n}")
        L.append(f"   retention = mean(phantom)/mean(motif) = {100 * frac:+.1f}%")
        per = [100 * r["phantom"] / r["motif"] for r in rs]
        L.append("   per-robot retention: " + " ".join(f"g{r['gen']}:{p:+.1f}%" for r, p in zip(rs, per)))
        _, blo, bhi = boot(diff, rng)
        _, plo, phi = boot(pd_, rng)
        _, tlo, thi = tint(diff)
        _, tplo, tphi = tint(pd_)
        c, p = verdicts(frac, (blo, bhi), (plo, phi))
        _, pt = verdicts(frac, (tlo, thi), (tplo, tphi))
        L.append(f"   verdict: code-as-merged {c}; pre-registered rule (boot) {p}; pre-registered rule (t) {pt}")
        # the static-decoy cost: phantom's own delta, which a food-free circuit would put at the gait component
        L.append(f"   phantom's own delta {np.mean(pd_):+.3f}: t-interval [{tplo:+.3f}, {tphi:+.3f}]"
                 + ("  -- BELOW ZERO: the decoy condition costs items on its own" if tphi < 0 else ""))
        L.append("")
    sys.stdout.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
