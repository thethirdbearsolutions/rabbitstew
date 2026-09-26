"""RBT-105 design adversary, probe 3: matched-null power of the rule, both directions, and of two
sharper replacements. Pure simulation; no run is read except the constants quoted below.

Model (one line per assumption, all stated in ADVERSARY.md F2/F3):
  * lognormal model: each founding population s has a latent propensity mu_s ~ N(0, icc); each run of it draws
    y = mu_s + e, e ~ N(0, 1 - icc): y is the run's standardised log late-season oscillator birth rate.
    icc = 0 is pure history (founders irrelevant); icc = 1 is fate fixed by the founders.
  * the run's `distinct` count is Poisson(lambda(y)) with log lambda linear in y, calibrated to RBT-90
    part 2: the five discarded arms' distinct 0,0,1,0,2 and the five acquired arms' 9,10,16,18,39
    (probe_distinct.txt). log lambda = a + b*y with the 10 arms' mean log(distinct+0.5) and sd.
  * seed selection copies the design: ten founding populations, one original run each (simulations with
    fewer than 2 (or 4) decided originals of either fate are redrawn, as RBT-90 gave 5/5); the 2 (or 4)
    discarded originals with the HIGHEST counts and the acquired ones with the LOWEST are chosen, as wave 1
    chose 7 & 805 and 4 & 807; 2 replicates each.
  * two models: "two-state" (primary; RBT-90's counts are bimodal, 0 of 10 in 3..7): seed s acquires with
    probability p_s ~ Beta(a, a), icc = 1/(2a+1) on the latent binary; a discarded run's count is drawn from
    RBT-90's discarded counts, an acquired run's is Poisson(lambda_s), lambda_s drawn once per seed from
    RBT-90's acquired counts. "lognormal" (secondary): the line below.
  * fate is RBT-84's bars on the count: <= 2 D, >= 8 A, else undecided.

Rules scored:
  R0 the pre-registered rule: HISTORY on >= 1 flip; FOUNDING if every replicate decided and equal to
     its original (with >= 2 of each fate); else NOT DECIDED.
  R1 flip-count rule on the binary fates: F = flips among decided replicates, n = decided replicates.
     FOUNDERS SHIFT FATE if P(Bin(n, .5) <= F) <= 0.05; HISTORY SUBSTANTIAL if P(Bin(n, .1) >= F) <= 0.05.
  R2 replicate-only continuous test: T = mean y of replicates of originally-acquired seeds minus mean y of
     replicates of originally-discarded seeds; exact permutation p over run labels among the replicates
     (valid under icc = 0 whatever the selection, because the originals are not in T).
  N  naive ICC F-test on original + replicates (one-way ANOVA), shown only to measure its selection bias.

    python runs/RBT-105/adversary/power.py > runs/RBT-105/adversary/power.txt
"""
import itertools
import math

import numpy as np

RBT90 = [0, 0, 1, 0, 2, 9, 10, 16, 18, 39]
ly = np.log(np.array(RBT90) + 0.5)
A, B = ly.mean(), ly.std()
SIMS = 4000
rng = np.random.default_rng(105)


def fate(c):
    return np.where(c <= 2, -1, np.where(c >= 8, 1, 0))


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def perm_table(m):
    half = m // 2
    rows = []
    for c in itertools.combinations(range(m), half):
        v = -np.ones(m)
        v[list(c)] = 1
        rows.append(v / half)
    return np.array(rows)


D_COUNTS = np.array([0, 0, 1, 0, 2])        #: RBT-90's discarded arms, the count given a discarded run
A_MEANS = np.array([9, 10, 16, 18, 39])     #: RBT-90's acquired arms, a seed's Poisson mean given an acquired run


def draw(model, icc, k):
    """Latent per-seed parameters for k founding populations."""
    if model == "two-state":
        if icc >= 1 - 1e-6:
            p = rng.integers(0, 2, k).astype(float)
        elif icc <= 1e-9:
            p = np.full(k, 0.5)
        else:
            a = (1 / icc - 1) / 2
            p = rng.beta(a, a, k)
        return p, rng.choice(A_MEANS, k)
    return rng.normal(0, math.sqrt(icc), k), None


def count(model, icc, lat, shape):
    if model == "two-state":
        p, lam = lat
        acq = rng.random(shape) < p.reshape(-1, *([1] * (len(shape) - 1)))
        dc = rng.choice(D_COUNTS, shape)
        ac = rng.poisson(np.broadcast_to(lam.reshape(-1, *([1] * (len(shape) - 1))), shape))
        return np.where(acq, ac, dc), None
    mu = lat[0]
    y = mu.reshape(-1, *([1] * (len(shape) - 1))) + rng.normal(0, math.sqrt(1 - icc), shape)
    return rng.poisson(np.exp(A + B * y)), y


def one(model, icc, per_side, reps, perms):
    while True:  # condition on what RBT-90 gave the design: at least per_side decided originals of each fate
        lat = draw(model, icc, 10)
        c0, _ = count(model, icc, lat, (10,))
        jit = c0 + rng.random(10) * 1e-3
        d_idx = [i for i in np.argsort(-jit) if c0[i] <= 2][:per_side]   # the discarded seeds nearest the bar
        a_idx = [i for i in np.argsort(jit) if c0[i] >= 8][:per_side]    # the acquired seeds nearest the bar
        if len(d_idx) == per_side and len(a_idx) == per_side:
            break
    seeds = np.array(d_idx + a_idx)
    f0 = fate(c0[seeds])
    sub = tuple(x[seeds] if x is not None else None for x in lat)
    cr, _ = count(model, icc, sub, (len(seeds), reps))
    fr = fate(cr)
    # R0
    flips = ((fr != 0) & (f0[:, None] != 0) & (fr != f0[:, None])).sum()
    rep_all = ((fr == f0[:, None]) & (f0[:, None] != 0)).all()
    r0 = "HISTORY" if flips else ("FOUNDING" if rep_all and (f0 == -1).sum() >= 2 and (f0 == 1).sum() >= 2 else "ND")
    # R1
    dec = (fr != 0) & (f0[:, None] != 0)
    n, F = int(dec.sum()), int(flips)
    shift = n > 0 and binom_cdf(F, n, 0.5) <= 0.05
    subst = n > 0 and (1 - binom_cdf(F - 1, n, 0.1)) <= 0.05
    r1 = "SHIFT" if shift else ("SUBST" if subst else "ND")
    # R2 (replicates only; label = side of the original's rank, not its fate, so it is fixed by design)
    side = np.repeat(np.r_[-np.ones(per_side), np.ones(per_side)], reps)
    yv = np.log(cr.ravel() + 0.5)
    t = (side / (len(side) / 2)) @ yv
    null = perms @ yv
    p2 = (null >= t - 1e-12).mean()
    # N: naive one-way ANOVA F on original + replicates
    allc = np.log(np.concatenate([c0[seeds][:, None], cr], axis=1) + 0.5)
    k, r = allc.shape
    gm = allc.mean()
    msb = r * ((allc.mean(1) - gm) ** 2).sum() / (k - 1)
    msw = ((allc - allc.mean(1, keepdims=True)) ** 2).sum() / (k * (r - 1))
    return r0, r1, p2, msb / max(msw, 1e-12), (fr == 0).mean()


def fcrit(per_side, reps):
    """The naive F's 0.95 quantile with NO selection and icc = 0 (the textbook null)."""
    k, r = 2 * per_side, reps + 1
    fs = []
    for _ in range(20000):
        x = rng.normal(size=(k, r))
        gm = x.mean()
        fs.append(r * ((x.mean(1) - gm) ** 2).sum() / (k - 1) / (((x - x.mean(1, keepdims=True)) ** 2).sum() / (k * (r - 1))))
    return float(np.quantile(fs, 0.95))


print(f"# calibration: log(distinct + 0.5) over RBT-90's ten arms: mean {A:.3f}, sd {B:.3f}; {SIMS} simulations per cell\n")
for model in ("two-state", "lognormal"):
  print(f"=== model: {model} ===")
  for per_side, label in ((2, "wave 1: 2 + 2 seeds x 2 replicates (m = 8)"), (4, "waves 1+2: 4 + 4 seeds x 2 replicates (m = 16)")):
      perms = perm_table(4 * per_side)
      fc = fcrit(per_side, 2)
      print(label)
      print(f"{'icc':>5s} | {'R0 HIST':>7s} {'R0 FOUND':>8s} {'R0 ND':>6s} | {'R1 SHIFT':>8s} {'R1 SUBST':>8s} {'R1 ND':>6s} | {'R2 p<=.05':>9s} | {'naive F':>7s} | undecided share of replicates")
      for icc in (0.0, 0.3, 0.5, 0.7, 0.9, 1.0 - 1e-9):
          out = [one(model, icc, per_side, 2, perms) for _ in range(SIMS)]
          r0 = [o[0] for o in out]
          r1 = [o[1] for o in out]
          print(f"{icc:5.2f} | {r0.count('HISTORY') / SIMS:7.3f} {r0.count('FOUNDING') / SIMS:8.3f} {r0.count('ND') / SIMS:6.3f} | "
                f"{r1.count('SHIFT') / SIMS:8.3f} {r1.count('SUBST') / SIMS:8.3f} {r1.count('ND') / SIMS:6.3f} | "
                f"{np.mean([o[2] <= 0.05 for o in out]):9.3f} | {np.mean([o[3] > fc for o in out]):7.3f} | {np.mean([o[4] for o in out]):.3f}", flush=True)
      print()
print("Read: icc = 0 rows are the matched null for every 'founders matter' verdict (R0 FOUNDING, R1 SHIFT, R2, naive F);")
print("icc near 1 rows are the matched null for R0 HISTORY. The naive F's icc = 0 row is its false-positive rate under the")
print("design's outcome-based seed selection (nominal 0.05); R2 excludes the originals and stays at <= 0.05.")
