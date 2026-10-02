# Adversary review: PR #511 "RBT-129 MuJoCo pin" (head 0ed649d1)

**Verdict: MERGE AFTER FIXES** (one test fix).

Spec: RULING.md item 6. Every remaining RBT-129 launch refuses any installed MuJoCo other than 3.14.0, as `importlib.metadata.version("mujoco")` reports it. `pyproject.toml` stays unchanged.

## MUST

**M1. An existing test fails whenever MuJoCo is not 3.14.0.** `tests/test_rbt129_launch.py:587` (`test_run_lane_refuses_another_tree`) expects exit 5. `check_host` now runs `check_mujoco` (`runs/RBT-129/launch/stages.py:388`) before the tree checks.

- **Reproduced.** In a venv with mujoco 3.3.7, which `pyproject.toml`'s `mujoco>=3.1` allows:
  - the test fails with `assert 9 == 5`;
  - `tests/test_rbt129_launch.py`, `tests/test_rbt129_mn.py` and `runs/RBT-129/mn-emitter-adversary/test_adversary.py` together give 1 failed, 97 passed, 1 skipped.
- **Failure scenario.** Any developer on another MuJoCo, or every installation once 3.14.1 is published (3.14.0 is the newest today), gets a red suite. A red suite hides real L2 regressions.
- **Fix.** In that test, call `_mujoco_is(monkeypatch, "3.14.0")`, or patch `stages.check_mujoco` to a no-op. Audit any other test that reaches `check_host` without patching it. I found only this one; the others monkeypatch `check_host`.

## Checked and OK

**Coverage.** Two paths run ecology or physics jobs, and both pass through `check_host`:

- `run-lane` (`stages.py:981`). Ecology runs with `sys.executable`, the same interpreter that ran the check.
- Every leg script that `write_script(..., launch)` writes. This covers `probes`, `pays`, `pays-prize`, `pays-steps`, `pays-steps2` and `calibrate`.
  - The script runs `stages.py verify` under `set -e` before any job, using the same `python` on PATH as its jobs.
  - Every caller passes `launch`.
  - Scripts already committed also call the HEAD `verify`.

Remaining stages emit lanes that `run-lane` runs: `stage1-emit`, `mn-emit`, `fork-source-emit` (the anchor fallback), and Stage 2 / R-B / retention. The emitters themselves launch nothing. I found no bypass.

**Exit code.** No collision.

- `stages.py` otherwise uses exits 1, 3, 4, 5, 6, 7 and 8.
- `check-branches` returns 0 or 1.
- `rabbitstew/cli.py` uses only string `SystemExit`, which exits 1.

**Read-side.** Not affected. `check_host` is called only from `run_lane` and `verify_leg`. The readout scripts, `resumed.py` and `check-branches` never reach it.

**Version strings.** The check is exact string equality. It refuses `3.14.0.post1`, `3.14`, `3.14.0rc1`, local `+` builds and a missing MuJoCo. This matches "any other than 3.14.0", and `platform.json` (`provenance.py:118`) records the version by the same method.

**New tests.**

- They are adequate: version parametrisation, both entry points (`run-lane`, `verify`), and a job sentinel.
- They catch removal of the `check_host` call.

## SHOULD

- **S1.** The second-host diagnosis in item 7 runs ecology directly, outside `run-lane`, so it is unguarded. Its procedure should require `check_mujoco`, or a manual `pip show mujoco` == 3.14.0, before it runs.
- **S2.** Refuse early at emit time: in `emit_lanes` / `mn-emit`, or with a warning. Today a wrong MuJoCo is caught only at `run-lane`, after `check_surface_clearance` has already simulated on the wrong physics.
- **S3.** `importlib.metadata` can disagree with the module actually imported, for example with stale dist-info or a source build on PYTHONPATH. Optionally also check `mujoco.__version__` (the ruling's method stays the primary check).
- **S4.** The new test's final step, `check_host({})` returning exit 5, and the run-lane exit-9 assertion both assume x86_64. On another machine they would get exit 3. This matches existing tests, so a skipif marker would be enough.

## Full suite

Clean venv `/tmp/v511`, Python 3.11, `pip install -e ".[dev]"`, no scipy. MuJoCo resolved to 3.14.0.

`920 passed, 1 skipped (scipy), 16 warnings in 909s.`

The pass depends on MuJoCo being 3.14.0 (see M1).
