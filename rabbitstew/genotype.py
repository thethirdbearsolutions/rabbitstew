"""Robot genotypes.

A genotype is a directed graph of :class:`Node` objects (with an arbitrary
root).  Each Node holds one :class:`Segment` and a list of
:class:`Connection` objects.  A Connection attaches a child Node to the
parent with a relative position, orientation and scale, a joint type and a
recursive limit (circuits are allowed in the graph).  Each Segment carries a
:class:`Brain`, a directed graph of neural units (Sensors, Effectors and
Neurons) whose links store the network weights.  A genotype may also carry a
global Brain made only of Neurons which can be linked to any local unit.

Two fields extend the paper's Connection: ``axis`` (the hinge or slider axis
in the child's frame) and ``joint_limit`` (``None`` for an unlimited joint).
Both are needed to build physically sensible joints and to make a wheeled
fixed body expressible.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Iterator, Optional, Sequence

import numpy as np


class Shape(IntEnum):
    """Segment shape (two bits)."""

    BOX = 0
    SPHERE = 1
    CYLINDER = 2

    @property
    def ndims(self) -> int:
        return {Shape.BOX: 3, Shape.SPHERE: 1, Shape.CYLINDER: 2}[self]


class JointType(IntEnum):
    """Joint type between a Segment and its parent (two bits)."""

    HINGE = 0
    BALL = 1
    SLIDER = 2
    FIXED = 3

    @property
    def ndof(self) -> int:
        return {JointType.HINGE: 1, JointType.BALL: 3, JointType.SLIDER: 1, JointType.FIXED: 0}[self]


# --------------------------------------------------------------------------- #
# Neural units
# --------------------------------------------------------------------------- #

#: The paper's sensor set.
PAPER_SENSOR_SOURCES = ("contact", "target", "opponent")
#: Vector-valued sources come in sets of three (``axis`` 0..2), all in the Segment's own frame.
VECTOR_SOURCES = ("target", "opponent", "up", "velocity")
#: Scalar sources.
SCALAR_SOURCES = ("contact", "target_distance", "opponent_distance", "joint_angle", "joint_velocity", "height", "oscillator", "food", "agent")
SENSOR_SOURCES = VECTOR_SOURCES + SCALAR_SOURCES
#: The oracle-free set for the foraging world: nothing tells a robot where anything is.  ``food`` and
#: ``agent`` are intensities at the Segment's own position (a smell), so a gradient exists only
#: between two Segments in different places, or across the same Segment's motion.
FORAGING_SENSOR_SOURCES = ("contact", "up", "velocity", "joint_angle", "joint_velocity", "height", "oscillator", "food", "agent")

#: Neuron transfer functions.  ``tanh`` is the paper's model.
NEURON_FUNCS = ("tanh", "sin", "abs", "relu", "sign", "integrate", "differentiate")
#: Joint motor modes.  ``torque`` is the paper's model; the others are servos.
MOTOR_MODES = ("torque", "position", "velocity")


@dataclass
class Sensor:
    """Input unit.

    ``source`` names what is read (see :data:`SENSOR_SOURCES`):

    * ``contact`` -- 1 while the Segment touches any other body, else 0.
    * ``target`` / ``opponent`` -- one component (``axis``) of the normalised
      direction from the Segment centre to the world target or to the
      opponent's root Segment, in the Segment's own frame.
    * ``up`` -- one component of the world up vector in the Segment's frame
      (orientation / gravity sense).
    * ``velocity`` -- one component of the Segment's linear velocity in its
      own frame, squashed with ``tanh``.
    * ``target_distance`` / ``opponent_distance`` -- ``d / (1 + d)`` of the
      horizontal distance in metres.
    * ``joint_angle`` / ``joint_velocity`` -- the Segment's parent joint
      position (normalised to its range, or ``sin`` of the angle when
      unlimited) or its velocity squashed with ``tanh``; 0 on the root and on
      fixed joints.
    * ``height`` -- ``tanh`` of the Segment centre's height in metres.
    * ``oscillator`` -- ``sin(2 pi freq t + phase)``: a central pattern
      generator, independent of the environment.
    """

    source: str = "contact"
    axis: int = 0
    freq: float = 1.0  #: oscillator frequency (Hz)
    phase: float = 0.0  #: oscillator phase (radians)

    kind = "sensor"

    def to_dict(self):
        d = {"kind": "sensor", "source": self.source, "axis": self.axis}
        if self.source == "oscillator":
            d["freq"] = self.freq
            d["phase"] = self.phase
        return d

    @property
    def label(self) -> str:
        if self.source in VECTOR_SOURCES:
            return f"{self.source} {'xyz'[self.axis]}"
        if self.source == "oscillator":
            return f"osc {self.freq:.2g} Hz"
        return self.source


@dataclass
class Neuron:
    """Processing unit: ``func(bias + sum(weight * input))``.

    ``func`` is one of :data:`NEURON_FUNCS`.  ``integrate`` is a leaky
    integrator of its input and ``differentiate`` responds to the change in
    its input between ticks; all others are memoryless.
    """

    bias: float = 0.0
    func: str = "tanh"

    kind = "neuron"

    def to_dict(self):
        d = {"kind": "neuron", "bias": self.bias}
        if self.func != "tanh":
            d["func"] = self.func
        return d


@dataclass
class Effector:
    """Output unit sending torque (or force) to the parent joint of its Segment.

    ``dof`` selects the degree of freedom driven on a ball joint (0..2); it is
    ignored for hinge and slider joints and the unit is inert on fixed joints
    and on the root Segment.
    """

    dof: int = 0
    bias: float = 0.0

    kind = "effector"

    def to_dict(self):
        return {"kind": "effector", "dof": self.dof, "bias": self.bias}


Unit = Sensor | Neuron | Effector


def unit_from_dict(d) -> Unit:
    kind = d["kind"]
    if kind == "sensor":
        return Sensor(source=d.get("source", "contact"), axis=int(d.get("axis", 0)), freq=float(d.get("freq", 1.0)), phase=float(d.get("phase", 0.0)))
    if kind == "neuron":
        return Neuron(bias=float(d.get("bias", 0.0)), func=str(d.get("func", "tanh")))
    if kind == "effector":
        return Effector(dof=int(d.get("dof", 0)), bias=float(d.get("bias", 0.0)))
    raise ValueError(f"unknown unit kind {kind!r}")


@dataclass(frozen=True)
class UnitRef:
    """Reference to a neural unit: ``node`` is a Node index or ``None`` for the global Brain."""

    node: Optional[int]
    index: int

    def to_list(self):
        return [self.node, self.index]

    @staticmethod
    def from_list(lst) -> "UnitRef":
        return UnitRef(None if lst[0] is None else int(lst[0]), int(lst[1]))


@dataclass
class Link:
    """Weighted connection between two neural units.

    Links are stored in the Brain owning the destination unit.
    """

    src: UnitRef
    dst: UnitRef
    weight: float = 0.0

    def to_dict(self):
        return {"src": self.src.to_list(), "dst": self.dst.to_list(), "weight": self.weight}

    @staticmethod
    def from_dict(d) -> "Link":
        return Link(UnitRef.from_list(d["src"]), UnitRef.from_list(d["dst"]), float(d["weight"]))


@dataclass
class Brain:
    """Directed graph of neural units with weighted links."""

    units: list = field(default_factory=list)
    links: list = field(default_factory=list)

    def to_dict(self):
        return {"units": [u.to_dict() for u in self.units], "links": [l.to_dict() for l in self.links]}

    @staticmethod
    def from_dict(d) -> "Brain":
        return Brain(
            units=[unit_from_dict(u) for u in d.get("units", [])],
            links=[Link.from_dict(l) for l in d.get("links", [])],
        )

    def copy(self) -> "Brain":
        return Brain.from_dict(self.to_dict())

    def units_of_kind(self, kind: str) -> list[int]:
        return [i for i, u in enumerate(self.units) if u.kind == kind]


# --------------------------------------------------------------------------- #
# Body units
# --------------------------------------------------------------------------- #


@dataclass
class Segment:
    """One body unit.

    ``dims`` are *relative* dimensions: ``(x, y, z)`` extents for a box,
    ``(radius,)`` for a sphere, ``(radius, length)`` for a cylinder.  They are
    normalised to unit volume (:meth:`normalized_dims`); absolute size comes
    from the scale factors along the path from the root at synthesis time.
    """

    shape: Shape = Shape.BOX
    dims: tuple = (1.0, 1.0, 1.0)
    brain: Brain = field(default_factory=Brain)

    def volume(self, dims=None) -> float:
        d = self.dims if dims is None else dims
        if self.shape == Shape.BOX:
            return d[0] * d[1] * d[2]
        if self.shape == Shape.SPHERE:
            return 4.0 / 3.0 * math.pi * d[0] ** 3
        return math.pi * d[0] ** 2 * d[1]

    def normalized_dims(self) -> tuple:
        """Dimensions scaled so the Segment encloses unit volume."""
        v = self.volume()
        if v <= 0:
            raise ValueError("segment has non-positive volume")
        s = v ** (-1.0 / 3.0)
        return tuple(float(x * s) for x in self.dims)

    def to_dict(self):
        return {"shape": int(self.shape), "dims": [float(x) for x in self.dims], "brain": self.brain.to_dict()}

    @staticmethod
    def from_dict(d) -> "Segment":
        return Segment(Shape(int(d["shape"])), tuple(float(x) for x in d["dims"]), Brain.from_dict(d.get("brain", {})))


@dataclass
class Connection:
    """Physical attachment of a child Node to its parent.

    ``position`` is a point in ``[-1, 1]^3`` mapped onto the parent's surface;
    ``orientation`` gives Euler angles (radians) of the child relative to the
    outward normal at the attachment point; ``scale`` multiplies the parent's
    size to give the child's; ``recursive_limit`` is the maximum number of
    instances of the child Node allowed along one root-to-leaf path.
    """

    child: int
    position: tuple = (1.0, 0.0, 0.0)
    orientation: tuple = (0.0, 0.0, 0.0)
    scale: float = 0.7
    joint_type: JointType = JointType.HINGE
    recursive_limit: int = 1
    axis: tuple = (0.0, 0.0, 1.0)
    joint_limit: Optional[float] = math.pi / 2
    motor: str = "torque"  #: one of MOTOR_MODES; ball joints are always torque driven
    mirror: bool = False  #: also synthesise a twin reflected across the parent's x-z plane (Sims' reflection)

    def to_dict(self):
        return {
            "child": self.child,
            "motor": self.motor,
            "mirror": self.mirror,
            "position": [float(x) for x in self.position],
            "orientation": [float(x) for x in self.orientation],
            "scale": float(self.scale),
            "joint_type": int(self.joint_type),
            "recursive_limit": int(self.recursive_limit),
            "axis": [float(x) for x in self.axis],
            "joint_limit": None if self.joint_limit is None else float(self.joint_limit),
        }

    @staticmethod
    def from_dict(d) -> "Connection":
        return Connection(
            child=int(d["child"]),
            position=tuple(float(x) for x in d.get("position", (1.0, 0.0, 0.0))),
            orientation=tuple(float(x) for x in d.get("orientation", (0.0, 0.0, 0.0))),
            scale=float(d.get("scale", 0.7)),
            joint_type=JointType(int(d.get("joint_type", 0))),
            recursive_limit=int(d.get("recursive_limit", 1)),
            axis=tuple(float(x) for x in d.get("axis", (0.0, 0.0, 1.0))),
            joint_limit=None if d.get("joint_limit") is None else float(d["joint_limit"]),
            motor=str(d.get("motor", "torque")),
            mirror=bool(d.get("mirror", False)),
        )


@dataclass
class Node:
    segment: Segment = field(default_factory=Segment)
    connections: list = field(default_factory=list)

    def to_dict(self):
        return {"segment": self.segment.to_dict(), "connections": [c.to_dict() for c in self.connections]}

    @staticmethod
    def from_dict(d) -> "Node":
        return Node(Segment.from_dict(d["segment"]), [Connection.from_dict(c) for c in d.get("connections", [])])


@dataclass
class Genotype:
    """A complete robot genotype: a node graph, a root index and an optional global Brain."""

    nodes: list = field(default_factory=list)
    root: int = 0
    global_brain: Optional[Brain] = None
    name: str = ""
    parents: list = field(default_factory=list)  #: names of the genotype(s) this one was bred from
    record: dict = field(default_factory=dict)  #: evaluation record under survival selection: evals, fitness_sum, born

    # -- serialisation ------------------------------------------------------ #
    def to_dict(self):
        return {
            "format": "rabbitstew-genotype",
            "version": 1,
            "name": self.name,
            "parents": list(self.parents),
            "record": dict(self.record),
            "root": self.root,
            "nodes": [n.to_dict() for n in self.nodes],
            "global_brain": None if self.global_brain is None else self.global_brain.to_dict(),
        }

    @staticmethod
    def from_dict(d) -> "Genotype":
        gb = d.get("global_brain")
        return Genotype(
            nodes=[Node.from_dict(n) for n in d["nodes"]],
            root=int(d.get("root", 0)),
            global_brain=None if gb is None else Brain.from_dict(gb),
            name=str(d.get("name", "")),
            parents=[str(x) for x in d.get("parents", [])],
            record=dict(d.get("record", {})),
        )

    def to_json(self, **kw) -> str:
        kw.setdefault("indent", 2)
        return json.dumps(self.to_dict(), **kw)

    @staticmethod
    def from_json(text: str) -> "Genotype":
        return Genotype.from_dict(json.loads(text))

    def save(self, path) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())
            f.write("\n")

    @staticmethod
    def load(path) -> "Genotype":
        with open(path) as f:
            return Genotype.from_json(f.read())

    def copy(self) -> "Genotype":
        return Genotype.from_dict(self.to_dict())

    # -- helpers ------------------------------------------------------------ #
    def brains(self) -> Iterator[tuple[Optional[int], Brain]]:
        """Yield ``(node_index_or_None, brain)`` for every Brain in the genotype."""
        for i, n in enumerate(self.nodes):
            yield i, n.segment.brain
        if self.global_brain is not None:
            yield None, self.global_brain

    def brain_of(self, node: Optional[int]) -> Optional[Brain]:
        if node is None:
            return self.global_brain
        return self.nodes[node].segment.brain

    def unit(self, ref: UnitRef) -> Unit:
        return self.brain_of(ref.node).units[ref.index]

    def neighbours(self, node: int) -> list[int]:
        """Nodes joined to ``node`` by a Connection in either direction (its children and its parents), excluding itself."""
        out: list[int] = []
        for c in self.nodes[node].connections:
            if c.child != node and c.child not in out:
                out.append(c.child)
        for i, n in enumerate(self.nodes):
            if i != node and any(c.child == node for c in n.connections) and i not in out:
                out.append(i)
        return out

    def reachable_nodes(self) -> list[int]:
        seen = []
        stack = [self.root]
        while stack:
            i = stack.pop()
            if i in seen:
                continue
            seen.append(i)
            stack.extend(c.child for c in self.nodes[i].connections)
        return seen

    def count_links(self) -> int:
        return sum(len(b.links) for _, b in self.brains())

    # -- validation --------------------------------------------------------- #
    def validate(self) -> list[str]:
        """Return a list of problems (empty when the genotype is well formed)."""
        problems: list[str] = []
        n = len(self.nodes)
        if n == 0:
            return ["genotype has no nodes"]
        if not 0 <= self.root < n:
            problems.append(f"root {self.root} out of range")
        for i, node in enumerate(self.nodes):
            seg = node.segment
            if len(seg.dims) != seg.shape.ndims:
                problems.append(f"node {i}: shape {seg.shape.name} needs {seg.shape.ndims} dims, got {len(seg.dims)}")
            elif any(d <= 0 for d in seg.dims):
                problems.append(f"node {i}: non-positive dimension")
            for j, c in enumerate(node.connections):
                if not 0 <= c.child < n:
                    problems.append(f"node {i} connection {j}: child {c.child} out of range")
                if c.scale <= 0:
                    problems.append(f"node {i} connection {j}: non-positive scale")
                if c.recursive_limit < 1:
                    problems.append(f"node {i} connection {j}: recursive_limit < 1")
                if len(c.position) != 3 or len(c.orientation) != 3 or len(c.axis) != 3:
                    problems.append(f"node {i} connection {j}: position/orientation/axis must have 3 components")
                if c.joint_limit is not None and c.joint_limit < 0:
                    problems.append(f"node {i} connection {j}: negative joint_limit")
                if c.motor not in MOTOR_MODES:
                    problems.append(f"node {i} connection {j}: unknown motor mode {c.motor!r}")
            problems.extend(self._validate_brain(i, seg.brain))
        if self.global_brain is not None:
            for k, u in enumerate(self.global_brain.units):
                if u.kind != "neuron":
                    problems.append(f"global brain unit {k}: only Neurons are allowed in the global Brain")
            problems.extend(self._validate_brain(None, self.global_brain))
        return problems

    def _validate_brain(self, owner: Optional[int], brain: Brain) -> list[str]:
        problems = []
        label = "global brain" if owner is None else f"node {owner} brain"
        for k, u in enumerate(brain.units):
            if u.kind == "sensor":
                if u.source not in SENSOR_SOURCES:
                    problems.append(f"{label} unit {k}: unknown sensor source {u.source!r}")
                if u.source in VECTOR_SOURCES and not 0 <= u.axis < 3:
                    problems.append(f"{label} unit {k}: vector sensor axis out of range")
                if u.source == "oscillator" and u.freq <= 0:
                    problems.append(f"{label} unit {k}: oscillator frequency must be positive")
            elif u.kind == "neuron" and u.func not in NEURON_FUNCS:
                problems.append(f"{label} unit {k}: unknown neuron function {u.func!r}")
            elif u.kind == "effector" and not 0 <= u.dof < 3:
                problems.append(f"{label} unit {k}: effector dof out of range")
        for k, l in enumerate(brain.links):
            if l.dst.node != owner:
                problems.append(f"{label} link {k}: destination belongs to another brain")
                continue
            if owner is not None and l.src.node not in (owner, None) and not (l.src.node is not None and 0 <= l.src.node < len(self.nodes) and l.src.node in self.neighbours(owner)):
                problems.append(f"{label} link {k}: source must be local, global or a neighbouring node's unit")
                continue
            for ref in (l.src, l.dst):
                b = self.brain_of(ref.node) if (ref.node is None or 0 <= ref.node < len(self.nodes)) else None
                if b is None or not 0 <= ref.index < len(b.units):
                    problems.append(f"{label} link {k}: unit reference {ref} out of range")
                    break
            else:
                if self.unit(l.dst).kind == "sensor":
                    problems.append(f"{label} link {k}: sensors cannot receive links")
        return problems

    def is_valid(self) -> bool:
        return not self.validate()


# --------------------------------------------------------------------------- #
# Random generation
# --------------------------------------------------------------------------- #


def random_segment(rng: np.random.Generator, shape: Optional[Shape] = None) -> Segment:
    if shape is None:
        shape = Shape(int(rng.integers(0, 3)))
    dims = tuple(float(x) for x in rng.uniform(0.3, 1.0, size=shape.ndims))
    return Segment(shape=shape, dims=dims)


def random_connection(rng: np.random.Generator, n_nodes: int, joint_types=tuple(JointType), vocab: Optional[BrainVocabulary] = None) -> Connection:
    vocab = vocab or BrainVocabulary()
    axis = rng.normal(size=3)
    axis /= max(np.linalg.norm(axis), 1e-9)
    joint = JointType(int(rng.choice([int(j) for j in joint_types])))
    return Connection(
        motor=str(rng.choice(list(vocab.motor_modes))),
        mirror=bool(rng.random() < vocab.mirror_rate),
        child=int(rng.integers(0, n_nodes)),
        position=tuple(float(x) for x in rng.uniform(-1.0, 1.0, size=3)),
        orientation=tuple(float(x) for x in rng.uniform(-math.pi / 2, math.pi / 2, size=3)),
        scale=float(rng.uniform(0.4, 0.9)),
        joint_type=joint,
        recursive_limit=int(rng.integers(1, 3)),
        axis=tuple(float(x) for x in axis),
        joint_limit=float(rng.uniform(0.3, math.pi / 2)) if rng.random() < 0.8 else None,
    )


@dataclass
class BrainVocabulary:
    """Which sensor sources, neuron functions and motor modes random generation and mutation may use."""

    sensor_sources: tuple = PAPER_SENSOR_SOURCES
    neuron_funcs: tuple = ("tanh",)
    motor_modes: tuple = ("torque",)
    mirror_rate: float = 0.0  #: probability that a random Connection is mirrored (0 = the paper's encoding)
    neighbour_links: bool = False  #: a local Brain may also read units of neighbouring nodes (parent and children), as in Sims (1994)

    @staticmethod
    def paper() -> "BrainVocabulary":
        return BrainVocabulary()

    @staticmethod
    def rich() -> "BrainVocabulary":
        return BrainVocabulary(sensor_sources=SENSOR_SOURCES, neuron_funcs=NEURON_FUNCS, motor_modes=MOTOR_MODES)

    @staticmethod
    def foraging() -> "BrainVocabulary":
        """The rich vocabulary without the oracle sensors (target and opponent direction and distance)."""
        return BrainVocabulary(sensor_sources=FORAGING_SENSOR_SOURCES, neuron_funcs=NEURON_FUNCS, motor_modes=MOTOR_MODES)

    @staticmethod
    def named(name: str) -> "BrainVocabulary":
        if name == "paper":
            return BrainVocabulary.paper()
        if name == "foraging":
            return BrainVocabulary.foraging()
        if name == "rich":
            return BrainVocabulary.rich()
        raise ValueError(f"unknown brain model {name!r}")

    def to_dict(self):
        return {"sensor_sources": list(self.sensor_sources), "neuron_funcs": list(self.neuron_funcs), "motor_modes": list(self.motor_modes), "mirror_rate": self.mirror_rate, "neighbour_links": self.neighbour_links}

    @staticmethod
    def from_dict(d) -> "BrainVocabulary":
        return BrainVocabulary(tuple(d["sensor_sources"]), tuple(d["neuron_funcs"]), tuple(d["motor_modes"]), float(d.get("mirror_rate", 0.0)), bool(d.get("neighbour_links", False)))


def random_sensor_set(rng: np.random.Generator, vocab: Optional[BrainVocabulary] = None) -> list:
    """One random sensor, or a set of three for a vector-valued source."""
    vocab = vocab or BrainVocabulary()
    source = str(rng.choice(list(vocab.sensor_sources)))
    if source in VECTOR_SOURCES:
        return [Sensor(source, axis) for axis in range(3)]
    if source == "oscillator":
        return [Sensor("oscillator", 0, freq=float(rng.uniform(0.3, 3.0)), phase=float(rng.uniform(0, 2 * math.pi)))]
    return [Sensor(source)]


def random_neuron(rng: np.random.Generator, vocab: Optional[BrainVocabulary] = None) -> Neuron:
    vocab = vocab or BrainVocabulary()
    return Neuron(float(rng.normal(0, 0.5)), str(rng.choice(list(vocab.neuron_funcs))))


def random_units(rng: np.random.Generator, max_sensor_sets=2, max_neurons=3, max_effectors=2, vocab: Optional[BrainVocabulary] = None) -> list:
    vocab = vocab or BrainVocabulary()
    units: list = []
    for _ in range(int(rng.integers(0, max_sensor_sets + 1))):
        units.extend(random_sensor_set(rng, vocab))
    units.extend(random_neuron(rng, vocab) for _ in range(int(rng.integers(0, max_neurons + 1))))
    units.extend(
        Effector(int(rng.integers(0, 3)), float(rng.normal(0, 0.5)))
        for _ in range(int(rng.integers(0, max_effectors + 1)))
    )
    return units


def random_links(rng: np.random.Generator, genotype: Genotype, owner: Optional[int], density=0.5, weight_sigma=1.0, vocab: Optional[BrainVocabulary] = None):
    """Populate the links of one Brain with random weights."""
    brain = genotype.brain_of(owner)
    assert brain is not None
    brain.links = []
    sources: list[UnitRef] = [UnitRef(owner, i) for i in range(len(brain.units))]
    if owner is not None:
        if genotype.global_brain is not None:
            sources += [UnitRef(None, i) for i in range(len(genotype.global_brain.units))]
        if vocab is not None and vocab.neighbour_links:
            for nb in genotype.neighbours(owner):
                sources += [UnitRef(nb, k) for k in range(len(genotype.nodes[nb].segment.brain.units))]
    else:
        for i, node in enumerate(genotype.nodes):
            sources += [UnitRef(i, k) for k in range(len(node.segment.brain.units))]
    for k, u in enumerate(brain.units):
        if u.kind == "sensor":
            continue
        for src in sources:
            if rng.random() < density:
                brain.links.append(Link(src, UnitRef(owner, k), float(rng.normal(0, weight_sigma))))


def random_genotype(
    rng: np.random.Generator,
    n_nodes: Optional[int] = None,
    max_connections: int = 3,
    global_neurons: Optional[int] = None,
    link_density: float = 0.5,
    name: str = "",
    vocab: Optional[BrainVocabulary] = None,
) -> Genotype:
    """Generate a random, valid genotype."""
    vocab = vocab or BrainVocabulary()
    if n_nodes is None:
        n_nodes = int(rng.integers(2, 6))
    nodes = []
    for _ in range(n_nodes):
        seg = random_segment(rng)
        seg.brain.units = random_units(rng, vocab=vocab)
        node = Node(segment=seg)
        for _ in range(int(rng.integers(0, max_connections + 1))):
            node.connections.append(random_connection(rng, n_nodes, vocab=vocab))
        nodes.append(node)
    # Make sure the root has at least one connection so bodies are rarely single blobs.
    root = int(rng.integers(0, n_nodes))
    if not nodes[root].connections:
        nodes[root].connections.append(random_connection(rng, n_nodes, vocab=vocab))
    if global_neurons is None:
        global_neurons = int(rng.integers(0, 5))
    gb = Brain(units=[random_neuron(rng, vocab) for _ in range(global_neurons)]) if global_neurons else None
    g = Genotype(nodes=nodes, root=root, global_brain=gb, name=name)
    for owner, _ in g.brains():
        random_links(rng, g, owner, density=link_density, vocab=vocab)
    problems = g.validate()
    assert not problems, problems
    return g
