# RBT-129 continuations: the EPA overflow rule (DRAFT, for the coordinator to rule on)

- **Status: DRAFT. Not registered.**
  - R-B's GO (`RBT129-RB-GO-1`; OWNER-DECISIONS-2026-10-03 item 3) is gated on a registered overflow rule.
  - `stages.py run-lane` refuses every R-B lane (exit 10) until `runs/RBT-129/continuations/OVERFLOW-RULE.md` is
    committed with a line `REGISTERED: <ruling ID>`. This draft does not have that line, and it is under another name.
- **When it must be ruled:** before any R-B data exist. Stage 2 adopts the same rule, or its plan amends it before
  Stage-2 data exist (owner decision 4).
- **Outcome-blind.** Written before any continuation has run. The only RBT-129 outcomes the author has seen are the
  committed Stage-1 readout and the crash diagnosis (#520, #521).
- **What it covers.** Every RBT-129 continuation: R-B, Stage 2a/2b, and any later arm on the instrumented build. Not
  the Stage-1 silent-corruption scan: its result is a Stage-1 integrity finding for a separate ruling (§6).

## 1. What the log can show

Every continuation runs on the guard-off instrumented MuJoCo 3.14.0 (`scripts/build_mujoco_instrumented.sh`). **On
every trajectory without an overflow** its physics is stock 3.14.0's, byte for byte (`IDENTITY.md`). **At and after an
overflow no such claim is made** (COORD-RULING-520 D3, FC-2): both builds are then in undefined behaviour, and what each
does is build-specific (memory layout, which read lands where). Post-overflow behaviour of this build, crash or no
crash, is **not evidence about stock**. The `epa_overflow.jsonl` record of the overflow is the signal, and the rule
below acts on that record alone. The build writes the run's `epa_overflow.jsonl`, with these lines:
- one per EPA iteration whose horizon has **17 to 24 edges: a near miss**. The arrays hold 24, so nothing is written
  out of bounds, and the physics is well defined;
- one per EPA iteration whose horizon has **more than 24 edges: an overflow**. Stock MuJoCo writes past the 24-entry
  arrays (google-deepmind/mujoco#3646). What follows is **undefined behaviour**:
  - a later read of the corrupted entry may fault (the Stage-1 crash, `RULING.md`);
  - or it may build a wrong contact that step, with no crash (silent corruption; #521 MAJOR 2).

  The build cannot tell these two apart. It only guarantees that every overflow is recorded, with its season, the
  `mj_step` within the bout, the horizon size and the geom pair.

Definitions used below:
- **Arm-seed:** one arm (S, M or N) of one seed at one point, for example `RB/c2-p030-U-G/129010/M`.
- **The S60 phase:** an arm-seed's seasons 0–59. M and N fork from S's season-60 state (ckpt60), so an event in S's
  S60 phase sits upstream of S, M and N of that seed alike.
- **A season's events:** taken from the season's last attempt (`epa_ecology.read_log`). A killed run resumes from its
  last saved season and runs the rest again, so only the attempt that produced the kept data counts.

## 2. Case (iii): near misses only (horizon 17–24, no overflow)

- **What happens to the unit:** nothing. It is not flagged, excluded or put through any sensitivity analysis. Its
  physics is stock 3.14.0's and well defined.
- **What the readout prints**, in the integrity section, per stage and arm:
  - the number of arm-seeds with at least one near miss;
  - the total number of near misses;
  - the largest horizon seen;
  - the EPA iterations logged (the histograms).
- **Purpose.** Near misses are the exposure figure: the rate at which the regime approaches the cap. They are
  descriptive. They enter no call, family, verdict, R-A or R-B rule.

## 3. Case (i): an overflow is logged and the run does not crash

### 3.1 The state

- The arm-seed is **OVERFLOWED**. Like CRASHED (`RULING.md` item 1), this is a unit state, not a call.
- An overflow in S's S60 phase makes **S, M and N of that seed** OVERFLOWED: they all descend from the
  post-overflow state.
- An overflow in S after season 59, or in M or N, makes **only that arm-seed** OVERFLOWED.
- **The state follows from the logged overflow line alone** (FC-2), whatever the run does afterwards: completing,
  crashing (§4), or diverging from any reference. Nothing after the event is read as evidence that it was harmless or
  harmful.
- **Nothing is re-run, resumed from an earlier state, or replaced.** The reasons are those of `RULING.md` item 2: a
  re-run of the same state reproduces the same event (the build is deterministic), and a perturbed re-run is a
  substitute seed.

### 3.2 The primary analysis: kept, flagged

- **The OVERFLOWED arm-seed is kept as observed** in every registered computation.
- **Why kept, not dropped** (for the coordinator to weigh):
  1. **Excluding it is outcome-correlated missingness.** Overflow risk is a property of the physics regime (deep
     overlaps of smooth geoms; DIAGNOSIS (d)). So it may differ by fauna body, terrain and point. Dropping such seeds
     selects on that regime.
  2. **The stock code's writes are small in scope.** In the stock source, the out-of-bounds writes land in `mjData`'s
     per-step stack arena, which is re-carved every step. This is an argument from reading the code, about stock; it
     is **not** supported by anything this build does after an overflow (FC-2), and the coordinator may give it no
     weight.
  3. **There is a precedent.** Stage 1 already keeps runs with silent physics discontinuities, namely MuJoCo's
     `mjWARN_BADQACC` auto-resets (DIAGNOSIS, Files).

### 3.3 The sensitivity analysis (required)

- Every registered call that uses an OVERFLOWED arm-seed is recomputed **with that arm-seed treated as missing**.
- Where a logical bound exists, its **logical bounds** are also printed. This is the treatment `RULING.md` item 4
  gives the CRASHED seed: y′ in [−s₀, 1 − s₀], under the readout's convention for an emptied world. Income flow has
  no such bound, and the readout says so.
- If the call differs between the primary and the sensitivity analysis, it is labelled **OVERFLOW-SENSITIVE** in the
  map and in every verdict that counts it. The label never changes the call. It is disclosed beside it.

### 3.4 Escalation

- **Before the readout:** if more than 5% of a stage's arm-seeds are OVERFLOWED, or any one point has 3 or more, the
  coordinator re-rules before the readout plan is committed. The overflow is then a pattern, not an incident.
- **During the run:** the lane runner prints each overflow as it happens. The line gives the job name and the count
  only, with no season (it is integrity, not outcome). In-flight lanes go on.

### 3.5 The alternative, for the coordinator to choose instead

- **Excluded, primary.** OVERFLOWED arm-seeds enter no call, exactly as CRASHED does.
- The sensitivity analysis then runs the other way: kept as observed.
- This trades the missingness bias of point 1 above for robustness to undefined behaviour.
- The draft recommends §3.2 (kept). Either way, both analyses are printed, so the choice decides only which one is
  primary.

## 4. Case (ii): the run crashes

### 4.1 What counts as a crash

- The rule is `RULING.md` item 5, unchanged: two attempts in a row of the same job fault inside libmujoco, one of them
  at WORKERS=1.
- `RULING.md`'s "same instruction" is **replaced by "inside libmujoco, in the convex collider"**, as DIAGNOSIS (c)
  recommends. One overflow can fault at different instructions in different process layouts (`projectOriginPlane`+5
  on host1; `mj_narrowphase` in the standalone replay).

### 4.2 Attested and unattested crashes

The run's `epa_overflow.jsonl` decides which kind of crash it is.
- **The overflow rule applies first** (FC-2). An arm-seed whose log holds an overflow line is OVERFLOWED by §3,
  whether or not it then crashed; a crash adds the CRASHED state on top, and the crash itself is not evidence about
  what stock would have done.
- **CRASHED (EPA overflow, attested).** In each of the two attempts, the attempt's last season line is followed by an
  overflow line written by one of that attempt's processes.
  - The library writes that line with a single `write(2)`, before the corrupted read that faults, so it survives the
    SIGSEGV.
- **CRASHED (unattested).** Anything else, for example a fault with no overflow logged in that attempt. Its mechanism
  is unknown.
- **Who checks.** A crash-only check reads the log for that test alone. It reports **attested yes or no**, never the
  season, step, geom or any outcome. The log of a crashed arm-seed sits on its quarantined branch (§4.4).

### 4.3 What each kind of crash means

| crash | in S | in M or N |
|---|---|---|
| **attested** | The arm-seed is CRASHED. Its seed's income-layer value is missing at that point, so the point's n is one lower (for example 15 of 16 in R-B). **The hive does not stop**: the mechanism is known, and its rate is what the log measures. A crash in S's S60 phase also leaves M and N of the seed with no fork source: they are CRASHED too. | The arm-seed is CRASHED, as `RULING.md` item 1 defines it. **M/N lane issuance does not stop** (unlike `RULING.md` item 5). The pattern the item-5 stop guarded against is now attested to be a known physics bug, not an unknown process. |
| **unattested** | **The hive stops**, as `RULING.md` item 5 has it for any S crash. Then HELP. | `RULING.md` item 5 applies as written: M/N lane issuance stops, in-flight jobs finish, and nothing is excluded, re-run or replaced until the coordinator re-rules. |

### 4.4 For every crashed arm-seed

- **No re-run, no substitute seed, no resume from an earlier state** (`RULING.md` item 2).
- **For the CRASHED Stage-1 unit:** `1/c2-p030-U-G/129001/M` stays CRASHED. R-B's seeds 9–16 at `c2-p030-U-G` are
  never its stand-in, so M there is at most 15 of 16.
- **Quarantine** (`RULING.md` item 3):
  - The partial run's branch is kept and never restored or read, except by the crash-only check of §4.2.
  - Its `epa_overflow.jsonl` is part of that branch. Its season lines would show how far the run got, so it is not
    copied into any report.
  - The readout refuses the label mechanically.
- **In the readout:** the arm-seed enters no M1 or M4 category, and no mean, table or figure.
  - Its sensitivity output is the logical bound of §3.3, where one exists, labelled "bound under arbitrary
    missingness".
  - It counts against no registered stop rule (`RULING.md` item 1).

## 5. Disclosure (every continuation readout's integrity section)

1. **The build.**
   - Every continuation run's `platform.json` records `mujoco_build`, in its top-level record and in every `resumes`
     entry.
   - Each must carry `libmujoco_sha256` = `7ae75f7f…` (`mjbuild.INSTR_SO_SHA`) and the build marker.
   - The aggregate is PASS or FAIL, as READOUT-PLAN §2.6 does for the version. Any other build: HELP.
2. **The log.**
   - Every continuation run has `epa_overflow.jsonl`.
   - The log has a season line for every season the run ran, from its last attempt.
   - A run with a season unlogged is **UNLOGGED**. It is treated as OVERFLOWED (§3) and listed. The log is the only
     evidence that an overflow did not happen.
3. **The counts, per stage and arm:**
   - arm-seeds with a near miss, and the total number of near misses;
   - the largest horizon;
   - OVERFLOWED arm-seeds and overflow events;
   - CRASHED arm-seeds (attested or unattested);
   - EPA iterations logged.
   - Arm-seeds are named for OVERFLOWED and CRASHED only. A near miss is not named.
4. **The labels.** Every OVERFLOW-SENSITIVE call is listed beside its primary call.
5. **The standing sentence**, printed whatever the counts:

   > Continuations ran on MuJoCo 3.14.0 with an instrumented build that is byte-identical to stock on every
   > trajectory without an overflow (and makes no claim at or after one). The build logs every EPA
   > horizon overflow (google-deepmind/mujoco#3646), a memory-safety bug that can corrupt a contact without crashing.
   > Every overflow in these runs is therefore known and handled by the registered rule. Stage-1 units outside the M/N
   > silent-corruption scan were not checked this way.

## 6. Not covered here

- **The Stage-1 scan.** If it finds a Stage-1 M or N unit with an overflow, or one that does not replay byte for byte,
  that is a Stage-1 integrity finding. The coordinator rules on it against the accepted Stage-1 record (COORD-RULING-517
  C1), which this draft does not touch.
- **The S scan** (~600–800 core-h) is the owner's later decision (owner decision 1).
- **A memory-safe build.** Upstream #3650, or the 6N sizing, would change physics at overflow events. That is option
  (b), not chosen. If it is ever adopted, it needs its own registration.

---
_Generated by [Claude Code](https://claude.ai/code)_
