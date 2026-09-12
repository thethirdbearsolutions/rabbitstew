# RBT-9: Condition A foothold rate, seeds 305–308

Four more seeds of the redesigned task (condition A of paper 3: random start bearing, time-at-target score, random terrain resampled each generation, rich brain, equal mass budget 15.34, from rest, one opponent × one draw, population 20, 200 generations, round-robin champion bouts every 5 generations). Nothing was changed from the ticket's command line except `--workers 1` (four runs shared a 4-core box, one core each). Code at commit e09ff7b (`claude/new-session-4cao7d`); all 113 tests passing before the runs.

All numbers below are fresh-draw: the generation's best evaluated alone on 12 start-and-terrain draws (seeds 5000–5011) the run never trained on (`scripts/eval_fresh.py RUN 20 12`, `tat` field). "Steerer" = holistic fresh-draw time at target ≥ 0.2 at any checkpoint.

## Per-seed table

| Seed | Holistic fresh tat g40 / g100 / g199 | Max holistic fresh tat (gen) | Wheeled fresh tat g199 | Heritability h / c | Founders at g199 h / c (of 20) | Final champion bouts (holistic mean fitness, holistic–wheeled wins of 50) |
|---|---|---|---|---|---|---|
| 305 | 0.00 / 0.00 / 0.00 | 0.00 (all checkpoints) | 0.53 | 0.018 / 0.086 | 8 / 6 | 0.110, 0–49 |
| 306 | 0.00 / 0.00 / 0.00 | 0.02 (g80) | 0.29 | 0.023 / 0.105 | 1 / 7 | 0.112, 4–44 |
| 307 | 0.00 / 0.00 / 0.00 | 0.00 (all checkpoints) | 0.08 | 0.039 / 0.083 | 5 / 4 | 0.047, 1–49 |
| 308 | 0.00 / 0.00 / 0.00 | 0.02 (g0) | 0.02 | 0.021 / 0.054 | 5 / 2 | 0.150, 3–47 |

Heritability is the realised parent–child fitness correlation over all 3980 children per population (`rabbitstew heritability`). Wins that do not sum to 50 are drawn bouts.

Full fresh-draw curves (checkpoints every 20 generations plus 199):

| Seed | Population | g0 | g20 | g40 | g60 | g80 | g100 | g120 | g140 | g160 | g180 | g199 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 305 | holistic | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 305 | wheeled | 0.00 | 0.34 | 0.56 | 0.27 | 0.57 | 0.00 | 0.58 | 0.61 | 0.60 | 0.35 | 0.53 |
| 306 | holistic | 0.00 | 0.00 | 0.00 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 306 | wheeled | 0.06 | 0.41 | 0.19 | 0.55 | 0.09 | 0.21 | 0.29 | 0.52 | 0.58 | 0.33 | 0.29 |
| 307 | holistic | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 307 | wheeled | 0.12 | 0.08 | 0.00 | 0.59 | 0.00 | 0.58 | 0.59 | 0.55 | 0.28 | 0.57 | 0.08 |
| 308 | holistic | 0.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 308 | wheeled | 0.00 | 0.00 | 0.53 | 0.55 | 0.02 | 0.32 | 0.53 | 0.60 | 0.45 | 0.47 | 0.02 |

## Foothold rate

None of the four new seeds produced a steerer. The holistic best's fresh-draw time at target never exceeded 0.02 at any checkpoint in any of them, against a steerer threshold of 0.2. Combined with the paper's four (301 yes; 302, 303, 304 no), condition A stands at **1 steerer in 8 seeds** (12.5%). The ticket description's "1 in 3" and the comment's "1 in 4" both become 1 in 8. This does not contradict paper 3 §4a's qualitative claim (a foothold is a lucky-lineage event under a fitness signal that is mostly noise); it does lower the rate at which that luck occurs, and the paper's line "Condition A closes at one steerer in four seeds" should be read as one in eight.

The wheeled side behaved as in the paper's seeds: every Pioneer became a competent goal-holder at some point (peaks 0.58–0.61 fresh-draw tat in all four seeds), and in three of four it had partly or wholly lost it by generation 199 (0.29, 0.08, 0.02; only 305 held 0.53 at the end), the same trading-away of steering for straight-line drive that 301's Pioneer showed. The wheeled side won the final champion bouts in every seed (44–49 of 50).

Heritability is at the bottom of the paper's condition A range on the holistic side (0.02–0.04, versus 0.03–0.12 in §4b) and inside it on the wheeled side (0.05–0.11). Founder counts at generation 199 are 5, 5, 8 and 1 holistic and 6, 7, 4, 2 wheeled. Two of these sit outside the paper's "two to six" range: 305's holistic population still descends from 8 founders, and 306's has coalesced to a single founder. 306's collapse to one founder is not a found hill: its heritability is 0.02 and its fresh-draw competence is zero throughout, so it is drift that happened to run to fixation within 200 generations.

## Do the steerers look like A-301's?

There are no new steerers to compare, so step 5 of the ticket (`rabbitstew analyze` on the steerer's run) was not run. A-301's competence, per paper 4, is a single reflex arc from the target-direction sensor's vertical component in one part's own frame to a torque effector in that same part. Nothing in seeds 305–308 reached the fresh-draw level at which that question can be asked: the highest holistic checkpoint across the four runs is 0.02, which is the level 302, 303 and 304 sat at. On the evidence of eight seeds, the single-arc steerer of 301 is so far unique, and whether it is the typical form a condition A foothold takes, or a one-off, cannot be settled at this foothold rate without many more seeds.

## Files

`runs/RBT-9/A-{305,306,307,308}/`: config.json, history.json, lineage.jsonl, holistic/ and conventional/ (best_gen*.json and champion checkpoints), fresh_eval.json. `A-*.log` are the evolve logs (the runs were interrupted twice by the box and resumed with `--resume`, which is visible in the logs as repeated generation numbers around 20 and 30–38; the resumed state is the checkpoint, so no generation was evaluated twice); `A-*.fresh.log` are the eval_fresh outputs. No analysis.json (no steerer). `state.json` resume checkpoints are omitted.

Run notes: about 1 h 45 min wall for all four seeds together at one worker each on 4 cores, i.e. roughly 14–22 s per generation per run, rising to 45–70 s in the last generations.
