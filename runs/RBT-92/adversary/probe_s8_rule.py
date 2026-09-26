"""RBT-92 adversary probe D: does RBT-89 section 8's onset rule really have no solution on a selected arm?

Section 8: a turnover peak is a ten-season window in which one population's deaths reach 20; T is
placed at least 20 seasons after the last peak.  Read literally (the last peak window before T,
either fauna, ends at or before T - 20), this lists every T that satisfies it on RBT-71's committed
selected runs (the files cohort_cycle.py reads), in the candidate range [120, 400] (T <= 400 keeps
the tail inside 600 seasons).  No run; deaths only.

    python runs/RBT-92/adversary/probe_s8_rule.py > runs/RBT-92/adversary/probe_s8_rule.txt
"""
import csv
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "RBT-71")


def spans(ts):
    out = []
    for t in ts:
        if out and t == out[-1][1] + 1:
            out[-1][1] = t
        else:
            out.append([t, t])
    return ", ".join(f"{a}-{b}" if a != b else str(a) for a, b in out) or "none"


print(__doc__.split("\n\n")[0])
print()
for seed in (804, 805, 806):
    rows = list(csv.DictReader(open(os.path.join(ROOT, f"forage-{seed}", "seasons.txt")), delimiter="\t"))
    d = {(int(r["season"]), r["population"]): int(r["deaths"]) for r in rows}
    peak = lambda s, p: sum(d.get((x, p), 0) for x in range(s, s + 10)) >= 20
    for pops in (("holistic",), ("conventional",), ("holistic", "conventional")):
        ok = [T for T in range(120, 401) if not any(peak(s, p) for p in pops for s in range(T - 29, T))]
        print(f"forage-{seed} {'+'.join(pops):23s} T in [120,400] satisfying section 8 literally: {spans(ok)}  "
              f"({len(ok)} seasons; in the design's [340,400]: {sum(1 for t in ok if t >= 340)})")
