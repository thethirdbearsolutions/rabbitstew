# RBT-71 Deliverable A: the strand-2 result on three fresh seeds

The foraging economy's headline claims, reproduced on seeds **804, 805 and 806**, each with its own paired
neutral control. Every expectation and the verdict rule were posted on RBT-71 before the first run was
launched (comment of 02:43 UTC, 2026-09-14). Nothing was tuned; one flag changed per run, the seed.

**Verdict: VERDICT_TBD**

## Scorecard against the pre-registration

| clause | rule | 804 | 805 | 806 | result |
|---|---|---|---|---|---|
| **R1** crossover | holistic leads on mean gain in > ½ of seasons 100–599, ≥ 2 of 3 seeds | **0.976** | **0.832** | R1_806 | R1_RESULT |
| **R2** heritability | holistic lifetime-yield heritability ≥ 0.20, n ≥ 30, ≥ 2 of 3 seeds | **0.399** (n=634) | **0.382** (n=628) | R2_806 | R2_RESULT |
| **R3** selection, not drift | holistic founders in the final ancestry < paired neutral control, 3 of 3 seeds | **1 vs 12** | **1 vs 12** | R3_806 | R3_RESULT |
| extinction | none on either side, any seed | none | none | EXT_806 | EXT_RESULT |

The coordinator's originally suggested R2 clause (holistic heritability exceeds the neutral control's),
withdrawn before the runs but reported per seed as promised: R2ALT_ROW.

## 1. The runs

Six runs of the `forage-801` baseline, RBT-60's command, 600 seasons each, `--workers 4`:

```
rabbitstew ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 --workers 4 \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --max-age 60 --duration 15 --mass-budget 15.34 --conventional-topology --terrain random \
  --random-start --score food --seed SEED [--neutral] --out runs/RBT-71/{forage,neutral}-SEED
```

`launch.sh SEED [neutral]` is that command; `measure.py` is every number below; `readout-SEED.txt`
are its printed outputs; `measure.json` the machine-readable form. The bulk (`history.json`,
`lineage.jsonl`, saved bests) stays out of git per `runs/README.md`.

**Code version, all six runs: integration head `f3aa69d`.** PR #12 (RBT-27/30) merged into the
integration branch at 04:29 UTC while forage-804, neutral-804 and forage-805 were running. It
changes the economy (an exploded body forfeits its season). The package is installed editable, so
this was checked rather than assumed: those three processes and their forked workers had loaded the
tree at `f3aa69d` before it moved and are unaffected; the remaining three runs were pinned to a
worktree at `f3aa69d` through `PYTHONPATH`. Each run has a `.code.txt` beside it saying which. So all
six ran the economy that 801, 802 and 803 ran, with the forfeit rule excluded by construction. A
re-run on the current head would be a different arm and is not this one.

**Search depth, stated before the run and measured after.** `max_age` 60 over 600 seasons predicts a
median first-parent chain of 2 × 599 / 60 = **20** at season 599 (RBT-59/60). Measured, every one of
the twelve population-rows: DEPTH_RANGE. Evaluation count per individual: up to 60 seasons. **This is
twenty generations of selection, not six hundred**, and no sentence below implies otherwise.

## 2. Per seed, never pooled

TABLE_TBD

For comparison, the record this reproduces (docs/foraging-world.md, RBT-10), same command, seeds 801–803
at work cost 0.03: holistic minimum 7 / 31 / 42 at season 11; sustained crossover 83 / 18 / 11; holistic
gain at 599 +1.41 / +1.04 / +0.97 against wheeled +0.95 / +0.86 / +0.93; founders 1 / 3 / 3 holistic,
7 / 15 / 12 wheeled; holistic yield heritability 0.51 / 0.32 / 0.28. RBT-10 tabulated the lead as
"450 to 566 of 600 seasons" on 802/803; here it is LEAD_SEASONS of 600 on 804/805/806.

## 3. What each clause says

### R1: the crossover R1_HEADLINE

R1_TEXT

### R2: lifetime yield is heritable, and the control says why that is not trivial

R2_TEXT

### R3: one founder, against twelve

R3_TEXT

### The demographics

DEMO_TEXT

## 4. Predictions scored

| prediction (per seed) | 804 | 805 | 806 | verdict |
|---|---|---|---|---|
| R1 fraction 0.70–0.95, point 0.85 | 0.976 | 0.832 | P1 | PV1 |
| sustained crossover 10–90 | 17 | 27 | P2 | PV2 |
| holistic gain at 599 +0.95 to +1.45 | +1.11 | +1.18 | P3 | PV3 |
| wheeled gain at 599 +0.85 to +1.05 | +0.98 | **+1.10** | P4 | PV4 |
| holistic heritability 0.25–0.50, point 0.33 | 0.399 | 0.382 | P5 | PV5 |
| wheeled heritability 0.10–0.40 | 0.229 | 0.276 | P6 | PV6 |
| neutral heritability 0.40–0.65, not below selected | **0.070** / 0.237 | **−0.063** / 0.338 | P7 | **wrong**, see §3 R2 |
| holistic founders 1–5, neutral 10–18 | 1 / 12 | 1 / 12 | P8 | PV8 |
| wheeled founders 5–17, neutral 12–20 | 12 / 14 | 10 / 15 | P9 | PV9 |
| holistic deaths at season 11: 30–40 | **41** | 33 | P10 | PV10 |
| holistic minimum 7–45, back at 60 by 15–35 | 26 / 16 | 8 / 26 | P11 | PV11 |
| depth 18–24, all four populations | 22, 19, 21, 18 | 20, 18, 19, 21 | P12 | PV12 |
| overall "reproduces" at 0.6 | | | | OVERALL_PV |

## 5. Exposures, stated

- **RBT-44 is open.** Its specific defect (a `--survival` GA re-logging a survivor under a new name
  every generation, so one individual is counted once per generation it survives) does not apply
  here: `read_lineage` keeps one record per name and correlates lifetime means. What does remain is
  that the parent's yield used is its **final** lifetime mean, not its mean at the moment of
  breeding, and parent and child overlap in the seasons they are alive, so shared season-to-season
  world variance can inflate the correlation. The paired neutral control carries the same overlap
  and is the check on the size of that inflation; the number should be read as an upper bound on
  additive heritability. On the holistic side the control reads near zero on all three seeds, so
  whatever the inflation is, it is not what the 0.38–0.40 is made of.
- **Bout-score heritability on these populations** (the ticket's Deliverable A item 2) was not in the
  coordinator's fixed scope and was not run. The contrast with the arena's zero remains a contrast
  across two literatures, not within one run.
- **No champion was labbed.** No claim is made here about what any individual best is; the claims are
  about population means, ancestry and heritability. "Locomotion from survival" is read off the
  holistic mean gain going from ~0 to > +1 a season under starvation while the paired control's holistic
  mean stays at ~0 for 600 seasons, not off any body's gait.
- **Frame → calibrate → manipulation → measure.** The instruments are the toolkit's own `heritability`,
  `founder_survival` and RBT-59's depth logic, already round-tripped on 801–803 and RBT-59/60; nothing
  new was introduced and nothing was re-calibrated here. Stated, not unstated.
- **The 801 neutral control's 0.52 holistic heritability**, quoted in `docs/foraging-world.md`, is
  contradicted by every fresh control (804: 0.07, 805: −0.06, 806: N806, RBT-82's re-run: 0.15) and is
  marked unverified there per RBT-82. The three controls here are the measured figures.
- **One flag changed per run, one economy, one code version.** Three seeds is three seeds; nothing
  here is a distribution.

## 6. Process notes

- Launched as harness background tasks, not `nohup` (RBT-60's death at season 107). All six ran to
  "results in". Two harness tasks (neutral-804, forage-805) reported exit code 2 *after* their run
  completed: bash re-read `launch.sh` at its old offset after I rewrote the file to add the code pin.
  The runs' outputs are intact and the artefact is recorded here so nobody reads exit 2 as a death.
  Do not edit a running script.
- Two at a time on four cores at about 5.5 seasons a minute each; a pair took about 110 minutes.
- The first four RBT-71 commits went onto the integration branch directly; the coordinator asked
  for a results branch and everything from `c62d9ef` on is on `results/RBT-71`, PR'd with this report.

## Files

`launch.sh`, `measure.py`, `measure.json`, `readout-804.txt`, `readout-805.txt`, `readout-806.txt`,
`readout-all.txt`, `{forage,neutral}-{804,805,806}/config.json`, `*.code.txt`. Bulk output on the
machine that ran it, regenerable from the command above (the simulator is deterministic; RBT-60
confirmed 11,218 lineage records identical across two launches).
