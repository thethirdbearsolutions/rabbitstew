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


def test_lane_extras_are_the_founding_flags_only():
    stages.check_extra(["--only-fauna", H, "--holistic-stream-salt", "3", "--designed-stream-salt", "0"])
    for bad in (["--merge-after", "3"], ["--only-fauna", "both"], ["--designed-stream-salt", "-1"], ["--seed"]):
        with pytest.raises(SystemExit):
            stages.check_extra(bad)


# --- the gate and the report, from records -----------------------------------------------------------------------

def _write_screen(root, capped=(), fail0=(), missing=()):
    for j in stages.SCREEN_SEEDS:
        for k in (H, D):
            d = stages.screen_dir(str(root), j, k)
            os.makedirs(d, exist_ok=True)
            if (j, k) in missing:
                continue
            outcomes = {} if (j, k) in capped else ({0: 60} if (k == D or j not in (2, 3)) else {0: 0, 1: 58})
            attempt, _ = _fake(outcomes)
            with open(os.path.join(d, stages.SCREEN_FILE), "w") as f:
                json.dump({"seed": stages.seed(j), "fauna": k, **stages.screen(attempt)}, f)
            if j in stages.SALT0_REF:
                with open(os.path.join(d, stages.SALT0_FILE), "w") as f:
                    f.write(f"SALT0 {'FAIL' if (j, k) in fail0 else 'PASS'}: ...\n")


def test_the_gate_passes_a_clean_screen_and_returns_the_salts(tmp_path):
    _write_screen(tmp_path)
    salts = stages.screen_gate(str(tmp_path))
    assert salts[1] == (0, 0) and salts[2] == (1, 0) and salts[3] == (1, 0) and len(salts) == 16


@pytest.mark.parametrize("kw", [dict(missing=[(5, H)]), dict(fail0=[(4, D)]), dict(capped=[(1, H), (2, D)]),
                                dict(capped=[(9, H), (12, D), (16, H)])])
def test_the_gate_refuses_an_incomplete_screen_a_salt0_mismatch_or_the_stop_rule(tmp_path, kw):
    _write_screen(tmp_path, **kw)
    with pytest.raises(SystemExit) as e:
        stages.screen_gate(str(tmp_path))
    assert e.value.code == 8


def test_stage1_emit_refuses_without_the_screen(repo_tmp, fair_check):
    with pytest.raises(SystemExit) as e:
        stages.main(["stage1-emit", "--fair=--fair", "--root", str(repo_tmp)])
    assert e.value.code == 8


def test_the_screen_emits_32_screens_and_8_salt0_compares(repo_tmp, fair_check):
    stages.main(["screen-emit", "--fair=--fair", "--root", str(repo_tmp), "--hosts", "2"])
    jobs = [json.loads(l) for p in (repo_tmp / "lanes" / "F").glob("host*-lane*.jsonl") for l in p.read_text().splitlines()]
    screens = [j for j in jobs if j["job"] == "screen"]
    cmps = [j for j in jobs if j["job"] == "salt0cmp"]
    assert len(screens) == 32 and {(j["seed"], j["fauna"]) for j in screens} == {(stages.seed(j), k) for j in range(1, 17) for k in (H, D)}
    assert {j["point"] for j in screens} == {"c0-p030-U-L"} and all(j["seasons"] == 60 for j in screens)
    assert {(j["seed"], j["fauna"]) for j in cmps} == {(stages.seed(j), k) for j in (1, 2, 3, 4) for k in (H, D)}
    ref = {j["seed"]: j["ref"] for j in cmps}
    assert ref[129001].endswith("stage0/c0-p030-U-L/129001/S") and ref[129004].endswith("stageP/c0-p030-U-L/129004/S")
    assert all(not os.path.isabs(j["dir"]) for j in jobs)
    for p in (repo_tmp / "lanes" / "F").glob("host*-lane*.jsonl"):  # the compare follows its screen, in one lane
        names = [json.loads(l)["name"] for l in p.read_text().splitlines()]
        for i, n in enumerate(names):
            if n.endswith("salt0cmp"):
                assert n.replace("salt0cmp", "screen") in names[:i]
    block = json.loads((repo_tmp / "worlds" / "c0-p030-U-L.json").read_text())
    assert block["fair"] == ["--fair"] and "--sweep-log" in block["argv"]


# --- the jobs on a tiny world -------------------------------------------------------------------------------------

@pytest.fixture
def tiny(tmp_path, monkeypatch):
    monkeypatch.setenv("NO_DURABLE", "1")
    monkeypatch.setenv("WORKERS", "1")
    worlds = tmp_path / "worlds"
    worlds.mkdir()
    (worlds / "tiny.json").write_text(json.dumps({"id": "tiny", "argv": TINY + ["--fair", "--sweep-log"], "fair": ["--fair"]}))
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


def test_ksalt_passes_the_designed_half_at_s_ge_1_and_voids_otherwise(tmp_path, tiny):
    census = _two_fauna(tiny, tmp_path / "census")
    s1 = _two_fauna(tiny, tmp_path / "s1", stages.salts_argv(1, 0))
    st = _two_fauna(tiny, tmp_path / "st", stages.salts_argv(1, 1))
    stages.run_job({**tiny, "job": "ksalt", "name": "1/tiny/7/KSALT", "src": str(s1), "ref": str(census), "dir": str(tmp_path / "k1")})
    assert (tmp_path / "k1" / stages.KSALT_FILE).read_text().startswith("KSALT PASS")
    stages.run_job({**tiny, "job": "ksalt", "name": "1/tiny/7/KSALT", "src": str(st), "ref": str(census), "dir": str(tmp_path / "k2")})
    assert (tmp_path / "k2" / stages.KSALT_FILE).read_text().startswith("KSALT VOID")


def test_adopt_takes_the_census_state_only_at_its_own_config(tmp_path, tiny):
    census = _two_fauna(tiny, tmp_path / "census")
    job = {**tiny, "job": "adopt", "name": "1/tiny/7/S60", "src": str(census), "dir": str(tmp_path / "S")}
    stages.run_job(job)
    assert (tmp_path / "S" / "state.json").read_bytes() == (census / "state.json").read_bytes()
    salted = _two_fauna(tiny, tmp_path / "salted", stages.salts_argv(0, 2))  # a census state at another salt is refused
    with pytest.raises(SystemExit):
        stages.run_job({**job, "src": str(salted), "dir": str(tmp_path / "S2")})


def test_the_side_effect_table_and_the_screen_report(tmp_path, tiny, monkeypatch):
    root = tmp_path / "root"
    monkeypatch.setattr(stages, "SCREEN_SEEDS", (1,))
    monkeypatch.setattr(stages, "SALT0_REF", {1: "stage0"})
    monkeypatch.setattr(stages, "SCREEN_CRITERION", 1)
    monkeypatch.setattr(stages, "SCREEN_SALTS", (0, 1))
    monkeypatch.setattr(stages, "SCREEN_POINT", "tiny")
    for k in (H, D):
        d = stages.screen_dir(str(root), 1, k)
        stages.run_job({**tiny, "seed": stages.seed(1), "job": "screen", "name": f"F/tiny/1/{k}/screen", "fauna": k, "dir": d})
        with open(os.path.join(d, stages.SALT0_FILE), "w") as f:
            f.write("SALT0 PASS: test\n")
    fx = stages.side_effects(stages.attempt_dir(str(root), 1, D, 0), D)
    assert fx["founders"] == 4 and set(fx["seasons"]) == set(range(15)) and fx["seasons"][0]["founders_alive"] <= 4
    text = stages.screen_report(str(root))
    for head in ("## screen table", "## founding layer", "## salt-0 single-fauna re-run", "## stop rule", "## side-effect table"):
        assert head in text
    assert "stream draws (founders and their early history)" in text
    shutil.rmtree(root)
