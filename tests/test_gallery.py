import json
import os
import re
import shutil

from rabbitstew.ecology import Ecology, EcologyConfig
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, EvolutionConfig
from rabbitstew.gallery import _run_kind, _seats, build_gallery, read_cohorts
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


def test_gallery_of_a_foraging_ecology_replays_the_recorded_cohort(tmp_path):
    run = _foraging_run(tmp_path / "eco")
    out = tmp_path / "g.html"
    summary = build_gallery(run, str(out), record_every=2, log=None)
    assert summary["seasons"] == 1
    data = _payload(out)
    assert data["mode"] == "seasons" and data["group"] is True and data["cohorts"] is True
    assert data["copy"]["step"] == "Season"
    entry = data["entries"][0]
    assert entry["cohort"] is True
    # before the merge each fauna forages in its own arena, so a real cohort is four of one kind,
    # named individuals rather than copies of a champion
    assert [c["kind"] for c in entry["contenders"]] == [HOLISTIC] * 4
    names = [c["label"] for c in entry["contenders"]]
    assert len(set(names)) == 4 and all(n == c["name"] for n, c in zip(names, entry["contenders"]))
    assert [c["shade"] for c in entry["contenders"]] == [0, 1, 0, 1]  # two shades, so four of a kind stay apart
    recorded = read_cohorts(run)[entry["gen"]]
    seated = [seat["name"] for row in recorded for g in row["groups"] for seat in g]
    assert all(n in seated for n in names)
    assert len(entry["bout"]["food"]) == 4 and len(entry["bout"]["work"]) == 4
    assert set(u["robot"] for u in entry["traj"]["units"]) == {0, 1, 2, 3}  # four robots share the one arena
    food = entry["traj"]["food"]
    assert len(food["frames"]) == len(entry["traj"]["frames"]) and len(food["frames"][0]) == 2 * 5
    assert entry["eco"][HOLISTIC]["alive"] and entry["eco"][CONVENTIONAL]["capacity"] == 4
    assert data["curve"][0].keys() >= {"gen", "holistic", "conventional"}


def test_a_replayed_seat_carries_its_own_record_not_its_populations(tmp_path):
    run = _foraging_run(tmp_path / "eco", seasons=3)
    out = tmp_path / "g.html"
    build_gallery(run, str(out), record_every=2, log=None)
    entry = _payload(out)["entries"][-1]
    assert all("record" in c for c in entry["contenders"])
    for c in entry["contenders"]:
        assert c["record"]["age"] is not None and c["record"]["evals"] is not None
        assert c["record"]["lifetime"] is not None and c["record"]["energy"] is not None
    # the seats are distinct individuals: founders start at staggered ages, so the ages differ
    # even in a run where nobody has eaten yet and every energy is the same
    assert len({c["record"]["age"] for c in entry["contenders"]}) > 1


def test_gallery_falls_back_to_champions_for_a_run_without_cohorts(tmp_path):
    """A run written before RBT-27 has no cohorts.jsonl and no genomes: the page still builds,
    on the stand-in, and says so."""
    run = _foraging_run(tmp_path / "eco")
    os.remove(os.path.join(run, "cohorts.jsonl"))
    shutil.rmtree(os.path.join(run, HOLISTIC, "genomes"))
    shutil.rmtree(os.path.join(run, CONVENTIONAL, "genomes"))
    out = tmp_path / "g.html"
    build_gallery(run, str(out), record_every=2, log=None)
    data = _payload(out)
    assert data["cohorts"] is False and data["entries"][0]["cohort"] is False
    assert [c["kind"] for c in data["entries"][0]["contenders"]] == _seats(4)
    assert [c["label"] for c in data["entries"][0]["contenders"]] == ["Holistic best", "Conventional best", "Holistic best (copy 2)", "Conventional best (copy 2)"]
    assert "did not record who shared which arena" in data["copy"]["lead"]


def test_gallery_ignores_a_cohort_whose_genotypes_are_missing(tmp_path):
    """Half a record is not a record: with cohorts.jsonl but no genomes, fall back rather than
    replay a cohort assembled from whatever happens to be on disk."""
    run = _foraging_run(tmp_path / "eco")
    shutil.rmtree(os.path.join(run, HOLISTIC, "genomes"))
    out = tmp_path / "g.html"
    build_gallery(run, str(out), record_every=2, log=None)
    assert _payload(out)["entries"][0]["cohort"] is False


def test_an_ecology_can_be_told_not_to_save_genomes(tmp_path):
    evo = EvolutionConfig(seed=1, brain_model="foraging", conventional_topology=True, sim=SimConfig(duration=0.4, random_start=True, score="food", food=FoodConfig(items=5, radius=1.5, eat_radius=0.4)))
    eco = EcologyConfig(seasons=1, capacity=4, challenge="foraging", group_size=4, max_age=1000, log_every=1000, save_genomes=False)
    Ecology(evo, eco, out_dir=str(tmp_path / "eco"), log=None).run()
    assert not os.path.exists(os.path.join(tmp_path, "eco", HOLISTIC, "genomes"))
    assert os.path.exists(os.path.join(tmp_path, "eco", "cohorts.jsonl"))  # the draw is still on the record


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
