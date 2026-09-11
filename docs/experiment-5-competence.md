# Experiment 5: Competence, not position

*Pre-registered design. Written before the runs; results will be appended without editing this section.*

## The question

The competitive race of the original proposal has been answered: a designed wheeled body with an evolving controller beats co-evolved bodies on every clean run. The claim underneath the proposal is different and still open: that evolving body and brain together produces *competence* a designer did not build in, and that a designed body is not always the easier place to start. The capacity runs gave the first hint that the second half might be true: a hand-designed quadruped driven by controller evolution alone is, so far, harder to make walk than a body the search designed for itself.

This experiment asks two things with the opponent removed and the task demanding competence:

1. **Starting point.** Given the same task, the same operators and the same budget, which starting point produces the most competent robot: a random body evolving with its brain, a designed body evolving with its brain, or a designed body whose brain alone evolves?
2. **Coupling.** When a body and brain co-evolve, is the pair worth more than its parts: does the native brain outperform a fresh brain re-evolved on the same body under the same budget, and does the body outperform a designed body under a re-evolved brain?

## Task

Solo, on random terrain resampled every generation, from rest, at equal mass, with random start bearing, distance and heading. Fitness is time at the target plus a small progress term, and once a robot has held the target for one second the target moves 1.5 m in a random direction, up to three times per bout. A robot that cannot turn scores at most one waypoint; a robot that cannot hold position scores none. Every start, terrain and waypoint sequence is seeded and shared by the whole generation.

## Conditions

All with the rich brain model, population 30, 250 generations, two start draws per individual per generation, a descriptor archive for any population whose body evolves, and mirrored connections allowed.

| Condition | Body | Brain | Starting point |
|---|---|---|---|
| **H** | evolves | evolves | random genotypes |
| **Q+** | evolves | evolves | the designed quadruped |
| **Q** | fixed quadruped | topology and weights evolve | the designed quadruped |
| **P** | fixed Pioneer | topology and weights evolve | the designed Pioneer |

Three seeds each. H against Q+ tests whether a designed body is a better place to start body evolution than nothing. Q+ against Q tests whether letting the designed body change helps or hurts. Q against P is the wheel control: on mostly crossable ground a wheel should remain the most competent body, and if a quadruped or an evolved body beats it on waypoints, that is a result about steering and holding, not driving.

## Measurements

Every tenth generation's best, and every checkpoint's top five, go through the analysis toolkit: solo trials (approach, steering to three bearings, terrain bank, pushing, work per metre), descriptors, lesion maps, sensor influence, diversity and ancestry. At the end of each run:

- the final best's waypoints per bout over 20 fresh draws (the primary outcome);
- **coupling tests** on H and Q+ finals: a fresh controller evolved for 60 generations on the champion body (condition Q-style, `--fixed-body FILE`), compared with the native controller on the same 20 draws; and brain-only ablations (links zeroed, links random) as in the synergy profile;
- **cross-play** as a secondary measure only: the finals of all four conditions meet in a round robin under the original competitive score, so that the two questions, competence and winning, are reported side by side and never conflated.

## Pre-registered expectations

- Q, the designed quadruped with an evolving brain, will reach fewer waypoints than H by generation 100 and may or may not catch up by 250. If it never does, controller evolution on a body built for gaits is the bottleneck of this whole series.
- Q+ will reach more waypoints than Q (the body is allowed to simplify) and more than H early on (it starts able to stand); whether it holds that lead is the open question.
- P will reach the most waypoints of all on this terrain. If it does not, the wheel's advantage in the competitive runs was about driving straight, not about competence.
- Native brains will outperform re-evolved brains on H finals only if a real coupling exists; our prior, from the ablations so far, is that they will not.

## Budget

Twelve runs of about 250 generations at 30 individuals and 2 draws: roughly 60 solo simulations per generation per run, about 25 seconds per generation per core, about 1.7 hours per run, about 5 hours wall on four cores for the twelve runs, plus about an hour of analysis and coupling tests.

## Commands

```
rabbitstew evolve --terrain random --mass-budget 15.34 --random-start --score time_at_target --waypoints 3 \
    --locomotion-phase 250 --generations 250 --population 30 --draws 2 --brain-model rich --mirror --archive \
    --champion-interval 0 --seed 601 --out runs/e5/H-601                      # H
rabbitstew evolve ... --holistic-seed quadruped.json --seed 601 --out runs/e5/Qplus-601      # Q+
rabbitstew evolve ... --conventional-topology --fixed-body quadruped --seed 601 --out runs/e5/Q-601   # Q (read the conventional population)
rabbitstew evolve ... --conventional-topology --fixed-body pioneer --seed 601 --out runs/e5/P-601     # P (read the conventional population)
rabbitstew analyze runs/e5/H-601 --every 10
rabbitstew synergy runs/e5/H-601
```
