"""RBT-92: reproduction-event depth on the ten RBT-90 part 2 baselines, from their committed lineage-last.txt.

Depth of an individual = the length of its first-parent chain back to a founder (RBT-59's depth, RBT-71's
measure.py code path). Printed per seed and fauna: the median depth of the living at T - 1 (from onset.txt),
at T + 60, T + 160 and T + 199, and the events gained over the transient + recovery window [T, T + 160),
which is what "re-adapts" can mean inside the primary window (RBT-89 section 10: about five). The law
depth = 2 x seasons / max_age is printed beside it.

    python runs/RBT-92/baseline_depth.py > runs/RBT-92/baseline_depth.txt
"""
import csv
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "RBT-90")
KINDS = ("holistic", "conventional")


def onsets():
    out = {}
    for line in open(os.path.join(HERE, "onset.txt")):
        f = line.split("\t")
        if f[0].isdigit() and f[1].isdigit():
            out[int(f[0])] = int(f[1])
    return out


def main():
    print(__doc__.split("\n\n")[0])
    print()
    print(f"{'seed':>5} {'T':>4} {'fauna':12s} {'d(T-1)':>7} {'d(T+60)':>8} {'d(T+160)':>9} {'d(T+199)':>9} {'gain [T,T+160)':>15}   law 2*160/60 = 5.3")
    gains = {k: [] for k in KINDS}
    for seed, T in onsets().items():
        rows = list(csv.DictReader(open(os.path.join(BASE, f"forage-{seed}", "lineage-last.txt")), delimiter="\t"))
        for k in KINDS:
            ind = {r["name"]: (int(r["generation"]) - int(r["age"]), int(r["generation"]),
                               (r["parents"].split(",")[0] if r["parents"] else None)) for r in rows if r["population"] == k}
            memo = {}

            def depth(n):
                if n in memo:
                    return memo[n]
                p = ind.get(n, (0, 0, None))[2]
                memo[n] = 0 if p is None or p not in ind else 1 + depth(p)
                return memo[n]
            med = {}
            for label, s in (("T-1", T - 1), ("T+60", T + 60), ("T+160", T + 160), ("T+199", T + 199)):
                alive = [n for n, (b, l, _) in ind.items() if b <= s <= l]
                med[label] = statistics.median(depth(n) for n in alive) if alive else float("nan")
            g = med["T+160"] - med["T-1"]
            gains[k].append(g)
            print(f"{seed:>5} {T:>4} {k:12s} {med['T-1']:7.1f} {med['T+60']:8.1f} {med['T+160']:9.1f} {med['T+199']:9.1f} {g:15.1f}")
    print()
    for k in KINDS:
        print(f"{k:12s} gain over [T, T+160): median {statistics.median(gains[k]):.1f}, range {min(gains[k]):.1f}..{max(gains[k]):.1f} "
              f"over {len(gains[k])} seeds (RBT-89 section 10 predicts ~5.3)")


if __name__ == "__main__":
    main()
