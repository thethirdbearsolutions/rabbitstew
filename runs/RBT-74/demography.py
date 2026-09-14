"""Manipulation check for morphological innovation protection (RBT-74): does the mechanism do
what it is named for?  From lineage.jsonl, per generation: births by type (free-slot, readaptation,
elite), novel bodies (morph_age 0), distinct body plans, and, over the run, the fitness of
readaptation children against their parents' beside the same for free-slot children.

    python runs/RBT-74/demography.py RUN [--every N]

No simulation.  File analysis only.
"""
import json
import statistics as st
import sys
from collections import Counter, defaultdict


def main(run, every=1):
    recs = [json.loads(l) for l in open(f"{run}/lineage.jsonl")]
    hol = [r for r in recs if r["population"] == "holistic"]
    by = defaultdict(list)
    for r in hol:
        by[r["generation"]].append(r)
    name = {r["name"]: r for r in hol}
    print(f"{run}: holistic births by generation")
    print("gen  free readapt elite  novel  bodies  mean_age   best   mean  parts(best)")
    for g in sorted(by):
        if g % every and g != max(by):
            continue
        rs = by[g]
        c = Counter(r.get("birth") for r in rs)
        ages = [r["morph_age"] for r in rs if r.get("morph_age") is not None]
        best = max(rs, key=lambda r: r["fitness"])
        print(f"{g:3d}  {c.get('free', 0):4d} {c.get('readapt', 0):7d} {c.get('elite', 0):5d}  {sum(1 for r in rs if r.get('morph_age') == 0):5d}  {len({r.get('body') for r in rs}):6d}  {st.mean(ages) if ages else float('nan'):8.2f}  {best['fitness']:.3f}  {st.mean(r['fitness'] for r in rs):.3f}  {best.get('parts', 0):5d}")
    d = defaultdict(list)
    for r in hol:
        b = r.get("birth")
        if b in ("free", "readapt") and r["parents"] and r["parents"][0] in name:
            d[b].append(r["fitness"] - name[r["parents"][0]]["fitness"])
    print("\nchild minus parent fitness (all generations):")
    for k, v in d.items():
        if v:
            print(f"  {k:8} n={len(v):5d}  mean {st.mean(v):+.4f}  median {st.median(v):+.4f}  share improved {sum(x > 0 for x in v) / len(v):.2f}")
    novel = [r for r in hol if r.get("morph_age") == 0 and r["parents"] and r["parents"][0] in name]
    if novel:
        v = [r["fitness"] - name[r["parents"][0]]["fitness"] for r in novel]
        print(f"  {'novel':8} n={len(v):5d}  mean {st.mean(v):+.4f}  median {st.median(v):+.4f}  share improved {sum(x > 0 for x in v) / len(v):.2f}   (free-slot children whose body changed)")
    # Did readaptation recover what the body change cost?  For each protected lineage: fitness at
    # age 0 versus its carrier's fitness at the end of the window.
    end_age = max((r["morph_age"] for r in hol if r.get("morph_age") is not None), default=0)
    if any(r.get("birth") == "readapt" for r in hol):
        k = max(r["morph_age"] for r in hol if r.get("birth") == "readapt")
        gains = []
        for r in hol:
            if r.get("birth") == "readapt" and r["morph_age"] == k:
                cur = r
                ok = True
                for _ in range(k):
                    if not cur["parents"] or cur["parents"][0] not in name:
                        ok = False
                        break
                    cur = name[cur["parents"][0]]
                if ok and cur.get("morph_age") == 0:
                    gains.append(r["fitness"] - cur["fitness"])
        if gains:
            print(f"\nreadapted lineage at age {k} minus the same lineage at age 0: n={len(gains)}  mean {st.mean(gains):+.4f}  median {st.median(gains):+.4f}  share improved {sum(x > 0 for x in gains) / len(gains):.2f}")


if __name__ == "__main__":
    every = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 1
    main(sys.argv[1], every)
