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
    # Byte for byte (RBT-93): the resumed run re-evaluates the generation it stopped in, and must not log it twice.
    assert (part / "lineage.jsonl").read_bytes() == (whole / "lineage.jsonl").read_bytes()


def test_resume_discards_a_generation_logged_before_a_kill(tmp_path):
    """A kill after one population's lineage was written but before the state was saved (RBT-93): the resume re-evaluates
    that generation, so the lines it already wrote are the ones that would be duplicated."""
    whole = _run(tmp_path, "whole", 4, generations=6)
    part = _run(tmp_path, "part", 4, generations=3)
    restart = json.loads((part / "state.json").read_text())["populations"][HOLISTIC]["generation"]
    partial = [l for l in _lineage(whole, HOLISTIC) if json.loads(l)["generation"] == restart]
    assert partial  # the killed attempt got as far as logging the holistic side of the restart generation
    with open(part / "lineage.jsonl", "ab") as f:
        f.write(b"\n".join(partial) + b"\n")
    Experiment.resume(str(part), generations=6, log=None).run()
    assert (part / "lineage.jsonl").read_bytes() == (whole / "lineage.jsonl").read_bytes()


def test_resuming_a_single_stream_checkpoint_is_refused(tmp_path):
    part = _run(tmp_path, "old", 0, generations=3)
    state = json.loads((part / "state.json").read_text())
    state["rng"] = state.pop("rngs")[HOLISTIC]
    (part / "state.json").write_text(json.dumps(state))
    with pytest.raises(ValueError, match="RBT-85"):
        Experiment.resume(str(part), generations=6, log=None)


def _run_salted(tmp_path, name, salt, generations=6, seed=11):
    sim = SimConfig(duration=0.4, world=WorldConfig(terrain="random"))
    cfg = EvolutionConfig(population_size=6, generations=generations, champion_interval=3, champions=2, champion_mode="roundrobin", brain_model="rich", conventional_topology=True, holistic_stream_salt=salt, seed=seed, sim=sim)
    out = tmp_path / name
    Experiment(cfg, out_dir=str(out), log=None).run()
    return out


def test_holistic_stream_salt_moves_only_the_holistic_stream(tmp_path):
    """The arena's A/A pair (RBT-96): two runs at one seed that differ only in the holistic stream's spawn.
    The wheeled population and the terrains must be byte-identical across salts, and the holistic lineage must differ."""
    a = _run_salted(tmp_path, "salt0", 0)
    b = _run_salted(tmp_path, "salt1", 1)
    assert _lineage(a, CONVENTIONAL) == _lineage(b, CONVENTIONAL)
    assert len(_lineage(a, CONVENTIONAL)) == 6 * 6
    assert _environment(a) == _environment(b)
    assert _lineage(a, HOLISTIC) != _lineage(b, HOLISTIC)
    assert json.loads((b / "config.json").read_text())["holistic_stream_salt"] == 1


def test_holistic_stream_salt_zero_is_the_unsalted_stream():
    """Salt 0 is today's streams exactly, so every run before RBT-96 reproduces from its config; a non-zero salt
    gives a holistic stream distinct from all three unsalted streams and from other salts, leaving the others put."""
    plain, zero = spawn_streams(7), spawn_streams(7, holistic_salt=0)
    for name in STREAMS:
        assert plain[name].integers(0, 2**31 - 1, 8).tolist() == zero[name].integers(0, 2**31 - 1, 8).tolist()
    unsalted = {name: tuple(spawn_streams(7)[name].integers(0, 2**31 - 1, 8).tolist()) for name in STREAMS}
    salted = [spawn_streams(7, holistic_salt=s) for s in (1, 2)]
    for s in salted:
        for name in (CONVENTIONAL, TERRAIN):
            assert tuple(s[name].integers(0, 2**31 - 1, 8).tolist()) == unsalted[name]
    h = [tuple(s[HOLISTIC].integers(0, 2**31 - 1, 8).tolist()) for s in salted]
    assert len(set(h) | set(unsalted.values())) == len(STREAMS) + 2
