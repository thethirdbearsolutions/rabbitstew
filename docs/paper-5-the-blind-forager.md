# The Blind Forager

An economy with no fitness function evolved locomotion from survival alone, and the evolved bodies out-ate the designed one.

*Draft of the fifth paper in the series, written under Chaotic RBT-43. It argues the positive result of the
foraging programme, which currently runs as a thread through `docs/foraging-world.md` — a document organised
around the question the world kept answering "no" to. Nothing here is re-run: every number is cited to the run,
report or ticket it came from, and the fan-out is cited rather than recounted. `docs/foraging-world.md` remains
the fan-out's record and keeps the sensing null. Numbering and final title are the project owner's to settle.
Reproduction on fresh seeds and positioning against the open-ended-evolution literature were added under RBT-71
(Deliverables A and B): §0, the abstract, and the fresh-seed numbers in §§1–4 and §7 are that pass, and every
external citation in §0 was checked against its own record before it was written down.*

---

## Abstract

In a physically simulated world with food in a disc, a work cost per kilojoule, a basal cost per season, a birth
threshold and a lifespan, and nothing that scores, ranks or holds a tournament, a population of random bodies
evolved locomotion from survival alone in about twenty generations, on every seed tried (six). At four robots per
arena and twelve items in a three-metre disc, the co-evolved bodies led a designed differential-drive body on mean
energy gain for the majority of seasons on every seed, by a margin ranging from a fifth of an energy unit a season
to nothing, ending ahead on four seeds, at parity on one and behind on one; the lead reverses at eight robots per
arena, and the cheapness of the evolved gait is a property of the work-cost coefficient rather than of the bodies.
Lifetime foraging yield is heritable parent-to-child at 0.51, 0.40, 0.38 and 0.34 on the co-evolved side over the
founding seed and three pre-registered fresh seeds, against paired drift controls of the same world at −0.13 to
+0.07, where the competitive bout score used in the same simulator's arena carried no heritable signal; the
designed body's yield is as heritable under drift as under selection, so what changed is the measurement, not the
bodies. The foragers are blind, and §6 says what is and is not known about why. Every number is cited to a
committed report, and every scorecard quantity of the reproduction re-derives from the repository alone.

---

## 0. Where this sits, and what is and is not new in it

Selection without a fitness function is the founding move of a whole branch of artificial life, and this paper
does not rediscover it. Tierra evolved self-replicating machine code in a shared memory with no score at all, death
by a reaper queue and reproduction by copying (Ray, 1991); Avida gave that idea a two-dimensional geometry and then
a research platform (Adami & Brown, 1994; Ofria & Wilke, 2004); Polyworld put metabolism, vision, Hebbian learning
and reproduction into one ecology and let speciation come out of it (Yaeger, 1994); Geb was the first such system
to pass Bedau and Packard's activity statistics as unbounded (Channon, 2001); Division Blocks evolved physically
simulated bodies and their controllers "by natural selection" in a world whose energy comes from a simulated sun
(Spector, Klein & Feinstein, 2007); Chromaria was built to test which conditions such a world needs, the first of
them a minimal criterion an individual must meet to reproduce (Soros & Stanley, 2014); and open-ended foraging
with no explicit fitness has its own line (Miconi, 2011; Utimula, 2025). Co-evolved three-dimensional bodies in a
physically simulated world are Sims's (1994a, 1994b), and they have been run under free natural selection before:
Evosphere reimplemented Sims's creatures on a "microplanet" where they fight, are damaged and die, with no fitness
function (Miconi & Channon, 2006; Miconi, 2008). The economy in §2 is a small member of this family: energy from
food, a work cost, a basal cost, a birth threshold, a lifespan, and nothing that ranks.

The other half of the paper's ancestry is the body-brain co-optimisation literature, which is where the designed
body comes from and where the arena result of papers 1 to 4 already sits. Cheney, Bongard, SunSpiral and Lipson
(2016) is the canonical account of why co-optimising morphology and control underperforms: the morphology
converges before the controller has caught up with it, and a body mutation is punished because the controller
co-adapted to the old body no longer fits. Their follow-up proposed morphological innovation protection, a
temporary reduction of selection pressure on recently body-mutated individuals (Cheney et al., 2018); this
programme has never run it. Mertan and Cheney (2025) then trained controllers for 1,305,840 voxel designs and
mapped the whole morphology-fitness landscape against complete knowledge: the co-optimisers reach
morphology-controller pairs that fixed-morphology optimisation cannot, and then discard them, "regularly
undervalu[ing] individuals with newly mutated bodies." Read together, *"the designed body wins" is a statement
about the search, not about bodies*, and the 2005 proposal's flaw was its measurement rather than its
hypothesis. That sentence is strand 1's and is argued in full in RBT-73; it is stated here on those two
citations because §3 and §4 rest on it.

**What I could not find, and looked for.** A designed body and co-evolved bodies placed in the *same*
fitness-free economy and compared on realised income; and, in one simulator, the heritability of the quantity
that economy selects on set beside the heritability of the competitive score it replaced. The nearest neighbours
are Chaumont and Adami (2016), who co-evolve articulated foragers in three-dimensional physics but under an
explicit, staged fitness function and with no designed body beside them; Evosphere and Utimula's guideless model,
which are fitness-free and grow morphology but carry no designed control and compare no yields; and the
co-optimisation papers above, whose fixed-morphology comparisons are all made under an explicit objective.
**Coverage of that search, so the null is read at its weight**: general web search plus arXiv, Springer, MIT Press, ACM, IEEE Xplore
and Semantic Scholar records, from 10:52 to 11:06 UTC on 2026-09-14, about fifteen minutes of wall-clock (the
timestamps are in `runs/RBT-71/citations-check.txt`), following the ticket's own two-hour pass of the day before;
eighteen search queries and twelve record fetches, of which three queries were aimed
directly at a designed or fixed body compared with co-evolved bodies inside an artificial ecology with metabolism
and no explicit fitness; every citation above was then checked against the paper's own abstract or record. It is not a systematic review, no bibliographic database was queried
exhaustively, and a reader who knows a counter-example should file it against RBT-71. The contribution this paper
claims is therefore the configuration and the contrast, not the move: change the instrument from a ranked bout
to an economy, keep the simulator and both populations, and the co-evolved bodies stop being discarded (§3) while
the quantity selection acts on starts carrying information between generations (§4). That is consonant with
Mertan and Cheney, and offered as an independent, differently-mechanised instance of it.

---

---

## 1. The claim

**An ecology with no fitness function, no ranking and no tournament evolved locomotion from survival alone, in
about twenty generations; and at the four-robot baseline density the evolved bodies ended up out-foraging the
designed one on a fraction of its energy, a lead that reverses in a crowded arena (RBT-17).** The overtake,
the bottleneck and the heritability were reproduced on three fresh founding seeds under a pre-registered verdict
rule (RBT-71, Deliverable A; `runs/RBT-71/REPORT.md`): all three clauses met on all three seeds, and the effect
smaller on every fresh seed than on the seed this paper was first written from.

Nothing in the foraging ecology scores a robot. There is no target, no opponent, no rank, no elite and no
tournament. There is food in a disc, a work cost per kilojoule of actuator effort, a basal cost per season, a
birth threshold, a birth cost and a lifespan. A robot that eats enough keeps living and eventually breeds into
a slot that somebody's death opened. That is the whole selective apparatus.

Two things came out of it that were not put in. The first is movement, and then cheaper movement. The second is
a measurement that carries information between generations, which nothing else in this family of experiments
has produced.

One thing did not come out of it: perception. Section 6 argues that this is a fact about the search's reach and
not about the world's payoff, and that the distinction is now measured rather than assumed.

---

## 2. Locomotion from survival

This is the claim with the cleanest control and it is the one to defend hardest.

On seed 801 at work cost 0.03 per kilojoule, the distance the best holistic individual covers alone in a season
went **2.3 m, 2.9 m, 3.9 m, 7.2 m at seasons 0, 10, 20 and 30**, on 3.5 kJ where the Pioneer spends 17; by
season 100 the same lineage's path had reached 11.9 m while its energy per metre fell
(`docs/foraging-world.md`, first-forty-seasons and season-100 sections). No target sensor exists in the
`foraging` vocabulary. No score rewarded distance. Distance is what survival bought.

The path series above is one seed. What replicates across the five dense-arm runs — 801, 802 and 803 at work
cost 0.03 and at 0 (RBT-10, branch `claude/determined-shannon-2zb8jp`, `runs/RBT-10/`) — is the shape rather
than the series: the starvation wave, the recovery, the overtake, and a blind mower in every best. Thirteen of
sixteen replicate bests show no sensor lesion above 25%, and the three that do carry no nose (RBT-10).

**Why this is not drift.** The neutral control runs the same bodies and the same six hundred seasons with
nobody starving, breeding free and turnover by age alone. On the founding seed it finished with **14 holistic and
16 wheeled founders of 60** still in the final ancestry and its means unchanged from season 0; on the three fresh
seeds, each with its own paired control, the controls kept **12, 12 and 6** holistic founders while the foraging
arms kept **1, 1 and 3** (RBT-71). The foraging arms of RBT-10's replicates kept 3. Drift at this capacity over
ten lifespans keeps between a tenth and a quarter of the founders, and that spread is drift's own variance;
selection through starvation kept one to three on every seed run. The 3 against 6 on seed 806 is a margin, not
evidence, and the reproduction report says so. The control is in the toolkit as
`rabbitstew heritability RUN --drift-baseline NEUTRAL_RUN`, so the comparison is reproducible rather than an
impression (RBT-7).

**The bottleneck reproduces in kind, not in depth.** The season-11 starvation wave is the same size everywhere,
30 to 41 deaths, but the population minimum across the six seeds run at work cost 0.03 is **7, 8, 26, 28, 31
and 42** (801, 805, 804, 806, 802, 803), and on 805 the minimum came at season 16, five seasons after the wave,
not at the wave itself (RBT-71). The widely quoted 60 → 7 is the extreme, not the type, and a thirteen-season
re-run of 801 on current code reproduces it exactly, so the depth is the seed (RBT-10).

---

## 3. The overtake, and how much search bought it

The evolved side overtakes the designed one on mean energy gain early — season 83 on 801, 11 to 30 on the RBT-10
replicates, 17 to 27 on the pre-registered fresh seeds — and leads for the majority of seasons on every seed run.
How much of the run it leads, and by how much, is the seed. On 802 and 803 the lead held in **450 to 566 of 600
seasons** by +0.13 to +0.21 a season over seasons 100 to 599 (RBT-10); on 804, 805 and 806 it held in **571, 484
and 411 of 600** by **+0.21, +0.11 and +0.045** a season, and at season 599 the wheeled side was ahead on 806,
+1.02 to +0.94 (RBT-71). Over six seeds the holistic side ends ahead on four, at parity on one and behind on one.
801's climb to +1.63 at season 500 does **not** reproduce anywhere: the RBT-10 replicates plateau at +1.0 to +1.3
from season 30 on, and the fresh seeds end at +0.94 to +1.18 against the designed body's +0.98 to +1.10. The
honest sentence is that the co-evolved bodies out-forage the designed one for most of the run on every seed tried,
by a margin that ranges from a fifth of an energy unit a season to nothing; "for 450 to 566 of 600 seasons" was
the two most favourable replicates, and the fraction of seasons led is a duration measure that says nothing about
where the lead sits at the end.

**Six hundred seasons is about twenty generations, and the sentence must be written that way.** RBT-59 walked
first-parent chains in every arm with a committed lineage log: median first-parent depth is **18 to 24 across
fourteen population-rows in ten arms**, about **thirty seasons per reproduction event**. Reproduction is
slot-limited rather than income-limited — births equal deaths to three decimals in all fourteen rows, and 89%
of the living sit above the birth threshold holding five to thirteen times what they need and cannot spend it —
so depth follows `2 × seasons ÷ max_age`, and `max_age` has been 60 in every run this programme has done.

So "the evolved side overtakes and holds for 450 of 600 seasons" describes roughly twenty sequential mutations,
not six hundred rounds of anything. This makes the result **stronger, not weaker**: locomotion, cheapness and a
sustained lead over a designed body emerged inside about twenty generations of a search with no objective
function. It also means the lead is held by a population that is barely turning over, which is a fact about the
ecology's demography and not about the bodies.

Selection is nonetheless real. RBT-59 predicted, before measuring, that parents would be close to a uniform
draw and was wrong: the age-controlled standardised difference in lifetime yield between individuals that ever
bred and those that never did is **+0.43 SD median, range +0.03 to +0.85**. It acts through differential
survival to breeding — breeders reach mean age 45 to 58, non-breeders 10 to 44 — rather than through any choice
at a slot. That figure is a lower bound by its author's own note, since living longer is part of how a good
forager converts yield into offspring.

RBT-59 has since been accepted.

---

## 4. A measurement that carries between generations

Lifetime foraging yield is heritable. Parent-child correlation of a child's lifetime mean yield against its
parents' is **0.51 on seed 801, 0.28 to 0.44 across RBT-10's four replicates, and 0.40, 0.38 and 0.34 on the
three pre-registered fresh seeds** (628 to 657 pairs each) on the holistic side; 0.14 to 0.39 and 0.23 to 0.28 on
the wheeled side; and 0.246 to 0.56 across the wider fan-out — 0.56 in the long-range-smell arm (RBT-22), 0.246
in the persistent world (RBT-19), which is the lowest in the family and failed its own pre-registered floor of
0.4. **Against zero for any bout outcome anywhere in this series.** The 0.51 is the top of a range and not the
number.

Two controls now travel with that range, and they say different things. The **paired neutral controls** on 804,
805 and 806 — same world, same seed, nobody starves, breeding free — read **+0.07, −0.06 and −0.13** on the
holistic side: a drift population of random lumps never learns to eat (mean gain +0.01 to +0.03 at season 599, as
at season 0), so its lifetime yields are seasons' draws and carry nothing between generations. RBT-82's
independent short control reads 0.15 with an interval including zero, and the 0.52 once quoted for the founding
seed's control in `docs/foraging-world.md` is on no branch and is marked unverified there. But the same controls
read **0.24, 0.34 and 0.35 on the wheeled side**, which arrives able to eat: its yield is as heritable under
drift as under selection (0.23 to 0.28). So what these numbers certify is that lifetime yield is a *heritable
measurement* in this world, for any body that eats at all — not that selection produced the heritability. That
is the paper's claim stated correctly, and it is the stronger form: the bout score carried nothing between
generations under any regime this programme ran; lifetime yield carries something even with no selection acting
(RBT-71, RBT-82).

This is the result I would put first in a positioning paper, and §0 places it. The competitive score this project
spent three papers on carried no information from parent to child; a survival economy with no score at all
produced a quantity that does.

Two live methods questions travel in the same sentence as the range. **RBT-44** is open against the tooling
that produced it: newborn-only pairing under `--survival`, and a founder null that covers survival plus
lexicase. Its specific defect does not reach the ecology's pairing, which keeps one record per individual; what
does remain is that a parent's yield enters as its final lifetime mean and parent and child overlap in the seasons
they are alive, so shared season-to-season variance could inflate the correlation. The paired controls carry the
same overlap and read near zero on the holistic side, and RBT-82 measured the shared-season share of yield
variance in this world at 0.05 to 0.08, where its synthetic sweep shows no inflation; the numbers above are still
best read as upper bounds on additive heritability. And RBT-19 showed the number is not a constant of the fauna but a property of the world — patch
structure sharpened the two-nose gradient to twice the baseline's and simultaneously cut heritability from 0.51
to 0.246, because patch luck is within-season variance that selection has to see through. Structure that helps
a sensor can hurt the search.

---

## 5. What the economy bought, and what it did not

**The peak forager.** In RBT-19's persistent world — patches, depletion, slow regrowth at a spot, food state
carried across seasons — the season-590 holistic best eats **5.75 items alone on 4.2 kJ**, against the
baseline's best lumps at 2.1 to 2.5 and the Pioneer's 1.0 to 1.6 on 17 to 21 kJ. It is the strongest forager
the series has produced and it carries no food sensor at all. It is also **one individual, from one arm, on one
seed**, reported here as an existence proof and not as a rate.

**Cheapness is a coefficient, not a result.** Under the work cost the evolved mowers get steadily cheaper. With
moving free they do not: 801's and 802's free-arm bests spend about 2 kJ, but 803's spend **12 to 16 kJ at
seasons 100, 300 and 590**, four to eight times its own work-cost bests. With work free nothing selects for
economy, so the cheap free-arm mowers were drift (RBT-10). The work cost is what buys efficiency, and any
sentence about cheapness that does not name the coefficient is wrong.

Which findings survive the coefficient: **the overtake and the bottleneck do** — nothing differs between the
work-cost arms within a seed on either. **Cheapness does not.**

**The out-eating claim fails in a crowd.** With eight robots sharing an arena (RBT-17) the wheeled bests
out-eat the holistic bests both alone and in groups: 2.12 against 0.88 alone, and 2.34 against 1.14 per robot
in eights, at season 590. The claim in §1 holds at the four-robot baseline and reverses at eight. State the
boundary wherever the claim is made.

**The result is stated at a density, not in general.** At 3 items in a 3 m disc the holistic population dies
out in both work-cost arms, while the wheeled population goes extinct under the work cost and never dips with
moving free — so the sparse wheeled extinction was the coefficient and the sparse holistic one was not. At 6
items the holistic side starves out by season 15 and the wheeled side bottlenecks, breeds, holds at five to
nine for twenty seasons and dies at 51 of demographic stochasticity rather than starvation. At 12 blind grazing
is comfortable. Random lumps bootstrap somewhere between six and twelve items, and every arm run below that line
measured the bootstrap threshold and nothing else. Paper 6 closes the axis: a random lump's yield barely moves
over a factor of eight in density, because a random lump does not move, so the band where a blind grazer fails
and random founders can still bootstrap is empty.

---

## 6. It is blind: the prize is real, drift rarely proposes it and does not hold it, and whether selection keeps one it is handed is undecided

The forager is a mower. The eater lineage on 801 carries no food sensor; blanking every sensor, or silencing
every local brain, changes neither its path nor what it eats. Ten world arms varied smell range and legibility,
density, depletion, patch structure, crowding, season length and the work cost, each asking whether the variant
gave sensing a slope. Five died at the bootstrap line and five produced blind mowers; none produced a compass
on either side (`docs/foraging-world.md`, fan-out table). The strongest
piece of evidence for the blindness is now positive rather than absent: at 64 paired seeds a season-390 mower
that carries a nose it never reads is **bit-identical on 64 of 64 bouts** (RBT-38).

**The earlier explanation — that perception was not on the same hill — is false, and this paper must not
repeat it.** Two corrections killed it. The Pioneer's drive wheels hinge about their own outward normals, axis
dot product −1.0000, so the **effector sum** is the steering axis; every earlier reading of its wheel noses had
the sign convention wrong (RBT-64, RBT-62). Corrected, a four-link antisymmetric motif hand-installed on 7
Pioneers over 64 paired seeds earns **+0.897 items on a 1.516 baseline, +59%, on 7 of 7 robots** (RBT-61 as
corrected, tested in RBT-62) — on the population it was measured on, and the sign is population-specific,
because the motif's chemotactic sign depends on the lineage's direction of travel, which foraging selection
leaves free; on a population that drives the other way the same motif is negative (RBT-69). The hill was there
and it was steep. **And +59% is a floor, not the prize.** The ladder was extended to a = 384 on two populations,
each with the sign its own direction of travel requires: on the W4b-801 bests the gain is at least **+1.875
items (+148%)** and still rising at the top rung; on P-801's five forward-driving bests at least **+8.094
(+301%)**; the two P-801 bests that drive backward lose at every rung, as pre-registered from their measured
direction (RBT-67). No turnover was found inside the range. The mechanism is established by the manipulation
check and not by the item rate: at a = 384 a phantom-smell control, sensors fed a decoy layout with the real
items untouched, collapses the whole gain to −0.217 at the same pinned-effector fraction and the same actuator
work, while aim to the smell ascent and distance to the item centroid improve monotonically with gain (RBT-67).
Items per in-disc metre rising on a flat path is consistent with that and does not establish it on its own,
because path shape alone moves that rate by 2.07× at pinned length (RBT-39).

What was missing is the search's reach. The motif pays at per-link weights of 16 to 32. Across 180 evolved
robots and **19,892 link weights** at search depths 23, 39 and 78, the maximum weight anywhere is 4.65, 5.52
and 6.11 — **not one weight reaches 8**, where the installed compass is still null (RBT-62). Those are
weight-space figures, and the gap they describe should be quoted in those units: in realised small-signal
steering gain the best evolved individual is about ten times short of the paying magnitude and the median
population member has none at all (RBT-78's adversary round, RBT-81). Two earlier ways of putting a number on
the shortfall are withdrawn from this paper. Any path-sum "realised gain" at depth four or deeper is not a
quantity: the linearised series diverges on every committed brain (spectral radius 1.57 to 4.92), its value is
set by where the counting stopped, and it tracks the network's actual response at best in sign (RBT-78,
RBT-81). And no depth-1 steering figure is quoted here about an installed compass, because the only compass
motif this encoding can represent is routed through a global interneuron and its depth-1 term is zero by
construction (RBT-87). The mutation operator has a stationary weight scale of about 3: nothing bounds a weight,
but the redraw truncates the walk at σ(d) ≈ √(1 + 0.0392·d), which puts the typical link at 16 only around
depth 6,500. The deepest arm ever run reached 78 (RBT-62).

**Rarely reached is not never reached, and reaching is not keeping.** How rarely is now measured on one
denominator (RBT-78). The direct four-link motif never arrives under drift: 0 of 10,000 nineteen-mutation
lineages, maximum |a| 3.3, consistent with RBT-62's arithmetic. The 0.70% of lineages once quoted from a path
measure is a depth-4 truncation of that divergent series, carried entirely by indirect routes through the
recurrent global brain, roughly ten times larger one link deeper; under strict link-count matching an
information-free sensor pair clears it at the same rate at the magnitude that pays, and the "gradient-dominant"
filter that was meant to separate a compass from a pirouette is a sign test with no magnitude content. The
rate that could mean a compass, correct sign and magnitude together, is about one lineage in a thousand at
a ≥ 32; weighted by what the pirouette term costs, about one lineage in five thousand on one population and
none on the other would earn anything. And what drift proposes it also loses: in 1 of 16 forty-mutation chains
the motif crossed |a| ≥ 16, and the chain that went highest peaked at 26.5 and ended at 6.1 (RBT-77). So the
operator's limitation is *rarely reaches and does not retain*, not *cannot reach*.

**Handed a compass, does selection keep it? Undecided at three seeds.** Sixty founders seeded with the routed
motif, 300 seasons against a paired unseeded control and an economy-flattened drift arm, on three evolution
seeds, with the whole living population read every season rather than the score-selected champion (RBT-80,
replacing RBT-65's champion-only sighting; RBT-79). By the pre-registered rule the result is **NO VERDICT**:
the seeded-minus-drift carriage contrast at the plateau is +0.253, −0.030 and +0.286, so HELD is unreachable
on the sign clause and NOT HELD carries one seed of three, and the answer does not move when the carrier
predicate is swapped between the two truncation depths that can read a routed motif. Two things the same runs
do establish. **The unseeded control never evolves a compass**: 0.000 carriage under three predicates, three
seeds, about 1,300 distinct genotypes, measured over living populations, which is this programme's cleanest
null. And the seeded arm out-earns its control at arm level on all three seeds (+0.43, +0.37, +0.37 items a
season), with carriers out-earning non-carriers inside the seeded arm on all three; but both readings are
observational, the dose-response across seeds is flat, and the discriminating control (a seeded arm wired to a
food-irrelevant sensor) has not been run, so **"the compass pays" is not cited here as a mechanism.** The
post-hoc readings all lean the same way (loss of the motif by sign inversion is six to eight times higher
without selection, in every seed) and none of them is pre-registered; one seeded arm lost the motif outright at
the plateau and nobody has an account of it.

So the honest sentence is: **an economy with no fitness function built locomotion and metabolism and did not
build perception, because a compass that pays and keeps paying arrives by drift in about one lineage in a
thousand at the magnitude where it begins to pay, far fewer once the pirouette term is charged for, and is not
retained; and whether selection holds one it is handed is undecided at three seeds.** The topology is not the obstacle; it
turns up in 7 to 17% of a wheeled population. The obstacle is sign structure and magnitude, and a single wired
nose forces the compass and the pirouette terms to equal strength, with the pirouette the more strongly
measured of the two at −1.502 (RBT-62).

**How much of §6 is settled.** More than when this section was first written, and less than it reads. RBT-62
stated four limits on its own result. Three have moved. The payoff curve is no longer seven robots from one run
unbounded above: it is measured to a = 384 on two populations with their own signs, still rising, and its
mechanism is confirmed by the phantom-smell control at the top rung on one of them (RBT-67). The path-based
counts are not an upper bound; they are retired, because the series they truncate diverges, and the instrument
now reports the depth-1 term, a balance ratio, the sign and the spectral radius (RBT-78, RBT-81). Co-adaptation
has been run on three seeds and is undecided (RBT-80). The fourth limit stands unchanged: every one of these
numbers is Pioneer-only, because no holistic population carries a food nose on both wheels at any depth, and
for an arbitrary evolved body the steering axis is not the effector sum. The discrepancy this section used to
carry, 10⁻⁷⁷ against 0.70%, is resolved: the two counted different routes, the direct figure is the only
well-defined one of the two, and the path figure is a truncation depth's artefact (RBT-78). What remains open,
and is stated as open: whether a correctly signed compass is still chemotaxis at gains above the one checked
(a = 384 checked on W4b-801 only); whether the encoding admits any motif whose payoff is worth its pirouette
term without a hand-installed magnitude; and what selection does with a compass over more seeds than three.
Section 6 is the best current reading, not a closed result, and paper 7 (RBT-70) is about what happens when a
reading is treated as more settled than it is.

**Two standing cautions on every nose verdict quoted anywhere in this family.** A nose effect read off eight
seeds is not a result until it is re-read at 32 to 64: RBT-38's paired re-read killed ten of fifteen such
claims and left five. And the blind-mow floor of twice the eat radius times the density is not a null at all:
RBT-39 has now replayed ten standing champions' own recorded paths against layouts their worlds could equally
have dealt them, and the honest expectation lands between 0.70× and 1.67× that floor — body width raises it
(×1.54 to ×2.87), circling and retracing lower it by more (×0.39 to ×1.08). So a rate above the floor proves
nothing *and* a rate below it is not damning, which was the half this paper's earlier wording had treated as
safe. Measured against their own gaits, **no champion in the family — the strongest nose effect in it included
— collects food faster than its gait meets by accident.** The brake verdicts are untouched, resting as they do
on time inside the disc; the items-per-metre leg of every verdict should be struck (RBT-39, `runs/RBT-39/REPORT.md`).

---

## 7. What this paper claims, and what it does not

It claims exactly what an economy without a scoring function produced:

- locomotion, then cheaper locomotion under a work cost, from survival alone, in about twenty generations;
- a founder bottleneck that is selection and not drift, against a neutral control;
- a sustained lead in energy gain over a designed body at the four-robot baseline density;
- a heritable measure of lifetime performance where the competitive score in the same family carried none.

It does not claim intelligence, perception, situatedness or open-endedness. It does not claim the result is
general over density, over crowding, or over the work-cost coefficient; §5 gives the boundary for each. It does
not claim the world cannot reward sensing — §6 says the opposite, on measurement. It does claim the result
reproduces on fresh seeds, and says how much smaller it is when it does: three pre-registered seeds, three
clauses, met on all three (RBT-71, Deliverable A), with the lead, the heritability and the end-of-run gain each
below the founding seed's on every fresh seed. Six seeds of one configuration, at one density, one economy and
one lifespan, is what exists.

The most reframing thing the programme learned while this paper was being scoped is that its ten null arms are
not ten independent pieces of evidence that the world cannot reward sensing. They are one piece of evidence,
repeated ten times, that twenty generations is not enough search (RBT-59). That belongs in this paper because
it changes what the positive result means too: everything in §2 to §5 was bought with the same twenty
generations.

---

## Sources

Every number above traces to one of these. None was recomputed for this paper.

| Claim | Source |
|---|---|
| Path series, first forty seasons, the season-100 best, seed 801 | `docs/foraging-world.md` |
| Five-seed replication: minima, gains, crossover seasons, founders, heritability, free-arm cheapness | RBT-10, branch `claude/determined-shannon-2zb8jp`, `runs/RBT-10/` |
| Neutral control, drift baseline, toolkit reproducibility | `docs/foraging-world.md` (RBT-7) |
| Density series, bootstrap threshold, spent density axis | `docs/foraging-world.md`; `docs/paper-6-the-cow-is-the-correct-answer.md` |
| Crowded arena reversal (2.12 / 0.88 alone, 2.34 / 1.14 in eights) | RBT-17 |
| Persistent world, peak forager 5.75 items on 4.2 kJ, heritability 0.246 | RBT-19, `runs/RBT-19/REPORT.md`, `docs/persistent-world.md` |
| Long-range smell arm, heritability 0.56 | RBT-22 |
| Search depth 18–24, 30 seasons per reproduction, slot-limited births, +0.43 SD selection differential | RBT-59, `runs/RBT-59/REPORT.md` |
| Steering axis is the effector sum | RBT-64, RBT-62 |
| Compass prize +0.897 items on 1.516, 7/7 robots, 64 paired seeds | RBT-61 as corrected, tested in RBT-62 |
| Weight-scale gap: 19,892 links, max 4.65–6.11, none ≥ 8; σ(d) law (weight-space figures) | RBT-62, `runs/compass-gain/REPORT.md` |
| Compass ladder to a = 384: +1.875 on W4b-801, +8.094 on P-801's forward drivers, no turnover; phantom control at 384 collapses the gain | RBT-67, `runs/RBT-67/REPORT.md` |
| Arrival rates on one denominator: direct motif 0 of 10,000; the 0.70% path figure a depth-4 truncation of a divergent series, cleared by an information-free pair under matched wiring; about 1 in 1,000 gradient-correct at a ≥ 32, 1 in 5,000 or none payoff-weighted | RBT-78, `runs/RBT-78/REPORT.md` and adversary readouts |
| Realised-gain shortfall (best ~10× short, median absent); path term retired; depth-1 term, balance, sign, spectral radius reported | RBT-81 |
| Depth-1 term is zero by construction on the routed motif the encoding permits | RBT-87 (open) |
| Items per in-disc metre moves 2.07× with path shape at pinned length | RBT-39, `runs/RBT-39/shape_at_constant_length.txt` |
| Drift reaches a paying gain in 1 of 16 chains and loses it (peak 26.5, end 6.1) | RBT-77 |
| The compass's sign is population-specific | RBT-69 |
| Seeded compass, one seed, champion-only: control never evolves one; retention unmeasurable from champions | RBT-65, RBT-79 |
| Seeded compass over living populations, three seeds: NO VERDICT (plateau +0.253 / −0.030 / +0.286); control 0.000 carriage over ~1,300 genotypes; arm-level yield +0.43 / +0.37 / +0.37, observational | RBT-80, `runs/RBT-80/` |
| 64-paired-seed re-read, ten of fifteen nose claims dead, nose never read bit-identical 64/64 | RBT-38 |
| Blind-mow floor is a point-robot rate, and bounds the null in neither direction | RBT-39 (`runs/RBT-39/REPORT.md`) |
| Heritability tooling caveats | RBT-44 (open) |
| Instrument-failure methodology | paper 7, RBT-70 (filed for review) |
| Fresh-seed reproduction on 804/805/806: crossover, lead fractions, heritability, paired controls, founders, depth | RBT-71 Deliverable A, `runs/RBT-71/REPORT.md`; every scorecard quantity re-derives from the checkout via `runs/RBT-71/measure.py` |
| Neutral-control heritability near zero; the 801 control figure unverified; shared-season share 0.05–0.08 | RBT-82, `runs/RBT-82/` |
| External literature in §0 | the list below; each entry checked against the paper's own abstract or record on 2026-09-14 |

### External sources

Each of these was checked against its own abstract or an indexed record on 2026-09-14 before it was cited, and
none is cited from memory. The method was not uniform, and the exceptions are named: the MIT Press page for
Utimula (2025) returned HTTP 403 and the entry was confirmed through its PubMed, IEEE Xplore and dblp records;
the Springer page for Chaumont & Adami (2016) redirected to a login and the entry was confirmed through the arXiv
preprint's abstract (1112.5116); and the author's own publications page for Miconi returned 403, so the
Evosphere entries were confirmed through their IEEE Xplore, Springer and ResearchGate records rather than the
texts. One further publisher page (ScienceDirect, for an *Ecological Complexity* 2015 paper) returned 403 and that
paper is not cited.

- Adami, C. & Brown, C. T. (1994). Evolutionary learning in the 2D artificial life system "Avida". *Artificial Life IV*, MIT Press, 377–381.
- Channon, A. (2001). Passing the ALife test: activity statistics classify evolution in Geb as unbounded. *ECAL 2001*, LNCS 2159, Springer. doi:10.1007/3-540-44811-X_45
- Chaumont, N. & Adami, C. (2016). Evolution of sustained foraging in three-dimensional environments with physics. *Genetic Programming and Evolvable Machines*. doi:10.1007/s10710-016-9270-z (arXiv:1112.5116)
- Cheney, N., Bongard, J., SunSpiral, V. & Lipson, H. (2016). On the difficulty of co-optimizing morphology and control in evolved virtual creatures. *Proc. ALIFE 2016*, MIT Press, 226–233.
- Cheney, N., Bongard, J., SunSpiral, V. & Lipson, H. (2018). Scalable co-optimization of morphology and control in embodied machines. *J. R. Soc. Interface* 15(143): 20170937. doi:10.1098/rsif.2017.0937
- Mertan, A. & Cheney, N. (2025). Evolutionary brain-body co-optimization consistently fails to select for morphological potential. *Artificial Life*, accepted; extended from ALIFE 2025. arXiv:2508.17464
- Miconi, T. & Channon, A. (2006). An improved system for artificial creatures evolution. *Proc. ALIFE X*, MIT Press.
- Miconi, T. (2008). Evosphere: evolutionary dynamics in a population of fighting virtual creatures. *Proc. IEEE Congress on Evolutionary Computation 2008*.
- Miconi, T. (2011). The evolution of foraging in an open-ended simulation environment. *EPIA 2011*, LNCS, Springer. doi:10.1007/978-3-642-24769-9_10
- Ofria, C. & Wilke, C. O. (2004). Avida: a software platform for research in computational evolutionary biology. *Artificial Life* 10(2): 191–229. doi:10.1162/106454604773563612
- Ray, T. S. (1991). An approach to the synthesis of life. In Langton, Taylor, Farmer & Rasmussen (eds), *Artificial Life II*, Addison-Wesley, 371–408.
- Sims, K. (1994a). Evolving virtual creatures. *SIGGRAPH '94*, ACM, 15–22.
- Sims, K. (1994b). Evolving 3D morphology and behavior by competition. *Artificial Life IV*, MIT Press, 28–39; journal version *Artificial Life* 1(4): 353–372.
- Soros, L. B. & Stanley, K. O. (2014). Identifying necessary conditions for open-ended evolution through the artificial life world of Chromaria. *Proc. ALIFE 14*, MIT Press.
- Spector, L., Klein, J. & Feinstein, M. (2007). Division Blocks and the open-ended evolution of development, form, and behavior. *GECCO 2007*, ACM, 316–323. doi:10.1145/1276958.1277019
- Utimula, K. (2025). Guideless artificial life model for reproduction, development, and interactions. *Artificial Life* 31(1): 31–64.
- Yaeger, L. S. (1994). Computational genetics, physiology, metabolism, neural systems, learning, vision, and behavior or PolyWorld: life in a new context. *Artificial Life III*, Addison-Wesley, 263–298.

Two attributions in the ticket that scoped this paper are corrected above: morphological innovation protection is
the 2018 paper's proposal, not the 2016 paper's diagnosis; and arXiv:2508.17464 is Mertan and Cheney.
