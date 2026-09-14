"""RBT-80 three-seed report, AMENDED after the 10:18 adversary post.

Assembles the report from the per-seed depth readouts
(docs/artifacts/RBT-80-seed{A,B,C}-depths.txt, from scripts/rbt80_predicates.py)
plus each run's history.json and lineage.jsonl. No simulation.

Changes from the version posted at 9020cb2, all four required by the
coordinator's 10:40 comment:

  (a) the carrier predicate is reported under the DEPTH-1, DEPTH-2 and DEPTH-4
      steering terms side by side. Depth 1 is identically zero on every genome
      in this ticket -- the motif RBT-65 installs is routed through a global
      interneuron because the encoding forbids the direct one, so its
      nose-to-Effector path is length TWO and depth 1 cannot see it. Depth 2 is
      the shortest path that contains the installed motif and is the primary
      here; depth 4 is the original, kept beside it.
  (b) section 4 is computed at the PLATEAU 250-299, not at season 299, which
      the report's own section 5 rules out.
  (c) section 4b adds carriers against non-carriers INSIDE the seeded arm.
  (d) the series sections 1, 3 and 5 rest on are committed separately by
      scripts/rbt80_series.py; the carrier COUNT is read from column 2 of the
      readout rather than recovered from the rounded fraction.

The "gradient-dominant" column is dropped: |a| > |c| is the sign test
s_L * s_R < 0 with no magnitude in it (RBT-81), and seed C's control arm --
0.000 carriers throughout -- read 0.18 gradient-dominant under it.

Usage: ./v/bin/python scripts/rbt80_report.py
"""
import json, os, re, numpy as np

SEEDS = {"A": "seedA", "B": "seedB", "C": "seedC"}
ROOT = "runs/RBT-80"
ARMS = ("seeded", "control", "drift")
DEPTHS = (1, 2, 4)
PRIMARY_DEPTH = 2
PLATEAU = range(250, 300)
# Corrected no-selection floor (scripts/crossover_floor.py, commit 1ad0d93):
# structural retention r per reproduction x alignment survival at inversion q.
R_STRUCT, Q_INV = 0.989, 0.076
# column offsets in the depths readout: season, alive, then 3 per depth,
# then inverted(d2), balance>0, opposed<0, median rho
COL = {d: 2 + 3 * i for i, d in enumerate(DEPTHS)}
COL_INV = 2 + 3 * len(DEPTHS)


def floor_at(d):
    return (R_STRUCT ** d) * 0.5 * (1 + (1 - 2 * Q_INV) ** d)


def per_season(seed_label):
    """{arm: {season: {"alive", "inverted", depth: (count, fraction, median)}}}."""
    path = f"docs/artifacts/RBT-80-{SEEDS[seed_label]}-depths.txt"
    if not os.path.exists(path):
        return None
    txt = open(path).read()
    out = {}
    for arm in ARMS:
        if f"### {arm}" not in txt:
            continue
        blk = txt.split(f"### {arm}")[1].split("###")[0]
        d = {}
        for line in blk.splitlines():
            if not re.match(r"^\|\s*\d+\s*\|", line):
                continue
            p = [x.strip() for x in line.strip("|").split("|")]
            row = {"alive": int(p[1]), "inverted": int(p[COL_INV])}
            for dep in DEPTHS:
                c = COL[dep]
                row[dep] = (int(p[c]), float(p[c + 1]), float(p[c + 2]))
            d[int(p[0])] = row
        out[arm] = d
    return out


def conv_history(seed_label, arm):
    return [e for e in json.load(open(f"{ROOT}/{SEEDS[seed_label]}/{arm}/history.json"))["history"]
            if e["population"] == "conventional"]


def depth_of(seed_label, arm):
    return sum(e["births"] for e in conv_history(seed_label, arm)) / 60.0


def demography(seed_label, arm):
    rec = {}
    for line in open(f"{ROOT}/{SEEDS[seed_label]}/{arm}/lineage.jsonl"):
        r = json.loads(line)
        if r["population"] == "conventional":
            rec.setdefault(r["generation"], []).append(r)
    if 290 not in rec or 299 not in rec:
        return None
    base = {x["name"] for x in rec[290]}
    return (np.mean([x["age"] for x in rec[290]]), np.mean([x["age"] for x in rec[299]]),
            len({x["name"] for x in rec[299]} - base))


def plateau_mean(ps, arm, dep, field=1):
    return float(np.mean([v[dep][field] for k, v in ps[arm].items() if k in PLATEAU]))


if __name__ == "__main__":
    have = [s for s in SEEDS if per_season(s)]
    PS = {s: per_season(s) for s in have}
    print(f"RBT-80 three-seed report, AMENDED — seeds present: {', '.join(have)}")
    print("Carrier predicate: re-signed steering gain >= +16, under depths 1, 2, 4.\n")

    print("## 0. The predicate, and why depth 1 is empty here\n")
    print("`rabbitstew.analysis.steering_terms` returns the depth-1 term -- the weight on the")
    print("DIRECT nose-to-Effector links -- as the exact gain of a four-link motif. RBT-65's")
    print("motif is not that motif. The encoding rejects a link from one wheel's nose to the")
    print("other wheel's Effector (genotype.py:496; the wheels are siblings, not neighbours),")
    print("so `scripts/genotype_motif.py` routes it through a global tanh interneuron and the")
    print("nose-to-Effector path is length TWO. Measured on the seeded founders:\n")
    print("| quantity | value on every seeded founder |")
    print("|---|---|")
    print("| depth-1 a | +0.000 |")
    print("| depth-1 balance (both noses wired direct) | 0.000 |")
    print("| depth-1 opposed (sign of s_L*s_R) | 0 |")
    print("| depth-2 a | +64.000 = 2w, the installed value |")
    print("\nSo the depth-1 predicate defines no carriers anywhere, in any arm, in any seed,")
    print("and its verdict quantity is 0.000 - 0.000 = +0.000 by construction. It is reported")
    print("because it was asked for, and it is not a reading of this ticket's question.")
    print("Depth 2 is the shortest path sum that contains the installed motif; it is primary.\n")

    print("## 1. Carriage: plateau 250-299 (primary readout), under each depth\n")
    print("| seed | arm | d1 | d2 (PRIMARY) | d4 (original) | realised depth | floor |")
    print("|---|---|---|---|---|---|---|")
    P = {}
    for s in have:
        for arm in ARMS:
            if arm not in PS[s]:
                continue
            vals = {d: plateau_mean(PS[s], arm, d) for d in DEPTHS}
            P[(s, arm)] = vals
            dd = depth_of(s, arm)
            print(f"| {s} | {arm} | {vals[1]:.3f} | {vals[2]:.3f} | {vals[4]:.3f} | "
                  f"{dd:.1f} | {floor_at(dd):.3f} |")

    print("\n## 2. The verdict quantity: seeded minus drift, per seed, never pooled\n")
    print("| seed | readout | d1 | d2 (PRIMARY) | d4 (original) |")
    print("|---|---|---|---|---|")
    prim = {}
    for s in have:
        row = {}
        for d in DEPTHS:
            row[d] = P[(s, "seeded")][d] - P[(s, "drift")][d]
        prim[s] = row
        print(f"| {s} | plateau 250-299 | {row[1]:+.3f} | {row[2]:+.3f} | {row[4]:+.3f} |")
    for s in have:
        row = {d: PS[s]["seeded"][299][d][1] - PS[s]["drift"][299][d][1] for d in DEPTHS}
        print(f"| {s} | season 299 (secondary) | {row[1]:+.3f} | {row[2]:+.3f} | {row[4]:+.3f} |")

    print("\n## 3. Yield: seeded minus control per season, per seed (arm-level)\n")
    print("| seed | seeded mean | control mean | difference | sign |")
    print("|---|---|---|---|---|")
    for s in have:
        a = np.array([e["mean_lifetime_score"] for e in conv_history(s, "seeded")])
        b = np.array([e["mean_lifetime_score"] for e in conv_history(s, "control")])
        n = min(len(a), len(b))
        d = (a[:n] - b[:n]).mean()
        print(f"| {s} | {a[:n].mean():.3f} | {b[:n].mean():.3f} | {d:+.3f} | {'+' if d > 0 else '-'} |")
    print("\nSeries committed at docs/artifacts/RBT-80-series.txt. Within-arm contrast: see")
    print("docs/artifacts/RBT-80-within-arm.txt (measure (c)); the arm-level contrast alone")
    print("cannot separate the compass from the installation.")

    print(f"\n## 4. Loss by inversion vs structural loss, AT THE PLATEAU, depth {PRIMARY_DEPTH}\n")
    print("Season-299 values are shown beside it only to show what moving the readout does;")
    print("section 5 rules season 299 out for the drift arms.\n")
    print("| seed | arm | carriers (plateau) | inverted | lost structurally | "
          "same at s299 | floor prediction |")
    print("|---|---|---|---|---|---|---|")
    for s in have:
        for arm in ("seeded", "drift"):
            if arm not in PS[s]:
                continue
            rows = [v for k, v in PS[s][arm].items() if k in PLATEAU]
            carr = float(np.mean([r[PRIMARY_DEPTH][0] for r in rows]))
            inv = float(np.mean([r["inverted"] for r in rows]))
            alive = float(np.mean([r["alive"] for r in rows]))
            r299 = PS[s][arm][299]
            l299 = r299["alive"] - r299[PRIMARY_DEPTH][0] - r299["inverted"]
            dd = depth_of(s, arm)
            pred = alive * (1 - R_STRUCT ** dd)
            print(f"| {s} | {arm} | {carr:.1f}/{alive:.0f} | {inv:.1f} | "
                  f"{alive - carr - inv:.1f} | {l299} | {pred:.1f} |")

    print("\n## 5. Demographic transient, season 290 -> 299\n")
    print("| seed | arm | mean age 290 | mean age 299 | turnover | "
          f"carriage plateau -> s299 (d{PRIMARY_DEPTH}) |")
    print("|---|---|---|---|---|---|")
    for s in have:
        for arm in ARMS:
            dm = demography(s, arm)
            if not dm:
                continue
            pl = P[(s, arm)][PRIMARY_DEPTH]
            f299 = PS[s][arm][299][PRIMARY_DEPTH][1]
            print(f"| {s} | {arm} | {dm[0]:.1f} | {dm[1]:.1f} | {dm[2]}/60 | "
                  f"{pl:.3f} -> {f299:.3f} ({f299-pl:+.3f}) |")

    print("\n## 6. Verdict by the pre-registered rule\n")
    for d in DEPTHS:
        v = {s: prim[s][d] for s in have}
        n_small = sum(1 for s in have if abs(v[s]) < 0.10)
        signs = {int(np.sign(v[s])) for s in have}
        held = len(signs) == 1 and all(abs(v[s]) >= 0.20 for s in have)
        verdict = ("HELD" if held else
                   "NOT HELD" if n_small >= 2 else "NO VERDICT (neither condition met)")
        tag = " (degenerate: predicate is zero everywhere)" if d == 1 else ""
        print(f"  depth {d}: differences {', '.join(f'{s}={v[s]:+.3f}' for s in have)}"
              f"  signs {sorted(signs)}  |d|<0.10 on {n_small}/{len(have)}"
              f"  ->  {verdict}{tag}")
    print(f"\n  PRIMARY (depth {PRIMARY_DEPTH}): the verdict above for depth {PRIMARY_DEPTH}.")
