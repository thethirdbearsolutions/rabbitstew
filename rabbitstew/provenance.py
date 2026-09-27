"""The platform a run was made on (RBT-127; RBT-121 R13, auditor D's P7 and H48).

A seed is not a full description of a run: RBT-96 found that 0 of 250 rows reproduce between ARM and x86,
and seed 201 is a runaway on one platform and a driver on the other.  So every new run writes
``platform.json`` beside its ``config.json``: the OS, the CPU model, the Python, MuJoCo and numpy versions,
and the git sha of the code (only when this package's own source is tracked in the checkout it sits in;
otherwise ``None``, never a surrounding repository's sha).

It is a sibling file, not a ``config.json`` section, because ``config.json`` is byte-pinned: RBT-113's
golden digests (``tests/test_rbt113.py``) and the salt-0 round trip (``tests/test_salt0_golden.py``) hold
a default run's ``config.json`` to what the pre-hook code wrote, and a platform section would move those
bytes on every machine and every commit.

Runs made before RBT-127 have no ``platform.json``; :func:`read_platform` returns ``None`` for them.  A
resume appends its own platform under ``"resumes"``, so a run continued on another machine says so.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from typing import Optional

PLATFORM_FILE = "platform.json"


def _cpu_model() -> str:
    """The CPU's marketing name where the OS offers one; otherwise what ``platform`` knows."""
    try:
        if sys.platform.startswith("linux"):
            with open("/proc/cpuinfo") as f:
                fields = dict(line.split(":", 1) for line in f if ":" in line)
            fields = {k.strip(): v.strip() for k, v in fields.items()}
            for key in ("model name", "Model", "Hardware", "cpu model", "Processor"):
                if fields.get(key):
                    return fields[key]
        elif sys.platform == "darwin":
            out = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True, timeout=5)
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
    except Exception:
        pass
    return platform.processor() or platform.machine()


def _version(module: str) -> Optional[str]:
    try:
        return __import__(module).__version__
    except Exception:
        return None


_HERE = os.path.dirname(os.path.abspath(__file__))
# An inherited GIT_DIR or GIT_WORK_TREE would silently point `git -C` at another repository.
_GIT_ENV_DROP = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY", "GIT_CEILING_DIRECTORIES")


def _git(*args: str) -> Optional[str]:
    env = {k: v for k, v in os.environ.items() if k not in _GIT_ENV_DROP}
    try:
        out = subprocess.run(["git", "--no-optional-locks", "-C", _HERE, *args], capture_output=True, text=True, timeout=10, env=env)
    except Exception:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def _checkout_sha() -> tuple:
    """(sha, dirty) of the checkout this package's own source file is tracked in, else (None, None).

    A package installed into a venv that sits inside some other work tree (a ``.venv/`` in this checkout, or
    anywhere in an unrelated repository) is *in* that work tree but not *tracked* by it, so the tracked-file
    guard refuses it rather than recording the surrounding repository's HEAD.  ``--no-optional-locks`` keeps
    the dirty check from taking ``index.lock`` while an arm's launcher commits in the same checkout.
    """
    if _git("ls-files", "--error-unmatch", os.path.basename(__file__)) is None:
        return None, None
    sha = _git("rev-parse", "HEAD")
    if not sha:
        return None, None
    dirty = _git("status", "--porcelain", "--untracked-files=no")
    return sha, None if dirty is None else bool(dirty)


def _installed_commit() -> Optional[str]:
    """The commit pip recorded when the package was installed from a VCS URL (``direct_url.json``), if any."""
    try:
        from importlib.metadata import distribution

        raw = distribution("rabbitstew").read_text("direct_url.json")
        return (json.loads(raw).get("vcs_info") or {}).get("commit_id") if raw else None
    except Exception:
        return None


def _write(out_dir: str, rec: dict) -> None:
    path = os.path.join(out_dir, PLATFORM_FILE)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(rec, f, indent=2)
    os.replace(tmp, path)  # atomic, as state.json is written: a killed write never leaves a torn record


def platform_record() -> dict:
    """What a replay needs to know about the machine and the code, beyond the config."""
    sha, dirty = _checkout_sha()
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_model": _cpu_model(),
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "mujoco": _version("mujoco"),
        "numpy": _version("numpy"),
        "git_sha": sha,
        "git_dirty": dirty,
        "installed_commit": _installed_commit(),
        "written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def write_platform(out_dir: str) -> None:
    """Write ``platform.json`` for a new run in ``out_dir``."""
    _write(out_dir, platform_record())


def record_resume(out_dir: str) -> None:
    """Append this machine's record under ``"resumes"``; a pre-RBT-127 run gets a file holding only that list."""
    rec = read_platform(out_dir) or {}
    rec.setdefault("resumes", []).append(platform_record())
    _write(out_dir, rec)


def read_platform(run_dir: str) -> Optional[dict]:
    """The run's platform record, or ``None`` for a run made before RBT-127 (or with the file missing or damaged)."""
    try:
        with open(os.path.join(run_dir, PLATFORM_FILE)) as f:
            rec = json.load(f)
    except (OSError, ValueError):
        return None
    return rec if isinstance(rec, dict) else None
