"""RBT-124 design adversary: settle_until_rest when an at-rest body shares its world with a drifter.

    settle_bout.py > settle_bout.txt

The claim "a body already at rest is bit-identical" is tested solo.  In a two-robot bout (run_bout; RBT-118's arena
rematch) the settle is one world: a drifting partner keeps both robots settling, and kinetic damping zeroes BOTH at
their joint energy peaks.  Here the Pioneer (rng 0) is paired with each drifter fixture of tests/data/rbt124 and with
itself, under RBT-113's generation sim (terrain 1131, start 2131).  Reported: settle seconds, and the largest change in
the Pioneer's qpos (joint coordinates and root orientation; the root position is re-centred) at the clock's start,
flag on vs off.  Nothing is written into any run.
"""
import glob
import os
import sys
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-113"))
import world  # noqa: E402

from rabbitstew.evolution import generation_sim  # noqa: E402
from rabbitstew.fixed import pioneer_genotype  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import Simulation, spawn_layout  # noqa: E402

SC = replace(generation_sim(world.evolution_config("U", "", seed=1), 1131), random_start=True)
ON = replace(SC, settle_until_rest=0.01, settle_max=10.0)


def start_state(gs, sc):
    sim = Simulation(gs, sc, spawns=spawn_layout(len(gs), sc, 2131))
    idx = sim.robots[0]
    m = sim.model
    adr = [m.jnt_qposadr[j] for j in range(m.njnt) if m.jnt_bodyid[j] in set(idx.bodies)]
    q = np.concatenate([sim.data.qpos[a:a + (7 if m.jnt_type[j] == 0 else 4 if m.jnt_type[j] == 1 else 1)]
                        for a, j in zip(adr, [j for j in range(m.njnt) if m.jnt_bodyid[j] in set(idx.bodies)])])
    return q, sim.settle_seconds


def main():
    p = pioneer_genotype(np.random.default_rng(0))
    print("# settle_bout.py: the Pioneer as robot 0, partner as robot 1; flag eps 0.01, cap 10 s vs the plain settle")
    print(f"{'partner':34s} {'settle s':>8s} {'max |dq| Pioneer (excl. root xyz)':>34s}")
    for name, partner in [("(solo)", None), ("pioneer", p)] + [(os.path.basename(f), Genotype.load(f)) for f in sorted(glob.glob(os.path.join(ROOT, "tests", "data", "rbt124", "*.json")))]:
        gs = [p] if partner is None else [p, partner]
        q0, _ = start_state(gs, SC)
        q1, s = start_state(gs, ON)
        dq = np.abs(q1 - q0)
        dq[:3] = 0.0  # root position: re-centred on the spawn point in both
        print(f"{name:34s} {s:8.2f} {dq.max():34.3e}")


if __name__ == "__main__":
    main()
