# RBT-105 report: oscillator fate, founding population or run history?

Written by the RBT-105 designer, 2026-09-26, after all 17 arms had merged on integration (#195–#198, #200, #201, #203, #206, #208; every checkpoint 600/600).
- The verdicts are `readout.py` → `readout.txt`, the rule pre-registered in `PREREGISTRATION.md` as amended at 17:35.
- Everything labelled post hoc is `readout_posthoc.py` → `readout_posthoc.txt`, and changes no verdict.
- The ecology A/A is `aa_spread.py` → `aa_spread.txt`.
- Every number below is from one of those files, or from the readout adversary's probes (PR #214, `readout-adversary/`, carried onto this branch unchanged), cited by probe.

**Amended 2026-09-26, after the readout adversary** (`readout-adversary/READOUT-ADVERSARY.md`, F1–F10) and the coordinator's ruling on RBT-105 (21:58 UTC, CLEAR-WITH-AMENDMENTS).
- The amendments are wording only. No verdict and no number of the registered readout changes.
- F2, F3 and F8 are rewritten in place, and F4, F5, F7, F9 and F10 are added as one line each. The first text is in git history (ec30e15).
- Two committed outputs still carry the first wording: the header of `aa_spread.txt` ("UPPER BOUND") and the caveat in `readout_posthoc.txt` H6. Both are **superseded by F8** below. Their scripts are left unedited so that the outputs keep reproducing byte for byte.

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
  - This holds **at the registered bars (D ≤ 2, A ≥ 8) and on 6 of the 9 ±1 bar pairs**. It fails on none of the D ≥ 2 pairs, and on every D ≤ 1 pair, where it becomes NOT DECIDED (F2).
  - It is **not bar-free on the late rate** (F2).
  - R1 answers "does the same founders' outcome cross RBT-84's bars?", not "how much is history" (F3).
- **R2 (secondary): the founders shift the late oscillator rate.**
  - T = +2.348 on the mean log late birth rate, replicates of acquired originals minus replicates of discarded ones.
  - Exact permutation p = 0.0113 over 12870 labellings, originals left out.
- **R0 (reported; it tests only q > 0): HISTORY.** The same founders reach both fates on 3 of 8 founding populations (7, 805, 2).
  - It rests on **805 and 2 alone**, the two whose flips no bar choice touches: 805-b2 went 1 → 12, and 2-b2 went 18 → 0.
  - **Seed 2 is the strongest single piece of evidence for history.** It went from 18 to 2 and to 0 on both replicates, and it was not a boundary seed.

**What the programme may say** (the readout adversary's paragraph, adopted by the ruling, F3):
> Oscillator fate is **not fixed by the founding population**: from byte-identical founders, a different breeding history reversed the fate in 5 of 14 decided replicates (R1 SUBSTANTIAL HISTORY; the flip rate exceeds 0.1, 95% interval 0.13–0.65), on 3 of 8 founding populations. On two of them (805, 2) the reversal is far from any bar. **The founders shift the late oscillator birth rate** (R2, p = 0.011). How the variation divides between founders and history is not resolved at this n: post hoc, on the replicates' late rate, the founders' share is 0.72 [0.15, 0.94].

This replaces RBT-90 part 2's *"one run per founding population cannot separate founders from history"*. The design separates them, and finds both, in unresolved proportion.

The first version's "set by history, on a founder-dependent propensity", "history decides the fate" and "not a property of the founding population" are **withdrawn**. The verdict table registers no joint sentence, and history is not shown to dominate.
- The interval is two-sided Clopper–Pearson (`readout-adversary/probe_stats.txt` S8).
- The founder share is a one-way ICC on R2's y, replicates only, with its permutation p = 0.021 (S6).

## How firm, and what was not found (lessons 1–8 and the six smaller rules, paper 9 §6)

**The margin (the sign-guard rule; H1).**
- At n = 14, SUBSTANTIAL HISTORY needs F ≥ 4. F = 5 is **a margin of one flip**.
- Two of the five flips sit exactly on a bar: 7-b1 at 8, and 2-b1 at 2.
  - Were one of them undecided instead, the verdict holds (F = 4, n = 13).
  - Were both, it falls to NOT DECIDED (F = 3, n = 12).
- The two undecided replicates (seed 4, at 4 and 6) cannot move it: SUBSTANTIAL HISTORY holds whether they had kept or flipped. All nine imputations hold (F6).
- **H1 missed the originals** (F2).
  - **Seed 7's original sits on the discard bar at distinct = 2**, and seed 7 carries 2 of the 5 flips.
  - With D ≤ 1, seed 7's original is undecided: F = 2 of 10, and R1 is NOT DECIDED. P(Bin(10, ½) ≤ 2) = 0.055, one step from FOUNDERS DOMINANT.
  - Over every ±1 bar pair, SUBSTANTIAL HISTORY holds on 6 of 9 (`readout-adversary/probe_stats.txt` S4).
- **7-b1's count of 8 rests on one snapshot** (`readout-adversary/probe_windows.txt`).
  - Without season 590 it reads 7, which is undecided.
  - Its second half reads 1.
  - Its birth rate falls block by block: 0.321, 0.129, 0.091, 0.051. That is early carriage and then loss, like its original's.
- **Correction:** the first version said "7-b2 (14) … flip[s] far from any bar". 7-b2's own count is far from the bars, but **its original is on the bar**. Only 805-b2 and 2-b2 flip far from every bar, and R0 rests on them.
- **Bar-free** (S5):
  - a single cut on `distinct` gives SUBSTANTIAL HISTORY at every cut from 2.5 to 12.5;
  - a single cut on the late rate, anywhere in the originals' gap, gives SUBSTANTIAL HISTORY at 5 of 12 cuts and FOUNDERS DOMINANT at 7. At n = 16 one replicate crossing switches between the two opposite verdicts.

**FOUNDERS DOMINANT was not returned: its matched-null power** (H2, the adversary's model at n = 16).

| icc | two-state model | lognormal model |
|---|---|---|
| 0.5 | 0.538 | 0.407 |
| 0.7 | 0.831 | 0.685 |
| 0.9 | 0.986 | 0.938 |

- The absence speaks against a founder share of icc ≳ 0.7 on the two-state model, and only against icc ≳ 0.9 on the lognormal.
- **F10:** H2 is simulated at the design's n = 16. The realised n is 14, so these powers slightly overstate.

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

## The ecology A/A (`aa_spread.txt`, H6; amended per F8)

**The arithmetic stands.**
- In every replicate the designed-body fauna is identical to the original's in all 600 seasons (16 of 16).
- The paired contrast (rep − orig)_holistic − (rep − orig)_designed is therefore **exactly** the holistic difference. It has no designed-side term.

| window | rep − orig RMS (n = 16) | mean | b1 − b2 RMS (n = 8) |
|---|---|---|---|
| RBT-92's recovery window, [T+60, T+160) | 0.132 | +0.004 | 0.152 |
| before [T−100, T) | 0.130 | −0.041 | 0.093 |
| late [300, 600) | 0.118 | −0.010 | 0.115 |

**The permitted citation**, adopted verbatim by the ruling; paper 9 and RBT-107 cite it only in this form:
> RBT-105 measured the run-to-run spread that breeding history alone produces in the co-evolved fauna's income, from byte-identical founders, in RBT-90 part 2's baseline ecology, with the designed fauna held identical: RMS of a single-seed difference 0.10–0.17 across 100-season windows (0.132 at RBT-92's recovery window, 0.109 at the time-matched [60, 160)). It contains no turnover, no treatment and no designed-fauna history. It is a comparator of scale for a paired R-body contrast, not a bound in either direction, and not a null for any event.

**Withdrawn:**
- "a one-directional bound in each sense": the spread does not grow with time since divergence (`readout-adversary/probe_aa.txt` A2);
- "the cull-based estimates were not too large; if anything they sit at the low end". The time-matched 0.109 sits inside C3 and C4's own 0.071–0.123. **Same order of magnitude: no evidence that the cull-based figures are too large or too small.**
- The re-scalings of C3's and C4's contrasts on 0.132 (3.3, 0.4 and 11.0 SE) are re-scalings on a comparator, not tests.

**Post hoc: an early offset (A2).**
- In [60, 160) the replicates sit below their originals on 7 of 8 founding populations: mean −0.075, two-sided sign test p = 0.070.
- The RMS includes that offset, so it is not a spread about zero.
- By [450, 600) the mean is +0.004.

## Caveats (one line each, per the ruling)

- **F4.** R1's null, q = 0.1, is a chosen weak-history line: the design adversary's, adopted at 17:35. It is not a measured classifier rate. The verdict holds up to q ≈ 0.15 (the largest null rejected is 0.153; S1).
- **F5.** The flips are clustered by seed: both replicates flipped on 7 and on 2. Counted per seed (3 of 7 with a flip), p = 0.026 and q* = 0.13 (S2).
- **F7.** R2 stands as registered (p = 0.0113). On the 8 seed means p = 0.057, and on log(distinct + 0.5), the count R1 reads, p = 0.090 (S7).
- **F9.** q = 5/14 is the flip rate of founding populations chosen mostly near the bars, not of a random founding population.
- **F10.** H2's matched-null powers are simulated at n = 16, while the realised n is 14.

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
