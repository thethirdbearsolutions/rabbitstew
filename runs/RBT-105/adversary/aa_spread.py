"""RBT-105 design adversary, proposal F4: the ecology's founder-sharing A/A spread, REPORT ONLY.

RBT-105's replicate arms (same founders, same worlds, same designed-body fauna, another holistic stream)
are an A/A for the holistic fauna. This prints the replicate spread of the quantities RBT-92's instrument
reads from seasons.txt, over RBT-92's windows at each seed's committed onset T (runs/RBT-92/onset.txt):
    before [T-100, T)   recovery [T+60, T+160) (RBT-92's primary)   late [300, 600)
  x_h     holistic mean_lifetime_score, window mean (the income RBT-92's R-body and R-shift read)
  body    holistic - conventional mean_lifetime_score (R-body)
  alive_h holistic alive, window mean (survival)
  deaths_h holistic deaths per 10 seasons, window mean
and, per quantity and window, RMS of (replicate - original) over every replicate arm, and the t(n-1)
half-width 2.776 * RMS / 2 RBT-96 used for the arena, so the challenge verdicts (RBT-92/99/100/101) can be
read against it. It rules on nothing. Conventional quantities are omitted: the designed-body fauna is
byte-identical across replicates by construction, so its A/A spread here is 0 and says nothing.

Caveat printed with it: these replicates diverge from season 0; a challenge arm shares its baseline up to
T and diverges after. For windows long after T the two nulls should approach each other; for the recovery
window this is an upper bound on the challenge arms' own A/A spread, not an estimate of it.

    python runs/RBT-105/adversary/aa_spread.py [ARMS_DIR]  > runs/RBT-105/aa_spread.txt
"""
import csv
import math
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
ARMS = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "runs" / "RBT-105"
DESIGN = {7: (1, 2), 805: (1, 2), 4: (1, 2), 807: (1, 2), 806: (1, 2), 2: (1, 2), 1: (1, 2), 804: (1, 2)}


def onsets():
    out = {}
    for line in open(ROOT / "runs" / "RBT-92" / "onset.txt"):
        f = line.split("\t")
        if f[0].isdigit() and f[1].isdigit():
            out[int(f[0])] = int(f[1])
    return out


def table(path):
    x = {}
    for r in csv.DictReader(open(path / "seasons.txt"), delimiter="\t"):
        x[(int(r["season"]), r["population"])] = r
    return x


def q(t, name, lo, hi):
    vals = []
    for s in range(lo, hi):
        h, c = t.get((s, "holistic")), t.get((s, "conventional"))
        alive = int(h["alive"]) if h else 0
        xh = float(h["mean_lifetime_score"]) if h and alive else 0.0  # a dead fauna earns 0 (RBT-92's rule)
        vals.append({"x_h": xh, "body": xh - float(c["mean_lifetime_score"]), "alive_h": alive, "deaths_h": 10 * (int(h["deaths"]) if h else 0)}[name])
    return sum(vals) / len(vals)


T = onsets()
QS = ("x_h", "body", "alive_h", "deaths_h")
diffs = {}
print("seed K  window    " + " ".join(f"{n:>9s}" for n in QS))
for seed, ks in DESIGN.items():
    arms = [(0, ROOT / "runs" / "RBT-90" / f"forage-{seed}")] + [(k, ARMS / f"forage-{seed}-b{k}") for k in ks]
    arms = [(k, p) for k, p in arms if (p / "seasons.txt").exists()]
    if len(arms) < 2 or seed not in T:
        continue
    wins = {"before": (T[seed] - 100, T[seed]), "recovery": (T[seed] + 60, T[seed] + 160), "late": (300, 600)}
    base = table(arms[0][1])
    for k, p in arms:
        t = table(p)
        for w, (lo, hi) in wins.items():
            v = [q(t, n, lo, hi) for n in QS]
            print(f"{seed:4d} {k:1d}  {w:9s} " + " ".join(f"{x:9.3f}" for x in v))
            if k:
                for n, x in zip(QS, v):
                    diffs.setdefault((w, n), []).append(x - q(base, n, lo, hi))
print("\nreplicate - original, over every replicate arm (REPORT ONLY; see the caveat in the docstring)")
print("window    quantity    n      RMS   2.776*RMS/2")
for (w, n), d in sorted(diffs.items()):
    rms = math.sqrt(sum(x * x for x in d) / len(d))
    print(f"{w:9s} {n:9s} {len(d):3d} {rms:8.3f} {2.776 * rms / 2:10.3f}")
