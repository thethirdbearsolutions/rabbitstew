# RBT-74: morphological innovation protection on the arena, four seeds paired

**Verdict by the pre-registered rule: null.** Holistic mean champion fitness over the final fifth,
protected minus unprotected, paired by seed: **−0.062, +0.226, −0.057, +0.148**; mean **+0.064**,
range [−0.062, +0.226], **zero count 0** (|d| < 0.01), two positive and two negative. The rule
needed a mean of ±0.10 with three seeds agreeing; neither holds. My point prediction was a null at
confidence 0.65, and it was a null; its second clause, "every seed within ±0.10", is **wrong**: two
seeds sit outside it, both positive.

**The result that does not depend on the pairing** (section 6, within-run, both arms, every seed): a
body change costs 0.05–0.13 of bout score immediately, Cheney's premise on this substrate, and four
controller-only rounds recover none of it (−0.001 to −0.013 at age 4 against age 0, n = 882 per run).
The premise holds; the remedy does not act. The adversary (tp6zdu lead, 07:06 UTC) read this as the
report's strongest line, and it is.

**What the report is entitled to say, and what it is not.** It is not entitled to "the mechanism
does not help here". The four paired differences spread over ±0.15, so the smallest paired mean four
seeds could have resolved is about **0.15** (2 SE of the observed paired mean; from checkpoint noise
alone it would have been 0.05). The observed +0.064 lies inside that, so at four seeds *the instrument
cannot see an effect of this size*. And the instrument turns out to be measuring the wrong population
(section 4): the eight runs split cleanly by whether the **wheeled** side became a runaway driver,
not by arm.

Branch `claude/rbt-74-morphological-innovation-protection`; the mechanism is commit `a47e1b5`, the
run configurations `8f846ce`, this report and the readouts the commit that carries it. Pre-registration
posted on RBT-74 at 02:56 UTC before any run; the coordinator's confound note (03:29) and the
disambiguating arm (03:50) are on the ticket.

## 1. What was run

Exactly `docs/followup-paper.md` §7's command with the rich brain, one flag added on the protected arm:

    rabbitstew evolve --generations 250 --population 20 --duration 15 --mass-budget 15.34 \
        --conventional-topology --brain-model rich --terrain random \
        --champion-interval 5 --champions 5 --champion-mode roundrobin --seed S [--protect-morphology 4]

Seeds **201, 202, 203, 204**, both arms, eight runs, `scripts/rbt74_run.sh SEED prot|base`, all eight
concurrently on four cores at one worker each (about 3.7 h wall; the projected 14 CPU-hours were about
right). Rich brain because §4.6 found the paper-brain champion's links do nothing, and a mechanism whose
premise is control readapting to the body cannot act on a controller that does nothing. One relaunch
two minutes in, before the pre-registration's window closed, to log the birth type for the
conventional population too; the runs are deterministic, so the relaunched runs are the runs.

**The form** (Cheney, Bongard, SunSpiral & Lipson, ALIFE 2016 / J. R. Soc. Interface 2018, §III.B, the
explicit window; their own §III.C method is a parameter-free Pareto objective on morphological age):
a holistic child whose *body plan* (root, segments, connections with joint type, limit, axis, motor
mode, mirror and recursive limit, node graph; no units, links, weights or biases) differs from every
parent's is novel and starts at morphological age 0. While its age is below k = 4, its body plan is
guaranteed one child in the next generation, bred from its fittest carrier by a controller-only
operator (`mutate_brain`: weights, biases, oscillators, units, links; body plan asserted unchanged),
inheriting age + 1. From age 4 it competes like everyone else. Elitism and tournament selection are
untouched, founders are never protected, `--protect-morphology 0` is bit-identical to the previous
code (verified on a two-generation run). `tests/test_morph_protection.py` pins the exactly-k guarantee
and that a weight-only mutant is not shielded; 186 tests pass (177 on the checkout plus 9).

**k = 4**, single value, not tuned: the cycle period k + 1 = 5 equals the champion-bout interval, so
every checkpoint measures cohorts at the end of their window and the curve is not aliased by the
cycle. Why there is a cycle at all: the holistic operator changes the body plan in 1982 of 2000
children (99.1%), so every free-slot child is novel and the population alternates one body round with
four controller rounds. Measured on the runs: **every one** of the 4,482 free-slot births per baseline
run was novel (4,478 in base-201), and the protected runs bred 900 novel and 3,582 readaptation
children each, exactly the 1:4 the arithmetic gives.

## 2. Primary outcome: the pre-registered readout (`readout.txt`)

| run | final fifth | sd over its 11 checkpoints | holistic wins of 2550 | best checkpoint | fifths |
|---|---|---|---|---|---|
| base-201 | 0.469 | 0.180 | 456 | 0.74 (gen 130) | 0.32, 0.19, 0.39, 0.35, 0.47 |
| prot-201 | 0.407 | 0.173 | 389 | 0.74 (gen 245) | 0.33, 0.29, 0.37, 0.32, 0.41 |
| base-202 | 0.367 | 0.140 | 486 | 0.57 (gen 240) | 0.35, 0.32, 0.38, 0.27, 0.37 |
| prot-202 | **0.593** | 0.175 | **866** | **0.87 (gen 249)** | 0.37, 0.47, 0.46, 0.40, 0.59 |
| base-203 | 0.390 | 0.070 | 721 | 0.68 (gen 195) | 0.33, 0.36, 0.40, 0.52, 0.39 |
| prot-203 | 0.333 | 0.044 | 345 | 0.54 (gen 0) | 0.37, 0.31, 0.34, 0.38, 0.33 |
| base-204 | 0.326 | 0.119 | 695 | 0.61 (gen 145) | 0.46, 0.41, 0.33, 0.29, 0.33 |
| prot-204 | **0.474** | 0.185 | **956** | **0.88 (gen 170)** | 0.36, 0.43, 0.51, 0.54, 0.47 |

| seed | final fifth, prot − base | wins, prot − base | best checkpoint, prot − base |
|---|---|---|---|
| 201 | **−0.062** | −67 | 0.00 |
| 202 | **+0.226** | +380 | +0.29 |
| 203 | **−0.057** | −376 | −0.14 |
| 204 | **+0.148** | +261 | +0.27 |
| mean | +0.064 (SE 0.073) | +50 | +0.10 |

Zero count 0, positive 2, negative 2. Verdict **null**; neither "helps" (mean ≥ +0.10 and ≥ 3 positive)
nor "hurts" (mean ≤ −0.10 and ≥ 3 negative) is met.

**Instrument check, as pre-committed.** The unprotected arm's checkpoint-to-checkpoint SD within the
final fifth is 0.127 (mean over seeds), so an 11-checkpoint mean has SD 0.038, a paired difference of
two such means SD 0.054, and four such pairs resolve a mean of **0.054** at 2 SE if checkpoint noise
were the only noise. It is not: the observed spread of the four paired differences gives 2 SE =
**0.146**. Seed-to-seed drift is three times the checkpoint noise. The observed +0.064 is inside the
second figure, so this design could not have seen an effect below about 0.15, and the null is a
statement about the instrument's reach, not about the mechanism. For scale, the two positive seeds'
protected runs produced the two highest final-fifth values (0.59, 0.47) and the two highest
best-checkpoints (0.87, 0.88) in this family's random-terrain history; the paper's best was 0.65 by
fifths and 0.92 at one checkpoint.

## 3. The champion curves, and where the pairing broke

Per-checkpoint holistic mean fitness swings 0.1 to 0.8 within every run (readout section 2's SDs of
0.04 to 0.19 per run), which is the RBT-71 point in the arena's own numbers. In seeds 202 and 204 the
protected run is above its baseline at most checkpoints from generation 45 and 95 on; in 201 and 203
the sign flips checkpoint to checkpoint.

**Pairing by seed pairs the founders, not the runs.** Both populations of a run draw from one RNG
stream, and the protected arm's reproduction consumes it differently, so from generation 1 the
protected run's *wheeled* population, terrain seeds and start sides are a different random realisation
from the baseline's. Nothing in the holistic mechanism can reach the wheeled side except through those
draws, so the wheeled populations of the two arms are independent draws of the same process. I did not
foresee this when I pre-registered the pairing; it is the design's largest limitation and it decides
the reading of section 2.

## 4. The opponent decides the bout score (`toolkit.txt`)

The wheeled population's final-fifth bests measured alone, against the holistic final-fifth champion
fitness of the same run:

| run | wheeled approach, mean of 11 bests (m) | wheeled steering of 3 | holistic final fifth | holistic wins |
|---|---|---|---|---|
| base-201 | **−19.08** (runaway) | 0.00 | 0.469 | 456 |
| prot-204 | **−13.42** (runaway) | 0.00 | 0.474 | 956 |
| prot-202 | **−7.72** (runaway) | 0.64 | 0.593 | 866 |
| prot-201 | **−6.97** (runaway) | 0.27 | 0.407 | 389 |
| base-203 | +1.05 | 1.55 | 0.390 | 721 |
| base-204 | +1.48 | 2.18 | 0.326 | 695 |
| base-202 | +1.82 | 2.00 | 0.367 | 486 |
| prot-203 | +1.84 | 2.73 | 0.333 | 345 |

Four of eight wheeled populations ended as the §4.5 runaway (full throttle, straight through the goal
and on; the toolkit's approach trial reads −7 to −21 m). Those four runs have holistic final fifths of
0.41–0.59 (mean **0.486**); the four whose wheeled side still drives and steers have 0.33–0.39 (mean
**0.354**). The split is by opponent, not by arm, and **three of the four runaways happen to be
protected runs**, which is a 0.24-probability draw under no effect. The two "positive" seeds are the
two protected runs that drew a runaway opponent while their baselines did not; seed 203, the largest
negative on wins (−376), is the protected run that drew the *best* wheeled driver in the family
(steering 2.73 of 3) while its baseline drew a mediocre one. On the arena's instrument, protection's
paired difference is mostly which wheeled controller the run happened to evolve.

**Priced by the adversary** (tp6zdu lead, `runs/RBT-74/adversary.py`, `docs/runs/RBT-74-adversary.txt`
on their commit `79b952e`; reproduced my readout to four places first): the paired SE is **0.0729**
against an unpaired SE of **0.0628**, because the two arms' final fifths correlate at **−0.41** across
seeds, so pairing cost precision here rather than buying it, which is the signature of a dominant
variable assigned independently within each pair. Opponent composition alone (75% runaway in the
protected arm, 25% in the baseline, a 0.132 gap between the two opponent classes) predicts a paired
difference of **+0.066** against the observed +0.064. Adjusting for the opponent gives **−0.003**
(stratified on the runaway/driving label) or **+0.044** (opponent approach as a continuous covariate,
holistic = 0.382 − 0.0074 × approach, r = −0.67); the two disagree at n = 8 and neither is claimed,
but every adjusted estimate is below the pre-registered +0.10 and below the 0.146 resolution. The
null holds under all of them.

## 5. Secondary, pre-registered: what the holistic champions are, alone from rest

Final bests at generation 249 (approach in 15 s on flat ground, fell, steering successes of 3, terrain
success of 6, block push, parts, mass, xy extent, height, units/links, driven effectors, essential
units, `toolkit.txt`):

| run | approach | fell | steer | terrain | push | parts | mass | extent | height | units/links | driven | essential |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base-201 h249 | +1.13 | y | 0/3 | 0.00 | 0.00 | 2 | 14.83 | 0.20 | 0.01 | 26/12 | 0 | 0 |
| prot-201 h249 | +0.49 | n | 0/3 | 0.00 | 0.00 | **16** | 15.34 | 0.21 | 0.18 | 184/65 | 9 | 0 |
| base-202 h249 | +1.24 | n | 0/3 | 0.00 | 0.05 | 6 | 15.34 | 0.40 | 0.24 | 32/16 | 3 | 5 |
| prot-202 h249 | +1.44 | y | **3/3** | **0.33** | 0.00 | 4 | 15.34 | 0.52 | 0.07 | 49/24 | 6 | 8 |
| base-203 h249 | +0.99 | y | 0/3 | 0.00 | 0.00 | 3 | 14.96 | 0.23 | 0.02 | 41/6 | 0 | 0 |
| prot-203 h249 | +0.83 | n | 0/3 | 0.00 | 0.00 | 3 | 15.34 | 0.26 | 0.14 | 27/6 | 0 | 0 |
| base-204 h249 | +0.81 | y | 0/3 | 0.00 | 0.00 | 2 | 15.34 | 0.19 | 0.02 | 30/21 | 3 | 0 |
| prot-204 h249 | +0.70 | y | 0/3 | 0.00 | 0.00 | 2 | 15.29 | 0.13 | 0.09 | 27/1 | 0 | 0 |

Paired, protected minus unprotected, holistic, mean over the 11 analysed bests of the final fifth:
approach **−0.30, −0.13, −0.11, −0.08 m** (four of four negative, mean −0.155); terrain success
**0.00, +0.18, 0.00, −0.06**. The protected champions are not more capable alone; on approach they are
slightly less so in every seed. Whatever moved the bout score in seeds 202 and 204, it was not a better
holistic body.

**One exception worth its own line.** The prot-202 final best steers to all three off-axis goals and
crosses two of six test terrains: four parts (a cylinder with a ball-jointed sphere, a slider sphere
and a fixed sphere), six driven effectors, eight essential units, mean steering 1.45 of 3 over its
final fifth. §4.5 reported that no holistic champion in any run reached an off-axis goal. This one
does, on one seed, under protection, and I make no claim that protection produced it. **Its lab**
(`lab-prot-202-h249.txt`, 12 fresh draws, the standing rule): intact it gains **+1.87 m**, arrives at
10.0 s, time at target **0.20**, hold fraction 0.59, which is over the rule's competence line; with
the environmental sensors blanked, or the local brains silenced, it gains **0.00 m**; lesioning the
ball-jointed sphere's target-direction sensor (unit 12, `target z`) drops it to +0.40 m and its
velocity sensor (unit 17) to +0.68 m; its two effectors (units 8, 9) are each essential; the global
brain and the oscillator are not. This is a sensor-driven goal-reacher, the first evolved body in the
arena series whose approach depends on a sensor, and it is the champion RBT-52's question should be
asked of.

The rest are the paper's lumps: two- and three-part bodies that gain 0.5–1.2 m by a constant-bias
servo flip or lurch (prot-204: one link, no driven effector, identical 1.296 m final distance on all six
terrains, i.e. terrain-independent), zero steering, zero essential units. prot-201's whole final
population is a sixteen-part body (all 20 members; base-201 has three such of 20): protection let a
large body take the population, at the mass cap, and it approaches 0.42 m on average, less than its
baseline's 0.72.

## 6. Manipulation check: does the mechanism do what it is named for? (`demography.txt`)

Child minus parent bout score, all generations:

| run | novel (body-changed) children: mean, share improved | readaptation children: mean, share improved | readapted lineage at age 4 minus itself at age 0: mean, share improved |
|---|---|---|---|
| base-201 | −0.065, 0.25 (n 4478) | — | — |
| prot-201 | −0.057, 0.27 (n 900) | −0.006, 0.41 (n 3582) | −0.013, 0.37 (n 882) |
| base-202 | −0.071, 0.23 | — | — |
| prot-202 | −0.135, 0.26 | −0.006, 0.48 | −0.005, 0.49 |
| base-203 | −0.063, 0.20 | — | — |
| prot-203 | −0.053, 0.15 | −0.001, 0.25 | −0.001, 0.26 |
| base-204 | −0.102, 0.26 | — | — |
| prot-204 | −0.057, 0.25 | −0.004, 0.40 | −0.012, 0.40 |

The mechanism's premise holds on this substrate: **a body change costs 0.05–0.13 of bout score
immediately**, and only a fifth to a quarter of body-changed children beat their parent. The shield
does what it says: every protected body was carried for exactly four controller rounds (900 novel
lineages per run, 882 reaching age 4; the rest were born in the last four generations). **The remedy
does not act**: four rounds of controller-only mutation recover, on average, nothing (−0.001 to
−0.013), with a quarter to a half of readaptation children improving on their parent and the rest
not. Controller mutation on these bodies is flat: it neither destroys the pairing the way a body
mutation does nor climbs anywhere in four steps. In Cheney's terms the overtakes never come.

Parent-offspring correlation of the bout score by birth type says the same thing from the other side
(`realised_heritability`'s all-pairs figure, then split): baseline holistic all pairs 0.16–0.33 (paper
3 reported 0.17–0.20 on these runs' predecessors; RBT-71's "zero" is its summary of "almost entirely
noise", not a disagreement), of which body-changed children alone 0.11–0.26 and elite copies
0.0–0.31; protected holistic all pairs 0.38–0.59, driven by readaptation children at **0.34–0.67**
while their body-changed children sit at 0.25 like the baseline's. A controller-only child inherits its
parent's score two to three times as well as a body-changing child does. Conventional 0.00–0.08
throughout. In seed 203 both holistic populations score exactly 0.5 in 9–15% of bouts (a non-mover
against a non-moving best); elsewhere under 3%.

## 7. Realised search depth (`depth.txt`), the first for an arena arm

For every member alive at generation 249, the first-parent chain to generation 0 (RBT-59's walk).
The chain is 249 steps by construction; what varies is what the steps are. Medians over the 20 alive
(ranges in parentheses are across those 20; they are tiny, because every population has coalesced):

| population | mutation events | body-change events | controller-only events | elite copies | first-parent founders | all-ancestor founders (toolkit) |
|---|---|---|---|---|---|---|
| base-201 holistic | 157 (156–161) | 157 | 0 | 92 | 1 | 4 |
| base-202 holistic | 146 (144–147) | 146 | 0 | 103 | 1 | 2 |
| base-203 holistic | 166 (164–167) | 166 | 0 | 82 | 1 | 6 |
| base-204 holistic | 159 (157–160) | 159 | 0 | 90 | 1 | 7 |
| prot-201 holistic | 203 (197–218) | **46** | 157 | 46 | 1 | 7 |
| prot-202 holistic | 166 (163–167) | **41** | 124 | 83 | 1 | 4 |
| prot-203 holistic | 189 (187–193) | **47** | 142 | 60 | 1 | 5 |
| prot-204 holistic | 190 (186–205) | **47** | 143 | 59 | 1 | 4 |
| conventional, 8 runs | 206–228 | 0 | all | 21–43 | 1 | 2–8 |

Against the pre-registration: unprotected mutation depth **146–166**, *below* the predicted 190–230,
because a third to two fifths of every surviving chain is elite copies (the best sits and copies
itself; 82–103 of 249 steps); protected body-change depth **41–47**, inside the predicted 40–50;
protected controller-only depth 124–157, just under the predicted 150–200; conventional 206–228, inside
190–230. First-parent founders **1 in all sixteen populations** against the predicted 2–8: every
population is one first-parent lineage by generation 249, and the paper's 2–6 founders are the
all-ancestor count through crossover's second parents (2–8 here, same definition, same range).
Evaluations per individual: one bout per generation, as stated.

So the arena's body search, unprotected, is about **150 sequential body mutations deep** in 250
generations, and protection makes it **3.5× shallower in bodies** (41–47) while adding ~140
controller-only steps that section 6 shows go nowhere on average. That is the trade the mechanism
buys here, stated before the run and measured after it.

## 8. A1/A2 guards, confirmed from each run's `config.json` and the toolkit

`sim.synthesis.mass_budget = 15.34` and `sim.settle_time = 1.0` in all eight configs (`readout.txt`,
last two columns). Every final best masses 14.83–15.34 kg; the largest holistic bodies (prot-201's
sixteen parts) sit exactly at the cap. Champions were re-measured alone from rest by the toolkit's
solo trials (same config, so the same settling second and budget); the approach numbers in section 5
are from rest, and the biggest bodies approach least. Neither the 2016 mass artefact nor the spawn-drop
artefact is in these runs.

## 9. Predictions scored

| pre-registered | outcome |
|---|---|
| verdict null, confidence 0.65 | **null** |
| mean paired difference +0.02, every seed within ±0.10 | mean +0.064; **two seeds outside ±0.10** (+0.226, +0.148): wrong |
| protected body-change depth 40–50 | 41–47: right |
| unprotected mutation depth 190–230 | 146–166: **wrong**, elite copies are a third of the chain |
| founders 2–8 (first-parent) | 1 in every population: **wrong**; all-ancestor 2–8 matches the paper |
| the cycle of period 5 | exact, every run |
| coordinator's confound (shield vs operator) | not separable here, and now moot until the opponent is held fixed |

## 10. What this buys, and what next

- The field's prescribed control has been run on strand 1, pre-registered, four seeds paired, and it
  **does not close the gap on this instrument at this n**. RBT-73 can say so, with the qualifier that
  the instrument could not have resolved an effect under about 0.15 and that its between-run variance
  is the wheeled opponent's, not the holistic side's.
- The mechanism's premise (body change costs immediately) is confirmed on this encoding; its remedy
  (controller readaptation) has no gradient to climb in four rounds. That is a finding about the
  controllers, consistent with §4.5–4.6: bodies that move by constant bias have nothing for a
  controller mutation to tune.
- **Follow-up 1, the one that matters: hold the opponent fixed.** Give each population and the terrain
  its own RNG stream (three seeded generators instead of one), so a protected and an unprotected run at
  the same seed meet the *same* wheeled population on the same terrains. Cost: the same eight runs,
  3.7 h. Without it no arena arm can be paired, this one included, and the disambiguating arm the
  coordinator asked for would inherit the same confound. Per the adversary, separate streams make
  the opponent shared, not constant: whether a wheeled population goes runaway stays a coin flip, now
  the same flip on both sides. So the next arm pre-registers **the wheeled side's final-fifth solo
  approach as a covariate, reported whether or not it helps**, and reads the holistic score against
  it rather than discovering it afterwards.
- Follow-up 2, the disambiguating arm (cadence-matched controller-only rounds, no shield), is not
  triggered by the rule (null) and would be uninterpretable before follow-up 1.
- Follow-up 3: the prot-202 steering champion is the first holistic champion in the series to reach
  off-axis goals; its lab is in this directory, and it is a candidate for RBT-52's question.
- Not triggered: the paper-brain arm.

Instrument hygiene (protocol II): frame, the arena's own bout score and the toolkit's solo trials,
both established; calibration against a known case, **not done** for the bout score (no known-good
holistic body exists to install; the runaway split in section 4 is the post hoc calibration and it
found the instrument reading the opponent); manipulation check, done (section 6); measurement,
sections 2 and 5. What the summary step collapses: the paired bout difference collapses two wheeled
populations into one "opponent".

## Files

`readout.py` / `readout.txt` (primary outcome and instrument check), `toolkit.py` / `toolkit.txt`
(solo trials, structure, heritability), `depth.py` / `depth.txt` (search depth), `demography.py` /
`demography.txt` (manipulation check), `lab-prot-202-h249.txt` (the steering champion's lab),
`scripts/rbt74_run.sh` (the runs), the eight `config.json`. Bulk output (`history.json`,
`lineage.jsonl`, `analysis.json`, genotypes) is on the machine that ran it and regenerable from the
configs; the runs are deterministic.
