import json

import numpy as np

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, BoutRunner, EvolutionConfig, Experiment, Population, champion_bouts, evaluate, initial_population, reproduce
from rabbitstew.fixed import is_same_morphology, pioneer_genotype
from rabbitstew.genetics import MutationConfig, crossover, crossover_weights, mutate, mutate_weights, remove_node, remove_unit
from rabbitstew.genotype import Brain, Connection, Genotype, Link, Neuron, Node, Segment, Sensor, Shape, UnitRef, random_genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize


def test_mutate_weights_keeps_morphology(rng):
    p = pioneer_genotype(rng)
    c = mutate_weights(p, rng, MutationConfig(weight_rate=1.0))
    assert is_same_morphology(p, c)
    assert c.is_valid()
    assert any(a.weight != b.weight for (_, ba), (_, bb) in zip(p.brains(), c.brains()) for a, b in zip(ba.links, bb.links))
    assert p.to_dict() != c.to_dict()


def test_crossover_weights_mixes_parents(rng):
    a, b = pioneer_genotype(rng), pioneer_genotype(rng)
    c = crossover_weights(a, b, rng)
    assert is_same_morphology(a, c)
    wa = [l.weight for _, br in a.brains() for l in br.links]
    wb = [l.weight for _, br in b.brains() for l in br.links]
    wc = [l.weight for _, br in c.brains() for l in br.links]
    assert all(w in (x, y) for w, x, y in zip(wc, wa, wb))
    assert wc != wa and wc != wb


def test_holistic_operators_preserve_validity(rng):
    pop = [random_genotype(rng) for _ in range(10)]
    aggressive = MutationConfig(add_node_rate=0.5, remove_node_rate=0.4, add_connection_rate=0.5, remove_connection_rate=0.4, add_unit_rate=0.5, remove_unit_rate=0.4, add_link_rate=0.6, remove_link_rate=0.4, shape_rate=0.3, joint_type_rate=0.3)
    for _ in range(200):
        a, b = pop[rng.integers(10)], pop[rng.integers(10)]
        c = mutate(crossover(a, b, rng), rng, aggressive)
        assert c.validate() == []
        synthesize(c)
        pop[rng.integers(10)] = c


def test_mutation_changes_morphology_eventually(rng):
    g = random_genotype(rng)
    changed = False
    for _ in range(50):
        g2 = mutate(g, rng)
        if not is_same_morphology(g, g2):
            changed = True
            break
    assert changed


def test_remove_node_fixes_indices():
    nodes = [Node(Segment(Shape.SPHERE, (1.0,), Brain(units=[Neuron()]))) for _ in range(3)]
    nodes[0].connections = [Connection(child=1), Connection(child=2)]
    nodes[2].connections = [Connection(child=1)]
    g = Genotype(nodes=nodes, root=0, global_brain=Brain(units=[Neuron()]))
    g.global_brain.links = [Link(UnitRef(1, 0), UnitRef(None, 0), 1.0), Link(UnitRef(2, 0), UnitRef(None, 0), 2.0)]
    remove_node(g, 1)
    assert len(g.nodes) == 2
    assert [c.child for c in g.nodes[0].connections] == [1]
    assert g.nodes[1].connections == []
    assert [(l.src.node, l.weight) for l in g.global_brain.links] == [(1, 2.0)]
    assert g.is_valid()


def test_remove_unit_fixes_links():
    seg = Segment(Shape.SPHERE, (1.0,), Brain(units=[Sensor("contact"), Neuron(), Neuron()]))
    seg.brain.links = [Link(UnitRef(0, 0), UnitRef(0, 1), 1.0), Link(UnitRef(0, 1), UnitRef(0, 2), 2.0), Link(UnitRef(0, 0), UnitRef(0, 2), 3.0)]
    g = Genotype(nodes=[Node(seg)])
    remove_unit(g, 0, 1)
    assert len(seg.brain.units) == 2
    assert [(l.src.index, l.dst.index, l.weight) for l in seg.brain.links] == [(0, 1, 3.0)]
    assert g.is_valid()


def test_conventional_reproduction_never_changes_the_body(rng):
    cfg = EvolutionConfig(population_size=6, elites=1, sim=SimConfig(duration=0.5))
    pop = initial_population(CONVENTIONAL, cfg, rng)
    runner = BoutRunner(cfg.sim)
    evaluate(pop, runner, rng, cfg)
    assert len(pop.fitness) == 6
    new = reproduce(pop, rng, cfg)
    assert all(is_same_morphology(m, pop.members[0]) for m in new.members)
    assert new.generation == 1 and new.best == 0


def test_all_versus_best_uses_previous_best(rng):
    cfg = EvolutionConfig(population_size=4, sim=SimConfig(duration=0.5), random_sides=False)
    pop = initial_population(HOLISTIC, cfg, rng)
    runner = BoutRunner(cfg.sim)
    evaluate(pop, runner, rng, cfg)
    assert pop.best == int(np.argmax(pop.fitness))
    assert pop.runner_up != pop.best
    assert all(0.0 <= f <= 1.0 for f in pop.fitness)


def test_champion_modes(rng):
    cfg = EvolutionConfig(population_size=3, champions=2, sim=SimConfig(duration=0.5))
    h = initial_population(HOLISTIC, cfg, rng)
    c = initial_population(CONVENTIONAL, cfg, rng)
    runner = BoutRunner(cfg.sim)
    evaluate(h, runner, rng, cfg)
    evaluate(c, runner, rng, cfg)
    best = champion_bouts(h, c, runner, cfg)
    assert best["n_bouts"] == 1 and best["mode"] == "best"
    cfg.champion_mode = "roundrobin"
    rr = champion_bouts(h, c, runner, cfg)
    assert rr["n_bouts"] == 2 * 2 * 2
    assert rr["holistic_wins"] + rr["conventional_wins"] <= rr["n_bouts"]
    assert 0.0 <= rr["holistic_mean_fitness"] <= 1.0


def test_experiment_runs_and_writes_results(tmp_path):
    cfg = EvolutionConfig(population_size=4, generations=2, elites=1, champion_interval=1, champions=1, seed=7, sim=SimConfig(duration=0.5))
    ex = Experiment(cfg, out_dir=str(tmp_path), log=None)
    summary = ex.run()
    assert len(summary["history"]) == 4  # two populations x two generations
    assert len(summary["champions"]) == 2
    hist = json.loads((tmp_path / "history.json").read_text())
    assert hist["history"] == summary["history"]
    assert (tmp_path / "holistic" / "best_gen0000.json").exists()
    assert (tmp_path / "conventional" / "best_gen0001.json").exists()
    assert len(list((tmp_path / "holistic" / "final").glob("*.json"))) == 4
    assert Genotype.load(tmp_path / "holistic" / "best_gen0001.json").is_valid()


def test_experiment_is_deterministic(tmp_path):
    def run():
        cfg = EvolutionConfig(population_size=3, generations=2, champion_interval=0, seed=3, sim=SimConfig(duration=0.3))
        return Experiment(cfg, log=None).run()["history"]

    assert run() == run()


def test_worker_pool(tmp_path):
    cfg = EvolutionConfig(population_size=3, generations=1, champion_interval=0, seed=1, workers=2, sim=SimConfig(duration=0.3))
    summary = Experiment(cfg, log=None).run()
    assert len(summary["history"]) == 2
