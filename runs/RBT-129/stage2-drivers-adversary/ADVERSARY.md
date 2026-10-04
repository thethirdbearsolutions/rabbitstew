# RBT-129 Stage-2 drivers round (#533): adversary review

*Adversary: `session_01HSrytBaaQZ5ebri12t1bot`. Coordinator: `session_017eUHGNdTSsoVFAtLaJWehF`. Author:
`session_014peDKmK8Qdna38Zav4JWNH`. Written 2026-10-03.*

- *Reviewed: PR #533 head `755cf8c4f6b5712e779c8899fde00f725f753799`. Base `claude/new-session-4cao7d` at
  `247bbfb3fcce0f8cd6dec151d6df9612ca9e3269`, which is also the merge base. So the trial merge is the head itself: same
  tree, `f7fbb90`, from `git merge-tree`.*
- *No-peek held. I read no `run.log`, no `epa_overflow*.jsonl` of a real run, no Stage-1 or continuation run directory
  and no `ckpt/*` branch. Every git fetch used a narrow refspec. I launched no lane and opened no lock.*
- *Every gate test below ran in a scratch clone whose `origin` was a local bare repository. It ran on synthetic run
  directories with `NO_DURABLE=1`, on my own rebuild of v3. Nothing reached GitHub, and no ecology process started.*

## Verdict: **MERGE WITH FIXES**

- **BLOCKING 1 must be fixed and fix-checked before merge.** One lane restart turns O-2's "DIFFER = HELP" into an
  adoption.
- **MAJOR 2–4 must be resolved before `GO-ID-2A` opens.** A coordinator ruling also resolves MAJOR 3.
  - **MAJOR 2:** the committed lanes cannot run once the GO opens.
  - **MAJOR 3:** a pre-registration gate is moved.
  - **MAJOR 4:** fail-open readout states.
- **What I confirmed** (details in the claims table):
  - The PR changes nothing that live SCAN or RB lanes read or pin (claim a).
  - The 356-job emission matches the plan's 2a design and budget exactly (claim c).
  - A lane refuses with exit 10 today.
  - The v3 build reproduces.

## Findings

### 1. BLOCKING: after a lane restart, an S60CMP DIFFER is adopted (O-2's byte-equality gate is bypassed)

- **The code.** `s2lanes.run_job` (s2lanes.py L321–331) skips the `s60cmp` job whenever its done-marker exists
  (`if stages._finished(d, tag): return`). `s60_compare` writes that marker on DIFFER, before it raises:
  `stages._finish(d, ..., "S60CMP DIFFER")`, then `SystemExit`.
  - Nothing downstream checks the verdict. Not the `ckpt60` snapshot, not the `S` resume, not the M/N forks.
  - So the first run of the lane stops with "HELP, tell the coordinator", and **the next restart of the same lane goes
    straight on**. It snapshots, resumes S to 300 and forks M/N from a re-simulation that is *not* the census run.
- **Reproduced** with synthetic directories under `runs/RBT-129/stage2a/c05-p080-U-G/129001/`, on the PR head with
  `NO_DURABLE=1`:

  ```
  attempt 1: SystemExit: S2A/c05-p080-U-G/129001/S60CMP: S60CMP DIFFER: the re-simulation is not the census run; th...
  attempt 2: run_job RETURNED normally -> the lane goes on to ckpt60, S, M, N
  S60CMP.txt: S60CMP DIFFER: ... | marker files: ['.rbt129-done-S60CMP']
  ckpt60 after DIFFER: ['.rbt129-done-ckpt60', 'config.json', 'history.json', 'state.json']
  ```
- **Why it is blocking.**
  - Lane restarts are routine: containers are reclaimed, and runners restart refused lanes. The tooling's own K-SALT
    stop says "restarting it continues past this record". That is intended for K-SALT, whose VOID is a recorded outcome.
    It is wrong for O-2.
  - Plan §2.1 says "Not equal: HELP". COORD-RULING-523 P3 says the re-simulation is "REQUIRED before Stage-2a S60s are
    adopted".
  - A DIFFER chain would also enter the map as an ordinary scanned unit. Nothing marks it.
  - `test_s60_compare_writes_its_verdict_and_stops_on_differ` tests only the first run.
- **Fix.**
  - On a finished `s60cmp`, re-read `S60CMP.txt` (or the marker's note) and refuse unless it says IDENTICAL. Use a
    distinct exit code, so that re-runs keep refusing.
  - Also make the 129001 `ckpt60` job require a committed or saved `S60CMP IDENTICAL` beside it.
  - Add a restart test.

### 2. MAJOR: the committed lanes/S2A can never run (exit 5 once the GO opens), and later lock edits stall live 2a lanes

- **The conflict.** `launch.txt` pins `tree:runs/RBT-129/stage2-plan 2ca6f50…`, and `check_own_trees` refuses
  (exit 5) unless HEAD's tree is that tree. But `RULINGS-CITED-S2.md`, the file whose `GO-ID-2A:` line opens the
  lanes, **is inside that tree**. Opening the GO changes the pinned tree. So no commit satisfies both gates:
  - at the launch commit, the GO is PENDING, so exit 10;
  - on any commit with the GO open, the tree differs, so exit 5.
- **Reproduced in the scratch clone:**

  ```
  GO-ID-2A opened in a commit, pushed to the (local) base, lane run at that commit:
  REFUSED: HEAD:runs/RBT-129/stage2-plan is not the launch's 2ca6f50bda5e7de779f71ebad7564cf4d1e44500; check out the launch commit
  exit=5
  ```

  With `launch.txt` re-pinned by hand to the new tree, every gate passes ("ALL GATES PASS: the lane would start its 21
  jobs"). So the lanes run only after a **re-emission made after the GO opens**.
- **What this means.**
  - The lanes this PR registers and the adversary reviews are not the lanes that would run. The re-emission would
    happen after authorisation, with no review step named.
  - Any later commit to `runs/RBT-129/stage2-plan/` while 2a runs stalls every 2a lane at its next restart. That
    includes a ruled `QUARANTINE:` line after an attested crash (the rule requires one) and `GO-ID-INTERIM`. It also
    includes the readout-drivers round that §14 schedules "before GO-ID-INTERIM opens".
    - A lane at its old HEAD refuses with exit 10, because `check_go` needs HEAD's blob to equal the base's.
    - A lane on the new base refuses with exit 5.

    Reproduced: a merged `QUARANTINE:` line gives exit 10 at the old HEAD and exit 5 after checkout of the new base.
    Every such case forces a mid-stage re-emission.
- **Fix (one option).**
  - Pin the plan by **blob**: `stage2_readout.py` and `STAGE2-PLAN.md`, or the stage2-plan tree minus
    `RULINGS-CITED-S2.md`.
  - Leave `RULINGS-CITED-S2.md` to `check_go`.
  - Have `check_go` require only that the *base's* committed file opens the GO, without blob equality with HEAD. Read
    `QUARANTINE:` lines from the base too.
  - Then test that the committed lanes pass every gate on a simulated GO-open commit.

### 3. MAJOR: a pre-registration gate is moved: the readout drivers were to exist before the first GO; §14 now puts them after the 2a launch

- **What the registered plan said** (ADOPTED r2):
  - §2.7 item 7: "The drivers and the end-to-end synthetic test committed and fix-checked (§11)", as a gate **before
    any Stage-2 launch**.
  - §11: "**Before the first GO:** the drivers and continuation readers are written, with an end-to-end synthetic-tree
    test … checked by the same adversary … No rule may change in that round".
  - `stage2_readout.main` still raises "SKELETON: the drivers are completed … before the first GO".
- **What this PR says.** §11 and §14 add: "The readout drivers (`interim`, `final`) are the next round, before
  `GO-ID-INTERIM` opens". So the interim and final analysis code would be written while 2a data accumulate. The
  author is COORDINATOR-EXPOSED. No-peek still holds.
- **Why it matters.** This is the pre-data property §2.7 item 7 exists to protect. The PR does not amend §2.7 item 7,
  so the plan now contradicts itself.
- **Ruling P4 item 3 is ambiguous here.** It defines the drivers round as "Stage-2 job emission on the build". That
  may mean the coordinator meant to narrow the gate, but P4 does not amend §2.7.
- **Needs either:**
  - an explicit coordinator ruling that 2a may launch with the readout drivers outstanding (name the constraint that
    replaces it: for example, the drivers are fixed and adversary-checked before any 2a output is read, and that is
    recorded); or
  - the interim and final drivers plus the end-to-end synthetic test landed before `GO-ID-2A`.

### 4. MAJOR: the readout's states fail open on rule §4.6 HELP cases (A2 propagation and unit lines)

- **`s60_overflowed`** (stage2_readout.py L257–266):
  - **A missing `epa_overflow.source.jsonl` returns False** (not overflowed). Every Stage-2a and R-B S60 runs on the
    build, so a fork without its source log has an unvouched S60 phase. Rule §4.6 lists "a missing log" as HELP, and
    §5 says "a run whose log is incomplete is treated as overflowed".
    `test_s60_propagation_reads_seasons_0_to_59_of_the_source_log_only` asserts the fail-open (`not
    s2.s60_overflowed(K)` on an empty directory).
  - It ignores `read_log`'s `unlogged` for the source log. An UNLOGGED S60 phase propagates nothing.
  - It drops events under season `None`. In a log copied at season 60, every event is S60-phase, including any before an
    attempt's first season line.
- **`unit_state`** no longer detects **a foreign unit's line**, which §4.6 lists as HELP. r2's `parse_epa_log` raised
  on a start or event line of another unit. The tooling's `read_log` takes no unit, and `unit_state` passes the unit
  only to `crash_state`. The r2 test cases for this were deleted (see claim g).
- **Fix.**
  - Missing or UNLOGGED source log, or season-`None` events in it: HELP, defaulted per §4.6. Add a "Stage-1 / UNSCANNED"
    path only where a fork's source is a stock Stage-1 run.
  - Check that every line's `unit` is the run directory's id.

### 5. MINOR: FC-2 (2B2A in a strict-ancestor commit) is not enforced by code

- `check_go` accepts a commit that flips `2B2A:` and opens `GO-ID-2A` together. Reproduced: one commit with
  `2B2A: DECLINED` and `GO-ID-2A:` open, merged: "ALL GATES PASS".
- It holds today only because `2B2A: COMMITTED` is already on the base and P3 binds the coordinator procedurally.
- **Fix:** require `HEAD:RULINGS`'s 2B2A line to equal that in the parent of the commit that introduced the
  `GO-ID-2A:` line. A `git log -S'GO-ID-2A: RBT129'` walk is enough.

### 6. MINOR: `check_go` ignores a failed fetch

- The `git fetch` return code is discarded (s2lanes.py L209, the same pattern as `stages.check_overflow_rule`). The
  base comparison then runs against whatever `refs/remotes/origin/<base>` holds.
- Reproduced: origin unreachable, plus a tracking ref left at a GO-open commit while the real base has it PENDING.
  Result: "ALL GATES PASS".
- The realistic case is a GO later withdrawn on the base during a network outage.
- **Fix:** refuse (exit 10) when the fetch fails.

### 7. MINOR: run-lane checks each job's shape, not that the lane is the emission

- `check_lane_s2a` never reads `seasons` or `cost`. It does not require that the 129001 unit has its `S60CMP` before
  `ckpt60`, or any `S60CMP` at all. It does not require each unit's job order.
- Lane files are committed (`CLEAN`) but not pinned. With MAJOR 2 forcing a re-emission, nothing at run time ties the
  running lane to `s2a_units`.
- **Fix:** have `run-lane` rebuild the units (`s2a_units` over the committed inputs) and require the lane's jobs to be
  exactly that host and lane's slice. Or pin a digest of the lane files in `launch.txt`.

### 8. MINOR: A3 is implemented for start lines only

- OVERFLOW-RULE A3: "every `start` line … **and every `platform.json` record and `resumes` entry**". `unit_state`
  checks start lines only, and plan §3.1 now quotes A3 as start lines only.
- This is acceptable if the readout drivers add the platform and resumes check. §3.1 should quote A3 whole.

### 9. NOTE: the emission on a real census unit is untested before the GO

- `s60cmp` compares every file of the census snapshot except a skip list. That list is `K1_SKIP` plus
  `epa_overflow*`, `S60CMP.txt` and done-markers.
- If the census snapshots hold any file the build's run does not write, all 12 S60CMPs would DIFFER. That is
  fail-safe, but it would stall 2a at its first unit. Examples: a census-era provenance file, or a durable artifact
  outside the list.
- I could not test this under no-peek. The coordinator may want one 129001 re-simulation and comparison as an
  operational check. It counts against O-2's cost.

### 10. NOTE: smaller items

- **The test deletions are legitimate migrations (claim g)**, except as MAJOR 4 says.
  - The r2 crash-count cases (neither at WORKERS 1, one native exit, not the last two) are covered by the tooling's
    `test_crash_state_is_rulings_item_5_count`.
  - "Overflow after the exit line does not attest" is covered by
    `test_attestation_needs_the_faulting_process_in_the_faulting_season`.
  - "A season counts from its last attempt" is reversed to the union, as rule §1 / MINOR 11 require.
  - Lost without replacement: the foreign-unit HELPs (MAJOR 4), and r2's "exit with no start" HELP. `read_log` flags
    only an exit line that carries `nostart` as UNLOGGED. An exit line whose attempt has no start line is no longer
    flagged, so this one is only partly covered.
- **Commit pin.** `launch.txt` records `commit 9e4c89d`, a PR-branch commit. Nothing checks it, and a squash merge
  orphans it.
- **Missing `__file__` check.** `registered_epa` hashes the file at `path` but imports `epa_ecology` by name. If another
  `epa_ecology` is earlier on `sys.path`, or already in `sys.modules`, the hashed file is not the one used. Assert
  `epa_ecology.__file__ == path`.
- **Footer placement.** STAGE2-PLAN.md §14 is appended after the closing "Generated by Claude Code" footer.
- **Seed locks.** Stage-2a and SCAN share seeds 129001–129008, and so share `LOCKS/seed-*.lock` on one host. This only
  serialises. It does not change behaviour.
- **Seed-rule wording.** §2.3 says the valid counts are "seen at emission". The seed rule is in fact applied at run
  time (`seed_rule`), which is correct. The wording should follow.

## The author's claims

| claim | result | evidence |
|---|---|---|
| (a) nothing under `runs/RBT-129/launch`, `scripts` or `rabbitstew` changes; live SCAN and RB are unaffected | **CONFIRMED** | Tree hashes at the base, at `9e4c89d` and at the head: launch `4478e38`, rabbitstew `144b3b6`, scripts `c0c5a85`, all unchanged. `.gitignore` and `pyproject.toml` are untouched. `stages` reads only the unchanged `RULINGS-CITED-S2.md` from `stage2-plan` (QUARANTINE lines). Nothing in SCAN or RB imports `stage2` or `stage2-plan`. New labels `rbt-129-stage2a-*` are disjoint from `stage1`, `rb` and `scan`. `lanes/S2A` sits under `CLEAN`, but committed files do not dirty it. `git status -- runs/RBT-129/stage2` does not match `stage2a/` (tested). |
| (b) one override, no gate bypass | **CONFIRMED for the listed gates; see BLOCKING 1 for O-2** | The override rebinds `stages.CONTINUATION_PREFIXES` in-process. `continuation()` reads it at call time, so every S2A job goes through `epa_ecology.py`. **FC-3 (exit 9):** `check_host` → `check_continuation_build(launch line)`, `run_job` → `check_continuation_build()`, and `emit`. **Overflow rule (exit 10):** `stages.check_overflow_rule` in `run_lane`. **CRASHED (exit 4):** `check_not_crashed` in `stages.run_job` for fresh, resume and fork. **QUARANTINE:** `check_lane_s2a` on dir, src and ref, plus `_restore`, plus `s60_compare`. **Trees (exit 5):** `check_host` plus `check_own_trees` (but see MAJOR 2). |
| (c) 356 jobs on 20 lanes; S 28,800 / M 5,760 / N 1,920 | **CONFIRMED** | Recomputed from the 20 jsonl files: fresh 96, s60cmp 12, ksalt 24, snapshot 96, resume 96, fork 32; no duplicate names; 96 units, each whole in one lane, in the order S60 → (S60CMP or KSALT) → ckpt60 → S. Arm-seasons S 28,800 (96 × (60 + 240)), M 5,760, N 1,920, as in plan §2.5. Points are the 12 of §1.1. M is at `c1-p018-PW-L`, `c1-p053-U-L` and `c1-p053-U-G`, and N at `c1-p018-PW-L` (§2.3). N nulls are holistic on odd seeds and conventional (designed) on even. Seeds are 129001–129008, the plan's 2a seeds; no R-B seed (129009–129016) is used. Salts are those of `lanes/1/launch.txt`: (0,0), or (1,0) at 129002, 129007 and 129008, and (2,0) at 129003, on fresh and fork alike. K-SALT runs at 129002 and 129003 only, 24 point-seeds. Every world block is committed. Build line v3. 2b(2a) COMMITTED: nothing in 2a depends on it; 2b(2a) lanes are not emitted (they follow the interim), consistent with §2.4. |
| (d) O-2 `s60cmp` | **Right reference, complete comparison; adoption without equality is possible (BLOCKING 1); no leak** | The reference is the census `stage0/<pid>/129001/S` (stock, S 0–59, salts (0,0); the config compare bar `workers` pins seasons and argv). It compares the union of both file sets, so a file "only in" either side is DIFFER. It runs only at season 60, before the S resume. It prints and records the verdict and the differing file **names** only. It is outcome-neutral. |
| (e) exit 10 until GO-ID-2A is open and merged | **CONFIRMED for PENDING, empty, duplicate, wrong value, lower-case, 2B2A missing or duplicated, uncommitted (exit 5, dirty), committed but unpushed (exit 10)** | Bypasses found: same-commit 2B2A (MINOR 5) and failed fetch (MINOR 6). A GO line inside a code fence still counts; that is the parser's documented "begins a line" rule. |
| (f) FC-1, FC-6, FC-D (A1–A3), MAJOR 3 | **CONFIRMED with gaps** | **FC-1:** `local_quarantine_refs` matches every ref against the plan's list, ruled `QUARANTINE:` lines and `stages.quarantined_labels()`; tested. **FC-6:** the parameter is removed. **FC-D:** `registered_epa` refuses unless the blob is `be1f4c5`; the head's `epa_ecology.py` is `be1f4c5`, the same at `7dbb650`; copies deleted. **A2:** seasons 0–59 of `epa_overflow.source.jsonl` only, but fail-open (MAJOR 4). **A3:** every start line's sha, but start lines only (MINOR 8). **MAJOR 3:** §3.1 cites `9b39706` and `708a3af`, both verified as the blobs at `7dbb650` and at the head. |
| (g) `tests/test_rbt129_stage2_plan.py` | **Mostly legitimate; one weakening** | See NOTE 10 and MAJOR 4. |
| (h) full pytest: 1141 passed, 2 skipped | **CONFIRMED** | See below. |
| (i) rebuild v3; exit 10 now | **CONFIRMED** | `scripts/build_mujoco_instrumented.sh instr` from scratch in `/opt/rbt129-mjbuild` (clang/LLD 18.1.3, cmake 3.28.3, ninja 1.11.1) gave `built … sha256 2aea9a9447d68edf07936df0d7d6a0c37b7e2df54441814b20ddd6e96ab763f4`, vfmadd 0. On that venv, `NO_DURABLE=1 …/instr/bin/python runs/RBT-129/stage2/s2lanes.py run-lane runs/RBT-129/lanes/S2A/host0-lane0.jsonl` gave `REFUSED: … does not open the 2a GO …` with **exit=10**. |
| (j) anything else | MAJOR 2, MAJOR 3, NOTE 9 | |

### (h) Test suite

**1141 passed, 2 skipped**, 16 warnings, in 907 s. This ran at the head `755cf8c`, in a clean `.[dev]` venv (Python 3.11.15, mujoco 3.14.0 stock wheel, numpy 2.4.6, no scipy). The trial merge with the base is the same tree (`f7fbb90`), so the same result holds for it. The suite is green, but none of BLOCKING 1, MAJOR 2, MINOR 5 or MINOR 6 is covered by a test.

---

## Fix-check (#533 940fb90)

*`git fetch -q origin +refs/pull/533/head:… +refs/pull/535/head:…` (narrow). The head is `940fb90`, from `622e8d6` (the
fixes) and `940fb90` (the re-emission). The base is unchanged (`247bbfb`). Every gate test ran in a scratch clone whose
`origin` was a local bare repository, with `NO_DURABLE=1`, on my v3 build.*

### Verdict: **MERGE WITH FIXES**

- All eight findings are fixed. MAJOR 3 is ruled and the plan is edited to match.
- The MINOR 7 fix introduces one new MAJOR (**FC-A**). Fix it before `GO-ID-2A`. It does not block the merge, because
  nothing runs until the GO.

| finding | status | evidence |
|---|---|---|
| **BLOCKING 1** (DIFFER adopted on restart) | **FIXED** | See the attack table below. |
| **MAJOR 2** (lanes dead once the GO opens) | **FIXED** | See the scenario table below. |
| **MAJOR 3** (drivers before the first GO) | **RULED; plan amended** | §2.7 item 7, §10 step 3 and §11 now say the drivers come before `GO-ID-2A`. #535 is that round. |
| **MAJOR 4** (A2 and §4.6 fail open) | **FIXED** | `s60_state`: a missing or unreadable source log, `read_log` `unlogged`, or a 0–59 season with no season line gives UNLOGGED. Season-`None` overflows count as OVERFLOWED. A second unit is a HELP. CLEAN results only from a complete log. `unit_state` raises HELP on a foreign-unit line (`check_units`), and an exit with no start gives UNLOGGED. All of these are tested. |
| **MINOR 5** (FC-2) | **FIXED, with a residual** | See the FC-2 table below. |
| **MINOR 6** (failed fetch) | **FIXED** | Origin unreachable gives "the narrow fetch … failed (exit 128)", exit 10. |
| **MINOR 7** (lane equals the emission) | **FIXED, but see FC-A** | `check_emission` rebuilds the lane's slice from the committed inputs. A lane with its `S60CMP` line dropped is refused: "not the emission's lane (first difference at job 2; 17 jobs, 21 emitted)", exit 4. |
| **MINOR 8** (A3 whole) | **FIXED** | `platform_shas` checks the `platform.json` record and every `resumes` entry. A missing record is a HELP. Tested. |
| **NOTE 10** | **FIXED** | `registered_epa` now checks that `__file__` is the hashed file (tested). The footer is no longer mid-file. The §2.3 seed-rule wording is fixed. The `commit` line now names `622e8d6`. It is still unchecked and harmless under a merge commit. |

**BLOCKING 1: the attacks.** I ran `s2lanes.run_job` on synthetic directories under `runs/RBT-129/stage2a/…/129001/`:

| attack | result |
|---|---|
| DIFFER, then a restart | `s60cmp` refuses again (exit 4). `ckpt60`, `S` and `M` each refuse (exit 4, `require_identical`). |
| Verdict file edited to IDENTICAL, marker still DIFFER | Refused. `s60cmp_word` gives DIFFER if either source says DIFFER. |
| Marker edited to IDENTICAL, file still DIFFER | Refused. |
| Marker missing, file says IDENTICAL | `ckpt60` refuses ("no saved S60CMP IDENTICAL"). `s60cmp` re-runs the comparison, which DIFFERs again. |
| Fresh container (no `s60cmp` directory) | `ckpt60` refuses. |
| Restore race | `require_identical` restores `s60cmp` from its branch. `_finished` foreground-saves an unreceipted marker before trusting it, and a DIFFER is `save_now`'d before the refusal. A failed save only means a recomputation, which is deterministic. |
| IDENTICAL path | Runs; the restart skip works. |
| `stages.py run-lane` on an S2A lane | Refused: "not a continuation job, in a continuation lane", exit 4. |

- **One residual (NOTE).** A Python-level call to `stages.run_job(ckpt60_job)` bypasses `require_identical`. No CLI
  exposes this.

**MAJOR 2: the scenarios.** Each ran against the committed `lanes/S2A`, unmodified:

| scenario | result |
|---|---|
| Today | Exit 10. |
| GO opened in its own commit and merged | **ALL GATES PASS (21 jobs).** |
| Same, run at the old PR head | ALL GATES PASS: the GO is read from the base. |
| A `QUARANTINE:` line merged later | Applies at the old HEAD and at the new base (exit 4 for that unit's lane). |
| `GO-ID-INTERIM` opened and a plan prose edit merged later | ALL GATES PASS. |

- **The code pin** covers `s2lanes.py`, `stage2_readout.py` and `stage1_readout.py` by blob. The blobs are identical at
  #535's head, so the stacked merge keeps the lanes runnable. `check_code` refuses any other module loaded from
  `runs/` outside the pinned trees.
- **Import tricks.**
  - `blocks`, `epa_ecology` and `s2lanes` insert ROOT or LAUNCH at `sys.path[0]` only **if absent**. So
    `PYTHONPATH=/elsewhere:<ROOT>` (or `…:<LAUNCH>`) would load `rabbitstew` or `stages` from `/elsewhere`.
  - `check_code` only inspects files under `<ROOT>/runs/`, so it would not see this.
  - This takes a deliberate misconfiguration, and it is inherited from the pinned trees, which cannot change while
    SCAN and RB are live. **NOTE:** `check_code` could also require that `stages`, `blocks`, `mjbuild` and every
    `rabbitstew.*` module's `__file__` sits under ROOT's pinned trees.

**MINOR 5: the FC-2 cases.** All ran in the scratch clone:

| case | result |
|---|---|
| GO and a 2B2A flip in one commit | Refused (exit 10). |
| GO added, removed, re-added | Passes. Correct: the re-add's parent rules 2B2A. |
| GO opened on a side branch, then merged | Passes. |
| An "evil merge" that itself opens the GO, with no ordinary commit ever doing so | Refused ("not in this clone's history"). Pickaxe skips merges, and this fails closed. |
| An evil merge that opens the GO and flips 2B2A after an earlier add/remove | Refused. |
| An evil merge that opens the GO with 2B2A unchanged | Passes. This is FC-2-consistent. |

- **Residual (MINOR).** The walk takes the **latest** commit that changed the GO line's count. Take this sequence: GO
  opened, 2B2A then flipped, the GO closed and re-opened. It passes (verified). FC-2's purpose is that 2B2A is fixed
  before any 2a data exist. So the check should also require the 2B2A value at the **first** opener's parent
  (`opened[-1]`), and that it never changed since.
- **Shallow clones.**
  - They refuse with exit 10 when the opener or its parent is beyond the boundary. That is safe: it fails closed.
  - But the base gains about 56 commits a day (2026-10-03), and the default cloud clone depth is 50. A lane host cloned
    a day or more after the GO opens will refuse.
  - **The runner recipe should say:** `git fetch -q --shallow-since=2026-10-03 origin
    +refs/heads/claude/new-session-4cao7d:refs/remotes/origin/claude/new-session-4cao7d`. It is narrow, and deepens
    past the 2B2A commit. Or clone with a depth that covers the GO commit's parent.

### FC-A. MAJOR (new, from the MINOR 7 fix): one CRASHED or quarantined unit stops its whole lane for good

- **The remedies are now impossible.** `stages.check_not_crashed` refuses a CRASHED run with "re-emit the lane without
  it" (exit 4). A merged `QUARANTINE:` line refuses the unit's lane (exit 4). But `check_emission` now refuses any lane
  that is not exactly `s2a_units`' slice. `s2a_units` knows no crash or quarantine, so neither remedy is possible.
- **Reproduced.**
  - A committed lane with the CRASHED unit's jobs removed: "not the emission's lane (first difference at job 1; 15 jobs,
    21 emitted)", exit 4.
  - The quarantine case: exit 4 at both HEADs.
- **The consequence.** Rule §4.3 says an attested crash "does not stop the hive". Here one does stop the other ~4 units
  of its lane (14–21 jobs per lane). They stay stopped until someone changes `s2lanes.py`. That changes the code
  pins, forces a re-emission mid-stage, and is a code change after data exist.
- **Fix.** Let `s2a_units` / `check_emission` drop the units of CRASHED and quarantined run directories from the
  rebuilt emission, with the rest unchanged.
  - The CRASHED set comes from each unit's EPA log or crash record, through `crash_state` (an attested-only test, no
    outcome).
  - The quarantined set is the base's `QUARANTINE:` labels.
  - Also skip an S60CMP-DIFFER unit's later jobs, so they do not stop the lane, if the coordinator wants HELP confined to
    that unit.
  - Test the "re-emit without it" path end to end.

### NOTE. The scratch-clone run I started by mistake

- In one smoke test, I ran `s2lanes.py run-lane` in the scratch clone at a commit whose **local** fake base had the GO
  open. Every gate passed. That is further evidence that MAJOR 2 is fixed.
- The lane started `S2A/c1-p018-PW-L/129001/S60` (a fresh S 0–59 on the build). I killed it after about two minutes.
- It ran with `NO_DURABLE=1`, against a local bare-repo origin. Nothing was saved, pushed or read back. The scratch
  output was deleted unread.
- No real lane was launched and no real lock was touched. I disclose this for completeness.

### Test suite at #533's head

Running at the time of this commit; the result follows in the next commit.

---

## Review of #535 (1c95078)

*#535 is stacked on #533 (`fd676df` and the merge `1c95078`). It adds `runs/RBT-129/stage2/s2readout.py`,
`tests/test_rbt129_stage2_readout.py` and a §11/§14 edit. Pinned trees: launch `4478e38`, rabbitstew `144b3b6`,
scripts `c0c5a85`, all unchanged. The code pins in `lanes/S2A/launch.txt` are unchanged at #535 (the same three
blobs). The trial merge of #533 and #535 into the base is the same tree as #535's head (`ced028a`).*

### Verdict: **MERGE WITH FIXES**

- **R-1 to R-4 (MAJOR) must be fixed and fix-checked before merge.** This PR is §2.7 item 7's gate.
- Its structure is sound:
  - integrity runs first and fails first;
  - the interim prints only what S2-R3 allows;
  - the calls are Stage 1's;
  - the C3-1, C3-2 and C3-3 pins are wired.
- **What is wrong:** the crash path, several registered outputs, the OVERFLOW-SENSITIVE coverage and the 2b(2a) input
  are incomplete or unreachable.

### What I verified

| item | result |
|---|---|
| **Integrity first** | `interim` and `final` call `integrity()` before anything else and hand its lines to `on_integrity`, which `main` writes before computing. Any failure raises `Help`, and nothing further is read. |
| **Integrity covers** | every lane job's done-marker; `unit_state` (A3 whole, foreign unit, unattested crash, UNLOGGED); `s60_state` for M/N; `s60cmp_word` IDENTICAL; K-SALT with N-3; the crash ceiling; the standing sentence. |
| **The interim prints only what S2-R3 allows** | integrity; the 2B2A line; the R4 list with CP; the core-h upper bound; a "nothing else" line. No call, no §8 line, no x̄ (the test checks the words). The 2a calls are computed under BH over Stage-1 ∪ 2a at n = 8 (O-15) and dropped. |
| **The calls are Stage 1's** | `call_map` re-assembles `call_points`. I checked equivalence on the test's synthetic Stage-1 tree: on all 36 points, `sr.call_points` and `call_map` give **identical body and income calls (0 differences)**. Verdicts, BH, BY, Holm, `world_model`, `fieller`, `scorecard`, `rb_select` and `body_call` are `stage1_readout`'s, unaltered. The Stage-2 deltas are only the plan's: per-stage K2 (C3-1, `share_void`), the combination at extended points, and `crash_bounded_body`. |
| **C3 pins** | C3-1 `share_void` (yes); C3-2 `v5_mark` plus the literal line (yes); C3-3 `scorecard_item2` (yes); C3-4 RESOLVING over every completed M seed, through `call_points`' logic (yes); **C3-5: no** (R-2). |
| **HELP coverage** | missing marker, S60CMP not IDENTICAL, wrong build, unattested crash, the ceiling, K-SALT not PASS, foreign unit, a point with n < 1. All are tested except K-SALT and n < 1. |

### Findings

**R-1. MAJOR: the readout cannot read a real crash, and the end-to-end test only shows otherwise because its fixture
fabricates done-markers.**

- **Integrity needs a done-marker on every lane job.** `stage_integrity` raises "no done-marker" for any job without
  one, and `stage_states` does the same.
- **A CRASHED run never gets one.**
  - `crash_state` needs the last two attempts to exit natively.
  - `stages.check_not_crashed` refuses any further attempt.
  - `_finish` follows only a zero exit.
  - The unit's dependent jobs never run either: after an S crash, its S resume (if the crash is in S60), ckpt60, M and N;
    after an M crash, nothing later.
  - So every real crash makes the interim and the final **HELP forever**. That contradicts rule §4.3 ("the hive does not
    stop"; n is one lower) and plan §3.4's CRASHED column.
- **Re-emitting R-B's lanes without the unit** (its documented remedy) makes the unit vanish from `lane_jobs`. Its S
  state then defaults to **UNSCANNED**, which `keep_seed` keeps, so the partial run would be **read**.
- **The fixtures are unreachable states.** `_rule_cases` and `test_an_unattested_crash…` write
  `_crash_log(...)` over runs that `_continuation` already marked done, with intact ckpt60 histories. For example, an S
  that "crashed" at seasons 0–4 still has its ckpt60 at 59. No real run can be in that state.
- **Fix.**
  - Derive the continuation units from the emission (`s2a_units` / `rb_units`), not from the current lane files.
  - Classify a job with no marker whose run directory meets `crash_state` as CRASHED (attested, or HELP), and its
    downstream jobs as "no fork source", which rule §4.3 counts as CRASHED, one event.
  - Rebuild the fixtures from real crash shapes: no marker, no ckpt60 or no later arms, a crash in S60 and one in the
    resume.

**R-2. MAJOR: the final map leaves out registered outputs.**

| missing output | where it is registered |
|---|---|
| **MARGINAL on EARNS calls**, with C3-5's amended per-birth window. `per_birth_uncensored` is never called; `assemble` passes `with_regime=False`, so no per-birth or regime value is computed at all. | §2.2, §3.4 ("per-birth income, MARGINAL, regime: included"), §4.5 (8/8 → 2/8), S2-R1 C3-5 |
| The **M row** `M k of n (j CRASHED)` with y′'s bound under arbitrary missingness, and the exclude-mode bound for an excluded OVERFLOWED M seed (rule §3.3: y′ in [−s₀, 1 − s₀]) | §3.4, rule §3.3 and §4.5 |
| **M6** κ | §5.4 |
| **M1** counts with the Stage-2a points in their own block. Only M4 weighted shares are printed, under an "M1 and M4" heading. | §5.4 |
| The **overflow-pattern** disclosure: more than 5% of a stage, or 3 or more at a point | rule §3.4 |
| The **scorecard for the Stage-1 points** beside the final one | §5.7 |

- These are pre-registered outputs. Adding them after data would be discretion.

**R-3. MAJOR: OVERFLOW-SENSITIVE is compared on too little.**

- **What is compared.** Per point, the body and income calls. On the headline, `verdict[0]` only.
- **What rule §3.3 and plan §3.4 require:** "every call, family decision, map statistic and verdict that differs", with
  the difference **listed beside its primary** (rule §5 item 4).
- **Not compared:** the verdicts that also hold (`verdict[1:]`); the VARIANCE-DRIVEN and RESOLVING marks; each family's
  BH membership; M2 sensitivity, M3 rows, M4 shares, M7 and the cross-correlation; the scorecard; and V5.
- **Never printed:** the exclude-mode values beside the marked lines. Only a bare mark appears.
- **Fix:** diff every printed quantity between `maps["include-flagged"]` and `maps["exclude-known-flagged"]`, mark each
  difference, and print the sensitivity value beside it.

**R-4. MAJOR: nothing pins or checks the 2b(2a) input.**

- **No check on `lanes/S2B`.** `final_halves` reads whatever `lanes/S2B` lists. Its emitter does not exist (the test
  hand-writes S only), and nothing checks that its points equal the interim's R4 list, or that its seeds, salts and M/N
  arms match plan §2.4.
- **So the 2b(2a) design would be written after the coordinator has seen the R4 list.** That includes which R4 points
  get M and N. The interim's `m_pts`/`n_pts` also cap M at 6 without deducting GO-1's M at `c2-p030-U-G`, which plan
  §2.4 says is shared.
- **Fix:**
  - write the 2b(2a) emitter in this round, as a pure function of the recomputed R4 list and the gate;
  - make `final` recompute the R4 list and refuse unless `lanes/S2B` is exactly that emission;
  - deduct GO-1's M slot.

**R-5. MINOR: crash accounting gaps.**

- `crash_s` (CRASH-AFFECTED) reads `states["2a"]` for 2a points and `states["rb"]` for Stage-1 points only. A CRASHED S
  in **2b(2a)** never marks CRASH-AFFECTED. `crashed_s_merges` does see it, so the body bound and the income mark
  disagree.
- A CRASHED **N** is silently dropped by `arms_for`. It is in no list, has no count beside the call, and gets no bound.

**R-6. MINOR: Stage 1's M and N are not restored by `interim` or `final`.**

- Only `S` and `ckpt60` are restored. `stage1_readout.readout` also restored M and N.
- In a fresh container, `assemble_point` → `read_run` raises `FileNotFoundError`, an uncaught traceback rather than a
  `Help`.

**R-7. MINOR: the registered Stage-1 values are recomputed, not checked.**

- §5.5 says T1–T3 and Holm are the registered L410–L412 values and are "not re-run". `final` refits them (and Stage-1
  habitability) from the restored data through `call_map`.
- Equivalence holds on synthetic data (above). But nothing at run time checks the refit against the committed Stage-1
  record.
- **Fix:** refuse (HELP) unless the Stage-1 calls and T1–T3 equal `stage1_readout.txt`'s, or print the registered
  values.

**R-8. MINOR: the end-to-end test is shallow.**

- Restore is a no-op, RESOLVING is stubbed off (`NO_RES`), and 2b has no M or N.
- The crash fixtures are unreachable (R-1).
- The final-map assertions only check that sections exist and that the table has 48 rows. No call, verdict or mark is
  checked against an expected value. For example: EARNS-H at the U points; OVERFLOW-SENSITIVE where the excluded seed
  changes a call; V5-TOLERANCE-SENSITIVE.

**R-9. NOTE: the interim prints SKIPPED counts by arm.**

- These count M/N forks skipped by the seed rule or pre-merge extinction. They are pre-merge survival at the gated points.
- The plan lists "units done, CRASHED, OVERFLOWED and UNLOGGED counts by arm". Fold SKIPPED into done.

**R-10. NOTE: edge cases and display.**

- With `2B2A: COMMITTED` and an empty R4 list, `lanes/S2B` never exists, and `final` raises HELP ("holds no job").
- Rule §4.2 says a crash adds CRASHED on top of OVERFLOWED. The counts book only CRASHED, so an overflowed-then-crashed
  arm's overflow is not counted as OVERFLOWED.

### Test suite at #535's head (= the trial merge of #533 and #535 into the base)

Running at the time of this commit; the result follows in the next commit.

---
_Generated by [Claude Code](https://claude.ai/code)_
