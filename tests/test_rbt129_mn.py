"""RBT-129 launch condition L1 (founding-screen adversary; #495 ruling, open question 2): Stage 1's gated M/N emitter,
DESIGN 5.2 as amended by AMENDMENT-FOUNDING T5.

Nothing here runs a sweep arm: the census is written by hand (a few lineage rows), the gate is fed made-up validity,
and the forks and their S60 sources are tiny non-sweep worlds.  Each registered rule has a test that fails under its
obvious mutant (``runs/RBT-129/mn-emitter/mutants.py``): g0 from the wrong seeds or faunas, the slot-freeing rule
dropped, the salts not carried to M and N, M/N emitted where stage1-emit's screen gate refuses, and the census resume
taken at a salt other than 0."""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "runs", "RBT-129", "launch"))
import blocks  # noqa: E402
import stages  # noqa: E402

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC  # noqa: E402

from test_rbt129_launch import TINY, fair_check, repo_tmp, surface_clearance  # noqa: E402,F401


@pytest.fixture(autouse=True)
def _receipts_in_tmp(tmp_path, monkeypatch):
    """No test writes this machine's durable receipts (#510 adversary S-2)."""
    monkeypatch.setattr(stages, "DURABLE_DONE", str(tmp_path / "durable-done"))


H, D = HOLISTIC, CONVENTIONAL
TINY_ARGV = TINY + ["--fair", "--sweep-log"]


# --- census g0: T5's fixed definition, from the census runs ---------------------------------------------------------

def _census(root, pid, j, rows, price=0.03, hist=None):
    d = os.path.join(str(root), "stage0", pid, str(stages.seed(j)), "S")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "config.json"), "w") as f:
        json.dump({"sim": {"food": {"work_cost": price}}}, f)
    with open(os.path.join(d, "lineage.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(d, "history.json"), "w") as f:
        json.dump({"history": hist if hist is not None else [{"season": 59, "population": k, "alive": 10, "births": 1} for k in (H, D)]}, f)
    return d


def _row(kind, gen, food, work=0.0, death=None):
    r = {"population": kind, "generation": gen, "food": food, "work": work, "name": f"{kind}{gen}", "parents": []}
    if death:
        r["death"] = death
    return r


@pytest.fixture
def census_root(tmp_path, monkeypatch):
    """Census runs at one point for seeds 1-4: 1-3 are the census; seed 4 (the pilot's, never the census) and every
    row outside 30-59, every cull and merge-null row, would move g0 if read."""
    monkeypatch.setenv("NO_DURABLE", "1")
    pid = "c1-p030-U-G"
    _census(tmp_path, pid, 1, [_row(H, 30, 1.0), _row(D, 59, 2.0, work=1000.0), _row(H, 29, 50.0), _row(D, 60, 50.0),
                               _row(H, 40, 50.0, death="cull"), _row(D, 40, 50.0, death="merge-null"), _row(D, 45, 0.5, death="starved")])
    _census(tmp_path, pid, 2, [_row(D, 35, 0.2)])
    _census(tmp_path, pid, 3, [_row(D, 31, 0.1), _row(D, 58, 0.3)])
    _census(tmp_path, pid, 4, [_row(H, 40, 99.0), _row(D, 40, 99.0)])
    return tmp_path, pid


def test_census_g0_is_the_readouts_pooled_over_129001_129003_and_both_faunas(census_root):
    root, pid = census_root
    # seed 1: 1.0 (H) + (2.0 - 0.03 * 1000 / 1000) (D) + 0.5 (the starved row counts); seed 2: 0.2; seed 3: 0.1, 0.3
    want = (1.0 + 1.97 + 0.5 + 0.2 + 0.1 + 0.3) / 6 + 0.35
    assert stages.census_g0(str(root), pid) == pytest.approx(want)
    assert stages.G0_SEEDS == (1, 2, 3) and set(stages.G0_FAUNAS) == {H, D}
    assert (stages.G0_WINDOW, stages.G0_OFFSET) == ((30, 59), 0.35)


def test_census_g0_is_none_where_no_member_season_exists(tmp_path, monkeypatch):
    monkeypatch.setenv("NO_DURABLE", "1")
    for j in (1, 2, 3):
        _census(tmp_path, "c2-p080-PW-G", j, [_row(H, 10, 1.0)])
    assert stages.census_g0(str(tmp_path), "c2-p080-PW-G") is None


def test_census_g0_refuses_a_missing_census_run(tmp_path, monkeypatch):
    monkeypatch.setenv("NO_DURABLE", "1")
    _census(tmp_path, "c1-p030-U-G", 1, [_row(H, 30, 1.0)])
    with pytest.raises(SystemExit) as e:
        stages.census_g0(str(tmp_path), "c1-p030-U-G")
    assert e.value.code == 8


def test_the_designed_founding_fail_is_c2_on_the_census_seeds(tmp_path, monkeypatch):
    """C2: extinct at 59 before refill on >= 2 of the 3 census seeds; the holistic census layer is not used (T5)."""
    monkeypatch.setenv("NO_DURABLE", "1")
    dead = lambda k: [{"season": 59, "population": k, "alive": 3, "births": 3}]  # alive only by refill: extinct
    for j, h in ((1, dead(D)), (2, dead(D) + dead(H)), (3, [{"season": 59, "population": D, "alive": 5, "births": 0}])):
        _census(tmp_path, "p", j, [], hist=h)
    assert stages.census_ff(str(tmp_path), "p") is True
    _census(tmp_path, "p", 2, [], hist=[{"season": 59, "population": D, "alive": 4, "births": 1}])
    assert stages.census_ff(str(tmp_path), "p") is False
    assert stages.census_ff(str(tmp_path), "p", H) is True  # no H row at 59 on 1 and 3: the holistic layer is FF


def test_the_committed_readout_gives_t5s_counts():
    """T5 cites the readout's counts: census g0 <= 0.8 at 46 points, <= 1.0 at 63, not computable at 11; designed
    FOUNDING-FAIL at 34 of 150."""
    g0, ff = stages.committed_census()
    assert len(g0) == 150 and set(g0) == set(blocks.all_ids())
    vals = [v for v in g0.values() if v is not None]
    assert (sum(v <= 0.8 for v in vals), sum(v <= 1.0 for v in vals), sum(v is None for v in g0.values())) == (46, 63, 11)
    assert len(ff) == 34 and "c1-p030-PW-L" in ff and "c1-p080-U-G" in ff
    assert g0["c0-p080-PW-G"] == 0.329 and g0["c1-p080-PW-G"] is None


def test_gate_rank_refuses_a_g0_the_committed_readout_does_not_give(census_root, monkeypatch):
    root, pid = census_root
    g = stages.census_g0(str(root), pid)
    monkeypatch.setattr(stages, "committed_census", lambda path=None: ({pid: round(g, 3)}, set()))
    [r] = stages.gate_rank(str(root), [pid])
    assert r["g0"] == g
    monkeypatch.setattr(stages, "committed_census", lambda path=None: ({pid: round(g, 3) + 0.001}, set()))
    with pytest.raises(SystemExit) as e:
        stages.gate_rank(str(root), [pid])
    assert e.value.code == 8
    monkeypatch.setattr(stages, "committed_census", lambda path=None: ({pid: round(g, 3)}, {pid}))
    with pytest.raises(SystemExit):
        stages.gate_rank(str(root), [pid])


def test_gate_rank_orders_by_g0_and_sets_eligibility(monkeypatch):
    g = {"a": 0.9, "b": 0.5, "c": None, "d": 0.81, "e": 1.01, "c1-p030-PW-G": 0.434, "f": 0.3}
    monkeypatch.setattr(stages, "census_g0", lambda root, pid: g[pid])
    monkeypatch.setattr(stages, "census_ff", lambda root, pid: pid == "f")
    rank = stages.gate_rank("x", list(g), check_readout=False)
    assert [r["point"] for r in rank] == ["f", "c1-p030-PW-G", "b", "d", "a", "e", "c"]
    ok = {r["point"]: (r["m_ok"], r["n_ok"]) for r in rank}
    assert ok == {"f": (False, False), "c1-p030-PW-G": (False, False), "b": (True, True), "d": (True, False),
                  "a": (True, False), "e": (False, False), "c": (False, False)}
    assert "c1-p030-PW-G" in blocks.ANCHORS


# --- the gate: the seed rule and the slot-freeing rule ----------------------------------------------------------------

def _rank(g0s):
    return [{"point": f"p{i:02d}", "g0": g, "designed_ff": False, "anchor": False, "m_ok": g <= 1.0, "n_ok": g <= 0.8}
            for i, g in enumerate(g0s)]


def test_m_takes_the_twelve_lowest_and_n_the_four_lowest_under_0_8():
    rank = _rank([0.06 * i for i in range(1, 17)])  # 16 eligible for M, 13 of them for N
    valid = {r["point"]: {j: True for j in range(1, 9)} for r in rank}
    gate = stages.mn_gate(rank, valid)
    assert [r["point"] for r in gate if r["m"]] == [f"p{i:02d}" for i in range(12)]
    assert "M slots full" in gate[12]["why"] and "N slots full" in gate[4]["why"]
    assert [r["point"] for r in gate if r["n"]] == ["p00", "p01", "p02", "p03"]
    assert all(r["m"] == list(range(1, 9)) for r in gate if r["m"])


def test_a_point_where_m_runs_on_no_seed_frees_its_slot():
    """T5, DATA-INFORMED: the slot passes to the next point in the ranking; for M and, on the same seeds, for N."""
    rank = _rank([0.1 + 0.01 * i for i in range(14)])
    valid = {r["point"]: {j: j % 2 == 1 for j in range(1, 9)} for r in rank}
    valid["p00"] = {j: False for j in range(1, 9)}
    valid["p02"] = {j: False for j in range(1, 9)}
    gate = {r["point"]: r for r in stages.mn_gate(rank, valid)}
    assert gate["p00"]["m"] == [] and "slot freed" in gate["p00"]["why"]
    assert [p for p, r in sorted(gate.items()) if r["m"]] == ["p01"] + [f"p{i:02d}" for i in range(3, 14)]
    assert [p for p, r in sorted(gate.items()) if r["n"]] == ["p01", "p03", "p04", "p05"]
    assert gate["p13"]["m"] == [1, 3, 5, 7] and gate["p03"]["n"] == [1, 3, 5, 7]  # only the valid seeds


def test_n_is_never_run_where_m_is_not_or_above_0_8():
    rank = _rank([0.9, 0.85, 0.5])
    rank[2]["designed_ff"], rank[2]["m_ok"], rank[2]["n_ok"] = True, False, False
    gate = stages.mn_gate(rank, {r["point"]: {j: True for j in range(1, 9)} for r in rank})
    assert not any(r["n"] for r in gate)
    assert [r["why"] for r in gate][2] == "designed FOUNDING-FAIL in the census"


def test_the_gate_never_admits_an_anchor_or_an_ineligible_point():
    rank = _rank([0.2, 0.3, 1.2])
    rank[0]["anchor"], rank[0]["m_ok"], rank[0]["n_ok"] = True, False, False
    gate = stages.mn_gate(rank, {"p01": {j: True for j in range(1, 9)}})
    assert [bool(r["m"]) for r in gate] == [False, True, False]
    assert "anchor" in gate[0]["why"] and gate[2]["why"] == "census g0 > 1.0"


def test_mn_plan_reads_s60_only_at_m_eligible_points_and_waits_for_all_of_them(monkeypatch):
    rank = _rank([0.5, 1.5, 0.7])
    reads = []
    monkeypatch.setattr(stages, "mn_gate_inputs", lambda root: ({j: (0, 0) for j in range(1, 17)}, {r["point"]: [] for r in rank}, {}))
    monkeypatch.setattr(stages, "gate_rank", lambda root: rank)
    monkeypatch.setattr(stages, "s60_state", lambda root, pid, j, salts, argv: reads.append(pid) or True)
    gate, _, _ = stages.mn_plan("x")
    assert set(reads) == {"p00", "p02"} and len(reads) == 16
    monkeypatch.setattr(stages, "s60_state", lambda root, pid, j, salts, argv: None if (pid, j) == ("p02", 8) else True)
    with pytest.raises(SystemExit) as e:
        stages.mn_plan("x")
    assert e.value.code == 8


# --- the forks: from Stage 1's ckpt60, at the screened salts -------------------------------------------------------

def _salts(**over):
    s = {j: (0, 0) for j in range(1, 17)}
    s.update({int(k[1:]): v for k, v in over.items()})
    return s


def test_mn_units_fork_stage1s_ckpt60_with_each_seeds_salts(tmp_path):
    root = str(tmp_path)
    salts = _salts(j2=(1, 0), j3=(2, 0), j7=(1, 0))
    gate = [{"point": "c1-p010-PW-L", "m": [1, 2, 3, 7], "n": [1, 2, 3, 7]}, {"point": "c1-p080-HP-G", "m": [4], "n": []}]
    jobs = [j for u in stages.mn_units(root, gate, salts) for j in u["jobs"]]
    assert len(jobs) == 9 and all(j["job"] == "fork" and j["seasons"] == 300 and j["cost"] == 240 for j in jobs)
    for j in jobs:
        k = j["seed"] - 129000
        assert j["salts"] == list(salts[k])
        assert j["src"] == os.path.join(root, "stage1", j["name"].split("/")[1], str(j["seed"]), "ckpt60")  # never stage0
        assert j["dir"] == os.path.join(os.path.dirname(j["src"]), j["name"].split("/")[-1])
        assert j["set"]["merge_after"] == 60 and j["set"]["pooled_capacity"] == 120
        if j["name"].endswith("/N"):
            assert j["set"]["merge_null"] == ("holistic" if k % 2 else "conventional")
        else:
            assert "merge_null" not in j["set"]
    assert sum(j["name"].endswith("/N") for j in jobs) == 4


def test_a_lane_refuses_an_m_or_n_fork_off_its_launch_records_salts():
    launch = {"salts": "129001:0/0 129002:1/0"}
    ok = {"job": "fork", "name": "1/x/129002/M", "seed": 129002, "salts": [1, 0]}
    stages.check_lane_salts([ok], launch)
    for bad in ({**ok, "salts": [0, 0]}, {k: v for k, v in ok.items() if k != "salts"}, {**ok, "seed": 129001, "salts": [1, 0]}):
        with pytest.raises(SystemExit):
            stages.check_lane_salts([bad], launch)


@pytest.fixture
def tiny(tmp_path, monkeypatch):
    monkeypatch.setenv("NO_DURABLE", "1")
    monkeypatch.setenv("WORKERS", "1")
    worlds = tmp_path / "worlds"
    worlds.mkdir()
    (worlds / "tiny.json").write_text(json.dumps({"id": "tiny", "argv": TINY_ARGV, "fair": ["--fair"]}))
    monkeypatch.setattr(stages, "SCREEN_SEASON", 2)
    monkeypatch.setattr(stages, "MERGE", 3)
    return {"worlds": str(worlds), "point": "tiny", "seasons": 3}


def _s60(tiny, root, j, s, t, census=False):
    """A Stage-1 chain's S60 and ckpt60 on the tiny world at (s, t): fresh, or (``census``) the adopted census run."""
    unit = os.path.join(str(root), "stage1", "tiny", str(stages.seed(j)))
    if census:
        src = os.path.join(str(root), "stage0", "tiny", str(stages.seed(j)), "S")
        stages.run_job({**tiny, "job": "fresh", "name": "0/tiny/S", "seed": stages.seed(j), "dir": src, "extra": []})
        stages.run_job({**tiny, "job": "adopt", "name": f"1/tiny/{stages.seed(j)}/S60", "seed": stages.seed(j), "src": src, "dir": f"{unit}/S"})
    else:
        stages.run_job({**tiny, "job": "fresh", "name": f"1/tiny/{stages.seed(j)}/S60", "seed": stages.seed(j), "dir": f"{unit}/S",
                        "extra": stages.salts_argv(s, t)})
    stages.run_job({"job": "snapshot", "name": f"1/tiny/{stages.seed(j)}/ckpt60", "src": f"{unit}/S", "dir": f"{unit}/ckpt60",
                    "seed": stages.seed(j), "cost": 0})
    return unit


def test_s60_state_reads_the_merge_and_checks_the_salts(tmp_path, tiny):
    unit = _s60(tiny, tmp_path, 5, 2, 0)
    v = stages.s60_state(str(tmp_path), "tiny", 5, (2, 0), TINY_ARGV)
    assert v is stages.valid_at_merge(os.path.join(unit, "ckpt60")) and isinstance(v, bool)
    for wrong in ((0, 0), (2, 1), (1, 0)):
        with pytest.raises(SystemExit) as e:
            stages.s60_state(str(tmp_path), "tiny", 5, wrong, TINY_ARGV)
        assert e.value.code == 8
    assert stages.s60_state(str(tmp_path), "tiny", 6, (0, 0), TINY_ARGV) is None  # not run yet: the gate waits


def test_the_census_resume_is_accepted_only_at_salts_0_0(tmp_path, tiny):
    """F7: 129001's S60 is the census's only at (0, 0).  A ckpt60 adopted from the census where the screen says a salt
    is not 0 is refused, never forked."""
    _s60(tiny, tmp_path, 1, 0, 0, census=True)
    assert isinstance(stages.s60_state(str(tmp_path), "tiny", 1, (0, 0), TINY_ARGV), bool)
    for salts in ((1, 0), (0, 1)):
        with pytest.raises(SystemExit) as e:
            stages.s60_state(str(tmp_path), "tiny", 1, salts, TINY_ARGV)
        assert e.value.code == 8


def test_s60_state_refuses_a_ksalt_that_is_not_pass(tmp_path, tiny):
    unit = _s60(tiny, tmp_path, 2, 1, 0)
    with pytest.raises(SystemExit):  # K-SALT expected (census seed, s >= 1, t = 0) and missing
        stages.s60_state(str(tmp_path), "tiny", 2, (1, 0), TINY_ARGV)
    with open(os.path.join(unit, stages.KSALT_FILE), "w") as f:
        f.write("KSALT VOID: ...\n")
    with pytest.raises(SystemExit):
        stages.s60_state(str(tmp_path), "tiny", 2, (1, 0), TINY_ARGV)
    with open(os.path.join(unit, stages.KSALT_FILE), "w") as f:
        f.write("KSALT PASS: ...\n")
    assert isinstance(stages.s60_state(str(tmp_path), "tiny", 2, (1, 0), TINY_ARGV), bool)


def test_an_extinct_unit_is_not_valid_at_the_merge(tmp_path, tiny):
    unit = os.path.join(str(tmp_path), "stage1", "tiny", "129004")
    os.makedirs(unit)
    with open(os.path.join(unit, stages.EXTINCT), "w") as f:
        f.write("EXTINCT pre-merge at season 12: ...\n")
    assert stages.s60_state(str(tmp_path), "tiny", 4, (0, 0), TINY_ARGV) is False


def test_valid_at_merge_needs_both_faunas_alive_at_59(tmp_path, monkeypatch):
    monkeypatch.setattr(stages, "SCREEN_SEASON", 59)
    for rows, want in (([(H, 3), (D, 5)], True), ([(H, 0), (D, 5)], False), ([(D, 5)], False), ([(H, 2)], False)):
        (tmp_path / "history.json").write_text(json.dumps({"history": [{"season": 59, "population": k, "alive": a, "births": 0}
                                                                       for k, a in rows]}))
        assert stages.valid_at_merge(str(tmp_path)) is want


def test_the_m_and_n_forks_carry_the_salts_and_refuse_a_source_at_other_salts(tmp_path, tiny):
    unit = _s60(tiny, tmp_path, 3, 2, 0)
    gate = [{"point": "tiny", "m": [3], "n": [3]}]
    for job in stages.mn_units(str(tmp_path), gate, _salts(j3=(2, 0)))[0]["jobs"]:
        stages.run_job({**job, "seasons": 5})
        cfg = json.load(open(os.path.join(job["dir"], "config.json")))
        assert (cfg["holistic_stream_salt"], cfg.get("designed_stream_salt", 0)) == (2, 0)
        assert cfg["ecology"]["merge_after"] == stages.MERGE and cfg["ecology"]["pooled_capacity"] == 120
    bad = stages.mn_units(str(tmp_path), [{"point": "tiny", "m": [3], "n": []}], _salts(j3=(1, 0)))[0]["jobs"][0]
    with pytest.raises(SystemExit, match="salts"):
        stages.run_job({**bad, "dir": os.path.join(unit, "M2"), "name": "1/tiny/129003/M2", "seasons": 5})


# --- the emitter: refused wherever stage1-emit's gate would refuse ---------------------------------------------------

def test_mn_emit_refuses_without_the_screen_gate(repo_tmp, fair_check, monkeypatch):
    monkeypatch.setenv("NO_DURABLE", "1")
    with pytest.raises(SystemExit) as e:
        stages.main(["mn-emit", "--fair=--fair", "--root", str(repo_tmp)])
    assert e.value.code == 8
    assert not (repo_tmp / "lanes" / stages.MN_LANES).exists()


def test_mn_emit_calls_the_same_screen_gate_as_stage1_emit(repo_tmp, fair_check, monkeypatch):
    calls = []

    def refuse(root):
        calls.append(root)
        stages._refuse("the stop rule fired", 8)
    monkeypatch.setattr(stages, "screen_gate", refuse)
    for cmd in ("stage1-emit", "mn-emit"):
        with pytest.raises(SystemExit) as e:
            stages.main([cmd, "--fair=--fair", "--root", str(repo_tmp)])
        assert e.value.code == 8
    assert len(calls) == 2
    assert not (repo_tmp / "lanes").exists()


def test_mn_emit_refuses_a_stage1_launch_record_at_other_salts(repo_tmp, fair_check, monkeypatch):
    monkeypatch.setattr(stages, "screen_gate", lambda root: _salts(j2=(1, 0)))
    lanes = repo_tmp / "lanes" / "1"
    lanes.mkdir(parents=True)
    pairs = lambda s: " ".join(f"{stages.seed(j)}:{a}/{b}" for j, (a, b) in sorted(s.items()))
    (lanes / "launch.txt").write_text(f"fair --fair\neat {' '.join(blocks.EAT_RULED)}\nsalts {pairs(_salts())}\n")
    with pytest.raises(SystemExit) as e:
        stages.mn_gate_inputs(str(repo_tmp))
    assert e.value.code == 8
    (lanes / "launch.txt").write_text(f"fair --fair\neat {' '.join(blocks.EAT_RULED)}\nsalts {pairs(_salts(j2=(1, 0)))}\n")
    salts, argv, _ = stages.mn_gate_inputs(str(repo_tmp))
    assert salts[2] == (1, 0) and argv["c1-p010-PW-L"] == blocks.world_argv("c1-p010-PW-L", fair=["--fair"], eat=list(blocks.EAT_RULED))


def test_mn_emit_writes_the_gated_lanes_and_the_table(repo_tmp, fair_check, surface_clearance, monkeypatch):
    salts = _salts(j2=(1, 0))
    rank = _rank([0.3, 0.6, 0.9])
    rank[0]["point"], rank[1]["point"], rank[2]["point"] = "c1-p010-PW-L", "c1-p080-HP-L", "c1-p080-HP-G"
    valid = {"c1-p010-PW-L": {j: j != 5 for j in range(1, 9)}, "c1-p080-HP-L": {j: False for j in range(1, 9)},
             "c1-p080-HP-G": {j: j <= 2 for j in range(1, 9)}}
    launch = {"fair": "--fair", "eat": " ".join(blocks.EAT_RULED)}
    monkeypatch.setattr(stages, "mn_plan", lambda root: (stages.mn_gate(rank, valid), salts, launch))
    stages.main(["mn-emit", "--fair=--fair", "--root", str(repo_tmp), "--hosts", "1"])
    d = repo_tmp / "lanes" / stages.MN_LANES
    jobs = [json.loads(l) for p in d.glob("host*-lane*.jsonl") for l in p.read_text().splitlines()]
    assert sorted(j["name"] for j in jobs if j["name"].endswith("/N")) == sorted(
        f"1/c1-p010-PW-L/{stages.seed(j)}/N" for j in range(1, 9) if j != 5)
    assert sorted(j["name"] for j in jobs if j["name"].endswith("/M")) == sorted(
        [f"1/c1-p010-PW-L/{stages.seed(j)}/M" for j in range(1, 9) if j != 5] + [f"1/c1-p080-HP-G/{stages.seed(j)}/M" for j in (1, 2)])
    launch_txt = stages.read_launch(str(d / "launch.txt"))
    stages.check_lane_salts(jobs, launch_txt)  # every fork at its seed's screened salts
    stages.check_lane_forks([{**j, "src": stages.absolute(j["src"])} for j in jobs], launch_txt)  # and only the admitted ones
    assert sorted(launch_txt["forks"].split()) == sorted(j["name"][2:] for j in jobs)
    assert launch_txt["salts"].split()[1] == "129002:1/0"
    table = (d / "gate_table.txt").read_text()
    assert "slot freed" in table and "171 / 320" in table and "M + N = " in table
    assert all(not os.path.isabs(j["src"]) for j in jobs)
    with pytest.raises(SystemExit):  # Stage 1's flags only
        stages.main(["mn-emit", "--fair=--fair", "--eat=--eat-from root", "--root", str(repo_tmp)])


def test_the_gate_table_prints_every_point_and_the_disclosed_figure():
    rank = _rank([0.3, 0.9, 1.3])
    gate = stages.mn_gate(rank, {r["point"]: {j: True for j in range(1, 9)} for r in rank})
    text = stages.gate_report(gate)
    for r in rank:
        assert r["point"] in text
    arms = 8 + 8 + 8  # p00 M + N, p01 M
    assert f"M + N = {arms * 240 * 23.35 / 3600:.1f} / {arms * 240 * 43.72 / 3600:.1f} core-h" in text
    assert "about 171 / 320 core-h" in text
    for words in ("DATA-INFORMED (ruling on #500, item 1)", "not rescaled by the pilot's r = 1.53", "10 M-eligible and 7 N-eligible",
                  "reveal each M-eligible point's PARTIAL status", "cost basis", "2.34x"):
        assert words in text
    assert "M seeds" not in stages.gate_report(rank, rank_only=True)  # pre-data: no S60 column


# --- the #500 ruling's fixes -----------------------------------------------------------------------------------------

def test_census_g0_reads_the_two_faunas_only(census_root):
    """#500 ruling, SHOULD 5: a stray population in a census lineage does not enter g0."""
    root, pid = census_root
    before = stages.census_g0(str(root), pid)
    d = os.path.join(str(root), "stage0", pid, "129002", "S", "lineage.jsonl")
    with open(d, "a") as f:
        f.write(json.dumps(_row("null_b", 40, 99.0)) + "\n")
    assert stages.census_g0(str(root), pid) == before


def test_ksalt_is_required_at_129001_at_salts_1_0(tmp_path, tiny):
    """#500 ruling, MUST 3: F7 runs K-SALT wherever a census seed runs with s >= 1 and t = 0, 129001 included."""
    unit = _s60(tiny, tmp_path, 1, 1, 0)
    with pytest.raises(SystemExit) as e:
        stages.s60_state(str(tmp_path), "tiny", 1, (1, 0), TINY_ARGV)
    assert e.value.code == 8
    with open(os.path.join(unit, stages.KSALT_FILE), "w") as f:
        f.write("KSALT PASS: ...\n")
    assert isinstance(stages.s60_state(str(tmp_path), "tiny", 1, (1, 0), TINY_ARGV), bool)


@pytest.mark.parametrize("j", [1, 2, 3])
def test_no_ksalt_is_required_where_t_is_not_0(tmp_path, tiny, j):
    """#500 ruling, MUST 3: no K-SALT runs where t >= 1, so none may be required there (else mn-emit never emits)."""
    _s60(tiny, tmp_path, j, 1, 1)
    assert isinstance(stages.s60_state(str(tmp_path), "tiny", j, (1, 1), TINY_ARGV), bool)


def test_a_ksalt_void_on_an_extinct_unit_is_refused(tmp_path, tiny):
    """#500 ruling, SHOULD 2: K-SALT is read before the extinct short-circuit."""
    unit = os.path.join(str(tmp_path), "stage1", "tiny", "129002")
    os.makedirs(unit)
    with open(os.path.join(unit, stages.EXTINCT), "w") as f:
        f.write("EXTINCT pre-merge at season 12: ...\n")
    with open(os.path.join(unit, stages.KSALT_FILE), "w") as f:
        f.write("KSALT VOID: ...\n")
    with pytest.raises(SystemExit) as e:
        stages.s60_state(str(tmp_path), "tiny", 2, (1, 0), TINY_ARGV)
    assert e.value.code == 8
    with open(os.path.join(unit, stages.KSALT_FILE), "w") as f:
        f.write("KSALT PASS: ...\n")
    assert stages.s60_state(str(tmp_path), "tiny", 2, (1, 0), TINY_ARGV) is False


def test_a_lane_runs_only_the_admitted_forks(tmp_path):
    """#500 ruling, SHOULD 3: run-lane holds M/N forks to launch.txt's forks line, each with its arm's settings."""
    root = str(tmp_path)
    gate = [{"point": "c1-p010-PW-L", "m": [1, 2], "n": [1]}]
    jobs = [j for u in stages.mn_units(root, gate, _salts()) for j in u["jobs"]]
    launch = {"forks": " ".join(stages.mn_fork_names(gate))}
    assert sorted(launch["forks"].split()) == ["c1-p010-PW-L/129001/M", "c1-p010-PW-L/129001/N", "c1-p010-PW-L/129002/M"]
    stages.check_lane_forks(jobs, launch)
    stages.check_lane_forks(jobs + [{"job": "fresh", "name": "1/x/129001/S60", "seed": 129001}], {})  # no forks line: not checked
    m = jobs[0]
    d = os.path.join(root, "stage1", "c1-p010-PW-L", "129003")
    for bad in ({**m, "name": "1/c1-p010-PW-L/129003/M", "seed": 129003, "src": f"{d}/ckpt60", "dir": f"{d}/M"},  # hand-added seed
                {**m, "name": "1/c1-p080-HP-L/129001/M"},  # a point the gate did not admit
                {**m, "set": {**m["set"], "merge_null": "holistic"}},  # the M fork with N's settings
                {**jobs[1], "set": {**jobs[1]["set"], "merge_null": "conventional"}},  # N at the wrong null kind
                {**m, "src": os.path.join(root, "stage0", "c1-p010-PW-L", "129001", "S")},  # from the census, not ckpt60
                {**m, "job": "fresh"}):
        with pytest.raises(SystemExit) as e:
            stages.check_lane_forks([bad], launch)
        assert e.value.code == 4


def test_booked_and_before_refill_extinction_agree_in_the_ecology(tmp_path, tiny):
    """#500 ruling, OQ4: breeders are the season's survivors and a parent cannot die the season it breeds, so births > 0
    implies alive - births > 0, and "alive at 59" and "alive before refill at 59" are the same test of extinction."""
    rows = 0
    for j in (1, 2, 3):
        unit = _s60(tiny, tmp_path, j, 0, 0)
        hist = stages._history(os.path.join(unit, "ckpt60"))
        for e in hist:
            rows += 1
            assert (e["alive"] > 0) == (e["alive"] - e["births"] > 0)
        assert stages.valid_at_merge(os.path.join(unit, "ckpt60")) == all(stages.alive_before_refill(hist, k) > 0 for k in stages.FAUNAS)
    assert rows > 0


def test_run_lane_refuses_a_hand_added_fork_before_running_anything(repo_tmp, monkeypatch):
    """#500 ruling, SHOULD 3: the check is on run-lane's path, before any job runs."""
    monkeypatch.setattr(stages, "check_host", lambda launch: None)
    monkeypatch.setattr(stages, "check_lane_blocks", lambda jobs, launch: None)
    monkeypatch.setattr(stages, "run_job", lambda job: pytest.fail("a job ran"))
    gate = [{"point": "c1-p010-PW-L", "m": [1], "n": []}]
    lane = repo_tmp / "lanes" / stages.MN_LANES
    lane.mkdir(parents=True)
    (lane / "launch.txt").write_text(f"forks {' '.join(stages.mn_fork_names(gate))}\n")
    jobs = [j for u in stages.mn_units(str(repo_tmp), [{"point": "c1-p010-PW-L", "m": [1, 2], "n": []}], _salts()) for j in u["jobs"]]
    (lane / "host0-lane0.jsonl").write_text("".join(json.dumps({k: (stages.rel(v) if k in stages.PATH_KEYS else v) for k, v in j.items()}) + "\n"
                                                    for j in jobs))
    with pytest.raises(SystemExit) as e:
        stages.run_lane(str(lane / "host0-lane0.jsonl"))
    assert e.value.code == 4
