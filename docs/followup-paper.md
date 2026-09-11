# Rabbitstew, Twenty Years On: Does Co-evolving the Body Beat a Designed One?

*Draft follow-up to "Rabbitstew: A Robot Simulator with Variable Morphologies" (Jucovy, 2005).*

## Abstract

The 2005 proposal set out a simulator for evolving robot morphologies together with their controllers, and an experiment it was built for: evolve one population holistically, body and brain together, from random morphologies; evolve a second population's controller only, inside a fixed, human-designed wheeled body; and measure them against each other in a competitive race to the centre of an arena. The simulator was never built and the experiment never run. We built the simulator on a modern physics engine, ran the experiment as written, and then ran it again under a series of controls that the original design did not anticipate. The experiment as written favours the fixed body. Each apparent exception turned out to be an artefact that body evolution had found and a wheeled box could not: first a weight-class mismatch, since holistic bodies grew to several times the fixed body's mass; then a flaw in our own spawn protocol, which lifted bodies by their bounding spheres and let evolved bodies harvest the drop as momentum, enough to roll onto a raised plateau and over rails without a working motor. With mass equalised, bouts started from rest, the fixed body's controller topology free to evolve, and terrain drawn at random from a distribution not designed against either body, __RANDOM_SUMMARY__. Enriching the sensor and motor repertoire did not change the outcome. We add an analysis toolkit that measures bodies and brains alone, independent of the bout, which is what exposed both artefacts, and we argue that a competitive score cannot be the only instrument in an experiment of this kind.

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

### 4.2 A second artefact: the spawn drop

Our first 250-generation matrix, at equal mass with the fixed body's topology evolving, gave a parity band on flat ground under both brain models (holistic mean fitness 0.40 to 0.55 by fifths, 731 and 657 wins of 1836), decisive holistic wins on designed terrain (1218 of 1836 on the plateau with climbs onto the top in 180 bouts; 1744 of 1836 on rails, crossing all three rails in 1085 bouts), and no effect of the brain model. We report these numbers because they were published in the course of this work, and because the way they fell apart is the most useful thing in this paper.

Robots were placed for a bout by lifting each so that no part's bounding sphere was below the ground. For a wheeled box that is a centimetre; for a large boxy or branching evolved body it can be tens of centimetres, and when the bout began the body dropped. Bodies with an off-centre weight toppled, and evolution found the shape that topples towards the goal: the final flat-ground champion of one seed is a 13.5 kg sphere with a small box welded to its side, no motor, no work, that rolls 1.84 m towards the goal from the drop alone. The plateau climbs and rail crossings were the same energy, in larger bodies. Measured alone from rest, every holistic champion of that matrix gains between −0.25 and −0.07 m towards a goal on flat ground, crosses no test terrain, steers to no goal and does almost no actuator work; the wheeled champions of the flat runs gain 1.7 to 1.9 m, steer to two of three off-axis goals and cross 17 to 50 percent of the test terrains.

The protocol now settles every robot passively for a second, zeroes all velocities and re-centres it on its spawn point before the clock starts.

### 4.3 Random terrain, from rest

__RANDOM_RESULTS__

### 4.4 Flat ground, from rest

__FLAT_RESULTS__

### 4.5 What evolved

__ANALYSIS_MORE__

### 4.6 Is the brain doing anything?

For each final champion of the random-terrain runs we measured solo capability with the evolved links kept, with every link weight set to zero (biases kept), with every link weight redrawn at random, and with every segment dimension and connection scale perturbed by a 20 percent log-normal factor. *Brain dependence* is the share of capability lost under zeroed links; *body dependence* the share lost under the perturbed body.

| Run | Champion | Capability, full | Links zeroed | Links random | Body perturbed | Brain dependence | Body dependence |
|---|---|---|---|---|---|---|---|
| random, paper brain, 201 | h249-1 | +1.00 | +1.00 | +1.00 | +0.65 | 0.00 | 0.35 |
| random, paper brain, 202 | h249-2 | −1.96 | −3.12 | −1.14 | −1.67 | – | – |
| random, rich brain, 201 | h249-0 | +0.94 | +0.01 | −0.30 | −0.14 | 0.99 | 1.16 |
| random, rich brain, 202 | h249-4 | +0.31 | +0.04 | −0.31 | +0.06 | 0.88 | 0.82 |
| random, paper brain, 201 (Pioneer) | c249-7 | +3.69 | +1.09 | +0.48 | −0.57 | 0.70 | 1.15 |

Capability is approach progress plus mean steering progress in metres; dependence is undefined where the full profile is negative (a runaway or a non-mover).

Under the paper's brain model the holistic champion's links do nothing: zeroed, randomised or evolved, the body scores the same. Its behaviour is constant torque on ball joints, and the brain is decoration. Under the rich model the champions' links carry the behaviour, and a perturbed body loses it entirely. That is the first sign in this series of a working brain-body pair. It is not yet evidence of co-adaptation in the strict sense, which would require a different good brain in the same body to do worse; no transplant donor in the final populations aligned structurally with the champions, and the test is left for the next round with donors drawn from the champion's own lineage.

## 5. Discussion

**The task decides, and so does the protocol.** Every apparent holistic advantage we found was an exploit of something outside the intended task: mass, then the spawn drop. Each was found by evolution within a few generations, each was invisible to the competitive score, and each was obvious the moment a champion was measured alone. This is the strongest argument we have for the analysis toolkit: a zero-sum score between two robots cannot tell a body that moves from one that is heavy and in the way, or from one that was dropped from a height. It scored a motorless ball as a champion.

**Brain simplicity is not what protects the wheel.** We expected that a richer sensorimotor repertoire would let body evolution exploit gaits and feedback a wheeled box cannot, and weaken the fixed body's advantage. It did not, under any protocol. __RICH_DISCUSSION__

**Designed obstacles prove nothing about bodies in general.** A plateau higher than a wheel or a rail taller than a chassis proves that wheels cannot pass them. We include those runs only because they were the first place the spawn artefact showed, not as evidence about body evolution.

__DISCUSSION_MORE__

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
