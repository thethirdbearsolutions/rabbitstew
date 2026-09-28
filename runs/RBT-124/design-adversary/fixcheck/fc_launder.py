"""RBT-124 FIX-CHECK (design adversary): M1's leaf rule and M2's ball-mounted wheel, probed for laundering.

    fc_launder.py > fc_launder.txt

Run on #420 @ a5c9014.  RBT-113's generation sim (terrain 1131, start 2131); every driven DOF at full throttle
(Effector bias 3).  Each body is scored off and under the ranges (ball_cone = hinge_range = pi/2), and the worst ones
also under RBT-120's motor budget 1.77, with the PR's own lever code (levers.body_levers: work, work on contact-free
children, the report's wheel columns).  The MJCF's DOF and actuator counts (nv, nu) are printed off and on.
Bodies:
  M1 (hinge wheels)   prop-fixed, prop-ball, sphere-prop, hub12-wheels (the first review's launder.py), the Pioneer
  M2 (ball wheels)    bw-air        a sphere on a ball joint, leaf, all three DOFs driven, in the air (S1's residual)
                      bw-blade      the same sphere carrying a FIXED 1.2 m blade: not a leaf, so it must be coned
                      bw-heavy      a large cylinder (scale 1.0 of the root) on a ball joint, leaf, in the air
                      hub12-bw-emb  A's S1 hub with its 12 children made SPHERES (round leaves), orientation (0, pi/2, 0):
                                    twelve ball wheels spinning INSIDE the hub (A's embedded rotor, on round children)
                      hub12-bw-out  the same with orientation 0 (outward)
                      hub12-box-emb A's S1 embedded k=12 as registered (box children: coned), for scale
Nothing is written into any run.
"""
import math
import os
import sys
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-113"))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-124"))
import world  # noqa: E402
import rotor  # noqa: E402

import numpy as np  # noqa: E402

from rabbitstew.evolution import generation_sim  # noqa: E402
from rabbitstew.fixed import pioneer_genotype  # noqa: E402
from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Node, Segment, Shape  # noqa: E402
from rabbitstew.levers import body_levers  # noqa: E402
from rabbitstew.simulation import Simulation, spawn_layout  # noqa: E402

SC = generation_sim(world.evolution_config("U", "", seed=1), 1131)
ON = replace(SC, world=replace(SC.world, ball_cone=math.pi / 2, hinge_range=math.pi / 2))
BUD = replace(ON, world=replace(ON.world, motor_budget=1.77))
BLADE = Segment(Shape.BOX, (6.0, 0.3, 0.3))
FULL = lambda: Brain(units=[Effector(dof=d, bias=3.0) for d in range(3)])


def prop(wheel_shape, blade_joint):
    dims = (1.0, 0.4) if wheel_shape == Shape.CYLINDER else (1.0,)
    w = Segment(wheel_shape, dims, Brain(units=[Effector(dof=0, bias=3.0)]))
    blade = Connection(child=2, position=(0.5, 1.0, 0.0), scale=0.4, joint_type=blade_joint, joint_limit=None)
    axle = Connection(child=1, position=(0.0, 0.0, 1.0), scale=0.5, joint_type=JointType.HINGE, axis=(1.0, 0.0, 0.0), joint_limit=None)
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0)), [axle]), Node(w, [blade]), Node(BLADE)])


def hub_wheels(k=12):
    w = Segment(Shape.CYLINDER, (1.0, 0.4), Brain(units=[Effector(dof=0, bias=3.0)]))
    conns = []
    for i in range(k):
        a, b = 2 * math.pi * i / k, math.pi * (0.25 + 0.5 * ((i * 0.618) % 1.0))
        conns.append(Connection(child=1, position=(math.cos(a) * math.sin(b), math.sin(a) * math.sin(b), math.cos(b)), scale=0.25,
                                joint_type=JointType.HINGE, axis=(1.0, 0.0, 0.0), joint_limit=None))
    blade = Connection(child=2, position=(0.5, 1.0, 0.0), scale=0.6, joint_type=JointType.FIXED, joint_limit=None)
    nodes = [Node(Segment(Shape.SPHERE, (1.0,)), conns), Node(w, [blade]), Node(BLADE)] + [Node(Segment(Shape.BOX, (1.0, 1.0, 1.0))) for _ in range(5)]
    return Genotype(nodes=nodes, name="hub12w")


def ball_wheel(shape=Shape.SPHERE, scale=0.5, blade=False):
    dims = (1.0, 0.4) if shape == Shape.CYLINDER else (1.0,)
    kids = [Connection(child=2, position=(0.5, 1.0, 0.0), scale=0.4, joint_type=JointType.FIXED, joint_limit=None)] if blade else []
    mount = Connection(child=1, position=(0.0, 0.0, 1.0), scale=scale, joint_type=JointType.BALL, joint_limit=None)
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0)), [mount]), Node(Segment(shape, dims, FULL()), kids), Node(BLADE)])


def hub_ball_wheels(orientation, k=12, shape=Shape.SPHERE):
    child = Segment(shape, (1.0,) if shape == Shape.SPHERE else (1.0, 0.4), FULL())
    conns = []
    for i in range(k):
        a, b = 2 * math.pi * i / k, math.pi * (0.25 + 0.5 * ((i * 0.618) % 1.0))
        conns.append(Connection(child=1, position=(math.cos(a) * math.sin(b), math.sin(a) * math.sin(b), math.cos(b)), scale=0.25,
                                orientation=orientation, joint_type=JointType.BALL, joint_limit=None))
    nodes = [Node(Segment(Shape.SPHERE, (1.0,)), conns), Node(child)] + [Node(Segment(Shape.BOX, (1.0, 1.0, 1.0))) for _ in range(5)]
    return Genotype(nodes=nodes, name=f"hubbw{k}")


BODIES = [("prop-fixed", prop(Shape.CYLINDER, JointType.FIXED)), ("prop-ball", prop(Shape.CYLINDER, JointType.BALL)), ("sphere-prop", prop(Shape.SPHERE, JointType.FIXED)),
          ("hub12-wheels", hub_wheels()), ("pioneer", pioneer_genotype(np.random.default_rng(0))),
          ("bw-air", ball_wheel()), ("bw-blade", ball_wheel(blade=True)), ("bw-heavy", ball_wheel(Shape.CYLINDER, scale=1.0)),
          ("hub12-bw-emb", hub_ball_wheels((0.0, math.pi / 2, 0.0))), ("hub12-bw-out", hub_ball_wheels((0.0, 0.0, 0.0))),
          ("hub12-box-emb", rotor.star(12, (0.0, math.pi / 2, 0.0)))]
BUDGETED = {"hub12-wheels", "hub12-bw-emb", "hub12-bw-out", "hub12-box-emb", "bw-heavy", "pioneer"}


def dims(g, sc):
    sim = Simulation([g], replace(sc, random_start=True), spawns=spawn_layout(1, replace(sc, random_start=True), 2131))
    return sim.model.nv, sim.model.nu


def main():
    print("# fc_launder.py (#420 @ a5c9014): full throttle; draw (1131, 2131); ranges pi/2; budget = ranges + motor_budget 1.77")
    print(f"{'body':14s} {'nv off/on':>9s} {'nu off/on':>9s} {'off work':>10s} {'on work':>10s} {'on/off':>7s} {'on free J':>10s} {'on wheel J':>10s} {'budget work':>11s} {'bud/off':>7s} expl off/on")
    for name, g in BODIES:
        a, b = body_levers(g, SC, 2131), body_levers(g, ON, 2131)
        (v0, u0), (v1, u1) = dims(g, SC), dims(g, ON)
        bud = ""
        if name in BUDGETED:
            c = body_levers(g, BUD, 2131)
            bud = f"{c['work']:11.0f} {c['work'] / a['work']:7.3f}"
        else:
            bud = f"{'':11s} {'':7s}"
        print(f"{name:14s} {f'{v0}/{v1}':>9s} {f'{u0}/{u1}':>9s} {a['work']:10.0f} {b['work']:10.0f} {b['work'] / a['work'] if a['work'] else float('nan'):7.3f} "
              f"{b['work_free']:10.0f} {b['work_wheel']:10.0f} {bud} {int(a['exploded'])}/{int(b['exploded'])}")


if __name__ == "__main__":
    main()
