# RBT-129 Stage 1 readout: rulings cited, not read from branches

## F7 K-SALT de-duplication (resolves READOUT-PLAN.md O-1)

- **Ruling.** Coordinator, 2026-10-01 14:35 UTC, a comment on tracker issue RBT-129. It is labelled
  **DATA-INFORMED**. Quoted as the coordinator relayed it:

  > "A K-SALT reference is de-duplicated only when it shows the double-write signature; otherwise the check reads VOID."

- **Why.** It answers resume-adversary M1 (`resume-adversary/ADVERSARY.md`): the changed K-SALT reading had to be
  recorded as a ruling on F7. The signature is the one `stages.double_write` tests: every repeated line occurs exactly
  twice, in one contiguous range of generations, with no step back after de-duplication and a resume on record (#504).
- **Applied.** The coordinator's ruling of 2026-10-02 12:57 re-evaluated `1/c1-p010-PW-G/129003` as **PASS** under the
  merged `half_compare`. The census reference `stage0/c1-p010-PW-G/129003/S` shows the signature: 347 duplicate lines
  over generations 55–59, each written twice, from one resume. The resume adversary's N5 independently confirms this.
- **Record.** `KSALT.txt` on `ckpt/rbt-129-stage1-c1-p010-PW-G-129003-record` at
  `b00fc6af02fcf6d67dc7b257340e98e70f992a5a`. It is the rewritten record, and it keeps the superseded VOID text.
  **Cited, not read**: the plan's author has not fetched or read this branch. The readout reads it at integrity,
  after the go.

## COORD-RULING-512: the #512 adversary MUSTs (2026-10-02, before any Stage-1 output was opened)

- **The full text, verbatim:** `COORD-RULING-512.md`. It was relayed by the coordinator, session
  `session_017eUHGNdTSsoVFAtLaJWehF`.
- **What it rules.**
  - **R1:** EARNS calls count at every point with an income call.
  - **R2:** EARNS-TIE is a decided income call, so it fails verdict 5.
  - **R3:** the support rule for M2 and T1, NOT TESTABLE, and "NO VERDICT at Stage 1 (T1 NOT TESTABLE)".
  - **R4:** R-B eligibility at NOT RUN points (DATA-INFORMED), with its pins. No spending without an owner GO.
  - **R5:** every MUST, SHOULD and listed NOTE fixed. `--go` must match the coordinator's go ID.
- **The adversary report** it rules on: `runs/RBT-129/stage1-readout-adversary/ADVERSARY.md`, commit
  `2601f817c65137287005149b112278c59738b95d`.

## The go (adversary NOTE 7, NOTE 13; fix-check FC-NOTE 1)

- **How the script checks it.** `stage1_readout.py` runs only with `--go ID`, where `ID` is the non-empty value of a
  line of this file that begins with the literal tag `GO-ID:`.
- **The ID is registered now as pending** (fix-check 2, FC2-SHOULD 1). Its tag is `GO-ID-PENDING:`, which `go_ids()`
  does not accept. So the script still refuses, and the lock stays closed until the coordinator's go commit, after
  merge, renames the tag to `GO-ID:`.
  - the coordinator will issue the go with this ID after #512 merges;
  - until then nobody runs the script;
  - the go should also confirm the O-1 ruling quoted above, which this repository can only cite as relayed (NOTE 13).

GO-ID-PENDING: RBT129-S1-READOUT-GO-1

## Ruled K-SALT VOID seeds (fix-check FC-SHOULD 2)

- The readout reads ruled K-SALT VOID seeds only from lines of the form `KSALT-VOID: <point> <seed>` in this file (for
  example, a point id and a seed number from 129001 to 129008).
- **None is ruled.** A line is added only by a coordinator ruling, with a citation beside it. A malformed line is a
  HELP.

## stage1-provenance (coordinator ruling on fix-check FC-MUST 2, 2026-10-02)

- **No file from `runs/RBT-129/stage1-provenance/` is read by the plan or the script.** The reason: a per-directory
  verdict file from outside could carry outcome-correlated information. No one will produce it.
- **Ruling item 7** ("confirms from every Stage-1 unit's `platform.json`") is met by the script's own `platform.json`
  check at readout (plan §2.6).
- **The only provenance verdict this plan may cite**, as the coordinator relayed it: "every physics-running Stage-1
  directory is at MuJoCo 3.14.0 (PR #513)". It is cited, not read. The plan's author has never opened #513, its
  branch or that directory.

## O-23, the C1 point mapping (fix-check FC-MUST 1)

- **The ruling.** The fix-check adversary ruled O-23 in `stage1-readout-adversary/ADVERSARY.md` ("O-23 (the C1 point
  mapping): my ruling", commit `7e6e25b`). The coordinator adopted it as is: not a coordinator judgement, because the
  coordinator is exposed (`runs/RBT-129/coordinator/DISCLOSURE-2026-10-02.md`, on the integration branch; not read
  here).
- **What it says.** It adopts the "Stage-1 flanking pair" reading: a C1 sign change adds the R-A midpoint of the
  adjacent Stage-1 pair that flanks it. That gives 7 candidates.
