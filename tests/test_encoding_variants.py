import numpy as np

from rabbitstew.evolution import HOLISTIC, BoutRunner, EvolutionConfig, Experiment, descriptor_cell, evaluate, initial_population, reproduce, update_archive
from rabbitstew.genetics import MutationConfig, body_signature, mutate
from rabbitstew.genotype import BrainVocabulary, Connection, Genotype, JointType, Node, Segment, Shape, random_genotype
from rabbitstew.simulation import SimConfig, Simulation
from rabbitstew.synthesis import SynthesisConfig, mirror_connection, synthesize


def test_mirrored_connection_makes_a_reflected_twin():
    body = Node(Segment(Shape.BOX, (1.0, 1.0, 1.0)), [Connection(child=1, position=(0.5, 1.0, -0.3), orientation=(0.3, 0.1, -0.2), axis=(0.2, 0.9, 0.1), scale=0.5, mirror=True)])
    limb = Node(Segment(Shape.CYLINDER, (0.3, 1.0)))
    g = Genotype(nodes=[body, limb])
    ph = synthesize(g, SynthesisConfig(size_ratio_limit=10))
    assert len(ph.parts) == 3
    a, b = ph.parts[1], ph.parts[2]
    assert not a.mirrored and b.mirrored
    assert np.allclose(a.attach_pos * np.array([1, -1, 1]), b.attach_pos)
    assert np.allclose(a.joint_axis * np.array([1, -1, 1]), b.joint_axis)
    assert a.node == b.node == 1 and a.parent == b.parent == 0
    m = mirror_connection(body.connections[0])
    assert m.position[1] == -1.0 and m.orientation == (-0.3, 0.1, 0.2) and not m.mirror
    # the twin's geometry is the mirror image: settle both and compare geom centres
    sim = Simulation([g], SimConfig())
    idx = sim.robots[0]
    pa, pb = sim.data.geom_xpos[idx.geoms[1]], sim.data.geom_xpos[idx.geoms[2]]
    root = sim.data.geom_xpos[idx.geoms[0]]
    assert np.allclose((pa - root) * np.array([1, -1, 1]), pb - root, atol=1e-6)
    assert Genotype.from_json(g.to_json()).nodes[0].connections[0].mirror is True


def test_mirror_rate_and_toggle(rng):
    vocab = BrainVocabulary.rich()
    vocab.mirror_rate = 1.0
    g = random_genotype(rng, vocab=vocab)
    assert all(c.mirror for n in g.nodes for c in n.connections)
    cfg = MutationConfig(vocab=vocab, mirror_toggle_rate=1.0)
    g2 = mutate(g, rng, cfg)
    assert all(not c.mirror for n in g2.nodes for c in n.connections)  # every flag flipped
    assert body_signature(g) != body_signature(g2)
    for _ in range(20):
        g2 = mutate(g2, rng, MutationConfig(vocab=vocab))
        assert g2.is_valid()
        synthesize(g2)


def test_archive_keeps_structurally_distinct_elites(rng):
    cfg = EvolutionConfig(population_size=6, elites=1, archive=True, sim=SimConfig(duration=0.3))
    pop = initial_population(HOLISTIC, cfg, rng)
    evaluate(pop, BoutRunner(cfg.sim), rng, cfg)
    update_archive(pop, cfg.sim)
    cells = {descriptor_cell(m, cfg.sim) for m in pop.members}
    assert set(pop.archive) == cells and 1 <= len(pop.archive) <= 6
    new = reproduce(pop, rng, cfg)
    assert new.archive == pop.archive and len(new.members) == 6
    assert all(m.is_valid() for m in new.members)


def test_experiment_with_mirror_and_archive(tmp_path):
    cfg = EvolutionConfig(population_size=4, generations=2, elites=1, champion_interval=0, seed=5, mirror=True, archive=True, sim=SimConfig(duration=0.3))
    assert cfg.mutation.vocab.mirror_rate == 0.3
    out = Experiment(cfg, out_dir=str(tmp_path), log=None).run()
    assert all(e["archive_cells"] >= 1 for e in out["history"] if e["population"] == HOLISTIC)
    assert all(e["archive_cells"] is None for e in out["history"] if e["population"] != HOLISTIC)
    resumed = Experiment.resume(str(tmp_path), generations=3, log=None)
    assert resumed.populations[HOLISTIC].archive
    resumed.run()


def test_fixed_body_from_a_genotype_file(tmp_path, rng):
    from rabbitstew.evolution import CONVENTIONAL
    from rabbitstew.genetics import body_signature

    g = random_genotype(rng, vocab=BrainVocabulary.rich())
    path = tmp_path / "body.json"
    g.save(path)
    cfg = EvolutionConfig(population_size=3, fixed_body=str(path), brain_model="rich", conventional_topology=True, sim=SimConfig(duration=0.2))
    pop = initial_population(CONVENTIONAL, cfg, rng)
    assert all(body_signature(m) == body_signature(g) for m in pop.members)
    w0 = [l.weight for _, b in g.brains() for l in b.links]
    w1 = [l.weight for _, b in pop.members[0].brains() for l in b.links]
    assert w0 != w1 or not w0
    evaluate(pop, BoutRunner(cfg.sim), rng, cfg)
    new = reproduce(pop, rng, cfg)
    assert all(body_signature(m) == body_signature(g) for m in new.members)
