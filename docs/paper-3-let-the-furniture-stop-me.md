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

## 5. What we already know

Two things carry over from the second paper and do not depend on the task redesign. First, the competitive score cannot be the only instrument: it crowned a motorless ball, then a runaway, and it will crown whatever exploits the next flaw. Every artefact we found was found by measuring champions alone. Second, the proposal's three arguments for holistic evolution are all arguments about what a search could find, and the search we ran was not strong enough to find much of anything: twenty individuals, elitism, a direct encoding with no symmetry, and a fitness that does not discriminate until a body already moves. Whatever the redesigned task shows, the machinery will need the same attention as the task.

## Reproducibility

```
rabbitstew evolve --terrain random --mass-budget 15.34 --conventional-topology \
    --random-start --score time-at-target --opponents 5 --draws 3 --locomotion-phase 100 \
    --population 60 --generations 500 --brain-model rich --seed 301 --out runs/c-rich-301
rabbitstew analyze runs/c-rich-301 --every 10
```
