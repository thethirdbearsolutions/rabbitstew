# RBT-105 report: oscillator fate, founding population or run history?

Written by the RBT-105 designer, 2026-09-26, after all 17 arms had merged on integration (#195–#198, #200, #201, #203, #206, #208; every checkpoint 600/600).
- The verdicts are `readout.py` → `readout.txt`, the rule pre-registered in `PREREGISTRATION.md` as amended at 17:35.
- Everything labelled post hoc is `readout_posthoc.py` → `readout_posthoc.txt`, and changes no verdict.
- The ecology A/A is `aa_spread.py` → `aa_spread.txt`.
- Every number below is from one of those files.

## The verdicts (pre-registered)

**Gate: passed.**
- The positive control (seed 7, K = 0) reproduces the RBT-90 part 2 arm byte for byte: `seasons.txt` and `lineage-last.txt` against the committed files (`forage-7-b0/pairing.txt`).
- All 16 replicates keep their founders' fingerprint and their designed-body `seasons.txt` rows identical to the original's.

| seed | original (distinct) | K = 1 | K = 2 | per seed |
|---|---|---|---|---|
| 7 | discarded (2) | **acquired (8)** | **acquired (14)** | FLIPS |
| 805 | discarded (1) | discarded (2) | **acquired (12)** | FLIPS |
| 4 | acquired (9) | undecided (4) | undecided (6) | UNCLEAR |
| 807 | acquired (10) | acquired (15) | acquired (9) | REPLICATES |
| 806 | acquired (16) | acquired (35) | acquired (8) | REPLICATES |
| 2 | acquired (18) | **discarded (2)** | **discarded (0)** | FLIPS |
| 1 | discarded (0) | discarded (1) | discarded (0) | REPLICATES |
| 804 | discarded (0) | discarded (0) | discarded (0) | REPLICATES |

- **R1 (primary): SUBSTANTIAL HISTORY.** 5 flips in 14 decided replicates; P(Bin(14, 0.1) ≥ 5) = 0.0092.
- **R2 (secondary): the founders shift the late oscillator rate.**
  - T = +2.348 on the mean log late birth rate, replicates of acquired originals minus replicates of discarded ones.
  - Exact permutation p = 0.0113 over 12870 labellings, originals left out.
- **R0 (reported; it tests only q > 0): HISTORY.** The same founders reach both fates on 3 of 8 founding populations (7, 805, 2).

**What the programme may say.**
- **Oscillator fate is not a property of the founding population.** From byte-identical founders, in the same worlds, beside the same designed-body fauna, a different breeding history reverses the fate in 5 of 14 decided replicates.
  - The reversals are on 3 of 8 founding populations, in both directions: discarded → acquired on 7 and 805, acquired → discarded on 2.
  - That is above what a history effect of q = 0.1 would give.
- **The founders still matter to how much oscillator carriage there is.** Replicates of originally acquired populations carry linked oscillators at birth at a higher late rate than replicates of originally discarded ones (R2).
- Put together, the founders shift the propensity, and history decides the fate. RBT-90 part 2's wording, *"varies across runs; one run per founding population cannot separate founders from history"*, can now be replaced by: **"set by history, on a founder-dependent propensity"**.

## How firm, and what was not found (lessons 1–8 and the six smaller rules, paper 9 §6)

**The margin (the sign-guard rule; H1).**
- At n = 14, SUBSTANTIAL HISTORY needs F ≥ 4. F = 5 is **a margin of one flip**.
- Two of the five flips sit exactly on a bar: 7-b1 at 8, and 2-b1 at 2.
  - Were one of them undecided instead, the verdict holds (F = 4, n = 13).
  - Were both, it falls to NOT DECIDED (F = 3, n = 12).
- The two undecided replicates (seed 4, at 4 and 6) cannot move it: SUBSTANTIAL HISTORY holds whether they had kept or flipped.
- R0's HISTORY is not fragile: 7-b2 (14), 805-b2 (12) and 2-b2 (0) flip far from any bar.

**FOUNDERS DOMINANT was not returned: its matched-null power** (H2, the adversary's model at n = 16).

| icc | two-state model | lognormal model |
|---|---|---|
| 0.5 | 0.538 | 0.407 |
| 0.7 | 0.831 | 0.685 |
| 0.9 | 0.986 | 0.938 |

- The absence speaks against a founder share of icc ≳ 0.7 on the two-state model, and only against icc ≳ 0.9 on the lognormal.

**The two verdicts together are an unlikely pair under either model** (H2).
- P(SUBSTANTIAL HISTORY and R2) is at most 0.047 (two-state, at icc 0.3–0.5) and 0.057 (lognormal, at icc 0.5–0.6), and below 0.02 at icc 0 and icc ≥ 0.9.
- So the data point to an intermediate founder share, about 0.3–0.6, but neither model fits well.
- **The reason is H3: the replicates are not bimodal.**
  - The originals' late rates had a clean gap: discarded 0.004–0.013, acquired 0.221–0.337, on the 8 design seeds.
  - 6 of the 16 replicates fall inside that gap (0.025–0.191).
  - Two replicates' counts and late rates disagree:
    - 2-b1 is "discarded" by its count (2) with an acquired-like late rate (0.257);
    - 7-b1 is "acquired" by its count (8) with a rate of 0.072.
  - The bimodality RBT-90 part 2 showed was a property of those ten runs, not of the process. The two-state model's premise does not hold for the replicates, so read H2's icc range as indicative only.

**Replicate against replicate (H4, post hoc; the originals were selected on outcome).**
- The two replicate streams agree with each other on 6 of 7 seeds where both are decided. Replicates agree with their original on 9 of 14.
- On seeds 7 and 2 both replicates flipped together, away from the original.
- Under pure history at a base rate of ½, 6 of 7 agreeing pairs has probability 0.062. That is an illustration, not a test, and it points the same way as R2.
- Wave-1 seeds were chosen nearest the bars by their original's count, which is why R2 leaves the originals out. Seed 2 (18) was not a boundary seed.

**Which founder line won (H5, post hoc; RBT-90 F4's observation, on replicates).**
- The original's top founder line wins again on only 4 of 16 replicates.
- **Every flip changed the top line (5/5).** But so did 6 of the 9 kept fates. A change of winner accompanies every reversal without being sufficient for one.

**Lessons that do not apply, and why.**
- **Placebo onsets (1), arithmetic first (3, 7, 8), recovery from d = 0 (4):** there is no event in RBT-105.
- **The analogue of a placebo is in the gate:** the K = 0 control (byte-identical) and b1 against b2.
- **Survival under refill (5):** holistic `alive` is 60 in every window of every arm, and its A/A RMS is 0.000. It is not read.
- **Extinction coding:** no fauna went extinct.
- **UNVALIDATED means unread (6):** every readout here passed its gate.
  - R2's input (`osc_births.py`) reproduces the adversary's block rates on the originals: seed 7, 0.157 / 0.000 / 0.005 / 0.004; seed 4, 0.069 / 0.220 / 0.229 / 0.213.
- **Outcome-defined subsets are labelled post hoc:** H4 and H5.

## The ecology A/A, on the paired R-body scale (`aa_spread.txt`, H6)

**Why the scale is right here.**
- In every replicate the designed-body fauna is byte-identical to the original's (`pairing.txt`). The paired contrast (rep − orig)_holistic − (rep − orig)_designed is therefore exactly the holistic difference.
- `aa_spread.txt`'s `body` row is already on the scale the challenge readouts judge R-body on.

| window | rep − orig RMS (n = 16) | mean | b1 − b2 RMS (n = 8) | SE of a 10-seed mean |
|---|---|---|---|---|
| recovery [T+60, T+160) | **0.132** | +0.004 | 0.152 | 0.042 |
| before [T−100, T) | 0.130 | −0.041 | 0.093 | 0.041 |
| late [300, 600) | 0.118 | −0.010 | 0.115 | 0.037 |

**Against the challenge readouts' scale.**
- C3's cull contrasts gave 0.071 (cull − base) and 0.108 (cull20 − base), pooled 0.091 (`runs/RBT-100/readout-adversary/READOUT-ADVERSARY.md` F7). C4's gave 0.1075–0.1232 (`runs/RBT-101/readout-adversary/probe_readout.txt` P4).
- **RBT-105's recovery-window figure, 0.132, is 1.07–1.86× those, and 1.45× C3's pooled 0.091.** So the cull-based estimates were not too large. If anything they sit at the low end.

**It is a bound in one direction only, and each direction needs care.**
- These replicates diverge from season 0, while a challenge arm diverges from T. On that count, for the recovery window, it is an upper bound on a challenge arm's own A/A.
- But here the designed fauna contributes exactly 0, while a cull A/A moves both faunas. On that count it understates.
- Neither bound certifies the other direction.

**On this scale, the challenge numbers the programme quotes become:**
- C3's paired +0.138: 3.3 SE of a 10-seed mean, against 4.8 on 0.091.
- C3's residual +0.017: 0.4 SE.
- C4's −0.458: 11.0 SE.

The arithmetic is 0.132/√10 = 0.042.

## Predictions, scored

| prediction (PREREGISTRATION.md §4, amended) | confidence | outcome |
|---|---|---|
| The positive control reproduces the RBT-90 arm byte for byte | 0.95 | **right** |
| Every K ≥ 1 arm keeps its founders and designed-body rows | 0.97 | **right** (16/16) |
| R1: SUBSTANTIAL HISTORY | 0.50 | **right** |
| R1: FOUNDERS DOMINANT | 0.35 | not returned |
| R1: NOT DECIDED | 0.15 | not returned |
| R2 fires | 0.55 | **right** (p = 0.0113) |
| R0 prints HISTORY | 0.85 | **right** (3 of 8) |
| At least one flip falls on seed 4 or 7 | 0.60 | **right** (seed 7, both replicates; seed 4 went undecided) |
| The RBT-90 winner line wins again in fewer than half of the 16 replicates | 0.60 | **right** (4 of 16) |

## Reproducing it

From a checkout that never held the bulk:
```
python runs/RBT-105/readout.py          > runs/RBT-105/readout.txt
python runs/RBT-105/aa_spread.py        > runs/RBT-105/aa_spread.txt
python runs/RBT-105/readout_posthoc.py  > runs/RBT-105/readout_posthoc.txt   # H2 simulates; seeded, about 20 s
```
- The round trip is in `roundtrip.txt`: a fresh worktree of this commit, with no bulk, reproduces all three byte for byte.
- The per-arm inputs are the committed `seasons.txt`, `lineage-last.txt`, `oscillator.txt`, `osc_births.txt` and `pairing.txt`, written by `post_run.py` from each arm's bulk while it was there.
