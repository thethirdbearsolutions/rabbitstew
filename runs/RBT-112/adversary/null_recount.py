"""RBT-112 design adversary: the matched null re-counted from the committed null/ tables with independent parsing
(not pool_xnull.parse): per replicate row "k(kb)/n/B" at seasons 150, 300, 599, HELD (amended) iff k - kb > B, the
arm-level call HELD at both 300 and 599; for each operator block (FULL OPERATOR = crossover; designer's = mutation only).
Also the exact binomial 95% interval of each rate (Clopper-Pearson by bisection, no scipy).
Usage: null_recount.py NULL_DIR"""
import math, os, re, sys
D = sys.argv[1]
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
def cp(k, n, a=0.05):
    def bis(f, lo, hi):
        for _ in range(100):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) else (lo, m)
        return (lo + hi) / 2
    tail_ge = lambda p: sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))
    tail_le = lambda p: sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(0, k + 1))
    lo = 0.0 if k == 0 else bis(lambda p: tail_ge(p) < a / 2, 0, 1)
    hi = 1.0 if k == n else bis(lambda p: tail_le(p) > a / 2, 0, 1)
    return lo, hi
for tag, name in (("", "default"), ("-S0", "S = 0")):
    cnt = {"x": [0, 0, 0, 0, 0], "m": [0, 0, 0, 0, 0]}
    for s in SEEDS:
        blk = None
        for line in open(os.path.join(D, f"xnull-w32{tag}-{s}.txt")):
            if line.startswith("## FULL OPERATOR"): blk = "x"
            elif line.startswith("## designer"): blk = "m"
            m = re.match(r"^\| \d+ \| (.+) \| (True|False) \|$", line.strip())
            if m and blk:
                cells = [re.match(r"(\d+)\((\d+)\)/(\d+)/(\d+)", c.strip()) for c in m.group(1).split("|")]
                h = [int(c.group(1)) - int(c.group(2)) > int(c.group(4)) for c in cells]
                c = cnt[blk]
                c[0] += 1; c[1] += h[0]; c[2] += h[1]; c[3] += h[2]; c[4] += h[1] and h[2]
    for blk, lab in (("x", "crossover (the arm's operator)"), ("m", "mutation only")):
        n, a150, a300, a599, both = cnt[blk]
        lo, hi = cp(both, n)
        print(f"{name}, {lab}: replicates {n}; HELD at 150 {a150}, 300 {a300}, 599 {a599}; at 300 and 599 {both}/{n} = {both / n:.1%} [{lo:.1%}, {hi:.1%}]")
