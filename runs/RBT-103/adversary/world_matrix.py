"""RBT-103 adversary: the world control as a matrix rather than one pair of moves.
Reads the a = 64 per-body deltas from committed readouts (home rows) and from this directory's
probe readouts, and prints per-population home vs P-801-world gains, their paired difference
and ratio, with t(9) across populations."""
import os, re, numpy as np
from scipy import stats
A = "docs/artifacts"; O = "runs/RBT-103/adversary"
SEEDS = [1, 2, 3, 4, 7, 801, 804, 805, 806, 807]
def t_int(x):
    x = np.asarray(x, float); n = len(x); m = x.mean()
    h = stats.t.ppf(0.975, n - 1) * x.std(ddof=1) / np.sqrt(n); return m, m - h, m + h
def per_body(path):
    txt = open(path).read()
    rows = re.findall(r"^g(\d+)\s+[+-]1\s+(\d+\.\d+) \|\s+([+-]\d+\.\d+) \|\s+([+-]\d+\.\d+)", txt, re.M)
    return {int(g): (float(b), float(d64)) for g, b, _, d64 in rows}
def row(path):
    pb = per_body(path); d = [v[1] for v in pb.values()]; b = [v[0] for v in pb.values()]
    m, lo, hi = t_int(d)
    return m, lo, hi, np.mean(b), len(d), ("PAYS" if lo > 0 else "NEG" if hi < 0 else "unres")
print("## a = 64: each RBT-90 population's bodies in their own world vs P-801's world (seeds 7000+)")
print(f"{'seed':>5} | {'own world':>30} base | {'P-801 world':>30} base | diff  ratio")
H, P = [], []
for s in SEEDS:
    h = row(f"{A}/RBT-103-seed-{s}.txt"); p = row(f"{O}/xworld-seed-{s}-in-p801.txt")
    H.append(h[0]); P.append(p[0])
    print(f"{s:>5} | {h[0]:+.3f} [{h[1]:+.3f},{h[2]:+.3f}] {h[5]:5s} n={h[4]} {h[3]:.2f} | "
          f"{p[0]:+.3f} [{p[1]:+.3f},{p[2]:+.3f}] {p[5]:5s} n={p[4]} {p[3]:.2f} | {p[0]-h[0]:+.3f} {p[0]/h[0]:.2f}x")
for name, x in (("own world", H), ("P-801 world", P), ("P-801 world - own", np.subtract(P, H))):
    m, lo, hi = t_int(x); print(f"t(9) {name:18s} {m:+.3f} [{lo:+.3f}, {hi:+.3f}]")
print(f"PAYS count, own world {sum(1 for s in SEEDS if row(f'{A}/RBT-103-seed-{s}.txt')[5]=='PAYS')}/10, "
      f"P-801 world {sum(1 for s in SEEDS if row(f'{O}/xworld-seed-{s}-in-p801.txt')[5]=='PAYS')}/10")
print("\n## Committed populations (P-801, W4b-801) across worlds, a = 64")
cells = [("P-801", "P-801 world (26 items, 3 patches, regrow 45 s)", f"{A}/RBT-103-control-p801.txt", 7000),
         ("P-801", "P-801 world", f"{O}/seedblock9000-P801-home.txt", 9000),
         ("P-801", "P-801 world, instant regrow", f"{O}/world-P801-in-p801-instant-regrow.txt", 7000),
         ("P-801", "12 items, 3 patches", f"{O}/world-P801-in-sparse-patchy.txt", 7000),
         ("P-801", "26 items, no patches", f"{O}/world-P801-in-dense-uniform.txt", 7000),
         ("P-801", "RBT-90 world (12, no patches, instant)", f"{A}/RBT-103-world-control-p801.txt", 7000),
         ("P-801", "RBT-90 world", f"{O}/seedblock9000-P801-rbt90.txt", 9000),
         ("W4b", "W4b world (12, no patches, no regrow)", f"{A}/RBT-103-control-w4b.txt", 9000),
         ("W4b", "W4b world", f"{O}/w4b-home-s7000.txt", 7000),
         ("W4b", "RBT-90 world", f"{A}/RBT-103-world-control-w4b.txt", 7000),
         ("W4b", "RBT-90 world", f"{O}/w4b-rbt90-s9000.txt", 9000),
         ("W4b", "P-801 world", f"{O}/w4b-in-p801-world.txt", 7000)]
for pop, world, path, s0 in cells:
    m, lo, hi, b, n, v = row(path)
    print(f"{pop:6s} {world:42s} seeds {s0}+ | {m:+.3f} [{lo:+.3f}, {hi:+.3f}] {v:5s} base {b:.2f}  ({os.path.basename(path)})")
