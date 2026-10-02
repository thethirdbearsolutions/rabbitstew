# RBT-129 Stage-1 MuJoCo provenance (crash ruling item 7)

**Verdict: 360/360 run branches (S, M, N, census S) are at MuJoCo 3.14.0, at the top level and in every resume.
None has mixed versions. 117 snapshot branches carry no `platform.json` and are flagged below: 45 `-ckpt60` and 72 `-ksalt`. From source, these are copies or comparisons that run no physics; see "Why 117 branches have no `platform.json`".
One expected M/N branch is not yet on the remote.**

Scan: 2026-10-02, from base `9edecbddb51119e483e277abaaffda743fbd1549`, using `check_platform.py` (this directory).
Output: `platform.tsv` (one row per branch).

## Method

- **Branch list.** `git ls-remote origin 'refs/heads/ckpt/rbt-129-stage*'`.
  - **Stage 1:** every `ckpt/rbt-129-stage1-*`, minus the 288 `-record` branches. No `-unit` branches exist.
    The quarantined `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M` is excluded by name before any fetch. It was never
    fetched, and the script asserts this.
  - **Census:** `ckpt/rbt-129-stage0-<point>-129001-S` for each of the 36 Stage-1 points. All 36 exist.
- **Per branch, one at a time:**
  - fetch it with `--depth=1` into a throwaway bare repository in the session scratchpad;
  - concatenate its `run.tar.gz.part*` blobs in sorted order, in memory, as `scripts/durable.sh restore` does;
  - delete the throwaway repository at once.

  No tarball was written to disk, and `MANIFEST` was not read.
- **Reading the tar.**
  - Python `tarfile` walks member **names** only, to find members that end in `platform.json`. No name is printed or stored.
  - `extractfile()` is called only on that member. If there are several, the shallowest one is read. In practice every
    branch had at most one, so the "multiple members" note never fired.
  - No other member was extracted, listed or printed.
- **Fields recorded** (from `rabbitstew/provenance.py`):
  - the top-level `mujoco`;
  - the `mujoco` of each `resumes[]` entry, comma-joined, empty when there were no resumes;
  - `numpy`;
  - `python`;
  - `git_sha` (the checkout sha).

  A branch whose tar has no `platform.json` member gets `MISSING` in the `mujoco` column and empty fields elsewhere.

## Counts

| class | branches | `platform.json` present | MuJoCo 3.14.0 (top and every resume) | not 3.14.0 | mixed across resumes |
|---|---|---|---|---|---|
| Stage-1 `-S` | 288 | 288 | 288 | 0 | 0 |
| Stage-1 `-M` (quarantined unit excluded) | 30 | 30 | 30 | 0 | 0 |
| Stage-1 `-N` | 6 | 6 | 6 | 0 | 0 |
| Stage-0 census `-129001-S` | 36 | 36 | 36 | 0 | 0 |
| **all runs** | **360** | **360** | **360** | **0** | **0** |
| Stage-1 `-ckpt60` snapshots | 288 | 243 | 243 | 0 | 0 |
| Stage-1 `-ksalt` | 72 | 0 | — | — | — |
| **total scanned** | **720** | **603** | **603** | **0** | **0** |

Resume counts per run, with every resume entry at 3.14.0:

| class | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| S | 45 | 100 | 123 | 18 | 2 |
| M | 0 | 15 | 10 | 4 | 1 |
| N | 0 | 1 | 4 | 1 | 0 |
| census S | 36 | 0 | 0 | 0 | 0 |

The 29 `-ckpt60` branches that have a resume entry also read 3.14.0.

## Flagged (reported, not interpreted)

### MuJoCo not exactly 3.14.0

None.

### Mixed versions across resumes

None for MuJoCo. Every resume entry's `mujoco` is also 3.14.0.

### Expected branch not yet present (running hosts)

The lane files `runs/RBT-129/lanes/1/*.jsonl` and `runs/RBT-129/lanes/1-MN/*.jsonl` yield 686 expected unit and snapshot
labels. All are present on the remote except:

- `ckpt/rbt-129-stage1-c2-p010-PW-G-129005-N` (`1-MN/host2-lane0.jsonl`). It was not scanned.

host2, host5 and host9 are still running, so their M/N branches may not be their final saves. The rows read here are
from each branch's head at scan time, and a top-up pass is needed when those hosts finish.

### `platform.json` missing — `-ckpt60` (45)

- `ckpt/rbt-129-stage1-c0-p080-PW-G-129002-ckpt60`
- `ckpt/rbt-129-stage1-c0-p080-PW-G-129004-ckpt60`
- `ckpt/rbt-129-stage1-c0-p080-PW-G-129007-ckpt60`
- `ckpt/rbt-129-stage1-c1-p030-PW-G-129001-ckpt60`
- `ckpt/rbt-129-stage1-c1-p030-PW-G-129007-ckpt60`
- `ckpt/rbt-129-stage1-c1-p030-PW-G-129008-ckpt60`
- `ckpt/rbt-129-stage1-c1-p030-PW-L-129002-ckpt60`
- `ckpt/rbt-129-stage1-c1-p030-PW-L-129003-ckpt60`
- `ckpt/rbt-129-stage1-c1-p030-PW-L-129004-ckpt60`
- `ckpt/rbt-129-stage1-c1-p030-PW-L-129006-ckpt60`
- `ckpt/rbt-129-stage1-c1-p030-PW-L-129007-ckpt60`
- `ckpt/rbt-129-stage1-c1-p030-PW-L-129008-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-G-129001-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-G-129002-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-G-129003-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-G-129004-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-G-129006-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-G-129007-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-G-129008-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-L-129001-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-L-129002-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-L-129003-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-L-129004-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-L-129005-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-L-129006-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-L-129007-ckpt60`
- `ckpt/rbt-129-stage1-c1-p080-PW-L-129008-ckpt60`
- `ckpt/rbt-129-stage1-c2-p010-PW-G-129001-ckpt60`
- `ckpt/rbt-129-stage1-c2-p010-PW-G-129006-ckpt60`
- `ckpt/rbt-129-stage1-c2-p030-PW-G-129001-ckpt60`
- `ckpt/rbt-129-stage1-c2-p030-PW-G-129002-ckpt60`
- `ckpt/rbt-129-stage1-c2-p030-PW-G-129003-ckpt60`
- `ckpt/rbt-129-stage1-c2-p030-PW-G-129004-ckpt60`
- `ckpt/rbt-129-stage1-c2-p030-PW-G-129006-ckpt60`
- `ckpt/rbt-129-stage1-c2-p030-PW-G-129007-ckpt60`
- `ckpt/rbt-129-stage1-c2-p030-PW-G-129008-ckpt60`
- `ckpt/rbt-129-stage1-c2-p080-HP-G-129003-ckpt60`
- `ckpt/rbt-129-stage1-c2-p080-PW-G-129001-ckpt60`
- `ckpt/rbt-129-stage1-c2-p080-PW-G-129002-ckpt60`
- `ckpt/rbt-129-stage1-c2-p080-PW-G-129003-ckpt60`
- `ckpt/rbt-129-stage1-c2-p080-PW-G-129004-ckpt60`
- `ckpt/rbt-129-stage1-c2-p080-PW-G-129005-ckpt60`
- `ckpt/rbt-129-stage1-c2-p080-PW-G-129006-ckpt60`
- `ckpt/rbt-129-stage1-c2-p080-PW-G-129007-ckpt60`
- `ckpt/rbt-129-stage1-c2-p080-PW-G-129008-ckpt60`

### `platform.json` missing — `-ksalt` (72: every `-ksalt` branch)

- `ckpt/rbt-129-stage1-c0-p010-HP-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c0-p010-HP-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c0-p010-PW-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c0-p010-PW-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c0-p010-U-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c0-p010-U-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c0-p030-HP-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c0-p030-HP-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c0-p030-PW-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c0-p030-PW-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c0-p030-U-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c0-p030-U-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c0-p080-HP-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c0-p080-HP-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c0-p080-PW-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c0-p080-PW-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c0-p080-U-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c0-p080-U-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p010-HP-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p010-HP-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p010-HP-L-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p010-HP-L-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p010-PW-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p010-PW-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p010-PW-L-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p010-PW-L-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p010-U-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p010-U-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p010-U-L-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p010-U-L-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p030-HP-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p030-HP-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p030-HP-L-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p030-HP-L-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p030-PW-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p030-PW-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p030-PW-L-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p030-PW-L-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p030-U-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p030-U-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p030-U-L-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p030-U-L-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p080-HP-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p080-HP-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p080-HP-L-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p080-HP-L-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p080-PW-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p080-PW-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p080-PW-L-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p080-PW-L-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p080-U-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p080-U-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c1-p080-U-L-129002-ksalt`
- `ckpt/rbt-129-stage1-c1-p080-U-L-129003-ksalt`
- `ckpt/rbt-129-stage1-c2-p010-HP-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c2-p010-HP-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c2-p010-PW-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c2-p010-PW-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c2-p010-U-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c2-p010-U-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c2-p030-HP-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c2-p030-HP-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c2-p030-PW-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c2-p030-PW-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c2-p030-U-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c2-p030-U-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c2-p080-HP-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c2-p080-HP-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c2-p080-PW-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c2-p080-PW-G-129003-ksalt`
- `ckpt/rbt-129-stage1-c2-p080-U-G-129002-ksalt`
- `ckpt/rbt-129-stage1-c2-p080-U-G-129003-ksalt`

## Why 117 branches have no `platform.json` (from source)

This section is derived from source only: `runs/RBT-129/launch/stages.py` and `rabbitstew/provenance.py`. The
cross-checks below use only the `platform.json` fields already in `platform.tsv`. No other file was read from any branch.

> **No-peek note.** The code path that explains the 45 is the *pre-merge extinction* skip. So "45 `-ckpt60` branches
> without `platform.json`" is, by the code, a count of Stage-1 units whose S60 ended with every population empty. That
> is an outcome figure (DESIGN M2: survival call). It follows from the branch names already listed above, which carry
> the per-unit identity. I state it because the coordinator asked for the number to be explained. Nothing was read to
> establish extinction beyond the `platform.json` fields; the identification rests on the code and the cross-check below.

**Who writes `platform.json`.** Only the ecology process writes it:
- `write_platform` on a fresh run, `rabbitstew/ecology.py:425`;
- `record_resume`, which appends to `resumes[]`, on every `--resume`, `rabbitstew/ecology.py:966`.

No job in `stages.py` writes it directly. A directory that never runs `rabbitstew.cli ecology` has a `platform.json`
only if it was copied from one that did. The copy is `fork_config`, a `shutil.copytree`.

**`-ksalt` (72): a comparison, never physics.**
- `founding_job` (`kind == "ksalt"`) does `os.makedirs(d)` and writes only `KSALT.txt`.
- That file is `half_compare` of the chain's `S` directory (seasons 0–59) against the census `stage0/<point>/<seed>/S`.
- There is no ecology call and no copy.

`stage1_units` emits a K-SALT job only for a fresh S60 on a census seed with `s >= 1, t = 0`. Seed 129001 at (0, 0) is
adopted instead, so only 129002 and 129003 qualify: 36 points × 2 seeds = 72, which equals the count found.

The runs it compares are both covered:
- **its `src`:** the chain's S branch, whose S60 top-level record is in the 288 S rows;
- **its `ref`:** the stage0 census runs for 129002 and 129003. Those were not in this scan's scope (only stage0 129001
  was asked for); see "Scope gap" below.

**`-ckpt60` (288 = 36 × 8): a copy, never physics.** The `snapshot` job in `run_job` takes one of two paths:
1. **Live at the merge season.**
   - It calls `fork_config(S, ckpt60, {})`, which copies the whole S directory at season 60, `platform.json` included.
   - No ecology runs, so no resume is appended.
   - That is why 259 of the 288 `-ckpt60` rows have no `resumes`. The other 29 carry the resumes S had made before season 60.
   - **Cross-check:** for all 243 present `-ckpt60` records, the top-level `mujoco`, `numpy`, `python` and `sha` equal
     their S branch's top level.
2. **Every population empty at or before season 60.**
   - It writes `EXTINCT.txt` and `UNIT.txt` into the unit record and calls `_mark(ckpt60, ...)`.
   - `_mark` does `os.makedirs` and writes only the `.rbt129-done-ckpt60` marker; then `_save(ckpt60)`.
   - There is no `fork_config`, so the branch holds a marker and no `platform.json`.

   This is the only path in `run_job` that produces a `ckpt60` branch without `platform.json`. The S resume of such a
   unit is also skipped: `run_job`'s `extinct_season(...)` branch marks it done without running ecology. So that S's
   `platform.json` has no `resumes`.

   **Cross-check (platform fields only):** the 45 `-ckpt60` branches missing `platform.json` are **exactly** the 45
   Stage-1 `-S` branches whose `resumes` list is empty, as a set equality on unit labels. So 45 is not a code-path
   constant such as "36 adopted + k". It is the number of units that took path 2. Adoption, the 129001 `adopt` job,
   creates the S directory, not ckpt60. An adopted unit's ckpt60 goes through the same two paths as any other unit.

**Which physics each derived branch inherits, and whether it is covered.**

| derived branch | inherits physics of | that run's `platform.json` in the 360? |
|---|---|---|
| `-ckpt60` (live) | its unit's S60, which is the S branch's top-level record (or, for 129001, the census) | yes: all 243 match their S top level |
| `-ckpt60` (extinct) | nothing; no state is copied | n/a. The unit's only physics is S60, which is covered by its S row (all 45 present, at 3.14.0) |
| `-ksalt` | nothing; it compares S 0–59 with the census | S: yes. Census 129002/129003: not scanned (scope gap) |
| `-M`, `-N` | ckpt60's copy of S60 (top level), plus their own resumes | yes: all 36 M/N top-level records equal their ckpt60's, and each resume entry is the arm's own physics at 3.14.0 |
| 129001 `-S` (adopted, F7) | `adopt_census` → `fork_config(stage0/<point>/129001/S, ...)`, then its own resumes | yes: all 36 129001 S top-level records equal their `ckpt/rbt-129-stage0-<point>-129001-S` row (sha `02bf3b64f3795bd232c835bba6b011e9b8f98b49`), all at 3.14.0 |

**Every physics-running directory in scope has a `platform.json`.** This covers every Stage-1 S, M and N branch scanned,
and every stage0 129001 census S. None lacks one.

**Scope gap (not a finding).** The K-SALT reference runs, stage0 129002 and 129003 S at the 36 points, were not part of
this scan. They are census runs, not Stage-1 physics; the Stage-1 S for those seeds is a fresh run with its own record.
If the coordinator wants them, they can be added to the top-up pass under the same platform-only rule.

## Version histograms (603 records that have `platform.json`)

Values are counted over top-level records. Every resume entry's `mujoco` is also 3.14.0.

| field | value | count |
|---|---|---|
| mujoco | 3.14.0 | 603 |
| numpy | 2.4.6 | 603 |
| python | 3.11.15 | 603 |

Checkout `git_sha` (top level; provenance only):

| sha | S | M | N | ckpt60 | census S |
|---|---|---|---|---|---|
| `830450efe3555b084bc70a86fcfa688b5ecb974b` | 252 | 25 | 4 | 213 | 0 |
| `02bf3b64f3795bd232c835bba6b011e9b8f98b49` | 36 | 5 | 2 | 30 | 36 |

## Reproduce

```
python3 runs/RBT-129/stage1-provenance/check_platform.py <scratch-dir> runs/RBT-129/stage1-provenance/platform.tsv
```
