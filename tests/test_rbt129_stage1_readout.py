"""RBT-129 Stage 1 readout (runs/RBT-129/stage1-readout/): the quarantine refusal, the integrity checks, and every
registered rule of READOUT-PLAN.md on made-up numbers.

No Stage-1 output is read here.  The only repository files read are registered inputs: the lane files, the M/N launch
record and gate table, and the committed Stage 0 readout (C1 rows).  Every run directory is a synthetic fixture."""
import importlib.util
import json
import math
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCRIPT = os.path.join(REPO, "runs", "RBT-129", "stage1-readout", "stage1_readout.py")
spec = importlib.util.spec_from_file_location("stage1_readout", SCRIPT)
sr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sr)

H, D = sr.H, sr.D
QDIR = sr.QUARANTINED_DIR
QLAB = sr.QUARANTINED_LABEL


class CountingReader:
    """A stand-in for ``stages.branch_file`` that records every call and answers from a dict."""

    def __init__(self, files=None, default=None):
        self.calls, self.files, self.default = [], files or {}, default

    def __call__(self, label, member):
        self.calls.append((label, member))
        return self.files.get((label, member), self.default(label, member) if callable(self.default) else self.default)


# --- 2.5 the quarantine refusal (RULING.md item 3) ------------------------------------------------------------------

@pytest.mark.parametrize("label", [QLAB, "ckpt/" + QLAB, "refs/heads/ckpt/" + QLAB, "origin/ckpt/" + QLAB, QLAB.upper(),
                                   QLAB + "/run.log", QLAB + "-anything"])
def test_the_quarantined_label_is_refused(label):
    with pytest.raises(sr.QuarantineRefusal):
        sr.refuse_quarantined(label=label)


@pytest.mark.parametrize("path", [QDIR, QDIR + "/run.log", QDIR + "/state.json", os.path.join(REPO, QDIR),
                                  os.path.join(REPO, QDIR, "conventional", "best_gen0060.json"), QDIR + "/"])
def test_the_quarantined_directory_is_refused(path):
    with pytest.raises(sr.QuarantineRefusal):
        sr.refuse_quarantined(path=path, root=REPO)


@pytest.mark.parametrize("label", ["rbt-129-stage1-c2-p030-U-G-129001-ckpt60", "rbt-129-stage1-c2-p030-U-G-129001-S",
                                   "rbt-129-stage1-c2-p030-U-G-129001-record", "rbt-129-stage1-c2-p030-U-G-129002-M",
                                   "rbt-129-stage1-c0-p030-PW-G-129001-M"])
def test_neighbours_of_the_quarantined_unit_are_not_refused(label):
    sr.refuse_quarantined(label=label)


def test_the_guarded_reader_refuses_before_calling_the_reader():
    stub = CountingReader(default="x")
    read = sr.guarded_reader(stub)
    for member in ("run.log", "history.json", "platform.json", ".rbt129-done-M", "MANIFEST"):
        with pytest.raises(sr.QuarantineRefusal):
            read(QLAB, member)
    assert stub.calls == []
    assert read("rbt-129-stage1-c2-p030-U-G-129001-ckpt60", "platform.json") == "x"
    assert stub.calls == [("rbt-129-stage1-c2-p030-U-G-129001-ckpt60", "platform.json")]


def test_restore_and_read_run_refuse_the_quarantined_unit_before_touching_anything(tmp_path):
    calls = []
    with pytest.raises(sr.QuarantineRefusal):
        sr.guarded_restore(os.path.join(str(tmp_path), QDIR), root=str(tmp_path), restore=calls.append)
    assert calls == []
    poison = tmp_path / QDIR
    poison.mkdir(parents=True)
    (poison / "config.json").write_text("not json: reading this would fail differently")
    with pytest.raises(sr.QuarantineRefusal):
        sr.read_run(str(poison), root=str(tmp_path))
    sr.guarded_restore(os.path.join(str(tmp_path), "runs/RBT-129/stage1/c2-p030-U-G/129001/ckpt60"),
                       root=str(tmp_path), restore=calls.append)
    assert len(calls) == 1


def test_the_lane_that_schedules_the_quarantined_unit_is_never_loaded():
    mn = os.path.join(REPO, "runs", "RBT-129", "lanes", "1-MN")
    with pytest.raises(sr.QuarantineRefusal):
        sr.load_jobs([os.path.join(mn, sr.LANE0)], REPO)
    one, mnp = sr.lane_paths(REPO)
    assert os.path.join(mn, sr.LANE0) not in mnp and os.path.join(mn, sr.LANE0B) in mnp


def test_any_lane_file_scheduling_the_quarantined_directory_is_refused(tmp_path):
    lane = tmp_path / "copy.jsonl"
    lane.write_text(json.dumps({"job": "fork", "name": sr.CRASHED_JOB, "dir": QDIR,
                                "src": "runs/RBT-129/stage1/c2-p030-U-G/129001/ckpt60"}) + "\n")
    with pytest.raises(sr.QuarantineRefusal):
        sr.load_jobs([str(lane)], REPO)
    with pytest.raises(sr.QuarantineRefusal):
        sr.expected_labels([{"job": "fork", "name": sr.CRASHED_JOB, "dir": QDIR,
                             "src": "runs/RBT-129/stage1/c2-p030-U-G/129001/ckpt60"}], REPO)


def test_a_crashed_seed_is_never_read_and_the_guard_catches_a_caller_that_forgets(tmp_path):
    root = str(tmp_path)
    pid = sr.CRASHED_POINT
    for j in sr.SEEDS:
        _chain(root, pid, j, m=True)
    poison = tmp_path / QDIR
    (poison / "config.json").write_text("{broken")
    pt = sr.assemble_point(root, pid, m_seeds=list(sr.SEEDS), crashed_seeds=[1])
    assert sorted(pt["y_m"]) == [2, 3, 4, 5, 6, 7, 8] and pt["n"] == 8 and 1 in pt["x"]
    assert sr.m_row_label(pid, list(sr.SEEDS), {pid: [1]}) == "M 7 of 8 (1 CRASHED)"
    with pytest.raises(sr.QuarantineRefusal):
        sr.assemble_point(root, pid, m_seeds=list(sr.SEEDS))


# --- the registered inputs this plan's counts come from (lane files and launch records only) -------------------------

def test_the_lane_set_and_its_expected_labels():
    one, mn = sr.lane_paths(REPO)
    assert len(one) == 20 and len(mn) == 20
    jobs = sr.load_jobs(one, REPO) + sr.load_jobs(mn, REPO)
    kinds = {}
    for j in jobs:
        kinds[j["job"]] = kinds.get(j["job"], 0) + 1
    assert kinds == {"fresh": 252, "adopt": 36, "ksalt": 72, "snapshot": 288, "resume": 288, "fork": 37}
    exp = sr.expected_labels(jobs, REPO)
    assert len(exp) == 973 and QLAB not in exp
    assert len(sr.platform_dirs(jobs)) == 613
    assert len(sr.marker_jobs(jobs)) == 973


def test_the_crash_bookkeeping_reconciles_on_the_registered_lanes():
    assert sr.crash_reconcile(os.path.join(REPO, "runs", "RBT-129", "lanes", "1-MN")) == []


def test_the_crash_bookkeeping_fails_on_a_changed_lane(tmp_path):
    mn = os.path.join(REPO, "runs", "RBT-129", "lanes", "1-MN")
    for name in os.listdir(mn):
        (tmp_path / name).write_text(open(os.path.join(mn, name)).read())
    lane0b = (tmp_path / sr.LANE0B)
    lines = lane0b.read_text().splitlines()
    lane0b.write_text("\n".join(lines[:1]) + "\n")
    probs = sr.crash_reconcile(str(tmp_path))
    assert probs and any("minus" in p for p in probs)


def test_the_gate_table_parses_and_the_gate_check_compares():
    t = sr.parse_gate_table(os.path.join(REPO, "runs", "RBT-129", "lanes", "1-MN", "gate_table.txt"))
    assert t["c2-p030-U-G"] == (8, 8, 0) and t["c0-p030-PW-G"] == (2, 2, 2) and t["c0-p080-PW-G"] == (0, 0, 0)
    assert t["c1-p030-PW-G"][0] is None
    assert sum(1 for v in t.values() if v[0] is not None) == 10
    assert sum(v[1] for v in t.values()) == 31 and sum(v[2] for v in t.values()) == 7
    valid = {p: {j: j <= k for j in sr.SEEDS} for p, (k, _, _) in t.items() if k is not None}
    assert sr.gate_mismatches(t, valid) == []
    valid["c2-p030-U-G"][3] = False
    assert sr.gate_mismatches(t, valid) == ["c2-p030-U-G: gate table valid 8, recomputed 7"]


# --- 2.6 MuJoCo provenance -----------------------------------------------------------------------------------------

def _plat(top="3.14.0", resumes=("3.14.0",)):
    return json.dumps({"mujoco": top, "resumes": [{"mujoco": v} for v in resumes]})


def test_platform_passes_only_when_every_record_is_3_14_0():
    assert sr.check_platform(_plat()) == ("PASS", [])
    assert sr.check_platform(_plat(resumes=())) == ("PASS", [])
    assert sr.check_platform(_plat(resumes=("3.14.0", "3.14.0", "3.14.0")))[0] == "PASS"
    v, p = sr.check_platform(_plat(resumes=("3.14.0", "3.15.0")))
    assert v == "FAIL" and p == ["resumes[1]: '3.15.0'"]
    assert sr.check_platform(_plat(top="3.13.0"))[0] == "FAIL"
    assert sr.check_platform(_plat(top=None))[0] == "FAIL"
    assert sr.check_platform(json.dumps({"os": "Linux"}))[0] == "FAIL"
    assert sr.check_platform(None) == ("FAIL", ["no platform.json"])
    assert sr.check_platform("{torn")[0] == "FAIL"
    assert sr.check_platform("[1, 2]")[0] == "FAIL"


def test_platforms_are_read_one_file_at_a_time_from_every_run_directory():
    jobs = [{"job": "resume", "name": "1/a/129001/S", "dir": "runs/RBT-129/stage1/a/129001/S"},
            {"job": "fresh", "name": "1/a/129001/S60", "dir": "runs/RBT-129/stage1/a/129001/S"},
            {"job": "snapshot", "name": "1/a/129001/ckpt60", "dir": "runs/RBT-129/stage1/a/129001/ckpt60", "src": "x"},
            {"job": "ksalt", "name": "1/a/129001/KSALT", "dir": "runs/RBT-129/stage1/a/129001/ksalt"},
            {"job": "fork", "name": "1/a/129001/M", "dir": "runs/RBT-129/stage1/a/129001/M", "src": "x"}]
    stub = CountingReader({("rbt-129-stage1-a-129001-M", "platform.json"): _plat(resumes=("3.14.0", "3.1.0"))},
                          default=_plat())
    res = sr.check_platforms(jobs, sr.guarded_reader(stub), REPO)
    assert res["pass"] == 2 and list(res["fail"]) == ["runs/RBT-129/stage1/a/129001/M"]
    assert {m for _, m in stub.calls} == {"platform.json"} and len(stub.calls) == 3


# --- 2.2 markers, 2.7 K-SALT ----------------------------------------------------------------------------------------

def test_markers_classify_without_reporting_an_extinction_season():
    r = "runs/RBT-129/"
    jobs = [{"job": "resume", "name": "1/a/129001/S", "dir": r + "d/S"}, {"job": "fork", "name": "1/a/129001/M", "dir": r + "d/M"},
            {"job": "resume", "name": "1/a/129002/S", "dir": r + "e/S"}, {"job": "ksalt", "name": "1/a/129002/KSALT", "dir": r + "e/k"}]
    marks = {("rbt-129-d-S", ".rbt129-done-S"): "2026 skipped: extinct pre-merge at season 31",
             ("rbt-129-e-S", ".rbt129-done-S"): "2026"}
    out = sr.check_markers(jobs, CountingReader(marks), REPO)
    assert out == {"done": 1, "extinct": 1, "missing_s": [], "missing_fork": ["1/a/129001/M"],
                   "missing_other": ["1/a/129002/KSALT"]}
    assert "31" not in json.dumps(out)


def test_ksalt_reads_the_unit_record_and_lists_disagreements():
    assert sr.ksalt_word("KSALT PASS: the designed half\n  x") == "PASS"
    assert sr.ksalt_word("KSALT VOID: the designed half") == "VOID"
    assert sr.ksalt_word(None) == "MISSING" and sr.ksalt_word("junk") == "UNREADABLE"
    jobs = [{"job": "ksalt", "name": "1/p/129003/KSALT", "dir": "runs/RBT-129/stage1/p/129003/ksalt",
             "src": "runs/RBT-129/stage1/p/129003/S"}]
    files = {("rbt-129-stage1-p-129003-record", "KSALT.txt"): "KSALT PASS: x",
             ("rbt-129-stage1-p-129003-ksalt", "KSALT.txt"): "KSALT VOID: x",
             ("rbt-129-stage1-p-129003-ksalt", ".rbt129-done-KSALT"): "t KSALT VOID"}
    out = sr.check_ksalt(jobs, CountingReader(files), REPO)
    assert out == {"1/p/129003/KSALT": ("PASS", "VOID", "VOID")}


# --- the integrity driver on a synthetic repository -----------------------------------------------------------------

def _fixture_repo(tmp_path, monkeypatch):
    root = tmp_path
    one = root / "runs/RBT-129/lanes/1"
    mn = root / "runs/RBT-129/lanes/1-MN"
    one.mkdir(parents=True)
    mn.mkdir(parents=True)
    u = "runs/RBT-129/stage1/c2-p030-U-G"
    chain = [{"job": "adopt", "name": "1/c2-p030-U-G/129001/S60", "dir": f"{u}/129001/S"},
             {"job": "snapshot", "name": "1/c2-p030-U-G/129001/ckpt60", "src": f"{u}/129001/S", "dir": f"{u}/129001/ckpt60"},
             {"job": "resume", "name": "1/c2-p030-U-G/129001/S", "dir": f"{u}/129001/S"},
             {"job": "fresh", "name": "1/c2-p030-U-G/129002/S60", "dir": f"{u}/129002/S"},
             {"job": "ksalt", "name": "1/c2-p030-U-G/129002/KSALT", "src": f"{u}/129002/S", "dir": f"{u}/129002/ksalt"},
             {"job": "snapshot", "name": "1/c2-p030-U-G/129002/ckpt60", "src": f"{u}/129002/S", "dir": f"{u}/129002/ckpt60"},
             {"job": "resume", "name": "1/c2-p030-U-G/129002/S", "dir": f"{u}/129002/S"}]
    (one / "host0-lane0.jsonl").write_text("".join(json.dumps(j) + "\n" for j in chain))
    crashed = {"job": "fork", "name": sr.CRASHED_JOB, "src": f"{u}/129001/ckpt60", "dir": f"{u}/129001/M"}
    good = {"job": "fork", "name": "1/c2-p030-U-G/129002/M", "src": f"{u}/129002/ckpt60", "dir": f"{u}/129002/M"}
    (mn / sr.LANE0).write_text(json.dumps(crashed) + "\n" + json.dumps(good) + "\n")
    (mn / sr.LANE0B).write_text(json.dumps(good) + "\n")
    (mn / "launch.txt").write_text("# x\nforks c2-p030-U-G/129001/M c2-p030-U-G/129002/M\n")
    (mn / "gate_table.txt").write_text(open(os.path.join(REPO, "runs/RBT-129/lanes/1-MN/gate_table.txt")).read())
    monkeypatch.setattr(sr, "MN_FORKS_REGISTERED", 2)
    return str(root), chain + [good]


def _gate_ok(root):
    t = sr.parse_gate_table(os.path.join(root, "runs/RBT-129/lanes/1-MN/gate_table.txt"))
    return {p: {j: j <= k for j in sr.SEEDS} for p, (k, _, _) in t.items() if k is not None}


def test_the_gate_check_reads_ckpt60_through_the_guard(tmp_path):
    root = str(tmp_path)
    table = {"c2-p030-U-G": (7, 7, 0), "c1-p030-PW-G": (None, 0, 0)}
    for j in sr.SEEDS:
        _chain(root, "c2-p030-U-G", j, h_alive=j != 8)
    restored = []
    got = sr.gate_valid_from_ckpt60(root, table, restore=restored.append)
    assert got == {"c2-p030-U-G": {j: j != 8 for j in sr.SEEDS}} and len(restored) == 8
    assert sr.gate_mismatches(table, got) == []


def test_the_fork_double_write_check_never_reaches_the_quarantined_unit():
    seen = []
    jobs = [{"job": "fork", "name": "1/a/129002/M", "dir": "runs/RBT-129/stage1/a/129002/M"},
            {"job": "fork", "name": sr.CRASHED_JOB, "dir": QDIR}]
    with pytest.raises(sr.QuarantineRefusal):
        sr.fork_double_writes(jobs, lambda lab: seen.append(lab) or {}, REPO)
    assert seen == ["rbt-129-stage1-a-129002-M"]


def test_integrity_passes_on_a_complete_fixture_and_never_names_the_quarantined_unit(tmp_path, monkeypatch):
    root, jobs = _fixture_repo(tmp_path, monkeypatch)

    def answer(label, member):
        if member == "platform.json":
            return _plat()
        if member == "KSALT.txt":
            return "KSALT PASS: x"
        return "2026-10-02T00:00:00Z"
    stub = CountingReader(default=answer)
    twice = []
    clean = lambda lab: twice.append(lab) or {"lineage.jsonl": {"repeated": 0, "steps_back": 0, "torn": 0}}
    have = set(sr.expected_labels(sr.load_jobs(sr.lane_paths(root)[0], root) + sr.load_jobs(sr.lane_paths(root)[1], root), root))
    gate = _gate_ok(root)
    ok, lines, _ = sr.integrity(root, sr.guarded_reader(stub), have | {QLAB}, None, clean, gate)
    assert ok, lines
    assert all(QLAB.lower() not in lab.lower() for lab, _ in stub.calls)
    assert twice == ["rbt-129-stage1-c2-p030-U-G-129002-M"]
    assert any(sr.CRASHED_LINE in line for line in lines)
    ok2, lines2, _ = sr.integrity(root, sr.guarded_reader(stub), have, {"runs/RBT-129/stage1/c2-p030-U-G/129002/M": "FAIL"},
                                  clean, gate)
    assert not ok2 and any("disagree" in line for line in lines2)
    assert not sr.integrity(root, sr.guarded_reader(stub), have, None, None, gate)[0]  # a check not run fails
    assert not sr.integrity(root, sr.guarded_reader(stub), have, None, clean, None)[0]
    dirty = lambda lab: {"lineage.jsonl": {"repeated": 3, "steps_back": 1, "torn": 0}}
    ok3, lines3, _ = sr.integrity(root, sr.guarded_reader(stub), have, None, dirty, gate)
    assert not ok3 and any("WRITTEN TWICE 1/c2-p030-U-G/129002/M" in line for line in lines3)
    void = CountingReader(default=lambda lab, m: "KSALT VOID: x" if m == "KSALT.txt" else answer(lab, m))
    ok4, lines4, _ = sr.integrity(root, sr.guarded_reader(void), have, None, clean, gate)
    assert not ok4 and any("stream claim re-opens" in line for line in lines4)
    bad_gate = {p: dict(v) for p, v in gate.items()}
    bad_gate["c2-p030-U-G"][1] = False
    assert not sr.integrity(root, sr.guarded_reader(stub), have, None, clean, bad_gate)[0]


def test_integrity_fails_on_a_missing_branch_a_missing_fork_marker_and_a_wrong_mujoco(tmp_path, monkeypatch):
    root, jobs = _fixture_repo(tmp_path, monkeypatch)
    have = set(sr.expected_labels(sr.load_jobs(sr.lane_paths(root)[0], root) + sr.load_jobs(sr.lane_paths(root)[1], root), root))

    def answer(label, member):
        if member == "platform.json":
            return _plat(resumes=("3.15.0",)) if label.endswith("129002-S") else _plat()
        if member == ".rbt129-done-M":
            return None
        return "KSALT PASS" if member == "KSALT.txt" else "t"
    ok, lines, _ = sr.integrity(root, sr.guarded_reader(CountingReader(default=answer)), have - {"rbt-129-stage1-c2-p030-U-G-129002-ksalt"},
                                None, lambda lab: {}, _gate_ok(root))
    text = "\n".join(lines)
    assert not ok
    assert "MISSING ckpt/rbt-129-stage1-c2-p030-U-G-129002-ksalt" in text
    assert "MISSING 1/c2-p030-U-G/129002/M: a candidate second crash" in text
    assert "FAIL runs/RBT-129/stage1/c2-p030-U-G/129002/S" in text


def test_main_refuses_without_the_coordinators_go(capsys):
    assert sr.main(["integrity"]) == 9
    assert sr.main(["readout"]) == 9
    assert "Nothing was read" in capsys.readouterr().err


# --- distributions and tests ----------------------------------------------------------------------------------------

def test_distributions_match_known_values():
    assert abs(sr.t_sf(2.0, 10) - 0.036694) < 1e-5
    assert abs(sr.t_ppf(0.975, 7) - 2.364624) < 1e-4
    assert abs(sr.norm_ppf(0.975) - 1.959964) < 1e-5
    assert abs(sr.chi2_sf(3.841459, 1) - 0.05) < 1e-5
    assert abs(sr.chi2_sf(12.591587, 6) - 0.05) < 1e-5
    assert abs(sr.chi2_sf(1.0, 6) - 0.985612) < 1e-5
    assert abs(sr.f_sf(3.0, 4, 20) - 0.043201) < 1e-5
    assert abs(sr.betainc(2, 3, 0.4) - 0.5248) < 1e-4


def test_one_sample_t_and_tost():
    r = sr.one_sample_t([1.0, 2.0, 3.0, 4.0])
    assert abs(r["t"] - 3.872983) < 1e-5 and abs(r["p"] - 0.030466) < 1e-4
    assert sr.one_sample_t([0.3])["p"] is None and sr.one_sample_t([])["mean"] is None
    assert sr.one_sample_t([0.2, 0.2])["p"] == 0.0 and math.isnan(sr.one_sample_t([0.0, 0.0])["t"])
    assert sr.tost_p([0.01, -0.02, 0.0, 0.015, -0.01, 0.005, 0.0, 0.01], 0.15) < 1e-6
    assert sr.tost_p([0.5, 0.6, 0.55, 0.58], 0.15) > 0.9
    assert sr.tost_p([0.1], 0.15) is None


def test_bh_holm_by():
    p = {"a": 0.01, "b": 0.04, "c": 0.03, "d": 0.2, "e": None}
    assert sr.bh(p, 0.10) == {"a", "b", "c"}
    assert sr.bh({"a": 0.01, "b": 0.06}, 0.10) == {"a", "b"}
    assert sr.bh({"a": 0.051, "b": 0.12}, 0.10) == set()
    assert sr.bh({"a": 0.05, "b": 0.05}, 0.10) == {"a", "b"}
    assert sr.by({"a": 0.01, "b": 0.04, "c": 0.03, "d": 0.2}, 0.10) == {"a"}
    assert sr.holm({"T1": 0.01, "T2": 0.02, "T3": 0.04, "T4": 0.5}) == {"T1"}
    assert sr.holm({"T1": 0.01, "T2": 0.015, "T3": 0.04, "T4": 0.5}) == {"T1", "T2"}
    assert sr.holm_provisional({"T1": 0.012, "T2": 0.02, "T3": 0.4}) == {"T1"}
    assert sr.holm_provisional({"T1": 0.012, "T2": 0.02, "T3": 0.4}) <= sr.holm({"T1": 0.012, "T2": 0.02, "T3": 0.4, "T4": 0.001})


# --- 3 per-seed statistics ------------------------------------------------------------------------------------------

def _hist(alive_by, lo=0, hi=299, births=0, deaths=0):
    """history rows from {kind: f(season) -> alive}; a 0 writes no row after the first (the ecology's empty cohort)."""
    rows = []
    for k, f in alive_by.items():
        dead = False
        for s in range(lo, hi + 1):
            a = f(s)
            if dead:
                continue
            rows.append({"season": s, "population": k, "alive": a, "births": births, "deaths": deaths})
            dead = a == 0
    return rows


def test_alive_reads_a_missing_row_as_zero_and_validity_follows():
    h = _hist({H: lambda s: 30 if s < 100 else 0, D: lambda s: 40})
    assert sr.alive(h, H, 59) == 30 and sr.alive(h, H, 100) == 0 and sr.alive(h, H, 200) == 0
    assert sr.valid_share(h) and not sr.valid_income(h) and sr.extinct_by_end(h, H) and not sr.extinct_by_end(h, D)


def test_member_seasons_and_flow():
    rows = [{"generation": 250, "population": H, "food": 2.0, "work": 10000.0, "last_score": 1.7},
            {"generation": 250, "population": H, "food": 1.0, "work": 0.0, "death": "starved", "last_score": 1.0},
            {"generation": 250, "population": H, "evals": 0, "last_score": 0.0},
            {"generation": 250, "population": H, "food": 9.0, "work": 0.0, "death": "cull"},
            {"generation": 250, "population": H, "food": 9.0, "work": 0.0, "death": "merge-null"},
            {"generation": 239, "population": H, "food": 9.0, "work": 0.0},
            {"generation": 250, "population": D, "food": 0.5, "work": 0.0, "exploded": True, "last_score": 0.0}]
    assert abs(sr.flow(rows, H, 0.03) - ((2.0 - 0.3) + 1.0) / 2) < 1e-12
    assert abs(sr.flow(rows, H, 0.03, variant="survivors") - 1.7) < 1e-12
    assert abs(sr.flow(rows, H, 0.03, variant="p0") - ((2.0 - 0.3) + 1.0 + 0.0) / 3) < 1e-12
    assert sr.flow(rows, D, 0.03) == 0.5 and sr.flow(rows, D, 0.03, net="last_score") == 0.0
    assert sr.flow([], H, 0.03) is None


def test_yprime_uses_120_slots_and_the_empty_world_reads_zero():
    s = _hist({H: lambda s: 30, D: lambda s: 60}, hi=59)
    m = _hist({H: lambda s: 60, D: lambda s: 60})
    assert abs(sr.yprime_m(m, s) - (0.5 - 1 / 3)) < 1e-12
    empty = _hist({H: lambda s: 30 if s < 200 else 0, D: lambda s: 60 if s < 200 else 0})
    assert abs(sr.yprime_m(empty, s) + 1 / 3) < 1e-12
    assert sr.living_share_window(empty) is None
    assert abs(sr.living_share_window(m) - 0.5) < 1e-12
    nn = _hist({D: lambda s: 90, "null_b": lambda s: 30})
    assert abs(sr.yprime_n(nn, s, D) - (0.75 - 2 / 3)) < 1e-12
    none = _hist({H: lambda s: 0, D: lambda s: 0}, hi=59)
    assert sr.yprime_m(m, none) is None


def test_the_bound_under_arbitrary_missingness():
    y7 = [0.1, -0.05, 0.0, 0.2, 0.03, -0.1, 0.07]
    lo, hi = sr.missingness_bound(y7, 0.4)
    assert abs(lo - (sum(y7) - 0.4) / 8) < 1e-12 and abs(hi - (sum(y7) + 0.6) / 8) < 1e-12
    with pytest.raises(ValueError):
        sr.missingness_bound(y7, 1.2)
    with pytest.raises(ValueError):
        sr.missingness_bound(y7[:6], 0.4)


# --- 4 calls --------------------------------------------------------------------------------------------------------

def test_thresholds_at_any_n():
    assert sr.thresholds(8) == (5, 6) and sr.thresholds(16) == (10, 12) and sr.thresholds(12) == (8, 9)
    assert sr.thresholds(6) == (4, 5) and sr.thresholds(7) == (5, 6)


def _p(**kw):
    base = {"n": 8, "extinct": {H: 0, D: 0}, "valid_share": 8, "merge": {j: (True, True) for j in sr.SEEDS},
            "void": False, "n_ran": True, "share": {"mean": 0.0, "rejected": False}, "contingent": False, "tie": False,
            "resolving": False, "anchor": False}
    base.update(kw)
    return base


def test_the_body_call_order():
    assert sr.body_call(_p(extinct={H: 5, D: 6})) == "NEITHER"
    assert sr.body_call(_p(extinct={H: 5, D: 4})) == "EXCLUDED-H"
    assert sr.body_call(_p(extinct={H: 4, D: 5})) == "EXCLUDED-D"
    merge = {1: (True, False), 2: (True, False), 3: (False, True), 4: (True, True), 5: (True, True), 6: (True, True),
             7: (True, True), 8: (True, True)}
    assert sr.body_call(_p(valid_share=5, merge=merge)) == "PARTIAL-H"
    merge[2] = (False, True)
    assert sr.body_call(_p(valid_share=5, merge=merge)) == "PARTIAL-D"
    merge[3] = (False, False)
    assert sr.body_call(_p(valid_share=5, merge=merge)) == "PARTIAL-TIED"
    assert sr.body_call(_p(valid_share=5, merge=merge, void=True)) == "PARTIAL-TIED"  # PARTIAL precedes VOID
    assert sr.body_call(_p(void=True)) == "VOID"
    assert sr.body_call(_p(n_ran=False)) == "NOT RUN"
    assert sr.body_call(_p(n_ran=False, anchor=True)) == "RBT-118 (not available)"
    assert sr.body_call(_p(share={"mean": 0.12, "rejected": True})) == "H-WIN"
    assert sr.body_call(_p(share={"mean": 0.08, "rejected": True})) == "SATURATED"
    assert sr.body_call(_p(share={"mean": -0.1, "rejected": True})) == "D-WIN"
    assert sr.body_call(_p(contingent=True)) == "CONTINGENT"
    assert sr.body_call(_p(tie=True)) == "SATURATED"
    assert sr.body_call(_p(tie=True, resolving=True)) == "TIE"
    assert sr.body_call(_p(resolving=True)) == "UNDECIDED"
    assert sr.body_call(_p(n=7, extinct={H: 5, D: 0})) == "EXCLUDED-H"
    assert sr.body_call(_p(n=7, valid_share=5, merge={j: (True, j > 2) for j in range(1, 8)})) == "PARTIAL-H"


def test_the_income_call():
    assert sr.income_call(0.2, True, False) == "EARNS-H" and sr.income_call(-0.2, True, True) == "EARNS-D"
    assert sr.income_call(0.05, True, True) == "EARNS-TIE" and sr.income_call(0.05, True, False) == "UNDECIDED"
    assert sr.income_call(None, False, False) == "NOT TESTED"


def test_marginal_reads_net_of_work():
    assert sr.per_birth_income(-0.05) == 0.2 and sr.per_birth_income(None) is None
    assert sr.marginal({H: 0.2, D: 0.4}) is True and sr.marginal({H: 0.3, D: 0.4}) is False
    assert sr.marginal({H: None, D: 0.4}) is None


def test_contingent_k2_and_resolving():
    df_stage1 = sr.pooled_null({("c0-p030-PW-G", H): [0.1, -0.1], ("c2-p010-PW-G", D): [0.0], ("c2-p010-PW-G", H): [0.2],
                                ("c1-p010-PW-L", H): [0.05, 0.0], ("c1-p010-PW-G", H): [0.3]})[1]
    assert df_stage1 == 2 and not sr.contingent_callable(df_stage1) and sr.contingent_callable(12)
    ok, m, t, p = sr.k2_pooled([0.01, -0.02, 0.03, 0.0, -0.01, 0.02, 0.01])
    assert ok and abs(m - 0.0057142857) < 1e-9
    assert not sr.k2_pooled([0.06, 0.07, 0.05, 0.08, 0.06, 0.07, 0.06])[0]
    assert not sr.k2_pooled([0.1])[0]
    k2 = sr.k2_per_point({"a": [0.0, 0.01], "b": [0.3], "c": [0.2, 0.18]})
    assert k2["b"] == "UNTESTABLE (n = 1)" and k2["a"] == "PASS" and k2["c"] == "FAIL"
    calls = []
    fake = lambda lo, hi, rule, n, reps: calls.append((rule, n, reps)) or True
    assert not sr.resolving(True, False, [0.5, 0.6], 8, fake) and calls == []
    assert not sr.resolving(True, True, [0.5], 8, fake) and calls == []
    assert sr.resolving(True, True, [0.5, 0.6, 0.55], 3, fake) and calls == [("lottery", 3, 1500)]
    lo, hi = sr.g0_bounds([0.5, 0.6, 0.55])
    assert lo < 0.55 < hi


def test_variance_driven():
    y = [0.2, 0.3, 0.1, 0.25, 0.15, 0.35, 0.05, 0.3]
    dsd = [-0.2, -0.3, -0.1, -0.25, -0.15, -0.35, -0.05, -0.3]  # H steadier where H gains
    dmean = [0.01, -0.02, 0.0, 0.02, -0.01, 0.0, 0.01, -0.01]
    assert sr.variance_driven(y, dmean, [d + 0.001 * i for i, d in enumerate(dsd)], +1) is True
    assert sr.variance_driven(y, [-d for d in dsd], [0.01 * (i % 3) for i in range(8)], +1) is False
    assert sr.variance_driven(y[:3], dmean[:3], dsd[:3], +1) is None


# --- 6 map level ----------------------------------------------------------------------------------------------------

def test_the_lmm_recovers_known_coefficients_and_t1_rejects():
    import numpy as np
    rng = np.random.default_rng(0)
    beta = np.array([0.1, 0.3, 0.2, -0.1, 0.05, 0.15, -0.1])
    y, X, g = [], [], []
    for pid in sr.STAGE1_POINTS:
        row = sr.design_row(pid)
        u = rng.normal(0, 0.1)
        for _ in range(8):
            X.append(row)
            y.append(float(np.dot(beta, row) + u + rng.normal(0, 0.2)))
            g.append(pid)
    fit = sr.lmm_reml(y, X, g)
    assert np.allclose(fit["beta"], beta, atol=0.12)
    x2, df, p = sr.wald(fit)
    assert df == 6 and p < 1e-6
    z, p2 = sr.wald_one(fit, 1)
    assert z > 3 and p2 < 0.01
    flat = sr.lmm_reml([float(rng.normal(0, 0.2)) for _ in y], X, g)
    assert sr.wald(flat)[2] > 0.001


def test_the_design_row_is_centred_at_the_committed_world():
    assert sr.design_row("c1-p030-U-L") == [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    r = sr.design_row("c2-p080-PW-G")
    assert r[1] == 1.0 and abs(r[2] - math.log(0.08 / 0.03)) < 1e-12 and r[4:6] == [1.0, 1.0] and r[6] == r[2]


def test_fieller_and_m3_corroboration():
    xs = [0.01] * 4 + [0.03] * 4 + [0.08] * 4
    ys = [0.4 - 10 * x + e for x, e in zip(xs, [0.01, -0.01, 0.0, 0.005] * 3)]
    f = sr.fieller(xs, ys)
    assert f["kind"] == "bounded" and abs(f["p_star"] - 0.04) < 0.002 and f["lo"] < 0.04 < f["hi"]
    assert sr.m3_corroborates(f)
    noisy = sr.fieller(xs, [e for e in [0.3, -0.3, 0.1, -0.2] * 3])
    assert noisy["kind"] in ("unbounded", "whole line") and not sr.m3_corroborates(noisy)
    assert sr.fieller([0.01, 0.01, 0.01], [1, 2, 3])["kind"] == "not estimable"


def test_kappa_correlation_sign_changes():
    assert sr.cohen_kappa(["H", "D", "H"], ["H", "D", "H"]) == 1.0
    assert sr.cohen_kappa([], []) is None
    m, mx, n = sr.cross_correlation({"a": {1: 1, 2: 2, 3: 3}, "b": {1: 2, 2: 4, 3: 6}, "c": {1: 1, 2: 2}})
    assert n == 1 and abs(m - 1) < 1e-12
    assert sr.sign_changes([0.1, -0.2, None, 0.3, 0.0, 0.4]) == 2


# --- 7 refinement ---------------------------------------------------------------------------------------------------

def _stats(default_mean=0.2, default_t=2.0, **over):
    out = {}
    for pid in sr.STAGE1_POINTS:
        out[pid] = {"body": "NOT RUN", "resolving": False,
                    "income": {"mean": default_mean, "t": default_t, "n": 8, "call": "UNDECIDED"}}
    for pid, v in over.items():
        out[pid.replace("_", "-")] = {**out[pid.replace("_", "-")], **v}
    return out


def test_ra_pairs_are_the_42_registered():
    pairs = sr.ra_pairs()
    assert len(pairs) == 42 and len({m for _, _, m, _ in pairs}) == 42
    assert ("c0-p010-U-G", "c0-p030-U-G", "c0-p018-U-G", "price") in pairs
    assert ("c1-p030-PW-L", "c1-p080-PW-L", "c1-p053-PW-L", "price") in pairs
    assert ("c1-p030-HP-G", "c2-p030-HP-G", "c15-p030-HP-G", "clutter") in pairs
    assert sum(1 for p in pairs if p[0].endswith("-L")) == 6


def test_ra_fires_on_sign_or_decided_calls_and_ranks_g_first():
    st = _stats()
    st["c0-p030-U-G"]["income"] = {"mean": -0.1, "t": -1.0, "n": 8, "call": "UNDECIDED"}
    st["c1-p030-HP-L"]["income"] = {"mean": -0.3, "t": -9.0, "n": 8, "call": "UNDECIDED"}
    st["c2-p080-PW-G"] = {**st["c2-p080-PW-G"], "body": "EXCLUDED-H"}
    st["c1-p080-PW-G"]["income"] = {"mean": 0.4, "t": 4.0, "n": 8, "call": "EARNS-H"}
    sel, rows = sr.ra_select(st)
    assert sel[:4] == ["c0-p018-U-G", "c0-p053-U-G", "c05-p030-U-G", "c15-p080-PW-G"]  # |Δt| 3, 3, 3, then 2
    assert sel[-2:] == ["c1-p018-HP-L", "c1-p053-HP-L"]  # the L block last, whatever its |Δt|
    fired = {r["mid"]: r for r in rows if r["fires"]}
    assert fired["c15-p080-PW-G"]["calls"] and not fired["c15-p080-PW-G"]["sign"]
    assert all(r["layer"] == "income" for r in rows)


def test_ra_uses_the_share_layer_only_where_both_points_resolve_and_caps_at_16():
    st = _stats()
    for pid in sr.STAGE1_POINTS:
        c = int(pid[1])
        st[pid]["income"] = {"mean": (-1) ** c * 0.2, "t": (-1) ** c * (2.0 + c), "n": 8, "call": "UNDECIDED"}
    st["c0-p010-PW-G"].update(resolving=True, share={"mean": 0.1, "t": 1.0, "call": "UNDECIDED"})
    st["c1-p010-PW-G"].update(resolving=True, share={"mean": 0.1, "t": 1.0, "call": "UNDECIDED"})
    sel, rows = sr.ra_select(st)
    assert len(sel) == 16
    r = next(r for r in rows if r["mid"] == "c05-p010-PW-G")
    assert r["layer"] == "share" and not r["fires"]


def test_c1_candidates_from_the_committed_census_readout():
    cands = sr.c1_candidates(os.path.join(REPO, "runs", "RBT-129", "stageP0-readout", "stageP0_readout.txt"))
    assert "c0-p018-HP-G" in cands and "c05-p030-U-G" in cands and "c15-p030-U-G" in cands
    assert "c0-p018-PW-L" in cands and "c05-p018-U-G" in cands and len(cands) == len(set(cands))
    assert "c05-p010-U-G" not in cands  # on the c = 0.5 price row only the price axis's refinement levels are named
    assert all(c.split("-")[0] in ("c05", "c15") or c.split("-")[1] in ("p018", "p053") for c in cands)
    sel, rows = sr.ra_select(_stats(), cands)
    by_mid = {r["mid"]: r for r in rows if r["source"] == "C1"}
    assert by_mid["c0-p018-PW-L"]["no_stage1_pair"] and by_mid["c05-p018-U-G"]["no_stage1_pair"]
    assert not by_mid["c0-p018-HP-G"]["no_stage1_pair"] and by_mid["c0-p018-HP-G"]["dt"] == 0.0
    g_ranked = [m for m in sel if m.endswith("-G") and not by_mid.get(m, {}).get("no_stage1_pair")]
    assert sel[:len(g_ranked)] == g_ranked  # ranked G candidates before G candidates with no Stage-1 pair


def test_conditional_power_and_rb():
    assert abs(sr.conditional_power(0.0, 8) - 2 * sr.norm_cdf(-math.sqrt(2) * sr.norm_ppf(0.975))) < 1e-9
    assert sr.conditional_power(3.0, 8) > sr.conditional_power(1.0, 8) > sr.conditional_power(0.2, 8)
    assert sr.conditional_power(None, 8) is None and sr.conditional_power(1.0, 1) is None
    st = {"a": {"body": "NOT RUN", "income": {"t": 1.0, "n": 8, "call": "UNDECIDED"}},
          "b": {"body": "NOT RUN", "income": {"t": 2.0, "n": 8, "call": "UNDECIDED"}},
          "c": {"body": "NOT RUN", "income": {"t": 5.0, "n": 8, "call": "EARNS-H"}},
          "d": {"body": "PARTIAL-H", "income": {"t": 1.5, "n": 8, "call": "UNDECIDED"}},
          "e": {"body": "UNDECIDED", "share": {"t": 0.5, "n": 3}, "income": {"t": 0.1, "n": 8, "call": "UNDECIDED"}}}
    assert [p for p, _ in sr.rb_select(st)] == ["b", "a", "e"]
    assert [p for p, _ in sr.rb_select(st, literal=True)] == ["e"]
    assert sr.rb_select({k: v for k, v in st.items() if k != "e"}, literal=True) == []


# --- 9 the verdict logic ---------------------------------------------------------------------------------------------

def _pts(spec):
    return {pid: {"body": b, "income": i, "lever": None, "vd": False, "m_arm": False} for pid, (b, i) in spec.items()}


def test_verdicts():
    never = lambda pid: False
    depend = _pts({"a": ("NOT RUN", "EARNS-H"), "b": ("NOT RUN", "EARNS-H"), "c": ("NOT RUN", "EARNS-D"),
                   "d": ("NOT RUN", "EARNS-D"), "e": ("NOT RUN", "UNDECIDED")})
    assert sr.verdicts(depend, True, never)[0] == "EARNINGS DEPEND"
    assert sr.verdicts(depend, False, never) == ["NOT RESOLVED"]
    one = _pts({"a": ("NOT RUN", "EARNS-H"), "b": ("NOT RUN", "EARNS-H"), "c": ("NOT RUN", "EARNS-D"),
                "d": ("NOT RUN", "UNDECIDED"), "e": ("NOT RUN", "UNDECIDED")})
    assert sr.verdicts(one, True, never)[0] == "EARNINGS DOMINATED (H)"
    assert sr.verdicts(one, True, lambda pid: pid == "c")[0] == "EARNINGS DEPEND"
    hab = _pts({"a": ("NOT RUN", "EARNS-H"), "b": ("NOT RUN", "UNDECIDED"), "c": ("EXCLUDED-H", "UNDECIDED"),
                "d": ("PARTIAL-D", "UNDECIDED")})
    assert "DEPENDS ONLY THROUGH HABITABILITY (H)" in sr.verdicts(hab, False, never)
    inv = _pts({"a": ("NOT RUN", "EARNS-TIE"), "b": ("NOT RUN", "EARNS-TIE"), "c": ("NOT RUN", "UNDECIDED")})
    assert sr.verdicts(inv, False, never) == ["WORLD-INVARIANT"]
    lever = _pts({"a": ("NOT RUN", "EARNS-H"), "b": ("NOT RUN", "EARNS-H"), "c": ("NOT RUN", "EARNS-D"),
                  "d": ("NOT RUN", "EARNS-D")})
    lever["c"]["lever"] = True
    assert sr.verdicts(lever, True, never)[0] != "EARNINGS DEPEND"
    partial_earns = _pts({"a": ("PARTIAL-H", "EARNS-D"), "b": ("PARTIAL-H", "EARNS-D"), "c": ("NOT RUN", "EARNS-H"),
                          "d": ("NOT RUN", "EARNS-H")})
    assert sr.verdicts(partial_earns, True, never)[0] != "EARNINGS DEPEND"  # EARNS counted only where habitable


# --- the assembly on a synthetic tree --------------------------------------------------------------------------------

def _run(d, hist, rows, price=0.03):
    os.makedirs(d, exist_ok=True)
    json.dump({"sim": {"food": {"work_cost": price}}, "ecology": {"living_cost": 0.25}}, open(os.path.join(d, "config.json"), "w"))
    json.dump({"history": hist}, open(os.path.join(d, "history.json"), "w"))
    with open(os.path.join(d, "lineage.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def _rows(kind, food, lo=180, hi=299, n=2):
    return [{"generation": s, "population": kind, "food": food, "work": 0.0} for s in range(lo, hi + 1) for _ in range(n)]


def _chain(root, pid, j, h_alive=True, gain=0.3, m=False, n=False):
    u = sr.unit_dir(root, pid, j)
    hist = _hist({H: (lambda s: 2) if h_alive else (lambda s: 2 if s < 30 else 0), D: lambda s: 2}, births=0, deaths=0)
    rows = (_rows(H, 1.0 + gain + 0.01 * j) if h_alive else []) + _rows(D, 1.0)
    _run(os.path.join(u, "S"), hist, rows)
    _run(os.path.join(u, "ckpt60"), [e for e in hist if e["season"] <= 59], [])
    if m:
        _run(os.path.join(u, "M"), _hist({H: lambda s: 60 + j, D: lambda s: 60 - j}), _rows(H, 1.2) + _rows(D, 1.0))
    if n:
        k = sr.null_kind(j)
        _run(os.path.join(u, "N"), _hist({k: lambda s: 60, "null_b": lambda s: 60}), _rows(k, 1.0))


def test_assemble_and_call_on_a_synthetic_tree(tmp_path):
    root = str(tmp_path)
    for j in sr.SEEDS:
        _chain(root, "c1-p010-U-G", j, gain=0.3)
        _chain(root, "c1-p030-U-G", j, h_alive=j > 3, gain=0.0)
        _chain(root, "c0-p030-PW-G", j, m=j in (1, 5), n=j in (1, 5))
    pts = {"c1-p010-U-G": sr.assemble_point(root, "c1-p010-U-G"),
           "c1-p030-U-G": sr.assemble_point(root, "c1-p030-U-G"),
           "c0-p030-PW-G": sr.assemble_point(root, "c0-p030-PW-G", m_seeds=[1, 5], n_seeds=[1, 5])}
    a = pts["c1-p010-U-G"]
    assert a["n"] == 8 and a["valid_share"] == 8 and len(a["x"]) == 8 and a["crosscheck"] == 0
    assert abs(sum(a["x"].values()) / 8 - (0.3 + 0.045)) < 1e-9
    b = pts["c1-p030-U-G"]
    assert b["valid_share"] == 5 and b["extinct"][H] == 3 and len(b["x"]) == 5
    c = pts["c0-p030-PW-G"]
    assert sorted(c["y_m"]) == [1, 5] and sorted(c["y_n"]) == [1, 5] and c["g0"][1] is not None
    inter = sr.interference(c)
    assert inter[H][1] == 2
    calls = sr.call_points(pts, resolvable=lambda *a, **k: True)
    assert calls["c1-p010-U-G"]["body"] == "NOT RUN" and calls["c1-p010-U-G"]["income"]["call"] == "EARNS-H"
    assert calls["c1-p030-U-G"]["body"] == "PARTIAL-D"
    assert calls["c0-p030-PW-G"]["body"] in ("NOT RUN", "SATURATED", "UNDECIDED", "H-WIN", "D-WIN", "TIE")
    assert calls["c0-p030-PW-G"]["body"] != "NOT RUN"  # N ran there
    assert calls["c0-p030-PW-G"]["share_family"] and not calls["c1-p010-U-G"]["share_family"]


def test_a_point_settled_before_the_share_test_enters_no_share_family(tmp_path):
    root = str(tmp_path)
    for j in sr.SEEDS:
        _chain(root, "c0-p030-PW-G", j, h_alive=j in (1, 4, 5, 6), m=j in (1, 5), n=j in (1, 5))  # 4 of 8 valid: PARTIAL-D
        _chain(root, "c2-p010-PW-G", j, m=j in (2, 5), n=j in (2, 5))
    pts = {p: sr.assemble_point(root, p, m_seeds=m, n_seeds=m) for p, m in (("c0-p030-PW-G", [1, 5]), ("c2-p010-PW-G", [2, 5]))}
    calls = sr.call_points(pts, resolvable=lambda *a, **k: False)
    assert calls["c0-p030-PW-G"]["body"] == "PARTIAL-D" and not calls["c0-p030-PW-G"]["share_family"]
    assert calls["c2-p010-PW-G"]["share_family"] and calls["c2-p010-PW-G"]["body"] in ("SATURATED", "H-WIN", "D-WIN")


def test_the_flow_matches_the_sweep_logs_means():
    rows, hist = [], []
    for s in range(240, 300):
        foods = [1.0 + 0.1 * (s % 3), 0.5, 2.0]
        for i, f in enumerate(foods):
            rows.append({"generation": s, "population": H, "food": f, "work": 1000.0 * i,
                         **({"death": "starved"} if i == 1 else {})})
        rows.append({"generation": s, "population": H, "evals": 0})  # a newborn
        hist.append({"season": s, "population": H, "alive": 3, "births": 1, "deaths": 1,
                     "food_mean": sum(foods) / 3, "work_mean": 1000.0})
    run = {"history": hist, "rows": rows}
    assert abs(sr.flow(rows, H, 0.05) - sr.flow_from_history(hist, H, 0.05)) < 1e-12
    assert sr.history_crosscheck(run, H) == 0
    assert sr.flow_from_history([{**e, "food_mean": None} for e in hist], H, 0.05) is None
