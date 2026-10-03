"""RBT-118 prior (EXPLORATORY, descriptive only): does the random terrain explain the default world's holistic income lead?

    python runs/RBT-118/prior/terrain.py > runs/RBT-118/prior/terrain.txt

Auditor D's H56 (the random-terrain wheel tax, raised in the step-1 adversary's addendum, PR #402): the 30 default
histories all run on random terrain, where obstacles could tax a wheeled body.  The committed data hold a direct
comparison, RBT-107's and RBT-101's shift arms (`--shift terrain=flat`), which fork from the default histories at an
onset (360 and 352-382) and run on flat ground after it, same seed, same founders, same streams.

1. The terrain of every default history (config sim.world.terrain).
2. Per seed, H - D income after the onset in the flat arm against the same seasons of its own base history,
   and each fauna's own change (flat - base).  Windows: onset+140 .. onset+239 (500-599 on RBT-107, 522-599 or so on
   RBT-101, which ends at 599), and RBT-107's 1100-1199.
3. From the flat restores (levers-flat.tsv) against the base restores (levers.tsv), per fauna at seasons 599 and
   1199: food, work, net; and the static break-even price on flat ground.
4. The stress arms' holistic fewest alive after the onset (adversary MUST-4 cites it).

Descriptive only.  The flat arms are one onset and one magnitude; both faunas keep evolving after it.
"""
import csv
import json
import os
import re
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def load(run):
    t = defaultdict(dict)
    with open(os.path.join(ROOT, run, "seasons.txt")) as f:
        head = f.readline().rstrip("\n").split("\t")
        ix = {k: head.index(k) for k in ("season", "population", "alive", "mean_lifetime_score")}
        for line in f:
            r = line.rstrip("\n").split("\t")
            a = int(r[ix["alive"]])
            t[r[ix["population"]]][int(r[ix["season"]])] = (a, float(r[ix["mean_lifetime_score"]]) if a > 0 else np.nan)
    return t


def wmean(t, kind, lo, hi):
    v = [t[kind][s][1] for s in range(lo, hi) if s in t[kind]]
    v = [x for x in v if np.isfinite(x)]
    return float(np.mean(v)) if v else np.nan


def levers(name):
    L = defaultdict(dict)
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        return L
    for r in csv.DictReader(open(p), delimiter="\t"):
        if int(r["alive"]) == 0 or r["food"] == "":
            continue
        L[r["committed"]][(int(r["season"]), r["fauna"])] = {k: float(r[k]) for k in ("food", "work_j", "path", "gear_per_4mass")}
    return L


def main():
    runs = {r["run"]: r for r in csv.DictReader(open(os.path.join(HERE, "runs.tsv")), delimiter="\t")}
    print("# RBT-118 prior, terrain.py: EXPLORATORY, descriptive only (auditor D's H56)")

    print("\n## 1. Terrain of the 30 default histories")
    indep = sorted(r for r in runs if re.fullmatch(r"runs/RBT-90/forage-\d+|runs/RBT-107/fresh/base-\d+", r))
    terr = defaultdict(list)
    for r in indep:
        terr[json.load(open(os.path.join(ROOT, r, "config.json")))["sim"]["world"]["terrain"]].append(r)
    for k, v in terr.items():
        print(f"  terrain={k}: {len(v)} histories")

    print("\n## 2. Flat arms against their own base history, H - D income and each fauna's change (flat - base)")
    pairs = [(f"runs/RBT-107/fresh/shift-{s}", f"runs/RBT-107/fresh/base-{s}") for s in range(11, 31)]
    pairs += [(f"runs/RBT-101/shift-{s}", f"runs/RBT-90/forage-{s}") for s in (1, 2, 3, 4, 7, 801, 804, 805, 806, 807)]
    rows = []
    for flat, base in pairs:
        T = int(re.search(r"@(\d+)", runs[flat]["shift"]).group(1))
        tf, tb = load(flat), load(base)
        last = max(tb["holistic"]) + 1
        for name, lo, hi in (("onset+140..+239", T + 140, min(T + 240, last)), ("1100-1199", 1100, 1200)):
            if lo >= last:
                continue
            hb, db, hf, df = wmean(tb, "holistic", lo, hi), wmean(tb, "conventional", lo, hi), wmean(tf, "holistic", lo, hi), wmean(tf, "conventional", lo, hi)
            rows.append(dict(ticket=flat.split("/")[1], seed=flat.rsplit("-", 1)[1], T=T, w=name, base=hb - db, flat=hf - df, dH=hf - hb, dD=df - db))
    for tk in ("RBT-107", "RBT-101"):
        for w in ("onset+140..+239", "1100-1199"):
            R = [r for r in rows if r["ticket"] == tk and r["w"] == w and all(np.isfinite([r["base"], r["flat"]]))]
            if not R:
                continue
            b = np.array([r["base"] for r in R]); f = np.array([r["flat"] for r in R])
            dH = np.array([r["dH"] for r in R]); dD = np.array([r["dD"] for r in R])
            print(f"  {tk} {w:>16s} n={len(R):2d}: H-D base median {np.median(b):+.3f} (holistic ahead {int((b > 0).sum())}/{len(R)}); "
                  f"flat median {np.median(f):+.3f} (holistic ahead {int((f > 0).sum())}/{len(R)}); "
                  f"designed change median {np.median(dD):+.3f} (up on {int((dD > 0).sum())}), holistic change median {np.median(dH):+.3f} (up on {int((dH > 0).sum())}); "
                  f"flat H-D below base on {int((f < b).sum())}/{len(R)}")

    print("\n## 3. Food, work and net per fauna, flat restores against base restores (living population, 20-season window)")
    LB, LF = levers("levers.tsv"), levers("levers-flat.tsv")
    if not LF:
        print("  levers-flat.tsv absent: run levers.py --flat")
    for season in (599, 1199):
        for fauna in ("holistic", "conventional"):
            cells = defaultdict(list)
            for s in range(11, 31):
                b, f = LB.get(f"runs/RBT-107/fresh/base-{s}", {}).get((season, fauna)), LF.get(f"runs/RBT-107/fresh/shift-{s}", {}).get((season, fauna))
                if b and f:
                    for k in ("food", "work_j", "path"):
                        cells[k].append((b[k], f[k]))
                    cells["net"].append((b["food"] - 0.03 * b["work_j"] / 1000, f["food"] - 0.03 * f["work_j"] / 1000))
            if not cells:
                continue
            txt = "  ".join(f"{k} {np.median([x[0] for x in v]):.3f} -> {np.median([x[1] for x in v]):.3f}" if k != "work_j" else
                            f"work_kJ {np.median([x[0] for x in v]) / 1000:.2f} -> {np.median([x[1] for x in v]) / 1000:.2f}" for k, v in cells.items())
            print(f"  season {season} {('designed' if fauna == 'conventional' else fauna):9s} n={len(cells['food']):2d} (base -> flat medians): {txt}")
        pst, ahead = [], 0
        n = 0
        for s in range(11, 31):
            h, d = LF.get(f"runs/RBT-107/fresh/shift-{s}", {}).get((season, "holistic")), LF.get(f"runs/RBT-107/fresh/shift-{s}", {}).get((season, "conventional"))
            if not (h and d):
                continue
            n += 1
            dfood, dkj = d["food"] - h["food"], (d["work_j"] - h["work_j"]) / 1000
            if dfood > 0 and dkj > 0:
                pst.append(dfood / dkj)
            ahead += (h["food"] - 0.03 * h["work_j"] / 1000) > (d["food"] - 0.03 * d["work_j"] / 1000)
        if n:
            print(f"  season {season} flat: holistic nets more on {ahead}/{n}; break-even price defined on {len(pst)}/{n}"
                  + (f", median {np.median(pst):.4f}/kJ (range {min(pst):.4f}-{max(pst):.4f})" if pst else ""))

    print("\n## 4. Stress arms: holistic fewest alive after the onset")
    for pat in (r"runs/RBT-99/shift-\d+", r"runs/RBT-100/shift-\d+"):
        mins = []
        for r in sorted(x for x in runs if re.fullmatch(pat, x)):
            T = int(re.search(r"@(\d+)", runs[r]["shift"]).group(1))
            t = load(r)
            mins.append(min(a for s, (a, _) in t["holistic"].items() if s >= T))
        print(f"  {pat}: n={len(mins)}; holistic fewest alive from the onset on: min {min(mins)}, per arm {mins}")


if __name__ == "__main__":
    main()
