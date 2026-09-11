import math

import numpy as np
import pytest

from rabbitstew.genotype import (
    Brain,
    Connection,
    Effector,
    Genotype,
    JointType,
    Link,
    Neuron,
    Node,
    Segment,
    Sensor,
    Shape,
    UnitRef,
    random_genotype,
)


def test_random_genotypes_are_valid(rng):
    for _ in range(50):
        g = random_genotype(rng)
        assert g.validate() == []
        assert 2 <= len(g.nodes) <= 5


def test_json_roundtrip(rng, tmp_path):
    g = random_genotype(rng)
    g2 = Genotype.from_json(g.to_json())
    assert g2.to_dict() == g.to_dict()
    path = tmp_path / "g.json"
    g.save(path)
    assert Genotype.load(path).to_dict() == g.to_dict()


def test_copy_is_independent(rng):
    g = random_genotype(rng)
    c = g.copy()
    c.nodes[0].segment.dims = (9.0,) * len(c.nodes[0].segment.dims)
    assert g.nodes[0].segment.dims != c.nodes[0].segment.dims


def test_normalized_dims_have_unit_volume():
    for seg in [Segment(Shape.BOX, (2.0, 0.5, 3.0)), Segment(Shape.SPHERE, (0.7,)), Segment(Shape.CYLINDER, (0.2, 3.0))]:
        assert math.isclose(seg.volume(seg.normalized_dims()), 1.0, rel_tol=1e-9)


def test_validation_catches_bad_references():
    g = Genotype(nodes=[Node(Segment(Shape.SPHERE, (1.0,)))])
    g.nodes[0].connections.append(Connection(child=5))
    assert any("out of range" in p for p in g.validate())

    g = Genotype(nodes=[Node(Segment(Shape.SPHERE, (1.0,), Brain(units=[Sensor("contact"), Neuron()])))])
    g.nodes[0].segment.brain.links.append(Link(UnitRef(0, 1), UnitRef(0, 0), 1.0))  # into a sensor
    assert any("sensors cannot receive" in p for p in g.validate())

    g = Genotype(nodes=[Node(Segment(Shape.SPHERE, (1.0,)))], global_brain=Brain(units=[Effector()]))
    assert any("only Neurons" in p for p in g.validate())

    g = Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0)))])
    assert any("needs 3 dims" in p for p in g.validate())


def test_local_links_cannot_cross_nodes():
    n0 = Node(Segment(Shape.SPHERE, (1.0,), Brain(units=[Neuron()])))
    n1 = Node(Segment(Shape.SPHERE, (1.0,), Brain(units=[Neuron()])))
    g = Genotype(nodes=[n0, n1])
    n1.segment.brain.links.append(Link(UnitRef(0, 0), UnitRef(1, 0), 1.0))
    assert any("local or global" in p for p in g.validate())


def test_joint_type_dofs():
    assert JointType.HINGE.ndof == 1 and JointType.BALL.ndof == 3 and JointType.SLIDER.ndof == 1 and JointType.FIXED.ndof == 0
