"""RBT-112 readout: PRINT-ONLY sensitivity section.  POST HOC: none of it is scored, and it touches no scored path.

Written after readout.py's registered output was seen (readout.txt, VERDICT Z: FALSIFIED; function FOLLOWS).  It reads
the committed arm files through readout.py's own parsers (imported, not edited) and the committed nulls, and prints:

  S1  champions carrying a paying planted unit (resting.txt, F12's print), HZ against HU per seed, paired
  S2  HZ's planted-rooted carrier share k_planted/n at 300 and 599 against the CROSSOVER-inclusive S = 0 null's
      replicates (null/xnull-w32-S0-SEED.txt, FULL OPERATOR, 20 per seed; HU against the default xnull likewise).
      The registered B comes from the no-crossover lineage table (baseline/), which does not model the ecology's
      crossover handing bare mates' global brains into planted roots, so it over-states what the operator leaves
      when that table is high (S = 0).  CAVEAT: the null's genealogy is part 2's, not the arm's own.
  S3  carriage over ALL living designed genomes at 599, (k_planted + k_bare) / living: counts compasses that crossed
      into bare-rooted lineages, which the registered call excludes by design (RBT-106 F3)
  S4  the function line per seed, HZ and HU, patchy-scored (already in readout.txt; gathered here per seed)

Usage: sensitivity.py > sensitivity.txt
"""
import importlib.util
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
_spec = importlib.util.spec_from_file_location("rbt112_readout_s", os.path.join(HERE, "readout.py"))
ro = importlib.util.module_from_spec(_spec)
sys.modules["rbt112_readout_s"] = ro
_spec.loader.exec_module(ro)
_spec = importlib.util.spec_from_file_location("rbt106_pool_xnull_s", os.path.join(ROOT, "runs", "RBT-106", "adversary", "pool_xnull.py"))
px = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(px)
SEEDS = ro.SEEDS
fmt = lambda x: f"{x[0]:+.3f} [{x[1]:+.3f}, {x[2]:+.3f}]"


def living(arm, seed, season):
    d = os.path.join(ROOT, "runs", "RBT-106", f"HU-{seed}") if arm == "HU" else os.path.join(HERE, f"HZ-{seed}")
    m = re.search(r"living designed genomes (\d+)", open(os.path.join(d, f"held-{season}.txt")).read())
    return int(m.group(1)) if m else None


def null_share(tag, seed, col):
    """k_planted/n per replicate at the column (0: 150, 1: 300, 2: 599), full operator."""
    rows = px.parse(os.path.join(HERE, "null", f"xnull-w32{tag}-{seed}.txt"))["x"]
    return [(r[col]["k"] - r[col]["kb"]) / r[col]["n"] if r[col]["n"] else float("nan") for r in rows]


def main():
    print("# RBT-112 readout, SENSITIVITY: POST HOC, PRINT-ONLY, NOT SCORED (the verdict is readout.txt's)\n")
    rows = {(a, s): ro.read_arm(a, s) for a in ("HU", "HZ") for s in SEEDS}
    print("## S1: window champions (bests 300..590) carrying a paying planted unit (resting.txt)\n")
    print("| seed | HU | HZ |\n|---|---|---|")
    dz = []
    for s in SEEDS:
        u, z = rows[("HU", s)]["rest"], rows[("HZ", s)]["rest"]
        print(f"| {s} | {u['carriers']}/{u['of']} | {z['carriers']}/{z['of']} |")
        dz.append(z["carriers"] - u["carriers"])
    print(f"sum: HU {sum(rows[('HU', s)]['rest']['carriers'] for s in SEEDS)}/70, HZ {sum(rows[('HZ', s)]['rest']['carriers'] for s in SEEDS)}/70; "
          f"paired HZ - HU per seed {fmt(ro.t_int(dz))}")
    print("\n## S2: planted-rooted carrier share against the crossover-inclusive null's replicates (part 2's genealogy; CAVEAT)\n")
    print("| seed | arm | observed k_pl/n 300 | null 95th pct 300 | observed k_pl/n 599 | null 95th pct 599 | above at both |")
    print("|---|---|---|---|---|---|---|")
    above = {"HU": 0, "HZ": 0}
    for s in SEEDS:
        for arm, tag in (("HU", ""), ("HZ", "-S0")):
            r = rows[(arm, s)]
            obs = [r[h]["k"] / r[h]["n"] if r[h]["n"] else float("nan") for h in ("held300", "held599")]
            q = [float(np.nanpercentile(null_share(tag, s, c), 95)) if not all(np.isnan(null_share(tag, s, c))) else float("nan") for c in (1, 2)]
            both = all(np.isfinite(o) and np.isfinite(b) and o > b for o, b in zip(obs, q))
            above[arm] += both
            print(f"| {s} | {arm} | {obs[0]:.3f} | {q[0]:.3f} | {obs[1]:.3f} | {q[1]:.3f} | {both} |")
    print(f"seeds above the crossover-inclusive null's 95th percentile at both readings: HU {above['HU']}, HZ {above['HZ']}")
    print("(the null's 95th percentile is over 20 replicates on part 2's genealogy, where planted roots can die out: nan)")
    print("\n## S3: carriage over all living designed genomes at 599, (k_planted + k_bare) / living\n")
    print("| seed | HU | HZ |\n|---|---|---|")
    d3 = []
    for s in SEEDS:
        v = {}
        for arm in ("HU", "HZ"):
            h = rows[(arm, s)]["held599"]
            v[arm] = (h["k"] + h["kb"]) / living(arm, s, 599)
        d3.append(v["HZ"] - v["HU"])
        print(f"| {s} | {v['HU']:.3f} | {v['HZ']:.3f} |")
    print(f"paired HZ - HU {fmt(ro.t_int(d3))}")
    print("\n## S4: function per seed, patchy-scored (primary F, attribution), as in readout.txt\n")
    print("| seed | HU | HZ |\n|---|---|---|")
    for s in SEEDS:
        u, z = rows[("HU", s)]["fp"], rows[("HZ", s)]["fp"]
        print(f"| {s} | {u['F']:+.3f} {'FD' if u['fd'] else '-'}, {u['att']} | {z['F']:+.3f} {'FD' if z['fd'] else '-'}, {z['att']} |")


if __name__ == "__main__":
    main()
