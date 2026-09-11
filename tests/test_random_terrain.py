import json

import numpy as np

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, BoutRunner, EvolutionConfig, Experiment, champion_bouts, draw_terrain_seed, evaluate, generation_sim, initial_population
from rabbitstew.fixed import drive_straight_genotype
from rabbitstew.gallery import build_gallery
from rabbitstew.simulation import SimConfig, Simulation
from rabbitstew.world import Spawn, WorldConfig, random_terrain, scenery


def test_random_terrain_is_seeded_and_varied():
    a = random_terrain(WorldConfig(terrain="random", terrain_seed=7))
    b = random_terrain(WorldConfig(terrain="random", terrain_seed=7))
    c = random_terrain(WorldConfig(terrain="random", terrain_seed=8))
    assert len(a) == 14 and [(x.shape, x.dims, x.pos) for x in a] == [(x.shape, x.dims, x.pos) for x in b]
    assert [x.pos for x in a] != [x.pos for x in c]
    heights = [x.pos[2] + (x.dims[2] / 2 if x.shape.name == "BOX" else x.dims[1] / 2 if x.shape.name == "CYLINDER" else x.dims[0]) for x in a]
    assert min(heights) >= 0.03 - 1e-9 and max(heights) <= 0.3 + 1e-9
    assert all(np.hypot(x.pos[0], x.pos[1]) <= 2.6 + 0.35 for x in a)


def test_spawn_points_are_kept_clear():
    cfg = SimConfig(world=WorldConfig(terrain="random", terrain_seed=3, random_obstacles=40))
    sim = Simulation([drive_straight_genotype(0.5), drive_straight_genotype(0.5)], cfg)
    items = scenery(sim.config.world)
    assert len(items) == 40
    for it in items:
        for sp in sim.spawns:
            assert np.hypot(it.pos[0] - sp.position[0], it.pos[1] - sp.position[1]) > 0.6
    assert len(sim.start_recording().scenery) == 40
    sim.run(0.5)
    assert not any(sim.exploded)


def test_generation_seeds_are_recorded_and_reproducible(tmp_path, rng):
    cfg = EvolutionConfig(population_size=3, generations=3, elites=1, champion_interval=1, champions=1, champion_mode="best", seed=4, sim=SimConfig(duration=0.4, world=WorldConfig(terrain="random", random_obstacles=6)), random_sides=False)
    Experiment(cfg, out_dir=str(tmp_path), log=None).run()
    hist = json.loads((tmp_path / "history.json").read_text())
    seeds = [e["terrain_seed"] for e in hist["history"] if e["population"] == HOLISTIC]
    assert len(set(seeds)) == 3 and all(s is not None for s in seeds)
    assert [c["terrain_seed"] for c in hist["champions"]] == seeds
    out = tmp_path / "g.html"
    build_gallery(str(tmp_path), str(out), every=1, log=None)
    text = out.read_text()
    data = json.loads(text[text.index("const DATA = ") + len("const DATA = ") : text.index(";\n", text.index("const DATA = "))])
    for e, c in zip(data["entries"], hist["champions"]):
        assert e["bout"]["terrain_seed"] == c["terrain_seed"]
        assert abs(e["bout"]["fitness"][0] - c["bouts"][0]["holistic_fitness"]) < 2e-3
        assert len(e["traj"]["scenery"]) == 6


def test_fixed_terrain_seed_and_flat_have_no_generation_seed(rng):
    cfg = EvolutionConfig(sim=SimConfig(world=WorldConfig(terrain="random", terrain_seed=11)))
    assert draw_terrain_seed(cfg, rng) == 11
    assert draw_terrain_seed(EvolutionConfig(), rng) is None
    assert generation_sim(EvolutionConfig(), 5) is EvolutionConfig().sim or generation_sim(EvolutionConfig(), 5).world.terrain == "flat"


def test_all_mode_fights_everyone(rng):
    cfg = EvolutionConfig(population_size=3, champion_mode="all", sim=SimConfig(duration=0.3))
    h = initial_population(HOLISTIC, cfg, rng)
    c = initial_population(CONVENTIONAL, cfg, rng)
    runner = BoutRunner(cfg.sim)
    evaluate(h, runner, rng, cfg)
    evaluate(c, runner, rng, cfg)
    res = champion_bouts(h, c, runner, cfg)
    assert res["n_bouts"] == 3 * 3 * 2
