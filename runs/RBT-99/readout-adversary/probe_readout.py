"""RBT-99 readout adversary: probes on the committed tables only (no ckpt, no bulk; runs/README.md rule 6).

Reads what readout.sh feeds readout.py (RBT-99's shift and cull arms and cull-k files, RBT-92's cull20 arms, the RBT-90
baselines, RBT-92's onset.txt) through readout.py's own Arm / rbody / classify / stat, plus runs/RBT-99/price.txt and
the pre-registered runs/RBT-99/adversary/kj_baseline.txt (committed 13:21, before any arm).  Measures; tunes nothing.

  P1  inputs: every arm read, seed / event / k of each arm checked against config.json, events.txt and onset.txt
  P2  arithmetic: each body's own price (0.05 x its pre-onset kJ) against its R-shift; the paired effect against the
      price difference; what the data can and cannot attribute
  P3  extinction coded as 0 income: the weight of the extinct seeds, the post-hoc 7-seed subset, the registered
      D partition, and extinct seasons coded at the arithmetic income instead of 0
  P4  the null: the paired contrast against the registered random-cull null, with and without the capped seeds
  P5  the class rule on the no-event base, on placebo onsets, on cull20 and on the paired contrasts (RBT-92 F2)
  P6  A/A-like spread from the committed cull and cull20 contrasts; the sign guard's margin (RBT-92 F5, F6)
  P7  recovery time: d = 0 seeds leave the band?  'none' against the price (RBT-92 F4)
  P8  the turnover guard and 'holds up' at the level r and the paired r (RBT-92 F7)
  P9  the lifetime-mean lag: robots born before T still alive in the recovery window
  P10 price.txt against the pre-registered kJ probe (the late-gate deviation)
  P11 the scored predictions: Brier re-computed, and the rows that could not have failed

    python runs/RBT-99/readout-adversary/probe_readout.py > runs/RBT-99/readout-adversary/probe_readout.txt
"""
import csv
import json
import math
import os
import random
import statistics
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)

# the arm directory readout.sh assembles, by symlink, from committed files only
TMP = tempfile.mkdtemp()
SEEDS0 = [801, 804, 805, 806, 807, 1, 2, 3, 4, 7]
for s in SEEDS0:
    for a in ("shift", "cull"):
        if os.path.exists(f"runs/RBT-99/{a}-{s}"):
            os.symlink(os.path.abspath(f"runs/RBT-99/{a}-{s}"), f"{TMP}/{a}-{s}")
    if os.path.exists(f"runs/RBT-99/cull-k-{s}.txt"):
        os.symlink(os.path.abspath(f"runs/RBT-99/cull-k-{s}.txt"), f"{TMP}/cull-k-{s}.txt")
    for a in ("cull20", "base"):
        if os.path.exists(f"runs/RBT-92/{a}-{s}"):
            os.symlink(os.path.abspath(f"runs/RBT-92/{a}-{s}"), f"{TMP}/{a}-{s}")
os.environ["RBT92_ARM_DIR"] = TMP
os.environ["RBT92_ONSET"] = os.path.join(ROOT, "runs/RBT-92/onset.txt")
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-92"))
import readout as R  # noqa: E402

SEEDS = R.SEEDS
TS = R.onsets()
K = {s: R.cull_k_of(s) for s in SEEDS}
HO, CO = "holistic", "conventional"
WIN = {"before": (-100, 0), "transient": (0, 60), "recovery": (60, 160), "tail": (160, 200)}


def arm_of(arm, s):
    if arm == "cull" and not any(K[s].values()):
        return R.Arm(R.arm_path("base", s))
    return R.Arm(R.arm_path(arm, s))


A = {(a, s): arm_of(a, s) for a in R.ARMS for s in SEEDS}


def w(s, name, off=0):
    a, b = WIN[name]
    return TS[s] + off + a, TS[s] + off + b


def fwin(arm, kind, a, b):
    return statistics.fmean(arm.x[kind][t] for t in range(a, b))


def rsh(arm1, arm2, kind, s, name="recovery"):
    a, b = w(s, name)
    return fwin(A[(arm1, s)], kind, a, b) - fwin(A[(arm2, s)], kind, a, b)


def rb(arm, s, name="recovery", off=0):
    a, b = w(s, name, off)
    return R.rbody(A[(arm, s)], a, b)


def line(label, vals):
    n, m, sd, hw = R.stat(vals)
    pos = sum(1 for v in vals if v > 0)
    return f"{label}: mean {m:+.4f}  95% t({n - 1}) [{m - hw:+.4f}, {m + hw:+.4f}]  sd {sd:.4f}  positive {pos}/{n}"


def rms(v):
    return math.sqrt(statistics.fmean(x * x for x in v)) if v else float("nan")


def cls(vals, dz=0):
    n, m, sd, hw = R.stat(vals)
    pos = sum(1 for v in vals if v > 0)
    neg = sum(1 for v in vals if v < 0)
    return R.classify(n, m, hw, pos, neg, 0, dz, 0).split(" --")[0], m, hw, pos, n


def extinct(s, kind=CO, arm="shift"):
    T = TS[s]
    return any(A[(arm, s)].alive[kind][t] == 0 for t in range(T, T + 160))


price = {(int(r["seed"]), r["fauna"]): float(r["price"])
         for r in csv.DictReader((l for l in open("runs/RBT-99/price.txt") if "\t" in l), delimiter="\t")}
pkj = {(int(r["seed"]), r["fauna"]): float(r["kJ"])
       for r in csv.DictReader((l for l in open("runs/RBT-99/price.txt") if "\t" in l), delimiter="\t")}
kjb = {}
for l in open("runs/RBT-99/adversary/kj_baseline.txt"):
    f = l.split()
    if len(f) > 5 and f[0].isdigit() and f[1] in (HO, CO):
        kjb[(int(f[0]), f[1])] = (f[2], float(f[5]))

EXT = [s for s in SEEDS if extinct(s)]
CAP = [s for s in SEEDS if K[s].get(CO, 0) >= A[("base", s)].alive[CO][TS[s] - 1]]
SURV = [s for s in SEEDS if s not in EXT]

print("RBT-99 readout adversary: probes on committed tables (readout.py's own parser, the arm set readout.sh assembles)")
print(f"seeds {SEEDS}; designed extinct before T+160 in the shift arm: {EXT}; designed cull capped (k >= alive at T-1): {CAP}")
print()

# ---------------------------------------------------------------- P1
print("P1 INPUTS (what readout.sh links, checked against each arm's own files)")
nd = 0
for s in SEEDS:
    T = TS[s]
    out = []
    for a in ("shift", "cull", "cull20"):
        p = os.path.realpath(R.arm_path(a, s))
        c = json.load(open(os.path.join(p, "config.json")))
        e = c["ecology"]
        ok = c["seed"] == s and c["generations"] == 600
        if a == "shift":
            ok &= e["shift_at"] == T and e["shift"] == "work-cost=0.08" and e["cull"] is None
            ok &= A[(a, s)].shift_at == T and not A[(a, s)].culled
        else:
            want = f"holistic={K[s][HO]},conventional={K[s][CO]}" if a == "cull" else "holistic=20,conventional=20"
            ok &= e["cull_at"] == T and e["cull"] == want and e["shift"] is None
            got = {k: len(v) for (k, t), v in A[(a, s)].culled.items() if t == T}
            exp = {k: min(K[s][k] if a == "cull" else 20, A[("base", s)].alive[k][T - 1]) for k in (HO, CO)}
            ok &= all(got.get(k, 0) == exp[k] for k in (HO, CO)) and all(t == T for (_, t) in A[(a, s)].culled)
        seasons = sorted({t for t in A[(a, s)].x[HO]})
        ok &= seasons[0] == 0 and A[(a, s)].last == 599
        nd += 1
        out.append(f"{a} {'ok' if ok else 'MISMATCH'} ({os.path.relpath(p, ROOT)})")
    b = A[("base", s)]
    out.append(f"base seasons 0..{b.last}")
    print(f"  {s:>4} T={T} k={K[s]}: " + "; ".join(out))
print(f"  arm directories read: {nd} (10 shift + 10 cull from runs/RBT-99, 10 cull20 from runs/RBT-92) + {len(SEEDS)} baselines;"
      f" seeds read {len(SEEDS)}/10; none dropped or substituted")
# V0 on raw text for the RBT-99 arms, and the per-fauna stream separation after T
print("  V0 at raw-text level (alive, births, deaths, mean and best score), every season < T, RBT-99 arms:")
cols = ("alive", "births", "deaths", "mean_lifetime_score", "best_lifetime_score")
for s in SEEDS:
    T = TS[s]
    res = []
    for a in ("shift", "cull"):
        bad = sum(1 for (t, k), r in A[("base", s)].raw.items() if t < T
                  and any(r.get(c) != A[(a, s)].raw.get((t, k), {}).get(c) for c in cols if c in r))
        first = {k: min((t for t in range(T - 5, 600) if any(A[("base", s)].raw.get((t, k), {}).get(c)
                                                                 != A[(a, s)].raw.get((t, k), {}).get(c) for c in cols)),
                        default=None) for k in (HO, CO)}
        res.append(f"{a}: {bad} pre-T rows differ, first diff hol {first[HO]} conv {first[CO]}")
    print(f"    {s:>4} T={T}  " + ";  ".join(res))
print()

# ---------------------------------------------------------------- P2
print("P2 ARITHMETIC: each body's own price (0.05 x its own pre-onset kJ, price.txt) against its R-shift (recovery)")
print("   Income is gain - work_cost x kJ per season; at unchanged gait the shift takes exactly 0.05 x kJ from every")
print("   robot. So an unchanged population's R-shift is -price, and the paired (co-evolved - designed) R-shift of")
print("   two unchanged populations is price_designed - price_coevolved. net = R-shift + price: what is not arithmetic.")
print("  seed  price hol  price con  arith paired  R-shift hol  R-shift con  obs paired  net hol  net con  net con-hol"
      "  share hol  share con  base con inc  arith con inc")
rows = []
for s in SEEDS:
    ph, pc = price[(s, HO)], price[(s, CO)]
    h, c = rsh("shift", "base", HO, s), rsh("shift", "base", CO, s)
    a, b = w(s, "recovery")
    base_c = fwin(A[("base", s)], CO, a, b)
    rows.append(dict(s=s, ph=ph, pc=pc, h=h, c=c, nh=h + ph, nc=c + pc, bc=base_c))
    print(f"  {s:>4}  {ph:9.3f}  {pc:9.3f}  {pc - ph:+12.3f}  {h:+11.3f}  {c:+11.3f}  {h - c:+10.3f}  {h + ph:+7.3f}  {c + pc:+7.3f}"
          f"  {c + pc - h - ph:+11.3f}  {(h + ph) / ph:9.2f}  {(c + pc) / pc:9.2f}  {base_c:12.3f}  {base_c - pc:+13.3f}"
          + ("  (designed extinct)" if s in EXT else ""))


def sub(key, S):
    return [r[key] if isinstance(key, str) else key(r) for r in rows if r["s"] in S]


for lab, S in (("all ten", SEEDS), ("7 designed-surviving (post hoc)", SURV)):
    print(f"  {lab}:")
    print("    " + line("arithmetic paired prediction, price_des - price_coev", sub(lambda r: r["pc"] - r["ph"], S)))
    print("    " + line("observed paired, R-shift hol - R-shift con (= R-body shift - base)", sub(lambda r: r["h"] - r["c"], S)))
    print("    " + line("observed - arithmetic (= net hol - net con)", sub(lambda r: r["nh"] - r["nc"], S)))
    print("    " + line("net, co-evolved", sub("nh", S)))
    print("    " + line("net, designed", sub("nc", S)))
    print("    " + line("observed paired / arithmetic paired (ratio per seed)", sub(lambda r: (r["h"] - r["c"]) / (r["pc"] - r["ph"]), S)))
    mh = statistics.fmean(sub("nh", S)) / statistics.fmean(sub("ph", S))
    mc = statistics.fmean(sub("nc", S)) / statistics.fmean(sub("pc", S))
    print(f"    share of price recovered (mean net / mean price): co-evolved {mh:.3f}, designed {mc:.3f}")
    print("    " + line("share recovered, co-evolved - designed (per seed)", sub(lambda r: r["nh"] / r["ph"] - r["nc"] / r["pc"], S)))
print("  designed arithmetic income at 0.08 (its base recovery income - its price): "
      f"{min(r['bc'] - r['pc'] for r in rows):+.3f} .. {max(r['bc'] - r['pc'] for r in rows):+.3f}; below 0.25 on "
      f"{sum(r['bc'] - r['pc'] < R.BASAL for r in rows)}/10, below 0 on {sum(r['bc'] - r['pc'] < 0 for r in rows)}/10")
print("  co-evolved arithmetic income at 0.08: "
      + (lambda v: f"{min(v):+.3f} .. {max(v):+.3f}; below 0.25 on {sum(x < R.BASAL for x in v)}/10")(
          [fwin(A[("base", s)], HO, *w(s, "recovery")) - price[(s, HO)] for s in SEEDS]))
print("  transient window, same decomposition (the lifetime mean lags here, so arithmetic overstates the transient price):")
print("    " + line("observed paired, transient", [rsh("shift", "base", HO, s, "transient") - rsh("shift", "base", CO, s, "transient") for s in SEEDS]))
print()

# ---------------------------------------------------------------- P3
print("P3 EXTINCTION CODED AS 0 INCOME (13:10 ruling): weight of the extinct seeds")
d = {s: rb("shift", s) - rb("base", s) for s in SEEDS}
print("  per seed shift - base R-body, recovery: " + ", ".join(f"{s} {d[s]:+.3f}" for s in SEEDS))
print("  ranked: " + ", ".join(f"{s}{'*' if s in EXT else ''} {d[s]:+.3f}" for s in sorted(SEEDS, key=lambda s: -d[s])) + "   (* extinct)")
tot = sum(d.values())
print(f"  the three extinct seeds carry {sum(d[s] for s in EXT) / tot:.1%} of the summed paired effect (3 of 10 seeds)")
print("  " + line("all ten (registered)", [d[s] for s in SEEDS]))
print("  " + line("7 designed-surviving (post hoc: defined on the outcome, not registered)", [d[s] for s in SURV]))
NOND = [801, 804, 805, 1, 4, 7]
print("  " + line("6 seeds where D's designed half did not fire (the registered partition, also outcome-defined)", [d[s] for s in NOND]))
print("  " + line("5 seeds neither extinct nor cull-capped", [d[s] for s in SURV if s not in CAP]))
# extinct seasons coded at the arithmetic income: the base's designed income less the designed price, season by season
alt = []
for s in SEEDS:
    a, b = w(s, "recovery")
    sh, bs = A[("shift", s)], A[("base", s)]
    v = []
    for t in range(a, b):
        xc = sh.x[CO][t] if sh.alive[CO][t] > 0 else bs.x[CO][t] - price[(s, CO)]
        v.append((sh.x[HO][t] - xc) - (bs.x[HO][t] - bs.x[CO][t]))
    alt.append(statistics.fmean(v))
print("  " + line("all ten, extinct seasons coded at the unchanged-gait income (base - price) instead of 0", alt))
print("  class of the shift arm's R-body, recovery, on the 7 surviving seeds: %s (mean %+.4f, r %.4f, %d/%d positive)"
      % cls([rb("shift", s) for s in SURV]))
print("  class of the shift arm's R-body, recovery, on the 6 non-D seeds: %s (mean %+.4f, r %.4f, %d/%d positive)"
      % cls([rb("shift", s) for s in NOND]))
print("  the registered pre-registration text names no 'designed-surviving' subset; its only partition is D's test (8/10 guard)")
print()

# ---------------------------------------------------------------- P4
print("P4 THE NULL: paired contrast against the registered random-cull null (shift - cull), recovery")
for s in SEEDS:
    print(f"  {s:>4} k hol {K[s][HO]:>2} con {K[s][CO]:>2} (alive {A[('base', s)].alive[CO][TS[s] - 1]}): "
          f"R-null hol {rsh('shift', 'cull', HO, s):+.3f} con {rsh('shift', 'cull', CO, s):+.3f}  "
          f"R-body shift - cull {rb('shift', s) - rb('cull', s):+.3f}" + ("  [capped: designed null = extinction]" if s in CAP else ""))
nc = [s for s in SEEDS if s not in CAP]
print("  " + line("R-body shift - cull, all ten (capped seeds read as-is: shift against extinction)", [rb("shift", s) - rb("cull", s) for s in SEEDS]))
print("  " + line("R-body shift - cull, 7 uncapped (option (a): capped seeds n/a)", [rb("shift", s) - rb("cull", s) for s in nc]))
print("  " + line("R-body shift - cull, 5 uncapped and not extinct", [rb("shift", s) - rb("cull", s) for s in nc if s not in EXT]))
print("  " + line("designed R-null, 7 uncapped", [rsh("shift", "cull", CO, s) for s in nc]))
print("  " + line("designed R-null + price (the null carries no price), 7 uncapped", [rsh("shift", "cull", CO, s) + price[(s, CO)] for s in nc]))
print("  " + line("co-evolved R-null, all ten (= R-shift on the 3 k=0 seeds)", [rsh("shift", "cull", HO, s) for s in SEEDS]))
print("  " + line("R-cull designed, 7 uncapped (what a k = 27-43 random cull does to designed income)", [rsh("cull", "base", CO, s) for s in nc]))
print("  arithmetic paired prediction against the null (price_des - price_coev) is the same as against the base;")
print("  " + line("R-body shift - cull minus arithmetic, 7 uncapped", [rb("shift", s) - rb("cull", s) - (price[(s, CO)] - price[(s, HO)]) for s in nc]))
print()

# ---------------------------------------------------------------- P5
print("P5 THE CLASS RULE ON ARMS AND WINDOWS WITHOUT THE EVENT (RBT-92 F2), and on the paired contrasts")
for lab, vals in (("base, recovery", [rb("base", s) for s in SEEDS]),
                  ("base, before", [rb("base", s, "before") for s in SEEDS]),
                  ("cull20, recovery", [rb("cull20", s) for s in SEEDS]),
                  ("cull, recovery (3 capped seeds: designed extinct)", [rb("cull", s) for s in SEEDS]),
                  ("shift, recovery (the verdict)", [rb("shift", s) for s in SEEDS]),
                  ("shift - base, paired, recovery", [d[s] for s in SEEDS]),
                  ("shift - base, paired, 7 surviving", [d[s] for s in SURV]),
                  ("shift - cull, paired, 7 uncapped", [rb("shift", s) - rb("cull", s) for s in nc]),
                  ("cull20 - base, paired, recovery", [rb("cull20", s) - rb("base", s) for s in SEEDS])):
    c, m, hw, pos, n = cls(vals)
    print(f"  {lab:48s} mean {m:+.4f}  r {hw:.4f}  positive {pos}/{n}  -> {c}")
pl = []
for off in range(-200, 41, 10):
    vals = [rb("base", s, "recovery", off) for s in SEEDS]
    pl.append((off, cls(vals)))
nA = sum(1 for _, c in pl if c[0].startswith("A"))
print(f"  placebo onsets on the base alone, T' = T{pl[0][0]:+d} .. T{pl[-1][0]:+d} step 10, R-body over [T'+60, T'+160): "
      f"A on {nA}/{len(pl)}; the rest: " + ", ".join(f"T{o:+d} {c[0][:1]} ({c[3]}/10)" for o, c in pl if not c[0].startswith("A")))
print("  (the base and T are RBT-92's, byte for byte, so this equals RBT-92 F2's 23/25 by construction)")
print()

# ---------------------------------------------------------------- P6
print("P6 A/A-LIKE SPREAD in the committed data, recovery window (RBT-92 F5), and the sign guard (F6)")
sm = [s for s in SEEDS if 1 <= K[s][HO] <= 3]
kp = [s for s in SEEDS if K[s][HO] > 0]
print("  co-evolved cull - base, k 1..3 (%s): RMS %.4f" % (sm, rms([rsh("cull", "base", HO, s) for s in sm])))
print("  co-evolved cull - base, all k > 0 (%s): RMS %.4f" % (kp, rms([rsh("cull", "base", HO, s) for s in kp])))
print("  cull20 - base per fauna, all 20 fauna-seeds: RMS %.4f" % rms([rsh("cull20", "base", k, s) for s in SEEDS for k in (HO, CO)]))
print("  R-body cull20 - base per seed: RMS %.4f, mean %+.4f" % (rms([rb("cull20", s) - rb("base", s) for s in SEEDS]),
                                                           statistics.fmean([rb("cull20", s) - rb("base", s) for s in SEEDS])))
print("  against that ~0.08-0.11 per-seed spread: " + line("shift - base R-body", [d[s] for s in SEEDS]))
print("    per-seed values below 0.11: " + ", ".join(f"{s} {d[s]:+.3f}" for s in SEEDS if d[s] < 0.11))
print("    co-evolved R-shift per seed: " + ", ".join(f"{rsh('shift', 'base', HO, s):+.3f}" for s in SEEDS)
      + f"  RMS {rms([rsh('shift', 'base', HO, s) for s in SEEDS]):.4f}  (the size of the A/A-like spread)")
sv = [rb("shift", s) for s in SEEDS]
print(f"  sign guard: shift R-body positive {sum(v > 0 for v in sv)}/10 against the guard 8; smallest {min(sv):+.3f} (seed "
      f"{SEEDS[sv.index(min(sv))]}); margin 2 seeds")
rng = random.Random(99)
for sd_ in (0.05, 0.08, 0.11):
    for lab, base_vals in (("shift R-body", sv), ("paired shift - base", [d[s] for s in SEEDS])):
        cnt = sum(cls([v + rng.gauss(0, sd_) for v in base_vals])[0].startswith("A") for _ in range(2000))
        print(f"    jitter N(0, {sd_}) per seed, {lab:20s}: class A in {cnt / 2000:.1%} of 2000 draws")
print()

# ---------------------------------------------------------------- P7
print("P7 RECOVERY TIME (RBT-92 F4): does the paired rule's d mean 'recovered'?")
for k in (HO, CO):
    for s in SEEDS:
        T = TS[s]
        base = A[("base", s)]
        pre = [base.x[k][t] for t in range(T - 100, T)]
        h = 2 * statistics.stdev(pre)
        xs = A[("shift", s)].x[k]
        dp = R.recovery(xs, lambda t: base.x[k].get(t, float("nan")), h, T)
        out = [t - T for t in range(T, T + 160) if abs(xs[t] - base.x[k][t]) > h]
        extra = ""
        if k == CO:
            extra = f"  price/h {price[(s, CO)] / h:.1f}"
        else:
            extra = f"  price/h {price[(s, HO)] / h:.1f}"
        print(f"  {k[:4]} {s:>4}: d {R.fmtd(dp):>5}  h {h:.3f}  first out of band T+{out[0] if out else '-':<4} "
              f"seasons out of 160: {len(out):>3}{extra}")
print()

# ---------------------------------------------------------------- P8
print("P8 TURNOVER GUARD AND 'HOLDS UP' (RBT-92 F7)")
kp7 = [s for s in SEEDS if K[s][HO] > 0]
rn = [rsh("shift", "cull", HO, s) for s in kp7]
print("  " + line(f"co-evolved R-null on the {len(kp7)} k>0 seeds {kp7}", rn))
print("  the guard compares |mean| with the level r 0.1832, which is inflated by the designed collapse's between-seed spread")
rs_h = [rsh("shift", "base", HO, s) for s in SEEDS]
rs_c = [rsh("shift", "base", CO, s) for s in SEEDS]
for lab, v in (("co-evolved R-shift", rs_h), ("designed R-shift", rs_c), ("co-evolved R-null (all ten)", [rsh("shift", "cull", HO, s) for s in SEEDS])):
    n, m, sd, hw = R.stat(v)
    print(f"  {lab:28s} mean {m:+.4f}  own paired r {hw:.4f}  lower bound {m - hw:+.4f}  "
          f"holds up at level r (>= -0.1832): {'yes' if m >= -0.1832 else 'no'};  at own paired r: {'yes' if m >= -hw else 'no'}")
rbv = [rb("shift", s) for s in SEEDS]
print(f"  level r without the 3 extinct seeds (t(6) half-width of shift R-body on 7): {R.stat([rb('shift', s) for s in SURV])[3]:.4f}")
print()

# ---------------------------------------------------------------- P9
print("P9 THE LIFETIME-MEAN LAG: robots born before T still alive in the recovery window (shift arm, lineage-last.txt)")
for s in SEEDS:
    T = TS[s]
    arm = A[("shift", s)]
    out = []
    for k in (HO, CO):
        old = [sum(1 for (kk, n), (b, l, _) in arm.ind.items() if kk == k and b < T and b <= t <= l) for t in (T + 30, T + 60, T + 100)]
        out.append(f"{k[:4]} alive-and-born-before-T at T+30/T+60/T+100: {old[0]}/{old[1]}/{old[2]}")
    print(f"  {s:>4}: " + ";  ".join(out))
print()

# ---------------------------------------------------------------- P10
print("P10 price.txt (computed 18:40) against the pre-registered kJ probe (adversary/kj_baseline.txt, committed 13:21)")
print("  seed fauna         price.txt window/kJ     kj_baseline window/kJ   price diff")
for s in SEEDS:
    for k in (HO, CO):
        wb, kb = kjb[(s, k)]
        print(f"  {s:>4} {k:13s} {TS[s] - 40}-{TS[s] - 1} {pkj[(s, k)]:7.3f}      {wb} {kb:7.2f}          {0.05 * (pkj[(s, k)] - kb):+.4f}")
for k in (HO, CO):
    alt_net = [rsh("shift", "base", k, s) + 0.05 * kjb[(s, k)][1] for s in SEEDS]
    print(f"  {k}: net with the pre-registered kJ: mean {statistics.fmean(alt_net):+.4f}; share "
          f"{statistics.fmean(alt_net) / statistics.fmean([0.05 * kjb[(s, k)][1] for s in SEEDS]):.3f}")
alt_ar = [0.05 * (kjb[(s, CO)][1] - kjb[(s, HO)][1]) for s in SEEDS]
print("  " + line("arithmetic paired prediction with the pre-registered kJ", alt_ar))
print()

# ---------------------------------------------------------------- P11
print("P11 SCORING: Brier re-computed from score.txt's 12 binary rows")
bs = [(0.35, 0), (0.15, 0), (0.10, 0), (0.80, 1), (0.85, 1), (0.12, 1), (0.55, 1), (0.65, 0), (0.65, 0), (0.70, 1), (0.60, 1), (0.65, 1)]
print(f"  Brier {statistics.fmean([(p - o) ** 2 for p, o in bs]):.4f} over {len(bs)} rows (score.txt: 0.201)")
co_inc = [fwin(A[("shift", s)], HO, *w(s, "recovery")) for s in SEEDS]
co_ar = [fwin(A[("base", s)], HO, *w(s, "recovery")) - price[(s, HO)] for s in SEEDS]
print(f"  'co-evolved survives 10/10': alive min {min(min(A[('shift', s)].alive[HO][t] for t in range(TS[s], TS[s] + 160)) for s in SEEDS)}"
      f", recovery income {min(co_inc):+.3f}..{max(co_inc):+.3f}; at unchanged gait {min(co_ar):+.3f}..{max(co_ar):+.3f}: "
      "clears 0.25 by arithmetic alone on 10/10")
dr = [sum(A[("shift", s)].deaths[CO][t] for t in range(TS[s], TS[s] + 60)) / sum(A[("base", s)].deaths[CO][t] for t in range(TS[s], TS[s] + 60)) for s in SEEDS]
print(f"  'designed transient deaths >= 2x base': ratio {min(dr):.2f}..{max(dr):.2f}")
print("  'L(T+160) shift - cull within +-0.10': scored HIT in score.txt and REPORT.md section 6 on an UNVALIDATED readout (V3 FAIL)")
