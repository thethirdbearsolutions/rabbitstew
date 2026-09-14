# The Blind Forager

An economy with no fitness function evolved locomotion from survival alone, and the evolved bodies out-ate the designed one.

*Draft of the fifth paper in the series, written under Chaotic RBT-43. It argues the positive result of the
foraging programme, which currently runs as a thread through `docs/foraging-world.md` — a document organised
around the question the world kept answering "no" to. Nothing here is re-run: every number is cited to the run,
report or ticket it came from, and the fan-out is cited rather than recounted. `docs/foraging-world.md` remains
the fan-out's record and keeps the sensing null. Numbering and final title are the project owner's to settle.
Reproduction on fresh seeds and positioning against the open-ended-evolution literature are **not** in this
paper: they are RBT-71.*

---

## 1. The claim

**An ecology with no fitness function, no ranking and no tournament evolved locomotion from survival alone, in
about twenty generations; and at the four-robot baseline density the evolved bodies ended up out-foraging the
designed one on a fraction of its energy, a lead that reverses in a crowded arena (RBT-17).**

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
nobody starving, breeding free and turnover by age alone. It finished with **14 holistic and 16 wheeled
founders of 60** still in the final ancestry and its means unchanged from season 0. The foraging arms finished
with **1 founder on 801 and 3 in every other replicate**. Drift at this capacity over ten lifespans keeps a
quarter of the founders; selection through starvation kept one to three. The control is in the toolkit as
`rabbitstew heritability RUN --drift-baseline NEUTRAL_RUN`, so the comparison is reproducible rather than an
impression (RBT-7).

**The bottleneck reproduces in kind, not in depth.** The season-11 starvation wave is the same size everywhere,
30 to 39 deaths, but the population minimum across the five seeds is **7, 31, 32, 36 and 42**. The widely
quoted 60 → 7 is the extreme of five, not the type, and a thirteen-season re-run of 801 on current code
reproduces it exactly, so the depth is the seed (RBT-10).

---

## 3. The overtake, and how much search bought it

The evolved side overtakes the designed one on mean energy gain and holds the lead in **450 to 566 of 600
seasons** across the replicates, by +0.13 to +0.21 a season over seasons 100 to 599. The crossover season is 83
on 801 and 11 to 30 on the replicates — earlier and smaller than the seed that was written up first. 801's
climb to +1.63 at season 500 does **not** reproduce: the replicates plateau at +1.0 to +1.3 from season 30 on,
and on 803 under the work cost the two sides are at parity by the end (RBT-10).

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
parents' is **0.51 on seed 801 and 0.28 to 0.44 across the other four dense-arm runs** on the holistic side,
0.14 to 0.39 on the wheeled side, and 0.246 to 0.56 across the wider fan-out — 0.56 in the long-range-smell arm
(RBT-22), 0.246 in the persistent world (RBT-19), which is the lowest in the family and failed its own
pre-registered floor of 0.4. **Against zero for any bout outcome anywhere in this series.** The 0.51 is the top
of a range and not the number.

This is the result I would put first in a positioning paper. The competitive score this project spent three
papers on carried no information from parent to child; a survival economy with no score at all produced a
quantity that does. That contrast belongs to RBT-71 to place against the literature.

Two live methods questions travel in the same sentence as the range. **RBT-44** is open against the tooling
that produced it: newborn-only pairing under `--survival`, and a founder null that covers survival plus
lexicase. And RBT-19 showed the number is not a constant of the fauna but a property of the world — patch
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

## 6. It is blind, and the reason is not that perception did not pay

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
and it was steep.

What was missing is the search's reach. The motif pays at per-link weights of 16 to 32. Across 180 evolved
robots and **19,892 link weights** at search depths 23, 39 and 78, the maximum weight anywhere is 4.65, 5.52
and 6.11 — **not one weight reaches 8**, where the installed compass is still null. On the direct nose-to-effector
route the best gradient-dominant individual in the whole corpus carries a gain of 0.548 against the 32 needed
for a quarter of an item. (RBT-81: "gradient-dominant" is the sign test `s₁·s₂ < 0`, not a magnitude
filter, and any depth-4 path figure is a truncation of a divergent series; the instrument now reports
the depth-1 term, a balance ratio and the sign separately. The 0.548 is a depth-1 figure and stands.) The mutation operator has a stationary weight scale of about 3: nothing bounds a
weight, but the redraw truncates the walk at σ(d) ≈ √(1 + 0.0392·d), which puts the typical link at 16 only
around depth 6,500. The deepest arm ever run reached 78 (RBT-62).

**Rarely reached is not never reached, and reaching is not keeping.** Drift does occasionally deliver a paying
gain and then loses it again: in 1 of 16 forty-mutation chains the motif crossed |a| ≥ 16, and the chain that
went highest peaked at 26.5 and ended at 6.1 (RBT-77). So the operator's limitation is better stated as
*rarely reaches and does not retain* than as *cannot reach*.

**Handed a compass, does selection keep it?** The experiment has been run and answers half the question.
Seeding 60 founders with the motif and running 300 seasons against a paired control shows the compass **pays
in the ecology**, +0.337 items a season, and that the unseeded control **never evolves one**, median gain
0.000 with 0 of 30 champion snapshots reaching threshold (RBT-65). Whether a seeded population *retains* it is
not answerable from that run: the only witness recorded was the best-of-season champion, which is selected on
foraging score and therefore over-represents carriers — the seeded and the economy-flattened drift arm both
report near-total retention, 29/30 and 30/30, where pure mutation over the same depth should leave about 58%
(RBT-79). The rerun that can answer it reads the whole living population season by season, which the telemetry
added under RBT-27 makes possible, and is RBT-80. **This paper should not claim a retention result until it
lands.**

So the honest sentence is: **an economy with no fitness function built locomotion and metabolism and did not
build perception — not because perception did not pay, but because the operator's weight scale rarely reaches
the magnitude at which it pays and does not retain it when it does.** The topology is not the obstacle; it
turns up in 7 to 17% of a wheeled population. The obstacle is sign structure and magnitude, and a single wired
nose forces the compass and the pirouette terms to equal strength, with the pirouette the more strongly
measured of the two at −1.502 (RBT-62).

**How much of §6 is settled.** Less than the paragraphs above read. RBT-62 has been accepted, but it carries
four limits its own author states and they still hold: the payoff curve is 7 robots from one run on solo bouts and unbounded above,
since a = 64 topped every sweep; the path-based counts linearise tanh and are an upper bound; co-adaptation is
untested on both sides, since one study bolted a circuit onto a finished controller and the other measured
finished controllers; and it is Pioneer-only, because no holistic population carries a food nose on both wheels
at any depth. There is also an **unresolved discrepancy**: RBT-62's direct-route arithmetic gives order 10⁻⁷⁷
for the motif arriving by drift, where RBT-45's corrected calibration gives 0.70% of realistic lineages at
a ≥ 32 and 0.05% at a ≥ 64 by a path measure that allows indirect routes. Neither party thinks the other is
simply wrong; putting the two on one denominator is RBT-78.
Section 6 is the best current reading, not a closed result. The programme has just spent a paper (paper 7,
RBT-70, filed for review) on what happens when a reading is treated as more settled than it is.

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
not claim the world cannot reward sensing — §6 says the opposite, on measurement. And it does not claim the
result reproduces on fresh seeds: five seeds of one configuration is what exists, the reproduction is
pre-registered under RBT-71, and the project owner's stated position is that they are not convinced it is
reproducible.

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
| Search depth 18–24, 30 seasons per reproduction, slot-limited births, +0.43 SD selection differential | RBT-59, `runs/RBT-59/REPORT.md` (in review) |
| Steering axis is the effector sum | RBT-64, RBT-62 |
| Compass prize +0.897 items on 1.516, 7/7 robots, 64 paired seeds | RBT-61 as corrected, tested in RBT-62 |
| Weight-scale gap: 19,892 links, max 4.65–6.11, none ≥ 8; σ(d) law | RBT-62, `runs/compass-gain/REPORT.md` (in review) |
| Path-measure arrival rate, 0.70% at a ≥ 32 and 0.05% at a ≥ 64 | RBT-45 as corrected; reconciliation with RBT-62 is RBT-78 |
| Drift reaches a paying gain in 1 of 16 chains and loses it (peak 26.5, end 6.1) | RBT-77 |
| The compass's sign is population-specific | RBT-69 |
| Seeded compass pays +0.337 items a season; control never evolves one; retention unmeasurable from champions | RBT-65, RBT-79; rerun is RBT-80 |
| 64-paired-seed re-read, ten of fifteen nose claims dead, nose never read bit-identical 64/64 | RBT-38 |
| Blind-mow floor is a point-robot rate, and bounds the null in neither direction | RBT-39 (`runs/RBT-39/REPORT.md`) |
| Heritability tooling caveats | RBT-44 (open) |
| Instrument-failure methodology | paper 7, RBT-70 (filed for review) |
