# RBT-129 K3 calibration: the final decision (coordinator, 2026-09-28 19:52)

**Verdict: the perception layer is UNREADABLE at a = 6 at RBT-129's calibration cells. Reading, as pre-registered (S-2): "the perception layer is unreadable at a = 6: no seeable holistic control". No probe leg launches.**

Under S-2 this is **not** a reason to change G8(c)'s layout, its hosts, `c_layout`, the carrying rule or a = 6. Any such change after this output is data-driven, and is refused (#478 comment 5874231890; DESIGN §12, the 16:33 amendment, #483).

The decision applies DESIGN §12's registered rule mechanically:
- the 12:52 ruling on #471 (#472), with S1 (per-cell reading) and S2 (conditional second stage);
- the screen rule (c), adopted on #478 and merged in #478 and #486.

## The runs

| stage | lane | commit | branches |
|---|---|---|---|
| 1: 16 draws | `calibrate-c` (#486) | `2eeaec8` | `ckpt/rbt-129-calibration-c-c0-p030-{PW,HP}-G` (`a431da2`, `4b2acdc`) |
| 2: confirmation, 32 draws per plant (#471 S2) | `calibrate-c-s2` (#486) | `2eeaec8` | `ckpt/rbt-129-calibration-c-s2-c0-p030-{PW,HP}-G` (`eb345d2`, `715ae24`) |

**The screen, stage 1 (descriptive).**
- (c) admitted 64 of 64 draws at both cells. "At least half" would have admitted 3 at PW-G and 10 at HP-G.
- Per-control P(eat ≥ 1):
  - the designed G8(a) plants: 0.33–0.97 at PW-G and 0.42–1.00 at HP-G;
  - the **holistic G8(c) plants: 0.00–0.05 at both cells.**
- Under S-2 these figures are descriptive only. They are never used to re-select plants.

## Step 1: measured SEEN, 16 draws

| cell | (a) | (c) | bar |
|---|---|---|---|
| c0-p030-PW-G | 1 of 8 (0.125) | 0 of 8 | 0.45 |
| c0-p030-HP-G | 2 of 8 (0.250) | 0 of 8 | 0.45 |

The first branch FAILS: measured SEEN is below 0.45 somewhere.

## Step 2: projection from stage 1

The full output is in `k3_projection_stage1.txt`.

| cell | projected share at n 16 / 32 / 64, (a) | same, (c) | reading |
|---|---|---|---|
| PW-G | 0.394 / 0.496 / 0.588 | 0.014 / 0.031 / 0.077 | unreadable |
| HP-G | 0.320 / 0.429 / 0.535 | 0.000 / 0.000 / 0.000 | unreadable |

The pick is UNREADABLE, so **the S2 second stage was due.**

## Step 3: the pooled re-projection, 32 draws per plant (FINAL)

The full output is in `k3_projection_pooled_final.txt`.

| cell | projected share at n 16 / 32 / 64, (a) | same, (c) | reading |
|---|---|---|---|
| PW-G | 0.304 / 0.442 / 0.547 | 0.030 / 0.071 / 0.127 | unreadable |
| HP-G | 0.265 / 0.369 / 0.466 | 0.002 / 0.003 / 0.006 | unreadable |

**RULE (second stage, final): UNREADABLE at a = 6.** 64 draws do not reach 0.6 at every cell, so no probe leg runs.

## Checks the coordinator made

**Stage 2 used its own confirmation draws.**
- Stage-2 (16-draw) records are identical between the two runs, as expected, because the seasons are deterministic.
- Every (c) plant carries a `k3_confirm` battery at both cells (8 of 8).
- (a) plants: 7 of 8 at PW-G and 6 of 8 at HP-G carry `k3_confirm`. The others had already reached stage 3 in the call itself and carry its own `confirm`, which `k3_projection` reads (`planters.py` line 332).
- The confirmation-battery runs added no SEEN change, as the design intends.

**Robustness.**
- The verdict is driven by (c): its projected share is ≤ 0.13 at n 64 at both cells.
- (a) also misses 0.6 at both cells: 0.547 and 0.466.

## What it means

- At RBT-129's calibration cells, the registered perception probe cannot see a holistic G8(c) control.
- The O1 holistic plants carrying two single-instance noses almost never eat within the probe bout (P ≤ 0.05).
- Holistic PAYS and the perception layer at these points are therefore not readable with the registered instrument.
- **This is not a finding that holistic bodies cannot perceive.** It says the registered probe cannot measure it here.
