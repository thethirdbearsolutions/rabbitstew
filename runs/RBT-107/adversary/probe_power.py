"""RBT-107 design adversary: power of the directional (one-sided) tests the coordinator asked for, on the design's own
measured null, with its heavy tail kept, and the n each needs.

    python runs/RBT-107/adversary/probe_power.py > runs/RBT-107/adversary/probe_power.txt

The null is the design's: the ten per-seed A_NB = G_N^flat - G_B^flat at d ~ 240 (runs/RBT-107/design_power.txt, both
faunas, the same seed row kept together so the two faunas' correlation is kept).  Under H0 a seed's A_SB is drawn as
one of those ten rows, resampled with replacement, with one random sign flip for the whole row (A_SB = e_S - e_B is
symmetric under H0), times k:  k = 1 (d ~ 240, as measured) or k = sqrt(800/240) = 1.83 (the design's own scaling to
d = 800, an assumption).  Under H1 a shift delta is added.  Three nulls: EMPIRICAL (the ten rows), EMP-NO3 (seed 3
dropped: the one furniture-dependent base), and GAUSS (normal with the rows' RMS; the design's model).
Tests, all one-sided at alpha = 0.05, in the direction of RBT-101's post hoc finding (and of RBT-110's H):
    t        the mean, one-sided t(n-1)
    wilcox   Wilcoxon signed-rank, exact null distribution
    yuen20   20% trimmed mean, Yuen's one-sample t (df n - 2g - 1)
    sign     sign test, exact binomial
and, for comparison, the design's own two-sided rule on A_SB alone (t(n-1) 95% interval excludes 0 in the right
direction), which is what MALADAPTED needs of A_SB (it also needs A_SN; that only lowers power further).
Quantities: DES = designed A_SB < 0; CO = co-evolved A_SB > 0; PAIRED = A_SB(co) - A_SB(des) > 0 (RBT-110's H).
Effects are in income per robot-bout; RBT-101's post hoc sizes at T + 110 were DES -0.22, CO +0.05, PAIRED +0.27.
The resampling is a smoothed bootstrap (each drawn row plus normal jitter at Silverman's robust bandwidth per fauna),
so ten rows do not produce ties.  5000 replicates per cell, fixed stream.  Nothing here reads an arm.
"""
import math
import os
import re

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPS = 5000


def read_null():
    rows = {}
    for line in open(os.path.join(HERE, "..", "design_power.txt")):
        m = re.match(r"seed\s+(\d+)\s+(holistic|conventional)\s+A_NB\s+([+-][\d.]+)", line)
        if m:
            rows.setdefault(int(m.group(1)), {})[m.group(2)] = float(m.group(3))
    seeds = sorted(rows)
    return seeds, np.array([[rows[s]["holistic"], rows[s]["conventional"]] for s in seeds])


def t_crit(df, p=0.95):
    # upper quantile of Student t by bisection on a numerically integrated cdf
    def cdf(x):
        xs = np.linspace(0, x, 4001)
        f = (1 + xs * xs / df) ** (-(df + 1) / 2)
        c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
        return 0.5 + c * np.trapezoid(f, xs)
    lo, hi = 0.0, 20.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if cdf(mid) < p else (lo, mid)
    return (lo + hi) / 2


TC1, TC2 = {}, {}


def tc(df, p):
    d = TC1 if p == 0.95 else TC2
    if df not in d:
        d[df] = t_crit(df, p)
    return d[df]


WCRIT = {}


def wilcox_crit(n):
    # smallest c with P(W+ >= c) <= 0.05 under H0, exact
    if n not in WCRIT:
        top = n * (n + 1) // 2
        dist = np.zeros(top + 1)
        dist[0] = 1
        for r in range(1, n + 1):
            new = dist.copy()
            new[r:] += dist[:-r]
            dist = new
        dist /= dist.sum()
        tail = np.cumsum(dist[::-1])[::-1]  # P(W >= c)
        WCRIT[n] = int(np.argmax(tail <= 0.05))
    return WCRIT[n]


SCRIT = {}


def sign_crit(n):
    if n not in SCRIT:
        p = [math.comb(n, k) / 2 ** n for k in range(n + 1)]
        tail = np.cumsum(p[::-1])[::-1]
        SCRIT[n] = int(np.argmax(tail <= 0.05))
    return SCRIT[n]


def tests(x):
    """x: (reps, n) array, H1 direction positive.  Returns rejection rates."""
    reps, n = x.shape
    m, sd = x.mean(1), x.std(1, ddof=1)
    t = m / (sd / math.sqrt(n))
    out = {"t": np.mean(t > tc(n - 1, 0.95)), "2s-int": np.mean(t > tc(n - 1, 0.975))}
    ranks = np.argsort(np.argsort(np.abs(x), 1), 1) + 1
    wplus = np.where(x > 0, ranks, 0).sum(1)
    out["wilcox"] = np.mean(wplus >= wilcox_crit(n))
    g = int(math.floor(0.2 * n))
    xs = np.sort(x, 1)
    tm = xs[:, g:n - g].mean(1)
    w = np.clip(xs, xs[:, [g]], xs[:, [n - g - 1]])
    sw = w.std(1, ddof=1)
    h = n - 2 * g
    ty = tm / (sw / ((h / n) * math.sqrt(n)))
    out["yuen20"] = np.mean(ty > tc(h - 1, 0.95))
    out["sign"] = np.mean((x > 0).sum(1) >= sign_crit(n))
    return out


def draw(rng, null, n, k, kind):
    if kind == "GAUSS":
        rms = np.sqrt((null ** 2).mean(0))
        cov = np.corrcoef(null.T) * np.outer(rms, rms)
        return k * rng.multivariate_normal([0, 0], cov, size=(REPS, n))
    idx = rng.integers(0, len(null), size=(REPS, n))
    flip = rng.choice([-1.0, 1.0], size=(REPS, n, 1))
    return k * (null[idx] * flip + rng.normal(0, 1, size=(REPS, n, 2)) * bandwidth(null))


def bandwidth(null):
    # smoothed bootstrap (ten rows would otherwise give ties): Silverman's robust rule per fauna, on the rows symmetrised
    s = np.concatenate([null, -null])
    iqr = np.subtract(*np.percentile(s, [75, 25], axis=0))
    return 0.9 * np.minimum(s.std(0, ddof=1), iqr / 1.34) * len(null) ** (-0.2)


def main():
    print(__doc__.split("\n\n")[0])
    seeds, null = read_null()
    print(f"null rows (seed: A_NB co-evolved, designed) from design_power.txt: " +
          ", ".join(f"{s}: {a:+.3f} {b:+.3f}" for s, (a, b) in zip(seeds, null)))
    no3 = null[[i for i, s in enumerate(seeds) if s != 3]]
    print(f"RMS co-evolved {np.sqrt((null[:, 0] ** 2).mean()):.3f} (no seed 3: {np.sqrt((no3[:, 0] ** 2).mean()):.3f}); "
          f"designed {np.sqrt((null[:, 1] ** 2).mean()):.3f}; paired co - des {np.sqrt(((null[:, 0] - null[:, 1]) ** 2).mean()):.3f} "
          f"(no seed 3: {np.sqrt(((no3[:, 0] - no3[:, 1]) ** 2).mean()):.3f}); corr(co, des) across seeds {np.corrcoef(null.T)[0, 1]:+.2f}")
    print(f"smoothing bandwidth (co-evolved, designed): {', '.join(f'{b:.3f}' for b in bandwidth(null))}; no seed 3: {', '.join(f'{b:.3f}' for b in bandwidth(no3))}")
    print()
    rng = np.random.default_rng(107_2)
    NS = (10, 15, 20, 30, 40)
    for label, k in (("d~240 as measured", 1.0), ("scaled to d=800 (x1.83)", math.sqrt(800 / 240))):
        for q, deltas in (("DES", (0.10, 0.15, 0.22, 0.30)), ("PAIRED", (0.15, 0.20, 0.27, 0.35)), ("CO", (0.10, 0.20, 0.30))):
            for nk, nl in (("EMPIRICAL", null), ("EMP-NO3", no3), ("GAUSS", null)):
                if q == "DES" and nk == "EMP-NO3":
                    continue
                print(f"== {q}  null {nk}  {label}")
                print("   delta  n  " + "  ".join(f"{t:>7s}" for t in ("t", "wilcox", "yuen20", "sign", "2s-int")) + "   (power; delta 0 row = size)")
                for d in (0.0,) + deltas:
                    for n in NS:
                        e = draw(rng, nl, n, k, nk)
                        x = {"DES": -e[:, :, 1], "CO": e[:, :, 0], "PAIRED": e[:, :, 0] - e[:, :, 1]}[q] + d
                        r = tests(x)
                        print(f"   {d:+.2f} {n:3d}  " + "  ".join(f"{r[t]:7.3f}" for t in ("t", "wilcox", "yuen20", "sign", "2s-int")))
                print()


if __name__ == "__main__":
    main()
