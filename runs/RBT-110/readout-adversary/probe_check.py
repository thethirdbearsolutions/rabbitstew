"""RBT-110 readout adversary: re-check each split's NEW world against the shift arm's own recorded season T + 110,
on seeds the analysts did not check (first four recorded groups per fauna, recorded start seed and terrain seed),
with this adversary's own world construction (probe_reproduce.new_world, terrain seed replaced by the recorded one).
C4null's analyst checked only a pre-T season on random terrain; the flat world is checked here.

    python runs/RBT-110/readout-adversary/probe_check.py BULK > runs/RBT-110/readout-adversary/probe_check.txt
"""
import json
import os
import sys
from dataclasses import replace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_reproduce import SHIFT, TS, new_world  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, run_group  # noqa: E402

CHECKS = {"C1": (801, 7), "C2": (4, 801), "C3": (807, 801), "C4null": (1, 806)}


def check(bulk, ch, seed):
    run = f"{bulk}/{SHIFT[ch]}-{seed}"
    s = TS[seed] + 110
    h = [e for e in json.load(open(f"{run}/history.json"))["history"] if e["season"] == s]
    rec = {(x["population"], x["name"]): x["last_score"] for x in map(json.loads, open(f"{run}/lineage.jsonl"))
           if x["generation"] == s and "food" in x}
    cfg = SimConfig.from_dict(json.load(open(f"{bulk}/base-{seed}/config.json"))["sim"])  # the baseline's config
    n = bad = miss = 0
    sizes = []
    for c in map(json.loads, open(f"{run}/cohorts.jsonl")):
        if c["season"] != s:
            continue
        kind = c["cohort"]
        ts = [e["terrain_seed"] for e in h if e["population"] == kind][0]
        sim = new_world(ch, cfg, 1)
        if ch != "C4null":
            sim = replace(sim, world=replace(sim.world, terrain_seed=int(ts)))
        sizes.append(len(c["groups"][0]))
        for grp in c["groups"][:4]:
            got = [x["score"] for x in run_group([Genotype.load(f"{run}/{kind}/genomes/{m['name']}.json") for m in grp],
                                                 sim, c["start_seed"])]
            for m, g in zip(grp, got):
                if (kind, m["name"]) not in rec:
                    miss += 1
                    continue
                n += 1
                bad += round(g, 4) != round(rec[(kind, m["name"])], 4)
    print(f"{ch:6s} shift arm seed {seed:4d} season T+110 = {s} (recorded arena size {sizes}, terrain seeds {[e['terrain_seed'] for e in h]}): "
          f"{n - bad}/{n} recorded bouts reproduce to 4 decimals ({miss} robots with no row at s, simulated, not compared)")


if __name__ == "__main__":
    for ch, seeds in CHECKS.items():
        for sd in seeds:
            check(sys.argv[1], ch, sd)
