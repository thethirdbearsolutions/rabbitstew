# RBT-96: the arena's A/A pair, the null spread every arena ±0.10 rule is read against

Pre-registered on RBT-96 before any run (2026-09-26 12:31 UTC, the comment beginning "Pre-registration"); the cost comment (12:37) was posted before launch. Everything below is scored against those two comments. Readouts beside this file: `readout.txt` (the pre-registered readout, from the bulk) and `readout-from-summaries.txt` (the same, from the tracked files alone; identical to `readout.txt` except for the final "wrote …" line).

## Files by role

| role | path |
|---|---|
| the flag (its own commit, `896df2d`) | `rabbitstew/evolution.py` (`holistic_stream_salt`, `spawn_streams(seed, holistic_salt)`), `rabbitstew/cli.py` (`--holistic-stream-salt`), `rabbitstew/ecology.py` (threaded, so the field is never silently ignored) |
| the pinning tests | `tests/test_rng_streams.py`: `test_holistic_stream_salt_moves_only_the_holistic_stream`, `test_holistic_stream_salt_zero_is_the_unsalted_stream` |
| launcher, one arm | `scripts/rbt96_run.sh SEED s0|s1 [WORKERS]` |
| driver, all eight with snapshots | `runs/RBT-96/drive.sh` |
| readout | `runs/RBT-96/readout.py` (imports RBT-85's `readout.py` for the shared columns) |
| configs | `runs/RBT-96/{s0,s1}-{201..204}/config.json` |
| per-run summaries | `generations.txt` (RBT-85's columns), `opponent.txt` (the covariate row from `analysis.json`), `conventional-digest.txt` (both populations' lineage hashes) |
| readouts | `readout.txt`, `readout-from-summaries.txt` |
| bulk (not tracked) | `history.json`, `lineage.jsonl`, `analysis.json`, genomes, logs; all eight directories are on `ckpt/rbt-96-SEED-ARM` |

**Re-derivation:** `python runs/RBT-96/readout.py runs/RBT-96 --from-summaries`. From a clean worktree of `results/RBT-96` that never held the bulk it reproduces `readout-from-summaries.txt` byte for byte. It is a derivation, not a replay: adding 0.11 to one of `s1-201`'s eleven final-fifth checkpoints moves that pair's d from +0.246 to +0.256 and the RMS from 0.1281 to 0.1329. Unlike RBT-85, the pairing hashes and the covariate also re-derive from the checkout.

## 1. The build

- `--holistic-stream-salt S` replaces the holistic stream alone with the SeedSequence at spawn key `(i, S)`, where `i` is the holistic stream's index. The conventional and terrain streams are unchanged.
- **Salt 0 is the unsalted stream exactly**, so every earlier run reproduces from its config.
- Both tests fail on the code before the commit (no such field). They also fail on a wrong salt folded into the root seed, where the wheeled lineage then differs. So they pin the property.
- Suite: 257 → 259, all passing.

## 2. The pairing pairs (item 1)

In all four seeds:
- the two arms' conventional `lineage.jsonl` lines hash identically (5,000 each);
- the terrain and start seeds agree at all 250 generations;
- the holistic lineages differ.

The wheeled side's solo measurements are equal to the digit within every pair. **4/4 pairs pass.** The salt does what it is named after: an independent holistic population meets the same wheeled population on the same terrains, with no manipulation.

## 3. The null spread (items 2–3)

| seed | s0 | s1 | **d = s1 − s0** | wins d (of 2550) | best-ckpt d | wheeled solo approach (both arms) | wheeled steering /3 | holistic solo approach d | terrain d |
|---|---|---|---|---|---|---|---|---|---|
| 201 | 0.318 | 0.564 | **+0.246** | +348 | +0.13 | +1.77 m | 2.91 | +0.95 m | +0.39 |
| 202 | 0.491 | 0.466 | **−0.024** | −264 | −0.11 | −19.27 m | 0.00 | +0.08 m | +0.09 |
| 203 | 0.421 | 0.450 | **+0.029** | +178 | −0.03 | −2.90 m | 1.27 | +0.37 m | +0.00 |
| 204 | 0.281 | 0.218 | **−0.063** | −173 | −0.12 | +1.78 m | 1.55 | −0.63 m | −0.18 |

- **A/A RMS of d = 0.128** (4 df; the true mean is 0 by construction). SD 0.138 (3 df). Mean +0.047.
- |d| < 0.10: **3/4**. |d| < 0.05: **2/4**.
- The 95% χ² interval on σ from the RMS is **[0.077, 0.368]**. Even its lower end is above my pre-registered interval's upper end (0.070).
- RBT-85's three resolution figures at n = 4:

  | figure | RBT-96 | RBT-85 |
  |---|---|---|
  | independent checkpoints | 0.049 | 0.062 |
  | checkpoint-paired | 0.021 | 0.022 |
  | observed spread (2 SE) | **0.138** | 0.046 |

- One run's final-fifth mean scatters about its seed's expectation with SD ≈ RMS/√2 = **0.091**. Checkpoint noise alone predicts 0.035. **Most of the null is not measurement noise within a run but which holistic lineage the run happened to grow.**

**Seed 201 carries most of it.** Its s1 run climbs through the fifths (0.29, 0.32, 0.43, 0.60, 0.56) while s0 stays at 0.32–0.43, and s1's champions are better alone: solo approach +0.95 m, terrain success +0.39. That is a lineage that found a better locomotor, not a scoring artefact. It is the null behaving as a search: sometimes one of two identical runs makes a discovery the other does not. The RMS of the other three is 0.042. I say this as a description, not as a result. **No seed is dropped**: the pre-registration fixed the four, and a null whose tail is a discovery event is the null the rule is read against.

**The covariate.** corr(d, wheeled approach) = +0.38; corr(|d|, wheeled approach) = +0.53. Four points. The largest |d| is against a driving opponent (seed 201, steering 2.91), not a runaway. Nothing says the opponent class scales the null.

## 4. Against RBT-85, and what the flip rules now say (item 4)

- RBT-85's A/B d: −0.079, −0.091, −0.033, +0.010 (SD 0.046, RMS 0.063). The A/A d above: SD 0.138, RMS 0.128.
- SD ratio A/B over A/A **0.34**; variance ratio 0.11 against the F(3,3) 95% band [0.065, 15.4]. The band contains it, two-sided p = 0.11.
- **The A/B pairs were tighter than the A/A pairs, not looser.**

**The ±0.10 rule.** h = 2.776 · RMS / 2 = **0.178 > 0.10**. By the pre-registered flip rule, **the rule is unsound at n = 4**: under the A/A null a four-seed mean reaches |mean| ≥ 0.10 with probability **0.194**, about 1 time in 5. The consequences, as registered:
- Future arena pre-registrations use h, or more seeds. At this null, a 95% half-width of 0.10 needs **9 seeds** (t(8) · 0.128 / 3 = 0.098); 0.05 needs **28**.
- Every arena verdict made by the rule is re-read. The two I know of, RBT-74's and RBT-85's, were both null by rule; if any arena arm was ever called "helps" or "hurts" by it at n = 4, that verdict needs this null beside it. So the re-reading changes words, not verdicts: a "null" by this rule at n = 4 never had the power its threshold implied.

**RBT-85 (k = 4).** Its −0.0485 against the A/A null gives t(4) = −0.76, **two-sided p = 0.49**, well inside the null band ±0.178. By the registered rule (p ≥ 0.05): **RBT-85's −0.049 is inside the arena's null, and the arena cannot see k = 4's effect at n = 4.** RBT-85's verdict, null by rule, stands. What changes is the sentence about reach. RBT-85's t(3) interval (±0.074) was computed from the A/B spread itself. Against the A/A null the reach at n = 4 is ±0.178, not ±0.074.

**RBT-94** (eight k = 4 seeds). Against this null its 95% half-width would be **0.107**, so it could not separate −0.049 from zero. At this null, a half-width of 0.05 needs about 28 paired seeds. Its backlog status is the coordinator's call. On this evidence it cannot answer its own question at the size filed.

**RBT-74's +0.064** (the opponent's composition, not revisited) sits at 1.00 null SE of a four-seed mean (t(4) = 1.00, p = 0.37). It is inside the null on any reading.

**Why were RBT-85's A/B pairs tighter than this A/A null?** This was named in the pre-registration as a difference, and I now think it is not small. RBT-85's two arms shared their holistic **founders** and the holistic stream up to the first reproduction; here the salt moves the whole stream, founders included. So this A/A is a **wider null than the one a founder-sharing A/B design faces**. The pre-registration called that direction conservative for both readings above, and it is:
- "the rule is unsound" is stated against the wider null;
- the founder-sharing null could be as small as RBT-85's own spread suggests, and the F test cannot tell at n = 4.

Two candidate explanations, neither tested here:
- (i) shared founders buy most of RBT-85's +0.97 cross-seed correlation, so an arm that shares founders has a tighter null;
- (ii) four pairs drew no discovery event like seed 201's by chance.

**The measurement that separates them is a founder-sharing A/A**: the salt applied to the holistic stream only after the founders are drawn. It is one flag, 3.2 h here, and it is the null that RBT-85-style arms are actually read against. It is proposed as a follow-up, not run.

## 5. Cross-machine reproduction (item 5)

**0/250 generation rows reproduce in any seed**; the readout's "1/251" is the header line. Each s0 diverges from RBT-85's `base-SEED` at generation 0.
- The cost probe established the cause before launch: under MuJoCo 3.13.0 (RBT-85's version) on this x86 box, generations 0–2 were identical to the 3.14.0 run and different from the laptop's. **The platform (ARM M4 against x86) changes the float path, not the MuJoCo version.**
- The divergence is not cosmetic. It changes the **wheeled population** each seed grows, and so the opponent class:

  | seed | wheeled final-fifth approach, RBT-85 (laptop) | RBT-96 (cloud) |
  |---|---|---|
  | 201 | −19.33 m | +1.77 m |
  | 202 | −14.13 m | −19.27 m |
  | 203 | −0.96 m | −2.90 m |
  | 204 | +1.87 m | +1.78 m |

- **A seed is an artifact of its platform, not only of its code.** Arms that are paired by seed must run on the same platform. Every arena comparison across machines is unpaired.

## 6. The pre-registration, scored

| prediction | confidence | outcome |
|---|---|---|
| all four pairs pass the pairing check | 0.97 | **right** (4/4) |
| A/A RMS ≈ 0.040; realised in [0.020, 0.070] | 0.70 | **wrong**: 0.128, three times my point and outside my interval; its own 95% interval [0.077, 0.368] misses mine |
| A/A spread below RBT-85's A/B spread | 0.60 | **wrong**: A/A SD 0.138 against A/B 0.046 |
| all four \|d\| < 0.10 | 0.85 | **wrong**: 3/4 (seed 201, +0.246) |
| 2.776·RMS/2 < 0.10 (the rule clears the null) | 0.80 | **wrong**: h = 0.178 |
| RBT-85's −0.049 has p < 0.05 against the null | 0.40 | did not happen (p = 0.49); I put 0.60 on this side |
| corr(\|d\|, wheeled approach) small, \|r\| < 0.5 | 0.55 | **wrong, narrowly**: +0.53, four points |
| s0 reproduces RBT-85's base at all 251 rows | 0.25 | **wrong** (0/250); resolved by the cost probe before launch and posted then |
| identical at generation 0 | 0.6 | **wrong**; same |

**My model of the null was checkpoint noise plus a little drift, and it was wrong by a factor of three.** I anchored on RBT-85's two figures, 0.022 as the floor and 0.046 as the ceiling, as the ticket framed them. The ceiling was not a ceiling. It was a measurement of a founder-sharing design's spread, and it bounds the drift from above only under the assumption this arm shows to be false: that an independent holistic lineage behaves like a shared one.

## 7. What is and is not claimed

- **Claimed:** the four A/A differences, their spread, and the rule's consequences under the pre-registered flip rules. The pairing is exact. The platform breaks cross-machine seed reproduction and changes the opponent.
- **Not claimed:**
  - the size of the founder-sharing null (not measured);
  - that seed 201 is an outlier to discount (four points cannot say how heavy the tail is);
  - anything about k = 4 beyond "inside the null".
- **Instrument hygiene, by the README's order:**
  - Frame: RBT-85's arena, one flag.
  - Calibration against a known case: the pairing test pins the salt, and the pairing check per pair shows it held in the runs.
  - Manipulation check: holistic lineages differ in every pair, and the wheeled lineages are identical.
  - There is no effect to measure: this *is* the calibration.
- **The summary step that collapses:** the final-fifth mean collapses 11 checkpoints (within-run SD 0.06–0.18). The checkpoint-paired figure (0.021) is the uncollapsed version and is small, so the spread is between lineages, not within them.
- **Measured, not tuned:** no seed added or dropped, no arm re-run, none resumed; each arm ran once from launch to finish, and its snapshots were never restored. One printed sentence in `readout.py` was corrected after the run, and no number changed: it read "the rule cannot be met by noise alone at 95%" beside a probability of 0.194, which inverts the logic. The diff is on the ticket.

## 8. Compute

- Four-core cloud session, x86_64, Python 3.11.15, MuJoCo 3.14.0, numpy 2.4.6.
- Measured before launch: ~6.4 s per generation at `--workers 4` over the first 10 generations, the same throughput as two concurrent runs at `--workers 2`. `--workers` 2 and 4 give byte-identical arena runs (10 generations, seed 201).
- Launched 12:37 UTC, one seed's pair at a time at `--workers 2`, the toolkit after each. **All done 16:51 UTC: 4 h 14 min wall** for the eight runs plus toolkit, against a pre-launch estimate of ~3.6 h. Pairs took 52–70 min; the slowest arm of a pair sets the pace, leaving two cores idle for its last stretch.

## Follow-ups proposed (not filed; the coordinator's call)

1. **The founder-sharing A/A**: the salt applied only after founders are drawn, seeds 201–204, one flag, ~4 h here. It measures the null that RBT-85-style arms actually face, and it decides whether RBT-85's tight pairs were founders or luck.
2. **The rule**: replace ±0.10 at n = 4 in arena pre-registrations with h from the applicable A/A null, or with n ≥ 9 seeds at this null.
3. **Platform as part of a seed's identity**: `config.json` records neither platform nor MuJoCo version. A two-line addition (`platform.machine()`, `mujoco.__version__`) would make a cross-machine pairing error visible from the config.
