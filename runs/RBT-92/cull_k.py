"""RBT-92: the null's cull size per fauna, by RBT-89 section 8's rule.

    k(fauna) = max(0, deaths in the shift arm over [T, T + 10) - deaths in the baseline arm over [T, T + 10))

read from the shift arm's history.json (bulk; its first ten post-onset seasons are all the rule needs,
so this runs as soon as they exist, before any window is read) or its seasons.txt, and from the
baseline's committed seasons.txt.  Deaths only; no income column is read.

    python runs/RBT-92/cull_k.py SEED [SHIFT_DIR] > runs/RBT-92/cull-k-SEED.txt

run_arm.sh SEED cull reads the "cull" line.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("RBT92_BASELINE_DIR", "runs/RBT-90")
KINDS = ("holistic", "conventional")


def onset_of(seed):
    for line in open(os.path.join(HERE, "onset.txt")):
        f = line.split("\t")
        if f[0] == str(seed) and f[1].isdigit():
            return int(f[1])
    raise SystemExit(f"no onset for seed {seed} in onset.txt")


def deaths(run):
    if os.path.exists(os.path.join(run, "history.json")):
        rows = json.load(open(os.path.join(run, "history.json")))["history"]
    else:
        rows = list(csv.DictReader(open(os.path.join(run, "seasons.txt")), delimiter="\t"))
    return {(int(r["season"]), r["population"]): int(r["deaths"]) for r in rows}


def main(seed, shift_dir=None, T=None):
    T = T if T is not None else onset_of(seed)
    shift_dir = shift_dir or os.path.join(HERE, f"shift-{seed}")
    ds = deaths(shift_dir)
    db = deaths(os.path.join(BASE, f"forage-{seed}"))
    have = max(s for s, _ in ds)
    if have < T + 9:
        raise SystemExit(f"the shift arm has reached season {have}; the rule needs [{T}, {T + 10})")
    k = {}
    print(f"seed {seed}  T={T}  window [{T},{T + 10})")
    for kind in KINDS:
        a = sum(ds.get((s, kind), 0) for s in range(T, T + 10))
        b = sum(db.get((s, kind), 0) for s in range(T, T + 10))
        k[kind] = max(0, a - b)
        print(f"{kind:12s} deaths shift {a}  baseline {b}  excess {a - b}  k {k[kind]}")
    for kind in KINDS:  # the unselected reference (senior review deviation 1): the baseline's own mean per ten seasons before T
        print(f"{kind:12s} reference: baseline mean deaths per 10 seasons over [{T - 100},{T}) "
              f"{sum(db.get((s, kind), 0) for s in range(T - 100, T)) / 10:.1f}")
    print(f"cull\tholistic={k['holistic']},conventional={k['conventional']}")


if __name__ == "__main__":
    main(int(sys.argv[1]), *sys.argv[2:3])
