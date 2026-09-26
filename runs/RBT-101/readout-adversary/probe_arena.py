"""RBT-101 readout adversary, the crux (lesson 3): what does flat ground do to an UNCHANGED gait IN THE ARENA, and
what is the observed income change made of?

Reads the restored bulk (lineage.jsonl, one row per living individual per season: food, work (J), last_score =
food - 0.03 * work / 1000) of the ten RBT-90 baselines (ckpt/rbt-90-SEED, 600/600) and the ten shift arms
(ckpt/rbt-101-shift-SEED).  README rule 6: no table is read from a checkpoint; the bulk is, and probe_rederive.txt
shows the bulk regenerates the committed seasons.txt / lineage-last.txt / wiring.txt byte for byte (8/10 shift arms at
600/600; 804 and 805 checkpoints stop at 548 and 599 and agree with the committed tables on that prefix).  Every
season read here is <= T + 160 (<= 518 on 804), so the prefix covers it.

  Z  the zero-response prediction.  In season T every individual in the shift arm is an individual of the baseline
     (C0 plus nothing: births are processed after the season's gains), in the same groups of four, from the same start
     seeds (start_seed_check.txt): the only difference is the terrain.  Per individual, gain(shift) - gain(base) at
     season T is exactly "an unchanged gait on flat ground in the ecology's own arena, crowding, food and collisions
     included".  One draw per individual, 60 per fauna per seed.  Extended to [T, T+10): individuals born before T,
     alive in both arms that season, paired by name (groups can diverge once a death differs; gaits cannot).
  D  the decomposition of the observed change: per season, the mean over the living of food, 0.03 * kJ and
     last_score, shift - base, averaged over each window.  mean_lifetime_score (the axis) is a lifetime mean; by T+60
     every living robot was born after T (max_age 60), so in the recovery window the per-season mean and the axis
     measure the same thing up to age weighting and newborns (a newborn's row carries evals 0 and no bout, and
     mean_lifetime_score counts it at 0; the per-season means here skip it); both are printed.

    python runs/RBT-101/readout-adversary/probe_arena.py BULKDIR > runs/RBT-101/readout-adversary/probe_arena.txt
"""
import json
import math
import os
import statistics as st
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-92"))
import readout as R  # noqa: E402

B = sys.argv[1]
SEEDS, KINDS, TS = R.SEEDS, R.KINDS, R.onsets()
WC = 0.03
LAB = {"holistic": "co-evolved", "conventional": "designed"}


def load(path, smax):
    rows = {}
    for line in open(path):
        r = json.loads(line)
        g = r["generation"]
        if g > smax or "food" not in r:  # a newborn's row (evals 0) played no bout that season
            continue
        rows.setdefault((g, r["population"]), {})[r["name"]] = r
    return rows


def born(rows, kind, T):
    """Names alive at T - 1 (C0); anything present at s >= T that is in C0 was born before T."""
    return set(rows.get((T - 1, kind), {}))


def stat(label, v):
    n, m, sd, hw = R.stat(v)
    return (f"{label:58s} {m:+.4f} [{m - hw:+.4f}, {m + hw:+.4f}] pos {sum(x > 0 for x in v)}/{n}  "
            f"per seed [{', '.join(f'{x:+.3f}' for x in v)}]")


Z = {k: {"gain": [], "food": [], "work": []} for k in KINDS}
Z10 = {k: [] for k in KINDS}
Zn = {k: [] for k in KINDS}
DEC = {w: {k: {"gain": [], "food": [], "work": [], "axis": []} for k in KINDS} for w in ("transient", "recovery")}
WIN = {"transient": (0, 60), "recovery": (60, 160)}
SEASON_T_CHECK = []
for s in SEEDS:
    T = TS[s]
    base = load(f"{B}/base-{s}/lineage.jsonl", T + 160)
    shift = load(f"{B}/shift-{s}/lineage.jsonl", T + 160)
    ab, ash = R.Arm(f"runs/RBT-90/forage-{s}"), R.Arm(f"runs/RBT-101/shift-{s}")
    for k in KINDS:
        c0 = born(base, k, T)
        b, h = base[(T, k)], shift[(T, k)]
        common = sorted(set(b) & set(h))
        SEASON_T_CHECK.append((s, k, len(b), len(h), len(common), all(n in c0 for n in common)))
        for f, fn in (("gain", lambda r: r["last_score"]), ("food", lambda r: r["food"]), ("work", lambda r: WC * r["work"] / 1000)):
            Z[k][f].append(st.fmean(fn(h[n]) - fn(b[n]) for n in common))
        d10, n10 = [], 0
        for t in range(T, T + 10):
            bb, hh = base[(t, k)], shift[(t, k)]
            cm = [n for n in set(bb) & set(hh) if n in c0]
            n10 += len(cm)
            d10 += [hh[n]["last_score"] - bb[n]["last_score"] for n in cm]
        Z10[k].append(st.fmean(d10))
        Zn[k].append(n10)
        for w, (a, e) in WIN.items():
            acc = {"gain": [], "food": [], "work": [], "axis": []}
            for t in range(T + a, T + e):
                for f, fn in (("gain", lambda r: r["last_score"]), ("food", lambda r: r["food"]), ("work", lambda r: WC * r["work"] / 1000)):
                    acc[f].append(st.fmean(fn(r) for r in shift[(t, k)].values()) - st.fmean(fn(r) for r in base[(t, k)].values()))
                acc["axis"].append(ash.x[k][t] - ab.x[k][t])
            for f in acc:
                DEC[w][k][f].append(st.fmean(acc[f]))

print(__doc__.split("\n\n")[0])
print(f"seeds {SEEDS}; T {[TS[s] for s in SEEDS]}")
print()
print("Z0 season T membership: (seed, fauna, alive base, alive shift, common, all common in C0)")
print("   " + "  ".join(f"{s}/{k[0]}:{a}/{b}/{c}/{'C0' if ok else 'NOT-C0'}" for s, k, a, b, c, ok in SEASON_T_CHECK))
print()
print("Z  ZERO-RESPONSE: the same individuals, same groups of four, same start seeds, season T, shift - base (items/season)")
for k in KINDS:
    print("   " + stat(f"{LAB[k]:10s} gain (= the axis unit)", Z[k]["gain"]))
    print("   " + stat(f"{LAB[k]:10s}   food", Z[k]["food"]))
    print("   " + stat(f"{LAB[k]:10s}   work cost (0.03 x kJ)", Z[k]["work"]))
zp = [a - b for a, b in zip(Z["holistic"]["gain"], Z["conventional"]["gain"])]
print("   " + stat("paired (co-evolved - designed), season T", zp))
print()
print("Z10 the same over [T, T+10): pre-T-born individuals alive in both arms that season, paired by name")
for k in KINDS:
    print("   " + stat(f"{LAB[k]:10s} gain", Z10[k]) + f"  pairs per seed {Zn[k]}")
z10p = [a - b for a, b in zip(Z10["holistic"], Z10["conventional"])]
print("   " + stat("paired, [T, T+10)", z10p))
print()
for w in ("transient", "recovery"):
    a, e = WIN[w]
    print(f"D  DECOMPOSITION of the observed change, {w} [T+{a}, T+{e}): per-season mean over the living, shift - base")
    for k in KINDS:
        for f in ("axis", "gain", "food", "work"):
            print("   " + stat(f"{LAB[k]:10s} {'axis (mean_lifetime_score)' if f == 'axis' else f}", DEC[w][k][f]))
    print("   " + stat("paired axis (= readout's event - base)", [a - b for a, b in zip(DEC[w]["holistic"]["axis"], DEC[w]["conventional"]["axis"])]))
    print("   " + stat("paired per-season gain", [a - b for a, b in zip(DEC[w]["holistic"]["gain"], DEC[w]["conventional"]["gain"])]))
    print()
obs = [a - b for a, b in zip(DEC["recovery"]["holistic"]["axis"], DEC["recovery"]["conventional"]["axis"])]
print("R  RESIDUAL of the observed recovery paired contrast against the zero-response predictions")
print("   " + stat("observed - Z (season T)", [o - p for o, p in zip(obs, zp)]))
print("   " + stat("observed - Z10 ([T, T+10))", [o - p for o, p in zip(obs, z10p)]))
for k in KINDS:
    print("   " + stat(f"{LAB[k]:10s} observed R-shift - Z10", [o - p for o, p in zip(DEC["recovery"][k]["axis"], Z10[k])]))
    print(f"   {LAB[k]:10s} observed / Z10, ratio of means: {st.fmean(DEC['recovery'][k]['axis']) / st.fmean(Z10[k]):.2f}")
obs_g = [a - b for a, b in zip(DEC["recovery"]["holistic"]["gain"], DEC["recovery"]["conventional"]["gain"])]
print("   like for like (per-season gain observed in the recovery window against the per-season gain Z10 predicts):")
print("   " + stat("paired: observed gain - Z10", [o - p for o, p in zip(obs_g, z10p)]))
for k in KINDS:
    print("   " + stat(f"{LAB[k]:10s} observed gain - Z10", [o - p for o, p in zip(DEC["recovery"][k]["gain"], Z10[k])]))
print(f"   per-seed correlation of Z10 paired with observed paired: r = {st.correlation(z10p, obs):+.3f}")
print(f"   per-seed correlation of Z (season T) paired with observed paired: r = {st.correlation(zp, obs):+.3f}")
print()
print("TC TIME COURSE of the per-season gain, shift - base, mean over the ten seeds per 10-season bin; 'old' = born before T")
print("   (in C0), 'new' = born at or after T; each cell is the difference of the two arms' means over the living in that class")
print("   bin        co-evolved all   old      new     | designed all   old      new     | paired all | old share (shift, co-ev/designed)")
TCB = {}
for s in SEEDS:
    T = TS[s]
    base = load(f"{B}/base-{s}/lineage.jsonl", T + 199 if s != 804 else 547)
    shift = load(f"{B}/shift-{s}/lineage.jsonl", T + 199 if s != 804 else 547)
    for k in KINDS:
        c0 = born(base, k, T)
        for j in range(20):
            cell = {"all": [], "old": [], "new": [], "share": []}
            for t in range(T + 10 * j, T + 10 * j + 10):
                if (t, k) not in base or (t, k) not in shift:
                    continue
                for cls, pick in (("all", lambda n: True), ("old", lambda n: n in c0), ("new", lambda n: n not in c0)):
                    hb = [r["last_score"] for n, r in base[(t, k)].items() if pick(n)]
                    hs = [r["last_score"] for n, r in shift[(t, k)].items() if pick(n)]
                    if hb and hs:
                        cell[cls].append(st.fmean(hs) - st.fmean(hb))
                cell["share"].append(sum(n in c0 for n in shift[(t, k)]) / len(shift[(t, k)]))
            TCB[(s, k, j)] = {c: (st.fmean(v) if v else None) for c, v in cell.items()}


def mb(k, j, c):
    v = [TCB[(s, k, j)][c] for s in SEEDS if (s, k, j) in TCB and TCB[(s, k, j)][c] is not None]
    return (st.fmean(v), len(v)) if v else (float("nan"), 0)


for j in range(20):
    h = [mb("holistic", j, c) for c in ("all", "old", "new")]
    d = [mb("conventional", j, c) for c in ("all", "old", "new")]
    p = [TCB[(s, "holistic", j)]["all"] - TCB[(s, "conventional", j)]["all"] for s in SEEDS if (s, "holistic", j) in TCB and TCB[(s, "holistic", j)]["all"] is not None and TCB[(s, "conventional", j)]["all"] is not None]
    fmt = lambda x: "   n/a " if x[1] == 0 else f"{x[0]:+.3f}"
    print(f"   T+{10 * j:3d}..{10 * j + 9:3d}  {fmt(h[0])}   {fmt(h[1])}   {fmt(h[2])}  |  {fmt(d[0])}   {fmt(d[1])}   {fmt(d[2])}  |  {st.fmean(p):+.3f}    |  "
          f"{mb('holistic', j, 'share')[0]:.2f} / {mb('conventional', j, 'share')[0]:.2f}")

print()
print("S  THE SPREAD OF UNCHANGED-GAIT PREDICTIONS for the paired recovery contrast (observed -0.458, the axis), and each residual")
probe = {}
import re
for l in open("runs/RBT-101/flat_probe.txt"):
    if not l.startswith("#") and "\t" in l:
        f = l.split("\t")
        probe[(int(f[0]), f[1])] = float(re.search(r"flat-random ([-+][0-9.]+)", l).group(1))
pp = [probe[(s, "holistic")] - probe[(s, "conventional")] for s in SEEDS]
rows = [("solo probe, season-300 bests, halved for four to a group (PREREGISTRATION section 10's own discount)", [0.5 * x for x in pp]),
        ("solo probe, season-300 bests, as arith.py uses it", pp),
        ("the arena, the C0 population in its own groups of four, [T, T+10) (Z10)", z10p),
        ("the arena, season T only (Z)", zp)]
for lab, v in rows:
    n, m, sd, hw = R.stat(v)
    res = [o - x for o, x in zip(obs, v)]
    n2, m2, sd2, hw2 = R.stat(res)
    print(f"   {lab}")
    print(f"       predicted {m:+.3f} [{m - hw:+.3f}, {m + hw:+.3f}];  residual {m2:+.3f} [{m2 - hw2:+.3f}, {m2 + hw2:+.3f}] pos {sum(x > 0 for x in res)}/10;"
          f"  per-seed r(pred, obs) {st.correlation(v, obs):+.2f}")
print("   per fauna, the solo probe against the arena's unchanged population (Z10), items or gain per season:")
for k in KINDS:
    pv = [probe[(s, k)] for s in SEEDS]
    print(f"       {LAB[k]:10s} probe {st.fmean(pv):+.3f}   arena Z10 {st.fmean(Z10[k]):+.3f}   observed R-shift {st.fmean(DEC['recovery'][k]['axis']):+.3f}"
          f"   per-seed r(probe, Z10) {st.correlation(pv, Z10[k]):+.2f}")
