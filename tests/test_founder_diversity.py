"""RBT-90 part 1: the founding-population diversity readout re-derives from committed configs alone.

`runs/` is not a package, so the script is loaded by path.  No simulation: sixty founders per seed are
regenerated from the seed, the vocabulary and the capacity, and classified by RBT-28's ``wiring``.

Two generators.  ``founders()`` draws from ``spawn_streams(seed)[HOLISTIC]``, the founders an ecology
run on this head founds (RBT-95; RBT-90 part 2, 2026-09-26 ruling).  Part 1 measured, calibrated and
chose the part-2 seeds on the founders ``np.random.default_rng(seed)`` drew before RBT-95; the tests
taking the ``part1`` fixture pin those numbers as **part 1's generator**, the record of what part 1
measured, not as what a run on this head founds.
"""

import importlib.util
import json
import pathlib

import numpy as np
import pytest

from rabbitstew.ecology import Ecology, EcologyConfig
from rabbitstew.evolution import HOLISTIC

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def fd():
    spec = importlib.util.spec_from_file_location("founder_diversity", ROOT / "runs" / "RBT-90" / "founder_diversity.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def part1():
    """The script with part 1's generator: the holistic founders from ``default_rng(seed)``, as before RBT-95."""
    spec = importlib.util.spec_from_file_location("founder_diversity_part1", ROOT / "runs" / "RBT-90" / "founder_diversity.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.spawn_streams = lambda seed: {mod.HOLISTIC: np.random.default_rng(seed)}
    return mod


def test_founders_are_the_ones_the_ecology_founds(fd):
    """This head's generator: seed 801 -> 41/15/28 (docs/artifacts/RBT-90-head-founders.txt), and the same sixty bodies
    the ecology's own constructor founds from forage-801's command."""
    m = fd.measure(801)
    assert (m["n"], m["drive"], m["osc"], m["both"]) == (60, 41, 15, 28)
    evo, F = fd.founders(801)
    eco = Ecology(evo, EcologyConfig(**json.load(open(ROOT / fd.CONFIGS[801]))["ecology"]))
    assert [fd.adv.shape_sig(g) for g in eco.populations[HOLISTIC]] == m["sigs"]


def test_base_rates_reproduce_rbt84s_pre_registered_readout(part1):
    """Part 1's generator. RBT-84's founder_base_rate.txt: 801 -> 40/13/29, 807 -> 38/15/29; one classifier, one measurement."""
    fd = part1
    m801, m807 = fd.measure(801), fd.measure(807)
    assert (m801["n"], m801["drive"], m801["osc"], m801["both"]) == (60, 40, 13, 29)
    assert (m807["n"], m807["drive"], m807["osc"], m807["both"]) == (60, 38, 15, 29)
    assert abs(fd.rates(m801)["both"] - 0.483) < 5e-4


def test_founders_are_one_flag_from_forage_801(fd):
    """Each calibration seed regenerates from its own committed config, and the founders read only seed, vocabulary and capacity."""
    for seed in fd.CALIBRATION:
        raw = json.load(open(ROOT / fd.CONFIGS[seed]))
        assert raw["seed"] == seed
        evo, F = fd.founders(seed)
        assert len(F) == 60 and F[49].name == "h0-49"


def test_bodies_are_never_shared_between_seeds_but_shapes_are(fd):
    """The full signature has no resolution between random draws (0 of 60, every pair); the shape multiset does."""
    M = {s: fd.measure(s) for s in fd.CALIBRATION}
    for a in fd.CALIBRATION:
        assert len(set(M[a]["sigs"])) == 60
        for b in fd.CALIBRATION:
            if a == b:
                continue
            assert sum(x in set(M[b]["sigs"]) for x in M[a]["sigs"]) == 0
            shared_shapes = sum(x in set(M[b]["shapes"]) for x in M[a]["shapes"])
            assert 30 <= shared_shapes <= 56  # the calibration readout, either direction: 36/60 to 52/60


def test_seed_805_is_the_outlier_of_the_calibration_set(part1):
    """Part 1's generator. Its composite 21/60 = 0.350 is below every one of the 200 reference seeds (min 0.367): a label, not an exclusion."""
    fd = part1
    ref = json.load(open(ROOT / "docs" / "artifacts" / "RBT-90-reference.json"))
    r = fd.rates(fd.measure(805))
    assert r["both"] < ref["band"]["both"][0] and r["osc"] > ref["band"]["osc"][1]
    for seed in (801, 804, 806, 807):
        r = fd.rates(fd.measure(seed))
        assert all(ref["band"][k][0] <= r[k] <= ref["band"][k][1] for k in ("drive", "osc", "both", "parts_median", "units_median"))


def test_the_part_2_choice_is_deterministic_and_passes_the_rule(part1):
    """Part 1's generator, on which the committed ten were chosen. The coordinator's rule (RBT-90, 16:20): the five kept, candidates 1..200, the lexicographically first five whose union passes."""
    fd = part1
    ref = json.load(open(ROOT / "docs" / "artifacts" / "RBT-90-reference.json"))
    chosen, _ = fd.choose(10, ref)
    assert chosen == fd.CALIBRATION + (1, 2, 3, 4, 7)
    cache = {}
    assert fd.passes(chosen, ref, cache)
    assert not fd.passes(fd.CALIBRATION, ref, cache)  # the five alone fail clause 2
    assert not fd.passes(fd.CALIBRATION + (1, 2, 3, 4, 5), ref, cache) and not fd.passes(fd.CALIBRATION + (1, 2, 3, 4, 6), ref, cache)
    # the two statistics clause 2 is ruled on, as k/60
    both = [fd.rates(cache[s])["both"] for s in chosen]
    osc = [fd.rates(cache[s])["osc"] for s in chosen]
    assert min(both) <= 28 / 60 and max(both) >= 33 / 60 and min(osc) <= 11 / 60 and max(osc) >= 15 / 60
    assert fd.k60(28 / 60) == "28/60" and fd.k60(0.5) == "30/60" and fd.k60(0.4871) == "0.487"


def test_the_guard_reads_what_the_classifier_reads(fd, tmp_path):
    """founders() refuses a config whose vocabulary, capacity or synthesis differs from 801's (the adversary's guard note)."""
    import copy
    raw = json.load(open(ROOT / fd.CONFIGS[801]))
    for mutate in (lambda c: c["mutation"]["vocab"]["neuron_funcs"].pop(),
                   lambda c: c["ecology"].__setitem__("capacity", 61),
                   lambda c: c["sim"]["synthesis"].__setitem__(next(iter(c["sim"]["synthesis"])), "changed")):
        bad = copy.deepcopy(raw)
        mutate(bad)
        path = tmp_path / "config.json"
        path.write_text(json.dumps(bad))
        fd.CONFIGS[9999] = str(path.relative_to(ROOT)) if str(path).startswith(str(ROOT)) else str(path)
        try:
            with pytest.raises(SystemExit, match="differs from seed 801"):
                fd.founders(9999)
        finally:
            fd.CONFIGS.pop(9999, None)
