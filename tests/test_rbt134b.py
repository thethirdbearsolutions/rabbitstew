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


def _seed_dir(tmp_path, seed, cplus=None, cminus_hits=440, swap_ok=True, leak=False, cpu_h=0.0):
    d = str(tmp_path / f"134b-{seed}")
    food, sham = [5, 6, 7], [8, 9]
    _write(d, "B0", _rec("B0", food=food, sham=sham))
    with open(os.path.join(d, "cpu-ledger.jsonl"), "w") as f:  # the cost ledger, two chunks
        for _ in range(2):
            f.write(json.dumps({"cond": "B0", "swap": False, "label": W4B, "lo": 0, "cpu_s": cpu_h * 1800}) + "\n")
    _write(d, "B0-swap", _rec("B0", food=sham, sham=food if swap_ok else food[:2]))
    _write(d, "C-", _rec("C-", bg=_bg(cminus_hits), n=20_000))  # sealed: background block only, no sets
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
    assert acc["I5-S B0"] and acc["VOID none"] and "I5-S C-" not in acc  # no C- swap (trim iii)
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


def test_validation_summary_escalates_when_c_minus_holds_on_either_seed(assay, tmp_path, monkeypatch):
    """Review M1: row 1 of DESIGN-134b.md 5.3 fires on EITHER seed."""
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    _seed_dir(tmp_path, 20261101, cplus={"C+L1": 25}, cminus_hits=60)
    _seed_dir(tmp_path, 20261102, cplus={"C+L1": 25})
    assert assay.validation_summary() == "ESCALATE"


# ---------------------------------------------------------------- cost trims and the stop rule (DESIGN-134b.md 8)

@pytest.mark.parametrize("cond,seed,ok", [
    ("B0", 20261101, True), ("B0", 20261102, True),  # I5-S B0 at the held-out seeds
    ("C-", 20261101, False),  # trim (iii): no C- swap
    ("C+L1", 20261101, False), ("P5", 20260912, False),  # not sensor-blind
    ("B0", 20260912, False),  # trim (iv): cited from the diagnosis, not re-run
    ("A0", 20260912, True), ("P1", 20260912, True), ("P2", 20260912, True), ("P3", 20260912, True),
    ("P4", 20260912, True),
])
def test_swap_guard(assay, cond, seed, ok):
    assert (assay.check_swap_134b(cond, seed) is None) == ok


def test_run_134b_refuses_the_trimmed_swaps(assay, monkeypatch):
    with pytest.raises(SystemExit, match="I5-S does not run on C-"):
        assay.run_134b("C-", 20261101, 10, 10, 1, go=True, swap=True)
    monkeypatch.setattr(assay, "CPLUS_REGISTERED", "C+L1")
    with pytest.raises(SystemExit, match="cited"):
        assay.run_134b("B0", 20260912, 10, 10, 1, go=True, swap=True)


def test_the_cost_envelope_is_as_section_8_states(assay):
    """DESIGN-134b.md 8's figures: base 21.8 and base + the re-signing reserve (29.7, A0 out: item 8) fit the cap; the
    worst case (34.5: two climbs, re-signing at its cap) does not, which the stop rule guards."""
    c = assay.COST_H
    validation = len(assay.HELDOUT_SEEDS) * (2 * c["condition"] + c["C-"] + c["swap"])  # B0, C+L1, C-, B0 swap
    climbs = 2 * len(assay.HELDOUT_SEEDS) * c["condition"]
    assert assay.CPU_CAP_134B == 30.0
    assert assay.REGISTERED_RUN_H == pytest.approx(8 * c["condition"] + 5 * c["swap"])
    assert "A0" not in assay.RESIGN_CONDITIONS and assay.RESIGN_CAP == 7 * 400
    assert assay.RESIGN_RESERVE_H == pytest.approx(1.5 * 2800 * 6.8 / 3600)
    base = validation + assay.REGISTERED_RUN_H
    assert round(validation, 2) == 7.7 and round(assay.REGISTERED_RUN_H, 2) == 14.1 and round(base, 2) == 21.8
    assert round(base + assay.RESIGN_RESERVE_H, 1) == 29.7
    assert round(base + climbs + assay.RESIGN_RESERVE_H, 1) == 34.5


def test_cost_gate(assay, tmp_path, monkeypatch):
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    assert assay.cost_gate_134b(1.0, spent=10.0, still_to_come=15.0) is None
    assert "STOP-COST" in assay.cost_gate_134b(2.0, spent=14.0, still_to_come=15.0)
    _seed_dir(tmp_path, 20261101, cpu_h=3.25)
    _seed_dir(tmp_path, 20261102, cpu_h=3.25)
    assert assay.spent_134b() == pytest.approx(6.5)
    assert assay.cost_gate_134b(assay.resign_cost_h(3000)) is None  # 6.5 + 8.5
    assert "STOP-COST" in assay.cost_gate_134b(assay.resign_cost_h(3000), still_to_come=15.5)  # 30.5


@pytest.mark.parametrize("spent,want", [(0.5, "WAITING"), (14.0, "STOP-COST")])
def test_a_ladder_climb_passes_the_cost_stop_rule(assay, tmp_path, monkeypatch, spent, want):
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    for seed in assay.HELDOUT_SEEDS:
        _seed_dir(tmp_path, seed, cplus={"C+L1": 12}, cpu_h=spent / 2)
    assert assay.validation_summary() == want


# ---------------------------------------------------------------- C- sealed (review M2, adversary NIT a)

def test_c_minus_is_read_as_a_token_only(assay, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    _seed_dir(tmp_path, 20261101)
    acc = assay.readout_134b(20261101)
    out = capsys.readouterr().out
    assert acc["C- fails"] is True
    row = [ln for ln in out.splitlines() if ln.startswith("| C- |")][0]
    assert "sealed" in row and not any(ch.isdigit() for ch in row)
    line = [ln for ln in out.splitlines() if ln.startswith("C- ")][0]
    assert line.endswith("YES") and "/" not in line  # no counts, no bound


def test_a_sealed_chunk_records_background_rows_only(assay, monkeypatch):
    """The sealed mode on the default operator at throwaway seed 1 (C-'s own fields are not run here)."""
    monkeypatch.setattr(assay, "SEALED_134B", ("B0",))
    out = assay.chunk_134b(("B0", W4B, 0, 6, 6, 1, False))
    assert out["arrivals"] == [] and out["food_ids"] == [] and out["sham_ids"] == []
    assert len(out["bg"]) == 6 and all(len(b) == 6 for b in out["bg"])
    assert out["cpu_s"] > 0  # every chunk carries its CPU for the cost ledger


# ---------------------------------------------------------------- the exclusion flag (review M5)

def test_exclusion_flag(assay):
    b0 = _rec("B0", bg=_bg(44, ever_from=19_990))  # 10 remnants of 20,000; never-structured hit rate 44/19,990
    thr = 44 / 19_990
    few = _rec("C+L1", bg=_bg(44, ever_from=19_970))  # 30 remnants: excess 20/20,000 < thr
    many = _rec("P2", bg=_bg(44, ever_from=19_900))  # 100 remnants: excess 90/20,000 >= thr
    ex, t, flag = assay.exclusion_flag(few, b0)
    assert t == pytest.approx(thr) and ex == pytest.approx(20 / 20_000) and not flag
    assert assay.exclusion_flag(many, b0)[2]


# ---------------------------------------------------------------- the code facts the design rests on (review N2)

def test_the_pair_event_is_the_last_operation_of_a_mutation_step():
    """genetics.mutate_controller: after `_pair_event` only validation and the return remain, so a plant is in the
    genotype the step returns, and the tracked predicate sees it at the depth it is made."""
    import ast
    import inspect
    from rabbitstew import genetics
    fn = ast.parse(inspect.getsource(genetics.mutate_controller)).body[0]
    idx = [j for j, st in enumerate(fn.body) if "_pair_event" in ast.unparse(st)]
    assert len(idx) == 1
    rest = [ast.unparse(st) for st in fn.body[idx[0] + 1:]]
    assert rest[0] == "problems = child.validate()" and rest[-1] == "return child" and len(rest) == 3
    assert rest[1].startswith("if problems:") and "raise" in rest[1]


def test_no_committed_parent_is_structured_at_depth_0(assay):
    """0 of 67 parents satisfy the food or the agent predicate before any mutation."""
    n = 0
    for label in (W4B, P801):
        cfg, pool = assay.rbt78._load(label)
        for g in pool:
            ph = assay.synthesize(g, cfg.sim.synthesis)
            assert not assay.predicate(ph, "food") and not assay.predicate(ph, "agent")
            n += 1
    assert n == 67


def test_134b_lineages_are_r3_lineages(assay, monkeypatch):
    """The streams of lineage_134b are r3's `lineage`'s, keyed by the seed: so B0's 134b lineages at MASTER_SEED are
    the lineages the RBT-134 diagnosis swapped (trim iv).  Checked at throwaway seed 1."""
    monkeypatch.setattr(assay.rbt78, "MASTER_SEED", 1)
    for label in (W4B, P801):
        for i in range(5):
            assert _same(assay.lineage_134b(label, i, {}, 1, track=True)[0], assay.lineage(label, i, {})[0])


def test_i5s_b0_at_master_seed_is_cited_not_rerun(assay, tmp_path, monkeypatch, capsys):
    """Trim (iv): at MASTER_SEED no B0 swap file is read; I5-S B0 is the diagnosis's EXACT, cited (synthetic records,
    nothing run; the synthetic B0 does not reproduce RBT-91, so I2 VOIDs here, as it must)."""
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    monkeypatch.setattr(assay, "CPLUS_REGISTERED", "C+L1")
    _write(str(tmp_path / "134b-20260912"), "B0", _rec("B0", food=[5, 6, 7], sham=[8, 9]))
    acc = assay.readout_134b(20260912)
    out = capsys.readouterr().out
    assert acc["I5-S B0"] is True and "I5-S B0: cited" in out and "EXACT" in out
    assert not acc["VOID none"] and "I2 B0" in out


def test_every_run_passes_the_cost_stop_rule(assay, monkeypatch):
    """The coordinator's reading of OWNER-DECISIONS-2026-10-10 item 7: any projected overrun of 30 CPU-h stops."""
    monkeypatch.setattr(assay, "spent_134b", lambda: 14.0)  # + 0.9 + 10.7 + 5.0 > 30
    with pytest.raises(SystemExit, match="STOP-COST"):
        assay.run_134b("B0", 20261101, 100_000, 20_000, 1, go=True)


def test_registered_to_come_counts_only_missing_items(assay, tmp_path, monkeypatch):
    """MINOR B (round 2): at MASTER_SEED the stop rule counts every registered item without an output yet, so the whole
    registered run is checked before its first item."""
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    monkeypatch.setattr(assay, "CPLUS_REGISTERED", "C+L1")
    c = assay.COST_H
    assert assay.registered_to_come() == pytest.approx(assay.REGISTERED_RUN_H)
    assert assay.registered_to_come(exclude=("B0", False)) == pytest.approx(assay.REGISTERED_RUN_H - c["condition"])
    d = str(tmp_path / "134b-20260912")
    for name in ("B0", "C+L1", "A0", "P1", "P2", "P3", "P4", "A0-swap", "P1-swap", "P2-swap", "P3-swap"):
        _write(d, name, {})
    assert assay.registered_to_come() == pytest.approx(c["condition"] + c["swap"])  # P5 and P4's swap remain
    assert assay.registered_to_come(exclude=("P4", True)) == pytest.approx(c["condition"])


def test_the_registered_run_is_checked_whole_before_its_first_item(assay, monkeypatch):
    monkeypatch.setattr(assay, "CPLUS_REGISTERED", "C+L1")
    monkeypatch.setattr(assay, "registered_to_come", lambda exclude=None: 12.9 if exclude else 14.1)
    monkeypatch.setattr(assay, "spent_134b", lambda: 8.0)  # 8.0 + 1.2 + 12.9 + 9.07 > 30
    with pytest.raises(SystemExit, match="STOP-COST"):
        assay.run_134b("B0", 20260912, 100_000, 20_000, 1, go=True)


def _fake_chunk(cpu_s):
    def chunk(task):  # stands in for chunk_134b: nothing is computed
        cond, label, lo, hi, n_bg, master, swap = task
        return {"label": label, "n": hi - lo, "arrivals": [], "bg": [], "food_ids": [], "sham_ids": [], "planted": [],
                "mismatch": 0, "pair_events": {"events": 0, "refused": 0, "no_pair": 0}, "cpu_s": cpu_s}
    return chunk


def test_a_run_stops_mid_run_before_the_cap(assay, tmp_path, monkeypatch):
    """Review R2: the stop rule is checked after every chunk against the measured ledger; a run whose measured pace
    would carry spent past the cap cancels its unstarted chunks and exits STOP-COST, writing no output."""
    from concurrent.futures import ThreadPoolExecutor
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    with pytest.raises(SystemExit, match="STOP-COST mid-run"):  # 600 CPU-s per chunk x 100 chunks = 16.7 CPU-h
        assay.run_134b("B0", 20261101, 100_000, 20_000, 1, go=True, _chunk=_fake_chunk(600.0),
                       _executor=ThreadPoolExecutor)
    d = tmp_path / "134b-20261101"
    assert not (d / "B0.json").exists()
    lines = (d / "cpu-ledger.jsonl").read_text().splitlines()
    assert 1 <= len(lines) <= 3  # the finished chunks are counted, the rest never started
    assert assay.spent_134b() < assay.CPU_CAP_134B


def test_a_run_within_the_cap_completes(assay, tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    assay.run_134b("B0", 20261101, 4_000, 2_000, 2, go=True, _chunk=_fake_chunk(1.0), _executor=ThreadPoolExecutor)
    d = tmp_path / "134b-20261101"
    assert json.load(open(d / "B0.json"))["pools"] == {W4B: 4_000, P801: 4_000}
    assert len((d / "cpu-ledger.jsonl").read_text().splitlines()) == 4
    assert assay.spent_134b() == pytest.approx(4 / 3600)


def test_the_resign_reserve_uses_the_actual_eligible_count(assay, tmp_path, monkeypatch):
    """OWNER-DECISIONS-2026-10-10 item 8: A0 out; each re-signing condition at its actual eligible count (capped at
    400) once its MASTER_SEED output exists, at the cap until then."""
    monkeypatch.setattr(assay, "OUT", str(tmp_path))
    monkeypatch.setattr(assay, "CPLUS_REGISTERED", "C+L1")
    assert assay.resign_reserve_h() == pytest.approx(assay.RESIGN_RESERVE_H)
    d = str(tmp_path / "134b-20260912")
    flagged = dict(_arr(3, 50.0), units=[{"k": 1, "func": "sign", "bk": 0.0, "a": 50.0, "flip": True, "prod": 50.0}])
    c = _rec("C+L1", arrivals=[_arr(0, 20.0), _arr(1, 7.0), _arr(2, 5.0), flagged])  # 20 and 7 are >= a16 6.2831
    assert assay.resign_eligible(c) == 2
    _write(d, "C+L1", c)
    _write(d, "A0", _rec("A0", arrivals=[_arr(0, 20.0)]))  # A0 is never in the reserve
    _write(d, "P5", _rec("P5", arrivals=[_arr(i, 20.0) for i in range(500)]))  # capped at 400
    assert assay.resign_reserve_h() == pytest.approx(assay.resign_cost_h(5 * 400 + 2 + 400))  # B0, P1-P4 at the cap; C+L1 2; P5 400
