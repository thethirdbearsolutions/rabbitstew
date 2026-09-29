"""Adversary tests for RBT-129c (#495): the designed stream salt and the Stage F founder screen.

Run from a checkout of the PR head (they import its ``stages.py`` and ``rabbitstew``), for example:

    python -m pytest runs/RBT-129/founding-screen-adversary/test_founding_screen_adversary.py -q

Tiny non-sweep worlds only; nothing here runs the screen or a sweep arm.  A test named ``test_hole_*`` asserts the
behaviour the adversary reports as a defect (it passes on the PR head and documents the hole); every other test is
a check the PR should pass and does.
"""
import itertools
import json
import os
import shutil
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-129", "launch"))

import stages  # noqa: E402
from rabbitstew.ecology import breed_seed_sequence, merge_null_seed_sequence  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, STREAMS, spawn_streams  # noqa: E402

H, D = stages.H, stages.D
TINY = ["--capacity", "4", "--challenge", "foraging", "--group-size", "2", "--brain-model", "foraging", "--food-items", "4",
        "--duration", "0.4", "--terrain", "flat", "--conventional-topology", "--score", "food", "--living-cost", "0.05",
        "--initial-energy", "2", "--birth-threshold", "0.5", "--birth-cost", "0.2", "--max-age", "6"]


# --- 1. keys and streams ------------------------------------------------------------------------------------------ #

def _state(ss):
    return tuple(int(x) for x in ss.generate_state(8))


def test_no_key_collides_across_every_stream_the_sweep_can_make():
    """Every stream the sweep's seeds can spawn: unsalted (i,), holistic (0, s), designed (1, t), breed (0, 0, K),
    merge-null (i, 1, 0), for seeds 129001-129016 and salts / K 1-20.  All pool states distinct (not just the keys)."""
    seen = {}
    for seed in range(129001, 129017):
        keys = [(i,) for i in range(len(STREAMS))]
        keys += [(STREAMS.index(HOLISTIC), s) for s in range(1, 21)]
        keys += [(STREAMS.index(CONVENTIONAL), t) for t in range(1, 21)]
        streams = {k: np.random.SeedSequence(seed, spawn_key=k) for k in keys}
        streams.update({("breed", k): breed_seed_sequence(seed, k) for k in range(1, 21)})
        streams.update({("null", kind): merge_null_seed_sequence(seed, kind) for kind in (HOLISTIC, CONVENTIONAL)})
        for k, ss in streams.items():
            st = _state(ss)
            assert st not in seen, f"{seed} {k} collides with {seen[st]}"
            seen[st] = (seed, k)
    # spawn_streams' own children are exactly the (i,) keys, and a salt replaces one entry only
    for seed in (129001, 129016):
        base = spawn_streams(seed)
        for s, t in itertools.product((0, 1, 20), repeat=2):
            got = spawn_streams(seed, s, t)
            for name in STREAMS:
                moved = (name == HOLISTIC and s) or (name == CONVENTIONAL and t)
                same = got[name].bit_generator.state == base[name].bit_generator.state
                assert same != bool(moved), (seed, s, t, name)


def test_designed_salt_equals_the_mirror_seed_sequence_exactly():
    for seed, t in ((129001, 1), (129008, 20)):
        want = np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(STREAMS.index(CONVENTIONAL), t)))
        assert spawn_streams(seed, 0, t)[CONVENTIONAL].bit_generator.state == want.bit_generator.state


def test_negative_salts_are_refused_on_every_path():
    with pytest.raises(ValueError):
        spawn_streams(1, 0, -1)
    with pytest.raises(ValueError):
        spawn_streams(1, -1, 0)
    with pytest.raises(SystemExit):
        stages.check_extra(["--designed-stream-salt", "-1"])


# --- 2. salts on a tiny world: isolation and composition --------------------------------------------------------- #

@pytest.fixture
def tiny(tmp_path, monkeypatch):
    monkeypatch.setenv("NO_DURABLE", "1")
    monkeypatch.setenv("WORKERS", "1")
    worlds = tmp_path / "worlds"
    worlds.mkdir()
    (worlds / "tiny.json").write_text(json.dumps({"id": "tiny", "argv": TINY + ["--fair", "--sweep-log"], "fair": ["--fair"]}))
    monkeypatch.setattr(stages, "SCREEN_SEASON", 3)
    return {"worlds": str(worlds), "point": "tiny", "seed": 129002, "seasons": 4}


def _run(tiny, d, extra=(), **kw):
    stages.run_job({**tiny, **kw, "job": "fresh", "name": "x/S", "dir": str(d), "extra": list(extra)})
    return str(d)


def _half(d, kind):
    return stages.half_lines(d, kind, upto=99)


def _world(d):
    return [(e["season"], e["terrain_seed"], e["start_seed"]) for e in stages._history(d)]


def test_each_salt_moves_its_own_half_only_and_the_two_compose(tmp_path, tiny):
    """(s, t) on a two-fauna run: the holistic half is the (s, 0) run's, the designed half the (0, t) run's, and the
    worlds (terrain and start seeds) never move.  A non-trivial check: each salt does move its own half."""
    r00 = _run(tiny, tmp_path / "00")
    r30 = _run(tiny, tmp_path / "30", stages.salts_argv(3, 0))
    r05 = _run(tiny, tmp_path / "05", stages.salts_argv(0, 5))
    r35 = _run(tiny, tmp_path / "35", stages.salts_argv(3, 5))
    assert _world(r00) == _world(r30) == _world(r05) == _world(r35)
    assert _half(r30, D) == _half(r00, D) and _half(r30, H) != _half(r00, H)
    assert _half(r05, H) == _half(r00, H) and _half(r05, D) != _half(r00, D)
    assert _half(r35, H) == _half(r30, H) and _half(r35, D) == _half(r05, D)


def test_a_salted_fauna_alone_is_its_half_of_the_salted_two_fauna_run(tmp_path, tiny):
    """What the fork source relies on: a screened attempt (fauna alone at its salt) equals that fauna's half of the
    two-fauna run at (s_j, t_j), for either fauna, whatever the other's salt."""
    two = _run(tiny, tmp_path / "two", stages.salts_argv(2, 4))
    h = _run(tiny, tmp_path / "h", stages.screen_argv(H, 2))
    d = _run(tiny, tmp_path / "d", stages.screen_argv(D, 4))
    assert stages.half_compare(h, two, H, upto=3)[0] == "PASS"
    assert stages.half_compare(d, two, D, upto=3)[0] == "PASS"


def test_salts_reach_the_ckpt60_fork_and_every_resume(tmp_path, tiny):
    """A Stage-1 chain at (s, t): S60 fresh, the snapshot, S resumed; and an M fork of the snapshot.  The resumed and
    forked runs keep both salts in config.json, and the straight run equals the resumed one byte for byte."""
    ext = stages.salts_argv(3, 7)
    s = _run(tiny, tmp_path / "S", ext, seasons=2)
    straight = _run(tiny, tmp_path / "straight", ext, seasons=4)
    snap = tmp_path / "ckpt"
    stages.fork_config(s, str(snap), {})
    stages._resume({"seasons": 4}, s, False)
    for f in ("history.json", "lineage.jsonl", "state.json"):
        assert open(os.path.join(s, f), "rb").read() == open(os.path.join(straight, f), "rb").read(), f
    m = tmp_path / "M"
    stages.fork_config(str(snap), str(m), {"merge_after": 2, "pooled_capacity": 8})
    stages._resume({"seasons": 4}, str(m), False)
    for d in (s, str(snap), str(m)):
        cfg = json.load(open(os.path.join(d, "config.json")))
        assert (cfg.get("holistic_stream_salt"), cfg.get("designed_stream_salt")) == (3, 7), d


def test_breed_stream_is_refused_with_either_salt(tmp_path, tiny):
    for i, ext in enumerate((stages.salts_argv(1, 0), stages.salts_argv(0, 1))):
        d = tmp_path / f"b{i}"
        d.mkdir()
        with pytest.raises(SystemExit):
            stages._ecology([*TINY, "--fair", *ext, "--breed-stream", "1", "--seed", "1", "--seasons", "1"], str(d), "b")
        assert "breed_stream cannot be combined" in (d / "run.log").read_text()


# --- 3. the screen's rule ---------------------------------------------------------------------------------------- #

def test_the_rule_at_the_boundaries():
    runs = lambda alive: (lambda s: (alive.get(s, 0), 59 if alive.get(s, 0) else 10))
    r = stages.screen(runs({0: 29, 1: 30}))
    assert (r["salt"], r["capped"], len(r["tried"])) == (1, False, 2)  # 29 fails, exactly 30 passes
    r = stages.screen(runs({20: 30}))
    assert (r["salt"], r["capped"], len(r["tried"])) == (20, False, 21)  # the 20th redraw is still tried
    r = stages.screen(runs({21: 60}))
    assert (r["salt"], r["capped"], len(r["tried"])) == (0, True, 21)  # salt 21 is never tried
    assert stages.SCREEN_SALTS == tuple(range(21)) and stages.SCREEN_CRITERION == 30 and stages.SCREEN_SEASON == 59


def test_alive_before_refill_is_the_readouts_count():
    hist = [{"population": H, "season": 59, "alive": 60, "births": 31}, {"population": D, "season": 59, "alive": 30, "births": 0}]
    assert stages.alive_before_refill(hist, H) == 29 and not stages.founds(stages.alive_before_refill(hist, H))
    assert stages.founds(stages.alive_before_refill(hist, D))
    assert stages.alive_before_refill([], H) == 0  # extinct before 59: no row


@pytest.mark.parametrize("capped,fires", [
    ((), False), ((1,), False), ((9, 10), False), ((1, 9), False), ((1, 2), True), ((8, 9, 16), True),
    ((9, 10, 11), True), ((7, 8), True), ((8, 16), False)])
def test_the_stop_rule_table(capped, fires):
    assert bool(stages.stop_rule(list(capped))) == fires


def test_a_seed_capped_on_both_faunas_counts_once():
    res = {(j, k): {"capped": j in (9, 10) } for j in stages.SCREEN_SEEDS for k in stages.FAUNAS}
    assert stages.capped_seeds(res) == [9, 10] and not stages.stop_rule(stages.capped_seeds(res))


# --- 4. the gate, and what it trusts ----------------------------------------------------------------------------- #

def _fake_screen(root, alive=60, salt0_line="SALT0 PASS: fabricated\n", with_attempts=False):
    for j in stages.SCREEN_SEEDS:
        for k in stages.FAUNAS:
            d = stages.screen_dir(root, j, k)
            os.makedirs(d, exist_ok=True)
            rec = {"seed": stages.seed(j), "fauna": k, "point": "nowhere", "criterion": 1,
                   "tried": [{"salt": 0, "alive59": alive, "last": 59}], "salt": 0, "capped": False}
            json.dump(rec, open(os.path.join(d, stages.SCREEN_FILE), "w"))
            if j in stages.SALT0_REF:
                open(os.path.join(d, stages.SALT0_FILE), "w").write(salt0_line)


def test_hole_the_gate_accepts_records_with_no_attempt_behind_them(tmp_path):
    """HOLE (SHOULD): SCREEN.json and SALT0.txt are trusted as text.  Records written by hand, with no attempt
    directory, no history.json, a wrong point and a wrong criterion, pass the gate, and Stage 1 is emitted from them."""
    root = str(tmp_path)
    _fake_screen(root)
    assert not os.path.exists(stages.attempt_dir(root, 1, H, 0))
    salts = stages.screen_gate(root)
    assert salts == {j: (0, 0) for j in stages.SCREEN_SEEDS}
    assert len(stages.stage1_units(root, salts)) == len(stages.STAGE1_POINTS) * stages.STAGE1_N


def test_the_gate_refuses_a_missing_record_a_fail_and_the_stop_rule(tmp_path):
    root = str(tmp_path)
    _fake_screen(root, salt0_line="SALT0 FAIL: x\n")
    with pytest.raises(SystemExit):
        stages.screen_gate(root)
    _fake_screen(root)
    os.remove(os.path.join(stages.screen_dir(root, 16, D), stages.SCREEN_FILE))
    with pytest.raises(SystemExit):
        stages.screen_gate(root)
    _fake_screen(root)
    for j in (3, 5):  # two capped of seeds 1-8
        d = stages.screen_dir(root, j, H)
        rec = {"seed": stages.seed(j), "fauna": H, "tried": [{"salt": s, "alive59": 0, "last": 10} for s in range(21)], "salt": 0, "capped": True}
        json.dump(rec, open(os.path.join(d, stages.SCREEN_FILE), "w"))
    with pytest.raises(SystemExit):
        stages.screen_gate(root)


def test_a_float_salt_record_is_accepted_equivalent_mutant_reasoning(tmp_path):
    """Why the implementer's surviving mutant (the explicit order check removed) is equivalent: the re-derivation's
    dict equality already fixes the order and content of ``tried``; the one record the order check alone might have
    stopped, salts as floats (0.0 == 0), passes both with and without it."""
    rec = {"seed": 129001, "fauna": H, "tried": [{"salt": 0.0, "alive59": 40, "last": 59}], "salt": 0, "capped": False}
    stages.check_screen_record(rec)  # accepted, as it would be by the mutant
    for bad in ([{"salt": 1, "alive59": 40, "last": 59}],
                [{"salt": 0, "alive59": 0, "last": 5}, {"salt": 0, "alive59": 40, "last": 59}],
                [{"salt": 0, "alive59": 40, "last": 59, "extra": 1}]):
        with pytest.raises(SystemExit):
            stages.check_screen_record({**rec, "tried": bad})


# --- 5. Stage 1 and the fork source ------------------------------------------------------------------------------ #

def _salts(**over):
    s = {j: (0, 0) for j in stages.SCREEN_SEEDS}
    s.update({int(k[1:]): v for k, v in over.items()})
    return s


def test_stage1_resume_rule_and_ksalt_placement():
    units = stages.stage1_units("/r", _salts(j2=(4, 0), j3=(2, 1), j5=(1, 0), j1=(0, 0)))
    assert len(units) == 36 * 8 and {u["seed"] for u in units} == set(range(129001, 129009))
    by = {}
    for u in units:
        by.setdefault(u["seed"], []).append(u)
    for u in by[129001]:
        assert u["jobs"][0]["job"] == "adopt" and u["jobs"][0]["src"].endswith(f"/stage0/{u['jobs'][0]['point']}/129001/S")
    for sd, want_ksalt in ((129002, True), (129003, False), (129005, False), (129004, False)):
        for u in by[sd]:
            first = u["jobs"][0]
            assert first["job"] == "fresh"
            kinds = [j["job"] for j in u["jobs"]]
            assert ("ksalt" in kinds) == want_ksalt, (sd, kinds)
    assert by[129002][0]["jobs"][0]["extra"] == ["--holistic-stream-salt", "4"]
    assert by[129003][0]["jobs"][0]["extra"] == ["--holistic-stream-salt", "2", "--designed-stream-salt", "1"]


def test_129001_is_fresh_at_any_nonzero_salt_and_gets_ksalt_at_s_only():
    for st, ks in (((1, 0), True), ((0, 1), False), ((2, 3), False)):
        u = stages.stage1_units("/r", _salts(j1=st))[0]
        assert u["jobs"][0]["job"] == "fresh" and (("ksalt" in [j["job"] for j in u["jobs"]]) == ks)


def test_hole_no_ksalt_on_the_fork_source_where_f7_says_the_runs_overlap():
    """HOLE (SHOULD): F7 names "129007 and 129008 at W118-b" as a K-SALT overlap.  The fork source is the two-fauna
    S 0-59 at W118-b; at (s >= 1, t = 0) its designed half must equal the A-stage (5-8) or census (1-3) run there.
    fork_source_units emits no K-SALT job."""
    units = stages.fork_source_units("/r", _salts(j2=(3, 0), j7=(1, 0), j8=(5, 0)))
    assert [j["job"] for u in units for j in u["jobs"]] == ["fresh"] * 8


# --- 6. the side-effect table (F8) against the Stage-0 readout's founder solvency ------------------------------ #

def _readout_solvency(d, kind, hi):
    """stageP0-readout/stageP0_readout.py's founder solvency (its rows() keeps the starved and aged rows; it drops
    only cull and merge-null), over generations 0..hi."""
    cfg = json.load(open(os.path.join(d, "config.json")))
    p, lc = cfg["sim"]["food"]["work_cost"], float(cfg["ecology"]["living_cost"])
    fs = {}
    for r in map(json.loads, open(os.path.join(d, "lineage.jsonl"))):
        if r.get("death") in ("cull", "merge-null") or r["population"] != kind:
            continue
        if not r["parents"] and r["generation"] <= hi:
            fs.setdefault(r["name"], []).append(r.get("food", 0.0) - p * r.get("work", 0.0) / 1000.0)
    return len(fs), (sum(1 for v in fs.values() if sum(v) / len(v) >= lc) / len(fs) if fs else None)


def test_hole_side_effect_solvency_drops_the_founders_that_die(tmp_path, tiny):
    """HOLE (SHOULD): side_effects() keeps only rows with no ``death``, so a founder that starves in season 0 is not a
    founder at all, and every founder's last (starving) season is left out of its mean.  The PR says this is the
    Stage-0 readout's solvency over 0-14; the readout keeps those rows.  On a world where founders starve early the two
    disagree: the PR's count of founders is short of the 4 drawn and its solvency is at least the readout's."""
    harsh = [x for x in TINY]
    harsh[harsh.index("--living-cost") + 1] = "0.6"
    (tmp_path / "worlds" / "harsh.json").write_text(json.dumps({"id": "harsh", "argv": harsh + ["--fair", "--sweep-log"], "fair": ["--fair"]}))
    d = _run(tiny, tmp_path / "harsh", stages.screen_argv(H, 0), point="harsh", seasons=6)
    fx = stages.side_effects(d, H)
    n, sol = _readout_solvency(d, H, 14)
    assert n == 4
    assert fx["founders"] < n
    assert fx["solvency"] is None or sol is None or fx["solvency"] >= sol


def test_hole_side_effect_solvency_on_a_written_lineage(tmp_path):
    """The same hole on a hand-written two-founder lineage (living cost 0.25, price 0): founder a earns 0.3 for three
    seasons and starves in the fourth (its death row earns 0); founder b dies in season 0.  The readout's solvency is
    0 of 2 (a's mean is 0.225); the PR's is 1 of 1."""
    d = tmp_path / "a"
    d.mkdir()
    (d / "config.json").write_text(json.dumps({"sim": {"food": {"work_cost": 0.0}}, "ecology": {"living_cost": 0.25}}))
    row = lambda g, name, food, **kw: json.dumps({"generation": g, "population": H, "name": name, "parents": [], "nodes": 5,
                                                  "food": food, "work": 0.0, **kw})
    lines = [row(0, "b", 0.0, death="starved"), row(0, "a", 0.3), row(1, "a", 0.3), row(2, "a", 0.3), row(3, "a", 0.0, death="starved")]
    (d / "lineage.jsonl").write_text("\n".join(lines) + "\n")
    (d / "history.json").write_text(json.dumps({"history": []}))
    fx = stages.side_effects(str(d), H)
    assert (fx["founders"], fx["solvency"]) == (1, 1.0)
    assert _readout_solvency(str(d), H, 14) == (2, 0.0)


def test_ksalt_is_valid_under_persistent_food_and_random_terrain(tmp_path, tiny):
    """K-SALT's premise at the PW points (persistent food, random terrain, patches, smell): a holistic salt leaves the
    designed half and the worlds byte for byte, and a designed salt leaves the holistic half."""
    pw = TINY + ["--terrain", "random", "--obstacles", "3", "--obstacle-radius", "0.5", "--food-patches", "2",
                 "--patch-radius", "0.4", "--regrow-delay", "2", "--smell", "log", "--random-start"]
    (tmp_path / "worlds" / "pw.json").write_text(json.dumps({"id": "pw", "argv": pw + ["--fair", "--sweep-log"], "fair": ["--fair"]}))
    r00 = _run(tiny, tmp_path / "p00", point="pw")
    r40 = _run(tiny, tmp_path / "p40", stages.salts_argv(4, 0), point="pw")
    r06 = _run(tiny, tmp_path / "p06", stages.salts_argv(0, 6), point="pw")
    assert _world(r00) == _world(r40) == _world(r06)
    assert stages.half_compare(r40, r00, D, upto=3)[0] == "PASS" and _half(r40, H) != _half(r00, H)
    assert stages.half_compare(r06, r00, H, upto=3)[0] == "PASS" and _half(r06, D) != _half(r00, D)


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
