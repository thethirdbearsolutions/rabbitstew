# RBT-17 — W5, crowded arena: eight robots per arena at 12 items (seed 801)

One arm of the world fan-out. Same seed, economy and world as the baseline `forage-801` (12 items in a 3 m disc, decay 1 m, eat radius 0.35 m, work cost 0.03 per kJ, basal cost 0.25, initial energy 3, birth at 3, birth cost 1, capacity 60, 600 seasons), with one change: `--group-size 8`. Run at `runs/RBT-17/W5-801` from commit `e09ff7b` of `claude/new-session-4cao7d`, three workers, about 9 s a season. The run was started twice: the first attempt was killed at season 91 when the session's container was suspended (the ecology is not resumable), and the second was run from scratch under a live session; its season-by-season numbers matched the first attempt exactly over the seasons both covered, so the run is deterministic under `--workers 3`.

**Pre-registered expectation:** lower mean yields and a deeper bottleneck; the first place in this family where the `agent` sensor could earn its keep.

## 1. Ecology readout

Alive / births / deaths / mean lifetime gain per season (`readout.txt`; full table in `history.txt`):

| season | holistic alive | births | deaths | mean gain | wheeled alive | births | deaths | mean gain |
|---|---|---|---|---|---|---|---|---|
| 0 | 59 | 3 | 4 | +0.04 | 60 | 2 | 2 | +0.15 |
| 11 | **3** | 0 | 37 | +0.13 | 60 | 7 | 7 | +0.78 |
| 20 | 5 | 1 | 1 | +0.29 | 60 | 4 | 4 | +0.86 |
| 32 | 23 | 8 | 0 | +0.68 | 60 | 2 | 2 | +0.89 |
| 60 | 60 | 0 | 0 | +0.83 | 60 | 0 | 0 | +0.89 |
| 100 | 60 | 3 | 3 | +0.90 | 60 | 1 | 1 | +0.83 |
| 200 | 60 | 0 | 0 | +1.05 | 60 | 1 | 1 | +0.87 |
| 300 | 60 | 2 | 2 | +1.06 | 60 | 1 | 1 | +0.98 |
| 400 | 60 | 2 | 2 | +0.93 | 60 | 2 | 2 | +0.98 |
| 500 | 60 | 0 | 0 | +1.09 | 60 | 0 | 0 | +1.07 |
| 599 | 60 | 2 | 2 | +1.04 | 60 | 0 | 0 | +0.92 |

- **Bottleneck and recovery.** The holistic population fell 59 → 3 at season 11 (37 starved together in that one season, after 3, 3, 4, 1, 5 deaths over seasons 5 to 10), held at 3 to 5 until season 20, reached 23 at season 32 and was back at 60 by season 38. The total holistic energy at season 11 was 3.5: the population was one bad season from extinction. The wheeled population never dipped below 58 (season 5) and was full from season 6 on.
- **Crossover.** The first season the holistic mean gain exceeded the wheeled was **45** (baseline: 83). From season 100 on the holistic mean was above the wheeled in 384 of 500 seasons. Hundred-season means: holistic +0.98 / +0.93 / +1.00 over seasons 100–199 / 300–399 / 500–599; wheeled +0.81 / +0.92 / +0.96.
- **Extinctions.** None. Both populations full at season 599.
- **Founders at season 599** (`founders.txt`): holistic **1 of 60**, wheeled **5 of 60** (baseline 1 / 7; drift control 14 / 16).
- **Yield heritability** (`heritability.txt`; Pearson r between a child's lifetime mean yield with ≥ 5 evals and its parents' mean, same rule): holistic **0.34** (638 pairs), wheeled **0.27** (708 pairs). Baseline 0.51 / 0.24–0.39.

## 2. Solo probes (`scripts/forage_probe.py`, 8 seeds, each best alone in the arena)

Items eaten per season, alone, with displacement / path / work in the text files (`forage_probe_g*.txt`). `no_food` blanks both noses (food and agent), `no_env` every sensor but the oscillator, `no_local` silences the local brains.

| best | sensors | intact | no noses | no env | no local |
|---|---|---|---|---|---|
| holistic 0 | oscillator, up | 0.00 | 0.00 | 0.00 | 0.12 |
| holistic 100 | height, joint_angle | 1.50 | 1.50 | 1.12 | 1.25 |
| holistic 300 | joint_angle | 1.12 | 1.12 | 1.50 | 1.12 |
| holistic 400 | food, joint_angle | 0.25 | 0.25 | 0.25 | 0.38 |
| holistic 500 | food, joint_angle | 1.00 | 1.00 | 0.75 | 0.62 |
| holistic 580 | height | 1.12 | 1.12 | **2.88** | 0.62 |
| holistic 590 | food ×3, joint_angle, joint_velocity | 0.88 | 0.88 | 0.88 | 0.88 |
| wheeled 0 | all seven | 0.75 | 1.88 | 1.75 | 1.75 |
| wheeled 100 | all seven | 0.75 | 0.50 | 0.25 | 0.25 |
| wheeled 300 | all seven | 0.38 | 0.38 | 1.75 | 1.75 |
| wheeled 400 | all seven | 1.75 | 1.38 | 0.38 (drives 16 m off) | 0.38 |
| wheeled 500 | all seven | **1.62** | **1.12** | 0.12 (does not move) | 0.12 |
| wheeled 580 | all seven | 1.50 | 1.50 | 0.50 | 0.50 |
| wheeled 590 | all seven | **2.12** | **0.88** | 0.25 (drives 6 m off) | 0.25 |

Holistic: as in every dense arm, no nose lesion changes any holistic best's yield at any season, including the bests at 400, 500 and 590 that carry food sensors (the 590 best carries three). The holistic bests here are smaller mowers than the baseline's: 0.9–1.5 items alone on 4–14 kJ, against the baseline's 2.1–2.5 items on 2–6 kJ. The season-580 best eats two and a half times more with its environmental sensors blanked (1.12 → 2.88), the largest sensor-hindrance seen in the series, and the 590 best eats the same with everything off. Note the holistic bests spend 7–14 kJ a season from season 400 on, where the baseline's spent 2–6: cheap locomotion did not evolve here the way it did with four to an arena.

Wheeled: the bests at 500 and 590 lose a third and 58% of their solo yield when their noses are blanked, at essentially the same path length (590: 8.1 m intact, 8.6 m blanked). This is the strongest nose dependence in the family: the baseline's one nose-dependent Pioneer (season 500) went from 1.00 to 0.12 because it drove out of the disc without them; here the 590 best still stays near the disc with noses blanked (displacement 2.3 m) and still loses more than half its food.

## 3. Group probe (`group_probe.py`: eight copies of a best share one arena, 8 seeds, items eaten per robot)

`no_agent` blanks only the agent sensors' outgoing weights, `no_food` only the food sensors', `no_noses` both, `no_env` every sensor but the oscillator. Standard deviation over seeds in the text files.

| best | food / agent sensor units | intact | agent blanked | food blanked | both blanked | all env blanked |
|---|---|---|---|---|---|---|
| holistic 100 | 0 / 0 | 1.73 | 1.73 | 1.73 | 1.73 | 1.70 |
| holistic 590 | 3 / 0 | 1.14 | 1.14 | 1.14 | 1.14 | 1.36 |
| wheeled 100 | 3 / 3 | 1.19 | 1.44 | 0.31 | 1.03 | 0.36 |
| wheeled 590 | 3 / 3 | **2.34** | **2.22** | **1.52** | **1.22** | 0.69 (drives 5.6 m off) |

- **The `agent` sensor never earned its keep.** No holistic individual in the final population carries one (see §5); the holistic bests' yields are untouched by any nose lesion in the group as alone. In the wheeled 590 best, blanking the agent sensors alone costs 0.12 items per robot (2.34 → 2.22, within the seed-to-seed sd of 0.6–0.7); blanking the food sensors costs 0.82; blanking both costs 1.12. At season 100 blanking the agent sensors *raised* the group yield (1.19 → 1.44) while blanking food alone cut it to 0.31 and blanking both left 1.03: the two inputs were wired against each other, the food input cancelling the agent input's harm rather than either steering.
- In eight-robot groups the wheeled 590 best out-eats the holistic 590 best two to one per robot (2.34 vs 1.14), and its intact group yield exceeds its solo yield (2.12): the crowd does not hurt it. The mean gain the two populations actually achieved in the ecology was nonetheless nearly equal (§1), because the wheeled best spends 18 kJ a season (0.55 energy) where the holistic spends 14, and because a population's mean is not its best.

## 4. Compass or brake? (`steer_probe.py`, wheeled bests at 590 and 500, alone, 8 seeds)

Fraction of the season the centre of mass is inside the 3 m food disc, and the mean distance to the nearest live food item, overall and while inside the disc.

| best | mode | items | path | in disc | nearest food | nearest food while in disc |
|---|---|---|---|---|---|---|
| wheeled 590 | intact | 2.12 | 8.1 m | 67% | 1.57 m | **1.36 m** |
| | food blanked | 0.88 | 8.6 m | 50% | 2.14 m | **1.36 m** |
| | agent blanked | 2.12 | 8.1 m | 67% | 1.57 m | 1.36 m |
| | all env blanked | 0.25 | 8.5 m | 39% | 3.31 m | 1.37 m |
| wheeled 500 | intact | 1.62 | 10.1 m | 67% | 1.61 m | 1.32 m |
| | food blanked | 1.12 | 9.3 m | 68% | 1.52 m | 1.22 m |
| | all env blanked | 0.12 | 2.6 m | 99% | 1.39 m | 1.39 m |

While inside the disc, the 590 best is no closer to food with its nose than without (1.36 m either way); the food sensor's whole measurable effect on its position is the time it spends inside the disc (67% against 50%). The 500 best is, if anything, closer to food *without* its nose (1.22 m vs 1.32 m) and still eats a third less. Neither is a compass by the nearest-food criterion. The 590 best is a brake of the kind the baseline's season-500 Pioneer was, but a stronger one, and the 500 best's nose does something to its sweep that this probe does not resolve (a wider or more turning path through the items at the same mean distance). The `agent` sensor changes nothing in either.

## 5. The final populations (`population_lesion.py`: every individual alone, 3 seeds, intact vs both noses blanked)

| population | n | carry a nose | mean items alone, intact | noses blanked | nose-dependent (loses ≥ 0.5) | nose-hindered (gains ≥ 0.5) |
|---|---|---|---|---|---|---|
| holistic | 60 | 49 (food only; **no agent sensor in the population**) | 1.11 | 1.11 | **0** | 0 |
| wheeled | 60 | 60 (3 food + 3 agent each, by design) | 1.16 | 1.12 | **14** | 12 |

Forty-nine of sixty holistic individuals carry food sensor units (some carry eight or ten), and not one changes its yield by a hundredth of an item when they are blanked: the sensors are hitch-hikers from a body that grew units it does not wire. On the wheeled side a quarter of the population (14 of 60) loses at least half an item without its noses (the top four lose 2.0–2.3 of 2.7–3.3), a fifth gains as much, and the population mean is unchanged by the lesion (1.16 → 1.12). Nose use is present in the wheeled population as a polymorphism, not fixed.

## 6. Against the baseline

| | baseline `forage-801` (groups of 4) | **W5 (groups of 8)** |
|---|---|---|
| holistic bottleneck | 60 → 7 at season 11 | 60 → **3** at season 11 |
| holistic back to 60 | season 32 | season 38 |
| wheeled minimum | 60 (16 of 60 founders survive by s39) | 58 at season 5 |
| holistic mean gain, s100 / 300 / 500 / 599 | +1.02 / +1.19 / +1.63 / +1.41 | +0.90 / +1.06 / +1.09 / +1.04 |
| wheeled mean gain, s100 / 300 / 500 / 599 | +0.96 / +1.03 / +0.94 / +0.95 | +0.83 / +0.98 / +1.07 / +0.92 |
| first season holistic mean > wheeled | 83 | 45 |
| founders at 599, holistic / wheeled | 1 / 7 | 1 / 5 |
| heritability, holistic / wheeled | 0.51 / 0.24–0.39 | 0.34 / 0.27 |
| holistic best alone, s500 / 590 | 2.12 items on ~5 kJ / more with local brains off | 1.00 items on 13 kJ / 0.88 on 14 kJ |
| holistic nose lesion effect, any best | none | none |
| wheeled best alone, s500 / 590, intact → noses blanked | 1.00 → 0.12 (leaves disc) / 1.62 → 1.12 | 1.62 → 1.12 / **2.12 → 0.88** (stays near disc) |
| `agent` sensor effect | never mattered | never mattered (group probe: −0.12 of 2.34 at s590, within noise; absent from the holistic population) |
| extinctions | none | none |

The pre-registered expectations held in direction: the bottleneck was deeper (3 against 7) and the holistic yields were lower throughout (about −0.1 to −0.5 a season against the baseline; the late-run holistic advantage of +0.5 to +0.7 in the baseline shrank to about +0.05 to +0.15). Per-robot yield did not halve: with 12 items regrowing instantly, eight mowers in a disc still each meet about one item a season, and the wheeled side's mean gain barely moved (−0.13 at season 100, +0.13 at 500).

## 7. Does this variant give sensing a slope?

Not to the `agent` sensor, and only the same brake to the food sensor. Doubling the crowd made the other robots the main thing changing the food field, and the `agent` smell was informative in principle; in practice the holistic population ended the run with no agent sensor at all in sixty genomes, 49 of them carrying food sensors that do nothing, and the wheeled best's agent sensors, when blanked in an eight-robot arena, cost it a tenth of an item that is inside the seed-to-seed noise. What the crowded arena did select, on the designed side, is a stronger version of the baseline's one situated behaviour: a food-sensor brake that holds the Pioneer in the disc, which at season 590 is worth 1.2 items alone and 1.1 per robot in a group of eight, the largest nose effect in the family, present in a quarter of the final wheeled population and reversed in another fifth. It is still not a compass: with the nose on or off the robot is 1.36 m from the nearest item while it is in the disc. On the evolved side the crowded arena did worse than the baseline on the one hill this world has, cheap locomotion: the holistic bests here spend two to three times the baseline's energy for half the food, the season-11 bottleneck went to three survivors and one founder, and heritability fell from 0.51 to 0.34. The slope the crowd added, if any, was toward staying where the food is, and only a body that arrives with the noses and the wheels to express it in one weight climbed it.

**Contradictions with the docs, stated plainly.** (1) `docs/foraging-world.md` says the wheeled side "never" evolved a controller whose noses raise its yield except as a brake; the W5 wheeled 500 best is closer to food without its nose and still eats a third less with it blanked, which is not a brake in the sense of the docs (its time in the disc is unchanged, 67% vs 68%) and not a compass either; the probe here does not say what it is. (2) The docs' claim that the evolved bodies "ended up out-eating the designed one on a fraction of its energy" does not hold in the crowded arena: the holistic bests eat less than the wheeled bests alone and in groups (0.88 vs 2.12 alone, 1.14 vs 2.34 per robot in eights at season 590) on 14 kJ against 17–18, and the populations' mean gains are within 0.1 of each other over the last hundred seasons.

## Files

`W5-801/` (config.json, history.json, lineage.jsonl, `<kind>/best_gen*.json`, `<kind>/final/`), `W5-801.log`, `history.txt`, `readout.txt` + `readout.py`, `founders.txt`, `heritability.txt` + `heritability.py`, `forage_probe_g*.txt`, `group_probe.py` + `group_probe_g100.*` + `group_probe_g590.*`, `steer_probe.py` + `steer_probe_conventional_g{500,590}.txt`, `population_lesion.py` + `population_lesion.{txt,json}`.
