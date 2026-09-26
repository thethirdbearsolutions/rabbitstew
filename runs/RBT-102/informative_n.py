"""RBT-102, after the adversary (coordinator ruling 16:55): at what genome count would a zero become
informative against drift?

Reads the adversary's committed matched drift null, `runs/RBT-102/adversary/replay_null-rows.txt`
(one row per arm and replay: each arm's own founders and pedigree, one `mutate_controller` per birth,
never scored). No simulation, no new data.

The unit is one ten-arm set: 12,276 genomes, the same founders, pedigrees and depths as RBT-102. The
100 replay sets are independent draws of that unit, so for k independent sets
P(0 | drift) = p0^k, where p0 is the per-set zero fraction. The answer is the smallest k with
p0^k < 0.05, given in genomes as k x 12,276.

A Poisson reading (P(0) = exp(-mean carriers)) is printed beside it for contrast only. Carriers
under drift are clustered: one arrival is inherited by its descendants, so a replay reads either 0 or
several. That clustering makes P(0) far higher than Poisson says, and the Poisson n is therefore an
underestimate. It is not the answer.

    python runs/RBT-102/informative_n.py
"""
import json
import math
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "adversary", "replay_null-rows.txt")


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return max(0.0, c - h), min(1.0, c + h)


def need(p0, alpha=0.05):
    """Smallest k with p0**k < alpha."""
    if p0 <= 0.0:
        return 1
    if p0 >= 1.0:
        return math.inf
    return math.floor(math.log(alpha) / math.log(p0)) + 1


def main():
    text = open(ROWS).read().strip()
    rows = json.loads(text) if text.startswith("[") else [json.loads(l) for l in text.splitlines() if l.strip()]
    sets = defaultdict(lambda: [0, 0, 0])  # rep -> [arms, genomes, carriers]
    for r in rows:
        s = sets[r["rep"]]
        s[0] += 1
        s[1] += r["genomes"]
        s[2] += r["carriers"]
    full = {k: v for k, v in sets.items() if v[0] == 10}
    n_sets = len(full)
    genomes = {v[1] for v in full.values()}
    assert len(genomes) == 1, genomes
    G = genomes.pop()
    zeros = sum(1 for v in full.values() if v[2] == 0)
    mean_c = sum(v[2] for v in full.values()) / n_sets
    p0 = zeros / n_sets
    lo, hi = wilson(zeros, n_sets)
    print("# RBT-102: the genome count at which a zero becomes informative against matched drift\n")
    print(f"source: runs/RBT-102/adversary/replay_null-rows.txt ({len(rows)} rows, {n_sets} complete ten-arm sets)")
    print(f"one set = {G} genomes (RBT-102's denominator)\n")
    print(f"per-set P(0 | drift) = {zeros}/{n_sets} = {p0:.2f} [{lo:.2f}, {hi:.2f}] (Wilson 95%)")
    print(f"mean carriers per set under drift = {mean_c:.2f} ({100 * mean_c / G:.4f}% of genomes)\n")
    print("| P(0) per set | sets needed for P(0 | drift) < 0.05 | genomes | arms of RBT-90 part-2 size |")
    print("|---|---|---|---|")
    for label, p in (("point", p0), ("Wilson low", lo), ("Wilson high", hi)):
        k = need(p)
        print(f"| {label} {p:.2f} | {k} | {k * G:,} | {10 * k} |")
    k_pois = math.log(20) / mean_c
    print(f"\ncontrast only (Poisson, ignores clustering): {k_pois:.1f} sets = {k_pois * G:,.0f} genomes."
          f" Poisson gives P(0 | one set) = {math.exp(-mean_c):.2f}, against the observed {p0:.2f}, so it"
          f" understates the n needed.")


if __name__ == "__main__":
    main()
