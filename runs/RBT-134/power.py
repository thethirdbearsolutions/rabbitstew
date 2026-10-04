"""RBT-134 power at the planned n (DESIGN.md section 7), r3.  Stdlib only; no data read.

PRIMARY.  Per condition, k = lineages out of N = 200,000 that carry the structure AND whose own links read
|a| >= 12.5236 (the a = 32 own-link rung; ERRATA H41).  The default operator's count on the SAME lineage seeds
is 0 (runs/RBT-104/drift-reach-k1.txt; RBT-91-alone-baseline.txt).  Under H0 (the candidate's per-lineage rate
equals the default's), conditional on k + 0 events the candidate's share is Binomial(k, 1/2), so the exact
one-sided p is 0.5^k (McNemar on the discordant pairs; every condition is paired, DESIGN.md section 3).  Holm over
the m = 2 registered candidates (P2, P3; r2, design adversary M3).

BACKGROUND (r2, design adversary S1: one non-inferiority rule for every candidate).  Structureless whole-brain
|a| >= 6.8664 among the 40,000 background lineages, with every lineage whose probe flips a `sign` unit removed
(adversary M2).  B0's committed rate on that definition is 22 of 9,990: 26 hits on 9,996, of which 4 are on the
6 flagged lineages (r3, fix-check FC-M1; design-adversary/fc_bg_flip.txt).  HOLDS iff the one-sided 95% upper bound on the ratio candidate / B0 (Katz log
interval on the two counts, ignoring the pairing, which only widens it) is <= 2.

Usage: power.py > power.txt
"""
import math

N = 200_000
ARRIVALS = 84  # default operator, RBT-91-alone-baseline.txt
M = 2  # P2, P3 (DESIGN.md section 6; A0, P1, P4, P5 are decided by bounds/ceilings and run as checks)
ALPHA = 0.05
P0_BG = 22 / 9_990  # B0, `sign`-flip lineages removed (design-adversary/fc_bg_flip.txt; r3, FC-M1)
N_BG = 40_000
MARGIN = 2.0


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
    print("## Primary: exact paired test against the default operator's 0, Holm over m = 2\n")
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
    print("\n## Background: HOLDS iff the one-sided 95% upper bound on candidate/B0 is <= 2 (Katz log, unpaired)\n")
    print(f"B0 p0 = {100 * P0_BG:.3f}% (22 of 9,990 unflagged), n_bg = {N_BG:,} per condition\n")
    print("| true ratio | expected B0 hits | expected candidate hits | P(HOLDS) |")
    print("|---|---|---|---|")
    for ratio in (1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 6.3):
        x0, x1 = P0_BG * N_BG, P0_BG * ratio * N_BG
        se = math.sqrt(1 / x1 + 1 / x0 - 2 / N_BG)
        p_hold = phi((math.log(MARGIN) - 1.6449 * se - math.log(ratio)) / se)
        print(f"| {ratio:.2f}x | {x0:.0f} | {x1:.0f} | {p_hold:.3f} |")
    print("\nThe same rule, the same n and the same interval for every candidate.  6.3x is RBT-91's coupled widening at")
    print("weight_sigma 4.0 (1.64% / 0.26%; decision doc line 32).  An unchanged background HOLDS with probability")
    print("near 1, a 2x background fails with probability ~0.95, and between them the margin decides.")


if __name__ == "__main__":
    main()
