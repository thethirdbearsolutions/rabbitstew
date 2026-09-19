"""Per-population and per-terrain RNG streams (RBT-85): an arm that changes one population's
reproduction must not move the other population's draws or the terrain sequence, or two runs
at one seed are not a pair (RBT-74: paired SE above unpaired, correlation -0.41)."""

import json

import pytest

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, STREAMS, TERRAIN, EvolutionConfig, Experiment, spawn_streams
from rabbitstew.simulation import SimConfig
from rabbitstew.world import WorldConfig


def _run(tmp_path, name, k, generations=7, seed=11):
    sim = SimConfig(duration=0.4, world=WorldConfig(terrain="random"))
    cfg = EvolutionConfig(population_size=6, generations=generations, champion_interval=3, champions=2, champion_mode="roundrobin", brain_model="rich", conventional_topology=True, morph_protection=k, seed=seed, sim=sim)
    out = tmp_path / name
    Experiment(cfg, out_dir=str(out), log=None).run()
    return out


def _lineage(out, kind):
    """The raw lineage lines of one population, as written."""
    return [l for l in (out / "lineage.jsonl").read_bytes().splitlines() if json.loads(l)["population"] == kind]


def _environment(out):
    hist = json.loads((out / "history.json").read_text())["history"]
    return [(e["generation"], e["terrain_seed"], e["start_seeds"]) for e in hist if e["population"] == HOLISTIC]


def test_arms_differing_in_holistic_reproduction_share_the_opponent_and_the_terrain(tmp_path):
    base = _run(tmp_path, "base", 0)
    prot = _run(tmp_path, "prot", 4)
    # The manipulation took: the holistic populations diverge (otherwise this test pins nothing).
    assert _lineage(base, HOLISTIC) != _lineage(prot, HOLISTIC)
    assert any(json.loads(l)["birth"] == "readapt" for l in _lineage(prot, HOLISTIC))
    # The wheeled population is the same population, byte for byte, names, parents and scores.
    assert _lineage(base, CONVENTIONAL) == _lineage(prot, CONVENTIONAL)
    assert len(_lineage(base, CONVENTIONAL)) == 7 * 6
    # Same terrains and start layouts, every generation.
    env = _environment(base)
    assert env == _environment(prot)
    assert len({t for _, t, _ in env}) == len(env) and all(t is not None for _, t, _ in env)


def test_founders_are_shared_across_arms(tmp_path):
    a = Experiment(EvolutionConfig(population_size=4, morph_protection=0, seed=5, sim=SimConfig(duration=0.3)), log=None)
    b = Experiment(EvolutionConfig(population_size=4, morph_protection=4, seed=5, sim=SimConfig(duration=0.3)), log=None)
    for kind in (HOLISTIC, CONVENTIONAL):
        assert [m.to_dict() for m in a.populations[kind].members] == [m.to_dict() for m in b.populations[kind].members]


def test_streams_are_independent_and_seeded():
    a, b = spawn_streams(7), spawn_streams(7)
    assert set(a) == set(STREAMS) == {HOLISTIC, CONVENTIONAL, TERRAIN}
    b[HOLISTIC].random(1000)  # one stream consumed; the others do not move
    for name in (CONVENTIONAL, TERRAIN):
        assert a[name].integers(0, 2**31 - 1, 8).tolist() == b[name].integers(0, 2**31 - 1, 8).tolist()
    draws = {name: spawn_streams(7)[name].integers(0, 2**31 - 1, 8).tolist() for name in STREAMS}
    assert len({tuple(v) for v in draws.values()}) == len(STREAMS)
    assert spawn_streams(8)[TERRAIN].integers(0, 2**31 - 1, 8).tolist() != draws[TERRAIN]


def test_resume_restores_every_stream(tmp_path):
    whole = _run(tmp_path, "whole", 4, generations=6)
    part = _run(tmp_path, "part", 4, generations=3)
    state = json.loads((part / "state.json").read_text())
    assert set(state["rngs"]) == set(STREAMS)
    Experiment.resume(str(part), generations=6, log=None).run()
    assert json.loads((part / "history.json").read_text()) == json.loads((whole / "history.json").read_text())
    # A resume re-evaluates the generation it stopped in and appends it to lineage.jsonl again, so compare the distinct lines.
    for kind in (HOLISTIC, CONVENTIONAL):
        assert list(dict.fromkeys(_lineage(part, kind))) == _lineage(whole, kind)


def test_resuming_a_single_stream_checkpoint_is_refused(tmp_path):
    part = _run(tmp_path, "old", 0, generations=3)
    state = json.loads((part / "state.json").read_text())
    state["rng"] = state.pop("rngs")[HOLISTIC]
    (part / "state.json").write_text(json.dumps(state))
    with pytest.raises(ValueError, match="RBT-85"):
        Experiment.resume(str(part), generations=6, log=None)
