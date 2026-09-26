"""RBT-92: the onset season T per seed, by the committed rule, from the seed's finished RBT-90 part 2 arm.

The cohort cycle on the selected baseline is a 60-season mortality wave (max_age = 60) that crosses
RBT-89 section 8's 20/60 peak threshold every cycle on every committed selected population-run
(runs/RBT-92/cohort_cycle.txt: 6/6; the period is 60 on 12/12), so "at least 20 seasons after the
last peak" has no solution on a selected arm.  The rule placing the event OFF the cycle, in the
trough half a period from the last wave, and reading NOTHING at or after the onset:

    p = the start s in [280, 330] maximising the deaths of both faunas together over [s, s + 10) of
        the seed's baseline arm (ties to the larger s); the wave's centre is c = p + 5
    T = c + 30 if c + 30 >= 340, else c + 90          (so T is in [340, 395])

It reads only seasons [280, 340), all before every T it can return, so the baseline's seasons from
T on (the control for k in cull_k.py and for R-shift) are never selected on.  It reads deaths only,
never income, and only from the finished baseline arm.  340 keeps >= 11 reproduction events of depth
before the onset (2T/60, RBT-59), and T + 200 <= 595 keeps the tail window inside the 600 seasons.

History, all before any arm exists:
  * 12:42 (as posted): T minimised deaths over [T - 10, T + 10). It read ten post-onset seasons of the
    baseline that is also the control for k, so the trough selection biased k upward (senior review,
    deviation 1).
  * 13:10 ruling: minimise over [T - 20, T). Dry-run on RBT-71's committed arms it lands T at the END
    of the trough, on the rising edge of the next wave: holistic deaths over [T, T + 10) 28, 20, 16 on
    804, 805, 806, against 10, 2, 4 under this rule (runs/RBT-92/onset_rules_dryrun.txt).  That is the
    transient RBT-89 section 8 forbids, so this rule replaces it (Amendment 2).

Printed beside T, as unselected references that enter no verdict: D at the fixed T = 370, and the
baseline's mean deaths per ten seasons over [T - 100, T), and the baseline's deaths over [T, T + 10)
(the k-window's control), which the rule did not read.

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
LO, PLO, PHI, PERIOD = 340, 280, 330, 60
FIXED = 370  # the unselected reference T printed beside the chosen one; enters no verdict
BASE = os.environ.get("RBT92_BASELINE_DIR", "runs/RBT-90")
KINDS = ("holistic", "conventional")


def deaths_alive(path):
    d, a = {}, {}
    for r in csv.DictReader(open(path), delimiter="\t"):
        s, k = int(r["season"]), r["population"]
        d[(s, k)] = int(r["deaths"])
        a[(s, k)] = int(r["alive"])
    return d, a


def onset(seed):
    path = os.path.join(BASE, f"forage-{seed}", "seasons.txt")
    d, a = deaths_alive(path)
    last = max(s for s, _ in d)
    if last < 599:
        return None, f"{seed}\tUNFINISHED\tbaseline {path} ends at season {last} < 599; the rule waits for the finished arm"
    tot = lambda s0, s1: sum(d.get((t, k), 0) for t in range(s0, s1) for k in KINDS)
    p = max(range(PLO, PHI + 1), key=lambda t: (tot(t, t + 10), t))
    c = p + 5
    T = c + PERIOD // 2 if c + PERIOD // 2 >= LO else c + PERIOD + PERIOD // 2
    dead = [k for k in KINDS if a.get((T - 1, k), 0) == 0]
    if dead:
        return None, f"{seed}\tEXCLUDED\t{'+'.join(dead)} at alive = 0 at season {T - 1} (seed rule's one exclusion)"
    hol = [sum(d.get((t, "holistic"), 0) for t in range(u, u + 10)) for u in range(PLO, 420, 10)]
    con = [sum(d.get((t, "conventional"), 0) for t in range(u, u + 10)) for u in range(PLO, 420, 10)]
    ref = {k: sum(d.get((t, k), 0) for t in range(T - 100, T)) / 10 for k in KINDS}
    after = {k: sum(d.get((t, k), 0) for t in range(T, T + 10)) for k in KINDS}
    return T, (f"{seed}\t{T}\twave window [{p},{p + 10}) deaths {tot(p, p + 10)}\tunselected references: D(T=370) over [350,370) "
               f"{tot(350, 370)}; baseline deaths [T,T+10) holistic {after['holistic']} conventional {after['conventional']} "
               f"(not read by the rule); mean per 10 seasons over [T-100,T) holistic {ref['holistic']:.1f} conventional "
               f"{ref['conventional']:.1f}\t10-season deaths from {PLO} in steps of 10: holistic {hol} conventional {con}")


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
