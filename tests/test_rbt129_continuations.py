"""RBT-129 continuations (OWNER-DECISIONS-2026-10-03): the instrumented MuJoCo build's identity and its run-lane gate,
the per-run EPA log, R-B's emission and the M/N silent-corruption scan.

Nothing here runs a sweep arm.  The instrumented library itself is not installed in the test venv, so the build gate is
tested by its refusal of the stock wheel (and by ``runs/RBT-129/continuations/identity.sh`` and the smoke run, recorded
in ``runs/RBT-129/continuations/IDENTITY.md``); the wrapper is tested on a tiny world under the stock wheel, with the
identity stood in."""
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LAUNCH = os.path.join(ROOT, "runs", "RBT-129", "launch")
sys.path.insert(0, LAUNCH)
import blocks  # noqa: E402
import epa_ecology  # noqa: E402
import mjbuild  # noqa: E402
import stages  # noqa: E402

from test_rbt129_launch import TINY, fair_check, repo_tmp, surface_clearance  # noqa: E402,F401

RUNS = os.path.join(ROOT, "runs", "RBT-129")
BUILD_SH = os.path.join(ROOT, "scripts", "build_mujoco_instrumented.sh")


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    """No test writes this machine's durable receipts, saves, or leaves a build check cached."""
    monkeypatch.setattr(stages, "DURABLE_DONE", str(tmp_path / "durable-done"))
    monkeypatch.setenv("NO_DURABLE", "1")
    monkeypatch.setattr(stages, "_BUILD_CHECKED", None)
    monkeypatch.setattr(stages, "_CONTINUATION", False)
    monkeypatch.setattr(stages, "_QUARANTINE_CACHE", [])


# --- the build recipe and its identity -------------------------------------------------------------------------------

def _script_const(name):
    for line in open(BUILD_SH):
        if line.startswith(name + "="):
            return line.strip().split("=", 1)[1]
    raise AssertionError(name)


def test_the_recipe_and_the_identity_check_pin_the_same_shas():
    assert _script_const("PATCH_SHA") == mjbuild.PATCH_SHA == mjbuild.sha256(mjbuild.PATCH)
    assert _script_const("STOCK_SO_SHA") == mjbuild.STOCK_SO_SHA
    assert _script_const("INSTR_SO_SHA") == mjbuild.INSTR_SO_SHA != mjbuild.STOCK_SO_SHA
    assert mjbuild.MUJOCO_COMMIT in open(BUILD_SH).read() and "/opt/rbt129-mjbuild" in open(BUILD_SH).read()
    assert mjbuild.BUILD_LINE == f"{mjbuild.BUILD_ID} sha256:{mjbuild.INSTR_SO_SHA}"


def test_the_patch_only_adds_and_has_no_guard():
    """Guard off (owner decision 2, option (c)): the patch removes no line of MuJoCo, leaves addEdge's two writes as they
    are, and its added lines in MuJoCo's own files only call the two rbt_hzn hooks (and include their header)."""
    text = open(mjbuild.PATCH).read()
    files, cur = {}, None
    for line in text.splitlines():
        if line.startswith("+++ b/"):
            cur = line[len("+++ b/"):]
            files[cur] = []
        elif line.startswith("-") and not line.startswith("---"):
            raise AssertionError(f"the patch removes a line of {cur}: {line}")
        elif line.startswith("+") and not line.startswith("+++"):
            files[cur].append(line[1:])
    assert set(files) == {"src/engine/CMakeLists.txt", "src/engine/engine_collision_gjk.c", "src/engine/engine_forward.c",
                          "src/engine/engine_rbt_hzn.c", "src/engine/engine_rbt_hzn.h"}
    added = [x.strip() for f in ("src/engine/engine_collision_gjk.c", "src/engine/engine_forward.c") for x in files[f]]
    assert all(x.startswith(("#include \"engine/engine_rbt_hzn.h\"", "rbt_hzn_observe(", "rbt_hzn_step(", "obj1->geom,"))
               for x in added), added
    assert "GUARD" not in text.upper().replace("GUARD OFF", "").replace("GUARD-OFF", "")
    hooks = "".join(files["src/engine/engine_rbt_hzn.c"])
    code = "\n".join(x.split("//")[0] for x in files["src/engine/engine_rbt_hzn.c"])  # the hooks' code, comments dropped
    assert mjbuild.BUILD_ID in hooks and "pt->" not in code and "horizon" not in code and "mjData" not in code


def test_loaded_libs_reads_the_process_maps(tmp_path):
    maps = tmp_path / "maps"
    maps.write_text("7f00-7f01 r-xp 00000000 08:01 1 /venv/mujoco/libmujoco.so.3.14.0\n"
                    "7f01-7f02 r--p 00001000 08:01 1 /venv/mujoco/libmujoco.so.3.14.0\n"
                    "7f02-7f03 r-xp 00000000 08:01 2 /usr/lib/libc.so.6\n7f03-7f04 rw-p 00000000 00:00 0\n")
    assert mjbuild.loaded_libs(str(maps)) == ["/venv/mujoco/libmujoco.so.3.14.0"]


def test_the_stock_wheel_is_refused_by_sha_and_marker():
    """The test venv runs the pip wheel: __version__ is 3.14.0, but its libmujoco is not the instrumented build's."""
    ident = mjbuild.identity()
    if ident["libmujoco_sha256"] == mjbuild.INSTR_SO_SHA:
        pytest.skip("run under the instrumented build (test_the_forced_overflow_on_the_build covers that side)")
    assert ident["mujoco"] == "3.14.0" and ident["build_id"] is None
    with pytest.raises(SystemExit) as e:
        mjbuild.check_instrumented()
    assert e.value.code == 9


def test_a_launch_must_record_this_trees_build():
    mjbuild.check_build_line(mjbuild.BUILD_LINE)
    with pytest.raises(SystemExit) as e:
        mjbuild.check_build_line(mjbuild.BUILD_LINE.replace(mjbuild.INSTR_SO_SHA, mjbuild.STOCK_SO_SHA))
    assert e.value.code == 9


def test_check_host_holds_a_continuation_launch_to_the_build(monkeypatch):
    """A launch with a mujoco_build line is refused (exit 9) on the stock wheel, before its trees are even read; a
    launch without one is checked exactly as before."""
    calls = []
    monkeypatch.setattr(stages, "check_mujoco", lambda: calls.append("pin"))
    with pytest.raises(SystemExit) as e:
        stages.check_host({stages.BUILD_KEY: mjbuild.BUILD_LINE})
    assert e.value.code == 9 and calls == ["pin"]
    with pytest.raises(SystemExit) as e:
        stages.check_host({})
    assert e.value.code == 5  # the old path: no tree record


# --- the run-lane gate -----------------------------------------------------------------------------------------------

def _job(name, **k):
    return {"job": "fork", "name": name, "dir": f"/x/{name}", "seed": int(name.split("/")[2]), **k}


def test_a_continuation_job_needs_a_build_launch_and_a_build_launch_runs_continuations_only():
    rb = _job("RB/c2-p030-U-G/129009/M")
    with pytest.raises(SystemExit) as e:
        stages.check_lane_continuation([rb], {})
    assert e.value.code == 9
    with pytest.raises(SystemExit) as e:
        stages.check_lane_continuation([_job("1/c2-p030-U-G/129002/M")], {stages.BUILD_KEY: mjbuild.BUILD_LINE})
    assert e.value.code == 4
    stages.check_lane_continuation([_job("1/c2-p030-U-G/129002/M")], {})  # Stage 1: untouched


@pytest.mark.parametrize("key,path", [("src", "runs/RBT-129/stage1/c2-p030-U-G/129001/M"),
                                      ("ref", os.path.join(RUNS, "stage1", "c2-p030-U-G", "129001", "M"))])
def test_no_continuation_job_touches_the_crashed_unit(key, path):
    job = {"job": "scancmp", "name": "SCAN/c2-p030-U-G/129001/M-cmp", "dir": "/x/d", "seed": 129001, key: path}
    with pytest.raises(SystemExit) as e:
        stages.check_lane_continuation([job], {stages.BUILD_KEY: mjbuild.BUILD_LINE, "scan": "c2-p030-U-G/129001/M"})
    assert e.value.code == 4


def test_the_quarantined_branch_is_never_restored_even_without_saves(monkeypatch):
    stages.quarantined_labels()  # read the committed QUARANTINE: files before subprocess is stubbed
    called = []
    monkeypatch.setattr(stages.subprocess, "run", lambda *a, **k: called.append(a))
    with pytest.raises(SystemExit) as e:
        stages._restore(os.path.join(RUNS, "stage1", "c2-p030-U-G", "129001", "M"))
    assert e.value.code == 4 and not called
    assert stages._label(os.path.join(RUNS, "stage1", "c2-p030-U-G", "129001", "M")) in stages.QUARANTINED


def test_r_b_lanes_refuse_until_the_overflow_rule_is_registered(monkeypatch, tmp_path):
    """R-B's gate (exit 10), keyed on the launch's go line: no rule file, an uncommitted one, a rule without a well-formed
    REGISTERED: RBT129-<id> and OVERFLOW-RULE: line (MINOR 8) are all refused; the scan is not gated on it."""
    rb = _job("RB/c2-p030-U-G/129009/M")
    launch = {stages.BUILD_KEY: mjbuild.BUILD_LINE, "rb_points": " ".join(stages.RB_POINTS), "go": stages.RB_GO}
    monkeypatch.setattr(stages, "OVERFLOW_RULE", str(tmp_path / "OVERFLOW-RULE.md"))
    with pytest.raises(SystemExit) as e:
        stages.check_lane_continuation([rb], launch)
    assert e.value.code == 10
    (tmp_path / "OVERFLOW-RULE.md").write_text("REGISTERED: RBT129-X\nOVERFLOW-RULE: include-flagged\n")
    with pytest.raises(SystemExit) as e:  # present but not committed
        stages.check_lane_continuation([rb], launch)
    assert e.value.code == 10
    monkeypatch.setattr(stages, "check_overflow_rule", lambda: "blob")
    stages.check_lane_continuation([rb], launch)
    scan = _job("SCAN/c2-p030-U-G/129005/M")
    stages.check_lane_continuation([dict(scan, set=_scan_set(scan), src="runs/RBT-129/stage1/c2-p030-U-G/129005/ckpt60")],
                                   {stages.BUILD_KEY: mjbuild.BUILD_LINE,
                                                                          "scan": "c2-p030-U-G/129005/M"})


def _scan_set(job):
    return {"merge_after": 60, "pooled_capacity": 120}


@pytest.mark.parametrize("text", [
    "", "REGISTERED:\nOVERFLOW-RULE: include-flagged\n", "REGISTERED: RULING-1\nOVERFLOW-RULE: include-flagged\n",
    "REGISTERED: RBT129-OVR-1\n", "REGISTERED: RBT129-OVR-1\nOVERFLOW-RULE: either\n",
    "REGISTERED: RBT129-OVR-1\nREGISTERED: RBT129-OVR-2\nOVERFLOW-RULE: include-flagged\n",
    "REGISTERED: RBT129-OVR-1\nOVERFLOW-RULE: include-flagged\nOVERFLOW-RULE: exclude-known-flagged\n"])
def test_the_registered_rule_needs_an_id_and_a_primary(text):
    with pytest.raises(SystemExit) as e:
        stages.parse_rule(text)
    assert e.value.code == 10


def test_a_well_formed_rule_parses():
    assert stages.parse_rule("# r\nREGISTERED: RBT129-OVR-1\nOVERFLOW-RULE: exclude-known-flagged\n") == \
        ("RBT129-OVR-1", "exclude-known-flagged")


def test_a_build_launch_must_say_what_it_runs(monkeypatch):
    """MINOR 8: a mujoco_build launch with neither a scan nor an rb_points line is refused (exit 4), and a go line alone
    opens the overflow-rule gate whatever the jobs are named."""
    job = dict(_job("SCAN/c2-p030-U-G/129005/M"), set={"merge_after": 60, "pooled_capacity": 120},
               src="runs/RBT-129/stage1/c2-p030-U-G/129005/ckpt60")
    with pytest.raises(SystemExit) as e:
        stages.check_lane_continuation([job], {stages.BUILD_KEY: mjbuild.BUILD_LINE})
    assert e.value.code == 4
    called = []
    monkeypatch.setattr(stages, "check_overflow_rule", lambda: called.append(1) or "blob")
    stages.check_lane_continuation([job], {stages.BUILD_KEY: mjbuild.BUILD_LINE, "scan": "c2-p030-U-G/129005/M",
                                           "go": stages.RB_GO})
    assert called


def test_ruled_quarantine_lines_are_refused(monkeypatch):
    """MAJOR 1: a committed QUARANTINE: line (the Stage-2 plan's format) quarantines a label, case-insensitively, for
    _restore and the lane check; an empty one is refused."""
    texts = {stages.QUARANTINE_FILES[0]: "QUARANTINE: rbt-129-RB-c1-p010-U-L-129011-S\n", stages.QUARANTINE_FILES[1]: ""}
    monkeypatch.setattr(stages, "_committed_text", lambda path: texts.get(path, ""))
    d = os.path.join(RUNS, "rb", "c1-p010-U-L", "129011", "S")
    assert stages.is_quarantined(stages._label(d))
    with pytest.raises(SystemExit) as e:
        stages._restore(d)
    assert e.value.code == 4
    job = {"job": "resume", "name": "RB/c1-p010-U-L/129011/S", "dir": d, "seed": 129011}
    monkeypatch.setattr(stages, "check_overflow_rule", lambda: "blob")
    with pytest.raises(SystemExit) as e:
        stages.check_lane_continuation([job], {stages.BUILD_KEY: mjbuild.BUILD_LINE,
                                               "rb_points": " ".join(stages.RB_POINTS)})
    assert e.value.code == 4
    monkeypatch.setattr(stages, "_QUARANTINE_CACHE", [])
    texts[stages.QUARANTINE_FILES[1]] = "QUARANTINE:   \n"
    with pytest.raises(SystemExit) as e:
        stages.quarantined_labels()
    assert e.value.code == 4


def test_an_r_b_lane_runs_only_its_points_and_seeds_9_to_16(monkeypatch):
    monkeypatch.setattr(stages, "check_overflow_rule", lambda: "blob")
    launch = {stages.BUILD_KEY: mjbuild.BUILD_LINE, "rb_points": " ".join(stages.RB_POINTS)}
    for bad in ("RB/c0-p030-PW-G/129009/S", "RB/c2-p030-U-G/129008/M"):
        with pytest.raises(SystemExit) as e:
            stages.check_lane_continuation([_job(bad)], launch)
        assert e.value.code == 4


def test_a_continuation_job_checks_the_build_before_anything_and_runs_through_the_wrapper(monkeypatch, tmp_path):
    def refuse(line=None):
        raise SystemExit(9)
    monkeypatch.setattr(stages, "check_continuation_build", refuse)
    with pytest.raises(SystemExit) as e:
        stages.run_job({"job": "resume", "name": "RB/c2-p030-U-G/129009/S", "dir": str(tmp_path / "nowhere"), "seed": 129009,
                        "seasons": 300, "cost": 240})
    assert e.value.code == 9 and not (tmp_path / "nowhere").exists()

    seen = []

    class Proc:
        def __init__(self, cmd, **k):
            seen.append(cmd)

        def wait(self):
            return 0
    monkeypatch.setattr(stages.subprocess, "Popen", Proc)
    d = tmp_path / "run"
    d.mkdir()
    for cont in (True, False):
        monkeypatch.setattr(stages, "_CONTINUATION", cont)
        stages._ecology(["--resume", "--seasons", "300"], str(d), "label")
    assert seen[0][1:2] == [stages.EPA_WRAPPER] and seen[1][1:4] == ["-m", "rabbitstew.cli", "ecology"]
    assert seen[0][2:] == seen[1][4:]


def test_r_b_forks_only_seeds_valid_at_the_merge(monkeypatch, tmp_path):
    """DESIGN 5.2's seed rule, applied at run time for R-B: a seed whose S has a fauna dead at season 59 gets no M."""
    monkeypatch.setattr(stages, "check_continuation_build", lambda line=None: {})
    src = tmp_path / "rb" / "c2-p030-U-G" / "129009" / "ckpt60"
    src.mkdir(parents=True)
    (src / "config.json").write_text(json.dumps({"ecology": {}}))
    (src / "history.json").write_text(json.dumps({"history": [{"season": 59, "population": "holistic", "alive": 0},
                                                              {"season": 59, "population": "conventional", "alive": 9}]}))
    (src / "state.json").write_text(json.dumps({"season": 60, "populations": {"holistic": [], "conventional": ["a"]}}))
    d = src.parent / "M"
    stages.run_job({"job": "fork", "name": "RB/c2-p030-U-G/129009/M", "src": str(src), "dir": str(d), "seed": 129009,
                    "seasons": 300, "salts": [0, 0], "seed_rule": True, "set": {"merge_after": 60}, "cost": 240})
    assert open(d / ".rbt129-done-M").read().strip().endswith("skipped: not valid at the merge (DESIGN 5.2 seed rule)")
    assert not (d / "state.json").exists()


# --- the EPA log -----------------------------------------------------------------------------------------------------

def _ev(kind, n, pid=7):
    return {"event": kind, "nedges": n, "cap": 24, "epa_iteration": 3, "nverts": 9, "nfaces": 20, "geom1": 1, "type1": 6,
            "geom2": 2, "type2": 5, "step": 11, "time": 0.022, "process_steps": 99, "pid": pid}


def test_read_log_takes_the_union_over_attempts_and_flags_unlogged(tmp_path):
    """MINOR 11: a season's events are the union over the attempts that ran it (an overflow is never un-seen; a re-run's
    repeat counts once).  MINOR 9 / W7: a histogram whose overflows differ from its pid's overflow lines, or an unreadable
    line in mid-attempt, is UNLOGGED; a cut final line is not."""
    path = tmp_path / mjbuild.EPA_LOG
    ov = dict(_ev("overflow", 25, pid=7), attempt=1)
    lines = [{"start": "t0", "attempt": 1, "pid": 1}, {"season": 60, "pid": 1}, dict(_ev("near", 17), attempt=1),
             {"season": 61, "pid": 1}, dict(_ev("near", 19), attempt=1), ov,
             {"hist": {"5": 10, "25": 1}, "epa_iterations": 11, "overflows": 1, "attempt": 1, "pid": 7},
             {"start": "t1", "attempt": 2, "pid": 2}, {"season": 61, "pid": 2}, dict(_ev("near", 19), attempt=2),
             {"season": 62, "pid": 2}, {"hist": {"5": 4}, "epa_iterations": 4, "overflows": 0, "attempt": 2, "pid": 7}]
    path.write_text("".join(json.dumps(x) + "\n" for x in lines) + '{"event": "near", "nedg')
    r = epa_ecology.read_log(str(path))
    assert r["starts"] == 2 and r["bad_lines"] == 1 and r["unlogged"] == []
    assert [e["nedges"] for e in r["seasons"][61]["overflow"]] == [25]  # the re-run season did not un-see it
    assert [e["nedges"] for e in r["seasons"][61]["near"]] == [19]  # the repeat of the same event counts once
    assert (r["near"], r["overflow"], r["max_nedges"]) == (2, 1, 25) and r["epa_iterations"] == 15
    # a histogram that counted an overflow its log never got (MINOR 9), and a cut line followed by more lines
    with open(path, "a") as f:
        f.write("\n" + json.dumps({"hist": {}, "epa_iterations": 0, "overflows": 2, "attempt": 2, "pid": 9}) + "\n")
    r = epa_ecology.read_log(str(path))
    assert any("histogram overflows 2" in x for x in r["unlogged"])
    assert any("mid-attempt" in x for x in r["unlogged"])
    assert epa_ecology.read_log(str(tmp_path / "missing"))["starts"] == 0


def test_a_fresh_runs_delete_keeps_its_log(tmp_path):
    """MINOR 10: ``_fresh``'s rmtree of a run that never finished a season keeps its EPA log as .prev-<n>; the attempt
    count and every reader read both."""
    d = tmp_path / "run"
    d.mkdir()
    (d / mjbuild.EPA_LOG).write_text(json.dumps({"start": "t", "attempt": 1, "pid": 1}) + "\n"
                                     + json.dumps(dict(_ev("overflow", 25), attempt=1)) + "\n")
    (d / "lineage.jsonl").write_text("x")
    put_back = epa_ecology.keep_log(str(d))
    import shutil
    shutil.rmtree(d)
    d.mkdir()
    put_back()
    assert sorted(os.listdir(d)) == [mjbuild.EPA_LOG + ".prev-1"]
    log = str(d / mjbuild.EPA_LOG)
    assert epa_ecology.attempts(log) == 2 and epa_ecology.read_log(log)["overflow"] == 1
    (d / mjbuild.EPA_LOG).write_text(json.dumps({"start": "t", "attempt": 2, "pid": 2}) + "\n")
    put_back = epa_ecology.keep_log(str(d))
    shutil.rmtree(d)
    d.mkdir()
    put_back()
    assert sorted(os.listdir(d)) == [mjbuild.EPA_LOG + ".prev-1", mjbuild.EPA_LOG + ".prev-2"]
    assert epa_ecology.attempts(log) == 3 and epa_ecology.overflow_records(log)[0]["attempt"] == 1


def test_the_wrapper_logs_seasons_records_the_build_and_changes_no_output(tmp_path, fair_check):
    """On a tiny world, two workers: the wrapper's run (identity stood in, since the test venv has the stock wheel) and
    a plain ``-m rabbitstew.cli`` run are byte-identical in every output file; the wrapper's platform.json carries
    mujoco_build, and its log has its start and one line per season."""
    argv = TINY + ["--fair", "--sweep-log", "--seed", "3", "--seasons", "3", "--workers", "2"]
    a, b = tmp_path / "wrapped", tmp_path / "plain"
    code = ("import sys; sys.path.insert(0, %r); import epa_ecology, mjbuild\n"
            "ident = dict(mjbuild.identity(), build_id='STAND-IN')\n"
            "argv = sys.argv[1:]; epa_ecology.install(epa_ecology._out_dir(argv), ident, argv)\n"
            "from rabbitstew import cli; sys.exit(cli.main(['ecology', *argv]))\n") % LAUNCH
    subprocess.run([sys.executable, "-c", code, *argv, "--out", str(a)], cwd=ROOT, check=True, capture_output=True)
    subprocess.run([sys.executable, "-m", "rabbitstew.cli", "ecology", *argv, "--out", str(b)], cwd=ROOT, check=True,
                   capture_output=True)
    skip = ("platform.json", mjbuild.EPA_LOG)
    files = lambda d: {os.path.relpath(os.path.join(r, n), d): open(os.path.join(r, n), "rb").read()
                       for r, _, ns in os.walk(d) for n in ns if n not in skip}
    assert files(a) == files(b) and len(files(a)) > 5
    assert json.load(open(a / "platform.json"))["mujoco_build"]["build_id"] == "STAND-IN"
    assert "mujoco_build" not in json.load(open(b / "platform.json"))
    log = [json.loads(x) for x in open(a / mjbuild.EPA_LOG)]
    assert "start" in log[0] and [x["season"] for x in log if "season" in x] == [0, 1, 2]


# --- R-B ---------------------------------------------------------------------------------------------------------------

def test_the_r_b_points_are_the_committed_readouts():
    assert tuple(stages.committed_rb()) == stages.RB_POINTS and len(stages.RB_POINTS) == 9
    assert [stages.seed(j) for j in stages.RB_SEEDS] == list(range(129009, 129017))


def test_the_r_b_gate_admits_m_at_c2_p030_u_g_only_and_no_n():
    """DESIGN 5.2 at the R-B points, from the committed census: of the 9, only c2-p030-U-G has census g0 <= 1.0 (0.938,
    designed not FOUNDING-FAIL); none has g0 <= 0.8."""
    gate = {r["point"]: r for r in stages.rb_gate()}
    assert [p for p, r in gate.items() if r["m"]] == ["c2-p030-U-G"] and not any(r["n"] for r in gate.values())


def test_r_b_units(monkeypatch):
    salts, launch = stages.rb_inputs(RUNS)
    units = stages.rb_units("runs/RBT-129", salts, stages.rb_gate())
    assert len(units) == 72 and {u["seed"] for u in units} == set(range(129009, 129017))
    jobs = [j for u in units for j in u["jobs"]]
    assert all(j["name"].startswith("RB/") and stages.continuation(j) for j in jobs)
    assert not any(j["seed"] <= 129008 for j in jobs)
    m = [j for j in jobs if j["name"].endswith("/M")]
    assert len(m) == 8 and all(j["name"].startswith("RB/c2-p030-U-G/") and j["seed_rule"] for j in m)
    assert not [j for j in jobs if j["name"].endswith("/N")]
    for j in jobs:
        if j["job"] == "fresh":
            assert j["extra"] == stages.salts_argv(*salts[j["seed"]])  # screened salts, as check_lane_salts holds
    assert salts[129010] == (1, 0) and salts[129016] == (1, 0)
    (s_lo, s_hi), (m_lo, m_hi) = stages.rb_core_h(units)
    assert (round(s_lo), round(s_hi)) == (140, 262)  # the readout's "S arms 140 / 262 core-h"
    assert (round(m_lo, 1), round(m_hi, 1)) == (12.5, 23.3)


# --- the scan ----------------------------------------------------------------------------------------------------------

def test_the_scan_replays_every_stage_1_m_and_n_fork_but_the_crashed_one():
    units, excluded = stages.scan_units(RUNS)
    assert excluded == ["c2-p030-U-G/129001/M"] and len(units) == 37
    forks = [u["jobs"][0] for u in units]
    assert sum(f["name"].endswith("/M") for f in forks) == 30 and sum(f["name"].endswith("/N") for f in forks) == 7
    for u in units:
        fork, cmp_ = u["jobs"]
        assert fork["dir"] == cmp_["dir"] and "mn-corruption-scan" in fork["dir"]
        assert not any(stages._label(p) in stages.QUARANTINED for p in (fork["src"], fork["dir"], cmp_["ref"]))
        if fork["name"].endswith("/N"):
            assert fork["set"]["merge_null"] == stages.null_kind(fork["seed"] - blocks.SEED_BASE)
    launch = {stages.BUILD_KEY: mjbuild.BUILD_LINE, "scan": " ".join(f["name"][5:] for f in forks)}
    jobs = [j for u in units for j in u["jobs"]]
    stages.check_lane_continuation(jobs, launch)
    bad = dict(jobs[0], set={"merge_after": 60})
    with pytest.raises(SystemExit) as e:
        stages.check_lane_continuation([bad], launch)
    assert e.value.code == 4


def _run_dir(path, files):
    os.makedirs(path, exist_ok=True)
    for name, data in files.items():
        os.makedirs(os.path.dirname(os.path.join(path, name)) or path, exist_ok=True)
        with open(os.path.join(path, name), "w") as f:
            f.write(data)


def test_scan_compare_names_differing_files_and_never_their_contents(tmp_path, capsys):
    stored, replay = tmp_path / "stage1" / "c1-p080-U-L" / "129004" / "M", tmp_path / "replay" / "M"
    common = {"state.json": "{}", "lineage.jsonl": "a\n", "holistic/g1.json": "x", "config.json": "{}"}
    _run_dir(stored, {**common, ".rbt129-done-M": "t", "run.log": "season 61 alive 9", "platform.json": "{}"})
    _run_dir(replay, {**common, ".rbt129-done-M": "t", "run.log": "other", mjbuild.EPA_LOG: json.dumps(_ev("near", 20)) + "\n",
                      "platform.json": json.dumps({"resumes": [{"mujoco_build": {"libmujoco_sha256": "abc"}}]})})
    job = {"name": "SCAN/c1-p080-U-L/129004/M-cmp", "ref": str(stored)}
    stages.scan_compare(job, str(replay))
    text = open(replay / stages.SCAN_FILE).read()
    assert text.startswith("SCAN IDENTICAL: c1-p080-U-L/129004/M") and "4 files compared" in text
    assert "near(>=17) 1" in text and "max_horizon 20" in text and "build: abc" in text
    (replay / "lineage.jsonl").write_text("b\n")
    (replay / "extra.json").write_text("{}")
    stages.scan_compare(job, str(replay))
    text = open(replay / stages.SCAN_FILE).read()
    assert text.startswith("SCAN DIFFER") and "DIFFERS: lineage.jsonl" in text and "only in replay: extra.json" in text
    assert "a\n" not in text.replace("SCAN", "") and "b\n" not in text.split("\n", 1)[1].replace("  ", "")
    assert "alive" not in capsys.readouterr().out
    os.remove(stored / ".rbt129-done-M")
    stages.scan_compare(job, str(replay))
    assert open(replay / stages.SCAN_FILE).read().startswith("SCAN NO-REFERENCE")
    with pytest.raises(SystemExit) as e:
        stages.scan_compare({"name": "SCAN/c2-p030-U-G/129001/M-cmp", "ref": os.path.join(RUNS, "stage1", "c2-p030-U-G", "129001", "M")},
                            str(replay))
    assert e.value.code == 4


# --- the committed lanes -----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["RB", "SCAN"])
def test_the_committed_continuation_lanes(name, monkeypatch):
    lane_dir = os.path.join(RUNS, "lanes", name)
    if not os.path.isdir(lane_dir):
        pytest.skip(f"lanes/{name} not emitted on this tree")
    monkeypatch.setattr(stages, "check_overflow_rule", lambda: "blob")
    launch = stages.read_launch(os.path.join(lane_dir, "launch.txt"))
    assert launch[stages.BUILD_KEY] == mjbuild.BUILD_LINE
    jobs = [json.loads(x) for f in sorted(os.listdir(lane_dir)) if f.endswith(".jsonl") for x in open(os.path.join(lane_dir, f))]
    jobs = [{k: (stages.absolute(v) if k in stages.PATH_KEYS else v) for k, v in j.items()} for j in jobs]
    stages.check_lane_continuation(jobs, launch)
    stages.check_lane_salts(jobs, launch)
    assert all(stages.continuation(j) for j in jobs)
    assert not any("129001/M" in j.get(k, "") and "c2-p030-U-G" in j.get(k, "") for j in jobs for k in ("dir", "src", "ref"))
    if name == "RB":
        assert len(jobs) == 9 * 8 * 3 + 8 and launch["go"] == stages.RB_GO
    else:
        assert len(jobs) == 2 * 37


@pytest.mark.parametrize("cmd", ["rb-emit", "scan-emit"])
def test_every_continuation_emitter_refuses_off_the_build(cmd, tmp_path):
    """COORD-RULING-520 D3 / FC-3: emitters, like run-lane, refuse unless the loaded libmujoco's sha256 and build marker
    are the registered build's (the test venv has the stock wheel); nothing is written."""
    with pytest.raises(SystemExit) as e:
        stages.main([cmd, "--fair=--fair", "--root", str(tmp_path)])
    assert e.value.code == 9 and not os.listdir(tmp_path)


def test_events_come_from_the_dedicated_log_only(tmp_path):
    """FC-3: the scan and the lane read EPA events only from epa_overflow.jsonl, never from run.log."""
    import inspect
    for fn in (stages.scan_compare, stages.scan_report, stages.epa_note, epa_ecology.read_log):
        assert "run.log" not in inspect.getsource(fn)
    d = tmp_path / "run"
    d.mkdir()
    (d / "run.log").write_text('{"event": "overflow", "nedges": 30}\nRBT_HZN overflow: nedges 25\n')
    assert epa_ecology.read_log(str(d / mjbuild.EPA_LOG))["overflow"] == 0


def _write(path, lines):
    path.write_text("".join(json.dumps(x) + "\n" for x in lines))


def test_unit_and_attempt_ids():
    d = os.path.join(RUNS, "rb", "c2-p030-U-G", "129009", "M")
    assert epa_ecology.unit_id(d) == "rbt-129-rb-c2-p030-U-G-129009-M" == stages._label(d)


def test_attestation_needs_the_faulting_process_in_the_faulting_season(tmp_path):
    """W6 (native_exit folded in, MINOR 5): an overflow line of the unit and attempt, from a process that died natively
    in that attempt, after the attempt's last season line, before its native exit line."""
    log = tmp_path / mjbuild.EPA_LOG
    start = {"start": "t", "unit": "u", "attempt": 1, "workers": 2, "pid": 100}
    ov = lambda pid: dict(_ev("overflow", 25, pid=pid), unit="u", attempt=1, seq=1)
    pb = {"pool_broken": {"attempt": 1, "workers": {"101": -11, "102": None}}, "pid": 100}
    native = {"exit": {"attempt": 1, "code": 1, "signal": None, "native": True}}
    cases = {
        "the faulting worker, in the last season": ([start, {"season": 60, "pid": 100}, {"season": 61, "pid": 100},
                                                     ov(101), pb, native], True),
        "an overflow seasons earlier, survived": ([start, {"season": 60, "pid": 100}, ov(101),
                                                  {"season": 61, "pid": 100}, pb, native], False),
        "the other worker overflowed": ([start, {"season": 61, "pid": 100}, ov(102), pb, native], False),
        "not a native exit": ([start, {"season": 61, "pid": 100}, ov(101), pb,
                               {"exit": {"attempt": 1, "code": -9, "signal": 9, "native": False}}], False),
        "no exit line yet": ([start, {"season": 61, "pid": 100}, ov(101), pb], False),
        "workers 1: the parent faults": ([dict(start, workers=1), {"season": 61, "pid": 100}, ov(100),
                                          {"exit": {"attempt": 1, "code": -11, "signal": 11, "native": True}}], True),
        "another unit's line": ([start, {"season": 61, "pid": 100}, dict(ov(101), unit="v"), pb, native], False),
    }
    for name, (lines, want) in cases.items():
        _write(log, lines)
        assert epa_ecology.attested(str(log), "u", 1) is want, name
    assert epa_ecology.native_exit(str(log), 1) is True and epa_ecology.overflow_before_exit(str(log), "v", 1)


def test_crash_state_is_rulings_item_5_count(tmp_path):
    """Two consecutive native exits, one at workers 1: CRASHED, attested only when both attempts are."""
    log = tmp_path / mjbuild.EPA_LOG

    def attempt(k, workers, native, overflow):
        out = [{"start": "t", "unit": "u", "attempt": k, "workers": workers, "pid": 100 + k}, {"season": 70, "pid": 100 + k}]
        if overflow:
            out.append(dict(_ev("overflow", 25, pid=100 + k), unit="u", attempt=k, seq=1))
        out.append({"exit": {"attempt": k, "code": -11 if native else 0, "signal": 11 if native else None, "native": native}})
        return out
    _write(log, attempt(1, 2, True, True) + attempt(2, 1, True, True))
    assert epa_ecology.crash_state(str(log), "u") == {"attempts": (1, 2), "attested": True}
    _write(log, attempt(1, 2, True, True) + attempt(2, 1, True, False))
    assert epa_ecology.crash_state(str(log), "u") == {"attempts": (1, 2), "attested": False}
    _write(log, attempt(1, 2, True, True) + attempt(2, 2, True, True))
    assert epa_ecology.crash_state(str(log), "u") is None  # neither at workers 1
    _write(log, attempt(1, 1, True, True) + attempt(2, 2, False, False) + attempt(3, 2, True, True))
    assert epa_ecology.crash_state(str(log), "u") is None  # not consecutive natives
    _write(log, attempt(1, 1, True, True))
    assert epa_ecology.crash_state(str(log), "u") is None


def test_a_crashed_continuation_is_never_resumed(monkeypatch, tmp_path):
    """MAJOR 1: run_job refuses (exit 4) a continuation job whose log meets the crash count, before any ecology runs."""
    monkeypatch.setattr(stages, "check_continuation_build", lambda line=None: {})
    d = tmp_path / "M"
    d.mkdir()
    (d / "state.json").write_text("{}")
    lines = []
    for k, w in ((1, 2), (2, 1)):
        lines += [{"start": "t", "unit": epa_ecology.unit_id(str(d)), "attempt": k, "workers": w, "pid": k},
                  {"exit": {"attempt": k, "code": -11, "signal": 11, "native": True}}]
    _write(d / mjbuild.EPA_LOG, lines)
    ran = []
    monkeypatch.setattr(stages, "_resume", lambda *a: ran.append(a))
    with pytest.raises(SystemExit) as e:
        stages.run_job({"job": "resume", "name": "RB/c2-p030-U-G/129009/S", "dir": str(d), "seed": 129009,
                        "seasons": 300, "cost": 240})
    assert e.value.code == 4 and not ran


def test_exit_lines_and_nostart(tmp_path):
    log = tmp_path / mjbuild.EPA_LOG
    assert epa_ecology.attempts(str(log)) == 1 and epa_ecology.current_attempt(str(log)) is None
    _write(log, [{"start": "t", "unit": "u", "attempt": 1}, {"start": "t", "unit": "u", "attempt": 2}])
    assert epa_ecology.attempts(str(log)) == 3 and epa_ecology.current_attempt(str(log)) == 2
    assert epa_ecology.write_exit(str(tmp_path), -11)["exit"] == {"attempt": 2, "code": -11, "signal": 11, "native": True}
    # MINOR 7: a process that died before its start line is never booked to the previous attempt
    rec = epa_ecology.write_exit(str(tmp_path), -11, nostart=True)["exit"]
    assert rec["attempt"] is None and rec["nostart"] is True
    assert any("nostart" in x for x in epa_ecology.read_log(str(log))["unlogged"])
    # a broken pool: the parent exits 1, natively only if a worker of the same attempt died on a native signal
    _write(log, [{"start": "t", "unit": "u", "attempt": 1}])
    assert epa_ecology.write_exit(str(tmp_path), 1)["exit"]["native"] is False
    with open(log, "a") as f:
        f.write(json.dumps({"pool_broken": {"attempt": 1, "workers": {"7": -11, "8": None}}}) + "\n")
    assert epa_ecology.write_exit(str(tmp_path), 1)["exit"]["native"] is True
    assert epa_ecology.write_exit(str(tmp_path), 0)["exit"]["native"] is False


@pytest.mark.parametrize("wrote_start", [True, False])
def test_run_lane_writes_the_exit_line_after_a_continuations_ecology(monkeypatch, tmp_path, wrote_start):
    d = tmp_path / "run"
    d.mkdir()
    log = d / mjbuild.EPA_LOG
    log.write_text(json.dumps({"start": "t", "unit": "u", "attempt": 4}) + "\n")

    class Proc:
        def __init__(self, cmd, **k):
            if wrote_start:  # the wrapper's start line, as epa_ecology.install writes it
                with open(log, "a") as f:
                    f.write(json.dumps({"start": "t", "unit": "u", "attempt": 5}) + "\n")

        def wait(self):
            return -11
    monkeypatch.setattr(stages.subprocess, "Popen", Proc)
    saved = []
    monkeypatch.setattr(stages, "save_crash_record", lambda d: saved.append(d))
    monkeypatch.setattr(stages, "_CONTINUATION", True)
    with pytest.raises(SystemExit):
        stages._ecology(["--resume"], str(d), "label")
    last = json.loads(open(log).read().splitlines()[-1])["exit"]
    if wrote_start:
        assert last == {"attempt": 5, "code": -11, "signal": 11, "native": True}
    else:
        assert last["attempt"] is None and last["nostart"] is True
    assert saved == [str(d)]  # the crash record after a native exit (MAJOR 1)


def test_a_unit_id_the_library_would_cut_is_refused(tmp_path):
    out = tmp_path / ("x" * 130)
    with pytest.raises(SystemExit) as e:
        epa_ecology.install(str(out), {"build_id": "b", "libmujoco_sha256": "s", "libmujoco_path": "/nonexistent"}, [])
    assert e.value.code == 4


def test_the_scan_report_commits_counts_only(tmp_path, monkeypatch):
    """MAJOR 2 and 4: totals by arm; a unit named only when not IDENTICAL and CLEAN; no season, near-miss figure, file
    count or file name; the header says CLEAN covers seasons 60-299 and the S60 phase is UNSCANNED."""
    root = tmp_path
    (root / "lanes" / "1-MN").mkdir(parents=True)
    (root / "lanes" / "1-MN" / "launch.txt").write_text(
        "salts 129004:0/0 129005:0/0\nforks c1-p080-U-L/129004/M c1-p080-U-L/129005/N\n")
    units, _ = stages.scan_units(str(root))
    logs = {0: [{"start": "t", "attempt": 1, "pid": 1}, {"season": 61, "pid": 1}, dict(_ev("near", 20), attempt=1)],
            1: [{"start": "t", "attempt": 1, "pid": 1}, {"season": 77, "pid": 1}, dict(_ev("overflow", 25), attempt=1)]}
    for i, u in enumerate(units):
        d = u["jobs"][0]["dir"]
        os.makedirs(d)
        _write(__import__("pathlib").Path(d) / mjbuild.EPA_LOG, logs[i])
        with open(os.path.join(d, stages.SCAN_FILE), "w") as f:
            f.write(("SCAN IDENTICAL: x\n" if i == 0 else "SCAN DIFFER: x\n") + "  DIFFERS: lineage.jsonl\n  1661 files\n")
    text = stages.scan_report(str(root))
    assert "M: CLEAN (seasons 60-299) 1, IDENTICAL 1" in text and "N: DIFFER 1, OVERFLOWED 1" in text
    assert "c1-p080-U-L/129005/N: DIFFER; OVERFLOWED; overflow 1" in text and "c1-p080-U-L/129004/M" not in text
    assert "UNSCANNED" in text and "seasons 60-299" in text
    for word in ("lineage", "1661", "near", "77", '"season"'):
        assert word not in text.split("named (")[1], word
    assert not os.path.exists(root / stages.SCAN_DIR / "epa")


def test_the_forced_overflow_on_the_build():
    """The forced overflow (upstream #3646's pair) at WORKERS=2; runs only where the instrumented build is loaded (the
    committed record is records/forced-overflow.txt)."""
    try:
        mjbuild.check_instrumented()
    except SystemExit:
        pytest.skip("the instrumented build is not loaded here")
    import tempfile
    out = tempfile.mkdtemp()
    r = subprocess.run([sys.executable, os.path.join(RUNS, "continuations", "forced_overflow.py"), out, "2"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "FORCED OVERFLOW PASS" in r.stdout, r.stdout + r.stderr
