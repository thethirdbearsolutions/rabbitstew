"""W1 gate check (#484): how "at least half" and "at least one" behave as the number of screen hosts N grows.

    python runs/RBT-116/design-adversary/w1_gate_hosts.py > runs/RBT-116/design-adversary/w1_gate_hosts.txt

RBT-116 §1.1 names the screen's hosts only as "the positive-control hosts of G8(a) and G8(c)", and G8 has 4 designed + 4
holistic hosts per unit, 192 in all.  The registration does not fix N, and both rules depend on it strongly.  Exact
binomial arithmetic, no simulation, no W1 data.  Model: a draw has a per-host eat probability p_d.  Half the hosts
(the G8(c) plants, as in the fixture and RBT-129's HP) never eat, and the other half eat at 2·p_d.  Draw classes:
- "typical": p_d = 0.25 (a mean eat rate of 0.25, as the fixture and RBT-129's cells);
- "hard": p_d = 0.02 (a near-hopeless layout: MUST 1's M2 worry), 10% of draws.
Reported per N: P(admit | typical) and P(admit | hard) under each rule, and each rule's admitted share of the pool.
"""
from math import comb


def tail(n, p, k):
    """P(Binomial(n, p) >= k)."""
    return sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


print("# w1_gate_hosts.py: screen admission vs N screen hosts (half never eat, the rest at 2 p_d); typical p_d 0.25, hard p_d 0.02 (10% of draws)")
print(f"{'N':>4s} | {'>= half: typical':>16s} {'hard':>8s} {'pool share':>10s} | {'>= 1: typical':>13s} {'hard':>8s} {'pool share':>10s}")
for N in (8, 12, 16, 32, 48, 96, 192):
    eaters = N // 2
    half = -(-N // 2)
    row = []
    for rule_k in (half, 1):
        t = tail(eaters, 2 * 0.25, rule_k)
        h = tail(eaters, 2 * 0.02, rule_k)
        row += [t, h, 0.9 * t + 0.1 * h]
    print(f"{N:4d} | {row[0]:16.3f} {row[1]:8.3f} {row[2]:10.3f} | {row[3]:13.3f} {row[4]:8.3f} {row[5]:10.3f}")
print("# ('>= half' with half the hosts never eating needs EVERY eater to eat; '>= 1' at large N admits even hard draws.)")
