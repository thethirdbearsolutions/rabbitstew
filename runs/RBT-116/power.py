"""RBT-116 (DRAFT design): power of the paired crossing comparison, bounded by each body's floor and ceiling.

    python runs/RBT-116/power.py [--reps R] > runs/RBT-116/power.txt

Pure Python (no numpy, no scipy), so it runs anywhere.  NOT a simulator run: a caricature of the readout's inputs,
pushed through the readout's own statistic and verdict rules (PREREGISTRATION.md §6, §7), so that every verdict's
rate is known at the registered n before any arm.

The model, per seed unit and fauna f in {H (holistic), P (Pioneer)}:
  * the U line (truncation on net yield, real smell) CROSSES within the G = 48 generations with probability p_f;
    the crossing generation t_c is uniform on [0, G).  After t_c the true share of members that STEER rises
    linearly to the plateau Q_f over TAU generations (a sweep), and stays there (held under selection).
  * before crossing, and in the N line (the same selection with rotated-decoy smell) at every probe, the share is
    the instrument's false-STEERS rate EPS (the matched null: identical selection, no smell information).
  * the readout probes M members per line at generations T_PROBE; each is classified STEERS with probability
    equal to the true share (sensitivity is folded into Q_f: Q_f = plateau share x instrument sensitivity).
  * A_f = mean over probes of (share_U - share_N); d = A_H - A_P, paired by seed.
FLOOR and CEILING are explicit: A_f lies in [-EPS, Q_f]; nothing in the model can respond beyond them (RBT-113's
lesson: an unbounded model promised effects a bounded body cannot deliver).
"""
import argparse
import itertools
import math
import random

G = 48
T_PROBE = (12, 24, 36, 48)
M = 16          # members probed per line per fauna per probe
TAU = 12        # generations from a crossing to the plateau
EPS = 0.02      # false-STEERS rate per member (instrument, on coverage foragers); the pre-launch gate caps it at 0.05
DELTA_EQ = 0.025  # equivalence margin on d: half the mean d of the weakest bypass of interest (p_H 0.25 vs p_P 0.04: d ~ 0.048)
CROSS_SHARE = 0.25  # a LINE has crossed if, at the last probe, share_U >= this and share_U - share_N >= this
P_FLOOR = 0.25      # NEITHER CROSSES: each fauna's exact upper 95% bound on P(line crosses) is below this

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
        20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 30: 2.042, 40: 2.021}


def tq(df):
    return T975.get(df) or T975[max(k for k in T975 if k <= df)]


def t_ci(x):
    n = len(x)
    m = sum(x) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in x) / (n - 1)) if n > 1 else 0.0
    h = tq(n - 1) * sd / math.sqrt(n)
    return m, m - h, m + h


def sign_flip_p(x, rng, draws=4000):
    n = len(x)
    obs = abs(sum(x))
    if n <= 12:
        pats = itertools.product((1, -1), repeat=n)
        c = t = 0
        for s in pats:
            t += 1
            c += abs(sum(a * b for a, b in zip(s, x))) >= obs - 1e-12
        return c / t
    c = sum(abs(sum(v if rng.random() < 0.5 else -v for v in x)) >= obs - 1e-12 for _ in range(draws))
    return (c + 1) / (draws + 1)


def share(true_q, rng):
    return sum(rng.random() < true_q for _ in range(M)) / M


def unit_A(p, Q, rng):
    """(A, crossed): the time-averaged null-corrected share, and the line-level crossing call at the last probe."""
    cross = rng.random() < p
    tc = rng.uniform(0, G) if cross else None
    a = []
    for t in T_PROBE:
        q = EPS
        if cross and t > tc:
            q = max(EPS, Q * min(1.0, (t - tc) / TAU))
        u, nn = share(q, rng), share(EPS, rng)
        a.append(u - nn)
    return sum(a) / len(a), (u >= CROSS_SHARE and u - nn >= CROSS_SHARE)


def binom_upper(k, n, alpha=0.05):
    """Exact (Clopper-Pearson) one-sided upper 1-alpha bound on a binomial rate, by bisection."""
    if k >= n:
        return 1.0
    lo, hi = k / n, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        cdf = sum(math.comb(n, i) * mid ** i * (1 - mid) ** (n - i) for i in range(k + 1))
        lo, hi = (mid, hi) if cdf > alpha else (lo, mid)
    return hi


def verdict(UH, UP, rng):
    AH, AP = [u[0] for u in UH], [u[0] for u in UP]
    kH, kP, n = sum(u[1] for u in UH), sum(u[1] for u in UP), len(UH)
    d = [h - p for h, p in zip(AH, AP)]
    md, lo, hi = t_ci(d)
    p = sign_flip_p(d, rng)
    _, hlo, hhi = t_ci(AH)
    _, plo, phi = t_ci(AP)
    crossesH, crossesP = hlo > 0 and sign_flip_p(AH, rng) < 0.05, plo > 0 and sign_flip_p(AP, rng) < 0.05
    if lo > 0 and p < 0.05 and crossesH:
        return "HOLISTIC MORE READILY"
    if hi < 0 and p < 0.05 and crossesP:
        return "PIONEER MORE READILY"
    if binom_upper(kH, n) < P_FLOOR and binom_upper(kP, n) < P_FLOOR:
        return "NEITHER CROSSES"
    if -DELTA_EQ < lo and hi < DELTA_EQ and max(kH, kP) >= 3:
        return "NOT MORE READILY (EQUIVALENT)"
    return "INCONCLUSIVE"


VERDICTS = ("HOLISTIC MORE READILY", "PIONEER MORE READILY", "NEITHER CROSSES", "NOT MORE READILY (EQUIVALENT)",
            "INCONCLUSIVE")

# (label, p_H, Q_H, p_P, Q_P)
SCENARIOS = [
    ("null: both at the Pioneer's prior floor", 0.04, 0.5, 0.04, 0.5),
    ("null: neither ever crosses", 0.0, 0.5, 0.0, 0.5),
    ("bypass, weak: holistic crosses 1 line in 4", 0.25, 0.5, 0.04, 0.5),
    ("bypass, weakest of interest: 1 line in 6", 0.167, 0.5, 0.04, 0.5),
    ("bypass: holistic crosses 1 line in 2", 0.50, 0.5, 0.04, 0.5),
    ("bypass, strong: 3 lines in 4", 0.75, 0.5, 0.04, 0.5),
    ("bypass, but holistic plateau low (Q 0.25)", 0.50, 0.25, 0.04, 0.5),
    ("both cross equally, 1 in 2", 0.50, 0.5, 0.50, 0.5),
    ("both at ceiling (every line, Q 0.8)", 1.0, 0.8, 1.0, 0.8),
    ("Pioneer crosses more (0.5 vs 0.1)", 0.10, 0.5, 0.50, 0.5),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=400)
    ap.add_argument("--units", type=int, nargs="+", default=[12, 24])
    a = ap.parse_args()
    rng = random.Random(116)
    print(f"# RBT-116 power (DRAFT): {a.reps} simulated readouts per row; G={G}, probes at {T_PROBE}, M={M} members,")
    print(f"# TAU={TAU}, EPS={EPS}, DELTA_EQ={DELTA_EQ}, CROSS_SHARE={CROSS_SHARE}, P_FLOOR={P_FLOOR}.  Rows: P(verdict).")
    print(f"# Pioneer prior p_P = 0.04: about 1920 births per 48-generation line x ~2e-5 correctly signed paying")
    print(f"# proposals per lineage (paper 8); an assumption for the model, not a registered arm.")
    for n in a.units:  # noqa: the registered n is 24
        print(f"\n## n = {n} paired seed units")
        print("scenario".ljust(46) + "".join(v.split(" (")[0][:12].rjust(14) for v in VERDICTS) + "   mean d")
        for lab, pH, QH, pP, QP in SCENARIOS:
            cnt = dict.fromkeys(VERDICTS, 0)
            ds = []
            for _ in range(a.reps):
                UH = [unit_A(pH, QH, rng) for _ in range(n)]
                UP = [unit_A(pP, QP, rng) for _ in range(n)]
                cnt[verdict(UH, UP, rng)] += 1
                ds.append(sum(u[0] for u in UH) / n - sum(u[0] for u in UP) / n)
            print(lab.ljust(46) + "".join(f"{cnt[v] / a.reps:14.3f}" for v in VERDICTS) + f"   {sum(ds) / len(ds):+.3f}")


if __name__ == "__main__":
    main()
