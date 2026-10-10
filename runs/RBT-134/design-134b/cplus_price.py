"""RBT-134b: price the C+ rate ladder from the committed parents' structure and the operator's rates (arithmetic only).

Reads only `parent_checks.txt` (committed parents, no lineage) and the mutation rates it prints.  No RBT-134 output and
no lineage is read or run.  Hazards per later mutation step on a plant made after step d (R = 19 - d steps remain):

  clean   remove_unit picks the planted unit:                 remove_unit_rate / (n_global + 1)
  remnant remove_link pops an in-leg (global brain):          remove_link_rate x 2 / (L_global + 2)
          remove_link pops an out-leg (a wheel brain):        remove_link_rate x (1/(L_left + 1) + 1/(L_right + 1))
          a leg is reset to N(0, 1) (sign coin vs the plant): weight_rate x weight_reset_rate x 4, half of it remnant
  deaf    the unit is re-typed to sign / differentiate / abs (deaf at b_k ~ 0 under +-drive): func_rate x 3/7
          (and a same-sign reset leaves a structure too small for the rung: the other half of the reset hazard)

Hazards are held at the parent's values (add_link at 0.15 only lowers the out-leg hazard later, so remnants are
over-priced).  Yield = Y0 (parent_checks: depth-0 share >= a32) x P(no clean, remnant or deaf event).  The bias walk
of b_k and b_E is not priced: it is the reason for the factor w in [0.5, 1] on the yield.
"""
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
K, N = 19, 200_000
LADDER = (5e-5, 2e-4, 1e-3, 5e-3)  # the last is r3's C+ rate, for comparison only
B0_BG = 22 / 9_990  # r3 FC-M1's unflagged B0 background (DESIGN.md 9): the r3 clause's reference rate
N_BG = 40_000


def parents():
    txt = open(os.path.join(HERE, "parent_checks.txt")).read()
    rates = {}
    for block in re.split(r"\n## ", txt)[1:]:
        if "parents;" not in block:
            continue
        hdr = block.splitlines()[0]
        r = {k: float(v) for k, v in re.findall(r"(\w+_rate|max_units_per_brain) ([\d.]+)", hdr)}
        for row in re.findall(r"^\| \d+ \| yes \| yes \| yes \| (\d+) \| (\d+) \| (\d+)/(\d+) \| [^|]* \| ([\d.]+) \|$", block, re.M):
            ng, lg, ll, lr, y0 = int(row[0]), int(row[1]), int(row[2]), int(row[3]), float(row[4])
            yield r, ng, lg, ll, lr, y0
        rates.update(r)


def per_plant(r, ng, lg, ll, lr, y0, rem=0.1):
    h_clean = r["remove_unit_rate"] / (ng + 1)
    h_reset = r["weight_rate"] * r["weight_reset_rate"] * 4
    h_rem = rem * 2 / (lg + 2) + rem * (1 / (ll + 1) + 1 / (lr + 1)) + h_reset / 2
    h_deaf = r["func_rate"] * 3 / 7 + h_reset / 2
    h = h_clean + h_rem + h_deaf
    surv = sum(math.exp(-h * (K - d)) for d in range(1, K + 1)) / K
    remn = sum((1 - math.exp(-h * (K - d))) * h_rem / h for d in range(1, K + 1)) / K
    return y0 * surv, remn


def main():
    rows = list(parents())
    yields = [per_plant(*row) for row in rows]
    y = sum(a for a, _ in yields) / len(yields)
    rm = sum(b for _, b in yields) / len(yields)
    print(__doc__.split("\n\n")[0])
    print(f"\nparents {len(rows)}; mean yield per plant (w = 1) {y:.3f}; mean remnant share per plant {rm:.3f}\n")
    print("| rate per mutation | planted lineages per 200,000 | E[k a32], w = 1 | E[k], w = 0.5 | P(k >= 6) at w = 0.5 "
          "| P(k >= 20) at w = 0.5 | remnants in r3's 40,000 background (upper) | r3 clause: remnant share of the B0 rate |")
    print("|---|---|---|---|---|---|---|---|")
    for rate in LADDER:
        plant = 1 - (1 - rate) ** K
        ek1, ek5 = N * plant * y, N * plant * y * 0.5
        rem = N_BG * plant * rm
        print(f"| {rate:g} | {N * plant:.0f} | {ek1:.1f} | {ek5:.1f} | {1 - pois_cdf(5, ek5):.6f} | {1 - pois_cdf(19, ek5):.4f} "
              f"| {rem:.1f} | {rem / (N_BG * B0_BG):.2f}x |")


def pois_cdf(k, mu):
    return sum(math.exp(-mu) * mu ** j / math.factorial(j) for j in range(k + 1))


if __name__ == "__main__":
    main()
