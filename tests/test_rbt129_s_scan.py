"""RBT-129 Stage-1 S silent-corruption scan (``runs/RBT-129/s-corruption-scan/sscan.py``): the replay set pinned by the
committed Stage-1 emission, the job chain, the cost, the comparison (bar ``workers``), the phase states, the lane gates
and the committed lanes; the chain end to end through ``stages``' real jobs on a toy ecology; the counts-only report."""
import importlib.util
import json
import os
import shutil
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCRIPT = os.path.join(REPO, "runs", "RBT-129", "s-corruption-scan", "sscan.py")
spec = importlib.util.spec_from_file_location("sscan", SCRIPT)
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
stages = S.stages
RUNS = S.RUNS


@pytest.fixture(scope="module")
def units():
    return S.sscan_units(RUNS)


def _refused(code, fn, *a, **k):
    with pytest.raises(SystemExit) as e:
        fn(*a, **k)
    assert e.value.code == code


def _lanes1():
    d = os.path.join(RUNS, "lanes", "1")
    return {j["name"]: j for f in sorted(os.listdir(d)) if f.endswith(".jsonl")
            for j in (json.loads(x) for x in open(os.path.join(d, f)) if x.strip())}


# -- the replay set and the chain --------------------------------------------------------------------------------- #

def test_the_replay_set_is_every_stage1_s_chain(units):
    """288 chains: every unit with an S resume job in lanes/1 (36 points x seeds 129001-129008); none excluded (the
    CRASHED Stage-1 unit is an M arm)."""
    l1 = _lanes1()
    chains = sorted({tuple(n.split("/")[1:3]) for n, j in l1.items() if j["job"] == "resume" and n.endswith("/S")})
    assert len(units) == len(chains) == 288 == 36 * 8
    assert [(u["jobs"][0]["point"], str(u["seed"])) for u in units] == chains
    assert {u["seed"] for u in units} == set(range(129001, 129009))
    assert not any("/M" in j["name"] or j["name"].endswith("/N") for u in units for j in u["jobs"])


def test_each_chain_is_stage1s_chain_on_the_build(units):
    """S60 fresh at Stage 1's salts (exactly its extra; the census adoption at (0, 0)), ckpt60, S to 300, and the two
    comparisons against the stored ckpt60 and S."""
    l1 = _lanes1()
    salts = stages._salts_line(stages.read_launch(os.path.join(RUNS, "lanes", "1", "launch.txt"))["salts"])
    for u in units:
        fresh, snap, res, c60, cs = u["jobs"]
        pid, sd = fresh["point"], u["seed"]
        unit = f"{pid}/{sd}"
        d = os.path.join(RUNS, S.SCAN_DIR, "replay", pid, str(sd))
        st1 = os.path.join(RUNS, "stage1", pid, str(sd))
        assert [j["name"] for j in u["jobs"]] == [f"SSCAN/{unit}/{t}" for t in ("S60", "ckpt60", "S", "ckpt60-cmp", "S-cmp")]
        assert [j["job"] for j in u["jobs"]] == ["fresh", "snapshot", "resume", "sscancmp", "sscancmp"]
        assert fresh["dir"] == res["dir"] == cs["dir"] == f"{d}/S" and snap["dir"] == c60["dir"] == f"{d}/ckpt60"
        assert fresh["seasons"] == 60 and res["seasons"] == 300 and snap["src"] == f"{d}/S"
        assert c60["ref"] == f"{st1}/ckpt60" and cs["ref"] == f"{st1}/S"
        assert fresh["extra"] == stages.salts_argv(*salts[sd])
        s60 = l1[f"1/{unit}/S60"]
        assert (s60["job"], s60.get("extra", [])) in (("fresh", fresh["extra"]), ("adopt", []))
        if s60["job"] == "adopt":
            assert sd == 129001 and salts[sd] == (0, 0)


def test_the_cost(units):
    assert S.arm_seasons(units) == 288 * 300 == 86400
    lo, hi = S.core_h(units)
    assert round(lo) == 560 and round(hi) == 1049


# -- the comparison and the states --------------------------------------------------------------------------------- #

def _run_dir(d, files, workers=2):
    os.makedirs(d, exist_ok=True)
    json.dump({"seed": 1, "workers": workers, "ecology": {"merge_after": None}}, open(os.path.join(d, "config.json"), "w"))
    for n, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(d, n)) or d, exist_ok=True)
        open(os.path.join(d, n), "w").write(text)


def test_the_verdict_is_byte_for_byte_bar_logs_and_workers(tmp_path):
    a, b = str(tmp_path / "stored"), str(tmp_path / "replay")
    same = {"lineage.jsonl": "x\n", "history.json": "{}", "state.json": "{}"}
    _run_dir(a, {**same, "run.log": "stock", "platform.json": "{}", "command.txt": "a"}, workers=4)
    _run_dir(b, {**same, "run.log": "build", "epa_overflow.jsonl": "{}", ".rbt129-done-S": "t", S.SSCAN_FILE: "v"})
    assert S.verdict(a, b) == ("IDENTICAL", ["3 files compared"])
    open(os.path.join(b, "lineage.jsonl"), "w").write("y\n")
    open(os.path.join(b, "cohorts.jsonl"), "w").write("z\n")
    word, lines = S.verdict(a, b)
    assert word == "DIFFER" and "DIFFERS: lineage.jsonl" in lines and "only in replay: cohorts.jsonl" in lines
    _run_dir(b, same)
    os.remove(os.path.join(b, "cohorts.jsonl"))
    cfg = json.load(open(os.path.join(b, "config.json")))
    json.dump({**cfg, "seed": 2}, open(os.path.join(b, "config.json"), "w"))
    assert S.verdict(a, b) == ("DIFFER", ["3 files compared", "DIFFERS: config.json (bar workers)"])


def _info(seasons, overflow=(), unlogged=(), none_overflow=False):
    per = {s: {"near": [], "overflow": [1] if s in overflow else []} for s in seasons}
    if none_overflow:
        per[None] = {"near": [], "overflow": [1]}
    return {"seasons": per, "unlogged": list(unlogged)}


def test_the_phase_states():
    full, s60 = range(0, 300), range(0, 60)
    assert S.phase_state(_info(full), s60, "CLEAN (seasons 0-59)") == "CLEAN (seasons 0-59)"
    assert S.phase_state(_info(full, overflow=(150,)), s60, "CLEAN (seasons 0-59)") == "CLEAN (seasons 0-59)"
    assert S.phase_state(_info(full, overflow=(150,)), full, "CLEAN (seasons 0-299)") == "OVERFLOWED"
    assert S.phase_state(_info(full, overflow=(30,)), s60, "CLEAN (seasons 0-59)") == "OVERFLOWED"
    assert S.phase_state(_info(full, none_overflow=True), s60, "x") == "OVERFLOWED"        # before a season line
    assert S.phase_state(_info(range(0, 59)), s60, "x") == "UNLOGGED"                       # a season unlogged
    assert S.phase_state(_info(full, unlogged=("bad line",)), s60, "x") == "UNLOGGED"
    assert S.phase_state(_info(range(0, 38)), range(0, 38), "CLEAN") == "CLEAN"            # a pre-merge extinction


# -- the gates --------------------------------------------------------------------------------------------------- #

def _emitted(units):
    worlds = os.path.join(RUNS, "worlds")
    return [{k: (stages.rel(v) if k in stages.PATH_KEYS else v) for k, v in {**j, "worlds": worlds}.items()}
            for u in units for j in u["jobs"]]


def test_the_lane_check(units):
    launch = {stages.BUILD_KEY: "x", "go": S.GO_VALUE}
    jobs = [{k: (stages.absolute(v) if k in stages.PATH_KEYS else v) for k, v in j.items()} for j in _emitted(units[:3])]
    S.check_lane_sscan(jobs, launch)
    _refused(4, S.check_lane_sscan, jobs, {stages.BUILD_KEY: "x", "go": "RBT129-S2-2A-GO-1"})
    for bad in ({**jobs[0], "job": "resume"}, {**jobs[1], "name": jobs[1]["name"].replace("SSCAN/", "SCAN/")},
                {**jobs[2], "dir": os.path.join(RUNS, "stage1", "x", "129001", "S")},
                {**jobs[3], "ref": os.path.join(RUNS, "stage1", "c2-p030-U-G", "129001", "M")}):
        _refused(4, S.check_lane_sscan, [bad], launch)


def test_the_go_parse():
    assert not S.go_open("GO-ID-SSCAN-PENDING: RBT129-SSCAN-GO-1\n")
    assert S.go_open("x\nGO-ID-SSCAN: RBT129-SSCAN-GO-1\n")
    assert not S.go_open("GO-ID-SSCAN: RBT129-SSCAN-GO-1\nGO-ID-SSCAN: RBT129-SSCAN-GO-1\n")
    assert not S.go_open("GO-ID-SSCAN: \n") and not S.go_open("GO-ID-SSCAN: RBT129-SSCAN-GO-2\n")
    assert not S.go_open(open(os.path.join(REPO, S.LOCKS_REL)).read())   # committed PENDING: the coordinator opens it


def _sh(cwd, *a):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_check_go_reads_the_merged_base_after_a_narrow_fetch(tmp_path):
    origin, work = str(tmp_path / "o.git"), str(tmp_path / "w")
    _sh(str(tmp_path), "init", "-q", "--bare", origin)
    _sh(str(tmp_path), "init", "-q", work)
    for k, v in (("user.email", "t@t"), ("user.name", "t")):
        _sh(work, "config", k, v)
    _sh(work, "remote", "add", "origin", origin)
    path = os.path.join(work, S.LOCKS_REL)
    os.makedirs(os.path.dirname(path))
    text = open(os.path.join(REPO, S.LOCKS_REL)).read()
    open(path, "w").write(text)
    _sh(work, "add", "-A")
    _sh(work, "commit", "-q", "-m", "pending")
    _sh(work, "push", "-q", "origin", "HEAD:refs/heads/b")
    _refused(10, S.check_go, "b", work)
    open(path, "w").write(text.replace("GO-ID-SSCAN-PENDING:", "GO-ID-SSCAN:"))
    _sh(work, "commit", "-q", "-am", "open, locally only")
    _refused(10, S.check_go, "b", work)                       # read from the merged base, never the checkout
    _sh(work, "push", "-q", "origin", "HEAD:refs/heads/b")
    S.check_go("b", work)
    _sh(work, "remote", "set-url", "origin", str(tmp_path / "gone.git"))
    _refused(10, S.check_go, "b", work)                       # a failed fetch refuses, whatever the tracking ref shows


def test_the_code_gate():
    launch = S.code_pins()
    S.check_code(launch, loaded=set(S.CODE_FILES))
    _refused(5, S.check_code, {"code:runs/RBT-129/s-corruption-scan/sscan.py": "0" * 40}, loaded=set(S.CODE_FILES))
    _refused(5, S.check_code, launch, loaded=set(S.CODE_FILES) | {"runs/RBT-129/stage2/s2lanes.py"})
    _refused(5, S.check_code, {}, loaded=set(S.CODE_FILES))


def test_it_imports_nothing_from_stage2():
    """NOTE 17 and P-1: the scan's code is this file alone, outside the pinned trees, importing no Stage-2 module."""
    imports = [x for x in open(SCRIPT).read().splitlines() if x.lstrip().startswith(("import ", "from "))]
    assert imports and not any("s2" in x or "stage2" in x or "readout" in x for x in imports)
    assert not any(S.CODE_FILES[0].startswith(t + "/") for t in stages.PINNED_TREES)


# -- the committed lanes ------------------------------------------------------------------------------------------- #

def test_the_committed_lanes_are_what_emit_writes(units):
    lane_dir = os.path.join(RUNS, "lanes", S.NAME)
    launch = stages.read_launch(os.path.join(lane_dir, "launch.txt"))
    import mjbuild
    assert launch[stages.BUILD_KEY] == mjbuild.BUILD_LINE and launch["go"] == S.GO_VALUE
    assert {k: v for k, v in launch.items() if k.startswith("code:")} == S.code_pins()
    for t in stages.PINNED_TREES:
        assert launch["tree:" + t] == stages._git("rev-parse", f"HEAD:{t}")
    assert int(launch["units"]) == 288 and launch["salts"] == stages.read_launch(
        os.path.join(RUNS, "lanes", "1", "launch.txt"))["salts"]
    files = sorted(f for f in os.listdir(lane_dir) if f.endswith(".jsonl"))
    assert len(files) == 2 * int(launch["hosts"])
    jobs = []
    for f in files:
        raw = [json.loads(x) for x in open(os.path.join(lane_dir, f)) if x.strip()]
        S.check_emission(os.path.join(lane_dir, f), launch, raw)
        jobs += raw
    assert sorted(j["name"] for j in jobs) == sorted(j["name"] for j in _emitted(units))
    absj = [{k: (stages.absolute(v) if k in stages.PATH_KEYS else v) for k, v in j.items()} for j in jobs]
    stages.check_lane_salts(absj, launch)
    S.check_lane_sscan(absj, launch)
    _refused(4, S.check_emission, os.path.join(lane_dir, files[0]), launch, raw[::-1])


# -- the chain end to end, through stages' real jobs on a toy ecology -------------------------------------------- #

EXTINCT_AT = {}
OVERFLOW_AT = {}


def toy_ecology(cmd, d, label, long=False):
    """``stages._ecology`` replaced: deterministic per (seed, salts, season); a continuation logs as the build does."""
    import epa_ecology as EPA
    import mjbuild

    seasons = int(cmd[cmd.index("--seasons") + 1])
    if "--resume" in cmd:
        cfg = json.load(open(os.path.join(d, "config.json")))
        start = json.load(open(os.path.join(d, "state.json")))["season"]
    else:
        cfg = {"seed": int(cmd[cmd.index("--seed") + 1]), "ecology": {"merge_after": None},
               "workers": int(os.environ.get("WORKERS", "2"))}
        json.dump(cfg, open(os.path.join(d, "config.json"), "w"))
        start = 0
    key = (cfg["seed"], os.path.normpath(d).split(os.sep)[-4])            # (seed, "stage1" | "replay")
    end = min(seasons, EXTINCT_AT.get(key, seasons))
    cont = stages._CONTINUATION
    log = os.path.join(d, mjbuild.EPA_LOG)
    if cont:
        with open(log, "a") as f:
            f.write(json.dumps({"start": "T", "unit": EPA.unit_id(d), "attempt": EPA.attempts(log), "workers": 2, "pid": 1,
                                "libmujoco_sha256": "x"}) + "\n")
    with open(os.path.join(d, "lineage.jsonl"), "a") as lf, open(log, "a") if cont else open(os.devnull, "w") as ef:
        for s in range(start, end):
            lf.write(json.dumps({"seed": cfg["seed"], "season": s}) + "\n")
            ef.write(json.dumps({"season": s, "pid": 1}) + "\n")
            if s in OVERFLOW_AT.get(key, ()):
                ef.write(json.dumps({"event": "overflow", "unit": EPA.unit_id(d), "attempt": EPA.attempts(log) - 1,
                                     "pid": 1, "seq": s, "nedges": 25, "step": 1}) + "\n")
    alive = key not in EXTINCT_AT
    json.dump({"season": end, "populations": {"h": ["hF"] if alive else [], "d": ["dF"] if alive else []}},
              open(os.path.join(d, "state.json"), "w"))
    if cont:
        EPA.write_exit(d, 0)


@pytest.fixture
def toy(monkeypatch):
    monkeypatch.setenv("NO_DURABLE", "1")
    monkeypatch.setattr(stages, "_ecology", toy_ecology)
    monkeypatch.setattr(stages, "check_continuation_build", lambda line=None: {})
    monkeypatch.setattr(stages, "CONTINUATION_PREFIXES", stages.CONTINUATION_PREFIXES)
    S.with_sscan_prefix()
    yield
    EXTINCT_AT.clear()
    OVERFLOW_AT.clear()


def _chain(units, root, pid, sd, prefix):
    """A unit's chain under ``prefix`` (``1/``: the stored Stage-1 run, stock; ``SSCAN/``: the replay), rooted at
    ``root``, as sscan_units writes it."""
    u = next(x for x in units if x["jobs"][0]["point"] == pid and x["seed"] == sd)
    out = []
    for j in u["jobs"]:
        j = {**j, "worlds": os.path.join(RUNS, "worlds")}
        for k in ("dir", "src", "ref"):
            if k in j:
                j[k] = os.path.join(root, os.path.relpath(j[k], RUNS))
        if prefix == "1/":
            if j["job"] == "sscancmp":
                continue
            j = {**j, "name": "1/" + j["name"][len("SSCAN/"):],
                 **{k: j[k].replace(os.path.join(S.SCAN_DIR, "replay"), "stage1") for k in ("dir", "src") if k in j}}
        out.append(j)
    return out


def _run(jobs):
    for j in jobs:
        S.run_job(j)


PT = "c1-p080-U-L"


def test_a_chain_end_to_end(units, tmp_path, toy, monkeypatch, capsys):
    """Stage 1's stored chain (stock) and the scan's replay (the build) through the real jobs: IDENTICAL and CLEAN on
    both comparisons, bar a different worker count; an S60-phase overflow is OVERFLOWED for both; a stored file changed
    is a DIFFER (names only); a stored run with no marker is NO-REFERENCE; a pre-merge extinction takes its own path."""
    root = str(tmp_path)
    cases = {129002: "clean", 129003: "s60-overflow", 129004: "late-overflow", 129005: "differ", 129006: "noref",
             129007: "extinct"}
    OVERFLOW_AT.update({(129003, "replay"): (30,), (129004, "replay"): (150,)})
    EXTINCT_AT.update({(129007, "stage1"): 38, (129007, "replay"): 38})
    for sd in cases:
        monkeypatch.setenv("WORKERS", "4")
        _run(_chain(units, root, PT, sd, "1/"))
    st1 = lambda sd, arm: os.path.join(root, "stage1", PT, str(sd), arm)
    open(os.path.join(st1(129005, "S"), "lineage.jsonl"), "a").write("tampered\n")
    os.remove(os.path.join(st1(129006, "S"), ".rbt129-done-S"))
    monkeypatch.setenv("WORKERS", "2")
    for sd in cases:
        _run(_chain(units, root, PT, sd, "SSCAN/"))
    out = capsys.readouterr().out
    first = lambda sd, tag: open(os.path.join(root, S.SCAN_DIR, "replay", PT, str(sd),
                                               "ckpt60" if tag == "ckpt60-cmp" else "S", S.SSCAN_FILE)).read().splitlines()[:2]
    assert first(129002, "ckpt60-cmp")[0].startswith("SSCAN IDENTICAL: ") and "CLEAN (seasons 0-59); overflow 0" in first(129002, "ckpt60-cmp")[1]
    assert first(129002, "S-cmp")[0].startswith("SSCAN IDENTICAL: ") and "CLEAN (seasons 0-299); overflow 0" in first(129002, "S-cmp")[1]
    assert "OVERFLOWED; overflow 1" in first(129003, "ckpt60-cmp")[1] and "OVERFLOWED; overflow 1" in first(129003, "S-cmp")[1]
    assert "CLEAN (seasons 0-59)" in first(129004, "ckpt60-cmp")[1] and "OVERFLOWED; overflow 1" in first(129004, "S-cmp")[1]
    assert first(129005, "ckpt60-cmp")[0].startswith("SSCAN IDENTICAL") and first(129005, "S-cmp")[0].startswith("SSCAN DIFFER")
    assert first(129006, "S-cmp")[0].startswith("SSCAN NO-REFERENCE")
    assert first(129007, "S-cmp")[0].startswith("SSCAN IDENTICAL") and "CLEAN (seasons 0-299)" in first(129007, "S-cmp")[1]
    assert os.path.exists(os.path.join(root, S.SCAN_DIR, "replay", PT, "129007", "EXTINCT.txt"))
    # the runner's lines carry the verdict, the state and the count only: no file name, season or EPA figure
    lines = [x for x in out.splitlines() if "SSCAN " in x]
    assert len(lines) == 12 and not any("lineage" in x or "near" in x or "horizon" in x for x in lines)
    # markers: a second run skips every job (restart safety), the comparison's marker note is the verdict line
    note = open(os.path.join(root, S.SCAN_DIR, "replay", PT, "129002", "S", ".rbt129-done-S-cmp")).read()
    assert "SSCAN IDENTICAL:" in note
    _run(_chain(units, root, PT, 129002, "SSCAN/"))
    assert "SSCAN " not in capsys.readouterr().out

    # the report: counts only, names only the flagged units
    monkeypatch.setattr(S, "sscan_units", lambda r=None: [
        {"stage": "SSCAN", "seed": sd, "jobs": _chain(units, root, PT, sd, "SSCAN/")} for sd in list(cases) + [129008]])
    rep = S.scan_report(root)
    assert "S60 phase (seasons 0-59): CLEAN (seasons 0-59) 5, IDENTICAL 6, OVERFLOWED 1, PENDING 1" in rep
    assert "S (seasons 0-299): CLEAN (seasons 0-299) 4, DIFFER 1, IDENTICAL 4, NO-REFERENCE 1, OVERFLOWED 2, PENDING 1" in rep
    named = rep.split("named (DIFFER, NO-REFERENCE, OVERFLOWED or UNLOGGED only):\n")[1].split("\n\n")[0].splitlines()
    assert sorted(x.split(":")[0].strip() for x in named) == sorted(
        [f"{PT}/129003/ckpt60-cmp", f"{PT}/129003/S-cmp", f"{PT}/129004/S-cmp", f"{PT}/129005/S-cmp", f"{PT}/129006/S-cmp"])
    assert "lineage" not in rep and "near" not in rep and "horizon" not in rep and "units: 7" in rep
