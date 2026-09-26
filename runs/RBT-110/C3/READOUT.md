# RBT-110 C3 (scarce food, RBT-100): refund/response split, readout

Analyst: RBT-110 C3. Pre-registration: RBT-110 (binding). Coordinator: session_01WKXr6PgNkscGhVc7Bzth9k.

## What was run

- **Harness:** `probe_split.py` is `runs/RBT-101/readout-adversary/probe_refund.py` with one change, the world. The new world has 6 food items and the old world has 12, both on random terrain with terrain seed = the draw. Everything else is the adversary's:
  - populations, and the group-of-four shuffle stream `"SEED POP KIND DRAW"`;
  - D = 4 draws from `"RBT-101 refund SEED"`, with the same start seeds across populations and worlds.
  - The script was committed and pushed (`ca77095`) before any read.
- **Harness check** (`check.txt`, `check_new.txt`), run before the read:
  - RBT-90 baseline, seed 1, season T − 1 = 381, 12 items: **32/32** bouts reproduce the recorded gain to 4 decimals.
  - Additional check: RBT-100 shift arm, seed 1, season T + 110 = 492, under this script's own 6-item world: **18/18**. So the new world is the ecology's own.
- **Bulk** was restored with `scripts/durable.sh restore` into scratch, outside the repo (README rule 6; no table was read from a checkpoint):
  - `ckpt/rbt-90-SEED` (base): all 600/600;
  - `ckpt/rbt-100-shift-SEED` (shift): all 600/600;
  - `ckpt/rbt-92-cull20-SEED` (null): 600/600, except 806 at 565.
  - Every read season (at most T + 190 = 572, on seed 1) is covered by every run. For 806's cull20, T + 190 = 555 < 565. **No seed is short at any read point.**
- **Configs:** every run's `sim` config is identical to the base's (asserted). Each shift arm's `shift_at` equals the onset T in `runs/RBT-92/onset.txt`, and each cull20 arm's `cull_at` equals T as well.
- **Scale:** 21,856 group bouts, 4 workers, about 75 min.
- **MuJoCo instability warnings:** 122 "simulation is unstable" warnings over about 87k robot-bouts. They were left as the simulator scores them, as in the ecology.

## Primary (r = 110): paired RESPONSE (co-evolved − designed), 6 items

| | n | mean | 95% CI | pos | one-sided p (H: > 0) | MDE 80%, α 0.05 / 0.05/3 |
|---|---|---|---|---|---|---|
| **paired RESPONSE** | 8 | **−0.018** | [−0.332, +0.297] | 3/8 | **0.551** | 0.371 / 0.471 |
| paired RESPONSE net of null | 8 | −0.070 | [−0.413, +0.274] | 2/8 | 0.677 | 0.405 / 0.514 |

- **Per seed** (801, 804, 805, 806, 807, 1, 2, 3, 4, 7): +0.363, −0.133, +0.467, n/a, −0.149, −0.750, +0.179, n/a, −0.092, −0.026.
- **Excluded:** 806 and 3, because the designed fauna is extinct in the shift arm at T + 110 (0 alive). No other seed is excluded.
- **n per fauna:**
  - co-evolved RESPONSE 10/10;
  - designed RESPONSE 8/10;
  - RESPONSE_null 10/10 for both faunas.
- **Verdict for C3: NOT DECIDED.**
  - The one-sided p of 0.551 is above 0.05 at every Holm step, so C3 is not SUPPORTED whatever the coordinator's Holm order.
  - The two-sided CI includes 0, so it is not CONTRADICTED.
  - The MDE at 80% power is 0.37 (α 0.05) to 0.47 (α 0.05/3), larger than C4's +0.27.
  - The result is conditional on the designed fauna's survival (lesson 7).
  - Holm across C1–C3 is left to the coordinator.

## Secondary

At r = 110:

| | n | mean | 95% CI | pos |
|---|---|---|---|---|
| co-evolved RESPONSE | 10 | **+0.194** | [+0.105, +0.284] | 9/10 (one-sided p 0.0004) |
| co-evolved RESPONSE net of null | 10 | +0.157 | [+0.072, +0.243] | 9/10 |
| designed RESPONSE | 8 | **+0.199** | [−0.122, +0.521] | 6/8 (H says < 0: one-sided p 0.91) |
| designed RESPONSE net of null | 8 | +0.213 | [−0.100, +0.525] | 6/8 |
| RESPONSE_null, co-evolved / designed | 10 / 10 | +0.037 / −0.022 | [−0.027, +0.101] / [−0.073, +0.030] | |
| REFUND, co-evolved / designed | 10 / 10 | −0.578 / −0.773 | | 0/10 each |
| paired REFUND | 10 | +0.195 | [+0.054, +0.336] | 8/10 |

**Time course of the paired RESPONSE** (both faunas present):

| r | n | mean | 95% CI | pos |
|---|---|---|---|---|
| 50 | 10 | −0.034 | [−0.150, +0.082] | 4/10 |
| 110 | 8 | −0.018 | [−0.332, +0.297] | 3/8 |
| 190 | 5 | +0.073 | [−0.045, +0.191] | 4/5 |

- Excluded at r = 190: 801, 805, 806, 1 and 3, where the designed fauna is extinct in the shift arm.
- **Co-evolved RESPONSE:** +0.086 at r = 50 (8/10), +0.194 at r = 110 (9/10) and +0.178 at r = 190 (10/10).
- **Designed RESPONSE:** +0.120 at r = 50 (8/10), +0.199 at r = 110 (6/8) and +0.099 at r = 190 (5/5, survivors only).

## Reading

- **H's second half fails on C3.** H has the designed RESPONSE negative. Here both faunas' post-onset populations forage the 6-item world better than their no-event contemporaries:
  - co-evolved +0.19, resolved and well clear of its null (+0.04);
  - designed +0.20, not resolved.
- **The paired contrast is about zero** (−0.02), with a very wide CI. That width is driven by the designed side.
- **The refund:** scarce food costs the designed baseline more than the co-evolved one (paired REFUND +0.20), so the arithmetic favours the co-evolved body.
- **Unlike C4, the response is not the part that separates the faunas.**

## Caveats (for the readout adversary)

1. **The designed shift populations are tiny on several seeds at r = 110:**

   | seed | 805 | 1 | 801 | 2 | 4 |
   |---|---|---|---|---|---|
   | designed alive | 1 | 2 | 5 | 6 | 15 |

   - The adversary's harness plays groups as the population allows ("groups as run"). A population of 1–2 therefore forages in a group of 1–2 against the base's groups of 4, which means less competition for the 6 items.
   - The largest designed RESPONSE, seed 1's +1.055 (2 alive), and the most negative paired value, seed 1's −0.750, are likely group-size effects rather than gait differences.
   - The pre-registration excludes only the extinct case, so these seeds stay in and the verdict above is unchanged.
   - **Post hoc and labelled as such (not a verdict input):** on the four seeds whose designed shift population is ≥ 12 (RBT-89's floor) at T + 110, the paired RESPONSE is 804 −0.133, 807 −0.149, 4 −0.092 and 7 −0.026, all negative. The positive paired values come from the seeds with 1–6 designed alive.
2. **Survivor conditioning** (lesson 7). The designed fauna is extinct on 2/10 seeds at T + 110 and 5/10 at T + 190, so the designed RESPONSE is a response of survivors.
3. **Drift:** the refund's drift against C0 is small: co-evolved +0.03 and designed −0.04 at r = 110.

## Files

- `probe_split.py`: the script.
- `check.txt`, `check_new.txt`: the harness checks.
- `split.txt`: the full output (stdout), including the population sizes per seed, fauna and read point.
