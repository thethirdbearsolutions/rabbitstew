"""RBT-124 design adversary: can a free rotor be laundered through a "wheel" (world.is_wheel)?

    launder.py > launder.txt

RBT-113's generation sim (terrain 1131, start 2131), as runs/RBT-124/rotor.py.  Every body is driven at full throttle
(Effector bias 3).  Each is scored with the ranges off and on (ball_cone = hinge_range = pi/2), with RBT-124's own
lever code (levers.body_levers: work, work on contact-free children).  Bodies:
  wheel            rotor.py's wheel: a cylinder on an unlimited hinge about its own axis (the reference)
  prop-fixed       the same wheel, axle pointing up, carrying a 1.2 m box blade on a FIXED link: a propeller
  prop-ball        the same, blade on an undriven BALL joint (the blade can only swing within the cone, but the wheel turns it)
  sphere-prop      a sphere on an x hinge (a wheel by the rule) carrying a FIXED blade
  hub12-wheels     a sphere hub with 12 x-hinged cylinder wheels, each carrying a FIXED blade (S1's hub, laundered)
  hub12-ball       S1 embedded k=12 on ball joints (rotor.py's worst), for scale
With --leaf, is_wheel is patched (in this process only) to also require that the part is a LEAF (no child part):
the adversary's proposed rule.  The Pioneer's wheels are leaves, so it must be unchanged; the laundered props not.
Nothing is written into any run.
"""
import math
import os
import sys
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-113"))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-124"))
import world  # noqa: E402
import rotor  # noqa: E402

from rabbitstew.evolution import generation_sim  # noqa: E402
from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Node, Segment, Shape  # noqa: E402
from rabbitstew.levers import body_levers  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402
from rabbitstew.world import is_wheel  # noqa: E402

SC = generation_sim(world.evolution_config("U", "", seed=1), 1131)
ON = replace(SC, world=replace(SC.world, ball_cone=math.pi / 2, hinge_range=math.pi / 2))
BLADE = Segment(Shape.BOX, (6.0, 0.3, 0.3))  # relative dims; scaled by the connection


def prop(wheel_shape, blade_joint, up=True):
    dims = (1.0, 0.4) if wheel_shape == Shape.CYLINDER else (1.0,)
    w = Segment(wheel_shape, dims, Brain(units=[Effector(dof=0, bias=3.0)]))
    blade = Connection(child=2, position=(0.5, 1.0, 0.0), scale=0.4, joint_type=blade_joint, joint_limit=None)
    axle = Connection(child=1, position=(0.0, 0.0, 1.0) if up else (0.0, 1.0, 0.0), scale=0.5, joint_type=JointType.HINGE, axis=(1.0, 0.0, 0.0), joint_limit=None)
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0)), [axle]), Node(w, [blade]), Node(BLADE)])


def hub_wheels(k=12):
    w = Segment(Shape.CYLINDER, (1.0, 0.4), Brain(units=[Effector(dof=0, bias=3.0)]))
    conns = []
    for i in range(k):
        a, b = 2 * math.pi * i / k, math.pi * (0.25 + 0.5 * ((i * 0.618) % 1.0))
        conns.append(Connection(child=1, position=(math.cos(a) * math.sin(b), math.sin(a) * math.sin(b), math.cos(b)), scale=0.25,
                                joint_type=JointType.HINGE, axis=(1.0, 0.0, 0.0), joint_limit=None))
    blade = Connection(child=2, position=(0.5, 1.0, 0.0), scale=0.6, joint_type=JointType.FIXED, joint_limit=None)
    nodes = [Node(Segment(Shape.SPHERE, (1.0,)), conns), Node(w, [blade]), Node(BLADE)]
    nodes += [Node(Segment(Shape.BOX, (1.0, 1.0, 1.0))) for _ in range(5)]  # recessive, to lift the part cap as S1 does
    return Genotype(nodes=nodes, name="hub12w")


BODIES = [("wheel", rotor.wheel_rotor()), ("prop-fixed", prop(Shape.CYLINDER, JointType.FIXED)), ("prop-ball", prop(Shape.CYLINDER, JointType.BALL)),
          ("sphere-prop", prop(Shape.SPHERE, JointType.FIXED)), ("hub12-wheels", hub_wheels()), ("hub12-ball", rotor.star(12, (0.0, math.pi / 2, 0.0)))]
try:
    from rabbitstew.fixed import pioneer_genotype
    import numpy as _np
    BODIES.append(("pioneer", pioneer_genotype(_np.random.default_rng(0))))
except ImportError:
    pass


def patch_leaf():
    import rabbitstew.simulation as S
    import rabbitstew.synthesis as Y
    import rabbitstew.world as W
    orig_syn, orig_wheel = Y.synthesize, W.is_wheel

    def syn(g, cfg=None):
        ph = orig_syn(g, cfg)
        parents = {p.parent for p in ph.parts if p.parent is not None}
        for p in ph.parts:
            p._leaf = p.index not in parents
        return ph

    S.synthesize = syn
    W.is_wheel = lambda part: orig_wheel(part) and getattr(part, "_leaf", True)


def main():
    if "--leaf" in sys.argv:
        patch_leaf()
        print("# is_wheel patched: a wheel must also be a leaf")
    print("# launder.py: season work (J) and work on contact-free children, ranges off vs on (pi/2); draw (1131, 2131)")
    print(f"{'body':14s} {'parts':>5s} {'wheels':>6s} {'off work':>10s} {'on work':>10s} {'on/off':>7s} {'on work_free':>12s} {'on w_free':>9s} {'exploded':>8s}")
    for name, g in BODIES:
        import rabbitstew.simulation as S
        import rabbitstew.world as W
        ph = S.synthesize(g, SC.synthesis)
        nw = sum(W.is_wheel(p) for p in ph.parts)
        a, b = body_levers(g, SC, 2131), body_levers(g, ON, 2131)
        print(f"{name:14s} {len(ph.parts):5d} {nw:6d} {a['work']:10.0f} {b['work']:10.0f} {b['work'] / a['work'] if a['work'] else float('nan'):7.3f} "
              f"{b['work_free']:12.0f} {b['w_free']:9.2f} {int(a['exploded'])}/{int(b['exploded'])}")


if __name__ == "__main__":
    main()
