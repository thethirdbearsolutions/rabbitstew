"""RBT-99 adversary probe 3: is a robot's kJ its own (persistent) and its parent's (heritable)?

Probe 2's churn depends on both.  From the same pre-onset window of ckpt/rbt-90-SEED lineage.jsonl:
  repeatability  share of kJ variance between individuals (one-way ANOVA ICC on individuals with >= 4 rows)
  parent-child   regression of a child's mean kJ on its first parent's mean kJ (both with >= 3 rows in
                 the window), slope and n; slope ~ h2/2 per parent under a crossover rate of 0.5 is not
                 assumed: the slope is printed as measured.

    python runs/RBT-99/adversary/kj_heritability.py BULKDIR > runs/RBT-99/adversary/kj_heritability.txt
"""
import json, os, sys
import numpy as np
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)


def main(bulk):
    print(__doc__.split("\n\n")[0]); print()
    print(f"{'seed':>4} {'fauna':12} {'n ind':>5} {'ICC kJ':>6} {'n pairs':>7} {'slope child~parent':>18}")
    for seed in SEEDS:
        d = os.path.join(bulk, f"forage-{seed}")
        end = min(340, json.load(open(os.path.join(d, "state.json")))["season"])
        kj, par = {}, {}
        for line in open(os.path.join(d, "lineage.jsonl")):
            r = json.loads(line)
            if end - 80 <= r["generation"] < end and "work" in r:
                k = (r["population"], r["name"])
                kj.setdefault(k, []).append(r["work"] / 1000)
                if r["parents"]:
                    par[k] = (r["population"], r["parents"][0])
        for f in ("holistic", "conventional"):
            g = [np.array(v) for (p, _), v in kj.items() if p == f and len(v) >= 4]
            allv = np.concatenate(g); m = allv.mean()
            n0 = np.mean([len(x) for x in g])
            msb = sum(len(x) * (x.mean() - m) ** 2 for x in g) / (len(g) - 1)
            msw = sum(((x - x.mean()) ** 2).sum() for x in g) / (len(allv) - len(g))
            icc = (msb - msw) / (msb + (n0 - 1) * msw)
            pairs = [(np.mean(kj[pk]), np.mean(v)) for k, v in kj.items() if k[0] == f and len(v) >= 3
                     and (pk := par.get(k)) in kj and len(kj[pk]) >= 3]
            x, y = np.array(pairs).T
            slope = np.polyfit(x, y, 1)[0]
            print(f"{seed:>4} {f:12} {len(g):5d} {icc:6.2f} {len(pairs):7d} {slope:18.2f}")


if __name__ == "__main__":
    main(sys.argv[1])
