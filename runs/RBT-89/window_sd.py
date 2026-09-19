"""RBT-89: the between-seed spread of a WINDOWED income lead, from committed tables only.

The protocol's section 7 sets the resolvable effect size from seven 500-season leads and says
the spread of a 100-season windowed lead is a number the programme does not have.  The
adversary (RBT-89 review, 15:59) pointed out that class B ("draw") is reachable only if the
windowed between-seed SD is <= 0.1225 (r = 2 SD / sqrt(6) <= 0.10), and that the committed
seasons.txt of RBT-71's three seeds settle it with no run.  This is that file analysis.

For each seed the per-season lead is mean_lifetime_score(holistic) - mean_lifetime_score
(conventional) from runs/RBT-71/forage-SEED/seasons.txt.  Windows of W seasons are cut from
season 100 on (the founding bottleneck and recovery are over by season 30 on every seed).
Reported: the window means per seed, the between-seed SD of each window's mean, the pooled
between-seed SD, and 2 SD / sqrt(n) for n = 4, 6, 10, which is r in the protocol's section 9.

Usage: window_sd.py [W ...]     (default 60 100 500)
"""
import sys
import numpy as np

SEEDS = (804, 805, 806)
KIND = {"holistic": 0, "conventional": 1}


def leads(seed):
    rows = {}
    with open(f"runs/RBT-71/forage-{seed}/seasons.txt") as f:
        head = f.readline().split("\t")
        s_i, p_i, m_i = head.index("season"), head.index("population"), head.index("mean_lifetime_score")
        for line in f:
            c = line.rstrip("\n").split("\t")
            rows.setdefault(int(c[s_i]), {})[c[p_i]] = float(c[m_i])
    n = max(rows) + 1
    return np.array([rows[s]["holistic"] - rows[s]["conventional"] for s in range(n)])


def main():
    widths = [int(a) for a in sys.argv[1:]] or [60, 100, 500]
    L = {s: leads(s) for s in SEEDS}
    print("# RBT-89: between-seed SD of a windowed income lead (holistic - designed), RBT-71 seeds 804/805/806\n")
    for W in widths:
        starts = list(range(100, 600 - W + 1, W))
        print(f"## window W = {W} seasons, windows starting at {starts}\n")
        print(f"{'start':>6s}  " + "  ".join(f"{s:>8d}" for s in SEEDS) + f"  {'mean':>8s}  {'between-seed SD':>15s}")
        sds, block = [], {s: [] for s in SEEDS}
        for a in starts:
            m = [L[s][a:a + W].mean() for s in SEEDS]
            for s, v in zip(SEEDS, m):
                block[s].append(v)
            sd = float(np.std(m, ddof=1))
            sds.append(sd)
            print(f"{a:6d}  " + "  ".join(f"{v:+8.3f}" for v in m) + f"  {np.mean(m):+8.3f}  {sd:15.4f}")
        pooled = float(np.sqrt(np.mean(np.square(sds))))
        within = np.mean([np.std(block[s], ddof=1) for s in SEEDS]) if len(starts) > 1 else float("nan")
        print(f"\n  pooled between-seed SD of a {W}-season window lead: {pooled:.4f}   (within-run block-to-block SD, mean over seeds: {within:.4f})")
        print("  r = 2 SD / sqrt(n):  " + "  ".join(f"n={n}: {2 * pooled / np.sqrt(n):.4f}" for n in (4, 6, 10)))
        print(f"  class B reachable at n = 6 (needs SD <= 0.1225): {'YES' if pooled <= 0.1225 else 'NO'}\n")
    print("  Three seeds is three draws; the SD of three values has its own error (about +-40% at n = 3).")
    print("  The first challenge arm recomputes this from its own stage-1 tables and quotes both.")


if __name__ == "__main__":
    main()
