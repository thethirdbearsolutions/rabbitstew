"""RBT-125 world gate, part C: the R6 side effects of the perception pack (REGISTRATION.md §C).  Solo seasons, 15 s.

  founders   RBT-113's generation-0 founders at seed 1 (40 per fauna, drawn exactly as Experiment draws them:
             initial_population(kind, config, spawn_streams(1)[kind]) on RBT-113's U-arm config), 8 start draws each
             (126000..126007), in every condition.  Per fauna: mean items, mean net (items - 0.03 x kJ), and the share
             SOLVENT (mean net >= the ecology's living cost 0.25 per season) -- solo, so a founder's arena is its own.
  corpus     the committed ecology corpus's living: RBT-90 part 2's seed-801 run at season 600 (state.json, 60 per
             fauna, restored from ckpt/rbt-90-801), 4 start draws each (127000..127003).  Per fauna: mean net and
             net / living cost -- the income / cost regime of R5, survivor-weighted (these are the living) and solo.
  tumbler    RBT-121 adversary section 7's blind tumbler: a 0.3 m cube with one box arm on an unlimited hinge at full
             throttle and no sensor (phys_rod.py's rod), arm 0.45 m and 6.46 m, 20 draws (2131..2150), on RBT-113's
             generation-1131 world; plus the same rod with an unused food nose on its root, under eat_from = sensor.

Conditions are the gate's worlds (worlds/<cell>) with, where named, one eating flag changed.

    side_effects.py BODIES_ROOT [--procs 4]     (BODIES_ROOT/forage-801/state.json)
"""
import argparse
import json
import os
import sys
from dataclasses import replace
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-113"))
import world as rbt113  # noqa: E402

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Node, Segment, Sensor, Shape  # noqa: E402
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402

LIVING_COST = 0.25
CONDS_FOUNDERS = ["U-G0", "U-G2.5", "U-G10", "PW-G0", "PW-G2.5", "PW-G10", "U-G0/root", "U-G0/sensor", "U-G0/surface",
                  "U-G0/clear-geoms", "PW-G2.5/root", "PW-G2.5/sensor"]
CONDS_CORPUS = ["U-G0", "U-G2.5", "U-G10", "U-G0/root", "U-G0/sensor", "U-G0/surface", "U-G0/clear-geoms"]
FLAG = {"root": {"eat_from": "root"}, "sensor": {"eat_from": "sensor"}, "surface": {"eat_rule": "surface"}, "clear-geoms": {"clear_from": "geoms"}}


def cond_cfg(cond, base=None):
    cell, _, flag = cond.partition("/")
    cfg = SimConfig.from_dict(json.load(open(os.path.join(HERE, "worlds", cell, "config.json")))["sim"])
    if base is not None:  # the tumbler: RBT-113's generation world with the cell's food block
        cfg = replace(base, food=cfg.food)
    if flag:
        cfg = replace(cfg, food=replace(cfg.food, **FLAG[flag]))
    return cfg


def rod(a, nose=False):
    arm = Segment(Shape.BOX, (float(a), 1.0, 1.0), Brain(units=[Effector(dof=0, bias=3.0)]))
    conn = Connection(child=1, position=(1.0, 0.0, 0.0), scale=1.0, joint_type=JointType.HINGE, axis=(0.0, 0.0, 1.0), joint_limit=None)
    root = Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=[Sensor("food")] if nose else []))
    return Genotype(nodes=[Node(root, [conn]), Node(arm)], name="rod")


def season(task):
    key, gd, cfg, seed = task
    g = Genotype.from_dict(gd)
    cfg = replace(cfg, random_start=True)
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    sim.run()
    return key, sim.harvest(0)["food"], sim.food_score(0)


def run(tasks, procs):
    with get_context("fork").Pool(procs) as pool:
        rows = pool.map(season, tasks, chunksize=8)
    out = {}
    for key, f, n in rows:
        out.setdefault(key, []).append((f, n))
    return {k: np.array(v) for k, v in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bodies_root")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--part", choices=["founders", "corpus", "tumbler", "all"], default="all")
    a = ap.parse_args()

    if a.part in ("founders", "all"):
        evo = rbt113.evolution_config("U", "", seed=1)
        streams = spawn_streams(1)
        founders = {kind: [m.genotype.to_dict() if hasattr(m, "genotype") else m.to_dict() for m in initial_population(kind, evo, streams[kind]).members]
                    for kind in (HOLISTIC, CONVENTIONAL)}
        seeds = [126000 + i for i in range(8)]
        tasks = [((c, kind, i), gd, cond_cfg(c), s) for c in CONDS_FOUNDERS for kind in founders for i, gd in enumerate(founders[kind]) for s in seeds]
        R = run(tasks, a.procs)
        print(f"# founders: RBT-113 seed-1 generation 0, {len(founders[HOLISTIC])} + {len(founders[CONVENTIONAL])}, {len(seeds)} solo draws each")
        print("| condition | fauna | items | net | solvent (net >= 0.25) | any food | items vs U-G0 |")
        print("|---|---|---|---|---|---|---|")
        for c in CONDS_FOUNDERS:
            for kind in founders:
                per = np.array([R[(c, kind, i)].mean(axis=0) for i in range(len(founders[kind]))])
                ref = np.array([R[("U-G0", kind, i)].mean(axis=0) for i in range(len(founders[kind]))])
                rel = per[:, 0].sum() / ref[:, 0].sum() - 1 if ref[:, 0].sum() > 0 else float("nan")
                print(f"| {c} | {kind} | {per[:, 0].mean():.3f} | {per[:, 1].mean():+.3f} | {(per[:, 1] >= LIVING_COST).mean():.2f} | "
                      f"{(per[:, 0] > 0).mean():.2f} | {100 * rel:+.0f}% |", flush=True)

    if a.part in ("corpus", "all"):
        st = json.load(open(os.path.join(a.bodies_root, "forage-801", "state.json")))
        seeds = [127000 + i for i in range(4)]
        pops = {kind: st["populations"][kind] for kind in (HOLISTIC, CONVENTIONAL)}
        tasks = [((c, kind, i), gd, cond_cfg(c), s) for c in CONDS_CORPUS for kind in pops for i, gd in enumerate(pops[kind]) for s in seeds]
        R = run(tasks, a.procs)
        print(f"\n# corpus: RBT-90 part 2 seed 801, the living at season {st['season']} ({len(pops[HOLISTIC])} + {len(pops[CONVENTIONAL])}), {len(seeds)} solo draws each")
        print("| condition | fauna | items | net | net / living cost | below cost | items vs U-G0 |")
        print("|---|---|---|---|---|---|---|")
        for c in CONDS_CORPUS:
            for kind in pops:
                per = np.array([R[(c, kind, i)].mean(axis=0) for i in range(len(pops[kind]))])
                ref = np.array([R[("U-G0", kind, i)].mean(axis=0) for i in range(len(pops[kind]))])
                print(f"| {c} | {kind} | {per[:, 0].mean():.3f} | {per[:, 1].mean():+.3f} | {per[:, 1].mean() / LIVING_COST:.2f} | "
                      f"{(per[:, 1] < LIVING_COST).mean():.2f} | {100 * (per[:, 0].sum() / ref[:, 0].sum() - 1):+.0f}% |", flush=True)

    if a.part in ("tumbler", "all"):
        base = generation_sim(rbt113.evolution_config("U", "", seed=1), 1131)
        seeds = list(range(2131, 2151))
        conds = ["U-G0", "U-G0/root", "U-G0/sensor", "U-G0/surface", "U-G0/clear-geoms", "PW-G0", "PW-G0/root", "PW-G2.5/root"]
        tasks = []
        for L in (0.45, 6.46):
            aa = (L / 0.3) ** 1.5
            for c in conds:
                tasks += [((L, c, False), rod(aa).to_dict(), cond_cfg(c, base), s) for s in seeds]
            tasks += [((L, "U-G0/sensor", True), rod(aa, nose=True).to_dict(), cond_cfg("U-G0/sensor", base), s) for s in seeds]
        R = run(tasks, a.procs)
        print(f"\n# tumbler (RBT-121 adversary section 7): one full-throttle hinge, no sensor, {len(seeds)} draws, RBT-113's world at terrain 1131")
        print("| arm (m) | condition | food | net | +/- SE (net) |")
        print("|---|---|---|---|---|")
        for key in R:
            x = R[key]
            print(f"| {key[0]:.2f} | {key[1]}{' + an unused root nose' if key[2] else ''} | {x[:, 0].mean():.2f} | {x[:, 1].mean():+.2f} | "
                  f"{x[:, 1].std(ddof=1) / np.sqrt(len(x)):.2f} |", flush=True)


if __name__ == "__main__":
    main()
