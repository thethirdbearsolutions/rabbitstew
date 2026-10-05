"""RBT-129 Stage 2a's emitter and lane runner (runs/RBT-129/stage2/s2lanes.py), on synthetic run directories.

No Stage-2 run exists; nothing is launched.  The repository files read are registered inputs only: lanes/1 and
lanes/1-MN launch records, the committed census readout, the accepted Stage-1 record and RULINGS-CITED-S2.md."""
import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCRIPT = os.path.join(REPO, "runs", "RBT-129", "stage2", "s2lanes.py")
spec = importlib.util.spec_from_file_location("s2lanes", SCRIPT)
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)
stages, s2 = L.stages, L.s2


@pytest.fixture(scope="module")
def built():
    salts, launch = L.s2a_inputs(L.RUNS)
    gate = L.s2a_gate()
    return salts, launch, gate, L.s2a_units(L.RUNS, salts, gate)


def _launch(gate):
    return {"go": L.GO_VALUE, stages.BUILD_KEY: "x", "s2a_points": " ".join(s2.STAGE2A_POINTS),
            "s2a_m": " ".join(r["point"] for r in gate if r["m"]), "s2a_n": " ".join(r["point"] for r in gate if r["n"])}


def _jobs(units):
    return [{k: (os.path.join(L.ROOT, stages.rel(v)) if k in stages.PATH_KEYS else v) for k, v in j.items()}
            for u in units for j in u["jobs"]]


def test_the_gate_is_the_plans(built):
    _, _, gate, _ = built
    cen = s2.sr.census_layer(s2.CENSUS_TXT)
    m, n, _ = s2.mn_gate(s2.STAGE2A_POINTS, cen, s2.M_CAP["2a"], s2.N_CAP["2a"])
    assert [r["point"] for r in gate if r["m"]] == m == ["c1-p018-PW-L", "c1-p053-U-L", "c1-p053-U-G"]
    assert [r["point"] for r in gate if r["n"]] == n == ["c1-p018-PW-L"]


def test_the_units_and_the_budget(built):
    salts, _, gate, units = built
    assert len(units) == 12 * 8
    tags = lambda u: [j["name"].rsplit("/", 1)[1] for j in u["jobs"]]
    for u in units:
        j = u["seed"] - 129000
        pid = u["jobs"][0]["point"]
        want = ["S60"] + (["S60CMP"] if j == 1 else ["KSALT"] if j in (2, 3) else []) + ["ckpt60", "S"]
        want += (["M"] if pid in ("c1-p018-PW-L", "c1-p053-U-L", "c1-p053-U-G") else []) + (["N"] if pid == "c1-p018-PW-L" else [])
        assert tags(u) == want, (pid, j)
        assert u["jobs"][0]["extra"] == stages.salts_argv(*salts[u["seed"]])
    a = L.arm_seasons(units)
    assert a == {"S": 12 * 8 * 300, "M": 3 * 8 * 240, "N": 1 * 8 * 240}
    b = s2.budget(3, 1, 0, 0, 0)                     # the plan's 2a rows (O-2 re-simulation included)
    assert b["2a S"] == pytest.approx(s2.core_h(a["S"])) and b["2a M"] == pytest.approx(s2.core_h(a["M"]))
    assert b["2a N"] == pytest.approx(s2.core_h(a["N"]))


def test_the_census_references_and_forks(built):
    _, _, _, units = built
    for u in units:
        for j in u["jobs"]:
            pid, sd, tag = j["name"].split("/")[1:]
            if tag in ("S60CMP", "KSALT"):
                assert j["ref"].endswith(os.path.join("stage0", pid, sd, "S"))
            if tag in ("M", "N"):
                assert j["seed_rule"] and j["src"].endswith(os.path.join("stage2a", pid, sd, "ckpt60"))
                if tag == "N":
                    assert j["set"]["merge_null"] == stages.null_kind(int(sd) - 129000)


def test_the_lane_check_accepts_what_emit_wrote(built):
    _, _, gate, units = built
    L.check_lane_s2a(_jobs(units), _launch(gate))


@pytest.mark.parametrize("mutate", [
    lambda j: j.update(job="fresh") if j["name"].endswith("/S60CMP") else None,                   # wrong kind
    lambda j: j.update(name=j["name"].replace("/129002/", "/129009/")) if "/129002/" in j["name"] else None,
    lambda j: j.update(ref=j["ref"].replace("129001", "129002")) if j["name"].endswith("/S60CMP") else None,
    lambda j: j.update(set={**j["set"], "pooled_capacity": 60}) if j["name"].endswith("/M") else None,
    lambda j: j.update(seed_rule=False) if j["name"].endswith("/N") else None,
    lambda j: j.update(dir=j["dir"].replace("stage2a", "stage1")) if j["name"].endswith("/S") else None,
])
def test_the_lane_check_refuses_a_hand_edit(built, mutate):
    _, _, gate, units = built
    jobs = _jobs(units)
    for j in jobs:
        mutate(j)
    with pytest.raises(SystemExit) as e:
        L.check_lane_s2a(jobs, _launch(gate))
    assert e.value.code == 4


def test_m_at_a_point_the_gate_did_not_admit_is_refused(built):
    _, _, gate, units = built
    jobs = _jobs(units)
    extra = dict(next(j for j in jobs if j["name"].endswith("/M")))
    pid = "c05-p080-U-G"
    extra.update(name=f"S2A/{pid}/129004/M", src=os.path.join(L.RUNS, "stage2a", pid, "129004", "ckpt60"),
                 dir=os.path.join(L.RUNS, "stage2a", pid, "129004", "M"), seed=129004)
    with pytest.raises(SystemExit):
        L.check_lane_s2a(jobs + [extra], _launch(gate))


def test_a_launch_without_the_s2a_lines_is_refused(built):
    _, _, gate, units = built
    with pytest.raises(SystemExit):
        L.check_lane_s2a(_jobs(units), {**_launch(gate), "go": "RBT129-RB-GO-1"})


# --- O-2: the re-simulation against the census ----------------------------------------------------------------------

def _s60(d, season=60, config=None, lineage="a\nb\n"):
    os.makedirs(d, exist_ok=True)
    cfg = config or {"ecology": {"merge_after": None}, "seed": 129001, "workers": 2}
    json.dump(cfg, open(os.path.join(d, "config.json"), "w"))
    json.dump({"season": season, "populations": {"holistic": [1], "conventional": [1]}}, open(os.path.join(d, "state.json"), "w"))
    open(os.path.join(d, "lineage.jsonl"), "w").write(lineage)
    open(os.path.join(d, "history.json"), "w").write("{}")
    open(os.path.join(d, "platform.json"), "w").write("{\"build\": \"x\"}")
    open(os.path.join(d, "epa_overflow.jsonl"), "w").write("{}\n")
    open(os.path.join(d, ".rbt129-done-S60"), "w").write("t")


def test_s60_verdict(tmp_path):
    a, b = str(tmp_path / "re"), str(tmp_path / "census")
    _s60(a)
    _s60(b, config={"ecology": {"merge_after": None}, "seed": 129001, "workers": 4})   # workers differ: ignored
    open(os.path.join(b, "platform.json"), "w").write("{\"stock\": 1}")                # provenance differs: ignored
    assert L.s60_verdict(a, b)[0] == "IDENTICAL"
    open(os.path.join(b, "lineage.jsonl"), "w").write("a\nc\n")
    v, lines = L.s60_verdict(a, b)
    assert v == "DIFFER" and "DIFFERS: lineage.jsonl" in lines
    _s60(b, config={"ecology": {"merge_after": None}, "seed": 129002, "workers": 4})
    assert "DIFFERS: config.json (bar workers)" in L.s60_verdict(a, b)[1]


def test_s60_compare_writes_its_verdict_and_stops_on_differ(tmp_path, monkeypatch):
    monkeypatch.setenv("NO_DURABLE", "1")
    a, b, d = str(tmp_path / "re"), str(tmp_path / "census"), str(tmp_path / "s60cmp")
    _s60(a)
    _s60(b)
    job = {"name": "S2A/c05-p080-U-G/129001/S60CMP", "src": a, "ref": b, "seasons": 60}
    assert L.s60_compare(job, d) == "IDENTICAL"
    assert open(os.path.join(d, L.S60CMP_FILE)).readline().startswith("S60CMP IDENTICAL")
    open(os.path.join(b, "lineage.jsonl"), "w").write("x\n")
    with pytest.raises(SystemExit) as e:
        L.s60_compare(job, d)
    assert e.value.code == 4 and L.s60cmp_word(d) == "DIFFER"


def test_a_differ_refuses_every_later_job_of_the_unit_on_every_restart(tmp_path, monkeypatch):
    """BLOCKING 1 (#533 adversary): a lane restarted after a DIFFER never adopts the re-simulation; ckpt60, S, M and N of
    the 129001 unit refuse (exit 4) without a saved IDENTICAL beside them."""
    monkeypatch.setenv("NO_DURABLE", "1")
    ran = []
    monkeypatch.setattr(L.stages, "run_job", lambda job: ran.append(job["name"]))
    unit = tmp_path / "stage2a" / "c05-p080-U-G" / "129001"
    census = str(tmp_path / "census")
    _s60(str(unit / "S"))
    _s60(census)
    open(os.path.join(census, "lineage.jsonl"), "w").write("x\n")
    name = "S2A/c05-p080-U-G/129001/"
    cmp_job = {"job": "s60cmp", "name": name + "S60CMP", "seed": 129001, "src": str(unit / "S"), "ref": census,
               "dir": str(unit / "s60cmp"), "seasons": 60}
    later = [{"job": "snapshot", "name": name + "ckpt60", "seed": 129001, "src": str(unit / "S"), "dir": str(unit / "ckpt60")},
             {"job": "resume", "name": name + "S", "seed": 129001, "dir": str(unit / "S")},
             {"job": "fork", "name": name + "M", "seed": 129001, "src": str(unit / "ckpt60"), "dir": str(unit / "M")}]
    for job in later:                                        # before any comparison: no record, refused
        with pytest.raises(SystemExit) as e:
            L.run_job(job)
        assert e.value.code == 4
    L.run_job({**cmp_job, "job": "fresh", "name": name + "S60", "dir": str(unit / "S")})   # S60 itself is not gated
    assert ran == [name + "S60"]
    for restart in range(3):                                 # the first run and two restarts of the lane
        with pytest.raises(SystemExit) as e:
            L.run_job(cmp_job)
        assert e.value.code == 4
        for job in later:
            with pytest.raises(SystemExit) as e:
                L.run_job(job)
            assert e.value.code == 4
    assert ran == [name + "S60"] and not (unit / "ckpt60").exists()
    # a verdict file edited to IDENTICAL beside a DIFFER marker is still a DIFFER
    open(unit / "s60cmp" / L.S60CMP_FILE, "w").write("S60CMP IDENTICAL: edited\n")
    with pytest.raises(SystemExit):
        L.run_job(later[0])
    # an IDENTICAL comparison lets the unit go on, and a restart skips it
    import shutil
    shutil.rmtree(unit / "s60cmp")
    open(os.path.join(census, "lineage.jsonl"), "w").write(open(unit / "S" / "lineage.jsonl").read())
    L.run_job(cmp_job)
    L.run_job(cmp_job)
    for job in later:
        L.run_job(job)
    assert ran == [name + "S60"] + [j["name"] for j in later]


def test_s60_compare_runs_only_before_s_resumes(tmp_path, monkeypatch):
    monkeypatch.setenv("NO_DURABLE", "1")
    a, b = str(tmp_path / "re"), str(tmp_path / "census")
    _s60(a, season=180)
    _s60(b)
    with pytest.raises(SystemExit) as e:
        L.s60_compare({"name": "S2A/x/129001/S60CMP", "src": a, "ref": b, "seasons": 60}, str(tmp_path / "c"))
    assert e.value.code == 4


# --- the gates ------------------------------------------------------------------------------------------------------

def test_the_2a_go_is_closed_today_and_opens_only_well_formed():
    text = L.committed(L.RULINGS_REL)
    if not L.go_open(text):                                  # today: GO-ID-2A is PENDING
        with pytest.raises(SystemExit) as e:
            L.check_go()
        assert e.value.code == 10
    assert L.go_open("2B2A: COMMITTED\nGO-ID-2A: RBT129-S2-2A-GO-1\n")
    assert not L.go_open("GO-ID-2A: RBT129-S2-2A-GO-1\n")                        # no 2B2A line
    assert not L.go_open("2B2A: COMMITTED\nGO-ID-2A: OTHER\n")
    assert not L.go_open("2B2A: COMMITTED\nGO-ID-2A: RBT129-S2-2A-GO-1\nGO-ID-2A: RBT129-S2-2A-GO-1\n")   # duplicate


def test_stage2a_jobs_are_continuations_only_through_the_one_override():
    job = {"name": "S2A/c05-p080-U-G/129001/S60"}
    saved = stages.CONTINUATION_PREFIXES
    try:
        stages.CONTINUATION_PREFIXES = tuple(p for p in saved if p != L.PREFIX)
        assert not stages.continuation(job)
        L.with_s2a_prefix()
        L.with_s2a_prefix()
        assert stages.continuation(job) and stages.CONTINUATION_PREFIXES.count(L.PREFIX) == 1
    finally:
        stages.CONTINUATION_PREFIXES = saved


def test_emit_refuses_off_the_build():
    import mjbuild
    try:
        mjbuild.check_instrumented()
        pytest.skip("this process runs the instrumented build")
    except SystemExit:
        pass
    with pytest.raises(SystemExit) as e:
        L.emit(L.RUNS, 10)
    assert e.value.code == 9


def test_the_driver_touches_no_pinned_tree():
    """NOTE 17: Stage 2a's code lives outside stages.PINNED_TREES."""
    for t in stages.PINNED_TREES:
        assert not os.path.abspath(SCRIPT).startswith(os.path.join(L.ROOT, t) + os.sep)
        assert not any(t == o or o.startswith(t + "/") for o in L.OWN_TREES + L.CODE_FILES)
    assert {os.path.relpath(f, L.ROOT) for f in (SCRIPT, s2.__file__, s2.sr.__file__)} == set(L.CODE_FILES)
    assert not set(L.UNPINNED) & set(L.CODE_FILES)


def test_the_committed_lanes_are_what_emit_writes(built):
    """lanes/S2A as committed: its launch record names the registered build, the GO and the gate, pins this tree's
    launch tree, and every job passes the lane check and equals an emitted job."""
    _, _, gate, units = built
    lane_dir = os.path.join(L.RUNS, "lanes", L.NAME)
    launch = stages.read_launch(os.path.join(lane_dir, "launch.txt"))
    import mjbuild
    assert launch[stages.BUILD_KEY] == mjbuild.BUILD_LINE and launch["go"] == L.GO_VALUE
    assert launch["s2a_m"].split() == [r["point"] for r in gate if r["m"]]
    assert launch["s2a_n"].split() == [r["point"] for r in gate if r["n"]]
    assert launch["tree:runs/RBT-129/launch"] == stages._git("rev-parse", "HEAD:runs/RBT-129/launch")
    assert {k: v for k, v in launch.items() if k.startswith("code:")} == L.code_pins()   # MAJOR 2: by blob, no tree:
    assert not any(k.startswith("tree:runs/RBT-129/stage2") for k in launch)
    for f in sorted(os.listdir(lane_dir)):                                                # MINOR 7
        if f.endswith(".jsonl"):
            L.check_emission(os.path.join(lane_dir, f), launch,
                             [json.loads(x) for x in open(os.path.join(lane_dir, f)) if x.strip()])
    jobs = [json.loads(x) for f in sorted(os.listdir(lane_dir)) if f.endswith(".jsonl")
            for x in open(os.path.join(lane_dir, f)) if x.strip()]
    emitted = {j["name"]: {k: (stages.rel(v) if k in stages.PATH_KEYS else v) for k, v in j.items()}
               for u in units for j in u["jobs"]}
    assert sorted(j["name"] for j in jobs) == sorted(emitted)
    for j in jobs:
        assert {k: v for k, v in j.items() if k != "worlds"} == emitted[j["name"]]
    L.check_lane_s2a([{k: (stages.absolute(v) if k in stages.PATH_KEYS else v) for k, v in j.items()} for j in jobs], launch)


# --- MAJOR 2, MINOR 5 and 6 (#533 adversary): the gates in a scratch repository with a local bare origin ----------

def _sh(cwd, *a):
    import subprocess
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def _write(root, rel, text):
    os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
    open(os.path.join(root, rel), "w").write(text)


def _commit(root, msg, push="b"):
    _sh(root, "add", "-A")
    _sh(root, "commit", "-q", "-m", msg)
    if push:
        _sh(root, "push", "-q", "origin", f"HEAD:refs/heads/{push}")


@pytest.fixture()
def scratch(tmp_path):
    """A repository holding the lane's code, RULINGS-CITED-S2.md as committed here (GO-ID-2A PENDING, 2B2A COMMITTED),
    continuations/QUARANTINE.md and the plan; origin is a local bare repository with the base ``b``."""
    origin, work = str(tmp_path / "origin.git"), str(tmp_path / "work")
    _sh(str(tmp_path), "init", "-q", "--bare", origin)
    _sh(str(tmp_path), "init", "-q", work)
    _sh(work, "config", "user.email", "t@t")
    _sh(work, "config", "user.name", "t")
    _sh(work, "remote", "add", "origin", origin)
    for rel in L.CODE_FILES + L.UNPINNED + ("runs/RBT-129/stage2-plan/STAGE2-PLAN.md",):
        text = open(os.path.join(L.ROOT, rel)).read()
        _write(work, rel, pending(text) if rel == L.RULINGS_REL else text)
    _commit(work, "base")
    return work


def pending(text):
    """RULINGS-CITED-S2.md with every GO line in its PENDING form, whatever the committed file has opened since (the
    scratch repository's base is the state before any GO, so each test makes the opening transition itself)."""
    for tag in ("GO-ID-2A", "GO-ID-INTERIM", "GO-ID-FINAL"):
        text = text.replace(f"\n{tag}: ", f"\n{tag}-PENDING: ")
    assert "\nGO-ID-2A-PENDING: RBT129-S2-2A-GO-1" in text and "\nGO-ID-2A: " not in text
    return text


def _rulings(work):
    return open(os.path.join(work, L.RULINGS_REL)).read()


def _open_go(text):
    return text.replace("GO-ID-2A-PENDING: RBT129-S2-2A-GO-1", "GO-ID-2A: RBT129-S2-2A-GO-1")


def _refused(code, fn, *a, **k):
    with pytest.raises(SystemExit) as e:
        fn(*a, **k)
    assert e.value.code == code, e.value.code


def test_opening_the_go_and_later_locks_leave_the_lanes_runnable_and_code_changes_do_not(scratch):
    """MAJOR 2: the lane pins the code it executes by blob; opening GO-ID-2A, a later lock, a ruled QUARANTINE: line and
    a plan edit change nothing it pins (no exit 5), and the GO and the quarantine are read from the merged base."""
    work = scratch
    launch = L.code_pins(work)
    assert set(launch) == {f"code:{p}" for p in L.CODE_FILES} and all(launch.values())
    L.check_code(launch, work, loaded=L.CODE_FILES)
    _refused(10, L.check_go, "b", work)                                    # PENDING on the base
    _write(work, L.RULINGS_REL, _open_go(_rulings(work)))
    _commit(work, "open GO-ID-2A", push=None)
    _refused(10, L.check_go, "b", work)                                    # opened locally only
    _sh(work, "push", "-q", "origin", "HEAD:refs/heads/b")
    L.check_go("b", work)
    L.check_code(launch, work, loaded=L.CODE_FILES)                        # the GO-open commit: no exit 5
    _write(work, L.RULINGS_REL, _rulings(work).replace("GO-ID-INTERIM-PENDING:", "GO-ID-INTERIM:")
           + "\nQUARANTINE: rbt-129-stage2a-c05-p080-U-G-129004-M\n")
    _write(work, "runs/RBT-129/continuations/QUARANTINE.md",
           open(os.path.join(work, "runs/RBT-129/continuations/QUARANTINE.md")).read() + "\nQUARANTINE: rbt-129-rb-x\n")
    _write(work, "runs/RBT-129/stage2-plan/STAGE2-PLAN.md", "edited\n")
    _commit(work, "later locks, a quarantine and a plan edit")
    L.check_code(launch, work, loaded=L.CODE_FILES)
    L.check_go("b", work)
    assert {"rbt-129-stage2a-c05-p080-U-G-129004-M", "rbt-129-rb-x"} <= set(L.base_quarantined_labels("b", work))
    _sh(work, "reset", "-q", "--hard", "HEAD~2")                           # a lane at the launch commit, base moved on
    L.check_code(launch, work, loaded=L.CODE_FILES)
    L.check_go("b", work)                                                  # the GO and quarantines come from the base
    assert "rbt-129-rb-x" in L.base_quarantined_labels("b", work)
    _sh(work, "reset", "-q", "--hard", "origin/b")
    for rel in L.CODE_FILES:                                               # any change to executed code: exit 5
        _write(work, rel, open(os.path.join(work, rel)).read() + "\n# edited\n")
        _refused(5, L.check_code, launch, work, loaded=L.CODE_FILES)       # uncommitted
        _commit(work, f"edit {rel}", push=None)
        _refused(5, L.check_code, launch, work, loaded=L.CODE_FILES)       # committed
        _sh(work, "reset", "-q", "--hard", "HEAD~1")
    _refused(5, L.check_code, launch, work, loaded=L.CODE_FILES + ("runs/RBT-129/other/x.py",))   # unpinned code
    _refused(5, L.check_code, {k: v for k, v in launch.items() if "stage1" not in k}, work, loaded=L.CODE_FILES)


def test_fc2_the_go_must_follow_the_2b2a_ruling_in_a_strict_descendant(scratch):
    """MINOR 5: one commit that rules 2B2A and opens GO-ID-2A is refused, and stays refused after the GO is withdrawn
    and re-opened (the #533 fix-check's residual: every opener, the first included, is checked)."""
    work = scratch
    _write(work, L.RULINGS_REL, _open_go(_rulings(work)).replace("2B2A: COMMITTED", "2B2A: DECLINED"))
    _commit(work, "2B2A and the GO together")
    _refused(10, L.check_go, "b", work)
    _write(work, L.RULINGS_REL, _rulings(work).replace("GO-ID-2A: RBT129-S2-2A-GO-1", "GO-ID-2A-PENDING: RBT129-S2-2A-GO-1"))
    _commit(work, "GO withdrawn")
    _write(work, L.RULINGS_REL, _open_go(_rulings(work)))
    _commit(work, "GO reopened")
    _refused(10, L.check_go, "b", work)                                     # the first opener still fails


def test_fc2_a_2b2a_ruled_first_passes_and_a_flip_after_the_go_is_refused(scratch):
    """The #533 fix-check's residual: GO opened, 2B2A then flipped, the GO closed and re-opened (the last opener's
    parent rules the flipped value): refused, since 2B2A changed after the first opener."""
    work = scratch
    _write(work, L.RULINGS_REL, _rulings(work).replace("2B2A: COMMITTED", "2B2A: DECLINED"))
    _commit(work, "2B2A ruled in its own commit")
    _write(work, L.RULINGS_REL, _open_go(_rulings(work)))
    _commit(work, "GO opened after it")
    L.check_go("b", work)
    _write(work, L.RULINGS_REL, _rulings(work).replace("2B2A: DECLINED", "2B2A: COMMITTED"))
    _commit(work, "2B2A flipped after the GO")
    _refused(10, L.check_go, "b", work)
    _write(work, L.RULINGS_REL, _rulings(work).replace("GO-ID-2A: RBT129-S2-2A-GO-1", "GO-ID-2A-PENDING: RBT129-S2-2A-GO-1"))
    _commit(work, "GO closed")
    _write(work, L.RULINGS_REL, _open_go(_rulings(work)))
    _commit(work, "GO reopened")
    _refused(10, L.check_go, "b", work)


def test_a_shallow_clone_refuses_with_the_deepening_fetch(scratch, tmp_path, capsys):
    work = scratch
    for k in range(3):
        _write(work, "runs/RBT-129/stage2-plan/STAGE2-PLAN.md", f"edit {k}\n")
        _commit(work, f"edit {k}")
    _write(work, L.RULINGS_REL, _open_go(_rulings(work)))
    _commit(work, "open")
    shallow = str(tmp_path / "shallow")
    _sh(str(tmp_path), "clone", "-q", "--depth", "1", "--branch", "b", "file://" + str(tmp_path / "origin.git"), shallow)
    with pytest.raises(SystemExit) as e:
        L.check_go("b", shallow)
    assert e.value.code == 10 and "--shallow-since=2026-10-03" in capsys.readouterr().err


def test_the_lanes_modules_must_be_the_checkouts(tmp_path):
    """#533 fix-check: stages, blocks, mjbuild, epa_ecology and rabbitstew from anywhere else refuse (exit 5)."""
    import types
    real = {n: types.SimpleNamespace(__file__=os.path.join(L.ROOT, f)) for n, f in L.PINNED_MODULES.items()}
    real["rabbitstew.ecology"] = types.SimpleNamespace(__file__=os.path.join(L.ROOT, "rabbitstew", "ecology.py"))
    L.check_modules(real)
    for name in list(L.PINNED_MODULES) + ["rabbitstew.ecology"]:
        _refused(5, L.check_modules, {**real, name: types.SimpleNamespace(__file__=str(tmp_path / "elsewhere.py"))})


# --- FC-A: a ruled CRASHED or quarantined run leaves its lane runnable, re-emitted without it ------------------------

def _lane(built, k=3):
    _, _, _, units = built
    worlds = os.path.join(L.RUNS, "worlds")
    return [{kk: (stages.rel(v) if kk in stages.PATH_KEYS else v) for kk, v in {**j, "worlds": worlds}.items()}
            for u in stages.layout(units, 10)[k] for j in u["jobs"]]


def test_fc_a_a_lane_without_a_ruled_crashed_run_passes_and_nothing_else_may_go(built, scratch, tmp_path):
    """A ruled ``CRASHED:`` record of an M run lets its lane omit that M only; of an S run, the whole unit (S60, its
    comparison, ckpt60, S, M, N); a ``QUARANTINE:`` line likewise.  Dropping any other job is refused (exit 4)."""
    work = scratch
    units = lambda jobs: {j["name"].rsplit("/", 1)[0] for j in jobs}
    want = next(w for w in (_lane(built, k) for k in range(20))
                if len(units(w)) >= 3 and any(j["name"].endswith("/M") for j in w))
    m = next(j for j in want if j["name"].endswith("/M"))
    s = next(j for j in want if j["name"].endswith("/S") and j["seed"] != m["seed"])
    lab = lambda j: stages._label(stages.absolute(j["dir"]))
    _write(work, L.RULINGS_REL, _rulings(work) + f"\nCRASHED: {lab(m)}\n")
    _commit(work, "a ruled crash of an M run")
    path = str(tmp_path / "host1-lane1.jsonl")
    launch = {"hosts": "10"}
    without_m = [j for j in want if j["name"] != m["name"]]
    L.check_emission(path, launch, without_m, "origin/b", work, want=want)
    L.check_emission(path, launch, want, "origin/b", work, want=want)          # not yet re-emitted: still the lane
    other = next(j for j in want if j["name"].endswith("/N") or j["name"] != m["name"] and j["name"].endswith("/S"))
    _refused(4, L.check_emission, path, launch, [j for j in without_m if j["name"] != other["name"]], "origin/b", work, want=want)
    _refused(4, L.check_emission, path, launch, [j for j in want if j["name"] != other["name"]], "origin/b", work, want=want)
    _write(work, L.RULINGS_REL, _rulings(work) + f"\nCRASHED: {lab(s)}\n")
    _commit(work, "a ruled crash of an S run")
    unit = s["name"].rsplit("/", 1)[0] + "/"
    gone = L.droppable(want, *L.ruled_exclusions("origin/b", work))
    assert gone == {m["name"]} | {j["name"] for j in want if j["name"].startswith(unit)}
    L.check_emission(path, launch, [j for j in want if j["name"] not in gone], "origin/b", work, want=want)
    _refused(4, L.check_emission, path, launch, without_m, "origin/b", work, want=want)   # must drop both now
    q = next(j for j in want if j["name"].endswith("/S60") and not j["name"].startswith(unit)
             and not j["name"].startswith(m["name"].rsplit("/", 1)[0] + "/"))
    qunit = q["name"].rsplit("/", 1)[0] + "/"
    _write(work, "runs/RBT-129/continuations/QUARANTINE.md",
           open(os.path.join(work, "runs/RBT-129/continuations/QUARANTINE.md")).read() + f"\nQUARANTINE: {lab(q)}\n")
    _commit(work, "a quarantine")
    gone2 = L.droppable(want, *L.ruled_exclusions("origin/b", work))
    assert gone2 == gone | {j["name"] for j in want if j["name"].startswith(qunit)}
    L.check_emission(path, launch, [j for j in want if j["name"] not in gone2], "origin/b", work, want=want)
def test_a_failed_fetch_refuses_even_with_a_stale_go_open_tracking_ref(scratch, tmp_path):
    """MINOR 6: origin unreachable while the tracking ref still shows a GO the base has since withdrawn."""
    work = scratch
    _write(work, L.RULINGS_REL, _open_go(_rulings(work)))
    _commit(work, "open")
    L.check_go("b", work)
    _sh(work, "remote", "set-url", "origin", str(tmp_path / "gone.git"))
    _refused(10, L.check_go, "b", work)


def test_the_lane_file_must_be_its_slice_of_the_emission(built, tmp_path):
    """MINOR 7: run-lane rebuilds the emission and refuses a lane file that is not exactly its slice."""
    salts, launch0, gate, units = built
    lanes = stages.layout(units, 10)
    worlds = os.path.join(L.RUNS, "worlds")
    raw = [{k: (stages.rel(v) if k in stages.PATH_KEYS else v) for k, v in {**j, "worlds": worlds}.items()}
           for u in lanes[3] for j in u["jobs"]]
    launch = {"hosts": "10", "salts": launch0["salts"]}
    path = str(tmp_path / "host1-lane1.jsonl")
    L.check_emission(path, launch, raw)
    _refused(4, L.check_emission, str(tmp_path / "host1-lane0.jsonl"), launch, raw)        # another lane's slice
    _refused(4, L.check_emission, path, launch, raw[:-1])                                 # a job dropped
    _refused(4, L.check_emission, path, launch, [raw[1], raw[0]] + raw[2:])               # reordered
    _refused(4, L.check_emission, path, launch, [{**raw[0], "seasons": 61}] + raw[1:])    # a field edited
    _refused(4, L.check_emission, path, {"salts": launch0["salts"]}, raw)                  # no hosts line


def test_drop_re_emits_the_committed_lanes_without_a_ruled_crash(scratch, tmp_path):
    """FC-A's remedy end to end: ``drop`` rewrites only the lane holding the ruled CRASHED run, without it; every lane
    then passes ``check_emission``; launch.txt is untouched."""
    import shutil
    work = scratch
    lanes = str(tmp_path / "S2A")
    shutil.copytree(os.path.join(L.RUNS, "lanes", L.NAME), lanes)
    launch_before = open(os.path.join(lanes, "launch.txt")).read()
    raw = lambda f: [json.loads(x) for x in open(os.path.join(lanes, f)) if x.strip()]
    f0 = next(f for f in sorted(os.listdir(lanes)) if f.endswith(".jsonl") and any(j["name"].endswith("/M") for j in raw(f)))
    m = next(j for j in raw(f0) if j["name"].endswith("/M"))
    assert L.drop(lanes, "b", work) == []                                   # nothing ruled: nothing rewritten
    _write(work, L.RULINGS_REL, _rulings(work) + f"\nCRASHED: {stages._label(stages.absolute(m['dir']))}\n")
    _commit(work, "a ruled crash")
    assert L.drop(lanes, "b", work) == [os.path.join(lanes, f0)]
    assert m["name"] not in {j["name"] for j in raw(f0)}
    launch = stages.read_launch(os.path.join(lanes, "launch.txt"))
    for f in sorted(os.listdir(lanes)):
        if f.endswith(".jsonl"):
            L.check_emission(os.path.join(lanes, f), launch, raw(f), "origin/b", work)
    assert open(os.path.join(lanes, "launch.txt")).read() == launch_before


def test_an_incomplete_ruling_drops_like_a_crash_and_needs_its_ruling_id(built, scratch, tmp_path):
    """COORD-RULING-RB-HELP-1's kind: ``INCOMPLETE: <run label> <ruling id>`` lets the lane omit that run and what reads
    it, as CRASHED: does; a line without its ruling id refuses (exit 4)."""
    work = scratch
    want = _lane(built)
    s = next(j for j in want if j["name"].endswith("/S"))
    lab = stages._label(stages.absolute(s["dir"]))
    _write(work, L.RULINGS_REL, _rulings(work) + f"\nINCOMPLETE: {lab} RBT129-RB-HELP-1\n")
    _commit(work, "an incomplete run")
    q, c, inc = L.ruled_exclusions("origin/b", work)
    # the committed QUARANTINE.md carries the real RB-HELP-1 line too (an R-B label, so no S2A job matches it)
    assert inc[lab] == "RBT129-RB-HELP-1" and set(inc) - {lab} <= {"rbt-129-rb-c2-p010-HP-G-129014-S"} and not c
    unit = s["name"].rsplit("/", 1)[0] + "/"
    gone = L.droppable(want, q, c, inc)
    assert gone == {j["name"] for j in want if j["name"].startswith(unit)}
    L.check_emission(str(tmp_path / "host1-lane1.jsonl"), {"hosts": "10"}, [j for j in want if j["name"] not in gone],
                     "origin/b", work, want=want)
    _write(work, L.RULINGS_REL, _rulings(work) + f"\nINCOMPLETE: {lab}\n")
    _commit(work, "an incomplete line without its ruling")
    _refused(4, L.ruled_exclusions, "origin/b", work)


def _evil_merge(work, edit, name):
    """A merge commit whose resolution makes ``edit`` to RULINGS-CITED-S2.md (a side branch with an unrelated commit)."""
    _sh(work, "checkout", "-q", "-b", name)
    _write(work, f"runs/RBT-129/stage2-plan/{name}.md", name + "\n")
    _commit(work, f"{name}: unrelated", push=None)
    _sh(work, "checkout", "-q", "-")
    _sh(work, "merge", "-q", "--no-ff", "--no-commit", name)
    _write(work, L.RULINGS_REL, edit(_rulings(work)))
    _sh(work, "add", "-A")
    _sh(work, "commit", "-q", "-m", f"merge {name}")
    _sh(work, "push", "-q", "origin", "HEAD:refs/heads/b")


def test_fc2_a_flip_and_flip_back_inside_merges_is_refused(scratch):
    """#533 fix-check 2, NOTE 1: every first-parent state after the GO opens rules the same 2B2A."""
    work = scratch
    _write(work, L.RULINGS_REL, _open_go(_rulings(work)))
    _commit(work, "open")
    L.check_go("b", work)
    _evil_merge(work, lambda t: t.replace("2B2A: COMMITTED", "2B2A: DECLINED"), "side1")
    _evil_merge(work, lambda t: t.replace("2B2A: DECLINED", "2B2A: COMMITTED"), "side2")
    _refused(10, L.check_go, "b", work)


def test_a_go_opened_only_inside_a_merge_says_so(scratch, capsys):
    """#533 fix-check 2, NOTE 2: refused (exit 10) with the right reason, not the shallow-clone one."""
    work = scratch
    _evil_merge(work, _open_go, "side")
    with pytest.raises(SystemExit) as e:
        L.check_go("b", work)
    err = capsys.readouterr().err
    assert e.value.code == 10 and "opened only inside a merge commit" in err and "shallow" not in err
