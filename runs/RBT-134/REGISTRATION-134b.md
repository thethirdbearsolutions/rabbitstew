# RBT-134b registration amendment (DESIGN-134b.md §9 step 3) and the registered-run runbook

**Status.** This amendment registers RBT-134b's C+ rung and wires the registered run. Nothing in it runs.

The registered run at `MASTER_SEED 20260912` (DESIGN-134b.md §9 step 5) waits for three things:
1. this PR's review;
2. its merge;
3. **the owner's first-hand GO for the registered run.** It spends the 30 CPU-h cap (OWNER-DECISIONS-2026-10-10
   items 7 and 8).

**Blindness.** This amendment was drafted by the RBT-134b fixing session. The validation's outcome reached it only as
the one verdict line below, relayed by the coordinator. It read nothing on `claude/rbt134b-validation`. Everything in
DESIGN-134b.md's Blindness record still holds.

---

## 1. What is registered

**The held-out validation** (DESIGN-134b.md §5) ran under the owner's GO, OWNER-DECISIONS-2026-10-10 item 9 (the L1
path):
- **Code.** It ran at `f0b5690b`, the merge of #576.
- **Seeds.** It used the two held-out seeds, `20261101` and `20261102`.
- **Outputs.** They are committed on `claude/rbt134b-validation` at **`d02e4c70`**.
- **Runs.** All eight runs and `validate134b` exited 0. No ladder climb was needed.

`validate134b` ended:

```
REGISTER C+ = C+L1 ({'pair_event_rate': 5e-05, 'pair_event_scale': 16.0, 'pair_event_zero_bias': True})
```

So:
- **`assay.CPLUS_REGISTERED = "C+L1"`.** This is `pair_event_rate` 5×10⁻⁵, `pair_event_scale` 16 and
  `pair_event_zero_bias` True: r3's plant at the ladder's first rung (DESIGN-134b.md §3).
- **The verdict line is in the code.** `assay.VALIDATION_VERDICT` holds it verbatim. A test checks that it is exactly
  the line `validation_summary` prints for `CONDITIONS_134B["C+L1"]`.
- **`MASTER_SEED` runs are now allowed.** `check_seed_134b` admits B0, C+L1, A0 and P1–P5 there. It still refuses
  C+L2, C+L3 and C−.

**The validation's spend.** `assay.VALIDATION_SPENT_H` is the sum of the validation's cost-ledger `cpu_s` at
`d02e4c70`, rounded up to 0.1 CPU-h. **Value: pending.** A session cleared to read the validation outputs is computing
it, and the coordinator will relay it; this session does not read that branch. Until it is set, the constant is
`None` and the lane refuses (exit 11).
- `spent_134b` counts the constant only when neither held-out ledger is present, as in the registered run's clean
  checkout. When the ledgers are present (the validation's own checkout), it sums them instead and never adds the
  constant as well. A test checks this both ways.
- Without the constant, the stop rule would count the validation's spend as 0 and undercount against the 30 CPU-h
  cap.

**The two held-out seeds are a tuning set. They are never pooled**, with each other or with the registered run
(DESIGN-134b.md §5.3). The registered run at `MASTER_SEED 20260912` is the only test.

**Lane B is unsealed after the owner's GO for the registered run, and before its readout** (DESIGN-134b.md §7, §9
step 4):
- its committed E1, E2 and H1 outputs (`claude/rbt134-runs-B`) are read then, and not earlier;
- nothing in lane B is re-run.

**Everything else is as DESIGN-134b.md registers it.** That covers:
- the never-structured background and its clause;
- I9, I5-S (B0's cited), and the EXCLUSION-FLAG;
- the family and Holm, n, the rungs, and the streams;
- the cost cap and the stop rule.

---

## 2. The registered-run lane (`lanes/lane134b.sh`, `lanes/relay134b.py`)

The lane is the 134b counterpart of lane A, on the same conventions (`lanes/common.sh`, LAUNCH.md):
- a sha-bound GO;
- refusals for a dirty tree, untracked files and outputs from another head;
- atomic outputs, and restart-safe skips;
- all sub-command output to the lane log;
- a RELAY block that carries tokens only.

Lanes A and B, `relay.py` and `common.sh` are unchanged.

**Order (DESIGN.md §13):**

| stage | runs |
|---|---|
| controls | B0, **C+L1**, A0, A0's I5-S swap |
| **the control gate** | `readout134b` over the controls alone → `readout-controls.txt`. The lane stops (exit 8, outputs committed, RELAY printed) unless its VOID list is `none` |
| checks and family | P1 (+ swap), P4 (+ swap), P5; **P2 first** (+ swap), then P3 (+ swap) |
| readout | `readout134b` → `readout.txt` |
| re-signing (untimed, as in lane A) | `resign134b` for B0, C+L1, P1, P4, P5, P2 and P3, capped at 400 per condition. A0 is not re-signed: its k at a16 is bounded at 0 (OWNER-DECISIONS-2026-10-10 item 8) |

Swaps:
- B0's I5-S at `MASTER_SEED` is the RBT-134 diagnosis's EXACT, cited and not re-run (trim iv).
- C+L1 and P5 are not sensor-blind, so they have no swap.

**The cost stop rule** (DESIGN-134b.md §8) runs inside every `run134b` and every `resign134b`.
- **Re-signing** passes the rule first. It is priced at the condition's **actual eligible count**: unflagged arrivals
  with best |a| ≥ a16, capped at 400 (OWNER-DECISIONS-2026-10-10 item 8). A0 is excluded from the reserve held for
  later conditions.
- **The ledger.** Each re-signed robot's CPU enters the cost ledger as it completes.
- **Per robot.** The rule is checked again after each robot, as for chunks.
- **A STOP-COST exits 9.** The lane then commits what it has, prints the RELAY block with status `stopped-cost`, and
  exits 9. Nothing further runs until the owner rules.

**Output branch.** The outputs are `runs/RBT-134/out/134b-20260912/`. They are committed to **`claude/rbt134b-runs`**,
a new branch, so lanes A and B and the validation branch are untouched.

---

## 3. Runbook

### Before launching

- **Host.** Use a host with no RBT-129 Stage-2a lane and no RBT-116 gate lane (LAUNCH.md).
- **Checkout.** Use a clean checkout of the GO sha.
- **The venv, with mujoco pinned in the venv only.** A repo-wide pin waits until SSCAN ends, so `pyproject.toml` is
  unchanged. Put the venv outside the checkout, so the clean-tree check passes:

  ```
  python3 -m venv "$HOME/venv-rbt134b"
  "$HOME/venv-rbt134b/bin/pip" install -e '.[dev]' 'mujoco==3.14.0'
  ```

  The lane refuses any other mujoco (exit 10).
- **The validation's spend** is registered in the code (`assay.VALIDATION_SPENT_H`, §1). Nothing is fetched from
  the validation branch. The lane refuses while the constant is unset (exit 11).
- **Dry run first.** `RBT134_DRY=1` prints the plan and runs nothing.

### Run

```
RBT134B_GO=<the owner's GO sha for the registered run> PYTHON="$HOME/venv-rbt134b/bin/python" \
  bash runs/RBT-134/lanes/lane134b.sh
```

**The GO variable.** `RBT134B_GO` is this lane's GO. Lane A's `RBT134_GO` is not accepted for it. `WORKERS`,
`RBT134_NO_PUSH` and `RBT134_DRY` work as in LAUNCH.md.

### Exit codes

Codes 3–8 are as LAUNCH.md, with exit 8 meaning the run stopped at the control gate. The lane adds:

| code | meaning |
|---|---|
| 9 | STOP-COST: 30 CPU-h would be passed. Outputs so far are committed and the RELAY is printed (status `stopped-cost`); the owner decides |
| 10 | refused: this interpreter's mujoco is not 3.14.0 |
| 11 | refused: the held-out validation's spend (`assay.VALIDATION_SPENT_H`) is not registered |

### Relay: only the RELAY block

`===== RELAY RBT-134b registered run =====` carries:
- the GO sha, the status, and whether the outputs were committed;
- **TOKENS**: each control's id with YES/NO only. The controls are I2, I3, I5-S, I9 and the B0 r3-background prefix,
  from `readout-controls.txt` when stopped, else from `readout.txt`;
- the **ids** on the VOID list, never their text;
- the SHA256 of every output file;
- TIME per stage, rounded to the hour. Re-signing is untimed.

**Never relay** anything LAUNCH.md forbids:
- k, p, Holm or verdict lines;
- background counts, ratios, Katz bounds or EXCLUSION-FLAGs;
- arrival counts other than B0's;
- the §3 tables, re-sign counts, ledger figures, or the figures in a STOP-COST message;
- any line of `readout-controls.txt`, `readout.txt` or the lane log.

**Reading the outputs.** The readout is read only in the readout session, from `claude/rbt134b-runs`. That happens
after lane B is unsealed (§1). C−'s sealed held-out counts may be printed there (DESIGN-134b.md §4.4).

---

## 4. Code and tests (this PR)

- **`runs/RBT-134/assay.py`:**
  - `CPLUS_REGISTERED = "C+L1"` and `VALIDATION_VERDICT`;
  - `REGISTERED_CONDITIONS`;
  - `resign134b`, with `resign_rows` (r3's selection on 134b records) and `_resign_one_134b`;
  - `resign_reserve_h`, which leaves out conditions already re-signed;
  - `VALIDATION_SPENT_H`, counted by `spent_134b` exactly once (§1);
  - `_run_windowed`, the one windowed, ledgered, stop-ruled runner that `run134b` and `resign134b` now share;
  - `STOP_COST_EXIT = 9`.
- **`runs/RBT-134/lanes/lane134b.sh`, `relay134b.py`:** the lane (§2).
- **`tests/test_rbt134b.py`:**
  - the registered rung and the verdict line;
  - the `MASTER_SEED` guard;
  - `resign134b`: r3's selection, the per-robot ledger, the cost rule before and during, and the refusals;
  - STOP-COST's exit status.
- **`tests/test_rbt134b_lane.py`:**
  - the refusals: no GO, lane A's GO, GO not HEAD, dirty tree, mujoco, an unregistered validation spend;
  - DESIGN.md §13's order in the plan;
  - restart skips and stale refusals;
  - the stubbed run (no numbers on the console), the control gate and the STOP-COST stop;
  - crashing checks fail closed;
  - a RELAY block with no numbers, the gate, and completeness.
- **Nothing is touched under `rabbitstew/`, `scripts/` or `runs/RBT-129/`.** `pyproject.toml` is unchanged.
