# RBT-101 readout adversary: PR #193 (`results/RBT-101-readout` at `880ce66`)

I attacked the RBT-101 readout for challenge C4 (the furniture removed, `--shift terrain=flat`). The designer's
files are not edited. Income, class and re-wiring numbers come from committed tables, read through RBT-92's
`readout.py` as `readout.sh` assembles it. Three probes read bulk, and README rule 6 allows it: bulk restored from
`ckpt/rbt-90-SEED` and `ckpt/rbt-101-shift-SEED`, never a table from a checkpoint, and `probe_bulk.txt` shows that
this bulk regenerates the committed tables byte for byte. No new arm was run. The simulation in `probe_refund.py`
is the ecology's own `run_group`, checked bout for bout against a recorded season (`probe_refund_check.txt`).

| probe | file |
|---|---|
| round trip, five perturbations of my choosing (fresh worktrees of `880ce66`, no bulk) | `probe_rederive.sh` → `probe_rederive.txt` |
| checkpoints: their seasons; `wiring.txt` and the shift tables regenerated from the bulk | `probe_bulk.sh` → `probe_bulk.txt` |
| inputs, class robustness (leave-one-out, windows, flips), the null, A/A, lessons 4–6, scoring | `probe_readout.py` → `probe_readout.txt` |
| **the crux:** the arena's own zero-response season, food/work decomposition, time course, the spread of predictions | `probe_arena.py` → `probe_arena.txt` |
| **the crux, by simulation:** the refund and the response at the same season, separated | `probe_refund.py` → `probe_refund.txt` (harness check `probe_refund_check.txt`) |

## The verdict of this review

- **Class C is computed correctly, follows the registered rule, and stands.** It survives leave-one-seed-out on
  10/10 drops and every 100-season window from T to T+200. It holds one adversarial flip, and 98% of jitters at the
  A/A scale (F3).
- **The attribution is wrong, and it is the crux (F2, MUST-FIX).** The solo probe is not a valid unchanged-gait
  prediction for the arena. In the arena itself, measured three ways, unchanged gaits on flat ground
  predict a paired contrast of **−0.63 to −0.81**, against the observed **−0.458**.
  - **The furniture arithmetic therefore accounts for all of the class-C flip, and more.**
  - The part beyond the arithmetic resolves, and it runs **against** the falsifier: +0.17 to +0.27.
  - Separated by simulation at the same season, the designed fauna's own post-onset gaits forage **worse** than
    the baseline's contemporaneous gaits on flat ground (−0.22) and on random ground (−0.17).
  - The data do not support "the designed fauna adapted better". Neither does the report's "no response beyond
    the arithmetic is shown; a response up to ±0.35 would be invisible".
- **Must change before merge: F2** (the arithmetic, its numbers and the sentences built on it). **F3–F8 are
  caveats** with one-line wording fixes: the A/A reference, the owner's verbatim words, the null's emptiness, the
  T+199 line, and two banked recovery "rights".
- **Nothing here needs a new arm.** The one new measurement is F2's `probe_refund.py`: short, seeded group probes
  in the ecology's own harness, 7200 group bouts.
- **The verdict need not wait for RBT-105** (F6). The paired contrast is 12 A/A standard errors.

## Findings

### F1 NONE (two notes): re-derivation, inputs, no seed dropped, `wiring.txt` from 600/600 bulk

Evidence: `probe_rederive.txt`, `probe_bulk.txt`, `probe_readout.txt` P1.

**Round trip.**
- The fresh worktree of `880ce66` holds 0 untracked or ignored files and 0 bulk-shaped files under `runs/RBT-101`,
  `RBT-92` and `RBT-90`.
- In it, `readout.sh`, `rewire.py`, `placebo.py` and `arith.py` reproduce the committed readouts **byte for byte**
  (sha256 `8ef10665…`, `62c3f7d6…`, `3c947417…`, `4af34840…`).

**Perturbations of my choosing**, each in its own fresh worktree:

| # | cell | what moved |
|---|---|---|
| 1 | a baseline cell, `RBT-90/forage-805` s420 designed +1.0 | seed 805 base recovery R-body +0.2092 → +0.1992; base mean +0.1481 → +0.1471; designed R-shift on 805 +0.789 → +0.779; event − base −0.4582 → −0.4572; the arith residual −0.1331 → −0.1321. 7 + 6 + 5 lines; `rewire.txt` untouched |
| 2 | a wiring cell that reaches the **scored** statistic (F7) | 16 `rewire.txt` lines, including new_existing designed shift − base; no income line |
| 3 | `flat_probe.txt`, 806 designed +0.891 → +0.391 | only `arith.txt` (6 lines): residual −0.133 → −0.183. The arithmetic reads the committed probe |
| 4 | `shift-805/` deleted | `readout.sh`: "not read", 9/10, exit 0. `placebo.py` and `arith.py` crash (FileNotFoundError). Loud, not silent |
| 5 | `shift-806/seasons.txt` replaced by 807's | `readout.sh`: V0 FAIL, "the shift is not read", exit 1. **`placebo.py` and `arith.py` have no V0 of their own: they exit 0 and 9 lines of `placebo.txt` move** |

**Inputs.**
- **10 shift arms** were read. Each config has the right seed, `shift_at = T` from `onset.txt` and `terrain=flat`.
  Each `events.txt` has the shift from T to 599, and each table spans seasons 0–599.
- **4 cull arms** were read (801 3/0, 1 3/0, 2 0/2, 4 1/0). Each config matches `cull-k-SEED.txt`, and `events.txt`
  has exactly that cull at T.
- **6 k = 0/0 seeds** have no cull directory, and the baseline is read as the null.
- **10 cull20 arms** from RBT-92 are linked (20/20 at T), plus the 10 RBT-90 baselines.
- **No seed dropped or substituted.**

**README rule 6** (`probe_bulk.txt`).
- All ten `ckpt/rbt-90-SEED` checkpoints stand at 600/600.
- **`base-SEED/wiring.txt` regenerates byte for byte from that bulk on 10/10 seeds.**
- **Shift checkpoints.** Eight stand at 600/600. From their bulk, `tables.py` and `wiring.py` regenerate
  `seasons.txt`, `lineage-last.txt`, `bodysig.txt`, `events.txt` and `wiring.txt` byte for byte.
- **`ckpt/rbt-101-shift-804` stands at 548/600 and `-805` at 599/600.** Both were last saved at 16:20, before
  their post-run tables were committed (804 at 16:26). So the arm runners skipped rule 6's final save. Their
  committed `seasons.txt` equal the checkpoint bulk's on its whole prefix.
- **Every season this review reads from the bulk is ≤ T + 160 (518 on 804), so it is covered.**
- Nothing in the readout reads a checkpoint.

**Notes (suggestions, not required for the verdict):**
- `placebo.py` and `arith.py` now carry the report's headline contrasts (lessons 2 and 3). They should refuse to
  print unless `readout.py`'s V0–V2 pass, as `readout.py` does.
- The owner could re-save 804 and 805 from the arm sessions' directories if those still exist. Otherwise the
  committed tables are the record.

### F2 MUST-FIX (the crux, lesson 3): the arena's own unchanged-gait arithmetic over-predicts the effect; the residual resolves the other way, and the non-arithmetic part runs against the designed body

Evidence: `probe_arena.txt` (Z, Z10, D, TC, S), `probe_refund.txt` and `probe_refund_check.txt`.

**Is the solo probe a valid unchanged-gait prediction?**
- **Committed before any arm: yes.** `flat_probe.py`/`.txt` are in `b806ede` at 13:45 UTC. The first arm
  launched at 15:21 (`cdd5056`, seed 801), and the file has not changed since.
- **Its use as the arithmetic was not registered.** §1 and §10 say "the probe enters no verdict". §10's own
  reading of it halved the solo gain for four to a group. `arith.py` was written at 19:35, after every arm, and
  uses the probe **undiscounted**. With the registered discount the residual is **−0.296 [−0.511, −0.080]**, and
  it resolves (`probe_arena.txt` S).
- **What the probe measures:**
  - **Bodies:** one season-300 best per fauna, not the population at T.
  - **Setting:** alone in the arena, not four to a group.
  - **Unit:** items, not gain. This last one does not matter. In the arena the work term changes by
    +0.001–0.018 (0.03 × kJ) on flat ground (`probe_arena.txt` Z, D), so the income change is food.
- **Solo is not the arena, and the difference has a sign.**
  - The onset population, unchanged, in its own groups of four on its own start seeds, gains **+0.79** designed
    and **+0.16** co-evolved (Z10).
  - The solo bests gain +0.57 and +0.25.
  - The probe under-predicts the wheels' refund and over-predicts the co-evolved body's.
  - Per seed it predicts neither the arena (r(probe, Z10) −0.28 and −0.00) nor the outcome (r −0.04).

**Three unchanged-gait predictions made in the arena itself.** None uses a genome born after T; the same-season split
below adds the no-event baseline's own T+110 population, and no shift-arm genome enters a prediction.

1. **Z, the arm's own season T.** Births are processed after the season's gains, so in season T the shift arm plays
   the baseline's individuals, in the same groups of four, from the same start seeds
   (`start_seed_check.txt`). Only the terrain differs; the pairs are the individuals that survive season T in both arms (54–60 per fauna). This is the designer's "natural next measurement" (§8
   caveat 7), already on disk in the bulk. Per individual, gain(shift) − gain(base).
2. **Z10:** the same over [T, T+10), on pre-T-born individuals alive in both arms, paired by name. That is 464–572
   pairs per seed and fauna.
3. **Simulation, `probe_refund.py`:** the ecology's `run_group` with the run's config, four to an arena, four
   seeded draws, flat against random.
   - The harness reproduces a recorded season **bout for bout** (32/32 to four decimals, `probe_refund_check.txt`).
   - At the same season its simulated shift − base reproduces the observed paired contrast, **−0.450 against
     −0.458, per-seed r +0.80**.

**The spread of predictions for the paired recovery contrast** (observed −0.458 [−0.596, −0.320]):

| unchanged-gait prediction | predicted | residual (observed − predicted) | per-seed r with observed |
|---|---|---|---|
| solo probe, halved for groups (PREREGISTRATION §10's own discount) | −0.163 | −0.296 [−0.511, −0.080], 2/10 positive | −0.04 |
| **solo probe as `arith.py` uses it** | −0.325 | −0.133 [−0.486, +0.219], 6/10 | −0.04 |
| **arena Z10**, onset population, [T, T+10) | **−0.630** [−0.759, −0.501] | **+0.172 [+0.055, +0.289], 8/10** | **+0.62** |
| arena Z, season T only | −0.701 [−0.982, −0.421] | +0.243 [−0.007, +0.493], 7/10 | +0.46 |
| simulated, onset population (C0), flat − random | −0.806 [−0.934, −0.678] | — | — |
| **simulated at T+110**, the baseline's own gaits then (the refund) | **−0.721 [−0.885, −0.558]** | **+0.272 [+0.053, +0.491], 8/10** (the response) | — |

- **The residual's sign depends on the predictor**, from −0.30 to +0.27.
- **The only predictors made in the axis's own setting are the arena's.** They also predict per seed (r +0.62).
  Every one of them over-predicts the effect.

**The same season, separated** (`probe_refund.txt`, T + 110, mid-recovery). R-shift splits exactly into:
- **REFUND** = gain(base population, flat) − gain(base population, random), what open ground pays the baseline's
  own gaits then;
- **RESPONSE** = gain(shift population, flat) − gain(base population, flat).

| | REFUND | RESPONSE (both on flat) | response on random ground | total (simulated R-shift) | observed R-shift |
|---|---|---|---|---|---|
| co-evolved | +0.222 [+0.162, +0.283] 10/10 | +0.050 [−0.127, +0.227] 7/10 | +0.074 [−0.123, +0.271] | +0.272 | +0.177 |
| designed | +0.944 [+0.815, +1.072] 10/10 | **−0.222 [−0.445, +0.002] 2/10** | **−0.174 [−0.312, −0.036] 1/10** | +0.722 | +0.635 |
| **paired** | **−0.721 [−0.885, −0.558] 0/10** | **+0.272 [+0.053, +0.491] 8/10** | | −0.450 | −0.458 |

**What the data attribute:**
- **All of the class-C flip, and more, to the furniture.**
  - At an unchanged gait, open ground pays the wheels +0.94 a season against +0.14–0.22 for the co-evolved gaits.
    That is **4–7×**, not "about twice" (§4, §9, and the ticket's "2:1").
  - Unchanged gaits alone would have turned the +0.158 pre-onset lead into a deficit on **10/10** seeds.
  - §9's "the lead … was partly bought by the clutter" should read "**wholly**, and more".
- **The part beyond the arithmetic favours the co-evolved body.** It resolves on the arena's predictor (+0.17,
  8/10) and on the same-season split (+0.27, 8/10).
  - It is carried by the designed side. Its population after the onset forages **worse** than the baseline's
    contemporaneous population, on flat ground (−0.22, 2/10) and on random ground too (−0.17, 1/10). So its gait
    got worse generally, not worse at one terrain.
  - The designed body kept about two thirds of its refund: +0.635 observed, or +0.669 on the per-season gain,
    against +0.94.
  - The co-evolved body's response is unresolved (+0.05).
  - The time course (`probe_arena.txt` TC) agrees. Designed shift − base per-season gain slides from +0.77 in the
    first ten seasons to +0.60–0.66 by T+140–199. Co-evolved rises from +0.12–0.17 to +0.17–0.24. Newborn designed
    robots gain less than the old ones in the same seasons.
- **What the data do not attribute:** anything to a better response by the designed fauna. The report's sentences
  are silent on direction ("no response … beyond the arithmetic is shown"), and they rest on a predictor whose
  residual interval is ±0.35 wide. The better predictor narrows it to ±0.12 and moves it to the other side of 0.
- **The mechanism of the designed decline is not measured here**, and I do not claim one. It could be relaxed
  selection on an easy income, drift, or crowding effects of a richer arena. It is a fact about the designed
  population after T, and it is post hoc (my predictor, chosen after the arms). It should be labelled that way.

**Required:** replace §4's table and bullets, the headline paragraph and caveat 7, §9's arithmetic, and the ticket's
lesson-3 paragraph. I propose:

> On open ground both bodies earned more. Measured in the ecology's own arena, the furniture's arithmetic (unchanged
> gaits, four to a group, flat against random ground) pays the wheeled designed body about +0.94 a season and the
> co-evolved gaits +0.14 to +0.22. It predicts a paired contrast of −0.63 to −0.81, more than the observed −0.458
> [−0.596, −0.320]. So the falsifier fires wholly by the arithmetic of the furniture. The pre-onset lead was the
> clutter's tax on wheels. Beyond the arithmetic the contrast moved back toward the co-evolved body, by +0.17
> [+0.06, +0.29] (arena predictor) or +0.27 [+0.05, +0.49] (same-season split), 8/10 each (post hoc, adversary's
> predictor). The designed population born after the shift foraged worse than the baseline's contemporaneous
> population on both terrains. The data attribute the class to the furniture, not to any body adapting, and the
> non-arithmetic part runs against the designed body. The pre-registered solo-best probe (committed before the
> arms) predicted the direction. It under-predicted the wheels' refund in the arena (+0.57 against +0.79) and did
> not predict per seed (r −0.04).

- Carry the solo probe's own line as the pre-registered prior, beside the arena's.
- **Delete** "the designed body gains about what its unchanged best gains alone (1.11×)", "per seed the probe
  predicts nothing … a response of up to ±0.35 … would not be visible", and "about twice the tax".
- **For RBT-107:** the designed fauna's gait deteriorated after T. A deeper window on C4 should expect the paired
  contrast to keep moving toward the co-evolved body (tail −0.42, the TC bins to −0.37). Its re-wiring question
  sits beside a designed population that is changing in income, not only in wiring.

### F3 CAVEAT: class C is robust at "margin 1"; the report overstates its fragility and uses the wrong A/A figure

Evidence: `probe_readout.txt` P2 and P4.

- **The sign-guard margin is computed correctly**: 9/10 negative against ⌈0.8·10⌉ = 8. But margin 1 means **one**
  seed may flip and C still holds; it takes two.
  - Flipping the least-negative seed (2) gives 8/10 → **C**. Flipping two (2 and 7) gives 7/10 → F.
- **Leave one seed out: C on 10/10 drops** (n = 9, guard 8/9, |m|/r 1.55–2.36).
- **The window: C on every 100-season window** from [T, T+100) to [T+100, T+200), and on the transient
  (8/10) and the tail (9/10). The paired contrast is −0.40 / −0.46 / −0.42 across transient, recovery and tail.
- **Jitter illustration** (RBT-92 F6's method, not a test): with each seed jittered by N(0, s), C is returned on
  99.9% of draws at s = 0.077, **98.4% at s = 0.108** (the paired A/A-like RMS) and 93.5% at s = 0.15.
- **Required:**
  - Strike or soften "a replicate could plausibly return F through the sign guard, as RBT-92's could". RBT-92 sat at
    margin 0 and returned F on 9–20% of jitters; this one returns F on about 2% at the A/A scale.
  - **The A/A comparison for seed 2 uses the wrong reference.** "1.4× the A/A-like RMS (0.077)" divides by
    `placebo.py`'s **per-fauna** RMS of R-cull20. The class is read on the **paired** level R-body. Its A/A-like
    per-seed RMS is 0.108 (cull20 − base) to 0.123 (the four real culls). Seed 2's −0.104 is **0.84–0.97×** that,
    so it is the one seed within A/A noise of 0. Say so; the class does not depend on it (flip 1 above).
- **Unregistered, for the reader:** F2's arena arithmetic says an *unchanged* population would also have returned
  C (base R-body + the arena's zero-response paired contrast is negative on 10/10 seeds). So the class is robust
  because the arithmetic is large. It is not robust because of anything either body did after T.

### F4 CAVEAT: the falsifier's wording, and "wins"

- The pre-registration's wording is carried verbatim: "the designed body wins after the shift" (`PREREGISTRATION.md`
  summary table and §11, which is RBT-92's).
- **That is not the owner's sentence.** `docs/held-out-challenges.md` §9 gives it verbatim as "the designed body wins
  on the held-out challenge", and §11 of the pre-registration adds "for C4 … 'the designed body wins on open
  ground'". The report calls RBT-92's paraphrase the owner's words. It should quote §9 verbatim beside the
  registered label.
- **"Wins" is not over-claimed as a level.** The designed body earns more on open ground, −0.310, 9/10, and the
  report says in the same breath that the co-evolved body gained. Keep the "gained less, did not lose" sentence
  wherever "wins" appears, including the ticket summary, which does.
- **§9's "the co-evolved body's income lead … was partly bought by the clutter" understates the arithmetic.** In the
  arena (F2), unchanged gaits on flat ground reverse the pre-onset lead on 10/10 seeds. The data say the **whole**
  lead, and more, was the clutter's tax on wheels at onset.

### F5 CAVEAT: the registered null is empty here; −0.472 is −0.458 re-read, and the headline should say so

Evidence: `probe_readout.txt` P3.

- **k = max(0, excess deaths), and a boon lowers deaths.** Designed excess deaths over [T, T+10) are negative on
  7/10 seeds (to −11). The null is one-sided by construction and has nothing to match on 6/10 seeds (k = 0/0). On
  the other four, k totals 1–3 robots.
- **Event − null equals event − base on 6/10 seeds**, and the two per-seed vectors correlate at +0.91.
- **Matched-null power:**
  - **Absorption.** Scaled linearly from cull20 (paired R-body RMS 0.108 for 40 culled), a cull of the realised
    k (0.9 robots per seed on average) could move paired R-body by about **0.002 per seed, 0.5% of the event**.
    The realised 1–3-robot culls actually moved it by RMS 0.078 (17%), which is noise, not a matched effect.
  - **Sensitivity.** Event − null has sd 0.158 and half-width 0.113. Its minimum detectable effect (5% two-sided,
    power 0.8, t(9)) is **0.157**, and −0.472 is **3.0×** that.
  - So the null test has power, but only against a null that is the baseline itself. **It is not an independent test
    of turnover.**
- **Required:** the headline's "Against the registered random-cull null it is −0.472 [−0.585, −0.359]" must carry
  "(≡ event − base on the six k = 0/0 seeds; the null could absorb ~0.5% of the event)". Otherwise it reads as a
  second line of evidence. §3's table already says it; the headline and the ticket summary do not.
- The turnover guard's "no" is on n = 3. The report says so; the ticket summary should too.
- **cull20 is the turnover reference that carries a turnover**: paired R-body +0.043 [−0.031, +0.118]. The report's
  use of it is right.

### F6 CAVEAT: A/A; the conditional wording can go on the paired contrast, but not for the reason given

Evidence: `probe_readout.txt` P4.

**A/A-like per-seed RMS on the paired R-body:**

| source | RMS |
|---|---|
| cull20 − base | 0.108 |
| the four real 1–3-robot culls | 0.123 |
| per fauna, cull20 (placebo.py's figure) | 0.077 |

**The −0.458:**
- It is **3.7×** a single seed's paired A/A RMS, and **12 SE** of a ten-seed A/A mean (SE 0.039).
- Its smallest per-seed value, −0.122, is 1.0× the RMS.
- For RBT-105 to reach it, the paired per-seed spread would have to be about 0.64, against an observed between-seed
  sd of 0.193 that already contains run-to-run noise (RBT-92 F5).
- **Drop the A/A condition from the paired contrast.**

**The co-evolved gain's lower bound (+0.076):**
- The report calls it "at the A/A-like per-seed RMS" and marks it A/A-conditional. That compares an interval
  bound on a mean with a per-seed spread.
- The ten-seed mean's A/A SE is 0.077/√10 = 0.024, so +0.177 is about 7 SE.
- The between-seed t interval already contains the noise. The conditional can go. If RBT-105's holistic per-seed
  RMS comes in above about 0.25, revisit.

**The designer's residual, −0.133:**
- It is **not "inside" A/A**. It is 1.1× one seed's RMS and 3.4 SE of an A/A mean.
- Its interval, ±0.35, comes from the solo probe's per-seed misfit (sd 0.49), not from A/A noise.
- The question "is −0.133 far enough inside an A/A spread?" therefore has no answer. F2 replaces the residual.

**The arena residual (F2), +0.172:**
- Per-seed sd 0.164, half-width 0.117.
- It is 4.4 SE of an A/A mean. It is resolved on the between-seed interval, which already contains that noise.

### F7 CAVEAT: re-wiring; the verdict and its power figures check out, and one line should come out

Evidence: `rewire.txt`, `control360.txt`, `probe_rederive.txt` §2, `probe_bulk.txt`.

**Checked:**
- `CONTROL-FAUNA n=10` PASS for both faunas.
- Smallest f detected on ≥ 0.8 of replicates at w = 1.0: **0.5 holistic, 0.2 designed**. That is exactly the
  report's "blind below".
- The same thresholds hold at w = 0.5: detection 0.810 at f = 0.5 holistic, and 0.995 at f = 0.2 designed.
- False positives of the full rule ≤ 1/400 holistic and 0/400 designed at n = 10.
- Depth, shift − base: +0.09 [−0.03, +0.21] holistic and −0.07 designed. Both are under the 0.5-event caveat
  bar, as reported.
- **The base `wiring.txt` for all ten seeds regenerates byte for byte from the 600/600 `ckpt/rbt-90-SEED` bulk
  (README rule 6).** So do the shift arms' `wiring.txt` on the eight checkpoints at 600/600.

**The wording holds.**
- Every verdict line carries "blind below f ≈ …", and no bare NO CHANGE SEEN appears in the report or the ticket.
- §9's "Nothing was re-wired that the positive control could have seen" is the right sentence.

**Two refinements:**
1. **f is a fraction of *installable* survivors whose sensor count did not grow**, not of survivors. Holistic
   installable is 540/600, and 159/600 holistic survivors carry a grown sensor count and cannot score
   `new_existing`. "Blind below about half of the survivors" should read "half of the installable survivors".
2. **The T + 199 line should not be carried "for RBT-107".**
   - `rewire.txt` prints, per fauna, 13 statistics × 4 contrasts × 3 read points: 156 intervals.
   - One of them, designed new_existing shift − cull20 at T + 199, ending at −0.0001, is what chance gives at
     that count.
   - It is unregistered as a read point for a verdict. Reporting it as "at the edge of FEWER NEW LINKS" for RBT-107
     is the one place the report reads a number it has not validated.
   - Either drop it or label it "one of 156 printed intervals; not a finding".

**My perturbation reaches the scored statistic.** The designer's round-trip wiring perturbation moved only
unscored W-acq lines. I set a designed T+160 survivor's g1 in `shift-1/wiring.txt` to 5 above its ancestors. That
moves seed 1's `new_existing` 0.233 → 0.250 and the designed shift − base line +0.0117 → +0.0133 (16 lines). The
scored statistic is derived from the table, not replayed.

### F8 CAVEAT: scoring; two banked "rights" are lesson 4's artifacts

Evidence: `probe_readout.txt` P5.

- **The arithmetic is right.** The Brier over the 8 listed binary predictions is 0.1278.
- **Two of the eight are the recovery-time predictions**, scored "right, as registered".
  - The designed "none on ≥ 5/10" can only be right for a boon: the paired rule is sign-blind, and an income that
    rises never re-enters the band.
  - The co-evolved "≤ 60 on ≥ 6/10" counts **4 d = 0 artifacts** among the 6, which the report itself says.
- **Lesson 4 says no recovery claim.** The rule was RBT-92 F11's: an uninformative "right" is not banked.
  **Required:** mark both "not scored (lesson 4)" and give the Brier on the six remaining, **0.087**. It happens to
  improve the score; the point is that it is not scored on artifacts.
- The class prediction: C held 0.30. The multi-class Brier is 0.678 against 0.857 for a uniform guess over seven
  classes. That is fair to print.
- **"What I got wrong"** should add F2's fact: the arena did not halve the designed body's solo gain, it raised it
  (+0.79 against +0.57). The pre-registered discount was wrong in direction for the wheels, and right in direction
  for the co-evolved body (+0.16 against +0.25).
- **Lessons 5 and 6 are observed.**
  - Alive is 60 in every season of [T−100, T+200) in every arm, seed and fauna (min 60, max 60).
  - The minimum transient income is 0.974 against D/E's 0.25.
  - L is "not scored (UNVALIDATED, V3)" in §1 and in the table.

### F9 NONE: lesson 1 and RBT-99's placebo method

- `placebo.txt` P3 is RBT-99's method on C4's paths, and I re-derived it byte for byte.
- A on the base arm's before, recovery and tail windows, and on 23/25 placebo onsets. That is RBT-92's result by
  construction, since the base and T are RBT-92's.
- The C on the shift arm is the event's. The report says so, and adds that the flip is the arithmetic's size.
  With F2 that becomes "and more than the arithmetic needs".

---
_Generated by [Claude Code](https://claude.ai/code)_
