"""RBT-99 adversary probe 1: the population's own kJ, not two seeds' bests.

The designer's item-3 prior (runs/RBT-99/work_budget.txt) prices 0.08 with the kJ of RBT-10's per-season
BESTS at seeds 802/803 and applies it to RBT-71's population income at 804-806.  The populations C2 will
actually shock are the ten RBT-90 part 2 baselines.  Their bulk is on ckpt/rbt-90-SEED (scripts/durable.sh
restore); this reads ONLY pre-onset seasons (T is in [340, 400] by RBT-92's committed rule, so every season
read here is < 340 and is byte-identical in every RBT-92/RBT-99 arm), and prints nothing RBT-90 part 2
scores (no heritability, no fauna contrast of R).  It is a design probe, not a result.

Per seed, fauna, window W = the last 40 seasons before min(340, seasons written):
  alive       mean alive per season
  items       mean items eaten per individual-season
  kJ          mean and quantiles of actuator work per individual-season (lineage "work", J / 1000)
  net@.03     mean season gain as run (lineage last_score = items - 0.03 kJ)
  net@.08     the same individual-seasons re-priced: last_score - 0.05 kJ  (exact: simulation.py food_gain)
  <basal@.08  fraction of individual-seasons whose re-priced gain is below the 0.25 basal cost
  <basal@.03  the same at the price actually paid (the baseline's own share of losing seasons)

    python runs/RBT-99/adversary/kj_baseline.py BULKDIR > runs/RBT-99/adversary/kj_baseline.txt
"""
import json
import os
import statistics as st
import sys

BASAL, EXTRA = 0.25, 0.05
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))]


def main(bulk):
    print(__doc__.split("\n\n")[0])
    print()
    hdr = f"{'seed':>4} {'fauna':12} {'window':>9} {'alive':>5} {'items':>5} {'kJ mean':>7} {'kJ q10/50/90':>17} {'net@.03':>7} {'net@.08':>7} {'<basal@.03':>10} {'<basal@.08':>10}"
    print(hdr)
    agg = {"holistic": [], "conventional": []}
    for seed in SEEDS:
        d = os.path.join(bulk, f"forage-{seed}")
        done = json.load(open(os.path.join(d, "state.json")))["season"]
        end = min(340, done)
        lo = end - 40
        rows = {"holistic": [], "conventional": []}
        alive = {"holistic": {}, "conventional": {}}
        for line in open(os.path.join(d, "lineage.jsonl")):
            r = json.loads(line)
            g = r["generation"]
            if lo <= g < end and "work" in r:
                rows[r["population"]].append(r)
                alive[r["population"]][g] = alive[r["population"]].get(g, 0) + 1
        for f in ("holistic", "conventional"):
            v = rows[f]
            kj = [r["work"] / 1000 for r in v]
            n3 = [r["last_score"] for r in v]
            n8 = [r["last_score"] - EXTRA * r["work"] / 1000 for r in v]
            b3 = sum(x < BASAL for x in n3) / len(v)
            b8 = sum(x < BASAL for x in n8) / len(v)
            a = st.mean(alive[f].values())
            agg[f].append((st.mean(n3), st.mean(n8), st.mean(kj)))
            print(f"{seed:>4} {f:12} {lo:>4}-{end - 1:<4} {a:5.1f} {st.mean(r['food'] for r in v):5.2f} {st.mean(kj):7.2f} "
                  f"{q(kj, .1):5.1f}/{q(kj, .5):5.1f}/{q(kj, .9):5.1f} {st.mean(n3):7.3f} {st.mean(n8):7.3f} {b3:10.2f} {b8:10.2f}")
    print()
    for f in ("holistic", "conventional"):
        n3, n8, kj = zip(*agg[f])
        print(f"  {f:12}: seed-mean kJ {min(kj):.2f}..{max(kj):.2f}; net@.08 {min(n8):+.3f}..{max(n8):+.3f}; "
              f"seeds with net@.08 < basal: {sum(x < BASAL for x in n8)}/{len(n8)}")


if __name__ == "__main__":
    main(sys.argv[1])
