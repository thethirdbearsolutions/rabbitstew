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
    b = s2.budget(3, 1, s2.rb_stage2a_slots(), 3, 1)
    assert s2.rb_stage2a_slots() == 11
    assert b["2a S"][0] == pytest.approx(12 * 2340 * 23.35 / 3600)
    assert b["2a total"] == pytest.approx((231.9, 434.3), abs=0.06)
    assert b["2b(2a) total"] == pytest.approx((221.0, 413.9), abs=0.06)
    assert b["total"] == pytest.approx((453.0, 848.2), abs=0.06)


# --- 3 the build and overflow handling ----------------------------------------------------------------------------

OVF = "RBT_HZN overflow: nedges 25 (cap 24), EPA iteration 32, nverts 37, nfaces 133, geom 30 type 6, geom 32 type 5\n"
STAT0 = "epa_iterations 396701 overflow 0 hist 3:140887 4:146634 10:4\n"
STAT1 = "epa_iterations 100 overflow 1 hist 3:50 25:1\n"


def test_parse_hzn_and_unit_states():
    clean = s2.parse_hzn(["some other stderr\n"], [STAT0])
    assert clean["overflow_lines"] == 0 and clean["max_horizon"] == 10
    assert s2.unit_state(True, clean) == s2.CLEAN
    flagged = s2.parse_hzn([OVF], [STAT0, STAT1])
    assert flagged["processes"] == 2 and flagged["max_horizon"] == 25
    assert s2.unit_state(True, flagged) == s2.FLAGGED
    assert s2.unit_state(False, flagged, crashed=True) == s2.CRASHED


@pytest.mark.parametrize("args", [
    (False, {"overflow_lines": 0, "processes": 1, "stats_overflow": 0}, True),   # crash, no attesting line
    (False, {"overflow_lines": 0, "processes": 1, "stats_overflow": 0}, False),  # neither done nor crashed
    (True, {"overflow_lines": 0, "processes": 0, "stats_overflow": 0}, False),   # no build record
    (True, None, False),
    (True, {"overflow_lines": 1, "processes": 1, "stats_overflow": 0}, False),   # stderr and stats disagree
])
def test_unclassifiable_units_are_a_help(args):
    with pytest.raises(s2.Stage2Help):
        s2.unit_state(*args)


def test_a_malformed_overflow_line_is_a_help():
    with pytest.raises(s2.Stage2Help):
        s2.parse_hzn(["RBT_HZN overflow: garbled\n"], [STAT0])


def test_keep_seed_by_rule():
    for mode in s2.OVERFLOW_RULES:
        assert s2.keep_seed(s2.CLEAN, mode) and s2.keep_seed(s2.UNSCANNED, mode)
        assert not s2.keep_seed(s2.CRASHED, mode)
    assert s2.keep_seed(s2.FLAGGED, "include-flagged") and not s2.keep_seed(s2.FLAGGED, "exclude-flagged")


def test_check_build():
    assert s2.check_build("ab", "ab") and not s2.check_build("ab", "cd") and not s2.check_build("", "")


def _p(n, ext_h=0, ext_d=0, valid=None):
    valid = n if valid is None else valid
    merge = {j: (True, True) for j in range(1, valid + 1)}
    merge.update({j: (True, False) for j in range(valid + 1, n + 1)})
    return {"n": n, "extinct": {H: ext_h, D: ext_d}, "valid_share": valid, "merge": merge, "n_ran": False}


def test_crash_bound_robust_and_sensitive():
    primary, calls, word = s2.crash_bounded_body(_p(7), {8: (True, True)})
    assert primary == "NOT RUN" and word == "crash-robust"
    # 4 of 7 extinct D: n 8 restores EXCLUDED-D (>= 5) if the crashed seed lost D
    primary, calls, word = s2.crash_bounded_body(_p(7, ext_d=4), {8: (True, True)})
    assert primary == "NOT RUN" and "EXCLUDED-D" in calls and word == "CRASH-SENSITIVE"


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


def test_c3_3_scorecard_item2_counts_where_the_share_layer_ran():
    pts = {p: {"n_ran": False, "body": "EXCLUDED-H" if i < 10 else "NOT RUN", "resolving": False}
           for i, p in enumerate(sr.STAGE1_POINTS)}
    for p in list(sr.STAGE1_POINTS)[:4]:
        pts[p] = {"n_ran": True, "body": "PARTIAL-D", "resolving": False}
    assert s2.scorecard_item2(pts) == ("AS PREDICTED", 32, 36, 0)
    for p in list(sr.STAGE1_POINTS)[:3]:
        pts[p]["resolving"] = True
    assert s2.scorecard_item2(pts)[0] == "NOT SHOWN"


def test_c3_4_share_model_scope():
    pts = {"c2-p030-U-G": _pt(m_arm=True), "c1-p080-HP-L": _pt(body="PARTIAL-D", m_arm=True),
           "c1-p053-U-G": _pt(m_arm=True), "c1-p030-U-G": _pt()}
    assert s2.share_model_points(pts) == ["c2-p030-U-G"]
    assert s2.share_model_points(pts, scope="all") == ["c1-p080-HP-L", "c2-p030-U-G"]


def test_c3_5_uncensored_per_birth():
    assert s2.PER_BIRTH_WINDOW == (180, 239) and s2.PER_BIRTH_WINDOW[1] + 59 < sr.SEASON_END
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


# --- 6 the locks -----------------------------------------------------------------------------------------------------

def test_the_committed_locks_are_closed():
    assert s2.go_ids() == set()
    assert s2.refusal(s2.GO_ID)
    assert s2.ruled("OVERFLOW-RULE:") == set() and s2.ruled("BUILD-SHA256:") == set()
    assert f"GO-ID-PENDING: {s2.GO_ID}" in open(s2.RULINGS).read()
    assert s2.main(["final", "--go", s2.GO_ID]) == 9


def test_every_lock_must_open(tmp_path):
    p = tmp_path / "r.md"
    base = f"GO-ID: {s2.GO_ID}\n"
    p.write_text(base)
    assert "overflow" in s2.refusal(s2.GO_ID, str(p))
    p.write_text(base + "OVERFLOW-RULE: something-else\n")
    assert "overflow" in s2.refusal(s2.GO_ID, str(p))
    p.write_text(base + "OVERFLOW-RULE: include-flagged\n")
    assert "build" in s2.refusal(s2.GO_ID, str(p))
    p.write_text(base + "OVERFLOW-RULE: include-flagged\nBUILD-SHA256: abc\n")
    assert s2.refusal(s2.GO_ID, str(p)) == ""
    assert s2.refusal("OTHER", str(p))
    p.write_text("GO-ID:\nOVERFLOW-RULE: include-flagged\nBUILD-SHA256: abc\n")
    assert s2.refusal("", str(p))
