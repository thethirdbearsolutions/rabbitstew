"""RBT-131: ``<kind>/final/`` holds exactly the living population, also after a resume or a fork.

``Ecology._save_populations`` wrote one file per member when a run ended and never cleared the directory, so a resumed
or forked run whose population shrank kept the earlier run's surplus (dead) members in ``final/``, and anything reading
``final/`` sampled them.  The member files are now cleared before they are written.

* Resume: a run stopped before its cull and resumed through it leaves ``final/`` equal to the state's population and
  byte-identical to the straight run's.  Fails before the fix (the stopped run's surplus files stay).
* Fork: a finished run copied, given a cull in its config and resumed, likewise.
* A fresh run is byte-identical: every file of ``final/`` against digests recorded on the pre-fix code.
"""
import hashlib
import json
import platform
import shutil

import pytest

from rabbitstew.ecology import Ecology
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC

from test_ecology_switches import _eco, _evo

CULL = dict(cull_at=2, cull="holistic=3,conventional=2")


def _final(out, kind):
    return sorted((out / kind / "final").iterdir())


def _living(out, kind):
    return json.loads((out / "state.json").read_text())["populations"][kind]


def _assert_final_is_the_living(out):
    for kind in (HOLISTIC, CONVENTIONAL):
        files, living = _final(out, kind), _living(out, kind)
        assert [p.name for p in files] == [f"{i:03d}.json" for i in range(len(living))]
        assert [json.loads(p.read_text())["name"] for p in files] == [m["name"] for m in living]


def test_a_resume_through_a_cull_leaves_only_the_living_in_final(tmp_path):
    straight = tmp_path / "straight"
    Ecology(_evo(), _eco(seasons=4, capacity=6, **CULL), out_dir=str(straight), log=None).run()
    out = tmp_path / "resumed"
    Ecology(_evo(), _eco(seasons=2, capacity=6, **CULL), out_dir=str(out), log=None).run()
    before = {kind: len(_final(out, kind)) for kind in (HOLISTIC, CONVENTIONAL)}
    Ecology.resume(str(out), seasons=4, log=None).run()
    after = {kind: len(_living(out, kind)) for kind in (HOLISTIC, CONVENTIONAL)}
    assert all(after[k] < before[k] for k in before), (before, after)  # the population shrank across the resume
    _assert_final_is_the_living(out)
    for kind in (HOLISTIC, CONVENTIONAL):
        assert [p.read_bytes() for p in _final(out, kind)] == [p.read_bytes() for p in _final(straight, kind)]


def test_a_fork_into_a_cull_leaves_only_the_living_in_final(tmp_path):
    base = tmp_path / "base"
    Ecology(_evo(), _eco(seasons=2, capacity=6), out_dir=str(base), log=None).run()
    fork = tmp_path / "fork"
    shutil.copytree(base, fork)  # as runs/RBT-107/fork.py does
    cfg = json.loads((fork / "config.json").read_text())
    cfg["ecology"].update(CULL)
    (fork / "config.json").write_text(json.dumps(cfg, indent=2))
    (fork / HOLISTIC / "final" / "notes.txt").write_text("not a member")
    Ecology.resume(str(fork), seasons=4, log=None).run()
    for kind in (HOLISTIC, CONVENTIONAL):
        assert len(_living(fork, kind)) < len(_final(base, kind))
    assert (fork / HOLISTIC / "final" / "notes.txt").read_text() == "not a member"  # only member files are cleared
    (fork / HOLISTIC / "final" / "notes.txt").unlink()
    _assert_final_is_the_living(fork)


FRESH = {  # sha256 of every final/ file of a fresh run, recorded on the pre-fix code (01f113d), x86_64
    "holistic/final/000.json": "b9781ff481e118c1fe50bd0fafd53c26b29c19f1d53d18be242a78c157d98300",
    "holistic/final/001.json": "b46e8014d432806d210ffa6f304a8efd31050c8b7b951d5fa27f7fc8d327acf2",
    "holistic/final/002.json": "408b4027957717b0bfe58b7ba42fce604bc7709d98537149a0238bf791d942ea",
    "conventional/final/000.json": "9cbf092c968bbd2a2242baf885dc58bbc8d5f361d276fecdc5ae6ba532a65848",
    "conventional/final/001.json": "4db084f8491e18363c149ff2c91555ed6c8c8df3a8ffda7c1c2dff6d55778458",
    "conventional/final/002.json": "d9a0dfa89621fb3443c27508308838918c2caac72f08503349b72a3a17486eab",
    "conventional/final/003.json": "b482be1505e1e3bc4a90468984073669c3860d2c1461a9cdf566635ce242d54b",
}


def _digests(out):
    return {f"{kind}/final/{p.name}": hashlib.sha256(p.read_bytes()).hexdigest()
            for kind in (HOLISTIC, CONVENTIONAL) for p in _final(out, kind)}


@pytest.mark.skipif(platform.machine() != "x86_64", reason="digests recorded on x86_64 (RBT-96)")
def test_a_fresh_run_writes_final_byte_for_byte_as_before(tmp_path):
    Ecology(_evo(), _eco(seasons=4, capacity=6, **CULL), out_dir=str(tmp_path / "fresh"), log=None).run()
    assert _digests(tmp_path / "fresh") == FRESH
