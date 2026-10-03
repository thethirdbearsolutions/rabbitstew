# Coordinator ruling on the continuations tooling (#527, adversary #531): ACCEPTED; build and overflow rule REGISTERED

*Coordinator: `session_017eUHGNdTSsoVFAtLaJWehF`. Ruled 2026-10-03 ~21:10 UTC. **COORDINATOR-EXPOSED** (see `DISCLOSURE-2026-10-02.md`). No R-B, Stage-2 or scan data exist.*

*Inputs:*
- *Tooling: #527, final head `2a03a159f6605169f4fcf6eda65b86f4e27b878d`, squash-merged as `7dbb650e868466548f4c340a169f8cf687b0bd5c`.*
- *Adversary: #531 (`session_01P8aqsdg3DfgiFUuB4jGcuv`), head `5907a8de1695237d3f992dc4a0742250c929f01f`:*
  - *round 1, MERGE WITH FIXES: 0 BLOCKING, 5 MAJOR, 7 MINOR, 6 NOTE, and W1–W9 on the draft;*
  - *fix-check 1, MERGE WITH FIXES: new MAJOR FC-A and FC-B;*
  - *fix-check 2, **MERGE**.*
- *Full suite on the coordinator's trial merge of both, in a clean `.[dev]` venv without scipy: 1122 passed, 2 skipped (18 min).*

## T1. The tooling is ACCEPTED

The tooling covers build (c), the run-lane gates and the EPA log, the M/N scan job, the R-B lanes and the crash and quarantine refusals. The adversary verified by re-running:
- an independent from-scratch rebuild gives the same sha;
- the patch is log-only, apart from the fail-closed write;
- identity with stock: 4 units (the author's), 1 of them reproduced by the adversary;
- the forced overflow, 10/10 at WORKERS=2 after FC-A;
- FC-3 refuses stock, `LD_LIBRARY_PATH` and `LD_PRELOAD` (exit 9);
- there are no `run.log` readers;
- the scan list is `lanes/1-MN` minus the CRASHED unit;
- R-B's 224 jobs and their gates;
- FC-B is fixed: a fork's own log starts clean, and the plan's parser reads CLEAN.

The merge is a **squash** (FC-E), so the withdrawn smoke logs of `5d04edc` stay off the base history.

## T2. BUILD-SHA256 is REGISTERED (v3)

- **The build:** `libmujoco.so.3.14.0`, sha256 **`2aea9a9447d68edf07936df0d7d6a0c37b7e2df54441814b20ddd6e96ab763f4`**, marker `rbt129-epa-instr/3`, built in `/opt/rbt129-mjbuild` with clang/LLD 18.1.3.
- **Cited by blob at `7dbb650e868466548f4c340a169f8cf687b0bd5c`:**
  - `scripts/build_mujoco_instrumented.sh` `9b39706`;
  - `runs/RBT-129/continuations/build/mujoco-3.14.0-rbt129-epa-log.patch` `708a3af`.
- **Superseded:** v2 (`1d138916…`, marker /2) and v1 (`7ae75f7f…`, marker /1) are not registered, and no continuation ran on them. Only identity, smoke and forced tests did.
- **MAJOR 3.** The Stage-2 plan §3.1 still cites the v1 blobs `1b6cf31`/`ccde8f9`. This ruling governs over that text. The drivers round corrects §3.1.
- **The lock.** `RULINGS-CITED-S2.md` opens `BUILD-SHA256:` with this sha, in a commit of its own.

## T3. The continuation overflow rule is REGISTERED: `RBT129-OVERFLOW-RULE-1`

- **The rule.** `runs/RBT-129/continuations/OVERFLOW-RULE.md` is draft r3 plus amendments A1–A3. These are the fix-check 2 residuals:
  - A1: the registered tooling commit;
  - A2: S60-phase propagation reads seasons 0–59 of the source log only;
  - A3: build PASS needs every start line's sha.
- **Primary analysis: `include-flagged`. Sensitivity: `exclude-known-flagged`,** with the whole map recomputed and the OVERFLOW-SENSITIVE marks.
- **The ceiling:** a second attested crash *event* at one point, or a third across GO-1 and Stage 2, stops launches. An unattested crash stops the hive at once. The coordinator does the stopping.
- **Every HELP state has a registered default** (§4.6).
- **Who the rule binds.** It binds R-B and every Stage-2 continuation. The Stage-2 plan cites it (S2-R2). Its `stage2_readout` copies of `attested`/`read_log`/`source_log` are held to the tooling definitions (A1; FC-D). The drivers round ports them.
- **The lock.** `RULINGS-CITED-S2.md` opens `OVERFLOW-RULE: include-flagged`, in a commit of its own.
- **The run-lane gate.** It accepts `RBT129-OVERFLOW-RULE-1` (exit 10 lifts) once this file is on the base.

## T4. NOTE 14: the R-B M forks are inside GO-1

- **The jobs.** The 8 seed-rule M forks at `c2-p030-U-G`, seeds 129009–129016, at most 12.5 / 23.3 core-h.
- **Why they are in scope:**
  - DESIGN §5.2 provides M "up to 6 R-B points";
  - DESIGN's 2b row says "all layers";
  - READOUT-PLAN L882 anticipates them ("129001's M stays CRASHED, 15 of 16").
- **The ruling.** They are **within `RBT129-RB-GO-1`**. The GO's priced figure (140 / 262 core-h, S arms) rises to at most 153 / 286 core-h. That is disclosed to the owner here and in the next progress report.

## T5. Launch order and the drivers round

- **The M/N silent-corruption scan** (owner item 1) launches now, on `lanes/SCAN`: 10 lanes, 5 sessions.
- **R-B** (GO-1) launches now, on `lanes/RB`: 20 lanes, 10 sessions.
- **Runners follow the author's launch recipe.** The no-peek clause is pasted into every runner prompt. Runners relay only start and done lines, overflow counts, refusals and exit codes.
- **NOTE 17.** The lanes pin the launch tree. The drivers round must not merge any change to `runs/RBT-129/launch/`, `scripts/` or `rabbitstew/` while SCAN or RB lanes are live, because restarts would refuse with exit 5. It may be written and reviewed meanwhile. Its merge waits until SCAN and RB are complete, or else re-emits their lanes in the same PR, with the coordinator's agreement.
- **The scan's result** goes to READOUT-STAGE1-CORRECTIONS A7 as counts only (`scan-report`), with the states CLEAN (seasons 60–299) / OVERFLOWED / UNLOGGED and the S60 phase UNSCANNED. The S scan is then the owner's decision.

---
_Generated by [Claude Code](https://claude.ai/code)_
