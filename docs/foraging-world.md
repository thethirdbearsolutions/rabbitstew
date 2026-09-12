# The Foraging World

A third challenge for the ecology, and the first world in this series that is not a task.

## Why

The lesion study (paper 4) showed that every evolved controller with any competence is a reflex arc from a sensor that already contains the answer: the target direction, handed to the robot in its own frame. Reaching a point is a one-dimensional demand that one arc satisfies, after which nothing further is asked, and nothing in the world persists, depletes or pushes back. The foraging world removes all three conveniences at once, for both populations equally, and encodes no answer.

## What

- **Food.** Items lie in a disc around the centre. A robot eats one by bringing any part of itself within the eat radius; the item then regrows at a new random position drawn from the season's seed.
- **No oracle.** The `foraging` vocabulary drops the target and opponent direction and distance sensors. In their place are two smells: `food` and `agent`, the summed intensity `sum(exp(-d / decay))` of food items and of other robots at the sensing segment's own position, squashed to (0, 1). A gradient exists only between two segments in different places or across one segment's motion. The designed bodies get a nose on the chassis and one on each drive wheel or leg, so a Braitenberg pairing is available to them too.
- **An economy.** Energy is food eaten times its value, minus a work cost per kilojoule of actuator effort and, in the ecology, a basal living cost per season. Under the ecology's `foraging` challenge, groups of robots share one arena each season and compete for the same food; birth, death and carrying capacity follow from the economy rather than from a rank.

## How to run

```
rabbitstew ecology --challenge foraging --brain-model foraging --food-items 12 --food-radius 3 \
    --living-cost 0.1 --work-cost 0.05 --group-size 4 --seasons 600 --capacity 60 \
    --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --seed 801
```

`rabbitstew evolve --score food --brain-model foraging --food-items 12 ...` runs the GA on the same world with a solo food score, for comparison.

## Calibration (random robots, 15 s, groups of four, 12 items in a 3 m disc, food never within 0.8 m of a robot)

| | eat anything | items eaten, median / 90th pct | actuator work, median | displacement, median |
|---|---|---|---|---|
| random holistic genotypes (n=32) | 6% | 0 / 0 | 0.01 kJ | 0.07 m |
| Pioneer with random weights (n=16) | 81% | 1 / 3.5 | 17.5 kJ | 1.8 m |

Chosen economy: food value 1, basal cost 0.25 per season, work cost 0.03 per kJ, initial energy 3, birth at 3, birth cost 1, lifespan 60 seasons. A lump that never eats lives twelve seasons on its birth energy. A median random Pioneer nets about +0.2 a season; its best decile about +2.5. The holistic population must find eating before it runs out of founders, which is the demand.

## The economy's coefficients are a parameter, not a result

The basal and work costs were chosen while looking at both populations' random yields, which is where thumbs come from. Two arms therefore run on the same seed: `forage-801` with the work cost at 0.03 per kJ, and `forage-freework-801` with the work cost at zero, so that moving is free and only the basal cost applies. A finding that flips between them is a finding about the coefficient and is not reported as anything else.

## What we expect, written before the run

- Random lumps mostly starve; a body that moves at all eats occasionally; a Braitenberg pairing of two noses on two segments is the first thing worth finding, and finding it needs a body with two segments apart.
- The Pioneer arrives able to move and with two noses on its wheels; the question is whether controller evolution finds the pairing before the holistic search finds a body that can.
- The measurements that were flat in every task so far, proprioception influence, cross-part links (with `--neighbour-links`), state-holding units, are the ones that would move if the world is now asking for them. If they stay flat here too, the answer is the search, not the world.

## First forty seasons (seed 801, work cost 0.03; the zero-work-cost arm matches in shape)

**Selection without a ranking worked.** The holistic population fell from 60 to 7 at season 11, when the founders that never ate starved together, held at 7 to 11 for ten seasons, then regrew to 60 by season 32 with the mean energy gain rising from +0.02 a season to +0.79. Every individual alive at season 39 descends from one founder; the wheeled side kept 16 of its 60. The path the best holistic individual covers alone in a season went 2.3 m, 2.9 m, 3.9 m, 7.2 m at seasons 0, 10, 20, 30, on 3.5 kJ where the Pioneer spends 17. Locomotion evolved from survival alone.

**But it is blind.** The eater lineage carries no food sensor at all, only a joint-angle sensor that does nothing: blanking every sensor, or silencing every local brain, changes neither its path nor what it eats. It is a random-walk grazer, and its yield is what a random walk of its length should encounter: path times twice the eat radius times the food density. The Pioneer's best at season 0 was a situated forager, chemotaxis on its wheel noses, losing five sixths of its food when they were blanked; by season 20 blanking the noses raised its yield, and by season 30 its best ate more with every environmental sensor off. Both populations converged on mowing.

**Why: the food is too dense.** With 12 items regrowing instantly in a 3 m disc, a random walk of 7 m meets about two items a season for a cost of 0.36 energy, so blind grazing is comfortably net positive and sensing is an expense. The break-even density for a blind grazer of that path and cost is about 0.07 items per square metre, two items in the disc. Below it, only a robot that finds food faster than chance can live. A third arm, `forage-sparse-801`, runs the same seed and economy with 3 items, pre-registered as the density at which a blind grazer is marginal; if sensing is ever going to earn its keep in this world, it is there.

## The sparse arm: extinction on both sides (3 items, work cost 0.03)

The wheeled population went 60, 38, 9, 6, 4, 2, 0 over seasons 0 to 10: a random-weight Pioneer eats about a quarter of an item a season on three items and pays 0.75 in work and basal cost. The holistic population held near 50 until its founders' energy ran out together at season 11, when 38 starved in one season; 3 survivors ate about 0.24 a season against a basal cost of 0.25 and died out by season 24 without one birth. Neither random population can bootstrap at this density under this economy. The paired arm with zero work cost, `forage-sparse-freework-801`, is running to separate the density from the coefficient: at zero work cost the Pioneer's founders keep 0.5 more a season, and if it survives there and not here, the sparse result is about my coefficient and not about the body.

**Season 100, dense arm.** Still blind on both sides. The holistic best is a four-part, sixteen-unit body with one joint-angle sensor and no nose; alone in the arena it eats 2.25 items a season over an 11.9 m path on 4.8 kJ, and no lesion changes any of it. Its path has lengthened from 2.3 m at season 0 to 11.9 m at 100 while its energy per metre fell; what evolved is efficient locomotion, selected by survival, and nothing that senses. The Pioneer best at season 100 eats 1.0 items intact, 1.4 with its noses blanked and 1.5 with every sensor blanked, on 20 kJ. In a world where blind mowing pays, both populations converged on it, and the evolved body mows on a quarter of the energy.

**Season 200, dense arm.** The holistic best at 150 is the strongest mower yet, 2.5 items alone on 5.6 kJ, and still blind: sensors change nothing, and silencing the local brains costs it two thirds of its yield because its constant drive runs through local neurons. The best at 200 carries food and agent sensors for the first time, and they do nothing. The Pioneer best at 200 has become sensor-dependent again, 1.62 items intact against 0.38 with every environmental sensor blanked, when it runs off at 6.6 m displacement; but the noses account for little of that (1.38 with only the noses blanked). What it uses is orientation and velocity to hold a circling gait inside the food disc, situated in the sense of staying where the food is, not of smelling it.

**Seasons 300 and 400, dense arm.** The holistic best at 300 carries a food sensor and, on eight seeds, loses half its yield when it alone is blanked (1.75 to 0.88 items) but none when every sensor is blanked (1.88): the food input's job is to cancel a harmful joint-angle input, not to steer, and the bias-only gait underneath is a 9 m mow on 2.3 kJ, the cheapest locomotion in the series. The best at 400 has no nose again and eats 2.38 items alone with no lesion touching it. The Pioneer bests at 300 and 400 eat 1.25 and 0.88 intact and 1.62 and 1.38 with sensors blanked. Four hundred seasons in, the dense world has produced ever cheaper blind mowing on the evolved side and nothing on either side that smells.

**The zero-work-cost dense arm, complete (600 seasons).** Mean energy gain at seasons 100, 300, 500 and 599: holistic +0.97, +1.34, +1.28, +1.24; wheeled +0.98, +1.00, +1.00, +1.14. Both populations full throughout after the holistic bottleneck; the holistic side descends from one founder of sixty, the wheeled from twelve. The final holistic best (seven parts, 44 units, sensors for food, orientation and velocity) eats 1.25 items alone on 1.8 kJ whether its sensors are on or off, and 1.88 with its local brains silenced. The final Pioneer best eats 1.00 intact and 1.62 with every sensor blanked; its season-500 predecessor does not move at all without its sensors, its drive being gated through orientation and velocity inputs, and eats nothing. With moving free the picture is the same as under the work cost: cheap blind mowing on the evolved side, sensing that costs more than it earns on the designed side, and no chemotaxis anywhere in six hundred seasons.

**The first dense arm, complete (600 seasons, work cost 0.03).** Mean energy gain at seasons 100, 300, 500 and 599: holistic +1.02, +1.19, +1.63, +1.41; wheeled +0.96, +1.03, +0.94, +0.95. Both populations full from season 32 to the end; the holistic side descends from one founder, the wheeled from seven. The holistic best at 500 eats 2.12 items alone over an 11.4 m path with one joint sensor and no lesion effect at all; the best at 590 has seven parts and eats more with its local brains silenced. The Pioneer best at 500 is the one controller in six hundred seasons of either dense arm whose noses demonstrably work: intact it eats 1.00 and stays in the disc; with the noses blanked it drives 19 m in a straight line and eats 0.12. Its noses do not steer it to food; they stop it leaving. The best at 590 keeps a weaker version (1.62 intact, 1.12 without noses).

**The drift baseline.** The neutral control (same bodies, same seasons, no starvation, free breeding, turnover by age only) finished its 600 seasons with 14 holistic and 16 wheeled founders of 60 still in the ancestry and means unchanged from season 0. Drift alone at capacity 60 over ten lifespans keeps a quarter of the founders. The foraging arms' one holistic founder is the season-11 bottleneck, selection through starvation, not drift; the wheeled side's 7 to 12 is between the two, a population that was selected but never bottlenecked.

**What the foraging world showed, in one paragraph.** An economy with no fitness function and no ranking evolved locomotion from survival alone, through a founder bottleneck, in every dense arm, and the evolved bodies ended up out-eating the designed one on a fraction of its energy. It did not evolve sensing, because at twelve items blind mowing pays and at three nobody random can live, and in between a small population dies of bad luck. The one situated controller that appeared, a Pioneer whose noses keep it from driving away, is a brake rather than a compass. Whether a fauna that already lives can be walked into a poorer world where mowing stops paying is the range-expansion question, banked below with the interchange.

**The sparse pair, resolved.** With moving free, the wheeled population never dipped: 60 alive at every season, mean gain +0.21 at season 11 and +0.32 at season 32, turning over ten or more a season. The wheeled extinction on sparse food was the work-cost coefficient and nothing else. The holistic population followed the same course in both arms, since a lump's budget never depended on the work cost: 45 starved together at season 11, the last four ate a third of an item a season, bred nothing, and the last one died at season 31. Random lumps cannot bootstrap on three items; blind grazing is comfortable on twelve. A density series is therefore the next arm, pre-registered as such: `forage-mid-801` runs six items on the same seed and economy, between the density where a blind grazer is marginal and the one where it is comfortable.

**The sparse wheels-only arm, complete (600 seasons, moving free).** The Pioneer population stayed full from season 11 to the end at a mean gain of +0.36 to +0.45, and never used its nose. The best at season 0 lost half its yield with the noses blanked; the bests at 400 and 590 eat a quarter of an item a season alone whether the noses, or every environmental sensor, are on or off. Six hundred seasons on three items, where finding food faster than chance is the only way to eat more, did not select chemotaxis into a body that arrived with the sensors and the wheels to do it. On yields of a quarter of an item a season, a solo season cannot tell a chemotaxer from a wanderer, and selection had nothing to work with that drift did not swamp.

**Six items.** The holistic population starved out at season 15 (37 deaths at season 11, two survivors that ate a twelfth of an item a season). The wheeled population, under the work cost, bottlenecked to 11 by season 17 with a positive mean gain of +0.32 and kept breeding: the first time the Pioneer side has been selected rather than merely sustained. It then held at five to nine for twenty seasons, a young breeding population with a positive budget, and went extinct at season 51 anyway: at that size a couple of unlucky seasons remove the eaters faster than they breed, which is demographic stochasticity, not starvation of the type. Random lumps therefore bootstrap somewhere between six and twelve items in this disc; under the work cost the wheels are marginal at six and gone at three, and without it they live at three. The dense arms meanwhile crossed over at season 83: holistic mean gain +1.02 against wheeled +0.94.

A further option, banked rather than run: a range expansion, in which the population that evolved at twelve items is carried into six and then three, as a colonising fauna meets a poorer habitat. It needs the ecology to start from a saved population, which is the same machinery the interchange needs.

## Why sensing did not evolve, and the banked world that would give it a hill

Lifetime foraging yield is heritable in the ecology: parent-child correlation 0.51 (holistic) and 0.24 to 0.39 (wheeled) across both dense arms, against zero for any bout outcome in this series. The search had signal. What it lacked was a slope toward sensing. The world has one hill, move more for less, which bias mutation climbs. Sensing is a cliff: a Braitenberg pairing needs two noses on separated segments, crossed wiring and the right signs before it earns one extra item, and with food regrowing instantly at random a half-built nose earns nothing. The one nose-dependent behaviour that did appear, a Pioneer whose noses keep it from driving out of the disc, is a one-bit skill that one sensor and one weight can express.

**Banked: a persistent world.** Food in patches that deplete when eaten and regrow slowly; food state carried across seasons instead of reset; a smell that carries over several metres. A weak nose bias then pays a little, because drifting toward a patch edge beats drifting away, which is the slope the cliff lacked; leaving an exhausted patch and remembering where another was become graded skills, which is what integrators are for; and a neighbour eating the patch you are on is a challenge rather than noise. None of it encodes an answer and all of it applies to both bodies alike. The range expansion and the interchange run on this world.

## World fan-out (delegated arms, Chaotic RBT-13 to RBT-21; results on branches results/RBT-n)

All arms change one thing from forage-801 on the same seed and ask one question: does the variant give sensing a slope? Rows fill in as the arms report.

| Arm | Change | Outcome | Sensing? |
|---|---|---|---|
| W2, RBT-14 | 6 items in a 4 m disc, smell decay 3 m | wheeled extinct at 23, holistic at 31; 0.12 items/m² is the sparse arm's density and nothing bootstraps; tripling smell reach changed no founder's yield | no fauna to select |
| W3, RBT-15 | 60 s seasons, 6 items, basal 1.0 | both extinct by season 6; the arm reproduced the fatal six-item economy per simulated second and never isolated season length (design error, mine); corrected as W3' | no fauna |
| W6, RBT-18 | work cost 0.15 per kJ | wheeled extinct at 3, holistic at 33; the founder that carried the baseline became a subsister at this coefficient; the one nose that worked (a season-0 Pioneer, 57% of food lost when blanked) was bankrupt by its wheels | a founder's nose, dead by season 2 |
| W1, RBT-13 | smell decay 3 m at baseline density | pending | |
| W4, RBT-16 | no regrowth within a season, 24 items | pending | |
| W5, RBT-17 | eight robots per arena | pending | |
| W3', RBT-20 | 60 s seasons at baseline density, basal 1.0 | pending | |
| W6', RBT-21 | work cost 0.08 per kJ | pending | |
| P, RBT-19 | persistent world: patches, regrowth delay, state across seasons, smell 3 m | pending | |

Lesson of the first three: a world variant is only informative at a density and economy where random founders form a breeding population; below that line every arm measures the bootstrap threshold and nothing else.

## Banked next move: the interchange

The two ecologies never meet as they stand. The head-to-head, when it comes, will be run two ways. As measurement: individuals from each ecology placed in the other's world without selection, the old bout for the paper's question and a mixed foraging arena for who eats more when food is shared. As ecology: the two populations evolve apart for a pre-registered number of seasons, then merge into one arena with one pooled capacity, births of either kind taking any free slot, and the run records which fauna persists. The merge season and the pooled capacity are fixed in advance, because both are places a thumb could rest. Not to be built until the separate runs show whether the holistic side finds eating at all.
