"""RBT-117 design adversary: statistical probes on SYNTHETIC data only (no RBT-113 arm output is read).

  A. level of compare.decide under a symmetric null (exact test, 12 seeds)
  B. level under a mean-zero but SKEWED d (a zero-inflated holistic fauna, two seeds of twelve 'discover eating')
  C. the C-line control: false-VOID rate of the registered rule as a function of the true mean d, with c drawn from
     RBT-113's own power model (sim_arm's -0.02 sigma0/gen bias, scaled by pilot.txt's founder SDs), as RBT-117's
     power.py does; and the same for a fixed pre-data threshold (the proposed fix)
  D. the literal and registered control rules against a gross C-line fault (the holistic C line drifting +1 raw)

    python runs/RBT-117/design-adversary/probe_stats.py > runs/RBT-117/design-adversary/probe_stats.txt
"""
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-113"))
import power as p113  # noqa: E402

spec = importlib.util.spec_from_file_location("cmp117", os.path.join(ROOT, "runs", "RBT-117", "compare.py"))
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

SIG = {"holistic": 0.1362, "designed": 0.7086}
N = 12
rng = np.random.default_rng(20260927)
Z = np.zeros(N)


def rate(gen, reps, c_gen=None, rule=cp.decide):
    out = {}
    for _ in range(reps):
        v = rule(gen(), c_gen() if c_gen else Z)[0]
        out[v] = out.get(v, 0) + 1
    return {k: v / reps for k, v in sorted(out.items())}


if os.environ.get("ONLY") != "CD":
    print("# A. symmetric null, d ~ N(0, 0.8), 20000 reps")
    print("  ", rate(lambda: 0.8 * rng.standard_normal(N), 20000))

    print("\n# B. mean-zero SKEWED null: designed D ~ N(mu, 0.8); holistic D = 0 except 2 of 12 seeds at +3 raw ('escape');")
    print("#    mu set so E[d] = 0 exactly (mu = 0.5). 20000 reps.")
    def skew():
        dh = np.zeros(N)
        dh[rng.choice(N, 2, replace=False)] = 3.0
        return dh - (0.5 + 0.8 * rng.standard_normal(N))
    print("  ", rate(skew, 20000))
    print("#    and with the escape count Binomial(12, 1/6) instead of fixed at 2:")
    def skew2():
        dh = np.where(rng.random(N) < 1 / 6, 3.0, 0.0)
        return dh - (0.5 + 0.8 * rng.standard_normal(N))
    print("  ", rate(skew2, 20000))

# C. control false-VOID rate vs true mean d
print("\n# C. registered control rule: P(VOID) by the true mean d; c from RBT-113's sim_arm (bias -0.02 sigma0/gen,")
print("#    holistic h2 0.2, designed 0.43, raw via pilot SDs; drift = b_C x 23 as RBT-117's power.py does);")
print("#    d = true mean + centred model noise (SD from power.txt, about 0.82). 400 reps per row.")
pool_c, pool_d = [], []
for _ in range(1200):
    ch = p113.sim_arm(0.2, rng)
    cd = p113.sim_arm(0.43, rng)
    pool_c.append(ch["b_C"] * (p113.G - 1) * SIG["holistic"] - cd["b_C"] * (p113.G - 1) * SIG["designed"])
    pool_d.append(ch["div_end"] * SIG["holistic"] - cd["div_end"] * SIG["designed"])
pool_c, pool_d = np.array(pool_c), np.array(pool_d)
cen = pool_d - pool_d.mean()
print(f"#    model c per seed: mean {pool_c.mean():+.3f} raw, SD {pool_c.std(ddof=1):.3f}; "
      f"P(sign-flip p_c < 0.05 at 12 seeds) = {np.mean([cp.ro.sign_flip_p(rng.choice(pool_c, N)) < 0.05 for _ in range(400)]):.2f}")

FIXED = float(os.environ.get("FIXED", "0.8"))  # proposed: a fixed pre-data bound (about the registered MDE, 0.76-0.83 raw, and 3x the modelled bias difference, +0.28), not a fraction of the observed d


def decide_fixed(d, c):
    d, c = np.asarray(d, float), np.asarray(c, float)
    pc = cp.ro.sign_flip_p(c)
    if pc < cp.ALPHA and abs(float(c.mean())) >= FIXED:
        return "VOID", {}
    return cp.decide(d, np.zeros(len(d)))


print(f"  {'true mean d':>11s}  {'registered: P(VOID)':>20s} {'P(HOL)':>7s} {'P(DES)':>7s}   {'fixed ' + str(FIXED) + ': P(VOID)':>18s} {'P(HOL)':>7s} {'P(DES)':>7s}")
for m in (-2.8, -0.8, -0.4, 0.0, 0.4, 0.6, 0.8, 1.2):
    reg = {"VOID": 0, cp.VERDICTS[0]: 0, cp.VERDICTS[1]: 0}
    fix = dict(reg)
    for _ in range(400):
        d = m + rng.choice(cen, N)
        c = rng.choice(pool_c, N)
        v = cp.decide(d, c)[0]
        reg[v] = reg.get(v, 0) + 1
        v2 = decide_fixed(d, c)[0]
        fix[v2] = fix.get(v2, 0) + 1
    print(f"  {m:+11.2f}  {reg['VOID'] / 400:20.3f} {reg[cp.VERDICTS[0]] / 400:7.3f} {reg[cp.VERDICTS[1]] / 400:7.3f}   "
          f"{fix['VOID'] / 400:18.3f} {fix[cp.VERDICTS[0]] / 400:7.3f} {fix[cp.VERDICTS[1]] / 400:7.3f}")

print("\n# D. a gross C-line fault: the holistic C line drifts +1.0 raw more than the model (e.g. a selected control)")
for m in (-2.8, 0.0, 0.8):
    reg = fixv = 0
    for _ in range(400):
        d = m + rng.choice(cen, N)
        c = rng.choice(pool_c, N) + 1.0
        reg += cp.decide(d, c)[0] == "VOID"
        fixv += decide_fixed(d, c)[0] == "VOID"
    print(f"  true mean d {m:+.2f}: registered P(VOID) {reg / 400:.3f}   fixed {FIXED} P(VOID) {fixv / 400:.3f}")
