"""RBT-129c (AMENDMENT-FOUNDING F1-F8, DESIGN section 15): the designed stream salt on the ecology, and Stage F, the
founder screen at W118-b, with the salt-0 byte-compare, the fork source, the stop rule and Stage 1's lane emission.

Nothing here runs a sweep arm or the screen: the ecology runs are tiny non-sweep worlds, and the screen's rule is
tested with made-up alive counts.  Each rule has a test that fails under its obvious mutant (a criterion of >= 1, salts
out of order, a stop rule missing a clause, the census resume at a non-zero salt)."""
import json
import os
import shutil
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "runs", "RBT-129", "launch"))
import blocks  # noqa: E402
import stages  # noqa: E402

from rabbitstew.cli import build_parser, ecology_configs  # noqa: E402
from rabbitstew.ecology import Ecology  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC  # noqa: E402

from test_ecology_switches import _breeding_eco, _evo  # noqa: E402
from test_rbt129_launch import TINY, fair_check, repo_tmp, surface_clearance  # noqa: E402,F401

H, D = HOLISTIC, CONVENTIONAL


def _rows(out, kind=None):
    return [l for l in (out / "lineage.jsonl").read_text().splitlines() if kind is None or json.loads(l)["population"] == kind]


def _hist(out, kind=None):
    return [e for e in json.loads((out / "history.json").read_text())["history"] if kind is None or e["population"] == kind]


def _eco_run(out, eco, s=0, t=0):
    evo = _evo(11, 1.5)
    evo.holistic_stream_salt, evo.designed_stream_salt = s, t
    Ecology(evo, eco, out_dir=str(out), log=None).run()
    return out


# --- the designed salt on the ecology ------------------------------------------------------------------------------

def test_the_ecology_subcommand_takes_both_salts_and_writes_them_only_when_set():
    args = build_parser().parse_args(["ecology", "--seed", "5", "--holistic-stream-salt", "2", "--designed-stream-salt", "3"])
    evo, _ = ecology_configs(args)
    assert (evo.holistic_stream_salt, evo.designed_stream_salt) == (2, 3)
    d = evo.to_dict()
    assert d["holistic_stream_salt"] == 2 and d["designed_stream_salt"] == 3
    plain = ecology_configs(build_parser().parse_args(["ecology", "--seed", "5"]))[0].to_dict()
    zero = ecology_configs(build_parser().parse_args(["ecology", "--seed", "5", "--holistic-stream-salt", "0",
                                                      "--designed-stream-salt", "0"]))[0].to_dict()
    assert plain == zero and "designed_stream_salt" not in zero and "holistic_stream_salt" not in zero
    with pytest.raises(SystemExit):
        ecology_configs(build_parser().parse_args(["ecology", "--designed-stream-salt", "-1"]))


def test_a_designed_salt_moves_only_the_designed_fauna_of_an_ecology(tmp_path):
    a = _eco_run(tmp_path / "a", _breeding_eco(seasons=4))
    b = _eco_run(tmp_path / "b", _breeding_eco(seasons=4), t=1)
    assert _rows(a, H) == _rows(b, H) and _hist(a, H) == _hist(b, H)
    assert _rows(a, D) != _rows(b, D)
    c = _eco_run(tmp_path / "c", _breeding_eco(seasons=4), s=1)  # and the holistic salt, the designed fauna
    assert _rows(a, D) == _rows(c, D) and _rows(a, H) != _rows(c, H)


def test_both_salts_survive_the_season_fork_and_a_resume(tmp_path, monkeypatch):
    """T9: a run at (s, t) checkpointed and forked (stages.fork_config, as ckpt60) then resumed is the straight run."""
    straight = _eco_run(tmp_path / "straight", _breeding_eco(seasons=5), s=2, t=3)
    part = _eco_run(tmp_path / "part", _breeding_eco(seasons=3), s=2, t=3)
    stages.fork_config(str(part), str(tmp_path / "fork"), {})
    cfg = json.loads((tmp_path / "fork" / "config.json").read_text())
    assert (cfg["holistic_stream_salt"], cfg["designed_stream_salt"]) == (2, 3)
    Ecology.resume(str(tmp_path / "fork"), seasons=5, log=None).run()
    for name in ("lineage.jsonl", "history.json"):
        assert (straight / name).read_bytes() == (tmp_path / "fork" / name).read_bytes()


@pytest.mark.parametrize("kind", [H, D])
def test_salts_compose_with_only_fauna(tmp_path, kind):
    """F1: the fauna alone at its salt is its half of the two-fauna run at (s, t), byte for byte."""
    both = _eco_run(tmp_path / "both", _breeding_eco(seasons=4), s=2, t=3)
    alone = _eco_run(tmp_path / "alone", _breeding_eco(seasons=4, only_fauna=kind), s=2, t=3)
    assert _rows(both, kind) == _rows(alone) and _hist(both, kind) == _hist(alone)
    assert stages.half_compare(str(alone), str(both), kind, upto=3)[0] == "PASS"


@pytest.mark.parametrize("null", [H, D])
def test_salts_compose_with_merge_null(tmp_path, null):
    """The null arm at (s, t) is the merged arm at (s, t) until the merge (RBT-130's check, salted)."""
    kw = dict(seasons=6, merge_after=3, sweep_log=True, pooled_capacity=16, max_age=8)
    m = _eco_run(tmp_path / "M", _breeding_eco(**kw), s=1, t=2)
    n = _eco_run(tmp_path / "N", _breeding_eco(merge_null=null, **kw), s=1, t=2)
    before = lambda out: [r for r in _rows(out) if json.loads(r)["generation"] < 3]
    assert before(m) == before(n) and before(m)
    assert any(json.loads(r)["population"] == "null_b" for r in _rows(n))


# --- the screen's rule -------------------------------------------------------------------------------------------

def _fake(outcomes):
    """attempt(salt) from {salt: alive59}; records the order of the calls."""
    calls = []

    def attempt(salt):
        calls.append(salt)
        return outcomes.get(salt, 0), (59 if outcomes.get(salt, 0) else 12)
    return attempt, calls


def test_the_screen_keeps_the_first_salt_with_30_alive_and_stops():
    attempt, calls = _fake({2: 45, 3: 60})
    r = stages.screen(attempt)
    assert r["salt"] == 2 and not r["capped"] and calls == [0, 1, 2]
    assert [a["salt"] for a in r["tried"]] == [0, 1, 2] and r["tried"][-1] == {"salt": 2, "alive59": 45, "last": 59}


def test_the_criterion_is_30_not_1():
    """Mutant: >= 1.  One to 29 survivors do not found (F2); 30 does."""
    attempt, calls = _fake({0: 1, 1: 29, 2: 30})
    r = stages.screen(attempt)
    assert r["salt"] == 2 and calls == [0, 1, 2]
    assert stages.founds(30) and not stages.founds(29) and not stages.founds(1)
    assert stages.SCREEN_CRITERION == 30


def test_the_salts_are_tried_in_order_zero_to_twenty():
    """Mutant: any other order.  The rule calls 0, 1, ..., 20, and a record whose salts are out of order is refused."""
    assert stages.SCREEN_SALTS == tuple(range(21))
    attempt, calls = _fake({})
    stages.screen(attempt)
    assert calls == list(range(21))
    attempt, _ = _fake({1: 50, 0: 0})
    rec = {"seed": 129001, "fauna": H, **stages.screen(attempt)}
    stages.check_screen_record(rec)
    bad = json.loads(json.dumps(rec))
    bad["tried"] = bad["tried"][::-1]
    with pytest.raises(SystemExit):
        stages.check_screen_record(bad)
    skipped = {"seed": 129001, "fauna": H, "tried": [{"salt": 0, "alive59": 0, "last": 10}, {"salt": 2, "alive59": 50, "last": 59}],
               "salt": 2, "capped": False}
    with pytest.raises(SystemExit):
        stages.check_screen_record(skipped)


def test_a_fauna_failing_all_21_salts_keeps_salt_0_screen_capped():
    attempt, calls = _fake({s: 29 for s in range(21)})
    r = stages.screen(attempt)
    assert r == {"tried": r["tried"], "salt": 0, "capped": True} and len(r["tried"]) == 21 and calls == list(range(21))
    stages.check_screen_record({"seed": 129009, "fauna": D, **r})
    forged = {"seed": 129009, "fauna": D, **r, "salt": 20}  # a capped fauna keeps salt 0, never its last try
    with pytest.raises(SystemExit):
        stages.check_screen_record(forged)
    short = {"seed": 129009, "fauna": D, "tried": r["tried"][:5], "salt": 0, "capped": True}  # capped before the cap
    with pytest.raises(SystemExit):
        stages.check_screen_record(short)


@pytest.mark.parametrize("capped, fires", [
    ([], False), ([1], False), ([9], False), ([1, 9], False), ([9, 16], False),
    ([1, 2], True),          # the second clause alone (2 of 1-8): kills a stop rule missing it
    ([9, 10, 11], True),     # the first clause alone (3 of 16, none in 1-8): kills a stop rule missing it
    ([1, 9, 10], True), ([7, 8], True), ([8, 9, 16], True)])
def test_the_stop_rule_has_both_clauses(capped, fires):
    assert bool(stages.stop_rule(capped)) == fires


def test_a_seed_is_capped_if_either_fauna_is():
    rec = lambda c: {"capped": c}
    res = {(1, H): rec(False), (1, D): rec(True), (2, H): rec(True), (2, D): rec(True), (3, H): rec(False), (3, D): rec(False)}
    assert stages.capped_seeds(res) == [1, 2]
    assert stages.stop_rule(stages.capped_seeds(res))


def test_the_alive_count_is_before_refill_and_last_alive_likewise():
    hist = [{"season": 59, "population": H, "alive": 31, "births": 2}, {"season": 59, "population": D, "alive": 60, "births": 0},
            {"season": 58, "population": H, "alive": 3, "births": 3}]
    assert stages.alive_before_refill(hist, H) == 29 and not stages.founds(stages.alive_before_refill(hist, H))
    assert stages.alive_before_refill(hist, D) == 60
    assert stages.alive_before_refill(hist[1:2], H) == 0  # no row: extinct
    assert stages.last_alive(hist, H) == 59 and stages.last_alive(hist[2:], H) == -1


# --- Stage 1's lanes read the screen's salts ------------------------------------------------------------------------

def _salts(**over):
    s = {j: (0, 0) for j in range(1, 17)}
    s.update({int(k[1:]): v for k, v in over.items()})
    return s


def _by(units, j):
    return [u for u in units if u["seed"] == stages.seed(j)]


def test_stage1_resumes_the_census_only_for_129001_at_salts_0_0(tmp_path):
    units = stages.stage1_units(str(tmp_path), _salts(j2=(3, 0), j3=(4, 0), j4=(0, 1), j5=(2, 5)))
    assert len(units) == 36 * 8 and {u["seed"] for u in units} == {stages.seed(j) for j in range(1, 9)}
    assert len(stages.STAGE1_POINTS) == 36 == len(set(stages.STAGE1_POINTS))
    for u in _by(units, 1):
        first = u["jobs"][0]
        assert first["job"] == "adopt" and first["src"].endswith(os.path.join("stage0", first["point"], "129001", "S"))
    for j in range(2, 9):
        for u in _by(units, j):
            assert u["jobs"][0]["job"] == "fresh"
    first = {j: _by(units, j)[0]["jobs"][0] for j in range(1, 9)}
    assert first[2]["extra"] == ["--holistic-stream-salt", "3"] and first[4]["extra"] == ["--designed-stream-salt", "1"]
    assert first[5]["extra"] == ["--holistic-stream-salt", "2", "--designed-stream-salt", "5"] and first[6]["extra"] == []
    assert [j["job"] for j in _by(units, 2)[0]["jobs"]] == ["fresh", "ksalt", "snapshot", "resume"]
    assert [j["job"] for j in _by(units, 1)[0]["jobs"]] == ["adopt", "snapshot", "resume"]
    assert all(j["job"] != "ksalt" for u in _by(units, 4) + _by(units, 5) for j in u["jobs"])  # t != 0 or not a census seed
    assert all(u["jobs"][-1]["seasons"] == 300 for u in units)


@pytest.mark.parametrize("salts", [(1, 0), (0, 1), (2, 7)])
def test_stage1_runs_129001_fresh_when_either_salt_is_not_0(tmp_path, salts):
    """Mutant: the census resume used when a salt is not 0."""
    units = stages.stage1_units(str(tmp_path), _salts(j1=salts))
    for u in _by(units, 1):
        first = u["jobs"][0]
        assert first["job"] == "fresh" and first["extra"] == stages.salts_argv(*salts)
    ks = [j for u in _by(units, 1) for j in u["jobs"] if j["job"] == "ksalt"]
    assert bool(ks) == (salts[0] >= 1 and salts[1] == 0)


def test_the_fork_source_is_two_fauna_at_the_screened_salts(tmp_path):
    units = stages.fork_source_units(str(tmp_path), _salts(j3=(5, 0), j9=(0, 2)), 16)
    jobs = [u["jobs"][0] for u in units]
    assert len(jobs) == 16 and all(j["point"] == "c0-p030-U-L" and j["seasons"] == 60 for j in jobs)
    assert all("--only-fauna" not in j["extra"] for j in jobs)
    assert jobs[2]["extra"] == ["--holistic-stream-salt", "5"] and jobs[8]["extra"] == ["--designed-stream-salt", "2"]
    assert len(stages.fork_source_units(str(tmp_path), _salts())) == 8


def test_the_fork_source_has_ksalt_where_f7_says_the_runs_overlap(tmp_path):
    """#495 ruling MUST 1 (F7: "and 129007 and 129008 at W118-b"): at s >= 1, t = 0 the fork source's designed half is
    byte-compared with the seed's two-fauna run at W118-b: the census S (1-3), the pilot S (4), the A-stage S (5-8)."""
    root = str(tmp_path)
    salts = _salts(j2=(3, 0), j4=(2, 0), j6=(1, 1), j7=(1, 0), j8=(5, 0), j10=(1, 0))
    units = stages.fork_source_units(root, salts, 16)
    ks = {u["seed"]: j for u in units for j in u["jobs"] if j["job"] == "ksalt"}
    assert set(ks) == {129002, 129004, 129007, 129008}  # not t >= 1 (6), not s = 0 (1, 3, 5), no reference past 8 (10)
    for sd, want in ((129002, "stage0"), (129004, "stageP"), (129007, "stage0"), (129008, "stage0")):
        assert ks[sd]["ref"] == os.path.join(root, want, "c0-p030-U-L", str(sd), "S")
        assert ks[sd]["src"] == os.path.join(root, "stageF", "fork", "c0-p030-U-L", str(sd), "S")
    for u in units:  # after the fresh S it reads
        kinds = [j["job"] for j in u["jobs"]]
        assert kinds[0] == "fresh" and kinds in (["fresh"], ["fresh", "ksalt"])


def test_lane_extras_are_the_founding_flags_only():
    stages.check_extra(["--only-fauna", H, "--holistic-stream-salt", "3", "--designed-stream-salt", "0"])
    for bad in (["--merge-after", "3"], ["--only-fauna", "both"], ["--designed-stream-salt", "-1"], ["--seed"]):
        with pytest.raises(SystemExit):
            stages.check_extra(bad)


def test_a_lane_runs_only_its_launch_records_salts():
    launch = {"salts": "129001:0/0 129002:3/0"}
    ok = [{"job": "fresh", "name": "1/x/129002/S60", "seed": 129002, "extra": ["--holistic-stream-salt", "3"]},
          {"job": "fresh", "name": "1/x/129001/S60", "seed": 129001, "extra": []}]
    stages.check_lane_salts(ok, launch)
    stages.check_lane_salts([{**ok[0], "extra": []}], {})  # a lane without a salts line (the screen's) is not checked
    for bad in ({**ok[0], "extra": ["--holistic-stream-salt", "4"]}, {**ok[1], "extra": ["--designed-stream-salt", "1"]},
                {**ok[0], "seed": 129003}):
        with pytest.raises(SystemExit):
            stages.check_lane_salts([bad], launch)


def test_stage1_emit_refuses_without_the_screen(repo_tmp, fair_check, monkeypatch):
    monkeypatch.setenv("NO_DURABLE", "1")
    with pytest.raises(SystemExit) as e:
        stages.main(["stage1-emit", "--fair=--fair", "--root", str(repo_tmp)])
    assert e.value.code == 8


def test_the_screen_emits_32_screens_and_16_salt0_compares(repo_tmp, fair_check):
    stages.main(["screen-emit", "--fair=--fair", "--root", str(repo_tmp), "--hosts", "2"])
    jobs = [json.loads(l) for p in (repo_tmp / "lanes" / "F").glob("host*-lane*.jsonl") for l in p.read_text().splitlines()]
    screens = [j for j in jobs if j["job"] == "screen"]
    cmps = [j for j in jobs if j["job"] == "salt0cmp"]
    assert len(screens) == 32 and {(j["seed"], j["fauna"]) for j in screens} == {(stages.seed(j), k) for j in range(1, 17) for k in (H, D)}
    assert {j["point"] for j in screens} == {"c0-p030-U-L"} and all(j["seasons"] == 60 for j in screens)
    assert {(j["seed"], j["fauna"]) for j in cmps} == {(stages.seed(j), k) for j in range(1, 9) for k in (H, D)}
    ref = {j["seed"]: j["ref"] for j in cmps}
    for sd in (129001, 129002, 129003, 129005, 129006, 129007, 129008):  # census and A-stage S (SHOULD 2)
        assert ref[sd].endswith(f"stage0/c0-p030-U-L/{sd}/S")
    assert ref[129004].endswith("stageP/c0-p030-U-L/129004/S")
    assert all(not os.path.isabs(j["dir"]) for j in jobs)
    for p in (repo_tmp / "lanes" / "F").glob("host*-lane*.jsonl"):  # the compare follows its screen, in one lane
        names = [json.loads(l)["name"] for l in p.read_text().splitlines()]
        for i, n in enumerate(names):
            if n.endswith("salt0cmp"):
                assert n.replace("salt0cmp", "screen") in names[:i]
    block = json.loads((repo_tmp / "worlds" / "c0-p030-U-L.json").read_text())
    assert block["fair"] == ["--fair"] and "--sweep-log" in block["argv"]
    assert "fair --fair" in (repo_tmp / "lanes" / "F" / "launch.txt").read_text()


def test_emit_refuses_a_root_outside_the_repository_before_writing(tmp_path, fair_check):
    with pytest.raises(SystemExit):
        stages.emit_lanes("F", [], 1, str(tmp_path), ["--fair"], list(blocks.EAT_RULED))
    assert not (tmp_path / "lanes").exists()


# --- the jobs on a tiny world -------------------------------------------------------------------------------------

@pytest.fixture
def tiny(tmp_path, monkeypatch):
    monkeypatch.setenv("NO_DURABLE", "1")
    monkeypatch.setenv("WORKERS", "1")
    worlds = tmp_path / "worlds"
    worlds.mkdir()
    (worlds / "tiny.json").write_text(json.dumps({"id": "tiny", "argv": TINY + ["--fair", "--sweep-log"], "fair": ["--fair"]}))
    monkeypatch.setattr(stages, "SCREEN_SEASONS", 3)
    monkeypatch.setattr(stages, "SCREEN_SEASON", 2)
    return {"worlds": str(worlds), "point": "tiny", "seed": 7, "seasons": 3}


def _two_fauna(tiny, d, extra=()):
    stages.run_job({**tiny, "job": "fresh", "name": "ref/S", "dir": str(d), "extra": list(extra)})
    return d


def test_the_screen_job_runs_salts_in_order_and_keeps_the_first_pass(tmp_path, tiny, monkeypatch):
    """On a tiny world (capacity 4) a criterion of 1 stands in for 30; each attempt is a single-fauna run from 0."""
    monkeypatch.setattr(stages, "SCREEN_CRITERION", 1)
    monkeypatch.setattr(stages, "SCREEN_SALTS", (0, 1, 2))
    d = tmp_path / "F" / "conventional"
    stages.run_job({**tiny, "job": "screen", "name": "F/tiny/7/conventional/screen", "fauna": D, "dir": str(d)})
    rec = json.loads((d / stages.SCREEN_FILE).read_text())
    assert rec["tried"][0]["salt"] == 0 and rec["salt"] == rec["tried"][-1]["salt"]
    for a in rec["tried"]:
        cfg = json.loads((d / f"salt{a['salt']}" / "config.json").read_text())
        assert cfg["ecology"]["only_fauna"] == D and cfg.get("designed_stream_salt", 0) == a["salt"]
        assert "holistic_stream_salt" not in cfg
    if not rec["capped"]:
        assert not (d / f"salt{rec['salt'] + 1}").exists()  # no later salt once one passes
    # the salt-0 attempt is the designed half of the two-fauna run at salts (0, 0), byte for byte
    ref = _two_fauna(tiny, tmp_path / "ref")
    stages.run_job({**tiny, "job": "salt0cmp", "name": "F/tiny/7/conventional/salt0cmp", "fauna": D, "dir": str(d),
                    "src": str(d / "salt0"), "ref": str(ref)})
    assert (d / stages.SALT0_FILE).read_text().startswith("SALT0 PASS")


def test_a_salt0_mismatch_fails_loudly(tmp_path, tiny):
    alone = tmp_path / "alone"
    stages.run_job({**tiny, "job": "fresh", "name": "a/S", "dir": str(alone), "extra": stages.screen_argv(H, 0)})
    ref = _two_fauna(tiny, tmp_path / "ref", stages.salts_argv(1, 0))  # not the same holistic stream
    d = tmp_path / "F"
    d.mkdir()
    with pytest.raises(SystemExit, match="SALT0 MISMATCH"):
        stages.run_job({**tiny, "job": "salt0cmp", "name": "F/tiny/7/holistic/salt0cmp", "fauna": H, "dir": str(d),
                        "src": str(alone), "ref": str(ref)})
    assert (d / stages.SALT0_FILE).read_text().startswith("SALT0 FAIL")
    assert not stages._done(str(d), "salt0cmp")
    # and one edited lineage line is caught
    ref0 = _two_fauna(tiny, tmp_path / "ref0")
    lines = (ref0 / "lineage.jsonl").read_text().splitlines()
    k = next(i for i, l in enumerate(lines) if json.loads(l)["population"] == H)
    lines[k] = lines[k].replace('"energy": ', '"energy":  ')
    (ref0 / "lineage.jsonl").write_text("\n".join(lines) + "\n")
    assert stages.half_compare(str(alone), str(ref0), H)[0] == "FAIL"


def test_ksalt_passes_the_designed_half_at_s_ge_1_and_a_void_fails_loudly(tmp_path, tiny, capsys):
    """F7; #495 ruling SHOULD 6: a VOID is written to the unit's record, printed to stderr and stops the lane; the job
    is marked, so a restarted lane goes on past it."""
    census = _two_fauna(tiny, tmp_path / "census")
    s1 = _two_fauna(tiny, tmp_path / "unit" / "S", stages.salts_argv(1, 0))
    st = _two_fauna(tiny, tmp_path / "unit2" / "S", stages.salts_argv(1, 1))
    stages.run_job({**tiny, "job": "ksalt", "name": "1/tiny/7/KSALT", "src": str(s1), "ref": str(census), "dir": str(tmp_path / "unit" / "ksalt")})
    assert (tmp_path / "unit" / "ksalt" / stages.KSALT_FILE).read_text().startswith("KSALT PASS")
    assert (tmp_path / "unit" / stages.RECORD / stages.KSALT_FILE).read_text().startswith("KSALT PASS")
    job = {**tiny, "job": "ksalt", "name": "1/tiny/7/KSALT", "src": str(st), "ref": str(census), "dir": str(tmp_path / "unit2" / "ksalt")}
    with pytest.raises(SystemExit, match="KSALT VOID"):
        stages.run_job(job)
    assert "KSALT VOID" in capsys.readouterr().err
    assert (tmp_path / "unit2" / "ksalt" / stages.KSALT_FILE).read_text().startswith("KSALT VOID")
    assert (tmp_path / "unit2" / stages.RECORD / stages.KSALT_FILE).read_text().startswith("KSALT VOID")
    assert (tmp_path / "unit2" / stages.KSALT_FILE).exists()
    stages.run_job(job)  # restarted: marked, so it does not stop the lane again


def test_adopt_takes_the_census_state_only_at_its_own_config(tmp_path, tiny):
    census = _two_fauna(tiny, tmp_path / "census")
    job = {**tiny, "job": "adopt", "name": "1/tiny/7/S60", "src": str(census), "dir": str(tmp_path / "S")}
    stages.run_job(job)
    assert (tmp_path / "S" / "state.json").read_bytes() == (census / "state.json").read_bytes()
    salted = _two_fauna(tiny, tmp_path / "salted", stages.salts_argv(0, 2))  # a census state at another salt is refused
    with pytest.raises(SystemExit):
        stages.run_job({**job, "src": str(salted), "dir": str(tmp_path / "S2")})


def test_stage1_units_keep_records_and_every_record_has_a_branch(tmp_path, monkeypatch):
    """#495 ruling SHOULD 8: Stage-1 chains' unit files (EXTINCT.txt, UNIT.txt, KSALT.txt) are restored from and listed
    as the unit's record branch, as the pilot's are."""
    root = tmp_path / "repo" / "runs" / "RBT-129"
    monkeypatch.setattr(stages, "ROOT", str(tmp_path / "repo"))
    monkeypatch.setattr(stages, "RUNS", str(root))
    units = stages.stage1_units(str(root), _salts(j2=(1, 0)))
    lane = tmp_path / "lane.jsonl"
    lane.write_text("".join(json.dumps({k: (stages.rel(v) if k in stages.PATH_KEYS else v) for k, v in j.items()}) + "\n"
                            for u in units[:2] for j in u["jobs"]))
    want = stages.expected_branches([str(lane)])
    for u in units[:2]:
        unit = os.path.dirname(u["jobs"][0]["dir"])
        assert stages._label(os.path.join(unit, stages.RECORD)) in want
    assert "1/" in stages.UNIT_PREFIXES and "P/" in stages.UNIT_PREFIXES


# --- the gate re-derives from the attempt runs -----------------------------------------------------------------------

@pytest.fixture
def screened(tmp_path, tiny, monkeypatch):
    """A real tiny screen: seeds 1-2, both faunas, salts 0-2, a criterion of 1, each seed's two-fauna reference at
    stage0/tiny/<seed>/S, and the salt-0 compares; the gate's block argv is the tiny world's."""
    root = tmp_path / "root"
    monkeypatch.setattr(stages, "SCREEN_SEEDS", (1, 2))
    monkeypatch.setattr(stages, "SALT0_REF", {1: "stage0", 2: "stage0"})
    monkeypatch.setattr(stages, "SCREEN_CRITERION", 1)
    monkeypatch.setattr(stages, "SCREEN_SALTS", (0, 1, 2))
    monkeypatch.setattr(stages, "SCREEN_POINT", "tiny")
    monkeypatch.setattr(stages, "screen_block_argv", lambda root: TINY + ["--fair", "--sweep-log"])
    for j in (1, 2):
        _two_fauna({**tiny, "seed": stages.seed(j)}, stages.salt0_ref(str(root), j))
        for k in (H, D):
            d = stages.screen_dir(str(root), j, k)
            base = {**tiny, "seed": stages.seed(j), "fauna": k, "dir": d}
            stages.run_job({**base, "job": "screen", "name": f"F/tiny/{j}/{k}/screen"})
            stages.run_job({**base, "job": "salt0cmp", "name": f"F/tiny/{j}/{k}/salt0cmp", "src": stages.attempt_dir(str(root), j, k, 0),
                            "ref": stages.salt0_ref(str(root), j)})
    return root


def _rec(root, j, k):
    return os.path.join(stages.screen_dir(str(root), j, k), stages.SCREEN_FILE)


def test_the_gate_passes_a_real_screen_and_returns_its_salts(screened):
    salts = stages.screen_gate(str(screened))
    recs = {(j, k): json.load(open(_rec(screened, j, k))) for j in (1, 2) for k in (H, D)}
    assert salts == {j: (recs[(j, H)]["salt"], recs[(j, D)]["salt"]) for j in (1, 2)}
    assert stages.salt0_verdicts(str(screened)) == {(j, k): "PASS" for j in (1, 2) for k in (H, D)}


def _edit(path, **kw):
    rec = json.load(open(path))
    rec.update(kw)
    json.dump(rec, open(path, "w"))


@pytest.mark.parametrize("how", ["no attempt", "alive edited", "point", "criterion", "attempt config", "incomplete"])
def test_the_gate_refuses_records_their_runs_do_not_bear_out(screened, how):
    """#495 ruling SHOULD 1: a record is checked against its attempt's own run: a hand-written SCREEN.json (no run), an
    alive count the run does not give, the wrong point or criterion, an attempt run at another salt, or cut short."""
    path = _rec(screened, 2, D)
    rec = json.load(open(path))
    first = rec["tried"][0]
    if how == "no attempt":
        shutil.rmtree(stages.attempt_dir(str(screened), 2, D, first["salt"]))
    elif how == "alive edited":  # a record the rule still accepts, but not what the run gives
        fake = {"salt": 0, "alive59": first["alive59"] + 100, "last": first["last"]}
        _edit(path, tried=[fake], salt=0, capped=False)
    elif how == "point":
        _edit(path, point="c1-p030-U-L")
    elif how == "criterion":
        _edit(path, criterion=30)
    elif how == "attempt config":
        cfg = os.path.join(stages.attempt_dir(str(screened), 2, D, first["salt"]), "config.json")
        c = json.load(open(cfg))
        c["designed_stream_salt"] = 9
        json.dump(c, open(cfg, "w"), indent=2)
    else:
        st = os.path.join(stages.attempt_dir(str(screened), 2, D, first["salt"]), "state.json")
        s = json.load(open(st))
        s["season"] = 1
        json.dump(s, open(st, "w"))
    with pytest.raises(SystemExit) as e:
        stages.screen_gate(str(screened))
    assert e.value.code == 8


def test_the_gate_recomputes_the_salt0_compare_rather_than_read_salt0_txt(screened):
    """A SALT0.txt saying PASS is not enough: an edited reference line fails the gate (SHOULD 1)."""
    ref = os.path.join(stages.salt0_ref(str(screened), 1), "lineage.jsonl")
    lines = open(ref).read().splitlines()
    k = next(i for i, l in enumerate(lines) if json.loads(l)["population"] == H)
    lines[k] = lines[k].replace('"energy": ', '"energy":  ')
    open(ref, "w").write("\n".join(lines) + "\n")
    assert open(os.path.join(stages.screen_dir(str(screened), 1, H), stages.SALT0_FILE)).read().startswith("SALT0 PASS")
    with pytest.raises(SystemExit) as e:
        stages.screen_gate(str(screened))
    assert e.value.code == 8


def test_the_gate_refuses_a_missing_record_and_the_stop_rule(screened, monkeypatch):
    os.remove(_rec(screened, 1, H))
    with pytest.raises(SystemExit) as e:
        stages.screen_gate(str(screened))
    assert e.value.code == 8


def test_the_gate_applies_the_stop_rule_to_a_real_capped_screen(tmp_path, tiny, monkeypatch):
    """With a criterion no tiny run meets, every fauna is capped at salt 0: seeds 1 and 2 are two capped of 1-8."""
    monkeypatch.setattr(stages, "SCREEN_SEEDS", (1, 2))
    monkeypatch.setattr(stages, "SALT0_REF", {})
    monkeypatch.setattr(stages, "SCREEN_CRITERION", 999)
    monkeypatch.setattr(stages, "SCREEN_SALTS", (0, 1))
    monkeypatch.setattr(stages, "SCREEN_POINT", "tiny")
    monkeypatch.setattr(stages, "screen_block_argv", lambda root: TINY + ["--fair", "--sweep-log"])
    root = tmp_path / "root"
    for j in (1, 2):
        for k in (H, D):
            stages.run_job({**tiny, "seed": stages.seed(j), "fauna": k, "dir": stages.screen_dir(str(root), j, k),
                            "job": "screen", "name": f"F/tiny/{j}/{k}/screen"})
    with pytest.raises(SystemExit) as e:
        stages.screen_gate(str(root))
    assert e.value.code == 8
    text = stages.screen_report(str(root))
    assert "STAGE 1 DOES NOT LAUNCH" in text
    for k in (H, D):  # SHOULD 3: a capped fauna's draws are their own group, not accepted and not rejected
        assert f"  {k:12s} capped   draws   4" in text
        assert f"  {k:12s} accepted draws   0" in text and f"  {k:12s} rejected draws   0" in text


# --- F8: the side-effect table and the report ---------------------------------------------------------------------

def _written(tmp_path):
    """A hand-written two-founder lineage (living cost 0.25, price 0): founder a earns 0.3 for three seasons and starves
    in the fourth (its death row earns 0); founder b dies in season 0."""
    d = tmp_path / "a"
    d.mkdir()
    (d / "config.json").write_text(json.dumps({"sim": {"food": {"work_cost": 0.0}}, "ecology": {"living_cost": 0.25}}))
    row = lambda g, name, food, **kw: json.dumps({"generation": g, "population": H, "name": name, "parents": [], "nodes": 5,
                                                  "food": food, "work": 0.0, **kw})
    lines = [row(0, "b", 0.0, death="starved"), row(0, "a", 0.3), row(1, "a", 0.3), row(2, "a", 0.3),
             row(3, "a", 0.0, death="starved"), row(3, "c", 9.0, death="cull")]
    (d / "lineage.jsonl").write_text("\n".join(lines) + "\n")
    (d / "history.json").write_text(json.dumps({"history": []}))
    return d


def test_founder_solvency_is_the_stage0_readouts(tmp_path):
    """#495 ruling MUST 2: the readout keeps the starved and aged rows (drops cull and merge-null): founders are 2 (b,
    dead in season 0, counts), a's mean is 0.225 < 0.25 (its dying season counts), so solvency is 0 of 2."""
    fx = stages.side_effects(str(_written(tmp_path)), H)
    assert (fx["founders"], fx["solvency"]) == (2, 0.0)
    s0, s3 = fx["seasons"][0], fx["seasons"][3]
    assert s0["founders_alive"] == 1 and abs(s0["income"] - 0.15) < 1e-12  # the living founder; income with the dead
    assert s3["founders_alive"] == 0 and s3["income"] == 0.0  # the cull row is not in the income either


def test_the_side_effect_table_and_the_screen_report(screened):
    fx = stages.side_effects(stages.attempt_dir(str(screened), 1, D, 0), D)
    assert fx["founders"] == 4 and set(fx["seasons"]) == set(range(15)) and fx["seasons"][0]["founders_alive"] <= 4
    text = stages.screen_report(str(screened))
    for head in ("## screen table", "## founding layer", "## salt-0 single-fauna re-run", "## stop rule", "## side-effect table"):
        assert head in text
    assert "stream draws (founders and their early history)" in text
    # SHOULD 4: the census's own numbers, from the committed readout
    assert "holistic     FOUNDING-FAIL at 150 of 150 points" in text and "conventional FOUNDING-FAIL at 34 of 150 points" in text
    assert "absent means 0" in text


# --- the byte-compare (the #495 adversary's two tests, SHOULD 7) ------------------------------------------------

def test_the_byte_compare_sees_season_59_and_nothing_after(tmp_path):
    """Kills the mutant that drops the last season from the compare: two runs that differ only in season 59's row (or
    lineage line) FAIL; a difference at season 60 (the pilot S ran on to 300) does not count."""
    def write(d, hist, lin):
        d.mkdir()
        (d / "history.json").write_text(json.dumps({"history": hist}))
        (d / "lineage.jsonl").write_text("".join(json.dumps(r) + "\n" for r in lin))
    row = lambda s, alive: {"season": s, "population": H, "alive": alive, "births": 0}
    line = lambda g, e: {"generation": g, "population": H, "name": "a", "energy": e}
    write(tmp_path / "a", [row(58, 5), row(59, 5)], [line(58, 1.0), line(59, 1.0)])
    write(tmp_path / "b", [row(58, 5), row(59, 4)], [line(58, 1.0), line(59, 1.0)])
    write(tmp_path / "c", [row(58, 5), row(59, 5)], [line(58, 1.0), line(59, 2.0)])
    write(tmp_path / "d", [row(58, 5), row(59, 5), row(60, 9)], [line(58, 1.0), line(59, 1.0), line(60, 7.0)])
    a = str(tmp_path / "a")
    assert stages.half_compare(a, str(tmp_path / "b"), H)[0] == "FAIL"
    assert stages.half_compare(a, str(tmp_path / "c"), H)[0] == "FAIL"
    assert stages.half_compare(a, str(tmp_path / "d"), H)[0] == "PASS"


def test_the_byte_compare_is_never_vacuous(tmp_path):
    """Kills the mutant without the EMPTY guard: an attempt that never ran, compared with a reference that is not
    restored (both directories empty), must FAIL, not PASS on [] == []; and so must an attempt with history but no
    lineage."""
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(), b.mkdir()
    assert stages.half_compare(str(a), str(b), H)[0] == "FAIL"
    (a / "history.json").write_text(json.dumps({"history": [{"season": 0, "population": H, "alive": 1, "births": 0}]}))
    (b / "history.json").write_text((a / "history.json").read_text())
    assert stages.half_compare(str(a), str(b), H)[0] == "FAIL"
