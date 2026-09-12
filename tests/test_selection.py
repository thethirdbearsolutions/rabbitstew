import json

import numpy as np

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, BoutRunner, EvolutionConfig, Experiment, evaluate, initial_population, lexicase_select, reproduce
from rabbitstew.simulation import SimConfig


def test_lexicase_prefers_the_best_on_some_objective():
    rng = np.random.default_rng(0)
    vectors = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [0.1, 0.1, 0.1]]
    picks = [lexicase_select(vectors, rng) for _ in range(300)]
    assert set(picks) == {0, 1, 2}  # the all-round mediocre one is never picked
    assert all(abs(picks.count(i) - 100) < 40 for i in range(3))


def test_survival_keeps_parents_and_accumulates_evaluations(rng):
    cfg = EvolutionConfig(population_size=4, survival=True, sim=SimConfig(duration=0.3, random_start=True), draws=1)
    pop = initial_population(CONVENTIONAL, cfg, rng)
    runner = BoutRunner(cfg.sim)
    evaluate(pop, runner, rng, cfg, None, [1])
    assert all(m.record["evals"] == 1 for m in pop.members)
    assert len(pop.vectors) == 4 and len(pop.vectors[0]) == 5
    new = reproduce(pop, rng, cfg)
    assert len(new.members) == 8  # 4 survivors + 4 children
    survivors = [m for m in new.members if m.record.get("survivor_of")]
    assert len(survivors) == 4 and all(m.record["evals"] == 1 for m in survivors)
    assert all(not m.record for m in new.members if not m.record.get("survivor_of"))
    evaluate(new, runner, rng, cfg, None, [2])
    assert all(m.record["evals"] == 2 for m in new.members if m.record.get("survivor_of"))
    for m in new.members:
        assert abs(m.record["fitness_sum"] / m.record["evals"] - new.fitness[new.members.index(m)]) < 1e-9
    again = reproduce(new, rng, cfg)
    assert len(again.members) == 8  # truncated back to population_size survivors + children


def test_experiment_with_survival_and_lexicase(tmp_path):
    cfg = EvolutionConfig(population_size=3, generations=3, elites=1, champion_interval=0, seed=2, survival=True, selection="lexicase", sim=SimConfig(duration=0.3, random_start=True, score="closeness"))
    out = Experiment(cfg, out_dir=str(tmp_path), log=None).run()
    lines = [json.loads(l) for l in (tmp_path / "lineage.jsonl").read_text().splitlines()]
    assert any(l.get("survivor_of") for l in lines if l["generation"] == 2)
    assert all(len(l["vector"]) == 5 for l in lines)
    assert max(l.get("evals", 1) for l in lines) == 3  # someone survived the whole run
    resumed = Experiment.resume(str(tmp_path), generations=4, log=None)
    resumed.run()
