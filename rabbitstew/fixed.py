"""The human-designed fixed morphology used by the *conventional* population.

The body is modelled loosely on a differential-drive research robot such as
the ActivMedia Pioneer: a box chassis, two driven wheels at the front (one
Node each so that the global Brain can command them independently) and two
free-rolling wheels at the rear (a single Node instantiated twice).  Wheels
are cylinders hinged about their own length axis without joint limits.

**Sign convention -- read this before writing a controller or an analysis for
this body.**  Each wheel is mounted on the chassis side it sits on and hinges
about its own length axis, which points *outward*, so the two drive axes are
**antiparallel** (world-frame dot product -1.0 at rest; asserted by
``tests/test_pioneer_drive.py``).  That is the transpose of a textbook
differential drive, and it inverts the intuition most controller authors bring:

* the **sum** of the two drive commands is the **steering** axis -- a positive
  sum yaws clockwise seen from above, that is, to the robot's right;
* their **difference** (left minus right) is the **throttle** -- positive is
  forward.

So a circuit that puts the same sign on both wheels pirouettes on the spot
instead of driving, and a Braitenberg compass on this body is the
*antisymmetric* motif: one nose wired with the same sign into both Effectors
and the other nose with the opposite sign.  :func:`steering_throttle` and
:func:`drive_commands` convert between the two descriptions so that nothing
downstream has to rederive this.

**Which of the two antisymmetric orientations is the compass is not a property
of this body.**  It depends on which way the population drives: nothing in a
foraging ecology rewards driving nose-first over tail-first, so lineages fix a
direction arbitrarily and the same weights are a compass for one population and
an anti-compass for another (RBT-69).  Run ``scripts/travel_direction.py`` on a
run directory -- about two minutes -- before installing any sensorimotor circuit
on an evolved population, and measure chemotaxis in the *travel* frame rather
than against chassis yaw.

The controller is fully centralised: the chassis carries the Sensors, the
global Brain holds the hidden Neurons and each drive wheel holds one
Effector.  Only link weights and biases change under conventional evolution;
:func:`is_same_morphology` lets the evolutionary loop assert that.
"""

from __future__ import annotations

import math

import numpy as np

from .genotype import Brain, Connection, Effector, Genotype, JointType, Link, Neuron, Node, Segment, Sensor, Shape, UnitRef
from .synthesis import Phenotype

CHASSIS, LEFT_DRIVE, RIGHT_DRIVE, CASTER = 0, 1, 2, 3


def _mount(sources: tuple | None, rich_default: list, all_scalar: bool = False) -> list:
    """Sensors for a designed body under an explicit vocabulary: every vector source on three axes
    and every scalar source once (joint sensors and oscillators are mounted by the caller)."""
    if sources is None:
        return rich_default
    from .genotype import VECTOR_SOURCES

    units = []
    for src in sources:
        if src in ("joint_angle", "joint_velocity", "oscillator"):
            continue
        if src in VECTOR_SOURCES:
            units += [Sensor(src, a) for a in range(3)]
        else:
            units.append(Sensor(src))
    return units


def pioneer_genotype(rng: np.random.Generator | None = None, hidden: int = 6, weight_sigma: float = 1.0, name: str = "pioneer", rich: bool = False, sources: tuple | None = None) -> Genotype:
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
    if sources is not None:
        chassis.brain.units = _mount(sources, chassis.brain.units)
    smell = [Sensor(src) for src in ("food", "agent") if sources is not None and src in sources]  # a nose on each wheel: left and right intensities

    def wheel_segment(effector: bool) -> Segment:
        seg = Segment(Shape.CYLINDER, (1.0, 0.4))
        if effector:
            seg.brain.units = [Effector(0, 0.0)] + ([Sensor("joint_velocity")] if rich else []) + [Sensor(u.source) for u in smell]
        return seg

    def wheel_connection(child: int, x: float, side: float) -> Connection:
        return Connection(
            child=child,
            position=(x, side, -0.6),
            orientation=(0.0, 0.0, 0.0),
            scale=0.324,
            joint_type=JointType.HINGE,
            recursive_limit=1,
            # About the wheel's own length axis, which points outward, so the left and right
            # drive axes are antiparallel: the effector SUM steers, their DIFFERENCE throttles.
            # See the module docstring and :func:`steering_throttle` before wiring anything here.
            axis=(1.0, 0.0, 0.0),
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
    # Driving is the *difference* of the two commands (the drive axes are antiparallel), so the
    # right wheel takes the opposite sign: (+p, -p) is steering 0, throttle p.
    for wheel, sign in ((LEFT_DRIVE, 1.0), (RIGHT_DRIVE, -1.0)):
        brain = g.nodes[wheel].segment.brain
        brain.units[0].bias = 0.0
        brain.links[0].weight = sign * math.atanh(power)
    return g


# --------------------------------------------------------------------------- #
# The drive convention: steering is the sum, throttle is the difference
# --------------------------------------------------------------------------- #


def steering_throttle(left: float, right: float) -> tuple[float, float]:
    """Resolve a Pioneer's two drive-Effector commands into ``(steering, throttle)``.

    The two drive hinges are antiparallel (see the module docstring), so it is
    the *sum* of the commands that turns the robot and their *difference* that
    drives it:

    * ``steering = (left + right) / 2`` -- positive yaws clockwise seen from
      above, that is, to the robot's right.
    * ``throttle = (left - right) / 2`` -- positive is forward.

    Halving puts both components on the same scale as a single wheel command,
    so :func:`drive_straight_genotype`'s ``(+p, -p)`` reads as steering 0,
    throttle ``p``.  :func:`drive_commands` is the inverse.
    """
    return 0.5 * (left + right), 0.5 * (left - right)


def drive_commands(steering: float, throttle: float) -> tuple[float, float]:
    """The ``(left, right)`` drive commands realising a steering and a throttle: the inverse of :func:`steering_throttle`.

    Use this when *installing* a circuit by hand.  A pure compass on this body
    is ``drive_commands(steering=k * (n1 - n2), throttle=0)``, which is the
    same sign from one nose into both Effectors and the opposite sign from the
    other -- not the crossed, same-signed wiring a textbook differential drive
    would want.
    """
    return steering + throttle, steering - throttle


def drive_effector_units(ph: Phenotype) -> tuple[list[int], list[int]]:
    """``(left, right)`` unit indices of the drive Effectors of a synthesised Pioneer.

    Side is read from the sign of each wheel Part's attachment ``y`` in the
    chassis frame (+y is the robot's left), not from Node order, so this still
    holds if the Connections are reordered.  Pioneer-shaped bodies only: it
    assumes every live Effector belongs to a wheel mounted off the centreline.
    """
    left: list[int] = []
    right: list[int] = []
    for i, ui in enumerate(ph.units):
        if ui.unit.kind != "effector" or ui.part is None:
            continue
        part = ph.parts[ui.part]
        if part.parent is None or part.joint_type == JointType.FIXED:
            continue
        (left if part.attach_pos[1] > 0 else right).append(i)
    return left, right


# --------------------------------------------------------------------------- #
# A designed legged body: the controller-only capacity test
# --------------------------------------------------------------------------- #

QUAD_BODY = 0
QUAD_HIPS = (1, 2, 3, 4)  #: front-left, front-right, back-left, back-right
QUAD_SHINS = (5, 6, 7, 8)


def quadruped_genotype(rng: np.random.Generator | None = None, hidden: int = 8, weight_sigma: float = 1.0, name: str = "quadruped", rich: bool = True, sources: tuple | None = None) -> Genotype:
    """A hand-designed quadruped whose gait must be found by controller evolution alone.

    A box body with four two-segment legs, each leg its own pair of Nodes so
    that the global Brain can command every joint separately: a hip on a
    fore-aft hinge under each corner of the body and a shin on a fore-aft
    hinge under each hip, all position servos.  Every leg segment carries a
    joint-angle sensor, a contact sensor and an Effector with a local reflex
    link from its own angle; the body carries contact, target, opponent,
    orientation, velocity and distance sensors and two oscillators a quarter
    period apart; the global Brain holds the hidden Neurons.  Used to test
    whether the neural search can find a walking gait on a body built for one.
    """
    rng = np.random.default_rng() if rng is None else rng
    body = Segment(Shape.BOX, (0.5, 0.3, 0.12))
    body.brain.units = [Sensor("contact")] + [Sensor("target", a) for a in range(3)] + [Sensor("opponent", a) for a in range(3)]
    if rich:
        body.brain.units += [Sensor("up", a) for a in range(3)] + [Sensor("velocity", a) for a in range(3)] + [Sensor("target_distance"), Sensor("oscillator", freq=1.0), Sensor("oscillator", freq=1.0, phase=math.pi / 2)]
    if sources is not None:
        body.brain.units = _mount(sources, body.brain.units) + ([Sensor("oscillator", freq=1.0), Sensor("oscillator", freq=1.0, phase=math.pi / 2)] if "oscillator" in sources else [])
    smell = [Sensor(src) for src in ("food", "agent") if sources is not None and src in sources]

    def leg_segment(radius: float) -> Segment:
        seg = Segment(Shape.CYLINDER, (radius, 1.0))
        seg.brain.units = [Effector(0, 0.0)] + ([Sensor("joint_angle"), Sensor("contact")] if rich else []) + [Sensor(u.source) for u in smell]
        return seg

    def hip_connection(child: int, x: float, y: float) -> Connection:
        # underside corner, hanging down (the outward normal is -z), swinging fore-aft about the body's y axis
        return Connection(child=child, position=(x, y, -1.0), orientation=(0.0, 0.0, 0.0), scale=0.45, joint_type=JointType.HINGE, recursive_limit=1, axis=(0.0, 1.0, 0.0), joint_limit=0.9, motor="position")

    def knee_connection(child: int) -> Connection:
        return Connection(child=child, position=(1.0, 0.0, 0.0), orientation=(0.0, 0.0, 0.0), scale=0.8, joint_type=JointType.HINGE, recursive_limit=1, axis=(0.0, 1.0, 0.0), joint_limit=1.2, motor="position")

    corners = [(0.75, 0.8), (0.75, -0.8), (-0.75, 0.8), (-0.75, -0.8)]
    nodes = [Node(body, [hip_connection(h, x, y) for h, (x, y) in zip(QUAD_HIPS, corners)])]
    for h, sh in zip(QUAD_HIPS, QUAD_SHINS):
        nodes.append(Node(leg_segment(0.25), [knee_connection(sh)]))
    for sh in QUAD_SHINS:
        nodes.append(Node(leg_segment(0.22)))
    g = Genotype(nodes=nodes, root=QUAD_BODY, global_brain=Brain(units=[Neuron(0.0) for _ in range(hidden)]), name=name)
    n_body = len(body.brain.units)
    for h in range(hidden):
        for k in range(n_body):
            g.global_brain.links.append(Link(UnitRef(QUAD_BODY, k), UnitRef(None, h), 0.0))
        for h2 in range(hidden):
            g.global_brain.links.append(Link(UnitRef(None, h2), UnitRef(None, h), 0.0))
    for node in QUAD_HIPS + QUAD_SHINS:
        brain = g.nodes[node].segment.brain
        for h in range(hidden):
            brain.links.append(Link(UnitRef(None, h), UnitRef(node, 0), 0.0))
        if rich:
            brain.links.append(Link(UnitRef(node, 1), UnitRef(node, 0), 0.0))  # local reflex: own angle -> own effector
            for h in range(hidden):
                g.global_brain.links.append(Link(UnitRef(node, 1), UnitRef(None, h), 0.0))
    randomize_weights(g, rng, weight_sigma)
    assert g.is_valid(), g.validate()
    return g
