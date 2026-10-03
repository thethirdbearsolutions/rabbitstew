"""RBT-129 continuations: the identity of the guard-off INSTRUMENTED MuJoCo 3.14.0 (owner decision 2, option (c):
``runs/RBT-129/coordinator/OWNER-DECISIONS-2026-10-03.md``).

Every RBT-129 continuation (R-B, Stage 2, the M/N silent-corruption scan) runs on this build and nothing else.  The
build is stock MuJoCo 3.14.0 plus ``runs/RBT-129/continuations/build/mujoco-3.14.0-rbt129-epa-log.patch``, which only
counts and logs EPA horizon sizes (no guard: the 24-entry horizon arrays overflow exactly as in stock).  It is made by
``scripts/build_mujoco_instrumented.sh``.

``mujoco.__version__`` reads "3.14.0" under both builds, so the version is not the identity.  ``check_instrumented``
holds the process to three things at once:
  1. the installed distribution and the imported module are MuJoCo 3.14.0 (as ``stages.check_mujoco``);
  2. the ``libmujoco.so.3.14.0`` this process has actually mapped (``/proc/self/maps``) hashes to ``INSTR_SO_SHA``,
     the recipe's output;
  3. that library answers ``rbt_hzn_build_id()`` with ``BUILD_ID``, a marker no stock library carries.
Any failure is refused with exit 9, the MuJoCo pin's exit code (``stages.check_mujoco``).
"""
import hashlib
import importlib.metadata
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

MUJOCO_VERSION = "3.14.0"
#: google-deepmind/mujoco tag 3.14.0
MUJOCO_COMMIT = "9ecbb9d7b5ee623f54745638d36799ff90e6f7cd"
LIB = "libmujoco.so.3.14.0"
PATCH = os.path.join(ROOT, "runs", "RBT-129", "continuations", "build", "mujoco-3.14.0-rbt129-epa-log.patch")
#: keep these three in step with scripts/build_mujoco_instrumented.sh (a test checks it)
PATCH_SHA = "06877b1162b419d1c853d7119d658c7dbaab92a5e233357cd1da96345f8b55b5"
STOCK_SO_SHA = "5e7623e30f55bf324d4c9648379ebeba5bcd153ee0304c52eac74bf8d441000b"
INSTR_SO_SHA = "7ae75f7fe32e437b2c7283930f38f20adfa33bbe4895c5d91b0c95233814edb8"
#: what the patched library's ``rbt_hzn_build_id()`` returns (engine_rbt_hzn.c's RBT_HZN_ID)
BUILD_ID = f"rbt129-epa-instr/1 mujoco {MUJOCO_VERSION} {MUJOCO_COMMIT} guard-off count-and-log"
#: the build as launch.txt's ``mujoco_build`` line and each run's platform.json record it
BUILD_LINE = f"{BUILD_ID} sha256:{INSTR_SO_SHA}"
#: the near-miss threshold the log uses (the coordinator's brief: horizon >= 17); the cap is the stock arrays' 24
NEAR = 17
CAP = 24
#: the per-run event log, beside the run's other files (saved with it to its checkpoint branch)
EPA_LOG = "epa_overflow.jsonl"


def _refuse(msg: str, code: int = 9):
    print(f"REFUSED: {msg}", file=sys.stderr, flush=True)
    raise SystemExit(code)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def loaded_libs(maps: str = "/proc/self/maps") -> list:
    """The distinct paths of every ``libmujoco.so.3.14.0`` this process has mapped."""
    out = []
    try:
        with open(maps) as f:
            for line in f:
                parts = line.split(None, 5)
                if len(parts) == 6 and os.path.basename(parts[5].strip()) == LIB and parts[5].strip() not in out:
                    out.append(parts[5].strip())
    except OSError:
        pass
    return out


def build_id(path: str):
    """``rbt_hzn_build_id()`` of the library at ``path`` (None for a library without it, as stock is)."""
    import ctypes

    try:
        fn = ctypes.CDLL(path).rbt_hzn_build_id
    except (OSError, AttributeError):
        return None
    fn.restype = ctypes.c_char_p
    return fn().decode()


def identity() -> dict:
    """What this process runs: the mapped libmujoco (exactly one), its sha256 and its build marker."""
    import mujoco  # noqa: F401  (maps the library)

    libs = loaded_libs()
    if len(libs) != 1:
        _refuse(f"this process maps {len(libs)} {LIB} libraries ({libs}), not exactly one")
    return {"build_id": build_id(libs[0]), "libmujoco_sha256": sha256(libs[0]), "libmujoco_path": libs[0],
            "mujoco": getattr(mujoco, "__version__", None), "patch_sha256": PATCH_SHA}


def check_instrumented() -> dict:
    """Refuse (exit 9) unless this process runs the instrumented build (module docstring); return its identity."""
    try:
        v = importlib.metadata.version("mujoco")
    except importlib.metadata.PackageNotFoundError:
        v = None
    if v != MUJOCO_VERSION:
        _refuse(f"MuJoCo {v or '(not installed)'} is installed; RBT-129 continuations run on the instrumented MuJoCo"
                f" {MUJOCO_VERSION} only (scripts/build_mujoco_instrumented.sh)")
    ident = identity()
    if ident["mujoco"] != v:
        _refuse(f"the mujoco module imported here is {ident['mujoco']!r}, not the installed distribution's {v}")
    if ident["libmujoco_sha256"] != INSTR_SO_SHA:
        kind = "the stock pip wheel's" if ident["libmujoco_sha256"] == STOCK_SO_SHA else "an unknown"
        _refuse(f"{ident['libmujoco_path']} is {kind} libmujoco (sha256 {ident['libmujoco_sha256']}), not the instrumented"
                f" build's {INSTR_SO_SHA}: an RBT-129 continuation refuses to start on it"
                " (OWNER-DECISIONS-2026-10-03 item 2; scripts/build_mujoco_instrumented.sh)")
    if ident["build_id"] != BUILD_ID:
        _refuse(f"{ident['libmujoco_path']} answers rbt_hzn_build_id() with {ident['build_id']!r}, not {BUILD_ID!r}")
    return ident


def check_build_line(line: str) -> None:
    """A launch's ``mujoco_build`` line must be this module's ``BUILD_LINE`` (exit 9 otherwise)."""
    if line != BUILD_LINE:
        _refuse(f"launch.txt's mujoco_build {line!r} is not this tree's {BUILD_LINE!r}: re-emit the lanes")
