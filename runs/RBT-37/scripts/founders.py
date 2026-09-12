import sys, json
from rabbitstew.analysis import read_lineage, founders
run = sys.argv[1]
lin = read_lineage(run)
out = {}
for kind in ("holistic", "conventional"):
    recs = [r for (p, n), r in lin.items() if p == kind]
    gmax = max(r["generation"] for r in recs)
    names = [r["name"] for r in recs if r["generation"] == gmax]
    out[kind] = {"generation": gmax, **founders(lin, kind, names)}
    print(kind, out[kind])
json.dump(out, open(f"{run}/founders.json", "w"), indent=1)
