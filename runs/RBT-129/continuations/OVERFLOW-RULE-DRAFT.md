# RBT-129 continuations: the EPA overflow rule (DRAFT r2, for the coordinator to rule on)

- **Status: DRAFT r2. Not registered.**
  - R-B's GO (`RBT129-RB-GO-1`; OWNER-DECISIONS-2026-10-03 item 3) is gated on a registered overflow rule.
  - `stages.py run-lane` refuses every R-B lane (exit 10) until `runs/RBT-129/continuations/OVERFLOW-RULE.md` is on
    `origin/claude/new-session-4cao7d`, committed and unmodified, with exactly one `REGISTERED: RBT129-<id>` line and
    exactly one `OVERFLOW-RULE: include-flagged` (or `exclude-known-flagged`) line. The coordinator writes that file;
    this draft is under another name and has neither line.
- **r2.** Revised for the #527 adversary review (`runs/RBT-129/continuations-adversary/ADVERSARY.md`, PR #531), as the
  coordinator scoped it: W1–W9 (Part 2), MAJOR 4 (the scan is CLEAN for seasons 60–299 only) and MAJOR 6 (the ceiling
  counts crash **events**). Section numbers are kept where they did not change; §3.5 is gone (W1).
- **When it must be ruled:** before any R-B data exist.
- **One rule for R-B and Stage 2** (coordinator, 2026-10-03 13:02). The coordinator registers it as a standalone ruling
  from this draft and the Stage-2 plan's section. The record fields and the attestation test (§4.2) are agreed with the
  plan author (`session_014peDKmK8Qdna38Zav4JWNH`; #523).
- **Outcome-blind.** Written before any continuation has run. The only RBT-129 outcomes the author has seen are the
  committed Stage-1 readout and the crash diagnosis (#520, #521).
- **What it covers.** Every RBT-129 continuation: R-B, Stage 2a/2b, and any later arm on the instrumented build. The
  Stage-1 silent-corruption scan is a Stage-1 integrity finding for a separate ruling (§6); its state names are fixed
  here (§6.1) so that ruling reads them as defined.

## 1. What the log can show

Every continuation runs on the guard-off instrumented MuJoCo 3.14.0 (`scripts/build_mujoco_instrumented.sh`). **On
every trajectory without an overflow** its physics is stock 3.14.0's, byte for byte (`IDENTITY.md`). **At and after an
overflow no such claim is made** (COORD-RULING-520 D3, FC-2): both builds are then in undefined behaviour, and what each
does is build-specific. Post-overflow behaviour of this build, crash or no crash, is **not evidence about stock**. The
`epa_overflow.jsonl` record of the overflow is the signal, and the rule below acts on that record alone.

The build writes the run's `epa_overflow.jsonl`:
- one line per EPA iteration whose horizon has **17 to 24 edges: a near miss**. The arrays hold 24, so nothing is
  written out of bounds, and the physics is well defined. Near-miss lines are written best effort;
- one line per EPA iteration whose horizon has **more than 24 edges: an overflow**. Stock MuJoCo writes past the 24-entry
  arrays (google-deepmind/mujoco#3646). The first effect is a corrupted horizon entry in the same EPA call; a wrong
  contact then enters the state and persists. What follows is **undefined behaviour**: a fault (the Stage-1 crash), or a
  wrong contact with no crash (silent corruption; #521 MAJOR 2). The build cannot tell these apart.
- **It writes every overflow, before EPA reads the overflowed arrays, unless the log write itself fails; then the
  process aborts** (W8, MINOR 9; build `rbt129-epa-instr/3`). An overflow is therefore either in the log or the run
  ended in an unattested crash (§4).

**Definitions (W9).**
- **Arm-seed:** one arm (S, M or N) of one seed at one point, for example `RB/c2-p030-U-G/129010/M`.
- **Run directory / unit id:** the directory one job writes; its id is its checkpoint label (`unit` on every log line).
- **The S60 phase:** seasons 0–59 of the run that wrote the ckpt60 the arm forked from. For R-B and Stage 2 that is the
  seed's own `…/S60` run directory. For Stage 1, see §6.1.
- **Attempt:** one start of a run directory's ecology (`attempt` = 1 + the earlier starts, across restarts and resumes).
- **Kept data:** a season's events are the **union over every attempt that ran it** (`epa_ecology.read_log`). A killed
  run resumes from its last saved season and runs the rest again; an overflow once logged is never un-seen (MINOR 11).
- **Near-miss threshold and cap:** 17 and 24, fixed by the build and its wrapper (`RBT_HZN_NEAR` is set by the wrapper;
  it is not a lane parameter).
- **The hive:** all RBT-129 continuation lanes, R-B and Stage 2 alike.

## 2. Case (iii): near misses only (horizon 17–24, no overflow)

- **What happens to the unit:** nothing. It is not flagged, excluded or put through any sensitivity analysis.
- **What the readout prints**, in the integrity section, per stage and arm: the number of arm-seeds with at least one
  near miss; the total number of near misses; the largest horizon; the EPA iterations logged. **No arm-seed is named for
  a near miss.**
- They are descriptive: the exposure figure. They enter no call, family, verdict, R-A or R-B rule.

## 3. Case (i): an overflow is logged and the run does not crash

### 3.1 The state

- The arm-seed is **OVERFLOWED**. Like CRASHED (`RULING.md` item 1), this is a unit state, not a call.
- An overflow in the S60 phase makes **S, M and N of that seed** OVERFLOWED: they all descend from the post-overflow
  state. An overflow in S after season 59, or in M or N, makes **only that arm-seed** OVERFLOWED.
- **The state follows from the logged overflow line alone** (FC-2), whatever the run does afterwards: completing,
  crashing (§4), or diverging from any reference.
- **Nothing is re-run, resumed from an earlier state, or replaced** (`RULING.md` item 2): a re-run of the same state
  reproduces the same event (the build is deterministic), and a perturbed re-run is a substitute seed.

### 3.2 The primary analysis: `OVERFLOW-RULE: include-flagged`

- **The OVERFLOWED arm-seed is kept as observed** in every registered computation, flagged.
- **Why** (W5: the only reason kept): excluding it is outcome-correlated missingness. Overflow risk is a property of the
  physics regime (deep overlaps of smooth geoms; DIAGNOSIS (d)), so it may differ by fauna body, terrain and point;
  dropping such seeds selects on that regime.
- **Fixed now (W1):** `include-flagged` is the primary analysis and `exclude-known-flagged` is the sensitivity analysis.
  There is no alternative left to choose after data.

### 3.3 The sensitivity analysis (required; W4)

- Under `exclude-known-flagged`, **the whole final map is recomputed** with every OVERFLOWED arm-seed treated as missing:
  every call, every family's BH, Holm, every map statistic and every verdict (Stage-2 plan §3.4).
- Where a logical bound exists for a missing seed, it is printed too (the treatment `RULING.md` item 4 gives the CRASHED
  seed: y′ in [−s₀, 1 − s₀], under the readout's convention for an emptied world). Income flow has no such bound, and the
  readout says so.
- Every call, family decision, map statistic and verdict that differs between the two is marked **OVERFLOW-SENSITIVE**;
  on the headline, the mark sits on the headline line. The mark never changes the call.

### 3.4 A pattern of overflows (W2)

- If more than 5% of a stage's arm-seeds, or 3 or more at one point, are OVERFLOWED, the readout **adds** a disclosure
  line ("overflow is a pattern at …"), and the OVERFLOW-SENSITIVE marks are printed on every affected line.
- The primary analysis, the sensitivity analysis and every call stay as registered. **No re-rule is triggered by
  overflow counts.**
- During the run, the lane runner prints each job's overflow count, with no season (integrity, not outcome). Lanes go on.

## 4. Case (ii): the run crashes

### 4.1 What counts as a crash

- `RULING.md` item 5's count: two attempts in a row of the same run directory exit natively (a fatal signal inside
  native code), one of them at `workers` 1. From the log: the run's last two `exit` lines are consecutive attempts, both
  `native: true`, and one of the two `start` lines has `workers: 1` (`epa_ecology.crash_state`).
- `RULING.md`'s "same instruction" is **replaced by "a native exit"**, as DIAGNOSIS (c) recommends: one overflow can
  fault at different instructions in different process layouts.

### 4.2 Attested and unattested crashes

- **The overflow rule applies first** (FC-2). An arm-seed whose log holds an overflow line is OVERFLOWED by §3, whether
  or not it then crashed; a crash adds the CRASHED state on top.
- **Attested, per counting attempt (W6; `epa_ecology.attested`, `native_exit` folded in):** an overflow line of this
  unit and this attempt whose `pid` is a process that died natively in that attempt (a `pool_broken` worker with a fatal
  signal, or the attempt's own pid when its `exit` line carries a fatal `signal`), logged after the attempt's last
  `season` line and before its `exit` line, which has `native: true`.
  - So an overflow the run survived seasons earlier never attests a later, unrelated fault. A mismatch is unattested.
  - The record fields are agreed with the Stage-2 plan: `unit`, `attempt`, `pid`, `seq`, `step` on every library line;
    `unit`, `attempt`, `workers`, `pid` on the `start` line; run-lane's `{"exit": {"attempt", "code", "signal",
    "native"}}`; the wrapper's `pool_broken`.
  - The forced overflow at WORKERS=2 (upstream #3646's pair, in forked pool workers) shows the chain, and shows that a
    log the library cannot open makes the worker abort, leaving an unattested crash (`records/forced-overflow.txt`).
- **CRASHED (attested):** both counting attempts are attested. **CRASHED (unattested):** anything else.
- **Who checks.** A crash-only check reads the log for this test alone and reports **attested yes or no**, never the
  season, step, geom or any outcome. `run-lane` itself refuses (exit 4) to resume a run directory whose log meets §4.1,
  printing "CRASHED (attested yes/no): re-emit the lane without it". After every native exit, `run-lane` saves the log
  alone to `ckpt/<label>-crashlog`, so the evidence outlives a lost container.

### 4.3 What each kind of crash means

| crash | in S | in M or N |
|---|---|---|
| **attested** | The arm-seed is CRASHED. Its seed's income-layer value is missing at that point, so the point's n is one lower (for example 15 of 16 in R-B). **The hive does not stop.** A crash in the S60 phase also leaves M and N of the seed with no fork source: they are CRASHED too (one event, §4.4). | The arm-seed is CRASHED, as `RULING.md` item 1 defines it. **M/N lane issuance does not stop.** |
| **unattested** | **The hive stops.** Then HELP. | `RULING.md` item 5 applies as written: M/N lane issuance stops, in-flight jobs finish, and nothing is excluded, re-run or replaced until the coordinator re-rules. |

### 4.4 The ceiling (MAJOR 6)

> **Ceiling.** Count **attested crash events**: distinct run directories with a CRASHED (attested) state of their own,
> by RULING item 5's count. Arm-seeds made CRASHED only because their fork source crashed are **not** counted. A second
> such event at one point, or a third across GO-1 and Stage 2 together, stops all continuation launches and restarts
> until the coordinator re-rules. Stage-1's `1/c2-p030-U-G/129001/M` is not counted. The M/N scan's replays are not
> counted: a scan crash is a Stage-1 integrity finding (§6).

- An unattested crash already stops at the first (§4.3).

### 4.5 For every crashed arm-seed

- **No re-run, no substitute seed, no resume from an earlier state** (`RULING.md` item 2), on any build.
- **The instrumented build is allowed for new units only** (Stage-2 plan A-11): `RULING.md` item 2's bar on another
  build stands for every CRASHED unit, Stage 1's included.
- **For the CRASHED Stage-1 unit:** `1/c2-p030-U-G/129001/M` stays CRASHED. R-B's seeds 9–16 at `c2-p030-U-G` are never
  its stand-in, so M there is at most 15 of 16.
- **Quarantine** (`RULING.md` item 3): the partial run's branch, its crash record and its EPA log are kept and never
  restored or read, except by the crash-only check of §4.2. The coordinator adds its label as a `QUARANTINE: <label>`
  line (`continuations/QUARANTINE.md`, or the Stage-2 plan's `RULINGS-CITED-S2.md`); `_restore`, the lanes and the
  readers then refuse it mechanically.
- **In the readout:** the arm-seed enters no M1 or M4 category, and no mean, table or figure. Its sensitivity output is
  the logical bound of §3.3, where one exists, labelled "bound under arbitrary missingness". It counts against no
  registered stop rule (`RULING.md` item 1).

### 4.6 Every HELP state has a registered default (W3)

HELP covers: an unattested crash; a missing log or `start` line; a `nostart` exit (a process that died before its start
line, MINOR 7); a foreign unit's line; an UNLOGGED log (§5 item 2); a wrong build sha.

> Default, absent a ruling within the readout window: a HELP arm-seed is read as **OVERFLOWED** (include-flagged with its
> sensitivity) if it completed its seasons, and as **CRASHED (unattested)** if it did not. A wrong sha is never
> defaulted: that arm-seed is VOID and re-run on the registered build from its last state that carries the registered
> sha.

## 5. Disclosure (every continuation readout's integrity section)

1. **The build.** Every continuation run's `platform.json` records `mujoco_build`, in its top-level record and in every
   `resumes` entry, with the registered `libmujoco_sha256` and build marker. The aggregate is PASS or FAIL, as
   READOUT-PLAN §2.6 does for the version. Any other build: HELP (§4.6).
2. **The log.** Every continuation run has `epa_overflow.jsonl` (with any `.prev-<n>` kept across a deleted run
   directory). A run is **UNLOGGED** (W7) when: a season it ran has no `season` line; or a process's histogram
   `overflows` exceeds its overflow event lines; or the log has an unreadable line that is not the final line of an
   attempt; or it holds a `nostart` exit. UNLOGGED is HELP (§4.6) and is listed.
3. **The counts, per stage and arm:** arm-seeds with a near miss and the total of near misses; the largest horizon;
   OVERFLOWED arm-seeds and overflow events; CRASHED arm-seeds and crash events (attested or unattested); EPA iterations
   logged. Arm-seeds are **named for OVERFLOWED and CRASHED only**; a near miss is not named.
4. **The labels.** Every OVERFLOW-SENSITIVE call, decision, statistic and verdict is listed beside its primary.
5. **The standing sentence** (W8), printed whatever the counts:

   > Continuations ran on MuJoCo 3.14.0 with an instrumented build that is byte-identical to stock on every trajectory
   > without an overflow (and makes no claim at or after one). The build logs every EPA horizon overflow
   > (google-deepmind/mujoco#3646), a memory-safety bug that can corrupt a contact without crashing. Every overflow the
   > build logged in these runs is handled by the registered rule. A run whose log is incomplete is treated as
   > overflowed. Stage-1 units outside the M/N scan's seasons 60–299 were not checked this way.

## 6. Not covered here, and the scan's state names

### 6.1 The Stage-1 M/N scan (MAJOR 4)

- Each scan replay starts from the unit's stock ckpt60 and runs seasons 60–299 of its M or N arm on the build.
- **States:** **CLEAN (seasons 60–299)**: no overflow logged in those seasons and a complete log; **OVERFLOWED**;
  **UNLOGGED** (HELP). The S60 phase upstream of every Stage-1 M and N (S's seasons 0–59) is **not** replayed and stays
  **UNSCANNED** until the owner's S scan. No scan state says anything about seasons 0–59.
- A scan unit that does not replay byte for byte (DIFFER) is silent corruption or nondeterminism; that, and any
  OVERFLOWED scan unit, is a Stage-1 integrity finding the coordinator rules on against the accepted Stage-1 record
  (COORD-RULING-517 C1), which this draft does not touch.
- The scan's committed report carries **counts only** (MAJOR 2): totals by arm, and units named only when DIFFER,
  NO-REFERENCE, OVERFLOWED or UNLOGGED.
- Scan crashes are not counted toward §4.4's ceiling.

### 6.2 Elsewhere

- **The S scan** (~600–800 core-h) is the owner's later decision (owner decision 1).
- **A memory-safe build.** Upstream #3650, or the 6N sizing, would change physics at overflow events. That is option
  (b), not chosen. If it is ever adopted, it needs its own registration.

## r1 → r2

| item | change |
|---|---|
| W1 | §3.5 (the alternative left open) deleted; `include-flagged` primary, `exclude-known-flagged` sensitivity |
| W2 | §3.4: overflow counts add a disclosure line and marks; no re-rule |
| W3 | §4.6: a registered default for every HELP state |
| W4 | §3.3: the whole final map is recomputed under the sensitivity analysis |
| W5 | §3.2: reasons 2 and 3 deleted; §1 says the wrong contact persists |
| W6 | §4.2: attestation needs the faulting process, in the faulting season, before a native exit |
| W7 | §5 item 2: UNLOGGED widened; §6.1 the scan's states |
| W8 | §1 and §5.5: no "every overflow is known"; an incomplete log is treated as overflowed |
| W9 | §1: the hive, the S60 phase, the threshold, kept data (union over attempts) |
| MAJOR 4 | §6.1: CLEAN (seasons 60–299); S60 UNSCANNED |
| MAJOR 6 | §4.4: the ceiling counts crash events; an S60 crash is one event; scan crashes not counted |
| MINOR 7, 9, 10, 11 | §1, §4.2, §4.6, §5: abort on a failed write; `nostart` exits; kept `.prev-<n>` logs; union over attempts |
| A-11 | §4.5: the instrumented build for new units only; no CRASHED unit re-run on any build |

---
_Generated by [Claude Code](https://claude.ai/code)_
