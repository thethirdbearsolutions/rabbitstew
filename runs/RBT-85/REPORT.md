# RBT-85: arena arms that are actually paired, and RBT-74's eight runs again as the first use

Pre-registered on RBT-85 before any run started (2026-09-19, the comment beginning "Pre-registration"). Everything below is scored against that comment. Readouts beside this file: `readout.txt` (the pre-registered readout), `readout-from-summaries.txt` (the same verdict re-derived from the committed `generations.txt` files alone), `toolkit.txt`, `depth.txt`, `demography.txt`. Scripts: `readout.py` here; `depth.py`, `demography.py` and `toolkit.py` are RBT-74's, run unmodified on these runs.

## 1. The result that the ticket is for: the pairing now pairs

In all four seeds the protected and unprotected runs carry **the same wheeled population on the same terrains**: the conventional `lineage.jsonl` lines (names, parents, scores; 5,000 per run) hash identically across the two arms, and the terrain and start seeds agree at all 250 generations. The toolkit confirms it from the other side: the wheeled side's solo measurements are equal to the digit within every pair, and its first-parent depth is identical across arms.

| | RBT-74 (one shared stream) | RBT-85 (per-population streams) |
|---|---|---|
| paired SE of the mean difference | 0.0729 | **0.0231** |
| unpaired SE | 0.0628 | 0.0586 |
| ratio | 1.16 (pairing harmful) | **0.39** |
| corr(base, prot) across seeds | −0.41 | **+0.97** |

Same seeds, same configuration, same k, same machine-independent code path apart from the streams. The unpaired SE barely moved; the paired SE fell by a factor of three. Pairing an arena arm by seed now buys what pairing is supposed to buy.

## 2. Verdict by the pre-registered rule: null, leaning negative

Holistic mean champion fitness over the final fifth (11 checkpoints × 50 round-robin bouts), protected minus unprotected, paired by seed, with the pre-registered covariate beside each difference:

| seed | base | prot | **d** | wins d (of 2550) | best checkpoint d | wheeled final-fifth solo approach (both arms) | wheeled steering /3 |
|---|---|---|---|---|---|---|---|
| 201 | 0.459 | 0.380 | **−0.080** | −370 | −0.25 | −19.33 m | 0.00 |
| 202 | 0.485 | 0.394 | **−0.091** | −383 | −0.26 | −14.13 m | 0.00 |
| 203 | 0.306 | 0.273 | **−0.033** | −203 | −0.16 | −0.96 m | 2.09 |
| 204 | 0.290 | 0.300 | **+0.010** | +4 | +0.06 | +1.87 m | 2.73 |

Mean **−0.0485**, range [−0.091, +0.010], three negative, one positive, zero count 1 (seed 204's +0.0099 is under the 0.01 line). Rule: *hurts* needs mean ≤ −0.10 and ≥ 3 negative; the sign count is met and the mean is not. **Null.** The controller-only disambiguating arm is not triggered and was not run.

**What the report is entitled to say.** SE of the paired mean 0.0231, so the mean sits at −2.10 SE. The pre-registration committed to reporting "the instrument could not see an effect of this size" if |mean| fell inside the realised 2 SE (0.046); it falls a hair outside (0.0485), so that sentence is not available, and neither is its opposite: with four differences the 95% interval is t(3) × SE = ±0.0735, i.e. **[−0.122, +0.025]**, which contains zero and contains the −0.10 threshold. Four properly paired seeds say the effect of k = 4 protection on the bout score is somewhere between a tenth against and a fortieth for. RBT-74's +0.064 is outside that interval's upper end by 0.04 and had the opposite sign; RBT-74's adversary had already shown that figure was the opponent's composition.

## 3. The opponent covariate, reported whether or not it helps

It cannot confound a paired difference any more (it is identical within each pair). Across seeds it still decides the level: holistic final-fifth score against wheeled solo approach, r = −0.95 in the unprotected arm and −0.91 in the protected arm; the two seeds whose wheeled side ran away backward at −14 to −19 m are the two where the holistic side scores 0.38–0.49, and the two with a steering wheeled side are the two at 0.27–0.31. That reproduces RBT-74's split (its r was −0.67 on eight independently drawn opponents) with the opponent now held fixed within pairs.

One thing the covariate shows that I did not predict: the paired difference itself tracks it (r = +0.91 across the four seeds: −0.080 and −0.091 against the runaways, −0.033 and +0.010 against the drivers). **This is four points and I draw nothing from it.** It has at least two readings that this design cannot separate: an opponent-by-arm interaction, or plain scale (against a runaway the holistic score has more room above its floor, so any difference between arms is larger there). The pre-registration said an interaction is not resolvable at n = 4 and that stands. It is recorded because the rule is that the covariate is printed beside the difference whether or not it helps.

On the pre-registered label: I kept RBT-74's "runaway = approach < 0". Seed 203's wheeled side reads −0.96 m with steering 2.09/3, which the label calls a runaway and which is not what RBT-74 meant by one (−7 to −19 m, steering ≤ 0.64). The prediction "holistic scores higher against runaways, both arms" holds under the label as registered (0.417 vs 0.290 unprotected; 0.349 vs 0.300 protected) and more cleanly under the continuous value; the label is a poor summary and the continuous value is the covariate.

## 4. Secondary, pre-registered

**Holistic champions alone from rest** (final-fifth mean over 11 bests, protected minus unprotected): approach **−0.57, −0.39, +0.03, −0.12 m**; terrain success −0.02, −0.11, +0.02, +0.06. Three of four negative on approach, as in RBT-74 (four of four there). The protected champions are not more capable alone. No final best steers to more than 1 of 3 off-axis goals; RBT-74's prot-202 steering champion was a product of that run's draws and does not recur here (these runs do not reproduce RBT-74's by construction).

**Manipulation check** (`demography.txt`, within-run, independent of pairing; a second draw of RBT-74's):

| run | body-changed child − parent | share improved | readaptation child − parent | lineage at age 4 − same lineage at age 0 (n = 882) |
|---|---|---|---|---|
| base 201–204 | −0.117, −0.118, −0.099, −0.079 | 0.25–0.26 | (none) | |
| prot-201 | −0.052 | 0.26 | −0.002 | **+0.003** (0.45 improved) |
| prot-202 | −0.041 | 0.32 | −0.009 | **−0.022** (0.38) |
| prot-203 | −0.050 | 0.24 | −0.005 | **−0.014** (0.41) |
| prot-204 | −0.073 | 0.23 | −0.005 | **−0.008** (0.46) |

RBT-74's finding replicates on fresh draws: a body change costs 0.04–0.12 of bout score at once in every run of both arms, and four controller-only rounds recover none of it (−0.022 to +0.003). The premise holds and the remedy does not act. The cycle ran as designed: 900–902 free and 3,580–3,582 readaptation births per protected run; 4,482 free births per unprotected run.

**A1/A2**: `mass_budget 15.34` and `settle_time 1.0` in all eight `config.json` (printed per run in `readout.txt`); every final best 15.34 kg or under; champions re-measured alone from rest by the toolkit.

## 5. Realised search depth

First-parent chains of the 20 alive at generation 249, medians (`depth.txt`):

| population | mutation events | body changes | controller-only | elite copies | founders |
|---|---|---|---|---|---|
| unprotected holistic | 177, 166, 171, 152 | = mutation events (151 + 1 on 204) | 0–1 | 72–97 | 1 |
| protected holistic | 187, 219, 202, 187 | **46, 52, 48, 43** | 141, 166, 154, 144 | 30–62 | 1 |
| conventional (identical across arms) | 204, 215, 220, 213 | 0 | all | 30–45 | 1 |

~150–180 sequential body mutations in 250 generations unprotected; ~45–50 under protection.

## 6. The pre-registration, scored

| prediction | confidence | outcome |
|---|---|---|
| verdict null | 0.75 | **right** |
| mean paired difference −0.01 | point | sign right; observed −0.049, five times my magnitude |
| all four pairs byte-identical | 0.97 | right |
| corr(base, prot) > 0 and paired SE < unpaired | 0.70 | right (+0.97; ratio 0.39) |
| all four \|d\| ≤ 0.10 | 0.55 | right (max 0.091) |
| holistic scores higher against runaway opponents, both arms | 0.70 | right under the registered label; the label is poor (§3) |
| holistic solo approach d negative in ≥ 3 of 4 | 0.60 | right (3 of 4) |
| 2 SE of the paired mean ~0.08, within 0.05–0.12 | 0.60 | **wrong**: 0.046, just under my interval; the pairing bought more than I expected |
| depth, unprotected mutation events 145–170 | | **two of four outside** (177, 171), both above |
| depth, protected body changes 40–50 | | one of four outside (52) |
| depth, protected controller-only 120–160; mutation events 165–205 | | one of four outside each (166; 219, both prot-202) |
| depth, conventional 205–230 | | one of four outside by one (204) |
| first-parent founders 1 everywhere; conventional depth identical across arms | | right |

I took RBT-74's measured ranges as the depth prediction on the argument that the operators are unchanged. They are, but four runs' ranges are not a population's range, and new draws went outside them in five of sixteen cells. Noted for the next pre-registration that borrows a measured range as a prediction interval.

## 7. What eight runs resolved

Three readings, all printed by `readout.py`: from the unprotected arm's checkpoint SD treated as independent across arms, 0.062; from the checkpoint-paired differences (what shared terrains and opponents actually leave), **0.022**; from the observed spread of the four paired differences, **0.046** at 2 SE, or **0.074** at the t(3) 95% half-width. RBT-74's corresponding figures were 0.054 and 0.146. The arena instrument with per-population streams resolves, at four seeds, roughly a third of what it could before, and the ±0.10 rule is now a threshold the design can see rather than one at its edge. A sharper answer on k = 4 (is −0.05 real) would take more seeds, not a different instrument; at the observed SD of the differences (0.046), eight seeds would put the 95% half-width near 0.04.

## 8. Instrument hygiene, by the README's order

Frame: the arena as RBT-74 ran it, one flag between arms. Calibration against a known-good holistic body: **not done** (none exists; unchanged from RBT-74). Manipulation check: done, within-run (§4). The pairing itself was checked where it could fail: `tests/test_rng_streams.py` fails when one generator is shared, and the per-pair hash is in `readout.txt`. Measured, not tuned: nothing was re-run, no seed was added or dropped, the readout script was written and smoke-tested on throwaway runs before launch and not edited after the runs finished. The summary step that collapses: the final-fifth mean collapses 11 checkpoints whose SD within a run is 0.06–0.23; the checkpoint-paired figure in §7 is the uncollapsed version.

None of the eight runs was resumed; no `lineage.jsonl` holds a duplicated generation.

## 9. Compute

MacBook Air M4 (4 P + 6 E cores), Python 3.12.9, MuJoCo 3.13.0. Eight single-worker runs side by side, launched 14:24 UTC, the last toolkit pass finished 15:42 UTC: **1 h 18 min wall** for the package RBT-74 ran in ~3.7 h on four cloud cores. Generation 0 alone on a core takes 3.9 s; averaged over a full run with eight side by side, 11–19 s per generation.

## 10. What is and is not in the repository

Tracked: the eight `config.json`, the eight `generations.txt` (one row per generation: terrain and start seed, both populations' best and mean bout score, best distance, parts and mass, and each checkpoint's champion mean and wins), the readouts, the scripts, this report. `python runs/RBT-85/readout.py runs/RBT-85 --from-summaries` re-derives the differences, the verdict, the SEs, the correlation and the resolution figures from the tracked files alone (`readout-from-summaries.txt` is that output). The lineage hashes, the covariate, depth, demography and toolkit readouts are printed from bulk that stays out (`lineage.jsonl`, `analysis.json`, `history.json`, genome dumps, logs), per `runs/README.md`; re-deriving those means re-running `scripts/rbt85_run.sh SEED ARM`, which reproduces a run from its config.

## Follow-ups

1. The disambiguating controller-only arm: not triggered (null).
2. Whether −0.05 is real: four more seeds (205–208), same rule, would halve the interval. Cheap here (~1.3 h). Filed as a proposal, **RBT-94**.
3. A resume appends the restart generation to `lineage.jsonl` a second time (pre-existing; history is unaffected; `readout.py` hashes distinct lines). Harmless to every current reader that indexes by name; filed as **RBT-93**.
