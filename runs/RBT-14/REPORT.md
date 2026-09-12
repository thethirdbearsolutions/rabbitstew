# RBT-14 — W2: sparse, wide, long smell (6 items in a 4 m disc, decay 3 m)

Run: `runs/RBT-14/W2-801`, seed 801, base commit e09ff7b (branch `claude/new-session-4cao7d`).
Flags exactly as the ticket: `--food-items 6 --food-radius 4 --food-decay 3.0`, everything else the
forage-801 baseline (eat radius 0.35, work cost 0.03, living cost 0.25, initial energy 3, birth at 3,
birth cost 1, capacity 60, groups of 4, 15 s seasons, random terrain and start). Confirmed from
`config.json`. 113 tests passed before the run.

## Result in one line

**Total extinction at season 31.** The wheeled population died out at season 23 and the holistic
population at season 31. The pre-registered expectation (holistic extinction, as at 6 items with 1 m
smell) held, and the wheeled side went too, faster than it did at 6 items with short smell (51).
Nothing on either side ever used its nose; there was nothing alive long enough to select on.

## 1. Ecology readout (`history.txt`, `readout.txt`)

Seasons past 31 do not exist. Mean gain is the mean lifetime energy gain per season of the individuals
alive after that season's deaths and births.

| season | holistic alive | births | deaths | mean gain | best gain | wheeled alive | births | deaths | mean gain | best gain |
|---|---|---|---|---|---|---|---|---|---|---|
| 0  | 56 | 0 | 4  | −0.029 | +0.000 | 60 | 2 | 2  | −0.377 | +1.065 |
| 3  | 55 | 0 | 2  | −0.013 | +0.210 | 37 | 4 | 21 | −0.052 | +2.423 |
| 11 | 2  | 0 | 37 | +0.149 | +0.216 | 7  | 0 | 1  | +0.148 | +0.557 |
| 20 | 3  | 1 | 0  | +0.089 | +0.299 | 2  | 0 | 1  | +0.342 | +0.376 |
| 23 | 3  | 0 | 0  | +0.147 | +0.258 | 0  | 0 | 1  | —      | —      |
| 30 | 1  | 0 | 1  | +0.224 | +0.224 | —  | — | —  | —      | —      |
| 31 | 0  | 0 | 1  | —      | —      | —  | — | —  | —      | —      |
| 32, 60, 100 … 599 | — | | | | | — | | | | |

**Bottleneck and recovery.** None recovered. Holistic: 56 → 39 by season 10 by age deaths, then 37
starved in one season at 11 (the founders' 3 energy at 0.25 a season runs out at season 11, as in
every arm); 2 survivors; peak of 3 at seasons 20–23 after two births; extinct at 31. Wheeled: 60 → 37
at season 3 (21 deaths), 9 by season 9, 7 at 11, then a slow bleed to 0 at 23. Minimum before
extinction: holistic 1 (seasons 15–18 and 30), wheeled 1 (season 22).

**First season holistic mean gain exceeds wheeled: 0**, trivially: 56 random lumps that did not move
lost 0.03 a season while 60 random Pioneers lost 0.38 driving. Between seasons 4 and 22 the wheeled
mean was above the holistic mean in every season but one (season 11, +0.148 vs +0.149). This is not
the baseline's season-83 crossover; nothing here was ever selected up.

**Extinction seasons.** Wheeled 23, holistic 31, "everyone died" at 31.

**Total turnover.** Holistic 3 births, 63 deaths. Wheeled 21 births, 81 deaths. Wheeled births came
from a handful of founders (c0-55, c0-40, c0-15, c0-13 and a few one-offs); the last wheeled birth was
at season 13 and the last holistic one at season 20.

**What the survivors did (lineage.jsonl).** Not one of the 56 holistic founders ate anything in
season 0 (season-0 mean gain −0.029 is pure work cost). The lump that carried the population, h0-7
(4 parts, 20 units, four joint-angle sensors, no nose), ate exactly one item in a season on seasons 11,
17, 18, 19, 20 and 27 and nothing in the other 25: a gain of +0.966 in an eating season, −0.034
otherwise, against a basal cost of 0.25. That is 6 items in 31 seasons, 0.19 a season, below the
0.25 break-even, and it died at age 58 with 0.20 energy: starvation, two seasons short of the age
limit. Its two children (he62, he63) inherited the same one-item-every-few-seasons habit; he62 ate on
seasons 21 and 27 and starved at 30, he63 never ate and starved at 24. On the wheeled side 12 of 60
founders ate in season 0; the two that kept the population going, c0-55 and c0-40, ate two items
(gain +1.35 to +1.47) roughly one season in three and paid 0.53–0.65 of work in the seasons they
did not; c0-40 was the last Pioneer alive and died at 23 with 0.07 energy.

## 2. Founders at the last season with survivors

```
holistic     last season with survivors 30: {'founders': 1, 'of': 1}
conventional last season with survivors 22: {'founders': 1, 'of': 1}
```
Both are single individuals, and both are founders themselves (h0-7 and c0-40 are generation-0
genotypes). No descendant outlived its parent on either side.

## 3. Yield heritability

Not estimable. With the ticket's rule (child and parents both with ≥ 5 evaluations) there are 2
qualifying holistic children and 6 wheeled, against the 10 the estimator needs. Dropping the eval
filter would not help (3 holistic and 21 wheeled children in total, most dead within a few seasons).
There was no breeding population to be heritable.

## 4. Probes (`probe.txt`; 12 seeds each, robot alone in the arena)

```
holistic     g  0 parts  2 units   5 sensors []
     intact: food 0.00 disp 0.00 path 0.0 work 0.0kJ  no_food: food 0.00 disp 0.00 path 0.0 work 0.0kJ  no_env: food 0.00 disp 0.00 path 0.0 work 0.0kJ  no_local: food 0.00 disp 0.00 path 0.0 work 0.0kJ
holistic     g 10 parts  4 units  20 sensors ['joint_angle']
     intact: food 0.42 disp 0.28 path 2.9 work 1.1kJ  no_food: food 0.42 disp 0.28 path 2.9 work 1.1kJ  no_env: food 0.42 disp 0.28 path 2.9 work 1.1kJ  no_local: food 0.33 disp 0.42 path 2.7 work 1.0kJ
holistic     g 20 parts  4 units  20 sensors ['joint_angle']
     intact: food 0.42 disp 0.28 path 2.9 work 1.1kJ  no_food: food 0.42 disp 0.28 path 2.9 work 1.1kJ  no_env: food 0.42 disp 0.28 path 2.9 work 1.1kJ  no_local: food 0.33 disp 0.42 path 2.7 work 1.0kJ
holistic     g 30 parts  4 units  20 sensors ['joint_angle']
     intact: food 0.42 disp 0.28 path 2.9 work 1.1kJ  no_food: food 0.42 disp 0.28 path 2.9 work 1.1kJ  no_env: food 0.42 disp 0.28 path 2.9 work 1.1kJ  no_local: food 0.33 disp 0.42 path 2.7 work 1.0kJ
conventional g  0 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 0.08 disp 17.61 path 17.6 work 29.7kJ  no_food: food 0.17 disp 21.04 path 20.9 work 30.1kJ  no_env: food 0.25 disp 1.43 path 5.5 work 18.8kJ  no_local: food 0.25 disp 1.43 path 5.5 work 18.8kJ
conventional g 10 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 0.58 disp 1.77 path 7.5 work 18.0kJ  no_food: food 0.50 disp 1.39 path 6.1 work 17.7kJ  no_env: food 0.25 disp 1.19 path 4.7 work 14.3kJ  no_local: food 0.25 disp 1.19 path 4.7 work 14.3kJ
conventional g 20 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 0.58 disp 1.77 path 7.5 work 18.0kJ  no_food: food 0.50 disp 1.39 path 6.1 work 17.7kJ  no_env: food 0.25 disp 1.19 path 4.7 work 14.3kJ  no_local: food 0.25 disp 1.19 path 4.7 work 14.3kJ
```

Seasons 10, 20 and 30 on the holistic side and 10 and 20 on the wheeled side are the same
individual each time (h0-7 and c0-40; `best_name` in history.json), so those rows are exact repeats
on the same 12 seeds.

- **holistic g0 (h0-6)**: two parts, five units, no sensors; does not move and eats nothing alone, so no
  lesion can matter. It was "best" at season 0 only because every lump scored ≈ 0 and it paid no work.
- **holistic g10/20/30 (h0-7)**: no nose at all (four joint-angle sensors); intact, no_food and no_env
  are identical (0.42 items over a 2.9 m path on 1.1 kJ), and silencing the local brains costs 21 %
  (0.42 → 0.33), under the 25 % mark. A blind, short random walk; at 0.12 items per m² a 2.9 m path
  with a 0.7 m swath should meet about 0.24 items, and it meets 0.42. No sensor matters.
- **wheeled g0 (c0-35)**: alone it eats 0.08 and drives 17.6 m straight out of the disc on 29.7 kJ; with
  the noses blanked it eats 0.17 (+100 %), with every environmental sensor blanked 0.25 (+200 %) and
  stays in the disc (displacement 1.4 m). Its sensors matter, and in the wrong direction: its
  season-0 lifetime gain of +1.07 in the shared arena was one lucky season, and it starved at 3.
- **wheeled g10/20 (c0-40)**: 0.58 intact, 0.50 with the noses blanked (−14 %, under the mark), 0.25
  with every environmental sensor blanked (−57 %). Its yield depends on sensors, but not the noses:
  with orientation, velocity and contact inputs off it drives a shorter path (4.7 m vs 7.5 m) on
  less energy, the same "situated in the sense of staying" pattern as the baseline's season-200
  Pioneer. Not nose-dependent.

`no_food` never halved a best's yield, so the wiring report is not triggered; for completeness, c0-40
carries food and agent sensors on the chassis (part 0, units 8/9) and on both drive wheels (parts 1
and 2, units 12/13 and 16/17), the standard Pioneer nose layout, with both live effectors
environment-driven (`env_driven_effectors` 2 of 2, `sensor_sources` food 3, agent 3, up 3,
velocity 3, joint_velocity 2, contact 1, height 1). The noses are wired in and do almost nothing.

## 5. Against the baseline

| | forage-801 (12 items, r 3, decay 1) | mid-801 (6 items, r 3, decay 1) | sparse-801 (3 items) | **W2 (6 items, r 4, decay 3)** |
|---|---|---|---|---|
| food density (items/m²) | 0.42 | 0.21 | 0.11 | **0.12** |
| holistic minimum / season | 7 at 11 | 2 at 11 | 3 at 11 | **2 at 11** |
| holistic back to 60 | season 32 | never (extinct 15) | never (extinct 24) | **never (extinct 31)** |
| wheeled minimum | 16 kept | 11 at 17, then 5–9 | 2, then 0 | **1 at 22** |
| wheeled fate | full to 599 | extinct 51 | extinct 10 | **extinct 23** |
| first holistic > wheeled mean | 83 | — | — | **0 (trivial), never after** |
| holistic mean gain 100/300/500/599 | +1.02/+1.19/+1.63/+1.41 | — | — | **—** |
| wheeled mean gain 100/300/500/599 | +0.96/+1.03/+0.94/+0.95 | — | — | **—** |
| holistic founders in final ancestry | 1 of 60 | — | — | **1 (itself)** |
| any nose-dependent best | Pioneer at 500 (brake, not compass) | — | — | **none** |

Baseline and comparison figures are from docs/foraging-world.md; W2 from this run. Density for W2 is
6 / (π·4²) = 0.12 per m², which is the sparse arm's density, not the mid arm's; the ticket's "a third
of baseline" is right (0.42 → 0.12) and the closer comparison is therefore sparse-801, not mid-801.

## Does this variant give sensing a slope?

No, and it could not have: nothing lived long enough to be selected. At 0.12 items per square metre
this disc is as poor as the sparse arm's, and the sparse arm's verdict repeats almost season for
season: the holistic founders starve together at season 11, the handful that eat at all eat below the
basal cost and breed once or twice into children no better than themselves, and the wheeled founders
that burn 0.4–0.65 a season driving run out of birth energy by season 3 and never form a breeding
population. Tripling the smell's reach changed no founder's yield, because a random controller does
not turn smell into steering, and the one thing a longer smell could have rewarded, a weak nose bias
that drifts a lump toward food, needs a lineage with time to acquire it. Under the work cost, six
items in a 4 m disc is below the bootstrap density for random founders of both kinds. The one
contrast with the docs worth stating plainly: at six items in the *3 m* disc the wheeled population
was "selected rather than merely sustained" and lasted to season 51; here, with the same six items
spread over 78% more area, it lasted to 23 and never bottlenecked into a breeding core. Density, not
item count and not smell reach, is what the founders felt. If a wider-smell world is to be tested,
it has to be one where something lives: the same decay at the baseline's density, or the banked
range expansion in which an already-mowing fauna is carried down to this density.
