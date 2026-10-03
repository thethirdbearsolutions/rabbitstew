"""Monte Carlo check of rederive.py's exact income power at small n (stdlib random, seed 129)."""
import contextlib, io, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with contextlib.redirect_stdout(io.StringIO()):
    import rederive as R
random.seed(129)
print("Monte Carlo check of income power at |H-D| = 0.4, alpha 0.05 two-sided (400,000 draws per cell; seed 129)")
for n in (2, 3, 4, 8):
    for sd in (0.334, 0.275):
        c = R.crit(0.05, n - 1); hit = 0; N = 400000
        for _ in range(N):
            xs = [random.gauss(0.4, sd) for _ in range(n)]
            m = sum(xs) / n; s = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
            hit += abs(m / (s / math.sqrt(n))) > c
        p = hit / N
        print(f"  n {n} sd {sd}: t_crit {c:.4f}  MC {p:.4f} +- {1.96*math.sqrt(p*(1-p)/N):.4f}   exact (this route) {R.power(n, sd):.4f}")
