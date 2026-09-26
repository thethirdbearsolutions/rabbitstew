"""RBT-101 readout adversary: the readout's inputs, the class's robustness, the null, an A/A-like spread, and the
scoring, from committed tables only, through RBT-92's readout.py (Arm, rbody, classify, stat) as readout.sh uses it.

    python runs/RBT-101/readout-adversary/probe_readout.py > runs/RBT-101/readout-adversary/probe_readout.txt

  P1  inputs: every arm directory, its config (seed, event season, flag), events.txt, table span; cull-k files
  P2  class C's robustness: leave one seed out; the window; one- and two-seed flips; a jitter illustration
  P3  the registered null: what it could absorb at the realised k, its matched-null power, and what -0.472 means
  P4  A/A-like spreads from the committed cull and cull20 contrasts, against -0.458 and the residuals
  P5  lessons 4-6 and the scoring
"""
import json
import math
import os
import random
import statistics as st
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-92"))
import readout as R  # noqa: E402

SEEDS, KINDS, TS = R.SEEDS, R.KINDS, R.onsets()
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}
K = {}
for s in SEEDS:
    for l in open(f"runs/RBT-101/cull-k-{s}.txt"):
        if l.startswith("cull\t"):
            K[s] = {p.split("=")[0]: int(p.split("=")[1]) for p in l.split("\t")[1].strip().split(",")}
K00 = [s for s in SEEDS if K[s] == {"holistic": 0, "conventional": 0}]


def path(arm, s):
    if arm == "cull" and s in K00:
        return f"runs/RBT-90/forage-{s}"
    return {"base": f"runs/RBT-90/forage-{s}", "shift": f"runs/RBT-101/shift-{s}", "cull": f"runs/RBT-101/cull-{s}",
            "cull20": f"runs/RBT-92/cull20-{s}"}[arm]


A = {(a, s): R.Arm(path(a, s)) for a in ("base", "shift", "cull", "cull20") for s in SEEDS}
W = {"transient": (0, 60), "recovery": (60, 160), "tail": (160, 200)}


def rb(arm, s, a, b):
    return R.rbody(A[(arm, s)], TS[s] + a, TS[s] + b)


def fx(arm, s, k, a, b):
    return st.fmean(A[(arm, s)].x[k][t] for t in range(TS[s] + a, TS[s] + b))


def line(label, v):
    n, m, sd, hw = R.stat(v)
    return f"{label}: {m:+.4f} [{m - hw:+.4f}, {m + hw:+.4f}] sd {sd:.4f} pos {sum(x > 0 for x in v)}/{n} neg {sum(x < 0 for x in v)}/{n}"


def cls(v):
    n, m, sd, hw = R.stat(v)
    return R.classify(n, m, hw, sum(x > 0 for x in v), sum(x < 0 for x in v), 0, 0, 0)[:2].strip(". ")


print(__doc__.split("\n\n")[0])
print()
print("P1 INPUTS")
for arm in ("shift", "cull"):
    for s in SEEDS:
        d = f"runs/RBT-101/{arm}-{s}"
        if not os.path.isdir(d):
            print(f"   {arm:5s} {s:>4}: no directory ({'k = 0/0, the null is the baseline' if arm == 'cull' and s in K00 else 'MISSING'})")
            continue
        c = json.load(open(f"{d}/config.json"))
        e = c["ecology"]
        ev = [l.rstrip("\n").split("\t") for l in open(f"{d}/events.txt")][1:]
        seasons = sorted({int(l.split("\t")[0]) for l in open(f"{d}/seasons.txt") if l[0].isdigit()})
        flag = f"shift {e['shift']} at {e['shift_at']}" if arm == "shift" else f"cull {e.get('cull')} at {e['cull_at']}"
        want = (e["shift"] == "terrain=flat" and e["shift_at"] == TS[s]) if arm == "shift" else (
            e["cull_at"] == TS[s] and e["cull"] == f"holistic={K[s]['holistic']},conventional={K[s]['conventional']}" and e["shift"] is None)
        evs = [(r[0], r[1], r[2], r[3]) for r in ev if r[0] in ("shift", "cull")]
        print(f"   {arm:5s} {s:>4}: config seed {c['seed']} {flag}  T {TS[s]}  {'OK' if want and c['seed'] == s else 'WRONG'};  "
              f"events {evs};  seasons {seasons[0]}..{seasons[-1]} ({len(seasons)})")
print(f"   k = 0/0 seeds {K00}; cull-k per seed " + ", ".join(f"{s}:{K[s]['holistic']}/{K[s]['conventional']}" for s in SEEDS))
print("   cull20 (RBT-92's, linked by readout.sh): " + ", ".join(
    f"{s}:{json.load(open(f'runs/RBT-92/cull20-{s}/config.json'))['ecology']['cull']}@{json.load(open(f'runs/RBT-92/cull20-{s}/config.json'))['ecology']['cull_at']}"
    + ("" if json.load(open(f'runs/RBT-92/cull20-{s}/config.json'))['ecology']['cull_at'] == TS[s] else " WRONG T") for s in SEEDS))

print()
print("P2 CLASS C's ROBUSTNESS (recovery window unless stated; the class rule is readout.py's classify with E1/D/E2 = 0, as readout.txt)")
rec = [rb("shift", s, 60, 160) for s in SEEDS]
print("   " + line("shift R-body, recovery (the verdict)", rec) + f"  -> {cls(rec)}")
print("   per seed: " + ", ".join(f"{s}:{v:+.3f}" for s, v in zip(SEEDS, rec)))
print("   (a) leave one seed out (n = 9, guard ceil(0.8 x 9) = 8, r = t(8) half-width):")
for i, s in enumerate(SEEDS):
    v = rec[:i] + rec[i + 1:]
    n, m, sd, hw = R.stat(v)
    print(f"       drop {s:>4}: mean {m:+.4f} r {hw:.4f} neg {sum(x < 0 for x in v)}/9 |m|/r {abs(m) / hw:.2f} -> {cls(v)}")
print("   (b) the window: a 100-season window starting at T + a, and the registered windows")
for a in (0, 20, 40, 50, 60, 70, 80, 100):
    v = [rb("shift", s, a, a + 100) for s in SEEDS]
    n, m, sd, hw = R.stat(v)
    print(f"       [T+{a:3d}, T+{a + 100:3d}): mean {m:+.4f} r {hw:.4f} neg {sum(x < 0 for x in v)}/10 -> {cls(v)}")
for wn, (a, b) in W.items():
    v = [rb("shift", s, a, b) for s in SEEDS]
    n, m, sd, hw = R.stat(v)
    print(f"       {wn:9s} [T+{a}, T+{b}): mean {m:+.4f} r {hw:.4f} neg {sum(x < 0 for x in v)}/10 -> {cls(v)}")
print("   (c) flips: the guard is 8/10 and 9 are negative, so ONE seed may turn positive and C still holds on the guard;")
print("       setting the k least-negative seeds to +|value| (the adversarial flip):")
order = sorted(range(10), key=lambda i: (rec[i] >= 0, -rec[i]))
for k in (1, 2):
    v = rec[:]
    for i in [j for j in order if rec[j] < 0][:k]:
        v[i] = abs(v[i])
    n, m, sd, hw = R.stat(v)
    print(f"       flip {k}: mean {m:+.4f} r {hw:.4f} neg {sum(x < 0 for x in v)}/10 -> {cls(v)}")
print("   (d) illustration, not a test (RBT-92 F6's method): each per-seed value jittered by N(0, s), 4000 draws; share of C")
rnd = random.Random(101)
for sj in (0.05, 0.077, 0.108, 0.15):
    out = {}
    for _ in range(4000):
        c = cls([x + rnd.gauss(0, sj) for x in rec])
        out[c] = out.get(c, 0) + 1
    print(f"       s = {sj:.3f}: " + "  ".join(f"{c}:{n / 4000:.3f}" for c, n in sorted(out.items())))
print("   (e) seeds within one A/A-like per-seed RMS of zero (0.108, P4): " + ", ".join(f"{s}:{v:+.3f}" for s, v in zip(SEEDS, rec) if abs(v) < 0.108))
print("   (f) the paired contrast by window (event - base R-body): " + "; ".join(
    f"{wn} {R.stat([rb('shift', s, a, b) - rb('base', s, a, b) for s in SEEDS])[1]:+.3f}" for wn, (a, b) in W.items()))

print()
print("P3 THE REGISTERED NULL (random cull of k = excess deaths in [T, T+10))")
exc = {}
for s in SEEDS:
    for l in open(f"runs/RBT-101/cull-k-{s}.txt"):
        f = l.split()
        if len(f) > 6 and f[1] == "deaths":
            exc[(s, f[0])] = int(f[7])
for k in KINDS:
    print(f"   {k:12s} excess deaths shift - base over [T, T+10), per seed: " + ", ".join(f"{s}:{exc[(s, k)]:+d}" for s in SEEDS)
          + f"   negative on {sum(exc[(s, k)] < 0 for s in SEEDS)}/10")
print("   k = max(0, excess): a boon lowers deaths, so the null is one-sided by construction and has nothing to match on "
      f"{len(K00)}/10 seeds.")
d_sb = [rb("shift", s, 60, 160) - rb("base", s, 60, 160) for s in SEEDS]
d_sc = [rb("shift", s, 60, 160) - rb("cull", s, 60, 160) for s in SEEDS]
d_cb = [rb("cull", s, 60, 160) - rb("base", s, 60, 160) for s in SEEDS]
print("   " + line("event - base (paired R-body)", d_sb))
print("   " + line("event - null (registered)", d_sc))
print("   " + line("null - base (what the null itself did to R-body)", d_cb))
kp = [s for s in SEEDS if s not in K00]
print("   " + line(f"null - base on the {len(kp)} seeds with a cull", [rb('cull', s, 60, 160) - rb('base', s, 60, 160) for s in kp]))
print(f"   identical seeds: event - null == event - base on {sum(abs(a - b) < 1e-12 for a, b in zip(d_sb, d_sc))}/10")
c20 = [rb("cull20", s, 60, 160) - rb("base", s, 60, 160) for s in SEEDS]
n, m20, sd20, hw20 = R.stat(c20)
rms20 = math.sqrt(st.fmean(x * x for x in c20))
kk = [K[s]["holistic"] + K[s]["conventional"] for s in SEEDS]
print(f"   scale: a cull of 20 + 20 moves paired R-body by mean {m20:+.4f}, per-seed RMS {rms20:.4f} (cull20 - base, recovery)")
print(f"   matched-null power, (i) absorption: at the realised k (total culled per seed {kk}, mean {st.fmean(kk):.1f} of the 40 in cull20),")
print(f"       a null scaled linearly from cull20 could move paired R-body by about {rms20 * st.fmean(kk) / 40:.4f} per seed RMS, "
      f"i.e. {100 * rms20 * st.fmean(kk) / 40 / abs(st.fmean(d_sb)):.1f}% of the -0.458 event; the observed null - base RMS is "
      f"{math.sqrt(st.fmean(x * x for x in d_cb)):.4f} ({100 * math.sqrt(st.fmean(x * x for x in d_cb)) / abs(st.fmean(d_sb)):.1f}%).")
n, m, sd, hw = R.stat(d_sc)
mde = (2.262 + 0.883) * sd / math.sqrt(10)
print(f"   matched-null power, (ii) sensitivity: the event - null contrast has sd {sd:.4f}, half-width {hw:.4f}; its minimum detectable")
print(f"       effect (two-sided 5%, power 0.8, t(9)) is {mde:.4f}; the observed -0.472 is {abs(m) / mde:.1f}x that. The null test cannot fail")
print(f"       to separate an effect of this size from a null that is the baseline itself on {len(K00)}/10 seeds: it is a re-read of")
print(f"       event - base (correlation of the two per-seed vectors {st.correlation(d_sb, d_sc):+.3f}), not an independent test of turnover.")
print("   the turnover reference that does carry a turnover: cull20 - base paired R-body " + line("", c20)[2:])

print()
print("P4 A/A-LIKE SPREADS (committed contrasts of an intervention with ~0 expected effect on the paired level)")
aa_c20_pair = c20
aa_cull_pair = [rb("cull", s, 60, 160) - rb("base", s, 60, 160) for s in kp]
aa_c20_f = [fx("cull20", s, k, 60, 160) - fx("base", s, k, 60, 160) for s in SEEDS for k in KINDS]
aa_cull_f = [fx("cull", s, k, 60, 160) - fx("base", s, k, 60, 160) for s in kp for k in KINDS if K[s][k] > 0]
rms = lambda v: math.sqrt(st.fmean(x * x for x in v))
print(f"   paired R-body, cull20 - base (10 seeds): RMS {rms(aa_c20_pair):.4f}, sd {st.stdev(aa_c20_pair):.4f}")
print(f"   paired R-body, cull - base (the {len(kp)} seeds with k > 0): RMS {rms(aa_cull_pair):.4f}  per seed [{', '.join(f'{x:+.3f}' for x in aa_cull_pair)}]")
print(f"   per fauna, cull20 - base (20 values): RMS {rms(aa_c20_f):.4f}  <- placebo.py's 0.0768 (per fauna, not paired)")
print(f"   per fauna, the culled fauna of the k > 0 culls ({len(aa_cull_f)} values): RMS {rms(aa_cull_f):.4f}")
aa = max(rms(aa_c20_pair), rms(aa_cull_pair))
print(f"   taking the paired A/A-like per-seed RMS as {aa:.3f} (the larger):")
print(f"     a 10-seed mean of A/A differences has SE {aa / math.sqrt(10):.4f}; |-0.458| is {0.458 / (aa / math.sqrt(10)):.0f} SE, and -0.458 is"
      f" {0.458 / aa:.1f}x a SINGLE seed's A/A RMS; per seed the smallest event - base value is {max(d_sb):+.3f} ({abs(max(d_sb)) / aa:.1f}x)")
print(f"     so the paired event contrast needs no A/A condition. For RBT-105's aa_spread.txt to reach it, its per-seed RMS would have to be")
print(f"     about {0.458 * math.sqrt(10) / 2.262 / 1.0:.2f} or more on the PAIRED contrast (the t(9) interval's own sd would be ~that); the")
print(f"     observed between-seed sd {st.stdev(d_sb):.3f} already contains the run-to-run noise (RBT-92 F5).")
print(f"     the designer's residual -0.133 is {0.133 / aa:.1f}x a single seed's A/A RMS and {0.133 / (aa / math.sqrt(10)):.1f} SE: it is not 'far inside' any")
print(f"     A/A spread; its interval (+-0.35) is set by the probe's per-seed misfit (sd 0.49), not by A/A noise.")
print(f"     the sign-guard seed 2 (R-body -0.104) is {0.104 / aa:.2f}x the paired A/A RMS (the report's 1.4x divides by the per-fauna 0.077).")

print()
print("P5 LESSONS 4-6 AND SCORING")
mins = {}
for arm in ("base", "shift", "cull", "cull20"):
    for s in SEEDS:
        for k in KINDS:
            mins[(arm, s, k)] = min(A[(arm, s)].alive[k][t] for t in range(TS[s] - 100, TS[s] + 200))
print(f"   alive over [T-100, T+200), every arm, seed and fauna: min {min(mins.values())}, max "
      f"{max(max(A[(a, s)].alive[k][t] for t in range(TS[s] - 100, TS[s] + 200)) for a in ('base', 'shift', 'cull', 'cull20') for s in SEEDS for k in KINDS)}")
inc = min(fx(a, s, k, 0, 60) for a in ("shift",) for s in SEEDS for k in KINDS)
print(f"   min window income, shift arm, transient: {inc:.3f} against D/E's 0.25")
BR = [("designed R-shift > 0 on >= 8/10", 0.7, True, "informative"),
      ("designed R-shift > co-evolved", 0.75, True, "informative"),
      ("'holds up'", 0.85, True, "informative (co-evolved gained)"),
      ("k = 0/0 on >= 6/10", 0.55, True, "informative"),
      ("designed recovery 'none' on >= 5/10", 0.5, True, "LESSON 4: the paired rule is sign-blind; a boon cannot re-enter"),
      ("co-evolved recovery <= 60 on >= 6/10", 0.5, True, "LESSON 4: 4 of the 6 are the d = 0 artifact"),
      ("re-wiring holistic NO CHANGE SEEN", 0.85, True, "informative at f >= 0.5 only"),
      ("re-wiring designed NO CHANGE SEEN", 0.65, True, "informative at f >= 0.2 only")]
b8 = st.fmean((1 - p) ** 2 for _, p, ok, _ in BR)
b6 = st.fmean((1 - p) ** 2 for name, p, ok, why in BR if not why.startswith("LESSON"))
print(f"   Brier over the report's 8 binary predictions: {b8:.4f} (report: 0.128); without the two recovery rows (lesson 4): {b6:.4f}")
for name, p, ok, why in BR:
    print(f"       {name:40s} p {p:.2f} outcome {'yes' if ok else 'no'}  {why}")
cp = {"B": 0.35, "C": 0.30, "F": 0.25, "A": 0.05, "D": 0.02, "E1": 0.02, "E2": 0.01}
mb = sum((p - (1.0 if c == "C" else 0.0)) ** 2 for c, p in cp.items())
print(f"   the class prediction (Amendment 2): multi-class Brier {mb:.3f} (uniform over 7 classes: {sum((1 / 7 - (1.0 if c == 'C' else 0.0)) ** 2 for c in cp):.3f});"
      f" log score ln(0.30) = {math.log(0.30):.3f}")
