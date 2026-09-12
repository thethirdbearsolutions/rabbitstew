import numpy as np

from rabbitstew.genetics import MutationConfig, mutate, remove_node
from rabbitstew.genotype import Brain, BrainVocabulary, Connection, Effector, Genotype, Link, Neuron, Node, Segment, Sensor, Shape, UnitRef, random_genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import SynthesisConfig, synthesize


def chain():
    """root (node 0) with a sensor, child node 1 with an effector that reads the root's sensor."""
    root = Node(Segment(Shape.BOX, (0.3, 0.2, 0.1), brain=Brain(units=[Sensor("contact", 0)])), connections=[Connection(child=1, position=(1.0, 0.0, 0.0), recursive_limit=2)])
    leaf = Node(Segment(Shape.BOX, (0.2, 0.1, 0.1), brain=Brain(units=[Effector(0, 0.0)], links=[Link(UnitRef(0, 0), UnitRef(1, 0), 2.0)])))
    return Genotype(nodes=[root, leaf], root=0)


def test_neighbour_link_validates_and_resolves_to_the_actual_parent_part():
    g = chain()
    assert g.validate() == []
    assert g.neighbours(1) == [0] and g.neighbours(0) == [1]
    ph = synthesize(g, SynthesisConfig())
    cross = [(s, d) for s, d, _ in ph.links if ph.units[s].part != ph.units[d].part and ph.units[s].part is not None and ph.units[d].part is not None]
    assert cross, "the leaf's effector must read the root's sensor across parts"
    for s, d in cross:
        assert ph.parts[ph.units[d].part].parent == ph.units[s].part  # source is the destination part's own parent


def test_non_neighbour_source_is_rejected():
    g = chain()
    g.nodes.append(Node(Segment(Shape.SPHERE, (0.1,), brain=Brain(units=[Neuron(0.0)]))))
    g.nodes[1].segment.brain.links.append(Link(UnitRef(2, 0), UnitRef(1, 0), 1.0))  # node 2 is not connected to node 1
    assert any("neighbouring" in p for p in g.validate())


def test_random_and_mutated_genotypes_use_neighbour_links_only_when_allowed():
    rng = np.random.default_rng(0)
    on = BrainVocabulary(neighbour_links=True)
    off = BrainVocabulary()

    def cross_links(g):
        return sum(1 for owner, b in g.brains() if owner is not None for l in b.links if l.src.node not in (owner, None))

    assert sum(cross_links(random_genotype(rng, n_nodes=3, vocab=off)) for _ in range(20)) == 0
    assert sum(cross_links(random_genotype(rng, n_nodes=3, vocab=on)) for _ in range(20)) > 0
    g = random_genotype(rng, n_nodes=3, vocab=on)
    cfg = MutationConfig(vocab=on)
    for _ in range(30):
        g = mutate(g, rng, cfg)
        assert g.validate() == [], g.validate()


def test_removing_a_node_prunes_orphaned_neighbour_links():
    g = chain()
    g.nodes.append(Node(Segment(Shape.SPHERE, (0.1,), brain=Brain(units=[Neuron(0.0)]))))
    g.nodes[1].connections.append(Connection(child=2, position=(1.0, 0.0, 0.0)))
    g.nodes[2].segment.brain.links.append(Link(UnitRef(1, 0), UnitRef(2, 0), 1.0))  # node 2 reads node 1
    assert g.validate() == []
    remove_node(g, 1)
    assert g.validate() == []
    assert all(l.src.node in (owner, None) or l.src.node in g.neighbours(owner) for owner, b in g.brains() if owner is not None for l in b.links)


def test_vocabulary_roundtrip_keeps_the_flag():
    v = BrainVocabulary.from_dict(BrainVocabulary(neighbour_links=True).to_dict())
    assert v.neighbour_links is True


def test_crossover_keeps_valid_neighbour_links():
    from rabbitstew.genetics import crossover

    rng = np.random.default_rng(1)
    on = BrainVocabulary(neighbour_links=True)
    parents = [random_genotype(rng, n_nodes=3, vocab=on) for _ in range(10)]
    kept = 0
    for _ in range(40):
        a, b = parents[int(rng.integers(0, 10))], parents[int(rng.integers(0, 10))]
        c = crossover(a, b, rng)
        assert c.validate() == [], c.validate()
        kept += sum(1 for owner, br in c.brains() if owner is not None for l in br.links if l.src.node not in (owner, None))
    assert kept > 0
