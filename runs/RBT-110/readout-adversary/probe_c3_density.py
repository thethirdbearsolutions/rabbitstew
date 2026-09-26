"""RBT-110 readout adversary: C3's designed RESPONSE on near-extinct seeds, matched for arena size.

At T + 110 the designed fauna of C3's shift arm is 1, 2, 5, 6 and 15 strong on seeds 805, 1, 801, 2 and 4.  The split
cuts a shuffled population into arenas of four with the remainder as a smaller last arena (as the ecology does), so
these populations forage partly or wholly in arenas of 1-3 robots on 6 items, against a baseline population foraging
in fours.  On scarce food, fewer mouths per arena is income by itself.  This probe reads the baseline's designed
population on the same new world (6 items, random terrain = the draw, the adversary's draws and shuffle stream) cut
into arenas of 1, 2, 3 and 4, and forms
    RESPONSE_as_run      gain(shift pop, as cut) - gain(base pop, fours)                      (the analysts')
    RESPONSE_matched     gain(shift pop, as cut) - sum_g w_g gain(base pop, arenas of g)      w_g = the share of the
                                                                                               shift pop in arenas of g
    density effect       RESPONSE_as_run - RESPONSE_matched
Post hoc and descriptive; the pre-registered read (groups as run) is unchanged.

    python runs/RBT-110/readout-adversary/probe_c3_density.py BULK > runs/RBT-110/readout-adversary/probe_c3_density.txt
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

SEEDS, TS = R.SEEDS, R.onsets()
D, r, K = 4, 110, "conventional"
SMALL = [805, 1, 801, 2, 4]


def alive(run, s):
    return [x["name"] for x in map(json.loads, open(f"{run}/lineage.jsonl"))
            if x["generation"] == s and x["population"] == K and "food" in x]


def task(a):
    run, names, cfgd, seed = a
    cfg = SimConfig.from_dict(cfgd)
    cfg = replace(cfg, world=replace(cfg.world, terrain="random", terrain_seed=int(seed)), food=replace(cfg.food, items=6))
    return [x["score"] for x in run_group([Genotype.load(f"{run}/{K}/genomes/{n}.json") for n in names], cfg, seed)]


def main(bulk):
    cfgd = json.load(open(f"{bulk}/base-{SEEDS[0]}/config.json"))["sim"]
    jobs, keys = [], []
    for s in SMALL:
        T = TS[s]
        rnd = random.Random(f"RBT-101 refund {s}")
        draws = [rnd.randrange(1, 2**31 - 1) for _ in range(D)]
        for p, arm in (("shift", "s100"), ("base", "base")):
            run = f"{bulk}/{arm}-{s}"
            names = alive(run, T + r)
            for d, seed in enumerate(draws):
                order = names[:]
                random.Random(f"{s} {p} {K} {d}").shuffle(order)
                for g in ((4,) if p == "shift" else (1, 2, 3, 4)):
                    for gi in range(0, len(order), g):
                        grp = order[gi:gi + g]
                        jobs.append((run, grp, cfgd, seed))
                        keys.append((s, p, g, len(grp), len(names)))
    with ProcessPoolExecutor(int(os.environ.get("WORKERS", "4"))) as ex:
        res = list(ex.map(task, jobs, chunksize=2))
    acc, sizes, npop = {}, {}, {}
    for (s, p, g, n, N), out in zip(keys, res):
        npop[(s, p)] = N
        if p == "shift":
            acc.setdefault((s, "shift"), []).extend(out)
            sizes.setdefault(s, []).extend([n] * n)  # one entry per robot: the size of its arena
        elif n == g:  # base: arenas of exactly g (drop the ragged remainder so each level is a pure arena size)
            acc.setdefault((s, "base", g), []).extend(out)
    print(__doc__.split("\n\n")[0])
    print()
    print("seed  n_shift n_base  shift robots by arena size   base gain in arenas of 1 / 2 / 3 / 4     shift gain  "
          "RESPONSE as run  matched  density effect")
    ra, rm = [], []
    for s in SMALL:
        sh = st.fmean(acc[(s, "shift")])
        b = {g: st.fmean(acc[(s, "base", g)]) for g in (1, 2, 3, 4)}
        cnt = {g: sizes[s].count(g) for g in (1, 2, 3, 4)}
        w = {g: cnt[g] / len(sizes[s]) for g in cnt}
        matched = sh - sum(w[g] * b[g] for g in b)
        asrun = sh - b[4]
        ra.append(asrun)
        rm.append(matched)
        print(f"{s:4d}  {npop[(s, 'shift')]:7d} {npop[(s, 'base')]:6d}  {str({g: cnt[g] for g in cnt if cnt[g]}):28s} "
              f"{b[1]:+.3f} / {b[2]:+.3f} / {b[3]:+.3f} / {b[4]:+.3f}     {sh:+.3f}      {asrun:+.3f}        {matched:+.3f}   {asrun - matched:+.3f}")
    print(f"mean over these {len(SMALL)} seeds: as run {st.fmean(ra):+.3f}, matched {st.fmean(rm):+.3f}")
    print("(the base 'arenas of 4' figure drops the ragged last arena, so it can differ from the analysts' base read in"
          " the third decimal)")


if __name__ == "__main__":
    main(sys.argv[1])
