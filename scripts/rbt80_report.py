"""RBT-80 three-seed report: both readouts, yield per seed, inversion vs selection.

Assembles the final report from the per-seed analyser readouts
(docs/artifacts/RBT-80-seed{A,B,C}.txt) plus each run's history.json and
lineage.jsonl. No simulation; reads what is already measured.

Reports, per the coordinator's 07:38 comment:
  - carrier fraction as the PLATEAU mean over sampled seasons 250-299 (primary)
    and at season 299 (secondary), seeded minus drift, PER SEED, never pooled
  - yield seeded minus control per season, per seed, with the per-seed sign
  - loss-by-inversion separated from loss-by-selection, per seed per arm
  - each arm against the no-selection floor at ITS OWN realised depth
  - the demographic transient check that decided which readout is primary

Usage: python scripts/rbt80_report.py
"""
import json, os, re, sys, numpy as np

SEEDS = {"A": "seedA", "B": "seedB", "C": "seedC"}
ROOT = "runs/RBT-80"
ARMS = ("seeded", "control", "drift")
# Corrected no-selection floor (scripts/crossover_floor.py, commit 1ad0d93):
# structural retention r per reproduction x alignment survival at inversion q.
R_STRUCT, Q_INV = 0.989, 0.076


def floor_at(d):
    return (R_STRUCT ** d) * 0.5 * (1 + (1 - 2 * Q_INV) ** d)


def per_season(seed_label):
    """{arm: {season: (carrier_fraction, inverted_count, alive)}} from the readout."""
    path = f"docs/artifacts/RBT-80-{SEEDS[seed_label]}.txt"
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
            if re.match(r"^\|\s*\d+\s*\|", line):
                p = [x.strip() for x in line.strip("|").split("|")]
                # season | alive | carriers | fraction | median a | grad-dom | inverted
                d[int(p[0])] = (float(p[3]), int(p[6]), int(p[1]))
        out[arm] = d
    return out


def depth(seed_label, arm):
    h = [e for e in json.load(open(f"{ROOT}/{SEEDS[seed_label]}/{arm}/history.json"))["history"]
         if e["population"] == "conventional"]
    return sum(e["births"] for e in h) / 60.0


def yield_by_season(seed_label, arm):
    h = [e for e in json.load(open(f"{ROOT}/{SEEDS[seed_label]}/{arm}/history.json"))["history"]
         if e["population"] == "conventional"]
    return np.array([e["mean_lifetime_score"] for e in h])


def demography(seed_label, arm):
    rec = {}
    for line in open(f"{ROOT}/{SEEDS[seed_label]}/{arm}/lineage.jsonl"):
        r = json.loads(line)
        if r["population"] == "conventional":
            rec.setdefault(r["generation"], []).append(r)
    if 290 not in rec or 299 not in rec:
        return None
    base = {x["name"] for x in rec[290]}
    a290 = np.mean([x["age"] for x in rec[290]])
    a299 = np.mean([x["age"] for x in rec[299]])
    turn = len({x["name"] for x in rec[299]} - base)
    return a290, a299, turn


if __name__ == "__main__":
    have = [s for s in SEEDS if per_season(s)]
    print(f"RBT-80 three-seed report — seeds present: {', '.join(have)}\n")

    print("## 1. Carriage: plateau (primary) and season 299 (secondary)\n")
    print("| seed | arm | plateau 250-299 | season 299 | realised depth | floor at that depth |")
    print("|---|---|---|---|---|---|")
    P, S = {}, {}
    for s in have:
        ps = per_season(s)
        for arm in ARMS:
            if arm not in ps:
                continue
            pl = np.mean([v[0] for k, v in ps[arm].items() if 250 <= k <= 299])
            s299 = ps[arm].get(299, (float("nan"),))[0]
            d = depth(s, arm)
            P[(s, arm)] = pl; S[(s, arm)] = s299
            print(f"| {s} | {arm} | {pl:.3f} | {s299:.3f} | {d:.1f} | {floor_at(d):.3f} |")

    print("\n## 2. The verdict quantity: seeded minus drift, per seed, never pooled\n")
    print("| seed | plateau (PRIMARY) | season 299 (secondary) |")
    print("|---|---|---|")
    prim = {}
    for s in have:
        p = P[(s, "seeded")] - P[(s, "drift")]
        q = S[(s, "seeded")] - S[(s, "drift")]
        prim[s] = p
        print(f"| {s} | {p:+.3f} | {q:+.3f} |")

    print("\n## 3. Yield: seeded minus control per season, per seed\n")
    print("| seed | seeded mean | control mean | difference | sign |")
    print("|---|---|---|---|---|")
    for s in have:
        a, b = yield_by_season(s, "seeded"), yield_by_season(s, "control")
        n = min(len(a), len(b))
        d = (a[:n] - b[:n]).mean()
        print(f"| {s} | {a[:n].mean():.3f} | {b[:n].mean():.3f} | {d:+.3f} | {'+' if d > 0 else '-'} |")

    print("\n## 4. Loss by inversion vs loss by selection (seeded and drift)\n")
    print("| seed | arm | carriers at s299 | inverted at s299 | lost, not inverted |")
    print("|---|---|---|---|---|")
    for s in have:
        ps = per_season(s)
        for arm in ("seeded", "drift"):
            if arm not in ps or 299 not in ps[arm]:
                continue
            frac, inv, alive = ps[arm][299]
            carr = int(round(frac * alive))
            print(f"| {s} | {arm} | {carr}/{alive} | {inv} | {alive - carr - inv} |")

    print("\n## 5. Demographic transient, season 290 -> 299\n")
    print("| seed | arm | mean age 290 | mean age 299 | turnover |")
    print("|---|---|---|---|---|")
    for s in have:
        for arm in ARMS:
            dm = demography(s, arm)
            if dm:
                print(f"| {s} | {arm} | {dm[0]:.1f} | {dm[1]:.1f} | {dm[2]}/60 |")

    print("\n## 6. Verdict by the pre-registered rule\n")
    n_small = sum(1 for s in have if abs(prim[s]) < 0.10)
    signs = {np.sign(prim[s]) for s in have}
    print(f"  HELD requires seeded-drift >= +0.20 with the SAME SIGN on all three seeds.")
    print(f"    signs present: {sorted(signs)} -> {'UNREACHABLE' if len(signs) > 1 else 'possible'}")
    print(f"  NOT HELD requires |difference| < 0.10 on at least two of three seeds.")
    print(f"    seeds under 0.10: {n_small}/{len(have)}")
    if len(have) == 3:
        print(f"\n  VERDICT: {'NOT HELD' if n_small >= 2 else 'NO VERDICT (neither condition met)'}")
