# RBT-110 C2: the refund/response split on dearer work (RBT-99, work cost 0.03 → 0.08)

Analyst readout for challenge C2 under RBT-110's pre-registration (binding; filed 20:45 UTC). It is analysis only,
from existing checkpoints, and adds no new arm.

## Headline

| T + 110 (primary) | mean | 95% t CI | positive | one-sided p (H's direction) | n |
|---|---|---|---|---|---|
| **paired RESPONSE** (co-evolved − designed), H: > 0 | **−0.229** | [−0.564, +0.105] | 2/7 | **0.928** | 7 |
| paired RESPONSE net of the cull20 null | −0.298 | [−0.447, −0.148] | 0/7 | 0.999 | 7 |
| designed RESPONSE, H: < 0 | **+0.571** | [+0.429, +0.712] | 7/7 | 1.000 | 7 |
| co-evolved RESPONSE | +0.278 | [+0.101, +0.455] | 9/10 | — | 10 |
| designed RESPONSE_null (cull20 − base) | −0.035 | [−0.190, +0.119] | 4/10 | — | 10 |
| co-evolved RESPONSE_null | +0.111 | [−0.026, +0.248] | 6/10 | — | 10 |
| paired RESPONSE_null | +0.146 | [−0.040, +0.333] | 7/10 | — | 10 |
| REFUND designed / co-evolved / paired | −0.968 / −0.263 / +0.706 | | 0/10, 0/10, 10/10 | | 10 |

- **Verdict for C2: NOT DECIDED.** The unadjusted one-sided p is 0.928, so no Holm step can make it SUPPORTED. The
  two-sided CI does not lie entirely below 0, so the registered rule does not make it CONTRADICTED either. The MDE
  at 80% power from the observed per-seed sd is **0.389** (one-sided 5%), or 0.458 (two-sided).
- **The point estimate runs against H.** Every secondary statistic runs against it too:
  - The designed RESPONSE is positive on 7/7 seeds, not negative.
  - Net of the null, the paired RESPONSE lies entirely below 0 (0/7).
  - The paired RESPONSE is negative at every read point: −0.309 at T+50 (n = 10, 1/10), −0.229 at T+110 and −0.128
    at T+190.
  - The registered verdict is on the un-netted statistic, and it is NOT DECIDED. Holm across C1–C3 is left to the
    coordinator. The one-sided p to feed it is **0.9280**.
- **Against C4:** C4's post-hoc +0.27 lies outside C2's 95% CI, which is given here for the coordinator's pooled
  comparison.

## What the split says on C2 (description, not verdict)

- **The refund is a pure price.** Work cost enters only the pricing (`simulation.py`: items × value − work_cost ×
  kJ / 1000), so both worlds share their trajectories. The REFUND is −0.05 × kJ, paid **3.7× more by the wheels**:
  - designed −0.968, co-evolved −0.263, paired +0.706 (10/10);
  - the onset population C0 pays the same, −0.943 and −0.266.
- **The designed fauna's post-onset survivors cut their work bill.** Their RESPONSE is +0.571 on the new world but
  only +0.096 [−0.101, +0.293] on the old one. The same gaits are nearly no better at the old price, and about 5/6
  of their gain on the new world is work not done.
- **The co-evolved RESPONSE (+0.278) is mostly not about price.** It is +0.222 on the old world too. Part of it is
  turnover: the co-evolved cull20 null is +0.111, and net of that null +0.167 remains (9/10).
- **Survivor conditioning (lesson 7).** The designed fauna is extinct in the shift arm at T+110 and T+190 on seeds
  **806, 807 and 2**, which are excluded from every designed and paired RESPONSE there (n = 7).
  - Those are the seeds where the designed fauna did worst, so the designed RESPONSE is conditional on survival and
    flatters the designed body.
  - At T+50 all ten seeds are present (806 with 6 robots, 807 with 43, 2 with 22). There the paired RESPONSE is
    −0.309 [−0.573, −0.045] on n = 10.
  - The three later-extinct seeds do not all go against H: 807 is −0.167 and 2 is −0.178, but 806 is +0.395, and
    806's designed fauna is down to 6 robots.

## Arms, coverage and exclusions

- **Restored bulk** (README rule 6), into scratch outside the repo, with `scripts/durable.sh restore`:
  - `ckpt/rbt-90-SEED`: 10/10 at 600/600 (the baseline);
  - `ckpt/rbt-99-shift-SEED`: 10/10 at 600/600;
  - `ckpt/rbt-92-cull20-SEED`: 9/10 at 600/600, and **806 at 565/600**.
- **Coverage.** 806's T+190 is season 555 < 565, and the script asserts coverage for every read. So every read
  point is covered on every seed, and nothing was substituted.
- **Configs.** Each shift config differs from its baseline only by `shift_at = T` and `shift = work-cost=0.08`, and
  each cull20 config only by `cull_at = T` and `cull = holistic=20,conventional=20`. All sim blocks are identical,
  with a work cost of 0.03.
- **T** comes from `runs/RBT-92/onset.txt`, as in RBT-99.
- **Excluded seeds:**
  - 806, 807 and 2 are excluded from the designed and paired RESPONSE, and from its net, at T+110 and T+190. The
    reason is that the designed fauna is extinct in the shift arm at the read point.
  - No other seed is excluded from anything, and no base or cull20 fauna is extinct at any read point.
- **n per fauna:**

  | read point | co-evolved | designed | paired |
  |---|---|---|---|
  | T+50 | 10 | 10 | 10 |
  | T+110 | 10 | 7 | 7 |
  | T+190 | 10 | 7 | 7 |

  The null is n = 10 throughout.

## Harness

- **Script.** `probe_split.py` was committed (`e51331f`) before any read. It is `probe_refund.py` with only the
  world difference changed, from flat vs random terrain to work cost 0.08 vs 0.03 on the baseline's random terrain
  (terrain seed = draw). Two populations were added, cull20 and the three read points.
- **Kept identical to the adversary's:**
  - the draws, D = 4 from `random.Random("RBT-101 refund SEED")`;
  - the group shuffles (`"SEED POP KIND DRAW"`), in groups of four;
  - the configs and `run_group`.
- **`check.txt`:** baseline seed 3, season T − 1 = 351, reproduces the recorded gains bout for bout, **32/32** to
  4 decimals.
- **`check_shift.txt`:** shift arm seed 3, season T + 1 = 353, re-simulated at work cost 0.08, is also **32/32**.
  So the new world's pricing is the arm's own.
- **Run size.** The run simulated 22,552 group bouts. MuJoCo printed 120 "simulation is unstable" warnings, as the
  ecology's own seasons can. The check seasons reproduce exactly, so these warnings are part of the recorded
  dynamics, not of the probe.

## Files

- `probe_split.py`: the probe.
- `check.txt`, `check_shift.txt`: the harness checks.
- `split.txt`: the full readout. It has per-seed values for every quantity at r = 110, 50 and 190, plus MDEs and the
  verdict line.

Reproduce with:

```
python runs/RBT-110/C2/probe_split.py BULK --check 3
python runs/RBT-110/C2/probe_split.py BULK 4
```

BULK holds `base-SEED`, `shift-SEED` and `cull20-SEED`. The read takes about 80 minutes on 4 cores.
