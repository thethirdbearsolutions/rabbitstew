# RBT-129 Stage 2a: the lane runner recipe (`s2lanes.py run-lane`)

Nothing here launches anything. A lane refuses (exit 10) until `GO-ID-2A` is open on the merged base
(`STAGE2-PLAN.md` §2.7, §11). This page says how a host gets to the point where the gates can pass, and what each
refusal means.

## 1. The checkout

- **The code.** Check out a commit whose `runs/RBT-129/stage2/s2lanes.py`, `runs/RBT-129/stage2-plan/stage2_readout.py`
  and `runs/RBT-129/stage1-readout/stage1_readout.py` are the blobs `lanes/S2A/launch.txt` pins (`code:` lines), and
  whose `rabbitstew`, `runs/RBT-129/launch` and `scripts` trees are the ones it pins (`tree:` lines). The lock and
  ruling files (`RULINGS-CITED-S2.md`, `continuations/QUARANTINE.md`) and the plan's prose are not pinned: the GO and
  the quarantine lines are read from the merged base.
- **The history the GO check needs (FC-2).** `check_go` walks the base's history of `RULINGS-CITED-S2.md` to every
  commit that opened `GO-ID-2A` and its parent. A shallow clone (the cloud default is depth 50; the base gains about 56
  commits a day) must be deepened first, with a **narrow** fetch:

  ```
  git fetch -q --shallow-since=2026-10-03 origin +refs/heads/claude/new-session-4cao7d:refs/remotes/origin/claude/new-session-4cao7d
  ```

  or deepen (`--deepen=<n>`, same refspec) until the walk resolves. Without it the lane refuses with exit 10 and prints
  this command. Never a bare `git fetch` or `git pull`.
- **No PYTHONPATH.** `check_modules` refuses (exit 5) if `stages`, `blocks`, `mjbuild`, `epa_ecology` or `rabbitstew`
  load from anywhere but this checkout.

## 2. The interpreter

`/opt/rbt129-venvs/instr/bin/python`: the registered build (c) v3, libmujoco sha256
`2aea9a9447d68edf07936df0d7d6a0c37b7e2df54441814b20ddd6e96ab763f4` (`STAGE2-PLAN.md` §3.1). Any other refuses (exit 9).

## 3. The command

```
/opt/rbt129-venvs/instr/bin/python runs/RBT-129/stage2/s2lanes.py run-lane runs/RBT-129/lanes/S2A/hostK-laneL.jsonl
```

One lane per process; a host runs its two lanes (`lane0`, `lane1`).

## 4. The gates, in order, and their exit codes

| gate | refuses with |
|---|---|
| x86_64, MuJoCo 3.14.0, the build, the pinned trees, nothing uncommitted under them or the lanes (`stages.check_host`) | 3, 9, 5 |
| the modules are this checkout's (`check_modules`) | 5 |
| the code is the launch's, by blob, committed (`check_code`) | 5 |
| the 2a GO on the merged base, FC-2, a successful narrow fetch, enough history (`check_go`) | 10 |
| the overflow rule registered and merged (`stages.check_overflow_rule`) | 10 |
| the lane file is its slice of the emission, or that slice less the base's ruled exclusions (`check_emission`) | 4 |
| blocks, salts, every job a Stage-2a job, no quarantined label (`check_lane_s2a`) | 4 |

At run time: a CRASHED run refuses (exit 4, `stages.check_not_crashed`); an S60CMP DIFFER refuses (exit 4) at its
comparison and at every later job of its unit, on every restart (`require_identical`).

## 5. After a refusal

- **A CRASHED run, or a quarantined one.** The coordinator rules it on the base: `CRASHED: <run label>` (the run
  directory's checkpoint label, e.g. `rbt-129-stage2a-c1-p053-U-L-129006-M`) and/or `QUARANTINE: <label>` in
  `RULINGS-CITED-S2.md` or `continuations/QUARANTINE.md`. Then re-emit the lanes without it:

  ```
  /opt/rbt129-venvs/instr/bin/python runs/RBT-129/stage2/s2lanes.py drop
  ```

  `drop` rewrites only the lane files that hold the ruled runs (the run, and every job that reads it: a crashed S takes
  its whole unit; a crashed M only itself). `launch.txt` is unchanged, so the code pins hold. Commit the lane files,
  then restart the lane. `check_emission` accepts exactly that lane, and nothing else may be dropped.
- **S60CMP DIFFER.** HELP: tell the coordinator. The unit does not go on.
- **Anything else.** HELP, with the refusal's text.
