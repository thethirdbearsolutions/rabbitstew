"""RBT-97 adversary: can the pre-registered phantom verdict band (retention < 25% food-dependent,
>= 75% gait effect, else unresolved) be resolved at 7 robots x 64 seeds on P-801?

No simulation.  The noise model is RBT-67's committed per-seed differences on P-801
(docs/artifacts/RBT-67/p801.json, seeds 7000..7063): for each correctly signed robot and rung, the
motif arm's 64 per-seed differences are taken as observed, and a phantom arm is synthesised as

    phantom_diff[seed] = R * motif_mean(robot) + noise[seed],  noise ~ resampled centred motif diffs

i.e. with the SAME per-seed spread as the motif arm (an assumption, stated: the phantom arm's
spread is unmeasured; RBT-67's W4b phantom-384 row had a spread of the same order).  Retention is
the pooled ratio sum(phantom diffs) / sum(motif diffs), its 95% CI a percentile bootstrap over
robots (the author's stated error term), 2,000 synthetic experiments per true R.

Reported per rung: the median CI half-width on R, and P(verdict) for each true R under the
pre-registered rule, on (a) the five correctly signed P-801 robots RBT-67 measured and (b) seven,
with g100/g400 given their RBT-69 per-robot gains at a = 64 (+3.734, +1.109; published sign,
docs/runs/RBT-69-travel-direction.txt) as if re-signed -- only at a = 64, the one rung they exist.

Usage: python runs/RBT-97/adversary_band.py
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)
import numpy as np

CORRECT = (0, 200, 300, 500, 590)
EXTRA_64 = {100: 3.734, 400: 1.109}
RS = (0.0, 0.10, 0.25, 0.50, 0.75, 1.0)
N_EXP, N_BOOT = 2000, 400


def experiment(rng, motif, R):
    """One synthetic arm: returns (retention estimate, CI lo, CI hi)."""
    ph = []
    for d in motif:
        noise = rng.choice(d - d.mean(), len(d), replace=True)
        ph.append(R * d.mean() + noise)
    msum = np.array([d.sum() for d in motif])
    psum = np.array([p.sum() for p in ph])
    est = psum.sum() / msum.sum()
    k = len(motif)
    boots = []
    for _ in range(N_BOOT):
        i = rng.integers(0, k, k)
        den = msum[i].sum()
        if den != 0:
            boots.append(psum[i].sum() / den)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return est, lo, hi


def verdict(est, lo, hi):
    # pre-registered: food-dependent if retention < 25% (and motif - phantom excludes 0, which it does
    # whenever retention is well below 1 here); gait if >= 75% with phantom's own CI excluding zero;
    # the band is read on the point estimate as posted, and ALSO on the CI (the stricter reading).
    return ("food" if est < 0.25 else "gait" if est >= 0.75 else "unres",
            "food" if hi < 0.25 else "gait" if lo >= 0.75 else "unres")


def main():
    d = json.load(open("docs/artifacts/RBT-67/p801.json"))
    rng = np.random.default_rng(97)
    L = ["RBT-97 adversary: resolvability of the phantom retention band at 7 x 64 on P-801 (synthetic, RBT-67 noise)", ""]
    for c in d["cells"]:
        a = c["a"]
        if a not in (64.0, 384.0):
            continue
        sets = {"5 correct robots": [np.asarray(r["diffs"], float) for r in c["robots"] if r["gen"] in CORRECT]}
        if a == 64.0:
            sd = np.mean([x.std(ddof=1) for x in sets["5 correct robots"]])
            extra = [np.asarray(sets["5 correct robots"][0] - sets["5 correct robots"][0].mean() + m) for m in EXTRA_64.values()]
            sets["7 robots (g100/g400 at RBT-69 gains)"] = sets["5 correct robots"] + extra
        for name, motif in sets.items():
            means = [x.mean() for x in motif]
            L.append(f"a = {a:.0f}, {name}: motif means " + " ".join(f"{m:+.2f}" for m in means) +
                     f", per-seed sd {np.mean([x.std(ddof=1) for x in motif]):.2f}")
            L.append(f"   {'true R':>6s} {'median half-width':>17s} | point-estimate rule: food / unres / gait | CI rule: food / unres / gait")
            for R in RS:
                res = [experiment(rng, motif, R) for _ in range(N_EXP)]
                hw = np.median([(h - l) / 2 for _, l, h in res])
                v1 = [verdict(*x)[0] for x in res]
                v2 = [verdict(*x)[1] for x in res]
                f = lambda v, k: sum(x == k for x in v) / len(v)
                L.append(f"   {R:6.2f} {hw:17.3f} | {f(v1, 'food'):5.2f} {f(v1, 'unres'):5.2f} {f(v1, 'gait'):5.2f}"
                         f"            | {f(v2, 'food'):5.2f} {f(v2, 'unres'):5.2f} {f(v2, 'gait'):5.2f}")
            L.append("")
    sys.stdout.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
