"""RBT-101 readout adversary: separate the furniture's arithmetic from a response, at the same seasons, by simulation.

The observed recovery R-shift of a fauna is  gain(shift population, flat) - gain(base population, random).  Adding and
subtracting gain(base population, flat) splits it exactly into
    REFUND    gain(base pop, flat)  - gain(base pop, random)   what flat ground pays the baseline's own gaits then
    RESPONSE  gain(shift pop, flat) - gain(base pop, flat)     what the shift population's gaits do better on flat
                                                               than the baseline's gaits of the same season
Both are measured here on the same draws, the ecology's own way (rabbitstew.simulation.run_group, four of a fauna to
an arena, the run's config), for three populations per seed and fauna, read from the restored bulk's genomes and
lineage (README rule 6: no table is read from a checkpoint):
    C0     alive in the baseline at T - 1 (the onset population; the same in every arm)
    base   alive in the baseline at T + 110 (the middle of the recovery window)
    shift  alive in the shift arm at T + 110
Groups: each population shuffled into groups of four by a fixed stream; D draws, each draw a start seed shared by
every population and both terrains; random terrain takes terrain seed = the draw, as the ecology does.

--check SEED reproduces one real season of the baseline (season T - 1, its own cohorts, start seed and terrain seed)
bout by bout against lineage.jsonl's recorded gains, so the harness is the ecology's.

    python runs/RBT-101/readout-adversary/probe_refund.py BULKDIR --check 3
    python runs/RBT-101/readout-adversary/probe_refund.py BULKDIR [D] > runs/RBT-101/readout-adversary/probe_refund.txt
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
LAB = {"holistic": "co-evolved", "conventional": "designed"}
MID = 110


def cfg_of(run):
    return SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])


def world(cfg, terrain, seed):
    w = replace(cfg.world, terrain=terrain, terrain_seed=(int(seed) if terrain == "random" else None))
    return replace(cfg, world=w)


def alive(run, kind, s):
    out = []
    for line in open(f"{run}/lineage.jsonl"):
        r = json.loads(line)
        if r["generation"] == s and r["population"] == kind and "food" in r:  # played season s
            out.append(r["name"])
    return out


def task(args):
    run, kind, names, cfg_d, terrain, seed = args
    cfg = world(SimConfig.from_dict(cfg_d), terrain, seed)
    gs = [Genotype.load(f"{run}/{kind}/genomes/{n}.json") for n in names]
    return [r["score"] for r in run_group(gs, cfg, seed)]


def check(bulk, seed):
    run = f"{bulk}/base-{seed}"
    s = TS[seed] - 1
    h = [e for e in json.load(open(f"{run}/history.json"))["history"] if e["season"] == s]
    rec = {}
    for line in open(f"{run}/lineage.jsonl"):
        r = json.loads(line)
        if r["generation"] == s and "food" in r:
            rec[(r["population"], r["name"])] = r["last_score"]
    cfg = cfg_of(run)
    n = bad = 0
    for line in open(f"{run}/cohorts.jsonl"):
        c = json.loads(line)
        if c["season"] != s:
            continue
        kind = c["cohort"]
        ts = [e["terrain_seed"] for e in h if e["population"] == kind][0]
        sim = replace(cfg, world=replace(cfg.world, terrain_seed=int(ts)))
        for grp in c["groups"][:4]:
            gs = [Genotype.load(f"{run}/{kind}/genomes/{m['name']}.json") for m in grp]
            got = [r["score"] for r in run_group(gs, sim, c["start_seed"])]
            for m, g in zip(grp, got):
                n += 1
                bad += round(g, 4) != round(rec[(kind, m["name"])], 4)
                print(f"   {kind:12s} {m['name']:8s} recorded {rec[(kind, m['name'])]:+.4f} re-simulated {g:+.4f}")
    print(f"CHECK seed {seed} season {s}: {n - bad}/{n} bouts reproduce the recorded gain to 4 decimals")


def main(bulk, D):
    cfgd = json.load(open(f"{bulk}/base-{SEEDS[0]}/config.json"))["sim"]
    jobs, keys = [], []
    for s in SEEDS:
        T = TS[s]
        rnd = random.Random(f"RBT-101 refund {s}")
        draws = [rnd.randrange(1, 2**31 - 1) for _ in range(D)]
        pops = {}
        for k in KINDS:
            pops[("C0", k)] = (f"{bulk}/base-{s}", alive(f"{bulk}/base-{s}", k, T - 1))
            pops[("base", k)] = (f"{bulk}/base-{s}", alive(f"{bulk}/base-{s}", k, T + MID))
            pops[("shift", k)] = (f"{bulk}/shift-{s}", alive(f"{bulk}/shift-{s}", k, T + MID))
        for (p, k), (run, names) in pops.items():
            for d, seed in enumerate(draws):
                order = names[:]
                random.Random(f"{s} {p} {k} {d}").shuffle(order)
                for gi in range(0, len(order), 4):
                    grp = order[gi:gi + 4]
                    for terrain in ("random", "flat"):
                        jobs.append((run, k, grp, cfgd, terrain, seed))
                        keys.append((s, p, k, terrain, d, len(grp)))
    with ProcessPoolExecutor(int(os.environ.get("WORKERS", "4"))) as ex:
        res = list(ex.map(task, jobs, chunksize=2))
    acc = {}
    for (s, p, k, terrain, d, n), out in zip(keys, res):
        acc.setdefault((s, p, k, terrain), []).extend(out)
    G = {key: st.fmean(v) for key, v in acc.items()}
    print(__doc__.split("\n\n")[0])
    print(f"D = {D} draws per population and terrain; populations of 54-60 per fauna in groups of four; mid-recovery season T + {MID}")
    print()

    def stat(label, v):
        n, m, sd, hw = R.stat(v)
        return f"{label:52s} {m:+.4f} [{m - hw:+.4f}, {m + hw:+.4f}] pos {sum(x > 0 for x in v)}/{n}  per seed [{', '.join(f'{x:+.3f}' for x in v)}]"

    out = {}
    for k in KINDS:
        print(f"{LAB[k]} (mean gain per robot-bout, simulated)")
        out[("c0", k)] = [G[(s, "C0", k, "flat")] - G[(s, "C0", k, "random")] for s in SEEDS]
        out[("refund", k)] = [G[(s, "base", k, "flat")] - G[(s, "base", k, "random")] for s in SEEDS]
        out[("resp", k)] = [G[(s, "shift", k, "flat")] - G[(s, "base", k, "flat")] for s in SEEDS]
        out[("total", k)] = [G[(s, "shift", k, "flat")] - G[(s, "base", k, "random")] for s in SEEDS]
        out[("respr", k)] = [G[(s, "shift", k, "random")] - G[(s, "base", k, "random")] for s in SEEDS]
        print("   " + stat("C0 refund, flat - random (the onset population)", out[("c0", k)]))
        print("   " + stat(f"REFUND at T+{MID}: base pop, flat - random", out[("refund", k)]))
        print("   " + stat(f"RESPONSE at T+{MID}: shift pop - base pop, both flat", out[("resp", k)]))
        print("   " + stat("  the same on random terrain (shift pop - base pop)", out[("respr", k)]))
        print("   " + stat("TOTAL = REFUND + RESPONSE (simulated R-shift)", out[("total", k)]))
        print("   " + stat("the refund's drift, T+110 against C0", [a - b for a, b in zip(out[("refund", k)], out[("c0", k)])]))
        print()
    print("paired (co-evolved - designed)")
    for lab, key in (("C0 refund", "c0"), (f"REFUND at T+{MID}", "refund"), (f"RESPONSE at T+{MID}", "resp"), ("TOTAL (simulated event - base)", "total")):
        print("   " + stat(lab, [a - b for a, b in zip(out[(key, "holistic")], out[(key, "conventional")])]))
    obs = [R.rbody(R.Arm(f"runs/RBT-101/shift-{s}"), TS[s] + 60, TS[s] + 160) - R.rbody(R.Arm(f"runs/RBT-90/forage-{s}"), TS[s] + 60, TS[s] + 160) for s in SEEDS]
    print("   " + stat("observed event - base, recovery (readout.txt)", obs))
    tot = [a - b for a, b in zip(out[("total", "holistic")], out[("total", "conventional")])]
    print(f"   per-seed r(simulated TOTAL, observed) {st.correlation(tot, obs):+.2f}")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "--check":
        check(sys.argv[1], int(sys.argv[3]))
    else:
        main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 4)
