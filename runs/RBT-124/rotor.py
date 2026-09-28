"""RBT-124: the embedded-rotor bodies of RBT-121 audit A (A2's test), with the joint ranges off and on.

    rotor.py > rotor.txt

Under RBT-113's SimConfig (mass budget 15.34, food world, work cost 0.03 / kJ, 15 s seasons) on its first generation
sim (terrain 1131, start 2131), as probe_synthetic.py.  Bodies:
  S1 embedded   audit A's S1 star hub, k children on driven ball joints at full throttle (bias 3 on every DOF), with
                orientation (0, pi/2, 0): each child points INTO the root, the embedded rotor A2 names;
  S1 outward    the same, orientation (0, 0, 0);
  rod           S2's 6.5 m arm on an unlimited hinge about the vertical, full throttle (a hinge rotor);
  wheel rotor   a cylinder hinged about its own length axis, full throttle (a wheel: hinge_range must leave it free).
Reported: season work (J) off and on, and on/off.  Nothing is written into any run.
"""
import math
import os
import sys
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "runs", "RBT-113"))
import world  # noqa: E402

import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import generation_sim  # noqa: E402
from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Node, Segment, Shape  # noqa: E402

SC = generation_sim(world.evolution_config("U", "", seed=1), 1131)
CONE = math.pi / 2
HINGE = math.pi / 2


def star(k, orientation):
    child = Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=[Effector(dof=d, bias=3.0) for d in range(3)]))
    conns = []
    for i in range(k):
        a, b = 2 * math.pi * i / max(k, 1), math.pi * (0.25 + 0.5 * ((i * 0.618) % 1.0))
        conns.append(Connection(child=1, position=(math.cos(a) * math.sin(b), math.sin(a) * math.sin(b), math.cos(b)), scale=0.25,
                                orientation=orientation, joint_type=JointType.BALL, joint_limit=None))
    nodes = [Node(Segment(Shape.SPHERE, (1.0,)), conns), Node(child)]
    need = math.ceil((k + 1) / 2.0)
    nodes += [Node(Segment(Shape.BOX, (1.0, 1.0, 1.0))) for _ in range(max(0, need - 2))]  # recessive: unreachable
    return Genotype(nodes=nodes, name=f"star{k}")


def rod():
    arm = Segment(Shape.BOX, (5.0, 0.05, 0.05), Brain(units=[Effector(dof=0, bias=3.0)]))
    conn = Connection(child=1, position=(1.0, 0.0, 0.0), scale=1.0, joint_type=JointType.HINGE, axis=(0.0, 0.0, 1.0), joint_limit=None)
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0)), [conn]), Node(arm)], name="rod")


def wheel_rotor():
    w = Segment(Shape.CYLINDER, (1.0, 0.4), Brain(units=[Effector(dof=0, bias=3.0)]))
    conn = Connection(child=1, position=(0.0, 1.0, 0.0), scale=0.5, joint_type=JointType.HINGE, axis=(1.0, 0.0, 0.0), joint_limit=None)
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0)), [conn]), Node(w)], name="wheel")


def work(g, on, seed=2131):
    cfg = replace(SC, random_start=True)
    if on:
        cfg = replace(cfg, world=replace(cfg.world, ball_cone=CONE, hinge_range=HINGE))
    sim = S.Simulation([g], cfg, spawns=S.spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    sim.run()
    return float(sim.work[0]), bool(sim.exploded[0])


BODIES = [(f"S1 embedded k={k}", star(k, (0.0, math.pi / 2, 0.0))) for k in (1, 3, 12)] + \
         [(f"S1 outward  k={k}", star(k, (0.0, 0.0, 0.0))) for k in (1, 12)] + [("rod (hinge)", rod()), ("wheel rotor", wheel_rotor())]


def main():
    print(f"# rotor.py: season work (J), ranges off vs on (ball_cone {CONE:.4f}, hinge_range {HINGE:.4f}); draw (1131, 2131)")
    print(f"{'body':22s} {'off (J)':>10s} {'on (J)':>10s} {'on/off':>7s}  exploded off/on")
    for name, g in BODIES:
        w0, x0 = work(g, False)
        w1, x1 = work(g, True)
        print(f"{name:22s} {w0:10.1f} {w1:10.1f} {w1 / w0 if w0 else float('nan'):7.3f}  {x0}/{x1}")


if __name__ == "__main__":
    main()
