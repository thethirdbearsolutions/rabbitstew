"""RBT-116 (DRAFT, revision 5): power of the paired crossing comparison, bounded by each body's floor and ceiling,
with the plateau DERIVED from holding arithmetic rather than asserted (design adversary MUST 4, MUST 9).

    python3 runs/RBT-116/power.py [--reps R] > runs/RBT-116/power.txt

Pure Python (no numpy, no scipy).  NOT a simulator run: a caricature of the readout's inputs pushed through the
readout's registered statistic and verdict rules (PREREGISTRATION.md §6-§7).  It is re-run before launch with the
gate's measured inputs (EPS_U, EPS_N, sensitivity, u_f, sigma_P, Delta): every constant marked GATE below.

Part 1, holding (`hold`): a transcription of the design adversary's `hold.py` (runs/RBT-116/design-adversary/) at
crossover 0 (pinned, §5.1): N 40, the top 10 on a D-draw mean are the pool, each child copies a uniform pool
parent, a carrier's child loses the trait with probability u.  Fitness = background + Delta * carrier + draw noise
/ sqrt(D), with auditor B's RBT-113 background and draw SDs.  The plateau Q_f is the mean carrier share at
generation 48 from a saturated start.

Part 2, the readout.  Per unit and fauna:
  * the U line crosses with probability p_f at a uniform generation, then sweeps linearly over TAU generations to
    its plateau Q_f (from part 1);
  * each probed member is called STEERS (after the confirmation battery) with probability
        Q(t) * SENS_C + (1 - Q(t)) * EPS_C
    where SENS_C = SENS**2 (two independent calls) and EPS_C = EPS**2 (U and N have their own EPS, MUST 7);
  * M = 40 members probed (all of them) at generations 12, 24, 36, 48;
  * A_f = mean over probes of (share_U - share_N); d = A_H - A_P, paired by unit;
  * a line has CROSSED if at generation 48 U has >= CROSS_K confirmed steerers of 40 and >= CROSS_K more than N.
    (A share threshold such as 0.125 is unreachable for a real trait held at plateau Q < 0.31 once confirmed
    sensitivity (about 0.4) multiplies it: it would turn a low-plateau bypass into NEITHER.)
Verdicts (MUST 8): HOLISTIC MORE READILY needs the A test AND the paired exact test on crossed lines.
"""
import argparse
import itertools
import math
import random

N, K, G = 40, 10, 48
T_PROBE = (12, 24, 36, 48)
M = 40             # members probed: all of them (adversary's cheap cure)
TAU = 12           # generations from a crossing to its plateau
SENS = 0.63        # GATE: single-call sensitivity on a true steerer (steer_probe.txt, steer2 k6, no count veto)
EPS = 0.02         # GATE: single-call false-STEERS rate (G4 caps it at 0.05)
CROSS_K = 3        # a line has CROSSED: >= 3 of 40 confirmed steerers in U at generation 48, and >= 3 more than N
P_FLOOR = 0.25     # NEITHER: each fauna's exact upper 95% bound on P(line crosses) is below this
DELTA_EQ = 0.015   # equivalence margin on d: half the mean d of the weak bypass (p_H 0.25: d ~ 0.030) at this readout
F_MIN = 0.25       # the STEERS threshold, in items per season: Delta for holding (MUST 4)
NOISE = {"holistic": (0.336, 1.158), "designed": (0.056, 1.343)}  # GATE: B's noise.txt (background SD, draw SD)
U_PRIOR = {"holistic": 0.146, "designed": 0.28}                   # GATE: B2's route loss; paper 10's u

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
        20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 30: 2.042, 40: 2.021}


# ---------- part 1: holding ----------

def hold(delta, u, sb, sd, D, rng, start, gens=G):
    c = [i < start for i in range(N)]
    for _ in range(gens):
        fit = [rng.gauss(0, sb) + (delta if c[i] else 0.0) + rng.gauss(0, sd / math.sqrt(D)) for i in range(N)]
        pool = sorted(range(N), key=lambda i: -fit[i])[:K]
        c = [c[rng.choice(pool)] and rng.random() >= u for _ in range(N)]
    return sum(c) / N


def plateau(fauna, delta, u, D, rng, reps=60):
    sb, sd = NOISE[fauna]
    return sum(hold(delta, u, sb, sd, D, rng, N) for _ in range(reps)) / reps


def s_approx(fauna, delta, D):
    sb, sd = NOISE[fauna]
    return 1.27 * delta / math.sqrt(sb ** 2 + sd ** 2 / D)


# ---------- part 2: the readout ----------

def tq(df):
    return T975.get(df) or T975[max(k for k in T975 if k <= df)]


def t_ci(x):
    n = len(x)
    m = sum(x) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in x) / (n - 1)) if n > 1 else 0.0
    h = tq(n - 1) * sd / math.sqrt(n)
    return m, m - h, m + h


def sign_flip_p(x, rng, draws=2000):
    obs = abs(sum(x))
    if len(x) <= 12:
        pats = list(itertools.product((1, -1), repeat=len(x)))
        return sum(abs(sum(a * b for a, b in zip(s, x))) >= obs - 1e-12 for s in pats) / len(pats)
    c = sum(abs(sum(v if rng.random() < 0.5 else -v for v in x)) >= obs - 1e-12 for _ in range(draws))
    return (c + 1) / (draws + 1)


def binom_upper(k, n, alpha=0.05):
    if k >= n:
        return 1.0
    lo, hi = k / n, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        cdf = sum(math.comb(n, i) * mid ** i * (1 - mid) ** (n - i) for i in range(k + 1))
        lo, hi = (mid, hi) if cdf > alpha else (lo, mid)
    return hi


def mcnemar_one_sided(b, c):
    """Exact one-sided p that b (units where only the first fauna crossed) exceeds c, on b + c discordant units."""
    n = b + c
    if n == 0:
        return 1.0
    return sum(math.comb(n, i) for i in range(b, n + 1)) / 2 ** n


def share(q, rng):
    return sum(rng.random() < q for _ in range(M)) / M


def unit(p, Q, eps_u, eps_n, rng, fixed=None):
    """(A, crossed) for one unit and fauna. `fixed` pins the true share at every probe (the outlier rows)."""
    su, sn = SENS * SENS, None
    eu, en = eps_u * eps_u, eps_n * eps_n
    cross = rng.random() < p
    tc = rng.uniform(0, G) if cross else None
    a = []
    for t in T_PROBE:
        q = fixed if fixed is not None else (Q * min(1.0, (t - tc) / TAU) if cross and t > tc else 0.0)
        u_ = share(q * su + (1 - q) * eu, rng)
        n_ = share(en, rng)
        a.append(u_ - n_)
    ku, kn = round(u_ * M), round(n_ * M)
    return sum(a) / len(a), (ku >= CROSS_K and ku - kn >= CROSS_K)


def verdict(UH, UP, rng):
    AH, AP = [u[0] for u in UH], [u[0] for u in UP]
    n = len(UH)
    kH, kP = sum(u[1] for u in UH), sum(u[1] for u in UP)
    b = sum(h[1] and not p[1] for h, p in zip(UH, UP))
    c = sum(p[1] and not h[1] for h, p in zip(UH, UP))
    d = [h - p for h, p in zip(AH, AP)]
    _, lo, hi = t_ci(d)
    pd = sign_flip_p(d, rng)
    if lo > 0 and pd < 0.05 and mcnemar_one_sided(b, c) < 0.05:
        return "HOLISTIC MORE READILY"
    if hi < 0 and pd < 0.05 and mcnemar_one_sided(c, b) < 0.05:
        return "PIONEER MORE READILY"
    if binom_upper(kH, n) < P_FLOOR and binom_upper(kP, n) < P_FLOOR:
        return "NEITHER CROSSES"
    if -DELTA_EQ < lo and hi < DELTA_EQ and min(kH, kP) >= 3:  # both bodies must have crossed
        return "EQUIVALENT"
    if lo > 0 and pd < 0.05:
        return "INCONCL: H STEERS MORE, NOT CROSSED"
    return "INCONCLUSIVE"


VERDICTS = ("HOLISTIC MORE READILY", "PIONEER MORE READILY", "NEITHER CROSSES", "EQUIVALENT",
            "INCONCL: H STEERS MORE, NOT CROSSED", "INCONCLUSIVE")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=300)
    ap.add_argument("--units", type=int, default=24)
    a = ap.parse_args()
    rng = random.Random(1165)

    print("# RBT-116 power, revision 5 (DRAFT).  Part 1: holding at crossover 0 (pinned), Delta = F_MIN = 0.25,")
    print("# B's RBT-113 noise; the priors u are B2's 0.146 (holistic) and paper 10's 0.28 (designed).  GATE values")
    print("# replace every prior before launch.  (1+s)(1-u) is the per-generation growth of a rare carrier lineage.")
    print(f"{'fauna':9s} {'D':>3s} {'u':>6s} {'s~1.27D/sP':>11s} {'(1+s)(1-u)':>11s} {'plateau Q':>10s}")
    Q = {}
    for fauna in ("holistic", "designed"):
        for D in (4, 8, 16):
            for u in (0.146, 0.28):
                s = s_approx(fauna, F_MIN, D)
                q = plateau(fauna, F_MIN, u, D, rng)
                Q[(fauna, D, u)] = q
                print(f"{fauna:9s} {D:3d} {u:6.3f} {s:11.3f} {(1 + s) * (1 - u):11.3f} {q:10.3f}")

    QH = Q[("holistic", 16, U_PRIOR["holistic"])]
    QP = Q[("designed", 16, U_PRIOR["designed"])]
    QPh = Q[("designed", 16, U_PRIOR["holistic"])]
    QHl = Q[("holistic", 16, U_PRIOR["designed"])]
    print(f"\n# Part 2 uses D = 16 plateaus at the prior u: Q_H = {QH:.3f} (u 0.146), Q_P = {QP:.3f} (u 0.28).")
    print(f"# Readout: n = {a.units} units, M = {M} probed, SENS {SENS} per call (confirmed: {SENS**2:.3f}),")
    print(f"# EPS {EPS} per call (confirmed: {EPS**2:.4f}), CROSS_K {CROSS_K} of {M}, P_FLOOR {P_FLOOR}; {a.reps} readouts per row.")
    print("# Verdict columns: " + " | ".join(VERDICTS))

    rows = [
        ("null: both at the Pioneer's prior floor (p 0.04)", 0.04, QH, 0.04, QP, EPS, EPS, None),
        ("null: neither ever crosses", 0.0, QH, 0.0, QP, EPS, EPS, None),
        ("null + U/N EPS gap in holistic (0.04 vs 0.01)", 0.04, QH, 0.04, QP, 0.04, 0.01, None),
        ("null + U/N EPS gap at the G4 cap (0.05 vs 0.01)", 0.04, QH, 0.04, QP, 0.05, 0.01, None),
        ("null + ONE holistic unit at true share 1.0", 0.04, QH, 0.04, QP, EPS, EPS, "outlier"),
        ("weak bypass: p_H 0.25", 0.25, QH, 0.04, QP, EPS, EPS, None),
        ("bypass: p_H 0.5", 0.50, QH, 0.04, QP, EPS, EPS, None),
        ("strong bypass: p_H 0.75", 0.75, QH, 0.04, QP, EPS, EPS, None),
        (f"bypass p_H 0.5, holistic held at the designed u (Q {QHl:.2f})", 0.50, QHl, 0.04, QP, EPS, EPS, None),
        ("bypass p_H 0.5 at a low plateau (Q 0.12)", 0.50, 0.12, 0.04, QP, EPS, EPS, None),
        ("both cross, p 0.5 each", 0.50, QH, 0.50, QP, EPS, EPS, None),
        (f"both cross p 0.5, equal u 0.146 (Q_P {QPh:.2f})", 0.50, QH, 0.50, QPh, EPS, EPS, None),
        ("Pioneer more: p_H 0.1, p_P 0.5", 0.10, QH, 0.50, QP, EPS, EPS, None),
    ]
    print(f"\n{'scenario':62s}" + "".join(f"{v.split(':')[0][:10]:>11s}" for v in VERDICTS) + "   mean d")
    for lab, pH, qH, pP, qP, eu, en, special in rows:
        cnt = dict.fromkeys(VERDICTS, 0)
        ds = []
        for _ in range(a.reps):
            UH = [unit(pH, qH, eu, en, rng) for _ in range(a.units)]
            if special == "outlier":
                UH[0] = unit(0.0, qH, eu, en, rng, fixed=1.0)
            UP = [unit(pP, qP, EPS, EPS, rng) for _ in range(a.units)]
            cnt[verdict(UH, UP, rng)] += 1
            ds.append(sum(u[0] for u in UH) / a.units - sum(u[0] for u in UP) / a.units)
        print(f"{lab:62s}" + "".join(f"{cnt[v] / a.reps:11.3f}" for v in VERDICTS) + f"   {sum(ds) / len(ds):+.3f}")


if __name__ == "__main__":
    main()
