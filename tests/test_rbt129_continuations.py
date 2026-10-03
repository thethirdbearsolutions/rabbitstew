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
    assert mjbuild.BUILD_ID in hooks and "pt->" not in hooks and "horizon" not in hooks.replace("horizon sizes", "")


def test_loaded_libs_reads_the_process_maps(tmp_path):
    maps = tmp_path / "maps"
    maps.write_text("7f00-7f01 r-xp 00000000 08:01 1 /venv/mujoco/libmujoco.so.3.14.0\n"
                    "7f01-7f02 r--p 00001000 08:01 1 /venv/mujoco/libmujoco.so.3.14.0\n"
                    "7f02-7f03 r-xp 00000000 08:01 2 /usr/lib/libc.so.6\n7f03-7f04 rw-p 00000000 00:00 0\n")
    assert mjbuild.loaded_libs(str(maps)) == ["/venv/mujoco/libmujoco.so.3.14.0"]


def test_the_stock_wheel_is_refused_by_sha_and_marker():
    """The test venv runs the pip wheel: __version__ is 3.14.0, but its libmujoco is not the instrumented build's."""
    ident = mjbuild.identity()
    assert ident["mujoco"] == "3.14.0" and ident["libmujoco_sha256"] != mjbuild.INSTR_SO_SHA and ident["build_id"] is None
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
        stages.check_lane_continuation([job], {stages.BUILD_KEY: mjbuild.BUILD_LINE})
    assert e.value.code == 4


def test_the_quarantined_branch_is_never_restored_even_without_saves(monkeypatch):
    called = []
    monkeypatch.setattr(stages.subprocess, "run", lambda *a, **k: called.append(a))
    with pytest.raises(SystemExit) as e:
        stages._restore(os.path.join(RUNS, "stage1", "c2-p030-U-G", "129001", "M"))
    assert e.value.code == 4 and not called
    assert stages._label(os.path.join(RUNS, "stage1", "c2-p030-U-G", "129001", "M")) in stages.QUARANTINED


def test_r_b_lanes_refuse_until_the_overflow_rule_is_registered(monkeypatch, tmp_path):
    rb = _job("RB/c2-p030-U-G/129009/M")
    launch = {stages.BUILD_KEY: mjbuild.BUILD_LINE, "rb_points": " ".join(stages.RB_POINTS)}
    monkeypatch.setattr(stages, "OVERFLOW_RULE", str(tmp_path / "OVERFLOW-RULE.md"))
    with pytest.raises(SystemExit) as e:
        stages.check_lane_continuation([rb], launch)
    assert e.value.code == 10
    (tmp_path / "OVERFLOW-RULE.md").write_text("# draft, not yet ruled\n")
    with pytest.raises(SystemExit) as e:
        stages.check_lane_continuation([rb], launch)
    assert e.value.code == 10
    (tmp_path / "OVERFLOW-RULE.md").write_text("REGISTERED: RULING-X\n")  # registered, but not committed
    with pytest.raises(SystemExit) as e:
        stages.check_lane_continuation([rb], launch)
    assert e.value.code == 10
    monkeypatch.setattr(stages, "check_overflow_rule", lambda: "blob")
    stages.check_lane_continuation([rb], launch)
    scan = _job("SCAN/c2-p030-U-G/129005/M")  # the scan is not gated on the rule
    stages.check_lane_continuation([scan], {stages.BUILD_KEY: mjbuild.BUILD_LINE})


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


def test_read_log_keeps_each_seasons_last_attempt(tmp_path):
    path = tmp_path / mjbuild.EPA_LOG
    lines = [{"start": "t0", "pid": 1}, {"season": 60}, _ev("near", 17), {"season": 61}, _ev("near", 19), _ev("overflow", 25),
             {"hist": {"5": 10, "19": 1}, "epa_iterations": 11},
             {"start": "t1", "pid": 2}, {"season": 61}, _ev("near", 18), {"season": 62},
             {"hist": {"5": 4, "18": 1}, "epa_iterations": 5}]
    path.write_text("".join(json.dumps(x) + "\n" for x in lines) + '{"event": "near", "nedg')  # a line cut by a kill
    r = epa_ecology.read_log(str(path))
    assert r["starts"] == 2 and r["bad_lines"] == 1
    assert [e["nedges"] for e in r["seasons"][60]["near"]] == [17]
    assert [e["nedges"] for e in r["seasons"][61]["near"]] == [18] and r["seasons"][61]["overflow"] == []  # re-run season
    assert r["seasons"][62] == {"near": [], "overflow": []}
    assert (r["near"], r["overflow"]) == (2, 0) and r["max_nedges"] == 19  # the histogram saw the killed attempt's 19
    assert r["epa_iterations"] == 16 and r["hist"] == {5: 14, 19: 1, 18: 1}
    assert epa_ecology.read_log(str(tmp_path / "missing"))["starts"] == 0


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
