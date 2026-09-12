import json

import pytest

from rabbitstew.ecology import Ecology, EcologyConfig
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, EvolutionConfig
from rabbitstew.genotype import Genotype
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


def test_ecology_paired_challenge_still_runs_but_warns(tmp_path):
    evo = EvolutionConfig(seed=4, sim=SimConfig(duration=0.3, random_start=True, score="closeness"))
    eco = EcologyConfig(seasons=2, capacity=5, challenge="paired", max_age=10)
    with pytest.warns(UserWarning, match="retired ecology economy"):  # retired under RBT-8, kept so paper 3 reproduces
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
    with pytest.warns(UserWarning, match="retired ecology economy"):  # retired under RBT-8, kept so paper 3 reproduces
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
    assert p.parse_args(["ecology"]).living_cost == 0.05  # the default economy is absolute: energy comes from the world
    assert p.parse_args(["ecology", "--living-cost", "relative"]).living_cost == "relative"
    assert p.parse_args(["ecology", "--living-cost", "0.1"]).living_cost == 0.1


def test_default_economy_is_absolute_and_is_not_warned_about():
    eco = EcologyConfig()
    assert eco.retired_economy() is None
    assert eco.living_cost != "relative" and eco.challenge != "paired"
    assert eco.cost([0.0, 0.0, 0.0]) == 0.05  # a fixed charge, not whatever the neighbours happened to score


def test_retired_economies_are_named_with_their_reason():
    assert 'living_cost="relative"' in EcologyConfig(living_cost="relative").retired_economy()
    assert 'challenge="paired"' in EcologyConfig(challenge="paired").retired_economy()
    assert EcologyConfig(living_cost=0.1, challenge="foraging").retired_economy() is None


def test_only_an_absolute_cost_lets_a_converged_population_reach_the_threshold():
    """The failure RBT-8 is about, in the arithmetic alone.

    A converged population scores alike, so under a relative cost every member
    is charged exactly what it earned and nobody's energy ever moves; under an
    absolute cost the same competence pays, because the threshold is measured
    against the world and not against the neighbours.
    """
    gains = [0.5] * 8  # everyone alike, which is what a competent population becomes
    relative = EcologyConfig(living_cost="relative", initial_energy=2.0, birth_threshold=3.0)
    absolute = EcologyConfig(living_cost=0.25, initial_energy=2.0, birth_threshold=3.0)  # any absolute charge below the gain will do

    def energy_after(eco, seasons):
        energy = eco.initial_energy
        for _ in range(seasons):
            energy += gains[0] - eco.cost(gains)
        return energy

    assert energy_after(relative, 1000) == pytest.approx(2.0)  # no lifespan is long enough
    assert energy_after(relative, 1000) < relative.birth_threshold
    assert energy_after(absolute, 4) >= absolute.birth_threshold  # four good seasons buy a child


def test_neutral_ecology_turns_over_by_age_only(tmp_path):
    evo = EvolutionConfig(seed=6, sim=SimConfig(duration=0.3, random_start=True, score="closeness"))
    eco = EcologyConfig(seasons=5, capacity=6, starvation=False, birth_threshold=0.0, birth_cost=0.0, living_cost=0.0, max_age=3, stagger_ages=True)
    out = Ecology(evo, eco, out_dir=str(tmp_path), log=None).run()
    hist = out["history"]
    assert sum(h["deaths"] for h in hist) > 0 and sum(h["births"] for h in hist) > 0
    # each survivor breeds at most once a season, so a slot may wait a season; the population is full again by the end
    assert all(h["alive"] == 6 for h in hist if h["season"] == hist[-1]["season"])
    assert all(h["births"] >= min(h["deaths"], h["alive"] - h["births"]) for h in hist)  # freed slots are refilled whatever anyone scored


def _quick_evo(seed=7):
    return EvolutionConfig(seed=seed, brain_model="rich", conventional_topology=True, sim=SimConfig(duration=0.3, random_start=True, score="closeness"))


def test_ecology_starts_from_a_saved_population(tmp_path):
    first = tmp_path / "first"
    eco = EcologyConfig(seasons=2, capacity=4, birth_threshold=100.0, max_age=1000, stagger_ages=False)
    Ecology(_quick_evo(), eco, out_dir=str(first), log=None).run()
    saved = sorted(p.name for p in (first / HOLISTIC / "final").iterdir())
    assert len(saved) == 4

    second = Ecology(_quick_evo(seed=8), EcologyConfig(seasons=1, capacity=4, max_age=1000, seed_from=str(first)), out_dir=str(tmp_path / "second"), log=None)
    loaded = second.populations[HOLISTIC]
    original = [Genotype.load(first / HOLISTIC / "final" / n) for n in saved]
    assert [g.name for g in loaded] == [g.name for g in original]
    assert [len(g.nodes) for g in loaded] == [len(g.nodes) for g in original]
    # they enter as founders of the new run: age carried over, lifetime record and parentage cleared
    assert all(m.record["evals"] == 0 and m.parents == [] for m in loaded)
    assert [m.record["age"] for m in loaded] == [g.record["age"] for g in original]
    assert all(m.record["kind"] == CONVENTIONAL for m in second.populations[CONVENTIONAL])


def test_saved_population_is_cycled_when_smaller_than_capacity(tmp_path):
    run = tmp_path / "run"
    Ecology(_quick_evo(), EcologyConfig(seasons=1, capacity=3, birth_threshold=100.0, max_age=1000), out_dir=str(run), log=None).run()
    e = Ecology(_quick_evo(seed=9), EcologyConfig(seasons=1, capacity=7, max_age=1000, seed_from=str(run)), out_dir=str(tmp_path / "out"), log=None)
    members = e.populations[HOLISTIC]
    assert len(members) == 7
    assert len({m.name for m in members}) == 7  # clones are renamed, so lineage names stay unique


def test_merge_after_pools_the_two_ecologies(tmp_path):
    eco = EcologyConfig(seasons=4, capacity=4, merge_after=2, pooled_capacity=8, living_cost=0.0, birth_threshold=0.05, birth_cost=0.01, max_age=1000)
    out = Ecology(_quick_evo(), eco, out_dir=str(tmp_path), log=None).run()
    hist = out["history"]
    assert all(not h["merged"] and h["capacity"] == 4 for h in hist if h["season"] < 2)
    assert all(h["merged"] and h["capacity"] == 8 for h in hist if h["season"] >= 2)
    for season in (2, 3):
        rows = [h for h in hist if h["season"] == season]
        assert sum(h["alive"] for h in rows) <= 8  # one pooled capacity, not two
        assert len({h["living_cost"] for h in rows}) == 1  # one arena, one living cost


def test_after_the_merge_a_fauna_can_take_more_than_its_own_capacity(tmp_path):
    eco = EcologyConfig(seasons=1, capacity=4, merge_after=0, pooled_capacity=8, living_cost=0.0, birth_threshold=0.0, birth_cost=0.0, max_age=1000, crossover_rate=0.0)
    e = Ecology(_quick_evo(), eco, out_dir=str(tmp_path), log=None)
    e.populations[CONVENTIONAL] = []  # the designed fauna dies out before the interchange
    e.step()
    assert len(e.populations[HOLISTIC]) == 8  # every free slot in the merged arena is open to it
    assert all(m.record["kind"] == HOLISTIC for m in e.populations[HOLISTIC])
    last = [h for h in e.history if h["season"] == 0]
    assert {h["population"]: h["alive"] for h in last} == {HOLISTIC: 8, CONVENTIONAL: 0}  # extinction is on the record


def test_merged_births_stay_within_their_own_fauna(tmp_path):
    eco = EcologyConfig(seasons=3, capacity=4, merge_after=0, pooled_capacity=12, living_cost=0.0, birth_threshold=0.05, birth_cost=0.01, max_age=1000, crossover_rate=1.0)
    e = Ecology(_quick_evo(), eco, out_dir=str(tmp_path), log=None)
    e.run()
    by_name = {m.name: m for kind in (HOLISTIC, CONVENTIONAL) for m in e.populations[kind]}
    children = [m for m in by_name.values() if m.parents]
    assert children
    for child in children:
        for parent in child.parents:
            if parent in by_name:  # a parent that outlived the child's birth
                assert by_name[parent].record["kind"] == child.record["kind"]


def test_merge_and_seed_flags_parse(tmp_path):
    from rabbitstew.cli import build_parser

    a = build_parser().parse_args(["ecology", "--merge-after", "40", "--pooled-capacity", "90", "--from-run", str(tmp_path)])
    assert (a.merge_after, a.pooled_capacity, a.from_run) == (40, 90, str(tmp_path))
    assert build_parser().parse_args(["ecology"]).merge_after is None


def test_analyze_run_on_an_ecology(tmp_path):
    from rabbitstew.analysis import TrialConfig, analyze_run

    evo = EvolutionConfig(seed=8, sim=SimConfig(duration=0.3, random_start=True, score="closeness"))
    eco = EcologyConfig(seasons=21, capacity=4, starvation=False, birth_threshold=100.0, living_cost=0.0, max_age=1000, stagger_ages=False)
    Ecology(evo, eco, out_dir=str(tmp_path), log=None).run()
    quick = TrialConfig(approach_duration=0.4, steering_bearings=(90.0,), steering_duration=0.4, terrain_seeds=(0,), terrain_duration=0.4, push_duration=0.4, lesion_duration=0.3)
    res = analyze_run(str(tmp_path), out_json=str(tmp_path / "a.json"), out_html=str(tmp_path / "a.html"), every=1, lesions="none", trials=quick, log=None)
    # an ecology only saves a best every tenth season, so those are the only seasons to analyse
    assert sorted({r["generation"] for r in res["individuals"]}) == [0, 10, 20]
    assert res["config"]["ecology"] is True and res["config"]["seasons"] == 21 and res["config"]["challenge"] == "solo"
    chain = res["lineage"][HOLISTIC]["chain"]
    assert all(k in chain[0] for k in ("energy", "age", "evals"))  # the ecology's own record, not the GA's
    assert res["lineage"][HOLISTIC]["cohort_generation"] == 20
    assert res["heritability"][HOLISTIC]["min_evals"] == 5  # a season's yield alone is the world's draw
    html = (tmp_path / "a.html").read_text()
    assert "saved season's best" in html and "the horizontal axis counts seasons" in html


def test_heritability_command_on_an_ecology_run(tmp_path, capsys):
    from rabbitstew.cli import main

    for name in ("run", "neutral"):
        evo = EvolutionConfig(seed=9, sim=SimConfig(duration=0.3, random_start=True, score="closeness"))
        eco = EcologyConfig(seasons=4, capacity=4, starvation=False, birth_threshold=0.0, birth_cost=0.0, living_cost=0.0, max_age=2, stagger_ages=False)
        Ecology(evo, eco, out_dir=str(tmp_path / name), log=None).run()
    run, neutral = str(tmp_path / "run"), str(tmp_path / "neutral")
    assert main(["heritability", run, "--drift-baseline", neutral, "--mutation", "4"]) == 0
    out = capsys.readouterr().out
    assert "lifetime mean yield, evals >= 5" in out and f"drift baseline {neutral}" in out
    assert "parent-child pairs under mutate" in out and "median descriptor r" in out


def test_founder_model_is_refused_for_an_ecology(tmp_path):
    import pytest

    from rabbitstew.cli import main

    evo = EvolutionConfig(seed=10, sim=SimConfig(duration=0.3, random_start=True, score="closeness"))
    Ecology(evo, EcologyConfig(seasons=1, capacity=3, max_age=1000), out_dir=str(tmp_path), log=None).run()
    with pytest.raises(SystemExit, match="--drift-baseline"):
        main(["heritability", str(tmp_path), "--founder-model"])
