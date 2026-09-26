# RBT-97 adversary, round 1: §1 re-derived, and the phantom instrument attacked before it runs

Named adversary: a fresh cloud session, redirected by the coordinator at 12:34 UTC on 2026-09-26.
Branch `results/RBT-97-adversary`, cut from integration `1cedfb5`. No simulation was run for this
round; everything below comes from committed files.

| role | file |
|---|---|
| independent re-derivation of §1 | `runs/RBT-97/adversary_resign.py` → `adversary_resign.txt` |
| resolvability of the 25%/75% band | `runs/RBT-97/adversary_band.py` → `adversary_band.txt` |
| `mechanism.py`'s verdict line against the pre-registered rule | `runs/RBT-97/adversary_verdict.py` → `adversary_verdict.txt` |

Inputs: `docs/artifacts/RBT-67/{w4b,p801}.json`, which hold the per-seed differences at seeds
7000–7063, and the direction readouts `docs/runs/RBT-69-travel-direction.txt` and
`docs/artifacts/RBT-67/travel_direction_{w4b,p801}.txt`. The instrument under attack is
`runs/RBT-97/mechanism.py` at `39cddff` on `origin/results/RBT-97-mechanism`, and
`scripts/compass_mechanism.py`.

## 1. §1 re-derived: it stands

The script was written before reading the author's `resign_rbt67.py`.

- **All 98 per-robot deltas reproduce exactly**: 14 robots × 7 rungs, 0 of 98 mismatches against
  `docs/artifacts/RBT-97-rbt67-resigned.txt`. Every per-seed list reproduces its stored delta.
- **The pooled means reproduce to the third decimal.** Correctly signed robots (12): +0.674,
  +1.930, +2.975, +3.743, +4.111, +4.103, +4.466. Inverted robots (2): −1.430 up to −2.211.
- **The sign assignment is right.** On P-801 two independent direction readouts (RBT-69's and
  RBT-67's) agree on every robot, and g100 and g400 are the only backward drivers.
- **The split was not chosen after seeing the numbers.** RBT-67's pre-registration (09-14 02:53)
  named g100 and g400 as losers at confidence 0.80, from PR #11's direction readout of 02:42.
  RBT-67's ladder ran after both. The author's per-robot split is that pre-registered split, so
  this counts in the author's favour.

Four qualifications. None of them reverses §1.

1. **The CI method is narrower than a t-interval.** Taken over 12 robots, the percentile bootstrap
   gives [+0.438, +0.967] at a = 32. The t-interval (df 11) gives [+0.358, +0.991]. Both exclude
   zero at every rung. Per population, on the correctly signed robots, t-intervals:
   - W4b a = 32: +0.435 [+0.261, +0.610]
   - P-801 a = 32: +1.009 [+0.236, +1.783]
2. **"12/12 better" counts point estimates.** The robots whose own interval over 64 seeds sits
   above zero number **6/12 at a = 32** and 10/12 at a = 64. "Every robot gains at every rung" is
   true of the means. At the lowest rung, half the robots are individually unresolved.
3. **"Fourteen of fourteen robots" is not in RBT-67's data.** RBT-67 shows g100 and g400 losing
   with the wrong sign. It never gave them their own compass. Their gain with the right sign
   exists only in RBT-69's run (+3.734, +1.109), at a = 64 only.
4. **§1 covers neither the ticket's null rung nor its motif.**
   - RBT-67 has no a = 16 (w = 8) rung, so "including the lowest" means w = 16.
   - RBT-67 installs the direct four-link motif in the runtime weights, which the genotype cannot
     represent. RBT-91's 6.87 is the realised response of the **routed** motif, the one drift
     proposes.
   - Routed and direct agree on W4b (`genotype_motif.txt`: +0.277 against +0.246 at w = 16,
     +0.879 against +0.897 at w = 32). **The routed motif has never been measured on P-801.**
   - So "the magnitude drift never reaches demonstrably pays" is shown on W4b. On P-801 it is
     shown only for a circuit drift cannot build.

## 2. The instrument, before it runs

### 2a. The verdict line in `mechanism.py` does not implement the pre-registered gait rule

This is a blocking finding.

- **Pre-registration:** gait effect if phantom retains ≥ 75% *"with its own CI excluding zero"*.
- **Code:** `"GAIT EFFECT" if frac >= 0.75 and (dlo > 0) == (dhi > 0)`, where `[dlo, dhi]` is
  the CI of **motif − phantom**.
- **Consequence:** at full retention motif − phantom is about zero, so this branch needs retention
  to be significantly *different* from 100%.

Scored on synthetic arms built from RBT-67's own P-801 noise, with `mechanism.py`'s statistics:

| true retention | code → GAIT (a = 64 / 384) | pre-registered rule → GAIT |
|---|---|---|
| 0.75 | 0.21 / 0.49 | 0.50 / 0.51 |
| 0.90 | 0.19 / 0.55 | 0.91 / 1.00 |
| **1.00** | **0.17 / 0.16** | **0.99 / 1.00** |

**As written, the arm cannot return the one verdict that would falsify chemotaxis on P-801.** A
pure gait effect reads UNRESOLVED 83–84% of the time. The two rules agree on the food-dependent
side (0.98 / 1.00 at R = 0), so if the prediction is right the bug never shows. That is exactly
why it has to be fixed before the result, not after. The fix is one line: use phantom's own CI,
as registered. The ~17% GAIT at R = 1, where motif − phantom is truly zero, also says a percentile
bootstrap over 5 robots under-covers. A t-interval with df 4 would be the honest term.

### 2b. With per-robot signs, the pre-registered sign control is never computed

- In `--sign per-robot` mode, `correct` is every robot whose sign matches its own direction. That
  is **all seven**, so `inverted` is empty.
- g100 and g400 carry their compass and are **pooled into the claim**.
- The coordinator's condition 2 asked for the inverted robots' phantom column, and prediction 5
  says they lose at both rungs. Neither can happen in this arm.

The author should say which design is intended. One option is per-robot signs with the antimotif
column as the sign control. The other keeps g100 and g400 on the population sign as in-sample
anti-compasses. Prediction 5 and the pooled group follow from that choice.

### 2c. The "positive control" cannot void a body, and it does not reach the phantom

`calibration()` checks that `base` and `motif` reproduce RBT-67's numbers at a 1e-9 tolerance.
That is a determinism check: it fails only if the code path changed.

- It never exercises the decoy, which is the instrument that decides the verdict.
- g100 and g400 are checked on baseline only (their sign changed). They carry **no calibrated
  motif** and still enter the verdict.
- The W4b reproduction (`RBT-97-reproduction.txt`, 448 of 448 bouts identical) is real and good
  work. It proves the generalisation, not the phantom.

What would count as a positive control for the phantom:

- **The food-dependent side:** the known W4b collapse (a = 384: +1.875 → −0.217, RBT-67 §10) run
  through `mechanism.py --pop w4b`. It costs minutes.
- **The gait side has no known case at all.** So a GAIT reading has never been shown to be reachable,
  and 2a shows that as coded it largely is not.

### 2d. The decoy preserves patch structure but not depletion

**The patch structure is fine, so the answer to the coordinator's first question is "mostly yes".**
`set_food_seed(seed + 5000)` redraws the three patch centres (`_draw_patch_centres` runs per
seed). So the decoy has P-801's clustering at locations uncorrelated with the real patches.

**But the decoy is static.** `DecoySmell` swaps `food_pos` for a fixed array that is never
depleted. Meanwhile the real field loses what the robot eats, which at a = 384 is about 40% of the
crop (≈ 2.8 + 8.1 of 26 items on the five forward drivers) (P-801 has no regrowth within a 15 s season, since `regrow_delay` 45 > 15). So the phantom
robot steers on 26 undiminished items packed into three 0.6 m patches: a persistent, stronger
attractor placed away from the food.

Phantom Δ therefore measures the gait component *plus the cost of being held at a fake patch*.
That cost is negative, and it pushes retention **toward the food-dependent verdict**. It is
arguable, not measured. It is directional, and it points the same way as the prediction.

Two proposed fixes, neither of which adds a flag:

- **A depleting decoy:** the live real layout rotated about the arena centre by a random angle
  each bout. It keeps count, patch geometry, radial distribution and depletion, and removes the
  correlation.
- **RBT-39's trajectory null on the motif bouts**, as a second reading that needs no decoy. It asks
  whether the motif robot beats its own path against world-dealt layouts.

### 2e. The band itself is resolvable

`adversary_band.txt` uses RBT-67's per-seed noise and assumes the phantom arm has the same spread.
The half-width on pooled retention is ±0.19 at a = 64 and ±0.09 at a = 384.

- True retention 0 reads food-dependent 0.98–1.00 under the posted rule.
- 0.5 reads unresolved 0.98–1.00.
- The band edges are knife-edge, as any threshold is.
- A true 10–25% partial retention reads food-dependent 51–91% of the time. That matches the
  author's own statement that it *"cannot resolve a partial retention below about 25%"*.

## Credit

- §1 is correct, reproduces exactly from committed files, and rests on a split pre-registered
  before any of RBT-67's data existed.
- Reading the record before designing against it removed a false premise from RBT-91's closing.
  That is the most valuable thing on this ticket.
- The W4b bout-for-bout reproduction, 448 of 448, is the right way to generalise a hard-coded
  script.
- The pre-registration's own statement of what the n cannot resolve is accurate.

## Owed before the arm's verdict can be read

1. Fix the gait branch to the pre-registered rule (2a), preferably with a t-interval over robots.
2. State the sign design, and with it prediction 5 and the pooled group (2b).
3. A phantom positive control on the food-dependent side, `--pop w4b` at a = 384 (2c).
4. Either a depleting decoy or the trajectory-null reading beside the phantom, or report
   food-dependence as "phantom, static decoy" with 2d's bias stated (2d).
5. In the report, the per-population and seed-level counts beside the pooled 12/12 (§1,
   qualifications 2 and 4).

Checks done, in rule II's terms:

- **Frame:** checked. Both direction readouts were parsed, and they agree on every robot.
- **Calibrate:** checked. The 98 values were re-derived.
- **Manipulation check (the decoy):** read from source, not run.
- **Measure:** not applicable to this round; no simulation.

Not touched: RBT-97's status and assignee. The branch `origin/results/RBT-97` exists but carries no
commit of mine. It points at the old integration head `852dcac`, where the harness created it when
this session was first assigned RBT-97. I also called `issue_start` on RBT-97 at 12:25, before the
redirect. That is why the lease shows a claim at that minute.
