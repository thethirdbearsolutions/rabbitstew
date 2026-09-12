# The Sims-budget run

*Pre-registered design and measured cost. Written before the run; results will be
appended without editing this section.* (Chaotic RBT-5.)

## The question

Every condition in this series so far has been run at population 20, 30 or 60. Sims
(1994) ran 300. The ticket that asks for this run asks a narrow version of a broad
question: does the search find anything different when it is given Sims' population
and Sims' encoding, rather than Sims' task?

Three things change together, and the run cannot separate them:

- **Population 300.** Fifteen times the population of every condition in papers 3 and
  4. Founder collapse at population 20 is drift and nothing else: an ancestry-only
  model of the reproduction scheme coalesces to about four founders by generation 50
  under fitness that is pure noise, and the runs match the noise case.
- **`--neighbour-links`.** A local brain may read the units of nodes it is joined to,
  which is how Sims expressed distributed control between parts. Without it every
  local brain is an island and coordination has to route through the global brain,
  which in all three labbed champions of this series carried exactly one number.
- **(mu+lambda) survival with epsilon-lexicase.** Parents persist, are re-evaluated
  every generation and compete with their children on running-mean fitness, and
  parents are chosen by shuffling the five objectives rather than by scalarising them.

## The score: solo, not bouts

Fitness is closeness (progress integrated over the whole bout) evaluated **solo for
the whole run**. `--locomotion-phase` is pinned to the run's length, so champion bouts
still run at the checkpoint interval but return a measurement only; nothing a bout
returns feeds selection. This is the arrangement of the paper 4 capacity runs.

That is a departure from the ticket's own description of the configuration, and it is
the one decision here worth arguing. Paper 3 measured realised heritability of the
holistic population's fitness under a zero-sum bout at 0.05 or less, at one, two and
four bouts per individual, while the identical dense score used solo gave 0.35 to
0.41. Four bouts per individual instead of one should halve sampling noise in the
score; the holistic heritability does not move, so the noise is not draw-to-draw
variance that averaging removes. Under condition C a solo phase built a fresh-draw
time at target of 0.31 in sixty generations and twenty generations of bouts took it
back to 0.02. Fifteen times the population does not repair a score with no heritable
signal in it; it buys fifteen times as much drift. Pass `--locomotion-phase 0` to run
the bout-scored arm anyway.

One consequence had to be checked rather than assumed. `_select` falls back to
tournament selection when `Population.vectors` is empty, so moving to a solo score
could have made `--selection lexicase` a silent no-op. It does not: the solo path
records the same five-objective vector (closeness, time at target, waypoints,
uprightness, and progress per kJ of actuator work) that the bout path does, and every
lineage row of a solo run carries one.

## Cost

Measured on a 4-core box at the script's defaults (population 300, 15 s bouts, four
draws per individual, rich brain model, four workers), three generations, seed 96:

| Generation | Wall clock |
|---|---|
| 0 (children only) | 283 s |
| 1 (survival: parents re-evaluated) | 552 s |
| 2 | 565 s |

Roughly nine minutes per generation in the steady state, so a hundred generations is
about sixteen hours of wall clock on four cores and two hundred is about thirty-two.
The ticket that requested the run estimated hours *per generation*; that is wrong by
a factor of tens at the start of a run. The estimate should be treated as a floor rather than a forecast: the holistic
body distribution keeps moving over a long run (one paper 3 best had sixteen
parts and 133 units at generation 150 and four parts and 66 units at generation
199), and the per-bout cost moves with it. It is a run to queue behind free
cores, not a run to rule out.

## Reproducibility

```
scripts/run_sims.sh SEED [GENERATIONS] [EXTRA...]
```

which is

```
rabbitstew evolve --population 300 --generations N \
    --survival --selection lexicase --mirror --neighbour-links \
    --score closeness --locomotion-phase N \
    --terrain random --random-start --mass-budget 15.34 --conventional-topology \
    --brain-model rich --duration 15 --draws 4 \
    --champion-interval 5 --workers $(nproc) --seed SEED --out runs/sims-SEED
```

`NAME`, `POP`, `DURATION`, `WORKERS`, `DRAWS`, `BRAIN` and `CHAMPION_INTERVAL`
override the defaults from the environment; anything after the generation count is
passed through to `evolve`, so `--archive` and `--heading-curriculum` are available
without editing the script.

Neighbour links are expressed, not merely permitted. In the final holistic population
of the three-generation cost run above, 15,484 of 31,415 local brain links read a
neighbouring node's units; in an otherwise identical run with the flag omitted, zero
of 219 do.

Heritability is `rabbitstew heritability RUN`, windowed. Capability numbers are
fresh-draw solo scores from `scripts/eval_fresh.py RUN 20 12` (every twentieth
generation's best, twelve draws seeded outside the run's own range), never a
training-draw best. Any champion that reaches competence gets a lab under the
standing rule before anything is claimed about it.
