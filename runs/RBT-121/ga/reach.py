"""RBT-121 audit B, probe 2: what one application of the holistic operator reaches (no simulation).

    python runs/RBT-121/ga/reach.py > runs/RBT-121/ga/reach.txt

Starts from RBT-113's holistic founders (seeds 1-4, the arm's own config via runs/RBT-113/world.py) and from a
neutral population walked 23 generations under the C line's own scheme (10 of 40 uniform parents, crossover 0.5,
`mutate`).  For each start it applies single `mutate` calls and measures, on the synthesised phenotype under the arm's
synthesis config and mass budget:

* sum gear: world.py's rule, 4 x the larger connected mass per driven DOF (torque motors and servos alike);
* driven DOFs, parts;
* link survival: the share of the parent's links (by src, dst) still present in the child, i.e. wiring erosion;
* food wiring: the number of (food sensor on segment i -> effector on segment j != i) routes, direct or through one
  global neuron, with nonzero weights: the raw structure a holistic compass needs (a smell gradient exists only
  between two segments in different places).  A NEW route is one the parent lacked.

It also measures crossover's node-count bias on pairs of unequal founders.
"""
import math
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "RBT-113"))
import world as W  # noqa: E402  (RBT-113's command line, read only)

from rabbitstew.evolution import HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genetics import crossover, mutate  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402
from rabbitstew.world import driven_dofs  # noqa: E402


def pheno(g, cfg):
    sc = cfg.sim
    ph = synthesize(g, sc.synthesis)
    dr = driven_dofs(ph)
    gear = sum(sc.world.motor_strength * max(ph.parts[p].mass, ph.parts[ph.parts[p].parent].mass) for p, _ in dr)
    ball = sum(1 for p, _ in dr if int(ph.parts[p].joint_type) == 1)
    return gear, len(dr), ball, len(ph.parts)


def link_keys(g):
    return Counter((owner, l.src, l.dst) for owner, b in g.brains() for l in b.links)


def food_routes(g):
    """(food-sensor node, effector node) pairs with i != j joined directly or via one global neuron."""
    food = {(i, k) for i, n in enumerate(g.nodes) for k, u in enumerate(n.segment.brain.units) if u.kind == "sensor" and u.source == "food"}
    eff = {(i, k) for i, n in enumerate(g.nodes) for k, u in enumerate(n.segment.brain.units) if u.kind == "effector"}
    into = {}  # dst ref -> set of src refs, nonzero weight
    for _, b in g.brains():
        for l in b.links:
            if l.weight != 0.0:
                into.setdefault((l.dst.node, l.dst.index), set()).add((l.src.node, l.src.index))
    routes = set()
    for e in eff:
        for s in into.get(e, ()):
            if s in food and s[0] != e[0]:
                routes.add((s[0], e[0]))
            if s[0] is None:
                for s2 in into.get(s, ()):
                    if s2 in food and s2[0] != e[0]:
                        routes.add((s2[0], e[0]))
    return routes


def neutral_walk(members, cfg, rng, gens=23, k=10, xrate=0.5):
    pop = list(members)
    for _ in range(gens):
        pool = sorted(int(i) for i in rng.choice(len(pop), size=k, replace=False))
        kids = []
        for _ in range(len(pop)):
            a = pop[pool[int(rng.integers(0, k))]]
            b = pop[pool[int(rng.integers(0, k))]] if rng.random() < xrate else None
            c = crossover(a, b, rng) if b is not None else a.copy()
            kids.append(mutate(c, rng, cfg.mutation))
        pop = kids
    return pop


def single_steps(starts, cfg, rng, per=25):
    rows = []
    for g in starts:
        g0, n0, b0, p0 = pheno(g, cfg)
        L0, R0 = link_keys(g), food_routes(g)
        for _ in range(per):
            c = mutate(g, rng, cfg.mutation)
            g1, n1, b1, p1 = pheno(c, cfg)
            L1, R1 = link_keys(c), food_routes(c)
            surv = sum((L0 & L1).values()) / max(1, sum(L0.values()))
            rows.append((g0, g1, n1 - n0, b1 - b0, p1 - p0, surv, sum(L0.values()), len(R1 - R0), len(R0 - R1), len(R0)))
    return np.array(rows, dtype=float)


def report(tag, A):
    g0, g1 = A[:, 0], A[:, 1]
    lr = np.log((g1 + 1) / (g0 + 1))
    print(f"## {tag}: {len(A)} single mutations from {len(A) // 25} starts; median start sum gear {np.median(g0):.1f}")
    print(f"  sum gear x>=1.5: {np.mean(g1 >= 1.5 * g0 + 1e-9) * 100:5.2f}%   x<=1/1.5: {np.mean(g1 * 1.5 <= g0 - 1e-9) * 100:5.2f}%   "
          f"unchanged: {np.mean(np.isclose(g1, g0)) * 100:5.1f}%   mean log ratio {lr.mean():+.4f}  sd {lr.std():.3f}")
    print(f"  driven DOFs +: {np.mean(A[:, 2] > 0) * 100:5.2f}%  -: {np.mean(A[:, 2] < 0) * 100:5.2f}%   ball-joint driven DOFs +: {np.mean(A[:, 3] > 0) * 100:5.2f}%  -: {np.mean(A[:, 3] < 0) * 100:5.2f}%   "
          f"parts +: {np.mean(A[:, 4] > 0) * 100:5.2f}%  -: {np.mean(A[:, 4] < 0) * 100:5.2f}%")
    has = A[:, 6] > 0
    print(f"  link survival per mutation (by src,dst): mean {A[has, 5].mean():.4f}; share of mutations losing >=1 link {np.mean(A[has, 5] < 1) * 100:.1f}%; "
          f"losing >=25% of links {np.mean(A[has, 5] < 0.75) * 100:.1f}%")
    haveR = A[:, 9] > 0
    print(f"  food routes (food sensor on i -> effector on j != i): starts carrying one {np.mean(haveR) * 100:.1f}%;  "
          f"a NEW route per mutation {np.mean(A[:, 7] > 0) * 100:.3f}%;  an existing route LOST per mutation (carriers) "
          f"{np.mean(A[haveR, 8] > 0) * 100 if haveR.any() else float('nan'):.2f}%")


def crossover_bias(founders, rng, n=4000):
    ns, ms, gb = [], [], []
    for _ in range(n):
        a, b = founders[int(rng.integers(0, len(founders)))], founders[int(rng.integers(0, len(founders)))]
        if len(a.nodes) == len(b.nodes):
            continue
        c = crossover(a, b, rng)
        ns.append(len(c.nodes)); ms.append((len(a.nodes) + len(b.nodes)) / 2)
        if (a.global_brain is None) != (b.global_brain is None):
            gb.append(c.global_brain is not None)
    ns, ms = np.array(ns), np.array(ms)
    print(f"## crossover on {len(ns)} unequal founder pairs: child nodes {ns.mean():.3f} against parents' mean {ms.mean():.3f} "
          f"(child > mean {np.mean(ns > ms) * 100:.1f}%, < mean {np.mean(ns < ms) * 100:.1f}%)")
    print(f"   exactly one parent has a global brain ({len(gb)} pairs): child has one {np.mean(gb) * 100:.1f}% (50% = no bias)")


def main():
    rng = np.random.default_rng(12101)
    cfg = W.evolution_config("C", "", seed=1)
    founders = []
    for seed in (1, 2, 3, 4):
        founders += initial_population(HOLISTIC, cfg, spawn_streams(seed, cfg.holistic_stream_salt)[HOLISTIC]).members
    report("holistic founders, seeds 1-4", single_steps(founders, cfg, rng))
    walked = neutral_walk(founders[:40], cfg, rng) + neutral_walk(founders[40:80], cfg, rng)
    gw = np.array([pheno(g, cfg)[0] for g in walked]); gf = np.array([pheno(g, cfg)[0] for g in founders[:80]])
    nw = np.array([len(g.nodes) for g in walked]); nf = np.array([len(g.nodes) for g in founders[:80]])
    print(f"## neutral walk (C scheme, 23 generations, seeds 1-2): nodes {nf.mean():.2f} -> {nw.mean():.2f}; "
          f"sum gear median {np.median(gf):.1f} -> {np.median(gw):.1f}, 90th pct {np.percentile(gf, 90):.1f} -> {np.percentile(gw, 90):.1f}")
    report("after the neutral walk", single_steps(walked, cfg, rng))
    crossover_bias(founders, rng)


if __name__ == "__main__":
    main()
