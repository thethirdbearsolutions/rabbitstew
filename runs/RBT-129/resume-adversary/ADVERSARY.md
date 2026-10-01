# RBT-129 resume adversary: PR #503 (one writer per run directory; K-SALT de-duplication)

**PR reviewed:** #503, head `9c47959`. **Base:** `claude/new-session-4cao7d` at `830450e`. The base had not moved, so
the trial merge is the PR head.

**No-peek:** No Stage-1 outcome was read or is reported here. That covers fitness, income, survival, alive counts,
shares, and Stage-1 lineage line counts.

- For the Stage-1 side of the 129003 K-SALT pair, this report gives only the verdict and whether the counts are equal.
- Census (Stage 0) structure is given as totals and season indices.

## Verdict: **MERGE AFTER FIXES**

There is one MUST, and it is a record, not code. The lock, the extinct-resume fix and the K-SALT de-duplication are
correct as written, and nothing in them changes the output of an uninterrupted run.

I re-ran the census reference cleanly from season 0, as DUP-VERIFY did, and it confirms the de-duplicated reading
exactly. The SHOULDs narrow the de-duplication rule and close two small gaps around the lock.

**Tests:** full pytest in a clean venv (`python -m venv /tmp/v && pip install -e '.[dev]'`, no scipy, python 3.11.15) on
the trial merge: **902 passed, 1 skipped**, 16 warnings, 961 s.

---

## MUST

**M1. Record the changed K-SALT reading as a ruling on F7 before the 129003 K-SALT is re-run and counted.**

- `half_compare` now reads every K-SALT reference (and SALT0 reference) with its exact-duplicate lineage lines
  dropped. That changes how a registered control (AMENDMENT-FOUNDING F7) is read, after the control fired VOID.
- The change is sound (see §2). It still needs a one-paragraph ruling next to F7, so the record does not show a
  control quietly redefined after a failure. The ruling should say:
  - the rule;
  - that it can only turn a reference-side double write from VOID into PASS, never the reverse;
  - the evidence for 129003: `dupverify.txt` here.
- The 13:19 VOID record and its done-marker stay where they are. The re-run is a separate, deliberate step, as the PR
  says.

## SHOULD

**S1. Narrow the de-duplication to the signature of a double write, and fail closed otherwise.** Today any exact
duplicate in any reference is dropped silently, apart from a count. I recommend dropping duplicates only when all of
the following hold:

- (a) every dropped line occurs exactly twice;
- (b) the generations holding duplicates are a contiguous range, and every line in each of them is doubled (a complete
  second copy);
- (c) the de-duplicated sequence has no step back in `generation`;
- (d) the reference's `platform.json` holds at least one resume record.

If any of these fails, the comparison should report VOID with the reason.

- The verdict line should name the generation range (for example `347 lines, generations 55-59, each doubled`), not
  only the count.
- The 129003 census meets (a)–(d): multiplicity 2 everywhere, generations 55–59 each fully doubled, no steps back
  after de-duplication, one resume record.
- This is a SHOULD, not a MUST, because the current rule cannot produce a false PASS (§2).

**S2. Fix the docstring's account of DUP-VERIFY.** The Stage P+0 DUP-VERIFY (`stageP0-readout/dupverify.txt`) did not
de-duplicate. It re-ran each unit cleanly from its checkpoint and compared the two, finding "saved = re-run + exact
duplicates". It then REPLACED each unit with its re-run.

- The new docstring says the reference is taken "as the Stage P+0 readout's DUP-VERIFY took them", which is not what
  DUP-VERIFY did.
- Suggested wording: "DUP-VERIFY established, by clean re-runs, that a double-written run is its clean run plus exact
  duplicates; this reads such a reference accordingly."
- For 129003 the clean re-run now exists (§2).

**S3. `_writer_gone` can wait forever, and it says so only once.** A hung orphan (for example a wedged pool worker)
stalls the lane with a single stderr line. Repeat the line every few minutes, with the lock holder's PID if it can be
read (`fcntl F_GETLK`), so a stall can be seen in the runner's log. Waiting is the right default, since proceeding is
what caused the double write.

**S4. `run_job` restores before it waits.** `run_job` calls `_restore(d, probe)` before `_fresh` / `_resume` reach
`_writer_gone`.

- Failure case: an orphan is still writing `d` but has not yet written its first `state.json` (it is inside season
  0), and a `ckpt/` branch for `d` exists. Then `durable.sh restore` unpacks into a live writer's directory.
- This window is narrow: the branch needs a 20-minute periodic snapshot taken before season 0 ended.
- The fix is cheap: call `_writer_gone(d)` at the top of `run_job` for the job kinds that write `d`.

**S5. `resumed.py --check-runs` only checks runs that have a resume record. Make "check every checkpointed run" the
default.**

- At 830450e, a lane restarted beside an orphan that was still in season 0 hits the `rmtree` branch of `_fresh` and
  starts fresh in the same path. That leaves a double write with **no** resume record: `command.txt` and
  `platform.json` are recreated by the new attempt.
- I ran the structural check over every checkpointed run, not only the resumed ones (`allruns.py`, `allruns.txt`, as of
  about 14:20 UTC):

| | checkpointed | with a resume record | never resumed | written twice |
|---|---|---|---|---|
| Stage-1 run dirs | 167 | 80 | 87 | **0** |
| census sources | 108 | 8 | 100 | **1** (`stage0/c1-p010-PW-G/129003/S`) |

- This reproduces the audit's claims ("no Stage-1 run written twice"; 1 of 108 sources). The Stage-1 numbers grew
  because the branches moved on since 13:45 (153 → 167 checkpointed).
- The claim holds only up to each run's latest snapshot. A double write after the snapshot would not be seen. Rerun the
  check when the stage closes.

## NOTE

**N1. Byte-identity of an uninterrupted run (required): holds.**

Fresh runs at base `830450e` and at the PR head were compared with `diff -r`, excluding `run.lock`. Only
`platform.json` differs (`git_sha` and `written_utc`).

| case | how it was run | result |
|---|---|---|
| plain (persistent food, sweep log) | `byte.py`, 8 seasons, workers 2 | identical, 34 files |
| merge (`merge_after`, pooled capacity) | `byte.py`, 8 seasons, workers 2 | identical, 35 files |
| all-extinct at season 1 | `byte.py`, starvation | identical, 20 files |
| the production CLI | census command line (`--fair --sweep-log`, real world block), 3 seasons, `--workers 2`, process pool forked | identical, 255 files |

The new code adds no RNG draw. The pre-step extinct check reads lengths only, and the lock is file I/O outside the
simulation.

**N2. Lock semantics, probed (`lockprobe.py`):**

- **Released on SIGKILL.** The lock is freed when its holder is SIGKILLed, even while the holder's forked children
  are still alive. Forked children do not hold it.
- **Same-process caveats.** Within one process, `lockf` gives no exclusion: a second `hold_run` returns at once. Any
  `open`+`close` of `run.lock` by the holder drops the lock (POSIX record-lock semantics).
  - I checked the code paths: nothing in the ecology process opens `run.lock`. `glob('*.json')` does not match it,
    `durable.sh`'s tar runs in another process, and `output_files` skips it.
  - So the guarantee holds today. Say this in the `hold_run` docstring, so no later in-process reader breaks it.
- **No deadlock with the per-seed `flock`.** The ecology child does not inherit the lane's seed-lock descriptor:
  Python opens files `O_CLOEXEC` and `Popen` uses `close_fds=True`. So an orphan never holds the seed lock while the
  lane waits on `run.lock`.
- **When the lock is taken and released.** It is taken before the first byte of a fresh run (`__init__`, before
  `config.json`) and before a resume reads `state.json` or cuts the logs. It is released at the end of `run()`.
  - An exception, or an `Ecology` that is constructed but never `run()`, leaks the descriptor until the process exits.
    That is harmless for the CLI.
- **Long durable saves.** A save neither takes nor drops the lock.
- **NFS.** Run directories are on local container disk. `lockf` over NFS depends on NLM and was not tested.

**N3. A fresh CLI run into a directory someone else is writing now waits, then appends.** This is a pre-existing
hazard of `ecology --out` over an existing directory. The lane avoids it, because `_fresh` waits and only then
`rmtree`s or resumes. Consider refusing a fresh run when `run.lock` is held, instead of waiting.

**N4. The all-extinct resume fix.**

- Uninterrupted runs: identical (N1).
- A resume from a saved all-extinct state at 830450e:
  - It differs from the uninterrupted run only in `state.json`, whose `season` is one ahead.
  - `history.json` and the logs are identical in the synthetic case.
  - Under the PR, the resume equals the uninterrupted run.
- Completed runs keep their bytes; nothing is rewritten. A completed run that went through such a resume before the PR
  carries `state.json` one season ahead, and would differ from a re-run under the PR in that file only.
- I did not look for such runs. Finding them means reading Stage-1 extinction, which is no-peek.

**N5. DUP-VERIFY of the census reference (`dupverify.py`, `dupverify.txt`).**

- **Method.** `stage0/c1-p010-PW-G/129003/S` was re-run from season 0 to 60, clean, at the PR head. It used the
  census's own `command.txt` line (workers 2, python 3.11.15). It was compared with the saved census restored from
  `ckpt/rbt-129-stage0-c1-p010-PW-G-129003-S`.
- **Files.** 689 of 691 output files are byte-identical, including `history.json`, `state.json`, `arenas.json`, every
  genome and `final/`.
- **`lineage.jsonl`.** Saved 4748 lines; re-run 4401. The saved file, de-duplicated by first occurrence, is 4401 lines
  and **equals the re-run line for line, in order**. 0 lines are only in the saved file and 0 only in the re-run.
- **`cohorts.jsonl`.** Saved 77, re-run 72. The de-duplicated saved file equals the re-run, in order.
- **`half_compare(re-run, saved)`.** PASS for both faunas (the conventional one with the dropped-lines note).
- **Structure of the duplicates** (lineage):
  - the 347 duplicate lines are all in conventional generations 55–59, each line exactly twice;
  - the season column steps back twice in the raw file and never after de-duplication.
- This settles the 129003 reference on the DUP-VERIFY precedent's own terms. It also shows the PR head reproduces the
  census streams byte for byte.

**N6. Why the de-duplication cannot produce a false PASS.**

- Only the reference `b` is de-duplicated; the attempt `a` is not. A PASS needs `a == dedup(b)` as ordered lists.
- A single writer never repeats a lineage line: a line carries generation, name and death tag.
- So if the two writers diverged, their differing lines survive de-duplication, the length differs, and the result is
  FAIL. If `a` itself were double-written, its duplicates survive while `dedup(b)`'s do not, and the result is FAIL.
- Interleaving two identical writer sequences keeps first-occurrence order: each copy is increasing, so the minimum of
  the two positions is increasing too. Order is preserved, as confirmed on 129003.
- A false PASS would need `a` to reproduce exactly the same loss that `b` suffered. The residual risk is VOIDs that
  should have been PASSes, not the reverse. Hence S1 is a SHOULD.

**N7. The 129003 K-SALT pair (verdict only).**

- `half_compare(stage1 S, census S, conventional)` at 830450e: **FAIL** (the lineage differs; history rows are equal
  in count and content).
- At the PR head: **PASS**, with "347 exact duplicate lineage lines of the reference dropped".
- The Stage-1 S of this pair has 0 repeated rows, and its `command.txt` shows one fresh `--seasons 60` line.

**N8. No-peek hygiene in the PR body.** PR #503's body prints a Stage-1 count: the designed half's lineage line count
for seasons 0–59, which is a sum over the season population. `KSALT.txt` records the same number by design, but it is
a near-outcome. Keep such counts in `KSALT.txt` and out of PR prose. The census per-generation living/starved counts
are Stage 0 and are not covered.

**N9. SALT0 also goes through `half_compare`.** Stage F is complete. Under the PR, any SALT0 comparison could only move
from FAIL to PASS. No recorded SALT0 is re-run by this PR.

---

## Files

All scripts write under the scratchpad (`/tmp/claude-0`) and are kept here as provenance.

- `byte.py`: the synthetic fresh-run byte-identity check (N1). It was run once from each worktree.
- `lockprobe.py`: the lock-semantics probes (N2).
- `allruns.py`, `allruns.txt`: the structural double-write check over every checkpointed run (S5). It uses PR #503's
  `resumed.py`.
- `dupverify.py`, `dupverify.txt`: the census clean re-run comparison (N5). Counts and indices only.
