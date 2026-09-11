import math

import numpy as np

from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Link, Neuron, Node, Segment, Sensor, Shape, UnitRef, random_genotype
from rabbitstew.synthesis import Part, SynthesisConfig, outward_normal, surface_point, synthesize


def chain(n_nodes: int, recursive_limit: int = 1) -> Genotype:
    nodes = [Node(Segment(Shape.BOX, (1.0, 1.0, 1.0))) for _ in range(n_nodes)]
    for i in range(n_nodes - 1):
        nodes[i].connections.append(Connection(child=i + 1, recursive_limit=recursive_limit))
    return Genotype(nodes=nodes)


def test_size_ratio_limit_caps_parts():
    g = chain(4, recursive_limit=5)
    g.nodes[3].connections.append(Connection(child=0, recursive_limit=5))  # circuit back to the root
    for ratio in (0.5, 1.0, 2.0):
        ph = synthesize(g, SynthesisConfig(size_ratio_limit=ratio))
        assert len(ph.parts) == math.ceil(ratio * 4)
        assert ph.truncated


def test_recursive_limit_counts_instances_on_path():
    g = Genotype(nodes=[Node(Segment(Shape.SPHERE, (1.0,)))])
    g.nodes[0].connections.append(Connection(child=0, recursive_limit=3, scale=0.5))
    ph = synthesize(g, SynthesisConfig(size_ratio_limit=50))
    assert len(ph.parts) == 3
    assert [p.parent for p in ph.parts] == [None, 0, 1]
    assert not ph.truncated


def test_breadth_first_order():
    g = Genotype(nodes=[Node(Segment(Shape.SPHERE, (1.0,))), Node(Segment(Shape.SPHERE, (1.0,))), Node(Segment(Shape.SPHERE, (1.0,)))])
    g.nodes[0].connections = [Connection(child=1, position=(1, 0, 0)), Connection(child=2, position=(-1, 0, 0))]
    g.nodes[1].connections = [Connection(child=2, position=(0, 1, 0))]
    ph = synthesize(g, SynthesisConfig(size_ratio_limit=1.0))  # 3 parts allowed
    assert [p.node for p in ph.parts] == [0, 1, 2]  # both children of the root before any grandchild
    assert ph.parts[2].parent == 0


def test_sizes_scale_along_the_path():
    g = chain(3)
    g.nodes[0].connections[0].scale = 0.5
    g.nodes[1].connections[0].scale = 0.5
    cfg = SynthesisConfig(root_size=0.4, min_size=0.01)
    ph = synthesize(g, cfg)
    assert [round(p.size, 6) for p in ph.parts] == [0.4, 0.2, 0.1]
    assert math.isclose(ph.parts[0].volume(), 0.4 ** 3, rel_tol=1e-9)
    assert math.isclose(ph.parts[0].mass, 0.4 ** 3 * cfg.density, rel_tol=1e-9)


def test_mass_budget_scales_every_part():
    g = chain(3)
    ph = synthesize(g, SynthesisConfig(root_size=0.4, min_size=0.01))
    heavy = ph.total_mass()
    assert heavy > 20
    ph2 = synthesize(g, SynthesisConfig(root_size=0.4, min_size=0.01, mass_budget=15.0))
    assert math.isclose(ph2.total_mass(), 15.0, rel_tol=1e-9)
    assert all(math.isclose(a.mass / b.mass, ph2.mass_scaled) for a, b in zip(ph2.parts, ph.parts))
    assert [p.dims for p in ph2.parts] == [p.dims for p in ph.parts]  # geometry is untouched
    light = synthesize(g, SynthesisConfig(root_size=0.1, mass_budget=15.0))
    assert light.mass_scaled == 1.0 and light.total_mass() < 15.0


def test_surface_points_lie_on_surface():
    box = (2.0, 1.0, 0.5)
    p = surface_point(Shape.BOX, box, (0.2, -1.0, 0.3))
    assert np.isclose(p[1], -0.5) and np.isclose(p[0], 0.2) and np.isclose(p[2], 0.075)
    assert np.allclose(outward_normal(Shape.BOX, box, p), (0, -1, 0))
    s = surface_point(Shape.SPHERE, (0.3,), (1, 1, 0))
    assert np.isclose(np.linalg.norm(s), 0.3)
    c = surface_point(Shape.CYLINDER, (0.2, 1.0), (0.1, 0.5, 0.5))  # curved side
    assert np.isclose(np.linalg.norm(c[1:]), 0.2) and np.isclose(c[0], 0.05)
    cap = surface_point(Shape.CYLINDER, (0.2, 1.0), (-1.0, 0.1, 0.0))  # end cap
    assert np.isclose(cap[0], -0.5)
    assert np.allclose(outward_normal(Shape.CYLINDER, (0.2, 1.0), cap), (-1, 0, 0))


def test_brains_are_instantiated_per_part_and_global_links_fan_in():
    seg = Segment(Shape.SPHERE, (1.0,), Brain(units=[Sensor("contact"), Effector()]))
    seg.brain.links.append(Link(UnitRef(0, 0), UnitRef(0, 1), 0.5))
    seg.brain.links.append(Link(UnitRef(None, 0), UnitRef(0, 1), 0.25))
    g = Genotype(nodes=[Node(seg, [Connection(child=0, recursive_limit=3, scale=0.6)])], global_brain=Brain(units=[Neuron()]))
    g.global_brain.links.append(Link(UnitRef(0, 0), UnitRef(None, 0), 1.0))
    ph = synthesize(g, SynthesisConfig(size_ratio_limit=10))
    assert len(ph.parts) == 3
    assert len(ph.units) == 3 * 2 + 1
    # 2 local links per instance + one global link per instance
    assert len(ph.links) == 3 * 2 + 3
    assert ph.units_of_part(None) == [6]


def test_invalid_genotype_is_rejected():
    g = Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=[Neuron()])))])
    g.nodes[0].connections.append(Connection(child=3))
    try:
        synthesize(g)
    except ValueError as e:
        assert "invalid genotype" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_random_genotypes_synthesize(rng):
    for _ in range(30):
        ph = synthesize(random_genotype(rng))
        assert 1 <= len(ph.parts) <= SynthesisConfig().max_parts(len(ph.genotype.nodes))
        assert all(isinstance(p, Part) for p in ph.parts)
        assert ph.parts[0].parent is None
