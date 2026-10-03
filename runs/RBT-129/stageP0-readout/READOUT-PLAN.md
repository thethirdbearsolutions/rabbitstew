# RBT-129 Stage P (pilot) and Stage 0 (census): readout plan (pre-data)

*Written and committed before any Stage P or Stage 0 run output was opened. No `ckpt/rbt-129-stageP-*` or
`ckpt/rbt-129-stage0-*` branch had been restored or had its tarball read when this commit was pushed; the refs had
been fetched and only branch names were listed. The commit timestamp is the audit trail. Inputs read so far:
`DESIGN.md` §4.1, §5.1, §5.2 (the M/N gate), §6.1, §10.1, §11.1, §12 and its amendments; `power.py`, `power.txt`,
`prior_regime.py`; `launch/stages.py`; the lane files `lanes/P-0/*.jsonl` and `lanes/P-0/launch.txt`;
`scripts/regime.py`'s docstring; `rabbitstew/ecology.py`'s lineage, history and log formats (source, not output).*

Launch: `716e2d3`, lane fix at `02bf3b6` (fix1/fix1b: an S that is fully extinct at or before season 60 is
`EXTINCT.txt` in its unit record; its resume, M, N, K1 fork and K1 are skipped).

## 0. Order

1. `integrity.txt` (§1), then DUP-VERIFY (§2). **No readout number is computed before both are done.**
2. The pilot constants (§3), then `power_stageP.txt` (§4), then the §4.1 fallback statement (§5).
3. The census-layer calls (§6).
4. `READOUT-STAGEP0.md`.

Everything is computed by one script, `stageP0_readout.py`, from the restored directories; its output is
`stageP0_readout.txt`.

## 1. Integrity (`integrity.txt`)

- `stages.py check-branches` logic (`expected_branches` over the 20 lane files vs `git ls-remote`): every run
  directory and every pilot unit record has its `ckpt/rbt-129-*` branch. Missing ones are listed by name.
- Every done-marker expected for a job is present in its restored directory (`.rbt129-done-<tag>`), or the unit's
  `EXTINCT.txt` explains its absence.
- Checkpoint-restore quirk: a `ckpt60` directory that restores all-empty (every population empty in `state.json`) on a
  `716e2d3` unit means **extinct pre-merge**, not a lost checkpoint. Recorded as such.
- Quarantined and re-run census jobs (coordinator's log): host8 `0/c0-p010-PW-L/129002/S`; host9
  `0/c05-p010-PW-G/129003/S`, `0/c0-p010-HP-G/129002/S`; host0 `0/c05-p018-U-G/129003/S`. The quarantined originals
  were local-only on archived containers and are lost; the clean re-runs on the ckpt branches are the data. Listed.
- Pre-merge extinctions at `c2-p030-PW-G` seeds 129001, 129002, 129004 (checked against each unit's `EXTINCT.txt`).
- K1, per point: read in `check_branches`' registered order (the unit record's `K1.txt`; K1fork's done-marker note;
  a `-unit` branch's `K1.txt`; else recomputed with `k1_compare` on restored K1ref and K1fork). Where K1's seed
  (129001) is extinct pre-merge it is UNTESTABLE there, and any re-run on the lowest seed that reached season 60 is
  recorded with its host. A K1 FAIL makes the point VOID (§6.1) — printed, and flagged in every pilot number from it.
- The free K1-type control (§11.1 note): the pilot's `S60` at its 4 points × seeds 129001–129003 against the census's
  `0/<point>/<seed>/S` (same block, seed, streams), `k1_compare`. PASS/FAIL per pair, printed.

## 2. DUP-VERIFY (ruling 05:48)

Units: `P/c1-p030-PW-G/129002/M` (host4-lane1) and `P/c1-p030-U-L/129002/S` (host0-lane1), each resumed from
`state.json` after a mid-run double-write.

- A git worktree at `02bf3b6` in the scratchpad. The unit's `ckpt60` restored from its branch into it.
- The job is re-run with `stages.run_job` on its own lane line, with `dir` pointed at a scratch directory and
  `NO_DURABLE=1` (no branch is written), `WORKERS=2`: M = `fork` (`fork_config(ckpt60, dir, {"merge_after": 60,
  "pooled_capacity": 120})`, then `--resume --seasons 300`); S = `ckpt60` copied (`fork_config(ckpt60, dir, {})`, as
  the snapshot job did) then the `resume` job (`--resume --seasons 300`). Both run as harness background tasks.
- The saved run (restored from its branch) is compared with `k1_compare(saved, rerun)` (every output file byte for
  byte; config.json, platform.json, command.txt, logs and done-markers excluded).
- **IDENTICAL** if PASS. **REPLACED** on any difference: the clean re-run's directory is the unit's data for every
  number below, and the differing files are listed.

## 3. The pilot constants (only these may change, §4.1)

Pilot points: `c1-p030-U-L`, `c0-p030-U-L`, `c1-p030-PW-G`, `c2-p030-PW-G`; seeds 129001–129004; arms S (0–299),
M and N (forked at 60, to 299). Window 240–299.

**(a) Per-seed SD of the income difference.** Per S arm and fauna, the income flow = mean over the lineage rows with
`generation` in 240–299 of that fauna of `food − p · work` (p from the run's config; `last_score` is printed beside as
a cross-check, and any disagreement reported). Per seed x = flow_H − flow_D. A seed is valid at a point when both
faunas have rows in 240–299; an extinct-pre-merge unit or a seed with a fauna extinct before 240 is excluded and
counted. Per point: n, mean, SD (ddof 1). The constants for `power.py` part 1 are **the minimum and maximum per-point
SD over points with n ≥ 3** (they replace the registered floor 0.144 and ceiling 0.334), plus the **pooled SD**
√(Σ(nᵢ−1)sᵢ² / Σ(nᵢ−1)) over those points, printed as a third row.

**(b) Null y′ SD.** Per N arm: y′ = (mean over seasons 240–299 of alive(K-label) / 120) − (share at the merge,
nK / (nK + n_other) from the season-59 history counts of the two faunas, before the null replacement), K = the kept
fauna (holistic on odd seeds, designed on even). Alive counts from `history.json`. The registered constant is the SD
of y′ over all available N runs (ddof 1; the design's "12 null runs, df 11"; the actual count and df are printed).
The pooled per-kind SD with the kind offset removed (df = runs − 2) is printed beside, descriptive. Pre-merge-extinct
units have no N.

**(c) Real/replica ratio.** r = (b) / the replica's null y′ SD under the registered shuffle, taken as the mean of the
four `lottery … edge +0.00 tau 0.0` rows of `power.txt` §2 (g0 0.5–1.3), read from the file by the script.
The M arms' y′ (same definition, K = holistic) are printed descriptively beside; they do not enter r.

**(d) Cost per arm-season.** From each pilot arm's `run.log` per-season wall times (`(… s)` at the end of each season
line), × 2 cores (WORKERS = 2): per arm the mean core-s per season over its seasons (S: 60–299 of the resume; M, N:
60–299). Constants: the **median** over all pilot S, M and N arms (replaces the 20 core-s point) and the **maximum
per-point mean** (replaces the 25 core-s ceiling). Arms whose `command.txt` shows more than one invocation (resumed
after a restore) are excluded from (d) and counted.

## 4. The `power.py` re-run (`power_stageP.txt`)

`power.py` is changed only to take these constants: its literals 0.144/0.334 (part 1), 20/25 core-s (part 4) and a
y′ scale (1.0, applied as ȳ + r·(y′ − ȳ) to every replica cell in `_cell`) become module constants with those
defaults, set from `stageP0-readout/pilot_constants.json` when `--pilot FILE` is given. Registered output is
unchanged without the flag. Command:

    python3 runs/RBT-129/power.py 500 --pilot runs/RBT-129/stageP0-readout/pilot_constants.json > runs/RBT-129/stageP0-readout/power_stageP.txt

followed by the r3 part (`… 500 r3 --pilot …`, appended). Nothing else changes: grid, rules, thresholds, calls, reps.

**The Stage 1 number:** power at n = 8 of the income-layer t test at |H − D| = 0.4, BH-half threshold (α = q/2 = 0.05
two-sided), `power_t(0.4, sd, 8, 0.05)`, at the pooled SD (the point estimate; this decides §5), and at the min and
max per-point SD (printed beside).

## 5. The §4.1 fallback

It **triggers** if the power in §4 at the pooled SD is below 0.5. If it triggers, the readout says so and lists the
two registered options (n = 12; or fewer points, dropped in order: the 9 L points, then the c = 2 row of U) with the
§4 power at n = 12 printed beside. **The readout does not choose; the coordinator rules n.** If the min/max-SD rows
disagree with the pooled row about 0.5, that is stated.

## 6. Stage 0 census-layer calls (§5.1), from the 150 × 3 `0/<point>/<seed>/S` runs

- **FOUNDING-FAIL (C2)**, per fauna and point: a seed is extinct for a fauna when its alive count at season 59 before
  same-season refill (`alive − births` of that fauna's season-59 `history.json` entry) is 0, or the run stopped
  before season 59 with that fauna empty. FOUNDING-FAIL iff extinct on ≥ 2 of 3 seeds. Flagged provisional, as
  registered; never EXCLUDED.
- **Founder solvency**, per fauna and point (seeds pooled; per seed printed): founders = members present at season 0
  (lineage rows at generation 0 whose `born` is ≤ 0, i.e. not born in the run); a founder is solvent when its mean
  `food − p · work` over its rows in its first 12 seasons (seasons 0–11) is ≥ the run's living cost. Share solvent.
- **The regime early**: `scripts/regime.py RUN --windows 30-59`, per fauna and seed: window-local saturation (the
  registered "net income ÷ living cost" figure), viability, quintiles, deaths by age and starvation, eligible
  breeders, median energy. Printed per point (seeds' mean). This is the only habitability proxy at points never run
  at Stage 1, with its 60-season limit stated.
- **Census g0** (§5.2): mean `food − p · work` over all member-seasons 30–59, faunas and seeds pooled, + 0.35. Printed
  per point; it feeds the Stage-1 M/N gate, which the coordinator applies.
- **C1** (monotonicity): the census income difference = flow_H − flow_D over seasons 30–59, seeds pooled (member-
  seasons pooled across seeds). Along each price row (fixed c, L, s) and clutter row (fixed p, L, s), count sign
  changes; rows with > 1 are listed for R-A.
- **Side effects (R10)**: income flow, births, depth, saturation, solvency per point, printed against
  `c1-p030-U-L`. Descriptive.
- **C3** (rest on c = 2) and **PAYS**: not in the P-0 lanes. PAYS is read by #467/#487; C3 is reported NOT RUN.

## 7. Extinct, UNTESTABLE and quarantined units

- Extinct pre-merge pilot units: no M, N or K1; excluded from (a), (b) and (d) and counted. At the pilot they are a
  survival fact, printed.
- K1 UNTESTABLE at a unit: recorded; the point's K1 is read from the lowest seed that reached season 60 if a re-run
  exists, else the point is flagged "K1 not testable".
- A census fauna extinct at a seed enters FOUNDING-FAIL's count; its solvency uses the founders it had; its regime
  rows are empty and printed as such.
- Quarantined originals are lost and never used; only the clean re-runs are read.

## 8. Descriptive only

Per-point pilot means of H − D; M arms' y′ and one-world income; the kind-offset-removed null SD; the per-life regime
figures; `last_score`; census g0 and every side-effect row; the free K1-type control is a control, not an outcome.
No layer call (body, share, perception, retention) is made from Stage P (§4.1: "none").
