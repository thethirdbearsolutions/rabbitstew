"""RBT-96 adversary, item 4: the test the PR's two tests do not contain.

Both of the PR's tests compare the new ``spawn_streams`` with itself (salt 0 against the default,
which is also 0), so a mutant that re-spawns the holistic stream at spawn key (i, 0) even for salt 0
passes all eight tests in tests/test_rng_streams.py while changing every earlier run's holistic
population (shown in item4.txt).  This pins salt 0 to the pre-salt construction, written out
independently of the function under test, and to literal draws recorded from the pre-salt code
(merge-base 852dcac).

    PYTHONPATH=<checkout> python -m pytest -q runs/RBT-96/adversary/test_salt0_golden.py
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

