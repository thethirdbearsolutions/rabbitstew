"""RBT-132 design adversary: the null rate and power of RBT-129 §6.3 PERCEIVES' STEERS clause under four readings.

    python runs/RBT-116/design-adversary/rbt132_perceives_null.py > runs/RBT-116/design-adversary/rbt132_perceives_null.txt

Independent of probe_power.py: own code, scipy.stats (beta quantiles for Clopper-Pearson, Fisher's exact test), exact
sums over both binomials, no simulation; needs scipy, which is not a project dependency.  Founders N = evolved N (20 a seed, pooled over the seeds). No probe data."""
import numpy as np
from scipy import stats

def cp_up(k, n, a=0.05):
    return 1.0 if k >= n else stats.beta.ppf(1 - a, k + 1, n - k)

def thr_plugin_exact(k, nf, ne):  # smallest c with P(Bin > c) <= .05
    p = k / nf
    c = 0
    while stats.binom.sf(c, ne, p) > 0.05: c += 1
    return c

def thr_cp_count(k, nf, ne):      # C: count > ne * CP upper(k, nf) (confidence bound on the expected count)
    return ne * cp_up(k, nf)

def thr_cp_quantile(k, nf, ne):   # B (designer's): 95% quantile of Bin(ne, CP upper)
    p = cp_up(k, nf); c = 0
    while stats.binom.sf(c, ne, p) > 0.05: c += 1
    return c

def fisher_pass(k, e, nf, ne):    # D: one-sided Fisher exact, evolved > founders, alpha .05
    return stats.fisher_exact([[e, ne - e], [k, nf - k]], alternative="greater")[1] <= 0.05

def rate(nf, ne, pf, pe, reading):
    kf = stats.binom.pmf(np.arange(nf + 1), nf, pf)
    ke = stats.binom.pmf(np.arange(ne + 1), ne, pe)
    tot = 0.0
    for k in range(nf + 1):
        if kf[k] < 1e-14: continue
        if reading == "D":
            tot += kf[k] * sum(ke[e] for e in range(ne + 1) if ke[e] > 1e-14 and fisher_pass(k, e, nf, ne))
        else:
            t = {"A": thr_plugin_exact, "B": thr_cp_quantile, "C": thr_cp_count}[reading](k, nf, ne)
            tot += kf[k] * ke[np.arange(ne + 1) > t].sum()
    return tot

R = {"A": "plug-in rate, 95% count quantile (designer's 'registered')",
     "B": "CP-upper rate, then 95% count quantile (designer's 'exact-bound')",
     "C": "count > N x CP-upper rate (confidence bound on the expected count)",
     "D": "one-sided Fisher exact at 0.05 (reference two-sample test)"}
print("# rbt132_perceives_null.py (design adversary, RBT-132): PERCEIVES' STEERS clause, exact over both binomials; scipy, own code")
for k, v in R.items(): print(f"# {k}: {v}")
print("\n## null (evolved rate = founders' rate = eps), founders N = evolved N")
eps_grid = (0.001, 0.005, 0.01, 0.02, 0.03, 0.05)
print(f"{'N':>4s} {'eps':>6s} " + " ".join(f"{r:>7s}" for r in R))
for n in (80, 160):
    for eps in eps_grid:
        print(f"{n:4d} {eps:6.3f} " + " ".join(f"{rate(n, n, eps, eps, r):7.3f}" for r in R))
print("\n## power, N 80, founders eps 0.005 / 0.05, tau 2 s caricature SENS (two-nose 0.40, one-nose 0.24); pe = q*SENS + (1-q)*eps")
for sens, lab in ((0.40, "two"), (0.24, "one")):
    for eps in (0.005, 0.05):
        for q in (0.10, 0.25, 0.50):
            pe = q * sens + (1 - q) * eps
            print(f"{lab:4s} eps {eps:5.3f} q {q:.2f}: " + " ".join(f"{r} {rate(80, 80, eps, pe, r):.3f}" for r in R))
print("\n## thresholds at N 80 (evolved count must EXCEED): founders' k -> A / B / C")
for k in range(0, 6):
    print(f"k_f {k}: A {thr_plugin_exact(k,80,80)}  B {thr_cp_quantile(k,80,80)}  C {thr_cp_count(k,80,80):.2f}")
