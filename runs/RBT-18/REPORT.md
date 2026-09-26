# RBT-18, world fan-out arm W6: expensive movement (work cost 0.15 per kJ, 12 items, seed 801)

One flag changed from the baseline `forage-801`: `--work-cost 0.15` (five times the baseline 0.03). Everything else as in the issue's command line. Base commit e09ff7b on `claude/new-session-4cao7d`; 113 tests passed before the run.

**Result in one line.** Both populations went extinct before any selection on wiring could act: the wheeled side at season 3, the holistic side at season 33. The run asked for 600 seasons and ended at 33. Nothing in it can say whether sensing has a slope, because nothing in it lived long enough to be selected.

**About the coefficient.** This arm deliberately leans on the work-cost coefficient that `docs/foraging-world.md` flags as the place a thumb could rest. Everything below is a finding about that coefficient at this value. The within-run lesion results are reported; the holistic-versus-wheeled comparison is not interpreted, since at 0.15 per kJ the two bodies' random work budgets (0.01 kJ against 17.5 kJ median) decide the outcome before evolution starts.

## Ecology readout

Mean lifetime gain is the mean over an individual's seasons of (items eaten x 1) minus 0.15 x kJ, before the 0.25 basal cost. From `history.txt`:

| season | holistic alive | births | deaths | mean gain | wheeled alive | births | deaths | mean gain |
|---|---|---|---|---|---|---|---|---|
| 0 | 58 | 3 | 5 | -0.02 | 31 | 1 | 30 | -1.60 |
| 1 | 60 | 3 | 1 | +0.04 | 8 | 0 | 23 | -0.81 |
| 2 | 60 | 1 | 1 | +0.04 | 2 | 0 | 6 | -0.47 |
| 3 | 60 | 1 | 1 | +0.02 | 0 | 0 | 2 | extinct |
| 11 | 2 | 0 | 35 | +0.29 | | | | |
| 20 | 2 | 1 | 0 | +0.23 | | | | |
| 32 | 1 | 0 | 0 | +0.32 | | | | |
| 33 | 0 | 0 | 1 | extinct | | | | |

Seasons 60 and beyond do not exist. Full per-season table in `history.txt`.

**Wheeled: extinct at season 3.** Thirty of sixty Pioneers died in season 0 itself. Dying in one season from 3 energy needs a season gain of -2.75 or worse, that is more than 18 kJ of work without an item; the calibration's median random Pioneer spends 17.5 kJ, so half the founders were over the line on their first season. Of the 31 survivors of season 0, 84% had spent more than 5 kJ and 58% more than 10 kJ; the mean gain was -1.60. Eight were alive after season 1, two after season 2, none after season 3. One child was born (from `c0-8`, the season-0 best) and died with its parent's cohort. Founders at the last season with survivors (season 2): 2 of 2, both generation-0 individuals. The pre-registered expectation was that the wheeled side starves early unless controller evolution finds economy fast; it starved before controller evolution had a second generation to work with.

**Holistic: bottleneck at season 11 as in the baseline, no recovery, extinct at season 33.** The founders that never ate ran their 3 energy down by 0.25 a season and 35 starved together at season 11, the same season as the baseline's 60 to 7. The difference is the size of the remnant and its budget. Two founders survived: `h0-51`, which spends almost nothing and ate one item in fifteen seasons, and `h0-7`, which eats about half an item a season. `h0-51` starved at season 15. `h0-7` reached age 60 at season 33 with 0.21 energy left, which its next season's costs would have taken anyway, and bred twice, at seasons 20 and 21, after a one-off season in which it ate four items; both children ate a little (lifetime gain +0.07 and +0.15) and starved at ages 4 and 9. Between seasons 4 and 10 the population shed 23 more than it bred: 10 age-outs over the whole run, and the rest starvation, including eight of the eleven children born in seasons 0 to 8, which start on 1 energy and last four seasons without eating. Founders at the last season with survivors (season 32): 1 of 1.

**Why `h0-7` could not refound the population.** Its per-season gains alternate between +0.83 (one item, 0.17 of work) and -0.17 (no item, the same work): it spends about 1.1 kJ a season and eats one item in roughly two seasons. At 0.15 per kJ that is a lifetime mean of +0.32 against a basal cost of 0.25, a net of +0.07 a season, so about fifteen seasons from birth energy to the breeding threshold. At the baseline 0.03 per kJ the same lump would net about +0.20 a season and breed every five. The baseline docs say a lump's budget never depended on the work cost; that holds for the median lump (79% of the holistic founders spent under 0.1 kJ in season 0) and fails for the one lump that mattered, whose 1.1 kJ costs two thirds of a basal cost at this coefficient. The season-0 and season-10 holistic bests here (`h0-49`, path 2.3 m; `h0-7`, path 2.9 m) match the baseline's reported paths at seasons 0 and 10, as expected for the same seed, which is consistent with `h0-7` being the baseline's single founder; I could not check this directly since the baseline run files are not in the repository.

**Yield heritability.** Not measurable. Child with at least five evaluations: one on the holistic side (`he71`, lifetime gain +0.15, parent `h0-7` at +0.32), none on the wheeled side. No correlation is reported.

## Probes (eight fresh seeds each, robot alone in the arena; `probe.txt`)

Bests exist only at holistic seasons 0, 10, 20, 30 and wheeled season 0; the issue's 100, 300 and 590 do not exist. The holistic best at 10, 20 and 30 is the same individual, `h0-7`.

| best | sensors | intact items / path / work | items per kJ | no_food | no_env | no_local |
|---|---|---|---|---|---|---|
| holistic s0 `h0-49` (4 parts, 29 units) | oscillator, up | 0.00 / 2.3 m / 0.7 kJ | 0 | 0.00, same path and work | 0.00 | 0.12 on 0.3 kJ |
| holistic s10-30 `h0-7` (4 parts, 20 units) | joint_angle only | 0.50 / 2.9 m / 1.1 kJ | 0.45 | 0.50 / 2.9 m / 1.1 kJ | 0.50 / 2.9 m / 1.1 kJ | 0.62 / 2.8 m / 1.0 kJ (0.62 per kJ) |
| wheeled s0 `c0-8` (Pioneer, 24 units) | food x3, agent x3, contact, height, joint_velocity x2, up, velocity | 0.88 / 7.5 m / 22.9 kJ | 0.038 | 0.38 / 4.0 m / 21.7 kJ (0.018 per kJ) | 0.12 / 3.6 m / 17.0 kJ | 0.12 / 3.6 m / 17.0 kJ |

One sentence per best:

- `h0-49` eats nothing alone on any lesion; its season-0 group score of 1.87 was a matter of where the food and its group mates fell, and no sensor matters (it has no nose).
- `h0-7` carries no food or agent sensor, and blanking its one joint-angle sensor, or every sensor, changes neither its path, its work nor its yield to two decimals; silencing its local brains raises its yield by a quarter on a tenth less work, so no sensor matters and the local brains are a small drag: a blind mower, the same kind of thing the baseline found.
- `c0-8` is the one controller in the run whose noses demonstrably work: blanking the food and agent sensors more than halves its yield (0.88 to 0.38 items) and halves its economy (0.038 to 0.018 items per kJ), and blanking every environmental sensor leaves 0.12; but the noses buy half an item, that is 0.5 energy, a season, against a work bill of 3.4 energy at this coefficient, so the robot that uses its nose best is bankrupt by 2.8 a season and died at season 2.

**`c0-8` wiring, since `no_food` halves its yield.** `controller_descriptors`: 24 units, 16 sensors, 6 tanh neurons, 2 effectors both driven, 120 links, mean |weight| 0.87, centralisation 1.0 (all six neurons global), 6 cyclic units, mean sensor path 2.0, both effectors environment-driven, none oscillator-driven. Food sensors sit on parts 0, 1 and 2, that is the chassis and both drive wheels; agent sensors on the same three parts. This is the designed Pioneer's stock nose layout with a random dense controller, the Braitenberg pairing the docs describe as available to the designed body from the start.

## Against the baseline

Baseline figures from the issue and `docs/foraging-world.md` (forage-801, work cost 0.03); items per kJ from the docs' probe numbers where both items and kJ are given.

| | baseline (0.03 per kJ) | this arm (0.15 per kJ) |
|---|---|---|
| holistic population | 60 to 7 at season 11, 60 again by 32, full to 599 | 60 to 2 at season 11, extinct at 33 |
| wheeled population | kept 16 of 60 at season 39, full to 599 | 31, 8, 2, 0 over seasons 0 to 3 |
| holistic founders in final ancestry | 1 of 60 | 1 of 1 at season 32 (then none) |
| wheeled founders in final ancestry | 7 of 60 | 2 of 2 at season 2 (then none) |
| holistic mean gain, seasons 100/300/500/599 | +1.02 / +1.19 / +1.63 / +1.41 | none; +0.32 at season 32 (one individual) |
| wheeled mean gain, seasons 100/300/500/599 | +0.96 / +1.03 / +0.94 / +0.95 | none; -0.47 at season 2 (two individuals) |
| holistic best, items per kJ | s100: 2.25 on 4.8 kJ = 0.47; s150: 2.5 on 5.6 = 0.45; s300: 1.75 on 2.3 = 0.76 | s10-30 `h0-7`: 0.50 on 1.1 kJ = 0.45 |
| wheeled best, items per kJ | random Pioneer ~1 on 17.5 kJ = 0.06; s100: 1.0 on 20 kJ = 0.05 | s0 `c0-8`: 0.88 on 22.9 kJ = 0.038 |
| holistic best path, seasons 0 / 10 / 20 / 30 | 2.3 / 2.9 / 3.9 / 7.2 m | 2.3 / 2.9 / 2.9 / 2.9 m (the same individual from 10 on) |
| sensor lesion on any holistic best | none changes yield | none changes yield |
| nose-dependent controller | Pioneer best at s0 (five sixths of food lost when blanked), s500 (a brake) | Pioneer best at s0 only (57% of food lost when blanked); dead at s2 |
| yield heritability | 0.51 holistic, 0.24-0.39 wheeled | not measurable (one qualifying child) |

## Does this variant give sensing a slope?

Not one that anything could climb. Raising the work cost to 0.15 per kJ did make path length expensive, as intended: the Pioneer's 17 to 23 kJ of random driving now costs 2.6 to 3.4 energy a season against a yield of about one item, which is why half the wheeled founders died in their first season and the population was gone in four; the one Pioneer that used its nose was the one that eked out 0.88 items, and its nose bought it half an item against a three-energy work bill. On the holistic side the coefficient did not touch the median lump, which spends nothing and starves at season 11 exactly as in the baseline, but it did touch the one founder that eats, whose 1.1 kJ a season went from a rounding error to two thirds of a basal cost and turned it from the baseline's breeder into a subsister that bred twice in sixty seasons. The arm therefore did not reach the stage where the question applies: selection for cheaper locomotion and then for a nose needs a breeding population, and at this coefficient there was none on either side on seed 801. What the arm measures is the coefficient, as the docs warned it might: at 0.03 per kJ the world has a fauna that mows, at 0.15 it has no fauna, and the only nose that worked was a founder's, paying for itself at 0.5 energy a season and losing that to its wheels. A work cost that punishes mowing without emptying the world would have to sit between the two, and the value at which a 1.1 kJ blind mower still breeds is about 0.1 per kJ (net +0.12 a season) on the arithmetic above; that is a suggestion for a further arm, not a result of this one.

## Files

`runs/RBT-18/W6-801/` (config.json, history.json, lineage.jsonl, holistic/best_gen0000-0030.json, conventional/best_gen0000.json; `<kind>/final/` are empty since both populations were extinct), `W6-801.log`, `history.txt`, `lineage_readout.txt`, `probe.txt`, this report. The `runs/` directory is gitignored in the repository and was added with `git add -f`.
