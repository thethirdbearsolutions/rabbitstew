"""RBT-107 item 2: how many reproduction events does the post-event population turn over per season?

    python runs/RBT-107/depth.py > runs/RBT-107/depth.txt

Reads only committed lineage-last.txt (RBT-92's Arm): the ten RBT-90 part 2 baselines (runs/RBT-90/forage-SEED)
and the ten RBT-101 C4 shift arms (runs/RBT-101/shift-SEED), with T from runs/RBT-92/onset.txt.  No income column.

Three depth measures, per fauna, for the individuals alive at season s, counted from C0 = those alive at T - 1:
    fp     first-parent chain length back to a founder (RBT-92's baseline_depth.py), minus its median over C0.
           RBT-92 section 5 / RBT-89 section 10's "about five events" is this measure over [T, T+160).
    few    the fewest births from the individual back to any C0 member, every parent followed (RBT-101's
           rewire.py depth).  The conservative count: a crossover child of an old and a young parent scores low.
    most   the most births back to a C0 member, every parent followed.  The generous count.
Each is the median (fp) or mean (few, most) over the living at s, read at s = T + 40, T + 80, ..., <= 599.  The rate
is the least-squares slope of the measure on s over [T + 40, last read], in events per season; the season count to
20 events is 20 / rate.  The pooled rate is the median of the per-seed rates.

Environment overrides: RBT107_SEEDS, RBT107_C4 (the directory holding shift-SEED, default runs/RBT-101).
"""
import importlib.util
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
spec = importlib.util.spec_from_file_location("r92", os.path.join(ROOT, "runs", "RBT-92", "readout.py"))
R92 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R92)
sys.setrecursionlimit(100000)

KINDS = ("holistic", "conventional")
SEEDS = [int(s) for s in os.environ.get("RBT107_SEEDS", "801 804 805 806 807 1 2 3 4 7").split()]
C4 = os.environ.get("RBT107_C4", os.path.join(ROOT, "runs", "RBT-101"))
TARGET = 20


def onsets():
    out = {}
    for line in open(os.path.join(ROOT, "runs", "RBT-92", "onset.txt")):
        f = line.split("\t")
        if f[0].isdigit() and f[1].isdigit():
            out[int(f[0])] = int(f[1])
    return out


def slope(xs, ys):
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def measures(arm, kind, T, reads):
    ind = {n: v for (k, n), v in arm.ind.items() if k == kind}
    memo = {}

    def fp(n):
        if n not in memo:
            ps = ind.get(n, (0, 0, []))[2]
            memo[n] = 0 if not ps or ps[0] not in ind else 1 + fp(ps[0])
        return memo[n]

    c0 = arm.alive_at(kind, T - 1)
    fp0 = statistics.median(fp(n) for n in c0)
    lo, hi = {}, {}

    def few(n):
        if n in c0:
            return 0
        if n not in lo:
            ps = [p for p in ind.get(n, (0, 0, []))[2] if p in ind]
            v = [few(p) for p in ps]
            v = [x for x in v if x is not None]
            lo[n] = 1 + min(v) if v else None
        return lo[n]

    def most(n):
        if n in c0:
            return 0
        if n not in hi:
            ps = [p for p in ind.get(n, (0, 0, []))[2] if p in ind]
            v = [most(p) for p in ps]
            v = [x for x in v if x is not None]
            hi[n] = 1 + max(v) if v else None
        return hi[n]

    out = {}
    for s in reads:
        P = sorted(arm.alive_at(kind, s))
        if not P:
            continue
        f = [few(n) for n in P]
        m = [most(n) for n in P]
        f = [x for x in f if x is not None]
        m = [x for x in m if x is not None]
        out[s] = (statistics.median(fp(n) for n in P) - fp0, statistics.fmean(f), statistics.fmean(m))
    return out


def main():
    print(__doc__.split("\n\n")[0])
    print()
    T_of = onsets()
    rates = {(a, k, j): [] for a in ("base", "shift") for k in KINDS for j in range(3)}
    names = ("fp", "few", "most")
    for seed in SEEDS:
        T = T_of[seed]
        for label, path in (("base", os.path.join(ROOT, "runs", "RBT-90", f"forage-{seed}")),
                            ("shift", os.path.join(C4, f"shift-{seed}"))):
            if not os.path.exists(os.path.join(path, "lineage-last.txt")):
                print(f"seed {seed} {label}: no lineage-last.txt at {path}; skipped")
                continue
            arm = R92.Arm(path)
            reads = list(range(T + 40, arm.last + 1, 40))
            for kind in KINDS:
                m = measures(arm, kind, T, reads)
                row = "  ".join(f"{s - T:+d}:{v[0]:.1f}/{v[1]:.1f}/{v[2]:.1f}" for s, v in m.items())
                rs = []
                for j in range(3):
                    xs = [s for s in m]
                    r = slope(xs, [m[s][j] for s in xs]) if len(xs) > 1 else float("nan")
                    rates[(label, kind, j)].append(r)
                    rs.append(r)
                print(f"seed {seed:>4} T={T} {label:5s} {kind:12s} rate fp/few/most per 100 seasons "
                      f"{100 * rs[0]:.2f}/{100 * rs[1]:.2f}/{100 * rs[2]:.2f}   (T+d: fp/few/most) {row}")
    print()
    print(f"POOLED (median of per-seed rates; seasons after T to {TARGET} events = {TARGET} / rate)")
    for label in ("base", "shift"):
        for kind in KINDS:
            parts = []
            for j, nm in enumerate(names):
                v = [r for r in rates[(label, kind, j)] if r == r]
                if not v:
                    continue
                med = statistics.median(v)
                parts.append(f"{nm} {100 * med:.2f}/100 (range {100 * min(v):.2f}..{100 * max(v):.2f}, n={len(v)}) "
                             f"-> {TARGET / med:.0f} seasons (range {TARGET / max(v):.0f}..{TARGET / min(v):.0f})")
            print(f"DEPTH {label:5s} {kind:12s} " + " | ".join(parts))


if __name__ == "__main__":
    main()
