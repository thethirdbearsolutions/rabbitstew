# Rabbitstew

**Robotic Artificial Brain/Body-Intertwined Simulation Toolkit and Evolution Workshop**

A physical robot simulator in Python whose robot morphologies can be generated,
mutated and evolved automatically, together with the experiment it was designed
for: a side-by-side comparison of *holistic* evolution (bodies and brains
evolving together from random morphologies) against *conventional* evolution
(controllers evolving inside a fixed, human-designed body).

The design follows Ethan G. Jucovy's 2005 proposal *Rabbitstew: A Robot
Simulator with Variable Morphologies*, which in turn draws on Karl Sims' evolved
virtual creatures. The physics engine is [MuJoCo](https://mujoco.org) rather
than the (now unmaintained) PyODE bindings the paper planned to use; the
architecture is otherwise as described. See *Design* below for the mapping and
the handful of places where this implementation fills in or departs from the
paper.

## Installation

```bash
pip install -e .          # runtime: mujoco, numpy
pip install -e '.[dev]'   # adds pytest
pytest                    # ~50 tests, a few seconds
```

Python 3.10+ is required. MuJoCo ships binary wheels for Linux, macOS and
Windows, so no compiler is needed. Everything runs headless; the interactive
viewer (`simulate --view`) needs a display.

## Quick start

```bash
# A random creature and the fixed Pioneer-style body with a constant forward drive.
rabbitstew random --seed 5 --out creature.json
rabbitstew fixed --drive --out pioneer.json

# Validate a genotype and see what body it synthesises into.
rabbitstew inspect creature.json

# A ten-second, two-robot bout: who gets closer to the centre of the world?
rabbitstew simulate creature.json pioneer.json --out bout.traj --html bout.html

# Replay any trajectory file in a browser.
rabbitstew visualize bout.traj --out replay.html

# The experiment: both populations, 30 generations, champions meet every 5.
rabbitstew evolve --generations 30 --population 20 --champion-mode roundrobin --workers 4 --out runs/exp1
rabbitstew history runs/exp1/history.json

# One page, one slider: re-simulate and replay every generation's champion bout.
rabbitstew gallery runs/exp1 --out runs/exp1/gallery.html

# Several seeds of one configuration, and a report with the mean champion curve.
for s in 1 2 3 4; do rabbitstew evolve --seed $s --duration 15 --out runs/seed$s; done
rabbitstew report runs/seed1 runs/seed2 runs/seed3 runs/seed4 --out report.html
```

The same things from Python:

```python
import numpy as np
from rabbitstew import random_genotype, SimConfig, run_bout
from rabbitstew.fixed import pioneer_genotype
from rabbitstew.visualizer import write_html

rng = np.random.default_rng(0)
result = run_bout(random_genotype(rng), pioneer_genotype(rng), SimConfig(duration=10.0), record=True)
print(result.distances, result.fitness, result.winner)
write_html(result.trajectory, "bout.html")
```

## Design

Rabbitstew is composed of two major parts: the data structures that fully
describe robot genotypes, and the physical instantiation of robots active in a
simulation. Passive features of the environment (walls, blocks) are not a
separate category: a wall is a robot with no brain, welded to the ground.

### Genotypes (`rabbitstew.genotype`)

A genotype is a directed graph of **Nodes** with an arbitrary root. Each Node
holds one **Segment** and a list of **Connections**.

* A **Segment** has a shape (box, sphere or cylinder) and relative dimensions
  that are normalised to unit volume; absolute size is fixed at synthesis time
  by the scale factors along the path from the root. Each Segment carries a
  **Brain**.
* A **Connection** attaches a child Node with a relative position (a point of
  `[-1, 1]^3` mapped onto the parent's surface), an orientation (Euler angles
  relative to the outward normal at that point), a scale factor, a joint type
  (hinge, ball, slider or fixed) and a recursive limit: the number of instances
  of the child Node allowed along one root-to-leaf path, so that circuits in the
  graph produce repeated parts.
* A **Brain** is a directed graph of neural units with weighted links.
  **Sensors** read the environment: a binary contact sensor, and sets of three
  direction sensors giving the normalised direction, in the Segment's own frame,
  from the Segment to the world centre or to the opponent's root. **Effectors**
  send torque to the Segment's parent joint. **Neurons** are pure processing
  units. Local units may only be linked within their own Brain, except that an
  optional **global Brain** made purely of Neurons can be linked to any local
  unit. This admits fully distributed controllers, fully centralised ones, and
  hybrids.

Genotypes serialise to JSON (`Genotype.save/load`) and validate themselves
(`Genotype.validate`).

### Synthesis (`rabbitstew.synthesis`)

`synthesize()` expands a genotype breadth-first from the root, creating one
**Part** per Node instance until the externally imposed **size-ratio limit**
(maximum parts as a multiple of the number of Nodes) halts the process. The
breadth-first order expresses as many distinct Nodes as possible before the
limit bites; Nodes that are never reached are carried silently, like recessive
genetic material. Each Part gets its own instance of its Node's Brain; the
global Brain is instantiated once, and links from a Node into it are summed over
that Node's instances.

### Physical instantiation (`rabbitstew.world`, `rabbitstew.simulation`)

For each Part up to three MuJoCo objects are created: a body (mass), a geom
(collision extent) and, for all but the root, a joint to the parent. Fixed
joints weld the child to its parent. Effectors drive joint-space motors whose
gear scales with the larger of the two connected masses. Robots are synthesised
when a simulation starts and discarded when it ends. `Simulation` steps physics
and brains together; `run_bout()` runs the paper's competition and returns each
robot's final centre-of-mass distance from the world centre and the zero-sum
fitness `opponent_distance / (own_distance + opponent_distance)`.

### Brains at runtime (`rabbitstew.brain`)

All Brains of a robot are folded into one dense network updated synchronously
once per control tick (every four physics steps by default): sensors are
overwritten with their readings, every other unit computes
`tanh(bias + Σ weight · input)` from the previous tick's activations, and
effector outputs are summed per driven degree of freedom and clipped to
`[-1, 1]`.

### Trajectory file and visualizer (`rabbitstew.trajectory`, `rabbitstew.visualizer`)

The simulator and the visualizer are decoupled through a plain-text data file,
exactly as the paper lays it out: a header listing every unit's shape code and
absolute dimensions, then one line per recorded step holding a position vector
and an orientation quaternion for each unit. `visualize` turns such a file into
a self-contained HTML replay (three.js from a CDN; drag to orbit, scrub, change
speed). `simulate --view` opens MuJoCo's interactive viewer instead.

### The fixed body (`rabbitstew.fixed`)

`pioneer_genotype()` is the conventional population's body: a box chassis with
two driven front wheels and two free-rolling rear wheels, loosely modelled on a
differential-drive research robot. It is an ordinary genotype, so it goes
through the same synthesis and simulation as everything else. Its controller is
fully centralised: sensors on the chassis, hidden Neurons in the global Brain,
one Effector per drive wheel. Conventional evolution changes only the weights
and biases; `is_same_morphology()` asserts that on every generation.

### Evolution (`rabbitstew.genetics`, `rabbitstew.evolution`)

Within a population every generation is an **all-versus-best**, two-at-a-time
competition: each member is simulated against the previous generation's best
(the best meets the runner-up), and fitness comes from that bout. Survivors are
chosen by elitism and tournament selection; children come from crossover and
mutation. The holistic operators touch everything (segment shapes and sizes,
connection geometry, joint types and limits, recursive limits, the node graph,
neural units, links and weights); the conventional operators touch only weights
and biases.

At periodic intervals the top members of each population meet in **champion
bouts** which do not feed back into evolution and exist only to measure the
populations against each other. `--champion-mode best` is the paper's
best-versus-best measurement; `--champion-mode roundrobin` pits every champion
of one population against every champion of the other, from both starting
sides, which gives a far less noisy score. Everything is written to the output
directory: `config.json`, `history.json` (per-generation statistics and every
champion bout), the best genotype of every generation, the top-k genotypes of
every checkpoint, and the final populations.

### Bout gallery (`rabbitstew.gallery`)

Bouts are deterministic given the two genotypes, so nothing needs to be
recorded during evolution. `rabbitstew gallery RUN_DIR` re-simulates the bout
between the best holistic and the best conventional genotype of every
generation and writes one self-contained page: a generation slider drawn over
the champion curve, a 3-D replay of the selected bout, cards for the two
contenders (fitness, distance, parts, mass, network size), the round-robin grid
of the checkpoint when the generation was one, and the phenotype listing. Use
`--every N` to thin long runs and `--record-every` to trade replay smoothness
for page size. Each contender card carries its own small viewer of the body at
rest (drag to rotate) and an *Inspect brain* button that opens the controller as
a layered graph, sensors to neurons to effectors grouped by body part, with link
width and colour by weight.

### Report (`rabbitstew.report`)

`rabbitstew report RUN_DIR [RUN_DIR ...]` draws the champion curve, the size
of each generation's best (neural units, links, mass) and the within-population
statistics as one page. Given several runs of the same configuration with
different seeds it draws each seed thinly and the across-seed mean emphasised.

### A note on fairness

Holistic bodies can grow: a child part may be up to 1.2 times its parent's
size and the largest part may reach 0.6 m, so a holistic creature can weigh
several times the 15 kg fixed body, and in a shoving contest mass is an asset
regardless of control. `--mass-budget KG` (a `SynthesisConfig.mass_budget`)
scales every part's mass of any heavier robot down to the budget, leaving its
geometry untouched, so that both populations compete at the same weight.

## Exploring beyond the paper

The paper's brain model is deliberately minimal, and a minimal brain is
exactly what a wheeled box is good at using. Three switches open the problem
up; all of them default to the paper's setting.

* **`--brain-model rich`** adds sensors (orientation, body velocity, distance
  to target and opponent, joint angle and velocity, height, and free-running
  oscillators), neuron transfer functions beyond `tanh` (`sin`, `abs`, `relu`,
  `sign`, a leaky `integrate`, `differentiate`) and motor modes beyond raw
  torque (`position` and `velocity` servos, per joint). The fixed body gets the
  sensors a real research robot has (orientation, velocity, distances, wheel
  speeds) so it is not handicapped in sensing.
* **`--conventional-topology`** lets the fixed body's controller *topology*
  evolve too: neurons in the global brain are added, removed and re-typed and
  links anywhere are added and removed, while the body and its mounted sensors
  and effectors stay fixed. With it, the only difference between the two
  populations is whether the body evolves.
* **`--terrain plateau|rails`** replaces the flat arena with a task a wheeled
  box cannot win by driving: a raised central disc higher than the wheel
  radius, or a field of low rails taller than the chassis clearance. The target
  point moves to the plateau top; terrain appears in every replay.

Long runs checkpoint after every generation (`state.json`) and continue with
`--resume`, optionally to a higher `--generations`.

## Analysing what evolved (`rabbitstew analyze`)

Win rate against one opponent says who won, not what evolved.
`rabbitstew analyze RUN_DIR` measures every fifth generation's best of both
populations with the robot alone, and writes `analysis.json` and
`analysis.html` into the run directory:

* **Solo capability trials**: approaching a goal on flat ground (progress,
  speed, straightness, falls, actuator work per metre), steering to goals at
  90°, −90° and 180° from the initial heading, crossing a fixed bank of six
  random terrains, and pushing a passive block.
* **Structural descriptors**: expressed versus recessive nodes, parts, depth,
  branching, mirror symmetry, ground footprint, joint / motor / shape
  fractions; connected units, driven effectors (and how many an oscillator
  drives), sensor-to-effector path length, recurrence, centralisation.
* **Functional network analysis**: a static influence of every sensor on the
  live effectors, and a lesion map (`--lesions final|all|none`) that silences
  each unit in turn and measures the approach progress lost.
* **Population level**: descriptor diversity of the checkpoint champions and
  the final population, and, from `lineage.jsonl` (every individual's parents,
  fitness and size, written each generation), the ancestry of the final best
  and how many generation-0 founders the final population descends from.

## The ecology's economy (`rabbitstew ecology`)

`rabbitstew ecology` replaces the GA's ranking and culling round with energy,
age, births and deaths: each season an individual faces a challenge, gains
energy equal to its score, pays a living cost, breeds when it can afford the
birth threshold and a slot is free, and dies of starvation or old age.

**The economy must be absolute.** The living cost is a fixed charge
(`--living-cost`, default 0.05) against a gain that comes from the world, so
energy enters the population and an individual that scores above the cost
accumulates it however well its neighbours are doing. This is the only
arrangement in which a competent population keeps reproducing, and it is what
the foraging world uses.

**The default cost is a parameter, not a result.** 0.05 was chosen by measuring
what random founders of both populations earn on the ecology's own default
challenge (solo, closeness score, random terrain and start, 10 s, 60 per
population, four seasons' draws; `scripts/calibrate_cost.py` reproduces the
table, and `--living-cost` is the knob if your challenge pays differently):

| living cost | holistic founders net positive | wheeled founders net positive | seasons a zero-scorer lives |
|---|---|---|---|
| 0.02 | 15% | 47% | 100 (longer than the 60-season lifespan: starvation never bites) |
| **0.05** | **7%** | **35%** | **40** |
| 0.10 | 2% | 32% | 20 |
| 0.25 | 0% | 17% | 8 |

0.05 is the largest charge under which both populations still have founders
that pay their way, and the smallest under which starvation happens at all
within a lifespan. At 0.25 no random holistic body is net positive, so that
side is extinct before anything can evolve, which is the bootstrap failure the
sparse foraging arm hit; at 0.02 nobody starves and turnover is by age alone,
which is the neutral-drift control rather than an economy.

Forty seasons at the default settings (capacity 60, seed 3) say the economy
works: the wheeled population holds all 60 slots throughout, replacing 40
deaths with 40 births while its mean lifetime score goes 0.077 to 0.244. The
holistic population bottlenecks from 60 to 23 on two births, which is the
random-body bootstrap problem the sparse foraging arm also hit and not a
property of the cost. Under the retired relative cost neither population can
breed at all once it converges, however well it does.

Two economies where the energy comes from the neighbours instead are retired
(Chaotic RBT-8). They are still reachable, so that paper 3's runs reproduce,
but they are not defaults and selecting either warns:

* **`--living-cost relative`** charges each population its own mean gain that
  season. Energy is then conserved exactly, and a birth needs somebody a whole
  threshold above their own contemporaries: the better and more alike a
  population becomes, the less anyone can breed. Paper 3's solo ecology aged
  out at 196 seasons without a single birth on the holistic side.
* **`--challenge paired`** scores a random pairing 0 and 1 whatever either
  robot did, so the pot is fixed and energy tracks a win rate rather than
  anything the world yields. Paper 3's paired ecology took 444 seasons to die
  instead of 196.

`docs/paper-3-let-the-furniture-stop-me.md` reports both extinctions, and
`docs/foraging-world.md` is the absolute economy that replaced them.

## Departures from the paper

* **Physics engine.** MuJoCo instead of PyODE. The body / geom / joint model
  is the same; a fixed joint is a welded child body rather than a joint object.
* **Joint axis and limit.** A Connection carries two fields the paper does not
  list: the hinge or slider axis in the child's frame, and an optional joint
  limit. Without them evolved bodies fold through themselves and a wheel cannot
  be expressed. Both are evolvable in the holistic population.
* **Surface attachment and sizing.** The paper leaves open how a Connection's
  relative position maps onto the parent and how absolute size is derived. Here
  the position is projected onto the parent's surface, the child's local X axis
  points along the outward normal there (before the Connection's own rotation),
  and a child's characteristic length is the parent's times the Connection's
  scale, clamped to a configurable range.
* **Direction sensors** are expressed in the Segment's own frame rather than
  the world frame, so a controller can steer without knowing its own heading.
* **Champion measurement.** Round-robin champion bouts are offered alongside
  the paper's best-versus-best, as its own footnote suggests.
* **Visualizer.** An HTML replay instead of VPython. The orientation math uses
  the active rotation `q v q'`; the paper writes the product the other way
  round, which is the inverse rotation under the ODE/MuJoCo convention.

## Layout

```
rabbitstew/
  genotype.py     Nodes, Connections, Segments, Brains; JSON; validation; random generation
  synthesis.py    breadth-first genotype -> phenotype expansion
  world.py        MuJoCo model construction (bodies, geoms, joints, motors)
  brain.py        runtime neural networks
  simulation.py   stepping, sensing, bouts, fitness
  trajectory.py   the data file shared with the visualizer
  visualizer.py   HTML replay export, shared replay scene, orientation helpers, live viewer
  gallery.py      per-generation champion-bout gallery with a slider
  analysis.py     descriptors, solo trials, lesion maps, diversity, lineage
  analysis_page.py  the analysis page
  fixed.py        the Pioneer-style fixed body
  genetics.py     mutation and crossover (holistic and weights-only)
  evolution.py    populations, all-versus-best, champion bouts, experiment driver
  cli.py          the `rabbitstew` command
tests/            pytest suite
```

## Standing rule: lab every champion

Any evolved robot that reaches competence gets a lab before anything is claimed about it: a fresh-draw time at target of 0.2 or more on the redesigned task, or a forager whose yield depends on a sensor. The lab is `scripts/lab.py RUN KIND GEN`, which dumps the phenotype's units and links and then measures, on fresh draws the run never saw, every lesion that matters: environmental sensors blanked, oscillators blanked, the global brain silenced, the local brains silenced, and each linked unit silenced alone, each with progress, time at target, path length, straightness, arrival time, hold fraction after arrival and actuator work. Claims about what a champion is are made from that table and the wiring, not from its score. Reports on delegated runs (Chaotic RBT) include the table for every champion they produce.

Stills of a champion (four frames of a solo bout plus two close-ups on one sheet) come from `scripts/shots.py RUN KIND GEN OUTDIR`, which drives the project's replay page in headless Chromium; the sheets for A-301, cap-401 and cap-403 are in `docs/img/`.

## Queued runs

`scripts/run_sims.sh SEED [GENERATIONS]` is the Sims-budget run: population 300, (mu+lambda) survival, epsilon-lexicase over the five-objective score vector, mirrored connections, and neighbour links so that distributed control between parts is expressible as in Sims (1994). It is scored on a dense solo score rather than a bout, because the bout format is where paper 3 found the heritability going; the design, that argument and the measured cost (about nine minutes per generation on four cores) are in `docs/sims-budget-run.md`.

`scripts/run_forage.sh SEED SEASONS BASAL WORKCOST` is the foraging ecology; see `docs/foraging-world.md`.
