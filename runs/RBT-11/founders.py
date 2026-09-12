"""Founders at the final (or given) generation for both populations of runs/RBT-11/sims-901."""
import sys
from rabbitstew.analysis import read_lineage, founders
run = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-11/sims-901"
lin = read_lineage(run)
for kind in ("holistic", "conventional"):
    recs = [r for (p, n), r in lin.items() if p == kind]
    gmax = max(r["generation"] for r in recs)
    names = [r["name"] for r in recs if r["generation"] == gmax]
    print(kind, "generation", gmax, founders(lin, kind, names))
