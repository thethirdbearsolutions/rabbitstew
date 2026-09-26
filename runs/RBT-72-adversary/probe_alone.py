"""RBT-72 adversary: re-derive the links-alone table (paper 8 §4.2) from the three
committed readouts by an independent parser, and test the claim that the whole-brain
column "is background"."""
import re, math, sys

def _lchoose(n,k): return math.lgamma(n+1)-math.lgamma(k+1)-math.lgamma(n-k+1)
def fisher_exact(t):
    (a,b),(c,d)=t; r1=a+b; c1=a+c; N=a+b+c+d
    lp=lambda x: _lchoose(r1,x)+_lchoose(N-r1,c1-x)-_lchoose(N,c1)
    p0=lp(a); ps=[lp(x) for x in range(max(0,c1-(N-r1)),min(r1,c1)+1)]
    return None, min(1.0,sum(math.exp(q) for q in ps if q<=p0+1e-9))
def cp_upper0(n): return 1-0.025**(1/n)  # exact Clopper-Pearson upper for 0/n

RUNG, NULL = 6.8664, 3.57
LINE = re.compile(r"^\s+(\S+) lineage (\d+): \d+ unit\(s\), LINKS ALONE ([+-][\d.]+) .*whole brain ([+-][\d.]+)")
BG = re.compile(r"(\d+) of (\d+) STRUCTURELESS")

def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return c - h, c + h

for tag in ("baseline", "1.6", "4.0"):
    txt = open(f"docs/artifacts/RBT-91-alone-{tag}.txt").read()
    rows = [(m[1], int(m[2]), float(m[3]), float(m[4])) for m in map(LINE.match, txt.splitlines()) if m]
    bk, bn = map(int, BG.search(txt).groups())
    n = len(rows)
    own = [abs(r[2]) for r in rows]
    wb_hits = [r for r in rows if abs(r[3]) >= RUNG]
    lo, hi = wilson(0, n)
    cp_hi = cp_upper0(n)
    odds, p = fisher_exact([[len(wb_hits), n - len(wb_hits)], [bk, bn - bk]])
    print(f"sigma {tag}: arrivals {n} (W4b {sum(r[0].startswith('W4b') for r in rows)}, P801 {sum(r[0].startswith('P-801') for r in rows)})")
    print(f"  own links >= {RUNG}: {sum(o >= RUNG for o in own)}/{n}; >= null {NULL}: {sum(o >= NULL for o in own)}/{n}; max {max(own):.4f}; median {sorted(own)[n//2]:.4f}")
    print(f"  Wilson upper for 0/{n}: {hi:.4f}; Clopper-Pearson upper: {cp_hi:.4f}")
    print(f"  whole brain >= rung: {len(wb_hits)}/{n} = {len(wb_hits)/n:.4f}; background {bk}/{bn} = {bk/bn:.4f}")
    print(f"  enrichment {len(wb_hits)/n/(bk/bn):.1f}x, Fisher two-sided p = {p:.2g}")
    for r in wb_hits:
        print(f"    hit {r[0]} {r[1]}: links alone {r[2]:+.4f}, whole brain {r[3]:+.4f}, same sign {r[2]*r[3] > 0}")
