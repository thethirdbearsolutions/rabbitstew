"""RBT-100 (C3): arithmetic first, then the registered predictions scored, from committed files only.

    python runs/RBT-100/score.py > runs/RBT-100/score.txt

1. ARITHMETIC (the coordinator's 19:35 lesson 3; RBT-99's F2).  C3 halves the items in the disc and nothing else
   (PREREGISTRATION.md section 3.1).  An UNCHANGED population's gross food halves and its work does not move
   (section 4; the round-1 adversary's P1 measured x0.47-0.49 gross and an unmoved work charge).  From each seed's
   pre-onset seasons [T-40, T) of base-SEED/own.txt (the baseline's own net table; its pre-T rows equal the shift
   arm's, checked below), per fauna:
     food, work    mean items eaten and work charge per individual-season over the survivors of each season
     price         food / 2: what the shift takes from that fauna's season income if nobody changes
     unchanged     food / 2 - work: the fauna's season own net at an unchanged gait, against basal 0.25
   The arithmetic paired prediction for R-body (shift - base) is price(designed) - price(co-evolved).  The observed
   paired effect and each fauna's R-shift are readout.py's (recovery window, extinct = 0); the residual of each fauna
   is R-shift + price, its net, read side by side.  The same is printed on the own-net scale (own.txt's
   net_survivors, shift - base), which is a season mean, not the axis's lifetime mean.
2. SCORING of every registered prediction (PREREGISTRATION.md section 8 and Amendments 1-3), as registered.  [YES]/[NO ]
   says whether the predicted event happened; the Brier score weighs it against the stated probability.
"""
import csv
import math
import os
import statistics
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-92"))
import readout as R  # noqa: E402

KINDS = ("holistic", "conventional")
SEEDS = R.SEEDS
TS = R.onsets()
TR, RE = 60, 100


def own(path):
    return {(int(r["season"]), r["population"]): r for r in csv.DictReader(open(os.path.join(path, "own.txt")), delimiter="\t")}


def ownmean(o, k, a, b, col):
    v = [float(o[(t, k)][col]) for t in range(a, b) if (t, k) in o and o[(t, k)][col] != "-"]
    return statistics.fmean(v) if v else float("nan")


def ci(v):
    n, m, sd, hw = R.stat(v)
    return f"{m:+.4f} [{m - hw:+.4f}, {m + hw:+.4f}] (t({n - 1}), sd {sd:.4f}, positive {sum(x > 0 for x in v)}/{n})"


def k_of(s):
    for line in open(f"runs/RBT-100/cull-k-{s}.txt"):
        if line.startswith("cull\t"):
            return {p.split("=")[0]: int(p.split("=")[1]) for p in line.split("\t")[1].strip().split(",")}


A = {(a, s): R.Arm(p) for s in SEEDS for a, p in (("base", f"runs/RBT-90/forage-{s}"), ("shift", f"runs/RBT-100/shift-{s}"),
                                                   ("cull", f"runs/RBT-100/cull-{s}"))}
OB = {s: own(f"runs/RBT-100/base-{s}") for s in SEEDS}
OS = {s: own(f"runs/RBT-100/shift-{s}") for s in SEEDS}


def wm(a, s, k, lo, hi):
    return statistics.fmean(A[(a, s)].x[k][t] for t in range(TS[s] + lo, TS[s] + hi))


print(__doc__.split("\n\n")[0])
print()
print("1. ARITHMETIC FIRST: what halving the items does to an UNCHANGED population, from pre-onset seasons [T-40, T)")
same = sum(1 for s in SEEDS for key, r in OB[s].items() if key[0] < TS[s] and OS[s].get(key) != r)
print(f"   base-SEED/own.txt and shift-SEED/own.txt rows before T that differ: {same} (V0 on the own tables)")
print("   seed   T  | co-evolved food  work  net   price unchanged | designed food  work  net   price unchanged")
price, unch = {k: [] for k in KINDS}, {k: [] for k in KINDS}
for s in SEEDS:
    T = TS[s]
    cells = []
    for k in KINDS:
        f = ownmean(OB[s], k, T - 40, T, "food")
        w = ownmean(OB[s], k, T - 40, T, "work")
        price[k].append(f / 2)
        unch[k].append(f / 2 - w)
        cells.append(f"{f:5.3f} {w:5.3f} {f - w:+.3f} {f / 2:5.3f} {f / 2 - w:+.3f}")
    print(f"   {s:>4} {T:>4} |       {cells[0]}  |     {cells[1]}")
for k in KINDS:
    below = sum(u < R.BASAL for u in unch[k])
    print(f"   {k:12s}: price {ci(price[k])};  unchanged-gait season net {ci(unch[k])};  below basal 0.25 on {below}/10 seeds")
arith = [pc - ph for ph, pc in zip(price["holistic"], price["conventional"])]
rs = {k: [wm("shift", s, k, TR, TR + RE) - wm("base", s, k, TR, TR + RE) for s in SEEDS] for k in KINDS}
obs = [a - b for a, b in zip(rs["holistic"], rs["conventional"])]
print()
print("   The paired contrast, recovery window [T+60, T+160), on the axis (lifetime mean, extinct = 0):")
print(f"     arithmetic prediction for two unchanged populations, price(designed) - price(co-evolved): {ci(arith)}")
print(f"     observed shift - base R-body (= co-evolved R-shift - designed R-shift):                  {ci(obs)}")
print(f"     residual, observed - arithmetic:                                                         {ci([o - a for o, a in zip(obs, arith)])}")
net = {k: [r + p for r, p in zip(rs[k], price[k])] for k in KINDS}
print("   Both nets side by side (net = R-shift + price: what each body recovered of its own price; recovery window):")
for k in KINDS:
    share = [n / p for n, p in zip(net[k], price[k])]
    print(f"     {k:12s} R-shift {ci(rs[k])}")
    print(f"     {'':12s} net     {ci(net[k])};  share of price recovered, mean {statistics.fmean(share):+.3f} "
          f"(per seed {min(share):+.2f} to {max(share):+.2f})")
print(f"     net co-evolved - net designed: {ci([a - b for a, b in zip(net['holistic'], net['conventional'])])}")
ext = [s for s in SEEDS if any(A[('shift', s)].alive['conventional'].get(t, 0) == 0 for t in range(TS[s] + TR, TS[s] + TR + RE))]
print(f"     designed conditioning: extinct inside the recovery window on {len(ext)}/10 seeds ({', '.join(map(str, ext))}): "
      f"its axis is 0 from extinction there; survivor-conditioned elsewhere")
print("   The same on the own-net scale (own.txt net_survivors, a season mean over each season's survivors; shift - base):")
for k in KINDS:
    d = [ownmean(OS[s], k, TS[s] + TR, TS[s] + TR + RE, "net_survivors") - ownmean(OB[s], k, TS[s] + TR, TS[s] + TR + RE, "net_survivors")
         for s in SEEDS]
    print(f"     {k:12s} {ci(d)};  + price: {ci([a + p for a, p in zip(d, price[k])])}")
print()

# ------------------------------------------------------------------ scoring
print("2. THE REGISTERED PREDICTIONS, SCORED (section 8 and Amendments 1-3; values from committed tables)")
sh = {s: A[("shift", s)] for s in SEEDS}


def minalive(s, k, lo=0, hi=160):
    return min(sh[s].alive[k].get(t, 0) for t in range(TS[s] + lo, TS[s] + hi))


def extinct_by(s, k, off):
    return any(sh[s].alive[k].get(t, 0) == 0 for t in range(TS[s], TS[s] + off))


def bankrupt(s, k):
    return (wm("shift", s, k, 0, TR) < R.BASAL or wm("shift", s, k, TR, TR + RE) < R.BASAL or minalive(s, k) < R.FLOOR)


dz = sum(bankrupt(s, "conventional") and not bankrupt(s, "holistic") for s in SEEDS)
rbr = [R.rbody(sh[s], TS[s] + TR, TS[s] + TR + RE) for s in SEEDS]
n, m, _, _ = R.stat(rbr)
print(f"   class: A (readout.txt).  Registered (Amendment 3): D 0.45, A 0.30, F 0.09, E1 0.06, B 0.04, C 0.04, E2 0.02 -> "
      f"p(realised) 0.30; multiclass Brier {sum((p - (c == 'A')) ** 2 for c, p in (('D', .45), ('A', .30), ('F', .09), ('E1', .06), ('B', .04), ('C', .04), ('E2', .02))):.3f}")
print(f"     class D's test: {dz}/10 seeds, guard ceil(0.8n) = 8 -> D missed by {8 - dz} seed(s); A's sign guard: "
      f"{sum(x > 0 for x in rbr)}/10 positive against 8 -> margin {sum(x > 0 for x in rbr) - 8}")
B = []


def binary(label, p, hit, value):
    B.append((p, 1 if hit else 0))
    print(f"   [{'YES' if hit else 'NO '}] p {p:.2f}  {label}: {value}")


def point(label, pred, lo, hi, vals):
    med = statistics.median(vals)
    print(f"   [point] {label}: predicted {pred} ({lo} to {hi}); realised median {med:+.3f}, per seed "
          f"[{', '.join(f'{v:+.3f}' if isinstance(v, float) else str(v) for v in vals)}]; "
          f"median {'inside' if lo <= med <= hi else 'OUTSIDE'} the range, {sum(lo <= v <= hi for v in vals)}/10 per-seed values inside")


extinct200 = [s for s in SEEDS if extinct_by(s, "conventional", 200)]
binary("designed reaches alive = 0 by T+200 on >= 3/10", 0.5, len(extinct200) >= 3, f"{len(extinct200)}/10 ({', '.join(map(str, extinct200))})")
point("designed min alive over [T, T+160)", "9", 0, 35, [minalive(s, "conventional") for s in SEEDS])
nonext = [s for s in SEEDS if not extinct_by(s, "conventional", 160)]
fl = sum(minalive(s, "conventional") < R.FLOOR for s in nonext)
inc = sum(wm("shift", s, "conventional", TR, TR + RE) < R.BASAL for s in nonext)
print(f"   [cond ] 'if D, among seeds not extinct by T+160 the floor fires on more seeds than the recovery-income trigger', 0.65: "
      f"NOT SCORED (the class is not D). For the record: {len(nonext)} such seeds, floor {fl}, recovery income {inc}")
binary("co-evolved survives to T+200 on 10/10", 0.8, not any(extinct_by(s, "holistic", 200) for s in SEEDS), "10/10" if not any(extinct_by(s, 'holistic', 200) for s in SEEDS) else "no")
point("co-evolved min alive over [T, T+160)", "38", 15, 60, [minalive(s, "holistic") for s in SEEDS])
point("co-evolved recovery income (axis)", "+0.48", 0.33, 0.65, [wm("shift", s, "holistic", TR, TR + RE) for s in SEEDS])
binary("co-evolved trips no D trigger on >= 8/10", 0.75, sum(not bankrupt(s, "holistic") for s in SEEDS) >= 8,
       f"{sum(not bankrupt(s, 'holistic') for s in SEEDS)}/10")
dr = [wm("shift", s, "conventional", TR, TR + RE) for s in SEEDS]
point("designed recovery income (axis, living mean, extinct = 0)", "+0.28", 0.10, 0.45, dr)
binary("designed recovery income below 0.25 on >= 8/10", 0.2, sum(x < R.BASAL for x in dr) >= 8, f"{sum(x < R.BASAL for x in dr)}/10")
for wn, pred, lo, hi in (("before", "+0.12", None, None), ("transient", "+0.15", None, None), ("recovery", "+0.22", -0.05, 0.50)):
    a, b = {"before": (-100, 0), "transient": (0, 60), "recovery": (60, 160)}[wn]
    v = [R.rbody(sh[s], TS[s] + a, TS[s] + b) for s in SEEDS]
    print(f"   [point] R-body {wn}: predicted {pred}; realised mean {statistics.fmean(v):+.4f}"
          + (f"; per-seed range predicted {lo} to {hi}, realised {min(v):+.3f} to {max(v):+.3f}, {sum(lo <= x <= hi for x in v)}/10 inside" if lo is not None else ""))
print(f"   [point] co-evolved R-shift recovery: predicted -0.60 (-0.85 to -0.35); realised mean {statistics.fmean(rs['holistic']):+.4f} "
      f"({'inside' if -0.85 <= statistics.fmean(rs['holistic']) <= -0.35 else 'OUTSIDE'})")
print(f"   [point] designed R-shift recovery (restated, extinct = 0): predicted -0.75 (-1.05 to -0.40); realised mean "
      f"{statistics.fmean(rs['conventional']):+.4f} ({'inside' if -1.05 <= statistics.fmean(rs['conventional']) <= -0.40 else 'OUTSIDE'})")
binary("co-evolved R-shift > designed R-shift (the co-evolved loses less)", 0.65, statistics.fmean(obs) > 0,
       f"paired {ci(obs)}; the arithmetic predicts {statistics.fmean(arith):+.4f} of it (section 1)")
rpow = float(open("runs/RBT-100/readout.txt").read().split("  r = ")[1].split(" ")[0])
binary("'holds up' (co-evolved R-shift >= -r) NOT earned", 0.95, statistics.fmean(rs["holistic"]) < -rpow,
       f"R-shift {statistics.fmean(rs['holistic']):+.4f} against -r = {-rpow:+.4f}")
K1 = [k_of(s)["holistic"] for s in SEEDS]
K2 = [k_of(s)["conventional"] for s in SEEDS]
print(f"   [point] k: K1 predicted median 2 (0-12), realised median {statistics.median(K1)} {K1}; K2 predicted median 10 (0-30), "
      f"realised median {statistics.median(K2)} {K2}")
rn = [wm("shift", s, "holistic", TR, TR + RE) - wm("cull", s, "holistic", TR, TR + RE) for s in SEEDS if k_of(s)["holistic"] > 0]
binary("turnover guard: co-evolved |R-null| >= r (printed; not interpretable for C3, Amendment 2)", 0.95,
       abs(statistics.fmean(rn)) >= rpow, f"|{statistics.fmean(rn):+.4f}| on the {len(rn)} seeds with co-evolved k > 0, r {rpow:.4f}")
txt = open("runs/RBT-100/readout.txt").read()
c3 = txt.split("CLAIM 3: ")[1].split("\n")[0]
binary("CLAIM 3 holds (added after P1)", 0.75, "HOLDS" in c3, c3)
own_below = {k: sum(ownmean(OS[s], k, TS[s] + TR, TS[s] + TR + RE, "net_all_ub") < R.BASAL for s in SEEDS) for k in KINDS}
binary("designed own net (all who ran, upper bound) below basal in recovery on >= 8/10 (added after P1)", 0.6,
       own_below["conventional"] >= 8, f"{own_below['conventional']}/10")
binary("co-evolved own net below basal in recovery on <= 2/10 (added after P1)", 0.7, own_below["holistic"] <= 2, f"{own_below['holistic']}/10")
F = {s: R.Arm(f"runs/RBT-100/founders6-{s}") for s in SEEDS}
fh = sum(F[s].alive["holistic"].get(59, 0) < R.FLOOR for s in SEEDS)
fc = sum(F[s].alive["conventional"].get(59, 0) < R.FLOOR for s in SEEDS)
binary("co-evolved founders at six items FAIL on 3-7/10 (added after P2)", 0.7, 3 <= fh <= 7, f"{fh}/10")
binary("designed founders FAIL on >= 8/10 (added after P2)", 0.8, fc >= 8, f"{fc}/10")
cs = txt.split("contrast sentence on ")[1].split(" ")[0]
binary("the contrast sentence prints on at least half the founder-fail seeds (added after P2)", 0.6,
       int(cs.split("/")[0]) * 2 >= int(cs.split("/")[1]), cs)
binary("co-evolved founders HOLD on >= 3/10 (added after P2)", 0.7, 10 - fh >= 3, f"{10 - fh}/10")
rec = txt.split("paired (primary)")
none_h = rec[1].count("'none'") if "holistic     shift" in rec[1] else None
lines = {l.split(":")[0].strip(): l for l in txt.splitlines() if l.startswith("  paired (primary)")}
def per(label):
    l = next(x for x in txt.splitlines() if x.startswith("  paired (primary)") and label in x)
    return eval(l.split("per seed ")[1])
sh_none = min(sum(v == "none" for v in per(f"{k:12s} shift")) for k in KINDS)
binary("recovery (paired, restated): shift 'none' within 180 on >= 9/10 for both faunas (scored as registered; NOT a recovery claim, lesson 4)",
       0.8, sh_none >= 9, f"holistic {sum(v == 'none' for v in per('holistic     shift'))}/10, designed {sum(v == 'none' for v in per('conventional shift'))}/10")
cu = [sum(v != "none" and int(v) <= 20 for v in per(f"{k:12s} cull  ")) for k in KINDS]
binary("recovery (paired, restated): cull <= 20 on >= 8/10 (both faunas; scored as registered, not a claim)", 0.6, min(cu) >= 8,
       f"holistic {cu[0]}/10, designed {cu[1]}/10")
ech = txt.split("ECHO:")[1]
bh = int(ech.split("holistic    : a peak starting inside the recovery window on shift ")[1].split(", base ")[1].split("/")[0])
binary("ECHO: base has a holistic peak starting inside the recovery window on >= 8/10", 0.7, bh >= 8, f"{bh}/10")
binary("ECHO: the echo sentence printed", 0.25, "contains the shift's own echo" in ech.split("CLASS D")[0], "printed" if "contains the shift's own echo" in ech.split("CLASS D")[0] else "not printed")
lsc = txt.split("T+160  L  shift-cull : ")[1].split(" ")[0]
print(f"   [----] p 0.50  carriage L(T+160) shift - cull, holistic, below -0.10: NOT SCORED (UNVALIDATED, V3); value {lsc}, not read")
dep = txt.split("DEPTH:")[1]
hs = float(dep.split("holistic     shift:")[1].split("median ")[1].split("\n")[0])
hb = float(dep.split("holistic      base:")[1].split("median ")[1].split("\n")[0])
binary("depth: co-evolved shift median <= base median", 0.7, hs <= hb, f"{hs} against {hb}")
print(f"   Brier over the {len(B)} probability-stated binary predictions (class rows, the conditional row and the carriage row "
      f"excluded): {statistics.fmean((p - o) ** 2 for p, o in B):.3f}")
print()
print("   Most exposed claims (section 9):")
print(f"     1. C3 bankrupts the designed population first; falsified if D's test counts <= 5/10: it counts {dz}/10 -> "
      f"{'not falsified' if dz > 5 else 'FALSIFIED'} (and class D itself missed its 8/10 guard by {8 - dz})")
ch = sum(bankrupt(s, "holistic") for s in SEEDS)
print(f"     2. the established co-evolved population holds; falsified if it trips a D trigger on >= 3/10: {ch}/10 -> "
      f"{'not falsified' if ch < 3 else 'FALSIFIED'}")
print(f"     3. (rescored) recruits carry the designed excess mortality: {c3}")
