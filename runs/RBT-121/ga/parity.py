"""RBT-121 audit B, probe 6: per-child disruption of the two faunas' operators, on RBT-113's founders (seeds 1-4).

    python runs/RBT-121/ga/parity.py > runs/RBT-121/ga/parity.txt

For each founder, 25 children by the fauna's own operator (`mutate` for holistic, `mutate_controller` for the
designed body, RBT-113's config).  Printed: the share of the parent's links (by src, dst) that survive, the share of
children losing any link, and the share of food routes (food sensor on segment i -> effector on segment j != i,
direct or through one global unit; probe 2's definition) lost per child among carriers.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "RBT-113"))
import world as W  # noqa: E402
from reach import food_routes, link_keys  # noqa: E402

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genetics import mutate, mutate_controller  # noqa: E402


def main():
    rng = np.random.default_rng(12106)
    cfg = W.evolution_config("C", "", seed=1)
    for kind, fn in ((HOLISTIC, mutate), (CONVENTIONAL, mutate_controller)):
        surv, anyloss, rl, carriers = [], [], [], 0
        for seed in (1, 2, 3, 4):
            for g in initial_population(kind, cfg, spawn_streams(seed, cfg.holistic_stream_salt)[kind]).members:
                L0, R0 = link_keys(g), food_routes(g)
                for _ in range(25):
                    c = fn(g, rng, cfg.mutation)
                    L1 = link_keys(c)
                    s = sum((L0 & L1).values()) / max(1, sum(L0.values()))
                    surv.append(s); anyloss.append(s < 1)
                    if R0:
                        carriers += 1
                        rl.append(len(R0 - food_routes(c)) / len(R0))
        print(f"{kind:12s} link survival per child {np.mean(surv):.4f}, children losing any link {np.mean(anyloss) * 100:5.1f}%, "
              f"food-route carriers {carriers} children, mean share of routes lost per child {np.mean(rl) * 100 if rl else float('nan'):.2f}%")


if __name__ == "__main__":
    main()
