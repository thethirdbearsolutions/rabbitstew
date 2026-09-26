# The Prize, the Proposal Rate and the Magnitude Gap

Why six hundred seasons produced no compass.

*Eighth paper in the Rabbitstew series, written under Chaotic RBT-72. **Draft, filed for
review; nothing in it has been adversaried.** It owns strand 3, the sensing null and its
explanation. Paper 5 §6 (`docs/paper-5-the-blind-forager.md`) and paper 6
(`docs/paper-6-the-cow-is-the-correct-answer.md`) cite this result and do not re-derive it;
paper 7 (`docs/paper-7-five-instruments.md`) catalogues the instruments, and this paper
borrows its catalogue form for the strand's own withdrawn claims in §7. Nothing here is
re-run and no new simulation was made for it. Every number is cited to a committed file on
the integration branch, and every headline number is recomputed from that file by
`runs/RBT-72/rederive.py`, whose printed table is `runs/RBT-72/rederive.txt`; the bracketed
tags in the text (P6, R15, M18 and so on) are that table's row ids. Where the recomputation
disagrees with the figure the tickets quoted, the text says so and uses the file's number.
Where a number rests on a printed readout with no data behind it on the branch, or on prose
alone, the text says that too. Sources: `docs/foraging-world.md`, `docs/rbt-91-weight-scale-decision.md`,
and Chaotic RBT-45, 62, 65, 67, 69, 77, 78, 80, 81, 87 and 91, with their reports and
readouts under `runs/` and `docs/artifacts/`. One section, §5, depends on RBT-97, which is
running while this is written; it is stated as a pending result with both outcomes' consequences
written before the result exists.*

---

## Abstract

A population of designed two-wheeled robots foraged for six hundred seasons in a world that
gave each wheel a nose, and no robot ever steered by smell. We decompose the question "why
not" into three quantities that the programme spent a month learning to measure separately:
the **prize** (what a working compass is worth to a robot that carries one), the **proposal
rate** (how often the mutation operator builds its structure), and the **magnitude gap**
(whether what it builds is strong enough to be worth anything). **Every number in this paper
is for one body, the designed Pioneer, on two founding populations.** No co-evolved body
carries a food nose on both wheels at any depth, the decomposition below uses the Pioneer's
specific geometry, and nothing here licenses a claim about chemotaxis in evolved bodies
generally.

On that body the three are separately measured and disagree about where the obstacle is. The
prize, for a four-link compass installed directly into the controller, is large and still
rising at the top of every sweep: at least **+1.875 items against a 1.270 baseline** on one
population and **+8.094 against 2.688** on the other's forward drivers, once the circuit's sign
is set by the way each robot actually drives, and a phantom-smell control removes the whole
gain. The proposal rate is not zero: a nineteen-mutation drift from committed parents builds
the only compass structure the genotype can express in **84 of 200,000** lineages, and those
arrivals point toward food about as often as a coin flip (**35 of 83** resolved). The
magnitude gap is total: **not one** of those arrivals' own circuits reaches the response of
the first paying rung, at the operator's default weight scale or at four or ten times it,
while widening the scale inflates the recurrent gain of brains carrying no compass at all. So
on the record as of 2026-09-26, drift proposes the structure, never the magnitude, and no
change to the one operator parameter that should supply magnitude does so.

What the record does not yet contain is a payoff curve for the circuit drift can actually
build. Every prize above is for a directly wired motif that the genotype's encoding cannot
express; the expressible motif is routed through a global interneuron and has never had its
payoff measured on these bodies. That is RBT-97, and §5 writes down what each of its outcomes
does to this paper before it reports. Eleven claims made in this strand during its month were
withdrawn; §7 lists them with the instrument each rested on, and four figures still quoted
elsewhere fail to re-derive from their own files (§8).

---

## 0. What this paper is, and what it is not

It is a synthesis. The measurements are the tickets' and every one is cited to its file. What
the paper adds is the decomposition as the organising frame, the ordering of the three terms,
a re-derivation of every number from the branch, and a record of which claims fell and why.

It is not a claim that the search *cannot* find a compass. The decomposition says why this
search, on this body, at this depth, did not; §5 says what would change that reading. It is
not a claim about co-evolved bodies (see the abstract). And it is not the paper the ticket
was filed to write. RBT-72 was scoped on 2026-09-13 around three numbers, *the prize is +59%,
the topology is common, the magnitude never arrives*, and the ticket's own description asked
for the paper to be held until co-adaptation (RBT-65), the prize's upper bound (RBT-67) and a
discrepancy between two authors (RBT-62 against RBT-45) were settled. All three were settled
and each changed the thesis: the prize turned out to have a sign that depends on the
population, the "common topology" turned out to be a connectivity count that could not tell a
compass from a pirouette, and the discrepancy turned out to be two instruments of which one was
not a quantity. The ticket's
premise that the paper should contain the pre-registered `weight_sigma = 2.0` evolutionary arm
of RBT-62 §7 also did not survive: that arm was never run, for a measured reason (§6.3), and
its prediction is unscored.

---

## 1. The body, and the three quantities

### 1.1 The body steers with the sum

The Pioneer's two drive wheels hinge about their own outward normals, so the two hinge axes
are antiparallel, world-frame dot product **−1.0000** [P1] (`docs/artifacts/RBT-23-W4b-801/verify_independent-rerun.txt`).
The **sum** of the two drive Effectors' commands turns the robot and their **difference**
drives it forward: the transpose of the differential drive every earlier controller author and
structural statistic assumed. Paper 7 §3.7 records how that convention was found (E5); this
paper uses it and does not re-argue it. `rabbitstew.fixed.drive_commands(steering, throttle)`
writes a circuit on the correct axes by construction (RBT-64).

### 1.2 The decomposition: compass and pirouette

Each wheel carries a `food` nose. Write each nose's signed gain onto the steering axis as `s₁`
and `s₂`. Any pair splits into two terms:

| term | what it puts on the steering axis | what it does |
|---|---|---|
| `a = (s₁ − s₂)/2` | `a · (n₁ − n₂)`, the left–right difference in smell | turns up the gradient: **the compass** |
| `c = (s₁ + s₂)/2` | `c · (n₁ + n₂)`, the total smell | turns harder whenever anything smells: **the pirouette** |

Two consequences carry the rest of the paper (RBT-62, `runs/compass-gain/REPORT.md` §2).
First, **a single wired nose forces `|a| = |c|` identically**: half compass, half pirouette.
Second, the pirouette is not neutral. Installed on its own it destroys foraging: **−1.502
items** on the population the prize was first measured on [P4], and on a second population
**−2.710, 0 of 7 robots**, displacement collapsing from 2.00 m to 0.35 m [P29]
(`docs/runs/RBT-69-compass-replication.txt`). So a nose that is wired at all is at best half a
compass carrying an equal dose of something measurably worse than nothing.

The criterion the strand used throughout to separate the two, `|a| > |c|`, is algebraically
`s₁ · s₂ < 0`, a sign test with no magnitude in it (RBT-78's adversary, asserted exactly on
200,000 random pairs, `docs/runs/RBT-78-adversary.txt`). It is retired (§7, W7). The instrument
that replaced it, `rabbitstew.analysis.steering_terms`, reports `a`, `c`, the balance ratio
`r = min(|s₁|,|s₂|) / max(|s₁|,|s₂|)` and the sign separately, with no threshold (RBT-81).

### 1.3 Two motifs, only one of which the genotype can hold

The compass that pays is the **four-link antisymmetric motif**: one nose into both drive
Effectors at `+w`, the other into both at `−w`, so `a = 2w` and `c = 0`. Written straight into
a synthesised controller's weight matrix it is exact. **Written into a genotype it is
rejected.** A link into a node's brain may come only from that node, the global brain, or a
neighbour, and the two drive wheels are siblings, not neighbours (`genotype.py:496`); the cross
links fail validation (RBT-87, `tests/test_steering_terms.py`). The shortest compass the genotype *can* hold, and the one every proposal count below is for, is
**routed**: both noses into one global `tanh`
interneuron with opposite signs, the interneuron into both Effectors with the same sign
(`scripts/genotype_motif.py`). Its nose-to-Effector path is two links, so it reads **zero** on
the depth-1 term by construction and exactly `2w` on the depth-2 term (RBT-87; RBT-80's
adversary, 7 of 7 committed P-801 bests).

This distinction is the least visible fact in the strand and the one §5 turns on. **Every
payoff number in §2 is for the direct motif. Every proposal-rate and magnitude number in §3
and §4 is for the routed motif.** The bridge between them, a payoff curve for the routed motif
on these bodies, does not exist on the branch.

### 1.4 Two spaces, and a depth chosen by the circuit

A weight-space quantity (the direct weight, or a path sum through the weight matrix) is a
property of the genome. A behaviour-space quantity (what the network's steering output
actually does when the noses are driven apart) is a property of the genome and its operating
point together. On 1,519 drift lineages carrying direct wiring, the depth-1 term recovers the
**sign** of the measured response in **1403/1519 = 92%** and its **magnitude not at all**
(correlation **+0.0013**) [R13, R14] (`docs/runs/RBT-81-adversary.txt`). And any path sum
deeper than the circuit under test is not a quantity on these brains: the recurrent core's
spectral radius exceeds 1 on every committed Pioneer best, so the series diverges, and **every**
drift lineage that clears `|a| ≥ 16` at depth 4 moves by more than 20% between depths 4 and 8,
**100.0% on both pools**, with **544** and **358** further lineages clearing only at depth 8
[R11, R12] (`docs/runs/RBT-78-truncation.txt`). The rule this paper follows is the programme's:
the depth is chosen by the structure under test and printed beside the number, and a magnitude
is scored on the circuit under test, not on the whole brain around it (README; RBT-87, RBT-91).

---

## 2. The prize: what a correctly signed compass is worth

### 2.1 The first measurement, and why it is a floor

Installed directly on the seven committed `W4b-801` Pioneer bests (the population of RBT-23's
no-regrowth twelve-item world, `docs/artifacts/RBT-23-W4b-801/`), 64 paired seeds from 9000:

| circuit | `a` | Δ items | 95% CI over robots | robots improved | file |
|---|---|---|---|---|---|
| compass, w = 8 | 16 | +0.054 | [−0.040, +0.158] | 3/7 | readout [P2] |
| compass, w = 16 | 32 | +0.246 | [+0.147, +0.353] | 7/7 | readout [P3] |
| **compass, w = 32** | **64** | **+0.897** | **[+0.632, +1.176]** | **7/7** | JSON [P6–P8] |
| pirouette, w = 32 | ~0 | −1.502 | [−1.614, −1.375] | 0/7 | readout [P4] |

Baseline **1.516** items [P5]; the a = 64 row is **+59%** of it [P9]. The a = 64 row and the
baseline recompute from `docs/artifacts/RBT-67/seedset_anchor.json`, where RBT-67's
independently written ladder harness reproduced the source's per-robot deltas to the last
printed decimal; the other three rows are printed readouts with no per-bout data behind them
on the branch (`verify_independent-rerun.txt`).

**The +59% is a floor, not the prize.** RBT-67 extended the ladder to a = 384 on seeds 7000
onward (`docs/artifacts/RBT-67/w4b.json`):

| a | 32 | 64 | 96 | 128 | 192 | 256 | 384 |
|---|---|---|---|---|---|---|---|
| Δ items, W4b-801 (baseline 1.270) | +0.435 | +1.018 | +1.333 | +1.413 | +1.627 | +1.634 | **+1.875** |

All seven robots improve at every rung [P14, P17]; at a = 384 the interval over robots is
**[+1.243, +2.438]**, **+148%** of baseline [P15, P16]. No turnover was found inside the
range, against a pre-registered prediction that it would peak and turn over at 96 or 128
(confidence 0.60; RBT-67, `docs/artifacts/RBT-67/PREREGISTRATION.md`). The two baselines
differ by a quarter of an item (1.516 on seeds 9000+, 1.270 on 7000+) and RBT-67 showed that
difference is the seed set and nothing else: its own `bout()` on seeds 9000–9063 returns
1.516 and +0.897 exactly (`docs/artifacts/RBT-67/seedset_anchor.txt`). Anyone comparing two
64-seed baselines across tickets should remember that a quarter of an item is the size of that
effect.

### 2.2 The mechanism is steering, and the evidence for it is the phantom

Items per in-disc metre rise on a flat path (RBT-67 §3), which is consistent with steering and
does not establish it, because path *shape* alone moves that rate by 2.07× at pinned length
(RBT-39, `runs/RBT-39/shape_at_constant_length.txt`). What establishes it is the manipulation
check at the top of the ladder (`docs/artifacts/RBT-67/manipulation_384.json`):

| condition | Δ items | bearing to smell ascent (rad) | distance to live-item centroid (m) |
|---|---|---|---|
| base | — | 1.534 | 2.83 |
| compass, a = 64 | +1.018 | 1.347 | 2.32 |
| compass, a = 384 | **+1.875** | **1.265** | **2.02** |
| phantom smell, a = 64 | +0.257 | 1.449 | 2.33 |
| **phantom smell, a = 384** | **−0.217** | 1.512 | 1.95 |
| antimotif, a = 384 | −1.094 | 2.084 | 5.08 |

[P22–P26]. With the noses fed a decoy layout and the real items left in place, the whole gain
at a = 384 is gone. Aim at the smell ascent and distance to the centroid both improve
monotonically with gain; neither carries a heading convention. At a = 64 the phantom keeps a
residual **+0.257** of the +1.018.

The earlier phantom figure quoted in this strand's founding documents does not re-derive. A
*"yoked phantom-food control"* at a = 64 on seeds 9000+ is reported as **+0.163**, and the
taxis-specific gain as *"+0.723, +48%"* (paper 7 §3.7; `runs/sim-audit/CHAOTIC-DOC.md`; the
RBT-72 ticket). No script or readout for that control is committed [P10]; and the subtraction
itself is **0.897 − 0.163 = +0.734, +48.4%**, not +0.723 [P11, P12]. The +0.723 should not be
quoted again. The a = 64 phantom that *is* on the branch is RBT-67's +0.257, on different seeds.

### 2.3 The sign belongs to the population, and it sorts individual robots

Nothing in a foraging ecology rewards driving nose-first over tail-first, so each lineage
settles on a direction of travel by accident. The `W4b-801` bests drive **backward**, pooled
travel offset **−174.1°, R = 0.756**, all seven [P35]
(`docs/artifacts/RBT-23-W4b-801/travel_direction.txt`). The persistent world's `P-801` bests
drive forward on balance, pooled **+12.0°, R = 0.430**, five forward and two backward (gens
100 and 400) [P34] (`docs/runs/RBT-69-travel-direction.txt`). A motif that is a compass for a
backward driver is an anti-compass for a forward one.

That one parameter explains the whole of RBT-69's apparent non-replication. Installed on
`P-801` with the **W4b sign**, the motif at w = 16 and w = 32 reads **−1.154** and **−0.549**
[P27, P28]. Split by each robot's own direction at w = 32, the five forward drivers average
**−1.738, 1 of 5 improved**, and the two backward drivers **+2.422, 2 of 2** [P31–P33]; the
−0.549 is five anti-compasses averaged with two compasses. And with **each population's own
sign**, RBT-67's ladder on `P-801` (`docs/artifacts/RBT-67/p801.json`):

| a | 32 | 64 | 384 |
|---|---|---|---|
| five forward drivers (baseline 2.688 [P20b]) | +1.009, 5/5 | **+3.206, 5/5** | **+8.094, 5/5** (+301%) |
| two backward drivers | −1.430 | −1.594 | −2.211 |

[P19, P20]. The two backward drivers are negative at **12 of 12** robot-rungs from a = 64 up,
as RBT-67 pre-registered from their measured direction [P21].

**So on both committed populations, a correctly signed direct compass pays from the first
paying rung upward, and pays more on the population the RBT-91 decision named as the one where it did not.** Any quoted
prize has to name its population and the sign it was installed at, and a population whose
members drive in both directions has no single compass sign at all.

### 2.4 What a population does with a compass it is handed

RBT-65 and RBT-80 seeded sixty `W4b-801` founders with the **routed** motif at w = 32 and ran
300 seasons against an unseeded control and an economy-flattened drift arm, on three evolution
seeds, reading the whole living population every ten seasons (RBT-80,
`docs/artifacts/RBT-80-*.txt`). Expected depth: 2 × 300 ÷ 60 = 10.

- **The control never evolves a compass.** Carriage **0.000** at the plateau under all three
  truncation depths on all three seeds [S3] (`RBT-80-three-seed-report.txt`), over about
  1,300 distinct genotypes.
- **The seeded arm out-earns its control** in mean lifetime score by **+0.432, +0.371, +0.373**
  over 300 seasons [S1] (recomputed from `RBT-80-series.txt`), and inside the seeded arm
  carriers out-earn non-carriers by **+1.144, +0.415, +0.499** [S5] (`RBT-80-within-arm.txt`).
  Both contrasts are observational. The dose-response across seeds is flat, and the
  discriminating control (a seeded arm wired to a food-irrelevant sensor) has not been run, so
  these are not cited as evidence that the routed compass *pays*; they are the reason §5's
  question is not idle.
- **Whether selection holds it: NO VERDICT** by the pre-registered rule. Seeded minus drift
  carriage at the plateau, depth 2: **+0.253, −0.030, +0.286** [S2]. HELD needed the same sign
  on all three seeds; NOT HELD needed |d| < 0.10 on two. The author's 0.7 prediction of HELD is
  falsified.
- Post hoc and consistent, not pre-registered: carriers lost to **direction inversion** run at
  **2.2 / 1.7 / 2.7** in the seeded arms against **17.3 / 12.2 / 18.0** under drift [S4]. The
  motif survives reproduction structurally (retention 0.989, `docs/artifacts/RBT-80-crossover-floor.txt`);
  what drift erodes is which way it points.

---

## 3. The proposal rate: how often drift builds the structure

### 3.1 The yardstick: six hundred seasons is about twenty mutations

`Ecology._breed` applies one `mutate_controller` per reproduction. Along first-parent chains,
the conventional individuals alive at season 599 of RBT-23's run sit at depth **median 19, max
23** [R1] (`runs/RBT-45/stats.txt`), and across the fourteen population-rows of the fan-out that
reached season 599 the median ranges **18 to 24** [R2] (`runs/RBT-59/depth.json`). Depth is
`2 × seasons ÷ max_age` (RBT-59) and shortening the lifespan to buy depth loses heritability and
yield together (RBT-60). Every rate below is quoted at this depth, nineteen mutations from
committed parents, unless it says otherwise.

### 3.2 What was counted, in the order it was counted

| ticket | predicate | instrument | at depth ~19 | what it turned out to count |
|---|---|---|---|---|
| RBT-45 | both wheel noses wired; "crossed" pair | `sensor_influence`: absolute weights, clipped at 3.0, paths to depth 4 | pair 0.091, crossed 0.013 of 2,000 [R0] | connectivity, sign-blind; the "crossed" pair is the pirouette (§7, W1) |
| RBT-45 §7 | signed path `a ≥ 32` | depth-4 signed path sum | **0.70%**; a ≥ 64 0.05% [R10] | a truncation of a divergent series (W4) |
| RBT-62 | both noses wired, evolved populations | PATH depth 4 / DIRECT depth 1 | **0/10/4** of 60 PATH, **0/5/0** DIRECT, at depths 23/39/78 [R3, R4] | the "7–17%" is the two non-zero PATH counts (6.7%, 16.7%); the baseline reads 0% [R5] |
| RBT-78 | direct four-link motif | depth-1 term | **0 of 10,000**, max `|a|` 3.232 / 3.333 [R8] | zero by construction on any routed circuit (RBT-87) |
| **RBT-91** | **routed-motif structure: a global unit fed by both noses at opposite sign, feeding both Effectors at the same sign; no magnitude** | predicate on summed weights; self-test 6 of 6 | **84 of 200,000 (0.042%)** [R15] | the structure itself |

The first four rows are each a correct count of something other than the compass drift could
build; §7 says what. The fifth is the first predicate that can see the routed motif and only
the routed motif, and it can say yes: it finds an installed motif 6 of 6 times across three
magnitudes and both signs and reads 0 on the bare parent
(`docs/artifacts/RBT-91-structural-rate.txt`).

### 3.3 The structure is proposed, rarely and unevenly

**54 of 100,000** lineages from the seven `W4b-801` bests and **30 of 100,000** from the sixty
`P-801` finals carry the structure after nineteen mutations [R15]
(`docs/artifacts/RBT-91-alone-baseline.txt`). About four in ten thousand. Two cautions on
reading that as a rate. Lineages cluster on their parents: at the first denominator of 10,000,
three of the four arrivals were `W4b-801` lineages 176, 2430 and 3550, all of index 1 mod 7, so
all from the one parent `ce556` [R16] (RBT-91's adversary). And RBT-45 measured the design
effect of cycling a fixed parent pool at 2 to 9, so binomial standard errors on counts drawn this way are too narrow by roughly its square
root, 1.5 to 3 (`runs/RBT-45/variance.json`). The re-run of this readout for this paper
reproduced it byte for byte (§8).

### 3.4 Structure is not direction

A predicate on shape cannot say whether the shape points at food; that depends on the carrier's
own direction of travel. Re-signing each of the 84 arrivals against its own measured direction
at RBT-80's reference probe (16 seeds × 15 s), with arrivals within 15° of sideways left
undetermined: **35 compasses, 48 anti-compasses, 1 undetermined**, **42.2% [32.1, 52.9]** of
the resolved [R17, R18] (`docs/artifacts/RBT-91-resigned-84-reference.txt`), and **41.7% to
42.9%** whichever way the undetermined arrival goes [R18b]. Against 0.5, z = **−1.43** [R19].
The null is 0.5 by the symmetry of the proposal: the motif's sign comes from freshly drawn and
randomly walking weights, and nothing couples it to the carrier's direction.

So the proposal rate of a *correctly signed* compass structure is about two in ten thousand
lineages of realistic depth. That is not zero, and §4 is about why it does not matter.

---

## 4. The magnitude gap

### 4.1 A single weight has a ceiling, and it is the operator's

`mutate_weights` touches each link weight with probability 0.25; a touched weight takes an
`N(0, 0.4)` step, or with probability 0.02 is redrawn from `N(0, 1)`. Nothing clamps it (read
from source, RBT-91). Per mutation, P(step) = 0.245 and P(reset) = 0.005, so the walk
equilibrates at variance `1 + σ²·P(step)/P(reset)` = **8.84**, rms **2.97** [M8]. The census of
every committed best on the branch agrees: **9,637 links, max |w| 5.200, none ≥ 8** [M11]
(`docs/artifacts/RBT-91-weight-census.txt`), and RBT-62's wider census over three search depths
agrees too: **19,892 links**, maxima **4.65 / 5.52 / 6.11** at depths 23 / 39 / 78, **none ≥ 8**
[M1–M3] (`runs/compass-gain/survey.log`; the A30 and A15 populations are not committed, so that
census re-derives from the printed log only). Run forward under `mutate_weights` with nothing
selecting, the committed bests reach the same ceiling at the same depth: the depth-20 drift row
reads max **4.835**, none ≥ 8 [M13]. The ceiling is not selection and not a clamp; it is the
reset.

The operator's asymptote, from the same readout at 20,000 mutations: **rms 3.016, 2.17% of
weights ≥ 8, 0.03% ≥ 16** [M12]. Two figures in `docs/rbt-91-weight-scale-decision.md` differ
from that readout: its table gives the asymptote as *rms 2.938, 1.96% ≥ 8* and the depth-20
drift maximum as *5.008*. The script re-runs byte-identical to the committed readout today
(§8), so the document's figures are from an earlier run of a different census and are flagged
here rather than used.

### 4.2 The motif's magnitude is a product, and its own links never reach the rung

A single weight is not the quantity a routed motif needs. Its linearised gain is
`a = (u_L − u_R)(v_L + v_R)/2 · sech²(b)`: four free weights and the interneuron's bias. At the
weight asymptote, four free weights clear |a| ≥ 32 in **1.32%** of draws with the bias ignored
and **0.055%** with it [M14]; from the committed bests' own weights and biases, **0 in 200,000**
[M15] (`docs/runs/RBT-91-adversary.txt`). The bias matters because it has no reset: its sd grows
as `0.2 · √depth` and the `tanh` slope collapses with it, median `sech²(b)` **0.735** at depth
20, **0.085** at 200 and **0.001** at 1,000 [M15b] (same readout). These are linear bounds. The realised response is smaller: an
installed routed motif at w = 8, linear 2w = 16, delivers a realised small-signal steering
response of **3.57** through the interneuron's and the Effector's `tanh`, a factor of **4.5**
[M16, M17]. The first paying rung for the direct motif (a = 32, +0.246 items) corresponds to an
installed routed motif at w = 16, whose realised response through the same probe is **6.87**;
RBT-91 scored every arrival against that reference.

Scored on **the motif unit's own four links with the rest of the brain silenced**, which is the
circuit under test:

| `weight_sigma` | structural arrivals | own links ≥ 6.87 | largest own-link response | structureless background, whole brain ≥ 6.87 |
|---|---|---|---|---|
| **0.4** (default) | 84 | **0 of 84** [0.0, 4.4] | 1.26 | 26 / 9,996 = **0.26%** |
| **1.6** (pre-registered) | 63 | **0 of 63** [0.0, 5.7] | 3.51 | 141 / 9,995 = **1.41%** |
| **4.0** (ten times, post hoc) | 66 | **0 of 66** [0.0, 5.5] | 3.91 | 164 / 9,994 = **1.64%** |

[M18–M20] (`docs/artifacts/RBT-91-alone-{baseline,1.6,4.0}.txt`). **No drift-proposed motif's
own circuit reaches the paying rung at any weight scale tested**; the largest anywhere is 3.91
against 6.87. The whole brain around them does reach it, 4 of 84, 4 of 63 and 4 of 66, and
that column is background: brains with **no motif at all** clear the same bar at 0.26% rising
six-fold to 1.64% as the scale widens, while the conditional fraction sits flat. What widening
pumps is the recurrent gain of every brain, not the circuit. It does so because `weight_sigma`
drives the bias step as well as the weight step (`genetics.py` lines 105 and 108) and the bias
walk has no reset: RBT-91's pre-registered prediction, made at confidence 0.6 before the run.

### 4.3 How far short

At the default scale the largest own-link response among 84 arrivals is 1.26: about a third of
the null rung's 3.57 and a fifth of the paying rung's 6.87. At ten times the scale the largest
is 3.91, just above the null rung and 57% of the paying one, and the median is 0.0000. In weight space the shortfall is what RBT-62 called "thirty times too small": the best
direct `|a|` in its 180-robot corpus is 1.053 against a paying 32 (`survey.log`). In
behaviour space the best evolved individual is about ten times short and the median has no
response at all (RBT-78's adversary, RBT-81). Neither "thirty times" nor "ten times" should be
quoted without its unit.

One unit problem is unresolved and should travel with every realised magnitude in this
section. Two calibrated small-signal probes exist and disagree by **2.32×** on nominally
comparable installs: RBT-91's probe reads a routed motif at w = 8 as 3.5657, and RBT-81's
adversary's probe reads a direct motif at w = 8 as 8.264 [M21, M22]
(`docs/runs/RBT-81-drive-spec.txt`). They differ in routing and possibly in whether they report
the Effector sum or the half-sum. Ratios inside one probe hold; no absolute magnitude should be
carried from one to the other until one motif of each routing has been read through both (§9).

---

## 5. Whether the prize exists for the circuit drift can build: RBT-97, pending

### 5.1 What is and is not on the record

§2 measured the **direct** motif's prize, and it is large on both populations once signed per
direction of travel. §3 and §4 measured the **routed** motif's proposal and magnitude. The
"paying rung" of 6.87 that every arrival in §4 is scored against is therefore a borrowed
number: the realised response of a routed install at w = 16, labelled as paying because the
*direct* motif pays +0.246 at the corresponding a = 32. Nobody has installed the routed motif
on these bodies at w = 8, 16 and 32 and measured what it earns. RBT-80's seeded arms carry it
at w = 32 and out-earn their controls (§2.4), but observationally, on one population, with a flat
dose-response. **Whether the compass drift can build pays at the magnitudes drift could reach
is the one measurement the decomposition lacks, and RBT-97 is making it.**

### 5.2 A note on RBT-97's stated premise

RBT-97's description, and the closing section of `docs/rbt-91-weight-scale-decision.md`, give
as the reason the prize may not exist that RBT-69 *"installed the corrected motif on P-801 and
measured it negative at every magnitude the source reports a gain at (−0.328 at w = 16, −0.375
at w = 32), with the world ruled out"*. On the committed files that reading is the one RBT-69
itself superseded. Those two numbers are the **W4b sign** installed on `P-801` robots in a
W4′-shaped world [P30] (`docs/runs/RBT-69-compass-replication-w4.txt`); `P-801` is five forward
drivers and two backward, so the W4b sign is an anti-compass for most of it, and the native-world
equivalent (−0.549 at w = 32) resolves into five anti-compasses and two compasses [P31–P33]. With
`P-801`'s own sign, RBT-67 measured the direct motif **positive on all five forward drivers from
a = 32 up** (§2.3). So the committed record does not show a correctly signed compass failing on
`P-801`; it shows the direct motif paying there. The live question is the one in §5.1, about the
routed motif, and it is a real one: routing passes the signal through an extra `tanh` and a bias
that drift walks, and the realised response of a routed install is 4.5 times below its linear
value (§4.2). This note is not a prediction of RBT-97's outcome. It is here so that whichever
way RBT-97 lands, its result is read against what the files show rather than against its
premise's sentence.

### 5.3 The outcomes, and what each does to this paper

RBT-97's verdict is per population, per rung: pays, null, or negative. The consequences below
are fixed now, before its numbers exist.

**(a) The routed motif pays on both populations at the rungs drift could reach (w ≤ 32).** The
decomposition closes and the title's answer is the one the abstract gives: the prize exists
for the circuit drift can build, the structure is proposed at about two correctly signed
arrivals in ten thousand lineages, and the magnitude gap is total at every operator scale
tested. The obstacle is then magnitude, and specifically magnitude that `weight_sigma` cannot
supply because it also walks the bias. The next operator question is a per-link gain or a
bias-reset, not a wider step and not a correlated-link operator (§6.2). §2.4's seeded-arm yields
become consistent with a mechanism rather than merely observational, though the food-irrelevant
seeded control would still be owed before they are cited as one.

**(b) It pays on one population and not the other.** The prize is a founding-population
property (the RBT-84 pattern), and the title's answer splits. On the paying population, as
(a). On the other, the null is the correct answer for that population, which is paper 6's
thesis restricted to it: evolution declined a circuit that does not pay. The paper would then
have to say which population property decides it, and direction of travel, having already
sorted individual robots for the direct motif (§2.3), is the first candidate to measure, not to
assume.

**(c) It is null or negative on both at w ≤ 32 while the direct motif pays (§2).** Then the
compass the encoding can express is not worth building at the magnitudes a search could reach,
and the title's answer changes from "the magnitude never arrives" to "the circuit that could
arrive does not pay". The magnitude gap of §4 stays true and becomes moot. The direct-motif
ladder of §2 becomes a statement about a circuit the genotype cannot hold, and the strand's
central number would have been the right answer to a question the robots were never asked.
The mechanism to look for first is the routing itself: the interneuron's `tanh` and its
bias-set operating point, which RBT-97's positive control on each body would have to rule out
before "does not pay" is read as a property of the world. On this outcome the compass question
on this world retires, as RBT-97's description says.

Whichever of these lands, the §7 catalogue and the §4 table stand; what moves is §0's
one-sentence answer and the abstract's last paragraph.

---

## 6. What this does to the operator questions

### 6.1 The order of the barriers

In the order the record now supports: the **prize** exists for the direct motif on both
populations (§2), pending for the routed motif (§5). The **proposal** of the routed structure is
non-zero, about four in ten thousand at depth 19, halved by the sign coin flip (§3). The **magnitude** of its own links never reaches the paying rung under any weight scale tested,
and at the default scale never reaches the null rung (§4). At the depth these runs reach, magnitude binds: no arrival's own circuit reached the rung in 213
arrivals over three weight scales, and at the default scale the upper end of the interval (4.4% of
84 arrivals) times the structural rate (0.042%) times the sign (0.42) bounds a correctly signed,
paying arrival below one in a hundred thousand lineages.

That is not the ordering this strand argued for during most of its life. RBT-91's first decision
ordered magnitude as the *smaller* barrier and structure the larger, on a structural rate ("0 of
10,000") produced by an instrument that could not see the routed motif; its second said the
magnitude was "not far away" on a whole-brain response that was not the motif's (§7, W9, W10).

### 6.2 Against RBT-42: operators that fix topology do not fix magnitude

RBT-42 proposes a correlated-link operator to raise the rate at which the compass's wiring is
proposed. On the record above it addresses the wrong barrier twice over. The routed structure
is already proposed (84 in 200,000), and what withholds a compass is that the structure arrives with an own-link response near zero
(links-alone median 0.05 and 0.02 on the two pools at the default scale, largest
1.26) and a walking bias, below the zone where the
direct motif at a = 16 is already null (+0.054, CI straddling zero, [P2]). A correlated-link operator would raise the count of inert circuits.
Two independent routes reached that conclusion before the routed-motif measurements existed
(RBT-62 §6; RBT-61's author on RBT-45), and the RBT-45 recommendation to "re-aim it at the
crossed pairing" is withdrawn because the crossed pairing is the pirouette (§7, W1).

The general point is sharper than RBT-62 made it. It is not only that a topology operator
leaves magnitude alone. **The operator parameter that is nominally about magnitude does not
supply it either**, because it is coupled to a second walk (the bias) that runs against the
motif. A search-space diagnosis that counts only wiring prescribes the wrong operator; one that
counts only weights prescribes the wrong parameter.

### 6.3 The pre-registered arm this paper was supposed to contain

RBT-62 §7 pre-registered an evolutionary arm at `weight_sigma = 2.0` on seeds 801–805, predicting
"still blind" at confidence 0.7, and RBT-72's description asked for this paper to contain it.
**It was never run.** RBT-91 measured the drift-form version of its question instead (does
widening move the proposal of usable motifs) at `weight_sigma` 1.6 and 4.0 and found it moves
nothing (§4.2); option B's evolutionary positive control was declined on that measurement, not
on cost. So the evolutionary prediction remains unscored, and the paper does not claim it.

---

## 7. What was withdrawn, and why

In the manner of paper 7 §3: each entry names the claim, the instrument or inference it rested
on, what that instrument could not see, and what replaced it. Every one was published on a
ticket or in a document before it fell. None is the fault of one author; several were withdrawn
by the author who made them.

| # | Claim, as published | Rested on | What it could not see | Replaced by |
|---|---|---|---|---|
| W1 | *"The crossed pairing — the only one that steers"* arrives in 1.3% of lineages; re-aim RBT-42 at it (RBT-45 §5) | `sensor_influence`, absolute and clipped; the textbook drive convention | the antiparallel axes: on this body the crossed pair is the pirouette | the four-link antisymmetric motif (RBT-45 correction 3; RBT-62) |
| W2 | *"The structural precondition is present in 7 to 17 percent… the bottleneck is not that the circuit is never proposed"* (`runs/compass-gain/SUPERSEDED-FINDING.md`) | the same absolute clipped sum | sign structure and magnitude | RBT-62's own correction, same day |
| W3 | *"The +0.897 is real and it is not chemotaxis"*; the published sign steers away from food (RBT-69, 19:22) | bearing against chassis yaw, calibrated on a designed forward driver | that the population drives backward (paper 7, E8) | travel-frame bearing and the phantom control (RBT-69, 20:47) |
| W4 | Drift proposes a paying compass in **0.70%** of realistic lineages (RBT-45 §7) | the depth-4 signed path sum | that the series diverges (ρ > 1 on every committed best) and an information-free sensor pair clears it at the same rate | the direct route (0 of 10,000) and, for the routed motif, the structural predicate (RBT-78, RBT-91) |
| W5 | P(paying direct motif) ≈ **10⁻⁷⁷** (RBT-62 §4) | a reset-free random walk and an arithmetic step | that the direct motif cannot be written in the genotype (RBT-87), that the walk has a stationary scale, and see §8 on the arithmetic | nothing; the direct motif's proposal rate is not a quantity drift can have |
| W6 | A typical link reaches w = 16 at **depth ≈ 6,500** (RBT-62 §4) | `σ(d) ≈ √(1 + 0.0392 d)`, which omits the reset | the stationary distribution: the walk stops growing near depth 1,000 at rms ≈ 3 | the operator asymptote (RBT-91 census; the RBT-89 delegate) |
| W7 | "Gradient-dominant" (`|a| > |c|`) individuals and arrival rates (RBT-62, RBT-45, RBT-78) | the criterion itself | that it is `s₁·s₂ < 0`, a sign test; admitted circuits had median balance 0.013–0.058 | balance ratio and sign reported separately (RBT-81) |
| W8 | Depth-1 `a` tracks the realised steering response at **r = +0.985** (RBT-78 adversary) | 14 committed bests | that 8 of 14 contribute (0, 0) | 1,519 wired lineages: sign 92%, magnitude r ≈ 0.00 (RBT-81) |
| W9 | Magnitude is the **smaller** barrier; widening removes it and leaves structure (RBT-91, 15:40) | "0 of 10,000" as the structural rate, and the installed motif's arithmetic as the evolved motif's | that RBT-78's instrument reads zero on the routed motif by construction | the structural predicate: 84 in 200,000 (RBT-91) |
| W10 | *"The magnitude is not far away"*: one arrival at **92% of the first paying rung** (RBT-91, 16:21) | the whole-brain small-signal response | that the brain, not the motif, carried it: the motif's own links read +0.0036, and the arrival was an anti-compass | the links-alone column, 0 of 84 (RBT-91) |
| W11 | *"Magnitude is reached by drift"* (RBT-91's pre-written outcome text) | the same whole-brain column | as W10 | not used; struck in the decision document |

Four more readings fell in the same month without being claims of this strand's result, and are
listed so the chain is complete: RBT-75's premise that *"the prize inverts between worlds"*
(it was direction of travel; RBT-75 cancelled); RBT-77's hypothesis that direction flips destroy
partial compasses faster than selection can fix them (refuted by its own race); RBT-91's
*"pays from a = 16"* (a = 16 is the null rung; corrected in its PR #52); and RBT-91's *"1 of 4
arrivals is a compass"* (small-sample noise; 35 of 83 at n = 84).

Two patterns, stated once. **Eight of the eleven** (W1–W4, W7, W8, W10, W11) are paper 7's
class exactly: a summary many-to-one in the direction the question turned on (absolute values,
a body-fixed frame, a truncated divergent series, a sign test, a denominator of zeros, a whole
brain standing in for one unit). **Three** (W5, W6, W9) are arithmetic done on the wrong object:
the installed motif's algebra applied to an evolved one, a motif the genotype cannot hold, or a
model of the operator with its reset left out. **Six were withdrawn by the person who made them**
(W1, W2, W3, W7, W8, W11); the other five by a peer or a named adversary. Every one was a
well-formed number with nothing wrong on its face, which is the reason §2 rests on the phantom
control and not on the item rate.

One number from the record still stands on a retired instrument and is flagged rather than
withdrawn: RBT-77's race, *"1 of 16 forty-mutation chains reaches |a| ≥ 16, peaking at 26.5 and
ending at 6.1"*, and its companion *"0 of 288 single mutations reach |a| ≥ 8"*, were read with
`scripts/compass_race.py` and `scripts/compass_vs_flip.py`, both at `DEPTH = 4`
(`docs/artifacts/RBT-23-W4b-801/compass_race.txt`, `compass_vs_flip.txt`) [S6, S7]. Paper 5 §6
quotes the race as "rarely reaches and does not retain". On a brain with ρ > 1 a depth-4 value
is not a gain (§1.4), and the single-mutation readout's parents (gens 140, 200, …) come from the
uncommitted RBT-23 run. The qualitative reading may survive; the numbers need re-reading at the
circuit's depth before anyone quotes them (§9).

---

## 8. Re-derivation, and what did not re-derive

`runs/RBT-72/rederive.py` recomputes 100 figures from 33 committed files; `runs/RBT-72/rederive.txt`
is its output. **77 match** at the precision they were quoted. **16** rest on printed readouts
with no data behind them on the branch (the verify-independent rows, RBT-69's tables, the
RBT-77 race, parts of RBT-62's survey log), and are read, and where they are arithmetic
recomputed, from those readouts. **One** rests on prose alone (the +0.163 phantom). **Six rows,
four figures, do not match**:

1. **+0.723 (+48%)**, the taxis-specific gain: 0.897 − 0.163 = **+0.734 (+48.4%)**, and the
   +0.163 has no script or readout on the branch [P10–P12]. Not used.
2. **10⁻⁷⁷**, RBT-62 §4: the report takes the four-link combination's SD as 2σ ≈ 3.4. With that
   SD, P(|a| ≥ 32) is about **10⁻¹⁹·⁹**. The quoted 10⁻⁷⁷ corresponds instead to SD = σ = 1.72,
   which is in fact the right SD for `a = (w₁ + w₂ − w₃ − w₄)/2` [M9, M10]. The number is
   therefore right and its stated derivation is not; and it is moot either way (W5).
3. **The operator asymptote** in the RBT-91 decision document (*rms 2.938, 1.96% ≥ 8*) against
   the committed readout (**3.016, 2.17%**) [M12].
4. **The depth-20 drift maximum** in the same document (*5.008*) against the readout (**4.835**)
   [M13]. Items 3 and 4 do not change the decision (0.03% ≥ 16 either way); the document should
   cite its own readout.

Reproducibility of the readouts themselves, from this branch with no bulk: `python
runs/RBT-91/weight_census.py` and `python runs/RBT-78/reconcile.py --n 5000 --workers 4`
re-run **byte-identical** to `docs/artifacts/RBT-91-weight-census.txt` and
`docs/runs/RBT-78-reconcile.txt` (about twenty seconds each, no simulation), and
`python runs/RBT-91/structural_rate.py --n 100000 --workers 4 --background 5000` re-runs
**byte-identical** to `docs/artifacts/RBT-91-alone-baseline.txt` (about nine minutes on four
cores, no simulation). So the §3 and §4 counts at the default scale reproduce from the branch
alone; the widened-scale readouts and the re-signing (which simulates each arrival's direction
of travel) were not re-run.

---

## 9. What is owed

No simulation was run for this paper. These are the readouts a complete version of it would
cite, none of which exists on the branch:

1. **The routed motif's payoff curve on both populations**, signed per individual (RBT-97, in
   progress). §5 is written against it.
2. **The two small-signal probes reconciled** on one direct and one routed install, so that the
   paying-rung reference (6.87) and RBT-81's calibration (8.264 at w = 8) are in one unit (§4.3).
3. **RBT-77's race and single-mutation acquisition re-read at the circuit's depth**, routed
   structure and links-alone response, from committed parents (§7).
4. **The a = 64 phantom on seeds 9000+** with a script and readout, or its figure retired from
   paper 7 §3.7 (§2.2).
5. **RBT-69's travel-frame manipulation check** (+0.835 → −0.071 under the phantom; bearing
   1.490 / 1.377 / 1.746): `scripts/compass_mechanism.py` is committed, its readout is not.
6. **The founders RBT-80 seeded and the RBT-23 final population** that RBT-45's grid and
   RBT-77's single-mutation readout drew from: committed nowhere (RBT-86).
7. **The A30-801 and A15-801 genotypes** behind RBT-62's 180-robot census, so M1–M4 re-derive
   from data rather than from `survey.log`.
8. **RBT-80's discriminating control**, a seeded arm wired to a food-irrelevant sensor, before
   §2.4's yields are cited as a mechanism.
9. **A behaviour-space readout of evolved steering** (RBT-83), with a positive control, so the
   population's realised gain can be quoted without a weight-space proxy.
10. **Any co-evolved body with a food nose on two parts**, or a generalisation of `a`/`c` to an
    arbitrary body's steering axis, before the one-body limit can be lifted.
11. **Figures.** The prize ladders (§2.1, §2.3) and the links-alone table (§4.2) can be drawn
    from `w4b.json`, `p801.json` and the three `alone` readouts as committed. A figure of the
    routed motif's prize against its realised response cannot be drawn until item 1 exists.

---

## 10. Conclusion

The programme spent ten world-variant arms asking whether its world rewarded a nose and
concluded, twice, that it did not. On this body it does: a correctly signed compass installed
directly into the controller earns more than the robot's whole baseline yield on one population
and three times it on another, and a phantom-smell control removes the gain. What evolution had
to reach it with was a mutation operator that builds the only compass its genotype can hold a
few times in ten thousand lineages, points it the right way half the time, and never makes its
own links strong enough to matter, at the default weight scale or at ten times it. Six hundred seasons is about twenty mutations deep, and at that depth no paying compass was
observed in 213 drift-proposed structures and fewer than one in a hundred thousand lineages is
the bound.

Whether that is the whole answer depends on a measurement being made as this is written: whether
the compass drift can build pays at the magnitudes drift could give it. If it does, the answer
is the magnitude gap. If it does not, the programme measured a large prize for a circuit its
robots could never have held, and the magnitude gap was true and beside the point.

Either way the record of how the answer was reached is worth as much as the answer. Eleven
claims were published and withdrawn in one month on this one question. Each was a well-formed
number from an instrument that could not see what the question turned on, or arithmetic done on
the wrong object, and five of the eleven fell only because someone other than their author was
asked to attack them.

---

## Sources

Every row cites the committed file its number re-derives from; `rederive.txt` row ids in brackets.

| Claim | File | Rows |
|---|---|---|
| Hinge axes antiparallel; the direct motif at a = 16 / 32; the pirouette −1.502 | `docs/artifacts/RBT-23-W4b-801/verify_independent-rerun.txt` | P1–P4 |
| Baseline 1.516, +0.897 [+0.632, +1.176], 7/7, +59% | `docs/artifacts/RBT-67/seedset_anchor.json` | P5–P9 |
| The +0.163 phantom and +0.723 (not re-derivable; arithmetic mismatch) | `runs/sim-audit/CHAOTIC-DOC.md` | P10–P12 |
| W4b ladder to a = 384, +1.875 [+1.243, +2.438], +148%, 7/7 at every rung | `docs/artifacts/RBT-67/w4b.json` | P13–P17 |
| P-801 own sign: forward five +1.009 / +3.206 / +8.094 on baseline 2.688, +301%; backward two negative 12/12 | `docs/artifacts/RBT-67/p801.json` | P18–P21, P20b |
| Phantom at 384 −0.217, at 64 +0.257; antimotif −1.094; bearing; centroid | `docs/artifacts/RBT-67/manipulation_384.json` | P22–P26 |
| P-801 with the W4b sign, native world (−1.154, −0.549; pirouette −2.710, 0/7) | `docs/runs/RBT-69-compass-replication.txt` | P27–P29 |
| P-801 with the W4b sign, W4′-shaped world (−0.328, −0.375) | `docs/runs/RBT-69-compass-replication-w4.txt` | P30 |
| Per-robot split by direction; P-801 pooled +12.0°, R 0.430 | `docs/runs/RBT-69-travel-direction.txt` | P31–P34 |
| W4b pooled −174.1°, R 0.756 | `docs/artifacts/RBT-23-W4b-801/travel_direction.txt` | P35 |
| RBT-45 grid: pair 0.091, "crossed" 0.013 at k = 19 | `runs/RBT-45/cells.json` | R0 |
| Depth median 19, max 23; fourteen rows 18–24 | `runs/RBT-45/stats.txt`; `runs/RBT-59/depth.json` | R1, R2 |
| RBT-62 topology counts, best direct 0.548, best path 16.257 | `runs/compass-gain/survey.log` | R3–R7 |
| RBT-78 direct route 0 of 10,000, max 3.232 / 3.333; path 0.44% / 0.36% | `docs/runs/RBT-78-reconcile.txt` | R8, R9 |
| RBT-45 0.70% / 0.05% (path, depth 4) | `runs/RBT-45/motif.json` | R10 |
| Truncation: 100% move, 544 / 358 | `docs/runs/RBT-78-truncation.txt` | R11, R12 |
| Depth-1 sign 1403/1519, magnitude r +0.0013 | `docs/runs/RBT-81-adversary.txt` | R13, R14 |
| 84 of 200,000 | `docs/artifacts/RBT-91-alone-baseline.txt` | R15 |
| First four arrivals, three from one parent | `docs/artifacts/RBT-91-structural-rate.txt` | R16 |
| 35 / 48 / 1; 42.2% [32.1, 52.9]; bounds 41.7–42.9%; z −1.43 | `docs/artifacts/RBT-91-resigned-84-reference.txt` | R17–R19 |
| 19,892 links, none ≥ 8, maxima; σ observed | `runs/compass-gain/survey.log` | M1–M4 |
| Operator arithmetic: 0.0392, σ(d), 6,505, variance 8.84 | `runs/RBT-91/weight_census.py`; `docs/artifacts/RBT-91-weight-census.txt` | M5–M8 |
| 10⁻⁷⁷ (derivation mismatch) | `runs/compass-gain/REPORT.md` §4 | M9, M10 |
| Census 9,637 links, max 5.200; asymptote; depth-20 drift | `docs/artifacts/RBT-91-weight-census.txt` | M11–M13 |
| Four free weights, bias, tanh slope | `docs/runs/RBT-91-adversary.txt` | M14, M15, M15b |
| Routed motif at w = 8 reads 3.5657 | `docs/artifacts/RBT-91-structural-rate.txt` | M16, M17 |
| Links alone 0/84, 0/63, 0/66 (213 arrivals); medians 0.05 / 0.02; the < 1e-5 bound; background 0.26% / 1.41% / 1.64% | `docs/artifacts/RBT-91-alone-{baseline,1.6,4.0}.txt` | M18–M20, M18b–d |
| The other probe: 8.264 / 32.236; 2.32× | `docs/runs/RBT-81-drive-spec.txt` | M21, M22 |
| RBT-80 yields, plateau contrasts, control 0.000, inversions, within-arm | `docs/artifacts/RBT-80-series.txt`, `-three-seed-report.txt`, `-within-arm.txt` | S1–S5 |
| RBT-77 race and single mutations (depth-4 instrument) | `docs/artifacts/RBT-23-W4b-801/compass_race.txt`, `compass_vs_flip.txt` | S6, S7 |
| Decomposition and the |a| = |c| identity; the survey's design | `runs/compass-gain/REPORT.md` | — |
| The routed motif; depth-1 zero by construction | RBT-87; `tests/test_steering_terms.py`; `scripts/genotype_motif.py` | — |
| The RBT-91 decision and its three restatements | `docs/rbt-91-weight-scale-decision.md` | — |
| Instrument taxonomy | `docs/paper-7-five-instruments.md` | — |
