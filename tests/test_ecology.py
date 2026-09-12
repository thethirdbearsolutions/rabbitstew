import json

from rabbitstew.ecology import Ecology, EcologyConfig
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, EvolutionConfig
from rabbitstew.simulation import SimConfig


def test_ecology_runs_births_deaths_and_lineage(tmp_path):
    evo = EvolutionConfig(seed=3, brain_model="rich", conventional_topology=True, sim=SimConfig(duration=0.3, random_start=True, score="closeness"))
    eco = EcologyConfig(seasons=6, capacity=6, living_cost=0.3, birth_threshold=0.6, birth_cost=0.3, max_age=4, initial_energy=0.7, stagger_ages=False)
    e = Ecology(evo, eco, out_dir=str(tmp_path), log=None)
    out = e.run()
    hist = out["history"]
    assert {h["population"] for h in hist} == {HOLISTIC, CONVENTIONAL}
    assert any(h["deaths"] > 0 for h in hist)  # old age at 4 seasons guarantees deaths
    assert all(h["alive"] <= 6 for h in hist)
    lines = [json.loads(l) for l in (tmp_path / "lineage.jsonl").read_text().splitlines()]
    assert all("energy" in l and "age" in l and "evals" in l for l in lines)
    assert max(l["evals"] for l in lines) >= 2  # somebody lived through more than one challenge
    assert (tmp_path / "history.json").exists() and (tmp_path / "config.json").exists()
    assert (tmp_path / HOLISTIC / "final").exists()


def test_ecology_paired_challenge(tmp_path):
    evo = EvolutionConfig(seed=4, sim=SimConfig(duration=0.3, random_start=True, score="closeness"))
    eco = EcologyConfig(seasons=2, capacity=5, challenge="paired", max_age=10)
    Ecology(evo, eco, out_dir=str(tmp_path), log=None).run()
    lines = [json.loads(l) for l in (tmp_path / "lineage.jsonl").read_text().splitlines()]
    assert all(0.0 <= l["last_score"] <= 1.0 for l in lines)


def test_history_command_prints_ecology_seasons(tmp_path, capsys):
    import json
    from rabbitstew.cli import main

    hist = {"ecology": True, "champions": [], "history": [
        {"season": 0, "population": "holistic", "alive": 4, "births": 0, "deaths": 0, "best_lifetime_score": 0.6, "mean_lifetime_score": 0.5, "mean_age": 1.0, "max_age": 1},
        {"season": 0, "population": "conventional", "alive": 4, "births": 1, "deaths": 1, "best_lifetime_score": 0.7, "mean_lifetime_score": 0.4, "mean_age": 1.0, "max_age": 1},
    ]}
    path = tmp_path / "history.json"
    path.write_text(json.dumps(hist))
    assert main(["history", str(path)]) == 0
    out = capsys.readouterr().out
    assert "season" in out and "conventional" in out and "0.700/0.400" in out


def test_relative_living_cost_conserves_energy_and_staggers_ages(tmp_path):
    evo = EvolutionConfig(seed=5, sim=SimConfig(duration=0.3, random_start=True, score="closeness"))
    eco = EcologyConfig(seasons=3, capacity=8, living_cost="relative", initial_energy=2.0, birth_threshold=100.0, max_age=1000)
    e = Ecology(evo, eco, out_dir=str(tmp_path), log=None)
    ages0 = [m.record["age"] for m in e.populations[HOLISTIC]]
    assert len(set(ages0)) > 1 and min(ages0) >= 0 and max(ages0) < 1000
    out = e.run()
    for h in out["history"]:
        assert h["deaths"] == 0 and h["births"] == 0
        assert abs(h["total_energy"] - 8 * 2.0) < 1e-6  # relative cost moves energy around, never creates or destroys it


def test_fixed_living_cost_parses_from_cli():
    from rabbitstew.cli import build_parser

    p = build_parser()
    assert p.parse_args(["ecology", "--living-cost", "relative"]).living_cost == "relative"
    assert p.parse_args(["ecology", "--living-cost", "0.1"]).living_cost == 0.1


def test_neutral_ecology_turns_over_by_age_only(tmp_path):
    evo = EvolutionConfig(seed=6, sim=SimConfig(duration=0.3, random_start=True, score="closeness"))
    eco = EcologyConfig(seasons=5, capacity=6, starvation=False, birth_threshold=0.0, birth_cost=0.0, living_cost=0.0, max_age=3, stagger_ages=True)
    out = Ecology(evo, eco, out_dir=str(tmp_path), log=None).run()
    hist = out["history"]
    assert sum(h["deaths"] for h in hist) > 0 and sum(h["births"] for h in hist) > 0
    # each survivor breeds at most once a season, so a slot may wait a season; the population is full again by the end
    assert all(h["alive"] == 6 for h in hist if h["season"] == hist[-1]["season"])
    assert all(h["births"] >= min(h["deaths"], h["alive"] - h["births"]) for h in hist)  # freed slots are refilled whatever anyone scored
