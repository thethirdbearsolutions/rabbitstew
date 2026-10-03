"""RBT-129 Stage 2 plan (runs/RBT-129/stage2-plan/): every rule the skeleton registers, on made-up numbers.

No Stage-2 output exists.  The only repository files read are registered inputs: the accepted Stage-1 record
(``stage1_readout.txt``, checked by sha256), the committed census readout and ``RULINGS-CITED-S2.md``."""
import importlib.util
import math
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCRIPT = os.path.join(REPO, "runs", "RBT-129", "stage2-plan", "stage2_readout.py")
spec = importlib.util.spec_from_file_location("stage2_readout", SCRIPT)
s2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s2)
sr = s2.sr
H, D = sr.H, sr.D


# --- 1 registered inputs -------------------------------------------------------------------------------------------

def test_the_inputs_are_the_accepted_stage1_record():
    assert s2.check_inputs() == []
    assert len(s2.STAGE2A_POINTS) == 12 and len(set(s2.STAGE2A_POINTS)) == 12
    assert len(s2.RB_GO1_POINTS) == 9


def test_every_stage2a_point_is_a_stage1_midpoint_and_not_a_stage1_point():
    mids = {m for _, _, m, _ in sr.ra_pairs()}
    assert set(s2.STAGE2A_POINTS) <= mids
    assert not set(s2.STAGE2A_POINTS) & set(sr.STAGE1_POINTS)


def test_a_changed_record_is_reported(tmp_path):
    p = tmp_path / "x.txt"
    p.write_text(open(s2.STAGE1_TXT).read().replace("c1-p018-PW-L\n", "c1-p018-U-L\n"))
    assert s2.check_inputs(str(p))


# --- 2 what runs ---------------------------------------------------------------------------------------------------

def test_the_stage2a_gate_from_the_committed_census():
    cen = sr.census_layer(s2.CENSUS_TXT)
    m, n, _ = s2.mn_gate(s2.STAGE2A_POINTS, cen, s2.M_CAP["2a"], s2.N_CAP["2a"])
    assert m == ["c1-p018-PW-L", "c1-p053-U-L", "c1-p053-U-G"]
    assert n == ["c1-p018-PW-L"]


def test_the_gate_frees_a_slot_with_no_valid_seed_and_respects_caps():
    cen = {"ff": {H: set(), D: {"b"}}, "points": {"a": ("", "0.5"), "b": ("", "0.6"), "c": ("", "0.7"),
                                                  "d": ("", "0.9"), "e": ("", "1.2"), "f": ("", "--")}}
    m, n, _ = s2.mn_gate("abcdef", cen, 2, 1, anchors=())
    assert m == ["a", "c"] and n == ["a"]
    m, n, _ = s2.mn_gate("abcdef", cen, 2, 1, valid={"a": 0, "c": 3, "d": 4}, anchors=())
    assert m == ["c", "d"] and n == ["c"]
    m, _, _ = s2.mn_gate("abcdef", cen, 4, 2, anchors=("a",))
    assert "a" not in m and "b" not in m and "e" not in m and "f" not in m


def test_the_budget():
    assert s2.rb_stage2a_slots() == 11
    b = s2.budget(3, 1, s2.rb_stage2a_slots(), 3, 1)                       # O-2's re-simulation (REQUIRED)
    assert b["2a S"][0] == pytest.approx(12 * 2400 * 23.35 / 3600)
    assert b["2a total"] == pytest.approx((236.6, 443.0), abs=0.06)
    assert b["2b(2a) total"] == pytest.approx((221.0, 413.9), abs=0.06)
    assert b["total"] == pytest.approx((457.7, 856.9), abs=0.06)
    b = s2.budget(3, 1, s2.rb_stage2a_slots(), 3, 1, resim_129001=False)   # census adoption, if the owner declines
    assert b["2a S"][0] == pytest.approx(12 * 2340 * 23.35 / 3600)
    assert b["total"] == pytest.approx((453.0, 848.2), abs=0.06)


# --- 3 the build and overflow handling (S2-R2) -------------------------------------------------------------------

import json  # noqa: E402

SHA = "7ae75f7fe32e437b2c7283930f38f20adfa33bbe4895c5d91b0c95233814edb8"


U = "rbt-129-s2a-c1-p053-U-G-129003-S"


def _log(*attempts, unit=U):
    """Synthetic epa_overflow.jsonl lines in the tooling's format: each attempt = (seasons, overflow_at); the attempt id
    is 0-based, the number of start lines already in the log."""
    out = []
    for k, (seasons, over_at) in enumerate(attempts):
        out.append(json.dumps({"start": "T", "unit": unit, "attempt": k, "pid": 10 + k, "libmujoco_sha256": SHA}))
        for s in seasons:
            out.append(json.dumps({"season": s, "pid": 10 + k}))
            out.append(json.dumps({"event": "near", "unit": unit, "attempt": k, "nedges": 18, "pid": 20 + k, "seq": s}))
            if s in over_at:
                out.append(json.dumps({"event": "overflow", "unit": unit, "attempt": k, "nedges": 25, "pid": 20 + k}))
    return out


def test_clean_overflowed_unlogged():
    log = s2.parse_epa_log(_log((range(60, 300), ())), unit=U)
    assert s2.unit_state(log, range(60, 300), registered_sha=SHA) == s2.CLEAN
    log = s2.parse_epa_log(_log((range(60, 300), (150,))))
    assert s2.unit_state(log, range(60, 300)) == s2.OVERFLOWED
    log = s2.parse_epa_log(_log((range(60, 299), ())))
    assert s2.unit_state(log, range(60, 300)) == s2.UNLOGGED


def test_a_season_counts_from_its_last_attempt():
    # attempt 0 overflowed at 150 and was killed; the resume re-ran 120-299 cleanly: the kept data are clean
    log = s2.parse_epa_log(_log((range(60, 160), (150,)), (range(120, 300), ())))
    assert s2.unit_state(log, range(60, 300)) == s2.CLEAN


def test_attested_crash_needs_both_counting_attempts():
    log = s2.parse_epa_log(_log((range(60, 200), (199,)), (range(190, 200), (199,))))
    assert s2.unit_state(log, range(60, 300), crashed=[(0, 2, True), (1, 1, True)]) == s2.CRASHED


@pytest.mark.parametrize("attempts,counting", [
    # an earlier attempt overflowed and survived; the two counted crashes have no overflow: unattested (finding 2)
    (((range(60, 150), (100,)), (range(140, 200), ()), (range(190, 200), ())), [(1, 2, True), (2, 1, True)]),
    # one of the two counting attempts is unattested
    (((range(60, 200), (199,)), (range(190, 200), ())), [(0, 2, True), (1, 1, True)]),
    # neither counting attempt at WORKERS=1
    (((range(60, 200), (199,)), (range(190, 200), (199,))), [(0, 2, True), (1, 2, True)]),
    # only one native exit
    (((range(60, 200), (199,)), (range(190, 200), (199,))), [(0, 1, True), (1, 2, False)]),
    # not consecutive
    (((range(60, 200), (199,)), (range(190, 200), ()), (range(190, 200), (199,))), [(0, 1, True), (2, 2, True)]),
])
def test_unattested_or_uncounted_crashes_are_a_help(attempts, counting):
    with pytest.raises(s2.Stage2Help):
        s2.unit_state(s2.parse_epa_log(_log(*attempts)), range(60, 300), crashed=counting)


def test_build_record_helps():
    with pytest.raises(s2.Stage2Help):
        s2.unit_state(s2.parse_epa_log([]), range(60, 300))
    log = s2.parse_epa_log(_log((range(60, 300), ())))
    with pytest.raises(s2.Stage2Help):
        s2.unit_state(log, range(60, 300), registered_sha="0" * 64)
    with pytest.raises(s2.Stage2Help):
        s2.parse_epa_log([json.dumps({"event": "overflow", "unit": U, "attempt": 0, "nedges": 25})])
    with pytest.raises(s2.Stage2Help):
        s2.parse_epa_log(_log((range(60, 62), ())), unit="rbt-129-other")
    cut = s2.parse_epa_log(_log((range(60, 300), ())) + ['{"event": "over'])
    assert cut["bad"] == 1


def test_s60_overflow_propagates_to_m_and_n():
    st = {(1, "S"): s2.CLEAN, (1, "M"): s2.CLEAN, (1, "N"): s2.CRASHED, (2, "S"): s2.CLEAN}
    out = s2.propagate_s60(st, {1: True})
    assert out[(1, "S")] == out[(1, "M")] == s2.OVERFLOWED and out[(1, "N")] == s2.CRASHED and out[(2, "S")] == s2.CLEAN


def test_the_crash_ceiling():
    assert s2.crash_ceiling([("a", "2a")]) == "continue"
    assert s2.crash_ceiling([("a", "2a"), ("b", "GO-1")]) == "continue"
    assert s2.crash_ceiling([("a", "2a"), ("a", "2b")]).startswith("STOP")
    assert s2.crash_ceiling([("a", "2a"), ("b", "GO-1"), ("c", "2b")]).startswith("STOP")


def test_ksalt_with_an_overflow_is_a_help():
    assert s2.ksalt_outcome("PASS", True) == "PASS"
    assert s2.ksalt_outcome("VOID", False) == "VOID"
    with pytest.raises(s2.Stage2Help):
        s2.ksalt_outcome("VOID", True)


def test_keep_seed_by_rule():
    assert s2.OVERFLOW_RULES == ("include-flagged", "exclude-known-flagged")
    for mode in s2.OVERFLOW_RULES:
        assert s2.keep_seed(s2.CLEAN, mode) and s2.keep_seed(s2.UNSCANNED, mode)
        assert not s2.keep_seed(s2.CRASHED, mode)
    for st in (s2.OVERFLOWED, s2.UNLOGGED):
        assert s2.keep_seed(st, "include-flagged") and not s2.keep_seed(st, "exclude-known-flagged")


def test_check_build():
    assert s2.check_build(SHA, SHA) and not s2.check_build(SHA, "0" * 64) and not s2.check_build("abc", "abc")


def _p(n, ext_h=0, ext_d=0, valid=None):
    valid = n if valid is None else valid
    merge = {j: (True, True) for j in range(1, valid + 1)}
    merge.update({j: (True, False) for j in range(valid + 1, n + 1)})
    return {"n": n, "extinct": {H: ext_h, D: ext_d}, "valid_share": valid, "merge": merge, "n_ran": False}


def test_crash_bound_robust_and_sensitive():
    r = s2.crash_bounded_body(_p(7), {8: (True, True)})
    assert r["primary"] == "NOT RUN" and r["word"] == "crash-robust"
    r = s2.crash_bounded_body(_p(7, ext_d=4), {8: (True, True)})
    assert r["primary"] == "NOT RUN" and "EXCLUDED-D" in r["feasible"] and r["word"] == "CRASH-SENSITIVE"


def test_crash_bound_enumerates_feasible_states_only():
    # the adversary's case: H extinct on 4 of 7, the crashed seed's ckpt60 shows H dead at 59
    p = _p(7, ext_h=4)
    for j in range(5, 8):
        p["merge"][j] = (True, True)
    r = s2.crash_bounded_body(p, {8: (False, True)})
    assert r["feasible"] == {"EXCLUDED-H"} and r["primary"] == "NOT RUN"
    assert r["word"] == "primary infeasible given ckpt60"


def test_crash_affected_income_marks_small_counting_sets():
    aff = s2.crash_affected({"a": "EARNS-H", "b": "EARNS-H", "c": "EARNS-D"}, {"a": 1})
    assert aff == {"a": True, "b": False, "c": False}
    assert s2.verdict_crash_mark({"EARNS-H": ["a", "b"]}, aff)
    assert not s2.verdict_crash_mark({"EARNS-H": ["a", "b", "x"]}, aff)
    assert not s2.verdict_crash_mark({"EARNS-D": ["c"]}, aff)


# --- 4 the C3 pins ---------------------------------------------------------------------------------------------------

def test_c3_1_k2_scope():
    assert not s2.share_void(False, ["1"], {"1": False}, None)       # no N: never VOID
    assert s2.share_void(True, ["1"], {"1": False}, "PASS")          # pooled FAIL in the point's stage
    assert s2.share_void(True, ["1", "2b"], {"1": False, "2b": True}, "PASS")   # either half's stage
    assert not s2.share_void(True, ["2a"], {"2a": True}, "PASS")
    assert s2.share_void(True, ["2a"], {"2a": True}, "FAIL")


def _pt(body="NOT RUN", income="UNDECIDED", **kw):
    return dict({"body": body, "income": income, "lever": False, "vd": False, "m_arm": False, "resolving": False}, **kw)


def test_c3_2_verdict5_registered_tolerates_one_and_literal_does_not():
    pts = {"a": _pt(income="EARNS-D"), "b": _pt(income="EARNS-D"), "c": _pt(income="EARNS-H"),
           "e1": _pt(body="EXCLUDED-D", income="NOT TESTED"), "e2": _pt(body="EXCLUDED-D", income="NOT TESTED")}
    reg = sr.verdicts(pts, "does not reject", lambda p: False)
    assert "DEPENDS ONLY THROUGH HABITABILITY (D)" in reg
    assert s2.verdict5_literal(pts, lambda p: False) == []
    del pts["c"]
    assert s2.verdict5_literal(pts, lambda p: False) == ["DEPENDS ONLY THROUGH HABITABILITY (D)"]
    pts["t"] = _pt(income="EARNS-TIE")   # R2: any EARNS-TIE fails both readings
    assert "DEPENDS ONLY THROUGH HABITABILITY (D)" not in sr.verdicts(pts, "does not reject", lambda p: False)
    assert s2.verdict5_literal(pts, lambda p: False) == []


def test_c3_2_hinge_marks_v5_tolerance_sensitive():
    # MAJOR 6's scenario: one EARNS-H survives, uncorroborated; 6 EARNS-D; a counting set of survival calls for H
    pts = {f"d{i}": _pt(income="EARNS-D") for i in range(6)}
    pts["h"] = _pt(body="PARTIAL-D", income="EARNS-H")
    pts.update({f"s{i}": _pt(body="EXCLUDED-D", income="NOT TESTED") for i in range(4)})
    reg, lit, mark = s2.v5_mark(pts, "rejects", lambda p: False)
    assert reg == "DEPENDS ONLY THROUGH HABITABILITY (D)" and lit == "NOT RESOLVED"
    assert mark == "V5-TOLERANCE-SENSITIVE"
    pts["h2"] = _pt(body="PARTIAL-D", income="EARNS-H")   # two EARNS-H: both readings give EARNINGS DEPEND
    assert s2.v5_mark(pts, "rejects", lambda p: False) == ("EARNINGS DEPEND", "EARNINGS DEPEND", "")


def test_c3_3_scorecard_item2_is_scored_on_body_calls():
    pts = {p: {"n_ran": False, "body": "EXCLUDED-H" if i < 21 else "NOT RUN", "resolving": False}
           for i, p in enumerate(sr.STAGE1_POINTS)}
    for p in list(sr.STAGE1_POINTS)[:4]:
        pts[p] = {"n_ran": True, "body": "PARTIAL-D", "resolving": False}
    r = s2.scorecard_item2(pts)
    assert r["registered"] == "NOT SHOWN (15 of 36; RESOLVING 0)"
    assert "gated out at 32 of 36" in r["gated"] and "not RESOLVING at 4 of 4" in r["n_points"]
    assert r["gated"].startswith("NON-REGISTERED") and r["n_points"].startswith("NON-REGISTERED")


def test_c3_3_matches_the_stage1_scripted_line():
    want = [l for l in open(s2.STAGE1_TXT) if "share NOT RUN or SATURATED" in l][0]
    assert "NOT SHOWN (15 of 36; RESOLVING 0)" in want   # the pre-data code's reading, which S2-R1 keeps


def test_c3_4_share_model_scope():
    pts = {"c2-p030-U-G": _pt(m_arm=True), "c1-p080-HP-L": _pt(body="PARTIAL-D", m_arm=True),
           "c1-p053-U-G": _pt(m_arm=True), "c1-p030-U-G": _pt()}
    assert s2.share_model_points(pts) == ["c1-p080-HP-L", "c2-p030-U-G"]          # registered: the pre-data code
    assert s2.share_model_points(pts, scope="habitable") == ["c2-p030-U-G"]       # non-registered line


def test_c3_5_uncensored_per_birth():
    # a life born at b is evaluated b+1 .. b+60 at most; its last row must precede the last season (regime.py:175)
    assert s2.PER_BIRTH_WINDOW == (180, 238) and s2.PER_BIRTH_WINDOW[1] + 60 < sr.SEASON_END
    assert s2.per_birth_uncensored({"complete_lives": 40, "censored_lives": 0, "net_per_birth": 0.1}) == pytest.approx(0.35)
    assert s2.per_birth_uncensored({"complete_lives": 0}) is None and s2.per_birth_uncensored(None) is None
    with pytest.raises(s2.Stage2Help):
        s2.per_birth_uncensored({"complete_lives": 40, "censored_lives": 1, "net_per_birth": 0.1})
    assert sr.marginal({H: s2.per_birth_uncensored({"complete_lives": 3, "net_per_birth": -0.1}), D: 0.5})


# --- 5 the final map -------------------------------------------------------------------------------------------------

X1 = [0.31, 0.12, 0.25, 0.40, 0.05, 0.22, 0.18, 0.29]
X2 = [0.21, 0.33, 0.10, 0.27, 0.19, 0.36, 0.08, 0.24]
T1 = [0.02, -0.05, 0.04, 0.01, -0.03, 0.03, 0.00, -0.01]
T2 = [0.01, -0.02, 0.03, -0.04, 0.02, 0.00, 0.01, -0.01]


def test_combination_agrees_with_the_stage1_registered_function():
    for x1, x2 in ((X1, X2), (T1, T2), ([-v for v in X1], X2)):
        c = s2.combined_p(x1, x2)
        for e in (True, False):
            for t in (True, False):
                want = sr.stage2_income_call(x1, x2, lambda p, e=e, pp=c["p_earns"]: e and p == pytest.approx(pp),
                                             lambda p, t=t, pp=c["p_tie"]: t and p == pytest.approx(pp))
                got = sr.income_call(c["mean"], e, t)
                assert got == want


def test_combination_is_symmetric_and_a_tie_reads_tie():
    a, b = s2.combined_p(X1, X2), s2.combined_p(X2, X1)
    assert a["p_earns"] == pytest.approx(b["p_earns"]) and a["p_earns"] < 0.001
    assert s2.combined_p(T1, T2)["p_tie"] < 0.001


def test_median_unbiased_is_the_mean_of_half_means_at_equal_sd():
    x2 = [v + 0.1 for v in X1]
    assert s2.median_unbiased(X1, x2) == pytest.approx(sum(X1) / 8 + 0.05, abs=1e-6)


@pytest.mark.parametrize("sign", (1, -1))
def test_extreme_halves_are_symmetric_and_finite(sign):
    huge = [sign * (5.0 + 1e-6 * i) for i in range(8)]         # t in the tens of thousands at df 7
    z = s2._z_upper(huge, 0.0)
    assert math.isfinite(z) and sign * z > 8 and s2._z_upper([-v for v in huge], 0.0) == pytest.approx(-z)
    c = s2.combined_p(huge, [-v for v in huge])          # two opposite extreme halves cancel
    assert c["z"] == pytest.approx(0.0, abs=1e-9)
    assert s2._z_upper([sign * v for v in X1], 0.0) == pytest.approx(-s2._z_upper([-sign * v for v in X1], 0.0))


def test_point_tests_and_final_bh():
    t = {"ext": s2.point_income_test(X1, X2), "one": s2.point_income_test(X1), "short": s2.point_income_test(X1, [0.2]),
         "none": s2.point_income_test([0.3]), "tie": s2.point_income_test(T1, T2)}
    assert t["ext"]["how"] == "combined" and t["ext"]["n"] == 16
    assert t["short"]["how"] == "half 2 short" and t["one"]["how"] == "half 1"
    assert t["none"]["p_earns"] is None
    calls = s2.final_income_calls(t)
    assert calls["ext"] == "EARNS-H" and calls["tie"] == "EARNS-TIE" and calls["none"] == "NOT TESTED"


def test_m4_weights():
    w = s2.m4_weights(sr.STAGE1_POINTS, s2.STAGE2A_POINTS)
    for s in ("G", "L"):
        assert sum(v for p, v in w.items() if p.endswith("-" + s)) == pytest.approx(1.0)
    assert all(v > 0 for v in w.values())
    w0 = s2.m4_weights(sr.STAGE1_POINTS, ())
    assert w0["c1-p030-U-G"] == pytest.approx(1 / 27) and w0["c1-p030-U-L"] == pytest.approx(1 / 9)


# --- 6 the locks (S2-R3) ------------------------------------------------------------------------------------------

def _rulings(tmp_path, **kw):
    lines = {"2B2A:": "COMMITTED", "GO-ID-2A:": "RBT129-S2-2A-GO-1", "GO-ID-INTERIM:": "RBT129-S2-INTERIM-GO-1",
             "GO-ID-FINAL:": "RBT129-S2-FINAL-GO-1", "OVERFLOW-RULE:": "include-flagged", "BUILD-SHA256:": SHA}
    lines.update(kw)
    p = tmp_path / "r.md"
    p.write_text("".join(f"{k} {v}\n" for k, v in lines.items() if v is not None))
    return str(p)


def test_the_committed_locks_are_pending_or_well_formed():
    """Not stale when the coordinator opens a lock (finding 13 (e)): each tag is either still -PENDING or ruled and
    well formed, and no step may run while any is pending."""
    text = open(s2.RULINGS).read()
    for tag in s2.RULED_TAGS:
        pending = tag[:-1] + "-PENDING:"
        ruled = s2.ruled(tag)
        assert (pending in text and not ruled) or len(ruled) == 1
    if any(not s2.ruled(t) for t in s2.RULED_TAGS):
        for step, tag in s2.STEP_GO.items():
            assert s2.refusal(step, s2.GO_IDS[tag])
            assert s2.main([step, "--go", s2.GO_IDS[tag]]) == 9


def test_every_lock_must_open(tmp_path):
    assert s2.refusal("interim", "RBT129-S2-INTERIM-GO-1", _rulings(tmp_path)) == ""
    assert s2.refusal("final", "RBT129-S2-FINAL-GO-1", _rulings(tmp_path)) == ""
    assert "no GO" in s2.refusal("final", "RBT129-S2-INTERIM-GO-1", _rulings(tmp_path))    # a step's own lock only
    assert "no GO" in s2.refusal("interim", "RBT129-S2-INTERIM-GO-1", _rulings(tmp_path, **{"GO-ID-INTERIM:": None}))
    assert "2a" in s2.refusal("interim", "RBT129-S2-INTERIM-GO-1", _rulings(tmp_path, **{"GO-ID-2A:": None}))
    assert "2b(2a)" in s2.refusal("interim", "RBT129-S2-INTERIM-GO-1", _rulings(tmp_path, **{"2B2A:": "MAYBE"}))
    assert "overflow" in s2.refusal("interim", "RBT129-S2-INTERIM-GO-1",
                                    _rulings(tmp_path, **{"OVERFLOW-RULE:": "exclude-flagged"}))
    assert "build" in s2.refusal("interim", "RBT129-S2-INTERIM-GO-1", _rulings(tmp_path, **{"BUILD-SHA256:": "abc"}))
    assert s2.refusal("interim", "RBT129-S2-INTERIM-GO-1", _rulings(tmp_path, **{"2B2A:": "DECLINED"})) == ""


def test_duplicated_or_empty_ruled_lines_are_a_help(tmp_path):
    p = _rulings(tmp_path)
    open(p, "a").write("GO-ID-FINAL: OTHER\n")
    assert s2.refusal("final", "RBT129-S2-FINAL-GO-1", p).startswith("HELP")
    p = _rulings(tmp_path)
    open(p, "a").write("BUILD-SHA256:\n")
    assert s2.refusal("final", "RBT129-S2-FINAL-GO-1", p).startswith("HELP")


def test_the_quarantine_list(tmp_path):
    assert s2.is_quarantined("ckpt/" + sr.QUARANTINED_LABEL.upper())
    assert not s2.is_quarantined("ckpt/rbt-129-s2a-c1-p053-U-G-129003-M")
    p = _rulings(tmp_path)
    open(p, "a").write("QUARANTINE: rbt-129-s2a-c1-p053-U-G-129003-M\n")
    assert s2.is_quarantined("refs/heads/ckpt/rbt-129-s2a-c1-p053-u-g-129003-m-x", p)


# --- §4.5 / S2-R1: the committed §9.1 computation --------------------------------------------------------------------

S91 = os.path.join(REPO, "runs", "RBT-129", "stage2-plan", "s91_rule_chosen.txt")


def test_the_committed_s91_output_reproduces_the_stage1_per_birth_and_rules_9_1():
    """Its censored (240) column must equal the per-birth income the accepted Stage-1 record printed (3 decimals), so
    the reader is the readout's; and the registered §9.1 choice is the committed one."""
    text = open(S91).read()
    s1 = {}
    pid = None
    for line in open(s2.STAGE1_TXT):
        m = __import__("re").match(r"  (c\S+)\s{2,}", line)
        if m and "share" in line:
            pid = m.group(1)
        m = __import__("re").search(r"per-birth income \(net of work; O-5\) H (\S+) D (\S+);", line)
        if m and pid:
            s1[pid] = (m.group(1), m.group(2))
    rows = [l for l in text.splitlines() if l.startswith("  c")]
    assert len(rows) == 8
    for l in rows:
        p = l.split()[0]
        h, d = l.split("| 240: H ")[1].split(" | ")[0].split(" D ")
        d = d.split()[0]
        assert (f"{float(h):+.3f}", f"{float(d):+.3f}") == s1[p], p
    assert sum(1 for l in rows if l.rstrip().endswith("MARGINAL")) == 2
    assert "the registered §9.1 choice: H-sign none; D-sign c0-p080-HP-G" in text
    assert "printed only: H-sign none; D-sign none" in text
