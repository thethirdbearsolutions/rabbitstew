# RBT-129 continuations: the instrumented build, run-lane, the M/N scan, R-B

*Owner decisions of 2026-10-03 (`../coordinator/OWNER-DECISIONS-2026-10-03.md`, merged in #522):*
- **(1)** a Stage-1 silent-corruption scan, M and N first;
- **(2)** every RBT-129 continuation runs on **option (c)**: a guard-off, instrumented MuJoCo 3.14.0 that is
  byte-identical to stock on trajectories without an overflow (at and after one, both builds are in undefined
  behaviour and nothing is claimed: COORD-RULING-520 D3, FC-2) and logs every EPA horizon overflow;
- **(3)** R-B is GO (`RBT129-RB-GO-1`), gated on that build and on a registered overflow rule.

*Coordinator: `session_017eUHGNdTSsoVFAtLaJWehF`.*

**Nothing here was launched.** The only runs made here are the build-identity runs (`IDENTITY.md`) and the scan smoke
test on 2 units (`SMOKE.md`).

## Files

| file | what |
|---|---|
| `../../../scripts/build_mujoco_instrumented.sh` | the build recipe: `instr OUT_VENV` builds and installs it, `stock OUT_VENV` makes the reference venv |
| `build/mujoco-3.14.0-rbt129-epa-log.patch` | the patch: count and log only, no guard |
| `../launch/mjbuild.py` | the build's identity and its check (`check_instrumented`) |
| `../launch/epa_ecology.py` | a continuation's ecology entry point: build check, `platform.json` record, the EPA log; `read_log` |
| `../launch/stages.py` | `run-lane`'s continuation gate; `rb-emit`, `scan-emit`, `scan-report`; job kind `scancmp` |
| `identity.sh` | stock vs instrumented, byte for byte, on Stage-1 units from their ckpt60 |
| `forced_overflow.py` | a forced EPA overflow (upstream #3646's pair) at WORKERS=2: start, overflow, `pool_broken` and exit lines, attestation, worker histograms |
| `records/` | raw output of the identity runs and the forced overflow |
| `IDENTITY.md` | the build's provenance, its reproduction, and the identity result |
| `SMOKE.md` | the scan's smoke test on 2 units |
| `OVERFLOW-RULE-DRAFT.md` | the overflow rule, a draft for the coordinator to rule on |
| `../lanes/RB/`, `../lanes/SCAN/` | the emitted lanes, not launched |
| `../../../tests/test_rbt129_continuations.py` | the tests |

## 1. The build (option (c))

- **The patch.** `build/mujoco-3.14.0-rbt129-epa-log.patch` applies to tag 3.14.0 (`9ecbb9d7`).
  - It adds `src/engine/engine_rbt_hzn.{c,h}` and two calls:
    - `rbt_hzn_observe(...)` in `epa`, right after `horizon(pt, face)`;
    - `rbt_hzn_step(...)` at the top of `mj_step`.
  - It **removes no line**. `addEdge` still writes past the 24-entry arrays, as stock does. The hooks only read their
    arguments and write their own statics and the log file. They never touch `mjModel`, `mjData`, the polytope or the
    FP environment.
  - A test (`test_the_patch_only_adds_and_has_no_guard`) holds the patch to this.
- **The log.** With `RBT_HZN_LOG=<file>`, the library appends one JSON line per EPA iteration whose horizon has
  **≥ 17 edges** ("near") or **> 24** ("overflow").
  - Each line has: the horizon size, the EPA iteration, the vertex and face counts, the geom pair (ids and types), the
    `mj_step` within the bout, the bout time, and the pid.
  - Each line is one `write(2)` on an `O_APPEND` descriptor, so workers' lines never interleave. The overflow line is
    written before the corrupted read that can fault, so it survives a SIGSEGV.
  - **Fail closed** (build v3, `rbt129-epa-instr/3`; #527 adversary MINOR 9): if the log cannot be opened, or an
    overflow line is not written whole, the process aborts (SIGABRT). An overflow is never lost silently and never
    falls back to stderr (`run.log`); the run ends as an unattested crash. Nothing about the physics changes: this runs
    only after a horizon already overflowed.
  - Each process also writes a histogram of every horizon size at exit (forked workers through a
    `multiprocessing.util.Finalize`).
- **The recipe.** Run `scripts/build_mujoco_instrumented.sh instr /opt/rbt129-venvs/instr`. It:
  - refuses any other toolchain (clang/LLD 18.1.3, cmake 3.28.3, ninja 1.11.1);
  - builds in **`/opt/rbt129-mjbuild`**, a fixed absolute path that is part of the recipe (ThinLTO symbol names;
    DIAGNOSIS "Builds");
  - checks the patch's sha256 and the output's: **`2aea9a9447d68edf07936df0d7d6a0c37b7e2df54441814b20ddd6e96ab763f4`**;
  - installs the output into a venv of the pip wheel (`mujoco==3.14.0`, `numpy==2.4.6`), replacing the wheel's
    `libmujoco.so.3.14.0`, whose stock sha256 `5e7623e3…441000b` it checks first;
  - finishes by running `mjbuild.check_instrumented()` in the new venv.
- **Reproduced:** a from-scratch rebuild (new clone, new dependency fetches) gave the same sha256. Details in
  `IDENTITY.md`.
- **Versions.** v1 `7ae75f7f…` (first log), v2 `1d138916…` (unit/attempt/pid/seq on every line), **v3 `2aea9a94…`**
  (fail-closed overflow write). Each was built twice from scratch with the same sha, and v3 is the build the lanes,
  the identity check and the registration use.

### Why not #520's log-only build (`74e1d8a2…`, `diag/mujoco-3.14.0-epa-horizon-log-only.patch`)

Both are guard-off and hook the same point (right after `horizon(pt, face)` in `epa`); both log an overflow and then
behave as stock does, crash included. This build is a superset, for what continuations need and #520's lacks:
1. **near misses** (horizon ≥ 17) are logged, not only overflows (> 24);
2. each event carries the **`mj_step` within the bout** (a hook in `mj_step`), and the wrapper's season lines place it
   in its **season**;
3. events go to a **dedicated per-run file** (`epa_overflow.jsonl`), not to stderr: stderr is the run's `run.log`,
   which holds per-season outcome lines, so reading overflows there would be a no-peek risk (FC-3 forbids it);
4. the per-process horizon **histogram survives `WORKERS=2`**: pool workers leave through `os._exit`, which skips
   #520's destructor; here a fork resets the counts and a `multiprocessing` finalizer flushes them;
5. an **identity marker**, `rbt_hzn_build_id()`, that `mjbuild.check_instrumented` requires beside the sha256.

The sha256s differ because the patches differ (and the WORKDIRs: `/tmp/rbt129-mjbuild/logonly` against
`/opt/rbt129-mjbuild`). Reproducibility and identity are shown for this build in `IDENTITY.md`.

## 2. Run-lane integration

- **Which jobs.** A job named `RB/…` or `SCAN/…` is a continuation (`stages.continuation`).
- **The checks.** `run-lane` refuses:
  - **exit 9:** a continuation job in a lane whose `launch.txt` has no `mujoco_build` line, or a `mujoco_build` line
    that is not this tree's `mjbuild.BUILD_LINE`;
  - **exit 9:** any continuation lane in a process not running the instrumented build. `mjbuild.check_instrumented`:
    - finds the `libmujoco.so.3.14.0` the process has **mapped** (`/proc/self/maps`), exactly one;
    - checks it against `INSTR_SO_SHA`;
    - checks that its `rbt_hzn_build_id()` returns the build marker.

    `__version__` alone reads "3.14.0" under both builds, so it is not used for identity;
  - **exit 4:** a non-continuation job in a continuation lane;
  - **exit 4:** a job touching the CRASHED unit's directory;
  - **exit 4:** a scan or R-B job outside its launch's list;
  - **exit 10:** an R-B lane (keyed on the launch's `go` line), until `OVERFLOW-RULE.md` is committed, unmodified, on
    `origin/claude/new-session-4cao7d`, with exactly one `REGISTERED: RBT129-<id>` line and exactly one
    `OVERFLOW-RULE: include-flagged|exclude-known-flagged` line (#527 adversary MINOR 8);
  - **exit 4:** a `mujoco_build` launch with neither a `scan` nor an `rb_points` line;
  - **exit 4:** a continuation job whose run directory already meets RULING item 5's crash count in its log (its last
    two attempts consecutive native exits, one at `workers` 1): "CRASHED (attested yes/no): re-emit the lane without
    it" (MAJOR 1). After every native exit, run-lane saves the run's EPA log alone to `ckpt/<label>-crashlog`, and the
    check reads that record when it holds more than the local log.
- **Emitters too** (COORD-RULING-520 D3, FC-3): `rb-emit` and `scan-emit` refuse (exit 9) unless the emitting process
  runs the instrumented build, checked the same way. Emit with `/opt/rbt129-venvs/instr/bin/python`.
- **Quarantine.** `stages._restore`, the lane check and the scan refuse (exit 4) the Stage-1 label and every committed
  `QUARANTINE: <label>` line of `continuations/QUARANTINE.md` and `stage2-plan/RULINGS-CITED-S2.md` (the plan's format;
  case-insensitive substring). In particular `_restore` refuses `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M`, with or
  without saves, for every caller.
- **The run.** A continuation's ecology runs through `epa_ecology.py`. That file:
  - checks the build again, in the ecology process itself;
  - adds `mujoco_build` (build marker, the mapped library's sha256 and path, the patch sha256) to every platform
    record it writes: the top level of a fresh run's `platform.json`, and each `resumes` entry;
  - writes `epa_overflow.jsonl` in the run directory, with a `start` line per process start and a `season` line as
    each season begins.

  The log rides the run's checkpoint branch with the rest of the directory.
- **Ids and the fault marker** (agreed with the Stage-2 plan): every library line carries `unit` (the run's checkpoint
  label), `attempt` (1 + earlier starts), `pid`, `seq`; the start line carries `workers`; a broken pool's worker exit
  codes go to a `pool_broken` line; after the ecology process exits, `run-lane` appends
  `{"exit": {"attempt", "code", "signal", "native"}}`. `epa_ecology.attested(log, unit, attempt)` (an overflow line of the unit and attempt, before
  that attempt's exit line) and `epa_ecology.native_exit(log, attempt)` are the crash attestation. `forced_overflow.py` checks the chain at WORKERS=2 (`records/forced-overflow.txt`).
- **Reading the log.** `epa_ecology.read_log` assigns each event to its season and keeps each season's **last** attempt
  (a resumed run repeats the seasons after its last save).
- **After each job.** `run-lane` prints `EPA OVERFLOW: <job>: <n>` when there was one: the count only, no season.
- **Stage 1 is untouched.** Jobs not named `RB/` or `SCAN/` run `-m rabbitstew.cli` as before, on the stock pin
  (`check_mujoco`). No Stage-1 record, lane, readout or registered plan is changed. The 2 h cap and the durable-done
  rules (`_finished`, receipts, `_restore`'s sentinel) apply to continuation jobs unchanged.

## 3. The M/N silent-corruption scan (owner decision 1)

- **The lanes.** `stages.py scan-emit --fair=--fair` writes `lanes/SCAN/`. Every Stage-1 M and N fork in
  `lanes/1-MN/launch.txt`'s `forks` line is included, **except the CRASHED `c2-p030-U-G/129001/M`**: 30 M and 7 N,
  37 units, 58 / 108 core-h.
- **The two jobs per unit:**
  - `fork SCAN/<point>/<seed>/<arm>`: the unit's ckpt60 (restored from `ckpt/rbt-129-stage1-…-ckpt60`), forked with its
    arm's settings and resumed to 300 on the instrumented build, into
    `mn-corruption-scan/replay/<point>/<seed>/<arm>`. It is saved to its own `ckpt/rbt-129-mn-corruption-scan-replay-…`
    branch, with periodic saves, and is resumable across the 2 h cap.
  - `scancmp SCAN/<point>/<seed>/<arm>-cmp`: restores the stored run from `ckpt/rbt-129-stage1-<point>-<seed>-<arm>`
    and compares every file byte for byte. `config.json` is included; logs, `platform.json`, the EPA log and
    `SCAN.txt` are not. It writes `SCAN.txt` (IDENTICAL, DIFFER with the differing file **names** only, or
    NO-REFERENCE), with the replay's EPA summary.
- **The report.** `stages.py scan-report` writes `mn-corruption-scan/scan_report.txt`: **counts only** (#527 adversary
  MAJOR 2): totals by arm of each verdict and state, and a unit named only when it is DIFFER, NO-REFERENCE, OVERFLOWED
  or UNLOGGED. No EPA log, season, geom pair, near-miss figure or differing file name is copied; those stay in each
  replay's `SCAN.txt` and log, on its checkpoint branch, for the coordinator.
- **Coverage (MAJOR 4).** The scan's state is **CLEAN (seasons 60–299)**: each replay starts from the stock ckpt60, so
  the S60 phase upstream of every Stage-1 M and N (S's seasons 0–59) is **UNSCANNED**. The report header says so.
- **What a mismatch means.** It is silent corruption, or nondeterminism. The EPA log tells the two apart: an overflow
  in the replay's log marks corruption. A DIFFER with no overflow is nondeterminism, which is itself an integrity
  finding.
- **The scan is not gated** on the overflow rule. It produces no continuation data.

## 4. R-B (owner decision 3, `RBT129-RB-GO-1`)

- **The lanes.** `stages.py rb-emit --fair=--fair` writes `lanes/RB/`: 224 jobs on 20 lanes.
- **The points.** The 9 points of `stage1_readout.txt` L442–L451, checked against the committed readout at emission.
- **The seeds.** 129009–129016 at their screened salts, from `lanes/1/launch.txt` (= `lanes/1-MN`'s): 129010 and
  129016 at (1, 0), the rest at (0, 0).
- **The arms**, per READOUT-PLAN §7.2 and DESIGN §4.1 (2b: "all layers") and §5.2:
  - **S at all 9 points.** S60 fresh, ckpt60, S to 300. There is no census adoption and no K-SALT: those apply to seeds
    1 and 1–3 only. 72 chains, **140 / 262 core-h**, which matches the readout.
  - **M at `c2-p030-U-G` only.** §5.2 gates M at up to 6 R-B points, at census g0 ≤ 1.0 with the designed fauna not
    FOUNDING-FAIL and the point not an anchor. Of the 9 points, only `c2-p030-U-G` (g0 0.938) qualifies. That is read
    from the committed Stage-0 readout, which Stage 1's gate was checked against.
    - The **seed rule** (valid at the merge) is applied per seed at run time (`seed_rule`). A seed that is not valid
      gets a skipped M with its reason.
    - At most 8 arms, 12.5 / 23.3 core-h.
  - **N at none.** No R-B point has g0 ≤ 0.8.
- **The CRASHED unit.** `1/c2-p030-U-G/129001/M` stays CRASHED: not re-run, and no stand-in among seeds 9–16. M there
  reads at most 15 of 16. No R-B job touches seeds 1–8.
- **Gates.** The lanes run only on the instrumented build (exit 9) and only once the overflow rule is registered
  (exit 10). Both refusals were checked against the committed lanes.
- **Not launched.**

## 5. To launch (the coordinator)

On each runner host, from the repository root at the lanes' commit:

```
scripts/build_mujoco_instrumented.sh instr /opt/rbt129-venvs/instr   # must print sha256 2aea9a94...; else stop
/opt/rbt129-venvs/instr/bin/python runs/RBT-129/launch/stages.py run-lane runs/RBT-129/lanes/SCAN/hostK-laneL.jsonl
```

- Run it as a harness background task, two lanes a 4-core session at `WORKERS=2`, as before.
- **Scan.** Afterwards, `stages.py scan-report`.
- **R-B.** First the coordinator commits `continuations/OVERFLOW-RULE.md` with its `REGISTERED:` line. That file is
  outside the pinned trees, so the lanes need no re-emission.
- **Lane loads.** The scan's odd-seed lanes carry 4–5 units, about 6–8 h of wall time; even-seed lanes carry 2–3.
  `--hosts` can be raised at re-emission.

---
_Generated by [Claude Code](https://claude.ai/code)_
