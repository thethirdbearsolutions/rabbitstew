# RBT-60: the depth law holds, and buying generations did not pay

The baseline `forage-801` with **one flag changed**, `--max-age 15`, seed 801, 600 seasons.
Every expectation below was pre-registered on the issue before the run was launched.

## Scorecard

| # | Pre-registered expectation | Result | |
|---|---|---|---|
| 1 | depth at season 599 in **70–90** (point prediction 80) | holistic **78**, wheeled **67** | **half met** |
| 2 | depth at season 150 in **18–24** | both **18** | **met** |
| 3 | births still equal deaths | **1.000** both populations | **met** |
| 4 | heritability of lifetime yield **below 0.28** | **0.251** and **0.128** | **met** |
| 5 | does the trade pay? *(declined to predict)* | **no** | answered |

## 1. The law

`depth ≈ 2 × seasons ÷ max_age`, derived from deaths settling at `capacity / max_age`.

| season | holistic | wheeled | 2S/A | ratio |
|---|---|---|---|---|
| 107 | 13 | 13 | 14.3 | 0.91 / 0.91 |
| 150 | 18 | 18 | 20.0 | 0.90 / 0.90 |
| 300 | 37 | 36 | 40.0 | 0.93 / 0.90 |
| 599 | **78** | **67** | 79.9 | 0.98 / 0.84 |

Against the baseline's 23 and 22 at the same season, this is **3.4× and 2.9× the search depth from
one flag**. The law predicts within about 10% and is consistently a little **over**: mean ratio
0.91. That direction is expected and refines the derivation — the step `A/2` assumes children arrive
uniformly across a life, and they arrive slightly later than uniform because a parent needs time to
bank the threshold, so each step takes a little longer than half a lifespan.

The wheeled side's 67 at season 599 falls just under the pre-registered band. I am recording
expectation 1 as half met rather than rounding it in.

## 2. Slot-limitation survives, with less slack

Births equal deaths to three decimals in both populations, as predicted. What changed is the
cushion: the share of the living sitting above the birth threshold fell from the baseline's 88% and
93% to **57% and 63%**, and mean energy from 32.0 and 19.5 to **8.0 and 6.5**. Shorter lives leave
less time to bank. Reproduction is still slot-limited; there is simply less idle surplus behind it.

## 3. The cost, as predicted

Heritability of lifetime yield, parent to child, `evals ≥ 5`:

| | baseline | at `max_age` 15 |
|---|---|---|
| holistic | 0.51 | **0.251** |
| wheeled | 0.24–0.39 | **0.128** |

Halved on both sides. An individual now has at most fifteen evaluations rather than sixty, so its
lifetime mean yield is a much noisier estimate of its quality, and the parent-offspring correlation
falls accordingly. This was expectation 4 and it is the mechanism of what follows.

## 4. The trade does not pay

Mean energy gain at season 599:

| | baseline | at `max_age` 15 |
|---|---|---|
| holistic | **+1.41** | **+1.09** |
| wheeled | +0.95 | +0.96 |

3.4× the generations, and foraging performance is **worse** on the evolved side and flat on the
designed one. Response to selection goes as heritability × differential × generations; heritability
halved, generations tripled, and the product did not come out ahead. Noisier selection does not
merely slow progress on a converged population, it lets it drift back.

## 5. And still no sensing

Paired lesion at 64 seeds on the final bests, intact minus noses blanked:

- **Holistic `he2996`: 64 of 64 bouts bit-identical.** Items, items per cell, nearest-item distance,
  every channel, exactly zero difference. Completely blind, as blind as anything in the family.
- **Wheeled `ce3516`: −0.406 items, t = −2.89**, separable and **negative** — it eats 0.469 intact
  against 0.875 with its noses blanked. Nose-hindered. Half its seeds are unmoved, right at the
  zero-count veto's boundary.

Three and a half times the search, and the deepest-searched population this programme has ever run
is bit-identically blind.

## 6. What this does to RBT-59's recommendation, which was mine

RBT-59 concluded that the programme had been buying seasons when it needed generations, and named
`max_age` as the cheapest unexploited lever. **The lever works and the recommendation was wrong.**

`max_age` does not control search depth alone. It controls depth **and** evaluation fidelity, because
a lifespan is also a sample size: fifteen seasons is fifteen draws on which an individual's quality
is judged. Shortening it buys steps and pays in signal, and on this evidence the trade loses.

The corrected recommendation is that the programme needs depth **without** the fidelity cost, which
means decoupling the two: more challenges per season, or repeated evaluation within a season, or a
reproduction scheme that does not tie the number of assessments to the length of a life. That is a
better target than either "enrich the world" or "shorten the lifespan", and it is only visible
because this arm was run.

## 7. Two process notes

**The first launch was killed at season 107** by the environment, not by anything in the run, and I
misread its stalled log as slow progress and invented a cause (core contention) for a number I had
not checked. Recorded on the issue. The relaunch was identical in every flag and seed.

**An unplanned reproducibility check came out of that.** The dead run's lineage log was saved before
the relaunch: **11,218 records through season 100, identical in both runs**, every field. The
simulator is deterministic and the two runs are the same run.

## Files

`A15-801/`, `A15-801.log`, `checkpoint.py`. `A30-801` (the `max_age` 30 middle point) runs next.

## Reproducing

```
rabbitstew ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 --workers 4 \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --max-age 15 --duration 15 --mass-budget 15.34 --conventional-topology --terrain random \
  --random-start --score food --seed 801 --out runs/RBT-60/A15-801
python runs/RBT-60/checkpoint.py runs/RBT-60/A15-801 150 300 599
```
