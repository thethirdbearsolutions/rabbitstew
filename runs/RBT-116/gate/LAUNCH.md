# RBT-116 W1 gate: how to launch the lanes

**Only on the coordinator's GO.** Every lane refuses without `RBT116_GATE_GO=1`. The lanes are pinned to
`rabbitstew/` tree `5c69daac` (claude/new-session-4cao7d at `8918697` and later) and to the blob of every script the
gate loads (`lanes/LANES.txt`). Any other tree or blob exits 6.

## The lanes (35 scripts in `runs/RBT-116/gate/lanes/`; 6 waves)

**Starting a wave.** Start a wave only when, for every lane of the wave before it:
1. the lane exited 0 after printing `lane <name> done` (each lane saves its final snapshot before that line), **and**
2. its final snapshot is on the remote: `scripts/durable.sh status <label>` names it for every `ckpt/rbt-116-w1-*`
   label the lane writes (its labels are in its script).

**Never start wave 4 (`g6-pilot`) or wave 5 (`readout`) while any `g6u`, `g4` or `g7` lane is still running or
unsaved.** The cells that read those shards sum whatever files exist when they run:
- G6's u_f (`measured_u`) adds up the `g6_u` parent files present, so a partial merge would silently change G6's choice
  of D;
- G4's and G7's summaries would read short, and fail rather than wait.

The coordinator gates the waves, and a runner reports DONE only on exit 0, which comes after the final save. This rule
is written down so that it does not rest on that alone.

| wave | lanes | what | CPU-h | wall at WORKERS=4 |
|---|---|---|---|---|
| 0 | `b-O1` … `b-O4`, `b-Z1` … `b-Z4` (8) | the 24 burn-ins B (3 units each), D16, 13 generations | 44 (5.5 per lane) | ≈ 1.5–2 h |
| 1 | `gate-a`, `g6-noise`, `g5` (3) | fixture check, config, hosts, screen, G1 + G2, G8 (d)(e) / σ_P / G5 timing | ≈ 3.5 | ≈ 45 min |
| 2 | `g8-s0` … `g8-s5`, `g4-s0` … `g4-s3`, `g7`, `g9-s0`, `g9-s1` (13) | G8 on 192 hosts, G4, G7, G9 | ≈ 12 | ≈ 30–40 min per lane |
| 3 | `g6u-s0` … `g6u-s7` (8) | G6's u_f | ≈ 26 (range 16–56) | ≈ 50 min (up to 1.5 h) |
| 4 | `g6-pilot` (1) | G6's choice, the pilot's 24 generations, its probe | ≈ 4.2 at D16 | ≈ 1.1 h |
| 5 | `readout` (1) | GATE.txt and `power.py` at the measured inputs | < 0.5 | ≈ 20 min |

**Runner sessions: 8.**
- Waves 0 and 3 use all 8, and wave 1 uses 3.
- Wave 2's 13 lanes run in two rounds on the 8 sessions: first `g8-s0`…`g8-s5`, `g7` and `g4-s0`, then `g4-s1`…`g4-s3`
  and `g9-s0`, `g9-s1`.
- Waves 4 and 5 use 1.
- With 13 sessions, wave 2 runs in one round and saves about 30 min.

**Wall clock: about 6 h end to end** (about 4 h for the gate after the burn-ins), plus the hand-off time between
waves. CPU: about 45 CPU-h for the gate (32–75 depending on how many plants steer) plus 44 CPU-h for the burn-ins, at
0.40 CPU-s per season. The burn-ins are the arms' B: they are not re-run for the arms.

## Running a lane

In a fresh cloud session (x86_64, 4 cores), on a clean checkout of claude/new-session-4cao7d at or after the merge of
this file:

```
RBT116_GATE_GO=1 WORKERS=4 bash runs/RBT-116/gate/lanes/<lane>.sh
```

Run it as a **harness background task** (never `nohup`). The lane snapshots itself to `ckpt/rbt-116-w1-*` with
`scripts/durable.sh`: every 20 minutes, and at the end of each cell or run. Its log is
`runs/RBT-116/gate/W1/lane-<lane>.log`, or `<run>/run.log` for an evolve run.

**Restart.** Re-run the same command, in the same or a fresh session.
- **Evolve runs** (wave 0, G5's timing runs and the pilot) are restored from their own checkpoint and continue with
  `evolve --resume`, byte for byte.
- **Gate cells** restore the earlier waves' checkpoints and skip every unit, host, shard or parent whose output is
  already on disk.
  - In the same container, a restarted cell lane loses nothing.
  - In a fresh container it recomputes its own shard. Every cell is deterministic, so the result is identical; only
    the time is lost.

## Exit codes

| code | meaning | action |
|---|---|---|
| 0 | the lane is done | start the next wave when its siblings are done |
| 1 | a `REFUSED: …` from gate.py (a missing input) or a Python error | read the log; report it |
| 3 | not x86_64; **or** a checkpoint this lane restores does not exist yet: an earlier wave's lane has not saved (the log shows `durable: no ckpt/…`) | use a cloud x86_64 session; or wait until the earlier wave's lanes are done and saved, then re-run |
| 4 | no GO (`RBT116_GATE_GO` unset) | — |
| 5 | uncommitted changes to `rabbitstew/` or a pinned script | use a clean checkout |
| 6 | `rabbitstew/` or a pinned script is not the emitted one | check out the pinned tree, or re-emit the lanes (`lanes.py emit`) and get the coordinator's ruling |
| 7 | a checkpoint restore failed (anything but "no checkpoint yet") | retry; report if it persists |
| 8 | the screen failed (`W1 FAILS ITS GATE at the screen`), or an evolve run stopped on `DecoyRefused` (`STOPPED FOR A RULING (H16)`) | the gate has failed, or a ruling is needed: report it |
| 9 | G1 failed: no paying rung, or fewer than 12 of 16 PASS | in `gate-a` this is logged and the lane goes on. Later G8, G7 and G9 cells refuse without a paying rung |
| 10 | the pilot has fewer than 8 paying plants per fauna | report it |
| 11 | the readout's verdict is FAIL | `GATE.txt` says which rows |
| 12 | the G8(f) fixture check failed | no gate cell may run (Amendments 2 and 3); report it |
| 13 | no K in 3..9 meets R5-1's rule | stopped for a ruling; `GATE.txt` has the table |

The gate's outputs are in `runs/RBT-116/gate/W1/`. The readout's `GATE.txt`, `g1.txt`, `g6.txt` and `screen.txt` are
the evidence to commit; the JSON and the run directories are bulk, kept in the `ckpt/rbt-116-w1-*` checkpoints.
