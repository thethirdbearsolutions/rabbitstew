# RBT-129 #465 fix-check: `ec283bb`, against #466 and the coordinator's ruling (#465 comment 5868360809)

**Verdict: MERGE.** Both MUST items are fixed and tested. So are S-2 to S-5, and N-2 and N-3. N-1 is fixed in the
code but has no test (NIT below).

**The trees:**
- **`ec283bb` on integration `bb4fa2d`:** a fast-forward. `bb4fa2d` is an ancestor of `ec283bb`, since #465 merged
  it in.
- **`ec283bb` + #459's `3e59928`** (= `9778848`).
- **#459's newer head `dc122ae`**, where named.

**The evidence**, all in this directory:
- `probe_465_fixcheck.txt`;
- `mutants465fix.py` → `mutants465fix.txt`;
- `suite_465_fixcheck.txt`.

**No-peek.** No Stage P, census or pays output was read. `durable.sh` was a local stub. The one remote read was
`git ls-remote` of branch names, reported only in aggregate.

## M-1: unit status and records. Fixed

**`unit_status` reads four sources in order:**
1. the unit's record (restored from its branch);
2. `EXTINCT.txt`;
3. **the local ckpt60 done-marker**;
4. **that marker from ckpt60's own branch**, through `branch_file`.

**`branch_file`** fetches the branch and pulls the one tar member (`ckpt60/.rbt129-done-ckpt60`) out in memory. It
restores nothing and reads nothing else.

**`_from_marker`** classifies the marker:
- the text written by the 7f8bfea and #465 code, `skipped: extinct pre-merge at season N`, means extinct;
- a bare timestamp means alive.

**Tested:**
- the PR's test reads status from a stubbed branch;
- its end-to-end test uses a real bare remote and a real `durable.sh`.

**Mutants, all killed:**
- M1a: no branch read;
- M1b: the local marker ignored;
- M1c: every marker read as alive;
- M1g: `branch_file` reads the wrong member.

**The premise holds now.** LEGS.md says every unit's ckpt60 directory is on the remote. That was not true of
`7f8bfea`'s extinct units, which were never saved. But by name only, **all 16 pilot units' `ckpt60` branches are now
on the remote** (L), presumably from hand saves.

Units' `record` branches: **0 of 16** so far. That is expected until `check-branches --save` runs on the Stage P
hosts.

**`check-branches --save` backfills `record/`** from the machine's `EXTINCT.txt` and `K1.txt`, plus a `UNIT.txt`
derived from the ckpt60 marker. It never overwrites the unit's own files.
- **`--repo DIR`** re-roots `ROOT` and `RUNS` after the lane paths are made absolute. The labels, `absolute()`,
  `durable.sh` and `git` then all resolve against the Stage P checkout.
- Mutants killed: M1d (no backfill), M1e (`K1.txt` not copied) and M1f (`--repo` ignored).
- **A K1 unit's ckpt60 and K1 jobs sit on the same lane** in all four P/0 K1 units (`host0`–`host3`, `lane0`), so
  `K1.txt` and the marker are on the same host for the backfill.

**The four K1 routes** are documented in `check_branches`' docstring and in LEGS.md:
1. **The record's `K1.txt`:** backfilled as above.
2. **K1fork's `.rbt129-done-K1` note:** written on both paths (`K1 PASS`/`FAIL`, and `…; K1 UNTESTABLE`). Mutants
   S3a and S3b are killed.
3. **The hand-saved `-unit` branches:** a readout-side lookup, with no code, as documented.
4. **`k1_compare` on restored K1ref and K1fork:** sound on restored directories, because `output_files` skips
   `.rbt129-done-*`, so the new K1 marker cannot create a spurious "only in fork".

## M-2: bounded saves. Fixed

- **What `save_now` does now:**
  - it starts `durable.sh` in its own session (`start_new_session`);
  - on `DURABLE_TIMEOUT` (900 s) it sends `SIGKILL` to the whole process group, logs `exit timeout`, retries once,
    then warns;
  - it releases the lock in a `finally` (and when the lock file closes).
- **(C2')**, with a 2 s timeout, and a stub whose "push" is a backgrounded `sleep 600`:
  - the lane process exited after its two bounded attempts (+4.8 s);
  - a leg's synchronous save got the lock between the attempts, and returned in 1.7 s;
  - both timeouts were logged;
  - **0 of 2 "push" grandchildren were alive** afterwards.
- **Mutants killed:**
  - M2a: the timeout never fires;
  - M2b: only `durable.sh` is killed, so the push lives on;
  - M2c: no retry;
  - M2d: a timeout returns 0.
- **Note:** a real save longer than 900 s (a very large run directory through the proxy) would be killed twice and
  warned. `check-branches` would then name it. Watch `durable.log` for `exit timeout`.

## The SHOULDs and NITs

| item | fix | test / mutant |
|---|---|---|
| **S-2**: periodic thread not a daemon | `daemon` dropped; `stop.set()` in a `finally`. (C3'): stopped mid-save, the thread is `daemon=False` and its save completes and is logged (`exit 0`); nothing is orphaned | new test; S2 killed |
| **S-3**: K1's verdict in its marker | both paths | S3a and S3b killed |
| **S-4**: `verify` covers both copies | `worlds/config/<id>/config.json` and `worlds/<id>.config.json` are both rebuilt and compared; a missing copy gives exit 4 | test edits `smell_tau` and the motor budget, and deletes the file; S4 killed |
| **S-5**: `compass_dose_response.py` pinned | added to `RBT97_CHAIN` | S5 killed |
| **N-1**: log under the lock | written inside the `try`, under `flock` | **no test**: M2e′, the log moved after the unlock, survives (NIT) |
| **N-2**: stage 2 passes, the confirmation does not | added to `test_calib_extract…` | N3a (the fallback without the confirmation) is now killed **before** #459 too |
| **N-3**: `_seen` = `planters.seen` when present | `_planters()` loads the pinned file under one module name, `rbt116_planters`, sharing `rbt116_steer` with `_steer()`; the fallback is otherwise the restated rule | below |

**N-3: the two agree on the K3 rule as ruled** (stage-2 c2 ∧ c3, repeated on the confirmation, F playing no part).
- **Method:** 192 records per head. They cover every combination of the four flags; `confirm`, `k3_confirm` or no
  confirmation; stage 2 present or absent; and a paying F or not.
- **Result:** `stages._seen`, `planters.seen`, the restated fallback and the ruled rule give **identical verdicts on
  all 192**, at both `3e59928` (`planters.py` `c9f6fca`) and `dc122ae` (`dfe53ed`).
- **The SD cross-check:** `dc122ae` adds `planters.dT_sd`. On 300 batteries (n = 2–64), `stages._dt_sd` equals it,
  and `np.std(ddof=1)`, to 1.4e-16. A zero spread gives 0 and n = 1 gives `nan` in both.
- **On a tree with #459,** `test_seen_is_planters_seen` now compares `planters.seen` with itself. The fallback is
  pinned before #459 by N-2's case (N3a and N3b killed); after #459 it is unused.

## Trial merges and the full suite (clean `.[dev]` venv, no scipy)

| tree | result |
|---|---|
| `ec283bb` on `bb4fa2d` | **723 passed, 2 skipped** (scipy; `planters.py` absent until #459). This matches the designer's count |
| `ec283bb` + `3e59928` | **757 passed, 1 skipped** (scipy) |
| `ec283bb` + `dc122ae` | `test_rbt129_launch.py` + `test_rbt132.py`: **87 passed** |
| mutants on `ec283bb` | **18 of 19 killed**. The survivor, M2e, is equivalent (closing the lock file unlocks it anyway); the real N-1 mutant M2e′ survives (NIT) |

## The running trees are untouched

`bb4fa2d..ec283bb` changes only `LEGS.md`, `runs/RBT-129/launch/stages.py` and `tests/test_rbt129_launch.py`.
- **`rabbitstew/`** (`b3a29ba`), **`scripts/`** (`d517cf5`), **`runs/RBT-129/lanes`** (`1513e19`) and
  **`runs/RBT-129/worlds`** (`2add53c`) are identical.
- **Stage P/0** runs from `7f8bfea` (launch tree `ae05373`), and **the finished legs** from `29ab80b` (`8f2e3ca`).
  Neither reads this launch tree (`9a3fa98`).
- **#459** changes nothing outside `runs/RBT-116/` and `tests/` since its merge-base.

## The list

- **MUST:** none.
- **NIT:** add a test for N-1: a slow second writer, or an assertion that the log line lands before the lock frees.
- **Operational:** run `check-branches --repo <session checkout> --save` in every Stage P session. Records are 0 of
  16 until then, and `K1.txt` for the old-code units lives only there.

---
_Generated by [Claude Code](https://claude.ai/code)_
