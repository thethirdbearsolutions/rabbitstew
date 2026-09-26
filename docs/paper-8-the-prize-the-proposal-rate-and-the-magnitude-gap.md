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
alone, the text says that too. **Revised 2026-09-26 in answer to adversary round 1** (six must-fix
items F1–F6, five caveats C1–C5, all taken; RBT-72's ticket carries the answer) and to one error
of this paper's own found while answering it (§7, W14). RBT-97's first result is in §5 as
provisional. Sources: `docs/foraging-world.md`, `docs/rbt-91-weight-scale-decision.md`,
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
is set by the way each robot actually drives. On the first population a phantom-smell control
removes the whole gain, so it is chemotaxis; on the second, the same control reads
food-dependent at both rungs tested but is still under review (RBT-97), so that gain is stated
here as yield. On the first population the routed motif, the one the genotype can hold, pays at
the same rungs as the direct one. The proposal rate is not zero: a nineteen-mutation drift from
committed parents builds the routed motif's structure in **84 of 200,000** lineages, and on the
motif's own links those arrivals point toward food as often as a coin flip (**30 of 58**). The
magnitude gap is total: **not one** of those arrivals' own circuits reaches the response of
the first paying rung, at the operator's default weight scale or at four or ten times it,
while widening the scale inflates the recurrent gain of brains carrying no compass at all. So
on the record as of 2026-09-26, drift proposes the structure, never the magnitude, and no
change to the one operator parameter that should supply magnitude does so.

What the record does not yet contain is the routed motif's payoff on the second population,
and no ticket owns it (§9); nor has RBT-97's food-dependence result on that population closed.
§5 writes down what each of RBT-97's outcomes does to this paper before it closes.
Fourteen claims made in this strand during its month were withdrawn, three of them during this
paper's own review and one of those this paper's own; §7 lists them with the instrument each rested on, and four figures still quoted
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
and §4 is for the routed motif.** The bridge between them, a payoff curve for the routed motif, exists on W4b-801 only
(`docs/artifacts/RBT-23-W4b-801/genotype_motif.txt`, §5.1) and pays there at the same rungs as the
direct motif; on P-801 it does not exist.

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
| **compass, w = 32** | **64** | **+0.897** | **[+0.632, +1.176]**; t [+0.529, +1.266] | **7/7** | JSON [P6–P8, C1] |
| pirouette, w = 32 | ~0 | −1.502 | [−1.614, −1.375] | 0/7 | readout [P4] |

Baseline **1.516** items [P5]; the a = 64 row is **+59%** of it [P9]. The "95% CI over robots"
throughout §2 is the source tickets' bootstrap percentile interval over the seven robots; at n = 7
the t-interval is wider, and it is printed beside the bootstrap wherever this paper re-derived it
(round 1, C1). No sign changes. The a = 64 row and the
baseline recompute from `docs/artifacts/RBT-67/seedset_anchor.json`, where RBT-67's
independently written ladder harness reproduced the source's per-robot deltas to the last
printed decimal; the other three rows are printed readouts with no per-bout data behind them
on the branch (`verify_independent-rerun.txt`).

**The +59% is a floor, not the prize.** RBT-67 extended the ladder to a = 384 on seeds 7000
onward (`docs/artifacts/RBT-67/w4b.json`):

| a | 32 | 64 | 96 | 128 | 192 | 256 | 384 |
|---|---|---|---|---|---|---|---|
| Δ items, W4b-801 (baseline 1.270) | +0.435 | +1.018 | +1.333 | +1.413 | +1.627 | +1.634 | **+1.875** |

All seven robots improve at every rung [P14, P17]; at a = 384 the interval over robots is **[+1.243, +2.438]** by bootstrap and **[+1.062, +2.688]**
by t [C1], **+148%** of baseline [P15, P16]. No turnover was found inside the
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
at a = 384 is gone. The column that separates taxis from its control is the bearing to the smell
ascent, which improves monotonically with gain (1.534, 1.347, 1.265) and not under the phantom
(1.512); it carries no heading convention. The distance to the live-item centroid does **not**
discriminate: the phantom at a = 384 ends nearer the centroid (1.95 m) than the real compass
(2.02 m) while losing 0.217 items, so it is not used as evidence here (round 1, C2). At a = 64 the
phantom keeps a residual **+0.257** of the +1.018. **This control exists for W4b-801 only**
(`manipulation_384.json` carries `"population": "w4b"`; round 1, F2).

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

**So on both committed populations a correctly signed direct compass raises yield from the first
paying rung upward, and raises it most on the population the RBT-91 decision named as the one
where it did not.** On W4b-801 that gain is chemotaxis by the phantom control (§2.2). On P-801 it
is, on the record this paper cites as settled, **yield and not yet chemotaxis**: RBT-97's
phantom arm reads food-dependent at both rungs, provisionally, with a decoy bias still open (§5.3),
and until it closes the gait reading RBT-97 named (a rail fraction of 14.7% at a = 384, and
in-disc path falling while items per metre triple [K4]) is not excluded (round 1, F2). Any quoted
prize has to name its population and the sign it was installed at, and a population whose members
drive in both directions has no single compass sign at all.

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
  these are not cited as evidence that the routed compass *pays*. One more caution on them (round 1,
C3): most of the gap is present at **season 0**, before any selection, at **+0.774 / +0.498 /
+0.569**, falling to **+0.451 / +0.252 / +0.272** at the plateau [C3]. With the founders
uncommitted (§9), that season-0 gap is either the routed motif's immediate effect at w = 32 on
W4b founders, consistent with `genotype_motif.txt`'s +0.879 (§5.1), or a founder mismatch; nothing
on the branch separates the two.
- **Whether selection holds it: NO VERDICT** by the pre-registered rule. Seeded minus drift
  carriage at the plateau, depth 2: **+0.253, −0.030, +0.286** [S2]. HELD needed the same sign
  on all three seeds; NOT HELD needed |d| < 0.10 on two. The author's 0.7 prediction of HELD is
falsified. The arms also ran at different realised depths, about 11 mutations in the seeded arms
and **5.0** in the drift arms (`RBT-80-three-seed-report.txt` §1), so the contrast compares
retention at different depths; if anything that understates the inversion contrast below (round 1,
C4).
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
own direction of travel. RBT-91 re-signed each of the 84 arrivals against its own measured
direction at RBT-80's reference probe (16 seeds × 15 s), leaving arrivals within 15° of sideways
undetermined, and reported **35 compasses, 48 anti-compasses, 1 undetermined, 42.2% [32.1, 52.9]**
[R17, R18] (`docs/artifacts/RBT-91-resigned-84-reference.txt`). **That figure is a well-formed
number from the wrong instrument** (round 1, F3; §7, W12). `runs/RBT-91/resign_arrivals.py`
re-signs the **whole-brain** response, the quantity §4.2 retires as the motif's magnitude: its
"raw a" column equals the whole-brain column of the `alone` readout on **83 of 83** parsed rows
[F3a]. And its classifier calls anything not positive an anti-compass, so **5** arrivals whose
response prints as 0.0000 were counted as anti-compasses [F3b]. Excluding those gives 35 / 43,
44.9% [34.3, 55.9] [F3c].

Read on the circuit under test, the motif unit's own four links, re-signed by the same measured
direction, with arrivals whose own response is below 10⁻⁴ left unsigned:

| predicate | compass | anti | fraction, Wilson 95% |
|---|---|---|---|
| whole brain, zeros counted as anti (as committed) | 35 | 48 | 42.2% [32.1, 52.9] |
| whole brain, zeros excluded | 35 | 43 | 44.9% [34.3, 55.9] |
| **motif's own links, \|a\| ≥ 10⁻⁴** | **30** | **28** | **51.7% [39.2, 64.1]** |

[F3c, F3d] (the own-link values are from `docs/artifacts/RBT-91-alone-baseline.txt`; round 1's
`runs/RBT-72-adversary/probe_resign.txt` reaches the same counts with independent code). The two
signs agree on only **31 of 57** arrivals where both are non-zero [F3e]. The null is 0.5 by the
symmetry of the proposal (the motif's sign comes from freshly drawn and randomly walking weights,
and nothing couples it to the carrier's direction), and on the motif's own links the arrivals sit
on it. The coin flip survives and is cleaner; the committed z of −1.43 was never a finding.

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
20, **0.085** at 200 and **0.001** at 1,000 [M15b] (same readout). These are linear bounds.

**The rung, on the scale the arrivals are scored on.** `runs/RBT-91/structural_rate.py` hard-codes
the paying-rung reference as 6.8664 and no committed readout printed it. Round 1 measured it with
the same install, host (P-801 gen 590) and probe (`runs/RBT-72-adversary/probe_rung.txt`, re-run
byte-identical for this answer): **3.57 and 6.87 are the whole-brain responses** of an installed
routed motif at w = 8 and w = 16 [M16, G4], a host whose bare brain already reads +0.30 and whose
two signs read asymmetrically. The arrivals below are scored on **the motif's own links**, and on
that scale the installed motif reads **6.28 at w = 8 (the null rung) and 12.52 at w = 16 (the
paying rung)** [G3]. So the linear value 16 is attenuated **2.55×** by the motif's own `tanh`
units [G5], not the 4.5× the first draft gave; most of that 4.5× was the host brain damping it.
RBT-91's "realised against realised" was not like for like, and the correction runs in the
conservative direction: every zero below gets stronger.

Scored on **the motif unit's own four links with the rest of the brain silenced**, which is the
circuit under test, against both references:

| `weight_sigma` | structural arrivals | own links ≥ 6.87 (as committed) | own links ≥ 12.52 (like for like) | largest own-link response | structureless background, whole brain ≥ 6.87 |
|---|---|---|---|---|---|
| **0.4** (default) | 84 | **0 of 84** [0.0, 4.4] | **0 of 84** | 1.26 | 26 / 9,996 = **0.26%** |
| **1.6** (pre-registered) | 63 | **0 of 63** [0.0, 5.7] | **0 of 63** | 3.51 | 141 / 9,995 = **1.41%** |
| **4.0** (ten times, post hoc) | 66 | **0 of 66** [0.0, 5.5] | **0 of 66** | 3.91 | 164 / 9,994 = **1.64%** |

[M18–M20, G3] (`docs/artifacts/RBT-91-alone-{baseline,1.6,4.0}.txt`). **No drift-proposed motif's
own circuit reaches the paying rung at any weight scale tested**, on either reference; the largest
anywhere is 3.91, and it does not reach even the like-for-like null rung of 6.28.

The whole brain around the arrivals does clear the committed 6.87, in 4 of 84, 4 of 63 and 4 of
66, and the first draft called that column background. The same files say otherwise (round 1,
F5): the arrivals clear it **18.3×** more often than structureless lineages at the default scale
(one-sided Fisher **p ≈ 10⁻⁴**), **4.5×** at σ 1.6 (p 0.013) and **3.7×** at σ 4.0 (p 0.024) [F5].
The hits are **enriched, and not carried by the motif's own links**: at σ 0.4, three of the four
have own links at zero or of the opposite sign. The cause is unmeasured; that lineages which
acquire the structure carry more added links, and so more recurrence, is a candidate and not a
finding. What is measured is that widening the scale raises the **structureless** rate six-fold,
0.26% to 1.64%: it pumps the recurrent gain of every brain, not the circuit. It does so because
`weight_sigma` drives the bias step as well as the weight step (`genetics.py` lines 105 and 108)
and the bias walk has no reset, which was RBT-91's pre-registered prediction at confidence 0.6. One
more reading should not be quoted as a gain: the two largest whole-brain values at σ 4.0,
**+49.9994 and +50.0000** [F5b], are exactly what the probe returns when one drive Effector swings
rail to rail between the two drive signs at drive 0.01, a saturated reading and not a response.

### 4.3 How far short

On the like-for-like scale, the largest own-link response among the 84 default-scale arrivals,
1.26, is **20%** of the null rung and **10%** of the paying rung; at ten times the scale the
largest, 3.91, is **62%** of the null rung and **31%** of the paying rung, and the median is 0.0000
[G7]. In weight space the shortfall is what RBT-62 called "thirty times too small": the best direct
`|a|` in its 180-robot corpus is 1.053 against a paying 32 (`survey.log`). In behaviour space the
best evolved individual is about ten times short and the median has no response at all (RBT-78's
adversary, RBT-81). Neither "thirty times" nor "ten times" should be quoted without its unit.

**The two probes, partly reconciled.** The first draft reported that RBT-91's probe (3.5657 for a
routed motif at w = 8) and RBT-81's adversary's probe (8.264 for a direct motif at w = 8) disagree
by **2.32×** [M21, M22] (`docs/runs/RBT-81-drive-spec.txt`). Against the routed motif's own links
at w = 8, 6.28, the disagreement is **1.32×** [G6]: most of the 2.32× was the host brain, not the
probe. What remains is a routed motif's two `tanh` stages against a direct link, which should
attenuate it; no absolute magnitude should yet be carried between probes without saying which
motif and which scale (§9).

---

## 5. Whether the prize exists for the circuit drift can build, and RBT-97

*Revised 2026-09-26 in answer to adversary round 1 (F1, F2) and to an error of this paper's own.
The first draft said the routed motif's payoff had never been measured and that RBT-97 was
measuring it. The first is false on W4b-801; the second describes an arm nobody is running.*

### 5.1 What is on the record

§2 measured the **direct** motif's prize. §3 and §4 measured the **routed** motif's proposal
and magnitude. The bridge between them, what the routed motif earns, is **measured on W4b-801
and nowhere else**. `docs/artifacts/RBT-23-W4b-801/genotype_motif.txt` installs the routed motif
through the genotype on the seven W4b bests, 64 paired seeds, baseline 1.516, and reads **+0.114
[−0.020, +0.237], 5 of 7** at w = 8, **+0.277, 7 of 7** at w = 16 and **+0.879, 7 of 7** at
w = 32; the anti-signed routed motif at w = 32 reads **−1.020, 0 of 7** [G1, G2]. Those sit
beside the direct motif's +0.054, +0.246 and +0.897 on the same seeds (§2.1), so on W4b the
circuit drift can build pays at the same rungs as the one it cannot. The first draft of this
section said nobody had measured it; that was this paper's error, found while answering round 1
(RBT-97's adversary had cited the file, `runs/RBT-97/ADVERSARY.md` §1).

**On P-801 the routed motif has never been measured**, and no ticket now owns that measurement
(§9). The "paying rung" the arrivals of §4 are scored against was also read on a P-801 host
(gen 590) and, as round 1 found, on the whole brain rather than the motif's own links (§4.2, F4).
On P-801's forward drivers the direct ladder starts at a = 32, where it already pays +1.009, so
P-801's null rung is unmeasured too (round 1, C5).

### 5.2 RBT-97's premise, resolved twice independently

RBT-97's description, and the closing section of `docs/rbt-91-weight-scale-decision.md`, gave as
the reason the prize might not exist that RBT-69 *"installed the corrected motif on P-801 and
measured it negative at every magnitude the source reports a gain at (−0.328 at w = 16, −0.375
at w = 32), with the world ruled out"*. On the committed files that is RBT-69's reading from
before its own resolution: the two numbers are the **W4b sign** installed on P-801 robots in a
W4′-shaped world [P30], and P-801 is five forward drivers and two backward, so that sign is an
anti-compass for most of it [P31–P33]. With each robot's own sign the direct motif pays on every
robot. This paper's first draft said so in this section, and **RBT-97's author reached the same
finding independently at 12:28**, re-signing RBT-67's committed per-seed data per robot:
**12 of 12** correctly signed robots pay at every rung from a = 32 (+0.674 at a = 32), and the
two inverted robots lose at every rung [K3] (`docs/artifacts/RBT-97-rbt67-resigned.txt`, PR #71).
Round 1's adversary reproduced that table exactly. RBT-97's adversary adds two cautions that
belong here: "12 of 12" counts point estimates, and at a = 32 only 6 of 12 robots have their own
64-seed interval above zero; and the P-801 half of the result is for the direct motif, which drift
cannot build (`runs/RBT-97/ADVERSARY.md` §1).

### 5.3 What RBT-97 is measuring, and its provisional result

RBT-97 §2 asks whether the **direct** motif's gain on P-801 is food-dependent: the seven P-801
bests, each carrying its own sign, at a = 64 and 384, under base, motif, phantom smell and
anti-motif, 64 seeds. **Its first readout says food-dependent at both rungs**
(`docs/artifacts/RBT-97-p801-mechanism.txt`, PR #79) [K1, K2]:

| a | motif Δ | motif − phantom | phantom retains | pre-registered verdict |
|---|---|---|---|---|
| 64 | +2.982 | **+2.958 [+1.812, +4.158]** | **0.8%** | food-dependent |
| 384 | +6.962 | **+7.705 [+4.980, +10.201]** | **−10.7%** | food-dependent |

**This is provisional and is not cited as settled.** RBT-97 is open. Its adversary found that the
decoy is **static**: it never depletes while the real field loses what the robot eats (about 40%
of the crop at a = 384), so the phantom holds the robot at a persistent fake patch, a cost that
pushes retention toward the food-dependent verdict (`runs/RBT-97/ADVERSARY.md` §2d). Owed on
RBT-97 before its verdict can be read: a **rotated-layout (depleting) decoy** or RBT-39's
trajectory null beside the phantom, the **routed motif on P-801**, and its **round 2**.

### 5.4 RBT-97's outcomes, and what each does to this paper

Fixed now, before RBT-97 closes. Under every outcome §4's table and §7 stand.

**(a) Food-dependent on P-801, confirmed with a depleting decoy.** The restriction in the abstract,
§2.3 and §10 lifts: the prize is chemotaxis on both committed populations, not only yield on one.
The decomposition then closes on W4b fully (prize for the routed motif measured, §5.1) and on P-801
for the direct motif, with the routed motif's P-801 payoff still owed. The title's answer is the
magnitude gap: structure proposed at about two in ten thousand lineages, the motif's own links
never at the rung under any operator scale tested, and `weight_sigma` unable to supply magnitude
because it also walks the bias (§6.2).

**(b) A gait effect on P-801.** The prize is chemotaxis on W4b only, a founding-population property
(the RBT-84 pattern). The abstract's +8.094 and §10's "three times it on another" are withdrawn or
restated as "a yield effect that is not steering"; §2.3's last paragraph is rewritten; and the
routed-motif question becomes W4b-only, where §5.1 says it is already answered. On P-801 the null
is then paper 6's answer for that population: there was no compass there to be had.

**(c) Unresolved at RBT-97's n.** Stated as unresolved, at that n; the restriction stays.

Once RBT-97 closes, a small follow-up PR replaces §5.3 with its final result and keeps the branch
above that obtains.

---

## 6. What this does to the operator questions

### 6.1 The order of the barriers

In the order the record now supports: the **prize** exists for the direct motif on both
populations as yield, and as chemotaxis on W4b-801 (§2); for the routed motif it is measured on
W4b-801, where it pays at the same rungs, and unmeasured on P-801 (§5). The **proposal** of the routed structure is
non-zero, about four in ten thousand at depth 19, halved by the sign coin flip (§3). The **magnitude** of its own links never reaches the paying rung under any weight scale tested,
and at the default scale never reaches the null rung (§4). At the depth these runs reach, magnitude binds: no arrival's own circuit reached the rung in 213
arrivals over three weight scales, and the rate of a correctly signed, paying arrival is **of order 10⁻⁵ per lineage or below**. The
first draft called 7.7 × 10⁻⁶ a bound, but that multiplied one upper bound (4.4% of 84 arrivals) by
two point estimates (the structural rate and the sign). Taking each factor at its own upper end,
the structural rate with its interval widened by the √9 of RBT-45's design effect and the sign at
52.9% (whole brain) or 64.1% (own links), gives **1.6 × 10⁻⁵ to 1.9 × 10⁻⁵** [F6] (round 1, F6).
A joint bound has not been computed.

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
| W10 | *"The magnitude is not far away"*: one arrival at **92% of the first paying rung** (RBT-91, 16:21) | the whole-brain small-signal response | that the brain, not the motif, carried it: the motif's own links read +0.0036; and the arrival was called an anti-compass on the whole-brain sign, while by its own links (carrier driving backward) it is a compass | the links-alone column, 0 of 84 (RBT-91) |
| W11 | *"Magnitude is reached by drift"* (RBT-91's pre-written outcome text) | the same whole-brain column | as W10 | not used; struck in the decision document |
| W12 | **35 compasses, 48 anti-compasses: 42.2% [32.1, 52.9], z −1.43** (RBT-91's re-signing; this paper's first draft) | `resign_arrivals.py`, which re-signs the **whole-brain** response and calls a response of 0.0000 an anti-compass | the motif's own links, whose sign agrees with the whole brain's on 31 of 57 | the motif's own links re-signed: 30 / 28, 51.7% [39.2, 64.1] (round 1, F3; §3.4) |
| W13 | The paying rung is **6.87**, *"realised against realised"*, and the routed motif is attenuated **4.5×** through the `tanh` (RBT-91; this paper's first draft) | a whole-brain reading of the installed motif, compared with links-alone readings of the arrivals | that the host brain damps the installed motif: links alone it reads 6.28 and 12.52, and the attenuation is 2.55× | the like-for-like rungs (round 1, F4; §4.2) |
| W14 | *"The routed motif has never had its payoff measured on these bodies; RBT-97 is measuring it"* (this paper's first draft) | the RBT-97 description, read without checking the branch or RBT-97's approved design | `genotype_motif.txt`, which measures it on W4b-801, and RBT-97 §2, which measures the direct motif on P-801 | §5.1, §5.3 (this paper's own finding while answering round 1, and round 1, F1) |

Four more readings fell in the same month without being claims of this strand's result, and are
listed so the chain is complete: RBT-75's premise that *"the prize inverts between worlds"*
(it was direction of travel; RBT-75 cancelled); RBT-77's hypothesis that direction flips destroy
partial compasses faster than selection can fix them (refuted by its own race); RBT-91's
*"pays from a = 16"* (a = 16 is the null rung; corrected in its PR #52); and RBT-91's *"1 of 4
arrivals is a compass"* (small-sample noise; see W12 for what the n = 84 figure itself became).
Three sentences of this paper's first draft were also corrected in review and are recorded here
rather than in the table, because they were wording on correct numbers: that the whole-brain
hits among arrivals are "background" (they are enriched 18.3× and not carried by the motif; §4.2,
round 1 F5), that 7.7 × 10⁻⁶ is "the bound" (it multiplies an upper bound by point estimates;
§6.1, round 1 F6), and that the phantom control removes the gain "on both populations" (it
exists for W4b-801 only; §2.2, round 1 F2).

Three patterns, stated once. **Ten of the fourteen** (W1–W4, W7, W8, W10–W13) are paper 7's
class exactly: a summary many-to-one in the direction the question turned on (absolute values,
a body-fixed frame, a truncated divergent series, a sign test, a denominator of zeros, a whole
brain standing in for one unit, twice more in W12 and W13 after W10 had already named it).
**Three** (W5, W6, W9) are arithmetic done on the wrong object: the installed motif's algebra
applied to an evolved one, a motif the genotype cannot hold, or a model of the operator with its
reset left out. **One** (W14) is neither: a record read from a ticket's description instead of
from the branch, in a paper whose method is to read the branch. **Seven were withdrawn by the
person who made them** (W1, W2, W3, W7, W8, W11, W14); the other seven by a peer or a named
adversary. W12 and W13 are worth a sentence of their own: the whole-brain substitution W10
retired was still inside two of the instruments this paper re-derived and called matching, and
re-deriving a number from its file cannot see that the file holds the wrong quantity. Every one was a
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

`runs/RBT-72/rederive.py` recomputes 124 figures from 37 committed files; `runs/RBT-72/rederive.txt`
is its output. The rows added in answer to round 1 are the G, F, C and K rows. **91 match** at the
precision they were quoted. **26** rest on printed readouts with no data behind them on the
branch (the verify-independent rows, RBT-69's tables, the RBT-77 race, parts of RBT-62's survey
log, `genotype_motif.txt`, RBT-97's readouts and round 1's `probe_rung.txt`), and are read, and where
they are arithmetic recomputed, from those readouts. **1** rests on prose alone (the +0.163
phantom). A match here means the file says what the paper says; it does not mean the file holds
the right quantity, which is how W12 and W13 passed the first draft's re-derivation (§7). **Six rows,
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
cores, no simulation). Round 1's `runs/RBT-72-adversary/probe_rung.py` also re-runs byte-identical
to its readout (under a second). So the §3 and §4 counts at the default scale, and the
like-for-like rungs, reproduce from the branch alone; the widened-scale readouts and the
re-signing (which simulates each arrival's direction of travel) were not re-run.

---

## 9. What is owed

No simulation was run for this paper. These are the readouts a complete version of it would
cite, none of which exists on the branch:

1. **The routed motif's payoff curve on P-801**, signed per individual, at w = 8, 16 and 32.
   **No ticket owns it**; RBT-97 §2 measures the direct motif. The coordinator is asked to file
   it. It is the one missing bridge in §1.3 (on W4b-801 it exists, `genotype_motif.txt`).
2. **RBT-97's open items**: a rotated-layout (depleting) decoy or RBT-39's trajectory null beside
   the phantom, the routed motif on P-801 (item 1), and its adversary's round 2. §5.3 is
   provisional until they report.
3. **The probes reconciled to the end**: one direct and one routed install read through both
   probes, on both the whole-brain and the links-alone scale, so that the residual 1.32× (§4.3)
   is attributed; and `structural_rate.py`'s hard-coded 6.8664 printed in its readout.
4. **RBT-77's race and single-mutation acquisition re-read at the circuit's depth**, routed
   structure and links-alone response, from committed parents (§7).
5. **The a = 64 phantom on seeds 9000+** with a script and readout, or its figure retired from
   paper 7 §3.7 (§2.2).
6. **RBT-69's travel-frame manipulation check** (+0.835 → −0.071 under the phantom; bearing
   1.490 / 1.377 / 1.746): `scripts/compass_mechanism.py` is committed, its readout is not.
7. **The founders RBT-80 seeded and the RBT-23 final population** that RBT-45's grid and
   RBT-77's single-mutation readout drew from: committed nowhere (RBT-86). With RBT-80's founders
   on the branch, §2.4's season-0 gap could be split between the routed motif's immediate
   effect and a founder mismatch.
8. **The A30-801 and A15-801 genotypes** behind RBT-62's 180-robot census, so M1–M4 re-derive
   from data rather than from `survey.log`.
9. **RBT-80's discriminating control**, a seeded arm wired to a food-irrelevant sensor, before
   §2.4's yields are cited as a mechanism.
10. **A behaviour-space readout of evolved steering** (RBT-83), with a positive control, so the
   population's realised gain can be quoted without a weight-space proxy.
11. **Any co-evolved body with a food nose on two parts**, or a generalisation of `a`/`c` to an
    arbitrary body's steering axis, before the one-body limit can be lifted.
12. **Figures.** The prize ladders (§2.1, §2.3) and the links-alone table (§4.2) can be drawn
    from `w4b.json`, `p801.json` and the three `alone` readouts as committed. A figure of the
    routed motif's prize against its realised response can be drawn for W4b-801 from
    `genotype_motif.txt` and `probe_rung.txt`; for P-801 it waits on item 1.

---

## 10. Conclusion

The programme spent ten world-variant arms asking whether its world rewarded a nose and
concluded, twice, that it did not. On this body it does, at least on the population where the
control exists: a correctly signed compass installed directly into the controller earns more
than the robot's whole baseline yield there, a phantom-smell control removes the gain, and the
routed compass the genotype can hold pays at the same rungs. On the second population the direct
compass raises yield three-fold and a first phantom reading says it too is food-dependent, a
reading still under review. What evolution had
to reach it with was a mutation operator that builds the only compass its genotype can hold a
few times in ten thousand lineages, points it the right way half the time, and never makes its
own links strong enough to matter, at the default weight scale or at ten times it. Six hundred
seasons is about twenty mutations deep, and at that depth no paying compass was observed in 213
drift-proposed structures; the rate is of order 10⁻⁵ per lineage or below.

On W4b-801 that is the whole answer: the prize exists for the circuit drift can build, and the
magnitude gap withholds it. On P-801 two things are open, whether the direct compass's gain is
chemotaxis (RBT-97, provisional) and what the routed one earns (unowned). If both come back as
they did on W4b-801, the answer is the magnitude gap on both populations. If either does not,
the programme will have measured a large prize for a circuit that population's robots could not
have used, and the magnitude gap there was true and beside the point.

Either way the record of how the answer was reached is worth as much as the answer. Fourteen
claims were published and withdrawn in one month on this one question, one of them this paper's.
Each was a well-formed number from an instrument that could not see what the question turned
on, arithmetic done on the wrong object, or a record read from a description rather than the
branch; and seven of the fourteen fell only because someone other than their author was asked to
attack them.

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
| The re-signing re-read: whole-brain raw a 83/83, five zeros as anti; 35 / 43; own links 30 / 28, 51.7% [39.2, 64.1]; signs agree 31/57 | `docs/artifacts/RBT-91-resigned-84-reference.txt` with `docs/artifacts/RBT-91-alone-baseline.txt`; round 1's `runs/RBT-72-adversary/probe_resign.txt` | F3a–F3e |
| 19,892 links, none ≥ 8, maxima; σ observed | `runs/compass-gain/survey.log` | M1–M4 |
| Operator arithmetic: 0.0392, σ(d), 6,505, variance 8.84 | `runs/RBT-91/weight_census.py`; `docs/artifacts/RBT-91-weight-census.txt` | M5–M8 |
| 10⁻⁷⁷ (derivation mismatch) | `runs/compass-gain/REPORT.md` §4 | M9, M10 |
| Census 9,637 links, max 5.200; asymptote; depth-20 drift | `docs/artifacts/RBT-91-weight-census.txt` | M11–M13 |
| Four free weights, bias, tanh slope | `docs/runs/RBT-91-adversary.txt` | M14, M15, M15b |
| Routed motif at w = 8 reads 3.5657 | `docs/artifacts/RBT-91-structural-rate.txt` | M16, M17 |
| Links alone 0/84, 0/63, 0/66 (213 arrivals); medians 0.05 / 0.02; the < 1e-5 bound; background 0.26% / 1.41% / 1.64% | `docs/artifacts/RBT-91-alone-{baseline,1.6,4.0}.txt` | M18–M20, M18b–d |
| The other probe: 8.264 / 32.236; 2.32× | `docs/runs/RBT-81-drive-spec.txt` | M21, M22 |
| Routed motif payoff on W4b: +0.114 / +0.277 / +0.879, anti −1.020 | `docs/artifacts/RBT-23-W4b-801/genotype_motif.txt` | G1, G2 |
| Like-for-like rungs 6.28 / 12.52; whole-brain 6.8664; 2.55×; 1.32×; shares of the rungs | `runs/RBT-72-adversary/probe_rung.txt` (re-run byte-identical) | G3–G7 |
| Enrichment 18.3× / 4.5× / 3.7× and Fisher p; the two readings at 50 | `docs/artifacts/RBT-91-alone-{baseline,1.6,4.0}.txt` | F5, F5b |
| The per-lineage rate: 7.7 × 10⁻⁶ point product; 1.6–1.9 × 10⁻⁵ at the factors' upper ends | `docs/artifacts/RBT-91-alone-baseline.txt` | F6, M18c |
| t-intervals at n = 7 | `docs/artifacts/RBT-67/seedset_anchor.json`, `w4b.json` | C1 |
| RBT-80 season-0 and plateau gaps | `docs/artifacts/RBT-80-series.txt` | C3 |
| P-801 rail fraction, in-disc path, items per metre | `docs/artifacts/RBT-67/p801.json` | K4 |
| RBT-97 §2, P-801 phantom (provisional): +2.958 / +7.705; retains 0.8% / −10.7% | `docs/artifacts/RBT-97-p801-mechanism.txt` (PR #79) | K1, K2 |
| RBT-97 §1, RBT-67 re-signed per robot: 12/12 from a = 32 | `docs/artifacts/RBT-97-rbt67-resigned.txt` (PR #71) | K3 |
| RBT-97's open items (static decoy; 6 of 12 resolved at a = 32; routed motif never on P-801) | `runs/RBT-97/ADVERSARY.md` | — |
| Round 1 | Chaotic RBT-72, 12:55 UTC; `runs/RBT-72-adversary/` (PR #78) | — |
| RBT-80 yields, plateau contrasts, control 0.000, inversions, within-arm | `docs/artifacts/RBT-80-series.txt`, `-three-seed-report.txt`, `-within-arm.txt` | S1–S5 |
| RBT-77 race and single mutations (depth-4 instrument) | `docs/artifacts/RBT-23-W4b-801/compass_race.txt`, `compass_vs_flip.txt` | S6, S7 |
| Decomposition and the |a| = |c| identity; the survey's design | `runs/compass-gain/REPORT.md` | — |
| The routed motif; depth-1 zero by construction | RBT-87; `tests/test_steering_terms.py`; `scripts/genotype_motif.py` | — |
| The RBT-91 decision and its three restatements | `docs/rbt-91-weight-scale-decision.md` | — |
| Instrument taxonomy | `docs/paper-7-five-instruments.md` | — |
