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
    assert "DIFFER" in str(e.value)


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
        assert not any(t == o or o.startswith(t + "/") for o in L.OWN_TREES)
