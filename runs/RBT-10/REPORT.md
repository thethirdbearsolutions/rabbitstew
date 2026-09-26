# RBT-10: the dense foraging ecology replicated on seeds 802 and 803, both work-cost arms

**Answer in three sentences.** The season-11 starvation event and the recovery reproduce on both seeds and in both arms, but much shallower than seed 801's: the holistic population fell to 31 to 42 of 60 (801: 7) and was back at capacity by season 13 to 15 (801: 32), with three founders surviving in the final ancestry instead of one. The holistic side overtakes the wheeled side in all four runs, and earlier than on 801 (sustained lead from season 11 to 30 against 801's 83), by a margin at season 599 of +0.04 to +0.22 a season (801: +0.46 under the work cost, +0.10 without). Every holistic best is a blind mower as on 801, no nose on either side steers toward food, and the one thing that differs from the docs beyond the depth of the bottleneck is that the Pioneer's noses matter more often here: six of sixteen Pioneer bests lose more than a quarter of their yield with the noses blanked, mostly as the brake 801 found once, and one (802, free work, season 590) halves its yield without lengthening its path, which the lesion cannot separate from steering.

## Setup

- Code: commit `e09ff7b` on `claude/new-session-4cao7d` (the base the ticket names), unchanged; results on the session branch `claude/determined-shannon-2zb8jp` because this session is restricted to it (the ticket asked for `results/RBT-10`).
- The ticket's command verbatim: 600 seasons, capacity 60, foraging challenge, groups of four, 12 items in a 3 m disc, eat radius 0.35, decay 1.0, living cost 0.25, initial energy 3, birth at 3, birth cost 1, 15 s seasons, mass budget 15.34, conventional topology, random terrain, random start, food score; work cost 0.03 (`w0.03`) or 0 (`w0.0`); seeds 802 and 803.
- Box: 4 cores, 15 GB. All four runs concurrently with `--workers 4`, about 24 s a season each, 4 h 05 m per run (12:20 to 16:25 UTC, 2026-09-12). A first launch died at seasons 17 to 19 when the container restarted; the relaunch reproduced season 0 of the first launch and of a two-season smoke test exactly, so the ecology is deterministic per seed and nothing from the dead launch was kept.
- No `everyone died` line and no traceback in any log. `pytest -q`: 113 passed before the runs.
- Files: `runs/RBT-10/<run>/{config.json,history.json,lineage.jsonl,holistic/,conventional/}` (bests every ten seasons and `final/`), `<run>.log`, `<run>.probe.txt`, `<run>.history.txt` (the `rabbitstew history` dump), `readout.txt` (section 1 as produced by `readout.py`), `check-801/` (section 4), this report.

## 1. Ecology readout, per run

Columns: alive, births, deaths and mean lifetime gain per population at the ticket's seasons. Mean lifetime gain is the ecology's `mean_lifetime_score`: the mean over living individuals of their lifetime mean per-season score, where a season's score is food eaten times its value minus the work cost of that season's actuator effort; the basal cost of 0.25 a season is charged separately and is not in this number (this is the figure the docs quote as "mean energy gain"). hol = holistic (evolved), wheel = conventional (Pioneer). Founders follow every parent back to generation 0 from everyone alive at the last season. Yield heritability is the Pearson r between a child's lifetime mean yield (the `fitness` field of its last lineage record, evals >= 5) and the mean of its parents' (same rule, every parent qualifying).

### forage-w0.03-802  (seasons completed: 600)

| season | hol alive | hol births | hol deaths | hol mean gain | wheel alive | wheel births | wheel deaths | wheel mean gain |
|---|---|---|---|---|---|---|---|---|
| 0 | 57 | 1 | 4 | -0.03 | 60 | 1 | 1 | +0.21 |
| 11 | 31 | 9 | 38 | +0.39 | 60 | 3 | 3 | +0.56 |
| 20 | 60 | 0 | 0 | +0.90 | 60 | 1 | 1 | +0.73 |
| 32 | 60 | 0 | 0 | +0.99 | 60 | 2 | 2 | +0.86 |
| 60 | 60 | 1 | 1 | +1.02 | 60 | 0 | 0 | +0.93 |
| 100 | 60 | 0 | 0 | +1.05 | 60 | 0 | 0 | +0.96 |
| 200 | 60 | 2 | 2 | +0.85 | 60 | 5 | 5 | +0.79 |
| 300 | 60 | 2 | 2 | +1.10 | 60 | 0 | 0 | +0.90 |
| 400 | 60 | 0 | 0 | +1.08 | 60 | 2 | 2 | +0.81 |
| 500 | 60 | 3 | 3 | +1.07 | 60 | 1 | 1 | +0.96 |
| 599 | 60 | 0 | 0 | +1.04 | 60 | 0 | 0 | +0.86 |

- **hol** bottleneck: 31 alive at season 11; recovery to 60: season 15
- **wheel** no bottleneck: never below capacity 60
- **crossover** (holistic mean gain > wheeled): first at season 18; first sustained for 10 seasons: 18; holistic ahead in 559 of 600 seasons
- **hol final** (season 599): alive 60, mean gain +1.04, best lifetime 2.11
- **wheel final** (season 599): alive 60, mean gain +0.86, best lifetime 2.23
- log: 0 'everyone died' line(s)
- **hol** founders at season 599: 3 of 60 alive; yield heritability r = 0.32 (n = 646 parent-child pairs)
- **wheel** founders at season 599: 15 of 60 alive; yield heritability r = 0.14 (n = 715 parent-child pairs)


### forage-w0.0-802  (seasons completed: 600)

| season | hol alive | hol births | hol deaths | hol mean gain | wheel alive | wheel births | wheel deaths | wheel mean gain |
|---|---|---|---|---|---|---|---|---|
| 0 | 57 | 1 | 4 | +0.02 | 60 | 1 | 1 | +0.78 |
| 11 | 32 | 11 | 39 | +0.46 | 60 | 2 | 2 | +0.75 |
| 20 | 60 | 4 | 4 | +0.80 | 60 | 1 | 1 | +0.82 |
| 32 | 60 | 1 | 1 | +1.04 | 60 | 3 | 3 | +0.94 |
| 60 | 60 | 1 | 1 | +1.05 | 60 | 1 | 1 | +1.08 |
| 100 | 60 | 1 | 1 | +0.96 | 60 | 3 | 3 | +1.03 |
| 200 | 60 | 2 | 2 | +1.02 | 60 | 1 | 1 | +1.08 |
| 300 | 60 | 1 | 1 | +1.12 | 60 | 0 | 0 | +0.94 |
| 400 | 60 | 3 | 3 | +1.07 | 60 | 1 | 1 | +0.76 |
| 500 | 60 | 0 | 0 | +1.19 | 60 | 2 | 2 | +0.97 |
| 599 | 60 | 0 | 0 | +1.06 | 60 | 2 | 2 | +0.86 |

- **hol** bottleneck: 32 alive at season 11; recovery to 60: season 14
- **wheel** no bottleneck: never below capacity 60
- **crossover** (holistic mean gain > wheeled): first at season 21; first sustained for 10 seasons: 30; holistic ahead in 450 of 600 seasons
- **hol final** (season 599): alive 60, mean gain +1.06, best lifetime 2.78
- **wheel final** (season 599): alive 60, mean gain +0.86, best lifetime 1.74
- log: 0 'everyone died' line(s)
- **hol** founders at season 599: 3 of 60 alive; yield heritability r = 0.44 (n = 638 parent-child pairs)
- **wheel** founders at season 599: 17 of 60 alive; yield heritability r = 0.39 (n = 621 parent-child pairs)


### forage-w0.03-803  (seasons completed: 600)

| season | hol alive | hol births | hol deaths | hol mean gain | wheel alive | wheel births | wheel deaths | wheel mean gain |
|---|---|---|---|---|---|---|---|---|
| 0 | 60 | 4 | 4 | +0.11 | 60 | 1 | 1 | +0.19 |
| 11 | 42 | 12 | 30 | +0.62 | 60 | 5 | 5 | +0.60 |
| 20 | 60 | 1 | 1 | +0.89 | 60 | 1 | 1 | +0.70 |
| 32 | 60 | 1 | 1 | +0.98 | 60 | 0 | 0 | +0.79 |
| 60 | 60 | 2 | 2 | +0.92 | 60 | 1 | 1 | +0.83 |
| 100 | 60 | 2 | 2 | +0.96 | 60 | 1 | 1 | +0.82 |
| 200 | 60 | 2 | 2 | +0.96 | 60 | 3 | 3 | +0.82 |
| 300 | 60 | 0 | 0 | +1.02 | 60 | 0 | 0 | +0.96 |
| 400 | 60 | 0 | 0 | +0.89 | 60 | 0 | 0 | +0.81 |
| 500 | 60 | 1 | 1 | +1.00 | 60 | 1 | 1 | +0.99 |
| 599 | 60 | 0 | 0 | +0.97 | 60 | 1 | 1 | +0.93 |

- **hol** bottleneck: 42 alive at season 11; recovery to 60: season 13
- **wheel** no bottleneck: never below capacity 60
- **crossover** (holistic mean gain > wheeled): first at season 1; first sustained for 10 seasons: 11; holistic ahead in 513 of 600 seasons
- **hol final** (season 599): alive 60, mean gain +0.97, best lifetime 2.13
- **wheel final** (season 599): alive 60, mean gain +0.93, best lifetime 2.30
- log: 0 'everyone died' line(s)
- **hol** founders at season 599: 3 of 60 alive; yield heritability r = 0.28 (n = 667 parent-child pairs)
- **wheel** founders at season 599: 12 of 60 alive; yield heritability r = 0.20 (n = 693 parent-child pairs)


### forage-w0.0-803  (seasons completed: 600)

| season | hol alive | hol births | hol deaths | hol mean gain | wheel alive | wheel births | wheel deaths | wheel mean gain |
|---|---|---|---|---|---|---|---|---|
| 0 | 60 | 3 | 3 | +0.13 | 60 | 1 | 1 | +0.73 |
| 11 | 36 | 12 | 36 | +0.54 | 60 | 5 | 5 | +0.68 |
| 20 | 60 | 2 | 2 | +0.96 | 60 | 1 | 1 | +0.80 |
| 32 | 60 | 1 | 1 | +1.08 | 60 | 1 | 1 | +0.88 |
| 60 | 60 | 3 | 3 | +1.07 | 60 | 1 | 1 | +0.94 |
| 100 | 60 | 0 | 0 | +1.05 | 60 | 1 | 1 | +0.83 |
| 200 | 60 | 3 | 3 | +1.09 | 60 | 1 | 1 | +1.00 |
| 300 | 60 | 0 | 0 | +1.28 | 60 | 0 | 0 | +0.98 |
| 400 | 60 | 2 | 2 | +1.21 | 60 | 1 | 1 | +0.92 |
| 500 | 60 | 6 | 6 | +1.23 | 60 | 0 | 0 | +1.07 |
| 599 | 60 | 1 | 1 | +1.29 | 60 | 0 | 0 | +1.07 |

- **hol** bottleneck: 36 alive at season 11; recovery to 60: season 14
- **wheel** no bottleneck: never below capacity 60
- **crossover** (holistic mean gain > wheeled): first at season 19; first sustained for 10 seasons: 19; holistic ahead in 566 of 600 seasons
- **hol final** (season 599): alive 60, mean gain +1.29, best lifetime 2.74
- **wheel final** (season 599): alive 60, mean gain +1.07, best lifetime 2.19
- log: 0 'everyone died' line(s)
- **hol** founders at season 599: 3 of 60 alive; yield heritability r = 0.28 (n = 645 parent-child pairs)
- **wheel** founders at season 599: 13 of 60 alive; yield heritability r = 0.25 (n = 612 parent-child pairs)



## 2. Probes

`scripts/forage_probe.py <run> 0,100,300,590 8`: the best of each population at seasons 0, 100, 300 and 590, alone in the arena on eight fresh seeds, intact, with the food and agent noses blanked (`no_food`), with every environmental sensor blanked (`no_env`), and with the local brains silenced (`no_local`). One sentence per best on whether any sensor matters, the line being a lesion that changes items eaten by more than 25% of the intact value. MuJoCo instability warnings are stripped; the raw files are `runs/RBT-10/<run>.probe.txt`.

### forage-w0.03-802

```
holistic     g  0 parts  6 units  25 sensors ['oscillator', 'up']
     intact: food 1.62 disp 1.60 path 7.2 work 3.2kJ  no_food: food 1.62 disp 1.60 path 7.2 work 3.2kJ  no_env: food 1.62 disp 1.60 path 7.2 work 3.2kJ  no_local: food 1.62 disp 1.60 path 7.2 work 3.2kJ
holistic     g100 parts  4 units  12 sensors ['agent']
     intact: food 1.50 disp 2.74 path 8.1 work 2.3kJ  no_food: food 1.50 disp 2.74 path 8.1 work 2.3kJ  no_env: food 1.50 disp 2.74 path 8.1 work 2.3kJ  no_local: food 1.50 disp 2.74 path 8.1 work 2.3kJ
holistic     g300 parts  4 units  12 sensors ['oscillator']
     intact: food 0.62 disp 2.10 path 7.4 work 2.3kJ  no_food: food 0.62 disp 2.10 path 7.4 work 2.3kJ  no_env: food 0.62 disp 2.10 path 7.4 work 2.3kJ  no_local: food 0.62 disp 2.10 path 7.4 work 2.3kJ
holistic     g590 parts 10 units  45 sensors ['joint_velocity', 'oscillator', 'up']
     intact: food 1.12 disp 2.14 path 7.7 work 4.8kJ  no_food: food 1.12 disp 2.14 path 7.7 work 4.8kJ  no_env: food 1.00 disp 1.68 path 7.2 work 4.7kJ  no_local: food 0.88 disp 1.52 path 7.7 work 4.6kJ
conventional g  0 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 0.62 disp 13.39 path 13.6 work 22.8kJ  no_food: food 0.88 disp 13.23 path 13.4 work 22.7kJ  no_env: food 0.50 disp 2.38 path 4.3 work 14.8kJ  no_local: food 0.50 disp 2.38 path 4.3 work 14.8kJ
conventional g100 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 1.62 disp 2.45 path 6.2 work 17.4kJ  no_food: food 0.50 disp 2.06 path 14.4 work 14.2kJ  no_env: food 2.12 disp 2.19 path 10.0 work 17.9kJ  no_local: food 2.12 disp 2.19 path 10.0 work 17.9kJ
conventional g300 parts  5 units  23 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 0.25 disp 1.26 path 3.3 work 17.1kJ  no_food: food 0.50 disp 0.82 path 2.7 work 18.5kJ  no_env: food 0.62 disp 2.32 path 8.8 work 17.5kJ  no_local: food 0.62 disp 2.32 path 8.8 work 17.5kJ
conventional g590 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 1.38 disp 0.86 path 7.7 work 27.0kJ  no_food: food 1.50 disp 1.63 path 8.0 work 28.8kJ  no_env: food 0.38 disp 15.95 path 16.0 work 29.1kJ  no_local: food 0.38 disp 15.95 path 16.0 work 29.1kJ
```

- **holistic g0**: No: no nose, and every lesion leaves 1.62 items unchanged; a blind mower.
- **holistic g100**: No: one agent nose that does nothing (1.50 in every mode); blind.
- **holistic g300**: No: oscillator only, 0.62 in every mode; blind and a weak eater.
- **holistic g590**: No: no nose; blanking every sensor costs 11% (1.12 to 1.00) and silencing the local brains 21%, both under the line.
- **conventional g0**: Yes, harmfully: blanking the noses raises yield 42% (0.62 to 0.88); it is a 13 m runaway either way, and blanking every sensor stops the run (2.4 m) at 0.50.
- **conventional g100**: Yes: the noses are a brake, not a compass; without them it drives 14 m and eats 0.50 (down 69% from 1.62), and with every sensor blanked it stays put and eats 2.12 (up 31%).
- **conventional g300**: Yes, harmfully: a poor forager (0.25) that eats twice as much with its noses blanked (0.50) and 2.5 times as much with every sensor blanked (0.62).
- **conventional g590**: Yes, but not the noses: noses blanked changes nothing (1.38 to 1.50); every sensor blanked sends it 16 m away for 0.38 (down 72%), the orientation-and-velocity brake of 801's season-200 Pioneer.

### forage-w0.0-802

```
holistic     g  0 parts  6 units  25 sensors ['oscillator', 'up']
     intact: food 1.62 disp 1.60 path 7.2 work 3.2kJ  no_food: food 1.62 disp 1.60 path 7.2 work 3.2kJ  no_env: food 1.62 disp 1.60 path 7.2 work 3.2kJ  no_local: food 1.62 disp 1.60 path 7.2 work 3.2kJ
holistic     g100 parts  6 units  29 sensors ['oscillator', 'up']
     intact: food 0.62 disp 1.42 path 6.4 work 2.1kJ  no_food: food 0.62 disp 1.42 path 6.4 work 2.1kJ  no_env: food 0.62 disp 1.42 path 6.4 work 2.1kJ  no_local: food 0.62 disp 1.42 path 6.4 work 2.1kJ
holistic     g300 parts  8 units  21 sensors []
     intact: food 1.25 disp 2.56 path 8.2 work 5.2kJ  no_food: food 1.25 disp 2.56 path 8.2 work 5.2kJ  no_env: food 1.25 disp 2.56 path 8.2 work 5.2kJ  no_local: food 1.25 disp 2.56 path 8.2 work 5.2kJ
holistic     g590 parts  5 units  24 sensors ['height', 'velocity']
     intact: food 2.38 disp 2.20 path 6.9 work 2.1kJ  no_food: food 2.38 disp 2.20 path 6.9 work 2.1kJ  no_env: food 2.38 disp 2.20 path 6.9 work 2.1kJ  no_local: food 2.38 disp 2.20 path 6.9 work 2.1kJ
conventional g  0 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 0.62 disp 13.39 path 13.6 work 22.8kJ  no_food: food 0.88 disp 13.23 path 13.4 work 22.7kJ  no_env: food 0.50 disp 2.38 path 4.3 work 14.8kJ  no_local: food 0.50 disp 2.38 path 4.3 work 14.8kJ
conventional g100 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 1.50 disp 2.45 path 8.6 work 19.2kJ  no_food: food 0.88 disp 2.73 path 8.0 work 19.1kJ  no_env: food 0.38 disp 8.88 path 11.6 work 16.3kJ  no_local: food 0.38 disp 8.88 path 11.6 work 16.3kJ
conventional g300 parts  5 units  25 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 1.38 disp 2.69 path 9.3 work 20.1kJ  no_food: food 2.50 disp 2.89 path 8.4 work 20.4kJ  no_env: food 0.25 disp 0.54 path 1.8 work 18.6kJ  no_local: food 0.25 disp 0.54 path 1.8 work 18.6kJ
conventional g590 parts  5 units  26 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 2.00 disp 2.72 path 6.3 work 23.0kJ  no_food: food 1.00 disp 1.61 path 5.3 work 22.4kJ  no_env: food 0.88 disp 0.75 path 3.7 work 27.6kJ  no_local: food 0.88 disp 0.75 path 3.7 work 27.6kJ
```

- **holistic g0**: No: same season-0 best as the work-cost arm (same seed), 1.62 in every mode; blind.
- **holistic g100**: No: 0.62 in every mode; blind and weak.
- **holistic g300**: No: it carries no sensor of any kind; a pure oscillator mower at 1.25.
- **holistic g590**: No: height and velocity inputs only, 2.38 items in every mode on 2.1 kJ; the strongest blind mower in the four runs.
- **conventional g0**: Yes, harmfully: same genotype as the work-cost arm's season-0 best; noses blanked raises yield 42%, all sensors blanked halts the runaway.
- **conventional g100**: Yes: noses blanked drops 1.50 to 0.88 (down 41%), every sensor blanked to 0.38 with a 9 m runaway; the noses are part of what keeps it in the disc.
- **conventional g300**: Yes, both ways: noses blanked nearly doubles yield (1.38 to 2.50); every sensor blanked and it barely moves (1.8 m path, 0.25), so its drive is gated through the non-nose sensors.
- **conventional g590**: Yes: noses blanked halves yield (2.00 to 1.00) and shortens the path (6.3 to 5.3 m) rather than lengthening it, so this is not a brake; whether the noses steer or gate the drive the lesion cannot say. The most nose-dependent controller of the sixteen.

### forage-w0.03-803

```
holistic     g  0 parts  8 units  53 sensors ['joint_angle', 'velocity']
     intact: food 0.38 disp 0.45 path 6.7 work 2.9kJ  no_food: food 0.38 disp 0.45 path 6.7 work 2.9kJ  no_env: food 0.00 disp 0.61 path 6.6 work 3.6kJ  no_local: food 0.12 disp 0.79 path 6.8 work 3.7kJ
holistic     g100 parts  2 units  11 sensors ['height', 'oscillator']
     intact: food 1.50 disp 5.35 path 11.0 work 7.8kJ  no_food: food 1.50 disp 5.35 path 11.0 work 7.8kJ  no_env: food 0.62 disp 5.13 path 11.3 work 8.1kJ  no_local: food 0.25 disp 10.22 path 15.4 work 11.2kJ
holistic     g300 parts  6 units  19 sensors ['oscillator']
     intact: food 2.38 disp 2.12 path 8.8 work 5.8kJ  no_food: food 2.38 disp 2.12 path 8.8 work 5.8kJ  no_env: food 2.38 disp 2.12 path 8.8 work 5.8kJ  no_local: food 1.75 disp 4.57 path 10.3 work 5.4kJ
holistic     g590 parts  8 units  37 sensors ['height', 'joint_angle', 'joint_velocity', 'oscillator', 'velocity']
     intact: food 1.00 disp 3.15 path 11.4 work 2.7kJ  no_food: food 1.00 disp 3.15 path 11.4 work 2.7kJ  no_env: food 1.75 disp 3.91 path 11.1 work 3.4kJ  no_local: food 0.00 disp 0.41 path 0.5 work 0.1kJ
conventional g  0 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 0.62 disp 1.82 path 5.2 work 17.3kJ  no_food: food 0.38 disp 1.40 path 4.2 work 17.8kJ  no_env: food 0.75 disp 0.89 path 5.0 work 13.5kJ  no_local: food 0.75 disp 0.89 path 5.0 work 13.5kJ
conventional g100 parts  5 units  26 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 0.88 disp 0.90 path 7.1 work 22.2kJ  no_food: food 0.62 disp 2.84 path 3.8 work 14.5kJ  no_env: food 0.38 disp 4.08 path 8.3 work 14.3kJ  no_local: food 0.38 disp 4.08 path 8.3 work 14.3kJ
conventional g300 parts  5 units  25 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 0.88 disp 1.60 path 5.9 work 17.8kJ  no_food: food 1.25 disp 2.13 path 7.4 work 15.8kJ  no_env: food 0.38 disp 15.53 path 15.4 work 18.8kJ  no_local: food 0.38 disp 15.53 path 15.4 work 18.8kJ
conventional g590 parts  5 units  28 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 1.00 disp 1.21 path 6.2 work 22.0kJ  no_food: food 1.12 disp 1.46 path 6.6 work 23.2kJ  no_env: food 1.50 disp 1.63 path 6.7 work 26.8kJ  no_local: food 1.50 disp 1.63 path 6.7 work 26.8kJ
```

- **holistic g0**: Yes on tiny counts: 0.38 intact (3 items in 8 trials), 0.00 with every sensor blanked; joint-angle and velocity inputs, no nose.
- **holistic g100**: Yes, not a nose: a two-part body whose height input matters, 1.50 to 0.62 (down 59%) with the same 11 m path; silencing the local brains sends it 15 m away for 0.25.
- **holistic g300**: No: oscillator only, 2.38 items on 5.8 kJ in every sensor mode; blind, and the second-strongest mower in the four runs.
- **holistic g590**: Yes, harmfully: five sensor kinds and no nose; blanking them all raises yield 75% (1.00 to 1.75); with the local brains silenced it does not move.
- **conventional g0**: Yes on small counts: noses blanked 0.62 to 0.38 (down 39%, 5 items to 3 in 8 trials); every sensor blanked 0.75, so the nose effect is inside the noise of the others.
- **conventional g100**: Yes, marginally: noses blanked 0.88 to 0.62 (down 29%) with the path halved (7.1 to 3.8 m); every sensor blanked 0.38 with a 4 m runaway.
- **conventional g300**: Yes: noses blanked raises yield 43% (0.88 to 1.25); every sensor blanked and it drives 15.5 m away for 0.38, the orientation-and-velocity brake again.
- **conventional g590**: Yes, harmfully: noses blanked 1.00 to 1.12, every sensor blanked 1.50 (up 50%); the blind version eats more.

### forage-w0.0-803

```
holistic     g  0 parts  8 units  53 sensors ['joint_angle', 'velocity']
     intact: food 0.38 disp 0.45 path 6.7 work 2.9kJ  no_food: food 0.38 disp 0.45 path 6.7 work 2.9kJ  no_env: food 0.00 disp 0.61 path 6.6 work 3.6kJ  no_local: food 0.12 disp 0.79 path 6.8 work 3.7kJ
holistic     g100 parts  2 units  10 sensors ['oscillator']
     intact: food 1.25 disp 9.12 path 17.3 work 16.4kJ  no_food: food 1.25 disp 9.12 path 17.3 work 16.4kJ  no_env: food 1.25 disp 9.12 path 17.3 work 16.4kJ  no_local: food 0.50 disp 2.20 path 7.0 work 2.3kJ
holistic     g300 parts 12 units  40 sensors ['food', 'joint_velocity', 'oscillator']
     intact: food 1.75 disp 5.10 path 14.5 work 14.3kJ  no_food: food 1.88 disp 5.68 path 14.9 work 16.2kJ  no_env: food 1.88 disp 5.68 path 14.9 work 16.2kJ  no_local: food 1.88 disp 6.90 path 15.1 work 17.8kJ
holistic     g590 parts  3 units  18 sensors ['agent', 'oscillator', 'up', 'velocity']
     intact: food 1.50 disp 3.71 path 11.9 work 12.4kJ  no_food: food 1.50 disp 3.71 path 11.9 work 12.4kJ  no_env: food 1.75 disp 4.14 path 10.7 work 8.4kJ  no_local: food 2.00 disp 2.84 path 8.0 work 5.4kJ
conventional g  0 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 1.62 disp 1.44 path 7.1 work 15.6kJ  no_food: food 1.75 disp 1.31 path 7.2 work 14.4kJ  no_env: food 0.12 disp 0.55 path 1.9 work 21.0kJ  no_local: food 0.12 disp 0.55 path 1.9 work 21.0kJ
conventional g100 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 1.38 disp 1.36 path 8.4 work 22.4kJ  no_food: food 0.75 disp 1.59 path 7.1 work 22.1kJ  no_env: food 0.75 disp 3.81 path 11.3 work 19.1kJ  no_local: food 0.75 disp 3.81 path 11.3 work 19.1kJ
conventional g300 parts  5 units  24 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 2.12 disp 2.60 path 8.4 work 20.2kJ  no_food: food 1.62 disp 2.99 path 9.2 work 21.1kJ  no_env: food 1.25 disp 2.26 path 7.9 work 16.2kJ  no_local: food 1.25 disp 2.26 path 7.9 work 16.2kJ
conventional g590 parts  5 units  23 sensors ['agent', 'contact', 'food', 'height', 'joint_velocity', 'up', 'velocity']
     intact: food 1.62 disp 1.98 path 7.1 work 16.5kJ  no_food: food 2.25 disp 1.78 path 6.6 work 15.6kJ  no_env: food 0.88 disp 1.73 path 4.5 work 15.8kJ  no_local: food 0.88 disp 1.73 path 4.5 work 15.8kJ
```

- **holistic g0**: Same season-0 best as the work-cost arm: 0.38 intact, 0.00 with every sensor blanked, on tiny counts.
- **holistic g100**: No: oscillator only, 1.25 in every sensor mode; a 17 m mower on 16.4 kJ, expensive because moving is free here.
- **holistic g300**: No: it carries a food nose and the nose does nothing (1.75 intact, 1.88 blanked, within 8%); a 14.5 m mower on 14.3 kJ.
- **holistic g590**: No: agent nose, orientation and velocity, and every sensor blanked changes yield by 17% (1.50 to 1.75); silencing the local brains raises it to 2.00 on less energy.
- **conventional g0**: Yes, not the noses: noses blanked 1.62 to 1.75; every sensor blanked and it stalls at 1.9 m for 0.12 (down 93%), drive gated through the non-nose sensors.
- **conventional g100**: Yes: noses blanked 1.38 to 0.75 (down 46%), the same as every sensor blanked, so the noses are the sensors that matter here; path shortens slightly (8.4 to 7.1 m), not a runaway brake.
- **conventional g300**: Borderline: noses blanked 2.12 to 1.62 (down 24%, just under the line), every sensor blanked 1.25 (down 41%); the best Pioneer of the four runs, and a partly nose-dependent one.
- **conventional g590**: Yes, harmfully: noses blanked raises yield 39% (1.62 to 2.25); every sensor blanked 0.88 (down 54%).

## 3. Comparison with seed 801

Seed 801 numbers are from `docs/foraging-world.md`; its season-10 gain and pre-wave births are from the 13-season re-run in section 4. Gains are at seasons 100 / 300 / 500 / 599. "Sustained crossover" is the first season from which the holistic mean gain stays above the wheeled for ten seasons running. Heritability for 801 is quoted as the docs give it, pooled across both arms.

| run | hol minimum alive (season) | hol back at 60 | hol births before the wave (s0 to 11) | hol gain at s10 | hol gain 100/300/500/599 | wheel gain 100/300/500/599 | sustained crossover | founders hol / wheel | heritability hol / wheel |
|---|---|---|---|---|---|---|---|---|---|
| 801 w0.03 (docs) | 7 (11) | 32 | 11 | +0.05 | +1.02 / +1.19 / +1.63 / +1.41 | +0.96 / +1.03 / +0.94 / +0.95 | 83 | 1 / 7 | 0.51 / 0.24 to 0.39 |
| 801 w0.0 (docs) | "matches in shape" | | | | +0.97 / +1.34 / +1.28 / +1.24 | +0.98 / +1.00 / +1.00 / +1.14 | not given | 1 / 12 | (pooled above) |
| 802 w0.03 | 31 (11) | 15 | 30 | +0.18 | +1.05 / +1.10 / +1.07 / +1.04 | +0.96 / +0.90 / +0.96 / +0.86 | 18 | 3 / 15 | 0.32 / 0.14 |
| 802 w0.0 | 32 (11) | 14 | 24 | +0.24 | +0.96 / +1.12 / +1.19 / +1.06 | +1.03 / +0.94 / +0.97 / +0.86 | 30 | 3 / 17 | 0.44 / 0.39 |
| 803 w0.03 | 42 (11) | 13 | 39 | +0.25 | +0.96 / +1.02 / +1.00 / +0.97 | +0.82 / +0.96 / +0.99 / +0.93 | 11 | 3 / 12 | 0.28 / 0.20 |
| 803 w0.0 | 36 (11) | 14 | 31 | +0.21 | +1.05 / +1.28 / +1.23 / +1.29 | +0.83 / +0.98 / +1.07 / +1.07 | 19 | 3 / 13 | 0.28 / 0.25 |

Mean holistic-minus-wheeled margin over seasons 100 to 599: +0.21, +0.13, +0.13, +0.19 a season (802 w0.03, 802 w0.0, 803 w0.03, 803 w0.0). Over the last ten seasons: hol +1.03 / wheel +0.85, +1.02 / +0.90, +0.94 / +0.88, +1.27 / +1.08.

Deaths at season 11: 801 37, 802 w0.03 38, 802 w0.0 39, 803 w0.03 30, 803 w0.0 36.

## 4. Check: seed 801 under the current code, 13 seasons (`check-801/`)

Because the new bottlenecks were so much shallower than the docs' 60 to 7, seed 801 was re-run with the ticket's command for 13 seasons on the same commit. Holistic alive at seasons 0 to 12: 59, 60, 60, 58, 54, 55, 53, 53, 50, 47, 42, 7, 7; deaths at season 11: 37; mean gain +0.04 at season 0, +0.05 at season 10, +0.32 among the seven at season 11. That is the docs' 60 to 7 at season 11 exactly. The depth of 801's bottleneck is the seed, not a change in the code since the docs were written.

## 5. Verdict

**The bottleneck-and-recovery reproduces in kind and not in depth.** In all four runs the founders that never ate starved together at season 11, the horizon set by the initial energy of 3 and the basal cost of 0.25, and the starvation wave was the same size as 801's (30 to 39 deaths against 37). What differs is what the population was made of when the wave hit. On 801 the founders ate almost nothing for ten seasons (mean gain +0.05 at season 10) and bred 11 children before the wave; on 802 and 803 they ate three to five times as much (+0.18 to +0.25) and bred 24 to 39, so when the non-eaters died the population already held two dozen eaters' offspring, the minimum was 31 to 42 rather than 7, and capacity was back in two to four seasons rather than twenty-one. Three founders survive in every final ancestry against 801's one, still far below the neutral control's fourteen, so this is selection through starvation as the docs say, on a seed whose founders had less far to fall. Across five seeds the season-11 minimum is 7, 31, 32, 36, 42: the docs' 60 to 7 is the extreme of the five and should not be read as the typical case.

**The holistic side overtakes in all four runs, and earlier.** The sustained lead begins at season 11 to 30 (801: 83) and holds for 450 to 566 of 600 seasons, at +0.13 to +0.21 a season averaged over seasons 100 to 599. Two things from 801 do not reproduce. The holistic climb to +1.63 at season 500 does not: here the holistic mean plateaus at +1.0 to +1.3 from season 30 to the end, in both arms. And the size of the lead varies: in 803 under the work cost the two populations are at parity by the end (+0.94 against +0.88 over the last ten seasons), the smallest and least secure of the four overtakes. The wheeled side is flat at +0.8 to +1.1 throughout in every run, as on 801. Nothing flips between the work-cost arms: bottleneck, recovery, crossover and founders agree within a seed across the two arms, so none of it is a finding about the coefficient.

**Every holistic best is a blind mower, as on 801.** Thirteen of sixteen show no sensor lesion above the 25% line; the three that do (803 under the work cost at seasons 0, 100 and 590) have no nose, and the inputs that matter are joint angle, height and velocity, one of them harmful (blanking every sensor raises the season-590 best's yield 75%). Three holistic bests carry a food or agent nose and none of them uses it. The strongest mowers eat 2.38 items alone on 2.1 kJ (802 free work, season 590) and 5.8 kJ (803 work cost, season 300).

**The Pioneer's noses matter more often here than the docs found, and still never as a compass.** On 801 the docs report one Pioneer best in six hundred seasons of either arm whose noses demonstrably worked (season 500, a brake). Here blanking the noses moves the yield by more than a quarter in ten of sixteen Pioneer bests: six lose (802 w0.03 s100, 802 w0.0 s100 and s590, 803 w0.03 s0 and s100, 803 w0.0 s100) and four gain (802 w0.03 s0, 802 w0.0 s300, 803 w0.03 s300, 803 w0.0 s590). In the losing cases where the path lengthens with the noses blanked (802 w0.03 s100: 6 m to 14 m) it is the brake the docs describe. In two (802 w0.0 s590: 2.00 to 1.00 with the path shortening from 6.3 to 5.3 m; 803 w0.0 s100: 1.38 to 0.75) the path does not lengthen, which is what nose-gated drive would look like and also what steering would look like, and this probe cannot tell them apart. So the docs' claim that the wheeled noses never steered toward food is neither confirmed nor contradicted by these runs: it is untested by a solo lesion, and a test that could settle it (a yield slope against food density, or a track of heading against the nearest item) was not asked for and was not run. The controllers where every environmental sensor matters but the noses do not (802 w0.03 s590, 803 w0.03 s300, 803 w0.0 s0) are the orientation-and-velocity circling the docs found at 801's season 200.

**What smells.**
1. The free-work arm's "cheap blind mowing" is not a general result. 801's free arm ended on a 1.8 kJ mower and 802's on 2.1 kJ, but 803's free-arm holistic bests spend 16.4 kJ at season 100, 14.3 at 300 and 12.4 at 590, four to eight times the work-cost arm's bests on the same seed. With the work cost at zero nothing selects for cheapness, so the cheap mowers on 801 and 802 are drift, and the docs' sentence about the free arm ("cheap blind mowing on the evolved side") describes a seed, not the arm.
2. Holistic yield heritability is 0.28 to 0.44 here against the docs' 0.51 for 801; wheeled 0.14 to 0.39 overlaps the docs' 0.24 to 0.39 except for 802 under the work cost at 0.14. The rule used here requires every parent to have five or more evaluations; the docs do not state their rule, so part of the gap may be the rule.
3. The mean gain is the survivors' average, so it jumps across the starvation wave by removing the non-eaters (801: +0.05 at season 10, +0.32 among the seven at 11; 802 w0.03: +0.18 to +0.39) without any individual improving. The recovery-phase rise in every run, 801 included, is partly that artifact and partly the eaters' children, and this readout does not separate them.
4. Several probe yields rest on tiny counts: the 803 season-0 holistic best's "sensors matter" is 3 items against 0 in 8 trials, and the Pioneer season-0 nose effects are 5 against 3. They are reported because the rule says to, and should not be read.
5. The one Pioneer controller in these runs with a nose effect that is not a brake (802 free work, season 590, the most nose-dependent of the sixteen) appeared in the arm where moving is free, where the docs argued sensing should matter least. One controller is not a trend, but it is the place to point a steering test if one is run.
