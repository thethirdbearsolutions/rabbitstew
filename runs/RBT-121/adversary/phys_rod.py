"""RBT-121 adversary (physics): is audit A's A5 rod sweeper reachable by selection?  Payoff of the intermediates.

    phys_rod.py > phys_rod.txt

A 0.3 m cube root with one box arm of relative dims (a, 1, 1) on an unlimited vertical hinge, full throttle via one
biased effector, no sensor (audit A's S2 when a = 100, i.e. dims (5, .05, .05)).  The arm's length at size 0.3 is
0.3 x a^(2/3).  For a path of lengths from founder-like to 6.5 m, 10 start draws each (2131..2140), terrain 1131,
RBT-113's U-arm SimConfig: food, work cost, net, exploded; plus the analytic count of dims-mutation events needed.
Nothing is written into any run.
"""
import math
import os
import sys
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "RBT-113"))
import world  # noqa: E402

import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import generation_sim  # noqa: E402
from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Node, Segment, Shape  # noqa: E402

SC = generation_sim(world.evolution_config("U", "", seed=1), 1131)


def rod(a, scale=1.0):
    arm = Segment(Shape.BOX, (float(a), 1.0, 1.0), Brain(units=[Effector(dof=0, bias=3.0)]))
    conn = Connection(child=1, position=(1.0, 0.0, 0.0), scale=scale, joint_type=JointType.HINGE, axis=(0.0, 0.0, 1.0), joint_limit=None)
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0)), [conn]), Node(arm)], name="rod")


def main():
    print("# phys_rod.py: rod sweeper intermediates, 10 draws each; yields per season (food value 1, work cost 0.03/kJ)")
    print(f"# food_cfg: {SC.food}")
    print("  aspect  length(m)  food   work(yield)  net    exploded  on/off")
    for L in (0.45, 0.9, 1.5, 2.5, 3.5, 5.0, 6.46):
        a = (L / 0.3) ** 1.5
        for off in (False, True):
            R = []
            for s in range(2131, 2141):
                cfg = replace(SC, random_start=True)
                sim = S.Simulation([rod(a)], cfg, spawns=S.spawn_layout(1, cfg, s))
                sim.set_food_seed(s)
                if off:
                    sim.brains[0].effector_output = lambda *x: 0.0
                sim.run()
                R.append((sim.food_eaten[0], sim.work[0] * SC.food.work_cost / 1000, sim.food_score(0), sim.exploded[0]))
            R = np.array(R, float)
            ln = sim.phenotypes[0].parts[1].dims[0]
            print(f"  {a:7.1f}  {ln:8.2f}  {R[:, 0].mean():5.2f}  {R[:, 1].mean():8.3f}  {R[:, 2].mean():+6.2f}  {int(R[:, 3].sum()):3d}      {'off' if off else 'on'}")
    # analytic: d ln(length) per dims event = (2/3) e0 - (1/3) e1 - (1/3) e2, e ~ N(0, 0.2)
    sd = 0.2 * math.sqrt(4 / 9 + 1 / 9 + 1 / 9)
    need = math.log(6.46 / 0.3)  # from a unit cube arm at size 0.3 (founder dims are U(0.3, 1): aspect near 1)
    print(f"# sd of d ln(length) per dims event {sd:.3f}; needed {need:.2f} in ln; events if every event were +1 sd: {need / sd:.0f};"
          f" if only improving events kept (mean half-normal {sd * math.sqrt(2 / math.pi):.3f}): {need / (sd * math.sqrt(2 / math.pi)):.0f} kept events"
          f" = about {2 * need / (sd * math.sqrt(2 / math.pi)):.0f} dims events on that node (half are worse), at dims_rate 0.2 per node per offspring")


if __name__ == "__main__":
    main()
