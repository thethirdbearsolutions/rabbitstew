"""How often does one reproduction event flip the direction of travel?

This is RBT-77's load-bearing parameter. The pedigree evidence for it is biased:
it compares CHAMPIONS, and both members of a champion pair had to win their
generation, so it says nothing clean about ordinary offspring.

Here the run's own mutation operator is applied to a champion, with the run's
own MutationConfig, and the offspring measured directly. Unbiased, and the
sample size is whatever we pay for.

Reads: a direction flip rate near zero means the trait is stably inherited and
the RBT-77 sabotage mechanism is unavailable - a lineage carrying a compass
keeps its sign. A rate near 0.5 means the sign a nose->wheel circuit needs is
re-randomised almost every generation, and no chemotactic wiring can accumulate.

Caveat carried in the output: the run uses crossover_rate 0.5, so half of real
reproductions also recombine. This measures the mutation channel only.

Usage: python scripts/direction_heritability.py [offspring_per_parent] [procs]
"""
import json, sys, numpy as np
from dataclasses import replace
from multiprocessing import Pool
from rabbitstew.genotype import Genotype
from rabbitstew.genetics import mutate_controller, MutationConfig
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout

RUN = "runs/RBT-23/W4b-801"
raw = json.load(open(f"{RUN}/config.json"))
cfg = SimConfig.from_dict(raw["sim"])
MUT = raw["mutation"]
PARENTS = [140, 200, 300, 400, 500, 590]   # 140 drives forward; the rest backward
SEEDS = 5


def mutation_config():
    """The run's own mutation parameters, not the library defaults."""
    import dataclasses
    from rabbitstew.genotype import BrainVocabulary
    names = {f.name for f in dataclasses.fields(MutationConfig)}
    vals = {k: v for k, v in MUT.items() if k in names}
    if isinstance(vals.get("vocab"), dict):
        vals["vocab"] = BrainVocabulary.from_dict(vals["vocab"])
    return dataclasses.replace(MutationConfig(), **vals)


def wrap(a):
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def circ(v):
    return float(np.degrees(np.arctan2(np.mean(np.sin(v)), np.mean(np.cos(v)))))


def direction_of(g):
    T = []
    for seed in range(9000, 9000 + SEEDS):
        c = replace(cfg, random_start=True)
        sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
        sim.set_food_seed(seed)
        idx = sim.robots[0]
        last = sim.data.xpos[idx.root_body][:2].copy()
        for _ in range(int(round(c.duration / c.control_dt))):
            sim.step()
            if sim.exploded[0]:
                break
            q = sim.data.xquat[idx.root_body]
            yaw = float(np.arctan2(2 * (q[0] * q[3] + q[1] * q[2]),
                                   1 - 2 * (q[2] ** 2 + q[3] ** 2)))
            pos = sim.data.xpos[idx.root_body][:2]
            d = pos - last
            if np.linalg.norm(d) > 1e-3:
                T.append(wrap(float(np.arctan2(d[1], d[0])) - yaw))
            last = pos.copy()
    if not T:
        return None, 0.0
    R = float(np.hypot(np.mean(np.sin(T)), np.mean(np.cos(T))))
    return circ(T), R


def child(task):
    gen, k = task
    p = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    rng = np.random.default_rng([gen, k])
    c = mutate_controller(p, rng, mutation_config())
    m, R = direction_of(c)
    return gen, k, m, R


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    par_dir = {}
    for gen in PARENTS:
        m, R = direction_of(Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json"))
        par_dir[gen] = ("BACK" if abs(m) > 90 else "fwd", m, R)
    tasks = [(gen, k) for gen in PARENTS for k in range(n)]
    with Pool(procs) as p:
        rows = p.map(child, tasks)

    print(f"Direction heritability across one mutation event")
    print(f"{RUN}, mutate_controller with the run's own MutationConfig, "
          f"{len(PARENTS)} parents x {n} offspring, {SEEDS} seeds each\n")
    print("| parent gen | parent dir | offspring measured | flipped | flip rate | mean R |")
    print("|---|---|---|---|---|---|")
    rates = []
    for gen in PARENTS:
        sub = [r for r in rows if r[0] == gen and r[2] is not None]
        if not sub:
            continue
        pf = par_dir[gen][0]
        flips = sum(1 for _, _, m, _ in sub if ("BACK" if abs(m) > 90 else "fwd") != pf)
        rate = flips / len(sub)
        rates.append(rate)
        print(f"| {gen} | {pf} ({par_dir[gen][1]:+.0f}°) | {len(sub)} | {flips} | "
              f"**{rate:.2f}** | {np.mean([r[3] for r in sub]):.2f} |")
    rng = np.random.default_rng(5)
    bs = np.array([rng.choice(rates, len(rates)).mean() for _ in range(20000)])
    print(f"\npooled flip rate {np.mean(rates):.3f}  "
          f"95% CI over parents [{np.percentile(bs,2.5):.3f}, {np.percentile(bs,97.5):.3f}]")
    print("\nThe run also uses crossover_rate 0.5; this is the mutation channel only.")
