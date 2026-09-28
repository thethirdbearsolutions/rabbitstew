# RBT-129 legs fix-check: PR #455 at `29ab80b`, against ADVERSARY-LEGS.md (#457)

**Verdict: MERGE.** Every item on #457's list is fixed and tested, and nothing new blocks the merge.
- There is one launch instruction (N-1): which commit the runners check out.
- There are two notes (N-2, N-3), neither blocking.

**The files.**
- `probe_fixcheck_legs.txt` holds the verify runs, the deviation matrix (its script is inlined at the end) and the
  runner audit.
- `suite_fixcheck_legs.txt` holds the full suite.

**What ran.** Nothing on real hosts: only `verify`, the tests' fixtures, and one stubbed job, run through the emitted
promote-and-save line against a local bare remote, not origin.

**The trial merge.** Integration `7f8bfea` is an ancestor of `29ab80b`, because #455 merged it in with a merge commit.
So the trial merge onto `7f8bfea` is a fast-forward to `29ab80b`.

## The items

| item | status | evidence |
|---|---|---|
| **L-1 (MUST)**: the steps leg reads a verified input | **Fixed.** `step_jobs` passes `--config runs/RBT-129/worlds/config/<id>`, the directory `verify` rebuilds and fair-checks, and `steps.py` reads `<dir>/config.json`. No runner references `worlds/<id>.config.json` any more (0 hits). | Matrix: a committed motor budget of 3.0, or centre eating, in `worlds/config/c1-p030-PW-G/config.json` gives **exit 4 on both legs**; uncommitted, it gives exit 5. `test_l1_an_edited_steps_input_is_refused` checks both edits against the file the emitted job reads. |
| **L-2 (MUST)**: `--decoy 3` at the PW cells | **Fixed, exact parity.** 60 of the 180 prize jobs carry `--decoy 3`: 10 hosts × the 6 PW cells. No U or HP job has a decoy, and every PW job has one. That is where registered `run_gate.sh:62` puts it (`prize $cell $s --decoy 3` for the PW cells only). | LEGS.md has the parity table: only the world differs, as DESIGN §5.1 asks. The test pins 60 jobs over 6 cells. |
| **S-1**: per-leg pins | **Fixed.** Prize pins `prize_gate.py`, `routed_populations.py`, `routed_p801.py` and `g500_direction.py`. Steps pins the same four plus `steps.py`. `steer.py` is not pinned. | Matrix: an edit to `routed_p801.py` or `g500_direction.py` gives exit 6 on both legs. An edit to `steps.py` gives exit 6 on steps only. **An edit to `steer.py` gives exit 0**, so RBT-132's change cannot stop the legs. |
| **S-2**: run from the legs' own commit | **Fixed, with integration through #456 merged in.** The launch records pin `rabbitstew` `b3a29ba` and `scripts` `d517cf5` (both `7f8bfea`'s), and `runs/RBT-129/launch` `8f2e3ca` (this PR's). LEGS.md and the PR comment say to check out `29ab80b`, and never integration's head. | `verify` gives exit 0 on both legs at `29ab80b`, and again on `29ab80b` with #457 merged. A later commit touching `stages.py` gives exit 5, which is loud. See N-1 for `61cb19b`. |
| **S-3**: durable outputs | **Fixed, and it works end to end.** After each promotion, the runner saves that cell's directory to `ckpt/rbt-129-stage0-pays-<id>-{prize,steps}`. At its top, it restores any missing cell directory. Cells are split whole across runners (0 directories shared), and there is one save per job: 180 prize and 18 steps. | Stub run (probe §e): job 801 promoted and saved, then the cell directory was deleted as a stand-in for a reclaim. The rerun restored it and **did not rerun 801** (it ran once over two runs). A job without `ROW` is not promoted (`FAILED`, exit 1). The untracked outputs and restored hosts do not trip `verify`'s clean check (exit 0), since `stage0/`, `bodies/` and `hosts113/` are outside `CLEAN`. |
| **S-4**: how to start and stop | **Fixed.** All 6 runner headers and LEGS.md say: start as a harness background task, one per session; never `nohup`, `&` or `setsid`; never `pkill` by name, kill children by pid. Outside comments, no runner contains `nohup`, `setsid`, `disown`, a trailing `&` or `pkill`. | Probe §d. |

## The further checks

**`verify` on clean checkouts: pass where the runners run.**
- **`29ab80b`** (the PR head, which is also the trial merge onto `7f8bfea`): both legs exit 0.
- **`29ab80b` + #457:** both legs exit 0. #457 touches only `runs/RBT-129/design-adversary/`.

**No drift in P/0.**
- `git diff 7f8bfea 29ab80b -- runs/RBT-129/lanes/P-0/` is empty. `lanes/P-0` is tree `ace63db` on both.
- P/0's `launch.txt` pins `runs/RBT-129/launch` `ae05373`, which is `7f8bfea`'s tree after the fix1/fix1b amendments.
- #455 changes nothing that `run-lane` or `run_job` uses. Its `stages.py` hunks are the leg functions,
  `write_script`'s optional `launch` argument, and the argparse dispatch.
- Once #455 merges, integration's launch tree becomes `8f2e3ca`. So **P/0 must keep running from `7f8bfea` (#456's
  commit)**, as LEGS.md says. A P/0 restart on integration's head would refuse with exit 5, loudly.

**The full suite:** clean `python -m venv` plus `pip install -e ".[dev]"`, no scipy, at `29ab80b`:
- **710 passed, 1 skipped, 16 warnings in 24 min.**
- The skip is `tests/test_rbt125_harness.py:170` ("could not import 'scipy.stats'"), which is expected.

## Notes

**N-1 (launch instruction): check out `29ab80b`, or #455's merge commit, not the `commit` line in `launch.txt`.**
- Each `launch.txt` records `commit 61cb19b`. That is the **emit base**: the HEAD the legs were emitted on, before the
  re-emit was committed.
- At `61cb19b`, `lanes/pays-*/` still hold the previous emit (`45e03c9`, launch tree `a4fd07d`). So a session that
  checks out the recorded commit and runs its `runnerK.sh` gets **exit 5 on both legs**. That is loud, and it runs
  nothing, but it is not the checkout to use.
- The right checkout is any commit whose pinned trees are the record's and which carries `29ab80b`'s `lanes/pays-*/`:
  - `29ab80b` itself, as the PR comment says;
  - or the merge commit of #455 (and #457) into integration, as long as nothing under `rabbitstew/`, `scripts/`,
    `runs/RBT-129/launch`, `worlds/` or `lanes/` has moved.
- Name that commit in the launch message.

**N-2 (minor): a failed restore redoes and overwrites.** `restore_outputs` swallows a failed restore (`|| true`), for
example a proxy error on a fresh container. The runner then redoes that cell's promoted jobs. Its next save
force-pushes a snapshot holding only the redone subset, which replaces the older, fuller one. This costs time, not
correctness: every job is still redone and promoted on its own `ROW`/`STEP`. If a runner logs no `durable: restored`
line for a cell it had already started, restart it rather than let it run on.

**N-3 (tidy-up, not blocking):**
- `world_config_dirs` still writes `worlds/<id>.config.json`, which no leg reads and `verify` does not check. An edit
  to it gives exit 0, which is harmless today.
- Drop it, or verify it too, before anything starts reading it again.

## The list

- **MUST:** none. L-1 and L-2 are closed.
- **SHOULD:** none open. S-1 to S-4 are closed.
- **Launch:** the runners check out `29ab80b`, or #455's merge commit (N-1), each started as a harness background
  task. P/0 stays on `7f8bfea`.

**MERGE #455 + #457, and launch the 6 runners.**

---
_Generated by [Claude Code](https://claude.ai/code)_
