import json

from rabbitstew.ecology import Ecology, EcologyConfig
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, EvolutionConfig
from rabbitstew.simulation import SimConfig


def test_ecology_runs_births_deaths_and_lineage(tmp_path):
    evo = EvolutionConfig(seed=3, brain_model="rich", conventional_topology=True, sim=SimConfig(duration=0.3, random_start=True, score="closeness"))
    eco = EcologyConfig(seasons=6, capacity=6, living_cost=0.3, birth_threshold=0.6, birth_cost=0.3, max_age=4, initial_energy=0.7)
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
