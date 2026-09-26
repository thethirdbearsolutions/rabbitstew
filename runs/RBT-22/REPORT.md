# RBT-22 — W1', readable long-range smell: normalised intensity sensor, then decay 3 m at baseline density (seed 801)

The corrected W1 arm. RBT-13 ran long-range smell and found that the `i/(1+i)` squash saturates at twelve items and 3 m decay, so that arm delivered range at the price of resolution and never tested range on its own. This arm adds normalised smell modes, measures which one actually has a slope, and re-runs W1 with it. Only change from the baseline `forage-801`: `--food-decay 3.0 --smell log`. Nothing else touched, nothing tuned.

Run: `runs/RBT-22/W1b-801`, 600 seasons, seed 801, completed without interruption. Code: PR [#3](https://github.com/thethirdbearsolutions/rabbitstew/pull/3) on `feature/RBT-22`.

## 1. Signal range, measured before the arm (`smell_range.py`, `smell_range.txt`)

Signal read by a nose at 0 / 2 / 3 / 4 m from the centre of a 12-item, 3 m disc, and the slope per metre there, over 4000 random layouts. The first two rows reproduce RBT-13's table to the reported precision, so this is the same measurement on the same quantity.

| smell | decay | signal at 0 / 2 / 3 / 4 m | slope per metre at 0 / 2 / 3 / 4 m | over one eat radius (0.35 m) at 3 m | 0.5 m vs 2.5 m from an item |
|---|---|---|---|---|---|
| `sum` | 1 m | 0.67 / 0.61 / 0.48 / 0.29 | 0.046 / 0.091 / 0.179 / 0.179 | 0.063 | 0.160 |
| `sum` | 3 m | 0.86 / 0.84 / 0.81 / 0.76 | 0.007 / 0.024 / 0.042 / 0.055 | 0.015 | 0.039 |
| `mean` | 3 m | 0.35 / 0.31 / 0.26 / 0.21 | 0.013 / 0.037 / 0.052 / 0.050 | 0.018 | 0.065 |
| `log` | 3 m | 0.78 / 0.72 / 0.65 / 0.56 | 0.019 / 0.057 / 0.085 / 0.090 | 0.030 | 0.100 |

`mean` lands in the 0.3–0.5 band the issue predicted. `log` has the larger slope at every radius inside the disc and the larger 0.5 m-to-2.5 m span, so **the arm ran `--smell log`**, per the issue's pick-the-steeper rule.

Stated plainly, because it bounds what this arm can conclude: `log` at 3 m decay still reads a gradient about half as steep per metre as plain `sum` at 1 m (0.085 against 0.179 at 3 m from centre). Normalising recovers most of what the saturation cost, not all of it. This arm therefore tests a *readable* long-range nose, not one as sharp as the baseline's short-range nose.

## 2. Ecology readout (`readout.py`, `readout.txt`)

| season | holistic alive | births | deaths | mean gain | wheeled alive | births | deaths | mean gain |
|---|---|---|---|---|---|---|---|---|
| 0 | 59 | 3 | 4 | +0.04 | 60 | 2 | 2 | −0.17 |
| 11 | 14 | 2 | 37 | +0.33 | 60 | 9 | 9 | +0.65 |
| 20 | 60 | 3 | 3 | +1.08 | 60 | 0 | 0 | +0.66 |
| 32 | 60 | 2 | 2 | +0.95 | 60 | 5 | 5 | +0.61 |
| 60 | 60 | 0 | 0 | +1.03 | 60 | 2 | 2 | +0.75 |
| 100 | 60 | 0 | 0 | +1.10 | 60 | 2 | 2 | +0.76 |
| 200 | 60 | 2 | 2 | +1.02 | 60 | 2 | 2 | +0.80 |
| 300 | 60 | 0 | 0 | +1.14 | 60 | 2 | 2 | +0.82 |
| 400 | 60 | 2 | 2 | +1.35 | 60 | 3 | 3 | +0.85 |
| 500 | 60 | 2 | 2 | +1.40 | 60 | 1 | 1 | +1.05 |
| 599 | 60 | 1 | 1 | +1.70 | 60 | 1 | 1 | +1.01 |

- Bottleneck: holistic min alive **14 at season 11** (37 starved in one season), recovered to 60 at **season 19**. Wheeled never dipped below 60. No extinction. This is the shallowest bottleneck of the family (baseline 7, RBT-13 8, RBT-17 3).
- Crossover: holistic leads wheeled from **season 19**, the season it regained capacity, and in 573 of the 581 seasons from there on. Averaged over seasons 19 to 599: holistic **+1.25**, wheeled **+0.86**.
- The raw "first season holistic exceeds wheeled" reading is season 0, where both populations are random founders that have barely eaten and the ranking is a coin flip. That number is not comparable to RBT-13's 20 or the baseline's 83, so the post-recovery reading above is the one quoted. The first season after which holistic stays above wheeled with no exceptions at all is 272.
- Turnover: 831 holistic births/deaths, 1125 wheeled.

Founders at season 599: holistic **1 of 60**, wheeled **14 of 60**.

Yield heritability (parent–child Pearson r on lifetime mean yield, child and all parents with evals ≥ 5): holistic **r = 0.563** (n = 633), wheeled **r = 0.262** (n = 711). The holistic figure is the highest in the family.

## 3. Probes (`probe.txt`; `scripts/forage_probe.py runs/RBT-22/W1b-801 0,100,300,590 8`)

```
holistic     g  0 parts  4 units  29 sensors ['oscillator', 'up']
     intact: food 0.00 disp 0.27 path 2.3 work 0.7kJ  no_food: 0.00  no_env: 0.00  no_local: 0.12
holistic     g100 parts  5 units  26 sensors ['joint_angle']
     intact: food 2.00 disp 1.70 path 9.0 work 17.4kJ  no_food: 2.00  no_env: 2.00  no_local: 2.00
holistic     g300 parts  6 units  40 sensors ['joint_angle', 'velocity']
     intact: food 2.75 disp 2.56 path 9.1 work 7.9kJ  no_food: 2.75  no_env: 2.12  no_local: 2.62
holistic     g590 parts  4 units  30 sensors ['joint_angle']
     intact: food 1.00 disp 2.08 path 7.8 work 7.3kJ  no_food: 1.00  no_env: 4.38  no_local: 4.38
conventional g  0  intact: food 1.12 disp 14.53 path 18.0 work 26.4kJ  no_food: 0.88  no_env: 1.00  no_local: 1.00
conventional g100 intact: food 1.12 disp  1.26 path  5.3 work 17.9kJ  no_food: 1.00  no_env: 0.75  no_local: 0.75
conventional g300 intact: food 1.12 disp  1.13 path  7.5 work 26.9kJ  no_food: 0.75  no_env: 0.75  no_local: 0.75
conventional g590 intact: food 1.00 disp  1.37 path  6.8 work 22.4kJ  no_food: 1.75  no_env: 0.75  no_local: 0.75
```

One sentence per best, a sensor "mattering" being a lesion that moves items eaten by more than 25%:

- **holistic g0**: no nose, eats nothing, nothing matters.
- **holistic g100**: one joint-angle sensor, no nose; every lesion identical to intact — blind mowing, expensively, on 17.4 kJ.
- **holistic g300**: the arm's best mower, 2.75 items on 7.9 kJ; no nose; blanking all env sensors costs 23%, just under threshold.
- **holistic g590**: no nose, and **its own sensorium is a handicap** — 1.00 items intact against 4.38 with env sensors blanked. Examined in §5.
- **Pioneer g0**: unlike RBT-13's, the season-0 noses are not catastrophic here (1.12 intact against 0.88 blanked); this is the de-saturation showing up, see §7.
- **Pioneer g100**: noses worth 11%, inside noise.
- **Pioneer g300**: noses worth 33% on 8 seeds, the only best over threshold; examined in §4.
- **Pioneer g590**: noses *hurt*, 1.00 intact against 1.75 blanked.

### Every saved holistic best, and the nosed members of the final population

`nosed_bests.py` / `holistic_sensors_by_gen.txt`: **0 of 60 saved holistic bests carry a food or agent sensor at all.** The issue's instruction to probe every saved holistic best that carries a food sensor has an empty set — the first arm in the family where that is true. RBT-13 had 7, RBT-17 had many.

The final population does carry noses, so those were probed instead (`probe_final_nosed.py`, `probe_final_nosed.txt`). Of the 60 final holistic members:

| level | count |
|---|---|
| declare a smell sensor in the genotype | 10 |
| express one in the synthesised body | 7 |
| have one wired into the controller | **0** |

All 7 expressed noses are **unlinked**: zero outgoing links, so blanking them is provably a no-op, which the probe confirms at `+0%` for all seven. Yields range 0.25 to 2.12 items on 2.2 to 12.1 kJ.

## 4. Pioneer g300, the one best over threshold: brake, compass, or noise?

On 8 seeds the nose was worth 33%. Checked properly it is neither a compass nor, at this sample size, a real effect.

`brake_or_compass.txt`, 16 seeds:

| mode (n = 16) | items eaten | path (m) | time inside the 3 m disc | mean distance from centre (m) | items per metre of in-disc path |
|---|---|---|---|---|---|
| intact | 0.94 ± 0.37 | 7.7 | 0.78 | 2.36 | 0.172 |
| no_food | 0.69 ± 0.25 | 8.4 | 0.70 | 2.65 | 0.130 |
| no_env | 0.69 ± 0.25 | 9.2 | 0.58 | 2.98 | 0.162 |

`forage_lab_conventional300.txt`, 12 fresh draws on a different seed block:

| mode (n = 12) | items | path (m) | in-disc | mean r (m) | items per m in-disc | work (kJ) |
|---|---|---|---|---|---|---|
| intact | 1.67 ± 0.41 | 7.9 | 0.89 | 2.03 | 0.247 | 26.9 |
| no_smell | 1.42 ± 0.36 | 9.1 | 0.86 | 2.15 | 0.186 | 27.4 |
| no_env | 1.25 ± 0.43 | 8.0 | 0.95 | 1.93 | 0.167 | 27.4 |
| no_global | 0.50 ± 0.15 | 3.3 | 0.89 | 2.03 | 0.175 | 14.4 |

Three readings of the same robot give the nose 33% (8 seeds), 27% (16 seeds) and 15% (12 draws), with error bars that overlap zero in each. **The honest conclusion is that no effect of this size is measurable at these sample sizes**, which is itself worth recording: RBT-13's and RBT-17's nose effects were read off comparable n.

The direction, where there is one, is the brake signature again and not a compass. Without the nose the robot spends less of the season inside the disc and sits further from the centre. And it never beats chance: a blind mow of its in-disc path should collect 2 × eat radius × density = **0.297 items per metre**, and intact it gets 0.247. It is eating *below* the blind-mow rate with its nose on.

That 0.297 is the rate for a point robot sweeping a fresh straight line. A real body eats when *any* of its geoms comes within the eat radius, so a five-part Pioneer sweeps a corridor wider than 0.7 m and should beat 0.297 without any sensing at all; conversely a robot that retraces its path or circles beats it for a reason unrelated to search. The figure is therefore a useful floor, not a chemotaxis test: falling below it (as this robot does) is damning, and exceeding it is not evidence of anything.

What actually drives it, from the per-unit lesions: one wheel effector (+75% of yield), a chassis velocity sensor (+60%), a chassis up sensor (+50%), then two global neurons. Its drive is gated through orientation and velocity, exactly as RBT-13's g300 was. `lab.py` on the same champion (`lab_conventional300.txt`) agrees and adds nothing a forager reading can use, which is what RBT-28 was filed about.

## 5. Holistic g590: a best that its own sensors make worse

`forage_lab_holistic590.txt`, 12 draws:

| mode (n = 12) | items | change |
|---|---|---|
| intact | 2.17 ± 0.42 | — |
| no_smell | 2.17 | 0.00 (it has no nose) |
| no_env | 3.09 | **+0.92** |
| no_global | 3.17 | **+1.00** |
| no_local | 3.09 | +0.92 |

Every single-unit lesion in this robot costs **0.00 or less**: not one unit is load-bearing for yield, and several help when removed. The 8-seed probe's dramatic 1.00-against-4.38 shrinks to 2.17-against-3.09 on 12 draws and a different seed block, but the sign is stable. The arm's final holistic best is strictly worse than its own lesioned versions, its joint-angle sensor being the handicap. Selection is on lifetime energy across many seasons in groups of four, not on solo yield, so this is not a contradiction; it does mean the fittest lineage is carrying sensory baggage it would be better off without.

## 6. Wiring (`wiring.txt`)

Pioneer g300 and g590, food and agent sensors and their outgoing links:

- g300: **chassis** food nose → five global neurons (weights +0.60 to −1.61). Wheel food noses on parts 1 and 2: **no outgoing links at all**.
- g590: chassis food nose → five global neurons. Wheel food nose on part 1: none; on part 2: a single link into one local unit.

No crossed pairing of the two wheel noses in either. That is now **seven arms in a row** in which the designed body arrives wired for a Braitenberg circuit and evolution routes only the chassis nose into the global brain instead. On the evolved side this arm goes further than any predecessor: of the ten final lumps that declare a nose, not one wires it to anything.

## 7. Against the baseline and RBT-13

| | baseline forage-801 (sum, 1 m) | RBT-13 W1 (sum, 3 m) | **RBT-22 W1' (log, 3 m)** |
|---|---|---|---|
| signal slope per metre at 3 m | 0.179 | 0.042 | **0.085** |
| holistic bottleneck | 60 → 7 at 11, back by 32 | 60 → 8 at 11, back by 23 | **60 → 14 at 11, back by 19** |
| holistic mean gain @ 100 / 300 / 500 / 599 | +1.02 / +1.19 / +1.63 / +1.41 | +1.21 / +1.36 / +1.05 / +1.19 | **+1.10 / +1.14 / +1.40 / +1.70** |
| wheeled mean gain @ 100 / 300 / 500 / 599 | +0.96 / +1.03 / +0.94 / +0.95 | +0.84 / +0.79 / +0.92 / +0.82 | **+0.76 / +0.82 / +1.05 / +1.01** |
| crossover (post-recovery reading) | 83 | 20 | **19** |
| founders of 60, holistic / wheeled | 1 / 7 | 1 / 8 | **1 / 14** |
| heritability holistic / wheeled | 0.51 / 0.24–0.39 | 0.44 / 0.24 | **0.563 / 0.262** |
| saved holistic bests carrying a nose | some | 7 of 61 | **0 of 60** |
| holistic best with a lesion > 25% | none | none | **none** |
| nose-dependent Pioneer best | season 500, a brake (88% loss) | season 590, a brake (57% on 16 seeds) | **none that survives 16 seeds** |
| any chemotaxis | no | no | **no** |

Two differences from RBT-13 that the sensor change plausibly explains, both on the wheeled side. RBT-13's season-0 Pioneers were actively poisoned by the saturated smell: a constant 0.86 input into a random-weight controller left them eating 0.00 items intact against 1.62 blanked. Here the same season-0 Pioneer eats 1.12 intact against 0.88 blanked, and the wheeled population's late-run mean gain recovers to +1.01 from RBT-13's +0.82, back to baseline level. De-saturating the smell removed a handicap. It did not add a capability.

The holistic side's improvement (bottleneck 14 not 8, gain +1.70 not +1.19, heritability 0.563 not 0.44, the best in the family on all three) **cannot** be credited to the readable smell, and I want to be explicit about that rather than let the numbers imply it: no holistic individual in this run wires a smell sensor to anything, so nothing on that side can be reading the gradient the change created. With one seed and one run per arm, lineage luck is the parsimonious explanation. The arm's own best mower is also much less efficient than RBT-13's, 2.75 items on 7.9 kJ against 3.12 on 1.2 kJ, so "healthier demography" here does not mean "better foragers".

## 8. Answer

**No. A readable long-range smell did not give sensing a slope either.** The pre-registered expectation was that this would be the arm where a nose bias finally pays, because it is the first in which the gradient is legible across the whole disc; the pre-registered fallback was that if no holistic best loses more than 25% of its yield to a blanked nose by season 600, information was not the limit in this world. Not one did, and the arm went further in the opposite direction than any predecessor: zero of sixty saved holistic bests carry a nose at all, and of the ten final lumps whose genotypes declare one, seven express it and none wire it to anything. The single Pioneer best that cleared the threshold on eight seeds gives 33%, 27% and 15% on three different samples with error bars overlapping zero, eats below the blind-mow rate with its nose on, and shows the brake signature rather than a compass. **Information range was not the limit, and neither was information legibility.** RBT-13's caveat is now retired: the squash was a real design error, correcting it measurably de-poisoned the designed body's season-0 founders, and it changed nothing about whether anything evolved to smell.

What this leaves standing is the explanation the fan-out has been circling. The disc is 3 m across at 0.424 items/m² and a season is 15 s, over which these robots travel 5 to 9 m: the whole food supply is within reach of an undirected mow, and the noseless holistic g590 clears the point-robot chance rate at 0.48 to 0.52 items per metre of in-disc path on body width alone. A compass earns nothing when the food is everywhere you already are. The arms sparse enough to reward search (W2, 0.12 items/m²) sit below the density at which random founders form a breeding population and went extinct by season 31. That squeeze, not the sensor, is the live hypothesis: the densities where a population survives are the densities where blind mowing suffices, and every arm so far has been run inside it. `docs/persistent-world.md` (RBT-19) is the design that escapes it, by keeping local density high enough to bootstrap while making depletion turn patch-leaving into a graded skill.

## Files

`W1b-801/` (config.json, history.json, lineage.jsonl, best_gen*.json, holistic/final, conventional/final), `W1b-801.log`, `smell_range.py` / `.txt`, `readout.py` / `.txt`, `nosed_bests.py`, `holistic_sensors_by_gen.txt`, `probe.txt`, `probe_final_nosed.py` / `.txt`, `wiring.py` / `.txt`, `brake_or_compass.py` / `.txt`, `forage_lab_holistic590.txt`, `forage_lab_conventional300.txt`, `lab_conventional300.txt`.

Code: `feature/RBT-22`, PR #3. `scripts/forage_lab.py`, used in §4 and §5, is RBT-28's and lives on `feature/RBT-28`; it is not part of PR #3.
