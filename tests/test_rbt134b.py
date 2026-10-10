"""RBT-134b (runs/RBT-134/DESIGN-134b.md): the redesigned C+, the never-structured background, I9, I5-S and the
held-out validation summary.

No registered condition is run, and no MASTER_SEED or held-out seed is used: the mechanism tests use throwaway seed
1 with artificial MutationConfig fields (a pair-event rate of 0.03, which no condition registers) on a few lineages, and
the readout tests use synthetic records.
"""
import importlib.util
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W4B, P801 = "W4b-801-bests", "P-801-final60"


@pytest.fixture(scope="module")
def assay():
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        spec = importlib.util.spec_from_file_location("assay134b", os.path.join(ROOT, "runs", "RBT-134", "assay.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


def test_registered_134b_constants(assay):
    assert assay.HELDOUT_SEEDS == (20261101, 20261102)
    assert assay.rbt78.MASTER_SEED not in assay.HELDOUT_SEEDS and 20261011 not in assay.HELDOUT_SEEDS
    assert assay.CPLUS_LADDER == (5e-5, 2e-4, 1e-3) and assay.ACCEPT_K == 20
    assert assay.CPLUS_REGISTERED is None  # set only by the registration amendment, after validation
    for j, rate in enumerate(assay.CPLUS_LADDER):  # r3's plant, only the rate changes
        assert assay.CONDITIONS_134B[f"C+L{j + 1}"] == dict(assay.CONDITIONS["C+"], pair_event_rate=rate)
    for c in ("B0", "A0", "P1", "P2", "P3", "P4", "P5"):  # carried over unchanged
        assert assay.CONDITIONS_134B[c] == assay.CONDITIONS[c]
    assert assay.CONDITIONS_134B["C-"] == {"weight_sigma": 4.0}
    assert assay.FAMILY == ("P2", "P3") and assay.MARGIN == 2.0 and assay.WHOLE == 6.8664


@pytest.mark.parametrize("cond,seed,ok", [
    ("B0", 20261101, True), ("C+L1", 20261102, True), ("C-", 20261101, True),
    ("P2", 20261101, False), ("A0", 20261102, False),  # no family or check condition at a held-out seed
    ("B0", 20261011, False), ("B0", 1, False),  # only the registered held-out seeds
    ("B0", 20260912, False), ("P2", 20260912, False),  # MASTER_SEED waits for the registration amendment
])
def test_seed_guard(assay, cond, seed, ok):
    assert (assay.check_seed_134b(cond, seed) is None) == ok


def test_seed_guard_after_registration(assay, monkeypatch):
    monkeypatch.setattr(assay, "CPLUS_REGISTERED", "C+L2")
    assert assay.check_seed_134b("P2", 20260912) is None and assay.check_seed_134b("C+L2", 20260912) is None
    assert assay.check_seed_134b("C+L1", 20260912) and assay.check_seed_134b("C-", 20260912)


def test_run_134b_refuses_without_go(assay):
    with pytest.raises(SystemExit, match="GO"):
        assay.run_134b("B0", 20261101, 10, 10, 1, go=False)
    with pytest.raises(SystemExit, match="refused"):
        assay.run_134b("P2", 20261101, 10, 10, 1, go=True)


def _same(ph1, ph2):
    return (ph1.links == ph2.links
            and [(u.ref, u.unit.kind, getattr(u.unit, "func", None), getattr(u.unit, "bias", None)) for u in ph1.units]
            == [(u.ref, u.unit.kind, getattr(u.unit, "func", None), getattr(u.unit, "bias", None)) for u in ph2.units])


def test_a_plant_is_structure_and_an_unplanted_lineage_is_b0s(assay):
    """The two facts I9 rests on (DESIGN-134b.md 4.3): every planted lineage is ever-structured, and a pair-condition
    lineage without a plant IS the default lineage (the event's draws are all on aux_rng)."""
    fields = {"pair_event_rate": 0.03, "pair_event_scale": 16.0, "pair_event_zero_bias": True}  # artificial
    planted = unplanted = remnants = 0
    for label in (W4B, P801):
        for i in range(20):
            ph, _, ever, pl = assay.lineage_134b(label, i, fields, 1, track=True)
            if pl:
                planted += 1
                assert ever is True
                remnants += not assay.predicate(ph, "food")
            else:
                unplanted += 1
                ph0, _, ever0, _ = assay.lineage_134b(label, i, {}, 1, track=True)
                assert _same(ph, ph0) and ever == ever0
    assert planted and unplanted and remnants  # remnants occur, and every one is ever-structured (excluded)


def test_swap_exchanges_the_two_predicates(assay):
    """I5-S's identity on the default operator: from swapped parents the food predicate is the original sham."""
    for label in (W4B, P801):
        for i in range(10):
            ph = assay.lineage_134b(label, i, {}, 1)[0]
            phs = assay.lineage_134b(label, i, {}, 1, swap=True)[0]
            assert assay.predicate(phs, "food") == assay.predicate(ph, "agent")
            assert assay.predicate(phs, "agent") == assay.predicate(ph, "food")


def test_plant_visibility_on_every_committed_parent(assay):
    """DESIGN-134b.md 1 (V): a plant on any committed parent is a predicate unit at the depth it is made."""
    import numpy as np
    from rabbitstew import genetics
    for label in (W4B, P801):
        cfg, pool = assay.rbt78._load(label)
        mcfg = assay.replace(cfg.mutation, pair_event_rate=1.0, pair_event_scale=16.0, pair_event_zero_bias=True)
        for g in pool:
            child = g.copy()
            genetics._pair_event(child, np.random.default_rng(0), mcfg)
            ph = assay.synthesize(child, cfg.sim.synthesis)
            k = [j for j, u in enumerate(ph.units) if u.part is None and u.ref.index == len(child.global_brain.units) - 1]
            assert len(k) == 1 and k[0] in assay.predicate(ph, "food")


# ---------------------------------------------------------------- synthetic readouts

def _arr(i, a, label=W4B):
    return {"label": label, "i": i, "parent": 0, "whole": 0.0,
            "units": [{"k": 1, "func": "tanh", "bk": 0.0, "a": a, "flip": False, "prod": a}]}


def _bg(hits, n=20_000, ever_from=None, remnant_a=50.0, planted=()):
    rows = []
    for i in range(n):
        ever = ever_from is not None and i >= ever_from
        a = remnant_a if ever else (10.0 if i < hits else 0.0)
        rows.append([W4B, i, False, a, False, ever, i in planted])
    return rows


def _rec(cond, arrivals=(), bg=None, food=(), sham=(), planted=(), n=100_000):
    return {"condition": cond, "fields": {}, "pools": {W4B: n, P801: n}, "n_per_pool": n, "n_bg_per_pool": 20_000,
            "arrivals": list(arrivals), "bg": bg if bg is not None else _bg(44), "mismatch": 0,
            "food_ids": [[W4B, i] for i in food], "sham_ids": [[W4B, i] for i in sham],
            "planted": [[W4B, i, True] for i in planted], "pair_events": {"events": 0, "refused": 0, "no_pair": 0}}


def _write(d, name, rec):
    os.makedirs(d, exist_ok=True)
    json.dump(rec, open(os.path.join(d, f"{name}.json"), "w"))


def _seed_dir(tmp_path, seed, cplus=None, cminus_hits=440, swap_ok=True, leak=False):
    d = str(tmp_path / f"134b-{seed}")
    food, sham = [5, 6, 7], [8, 9]
    _write(d, "B0", _rec("B0", food=food, sham=sham))
    _write(d, "B0-swap", _rec("B0", food=sham, sham=food if swap_ok else food[:2]))
    _write(d, "C-", _rec("C-", bg=_bg(cminus_hits), food=food, sham=sham))
    _write(d, "C--swap", _rec("C-", food=sham, sham=food))
    for name, k in (cplus or {}).items():
        planted = list(range(30_000, 30_000 + k))
        bg = _bg(44, ever_from=19_000)  # 1,000 remnants: r3's measure fails, never-structured does not
        if leak:
            bg[3][3] = 99.0  # a never-structured row that differs from B0's
        _write(d, name, _rec(name, arrivals=[_arr(i, 20.0) for i in planted], bg=bg, food=food + planted,
                             sham=sham, planted=planted))
    return d


def test_readout_134b_held_out(assay, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    _seed_dir(tmp_path, 20261101, cplus={"C+L1": 25})
    acc = assay.readout_134b(20261101)
    out = capsys.readouterr().out
    assert acc["I4b C+L1"] and acc["ACCEPT C+L1"] and acc["I9 C+L1"] and acc["C- fails"]
    assert acc["I5-S B0"] and acc["I5-S C-"] and acc["VOID none"]
    assert "HELD-OUT VALIDATION" in out and "never pooled" in out
    row = [l for l in out.splitlines() if l.startswith("| C+L1 |")][0]
    assert "| 1000 |" in row  # the remnants are counted, and excluded from the 134b background


def test_readout_134b_r3_measure_would_fail_on_the_same_records(assay, tmp_path, monkeypatch):
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    _seed_dir(tmp_path, 20261101, cplus={"C+L1": 25})
    c = json.load(open(tmp_path / "134b-20261101" / "C+L1.json"))
    b0 = json.load(open(tmp_path / "134b-20261101" / "B0.json"))
    assert assay.katz_upper(*assay.bg_hits(c), *assay.bg_hits(b0)) > assay.MARGIN
    assert assay.katz_upper(*assay.bg_never(c), *assay.bg_never(b0)) <= assay.MARGIN


def test_i9_catches_a_leak_and_i5s_a_mismatch(assay, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    _seed_dir(tmp_path, 20261101, cplus={"C+L1": 25}, leak=True, swap_ok=False)
    acc = assay.readout_134b(20261101)
    out = capsys.readouterr().out
    assert not acc["I9 C+L1"] and not acc["ACCEPT C+L1"] and not acc["I5-S B0"] and not acc["VOID none"]
    assert "- I9 C+L1" in out and "- I5-S B0" in out


def test_c_minus_must_fail_the_clause(assay, tmp_path, monkeypatch):
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    _seed_dir(tmp_path, 20261101, cminus_hits=60)  # a 1.4x pump: the clause cannot be shown to fail it
    assert assay.readout_134b(20261101)["C- fails"] is False


@pytest.mark.parametrize("ladder,cminus,want", [
    ({20261101: {"C+L1": 25}, 20261102: {"C+L1": 25}}, 440, "C+L1"),
    ({20261101: {"C+L1": 12, "C+L2": 40}, 20261102: {"C+L1": 30, "C+L2": 40}}, 440, "C+L2"),  # L1 short on one seed
    ({20261101: {"C+L1": 12}, 20261102: {"C+L1": 30}}, 440, "WAITING"),  # L2 has not run yet
    ({s: {"C+L1": 3, "C+L2": 4, "C+L3": 5} for s in (20261101, 20261102)}, 440, "ESCALATE"),
    ({20261101: {"C+L1": 25}, 20261102: {"C+L1": 25}}, 60, "ESCALATE"),  # C- does not fail: the clause is broken
])
def test_validation_summary(assay, tmp_path, monkeypatch, capsys, ladder, cminus, want):
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    for seed, cplus in ladder.items():
        _seed_dir(tmp_path, seed, cplus=cplus, cminus_hits=cminus)
    assert assay.validation_summary() == want


def test_validation_summary_escalates_on_an_i9_leak(assay, tmp_path, monkeypatch):
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    _seed_dir(tmp_path, 20261101, cplus={"C+L1": 25}, leak=True)
    _seed_dir(tmp_path, 20261102, cplus={"C+L1": 25})
    assert assay.validation_summary() == "ESCALATE"
