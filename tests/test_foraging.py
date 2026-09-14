import numpy as np

from rabbitstew.ecology import Ecology, EcologyConfig
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, EvolutionConfig
from rabbitstew.fixed import pioneer_genotype
from rabbitstew.genotype import Brain, BrainVocabulary, Effector, Genotype, Node, Segment, Sensor, Shape, random_genotype
from rabbitstew.simulation import FoodConfig, SimConfig, Simulation, run_group, run_solo
from rabbitstew.world import Spawn


def block_with_nose():
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 0.5), brain=Brain(units=[Sensor("food"), Sensor("agent"), Effector(0, 0.0)])))], name="nose")


def test_food_is_eaten_by_proximity_and_regrows_elsewhere():
    cfg = SimConfig(duration=1.0, food=FoodConfig(items=5, radius=2.0, eat_radius=0.4), settle_time=0.2)
    sim = Simulation([block_with_nose()], cfg, spawns=[Spawn((0.0, 0.0, 0.0), 0.0)])
    sim.set_food_seed(3)
    sim.food_pos[:] = 5.0  # all food far away
    sim.food_pos[0] = sim.data.geom_xpos[sim.robots[0].geoms[0]][:2]  # one item under the robot
    sim.step()
    assert sim.food_eaten[0] == 1
    assert len(sim.food_events) == 1
    assert np.linalg.norm(sim.food_pos[0]) <= 2.0 + 1e-9 and np.linalg.norm(sim.food_pos[0] - sim.data.geom_xpos[sim.robots[0].geoms[0]][:2]) > 0.4  # regrew somewhere else in the disc
    assert abs(sim.score(0)) < 1e-6  # score is "distance" here (the block sits at the centre); food_score is separate
    assert sim.food_score(0) == 1.0


def test_food_sensor_reads_intensity_not_direction():
    cfg = SimConfig(duration=1.0, food=FoodConfig(items=1, radius=2.0, decay=1.0), settle_time=0.2)
    sim = Simulation([block_with_nose()], cfg, spawns=[Spawn((0.0, 0.0, 0.0), 0.0)])
    here = sim.data.geom_xpos[sim.robots[0].geoms[0]][:2]
    sim.food_pos[0] = here + np.array([0.5, 0.0])
    near = sim.sensor_values(0, set())[0]
    sim.food_pos[0] = here + np.array([0.0, -2.5])  # same value whatever the direction; weaker further away
    far = sim.sensor_values(0, set())[0]
    sim.food_pos[0] = here + np.array([-0.5, 0.0])
    near_other_side = sim.sensor_values(0, set())[0]
    assert near > far > 0.0 and abs(near - near_other_side) < 1e-9
    assert sim.sensor_values(0, set())[1] == 0.0  # no other agent


def test_foraging_vocabulary_has_no_oracle_and_designed_body_gets_noses():
    v = BrainVocabulary.named("foraging")
    assert "target" not in v.sensor_sources and "opponent" not in v.sensor_sources and "food" in v.sensor_sources
    g = pioneer_genotype(np.random.default_rng(0), rich=True, sources=v.sensor_sources)
    sources = [u.source for _, b in g.brains() for u in b.units if u.kind == "sensor"]
    assert "target" not in sources and sources.count("food") >= 3  # chassis and both drive wheels
    assert g.validate() == []
    r = random_genotype(np.random.default_rng(1), n_nodes=3, vocab=v)
    assert all(u.source not in ("target", "opponent", "target_distance", "opponent_distance") for _, b in r.brains() for u in b.units if u.kind == "sensor")


def test_run_group_and_solo_food_score():
    v = BrainVocabulary.named("foraging")
    cfg = SimConfig(duration=0.4, random_start=True, score="food", food=FoodConfig(items=6, radius=2.0, work_cost=0.1), settle_time=0.2)
    gs = [random_genotype(np.random.default_rng(i), n_nodes=2, vocab=v) for i in range(3)]
    res = run_group(gs, cfg, start_seed=7)
    assert len(res) == 3 and all({"score", "food", "work"} <= set(r) for r in res)
    assert run_solo(gs[0], cfg, 7)["score"] == run_solo(gs[0], cfg, 7)["score"]  # reproducible from the seed


def test_ecology_foraging_challenge_runs(tmp_path):
    evo = EvolutionConfig(seed=8, brain_model="foraging", conventional_topology=True, sim=SimConfig(duration=0.3, random_start=True, score="food", food=FoodConfig(items=4, radius=2.0)))
    eco = EcologyConfig(seasons=2, capacity=5, challenge="foraging", group_size=2, living_cost=0.05, max_age=100)
    out = Ecology(evo, eco, out_dir=str(tmp_path), log=None).run()
    assert {h["population"] for h in out["history"]} == {HOLISTIC, CONVENTIONAL}
    assert all(abs(h["living_cost"] - 0.05) < 1e-12 for h in out["history"])


def test_food_never_spawns_under_a_robot():
    cfg = SimConfig(duration=1.0, food=FoodConfig(items=40, radius=1.5, clearance=0.8), settle_time=0.2)
    sim = Simulation([block_with_nose()], cfg, spawns=[Spawn((0.0, 0.0, 0.0), 0.0)])
    sim.set_food_seed(5)
    here = sim.data.xpos[sim.robots[0].root_body][:2]
    assert np.linalg.norm(sim.food_pos - here, axis=1).min() >= 0.8


def _smell_at(mode, offset, items=12, decay=3.0, seed=11):
    """Smell read by a nose at ``offset`` metres from the disc centre, over one fixed 12-item layout."""
    cfg = SimConfig(duration=1.0, food=FoodConfig(items=items, radius=3.0, decay=decay, smell=mode), settle_time=0.2)
    sim = Simulation([block_with_nose()], cfg, spawns=[Spawn((0.0, 0.0, 0.0), 0.0)])
    sim.set_food_seed(seed)
    rng = np.random.default_rng(seed)
    ang, rad = rng.uniform(0, 2 * np.pi, items), 3.0 * np.sqrt(rng.uniform(0, 1, items))
    sim.food_pos[:] = np.stack([rad * np.cos(ang), rad * np.sin(ang)], axis=1)
    sim.food_pos[0] = (0.0, 0.0)  # one item at the centre, so distance from it is the x offset
    here = sim.data.geom_xpos[sim.robots[0].geoms[0]][:2].copy()
    sim.food_pos[:] += here  # the layout rides with wherever the block settled
    sim.food_pos[:, 0] += offset  # ... and slide it, which moves the nose through the disc
    return sim.sensor_values(0, set())[0]


def test_normalised_smell_modes_are_monotone_in_distance_and_bounded():
    for mode in ("mean", "log"):
        readings = [_smell_at(mode, off) for off in (0.0, 0.5, 1.5, 2.5, 4.0, 8.0)]
        assert all(0.0 < r < 1.0 for r in readings), (mode, readings)
        assert all(a > b for a, b in zip(readings, readings[1:])), (mode, readings)


def test_normalised_smell_has_a_steeper_slope_across_the_disc_than_the_sum():
    """RBT-22: at 12 items and decay 3 m the summed smell sits on the squash's flat shoulder."""
    spans = {m: _smell_at(m, 0.5) - _smell_at(m, 2.5) for m in ("sum", "mean", "log")}
    assert spans["sum"] > 0.0
    assert spans["mean"] > spans["sum"], spans
    assert spans["log"] > spans["sum"], spans


def test_smell_mode_defaults_to_the_original_sum_and_survives_a_config_round_trip():
    assert FoodConfig().smell == "sum"
    cfg = SimConfig(food=FoodConfig(items=4, smell="log"))
    assert SimConfig.from_dict(cfg.to_dict()).food.smell == "log"


def test_an_exploded_robot_books_no_work_and_no_items():
    """RBT-30: the actuator work a diverging integrator runs up is not a measurement.  Billed, it
    reached 8e6 kJ for one founder in sixty against a median of 0.007 kJ."""
    cfg = SimConfig(duration=1.0, score="food", food=FoodConfig(items=4, radius=2.0, eat_radius=0.4, work_cost=0.03), settle_time=0.0)
    sim = Simulation([block_with_nose()], cfg, spawns=[Spawn((0.0, 0.0, 0.0), 0.0)])
    sim.food_pos[0] = sim.data.geom_xpos[sim.robots[0].geoms[0]][:2]
    sim.step()
    assert sim.food_eaten[0] == 1 and sim.food_score(0) > 0  # a stable robot books what it did
    sim.work[0] = 1.5e9  # the pre-explosion bill
    sim.exploded[0] = True
    assert sim.food_score(0) == 0.0
    assert sim.harvest(0) == {"food": 0.0, "work": 0.0, "exploded": True}


def test_the_forfeit_reaches_the_rows_a_group_season_reports():
    from rabbitstew.simulation import run_group

    cfg = SimConfig(duration=0.5, score="food", food=FoodConfig(items=3, radius=1.5, eat_radius=0.4, work_cost=0.03))
    rows = run_group([block_with_nose(), block_with_nose()], cfg, start_seed=1)
    assert all(r["work"] >= 0.0 and not r["exploded"] for r in rows)
    assert all(set(r) >= {"score", "food", "work", "path", "exploded"} for r in rows)
