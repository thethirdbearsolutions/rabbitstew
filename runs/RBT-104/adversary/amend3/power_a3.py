"""RBT-104 design adversary, Amendment 3 re-check: P(SUPPORTED | H) once SUPPORTED counts only
lines whose ATTRIBUTION reads `compass: FOOD-DEPENDENT`.

Inputs, all from committed files:
  q_H = 0.5 and d = 0.82        PREREGISTRATION.md section 6.3 (P(a line reads primary FD | H); primary per-line power)
  d_c: 4 of 8                   docs/artifacts/RBT-103-decoy-*.txt, retention rule met on 4 of 8 paying populations
  S1 cap 0.735-0.921            adversary power.txt (P(S1 <= 1 primary FD of 10 | S1 has no compass))
Amendment 3's arithmetic: q_c = q_H * d_c / d, P(SUPPORTED's count) = P(Binomial(n, q_c) >= 5),
P(SUPPORTED | H) <= that x S1 cap (the paired-F condition only lowers it further).
This script re-derives Amendment 3's figure and shows its spread over d_c's own uncertainty and n.
"""
from math import comb


def ge(k, n, q):
    return sum(comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(k, n + 1))


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return c - h, c + h


D, CAP = 0.82, (0.735, 0.921)
lo, hi = wilson(4, 8)
print("# RBT-104 adversary: P(SUPPORTED | H) under Amendment 3's attribution requirement\n")
print(f"d_c = 4/8 = 0.50, Wilson 95% [{lo:.3f}, {hi:.3f}]; d = {D}; S1 cap {CAP[0]}-{CAP[1]}\n")
print("| q_H | d_c | q_c | n = 10: P(count >= 5) | P(SUPPORTED \\| H) <= | n = 7: P(count >= 5) | P(SUPPORTED \\| H) <= |")
print("|---|---|---|---|---|---|---|")
for qh in (0.5, 0.3):
    for dc in (lo, 0.5, hi):
        qc = min(1.0, qh * dc / D)
        p10, p7 = ge(5, 10, qc), ge(5, 7, qc)
        print(f"| {qh} | {dc:.3f} | {qc:.3f} | {p10:.3f} | {p10 * CAP[0]:.3f}-{p10 * CAP[1]:.3f} | {p7:.3f} | {p7 * CAP[0]:.3f}-{p7 * CAP[1]:.3f} |")
print("\nAmendment 3's stated figure is the q_H = 0.5, d_c = 0.50, n = 10 row.")
