"""RBT-100 readout adversary: the arithmetic, extinction, power, A/A, D, founders and the guards, from committed files.

Reads only committed tables (seasons.txt, own.txt, events.txt, config.json, cull-k, founders6), through RBT-92's
readout.py Arm / rbody / classify / stat, as score.py and placebo.py do.  No bulk, no ckpt, no new arm.

  P1  inputs: every arm's config (seed, event season, flag, value), table coverage, V0 on own.txt
  P2  the arithmetic (lesson 3): score.py's construction reproduced; its choices varied (pre-T window, scale);
      linearity in food density tested; the extinction-consistent version; the spread of predictions and residuals
  P3  extinction coding: how much of the paired effect, the residual and the class come from the 5 extinct seeds
  P4  matched-null power of the residual: what the design could have detected
  P5  A/A-like spread from the committed cull and cull20 contrasts; is +0.138 [+0.006, ...] inside it?
  P6  D at 7/10: per-seed trigger margins, binomial and jitter illustrations
  P7  the sign guard (RBT-92 F6 jitter) on R-body and on the paired contrast
  P8  the established population's survivorship reading: survival-based or income-based? starved share
  P9  founders6: trajectories, the season-59 threshold, conditioning of "7/7"

    python runs/RBT-100/readout-adversary/probe_readout.py > runs/RBT-100/readout-adversary/probe_readout.txt
"""
import csv
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

KINDS = ("holistic", "conventional")
H, D = KINDS
SEEDS = R.SEEDS
TS = R.onsets()
TR, RE = 60, 100
C3 = "runs/RBT-100"


def path(arm, s):
    return {"base": f"runs/RBT-90/forage-{s}", "shift": f"{C3}/shift-{s}", "cull": f"{C3}/cull-{s}",
            "cull20": f"runs/RBT-92/cull20-{s}", "founders6": f"{C3}/founders6-{s}"}[arm]


A = {(a, s): R.Arm(path(a, s)) for a in ("base", "shift", "cull", "cull20", "founders6") for s in SEEDS}


def own(p):
    return {(int(r["season"]), r["population"]): r for r in csv.DictReader(open(os.path.join(p, "own.txt")), delimiter="\t")}


OB = {s: own(f"{C3}/base-{s}") for s in SEEDS}
OS = {s: own(f"{C3}/shift-{s}") for s in SEEDS}


def om(o, k, a, b, col):
    v = [float(o[(t, k)][col]) for t in range(a, b) if (t, k) in o and o[(t, k)][col] != "-"]
    return st.fmean(v) if v else float("nan")


def osum(o, k, a, b, col):
    return sum(float(o[(t, k)][col]) for t in range(a, b) if (t, k) in o and o[(t, k)][col] != "-")


def wm(a, s, k, lo, hi, x=None):
    xs = x if x is not None else A[(a, s)].x[k]
    return st.fmean(xs[t] for t in range(TS[s] + lo, TS[s] + hi))


def ci(v, p=3):
    n, m, sd, hw = R.stat(v)
    return f"{m:+.{p}f} [{m - hw:+.{p}f}, {m + hw:+.{p}f}] sd {sd:.{p}f}, {sum(x > 0 for x in v)}/{n} positive"


def per(v, p=3):
    return "[" + ", ".join(f"{x:+.{p}f}" for x in v) + "]"


def rs(arm, k, x=None):
    """R-shift of arm against base, recovery window, per seed (extinct = 0, the registered coding unless x given)."""
    return [(wm(arm, s, k, TR, TR + RE, x[s] if x else None)) - wm("base", s, k, TR, TR + RE) for s in SEEDS]


def kof(s):
    for l in open(f"{C3}/cull-k-{s}.txt"):
        if l.startswith("cull\t"):
            return {p.split("=")[0]: int(p.split("=")[1]) for p in l.split("\t")[1].strip().split(",")}


def extinct_at(s, k):
    al = A[("shift", s)].alive[k]
    z = [t for t in range(TS[s], 600) if al.get(t, 0) == 0]
    return z[0] if z else None


EXT = [s for s in SEEDS if extinct_at(s, D) is not None and extinct_at(s, D) < TS[s] + TR + RE]
NON = [s for s in SEEDS if s not in EXT]

print(__doc__.split("\n\n")[0])
print(f"seeds {SEEDS}; T {[TS[s] for s in SEEDS]}")
print()

# ------------------------------------------------------------------ P1
print("P1  INPUTS")
bad = []
fends = {}
for s in SEEDS:
    for a in ("shift", "cull", "founders6"):
        c = json.load(open(os.path.join(path(a, s), "config.json")))
        e, f = c["ecology"], c["sim"]["food"]
        want = {"shift": (600, TS[s], "food-items=6", None, None, 12), "cull": (600, None, None, TS[s], None, 12),
                "founders6": (60, None, None, None, None, 6)}[a]
        got = (e["seasons"], e["shift_at"], e["shift"], e["cull_at"], None, f["items"])
        if c["seed"] != s or got != want:
            bad.append((a, s, got, want))
        if a == "cull":
            kk = kof(s)
            spec = ",".join(f"{k}={kk[k]}" for k in KINDS)
            if e["cull"] != spec:
                bad.append((a, s, e["cull"], spec))
    for a in ("shift", "cull", "base", "cull20"):
        rows = A[(a, s)].raw
        if a != "base" and max(t for t, _ in rows) != 599:
            bad.append((a, s, "last season", max(t for t, _ in rows)))
    fl = max(t for t, _ in A[("founders6", s)].raw)
    if fl != 59 and any(A[("founders6", s)].raw[(fl, k)]["alive"] != "0" for k in KINDS if (fl, k) in A[("founders6", s)].raw) \
            and not all(A[("founders6", s)].alive[k].get(fl + 1, 0) == 0 for k in KINDS):
        bad.append(("founders6", s, "last season", fl))
    fends[s] = fl
    ev = [l.rstrip("\n").split("\t") for l in open(f"{C3}/shift-{s}/events.txt")][1:]
    if not (len(ev) == 1 and ev[0][0] == "shift" and int(ev[0][2]) == TS[s] and '"value": 6' in ev[0][4]):
        bad.append(("shift events", s, ev))
    # V0 on raw seasons.txt: shift and cull rows before T equal the baseline's
    for a in ("shift", "cull"):
        d0 = sum(1 for (t, k), r in A[(a, s)].raw.items() if t < TS[s]
                 and any(A[("base", s)].raw[(t, k)][c] != v for c, v in r.items() if c in A[("base", s)].raw[(t, k)]))
        if d0:
            bad.append((a, s, "pre-T rows differ", d0))
    d1 = sum(1 for key, r in OB[s].items() if key[0] < TS[s] and OS[s].get(key) != r)
    if d1:
        bad.append(("own", s, "pre-T own rows differ", d1))
    # own.txt against the committed seasons.txt: alive, and deaths = starved + aged
    for arm, o in (("base", OB[s]), ("shift", OS[s])):
        mism = sum(1 for (t, k), r in o.items() if int(r["alive"]) != A[(arm, s)].alive[k].get(t, 0))
        dm = sum(1 for (t, k), r in o.items() if t >= 1 and int(r["starved"]) + int(r["aged"]) != A[(arm, s)].deaths[k].get(t, 0))
        if mism or dm:
            bad.append((arm, s, "own.txt vs seasons.txt alive/deaths mismatches", mism, dm))
print(f"    30 C3 arm configs (10 shift, 10 cull, 10 founders6) + 10 cull20 + 10 base read; shift/cull/cull20 tables 0..599,")
print(f"    founders6 0..59 or to the season both faunas are extinct ({ {s: e for s, e in fends.items() if e != 59} }); shift events = one food.items=6 row from T; V0 raw pre-T rows (shift, cull) and pre-T own rows;")
print(f"    (V0 compares the columns the baseline carries; RBT-90's seasons.txt has no mean_age/max_age)")
print(f"    own.txt (base and shift) alive = seasons.txt alive and starved + aged = seasons.txt deaths (season >= 1).")
print(f"    problems found: {len(bad)}" + ("" if not bad else "  " + repr(bad[:8])))
print()

# ------------------------------------------------------------------ P2
print("P2  THE ARITHMETIC (lesson 3)")
print("  score.py builds it from base-SEED/own.txt over [T-40, T): food, work = means over each season's SURVIVORS;")
print("  price = food/2 (linear in density, work unchanged); paired prediction = price(designed) - price(co-evolved);")
print("  compared with the AXIS (seasons.txt mean_lifetime_score, a lifetime mean over the living, extinct = 0).")
print("  Pre-onset only: score.py reads own.txt rows in range(T-40, T) (by construction, code read). score.py was committed at 3f8dfc7 (19:40 UTC),")
print("  after the arms (last arm merge 19:30); its FORM is §4's, registered at c456dd0 (13:03) before any arm.")
obs = [a - b for a, b in zip(rs("shift", H), rs("shift", D))]


def price(s, k, lo=-40, col="food"):
    return om(OB[s], k, TS[s] + lo, TS[s], col) / 2


variants = {}
for lo in (-10, -20, -40, -60, -100):
    variants[f"survivors' food, [T{lo}, T)"] = [price(s, D, lo) - price(s, H, lo) for s in SEEDS]
# axis-scale: the axis's own pre-T level against own.txt's food - work; price rescaled to the axis
ratio = {k: [] for k in KINDS}
for s in SEEDS:
    for k in KINDS:
        ax = wm("base", s, k, -40, 0)
        on = om(OB[s], k, TS[s] - 40, TS[s], "net_survivors")
        ratio[k].append(ax / on)
print(f"  scale check, pre-T [T-40, T): axis level / own.txt season net, per seed: co-evolved {per(ratio[H], 2)}, designed {per(ratio[D], 2)}")
variants["axis-scaled price (price x axis/own-net, [T-40, T))"] = [price(s, D) * r2 - price(s, H) * r1 for s, r1, r2 in zip(SEEDS, ratio[H], ratio[D])]
# linearity: the gross-food ratio shift/base in the first seasons after T, before selection can act (same individuals)
rho = {k: [] for k in KINDS}
for s in SEEDS:
    for k in KINDS:
        fs = osum(OS[s], k, TS[s], TS[s] + 3, "food") / 3
        fb = osum(OB[s], k, TS[s], TS[s] + 3, "food") / 3
        rho[k].append(fs / fb)
print(f"  LINEARITY: gross food per survivor, shift / base, seasons [T, T+3) (the same robots; post-onset but pre-selection):")
print(f"    co-evolved {per(rho[H], 3)} mean {st.fmean(rho[H]):.3f};  designed {per(rho[D], 3)} mean {st.fmean(rho[D]):.3f}  (linear = 0.500)")
for w in (1, 5, 10):
    r_ = {k: st.fmean(osum(OS[s], k, TS[s], TS[s] + w, "food") / osum(OB[s], k, TS[s], TS[s] + w, "food") for s in SEEDS) for k in KINDS}
    print(f"    window [T, T+{w}): co-evolved {r_[H]:.3f}, designed {r_[D]:.3f}")
pre_alive = {k: sorted({int(OB[s][(t, k)]['alive']) for s in SEEDS for t in range(TS[s] - 100, TS[s])}) for k in KINDS}
print(f"    pre-onset data cannot test linearity: alive over [T-100, T) takes the values {pre_alive[H]} (co-evolved), "
      f"{pre_alive[D]} (designed); group size 4 throughout; food items 12 throughout")
variants["empirical density response rho, [T, T+3) (post-onset, pre-selection)"] = [
    om(OB[s], D, TS[s] - 40, TS[s], "food") * (1 - rd) - om(OB[s], H, TS[s] - 40, TS[s], "food") * (1 - rh)
    for s, rh, rd in zip(SEEDS, rho[H], rho[D])]
# extinction-consistent: score.py's own unchanged-gait net says the designed population is below basal on 10/10, i.e.
# an unchanged designed population cannot persist; under extinct = 0 its recovery R-shift is then -(its base level)
unch_d = [om(OB[s], D, TS[s] - 40, TS[s], "food") / 2 - om(OB[s], D, TS[s] - 40, TS[s], "work") for s in SEEDS]
variants["extinction-consistent: unchanged designed gait below basal -> extinct -> axis 0"] = [
    wm("base", s, D, TR, TR + RE) - price(s, H) for s in SEEDS]
print()
print(f"  {'prediction for two unchanged populations':78s} {'arithmetic':>30s}   residual (observed - arithmetic)")
for name, v in variants.items():
    print(f"  {name:78s} {ci(v):>30s}   {ci([o - a for o, a in zip(obs, v)])}")
vals = [st.fmean(v) for n, v in variants.items() if not n.startswith("extinction")]
print(f"  observed paired effect (registered, extinct = 0): {ci(obs)}")
print(f"  spread of the linear/scale/window/empirical predictions: {min(vals):+.3f} to {max(vals):+.3f}; residual "
      f"{st.fmean(obs) - max(vals):+.3f} to {st.fmean(obs) - min(vals):+.3f}")
print(f"  unchanged-gait designed net < 0.25 on {sum(u < R.BASAL for u in unch_d)}/10 (score.py); yet the designed fauna was NOT")
print(f"  extinct by T+160 on {len(NON)}/10 ({NON}): the unchanged population the linear arithmetic describes is not the one")
print(f"  that survived; the residual compares the observed arm with an unchanged population that the same arithmetic says")
print(f"  could not have persisted.")
print()

# ------------------------------------------------------------------ P3
print("P3  EXTINCTION CODING (Arm.x: 0 from the first alive = 0 season on; RBT-92 Amendment 2, the 13:10 ruling)")
for s in SEEDS:
    e = extinct_at(s, D)
    print(f"    {s:>4}: designed extinct at {('T+' + str(e - TS[s])) if e else '-':>6}; recovery seasons at 0: "
          f"{sum(1 for t in range(TS[s] + TR, TS[s] + TR + RE) if A[('shift', s)].alive[D].get(t, 0) == 0):>3}/100; paired {obs[SEEDS.index(s)]:+.3f}")
pe = [obs[SEEDS.index(s)] for s in EXT]
pn = [obs[SEEDS.index(s)] for s in NON]
arith = variants["survivors' food, [T-40, T)"]
print(f"  paired effect on the {len(EXT)} extinct seeds {EXT}: {ci(pe)}")
print(f"  paired effect on the {len(NON)} surviving seeds {NON}: {ci(pn)}")
print(f"  share of the summed paired effect carried by the extinct seeds: {sum(pe) / sum(obs):.0%}")
print(f"  residual on extinct seeds {ci([obs[SEEDS.index(s)] - arith[SEEDS.index(s)] for s in EXT])}; "
      f"on surviving seeds {ci([obs[SEEDS.index(s)] - arith[SEEDS.index(s)] for s in NON])}")


def recode(fill):
    """designed shift series with extinct seasons re-coded by fill(s, t) (None: drop those seasons from the mean)."""
    out = {}
    for s in SEEDS:
        a = A[("shift", s)]
        x = dict(a.x[D])
        for t in range(TS[s], 600):
            if a.alive[D].get(t, 0) == 0:
                x[t] = fill(s, t)
        out[s] = x
    return out


def rs_masked(x):
    v = []
    for s in SEEDS:
        ts = [t for t in range(TS[s] + TR, TS[s] + TR + RE) if x[s][t] is not None]
        v.append(st.fmean(x[s][t] for t in ts) - wm("base", s, D, TR, TR + RE))
    return v


codings = {
    "0 (registered)": rs("shift", D),
    "unchanged-gait net, food/2 - work, pre-T (RBT-99 F5's alternative)": rs_masked(recode(lambda s, t: unch_d[SEEDS.index(s)])),
    "-0.25 (a dead fauna pays basal and earns nothing)": rs_masked(recode(lambda s, t: -R.BASAL)),
    "extinct seasons dropped (living seasons only)": rs_masked(recode(lambda s, t: None)),
}
print("  designed R-shift, the paired effect, the residual and the shift R-body class under other codings of the extinct seasons:")
for name, v in codings.items():
    pair = [a - b for a, b in zip(rs("shift", H), v)]
    rb = [st.fmean(A[("shift", s)].x[H][t] for t in range(TS[s] + TR, TS[s] + TR + RE)) - (v[i] + wm("base", s, D, TR, TR + RE))
          for i, s in enumerate(SEEDS)]
    n, m, sd, hw = R.stat(rb)
    print(f"    {name:66s} paired {ci(pair)}; residual {st.fmean(pair) - st.fmean(arith):+.3f}; "
          f"R-body {m:+.3f} r {hw:.3f} {sum(x > 0 for x in rb)}/10")
excl = [obs[SEEDS.index(s)] for s in NON]
print(f"    extinct seeds excluded (post hoc, n = {len(NON)}): paired {ci(excl)}; residual "
      f"{ci([obs[SEEDS.index(s)] - arith[SEEDS.index(s)] for s in NON])}")
print()

# ------------------------------------------------------------------ P4
print("P4  POWER OF THE RESIDUAL (+0.017)")
res = [o - a for o, a in zip(obs, arith)]
n, m, sd, hw = R.stat(res)
t975, t80 = 2.262, 0.883
print(f"  residual {ci(res)}; its own sd {sd:.3f} -> t(9) half-width {hw:.3f}; minimum detectable residual (two-sided 5%,")
print(f"  80% power, n = 10): (t.975 + t.80) x sd / sqrt(10) = {(t975 + t80) * sd / math.sqrt(10):.3f}")
nulls = {}
for arm in ("cull", "cull20"):
    nulls[arm] = [a - b for a, b in zip(rs(arm, H), rs(arm, D))]
    print(f"  matched null, {arm:6s} - base paired R-body (no price, arithmetic 0): {ci(nulls[arm])}; RMS "
          f"{math.sqrt(st.fmean(x * x for x in nulls[arm])):.3f}; MDE at that sd {(t975 + t80) * R.stat(nulls[arm])[2] / math.sqrt(10):.3f}")
print(f"  the arithmetic prediction itself is +{st.fmean(arith):.3f}: the design could detect a response difference only if it")
print(f"  exceeded about {(t975 + t80) * sd / math.sqrt(10) / st.fmean(arith):.1f}x the whole arithmetic effect")
print()

# ------------------------------------------------------------------ P5
print("P5  A/A-LIKE SPREAD FROM THE COMMITTED CULL AND CULL20 CONTRASTS (recovery window)")
for arm in ("cull", "cull20"):
    for k in KINDS:
        v = rs(arm, k)
        sel = v if arm == "cull20" else [x for x, s in zip(v, SEEDS) if kof(s)[k] > 0]
        print(f"  {arm:6s} - base, {k:12s} per fauna: RMS {math.sqrt(st.fmean(x * x for x in sel)):.3f} (n = {len(sel)})")
    v = nulls[arm]
    print(f"  {arm:6s} - base, R-body (paired, the scale of +0.138): RMS {math.sqrt(st.fmean(x * x for x in v)):.3f}, "
          f"sd {R.stat(v)[2]:.3f}, mean {st.fmean(v):+.3f}")
aa = math.sqrt(st.fmean(x * x for x in nulls["cull"] + nulls["cull20"]))
print(f"  pooled paired A/A-like RMS (20 seed-contrasts): {aa:.3f} -> SE of a 10-seed mean {aa / math.sqrt(10):.3f}; "
      f"+0.138 is {st.fmean(obs) / (aa / math.sqrt(10)):.1f} SE; the residual +0.017 is {st.fmean(res) / (aa / math.sqrt(10)):.1f} SE")
print(f"  placebo.txt's A/A reference, RMS of R-cull20 PER FAUNA (0.077), is on the wrong scale for a paired R-body; "
      f"the paired scale is {math.sqrt(st.fmean(x * x for x in nulls['cull20'])):.3f}")
print(f"  per-seed paired values within one paired A/A unit ({aa:.3f}) of 0: "
      f"{[(s, round(o, 3)) for s, o in zip(SEEDS, obs) if abs(o) < aa]}")
print()

# ------------------------------------------------------------------ P6
print("P6  D AT 7/10: PER-SEED MARGINS TO THE TRIGGERS (designed; co-evolved trips none)")


def trig(s, k):
    tr = wm("shift", s, k, 0, TR)
    rc = wm("shift", s, k, TR, TR + RE)
    ma = min(A[("shift", s)].alive[k].get(t, 0) for t in range(TS[s], TS[s] + 160))
    return tr, rc, ma


dseeds = []
for s in SEEDS:
    tr, rc, ma = trig(s, D)
    isd = tr < R.BASAL or rc < R.BASAL or ma < R.FLOOR
    dseeds.append(isd)
    print(f"    {s:>4}: transient {tr:+.3f} ({tr - R.BASAL:+.3f}), recovery {rc:+.3f} ({rc - R.BASAL:+.3f}), min alive {ma:>2} "
          f"({ma - R.FLOOR:+d}) -> {'D' if isd else 'not D'}")
print(f"  D's test: {sum(dseeds)}/10.  The three not-D seeds sit 0.14-0.19 above both income triggers and 13-48 robots")
print(f"  above the floor; the nearest D seeds to NOT firing are those tripped by the floor alone with living-mean income > 0.25.")
b = lambda n, k, p: math.comb(n, k) * p ** k * (1 - p) ** (n - k)
for p in (0.7, 0.8):
    print(f"  binomial, per-seed p = {p}: P(>= 8/10) = {sum(b(10, k, p) for k in range(8, 11)):.3f}; P(<= 7/10) = {sum(b(10, k, p) for k in range(0, 8)):.3f}")
random.seed(100)
for sj in (0.077, 0.11):
    hits = 0
    for _ in range(4000):
        c = 0
        for s in SEEDS:
            tr, rc, ma = trig(s, D)
            c += (tr + random.gauss(0, sj) < R.BASAL or rc + random.gauss(0, sj) < R.BASAL or ma < R.FLOOR)
        hits += c >= 8
    print(f"  jitter, income triggers only (alive held), N(0, {sj}): D's count >= 8 in {hits / 4000:.1%} of draws")
print()

# ------------------------------------------------------------------ P7
print("P7  SIGN GUARD (RBT-92 F6 illustration: per-seed values jittered by N(0, s), guard ceil(0.8n) = 8)")
rb_shift = [R.rbody(A[("shift", s)], TS[s] + TR, TS[s] + TR + RE) for s in SEEDS]
for label, v in (("R-body shift (the class)", rb_shift), ("paired shift - base", obs)):
    for sj in (0.05, 0.077, 0.11):
        k8 = sum(sum(x + random.gauss(0, sj) > 0 for x in v) >= 8 for _ in range(4000))
        print(f"    {label:26s} s {sj:.3f}: >= 8/10 positive in {k8 / 4000:.1%}")
print()

# ------------------------------------------------------------------ P8
print("P8  THE ESTABLISHED CO-EVOLVED POPULATION, RECOVERY WINDOW: what 'paid its way' rests on")
for s in SEEDS:
    lo, hi = TS[s] + TR, TS[s] + TR + RE
    ran = osum(OS[s], H, lo, hi, "ran")
    stv = osum(OS[s], H, lo, hi, "starved")
    ranb = osum(OB[s], H, lo, hi, "ran")
    stvb = osum(OB[s], H, lo, hi, "starved")
    ns, ub = om(OS[s], H, lo, hi, "net_survivors"), om(OS[s], H, lo, hi, "net_all_ub")
    w = om(OS[s], H, lo, hi, "work")
    # a starved robot's own net is at least -(its work charge); with the survivors' mean work as a stand-in
    lb = (ran * ns - stv * w) / (ran + stv)
    print(f"    {s:>4}: min alive {min(A[('shift', s)].alive[H].get(t, 0) for t in range(lo, hi))}; starved share of runners "
          f"shift {stv / (ran + stv):.3f} (base {stvb / (ranb + stvb):.3f}); survivors {ns:+.3f}, all-runner UPPER bound {ub:+.3f}, "
          f"all-runner value if the starved ate nothing (approx.) {lb:+.3f}")
print("  net_all_ub is an UPPER bound (own_table.py: '< 0.25 means below basal for certain'); above 0.25 it certifies nothing.")
print()

# ------------------------------------------------------------------ P9
print("P9  FOUNDERS6: co-evolved alive by season (every 5th, and 55-59), and the season-59 threshold (>= 12)")
for s in SEEDS:
    al = A[("founders6", s)].alive[H]
    print(f"    {s:>4}: " + " ".join(f"{al.get(t, 0)}" for t in list(range(0, 55, 5)) + list(range(55, 60)))
    + f"   min over 40-59 {min(al.get(t, 0) for t in range(40, 60))}, max {max(al.get(t, 0) for t in range(40, 60))}")
print("  the established fauna HOLDS on 10/10 (min alive 60; survivors' net >= 0.25), so 'contrast on c/(f - h)' equals")
print("  founders FAIL on f - h: '7/7' is the founders count restated, not a second outcome.")
