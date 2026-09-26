"""RBT-92: the onset season T per seed, by the committed rule, from the seed's finished RBT-90 part 2 arm.

The cohort cycle on the selected baseline is a 60-season mortality wave (max_age = 60) that crosses
RBT-89 section 8's 20/60 peak threshold every cycle on every committed selected population-run
(runs/RBT-92/cohort_cycle.txt: 6/6), so "at least 20 seasons after the last peak" has no solution on
a selected arm.  The rule placing the event OFF the cycle is therefore:

    T = the season in [340, 400] minimising D(T), the deaths of both faunas together over the
        twenty seasons [T - 10, T + 10) of the seed's baseline arm; ties go to the larger T.

[340, 400] is one full cycle, so a trough always exists in it; 400 is the latest T whose tail window
[T + 160, T + 200) still ends inside the 600 seasons the baseline ran; 340 keeps >= 11 reproduction
events of depth before the onset (2T/60, RBT-59).  The rule reads deaths only, from the baseline's
committed seasons.txt, after the arm has finished; no income column is read.  It also applies the seed
rule's one exclusion (runs/RBT-92/SEED-RULE.md): a seed with either fauna at alive = 0 at T - 1 is
marked EXCLUDED.

    python runs/RBT-92/onset.py [SEED ...] > runs/RBT-92/onset.txt
      (default: the ten seeds of the seed rule; baseline tables at runs/RBT-90/forage-SEED/seasons.txt,
       or RBT92_BASELINE_DIR/forage-SEED/seasons.txt)

Output: one line per seed, "SEED T D(T) ..." (run_arm.sh reads the first two fields), then the
deaths profile the choice was made on.
"""
import csv
import os
import sys

SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
LO, HI, HALF = 340, 400, 10
BASE = os.environ.get("RBT92_BASELINE_DIR", "runs/RBT-90")
KINDS = ("holistic", "conventional")


def deaths_alive(path):
    d, a = {}, {}
    for r in csv.DictReader(open(path), delimiter="\t"):
        s, k = int(r["season"]), r["population"]
        d[(s, k)] = int(r["deaths"])
        a[(s, k)] = int(r["alive"])
    return d, a


def onset(seed, lo=LO, hi=HI, half=HALF):
    path = os.path.join(BASE, f"forage-{seed}", "seasons.txt")
    d, a = deaths_alive(path)
    last = max(s for s, _ in d)
    if last < hi + half:
        return None, f"{seed}\tUNFINISHED\tbaseline {path} ends at season {last} < {hi + half}; the rule waits for the finished arm"
    D = {T: sum(d.get((s, k), 0) for s in range(T - half, T + half) for k in KINDS) for T in range(lo, hi + 1)}
    T = min(D, key=lambda t: (D[t], -t))
    dead = [k for k in KINDS if a.get((T - 1, k), 0) == 0]
    if dead:
        return None, f"{seed}\tEXCLUDED\t{'+'.join(dead)} at alive = 0 at season {T - 1} (seed rule's one exclusion)"
    hol = [d.get((s, "holistic"), 0) for s in range(lo - half, hi + half)]
    con = [d.get((s, "conventional"), 0) for s in range(lo - half, hi + half)]
    prof = f"deaths [{lo - half},{hi + half}) holistic {hol} conventional {con}"
    return T, f"{seed}\t{T}\tD={D[T]}/20 seasons\trange of D over [{lo},{hi}]: {min(D.values())}..{max(D.values())}\t{prof}"


def main(seeds):
    print("seed\tT\tD(T)\tnotes   (runs/RBT-92/onset.py; rule in its docstring)")
    for s in seeds:
        try:
            _, line = onset(s)
        except FileNotFoundError as e:
            line = f"{s}\tMISSING\t{e.filename}"
        print(line)


if __name__ == "__main__":
    main([int(x) for x in sys.argv[1:]] or SEEDS)
