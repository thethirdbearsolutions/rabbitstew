"""RBT-92 adversary probe B: what "recovery time" reads on an arm with no event at all.

readout.py's recovery time is the first d >= 0 with |x(t) - P| <= h for all t in [T+d, T+d+20),
P the fauna's mean over [T-100, T) and h twice the SD of its per-season values there.  Applied to
the control (no event), it is the instrument's floor; the pre-registration predicts "base 0 on
10/10, 0.8" and states "base's own value is the floor".  Twenty consecutive seasons inside a
+-2 SD band is not a sure thing even with no event (0.95^20 = 0.36 for independent seasons), so
the floor is measured here on RBT-71's committed forage runs (the RBT-92 economy, pre-RBT-95
streams; mean_lifetime_score read from committed tables of a closed ticket, no run), at every
candidate T in [340, 400] (the onset rule's range) and at the trough rule's T.

    python runs/RBT-92/adversary/probe_recovery_floor.py > runs/RBT-92/adversary/probe_recovery_floor.txt
"""
import csv
import os
import statistics

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "RBT-71")
RUNS = [f"forage-{s}" for s in (804, 805, 806)]
TROUGH = {"forage-804": 370, "forage-805": 375, "forage-806": 362}  # onset.py's dry run (PREREGISTRATION §5)
KINDS = ("holistic", "conventional")
BEFORE, RUN, MAXD = 100, 20, 180


def recovery(x, P, h, T):
    for d in range(0, MAXD + 1):
        if all(T + d + i in x and abs(x[T + d + i] - P) <= h for i in range(RUN)):
            return d
    return None


def main():
    print(__doc__.split("\n\n")[0])
    print()
    allv = []
    for run in RUNS:
        rows = list(csv.DictReader(open(os.path.join(ROOT, run, "seasons.txt")), delimiter="\t"))
        for k in KINDS:
            x = {int(r["season"]): float(r["mean_lifetime_score"]) for r in rows if r["population"] == k}
            ds = []
            for T in range(340, 401):
                pre = [x[s] for s in range(T - BEFORE, T)]
                ds.append(recovery(x, statistics.fmean(pre), 2 * statistics.stdev(pre), T))
            T = TROUGH[run]
            pre = [x[s] for s in range(T - BEFORE, T)]
            dT = recovery(x, statistics.fmean(pre), 2 * statistics.stdev(pre), T)
            fin = [d for d in ds if d is not None]
            zero = sum(1 for d in ds if d == 0)
            allv += ds
            print(f"{run:11s} {k:12s} at the trough T={T}: d = {dT}   over T in [340,400] (61 onsets): d = 0 on {zero}/61, "
                  f"none on {61 - len(fin)}/61, median {statistics.median(fin) if fin else '--'}, max {max(fin) if fin else '--'}")
    fin = [d for d in allv if d is not None]
    print()
    print(f"pooled, 3 runs x 2 faunas x 61 onsets: d = 0 on {sum(1 for d in allv if d == 0)}/{len(allv)}, d <= 20 on "
          f"{sum(1 for d in fin if d <= 20)}/{len(allv)}, none on {len(allv) - len(fin)}/{len(allv)}; median {statistics.median(fin)}")


if __name__ == "__main__":
    main()
