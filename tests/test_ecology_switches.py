"""The ecology's three switches (RBT-95): per-population and terrain RNG streams with a checkpoint,
a mid-run onset (``shift_at``/``shift``) and a random cull (``cull_at``/``cull``).

Each test here was shown to fail on the code before its switch existed; the failures are quoted on
the ticket.  No result is read: these pin the mechanics the held-out challenge protocol
(``docs/held-out-challenges.md`` sections 5 and 8) needs.
"""

import json

import pytest

from rabbitstew.ecology import Ecology, EcologyConfig
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, STREAMS, EvolutionConfig
from rabbitstew.simulation import FoodConfig, SimConfig
from rabbitstew.world import WorldConfig


def _evo(seed=11):
    return EvolutionConfig(seed=seed, brain_model="foraging", conventional_topology=True,
                           sim=SimConfig(duration=0.3, random_start=True, score="food", world=WorldConfig(terrain="random"),
                                         food=FoodConfig(items=4, radius=1.5, eat_radius=0.4)))


def _eco(**kw):
    base = dict(seasons=4, capacity=4, challenge="foraging", group_size=2, max_age=1000, birth_threshold=100.0, log_every=1000)
    base.update(kw)
    return EcologyConfig(**base)


def _run(tmp_path, name, eco, seed=11):
    out = tmp_path / name
    Ecology(_evo(seed), eco, out_dir=str(out), log=None).run()
    return out


def _lineage(out, kind):
    return [l for l in (out / "lineage.jsonl").read_bytes().splitlines() if json.loads(l)["population"] == kind]


def _environment(out, kind=CONVENTIONAL):
    hist = json.loads((out / "history.json").read_text())["history"]
    return [(e["season"], e["terrain_seed"], e["start_seed"]) for e in hist if e["population"] == kind]


# --------------------------------------------------------------------------- #
# item 3: streams and the checkpoint
# --------------------------------------------------------------------------- #

def test_arms_differing_in_holistic_founders_share_the_conventional_fauna_and_the_terrain(tmp_path):
    """With the two fauna in separate arenas for the whole run (``merge_after`` past its length, said
    here on purpose): the designed-body side of two arms that differ on the holistic side is the same
    run, byte for byte, scores included, because nothing it scores against is holistic."""
    donor = _run(tmp_path, "donor", _eco(seasons=1), seed=3)
    base = _run(tmp_path, "base", _eco(merge_after=99))
    other = _run(tmp_path, "other", _eco(merge_after=99, seed_holistic=str(donor)))
    assert _lineage(base, HOLISTIC) != _lineage(other, HOLISTIC)  # the holistic-side flag took
    # The designed-body fauna is the same fauna, byte for byte, and meets the same worlds.
    assert _lineage(base, CONVENTIONAL) == _lineage(other, CONVENTIONAL)
    assert len(_lineage(base, CONVENTIONAL)) == 4 * 4
    env = _environment(base)
    assert env == _environment(other)
    assert len({t for _, t, _ in env}) == len(env) and all(t is not None for _, t, _ in env)


CONTEST = ("fitness", "energy", "last_score", "food", "work", "path", "exploded", "arena")  #: the fields a shared arena decides


def test_after_a_merge_the_comparator_shares_everything_but_the_contest(tmp_path):
    """Once the fauna share an arena the conventional side's scores depend on the holistic bodies it
    meets, so byte identity across holistic-side arms holds only up to ``merge_after``.  After it,
    what stays shared is the comparator's founders and ages, its own reproduction draws and the
    worlds; its income is a contest outcome and a covariate (runs/README.md, README rule seven)."""
    donor = _run(tmp_path, "donor", _eco(seasons=1), seed=3)
    base = _run(tmp_path, "base", _eco(seasons=4, merge_after=2))
    other = _run(tmp_path, "other", _eco(seasons=4, merge_after=2, seed_holistic=str(donor)))
    rows = lambda out: [json.loads(l) for l in _lineage(out, CONVENTIONAL)]
    b, o = rows(base), rows(other)
    assert [r for r in b if r["generation"] < 2] == [r for r in o if r["generation"] < 2]  # identical up to the merge
    after_b, after_o = [r for r in b if r["generation"] >= 2], [r for r in o if r["generation"] >= 2]
    assert after_b and [{k: v for k, v in r.items() if k not in CONTEST} for r in after_b] == [{k: v for k, v in r.items() if k not in CONTEST} for r in after_o]
    # the contest is against different bodies: the holistic founders the comparator meets are not the same genomes
    assert (base / HOLISTIC / "genomes" / "h0-0.json").read_bytes() != (other / HOLISTIC / "genomes" / "h0-0.json").read_bytes()
    pooled = lambda out: [json.loads(l)["cohort"] for l in (out / "cohorts.jsonl").read_bytes().splitlines() if json.loads(l)["season"] >= 2]
    assert pooled(base) and set(pooled(base)) == set(pooled(other)) == {"holistic+conventional"}
    assert _environment(base) == _environment(other)  # the worlds, every season, merged or not
    streams = lambda out: json.loads((out / "state.json").read_text())["rngs"]
    assert streams(base)[CONVENTIONAL] == streams(other)[CONVENTIONAL]  # the comparator's own stream is where the control's is
    assert streams(base)["terrain"] == streams(other)["terrain"]


def test_resume_restores_the_ecology_byte_for_byte(tmp_path):
    whole = _run(tmp_path, "whole", _eco(seasons=5))
    part = _run(tmp_path, "part", _eco(seasons=3))
    state = json.loads((part / "state.json").read_text())
    assert set(state["rngs"]) == set(STREAMS)
    Ecology.resume(str(part), seasons=5, log=None).run()
    for name in ("lineage.jsonl", "cohorts.jsonl", "history.json", "config.json"):
        assert (part / name).read_bytes() == (whole / name).read_bytes(), name


def test_resuming_a_single_stream_ecology_checkpoint_is_refused(tmp_path):
    part = _run(tmp_path, "old", _eco(seasons=2))
    state = json.loads((part / "state.json").read_text())
    state["rng"] = state.pop("rngs")[HOLISTIC]
    (part / "state.json").write_text(json.dumps(state))
    with pytest.raises(ValueError, match="RBT-95"):
        Ecology.resume(str(part), seasons=4, log=None)


# --------------------------------------------------------------------------- #
# item 1: the mid-run onset
# --------------------------------------------------------------------------- #

def _history(out):
    return json.loads((out / "history.json").read_text())["history"]


def _groups(out, season):
    rows = [json.loads(l) for l in (out / "cohorts.jsonl").read_text().splitlines()]
    return [len(g) for r in rows if r["season"] == season and r["cohort"] == HOLISTIC for g in r["groups"]]


def test_a_shift_past_the_run_is_a_no_op_byte_for_byte(tmp_path):
    base = _run(tmp_path, "base", _eco())
    late = _run(tmp_path, "late", _eco(shift_at=99, shift="group_size=1"))
    for name in ("lineage.jsonl", "cohorts.jsonl", "history.json"):
        assert (base / name).read_bytes() == (late / name).read_bytes(), name
    assert json.loads((late / "config.json").read_text())["ecology"]["shift"] == "group_size=1"


def test_a_shift_changes_one_parameter_in_place_from_its_season_on(tmp_path):
    control = _run(tmp_path, "control", _eco(seasons=5))
    shifted = _run(tmp_path, "shifted", _eco(seasons=5, shift_at=3, shift="group_size=1"))
    before = lambda out: [l for l in (out / "lineage.jsonl").read_bytes().splitlines() if json.loads(l)["generation"] < 3]
    assert before(control) == before(shifted) and len(before(control)) == 3 * 8
    # the record: absent before the onset and in the control, present from the onset on
    assert all("shift" not in e for e in _history(control))
    assert all(("shift" in e) == (e["season"] >= 3) for e in _history(shifted))
    assert {json.dumps(e["shift"], sort_keys=True) for e in _history(shifted) if e["season"] >= 3} == {json.dumps({"at": 3, "flag": "group_size", "value": 1}, sort_keys=True)}
    # exactly the one parameter moved: groups of two until season 3, of one from it
    assert _groups(shifted, 2) == [2, 2] and _groups(shifted, 3) == [1, 1, 1, 1] and _groups(control, 3) == [2, 2]
    # and the individuals carried across the onset are the same individuals, one season older
    rows = lambda out, s: {json.loads(l)["name"]: json.loads(l) for l in (out / "lineage.jsonl").read_bytes().splitlines() if json.loads(l)["generation"] == s}
    at2, at3 = rows(shifted, 2), rows(shifted, 3)
    assert set(at3) == set(at2)  # breeding is off and nobody dies: the population is the population
    assert all(at3[n]["age"] == at2[n]["age"] + 1 and at3[n]["evals"] == at2[n]["evals"] + 1 and at3[n]["parents"] == at2[n]["parents"] for n in at3)


def test_a_simulator_field_shifts_by_dotted_path_and_bad_shifts_are_refused(tmp_path):
    e = Ecology(_evo(), _eco(seasons=3, shift_at=1, shift="food.items=2"), out_dir=str(tmp_path / "food"), log=None)
    assert e.evo.sim.food.items == 4
    e.run()
    assert e.evo.sim.food.items == 2 and isinstance(e.evo.sim.food.items, int)
    assert [e_["shift"]["value"] for e_ in _history(tmp_path / "food") if e_["season"] >= 1] == [2] * 4
    # RBT-89's challenge flags by their CLI names, recorded under the field they set
    for spoken, flag, value in (("group-size=1", "group_size", 1), ("work-cost=0.08", "food.work_cost", 0.08), ("food-items=2", "food.items", 2), ("terrain=flat", "world.terrain", "flat")):
        e2 = Ecology(_evo(), _eco(seasons=2, shift_at=1, shift=spoken), out_dir=str(tmp_path / spoken.split("=")[0]), log=None)
        e2.run()
        assert [h["shift"] for h in _history(tmp_path / spoken.split("=")[0]) if h["season"] == 1][0] == {"at": 1, "flag": flag, "value": value}
    for bad in ("nonsense=1", "capacity=3", "food.nonsense=1", "group_size", "seasons=9"):
        with pytest.raises(ValueError):
            Ecology(_evo(), _eco(shift_at=1, shift=bad), log=None)
    with pytest.raises(ValueError):  # one without the other
        Ecology(_evo(), _eco(shift="group_size=1"), log=None)


# --------------------------------------------------------------------------- #
# item 2: the random cull
# --------------------------------------------------------------------------- #

def _rows(out, pred):
    return [json.loads(l) for l in (out / "lineage.jsonl").read_bytes().splitlines() if pred(json.loads(l))]


def test_a_cull_removes_each_faunas_count_at_its_season_records_them_as_deaths_and_moves_nothing_else(tmp_path):
    """The protocol's k is each fauna's own excess deaths, so the counts differ and one is often 0
    (section 8): here 2 holistic and 0 conventional.  The fauna at 0 draws nothing, so its stream,
    its lineage and its cohorts are the control's to the byte for the whole run."""
    control = _run(tmp_path, "control", _eco(seasons=5))
    culled = _run(tmp_path, "culled", _eco(seasons=5, cull_at=3, cull="holistic=2,conventional=0"))
    before = lambda out: [l for l in (out / "lineage.jsonl").read_bytes().splitlines() if json.loads(l)["generation"] < 3]
    assert before(control) == before(culled) and len(before(control)) == 3 * 8
    assert [e for e in _history(control) if e["season"] < 3] == [e for e in _history(culled) if e["season"] < 3]
    ctl = {(e["season"], e["population"]): e for e in _history(control)}
    for e in _history(culled):
        c = ctl[(e["season"], e["population"])]
        n = {HOLISTIC: 2, CONVENTIONAL: 0}[e["population"]]
        if e["season"] == 3:
            assert e["alive"] == c["alive"] - n and e["deaths"] == c["deaths"] + n and e["culled"] == {HOLISTIC: 2, CONVENTIONAL: 0}
        else:
            assert "culled" not in e
        assert (e["terrain_seed"], e["start_seed"]) == (c["terrain_seed"], c["start_seed"])  # the cull drew from the fauna's stream, not the terrain's
    dead = _rows(culled, lambda r: r["population"] == HOLISTIC and r.get("death") == "cull")
    assert len(dead) == 2 and all(r["generation"] == 3 for r in dead)
    alive_after = {r["name"] for r in _rows(culled, lambda r: r["population"] == HOLISTIC and r["generation"] >= 3 and "death" not in r)}
    assert not {r["name"] for r in dead} & alive_after  # gone, and not cloned back
    assert len(_rows(culled, lambda r: r["population"] == HOLISTIC and r["generation"] == 4)) == 2  # slots stay free: breeding is off
    # the fauna culled by 0: no cull rows, and the same fauna as the control's, byte for byte, every season
    assert not _rows(culled, lambda r: r["population"] == CONVENTIONAL and "death" in r)
    assert _lineage(culled, CONVENTIONAL) == _lineage(control, CONVENTIONAL)
    conv_cohorts = lambda out: [l for l in (out / "cohorts.jsonl").read_bytes().splitlines() if json.loads(l)["cohort"] == CONVENTIONAL]
    assert conv_cohorts(culled) == conv_cohorts(control)
    streams = lambda out: json.loads((out / "state.json").read_text())["rngs"]
    assert streams(culled)[CONVENTIONAL] == streams(control)[CONVENTIONAL] and streams(culled)[HOLISTIC] != streams(control)[HOLISTIC]
    assert json.loads((culled / "config.json").read_text())["ecology"]["cull"] == "holistic=2,conventional=0"


def test_a_cull_larger_than_the_fauna_takes_everyone_and_bad_culls_are_refused(tmp_path):
    out = _run(tmp_path, "all", _eco(seasons=3, cull_at=1, cull="99"))  # a bare N: N of each fauna
    # Every individual of both fauna is written as culled at season 1 ...
    assert len(_rows(out, lambda r: r.get("death") == "cull" and r["generation"] == 1)) == 8
    assert not _rows(out, lambda r: r["generation"] >= 1 and "death" not in r)
    # ... and, as for any season nobody survives, no history row is written and the run stops (pre-existing: an
    # empty cohort records nothing), so a total cull is read from the lineage.  The protocol's k is never the fauna.
    assert [e["season"] for e in _history(out)] == [0, 0]
    for kw in (dict(cull_at=1), dict(cull="2"), dict(cull_at=1, cull="-1"), dict(cull_at=1, cull="wheels=1"), dict(cull_at=1, cull="holistic=0,conventional=0"), dict(cull_at=1, cull="two")):
        with pytest.raises(ValueError):
            Ecology(_evo(), _eco(**kw), log=None)


# --------------------------------------------------------------------------- #
# the adversaries' rounds (RBT-95, 16:44 and 16:47 UTC): what they broke, pinned
# --------------------------------------------------------------------------- #

def _breeding_eco(**kw):
    """The item-3 adversary's configuration: breeding on (threshold under the founders' energy), deaths on, crossover on."""
    base = dict(seasons=6, capacity=6, challenge="foraging", group_size=2, max_age=5, initial_energy=2.0,
                birth_threshold=1.2, birth_cost=0.5, living_cost=0.05, crossover_rate=0.5, log_every=1000)
    base.update(kw)
    return EcologyConfig(**base)


def test_a_flat_terrain_shift_keeps_the_start_seeds_paired_with_the_control(tmp_path):
    """C4 (--terrain flat): with no terrain seed to draw, the shifted arm fell one draw behind the control per season
    and its start seeds diverged from the onset (items 1-2 adversary, probe 1).  The terrain stream is now drawn once
    a season whatever the terrain, so the flat arm meets the control's start layouts."""
    control = _run(tmp_path, "control", _eco(seasons=5))
    flat = _run(tmp_path, "flat", _eco(seasons=5, shift_at=2, shift="terrain=flat"))
    c = {(e["season"], e["population"]): e for e in _history(control)}
    for e in _history(flat):
        assert e["start_seed"] == c[(e["season"], e["population"])]["start_seed"]
        assert (e["terrain_seed"] is None) == (e["season"] >= 2)


def test_a_torn_final_lineage_line_is_dropped_on_resume(tmp_path):
    """A kill mid-write leaves a cut last row; it belongs to the unfinished season the resume drops anyway (item-3 adversary, P4)."""
    whole = _run(tmp_path, "whole", _eco(seasons=5))
    part = _run(tmp_path, "part", _eco(seasons=3))
    data = (part / "lineage.jsonl").read_bytes()
    (part / "lineage.jsonl").write_bytes(data + data.splitlines()[-1][:-37])  # a torn copy of the last row, no newline
    Ecology.resume(str(part), seasons=5, log=None).run()
    assert (part / "lineage.jsonl").read_bytes() == (whole / "lineage.jsonl").read_bytes()
    with pytest.raises(ValueError, match="lineage.jsonl"):  # a torn line anywhere else is still refused
        (part / "lineage.jsonl").write_bytes(data.splitlines()[0][:-20] + b"\n" + data)
        Ecology.resume(str(part), seasons=6, log=None)


def test_a_resume_keeps_the_seed_paths_in_config(tmp_path):
    """resume() nulled seed_from/seed_holistic/seed_conventional and wrote that to config.json, so a resumed seeded run's
    config said its founders were generated (item-3 adversary, P5).  The paths are nulled in memory only."""
    donor = _run(tmp_path, "donor", _eco(seasons=1), seed=3)
    whole = _run(tmp_path, "whole", _eco(seasons=5, seed_holistic=str(donor)))
    part = _run(tmp_path, "part", _eco(seasons=3, seed_holistic=str(donor)))
    Ecology.resume(str(part), seasons=5, log=None).run()
    assert json.loads((part / "config.json").read_text())["ecology"]["seed_holistic"] == str(donor)
    for name in ("config.json", "lineage.jsonl", "history.json"):
        assert (part / name).read_bytes() == (whole / name).read_bytes(), name


def test_malformed_checkpoints_are_refused_with_one_message(tmp_path):
    part = _run(tmp_path, "part", _eco(seasons=2))
    state = json.loads((part / "state.json").read_text())
    state["rngs"].pop("terrain")
    (part / "state.json").write_text(json.dumps(state))
    with pytest.raises(ValueError, match="terrain.*RBT-95"):
        Ecology.resume(str(part), seasons=4, log=None)
    arena = tmp_path / "arena"
    arena.mkdir()
    (arena / "config.json").write_text(json.dumps({k: v for k, v in json.loads((part / "config.json").read_text()).items() if k != "ecology"}))
    (arena / "state.json").write_text("{}")
    with pytest.raises(ValueError, match="not an ecology run"):
        Ecology.resume(str(arena), log=None)


def test_regrow_delay_cannot_be_shifted(tmp_path):
    """Ecology.persistent is fixed at construction, so a shift of food.regrow_delay would run a persistent world with no arenas (items 1-2 adversary, probe 2)."""
    with pytest.raises(ValueError, match="regrow_delay"):
        Ecology(_evo(), _eco(shift_at=1, shift="food.regrow_delay=45"), log=None)


def test_a_resume_can_take_the_trait_predicate_back(tmp_path):
    trait = lambda g: float(len(g.nodes))
    whole = tmp_path / "whole"
    Ecology(_evo(), _eco(seasons=5), out_dir=str(whole), log=None, trait=trait, trait_threshold=3.0, trait_name="nodes").run()
    part = tmp_path / "part"
    Ecology(_evo(), _eco(seasons=3), out_dir=str(part), log=None, trait=trait, trait_threshold=3.0, trait_name="nodes").run()
    Ecology.resume(str(part), seasons=5, log=None, trait=trait, trait_threshold=3.0, trait_name="nodes").run()
    assert all("carriers" in e for e in _history(part))
    assert (part / "history.json").read_bytes() == (whole / "history.json").read_bytes()


def test_with_reproduction_on_the_pair_and_the_resume_still_hold(tmp_path):
    """The item-3 tests above breed nobody; the adversary showed the pairing and the resume hold with reproduction on, and this pins it."""
    donor = _run(tmp_path, "donor", _eco(seasons=1), seed=3)
    base = _run(tmp_path, "base", _breeding_eco(merge_after=99))
    other = _run(tmp_path, "other", _breeding_eco(merge_after=99, seed_holistic=str(donor)))
    conv = [json.loads(l) for l in _lineage(base, CONVENTIONAL)]
    assert any(r["parents"] for r in conv) and any(r["age"] == 0 for r in conv)  # children were born and logged
    assert _lineage(base, CONVENTIONAL) == _lineage(other, CONVENTIONAL) and _lineage(base, HOLISTIC) != _lineage(other, HOLISTIC)
    assert sorted(p.name for p in (base / CONVENTIONAL / "genomes").iterdir()) == sorted(p.name for p in (other / CONVENTIONAL / "genomes").iterdir())
    whole = _run(tmp_path, "whole", _breeding_eco(seasons=6))
    part = _run(tmp_path, "part", _breeding_eco(seasons=3))
    Ecology.resume(str(part), seasons=6, log=None).run()
    for name in ("lineage.jsonl", "cohorts.jsonl", "history.json"):
        assert (part / name).read_bytes() == (whole / name).read_bytes(), name
    for kind in (HOLISTIC, CONVENTIONAL):
        files = sorted(p.name for p in (whole / kind / "genomes").iterdir())
        assert files == sorted(p.name for p in (part / kind / "genomes").iterdir())
        assert all((whole / kind / "genomes" / f).read_bytes() == (part / kind / "genomes" / f).read_bytes() for f in files)
