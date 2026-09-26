"""RBT-104, coordinator's condition 1 (17:02): P(each pre-registered "absent" outcome | magnitude is
the whole cause), at this design's n and depth, in THIS world (RBT-90's uniform one: the 17:46 note).

Inputs, all committed:
  * detection power of readout (b) on a population whose champions carry a paying compass:
    RBT-103's rotated-decoy readouts (`docs/artifacts/RBT-103-decoy-*.txt`), the installed a = 64
    motif's "motif - decoy" (= this design's F) with its t(6) interval over 7 bodies, in RBT-90's
    world.  Per population, power of "t(6) lower bound > 0" at that effect and standard error.
  * the uniform-world prize: +0.844 [+0.618, +1.070] at a = 64 (RBT-103, ten populations).
  * drift's arrivals for U8: 0.26 expected over ten arms (RBT-102 section 2.4), of which 3 of 84
    clear a = 64 at K = 8 (`drift-reach-k8.txt`) and half are correctly signed (paper 8 section 3.4).

The one quantity no file supplies is q, the probability that, if magnitude is the whole cause, an
S8 population's second-half champions carry a paying compass at all.  It is tabled, not assumed.
"""
import glob
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
T6 = 2.447


def tcdf_approx(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def binom_le(k, n, p):
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k + 1))


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "docs", "artifacts", "RBT-103-decoy-*.txt"))):
        m = re.search(r"motif - decoy\s+([-+]\d+\.\d+) \[\s*([-+]\d+\.\d+),\s*([-+]\d+\.\d+)\]", open(f).read())
        if m:
            mean, lo, hi = map(float, m.groups())
            se = (hi - lo) / (2 * T6)
            # power of "lower bound > 0" if the true effect is `mean` with this se (normal approx.)
            rows.append((os.path.basename(f)[len("RBT-103-decoy-"):-4], mean, se, tcdf_approx(mean / se - T6)))
    print("# RBT-104: matched-null power, in RBT-90's uniform world (condition 1; 17:46 note)\n")
    print("## Readout (b)'s power on one population whose champions carry a paying compass\n")
    print("  from RBT-103's installed a = 64 motif, motif - decoy (this design's F), t(6) over 7 bodies:")
    for name, mean, se, pw in rows:
        print(f"    population {name:>4s}: F {mean:+.3f}, se {se:.3f}, power {pw:.2f}")
    d = sum(r[3] for r in rows) / len(rows)
    print(f"  mean power d = {d:.2f} over {len(rows)} populations (effect at the uniform-world prize, +0.84 at a = 64)")

    print("\n## P(the pre-registered null | magnitude is the whole cause)\n")
    print("q = P(an S8 population's champions carry a paying compass | the hypothesis); each S8 population")
    print("then reads FOOD-DEPENDENT with p = q * d.  With 10 usable S8 populations (fewer: see the VOID rule):\n")
    print("| q | p = q d | P(FALSIFIED's count: <= 1 of 10) | P(SUPPORTED's count: >= 5 of 10) | P(no paying carrier in any S8 window) |")
    print("|---|---|---|---|---|")
    for q in (0.2, 0.3, 0.5, 0.7, 0.9):
        p = q * d
        print(f"| {q:.1f} | {p:.2f} | {binom_le(1, 10, p):.3f} | {1 - binom_le(4, 10, p):.3f} | {(1 - q) ** 10:.4f} |")
    print("\n  With only 7 usable (the VOID floor), P(<= 1 of 7) at q = 0.5 is "
          f"{binom_le(1, 7, 0.5 * d):.3f} and at q = 0.3 is {binom_le(1, 7, 0.3 * d):.3f}.")
    print("  Reading: FALSIFIED is a fair test of the hypothesis if it implies q >= ~0.5; at q = 0.2-0.3")
    print("  (selection keeps a compass in only a fifth to a third of populations) the null fires with")
    print("  substantial probability under the hypothesis, and the report must say FALSIFIED means")
    print("  'selection did not keep a paying compass in most populations', not 'in none'.")

    lam = 0.26 * (3 / 84) * 0.5
    print("\n## U8, the literal arm (no verdict; stated for the record)\n")
    print(f"  expected correctly signed, paying de novo arrivals over ten arms: 0.26 x 3/84 x 0.5 = {lam:.4f}")
    print(f"  P(no food-dependent U8 champion | the hypothesis) >= P(no such arrival) = exp(-{lam:.4f}) = {math.exp(-lam):.3f}")
    print(f"  P(no structural arrival at all in U8) = exp(-0.26) = {math.exp(-0.26):.3f}")


if __name__ == "__main__":
    main()
