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

## Fix-check (d8ef5cb4)

**Verdict: MERGE.** No MUST items remain.

Base is 9edecbd. Commit d8ef5cb4 changes only `runs/RBT-129/launch/stages.py` and `tests/test_rbt129_launch.py`, and adds this review as `runs/RBT-129/mujoco-pin-adversary/ADVERSARY.md`. It touches nothing under `rabbitstew/` and does not change `pyproject.toml`.

### Claims

**M1. Verified.**
- `test_run_lane_refuses_another_tree` now pins 3.14.0 through `_mujoco_is`.
- The autouse `surface_clearance` fixture runs the launcher tests on the pinned version.
- The only other place that reaches `check_host` is `tests/test_rbt129_mn.py:490`, which patches it out.
- Venv with mujoco 3.3.7: the launch, mn, mn-emitter-adversary, rbt129c and resume_lock tests give **177 passed, 1 skipped**. This matches the author's count.

**S2. Verified.**
- `check_surface_clearance` calls `check_mujoco()` first, whatever the eating rule.
- Every emitter reaches `check_surface_clearance` before it writes worlds or lanes, or simulates anything:
  - `emit`, `emit_lanes` (used by `screen-emit`, `stage1-emit`, `fork-source-emit` and `mn-emit`), `prelaunch`, `pays-prize`, `pays-steps`, `pays-steps2`, `calibrate`, `probes` and `pays`;
  - before it, they run only `rel`, `check_fair`, `check_eat` and `check_steer`, which do no physics and write nothing;
  - `screen_units(a.root)`, evaluated before `emit_lanes`, is pure.
- `stage1-emit`, `fork-source-emit` and `mn-emit` also call `check_mujoco()` before `screen_gate` / `mn_plan`.
- **Mutation reasoning.** If the call is dropped from `check_surface_clearance`, or the early calls are dropped from `mn-emit` / `stage1-emit`, the new test fails, because `surface_clearance_ok`, `screen_gate` and `mn_plan` are patched to `pytest.fail`.
- **Read-side.** `screen-table`, `mn-rank`, `check-branches`, `calib-extract`, `save` and the readout scripts never reach the check.

**S3. Verified.**
- `check_mujoco` requires `mujoco.__version__` to equal the metadata version, and exits 9 otherwise.
- The real 3.14.0 wheel reports `3.14.0` for both. The 3.3.7 wheel reports `3.3.7` for both.
- The test is parametrised over 3.3.7, 3.14.1 and None.

**S4. Verified.** The `X86` `skipif` is applied to the run-lane / verify exit-9 test.

### Re-attack

**Does the autouse fixture hide a real failure? No.**
- It fakes only the version report, and only in `test_rbt129_launch.py`.
- The pin's own tests set the version explicitly.
- Physics byte-identity lives in other files, which do not use this fixture.

**Is there any lane write or simulation before the check? None found.**

### Nits

- **N1.** At `tests/test_rbt129_launch.py:1401` (`test_the_emitters_refuse_another_mujoco_before_they_simulate_or_write`), the lambdas capture `name` late. Every failure message would say "plan". This is cosmetic; fix it with `lambda *a, n=name, **k:`.
- **N2.** S1 is still open: the second-host diagnosis in ruling item 7 runs ecology directly and is not guarded by the tool. That is a procedural matter for the diagnosis brief, not a blocker for this PR.

### The 12 failures on 3.3.7 already fail on base

Full suite on mujoco 3.3.7 at d8ef5cb4: **12 failed, 912 passed, 1 skipped**.
- All 12 are physics byte-identity tests in `test_rbt113`, `test_rbt120`, `test_rbt124`, `test_rbt125`, `test_rbt126`, `test_rbt130` and `test_rbt131`. This PR touches none of these files.
- **Spot-check on base 9edecbd** under 3.3.7, with `PYTHONPATH` set so `rabbitstew` was imported from the base worktree, on six of them:
  - `test_rbt113::test_default_is_byte_identical_to_the_pre_hook_code[extra0,1,2]`
  - `test_rbt124::test_a_self_jammed_body_is_flagged_not_settled`
  - `test_rbt125::test_off_is_byte_identical_to_the_pre_pack_code`
  - `test_rbt131::test_a_fresh_run_writes_final_byte_for_byte_as_before`
- **All 6 also fail on base.** The failures come from the MuJoCo version, not from this PR.

### Full suite on 3.14.0

Clean venv, Python 3.11, `pip install -e ".[dev]"`, no scipy.

`924 passed, 1 skipped (scipy), 16 warnings in 865s.`
