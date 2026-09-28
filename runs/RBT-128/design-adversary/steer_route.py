"""RBT-128 design adversary, question 3(b): does S = 0 remove the route by which a sensor-to-motor (compass) response
evolves?

    python runs/RBT-128/design-adversary/steer_route.py > runs/RBT-128/design-adversary/steer_route.txt

A compass (RBT-97's routed motif; RBT-125's contrast channel feeds the same food sensors) acts through the link weights
from the food sensors, directly or via a global/segment neuron, into the Effectors.  An Effector bias only sets where
on its tanh the Effector sits: at |bias| >> 1 the motor is pinned and the compass is masked (paper 10's masking,
there through the global bias).  So freezing Effector biases should not remove the route, and may protect it.

Measured: the food-sensor GAIN of a genome = mean over its food sensors i and driven DOFs of
|out(s_i = +0.5) - out(s_i = -0.5)| with every other sensor at 0 (network run 60 ticks, output averaged over ticks
40-59, as effective_drive.py).  Rows as in effective_drive.py.  (1) selection FOR gain (truncation 10 of 40, 23
rounds, 5 replicates, rng [128, rep]); (2) the drift alone (80 lineages, rng 12105).  Cells: mean gain, and the
share of genomes whose gain is > 0.1.  RBT-113 seed-1 founders.  Holistic founders carry few food sensors
(6 in 10 founders), so a holistic genome with none has gain 0.
"""
import os
import sys
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import effective_drive as E  # noqa: E402  (installs the born0 hook, off by default)

from rabbitstew.brain import RuntimeBrain  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genetics import mutate, mutate_controller  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

_cache = {}


def _run(br, s):
    br.reset()
    acc = {k: 0.0 for k in br.effectors}
    for t in range(60):
        br.step(s)
        if t >= 40:
            for k in br.effectors:
                acc[k] += br.effector_output(*k) / 20
    return np.array(list(acc.values()), float)


def gain(g, syn):
    if id(g) in _cache:
        return _cache[id(g)][1]
    br = RuntimeBrain(synthesize(g, syn))
    food = [j for j, s in enumerate(br.sensors) if s.source == "food"]
    if not food or not br.effectors:
        v = 0.0
    else:
        gs = []
        for j in food:
            s = np.zeros(len(br.sensors))
            s[j] = 0.5
            a = _run(br, s)
            s[j] = -0.5
            b = _run(br, s)
            gs.append(np.mean(np.abs(a - b)))
        v = float(np.mean(gs))
    _cache[id(g)] = (g, v)
    return v


def summ(ms, syn):
    v = np.array([gain(g, syn) for g in ms])
    return float(v.mean()), float(np.mean(v > 0.1))


def fmt(tr):
    return " / ".join(f"{a:.3f} ({100 * b:4.0f}%)" for a, b in tr)


def main():
    cfg = E.W.evolution_config("C", "", seed=1)
    syn = cfg.sim.synthesis
    st = spawn_streams(1, cfg.holistic_stream_salt)
    print("# SELECTION for food-sensor gain: mean gain (share of genomes with gain > 0.1) at G 0 / 6 / 12 / 23, mean of 5 replicates")
    for kind, fn in ((CONVENTIONAL, mutate_controller), (HOLISTIC, mutate)):
        founders = initial_population(kind, cfg, st[kind]).members
        for name, S, G, born0 in E.ROWS[kind]:
            E.BORN0["on"] = born0
            mc = replace(cfg.mutation, effector_bias_sigma=S, global_bias_sigma=G if G is not None else cfg.mutation.global_bias_sigma)
            rows = []
            for rep in range(5):
                _cache.clear()
                rng = np.random.default_rng([128, rep])
                pop = list(founders)
                tr = [summ(pop, syn)]
                for gen in range(1, 24):
                    parents = sorted(pop, key=lambda g: gain(g, syn), reverse=True)[:10]
                    pop = [fn(parents[int(rng.integers(0, 10))], rng, mc) for _ in range(40)]
                    if gen in (6, 12, 23):
                        tr.append(summ(pop, syn))
                rows.append(tr)
            print(f"{kind:12s} {name:10s}: {fmt(np.mean(np.array(rows), axis=0))}", flush=True)
    E.BORN0["on"] = False
    print()
    print("# DRIFT alone, 80 lineages, rng 12105: mean gain (share > 0.1) at G 0 / 23 / 60 / 150")
    for kind, fn in ((CONVENTIONAL, mutate_controller), (HOLISTIC, mutate)):
        for name, S, G, born0 in E.ROWS[kind]:
            E.BORN0["on"] = born0
            rng = np.random.default_rng(12105)
            mc = replace(cfg.mutation, effector_bias_sigma=S, global_bias_sigma=G if G is not None else cfg.mutation.global_bias_sigma)
            ms = initial_population(kind, cfg, spawn_streams(1, cfg.holistic_stream_salt)[kind]).members * 2
            done, tr = 0, []
            for gen in (0, 23, 60, 150):
                for _ in range(gen - done):
                    ms = [fn(g, rng, mc) for g in ms]
                done = gen
                _cache.clear()
                tr.append(summ(ms, syn))
            print(f"{kind:12s} {name:10s}: {fmt(tr)}", flush=True)
    E.BORN0["on"] = False


if __name__ == "__main__":
    main()
