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
