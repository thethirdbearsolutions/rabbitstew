# Adversary: P4's expected k, upper bound.  Each of the 84 default arrivals' link product is multiplied by
# exp(X), X ~ N(0, s^2), s = the design's own 0.75*sqrt(19*0.2) = 1.46 (DESIGN 2.1), and read at the
# corrected max f' (abs = 1) with sech^2 = 1.  Arrival count held at 84 (P4 does not change the structural law).
import math
fmax = {"tanh":1,"sin":1,"relu":1,"integrate":2*(1-0.9**12),"abs":1,"differentiate":0,"sign":0}
rows = [l.split("|")[1:-1] for l in open("decompose_arrivals_baseline.txt") if l.startswith("| W4b") or l.startswith("| P-801")]
s = 0.75 * math.sqrt(19 * 0.2)
Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
for rung in (6.2831, 12.5236, 24.7145):
    e = 0.0
    for r in rows:
        c = [x.strip() for x in r]
        b = abs(float(c[11])) * fmax[c[2]]
        if b > 0: e += 1 - Phi(math.log(rung / b) / s)
    print(f"rung {rung}: expected k <= {e:.2f} (unit downstream slope, sd {s:.2f})")
