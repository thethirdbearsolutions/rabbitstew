# RBT-129 continuations: the instrumented build, run-lane, the M/N scan, R-B

*Owner decisions of 2026-10-03 (`../coordinator/OWNER-DECISIONS-2026-10-03.md`, merged in #522):*
- **(1)** a Stage-1 silent-corruption scan, M and N first;
- **(2)** every RBT-129 continuation runs on **option (c)**: a guard-off, instrumented MuJoCo 3.14.0 that is
  byte-identical to stock and logs every EPA horizon overflow;
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
  - Each process also writes a histogram of every horizon size at exit (forked workers through a
    `multiprocessing.util.Finalize`).
- **The recipe.** Run `scripts/build_mujoco_instrumented.sh instr /opt/rbt129-venvs/instr`. It:
  - refuses any other toolchain (clang/LLD 18.1.3, cmake 3.28.3, ninja 1.11.1);
  - builds in **`/opt/rbt129-mjbuild`**, a fixed absolute path that is part of the recipe (ThinLTO symbol names;
    DIAGNOSIS "Builds");
  - checks the patch's sha256 and the output's: **`7ae75f7fe32e437b2c7283930f38f20adfa33bbe4895c5d91b0c95233814edb8`**;
  - installs the output into a venv of the pip wheel (`mujoco==3.14.0`, `numpy==2.4.6`), replacing the wheel's
    `libmujoco.so.3.14.0`, whose stock sha256 `5e7623e3…441000b` it checks first;
  - finishes by running `mjbuild.check_instrumented()` in the new venv.
- **Reproduced:** a from-scratch rebuild (new clone, new dependency fetches) gave the same sha256. Details in
  `IDENTITY.md`.

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
  - **exit 10:** an R-B lane, until `OVERFLOW-RULE.md` is committed with a `REGISTERED:` line.
- **Quarantine.** `stages._restore` refuses (exit 4) to restore `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M`, with or
  without saves, for every caller.
- **The run.** A continuation's ecology runs through `epa_ecology.py`. That file:
  - checks the build again, in the ecology process itself;
  - adds `mujoco_build` (build marker, the mapped library's sha256 and path, the patch sha256) to every platform
    record it writes: the top level of a fresh run's `platform.json`, and each `resumes` entry;
  - writes `epa_overflow.jsonl` in the run directory, with a `start` line per process start and a `season` line as
    each season begins.

  The log rides the run's checkpoint branch with the rest of the directory.
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
- **The report.** `stages.py scan-report` writes `mn-corruption-scan/scan_report.txt`, and copies each unit's EPA log
  to `mn-corruption-scan/epa/`.
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
scripts/build_mujoco_instrumented.sh instr /opt/rbt129-venvs/instr   # must print sha256 7ae75f7f...; else stop
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
