"""RBT-127: new runs record their platform in ``platform.json`` beside ``config.json`` (RBT-121 R13; auditor D, H48).

* An `evolve` run and an `ecology` run write the OS, CPU model, Python, MuJoCo and numpy versions and the git sha.
* ``config.json`` does not change: it carries no platform key, so RBT-113's golden digests and the salt-0 round trip
  still hold (they run in their own files; this file checks the key is absent).
* A resume appends its own platform under ``"resumes"``.
* Readers tolerate its absence: a committed pre-RBT-127 run reads as ``None``, and a population directory holding a
  ``platform.json`` does not offer it as a genotype.
"""
import json
import os
import platform
import subprocess

import mujoco
import numpy as np
import pytest

from rabbitstew.ecology import Ecology, EcologyConfig, population_files
from rabbitstew.evolution import EvolutionConfig, Experiment
from rabbitstew.provenance import PLATFORM_FILE, platform_record, read_platform
from rabbitstew.simulation import FoodConfig, SimConfig
from rabbitstew.world import WorldConfig

ROOT = os.path.join(os.path.dirname(__file__), "..")
KEYS = {"os", "os_release", "platform", "machine", "cpu_model", "python", "python_implementation", "mujoco", "numpy",
        "git_sha", "git_dirty", "written_utc"}


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


def test_an_evolve_run_writes_platform_json_and_leaves_config_json_alone(tmp_path):
    Experiment(_evo(), out_dir=str(tmp_path / "a"), log=None)
    _check(read_platform(str(tmp_path / "a")))
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
