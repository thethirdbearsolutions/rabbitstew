# RBT-110, C4null: C4's refund/response split against its missing null (cull20, flat ground)

Analyst readout under RBT-110's pre-registration. No new arm was run. Everything below is simulated from restored
bulk (README rule 6); no table was read from a checkpoint.

| file | role |
|---|---|
| `probe_split.py` | the harness: `runs/RBT-101/readout-adversary/probe_refund.py`, adding only the cull20 population and the read points 50 and 190. Committed (`8509089`; check fix `b7740b5`) before any read |
| `check.txt` | harness check: seed 801, season T − 1 = 360 of the baseline, re-simulated bout for bout |
| `split.txt` | the reads: r = 110 (primary; opens with the adversary's lines reproduced), then 50 and 190 |

## Setup

- `uname -m` x86_64; `pytest -q`: 289 passed.
- Restored with `scripts/durable.sh restore`: `ckpt/rbt-90-SEED` (base), `ckpt/rbt-101-shift-SEED` (shift) and
  `ckpt/rbt-92-cull20-SEED` (cull20), ten seeds each, 30 ckpts. None warned of a partial snapshot.
- **Season coverage (`state.json`; seasons < N are complete):**
  - 600 for every ckpt except shift-804 (548), shift-805 (599) and cull20-806 (565).
  - The lineage past N is a partial season, and the script treats it as not covered.
  - **Seed 804 is not covered at T + 190 = 548 in its shift arm.** It is left out of every r = 190 value that needs
    shift (n = 9 there), and nothing is substituted. Everything else is covered at every read point.
- No fauna is extinct at any read point in any arm, so no other seed is excluded. n = 10 per fauna except as above.

## Harness

- **Reproduction:** at r = 110, the adversary's C0, REFUND, RESPONSE and TOTAL lines (`probe_refund.txt`) came out
  **identical to the last digit**, all 18 simulated lines. Only the header lines differ.
- **Check** (`check.txt`): 30/30 recorded bouts of seed 801, season 360, reproduce the recorded gain to 4 decimals.
- **One deviation from the adversary's `--check`, disclosed:**
  - On seed 801 the adversary's code raised `KeyError`. Robot he663 played season 360 in its cohort, but it aged out
    at the season's end, and `lineage.jsonl` has no row for a robot at the season it dies in.
  - The adapted check prints such bouts as "no record" and counts them (2 of 32). It still simulates them in their
    groups, so every recorded groupmate's bout is tested.
  - This is a gap in what was recorded, not a harness mismatch.
- **Inherited caveat (the populations are binding, so they were not changed):**
  - The adversary's "alive at s" means has a lineage row at s with `food`. It therefore omits the robots that played
    s and died at its end: 0–6 of 120 per arm and seed at T + 110 (base 111–118, shift 114–118, cull20 114–120 of 120).
  - The omission is of the same kind in every arm.

## Results (mean gain per robot-bout, simulated; D = 4; paired = co-evolved − designed)

**Primary, r = 110** (n = 10):

| | designed | co-evolved | paired |
|---|---|---|---|
| REFUND (base, flat − random) | +0.94 [+0.82, +1.07] | +0.22 [+0.16, +0.28] | −0.72 [−0.89, −0.56] |
| RESPONSE (shift − base, flat) | −0.22 [−0.45, +0.00], 2/10 | +0.05 [−0.13, +0.23], 7/10 | **+0.27 [+0.05, +0.49], 8/10, p1 = 0.010** |
| RESPONSE_null (cull20 − base, flat) | −0.02 [−0.26, +0.21], 4/10 | **+0.18 [+0.03, +0.33], 8/10** | **+0.20 [+0.00, +0.40], 7/10, p1 = 0.024** |
| RESPONSE net of null (shift − cull20) | −0.20 [−0.45, +0.05], 5/10, p1(<0) = 0.054 | −0.13 [−0.27, +0.02], 3/10 | **+0.07 [−0.18, +0.33], 6/10, p1 = 0.27, MDE80 0.31** |

**Verdicts at r = 110.** The one-sided p are unadjusted; the Holm step across challenges is the coordinator's.
- Paired RESPONSE: **SUPPORTED** on the unadjusted p = 0.0103 (mean > 0).
- Paired RESPONSE net of the null: **NOT DECIDED** (p = 0.27; MDE at 80% power 0.31).
- Designed RESPONSE, H's direction (< 0): p = 0.026. Net of the null: p = 0.054.

**Time course (paired):**

| r | RESPONSE | RESPONSE_null | net of null |
|---|---|---|---|
| 50 | −0.02 [−0.24, +0.19], 5/10 | +0.01 [−0.24, +0.26] | −0.04 [−0.21, +0.14] |
| 110 | +0.27 [+0.05, +0.49], 8/10 | +0.20 [+0.00, +0.40] | +0.07 [−0.18, +0.33] |
| 190 (n = 9; 804 not covered) | +0.42 [+0.16, +0.69], 9/9, p1 = 0.003 | +0.09 [−0.24, +0.42] (n = 10) | +0.31 [−0.20, +0.82], p1 = 0.10, MDE80 0.61 |

**Designed RESPONSE over time:**
- r = 50: −0.06.
- r = 110: −0.22.
- r = 190: −0.34 [−0.50, −0.18], 0/9, p1 = 0.0006. Its null stays near 0: +0.07, −0.02, −0.04.
- Net of the null: −0.13 [−0.23, −0.03] (p1 = 0.008), then −0.20, then −0.29 (p1 = 0.059).

**Co-evolved RESPONSE over time:** −0.08, +0.05, +0.08, never resolved. Its null is +0.09, +0.18, +0.04.

## What this says, plainly

1. **At the primary read, turnover alone reproduces most of C4's +0.27.**
   - Culling 20 of each fauna on unchanged ground, then reading on flat ground, gives a paired "response" of +0.20.
   - That null is carried by the co-evolved side (+0.18), where C4's own co-evolved RESPONSE is only +0.05.
   - Net of the null, the paired effect at T + 110 is +0.07, not resolved (MDE 0.31).
   - As a reference for C4's +0.27, **the null does not let the r = 110 finding stand as a non-arithmetic response
     to the challenge.**
2. **The designed side's negative RESPONSE is not turnover, and it grows.**
   - Its null is about 0 at every read point, while the RESPONSE deepens: −0.06, then −0.22, then −0.34 (9/9
     negative at r = 190).
   - Net of the null it is negative at every read point: p1 0.008 at r = 50, 0.054 at r = 110, 0.059 at r = 190.
   - Of H's two parts, the designed part survives the null; the paired part does not at r = 110.
3. **At r = 190 the paired RESPONSE is larger (+0.42, 9/9) and the null has faded (+0.09).**
   - The net value, +0.31, is not resolved: the null's per-seed sd at r = 190 is 0.46, and seed 801's null is −0.93.
   - This is a secondary read and is reported, not promoted.

**For the coordinator:**
- C4's one-sided p at r = 110 for the paired RESPONSE is **0.0103**, and 0.2687 net of the null.
- n = 10 per fauna at r = 50 and r = 110; n = 9 at r = 190 (seed 804's shift arm is not covered).
- No seed was excluded for extinction.
