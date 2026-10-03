"""RBT-121 audit B, probe 2b: which operator class moves sum gear (probe 2's measure), one class at a time.

    python runs/RBT-121/ga/gear_levers.py > runs/RBT-121/ga/gear_levers.txt

RBT-113's MutationConfig with every structural and body rate set to 0 except one class, applied once to each of the
160 holistic founders (seeds 1-4) 25 times.  Printed per class: the share of calls raising sum gear >= 1.5x or cutting
it to <= 1/1.5, at the class's shipped rate; and the same share per call of the whole shipped operator for reference.
"""
import dataclasses
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "RBT-113"))
import world as W  # noqa: E402
from reach import pheno  # noqa: E402

from rabbitstew.evolution import HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genetics import mutate  # noqa: E402

ZERO = ("dims_rate", "shape_rate", "position_rate", "orientation_rate", "scale_rate", "axis_rate", "joint_type_rate",
        "joint_limit_rate", "recursive_limit_rate", "add_node_rate", "remove_node_rate", "add_connection_rate",
        "remove_connection_rate", "add_unit_rate", "remove_unit_rate", "add_link_rate", "remove_link_rate", "motor_rate",
        "mirror_toggle_rate", "func_rate")
CLASSES = {
    "all (shipped)": None,
    "segment dims/shape": ("dims_rate", "shape_rate"),
    "connection scale": ("scale_rate",),
    "joint type": ("joint_type_rate",),
    "recursive limit": ("recursive_limit_rate",),
    "add/remove node": ("add_node_rate", "remove_node_rate"),
    "add/remove connection": ("add_connection_rate", "remove_connection_rate"),
    "add/remove unit": ("add_unit_rate", "remove_unit_rate"),
    "motor mode": ("motor_rate",),
}


def main():
    rng = np.random.default_rng(12107)
    cfg = W.evolution_config("C", "", seed=1)
    founders = []
    for seed in (1, 2, 3, 4):
        founders += initial_population(HOLISTIC, cfg, spawn_streams(seed, cfg.holistic_stream_salt)[HOLISTIC]).members
    base = [pheno(g, cfg)[0] for g in founders]
    for name, keep in CLASSES.items():
        mc = cfg.mutation if keep is None else dataclasses.replace(cfg.mutation, **{k: 0.0 for k in ZERO if k not in keep})
        up = down = n = 0
        for g, g0 in zip(founders, base):
            for _ in range(25):
                g1 = pheno(mutate(g, rng, mc), cfg)[0]
                up += g1 >= 1.5 * g0 + 1e-9; down += g1 * 1.5 <= g0 - 1e-9; n += 1
        print(f"{name:22s} x>=1.5: {up / n * 100:5.2f}%   x<=1/1.5: {down / n * 100:5.2f}%")


if __name__ == "__main__":
    main()
