# RBT-129 legs adversary: PR #455 (`results/RBT-129-legs` at `9a71210`, base integration `ce69f17`)

**Verdict: MERGE AFTER FIXES.**
- There are two MUST items. Each is a one-line change in `stages.py`, followed by a re-emit.
- The launch record, the guard and the resume logic are otherwise sound.
- The runners never detach themselves.

**How it was checked.**
- **The trial merge** of #455 onto `ce69f17` is a **fast-forward** to `9a71210`, because integration has not moved.
  `stages.py verify` passes for both legs on that checkout.
- **The evidence:**
  - `probe_legs_verify.txt` runs the deviation matrix with the script `dev_matrix.sh`, which is inlined below it.
  - `suite_legs.txt` holds the full suite, run in a clean `.[dev]` venv without scipy.
- **Nothing ran on real hosts.** I ran only `verify` and the tests' fixtures: no prize or step bout, and no host
  restore.

## 1. The launch record and the `verify` guard

**What each leg's `launch.txt` records** (both at commit `4cdf8b9`):

| field | value |
|---|---|
| trees | `rabbitstew` `b3a29ba` (= `ce69f17`'s), `runs/RBT-129/launch` `9f617a6` (= this PR's, unchanged at `9a71210`), `scripts` `d517cf5` |
| fairness and eating | `--fair`; `--eat-from root --eat-rule surface` |
| cells | the 18 PAYS cells |
| tool blobs | `prize_gate.py` `c29611c`, `routed_populations.py` `af285fe`, **`steer.py` `1ecbbf9`**, `steps.py` `4834838` |

**Every deviation I tried is refused, except one** (both legs, same exit code):

| deviation | exit |
|---|---|
| none (clean `9a71210`) | 0 |
| `fair --unfair-i-know` (committed) | 4 |
| `eat --eat-from root` (committed) | 4 |
| `tree:rabbitstew` another tree (committed) | 5 |
| an uncommitted edit under `runs/RBT-129/launch` | 5 |
| `worlds/config/c1-p030-PW-G/config.json` motor budget 3.0 (committed) | 4 |
| `prize_gate.py` edited (committed) | 6 |
| `steer.py` edited (uncommitted) | 6 |
| `simulation.py` reverted to pre-#446 (uncommitted) | 5 |
| `simulation.py` pre-#446, committed, and `launch.txt`'s tree updated to match | **4** (the #446 capability probe) |
| a later commit touching `runs/RBT-129/launch/stages.py` (a stand-in for fix1) | 5 |
| **`worlds/c1-p030-PW-G.config.json` (the steps leg's input) motor budget 3.0 (committed)** | **0: accepted** |
| **the same file with `eat_rule` `centre` (committed)** | **0: accepted** |

**MUST L-1: `verify` never checks the steps leg's actual input.**
- `verify_leg` rebuilds and compares `worlds/config/<id>/config.json`. That is the prize leg's `--config-from`
  directory.
- The steps jobs, however, read `worlds/<id>.config.json`: `step_jobs` → `config_json_path`, which is `--config
  runs/RBT-129/worlds/<id>.config.json`.
- Nothing compares that file. `steps.py` itself checks only the `fairness` marker (S12), not the preset values or the
  eating rule.
- So a committed edit to that file (motor budget 3.0, or centre eating) passes every guard, and the step bouts would
  run unfair or on the wrong eating rule.
- **Fix, either of:**
  - point `step_jobs` at the verified directory: `--config runs/RBT-129/worlds/config/<id>`, which `steps.py` accepts
    as a directory;
  - or have `verify_leg` rebuild and compare `worlds/<id>.config.json` too.

  The first leaves one file per cell, not two.

**SHOULD S-1: pin only what each leg runs, and the whole import chain.**
- Both launch records pin `steer.py` `1ecbbf9`, which neither designed leg runs. B1 (in LEGS.md) needs `steer.py`
  changed for τ = 2 s. When that lands, every designed-leg runner restarted on the new tree would refuse with exit 6,
  although nothing it runs has changed.
- Conversely, `routed_populations.py` loads RBT-97's `routed_p801.py` and `g500_direction.py`. Neither is pinned
  (this was the R1 check's S3). Pin them.
- Pin per leg:
  - **prize leg:** `prize_gate.py`, `routed_populations.py`, `routed_p801.py`, `g500_direction.py`;
  - **steps leg:** the same four, plus `steps.py`.

**Does `verify` pass on the merge result, not only on `9a71210`?** Yes, today: the merge is a fast-forward. But it
will stop passing as soon as integration's `runs/RBT-129/launch`, `rabbitstew` or `scripts` tree moves. That happens
with fix1, for example (see §4). This is safe, since it fails loudly with exit 5, not silently.

**SHOULD S-2: run each leg from its launch commit, not from integration's head.** `launch.txt`'s `commit` line is the
leg's own commit, `4cdf8b9`. Stage P/0 already works this way: its `launch.txt` pins `rabbitstew` `69b5d6c`, and
integration has since moved to `b3a29ba`. LEGS.md's "sessions checked out at the merge" is fragile after a reclaim.

## 2. Parity with RBT-125's registered harness

**What matches.**
- **Prize hosts:** RBT-90's ten, 801, 804, 805, 806, 807, 1, 2, 3, 4 and 7, restored from `ckpt/rbt-90-SEED`.
- **Prize command:** `--w 3` (a = 6), `--procs 4`, and the harness's own 64 paired seeds from 7000 (not overridden).
- **Step hosts and seeds:** RBT-113 O1's 15 hosts through `hosts(HOSTS_ROOT)` with `default_rng(125)`, and the
  default 128 seeds from 125000.
- **Coverage:** 180 prize jobs (10 × 18), each emitted exactly once across the three runners (60 each), and 18 step
  jobs (6 each).
- **The flags that differ** are `--config-from worlds/config/<id>` and `--config`, which carry `--fair` and root +
  surface.

**MUST L-2: the decoy is missing.**
- RBT-125 §A's registered `run_gate.sh` runs the PW cells with `--decoy 3`: `prize $cell $s --decoy 3` for PW-G2.5,
  PW-G10 and PW-G0.
- Its PASS rule needs (motif − decoy) > 0, because "a prize that the decoy keeps is not a perception prize"
  (REGISTRATION §A).
- #455's prize jobs pass no `--decoy` at any cell, PW included. That is a parity difference beyond `--fair` and the
  eating rule.
- Without it, a designed PAYS at a PW cell can come from the installed motif's motor effect rather than from smell.
- **Fix:** add `--decoy 3` to the six PW cells' prize jobs, which is exact parity. Better, add it to all 18 cells, so
  PAYS is a perception prize everywhere. This adds cost, and the ruling says not to trim.

**The resume and promotion logic is sound.** Each job:
- skips if its final output already holds `^ROW` (or `^STEP`);
- otherwise writes `.tmp`, and promotes with `mv` only when the program **exits 0 and** the marker is present in
  `.tmp`.

What that guarantees:
- A killed or crashed run never reaches the `mv`. Its `.tmp` is overwritten on the next attempt (`>`).
- `mv` within one filesystem is atomic, so a partial output is never promoted.
- Each output is one file per (host, cell) or per cell. The runner split (`jobs[k::runners]`) is disjoint, and a
  restart skips promoted files, so nothing is double-counted.

**Caveats.**
- The first `FAILED` job stops the whole runner (`exit 1`), and a restart resumes from there.
- **SHOULD S-3: outputs are lost with a reclaimed container.** They live only in the container, and no durable
  snapshot or commit is taken. So a reclaim loses every promoted output of that runner, and the restart redoes them.
  Add a `scripts/durable.sh save` of the leg's `stage0/pays` subtree after each promotion, or every N jobs, with a
  restore at the top of the runner.

## 3. Container reclaim: no self-backgrounding

- **The scripts:** `runnerK.sh` for both legs contains no `nohup`, `setsid`, `disown` or trailing `&`.
- **The tools they call** run in the foreground:
  - `durable.sh restore`;
  - `prize_gate.py` and `steps.py`, which use a `multiprocessing` Pool and wait for it.

So each runner can be started as a harness background task, and it lives and dies with the session.

**SHOULD S-4: say how to start them.** LEGS.md says only "run `bash runs/RBT-129/lanes/…/runnerK.sh`". Given this
morning's loss, write it out: start each runner as a **harness background task** (the Bash tool's
`run_in_background`), one per session, **never `nohup`, `&` or `setsid`**. Reclaim is then handled by restarting the
same script, which resumes (§2).

## 4. A collision with the pending fix1 (`launch/RBT-129-P0-fix1`, a child of `716e2d3`)

**Status:** the fix1 branch is not on the remote yet, so this is an analysis, not a trial merge.

**Text: no conflict is expected in `stages.py`.**
- fix1 changes the snapshot and fork jobs, which live in `run_job` (around lines 540–600 on integration).
- #455's hunks are elsewhere:
  - new functions before `write_script` (`LEG_TOOLS`, `write_leg_launch`, `verify_leg`);
  - `write_script` itself;
  - the leg job builders, `prize_jobs`, `restore_hosts`, `step_jobs` and `restore_step_hosts` (around line 760 and
    after);
  - the argparse setup and `main`'s dispatch.
- **The one likely conflict** is `tests/test_rbt129_launch.py`. #455 rewrites 110 lines there, and if fix1 adds its
  test next to those, the two hunks can clash. That is easy to resolve.

**Trees: a guaranteed collision.**
- Whichever of #455 and fix1 merges second changes `runs/RBT-129/launch`'s tree.
- If fix1 merges after #455, the legs' launch records pin `9f617a6`, and their runners refuse with exit 5 on any
  checkout of the new integration. The probe's stand-in commit shows exactly this.
- Symmetrically, fix1's own re-emitted P/0 record would pin a tree that #455's merge changes.
- **Fix:** run the legs from `4cdf8b9`/`9a71210` (S-2), or re-emit both legs after fix1 merges (`stages.py
  pays-prize` / `pays-steps`, then commit). Either way, the refusal is loud, never silent.

## 5. The full suite

The trial merge (= `9a71210`) was run in a clean venv: `python -m venv`, then `pip install -e ".[dev]"`, with scipy
absent. Result (`suite_legs.txt`):

**706 passed, 1 skipped, 16 warnings in 11 min 2 s.**

The skip is , the scipy cross-check, which is expected without scipy.

## The list

**MUST**
- **L-1:** `verify` must cover the steps leg's actual input. Point `step_jobs` at `worlds/config/<id>` (verified), or
  verify `worlds/<id>.config.json` too.
- **L-2:** add `--decoy 3` to the prize jobs at the six PW cells (parity with RBT-125 §A's registered harness), or to
  all 18 cells.

Re-emit both legs after the fixes, and commit.

**SHOULD**
- **S-1:** pin per leg exactly the tools it runs. Drop `steer.py` from the designed legs, and add RBT-97's
  `routed_p801.py` and `g500_direction.py`.
- **S-2:** run each leg from its own launch commit, or re-emit after fix1 merges.
- **S-3:** snapshot the leg's outputs durably, so a reclaim does not redo promoted jobs.
- **S-4:** LEGS.md should say to start runners as harness background tasks, never `nohup`, `&` or `setsid`.

---
_Generated by [Claude Code](https://claude.ai/code)_
