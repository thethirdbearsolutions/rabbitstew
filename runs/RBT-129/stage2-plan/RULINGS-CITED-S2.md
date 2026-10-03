# RBT-129 Stage 2: rulings cited, and the locks the coordinator opens

`stage2_readout.py` reads only lines of this file that **begin** with a ruled tag. Every such tag below is registered as
`-PENDING:`, which the script never accepts. The coordinator opens a lock by renaming its tag, in a commit of its own,
with a citation beside it. **An empty or duplicated ruled line is a HELP** (`ruled_lines`).

## Rulings this plan cites (merged on `claude/new-session-4cao7d` unless noted)

- `stage1-readout/COORD-RULING-512.md`: R1–R5, kept (plan §6).
- `stage1-readout/COORD-RULING-517.md`: C1 (the Stage-1 record) and C3 (the five items pinned in plan §4).
- `stage1-readout/RULINGS-CITED.md`: the F7 de-duplication and O-23.
- `mn-crash/RULING.md` r3: items 1–7, kept except as A-7 and A-11 propose for continuations (plan §3.5, §6).
- `mn-crash/COORD-RULING-520.md` (#525): D1–D4. The build is option (c); FC-2 (the overflow record is the signal) and
  FC-3 (sha + marker identity; events from the dedicated per-run log only).
- `coordinator/OWNER-DECISIONS-2026-10-03.md`: items 1–4.
- `calibration-final/DECISION.md`: the perception layer is UNREADABLE at a = 6, so no probe leg runs.
- **The continuation overflow rule.** This is the coordinator's standalone ruling, built from the tooling draft
  (`continuations/OVERFLOW-RULE-DRAFT.md`, branch `claude/rbt129-continuations-tooling`) and this plan. It is cited and
  not redefined here (S2-R2). It is pending.

## The coordinator's rulings on the #523 fix round (COORDINATOR-EXPOSED; they bind this round)

They were relayed by `session_017eUHGNdTSsoVFAtLaJWehF` on 2026-10-03, on the adversary report #524 (head `f63122b`,
ADOPT WITH CHANGES: 7 MAJOR, 8 MINOR, 7 NOTE).

- **S2-R1: one principle for every C3 pin (MAJOR 5).** Wherever plan text and pre-data committed code disagree, the
  pre-data code governs.
  - **C3-1** adopted as proposed.
  - **C3-2** follows the code reading (one uncorroborated other-fauna EARNS is tolerated), with three conditions:
    - prominent disclosure that it is the hinge;
    - the literal reading printed every time;
    - the mark **V5-TOLERANCE-SENSITIVE** when the two differ (MAJOR 6).
  - **C3-3: the pin is REJECTED.** Item 2 is scored on body calls, as the code did. The gated-out count and the share
    status at the N points are printed as non-registered lines.
  - **C3-4** follows the pre-data code: every completed M seed. The habitable-only fit is non-registered. There are no
    stakes either way.
  - **C3-5** adopts the uncensored measure, DATA-INFORMED, with two conditions:
    - its Stage-1 effect is disclosed;
    - DESIGN §9.1 is ruled explicitly by DESIGN's rule. Its points are computed and committed before any Stage-2 data,
      with the counterfactual (MAJOR 4; O-12).
- **S2-R2: overflow and crash handling (MAJOR 1–3; O-3, O-6, O-8, O-23; N-2–N-4).**
  - **One continuation rule** covers GO-1 and Stage 2. It is the coordinator's standalone ruling, cited.
  - **The signal** is the registered build's per-event log, one O_APPEND write per event. It is not a destructor stats
    file. CT-2 adds a forced-overflow replay at the launch WORKERS.
  - **"Attested"** means an overflow record with the same unit and attempt id, logged before that attempt's abnormal
    exit. The fields are coordinated with the tooling session.
  - **The ceiling.** A second attested crash at one point, or a third overall (Stage 2 and GO-1), stops launches for a
    re-rule. An unattested crash is a crash under RULING item 5, as registered.
  - **`crash_bounded_body`** enumerates feasible completions only. Income at such a point is marked CRASH-AFFECTED.
  - **O-8.** Flagged units are included in the primary analysis. The sensitivity is "exclude-known-flagged". Reason 3 is
    deleted.
  - **N-2.** Amendment A-11 is drafted for the coordinator's ruling.
  - **N-3.** A K-SALT mismatch with an overflow is a HELP.
- **S2-R3: optional stopping (MAJOR 7; N-1, N-5).**
  - **Separate locks:** `GO-ID-2A:`, `GO-ID-INTERIM:` and `GO-ID-FINAL:`.
  - **The interim** prints no provisional §8 and no verdict-relevant call. It prints only operational and integrity
    status and the R4 list.
  - **2b(2a)** is committed or declined by the owner before any 2a data exist: `2B2A: COMMITTED | DECLINED`, set before
    `GO-ID-2A` can open.
- **S2-R4: the rest.**
  - O-9, O-10 and O-17: the adversary's dispositions. The quarter rule is kept and stated.
  - **O-2.** The 129001 S0–59 re-simulation at the 12 midpoints, on the build, with byte-equality adoption, is
    **REQUIRED**. It is pending the owner's cost OK (~5–9 core-h).
  - Every MINOR is fixed. The NOTEs are at the author's discretion, with each disposition stated.

## The locks

The 2b(2a) decision must be registered before the 2a GO opens:

2B2A-PENDING: COMMITTED or DECLINED (the owner's decision, before any 2a data exist)

GO-ID-2A-PENDING: RBT129-S2-2A-GO-1

GO-ID-INTERIM-PENDING: RBT129-S2-INTERIM-GO-1

GO-ID-FINAL-PENDING: RBT129-S2-FINAL-GO-1

The value is `include-flagged` (S2-R2's primary; the sensitivity is then `exclude-known-flagged`):

OVERFLOW-RULE-PENDING: include-flagged

The sha256 of the registered option-(c) `libmujoco.so.3.14.0`. It must be 64 hex digits. The tooling's current build is marker
`rbt129-epa-instr/2`, sha `1d138916…94aa0` (reported 13:11Z), which is not yet registered:

BUILD-SHA256-PENDING:

## Quarantined labels

`stage2_readout.QUARANTINED` holds the Stage-1 unit `rbt-129-stage1-c2-p030-U-G-129001-M`. The label of any new attested
CRASHED unit is added by ruling only, as a line that begins `QUARANTINE: <label>`. None is ruled.
