# Five Instruments, Five Wrong Readings

*Seventh paper in the Rabbitstew series, and the first about the programme rather than
about robots. **Draft. Nothing in it has been reviewed.** It reports seven occasions on
which this project measured something with a broken instrument, believed the reading, and
built on it — two in the arena experiment (2026-09-11) and five in the foraging ecology
over a single eighteen-hour period (2026-09-12/13). Sources: `docs/followup-paper.md` §4.1–4.2,
Chaotic RBT-38, RBT-58, RBT-59, RBT-60, RBT-62, RBT-63, RBT-64, and the two lead-researcher
documents in the RBT doc store. Numbers are cited to the arm that produced them; where an
arm's own author has since retracted a claim, the retraction is cited rather than the claim.*

---

## Abstract

An evolutionary-robotics programme ran two experiments over six papers and roughly a dozen
world variants, and concluded that its evolved population would not evolve chemotaxis
because no world it could build both rewarded a nose and sustained a population. That
conclusion was wrong, and it was wrong for a reason with no biological content: the fixed
body's two drive wheels hinge about antiparallel axes, so the **sum** of its two effector
commands steers it and the **difference** drives it — the transpose of the differential
drive every controller author and every structural statistic assumed. Corrected, a
hand-installed four-link chemotaxis circuit earns **+0.897 items against a 1.516 baseline
(+59%, 7/7 robots)**. The world rewarded chemotaxis richly and had done so throughout.

Reviewing the programme for other instances, we find seven. In each, a quantity was
measured with a device that could not see the thing the question turned on, the reading was
believed, and subsequent work was denominated in it. The failures are not independent: five
of the seven share a single structure, which we name and characterise. We report what
caught them, and — more usefully — what did not. Four independent layers of internal
verification (a held-out test, multiple-comparison discipline, a 64-seed paired design, and
bootstrapping over the right unit) all passed, in agreement, on a circuit that could not
work. What broke the error was an outside appeal to physics: *Braitenberg vehicles
demonstrably work, so if a hand-installed one earns nothing, suspect the apparatus.*

We argue that this programme is a useful specimen for a question the autonomous-research
literature has posed but not yet studied longitudinally: what happens to a research
programme whose verification is performed by the same kind of agent that produced the
claim. Every incident here is timestamped, most were pre-registered, and four of five
retracted predictions are visible *only* because a verdict rule was fixed before the
numbers were computed.

---

## 1. What this paper is not

It is not a defence. Six papers in this series contain claims that the seventh deletes, and
two of the retractions are of the retracting author's own work from hours earlier. It is
also not a confession dressed as method: the incidents below were caught, mostly quickly,
mostly by the programme's own discipline, and the cost — roughly ten world-variant arms —
is recoverable. What makes them worth a paper is that they form a **class**, that the class
is invisible to the checks the field ordinarily prescribes, and that the conditions which
produced them are now common.

---

## 2. The programme, in one page

Rabbitstew implements a 2005 proposal for a variable-morphology robot simulator: genotypes
are directed graphs of segments, each carrying a local neural brain, expanded breadth-first
into a MuJoCo body. It was built to run one experiment — evolve one population's bodies and
brains together from random morphologies, evolve a second population's controller inside a
fixed differential-drive body, and race them. Two later strands grew out of it: a
designed-quadruped comparison, and a **foraging ecology** with no fitness function at all,
in which robots eat, pay a basal and a per-kilojoule work cost, breed above an energy
threshold and die of age or starvation.

The ecology's animating question became: *will sensing evolve?* Across five seeds, two work
costs and roughly ten world variants at 600 seasons each, the answer was always the same
blind grazer. The sixth paper argued the grazer was not a search failure but the correct
optimum of every world we had built.

Every incident below bears on that argument.

---

## 3. The seven incidents

| # | Instrument | What it could not see | What it cost |
|---|---|---|---|
| A1 | the competitive bout score, with free mass | that the score rewards mass regardless of control | one near-parity result |
| A2 | the same score, with a bounding-sphere spawn lift | that potential energy at spawn is a motor | a 250-generation matrix, 4 conditions |
| E1 | unpaired standard errors on paired lesion runs | that the modes shared a seed list | **10 of 15** standing nose claims |
| E2 | a compass criterion, fixed in advance, met | that both its conditions clear on mobility alone | one false compass, nearly published |
| E3 | "seasons" as the unit of search effort | that 600 seasons is ~20 reproductions | the denomination of every economy arm |
| E4 | `sensor_influence`: absolute weights, clipped at 3.0 | sign structure, and any magnitude shortfall | one reversed conclusion |
| E5 | the fixed body's hinge convention, documented nowhere | that the effector **sum** steers | ten world arms; four agents |

### 3.1 A1 — the score was a scale

In the arena experiment's first replication, one 50-generation seed crossed parity at
generation 18. Investigated: holistic champions weighed 30–90 kg against the fixed body's
15.34 kg. Across 50 replayed best-versus-best bouts, holistic fitness correlated **0.41
with mass** and **0.04 with the number of connected neural units or driven effectors**. One
champion **with no driven effector at all** won its bout. Under an equal-mass control the
result fell from 0.31 to 0.21 by thirds, 113 wins of 936.

The instrument was a shoving contest reported as a measure of control.

### 3.2 A2 — the score was an altimeter

Robots were placed for a bout by lifting each until no part's bounding sphere was below
ground: a centimetre for a wheeled box, tens of centimetres for a large branching evolved
body. When the clock started, the body dropped, and evolution found the shape that topples
goalward. The final flat-ground champion of one seed is a **13.5 kg sphere with a small box
welded to its side, no motor, no actuator work, that rolls 1.84 m toward the goal from the
drop alone.**

This voided a published matrix: a flat-ground parity band, 1218 of 1836 holistic wins on a
raised plateau with **180 recorded climbs**, and 1744 of 1836 on rails with **1085 recorded
crossings**. Re-measured from rest, every holistic champion of that matrix gains between
**−0.25 and −0.07 m** toward a goal, crosses no test terrain, and steers to no goal.

A1 and A2 are the [Lehman & Clune (2020)](https://arxiv.org/abs/1803.03453) genre: evolution
exploiting the apparatus. They are included because they establish that this class of error
was already twice-demonstrated in this programme **before** the five that follow, and was
still not defended against.

### 3.3 E1 — the wrong error term, and the wrong summary

Every lesion probe in the foraging family ran each mode over the *same* seed list and then
compared means using each mode's own standard error, as if the samples were independent.
Re-read at 64 paired seeds with a sign-flip permutation test, **five of fifteen standing
nose-dependence claims survive and ten die.**

Two findings inside that are worth more than the count. First, the eight-seed readings were
**biased, not merely noisy**: every effect that moved, moved the same direction — 88%→83%,
58%→35%, 74%→35%, 57%→29%, 28%→−13%, 27%→**+2%**. Not one got larger. That is the signature
of selecting a champion on a small probe and then reporting that same probe.

Second, the mean was the wrong summary regardless of its error bar. The claim that motivated
the ticket, a "27% nose effect," decomposes as:

```
per-seed differences: 0 0 0 -1 0 +4 0 0 0 0 0 0 0 -1 +2 0
lesion changed nothing on 12 of 16 seeds
```

A robot unaffected by its nose in three quarters of its bouts, with one lucky outing,
reported as a smooth 27% bias. At 64 paired seeds it reads **+0.031 items, t = +0.14**.

Note what the re-read *cannot* do: it re-analysed existing genotypes, so it can kill claims
and cannot create them. Note also that the ticket's own framing was wrong — pairing was
rarely the binding problem; sample size was.

### 3.4 E2 — the criterion passed and the claim was false

The family's best chemotaxis candidate was read at 256 paired seeds against a criterion
fixed on the issue beforehand: *compass if nearest-item distance falls at |t| ≥ 2.5 and
items per metre rises.* It met it — nearest-item distance **t = −3.60**, interval excluding
zero, items per metre up.

It is not a compass. The arena holds 24 items in a 3 m disc, 0.849 items/m², and a cell of
fresh ground is 0.49 m², so a blind body sweeping new ground should meet **0.416 items** per
cell by chance. **It gets 0.406** — two percent *below* chance. It eats eighteen times more
with its noses on because it **moves**: 7.6 cells against 2.3, on 4.1 m of path against 2.2.
Blanked, it sits in the disc for 99.9% of the season. The noses gate its drive. It is a
throttle.

The criterion's defect, stated so nobody reuses it: **both conditions are satisfiable by
mobility alone.** "Items per metre rises" is read against a point-robot floor that a
barely-moving robot sits an eighth of, so any change making an immobile robot mobile clears
it. "Nearest-item distance falls" is a byproduct of covering fresh ground in a *depleting*
arena. The measured effect, 4.8 cm, is an eighth of the eat radius.

E2 is the most instructive incident in the paper, because the pre-registration worked
perfectly and produced a false positive anyway. **A verdict rule fixed in advance is
protection against choosing the analysis after seeing the data. It is no protection at all
against a rule that measures the wrong thing.**

### 3.5 E3 — the unit of the experiment was never converted

Every design decision in the ecology is denominated in **seasons**. Selection is denominated
in **reproduction events**. Nobody had computed the conversion. Measured across fourteen
population-rows in ten arms as the first-parent chain length from a survivor back to a
founder — exact, because the breeding routine applies exactly one mutation per event —
the median depth is **18 to 24**. Six hundred seasons is **twenty generations.**

Nor does the conversion respond to the thing the arms were varying. Mean energy gain spans a
factor of 2.5 across those rows and **r(gain, depth) = −0.153**. The mechanism:

| check | result |
|---|---|
| births ÷ deaths per season | **1.000 in all fourteen rows**, to three decimals |
| share of the living at or above the birth threshold | median **89%** |
| mean energy of the living, against a threshold of 3.0 | 13.9 to 40.8 |

Births are **slot-limited, not energy-limited**. A slot opens only on a death and deaths are
dominated by old age, so the reproduction rate is pinned to the death rate however rich the
world is. The median individual holds five to thirteen times what it needs to breed and
cannot. **Every economy arm in the fan-out — work cost, density, depletion, patches,
crowding — varied a parameter that does not control the search rate.**

The follow-up is the reason this is in a methodology paper rather than a results one. The
obvious remedy is to buy generations by shortening the lifespan, and it was pre-registered
and run. The derived law held across a fourfold range (`depth ≈ 2 × seasons ÷ max_age`,
predicted within ~10% at four checkpoints):

| `max_age` | 60 | 30 | **15** |
|---|---|---|---|
| realised depth at season 599 | 23 | 39 | **78** |
| heritability of lifetime yield | 0.51 | 0.461 | **0.251** |
| mean energy gain | +1.41 | +1.255 | **+1.094** |
| sensing | absent | absent | **absent** |

**A lifespan is also a sample size.** At `max_age` 15 an individual gets fifteen evaluations
instead of sixty, its lifetime mean yield is a far noisier estimate of its quality, and
parent-offspring correlation halves. 3.4× the search depth bought a *worse* population. The
recommendation was refuted by the arm its own author ran to test it.

### 3.6 E4 — counting wiring and calling it a circuit

`analysis.sensor_influence` sums the **absolute** weights along each path from a sensor to
an effector and clips the result at 3.0. It is in every run's standard analysis output and
has been read, throughout the programme, as evidence about whether a robot has a circuit.

It cannot distinguish a circuit from its opposite, and it cannot see a magnitude shortfall.
Both facts decide the question the programme was asking. On this instrument a survey
concluded that "the structural precondition for a Braitenberg compass is present in 7 to 17
percent of the wheeled population, so the bottleneck is **not** that the circuit is never
proposed." The topology counts were right and replicate. The conclusion was reversed five
hours later by its own author, using a signed, unclipped measure.

### 3.7 E5 — the transposed drive

The fixed body's two drive wheels are each mounted to hinge about **its own outward normal**,
and the two wheels are mirrored. Mirroring the mount mirrors the axis, so the hinge axes are
antiparallel — measured world-frame dot product **−1.0000**:

| open-loop command | rotation | distance in 15 s |
|---|---|---|
| `(+1, +1)` | **1.221 rad/s** | 0.19 m |
| `(+1, −1)` | 0.0005 rad/s | **24.95 m** |

The **sum** steers and the **difference** drives. Every Braitenberg circuit this programme
installed or counted was wired onto the wrong axis. The classic crossed pairing — each
sensor to the *opposite* wheel — is, on this body, **the spinner**: −1.502 items, 0 of 7
robots improved.

Wired onto the correct axis, a four-link antisymmetric motif (both noses to both effectors,
opposite sign between noses, same sign across effectors) puts `2w(n₁ − n₂)` on the steering
axis and exactly zero on the throttle:

| circuit | steering gain *a* | Δ items | 95% CI | robots improved |
|---|---|---|---|---|
| antisymmetric, w=8 | +16 | +0.054 | [−0.040, +0.158] | 3/7 |
| antisymmetric, w=16 | +32 | +0.246 | [+0.147, +0.353] | 7/7 |
| **antisymmetric, w=32** | **+64** | **+0.897** | **[+0.632, +1.176]** | **7/7** |
| the crossed pair, w=32 | ~0 | −1.502 | [−1.614, −1.375] | 0/7 |

Against a 1.516-item baseline that is **+59%**. A yoked phantom-food control (decorrelated
items, same generator and disc, drive amplitude matched to 94%) earns +0.163, so the
taxis-specific gain is **+0.723, +48%**, and since the phantom still shares r = 0.45 with
the real drive through the disc's radial structure, that is a lower bound.

**The world rewarded chemotaxis richly, and ten world-variant arms were spent failing to
establish it.** The library already knew the convention: a hand-written straight-line
controller hardcodes `(+1, −1)` with the comment *"the right wheel needs the opposite
sign."* That knowledge lives inside one function and is surfaced nowhere at the
brain/genotype interface, in synthesis, or in any analysis tool. During the audit, **three
separate agents independently wrote "corrected" compasses that still routed the common mode
onto the throttle, after being told the axis convention was under suspicion.** The physics
is fine. The defect is that the convention is invisible from where circuits are written.

---

## 4. The class

Five of the seven (E1–E5) share one structure, and it is not "a bug":

> **A quantity is measured by a device that is systematically blind to the property the
> question turns on. The device returns a well-formed number. The number is believed,
> reported with an interval, and used to denominate further work.**

The blindness in each case is a *projection*: the instrument computes a summary that is
many-to-one in exactly the direction that matters.

| incident | the projection that lost the information |
|---|---|
| E1 | pairing collapsed into a marginal SE; a spiky distribution collapsed into a mean |
| E2 | steering and mobility collapsed into "items per metre" |
| E3 | reproduction events collapsed into wall-clock seasons |
| E4 | signed weights collapsed into `abs()`, then clipped at 3.0 |
| E5 | two antiparallel axes collapsed into "two wheels, differential drive" |

Three properties make this class dangerous and distinguish it from ordinary error.

**It is silent.** A broken instrument in this sense does not error, does not produce
outliers, and does not fail a sanity check. It produces a plausible number with a plausible
interval. E5's spike passed a held-out test, a multiple-comparison correction, a 64-seed
paired design and a bootstrap over the correct unit — four sound methods, all applied to the
wrong circuit.

**It is self-confirming.** Because the instrument is used everywhere, results are consistent
with each other. Ten world arms agreeing that sensing does not pay reads as replication. It
was ten measurements with one broken ruler, and their agreement was evidence of nothing but
the ruler's stability.

**It compounds through denomination.** Once "seasons" is the unit, every subsequent design
decision is expressed in it, and the error is inherited by work that never touches the
original measurement. This is why E3 is more expensive than its ticket suggests: it did not
produce a wrong number, it produced a wrong *axis of variation* for a dozen arms.

---

## 5. What caught them, and what did not

### 5.1 What did not

- **Internal replication.** Ten arms agreed. See above.
- **Statistical rigour.** All four layers on E5's spike were correct and irrelevant. Rigour
  operates downstream of the instrument and cannot see past it.
- **Adversarial internal review.** A seven-hypothesis audit ran twenty agents, each claimed
  defect refuted from three angles, and the two load-bearing claims were reproduced from
  scratch by an orchestrator using no audit script, matching to three decimals. It converged
  on the wrong answer, faster and with more confidence.
- **Being told.** Three agents wrote wrong corrections *after* being warned the convention
  was suspect.

### 5.2 What did

**An outside appeal to physics.** E5 was broken by a domain objection that referenced no
data in the programme at all: *Braitenberg vehicles demonstrably work; if a hand-installed
one earns nothing, the prior should be that the apparatus prevents the mechanism, not that
the mechanism is invalid.* This is an **external oracle** — a fact about the world not
derivable from the system's own outputs — and it is the only thing in the record that
reversed a consensus.

**A null with an implausible shape.** E5's spike reported crossed and uncrossed wirings as
behaviourally identical. That was read as a result; it was a symptom, since both arms shared
the same dominant spin term. *Two conditions that should differ and do not* is the
characteristic signature of an instrument collapsing them.

**A physical quantity computed independently of the pipeline.** E2 was killed by one number
— 0.416 items per swept cell, from density × area — that the analysis stack does not
produce. Every instrument in the programme could have been broken and that number would
still be right.

**Pre-registration, but only for a specific job.** Four of five wrong predictions in the
final push are visible *only* because a verdict rule was fixed before the numbers existed:
a selection-strength bound missed (+0.43 SD measured against a predicted <0.3), a
"buy generations" recommendation refuted by its own author's arm, a wiring survey reversed
by its own author, and a gradient-dominance filter predicted at confidence 0.6 to cut a rate
by an order of magnitude that in fact cost a factor of 1.6–3.8. But E2 shows the limit
exactly: pre-registration binds the *analyst*, not the *apparatus*.

### 5.3 The uncomfortable summary

**Four layers of internal verification agreed on a wrong answer, and the check that did the
work was an outside appeal to physics.** Everything in §5.1 scales with compute. Everything
in §5.2 does not.

---

## 6. The agent dimension

This programme was executed by LLM agents working from a shared issue tracker: a coordinator
delegating pre-registered arms, delegates running them and filing reports, one agent acting
as lead researcher for an eighteen-hour stretch. That is why it is a useful specimen.

The [verification-gap survey](https://arxiv.org/html/2608.05179v1) (2026) names the general
condition — agents chaining ideation, execution, analysis and write-up, with mechanical
metric-triggered loops vastly outnumbering externally validated ones, and no LLM-era system
in its corpus demonstrating a genuine external oracle. It reports the survey's own method as
**retrospective audit of published systems, not prospective longitudinal tracking**. The
adjacent literature names "correct answer, wrong mechanism": agents defending observables
with physics contradicted by their own simulation data.

E5 is that failure, in a form rare enough to be worth having on the record. The sixth paper
did not merely record blind mowers; it constructed a **sophisticated, internally consistent,
and completely wrong theory** of why they were correct — the food is dense, immobile,
uniformly scattered and instantly renewed, so a nose is a cost and evolution correctly
declined to pay for it. That theory is well argued. It is contradicted by the simulator's
own joint axes.

Three observations, offered as hypotheses about agent-run programmes rather than as findings:

1. **Agents are strong at the checks that scale and weak at the check that matters.**
   Twenty adversarial agents is cheap; the objection that reversed the result was a domain
   prior, arrived from outside, and cost one sentence.
2. **Explanatory fluency is a hazard specific to this setting.** A capable agent asked why a
   null occurred will produce a good reason. Paper 6's argument is the best writing in the
   series and defends an artefact. There is no analogous pressure toward "my ruler is bent."
3. **Honest retraction is achievable and is the most valuable artifact produced.** The +59%
   figure exists *only* because the author of the failed spike withdrew it themselves the
   same night and explained why. Two of the retractions here reverse the retracting author's
   own work from hours earlier. Whatever produced that behaviour — the pre-registration
   habit, the requirement to state a falsifier, the convention of leaving superseded notes
   in the repository beside their corrections rather than editing them away — is worth more
   than any of the results it corrected.

---

## 7. Related work

**Evolution exploiting the apparatus.** [Lehman, Clune et al. (2020)](https://arxiv.org/abs/1803.03453)
catalogue digital evolution subverting objectives and exposing bugs. A1 and A2 are entries
in that genre. E1–E5 are its complement and, as far as we can determine, are not catalogued:
the bug is in the **measuring instrument**, not in the world, so evolution does nothing
unusual and the experimenter simply reads the wrong quantity. Nothing surprising happens,
which is precisely why it survives.

**Reproducibility in evolutionary computation.** The field's standards work targets
artifacts and re-execution — code, seeds, traces. Every incident here would pass. The
programme's arms are checkpointed, seeded and re-simulable, and E5's ten arms would
reproduce perfectly, to the same wrong conclusion. **Reproducibility and instrument validity
are orthogonal**, and only the first is currently audited.

**Body-brain co-optimisation.** [Cheney, Bongard, SunSpiral & Lipson (2016)](https://direct.mit.edu/isal/proceedings/alif2016/28/226/99427)
give the canonical account of why co-optimising morphology and control underperforms, and
propose morphological innovation protection.
[Evolutionary Brain-Body Co-Optimization Consistently Fails to Select for Morphological
Potential](https://arxiv.org/pdf/2508.17464) (2025) exhaustively maps a morphology-fitness
landscape over 1,305,840 designs and finds co-optimisation reaches pairs that fixed-morphology
optimisation cannot, while the search discards them. Both bear on this programme's arena
result, and both are load-bearing context for §3.1–3.2: those incidents are why our own
apparent exceptions to the literature dissolved.

**Autonomous research agents.** See §6.

---

## 8. Recommendations

Ordered by cost-effectiveness as measured on this programme.

1. **Assert the convention in code, at the site where it is invisible.** The whole of E5
   would have been prevented by one test asserting the two wheel hinge axes are antiparallel,
   plus a named accessor for the steering and throttle channels at the brain/effector
   interface. Roughly an hour, against a demonstrated cost of ten arms, one voided
   experiment, one misdirected structural statistic, one withdrawn ticket and three agents
   writing wrong corrections. **Instrument fixes should outrank new science whenever the
   instrument has a demonstrated incident history.**
2. **Compute at least one key quantity outside the pipeline.** The density-times-area null
   that killed E2 took a line of arithmetic and is immune to every other instrument in the
   system. Any analysis stack should have at least one number in it that the stack did not
   produce.
3. **Denominate experiments in the unit selection actually uses**, and state the expected
   value before the run. Every arm should declare its expected realised search depth, not its
   season count.
4. **Never report a paired comparison as a mean and an interval alone.** Publish the per-seed
   difference list and the count of exactly-zero differences. E1's ten dead claims are all
   visible at a glance in that form and all invisible in the other.
5. **Treat an instrument that collapses a sign or clips a magnitude as broken by
   construction**, and audit every place it has been read. `abs()` and a clip at 3.0 are how
   E4 happened, and that function is in every run's standard output.
6. **Pre-register the verdict rule *and* an argument that the rule can fail.** E2's rule was
   fixed in advance and false. Requiring the author to state how the criterion could be
   cleared *without* the phenomenon would have caught it, since both of its conditions clear
   on mobility alone.
7. **Budget for an external oracle.** In an agent-run programme, the checks that scale are
   the ones that failed. Reserve a human — or any source of domain priors not derivable from
   the system's outputs — for the question "should this result be possible at all?"

---

## 9. Limitations

- **n = 1 programme, and its author is the programme.** This is a self-report by the system
  under study. The incident count is a lower bound: we found seven by looking, and have no
  estimate of how many instruments remain unaudited. `sensor_influence` was in every run's
  output for the programme's whole life before anyone read its source.
- **Nothing here is reviewed.** Six issues sit awaiting review, two of which delete published
  claims, and the pull requests carrying the work have had none.
- **The incident record is itself partly unauditable.** `runs/` is gitignored, so for many of
  the arms cited here the artifacts backing a finding are not in the repository and a
  re-audit can cover only what happens to have been committed (filed as RBT-68, in progress).
  This is arguably an eighth incident of the same class — the record of what was measured is
  a projection of what was measured — and it bears directly on §7's claim that
  reproducibility and instrument validity are orthogonal: here we have neither for part of
  the corpus.
- **The +59% figure carries every caveat of its source**: seven robots from one run, solo
  bouts, and unbounded above — a = 64 topped every sweep, so the prize is a lower bound of
  unknown looseness. It is Pioneer-only; for an arbitrary evolved body the steering axis is
  not the effector sum and the decomposition does not apply.
- **Co-adaptation is untested.** Every compass measured was bolted onto a finished
  controller. Whether a population can *hold* one it grew around is the open experiment, and
  until it runs, "the world rewards chemotaxis" means "a hand-installed circuit is rewarded."
- **The counterfactuals in §5 are not experiments.** We assert that a dot-product assertion
  would have prevented E5 and that pre-registration made four retractions visible. Neither
  was run as a controlled comparison, and both are the kind of claim this paper is otherwise
  warning against.
- **The class in §4 was derived from the same seven cases it describes**, so it is a
  taxonomy, not a prediction. Its test is whether it catches an eighth.

---

## 10. Conclusion

The programme spent roughly ten world-variant arms establishing that its world did not
reward chemotaxis. Its world rewarded chemotaxis by fifty-nine percent throughout, and the
cheapest thing that would have revealed it was an assertion about two dot products.

The generalisable finding is not that we made mistakes. It is that **the mistakes were
invisible to every check that scales with compute, and visible to one that does not.** As
research programmes are increasingly executed by systems that can run twenty adversarial
audits before lunch and can also write a compelling defence of an artefact, the binding
constraint moves from the quantity of verification to whether any of it is anchored outside
the system. Ten arms agreeing is not a replication if they share a ruler.

---

## Reproducing the incidents

Every incident is a file analysis or a re-read of committed genotypes; none requires
re-running a 600-season arm.

```
python runs/RBT-59/depth.py <run>          # E3: realised search depth
python scripts/density_window.py 15        # the density null of paper 6 §5
```

E1's re-read, E2's per-cell null, E4's signed influence measure and E5's axis assertion and
dose-response live on the branches cited in the issues. **Where a branch and this document
disagree, the branch wins.**
