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


# --- RBT-27 (reproducibility and telemetry) and RBT-30 (the explosion forfeit) --- #


def _forage_evo(duration: float = 0.4):
    from rabbitstew.simulation import FoodConfig

    return EvolutionConfig(seed=1, brain_model="foraging", conventional_topology=True,
                           sim=SimConfig(duration=duration, random_start=True, score="food",
                                         food=FoodConfig(items=5, radius=1.5, eat_radius=0.4, work_cost=0.03)))


def test_a_season_records_who_shared_each_arena(tmp_path):
    eco = EcologyConfig(seasons=3, capacity=8, challenge="foraging", group_size=4, max_age=1000, log_every=1000)
    e = Ecology(_forage_evo(), eco, out_dir=str(tmp_path), log=None)
    e.run()
    rows = [json.loads(l) for l in (tmp_path / "cohorts.jsonl").read_text().splitlines()]
    assert {r["season"] for r in rows} == {0, 1, 2}
    for r in rows:
        assert r["challenge"] == "foraging"
        assert sum(len(g) for g in r["groups"]) == 8  # everyone alive faced the season, once
        assert all(len(g) <= 4 for g in r["groups"])
        seats = [seat for g in r["groups"] for seat in g]
        assert len({s["name"] for s in seats}) == len(seats)  # nobody sits in two arenas
        assert {s["kind"] for s in seats} == {r["cohort"]}  # before the merge a cohort is one fauna
    # the draw actually varies between seasons: it is a record, not a formula
    by_season = {r["season"]: [sorted(s["name"] for s in g) for g in r["groups"]] for r in rows if r["cohort"] == HOLISTIC}
    assert by_season[0] != by_season[1] or by_season[1] != by_season[2]


def test_every_individual_is_saved_once_when_it_is_born(tmp_path):
    eco = EcologyConfig(seasons=4, capacity=6, challenge="foraging", group_size=3, max_age=2, birth_threshold=0.0, birth_cost=0.0, living_cost=0.0, log_every=1000)
    e = Ecology(_forage_evo(), eco, out_dir=str(tmp_path), log=None)
    e.run()
    lineage = [json.loads(l) for l in (tmp_path / "lineage.jsonl").read_text().splitlines()]
    ever = {(r["population"], r["name"]) for r in lineage}
    assert len(ever) > 6  # deaths at age 2 force births, so the run outlives its founders
    for kind, name in ever:
        assert (tmp_path / kind / "genomes" / f"{name}.json").exists(), f"{kind}/{name} was never saved"
    # and the saved genotype is the individual, loadable on its own
    kind, name = sorted(ever)[0]
    assert Genotype.load(str(tmp_path / kind / "genomes" / f"{name}.json")).is_valid()


def test_a_recorded_season_can_be_rerun_and_gives_the_same_numbers(tmp_path):
    """The point of the record: rebuild a season's arena from disk alone and get its result back."""
    from rabbitstew.gallery import season_arena
    from rabbitstew.simulation import run_group

    evo = _forage_evo()
    eco = EcologyConfig(seasons=2, capacity=4, challenge="foraging", group_size=4, max_age=1000, log_every=1000)
    Ecology(evo, eco, out_dir=str(tmp_path), log=None).run()
    cohorts = [json.loads(l) for l in (tmp_path / "cohorts.jsonl").read_text().splitlines()]
    lineage = {(r["generation"], r["population"], r["name"]): r for r in (json.loads(l) for l in (tmp_path / "lineage.jsonl").read_text().splitlines())}

    season = 0
    rows = [r for r in cohorts if r["season"] == season and r["cohort"] == HOLISTIC]
    arena = season_arena(rows, None, str(tmp_path))
    assert arena is not None and len(arena["members"]) == 4
    again = run_group(arena["members"], evo.sim, start_seed=arena["start_seed"])
    for seat, got in zip(arena["seats"], again):
        was = lineage[(season, seat["kind"], seat["name"])]
        # exact at the log's own precision: the lineage row rounds to four places
        assert round(got["food"], 4) == was["food"]
        assert round(got["work"], 4) == was["work"]
        assert round(got["score"], 4) == was["last_score"]


def test_the_lineage_row_carries_the_season_not_just_its_gain(tmp_path):
    eco = EcologyConfig(seasons=2, capacity=4, challenge="foraging", group_size=4, max_age=1000, log_every=1000)
    Ecology(_forage_evo(), eco, out_dir=str(tmp_path), log=None).run()
    rows = [json.loads(l) for l in (tmp_path / "lineage.jsonl").read_text().splitlines()]
    assert rows and all({"food", "work", "path", "exploded"} <= set(r) for r in rows)
    assert all("distance" not in r for r in rows)  # no hardcoded hole: a foraging season has no distance to a target
    assert all(isinstance(r["exploded"], bool) for r in rows)


def test_a_solo_season_records_its_distance_instead(tmp_path):
    evo = EvolutionConfig(seed=3, brain_model="rich", conventional_topology=True, sim=SimConfig(duration=0.3, random_start=True, score="closeness"))
    Ecology(evo, EcologyConfig(seasons=1, capacity=3, challenge="solo", max_age=1000, log_every=1000), out_dir=str(tmp_path), log=None).run()
    rows = [json.loads(l) for l in (tmp_path / "lineage.jsonl").read_text().splitlines()]
    assert rows and all({"distance", "time_at_target", "exploded"} <= set(r) for r in rows)
    assert all(r["distance"] is not None for r in rows)  # the field the ecology used to write as null
    assert all("food" not in r for r in rows)  # and nothing a solo season does not measure


def test_an_exploded_individual_forfeits_the_season(tmp_path):
    """RBT-30: no items, no work, so its energy moves by the living cost alone and the record says why."""
    eco = EcologyConfig(seasons=1, capacity=4, challenge="foraging", group_size=4, living_cost=0.25, initial_energy=3.0, max_age=1000, log_every=1000)
    e = Ecology(_forage_evo(), eco, out_dir=str(tmp_path), log=None)
    real = e._challenge

    def blow_up(members, sim, start_seed, key=()):
        rows = real(members, sim, start_seed, key)
        rows[0] = e._gain({**rows[0], "food": 9.0, "work": 1.5e9, "exploded": True})
        return rows

    e._challenge = blow_up
    e.step()
    victim = e.populations[HOLISTIC][0]
    assert victim.record["last_score"] == 0.0
    assert victim.record["energy"] == 3.0 - 0.25  # the living cost and nothing else
    row = [json.loads(l) for l in (tmp_path / "lineage.jsonl").read_text().splitlines()][0]
    assert row["exploded"] is True and row["last_score"] == 0.0


def test_carrier_fraction_is_logged_over_the_living_population(tmp_path):
    """RBT-79: a caller-supplied scalar, summarised into every season's history entry."""
    eco = EcologyConfig(seasons=3, capacity=6, living_cost=0.3, birth_threshold=0.6, birth_cost=0.3,
                        max_age=4, initial_energy=0.7, stagger_ages=False)
    seen = []

    def gain(g):
        seen.append(g.name)
        return float(len(g.name))                      # any scalar of the genotype will do

    e = Ecology(_quick_evo(), eco, out_dir=str(tmp_path), log=None,
                trait=gain, trait_threshold=4.0, trait_name="name_length>=4")
    hist = e.run()["history"]
    assert any(h["alive"] for h in hist)
    for h in hist:
        assert h["trait"] == "name_length>=4" and h["trait_threshold"] == 4.0
        assert 0 <= h["carriers"] <= h["alive"]
        if not h["alive"]:                              # an extinct population still records a row
            assert h["carriers"] == 0 and h["carrier_fraction"] == 0.0
            continue
        assert h["carrier_fraction"] == pytest.approx(h["carriers"] / h["alive"])
        assert h["trait_min"] <= h["trait_median"] <= h["trait_max"]
        assert h["trait_q1"] <= h["trait_median"] <= h["trait_q3"]
    on_disk = json.loads((tmp_path / "history.json").read_text())["history"]
    assert all("carriers" in h for h in on_disk)        # it reaches the file, not just the return
    assert len(seen) == len(set(seen))                  # cached: a genotype is measured once, ever


def test_no_trait_predicate_leaves_the_history_entry_exactly_as_it_was(tmp_path):
    """The hook is opt-in: a run that does not pass one must record what it always recorded."""
    eco = EcologyConfig(seasons=2, capacity=5, living_cost=0.3, birth_threshold=0.6, birth_cost=0.3,
                        max_age=4, initial_energy=0.7, stagger_ages=False)
    hist = Ecology(_quick_evo(), eco, out_dir=str(tmp_path), log=None).run()["history"]
    for h in hist:
        assert not {"trait", "carriers", "carrier_fraction", "trait_median"} & set(h)


def test_the_champion_over_reports_carriage_and_the_population_count_does_not(tmp_path):
    """The defect this ticket exists for, demonstrated rather than described.

    The saved champion is picked on `best_lifetime_score`, so for a trait that correlates with
    scoring well it is a biased witness -- in a drift arm as much as a selected one, which is what
    cost RBT-65 its control.  Here the trait is made to correlate with the lifetime score exactly:
    carriers are the individuals scoring at or above the population median.  The champion is a
    carrier by construction, while the population count reports the true half.
    """
    # Nobody dies and nobody breeds, so the population is a stable eight with lifetime scores that
    # differ: the bias under test is the readout's, not the demography's.
    eco = EcologyConfig(seasons=3, capacity=8, living_cost=0.0, birth_threshold=100.0,
                        max_age=1000, initial_energy=1.0, stagger_ages=False)
    e = Ecology(_quick_evo(seed=11), eco, out_dir=str(tmp_path), log=None)
    checked = 0

    def scores(kind):
        return {m.name: m.record["score_sum"] / max(1, m.record["evals"]) for m in e.populations[kind]}

    for _ in range(eco.seasons):
        e.step()
    for kind in (HOLISTIC, CONVENTIONAL):
        s = scores(kind)
        if len(s) < 4:
            continue
        median = sorted(s.values())[len(s) // 2]
        e.trait, e.trait_threshold, e.trait_name = (lambda m: float(s[m.name])), median, "score>=median"
        e._trait_cache = {}
        summary = e._trait_summary(e.populations[kind])
        champion = max(e.populations[kind], key=lambda m: s[m.name])
        assert s[champion.name] >= median                       # the champion always carries it
        assert summary["carrier_fraction"] < 1.0                # the population plainly does not
        assert summary["carriers"] == sum(v >= median for v in s.values())
        checked += 1
    assert checked, "neither population survived long enough to check"
