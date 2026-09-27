"""RBT-121 audit B, probe 5: the operators' unbounded walks (biases) against their bounded one (link weights).

    python runs/RBT-121/ga/bias_walk.py > runs/RBT-121/ga/bias_walk.txt

`mutate_weights` resets a perturbed LINK weight with probability 0.02, which bounds its variance (paper 8: rms 2.97).
A BIAS has no reset and no clip: it steps N(0, 0.4) with probability 0.25 per generation for ever, variance +0.04
per generation.  An Effector is tanh(bias + input), so a walked Effector bias is a motor held at a constant torque
whatever the sensors say (a resting drive), and a walked hidden-unit bias saturates the unit.  RBT-112's
--global-bias-sigma freezes only the designed body's GLOBAL units; Effector and segment biases keep walking.
This probe walks 80 lineages of the designed founders (seed 1, RBT-113's config, default and Z operators) and of
the holistic founders through G generations of the operator alone, and prints the share of Effectors whose resting
drive |tanh(bias)| exceeds 0.9 (a motor at >= 90% throttle with zero input), and the link-weight rms.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "RBT-113"))
import world as W  # noqa: E402

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genetics import mutate, mutate_controller  # noqa: E402


def stats(ms):
    eb = np.array([u.bias for g in ms for _, b in g.brains() for u in b.units if u.kind == "effector"])
    nb = np.array([u.bias for g in ms for o, b in g.brains() for u in b.units if u.kind == "neuron" and o is None])
    w = np.array([l.weight for g in ms for _, b in g.brains() for l in b.links])
    sat = np.mean(np.abs(np.tanh(eb)) > 0.9) * 100 if len(eb) else float("nan")
    return f"effector bias sd {eb.std() if len(eb) else float('nan'):5.2f}, resting drive >0.9: {sat:5.1f}%  | global-unit bias sd {nb.std() if len(nb) else float('nan'):5.2f}  | link rms {np.sqrt((w ** 2).mean()) if len(w) else float('nan'):6.2f}"


def main():
    rng = np.random.default_rng(12105)
    for op in ("", "Z"):
        cfg = W.evolution_config("C", op, seed=1)
        st = spawn_streams(1, cfg.holistic_stream_salt)
        for kind, fn in ((CONVENTIONAL, mutate_controller), (HOLISTIC, mutate)):
            if op == "Z" and kind == HOLISTIC:
                continue  # the Z operator does not touch the holistic operator
            ms = initial_population(kind, cfg, st[kind]).members * 2
            done = 0
            for G in (0, 23, 60, 150):
                for _ in range(G - done):
                    ms = [fn(g, rng, cfg.mutation) for g in ms]
                done = G
                print(f"{kind:12s} op {op or 'default':7s} G {G:3d}: {stats(ms)}")


if __name__ == "__main__":
    main()
