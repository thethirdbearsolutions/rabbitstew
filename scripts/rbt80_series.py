"""RBT-80 (d): commit the series that sections 1, 3 and 5 rest on.

The adversary's finding 7: the carriage tables are committed and re-derivable,
but the YIELD table -- the one result that replicates 3/3 -- is not, because
`rbt80_report.py` reads `runs/RBT-80/*/history.json` and `lineage.jsonl`, both
correctly untracked under RBT-68's policy. RBT-86 is the general rule.

This writes, as a plain `.txt` under docs/artifacts/ and so inside the RBT-68
policy (no genomes shipped):

  * per-season `mean_lifetime_score` for all nine arms -- section 3's yield
  * per-season conventional `births` -- section 1's realised depth (sum/60)
  * the season 290 -> 299 demography rows -- section 5's transient

Usage: ./v/bin/python scripts/rbt80_series.py > docs/artifacts/RBT-80-series.txt
"""
import json, os, numpy as np

ROOT = "runs/RBT-80"
SEEDS = {"A": "seedA", "B": "seedB", "C": "seedC"}
ARMS = ("seeded", "control", "drift")


def conv(seed, arm):
    p = f"{ROOT}/{SEEDS[seed]}/{arm}/history.json"
    if not os.path.exists(p):
        return None
    return [e for e in json.load(open(p))["history"] if e["population"] == "conventional"]


def lineage(seed, arm):
    rec = {}
    for line in open(f"{ROOT}/{SEEDS[seed]}/{arm}/lineage.jsonl"):
        r = json.loads(line)
        if r["population"] == "conventional":
            rec.setdefault(r["generation"], []).append(r)
    return rec


if __name__ == "__main__":
    cols = [(s, a) for s in SEEDS for a in ARMS if conv(s, a)]
    print("RBT-80 per-season series, conventional population, all nine arms.")
    print("Committed so sections 1, 3 and 5 of the report are re-derivable by")
    print("someone other than the author (adversary finding 7; RBT-86).")
    print("No genomes are shipped: these are aggregate per-season numbers only.\n")

    print("## mean_lifetime_score by season  (section 3: yield = seeded - control)\n")
    print("season " + " ".join(f"{s}:{a:<8s}" for s, a in cols))
    H = {(s, a): conv(s, a) for s, a in cols}
    n = min(len(v) for v in H.values())
    for i in range(n):
        print(f"{H[cols[0]][i]['season']:6d} " +
              " ".join(f"{H[c][i]['mean_lifetime_score']:10.4f}" for c in cols))

    print("\n## births by season  (section 1: realised depth = total births / 60)\n")
    print("season " + " ".join(f"{s}:{a:<8s}" for s, a in cols))
    for i in range(n):
        print(f"{H[cols[0]][i]['season']:6d} " +
              " ".join(f"{H[c][i]['births']:10d}" for c in cols))

    print("\n## totals\n")
    print("| seed | arm | mean_lifetime_score mean | total births | realised depth |")
    print("|---|---|---|---|---|")
    for c in cols:
        b = sum(e["births"] for e in H[c])
        m = float(np.mean([e["mean_lifetime_score"] for e in H[c]]))
        print(f"| {c[0]} | {c[1]} | {m:.4f} | {b} | {b/60.0:.1f} |")

    print("\n## demography, season 290 -> 299  (section 5: the transient)\n")
    print("| seed | arm | mean age 290 | mean age 299 | turnover 290->299 | alive 290 | alive 299 |")
    print("|---|---|---|---|---|---|---|")
    for s, a in cols:
        rec = lineage(s, a)
        if 290 not in rec or 299 not in rec:
            continue
        base = {x["name"] for x in rec[290]}
        print(f"| {s} | {a} | {np.mean([x['age'] for x in rec[290]]):.1f} | "
              f"{np.mean([x['age'] for x in rec[299]]):.1f} | "
              f"{len({x['name'] for x in rec[299]} - base)}/60 | "
              f"{len(rec[290])} | {len(rec[299])} |")
