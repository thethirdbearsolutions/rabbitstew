"""RBT-92 readout adversary: probes on the committed tables only (no ckpt, no bulk; runs/README.md rule 6).

Reads what readout.py reads (seasons.txt, events.txt, config.json, cull-k-SEED.txt, onset.txt, and the RBT-90
baselines) through readout.py's own Arm / rbody / classify / stat, so a disagreement is a finding about the
report, not about a second parser.  Measures; tunes nothing.  Sections:

  P1  inputs: every merged arm read, seed and event of each arm checked against its config and onset.txt
  P2  platform: V0 at byte level on the raw rows, and the per-fauna stream separation after T
  P3  the pre-registered class rule applied to arms and windows with no shift in them
  P4  the paired contrast (shift - base) and "holds up" for both bodies, at the level r and the paired r
  P5  ecology A/A-like references in the committed data (small random culls, cull20) against the effects
  P6  recovery time: the h threshold, the hold rule, and the inertia of a lifetime-mean column
  P7  the tail window
  P8  V3: what the table shows at T in cull20

    python runs/RBT-92/readout-adversary/probe_readout.py > runs/RBT-92/readout-adversary/probe_readout.txt
"""
import json
import math
import os
import statistics
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-92"))
import readout as R  # noqa: E402

SEEDS = R.SEEDS
TS = R.onsets()
BEF, TR, RC, TL = R.BEFORE if hasattr(R, "BEFORE") else 100, 60, 100, 40
WIN = {"before": (-100, 0), "transient": (0, 60), "recovery": (60, 160), "tail": (160, 200)}
K = {s: R.cull_k_of(s) for s in SEEDS}


def arm_of(arm, s):
    if arm == "cull" and not any(K[s].values()):
        return R.Arm(R.arm_path("base", s))
    return R.Arm(R.arm_path(arm, s))


ARMS = {(a, s): arm_of(a, s) for a in R.ARMS for s in SEEDS}


def w(s, name):
    a, b = WIN[name]
    return TS[s] + a, TS[s] + b


def fwin(arm, kind, a, b):
    return statistics.fmean(arm.x[kind][t] for t in range(a, b))


def line(label, vals):
    n, m, sd, hw = R.stat(vals)
    pos = sum(1 for v in vals if v > 0)
    return f"{label}: mean {m:+.4f}  95% t({n - 1}) [{m - hw:+.4f}, {m + hw:+.4f}]  sd {sd:.4f}  positive {pos}/{n}"


def rms(v):
    return math.sqrt(statistics.fmean(x * x for x in v)) if v else float("nan")


def cls(vals):
    n, m, sd, hw = R.stat(vals)
    pos = sum(1 for v in vals if v > 0)
    neg = sum(1 for v in vals if v < 0)
    # the class tests E1/D/E2 are 0/10 in every arm (alive 60 throughout, incomes > 0.25), so they are passed as 0;
    # checked below in P3
    return R.classify(n, m, hw, pos, neg, 0, 0, 0), m, hw, pos


print("RBT-92 readout adversary: probes on committed tables (readout.py's own parser)")
print()

# ---------------------------------------------------------------- P1
print("P1 INPUTS")
n_dirs = 0
for s in SEEDS:
    T = TS[s]
    for a in ("shift", "cull", "cull20"):
        p = R.arm_path(a, s)
        if a == "cull" and not any(K[s].values()):
            print(f"  {s:>4} {a:6s}: k = 0/0, no directory expected: {'ABSENT (ok)' if not os.path.isdir(p) else 'PRESENT (?)'}; the baseline is read")
            continue
        n_dirs += 1
        cfg = json.load(open(os.path.join(p, "config.json")))
        eco = cfg.get("ecology", {})
        ev = eco.get("shift_at") if a == "shift" else eco.get("cull_at")
        want = {"shift": "group-size=8", "cull": ",".join(f"{k}={K[s][k]}" for k in ("holistic", "conventional")),
                "cull20": "holistic=20,conventional=20"}[a]
        got = eco.get("shift") if a == "shift" else eco.get("cull")
        arm = ARMS[(a, s)]
        culls = {(pp, ss): len(nn) for (pp, ss), nn in arm.culled.items()}
        ok = cfg["seed"] == s and ev == T and got == want and arm.last == 599
        if a != "shift":
            want_c = {k: (20 if a == "cull20" else K[s][k]) for k in R.KINDS}
            ok &= all(culls.get((k, T), 0) == want_c[k] for k in R.KINDS) and all(ss == T for (_, ss) in culls)
        print(f"  {s:>4} {a:6s}: config seed {cfg['seed']} at {ev} '{got}'  seasons 0..{arm.last}  culls {culls or '-'}  {'OK' if ok else 'MISMATCH'}")
    b = ARMS[("base", s)]
    cfgb = json.load(open(os.path.join(R.arm_path("base", s), "config.json")))
    print(f"  {s:>4} base  : runs/RBT-90/forage-{s} config seed {cfgb['seed']}  seasons 0..{b.last}  {'OK' if cfgb['seed'] == s and b.last == 599 else 'MISMATCH'}")
print(f"  arm directories read: {n_dirs} (27 expected) + 10 baselines; seeds {len(SEEDS)}/10")
print()

# ---------------------------------------------------------------- P2
print("P2 PLATFORM: raw-text identity on the columns both tables carry (the RBT-90 baselines have no mean_age/max_age)")
COLS = ("alive", "births", "deaths", "mean_lifetime_score", "best_lifetime_score")
untouched = []
for s in SEEDS:
    T = TS[s]
    braw = ARMS[("base", s)].raw
    out = []
    for a in ("shift", "cull", "cull20"):
        if a == "cull" and not any(K[s].values()):
            continue
        araw = ARMS[(a, s)].raw
        same = lambda t, k: all(araw[(t, k)][c] == braw[(t, k)][c] for c in COLS)
        pre = all(same(t, k) for t in range(T) for k in R.KINDS)
        first = {k: next((t for t in range(600) if not same(t, k)), None) for k in R.KINDS}
        if a == "cull":
            for k in R.KINDS:
                if K[s].get(k, 0) == 0:
                    untouched.append((s, k, first[k]))
        out.append(f"{a}: pre-T identical {'yes' if pre else 'NO'}, first differing season hol {first['holistic']} conv {first['conventional']}")
    print(f"  {s:>4} T={T}: " + ";  ".join(out))
print(f"  a fauna with k = 0 in a run cull arm: first season differing from the baseline {untouched}")
print("  (None = byte-identical text through season 599)")
print()

# ---------------------------------------------------------------- P3
print("P3 THE CLASS RULE (RBT-89 section 9 as amended; readout.py's classify(), r = the arm's own t(9) half-width)")
print("   applied to arms and windows the rule was not written for, to see what it measures")
alive_min = min(ARMS[(a, s)].alive[k][t] for a in R.ARMS for s in SEEDS for k in R.KINDS
                for t in range(TS[s] - 100, TS[s] + 200))
inc_min = {k: min(fwin(ARMS[(a, s)], k, *w(s, wn)) for a in R.ARMS for s in SEEDS for wn in ("transient", "recovery"))
           for k in R.KINDS}
print(f"   class tests: min alive over [T-100, T+200) in every arm {alive_min}; min window income holistic "
      f"{inc_min['holistic']:.3f}, conventional {inc_min['conventional']:.3f} (D/E threshold 0.25): E1, D, E2 are 0/10 everywhere")
for a in R.ARMS:
    for wn in ("before", "recovery", "tail"):
        vals = [R.rbody(ARMS[(a, s)], *w(s, wn)) for s in SEEDS]
        c, m, hw, pos = cls(vals)
        print(f"   {a:6s} {wn:9s}: R-body {m:+.4f}  r {hw:.4f}  positive {pos}/10  -> {c}")
vals = [R.rbody(ARMS[("shift", s)], *w(s, "recovery")) - R.rbody(ARMS[("base", s)], *w(s, "recovery")) for s in SEEDS]
c, m, hw, pos = cls(vals)
print(f"   shift - base (paired) recovery: {m:+.4f}  r {hw:.4f}  positive {pos}/10  -> {c}")
print()
print("   placebo onsets on the baseline alone (no event anywhere): the rule on base R-body over [T'+60, T'+160)")
fire = 0
tot = 0
for off in range(-200, 41, 10):
    vals = [R.rbody(ARMS[("base", s)], TS[s] + off + 60, TS[s] + off + 160) for s in SEEDS]
    c, m, hw, pos = cls(vals)
    tot += 1
    fire += c.startswith("A")
    print(f"     T' = T{off:+4d}: {m:+.4f}  r {hw:.4f}  positive {pos}/10  -> {c[:1]}")
print(f"   class A fires on {fire}/{tot} placebo onsets with no shift")
print()

# ---------------------------------------------------------------- P4
print("P4 THE PAIRED CONTRAST AND 'HOLDS UP'")
rsh = {k: [fwin(ARMS[("shift", s)], k, *w(s, "recovery")) - fwin(ARMS[("base", s)], k, *w(s, "recovery")) for s in SEEDS] for k in R.KINDS}
diff = [a - b for a, b in zip(rsh["holistic"], rsh["conventional"])]
r_level = R.stat([R.rbody(ARMS[("shift", s)], *w(s, "recovery")) for s in SEEDS])[3]
print("   " + line("holistic R-shift recovery", rsh["holistic"]))
print("   " + line("designed R-shift recovery", rsh["conventional"]))
print("   " + line("difference (holistic - designed) = R-body(shift) - R-body(base)", diff))
for k in R.KINDS:
    n, m, sd, hw = R.stat(rsh[k])
    print(f"   {k:12s}: 'holds up' at the pre-registered bar -r = -{r_level:.4f}: mean {m:+.4f} -> {'yes' if m >= -r_level else 'no'};"
          f"  interval lower end {m - hw:+.4f} -> {'yes' if m - hw >= -r_level else 'no'};"
          f"  at its own paired r {hw:.4f} (not pre-registered): {'yes' if m >= -hw else 'no'}")
n, m, sd, hw = R.stat(diff)
print(f"   equivalence of the differential at 0.10: |mean| + r_paired = {abs(m) + hw:.4f} -> "
      f"{'inside +-0.10' if abs(m) + hw < 0.10 else 'NOT inside +-0.10: neither an effect nor its absence is shown'}")
print()

# ---------------------------------------------------------------- P5
print("P5 ECOLOGY A/A-LIKE REFERENCES IN THE COMMITTED DATA")
print("   (a) a random cull of k robots of one fauna diverges that fauna from its baseline at T, exactly as a challenge")
print("       arm does, with an intervention whose expected effect on the mean is ~0. Per fauna, window mean of")
print("       x_cull - x_base, on every fauna-seed with k > 0:")
aa = {wn: [] for wn in ("transient", "recovery", "tail")}
aa_small = {wn: [] for wn in aa}
for s in SEEDS:
    for k in R.KINDS:
        kk = K[s].get(k, 0)
        if kk <= 0:
            continue
        row = []
        for wn in aa:
            d = fwin(ARMS[("cull", s)], k, *w(s, wn)) - fwin(ARMS[("base", s)], k, *w(s, wn))
            aa[wn].append(d)
            if kk <= 3:
                aa_small[wn].append(d)
            row.append(f"{wn} {d:+.4f}")
        print(f"     {s:>4} {k:12s} k={kk:<2d}: " + "  ".join(row))
for wn in aa:
    print(f"   RMS over {len(aa[wn])} fauna-seeds, {wn:9s}: {rms(aa[wn]):.4f}   (k <= 3 only, n={len(aa_small[wn])}: {rms(aa_small[wn]):.4f})")
print("   (b) the same per fauna for cull20 - base (a third culled; a random cull, expected ~0 on the mean), all 20 fauna-seeds:")
aa20 = {wn: [fwin(ARMS[("cull20", s)], k, *w(s, wn)) - fwin(ARMS[("base", s)], k, *w(s, wn)) for s in SEEDS for k in R.KINDS] for wn in aa}
for wn in aa20:
    print(f"   RMS {wn:9s}: {rms(aa20[wn]):.4f}   mean {statistics.fmean(aa20[wn]):+.4f}")
print("   (c) R-body level: R-body(arm) - R-body(base) per seed, recovery window (the A/A analogue of the +0.032):")
for a in ("cull", "cull20", "shift"):
    ss = [s for s in SEEDS if a != "cull" or any(K[s].values())]
    v = [R.rbody(ARMS[(a, s)], *w(s, "recovery")) - R.rbody(ARMS[("base", s)], *w(s, "recovery")) for s in ss]
    print(f"     {a:6s} on {len(ss)} seeds: per seed [{', '.join(f'{x:+.3f}' for x in v)}]  RMS {rms(v):.4f}  sd {statistics.stdev(v):.4f}")
print("   (d) the sign guard: shift recovery R-body per seed, and the smallest |R-body| among the positives")
sv = {s: R.rbody(ARMS[("shift", s)], *w(s, "recovery")) for s in SEEDS}
print("     " + "  ".join(f"{s}:{v:+.3f}" for s, v in sv.items()))
pos = sorted(v for v in sv.values() if v > 0)
print(f"     positive {len(pos)}/10 (guard 8/10: zero margin); positives below the (a) recovery RMS {rms(aa['recovery']):.3f}: "
      f"{sum(1 for v in pos if v < rms(aa['recovery']))}; below the (c) cull RMS: see (c)")
bv = {s: R.rbody(ARMS[("base", s)], *w(s, "recovery")) for s in SEEDS}
cv = {s: R.rbody(ARMS[("cull", s)], *w(s, "recovery")) for s in SEEDS}
print(f"     base positive {sum(v > 0 for v in bv.values())}/10; cull positive {sum(v > 0 for v in cv.values())}/10 "
      f"(seeds that change sign base -> cull: {[s for s in SEEDS if (bv[s] > 0) != (cv[s] > 0)]}, with k {[K[s] for s in SEEDS if (bv[s] > 0) != (cv[s] > 0)]})")
print()

# ---------------------------------------------------------------- P6
print("P6 RECOVERY TIME: h, the 20-season hold, and the column's inertia")
print("   mean_lifetime_score is the living robots' mean of score_sum / evals over each robot's whole life")
print("   (rabbitstew/ecology.py _record), so at T + d a robot born before T still carries its pre-T seasons.")
lag1 = []
for s in SEEDS:
    b = ARMS[("base", s)]
    for k in R.KINDS:
        xs = [b.x[k][t] for t in range(TS[s] - 100, TS[s])]
        m = statistics.fmean(xs)
        num = sum((xs[i] - m) * (xs[i + 1] - m) for i in range(len(xs) - 1))
        den = sum((x - m) ** 2 for x in xs)
        lag1.append(num / den)
print(f"   lag-1 autocorrelation of x over [T-100, T), 20 fauna-seeds: median {statistics.median(lag1):+.3f}, range {min(lag1):+.3f} to {max(lag1):+.3f}")


def hk(s, k, mult):
    pre = [ARMS[("base", s)].x[k][t] for t in range(TS[s] - 100, TS[s])]
    return mult * statistics.stdev(pre)


print("   shift arm, paired |x_shift - x_base| over [T, T+20) as a fraction of h (the 20 seasons that decide d = 0):")
for k in R.KINDS:
    fr = []
    for s in SEEDS:
        h = hk(s, k, 2)
        fr.append(max(abs(ARMS[("shift", s)].x[k][t] - ARMS[("base", s)].x[k][t]) for t in range(TS[s], TS[s] + 20)) / h)
    print(f"     {k:12s}: " + "  ".join(f"{s}:{f:.2f}" for s, f in zip(SEEDS, fr)))
print("   paired recovery d (readout.py's recovery(), run 20) at h = m x SD(pre), per arm and fauna: d = 0 count / 'none' count")
for a in ("shift", "cull", "cull20"):
    for k in R.KINDS:
        row = []
        for mult in (0.5, 1.0, 1.5, 2.0):
            ds = []
            for s in SEEDS:
                base, arm = ARMS[("base", s)], ARMS[(a, s)]
                ds.append(R.recovery(arm.x[k], lambda t, b=base, kk=k: b.x[kk][t], hk(s, k, mult), TS[s]))
            row.append(f"h={mult}SD: 0 on {sum(d == 0 for d in ds)}/10, none {sum(d is None for d in ds)}")
        print(f"     {a:6s} {k:12s}: " + ";  ".join(row))
print("   'ever left the band' (any season in [T, T+160) with |x_arm - x_base| > h = 2 SD), holistic / designed:")
for a in ("shift", "cull", "cull20"):
    row = []
    for k in R.KINDS:
        left = sum(1 for s in SEEDS if any(abs(ARMS[(a, s)].x[k][t] - ARMS[("base", s)].x[k][t]) > hk(s, k, 2)
                                           for t in range(TS[s], TS[s] + 160)))
        row.append(f"{k} {left}/10")
    print(f"     {a:6s}: " + "  ".join(row))
print()

# ---------------------------------------------------------------- P7
print("P7 THE TAIL WINDOW [T+160, T+200)")
d_tail = [R.rbody(ARMS[("shift", s)], *w(s, "tail")) - R.rbody(ARMS[("base", s)], *w(s, "tail")) for s in SEEDS]
d_tail_c = [R.rbody(ARMS[("cull20", s)], *w(s, "tail")) - R.rbody(ARMS[("base", s)], *w(s, "tail")) for s in SEEDS]
print("   " + line("R-body(shift) - R-body(base), tail", d_tail))
print("   " + line("R-body(cull20) - R-body(base), tail (reference)", d_tail_c))
b_tr = [R.rbody(ARMS[("base", s)], *w(s, "tail")) - R.rbody(ARMS[("base", s)], *w(s, "recovery")) for s in SEEDS]
print("   " + line("base R-body tail - base R-body recovery (the base's own drift)", b_tr))
ss = [s for s in SEEDS if any(K[s].values())]
d_tail_cu = [R.rbody(ARMS[("cull", s)], *w(s, "tail")) - R.rbody(ARMS[("base", s)], *w(s, "tail")) for s in ss]
print(f"   R-body(cull) - R-body(base), tail, {len(ss)} seeds with k > 0: RMS {rms(d_tail_cu):.4f}")
print()

# ---------------------------------------------------------------- P8
print("P8 V3: THE CULL IN THE TABLE AT T (cull20 against base; alive / births / deaths in season T)")
for s in SEEDS:
    T = TS[s]
    row = []
    for k in R.KINDS:
        c, b = ARMS[("cull20", s)].raw[(T, k)], ARMS[("base", s)].raw[(T, k)]
        row.append(f"{k[:4]} alive {c['alive']}/{b['alive']} births {c['births']}/{b['births']} deaths {c['deaths']}/{b['deaths']}")
    print(f"   {s:>4} T={T}: " + ";  ".join(row))
print("   (cull20/base.  If the culled 20 are counted in deaths and births refill them in season T, the")
print("    end-of-season alive cannot dip: the designer's account of the alive half of V3.)")
print()
print("P5(e) SIGN-GUARD FRAGILITY: a replicate of the shift arm differs per seed from this one by about the A/A")
print("   difference RMS of (c).  Monte Carlo (fixed seed 92), 20000 draws: shift recovery R-body per seed + N(0, s),")
print("   the class rule re-applied with its own r.  An illustration of the guard's margin, not a test.")
import random  # noqa: E402
rng = random.Random(92)
obs = [sv[s] for s in SEEDS]
for sd_aa in (0.05, 0.08, 0.11):
    hit = {"A": 0, "F": 0, "other": 0}
    for _ in range(20000):
        v = [x + rng.gauss(0, sd_aa) for x in obs]
        c = cls(v)[0][:1]
        hit[c if c in hit else "other"] += 1
    print(f"   s = {sd_aa:.2f}: class A on {hit['A'] / 200:.1f}% of replicates, F on {hit['F'] / 200:.1f}%, other {hit['other'] / 200:.1f}%")
print()
print("P6(b) THE SEEDS READ AS 'NEVER LEFT THE BAND': shift arm, |x_shift - x_base| > h (2 SD, readout.py's h) in [T, T+160)")
print("   per seed: paired recovery d | first season out of the band (relative to T) | seasons out of 160")
for k in R.KINDS:
    for s in SEEDS:
        h = hk(s, k, 2)
        base, arm = ARMS[("base", s)], ARMS[("shift", s)]
        d = R.recovery(arm.x[k], lambda t, b=base, kk=k: b.x[kk][t], h, TS[s])
        out = [t - TS[s] for t in range(TS[s], TS[s] + 160) if abs(arm.x[k][t] - base.x[k][t]) > h]
        print(f"   {k:12s} {s:>4}: d {R.fmtd(d):>4} | first out T+{out[0] if out else '-'} | {len(out)}/160 out")
