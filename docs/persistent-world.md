# The Persistent World

The spec for the next world in the foraging series (Chaotic RBT-2), settled
before it is built and run (RBT-19). Everything below that carries a number was
measured with `scripts/persistent_supply.py` on the current simulator, before
the run, and the two places where the measurements contradict the world as it
was first written down are stated as such.

## Why

`docs/foraging-world.md` ends with the diagnosis: lifetime foraging yield is
heritable in the ecology (parent-child 0.51 holistic), so the search has signal,
but the world offers sensing a cliff rather than a hill. With twelve items
regrowing instantly at a fresh random spot, a half-built nose earns nothing: the
food a robot can smell is not the food that will be there, blind mowing pays,
and six arms of the fan-out changed one thing each without changing that.

Three properties would give a nose partial credit, and none of them encodes an
answer:

- **Patches.** Food in clusters, so a gradient points somewhere worth going.
- **Depletion with slow recovery.** An eaten item comes back at its own spot
  after a delay, so the patch a robot is standing on runs out, and where food
  was is information rather than noise.
- **Persistence across seasons.** Arena food state carries over, so a season
  starts in a world the previous season's occupants ate from.

## The world

Both bodies alike; the economy, the clearance rule and the group arenas
unchanged from the baseline arm `forage-801`.

| | baseline (`forage-801`) | persistent world |
|---|---|---|
| food layout | 12 items uniform in a 3 m disc | 26 spots in 3 patches of radius 0.6 m, centres uniform in the disc |
| regrowth | instant, at a fresh random spot | at the spot it was eaten from, after 45 s of simulated time (three seasons) |
| across seasons | re-seeded every season | carried: one persistent state per arena, 15 arenas at capacity 60 and groups of 4, groups assigned to arenas at random each season |
| smell | `sum(exp(-d/1.0))` squashed by `i/(1+i)` | unchanged |
| economy | value 1, basal 0.25, work 0.03 per kJ, initial energy 3, birth at 3, cost 1, lifespan 60 | unchanged |

## 1. What a season yields

Twelve groups of four random robots, 15 s, food placed once and not regrown
(which is what a 45 s regrow delay does to a 15 s season), against the baseline
measured the same way:

| layout | season-start crop | group eats | per robot | robot work |
|---|---|---|---|---|
| baseline, uniform, instant regrowth | 12 | 4.75 ± 3.70 | 1.19 | 18.7 kJ |
| depleting, uniform | 12 | 3.25 ± 2.31 | 0.81 | 18.9 kJ |
| depleting, patchy | 12 | 4.42 ± 4.27 | 1.10 | 18.8 kJ |
| depleting, patchy | 18 | 5.83 ± 6.74 | 1.46 | 18.6 kJ |
| depleting, patchy | 26 | 9.17 ± 7.62 | 2.29 | 19.1 kJ |

Random Pioneers; the random holistic genotypes eat 0.10 to 0.25 a season at
these densities on 0.8 kJ, as in the baseline. Two things to carry forward:
harvest is linear in the standing crop over a factor of five in density, and
clustering the same amount of food raises the mean a little and the spread a
lot (a season's yield in a patchy world is 0.97 of its own mean in standard
deviation, against 0.71 uniform), because finding a patch is worth several
items and missing every patch is worth none.

## 2. The ledger: how many spots

An item eaten in season *s* is missing for the next three seasons, so the
season-start crop settles at `N* = S - 3 E(N*)` for a world of `S` spots, with
`E` the harvest above:

| spots | season-start crop | group eats | per robot | supply ceiling |
|---|---|---|---|---|
| 12 | 5.8 | 2.07 | 0.52 | 4.00 |
| 18 | 8.7 | 3.10 | 0.77 | 6.00 |
| **26** | **12.6** | **4.48** | **1.12** | **8.67** |
| 32 | 15.5 | 5.51 | 1.38 | 10.67 |

The supply ceiling is `S / 45 s`, the most the arena can hand out however good
its occupants get. Stated per simulated second, as RBT-20's lesson requires: at
26 spots the world can supply 0.58 items per second per arena and hands the
founders 0.30, against the baseline's realised 0.32.

**Deviation from the ticket, with the reason.** RBT-19 as filed runs 12 spots at
a 45 s delay. That is a season-start crop of 5.8 and 0.52 items per robot: the
six-item arm, where the wheeled population bottlenecked to eleven and went
extinct at season 51 and the holistic population starved out at season 15. The
founders' budgets say the same thing. At 0.03 per kJ a random Pioneer pays 0.56
in work and 0.25 in basal cost:

| | items per robot | net energy per season |
|---|---|---|
| baseline | 1.19 | +0.38 |
| persistent, 26 spots | 1.12 | +0.31 |
| persistent, 12 spots | 0.52 | **-0.29** |

Twelve spots is a world whose random founders are bankrupt on arrival, and an
arm like that measures the bootstrap threshold and nothing else. Twenty-six
spots holds the founders' season-start crop at the baseline's twelve, which is
what "the season-0 economy matches the baseline" has to mean once food regrows
on a timer: the same *standing crop*, not the same number of spots.

The ceiling then does the work the world exists for. A baseline evolved lump
ate 2.1 to 2.5 items a season alone; four of them in one arena demand more than
8.67, so a fauna that reaches baseline competence is supply-limited, and from
there eating more is not mowing harder but being on a patch that has recovered.
Nothing in that is a thumb: the ceiling follows from the spot count and the
delay, both fixed before the run.

## 3. The smell, and the second deviation

The `food` sensor is the summed intensity `sum(exp(-d/decay))` squashed by
`i/(1+i)`. What a Braitenberg pairing can use is the difference between two
noses 0.33 m apart. Median difference over 4000 points in the disc, and the
share pointing the right way:

| layout | decay | reading | two-nose difference | toward food |
|---|---|---|---|---|
| baseline, 12 uniform | 1 m | 0.49-0.68 | 2.6e-02 | 92% |
| W1 (RBT-13), 12 uniform | 3 m | 0.82-0.86 | 3.5e-03 | 72% |
| patchy, 26 spots | 1 m | 0.35-0.87 | 4.9e-02 | 98% |
| patchy, 26 spots | 2 m | 0.78-0.93 | 1.2e-02 | 96% |
| patchy, 26 spots | 3 m | 0.87-0.94 | 6.0e-03 | 94% |
| patchy, 26 spots, mean squash | 3 m | 0.21-0.37 | 1.5e-02 | 94% |

And the signal this world is built to add, a patch being eaten down: the
reading a metre outside a patch as it falls from nine items to none, with two
full patches elsewhere in the arena.

| decay | squash | 9 items | 5 | 3 | 1 | 0 | full-to-empty |
|---|---|---|---|---|---|---|---|
| 1 m | sum | 0.775 | 0.648 | 0.551 | 0.395 | 0.243 | **0.53** |
| 3 m | sum | 0.916 | 0.892 | 0.874 | 0.848 | 0.819 | 0.10 |
| 1 m | mean | 0.108 | 0.090 | 0.077 | 0.047 | 0.017 | 0.09 |
| 3 m | mean | 0.300 | 0.255 | 0.250 | 0.215 | 0.203 | 0.10 |
| 1 m | log | 0.603 | 0.538 | 0.428 | 0.340 | 0.214 | 0.39 |
| 3 m | log | 0.712 | 0.690 | 0.679 | 0.652 | 0.635 | 0.08 |

**So the persistent world runs at decay 1 m with the sensor it already has.**
RBT-2 asked for a smell carrying over several metres and RBT-19 defaults it to
3 m; the measurements say the long decay is the wrong half of the trade in this
world, on both counts. Patch structure, not decay, is what restores the
gradient: at 1 m the two-nose difference is 4.9e-02, twice the baseline's and
eight times what 3 m gives, right 98% of the time, and it is *stronger* beyond
2 m from the patch (6.6e-02) than near it, because an exponential's fractional
slope is steepest where the squash has not saturated. And a 3 m decay flattens
the full-to-empty contrast from 0.53 to 0.10 under every normalisation, which
throws away depletion, the one signal this world adds.

RBT-22's mean normalisation is not needed at 1 m and should not be used here
even at 3 m: dividing by the number of items standing divides out exactly the
quantity a depleting patch varies. If the long decay is wanted for its own sake
later, that is a separate arm at decay 2 m with the summed squash, not a change
to this one.

## Parameters, fixed before the run

```
--food-items 26 --food-patches 3 --patch-radius 0.6 --regrow-delay 45 --food-radius 3
--eat-radius 0.35 --food-decay 1.0 --work-cost 0.03 --living-cost 0.25
--initial-energy 3 --birth-threshold 3 --birth-cost 1 --group-size 4 --capacity 60
--seasons 600 --duration 15 --mass-budget 15.34 --conventional-topology --terrain random
--random-start --score food --challenge foraging --brain-model foraging --seed 801
```

Fifteen arenas, one persistent food state each (spot positions, alive flags,
regrowth timers), groups assigned at random each season, states saved beside
`history.json`. Patch centres are drawn per arena when the arena is created and
then stay put for the run: an individual meets a given layout about four times
in a sixty-season life, so a gait tuned to one arena cannot pay, and no arena's
layout is anyone's inheritance.

One correction to the banked rationale while the parameters are being fixed:
"remembering where another patch was" is not available across seasons, because a
brain's state is rebuilt at every bout and arena assignment is random. What this
world can ask for is within-season memory, leaving a patch that has stopped
paying and not coming back to it, which is what an integrator can hold for
fifteen seconds.

## Pre-registered expectations

1. **Demography like the baseline's.** Founder budgets are within 20% of it, so
   expect the holistic bottleneck at season 11 (60 down to roughly 5-10),
   recovery by season 35, and the wheeled population holding above 40
   throughout. A holistic extinction would mean the ledger is wrong, not that
   the world is hard.
2. **Heritability of lifetime yield at or above 0.4** on the holistic side
   (baseline 0.51), lower than the baseline because patch luck adds
   within-season variance; read off lifetime yield, never one season.
3. **Supply limitation by mid-run.** Group harvest rises toward 8.67 items a
   season and per-robot yield falls below the founders' 1.12 as the population
   fills. A run where yields exceed the ceiling has a bookkeeping bug and is
   void.
4. **The question the world exists for.** By season 600, at least one of: a
   holistic best that loses more than half its yield to the `no_food` lesion;
   or a Pioneer best that passes RBT-13's brake-or-compass check as a compass,
   more items per metre of in-disc path and a shorter distance to the nearest
   item with its noses on than off. Both would be the first sensing in the
   series.
5. **What a null looks like.** If both populations are blind mowers again at
   600, then patches, depletion, persistence and a gradient twice as readable as
   the baseline's were together not a slope, and the series has run out of world
   to blame: the next question is the search (mutation operators that can build
   a crossed pairing in one step, RBT-25's heritable dynamics), not another
   arena.

## Reproducing the numbers

```
python scripts/persistent_supply.py 12          # harvest, ledger, smell, depletion
```

Twelve groups per condition, about four minutes, deterministic seeds; writes
`persistent_supply.json`. Re-run it against the built world before launch: the
harvest table is the acceptance test for the implementation, since a correct
persistent world at a season-start crop of 12.6 must hand four random Pioneers
4.5 items in a season, and the arena states must show about half the spots
empty at any time: 12.6 standing of 26 is 52% empty, which is what the ledger
above says and what the built world measured (RBT-19: crop 12.43, 52.2% empty,
4.54 items a season). An earlier draft of this line said a third, which was a
slip of prose against the table beside it; about a third of *patches* stand
empty, not of spots.
