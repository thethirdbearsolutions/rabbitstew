"""RBT-101 adversary probe B: `new` in two same-seed pairs that diverge after an UNPERCEIVED event (no terrain
change), and the realised size of natural new posture links against the installed reflex.

    PYTHONPATH=. python runs/RBT-101/adversary/pair_null.py > runs/RBT-101/adversary/pair_null.txt

Pairs (the RBT-92 and RBT-100 adversaries' short probe runs, restored from their ckpt/ branches; bulk):
  9902: plain vs --shift-at 150 --shift group-size=8   (C1-like, RBT-92 adversary)
  901:  plain vs --shift-at 100 --shift food-items=6   (C2-like, RBT-100 adversary)
They stop near T + 60, so the read is at min(T + 60, the last season recorded).  rewire.py's statistic at T + 60, C0 alive at T - 1.
"""
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import turnover_probe as tp  # noqa: E402

D = "runs/RBT-101/data/adv"


def new_at(run, T, off):
    life, parents = tp.lineage(run)
    off = min(off, max(l for _, l in life.values()) - T)
    W = {}
    for line in list(open(os.path.join(run, "adv_wiring.txt")))[1:]:
        p, n, a, b = line.split()
        W[(p, n)] = (float(a), float(b))
    res = {}
    for kind in tp.KINDS:
        alive = lambda s: {n for (k, n), (b, l) in life.items() if k == kind and b <= s <= l}
        c0, P = alive(T - 1), alive(T + off)
        hits, ho = [], []
        for n in P:
            stack, seen, anc = [n], set(), set()
            while stack:
                x = stack.pop()
                if x in seen:
                    continue
                seen.add(x)
                if x in c0:
                    anc.add(x)
                    continue
                stack.extend(parents.get((kind, x), []))
            A = [W[(kind, a)] for a in anc if (kind, a) in W]
            if (kind, n) in W and A:
                hits.append(W[(kind, n)][0] >= max(a[0] for a in A) + tp.NEW)
                ho.append(W[(kind, n)][1] >= max(a[1] for a in A) + tp.NEW)
        res[kind] = (off, len(P), statistics.fmean(hits) if hits else float("nan"), statistics.fmean(ho) if ho else float("nan"))
    return res


print("# RBT-101 adversary probe B: same-seed pairs diverged by an unperceived event; new (posture) and new_other (placebo) at T + 60")
for seed, T, a, b in ((9902, 150, "rbt-92-adv-plain-9902", "rbt-92-adv-shift-9902"), (901, 100, "rbt-100-adv-plain-901", "rbt-100-adv-shift-901")):
    ra, rb = new_at(os.path.join(D, a), T, 60), new_at(os.path.join(D, b), T, 60)
    for kind in tp.KINDS:
        print(f"{seed}\t{kind}\tread T+{ra[kind][0]}/T+{rb[kind][0]}\tplain |P| {ra[kind][1]} new {ra[kind][2]:.3f} new_other {ra[kind][3]:.3f}\t"
              f"shift |P| {rb[kind][1]} new {rb[kind][2]:.3f} new_other {rb[kind][3]:.3f}\t"
              f"shift - plain: new {rb[kind][2] - ra[kind][2]:+.3f}, new_other {rb[kind][3] - ra[kind][3]:+.3f}")

# the natural new posture links' size, from the committed control tables (P at 300 against C0 at 139)
print()
print("# natural new posture links in the baseline (control/SEED.txt, no install): g1 gain over the largest C0-ancestor g1, among hits")
for kind in tp.KINDS:
    gains, allgain = [], []
    for seed in (801, 804, 805, 806, 807, 1, 2, 3, 4, 7):
        rows = [l.rstrip("\n").split("\t") for l in open(f"runs/RBT-101/control/{seed}.txt") if not l.startswith("#")]
        head, rows = rows[0], [dict(zip(rows[0], r)) for r in rows[1:]]
        c0 = {r["name"]: float(r["g1"]) for r in rows if r["role"] == "C0" and r["population"] == kind}
        for r in rows:
            if r["role"] == "P" and r["population"] == kind and r["c0_ancestors"] != "-":
                gmax = max(c0[a] for a in r["c0_ancestors"].split(","))
                d = float(r["g1"]) - gmax
                allgain.append(d)
                if d >= 0.5:
                    gains.append(d)
    q = statistics.quantiles(gains, n=4)
    print(f"{kind}: {len(gains)}/{len(allgain)} hits; gain median {statistics.median(gains):.3f}, quartiles {q[0]:.3f}-{q[2]:.3f}, max {max(gains):.3f}"
          f"; installed reflex adds +1.0 (w = 1.0) or +0.5 (w = 0.5)")
