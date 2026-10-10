# RBT-134 launch runbook (lanes A and B)

The registered design is `DESIGN.md` (r3 plus amendments C1 and I5-a). The code is #541 and #552. The GO and the
relay discipline are the coordinator's (GO-READINESS, 2026-10-05). Nothing here changes `rabbitstew/`, `scripts/` or
`runs/RBT-129/`.

## Before launching

- **Host and checkout.** Use a host with no RBT-129 Stage-2a lane and no RBT-116 gate lane. Use a **clean checkout of
  the GO sha** with a `.[dev]` venv. Each lane refuses a dirty tree, and any untracked file outside
  `runs/RBT-134/out/` (an untracked `.py` beside the scripts would shadow an import).
- **The GO is a sha.** `RBT134_GO` must be the coordinator's GO sha, and it must equal `git rev-parse HEAD`.
- **Separate output branches.** Lanes A and B can run at the same time from one checkout, because their outputs never
  overlap. Each lane commits only its own files, to its own branch, so the two never race on one branch.
- **Dry run first.** `RBT134_DRY=1` prints the plan (what would run and what would be skipped) and runs nothing.

## Run

```
RBT134_GO=<GO sha> bash runs/RBT-134/lanes/laneA.sh                       # Pioneer assay, gate, readout, re-signing
RBT134_GO=<GO sha> bash runs/RBT-134/lanes/laneB.sh "$TMPDIR/rbt134-founders"   # E1, E2 (+ founders), H1
```

**Environment variables:**

| variable | effect |
|---|---|
| `WORKERS` | processes per step (default 4) |
| `PYTHON` | interpreter (default `python3`) |
| `RBT134_NO_PUSH=1` | skips the output commit |
| `RBT134_DRY=1` | prints the plan and runs nothing |

**What each lane runs:**

| lane | order | output branch | estimate |
|---|---|---|---|
| A | B0, C+, A0 (each `assay.py run … --go`); **the control gate**; P1, P4, P5, **P2**, P3; then `readout`, then `resign` (cap 400) | `claude/rbt134-runs-A` | about 7–10 CPU-h, plus up to about 5 for re-signing |
| B | `e1_parity.py --go`; founders for 10 seeds (scratch path); E2 for B0, A0, P1–P5 × 10 seeds, plus summaries; H1 for B0, A0, P1–P4, plus readout | `claude/rbt134-runs-B` | about 5.5 CPU-h |

**The control gate (DESIGN.md 13 step 3: I1–I7 must pass before step 4).** After B0, C+ and A0, lane A runs the
registered readout over the controls alone into `out/readout-controls.txt`. `relay.py gate` reads only its VOID list.
Unless that list is `none`, the lane stops: it commits what it has, prints the RELAY block (status
`stopped-at-control-gate`, with the VOID ids) and exits 8. The checks and the family do not run.

**Restarting.** Re-running a lane is safe, and nothing from another head or of unknown provenance is ever accepted:
- **JSON outputs** (assay, H1) are written atomically. One is skipped only if it is the file's own condition, covers
  both pools at the lane's n (for the assay, also n_bg and the condition's registered fields) and records this head.
  A JSON that records another head, or none, refuses the run (exit 5). Anything else is re-run.
- **Text outputs** are written to `FILE.tmp`, renamed on success, then marked with the head in `FILE.head`. A text
  output is skipped only if `FILE.head` is this head. A file from another head, or one without its mark, refuses the
  run (exit 5): move it aside.
- **Founders** in the scratch path are reused only if `SHA256SUMS`'s digest is RBT-106's committed one for that seed
  and every file it lists hashes as listed. Otherwise the directory is removed and rebuilt (digest-checked).
- `readout-controls.txt`, `readout.txt` and `h1-readout.txt` are always regenerated.

**The console.** Every sub-command's stdout and stderr go to `out/lane-A.log` or `out/lane-B.log`, which is committed
with the outputs. The console shows only `run X`, `skip X (complete)`, `FAILED: X`, refusals and the RELAY block.

## Exit codes

| code | meaning |
|---|---|
| 0 | done: outputs committed (or `NOT COMMITTED` under `RBT134_NO_PUSH=1`), RELAY printed |
| 3 | refused: `RBT134_GO` not set |
| 4 | refused: dirty tree, or an untracked file outside `runs/RBT-134/out/` |
| 5 | refused: `RBT134_GO` is not HEAD, or an existing output was not written at this head |
| 6 | a sub-command failed (named on stderr, output in the lane log); re-run after fixing |
| 7 | an output is missing, or the output commit or push failed (outputs are still under `runs/RBT-134/out/`) |
| 8 | lane A stopped at the control gate: outputs committed, RELAY printed |

## Relay: only the RELAY block

Each lane ends with a `===== RELAY RBT-134 lane X =====` block. **That block, plus the exit code, is all the runner
relays.**

| section | contents |
|---|---|
| `head` | the GO sha |
| `status` | `done`, or `stopped-at-control-gate` |
| `COMMITTED` | `COMMITTED yes`, or `NOT COMMITTED` |
| `TOKENS` (lane A) | each control's id with its YES/NO tokens: I1–I7 per condition, and the B0 background prefix (all / unflagged); from `readout-controls.txt` when stopped at the gate |
| `VOID` (lane A) | `none`, or the **ids** of the VOID entries (never their text) |
| `TOKENS` (lane B) | `E1-B0-equals-parity.txt` and `E2-B0-equals-RBT-112-tables`, YES/NO |
| `SHA256` | one line per output file |
| `TIME` | per stage, wall and child CPU **rounded to the hour** (a finer time could encode a count, e.g. of re-signed arrivals) |

**Never relay:**
- any k, p, Holm or verdict line;
- background rates or ratios, Katz bounds, or ceiling results;
- arrival counts other than B0's;
- the §3 tables;
- re-sign counts;
- H1 arm counts or the STRUCTURE-BOUND line;
- E1, E2 or u(8) numbers for non-B0 conditions;
- any line of `readout.txt`, `readout-controls.txt`, `h1-readout.txt`, `e1.txt`, `e2-*.txt` or the lane logs.

The readout is read only in the readout session, from the committed output branches.

## Gated, not run by these lanes

- **E3** (the RBT-113 selection response) waits for Stage 2a to end, because it needs a `rabbitstew/` change (NOTE 17),
  and for a carried candidate.
- **H2** (the `steer.py` stage) waits for H1 arrivals and a committed W1 battery (DESIGN.md 5.3).
