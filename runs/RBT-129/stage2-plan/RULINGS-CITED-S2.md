# RBT-129 Stage 2: rulings cited, and the locks the coordinator opens

`stage2_readout.py` reads only lines of this file that begin with a ruled tag. Each tag below is registered as
`-PENDING:`, which the script never accepts. The coordinator opens a lock by renaming the tag in a commit of its own,
with a citation beside it. A malformed or duplicated ruled line is a HELP.

## Rulings this plan cites (all merged on `claude/new-session-4cao7d`)

- `stage1-readout/COORD-RULING-512.md`: R1–R5 (kept, plan §6).
- `stage1-readout/COORD-RULING-517.md`: C1 (the Stage-1 record), C3 (the five items this plan pins, §4).
- `stage1-readout/RULINGS-CITED.md`: F7 de-duplication, O-23.
- `mn-crash/RULING.md` r3: items 1–7 (kept, except as plan §3.5 proposes for continuations).
- `coordinator/OWNER-DECISIONS-2026-10-03.md`: items 1–4 (build (c); R-B GO `RBT129-RB-GO-1`; plan Stage 2).
- `calibration-final/DECISION.md`: the perception layer is UNREADABLE at a = 6; no probe leg (plan §2.6).

## The GO

GO-ID-PENDING: RBT129-S2-READOUT-GO-1

## The overflow-handling rule (plan §3.4; the coordinator rules on the draft)

The value is `include-flagged` (this plan's proposal) or `exclude-flagged`.

OVERFLOW-RULE-PENDING: include-flagged

## The continuation build (plan §3.1; from the continuations tooling PR, when it exists)

The sha256 of the option-(c) `libmujoco.so.3.14.0`, built by the committed recipe at its fixed WORKDIR.

BUILD-SHA256-PENDING:
