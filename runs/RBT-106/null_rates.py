"""RBT-106 amendment (adversary F3, coordinator 22:40): the false-positive rate of HELD under the FULL operator
(crossover then mutation), scored as amended: k_planted = k - k_bare against B; k_bare reported apart.

Reads the design adversary's committed null_xover readouts (`adversary/null_xover/xnull-*.txt`: part 2's ten
real genealogies, the founders planted at part 2's founders, the ecology's own operator, 20 replicates per
seed and cell, seasons 150, 300 and 599; and `adversary/null_xover_deep/`, the depth proxy x2 / x3), parsed with
the adversary's own `pool_xnull.parse` (imported).  Every replicate records k(k_bare)/n/B, so both rules come
from the same draws:

  as registered (PR #213)   HELD at a season iff k > B            (k counts bare-rooted transfer)
  as amended                HELD at a season iff k_planted > B    (k_planted = k - k_bare: the population n and
                                                                   mu describe; k_bare printed apart)

Printed per cell and operator: HELD at 150 (the H gate's season), at 300, at 599, at both 300 and 599 (the
arm-level call), and P(at least one of two gate seeds reads HELD at 150), the gate's chance of CONTINUE under
the null.

Usage: null_rates.py [null_xover | null_xover_deep]
"""
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("rbt106_pool_xnull", os.path.join(_HERE, "adversary", "pool_xnull.py"))
px = importlib.util.module_from_spec(_s)
_s.loader.exec_module(px)


def main():
    sub = sys.argv[1] if len(sys.argv) > 1 else "null_xover"
    print(f"# RBT-106: false-positive rate of HELD, full operator, adversary's {sub} draws, 10 seeds x 20 replicates\n")
    print("| cell | operator | rule | HELD at 150 | HELD at 300 | HELD at 599 | **HELD at 300 and 599** | gate: P(>= 1 of 2 seeds HELD at 150) |")
    print("|---|---|---|---|---|---|---|---|")
    for cell, label in px.CELLS:
        for op, name in (("x", "full"), ("m", "mutation only")):
            rows = []
            for s in px.SEEDS:
                rows += px.parse(os.path.join(_HERE, "adversary", sub, f"xnull-{cell}-{s}.txt"))[op]
            if not rows:
                continue
            for rule, held in (("k > B (registered)", lambda c: c["k"] > c["B"]),
                               ("k_planted > B (amended)", lambda c: c["k"] - c["kb"] > c["B"])):
                h = [[held(c) for c in r] for r in rows]
                tot = len(h)
                g = sum(x[0] for x in h) / tot
                both = sum(x[1] and x[2] for x in h)
                print(f"| {label} | {name} | {rule} | {sum(x[0] for x in h)}/{tot} | {sum(x[1] for x in h)}/{tot} | "
                      f"{sum(x[2] for x in h)}/{tot} | **{both}/{tot} = {100 * both / tot:.1f}%** | {1 - (1 - g) ** 2:.2f} |")


if __name__ == "__main__":
    main()
