"""The human-designed fixed morphology used by the *conventional* population.

The body is modelled loosely on a differential-drive research robot such as
the ActivMedia Pioneer: a box chassis, two driven wheels at the front (one
Node each so that the global Brain can command them independently) and two
free-rolling wheels at the rear (a single Node instantiated twice).  Wheels
are cylinders hinged about their own length axis without joint limits.

The controller is fully centralised: the chassis carries the Sensors, the
global Brain holds the hidden Neurons and each drive wheel holds one
Effector.  Only link weights and biases change under conventional evolution;
:func:`is_same_morphology` lets the evolutionary loop assert that.
"""

from __future__ import annotations

import math

import numpy as np

from .genotype import Brain, Connection, Effector, Genotype, JointType, Link, Neuron, Node, Segment, Sensor, Shape, UnitRef

CHASSIS, LEFT_DRIVE, RIGHT_DRIVE, CASTER = 0, 1, 2, 3


def pioneer_genotype(rng: np.random.Generator | None = None, hidden: int = 6, weight_sigma: float = 1.0, name: str = "pioneer", rich: bool = False) -> Genotype:
    """Build the fixed body with a random-weight centralised controller.

    With ``rich=True`` the chassis also carries the sensors a real research
    robot has: orientation (``up``), body velocity, distance to target and
    opponent, and each drive wheel reports its own speed, so that under the
    rich brain model the fixed body is not handicapped in sensing.
    """
    rng = np.random.default_rng() if rng is None else rng

    chassis = Segment(Shape.BOX, (0.45, 0.38, 0.2))
    chassis.brain.units = [Sensor("contact")] + [Sensor("target", a) for a in range(3)] + [Sensor("opponent", a) for a in range(3)]
    if rich:
        chassis.brain.units += [Sensor("up", a) for a in range(3)] + [Sensor("velocity", a) for a in range(3)] + [Sensor("target_distance"), Sensor("opponent_distance")]

    def wheel_segment(effector: bool) -> Segment:
        seg = Segment(Shape.CYLINDER, (1.0, 0.4))
        if effector:
            seg.brain.units = [Effector(0, 0.0)] + ([Sensor("joint_velocity")] if rich else [])
        return seg

    def wheel_connection(child: int, x: float, side: float) -> Connection:
        return Connection(
            child=child,
            position=(x, side, -0.6),
            orientation=(0.0, 0.0, 0.0),
            scale=0.324,
            joint_type=JointType.HINGE,
            recursive_limit=1,
            axis=(1.0, 0.0, 0.0),  # about the wheel's own length axis (the outward normal)
            joint_limit=None,
        )

    nodes = [
        Node(chassis, [wheel_connection(LEFT_DRIVE, 0.5, 1.0), wheel_connection(RIGHT_DRIVE, 0.5, -1.0), wheel_connection(CASTER, -0.5, 1.0), wheel_connection(CASTER, -0.5, -1.0)]),
        Node(wheel_segment(True)),
        Node(wheel_segment(True)),
        Node(wheel_segment(False)),
    ]
    g = Genotype(nodes=nodes, root=CHASSIS, global_brain=Brain(units=[Neuron(0.0) for _ in range(hidden)]), name=name)

    # Fully connected: chassis sensors -> hidden neurons (with recurrence) -> drive effectors.
    n_sensors = len(chassis.brain.units)
    for h in range(hidden):
        for s in range(n_sensors):
            g.global_brain.links.append(Link(UnitRef(CHASSIS, s), UnitRef(None, h), 0.0))
        for h2 in range(hidden):
            g.global_brain.links.append(Link(UnitRef(None, h2), UnitRef(None, h), 0.0))
    for wheel in (LEFT_DRIVE, RIGHT_DRIVE):
        for h in range(hidden):
            g.nodes[wheel].segment.brain.links.append(Link(UnitRef(None, h), UnitRef(wheel, 0), 0.0))
        if rich:  # wheel speed feeds the global brain
            for h in range(hidden):
                g.global_brain.links.append(Link(UnitRef(wheel, 1), UnitRef(None, h), 0.0))
    randomize_weights(g, rng, weight_sigma)
    assert g.is_valid(), g.validate()
    return g


def randomize_weights(g: Genotype, rng: np.random.Generator, sigma: float = 1.0) -> Genotype:
    for _, brain in g.brains():
        for link in brain.links:
            link.weight = float(rng.normal(0.0, sigma))
        for u in brain.units:
            if u.kind != "sensor":
                u.bias = float(rng.normal(0.0, 0.5 * sigma))
    return g


def morphology_signature(g: Genotype) -> tuple:
    """Everything about a genotype except its weights and biases."""
    sig = [g.root]
    for node in g.nodes:
        seg = node.segment
        sig.append((int(seg.shape), tuple(round(d, 9) for d in seg.dims)))
        sig.append(tuple((c.child, tuple(c.position), tuple(c.orientation), round(c.scale, 9), int(c.joint_type), c.recursive_limit, tuple(c.axis), c.joint_limit) for c in node.connections))
        sig.append(tuple((u.kind, getattr(u, "source", None), getattr(u, "axis", None), getattr(u, "dof", None)) for u in seg.brain.units))
        sig.append(tuple((l.src, l.dst) for l in seg.brain.links))
    if g.global_brain is not None:
        sig.append(tuple(u.kind for u in g.global_brain.units))
        sig.append(tuple((l.src, l.dst) for l in g.global_brain.links))
    return tuple(sig)


def is_same_morphology(a: Genotype, b: Genotype) -> bool:
    return morphology_signature(a) == morphology_signature(b)


def drive_straight_genotype(power: float = 0.6) -> Genotype:
    """A Pioneer whose wheels simply spin forward: handy for sanity checks."""
    g = pioneer_genotype(np.random.default_rng(0), hidden=1)
    for _, brain in g.brains():
        for link in brain.links:
            link.weight = 0.0
    g.global_brain.units[0].bias = 10.0  # saturates to +1
    # Each wheel hinges about its own outward normal, so the right wheel needs the opposite sign.
    for wheel, sign in ((LEFT_DRIVE, 1.0), (RIGHT_DRIVE, -1.0)):
        brain = g.nodes[wheel].segment.brain
        brain.units[0].bias = 0.0
        brain.links[0].weight = sign * math.atanh(power)
    return g
