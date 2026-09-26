"""RBT-96: salt 0 is the pre-salt holistic stream, pinned independently of the function under test
(the RBT-96 adversary's item 4, runs/RBT-96/adversary/test_salt0_golden.py on results/RBT-96-adversary).

Both of the PR's tests compare the new ``spawn_streams`` with itself (salt 0 against the default,
which is also 0), so a mutant that re-spawns the holistic stream at spawn key (i, 0) even for salt 0
passes all eight tests in tests/test_rng_streams.py while changing every earlier run's holistic
population (shown in item4.txt).  This pins salt 0 to the pre-salt construction, written out
independently of the function under test, and to literal draws recorded from the pre-salt code
(merge-base 852dcac).

    python -m pytest -q tests/test_salt0_golden.py
"""
import numpy as np

from rabbitstew.evolution import STREAMS, spawn_streams

# first four integers(0, 2**31 - 1) of each stream at seed 201, recorded on the pre-salt code (852dcac);
# the terrain draws are also s0-201's and s1-201's committed terrain seeds for generations 0-3
RECORDED_201 = {
    "holistic": [864646549, 1707149727, 276336530, 783501909],
    "conventional": [918441808, 1596473044, 1082716655, 2005663673],
    "terrain": [1060457471, 205314379, 555074330, 2137071901],
}


def _pre_salt(seed):
    return {name: np.random.default_rng(ss) for name, ss in zip(STREAMS, np.random.SeedSequence(seed).spawn(len(STREAMS)))}


def test_salt_zero_is_the_pre_salt_construction():
    for seed in (7, 201, 204):
        for salt_kw in ({}, {"holistic_salt": 0}):
            new, old = spawn_streams(seed, **salt_kw), _pre_salt(seed)
            for name in STREAMS:
                assert new[name].integers(0, 2**31 - 1, 8).tolist() == old[name].integers(0, 2**31 - 1, 8).tolist(), (seed, name, salt_kw)


def test_salt_zero_matches_recorded_draws():
    got = {name: spawn_streams(201)[name].integers(0, 2**31 - 1, 4).tolist() for name in STREAMS}
    assert got == RECORDED_201



def test_salt_zero_config_is_the_pre_salt_config_byte_for_byte(tmp_path):
    """A salt-0 config.json carries no holistic_stream_salt key, so it is byte-identical to one the pre-salt code
    wrote and tooling that compares configs does not see a difference (RBT-96 coordinator ruling item 2).
    RBT-85's base-201 config.json was written by the pre-salt code; re-writing it through this code must not move a byte."""
    import json
    import os

    from rabbitstew.evolution import EvolutionConfig, Experiment, _jsonable

    path = os.path.join(os.path.dirname(__file__), "..", "runs", "RBT-85", "base-201", "config.json")
    raw = open(path).read()
    assert "holistic_stream_salt" not in raw
    assert json.dumps(_jsonable(EvolutionConfig.from_dict(json.loads(raw)).to_dict()), indent=2) == raw
    # a run writes the same: no key at salt 0, the key at a non-zero salt, and both round-trip
    for salt in (0, 3):
        cfg = EvolutionConfig(population_size=2, seed=5, holistic_stream_salt=salt)
        Experiment(cfg, out_dir=str(tmp_path / f"s{salt}"), log=None)
        written = json.loads((tmp_path / f"s{salt}" / "config.json").read_text())
        assert ("holistic_stream_salt" in written) == bool(salt)
        assert EvolutionConfig.from_dict(written).holistic_stream_salt == salt
