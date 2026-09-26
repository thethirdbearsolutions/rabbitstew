"""RBT-105: POST HOC companions to the pre-registered readout (readout.txt).  Nothing here changes a verdict.

Every line is labelled post hoc.  It applies the programme's instrument lessons (docs/paper-9-net-of-arithmetic.md
section 6) to this readout, reading committed files only, except H2, which is a simulation under the design
adversary's own model (adversary/power.py, imported unchanged).

  H1  the R1 verdict's margin: which flips sit exactly on a bar, and the verdict if they were undecided (the
      "jitter the sign guard" rule)
  H2  matched-null power: P(each R1 verdict), P(R2) and P(R1 SUBSTANTIAL HISTORY and R2 both) by icc at n = 16,
      so the absent FOUNDERS DOMINANT verdict carries its power and the observed pair of verdicts an icc range
  H3  the continuous quantity: the replicates' late (300-599) birth-level rates against the originals' gap
  H4  replicate against replicate: do the two replicate streams of one founding population agree?
  H5  which founder line won, against whether the fate flipped (RBT-90 F4's observation, on replicates)
  H6  the ecology A/A on the PAIRED R-body scale (lesson: judge a paired contrast on the paired A/A scale),
      against C3's 0.091 (0.071-0.108) and C4's 0.108-0.123

    python runs/RBT-105/readout_posthoc.py > runs/RBT-105/readout_posthoc.txt
"""
import csv
import importlib.util
import itertools
import math
import pathlib
import statistics as st
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
spec = importlib.util.spec_from_file_location("ro", HERE / "readout.py")
ro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ro)
RBT90 = ROOT / "runs" / "RBT-90"
SIMS = 2000


def fates():
    rows = []
    for seed, ks in ro.DESIGN.items():
        d0, f0 = ro.fate_of(RBT90 / f"forage-{seed}" / "oscillator.txt")
        for k in ks:
            d, f = ro.fate_of(ro.arm_dir(seed, k) / "oscillator.txt")
            _, rate = ro.late_y(ro.arm_dir(seed, k))
            rows.append(dict(seed=seed, k=k, d0=d0, f0=f0, d=d, f=f, rate=rate))
    return rows


def orig_rates():
    out, cur = {}, None
    for line in open(HERE / "osc-births-rbt90.txt"):
        if line.startswith("forage-"):
            cur = int(line.split()[0].split("-")[1])
        elif line.startswith("{") and cur is not None:
            d = eval(line)  # noqa: S307 (our own JSON line)
            out[cur] = d["late_k"] / d["late_n"]
    return out


R = fates()
print("RBT-105 readout, POST HOC companions (readout_posthoc.py). No line here changes a pre-registered verdict.\n")

# ---------------------------------------------------------------- H1
print("H1  POST HOC. The R1 verdict's margin (the sign-guard lesson: a count met with little margin is fragile)")
flips = [r for r in R if r["f"] in ro.OPPOSITE and r["f"] == ro.OPPOSITE.get(r["f0"])]
dec = [r for r in R if r["f"] in ro.OPPOSITE]
F, n = len(flips), len(dec)
print(f"  F = {F} flips in n = {n} decided replicates: " + ", ".join(f"{r['seed']}-b{r['k']} ({r['f0'][0].upper()}->{r['f'][0].upper()}, distinct {r['d']})" for r in flips))
onbar = [r for r in flips if r["d"] in (ro.OSC_DISCARD, ro.OSC_ACQUIRE)]
print(f"  flips whose count sits exactly on a bar ({ro.OSC_DISCARD} or {ro.OSC_ACQUIRE}): {[str(r['seed']) + '-b' + str(r['k']) for r in onbar]}")
for drop in range(len(onbar) + 1):
    print(f"    if {drop} of them were undecided instead: F = {F - drop}, n = {n - drop} -> {ro.r1(F - drop, n - drop).split(':')[0]}")
print(f"  SUBSTANTIAL HISTORY needs P(Bin(n, 0.1) >= F) <= 0.05: at n = {n} that is F >= "
      f"{min(f for f in range(n + 1) if 1 - ro.binom_cdf(f - 1, n, 0.1) <= 0.05)}; the verdict has a margin of "
      f"{F - min(f for f in range(n + 1) if 1 - ro.binom_cdf(f - 1, n, 0.1) <= 0.05)} flip(s)")
undec = [f"{r['seed']}-b{r['k']} ({r['d']})" for r in R if r["f"] not in ro.OPPOSITE]
print(f"  undecided replicates (3-7): {undec}; had both gone to the original's fate, F = {F}, n = {n + len(undec)} -> {ro.r1(F, n + len(undec)).split(':')[0]}; "
      f"had both flipped, F = {F + len(undec)}, n = {n + len(undec)} -> {ro.r1(F + len(undec), n + len(undec)).split(':')[0]}")
print()

# ---------------------------------------------------------------- H2
print("H2  POST HOC. Matched-null power at the design's n = 16 (the adversary's power.py model, imported unchanged;")
print(f"    {SIMS} simulations per cell).  Its R2 is on log(distinct + 0.5), a stand-in for the registered late rate.")
src = (HERE / "adversary" / "power.py").read_text()
head = src[: src.index('print(f"# calibration')]
pw = {}
exec(compile(head, "power.py", "exec"), pw)  # noqa: S102 (the adversary's committed script, its definitions only)
pw["rng"] = np.random.default_rng(10505)
perms = pw["perm_table"](16)
print(f"  {'model':>9s} {'icc':>5s} | {'R1 FOUNDERS DOM':>15s} {'R1 SUBST HIST':>13s} {'R1 ND':>6s} | {'R2 p<=.05':>9s} | {'SUBST and R2':>12s}")
for model in ("two-state", "lognormal"):
    for icc in (0.0, 0.3, 0.4, 0.5, 0.6, 0.7, 0.9, 1.0 - 1e-9):
        pw["rng"] = np.random.default_rng(int(1000 * icc) + (0 if model == "two-state" else 7))
        out = [pw["one"](model, icc, 4, 2, perms) for _ in range(SIMS)]
        r1 = [o[1] for o in out]
        r2 = [o[2] <= 0.05 for o in out]
        both = sum(a == "SUBST" and b for a, b in zip(r1, r2)) / SIMS
        print(f"  {model:>9s} {icc:5.2f} | {r1.count('SHIFT') / SIMS:15.3f} {r1.count('SUBST') / SIMS:13.3f} {r1.count('ND') / SIMS:6.3f} | {np.mean(r2):9.3f} | {both:12.3f}", flush=True)
print("  Read: FOUNDERS DOMINANT was not returned; the rows give its power (e.g. icc 0.7 and above) as the matched null for")
print("  that absence.  The observed pair (SUBSTANTIAL HISTORY and R2 both) is most probable where the last column peaks.\n")

# ---------------------------------------------------------------- H3
print("H3  POST HOC. The continuous quantity: late (300-599) birth-level linked-oscillator rate (osc_births.txt)")
o = orig_rates()
od = [o[s] for s in ro.DESIGN if RBT90.joinpath(f"forage-{s}").exists() and ro.fate_of(RBT90 / f"forage-{s}" / "oscillator.txt")[1] == "discarded"]
oa = [o[s] for s in ro.DESIGN if ro.fate_of(RBT90 / f"forage-{s}" / "oscillator.txt")[1] == "acquired"]
lo, hi = max(od), min(oa)
print(f"  originals of the 8 design seeds: discarded {min(od):.3f}-{max(od):.3f}, acquired {min(oa):.3f}-{max(oa):.3f}: a gap ({lo:.3f}, {hi:.3f})")
for r in R:
    band = "D-like" if r["rate"] <= lo else "A-like" if r["rate"] >= hi else "IN THE GAP"
    print(f"    {r['seed']:4d}-b{r['k']}  original {r['f0']:>9s} ({o[r['seed']]:.3f})  replicate {r['f']:>9s} distinct {r['d']:2d}  late rate {r['rate']:.3f}  {band}")
gap = [r for r in R if lo < r["rate"] < hi]
print(f"  replicates inside the originals' gap: {len(gap)} of {len(R)}. The originals' clean separation is not reproduced by the")
print(f"  replicates; count and rate disagree where a replicate's distinct and its late rate point to different fates.\n")

# ---------------------------------------------------------------- H4
print("H4  POST HOC. Replicate against replicate (b1 against b2 of one founding population; the originals were selected on")
print("    outcome, the replicates were not)")
agree = tot = 0
for seed in ro.DESIGN:
    a, b = [r for r in R if r["seed"] == seed]
    same = a["f"] == b["f"] if a["f"] in ro.OPPOSITE and b["f"] in ro.OPPOSITE else None
    tot += same is not None
    agree += bool(same)
    print(f"    {seed:4d}: original {R[[r['seed'] for r in R].index(seed)]['f0']:>9s}; b1 {a['f']:>9s}, b2 {b['f']:>9s} -> " + ({True: "agree", False: "disagree", None: "not both decided"}[same]))
p = sum(math.comb(tot, i) for i in range(agree, tot + 1)) / 2 ** tot
print(f"  b1 and b2 agree on {agree} of {tot} seeds with both decided; replicate and original agree on {n - F} of {n} decided replicates.")
print(f"  Under pure history with a base rate of 1/2, P(>= {agree} of {tot} pairs agree) = {p:.3f} (illustration, not a test).\n")

# ---------------------------------------------------------------- H5
print("H5  POST HOC. Which founder line won (the living at season 599 traced by first parent; readout.txt), against the fate")
top = lambda w: w.split()[0] if w and w != "--" else None
rows5 = []
for r in R:
    w0 = top(ro.winners(RBT90 / f"forage-{r['seed']}"))
    w = top(ro.winners(ro.arm_dir(r["seed"], r["k"])))
    flipped = r in flips
    rows5.append((flipped, w == w0, r))
    print(f"    {r['seed']:4d}-b{r['k']}: top line {w:6s} (original {w0:6s}) {'same' if w == w0 else 'CHANGED':7s} fate {'FLIPPED' if flipped else ('undecided' if r['f'] not in ro.OPPOSITE else 'kept')}")
same_top = sum(s for _, s, _ in rows5)
print(f"  the original's top line wins again on {same_top} of {len(R)} replicates (prediction: fewer than half, 0.60)")
print(f"  every flip changed the top line: {all(not s for f, s, _ in rows5 if f)} ({sum(1 for f, s, _ in rows5 if f and not s)}/{F}); "
      f"kept fates with a changed top line: {sum(1 for f, s, r in rows5 if not f and not s and r['f'] in ro.OPPOSITE)} of {n - F}\n")

# ---------------------------------------------------------------- H6
print("H6  POST HOC. The ecology A/A on the PAIRED R-body scale (paper 9 section 6: judge a paired contrast on the paired scale)")
print("  In these replicates the designed-body fauna is byte-identical to the original (pairing.txt), so the paired contrast")
print("  (rep - orig)_holistic - (rep - orig)_designed IS the holistic difference: aa_spread.txt's 'body' row is on the paired scale.")
TS = {}
for line in open(ROOT / "runs" / "RBT-92" / "onset.txt"):
    f = line.split("\t")
    if f[0].isdigit() and f[1].isdigit():
        TS[int(f[0])] = int(f[1])


def x(path):
    t = {}
    for r in csv.DictReader(open(path / "seasons.txt"), delimiter="\t"):
        t[(int(r["season"]), r["population"])] = r
    return t


def rb(t, lo, hi):
    v = []
    for s in range(lo, hi):
        h, c = t.get((s, "holistic")), t.get((s, "conventional"))
        xh = float(h["mean_lifetime_score"]) if h and int(h["alive"]) else 0.0
        v.append(xh - float(c["mean_lifetime_score"]))
    return st.fmean(v)


for wname, (a, b) in (("recovery [T+60, T+160)", (60, 160)), ("before [T-100, T)", (-100, 0)), ("late [300, 600)", (None, None))):
    ro_d, rr_d = [], []
    for seed in ro.DESIGN:
        lo_, hi_ = (TS[seed] + a, TS[seed] + b) if b is not None and a is not None else (300, 600)
        base = rb(x(RBT90 / f"forage-{seed}"), lo_, hi_)
        reps = [rb(x(ro.arm_dir(seed, k)), lo_, hi_) for k in (1, 2)]
        ro_d += [v - base for v in reps]
        rr_d.append(reps[0] - reps[1])
    rms = math.sqrt(st.fmean(v * v for v in ro_d))
    rms_rr = math.sqrt(st.fmean(v * v for v in rr_d))
    print(f"  {wname:24s} rep - orig: RMS {rms:.3f} (n = {len(ro_d)}, mean {st.fmean(ro_d):+.3f}); b1 - b2: RMS {rms_rr:.3f} (n = {len(rr_d)}); "
          f"SE of a 10-seed mean {rms / math.sqrt(10):.3f}")
print("  the paired A/A-like scale the challenge readouts used: C3 cull - base 0.071, cull20 - base 0.108, pooled 0.091")
print("  (runs/RBT-100/readout-adversary/READOUT-ADVERSARY.md F7); C4 0.108-0.123 (runs/RBT-101/readout-adversary/probe_readout.txt P4).")
print("  Caveats: these replicates diverge from season 0, a challenge arm only from T (so for the recovery window this is an")
print("  upper bound in time); but here the designed side contributes 0 by construction, where a cull A/A moves both faunas.")
print("  alive_h has RMS 0.000 in every window: alive = 60 is the ecology's refill, not a result (lesson 5); it is not read.")
