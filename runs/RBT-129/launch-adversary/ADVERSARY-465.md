# RBT-129 launcher adversary: PR #465 (`results/RBT-129-launcher2` at `2f3c2dd`)

**Verdict: MERGE AFTER FIXES.** There are two MUST items:
- **M-1:** #465 cannot give any unit Stage P has actually run a status or a record. So the probe emit and
  `check-branches` cannot pass on Stage P as it stands.
- **M-2:** a save that hangs holds the machine-wide lock forever.

Everything else checked holds:
- the probe order and the EXTINCT skip;
- the serialized, logged save;
- the K1 marker on both paths;
- `check-branches`' enumeration;
- the calibration lane's no-peek, its SD recovery, cells and τ, and its pins;
- the untouched running trees.

**The evidence**, all in this directory:
- `probe_465.txt`: sections (A) to (E), with the drivers inlined;
- `mutants465.py` → `mutants465.txt`;
- `suite_465.txt`.

**The trees.**
- **The trial merge:** `2f3c2dd` onto `claude/new-session-4cao7d` (`fd74755`) gives `b25a1e4`.
  - It is not a fast-forward, because #465 predates #464's merge.
  - It merges cleanly, and the only extra file is #464's §12 amendment.
- **Where RBT-132's tools were needed**, the checks ran on that merge plus #459's head `3e59928`.

**No-peek.** No sweep arm, cell, member or planted line ran. `durable.sh` was a local stub in (C). The one remote read
was `git ls-remote` of `ckpt/rbt-129-*` branch names.

## 1. Probe order (i), and the EXTINCT skip (iv)

**The order is right.**
- `probe_jobs` emits each point's `planted` line before that point's probe lines.
- Each line is `_guarded`. A failed planted set exits the runner (`exit 1`) before any probe reads its missing
  `battery.json`.
- Mutant E3, which puts the planted line after the probes, is killed.

**The skip matches DESIGN M2** ("report, never probe"):
- a unit with `EXTINCT.txt` gets no probe line at either season;
- it is listed in `lanes/probes/extinct.txt`;
- its S is not restored;
- `probe_members.py` also writes EXTINCT itself if a unit is emitted anyway.

Mutants E1 (probe it anyway) and E2 (treat an unknown status as alive) are both killed.

**The exit-7 refusal is right as a guard**: never guess a unit's status. **Its remedy, however, cannot be reached for
Stage P's actual units (M-1).**

### MUST M-1: the units Stage P has run have no record, and #465 has no way to make one

Stage P runs `7f8bfea`'s `run_job`, and `7f8bfea` writes no `record/` or `UNIT.txt`. It also never saves an extinct
unit's evidence: `EXTINCT.txt`, the `skipped` ckpt60 marker and `K1.txt` stay in the container. For such units
(`probe_465.txt` (B)):

| where | alive unit | extinct unit |
|---|---|---|
| the Stage P machine that ran it (B1) | `alive` (local ckpt60 marker) | `extinct` (local `EXTINCT.txt`) |
| any other machine (B2) | **None → exit 7** | **None → exit 7** |
| another machine, with ckpt60 restored by hand | `alive` | **None**: nothing of it was ever saved |

**Nothing in #465 fixes the None:**
- `unit_status` restores only the (non-existent) record branch, never ckpt60's.
- **`check-branches --save` on the Stage P machine** saves every run directory that exists. But `record/` does not
  exist there, so both records stay `MISSING … not on this machine`, with exit 1 (B3).
- **A lane re-walked by #465's `run_job`** returns at each done-marker before any `unit_file`, so still no record
  (B4).
- **On the remote now**, 419 of the 542 branches `check-branches` expects for P/0 exist, and **0 of the 16 unit
  records** (E).

**The consequences:**
- Probes can be emitted only on a machine that holds all 16 units locally, and Stage P's units are spread over its
  hosts.
- `check-branches` can never pass on the P/0 lanes.
- An extinct unit's status dies with its container.

**The fix:** small, and needed before Stage P's containers go.
1. **`check-branches --save` backfills a missing record from what is on the machine.** For each pilot unit whose
   `record/` is missing, it writes the record from:
   - the unit's `EXTINCT.txt` and `K1.txt`;
   - a `UNIT.txt` derived from the ckpt60 done-marker: `skipped: extinct pre-merge at season N`, or a plain marker
     meaning alive.

   It then saves the record. The ckpt60 directories are run directories, so the same pass saves them too.
2. **`unit_status` falls back to ckpt60's marker**, restored from its branch. The marker is written in the same save
   as the skip decision, so it is authoritative for new-code units as well (see S-3).
3. **Make it runnable from a Stage P session.** Those sessions are pinned at `7f8bfea`. #465's `stages.py` in another
   checkout resolves the lane files' relative paths against its own root, where the unit directories are not. Add a
   `--repo DIR` (the checkout holding the runs), or write down the exact procedure.
4. Then run it in every Stage P session, now.

## 2. Durability

**Serialized: yes, across threads, processes and the periodic loop.**
- Every save takes `flock` on `/tmp/rbt129-durable.lock`. That includes the lanes' background `_save`, the periodic
  `_every` and the leg scripts' `stages.py save`.
- Evidence (C1): two lane-like processes, each with 3 background saves and 1 foreground save, plus a periodic loop,
  all at once. **At most 1 save ran at a time.**
- Mutants S1 (no lock), S2 (no retry), S3 (the Stage P failure: back to `/dev/null`) and S4 (periodic outside the
  lock) are all killed.
- The log carries each exit code and durable.sh's output. A failure warns with the label and exit code only.

### MUST M-2: no timeout, so one hung push stops every save on the machine

`save_now` runs `durable.sh save` with no `timeout=` while it holds the lock, and durable.sh's `git push` has none
either. A push that never returns (this session's own pushes hung today) holds the lock forever. Then:
- **Every other save on the machine waits.** A leg script's synchronous `stages.py save` blocks its runner; that
  covers the probes, pays and calibration runners.
- **The lane process cannot exit.** Its non-daemon save thread keeps it alive.

(C2), with the hang shortened to 8 s: the lane printed "main done" at +0.4 s but exited at +8.4 s, and a leg's
`stages.py save` returned only after 8.2 s.

**The fix:** `subprocess.run(..., timeout=900)`. On `TimeoutExpired`, kill the process group, log `exit timeout`,
and retry or warn as for any failure. The lock is then held for at most about 15 min per attempt.

**SHOULD S-2: the periodic thread is a daemon.**
- If the process exits during a periodic save (an ecology failure raises `SystemExit`; or the lane's last save wins
  the lock race), the thread dies but its `durable.sh` runs on. It then holds no lock, and its outcome is never
  logged.
- (C3): lock free right after exit, durable.sh still running, and 0 log lines. The save ended 2.8 s after the process
  exited. The same thing shows in (C1): 9 saves, 8 logged.
- **Fix:** make it non-daemon. Once `stop` is set, it ends after the save it is in.

**Reclaim mid-save.** Each branch update is one force-push of one ref: it lands whole or not at all, and the previous
snapshot stays. `flock` dies with the container. So a reclaim loses only saves not yet made, and a restored run
without its marker resumes or redoes. There is one exception:

**SHOULD S-3: the skip decision and its record go to two branches in unordered background saves.**
- The snapshot job's extinct path queues `_save(record)` twice, then `_mark(ckpt60)` and `_save(ckpt60)`. The lock
  gives no order.
- A reclaim after ckpt60's save and before the record's leaves a restored ckpt60 marked `skipped` and no
  `EXTINCT.txt`.
- The unit's resume, M, N and K1 then do not know it is extinct:
  - the resume runs on an emptied S;
  - M's fork copies a ckpt60 without `state.json`, and the lane dies (loudly).
- **Fix:** M-1's second part (status from the ckpt60 marker) closes this for status. Also put K1's verdict line in its
  done-marker's note (`_mark(d, "K1", "K1 PASS …")`), so it rides K1fork's own branch.

**The `<unit>/record/` mirror** is correct and idempotent for new-code units.
- `unit_file` writes the same text to the unit and to `record/`, then saves.
- `restore_record` restores only a missing `record/`, and copies back only files that are missing, never
  overwriting.
- A second walk of the lane re-runs and re-saves nothing (the PR's test).
- Mutant S5 (the record is not saved) is killed.

**The K1 marker is set on both paths.**
- On the verdict path, `unit_file(K1.txt)`, then `_mark(K1fork, "K1")` and `_save`.
- On the UNTESTABLE path, the same, with a `skipped` note.
- Mutants K1a and K1b (no marker on each path) are both killed.

**`check-branches` enumerates exactly.** On the committed P/0 lane files (E):
- 20 lanes, 546 jobs, 526 distinct run directories and 16 pilot units (4 points × 4 seeds);
- **542 expected = the run directories + the 16 records**;
- labels are unique per directory, and a `k1` job's directory is its K1fork's.

Mutants B1 (no records expected), B2 (always exit 0) and B3 (no re-check after `--save`) are all killed.

## 3. The calibration lane (DESIGN §12, #464)

**No-peek holds.**
- Each planted job's stdout and stderr go to files in its cell directory.
- The runner's stdout is only `calib-extract`'s lines. For each (a) and (c) plant, those are SEEN, then stage 2's and
  the confirmation's ΔT mean, SD and n, then the SEEN share per kind.
- A failed cell prints only `FAILED: <dir> (exit N)`.
- **Every leak mutant is killed:**
  - C1: stage-2 F as an unlabelled column;
  - C2: F in place of n;
  - C3: the call as a digit;
  - C4: the runner also prints `planted.txt`;
  - G1: a guarded job's stdout reaches the runner.
- K3's pass or fail can be read off the printed SEEN shares. That is inherent in the ruling, which reports each
  plant's SEEN.

**The SD recovery is exact.**
- `battery_stats` sets `lbdT = lower_bound(dT)`, which is `mean − t(0.95, n−1)·sd/√n`, over paired draws.
  `n = len(intact)`, and `_pairs` drops a refused draw from both conditions.
- So `sd = (dT − lbdT)·√n / t(0.95, n−1)`, using the same `t_quantile` from the pinned `steer.py`, is exact to
  rounding.
- It is 0 when the spread is 0 (the bound is then the mean), and `nan` when n < 2.
- The PR's test recovers `np.std(ddof=1)`. Mutant C5 (df = n) is killed.

**Cells and τ match #464.**
- `CALIB_CELLS` is (`c0-p030-PW-G`, `c0-p030-HP-G`). Mutant C7 (HP-L) is killed.
- Both cells' configs carry `smell_tau` 2.0 = `steer.registered_tau`, with G 2.5 and `fairness` fair (A).
- `planters.py planted` asserts the registered channel itself.

**Pins, and the refusal until #459.**
- The pins are `steer.py`, `planters.py` and RBT-97's four files, recorded in `lanes/calibrate/launch.txt` and
  re-checked in `runner.sh` (exit 6).
- `tool_pins` refuses with exit 6 while `planters.py` is absent: `STEER_TOOLS` pins it, and it is not on
  `fd74755`/`b25a1e4`.
- On the merge with #459, `calibrate` emits, and `verify` passes (A).

**SHOULD S-4: `verify` does not cover the file the calibration, probe and pays templates read.**
- `calib_jobs`, and the RBT132.md templates through `{config_json}`, read `worlds/<id>.config.json`.
- `verify` rebuilds only `worlds/config/<id>/config.json`: the legs' L-1 again.
- On `b25a1e4` + #459, committed edits to that file are **accepted by `verify` (exit 0)**: motor budget 3.0,
  `smell_tau` 1.0, and a removed `fairness` marker. The same edit to the verified file gives exit 4.
- **This is not a hole today.** `planters.py` and `probe_members.py` call the pinned `steer.py`'s
  `assert_point_world`, whose `POINT_SIM_HASH` covers all 24 launcher cells. It equals the verified file's hash, and
  it refuses every edit tried (A2, A3).
- **Fix:** have `verify_leg` compare `worlds/<id>.config.json` too, or pass `worlds/config/<id>`. `planters.py` takes
  a directory.

## 4. Pins, and the running trees

- `PRIZE_TOOLS` and `STEP_TOOLS` now take RBT-97's `mechanism.py` and `resign_rbt67.py`, through `RBT97_CHAIN`.
- **#465 changes only** `LEGS.md`, `runs/RBT-129/launch/stages.py` and `tests/test_rbt129_launch.py`. It touches no
  `lanes/` file, and neither `rabbitstew/` nor `scripts/`.
- The running legs (at `29ab80b`) and P/0 (at `7f8bfea`) pin their own launch trees and are unaffected. As before,
  neither may be restarted on integration's head once this merges (exit 5).

**SHOULD S-5: one link of RBT-97's chain is unpinned.** `mechanism.py` also loads
`docs/artifacts/RBT-67/compass_dose_response.py`. That file is outside every pinned tree and tool list. Add it to
`RBT97_CHAIN`. (`scripts/compass_*.py` are covered by the pinned `scripts/` tree.)

## 5. Tests

| check | result |
|---|---|
| full suite, trial merge `b25a1e4`, clean `.[dev]` venv, no scipy | **720 passed, 2 skipped**, 16 warnings (13 min 42 s). The skips: scipy (`test_rbt125_harness.py:170`), and `test_seen_is_planters_seen` (`planters.py` not on the tree until #459) |
| launcher tests on `b25a1e4` + #459 | **47 passed**; `_seen` equals the real `planters.seen` |
| mutants (`mutants465.txt`) | **21 of 22 killed** on `b25a1e4`. The survivor, C6 (SEEN without the confirmation), is killed on `b25a1e4` + #459 by `test_seen_is_planters_seen` |

## The list

**MUST**
- **M-1:**
  - backfill unit records from local evidence (`check-branches --save`);
  - have `unit_status` fall back to ckpt60's marker from its branch;
  - make the command runnable from a Stage P session (`--repo`);
  - run it in every Stage P session before those containers go.
- **M-2:** a timeout on `save_now`'s `durable.sh` (kill, log, retry or warn), so no hung push holds the machine-wide
  lock.

**SHOULD**
- **S-2:** make the periodic save thread non-daemon.
- **S-3:** derive the extinct status from the ckpt60 marker (with M-1), and carry K1's verdict in its done-marker.
- **S-4:** `verify` covers `worlds/<id>.config.json`, or the templates read `worlds/config/<id>`.
- **S-5:** pin `docs/artifacts/RBT-67/compass_dose_response.py` in `RBT97_CHAIN`.

**NIT**
- **N-1:** write `durable.log` while still holding the lock. Today, appends from several processes can interleave.
- **N-2:** add a stage-2-passes, confirmation-fails case to `test_calib_extract_prints_only_seen_and_dt`, so that C6
  is killed before #459 too.
- **N-3:** once #459 is in, have `calib-extract` import the pinned `planters.seen` rather than restate it.

---
_Generated by [Claude Code](https://claude.ai/code)_
