# The Cow Is the Correct Answer

*Sixth paper in the Rabbitstew series, and a synthesis rather than a run. The measurement it
rests on: in every world this family has built, yield is linear in the ground a body sweeps,
so the optimal body is a cheap mower, and no world has been built in which that is false
while a population can also live in it. The foraging ecology has now been run on five seeds,
two work costs and ten world variants; five went extinct at the bootstrap line and all five
survivors converged on blind grazing, none with a compass on either side. Sections 1 to 4
read those arms together, section 5 measures the density axis that was supposed to break the
result, and section 7's expectations for the last three arms were written before any of them
reported and are scored in the postscript. Sources: `docs/foraging-world.md`,
`docs/persistent-world.md` and the fan-out reports on Chaotic RBT-13 to RBT-23.*

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

**The grazer's yield is consistent with what a random walk of its length should meet.** The
foraging document put this qualitatively; the persistent-world calibration made it quantitative
by showing harvest is linear in the standing crop over a factor of five in density. It is
linearity that is measured, not the constant: RBT-39 points out that the blind-mow floor of
twice the eat radius times the density is a *point* robot's rate, and a real body sweeps a
corridor wider than that, so a yield above the floor proves nothing and only a yield below it
is damning. Nothing in this paper rests on the constant. A body whose
yield is proportional to the ground it sweeps is a grazer in the technical sense, and the only
thing worth optimising for such a body is distance covered per unit of energy. That is what
six hundred seasons produced: a path that lengthened from 2.3 m to 11.9 m while energy per
metre fell, ending in a 9 m mow on 2.3 kJ, the cheapest locomotion anywhere in the series.

**In a world of dense, immobile, uniformly scattered, instantly renewed food, this is optimal
and a nose is a cost.** At twelve items in a 3 m disc a random walk of 7 m meets about two items
a season for a movement cost of 0.36 energy, so grazing blind clears the 0.25 basal cost with
room to spare and the marginal item a nose would buy is worth less than the wiring that finds it.
Nothing in six hundred seasons asked the population a question that a longer cheaper walk did not
answer, and evolution correctly declined to pay for an organ that earns nothing. The cow is not the search failing.
It is the search succeeding at the problem we posed. The persistent world later made the point
against itself: clustering the food raised the evolved side's yield from the baseline's 2.1 to
2.5 items to 5.75, and it got there by dropping the food sensor entirely (RBT-19).

## 2. The nose was not missing. It was priced out.

**This section has been re-read at 64 paired seeds and rewritten. Half of what it originally
claimed did not survive** (RBT-38, `runs/RBT-38/pair_rbt21.txt`). The draft argued that selection
was offered a working nose and a hindering one and kept the hindering one. The working nose was
read off eight seeds and is not there at sixty-four. What follows is what the re-read supports,
and it is narrower than the draft; the draft's numbers are shown beside it rather than quietly
replaced.

**RBT-21 watched selection keep a body whose nose was costing it.** At a work cost of 0.08 per kJ
the wheeled founders were sorted rather than wiped: none died of a single season's work, fifty-one
of sixty were net negative, and over thirteen seasons the population's mean gain climbed from
−1.16 to +0.50 as the expensive drivers were removed. That is the clearest selection for economy on
the designed body anywhere in the family. Two Pioneers bracket what it chose, and at 64 paired
seeds, intact minus noses blanked:

| | published, n = 8 | re-read, n = 64 | verdict |
|---|---|---|---|
| `c0-8`, the season-0 best | loses 57% of its food | +0.281 items, paired SE 0.175, t = +1.61, CI [−0.061, +0.623] | **not separable; the 57% does not survive** |
| `c0-4`, the season-10 best | eats twice as much blanked | −0.609 items, paired SE 0.145, t = −4.19, CI [−0.894, −0.324] | **separable; 2.11×, replicated** |
| the two effects differ | asserted | +0.891, SE 0.227, t = +3.92, p = 0.0003, CI [+0.445, +1.336] | **separable** |

So the contrast the section rests on passes its pre-registered test: these two individuals'
noses do measurably different things. But only one of them does anything at all, and it is the
harmful one. `c0-8`'s nose is not demonstrably finding food; `c0-4`'s is demonstrably costing its
bearer six tenths of an item a season. The corrected claim is therefore not that selection chose
a hindering nose over a working one. It is that **selection kept the more economical body despite
its nose being a measurable liability, and the nose was not what selection acted on.** RBT-21's
own reading supports this better than the draft did: `c0-4` intact eats 0.547 against `c0-8`'s
0.953 and outlived it anyway, because it won on work rather than on yield.

**And neither is a compass.** Distance to the nearest item while in the disc is unmoved for both
(t = +0.64 and +0.12). What moves in both cases is ground covered, at unchanged yield per cell of
that ground: blanking `c0-8`'s noses shortens its path and narrows its sweep (t = +10.2 and +3.9)
while items per cell sits at t = +0.26; blanking `c0-4`'s lengthens its path, widens its sweep and
keeps it in the disc longer, with items per cell and items per metre both unmoved. Both noses
modulate how much ground gets swept and neither changes what a swept metre is worth. That is
section 1's thesis appearing inside this section's own centrepiece, which is either reassuring or
circular depending on your temperament, and is stated here so a reader can decide which.

**The same sign shows up wherever there are enough individuals to count.** In the crowded arena
(RBT-17) fourteen of sixty final Pioneers are nose-dependent and twelve are nose-hindered. In the
baseline, blanking the season-20 Pioneer's noses *raised* its yield, and by season 30 its best ate
more with every environmental sensor off. Every one of those counts was made with the eight-seed
method and none of them has been re-read yet; they are cited as a direction, not a quantity, until
RBT-38 works through the rest of its table.

**No nose-dependent controller in the series is a compass; three of them are one-bit devices.**
The complete fan-out gives three kinds, and all three ride on the chassis nose alone. A *brake*:
the baseline's season-500 Pioneer, whose noses stop it driving out of the disc, and which blanked
runs 19 m in a straight line and eats 0.12. A *throttle*: RBT-19's, which covers more distance and
takes more items per in-disc metre with its nose on. A *sweep modulator*: RBT-10's 802 free-work
Pioneer, a straighter and wider sweep through the global neurons at unchanged yield per cell of
ground covered. Each is one bit, each is a single sensor into a single gate, and all three were
read at eight or sixteen seeds and are still queued for the re-read that has already cost `c0-8`
its place on this list. The re-read has so far added a fourth instance rather than removing one:
`c0-8` itself, whose noses lengthen its path and widen its sweep at unchanged yield per cell, is a
sweep modulator, which is what it turns out to be once the food effect it was credited with is
taken away. In ten arms and two 600-season runs of the persistent world's kind,
no Pioneer ever had **both** wheel noses wired at once. RBT-19 read that as the search never
proposing a pairing, this paper quoted it approvingly, and **RBT-45 has since measured it and both
of us were wrong.** With no world and no selection, the operator proposes the *uncrossed* pairing
in 9.1% of lineages of realistic depth; it is proposed often. What is rare is the **crossed**
circuit a Braitenberg compass actually needs, at 1.3%, because two wheel brains cannot see each
other and the link must route through the global brain as a second draw.

Two things follow and both cut against what this section used to say. **Six hundred seasons is
nineteen mutations**: that is the median ancestral depth of the individuals alive at season 599,
maximum 23, which is an order of magnitude short of where the pairing's occupancy would settle.
And the sixty final genotypes are not sixty lineages; through their ancestry they descend from
eleven distinct founders. Against that, observing no crossed pairing carries a probability of
0.75 to 0.87 under pure drift. **The family's zero is not evidence that selection removed
anything. It is what a short, narrow search looks like.** The half-pairing is meanwhile common
rather than lethal, sitting in a fifth of one arm's final population, which is the opposite of
what "the intermediate is harmful" predicts. Sensing has been present in the founders of every arm and measurably functional in
several, and nothing in ten arms has carried it forward.

## 3. Every arm that made the world harder died before it could select

The fan-out is complete at ten arms. Five ended in extinction on both sides and five sustained a
population. All five survivors produced blind mowers and none produced a compass.

| Arm | Change from the baseline | Outcome |
|---|---|---|
| W2, RBT-14 | 6 items in a 4 m disc, decay 3 m | extinct at 23 and 31: no fauna to select |
| W3, RBT-15 | 60 s seasons, 6 items, basal 1.0 | extinct by season 6 |
| W3', RBT-20 | 60 s seasons at baseline density | extinct at 8 and 9 |
| W6, RBT-18 | work cost 0.15 per kJ | extinct at 3 and 33 |
| W6', RBT-21 | work cost 0.08 per kJ | extinct at 13 and 26 |
| W1, RBT-13 | smell decay 3 m | survived; blind; the smell squash saturated, so range was never tested |
| W4, RBT-16 | no regrowth, 24 items | survived; blind; its demography was the density, as W4' later showed |
| W5, RBT-17 | eight robots per arena | survived; blind |
| W1', RBT-22 | normalised smell (`log`) at decay 3 m | survived; blind; the shallowest bottleneck in the family and the best heritability, 0.56; zero of sixty saved holistic bests carry a nose |
| W4', RBT-23 | no regrowth, 12 items | survived; blind; the wheel noses had influence 0.0 for six hundred seasons; the depleted second half is real and nosed and blind robots eat the same in it |
| P, RBT-19 | persistent world: patches, depletion, state across seasons | survived; blind; the strongest mower of the series at 5.75 items, and **no holistic best carries a food sensor at all** |

**The invariant holds for all ten.** A world soft enough to sustain a population is a world in
which mowing pays. A world hard enough to punish mowing kills the population before selection can
compound anything. Ten arms have been spent traversing that line rather than finding a gap in it.

**The last three arms are the sharpest version of it.** W1' removed the excuse that the gradient
was illegible, and the population that read it best was the one that never grew a nose. W4' showed
that depletion adds "less food everywhere", a scalar the chassis nose already reads, and does not
shorten the distance a gradient must cover. P was built to answer the diagnosis rather than turn a
knob near it, and it returns two findings that cut against sensing from opposite directions:
structure that helps a sensor can hurt the search, since patches doubled the two-nose gradient and
halved yield heritability from 0.51 to 0.246 because patch luck is within-season variance; and
patches make blind mowing *better*, since a mower that blunders into a cluster takes several items
instead of one, which is a hill reachable one mutation at a time in a way chemotaxis is not.

**The mechanism is newborn endowment, and RBT-21 named it.** `birth_cost` is both what a parent
pays and, exactly, everything a child gets. A newborn therefore starts with one energy against a
basal cost of 0.25, which buys four seasons, and for a Pioneer at 0.08 per kJ, less than one
season of random driving. Ten of sixteen wheeled children in that arm lived a season or less, and
the best-fed adult in the run buried all four of its own. Every extinction in the fan-out has run
through newborns or through founders exhausting their starting energy. The measurement in the next
section puts the founders' clock at 12.0 seasons, and the starvation wave lands at season 11 in
every arm of the family, on every seed. RBT-29 is the package that tests this by decoupling a
child's starting energy from the birth cost; the RBT document "Notes: newborns, inheritance, and
the size of the world" argues that the fixed endowment is the clean instrument for it.

## 4. What the fan-out has actually been measuring

Read together, the arms have been measuring the bootstrap threshold rather than the slope toward
sensing. The fan-out's own lesson already says a world variant is only informative where random
founders form a breeding population. What has not been said is that the informative band may be
empty, and that is a measurement rather than an opinion (section 5).

**And there is a second thing the arms were measuring that nobody had counted: twenty generations.**
Every design decision in this family is denominated in seasons, and selection is denominated in
reproduction events. The conversion rate, measured across all fourteen population-rows of the ten
arms, is about thirty to one. Median first-parent chain length from an individual alive at season
599 back to a founder is **18 to 24**, and that is the number of sequential mutations the lineage
underwent (RBT-59).

It does not move with income. Mean gain across those rows spans a factor of 2.5 and its correlation
with depth is **−0.15**, because reproduction is slot-limited: births equal deaths to three decimals
in every arm, and 89% of the living sit above the birth threshold holding five to thirteen times
what they need, unable to breed. Every economy arm in section 3's table — work cost, density,
depletion, patches, crowding — varied a parameter that does not control the search rate.

Selection is not the weak link. The age-controlled difference in lifetime yield between individuals
that ever bred and those that never did is **+0.43 standard deviations**, and it works through
differential survival to breeding rather than through parent choice. So the arithmetic the fan-out
should be read against is twenty generations at about 0.43 SD, against a crossed Braitenberg circuit
that arrives in **1.3%** of lineages of that depth (RBT-45).

**This changes what section 3's table is evidence of.** Ten arms of blind mowing are not ten
independent demonstrations that no world rewards sensing. They are one demonstration, repeated ten
times, that twenty generations is not enough to assemble a circuit that arrives in one lineage in
seventy-seven.

**It does not, however, mean that a deeper search would have found one, and that has now been
tested.** RBT-60 ran the baseline at `max_age` 30 and 15, reaching depths of 39 and 78 against the
baseline's 23, and every column moved the wrong way together: heritability 0.51 to 0.461 to 0.251,
mean gain +1.41 to +1.255 to +1.094, and sensing absent at every depth, with both deeper arms'
holistic champions **bit-identical on all 64 bouts with their sensors blanked**. A lifespan is also
a sample size, so depth bought by shortening lives is paid for in the selection signal that would
have made it useful. The cow survives a search three and a half times deeper than the one that
first produced it.

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
They are a measured robot's yield scaled by a measured linearity, not the point-robot floor RBT-39
warns about, so that caution does not reach them. Every summary is a median over the non-exploded,
for the reason in section 6. Two limits to state before the findings: the solvency columns are one
season's draw per founder and so carry that season's noise, and the whole table is a solo-and-once
measurement of the kind that produced this paper's one failed prediction (section 7). RBT-33's
census, which samples founders and their one-mutation children over K seasons in company, is the
better instrument and supersedes these columns when it lands; this is the first measurement of the
band, not the last word on it. Three things fall out, and the third is the point of the paper.

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
live here" does not exist on this axis. The ladder did not step over the window: at every rung
from 3 to 24 items the mower's net is positive, from +0.04 to +3.07 in a shared arena, while the
solvent holistic founders never exceed three of sixty.

That is the answer to question 4, and it retires the density axis. The next arm is not eight items.

The persistent world then tested the same conclusion from the other side without meaning to. It did
not vary density; it clustered the same food, which is the one manipulation that should make finding
it worth something. The evolved side answered by dropping the food sensor altogether and more than
doubling its yield to 5.75 items, because a mower that blunders into a cluster takes several items
at once. Concentrating the resource made the grazer better, not obsolete.

## 6. A gap in the economy, found while measuring

`Simulation.food_score` charges `work_cost` against accumulated actuator work with no guard for
numerical instability. A robot is marked exploded once a body passes 200 m/s and is then no longer
stepped, but the work it booked on the way there is kept and billed. One holistic founder in sixty
of this paper's draw booked 1.5 × 10⁹ kJ, which at 0.03 per kJ is a bill of forty-four million
energy. In the ecology this is mostly benign, since the individual simply dies in season 0 and the
history file only records the living, and it is why this has not shown up before. It is not benign
in three places: any mean over a draw (this paper's first table was nonsense until every summary
became a median), the retired relative living cost, which would have set a whole population's
charge from that one number, and any future arm that reports mean gain including the dead. Filed as
RBT-30, which now carries the coordinator's decision: an exploded robot's season is forfeited and
flagged rather than billed. Nothing in the published results is affected.

## 7. Pre-registered expectations for the last three arms

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
   Filed as RBT-29, which decouples the two and reruns 0.08 and the baseline against them.
2. **Capacity at a marginal density.** The six-item arm went extinct at season 51 from a breeding
   population with a mean gain of +0.32, holding at five to nine individuals, which the docs
   correctly call demographic stochasticity rather than starvation. That is the one arm in the
   family that died of small numbers while solvent. Re-running six items at capacity 200 asks
   whether it dies of the economy or of the sample size, and section 5 says it is the only density
   on the ladder where an evolved mower is anywhere near marginal in a shared arena. It should not
   be run before the habitability calibrator (RBT-32): an arm whose question is demographic is
   exactly what the dry ecology should predict before anyone spends six hundred seasons on it.
3. **Evaluation fidelity, then the search, then the world.** This ordering changed twice. The draft
   put the world last and the operator second; RBT-59 put generations first on the grounds that
   depth is `2 × seasons / max_age` and `max_age` had never been varied; and **RBT-60 tested that
   and refuted it**. The law holds — depth went 23, 39, 78 as lifespan went 60, 30, 15 — and
   heritability, yield and sensing all moved against it. `max_age` does not buy search, it trades
   selection signal for search steps, because a lifespan is also the number of draws on which an
   individual is judged. What has never been tried is **decoupling the two**: repeated evaluation
   within a season, more challenges per season, or a reproduction scheme that does not tie
   assessments to lifespan. Only after that does the operator question become the binding one: RBT-25's heritable effector and joint dynamics asks half of it and RBT-42
   the other half, a correlated-link operator that can propose the crossed pairing at all, which
   RBT-45 measures at 1.3% per lineage of realistic depth against 9.1% for the uncrossed one.
   Section 5
   adds a reason to go there sooner: the holistic bootstrap is a locomotion lottery that pays one to
   three times in sixty regardless of the world, so the operators that make a lump move are upstream
   of every world question this series can ask.
4. **Two rules this paper owes the family.** A sensor-lesion effect read off eight seeds is not a
   result until it is re-read at 32 to 64 paired seeds (RBT-38, and the caveat in section 2). And a
   demographic prediction made from a solo-probe yield is not a prediction, because realised income
   in a shared arena is lower: RBT-21 caught the docs doing it, and section 7's W4' miss is this
   paper doing it. Both now stand in the README beside the lab rule. The second one belongs in
   RBT-33's design, since the census exists precisely to measure income in company.

## Reproducing section 5

```
python scripts/density_window.py 15
```

Sixty robots of each population at each of eight densities, one season each, about four minutes;
writes `density_window.json`. The founder draw is the same at every density, so density is the only
thing that differs between rows. Every summary is a median or a mean over the non-exploded, for the
reason in section 6.
