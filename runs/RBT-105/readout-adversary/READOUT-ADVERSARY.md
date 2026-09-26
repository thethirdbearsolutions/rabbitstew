# RBT-105 readout adversary

Written by the RBT-105 readout adversary (session_017YgnhxsX4sfebart1i4MgW), 2026-09-26, against PR #209 at `ec30e15`.
The designer's files are not edited. Every number here comes from a probe in this directory:

| probe | reads | what it does |
|---|---|---|
| `probe_roundtrip.txt` | a fresh worktree of `ec30e15` | reproduces the three readouts, and audits which files `readout.py` opens |
| `probe_rederive_bulk.txt` | the 17 checkpoints `ckpt/rbt-105-*`, restored | deletes every table, re-runs `post_run.py` from the bulk, and diffs against the committed files |
| `probe_perturb.txt` | the fresh worktree | makes six one-cell perturbations |
| `probe_stats.py` → `.txt` | committed files | R1's null, seed clustering, undecided handling, the bars, bar-free cuts, a continuous ICC, and R2 |
| `probe_windows.py` → `.txt` | the replicate bulk | the design adversary's `probe_distinct.py` windows, applied to the 16 replicates |
| `probe_aa.py` → `.txt` | committed `seasons.txt` | what the 0.132 A/A is, and how it varies with time since divergence |

No new arm was run.

## Summary

- **The numbers are right** (F1).
  - The tables regenerate byte for byte from the 600/600 bulk of all 17 arms.
  - All 17 arms are read, and none is dropped or substituted.
  - R1 = SUBSTANTIAL HISTORY, R2 p = 0.0113 and the A/A 0.132 all reproduce.
- **Three MUST-FIX items, all about wording.** No verdict is wrong.
  - **F2. The margin analysis (H1) left out the originals.** Seed 7's original sits on the discard bar (distinct 2), and seed 7 carries 2 of the 5 flips.
    - Move the discard bar to ≤ 1 and R1 falls to NOT DECIDED: F = 2 of 10, and P(Bin(10, ½) ≤ 2) = 0.055, a hair from FOUNDERS DOMINANT.
    - 7-b1's acquired count of 8 also rests on its last snapshot: drop season 590 and it reads 7.
    - With a single bar-free cut placed in the originals' late-rate gap, R1 comes out SUBSTANTIAL HISTORY at 5 of the 12 cut points and FOUNDERS DOMINANT at the other 7.
  - **F3. The combined sentence goes beyond both verdicts.** The sentence is "set by history, on a founder-dependent propensity", along with "history decides the fate" and "not a property of the founding population".
    - R1 licenses only q > 0.1. The 95% interval for the flip rate is [0.13, 0.65].
    - On the continuous late rate, the founders' share of the replicates' variance is ICC ≈ 0.72, 95% CI [0.15, 0.94] (post hoc).
    - The verdict table registers no combined sentence.
  - **F8. The A/A, 0.132.** The arithmetic is right, and paired equals holistic exactly. But "a one-directional bound in each sense" does not hold, and the conclusion drawn from it does not follow.
    - The spread does not grow with time since divergence: 0.110 in the first 100 seasons, and 0.109 in the time-matched [60, 160).
    - So it is not shown to be an upper bound on a challenge arm's A/A.
    - The cull figures therefore cannot be called "at the low end".
    - This is the number paper 9 and RBT-107 will cite, so its permitted use is pinned down below.
- **Caveats, no fix to the verdicts:**
  - F4: where 0.1 comes from, and how sensitive R1 is to it;
  - F5: clustering by seed;
  - F7: R2's seed-level p;
  - F9: flip rates are conditional on seeds chosen near the bars.
- **NONE:** F6 (undecided handling) and F10 (the lessons).

## Findings

### F1 NONE: re-derivation, inputs and provenance

**Round trip** (`probe_roundtrip.txt`).
- A fresh `git worktree` of `ec30e15` held 0 untracked or ignored files, and 0 bulk files under `runs/`.
- `readout.py`, `aa_spread.py` and `readout_posthoc.py` all exit 0 and reproduce their committed outputs byte for byte (sha256 `9047748d0588`, `0c7199799a7c`, `d7118050a62c`).

**What `readout.py` opens** (Python audit hook):
- the 16 replicates' `oscillator.txt`, `osc_births.txt` and `lineage-last.txt`;
- 17 `pairing.txt` files, the control's included;
- the 8 originals' `runs/RBT-90/forage-SEED/oscillator.txt` and `lineage-last.txt`;
- `part2_readout.py`.

It opens no bulk and no ckpt path. All 17 arms are read, and none is dropped. The control enters only through its gate, as registered.

**From the bulk (README rule 6)** (`probe_rederive_bulk.txt`).
- I restored all 17 checkpoints with `scripts/durable.sh restore`. Every one is at 600/600: `state.json` season 600, 1200 `seasons.txt` rows, and 60 holistic bests up to `best_gen0590`.
- In a worktree of `ec30e15` I deleted every arm's `seasons.txt`, `lineage-last.txt`, `oscillator.txt`, `osc_births.txt` and `pairing.txt`, and re-ran `post_run.py` from the bulk.
- **All 17 × 6 files, `config.json` included, are byte-identical to the committed ones.**
- `readout.py` and `aa_spread.py` on the regenerated tables give the committed hashes.
- Each `config.json` carries the arm's own seed and `breed_stream`, 17 of 17. No arm was substituted.

**Perturbations** (`probe_perturb.txt`). One cell each, in the fresh worktree, reverted after each:

| # | cell | what moved |
|---|---|---|
| P1 | 805-b2 `distinct` 12 → 7 | F 5 → 4, n 14 → 13; still SUBSTANTIAL HISTORY (p = 0.034); R0 now names 7 and 2 |
| P2 | **the original** `RBT-90/forage-7` `distinct` 2 → 3 | seed 7 becomes UNCLEAR; F = 3, n = 12; **R1 NOT DECIDED** (see F2) |
| P3 | 2-b1 `late_k` 98 → 5 | R1 unchanged; R2 T 2.348 → 1.987, p 0.0113 → 0.0296 |
| P4 | 1-b2 pairing founders line → False | `INVALID: pairing 1-b2 failed; no verdict` |
| P5 | 804-b2 `oscillator.txt` removed | `incomplete (804-b2 not analysed): no verdict` |
| P6 | 806-b1 season 450 holistic income +1.0 | only 806-b1's recovery and late rows move, and those RMS values go 0.132 → 0.133 and 0.118 → 0.119 |

### F2 MUST-FIX: the margin analysis missed the originals on the bars, and the verdict depends on the discretisation

**What H1 checked.** It jittered the two *replicates* on a bar (7-b1 at 8, 2-b1 at 2). It did not check the originals. **Seed 7's original sits exactly on the discard bar, at distinct = 2**, and seed 7 contributes 2 of the 5 flips.

**Every ±1 step at each bar, with the originals reclassified by the same bars** (`probe_stats.txt` S4):

| bars | F / n | R1 |
|---|---|---|
| D ≤ 2, A ≥ 8 (registered) | 5 / 14 | SUBSTANTIAL HISTORY (0.0092) |
| D ≤ 2 or 3, A ≥ 7 | 5 / 14 | SUBSTANTIAL HISTORY |
| D ≤ 2 or 3, A ≥ 9 | 4 / 12 | SUBSTANTIAL HISTORY (0.026) |
| **D ≤ 1, A ≥ 7, 8 or 9** | **2 / 10 or 2 / 9** | **NOT DECIDED**; P(Bin(10, ½) ≤ 2) = 0.055, one step from FOUNDERS DOMINANT |

The bars are RBT-84's, imported unchanged and fixed long before any arm, so there is no question of tuning. **The verdict is right as registered.** But it holds on 6 of the 9 bar pairs, and on none where D ≤ 1.

**One snapshot** (`probe_windows.txt`).
- 7-b1's count of 8 becomes 7 (undecided) when the last snapshot is dropped (`to580`).
- In its second half (`late`, seasons 300–590) 7-b1 counts 1, which is discarded.
- Its birth rate falls block by block: 0.321, 0.129, 0.091, 0.051.
- That is the original's trajectory (0.157, then about 0), only slower: early carriage, then loss.
- 806-b2 (8) behaves the same way: `late` gives 1, and its last block is 0.031.
- Its rate ends acquired-like at 0.296.

So, of the five flips:
- 7-b1 sits on a bar at both ends: its original's 2, and its own 8, which rests on one snapshot;
- 2-b1 sits on the bar, with an acquired-like late rate (0.257);
- 7-b2 flips far from the bar on its own count (14), but **its original is on the bar**. The report's "7-b2 (14) … far from any bar" is wrong on that count;
- 805-b2 (1 → 12; late rate 0.004 → 0.416) and 2-b2 (18 → 0; late rate 0.337 → 0.025) are the two flips that no bar choice touches. R0's HISTORY stands on them alone (P2).

**Bar-free** (S5). Use one cut, with no undecided band. A flip is then a replicate on the other side of the cut from its original.

On `distinct`:
- **SUBSTANTIAL HISTORY for every cut from 2.5 to 12.5.** F runs 5–7 of 16.
- FOUNDERS DOMINANT at a cut of 0.5, 1.5 or ≥ 15.5, where only the extreme seeds can cross.

On the late rate, with the cut anywhere in the originals' own gap (0.013, 0.221):
- F runs 3–6 of 16.
- The verdict alternates: SUBSTANTIAL HISTORY at 0.0131, 0.03, 0.05, 0.13 and 0.15; **FOUNDERS DOMINANT** at 0.02, 0.061–0.10, 0.20 and 0.22.
- At n = 16 the two R1 bars meet (F ≤ 4 against F ≥ 5), so one replicate crossing the cut switches between opposite verdicts.

**Is the verdict an artifact of discretisation?** Partly.
- On the count, it is robust across the middle of the range (S5), and it has two unambiguous flips (805-b2, 2-b2).
- It is not robust to the discard bar at the originals' end, nor to moving from the count to the rate R2 uses.

**Required changes to REPORT.md:**
- Add the originals to H1: 7-orig at 2 on the bar; D ≤ 1 gives NOT DECIDED (F = 2 of 10).
- Add 7-b1's one-snapshot dependence.
- Correct "7-b2 (14) … far from any bar": its original is on the bar.
- Say in the headline that SUBSTANTIAL HISTORY holds at the registered bars and on 6 of 9 ±1 bar pairs, and that it is not bar-free on the late rate.
- R0 HISTORY is carried by 805 and 2 alone.

### F3 MUST-FIX: the combined wording is not a registered verdict, and "history decides" overreaches

**What the verdicts license.**
- **R1 SUBSTANTIAL HISTORY** rejects "q ≤ 0.1".
  - One-sided, it excludes q ≤ 0.153.
  - The two-sided 95% Clopper–Pearson interval is **[0.128, 0.649]** (S8).
  - FOUNDERS DOMINANT's own test at F = 5 of 14 gives 0.212. The data fit neither extreme.
- **R2** says the replicates of acquired originals carry more linked oscillators late than the replicates of discarded ones.

**The continuous picture** (S6, post hoc, replicates only, with the originals left out because they were selected on outcome):
- one-way ICC on R2's y = **0.718, 95% CI [0.15, 0.94]**, exact permutation p over all 2,027,025 pairings = 0.021;
- on log(distinct + 0.5), 0.732, CI [0.18, 0.94].

As a point estimate, the founders account for about 70% of the between-run variance in late carriage. The interval is very wide.

**What the report says:**
- "oscillator fate is not a property of the founding population";
- "the founders shift the propensity, and history decides the fate";
- **"set by history, on a founder-dependent propensity"**.

"History decides" and "not a property" read as history dominant. Nothing registered supports that. The flip-rate interval reaches 0.13, and the continuous founder share has a point estimate of 0.7.

**The verdict table.** `PREREGISTRATION.md` §3 registers R1's three sentences and R2's one sentence, and no joint sentence. Asserting both together is statistically fine: an intersection–union claim has size ≤ α, so there is no multiplicity problem (F7). But the joint sentence has to be the two registered sentences side by side, not a new synthesis that ranks history above the founders.

**Proposed wording:**
> Oscillator fate is **not fixed by the founding population**: from byte-identical founders, a different breeding history reversed the fate in 5 of 14 decided replicates (R1 SUBSTANTIAL HISTORY; the flip rate exceeds 0.1, 95% interval 0.13–0.65), on 3 of 8 founding populations. On two of them (805, 2) the reversal is far from any bar. **The founders shift the late oscillator birth rate** (R2, p = 0.011). How the variation divides between founders and history is not resolved at this n: post hoc, on the replicates' late rate, the founders' share is 0.72 [0.15, 0.94].

That replaces RBT-90 part 2's "one run per founding population cannot separate founders from history". It separates them, and finds both, in unresolved proportion.

**H3 and the meaning of "fate".**
- The replicates are not bimodal: 6 of 16 fall in the originals' gap, and count and rate disagree on 7-b1, 2-b1 and 806-b2.
- So the trait is continuous, and "fate" is a threshold on it.
- The registered classifier still answers a well-posed question: does the same founding population land on both sides of RBT-84's bars?
- A flip rate on a thresholded continuous trait depends on how close the seeds sit to the threshold (F9). It is not a measure of history's share.
- The report should say that R1 answers "does the same founders' outcome cross the bars?", and that the "how much" is S6's continuous quantity, not q.

### F4 CAVEAT: R1's null, 0.1

**Where it comes from.**
- 0.1 was proposed by the design adversary as the line for a "weak history" effect: ADVERSARY.md F2, "HISTORY SUBSTANTIAL if P(Bin(n, 0.1) ≥ F) ≤ 0.05".
- The coordinator adopted it at 17:35, and it is registered (`PREREGISTRATION.md` §3; `Q_SUBST = 0.1` in `readout.py`).
- It is **a chosen line, not a measured rate.** It is not the classifier's misclassification rate, and nothing measured it.

**What a founders-only world flips at.**
- Under the design adversary's own model at icc = 1, P(SUBSTANTIAL HISTORY) is 0.000 (two-state) and 0.001 (lognormal).
- On the classifier's measured noise:
  - between adjacent checkpoints (`all` against `to580`), no run of 26 crosses D ↔ A: the 10 RBT-90 originals (`adversary/probe_distinct.txt`) and the 16 replicates (`probe_windows.txt`). One run, 7-b1, moves A → undecided;
  - the half-sample windows do cross (3 of 16 replicates), but a half-sample's count is smaller by construction, so the bars are not calibrated for it.
- So a founders-only world would flip at well under 0.1 from classifier noise, and 0.1 is a generous null for "founders fix it". **R1 answers "is the flip rate above a weak-history line of 0.1?". It does not answer "is history more than classifier noise?"**, which is easier.

**Sensitivity (S1):**

| null q | P(Bin(14, q) ≥ 5) | R1 fires? |
|---|---|---|
| 0.05 | 0.0004 | yes |
| 0.10 (registered) | 0.0092 | yes |
| 0.15 | 0.047 | yes |
| 0.20 | 0.130 | no |

- The largest null q it rejects is 0.153.
- At n = 16, with the undecided replicates counted as kept, q = 0.15 gives 0.079: no.

**For the report:** state where 0.1 comes from, and that the verdict survives up to q ≈ 0.15.

### F5 CAVEAT: clustering by seed

- **The flips are clustered.** Both replicates flipped on 7 and on 2. At the observed rate 5/14, independence predicts 0.89 seeds with both flipped; 2 were observed.
- In both cases the original is the odd run out. That is history in the original run, counted twice.

**A seed-clustered test** (S2). In the limit, one seed-level event (the original deviating) flips both replicates.
- Then the count is "seeds with ≥ 1 flip": **3 of 7** (seed 4 has no decided replicate).
- **P(Bin(7, 0.1) ≥ 3) = 0.026: it holds.** The largest seed-level null it rejects is 0.129; at 0.15, p = 0.074.
- Under independent replicates the per-replicate test is the right one (0.0092).
- The information-losing "≥ 1 of 2 flips" seed test at q = 0.1 gives 0.13. It is shown, but it is not the right cluster test.

**For the report:** the margin under clustering is thinner (q* 0.13, not 0.15). The clustering is itself evidence of a shared founder propensity: H4 found 6 of 7 b1/b2 pairs agree.

### F6 NONE: undecided handling

- Registered in `PREREGISTRATION.md` §3: "a replicate is decided if its fate is discarded or acquired". EXTINCT counts as undecided, and n is the number decided. It is not a choice made after the data.
- All 9 imputations of 4-b1 (4) and 4-b2 (6) (kept, flipped or excluded, for each) give SUBSTANTIAL HISTORY, with p between 0.0005 and 0.017 (S3).
- Seed 4's replicates (4 and 6, against an original of 9) both moved toward discarded. On a continuous reading that is more history, not less.

### F7 CAVEAT: R2 is sound as registered; its seed-level version is borderline

**Registration.**
- R2 is registered as SECONDARY, with its own α = 0.05 (amendment 4).
- No family-wise correction was registered, and none is needed for the conjunction (F3).
- It reproduces: T = +2.348, p = 0.0113.
- The replicate-level permutation is valid under R2's null (icc = 0 makes all 16 arms exchangeable), so the registered p stands.

**Robustness** (S7, post hoc):

| test | p |
|---|---|
| seed means, 8 seeds, C(8, 4) = 70 labellings (floor 0.014) | **0.057** |
| leave one seed out | 0.004–0.049; 1 out 0.049, 804 out 0.046 |
| rank version | 0.014 |
| on log(distinct + 0.5), the count R1 reads | **0.090** |

- The seed-level test is the right one if the question is about founding populations rather than runs.
- R2 is a property of the late birth rate, not of the count, and it leans on the two zero-carriage seeds (1, 804).

**For the report:**
- Keep the sentence "the founders shift the late oscillator birth rate".
- Do not generalise it to "the fate's propensity" without S7's two lines.

### F8 MUST-FIX: the 0.132 A/A, what it is, and what it may be cited for

**The computation is right** (`probe_aa.txt` A1, A4).
- The designed-body rows are identical to the original in all 600 seasons, in 16 of 16 replicates.
- RMS(rep − orig) of R-body over [T+60, T+160) = 0.1321, and of holistic income alone = 0.1321. The maximum difference is 0.
- "Paired equals holistic" holds exactly. The paired contrast has **no designed-side term at all**.
- 0.132/√10 = 0.042. C3's +0.138 is 3.3 SE on it, the residual 0.4 SE, and C4's 11.0 SE: all correct.

**What it is.**
- An estimate of one component of noise: how far holistic income, at fixed founders, in fixed worlds, beside a fixed designed fauna, differs between two breeding histories.
- It covers **breed stream only, with the founders shared.**

**What it is not.**
- **It is not a turnover null.** No one is killed and no refill is forced. It cannot stand in for the random-cull null of lesson 2, and says nothing about what a cull does.
- It is not a designed-fauna A/A: that side is 0 by construction.
- It is not the same object as the cull contrasts C3 and C4 used as "A/A-like" (0.071–0.123). Those are cull − base, and they carry:
  - the cull's own mean (+0.033, +0.043; RBT-100 F7);
  - post-T history in **both** faunas.

**"A one-directional bound in each sense": not established, and the conclusion does not follow.**
- *In time.* The report and `aa_spread.txt` call it an upper bound for the recovery window, because the replicates diverge from season 0 rather than from T. The spread does not grow with time since divergence (A2):

| window | RMS(rep − orig) of holistic income |
|---|---|
| [0, 100) | 0.110 |
| [60, 160), the time-matched analogue of [T+60, T+160) | **0.109** |
| [200, 300) | 0.144 |
| [350, 450) | 0.173 |
| [500, 600) | 0.101 |

  - The window-to-window variation, 0.10–0.17, is larger than any trend.
  - The time-matched figure is 0.109, not 0.132.
  - So "upper bound" is not shown. At best, it is an estimate whose value depends on the window by a factor of about 1.7.
- *In fauna.* It omits designed-side history entirely, so it understates on that count, as the report says.
- **"So the cull-based estimates were not too large. If anything they sit at the low end" does not follow.**
  - To say the cull figures are too small, 0.132 would have to be a lower bound on the challenge A/A. The report calls it an upper bound in time.
  - The time-matched 0.109 sits inside C3 and C4's own 0.071–0.123.
  - The correct statement is: **same order of magnitude; no evidence the cull-based figures are too large or too small.**
  - This is the smaller rule "an upper bound certifies only one direction", in a new place.
- *An offset* (A2, post hoc).
  - In [60, 160), the replicates sit below their originals on 7 of 8 founding populations: mean −0.075, two-sided sign test p = 0.070.
  - The RMS includes that offset. It is not a spread about zero.
  - By [450, 600) the mean is +0.004.

**Permitted citation, for paper 9 and RBT-107.**
> RBT-105 measured the run-to-run spread that breeding history alone produces in the co-evolved fauna's income, from byte-identical founders, in RBT-90 part 2's baseline ecology, with the designed fauna held identical: RMS of a single-seed difference 0.10–0.17 across 100-season windows (0.132 at RBT-92's recovery window, 0.109 at the time-matched [60, 160)). It contains no turnover, no treatment and no designed-fauna history. It is a comparator of scale for a paired R-body contrast, not a bound in either direction, and not a null for any event.

**Not permitted:**
- calling it "an upper bound on a challenge arm's A/A";
- using it to say "the cull-based A/A figures were too small, or at the low end";
- using it as a turnover or random-cull null;
- quoting "3.3 SE" (C3) as a test rather than as a re-scaling on this comparator.

### F9 CAVEAT: the flip rate is conditional on seeds chosen near the bars

- Wave 1 was chosen nearest the bars by the originals' counts (7 at 2, 805 at 1, 4 at 9, 807 at 10). On a continuous trait, a threshold flips most where the seeds sit near it.
- **q = 5/14 is the flip rate of this outcome-selected set**, not of a random founding population.
- Seed 2 (18) was not a boundary seed and flipped on both replicates. That is the strongest single piece of evidence for history, and it should be named as such.

**For the report:** qualify "5 of 14" with "among founding populations chosen mostly near the bars". The report already says this for R2, under H4.

### F10 NONE: programme lessons (paper 9 §6)

- **Matched-null power on the absent verdict.** FOUNDERS DOMINANT carries its power: 0.83 / 0.69 at icc 0.7 (H2).
  - H2 is simulated at n = 16, while the realised n is 14. That is a small overstatement, and worth a clause.
  - The other absent verdict, R1 NOT DECIDED, needs no power statement.
- **Survival.** `alive` = 60 everywhere, with A/A 0.000. It is not read, and no survival claim is made.
- **Outcome-defined subsets are labelled post hoc:** H4 and H5, and in this report S5–S7 and A2.
- **Lessons 1, 3, 4, 7 and 8** need an event, and RBT-105 has none. The report says so correctly.
- **The sign-guard rule** is where the report fell short (F2): it jittered the replicates and not the originals on the bar.
- **"An upper bound certifies only one direction"** was broken in F8.

## For the designer

1. **F2.** In H1, add the originals on a bar (7-orig at 2; with D ≤ 1, F = 2 of 10, NOT DECIDED) and 7-b1's one-snapshot count. Correct the R0 line "7-b2 … far from any bar". State that the verdict holds on 6 of 9 ±1 bar pairs and is not bar-free on the late rate.
2. **F3.** Replace "set by history, on a founder-dependent propensity", "history decides the fate" and "not a property of the founding population" with the two registered sentences side by side: the flip-rate interval, and the continuous founder share, labelled post hoc (proposed wording above).
3. **F8.** Drop "a one-directional bound in each sense" and "the cull-based estimates were not too large; if anything they sit at the low end". Use the permitted citation above, with the 0.10–0.17 window range and the time-matched 0.109.
4. Caveats to add, in a line each: F4 (0.1 is a chosen line; the verdict holds to q ≈ 0.15), F5 (the seed-clustered p = 0.026, q* = 0.13), F7 (the seed-level R2 p = 0.057; R2 on the count p = 0.09), F9 (conditional on seeds near the bars), and F10 (H2 is at n = 16).

_Generated by [Claude Code](https://claude.ai/code)_
