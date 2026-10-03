# RBT-129 Stage 2 (2a refinement, 2b extension, the final map): plan (pre-data), r2

*Written 2026-10-03 by the Stage-2 plan author, `session_014peDKmK8Qdna38Zav4JWNH`. Coordinator:
`session_017eUHGNdTSsoVFAtLaJWehF`. Authorised by `coordinator/OWNER-DECISIONS-2026-10-03.md` item 4.*

**r2 is the fix round.** It answers the adversary (#524, head `f63122b`: ADOPT WITH CHANGES, 7 MAJOR, 8 MINOR, 7 NOTE)
under the coordinator's rulings S2-R1 to S2-R4. Those rulings are COORDINATOR-EXPOSED and recorded in
`RULINGS-CITED-S2.md`. §13 maps every finding to its fix.

*Base: `claude/new-session-4cao7d` at `b8e6a01` (#525, COORD-RULING-520, merged in). r1 was `242528f`.*

**Still no Stage-2 data, and nothing launched.**
- No Stage-2, R-B or continuation run exists.
- The quarantined branch `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M` was never fetched, listed or read.
- The only run data read in this round are the S directories of the 8 Stage-1 EARNS points, for the §9.1 computation
  (§4.5), restored through the Stage-1 quarantine guard.

**What this author has seen** (a disclosure, not a peek).
- **Stage 2 is adaptive by design.** R-A chooses its points from the Stage-1 calls (DESIGN §4.2), so the author has read
  the accepted Stage-1 record in full.
- **Every rule that Stage-1 outputs could have motivated is labelled DATA-INFORMED.** That covers all five C3 pins (§4).
- **S2-R1 removes the author's discretion from the pins.** Wherever the plan's text and the pre-data committed code
  disagree, the code governs.

**Inputs read in r1.**
- `DESIGN.md` r4 and `AMENDMENT-FOUNDING.md` §7;
- all of `stage1-readout/`, and the run adversary;
- `mn-crash/` (RULING r3, INTEGRITY, REPRO) and the crash PRs #520 and #521;
- `coordinator/`;
- `calibration-final/DECISION.md`;
- the lanes and gate table of Stage 1;
- `stageP0_readout.txt`;
- source: `stages.py`, `provenance.py` and `regime.py`.

**Added in r2.**
- the adversary report and its probes (#524);
- `mn-crash/COORD-RULING-520.md` (#525);
- the continuations tooling branch `claude/rbt129-continuations-tooling` at `772af97`: `continuations/README.md`,
  `OVERFLOW-RULE-DRAFT.md` and `launch/epa_ecology.py`. Its PR is not yet opened;
- `scripts/regime.py:175`.

**The labels.** Every call, table and map carries the claim label (T4), **"among holistic and designed stream draws
(founders and their early history) that establish at W118-b"**. Every share line also carries **"under the committed
rule"**, and every verdict carries **"earns, not persists"**.

## 0. In one table

| question | answer | § |
|---|---|---|
| what Stage 2 is | 2a: R-A's 12 points at n = 8 (seeds 129001–129008). 2b: R-B to n = 16 (seeds 129009–129016). Then the final map: BH once over every point with R-B's combined p-values, and §8 | 1 |
| 2a arms | S at 12 points × 8 seeds × 300 seasons. 129001's S 0–59 is re-simulated on the build and adopted only on byte equality with the census (O-2, REQUIRED pending the owner's cost OK). M at 3 points and N at 1 (T5 gate), 240 seasons, on valid seeds | 2 |
| 2b | the 9 Stage-1 points are R-B **GO-1** (another session's tooling; read here only). Stage-2a points: ≤ 11, by R4. **The owner commits or declines 2b(2a) before any 2a data exist** (`2B2A:`) | 1.2, 2.4 |
| core-h (upper bounds; low / high) | **2a ≤ 236.6 / 443.0. 2b(2a) ≤ 221.0 / 413.9. Total ≤ 457.7 / 856.9.** If the owner declines O-2's re-simulation: 2a ≤ 231.9 / 434.3, total ≤ 453.0 / 848.2. GO-1 is separate | 2.5 |
| not run | the probe leg: perception, levers and T4 are **UNREADABLE** at a = 6. Retention and the sub-studies are outside Stage 2 | 2.6 |
| build and overflow | option (c), as registered by the continuations tooling (COORD-RULING-520 D3). **One continuation overflow rule**, the coordinator's standalone ruling, covers GO-1 and Stage 2; this plan cites it and maps it onto every Stage-2 statistic. The signal is the per-event `epa_overflow.jsonl` | 3 |
| crash | CRASHED needs both counting attempts **attested** (an overflow with the same unit and attempt id before a native exit). **Ceiling:** a 2nd attested crash at one point, or a 3rd overall, stops for a re-rule. An unattested crash falls under RULING item 5 as registered. Feasible-state bounds; CRASH-AFFECTED income | 3.4–3.5 |
| C3 pins (S2-R1: pre-data code governs) | (1) K2's pooled VOID reaches share calls at N points only. (2) Verdict 5 tolerates one uncorroborated other-fauna EARNS; **it is the hinge of the final headline**, and the headline line is marked **V5-TOLERANCE-SENSITIVE** when the literal reading differs. (3) §12 item 2 is scored on body calls (the r1 pin is rejected). (4) The share model uses every completed M seed. (5) MARGINAL uses the uncensored births 180–238 (DATA-INFORMED): MARGINAL on EARNS calls goes from 8/8 to **2/8**, and **§9.1 gives D-sign `c0-p080-HP-G`, H-sign none** (the counterfactual gives none) | 4 |
| optional stopping | separate locks `GO-ID-2A:`, `GO-ID-INTERIM:` and `GO-ID-FINAL:`. The interim prints no §8 and no call | 5.1, 11 |
| script | `stage2_readout.py` (skeleton), `s91_rule_chosen.py` → `s91_rule_chosen.txt`, and `tests/test_rbt129_stage2_plan.py` (42 tests) | 11 |
| open | 30 O-items with dispositions, and the N-items | 12 |

## 1. What Stage 2 is (DESIGN §4.1, §4.2, §7.1, §11.1 item 4)

- **2a.** At most 16 new points by R-A, at n = 8, with all layers.
- **2b.** At most 20 points to n = 16 by R-B (seeds 9–16, screened; F5, T8).
- **Order (M12).** 2a and 2b for Stage-1 points run side by side. 2b for Stage-2a points follows 2a, from what remains
  of the cap of 20.
- **The final map.** BH once over all points, with R-B's combined p-values (§7.1), then the §8 verdicts.
- **Nothing is added.** "No other point, seed or arm may be added after Stage 1 is seen, except by a new registration"
  (§4.2), and this plan adds none.

### 1.1 The 12 Stage-2a points (`stage1_readout.txt` L428–L441, as printed)

| rank | point | why (L429–L440) | layer | census g0 | designed FF | M / N (§2.3) |
|---|---|---|---|---|---|---|
| 1 | `c05-p080-U-G` | R-A (a)+(b), \|Δt\| 15.537 | income | 1.125 | no | — |
| 2 | `c1-p053-U-G` | R-A (a); also C1 | income | 0.996 | no | **M** |
| 3 | `c05-p030-U-G` | C1 | income | 1.332 | no | — |
| 4 | `c0-p018-HP-G` | C1 | income | 2.164 | no | — |
| 5 | `c15-p030-U-G` | R-A (a); also C1 | income | 1.015 | no | — |
| 6 | `c15-p010-U-G` | R-A (a) | income | 1.139 | no | — |
| 7 | `c1-p018-U-G` | C1 | income | 1.070 | no | — |
| 8 | `c2-p053-HP-G` | C1 | income | 1.120 | no | — |
| 9 | `c1-p053-U-L` | R-A (a) | income | 0.963 | no | **M** |
| 10 | `c1-p018-HP-L` | R-A (a) | income | 1.221 | no | — |
| 11 | `c1-p018-U-L` | R-A (a), \|Δt\| 0.039 (noise; corrections A6) | income | 1.174 | no | — |
| 12 | `c1-p018-PW-L` | R-A (b); also C1 | income | 0.551 | no | **M + N** |

- The holistic fauna is census FOUNDING-FAIL at all 150 points (unscreened, T3).
- `check_inputs` verifies the record's sha256 (`beb515aa…`) and re-parses both lists. `refusal()` runs it at every step.

### 1.2 R-B: GO-1 and the Stage-2a remainder

- **GO-1** (`RBT129-RB-GO-1`).
  - **Points.** The 9 points of L443–L451.
  - **Arms.** S on seeds 129009–129016 at 140 / 262 core-h, and M at `c2-p030-U-G` only (the tooling's gate; no N).
  - **Who does what.** The continuations tooling session tools and launches it. **This plan launches none of it.**
  - **How it enters the final map.** Under the **same** continuation overflow rule (S2-R2, O-3) and the unit-state
    mapping of §3.
  - `c2-p030-U-G`'s M stays CRASHED at 129001, so it reads at most 15 of 16 (RULING item 2).
- **The combination.**
  - At each extended point, Z = (Z₁ + Z₂)/√2 over seeds 1–8 and 9–16 (Lehmacher & Wassmer; R4 (iii)). Each half's
    signed z comes from its one-sided t p-value, computed symmetrically from the smaller tail (`_z_upper`, finding 12).
  - The TOST is combined per side, and EARNS-TIE needs both sides.
  - The |x̄| ≥ 0.10 bar is read on the pooled 16-seed mean.
  - `combined_p` reproduces `stage1_readout.stage2_income_call`'s decisions; a test pins them together.
- **The Stage-2a remainder.**
  - **Eligibility** is R4 as ruled: UNDECIDED or CONTINGENT; or NOT RUN with an income UNDECIDED. Anchors are never
    eligible.
  - **Ranking** is by CP, capped at 20 − 9 = 11.
  - **Whether it runs at all** is fixed by the owner **before any 2a data exist** (S2-R3; N-5):
    - `2B2A: COMMITTED` means "extend whatever R4 lists, ≤ 11 points, ≤ 221 / 414 core-h";
    - `2B2A: DECLINED` means the Stage-2a points stay at n = 8 in the final map, by rule.

## 2. What runs

### 2.1 Stage 2a, the S arm

- **Points and seeds.** 12 points × seeds 129001–129008 at the salts of `lanes/1/launch.txt`: 129002 (1, 0),
  129003 (2, 0), 129007 (1, 0), 129008 (1, 0), and (0, 0) otherwise.
- **The chain.** S60 → ckpt60 → S, seasons 0–299. The world block comes from `blocks.py`, under
  `--fair --eat-from root --eat-rule surface`.
- **129001 (O-2; S2-R4: REQUIRED, pending the owner's cost OK of ~5–9 core-h).** Its S 0–59 is **re-simulated on the
  build** at the 12 midpoints, then byte-compared with the census run at the same point (`K1_SKIP`-style: logs,
  `platform.json` and the EPA log excluded).
  - **Equal:** the census S60 is adopted, as T10 does at Stage 1. The unit is now scanned, and it doubles as CT-2
    identity evidence.
  - **Not equal:** HELP.
  - **Labelled** an extension of the Stage-1-scoped T10 rule to Stage 2 (finding 10).
  - **If the owner declines the cost:** the census S60 is adopted unscanned (labelled UNSCANNED, §3.6), and the budget
    falls by 4.7 / 8.7.
- **K-SALT (F7)** at 129002 and 129003: 24 point-seeds against the census references. **A mismatch in a unit whose log
  holds an overflow is a HELP, not a VOID** (N-3; `ksalt_outcome`). The PASS count is printed as identity evidence beside
  CT-2 (finding 11).
- **The build.** Every Stage-2 simulation job runs on the registered option-(c) build (§3.1).

### 2.2 What is measured

- **On S:** exactly Stage 1's measures (READOUT-PLAN §3). Per-birth income for MARGINAL is amended (§4.5).
- **On M and N:** y′, the one-world column, interference, g0 and the VARIANCE-DRIVEN inputs.

### 2.3 Stage 2a, the M/N gate (DESIGN §5.2, T5 and the #500 ruling, unchanged; `mn_gate`)

- **M** (≤ 4): **`c1-p018-PW-L` (0.551), `c1-p053-U-L` (0.963), `c1-p053-U-G` (0.996)**. The other 9 points have census
  g0 > 1.0.
- **N** (≤ 2): **`c1-p018-PW-L`** only. The null is holistic on odd seeds and designed on even seeds.
- **Seeds.** Valid at the merge only. A point with no valid seed frees its slot (T5); no other point is eligible. The
  valid counts are seen at emission, as the gate's registered input.

### 2.4 Stage 2b for Stage-2a points (only if `2B2A: COMMITTED`)

- **Size.** ≤ 11 points from the interim's R4 list, seeds 129009–129016 at the screened salts (129010 and 129016 at
  (1, 0)). All S60s are fresh.
- **M/N** within DESIGN's R-B caps (M ≤ 6, N ≤ 2), shared with GO-1, with Stage-1 points first.
- **K-SALT does not apply at seeds 9–16.** F7 reads "wherever … the census also ran", which settles O-4 from the text
  (finding 16).

### 2.5 Budget (`budget()`; 23.35 / 43.72 core-s per arm-season, T11)

| block | arm-seasons | core-h low / high |
|---|---|---|
| 2a S: 12 × 8 × 300 (129001 re-simulated, O-2) | 28,800 | 186.8 / 349.8 |
| 2a M: ≤ 3 × 8 × 240 | ≤ 5,760 | ≤ 37.4 / 70.0 |
| 2a N: ≤ 1 × 8 × 240 | ≤ 1,920 | ≤ 12.5 / 23.3 |
| **2a total** | | **≤ 236.6 / 443.0** |
| 2b(2a) S: ≤ 11 × 8 × 300 | ≤ 26,400 | ≤ 171.2 / 320.6 |
| 2b(2a) M: ≤ 3 × 8 × 240; N: ≤ 1 × 8 × 240 | ≤ 7,680 | ≤ 49.9 / 93.3 |
| **2b(2a) total (only if COMMITTED)** | | **≤ 221.0 / 413.9** |
| **this plan, total** | | **≤ 457.7 / 856.9** |
| without O-2's re-simulation | | 2a ≤ 231.9 / 434.3; total ≤ 453.0 / 848.2 |

**Not included:** CT-2's identity runs (≈ 3.5 / 6.6), the owner's Stage-1 M/N scan (58 / 108, the tooling's
lanes), and GO-1 (S 140 / 262; M at `c2-p030-U-G` 12.5 / 23.3).

### 2.6 What does not run, and why

- **The probe leg, the planted set and the R8 levers.** Perception is UNREADABLE at a = 6 (`calibration-final/DECISION.md`;
  §12's S-2, binding). So:
  - every perception call reads **NOT MEASURED**;
  - **T4 is NOT MEASURED** and enters Holm at p = 1, permanently (§5.5);
  - **LEVER is not evaluated.** Every EARNS and WIN call is counted with that caveat (O-13);
  - the perception verdicts read PERCEPTION NOT MEASURED.
- **Retention** (Stage-1 G points only), **the sub-studies** (their own registrations) and **the anchors** (never
  re-run; R4 (ii)) are outside Stage 2.

### 2.7 Gates before any Stage-2 launch

1. This plan merged, after the fix-check and the coordinator's ruling.
2. The continuation build registered, with `BUILD-SHA256:` ruled (64 hex digits).
3. The continuation overflow rule ruled, with `OVERFLOW-RULE:` set.
4. The continuations tooling carries:
   - the unit and attempt fields (§3.2; agreed);
   - CT-2, including the forced-overflow replay at the launch WORKERS;
   - the Stage-2a lanes, after its own adversary pass.
5. `2B2A: COMMITTED | DECLINED` registered by the owner. Only then may `GO-ID-2A:` open (the 2a go; O-1).
6. The O-2 cost OK, or its decline, recorded.
7. The drivers and the end-to-end synthetic test committed and fix-checked (§11).

## 3. The continuation build and how overflows enter every Stage-2 statistic (S2-R2)

**The rule is not redefined here.** One continuation overflow rule, the coordinator's standalone ruling built from the
tooling draft (`continuations/OVERFLOW-RULE-DRAFT.md`) and this plan, governs GO-1 and Stage 2 alike (O-3). This
section cites it and states what the Stage-2 readout does with it.

### 3.1 The build (COORD-RULING-520 D3)

- **What it is.** Option (c), the guard-off log-only build, registered by the continuations tooling:
  - `scripts/build_mujoco_instrumented.sh` (blob `1b6cf31`) and `continuations/build/mujoco-3.14.0-rbt129-epa-log.patch`
    (blob `ccde8f9`), on branch `claude/rbt129-continuations-tooling`;
  - a fixed WORKDIR `/opt/rbt129-mjbuild`;
  - the build marker `rbt129-epa-instr/2` and its sha256 `1d138916…94aa0`, as the tooling reported it at 13:11Z (the
    earlier `7ae75f7f…` belonged to marker /1). The registered value is whatever the coordinator enters as
    `BUILD-SHA256:`.

  These are cited by blob, not by PR head (finding 18). #520's `b90290b` patch is not used.
- **FC-2.** The build is byte-identical to stock on trajectories without an overflow. At and after an overflow, nothing
  is claimed, and **the overflow record is the signal**.
- **FC-3.** Launches and emitters refuse unless the mapped library's sha256 and build marker match. Events are read only
  from the run's own `epa_overflow.jsonl`, never from `run.log`.
- **The lock.** `BUILD-SHA256:` in `RULINGS-CITED-S2.md` must equal the registered sha, and every attempt's
  `start` line must carry it (`unit_state`).

### 3.2 The record the readout reads (`parse_epa_log`; S2-R2, finding 2; fields agreed with the tooling, 13:11Z)

- **The log.** `<run dir>/epa_overflow.jsonl`. One JSON object per line, each a single O_APPEND `write(2)`. It is never
  read from `run.log` (FC-3).
- **`start` line** at every process start: `unit` (the run's checkpoint label), `attempt` (0-based: how many start lines
  the log already held, i.e. the resume count), `pid`, `argv`, `build` and `libmujoco_sha256`.
- **`season` line** as each season begins.
- **`event` line** (`near` ≥ 17, `overflow` > 24), written **by libmujoco before EPA reads the overflowed arrays**, so a
  fault that follows leaves it. It carries `unit`, `attempt`, `pid` and `seq`.
- **Attested** (S2-R2, as the tooling's `epa_ecology.attested(path, unit, attempt)` implements it): the log holds an
  overflow line with **this unit and this attempt id**. It precedes that attempt's abnormal exit by construction.
- **The crash count** (two consecutive native exits, one at WORKERS = 1; RULING item 5) comes from the runner's own
  record. Each of the two counted attempts must then be attested in the log (`crash_attested`).
- **No destructor stats file is used** (finding 1). The worker histograms enter no check.
- **The tooling verified a forced overflow at WORKERS = 2** (`continuations/records/forced-overflow.txt`): every worker
  logged `nedges 25` with unit, attempt, pid and seq, then faulted, and attempts 0 and 1 were tagged correctly. CT-2
  repeats this on the registered build (O-6).
- **Kept data** follow the tooling's `read_log`: a season counts from its last attempt.

### 3.3 Unit states (`unit_state`, `propagate_s60`)

| state | when | how it enters |
|---|---|---|
| **CLEAN** | a log covering every season run; no overflow in the kept data | as any unit |
| **OVERFLOWED** | an overflow in the kept data (FC-2: whatever the run did afterwards). **An overflow in S's S60 phase makes S, M and N of that seed OVERFLOWED** | the "flagged" state, §3.4 |
| **UNLOGGED** | a season run with no season line | treated as OVERFLOWED |
| **CRASHED** | RULING item 5's counting rule (the runner's record: two consecutive native exits, one at WORKERS = 1), **with both counted attempts attested** in the log (an overflow line with that unit and attempt id) | §3.4–3.5 |
| HELP | an **unattested** crash (RULING item 5 as registered); a missing log or start line; a start or event line of another unit; an event with no matching start; a sha that is not the registered one | nothing further until the coordinator rules |
| **UNSCANNED** | a Stage-1 unit no scan covered | read as it stands (§3.6) |

A test pins the case "an earlier attempt overflowed and survived; the later crashes have no overflow": it is a HELP, not
CRASHED.

### 3.4 How flagged and crashed units enter every statistic (S2-R2; O-8)

- **Primary: include-flagged.** OVERFLOWED and UNLOGGED units are kept as observed.
- **The sensitivity: `exclude-known-flagged`.**
  - Flagged units are removed as a ruled K-SALT VOID is (O-7).
  - **The whole final map is recomputed** under it.
  - Every call, family decision, map statistic and verdict that differs is marked **OVERFLOW-SENSITIVE**. On the
    headline, the mark sits **on the headline line itself** (O-26).
  - It removes only *known* flags. UNSCANNED Stage-1 units are unchecked, and the report says so.
- **Why include is primary.**
  1. Stage-1 units ran on stock physics and are mostly unscanned. Including flagged units keeps one rule across the map.
  2. Overflow risk depends on bodies and worlds, so excluding is informative missingness.

  r1's third reason ("a flagged unit is what the registered pin produces") is **deleted**. After an overflow both builds
  are undefined, and the instrumented one need not match stock (finding 8; FC-2).

| statistic | OVERFLOWED / UNLOGGED (primary) | CRASHED |
|---|---|---|
| S validity and survival (EXCLUDED, PARTIAL, NEITHER) | included | removed from n. The call is bounded over **feasible** completions only (`crash_bounded_body`: a fauna dead at 59 stays extinct; a crash before 59 enumerates the merge states). It is marked CRASH-SENSITIVE, or **"primary call infeasible given ckpt60"** when the primary call is not feasible |
| income x_j, EARNS/TIE, R-B CP, M2 sensitivity fit, M3, M7, cross-correlation | included | removed; the point's income call is **CRASH-AFFECTED** (no logical bound). The §8 line carries CRASH-AFFECTED if such a point is in a counting set of ≤ 2 calls the verdict uses |
| per-birth income, MARGINAL, regime | included | removed |
| M: y′, one-world column, interference, g0 and RESOLVING, VARIANCE-DRIVEN | included | removed. `M k of n (j CRASHED)`, with the bound under arbitrary missingness for y′ |
| N: K2 (per point, pooled), the pooled null, CONTINGENT | included | removed; counts over completed runs |
| §8, M1, M4, scorecard | from the calls above | a unit state, never an M1 or M4 category |

### 3.5 Crashes: the ceiling and the amendments drafted for the coordinator

- **Attested crash** (`crash_attested`). A CRASHED unit, in any arm, is a unit state. **It does not stop the hive or M/N
  issuance**, because its mechanism is known. Two rules sit on top of that:
  - **the ceiling** (`crash_ceiling`; O-23): a **second attested CRASHED unit at the same point**, or a **third across
    Stage 2 and GO-1**, stops launches for a re-rule;
  - **the counting rule**: RULING item 5's "the same instruction" is read as "inside libmujoco, in the convex collider",
    with attestation by the log, because the fault site moves (#520 (b)).
- **Unattested crash.** RULING item 5 as registered. M/N issuance stops; an S crash stops the hive.
- **Item 2 stands.** There is no re-run, substitute seed or resume of any CRASHED unit.
- **Item 3, quarantine.** It applies to each new CRASHED unit's partial branch. The script holds the list (`QUARANTINED`
  and ruled `QUARANTINE:` lines). Its readers refuse the labels by case-insensitive substring.
- **A-11** (N-2; for the coordinator's ruling).
  - For **new** continuation units only, these are superseded by OWNER-DECISIONS-2026-10-03 item 2:
    - RULING item 7's "its fix applies to later registrations only, never to RBT-129";
    - item 2's "not on another MuJoCo build or a patched build", as it bears on continuations.
  - Item 2 still bars any re-run of a CRASHED unit, on any build.

### 3.6 Stage-1 units in the final map

- **What is UNSCANNED.** Stage-1 S, M and N units, and the census S60s if O-2 is declined. The exception is units the
  owner's M/N scan covers (the tooling's `lanes/SCAN`, 37 units). A scanned unit with an overflow becomes OVERFLOWED;
  without one, CLEAN.
- **The scan record** carries the count only, plus the scan's output-hash comparison. The season of the first overflow
  is dropped (O-7; finding 19: a how-far proxy).
- **The disclosure** (COORD-RULING-520 D2; A7). "A known memory-safety bug (EPA horizon overflow) can corrupt without
  crashing; the UNSCANNED units were not checked", with counts by arm.

## 4. The five C3 items (S2-R1: wherever plan text and pre-data code disagree, the pre-data code governs)

**All five are DATA-INFORMED in origin:** the run adversary raised each after reading Stage-1 outputs. Under S2-R1 the
author's choice is removed: four follow the pre-data code, and one (C3-5) is a measurement fix. **The other reading is
printed every time, labelled non-registered.**

| pin | the pre-data code | r2 | stake at Stage 1 |
|---|---|---|---|
| C3-1 | pooled VOID at N points only (`call_points`) | **the code** | none |
| C3-2 | verdict 5 tolerates one uncorroborated other EARNS (`verdicts`) | **the code**, marked when it matters | none at Stage 1; **the hinge of the final headline** (§4.2) |
| C3-3 | §12 item 2 on body calls: NOT SHOWN (15 of 36) | **the code** (r1's pin rejected) | descriptive |
| C3-4 | share fit on every completed M seed (p 0.9145) | **the code** | none; no call reads it |
| C3-5 | censored 240–299 per-birth | **amended** (a defect) | MARGINAL 8/8 → 2/8 of EARNS calls; §9.1 gets one D-sign point |

### 4.1 C3-1: the scope of K2's pooled VOID

- **The pin** (`share_void`). The pooled VOID makes VOID the **share call** at every point where N ran in a stage whose
  pooled K2 failed. A 16-seed point is VOID if either half's stage failed.
- **What it never touches:** points without N, income calls, survival calls, and habitability, except through §6.1
  item 3.
- **Stage 1's pooled FAIL (L311) stands.**
- **O-9 (S2-R4).** The conjunction is kept: |mean| < 0.05 **and** the t test not rejected.
- **O-10 (S2-R4).** FAIL at < 2 runs in a stage is kept.
- **Disclosed (finding 15).** At 2a, N runs only at `c1-p018-PW-L`. With Stage 1's null spread (sd ≈ 0.29), P(pass |
  centred null) is about 0.19 at 2 runs and 0.37 at 8. At < 2 runs it is FAIL by rule. A pooled FAIL can VOID that
  point's **body call** through §6.1 item 3 if items 1–2 do not settle it, which removes it from habitability, the M3
  rows and verdict 3's denominator. **O-10 is therefore not purely conservative.**

### 4.2 C3-2: verdict 5, and why it is the hinge

- **The registered reading** is the pre-data code. One uncorroborated other-fauna EARNS call does **not** fail verdict 5.
  Two calls, or one corroborated by M3, do. **Any EARNS-TIE fails it** (R2), and any other-fauna share WIN fails it.
- **Disclosure (MAJOR 6; S2-R1).** T1 is frozen at "rejects" (§5.5), so the final headline turns on counting sets. The H
  side of the Stage-1 headline is 2 EARNS-H, both non-habitable and neither R-B-eligible: `c1-p010-PW-L` (p 0.0266) and
  `c1-p080-HP-L` (p 0.0335, which passed BH by 0.0013). The final BH's K grows from 23 to as many as 35. The adversary's
  probe (`stage2-plan-adversary/probe/c3_2_hinge.txt`, the committed `verdicts` on the 36 Stage-1 calls):

  | scenario | registered | literal (non-registered) |
  |---|---|---|
  | as printed (2 EARNS-H) | EARNINGS DEPEND | — |
  | **exactly one EARNS-H survives, uncorroborated** | **DEPENDS ONLY THROUGH HABITABILITY (D)** | **NOT RESOLVED** |
  | both EARNS-H drop | DEPENDS ONLY THROUGH HABITABILITY (D) | the same |
  | one EARNS-H plus any EARNS-TIE | NOT RESOLVED | NOT RESOLVED |

  **This pin is the hinge of the likeliest change to the final headline.**
- **A second hinge (O-18).** Corroboration comes from the final-map M3. `c1-p018-HP-L` gives row (1, HP, L) a third price
  level. A bounded p* in [0.01, 0.08] there would corroborate a lone `c1-p080-HP-L` EARNS-H and keep EARNINGS DEPEND.
- **What is printed** (`v5_mark`, `verdicts_literal`). The literal reading is printed every time. Wherever the two
  headlines differ, **the headline line itself carries V5-TOLERANCE-SENSITIVE**. A test reproduces the scenario row
  above.

### 4.3 C3-3: §12 scorecard item 2 (r1's pin REJECTED)

- **Scored as the pre-data code scored it** (`scorecard_item2`). Body calls in {NOT RUN, SATURATED, RBT-118 (not
  available)} count. It is AS PREDICTED when that count is more than half and RESOLVING ≤ 2. At Stage 1 this reads
  **NOT SHOWN (15 of 36; RESOLVING 0)**; a test pins it to L617.
- **Two lines printed beside it, non-registered:**
  - "gated out at x of y (by design; §5.2: not evidence)";
  - "share layer at the N points: not RESOLVING at k of m". At Stage 1 this reads 4 of 4. It is the falsifiable part of
    the prediction.

### 4.4 C3-4: the share model's scope

- **The registered share fit** follows the pre-data code. It uses every point on the Stage-1 grid with an M arm, with
  every completed M seed (`share_model_points(scope="all")`).
- **The habitable-only fit** is printed as non-registered.
- **No stakes either way.** No call or verdict reads it. On the final map the habitable-only fit is NOT TESTABLE by
  construction, because only `c2-p030-U-G` is habitable among the Stage-1 M points (finding 17).

### 4.5 C3-5: the uncensored per-birth measure, and DESIGN §9.1 (DATA-INFORMED)

- **The amendment** (`per_birth_uncensored`). MARGINAL's per-birth income comes from `regime.py`'s window of births
  **180–238**, and it **replaces** the censored 240–299 measure at every point of the final map.
  - **The value.** `net_per_birth` + 0.25 (O-5), the mean over the point's income-valid seeds that have one.
  - **The bar.** MARGINAL when either fauna's value is **strictly** below 0.25, at full precision (finding 4).
  - **Printed beside:** the censored figure.
- **Why 238, not 239 (r2 correction, found by computation before any Stage-2 data).**
  - `regime.py:175` counts a life complete only when its last row precedes the run's last season.
  - A life born at 239 is evaluated in 240–299 and dies aged *in* 299, so regime.py counts it censored. The first run of
    `s91_rule_chosen.py` met exactly that case and stopped.
  - Births up to 238 end by 298. The S2-R1 ruling's "180–239" is read as this one-season correction. It is flagged for
    the coordinator.
- **Its Stage-1 effect** (`s91_rule_chosen.txt`, full precision, income-valid seeds):

  | EARNS call | habitable | censored 240–299 | births 180–238 (H / D) |
  |---|---|---|---|
  | `c0-p010-U-G` EARNS-D | yes | MARGINAL | not (0.643 / 1.194) |
  | `c0-p030-U-G` EARNS-D | yes | MARGINAL | not (0.430 / 0.979) |
  | `c0-p030-HP-G` EARNS-D | yes | MARGINAL | not (0.406 / 1.151) |
  | `c0-p080-U-G` EARNS-D | yes | MARGINAL | not (0.428 / 0.496) |
  | `c0-p080-HP-G` EARNS-D | yes | MARGINAL | not (0.469 / **0.2573**; the 2-decimal edge resolves to not) |
  | `c1-p030-HP-G` EARNS-D | no | MARGINAL | not (0.398 / 0.363) |
  | `c1-p010-PW-L` EARNS-H | no | MARGINAL | **MARGINAL** (0.071 / −0.042) |
  | `c1-p080-HP-L` EARNS-H | no | MARGINAL | **MARGINAL** (0.276 / −0.440) |

  - MARGINAL on EARNS calls goes from **8 of 8 to 2 of 8**. All 6 EARNS-D clear, and both EARNS-H stay.
  - The effect is fauna-asymmetric, and this plan states it.
  - MARGINAL changes no call and no verdict.
- **DESIGN §9.1, ruled by DESIGN's rule (S2-R1; MAJOR 4; O-12).** r1's statement that §9.1's points "were chosen after
  Stage 1" was false, and is withdrawn: nothing had computed them.
  - **The rule.** The habitable, non-LEVER, non-MARGINAL Stage-1 point with the largest BH-significant |x̄| for each sign.
  - **The computation.** `s91_rule_chosen.py`, committed with its output **before any Stage-2 data**. It uses the Stage-1
    calls and BH as accepted, the amended MARGINAL, and **LEVER not evaluated**, so no point is excluded on LEVER and the
    choice carries that caveat.
  - **Result: D-sign `c0-p080-HP-G` (x̄ −1.653); H-sign none** (both EARNS-H are non-habitable).
  - **The counterfactual on the censored measure: none of either sign.**
  - This creates a replication target for RBT-118 that the censored measure would not. RBT-118's registration takes it
    with this disclosure, and whether it accepts it is RBT-118's and the owner's decision (O-12).

## 5. The interim readout and the final map

### 5.1 The interim (S2-R3; MAJOR 7)

- **When.** After 2a completes, under `GO-ID-INTERIM:`.
- **What it prints, and nothing else:**
  - 2a integrity (§7);
  - the 2a gate re-check;
  - operational status (units done, CRASHED, OVERFLOWED and UNLOGGED counts by arm);
  - **the mechanical R4 list** for 2b(2a), with CP and core-h. It is printed only if `2B2A: COMMITTED`; with DECLINED it
    prints "declined".
- **What it computes but never prints.** The 2a calls, which R4's eligibility needs. They are computed under BH over
  Stage-1 ∪ 2a at n = 8 (O-15), and are **not printed to anyone**.
- **What it never prints:** no §8 line and no provisional call, for Stage-1 or 2a points.
- **The final step** needs `GO-ID-FINAL:`. That lock opens only after 2b(2a) has completed, or after
  `2B2A: DECLINED`.

### 5.2 The final income families (`point_income_test`, `final_income_calls`)

- **Points.** Every point with ≥ 2 income-valid half-1 seeds.
- **The test at each point:**
  - not extended: the n = 8 t and TOST;
  - extended with ≥ 2 income-valid seeds in each half: the combination;
  - extended with < 2 in half 2: the half-1 test, flagged "half 2 short" (O-16).
- **BH** runs once per family at q = 0.10.
- **The cross-point correlation** is printed. If its mean exceeds 0.3, BY is printed beside BH.
- **Body calls at n = 16** use ⌈5n/8⌉ = 10 and ⌈3n/4⌉ = 12, less VOID and CRASHED seeds.

### 5.3 Share families

- **Membership.** As at Stage 1 (ruling item 4(a), O-22). At extended N points the y′ test is combined the same way.
- **CONTINGENT is never callable on the final map** (finding 15). The holistic-null df is 2 (Stage 1), plus at most 3
  (2a) and at most 3 (2b(2a)), which is less than 12, unless RBT-118's anchor nulls arrive.
- **RESOLVING** is evaluated only where M and N both ran, at both g0 bounds, with the replica scaled by the pilot.
- **VARIANCE-DRIVEN** is wired for every share WIN. **LEVER** is not evaluated.

### 5.4 Map statistics

- **M1.** Over every point, Stage-2a points in their own block. The anchor is counted under NOT RUN (A2).
- **M2 income, registered.** The Stage-1 grid, seeds 1–8, Stage-1 habitability. Its values are final at Stage 1
  (L402–L412; **#512 adversary NOTE 10**, finding 20; O-19).
  - **Sensitivity fit.** It adds the Stage-2a points and the R-B extensions, with the MUE at extended points
    (`median_unbiased`, the root of the combined Z(μ); O-14).
- **M2 share.** As §4.4.
- **M3.** Every (c, L, s) row with ≥ 2 price levels among its habitable non-VOID points, Stage-2a points included. It is
  the M3 that corroborates in §8 ("from the final map"; O-18, the second hinge, §4.2). The Stage-1-only M3 is printed
  beside it.
- **M4** (S2-R4: the quarter rule, stated; O-17).
  - **The weights.** Equal weights over the 27 G and the 9 L Stage-1 points. A midpoint takes **one quarter of each
    parent's current weight**, midpoints in id order, then the weights are normalised per smell block.
  - **Its stated departures from an axis-Voronoi split:**
    - a parent split on both sides (e.g. `c1-p030-U-G`) keeps 0.5625 of its weight, not 0.5;
    - edge points are treated as interior ones;
    - the result depends on the fixed id order.
  - It is descriptive.
- **M5:** NOT MEASURED.
- **M6:** κ over decided share calls.
- **M7:** sign changes along every row of the final map.

### 5.5 T1–T4 and Holm

- **T1–T3** are the registered Stage-1 fit's values (L410–L412): T1 χ² 69.704, p 1.18e-13; T2 z +4.43; T3 z −0.79.
- **T4** is NOT MEASURED (p = 1).
- **The final Holm is therefore Stage 1's:** T1 and T2 rejected, T3 not. It is not re-run.

### 5.6 The §8 verdicts on the final map

- **The logic.** `stage1_readout.verdicts`, unchanged (R1, R2, R3, C3-2), over the final calls, with corroboration from
  §5.4's M3.
- **What the headline line carries**, as each applies:
  - **V5-TOLERANCE-SENSITIVE** (§4.2);
  - **OVERFLOW-SENSITIVE** (§3.4);
  - **CRASH-AFFECTED** (§3.4).
- **What is printed beneath it:**
  - the verdicts that also hold;
  - the two Stage-1 non-registered lines;
  - the literal verdict-5 reading;
  - the exclude-known-flagged map's verdict.
- **Perception:** PERCEPTION NOT MEASURED.
- **The label.** Every line carries the claim label and "earns, not persists".

### 5.7 The scorecard

Stage 1's `scorecard` is used, with item 2 as §4.3, and items 4 and 6 NOT MEASURED. It is printed for the final map and
for the Stage-1 points.

## 6. Stage-1 rules: kept, and the amendments

**Kept unchanged** (by importing the committed `stage1_readout.py`, blob `7b75cbc5f3dc35c85869a27780713b870ba9c1d1`):
- READOUT-PLAN §3–§9, every threshold, margin, family and procedure;
- R1–R5 and O-1 to O-23;
- the crash ruling's items 1, 3 and 4;
- T4–T8 and T10.

| id | what | reason | label |
|---|---|---|---|
| A-1 | MARGINAL's per-birth measure: births 180–238 (§4.5) | the Stage-1 measure is censored by construction | DATA-INFORMED; Stage-1 effect disclosed |
| A-2 | §9.1 computed by DESIGN's rule with A-1 (§4.5) | S2-R1 | DATA-INFORMED; counterfactual disclosed |
| A-3 | **withdrawn** (r1's C3-3 pin; S2-R1) | — | — |
| A-4 | the C3-2 hinge disclosure and the V5-TOLERANCE-SENSITIVE mark | S2-R1, MAJOR 6 | outcome-blind as a mark |
| A-5 | the K2 pooled scope (code); O-9 and O-10 kept and disclosed | S2-R1, S2-R4 | DATA-INFORMED in origin |
| A-6 | unit states, the include rule and the exclude-known-flagged sensitivity (§3) | S2-R2; the continuation rule | diagnosis-informed; outcome-blind to Stage 2 |
| A-7 | RULING item 5 for continuations: attestation, the ceiling, no stop for attested crashes (§3.5) | S2-R2 | proposed; for the standalone ruling |
| A-8 | interim content and the per-step locks (§5.1, §11) | S2-R3 | outcome-blind |
| A-9 | "half 2 short" and the MUE (§5.2, §5.4) | undefined in DESIGN | outcome-blind |
| A-10 | M4's quarter rule (§5.4) | undefined in DESIGN | outcome-blind; departures stated |
| A-11 | RULING items 2 and 7 for new continuation units (§3.5) | N-2 | drafted for the coordinator |
| A-12 | T10's census adoption at the 12 midpoints, only after a byte-equal re-simulation (§2.1) | O-2, finding 10 | REQUIRED, pending the owner's cost OK |

**Consequences, not amendments:** T4 NOT MEASURED, so Holm is final at Stage 1; LEVER not evaluated; perception NOT
MEASURED.

## 7. Integrity (each step's first output)

- **The READOUT-PLAN §2 checks**, over the continuation lane files: branches, markers, the resume audit, K-SALT
  (N-3), the gate re-check, the quarantine refusal (every listed label) and MuJoCo 3.14.0.
- **The build record**, for every attempt of every simulation unit:
  - the registered sha;
  - a log with a season line per season run;
  - CRASHED attested, or a HELP.
- **What is printed.** Counts only, by stage and arm: CLEAN, OVERFLOWED, UNLOGGED, CRASHED (attested), near-miss
  arm-seeds and the largest horizon (the draft's §5). No season and no unit, except OVERFLOWED and CRASHED units by name.
- **The final step** re-runs this over GO-1's units.
- **Any failure is a HELP**, and the integrity file is committed before any other output.

## 8. Descriptive only

Stage 1's descriptive list is kept. In addition:
- the non-registered lines of §4;
- the exclude-known-flagged map;
- the crash bounds;
- the Stage-1-only M3;
- the censored per-birth figure;
- the near-miss counts.

## 9. Reports

- **`READOUT-STAGE2A-INTERIM.md`:** §5.1's content only.
- **`READOUT-FINAL.md`:**
  - the final M1/M4 and the per-point table;
  - the families, with BH and BY;
  - M2, M3 and M7;
  - Holm;
  - §8 with its marks and its non-registered lines;
  - the scorecard;
  - the integrity disclosure;
  - every O-item as applied.

## 10. Order of operations

1. Fix-check of r2, then the coordinator's ruling, then merge.
2. The continuations tooling (CT-1 to CT-4, the unit and attempt fields), the continuation overflow rule, and the build
   sha registered.
3. The owner registers `2B2A:` and rules on O-2's cost. Only then is `GO-ID-2A:`.
4. 2a runs, beside GO-1.
5. `GO-ID-INTERIM:` → the interim (§5.1).
6. 2b(2a) runs, if COMMITTED.
7. `GO-ID-FINAL:` → integrity over every continuation unit, then the final map.

## 11. The script, the tests and the locks

- **`stage2_readout.py`** is a skeleton. It imports `stage1_readout.py`, and every Stage-2 rule in it is a tested pure
  function:
  - the inputs check and the gate;
  - the budget;
  - `parse_epa_log`, `unit_state`, `crash_attested`, `propagate_s60`, `crash_ceiling`, `ksalt_outcome`, `keep_seed`,
    `crash_bounded_body`, `crash_affected` and `verdict_crash_mark`;
  - the C3 functions, with `v5_mark`;
  - the combination and the MUE;
  - the final BH;
  - M4;
  - the locks, the quarantine list and `refusal`.
- **`s91_rule_chosen.py`** → **`s91_rule_chosen.txt`**: §9.1, committed. A test checks that its censored column equals
  the Stage-1 record's per-birth line at every EARNS point.
- **`tests/test_rbt129_stage2_plan.py`**: 42 tests. The full suite passes in a clean `.[dev]` venv without scipy (the
  PR states the count).
- **The locks** (`RULINGS-CITED-S2.md`, `refusal`).
  - A step runs only when all of these are ruled:
    - its own GO (`GO-ID-INTERIM:` or `GO-ID-FINAL:`);
    - `GO-ID-2A:`;
    - `2B2A: COMMITTED | DECLINED`;
    - `OVERFLOW-RULE: include-flagged | exclude-known-flagged`;
    - `BUILD-SHA256:` (64 hex digits).
  - A step also needs the inputs check to pass and no local ref naming a quarantined unit.
  - **Malformed lines are a HELP:** a duplicated or empty ruled line.
  - **The test does not go stale.** It asserts "pending, or ruled and well formed" (finding 13 (e)).
- **Before the first GO:**
  - the drivers and continuation readers are written, with an end-to-end synthetic-tree test. The tree has 2a, GO-1's
    halves, an OVERFLOWED unit, an S60-phase overflow, an UNLOGGED unit, an attested CRASHED M and S, and an unattested
    crash;
  - they are checked by the same adversary;
  - the readers reuse `sr.fetch_label`'s narrow refspecs and the guarded readers (finding 13 (f));
  - the lane labels of GO-1 and 2b(2a) are disjoint from each other and from Stage 1's (finding 13 (g)).
  - No rule may change in that round.

## 12. O-items: dispositions after the adversary and S2-R1 to S2-R4

| id | question | disposition |
|---|---|---|
| O-1 | does "plan it" authorise 2a? | no: `GO-ID-2A:` after `2B2A:` (owner) |
| O-2 | re-simulate 129001's S60 at the midpoints | **REQUIRED**, pending the owner's cost OK (A-12) |
| O-3 | one rule for GO-1 and Stage 2 | **yes**: the coordinator's standalone ruling, cited (§3) |
| O-4 | K-SALT at seeds 9–16 | does not apply (F7's text) |
| O-5 | 2a gate caps | 3 M, 1 N |
| O-6 | CT-2 scope | plus a forced-overflow replay at the launch WORKERS, the O-2 byte-compares and K-SALT as identity evidence |
| O-7 | scan record | count + output-hash; **no season** |
| O-8 | include vs exclude primary | **include-flagged**; sensitivity exclude-known-flagged; reason 3 deleted |
| O-9 | K2 pooled reading | conjunction kept; pass rate disclosed (§4.1) |
| O-10 | K2 pooled at < 2 runs | FAIL kept; disclosed that it can VOID a body call (§4.1) |
| O-11 | r1's C3-3 pin | **rejected** (S2-R1) |
| O-12 | MARGINAL replaced; §9.1 | replaced; **§9.1 computed and committed: D `c0-p080-HP-G`, H none**; counterfactual none (§4.5) |
| O-13 | lever-only leg | not here; a new registration (owner) |
| O-14 | MUE | the root of the combined Z(μ) |
| O-15 | interim BH set | Stage-1 ∪ 2a, **never printed** |
| O-16 | half 2 short | the half-1 test, flagged |
| O-17 | M4 | the quarter rule, stated with its departures |
| O-18 | M3 for corroboration | the final map; disclosed as a hinge |
| O-19 | registered M2 frozen | yes (DESIGN §7.3) |
| O-20 | K2 per point on the final map | adopted |
| O-21 | share combination | adopted |
| O-22 | crashed S seed | removed from n; feasible-state bound; CRASH-AFFECTED income |
| O-23 | attested S crash | not a stop, **with the ceiling** (2 at a point, 3 overall) |
| O-24 | no build record | HELP |
| O-25 | NOT MEASURED lines | printed for Stage 1 too |
| O-26 | sensitivity marks | on the headline line itself; no "robust" bar |
| O-27 | GO-1 fixed vs the interim BH | GO-1 fixed; the change is printed at the final only |
| O-28 | budget | upper bounds |
| O-29 | verdict-5 share veto | as coded |
| O-30 | the drivers after review | yes, carrying findings 1–3 and 12–13 |
| N-1 | per-step locks | done (§11) |
| N-2 | A-11 | drafted (§3.5) |
| N-3 | K-SALT with an overflow | HELP (§2.1) |
| N-4 | WORKERS | the per-event log makes WORKERS = 2 safe; CT-2 tests it (§3.2) |
| N-5 | 2b(2a) before 2a data | `2B2A:` (owner) |
| **O-31 (new)** | §4.5's 180–238 rather than the ruling's literal 180–239 | 238, because regime.py counts a 239 birth that ages out in 299 as censored; flagged for the coordinator |
| **O-32 (new)** | the attempt field names | **agreed with the tooling** (13:11Z): `unit` and a 0-based `attempt` on start and event lines; the crash count is the runner's item-5 record |

## 13. The fix round: where each finding is answered

| finding | answer | where |
|---|---|---|
| MAJOR 1 (WORKERS = 2 stats) | the destructor stats file is dropped; the per-event O_APPEND log is the record; CT-2 adds a forced-overflow replay at WORKERS = 2 | §3.2; `parse_epa_log` |
| MAJOR 2 (attestation) | the unit and attempt id on every start and event line (agreed with the tooling); both counted attempts attested; "earlier flagged, later unattested" is a HELP | §3.2–3.3; `crash_attested`; test |
| MAJOR 3 (S-crash gaps) | the ceiling; CRASH-AFFECTED income; feasible-state enumeration with "primary infeasible" | §3.4–3.5; `crash_ceiling`, `crash_affected`, `crash_bounded_body`; tests |
| MAJOR 4 (§9.1) | "were chosen" withdrawn; §9.1 computed at full precision and committed; counterfactual; strict bar | §4.5; `s91_rule_chosen.*` |
| MAJOR 5 (two principles) | S2-R1: the pre-data code governs; C3-3 rejected; C3-4 reverted | §4 |
| MAJOR 6 (hinge) | the table; V5-TOLERANCE-SENSITIVE on the headline; O-18 disclosed | §4.2; `v5_mark` |
| MAJOR 7 (optional stopping) | the owner decides 2b(2a) before 2a data; the interim prints no call or §8; separate locks | §1.2, §5.1, §11 |
| MINOR 8 | reason 3 deleted; exclude-known-flagged | §3.4 |
| MINOR 9 | A-11 | §3.5 |
| MINOR 10 | O-2 re-simulation, REQUIRED | §2.1 |
| MINOR 11 | K-SALT with an overflow is a HELP; K-SALT as identity evidence | §2.1; `ksalt_outcome` |
| MINOR 12 | symmetric z from the smaller tail; extreme tests in both signs | `_z_upper`; test |
| MINOR 13 | (a) sha validated; (b) duplicates and empties HELP; (c) quarantine list; (d) inputs in `refusal`; (e) non-stale test; (f), (g) carried to the drivers | §11; tests |
| MINOR 14 | quarter rule stated with its departures | §5.4 |
| MINOR 15 | K2 pass rates and CONTINGENT never callable, disclosed | §4.1, §5.3 |
| NOTE 16 | O-4 settled from F7's text; budget confirmed | §2.4, §2.5 |
| NOTE 17 | C3-4 NOT TESTABLE by construction on the final map, stated | §4.4 |
| NOTE 18 | the build cited by blob (now the tooling's) | §3.1 |
| NOTE 19 | the season dropped from the scan record | §3.6 |
| NOTE 20 | "#512 adversary NOTE 10" | §5.4 |
| NOTE 21 | tests extended to findings 1–3, 12 and 13 | §11 |
| NOTE 22 | noted: ≥ 1 overflow is more likely than not, which is why §3 is specific | §3 |

---
_Generated by [Claude Code](https://claude.ai/code)_
