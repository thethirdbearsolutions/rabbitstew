"""RBT-116 (DRAFT, revision 7): power of the paired crossing comparison, bounded by each body's floor and ceiling,
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
    where SENS_C and EPS_C are the CONFIRMED rates as the gate measures them (R5-1: never squared, since false
    passes may be genome-persistent); U and N have their own EPS_C (MUST 7), and the holistic SENS_C is the
    smaller of the two-nose (G8(c)) and one-nose (G8(f)) confirmed shares (R5-2);
  * M = 40 members probed (all of them) at generations 12, 24, 36, 48;
  * A_f = mean over probes of (share_U - share_N); d = A_H - A_P, paired by unit;
  * a line has CROSSED if at generation 48 U has >= K confirmed steerers of 40 and >= K more than N; K is chosen
    in part 2a as the smallest value at which the U/N gap at G4's cap (confirmed 0.05 vs 0.01) gives false
    HOLISTIC <= 0.01 (R5-1).
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
SENS_C_TWO = 0.48  # GATE: confirmed share, two-nose steerer (r5_probe.txt, steer2 k6 under r5's call and transform)
SENS_C_ONE = 0.32  # GATE: confirmed share, one-nose temporal steerer at its paying gain (r5_probe.txt, steer1 k32)
SENS_C_P = 0.48    # GATE: the Pioneer's confirmed share (G8(a)); the two-nose value until measured
EPS_C = 0.005      # GATE: confirmed false-STEERS rate (G4's point target)
EPS_CAP = 0.05     # G4's gate: the exact upper 95% bound on the confirmed rate must be <= this
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


def count(q, rng):
    return sum(rng.random() < q for _ in range(M))


def unit(p, Q, sens_c, eps_u, eps_n, K, rng, fixed=None):
    """(A, crossed) for one unit and fauna; all rates are CONFIRMED rates. `fixed` pins the true share."""
    cross = rng.random() < p
    tc = rng.uniform(0, G) if cross else None
    a = []
    for t in T_PROBE:
        q = fixed if fixed is not None else (Q * min(1.0, (t - tc) / TAU) if cross and t > tc else 0.0)
        ku = count(q * sens_c + (1 - q) * eps_u, rng)
        kn = count(eps_n, rng)
        a.append((ku - kn) / M)
    return sum(a) / len(a), (ku >= K and ku - kn >= K), (ku >= K + 2 and ku - kn >= K + 2)


def verdict(UH, UP, rng, idx=1):
    UH = [(u[0], u[idx]) for u in UH]
    UP = [(u[0], u[idx]) for u in UP]
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
    if -DELTA_EQ < lo and hi < DELTA_EQ and min(kH, kP) >= 3:
        return "EQUIVALENT"
    if lo > 0 and pd < 0.05:
        return "INCONCL: H STEERS MORE, NOT CROSSED"
    return "INCONCLUSIVE"


VERDICTS = ("HOLISTIC MORE READILY", "PIONEER MORE READILY", "NEITHER CROSSES", "EQUIVALENT",
            "INCONCL: H STEERS MORE, NOT CROSSED", "INCONCLUSIVE")


def row(rng, reps, n, K, pH, qH, sH, euH, enH, pP, qP, sP=SENS_C_P, eP=EPS_C, special=None):
    cnt = dict.fromkeys(VERDICTS, 0)
    ds = []
    for _ in range(reps):
        UH = [unit(pH, qH, sH, euH, enH, K, rng) for _ in range(n)]
        if special == "outlier":
            UH[0] = unit(0.0, qH, sH, euH, enH, K, rng, fixed=1.0)
        UP = [unit(pP, qP, sP, eP, eP, K, rng) for _ in range(n)]
        cnt[verdict(UH, UP, rng)] += 1
        ds.append(sum(u[0] for u in UH) / n - sum(u[0] for u in UP) / n)
    return cnt, sum(ds) / len(ds)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=300)
    ap.add_argument("--units", type=int, default=24)
    ap.add_argument("--tau2-priors", action="store_true", help="Amendment 2: the tau = 2 s SENS priors (design-adversary/tau_probe.txt)")
    a = ap.parse_args()
    global SENS_C_TWO, SENS_C_ONE, SENS_C_P
    if a.tau2_priors:  # Amendment 2 (S-S1): the r5 caricature re-read at tau = 2 s; the default reproduces power.txt (r7)
        SENS_C_TWO, SENS_C_ONE, SENS_C_P = 0.40, 0.24, 0.40
        print("# Amendment 2 priors (tau = 2 s, design-adversary/tau_probe.txt): SENS_C two-nose 0.40, one-nose 0.24, Pioneer 0.40")
    rng = random.Random(1166)
    n = a.units

    print("# RBT-116 power, revision 6 (DRAFT).  Part 1: holding at crossover 0 (pinned), Delta = F_MIN = 0.25,")
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

    print(f"\n# Part 2a (R5-1): choosing K.  All rates CONFIRMED (never squared).  D = 16 plateaus Q_H {QH:.2f}, Q_P {QP:.2f};")
    print(f"# Pioneer SENS_C {SENS_C_P}, EPS_C {EPS_C}.  n = {n}, M = {M}; {2 * a.reps} readouts in the cap cell, {a.reps // 2} in the others.")
    print("# Columns: false HOLISTIC at the U/N gap at G4's cap (0.05 vs 0.01) | same, gap 0.02 vs 0.005 |"
          " P(HOLISTIC) for a p_H 0.5 bypass at holistic SENS_C 0.48 / 0.32 / 0.20 | P(NEITHER) at SENS_C 0.20")
    chosen = None
    for K in (3, 4, 5, 6, 7):
        r = a.reps // 2
        rc = 2 * a.reps  # the selection cell gets more readouts: it decides K
        f_cap, _ = row(rng, rc, n, K, 0.04, QH, SENS_C_TWO, EPS_CAP, 0.01, 0.04, QP)
        f_mid, _ = row(rng, r, n, K, 0.04, QH, SENS_C_TWO, 0.02, 0.005, 0.04, QP)
        det = [row(rng, r, n, K, 0.5, QH, sc, EPS_C, EPS_C, 0.04, QP)[0] for sc in (0.48, 0.32, 0.20)]
        fc = f_cap["HOLISTIC MORE READILY"] / rc
        print(f"K = {K}:  false H at cap {fc:.3f} | at 0.02/0.005 {f_mid['HOLISTIC MORE READILY'] / r:.3f} | "
              + " / ".join(f"{d['HOLISTIC MORE READILY'] / r:.3f}" for d in det)
              + f" | NEITHER at 0.20: {det[2]['NEITHER CROSSES'] / r:.3f}")
        if chosen is None and fc <= 0.01:
            chosen = K
    K = chosen or 7
    print(f"# Registered K = {K}: the smallest with false HOLISTIC <= 0.01 at the gap at G4's cap.")

    SH = min(SENS_C_TWO, SENS_C_ONE)
    print(f"\n# Part 2b: the readout at K = {K}; holistic SENS_C = min(two-nose {SENS_C_TWO}, one-nose {SENS_C_ONE}) = {SH};")
    print(f"# Pioneer SENS_C {SENS_C_P}; EPS_C {EPS_C} unless stated; {a.reps} readouts per row.")
    print("# Verdict columns: " + " | ".join(VERDICTS))
    rows = [
        ("null: both at the Pioneer's prior floor (p 0.04)", dict(pH=0.04, qH=QH, sH=SH, euH=EPS_C, enH=EPS_C, pP=0.04, qP=QP)),
        ("null: neither ever crosses", dict(pH=0.0, qH=QH, sH=SH, euH=EPS_C, enH=EPS_C, pP=0.0, qP=QP)),
        ("null + U/N gap AT G4's CAP (0.05 vs 0.01), registered", dict(pH=0.04, qH=QH, sH=SH, euH=EPS_CAP, enH=0.01, pP=0.04, qP=QP)),
        ("null + U/N gap 0.02 vs 0.005", dict(pH=0.04, qH=QH, sH=SH, euH=0.02, enH=0.005, pP=0.04, qP=QP)),
        ("null + ONE holistic unit at true share 1.0", dict(pH=0.04, qH=QH, sH=SH, euH=EPS_C, enH=EPS_C, pP=0.04, qP=QP, special="outlier")),
        ("weak bypass: p_H 0.25", dict(pH=0.25, qH=QH, sH=SH, euH=EPS_C, enH=EPS_C, pP=0.04, qP=QP)),
        ("bypass: p_H 0.5", dict(pH=0.5, qH=QH, sH=SH, euH=EPS_C, enH=EPS_C, pP=0.04, qP=QP)),
        ("bypass: p_H 0.5, holistic SENS_C 0.48 (two-nose)", dict(pH=0.5, qH=QH, sH=0.48, euH=EPS_C, enH=EPS_C, pP=0.04, qP=QP)),
        ("bypass: p_H 0.5, holistic SENS_C 0.20 (weak one-nose)", dict(pH=0.5, qH=QH, sH=0.20, euH=EPS_C, enH=EPS_C, pP=0.04, qP=QP)),
        ("strong bypass: p_H 0.75", dict(pH=0.75, qH=QH, sH=SH, euH=EPS_C, enH=EPS_C, pP=0.04, qP=QP)),
        (f"bypass p_H 0.5, holistic held at the designed u (Q {QHl:.2f})", dict(pH=0.5, qH=QHl, sH=SH, euH=EPS_C, enH=EPS_C, pP=0.04, qP=QP)),
        ("both cross, p 0.5 each (unequal u)", dict(pH=0.5, qH=QH, sH=SH, euH=EPS_C, enH=EPS_C, pP=0.5, qP=QP)),
        (f"both cross p 0.5, equal u 0.146 (Q_P {QPh:.2f})", dict(pH=0.5, qH=QH, sH=SH, euH=EPS_C, enH=EPS_C, pP=0.5, qP=QPh)),
        ("Pioneer more: p_H 0.1, p_P 0.5", dict(pH=0.1, qH=QH, sH=SH, euH=EPS_C, enH=EPS_C, pP=0.5, qP=QP)),
    ]
    print(f"\n{'scenario':62s}" + "".join(f"{v.split(':')[0][:10]:>11s}" for v in VERDICTS) + "   mean d")
    for lab, kw in rows:
        cnt, md = row(rng, a.reps, n, K, **kw)
        print(f"{lab:62s}" + "".join(f"{cnt[v] / a.reps:11.3f}" for v in VERDICTS) + f"   {md:+.3f}")

    # Part 2c (R6-1): a HOLISTIC / PIONEER verdict is headlined only if it also holds at K + 2.
    print(f"\n# Part 2c (R6-1): P(HOLISTIC at K = {K}) and P(HOLISTIC at K and at K + 2 = {K + 2}, the headline rule); {a.reps} readouts.")
    for lab, kw in [rows[2], rows[3], rows[6], rows[7], rows[8], rows[5]]:
        at_k = both = 0
        for _ in range(a.reps):
            UH = [unit(kw["pH"], kw["qH"], kw["sH"], kw["euH"], kw["enH"], K, rng) for _ in range(n)]
            UP = [unit(kw["pP"], kw["qP"], SENS_C_P, EPS_C, EPS_C, K, rng) for _ in range(n)]
            v1 = verdict(UH, UP, rng, 1) == "HOLISTIC MORE READILY"
            v2 = v1 and verdict(UH, UP, rng, 2) == "HOLISTIC MORE READILY"
            at_k += v1
            both += v2
        print(f"{lab:62s} at K {at_k / a.reps:.3f}   headlined (K and K+2) {both / a.reps:.3f}")


if __name__ == "__main__":
    main()
