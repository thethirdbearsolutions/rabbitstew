# RBT-5: Sims-budget solo run, seed 902 — replicate of RBT-11, stopped at generation 20

Branch `claude/rbt-lowest-unclaimed-ticket-fe8mzt`. Run directory `runs/RBT-5/sims-902`.
Command: RBT-11's verbatim, with `--seed 902 --out runs/RBT-5/sims-902 --workers 3`.

**This is a truncated replicate and must not be read as one.** The package asks for 150
generations; this box has four cores and delivered 21 (generations 0 to 20) at about
6.4 minutes each. The heading curriculum is 20 percent ramped at the stopping point, so
every number below comes from a run that has not yet been given its own task at full
difficulty. The run was stopped on a generation boundary and `state.json` (14 MB) is
committed, so `rabbitstew evolve --resume --out runs/RBT-5/sims-902` continues from
generation 21 on a bigger box without repeating anything.

## Rate

| Generation | Wall clock |
|---|---|
| 0 (children only) | 184 s |
| 1 (survival: parents re-evaluated too) | 385 s |
| 2–20 | 373–419 s, mean 392 s |

150 generations at this rate is about 16 hours, which agrees with RBT-11's own budget
note (180k solo simulations at 1–2 s each is 3–6 h on sixteen cores, 16–32 h on three).
The package is correctly labelled "big box"; this box is not one.

## 1. Fresh-draw solo scores (`eval_fresh.py runs/RBT-5/sims-902 10 12`)

Twelve start-and-terrain draws seeded outside the run's range, at the full heading range
whatever the curriculum has reached.

| Generation | Holistic score | Holistic tat | Holistic progress | Wheeled score | Wheeled tat | Wheeled progress |
|---|---|---|---|---|---|---|
| 0 | 0.039 | 0.000 | 0.044 | 0.426 | 0.310 | 0.548 |
| 10 | 0.250 | 0.078 | 0.263 | 0.329 | 0.282 | 0.361 |
| 20 | 0.237 | 0.214 | 0.279 | 0.683 | 0.651 | 0.813 |

The holistic side reaches fresh-draw time at target 0.214 by generation 20. The capacity
runs of paper 4 reached 0.2–0.3 at generation 100 on a population of 20. On the face of
it the Sims budget gets to the same place five times faster in generations, and the lab
below says what it actually got there with.

## 2. Realised heritability (`rabbitstew heritability`)

| Window | Holistic | Wheeled | Pairs |
|---|---|---|---|
| generations 1–20 (whole run) | 0.3704 | 0.1943 | 11,414 / 11,581 |
| generations 1–10 | 0.2425 | 0.2520 | 5,414 / 5,581 |
| generations 11–20 | 0.3283 | 0.1588 | 6,000 / 6,000 |

The package's own windows (1–51, 51–101, 101–151) do not apply to a 21-generation run;
these are the halves. The holistic figure of 0.37 sits inside the 0.35–0.41 that paper 3
measured for a dense solo score, and is seven times the 0.05-or-less it measured under a
zero-sum bout. Nothing here contradicts the score argument the package is built on.

## 3. Founders

At generation 20, both populations of 600 (300 members plus 300 persisting parents under
survival selection) descend from **2 distinct generation-0 founders** each.

`--founder-model` says that under fitness that is pure noise, this reproduction scheme
would still have about **102 founders** at generation 10 or later. The observed 2 is not
the noise case. This is the sharpest contrast with paper 3, whose population-20 runs
matched their noise model exactly and whose ancestry collapse was therefore drift. Here
selection is doing something. Whether what it selected is worth having is question 5.

## 4. Capability of the finals (`rabbitstew analyze --lesions final`)

| | Holistic gen 20 | Wheeled gen 20 |
|---|---|---|
| Approach progress | +1.606 m | +1.951 m |
| Steering successes | **0 of 3** | 3 of 3 |
| Terrain successes | 0 of 6 | 3 of 6 |
| Mean speed | 0.239 m/s | 0.196 m/s |
| Straightness | 0.586 | 0.682 |
| Work per metre | **49.1 J/m** | 1885.7 J/m |
| Fell | no | no |

The holistic best moves, moves fast, and moves at a thirty-eighth of the wheeled body's
energy per metre. It reaches none of the three off-axis goals.

## 5. The lab (standing rule; `scripts/lab.py runs/RBT-5/sims-902 holistic 20 12`)

Fresh tat of 0.214 crosses the competence threshold, so the champion is labbed before it
is called anything. Three parts, 8 units, 10 links.

```
part 0: sphere dims=(0.186,)  joint=FIXED  parent=None  mass=7.68
part 1: sphere dims=(0.068,)  joint=SLIDER parent=0     mass=0.37
part 2: sphere dims=(0.183,)  joint=BALL   parent=0     mass=7.29
unit 0 part 0 effector dof2 bias=+0.39      unit 4 part 1 sensor agent   (unlinked)
unit 1 part 0 effector dof1 bias=+0.31      unit 5 part 2 effector dof2 bias=-0.14
unit 2 part 1 effector dof2 bias=-0.14      unit 6 part 2 neuron sign   (unlinked)
unit 3 part 1 neuron sign   (unlinked)      unit 7 part 2 sensor agent  (unlinked)
links: 0->0 +0.26  0->1 +0.63  2->1 +3.51  5->1 +3.51  2->1 +1.05  5->1 +1.05
       2->2 +0.79  0->2 -0.81  5->5 +0.79  0->5 -0.81
```

| mode | progress | tat | path | straight | arrive | hold | work |
|---|---|---|---|---|---|---|---|
| intact | +0.42 | 0.15 | 3.0 | 0.68 | 3.7 | 0.20 | 0.3 |
| env sensors blanked | +0.42 | 0.15 | 3.0 | 0.68 | 3.7 | 0.20 | 0.3 |
| oscillators blanked | +0.42 | 0.15 | 3.0 | 0.68 | 3.7 | 0.20 | 0.3 |
| global brain silenced | +0.42 | 0.15 | 3.0 | 0.68 | 3.7 | 0.20 | 0.3 |
| local brains silenced | +0.42 | 0.15 | 3.0 | 0.68 | 3.7 | 0.20 | 0.3 |
| lesion unit 0 (part 0 effector dof2) | +0.05 | 0.01 | 4.1 | 0.37 | 9.2 | 0.02 | 0.3 |
| lesion unit 1 (part 0 effector dof1) | +0.42 | 0.15 | 3.0 | 0.68 | 3.7 | 0.20 | 0.3 |
| lesion unit 2 (part 1 effector dof2) | +0.27 | 0.00 | 3.1 | 0.48 | — | 0.00 | 0.2 |
| lesion unit 5 (part 2 effector dof2) | +0.02 | 0.00 | 0.2 | 0.22 | — | 0.00 | 0.0 |

**Every sensor in this champion is unlinked.** Both `agent` sensors and both `sign`
neurons touch nothing. Blanking the environmental sensors, blanking the oscillators,
silencing the global brain and silencing the local brains all leave the behaviour
identical in every figure the lab reports, because there is no neuron and no sensor on any path
that matters. The whole robot is four effectors wired to each other and to themselves.
It is open-loop.

What does carry it is the effector coupling, and it is cross-part. Unit 5 lives on part 2
and drives unit 1 on part 0 at +3.51 and +1.05; unit 0 on part 0 drives units 2 and 5 on
parts 1 and 2 at −0.81. Lesioning unit 5 takes progress from +0.42 m to +0.02 m and the
path from 3.0 m to 0.2 m: the robot stops entirely. Lesioning unit 0 costs tat 0.15 to
0.01. So the two links that matter most are both between different parts.

The generation-10 best is the same object: the same three spheres on the same fixed,
slider and ball joints, two extra units that are wired to nothing, the same cross-part
weight (+2.60 rather than +3.51) and the same ±0.79/−0.85 self-and-cross pattern, every
sensor unlinked, and all four blanket lesion modes identical to intact. This is one
lineage seen twice, not two findings.

## 6. Wiring counts and controller descriptors

Phenotype link counts for the holistic best:

| Generation | parts | units | same-part links | **cross-part links** | global links | reflex arcs | env-driven effectors |
|---|---|---|---|---|---|---|---|
| 0 | 6 | 27 | 26 | 62 | 68 | 4 | 4 |
| 10 | 3 | 10 | 4 | 4 | 0 | 0 | 0 |
| 20 | 3 | 8 | 4 | 6 | 0 | 0 | 0 |

Cross-part links are non-zero, which they have been in no previous run in this series
because the encoding did not permit them. In the generation-20 genotype, 40 of 80 local
brain links read a neighbouring node's units.

Controller descriptors of the generation-20 best: `env_driven_effectors` 0,
`oscillator_driven_effectors` 0, `cyclic_units` 3, `global_neurons` 0, `sensor_sources`
`{'agent': 2}` (both unlinked). At generation 0 the best had 3 global neurons, 4
env-driven effectors and `{'opponent_distance': 1, 'target': 6}`; twenty generations of
selection removed all of it.

## Did the budget buy anything?

**Steering: no.** Fresh tat is 0.214, over the 0.2 threshold, but the capability trials
are 0 of 3 on off-axis goals and the lab shows why: the robot cannot steer because it
cannot sense. Its fresh-draw score is the fraction of random draws whose target happens
to lie where it was already going. A-301's champion reached fresh tat 0.54 with one
reflex arc; this one reaches 0.21 with none. The threshold is met and the capability
behind it is not there, which is exactly the failure mode the standing rule exists to
catch.

**Proprioception: no.** No `joint_angle` or `joint_velocity` sensor is on any path in
either labbed champion. No sensor of any kind is.

**A cross-part link that matters: yes, and this is the real result.** The package's own
test ("lesion of local brains costs more than the sum of single-part effects") returns
nothing here, because `no_local` spares effector biases and every working unit in this
champion is an effector. But the per-unit lesions answer the underlying question
directly: the behaviour is carried by effector-to-effector links between different parts,
and cutting the strongest of them stops the robot dead. Sims' encoding produced
distributed control on its first outing in this codebase. What it distributed is a
motor pattern, not a sensorimotor loop.

**And a contradiction with paper 3, stated plainly.** Paper 3 concluded that ancestry
collapse in this series is drift, because the runs matched an ancestry-only noise model.
At population 300 on a solo score that does not hold: 2 founders observed against 102
expected under noise, with holistic heritability of 0.37. Selection at this budget is
real and strong. It selected an open-loop roller, stripped three global neurons and four
sensor-driven effectors out of the generation-0 best, and got a fresh-draw score for it.
The problem was never that selection could not act; on this evidence the problem is what
a dense closeness score rewards when a body is free to become a thing that rolls.

**Caveat, repeated because it governs everything above.** Twenty generations of a
150-generation package, with the heading curriculum a fifth ramped. The capacity runs
were still improving at generation 100. None of this forecasts what seed 901 will show
at generation 150, and the honest comparison against it is impossible until this seed is
resumed to the same length.
