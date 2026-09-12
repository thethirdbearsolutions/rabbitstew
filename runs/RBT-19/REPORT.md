# RBT-19: the persistent foraging world

Run `P-801`, 600 seasons, complete. The world is the one settled in
`docs/persistent-world.md` (RBT-2): 26 spots in 3 patches of radius 0.6 m, an eaten
item back at its own spot after 45 s of simulated time (three seasons), 15
persistent arenas per population carried from season to season, groups assigned to
arenas at random, smell at decay 1 m with the summed squash already in the code.

Branch `claude/rbt-lowest-unclaimed-ticket-sxhcl3`, PR
[#2](https://github.com/thethirdbearsolutions/rabbitstew/pull/2).

## Pre-registered expectations

Copied from `docs/persistent-world.md` before the run was launched and before any
result was looked at.

1. **Demography like the baseline's.** Founder budgets are within 20% of it, so
   expect the holistic bottleneck at season 11 (60 down to roughly 5-10), recovery
   by season 35, and the wheeled population holding above 40 throughout. A holistic
   extinction would mean the ledger is wrong, not that the world is hard.
2. **Heritability of lifetime yield at or above 0.4** on the holistic side (baseline
   0.51), lower than the baseline because patch luck adds within-season variance;
   read off lifetime yield, never one season.
3. **Supply limitation by mid-run.** Group harvest rises toward 8.67 items a season
   and per-robot yield falls below the founders' 1.12 as the population fills. A run
   where yields exceed the ceiling has a bookkeeping bug and is void.
4. **The question the world exists for.** By season 600, at least one of: a holistic
   best that loses more than half its yield to the `no_food` lesion; or a Pioneer
   best that passes RBT-13's brake-or-compass check as a compass, more items per
   metre of in-disc path and a shorter distance to the nearest item with its noses
   on than off. Both would be the first sensing in the series.
5. **What a null looks like.** If both populations are blind mowers again at 600,
   then patches, depletion, persistence and a gradient twice as readable as the
   baseline's were together not a slope, and the series has run out of world to
   blame: the next question is the search (mutation operators that can build a
   crossed pairing in one step, RBT-25's heritable dynamics), not another arena.

## The answer, in one line

**Expectation 5. The null, with one qualification.** No holistic best in the run
carries a food sensor at all, and the one nose-dependent Pioneer has both of its
wheel noses unlinked, so it cannot be a compass and is not one. What it does have is
a chassis nose wired as a locomotion gate, which measurably raises how much it eats
per metre it covers. That is more than the baseline's brake and still not a compass.

## Design decisions and deviations

**Deviations from the ticket as filed**, all of them the document's, not mine:
`--food-items 26` not 12, and `--food-decay 1.0` not 3.0, both fixed by RBT-2's
pre-launch measurements and both stated on the issue. RBT-22's `--smell mean` is
not used, as RBT-2 directs.

**Deviations that are mine**, with reasons:

1. **Branch.** `claude/rbt-lowest-unclaimed-ticket-sxhcl3`, not `feature/RBT-19`:
   this session is pinned to that branch name. Base and contents are as asked.
2. **`--workers 4`, not 7.** This box has 4 cores. Worker count changes only wall
   clock: the group tasks are pure functions of their inputs and `map` preserves
   order, so the run is identical either way. It took 68 minutes.
3. **The clearance rule had to be put back by hand.** Persistence breaks it. Spots
   cannot move between seasons, so nothing stops a group spawning on top of food.
   Measured without a fix, robots ate **15% of all items on the first tick of a
   season** (130 of 875): free lunch for standing still, which rewards nothing about
   foraging and would dilute exactly the signal this world exists to create. Since
   the food cannot move, the robots are placed instead (`clear_spawn_layout`): the
   start layout is redrawn until nobody stands within `clearance` of a standing
   item, taking the roomiest of 128 draws when a full arena cannot afford the whole
   0.8 m. After it, 0 of 749 items were taken at spawn. I read this as keeping spec
   item 1's "keeping the clearance rule" rather than as a deviation from it, but it
   is a choice, and it is the only one in the build that could move a number.

**Two things the spec left open**, settled in the build: arenas are **per fauna**,
one bank of 15 each, because the two populations live in separate ecologies and
sharing food would couple them; and arenas **nobody visits still regrow**, by one
season's duration, because the world's clock does not stop where nobody is standing
and a bottlenecked population would otherwise freeze most of its arenas
mid-depletion.

**A contradiction with the spec, stated plainly.** `docs/persistent-world.md` asks
that "the arena states must show roughly a third of the spots empty at any time".
They show about half. Half is what the spec's own ledger implies, since a settled
crop of 12.6 standing out of 26 spots is 52% empty, so the prose and the table
disagree and the table is right. About a third of *patches* stand empty at a season
start, which may be what the prose meant.

## Tests and the acceptance test

`tests/test_persistent_food.py`, 17 tests: items cluster within `patch_radius` of a
centre; an eaten item returns at its own spot after the delay and not before; food
state round-trips through a `Simulation` and through `run_group`; the ecology
carries arena state across two seasons and regrows arenas nobody visited; the
clearance rule survives persistence; and food is conserved over a season. All 119
tests that existed before still pass, so nothing changes when `--food-patches` is
absent.

**Acceptance test.** `scripts/persistent_supply.py 12 world` creates twelve
persistent arenas and runs them season after season with fresh random Pioneers,
carrying state through `run_group` exactly as `Ecology` does. Settled over seasons
15-29:

| | measured | predicted (RBT-2) | off by |
|---|---|---|---|
| season-start crop | 12.43 | 12.60 | -1.3% |
| group eats per season | 4.54 | 4.48 | +1.3% |
| per robot | 1.13 | 1.12 | +0.9% |

Both inside the 25% tolerance, and closer than the tolerance needed.

## Readout

### 1. Demography

| | season 100 | 300 | 500 | 599 |
|---|---|---|---|---|
| holistic, this run | +1.147 | +1.184 | +1.303 | +1.147 |
| holistic, baseline `forage-801` | +1.02 | +1.19 | +1.63 | +1.41 |
| wheeled, this run | +1.167 | +1.069 | +1.040 | +0.874 |
| wheeled, baseline | +0.96 | +1.03 | +0.94 | +0.95 |

Bottleneck and recovery, against expectation 1: the holistic population fell to
**30 alive at season 11** and was back to 60 by **season 14**. The expectation was 5
to 10 at season 11 and recovery by 35, so the bottleneck was real but half as deep
and recovered twenty seasons sooner. The wheeled population **never dipped below
60**. Neither went extinct, and both were full from season 14 to the end. The
holistic mean gain first exceeded the wheeled one at **season 19**, against the
baseline's season 83.

Expectation 1 is met, and comfortably: the ledger that chose 26 spots was right that
the founders would not be bankrupt, and slightly conservative about how hard the
bootstrap would be.

### 2. Founders at the last season

| | founders behind the 60 alive at 599 | baseline |
|---|---|---|
| holistic | 1 of 58 | 1 of 60 |
| wheeled | 8 of 60 | 7 of 60 |

Indistinguishable from the baseline. The holistic side is again descended from a
single founder through the season-11 bottleneck; the wheeled side was selected but
never bottlenecked.

### 3. Heritability of lifetime yield

Pearson r between a child's lifetime mean yield and its parents' mean, both from the
last lineage record with at least 5 evaluations.

| | this run | baseline |
|---|---|---|
| holistic | **0.246** (670 pairs) | 0.51 |
| wheeled | 0.082 (832 pairs) | 0.24 to 0.39 |

**Expectation 2 is not met.** It asked for 0.4 or above on the holistic side and
predicted a fall from the baseline's 0.51 because patch luck adds variance. The fall
is real and larger than predicted: 0.246. The direction was right, the magnitude was
not. This matters for reading the rest: the search had roughly half the signal it
had in the baseline, and a world that adds variance to a heritable trait buys its
new gradient partly out of the trait's heritability. That is a cost of patches the
spec did not price.

### 4. Supply

Ceiling 8.67 items per group per season (26 spots over a 45 s delay).

| holistic, seasons | crop at start | empty | harvest | of ceiling | per robot |
|---|---|---|---|---|---|
| 0-99 | 14.68 | 44% | 3.91 | 45% | 0.98 |
| 200-299 | 11.53 | 56% | 4.83 | 56% | 1.21 |
| 400-499 | 11.26 | 57% | 4.95 | 57% | 1.24 |
| 500-599 | 10.14 | 61% | 5.28 | 61% | 1.32 |

The wheeled side runs the same course more gently, 49% to 57% of ceiling.

**Expectation 3 is half met.** Supply limitation is visible and develops exactly as
described: as the fauna gets better the standing crop is drawn down, from 14.7 to
10.1 on the holistic side, and harvest climbs from 45% to 61% of the ceiling. But
per-robot yield **rose** from 0.98 to 1.32 rather than falling below the founders'
1.12, because both populations were already full from season 14, so there was no
filling left to do; what changed was competence, not crowding.

**The five seasons above the ceiling are not a bookkeeping bug, and the run is not
void.** Five holistic seasons (131, 510, 542, 581, 588) show a mean group harvest
between 8.73 and 9.47 against the 8.67 ceiling. The ceiling is a *sustainable* rate,
`spots / delay`, not a per-season cap: a single season can beat it by drawing the
standing crop down, and by items whose 45 s delay happens to expire inside it. I
checked this rather than assuming it:

- In every one of the five, the group ate far less than stood in the arena at the
  season's start (142 eaten against 214 standing, and so on).
- Every saved arena has exactly 26 spots, never more items standing than spots, and
  every timer inside [0, 45 s].
- A test now asserts the conservation identity directly over six seasons of a live
  arena: eaten equals standing at the start, plus regrown during, minus standing at
  the end. It holds exactly.
- The long-run means never approach the ceiling: 61% at the very end.

### 5. Probes: did anything sense?

`scripts/forage_probe.py runs/RBT-19/P-801 0,100,300,590 8`, each best alone with
the run's own config, patches included, fresh food each trial.

**Holistic: no sensing, because there is no sensor.** Not one holistic best at
seasons 0, 100, 300 or 590 carries a `food` sensor at all. Their sensor lists are
joint angle, velocity and contact. The `no_food` lesion therefore changes nothing,
to the digit:

| holistic best | intact | no_food | no_env | no_local |
|---|---|---|---|---|
| gen 300 | 2.12 | 2.12 | 2.12 | 2.12 |
| gen 590 | 5.75 | 5.75 | 5.75 | 5.75 |

The gen-590 lump eats **5.75 items alone in a 15 s season on 4.2 kJ**, against the
baseline's best lumps at 2.1 to 2.5. The persistent world produced by far the
strongest blind mower the series has seen, and gave it no nose whatever.

**Wheeled: one nose-dependent best, and it is not a compass.** The Pioneer carries
three food sensors by construction. On 8 seeds the bests at 300 and 590 looked
strongly nose-dependent (63% and 58% of yield lost when blanked) and both passed the
16-seed brake-or-compass check as compasses. **Neither survives pairing.** With 64
paired seeds, the same seeds run with noses on and off:

| conventional gen 300 | on | off | diff ± SE | t |
|---|---|---|---|---|
| items eaten | 3.078 | 1.906 | +1.172 ± 0.561 | +2.09 |
| items per in-disc metre | 0.809 | 0.468 | +0.341 ± 0.158 | +2.15 |
| distance to nearest item | 1.439 | 1.486 | -0.047 ± 0.065 | -0.72 |
| fraction of time in disc | 0.853 | 0.986 | -0.133 ± 0.029 | -4.67 |

| conventional gen 590 | on | off | diff ± SE | t |
|---|---|---|---|---|
| items eaten | 3.594 | 2.875 | +0.719 ± 0.651 | +1.10 |
| items per in-disc metre | 0.881 | 0.899 | -0.019 ± 0.150 | -0.12 |
| distance to nearest item | 1.457 | 1.458 | -0.001 ± 0.056 | -0.02 |

The gen-590 effect **evaporates entirely** at 64 seeds: the 58% loss on 8 seeds was
small-sample inflation. The gen-300 best keeps a real yield gain and a real gain in
items per metre of in-disc path, but shows **no improvement in distance to the
nearest item**, which is half the compass definition. And both spend significantly
*less* time in the disc with their noses on, which is the opposite of a brake.

**The wiring settles it.** `scripts/lab.py` on the gen-300 best:

```
unit   8 part 0    sensor   food
unit  12 part 1    sensor   food               (unlinked)
unit  16 part 2    sensor   food               (unlinked)
```

Both wheel noses are unlinked. The only wired food sensor is the chassis one, and it
feeds a single global neuron that drives both wheels. **One scalar cannot give a
direction**, so a compass is not merely unproven here, it is unavailable to this
controller. Lesioning that one sensor halves the path length, from 7.7 m to 3.8 m,
and drops the work from 17.5 to 14.8 kJ: the nose is a throttle on locomotion, not a
steering signal. In six hundred seasons this world, like the six before it, produced
no Braitenberg pairing.

## Comparison against the baseline

| | baseline `forage-801` | persistent world `P-801` |
|---|---|---|
| holistic mean gain at 599 | +1.41 | +1.147 |
| wheeled mean gain at 599 | +0.95 | +0.874 |
| holistic founders of 60 | 1 | 1 |
| wheeled founders of 60 | 7 | 8 |
| holistic bottleneck | season 11 | season 11, to 30 not 5-10 |
| crossover season | 83 | 19 |
| yield heritability, holistic | 0.51 | 0.246 |
| best lump alone | 2.1-2.5 items | 5.75 items |
| food sensors on holistic bests | present, unused (RBT-16) | **absent entirely** |
| nose-dependent wheeled best | yes, a brake | yes, a throttle |
| a compass | no | no |

## Did the persistent world give sensing a slope?

No, not one that was climbed. Patches, depletion and persistence did everything the
spec said they would to the *world*: the ledger held to within 1.3%, the gradient
was twice as readable as the baseline's and right 98% of the time, patches visibly
depleted and recovered, and supply limitation developed across the run. The world
was built as specified and it worked. What it did not do was put sensing on the path
of least resistance.

Three things are worth carrying forward, and the third is the interesting one.

**The evolved side went further from sensing, not closer.** In the baseline and in
RBT-16, holistic bests carried food sensors and ignored them. Here they do not carry
them at all, while eating more than twice as much as the baseline's best lumps. Given
a world with a stronger gradient, the search spent its budget on mowing harder and
threw the sensor away. Patches make blind mowing *better*, because a mower that
blunders into a patch gets several items instead of one, and that is a hill the
search can climb one mutation at a time, which chemotaxis still is not.

**The world bought its gradient partly out of heritability.** Yield heritability
fell from 0.51 to 0.246, well past the 0.4 floor expectation 2 set. Patch luck adds
exactly the within-season variance the spec predicted, and that variance is noise the
selection has to see through. So the persistent world sharpened the signal a nose
could read while halving the signal selection could act on. That trade was not
priced before the run, and it is a general caution for any future arm that adds
structure to the world: structure that helps a sensor can hurt the search.

**The one nose that pays is a throttle, and that is a new kind.** The baseline's
nose-dependent Pioneer was a brake, kept in the disc by its noses. This run's
gen-300 best is the opposite: with its noses on it leaves the disc *more*, moves
twice as far, and eats significantly more per metre it covers inside the disc. Its
single chassis nose gates locomotion on the presence of a smell. That is a step past
a brake and it is still one bit, expressible by one sensor and one weight, which is
precisely why the search found it and not a pairing.

So the null of expectation 5 stands, and its conclusion with it: the series has run
out of world to blame. Six arms changed one thing each and this one changed three at
once, on a calibrated ledger, and the answer did not change. **The next question is
the search, not the arena.** RBT-25's heritable effector and joint dynamics is one
half of it; the half this run points at most directly is a mutation operator that
can wire two separated sensors into a crossed pairing in one step, because every
result in this series is consistent with a world where the pairing would pay and
cannot be reached one mutation at a time.

One concrete suggestion for whoever takes that up: the Pioneer's two wheel noses
have now sat unlinked in the best controller of at least two 600-season runs. That is
not the world failing to reward a pairing. That is the search never once proposing
one.
