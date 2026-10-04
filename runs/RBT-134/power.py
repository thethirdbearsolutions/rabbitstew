"""RBT-134 power at the planned n (DESIGN.md section 7).  Stdlib only; no data read.

PRIMARY.  Per condition, k = lineages out of N = 200,000 that carry the structure AND whose own links read
|a| >= 12.5236 (the a = 32 own-link rung; ERRATA H41).  The default operator's count on the SAME lineage seeds
is 0 (runs/RBT-104/drift-reach-k1.txt; RBT-91-alone-baseline.txt).  Under H0 (the candidate's per-lineage rate
equals the default's), conditional on k + 0 events the candidate's share is Binomial(k, 1/2), so the exact
one-sided p is 0.5^k.  Holm over the m = 4 registered candidates.

BACKGROUND.  Structureless whole-brain |a| >= 6.8664 (a whole-brain rung, so like for like here) among
n_bg structureless lineages; default 0.26% (docs/rbt-91-weight-scale-decision.md:30).  HOLDS iff the
point estimate is <= 2x the default's AND a one-sided two-proportion z test at 0.05 does not reject.

Usage: power.py > power.txt
"""
import math

N = 200_000
ARRIVALS = 84  # default operator, RBT-91-alone-baseline.txt
M = 4  # P2, P3, P4, P5 (DESIGN.md section 6; P1 and A0 are decided by the slope bound and run outside the family)
ALPHA = 0.05
P0_BG = 26 / 9_996


def pois_sf(k, lam):
    """P(Poisson(lam) >= k)."""
    if lam == 0:
        return 0.0 if k > 0 else 1.0
    term = math.exp(-lam)
    cdf = 0.0
    for i in range(k):
        cdf += term
        term *= lam / (i + 1)
    return max(0.0, 1.0 - cdf)


def phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def kmin(alpha):
    k = 1
    while 0.5 ** k > alpha:
        k += 1
    return k


def main():
    print("# RBT-134 power (power.py)\n")
    print("## Primary: exact paired test against the default operator's 0, Holm over m = 4\n")
    print("| Holm rank | alpha_i | smallest k with 0.5^k <= alpha_i |")
    print("|---|---|---|")
    for i in range(1, M + 1):
        a = ALPHA / (M - i + 1)
        print(f"| {i} | {a:.4f} | {kmin(a)} |")
    K = kmin(ALPHA / M)
    print(f"\nA candidate clears the first Holm step at k >= {K} (p = {0.5 ** K:.4f}).\n")
    print(f"| per-lineage rate r | expected k at N = {N:,} | as a fraction of {ARRIVALS} arrivals | P(k >= {K}) |")
    print("|---|---|---|---|")
    for r in (1e-5, 2e-5, 3e-5, 4e-5, 5e-5, 7.5e-5, 1e-4, 2e-4):
        lam = r * N
        print(f"| {r:.1e} | {lam:.1f} | {100 * lam / ARRIVALS:.1f}% | {pois_sf(K, lam):.3f} |")
    for target in (0.8, 0.95):
        lam = 0.0
        while pois_sf(K, lam) < target:
            lam += 0.01
        print(f"\n{int(target * 100)}% power at lambda = {lam:.2f}: r = {lam / N:.2e}, i.e. {100 * lam / ARRIVALS:.1f}% of an 84-arrival "
              f"denominator (RBT-104's link_scale 8 reached 8 of 84 = 9.5% at this rung; drift-reach-k8.txt)")
    print("\n## Background: does the structureless whole-brain rate HOLD (<= 2x default and no one-sided rejection)?\n")
    print(f"default p0 = {100 * P0_BG:.3f}% (26 of 9,996)\n")
    print("| n_bg per condition (both pools) | true ratio | P(HOLDS) | P(rejects 'unchanged' at 0.05) |")
    print("|---|---|---|---|")
    for n in (10_000, 40_000):
        for ratio in (1.0, 1.5, 2.0, 3.0, 6.3):
            p1 = P0_BG * ratio
            # simulate analytically: normal approximation to each proportion, unpaired (conservative: the design pairs)
            se_d = math.sqrt(P0_BG * (1 - P0_BG) / n + p1 * (1 - p1) / n)
            crit = 1.6449 * math.sqrt(2 * P0_BG * (1 - P0_BG) / n)
            p_rej = 1 - phi((crit - (p1 - P0_BG)) / se_d)
            se1 = math.sqrt(p1 * (1 - p1) / n)
            p_point_ok = phi((2 * P0_BG - p1) / se1)
            p_hold = max(0.0, min(p_point_ok, 1 - p_rej))  # upper bound on the joint; both are needed
            print(f"| {n:,} | {ratio:.1f}x | <= {p_hold:.3f} | {p_rej:.3f} |")
    print("\n(6.3x is RBT-91's coupled widening at weight_sigma 4.0: 1.64% / 0.26%; decision doc line 32.)")
    print("At n_bg = 40,000 a doubling is rejected with probability >= 0.99 and an unchanged background holds with")
    print("probability ~0.95; the default operator is re-run at the same n_bg on the same seeds (null B0).")


if __name__ == "__main__":
    main()
