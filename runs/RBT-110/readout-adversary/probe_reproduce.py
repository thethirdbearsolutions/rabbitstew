"""RBT-110 readout adversary: an independent re-implementation of the four splits' new-world reads at T + 110.

Written from the pre-registration and runs/RBT-101/readout-adversary/probe_refund.py, not from the analysts' scripts.
For each challenge, seed and fauna it simulates, on the challenge's NEW world only, the populations
    base    alive in the RBT-90 part 2 baseline at T + 110
    shift   alive in the challenge's shift arm at T + 110
    cull20  alive in RBT-92's cull20 arm at T + 110
with the adversary's draws (Random("RBT-101 refund SEED"), D = 4) and shuffles (Random("SEED POP KIND DRAW")), cut
into arenas of the challenge's group size (8 on C1, 4 elsewhere; the remainder a smaller last group, as ecology.py
_challenge cuts), and prints one mean gain per (challenge, seed, population, fauna, draw).

Two membership rules:
    lineage  the adversary's and the analysts' rule: a lineage.jsonl row at generation T + 110 with "food"
             (so the per-seed RESPONSE must reproduce the analysts' split.txt to the printed 3 decimals);
    played   everyone in cohorts.jsonl's groups at T + 110.  The lineage rule misses the robots that aged out at
             the season's end (they have no row at that generation; RBT-110 C4null's check found one).  The same
             shuffle stream on a longer list re-cuts every group, so the played read is also a re-grouping of the
             same population: its difference from the lineage read measures the harness's grouping noise.
             (base and shift only.)

    python runs/RBT-110/readout-adversary/probe_reproduce.py BULK > runs/RBT-110/readout-adversary/probe_reproduce.raw
BULK holds base-SEED, s92-SEED, s99-SEED, s100-SEED, s101-SEED, c20-SEED (ckpt/rbt-90, rbt-92-shift, rbt-99-shift,
rbt-100-shift, rbt-101-shift, rbt-92-cull20; restored with scripts/durable.sh restore).
"""
import json
import os
import random
import statistics as st
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-92"))
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, run_group  # noqa: E402

os.chdir(ROOT)
import readout as R  # noqa: E402

SEEDS, KINDS, TS = R.SEEDS, R.KINDS, R.onsets()
D, r = 4, 110
SHIFT = {"C1": "s92", "C2": "s99", "C3": "s100", "C4null": "s101"}
GSZ = {"C1": 8, "C2": 4, "C3": 4, "C4null": 4}


def new_world(ch, cfg, seed):
    if ch == "C4null":
        return replace(cfg, world=replace(cfg.world, terrain="flat", terrain_seed=None))
    cfg = replace(cfg, world=replace(cfg.world, terrain="random", terrain_seed=int(seed)))
    if ch == "C2":
        cfg = replace(cfg, food=replace(cfg.food, work_cost=0.08))
    if ch == "C3":
        cfg = replace(cfg, food=replace(cfg.food, items=6))
    return cfg


def members(run, kind, s, rule):
    if rule == "lineage":
        out = []
        for line in open(f"{run}/lineage.jsonl"):
            x = json.loads(line)
            if x["generation"] == s and x["population"] == kind and "food" in x:
                out.append(x["name"])
        return out
    lin = members(run, kind, s, "lineage")
    played = []
    for line in open(f"{run}/cohorts.jsonl"):
        c = json.loads(line)
        if c["season"] == s and c["cohort"] == kind:
            played = [m["name"] for g in c["groups"] for m in g]
    return lin + sorted(n for n in played if n not in set(lin))


def covered(run, s):
    return s < int(json.load(open(f"{run}/state.json"))["season"])


def task(a):
    ch, run, kind, names, cfgd, seed = a
    cfg = new_world(ch, SimConfig.from_dict(cfgd), seed)
    gs = [Genotype.load(f"{run}/{kind}/genomes/{n}.json") for n in names]
    return [x["score"] for x in run_group(gs, cfg, seed)]


def main(bulk):
    cfgd = json.load(open(f"{bulk}/base-{SEEDS[0]}/config.json"))["sim"]
    jobs, keys = [], []
    for ch in SHIFT:
        for s in SEEDS:
            T = TS[s]
            rnd = random.Random(f"RBT-101 refund {s}")
            draws = [rnd.randrange(1, 2**31 - 1) for _ in range(D)]
            for p, arm in (("base", "base"), ("shift", SHIFT[ch]), ("cull20", "c20")):
                run = f"{bulk}/{arm}-{s}"
                if not covered(run, T + r):
                    continue
                for rule in ("lineage", "played"):
                    if rule == "played" and p == "cull20":
                        continue
                    for k in KINDS:
                        names = members(run, k, T + r, rule)
                        for d, seed in enumerate(draws):
                            order = names[:]
                            random.Random(f"{s} {p} {k} {d}").shuffle(order)
                            g = GSZ[ch]
                            for gi in range(0, len(order), g):
                                jobs.append((ch, run, k, order[gi:gi + g], cfgd, seed))
                                keys.append((ch, s, p, k, rule, d, len(names)))
    print(f"# {len(jobs)} group bouts", file=sys.stderr, flush=True)
    with ProcessPoolExecutor(int(os.environ.get("WORKERS", "4"))) as ex:
        res = list(ex.map(task, jobs, chunksize=4))
    acc = {}
    for key, out in zip(keys, res):
        acc.setdefault(key, []).extend(out)
    print("challenge seed pop fauna rule draw n_alive mean_gain")
    for key in sorted(acc, key=str):
        ch, s, p, k, rule, d, n = key
        print(f"{ch} {s} {p} {k} {rule} {d} {n} {st.fmean(acc[key]):+.6f}")


if __name__ == "__main__":
    main(sys.argv[1])
