# RBT-23 — W4', depleting arena at baseline density: no regrowth, 12 items (seed 801)

One arm of the world fan-out, and the de-confounding follow-up to RBT-16. Same seed, economy and every
other flag as the baseline `forage-801`; the only change is `--no-regrow`. RBT-16 ran the depleting
arena at 24 items, so a first pass through its arena met twice the baseline's food and everything it
differed on was confounded with density (its own report says so). This arm holds the density at the
baseline's 12 and changes only whether eaten food comes back.

Command (run once under nohup, 600 seasons, 4 workers, 6.1 s a season, 61 minutes, no errors in the log):

```
rabbitstew ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 --workers 4 \
  --brain-model foraging --food-items 12 --no-regrow --food-radius 3 --eat-radius 0.35 --food-decay 1.0 --work-cost 0.03 \
  --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start --score food \
  --seed 801 --out runs/RBT-23/W4b-801
```

Files: `W4b-801/` (config.json, history.json, lineage.jsonl, `<kind>/best_gen*.json`, `<kind>/final/`),
`W4b-801.log`, `readout.txt` (from `readout.py`), `probe_split.txt` + `probe_split.json` (from
`forage_probe_split.py`), `group_split.txt` (from `group_split.py`), `wiring_590.txt` (nose wiring and
static influence for all eight bests), `lab_conventional_590.txt` (`scripts/lab.py`), `extras.txt`
(block means, turnover, bottleneck trajectory). The three scratch scripts are RBT-16's, copied from
branch `results/RBT-16` and committed next to the results; the only edit is that `group_split.py` now
takes the item count from the run's config instead of printing a hardcoded `/24`. No library changes.

`config.json` confirms the arm: `food.items` 12, `food.regrow` false, everything else the baseline's.

## 1. Ecology readout

`rabbitstew history` at the listed seasons (alive after the season's deaths and births; mean and best
lifetime gain per season):

| season | holistic alive | births | deaths | mean gain | best gain | wheeled alive | births | deaths | mean gain | best gain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 59 | 3 | 4 | +0.040 | +1.973 | 60 | 2 | 2 | −0.213 | +2.596 |
| 11 | 7 | 0 | 37 | +0.363 | +0.568 | 60 | 8 | 8 | +0.389 | +1.315 |
| 20 | 43 | 11 | 0 | +0.523 | +2.967 | 60 | 0 | 0 | +0.711 | +3.355 |
| 32 | 60 | 4 | 4 | +0.627 | +1.953 | 60 | 3 | 3 | +0.623 | +2.555 |
| 60 | 60 | 1 | 1 | +0.598 | +1.272 | 60 | 2 | 2 | +0.637 | +1.684 |
| 100 | 60 | 1 | 1 | +0.716 | +2.363 | 60 | 2 | 2 | +0.625 | +1.481 |
| 200 | 60 | 2 | 2 | +0.689 | +1.911 | 60 | 1 | 1 | +0.686 | +2.446 |
| 300 | 60 | 1 | 1 | +0.870 | +1.873 | 60 | 1 | 1 | +0.671 | +1.364 |
| 400 | 60 | 3 | 3 | +0.908 | +2.938 | 60 | 2 | 2 | +0.599 | +1.802 |
| 500 | 60 | 0 | 0 | +1.098 | +2.751 | 60 | 2 | 2 | +0.581 | +1.717 |
| 599 | 60 | 1 | 1 | +0.854 | +2.014 | 60 | 0 | 0 | +0.693 | +1.368 |

- **Bottleneck and recovery.** Holistic: 52, 50, 44 at seasons 8 to 10, then **7 at season 11** (37
  starved together as the founders' birth energy ran out), then 9, 11, 13, 17, 20, 21, 26, 32, 43, 51,
  57 and back to **60 at season 23**, full every season after. Wheeled: 60 at every one of the 600
  seasons, never dipped.
- **Extinctions:** none, either side. A breeding population formed, as at the baseline density it did.
- **Crossover.** Holistic mean gain first exceeds wheeled at season 0 (+0.040 against −0.213, both
  founder noise). The first 20-season unbroken run of holistic > wheeled starts at **season 116**, and
  holistic is ahead in **495 of seasons 100–599**. Hundred-season block means, holistic / wheeled:
  0–99 +0.52 / +0.58; 100–199 +0.77 / +0.63; 200–299 +0.82 / +0.65; 300–399 +0.89 / +0.65;
  400–499 +0.97 / +0.64; 500–599 +0.94 / +0.64.
- **Turnover, seasons 100–599:** holistic 807 births (a death in 403 of 500 seasons), wheeled 1060
  (435 of 500). Both at capacity throughout, turning over one or two a season.
- **Founders at season 599** (the last season with survivors, both sides full): holistic **1 of 60**;
  wheeled **11 of 60**. The neutral control keeps 14 and 16.
- **Yield heritability** (Pearson r, child's lifetime mean yield vs parents' mean, evals ≥ 5 both
  sides): holistic **r = +0.449** (n = 665); wheeled **r = +0.150** (n = 775).

## 2. Three-column comparison

Baseline `forage-801` numbers from `docs/foraging-world.md`; RBT-16 from its report on `results/RBT-16`.

| | baseline forage-801 (12 items, regrow) | RBT-16 / W4 (24 items, no regrow) | **this arm / W4' (12 items, no regrow)** |
|---|---|---|---|
| holistic bottleneck | 60 → **7** at season 11 | 60 → 32 at season 11 | 60 → **7** at season 11 |
| back to 60 | season 32 | season 13 | season 23 |
| wheeled minimum alive | 60 | 60 | 60 |
| holistic mean gain, seasons 100 / 300 / 500 / 599 | +1.02 / +1.19 / +1.63 / +1.41 | +1.40 / +1.59 / +1.68 / +1.46 | **+0.72 / +0.87 / +1.10 / +0.85** |
| wheeled mean gain, same seasons | +0.96 / +1.03 / +0.94 / +0.95 | +1.28 / +1.23 / +1.27 / +1.21 | **+0.63 / +0.67 / +0.58 / +0.69** |
| sustained crossover (20-season run) | 83 | 15 | **116** |
| founders at the end, holistic / wheeled | 1 / 7 | 1 / 17 | 1 / 11 |
| yield heritability, holistic / wheeled | 0.51 / 0.24–0.39 | 0.40 / 0.28 | 0.449 / 0.150 |
| extinctions | none | none | none |
| holistic best alone, items a season (≈100 / 300 / 500–590) | 2.25 / 1.75 / 2.12 | 1.62 / 1.75 / 2.38 | 2.12 / 0.75 / 2.12 |
| any holistic best whose yield moves > 25 % under a sensor lesion | none | none | **none** |
| any holistic best carrying a food sensor at all | some, unused | s590 carries two on two segments | **none of the four; one carries `agent` only, unwired** |
| any Pioneer best whose noses matter > 25 % | s500: brake, 1.00 → 0.12 | s100 (2.38 → 1.12), s590 (1.25 → 0.12) | s590 only, and weakly (1.38 → 1.00, −28 %) |

**This arm is the harder economy the ticket pre-registered.** Mean gain runs about a third below the
baseline on the holistic side and a third below on the wheeled side, at every block from 100 on, and
roughly half of RBT-16's. Twelve items that do not come back is a poorer world than twelve that do.

**RBT-16's confound is resolved, and it was density.** Everything RBT-16 differed from the baseline on
went the other way, or vanished, once the density was held at 12: its shallow bottleneck (32) is 7
again, exactly the baseline's; its two-season recovery is twenty-three seasons; its crossover at 15 is
116, later than the baseline's own 83; and its raised gains are gains a third *below* the baseline. Its
17 surviving wheeled founders are 11 here, between the baseline's 7 and RBT-16's 17. Not one of
RBT-16's demographic differences survives de-confounding: they were the first pass through a 24-item
arena, as its report suspected. Depletion on its own makes this world poorer, slower to recover and
slower to cross over. (The wheeled side never dipping is common to all three arms and is not a
density effect.)

## 3. Probes (each best ALONE on eight fresh seeds; depletion is by that robot only)

`forage_probe_split.py`: items eaten intact, with the food/agent sensors blanked (`no_food`), every
environmental sensor blanked (`no_env`), or the local brains silenced (`no_local`). The bracket splits
items into first half + second half of the 15 s season.

| best | parts / units | sensors | intact | no_food | no_env | no_local | path, work (intact) |
|---|---|---|---|---|---|---|---|
| holistic s0 | 4 / 29 | oscillator, up | 0.00 (0.00+0.00) | 0.00 | 0.00 | 0.12 | 2.3 m, 0.7 kJ |
| holistic s100 | 3 / 19 | agent, joint_angle, velocity | 2.12 (1.50+0.62) | 2.12 | 2.12 | 2.12 | 10.5 m, 1.2 kJ |
| holistic s300 | 3 / 13 | joint_angle, velocity | 0.75 (0.75+0.00) | 0.75 | 0.75 | 0.75 | 10.4 m, 4.0 kJ |
| holistic s590 | 4 / 26 | contact, joint_angle, oscillator | 2.12 (1.00+1.12) | 2.12 | 2.12 | 2.12 | 12.1 m, 11.2 kJ |
| Pioneer s0 | 5 / 24 | all seven sources | 1.25 (0.88+0.38) | 1.00 | 1.25 | 1.25 | 6.1 m, 15.2 kJ |
| Pioneer s100 | 5 / 26 | all seven | 0.75 (0.62+0.12) | **1.00** | **0.38** | 0.38 | 8.6 m, 17.4 kJ |
| Pioneer s300 | 5 / 24 | all seven | 1.12 (0.88+0.25) | 1.25 | **0.25** (runs off, 7.4 m) | 0.25 | 8.8 m, 21.8 kJ |
| Pioneer s590 | 5 / 26 | all seven | 1.38 (0.88+0.50) | **1.00** (−28 %) | **0.62** | 0.62 | 8.8 m, 20.8 kJ |

**Every holistic best that eats at all is lesion-invariant to the decimal.** The bests at seasons 100,
300 and 590 eat exactly the same, on exactly the same path for exactly the same work, intact, with the
noses blanked, with every environmental sensor blanked, and with the local brains silenced. This is a
stronger null than the baseline's or RBT-16's, where at least some lesions moved a best's yield up or
down: here nothing moves at all. The season-0 best eats nothing intact and is a lump that has not found
eating; its 0.12 under `no_local` is a different random walk, not a skill.

**And three of the four carry no nose to blank.** `wiring_590.txt` gives the static influence of every
food and agent sensor on the live effectors:

- **holistic s0, s300, s590: no food or agent sensor exists at all.** The season-590 best is four parts
  and 26 units with contact, joint-angle and oscillator sensors only.
- **holistic s100** carries two `agent` sensors, on parts 1 and 2, and both have influence **0.0**:
  present in the body, wired to nothing.
- **Pioneer, all four bests:** the chassis nose (unit 8, part 0) has influence 239, 230, 508 and 353 at
  seasons 0, 100, 300 and 590. Both wheel noses have influence **0.0** in every one of the four, except
  the part-2 nose at season 590 at 0.219, which is a rounding error beside 353. The `agent` sensors on
  the wheels are 0.0 throughout.

Six hundred seasons, and the wheel noses were never wired on the designed side while the evolved side
stopped carrying a nose at all. RBT-16's headline, that the evolved side had at last produced the
two-noses-on-two-segments wiring a Braitenberg pairing needs and earned nothing with it, does not
reproduce at the baseline density: here the wiring never appeared.

**The one lesion over the threshold, labbed.** Pioneer s590 loses 28 % when its noses are blanked
(1.38 → 1.00), the only best on either side past the ticket's 25 %, so it got `scripts/lab.py
runs/RBT-23/W4b-801 conventional 590 12` (`lab_conventional_590.txt`). It is five parts, 26 units, 116
links, centralisation 0.99, mean sensor path 1.5. The food sensor on part 1 is listed `(unlinked)`; the
one on part 2 reaches an effector through a single weight of **−0.01**; the chassis nose feeds the
hidden layer at −0.55 and −2.19. So the 28 % is one scalar again: the summed food intensity at the
chassis, which says "food is somewhere near" and not where it is. There is no second reading from a
second place to compare it against, which is what a compass would need. Blanking the chassis nose alone
(`lesion:8`) leaves it moving on a 9.2 m path against 9.9 m intact, so it is not the drive gate that
the baseline's season-500 best and RBT-16's s590 were either: those stopped dead without their noses.
It is a weaker version of the same one-bit skill.

**Yield split, first half against second.** Alone in a 12-item arena one robot removes only one or two
items, so solo depletion is mild and the split is mostly the walker revisiting mown ground: holistic
s100 1.50 + 0.62, s300 0.75 + 0.00, s590 1.00 + 1.12. The season-590 best is the one that eats more in
the second half than the first, and it has no nose at all.

## 4. Four copies sharing one arena (`group_split.py`, eight seeds, the ecology's own group size)

This is the depletion the population actually evolved under: four robots, twelve items, nothing regrows.

| best ×4 | robot 0's noses | group items of 12 (first + second half) | robot 0 (first + second) | robot 0 work |
|---|---|---|---|---|
| holistic s590 | intact | 5.25 (3.75 + 1.50) | 1.50 (1.12 + 0.38) | 11.3 kJ |
| holistic s590 | blanked | 5.25 (3.75 + 1.50) | 1.50 (1.12 + 0.38) | 11.3 kJ |
| Pioneer s590 | intact | 5.00 (4.00 + 1.00) | 1.62 (1.12 + 0.50) | 20.8 kJ |
| Pioneer s590 | blanked | 6.00 (5.12 + 0.88) | 1.62 (1.38 + 0.25) | 21.2 kJ |

Four copies strip 44 % of the arena in a season and take about three quarters of it in the first half;
the second half yields 1.0 to 1.5 items to the whole group against 3.75 to 4.0 in the first. That is
the depleted phase the pre-registration pointed at, and it is real. What happens in it: robot 0 eats
**1.50 items with its noses on and 1.50 with them off**, identical to the decimal, on the holistic
side. On the Pioneer side robot 0 eats **1.62 either way**, and the group as a whole eats *more* with
robot 0's noses blanked (6.00 against 5.00). The 28 % solo nose effect of Pioneer s590 does not
survive being put in the arena the population was actually selected in.

## 5. Does this variant give sensing a slope?

**No.** A depleting arena at the baseline's density makes the world poorer without making it
informative. What changed against the baseline: mean gain fell about a third on both sides, the
crossover moved later (116 against 83), and the wheeled side kept 11 founders instead of 7. What did
not change: the holistic population's course is blind mowing again, and more completely than in any
previous arm, because three of its four sampled bests do not carry a food or agent sensor at all and
the fourth carries two agent sensors wired to nothing; every holistic lesion moves nothing at all,
to the decimal; and on the Pioneer side the two wheel noses had influence 0.0 for six hundred seasons
while only the chassis nose was ever wired, exactly as in every other arm of this fan-out.

The pre-registered slope was that a depleted second half rewards going where food remains. The second
half is measurably depleted, and the ticket's expectation of a deeper bottleneck and possible extinction
was half right: the economy is harder, but the bottleneck is the baseline's 7, not deeper, and nobody
died out. In that depleted second half a nosed and a blind robot eat the same number of items to two
decimal places. The reason looks the same as the docs already give: what depletion adds to the smell
field is "less food everywhere", a scalar the chassis nose already reads, and the gradient toward the
items that remain still runs over metres in a 3 m disc with a 1 m decay inside a 15 s season. Removing
regrowth does not shorten that distance; it only lowers the mean. A half-built pairing still earns
nothing, so bias mutation climbs the one hill there is, move more for less, and that is what all six
hundred seasons produced.

The three world-fan-out arms that changed the food supply (W2 six items in a 4 m disc, W4 twenty-four
depleting, W4' twelve depleting) now agree: below the bootstrap density nothing lives, at or above it
blind mowing pays, and depletion within a season shifts the mean without adding a usable gradient.

## Contradictions with the docs and the ticket, stated plainly

- **The ticket's pre-registered expectation is only half confirmed.** It expected "a harder economy than
  the baseline ... so a deeper bottleneck and possibly extinction". The economy is harder, by about a
  third of the mean gain at every block from season 100 on. The bottleneck is **not** deeper: it is
  60 → 7 at season 11, the same season and the same depth as the baseline, and recovery was nine
  seasons *faster* than the baseline's (23 against 32). There was no extinction on either side. The
  season-11 wave is the founders' initial energy running out on a schedule that regrowth does not
  affect, and depletion cannot bite before there is a population eating enough for the arena to run
  down; so removing regrowth changes the economy the survivors live in without changing the shape of
  the founders' die-off. Reported as a result, per the ticket.
- **RBT-16's demography was density, not depletion, and this report says so with the arm that isolates
  it.** RBT-16 declined to attribute its higher gains to depletion and asked for exactly this run; every
  one of its demographic differences from the baseline reverses or disappears here. The docs' W4 row
  ("demography changed ... but confounded with a denser first pass") should now read that the change
  was the density, and that the depleting arena at baseline density is poorer than the baseline rather
  than richer.
- **The docs' expectation that a depleting arena puts usable structure in the smell field is
  contradicted more sharply here than in RBT-16.** RBT-16 could say the structure went unused by a body
  that had the wiring for it. At the baseline density the evolved side did not even retain a nose: three
  of four sampled bests carry no food or agent sensor, and the population's final best is blind in the
  strict sense that there is nothing to blank. The one Braitenberg-capable holistic wiring in the family
  (RBT-16's s590, two food sensors on two separated segments) does not reproduce here, so it should be
  read as one draw at 24 items and not as something the depleting world tends to produce.
- **`scripts/lab.py` reports locomotion metrics, not food.** It is the paper-4 harness and runs with
  `opponent_proxy=True`, so its table columns (progress, time at target, arrival) are about reaching a
  point, not foraging. It was still the right tool for what the ticket asked it for, the wiring dump and
  the per-unit lesions, and that is what is quoted above; the food numbers for that best come from the
  probe and the group probe instead.

## Reproducing

```
git checkout claude/rbt-lowest-unclaimed-ticket-55orfd
python3 -m venv v && ./v/bin/pip install -e '.[dev]' && ./v/bin/pytest -q     # 139 passed
./v/bin/python runs/RBT-23/readout.py runs/RBT-23/W4b-801
./v/bin/python runs/RBT-23/forage_probe_split.py runs/RBT-23/W4b-801 0,100,300,590 8
./v/bin/python runs/RBT-23/group_split.py runs/RBT-23/W4b-801 590 8
./v/bin/python scripts/lab.py runs/RBT-23/W4b-801 conventional 590 12
```
