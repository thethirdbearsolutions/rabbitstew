# RBT-20 — W3': long seasons at baseline density (60 s seasons, 12 items, basal 1.0), seed 801

**Outcome: both populations extinct before season 10. Wheeled 60 → 0 at season 8, holistic 60 → 0 at season 9. No breeding population formed, so the arm's target number, yield heritability, cannot be measured (no child reached five evaluations). Sensing was never on the table.**

Run: `runs/RBT-20/W3b-801`, flags exactly as the issue except `--workers 3` (four cores minus one; workers only size the process pool, the RNG is untouched). Tests: 113 passed before launch. The run ended on its own at season 9 ("everyone died"), 10 seasons, 2.5 minutes of wall time.

Branch note: results are on `claude/rbt-20-mtqdsp`, the branch this session was assigned, rather than `results/RBT-20`; the contents are what the issue asked for.

## 1. Season table (every season; there are only ten)

| season | holistic alive | births | deaths | mean lifetime gain | best | wheeled alive | births | deaths | mean lifetime gain | best |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 57 | 2 | 5 | +0.02 | 1.97 | 40 | 8 | **28** | −0.04 | 3.83 |
| 1 | 55 | 1 | 3 | +0.08 | 1.86 | 36 | 11 | 15 | +1.08 | 10.80 |
| 2 | 7 | 0 | **48** | +0.77 | 1.53 | 26 | 8 | 18 | +1.26 | 5.29 |
| 3 | 3 | 0 | 4 | +0.84 | 1.11 | 18 | 4 | 12 | +1.30 | 3.25 |
| 4 | 3 | 0 | 0 | +0.84 | 1.26 | 11 | 1 | 8 | +1.04 | 2.94 |
| 5 | 2 | 0 | 1 | +0.78 | 1.03 | 4 | 1 | 8 | +0.97 | 1.62 |
| 6 | 1 | 0 | 1 | +0.86 | 0.86 | 2 | 0 | 2 | +1.04 | 1.12 |
| 7 | 1 | 0 | 0 | +0.99 | 0.99 | 1 | 0 | 1 | +0.89 | 0.89 |
| 8 | 1 | 0 | 0 | +0.97 | 0.97 | 0 | 0 | 1 | extinct | |
| 9 | 0 | 0 | 1 | extinct | | | | | | |

- **Bottleneck.** Holistic: 48 of 55 starved together at season 2, exactly when 3 energy at basal 1.0 runs out for a founder that never eats (3 → 2 → 1 → 0), the season pre-registered in the issue. Minimum 3 alive at seasons 3–4. Wheeled: 28 of 60 dead at season 0, then 36, 26, 18, 11, 4, 2, 1, 0: a steady drain, not a bottleneck.
- **Recovery.** None on either side. The holistic survivors' lifetime mean gain was +0.78 to +0.99 a season against a basal cost of 1.0, so each of them was slowly starving; the last, founder h0-7, ate 2, 2, 1, 0, 2, 0, 0, 2, 1 items over its nine seasons (gains +1.86 / +0.86 / −0.14, constant 4.7 kJ of work) and died with 0.77 energy left short of the 1.0 basal.
- **First season holistic mean gain exceeds wheeled.** Season 0 (+0.02 against −0.04, because 28 bankrupt Pioneers dragged the wheeled mean down); from season 1 the wheeled mean was higher until it had no members.
- **Extinctions.** Wheeled at season 8, holistic at season 9.
- **Births.** Holistic 3 in total (seasons 0 and 1); wheeled 33 (8, 11, 8, 4, 1, 1 at seasons 0–5). A child is born with 1 energy and pays 1.0 basal at the end of its first season, so it must net a positive food-minus-work in its first 60 s or die; under the baseline it had a grace of four seasons at zero intake. 2 of 3 holistic children survived a first season and none a second; 12 of 33 wheeled children survived a first season, 8 a second, and no child of either kind reached a fifth evaluation. Every last survivor was a founder.

## 2. Founders at the last season with survivors

| | last season with survivors | founders / alive |
|---|---|---|
| holistic | 8 | 1 of 1 (h0-7, itself a founder) |
| wheeled | 7 | 1 of 1 (c0-44, itself a founder) |

Not a founder count in the baseline's sense (one lineage that took over sixty slots): the population simply ran down to its last founder.

## 3. Yield heritability

| | rule | n (children) | Pearson r |
|---|---|---|---|
| holistic | child and parents with evals ≥ 5 | 0 | undefined |
| wheeled | child and parents with evals ≥ 5 | 0 | undefined |
| holistic | no evals filter (`analysis.realised_heritability`) | 3 | undefined (n < 10) |
| wheeled | no evals filter | 33 | 0.18 |

Baseline: 0.51 holistic, 0.24–0.39 wheeled. The 0.18 is 33 wheeled children scored on one to four seasons each against parents scored on one to five; it is not comparable with the baseline's lifetime means and is reported only for completeness. **The number the arm was run for does not exist here.**

## 4. Probes (`scripts/forage_probe.py`, 8 seeds, the run's 60 s)

Bests are saved every ten seasons, so only season 0 exists (`probe.txt`).

| best | body | sensors | intact | noses blanked | all env sensors blanked | local brains silenced |
|---|---|---|---|---|---|---|
| holistic g0 (h0-49) | 4 parts, 29 units | oscillator, up | 0.00 items, 6.9 m path, 1.8 kJ | 0.00 | 0.00 | 0.25 |
| wheeled g0 (c0-55) | Pioneer, 24 units | contact, up, velocity, height, joint_velocity, food, agent | 2.38 items, 18.1 m path, 83.1 kJ, 2.4 m displacement | **0.62**, 5.7 m displacement | 0.62 | 0.62 |

- Holistic g0: eats nothing alone on fresh seeds in any condition; its 1.97 season-0 gain in the run was two items met in a shared arena. There is nothing to lesion; it is not a forager.
- Wheeled g0: **the noses matter. Blanking the food and agent sensors removes 74% of its food** (2.38 → 0.62) and more than doubles its displacement from spawn (2.4 → 5.7 m): like the baseline's season-500 Pioneer, the nose is a brake that keeps it in the disc, not a compass. Wiring (`controller_descriptors`): sensor_sources {food 3, agent 3, up 3, velocity 3, joint_velocity 2, contact 1, height 1}; env_driven_effectors 2 (both drive wheels). Food sensors sit on parts 0, 1 and 2: the chassis and the left and right drive wheels, the Pioneer's standard three noses. Its fate in the run: gains +3.83, +0.36, +3.69, −1.85, +0.08 over seasons 0–4, three children born at seasons 0–2, none of which survived its first season, and dead itself at season 5. The one nose that worked in this arm was bankrupt by its wheels inside five seasons, as in W6.

## 5. Why: a 60 s season is not four 15 s seasons

The issue's premise was that at 60 s and basal 1.0 "the economy per simulated second is the baseline's". It is on the cost side and not on the food side. Two measurements, both on the run's own genotypes (`quarters.py`, `founders_season0.py`; measurement, no flag of the arm changed).

**Within-season profile of the season-0 Pioneer best, alone, 8 seeds** (`quarters_gen0.txt`):

| quarter | items eaten | work | mean r from centre | seeds outside the 3 m disc |
|---|---|---|---|---|
| 0–15 s | 1.50 | 19.6 kJ | 3.3 m | 5/8 |
| 15–30 s | 0.62 | 20.8 kJ | 2.7 m | 3/8 |
| 30–45 s | 0.12 | 21.3 kJ | 2.4 m | 3/8 |
| 45–60 s | 0.12 | 21.4 kJ | 3.2 m | 5/8 |

Food falls to a twelfth of its first-quarter rate while work stays flat. The first 15 s (1.50 items, matching the calibration's 15 s Pioneer) harvest the standing crop around the spawn; after that the robot lives on the flux of regrowth into the strip it sweeps, or sits outside the disc (two seeds never re-entered and ate nothing). The three seeds that ate 3–4 items in the first quarter stayed inside the disc and still ate 2, 2, 1 then 0, 0, 1 after: local depletion, not leaving. Four 15 s seasons of this robot would yield about 6.0 items for 78 kJ; one 60 s season yields 2.38 for 83 kJ. Per simulated second the long season delivers 40% of the food at the same work cost.

**Season 0 replayed for the identical 120 founders, same terrain and start seeds, same groups, starvation off so the dead are counted**, at 60 s and at the baseline's 15 s (`founders_season0.txt`):

| | 60 s season: mean / median gain | starve in season 0 | can breed after season 0 | 15 s season: mean / median gain | starve | can breed | r(gain60, gain15) |
|---|---|---|---|---|---|---|---|
| holistic (56) | −0.03 / 0.00 | 1 | 2 | +0.04 / 0.00 | 0 | 3 | 0.85 |
| wheeled (58) | **−1.28 / −1.87** | **26** | 8 | +0.02 / −0.52 | 0 | 20 | 0.25 |

Net of basal, the wheeled founders' mean season is −2.28 at 60 s against −0.93 for four 15 s seasons. The same random Pioneers that all survive a 15 s season lose 26 of 58 in one 60 s season: their wheels turn for 60 s (≈ 2.5 energy of work) and eat for 15. A lump's gain is nearly the same at either length (r 0.85; the best eater took 1.97 at both, two items and no more), because it does not move and cannot reach a second crop; for it the arm is simply basal ×4 with food ×1, and the survivors' +0.8 a season is below the 1.0 they are charged.

## 6. Against the baseline

| | baseline forage-801 (15 s, basal 0.25) | W3' (60 s, basal 1.0) |
|---|---|---|
| holistic bottleneck | 60 → 7 at season 11, back to 60 by 32 | 60 → 3 at season 3, extinct at 9 |
| wheeled | never below 16, full from 32 | 60 → 40 at season 0, extinct at 8 |
| holistic mean gain 100 / 300 / 500 / 599 | +1.02 / +1.19 / +1.63 / +1.41 | — |
| wheeled mean gain | +0.96 / +1.03 / +0.94 / +0.95 | — |
| founders of the final population | 1 holistic, 7 wheeled | last survivors were single founders |
| yield heritability | 0.51 holistic, 0.24–0.39 wheeled | unmeasurable (no child with ≥ 5 evals) |
| a nose that mattered | Pioneer best at 500 (brake) | Pioneer best at 0 (brake, 74% of food), dead by season 5 |

## 7. Does a longer season give sensing a slope?

Heritability first: it could not be measured, because no child of either population lived five seasons, so this arm says nothing about whether per-season noise was the limit on sensing. What it measured instead is the bootstrap line again, from a new direction. The pre-registered reasoning treated the season as a unit of noise and scaled the basal cost with it, on the assumption that food per simulated second would follow; in this world it does not, because with instant regrowth at random positions most of a 15 s season's food is the standing crop near a fresh spawn, and a spawn reset four times a minute renews it four times where one long season renews it once. Halving the per-season noise therefore also cut the food supply per second by more than half while the work cost ran unchanged, and at basal 1.0 both random populations starved before breeding: the Pioneers bankrupt by their own wheels in the first season, as their identical founders never are at 15 s; the lumps at season 2 as pre-registered, with survivors netting +0.8 against a charge of 1.0 and a child given one season to prove itself. The one situated founder was again a Pioneer with a brake nose, and again it did not last. Season length cannot be varied on its own here by changing `--duration`; it is entangled with the spawn reset and the standing crop, and a long-season arm that keeps the food per second at the baseline's would have to match the food side too, which is a design question for the owner (it touches what the persistent world, RBT-19, is about), not a flag to tune in this arm. Lesson, the same as W2, W3 and W6: below the density-and-economy line where random founders breed, an arm measures the threshold and nothing else.

Suggested row for the fan-out table in `docs/foraging-world.md`:

| W3', RBT-20 | 60 s seasons at baseline density, basal 1.0 | wheeled extinct at 8, holistic at 9; a 60 s season harvests one standing crop where four 15 s seasons harvest four (best Pioneer 1.5, 0.6, 0.1, 0.1 items per quarter at 20 kJ each), so food per simulated second fell to about 40% while work did not; 26 of 58 Pioneer founders bankrupt in season 0, lumps starved together at season 2 as pre-registered, no child lived five seasons | a founder's nose (a brake, 74% of its food), dead by season 5 |

## Files

`W3b-801/` (config.json, history.json, lineage.jsonl, holistic/ and conventional/ best_gen0000.json; the final/ directories are empty because both populations were empty), `W3b-801.log`, `probe.txt`, `readout.py`, `quarters.py` and `quarters_gen0.txt`, `founders_season0.py` and `founders_season0.txt`, `wiring_conventional_gen0.txt`.
