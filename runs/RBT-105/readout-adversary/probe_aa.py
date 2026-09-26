"""RBT-105 readout adversary: what the 0.132 A/A is, from committed seasons.txt only.

  A1  reproduction of aa_spread.txt's recovery 'body' RMS, and the check that the designed side is identical
      season by season in all 16 replicates (so rep - orig of R-body == rep - orig of holistic income)
  A2  the spread as a function of time since the histories diverged: RMS(rep - orig) of holistic income over
      100-season windows starting s seasons after season 0. A challenge arm's recovery window is [T+60, T+160),
      i.e. 60-160 seasons after ITS divergence; RBT-105's own [60, 160) is the time-matched analogue.
  A3  what a challenge 'A/A-like' contrast contains that this one does not: both faunas move (a cull draws on
      both), and the event's own mean. Printed from the committed cull contrasts for comparison, not re-derived.
  A4  the SE arithmetic the report prints, and the ratio claims.

    python runs/RBT-105/readout-adversary/probe_aa.py > runs/RBT-105/readout-adversary/probe_aa.txt
"""
import csv
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent
ROOT = RUN.parent.parent
DESIGN = {7: (1, 2), 805: (1, 2), 4: (1, 2), 807: (1, 2), 806: (1, 2), 2: (1, 2), 1: (1, 2), 804: (1, 2)}
T = {}
for line in open(ROOT / "runs" / "RBT-92" / "onset.txt"):
    f = line.split("\t")
    if f[0].isdigit() and f[1].isdigit():
        T[int(f[0])] = int(f[1])


def table(p):
    h, c = {}, {}
    for r in csv.DictReader(open(p / "seasons.txt"), delimiter="\t"):
        (h if r["population"] == "holistic" else c)[int(r["season"])] = r
    return h, c


def wmean(t, lo, hi):
    return sum(float(t[s]["mean_lifetime_score"]) for s in range(lo, hi)) / (hi - lo)


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


orig = {s: table(ROOT / "runs" / "RBT-90" / f"forage-{s}") for s in DESIGN}
reps = {(s, k): table(RUN / f"forage-{s}-b{k}") for s, ks in DESIGN.items() for k in ks}

print("RBT-105 readout adversary, probe_aa.py\n")
same = sum(1 for (s, k), (h, c) in reps.items() if all(c[i] == orig[s][1][i] for i in range(600)))
d_body, d_h = [], []
for (s, k), (h, c) in reps.items():
    lo, hi = T[s] + 60, T[s] + 160
    body = wmean(h, lo, hi) - wmean(c, lo, hi)
    body0 = wmean(orig[s][0], lo, hi) - wmean(orig[s][1], lo, hi)
    d_body.append(body - body0)
    d_h.append(wmean(h, lo, hi) - wmean(orig[s][0], lo, hi))
print(f"A1  designed-body rows identical to the original in all 600 seasons: {same} of 16 replicates")
print(f"    recovery [T+60, T+160): RMS(rep - orig) of R-body = {rms(d_body):.4f}; of holistic income alone = {rms(d_h):.4f}; max |difference| = "
      f"{max(abs(a - b) for a, b in zip(d_body, d_h)):.2e}")
print("    so 'paired equals holistic' holds exactly here: the paired contrast has NO designed-side term to contribute.\n")

print("A2  RMS(rep - orig) of holistic income over [s, s+100), by seasons s since the histories diverged (season 0)")
print("    (seeds' recovery windows sit at s = T+60 = 412-442; a challenge arm's recovery window is at s = 60 after ITS divergence)")
for s in (0, 20, 40, 60, 100, 150, 200, 250, 300, 350, 400, 450, 500):
    v = [wmean(h, s, s + 100) - wmean(orig[sd][0], s, s + 100) for (sd, k), (h, c) in reps.items()]
    mean = sum(v) / len(v)
    print(f"    [{s:3d}, {s + 100:3d}): RMS {rms(v):.3f}  mean {mean:+.3f}" + ("   <- time-matched analogue of a challenge arm's recovery window" if s == 60 else ""))
v = [wmean(h, T[sd] + 60, T[sd] + 160) - wmean(orig[sd][0], T[sd] + 60, T[sd] + 160) for (sd, k), (h, c) in reps.items()]
print(f"    at each seed's own [T+60, T+160) (the report's figure): RMS {rms(v):.3f}")
per = {sd: sum(wmean(reps[(sd, k)][0], 60, 160) - wmean(orig[sd][0], 60, 160) for k in (1, 2)) / 2 for sd in DESIGN}
neg = sum(1 for x in per.values() if x < 0)
print(f"    POST HOC: the early offset. Mean over b1, b2 of rep - orig on [60, 160), per seed: " + " ".join(f"{sd}:{x:+.3f}" for sd, x in per.items()))
print(f"    negative on {neg} of 8 founding populations; two-sided sign test p = {2 * sum(math.comb(8, i) for i in range(neg, 9)) / 256:.3f}."
      " The RMS includes this offset; it is not a spread about 0.\n")

print("A3  one lifetime-mean axis, one history: the per-seed rep - orig values at [T+60, T+160) and at [60, 160)")
for (sd, k), (h, c) in reps.items():
    a = wmean(h, T[sd] + 60, T[sd] + 160) - wmean(orig[sd][0], T[sd] + 60, T[sd] + 160)
    b = wmean(h, 60, 160) - wmean(orig[sd][0], 60, 160)
    print(f"    {sd:4d}-b{k}: recovery {a:+.3f}   [60,160) {b:+.3f}")
print()
print("A4  arithmetic: 0.132/sqrt(10) = %.4f; C3 paired +0.138 / that = %.2f SE; residual +0.017 -> %.2f SE; C4 -0.458 -> %.1f SE"
      % (0.132 / math.sqrt(10), 0.138 / (0.132 / math.sqrt(10)), 0.017 / (0.132 / math.sqrt(10)), 0.458 / (0.132 / math.sqrt(10))))
print("    ratios: 0.132 / 0.071 = %.2f, / 0.091 = %.2f, / 0.108 = %.2f, / 0.1232 = %.2f" % (0.132 / 0.071, 0.132 / 0.091, 0.132 / 0.108, 0.132 / 0.1232))
print("    the cull 'A/A-like' contrasts are cull - base: they carry the cull's own mean (+0.033, +0.043; RBT-100 F7) and both faunas'")
print("    post-T history; RBT-105's rep - orig carries neither a treatment nor any designed-side history (A1).")
