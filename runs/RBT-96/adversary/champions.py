"""RBT-96 adversary, item 1: re-measure the final-fifth champions from the restored bulk.

Reads only the bulk restored from ckpt/rbt-96-SEED-ARM (history.json, champions_genNNNN/*.json,
config.json); it never reads a table out of a checkpoint (generations.txt is compared, not used).

  python runs/RBT-96/adversary/champions.py [--seeds 201 202 203 204] [--fresh 6] [--workers 4]

Sections printed (and written to champions.txt beside this file):
  A. in-run, re-derived from history.json: the final-fifth mean per arm and d; explosions.
  B. calibration: gen 249's champion bouts replayed on their own terrain seed; must equal history.json.
  C. fresh draws: the same 11 checkpoints x 5 x 5 x 2 round robin, on terrain seeds the run never saw.
  D. foreign opponents (seed 201 only): each arm's final-fifth holistic champions against the gen-249
     wheeled champions of seeds 202-204, on fresh terrains. Is s1-201's edge general or opponent-specific?
  E. solo capability (analysis.capability_profile) of all 55 final-fifth holistic champions per arm,
     with a fresh terrain bank.
"""
import argparse, json, os, statistics as st, sys, time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

from rabbitstew.analysis import TrialConfig, capability_profile
from rabbitstew.evolution import EvolutionConfig, generation_sim, _bout_task
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.dirname(HERE)
FRESH_BASE = 1_900_000_000  # fresh terrain seeds FRESH_BASE + j; asserted absent from every run's terrain draws
FOREIGN_TERRAINS = 2
NAN = float("nan")


def sim_of(run):
    return SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])


def final_fifth(run):
    h = json.load(open(f"{run}/history.json"))
    return [c for c in h["champions"] if c["generation"] >= 200], [r["terrain_seed"] for r in h["history"]]


def champs(run, kind, gen):
    d = f"{run}/{kind}/champions_gen{gen:04d}"
    return [Genotype.load(f"{d}/{f}").to_dict() for f in sorted(os.listdir(d), key=lambda f: int(f.split('.')[0]))]


def roundrobin(hs, cs, sim):
    return [(h, c, sim, swap, None) for h in hs for c in cs for swap in (False, True)]


def bouts(pool, tasks):
    rs = list(pool.map(_bout_task, tasks, chunksize=4))
    return [r["fitness"][0] for r in rs], sum(any(r["exploded"]) for r in rs)


def _cap(args):
    g, sim, trials = args
    p = capability_profile(Genotype.from_dict(g), sim, trials)
    return p["approach"]["progress"], p["steering"]["successes"], p["terrain"]["success_rate"], p["approach"]["exploded"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="*", default=[201, 202, 203, 204])
    ap.add_argument("--fresh", type=int, default=6)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--skip-solo", action="store_true")
    a = ap.parse_args()
    out = []
    say = lambda s="": (print(s, flush=True), out.append(s))
    fresh = [FRESH_BASE + j for j in range(a.fresh)]
    pool = ProcessPoolExecutor(a.workers)
    t0 = time.time()
    say(f"RBT-96 adversary item 1: champions re-measured from the restored bulk; fresh terrain seeds {fresh[0]}..{fresh[-1]}")
    rows = {}
    for seed in a.seeds:
        runs = {arm: f"{RUNS}/{arm}-{seed}" for arm in ("s0", "s1")}
        ff, terr = {}, set()
        for arm, run in runs.items():
            ff[arm], t = final_fifth(run)
            terr |= set(t) | {c["terrain_seed"] for c in ff[arm]}
        assert not terr & set(fresh), "a fresh seed was a training draw"
        gens = [c["generation"] for c in ff["s0"]]
        assert gens == [c["generation"] for c in ff["s1"]] and len(gens) == 11, gens
        sim = sim_of(runs["s0"])
        assert sim == sim_of(runs["s1"])
        # the wheeled champions must be the same genomes in both arms
        for g in gens:
            assert champs(runs["s0"], "conventional", g) == champs(runs["s1"], "conventional", g), (seed, g)
        say(f"\n=== seed {seed}: final-fifth checkpoints {gens[0]}..{gens[-1]} (n={len(gens)}); wheeled champions byte-identical across arms: True")
        # A. in-run from history.json
        inrun = {arm: [c["holistic_mean_fitness"] for c in ff[arm]] for arm in runs}
        expl = {arm: sum(any(b["exploded"]) for c in ff[arm] for b in c["bouts"]) for arm in runs}
        committed = {}
        for arm, run in runs.items():  # compared only, never used
            lines = [l.split("\t") for l in open(f"{run}/generations.txt").read().splitlines()[1:]]
            committed[arm] = st.mean(float(l[13]) for l in lines if l[13] and int(l[0]) >= 200)
        say(f"A. in-run (history.json): s0 {st.mean(inrun['s0']):.4f}  s1 {st.mean(inrun['s1']):.4f}  d {st.mean(inrun['s1']) - st.mean(inrun['s0']):+.4f}"
            f"   committed generations.txt agrees: {all(abs(st.mean(inrun[k]) - committed[k]) < 5e-6 for k in runs)}   exploded bouts s0 {expl['s0']}/550 s1 {expl['s1']}/550")
        say("   per checkpoint d (s1-s0): " + " ".join(f"{b - x:+.2f}" for x, b in zip(inrun["s0"], inrun["s1"])))
        # B. calibration: replay gen 249 on its own terrain seed
        last = {arm: ff[arm][-1] for arm in runs}
        rep = {}
        for arm, run in runs.items():
            s = generation_sim(EvolutionConfig(sim=sim), last[arm]["terrain_seed"])
            f, _ = bouts(pool, roundrobin(champs(run, "holistic", 249), champs(run, "conventional", 249), s))
            rep[arm] = (float(np.mean(f)), last[arm]["holistic_mean_fitness"])
        say("B. replay of gen 249 (harness calibration): " + "  ".join(f"{arm} {x:.6f} vs history {y:.6f} {'EXACT' if abs(x - y) < 1e-12 else 'DIFFERS'}" for arm, (x, y) in rep.items()))
        # C. fresh draws
        fr = {arm: [] for arm in runs}  # per checkpoint, mean over fresh terrains
        fexpl = {arm: 0 for arm in runs}
        for arm, run in runs.items():
            for g in gens:
                hs, cs = champs(run, "holistic", g), champs(run, "conventional", g)
                vals = []
                for ts in fresh:
                    f, e = bouts(pool, roundrobin(hs, cs, generation_sim(EvolutionConfig(sim=sim), ts)))
                    vals.append(float(np.mean(f))); fexpl[arm] += e
                fr[arm].append(vals)
        m = {arm: float(np.mean(fr[arm])) for arm in runs}
        dts = [float(np.mean([fr["s1"][i][j] for i in range(11)]) - np.mean([fr["s0"][i][j] for i in range(11)])) for j in range(len(fresh))]
        dck = [float(np.mean(fr["s1"][i]) - np.mean(fr["s0"][i])) for i in range(11)]
        say(f"C. fresh draws ({len(fresh)} terrains x 550 bouts per arm): s0 {m['s0']:.4f}  s1 {m['s1']:.4f}  d {m['s1'] - m['s0']:+.4f}"
            f"   d per fresh terrain: {' '.join(f'{x:+.3f}' for x in dts)}  (SD {st.stdev(dts) if len(dts) > 1 else NAN:.3f})   exploded s0 {fexpl['s0']} s1 {fexpl['s1']}")
        say("   per checkpoint fresh d: " + " ".join(f"{x:+.2f}" for x in dck) + f"   corr(in-run ckpt d, fresh ckpt d) {np.corrcoef([b - x for x, b in zip(inrun['s0'], inrun['s1'])], dck)[0, 1]:+.2f}")
        rows[seed] = dict(inrun=st.mean(inrun["s1"]) - st.mean(inrun["s0"]), fresh=m["s1"] - m["s0"], s0=m["s0"], s1=m["s1"])
        # D. foreign opponents (seed 201 only)
        if seed == 201:
            for fseed in (202, 203, 204):
                fcs = champs(f"{RUNS}/s0-{fseed}", "conventional", 249)
                fm = {}
                for arm, run in runs.items():
                    f = []
                    for g in gens:
                        for ts in fresh[:FOREIGN_TERRAINS]:
                            f += bouts(pool, roundrobin(champs(run, "holistic", g), fcs, generation_sim(EvolutionConfig(sim=sim), ts)))[0]
                    fm[arm] = float(np.mean(f))
                say(f"D. vs seed {fseed}'s gen-249 wheeled champions ({FOREIGN_TERRAINS} fresh terrains, {len(f)} bouts per arm): s0 {fm['s0']:.4f}  s1 {fm['s1']:.4f}  d {fm['s1'] - fm['s0']:+.4f}")
        # E. solo capability, all 55 champions per arm, fresh terrain bank
        if not a.skip_solo:
            trials = TrialConfig(terrain_seeds=tuple(range(1000, 1012)))
            cap = {}
            for arm, run in runs.items():
                gs = [h for g in gens for h in champs(run, "holistic", g)]
                cap[arm] = list(pool.map(_cap, [(h, sim, trials) for h in gs], chunksize=2))
            q = lambda arm, k: float(np.mean([c[k] for c in cap[arm]]))
            say(f"E. solo, 55 champions per arm: approach s0 {q('s0', 0):+.2f} m  s1 {q('s1', 0):+.2f} m  d {q('s1', 0) - q('s0', 0):+.2f}"
                f" | steering/3 s0 {q('s0', 1):.2f} s1 {q('s1', 1):.2f} | terrain (12 fresh) s0 {q('s0', 2):.2f} s1 {q('s1', 2):.2f} d {q('s1', 2) - q('s0', 2):+.2f}"
                f" | exploded s0 {sum(c[3] for c in cap['s0'])} s1 {sum(c[3] for c in cap['s1'])}")
            rows[seed].update(solo_d=q("s1", 0) - q("s0", 0), terr_d=q("s1", 2) - q("s0", 2))
        say(f"   [{time.time() - t0:.0f} s]")
    if len(rows) > 1:
        say("\n=== summary: A/A d in-run against fresh draws")
        say("seed   in-run d   fresh d   solo approach d   terrain d")
        for s, r in rows.items():
            say(f"{s}    {r['inrun']:+.3f}     {r['fresh']:+.3f}    {r.get('solo_d', float('nan')):+.2f}             {r.get('terr_d', float('nan')):+.2f}")
        for k in ("inrun", "fresh"):
            d = [r[k] for r in rows.values()]
            rms = float(np.sqrt(np.mean(np.square(d))))
            say(f"{k:7s} RMS {rms:.4f}  SD {st.stdev(d):.4f}  h = 2.776*RMS/2 = {2.776 * rms / 2:.3f}")
        d_in, d_fr = [r["inrun"] for r in rows.values()], [r["fresh"] for r in rows.values()]
        say(f"corr(in-run d, fresh d) {np.corrcoef(d_in, d_fr)[0, 1]:+.3f}")
    open(os.path.join(HERE, "champions.txt" if a.seeds == [201, 202, 203, 204] else f"champions-{'-'.join(map(str, a.seeds))}.txt"), "w").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
