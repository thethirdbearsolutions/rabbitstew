# RBT-129 Stage-1 MuJoCo provenance (crash ruling item 7)

**Verdict: 360/360 run branches (S, M, N, census S) are at MuJoCo 3.14.0, at the top level and in every resume.
None has mixed versions. 117 snapshot branches carry no `platform.json` and are flagged below: 45 `-ckpt60` and 72 `-ksalt`.
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
