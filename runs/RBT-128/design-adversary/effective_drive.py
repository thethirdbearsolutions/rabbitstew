"""RBT-128 design adversary: does S = 0 close resting throttle, or only the Effector's own bias?

    python runs/RBT-128/design-adversary/effective_drive.py > runs/RBT-128/design-adversary/effective_drive.txt

The designer's bias_select.py measures |tanh(Effector bias)| alone.  A motor's resting throttle is the Effector's
OUTPUT with the sensors quiet, clip(sum tanh(bias + W . activation)), and that also carries every constant input: a
global or segment neuron's bias through a link (a neuron with no input outputs tanh(b), a constant) is an Effector
bias by another name, and its weight walks at weight_sigma whatever S is.

Measured here: the NETWORK resting drive of each driven DOF = |output| averaged over ticks 40-59 of the runtime brain
(`rabbitstew.brain.RuntimeBrain`) stepped with every sensor at 0, on the synthesized phenotype.  Share = the fraction
of driven DOFs with network resting drive > 0.9.  Also reported, for comparison with the designer's tables, the
Effector-bias-only share (|tanh(bias)| > 0.9).

Same founders, operators and truncation scheme as runs/RBT-128/bias_select.py (RBT-113 seed-1 founders; 40 per
round, top 10 parents, 23 rounds, 5 replicates, rng [128, rep]), but the fitness selected FOR is the mean network
resting drive: the D line's direction, through whichever gene carries it.  Rows:
  unset          the default operator
  S=0            --effector-bias-sigma 0
  S=0,G=0        + --global-bias-sigma 0 (designed only: RBT-112's operator; it does not bind the holistic fauna)
  S=0,born0      holistic: S = 0 and a newly born Effector's founding bias multiplied by 0 (the same draw, so the
                 stream is unchanged): the adversary's fix for question (a)
Then the drift alone (no selection), 80 lineages, as bias_walk_s0.py (rng 12105), at G 0 / 23 / 60 / 150.
"""
import os
import sys
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "RBT-113"))
import world as W  # noqa: E402

from rabbitstew import genetics  # noqa: E402
from rabbitstew.brain import RuntimeBrain  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genetics import mutate, mutate_controller  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

_orig_random_unit = genetics._random_unit
BORN0 = {"on": False}


def _random_unit_born0(rng, owner, vocab):
    units = _orig_random_unit(rng, owner, vocab)
    if BORN0["on"]:
        for u in units:
            if u.kind == "effector":
                u.bias = 0.0 * u.bias
    return units


genetics._random_unit = _random_unit_born0
_cache = {}


def drives(g, syn):
    key = id(g)
    if key in _cache:
        return _cache[key][1]
    ph = synthesize(g, syn)
    br = RuntimeBrain(ph)
    zero = np.zeros(len(br.sensors))
    acc = {k: 0.0 for k in br.effectors}
    for t in range(60):
        br.step(zero)
        if t >= 40:
            for k in br.effectors:
                acc[k] += abs(br.effector_output(*k)) / 20
    d = np.array(list(acc.values()), float)
    _cache[key] = (g, d)
    return d


def ebias(g):
    return np.array([u.bias for _, b in g.brains() for u in b.units if u.kind == "effector"], float)


def fit(g, syn):
    d = drives(g, syn)
    return float(d.mean()) if len(d) else 0.0


def shares(ms, syn):
    d = np.concatenate([drives(g, syn) for g in ms])
    b = np.concatenate([ebias(g) for g in ms])
    return (float(np.mean(d > 0.9)) if len(d) else 0.0, float(np.mean(np.abs(np.tanh(b)) > 0.9)) if len(b) else 0.0)


ROWS = {CONVENTIONAL: [("unset", None, None, False), ("S=0", 0.0, None, False), ("S=0,G=0", 0.0, 0.0, False)],
        HOLISTIC: [("unset", None, None, False), ("S=0", 0.0, None, False), ("S=0,born0", 0.0, None, True)]}


def fmt(tr):
    return " / ".join(f"{100 * a:5.1f}% ({100 * b:5.1f}%)" for a, b in tr)


def main():
    cfg = W.evolution_config("C", "", seed=1)
    syn = cfg.sim.synthesis
    st = spawn_streams(1, cfg.holistic_stream_salt)
    print("# SELECTION for network resting drive (truncation 10 of 40, 23 rounds, 5 replicates).")
    print("# cells: network resting-drive share (Effector-bias-only share), mean over replicates, at G 0 / 6 / 12 / 23")
    for kind, fn in ((CONVENTIONAL, mutate_controller), (HOLISTIC, mutate)):
        founders = initial_population(kind, cfg, st[kind]).members
        for name, S, G, born0 in ROWS[kind]:
            BORN0["on"] = born0
            mc = replace(cfg.mutation, effector_bias_sigma=S, global_bias_sigma=G if G is not None else cfg.mutation.global_bias_sigma)
            rows = []
            for rep in range(5):
                _cache.clear()
                rng = np.random.default_rng([128, rep])
                pop = list(founders)
                tr = [shares(pop, syn)]
                for gen in range(1, 24):
                    parents = sorted(pop, key=lambda g: fit(g, syn), reverse=True)[:10]
                    pop = [fn(parents[int(rng.integers(0, 10))], rng, mc) for _ in range(40)]
                    if gen in (6, 12, 23):
                        tr.append(shares(pop, syn))
                rows.append(tr)
            m = np.mean(np.array(rows), axis=0)
            print(f"{kind:12s} {name:10s}: {fmt(m)}", flush=True)
    BORN0["on"] = False
    print()
    print("# DRIFT alone (no selection), 80 lineages, rng 12105, at G 0 / 23 / 60 / 150: network share (bias-only share)")
    for kind, fn in ((CONVENTIONAL, mutate_controller), (HOLISTIC, mutate)):
        for name, S, G, born0 in ROWS[kind]:
            BORN0["on"] = born0
            rng = np.random.default_rng(12105)
            mc = replace(cfg.mutation, effector_bias_sigma=S, global_bias_sigma=G if G is not None else cfg.mutation.global_bias_sigma)
            ms = initial_population(kind, cfg, spawn_streams(1, cfg.holistic_stream_salt)[kind]).members * 2
            done, tr = 0, []
            for gen in (0, 23, 60, 150):
                for _ in range(gen - done):
                    ms = [fn(g, rng, mc) for g in ms]
                done = gen
                _cache.clear()
                tr.append(shares(ms, syn))
            print(f"{kind:12s} {name:10s}: {fmt(tr)}", flush=True)
    BORN0["on"] = False


if __name__ == "__main__":
    main()
