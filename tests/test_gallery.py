import json
import re

from rabbitstew.ecology import Ecology, EcologyConfig
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, EvolutionConfig
from rabbitstew.gallery import _run_kind, _seats, build_gallery
from rabbitstew.simulation import FoodConfig, SimConfig


def _payload(path) -> dict:
    """The DATA literal the page hands to its script."""
    text = open(path).read()
    return json.loads(re.search(r"const DATA = (\{.*\});", text).group(1).replace("<\\/", "</"))


def _foraging_run(out_dir, seasons: int = 1, group_size: int = 4):
    evo = EvolutionConfig(seed=1, brain_model="foraging", conventional_topology=True, sim=SimConfig(duration=0.4, random_start=True, score="food", food=FoodConfig(items=5, radius=1.5, eat_radius=0.4)))
    eco = EcologyConfig(seasons=seasons, capacity=4, challenge="foraging", group_size=group_size, max_age=1000, log_every=1000)
    Ecology(evo, eco, out_dir=str(out_dir), log=None).run()
    return str(out_dir)


def test_seats_alternate_the_two_fauna():
    assert _seats(4) == [HOLISTIC, CONVENTIONAL, HOLISTIC, CONVENTIONAL]
    assert _seats(2) == [HOLISTIC, CONVENTIONAL]


def test_an_ecology_run_is_recognised_and_a_ga_run_is_not(tmp_path):
    run = _foraging_run(tmp_path / "eco")
    config, history, mode, eco = _run_kind(run)
    assert mode == "seasons" and eco["challenge"] == "foraging" and eco["group_size"] == 4
    assert history["history"][0]["season"] == 0


def test_gallery_of_a_foraging_ecology_replays_a_group_arena(tmp_path):
    run = _foraging_run(tmp_path / "eco")
    out = tmp_path / "g.html"
    summary = build_gallery(run, str(out), record_every=2, log=None)
    assert summary["seasons"] == 1
    data = _payload(out)
    assert data["mode"] == "seasons" and data["group"] is True
    assert data["copy"]["step"] == "Season"
    entry = data["entries"][0]
    assert [c["kind"] for c in entry["contenders"]] == _seats(4)
    assert [c["label"] for c in entry["contenders"]] == ["Holistic best", "Conventional best", "Holistic best (copy 2)", "Conventional best (copy 2)"]
    assert len(entry["bout"]["food"]) == 4 and len(entry["bout"]["work"]) == 4
    assert set(u["robot"] for u in entry["traj"]["units"]) == {0, 1, 2, 3}  # four robots share the one arena
    food = entry["traj"]["food"]
    assert len(food["frames"]) == len(entry["traj"]["frames"]) and len(food["frames"][0]) == 2 * 5
    assert entry["eco"][HOLISTIC]["alive"] and entry["eco"][CONVENTIONAL]["capacity"] == 4
    assert data["curve"][0].keys() >= {"gen", "holistic", "conventional"}


def test_gallery_of_a_duelling_ecology_keeps_two_seats_and_says_seasons(tmp_path):
    evo = EvolutionConfig(seed=1, brain_model="rich", conventional_topology=True, sim=SimConfig(duration=0.3, random_start=True, score="closeness"))
    Ecology(evo, EcologyConfig(seasons=1, capacity=3, challenge="solo", max_age=1000, log_every=1000), out_dir=str(tmp_path / "eco"), log=None).run()
    out = tmp_path / "g.html"
    build_gallery(str(tmp_path / "eco"), str(out), log=None)
    data = _payload(out)
    assert data["mode"] == "seasons" and data["group"] is False
    entry = data["entries"][0]
    assert len(entry["contenders"]) == 2 and "fitness" in entry["bout"]
    assert entry["traj"]["food"] is None  # no foraging world, nothing to draw
    assert "eco" in entry and "checkpoint" not in entry


def test_gallery_of_a_ga_run_is_unchanged(tmp_path):
    from rabbitstew.evolution import Experiment

    evo = EvolutionConfig(seed=2, generations=1, population_size=3, champion_interval=1, champions=1, brain_model="rich", conventional_topology=True, sim=SimConfig(duration=0.3))
    Experiment(evo, out_dir=str(tmp_path / "ga"), log=None).run()
    out = tmp_path / "g.html"
    build_gallery(str(tmp_path / "ga"), str(out), log=None)
    data = _payload(out)
    assert data["mode"] == "generations" and data["group"] is False
    assert data["copy"]["step"] == "Generation"
    entry = data["entries"][0]
    assert len(entry["contenders"]) == 2 and len(entry["bout"]["fitness"]) == 2
    assert "eco" not in entry and entry["traj"]["food"] is None
    assert data["curve"][0].keys() >= {"gen", "mean"}
