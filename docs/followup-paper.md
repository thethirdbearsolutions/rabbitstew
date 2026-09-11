# Rabbitstew, Twenty Years On: Does Co-evolving the Body Beat a Designed One?

*Draft follow-up to "Rabbitstew: A Robot Simulator with Variable Morphologies" (Jucovy, 2005).*

## Abstract

The 2005 proposal set out a simulator for evolving robot morphologies together with their controllers, and an experiment it was built for: evolve one population holistically, body and brain together, from random morphologies; evolve a second population's controller only, inside a fixed, human-designed wheeled body; and measure them against each other in a competitive race to the centre of an arena. The simulator was never built and the experiment never run. We built the simulator on a modern physics engine, ran the experiment as written, and then ran it again under a series of controls that the original design did not anticipate. The experiment as written favours the fixed body, and the one regime in which holistic evolution looked competitive turned out to be a weight-class mismatch: holistic bodies grew to several times the fixed body's mass, and equalising mass removed their advantage. With mass equalised and the fixed body's controller topology allowed to evolve, holistic evolution neither wins nor loses on flat ground across 250 generations. On terrain the picture inverts: when obstacles are placed that a wheel cannot clear, evolved bodies win decisively and, in some seeds, climb; on terrain drawn at random from a distribution not designed against either body, __RANDOM_SUMMARY__. Enriching the sensor and motor repertoire did not weaken the fixed body's advantage on flat ground. We conclude that the fixed body's strength is a property of the task, not of the brain model, and that the paper's competitive score is too thin an instrument to say what evolution produced. We add an analysis toolkit that measures bodies and brains alone, independent of the bout, and use it to show that the co-evolved controllers are mostly disconnected, that the winning evolved bodies on flat ground cannot steer, and that the winning wheeled controllers cannot cross terrain.

## 1. Introduction

The original proposal argued from three directions that holistic evolution ought to produce better robots than conventional evolution of a controller in a fixed body: brains and bodies co-evolve in nature; a gradual, undirected search avoids human bias and lets brain and body couple tightly; and, following Conrad, the extra dimensions of a joint search space may connect fitness peaks that are isolated in the controller's space alone. It also observed, correctly, that nobody had tested this head to head, and proposed the test: two populations, one competitive task, periodic bouts between their champions.

We report that test, and what happened when we tried to make it fair. Three things were not in the original design and each changed the answer. First, a mass budget: the proposal's genotype lets bodies grow, and a shoving contest rewards mass regardless of control. Second, a brain-only baseline: the proposal freezes the fixed body's network topology while the holistic side may grow its own, which confounds "body evolves" with "topology evolves". Third, the task itself: a flat arena and a race to its centre is a driving contest, and a wheeled box is the best driver in the room. We also extended the brain model well beyond the proposal's, because a minimal brain is the kind a wheeled box needs, and we wanted to know whether the fixed body's advantage was an artefact of that minimalism. It was not.

The final and largest addition is not an experiment but an instrument. The proposal's only measurement is a zero-sum score between two specific robots. We built a toolkit that measures each robot alone, in fixed situations, and describes its body and controller structurally and functionally, so that the question "what did evolution produce" can be answered separately from "who won".

## 2. The simulator

Rabbitstew is implemented in Python on MuJoCo, replacing the PyODE bindings the proposal planned to use. The architecture follows the proposal: a genotype is a directed graph of Nodes, each holding a Segment (box, sphere or cylinder with relative dimensions normalised to unit volume) and a list of Connections (child Node, relative position on the parent's surface, orientation, scale, joint type among hinge, ball, slider and fixed, and a recursive limit that lets circuits in the graph produce repeated parts). Synthesis is breadth-first from the root and stops at a size-ratio limit; unreached Nodes are carried silently. Each Segment carries a local Brain of Sensors, Effectors and Neurons; an optional global Brain of Neurons may link to any local unit. Passive scenery is a brainless robot welded to the ground. The visualizer is decoupled through the proposal's data file: unit shapes and dimensions, then a position and quaternion per unit per recorded step.

Deviations, all documented in the repository: a Connection carries a joint axis and an optional joint limit, needed for physically sensible joints and to express a wheel; the mapping of a Connection's position onto the parent's surface and the derivation of absolute size, which the proposal left open, are made explicit; direction sensors read in the Segment's own frame; joint damping acts as a motor's speed limit on driven joints and as light friction on passive ones; and the proposal's quaternion-to-axis formula is used in its active-rotation form.

The fixed body is a differential-drive box loosely modelled on a Pioneer: a chassis, two driven front wheels (one Node each, so the global brain can command them separately) and two free-rolling rear wheels. It is an ordinary genotype and passes through the same synthesis and physics as everything else.

## 3. Experimental design

**Populations.** Twenty individuals each. The holistic population starts from random genotypes of two to five Nodes and evolves everything: segments, connections, joint types and limits, the node graph, neural units, links and weights. The conventional population shares the fixed body; in the proposal's regime only its weights and biases evolve, and in our brain-only regime its global-brain neurons and all links evolve too, with the body and its mounted sensors and effectors held fixed and asserted unchanged every generation.

**Fitness.** The proposal's competition: two robots start on opposite sides of the centre, 2 m away, and after a fixed time each is scored by the opponent's horizontal centre-of-mass distance from the centre divided by the sum of both distances. The score is zero-sum and rewards both reaching the centre and keeping the opponent away. Within a population every member fights the previous generation's best and the best fights the runner-up; selection is elitist with tournaments; children come from crossover and mutation.

**Measurement.** At checkpoints the top *k* of each population meet in a round robin from both starting sides. The proposal's best-versus-best is available but gives too few bouts to support a claim, and we use *k* of 3 or 5, so 18 or 50 bouts per checkpoint. The holistic side's mean fitness across those bouts is the champion curve; 0.5 is parity.

**Controls.** A mass budget scales the masses of any robot heavier than the fixed body's 15.34 kg down to that figure, leaving geometry intact. The brain-only regime is as above. Every bout in a generation, including the champion bouts, shares the same terrain seed when terrain is random, and the seed is recorded so every bout can be re-simulated.

**Brain models.** *Paper*: binary contact sensors, three-axis direction sensors to the target and the opponent, tanh neurons, torque motors. *Rich*: adds orientation, body velocity, distance to target and opponent, joint angle and velocity, height, and free-running oscillators as sensors; sin, abs, relu, sign, leaky-integrate and differentiate as neuron functions; position and velocity servos as motor modes. Under the rich model the fixed body gets orientation, velocity, distance and wheel-speed sensors.

**Tasks.** *Flat*: the proposal's arena. *Plateau*: a raised central disc 0.15 m high, above the wheel radius, with the target on top. *Rails*: three low bars 0.1 m high across each approach, taller than the chassis clearance. These two are designed obstacles and prove only that wheels cannot cross them; they are reported for what they show about climbing. *Random*: fourteen obstacles per generation drawn from a seed, with uniform footprints from 0.15 to 0.7 m, log-uniform heights from 0.03 to 0.3 m (median 0.096 m, so roughly half are bumps a wheel rolls over and half are not), random shapes and yaws, and uniform positions within 2.6 m of the centre avoiding only the spawn points. Nothing in the distribution is aimed at either body; a fresh draw every generation prevents either population from overfitting a layout.

**Runs.** Bout length 8 s in the first replication and 15 s thereafter. Run lengths of 50 and 250 generations. Two to four seeds per condition. Everything is checkpointed and reproducible from the saved genotypes and seeds.

## 4. Results

### 4.1 The experiment as written

With the proposal's brain model, free mass and 8-second bouts, one 50-generation seed crossed parity at generation 18 and hovered around it, winning 214 of 468 champion bouts. With 15-second bouts across four seeds the fixed body dominated: holistic mean champion fitness 0.28, 0.37 and 0.35 by thirds of the run, 347 wins of 1872. The longer bout gives the driver time to reach the centre and sit on it.

The holistic side's near-parity result in the short-bout run was a weight-class mismatch. Its champions weighed 30 to 90 kg against the fixed body's 15 kg; across the 50 replayed best-versus-best bouts, holistic fitness correlated at 0.41 with mass and at 0.04 with the number of connected neural units or driven effectors; one champion with no driven effector at all still won its bout. Two control seeds at equal mass fell from 0.31 to 0.21 by thirds of the run, 113 wins of 936.

### 4.2 Equal mass, brain-only baseline, 250 generations, flat ground

| Condition | Holistic mean fitness by fifths of the run | Holistic wins |
|---|---|---|
| Flat, paper brain | 0.40, 0.42, 0.45, 0.55, 0.51 | 731 of 1836 |
| Flat, rich brain | 0.45, 0.44, 0.46, 0.45, 0.45 | 657 of 1836 |

Both conditions sit in a parity band for 250 generations. The seed spread is wide: final checkpoints range from 0.26 to 0.54 across seeds of the same condition. Enriching sensors and motors did not move the curve. The fixed body's controller grew from 15 to about 30 units under topology evolution; the holistic controllers grew to between 40 and 160 units.

### 4.3 Designed terrain

| Condition | Holistic mean fitness by fifths | Holistic wins | Reached the goal region (holistic / conventional) |
|---|---|---|---|
| Plateau, rich brain | 0.47, 0.49, 0.55, 0.53, 0.54 | 1218 of 1836 | on top: 180 / 0 of 1836 |
| Rails, rich brain | 0.70, 0.80, 0.77, 0.77, 0.76 | 1744 of 1836 | past all rails: 1085 / 0 of 1836 |

On rails the holistic side wins 95 percent of bouts from the first fifth on, crossing all three rails in most of them; the wheeled body crossed even the first rail in 8 bouts of 1836. On the plateau one seed evolved climbers by generation 140 and reached the top in 180 bouts; the other seed never climbed but still won on the ratio score by getting closer to the edge and shoving. These results are real but unsurprising: they show that body evolution finds bodies for obstacles a wheel cannot pass, and nothing about which body is better in general.

### 4.4 Random terrain

__RANDOM_RESULTS__

### 4.5 What evolved

The analysis toolkit measures each generation's best alone. On the flat, rich-brain seed 101 run, the final holistic best, a 16-part body from 8 nodes with 88 units and 24 links, gains 1.84 m towards a goal in 15 s, crosses all six test terrains, and cannot reach any goal placed off its initial heading. The final conventional best gains 1.95 m, steers to all three off-axis goals, and crosses no terrain. Its 31-unit brain is 94 percent connected with 17 units whose lesion costs more than 10 cm of progress; the holistic brain is 26 percent connected with one such unit, and 63 of its 88 units are sensors of which 9 have any path to an effector. Two hundred and fifty generations of flat-ground competition produced, on the holistic side, a body that moves forward well and a brain that barely uses its senses, and on the conventional side a controller that steers.

__ANALYSIS_MORE__

## 5. Discussion

**The task decides.** Every result above is consistent with one reading: the fixed body's advantage is a property of the flat-arena race, not of the brain model, the mass, or the evolutionary regime. Equalising mass and evolving the fixed body's topology brought the two populations to parity on flat ground and no further; changing the ground changed the winner. Conrad's extradimensional bypass may well exist, but on a flat arena there is no valley to bypass: the wheeled body's peak is reachable by weights alone.

**Brain simplicity is not what protects the wheel.** We expected that a richer sensorimotor repertoire would let body evolution exploit gaits and feedback a wheeled box cannot, and weaken the fixed body's advantage. On flat ground it did not. What the rich model did enable is visible on terrain and in the analysis: oscillator-driven servos produce the climbing and crawling bodies.

**Win rate is not a description.** The proposal's score is a comparison between two particular robots under one particular task. It cannot distinguish a body that moves well from a heavy one, or a brain that steers from one that lurches, and it scores a creature with no working effector as a winner when it happens to be heavy and in the way. The solo trials and structural measures do distinguish these things, and they say that co-evolution on this task produced specialists whose competence is narrow and whose brains are mostly inert. Whether that is a property of the task, the operators, or the direct genotype-to-phenotype mapping the proposal itself flagged as a limitation is the next question.

## 6. Limitations

Two to four seeds per condition; the flat-ground spread is large enough that the parity band is a description, not a proof. The mass budget equalises mass but not size. The random terrain distribution is one choice among many, and its parameters were not tuned but were also not derived from anything. Champion bouts use the top 3 to 5 rather than the whole population. The genotype-to-phenotype mapping is direct, with no development or enforced symmetry, as the proposal noted.

## 7. Reproducibility

Every experiment is a single command on the repository, and every bout can be re-simulated from the saved genotypes and terrain seeds:

```
rabbitstew evolve --generations 250 --population 20 --duration 15 --mass-budget 15.34 \
    --conventional-topology --brain-model rich --terrain random \
    --champion-interval 5 --champions 5 --champion-mode roundrobin --seed 201 --out runs/random-rich-201
rabbitstew compare "flat=runs/flat-rich-101,runs/flat-rich-102" "random=runs/random-rich-201,runs/random-rich-202"
rabbitstew gallery runs/random-rich-201 --every 5
rabbitstew analyze runs/random-rich-201 --lesions final
```

## References

Conrad, M. (1990). The geometry of evolution. *Biosystems* 24, 61–81.
Jucovy, E. G. (2005). Rabbitstew: A robot simulator with variable morphologies. Proposal.
Sims, K. (1994). Evolving 3D morphology and behavior by competition. *Artificial Life IV*.
Todorov, E., Erez, T., Tassa, Y. (2012). MuJoCo: A physics engine for model-based control. *IROS*.
