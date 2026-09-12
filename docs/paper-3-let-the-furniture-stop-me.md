# A Failure of the Task to Demand Competence: Let the Furniture Stop Me

*Third paper in the Rabbitstew series. Draft. Reports what the evolved champions actually do, why the competitive task lets them get away with it, and sets out the experiment that would fix the task.*

## Abstract

We evolved robot bodies and brains against a designed wheeled body under the competitive task of the original Rabbitstew proposal, corrected for the two artefacts reported in the second paper, and then measured every champion alone. The wheeled champions win, and the way they win is to drive at full throttle in a straight line, cross the centre of the arena at about 1.7 seconds, and keep going; on the cluttered random terrain they were evolved on, obstacles near the centre stop them where the score is highest, and on open ground nothing does. The evolved champions move a metre or two on constant-torque joints and are stopped by the same clutter closer to their own side. No final champion of either population, in any of eight runs, reaches a goal placed off its initial heading. The task, as staged, does not reward steering, holding position, or sensing at all: a snapshot score, a fixed start facing the goal, and one noisy bout per generation against one opponent make "straight ahead and let the furniture stop me" a near-optimal policy. A comparison of body evolution against a designed body on such a task compares two ways of not steering. We set out a redesigned task that demands competence, pre-register what we expect it to change, and state what result would and would not support the original thesis.

## 1. What the champions do

Eight runs of 250 generations, four on random terrain resampled every generation and four on flat ground, all at equal mass, all starting from rest, all with the fixed body's controller topology free to evolve, under both the proposal's brain model and a rich one. In every run the designed wheeled body wins the champion bouts. Measured alone, the winners look like this.

**The wheeled champions are runaways.** Placed alone on flat ground facing a goal two metres ahead, the final champion of the rich-brain random-terrain run at seed 201 reaches the goal in 1.7 seconds and is 21 metres past it at the bell. The final champions of three of the four random-terrain runs do the same. On their own training terrain, drawn from the same distribution as the bouts, the same controllers finish within 0.1 to 0.7 metres of the centre, because a box, a dome or a rail near the centre catches them. Across a fixed bank of six test terrains and two starting sides, the same controller finishes near the centre in nine of twelve trials and runs off in three, in each case when the straight line ahead happened to be clear.

**The evolved champions crawl and topple.** Final holistic bests gain −0.1 to +1.8 metres towards the goal in 15 seconds. The ones that move do so on ball joints and sliders driven by effectors with no inputs at all, a constant bias holding a constant torque, and several fall over within the trial. Their controllers carry 18 to 159 units of which 12 to 39 percent are connected to anything, and 2 to 30 units whose lesion costs more than 10 centimetres of progress. Oscillators, position servos, proprioception and orientation sensing were available in half the runs; oscillators never came to drive an effector in any final best.

**Nobody steers.** Steering trials place the goal at 90, −90 and 180 degrees from the initial heading. No final holistic best in any run reaches any of the three. The wheeled champions reach them in many intermediate generations and, in three of four random-terrain runs, have lost the ability by the end, trading it for straight-line speed. In the fourth the final champion steers to all three and is also the slowest.

**Both populations are collapsed.** After 250 generations each final population descends from two to six of its twenty founders.

Every one of these facts is invisible in the champion curve, which shows the wheeled body winning by a comfortable margin in every case.

## 2. Why the task allows it

The bout, as the proposal staged it and as we ran it, has three properties that together make not steering optimal.

1. **The start is always the same.** Both robots begin two metres from the centre on opposite sides, facing it. Heading never has to be sensed or corrected; the goal is straight ahead at time zero and a controller that ignores every sensor and drives forward is already aimed.
2. **The score is a snapshot.** Fitness is the opponent's distance from the centre over the sum of both distances at the bell. Being near the centre at one instant is rewarded; arriving and staying is not required; overshooting costs nothing more than stopping short by the same amount. On cluttered ground the clutter turns a runaway into a stopper for free.
3. **One bout, one opponent, one draw of terrain.** Each individual is scored by a single bout against the previous generation's best on that generation's terrain. Fitness is one sample of a noisy variable, and the thing it rewards is whatever worked once against one body on one layout.

A fourth property is not a flaw in the score but in the gradient. Until a body can move at all it scores essentially zero against anything that can, and the zero-sum score gives it no partial credit for getting closer to moving. The designed body arrives moving. The evolved population has to cross that gap under a signal that only starts to discriminate once the gap is crossed, which is why its champions are the first thing that moved forward rather than the best thing that could.

None of this is specific to bodies. The wheeled body's evolving controller is subject to exactly the same pressures and responds the same way: it discards steering for speed. That is the point. The task does not demand competence of either side, so it cannot tell us which side would have it.

## 3. The redesigned task

Four changes, each aimed at one property above, all implemented as options in the simulator so that the earlier runs keep their meaning.

**Randomised start.** Each bout draws a start bearing and a start distance for both robots from the same distribution, so the goal is not straight ahead and a controller must sense and correct heading to reach it. Both robots in a bout share the draw; every bout in a generation shares the terrain.

**Time-at-target score.** Fitness is the fraction of the bout each robot spends within a radius of the target, and the zero-sum comparison is made on that. Arriving early and staying is rewarded; overshooting is not; a runaway scores nothing.

**Multi-opponent, multi-draw evaluation.** Each individual meets several opponents drawn from the other population's current top ranks, on several start and terrain draws, and its fitness is the mean. This trades bouts for signal and removes the single-opponent lottery.

**A locomotion phase for both populations.** For the first part of a run, fitness is solo: progress towards a goal and time at it, with no opponent. Competition begins once the population can move. The designed body already arrives able to move, so the phase levels a head start rather than adding one.

## 4. The experiment

Random terrain, resampled every generation from the distribution of the second paper. Equal mass. The fixed body's controller topology evolving. Two brain models. Population 60 rather than 20, with a descriptor archive over parts, mass and symmetry to keep locomotion strategies alive, since the lineage logs show collapse to a handful of founders within a hundred generations. Five hundred generations. Four seeds per condition. The analysis toolkit run on every tenth generation's best and on every checkpoint's champions, so that what evolves is measured alone throughout.

Three conditions, adding the changes one at a time so that each can be credited:

- **A.** Randomised start and time-at-target score.
- **B.** A plus multi-opponent, multi-draw evaluation.
- **C.** B plus the locomotion phase.

Pre-registered expectations. Under A the runaways disappear from both populations and steering successes rise above zero in the wheeled population within a hundred generations; we do not expect the holistic population to steer under A alone. Under B the seed spread of the champion curve narrows. Under C the holistic population's solo approach progress exceeds one metre in most seeds before competition begins, and its final champions steer in at least one goal direction. In none of the three do we expect the holistic population to win the champion bouts on this terrain distribution, because on ground a wheel can mostly cross a wheel is close to optimal and the evolved side has not, in any run so far, found a wheel.

What would support the original thesis is not a holistic win but a specific pattern: holistic champions that steer, hold position and cross terrain the wheeled champions cannot, with a champion curve that rises through the run rather than plateauing by generation 100. What would count against it is the pattern we have now, repeated under a task that demands competence: evolved bodies that move but do not control, losing to a body that does both.

## 4a. Condition A under the redesigned task (complete, eight seeds)

Condition A, random start and time-at-target score, 200 generations on random terrain, rich brains, equal mass, the fixed body's controller topology evolving, one opponent and one draw per generation as in the earlier runs. Eight seeds, 301 to 308, all to 200 generations. The two seeds below are given in full because they are the two the analysis toolkit was run over at every checkpoint; the other six are summarised at the end of the section and agree with seed 302.

| Seed | Holistic champion fitness by fifths (40 gens) | Holistic wins | Time at target, holistic / wheeled | Fresh-draw solo score of the holistic best, gens 0 / 50 / 100 / 150 / 199 | Same for the wheeled best |
|---|---|---|---|---|---|
| 301 | 0.11, 0.24, 0.51, 0.42, 0.53 | 704 of 2020 | 0.11 / 0.20 | 0.00 / 0.16 / 0.33 / 0.47 / 0.54 | 0.03 / 0.66 / 0.67 / 0.71 / 0.52 |
| 302 | 0.17, 0.09, 0.11, 0.14, 0.15 | 179 of 1866 | 0.00 / 0.22 | 0.00 / 0.00 / 0.01 / 0.00 / 0.00 | 0.09 / 0.64 / 0.60 / 0.65 / 0.69 |

The fresh-draw solo score is the time-at-target score of the generation's best on twelve fixed start-and-terrain draws it never trained on; it is the number that survives the winner's curse described in the fourth paper.

**The runaways are gone, on both sides.** With the score counting time at the target rather than a snapshot, the wheeled champions spend a fifth of every bout parked at the target and no longer drive through it. Under the old score no champion of either population held position.

**Seed 301 produced the first evolved robot in the series that steers.** Its holistic champion's fresh-draw score rises steadily through the run to 0.54, and the analysis toolkit finds a two-part, ball-jointed body (a box on a box; reflection was not enabled in this run, so its symmetry is the box's own) driven by two torque effectors and a 32-unit brain with four essential units, that reaches two of three goals placed off its heading, crosses four of six test terrains and moves at 0.8 m/s. Steering appears around generation 100 and is retained. The Pioneer in that run steered to all three goals for most of the run and had traded it away for straight-line drive by the end; it still won the head-to-head, 1316 to 704, but the last checkpoint was 0.65 for the holistic side.

**The lab on seed 301's champion (scripts/lab.py, docs/lab-A-301.txt, twelve fresh draws).** Two parts: an 11 kg box as root and a 4.3 kg box on a ball joint. Of 32 units and 18 links, three units matter: the second part's target-bearing sensor (lesioned: 0.52 to 0.01), the joint torque it drives at −5.25 (lesioned: 0.00), and a second constant-torque effector on the same joint (0.37). Every global unit, every other local neuron, the oscillator, the contact, velocity and opponent sensors are inert, and silencing the whole global brain changes nothing to two decimals. The one thing the earlier lesion maps could not see is on a link rather than a unit: the driven effector feeds back on itself at +2.76, which makes a tanh unit bistable. Intact, that effector sits saturated 92 percent of the bout and flips sign about twenty times; with the self-loop cut it saturates 60 percent, flips sixty times, and time at target falls from 0.52 to 0.10. The champion is a bang-bang steerer with hysteresis: the bearing sensor flips a latch, and the latch, not the sensor, holds the torque. That is one bit of state, held in an effector rather than a neuron, and the first memory of any kind found in an evolved controller in this series.

**Seed 302 produced nothing on the holistic side.** Its fresh-draw score is zero at every generation while its Pioneer became a competent goal-holder at 0.6 to 0.7. The difference between the seeds is whether the holistic search found a foothold, a body that moves towards the goal often enough to be selected, in the first fifty generations.

**The other six seeds are all seed 302.** Seeds 303 and 304 were run here, 305 to 308 by a delegate (Chaotic RBT-9). The eight together:

| Seed | Holistic fresh-draw time at target | Pioneer fresh-draw peak | Final champion bouts, holistic of 50 | Heritability, holistic / wheeled | Steers? |
|---|---|---|---|---|---|
| 301 | 0.00 → 0.54, rising throughout | 0.71 | – (last checkpoint 0.65) | – | **yes**, from about gen 100 |
| 302 | 0.00 to 0.01 | 0.69 | – | – | no |
| 303 | 0.00 to 0.01 | 0.69 | 0 | 0.02 / 0.08 | no |
| 304 | 0.00 to 0.01 | 0.64 | 2 | 0.05 / 0.05 | no |
| 305–308 | never above 0.02 | 0.58 to 0.61 | 1 to 6 | 0.02 to 0.04 / – | no, none of four |

Seed 301's champion-bout count is its whole-run total (704 of 2020) rather than the final checkpoint, which is
why its cell is a dash and its last checkpoint is given instead; seeds 302 to 304's dashes are quantities the
runs did not report separately. The Pioneers of three of the four delegated seeds had lost their peak by the
end, as seed 301's did. **Condition A closes at one steerer in eight seeds.** The difference between the seeds
is whether the holistic search found a foothold in the first fifty generations, and seven times in eight it did
not. **Condition B**, one seed, is also complete and also found no steerer; it has its own section at
4b'' because what it settles is the averaging question of 4b', not the seed count of condition A.

This partially contradicts our pre-registered expectation: we did not expect holistic steering under A alone, and one seed of two produced it.

## 4b. Why the search found so little: drift, and a signal that was mostly noise

Two measurements from the lineage logs settle what the champion curves could not.

**Ancestry collapse is drift.** Every population in this series descends from two to six of its twenty founders by generation 100. An ancestry-only model of the reproduction scheme (twenty members, two elites, tournaments of three, crossover at one half) coalesces to about four founders by generation 50 under fitness that is pure noise, and to one under fully heritable fitness. The runs match the noise case. Founder collapse is what a population of twenty does; it is neither a failure of selection nor evidence that selection found anything. Trait diversity did not collapse: the champions' descriptor diversity stayed flat through the competitive runs and narrowed only in the one seed that climbed a hill.

**Fitness was almost entirely noise.** The realised heritability of fitness, the correlation between a child's score and its parents', is 0.17 to 0.20 for the holistic population in the competitive random-terrain runs, 0.03 to 0.12 under condition A, and 0.04 to 0.08 for the wheeled population in every condition. Eighty to ninety-seven percent of a child's score was the draw, not its genes. The wheeled population's fitness was never heritable: the designed body won on its body alone while its controller took a random walk, which is why its evolved runaways looked arbitrary. Evaluation averaging did not rescue it: with two opponents and two draws per individual (condition B, seed 301, 200 generations) the holistic side's heritability was 0.02 over the first hundred generations and 0.04 over the second, the wheeled side's 0.08 and 0.10. An earlier draft of this paragraph reported 0.74 for condition C; that number pooled the run's two phases, and the change of score between them inflated the correlation. Within phases, condition C's heritability was 0.41 (holistic) and 0.09 (wheeled) during the sixty-generation solo locomotion phase, and 0.12 and 0.05 in the competitive phase that followed. What is heritable, at this population size, is a dense solo score; the outcome of a zero-sum bout is not, however many bouts are averaged.

The mechanism, then, is evaluation resolution. One bout against one opponent on one layout cannot rank twenty bodies on a plateau where almost none of them move, so selection acts on noise, drift takes over, and a hill is found only when a lucky lineage happens to land on its slope, as one seed of two did under condition A. The experiment this implicates adds nothing to the search: the same GA and the same world, with the number of opponents and draws per evaluation swept from one to eight, measuring heritability and hill-finding.

## 4b'. Score resolution inside a bout does not help (sweep complete: dense arm and both averaging arms)

The dense arm of the evaluation-resolution sweep, the condition A world with closeness (progress integrated over the whole bout) as the bout score, one opponent and one draw, ran to generation 100. Realised heritability was 0.07 on both sides, inside the range of the sparse-score runs. On twelve fresh draws its holistic best held the target 0.00 of the time at every checkpoint, while its wheeled best reached 0.62 by generation 40 and 0.61 at the end. The same dense score used solo, in condition C's locomotion phase and the capacity runs, gave heritability 0.35 to 0.41. The bout format, not the score's resolution, is what turns evaluation into a coin flip. The averaging arms, at generation 30 of 100, do not help either. Over children born in generations 1 to 30, on the same seed and world:

| Evaluation per individual | Holistic heritability | Wheeled heritability |
|---|---|---|
| 1 opponent, 1 draw, time at target (A-301..304, B-301 window) | −0.02 to +0.14 | +0.04 to +0.18 |
| 1 opponent, 1 draw, closeness (dense) | +0.09 | −0.05 |
| 1 opponent, 4 draws | −0.14 | +0.11 |
| 2 opponents, 2 draws | −0.03 | +0.19 |

Both averaging arms then ran to generation 100. Over the whole run, heritability was −0.01 (four draws) and +0.05 (two opponents, two draws) on the holistic side and 0.13 on the wheeled side in both. On twelve fresh draws the holistic best held the target 0.00 of the time at every checkpoint in both arms, while the Pioneer's best reached 0.54 and 0.42 at the end and won the final champion bouts 50 to 0 and 49 to 1. Four bouts per individual instead of one should cut sampling noise in the score by a factor of two if that noise were the problem; the holistic heritability does not move, and neither does the hill-finding. The score's noise is not draw-to-draw variance that averaging removes. Either the bout outcome is not a function of anything a child inherits, or the operators change a child so much that it inherits little. The second is testable without a bout, by the parent-child correlation of body and controller descriptors under one round of mutation, and it is not the fault.

**What a child inherits, stage by stage.** Sixty parents from the condition A population at seed 301 were each mutated once with the run's own operators and no selection, and twenty-six body and controller descriptors were measured on parent and child. The median parent-child correlation is +0.81 for the holistic operators (parts +0.78, mass +0.75, symmetry +0.61, links +0.82, sensor-driven effectors +0.84, mean weight +0.88) and +0.90 for the controller-only operators. Structure is inherited faithfully. Solo behaviour, from the locomotion phase of condition C and the capacity runs, is inherited at 0.35 to 0.41. The outcome of a bout is inherited at zero, and four bouts averaged are still zero. Each stage loses signal and the bout loses all of it: what a child gets from its parents is its body and its wiring, mostly its behaviour, and none of its luck against one opponent on one terrain. Every population in this series was bred on the last of those.

## 4b''. Averaging bouts does not help either (condition B, one seed, complete)

Condition B is condition A with each individual scored on two opponents and two draws, four bouts averaged instead of one. Seed 301 ran to generation 200. The pre-registered expectation was that averaging narrows the seed spread of the champion curve; with one seed that cannot be tested, and what the seed does show is the same course as every non-steering seed of condition A.

**The holistic side never left the floor.** On twelve fresh draws the holistic best's time at target was 0.01, 0.00, 0.00, 0.00, 0.01, 0.02, 0.00, 0.00, 0.00, 0.01 and 0.00 at generations 0 to 199 by twenties. Its training fitness sat at 0.72 to 1.00 throughout, the winner's curse at full strength: the best of twenty on four bouts still looks like a competent robot and is not one. The Pioneer's best went 0.00, 0.37, 0.35, 0.55, 0.43, 0.62, 0.68, 0.69, 0.74, 0.69, 0.64 over the same checkpoints and, unlike three of the four condition A Pioneers run by the delegate, kept its competence to the end. In the checkpoint champion bouts the holistic champions held the target 0.00 of the time at every checkpoint but the last (0.01), the wheeled champions 0.14 to 0.56; the Pioneer won the final round robin 43 to 5. Four of the five holistic wins belong to one champion that held the target 0.13 to 0.17 of the bout on the round robin's single start draw against Pioneers that did not reach it; the fifth was a Pioneer driving fifty metres off the arena. On twelve fresh draws the generation's training best held the target 0.00, so the one holder is a draw-specific behaviour or a champion the training score did not pick, and either way it is not a steerer by this paper's test.

**Heritability by half was 0.02 and 0.04** for the holistic population and 0.08 and 0.10 for the wheeled, on 1,980 and 2,000 parent-child pairs per window. Four bouts averaged instead of one leaves the correlation between a child's score and its parents' where one bout left it. The holistic best at generation 199 has four parts and 66 units; at generation 150 it had sixteen parts and 133 units; the body distribution kept moving and nothing that moved was selected for anything. (Population 20, no descriptor archive, as in every condition run so far; the section 4 design at population 60 has not been run.)

This closes the averaging question begun in section 4b'. Across one hundred generations in the sweep and two hundred here, at one, two and four bouts per individual, the holistic side's heritability under a zero-sum bout is 0.05 or less and its fresh-draw competence is zero. The sampling noise that averaging removes is not where the signal went.

## 4c. Competition erases what the locomotion phase built (condition C, one seed, complete)

**A solo phase finds competence; the competitive phase loses it.** Condition C evaluates the first sixty generations on a solo score and then switches to two opponents and two draws per individual. Evaluated on twelve fresh terrain and start draws that the run never saw, the holistic best's time at target rose from 0.01 at generation 0 to 0.17 at 40 and 0.31 at 60, the end of the solo phase. Twenty generations of competition later it was 0.02, and at generation 100 it was 0.01. The wheeled best went from 0.44 to 0.71 over the same span and kept it. Heritability tells the same story from the other side: 0.41 for the holistic population while the score was solo, 0.12 once it was a bout. The competitive score is not merely noisier than the solo one; under it, the lineage that could reach the goal was replaced within twenty generations by lineages that could not, because reaching the goal alone is not what a zero-sum bout against a faster body rewards. The run's second hundred generations confirmed it: the holistic best's fresh-draw time at target was 0.00 at every checkpoint from generation 80 to 199, the wheeled best's 0.55 to 0.66, and the Pioneer won the final champion bouts 49 to 1. Over the full run, heritability was 0.40 for the holistic population during the solo phase and 0.05 during the competitive phase; the wheeled population's was 0.09 in both. What a solo score built in sixty generations, a hundred and forty generations of bouts did not merely fail to improve but removed and never restored.

**An ecology instead of a culling round.** The fitness signal in every condition above is consumed by a truncation and tournament step that discards most of each generation on one draw. As a test of whether the collapse is a property of that step rather than of the task, the repository now carries an ecology mode in which nobody is ranked: individuals persist across seasons, gain energy from each challenge and lose a little to living, breed when they can afford it and a slot is free, and die only of starvation or old age. Generations are decoupled from challenges and a population is a mixture of ages and lineages at any time. Two ecologies of the redesigned world are running: one whose seasonal challenge is a paired bout within the population, and a control whose challenge is a solo closeness score on which nobody starves, so that turnover comes only from old age and the run measures what morphology space looks like under no selection at all.

**The relative-cost ecology dies of its own success.** The solo ecology on the closeness score, with the living cost set to each population's mean gain that season, went extinct on both sides: the holistic population never produced a birth and aged out by season 157; the wheeled population converged on competent goal-holders (mean closeness 0.63 across the survivors) and then, being uniform, had nobody enough above its own average to earn a birth, and aged out by season 196. A relative cost with a fixed birth threshold is a Red Queen with no reproduction: the better and more alike a population becomes, the less anyone can breed. The paired ecology, whose bouts hand out 0 and 1 whatever the competence, only dies more slowly: with energy conserved by construction, a birth needs one individual to bank a full unit of other individuals' losses, which happened about once every twenty-five seasons against one or two age deaths in the same span, and the population slid from 60 to 7 holistic and 3 wheeled by season 325. An ecology whose energy comes only from the neighbours cannot sustain reproduction. The foraging ecology's absolute economy, where energy comes from the world and not from the neighbours, is the one that lets a competent population persist, and it is the design carried forward.

## 5. What we already know

Two things carry over from the second paper and do not depend on the task redesign. First, the competitive score cannot be the only instrument: it crowned a motorless ball, then a runaway, and it will crown whatever exploits the next flaw. Every artefact we found was found by measuring champions alone. Second, the proposal's three arguments for holistic evolution are all arguments about what a search could find, and the search we ran was not strong enough to find much of anything: twenty individuals, elitism, a direct encoding with no symmetry, and a fitness that does not discriminate until a body already moves. Whatever the redesigned task shows, the machinery will need the same attention as the task.

## Reproducibility

The block that stood here gave the section 4 design rather than the runs section 4a to 4c report, and its
`--score time-at-target` was not a spelling the command line accepts. These are the runs that were done.

Condition A, one opponent and one draw, seeds 301 to 308:

```
rabbitstew evolve --terrain random --mass-budget 15.34 --conventional-topology \
    --random-start --score time_at_target --population 20 --generations 200 \
    --brain-model rich --duration 15 --seed 301 \
    --champion-interval 5 --champions 5 --champion-mode roundrobin \
    --out runs/a-301
```

Condition B adds the averaged evaluation, condition C adds the solo phase before it:

```
... --opponents 2 --draws 2 --seed 301 --out runs/b-301
... --opponents 2 --draws 2 --locomotion-phase 60 --seed 301 --out runs/c-301
```

Conditions A, B and C were all run at population 20 with no descriptor archive (each run's `config.json`: `population_size: 20`, `archive: false`); the 1,980 and 2,000 parent-child pairs per hundred-generation window in 4b'' are that population's child count.

The evaluation-resolution sweep of 4b', seed 701, 100 generations: the dense arm is condition A with
`--score closeness`, the averaging arms are `--opponents 1 --draws 4` and `--opponents 2 --draws 2`.

Every capability number in 4a to 4c is a fresh-draw solo score, from `scripts/eval_fresh.py RUN 10 12`:
twelve start-and-terrain draws seeded outside the run's own range, never a training-draw best. Realised
heritability is `rabbitstew heritability RUN`, which takes windows so the phases of condition C are reported
apart. Structure and lesions are `rabbitstew analyze RUN --every 10 --lesions final`.

The section 4 design in full, population 60 with a descriptor archive over 500 generations and four seeds per
condition, has not been run; no run in this paper reaches 500 generations, population 60, or four seeds under
any condition (condition A has eight seeds at population 20).
