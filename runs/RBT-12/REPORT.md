# RBT-12: designed quadruped vs evolved lump, capacity runs on seeds 403 and 404

Solo time-at-target task on random terrain, random starts, heading curriculum over the first 100 generations, four draws per generation, 200 generations, population 20, rich brains, equal mass budget. Holistic population ("lump") evolves body and brain; the conventional population is the hand-designed quadruped whose controller alone evolves (8 hidden). Exact command as in the issue. Every capability number below is on fresh draws the run never saw (eval_fresh: 12 fixed draws at the full heading range, every 20 generations; g200 means the final best, best_gen0199).

Run notes: both runs were killed at generation 7 by the session harness (not by the simulator) and resumed with `--resume` from their saved state; no generations were lost. At about 25 s per generation both finished in 2.5 h wall-clock, not the 5 h estimated. `rabbitstew inspect` reports the unscaled mass of the holistic bests (18.7 and 36.7 kg); the lineage log confirms both were simulated at the 15.34 kg budget.

## Table

| seed | lump fresh tat g40 / g100 / g200 | quadruped fresh tat g40 / g100 / g200 | max (gen) lump / quadruped | heritability h / c: all, 1-100, 101-200 | founders at g199 (of 20) h / c |
|---|---|---|---|---|---|
| 403 | 0.08 / 0.03 / **0.68** | 0.02 / 0.07 / 0.01 | 0.68 (g199) / 0.21 (g80) | h 0.71, 0.14, 0.64; c 0.24, 0.22, 0.14 | 7 / 7 |
| 404 | 0.02 / 0.02 / 0.02 | 0.10 / 0.05 / 0.05 | 0.05 (g60) / 0.15 (g60) | h 0.09, 0.12, 0.05; c 0.25, 0.24, 0.24 | 3 / 4 |

Founders expected under pure-noise fitness for this reproduction scheme: 3.6 at 100 generations (`heritability --founder-model`). Seed 404's counts are at the drift baseline in both populations; seed 403's are twice it.

Full fresh-draw curves (time at target, every 20 generations, g0 first, then g20 … g180, g199):

- 403 lump: 0.05 0.05 0.08 0.00 0.00 0.03 0.00 0.05 **0.59 0.67 0.68**
- 403 quadruped: 0.00 0.05 0.02 0.07 **0.21** 0.07 0.02 0.08 0.08 0.09 0.01
- 404 lump: 0.00 0.03 0.02 0.05 0.03 0.02 0.04 0.04 0.00 0.03 0.02
- 404 quadruped: 0.00 0.07 0.10 **0.15** 0.02 0.05 0.01 0.13 0.08 0.06 0.05

Training-draw bests for comparison (winner's curse check): 403 lump reached 0.87 on its training draws at g199 against 0.68 fresh, so most of it is real; the quadruped's training bests of 0.33 to 0.44 in both seeds correspond to 0.02 to 0.21 fresh, so the quadruped's reported curve is still mostly curse.

## Capability of the final bests (`rabbitstew analyze --every 20 --lesions final`, flat-ground solo trials)

| best | approach (m gained of 2) | steering successes of 3 | terrain successes of 6 |
|---|---|---|---|
| 403 lump h199-15 (2 parts: box + sphere on a ball joint) | +1.69 | 3 | 4 |
| 403 quadruped c199-7 | +0.83 | 0 | 0 |
| 404 lump h199-12 (3 cylinders in a chain, ball joints) | +1.16 | 0 | 1 |
| 404 quadruped c199-7 | +1.50 | 0 | 2 |

The 403 lump is the first best in this series to pass all three steering trials. Its `fell` flag is set, which is meaningless for a body that moves by rolling its sphere.

Lesion block of the final holistic bests (silence each unit in turn, loss in metres of approach progress; essential = loss above 0.1 m):

- **403 h199-15**: 35 units, 5 links, 3 driven effectors, baseline 1.75 m; 6 essential, 1 harmful, effective fraction 0.23. Essential units: two effectors in the sphere part (loss 3.18 and 1.86 m), the `opponent z` sensor in the sphere part (1.62 m; with the opponent proxy this is the target direction's vertical component in the part's own frame, the same embodied trick A-301 found), the `up z` sensor in the sphere part (1.07 m), a third sphere effector (0.97 m), one global tanh neuron (0.31 m). Closed-loop, local, and sensor-driven, as the paper's lesion section predicts for solo-evolved bests. Silencing the whole global brain is not tested here; the single essential global neuron is the only one that matters.
- **404 h199-12**: 48 units, 17 links, 2 driven effectors, baseline 1.01 m; 14 essential, 1 harmful, effective fraction 0.31. Top losses: a global `sin` oscillator (2.60 m), part 2's effector 2 (2.01 m), part 0's `velocity z` sensor (1.80 m), a global tanh (1.51 m), part 1's effector 2 (1.30 m), part 1's `velocity z` (1.22 m), part 1's effector 0 (1.14 m), **part 2's `joint_angle` (0.98 m) and part 1's `joint_angle` (0.60 m)**, two `opponent_distance` sensors (0.66, 0.55 m). This best is open-loop-with-oscillator on flat ground (+1.16 m approach) but does not steer (0 of 3) and scores 0.02 fresh on the actual task. Its proprioceptive sensors carry measurable lesion loss, which contradicts the paper's sentence that joint angle and velocity have zero measured influence in every best. It is a flat-ground approach effect in a best that fails the task, so the sentence needs the qualifier "in every competent best", not a retraction.

The quadrupeds' lesion blocks: 403 c199-7 has 3 essential and 35 harmful units of 52 (removing most units helps it on flat ground), 404 c199-7 has 28 essential and 2 harmful. Both have 8 driven effectors and 230 to 289 links; neither steers.

## Across seeds 401 to 404

Seeds 401 and 402 are only known at generation 100 (from the paper doc: lump 0.22 vs quadruped 0.02, and lump 0.05 vs quadruped 0.10); their generation-200 numbers are not in the repository, so "how often is the lump ahead at 200" can only be answered for 403 and 404: one each. At generation 100 across all four seeds the lump is ahead once (401) and behind three times (402, 403, 404); at generation 200 on the two seeds that have it, the lump is ahead once by a wide margin (403: 0.68 vs 0.01) and behind once by a negligible one (404: 0.02 vs 0.05, both at noise level).

The quadruped's ceiling holds at what the doc said: its fresh-draw best never exceeds 0.21 in any of the four seeds (peaks 0.09, 0.14, 0.21, 0.15), and in 403 and 404 it does not keep its peak; by generation 200 it is at 0.01 and 0.05, with heritability 0.14 to 0.24 and, in 404, founder counts at the drift baseline. The quadruped's controller evolution finds a gait-like approach on flat ground (+0.83 and +1.50 m) but no steering in either seed (0 of 3), and time at target on random terrain at a random bearing needs steering.

Two things in the doc's framing are contradicted by 403. First, the lump's ceiling is not "0.2 to 0.3": seed 403 holds the goal for 68% of the bout on fresh draws, three times the highest number in the series so far, with a two-part rolling body and a five-link reflex controller. Second, the foothold is not a coin flipped once by generation 40: 403's lump was at 0.00 to 0.08 fresh for 140 generations, indistinguishable from 404's, and then found its body between generations 140 and 160 (heritability in the second window 0.64 against 0.14 in the first), after the curriculum had been fully open for 40 generations. Whether 402 and 404 would do the same given more generations is not known; 404 at 200 shows no sign of it (founders 3 of 20, heritability 0.05 in the second window).

So the sentence "the designed body is the safer start and the lower ceiling" is still right in both halves, and the second half is stronger than the doc has it. Safer start: the quadruped is at 0.04 to 0.15 fresh by generation 40 to 60 in all four seeds, while the lump found nothing in 402 and 404 and nothing for 140 generations in 403. Lower ceiling: 0.21 at best, never held, against 0.68 held for the last 40 generations of 403. The sentence should gain a clause: the designed body is the safer start, the lower ceiling, and it does not keep what it finds, while the evolved search's foothold can come late as well as early and, when it comes, climbs past anything the designed body reaches.
