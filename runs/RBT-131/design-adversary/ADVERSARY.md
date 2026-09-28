# RBT-131 design adversary: #452 (head 16447c4)

## Verdict: MERGE

The fix is correct, and it is byte-identical for every fresh run into a new directory. Both new tests fail on the
pre-fix tree, and all three pass on the fix. The audit's conclusion holds: **no committed number moves, so no erratum is
needed.** I found no MUST.

The SHOULDs correct the audit's wording, where two supporting statements are weaker than they read. They do not
change the verdict and can go in with the merge or right after it. Merging cannot reach the running RBT-129 lanes.

No new evolution was run. The probes use test-sized ecologies from `tests/test_ecology_switches` helpers, committed
files and checkpoint branches, read-only.

| # | Level | Finding |
|---|---|---|
| S1 | SHOULD | AUDIT §1 "A fresh run has no `final/` when it ends" is false for a fresh launch into a reused directory. `ecology --out X` does not refuse an existing X; only RBT-106 and RBT-112 `run_arm.sh` do. This is a third exposure path, which the audit's three questions do not ask about. The fix covers it. No committed result used it |
| S2 | SHOULD | AUDIT §2.1 "No snapshot's `platform.json` records a resume" is vacuous. All 385 run directories have `resumes: null`, and 0 of 29 in my sample carry a `platform.json` at all, because `record_resume` is RBT-127. Documented mid-run resumes (RBT-102 seed 3, RBT-105) are invisible to it. Drop the line or say it carries no information |
| S3 | SHOULD | `final_readers.txt` greps `runs/`, `scripts/` and `docs/` only. It should also list the library readers (`analysis.py:743`, `:880` and `:1015`, `ecology.py:1099` and `:1109`) and `runs/RBT-128/design-adversary/designed_scan.py:29`, a recursive `runs/**/*.json` glob that reads P-801's `final/`. All are safe (`probe_readers.txt`) |
| N1 | NIT | Clear-then-write leaves a window. A kill inside `_save_populations` leaves `final/` holding a *subset of the living* (`probe_fix_edges_fixed.txt` (A): 1 of 3). The pre-fix tree leaves a mix with the dead. The next resume, even one with no seasons left, rewrites it cleanly, and a runner that treats a missing "results in" as unfinished will resume it. Acceptable. Say in the docstring that `final/` is valid only once the log reads "results in" |
| N2 | NIT | `str.isdigit()` accepts non-ASCII digits: `٣.json` and `².json` are removed ((B)). Nothing writes such names. `re.fullmatch(r"[0-9]+", stem)` is exact |
| N3 | NIT | A fork whose `<kind>/final` is a *symlink* to the parent's makes the clear delete the parent's surplus ((C): 6 files become 3). The pre-fix tree already overwrote the parent's `000..n-1`, so the parent was corrupted either way. No committed script forks by symlink; the symlink users (RBT-92, 99 and 101 readouts) only read |
| N4 | NIT | Two processes writing one `out_dir`: the clear widens an existing race. It is not a supported use, and no launcher does it: RBT-129 takes a flock per seed, and `run_arm.sh` refuses to relaunch |
| N5 | NIT | AUDIT's RBT-129 row cites `stages._clear_final`. That file is not in #452's tree, which branches from 01f113d; it is on the base (`runs/RBT-129/launch/stages.py:565`). Cite the base commit |
| N6 | NIT | AUDIT's RBT-107 row says "fork.py / extend were used in throwaway checks only". `extend_arm.sh:55` (resumes a finished arm to 1200) and `new_seed.sh:47` (a fork, then cull20) are real launchers, planned in PREREGISTRATION:112 and never run: Amendment 2 superseded them, and PREREGISTRATION:580 says new_seed.sh "was not run end to end". The conclusion stands |
| N7 | NIT | `Evolution._save_populations`: the "harmless" claim is true (item 3). A one-line port would still keep the two writers symmetric. Optional |

## 1. The fix

**Byte-identical for fresh runs, confirmed.**
- The clear runs only on files that exist when a run ends. A fresh run into a new directory has none.
- The audit's own evidence: `fresh_identity_*.txt` (133 files, identical) and the golden `FRESH` digests.
- My own check: `probe_final_tests.txt`, every `tests/*.py` that mentions `final` (13 files), passes on 16447c4: 187
  passed.
- The exception is S1: a fresh launch over a finished run. There the fix *changes* the bytes, and correctly, since the
  pre-fix output kept the dead ((D): 6 files for 3 living on 01f113d, 3 for 3 on the fix).

**Clears only member files, confirmed** (`probe_fix_edges_*.txt` (B)).
- Removed: `0999.json`, `1000.json` (index ≥ 1000 is safe) and the two Unicode names in N2.
- Kept: `best.json`, `003.JSON`, `003.json.bak`, `notes.txt`, `.004.json`, `config.json`.

**Could it delete something a reader needs?**
- Only in the kill window (N1), and what it leaves there is a subset of the living, never a dead member.
- Recovery was checked: a resume after the simulated kill leaves `final/` equal to `state.json`, in both kinds.
- A partial `final/` from a crash *before* the fix is also cleared and rewritten by the next save, which is what is
  wanted, because `state.json` is the source of truth.
- `_parent_pool` and `population_files` fall back from an empty `final/` (an extinct fauna) to the saved bests, as
  documented. The fix makes a resumed-to-extinction fauna take that path instead of reading its dead.

**The tests really discriminate.** I re-ran `tests/test_rbt131.py` against a worktree of 01f113d, with
`PYTHONPATH` pinned to it (checked: `rabbitstew.__file__` is under the worktree).
- Pre-fix: resume FAILED, fork FAILED, fresh passed. The failure is `['000'..'005'] != ['000'..'002']`.
- On 16447c4: 3 passed.
- This matches the committed `test_rbt131_{prefix,fixed}.txt`.

## 2. The audit's completeness

**Readers** (`probe_readers.txt`, an independent grep).
- The search found no reader beyond those whose callers AUDIT §3 already covers. S3 is about listing them.
- The brief's specific claims check out line by line:
  - RBT-107, RBT-126, RBT-130 and RBT-118 read `lineage.jsonl`, `genomes/`, `best_gen*` or `state.json`, never
    `final/`. The only exceptions are RBT-107's `extend_check.sh:50-55`, which counts the stale files as its finding,
    and the `-not -path '*/final/*'` exclusions.
  - RBT-113 `decompose.py:83-86` asserts n = 40 and generation G-1, so a stale file would crash it, not bias it.

**Committed `final/` populations.**
- `git ls-files` has exactly one: `runs/RBT-19/P-801`.
- `probe_p801.txt` checks it: 60 + 60 names equal lineage's generation-599 living, lineage generations never restart
  (so no relaunch over the directory), and history's last season is 599 with 60 alive.

**Checkpoint sweep, resampled** (`probe_ckpt_sample.txt`).
- 20 random `ckpt/*` branches (`random.seed(131)`), 29 run directories.
- This is stricter than the audit's count check: member *names in order* against `state.json`'s populations.
- 17 ecology runs have a `final/`; there are **0 mismatches**. Arena rows match `population_size`.
- Also recorded: 0 of the 29 have a `platform.json` (S2).

**Could any result move?**
- A result would have to read an ecology `final/` produced by a resume after a finish, a fork, or (S1) a relaunch
  over a finished run, followed by a shrink.
- I found none. The one committed `final/` is clean. Every checkpointed `final/` I sampled is clean. Every seeded
  launch reads a digest-pinned `founders/` directory, not a run directory.

## 3. `Evolution._save_populations`

"Harmless while the arena population is fixed" is true for every committed arena run:
- `evolution.py` has no cull or shrink path. `reproduce()` always refills to `population_size`, or to 2 ×
  `population_size` under `survival`, which is also constant.
- `Experiment.resume` (`evolution.py:658-688`) takes the config from `config.json` and changes only `generations` and
  `workers`.
- Committed arena configs use 20, 40 or 300. RBT-37's extension keeps RBT-12's 20. No script edits `population_size`
  before a resume.
- Every rewrite therefore covers the same `000..N-1`.

A latent case in both writers, not fixed by #452 and not needed: a run resumed after it finished holds the *previous*
finish's `final/` until the extension ends. RBT-113 `decompose` guards against this with its generation assert. RBT-129
removes `final/` before every resume.

## 4. The running RBT-129 sweep (`probe_rbt129_pin.txt`)

- `git merge-tree` of #452 into the base is clean. It changes `tree:rabbitstew` from 69b5d6c (the launch's, in the one
  shared `lanes/P-0/launch.txt`) to b3a29ba. `runs/RBT-129/launch`, `scripts`, `lanes` and `worlds` are unchanged.
- `run_lane` calls `check_host` first, and that call refuses with exit 5 when any pinned tree differs. A lane started
  on a post-merge checkout cannot run.
- Nothing in `launch/`, `lanes/` or `scripts/durable.sh` pulls, checks out or resets. `durable.sh` fetches only
  `ckpt/<label>` into `refs/remotes/`, so a running lane's worktree never moves.
- The guard runs only once, at lane start, and each job re-imports `rabbitstew` from disk. So a *manual* `git pull` in
  a lane's checkout mid-lane would switch the code silently.
- Even then, `final/` would be unaffected: every lane resume and fork runs `_clear_final` (rmtree) first, and fresh jobs
  start in an emptied directory. #452 is a no-op on lane outputs.

**Merging #452 cannot affect running lanes.**

## Files

- `probe_fix_edges.py` → `probe_fix_edges_fixed.txt` (16447c4) and `probe_fix_edges_prefix.txt` (01f113d): (A) the
  kill window and its recovery, (B) the names cleared, (C) the symlinked fork, (D) a fresh run over a finished one.
- `probe_ckpt_sample.py` → `probe_ckpt_sample.txt`: 20 checkpoints, member names compared in order.
- `probe_p801.py` → `probe_p801.txt`: the only committed `final/`.
- `probe_readers.txt`: the independent reader search, and the claims checked line by line.
- `probe_rbt129_pin.txt`: the pinned trees, and the merge result.
- `probe_final_tests.txt`: every `final`-touching test file on 16447c4, 187 passed.
