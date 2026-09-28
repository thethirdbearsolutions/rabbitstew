"""RBT-128: how fast imposed selection can walk Effector biases to resting drive at each effector_bias_sigma.

    python runs/RBT-128/bias_select.py > runs/RBT-128/bias_select.txt

A planted positive for the [OPEN] item: RBT-113's truncation scheme (40 per generation, the top 10 kept as parents,
elites 0) run on the operator alone, with fitness = the mean |tanh(bias)| of a genome's Effectors (selection FOR
resting drive, the direction RBT-113's D line took through work), for 23 rounds of selection, 5 replicate seeds.
Designed body: RBT-113's seed-1 founders under mutate_controller; holistic: its holistic founders under mutate.
Reported: the share of Effectors at resting drive (|tanh(bias)| > 0.9) at G 23, mean over replicates.
"""
import os
import sys
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "RBT-113"))
import world as W  # noqa: E402

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genetics import mutate, mutate_controller  # noqa: E402


def biases(g):
    return np.array([u.bias for _, b in g.brains() for u in b.units if u.kind == "effector"], float)


def fit(g):
    b = biases(g)
    return float(np.mean(np.abs(np.tanh(b)))) if len(b) else 0.0


def share(ms):
    b = np.concatenate([biases(g) for g in ms])
    return float(np.mean(np.abs(np.tanh(b)) > 0.9)) if len(b) else 0.0


def main():
    cfg = W.evolution_config("C", "", seed=1)
    st = spawn_streams(1, cfg.holistic_stream_salt)
    print("# selection FOR resting drive, truncation 10 of 40, 23 rounds, 5 replicates: share at |tanh(bias)| > 0.9 at G 0 / 6 / 12 / 23")
    for kind, fn in ((CONVENTIONAL, mutate_controller), (HOLISTIC, mutate)):
        founders = initial_population(kind, cfg, st[kind]).members
        for S in (None, 0.2, 0.1, 0.05, 0.0):
            mc = replace(cfg.mutation, effector_bias_sigma=S)
            rows = []
            for rep in range(5):
                rng = np.random.default_rng([128, rep])
                pop = list(founders)
                traj = [share(pop)]
                for gen in range(1, 24):
                    parents = sorted(pop, key=fit, reverse=True)[:10]
                    pop = [fn(parents[int(rng.integers(0, 10))], rng, mc) for _ in range(40)]
                    if gen in (6, 12, 23):
                        traj.append(share(pop))
                rows.append(traj)
            m = np.mean(rows, axis=0)
            print(f"{kind:12s} S {'unset' if S is None else S:>5}: " + " / ".join(f"{100 * x:5.1f}%" for x in m), flush=True)


if __name__ == "__main__":
    main()
