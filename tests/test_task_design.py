import json

import numpy as np
import pytest

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, BoutRunner, EvolutionConfig, Experiment, draw_start_seeds, evaluate, initial_population, reproduce
from rabbitstew.fixed import drive_straight_genotype, pioneer_genotype
from rabbitstew.genotype import Genotype, Node, Segment, Shape
from rabbitstew.simulation import SimConfig, Simulation, run_bout, run_solo, spawn_layout, zero_sum_scores


def test_spawn_layout_is_seeded_opposite_and_within_ranges():
    cfg = SimConfig(random_start=True)
    a = spawn_layout(2, cfg, 5)
    b = spawn_layout(2, cfg, 5)
    c = spawn_layout(2, cfg, 6)
    assert [(s.position, s.yaw) for s in a] == [(s.position, s.yaw) for s in b]
    assert a[0].position != c[0].position
    for sp in a:
        d = np.hypot(sp.position[0], sp.position[1])
        assert 1.5 <= d <= 2.5
    assert np.allclose(np.array(a[0].position[:2]) + np.array(a[1].position[:2]), 0.0, atol=1e-9)  # opposite sides
    towards = np.arctan2(-a[0].position[1], -a[0].position[0])
    off = (a[0].yaw - towards + np.pi) % (2 * np.pi) - np.pi
    assert abs(off) <= 0.75 * np.pi + 1e-9
    assert spawn_layout(2, SimConfig(), 5)[0].position[0] == pytest.approx(-2.0)  # not random: the paper's layout


def test_time_at_target_score_rewards_staying_not_passing():
    driver = drive_straight_genotype(0.8)  # crosses the centre and keeps going
    block = Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0)))])
    cfg = SimConfig(score="time_at_target", duration=6.0)
    r = run_bout(driver, block, cfg)
    assert r.time_at_target[0] < 0.4 and r.time_at_target[1] == 0.0
    assert r.scores[0] > r.scores[1] and r.fitness[0] > 0.5  # the driver did pass through the target
    assert zero_sum_scores([0.0, 0.0], [False, False]) == [0.5, 0.5]
    assert zero_sum_scores([0.3, 0.1], [False, False]) == pytest.approx([0.75, 0.25])
    sim = Simulation([driver], SimConfig(score="time_at_target"), spawns=spawn_layout(2, SimConfig(), None)[:1])
    assert sim.score(0) == pytest.approx(0.0)


def test_run_solo_scores_alone():
    r = run_solo(drive_straight_genotype(0.6), SimConfig(duration=3.0, random_start=True), start_seed=1)
    assert 0.0 <= r["progress"] <= 1.0 and r["start_seed"] == 1 and not r["exploded"]
    assert r["score"] == pytest.approx(r["time_at_target"] + 0.1 * r["progress"])


def test_multi_opponent_multi_draw_evaluation(rng):
    cfg = EvolutionConfig(population_size=4, opponents=2, draws=2, sim=SimConfig(duration=0.3, random_start=True))
    pop = initial_population(CONVENTIONAL, cfg, rng)
    seeds = draw_start_seeds(cfg, rng)
    assert len(seeds) == 2 and all(s is not None for s in seeds)
    runner = BoutRunner(cfg.sim)
    calls = []
    orig = runner.run

    def spy(pairs, sim=None):
        calls.append(len(pairs))
        return orig(pairs, sim)

    runner.run = spy
    evaluate(pop, runner, rng, cfg, None, seeds)
    assert calls[0] == 4 * 1 * 2  # first generation: only one known opponent (a random best)
    assert len(pop.top) == 3
    new = reproduce(pop, rng, cfg)
    assert new.top == [0, 1]
    evaluate(new, runner, rng, cfg, None, seeds)
    assert calls[1] == (2 * 1 + 2 * 2) * 2  # elites meet the other elite; children meet both elites; two draws each


def test_locomotion_phase_then_competition(tmp_path):
    cfg = EvolutionConfig(population_size=3, generations=3, elites=1, champion_interval=1, champions=1, seed=8, locomotion_phase=2, sim=SimConfig(duration=0.3, random_start=True, score="time_at_target"))
    out = Experiment(cfg, out_dir=str(tmp_path), log=None).run()
    solo = [e["solo"] for e in out["history"] if e["population"] == HOLISTIC]
    assert solo == [True, True, False]
    assert all(len(e["start_seeds"]) == 1 and e["start_seeds"][0] is not None for e in out["history"])
    assert out["champions"][0]["start_seed"] == out["history"][0]["start_seeds"][0]
    assert out["champions"][0]["bouts"][0]["time_at_target"] is not None
    # the gallery reproduces the bout with the recorded start seed
    from rabbitstew.gallery import build_gallery

    build_gallery(str(tmp_path), str(tmp_path / "g.html"), every=1, log=None)
    text = (tmp_path / "g.html").read_text()
    data = json.loads(text[text.index("const DATA = ") + len("const DATA = ") : text.index(";\n", text.index("const DATA = "))])
    for e, c in zip(data["entries"], out["champions"]):
        assert e["bout"]["start_seed"] == c["start_seed"]
        assert abs(e["bout"]["fitness"][0] - c["bouts"][0]["holistic_fitness"]) < 2e-3
