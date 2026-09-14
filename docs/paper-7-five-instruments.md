# Five Instruments, Five Wrong Readings

*Seventh paper in the Rabbitstew series, and the first about the programme rather than
about robots. **Draft. Nothing in it has been reviewed.** It reports nine occasions on
which this project measured something with a broken instrument, believed the reading, and
built on it — two in the arena experiment (2026-09-11), five in the foraging ecology over a
single eighteen-hour period (2026-09-12/13), and **two more during this paper's own review**
(2026-09-13/14). Sources: `docs/followup-paper.md` §4.1–4.2, Chaotic RBT-38, RBT-58, RBT-59,
RBT-60, RBT-62, RBT-63, RBT-64, RBT-68, RBT-69, RBT-77, and the two lead-researcher
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
(+59%, 7/7 robots)** on the population it was measured on — while the miswired circuit the
programme had been counting all along is a smell-triggered pirouette worth **-1.502**.

A replication on a second substrate, run while this draft was in review, reproduced the
control and not the prize, and then **resolved into the best material in the paper**.
Nothing in a foraging ecology rewards driving nose-first over tail-first. The Pioneer has a
designed front; evolution never agreed to it, and each lineage froze onto a direction
arbitrarily. The population the +0.897 was measured on **drives backward** (pooled travel
offset −174.1°, all seven robots); the replication's population drives forward on balance
(pooled +12.0°, five of seven). The identical four weights are therefore a compass for one
and an anti-compass for the other. **And the parameter sorts individual robots, not just
populations**: within the forward-driving population, the two members that happen to drive
backward gain +3.734 and +1.109 while the five forward-drivers average −1.738, so the
reported −1.154 was five anti-compasses averaged with two compasses. No sign error, no
irreproducibility, no world effect: **two correct measurements of opposite things,
reconciled by a population parameter nobody had thought to record.**

Reviewing the programme for other instances, we find nine, two of which arrived during this
paper's own review. In eight, a quantity was measured with a device that could not see the
thing the question turned on, the reading was believed, and subsequent work was denominated
in it. The failures are not independent: **six of those eight share a single structure**,
which we name and characterise, and the other two are the already-catalogued case of
evolution exploiting its apparatus. **The ninth is neither, and is the more interesting
case** — no instrument was broken; a free parameter of the population silently inverted a
hand-installed intervention. It bounds the taxonomy, and it is closer to the field's
existing catalogue of evolution exploiting its apparatus than to anything else here.

We report what caught them, and — more usefully — what did not. Four independent layers of internal
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

## 3. The nine incidents

| # | Instrument | What it could not see | What it cost |
|---|---|---|---|
| A1 | the competitive bout score, with free mass | that the score rewards mass regardless of control | one near-parity result |
| A2 | the same score, with a bounding-sphere spawn lift | that potential energy at spawn is a motor | a 250-generation matrix, 4 conditions |
| E1 | unpaired standard errors on paired lesion runs | that the modes shared a seed list | **10 of 15** standing nose claims |
| E2 | a compass criterion, fixed in advance, met | that both its conditions clear on mobility alone | one false compass, nearly published |
| E3 | "seasons" as the unit of search effort | that 600 seasons is ~20 reproductions | the denomination of every economy arm |
| E4 | `sensor_influence`: absolute weights, clipped at 3.0 | sign structure, and any magnitude shortfall | one reversed conclusion |
| E5 | the fixed body's hinge convention, documented nowhere | that the effector **sum** steers | ten world arms; four agents |
| E8 | bearing measured against chassis yaw | that the population drives in reverse | two wrong retractions in one evening |
| E9 | *(not an instrument — see §3.10)* | that direction of travel is a free parameter | one apparent non-replication |

E8 and E9 keep the labels they were given on RBT-69 and RBT-70 during review, so the tickets
and the paper agree; there is no E6 or E7. Both arrived after this draft was filed, which is
why §3.8 to §3.10 read as a narrative rather than a post-mortem.

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
Both facts decide the question the programme was asking. Reproduced during the RBT-63 fix: a
compass and its common-mode twin both score `(2.0, 2.0)`, and a 32x weight increase reads as
**2.0 to 6.0** because of the per-link clip, against **1.0 to 32.0** signed.

On this instrument a survey concluded that "the structural precondition for a Braitenberg
compass is present in 7 to 17 percent of the wheeled population, so the bottleneck is **not**
that the circuit is never proposed." The topology counts were right and replicate. The
conclusion was reversed five hours later by its own author, using a signed, unclipped measure.

**The in-repository damage is narrower than that suggests, and the reason matters.** The
audit RBT-63 asked for found that *every surviving `influence` claim committed to the
repository is a zero claim* - and zero is the one value this measure reports faithfully,
because absolute weights cannot cancel, so a zero total means no path of length <= depth
exists. Both survive. The reversed conclusion lived in `runs/compass-gain/`, which **was
never committed**, because `runs/` is gitignored (RBT-68). So the audit of the instrument's
damage is bounded by what happens to be in git, and the load-bearing half was not in it.
That is a sharper version of this paper's point than the wide claim it replaces.

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

**On this population the world rewarded chemotaxis richly, and ten world-variant arms were
spent failing to establish it.** The library already knew the convention: a hand-written straight-line
controller hardcodes `(+1, −1)` with the comment *"the right wheel needs the opposite
sign."* That knowledge lives inside one function and is surfaced nowhere at the
brain/genotype interface, in synthesis, or in any analysis tool. During the audit, **three
separate agents independently wrote "corrected" compasses that still routed the common mode
onto the throttle, after being told the axis convention was under suspicion.** The physics
is fine. The defect is that the convention is invisible from where circuits are written.

### 3.8 The replication, what it appeared to leave open, and what resolved it

Run by the author of the RBT-63/RBT-64 fixes while this draft was in review, on a different
population (`RBT-19/P-801`, 7 robots × 64 paired seeds × 7 magnitudes, **6,720 bouts**,
baseline 2.770 items):

| motif | w | delta items | se | robots improved | metres moved | turns |
|---|---|---|---|---|---|---|
| compass | 1 | +0.143 | 0.195 | 4/7 | 2.16 | 2.01 |
| compass | 16 | **-1.154** | 0.204 | 2/7 | 3.93 | 1.83 |
| compass | 32 | **-0.549** | 0.245 | 3/7 | 4.38 | 1.52 |
| common | 4 | **-2.710** | 0.190 | **0/7** | **0.35** | **2.86** |
| common | 32 | -2.708 | 0.193 | 0/7 | 0.20 | 2.96 |

**The control replicated decisively.** At w ≥ 2 the common mode stops foraging and spins —
displacement 2.00 m → 0.20 m, yaw 2.28 → 2.96 turns, yield → 0.062, 0 of 7 robots — which is
§3.7's sign decomposition confirmed on an independent substrate by an independently written
script. **The prize appeared not to.** The compass read null at w ≈ 1 and fell monotonically
from there, the opposite of §3.7's dose-response, where a = 64 topped every sweep.

Three artefacts were ruled out before that null was reported: the nose is **not saturated**
(level 0.168–0.860 over real bouts, median left–right gap 0.056), four of the seven robots
carry **zero pre-existing wiring** out of either wheel nose, and it is **not tanh saturation
at the effectors** (0.1–1.0% of ticks pin at the rail, and the fraction *falls* as gain
rises). The +0.897 also re-ran exactly on its own substrate — baseline 1.516, 7/7 robots,
identical to three decimals. So both numbers were solid and they disagreed.

**The world was ruled out first, and explicitly.** Before the resolution arrived, the
replication's author tested their own hypothesis by reshaping `RBT-19`'s configuration toward
the source's world — 12 items, no patches, no regrowth — which moved the baseline to 1.219
against the source's 1.516, approximately matching. The compass stayed negative at every
magnitude §3.7 reports a gain at (**−0.328 ± 0.069** at w=16, **−0.375 ± 0.077** at w=32),
while the common mode pirouetted in that world too. They also diffed their installation
against the original: same four weights, same signs, same magnitudes. **Matching the world did
not recover the gain, and the installation was not the difference** — so by the time the real
explanation arrived, the two obvious ones had been tested and rejected, one of them by the
person who had proposed it.

**What resolved it is the ninth incident, and it is not a mistake by anyone.** Nothing in a
foraging ecology rewards driving nose-first over tail-first. The Pioneer has a designed
front; evolution never agreed to it, and each lineage froze onto a direction arbitrarily:

| population | pooled travel offset | so the published motif is |
|---|---|---|
| `RBT-23/W4b-801` (the +0.897) | **−174.1°** — drives backward, all seven robots | a **compass**, +0.897 |
| `RBT-19/P-801` (the replication) | **+12.0°** — five of seven forward | an **anti-compass** on balance, −1.154 |
| `drive_straight_genotype` | forward by construction | — |

One free parameter reconciles everything the programme could not reconcile that week. No sign
error by anyone, no irreproducibility, **two correct measurements of opposite things.**

**The sharpest confirmation came afterwards, one level down.** A pooled comparison of two
populations is a weak test; the reading predicts something much stronger, which is that
*within* a single population the robots the motif helps should be exactly the robots that
drive backward. Measured on the forward-driving population at w=32, 64 paired seeds:

| gen | travel offset | drives | motif Δ items |
|---|---|---|---|
| 0 | −0.4° | forward | −1.844 |
| **100** | **+177.2°** | **backward** | **+3.734** |
| 200 | −4.3° | forward | −2.438 |
| 300 | −2.3° | forward | −2.719 |
| **400** | **+165.1°** | **backward** | **+1.109** |
| 500 | +23.8° | forward | +0.609 |
| 590 | +2.1° | forward | −2.297 |

**Forward (n=5): mean −1.738, 1 of 5 improved. Backward (n=2): mean +2.422, 2 of 2 improved.**
The published −0.549 at this magnitude was five anti-compasses averaged with two compasses.
The two backward-drivers bracket the disputed +0.897 *from above*, and the single
forward-driver that gains is the least directionally committed robot in the set (+23.8°,
R = 0.506). Direction of travel does not merely correlate with the population-level sign; it
sorts individuals.

**A correction this produced, recorded because the paper cites the figure.** The resolution
as first written reported this population at +5.1° with "six of seven forward, gen 90 the
exception." An independent reimplementation measures **+12.0°, R = 0.430, five forward and
two backward**, and notes that the population under test has no generation 90 in its
sampled set at all, so the quoted exception came from a different generation list. The
resolution is unaffected and strengthened; the breakdown is corrected here, and this paper
uses the independently measured figures.

In the travel frame — where no heading convention enters — the motif on `W4b-801` is better
aimed than baseline (1.377 against 1.490) and eats more (2.393 against 1.558), and a
phantom-smell control confirms the food-dependence (+0.835 → −0.071). **It is a genuine
chemotactic compass on that population**, and §3.7 stands as drafted.

Two consequences for this paper. The first is that the world plays no part: an earlier draft
of this section proposed that the compass pays under instant regrowth and fails under patchy
depletion, and partially rehabilitated paper 6 on that basis. **That paragraph was wrong and
is deleted**; the arm filed to test it (RBT-75) was cancelled unrun. The second is that the
programme's answer to its headline question is back where RBT-45 left it — a claim about
acquisition, not about worlds or signs — and RBT-77, which argued that sign inversion is what
prevents a compass accumulating, was refuted by its own author's falsifier on a common
denominator: direction inverts at **7.6% per mutation event** [0.017, 0.142], while in 288
single mutations the largest steering gain observed was **2.075** against the ~16 needed to
be measurable, and only **1 chain in 16** of forty mutations ever reached it. Inversion is a
real secondary tax on a compass once acquired. Acquisition is the barrier.

**And the acquisition number this paper has been quoting is itself a projection.** The
figure carried downstream — drift proposes a paying motif in **0.70%** of realistic lineages
— was reconciled against the competing analytic estimate of ~10⁻⁷⁷ on one denominator, and
both turned out to be right about different routes. The **direct** four-link motif never
arrives: 0 of 10,000 drift lineages, maximum |a| = 3.3. The 0.70% is a depth-4 *path* sum
carried entirely by indirect routes through the recurrent global brain (median indirect
share 1.000), where weights multiply along a path and the magnitude grows about ×2.8 per
link. It is not a compass arrival rate, and the demonstration is a negative control done
properly: an information-free sensor pair — the `agent`-smell noses on the same two wheel
parts, carrying no food gradient at all — clears the same thresholds at the same rate as the
food noses at **a ≥ 64, the threshold that pays**, on both populations.

**And then the quantity turned out not to be a quantity.** The path sum `Σₖ Mᵏ` converges
only if the recurrent core's spectral radius `ρ < 1`. Measured on all fourteen committed
bests, **`ρ` is above 1 on every one of them** — 1.565 to 4.920. Run over the drift lineages
the arrival rates were computed from, **100.0% of the lineages that clear the threshold move
by more than 20% between depth 4 and depth 8**, in both pools. Their median `|a|` goes
**22.4 → 1,581 → 153,722** at depths 4, 8 and 12. Fifty-one lineages clear at depth 4; a
further 544 clear at depth 8.

So the depth-4 figure is **not an upper bound on anything** — it is an arbitrary truncation
of a divergent series, and the arrival rate is *set by where the counting stopped* rather
than bounded by it. Ten times larger one link deeper. Its author, who had written "a
permissive upper bound," amended it to this within the hour: **the direct-route figure is
the only one of the two that is well defined**, because depth 1 is exact on every robot, and
there it is 0.00% across 10,000 lineages.

**And then the same thing happened a third time, to the number that replaced it.** The
adversary assigned to check that result found that the qualified figure is *also* permissive,
for a reason with the same shape. The "gradient-dominant" filter, `|a| > |c|`, which is used
by three separate scripts in this programme's analysis stack, reduces algebraically to

> `|a| > |c|` ⟺ `−4·s₁s₂ > 0` ⟺ **`s₁·s₂ < 0`**

— asserted exactly on 200,000 random pairs. **It is a sign test carrying no magnitude
information whatsoever.** A pair with steering gains of +100 and −0.001 passes it while being
a one-nose pirouette to four decimal places. Measuring the balance of the lineages it admits,
`r = min(|s₁|,|s₂|)/max(|s₁|,|s₂|)`, which is 1.0 for a true antisymmetric motif: **median r
is 0.013 and 0.058**, with two thirds of them below 0.1. And weighting by what the two terms
are actually worth — the gradient earns +0.897 at a = 64, the pure common mode costs −1.502,
so break-even is `a/|c| ≈ 1.674` rather than 1.0 — **one of the nine passing lineages across
both pools would earn anything at all.** Roughly 1 in 5,000 on one population and 0 in 5,000
on the other.

So a single quantity was read four times in one night. **0.70%**, believed for days as
"drift proposes a compass". Then **0.06–0.12%**, once the food-specific control was matched.
Then **~0.02%**, once the gradient-dominance filter was shown to be a sign test with no
magnitude in it. And then the fourth reading, which subsumes the other three: **all of them
are computed on the path route, and the path route has no value to compute.** The only
well-defined number in the family is the direct one, and it is zero.

That is the paper's own thesis at its sharpest, and it did not need a new experiment — three
of the four readings came from linear algebra over already-committed files, in a single
night, by people attacking their own results. Two caveats belong with it, both raised by the
adversary against their own correction: at a ≥ 64 the comparison is one lineage against one
lineage, so neither the claim nor its correction is resolved at the threshold that matters;
and the payoff weighting rests on two linearised points from one population, which is not
enough to write a new threshold into a script.

### 3.9 E8 — the instrument built to catch the class, which had the class

The resolution above did not arrive cleanly. Between the non-replication and the explanation
sits a retraction that was posted and withdrawn within ninety minutes, and the instrument
that produced it was built **by the author of this taxonomy, an hour after writing it, while
deliberately applying it**.

To settle whether the motif was chemotactic, that author built a positive control: a Pioneer
with its evolved brain blanked to zero, forward throttle only, one motif installed — a robot
whose behaviour is known by construction. Sound, and the right instinct. The reported
measurement was **bearing to the nearest live item**, taken against **chassis yaw**.

Chassis yaw was calibrated on `drive_straight_genotype`, a designed forward-driver. Applied
to a population that drives in reverse, **every evolved-robot bearing was rotated by π.** The
conclusion drawn — that the motif this paper calls a compass is the anti-chemotactic one —
was exactly backwards, and was published to the ticket before geometry caught it.

The projection is **the reference frame**. Bearing-against-chassis-yaw is many-to-one over
travel direction, and a robot's heading is not a property of its body. That is §4's form
exactly. A second projection sits inside the same instrument and was noted by its author:
"bearing to the *nearest* item" is not what the circuit climbs either — the circuit climbs
`squash(Σ exp(−d/1.0))`, a summed field whose gradient points at the local centroid.

What makes this worth its own subsection rather than a line is the timing. **The positive
control was sound for its own robot; generalising it to a population that drives the other
way is what broke, and no amount of care inside the instrument would have caught it.** The
taxonomy in §4 did catch it, prospectively, on a case it was not derived from — which is the
test §9 said it needed. But it caught it *after* the wrong claim was posted, and it did not
prevent an author who had just written the checklist from building the next instrument with
the same defect inside an hour. Both facts belong in the record, and the second is the more
important one for §6.

### 3.10 E9 — a free parameter, and the boundary of the class

Direction of travel is the ninth incident and **it does not belong to §4's class.** No
instrument was blind to anything. Both measurements were correct, both replicated, and the
apparatus was working perfectly throughout.

What happened instead is that a **hidden free parameter of the population silently inverted a
hand-installed intervention.** Selection never had a reason to fix which way the Pioneer
drives, so it did not, and the experimenters carried an assumption the evolutionary process
had never agreed to. Of the obvious geometric candidates this is the only free one: roll
(−0.3° / −0.0°) and pitch (+1.1° / −1.0°) are pinned in both populations, upright 0.93–0.98,
so the noses stay left-right as designed.

This is closer to Lehman & Clune's genre than anything else in this catalogue — evolution
quietly exploiting a symmetry the experimenter forgot was free — while still producing the
signature failure shape of the rest: well-formed numbers, perfect replication, opposite
conclusions. **It is the bridge between this paper and its nearest ancestor.**

It also generates the one methodological rule in the catalogue that transfers without
modification to any other system:

> **Installing a circuit on a population is population-specific. Measure the direction of
> travel first, and verify any taxis claim in the travel frame — never against a body-fixed
> axis.** Two minutes per run.

And a sharper version of the same point, which the programme has adopted as a standing rule:
*"the population drives forward" is not a property of a run; it is a property of a run **at a
generation**.* Direction is neutral and labile — 7.6% per mutation event — so any arm
installing a fixed-sign circuit must state which generation it means.

---

## 4. The class

Six of the nine (E1–E5 and E8) share one structure, and it is not "a bug":

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
| E8 | the travel frame collapsed into a body-fixed axis (chassis yaw) |

**Eight of the nine incidents fit this shape. E9 does not, and the exception is
load-bearing.** In E9 no instrument was blind, no summary was many-to-one, and every number
was correct; a free parameter of the population inverted the intervention instead. That
matters twice over: it means the class is a real category rather than a relabelling of
"mistake," and it means a programme could close every projection in its analysis stack and
still be caught by E9's shape. §9 records this as the taxonomy's measured boundary rather
than a gap in it.

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

**An independent reimplementation, deliberately not a second invocation.** When the
within-population test above was run, its author declined to confirm the result by calling
the same `travel_direction` script the resolution had used, on the explicit grounds that a
six-hour chain in which two retractions were themselves instrument failures is not the place
to trust one instrument twice. They wrote a second implementation instead. **The two agree
on direction and disagree on the count** — five forward and two backward against six and
one, and a pooled offset of +12.0° against +5.1°. One invocation could not have revealed
that, and the discrepancy is small enough that nothing would have looked wrong.

**A physical quantity computed independently of the pipeline.** E2 was killed by one number
— 0.416 items per swept cell, from density × area — that the analysis stack does not
produce. Every instrument in the programme could have been broken and that number would
still be right.

**A positive control on a robot whose behaviour is known by construction** — the one
instrument class this programme did not own. It is what finally settled the direction
question. It is also what produced E8, because a positive control is only as general as the
population it was calibrated on. Both halves of that are findings.

**Pre-registration, but only for a specific job.** Four of five wrong predictions in the
final push are visible *only* because a verdict rule was fixed before the numbers existed:
a selection-strength bound missed (+0.43 SD measured against a predicted <0.3), a
"buy generations" recommendation refuted by its own author's arm, a wiring survey reversed
by its own author, and a gradient-dominance filter predicted at confidence 0.6 to cut a rate
by an order of magnitude that in fact cost a factor of 1.6–3.8. But E2 shows the limit
exactly: pre-registration binds the *analyst*, not the *apparatus*.

### 5.3 Two of these counterfactuals have since been tested, and one misfired

§9 of the filed draft flagged the claims in this section as asserted rather than run. Three
have moved since, and they did not all move the same way.

**Landed.** "A dot-product assertion would have prevented E5" and "a signed, unclipped
influence measure would have prevented E4" are now `tests/test_pioneer_drive.py` and
`tests/test_signed_influence.py`, merged in PR #6, together with `steering_throttle()` and
`drive_commands()` at the interface where circuits are written. The replication in §3.8
derives its four weights from `drive_commands()` rather than typing them out; three agents
wrote wrong corrections by hand before it existed and none has since.

**Misfired.** The third — that a manipulation check on a known-behaviour robot would have
caught E5 — was asserted, then appeared to be demonstrated, and **the demonstration turned
out to be E8.** The check was built, it fired, and it was wrong, because it inherited a
reference frame from the robot it was calibrated on. The counterfactual may still be true;
what is established is only that its first test failed in the class it was testing for.

That is the honest scoreboard: two of three, and the third is a cautionary tale rather than
a null. It is recorded here rather than quietly upgraded because §5's whole argument is that
the checks which scale are not the ones that work.

### 5.4 The uncomfortable summary

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
   **E8 is the strongest evidence against the optimistic reading of this section, and it
   arrived after the section was written.** An author who had just written this taxonomy,
   who was deliberately applying it, and who was building an instrument *specifically to
   catch the class*, built the next instrument with the same defect inside an hour — and
   published a conclusion from it. Knowing the failure mode in detail, in the moment, while
   looking for it, was not sufficient. Whatever protection is available here, it is not
   awareness.

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
are orthogonal**, and only the first is currently audited. This programme supplies a third
axis that neither covers, and it is the one doing the most damage here: **whether the
evidence still exists.** §9 records the case — the paper's own headline number and the
measurement that explains it both rest on genotypes that are in no repository.

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

   **This has since been done** - `tests/test_pioneer_drive.py`, `steering_throttle()` and
   `drive_commands()` (RBT-64), and `signed_influence` in the standard analysis output
   (RBT-63). The estimate was accurate, and the recommendation is recorded here as
   *discharged* rather than proposed. The replication in §3.8 derives its four weights from
   `drive_commands()` rather than typing them out, which is the first evidence that the
   accessor does the job it was added for: three agents wrote wrong corrections by hand
   before it existed, and none has since.
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
  under study. The incident count is a lower bound: the filed draft found seven by looking,
  **two more arrived during its own review**, and we have no estimate of how many instruments
  remain unaudited. `sensor_influence` was in every run's output for the programme's whole
  life before anyone read its source.
- **Two of the nine incidents were found by this paper's own review**, which cuts both ways.
  It is evidence the taxonomy does work prospectively (E8), and evidence that a catalogue
  compiled at any given moment is incomplete at that moment — including this one.
- **The class in §4 has a measured boundary, which is better than an unbroken record.** It
  caught E8 prospectively, on a case it was not derived from. It did **not** catch E9,
  because E9 is not in its class: no instrument was blind, and a free population parameter
  inverted the intervention instead. A taxonomy that never fails to apply is usually a
  taxonomy that is not saying anything.
- **The +0.897 figure carries every caveat of its source**: seven robots from one run, solo
  bouts, and **a floor rather than an estimate** — the sweep has since been extended and the
  gain is still climbing at a = 384 on both populations with no turnover, so +59% is the
  bottom of a range whose top nobody has found. It is Pioneer-only; for an arbitrary evolved body the steering axis is
  not the effector sum and the decomposition does not apply. **It is also population-specific
  in the sense E9 establishes**: it is a compass for a reverse-driving population and an
  anti-compass for a forward-driving one, and any restatement of it must name the population
  and, strictly, the generation.
- **Co-adaptation is untested.** Every compass measured was bolted onto a finished
  controller. Whether a population can *hold* one it grew around is the open experiment
  (RBT-65), and until it runs, "the world rewards chemotaxis" means "a hand-installed
  circuit is rewarded on a population that drives the way the installer assumed."
- **The counterfactuals in §5 are two-thirds tested and one-third cautionary** (§5.3). Two
  landed as merged tests; the third was asserted, apparently demonstrated, and the
  demonstration turned out to be E8. The claim that pre-registration made four retractions
  visible remains uncontrolled and is the kind of claim this paper otherwise warns against.
- **The paper's own headline number cannot be checked from a fresh checkout, and neither can
  its explanation.** This is the sharpest limitation here and it survives RBT-68's fix.
  `runs/RBT-23/W4b-801` — the population the +0.897 was measured on, and the same population
  whose −174.1° travel offset is half of §3.10 — **was committed nowhere** when the
  disagreement was live. It has since been recovered: the source's author still had the
  files and committed the seven genotypes and the run `config.json` under
  `docs/artifacts/RBT-23-W4b-801/`, 728K, which settled the dispute in an afternoon. Those
  files and `scripts/travel_direction.py` are **on the integration branch** as of PR #14;
  `verify_independent.py` — the script this paper cites as its independent verification — is
  committed on an open pull request and **not yet on the mainline**, so a reader can now
  obtain the substrate but not yet the check written against it.

  **The recovery is the uncomfortable part, not the loss.** It happened because one author
  still had the artifacts in a working tree, which the repository did not guarantee; had
  that session ended first, the programme's most-quoted number would have been permanently
  uncheckable. It bears directly on §7 and adds a third axis to it. Reproducibility and
  instrument validity are orthogonal; **whether the evidence still exists** is orthogonal to
  both, and a result can fail on it while passing the other two. A programme that fixed
  every projection in its analysis stack and pre-registered every verdict rule could still
  arrive here. RBT-68 (PR
  #7, merged) now tracks reports, scripts, readouts and `config.json` by default, but
  deliberately continues to ignore per-generation genotype dumps as regenerable bulk, and
  the genotypes are exactly what both measurements need. The consequence is concrete: the
  independent verification this paper cites as having been written from scratch without
  reusing any audit script (`verify_independent.py`) **is not executable by a reader**, and
  the disagreement in §3.8 could only be settled by someone holding those files.
  `runs/compass-gain/`, where E4's reversed conclusion lived, was in the same position and
  is now committed.

  It bears directly on §7 and adds a third axis to it. Reproducibility and instrument
  validity are orthogonal; **whether the evidence still exists** is orthogonal to both, and
  a result can fail on it while passing the other two. A programme that fixed every
  projection in its analysis stack and pre-registered every verdict rule could still arrive
  here.
- **A tenth instance was found among this paper's own citations, and we have not
  renumbered.** The 0.70% acquisition rate (§3.8) is a quantity whose name does not match
  what it measures — a network-gain bound read as a compass arrival rate — believed, quoted
  downstream, and repeated by this paper. That is §4's class exactly, making the true count
  at least ten — and the same quantity has now been re-read four times in one night, each
  reading an order of magnitude smaller, until the fourth established that the quantity the
  first three were computed on **diverges and has no value at all**. The criterion that
  produced the second is still live in three scripts. **One number, four instances**, and
  the only well-defined member of the family is the one that reads zero. The labels E1–E9 are load-bearing across a dozen tickets and are left alone;
  the honest statement is that the catalogue is a snapshot of what had been noticed by a
  particular hour, and that the rate of new instances has not fallen off. **Three of the
  last four were found inside this paper's own review.**
- **§3.10's rule is stated more confidently than it has been tested.** "Measure direction of
  travel before installing any circuit" is derived from two populations. It is cheap enough
  that the asymmetry of costs justifies it regardless, but it is not an established general
  result.

---

## 10. Conclusion

The programme spent roughly ten world-variant arms establishing that its world did not
reward chemotaxis, using a circuit that on this body is a pirouette worth minus one and a
half items. The cheapest thing that would have revealed it was an assertion about two dot
products.

The corrected circuit is worth +59% — on a population that drives backward. On one that
drives forward the same four weights cost it a full item, and both numbers are right. That
is the note to end on, because it is the one the programme could not have reached by being
more careful with its statistics. **Nothing in the world the robots live in rewards driving
nose-first over tail-first, so selection left the choice free, and an experimenter installed
a circuit that assumed an answer.** No instrument was broken. The apparatus worked perfectly
and produced opposite conclusions.

The programme's error was never that it reached a wrong conclusion about chemotaxis. It is
that it reached conclusions faster than it checked its rulers — and then, having written a
paper about exactly that, reached one more too fast anyway, twice, during this paper's own
review.

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
python scripts/compass_replication.py      # §3.8, ~10 min on four cores
```

E4's signed influence measure and E5's axis assertion are in the repository, not on a branch
(`tests/test_signed_influence.py`, `tests/test_pioneer_drive.py`, `steering_throttle()`,
`drive_commands()`, `analysis.signed_influence`; PR #6). E1's paired-statistics helper is
`rabbitstew/paired.py` with `scripts/paired_lesion.py` (PR #4), and `runs/` is now tracked
for evidence though not for bulk (PR #7). §3.9's and §3.10's material — the travel-direction
measurement, the direction-heritability draws and the acquisition-versus-inversion race —
lives on RBT-69's and RBT-77's branches and is not yet merged; cite those tickets rather than
a repository path.

**Status of the tickets this paper draws on, as of 2026-09-14.** Accepted: RBT-38, RBT-58,
RBT-59, RBT-60, RBT-62, RBT-63, RBT-64, RBT-68, RBT-69. Retitled and closed: RBT-61. Closed
as refuted: RBT-77. Cancelled unrun: RBT-75, the world-inversion arm this paper's earlier
draft called for, which §3.8 explains is unnecessary. Merged: PRs #4, #6, #7, #9; integration
branch at `f3aa69d`.

**Where a branch and this document disagree, the branch wins.**
