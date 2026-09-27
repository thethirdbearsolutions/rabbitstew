"""RBT-120 design adversary: which holistic founders does --motor-budget 1.77 move, and by which of its two parts?

For RBT-113's O founders (seed S, population 40; the same across U/D/C), compile and simulate one 15 s solo season
three ways -- off; the Sum-gear cap alone (servo clamp patched out); the registered budget (cap + servo clamp) -- and
classify each founder: over budget (scaled), servo-bearing, and whether its season's work / final qpos move.
    python runs/RBT-120/design-adversary/probe_clamp.py SEED [SEED ...]
"""
import os, sys
from dataclasses import replace
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import world as W120  # RBT-120's
import rabbitstew.world as rw
from rabbitstew.evolution import initial_population, spawn_streams, generation_sim
from rabbitstew.simulation import Simulation
from rabbitstew.synthesis import synthesize

_orig_limit = rw._servo_limit


def season(g, sim):
    s = Simulation([g], sim)
    s.run()
    return s.data.qpos.copy(), float(s.work[0])


def main(seeds):
    tot = dict(n=0, over=0, servo=0, servo_in=0, moved_full=0, moved_cap=0, moved_in_full=0, moved_in_cap=0)
    for seed in seeds:
        cfg = W120.evolution_config("D", seed=seed)
        rng = spawn_streams(cfg.seed, cfg.holistic_stream_salt)["holistic"]
        pop = initial_population("holistic", cfg, rng)
        base = generation_sim(cfg, None, 0)
        base = replace(base, world=replace(base.world, terrain="flat"))
        off = replace(base, world=replace(base.world, motor_budget=0.0))
        on = replace(base, world=replace(base.world, motor_budget=W120.MOTOR_BUDGET))
        for g in pop.members:
            ph = synthesize(g, base.synthesis)
            over = rw.motor_scale(ph, on.world) < 1.0
            modes = {ph.parts[i].motor for i, _ in rw.driven_dofs(ph) if ph.parts[i].joint_type != rw.JointType.BALL}
            servo = bool(modes & {"position", "velocity"})
            q0, w0 = season(g, off)
            q2, w2 = season(g, on)
            rw._servo_limit = lambda gear, config: {}
            try:
                q1, w1 = season(g, on)
            finally:
                rw._servo_limit = _orig_limit
            mf = not (np.array_equal(q0, q2) and w0 == w2)
            mc = not (np.array_equal(q0, q1) and w0 == w1)
            tot["n"] += 1; tot["over"] += over; tot["servo"] += servo; tot["servo_in"] += servo and not over
            tot["moved_full"] += mf; tot["moved_cap"] += mc
            tot["moved_in_full"] += mf and not over; tot["moved_in_cap"] += mc and not over
        print(seed, dict(tot), flush=True)
    print("# founders:", tot["n"], "| over budget (scaled):", tot["over"], "| with a servo:", tot["servo"],
          "| within budget but servo:", tot["servo_in"])
    print("# season moved by the registered budget (cap + clamp):", tot["moved_full"], "of which within budget (clamp alone):", tot["moved_in_full"])
    print("# season moved by the cap alone (clamp patched out):", tot["moved_cap"], "of which within budget:", tot["moved_in_cap"])


if __name__ == "__main__":
    main([int(s) for s in sys.argv[1:]])
