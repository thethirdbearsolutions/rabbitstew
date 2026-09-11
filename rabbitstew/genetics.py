"""Genetic operators.

Two regimes are provided:

* **holistic** -- :func:`mutate` and :func:`crossover` change morphology and
  control together: segment shapes and dimensions, connection geometry, joint
  types and limits, recursive limits, the node graph itself, neural units and
  links, and all weights.
* **conventional** -- :func:`mutate_weights` and :func:`crossover_weights`
  touch only link weights and unit biases, leaving the morphology and the
  network topology exactly as designed.

All operators return new genotypes and never modify their inputs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .genotype import (
    Brain,
    BrainVocabulary,
    Connection,
    Effector,
    Genotype,
    JointType,
    Link,
    Neuron,
    Node,
    Sensor,
    Shape,
    UnitRef,
    random_connection,
    random_neuron,
    random_segment,
    random_sensor_set,
)


@dataclass
class MutationConfig:
    # weights / biases
    weight_rate: float = 0.25  #: probability that each weight or bias is perturbed
    weight_sigma: float = 0.4
    weight_reset_rate: float = 0.02  #: probability that a perturbed weight is redrawn from scratch
    # segment parameters
    dims_rate: float = 0.2
    dims_sigma: float = 0.2  #: log-normal multiplicative noise on relative dimensions
    shape_rate: float = 0.03
    # connection parameters
    position_rate: float = 0.2
    position_sigma: float = 0.25
    orientation_rate: float = 0.2
    orientation_sigma: float = 0.35
    scale_rate: float = 0.2
    scale_sigma: float = 0.15
    axis_rate: float = 0.15
    joint_type_rate: float = 0.05
    joint_limit_rate: float = 0.1
    recursive_limit_rate: float = 0.05
    # graph structure
    add_node_rate: float = 0.08
    remove_node_rate: float = 0.05
    add_connection_rate: float = 0.1
    remove_connection_rate: float = 0.08
    max_nodes: int = 8
    max_connections_per_node: int = 4
    # neural structure
    add_unit_rate: float = 0.1
    remove_unit_rate: float = 0.06
    add_link_rate: float = 0.15
    remove_link_rate: float = 0.1
    max_units_per_brain: int = 12
    # limits
    min_scale: float = 0.25
    max_scale: float = 1.2
    max_recursive_limit: int = 3
    # vocabulary of the brain model (sensor sources, neuron functions, motor modes)
    vocab: BrainVocabulary = field(default_factory=BrainVocabulary)
    motor_rate: float = 0.05  #: probability that a connection's motor mode is redrawn
    mirror_toggle_rate: float = 0.05  #: probability that a connection's mirror flag flips (when the vocabulary allows mirroring)
    func_rate: float = 0.05  #: probability that a neuron's transfer function is redrawn
    oscillator_rate: float = 0.2  #: probability that an oscillator's frequency / phase is perturbed


# --------------------------------------------------------------------------- #
# Weights only (conventional evolution)
# --------------------------------------------------------------------------- #


def mutate_weights(g: Genotype, rng: np.random.Generator, config: Optional[MutationConfig] = None) -> Genotype:
    """Perturb link weights and unit biases; the topology is untouched."""
    config = config or MutationConfig()
    child = g.copy()
    for _, brain in child.brains():
        for link in brain.links:
            if rng.random() < config.weight_rate:
                if rng.random() < config.weight_reset_rate:
                    link.weight = float(rng.normal(0.0, 1.0))
                else:
                    link.weight += float(rng.normal(0.0, config.weight_sigma))
        for u in brain.units:
            if u.kind != "sensor" and rng.random() < config.weight_rate:
                u.bias += float(rng.normal(0.0, config.weight_sigma))
            elif u.kind == "sensor" and u.source == "oscillator" and rng.random() < config.oscillator_rate:
                u.freq = float(np.clip(u.freq * math.exp(rng.normal(0, 0.2)), 0.1, 5.0))
                u.phase = float((u.phase + rng.normal(0, 0.4)) % (2 * math.pi))
    return child


def crossover_weights(a: Genotype, b: Genotype, rng: np.random.Generator) -> Genotype:
    """Uniform crossover of weights and biases between two structurally identical genotypes.

    Falls back to a copy of ``a`` when the network topologies differ.
    """
    child = a.copy()
    brains_a = list(child.brains())
    brains_b = list(b.brains())
    if len(brains_a) != len(brains_b):
        return child
    for (_, ba), (_, bb) in zip(brains_a, brains_b):
        if len(ba.links) != len(bb.links) or len(ba.units) != len(bb.units):
            return a.copy()
    for (_, ba), (_, bb) in zip(brains_a, brains_b):
        for la, lb in zip(ba.links, bb.links):
            if rng.random() < 0.5:
                la.weight = lb.weight
        for ua, ub in zip(ba.units, bb.units):
            if ua.kind != "sensor" and ub.kind != "sensor" and rng.random() < 0.5:
                ua.bias = ub.bias
    return child


# --------------------------------------------------------------------------- #
# Holistic mutation
# --------------------------------------------------------------------------- #


def mutate(g: Genotype, rng: np.random.Generator, config: Optional[MutationConfig] = None) -> Genotype:
    """Holistic mutation: body, brain topology and weights may all change."""
    config = config or MutationConfig()
    child = mutate_weights(g, rng, config)
    _mutate_segments(child, rng, config)
    _mutate_connections(child, rng, config)
    _mutate_graph(child, rng, config)
    _mutate_neural(child, rng, config)
    problems = child.validate()
    if problems:  # pragma: no cover - defensive; operators are meant to preserve validity
        raise RuntimeError("mutation produced an invalid genotype: " + "; ".join(problems))
    return child


def _mutate_segments(g: Genotype, rng, cfg: MutationConfig) -> None:
    for node in g.nodes:
        seg = node.segment
        if rng.random() < cfg.shape_rate:
            new = random_segment(rng)
            seg.shape, seg.dims = new.shape, new.dims
        elif rng.random() < cfg.dims_rate:
            seg.dims = tuple(float(np.clip(d * math.exp(rng.normal(0, cfg.dims_sigma)), 0.05, 5.0)) for d in seg.dims)


def _mutate_connections(g: Genotype, rng, cfg: MutationConfig) -> None:
    for node in g.nodes:
        for c in node.connections:
            if rng.random() < cfg.position_rate:
                c.position = tuple(float(x) for x in np.clip(np.asarray(c.position) + rng.normal(0, cfg.position_sigma, 3), -1, 1))
            if rng.random() < cfg.orientation_rate:
                c.orientation = tuple(float(x) for x in np.asarray(c.orientation) + rng.normal(0, cfg.orientation_sigma, 3))
            if rng.random() < cfg.scale_rate:
                c.scale = float(np.clip(c.scale * math.exp(rng.normal(0, cfg.scale_sigma)), cfg.min_scale, cfg.max_scale))
            if rng.random() < cfg.axis_rate:
                axis = np.asarray(c.axis) + rng.normal(0, 0.5, 3)
                if np.linalg.norm(axis) > 1e-6:
                    c.axis = tuple(float(x) for x in axis / np.linalg.norm(axis))
            if rng.random() < cfg.joint_type_rate:
                c.joint_type = JointType(int(rng.integers(0, 4)))
            if rng.random() < cfg.joint_limit_rate:
                if c.joint_limit is None or rng.random() < 0.15:
                    c.joint_limit = None if c.joint_limit is not None else float(rng.uniform(0.3, math.pi / 2))
                else:
                    c.joint_limit = float(np.clip(c.joint_limit * math.exp(rng.normal(0, 0.3)), 0.05, math.pi))
            if rng.random() < cfg.recursive_limit_rate:
                c.recursive_limit = int(np.clip(c.recursive_limit + rng.choice([-1, 1]), 1, cfg.max_recursive_limit))
            if len(cfg.vocab.motor_modes) > 1 and rng.random() < cfg.motor_rate:
                c.motor = str(rng.choice(list(cfg.vocab.motor_modes)))
            if cfg.vocab.mirror_rate > 0 and rng.random() < cfg.mirror_toggle_rate:
                c.mirror = not c.mirror


def _mutate_graph(g: Genotype, rng, cfg: MutationConfig) -> None:
    # Add a node, attached to a random existing node.
    if len(g.nodes) < cfg.max_nodes and rng.random() < cfg.add_node_rate:
        seg = random_segment(rng)
        if rng.random() < 0.5:
            seg.brain.units = [Effector(int(rng.integers(0, 3)), 0.0)]
        g.nodes.append(Node(seg))
        parent = int(rng.integers(0, len(g.nodes) - 1))
        conn = random_connection(rng, len(g.nodes), vocab=cfg.vocab)
        conn.child = len(g.nodes) - 1
        g.nodes[parent].connections.append(conn)
    # Remove a non-root node.
    if len(g.nodes) > 1 and rng.random() < cfg.remove_node_rate:
        candidates = [i for i in range(len(g.nodes)) if i != g.root]
        remove_node(g, int(rng.choice(candidates)))
    # Add / remove connections.
    for node in g.nodes:
        if len(node.connections) < cfg.max_connections_per_node and rng.random() < cfg.add_connection_rate:
            node.connections.append(random_connection(rng, len(g.nodes), vocab=cfg.vocab))
        if node.connections and rng.random() < cfg.remove_connection_rate:
            node.connections.pop(int(rng.integers(0, len(node.connections))))


def remove_node(g: Genotype, n: int) -> None:
    """Delete node ``n`` (never the root), fixing every index that referred past it."""
    if n == g.root:
        raise ValueError("cannot remove the root node")
    del g.nodes[n]
    if g.root > n:
        g.root -= 1

    def remap(i: Optional[int]) -> Optional[int]:
        return None if i is None else (i - 1 if i > n else i)

    for node in g.nodes:
        node.connections = [c for c in node.connections if c.child != n]
        for c in node.connections:
            c.child = remap(c.child)
    for owner, brain in g.brains():
        brain.links = [l for l in brain.links if l.src.node != n and l.dst.node != n]
        for l in brain.links:
            l.src = UnitRef(remap(l.src.node), l.src.index)
            l.dst = UnitRef(remap(l.dst.node), l.dst.index)


def remove_unit(g: Genotype, owner: Optional[int], k: int) -> None:
    """Delete unit ``k`` of the brain owned by ``owner`` and every link touching it."""
    brain = g.brain_of(owner)
    del brain.units[k]

    def touches(ref: UnitRef) -> bool:
        return ref.node == owner and ref.index == k

    def remap(ref: UnitRef) -> UnitRef:
        if ref.node == owner and ref.index > k:
            return UnitRef(ref.node, ref.index - 1)
        return ref

    for _, b in g.brains():
        b.links = [l for l in b.links if not touches(l.src) and not touches(l.dst)]
        for l in b.links:
            l.src, l.dst = remap(l.src), remap(l.dst)


def _random_unit(rng, owner: Optional[int], vocab: BrainVocabulary):
    if owner is None:
        return [random_neuron(rng, vocab)]
    r = rng.random()
    if r < 0.3:
        return [random_neuron(rng, vocab)]
    if r < 0.6:
        return [Effector(int(rng.integers(0, 3)), float(rng.normal(0, 0.5)))]
    return random_sensor_set(rng, vocab)


def _link_sources(g: Genotype, owner: Optional[int]) -> list[UnitRef]:
    brain = g.brain_of(owner)
    sources = [UnitRef(owner, i) for i in range(len(brain.units))]
    if owner is None:
        for i, node in enumerate(g.nodes):
            sources += [UnitRef(i, k) for k in range(len(node.segment.brain.units))]
    elif g.global_brain is not None:
        sources += [UnitRef(None, i) for i in range(len(g.global_brain.units))]
    return sources


def _mutate_neural(g: Genotype, rng, cfg: MutationConfig) -> None:
    # Occasionally create a global brain where there is none.
    if g.global_brain is None and rng.random() < cfg.add_unit_rate / 2:
        g.global_brain = Brain()
    for owner, brain in list(g.brains()):
        if len(brain.units) < cfg.max_units_per_brain and rng.random() < cfg.add_unit_rate:
            brain.units.extend(_random_unit(rng, owner, cfg.vocab))
        if brain.units and rng.random() < cfg.remove_unit_rate:
            remove_unit(g, owner, int(rng.integers(0, len(brain.units))))
        if len(cfg.vocab.neuron_funcs) > 1:
            for u in brain.units:
                if u.kind == "neuron" and rng.random() < cfg.func_rate:
                    u.func = str(rng.choice(list(cfg.vocab.neuron_funcs)))
    for owner, brain in list(g.brains()):
        targets = [k for k, u in enumerate(brain.units) if u.kind != "sensor"]
        if targets and rng.random() < cfg.add_link_rate:
            sources = _link_sources(g, owner)
            if sources:
                src = sources[int(rng.integers(0, len(sources)))]
                dst = UnitRef(owner, int(rng.choice(targets)))
                brain.links.append(Link(src, dst, float(rng.normal(0, 1.0))))
        if brain.links and rng.random() < cfg.remove_link_rate:
            brain.links.pop(int(rng.integers(0, len(brain.links))))


# --------------------------------------------------------------------------- #
# Controller-only structural mutation (fixed body, evolving brain topology)
# --------------------------------------------------------------------------- #


def mutate_controller(g: Genotype, rng: np.random.Generator, config: Optional[MutationConfig] = None) -> Genotype:
    """Mutate weights *and* controller topology, leaving the body untouched.

    The body here means everything a designer fixes: segments, connections,
    and the sensors and effectors mounted on them.  What may change is the
    global Brain's set of Neurons (added, removed, re-typed), any link, and
    every weight and bias.  Used for the conventional population when the
    experiment isolates the *body* as the only difference between the two
    regimes.
    """
    config = config or MutationConfig()
    child = mutate_weights(g, rng, config)
    if child.global_brain is None:
        child.global_brain = Brain()
    gb = child.global_brain
    if len(gb.units) < config.max_units_per_brain and rng.random() < config.add_unit_rate:
        gb.units.append(random_neuron(rng, config.vocab))
    if gb.units and rng.random() < config.remove_unit_rate:
        remove_unit(child, None, int(rng.integers(0, len(gb.units))))
    if len(config.vocab.neuron_funcs) > 1:
        for u in gb.units:
            if rng.random() < config.func_rate:
                u.func = str(rng.choice(list(config.vocab.neuron_funcs)))
    for owner, brain in list(child.brains()):
        targets = [k for k, u in enumerate(brain.units) if u.kind != "sensor"]
        if targets and rng.random() < config.add_link_rate:
            sources = _link_sources(child, owner)
            if sources:
                src = sources[int(rng.integers(0, len(sources)))]
                brain.links.append(Link(src, UnitRef(owner, int(rng.choice(targets))), float(rng.normal(0, 1.0))))
        if brain.links and rng.random() < config.remove_link_rate:
            brain.links.pop(int(rng.integers(0, len(brain.links))))
    problems = child.validate()
    if problems:  # pragma: no cover - defensive
        raise RuntimeError("controller mutation produced an invalid genotype: " + "; ".join(problems))
    return child


def body_signature(g: Genotype) -> tuple:
    """Everything a designer fixes: segments, connections, and the sensors and effectors on each node."""
    sig = [g.root]
    for node in g.nodes:
        seg = node.segment
        sig.append((int(seg.shape), tuple(round(d, 9) for d in seg.dims)))
        sig.append(tuple((c.child, tuple(c.position), tuple(c.orientation), round(c.scale, 9), int(c.joint_type), c.recursive_limit, tuple(c.axis), c.joint_limit, c.motor, c.mirror) for c in node.connections))
        sig.append(tuple((u.kind, getattr(u, "source", None), getattr(u, "axis", None), getattr(u, "dof", None)) for u in seg.brain.units if u.kind != "neuron"))
    return tuple(sig)


def crossover_controller(a: Genotype, b: Genotype, rng: np.random.Generator) -> Genotype:
    """Crossover for a shared body with differing controller topologies: the
    child takes ``a``'s body and local brains and ``b``'s global Brain, keeping
    only links that still resolve."""
    child = a.copy()
    if b.global_brain is not None and rng.random() < 0.5:
        child.global_brain = b.global_brain.copy()
        for node_b, node_c in zip(b.nodes, child.nodes):
            # local links from the global brain travel with it
            keep = [l for l in node_c.segment.brain.links if l.src.node is not None]
            keep += [Link(l.src, l.dst, l.weight) for l in node_b.segment.brain.links if l.src.node is None]
            node_c.segment.brain.links = keep
        repair_links(child)
    return child


# --------------------------------------------------------------------------- #
# Holistic crossover
# --------------------------------------------------------------------------- #


def crossover(a: Genotype, b: Genotype, rng: np.random.Generator) -> Genotype:
    """Sims-style crossover: the node lists are aligned and the child takes a
    prefix of ``a``'s nodes followed by the remainder of ``b``'s.  References
    that no longer resolve are wrapped modulo the new node count; links whose
    unit index no longer exists are dropped."""
    k = int(rng.integers(1, len(a.nodes) + 1))
    nodes = [Node.from_dict(n.to_dict()) for n in a.nodes[:k]] + [Node.from_dict(n.to_dict()) for n in b.nodes[k:]]
    n = len(nodes)
    gb_src = a if (b.global_brain is None or (a.global_brain is not None and rng.random() < 0.5)) else b
    gb = None if gb_src.global_brain is None else gb_src.global_brain.copy()
    child = Genotype(nodes=nodes, root=a.root if a.root < n else 0, global_brain=gb, name="")
    for node in child.nodes:
        for c in node.connections:
            c.child %= n
    repair_links(child)
    if not child.is_valid():  # pragma: no cover - defensive
        return a.copy()
    return child


def repair_links(g: Genotype) -> None:
    """Drop links whose endpoints do not resolve after a structural change."""
    n = len(g.nodes)

    def ok(ref: UnitRef) -> bool:
        if ref.node is not None and not 0 <= ref.node < n:
            return False
        brain = g.brain_of(ref.node)
        return brain is not None and 0 <= ref.index < len(brain.units)

    for owner, brain in g.brains():
        kept = []
        for l in brain.links:
            if l.dst.node != owner or not ok(l.src) or not ok(l.dst):
                continue
            if owner is not None and l.src.node not in (owner, None):
                continue
            if g.unit(l.dst).kind == "sensor":
                continue
            kept.append(l)
        brain.links = kept
    if g.global_brain is not None:
        g.global_brain.units = [u for u in g.global_brain.units if u.kind == "neuron"]
        repair_links_after_global_prune(g)


def repair_links_after_global_prune(g: Genotype) -> None:
    n_global = len(g.global_brain.units)
    for _, brain in g.brains():
        brain.links = [l for l in brain.links if not (l.src.node is None and l.src.index >= n_global) and not (l.dst.node is None and l.dst.index >= n_global)]
