"""RBT-107 (Amendment 2, F6): Z10, the arithmetic in the ecology's own seasons, for §7's income residual.

    python runs/RBT-107/z10.py BASE_DIR SHIFT_DIR SEED T >> runs/RBT-107/z10.txt

RBT-101's readout adversary's Z10 (readout-adversary/probe_arena.py): over seasons [T, T + 10), every individual born
before T and playing that season in BOTH arms, paired by name, and gain(shift) - gain(base) from lineage.jsonl's
per-season rows (last_score = food - 0.03 x kJ / 1000; a row with no "food" key did not play).  The base and the shift arm
share the start seeds after T (RBT-101 start_seed_check.txt), so the pair differs in the terrain only, while the gaits
are the onset population's.  Reads bulk (lineage.jsonl), which is regenerable; the output line is committed.
Prints one line per fauna: SEED  KIND  Z10  n_pairs.
"""
import json
import os
import sys
from collections import defaultdict


def rows(run, T):
    """(season, fauna, name) -> gain over [T - 1, T + 10), rows that played (probe_arena.py's load())."""
    out = {}
    with open(os.path.join(run, "lineage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            s = r.get("generation")
            if T - 1 <= s < T + 10 and "food" in r:
                out[(s, r["population"], r["name"])] = float(r["last_score"])
    return out


def main(base, shift, seed, T):
    b, s = rows(base, T), rows(shift, T)
    c0 = {(k, n) for (t, k, n) in b if t == T - 1}  # probe_arena.py's born(): playing in the base at T - 1
    d = defaultdict(list)
    for key, v in s.items():
        if key[0] >= T and key in b and (key[1], key[2]) in c0:
            d[key[1]].append(v - b[key])
    for kind in ("holistic", "conventional"):
        v = d[kind]
        print(f"{seed}\t{kind}\tZ10 {sum(v) / len(v):+.4f}\tn_pairs {len(v)}" if v else f"{seed}\t{kind}\tZ10 n/a\tn_pairs 0")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
