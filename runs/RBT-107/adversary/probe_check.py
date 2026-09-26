"""RBT-107 design adversary: does garden.py's harness reproduce a recorded season of the ecology, bout for bout?

    python runs/RBT-107/adversary/probe_check.py RUN_DIR SEASON [GROUPS]

garden.py never checks itself against the ecology (probe_refund.py did: probe_refund_check.txt, 32/32).  This runs
garden.py's own pieces (garden.base_sim(seed), BoutRunner.run_groups, an exploder gains 0) on one recorded season of a
no-event base arm: its cohorts' groups, start seed and terrain seed (history.json), and compares every member's gain
with lineage.jsonl's recorded last_score.  It also tallies, over every recorded season in [S0, SEASON], each member's
recorded gain by the size of the group it foraged in (cohorts.jsonl), because the garden, like the ecology, leaves a
short last group when n is not a multiple of four.  Base (no-event) arms only.
"""
import json
import os
import statistics as st
import sys
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import garden as Gd  # noqa: E402
from rabbitstew.evolution import BoutRunner  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402


def main(run, s, ngroups):
    seed = int(json.load(open(os.path.join(run, "config.json")))["seed"])
    sim0 = Gd.base_sim(seed)
    hist = [e for e in json.load(open(os.path.join(run, "history.json")))["history"] if e["season"] == s]
    rec, by = {}, {}
    s0 = s - 100
    for line in open(os.path.join(run, "lineage.jsonl")):
        r = json.loads(line)
        if s0 <= r["generation"] <= s and "food" in r:
            rec[(r["generation"], r["population"], r["name"])] = r["last_score"]
    runner = BoutRunner(sim0, 4)
    n = bad = 0
    for line in open(os.path.join(run, "cohorts.jsonl")):
        c = json.loads(line)
        if not (s0 <= c["season"] <= s):
            continue
        kind = c["cohort"] if isinstance(c["cohort"], str) else c["cohort"][0]
        for grp in c["groups"]:
            for m in grp:
                v = rec.get((c["season"], kind, m["name"]))
                if v is not None:
                    by.setdefault((kind, len(grp)), []).append(v)
        if c["season"] != s:
            continue
        ts = [e["terrain_seed"] for e in hist if e["population"] == kind][0]
        sim = replace(sim0, world=replace(sim0.world, terrain_seed=int(ts)))
        groups = c["groups"][:ngroups]
        res = runner.run_groups([([Genotype.load(os.path.join(run, kind, "genomes", f"{m['name']}.json")) for m in g], c["start_seed"]) for g in groups], sim)
        for g, rs in zip(groups, res):
            for m, r in zip(g, rs):
                got = 0.0 if r["exploded"] else float(r["score"])
                want = rec[(s, kind, m["name"])]
                n += 1
                bad += round(got, 4) != round(want, 4)
                print(f"   {kind:12s} {m['name']:8s} recorded {want:+.4f} garden harness {got:+.4f}")
    runner.close()
    print(f"CHECK seed {seed} season {s}: {n - bad}/{n} bouts reproduce the recorded gain to 4 decimals (garden.py's harness)")
    print(f"recorded gain by group size, seasons [{s0}, {s}] (the ecology's own leftover groups):")
    for k in sorted(by):
        v = by[k]
        print(f"   {k[0]:12s} group of {k[1]}: n {len(v):5d} mean gain {st.fmean(v):+.3f}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 4)
