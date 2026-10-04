"""RBT-134 assay runner (runs/RBT-134/assay.py): the readout's rules on synthetic records, and the parsers.

No registered condition is run here (DESIGN.md 13: nothing runs before the merge and the GO).
"""
import importlib.util
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def assay():
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        spec = importlib.util.spec_from_file_location("assay134", os.path.join(ROOT, "runs", "RBT-134", "assay.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


def test_registered_constants(assay):
    assert assay.RUNGS == {"a16": 6.2831, "a32": 12.5236, "a64": 24.7145} and assay.PRIMARY == "a32"
    assert assay.FAMILY == ("P2", "P3") and assay.MARGIN == 2.0
    assert assay.B0_BG_PREFIX == {"all": (26, 9_996), "unflagged": (22, 9_990)}
    assert assay.CHECK_BOUND == {"A0": 0, "P1": 2, "P2": 29, "P3": 29}
    assert assay.CONDITIONS["P2"] == {"link_sigma": 4.0}
    assert assay.CONDITIONS["P3"] == {"link_sigma": 4.0, "bias_reset_rate": 0.2}
    assert assay.CONDITIONS["B0"] == {}


def test_committed_readouts_parse(assay):
    assert len(assay.committed_arrivals("RBT-91-alone-baseline.txt")) == 84
    assert len(assay.committed_arrivals("RBT-91-alone-1.6.txt")) == 63
    assert len(assay.committed_arrivals("RBT-91-alone-4.0.txt")) == 66


def test_exact_and_katz(assay):
    assert assay.binom_sf(6, 6) == pytest.approx(1 / 64)
    assert assay.binom_sf(5, 5) == pytest.approx(1 / 32)
    assert assay.binom_sf(0, 0) == 1.0
    # equal rates: the upper bound sits a little above 1; double the rate: above 2 at these counts
    assert 1.0 < assay.katz_upper(88, 40_000, 88, 40_000) < 1.5
    assert assay.katz_upper(176, 40_000, 88, 40_000) > 2.0


def test_flagged_units_never_count(assay):
    arr = {"units": [{"a": 90.0, "flip": True}, {"a": 3.0, "flip": False}]}
    assert assay.arrival_a(arr) == 3.0
    assert assay.arrival_a({"units": [{"a": 90.0, "flip": True}]}) is None


def _fake(cond, arrivals, bg, n=10):
    return {"condition": cond, "fields": {}, "n_per_pool": n, "n_bg_per_pool": n, "aux_key": 134, "git": "x" * 40,
            "pools": {"W4b-801-bests": n, "P-801-final60": n}, "arrivals": arrivals, "bg": bg, "sham": len(arrivals),
            "mismatch": 0, "pair_events": {"events": 0, "refused": 0}}


def _arr(i, a, func="tanh", flip=False, prod=None):
    return {"label": "W4b-801-bests", "i": i, "parent": 0, "whole": 0.0,
            "units": [{"k": 1, "func": func, "bk": 0.0, "a": a, "flip": flip, "prod": a if prod is None else prod}]}


def test_readout_verdicts_on_synthetic_records(assay, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    bg0 = [["W4b-801-bests", i, False, 10.0 if i < 40 else 0.0, False] for i in range(20_000)]
    bg_same = bg0
    bg_pump = [["W4b-801-bests", i, False, 10.0 if i < 400 else 0.0, False] for i in range(20_000)]
    recs = {
        "B0": _fake("B0", [_arr(1, 0.5)], bg0),
        "P2": _fake("P2", [_arr(j, 20.0) for j in range(2, 12)], bg_pump),  # moves, background pumped
        "P3": _fake("P3", [_arr(j, 20.0) for j in range(2, 12)] + [_arr(99, 80.0, func="sign", flip=True)], bg_same),
    }
    for c, r in recs.items():
        json.dump(r, open(tmp_path / f"{c}.json", "w"))
    assay.readout()
    out = capsys.readouterr().out
    assert "P2: discordant 10 up / 0 down" in out and "**MOVES-WITH-BACKGROUND**" in out
    assert "P3: discordant 10 up / 0 down" in out and "**PASS**" in out  # the flagged `sign` arrival is not counted


def test_readout_null_below_threshold(assay, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    bg0 = [["W4b-801-bests", i, False, 10.0 if i < 40 else 0.0, False] for i in range(20_000)]
    for c, arr in (("B0", []), ("P2", [_arr(j, 20.0) for j in range(4)]), ("P3", [])):
        json.dump(_fake(c, arr, bg0), open(tmp_path / f"{c}.json", "w"))
    assay.readout()
    out = capsys.readouterr().out
    assert out.count("**NULL**") == 2


def _h1():
    spec = importlib.util.spec_from_file_location("h1_134", os.path.join(ROOT, "runs", "RBT-134", "h1_census.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_h1_arms_on_planted_structures():
    """Arm G sees a global differencing unit on single-instance noses; arm I sees per-part nose -> Effector loops
    (here on two distinct wheel Nodes: I-dist, not I-dup)."""
    import numpy as np
    from rabbitstew.analysis import _run_config
    from rabbitstew.genetics import Link, MutationConfig, UnitRef, _wheel_pairs, mutate_controller
    from rabbitstew.genotype import Genotype
    from rabbitstew.synthesis import synthesize
    h1 = _h1()
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        cfg = _run_config("runs/RBT-19/P-801")
    finally:
        os.chdir(cwd)
    g = Genotype.load(os.path.join(ROOT, "runs", "RBT-19", "P-801", "conventional", "best_gen0590.json"))
    G, dup, dist, food_any, two_single, multi = h1.arms(synthesize(g, cfg.sim.synthesis))
    assert food_any and two_single and not multi
    plant = mutate_controller(g, np.random.default_rng(1), MutationConfig(pair_event_rate=1.0, weight_rate=0.0,
                              add_unit_rate=0.0, remove_unit_rate=0.0, add_link_rate=0.0, remove_link_rate=0.0,
                              func_rate=0.0), aux_rng=np.random.default_rng(2))
    assert h1.arms(synthesize(plant, cfg.sim.synthesis))[0]
    loops = g.copy()
    for node, s, e in _wheel_pairs(loops):
        loops.nodes[node].segment.brain.links.append(Link(UnitRef(node, s), UnitRef(node, e), 1.0))
    r = h1.arms(synthesize(loops, cfg.sim.synthesis))
    assert r[2] and not r[1]
