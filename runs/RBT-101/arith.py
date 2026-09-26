"""RBT-101 (C4): arithmetic first (the coordinator's 19:35 lesson 3).  What does flat ground do to an UNCHANGED gait,
from quantities fixed before any C4 arm existed, and what of the observed income change is left over?

The only committed unchanged-gait measurement is the endpoint probe, runs/RBT-101/flat_probe.txt (pre-registered as
C4's prior, section 1): each seed's season-300 best of each fauna, ALONE in the arena, 64 paired draws, flat minus
random, items eaten per 15 s bout.  Items per bout is the unit of mean_lifetime_score (one bout a season).  It is a
solo best, not the population at T in groups of four; it predicts the direction and rough size of an unchanged gait's
change, not the ecology's.  The residual is read against that caveat.

Per seed: predicted R-shift (probe) against observed R-shift (recovery window, shift - base, readout.py's own tables),
for each fauna and for the paired contrast (co-evolved - designed); the residual = observed - predicted.

    python runs/RBT-101/arith.py > runs/RBT-101/arith.txt
"""
import os
import re
import statistics
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-92"))
import readout as R  # noqa: E402

SEEDS = R.SEEDS
TS = R.onsets()
probe = {}
for line in open("runs/RBT-101/flat_probe.txt"):
    if line.startswith("#") or "\t" not in line:
        continue
    f = line.split("\t")
    probe[(int(f[0]), f[1])] = float(re.search(r"flat-random ([-+][0-9.]+)", line).group(1))


def rshift(s, k, a=60, b=160):
    base, shift = R.Arm(f"runs/RBT-90/forage-{s}"), R.Arm(f"runs/RBT-101/shift-{s}")
    T = TS[s]
    return statistics.fmean(shift.x[k][t] - base.x[k][t] for t in range(T + a, T + b))


def line(label, v):
    n, m, sd, hw = R.stat(v)
    return (f"{label:44s} mean {m:+.4f}  95% t({n - 1}) [{m - hw:+.4f}, {m + hw:+.4f}]  sd {sd:.4f}  positive {sum(x > 0 for x in v)}/{n}"
            f"   per seed [{', '.join(f'{x:+.3f}' for x in v)}]")


print(__doc__.split("\n\n")[0])
print(f"seeds (in order): {SEEDS}")
obs = {k: [rshift(s, k) for s in SEEDS] for k in R.KINDS}
pred = {k: [probe[(s, k)] for s in SEEDS] for k in R.KINDS}
for k, lab in (("holistic", "co-evolved"), ("conventional", "designed")):
    print(line(f"{lab}: predicted R-shift (solo probe)", pred[k]))
    print(line(f"{lab}: observed R-shift (recovery)", obs[k]))
    print(line(f"{lab}: residual (observed - predicted)", [o - p for o, p in zip(obs[k], pred[k])]))
    print(f"{lab}: observed / predicted, ratio of means: {statistics.fmean(obs[k]) / statistics.fmean(pred[k]):.2f}")
pp = [a - b for a, b in zip(pred["holistic"], pred["conventional"])]
po = [a - b for a, b in zip(obs["holistic"], obs["conventional"])]
print(line("paired (co-evolved - designed): predicted", pp))
print(line("paired (co-evolved - designed): observed", po))
print(line("paired: residual (observed - predicted)", [o - p for o, p in zip(po, pp)]))
r = statistics.correlation(pp, po)
print(f"paired: per-seed correlation of predicted with observed r = {r:+.3f} (n = 10)")
