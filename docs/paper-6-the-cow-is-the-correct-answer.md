# The Cow Is the Correct Answer

*Sixth paper in the Rabbitstew series, and a synthesis rather than a run. The foraging
ecology has now been run on five seeds, two work costs and nine world variants, and every
population that survived converged on blind grazing. This paper argues that the grazer is
not a failure of the search but the correct optimum of every world we have built, measures
the one axis that was supposed to break it, and pre-registers expectations for the three
arms in flight. Sections 1 to 4 draw on `docs/foraging-world.md`, `docs/persistent-world.md`
and the fan-out reports on Chaotic RBT-13 to RBT-21; section 5 is a new measurement made for
this paper; section 6 was written before RBT-19, RBT-22 or RBT-23 reported anything.*

## Questions

1. Is the blind mower a failure of the search, or the optimum of the world it lives in?
2. Sensing appeared in the founders of nearly every arm. Why did it not spread?
3. Why has every arm that made the world harder ended in extinction rather than in selection?
4. Is there a density at which mowing stops paying and a population can still live?

## 1. The cow, and why it is right

**What evolved is a grazer, and the record is now five seeds deep.** Across the replication
on seeds 801, 802 and 803 at two work costs (RBT-10), thirteen of sixteen holistic bests show
no sensor lesion above 25%; of the three that do, none carries a nose and one is actively
harmed by its sensors. Three bests carry a food or agent nose and none of them reads it. The
same holds in the surviving fan-out arms: RBT-13's strongest mower of the whole series, 3.12
items on 1.2 kJ, carries a nose it never uses, and RBT-16's season-590 lump carries two food
sensors on two separated segments, which is the wiring a Braitenberg pairing needs, and earns
nothing with them.

**The grazer's yield is exactly what a random walk of its length should meet.** The foraging
document put this qualitatively; the persistent-world calibration made it quantitative by
showing harvest is linear in the standing crop over a factor of five in density. A body whose
yield is proportional to the ground it sweeps is a grazer in the technical sense, and the only
thing worth optimising for such a body is distance covered per unit of energy. That is what
six hundred seasons produced: a path that lengthened from 2.3 m to 11.9 m while energy per
metre fell, ending in a 9 m mow on 2.3 kJ, the cheapest locomotion anywhere in the series.

**In a world of dense, immobile, uniformly scattered, instantly renewed food, this is optimal
and a nose is a cost.** Grass does not hide and does not run. Nothing in six hundred seasons
asked the population a question that a longer cheaper walk did not answer, and evolution
correctly declined to pay for an organ that earns nothing. The cow is not the search failing.
It is the search succeeding at the problem we posed.

## 2. The nose was not missing. It was priced out.

This is the strongest claim in the paper and it rests on one pair of individuals.

**RBT-21 watched selection remove a working nose.** At a work cost of 0.08 per kJ the wheeled
founders were sorted rather than wiped: none died of a single season's work, fifty-one of sixty
were net negative, and over thirteen seasons the population's mean gain climbed from −1.16 to
+0.50 as the expensive drivers were removed. That is the clearest selection for economy on the
designed body anywhere in the family. Two Pioneers bracket what it chose. `c0-8`, the season-0
best, loses 57% of its food when its noses are blanked: a working nose. `c0-4`, the founder that
survived ten seasons of that selection to become the season-10 best, eats **twice as much** with
its noses blanked. Same body, same stock three-nose layout, same controller topology, same mean
weight magnitude, opposite lesion sign. Both are generation-0 founders and no child in that run
ever became a best, so this is not a nose decaying over generations. It is selection, offered a
working nose and a hindering one, keeping the hindering one, because at that price `c0-8`'s half
an item was worth less than the wheels it rode on.

**The same sign shows up wherever there are enough individuals to count.** In the crowded arena
(RBT-17) fourteen of sixty final Pioneers are nose-dependent and twelve are nose-hindered. In the
baseline, blanking the season-20 Pioneer's noses *raised* its yield, and by season 30 its best ate
more with every environmental sensor off.

**Every nose-dependent controller in the entire series is a brake, not a compass.** The baseline's
season-500 Pioneer does not steer to food; its noses stop it driving out of the disc, and blanked,
it runs 19 m in a straight line and eats 0.12. RBT-13's and RBT-17's nose-dependent bests fail the
same brake-or-compass check the same way. Six hundred seasons, six arms, and no Pioneer ever wired
its two wheel noses into a pairing; the only thing that ever got wired was the chassis nose, into
a gate. Sensing has been present in the founders of every arm, measurably functional in several,
and the economy has priced it out every time.

## 3. Every arm that made the world harder died before it could select

Of the eight completed fan-out arms, five ended in extinction on both sides and three sustained a
population. All three survivors produced blind mowers.

| Arm | Change from the baseline | Outcome |
|---|---|---|
| W2, RBT-14 | 6 items in a 4 m disc, decay 3 m | extinct at 23 and 31: no fauna to select |
| W3, RBT-15 | 60 s seasons, 6 items, basal 1.0 | extinct by season 6 |
| W3', RBT-20 | 60 s seasons at baseline density | extinct at 8 and 9 |
| W6, RBT-18 | work cost 0.15 per kJ | extinct at 3 and 33 |
| W6', RBT-21 | work cost 0.08 per kJ | extinct at 13 and 26 |
| W1, RBT-13 | smell decay 3 m | survived; blind |
| W4, RBT-16 | no regrowth, 24 items | survived; blind |
| W5, RBT-17 | eight robots per arena | survived; blind |

**The invariant.** A world soft enough to sustain a population is a world in which mowing pays. A
world hard enough to punish mowing kills the population before selection can compound anything.
Nine arms have been spent traversing that line rather than finding a gap in it.

**The mechanism is newborn endowment, and RBT-21 named it.** `birth_cost` is both what a parent
pays and, exactly, everything a child gets. A newborn therefore starts with one energy against a
basal cost of 0.25, which buys four seasons, and for a Pioneer at 0.08 per kJ, less than one
season of random driving. Ten of sixteen wheeled children in that arm lived a season or less, and
the best-fed adult in the run buried all four of its own. Every extinction in the fan-out has run
through newborns or through founders exhausting their starting energy. The measurement in the next
section puts the founders' clock at 12.0 seasons, and the starvation wave lands at season 11 in
every arm of the family, on every seed.

## 4. What the fan-out has actually been measuring

Read together, the arms have been measuring the bootstrap threshold rather than the slope toward
sensing. The fan-out's own lesson already says a world variant is only informative where random
founders form a breeding population. What has not been said is that the informative band may be
empty, and that is a measurement rather than an opinion.

## 5. The density window is empty (new measurement)

The density ladder the family has climbed is 3, 6, 12 and 24 items in the 3 m disc, plus 6 in a
4 m disc. The docs read this as "random lumps bootstrap somewhere between six and twelve", which
invites the obvious next arm at eight or nine. `scripts/density_window.py` measures that band
directly: sixty random robots of each population, the same founder draw at every density, one 15 s
season, the baseline economy, no evolution. It also asks the counterfactual the ladder never asks,
which is what the baseline's *evolved* mower would net at each density if it were there.

| items | items/m² | lump ate | lump solvent of 60 | Pioneer ate | Pioneer solvent of 60 | mower net, alone | mower net, in a four |
|---|---|---|---|---|---|---|---|
| 3 | 0.106 | 0.02 | 1 | 0.27 | 13 | +0.17 | +0.04 |
| 6 | 0.212 | 0.03 | 2 | 0.50 | 18 | +0.73 | +0.47 |
| 8 | 0.283 | 0.03 | 2 | 0.80 | 24 | +1.11 | +0.76 |
| 9 | 0.318 | 0.03 | 2 | 0.83 | 26 | +1.29 | +0.91 |
| 10 | 0.354 | 0.03 | 2 | 0.68 | 22 | +1.48 | +1.05 |
| 12 | 0.424 | 0.03 | 2 | 1.13 | 27 | +1.86 | +1.34 |
| 16 | 0.566 | 0.03 | 2 | 1.25 | 28 | +2.61 | +1.92 |
| 24 | 0.849 | 0.05 | 3 | 2.43 | 39 | +4.11 | +3.07 |

The mower columns take the baseline's season-100 best, 2.25 items on 4.8 kJ, scaled linearly in
density, and the second applies RBT-21's realised-versus-solo correction of 0.385 against 0.50.
Three things fall out, and the third is the point of the paper.

**The founders' clock is 12.0 seasons and it explains the wave.** A lump that eats nothing pays
the basal cost and almost nothing else, its median work being 0.01 kJ, so three units of founding
energy last exactly 12.0 seasons. The starvation wave at season 11 in every arm of this family is
that number. A newborn's single unit buys 4.0 seasons for a lump and 3.6 for a Pioneer.

**A random lump's yield barely depends on density at all.** Over a factor of eight in food, a
random lump's take rises from 0.02 to 0.05 items and the number of solvent founders out of sixty
goes 1, 2, 2, 2, 2, 2, 2, 3. A random Pioneer's take over the same range rises from 0.27 to 2.43,
which is linear. The reason is in the work column: a random lump spends 0.01 kJ, which is to say it
does not move, and a body that does not move does not care how much food there is. **The density
axis is not a knob on the holistic bootstrap.** Every density arm in the family has been measuring
the Pioneer's budget and a locomotion lottery that pays out one to three times in sixty, which is
exactly the one-to-three founders that every dense run's final ancestry contains.

**There is no density at which mowing fails and anything lives.** The evolved mower is solvent at
every density on the ladder, including three items, where the sparse arm went extinct on both
sides: +0.17 alone and +0.04 sharing an arena with three others. Below that the mower goes under,
but so does everything else, and by then the founders are a full order of magnitude short of
bootstrapping. The window between "a blind grazer cannot live here" and "random founders cannot
live here" does not exist on this axis. It is not that the ladder stepped over the window. There
is no window to step over.

That is the answer to question 4, and it retires the density axis. The next arm is not eight items.

## 6. A gap in the economy, found while measuring

`Simulation.food_score` charges `work_cost` against accumulated actuator work with no guard for
numerical instability. A robot is marked exploded once a body passes 200 m/s and is then no longer
stepped, but the work it booked on the way there is kept and billed. One holistic founder in sixty
of this paper's draw booked 1.5 × 10⁹ kJ, which at 0.03 per kJ is a bill of forty-four million
energy. In the ecology this is mostly benign, since the individual simply dies in season 0 and the
history file only records the living, and it is why this has not shown up before. It is not benign
in three places: any mean over a draw (this paper's first table was nonsense until every summary
became a median), the retired relative living cost, which would have set a whole population's
charge from that one number, and any future arm that reports mean gain including the dead. Filed
as its own ticket; nothing in the published results is affected.

## 7. Pre-registered expectations for the three arms in flight

Written before RBT-19, RBT-22 and RBT-23 reported. Each carries the reason and the observation
that would falsify it. Where these disagree with the pre-registration already in
`docs/persistent-world.md`, both stand and the run decides; that document's expectations are the
project's, these are this paper's, and the disagreement on RBT-19 is the interesting one.

**W1', RBT-22 — normalised long-range smell (`log`, decay 3 m, baseline density).**

1. Demography within noise of the baseline: the wave at season 11, recovery, both populations full
   at 599. Confidence high; the economy is the baseline's unchanged.
2. No holistic best loses more than 25% of its yield to `no_food` at any sampled season.
   Confidence high.
3. If any nose-dependent best appears it is on the wheeled side and fails brake-or-compass as a
   compass.

*Reason.* This arm fixes readability, and readability was never the binding constraint. At twelve
items regrowing instantly at random, the food a robot smells is not the food that will be there,
so a gradient is information about a world that will not exist by the time the robot arrives. The
arm's own signal-range table makes the point sharper than I can: `log` at 3 m still delivers about
half the per-metre slope of the plain sum at 1 m, so this world hands a nose a *longer but
shallower* gradient than the baseline already had, and the baseline produced nothing in six
hundred seasons on five seeds. *Falsified by* a holistic best above the 25% line that passes
brake-or-compass.

**W4', RBT-23 — no regrowth, 12 items.**

1. The holistic wave lands at season 11 or 12 and the remnant is no larger than the baseline's 7.
2. The wheeled population falls below 20 by season 20, and more likely than not below 10 by
   season 60.
3. No sensing on either side, whoever survives.

*Reason.* Depletion without regrowth takes the group's harvest from 4.75 to 3.25, which is 0.81
items per robot, and a random Pioneer at 0.81 items pays 0.56 in work and 0.25 in basal cost for a
net of zero. This arm puts the wheeled founders exactly on the break-even line rather than the
baseline's +0.38, which is a demographic change, not an informational one. The holistic side is
unaffected either way, because section 5 says its founders do not respond to food density. On the
sensing question, RBT-16 already ran the within-season gradient at 24 items and measured nosed and
blind robots eating the same in the depleted second half. *Falsified by* a surviving population
carrying a best that passes brake-or-compass.

**P, RBT-19 — the persistent world.** This is the arm built to beat the cow, calibrated before
launch, and the one where I expect to be told I am wrong.

1. The demography works: founders at +0.31, the wave at 11, recovery, both populations persist to
   599. Confidence high; the ledger was constructed for exactly this.
2. Supply limitation bites by mid-run: group harvest rises toward the 8.67 ceiling and per-robot
   yield falls below the founders' 1.12. Confidence moderate to high.
3. **The world's own expectation 4 fails.** No holistic best loses more than half its yield to
   `no_food`, and no Pioneer best passes brake-or-compass as a compass. Confidence moderate, and
   this is the prediction I hold most loosely.

*Reason.* Patches, depletion and persistence change where the food is and how long it stays
missing. They do not change the fact that an evolved mower covers nine to twelve metres a season
inside a three-metre disc, crossing the whole arena several times. A gradient that points at the
nearest patch saves travel, and travel is not the scarce thing here. Supply limitation caps
everyone's harvest at the same ceiling; a ceiling does not pay a smeller more than a mower, it
pays them both less. The genuinely new signal is depletion, and the decision it supports is
"this patch is finished, go elsewhere", which a mower already implements by never stopping.

*What beats me.* The world can ask for within-season patch-leaving, which is what an integrator is
for, and the fan-out has never seen a state-holding unit matter anywhere. If a best turns up whose
yield depends on a `integrate` unit, or if the two-nose difference being twice the baseline's and
right 98% of the time is enough for a bias mutation to climb after all, I am wrong and the world
was the answer. *Falsified by* expectation 4 being met on either side.

**The thesis behind all three.** Sensing pays only where finding food faster than chance is worth
more than covering ground, and no world in this family has been built where that is true while a
population can also live in it. Three nulls would not mean evolution cannot find a nose. They would
mean we have not yet built a world that wants one.

**Postscript, scored after the three arms reported (coordinator, 2026-09-12).** W1' (RBT-22): all three expectations held. W4' (RBT-23): expectations 1 and 3 held; expectation 2 failed, the wheeled population never fell below 60, because realised income in a four is not the per-robot mean the break-even arithmetic used (the same error RBT-21 caught in the docs). P (RBT-19): expectations 1 and 3 held, expectation 2 half-held (supply limitation developed; per-robot yield rose rather than fell); the "what beats me" clause was not triggered, no state-holding unit mattered anywhere. The thesis stands on the evidence, and its one miss is a demographic prediction from a solo-derived number.

## 8. What I would vary next, in order

1. **Newborn endowment.** `birth_cost` is one number doing two jobs: the parent's price and the
   child's entire capital. Every extinction in the fan-out ran through it. Separating them costs a
   field and would let an arm ask an economic question without the answer being decided in the
   nursery. No value proposed; it wants the same pre-launch calibration the persistent world got.
2. **Capacity at a marginal density.** The six-item arm went extinct at season 51 from a breeding
   population with a mean gain of +0.32, holding at five to nine individuals, which the docs
   correctly call demographic stochasticity rather than starvation. That is the one arm in the
   family that died of small numbers while solvent. Re-running six items at capacity 200 asks
   whether it dies of the economy or of the sample size, and section 5 says it is the only density
   on the ladder where an evolved mower is anywhere near marginal in a shared arena.
3. **The search, not the world.** If RBT-19 nulls, `docs/persistent-world.md` already says the next
   question is mutation rather than another arena, and RBT-25's heritable effector and joint
   dynamics is the arm that asks it. Section 5 adds a reason to go there sooner: the holistic
   bootstrap is a locomotion lottery that pays one to three times in sixty regardless of the world,
   so the operators that make a lump move are upstream of every world question this series can ask.

## Reproducing section 5

```
python scripts/density_window.py 15
```

Sixty robots of each population at each of eight densities, one season each, about four minutes;
writes `density_window.json`. The founder draw is the same at every density, so density is the only
thing that differs between rows. Every summary is a median or a mean over the non-exploded, for the
reason in section 6.
