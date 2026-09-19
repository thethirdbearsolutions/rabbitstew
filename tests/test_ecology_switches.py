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
    donor = _run(tmp_path, "donor", _eco(seasons=1), seed=3)
    base = _run(tmp_path, "base", _eco())
    other = _run(tmp_path, "other", _eco(seed_holistic=str(donor)))
    assert _lineage(base, HOLISTIC) != _lineage(other, HOLISTIC)  # the holistic-side flag took
    # The designed-body fauna is the same fauna, byte for byte, and meets the same worlds.
    assert _lineage(base, CONVENTIONAL) == _lineage(other, CONVENTIONAL)
    assert len(_lineage(base, CONVENTIONAL)) == 4 * 4
    env = _environment(base)
    assert env == _environment(other)
    assert len({t for _, t, _ in env}) == len(env) and all(t is not None for _, t, _ in env)


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


def test_a_cull_removes_n_at_its_season_records_them_as_deaths_and_moves_nothing_else(tmp_path):
    control = _run(tmp_path, "control", _eco(seasons=5))
    culled = _run(tmp_path, "culled", _eco(seasons=5, cull_at=3, cull=2))
    before = lambda out: [l for l in (out / "lineage.jsonl").read_bytes().splitlines() if json.loads(l)["generation"] < 3]
    assert before(control) == before(culled) and len(before(control)) == 3 * 8
    assert [e for e in _history(control) if e["season"] < 3] == [e for e in _history(culled) if e["season"] < 3]
    ctl = {(e["season"], e["population"]): e for e in _history(control)}
    for e in _history(culled):
        c = ctl[(e["season"], e["population"])]
        if e["season"] == 3:
            assert e["alive"] == c["alive"] - 2 and e["deaths"] == c["deaths"] + 2 and e["culled"] == 2
        else:
            assert "culled" not in e
        assert (e["terrain_seed"], e["start_seed"]) == (c["terrain_seed"], c["start_seed"])  # the cull drew from the fauna's stream, not the terrain's
    for kind in (HOLISTIC, CONVENTIONAL):
        dead = _rows(culled, lambda r: r["population"] == kind and r.get("death") == "cull")
        assert len(dead) == 2 and all(r["generation"] == 3 for r in dead)
        names = {r["name"] for r in dead}
        alive_after = {r["name"] for r in _rows(culled, lambda r: r["population"] == kind and r["generation"] >= 3 and "death" not in r)}
        assert not names & alive_after  # gone, and not cloned back
        assert len([r for r in _rows(culled, lambda r: r["population"] == kind and r["generation"] == 4)]) == 2  # slots stay free: breeding is off
    assert json.loads((culled / "config.json").read_text())["ecology"]["cull"] == 2


def test_a_cull_larger_than_the_fauna_takes_everyone_and_bad_culls_are_refused(tmp_path):
    out = _run(tmp_path, "all", _eco(seasons=3, cull_at=1, cull=99))
    # Every individual of both fauna is written as culled at season 1 ...
    assert len(_rows(out, lambda r: r.get("death") == "cull" and r["generation"] == 1)) == 8
    assert not _rows(out, lambda r: r["generation"] >= 1 and "death" not in r)
    # ... and, as for any season nobody survives, no history row is written and the run stops (pre-existing: an
    # empty cohort records nothing), so a total cull is read from the lineage.  The protocol's k is never the fauna.
    assert [e["season"] for e in _history(out)] == [0, 0]
    for kw in (dict(cull_at=1), dict(cull=2), dict(cull_at=1, cull=-1)):
        with pytest.raises(ValueError):
            Ecology(_evo(), _eco(**kw), log=None)
