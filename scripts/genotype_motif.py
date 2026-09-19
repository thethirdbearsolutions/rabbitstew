"""Install the compass motif into the GENOTYPE, so it is heritable and mutable.

Required by RBT-65, which asks whether selection can hold a compass it is given.
Every compass measurement in this programme so far has written into the
PHENOTYPE weight matrix (sim.brains[0].W) after construction, which cannot be
inherited and cannot be mutated.

THE DIRECT MOTIF IS NOT GENOTYPE-REPRESENTABLE. A link into node N's brain may
take its source only from N itself, from the global brain, or from a
NEIGHBOURING node (genotype.py:496). The two drive wheels are SIBLINGS -
neighbours(1) == [0] - so `nose on wheel 1 -> effector on wheel 2`, which the
4-link antisymmetric motif needs twice, is rejected by the validator. Every
+0.897 measurement in this programme installed a circuit the encoding forbids.

What IS representable is the same computation routed through the global brain:

    n1 --(+1)--> [global tanh neuron k] --(w)--> e1
    n2 --(-1)-->                        --(w)--> e2

which puts 2*w*tanh(n1 - n2) on the steering axis where the direct motif puts
2*w*(n1 - n2). tanh is linear in the operating regime (RBT-69 measured the
median left-right nose gap at 0.056 and p95 at 0.086), so the two deliver the
same command until the gap approaches 1, which it never does. The routed
version saturates at 2w; the direct one does not.

Usage: python scripts/genotype_motif.py   (verifies and measures the prize)

NOTE (RBT-87): because the path is length two, `rabbitstew.analysis.steering_terms`
reads a = 0, balance = 0, opposed = 0 on this motif at its default depth 1; the
installed 2w appears in `path["a"]` at depth=2 (tests/test_steering_terms.py).
"""
import copy, json, sys, numpy as np
from dataclasses import replace
from multiprocessing import Pool
from rabbitstew.genotype import Genotype, UnitRef, Link, Neuron
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN = "runs/RBT-23/W4b-801"
cfg = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
GENS = (90, 190, 290, 390, 490, 550, 590)
NOSE, EFF = 2, 0          # index within each wheel node's brain
WHEELS = (1, 2)


def install(g, w, sign=+1.0):
    """Routed antisymmetric motif, in the genotype. Returns a new Genotype."""
    r = copy.deepcopy(g)
    if r.global_brain is None:
        from rabbitstew.genotype import Brain
        r.global_brain = Brain()
    gb = r.global_brain
    gb.units.append(Neuron(bias=0.0, func="tanh"))
    k = len(gb.units) - 1
    gb.links.append(Link(UnitRef(WHEELS[0], NOSE), UnitRef(None, k), +sign))
    gb.links.append(Link(UnitRef(WHEELS[1], NOSE), UnitRef(None, k), -sign))
    for nd in WHEELS:
        r.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, EFF), w))
    problems = r.validate()
    if problems:
        raise RuntimeError("installed motif is invalid: " + "; ".join(problems))
    return r


def direct_is_illegal(g):
    """Demonstrate that the textbook 4-link motif cannot be written here."""
    d = copy.deepcopy(g)
    d.nodes[2].segment.brain.links.append(Link(UnitRef(1, NOSE), UnitRef(2, EFF), 1.0))
    return d.validate()


def bout(task):
    gen, seed, cond, w = task
    c = replace(cfg, random_start=True)
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    if cond == "motif":
        g = install(g, w)
    elif cond == "anti":
        g = install(g, w, sign=-1.0)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
    return gen, seed, cond, w, float(sim.food_eaten[0])


if __name__ == "__main__":
    nseeds = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    seeds = [9000 + i for i in range(nseeds)]

    g0 = Genotype.load(f"{RUN}/conventional/best_gen0590.json")
    print("Genotype representability")
    print(f"  neighbours(1) = {g0.neighbours(1)}  -> wheels are siblings, not neighbours")
    bad = direct_is_illegal(g0)
    print(f"  direct n1->e2 link: {'REJECTED' if bad else 'accepted'} - {bad[0] if bad else ''}")
    print(f"  routed motif validates: {not install(g0, 32.0).validate()}")

    conds = [("base", 0.0)] + [("motif", w) for w in (8.0, 16.0, 32.0)] + [("anti", 32.0)]
    tasks = [(gn, s, c, w) for gn in GENS for s in seeds for c, w in conds]
    with Pool(procs) as p:
        rows = p.map(bout, tasks, chunksize=16)
    by = {(r[0], r[1], r[2], r[3]): r[4] for r in rows}
    base = float(np.mean([by[(gn, s, "base", 0.0)] for gn in GENS for s in seeds]))
    rng = np.random.default_rng(5)
    print(f"\nGenotype-installed routed motif, {len(GENS)} robots x {nseeds} paired seeds")
    print(f"baseline {base:.3f} items\n")
    print("| condition | w | delta items | 95% CI | robots improved |")
    print("|---|---|---|---|---|")
    for c, w in conds[1:]:
        per = [float(np.mean([by[(gn, s, c, w)] - by[(gn, s, "base", 0.0)] for s in seeds])) for gn in GENS]
        bs = np.array([rng.choice(per, len(per)).mean() for _ in range(20000)])
        print(f"| {c} | {w:g} | {np.mean(per):+.3f} | "
              f"[{np.percentile(bs,2.5):+.3f}, {np.percentile(bs,97.5):+.3f}] | "
              f"{sum(1 for x in per if x > 0)}/{len(GENS)} |")
