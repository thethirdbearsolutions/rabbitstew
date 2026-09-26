"""RBT-101 (C4, flat terrain): the coordinator's 18:45 ruling on RBT-92's readout adversary (lessons 1-2 of the 19:35
wake), applied to C4 without changing the registered readout; RBT-99's placebo.py with C4's paths.  Method: RBT-92's readout adversary, probe_readout.py P3/P4 (PR #183,
runs/RBT-92/readout-adversary/), reused through readout.py's own Arm / rbody / classify / stat, committed tables only.

  P3  the registered class rule on arms and windows with no shift (the base arm, and 25 placebo onsets on the
      baseline alone, T' = T - 200 .. T + 40 in steps of 10): does the rule measure the event or the lead's level?
  P4  the event itself: the paired event - base contrast (R-body(shift) - R-body(base) = co-evolved R-shift -
      designed R-shift), per fauna R-shift against the no-event control AND against the pre-registered null
      (R-null = shift - cull; n/a where the cull emptied the fauna, F3), each with its interval and per-seed values
  sign guard margin, and the per-seed RMS of the A/A-like references (R-cull20 recovery, both faunas)

    python runs/RBT-101/placebo.py > runs/RBT-101/placebo.txt

k = 0/0 seeds (no cull arm; the null is the baseline itself, RBT-92 amendment 2): shift - cull = shift - base there.
"""
import math
import os
import statistics
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-92"))
import readout as R  # noqa: E402

SEEDS = R.SEEDS
TS = R.onsets()
WIN = {"before": (-100, 0), "transient": (0, 60), "recovery": (60, 160), "tail": (160, 200)}
K = {}
for s in SEEDS:
    for l in open(f"runs/RBT-101/cull-k-{s}.txt"):
        if l.startswith("cull\t"):
            K[s] = {p.split("=")[0]: int(p.split("=")[1]) for p in l.split("\t")[1].strip().split(",")}


def path(arm, s):
    if arm == "cull" and K[s] == {"holistic": 0, "conventional": 0}:
        return f"runs/RBT-90/forage-{s}"  # k = 0/0: no event, the null is the baseline itself
    return {"base": f"runs/RBT-90/forage-{s}", "shift": f"runs/RBT-101/shift-{s}", "cull": f"runs/RBT-101/cull-{s}",
            "cull20": f"runs/RBT-92/cull20-{s}"}[arm]


A = {(a, s): R.Arm(path(a, s)) for a in ("base", "shift", "cull", "cull20") for s in SEEDS}


def w(s, name, off=0):
    a, b = WIN[name]
    return TS[s] + off + a, TS[s] + off + b


def fwin(arm, k, a, b):
    return statistics.fmean(arm.x[k][t] for t in range(a, b))


def line(label, vals):
    v = [x for x in vals if x is not None]
    n, m, sd, hw = R.stat(v)
    return (f"{label}: mean {m:+.4f}  95% t({n - 1}) [{m - hw:+.4f}, {m + hw:+.4f}]  sd {sd:.4f}  positive "
            f"{sum(1 for x in v if x > 0)}/{n}   per seed [{', '.join('  n/a ' if x is None else f'{x:+.3f}' for x in vals)}]")


def cls(vals, e1=0, d=0, e2=0):
    n, m, sd, hw = R.stat(vals)
    return R.classify(n, m, hw, sum(v > 0 for v in vals), sum(v < 0 for v in vals), e1, d, e2), m, hw, sum(v > 0 for v in vals)


print(__doc__.split("\n\n")[0])
print()
print("P3 THE CLASS RULE WHERE THERE IS NO SHIFT (readout.py's classify; r = the set's own t(9) half-width;")
print("   E1/D/E2 counts: 0 on the base arm, where both faunas sit at 60 with incomes > 0.25; the shift arm's D count is readout.txt's)")
for a, dd in (("base", 0), ("shift", int(os.environ.get("RBT101_SHIFT_D", "0")))):
    for wn in ("before", "recovery", "tail"):
        vals = [R.rbody(A[(a, s)], *w(s, wn)) for s in SEEDS]
        c, m, hw, pos = cls(vals, d=dd if a == "shift" and wn != "before" else 0)
        print(f"   {a:6s} {wn:9s}: R-body {m:+.4f}  r {hw:.4f}  positive {pos}/10  -> {c[:18]}")
fire, tot = 0, 0
print("   placebo onsets on the baseline alone: the rule on base R-body over [T'+60, T'+160)")
row = []
for off in range(-200, 41, 10):
    vals = [R.rbody(A[("base", s)], *w(s, "recovery", off)) for s in SEEDS]
    c, m, hw, pos = cls(vals)
    tot += 1
    fire += c.startswith("A")
    row.append(f"T{off:+d}:{c[0]}")
print("     " + "  ".join(row))
print(f"   class A fires on {fire}/{tot} placebo onsets with no shift, and on the base arm's own recovery window.")
print("   => the class rule reads the LEVEL of the co-evolved lead; the event is read only by the paired contrast below.")
print()
print("P4 THE EVENT ITSELF: paired contrasts, recovery window [T+60, T+160)")
rs = {k: [fwin(A[("shift", s)], k, *w(s, "recovery")) - fwin(A[("base", s)], k, *w(s, "recovery")) for s in SEEDS] for k in R.KINDS}
rn = {k: [None if (K[s][k] > 0 and K[s][k] >= A[("base", s)].alive[k][TS[s] - 1])
          else fwin(A[("shift", s)], k, *w(s, "recovery")) - fwin(A[("cull", s)], k, *w(s, "recovery")) for s in SEEDS] for k in R.KINDS}
rc = {k: [fwin(A[("cull", s)], k, *w(s, "recovery")) - fwin(A[("base", s)], k, *w(s, "recovery")) for s in SEEDS] for k in R.KINDS}
diff = [a - b for a, b in zip(rs["holistic"], rs["conventional"])]
print("   " + line("event - base, R-body (= co-evolved R-shift - designed R-shift)", diff))
for k in R.KINDS:
    print("   " + line(f"{k:12s} R-shift  (shift - no-event control)", rs[k]))
    print("   " + line(f"{k:12s} R-null   (shift - pre-registered cull null; n/a where the cull emptied the fauna)", rn[k]))
    print("   " + line(f"{k:12s} R-cull   (cull - control: what the null itself did)", rc[k]))
unc = [s for s in SEEDS if not (K[s]["conventional"] >= A[("base", s)].alive["conventional"][TS[s] - 1])]
sc = [R.rbody(A[("shift", s)], *w(s, "recovery")) - R.rbody(A[("cull", s)], *w(s, "recovery")) for s in unc]
print("   " + line(f"event - null, R-body (shift - cull), the {len(unc)} seeds where the cull did not empty a fauna "
                    f"(k = 0/0 seeds: = shift - base)", sc))
k00 = [s for s in SEEDS if K[s] == {"holistic": 0, "conventional": 0}]
kpos = [s for s in SEEDS if s not in k00]
print(f"   k = 0/0 seeds (null = the baseline itself): {k00}; seeds with a cull arm: {kpos}")
sc2 = [R.rbody(A[("shift", s)], *w(s, "recovery")) - R.rbody(A[("cull", s)], *w(s, "recovery")) for s in kpos]
print("   " + line(f"event - null, R-body, only the {len(kpos)} seeds with a real cull (post hoc subset, defined by k, not by outcome)", sc2))
n, m, sd, hw = R.stat(diff)
print(f"   sign guard: the class rule needs >= ceil(0.8n) = {math.ceil(0.8 * n)}/10 positive; R-body(shift) is positive on "
      f"{sum(R.rbody(A[('shift', s)], *w(s, 'recovery')) > 0 for s in SEEDS)}/10 (margin "
      f"{sum(R.rbody(A[('shift', s)], *w(s, 'recovery')) > 0 for s in SEEDS) - math.ceil(0.8 * n)} seeds); the paired event - base "
      f"contrast is positive on {sum(d > 0 for d in diff)}/10")
negs = sum(R.rbody(A[('shift', s)], *w(s, 'recovery')) < 0 for s in SEEDS)
print(f"   sign guard, class C direction (C4): R-body(shift) is negative on {negs}/10 against the guard {math.ceil(0.8 * n)}/10 "
      f"(margin {negs - math.ceil(0.8 * n)} seed(s)); the smallest |negative| per-seed R-body(shift) is "
      f"{min(abs(R.rbody(A[('shift', s)], *w(s, 'recovery'))) for s in SEEDS if R.rbody(A[('shift', s)], *w(s, 'recovery')) < 0):.4f}")
aa = [fwin(A[("cull20", s)], k, *w(s, "recovery")) - fwin(A[("base", s)], k, *w(s, "recovery")) for s in SEEDS for k in R.KINDS]
rms = math.sqrt(statistics.fmean(x * x for x in aa))
print(f"   A/A-like per-seed reference: RMS of R-cull20 (recovery, both faunas, 20 values) = {rms:.4f}; no single per-seed value "
      f"of the size of this RMS is read alone")
