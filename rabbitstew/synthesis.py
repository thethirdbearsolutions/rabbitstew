"""Genotype -> phenotype synthesis.

Synthesis walks the genotype graph breadth-first from the root Node, creating
one :class:`Part` per visited Node instance until the externally imposed
size-ratio limit halts the process.  A Connection is followed only while the
number of instances of its child Node on the current root-to-part path is
below the Connection's ``recursive_limit``.  The breadth-first order means
that as many distinct Nodes as possible are expressed before the limit hits;
Nodes that are never reached are simply not expressed (recessive material).

Each Part gets its own instance of its Node's local Brain; the global Brain
is instantiated once.  Links from a local unit into the global Brain are
summed over all instances of that Node.
"""

from __future__ import annotations

import math
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from . import quat
from .genotype import Effector, Genotype, JointType, Segment, Sensor, Shape, UnitRef


@dataclass
class SynthesisConfig:
    """Externally imposed, user-defined synthesis parameters."""

    size_ratio_limit: float = 2.0  #: max body parts = ceil(size_ratio_limit * number of Nodes)
    root_size: float = 0.3  #: characteristic length (m) of the root Segment (unit volume ** 1/3)
    min_size: float = 0.06  #: clamp on any Part's characteristic length
    max_size: float = 0.6
    density: float = 500.0  #: kg / m^3 for every Segment
    hard_part_cap: int = 64  #: absolute safety cap on parts per robot
    mass_budget: Optional[float] = None  #: if set, a robot heavier than this (kg) has every part's mass scaled down to meet it

    def max_parts(self, n_nodes: int) -> int:
        return max(1, min(self.hard_part_cap, math.ceil(self.size_ratio_limit * n_nodes)))


@dataclass
class Part:
    """One synthesised body unit."""

    index: int
    node: int
    parent: Optional[int]  #: parent Part index (None for the root)
    size: float  #: characteristic length (m)
    shape: Shape
    dims: tuple  #: absolute dimensions (box extents / sphere radius / cylinder radius, length)
    attach_pos: np.ndarray  #: joint anchor, in the parent Part's frame (zero for the root)
    rel_quat: np.ndarray  #: orientation relative to the parent Part (identity for the root)
    geom_offset: float  #: distance from the joint anchor to the geom centre along local +X
    joint_type: JointType
    joint_axis: np.ndarray  #: hinge / slider axis in this Part's frame
    joint_range: Optional[tuple]  #: (lo, hi) or None for unlimited
    mass: float
    depth: int
    connection_index: Optional[int] = None  #: index of the Connection in the parent Node
    motor: str = "torque"  #: motor mode of the joint to the parent
    mirrored: bool = False  #: this Part is the reflected twin of a mirrored Connection

    @property
    def half_length(self) -> float:
        """Half extent of the Part along its local X axis."""
        if self.shape == Shape.BOX:
            return self.dims[0] / 2.0
        if self.shape == Shape.SPHERE:
            return self.dims[0]
        return self.dims[1] / 2.0

    def volume(self) -> float:
        return Segment(self.shape, self.dims).volume()


@dataclass
class UnitInstance:
    part: Optional[int]  #: Part index, or None for a global unit
    ref: UnitRef  #: genotype unit reference
    unit: object  #: the Sensor / Neuron / Effector


@dataclass
class Phenotype:
    genotype: Genotype
    parts: list = field(default_factory=list)
    units: list = field(default_factory=list)  #: list[UnitInstance]
    links: list = field(default_factory=list)  #: list[(src_unit_idx, dst_unit_idx, weight)]
    node_instances: dict = field(default_factory=dict)  #: node index -> [part indices]
    truncated: bool = False  #: True when the size-ratio limit stopped synthesis early
    mass_scaled: float = 1.0  #: < 1 when a mass budget reduced every part's mass

    @property
    def root(self) -> Part:
        return self.parts[0]

    def total_mass(self) -> float:
        return sum(p.mass for p in self.parts)

    def units_of_part(self, part: Optional[int]) -> list[int]:
        return [i for i, u in enumerate(self.units) if u.part == part]


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #


def mirror_connection(conn):
    """The reflection of a Connection across the parent's x-z plane: y of the attachment, the
    orientation's x and z rotations, and the y of the joint axis change sign."""
    from dataclasses import replace

    px, py, pz = conn.position
    rx, ry, rz = conn.orientation
    ax, ay, az = conn.axis
    return replace(conn, position=(px, -py, pz), orientation=(-rx, ry, -rz), axis=(ax, -ay, az), mirror=False)


def absolute_dims(segment: Segment, size: float) -> tuple:
    return tuple(d * size for d in segment.normalized_dims())


def surface_point(shape: Shape, dims: tuple, position) -> np.ndarray:
    """Map a point of ``[-1, 1]^3`` onto the surface of a Segment (local frame).

    Boxes map component-wise onto their half extents; spheres project the
    point radially; cylinders (length along local X) use an end cap when the
    X component dominates and the curved side otherwise.
    """
    p = np.clip(np.asarray(position, dtype=float), -1.0, 1.0)
    if shape == Shape.BOX:
        half = np.asarray(dims) / 2.0
        # Push the point to the face whose component is largest so it lies on the surface.
        if np.all(np.abs(p) < 1e-9):
            p = np.array([1.0, 0.0, 0.0])
        k = int(np.argmax(np.abs(p)))
        p = p.copy()
        p[k] = math.copysign(1.0, p[k]) if p[k] != 0 else 1.0
        return p * half
    if shape == Shape.SPHERE:
        n = np.linalg.norm(p)
        if n < 1e-9:
            return np.array([dims[0], 0.0, 0.0])
        return p / n * dims[0]
    radius, length = dims
    h = length / 2.0
    yz = p[1:]
    nyz = np.linalg.norm(yz)
    if abs(p[0]) >= nyz:  # end cap
        x = math.copysign(h, p[0]) if p[0] != 0 else h
        return np.array([x, yz[0] * radius, yz[1] * radius])
    return np.array([p[0] * h, yz[0] / nyz * radius, yz[1] / nyz * radius])


def outward_normal(shape: Shape, dims: tuple, point: np.ndarray) -> np.ndarray:
    """Outward surface normal at ``point`` (a surface point in the local frame)."""
    if shape == Shape.BOX:
        half = np.asarray(dims) / 2.0
        ratios = np.abs(point) / np.maximum(half, 1e-9)
        k = int(np.argmax(ratios))
        n = np.zeros(3)
        n[k] = math.copysign(1.0, point[k]) if point[k] != 0 else 1.0
        return n
    if shape == Shape.SPHERE:
        n = np.linalg.norm(point)
        return point / n if n > 1e-9 else np.array([1.0, 0.0, 0.0])
    radius, length = dims
    if abs(abs(point[0]) - length / 2.0) < 1e-9 and np.linalg.norm(point[1:]) < radius - 1e-9:
        return np.array([math.copysign(1.0, point[0]), 0.0, 0.0])
    n = np.array([0.0, point[1], point[2]])
    m = np.linalg.norm(n)
    return n / m if m > 1e-9 else np.array([math.copysign(1.0, point[0]) if point[0] else 1.0, 0.0, 0.0])


# --------------------------------------------------------------------------- #
# Synthesis
# --------------------------------------------------------------------------- #


def synthesize(genotype: Genotype, config: Optional[SynthesisConfig] = None) -> Phenotype:
    """Expand ``genotype`` into a :class:`Phenotype` (breadth-first)."""
    if config is None:
        config = SynthesisConfig()
    problems = genotype.validate()
    if problems:
        raise ValueError("invalid genotype: " + "; ".join(problems))

    ph = Phenotype(genotype=genotype)
    max_parts = config.max_parts(len(genotype.nodes))
    # queue items: (node, parent_part_index, connection_index, path_counter, depth, mirrored)
    queue = deque([(genotype.root, None, None, Counter(), 0, False)])
    while queue:
        node_id, parent_idx, conn_idx, path, depth, mirrored = queue.popleft()
        if len(ph.parts) >= max_parts:
            ph.truncated = True
            break
        node = genotype.nodes[node_id]
        seg = node.segment
        if parent_idx is None:
            size = float(np.clip(config.root_size, config.min_size, config.max_size))
            dims = absolute_dims(seg, size)
            part = Part(
                index=len(ph.parts),
                node=node_id,
                parent=None,
                size=size,
                shape=seg.shape,
                dims=dims,
                attach_pos=np.zeros(3),
                rel_quat=quat.IDENTITY.copy(),
                geom_offset=0.0,
                joint_type=JointType.FIXED,
                joint_axis=np.array([0.0, 0.0, 1.0]),
                joint_range=None,
                mass=Segment(seg.shape, dims).volume() * config.density,
                depth=0,
            )
        else:
            parent = ph.parts[parent_idx]
            conn = genotype.nodes[parent.node].connections[conn_idx]
            if mirrored:
                conn = mirror_connection(conn)
            size = float(np.clip(parent.size * conn.scale, config.min_size, config.max_size))
            dims = absolute_dims(seg, size)
            attach = surface_point(parent.shape, parent.dims, conn.position)
            normal = outward_normal(parent.shape, parent.dims, attach)
            rel = quat.multiply(quat.align_x_to(normal), quat.from_euler(*conn.orientation))
            axis = np.asarray(conn.axis, dtype=float)
            if np.linalg.norm(axis) < 1e-9:
                axis = np.array([0.0, 0.0, 1.0])
            axis = axis / np.linalg.norm(axis)
            if conn.joint_type == JointType.HINGE:
                rng_ = None if conn.joint_limit is None else (-conn.joint_limit, conn.joint_limit)
            elif conn.joint_type == JointType.SLIDER:
                lim = 0.5 * size if conn.joint_limit is None else conn.joint_limit * size
                rng_ = (-lim, lim)
            else:
                rng_ = None
            tmp = Part(
                index=len(ph.parts),
                node=node_id,
                parent=parent_idx,
                size=size,
                shape=seg.shape,
                dims=dims,
                attach_pos=attach,
                rel_quat=rel,
                geom_offset=0.0,
                joint_type=conn.joint_type,
                joint_axis=axis,
                joint_range=rng_,
                mass=Segment(seg.shape, dims).volume() * config.density,
                depth=depth,
                connection_index=conn_idx,
                motor=conn.motor if conn.joint_type != JointType.BALL else "torque",
                mirrored=mirrored,
            )
            tmp.geom_offset = tmp.half_length
            part = tmp
        ph.parts.append(part)
        ph.node_instances.setdefault(node_id, []).append(part.index)
        new_path = path.copy()
        new_path[node_id] += 1
        for ci, conn in enumerate(node.connections):
            if new_path[conn.child] < conn.recursive_limit:
                queue.append((conn.child, part.index, ci, new_path, depth + 1, False))
                if conn.mirror:
                    queue.append((conn.child, part.index, ci, new_path, depth + 1, True))
    if queue:
        ph.truncated = True

    if config.mass_budget is not None:
        total = ph.total_mass()
        if total > config.mass_budget > 0:
            scale = config.mass_budget / total
            for p in ph.parts:
                p.mass *= scale
            ph.mass_scaled = scale

    _synthesize_brains(ph)
    return ph


def _synthesize_brains(ph: Phenotype) -> None:
    g = ph.genotype
    index: dict[tuple[Optional[int], int], int] = {}  # (part or None, unit index) -> unit instance idx
    for part in ph.parts:
        brain = g.nodes[part.node].segment.brain
        for k, u in enumerate(brain.units):
            index[(part.index, k)] = len(ph.units)
            ph.units.append(UnitInstance(part.index, UnitRef(part.node, k), u))
    if g.global_brain is not None:
        for k, u in enumerate(g.global_brain.units):
            index[(None, k)] = len(ph.units)
            ph.units.append(UnitInstance(None, UnitRef(None, k), u))

    # Local brain links, per part instance.
    for part in ph.parts:
        brain = g.nodes[part.node].segment.brain
        for link in brain.links:
            dst = index[(part.index, link.dst.index)]
            if link.src.node is None:
                src = index[(None, link.src.index)]
            else:
                src = index[(part.index, link.src.index)]
            ph.links.append((src, dst, float(link.weight)))
    # Global brain links: local sources are summed over every instance of the node.
    if g.global_brain is not None:
        for link in g.global_brain.links:
            dst = index[(None, link.dst.index)]
            if link.src.node is None:
                ph.links.append((index[(None, link.src.index)], dst, float(link.weight)))
            else:
                for pidx in ph.node_instances.get(link.src.node, []):
                    ph.links.append((index[(pidx, link.src.index)], dst, float(link.weight)))


def describe(ph: Phenotype) -> str:
    """Human-readable summary of a phenotype."""
    lines = [
        f"{len(ph.parts)} parts from {len(ph.genotype.nodes)} nodes"
        + (" (truncated by size-ratio limit)" if ph.truncated else ""),
        f"mass {ph.total_mass():.2f} kg, {len(ph.units)} neural units, {len(ph.links)} links",
    ]
    for p in ph.parts:
        dims = ", ".join(f"{d:.3f}" for d in p.dims)
        parent = "root" if p.parent is None else f"child of part {p.parent} via {p.joint_type.name.lower()}"
        n_units = len(ph.units_of_part(p.index))
        lines.append(f"  part {p.index}: node {p.node} {p.shape.name.lower()} [{dims}] {p.mass:.2f} kg, {parent}, {n_units} units")
    return "\n".join(lines)
