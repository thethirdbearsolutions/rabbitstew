# RBT-129 Stage-1 MuJoCo provenance (crash ruling item 7)

**Verdict: every directory in scope that runs physics has a `platform.json`, and every one is at MuJoCo 3.14.0.**
- **Runs covered:** 360 of 360, namely 288 S, 30 M (quarantined unit excluded), 6 N and 36 census S.
- **Resumes:** every resume entry is also at 3.14.0, and no run has mixed versions.
- **Not yet on the remote:** one expected M/N branch; see "Running hosts".

Scan date 2026-10-02, from base `9edecbddb51119e483e277abaaffda743fbd1549`. Script: `check_platform.py` in this
directory. Public table: `platform.tsv`.

> An earlier revision of this PR was withdrawn for no-peek reasons. Under the coordinator's ruling, the per-branch list
> of `-ckpt60` snapshot branches without `platform.json`, and its explanation, are **sealed for the readout's integrity
> section**. They are not in this PR, and the readout re-derives them at integrity.

## Method

- **Branch list.** `git ls-remote origin 'refs/heads/ckpt/rbt-129-stage*'`.
  - **Stage 1:** every `ckpt/rbt-129-stage1-*`, minus the `-record` branches. No `-unit` branches exist.
  - **Quarantine:** `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M` is excluded by name before any fetch. It was never
    fetched, and the script asserts this.
  - **Census:** `ckpt/rbt-129-stage0-<point>-129001-S` for each of the 36 Stage-1 points. All 36 exist.
- **Per branch, one at a time:**
  - fetch it with `--depth=1` into a throwaway bare repository in the session scratchpad;
  - concatenate its `run.tar.gz.part*` blobs in sorted order, in memory, as `scripts/durable.sh restore` does;
  - delete the throwaway repository at once.

  No tarball was written to disk, and `MANIFEST` was not read.
- **Reading the tar.**
  - Python `tarfile` walks member **names** only, to find a member ending in `platform.json`. No name is printed or stored.
  - `extractfile()` is called on that member only; the shallowest is taken if there are several. No other member was
    extracted, listed or printed.
- **Fields recorded:** the top-level `mujoco`, `numpy`, `python` and `git_sha`.
- **The `resumes_mujoco` column** reads `all 3.14.0` when every `resumes[]` entry's `mujoco` is 3.14.0, vacuously
  when there is none. Otherwise it lists the offending versions. The per-run number of resumes is not published.
- **What `platform.tsv` contains:**
  - the 360 runs;
  - the 72 `-ksalt` branches, marked `MISSING`.

  It has no `-ckpt60` rows. Those branches are copies whose top level is checked against their S below; their
  per-branch table is sealed.

## Counts (runs: every directory that runs physics)

| class | branches | `platform.json` present | MuJoCo 3.14.0 (top and every resume) | not 3.14.0 | mixed across resumes |
|---|---|---|---|---|---|
| Stage-1 `-S` | 288 | 288 | 288 | 0 | 0 |
| Stage-1 `-M` (quarantined unit excluded) | 30 | 30 | 30 | 0 | 0 |
| Stage-1 `-N` | 6 | 6 | 6 | 0 | 0 |
| Stage-0 census `-129001-S` | 36 | 36 | 36 | 0 | 0 |
| **all runs** | **360** | **360** | **360** | **0** | **0** |

## Directories that run no physics

Only the ecology process writes `platform.json`:
- `write_platform` on a fresh run, `rabbitstew/ecology.py:425`;
- `record_resume`, which appends to `resumes[]`, on each `--resume`, `rabbitstew/ecology.py:966`.

No job in `runs/RBT-129/launch/stages.py` writes it directly, so a directory that never runs ecology has one only if it
was copied from one that did. The copy is `fork_config`, a `shutil.copytree`. Two kinds of Stage-1 branch are made by
jobs that never run ecology:

- **`-ksalt` (72, design-determined; none has `platform.json`).**
  - `founding_job` (`kind == "ksalt"`) creates the directory and writes only `KSALT.txt`.
  - That file is `half_compare` of the chain's own S, seasons 0–59, against the census `stage0/<point>/<seed>/S`.
  - `stage1_units` emits the job only for a fresh S60 on census seeds 129002 and 129003 with `s >= 1, t = 0`, which
    gives 36 × 2.
  - Physics compared: the chain's S, which is covered in the 360, and the stage0 129002/129003 census runs, which are
    scheduled for the top-up pass.
- **`-ckpt60` (288 = 36 points × 8 seeds; some have no `platform.json`).**
  - The `snapshot` job in `run_job` never runs ecology.
  - Where it copies, `fork_config` copies the unit's S directory, `platform.json` included.
  - Every `-ckpt60` record present has the same top-level `mujoco`, `numpy`, `python` and `sha` as its S branch,
    which is covered in the 360. No `-ckpt60` record holds any version other than 3.14.0.
  - Which `-ckpt60` branches lack the file, and why, is sealed (see the note at the top).

**Inherited physics is covered.**
- **M/N:** each M and N top-level record equals its `-ckpt60`'s, which is S's season-60 record. Their resume entries
  are their own physics, all at 3.14.0.
- **Adopted 129001 S (F7, `adopt_census` → `fork_config`):** each top-level record equals its
  `ckpt/rbt-129-stage0-<point>-129001-S` row, sha `02bf3b64f3795bd232c835bba6b011e9b8f98b49`, at 3.14.0.

## Running hosts

The lane files `runs/RBT-129/lanes/1/*.jsonl` and `runs/RBT-129/lanes/1-MN/*.jsonl` name the expected unit and snapshot
labels. All are on the remote except:

- `ckpt/rbt-129-stage1-c2-p010-PW-G-129005-N` (`1-MN/host2-lane0.jsonl`). It was not scanned.

host2 and host5 are still running, so their M/N branches may not be their final saves. The rows here are each branch's
head at scan time. A top-up pass follows when those hosts are DONE. It will also add the stage0 129002 and 129003 census
runs, which are the K-SALT references.

## Version histograms (360 runs)

| field | value | count |
|---|---|---|
| mujoco (top level and every resume entry) | 3.14.0 | 360 |
| numpy | 2.4.6 | 360 |
| python | 3.11.15 | 360 |

Checkout `git_sha` (top level; provenance only):

| sha | S | M | N | census S |
|---|---|---|---|---|
| `830450efe3555b084bc70a86fcfa688b5ecb974b` | 252 | 25 | 4 | 0 |
| `02bf3b64f3795bd232c835bba6b011e9b8f98b49` | 36 | 5 | 2 | 36 |

## Reproduce

```
python3 runs/RBT-129/stage1-provenance/check_platform.py <scratch-dir> <RAW_TSV outside the repo> runs/RBT-129/stage1-provenance/platform.tsv
```

The raw table is sealed. The script refuses to write it inside the repository.
