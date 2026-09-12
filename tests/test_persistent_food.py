"""The persistent foraging world (RBT-19): patches, depletion with slow recovery, and food
state that carries from one season to the next."""

import numpy as np
import pytest

from rabbitstew.ecology import Ecology, EcologyConfig
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.genotype import BrainVocabulary, random_genotype
from rabbitstew.simulation import FoodConfig, SimConfig, Simulation, SynthesisConfig, clear_spawn_layout, run_group, spawn_layout


def food_cfg(**kw) -> FoodConfig:
    base = dict(items=26, radius=3.0, eat_radius=0.35, decay=1.0, patches=3, patch_radius=0.6, regrow_delay=45.0)
    base.update(kw)
    return FoodConfig(**base)


def sim_cfg(**kw) -> SimConfig:
    return SimConfig(duration=1.0, random_start=True, score="food", synthesis=SynthesisConfig(mass_budget=15.34), food=food_cfg(**kw))


def one_robot_sim(cfg: SimConfig, seed: int = 3) -> Simulation:
    g = random_genotype(np.random.default_rng(seed), name="r", vocab=BrainVocabulary.named("foraging"))
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    return sim


# -- 1. patches ------------------------------------------------------------- #

def test_items_cluster_within_patch_radius_of_a_centre():
    cfg = sim_cfg()
    sim = one_robot_sim(cfg)
    assert len(sim.patch_centres) == 3
    assert len(sim.food_spots) == 26
    d = np.linalg.norm(sim.food_spots[:, None, :] - sim.patch_centres[None, :, :], axis=2).min(axis=1)
    assert d.max() <= cfg.food.patch_radius + 1e-9
    assert np.linalg.norm(sim.food_spots, axis=1).max() <= cfg.food.radius + 1e-9
    # three patches, not one cloud: the spread of the centres dwarfs the spread within a patch
    assert np.linalg.norm(sim.patch_centres[:, None, :] - sim.patch_centres[None, :, :], axis=2).max() > cfg.food.patch_radius


def test_patches_off_keeps_the_uniform_placement():
    """With patches 0 and no delay the world is the baseline's, item for item."""
    a = one_robot_sim(SimConfig(duration=1.0, random_start=True, score="food", food=FoodConfig(items=12)))
    b = one_robot_sim(SimConfig(duration=1.0, random_start=True, score="food", food=FoodConfig(items=12)))
    assert len(a.patch_centres) == 0
    assert np.allclose(a.food_pos, b.food_pos)
    assert a.food_alive.all()


def test_clearance_still_holds_at_placement():
    cfg = sim_cfg(items=40)
    sim = one_robot_sim(cfg)
    d = np.linalg.norm(sim.food_spots - sim._robot_positions()[0], axis=1)
    assert d.min() >= cfg.food.clearance - 1e-9


# -- 2. depletion and recovery --------------------------------------------- #

def test_eaten_item_returns_at_its_own_spot_after_the_delay_and_not_before():
    cfg = sim_cfg(regrow_delay=2.0)
    sim = one_robot_sim(cfg)
    spot = sim.food_spots[0].copy()
    sim.food_eaten[0] = 0
    sim.food_alive[0] = False          # eat item 0 by hand: no need for a robot that can forage
    sim.food_timer[0] = cfg.food.regrow_delay
    sim.food_pos[0] = (1e6, 1e6)
    sim._regrow_spots(1.9)
    assert not sim.food_alive[0], "back before its delay ran out"
    assert sim.food_pos[0][0] > 1e5
    sim._regrow_spots(0.2)
    assert sim.food_alive[0]
    assert np.allclose(sim.food_pos[0], spot), "regrew somewhere other than its own spot"


def test_eating_empties_the_spot_for_the_delay():
    """A robot parked on an item eats it; the spot is empty and timing down straight after."""
    cfg = sim_cfg(regrow_delay=45.0, clearance=0.0)
    sim = one_robot_sim(cfg)
    here = sim._robot_positions()[0]
    sim.food_spots[:] = (50.0, 50.0)      # every other item well out of reach
    sim.food_spots[0] = here
    sim.food_pos = sim.food_spots.copy()
    sim._eat()
    assert sim.food_eaten[0] == 1
    assert int(sim.food_alive.sum()) == len(sim.food_alive) - 1
    assert not sim.food_alive[0]
    assert sim.food_timer[0] == pytest.approx(45.0)
    assert sim.food_pos[0][0] > 1e5, "the eaten item is still smellable where it was"


def test_an_item_eaten_in_a_15_s_season_is_still_gone_at_the_end_of_it():
    cfg = sim_cfg(regrow_delay=45.0)
    sim = one_robot_sim(cfg)
    sim.food_alive[0], sim.food_timer[0] = False, 45.0
    sim.food_pos[0] = (1e6, 1e6)
    sim._regrow_spots(15.0)
    assert not sim.food_alive[0]
    assert sim.food_timer[0] == pytest.approx(30.0)


# -- 3. the state round-trip ------------------------------------------------ #

def test_food_state_round_trips_through_a_simulation():
    cfg = sim_cfg()
    a = one_robot_sim(cfg, seed=5)
    a.food_alive[[1, 4, 9]] = False
    a.food_timer[[1, 4, 9]] = [30.0, 15.0, 44.0]
    a.food_pos[[1, 4, 9]] = (1e6, 1e6)
    state = a.food_state()
    assert isinstance(state["spots"], list) and isinstance(state["alive"][0], bool)

    b = one_robot_sim(cfg, seed=11)          # a different arena, until it is handed the state
    assert not np.allclose(b.food_spots, a.food_spots)
    b.set_food_state(state)
    assert np.allclose(b.food_spots, a.food_spots)
    assert np.allclose(b.patch_centres, a.patch_centres)
    assert list(b.food_alive) == list(a.food_alive)
    assert np.allclose(b.food_timer, a.food_timer)
    assert np.allclose(b.food_pos, a.food_pos)
    assert int(b.food_alive.sum()) == 23


def test_run_group_carries_the_state_in_and_hands_it_back():
    cfg = sim_cfg(regrow_delay=45.0)
    cfg.duration = 2.0
    rng = np.random.default_rng(1)
    vocab = BrainVocabulary.named("foraging")
    gs = [random_genotype(rng, name=f"g{i}", vocab=vocab) for i in range(2)]

    res, state = run_group(gs, cfg, start_seed=4, return_state=True, food_seed=77)
    assert len(res) == 2 and len(state["spots"]) == 26

    eaten = [i for i, a in enumerate(state["alive"]) if not a]
    if not eaten:                                     # random genotypes rarely reach an item
        state = {**state, "alive": [i != 0 for i in range(26)], "timer": [45.0 if i == 0 else 0.0 for i in range(26)]}
        eaten = [0]
    res2, state2 = run_group(gs, cfg, start_seed=4, food_state=state, return_state=True)
    assert state2["spots"] == state["spots"], "the spots moved between seasons"
    assert state2["centres"] == state["centres"], "the patch centres moved between seasons"
    for j in eaten:                                   # still gone, and closer to coming back
        assert not state2["alive"][j]
        assert state2["timer"][j] == pytest.approx(state["timer"][j] - cfg.duration, abs=1e-6)


# -- 4. the ecology carries its arenas across seasons ----------------------- #

def small_ecology(tmp_path, **food):
    evo = EvolutionConfig(seed=5, workers=1, conventional_topology=True, brain_model="foraging",
                          sim=SimConfig(duration=1.0, random_start=True, score="food", synthesis=SynthesisConfig(mass_budget=15.34), food=food_cfg(**food)))
    eco = EcologyConfig(seasons=2, capacity=4, challenge="foraging", group_size=2, initial_energy=3.0,
                        birth_threshold=3.0, birth_cost=1.0, living_cost=0.25, max_age=60, log_every=100)
    return Ecology(evo, eco, out_dir=str(tmp_path), log=lambda s: None)


def test_ecology_keeps_one_persistent_arena_per_group_slot(tmp_path):
    e = small_ecology(tmp_path)
    assert e.persistent
    e.step()
    bank = e.arenas[("holistic",)]
    assert len(bank) == 2, "capacity 4 in groups of 2 is two arenas"
    assert all(a["state"] is not None for a in bank), "every arena was used, so every one has state"
    assert len({tuple(map(tuple, a["state"]["centres"])) for a in bank}) == 2, "arenas share a layout"


def test_ecology_carries_arena_state_across_two_seasons(tmp_path):
    e = small_ecology(tmp_path)
    e.step()
    bank = e.arenas[("holistic",)]
    before = [{**a["state"]} for a in bank]
    # empty a spot in every arena, with a delay far longer than a season
    for a in bank:
        a["state"]["alive"][0] = False
        a["state"]["timer"][0] = 45.0
        a["state"]["alive"][1] = False
        a["state"]["timer"][1] = 45.0
    e.step()
    for a, was in zip(bank, before):
        assert a["state"]["spots"] == was["spots"], "the arena was re-seeded instead of carried"
        assert not a["state"]["alive"][0], "an item eaten last season was back at the start of this one"
        assert a["state"]["timer"][0] < 45.0, "the regrowth clock did not run"


def test_an_unvisited_arena_still_regrows(tmp_path):
    """Nobody stands in every arena every season; the world's clock runs in all of them."""
    e = small_ecology(tmp_path, regrow_delay=1.5)
    state = {"spots": [[1.0, 0.0], [0.0, 1.0]], "alive": [False, True], "timer": [1.5, 0.0], "centres": [[0.0, 0.0]]}
    aged = e._age_arena(state, 1.0)
    assert aged["alive"] == [False, True] and aged["timer"][0] == pytest.approx(0.5)
    aged = e._age_arena(aged, 1.0)
    assert aged["alive"] == [True, True] and aged["timer"][0] == 0.0


def test_arena_supply_is_logged_and_saved(tmp_path):
    e = small_ecology(tmp_path)
    e.step()
    e._flush()
    import json
    saved = json.load(open(tmp_path / "arenas.json"))
    assert saved["items"] == 26 and saved["regrow_delay"] == 45.0 and saved["patches"] == 3
    rows = [r for r in saved["seasons"] if r["season"] == 0]
    assert {r["population"] for r in rows} == {"holistic", "conventional"}
    for r in rows:
        assert r["season_start_crop_mean"] == 26.0, "season 0 starts in a full arena"
        assert r["empty_fraction"] == 0.0
        assert r["harvest_per_group"] >= 0.0
    assert len(saved["arenas"]["holistic"]) == 2


# -- 5. the clearance rule survives persistence ----------------------------- #

def test_a_group_entering_a_persistent_arena_starts_clear_of_the_food():
    """Spots cannot move between seasons, so the robots are placed away from the food instead.

    Nobody may start close enough to eat without moving; a crowded arena cannot always afford the
    full clearance, and there the roomiest draw of the 128 wins."""
    cfg = sim_cfg()
    sim = one_robot_sim(cfg, seed=2)
    state = sim.food_state()
    live = np.array([p for p, a in zip(state["spots"], state["alive"]) if a])
    gaps = []
    for seed in range(40):
        spawns = clear_spawn_layout(4, cfg, seed, state)
        pos = np.array([sp.position[:2] for sp in spawns])
        gaps.append(float(np.linalg.norm(pos[:, None, :] - live[None, :, :], axis=2).min()))
    gaps = np.array(gaps)
    assert gaps.min() > cfg.food.eat_radius, "a robot starts on top of an item: free lunch for standing still"
    assert gaps.min() > 0.5, "the roomiest of 128 draws still crowds the robots against the food"


def test_a_group_entering_a_half_eaten_arena_keeps_the_full_clearance():
    cfg = sim_cfg()
    sim = one_robot_sim(cfg, seed=2)
    state = sim.food_state()
    keep = np.random.default_rng(4).random(len(state["alive"])) < 0.45   # a settled arena, half empty
    state = {**state, "alive": [bool(v) for v in keep], "timer": [0.0 if v else 30.0 for v in keep]}
    live = np.array([p for p, a in zip(state["spots"], state["alive"]) if a])
    gaps = []
    for seed in range(25):
        pos = np.array([sp.position[:2] for sp in clear_spawn_layout(4, cfg, seed, state)])
        gaps.append(float(np.linalg.norm(pos[:, None, :] - live[None, :, :], axis=2).min()))
    gaps = np.array(gaps)
    assert gaps.min() > cfg.food.eat_radius
    assert (gaps >= cfg.food.clearance).mean() >= 0.5, "an arena with room to spare still crowds the robots"


def test_clear_spawn_layout_is_a_no_op_in_an_empty_arena():
    cfg = sim_cfg()
    state = {"spots": [[1.0, 0.0]], "alive": [False], "timer": [45.0], "centres": [[0.0, 0.0]]}
    a = clear_spawn_layout(4, cfg, 9, state)
    b = spawn_layout(4, cfg, 9)
    assert [s.position for s in a] == [s.position for s in b]
