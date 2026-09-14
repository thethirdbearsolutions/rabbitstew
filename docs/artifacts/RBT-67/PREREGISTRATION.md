# RBT-67 pre-registration — written before any bout was run

Posted to the ticket on 2026-09-14 before the ladder ran. Nothing below is a result.
The harness is `compass_dose_response.py` in this directory; the ladder is a ∈ {96, 128,
192, 256, 384} with a = 32 and a = 64 as calibration anchors, 7 robots × 64 paired seeds
from 7000, bootstrapped over robots, on both committed populations with the chemotactic
sign set per population.

## Definitions fixed in advance

- **Peak rung**: the rung with the largest mean paired Δ items over the seven robots.
- **Turnover**: the peak is not the top rung *and* the paired per-robot difference
  Δ(peak) − Δ(384), bootstrapped over robots, has a 95% CI excluding zero from above.
- **Saturate**: the peak is not the top rung, the CI above spans zero, and Δ(384) is at
  least three quarters of Δ(peak).
- **Keep climbing**: the peak *is* the top rung, a = 384.
- Anything else (peak below the top with a decline the CI cannot resolve and Δ(384) below
  ¾ of the peak) is reported as *unresolved at 64 seeds*, not forced into a bin.

## W4b-801 — seven bests, drive BACKWARD, the published sign is their compass

| shape past a = 64 | confidence |
|---|---|
| **peak and turn over inside the range** (peak at 96 or 128; a = 384 credibly below it) | **0.60** |
| saturate (plateau from about 128 on, no credible decline) | 0.25 |
| keep climbing to 384 | 0.15 |

- **Size of the prize**: the peak Δ lies between +1.0 and +2.0 items on a ~1.5 baseline.
  Nearer 0.9 than 2.5.
- **Mechanism prediction**: the fraction of ticks with both drive effectors pinned at the
  same sign (`rail%`) rises monotonically with a on every robot, and in-disc path length
  falls past the peak while items per in-disc metre does *not* fall. The turnover, if it
  comes, is a throttle loss from a saturated steering term, not worse steering. Falsified
  if items/m falls in step with items past the peak.
- **Anchors**: a = 64 on fresh seeds 7000..7063 lands inside the source's CI
  [+0.632, +1.176] with 7/7 improved; a = 32 lands near +0.25.
- **Readback**: at every rung ≥ 96 the realised a is within 20% of the installed 2k on
  all seven robots and has the installed sign; |a|/|c| ≥ 5 on every robot at every rung.
  Falsified if any robot's realised a is sign-reversed at a ≥ 96 (the RBT-45 calibration
  note about a sign-reversed robot is at a = 16–64, where evolved wiring can compete).

What would falsify the headline: Δ(384) the best rung and credibly above Δ(128) →
"keep climbing" and the prize is unbounded by this ladder.

## RBT-19/P-801 — seven bests, drive FORWARD, the opposite sign is their compass

| shape past a = 64 (population mean) | confidence |
|---|---|
| **peak and turn over inside the range** | **0.55** |
| saturate | 0.25 |
| keep climbing | 0.20 |

- **The per-generation prediction, and the sharp one**: g100 and g400 drive backward
  (PR #11: +177.2° and +165.1°), so the population-level sign anti-compasses them. They
  lose at every rung ≥ 64 and the "robots improved" count is ≤ 5/7 at every rung.
  Confidence 0.80. Falsified if either gains at a ≥ 64.
- Among the five forward drivers (g0, g200, g300, g500, g590) the peak Δ lies between +1
  and +3 items — larger than on W4b, because PR #11's two backward P-801 robots earned
  +3.7 and +1.1 with *their* compass at a = 64.
- **Saturation scale**: the median left-right nose gap on this substrate is 0.056
  (RBT-69), so a = 384 puts ~21 pre-tanh units on the steering axis; predicted rail% > 50%
  at a = 384 on this population.
- Readback and anchor predictions as for W4b, with the sign flipped.

## What I checked, in the rule-II order

- *Frame*: direction of travel per population, from `scripts/travel_direction.py`
  (to be re-run in the same session as the ladder and stated in the report).
- *Calibration*: a = 32 and a = 64 anchors against the source's own numbers; the
  install round-trips through the path-sum readback (`readback()` asserts the depth-1
  change in a equals the signed installed a, and the change in c is zero).
- *Manipulation check*: **not run in this harness.** RBT-69 established the travel-frame
  bearing improvement and the phantom-smell collapse at a = 64 on W4b; this ladder does not
  repeat it at higher a. If a turnover appears, whether the robot is still aiming at food
  at a = 384 is an open question this package does not answer.
- *Effect*: the ladder itself.
