"""RBT-112 power input: n and depth of the planted-rooted living on part 2's ten real genealogies.

Reads each restored part-2 arm's lineage.jsonl (the genealogy the matched null, null_xover_s0.py, runs its operator
down).  For seasons 150, 300 and 599: the designed-body living, those whose parents[0] root is a planted founder (even
i: held.py's n under the plant of RBT-104/106), and their mean parents[0] depth (held.py's depth).  No genome is read.

Usage: genealogy.py P2_ROOT > genealogy.txt       (P2_ROOT/SEED/lineage.jsonl, restored from ckpt/rbt-90-SEED)
"""
import json
import os
import sys

import numpy as np

SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
SEASONS = (150, 300, 599)


def main():
    root = sys.argv[1]
    print("# RBT-112: planted-rooted living on part 2's real genealogies (no compass selected; the null's genealogy)")
    print("seed\tseason\tliving\tn_planted_rooted\tmean_depth")
    for seed in SEEDS:
        parents, living = {}, {}
        for line in open(os.path.join(root, str(seed), "lineage.jsonl")):
            r = json.loads(line)
            if r["population"] != "conventional":
                continue
            parents.setdefault(r["name"], r["parents"])
            if "death" not in r:
                living.setdefault(r["generation"], []).append(r["name"])

        def rooted(nm):
            d = 0
            while parents.get(nm):
                nm, d = parents[nm][0], d + 1
            return nm, d
        for s in SEASONS:
            rs = [rooted(nm) for nm in living.get(s, [])]
            pl = [d for r, d in rs if int(r.split("-")[1]) % 2 == 0]
            print(f"{seed}\t{s}\t{len(rs)}\t{len(pl)}\t{np.mean(pl) if pl else float('nan'):.2f}")


if __name__ == "__main__":
    main()
