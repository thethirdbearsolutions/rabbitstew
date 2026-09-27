"""RBT-121 audit B, probe 1: what the operator does to body and brain size when selection is absent.

    python runs/RBT-121/ga/drift_lineage.py > runs/RBT-121/ga/drift_lineage.txt

Reads the committed RBT-113 lineage.jsonl of every seed directory (O1-O4, Z1-Z4; 24 directories).  The C line is
RBT-113's drift-matched control: 10 of 40 parents drawn uniformly, no selection.  Whatever C's size traits do between
generation 0 and generation 23 is the operator's own drift (plus sampling drift, which has no direction).  U and D are
printed beside it.  No simulation, no scored code touched.
"""
import glob
import json
import os
from collections import defaultdict

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "RBT-113")
TRAITS = ("nodes", "parts", "units", "links", "mass")


def main():
    acc = defaultdict(list)  # (fauna, line, trait) -> per-directory (gen0 mean, gen23 mean)
    dirs = sorted(d for d in glob.glob(os.path.join(ROOT, "[OZ]*", "*")) if os.path.isdir(d))
    for d in dirs:
        for line in "UDC":
            p = os.path.join(d, line, "lineage.jsonl")
            by = defaultdict(lambda: defaultdict(list))
            with open(p) as f:
                for row in f:
                    r = json.loads(row)
                    if r["generation"] in (0, 23):
                        for t in TRAITS:
                            if t in r:
                                by[(r["population"], r["generation"])][t].append(r[t])
            for fauna in ("holistic", "conventional"):
                for t in TRAITS:
                    a, b = by[(fauna, 0)][t], by[(fauna, 23)][t]
                    if a and b:
                        acc[(fauna, line, t)].append((np.mean(a), np.mean(b)))
    print(f"# {len(dirs)} seed directories; per-directory line means at generation 0 and 23; mean over directories,")
    print("# and how many directories moved up (the C line is the operator's drift under no selection)")
    for fauna in ("holistic", "conventional"):
        for line in "CUD":
            cells = []
            for t in TRAITS:
                v = np.array(acc[(fauna, line, t)])
                if len(v) == 0:
                    continue
                up = int((v[:, 1] > v[:, 0] + 1e-9).sum())
                cells.append(f"{t} {v[:, 0].mean():6.2f} -> {v[:, 1].mean():6.2f} ({v[:, 1].mean() / max(v[:, 0].mean(), 1e-9):4.2f}x, up {up}/{len(v)})")
            print(f"{fauna:12s} {line}  " + " | ".join(cells))


if __name__ == "__main__":
    main()
