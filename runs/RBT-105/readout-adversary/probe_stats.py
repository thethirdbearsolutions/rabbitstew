"""RBT-105 readout adversary: the statistics of R1 and R2, from the committed per-arm files only (no bulk).

  S1  R1's null: where 0.1 comes from, and the verdict's sensitivity to it (P(Bin(14, q) >= 5) over q)
  S2  seed clustering: the flips counted per founding population, under independent and fully clustered nulls
  S3  undecided handling (registered?), and every imputation of the two undecided replicates
  S4  the classifier's bars: every +-1 step at each bar, originals re-classified with them
  S5  bar-free: one cut c anywhere on the count, and anywhere in the originals' late-rate gap
  S6  a continuous founder share: one-way ICC on replicates only (8 seeds x 2), for R2's y and log(distinct+0.5)
  S7  R2: reproduction, seed-level permutation, leave-one-seed-out, rank version, and R2 on log(distinct + 0.5)
  S8  the flip-rate interval (what R1's F/n actually licenses)

    python runs/RBT-105/readout-adversary/probe_stats.py > runs/RBT-105/readout-adversary/probe_stats.txt
"""
import importlib.util
import itertools
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent
ROOT = RUN.parent.parent
spec = importlib.util.spec_from_file_location("ro", RUN / "readout.py")
ro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ro)
spec = importlib.util.spec_from_file_location("part2", ROOT / "runs" / "RBT-90" / "part2_readout.py")
p2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p2)


def sf(F, n, q):
    return 1 - ro.binom_cdf(F - 1, n, q)


def orig_late():
    out, cur = {}, None
    for line in open(RUN / "osc-births-rbt90.txt"):
        if line.startswith("forage-"):
            cur = int(line.split()[0].split("-")[1])
        elif line.startswith("{") and cur is not None:
            d = eval(line)  # noqa: S307
            out[cur] = (d["late_k"], d["late_n"])
    return out


OL = orig_late()
rows = []
for seed, ks in ro.DESIGN.items():
    d0, _ = ro.fate_of(ROOT / "runs" / "RBT-90" / f"forage-{seed}" / "oscillator.txt")
    for k in ks:
        d, _ = ro.fate_of(ro.arm_dir(seed, k) / "oscillator.txt")
        j = p2.last_json(ro.arm_dir(seed, k) / "osc_births.txt")
        rows.append(dict(seed=seed, k=k, d0=d0, d=d, lk=j["late_k"], ln=j["late_n"], r0=OL[seed][0] / OL[seed][1]))
for r in rows:
    r["y"] = math.log((r["lk"] + 0.5) / (r["ln"] + 1))
    r["rate"] = r["lk"] / r["ln"]
    r["ly"] = math.log(r["d"] + 0.5)


def fate(d, lo=2, hi=8):
    return "D" if d <= lo else ("A" if d >= hi else "u")


def count(lo=2, hi=8, rs=rows):
    F = n = 0
    for r in rs:
        f0, f = fate(r["d0"], lo, hi), fate(r["d"], lo, hi)
        if f0 in "AD" and f in "AD":
            n += 1
            F += f != f0
    return F, n


def r1(F, n):
    if n == 0:
        return "NOT DECIDED"
    if ro.binom_cdf(F, n, 0.5) <= 0.05:
        return "FOUNDERS DOMINANT"
    if sf(F, n, 0.1) <= 0.05:
        return "SUBSTANTIAL HISTORY"
    return "NOT DECIDED"


print("RBT-105 readout adversary, probe_stats.py (committed files only)\n")
F, n = count()
print(f"S0  reproduction: F = {F}, n = {n}, R1 = {r1(F, n)}, P(Bin({n}, 0.1) >= {F}) = {sf(F, n, 0.1):.4f}   (readout.txt: 5, 14, 0.0092)\n")

print("S1  R1's null q (registered: Q_SUBST = 0.1, PREREGISTRATION.md s3, from the design adversary's F2 proposal; no measurement behind it)")
for q in (0.05, 0.10, 0.15, 0.20, 0.25, 0.30):
    print(f"    q = {q:.2f}: P(Bin(14, q) >= 5) = {sf(5, 14, q):.4f}  -> {'fires' if sf(5, 14, q) <= 0.05 else 'does NOT fire'};"
          f"   at n = 16 (undecided counted as kept) P(Bin(16, q) >= 5) = {sf(5, 16, q):.4f}")
lo, hi = 0.0, 1.0
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if sf(5, 14, mid) <= 0.05 else (lo, mid)
print(f"    the largest null q that F = 5 of 14 still rejects at 0.05: q* = {lo:.3f}")
print("    what a founders-only world's flip rate is made of: count noise across the 3..7 gap. The design adversary's")
print("    within-run window re-scores (adversary/probe_distinct.txt; 10 RBT-90 arms x 7 windows) never cross D<->A;")
print("    see probe_windows.txt for the same on the 16 replicates (bulk).\n")

print("S2  seed clustering (flips per founding population; 7 seeds with both replicates decided or one flip)")
per = {}
for r in rows:
    f0, f = fate(r["d0"]), fate(r["d"])
    per.setdefault(r["seed"], []).append("x" if f == "u" else ("F" if f != f0 else "k"))
print("    " + "  ".join(f"{s}:{''.join(v)}" for s, v in per.items()))
dec = {s: v for s, v in per.items() if any(c != "x" for c in v)}
S = sum(1 for v in dec.values() if "F" in v)
m = len(dec)
print(f"    founding populations with >= 1 flip: {S} of {m} (seed 4 has no decided replicate)")
for q in (0.05, 0.10, 0.15, 0.20):
    ind = 1 - (1 - q) ** 2
    print(f"    q = {q:.2f}: independent replicates  P(Bin({m}, {ind:.3f}) >= {S}) = {sf(S, m, ind):.4f};"
          f"  fully clustered (a flip is the ORIGINAL's deviation, both replicates follow)  P(Bin({m}, {q:.2f}) >= {S}) = {sf(S, m, q):.4f}")
# a cluster-aware exact test on F itself: per-seed flip count ~ BetaBinomial(2, q, rho); the two limits above bracket it
# the pair structure actually seen: seeds with 2 flips vs 1 flip
two = sum(1 for v in dec.values() if v.count("F") == 2)
one = sum(1 for v in dec.values() if v.count("F") == 1)
print(f"    pattern: {two} seeds with both replicates flipped, {one} with one. Under independence at the observed rate 5/14,")
p = 5 / 14
e2 = m * p * p
print(f"    expected both-flipped seeds = {e2:.2f} (of {m}); observed {two}: flips are clustered by seed, i.e. the ORIGINAL is the odd run out on 7 and 2.")
lo, hi = 0.0, 1.0
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if sf(S, m, mid) <= 0.05 else (lo, mid)
print(f"    fully clustered, the largest seed-level q that {S} of {m} rejects at 0.05: {lo:.3f}\n")

print("S3  undecided handling: registered (PREREGISTRATION.md s3 'A replicate is decided if its fate is discarded or acquired';")
print("    EXTINCT counted as undecided; n = decided replicates). Every imputation of 4-b1 (4) and 4-b2 (6):")
for a, b in itertools.product(("kept", "flipped", "excluded"), repeat=2):
    FF, nn = 5, 14
    for x in (a, b):
        if x != "excluded":
            nn += 1
            FF += x == "flipped"
    print(f"    4-b1 {a:8s} 4-b2 {b:8s}: F = {FF}, n = {nn}: P(Bin(n, .1) >= F) = {sf(FF, nn, .1):.4f} -> {r1(FF, nn)}")
print()

print("S4  the bars: RBT-84's (<= 2 D, >= 8 A), imported unchanged from runs/RBT-90/part2_readout.py; set before RBT-90 part 2,")
print("    i.e. before any RBT-105 arm. Every +-1 step, originals re-classified with the same bars:")
for lo_ in (1, 2, 3):
    for hi_ in (7, 8, 9):
        FF, nn = count(lo_, hi_)
        dropped = [r["seed"] for r in rows if fate(r["d0"], lo_, hi_) == "u" and r["k"] == 1]
        print(f"    D <= {lo_}, A >= {hi_}: F = {FF:2d}, n = {nn:2d}, P(Bin(n,.1)>=F) = {sf(FF, nn, .1):.4f}, P(Bin(n,.5)<=F) = {ro.binom_cdf(FF, nn, .5):.3f}"
              f" -> {r1(FF, nn):20s} originals undecided: {dropped or '-'}")
print()

print("S5  bar-free: a single cut c (fate = above/below c; no undecided band), on the count and on the late rate")
print("    on distinct (flip = original and replicate on opposite sides of c), c from 0.5 to 20.5:")
for c in [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 12.5, 15.5, 20.5]:
    FF = sum(1 for r in rows if (r["d0"] > c) != (r["d"] > c))
    print(f"      c = {c:4.1f}: F = {FF:2d} of 16, P(Bin(16,.1)>=F) = {sf(FF, 16, .1):.4f}, P(Bin(16,.5)<=F) = {ro.binom_cdf(FF, 16, .5):.3f} -> {r1(FF, 16)}")
print("    on the late (300-599) birth rate, c anywhere in the originals' gap (0.013, 0.221):")
cuts = sorted({round(x, 4) for x in [0.0131, 0.02, 0.03, 0.05, 0.061, 0.07, 0.08, 0.1, 0.13, 0.15, 0.2, 0.22]})
for c in cuts:
    fl = [f"{r['seed']}-b{r['k']}" for r in rows if (r["r0"] > c) != (r["rate"] > c)]
    FF = len(fl)
    print(f"      c = {c:.4f}: F = {FF:2d} of 16 {r1(FF, 16):20s} P(Bin(16,.1)>=F) = {sf(FF, 16, .1):.4f}  {' '.join(fl)}")
print()


def icc(vals):
    """one-way ANOVA ICC(1) for groups of 2, with the F statistic and its exact-free permutation p over pairings."""
    g = list(vals.values())
    k, nn = len(g), 2
    grand = sum(sum(x) for x in g) / (k * nn)
    msb = nn * sum((sum(x) / nn - grand) ** 2 for x in g) / (k - 1)
    msw = sum(sum((v - sum(x) / nn) ** 2 for v in x) for x in g) / (k * (nn - 1))
    return (msb - msw) / (msb + (nn - 1) * msw), msb / msw


def perm_pairings(flat):
    """every way to split 16 values into 8 unordered pairs: 2027025; use F >= observed."""
    idx = list(range(len(flat)))
    out = []

    def rec(rem, acc):
        if not rem:
            out.append(list(acc))
            return
        a = rem[0]
        for j in range(1, len(rem)):
            rec(rem[1:j] + rem[j + 1:], acc + [(a, rem[j])])
    rec(idx, [])
    return out


print("S6  a continuous founder share, replicates only (8 seeds x 2; the originals, selected on outcome, left out)")
PAIRS = perm_pairings(list(range(16)))
import numpy as np  # noqa: E402  F(7, 8) quantiles by seeded simulation (no scipy in the container)
_g = np.random.default_rng(105)
_f = np.sort((_g.chisquare(7, 4_000_000) / 7) / (_g.chisquare(8, 4_000_000) / 8))
FQ = (_f[int(0.025 * len(_f))], _f[int(0.975 * len(_f))])
for key, lab in (("y", "R2's y = log late rate"), ("ly", "log(distinct + 0.5)")):
    vals = {}
    for r in rows:
        vals.setdefault(r["seed"], []).append(r[key])
    est, Fst = icc(vals)
    flat = [v for x in vals.values() for v in x]
    ge = 0
    for pr in PAIRS:
        _, f = icc({i: [flat[a], flat[b]] for i, (a, b) in enumerate(pr)})
        ge += f >= Fst - 1e-12
    # F(7, 8) CI for ICC
    lo_f, hi_f = FQ
    ci = ((Fst / hi_f - 1) / (Fst / hi_f + 1), (Fst / lo_f - 1) / (Fst / lo_f + 1))
    print(f"    {lab:24s}: ICC(1) = {est:+.3f}, 95% CI [{ci[0]:+.2f}, {ci[1]:+.2f}] (F(7, 8) quantiles), F(7, 8) = {Fst:.2f}, "
          f"exact permutation p over all {len(PAIRS)} pairings = {ge / len(PAIRS):.4f}")
    for s, v in vals.items():
        print(f"        {s:4d}: " + "  ".join(f"{x:+.2f}" for x in v))
print("    (R2 is a between-group contrast on the originals' labels; this is the label-free version of the same question.)\n")

print("S7  R2 (registered secondary, its own alpha 0.05; no family-wise correction registered, none needed for the")
print("    conjunction 'R1 and R2' (an intersection-union claim has size <= alpha))")
ys = [((1 if fate(r["d0"]) == "A" else -1), r["y"]) for r in rows]
t, p, nper = ro.r2(ys)
print(f"    reproduction: T = {t:+.3f}, p = {p:.4f} over {nper}   (readout.txt: +2.348, 0.0113)")
seeds = list(ro.DESIGN)
side = {s: (1 if fate(next(r['d0'] for r in rows if r['seed'] == s)) == "A" else -1) for s in seeds}
sm = {s: sum(r["y"] for r in rows if r["seed"] == s) / 2 for s in seeds}
acq = [s for s in seeds if side[s] > 0]
tobs = sum(sm[s] for s in acq) / 4 - sum(sm[s] for s in seeds if side[s] < 0) / 4
null = [sum(sm[s] for s in c) / 4 - sum(sm[s] for s in seeds if s not in c) / 4 for c in itertools.combinations(seeds, 4)]
print(f"    seed-level (8 seed means, C(8,4) = 70 labellings; smallest attainable p 1/70 = 0.0143): T = {tobs:+.3f}, p = {sum(v >= tobs - 1e-12 for v in null) / 70:.4f}")
for s in seeds:
    sub = [(sd, y) for (sd, y), r in zip(ys, rows) if r["seed"] != s]
    tt, pp, _ = ro.r2(sub)
    print(f"      leave seed {s:4d} out: T = {tt:+.3f}, p = {pp:.4f}")
# rank version
order = sorted(range(16), key=lambda i: ys[i][1])
rk = [0] * 16
for pos, i in enumerate(order):
    rk[i] = pos + 1
tt, pp, _ = ro.r2([(ys[i][0], rk[i]) for i in range(16)])
print(f"    rank (Wilcoxon-type) on y: T = {tt:+.3f}, p = {pp:.4f}")
tt, pp, _ = ro.r2([(ys[i][0], rows[i]["ly"]) for i in range(16)])
print(f"    on log(distinct + 0.5) (the adversary's first y; the count R1 reads): T = {tt:+.3f}, p = {pp:.4f}\n")

print("S8  what R1 licenses about the flip rate: F/n = 5/14 = 0.357")
lo_q = 0.0
lo, hi = 0.0, 5 / 14
for _ in range(80):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if sf(5, 14, mid) <= 0.025 else (lo, mid)
lo2, hi2 = 5 / 14, 1.0
for _ in range(80):
    mid = (lo2 + hi2) / 2
    lo2, hi2 = (mid, hi2) if ro.binom_cdf(5, 14, mid) > 0.025 else (lo2, mid)
print(f"    two-sided 95% Clopper-Pearson for q: [{lo:.3f}, {hi2:.3f}] (independent replicates; wider under seed clustering)")
print(f"    one-sided 95% lower bound: {q_star if (q_star := None) else ''}", end="")
lo, hi = 0.0, 5 / 14
for _ in range(80):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if sf(5, 14, mid) <= 0.05 else (lo, mid)
print(f"{lo:.3f}. 'History decides the fate' would need q near 1/2 (pure history, balanced design); q = 1/2 is inside the interval")
print(f"    but FOUNDERS DOMINANT's own test gives P(Bin(14, .5) <= 5) = {ro.binom_cdf(5, 14, .5):.3f}: neither q = 1/2 nor q = 0.1 is the fitted value.")
