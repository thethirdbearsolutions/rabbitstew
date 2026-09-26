"""RBT-104 design adversary, item 4: matched-null power for the pre-registered verdict.

The programme rule since RBT-102: for every "absent"/null verdict, state P(null outcome | the
hypothesis is wholly true) at this n and depth.  The pre-registration gives outcome confidences
(P-1..P-4) but no such number.  This script computes it in two layers, from committed numbers only.

LAYER 1, readout (b) on one arm: P(the line reads FOOD-DEPENDENT | a fraction p of its seven
window champions carries a working compass).  Per body, F is drawn from the committed bodies of
`runs/RBT-104/function-controls-801.txt`: a carrying body from the a = 64 install control's seven
per-body F (the uniform-world prize, RBT-103's +0.84 row), a non-carrying body from the bare
champions' seven (the negative control, gens 300-590).  The zero-count veto is modelled with
each class's committed zero fraction (carrier 129/448, bare 213/448), binomial over 64 seeds.
FOOD-DEPENDENT iff the t(6) interval over the seven bodies excludes zero from above and no veto.

LAYER 2, the verdict: with q = P(an S8 line reads FOOD-DEPENDENT | H), the S8 count is
Binomial(n_usable, q); FALSIFIED needs <= 1, SUPPORTED needs >= 5 (plus S1 <= 1 and the paired
F interval, which only lowers P(SUPPORTED)).  Printed for n_usable 7..10.

What q is under H is the design's to state.  Two anchors are printed beside it: the persistence
of the planted compass's paying magnitude under the operator alone (persistence-*.txt), and the
mutation-selection threshold that implies.
"""
import numpy as np
from math import comb

POS = [0.719, 0.672, 0.703, 0.391, 0.453, 1.125, 0.516]      # a = 64 install, per body F (function-controls-801.txt)
NEG = [0.281, 0.078, -0.094, -0.297, 0.172, 0.094, 0.000]    # bare champions gens 300-590, per body F
Z_POS, Z_NEG = 129 / 448, 213 / 448
T6 = 2.447
rng = np.random.default_rng(104)


def p_fd(p, n=200000, centre=False):
    carry = rng.random((n, 7)) < p
    neg = np.asarray(NEG) - (np.mean(NEG) if centre else 0.0)
    f = np.where(carry, rng.choice(POS, (n, 7)), rng.choice(neg, (n, 7)))
    z = rng.binomial(64, np.where(carry, Z_POS, Z_NEG)).sum(1) / 448
    m, se = f.mean(1), f.std(1, ddof=1) / np.sqrt(7)
    return float(((m - T6 * se > 0) & (z <= 0.5)).mean())


def binom_le(k, n, q):
    return sum(comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(k + 1))


def main():
    print("# RBT-104 adversary: matched-null power of the pre-registered verdict\n")
    print("## Layer 1: P(one arm's line reads FOOD-DEPENDENT | fraction p of its 7 window champions carries a working a = 64 compass)\n")
    print("| p | P(FOOD-DEPENDENT) |")
    print("|---|---|")
    q_of_p = {}
    for p in (0.0, 0.14, 0.29, 0.43, 0.57, 0.71, 0.86, 1.0):
        q_of_p[p] = p_fd(p)
        print(f"| {p:.2f} | {q_of_p[p]:.3f} |")
    fp0 = p_fd(0.0, centre=True)
    print(f"\n(p = 0 is readout (b)'s false-positive rate on bare champions: {q_of_p[0.0]:.3f} resampling the seven committed")
    print(f"bare bodies as they are (mean +0.033), {fp0:.3f} with them centred on zero.  p = 1 is its power on a fixed compass.)")
    print(f"\nConsequence for SUPPORTED, which also needs S1 <= 1 of 10: even with every S8 line food-dependent,")
    print(f"P(S1 <= 1 | S1 has no compass) = {binom_le(1, 10, q_of_p[0.0]):.3f} (uncentred) / {binom_le(1, 10, fp0):.3f} (centred),")
    print(f"so P(SUPPORTED | H) is capped there before the paired-F condition.\n")
    print("## Layer 2: P(verdict outcome | per-line q), S8 count ~ Binomial(n_usable, q)\n")
    print("| q | n = 7: P(FALSIFIED-count <= 1) | P(>= 5) | n = 10: P(<= 1) | P(>= 5) |")
    print("|---|---|---|---|---|")
    for q in (0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 0.95):
        print(f"| {q:.2f} | {binom_le(1, 7, q):.3f} | {1 - binom_le(4, 7, q):.3f} | {binom_le(1, 10, q):.3f} | {1 - binom_le(4, 10, q):.3f} |")
    print("\nFALSIFIED's count fires with P >= 0.25 under H whenever q <= ~0.25 at n = 10 (q <= ~0.35 at n = 7),")
    print("and NOT DECIDED absorbs most of the mass for 0.2 < q < 0.5.")
    print("\n## Anchor for q: what H must beat (persistence-801.txt / persistence-4.txt, operator alone)\n")
    for seed, kept1 in ((801, 0.74), (4, 0.75)):
        u = 1 - kept1
        print(f"  seed {seed}: paying magnitude kept after one generation of mutation in {kept1:.0%} of lineages -> "
              f"loss u = {u:.2f} per generation; a compass is held at mutation-selection balance only if its "
              f"selective advantage s > u (equilibrium share ~ 1 - u/s).")
    print("  window depth 14-17.5 generations (RBT-102): with s <= u the paying class is gone by the window;")
    print("  the operator alone leaves 2-3% of lineages paying at depth 16, 11-13% at depth 8.")


if __name__ == "__main__":
    main()
