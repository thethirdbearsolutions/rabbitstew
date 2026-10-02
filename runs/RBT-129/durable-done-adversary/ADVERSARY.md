# Adversary review: PR #510 "RBT-129 durable done-marker" (head e9c87788)

Verdict: **MERGE AFTER FIXES**

The core idea is sound. If the lane is killed anywhere after `_mark`, the restart finds no receipt, saves in the foreground and skips the job, so the job is never re-run. Kill-point table:

| kill point | restart behaviour | ok? |
|---|---|---|
| before `_mark` | no marker: the job re-runs or resumes (unchanged) | yes |
| marker written, save not started | no receipt: foreground save, receipt, skip | yes |
| during the save (tar or push) | no receipt: foreground save (it may duplicate a push that landed) | yes |
| save exited 0, receipt not yet written | duplicate foreground save (harmless) | yes |
| after the receipt | skip, no save | yes |
| reboot, dir gone | `_restore` restores it and receipts the restored markers: skip | yes |

Simulation behaviour: unchanged. `_finish` is exactly `_mark` followed by `_save` at every former call site, including the extinct-snapshot path, which used to save after the if/else. Every output file under runs/ is unchanged. The PR adds only receipts in /tmp, a stderr line and foreground saves at restart.

## MUST

### M1. A partially restored dir is force-pushed over the good snapshot
Lines: stages.py:728-747 (`_finished`), with stages.py:791-800 and scripts/durable.sh:102.

`durable.sh restore` unpacks into the run dir with `cp -a`. It merges the files in place and is not atomic. `durable.sh save` force-pushes a single parentless commit, so the previous snapshot is lost.

Scenario:
1. Near the 2 h cap, or during a reboot, the lane is killed inside a restore. This can be its own dir's restore or a fork's `_restore(job["src"])` of S.
2. `state.json` and `.rbt129-done-S60` were copied, but `lineage.jsonl` and `genomes/` were not, and no receipt was written.
3. On restart the probe exists, so there is no re-restore.
4. `_finished` finds a marker with no receipt and calls `save_now(d)`, which force-pushes the truncated dir over the only complete snapshot.

Before this PR, `_done` skipped the job and the branch stayed intact. Reproduced: a dir holding only `state.json` and the marker is pushed as-is (scratch repro, fake durable.sh).

Fix: `_restore` writes a `.rbt129-restoring` sentinel (outside the tar's view, or removed after success). `_finished` re-restores instead of saving when the sentinel is present. Alternatively make the restore atomic: copy to a sibling dir, then rename.

### M2. Unit-record saves keep the same lost-save window
Lines: stages.py:812-819 (`unit_file` / `_save(rec)`, no receipt), stages.py:948-954 and 966-971.

Scenario (the Stage-1 extinct `ckpt60` job):
1. `unit_file(EXTINCT)` and `unit_file(UNIT)` queue background record saves.
2. `_finish(d)` writes the marker.
3. The lane is killed before the queued saves finish.
4. On restart, `_finished` saves `ckpt60` only, and the record is never re-saved. Stage 1 has no K1 job to re-save it.
5. The record branch may already exist from KSALT's `unit_file`, so `check-branches` stays silent.
6. After a reboot, `restore_record` brings back a record without `EXTINCT.txt`. The resume, fork and M/N jobs then treat the unit as live. The fork of a marker-only `ckpt60` crashes on `config.json`, and keeps crashing on every restart.

Fix: when a pilot job's `_finished` takes the no-receipt path, also save `<unit>/record` in the foreground. Better still, receipt record saves too.

## SHOULD

- **S1. A reboot that keeps the run dirs but wipes /tmp** makes every done job on every lane save in the foreground, serially under the machine lock. Each save takes up to 2x900 s plus a retry, while L4 says no job waits on a save. This also pushes many redundant snapshots. Either keep receipts somewhere that survives a reboot (beside DURABLE_LOG, e.g. `runs/RBT-129/.durable-done/`, git-ignored), or bound the stall and document it.
- **S2.** `_fake_durable` (tests/test_rbt129_launch.py:847) does not patch `DURABLE_DONE`. Older tests that run `run_job` with a fake durable that exits 0 write receipts into the real `/tmp/rbt129-durable-done` on whatever machine runs them. The labels are tmp-path-derived, so nothing collides, but the tests should not touch the live machine. Patch it there, or in an autouse fixture.
- **S3.** `_receipt` (stages.py:717) uses a fixed `path + ".tmp"`. Two writers of the same receipt (a background thread and `_finished`, or two lanes) can race, and `os.replace` raises `FileNotFoundError`. Use a pid- or thread-unique tmp name. A `_receipt` exception inside `_finished` also kills the lane, so wrap it.
- **S4.** `check-branches --save` (stages.py:2038) saves without receipting. A manual backfill is therefore re-saved at the next restart.
- **S5.** `_finished` on a failed save returns True. That is acceptable, but `check-branches` checks only that a branch exists, not that the marker is on it. A periodic snapshot can satisfy it while the done-marker is still missing. Note this in the docstring, or have `check-branches` report unreceipted markers.

## Concurrency
- `save_now` serialization holds. Foreground saves at restart take the same lock.
- `_every` never receipts, which is correct: it stops before `_mark`.
- If a lane is killed, the orphaned `durable.sh` save (started with `start_new_session`, without the lock) can race the restart's foreground save to the same branch. Both snapshots contain the marker, so this is benign.

## Tests
- The SIGKILL test really kills the lane (`killpg`) and the hung save (the `sleep` pid) mid-save. It covers "kill during the save", not "kill between marker and save start". The fresh-job test covers the latter only by monkeypatching `_save`.
- The tests need no network: durable.sh is faked and `_restore` is stubbed or fails.
- Polling is bounded by a 60 s wait, plus a 0.2 s sleep before the read. That sleep is a small but real flake risk on a loaded host.
- No test covers M1 or M2.

## Suite
Clean venv `/tmp/v510`, `pip install -e ".[dev]"`, no scipy:
- Full suite: **915 passed, 1 skipped, 0 failed** in 15 min 12 s (`pytest -q`).
- An earlier run with `-x` hit the harness's 30-minute background limit and was stopped. The suite was slow, not hung: the rerun finished.
- The 5 new tests passed 5 times out of 5 in isolation. `test_rbt129_launch.py` with `test_rbt129_resume_lock.py`: 81 passed.
- S2 is confirmed: the run left 42 receipts in the real `/tmp/rbt129-durable-done`, from older tests such as `test_every_job_and_every_unit` that do not patch `DURABLE_DONE`.
