# RBT-129 Stage 2b(2a): the lane runner recipe (`s2b.py run-lane`)

Nothing here launches anything. A lane refuses (exit 10) until `GO-ID-2B: RBT129-S2-2B-GO-1` is open in
`stage2-plan/RULINGS-CITED-S2.md` on the merged base. That is the 2b lanes' own lock, which the coordinator opens after
the lanes' review.

## 1. The no-peek clause (paste it into every runner prompt, verbatim)

> **NO-PEEK.** You run the RBT-129 Stage 2b(2a) lanes and relay only what the lane prints on its own:
> - `start` and `done` lines;
> - EPA overflow counts;
> - `REFUSED:` lines and exit codes.
>
> **Never** open, read, print, `cat`, `grep`, `head`, `tail`, `diff`, `ls -l` or summarise anything else, under any
> path:
> - `run.log`, any `epa_overflow*.jsonl`, `durable.log`, `SCAN.txt`, `SSCAN.txt`, `S60CMP.txt`, `KSALT.txt`;
> - `state.json`, `history*`, `lineage*`, `cohorts*`, `arenas*`, `platform.json`, `config.json`, `EXTINCT.txt`,
>   `UNIT.txt`;
> - any file in a run directory (`runs/RBT-129/stage0|stage1|stageP|stage2a|stage2b|rb|…`);
> - `runs/RBT-129/stage2/stage2a_interim.txt` or `integrity-interim.txt`;
> - the content of any `ckpt/*` branch.
>
> **Fetch only with narrow refspecs** (`git fetch -q origin +refs/heads/<branch>:refs/remotes/origin/<branch>`). Never
> run a bare `git fetch` or `git pull`. Never fetch `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M`.
>
> **On a refusal, a crash, or a repeated non-native failure:** stop that lane and relay the line and the exit code to the
> coordinator. Do not diagnose by reading files. Do not change the repository.

## 2. The checkout

- **Check out the lanes' commit**, or any later commit of the merged base that keeps the pins below. It must carry:
  - the code blobs `lanes/S2B/launch.txt` pins (`code:` lines): `s2lanes.py`, `stage2_readout.py`,
    `stage1_readout.py` and `s2b.py`;
  - the `rabbitstew`, `runs/RBT-129/launch` and `scripts` trees it pins (`tree:` lines).

  The lock and ruling files (`RULINGS-CITED-S2.md`, `continuations/QUARANTINE.md`) are not pinned. The GOs are read
  from the merged base.
- **The history the 2a GO check needs (FC-2).** A shallow clone must be deepened first, with the narrow fetch in
  `RUNNER.md` §1.
- **No PYTHONPATH** (`check_modules`, exit 5).

## 3. The interpreter

`/opt/rbt129-venvs/instr/bin/python`: the registered build (c) v3, libmujoco sha256
`2aea9a9447d68edf07936df0d7d6a0c37b7e2df54441814b20ddd6e96ab763f4`. Any other interpreter refuses (exit 9).

## 4. The command

```
timeout -k 60 6600 /opt/rbt129-venvs/instr/bin/python runs/RBT-129/stage2/s2b.py run-lane runs/RBT-129/lanes/S2B/hostK-laneL.jsonl
```

- **The timebox (10-10 owner decision).** Each run ends itself after 110 min (`timeout -k 60 6600`: SIGTERM to the
  run's process group, SIGKILL 60 s later), so no harness background task ever reaches the 2 h cap. Exit **124** (or
  137) means "timeboxed", not a failure: start the same command again as a new background task, only after the old
  task has exited (its completion notice), and the second lane at least 60 s after the first. Before relaunching,
  check `pgrep -f 'durable.sh save'`: wait for any orphaned save from the old run to finish, and kill one by pid only
  if it is older than 15 min (its watchdog died with the run). The lane resumes exactly as it does after the cap: finished jobs are skipped by their
  markers, and a long job continues from its last 20-min durable snapshot.

- **One lane per process.** A host runs its two lanes (`lane0`, `lane1`) as harness background tasks, two lanes to a
  4-core session at `WORKERS=2`.
- **20 lanes on 10 hosts.** Each lane holds 4 S chains (S60, ckpt60, S to 300), and the two M points add M forks. That
  is 1,200–1,440 arm-seasons per lane, roughly 8–9 h of wall time.
- **Restarts.** A lane is resumable across the timebox (and the 2 h cap): a finished job is skipped once its marker is
  on its branch. Keep relaunching after exit 124/137 until the lane prints its own completion; any other exit code is
  a refusal or crash (§5): stop and relay.

## 5. The gates and their exit codes

| gate | refuses with |
|---|---|
| x86_64, MuJoCo 3.14.0, the build, the pinned trees, nothing uncommitted under them or the lanes (`stages.check_host`) | 3, 9, 5 |
| the pinned modules are this checkout's (`s2lanes.check_modules`) | 5 |
| the code is the launch's, by blob, committed (`s2b.check_code`) | 5 |
| the 2a GO with FC-2, a successful narrow fetch and enough history; then on the merged base `2B2A: COMMITTED`, `GO-ID-INTERIM` open, the interim output merged, and **`GO-ID-2B` open** (`s2b.check_go_2b`) | 10 |
| the overflow rule registered and merged (`stages.check_overflow_rule`) | 10 |
| `lanes/S2B` is exactly the emission from the committed interim, or that less the base's ruled exclusions (`check_s2b`) | 4 |
| blocks, salts, every job a 2b(2a) job of the gate (`check_lane_s2b`) | 4 |

At run time, a CRASHED run refuses (exit 4, `stages.check_not_crashed`). Stop the lane and tell the coordinator.
`s2lanes.drop` does not cover `lanes/S2B`. A ruled exclusion there is re-emitted by the coordinator's instruction, and
`check_s2b` accepts the emission less the base's ruled lines.

## 6. Beside the S scan (`lanes/SSCAN`)

The two lane sets can run side by side, on the same hosts and from the same checkout:
- **Trees:** both pin the same `rabbitstew` 5c69daac, `runs/RBT-129/launch` 4478e38d and `scripts` c0c5a858 trees.
- **Code pins:** they don't overlap. SSCAN pins `sscan.py` only; S2B pins `s2lanes.py`, `stage2_readout.py`,
  `stage1_readout.py` and `s2b.py`.
- **Seeds:** they are disjoint. SSCAN uses 129001–129008 and S2B uses 129009–129016, so the per-host seed locks never
  contend.
- **NOTE 17** applies while either set is live: no change to `runs/RBT-129/launch/`, `scripts/` or `rabbitstew/` may
  merge, and `continuations/OVERFLOW-RULE.md` stays at blob 162d7d0e.

---
_Generated by [Claude Code](https://claude.ai/code)_
