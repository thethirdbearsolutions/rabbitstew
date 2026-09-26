# RBT-16 — W4, depleting arena: no regrowth within a season, 24 items (seed 801)

One arm of the world fan-out. Same seed, economy and every other flag as the baseline `forage-801`;
the only changes are `--no-regrow --food-items 24`. Eaten food stays eaten until the season resets,
so the arena four robots share depletes as they eat.

Command (run once under nohup, 600 seasons, 4 workers, ~10 s a season, no errors in the log):

```
rabbitstew ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 --workers 4 \
  --brain-model foraging --food-items 24 --no-regrow --food-radius 3 --eat-radius 0.35 --food-decay 1.0 --work-cost 0.03 \
  --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start --score food \
  --seed 801 --out runs/RBT-16/W4-801
```

Files: `W4-801/` (config.json, history.json, lineage.jsonl, `<kind>/best_gen*.json`, `<kind>/final/`),
`W4-801.log`, `readout.txt` (from `readout.py`), `probe_split.txt` + `probe_split.json` (from
`forage_probe_split.py`, a scratch copy of `scripts/forage_probe.py` that also splits items by season
half using `sim.food_events`), `group_split.txt` (from `group_split.py`, four copies of a best sharing
one arena). The scratch scripts are committed next to the results and are not library changes.

## 1. Ecology readout

`rabbitstew history` at the listed seasons (alive after the season's deaths and births; mean and best
lifetime gain per season):

| season | holistic alive | births | deaths | mean gain | best gain | wheeled alive | births | deaths | mean gain | best gain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 60 | 4 | 4 | +0.090 | +1.973 | 60 | 2 | 2 | +0.551 | +5.193 |
| 11 | 32 | 10 | 37 | +0.587 | +2.963 | 60 | 2 | 2 | +0.990 | +5.362 |
| 20 | 60 | 2 | 2 | +1.385 | +3.837 | 60 | 1 | 1 | +1.186 | +2.763 |
| 32 | 60 | 0 | 0 | +1.435 | +3.898 | 60 | 2 | 2 | +1.096 | +2.258 |
| 60 | 60 | 0 | 0 | +1.701 | +4.393 | 60 | 2 | 2 | +1.298 | +4.592 |
| 100 | 60 | 0 | 0 | +1.404 | +3.441 | 60 | 0 | 0 | +1.277 | +3.489 |
| 200 | 60 | 1 | 1 | +1.729 | +4.405 | 60 | 3 | 3 | +1.086 | +2.310 |
| 300 | 60 | 1 | 1 | +1.586 | +3.751 | 60 | 0 | 0 | +1.229 | +2.903 |
| 400 | 60 | 1 | 1 | +1.427 | +3.049 | 60 | 0 | 0 | +1.393 | +3.513 |
| 500 | 60 | 3 | 3 | +1.675 | +4.259 | 60 | 2 | 2 | +1.268 | +3.245 |
| 599 | 60 | 0 | 0 | +1.459 | +4.493 | 60 | 2 | 2 | +1.209 | +2.797 |

- **Bottleneck and recovery.** Holistic: 60 → 59 at season 10 → 32 at season 11 (37 starved together
  when the founders' birth energy ran out, 10 born the same season) → 42 at 12 → 60 at 13, and full
  every season after. Wheeled: 60 at every season, never dipped.
- **Extinctions:** none, either side.
- **First season holistic mean gain exceeds wheeled:** season 15, and it stayed ahead: the first
  20-season run of holistic > wheeled also starts at 15, and holistic is ahead in 490 of seasons
  100–599. Hundred-season block means, holistic / wheeled: 0–99 +1.30 / +1.13; 100–199 +1.62 / +1.20;
  200–299 +1.51 / +1.20; 300–399 +1.47 / +1.30; 400–499 +1.56 / +1.27; 500–599 +1.53 / +1.29.
- **Turnover, seasons 100–599:** holistic 696 births (a death in 322 of 500 seasons), wheeled 681
  (365 of 500). Both populations at capacity, turning over one or two a season.
- **Founders at season 599:** holistic 1 of 60; wheeled 17 of 60.
- **Yield heritability** (Pearson r, child's lifetime mean yield vs parents' mean, evals ≥ 5 on both
  sides): holistic r = +0.40 (n = 640); wheeled r = +0.28 (n = 632).

## 2. Against the baseline (forage-801: 12 items, instant random regrowth, same everything else)

| | baseline forage-801 | W4 depleting, 24 items |
|---|---|---|
| holistic bottleneck | 60 → 7 at season 11, back to 60 by 32 | 60 → 32 at season 11, back to 60 at 13 |
| wheeled minimum alive | 60 (16 of the 60 founders kept at season 39) | 60 |
| holistic mean gain, seasons 100 / 300 / 500 / 599 | +1.02 / +1.19 / +1.63 / +1.41 | +1.40 / +1.59 / +1.68 / +1.46 |
| wheeled mean gain, same seasons | +0.96 / +1.03 / +0.94 / +0.95 | +1.28 / +1.23 / +1.27 / +1.21 |
| first season holistic > wheeled | 83 | 15 |
| founders at the end, holistic / wheeled | 1 / 7 | 1 / 17 |
| yield heritability, holistic / wheeled | 0.51 / 0.24–0.39 | 0.40 / 0.28 |
| extinctions | none | none |
| holistic best alone, items a season (season ~100 / 300 / 500–590) | 2.25 / 1.75 / 2.12 | 1.62 / 1.75 / 2.38 |
| any holistic best whose yield moves > 25 % under a sensor lesion | none | none (see §3) |
| any Pioneer best whose noses matter > 25 % | season 500: brake, 1.00 → 0.12 without noses | s100: 2.38 → 1.12 without noses (but 3.00 with all sensors off); s590: 1.25 → 0.12, it does not move without them; wheel noses unwired on both |

The wheeled side kept more than twice the founders it kept in the baseline (17 vs 7) and never lost a
season's worth of members; its mean gain sits a third higher throughout. The holistic bottleneck is
shallower by a factor of four and recovery is 19 seasons faster. Both are what 24 items instead of 12
in the first half of a season does for a random walker: the first pass through the arena meets twice
the food before anyone has eaten it.

## 3. Probes (each best ALONE on eight fresh seeds; depletion is by that robot only)

`forage_probe_split.py`: items eaten intact and with the food/agent sensors blanked (`no_food`), every
environmental sensor blanked (`no_env`), or the local brains silenced (`no_local`). The bracket splits
items into first half + second half of the 15 s season (`sim.food_events` tick ≤ or > step 750).

| best | parts / units | sensors | intact | no_food | no_env | no_local | path, work (intact) |
|---|---|---|---|---|---|---|---|
| holistic s0 | 4 / 29 | oscillator, up | 0.00 (0.00+0.00) | 0.00 | 0.25 | 0.62 | 2.3 m, 0.7 kJ |
| holistic s100 | 2 / 13 | joint_angle | 1.62 (1.00+0.62) | 1.62 | 1.62 | 1.62 | 10.0 m, 8.9 kJ |
| holistic s300 | 8 / 64 | joint_angle, up, velocity | 1.75 (1.25+0.50) | 1.75 | 1.75 | 1.75 | 10.4 m, 2.1 kJ |
| holistic s590 | 5 / 28 | food ×2 (parts 3, 4), joint_angle, velocity ×2 | 2.38 (1.62+0.75) | 2.38 | **3.12** (1.88+1.25) | 1.62 (0.62+1.00) | 10.6 m, 8.5 kJ |
| Pioneer s0 | 5 / 24 | all seven sources | 1.38 (1.38+0.00) | 0.88 | 0.00 | 0.00 | 19.3 m, 28.5 kJ |
| Pioneer s100 | 5 / 24 | all seven | 2.38 (1.88+0.50) | **1.12** (1.00+0.12) | **3.00** (2.00+1.00) | 3.00 | 6.8 m, 16.7 kJ |
| Pioneer s300 | 5 / 23 | all seven | 1.75 (1.50+0.25) | 1.75 (1.38+0.38) | 1.00 (1.00+0.00) | 1.00 | 6.6 m, 21.1 kJ |
| Pioneer s590 | 5 / 25 | all seven | 1.25 (1.12+0.12) | **0.12** (0.12+0.00) | 0.12 | 0.12 | 5.2 m, 19.5 kJ |

Baseline for the same seasons (docs): holistic bests eat 2.25 (s100), 1.75 (s300), 2.12 (s500) alone
with no lesion effect; Pioneer bests 1.0 (s100), 1.25 (s300), 1.00 (s500, 0.12 without noses).

Per best, does any sensor matter (> 25 % change in yield)?

- **Holistic s0** eats nothing intact; no sensor matters (a lump that has not found eating; its
  0.25 / 0.62 under `no_env` / `no_local` is a different random walk, not a skill).
- **Holistic s100** (two parts, 13 units, one joint-angle sensor, no nose): no lesion changes anything,
  1.62 items on a 10 m path under every condition. A blind mower.
- **Holistic s300** (eight parts, 64 units, joint-angle, up and velocity sensors, no nose): identical
  under every lesion, 1.75 items on 10.4 m for 2.1 kJ, the cheapest locomotion in this run. Blind.
- **Holistic s590** (five parts, 28 units; **two food sensors on two separate segments, parts 3 and 4**,
  plus one joint-angle and two velocity sensors): `no_food` changes nothing, 2.38 → 2.38, same path,
  same work. Blanking every environmental sensor *raises* its yield by 31 % (2.38 → 3.12) on a shorter
  path, so its sensors as a whole cost it food; silencing the local brains costs a third (→ 1.62).
  It has the two noses in two places a Braitenberg pairing needs, and does not use them.

- **Pioneer s0**: `no_food` −36 % (1.38 → 0.88), `no_env` → 0. The season-0 best is sensor-dependent,
  but it eats everything in the first half and then drives 19 m out of the disc, as in the baseline.
- **Pioneer s100**: `no_food` **halves** its yield (2.38 → 1.12), yet `no_env` raises it (→ 3.00,
  2.00+1.00) on a longer path for less work. Its noses are not steering it to food: their job is to
  cancel other sensor inputs, and the bias-only gait underneath is the better mower (the same pattern
  the baseline docs report for the holistic best at 300). Wiring (`controller_descriptors`): 24 units,
  16 sensors, 6 tanh neurons, 2 effectors, centralisation 1.0, mean sensor path 2.0, links 122. Food
  sensors sit on parts 0 (chassis), 1 and 2 (the two wheels); `sensor_influence` is 122 for the chassis
  nose and **0.0 for both wheel noses**. Only one nose is wired, so there is no pairing to steer with.
- **Pioneer s300**: `no_food` no change (1.75 → 1.75); `no_env` −43 % (→ 1.00) and it runs off 16 m.
  Orientation and velocity keep it in the disc; the noses do nothing.
- **Pioneer s590**: `no_food` −90 % (1.25 → 0.12) and `no_env` the same. Without its noses it does
  not move (displacement 0.23 m, path 2.2 m, work *up* to 24.7 kJ from 19.5: it spins in place).
  Wiring: 25 units, 16 sensors, 7 neurons (3 tanh, 2 relu, 1 abs, 1 integrate), 2 effectors,
  centralisation 0.99, mean sensor path 1.5, links 124. Chassis nose influence 580, wheel noses
  **0.0 and 0.0** again. The drive is gated through the chassis' summed food intensity: a scalar that
  says "food is somewhere near", not where. It is the baseline's season-500 brake in a new form, a
  one-sensor one-bit skill, and it eats 1.25 items to the blind holistic best's 2.38 on twice the work.

**Yield split, first half vs second half.** Alone in a 24-item arena the holistic bests eat about two
thirds of their items in the first half of the season (season 100: 1.00 + 0.62; 300: 1.25 + 0.50;
590: 1.62 + 0.75), so yield does fall through the season as pre-registered, even when one robot has
removed only two of twenty-four items. The fall is the random walker revisiting ground it has already
mown, not the arena running out.

**Four copies of a best sharing one arena** (`group_split.py`, eight seeds, the ecology's own group
size, so this is the depletion the population actually evolved under):

| best ×4 | robot 0's noses | group items of 24 (first + second half) | robot 0 (first + second) | robot 0 work |
|---|---|---|---|---|
| holistic s300 | intact | 12.00 (9.50 + 2.50) | 2.12 (1.75 + 0.38) | 2.0 kJ |
| holistic s300 | blanked | 12.00 (9.50 + 2.50) | 2.12 (1.75 + 0.38) | 2.0 kJ |
| holistic s590 | intact | 11.62 (9.25 + 2.38) | 2.75 (1.88 + 0.88) | 8.3 kJ |
| holistic s590 | blanked | 11.62 (9.25 + 2.38) | 2.75 (1.88 + 0.88) | 8.3 kJ |
| Pioneer s300 | intact | 6.62 (6.50 + 0.12) | 1.75 (1.75 + 0.00) | 20.5 kJ |
| Pioneer s300 | blanked | 6.88 (5.88 + 1.00) | 2.00 (1.38 + 0.62) | 20.8 kJ |
| Pioneer s590 | intact | 9.88 (7.25 + 2.62) | 2.25 (2.25 + 0.00) | 20.4 kJ |
| Pioneer s590 | blanked | 8.38 (5.50 + 2.88) | 0.12 (0.12 + 0.00) | 24.7 kJ |

Four holistic bests strip half the arena in a season, four fifths of it in the first half; the second
half yields a fifth of the first. This is the depleted half the pre-registration pointed at, and in it
robot 0 eats 0.38 to 0.88 items with or without its noses, to the decimal. The Pioneer s590 group
takes 9.9 of 24 and its robot 0 eats nothing at all in the second half whether its noses are on or
off; blanking them removes its first-half yield too, since it then does not move.

## 4. Does this variant give sensing a slope?

**No.** The depleting arena changed the ecology's demography and not its sensing. What changed:
both populations ate more from season 0 (the first pass through 24 items meets twice the food), the
holistic bottleneck was 32 instead of 7 and lasted two seasons instead of twenty-one, the wheeled
side never dipped and kept 17 founders, the holistic side crossed over the wheeled at season 15
instead of 83 and stayed ahead for 490 of the last 500 seasons, and yield stayed heritable (0.40 /
0.28). What did not change: no holistic best in 600 seasons alters its yield when its noses are
blanked, including the final one that carries two food sensors on two separated segments; the
holistic side's course is again ever cheaper blind mowing (2.1 kJ for 1.75 items at season 300),
and its best eats more with every environmental sensor off. On the Pioneer side two bests depend on
their noses, at seasons 100 and 590, and on both only the chassis nose is wired while the two wheel
noses have zero influence: one scalar gating the drive, a brake or a throttle, never a comparison
between two places. The pre-registered slope was that the second half of a depleted season rewards
going where food remains; the measured second half is where a quarter of the yield comes from and
where a blind and a nosed robot eat the same. A depleted arena does put structure in the smell field,
but the structure is "less food everywhere", a scalar a nose already on the chassis can read and a
gate can act on, which is the one-bit skill the docs said one sensor and one weight can express, and
that is all that evolved. The gradient that would make a pairing pay, toward the remaining items,
still runs over metres in a 3 m disc with a 1 m decay, in one 15 s season, and nothing here selected
for it. Whether this is depletion or density is confounded in this arm (see below): W4 is a denser
world at the start of every season as well as a depleting one.

## Contradictions with the docs, stated plainly

- The ticket says twenty-four items were chosen "so that the season starts with the same expected
  yield as the baseline". The measured start is not the same: with twice the items in the disc the
  founders of both populations ate more in their first seasons than in the baseline (holistic mean
  gain +0.09 at season 0 and +0.59 at season 11 against the baseline's starving founders; wheeled
  +0.55 at season 0), the holistic bottleneck was 32 instead of 7 and the wheeled side never dipped.
  The first pass through a 24-item arena is a 24-item arena, whatever happens later in the season, so
  the W4 arm is a denser world for a random walker as well as a depleting one. Anything W4 differs on
  from the baseline is confounded with density until a 12-item no-regrow arm (or a 24-item regrow arm)
  is run; this report does not attribute the higher gains to depletion.
- The docs' expectation that a depleting arena would put "structure" in the smell field that a nose
  could use is not contradicted by the measurement, but the measurement says the structure was not
  used: no best on either side in 600 seasons changes its yield by more than the noise when its noses
  are blanked, and the holistic best at 590, which carries two food sensors on two separate segments
  (parts 3 and 4), the first Braitenberg-capable wiring seen in this family, eats exactly the same
  without them and more with every environmental sensor off.
