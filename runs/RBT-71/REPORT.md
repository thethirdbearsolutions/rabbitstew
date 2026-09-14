# RBT-71 Deliverable A: the strand-2 result on three fresh seeds

The foraging economy's headline claims, reproduced on seeds **804, 805 and 806**, each with its own paired
neutral control. Every expectation and the verdict rule were posted on RBT-71 before the first run was
launched (comment of 02:43 UTC, 2026-09-14). Nothing was tuned; one flag changed per run, the seed.

**Verdict: reproduces, on all three pre-registered clauses, on all three seeds. And the load-bearing
effect is smaller on every fresh seed than on 801, shrinking monotonically across 804, 805, 806 to
near parity by the end of 806.** Both halves of that sentence are the result.

## Scorecard against the pre-registration

| clause | rule | 804 | 805 | 806 | result |
|---|---|---|---|---|---|
| **R1** crossover | holistic leads on mean gain in > ½ of seasons 100–599, on ≥ 2 of 3 seeds | **0.976** | **0.832** | **0.702** | **met, 3 of 3** |
| **R2** heritability | holistic lifetime-yield heritability ≥ 0.20, n ≥ 30, on ≥ 2 of 3 seeds | **0.399** (n=634) | **0.382** (n=628) | **0.337** (n=657) | **met, 3 of 3** |
| **R3** selection, not drift | holistic founders in the final ancestry < paired neutral control's, 3 of 3 seeds | **1 vs 12** | **1 vs 12** | **3 vs 6** | **met, 3 of 3** |
| extinction | none on either side, any seed | none | none | none | met |

The coordinator's originally suggested R2 clause (holistic heritability exceeds the paired neutral
control's), withdrawn before the runs but reported per seed as promised: 0.399 vs 0.070, 0.382 vs
−0.063, 0.337 vs −0.129. It would also have been met 3 of 3. The reason it was withdrawn stands (§3 R2).

## 1. The runs

Six runs of the `forage-801` baseline, RBT-60's command, 600 seasons each, `--workers 4`:

```
rabbitstew ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 --workers 4 \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --max-age 60 --duration 15 --mass-budget 15.34 --conventional-topology --terrain random \
  --random-start --score food --seed SEED [--neutral] --out runs/RBT-71/{forage,neutral}-SEED
```

`launch.sh SEED [neutral]` is that command; `measure.py` computes every number below from
`history.json` and `lineage.jsonl` using the toolkit's own `realised_heritability`, `founder_survival`
and RBT-59's depth logic; `readout-{804,805,806,all}.txt` are its printed outputs and `readout-cli.txt`
is the coordinator's exact `rabbitstew heritability RUN --drift-baseline NEUTRAL` command on each seed,
which agrees to the fourth decimal. The bulk (`history.json`, `lineage.jsonl`, saved bests) stays out
of git per `runs/README.md`.

The neutral control is `--neutral` on the same world and seed: `starvation` off, birth threshold and
cost 0, living cost 0, everything else identical (`neutral-SEED/config.json`), which is the drift
control `docs/foraging-world.md` describes and RBT-82 asked this ticket to confirm.

**Code version, all six runs: integration head `f3aa69d`.** PR #12 (RBT-27/30) merged into the
integration branch at 04:29 UTC while forage-804, neutral-804 and forage-805 were running. It changes
the economy (an exploded body forfeits its season). The package is installed editable, so this was
checked rather than assumed: those three processes and their forked workers had loaded the tree at
`f3aa69d` before it moved and are unaffected; the remaining three runs were pinned to a worktree at
`f3aa69d` through `PYTHONPATH`. Each run has a `.code.txt` beside it saying which. So all six ran the
economy that 801, 802 and 803 ran, with the forfeit rule excluded by construction. A re-run on the
current head is a different arm and is not this one.

**Search depth, stated before the run and measured after.** `max_age` 60 over 600 seasons predicts a
median first-parent chain of 2 × 599 / 60 = **20** at season 599 (RBT-59/60). Measured, over all twelve
population-rows (two fauna × selected and neutral × three seeds): medians **18 to 22**, ratios to the
law 0.88 to 1.10. Evaluation count per individual: up to 60 seasons. **This is twenty generations of
selection, not six hundred**, and no sentence below implies otherwise.

## 2. Per seed, never pooled

| measurement | 804 | 805 | 806 |
|---|---|---|---|
| holistic deaths at season 11 | 41 | 33 | 40 |
| holistic minimum (season) | 26 (11) | **8 (16)** | 28 (11) |
| holistic back at 60 by season | 16 | 26 | 16 |
| wheeled minimum | 60 | 60 | 60 |
| sustained crossover (20-season hold) | 17 | 27 | 22 |
| holistic leads, seasons 100–599 | **0.976** | **0.832** | **0.702** |
| holistic leads, all 600 seasons | 571 | 484 | 411 |
| mean lead, seasons 100–599 (energy/season) | **+0.212** | **+0.109** | **+0.045** |
| gain hol / wheel at 100 | +1.22 / +0.81 | +1.06 / +0.75 | +0.91 / +0.90 |
| gain hol / wheel at 300 | +1.12 / +0.90 | +1.02 / +1.00 | +1.00 / +0.92 |
| gain hol / wheel at 500 | +0.99 / +0.90 | +1.03 / +0.86 | +0.95 / +0.91 |
| gain hol / wheel at 599 | +1.11 / +0.98 | +1.18 / +1.10 | **+0.94 / +1.02** |
| yield heritability holistic, selected (evals ≥ 5) | +0.399 (n=634) | +0.382 (n=628) | +0.337 (n=657) |
| yield heritability wheeled, selected | +0.229 (n=713) | +0.276 (n=684) | +0.252 (n=711) |
| yield heritability holistic, **neutral** | +0.070 (n=595) | −0.063 (n=596) | −0.129 (n=592) |
| yield heritability wheeled, **neutral** | +0.237 (n=593) | +0.338 (n=594) | +0.351 (n=594) |
| founders holistic, selected / neutral | 1 / 12 | 1 / 12 | 3 / 6 |
| founders wheeled, selected / neutral | 12 / 14 | 10 / 15 | 7 / 8 |
| depth at 599 holistic, selected (min–max) | 22 (18–26) | 20 (17–27) | 22 (19–24) |
| depth at 599 wheeled, selected | 19 (15–24) | 18 (14–23) | 21 (17–26) |
| depth at 599 holistic / wheeled, neutral | 21 / 18 | 19 / 21 | 21 / 19 |
| neutral mean gain hol / wheel at 599 | +0.01 / +0.45 | +0.01 / +0.39 | +0.03 / +0.42 |

For comparison, the record this reproduces (`docs/foraging-world.md`, RBT-10), same command, seeds
801 / 802 / 803 at work cost 0.03: holistic minimum 7 / 31 / 42; sustained crossover 83 / 18 / 11;
holistic gain at 599 +1.41 / +1.04 / +0.97 against wheeled +0.95 / +0.86 / +0.93; founders 1 / 3 / 3
holistic and 7 / 15 / 12 wheeled; holistic yield heritability 0.51 / 0.32 / 0.28; the lead held in
450 to 566 of 600 seasons on 802/803. Here it is 571, 484 and 411 of 600.

## 3. What each clause says

### R1: the crossover reproduces in sign on every seed, and its size is the seed

The holistic side overtakes the designed one early (season 17 to 27, against 801's 83) and leads on mean
gain for more than half of seasons 100–599 on all three seeds. That is the pre-registered clause and it
is met with room on 804 and 805.

It is not met with room on 806. There the lead is 0.702 of seasons at a mean margin of **+0.045 energy
a season**, the two sides trade the lead through the middle of the run, and at season 599 the **wheeled
side is ahead**, +1.02 to +0.94. Across the three fresh seeds the effect falls monotonically:
0.976 → 0.832 → 0.702 of seasons, +0.21 → +0.11 → +0.045 a season. Put beside 801–803 the picture over six
seeds is: the holistic side ends ahead on four (801, 802, 804, 805), at parity on one (803), and behind on
one (806); it leads the majority of seasons on all six.

So the defensible sentence for paper 5 is **"the co-evolved bodies out-forage the designed one for most
of the run on every seed tried, by a margin that ranges from a fifth of an energy unit a season to
nothing"**, and not the ticket's "for 450–566 of 600 seasons", which was the two most favourable
replicates. The peak numbers quoted in the ticket (801's +1.63 at season 500, 5.75 items on 4.2 kJ) did
not recur on any fresh seed and are 801's. What did recur, every seed, is that a population of random
lumps that starts at a mean gain of about zero is earning +0.9 to +1.2 a season within a hundred
seasons and holds it, while the designed body, which starts near +0.5 and is never in danger, arrives
at +0.9 to +1.1.

### R2: lifetime yield is heritable on both sides, and the control says why that matters

Holistic yield heritability is 0.34 to 0.40 on the three seeds at n = 628 to 657, wheeled 0.23 to
0.28 at n = 684 to 713, all against the 0.20 floor and all far from the arena's zero. That is the
paper's sentence, and it holds.

The neutral controls are the informative miss. I predicted them at 0.40–0.65 from the 0.52 / 0.60 the
docs quote for 801's control; they read **+0.07, −0.06, −0.13** on the holistic side and 0.24 to 0.35 on
the wheeled side. The holistic drift population never learns to eat: its mean gain is +0.01 to +0.03
at season 599, the same as at season 0, so its lifetime yields are seasons' draws and carry nothing
between generations. The wheeled drift population arrives able to eat (+0.4 a season on random
weights) and its yield is as heritable under drift as under selection, which is what a heritable trait
does when nothing is selecting on it. Both are the physically sensible numbers. RBT-82 has since shown
the same on a fresh short control (0.15, interval including zero) and marked the docs' 0.52 / 0.60
unverified; the three controls here are the measured figures, at the full 600-season configuration.

What this does to the clause: the pre-registration argued that "exceeds the neutral control" was the
wrong test because drift populations inherit yield too, and the wheeled side shows exactly that
(0.34 and 0.35 under drift against 0.28 and 0.25 under selection on 805 and 806). The holistic side
happens to pass it because its drift control cannot eat. Report both, as promised; rest the claim on
the floor against zero, as registered.

### R3: one founder against twelve, twice; three against six, once

On 804 and 805 the whole holistic fauna at season 599 descends from **one** founder of sixty while the
paired control keeps twelve. That is the season-11 wave: 33 to 41 founders that never ate starve together
on their three units of energy, exactly as the arithmetic says, and the survivors' descendants take
the slots. Selection through starvation, not drift, thinned the ancestry, and the paired control is
what makes that a claim rather than a comparison with a borrowed number.

On 806 the margin is **3 against 6**. Three holistic founders survive, as on 802 and 803; but the 806
control kept only six of sixty, half what the other two controls and 801's kept. Six hundred seasons of
drift at capacity 60 evidently has that much variance in founder retention on its own, and a
one-seed comparison at 3 vs 6 is not the same evidence as 1 vs 12. The clause is met on 806, and it is
met on the margin; if R3 is to be load-bearing anywhere, it rests on 804 and 805, with 806 consistent.

### The demographics

The starvation wave landed at season 11 on every seed with 33 to 41 holistic deaths, as pre-registered
(founders on 3 energy at 0.25 a season). Its depth is the seed: minimum 26 and 28 on 804 and 806, back
at capacity by 16; **8 on 805**, reached at season 16 after five more seasons of decline, back at 60 by
26. Over the six seeds now run the minimum is 7, 8, 26, 28, 31, 42: 801 was the deepest, not the type,
and 805 is the second. The wheeled side never dipped below 60 on any seed. No extinction anywhere.

## 4. Predictions scored

| prediction (per seed) | 804 | 805 | 806 | verdict |
|---|---|---|---|---|
| R1 fraction 0.70–0.95, point 0.85 | 0.976 | 0.832 | 0.702 | 804 above the band, 806 at its floor; point 0.85 was about the middle seed |
| sustained crossover 10–90 | 17 | 27 | 22 | met |
| holistic gain at 599 +0.95 to +1.45 | +1.11 | +1.18 | **+0.94** | 806 a hundredth under |
| wheeled gain at 599 +0.85 to +1.05 | +0.98 | **+1.10** | +1.02 | 805 over |
| holistic heritability 0.25–0.50, point 0.33 | 0.399 | 0.382 | 0.337 | met, point good |
| wheeled heritability 0.10–0.40 | 0.229 | 0.276 | 0.252 | met |
| neutral heritability 0.40–0.65, not below selected | 0.070 / 0.237 | −0.063 / 0.338 | −0.129 / 0.351 | **wrong**, §3 R2 |
| holistic founders 1–5, neutral 10–18 | 1 / 12 | 1 / 12 | 3 / **6** | 806's control under |
| wheeled founders 5–17, neutral 12–20 | 12 / 14 | 10 / 15 | 7 / **8** | 806's control under |
| holistic deaths at season 11: 30–40 | **41** | 33 | 40 | 804 one over |
| holistic minimum 7–45, back by 15–35 | 26 / 16 | 8 / 26 | 28 / 16 | met |
| depth 18–24, all four populations | 22, 19, 21, 18 | 20, 18, 19, 21 | 22, 21, 21, 19 | met, 12 of 12 |
| "reproduces" at confidence 0.6 | | | | it did |

## 5. Exposures, stated

- **RBT-44 is open.** Its specific defect (a `--survival` GA re-logging a survivor under a new name
  every generation, so one individual is counted once per generation it survives) does not apply
  here: `read_lineage` keeps one record per name and correlates lifetime means. What does remain is
  that the parent's yield used is its **final** lifetime mean, not its mean at the moment of
  breeding, and parent and child overlap in the seasons they are alive, so shared season-to-season
  world variance can inflate the correlation. The paired neutral control carries the same overlap
  and is the check on the size of that inflation; the number should be read as an upper bound on
  additive heritability. RBT-82 has since measured the shared-season share of yield variance in this
  re-seeded world at 0.05–0.08, at which its synthetic sweep shows no inflation, and the holistic
  controls here read near zero with the same overlap; whatever the inflation is, the 0.34–0.40 is
  not made of it.
- **Bout-score heritability on these populations** (the ticket's Deliverable A item 2) was not in the
  coordinator's fixed scope and was not run. The contrast with the arena's zero remains a contrast
  across two literatures, not within one run.
- **No champion was labbed.** No claim is made here about what any individual best is; the claims are
  about population means, ancestry and heritability. "Locomotion from survival" is read off the
  holistic mean gain going from about zero to about +1 a season under starvation, on every seed, while
  the paired control's holistic mean stays at zero for 600 seasons, and not off any body's gait.
  Whether the 806 lumps are cheaper than the 806 Pioneers per item, the ticket's "on a fifth of the
  energy", was not measured here and should not be quoted from this package.
- **Frame → calibrate → manipulation → measure.** The instruments are the toolkit's own `heritability`,
  `founder_survival` and RBT-59's depth logic, already round-tripped on 801–803 and RBT-59/60; nothing
  new was introduced and nothing was re-calibrated here. Stated, not unstated.
- **Three seeds is three seeds.** Six with 801–803, all at one density, one economy, one lifespan.
  Nothing here is a distribution, and the monotone shrinkage across 804–806 is an observation about
  three numbers, not a trend.

## 6. Process notes

- Launched as harness background tasks, not `nohup` (RBT-60's death at season 107). All six ran to
  "results in". Two harness tasks (neutral-804, forage-805) reported exit code 2 *after* their run
  completed: bash re-read `launch.sh` at its old offset after I rewrote the file to add the code pin.
  The runs' outputs are intact; recorded so nobody reads exit 2 as a death. Do not edit a running script.
- Two runs at a time on four cores at about 5.5 seasons a minute each; a pair took about 110 minutes;
  the six took from 02:43 to 08:21 UTC.
- Interim reads of 804 and 805 were posted on the ticket as each landed, labelled interim; the
  verdict rule was not touched after them.
- The first four RBT-71 commits went onto the integration branch directly; the coordinator asked for a
  results branch and everything from `c62d9ef` on is on `results/RBT-71`, PR'd with this report.

## Files

`launch.sh`, `measure.py`, `measure.json`, `readout-804.txt`, `readout-805.txt`, `readout-806.txt`,
`readout-all.txt`, `readout-cli.txt`, `{forage,neutral}-{804,805,806}/config.json`, `*.code.txt`.
Bulk output on the machine that ran it, regenerable from the command above (the simulator is
deterministic; RBT-60 confirmed 11,218 lineage records identical across two launches).
