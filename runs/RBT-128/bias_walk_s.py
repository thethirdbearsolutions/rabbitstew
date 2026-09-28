"""RBT-128: the resting-drive walk under small effector_bias_sigma values (0.05, 0.1, 0.2), for the --fair preset's [OPEN] item.

    python runs/RBT-128/bias_walk_s.py > runs/RBT-128/bias_walk_s.txt

80 lineages of RBT-113's seed-1 founders (default operator; the designed body under mutate_controller, the holistic
under mutate) walked G generations by the operator alone (no selection), with the same rng as RBT-121's bias_walk.py,
at effector_bias_sigma S in (0.05, 0.1, 0.2).  RBT-124's bias_walk_s0.txt has S unset and S = 0 on the same stream.
Reported: the share of Effectors at resting drive (|tanh(bias)| > 0.9).
"""
import os
import sys
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "RBT-113"))
sys.path.insert(0, os.path.join(HERE, "..", "RBT-121", "ga"))
import world as W  # noqa: E402
from bias_walk import stats  # noqa: E402

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genetics import mutate, mutate_controller  # noqa: E402


def main():
    for S in (0.05, 0.1, 0.2):
        rng = np.random.default_rng(12105)
        cfg = W.evolution_config("C", "", seed=1)
        mc = replace(cfg.mutation, effector_bias_sigma=S)
        st = spawn_streams(1, cfg.holistic_stream_salt)
        for kind, fn in ((CONVENTIONAL, mutate_controller), (HOLISTIC, mutate)):
            ms = initial_population(kind, cfg, st[kind]).members * 2
            done = 0
            for G in (0, 23, 60, 150):
                for _ in range(G - done):
                    ms = [fn(g, rng, mc) for g in ms]
                done = G
                print(f"S {'unset' if S is None else S:5} {kind:12s} G {G:3d}: {stats(ms)}", flush=True)


if __name__ == "__main__":
    main()
