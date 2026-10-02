# RBT-129 Stage 1 (S arm, and the gated M and N forks): readout plan (pre-data)

*Written and committed before any Stage 1 run output was opened. No `ckpt/rbt-129-stage1-*` branch has been fetched,
checked out, restored or had its tarball read by this plan's author. No season table, history, lineage, cohort file,
run.log, income, alive count or readout output of any Stage-1 run has been read. The quarantined branch
`ckpt/rbt-129-stage1-c2-p030-U-G-129001-M` has not been touched in any way. The commit timestamp is the audit trail.*

*Inputs read so far (registered and ruled texts, launch records, source code; no Stage-1 output):*
- *`DESIGN.md` (r4) in full, especially §4.1–4.2, §5.2–5.5, §6.1–6.4, §7, §8, §11.1, §12 and §15 (Amendment F);*
- *`AMENDMENT-FOUNDING.md` in full (F1–F8, T1–T13);*
- *`mn-crash/RULING.md` (r3), `mn-crash/INTEGRITY-host1.md`, `mn-crash/REPRO-host7.md`;*
- *`lanes/1/launch.txt` and its 20 lane files; `lanes/1-MN/launch.txt`, `lanes/1-MN/gate_table.txt` and its 21 lane
  files (job lines only);*
- *`stageF/screen_table.txt`; `mn-emitter/README.md` (the #500 ruling); `resume-adversary/ADVERSARY.md`;
  `resume-audit/resumed-2026-10-01.txt`;*
- *the precedents `stageP0-readout/READOUT-PLAN.md`, `legs-readout/READOUT-PLAN.md`, and their adversary reports
  `stageP0-readout-adversary/ADVERSARY.md` and `legs-readout-adversary/ADVERSARY-LEGS.md`;*
- *the committed Stage P+0 readout `stageP0-readout/stageP0_readout.txt` (census layer and C1 rows; already read and
  registered) and `stageP0_readout.py`;*
- *source only: `launch/stages.py` (`check_branches`, `expected_branches`, `half_compare`, `double_write`, K-SALT,
  `s60_state`, `valid_at_merge`, `mn_gate`, `mn_plan`, `_label`, `branch_file`), `launch/resumed.py`,
  `launch/blocks.py`, `rabbitstew/ecology.py` (history, lineage, cohorts and log formats; `merge_null`; `_record`;
  `_sweep_fields`; `_log_lineage`), `rabbitstew/provenance.py`, `scripts/regime.py`, `power.py`.*

*Base: `claude/new-session-4cao7d` at `9edecbddb51119e483e277abaaffda743fbd1549`. Launch records: Stage 1 S at
`7bd6d529da549da648a8b94e1430ad40671930bb` (emitted 2026-10-01T09:42:36Z); M/N at
`3461abaef034ab9bd1a1644391ae0564b7e4f823` (emitted 2026-10-02T12:53:06Z).*

*Fix round (pre-data, still before any Stage-1 output was opened): the adversary report
`runs/RBT-129/stage1-readout-adversary/ADVERSARY.md` (`2601f817c65137287005149b112278c59738b95d`, ADOPT AFTER FIXES:
5 MUST, 9 SHOULD, 15 NOTE) and the coordinator's ruling on it, `COORD-RULING-512.md` (R1–R5), are applied here. §13
maps each item to where it is answered.*

Every call, table and map below carries the claim label (Amendment F, T4): **"among holistic and designed stream draws
(founders and their early history) that establish at W118-b"**, and every share-layer line carries **"under the
committed rule"** (§5.4).

## 0. What this readout covers, and what it cannot call

**Covered.**
- The S arm: 36 points × 8 seeds (129001–129008) = 288 units, each `S60` → `ckpt60` → `S` (to season 300), with
  K-SALT at 72 point-seeds (129002 and 129003, salts (1, 0) and (2, 0)).
- The gated M and N forks of `lanes/1-MN`: 38 registered fork jobs (31 M, 7 N) at 9 points. One is CRASHED
  (§2.4); 37 are read.

**Not covered: the perception layer (§6.3), the R8 levers (§5.3e) and the retention layer (§6.4).** Their legs (the
probe leg, the planted set, R_sel and R_marker) are not in `lanes/1` or `lanes/1-MN`. Each will be read under its own
pre-data plan. In this readout:
- every perception call reads **NOT MEASURED (probe leg not read)**;
- LEVER reads **not evaluated** on every EARNS call;
- items per new cell (`steer.py`) and T4 read **NOT MEASURED**.

None of these is printed as a finding.

**What the registered rules allow at Stage 1, worked out from registered inputs only.** These follow from
`gate_table.txt` (registered input: the valid-seed counts it prints were seen at emission, mn-emitter ruling item 7;
this readout notes that they were):
- **N ran at 4 points**, on 2, 2, 2 and 1 seeds. Every one of them is below ⌈3n/4⌉ = 6 valid seeds, so each is
  **settled by §6.1 item 1 or item 2** before any share test is reached. That means EXCLUDED or NEITHER if one fauna is
  extinct by 299 on ≥ 5 seeds, and PARTIAL otherwise (adversary NOTE 1). The same holds at n = 7 or 6 after a K-SALT
  VOID.
- **Every other point has no N arm.** The share call there is **NOT RUN (census g0 = x)** (§5.2; §6.1 item 8).
- So **no share WIN, TIE, CONTINGENT, SATURATED or UNDECIDED body call is reachable at Stage 1.** The body calls that
  can occur are EXCLUDED-H, EXCLUDED-D, NEITHER, PARTIAL-*, VOID, NOT RUN, and "RBT-118 (not available)" at the two
  Stage-1 anchors (§4.2 item 8). The share BH families are empty at Stage 1 (§5, O-22).
- **The map is carried by the income and survival layers**, as DESIGN §6.2 and AMENDMENT-FOUNDING §5 expect.
- The share statistics are still computed. They are printed descriptively wherever this plan says so (§8).
- The code implements every registered call. For Stage 2, the Stage-2 plan must wire VARIANCE-DRIVEN's inputs and LEVER
  into `verdicts`. At Stage 1 they are hard-wired to "not reachable" (no share WIN) and "not evaluated" (FC-NOTE 5).

## 1. Order of operations

0. **This plan** is committed and pushed, then reviewed by its adversary, and the coordinator rules. No Stage-1
   branch is fetched before the coordinator's go.
1. **Integrity (§2).** It reads branch names, `platform.json`, done-markers, `KSALT.txt`, the resume audit's
   provenance files and the season-59 alive counts that the gate already read, and nothing else.
   - **No readout number is computed before integrity passes.**
   - Any integrity failure is a **HELP** wake to the coordinator, and nothing further is read.
   - `integrity.txt` is committed **before** any other output is produced.
2. **Restore.** Only after integrity passes. The S, ckpt60 and ksalt directories of `lanes/1`, and the 37 completed
   M/N directories, are restored through the quarantine guard (§2.5).
3. **Per-seed statistics** (§3), then **per-point calls** (§4), then **families and multiplicity** (§5).
4. **Map-level statistics and T1–T4** (§6).
5. **The §4.2 refinement lists** (§7), computed by script and posted before any Stage-2 arm.
6. **The §8 verdict logic** (§9), evaluated and printed as **provisional** (Stage 1 only; §8 reads the final map).
7. `READOUT-STAGE1.md` (§10).

Everything is computed by one script, `stage1-readout/stage1_readout.py`, from the restored directories. Its outputs
are `integrity.txt` (step 1) and `stage1_readout.txt` (steps 3–6).
- **The go.** The script refuses to run unless `--go ID` matches a `GO-ID:` line in `RULINGS-CITED.md`. The
  coordinator adds that line when it issues the go (adversary NOTE 7; COORD-RULING-512 R5). Today there is none, so the
  script refuses.
- **The `readout` step** also refuses unless `integrity.txt` reads `INTEGRITY PASS` under the same go.
- **Committed now, in full** (MUST 2; COORD-RULING-512 R5): the integrity step, every statistic and call, and the
  `readout` driver that writes `stage1_readout.txt` end to end. An end-to-end synthetic-tree test covers it. That tree
  has all 36 points × 8 seeds, the registered M/N forks line, the CRASHED unit's directory poisoned, M 7 of 8, the
  bound and the paired S.
- **The readout session only runs it.** It writes no code: the earlier exception for a `stage1-provenance/` reader
  adapter is withdrawn with that input (§2.6). No rule, threshold or definition may be added or changed there.
- **The go ID** `RBT129-S1-READOUT-GO-1` is registered in `RULINGS-CITED.md` as `GO-ID-PENDING:`, which the script
  does not accept (FC2-SHOULD 1). The coordinator's go commit after merge renames it to `GO-ID:`. Until then the script
  refuses.
- **Ruled K-SALT VOID seeds** reach the readout only through `KSALT-VOID: <point> <seed>` lines in
  `RULINGS-CITED.md` (FC-SHOULD 2). None is ruled.
- **Tests** (`tests/test_rbt129_stage1_readout.py`) use synthetic fixtures only. The only repository files they read
  are registered inputs: the lane files, the M/N launch record and gate table, the committed census readout and
  `pilot_constants.json`.
- **Fetch hygiene** (SHOULD 8). The readout session never runs a bare `git fetch`, `git pull` or `git fetch --all`:
  the repository's default refspec would fetch `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M`.
  - Every branch is fetched by its own narrow refspec (`fetch_label`), after the quarantine check.
  - The script refuses to start if any local ref names the quarantined unit (`local_quarantine_refs`).

## 2. Integrity (`integrity.txt`)

Each check below prints a verdict and counts. It prints no outcome. A failure stops the readout.

### 2.1 Branches (`check-branches`)

- `stages.expected_branches`' rule is run over the lane set below. The script re-implements it as `expected_labels`,
  with the quarantine guard added. The lane set is:
  - the 20 lane files of `lanes/1`;
  - the 20 lane files of `lanes/1-MN` that remain **with `host1-lane0b.jsonl` in place of `host1-lane0.jsonl`**.
- The result is compared with `git ls-remote --heads origin 'refs/heads/ckpt/rbt-129-*'`, which lists names only.
- **Expected count, from the lane files:**
  - `lanes/1` has 936 jobs: 252 fresh S60, 36 adopt, 72 ksalt, 288 snapshot and 288 resume. They write 648 run
    directories (288 S, 288 ckpt60, 72 ksalt) and 288 unit records.
  - `lanes/1-MN` without `host1-lane0.jsonl` has 37 distinct fork directories. `host1-lane0b.jsonl` repeats two jobs
    of `host1-lane0.jsonl`; they are counted once.
  - **973 labels** in all.
- **PASS:** every expected label has its branch.
- **The quarantine guard (§2.5)** refuses before listing if the expected set holds the quarantined label. That would
  happen if `host1-lane0.jsonl` were passed.
- The quarantined branch's **existence** is printed as a name from the same `ls-remote` listing. Nothing else about it
  is read.

### 2.2 Done-markers

- For every job of §2.1's lane set, the marker `.rbt129-done-<tag>` is present in its directory's latest snapshot.
  The tag is the last field of the job's name. 973 markers are expected.
- Each marker is read on its own with `stages.branch_file(label, member)`, without restoring the directory.
- A marker whose note reads `skipped: extinct pre-merge at season N` is counted as **done (extinct pre-merge)**. Its
  season is not printed in `integrity.txt`.
- **Any S-chain marker missing** (`S60`, `ckpt60` or `S`) is an S-arm failure. Under ruling item 5 that stops the
  hive: HELP.
- **An M or N marker missing** (other than the CRASHED unit) is a candidate second crash. Under ruling item 5 nothing
  is excluded, re-run or replaced, and the M/N readout does not proceed until there is a new ruling with its adversary
  pass: HELP.

### 2.3 The resume audit

- **Why it is re-run.** `resume-audit/resumed-2026-10-01.txt` is clean, but it was taken at 14:40 on 2026-10-01, with
  185 of 576 run directories checkpointed.
- **Where it now runs** (SHOULD 3). It is therefore **re-run inside `integrity()`**, which fails on its findings.
  `resumed.written_twice` is called on:
  - the 576 S and ckpt60 directories;
  - the census sources that the lanes adopt from or K-SALT compares against;
  - the 37 completed M/N directories. `resumed.py` itself lists no `fork` job.
- **How each branch is read.** Each branch is first fetched by its own narrow refspec (NOTE 9), after the quarantine
  check. Only lineage and cohort structure is read: counts and season indices.
- **PASS:** no directory written twice.
- **The one accepted exception** is `stage0/c1-p010-PW-G/129003/S`, under the double-write signature exactly as the
  resume audit and the resume adversary's N5 record it:
  - lineage: 347 rows repeated, in seasons 55–59;
  - cohorts: 5 rows repeated, in the same seasons;
  - no torn line.
  It is listed as accepted.
- **Any other double write**, including a different count at that directory, is a HELP. Its unit is not read until the
  coordinator rules.

### 2.4 The CRASHED unit (ruling items 1, 3, 5)

- **Lane reconciliation.**
  - The jobs of `host1-lane0.jsonl` minus those of `host1-lane0b.jsonl` must be exactly `{1/c2-p030-U-G/129001/M}`.
  - `host1-lane0b.jsonl`'s jobs must be a subset of `host1-lane0.jsonl`'s.
  - `lanes/1-MN/launch.txt`'s `forks` line must hold 38 forks: the 37 completed plus this one.
  - These checks read lane job lines (registered input) only. The branch is never opened.
- **Printed:** `CRASHED: 1/c2-p030-U-G/129001/M (native SIGSEGV in libmujoco 3.14.0, projectOriginPlane under
  mjc_ccd), x4`.
- **Not printed:** how far the unit got (no season, wall time, population, fauna or member; item 3).
- **Disclosure** (the ruling's "What has been seen"):
  - The host1 runner displayed **0 per-season lines** (`INTEGRITY-host1.md`). So there is nothing to disclose under
    R2-2.
  - The coordinator saw job names, exit codes, dmesg lines, faulthandler frames, and attempt start and crash times.
  - The second-host reproduction (`REPRO-host7.md`) reports REPRODUCED. Its scratch directories were deleted unread.
  - The gate table's valid-seed counts were seen at emission (mn-emitter ruling item 7).
- **Exactly one CRASHED unit** is expected. A second (§2.2) triggers item 5.

### 2.5 The quarantine refusal (ruling item 3)

`stage1_readout.py` holds `QUARANTINED_LABEL = "rbt-129-stage1-c2-p030-U-G-129001-M"` and the matching directory
`runs/RBT-129/stage1/c2-p030-U-G/129001/M`. Every function that fetches, restores, reads a file from, or lists the
contents of a branch or run directory goes through `refuse_quarantined()`. It raises `QuarantineRefusal`:
- **for that label** anywhere in a ref or label, as a case-insensitive substring, whatever its prefix (`ckpt/`,
  `refs/remotes/origin/ckpt/`, `x-`, …) or suffix (`-`, `/`, `.tar`, `0`, …). No legitimate label contains it
  (adversary NOTE 6, probes P10–P11; fix-check FC-NOTE 7);
- for any path at or under that directory, **through symlinks too** (`realpath`);
- for any lane file that schedules that directory. That is `host1-lane0.jsonl`, which is never loaded.

The script also refuses to start if a local ref names the unit (§1, fetch hygiene). The `readout` driver restores only
through the guard, so a driver that forgot the CRASHED unit is still refused (a test proves it).

The tests (`tests/test_rbt129_stage1_readout.py`) prove the refusal fires **before** any reader is called (a counting stub
reader stays at zero calls). Neither the unit's files nor its branch enter any table, mean, figure or check. The
`ls-remote` name listing in §2.1 is the only place its name appears, and the ruling allows it.

### 2.6 MuJoCo provenance (ruling items 6 and 7)

- **What is read.** For every run directory of §2.1 that runs the ecology or copies one (288 S, 288 ckpt60 and the 37
  forks; ksalt directories and unit records run nothing), `platform.json` is read alone, with `branch_file`.
- **The one path with no `platform.json`.** This is determined from source (`stages.run_job`, the `snapshot` branch,
  fix1b), on the coordinator's instruction.
  - A `snapshot` job whose S state is fully extinct at or before season 60 does three things:
    - it writes `EXTINCT.txt` into the unit's record (`unit_file`);
    - it creates `ckpt60` with `_mark` alone (`os.makedirs`, plus the done-marker `skipped: extinct pre-merge at
      season N`);
    - it saves that directory.
  - No ecology runs there, and S is not copied, so that `ckpt60` legitimately has no `platform.json`.
  - Every other `ckpt60` is `fork_config(S, ckpt60)`, a whole copy of S, platform record included.
  - S itself always ran the ecology (or was adopted whole from the census).
  - The forks are copies of a live `ckpt60` and are then resumed. An extinct unit is not valid at the merge, so it
    has no fork.
- **The expected count** is therefore 288 S + (the `ckpt60`s copied from a live S) + 37 M/N, not a fixed 613.
- **A `ckpt60` with no `platform.json` PASSes** only when its unit record holds `EXTINCT.txt` **and** its done-marker
  reads `skipped: extinct pre-merge`. Otherwise it FAILs.
- **PASS.** The record's top-level `mujoco` is `"3.14.0"`, **and so is every entry of its `resumes` list**
  (`provenance.record_resume` appends one per `Ecology.resume`). An adopted S60 (129001) carries the census run's own
  top-level record. It is held to the same rule.
- **FAIL.** A missing or unreadable `platform.json` other than the extinct path above, a missing `mujoco` field, or
  any other version. Every failing directory and the versions found are listed. Any other version is **re-ruled**
  (item 7): HELP.
- **What is printed.** The 2.6 line prints the **aggregate PASS/FAIL only**. It gives no count of the extinct `ckpt60`s
  and no per-unit list. The extinct units belong to the survival layer, and are printed there (the per-point S
  lines). For the same reason, §2.2 prints one count of present markers, with extinct-pre-merge skips included and not
  split out.
- **No file from `runs/RBT-129/stage1-provenance/` is read** (coordinator ruling on fix-check FC-MUST 2). A
  per-directory verdict file from outside could carry outcome-correlated information, and no one will produce it.
  - Ruling item 7 is met by this check alone.
  - The only provenance verdict this plan cites is the coordinator's relayed statement: every physics-running Stage-1
    directory is at MuJoCo 3.14.0 (PR #513). It is cited, not read (`RULINGS-CITED.md`).

### 2.7 K-SALT (F7) and K1, as registered

- **K-SALT.** 72 point-seeds: seeds 129002 (salts (1, 0)) and 129003 (salts (2, 0)) at all 36 points.
  - The verdict is the **unit record's `KSALT.txt`**, the file `s60_state` and the M/N gate read. Its first line is
    `KSALT PASS` or `KSALT VOID`.
  - The ksalt directory's own `KSALT.txt` and its done-marker note are printed beside it. Any disagreement among the
    three is listed.
  - **The known case** is `1/c1-p010-PW-G/129003/KSALT`: VOID at `830450e`, and PASS under the #504 de-duplication on
    the double-write signature. It is printed with that history and cites resume-adversary M1, which asks that the
    changed reading be recorded as a ruling on F7.
  - **O-1: resolved by coordinator ruling** (tracker RBT-129, 2026-10-01 14:35 UTC, DATA-INFORMED; applied
    2026-10-02 12:57; record `b00fc6af02fcf6d67dc7b257340e98e70f992a5a` on
    `ckpt/rbt-129-stage1-c1-p010-PW-G-129003-record`). It is quoted in `RULINGS-CITED.md`, and this plan has not
    read that branch.
    - The ruling governs: a K-SALT reference is de-duplicated only when it shows the double-write signature.
      Otherwise the check reads VOID.
    - `1/c1-p010-PW-G/129003` reads **PASS** under it.
    - The readout checks that the record's first line reads `KSALT PASS`, and prints it with the superseded VOID
      noted. Any other reading is a HELP.
  - **A VOID** voids the point for the seed (F7; §6.1 item 3). See §4.1 for how a VOID seed enters n.
  - F7 also says a mismatch **re-opens RBT-129c's stream claim**. So any record verdict other than PASS is a HELP, and
    the point × seed is read as VOID only after the coordinator rules.
- **K1 (fork identity).** K1 is a pilot control (§5.5: "at every pilot point"). Stage 1 runs no K1 job. Its status as
  registered is printed:
  - PASS at `c1-p030-U-L` and `c0-p030-U-L`;
  - UNTESTABLE at `c1-p030-PW-G` and `c2-p030-PW-G` (129001 extinct before the merge; no re-run exists);
  - **never tested on a PW terrain** (P+0 adversary SHOULD 4).

  §6.1 item 3 VOIDs a point when K1 **failed** there. K1 failed nowhere, so no Stage-1 point is VOID by K1.
  **OPEN (O-2):** whether "K1 never tested on PW" should qualify the 7 PW M/N arms. This plan prints the
  qualification beside every PW M/N row and VOIDs nothing for it.
- **The gate's input, re-checked.**
  - The valid-at-merge counts (both faunas alive at season 59 in S, `stages.valid_at_merge`) at the 10 M-eligible
    points must equal `gate_table.txt`'s `valid` column.
  - They are read from each unit's ckpt60 `history.json` **alone**, with `branch_file`. No directory is restored during
    integrity (SHOULD 9).
  - Each admitted fork's seeds must equal that point's valid seeds.
  - A mismatch is a HELP.
  - These counts are the gate's registered input, already seen. Reading them is integrity, not a peek.

### 2.8 VOID handling (summary)

| source | scope | effect |
|---|---|---|
| K-SALT VOID (F7) | a point × seed | a HELP first (F7 re-opens the stream claim); once ruled, that seed is removed from the point (§4.1), counted and printed |
| K1 FAIL (§5.5) | a point's M and N | the share call is VOID; no Stage-1 instance (§2.7) |
| K2 pooled fail (§5.5) | the stage's share layer | every share call VOID; at Stage 1 it changes no call (§0) |
| K2 per-point fail | a point's share call | VOID; at Stage 1 every N point is settled by item 1 or 2 first (§6.1 precedence: VOID is item 3) |
| CRASHED (ruling item 1) | one M arm × seed | **not VOID**: a unit state; §2.4, §4.6 |
| a MuJoCo version other than 3.14.0 | any unit | **not VOID**: re-ruled (HELP) |
| a double write | any unit | **not VOID**: HELP |

## 3. Per-seed statistics (exact definitions)

Seeds j = 1…8 (129001–129008). Each runs at its salts from `lanes/1/launch.txt` (129002 (1, 0), 129003 (2, 0),
129007 (1, 0), 129008 (1, 0), others (0, 0)). Faunas H = `holistic`, D = `conventional`; NB = `null_b`. The price p is
`config.json`'s `sim.food.work_cost` (per kJ). The living cost is `ecology.living_cost` (0.25).

### 3.1 Alive counts, validity, extinction

- **alive(k, s)** is the `alive` field of S's `history.json` entry for population k at season s. **A missing entry
  reads 0.** The ecology writes no row for an empty cohort, and the run stops when every population is empty
  (`ecology.py` `step`, `run`). A unit with `EXTINCT.txt` reads 0 for both faunas from its extinction on.
- **Valid for the share test:** alive(H, 59) > 0 and alive(D, 59) > 0. This is `stages.valid_at_merge`, read from
  `ckpt60`, or from S where an extinct-pre-merge unit has no ckpt60 state. The #500 ruling item 4 shows booked and
  before-refill extinction cannot differ.
- **Valid for the income test:** alive(H, 239) > 0 and alive(D, 239) > 0 in S. That is "alive through season 239":
  present at the end of 239, so both have member-seasons in the window.
- **Extinct by 299 in S:** alive(k, 299) = 0.

### 3.2 Income flow and x_j (§5.3a; §6.1)

- **A member-season** is a `lineage.jsonl` row with `generation` in 240–299, the fauna's `population`, a `death` field
  absent or in {`starved`, `aged`}, and a `food` field present.
  - Rows with `death` ∈ {`cull`, `merge-null`} are excluded: not the economy's own deaths.
  - Newborn rows are excluded. They are written at birth with no season result: no `food`, `evals` 0.
  - Under `--sweep-log` each member evaluated in a season appears exactly once: as a living row, or as a `starved` or
    `aged` row.
- **Season net** = `food − p · work / 1000`, with work in J. This is DESIGN's "food − p · kJ", as the P+0 readout
  computed it.
- **Flow(k)** = the mean of season net over k's member-seasons in 240–299, pooled over seasons (member-season
  weighted).
- **x_j** = Flow(H) − Flow(D) in S, at an income-valid seed.
- **Cross-check at every income-valid seed** (SHOULD 3).
  - Per season, the member-season count must equal (alive − births) + deaths from `history.json`.
  - The flow must equal the member-season-weighted mean of `food_mean − p · work_mean / 1000` from the sweep log's
    `*_mean` fields, which cover "every member this season evaluated (the living and the dead)".
  - **A mismatch is a HELP**: repeated lineage rows would enter the flow twice.
- **An empty flow is a HELP** (SHOULD 7): an income-valid seed with no member-season for a fauna. It is not a crash.
- **Variants, printed beside and descriptive only:**
  - (i) `last_score` in place of the season net. This is a cross-check, not a true variant (NOTE 3):
    `Simulation.harvest` already zeroes food and work on an exploded robot, so both read 0 on exploded rows.
  - (ii) survivors' rows only (`death` absent).
  - (iii) the P+0 readout's convention: newborn rows read as 0, as `stageP0_readout.flows` did. It is printed for
    continuity with the pilot SD constants.
- **OPEN (O-3):** this plan reads DESIGN's "food − p · kJ" literally and includes the season's starved and aged
  members. Variants (i)–(iii) are printed so the adversary can weigh the alternatives. None is chosen by its value.
- **Exclusions** (SHOULD 7). No seed or run is excluded, winsorised or re-weighted for any reason except these:
  - K-SALT VOID, as ruled;
  - validity (§3.1);
  - CRASHED.

  The P+0 readout's post-plan exclusion of null runs has no counterpart here.

### 3.3 The share change y′ (§5.3b; §6.1)

- **For an M arm** at seed j: share(s) = alive_M(H, s) / 120, the holistic fauna's share of the 120 pooled slots
  (§5.3b).
- **s₀** = n_H / (n_H + n_D), from S's season-59 counts (ckpt60). n_H and n_D are printed per seed.
- **y′_j** = mean over s = 240…299 of share(s), minus s₀.
- **For an N arm** at seed j with K = the merge-null kind (holistic on odd seeds, designed on even; `stages.null_kind`):
  y′_null = mean over 240–299 of alive_N(K, s) / 120, minus n_K / (n_K + n_other) at 59. This is the P+0 readout's
  §3(b) convention. The replaced fauna's count at the merge is B's count (`ecology._replace_with_null`).
- **The empty-world convention** (required by ruling item 4's bound).
  - A season with no history entry for a label, because the cohort is empty or the run stopped when every population
    emptied, reads **alive 0, so a share of 0 of the 120 slots**.
  - A world that empties before season 240 therefore has share 0 in every window season, and y′ = −s₀.
  - The share is never set outside [0, 1], so ruling item 4's bound is printed (§4.6).
- **Printed beside, descriptive:** the share of the living, alive(H) / (alive(H) + alive(D)), with an empty world read
  as undefined and the seed listed. **OPEN (O-4):** y′ mixes a share of 120 slots at the window with a share of the
  living at the merge. The registered text says both, so this plan keeps both and prints the living-share variant.
  The P+0 adversary's note on `c1-p030-PW-G/129002` (a collapse to about 47 read through the /120 denominator) is the
  reason for the print.
- **No exclusion** of N runs beyond validity at the merge. The 7 N runs are all on valid seeds by construction (T5:
  "the same seed rule as M").

### 3.4 g0 for RESOLVING (§6.2)

- **g0_j** = the M arm's mean season net (§3.2's member-season definition) over seasons 180–299, faunas pooled,
  + 0.35.
- **Its 90% bounds** = mean ± t₀.₉₅,ₙ₋₁ · SD/√n over the point's M seeds.
- They are undefined at n < 2, and then the point is **not RESOLVING**.
- The census g0 (gate table) is printed beside.
- The census convention differs: the census g0 (T5, `stageP0_readout.py`) reads newborn rows as 0. So the M g0 is
  also printed under that convention, for a like-for-like comparison (NOTE 4).

### 3.5 Per-birth income and MARGINAL (§6.1, r3 S-3)

- Per fauna, from `scripts/regime.py RUN --windows 240-299` on S: the window's complete lives' mean lifetime gain
  (`fitness`, whose per-season gain is `food − p · kJ`, forfeited on explosion). Censored lives are counted.
- regime.py's `net_per_birth` subtracts the living cost. This plan reads DESIGN's "net income per birth" in DESIGN's
  own vocabulary, where "net" means net of work: **per-birth income = `net_per_birth` + living cost**.
- **MARGINAL:** either fauna's per-birth income < 0.25.
- **The aggregation** (FC-SHOULD 3). A fauna's per-birth income at a point is the mean, over the point's
  income-valid seeds that have one (a complete life born in 240–299), of each seed's regime `net_per_birth` + 0.25.
  MARGINAL is undefined, and not printed, when either fauna has no such seed.
- **OPEN (O-5):** the other reading is `net_per_birth` < 0.25, a bar twice as high. DESIGN §13 open item 4 already
  calls the bar strict. Both are printed, and the call uses this plan's reading.

### 3.6 VARIANCE-DRIVEN inputs (§6.1)

Per M seed, M arm, seasons 180–299, per fauna:
- **the season-to-season SD of member income:** for each member with ≥ 2 member-seasons in the window, the SD (ddof 1)
  of its season nets; then the mean over those members;
- **its share of zero-income seasons:** member-seasons with `food` = 0. **Exploded rows count**: their food is zeroed.
  The exploded count is printed (COORD-RULING-512 R5, NOTE 3).

The regression is §4.4's. **OPEN (O-6)** on "season-to-season": this plan uses the within-member SD, and prints the
pooled member-season SD beside it. It is not reachable at Stage 1 (no share WIN).

## 4. Per-point calls (DESIGN §6.1, F's T6)

Thresholds at n: EXCLUDED at ≥ ⌈5n/8⌉ seeds, PARTIAL at < ⌈3n/4⌉ valid seeds (5 and 6 at n = 8).

### 4.1 n, and VOID seeds

- n = 8 minus the point's K-SALT-VOID seeds. A point with n = 0 is a HELP, never NEITHER (NOTE 14).
- A VOID seed is not counted as extinct, invalid or valid. It is listed, and the call carries "K-SALT VOID on seed j".
- **OPEN (O-7):** the alternative is to count a VOID seed as invalid. That would let a code fault produce a PARTIAL
  survival call, so this plan does not use it.

### 4.2 The body call, in registered order (the first that applies)

1. **EXCLUDED-H / EXCLUDED-D / NEITHER.** A fauna is extinct by 299 in S on ≥ ⌈5n/8⌉ seeds. EXCLUDED-X names the
   extinct fauna (§8: a survival call for Y is EXCLUDED-(other)). If both faunas are, the call is NEITHER.
2. **PARTIAL.** Fewer than ⌈3n/4⌉ seeds are valid for the share test.
   - The named fauna is the survivor. Count the invalid seeds on which only H was alive at 59 (a_H), and those on
     which only D was (a_D).
   - **PARTIAL-H** if a_H > a_D. **PARTIAL-D** if a_D > a_H.
   - **PARTIAL-TIED** otherwise. That includes the case where every invalid seed lost both faunas. It is counted in
     M1 as PARTIAL with no survivor, and is a survival call for neither fauna.
   - **OPEN (O-8):** DESIGN names one survivor and does not say what to do with mixed seeds. This rule is the
     resolution.
3. **VOID.** K1 or K2 failed at the point (§2.8).
4. **H-WIN.** The share test on y′ (two-sided one-sample t over the point's share-valid seeds with an M and N arm) is
   BH-significant in the WIN family (§5), mean y′ > 0, and mean y′ ≥ δ_s = 0.10.
5. **D-WIN.** The mirror: mean y′ < 0 and |mean y′| ≥ 0.10.
6. **CONTINGENT.** All of the following:
   - F = var(y′) / σ̂²_null exceeds the one-sided 0.99 point of F(n − 1, df_null);
   - F is BH-significant in the CONTINGENT family;
   - neither 4 nor 5 holds;
   - df_null ≥ 12. Otherwise CONTINGENT is **not callable** at the stage (r3 S-2).

   σ̂²_null is pooled **per kind** (SHOULD 1). For each null kind K (holistic on odd seeds, designed on even), the pool
   takes every K-null run of the stage's N points, plus RBT-118's anchor nulls at 240–299 when delivered, with each
   (point, kind) mean removed. df_K = Σ over K's points of (n − 1). That reads "pooled per kind … with the kind offset
   removed" together with r3's "df ≈ (k × 4 − k) per kind".
   - **The pin.** The M arm's y′ is the holistic share change. So its F test divides by the **holistic-null** kind's
     σ̂², and CONTINGENT is callable only when that kind's df reaches 12. The designed-null σ̂² and df are printed
     beside it. **O-9 is fixed to this pin; it is open for the fix-check.**

   At Stage 1 the gate table's seeds give holistic df 2 (c0-p030-PW-G and c1-p010-PW-L, two odd seeds each) and
   designed df 0. So CONTINGENT is **not callable**.
7. **TIE.** TOST on y′ at ±0.10 succeeds (BH within the TIE family), **and** the point is RESOLVING (§4.5).
8. **SATURATED** if M and N ran and the point is not RESOLVING. **NOT RUN (census g0 = x)** if N did not run.
   - At the two Stage-1 anchors (`c1-p030-U-L`, `c1-p030-PW-G`) the share column reads **RBT-118 (not available)**
     unless RBT-118's or the anchor fallback's arms have been delivered at the sweep's window, with the sweep's seeds
     reported separately (T7). M4 counts it under NOT RUN with that note.
   - **OPEN (O-10):** whether the anchors' share column should instead block the readout. This plan says it does not.
9. **UNDECIDED.** Otherwise.

**VARIANCE-DRIVEN** and **LEVER** flags are computed for every share WIN. A VARIANCE-DRIVEN WIN is counted as its own
category in M1/M4 and is not a WIN in §8.

### 4.3 The income layer (§6.1)

- **Tested at every point**, on its income-valid seeds that are not K-SALT VOID, when there are ≥ 2 of them. K1 and
  K2 concern the M and N forks, so they VOID the share call and never the income call. A body call of VOID still
  makes the point not habitable for §8 (§9).
- **OPEN (O-11):** §6.1 sets no minimum, and AMENDMENT-FOUNDING §5 priced income power at valid n = 2…8, including
  points that are PARTIAL. So a survival body call does not suppress the income call.
- **§8 counts every EARNS call, wherever it is made** (COORD-RULING-512 R1). Habitability enters only as the
  denominator of verdict 3 (and of verdict 6's EARNS-TIE share). The earlier "habitable points only" restriction is
  withdrawn; it is printed only as a labelled, non-registered line (§9).
- The order:
  - **EARNS-H / EARNS-D:** x̄'s two-sided one-sample t is BH-significant in the EARNS family, and |x̄| ≥ 0.10, with the
    sign of x̄.
  - **EARNS-TIE:** TOST at ±δ_i = 0.15. Its p is max(p_lower, p_upper) of the two one-sided t tests (H₀: μ ≤ −0.15;
    H₀: μ ≥ +0.15), BH-significant in the TIE family.
  - **UNDECIDED:** otherwise.
- **Flags.** MARGINAL (§3.5) is printed on every EARNS call. **LEVER is not evaluated** (§0).
- Printed beside each call: the one-world column, i.e. the M arm's flow per fauna at points with an M arm (§4.6).

### 4.4 VARIANCE-DRIVEN (§6.1, r3 S-4)

- Per seed: y′_j regressed (OLS, with an intercept) on the standardised difference of the two faunas' mean income
  (M, 180–299) and on the standardised difference of their income SDs (§3.6).
- **VARIANCE-DRIVEN** when both hold:
  - the SD term's partial t, in the WIN's direction (the loser has the larger SD), exceeds the mean term's;
  - the mean term's partial t is below 2.
- At n − 3 < 1 residual df the fit is undefined, and the WIN is printed "VARIANCE-DRIVEN not testable".

### 4.5 RESOLVING (§6.2; ruling item 4(b))

- **Evaluated only where M and N both ran** (the 4 N points), with `power.resolvable(g0_lo, g0_hi, "lottery", n,
  reps=1500)` at the point's §3.4 bounds and its share-valid n.
- **The replica is scaled by the pilot** (MUST 1b). `power.load_pilot("stageP0-readout/pilot_constants.json")` runs
  first and sets `Y_SCALE` = 1.5297. DESIGN §4.1 and §10.1's last bullet rescale "the gate and the checks"; #500 item 2
  exempts the gate's thresholds only. The scale is printed in the header of `stage1_readout.txt`.
- **RESOLVING requires the pass at both bounds** (MUST 1a). `power.resolvable` returns `(rows, passes)`, and
  RESOLVING is `passes`. The earlier code took the truth value of the tuple, which is always True. A test now uses the
  real `power.resolvable`.
- At n < 2 the bounds are undefined, so the point is not RESOLVING.
- A point without N is **never** RESOLVING: not in §8 verdict 6, not in M4, not in the §6.3 cross-tab.
- At Stage 1 every N point is settled by §6.1 item 1 or 2 first. RESOLVING is printed there descriptively and changes
  no call.

### 4.6 The CRASHED seed (ruling item 4)

- The point `c2-p030-U-G` keeps n = 8 valid for every S-based statistic. Validity is S at 59, and S at 129001 is
  untouched everywhere.
- Its M arm feeds **only** these descriptive outputs, each on the **7 completed seeds**, with no imputation:

  | output | how |
  |---|---|
  | y′ (descriptive; no N, so NOT RUN) | mean and SD at n = 7 |
  | one-world column and interference table (M − S, per fauna) | **S paired on the same 7 seeds** (129002–129008) |
  | the regime readout on the M arm | n = 7 |
  | M2's share model and the secondary share Wald (T1) | n = 7 at this point; descriptive at Stage 1 |
  | verdict 4's denominator ("points with an M arm") | unchanged: the point has an M arm |

- Its M row reads **M 7 of 8 (1 CRASHED)** wherever n is printed.
- **The bound under arbitrary missingness** (item 4, Sensitivity):
  - s₀ is 129001's holistic share at season 59, n_H / (n_H + n_D), read from that unit's **ckpt60** at readout. The
    ckpt60 branch `rbt-129-stage1-c2-p030-U-G-129001-ckpt60` is not quarantined.
  - Ruling item 4 says "read from S60". The S60 job writes `S`, whose latest snapshot is at season 300, so `ckpt60`,
    the season-60 copy, is the S60 state (NOTE 2).
  - The printed bound on the 8-seed mean y′ is [(Σ₇ y′ − s₀) / 8, (Σ₇ y′ + 1 − s₀) / 8], labelled **"bound under
    arbitrary missingness"**.
  - It holds under §3.3's empty-world convention, which keeps every share in [0, 1].
  - Income flow has no logical bound, and the readout says so.
  - No min- or max-of-7 substitute is printed.
- **The paired-S rule in general.** At every M point the interference table pairs S on the M arm's seeds, which are
  the point's valid seeds (T5).

## 5. Families and multiplicity (§7.1)

- **Families.** Each is one test per point, BH at q = 0.10:
  - share WIN (two-sided t on y′);
  - share TIE (TOST at ±0.10);
  - share CONTINGENT (the F test);
  - null centring (K2 per point);
  - income EARNS (two-sided t on x);
  - income TIE (TOST at ±0.15).

  Perception per fauna and retention per fauna are not measured here.
- **Membership (ruling item 4(a)).** The share families hold **only points where N ran**. A point with M and no N has
  its y′ printed descriptively, **never tested and never entered in a BH ranking**.
  - **OPEN (O-22).** A point where N ran but whose body call is already settled by §6.1 items 1–3 (EXCLUDED,
    NEITHER, PARTIAL or VOID) can take no share call. So it enters no share family, and its share p-value is printed
    descriptively. At Stage 1 that is all 4 N points, so the share families are empty.
  - The income families hold every point tested by §4.3.
- **K = the number of tests in the family at this stage.** Untested points do not count. BH is the standard step-up:
  reject the k smallest p-values for the largest k with p₍ₖ₎ ≤ k·q/K. Ties in p are handled by that rule.
- **Provisional.** Stage-1 calls are provisional. The final map applies BH once over all points after Stage 2, with
  R-B's combined p-values (§7.1).
- **The cross-point correlation** of the seed-level statistic, per layer:
  - Pearson's r over the seeds valid at both points, for every pair of tested points with ≥ 3 common valid seeds.
    The mean and the maximum over pairs are printed.
  - If the mean exceeds 0.3, **Benjamini–Yekutieli** calls (q / Σᵢ 1/i) are printed beside BH's, and a call that holds
    under BH only is marked so.
- **K2** (§5.5).
  - **Pooled:** over the stage's 7 N runs, PASS iff |mean y′_null| < 0.05 **and** the two-sided one-sample t over the
    runs does not reject at α = 0.05. **OPEN (O-12):** this reads "differs from 0 by < 0.05 (t over seeds)" as that
    conjunction.
  - **Per point:** PASS iff the null's t test is not rejected under BH (q = 0.10, over the N points with ≥ 2 runs),
    **and** |mean y′_null| ≤ 0.15. At 1 run the t clause cannot reject, so **the size bar alone decides** (SHOULD 2).
  - **O-12 has an equivalence reading** (TOST at ±0.05), which would VOID far more often. It changes nothing at
    Stage 1, and it is to be ruled before Stage 2 (NOTE 11).
- **Holm, α = 0.05, over T1–T4** (§6.2).

## 6. Map-level statistics (§7.2, §7.3)

- **M1, the call table.** Counts of each body call and each income call per layout × smell and overall:
  - the survival count (EXCLUDED, PARTIAL, NEITHER) per fauna;
  - MARGINAL;
  - LEVER (not evaluated);
  - the census layer at the 114 points never run at Stage 1, read from the committed census readout (FOUNDING-FAIL,
    regime 30–59) and flagged as the only habitability proxy there, with its 60-season limit.
- **M2, the world model** (seed-level, random intercept per point):
  - **Income (primary).** x_j ~ c + log p + L (2 contrasts, U reference) + s + c × log p + (1 | point).
    - **Coding (O-21).** c − 1 and log(p / 0.03), so that T2's and T3's coefficients are the clutter and price
      effects at the committed world (c = 1, p = 0.03). With c × log p in the model, an uncentred coefficient would
      be the effect at p = 1/kJ or at c = 0. s is G = 1 and L = 0.
    - The data: the Stage-1 grid only, income-valid seeds, at habitable non-VOID points. "Habitable" means neither
      fauna EXCLUDED or PARTIAL, and not VOID (§8).
    - The fit: REML, by profiling the variance ratio.
    - Coefficients are printed with 95% Wald CIs, beside the §12 sign predictions.
  - **Share (secondary).** Only at points with an M arm: logit(share at 240–299, clipped to [1/240, 1 − 1/240]) −
    logit(s₀), on the same terms plus census g0.
    - Its seeds are every completed M seed; at the CRASHED point that is n = 7 (ruling item 4).
    - It runs under the same support rule and NOT TESTABLE conditions.
    - Its Wald T1 tests the world terms net of g0, outside Holm.
    - At Stage 1 it is descriptive. It is not identifiable on 1 habitable point (ruling NOTE 3).
    - Its point floor counts census g0 as a term, so it needs P + 3 points. That is stricter than the income fit and
      is kept, because the model is descriptive (FC-NOTE 3).
  - **Sensitivity fits** come at Stage 2.
- **When M2 cannot be estimated** (MUST 3; COORD-RULING-512 R3, verbatim in `COORD-RULING-512.md`).
  - **Support rule.** A world term whose column has no variation among the habitable income-valid seeds is dropped.
    c × log p is dropped when c or log p has fewer than 2 levels there. The dropped terms are printed.
  - **T1's df** is P, the number of remaining world terms.
  - **T1 is NOT TESTABLE** if any of these holds:
    - P = 0;
    - there are fewer than P + 2 habitable points;
    - the fit is singular (a rank-deficient design or a singular X′H⁻¹X) or non-finite under the pinned settings.

    The pinned settings are the λ grid of 0 and 10⁻⁴…10³ (57 log steps) and 80 golden-section steps. A failed fit
    gets no re-specification and no retry.
  - **T2 and T3** are each NOT TESTABLE if their term is dropped, or if T1 is.
  - **A NOT TESTABLE test enters Holm at p = 1.**
  - A collinear design (for example habitable points on a c/log p diagonal) is NOT TESTABLE as a whole under R3. It
    does not merely lose its interaction (FC-NOTE 4).
  - Why this matters: from the gate table, 9 of the 10 M-eligible points have fewer than 6 valid seeds, and several
    PW and L points cannot be habitable. So a dropped term is likely.
- **T1, T2 and T3** come from the income fit:
  - T1: a Wald χ² on the P world-term coefficients jointly;
  - T2: the c coefficient, z;
  - T3: the log p coefficient, z;
  - **Final values.** T1–T3 on the registered fit (the Stage-1 grid, seeds 1–8) are already their final values
    (§7.2). Only Holm waits on T4, so "provisional" applies to Holm and to §8, not to the coefficients (NOTE 10).
  - **OPEN (O-13):** the Wald test uses the GLS covariance at the REML estimates, with no small-sample df correction.
    DESIGN names a Wald test and no df rule.
- **T4: NOT MEASURED** (perception). **Holm at Stage 1 is provisional:**
  - T4 enters with p = 1. That can only reduce rejections of T1–T3 against any p it later takes.
  - It is printed as "T1–T3 Holm with T4 pending".
  - The final Holm comes after T4 is read.
- **M3, break-evens.** For each (c, L, s) row with ≥ 2 price levels among its habitable non-VOID points: an OLS line
  of seed-level x on p (DESIGN: "a line in p per row"), then p* = −a/b with a Fieller 95% interval.
  - The interval is printed as bounded, unbounded or the whole line.
  - p* is compared, descriptively, with 0.018 (c = 1) and 0.053 (c = 0).
  - **OPEN (O-14):** a per-row line in p, not M2's fitted log-p effect.
- **M4, area shares.** Over the 27 G points and, separately, the 9 L points, equally weighted: the fractions of H-WIN,
  D-WIN, TIE, CONTINGENT, SATURATED, NOT RUN, UNDECIDED, EXCLUDED, PARTIAL, VOID, LEVER and VARIANCE-DRIVEN, with
  NEITHER beside EXCLUDED, and the income calls' fractions printed beside.
- **M5, perception: NOT MEASURED.**
- **M6, concordance.** Cohen's κ between the share call's sign and the M arm's income sign over the points where both
  are decided. The same is done against S's income. At Stage 1 no share call is decided, so it prints "no decided
  share call". The interference table is printed.
- **M7, monotonicity.** The number of sign changes of x̄ along each price row and clutter row of the Stage-1 grid,
  over points with an estimate (n ≥ 2). Rows with more than one are listed. A row with a gap is printed with the gap.

## 7. The §4.2 refinement rules (mechanical; computed from the Stage-1 calls alone)

### 7.1 R-A (≤ 16 new points)

- **Candidate pairs.** Adjacent Stage-1 points:
  - on the price axis (same c, L, s), (0.01, 0.03) → midpoint p = 0.018, and (0.03, 0.08) → p = 0.053;
  - on the clutter axis (same p, L, s), (0, 1) → c = 0.5, and (1, 2) → c = 1.5.

  That gives 18 price and 18 clutter pairs at G, and 6 price pairs at L (c = 1 only), **42 pairs**. Midpoint ids
  follow the census naming (`c05`, `c15`, `p018`, `p053`).
- **The layer per pair:** the share layer (ȳ′) if **both** points are RESOLVING, otherwise the income layer (x̄). The
  layer is printed per pair. At Stage 1 every pair is on the income layer, because no point is RESOLVING.
- **A pair is refined when either holds:**
  - **(a) the estimates differ in sign.** Both points have an estimate on the layer (n ≥ 2), and their signs are
    strictly opposite. A zero estimate has no sign. UNDECIDED points count.
  - **(b) the decided calls differ.** On the share layer: different members of {H-WIN, D-WIN, TIE}. On the income
    layer: different members of {EARNS-H, EARNS-D, EARNS-TIE}. Or a WIN (or EARNS) for X beside EXCLUDED-X, NEITHER or
    PARTIAL-(other), i.e. a point where the winner is absent.
  - **OPEN (O-15):** DESIGN's (b) names the share calls. This plan reads it on the pair's layer, and reads "EXCLUDED or
    PARTIAL of the winner" as the winner being absent.
- **Ranking.**
  - Rank by |t₁ − t₂|, the two points' t statistics on the pair's layer, descending, with all G pairs before all L
    pairs (smell G first).
  - An infinite |Δt| (an SD of 0) ranks first among its smell. A pair with an undefined t ranks last.
  - Exact ties are broken by the midpoint id, ascending.
  - The first 16 are taken. **OPEN (O-16):** "smell G first" read as a block order, not a tie-break.
- **C1's non-monotone rows** (the 13 rows of `stageP0_readout.txt`). **O-23 RULED: the "Stage-1 flanking pair"
  reading.** The fix-check adversary ruled it, and the coordinator adopted it as is (`RULINGS-CITED.md`).
  - **What a sign change adds.** A sign change on a listed row adds **the R-A midpoint of the adjacent Stage-1 pair
    that flanks it**. So only sign changes on **Stage-1 rows** count:
    - price rows at c ∈ {0, 1, 2} (G) and at c = 1 (L);
    - clutter rows at p ∈ {0.01, 0.03, 0.08} (G).
  - **Why.** §5.1 C1 says the rows "enter R-A's pair list". §4.2 adds "the pair flanking each extra sign change,
    ranked in the same list". R-A's list holds pairs of adjacent Stage-1 points, and its rank, |t₁ − t₂|, exists only
    for them.
  - **What it admits.** From the committed census readout, **7 candidates**: `c0-p018-HP-G`, `c1-p018-PW-L`,
    `c1-p018-U-G`, `c1-p053-U-G`, `c2-p053-HP-G`, `c05-p030-U-G` and `c15-p030-U-G`.
  - **Ranking.** Each ranks by its flanking pair's |Δt| in the same list. It is not duplicated if (a) or (b) already
    selected it.
  - **No other point.** No census point off the Stage-1 grid is ever added. `ra_select` refuses a candidate that is
    not a Stage-1 midpoint.
  - **OPEN (O-17):** "each extra sign change" is read as every sign change on a listed row, because no registered
    order picks which one is extra.
- **L pairs** are refined only if fewer than 16 G pairs fire (O-16; NOTE 12). The report says so.
- **Printed:** every pair with its layer, both estimates and calls, |Δt|, which clause fired, and its rank. Then the
  selected ≤ 16.

### 7.2 R-B (≤ 20 points to n = 16, seeds 129009–129016, screened)

- **Eligible** (O-18, **RULED**: COORD-RULING-512 R4, **DATA-INFORMED**): a body call of UNDECIDED or CONTINGENT,
  **or a NOT RUN body call (a point with no N arm) with an UNDECIDED income call**.
  - The basis:
    - DESIGN §5.2 r4: "At a NOT RUN point the body call falls to the income and survival layers";
    - §10 prices R-B on income MDE80 at n = 16;
    - §11.2 budgets Stage 2b at 20 points.
  - It is labelled DATA-INFORMED because the author knew, from the registered gate table, that the literal list
    ("body call UNDECIDED or CONTINGENT") is empty at Stage 1.
  - The literal list is printed beside, labelled "not the registered reading".
- **No spending is authorized.** The eligibility rule authorizes no compute. **Launching R-B needs its own owner GO.**
  The readout prints the R-B list and its S-arm core-h: points × 8 seeds × 300 arm-seasons at 23.35 / 43.72 core-s.
- **Not eligible:**
  - EXCLUDED, PARTIAL, NEITHER and VOID points;
  - SATURATED points (§5.2's sentence names NOT RUN only; no Stage-1 instance; NOTE 15);
  - **the three RBT-118 anchors** (`c1-p030-U-L`, `c0-p030-U-L`, `c1-p030-PW-G`; R4 (ii)). The sweep does not
    re-run them (§5.2 item 3). If T7's anchor fallback is ever triggered, their eligibility is re-ruled then.
- **Ranking: by conditional power** of the combined test at the first-stage estimate. At a NOT RUN point the CP uses
  the **income** t and the income-valid n (R4 (i)). At an UNDECIDED or CONTINGENT point it uses the share layer's.
  - z₁ = sign(t₁) · Φ⁻¹(1 − p₁/2), where p₁ is the two-sided t p-value at df n₁ − 1.
  - The drift is θ = z₁ · √(n₂/n₁), with n₂ = 8.
  - CP = 1 − Φ(√2·c − z₁ − θ) + Φ(−√2·c − z₁ − θ), with c = Φ⁻¹(1 − α/2) and α = 0.05 (BH half, as §10 prices
    it).
  - Ties are broken by point id. The first 20 are taken.
  - **OPEN (O-19)** on α and the z conversion.
- **Stage 2's combined test** (R4 (iii); `stage2_income_call`).
  - **The EARNS test.** Z = (Z₁ + Z₂)/√2, each half's signed z being the inverse normal of its one-sided t p-value
    (Lehmacher & Wassmer).
  - **The TOST.** Each one-sided TOST z (H₀: μ ≤ −0.15; H₀: μ ≥ +0.15) is combined across the halves by the same
    rule. EARNS-TIE needs **both** combined one-sided tests to pass: the larger p enters the TIE family.
  - **The |x̄| ≥ 0.10 bar** is read on the pooled mean over all 16 seeds.
- R-B's list is posted with R-A's (M12).

## 8. Descriptive only (printed, never tested, never in a family, a verdict or R-A/R-B)

- y′ at every M point without N (5 points, ruling item 4(a)), and at the N points, whose body calls are already settled.
- Per seed: n_H and n_D at the merge.
- The share-of-the-living variant (§3.3).
- The N runs' y′ per run.
- K2's numbers, beyond their verdicts.
- The one-world income column (M flow per fauna) and the interference table (M − S, per fauna, S paired on M's
  seeds).
- The regime readout (`regime.py`) on every S and M arm, per fauna, per 60-season window.
- Per-birth incomes (both readings, §3.5).
- `mean_lifetime_score` for continuity.
- Per point and fauna, S arm, means over seeds: alive at 299; births and deaths (starved, aged) in 240–299; the number
  of seeds extinct and their extinction seasons.
- Food, work and path, as means per member-season over 240–299. The plan earlier said "per season"; the window mean is
  what is printed.
- M5 "NOT MEASURED" and M6's line, which at Stage 1 reads "no decided share call".
- The flow variants (§3.2).
- M-arm g0 beside census g0.
- RESOLVING at the N points (§4.5).
- The bound under arbitrary missingness (§4.6).
- The cross-point correlations and BY.
- The R-B literal list.
- The provisional §8 evaluation (§9), and its two labelled non-registered readings.
- The census layer at unrun points.
- **Founding beside the census** (AMENDMENT-FOUNDING T3; SHOULD 5). At each Stage-1 point, the census's
  FOUNDING-FAIL flags per fauna (unscreened) are printed beside Stage 1's founding (screened): the seeds on which each
  fauna is alive at 59.
- **The §12 scorecard** (SHOULD 6; `scorecard()`), pinned now. Each prediction reads AS PREDICTED, OPPOSITE, NOT SHOWN
  or NOT MEASURED:
  - **item 1.**
    - T2 > 0 and T3 > 0: AS PREDICTED if Holm-rejected with z > 0, OPPOSITE if rejected with z < 0, NOT SHOWN
      otherwise, NOT TESTABLE if dropped.
    - M3 p* above 0.018 at c = 1 and above 0.053 at c = 0, per row: AS PREDICTED if the Fieller lower bound exceeds
      the value, OPPOSITE if the upper bound is below it, NOT SHOWN otherwise.
    - EARNS-D on flat ground at p ≤ 0.03, and EARNS-H at c ≥ 1, p ≥ 0.03: AS PREDICTED if the predicted call occurs
      there and the other does not, OPPOSITE if only the other occurs, NOT SHOWN otherwise.
  - **item 2:** share NOT RUN or SATURATED at more than half the points, and RESOLVING at 0–2.
  - **item 3:** EXCLUDED-D or PARTIAL-H at some p = 0.08, c ≥ 1 point.
  - **items 4 and 6:** NOT MEASURED.
  - **item 5:** the provisional §8 headline is EARNINGS DEPEND.
- Per-point mean H − D and the per-point SD of x (for the power re-read). These are printed, not used to change n.

## 9. The §8 verdict logic (implemented; evaluated provisionally)

§8 reads the **final map**. At Stage 1 the evaluation is printed under the heading **"PROVISIONAL: Stage-1 calls
only; not a verdict"**.

**Terms.**
- **Decided share call:** H-WIN, D-WIN or TIE.
- **Decided income call:** EARNS-H, EARNS-D or EARNS-TIE.
- **Survival call for Y:** EXCLUDED-(other) or PARTIAL-Y.
- LEVER and VARIANCE-DRIVEN calls are not wins. LEVER is not evaluated at Stage 1, so every EARNS call is counted
  with that caveat printed.
- **Habitable:** not EXCLUDED-*, NEITHER, PARTIAL-* or VOID.
- **A counting set for fauna Y in a layer:** ≥ 2 such calls, or exactly 1 corroborated by an M3 p* whose Fieller 95%
  interval lies inside [0.01, 0.08] on that call's (c, L, s) row.
- The dominance verdicts tolerate one uncorroborated call for the other fauna.

**Rulings that govern this section** (COORD-RULING-512, verbatim in `COORD-RULING-512.md`):
- **R1 (MUST 4a).** EARNS calls count in verdicts 1, 2 and 5 at **every point where an income call is made**. "Habitable
  points" is only verdict 3's denominator (and verdict 6's for its EARNS-TIE share). The habitable-only reading is
  printed as a labelled, **non-registered**, descriptive line.
- **R2 (MUST 4b; O-20b reversed).** EARNS-TIE is a decided income call (§8, line 948). Verdict 5's "every decided EARNS
  call favours one fauna X" therefore **fails if any EARNS-TIE exists**. The reading that ignores EARNS-TIE is printed
  as a labelled, non-registered line.
- **R3 (MUST 3).** A NOT TESTABLE T1 is neither "rejects" nor "does not reject":
  - verdicts 1, 2 and 6 are not reachable;
  - verdicts 3 and 5 are evaluated as registered;
  - verdict 4 needs an X-WIN, which is unreachable at Stage 1.

  If no verdict is reached, §8 reads **"NO VERDICT at Stage 1 (T1 NOT TESTABLE)"**.

**In precedence order** (the first that holds; the others that hold are printed beneath):
1. **EARNINGS DEPEND:** T1 rejects (Holm), and EARNS-H and EARNS-D each form a counting set.
2. **DEPENDS** (share): T1 rejects, and H-WIN and D-WIN each form a counting set.
3. **EARNINGS DOMINATED (X):**
   - EARNS-X at ≥ 1/3 of the habitable points;
   - the other fauna has no counting set of WIN, EARNS or survival calls (pooled across those kinds).
4. **ONE BODY DOMINATES (X):** X-WIN at ≥ 1/3 of the points with an M arm (ruling item 4: `c2-p030-U-G` counts), and
   no counting set for the other fauna.
5. **DEPENDS ONLY THROUGH HABITABILITY:** all of the following, over decided calls only:
   - every decided EARNS call favours one fauna X. Under R2, any EARNS-TIE fails this;
   - the other fauna has no counting set of EARNS calls;
   - every share WIN favours X;
   - there is a counting set of survival calls for the other fauna Y.
6. **WORLD-INVARIANT:** all of the following:
   - T1 does not reject;
   - no layer has opposite-sign counting sets;
   - EARNS-TIE at ≥ half of the habitable points.

   The share route needs share TIE at ≥ half of the RESOLVING points **and** ≥ 6 RESOLVING points. RESOLVING counts
   only points where M and N both ran (ruling item 4(b)).
7. **NOT RESOLVED:** none of the above, with T1 testable. With T1 NOT TESTABLE: **NO VERDICT at Stage 1 (T1 NOT
   TESTABLE)**.

**Notes on the logic.**
- An EARNS-TIE counts toward WORLD-INVARIANT and never toward a counting set for either fauna.
- "No counting set for the other fauna" in verdict 3 pools WIN, EARNS and survival calls for the other fauna into one
  count, so two calls of different kinds also count (O-20a, accepted by the adversary).
- **Perception verdicts:** NOT MEASURED here.
- Every verdict line carries the claim label and "earns, not persists".

## 10. The readout report (`READOUT-STAGE1.md`)

1. **The headline:** the M1 call table and M4 shares, with the claim label and "provisional" on every line.
2. **Integrity:** §2's verdicts, the CRASHED line, the disclosure and the quarantine statement.
3. **The per-point table**, one row per point:
   - body call; n valid (share and income); n at the merge per seed;
   - x̄, its SD, t, p, BH and TOST, and the income call, with MARGINAL;
   - M n (`M 7 of 8 (1 CRASHED)` at `c2-p030-U-G`) and N n;
   - y′ (descriptive);
   - census g0 and M g0.
4. **The share layer:** what is NOT RUN and why (the gate); K2; CONTINGENT's df; RESOLVING at the N points.
5. **The one-world column and the interference table.**
6. **M2/T1–T3** with the support rule's dropped terms and Holm (T4 pending); the share model (descriptive); M3 and
   M7.
7. **The R-A and R-B lists**, the R-B core-h with "needs its own owner GO", and the R-B literal list.
8. **The provisional §8 evaluation** under R1 + R2 + R3, with the two non-registered lines.
9. **Founding beside the census**, the census layer at unrun points, and the §12 scorecard.
10. **The regime table** on every S and M arm.
11. **Every OPEN item** (§11) and how it was applied, and the exclusions statement (§3.2).

Every number in the report traces to a line of `stage1_readout.txt`.

## 11. OPEN for the adversary

Status of the items:
- **Resolved by coordinator ruling and listed only for traceability:** O-1, O-11's §8 part (R1), O-18 (R4) and O-20b
  (R2, reversed).
- **Fixed per the adversary:** O-9, now per kind with the holistic-null pin.
- **Ruled by the fix-check adversary, adopted by the coordinator:** O-23 (the Stage-1 flanking pair).
- **The rest** were accepted by the adversary as resolved.

Each item was resolved **before** any data, as stated, and none will be re-resolved by its effect on a call.

| id | where | the ambiguity | this plan's resolution |
|---|---|---|---|
| O-1 | §2.7 | the F7 ruling on the K-SALT de-duplication (resume-adversary M1) | **resolved by coordinator ruling**, not open: tracker RBT-129, 10-01 14:35; applied 10-02 12:57; record `b00fc6a` (`RULINGS-CITED.md`) |
| O-2 | §2.7 | K1 never tested on PW | the qualification is printed; nothing is VOID |
| O-3 | §3.2 | the flow's member-seasons and net | evaluated rows, starved and aged included, food − p · kJ; variants printed |
| O-4 | §3.3 | y′ mixes the /120 window share with the merge share of the living | as registered; the living-share variant printed |
| O-5 | §3.5 | "net income per birth below the living cost" | net of work: regime `net_per_birth` + cost < 0.25 |
| O-6 | §3.6 | "season-to-season SD" | within-member SD, averaged over members |
| O-7 | §4.1 | a K-SALT-VOID seed and n | removed from n; not invalid |
| O-8 | §4.2 | PARTIAL's survivor with mixed seeds | majority of invalid seeds; PARTIAL-TIED otherwise |
| O-9 | §4.2 | CONTINGENT's pooled null and its df | **per kind** (SHOULD 1): per-(point, kind) means removed, df_K = Σ(n − 1); the holistic-null kind divides var(y′) and must reach df 12 |
| O-10 | §4.2 | the anchors' share column | RBT-118 (not available); does not block |
| O-11 | §4.3 | a minimum n for the income test; and (split out) whether §8 counts EARNS at non-habitable points | test: ≥ 2 income-valid seeds, at every point; K1/K2 never VOID it. §8 part: **RULED (R1)**, every EARNS call counts |
| O-12 | §5 | K2 pooled pass rule | \|mean\| < 0.05 and the t test not rejected; the equivalence reading to be ruled before Stage 2 (NOTE 11) |
| O-13 | §6 | the Wald test's df | χ² / z on the GLS covariance |
| O-14 | §6 | M3's line | a per-row OLS of x on p, with Fieller |
| O-15 | §7.1 | R-A (b) on the income layer | read on the pair's layer; "of the winner" means the winner is absent |
| O-16 | §7.1 | "smell G first" | a block order |
| O-17 | §7.1 | "each extra sign change" | every sign change on a listed C1 row |
| O-18 | §7.2 | R-B's eligibility at NOT RUN points | **RULED (R4, DATA-INFORMED)**: an income UNDECIDED at a NOT RUN point is eligible; anchors not; CP on the income t; no spending without an owner GO |
| O-19 | §7.2 | CP's α and z conversion | α = 0.05, inverse normal of the t p-value |
| O-20 | §9 | (a) verdict 3's "no counting set" across kinds; (b) verdict 5's "decided EARNS call" | (a) pooled across kinds; (b) **RULED (R2), reversed**: EARNS-TIE is a decided income call, so verdict 5 fails if any exists |
| O-22 | §5 | share-family membership at an N point already EXCLUDED, PARTIAL or VOID | not in the family; p printed descriptively |
| O-23 | §7.1 | the C1 point mapping (SHOULD 4) | **RULED (fix-check, adopted by the coordinator)**: the R-A midpoint of the Stage-1 flanking pair; only Stage-1 rows; 7 candidates |
| O-21 | §6 | M2's coding, on which T2's and T3's coefficients depend once c × log p is in the model | c − 1 and log(p / 0.03), centred at the committed world; U and L are the references |

## 12. The crash ruling, adopted verbatim (`mn-crash/RULING.md` r3, items 1–7; blob `69b2c508d77447bd37fb1325b0c6050239b81f09`)

Where this plan implements each item:

| item | implemented in |
|---|---|
| 1 CRASHED | §2.4 (the integrity line), §4.6 (M 7 of 8), §2.8 (not VOID; no M1/M4 category; not an invalid seed), §2.2 (no stop rule counts it) |
| 2 no re-run, no substitute | §4.6 (no imputation; no stand-in); R-B (§7.2): if `c2-p030-U-G` is extended, 129001's M stays CRASHED, 15 of 16 |
| 3 quarantine | §2.5 and `stage1_readout.refuse_quarantined` with its test; nothing about how far the unit got is printed (§2.4) |
| 4 (a), (b), the table, the sensitivity | §5 (membership), §4.5 and §9 (RESOLVING), §4.6 (the table; S paired on the 7; the bound and the empty-world convention of §3.3) |
| 5 future crashes | §2.2 (a second missing M/N marker is a HELP; an S crash stops the hive) |
| 6 physics pinned | §2.6 (3.14.0 on every record and every resume) |
| 7 diagnosis, second host, provenance | §2.4 (REPRO-host7: REPRODUCED), §2.6 (`platform.json` at readout); the mechanism diagnosis is not used by this readout |

> ## Ruling
>
> 1. **The unit is CRASHED.**
>    - CRASHED is a **unit state, not a call** (SHOULD 4). It sits beside done, VOID (K1/K-SALT) and NOT RUN.
>    - It enters no M1 or M4 category. It is not an invalid seed: validity is S at season 59 (§6.1 item 2, line 647;
>      T5, line 444), so the point stays 8 of 8 valid.
>    - It counts against no registered stop rule. F4 counts SCREEN-CAPPED seeds only; K2's pooled VOID is N only (§5.5,
>      line 567).
>    - The integrity section records:
>      `CRASHED: 1/c2-p030-U-G/129001/M (native SIGSEGV in libmujoco 3.14.0, projectOriginPlane under mjc_ccd), x4`.
>    - The point's M row reads **M 7 of 8 (1 CRASHED)** wherever its n is printed.
> 2. **No re-run in Stage 1 or anywhere in RBT-129** (SHOULD 6, SHOULD 8).
>    - **Not on another MuJoCo build or a patched build, and no code guard.** A one-path patch could be byte-identical on
>      every trajectory that never enters the faulting path. Even so:
>      - the patched continuation is arbitrary physics at the event;
>      - the patch would be designed after a trajectory-dependent event;
>      - it needs a new pinned tree and an adversary pass, all for a column that can decide nothing (item 4).
>    - **No substitute seed** (§4.2, line 378; F4, line 213).
>    - **No resume from an earlier state.** The crash is deterministic, so this would need a perturbation, which is a
>      substitute seed.
>    - **If R-B extends this point to n = 16**, 129001's M stays CRASHED: 15 of 16, with no stand-in drawn from seeds
>      9–16.
> 3. **Quarantine** (MUST 2).
>    - **Where the partial run lives.** Periodic snapshots of the partial run already sit on
>      `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M` (`stages.py` `_every` line 689, `_label`). The partial `run.log`
>      also sits there and in host1's unit directory.
>    - **Keep the branch (R12).** No session restores, checks out or reads it before the RBT-129 readout is complete.
>      After that, only the item-7 diagnosis may use it, and that diagnosis reads crash data only.
>    - **The M/N readout script refuses the label `rbt-129-stage1-c2-p030-U-G-129001-M` mechanically**, and a test
>      covers that refusal. Neither its files nor its branch enter any table, mean, figure or check.
>    - **Nothing about how far the unit got is reported**: no season, wall time, population, fauna or member.
> 4. **What the point's M arm feeds, and how n = 7 is handled** (MUST 1). To make "no verdict or BH tally turns on this
>    column" true, two scopes are **pinned now**:
>    - **(a) Share BH families hold only points where N ran.** The share WIN, TIE and CONTINGENT families (§7.1, line 870)
>      contain only those points. A NOT RUN point's y′ (§6.1, line 632; §5.3b) is printed descriptively and never
>      tested, so it never enters a BH ranking.
>    - **(b) RESOLVING is evaluated only where M and N both ran.** That is, the M-arm g0 at its 90% bounds (§6.2,
>      line 723). A NOT RUN point is never counted as RESOLVING: not in §8 (verdict 6's share route, line 978), not in
>      M4, and not in the §6.3 cross-tab.
>
>    With (a) and (b) pinned, this point's M arm feeds only descriptive outputs, each computed on the 7 completed seeds
>    with no imputation:
>
>    | output | ref | how the 7 seeds are used |
>    |---|---|---|
>    | the share change y′ (descriptive) | §5.3b, §6.1 | printed at n = 7 |
>    | the one-world performance column and the interference table (M minus S, per fauna) | §5.3a line 474, §5.3b line 483; M6 line 918 | **S paired on the same 7 seeds** (SHOULD 3) |
>    | the regime readout "on every S and M arm" | §5.3d, line 506 | M arm at n = 7 |
>    | M2's share model and the secondary share Wald T1 | §7.2, line 895; §7.3, line 926 | n = 7 at this point; both are descriptive at Stage 1 because they are not identifiable on one habitable point (NOTE 3) |
>    | verdict 4's denominator, "points with an M arm" | §8, line 971 | unchanged: the point still has an M arm; X-WIN needs N |
>
>    - **S at 129001 is untouched everywhere else**: income, survival, perception, levers, retention.
>    - **Sensitivity** (SHOULD 2). Where a logical bound exists, the readout prints the logical bounds of the 8-seed value
>      with the missing seed anywhere in its range. For y′ the range is [−s₀, 1 − s₀], where s₀ is 129001's holistic share
>      at season 59, read from S60 at readout time. It is labelled "bound under arbitrary missingness". It holds only under the readout's convention for a world that
>      empties before season 240; the readout plan states that convention, and if it sets the share outside [0, 1], the
>      bound is not printed. Income flow has no
>      such bound, and the readout says so. No min/max-of-7 substitute is printed.
> 5. **Future crashes** (MUST 5, SHOULD 7, SHOULD 9).
>    - **What counts as CRASHED.**
>      - It counts only if two attempts in a row of the same job fault **inside libmujoco**, at **the same instruction**,
>        by dmesg or by a faulthandler stack in `mj_step`.
>      - One of those two attempts must run at WORKERS=1.
>      - SIGKILL, OOM, or a fault in any other library is not CRASHED. It is retried under the runner's brief.
>    - **With one CRASHED unit already on record, any further CRASHED unit, at any point and in any arm** (M, N, or the
>      anchor fallback's M and N under T7), means:
>      - the coordinator stops issuing new lane files and restarts for M/N jobs;
>      - in-flight jobs finish;
>      - no unit is excluded, re-run or replaced until there is a new ruling;
>      - the M/N readout plan is not committed until that ruling has an adversary pass.
>
>      A second crash makes crashes a pattern. Their spread over points, faunas and seeds is then informative, and in
>      particular a second crash on 129001 implicates the census adoption first (NOTE 2).
>    - **Why an N-arm crash matters.** It is not a share call: none is reachable at Stage 1, because every N point is
>      PARTIAL, by §6.1 item 2 and the gate table. It matters because of K2's pooled stage check, which VOIDs the stage's
>      share layer (§5.5, line 567), and because of the pooled null variance (§6.1 item 6).
>    - **An S-arm crash** is outside this ruling. It stops the hive at once, because it touches the income layer and every
>      verdict.
> 6. **Physics pinned for the rest of RBT-129** (MUST 4).
>    - Every remaining RBT-129 launch must refuse any installed MuJoCo other than 3.14.0
>      (`importlib.metadata.version("mujoco")`). The unit's `platform.json` is the confirmation at readout time
>      (item 7). This applies to Stage 2, R-B, the retention arms and the anchor fallback.
>    - The refusal is added to the launch tool before the next RBT-129 launch, with its own adversary pass.
>    - `pyproject.toml`'s `mujoco>=3.1` stays as it is for other work.
> 7. **Diagnosis and the second host** (MUST 4, SHOULD 1).
>    - **Second host, before the readout plan is committed.** Run the job once on a second host, starting from `ckpt60`,
>      not from the quarantined branch. **Outside run-lane (R2-1):** call the job's ecology command directly with
>      `NO_DURABLE=1`, in a scratch directory outside `runs/`, so no save can reach any `ckpt/` branch. The run uses a
>      label of its own. Its stdout and stderr pass only through a filter that keeps the `Fatal Python error` block. If it
>      runs past the crash, stop it at 2 h. Either way, delete the scratch directory unread when it exits. A run that does
>      not crash is a re-rule trigger only, never a stand-in for the CRASHED seed (item 2). Keep only:
>      - the exit code;
>      - the dmesg instruction pointer, or the faulthandler frames, captured by a filter that prints only the
>        `Fatal Python error` block.
>      If it does not crash on the second host, the unit is re-ruled before the readout plan: physics is then
>      host-dependent, which is a sweep-wide integrity question.
>    - **Version provenance.** At readout, the integrity section confirms from every Stage-1 unit's `platform.json` that
>      each one ran MuJoCo 3.14.0. `platform.json` is provenance, not outcome. Any other version is re-ruled.
>    - **Mechanism.** The full diagnosis runs only **after the M/N readout plan is committed**, in a crash-only session.
>      It reports the mechanism only: no season, fauna, member, group composition or population figure. Its fix applies
>      to **later registrations only**, never to RBT-129.
>      - A first hypothesis: `Simulation.step` keeps stepping an exploded robot. If confirmed, whether non-finite states
>        occur without crashing in other M arms is an integrity question for a later registration (NOTE 6).

## 13. The fix round: where each item is answered (adversary `2601f81`; COORD-RULING-512)

| item | answer | where |
|---|---|---|
| MUST 1 | RESOLVING unpacks `(rows, passes)`; the replica is scaled by `pilot_constants.json` (1.5297), and the scale is printed; a test uses the real `power.resolvable` | §4.5; `resolving`, `scaled_resolvable` |
| MUST 2 | the full `readout` driver is committed, with an end-to-end synthetic-tree test; the readout session only runs it | §1; `readout`, `test_the_readout_runs_end_to_end_on_a_synthetic_tree` |
| MUST 3 | R3: the support rule, NOT TESTABLE, Holm at p = 1, and NO VERDICT | §6, §9; `world_model`, `map_holm`, `t1_state`, `verdicts` |
| MUST 4 | R1 and R2, with the non-registered readings printed as labelled lines | §4.3, §9; `verdicts` |
| MUST 5 | R4: eligibility ruled and labelled DATA-INFORMED; ranking on the income t; anchors excluded; the Stage-2 combination; core-h with "owner GO" | §7.2; `rb_select`, `rb_core_h`, `stage2_income_call` |
| SHOULD 1 | σ̂²_null and df per kind; the holistic-null pin | §4.2; `pooled_null`, `CONTINGENT_KIND` |
| SHOULD 2 | K2 at one run: the size bar decides | §5; `k2_per_point` |
| SHOULD 3 | the resume audit inside integrity, which fails on any double write except the listed signature; a §3.2 cross-check mismatch is a HELP | §2.3, §3.2; `double_writes`, `assemble_point` |
| SHOULD 4 | the C1 point mapping listed as O-23 | §7.1, §11 |
| SHOULD 5 | founding beside the census at every Stage-1 point | §8; `readout` |
| SHOULD 6 | the §12 scorecard, pinned | §8; `scorecard` |
| SHOULD 7 | the exclusions statement; an empty flow is a HELP | §3.2; `assemble_point` |
| SHOULD 8 | no bare fetch; narrow refspecs only; a local ref naming the unit refuses the run | §1, §2.5; `fetch_label`, `local_quarantine_refs` |
| SHOULD 9 | the gate check reads ckpt60 `history.json` alone; nothing is restored in integrity | §2.7; `gate_valid_from_history` |
| NOTE 1 | "settled by item 1 or 2", not "each is PARTIAL" | §0, §4.5 |
| NOTE 2 | s₀ from ckpt60, which is the S60 state | §4.6 |
| NOTE 3 | `last_score` is a cross-check, not a variant; exploded rows count as zero-income, with the count printed | §3.2, §3.6; `income_spread` |
| NOTE 4 | M g0 also under the census convention | §3.4; `assemble_point` |
| NOTE 5 | the CRASHED seed's N read is not skipped | `assemble_point` |
| NOTE 6 | label forms and symlinks refused | §2.5; `_is_quarantined_label`, `_is_quarantined_path` |
| NOTE 7 | `--go` must match a `GO-ID:` line in `RULINGS-CITED.md` | §1; `go_ids`, `main` |
| NOTE 8 | the test file name | §2.5 |
| NOTE 9 | an explicit narrow fetch before `written_twice` | §2.3; `double_writes` |
| NOTE 10 | "provisional" applies to Holm and §8, not to the coefficients | §6 |
| NOTE 11 | O-12's equivalence reading, to be ruled before Stage 2 | §5, §11 |
| NOTE 12 | L pairs refine only if fewer than 16 G pairs fire | §7.1 |
| NOTE 13 | O-1's ruling is relayed; the go should confirm it | `RULINGS-CITED.md` |
| NOTE 14 | n = 0 is a HELP | §4.1; `thresholds` |
| NOTE 15 | SATURATED points are not R-B-eligible | §7.2 |

### 13.1 The fix-check round (adversary `7e6e25b`, `f2bf66c`; the coordinator's instructions of 2026-10-02 21:07)

| item | answer | where |
|---|---|---|
| FC-MUST 1 (O-23) | the Stage-1 flanking-pair reading, as ruled: `c1_candidates` keeps only `ra_pairs()` midpoints (7); the no-pair branch is removed, and `ra_select` refuses a non-midpoint | §7.1, §11; test `test_c1_candidates_from_the_committed_census_readout` |
| FC-MUST 2 (coordinator ruling) | the `stage1-provenance/verdicts.json` input is removed entirely: no reader, no adapter exception, no echo into `integrity.txt` | §1, §2.6; `integrity`, `main` |
| coordinator item 3 | the extinct-pre-merge `ckpt60` has no `platform.json` by construction (fix1b), so it is verified by `EXTINCT.txt` and its marker; the expected count is re-derived; 2.6 prints the aggregate only; §2.2's count is not split | §2.2, §2.6; `check_platforms`; test with one EXTINCT unit |
| FC-SHOULD 1 | the driver prints the living-share variant, the N runs' y′ per run, M5, M6, the S lines (alive, births, deaths starved/aged, extinction), `mean_lifetime_score`, and food/work/path per member-season | §8; `s_summary`, `readout` |
| FC-SHOULD 2 | ruled K-SALT VOIDs are read from `KSALT-VOID:` lines | §1; `ruled_ksalt_void` |
| FC-SHOULD 3 | M7 skips n < 2 and prints the gaps; the MARGINAL aggregation is stated | §3.5, §6; `readout` |
| FC-NOTE 1 | an empty `GO-ID:` value never passes | `go_ids` |
| FC-NOTE 2 | a failed narrow fetch is a HELP, not a crash | `fetch_label` |
| FC-NOTE 3 | the share model's floor counts census g0 as a term (P + 3 at most). This is stricter than the income fit, and kept: it is descriptive only | §6 |
| FC-NOTE 4 | a collinear design is NOT TESTABLE as a whole under R3, as ruled; noted so the outcome is no surprise | §6 |
| FC-NOTE 5 | VARIANCE-DRIVEN and LEVER are wired to "not reachable" and "not evaluated" at Stage 1; the Stage-2 plan must wire them | §0 |
| FC-NOTE 6 | `c0-p030-U-L` in R4 (ii)'s anchor list is not a Stage-1 point; harmless, and kept as ruled | §7.2 |
| FC-NOTE 7 | the guard now refuses the label as a case-insensitive substring anywhere (`x-<label>`, `<label>0`) | §2.5; `_is_quarantined_label` |
| item 5 | `RBT129-S1-READOUT-GO-1` registered as `GO-ID-PENDING:`, which the script refuses until the coordinator's go commit renames it (FC2-SHOULD 1) | `RULINGS-CITED.md`; test `test_a_pending_go_id_is_refused` |
