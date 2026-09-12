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
