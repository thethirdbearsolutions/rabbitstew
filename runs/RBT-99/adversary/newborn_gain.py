"""RBT-99 adversary probe 4: do newborns earn like adults?  (RBT-21's founders' route to extinction was
newborns spending their 1 energy before eating; probe 2 gives a child adult rows.)

Pre-onset window of ckpt/rbt-90-SEED lineage.jsonl (the 40 seasons before min(340, written)), rows by age
0-2 against age >= 3: mean items, mean kJ, mean gain as run and re-priced to 0.08, and the share re-priced
below the 0.25 basal cost.

    python runs/RBT-99/adversary/newborn_gain.py BULKDIR > runs/RBT-99/adversary/newborn_gain.txt
"""
import json, os, sys
import numpy as np
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)


def main(bulk):
    print(__doc__.split("\n\n")[0]); print()
    print(f"{'fauna':12} {'ages':>5} {'rows':>6} {'items':>6} {'kJ':>6} {'net@.03':>8} {'net@.08':>8} {'<basal@.08':>10}")
    acc = {}
    for seed in SEEDS:
        d = os.path.join(bulk, f"forage-{seed}")
        end = min(340, json.load(open(os.path.join(d, "state.json")))["season"])
        for line in open(os.path.join(d, "lineage.jsonl")):
            r = json.loads(line)
            if end - 40 <= r["generation"] < end and "work" in r:
                # the row's age is logged after the season's increment: age 1 is a robot's first season
                acc.setdefault((r["population"], "1-3" if r["age"] <= 3 else "4+"), []).append((r["food"], r["work"] / 1000, r["last_score"]))
    for (f, a), v in sorted(acc.items()):
        v = np.array(v)
        n8 = v[:, 2] - 0.05 * v[:, 1]
        print(f"{f:12} {a:>5} {len(v):6d} {v[:, 0].mean():6.2f} {v[:, 1].mean():6.2f} {v[:, 2].mean():8.3f} {n8.mean():8.3f} {(n8 < .25).mean():10.2f}")


if __name__ == "__main__":
    main(sys.argv[1])
