# RBT-129 continuations tooling (#527): adversary review

*Adversary: `session_01P8aqsdg3DfgiFUuB4jGcuv`. Reviewed 2026-10-03 at PR head `5d04edcf21ee7755dc8b95c4d7530289d5839969`
(`claude/rbt129-continuations-tooling`), base `claude/new-session-4cao7d` at `5830288e`.
Coordinator: `session_017eUHGNdTSsoVFAtLaJWehF`.*

**Hygiene.** I fetched only the PR head and the base, each with a narrow refspec, plus the ckpt60 branch of the one
unit I re-ran (`ckpt/rbt-129-stage1-c0-p030-PW-G-129001-ckpt60`, through the PR's own `identity.sh`). I did not fetch
or read the quarantined `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M`. I did not read any Stage-1 `run.log` or any other
per-unit Stage-1 outcome. I launched no SCAN or RB lane: the exit-10 gate was tested by calling
`check_lane_continuation` and `check_overflow_rule` directly, never through `run-lane`. I committed no `OVERFLOW-RULE.md`.
The one I made for the bypass test was a local commit in a throwaway worktree, never pushed.

## Verdict: MERGE WITH FIXES

- **The core claims hold. I reproduced them in my own container:**
  - the build's sha256 is bit-for-bit the same;
  - the patch only logs;
  - the forced overflow gives the same chain;
  - FC-3 refuses the stock library, an `LD_LIBRARY_PATH` swap and both `LD_PRELOAD` variants;
  - no `run.log` reader was added;
  - the scan's unit list is exactly the 38 forks of `lanes/1-MN` minus the crashed one;
  - R-B's points, seeds, salts and gate match the readout and DESIGN §5.2;
  - the test suite passes: 1057 passed, 2 skipped at the head; 1100 passed, 2 skipped on the trial merge.
- **Nothing found makes the tooling compute a wrong physics value.** There is no BLOCKING finding against the code.
- **Fix before R-B or the scan launches:**
  - MAJOR 1: no crashed-unit stop in the tooling;
  - MAJOR 2: the scan publishes more than counts.
- **Fix in the coordinator's registration, not in this PR's code:**
  - MAJOR 3: the Stage-2 plan cites the build v1 blobs;
  - MAJOR 4: the scan does not cover the S60 phase;
  - MAJOR 5 and MAJOR 6: rule wording on attestation and on the ceiling.

## Claims (a)–(j)

| claim | result |
|---|---|
| (a) build reproducible, sha `1d138916…`, marker /2, guard off | **VERIFIED.** A fresh clone and build in `/opt/rbt129-mjbuild` with clang/LLD 18.1.3 gave `1d138916760a1226e1882a578851bfd6da88c2ab9532949bdfdcfd25f0e94aa0`, `vfmadd count 0`. The patch reads only. See F-a. |
| (b) identity 4/4 units, 3709/3709 files | **VERIFIED, with a caveat (NOTE 15).** I reproduced one unit (N `c0-p030-PW-G/129001`, 30 seasons): see § (b) below. |
| (c) forced overflow at WORKERS=2 | **VERIFIED.** The same chain: two overflow lines (unit, attempt, pid, seq), then `pool_broken` with −11, then `exit` native, then attested; attempt 2 clean. The stock venv is refused with exit 9. |
| (d) FC-3 | **VERIFIED** against the stock library, an `LD_LIBRARY_PATH` swap, `LD_PRELOAD` of the stock library, and `LD_PRELOAD` under another name (all exit 9). Workers fork, so they share the parent's mapping. NOTE 16 lists the residual gaps. |
| (e) no-peek | **VERIFIED for readers.** No `run.log` reader was added. Two gaps: the C library falls back to stderr, which is `run.log` (MINOR 9), and the scan's published output (MAJOR 2). |
| (f) scan | **The unit list is VERIFIED:** 37 = `lanes/1-MN`'s 38 forks minus `c2-p030-U-G/129001/M`. Every fork's `src`, `set`, `salts`, `seasons` and `seed` equals its Stage-1 job. **Its output exposes more than counts** (MAJOR 2), and **its coverage stops at season 60** (MAJOR 4). |
| (g) smoke and resume, "last attempt counts" | **Sound.** `state.json` is saved every season and the pool `map` is synchronous, so only the in-progress season repeats. Edge cases are in MINOR 11. |
| (h) R-B, 224 jobs; exit 10 | **The jobs are VERIFIED:** 72 × 3 + 8 = 224; the 9 points equal the readout's L443–L451; only `c2-p030-U-G` passes §5.2 (g0 0.938; the next is 1.059); no N. **The exit-10 gate is weak** (MINOR 8). |
| (i) the overflow-rule draft | See **Part 2**. |
| (j) tests | **VERIFIED.** 1057 passed, 2 skipped at the head; 1100 passed, 2 skipped on the trial merge (§ (j)). |

### (b) My identity reproduction

`identity.sh` (copied to keep the run directories), stock venv against instrumented venv, `WORKERS=2`, 30 seasons from
`c0-p030-PW-G/129001`'s ckpt60, forked as N:

```
N:c0-p030-PW-G/129001 seasons 60-89 exit stock 0 instr 0 | 1121 files | stock vs instr: IDENTICAL | instr platform.json mujoco_build 1d138916760a... | epa: near(>=17) 0 overflow 0 max_horizon 13 epa_iterations 77052682
identity: 1/1 units IDENTICAL
```

### (j) Tests

The venv is clean: `python3.11 -m venv`, then `pip install -e .[dev]`. That gives mujoco 3.14.0, numpy 2.4.6 and
pytest 9.1.1, with **no scipy**.

| tree | result |
|---|---|
| PR head `5d04edc` | **1057 passed, 2 skipped** (19 min). Matches the claim. |
| trial merge with base `5830288` (clean, no conflicts) | **1100 passed, 2 skipped** (18 min) |

- The two skips need the instrumented build. One is `test_the_forced_overflow_on_the_build`; I ran that check by hand
  under (c).
- The trial merge brings in the Stage-2 plan's tests. `test_every_lock_must_open` passes here: this checkout holds no
  local ref of the quarantined branch.

## Part 1: findings on the tooling

### MAJOR 1. No mechanical CRASHED stop: a restarted lane resumes a CRASHED continuation unit

- **What `_ecology` does on a crash.**
  - On a non-zero exit, `_ecology` writes the `exit` line and raises `SystemExit`, and the lane stops.
  - The draft (§4.3) says an attested crash does **not** stop the hive. So the lane must be restarted to run its
    remaining jobs.
  - On restart, `run_job` finds no done-marker for the crashed job, so it runs `_resume` again.
  - After the second counting crash, that third run is a resume of a CRASHED unit, which RULING item 2 bars.
- **What the code has instead.**
  - There is no CRASHED marker, no per-job skip, and no lane-level refusal.
  - `stages.QUARANTINED` is a hard-coded one-element tuple holding the Stage-1 label. So the draft's §4.5 ("the
    readout refuses the label mechanically") and the plan's ruled `QUARANTINE:` lines have no counterpart in the
    tooling R-B runs on.
- **The evidence is not durable.**
  - The crashed attempt's overflow and `exit` lines exist only in the container's run directory: no save follows a
    failed job, and `_every` stops with the run.
  - If the container is lost, the branch's last periodic snapshot lacks them, so the crash cannot be attested. That
    fails safe (unattested → stop) but costs a stop.
- **Fix.**
  - After every native exit of a continuation job, save the run's `epa_overflow.jsonl` alone to a crash-record ref.
  - Have `run_job` refuse (exit 4) a continuation job whose log already holds two consecutive native exits, one at
    `workers` 1, and print "CRASHED (attested yes/no): re-emit the lane without it".
  - Have `_restore` and the readers refuse any label listed in a committed `QUARANTINE:` file, as the plan's drivers
    round does.

### MAJOR 2. The scan publishes per-unit EPA logs and per-unit near-miss rows, not counts only

- **What `scan_report` publishes.**
  - It copies every unit's whole `epa_overflow.jsonl` to `mn-corruption-scan/epa/`, which the README says is committed.
  - Each copy holds a `season` line for every season the replay ran. For a Stage-1 M or N unit whose world emptied, the
    last season line is its extinction season. Each event line also names the geom pair (which bodies were in contact
    in that season).
  - It prints per-unit rows: near-miss count, largest horizon, number of files compared.
  - On DIFFER, it lists the differing **file names**. Per-season files make that a "first season that differs".
- **What the rules allow.**
  - Stage-2 plan §3.6: "The scan record carries the count only, plus the scan's output-hash comparison. The season of
    the first overflow is dropped (O-7; finding 19: a how-far proxy)."
  - Plan line 551 and the draft's §5.3: no unit is named except OVERFLOWED and CRASHED ones; "a near miss is not named".
- **The smoke records do the same for 2 units.** `records/smoke-*.epa.jsonl` and SMOKE.md's "60–299" are committed.
- **Fix.**
  - Commit only: the totals by arm; the per-unit verdict (IDENTICAL / DIFFER / NO-REFERENCE) with the overflow count;
    and the units named only when DIFFER or overflowed.
  - Do not commit the logs or the DIFFER file names. Leave them on the replay branches, for the coordinator's ruling.
  - Strip the season lines from the two committed smoke logs, or move those logs to a branch.

### MAJOR 3. The Stage-2 plan registers the build by the v1 blobs, which do not build `1d138916…`

- **What the plan cites.** `STAGE2-PLAN.md` §3.1 (L208–L209) cites `scripts/build_mujoco_instrumented.sh` as blob
  `1b6cf31` and the patch as blob `ccde8f9`, "cited by blob, not by PR head". It pairs them with marker /2 and sha
  `1d138916…`.
- **Those blobs are build v1.**

```
$ git show ccde8f9 | grep -m1 'define RBT_HZN_ID'
+#define RBT_HZN_ID "rbt129-epa-instr/1 mujoco 3.14.0 ... guard-off count-and-log"
$ git show 1b6cf31 | grep -E '^INSTR_SO_SHA|^PATCH_SHA'
PATCH_SHA=06877b11...   INSTR_SO_SHA=7ae75f7fe32e...
```

- **The v2 blobs.** At every commit from `d2b3b65` to the head, the blobs are script **`f3e3c48`** and patch
  **`f262020`** (patch sha256 `c5dba64d…`).
- **Fix.** The coordinator's registration cites `f3e3c48` and `f262020`, and the plan's §3.1 is corrected in the drivers
  round. Not a code defect in #527.

### MAJOR 4. The M/N scan covers seasons 60–299 only; "scanned without an overflow = CLEAN" over-claims

- **Where the replay starts.** Each replay starts from the unit's stock ckpt60. The S60 phase upstream of every Stage-1
  M and N (S's seasons 0–59) is not replayed.
- **Why that matters.** Under the draft's own propagation rule (§3.1) and plan §3.3, an overflow there would make the M
  and N OVERFLOWED. The scan cannot see it.
- **What over-claims.**
  - Plan §3.6: "A scanned unit … without one, CLEAN".
  - The scan report's header: "every Stage-1 M and N fork, replayed…".
- **Fix.**
  - Name the state **CLEAN (seasons 60–299)**. The unit's S60 phase stays UNSCANNED until the owner's S scan.
  - The report header and the A7 disclosure say so in words.

### MINOR 5. `epa_ecology.attested` is not the plan's "attested"

- **The two definitions.**
  - Plan §3.2: "an overflow line with this unit and attempt, **followed in the log by this attempt's exit line with
    `native` true**".
  - The function: an overflow line of the unit and attempt not preceded by that attempt's exit line. It returns True
    when the attempt has **no exit line at all**, and it says nothing about `native`.
- **Why it is only MINOR.** The draft (§4.2) and the plan's `crash_attested` both AND it with `native_exit`, so the
  combined test is right.
- **The risk.** A future reader may call `attested()` alone.
- **Fix.** Rename it `overflow_before_exit`, or fold `native_exit` into `attested`.

### MAJOR 6 is in Part 2 (the ceiling).

### MINOR 7. `write_exit` attributes an exit to the latest `start` line, even when the process never wrote its own

- **The failure.** A process that dies before `install()` (the exit-9 refusal, an import error, a fault while loading)
  writes no `start` line. Its `exit` line then carries the **previous** attempt's number.
- **The consequence.** `native_exit` takes the **last** exit line of an attempt. So a later native death can be booked
  to an earlier attempt that overflowed and survived. That attempt then reads attested-and-native.
- **Fix.** Have run-lane count the `start` lines before it launches. If none was added, write
  `{"exit": {"attempt": null, "nostart": true, …}}`, and read that as HELP.

### MINOR 8. The exit-10 gate passes an empty `REGISTERED:` line, an unpushed local commit, and a renamed lane

Each case was run through `check_lane_continuation(jobs, launch)` on a real `lanes/RB` lane, in a throwaway worktree:

```
A (no file)                              -> exit 10
B (file present, uncommitted)            -> exit 10
C (committed locally, text "REGISTERED:") -> "overflow rule ... blob b3248911..." GATE PASSED
D (staged, not committed)                -> exit 10
E (RB jobs renamed SCAN/..., launch.txt without rb_points/scan, no rule) -> GATE PASSED
```

- **What C shows.** Nothing ties the file to a ruling: no ID format, no `OVERFLOW-RULE: include-flagged` line, no check
  that HEAD is on `origin`. Each lane prints its blob, but nothing makes the blobs agree across lanes.
- **What E shows.** It needs hand edits to committed lanes. But a continuation launch with neither a `scan` nor an
  `rb_points` line is accepted.
- **Fix.**
  - Require `REGISTERED: RBT129-…` with a non-empty ID.
  - Require `OVERFLOW-RULE: include-flagged|exclude-known-flagged`.
  - Require the blob to be reachable from `origin/<base>`.
  - Refuse a `mujoco_build` launch that has neither `scan` nor `rb_points`.
  - Key the R-B gate on the launch's `go` line, not on the job-name prefix.

### MINOR 9. A failed log write loses an overflow silently, or sends it to `run.log`

- **What `emit()` does.** If `open(RBT_HZN_LOG)` fails, it writes overflow lines to fd 2, which is the run's `run.log`.
  Nobody reads that (by design). A `write()` error is ignored.
- **The consequence.** The unit then reads CLEAN, because its season lines (written from Python) are all there. The
  draft's "the log is the only evidence that an overflow did not happen" makes this the one silent hole.
- **Fix, fail-closed and still guard-off.**
  1. On any open or short-write failure for an *overflow* line, `abort()`. That is a native exit with no overflow line,
     so the crash is unattested and stops the run. Nothing about the physics changes.
  2. The histogram line already carries `overflows`. Have the readout require
     `sum(hist.overflows) == number of overflow event lines` for every pid that wrote a histogram line, with HELP on a
     mismatch.

### MINOR 10. `_fresh` deletes the EPA log of a season-0 crash

- **What happens.** With no `state.json`, `_fresh` runs `shutil.rmtree(d)`. A continuation's S60 that crashes or is
  killed before its first season ends loses its `epa_overflow.jsonl`: the overflow, the exit line and the attempt count.
- **The consequence.** The item-5 count and attestation then restart from 1.
- **Fix.** Move the log aside to `epa_overflow.jsonl.prev-<n>` and have `read_log` and `attempts` read both, or keep the
  log through the rmtree.

### MINOR 11. Edge cases in "last attempt counts" (`read_log`)

- **Season None.** Events before an attempt's first season line go under season `None`. A later attempt's `None` bucket
  replaces the earlier one wholesale, so an earlier attempt's pre-season overflow can be dropped. No physics runs before
  `step()` today, so this is latent.
- **Season cut short.** A season that a later attempt *began but did not finish* replaces the earlier attempt's complete
  copy of that season. Only the final, completing attempt makes this right. A unit that ends in HELP or CRASHED mid-season
  is read from a partial season.
- **Fix.** Merge, don't replace: a season's overflow set is the union over attempts that ran it. An overflow is never
  un-seen.

### MINOR 12. A compiled `.pyc` is committed

`runs/RBT-129/continuations/__pycache__/forced_overflow.cpython-311.pyc` (16,637 bytes) is in the diff. Delete it and
add `__pycache__/` to `.gitignore`.

### NOTE 13. Where the overflow writes land (for the draft's §3.2 reason 2)

- **The layout.** In 3.14.0 (`mjc_ccd`, L2478–2480), `horizon.indices[24]` sits directly before `horizon.edges[0..23]`
  in the `mj_stackAllocByte` buffer. `addEdge` writes `edges[n]` and then `indices[n]`.
- **What a 25-edge horizon does.**
  - It overwrites `edges[0]` with a face index. That is in-buffer corruption of the horizon EPA then reads.
  - It writes `edges[24]` 4 bytes past the EPA region. Whether that is past the allocation depends on
    `max(epa_size, multiccd_size)`.
- **`nedges` itself is safe.** It lives in the `Polytope` on the C stack, so the logged `nedges` cannot be corrupted by
  the overflow.
- **Can the log line be lost?** The line is written after `horizon()` returns. So a fault *inside* `horizon()` would leave
  no line. That needs a write far enough past the arena to fault (about 9N edges × 4 bytes). It is not plausible at
  `ccd_iterations` defaults, but the forced test (direct `mjc_ccd`, ctypes buffer) does not exercise the in-arena case.
- **What this means for §3.2's reason 2** (writes "re-carved every step"). The first effect is a wrong horizon that same
  EPA call. A wrong contact then enters `qacc`, and so the state, which persists. Reason 2 should be deleted (Part 2, W5).

### NOTE 14. R-B M arms are not in the GO's priced cost

- **What the GO prices.** Owner item 3 prices "the S arms" at 140 / 262 core-h.
- **What the PR adds.** 8 seed-rule M forks at `c2-p030-U-G`, at 12.5 / 23.3 core-h.
- **Why they are probably authorized.**
  - DESIGN §5.2 provides M "up to 6 R-B points".
  - DESIGN's 2b row says "all layers".
  - READOUT-PLAN L882 anticipates "if `c2-p030-U-G` is extended, 129001's M stays CRASHED, 15 of 16".
- **Still.** The coordinator should record that the GO covers them.

### NOTE 15. The identity file counts include the ckpt60 files carried unchanged

- **The counts, for my re-run unit** (N `c0-p030-PW-G/129001`, 30 seasons; the same exclusions as `identity.sh`):

  | | files |
  |---|---|
  | carried unchanged from ckpt60 | 765 |
  | changed | 6: `state.json` (populations, RNG streams, arenas), `history.json`, `lineage.jsonl`, `cohorts.jsonl`, `arenas.json`, `config.json` |
  | new | 350: 343 `null_b/*.json`, 6 `holistic/*.json`, `run.lock` |
  | **total** | **1121** |

- **What that means.** About two-thirds of the "files identical" are the shared starting state and could not differ.
  The physics-bearing outputs (the full `state.json`, the genotype files and the history) **are** included, and they
  are identical. So the identity claim holds. The headline count should be quoted as "356 of 1121 files written or
  changed by the 30 seasons", and the same split given for the other three units.
- **My EPA figures match the PR's record exactly** (77,052,682 iterations, max horizon 13). That is consistent with
  determinism across hosts.

### NOTE 16. FC-3's residual gaps

- **Only `libmujoco` is hashed.** The pip wheel's Python bindings (`_functions…so` and the others) and its plugins
  (`plugin/lib*.so`) are not. The build script checks the wheel's stock `libmujoco` sha when it makes the venv, and that
  pins the wheel. But a venv repaired later is not re-checked.
- **The sha is taken from the file on disk.** It hashes the path's current bytes, not the mapped pages. A same-inode
  overwrite after `import` would pass. That is exotic.
- **Fork is assumed.** Python ≥ 3.14 makes forkserver the default on Linux, under which workers re-import. The venv pins
  3.11.
- **Possible tightening.** Record `sys.version` and the bindings' sha on the `start` line.

### NOTE 17. The lanes pin the launch tree `a0c1d3d`

The drivers round (COORD-RULING-523 P4 item 3) will change `runs/RBT-129/launch/`. After that, SCAN and RB lanes refuse
until they are re-emitted. That is correct behaviour, but put it in the launch checklist.

### NOTE 18. `unit` is cut to 127 characters in C and not in Python

- `rbt_unit[128]` truncates; `unit_id()` does not. An out-of-tree run directory longer than 127 characters can never
  attest.
- Real labels are at most about 60 characters, and the forced test's scratch path was 108.
- Fix: assert `len(unit) < 128` in `install`.

## Part 2: the overflow-rule draft (`OVERFLOW-RULE-DRAFT.md`), as a pre-registration

**Overall.**
- **What is right.**
  - The structure (near miss / overflowed / crashed).
  - FC-2's "the record is the signal".
  - The attempt-level fields.
  - The include-flagged primary, which is consistent with plan §3.4 and `RULINGS-CITED-S2`'s
    `OVERFLOW-RULE-PENDING: include-flagged`.
- **What needs fixing before registration:**
  - it still leaves **choices to be made after data** (W1–W3);
  - its **ceiling counts the wrong thing** (MAJOR 6);
  - **attestation is too coarse** (W6);
  - the **sensitivity is narrower than the plan's** (W4).

### MAJOR 6. The ceiling counts arm-seeds, and one S60 crash makes several

- **What the draft says.**
  - §4.3: "A crash in S's S60 phase also leaves M and N of the seed with no fork source: they are CRASHED too."
  - §4.4 stops at "a second attested CRASHED **arm-seed** at one point, or a third … overall".
- **The consequence.** At an M+N point, **one** S60 crash makes three CRASHED arm-seeds. That trips both limits at
  once, from a single event. At R-B's `c2-p030-U-G` (S+M), one S60 crash already hits "2 at one point".
- **The ambiguity.** "CRASHED unit" in plan §3.5 has the same problem.
- **Wording:**

  > **Ceiling.** Count **attested crash events**: distinct run directories with a CRASHED (attested) state of their
  > own, by RULING item 5's count. Arm-seeds made CRASHED only because their fork source crashed are **not** counted.
  > A second such event at one point, or a third across GO-1 and Stage 2 together, stops all continuation launches and
  > restarts until the coordinator re-rules. Stage-1's `1/c2-p030-U-G/129001/M` is not counted. The M/N scan's replays
  > are not counted: a scan crash is a Stage-1 integrity finding (§6).

  This also removes the draft's "the coordinator may rule otherwise when registering", which is open discretion.

### W1. Delete §3.5 ("the alternative, for the coordinator to choose instead")

- The registration must fix the primary. Leaving the choice open lets it be made after OVERFLOWED counts are known.
- Replace §3.5 with: "`OVERFLOW-RULE: include-flagged` (primary); `exclude-known-flagged` is the sensitivity analysis."

### W2. §3.4 escalation: fix what a re-rule may change, or drop the trigger

- **The problem.** ">5% of a stage's arm-seeds, or ≥3 at a point → the coordinator re-rules" is an open, data-triggered
  re-rule.
- **Wording:**

  > If more than 5% of a stage's arm-seeds, or 3 or more at one point, are OVERFLOWED, the readout **adds** a disclosure
  > line ("overflow is a pattern at …"), and the OVERFLOW-SENSITIVE marks are printed on every affected line. The
  > primary analysis, the sensitivity analysis and every call stay as registered. No re-rule is triggered by overflow
  > counts.

- **Timing.** Also, "before the readout plan is committed" does not fit R-B, whose readout is the Stage-2 plan's,
  committed before R-B data.

### W3. Every HELP state needs a registered default

HELP covers: an unattested crash; a missing log or start line; a foreign unit line; a wrong sha; and, after MINOR 7 and
MINOR 9, a missing start line or a histogram mismatch. Each is a post-data ruling unless a default is fixed now.

> Default, absent a ruling within the readout window: a HELP arm-seed is read as **OVERFLOWED** (include-flagged with
> its sensitivity) if it completed its seasons, and as **CRASHED (unattested)** if it did not. A wrong sha is never
> defaulted: that arm-seed is VOID and re-run on the registered build from its last state that carries the registered
> sha.

### W4. §3.3 sensitivity: recompute the whole map, as the plan does

- **The gap.** The draft recomputes "every registered call that uses an OVERFLOWED arm-seed". But BH (q = 0.10 across
  points), Holm and the map statistics couple points, so dropping one point's arm-seed can move another point's call.
  Plan §3.4 recomputes **the whole final map**.
- **Wording:** "Under `exclude-known-flagged`, the whole final map, every family's BH, Holm and every verdict are
  recomputed. Every call, family decision, map statistic and verdict that differs is marked OVERFLOW-SENSITIVE; on the
  headline the mark sits on the headline line."

### W5. Delete §3.2 reasons 2 and 3

- **Reason 2.** "Writes … re-carved every step" is not true of the mechanism (NOTE 13). The first effect is a corrupted
  `horizon.edges[0]` in the same EPA call. The wrong contact then persists through the state. The plan already deleted
  r1's equivalent.
- **Reason 3.** The `BADQACC` precedent is a documented, warned reset, not undefined behaviour.
- **What to keep.** Reason 1 (informative missingness) alone justifies include-primary.

### W6. Attest the faulting process and the season, not only the attempt

- **The gap.** The attempt-level test attests a crash whenever any overflow happened earlier in the same attempt. An
  attempt can run tens of seasons. An overflow in season 100 that the run survived would attest an unrelated native
  fault in season 180, and that crash would then **not** stop the hive.
- **The data to fix it is already logged:**
  - `pool_broken` names the worker pid that died on a signal;
  - every overflow line carries `pid`;
  - the parent pid is on the `start` line.
- **Wording:**

  > **Attested** (per counting attempt): an overflow line of this unit and attempt whose `pid` is a process that died
  > natively in that attempt (a `pool_broken` worker with a fatal signal, or the attempt's own pid when its `exit` line
  > has a fatal `signal`), logged after the attempt's last `season` line and before its `exit` line, which has
  > `native: true`.

- **No-peek is kept.** The crash-only check reports yes or no and never the season.
- **Note.** With WORKERS=1, the overflow pid is the parent's. With WORKERS=2, one worker can overflow and the other
  fault on a different bout (the forced test shows both workers overflowing). Requiring "the faulting pid" is the
  conservative reading, and a mismatch falls to unattested.

### W7. The scan's state names, and `UNLOGGED`

- **The scan's states.** Adopt MAJOR 4's **CLEAN (seasons 60–299)**. The S60 phase of every Stage-1 lineage stays
  **UNSCANNED**.
- **UNLOGGED.** Widen it:

  > UNLOGGED: a season run with no `season` line, **or** a process whose histogram `overflows` exceeds its overflow
  > event lines, **or** a log with `bad_lines` > 0 that are not the final line of an attempt.

  This closes MINOR 9's hole in the rule, even before the code is fixed.

### W8. The standing sentence (§5.5) over-claims

- **Now:** "Every overflow in these runs is therefore known and handled by the registered rule."
- **Replace with:** "Every overflow the build logged in these runs is handled by the registered rule. A run whose log is
  incomplete is treated as overflowed."
- **Also.** In §1, change "it only guarantees that every overflow is recorded" to "it writes every overflow, before EPA
  reads the overflowed arrays, unless the log write itself fails (then the run aborts)", once MINOR 9 is fixed.

### W9. Definitions to pin

- **The hive** (§4.3, unattested S crash): all RBT-129 continuation lanes, R-B and Stage 2 alike.
- **The S60 phase**: seasons 0–59 of the run that wrote the ckpt60 the arm forked from. For R-B that is the R-B seed's
  own `RB/…/S60`. For Stage 1, see W7.
- **Near-miss threshold**: 17 and cap 24, fixed by the build (`RBT_HZN_NEAR` is set by the wrapper and is not a lane
  parameter).
- **Kept data** (§1, "a season's events"): the union over attempts (MINOR 11), not the last attempt only. An overflow
  once logged is never unseen.

### Consistency check against the Stage-2 plan (A-7, A-11, S2-R2) and COORD-RULING-523 P4

| item | draft | plan | verdict |
|---|---|---|---|
| primary | include, with an exclude alternative open (§3.5) | include-flagged; sensitivity exclude-known-flagged | **align: delete §3.5** (W1) |
| S60 propagation | S, M and N OVERFLOWED | the same | consistent |
| attested | overflow before the attempt's exit, AND `native_exit` | overflow followed by a native exit line | consistent as a conjunction; tighten both (W6; MINOR 5) |
| ceiling | arm-seeds | "CRASHED unit" | **both ambiguous** (MAJOR 6) |
| unattested crash | item 5 as registered; S → hive stops | the same | consistent; define the hive (W9) |
| A-11 (item 7 / item 2 superseded for new units) | not stated | drafted | **add to the ruling**: the instrumented build is allowed for new units; no re-run of any CRASHED unit on any build |
| sensitivity scope | per call | whole map | **align to the plan** (W4) |
| scan | out of scope (§6) | CLEAN / OVERFLOWED for 37 units | **CLEAN (60–299)** (MAJOR 4) |
| build citation | sha `1d138916…` | blobs `1b6cf31` / `ccde8f9` (v1) | **cite `f3e3c48` / `f262020`** (MAJOR 3) |

## What I ran

```
# (a) build, fresh WORKDIR
bash scripts/build_mujoco_instrumented.sh instr /opt/rbt129-venvs/instr
  -> built /opt/rbt129-mjbuild/build/lib/libmujoco.so.3.14.0 sha256 1d138916760a1226e1882a578851bfd6da88c2ab9532949bdfdcfd25f0e94aa0
  -> compiler Ubuntu clang version 18.1.3 (1ubuntu1); linker Ubuntu LLD 18.1.3; vfmadd count 0
  -> installed: {'build_id': 'rbt129-epa-instr/2 mujoco 3.14.0 9ecbb9d7… guard-off count-and-log', 'libmujoco_sha256': '1d138916…'}
# (c) forced overflow
/opt/rbt129-venvs/instr/bin/python runs/RBT-129/continuations/forced_overflow.py $SCRATCH/forced 2
  -> attempt 1 (overflow): exit code 1; exit line {"attempt": 1, "code": 1, "signal": null, "native": true}; overflow lines 2;
     pool_broken [{"attempt": 1, "workers": {"2709": -11, "2710": null}}]; attested True
  -> attempt 2 (clean): exit code 0; native false; histogram lines 2; attested False
  -> FORCED OVERFLOW PASS
/opt/rbt129-venvs/stock/bin/python …forced_overflow.py  -> REFUSED: … the stock pip wheel's libmujoco … exit 9
# (d) FC-3
LD_LIBRARY_PATH=<dir with stock libmujoco.so.3.14.0>  -> maps that one; REFUSED stock sha; exit 9
LD_PRELOAD=<stock libmujoco.so.3.14.0>                -> REFUSED stock sha; exit 9
LD_PRELOAD=<stock renamed libother.so>                -> "maps 0 libmujoco.so.3.14.0 libraries"; exit 9
# (e)
git diff base...head -- '*.py' '*.sh' | grep '^+.*run\.log'   -> exclusion lists, docstrings and tests only
# (f) scan list vs lanes/1-MN
comm -3 <lanes/1-MN forks> <SCAN scan line>   -> c2-p030-U-G/129001/M only; 30 M + 7 N
per-fork src/set/salts/seasons/seed vs the Stage-1 job                -> 0 mismatches
# (h) R-B
224 jobs; 8 M; rb_gate: c2-p030-U-G g0 0.938 m=True; next c1-p030-U-G 1.059; no n
```

## Fix-check (head ad9dd23)

*Requested by the coordinator. Head `ad9dd23f6d772e61096849bf17de2c594839fa89`. It contains base `5830288` (the author
merged it), so the trial merge is a fast-forward to the same tree. Same hygiene as before: narrow fetches only; nothing
on the quarantined branch; no SCAN or RB launch; no `OVERFLOW-RULE.md` (the gate re-attack used local commits in a
throwaway worktree, never pushed).*

### Verdict: MERGE WITH FIXES

- **Every finding routed to the tooling is fixed** (table below). Build v3 reproduces from scratch, its identity holds,
  and the gate and quarantine re-attacks all refuse.
- **The fix-check found two new MAJORs.** Both were already present at r1, and I missed them then.
  - **FC-A:** a race in reading pool-worker exit codes. Real crashes can be booked as non-native exits, so they never
    attest and never count toward item 5. The PR's own forced-overflow check fails 4 of 7 runs here.
  - **FC-B:** every fork inherits its source's EPA log. Under the Stage-2 plan's parser, every R-B and Stage-2 M or N
    arm is then HELP.
- **FC-A has a one-line fix,** verified here (8 of 8 PASS). Both must be fixed before any R-B data are read; FC-A
  before any continuation launch.

### The build and identity

| claim | result |
|---|---|
| v3 rebuilt from scratch | **VERIFIED.** After `rm -rf /opt/rbt129-mjbuild`, the script gave `built … sha256 2aea9a9447d68edf07936df0d7d6a0c37b7e2df54441814b20ddd6e96ab763f4`, and `check_instrumented()` reported marker `rbt129-epa-instr/3` and patch `2821425a…`. |
| v2 → v3 is fail-closed only | **VERIFIED.** `git diff 5d04edc ad9dd23 -- …/build/ scripts/` touches only `RBT_HZN_ID` (/2 → /3), `emit()`, and the call `emit(…, over)` (previously `…, 1`). With a healthy log the path is the same `open` / `write` / `close`. `abort()` is reachable only after a failed `open` or a short `write` of an *overflow* line, which is already in UB. Near-miss and histogram lines stay best effort. No other line of the patch changed, so nothing on the physics path. |
| identity on v3 | **VERIFIED for one unit.** `identity.sh` (stock pip against v3, `WORKERS=2`, 30 seasons, N `c0-p030-PW-G/129001`): `1121 files (356 written or changed by the run + 765 carried unchanged from ckpt60) \| stock vs instr: IDENTICAL \| instr platform.json mujoco_build 2aea9a9447d6... \| epa: near(>=17) 0 overflow 0 max_horizon 13 epa_iterations 77052682`, the same EPA count as v2. |
| the NOTE 15 split | **VERIFIED for my unit:** 356 written or changed + 765 carried = 1121, exactly as `IDENTITY.md` prints. The four rows sum to 1146 + 2563 = 3709. |

### Forced overflow: FAIL in 4 of 7 runs (FC-A)

Here is my first run on v3, unedited (`forced_overflow.py $SCRATCH/forced3 2`):

```
attempt 1 (overflow): exit code 1; exit line {"attempt": 1, "code": 1, "signal": null, "native": true}; ...
    pool_broken [{"attempt": 1, "workers": {"2441": -11, "2442": null}}]; attested True
attempt 2 (clean): exit code 0; ... histogram lines 2; attested False
attempt 3 (unloggable): exit code 1; exit line {"attempt": 3, "code": 1, "signal": null, "native": false}; ...
    pool_broken [{"attempt": 3, "workers": {"2522": null, "2523": null}}]; attested False
FORCED OVERFLOW FAIL
```

Six more runs gave:

```
run 1 FAIL  attempt 1 pool_broken {null, null} -> attested False;  attempt 3 {null, null} -> native false
run 2 PASS  attempt 1 {-11, null};  attempt 3 {null, -6} native true
run 3 FAIL  attempt 1 {-11, null};  attempt 3 {null, null} -> native false
run 4 FAIL  all three cases right, but the clean case has 1 histogram line, not 2 (FC-C)
run 5 PASS
run 6 PASS
```

#### FC-A (MAJOR, must fix before any continuation launch): `pool_broken` reads `exitcode` before the dead worker is reaped

- **The bug.** The `terminate_broken` wrapper (`epa_ecology.install`) records `p.exitcode` for each worker *before*
  calling the original. A worker that has just died on SIGSEGV or SIGABRT is often not yet reaped, so its exit code
  reads `None`.
- **What follows.**
  - `write_exit` then writes `native: false`, because the parent itself exits 1.
  - The attempt does not attest, and **is not a crash at all** for item 5's count.
  - `crash_state` never trips, so `check_not_crashed` never refuses, and the lane can retry forever.
  - The "unloggable" case loses exactly what MINOR 9's fix was meant to guarantee: its abort becomes an ordinary
    failure.
- **When it started.** The race was there at r1. My r1 run of (c) passed by luck. The committed
  `records/forced-overflow.txt` shows a lucky run. `test_the_forced_overflow_on_the_build` is skipped off the build, so
  CI cannot see it.
- **The fix, verified here.** Reap each worker before reading its code:

  ```python
  for p in list((getattr(self, "processes", None) or {}).values()):
      p.join(5)
  codes = {str(p.pid): p.exitcode for p in ...}
  ```

  With that one change (applied to a scratch copy, then reverted), 8 of 8 runs PASS. Both workers then show their real
  signals: attempt 1 `{-11, -11}`, attempt 3 `{-6, -6}`.
- **Also fix the record.** Re-record `records/forced-overflow.txt`, and run the check ≥ 5 times on the launch host as
  part of CT-2.

#### FC-C (MINOR): the clean case's histogram count is flaky

`len(hists) >= workers` fails when one pool worker takes both tasks. The idle worker ran no EPA and no step, so it
writes no histogram line by design (`rbt_hzn_flush`'s early return). Fix: assert one line per worker that ran a task,
or give each worker its task explicitly.

### FC-B (MAJOR, before any R-B data are read): a fork inherits its source's EPA log

- **The cause.** `snapshot` and `fork` both use `fork_config` (`shutil.copytree`), so `ckpt60/` and then every M and N
  directory start with the S60 run's `epa_overflow.jsonl`. That file holds S's `start`, `season`, `exit` and event
  lines, under **S's unit id**.
- **The demonstration.** I built an S log (60 seasons), applied the real `fork_config` twice (snapshot, then fork), and
  appended an M attempt:

  ```
  M dir has S's log: True
  next M attempt number: 2
  plan parse_epa_log(unit=M) -> Stage2Help : a start line of another unit in this run's log
  tooling read_log: starts 2 unlogged []
  ```

- **The consequence.** The Stage-2 plan's `stage2_readout.parse_epa_log` (merged) raises HELP for "a start line of
  another unit". Under r2 §4.6's default, every R-B M arm (and every Stage-2 M and N) would then be read as
  **OVERFLOWED**.
- **What partly works.** The tooling's own `read_log` silently merges S's S60 seasons into the M's kept data. That
  happens to implement §3.1's propagation. But it also numbers the M's attempts from S's count, and it makes the two
  readers disagree.
- **Fix, in either place:**
  - *(tooling)* `fork_config` renames the inherited log to `epa_overflow.source.jsonl` (kept, outside every reader's
    default path). §3.1's propagation then reads the source run's own log; or
  - *(plan)* the parser treats lines of the fork source's unit, before the arm's first own start line, as the S60-phase
    record. The ruling must say which.

### The fixes, finding by finding

| finding | fix at ad9dd23 | check |
|---|---|---|
| MAJOR 1: crashed-unit stop | `check_not_crashed` (exit 4) before every continuation `fresh`/`resume`/`fork`; `save_crash_record` to `ckpt/<label>-crashlog` after every native or `nostart` exit; `QUARANTINE:` lines read from HEAD | **FIXED, given FC-A.** Two consecutive native exits, one at w1 → `CRASHED (attested no) … exit 4`. One native exit; native, killed, native; three native at w2: all allowed (`crash_state` None), as item 5 reads. Two *non-native* failures: allowed, which is exactly what FC-A produces from real crashes. |
| MAJOR 2: scan exposure | `scan_report` is counts only (totals by arm; units named only if DIFFER, NO-REFERENCE, OVERFLOWED or UNLOGGED); no `epa/` copies; smoke logs removed; `records/smoke.txt` counts only | **FIXED in the tree.** NOTE FC-E: the deleted smoke logs are still reachable in history (`5d04edc`). A merge commit carries them into the base, so squash-merge if that matters. |
| MAJOR 4: scan coverage | `scan_state` → `CLEAN (seasons 60-299)`; the report header carries the COVERAGE lines; SMOKE.md and r2 §6.1 say "UNSCANNED" for 0–59 | **FIXED** |
| MINOR 5: `attested` naming | `attested` is now W6's test (`native_exit` folded in); the r1 test is renamed `overflow_before_exit` | **FIXED** (see FC-D on the plan's copy) |
| MINOR 7: `nostart` | run-lane counts start lines before and after; `{"exit": {"attempt": null, "nostart": true}}`; `read_log` flags it as unlogged | **FIXED** |
| MINOR 8: gate | `REGISTERED: RBT129-\S+` and `OVERFLOW-RULE: include-flagged\|exclude-known-flagged`, each exactly once; the blob must equal `origin/claude/new-session-4cao7d`'s (narrow fetch); a build launch without `scan`/`rb_points` refused; the gate also keyed on `go`/`rb_points` | **FIXED.** Re-attack: A no file → 10; B uncommitted → 10; D staged → 10; C2 well-formed but only local → 10; C empty `REGISTERED:` → 10; C3 two `REGISTERED:` lines → 10; E renamed with no `rb_points`/`scan`/`go` → 4; E2 renamed with an empty `scan` line → 4. |
| MINOR 9: lost overflow line | v3 `abort()`; `read_log` cross-checks histogram `overflows` against overflow lines per (attempt, pid) | **FIXED in the library.** The abort is then lost to FC-A in 3 of my 7 runs. |
| MINOR 10: `_fresh` rmtree | `keep_log` keeps the log as `.prev-<n>`; `log_files` reads them first; `attempts` counts across them | **FIXED** |
| MINOR 11: union | `read_log` takes the union over attempts, de-duplicating a re-run's repeat by an event signature | **FIXED.** NOTE: the signature (`event, nedges, epa_iteration, nverts, nfaces, geom1, geom2, step, time`) could merge two distinct events of two bouts in one season. Counts are then a lower bound; the state cannot change. |
| MINOR 12: `.pyc` | removed; `.gitignore` has `__pycache__/`; 0 `.pyc` in the tree | **FIXED** |
| NOTE 15 | the split per unit in `IDENTITY.md` | **FIXED**, and verified for one unit |
| NOTE 16 | `bindings_sha256` and `python` on every start line | **FIXED** (recorded, not checked: as asked) |
| NOTE 18 | `install` refuses a unit id ≥ 128 characters (exit 4) | **FIXED** |
| QUARANTINE: refusal | `is_quarantined`: built-in label + committed `QUARANTINE:` lines (empty refused), case-insensitive substring | **Works.** The Stage-1 label matches its `-crashlog` too (in any case) and not `…-ckpt60`; QUARANTINE.md's indented example line is not read. NOTE: a too-short label quarantines more than one unit. That fails safe (a lane refuses). |

### Other new findings

- **FC-D (MINOR, plan / drivers round).** The Stage-2 plan's `stage2_readout.attested` (r1: "overflow … followed by a
  native exit") and its `parse_epa_log` ("a season counts from its last attempt") now differ from the tooling's
  `attested` (W6) and `read_log` (union). The ruling should say r2's definitions govern, and the drivers round must port
  them.
- **FC-F (MINOR).** `read_log` marks UNLOGGED "an unreadable line in mid-attempt" when an unreadable line is followed by
  any non-`start` line, **including run-lane's own `exit` line**. An ecology process killed mid-write while run-lane
  survives (an OOM kill) then reads UNLOGGED → HELP → OVERFLOWED by default. Fix: treat a bad line directly followed by
  its attempt's `exit` line as the attempt's final line, as r2 §5.2's wording already says.
- **FC-G (NOTE).** `crash_log` creates a temp directory per call and never removes it. It also runs `durable.sh restore`
  (a network fetch) before every continuation job. That is harmless at 224 jobs.
- **FC-H (NOTE).** For an S60 that crashed before season 60, the `snapshot` job refuses with "S must be re-run from 0
  to rebuild it". The refusal is right, but the wording points to a re-run that RULING item 2 bars. Reword it to
  "CRASHED: re-emit the lane without this seed's jobs".
- **FC-I (NOTE).** The smoke runs were on v2, so SMOKE.md carries no v3 claim. v3 differs only on the failed-write
  path, so that is acceptable.

### Draft r2: what changed, and what the ruling should still change

**r2 takes in W1–W9, MAJOR 4 and MAJOR 6 as written.** The W-items checked one by one:

| item | r2 |
|---|---|
| W1 | §3.5 is deleted; §3.2 fixes `include-flagged` |
| W2 | §3.4 adds a disclosure line and no re-rule |
| W3 | §4.6 |
| W4 | §3.3 recomputes the whole map |
| W5 | §3.2 keeps one reason, and §1 says the wrong contact persists |
| W6 | §4.2 |
| W7 | §5.2 and §6.1 |
| W8 | §1 and §5.5 |
| W9 | §1's definitions |
| MAJOR 4 | §6.1 |
| MAJOR 6 | §4.4, verbatim |
| A-11 | §4.5 |

**Remaining wording changes for the ruling:**

1. **§4.6, "absent a ruling within the readout window".** The window is undefined, which is open discretion. Replace
   with: "unless the coordinator rules on it before any outcome of that arm-seed is read".
2. **§4.6, wrong sha.** "VOID and re-run … from its last state that carries the registered sha" contradicts §3.1 and
   §4.5 ("nothing re-run, resumed from an earlier state, or replaced") unless it is scoped. Add: "This applies only to
   an arm-seed that is neither OVERFLOWED nor CRASHED in its registered-sha part. Its outcomes after that state are not
   read before the re-run. The re-run is labelled in the readout."
3. **§4.1, the count.** Add: "An attempt with no `exit` line (killed with its runner) breaks the run of attempts. A
   `nostart` exit is not an attempt. A pool worker's exit code is read only after the worker is reaped (FC-A)."
4. **§3.1 and §1, the inherited log (FC-B).** Add: "A fork's directory starts with a copy of its source's log. Lines of
   the source's unit, before the arm's first own `start` line, are the S60-phase record (§3.1), not a foreign unit's
   lines." Or the tooling stops copying it, and the sentence says the source run's own log is read for §3.1.
5. **§4.2, which definitions govern (FC-D).** Add: "`epa_ecology.attested`, `crash_state` and `read_log` at the
   registered tooling commit are the definitions. The Stage-2 readout is held to them (drivers round)."
6. **§2 and §5.3, near-miss counts.** Add "(a lower bound: near-miss lines are best effort, and identical events within
   a season are counted once)".
7. **§4.3, unattested S crash: "the hive stops".** Nothing in the tooling stops other lanes mechanically. Add: "by the
   coordinator, who stops lane issuance and restarts; in-flight lanes finish".

### Tests

The venv is clean `.[dev]` without scipy (mujoco 3.14.0, numpy 2.4.6, pytest 9.1.1).

- **At the head `ad9dd23`: 1118 passed, 2 skipped** (18 min). Matches the claim.
- **The trial merge into the current base `5830288` is the same tree.** The base is an ancestor of the head
  (`git merge-base --is-ancestor` holds), so the merge is a fast-forward. The single run above covers both.
- The two skips need the build. One is `test_the_forced_overflow_on_the_build`: off the build, CI does not run it, which
  is why FC-A is invisible to the suite.

## Fix-check 2 (head 2a03a15)

*Head `2a03a159f6605169f4fcf6eda65b86f4e27b878d`, fetched with a narrow refspec. It contains base `5830288`, so the trial
merge is a fast-forward to the same tree. Same rules as before: nothing on the quarantined branch; no SCAN or RB
launch; no `OVERFLOW-RULE.md`.*

### Verdict: MERGE

Every fix-check finding routed to the author is fixed and verified by running it. r3 takes in all seven wording items.
I found no regression. The residual items below are for the ruling and the drivers round, not for this PR.

| item | check |
|---|---|
| the build is still v3 | `git diff ad9dd23 2a03a15 -- runs/RBT-129/continuations/build scripts` is empty. `mjbuild` is unchanged, so the `.so` is still `2aea9a94…`, the one rebuilt in fix-check 1. The re-emitted RB and SCAN `launch.txt` files carry the `rbt129-epa-instr/3` build line, and their three `tree:` pins equal this head's trees. |
| **FC-A** | **FIXED.** `terminate_broken` now `join(REAP_S = 5)`s each worker before reading `exitcode`. The forced overflow at WORKERS=2 gave **10/10 PASS**, while the full suite ran on the same 4 cores. Every run read attempt 1 `{-11, -11}` and attempt 3 `{-6, -6}`, `native: true`. I put ad9dd23's `epa_ecology.py` into a scratch copy of the head: `test_pool_broken_reaps_before_reading_exit_codes` **fails** there and passes at the head. The new `records/forced-overflow.txt` is a reaped run. |
| **FC-B** | **FIXED.** `fork_config` moves the copied log to `epa_overflow.source.jsonl` (`set_aside_inherited`). My demonstration, re-run with the real `fork_config` (S log with an S60-phase overflow → snapshot → M fork): `ckpt60` and `M` each hold only `epa_overflow.source.jsonl`; the next M attempt is **1**; the plan's `parse_epa_log(unit=M)` → `unit_state` = **CLEAN** (no HELP); `source_log(M)` holds the overflow and seasons 0–59; S's own log is intact; `scan_files` skips `epa_overflow*`, and `identity.sh` excludes `epa_overflow*`. The same scratch-copy check: `test_a_fork_starts_its_own_log_and_keeps_its_sources` fails on the old code and passes at the head. |
| FC-C | **FIXED.** The clean case now checks a histogram line from every worker that *ran* a task (the pids the child printed), not `>= workers` |
| FC-F | **FIXED.** A cut line followed by an `exit` line is the attempt's final line. `test_a_cut_line_before_its_exit_line_is_not_unlogged` fails on the old code and passes at the head. |
| FC-G | **FIXED.** `check_not_crashed` owns the temp directory and removes it in `finally` |
| FC-H | **FIXED.** A continuation's `snapshot` with S not at season 60 says "CRASHED or lost: re-emit the lane without this seed's jobs, and tell the coordinator". The Stage-1 wording is kept for Stage-1 jobs. |
| FC-I | **FIXED.** SMOKE.md and README say the smoke ran on v2, and that no v3 smoke run is claimed |
| r3: the 7 items | **All in.** FC 1 (§4.6, "before any outcome of that arm-seed is read"); FC 2 (the wrong-sha re-run scoped); FC 3 (§4.1: killed attempt, `nostart`, reaped codes); FC 4 (§1, the inherited log); FC 5 (§4.2, the tooling's definitions govern); FC 6 (§2, §5.3: lower bound); FC 7 (§4.3: the coordinator stops the hive). |
| pytest | PYTEST4_PLACEHOLDER |
| regressions | **None found.** One check: an M or N fork's `epa_overflow.source.jsonl` comes from ckpt60's copy. That copy starts with no `epa_overflow.jsonl`, so the move does not run again, and the chain stays S's log → ckpt60 → M with no duplicate lines. `source_log` is read by no default reader. |

### Residual wording for the ruling (no tooling change needed)

1. **§4.2 FC 5, "at the registered tooling commit".** Name that commit in the ruling: #527's merge or squash commit on
   the base. Otherwise "registered" has no referent.
2. **§1 and §3.1, the S60-phase input.** "Read from the source run's own log" should say **its seasons 0–59 only**. An
   R-B or Stage-2 S run directory keeps one log for both the S60 job and the S resume to 300, so an unrestricted read
   would also propagate S's own post-60 overflows to M and N. Alternatively, cite `epa_overflow.source.jsonl` beside the
   fork, which holds exactly the S60 phase.
3. **§5.1, the build PASS.** It should also require every `start` line's `libmujoco_sha256` to be the registered sha.
   The plan's `unit_state` already does this; the ruling should list it beside `platform.json`.

FC-D (porting `attested` and `read_log` into `stage2_readout`, and making it read `source_log` for `propagate_s60`)
remains the drivers round's, as routed.

---
_Generated by [Claude Code](https://claude.ai/code)_
