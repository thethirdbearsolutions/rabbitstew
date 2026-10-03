"""RBT-128 design adversary: does fair.is_designed recognise every committed designed-fauna genome?

    python runs/RBT-128/design-adversary/designed_scan.py > runs/RBT-128/design-adversary/designed_scan.txt

Scans every committed genotype file under runs/ whose path names the conventional (designed) fauna, and every
file under a holistic/ path, and counts is_designed True/False.  A designed genome that reads False lets a
`simulate holistic.json designed.json` bout start with neither --fair nor --unfair-i-know.
"""
import collections
import glob
import json
import os

from rabbitstew.fair import is_designed
from rabbitstew.genotype import Genotype
from rabbitstew.fixed import drive_straight_genotype, pioneer_genotype, quadruped_genotype

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")


def main():
    import numpy as np
    print("# fixed constructors")
    for name, g in (("pioneer_genotype()", pioneer_genotype()), ("pioneer_genotype(rng, hidden=0)", pioneer_genotype(np.random.default_rng(1), hidden=0)),
                    ("drive_straight_genotype(0.6)", drive_straight_genotype(0.6)), ("quadruped_genotype()", quadruped_genotype())):
        print(f"  {name:34s} is_designed={is_designed(g)}")
    counts = collections.Counter()
    misses = collections.defaultdict(list)
    for path in sorted(glob.glob(os.path.join(ROOT, "runs", "**", "*.json"), recursive=True)):
        rel = os.path.relpath(path, ROOT)
        parts = rel.split(os.sep)
        kind = "conventional" if "conventional" in parts else ("holistic" if "holistic" in parts else None)
        if kind is None or os.path.basename(path) in ("config.json", "history.json", "state.json"):
            continue
        try:
            with open(path) as f:
                d = json.load(f)
            if not isinstance(d, dict) or "nodes" not in d:
                continue
            g = Genotype.from_dict(d)
        except Exception:
            continue
        r = is_designed(g)
        counts[(kind, r)] += 1
        if kind == "conventional" and not r:
            misses[os.path.dirname(rel)].append(os.path.basename(rel))
    print("# committed genomes: (fauna by path, is_designed) -> count")
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}")
    print("# designed-fauna directories whose genomes read is_designed=False (a mixed simulate bout with one starts unguarded)")
    for d in sorted(misses):
        print(f"  {d}: {len(misses[d])} files, e.g. {misses[d][0]}")


if __name__ == "__main__":
    main()
