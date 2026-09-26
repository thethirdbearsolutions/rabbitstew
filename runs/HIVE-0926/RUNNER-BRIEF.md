# Arm-runner brief: the held-out challenge fan-out (2026-09-26)

The coordinator (`session_01WKXr6PgNkscGhVc7Bzth9k`) dispatched these sessions on 2026-09-26, once four things were done:
- RBT-90 part 2's pooled readout was merged (#118);
- all four challenge designs were cleared: C1 RBT-92, C2 RBT-99, C3 RBT-100, C4 RBT-101;
- `runs/RBT-92/onset.txt` was committed (#117);
- C4's step-0 control passed (#119).

Each session's prompt names its **ticket, seed, section of this brief, and branch**. The design is pre-registered, adversaried and cleared. **Your job is to run it exactly, not to improve it.**

`SEED` is your seed. `T` is its onset, the second field of the seed's line in `runs/RBT-92/onset.txt`. `T+10` is ten seasons later.

## 0. Rules for every runner (binding)

- **Read first:** `runs/README.md`, especially "A run must outlive its container". Then read your ticket's `PREREGISTRATION.md` sections on per-arm commands and sequencing, and the header of the launcher named below. The launchers are pre-registered: run them as written, and change no script.
- **Branches:** work from the integration branch `claude/new-session-4cao7d`. Push only to the branch your prompt names.
- **Launching an arm:**
  - Start it as a harness background task (Bash `run_in_background`; never `nohup` or `&`), with `WORKERS=4`.
  - Beside it, as a second background task, run `DURABLE_WATCH_PID=<the arm's python pid> scripts/durable.sh every 20 <ARM_DIR> <LABEL>`, with the label given below. Use `pgrep -f` to find the pid.
  - Expect about 6 s per season, so a 600-season arm takes about 60–70 minutes.
- **Checking progress:** the season is in `<ARM_DIR>/state.json`. To read another session's checkpoints, fetch them explicitly: `git fetch origin '+refs/heads/ckpt/*:refs/remotes/origin/ckpt/*'`.
- **If your container restarts mid-arm:**
  1. `scripts/durable.sh restore <ARM_DIR> <LABEL>`;
  2. continue with `rabbitstew ecology --resume` on that directory, with the same WORKERS (see `runs/README.md`);
  3. restart the durable loop;
  4. once the arm ends, run the launcher's post-run lines by hand.
- **Committing:**
  - Commit only the small text files the post-run step writes. `.gitignore` keeps the bulk out.
  - `git add <ARM_DIR>`, then check `git status` / `git diff --cached --stat` shows no file over about 1 MB.
  - Commit and push after each arm and each k file.
  - When your arms are done, open **one PR** against `claude/new-session-4cao7d`, titled `<TICKET> arms, seed SEED: <arms>`.
- **Read no result.** Compute and post no income, recovery, class or wiring figure. The designer runs the pre-registered readout once every seed is in.
- **Your ticket comments are operational only:**
  - at launch, one line with your session id, branch and arms;
  - k when you compute it;
  - the PR number at the end;
  - anything that went wrong.
- **Wake the coordinator only for a failure or a question**, not on success; the coordinator sweeps PRs. To wake it:
  1. create a one-shot Routine with `create_trigger`, `persistent_session_id` `session_01WKXr6PgNkscGhVc7Bzth9k`, and the prompt "Delegate wake: <ticket> seed <SEED>, <what>; read it and act";
  2. fire it with `fire_trigger`.
- **k = 0/0 is not a failure.** When `cull-k-SEED.txt` reads `holistic=0,conventional=0`, the cull launcher exits 0 and runs nothing, by design (RBT-92 amendment 2): the null is the baseline itself. Say so on the ticket.
- **Scope:** touch no other seed's or ticket's directory, and change no shared file.

## 1. C1 session A (RBT-92): the shift arm, and k

1. Run `WORKERS=4 runs/RBT-92/run_arm.sh SEED shift`. It writes `runs/RBT-92/shift-SEED/`; the durable label is `rbt-92-shift-SEED`.
2. **At season T+10** (`state.json` season ≥ T+10, about 38 minutes in):
   - run `python runs/RBT-92/cull_k.py SEED runs/RBT-92/shift-SEED > runs/RBT-92/cull-k-SEED.txt`;
   - **commit and push it immediately**: session B of the same seed polls your branch for this file;
   - post k in one line on RBT-92.
3. When the arm ends, the launcher's post-run step has already written the tables. Check `seasons.txt`, `lineage-last.txt`, `events.txt`, `groups.txt` and `event.txt` are there. Commit, push, and open the PR.

## 2. C1 session B (RBT-92): the validation cull, then the null

1. Run `WORKERS=4 runs/RBT-92/run_arm.sh SEED cull20`. It writes `runs/RBT-92/cull20-SEED/`; the durable label is `rbt-92-cull20-SEED`. Its post-run step writes the tables **and `wiring.txt`**, which RBT-101 (C4) needs as its divergence null. Check both exist. Commit and push.
2. **Get k from session A's branch**, `results/RBT-92-arms-SEED-a`: `git fetch origin results/RBT-92-arms-SEED-a && git checkout FETCH_HEAD -- runs/RBT-92/cull-k-SEED.txt`.
   - Session A commits it about 38 minutes in, normally before your cull20 ends.
   - If it isn't there yet, poll every 5 minutes with a timeout-bounded loop.
   - Don't commit this file on your branch; it is session A's.
3. Run `WORKERS=4 runs/RBT-92/run_arm.sh SEED cull`. It writes `runs/RBT-92/cull-SEED/`; the durable label is `rbt-92-cull-SEED`. When it ends, commit, push, and open the PR with both arms.

## 3. C2, C3 and C4 (RBT-99, RBT-100, RBT-101): one session per seed, shift then null

There is no cull20 in these three: RBT-92's is cited, since it is the same command at the same seed and T.

| ticket | challenge | launcher | arm directories | durable labels |
|---|---|---|---|---|
| RBT-99 | C2 dearer work (`work-cost=0.08` at T) | `runs/RBT-99/run_arm.sh` | `runs/RBT-99/{shift,cull}-SEED/` | `rbt-99-{shift,cull}-SEED` |
| RBT-100 | C3 scarce food (`food-items=6` at T) | `runs/RBT-100/run_arm.sh` | `runs/RBT-100/{shift,cull}-SEED/` | `rbt-100-{shift,cull}-SEED` |
| RBT-101 | C4 flat terrain (`terrain=flat` at T) | `runs/RBT-101/run_arm.sh` | `runs/RBT-101/{shift,cull}-SEED/` | `rbt-101-{shift,cull}-SEED` |

`D` below is your ticket's directory, `runs/RBT-99`, `runs/RBT-100` or `runs/RBT-101`.

0. **C3 (RBT-100) only, first:** the founders6 arm, from adversary F5(a).
   - Run `WORKERS=4 runs/RBT-100/founders6.sh SEED`. It writes `runs/RBT-100/founders6-SEED/`: 60 seasons, about 6 minutes, with no event.
   - Its post-run step writes `seasons.txt`. Commit and push.
   - No durable loop is needed (it is under 20 minutes), but run it as a background task.
1. Run `WORKERS=4 D/run_arm.sh SEED shift`, with its durable loop.
2. **At season T+10:**
   - run `python runs/RBT-92/cull_k.py SEED D/shift-SEED > D/cull-k-SEED.txt`;
   - commit and push it;
   - post k in one line on your ticket.
3. When the shift arm ends, check its post-run text files exist; the launcher header lists them. C3's launcher also writes `own.txt`.
   - **C4 (RBT-101) only:** run `python runs/RBT-101/wiring.py runs/RBT-101/shift-SEED` while the genomes exist, and commit `wiring.txt`.
   - Commit and push.
4. Run `WORKERS=4 D/run_arm.sh SEED cull`, with its durable loop. At k = 0/0 it exits 0 and runs nothing.
   - Check its post-run files. **C4:** run `wiring.py` on `runs/RBT-101/cull-SEED` too.
   - Commit, push, and open the PR.
