"""RBT-127: new runs record their platform in ``platform.json`` beside ``config.json`` (RBT-121 R13; auditor D, H48).

* An `evolve` run and an `ecology` run write the OS, CPU model, Python, MuJoCo and numpy versions and the git sha.
* ``config.json`` does not change: it carries no platform key, so RBT-113's golden digests and the salt-0 round trip
  still hold (they run in their own files; this file checks the key is absent).
* A resume appends its own platform under ``"resumes"``; the file is written atomically.
* The git sha is this package's own checkout's or ``None``: never a surrounding repository's (a venv inside another
  work tree) and never one an inherited ``GIT_DIR`` points at (RBT-127 adversary S-code-1).
* Readers tolerate its absence: a committed pre-RBT-127 run reads as ``None``, and a population directory holding a
  ``platform.json`` does not offer it as a genotype.
"""
import importlib.util
import json
import os
import platform
import shutil
import subprocess

import mujoco
import numpy as np
import pytest

from rabbitstew.ecology import Ecology, EcologyConfig, population_files
from rabbitstew.evolution import EvolutionConfig, Experiment
import rabbitstew.provenance as provenance
from rabbitstew.provenance import PLATFORM_FILE, platform_record, read_platform
from rabbitstew.simulation import FoodConfig, SimConfig
from rabbitstew.world import WorldConfig

ROOT = os.path.join(os.path.dirname(__file__), "..")
KEYS = {"os", "os_release", "platform", "machine", "cpu_model", "python", "python_implementation", "mujoco", "numpy",
        "git_sha", "git_dirty", "installed_commit", "written_utc"}


def _evo(seed=11):
    return EvolutionConfig(seed=seed, population_size=2, generations=1, brain_model="foraging", conventional_topology=True,
                           sim=SimConfig(duration=0.3, random_start=True, score="food", world=WorldConfig(terrain="random"),
                                         food=FoodConfig(items=4, radius=1.5, eat_radius=0.4)))


def _eco(seasons):
    return EcologyConfig(seasons=seasons, capacity=4, challenge="foraging", group_size=2, max_age=1000, birth_threshold=100.0, log_every=1000)


def _check(rec):
    assert set(rec) >= KEYS
    assert rec["os"] == platform.system() and rec["machine"] == platform.machine()
    assert rec["python"] == platform.python_version()
    assert rec["mujoco"] == mujoco.__version__ and rec["numpy"] == np.__version__
    assert isinstance(rec["cpu_model"], str) and rec["cpu_model"]


def test_the_record_names_the_platform_and_the_code():
    rec = platform_record()
    _check(rec)
    try:
        head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
    except OSError:
        pytest.skip("no git on this machine")
    if head.returncode != 0:
        assert rec["git_sha"] is None and rec["git_dirty"] is None  # not a checkout: recorded as unknown, not guessed
    else:
        assert rec["git_sha"] == head.stdout.strip() and isinstance(rec["git_dirty"], bool)


def _clean_git(*args, cwd):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, env=env,
                          capture_output=True, text=True, check=True).stdout.strip()


def _repo(path):
    path.mkdir()
    _clean_git("init", "-q", cwd=path)
    (path / "README").write_text("x")
    _clean_git("add", "README", cwd=path)
    _clean_git("commit", "-qm", "outer", cwd=path)
    return path


def _load_copy(dest):
    """Import a copy of provenance.py from `dest`, as if the package were installed there."""
    dest.mkdir(parents=True)
    shutil.copy(provenance.__file__, dest / "provenance.py")
    spec = importlib.util.spec_from_file_location("provenance_copy", dest / "provenance.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.skipif(shutil.which("git") is None, reason="no git on this machine")
def test_a_package_inside_someone_elses_work_tree_records_no_sha(tmp_path):
    outer = _repo(tmp_path / "outer")
    mod = _load_copy(outer / ".venv" / "site-packages" / "rabbitstew")  # in the work tree, not tracked by it
    rec = mod.platform_record()
    assert rec["git_sha"] is None and rec["git_dirty"] is None
    _clean_git("add", "-f", ".venv/site-packages/rabbitstew/provenance.py", cwd=outer)  # tracked: its checkout's sha
    _clean_git("commit", "-qm", "track it", cwd=outer)
    rec = mod.platform_record()
    assert rec["git_sha"] == _clean_git("rev-parse", "HEAD", cwd=outer) and rec["git_dirty"] is False


@pytest.mark.skipif(shutil.which("git") is None, reason="no git on this machine")
def test_an_inherited_git_dir_does_not_redirect_the_sha(tmp_path, monkeypatch):
    before = platform_record()["git_sha"]
    other = _repo(tmp_path / "other")
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(other))
    rec = platform_record()
    assert rec["git_sha"] == before
    assert rec["git_sha"] != _clean_git("rev-parse", "HEAD", cwd=other)


def test_an_evolve_run_writes_platform_json_and_leaves_config_json_alone(tmp_path):
    Experiment(_evo(), out_dir=str(tmp_path / "a"), log=None)
    _check(read_platform(str(tmp_path / "a")))
    assert not (tmp_path / "a" / (PLATFORM_FILE + ".tmp")).exists()  # written through a temp file and os.replace
    raw = (tmp_path / "a" / "config.json").read_text()
    assert not any(f'"{k}"' in raw for k in ("cpu_model", "mujoco", "git_sha", "platform"))
    assert json.loads(raw) == json.loads(json.dumps(EvolutionConfig.from_dict(json.loads(raw)).to_dict()))


def test_an_ecology_run_writes_it_and_a_resume_appends_its_own(tmp_path):
    out = tmp_path / "eco"
    Ecology(_evo(), _eco(2), out_dir=str(out), log=None).run()
    first = read_platform(str(out))
    _check(first)
    assert "resumes" not in first
    assert "platform" not in json.loads((out / "config.json").read_text())
    Ecology.resume(str(out), seasons=3, log=None).run()
    after = read_platform(str(out))
    assert {k: after[k] for k in KEYS} == {k: first[k] for k in KEYS}  # the run's own record is kept
    assert len(after["resumes"]) == 1
    _check(after["resumes"][0])


def test_a_pre_rbt127_run_reads_as_none_and_resumes_with_only_its_resume_recorded(tmp_path):
    assert read_platform(os.path.join(ROOT, "runs", "RBT-85", "base-201")) is None  # committed before RBT-127
    assert read_platform(str(tmp_path)) is None
    (tmp_path / PLATFORM_FILE).write_text("{torn")
    assert read_platform(str(tmp_path)) is None
    out = tmp_path / "old"
    Ecology(_evo(), _eco(1), out_dir=str(out), log=None).run()
    (out / PLATFORM_FILE).unlink()  # as a run made before RBT-127 left it
    Ecology.resume(str(out), seasons=2, log=None).run()
    rec = read_platform(str(out))
    assert set(rec) == {"resumes"}
    _check(rec["resumes"][0])


def test_a_population_directory_does_not_offer_platform_json_as_a_genotype(tmp_path):
    Ecology(_evo(), _eco(1), out_dir=str(tmp_path), log=None).run()
    final = tmp_path / "holistic" / "final"
    (final / PLATFORM_FILE).write_text((tmp_path / PLATFORM_FILE).read_text())  # a copied run directory, say
    assert PLATFORM_FILE not in {os.path.basename(f) for f in population_files(str(tmp_path), "holistic")}
    assert PLATFORM_FILE not in {os.path.basename(f) for f in population_files(str(final), "holistic")}
