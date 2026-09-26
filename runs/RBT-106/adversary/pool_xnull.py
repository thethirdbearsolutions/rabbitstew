"""Pool null_xover.py's readouts (null_xover/xnull-*.txt) over the ten seeds, per cell and operator.

Printed per cell (w = 1 K = 1 `same`; w = 1 K = 8 `pay64`; w = 32 K = 1 `pay32`) and operator (the full
ecology operator with crossover; the designer's mutation-only one, which must reproduce
runs/RBT-106/null/ at 300 and 599):
  HELD at 150 (the P8 / H gate's season), at 300, at 599, and at both 300 and 599 (the arm-level call)
  the bare-rooted share of k (hits that enter k but neither n nor mu)
and, for the mutation-only operator, whether its 300/599 columns equal the designer's committed null files.

Usage: pool_xnull.py [DIR]   (default null_xover; null_xover_deep = the --deepen runs, no designer comparison)
"""
import glob
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
CELLS = (("w1", "w = 1, K = 1, `same` (P1, S1)"), ("w1-k8", "w = 1, K = 8, `pay64` (P8, S8)"), ("w32", "w = 32, K = 1, `pay32` (HU, HP)"))
ROW = re.compile(r"^\| (\d+) \| (.*) \| (True|False) \|$")
CELL = re.compile(r"(\d+)\((\d+)\)/(\d+)/(\d+)( H)?")


def parse(path):
    sec, out = None, {"x": [], "m": []}
    for line in open(path):
        if line.startswith("## FULL"):
            sec = "x"
        elif line.startswith("## designer"):
            sec = "m"
        m = ROW.match(line.strip())
        if m and sec:
            cells = [CELL.match(c.strip()).groups() for c in m.group(2).split("|")]
            out[sec].append([dict(k=int(a), kb=int(b), n=int(c), B=int(d), h=bool(e)) for a, b, c, d, e in cells])
    return out


def designer(cell, seed):
    rows = []
    for line in open(os.path.join(_HERE, "..", "null", f"null-{cell}-{seed}.txt")):
        m = re.match(r"^\| (\d+) \| (\d+)/(\d+)/(\d+)( H)? \| (\d+)/(\d+)/(\d+)( H)? \|", line)
        if m:
            g = m.groups()
            rows.append(((int(g[1]), int(g[2]), int(g[3])), (int(g[5]), int(g[6]), int(g[7]))))
    return rows


def main():
    sub = sys.argv[1] if len(sys.argv) > 1 else "null_xover"
    deep = sub != "null_xover"
    print(f"# RBT-106 adversary: the HELD null ({sub}), pooled over 10 seeds x 20 replicates (seasons 150, 300, 599)"
          + ("; depth x2 for K = 1 cells, x3 for K = 8 (--deepen)" if deep else "") + "\n")
    print("| cell | operator | HELD at 150 | HELD at 300 | HELD at 599 | **HELD at 300 and 599** | bare-rooted share of k (300, 599) |")
    print("|---|---|---|---|---|---|---|")
    checks = []
    for cell, label in CELLS:
        for op, name in (("x", "full (crossover + mutation)"), ("m", "designer's (mutation only)")):
            h150 = h300 = h599 = both = kb = k = tot = 0
            for s in SEEDS:
                d = parse(os.path.join(_HERE, sub, f"xnull-{cell}-{s}.txt"))[op]
                for r in d:
                    tot += 1
                    h150 += r[0]["h"]
                    h300 += r[1]["h"]
                    h599 += r[2]["h"]
                    both += r[1]["h"] and r[2]["h"]
                    kb += r[1]["kb"] + r[2]["kb"]
                    k += r[1]["k"] + r[2]["k"]
                if op == "m" and not deep:
                    mine = [((r[1]["k"], r[1]["n"], r[1]["B"]), (r[2]["k"], r[2]["n"], r[2]["B"])) for r in d]
                    checks.append((cell, s, mine == designer(cell, s)))
            print(f"| {label} | {name} | {h150}/{tot} | {h300}/{tot} | {h599}/{tot} | **{both}/{tot} = {100 * both / tot:.1f}%** | {kb}/{k} |")
    if deep:
        return
    ok = sum(c[2] for c in checks)
    print(f"\nmutation-only operator reproduces the designer's committed null/ files (k, n, B at 300 and 599, every replicate): "
          f"{ok} of {len(checks)} seed-cells" + ("" if ok == len(checks) else f"; differing: {[c[:2] for c in checks if not c[2]]}"))


if __name__ == "__main__":
    main()
