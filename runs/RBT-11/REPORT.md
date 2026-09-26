# RBT-11: Sims-budget solo run (population 300, survival + lexicase, mirror, neighbour links)

Run `runs/RBT-11/sims-901`, seed 901, 150 generations (checkpoints `best_gen0000` to `best_gen0149`), whole run solo (`--locomotion-phase 150`), closeness score, random terrain, random starts with a 100-generation heading curriculum, two draws per member per generation, population 300 in each of the holistic and wheeled (Pioneer body, evolving controller topology) populations. Every capability number below is on draws the run never saw.

## Deviations from the ticket

- **The box had 4 cores, not 16+**, so the run used `--workers 3`. A generation (1,200 solo simulations) took 200 to 207 s throughout; the run took 8 h 20 min wall-clock (11:20 to 19:40 UTC) and completed all 150 generations, so nothing was cut short.
- The last checkpoint is `best_gen0149.json` (generations are numbered from 0); the ticket's `best_gen0150.json` does not exist. The lesion script was pointed at 0149.
- Results are on branch `claude/dazzling-lamport-y47veb` (the branch this session was told to use), not `results/RBT-11`.
- `lineage.jsonl` is 53 MB, over the 50 MB threshold the ticket set for `state.json`, so it is committed gzipped (`lineage.jsonl.gz`, 5 MB; `gunzip -k` restores it for the heritability and founder tools). `state.json` (11 MB) is committed as is. `analysis.html` is not committed.
- `runs/` is git-ignored in this repository; the files were added with `git add -f`.

## 1. Fresh-draw evaluation (12 unseen draws, seeds 5000-5011, `scripts/eval_fresh.py`)

Score is the closeness score, `tat` the fraction of the 15 s bout spent within 0.5 m of the target, progress is metres gained towards the target.

| gen | holistic score | holistic tat | holistic progress | wheeled score | wheeled tat | wheeled progress |
|---|---|---|---|---|---|---|
| 0 | 0.16 | 0.00 | +0.12 | 0.53 | 0.42 | +0.81 |
| 10 | 0.25 | 0.08 | +0.22 | 0.56 | 0.36 | +0.67 |
| 20 | 0.13 | 0.00 | +0.11 | 0.56 | 0.51 | +0.72 |
| 30 | 0.22 | 0.13 | +0.26 | 0.46 | 0.39 | +0.55 |
| 40 | 0.24 | 0.01 | +0.26 | 0.65 | 0.61 | +0.75 |
| 50 | 0.15 | 0.00 | +0.13 | 0.69 | 0.69 | +0.84 |
| 60 | 0.18 | 0.02 | +0.18 | 0.66 | 0.60 | +0.80 |
| 70 | 0.22 | 0.06 | +0.23 | 0.67 | 0.65 | +0.78 |
| 80 | 0.21 | 0.07 | +0.22 | 0.62 | 0.54 | +0.77 |
| 90 | 0.45 | 0.19 | +0.52 | 0.62 | 0.61 | +0.72 |
| 100 | 0.20 | 0.05 | +0.24 | 0.69 | 0.71 | +0.83 |
| 110 | 0.19 | 0.01 | +0.19 | 0.70 | 0.68 | +0.78 |
| 120 | 0.39 | 0.15 | +0.43 | 0.73 | 0.76 | +0.84 |
| 130 | 0.25 | 0.12 | +0.19 | 0.69 | 0.70 | +0.79 |
| 140 | 0.44 | 0.16 | +0.51 | 0.69 | 0.68 | +0.83 |
| 149 | 0.38 | 0.16 | +0.42 | 0.69 | 0.71 | +0.80 |

Training best-of-generation (the run's own two draws) for the holistic best was 0.66 at generation 149 against 0.38 fresh: the winner's curse of paper 4 is still there at population 300.

**Tighter estimate of the finals** (`fresh24.py`, 24 further unseen draws, seeds 7000-7023, disjoint from the sets above and from the lesion set):

| best | score | tat | tat sd | progress | draws with tat ≥ 0.5 | draws with tat = 0 |
|---|---|---|---|---|---|---|
| holistic g149 | 0.46 | 0.22 | 0.35 | +0.56 | 7 of 24 | 16 of 24 |
| holistic g140 | 0.46 | 0.24 | 0.32 | +0.54 | 5 of 24 | 13 of 24 |
| holistic g120 | 0.38 | 0.19 | 0.32 | +0.44 | 5 of 24 | 17 of 24 |
| holistic g90 | 0.44 | 0.26 | 0.36 | +0.53 | 7 of 24 | 14 of 24 |
| wheeled g149 | 0.71 | 0.74 | 0.26 | +0.82 | 21 of 24 | 2 of 24 |

Pooled over all 44 unseen draws it saw (12 + 8 + 24), the final holistic best's time at target is **0.20**; the wheeled best's over 36 draws is 0.73. The holistic number is bimodal: on two draws in three the body never reaches the target, on the rest it arrives and stays. The holistic best has sat on this plateau since generation 90 (0.19 to 0.26 by the 24-draw set); the fresh score did not move in the last 60 generations.

## 2. Heritability (parent-offspring correlation of fitness, `rabbitstew heritability`)

| window | holistic (standard tool) | wheeled (standard tool) | holistic (newborn-only) | wheeled (newborn-only) |
|---|---|---|---|---|
| gens 1-150 | 0.161 (n=88,893) | 0.377 (n=88,953) | 0.098 (n=44,700) | 0.388 (n=44,700) |
| gens 1-50 | 0.089 (n=29,493) | 0.332 (n=29,553) | 0.080 (n=15,000) | 0.332 (n=15,000) |
| gens 51-100 | 0.311 (n=30,000) | 0.478 (n=30,000) | 0.110 (n=15,000) | 0.464 (n=15,000) |
| gens 101-150 | 0.099 (n=29,400) | 0.209 (n=29,400) | 0.096 (n=14,700) | 0.229 (n=14,700) |

Under `--survival` a surviving parent is re-logged every generation under a new name, with its running-mean fitness and its original parents, so the standard tool counts each survivor once per generation it survives and its fitness is a mean over several draws. The newborn-only column (`herit_newborn.py`) pairs each child once, on its first evaluation, with its parents' running mean at the time it was bred. The two agree except in the middle window, where the standard tool's 0.31 for the holistic population is survivors, not inheritance.

**The holistic solo-score heritability is 0.08 to 0.11 in every window.** Paper 3 §4b reports 0.35 to 0.41 for a solo dense score at population 20 (condition C's locomotion phase and the capacity runs). This run does not reproduce that: with population 300, lexicase selection over the score vector and running-mean survival fitness, the holistic child's first score is predicted by its parents' at r ≈ 0.1, in the range paper 3 called noise. The wheeled population's 0.23 to 0.46 is in line with, and above, the earlier solo runs. Which of the new mechanisms lowered it (lexicase selects on the vector, so a scalar parent-child correlation understates what selection sees; the heading curriculum changes the task every generation for the first 100) is not separable from one run.

## 3. Founders at generation 149 (`founders.py`, all 600 evaluated members, 300 survivors + 300 children)

| population | founders | of |
|---|---|---|
| holistic | 3 | 600 |
| wheeled | 3 | 600 |

Both populations of 300 descend from three of their 300 generation-0 founders. The `--founder-model` null printed by the tool (about 102 founders at generation 100 under pure-noise fitness) models tournament selection with two elites and does not model survival selection or lexicase, so it is not the right null for this run and the comparison says nothing about drift versus selection. Collapse to three founders at population 300 is, however, the same picture paper 3 §4b reports for population 20 (two to six founders). The final holistic best's ancestry chain runs h0-209 → h1-569 → h9-168 → … → h89-163 → h139-181 → h147-203 → h149-7, and every ancestor on the chain has two parts: the lineage that won never changed its body plan. Descriptor diversity at generation 149 is 1.21 (holistic) and 0.55 (wheeled) by `analyze`'s measure.

## 4. Capability of the finals (`rabbitstew analyze --every 10 --lesions final`)

| | holistic g149 (h149-7) | wheeled g149 (c149-22) |
|---|---|---|
| approach progress (m of 2) | +1.56 | +1.97 |
| approach final distance (m) | 0.44 | 0.03 |
| mean speed (m/s) | 0.13 | 0.21 |
| work per metre (J/m) | 99 | 3,224 |
| straightness | 0.81 | 0.61 |
| fell | yes | no |
| steering successes (bearings 90°, −90°, 180°) | 1 of 3 (180° only; final distances 1.99, 0.97, 0.46) | 3 of 3 (0.09, 0.01, 0.02) |
| terrain successes (6 seeds) | 3 of 6 | 4 of 6 |
| push (block displacement, m) | 0.03 | 0.55 |
| body | 2 parts, 1 hinge, 0.35 m across, 0.07 m tall | Pioneer, 5 parts |

The holistic final is a two-part lump with a single hinge that flops towards the target. It cannot turn to a target at 90° either side; it reaches one placed behind it. The wheeled best steers to all three bearings.

## 5. Situatedness and distribution (`situated.py`, 8 unseen draws, seeds 6000-6007; progress in m / time at target)

| holistic best | units (global/local, parts) | links same-part / cross-part / global | reflex arcs | effectors live / env-driven / osc / bias-only | intact | no env sensors | no oscillators | no global | no local |
|---|---|---|---|---|---|---|---|---|---|
| g50 | 15 (2/13, 2) | 11 / 10 / 8 | 6 | 1 / 1 / 0 / 0 | +0.35, 0.23 | +0.00, 0.00 | +0.35, 0.23 | +0.25, 0.01 | +0.00, 0.00 |
| g100 | 18 (4/14, 2) | 12 / 11 / 11 | 7 | 2 / 1 / 0 / 1 | +0.53, 0.28 | +0.31, 0.01 | +0.53, 0.28 | +0.45, 0.02 | +0.10, 0.00 |
| g149 (final) | 18 (3/15, 2) | 14 / 10 / 4 | 8 | 2 / 1 / 0 / 1 | +0.55, 0.20 | +0.16, 0.03 | +0.55, 0.20 | +0.55, 0.20 | +0.16, 0.03 |

The behaviour is closed-loop at every checkpoint: blank the environmental sensors and the time at target goes to zero. There are no oscillators in any best. The global brain mattered at generations 50 and 100 (silencing it took the time at target from 0.23 and 0.28 to 0.01 and 0.02) and is inert at 149, where its links to the rest fell from 11 to 4; paper 4's "the central brain is always inert" holds for the final and not for the two earlier bests of the same lineage.

**Cross-part links are no longer zero.** Every holistic best carries 10 or 11 links between the two parts' local brains, which the encoding could not express before `--neighbour-links`. Whether they matter (`crosspart.py`, same 8 draws; "local brain" is a part's sensors and neurons, effectors keep their bias, as in `situated.py`):

| holistic best | intact | cross-part links cut only | part 0 local brain silenced | part 1 local brain silenced | all local brains silenced |
|---|---|---|---|---|---|
| g50 | +0.35, 0.23 | +0.23, 0.00 | +0.25, 0.01 | +0.30, 0.19 | +0.00, 0.00 |
| g100 | +0.53, 0.28 | +0.20, 0.00 | +0.25, 0.00 | +0.09, 0.00 | +0.10, 0.00 |
| g149 | +0.55, 0.20 | +0.35, 0.02 | +0.30, 0.04 | +0.43, 0.10 | +0.16, 0.03 |

Cutting only the ten cross-part links of the final best takes its time at target from 0.20 to 0.02, the same loss as blanking every sensor. The links are on the working path. The ticket's test for a link that matters, that silencing all local brains costs more than the sum of the single-part costs, is not met: the whole-lesion cost is 0.17 of time at target and the two single-part costs sum to 0.26 (0.16 + 0.10). The parts' contributions overlap rather than combine.

What the wiring is, from the final best's 28 links: the only driven joint effector (unit 13, the hinge torque in part 1) receives the target direction's vertical component in part 1's own frame (unit 11, weight +3.1; the `opponent` sensors point at the target under the solo proxy), plus the root part's target y and z in the root's frame through two neighbour links (+1.35, −2.79), plus a root-part unit (6) that is an effector of the jointless root and so acts as a neuron, itself driven by the root's target z (+2.45). The per-unit lesion map from `analyze` says the same: unit 13 accounts for the whole approach progress (loss 1.56 of 1.56), unit 11 for most of it (0.83), the root's target sensors for 0.12 each. This is A-301's trick (paper 4: a bearing turned into a signal by the part's own frame as the body rolls), now read from two frames at once through a neighbour link.

## 6. Controller descriptors of the final bests (`controller_descriptors`)

| | holistic g149 | wheeled g149 |
|---|---|---|
| units | 18 | 26 |
| global neurons | 3 | 7 |
| live effectors / driven / env-driven / oscillator-driven | 2 / 1 / 1 / 0 | 2 / 2 / 2 / 0 |
| cyclic units | 1 | 6 |
| centralisation (share of links touching the global brain) | 0.14 | 0.98 |
| sensor sources | target ×3, opponent ×5 | contact 1, target 3, opponent 3, up 3, velocity 3, target_distance 1, opponent_distance 1, joint_velocity 2 |

The holistic best has **no joint-angle or joint-velocity sensor at all**, in any checkpoint (g50, g100, g149 all read only target and opponent direction), so proprioceptive influence is zero by absence. The wheeled best carries two joint-velocity sensors, one per driven wheel, and `analyze`'s single-unit lesion of each *raises* approach progress by 0.04 and 0.05 m: they are wired in and do nothing useful. Paper 4's "joint angle and velocity are in the vocabulary and their measured influence is zero in every best" still holds.

## Answer

The Sims budget did not buy what population 20 could not. **Steering:** the final holistic best's fresh time at target is 0.20 pooled over 44 unseen draws (0.16, 0.20 and 0.22 on the three draw sets), on the ticket's threshold and not over it, and it has not moved since generation 90; it steers to a target behind it and to neither side (1 of 3 steering bearings). That is the capacity runs' 0.2 to 0.3 at generation 100 (paper 4, population 20, no survival, no lexicase, no neighbour links) at fifteen times the evaluations per generation, and below A-301's champion (0.54 in the ticket, 0.46 on paper 4's eight draws). **Proprioception:** none; the winning lineage never carried a joint sensor, and the wheeled best's two joint-velocity sensors hurt slightly when present. **Coordination between parts:** the neighbour links are used, for the first time in this series (ten cross-part links in every holistic best, and cutting them kills steering: 0.20 → 0.02), but what they carry is the same target-direction reflex read in a second frame, feeding one hinge, and the lesion sums show overlap, not synergy. The evolved controller is one reflex arc with a helper, on a two-part body that was two parts at generation 0. Two findings contradict the docs plainly: the holistic solo-score heritability here is 0.08 to 0.11, not paper 3's 0.35 to 0.41, so the dense solo score at this population and selection scheme was mostly noise to the search after all; and the global brain was not inert at generations 50 and 100 of this lineage, only at 149. Founders collapsed to 3 of 300 in both populations, as at population 20, and the tool's noise null does not cover this reproduction scheme, so drift and selection cannot be told apart from the founder count here.

## Files

`runs/RBT-11/sims-901/`: `config.json`, `history.json`, `lineage.jsonl.gz`, `state.json`, `holistic/best_gen*.json`, `conventional/best_gen*.json`, `fresh_eval.json`, `analysis.json`, `descriptors.json`. `runs/RBT-11/`: `sims-901.log` (run log), `fresh_eval.log`, `heritability_founders.log`, `analyze.log`, `situated.log` + `situated.json`, `crosspart.log` + `crosspart.json`, `fresh24.log` + `fresh24.json`, `descriptors.log`, and the scripts `founders.py`, `descriptors.py`, `herit_newborn.py`, `situated.py` (copy of `scripts/situated.py` with CASES edited), `crosspart.py`, `fresh24.py`.
