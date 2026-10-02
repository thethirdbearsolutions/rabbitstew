"""A killed-and-resumed ecology is the uninterrupted one, byte for byte, wherever the kill lands; and one run
directory has one writer (RBT-129's K-SALT VOID on 1/c1-p010-PW-G/129003).

The census that K-SALT compared against had seasons 55-59 written twice to lineage.jsonl and cohorts.jsonl: a harness
kill took its lane, the ecology child lived on as an orphan, and the restarted lane resumed the same directory beside
it.  ``test_a_resume_beside_a_live_writer_waits_for_it`` reproduces that and failed before ``hold_run`` (26 duplicated
lineage rows, cohorts.jsonl duplicated, history.json and state.json identical).  A kill is ``os._exit`` in a forked
child: no cleanup runs, as under SIGKILL.
"""

import json
import os
import sys
import threading
import time

import pytest

from rabbitstew.ecology import RUN_LOCK, Ecology, EcologyConfig, hold_run
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.simulation import FoodConfig, SimConfig
from rabbitstew.world import WorldConfig

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "runs", "RBT-129", "launch"))
import stages  # noqa: E402


@pytest.fixture(autouse=True)
def _receipts_in_tmp(tmp_path, monkeypatch):
    """No test writes this machine's durable receipts (#510 adversary S-2)."""
    monkeypatch.setattr(stages, "DURABLE_DONE", str(tmp_path / "durable-done"))


FILES = ("lineage.jsonl", "cohorts.jsonl", "history.json", "state.json", "arenas.json")


def _evo():
    return EvolutionConfig(seed=11, brain_model="foraging", conventional_topology=True,
                           sim=SimConfig(duration=0.3, random_start=True, score="food", world=WorldConfig(terrain="random"),
                                         food=FoodConfig(items=4, radius=1.5, eat_radius=0.4)))


def _eco(**kw):
    # deaths by age and births every season, with the sweep log's death rows: every kind of lineage row is written
    base = dict(seasons=4, capacity=6, challenge="foraging", group_size=2, max_age=3, birth_threshold=0.0, birth_cost=0.0,
                starvation=False, log_every=1000, sweep_log=True)
    base.update(kw)
    return EcologyConfig(**base)


def _files(d):
    return {f: open(os.path.join(d, f), "rb").read() for f in FILES if os.path.exists(os.path.join(d, f))}


def _killed(out, eco, method, n, when):
    """Run ``eco`` in a child that dies (``os._exit``, no cleanup) at the ``n``-th call of ``Ecology.method``, before or
    after its body.  Returns whether it died there (False: the run ended first)."""
    pid = os.fork()
    if pid == 0:
        try:
            orig, calls = getattr(Ecology, method), [0]

            def hooked(self, *a, **kw):
                calls[0] += 1
                if calls[0] == n and when == "before":
                    os._exit(9)
                r = orig(self, *a, **kw)
                if calls[0] == n and when == "after":
                    os._exit(9)
                return r
            setattr(Ecology, method, hooked)
            Ecology(_evo(), eco, out_dir=out, log=None).run()
        finally:
            os._exit(0)
    _, st = os.waitpid(pid, 0)
    return os.WEXITSTATUS(st) == 9


#: mid-season (a lineage row, a cohort row), after the season's logs and before its state, between the history and the
#: state, and right after the state
KILLS = [("_log_lineage", 9, "before"), ("_log_lineage", 14, "after"), ("_record_cohort", 4, "before"), ("_record_cohort", 3, "after"),
         ("_record", 5, "after"), ("_flush", 2, "after"), ("save_state", 2, "before"), ("save_state", 3, "after")]


@pytest.mark.parametrize("method,n,when", KILLS)
def test_a_killed_run_resumes_byte_for_byte(tmp_path, method, n, when):
    ref = str(tmp_path / "ref")
    Ecology(_evo(), _eco(), out_dir=ref, log=None).run()
    out = str(tmp_path / "out")
    assert _killed(out, _eco(), method, n, when), "the kill point is past the run's end"
    assert os.path.exists(os.path.join(out, "state.json")), "the kill point is before the first season's state"
    Ecology.resume(out, log=None).run()
    want, got = _files(ref), _files(out)
    assert set(want) == set(got)
    for f in want:
        assert got[f] == want[f], f


def test_a_run_killed_after_its_extinct_state_resumes_to_nothing_more(tmp_path):
    """Killed after the state of the season everyone died in, before the run noticed: the resume steps no further
    (before, it stepped an empty season and moved state.json's season and streams on)."""
    eco = _eco(max_age=2, birth_threshold=100.0, seasons=6)
    ref = str(tmp_path / "ref")
    Ecology(_evo(), eco, out_dir=ref, log=None).run()
    last = json.load(open(os.path.join(ref, "state.json")))
    assert last["season"] < 6 and not any(last["populations"].values())  # extinct before the end
    out = str(tmp_path / "out")
    assert _killed(out, eco, "save_state", last["season"], "after")
    Ecology.resume(out, log=None).run()
    assert _files(out) == _files(ref)


def _slow_step(monkeypatch):
    step = Ecology.step

    def slow(self):
        step(self)
        time.sleep(0.3)
    monkeypatch.setattr(Ecology, "step", slow)


def test_a_resume_beside_a_live_writer_waits_for_it(tmp_path, monkeypatch):
    """The census failure: the first attempt is still running when the resume starts.  The resume waits for it and
    then goes on from the state it left, so the run is written once."""
    ref = str(tmp_path / "ref")
    Ecology(_evo(), _eco(seasons=6), out_dir=ref, log=None).run()
    _slow_step(monkeypatch)
    out = str(tmp_path / "out")
    pid = os.fork()
    if pid == 0:  # the orphan
        try:
            Ecology(_evo(), _eco(seasons=6), out_dir=out, log=None).run()
        finally:
            os._exit(0)
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                if json.load(open(os.path.join(out, "state.json")))["season"] >= 2:
                    break
            except (OSError, ValueError):
                pass
            time.sleep(0.02)
        said = []
        Ecology.resume(out, log=said.append).run()
        assert any("is writing this run; waiting" in s for s in said)
    finally:
        os.waitpid(pid, 0)
    assert _files(out) == _files(ref)


def test_a_killed_writer_leaves_no_lock_behind(tmp_path):
    out = str(tmp_path / "out")
    assert _killed(out, _eco(), "save_state", 2, "after")
    assert os.path.exists(os.path.join(out, RUN_LOCK))
    pid = os.fork()
    if pid == 0:  # another process: the lock is free at once
        import fcntl
        fd = os.open(os.path.join(out, RUN_LOCK), os.O_RDWR)
        try:
            fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            os._exit(0)
        except OSError:
            os._exit(1)
    _, st = os.waitpid(pid, 0)
    assert os.WEXITSTATUS(st) == 0


def test_the_lane_waits_for_a_live_writer_before_it_decides(tmp_path):
    """stages.py's ``_fresh`` / ``_resume`` wait on the directory's lock before reading state.json or wiping the
    directory; a directory that is not there yet is not created."""
    stages._writer_gone(str(tmp_path / "absent"))
    assert not (tmp_path / "absent").exists()
    d = str(tmp_path / "run")
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:  # a writer holding the lock for a while
        os.close(r)
        hold_run(d, log=None)
        os.write(w, b"x")
        time.sleep(1.0)
        os._exit(0)
    os.close(w)
    os.read(r, 1)
    done = []
    t = threading.Thread(target=lambda: (stages._writer_gone(d), done.append(time.time())))
    t0 = time.time()
    t.start()
    t.join(30)
    os.waitpid(pid, 0)
    assert done and done[0] - t0 >= 0.5


def test_k1_ignores_the_lock_file():
    assert RUN_LOCK in stages.K1_SKIP


H_ = "conventional"
_line = lambda g, n: {"generation": g, "population": H_, "name": n}
CLEAN = [_line(0, "a"), _line(1, "a"), _line(1, "b"), _line(2, "a"), _line(2, "b")]
#: the census signature: season 1 written twice, then season 2 by both writers, interleaved
TWICE = CLEAN[:3] + [CLEAN[1], CLEAN[2], CLEAN[3], CLEAN[3], CLEAN[4], CLEAN[4]]


def _half(d, lin, resumes=1):
    d.mkdir()
    (d / "history.json").write_text(json.dumps({"history": [{"season": s, "population": H_, "alive": 1} for s in range(3)]}))
    (d / "lineage.jsonl").write_text("".join(json.dumps(r) + "\n" for r in lin))
    if resumes is not None:
        (d / "platform.json").write_text(json.dumps({"resumes": [{"written_utc": "x"}] * resumes}))
    return str(d)


def test_k_salt_drops_a_double_written_references_duplicates_and_says_where(tmp_path):
    """The census of 1/c1-p010-PW-G/129003: seasons written twice by two writers; with them dropped it is the Stage-1
    half byte for byte.  The verdict line names the count, the generation range and the resume."""
    a = _half(tmp_path / "stage1", CLEAN)
    v, lines = stages.half_compare(a, _half(tmp_path / "census", TWICE), H_, upto=2)
    assert v == "PASS", lines
    assert ("4 exact duplicate lineage lines of the reference dropped: generations 1-2, each line twice, every line of those"
            " generations; the reference was resumed 1 time(s)") in lines[0]
    part = TWICE[:3] + [CLEAN[2], CLEAN[3], CLEAN[3], CLEAN[4], CLEAN[4]]  # the resume's cut took the orphan's first row
    v, lines = stages.half_compare(a, _half(tmp_path / "partial", part), H_, upto=2)
    assert v == "PASS" and "not every line of those generations" in lines[0]


def test_k_salt_never_de_duplicates_the_attempt_and_a_differing_line_still_fails(tmp_path):
    clean, twice = _half(tmp_path / "clean", CLEAN), _half(tmp_path / "twice", TWICE)
    assert stages.half_compare(twice, clean, H_, upto=2)[0] == "FAIL"
    assert stages.half_compare(twice, twice, H_, upto=2)[0] == "FAIL"  # dedup(b) != a
    other = _half(tmp_path / "other", CLEAN[:4] + [_line(2, "c")] + [CLEAN[3]])
    assert stages.half_compare(clean, other, H_, upto=2)[0] == "FAIL"


@pytest.mark.parametrize("name,lin,resumes,why", [
    ("thrice", CLEAN[:2] + [CLEAN[1], CLEAN[1]] + CLEAN[2:], 1, "a line occurs 3 times"),
    ("gap", CLEAN[:1] + CLEAN[:1] + CLEAN[1:3] + CLEAN[3:] + CLEAN[3:], 1, "are not one contiguous range"),
    ("stepback", [CLEAN[0], CLEAN[3], CLEAN[1], CLEAN[1], CLEAN[2], CLEAN[4]], 1, "step back in generation"),
    ("noresume", TWICE, 0, "holds no resume"),
    ("noplatform", TWICE, None, "holds no resume"),
])
def test_k_salt_refuses_duplicates_without_the_double_write_signature(tmp_path, name, lin, resumes, why):
    """Each test of the signature, failing alone, fails the comparison (K-SALT VOID) with its reason, and nothing is
    dropped."""
    a = _half(tmp_path / "a", CLEAN)
    v, lines = stages.half_compare(a, _half(tmp_path / name, lin, resumes), H_, upto=2)
    assert v == "FAIL"
    assert any(x.startswith("REFUSED:") and why in x for x in lines), lines
    assert "dropped" not in lines[0]


def test_a_waiting_writer_says_so_again_with_the_holders_pid(tmp_path):
    d = str(tmp_path / "run")
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(r)
        hold_run(d, log=None)
        os.write(w, b"x")
        time.sleep(2.6)
        os._exit(0)
    os.close(w)
    os.read(r, 1)
    said = []
    os.close(hold_run(d, log=said.append, every=1.0))
    os.waitpid(pid, 0)
    assert len(said) >= 2 and all(f"(pid {pid})" in s for s in said)


def test_run_job_waits_for_the_writer_before_it_restores(tmp_path, monkeypatch):
    """#504 S4: a live writer still in season 0 has no state.json, so the restore would unpack into its directory."""
    calls = []
    monkeypatch.setattr(stages, "_writer_gone", lambda d: calls.append(("wait", d)))
    monkeypatch.setattr(stages, "_restore", lambda d, probe="state.json": calls.append(("restore", d)))
    monkeypatch.setattr(stages, "_finished", lambda d, tag: True)
    d = str(tmp_path / "S")
    stages.run_job({"job": "resume", "name": "X/p/1/S", "dir": d, "seasons": 3})
    assert calls[:2] == [("wait", d), ("restore", d)]
