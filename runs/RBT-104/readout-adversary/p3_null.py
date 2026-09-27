"""RBT-104 readout adversary, POST HOC: the single-season null rate that P3 lacked.

P3 in posthoc.txt counts 5 of 20 single-season window readings with k_planted > B and says the null's
single-season rate "was not computed". It can be computed from the committed Amendment 3 null tables
(runs/RBT-104/null_xover/xnull-w1-k8-SEED.txt, parsed by null_rates.py's own parse(), unchanged):
per seed and season, the fraction of the 20 no-selection replicates with k_planted = k - k_bare > B.
It then gives the expected count under the null and P(>= observed | null), independent Bernoulli per
reading (a Poisson-binomial; the two seasons of one seed are not independent in the null, and the
per-seed rates rest on 20 replicates, so this is a descriptive yardstick, not a test).

  p3_null.py [PEEK_DIR]   (PEEK_DIR holds S8-SEED/peek-a3-{300,599}.txt; default the checkout's runs/RBT-104)
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
_s = importlib.util.spec_from_file_location("rbt104_null_rates", os.path.join(BASE, "null_rates.py"))
nr = importlib.util.module_from_spec(_s)
_s.loader.exec_module(nr)


def observed(d, s, w):
    m = re.search(r"^WINDOW seed \d+ season \d+: k = (\d+), n = (\d+), B = (\d+)", open(os.path.join(d, f"S8-{s}", f"peek-a3-{w}.txt")).read(), re.M)
    return int(m.group(1)) > int(m.group(3))


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else BASE
    print("# POST HOC: single-season null rate of k_planted > B (full-operator null, 20 replicates per seed)\n")
    print("| seed | null rate at 300 | null rate at 599 | observed above at 300 | at 599 |")
    print("|---|---|---|---|---|")
    ps, obs, idx = [], 0, {300: 1, 599: 2}
    for s in nr.SEEDS:
        reps = nr.parse(s)["xover"]
        row = [s]
        for w in (300, 599):
            k = sum(r[idx[w]][0] - r[idx[w]][1] > r[idx[w]][3] for r in reps)
            ps.append((k + 0.0) / len(reps))
            row.append(f"{k}/{len(reps)}")
        for w in (300, 599):
            o = observed(d, s, w)
            obs += o
            row.append("above" if o else "-")
        print("| " + " | ".join(str(x) for x in row) + " |")
    pooled = sum(ps) / len(ps)
    print(f"\npooled single-season null rate: {pooled:.4f} (mean of 20 seed-season cells)")
    print(f"expected readings above B under the null, of 20: {sum(ps):.2f}; observed {obs}")
    print(f"P(>= {obs} of 20 | null), per-cell rates: {nr.poibin_ge(ps, obs):.4f}")
    # a cell with 0/20 has an upper bound, not a zero rate: repeat with each cell at max(rate, one-sided 95% upper of 0/20)
    hi0 = nr._hi(0, 20)
    ps2 = [max(p, hi0) if p == 0 else p for p in ps]
    print(f"  with every 0/20 cell set to its one-sided 95% upper bound ({hi0:.3f}): expected {sum(ps2):.2f}, "
          f"P(>= {obs}) {nr.poibin_ge(ps2, obs):.4f}")


if __name__ == "__main__":
    main()
