# RBT-13 — W1, long-range smell: foraging ecology with food decay 3 m (seed 801)

One arm of the world fan-out. Only change from the baseline `forage-801`: `--food-decay 3.0` (smell length scale 3 m instead of 1 m). All other flags as in the issue; nothing tuned. Run: `runs/RBT-13/W1-801`, 600 seasons, both populations at capacity 60 from season 23 (holistic) and throughout (wheeled). Log: `W1-801.log`.

Provenance note: the first launch was killed at season 79 when the session's container was reclaimed between turns; the run was restarted from scratch with identical flags (seed 801 is deterministic, and the first 79 seasons replayed identically). Everything below is from the complete second run.

## A measurement caveat, stated up front

The smell sensor is squashed as `i / (1 + i)` (`Simulation._intensity`, `rabbitstew/simulation.py`), not left raw. With 12 items in a 3 m disc and decay 3 m the summed intensity is 4 to 6 everywhere inside the disc, so the squash sits on its flat shoulder. Measured over random item layouts (`smell_range.txt`):

| decay | r from centre | squashed signal | mean d(signal)/dx per metre | change over one eat radius (0.35 m) |
|---|---|---|---|---|
| 1 m | 0 / 2 / 3 / 4 m | 0.67 / 0.61 / 0.48 / 0.29 | 0.046 / 0.089 / 0.179 / 0.180 | 0.016 / 0.031 / 0.063 / 0.063 |
| 3 m | 0 / 2 / 3 / 4 m | 0.86 / 0.84 / 0.81 / 0.76 | 0.007 / 0.023 / 0.042 / 0.055 | 0.002 / 0.008 / 0.015 / 0.019 |

The pre-registration's intent, "a gradient exists across most of the disc", is met in the raw intensity, but in sensor units the gradient is 3 to 7 times **smaller** at 3 m decay than at 1 m, and the whole disc spans 0.05 of signal instead of 0.19. This arm therefore tests long range at the cost of resolution, not long range alone. This contradicts the framing in the issue (and the "smell that carries over several metres" idea in `docs/foraging-world.md`) as applied to this sensor: with a saturating squash, a longer decay gives the nose less to work with, not more, at this food density. Reported, not corrected.

## 1. Ecology readout (`readout.txt`, `history_table.txt`)

| season | holistic alive | births | deaths | mean gain | wheeled alive | births | deaths | mean gain |
|---|---|---|---|---|---|---|---|---|
| 0 | 59 | 3 | 4 | +0.04 | 60 | 2 | 2 | +0.05 |
| 11 | 8 | 1 | 36 | +0.24 | 60 | 7 | 7 | +0.72 |
| 20 | 28 | 9 | 1 | +0.91 | 60 | 1 | 1 | +0.81 |
| 32 | 60 | 2 | 2 | +1.04 | 60 | 0 | 0 | +0.84 |
| 60 | 60 | 0 | 0 | +1.21 | 60 | 1 | 1 | +0.88 |
| 100 | 60 | 1 | 1 | +1.21 | 60 | 0 | 0 | +0.84 |
| 200 | 60 | 2 | 2 | +1.15 | 60 | 3 | 3 | +0.84 |
| 300 | 60 | 0 | 0 | +1.36 | 60 | 1 | 1 | +0.79 |
| 400 | 60 | 3 | 3 | +1.04 | 60 | 1 | 1 | +0.77 |
| 500 | 60 | 0 | 0 | +1.05 | 60 | 2 | 2 | +0.92 |
| 599 | 60 | 0 | 0 | +1.19 | 60 | 3 | 3 | +0.82 |

- Bottleneck: holistic min alive **8 at season 11** (36 starved in one season), recovered to 60 at **season 23**. Wheeled never dipped below 60. No extinction.
- First season holistic mean gain exceeds wheeled: **20**. From season 32 on, holistic is above wheeled in 566 of 568 seasons (the two exceptions are single seasons near 460); averages over seasons 32 to 599: holistic +1.15, wheeled +0.84.
- Turnover: 865 holistic births/deaths, 1150 wheeled, over 600 seasons.

## 2. Founders at the last season

- holistic: **1 founder of 60** (generation 599)
- conventional (wheeled): **8 founders of 60**

## 3. Yield heritability (parent-child Pearson r on lifetime mean yield, child and all parents with evals ≥ 5)

- holistic: **r = 0.435** (n = 666)
- wheeled: **r = 0.241** (n = 700)

## 4. Probes (`probe.txt`; `scripts/forage_probe.py runs/RBT-13/W1-801 0,100,300,590 8`)

```
holistic     g  0 parts  4 units  29 sensors ['oscillator', 'up']
     intact: food 0.00 disp 0.27 path 2.3 work 0.7kJ  no_food: food 0.00 disp 0.27 path 2.3 work 0.7kJ  no_env: food 0.00 disp 0.27 path 1.9 work 0.7kJ  no_local: food 0.12 disp 0.74 path 0.9 work 0.3kJ
holistic     g100 parts  7 units  34 sensors ['joint_angle']
     intact: food 1.12 disp 2.44 path 6.2 work 1.5kJ  no_food: food 1.12 disp 2.44 path 6.2 work 1.5kJ  no_env: food 1.25 disp 2.23 path 5.6 work 1.5kJ  no_local: food 1.00 disp 1.96 path 5.6 work 1.5kJ
holistic     g300 parts  6 units  25 sensors ['joint_angle']
     intact: food 2.00 disp 1.72 path 6.1 work 1.4kJ  no_food: food 2.00 disp 1.72 path 6.1 work 1.4kJ  no_env: food 2.12 disp 0.82 path 5.2 work 1.4kJ  no_local: food 2.25 disp 0.62 path 5.2 work 1.4kJ
holistic     g590 parts  6 units  34 sensors ['oscillator', 'velocity']
     intact: food 2.00 disp 2.93 path 5.3 work 7.3kJ  no_food: food 2.00 disp 2.93 path 5.3 work 7.3kJ  no_env: food 2.00 disp 2.93 path 5.3 work 7.3kJ  no_local: food 2.00 disp 2.93 path 5.3 work 7.3kJ
conventional g  0 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 0.00 disp 0.28 path 2.2 work 24.4kJ  no_food: food 1.62 disp 1.64 path 6.9 work 17.9kJ  no_env: food 1.00 disp 1.26 path 5.3 work 15.4kJ  no_local: food 1.00 disp 1.26 path 5.3 work 15.4kJ
conventional g100 parts  5 units  23 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 0.38 disp 0.41 path 3.9 work 12.7kJ  no_food: food 0.75 disp 0.69 path 5.8 work 16.2kJ  no_env: food 0.12 disp 19.20 path 19.0 work 30.0kJ  no_local: food 0.12 disp 19.20 path 19.0 work 30.0kJ
conventional g300 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 1.88 disp 1.86 path 6.7 work 15.2kJ  no_food: food 2.00 disp 2.69 path 7.0 work 17.3kJ  no_env: food 0.12 disp 0.31 path 2.5 work 14.2kJ  no_local: food 0.12 disp 0.31 path 2.5 work 14.2kJ
conventional g590 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 1.62 disp 1.55 path 6.6 work 19.5kJ  no_food: food 0.88 disp 2.06 path 5.4 work 16.5kJ  no_env: food 1.38 disp 1.51 path 8.3 work 26.8kJ  no_local: food 1.38 disp 1.51 path 8.3 work 26.8kJ
```

One sentence per best (a sensor "matters" if a lesion changes items eaten by more than 25%):

- **holistic g0**: no nose, eats nothing, no sensor matters.
- **holistic g100**: one joint-angle sensor, no nose; no lesion moves its 1.12 items by more than 12% — blind mowing on 1.5 kJ.
- **holistic g300**: joint-angle only; 2.00 items intact, 2.12 with env blanked, 2.25 with local brains silenced — nothing matters, blind mowing on 1.4 kJ.
- **holistic g590**: oscillator and velocity sensors; 2.00 items under every lesion, identical path — nothing matters at all.
- **Pioneer g0**: the noses matter in the wrong direction: intact it barely moves (0.28 m) and eats 0.00, with the noses blanked it eats 1.62; at 3 m decay the saturated smell (signal 0.86 everywhere) is a constant input that stalls the random-weight controller.
- **Pioneer g100**: noses still hurt (0.38 intact, 0.75 blanked); with all env sensors blanked it drives 19 m in a straight line and eats 0.12 — the non-nose sensors keep it in, the noses do not.
- **Pioneer g300**: noses do nothing (1.88 intact, 2.00 blanked); with env sensors blanked it does not move (0.31 m) — its drive is gated through orientation/velocity, as the baseline's season-500 predecessor was.
- **Pioneer g590**: the noses matter: 1.62 intact, 0.88 with the noses blanked (a 46% cut on 8 seeds), 1.38 with every env sensor blanked. This is the only nose-dependent best in the run and is examined below.

### The Pioneer g590 nose-dependence: headline check

On the pre-registered rule (`no_food` cuts yield by more than half) the 8-seed probe says no (46%). On 16 seeds (`brake_or_compass.txt`) it says yes, narrowly:

| mode (n = 16) | items eaten | path (m) | time inside the 3 m disc | mean distance from centre (m) | items per metre of in-disc path |
|---|---|---|---|---|---|
| intact | 1.44 ± 0.31 | 6.2 | 0.88 | 2.16 | 0.276 |
| no_food (noses blanked) | 0.62 ± 0.29 | 5.3 | 0.65 | 2.61 | 0.200 |
| no_env | 1.06 ± 0.31 | 8.1 | 0.75 | 2.53 | 0.194 |

A 57% cut, at about two standard errors. What the noses do: with them blanked the robot spends a third of the season outside the food disc instead of an eighth, and its mean distance from the centre goes from 2.2 m to 2.6 m. Intact, it eats 0.276 items per metre of in-disc path, which is what a blind mow of that path should meet (2 × eat radius × density = 0.7 m × 0.424 items/m² = 0.297 items/m); it is not finding food faster than chance, it is staying where the food is. **This is the baseline's season-500 Pioneer again: a brake against leaving the disc, weaker (57% vs 88% loss), not a compass.**

Wiring (`wiring.txt`, `controller_descriptors`): sensor_sources {contact 1, up 3, velocity 3, height 1, food 3, agent 3, joint_velocity 2}; env_driven_effectors 2 of 2 driven; 127 links; mean sensor path 1.0. The food sensors sit on part 0 (the chassis, fixed), part 1 and part 2 (the two drive wheels, hinge joints). Only the **chassis nose** is wired into the controller (six links into the global neurons 18 to 23, weights −1.69 to +0.56); the wheel nose on part 2 has a single link to a local unit and the wheel nose on part 1 has none. There is no crossed pairing of the two wheel noses, i.e. no Braitenberg circuit; a single nose on the chassis, read through the global brain, is exactly the one-sensor one-bit skill that a brake needs and a compass cannot be built from. The same layout holds at g300 (chassis nose into the global neurons, wheel noses unused), where it has no effect on yield.

### Holistic bests that carried a nose (`holistic_sensors_by_gen.txt`, `probe_holistic_nosed.txt`)

Of 61 saved holistic bests (every 10 seasons), 7 carry a food or agent sensor (seasons 350, 390, 410, 420, 430, 440, 580); 5 of the final 60 holistic individuals carry one. Probed:

```
holistic     g390 parts  5 units  27 sensors ['food', 'joint_angle', 'oscillator', 'velocity']
     intact: food 3.12 disp 1.42 path 6.2 work 1.2kJ  no_food: food 3.12 ...  no_env: food 2.75 ...  no_local: food 3.25 ...
holistic     g440 (same individual)  identical
holistic     g580 parts  6 units  35 sensors ['food', 'oscillator', 'velocity']
     intact: food 1.50 disp 1.83 path 5.0 work 4.7kJ  no_food: food 1.50 ...  no_env: food 1.50 ...  no_local: food 1.75 ...
```

The g390/g440 best is the strongest mower in the whole foraging series so far, 3.12 items alone on 1.2 kJ, and its nose does nothing: blanking it changes neither path nor yield to the second decimal. The g580 nose is likewise inert. No holistic individual in this run uses its nose.

## Against the baseline (forage-801, decay 1 m)

| | baseline (decay 1 m) | **W1 (decay 3 m)** |
|---|---|---|
| holistic bottleneck | 60 → 7 at season 11, back to 60 by 32 | 60 → **8 at 11**, back to 60 by **23** |
| holistic mean gain @ 100 / 300 / 500 / 599 | +1.02 / +1.19 / +1.63 / +1.41 | **+1.21 / +1.36 / +1.05 / +1.19** |
| wheeled mean gain @ 100 / 300 / 500 / 599 | +0.96 / +1.03 / +0.94 / +0.95 | **+0.84 / +0.79 / +0.92 / +0.82** |
| first season holistic > wheeled | 83 | **20** |
| holistic founders of 60 | 1 | **1** |
| wheeled founders of 60 | 7 | **8** |
| yield heritability holistic / wheeled | 0.51 / 0.24–0.39 | **0.44 / 0.24** |
| holistic best with a sensor lesion > 25% | none | **none** (g0, 100, 300, 390, 440, 580, 590 all inert) |
| nose-dependent Pioneer best | season 500: 1.00 intact vs 0.12 noses blanked (brake) | **season 590: 1.44 vs 0.62 on 16 seeds (brake, weaker); 1.62 vs 0.88 on 8** |
| any chemotaxis | no | **no** |

## Answer

**No. Long-range smell did not give sensing a slope.** The ecology ran the same course as the baseline, slightly faster on the holistic side (recovery at 23 rather than 32, crossover at 20 rather than 83) and slightly worse for the wheeled side (mean gain 0.8 rather than 0.95, because the saturated smell is a handicap to a random-weight Pioneer at season 0), and it ended in the same place: one holistic founder, cheap blind mowing on 1.2 to 7 kJ that no sensor lesion touches, the best mower of the series carrying a nose it never reads, and one Pioneer whose noses are a brake against driving out of the disc, built from a single chassis nose into the global brain, with no Braitenberg pairing on the wheel noses that arrived wired for it. The pre-registered reading is therefore that **information range was not the limit**, with one qualification that this arm cannot separate: because the smell is squashed by `i/(1+i)` and twelve items at 3 m decay put the sum at 4 to 6, the 3 m arm delivered a gradient that spans the disc but is three to seven times weaker per metre than the 1 m arm's. A long-range smell that is also readable needs either a squash with a longer linear range, or a normalised intensity (mean over items instead of a sum, or a log), and that is a different arm, not this one.

## Files

`W1-801/` (config.json, history.json, lineage.jsonl, best_gen*.json, holistic/final, conventional/final), `W1-801.log`, `readout.py` / `readout.txt`, `history_table.txt`, `probe.txt`, `probe_holistic_nosed.txt`, `holistic_sensors_by_gen.txt`, `wiring.py` / `wiring.txt`, `brake_or_compass.py` / `brake_or_compass.txt`, `smell_range.txt`.
