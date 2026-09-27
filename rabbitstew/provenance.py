"""The platform a run was made on (RBT-127; RBT-121 R13, auditor D's P7 and H48).

A seed is not a full description of a run: RBT-96 found that 0 of 250 rows reproduce between ARM and x86,
and seed 201 is a runaway on one platform and a driver on the other.  So every new run writes
``platform.json`` beside its ``config.json``: the OS, the CPU model, the Python, MuJoCo and numpy versions,
and the git sha of the code (when the package sits in a git checkout).

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


def _git(*args: str) -> Optional[str]:
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        out = subprocess.run(["git", "-C", here, *args], capture_output=True, text=True, timeout=10)
    except Exception:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def platform_record() -> dict:
    """What a replay needs to know about the machine and the code, beyond the config."""
    sha = _git("rev-parse", "HEAD")
    dirty = _git("status", "--porcelain", "--untracked-files=no") if sha else None
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
        "git_dirty": None if dirty is None else bool(dirty),
        "written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def write_platform(out_dir: str) -> None:
    """Write ``platform.json`` for a new run in ``out_dir``."""
    with open(os.path.join(out_dir, PLATFORM_FILE), "w") as f:
        json.dump(platform_record(), f, indent=2)


def record_resume(out_dir: str) -> None:
    """Append this machine's record under ``"resumes"``; a pre-RBT-127 run gets a file holding only that list."""
    rec = read_platform(out_dir) or {}
    rec.setdefault("resumes", []).append(platform_record())
    with open(os.path.join(out_dir, PLATFORM_FILE), "w") as f:
        json.dump(rec, f, indent=2)


def read_platform(run_dir: str) -> Optional[dict]:
    """The run's platform record, or ``None`` for a run made before RBT-127 (or with the file missing or damaged)."""
    try:
        with open(os.path.join(run_dir, PLATFORM_FILE)) as f:
            rec = json.load(f)
    except (OSError, ValueError):
        return None
    return rec if isinstance(rec, dict) else None
