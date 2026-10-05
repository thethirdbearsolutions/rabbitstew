# RBT-134 launch runbook (lanes A and B)

The registered design is `DESIGN.md` (r3 plus amendments C1 and I5-a). The code is #541 and #552. The GO and the
relay discipline are the coordinator's (GO-READINESS, 2026-10-05). Nothing here changes `rabbitstew/`, `scripts/` or
`runs/RBT-129/`.

## Before launching

- **Host and checkout.** Use a host with no RBT-129 Stage-2a lane and no RBT-116 gate lane. Use a **clean checkout of
  the GO sha** with a `.[dev]` venv. Each lane refuses a dirty tree.
- **Separate output branches.** Lanes A and B can run at the same time from one checkout, because their outputs never
  overlap. Each lane commits only its own files, to its own branch, so the two never race on one branch.
- **Dry run first.** `RBT134_DRY=1` prints the plan (what would run and what would be skipped) and runs nothing.

## Run

```
RBT134_GO=1 bash runs/RBT-134/lanes/laneA.sh                       # Pioneer assay, readout, re-signing
RBT134_GO=1 bash runs/RBT-134/lanes/laneB.sh "$TMPDIR/rbt134-founders"   # E1, E2 (+ founders), H1
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
| A | B0, C+, A0, P1, P4, P5, **P2**, P3 (each `assay.py run … --go`), then `readout`, then `resign` (cap 400) | `claude/rbt134-runs-A` | about 7–10 CPU-h, plus up to about 5 for re-signing |
| B | `e1_parity.py --go`; founders for 10 seeds (scratch path); E2 for B0, A0, P1–P5 × 10 seeds, plus summaries; H1 for B0, A0, P1–P4, plus readout | `claude/rbt134-runs-B` | about 5.5 CPU-h |

**Restarting.** Re-running a lane is safe:
- outputs that are already complete are skipped;
- a JSON written at another head refuses the run (exit 5);
- text outputs are written to `FILE.tmp` and renamed only on success.

## Exit codes

| code | meaning |
|---|---|
| 0 | done: outputs committed, RELAY printed |
| 3 | refused: `RBT134_GO=1` not set |
| 4 | refused: dirty tree |
| 5 | refused: an existing output was written at another head |
| 6 | a sub-command failed (named on stderr); re-run after fixing |
| 7 | the output commit or push failed (outputs are still under `runs/RBT-134/out/`) |

## Relay: only the RELAY block

Each lane ends with a `===== RELAY RBT-134 lane X =====` block. **That block, plus the exit code, is all the runner
relays.**

| section | contents |
|---|---|
| `head` | the GO sha |
| `TOKENS` (lane A) | each control's id with its YES/NO tokens: I1–I7 per condition, and the B0 background prefix (all / unflagged) |
| `VOID` (lane A) | `none`, or the **ids** of the VOID entries (never their text) |
| `TOKENS` (lane B) | `E1-B0-equals-parity.txt` and `E2-B0-equals-RBT-112-tables`, YES/NO |
| `SHA256` | one line per output file |
| `TIME` | wall seconds, and the children's CPU user/sys |

**Never relay:**
- any k, p, Holm or verdict line;
- background rates or ratios, Katz bounds, or ceiling results;
- arrival counts other than B0's;
- the §3 tables;
- re-sign counts;
- H1 arm counts or the STRUCTURE-BOUND line;
- E1, E2 or u(8) numbers for non-B0 conditions;
- any line of `readout.txt`, `h1-readout.txt`, `e1.txt` or `e2-*.txt` itself.

The readout is read only in the readout session, from the committed output branches.

## Gated, not run by these lanes

- **E3** (the RBT-113 selection response) waits for Stage 2a to end, because it needs a `rabbitstew/` change (NOTE 17),
  and for a carried candidate.
- **H2** (the `steer.py` stage) waits for H1 arrivals and a committed W1 battery (DESIGN.md 5.3).
