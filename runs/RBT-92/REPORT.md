# RBT-92 report: the first epoch, crowding (group size 4 → 8) on ten founding populations

**Verdict (RBT-89 §9, as pre-registered): class A, co-evolved wins.** R-body in the recovery window of the
shift arm is **+0.180** (95% t(9) [+0.077, +0.284]). It is positive on **8/10** seeds, against a
resolvable r = **0.104**. The co-evolved body **holds up**: its own R-shift is −0.020, against the bar −r.
The falsifier, **"the designed body wins after the shift"**, is not met (class C needs mean ≤ −0.10).

**What the verdict does and does not say.**
- **The co-evolved lead was already there, and the shift did not move it.** The no-event baseline has R-body
  **+0.148** [+0.051, +0.245] in the same window.
- The shift arm exceeds its own control by only **+0.032** [−0.041, +0.105]. That figure is holistic R-shift
  minus designed R-shift, per seed.
- Crowding cost the designed body a little and resolvably: R-shift **−0.052** [−0.091, −0.013].
- It cost the co-evolved body nothing resolvable: **−0.020** [−0.073, +0.034].
- So class A here reads: *under crowding the co-evolved body kept the lead it had before it*. It does not read
  *crowding favoured the co-evolved body*, and it does not read *the co-evolved body re-adapted*.
- Nothing died of the shift. Both faunas sat at alive = 60 in every season of every arm and window.

Everything below re-derives from `runs/RBT-92/readout.txt`. That file is written by `readout.py` from
committed tables alone.

## Provenance

| what | where |
|---|---|
| pre-registration | `runs/RBT-92/PREREGISTRATION.md`, as amended 1–4 before any arm existed (posted on RBT-92 12:42; amendments 12:58, 13:3x, 14:30, 15:16 UTC) |
| seed rule | `SEED-RULE.md`, commit `66f5ab3`, 12:26 UTC, before any RBT-90 output was read: all ten, 10/10 read |
| onsets | `onset.txt` (`7455b29`), reproduced byte for byte by the adversary; T = 352–382 |
| baselines | the ten RBT-90 part 2 arms, `runs/RBT-90/forage-SEED/` |
| arms | 27 arms run by the hive at integration `852dcac`+ (roster `runs/HIVE-0926/roster.txt`): 10 shift, 10 cull20, and 7 cull; seeds 7, 805 and 806 have k = 0/0, so their null is the baseline itself |
| readout | `readout.txt`, on `results/RBT-92-design` merged with integration `47210f1` |
| round trip | a worktree of the readout commit holding no bulk: `readout.py` output is **byte-identical** to `readout.txt`. Perturbing one cell (`shift-3/seasons.txt`, season 450, holistic income +0.5) moves r (0.1037 → 0.1038) and seed 3's recovery R-body (+0.1958 → +0.2008) |
| tests | `python -m pytest -q`: 284 passed on the design head |

## 1. Validation, read first (V0–V3)

- **V0, V1 and V2 pass on 10/10 seeds.**
  - **V0:** every arm is identical to its baseline before T. That holds for every `seasons.txt` row, and for
    every `lineage-last.txt` row of an individual that died before T.
  - **V1:** the culls are exactly as stated.
  - **V2:** the tracer's alive count equals the table's.
- **V3 FAILS, and the failure is in my design, not in the runs.**
  - **The alive-dip half cannot see the cull.** The cull removes 20 of each fauna at the top of season T. The
    freed slots refill by breeding within that same season, and `seasons.txt` records alive at season end. So
    alive_cull20 − alive_base over [T, T+10) is **0 on 10/10** seeds, for both faunas.
  - The cull did happen. V1 counts it, and deaths over [T, T+10) in cull20 exceed the base by 18–43 per fauna.
    But I chose a column that cannot show it. The table sees the cull only in `deaths`.
  - **The L half does not resolve either.** Holistic L(T+60), cull20 − base, is −0.042 [−0.106, +0.022],
    negative on 8/10. The conventional side does resolve: Lc −0.057 [−0.101, −0.013].
- **Consequence, as pre-registered:** the carriage readouts print as **UNVALIDATED** and enter no sentence of
  this report beyond this one.
  - For the record, every L difference is within ±0.06. Two intervals exclude 0: Lc cull20 − base at T+60
    (−0.057 [−0.101, −0.013]) and L shift − cull at T+199 (+0.038 [+0.002, +0.074]).
  - I do not read any of them.
  - The fix, for the next epoch, is to read the cull's footprint in `deaths` and in the onset cohort. I am not
    applying it after the fact.

## 2. The co-evolved against designed contrast, before, at and after

R-body is holistic − designed `mean_lifetime_score`, as a window mean. The table gives the mean over 10 seeds,
with its 95% t(9) interval and the positive count.

| arm | before [T−100, T) | transient [T, T+60) | **recovery [T+60, T+160)** | tail [T+160, T+200) |
|---|---|---|---|---|
| base | +0.158 [+0.080, +0.236] 9/10 | +0.169 [+0.055, +0.283] 8/10 | +0.148 [+0.051, +0.245] 9/10 | +0.106 [+0.016, +0.196] 8/10 |
| **shift** | +0.158 (identical by V0) | +0.163 [+0.031, +0.295] 9/10 | **+0.180 [+0.077, +0.284] 8/10** | +0.201 [+0.081, +0.322] 9/10 |
| cull | +0.158 | +0.177 [+0.046, +0.307] 8/10 | +0.158 [+0.023, +0.294] 7/10 | +0.185 [+0.038, +0.332] 8/10 |
| cull20 | +0.158 | +0.205 [+0.055, +0.355] 8/10 | +0.191 [+0.084, +0.299] 8/10 | +0.194 [+0.063, +0.326] 8/10 |

**Power** (RBT-89 §7's line, printed by the readout):
- The per-seed spread of recovery R-body is sd 0.145, which gives **r = 0.104** at t(9). This is wider than the
  pre-registered expectation of 0.077, which came from RBT-89's SD of 0.108.
- The season-noise figure is 0.007. It understates, because it ignores the 60-season wave.
- r ≤ 0.10 is not met, so class B was not reachable at the realised spread. A mean inside ±0.10 would have read
  F, not B.
- The equivalence form |mean| + r = 0.284 is far from < 0.10.

## 3. What the shift did to each body (R-shift = shift − base, paired per season)

| fauna | transient | recovery | tail |
|---|---|---|---|
| co-evolved | −0.057 [−0.126, +0.013] 2/10 positive | **−0.020 [−0.073, +0.034]** 2/10 | +0.014 [−0.066, +0.094] 7/10 |
| designed | −0.050 [−0.090, −0.011] 3/10 | **−0.052 [−0.091, −0.013]** 3/10 | −0.082 [−0.136, −0.027] 2/10 |

- **Crowding is a small income cost in this economy:** a few hundredths of an item per robot per season on
  either body.
- It resolves on the designed body in every window, and on the co-evolved body in none.
- That is the opposite of my prediction (§6).
- The difference, holistic − designed R-shift in the recovery window, is +0.032 [−0.041, +0.105], positive on
  6/10. It does not resolve.

**The null.**
- **k, the excess deaths in [T, T+10), is tiny**, as the adversary's F6 warned. The co-evolved k is 1, 1, 0, 0,
  0, 2, 0, 0, 3, 0; the designed k is 0, 10, 0, 0, 3, 0, 2, 6, 1, 0.
- **Seeds 7, 805 and 806 have k = 0/0.** Their null is the baseline itself, so R-null = R-shift there by
  construction.
- **The turnover guard is scored on the 4/10 seeds with co-evolved k > 0** (801, 804, 1, 4). There the
  co-evolved R-null is −0.051, and |R-null| < r. So on those seeds the shift did to co-evolved income no more
  than a random cull of 1–3 robots. With the shift's own co-evolved effect unresolved, this says the null and
  the event were both small; it is not evidence of equivalence.
- **The turnover reference is cull20** (F6), a cull of a third of each fauna.
  - Co-evolved R-cull20 in the recovery window is +0.047 [−0.016, +0.110].
  - Designed R-cull20 in the recovery window is +0.004 [−0.035, +0.042].
  - A same-size random cull moves recovery income by less than r on both faunas, in either direction.

## 4. Recovery time

**The primary form is paired against the control.** Recovery means the first d from which |x_shift − x_base|
stays within h for 20 seasons.

| arm | co-evolved | designed |
|---|---|---|
| shift | recovered within 180 on **10/10**; per seed 71, 44, 52, 0, 0, 0, 0, 114, 0, 0; median 0 | 10/10; 21, 98, 0, 5, 0, 52, 0, 0, 0, 0 |
| cull | 10/10; one seed at 20, the rest 0 | 9/10; one "none" (804), one 31 |
| cull20 | 9/10; median 15; one "none" (2) | 10/10; median 2.5 |

- On six of ten seeds the co-evolved shift arm never left the control's band.
- On four (801, 804, 805, 3) it left the band and came back, within 44–114 seasons.
- **The P-form** (against the pre-event plateau; secondary) has its floor printed: the base's own d is 0 on
  5/10 seeds, holistic.

## 5. Readings owed by the pre-registration

- **The claim line (RBT-89 §2, C1):** "under a shift both bodies survive, does the co-evolved body out-earn the
  designed one, draw, or lose." Both survive on 10/10 seeds, at alive = 60 throughout. The co-evolved body
  out-earns the designed one by the rule, **class A**.
- **"Robust" means survivorship of standing morphology and gait**, not adaptation (§3, RBT-91 option A).
  - Depth inside the transient and recovery windows is about 5 reproduction events (`baseline_depth.txt`,
    median 5.0).
  - The shift left no resolvable mark on co-evolved income.
  - So the sentence is **"the co-evolved body survives the shift and keeps its lead"**. It is not "re-adapts".
  - No carriage claim is made, because V3 failed.
- **Class D and E tests:** 0/10 seeds each. E1 (both bankrupt), D (designed bankrupt) and E2 (co-evolved
  bankrupt) are all 0/10.
- **Forbidden readings, §14:**
  - The class is read on the recovery window, not the transient.
  - The bests' reversal is not R-body.
  - Nothing here is a champion reading.
- **Remainder groups (F5):** on every seed both faunas stayed at 60. From T on each fauna had seven groups of
  8 and one of 4: 240/3600 robot-seasons in the small group in the transient, 400/6000 in recovery, and a mean
  group size of 7.73. That is **identical on both faunas and on every seed**, so the between-fauna confound is
  0 and the treatment is diluted by 6.7% on both sides.
- **Seed 806 carries the drift flag.** Its baseline deaths over [T, T+10) were 54, against 1.5 × 34.3. Its
  recovery R-body is −0.014. Its transient is read with the flag beside it; it is not dropped.
- **By founding population (Amendment 4; descriptive, no test):**
  - The oscillator-discarding seeds (801, 804, 805, 1, 7) have mean recovery R-body +0.175.
  - The oscillator-acquiring seeds (806, 807, 2, 3, 4) have +0.186.
  - Neither founding half carries the verdict alone.

  | seed | T | R-body recovery, shift | R-body recovery, base | oscillator (part 2) | effector drive (part 2) |
  |---|---|---|---|---|---|
  | 801 | 361 | −0.093 | +0.019 | discarded | effector |
  | 804 | 358 | +0.092 | +0.113 | discarded | effector |
  | 805 | 359 | +0.200 | +0.209 | discarded | unresolved |
  | 806 | 365 | −0.014 | −0.042 | acquired | undecided |
  | 807 | 360 | +0.196 | +0.094 | acquired | unresolved |
  | 1 | 382 | +0.341 | +0.407 | discarded | effector |
  | 2 | 382 | +0.277 | +0.018 | acquired | undecided |
  | 3 | 352 | +0.196 | +0.161 | acquired | effector |
  | 4 | 355 | +0.277 | +0.241 | acquired | unresolved |
  | 7 | 354 | +0.333 | +0.261 | discarded | effector |

## 6. My predictions, scored as mine

| prediction (confidence) | outcome | scored |
|---|---|---|
| class B, draw (0.45); A 0.15 | **A** | **wrong** |
| R-body before +0.12 | +0.158 | within its spread, high |
| R-body transient +0.02 | +0.163 | **wrong** |
| R-body recovery +0.03, per-seed −0.15 to +0.20 | +0.180; per seed −0.093 to +0.341 (4 seeds above +0.20) | **wrong** |
| R-body tail +0.04 | +0.201 | **wrong** |
| holistic R-shift, recovery −0.20 (−0.35 to −0.05) | −0.020 | **wrong** |
| designed R-shift, recovery −0.08 (−0.20 to +0.05) | −0.052 | right |
| the shift costs the co-evolved body more than the designed one (0.55) | the other way on the means (+0.032 unresolved) | **wrong**. The secondary falsifier's rule (difference interval above 0) is not met. |
| designed survives on 10/10 (0.85) | 10/10 | right |
| K1 median 6, K1 ≤ 10 on ≥ 8/10 (0.6) | median 0; ≤ 10 on 10/10 | median wrong, clause right |
| K2 median 3 | median 0.5 | wrong |
| \|holistic R-null\| > r and close to R-shift (0.6), on k > 0 seeds | −0.051, below r | **wrong** |
| recovery, paired: shift holistic "none" on ≥ 7/10 (0.6) | none on 0/10 | **wrong** |
| recovery, paired: shift designed ≤ 60 on ≥ 6/10 (0.5) | 9/10 | right |
| recovery, paired: culls ≤ 20 on ≥ 8/10, both faunas (0.6) | cull 10/10 and 8/10; cull20 5/10 holistic, 8/10 designed | **wrong** (cull20 holistic) |
| L(T+160) shift − cull within ±0.10 (0.55) | +0.027 | right, but UNVALIDATED (V3) |
| class D not met (0.9) | 0/10 | right |

**The prediction that embarrasses me** is the mechanism.
- I reasoned that crowding halves the density a mower's yield rides on, so the cheap co-evolved mowers would
  lose most. They lost the least.
- Both populations stayed at capacity and nobody starved, so eight to an arena was a milder world than RBT-17's
  founders met from season 0.
- The pre-registration named the embarrassing case: an evolved gait carrying its lead into crowding, which is
  class A. That is what happened.

## 7. Caveats the report carries (adversary round 1 and the coordinator's rulings)

1. **V3 failed by design (§1), so carriage is unvalidated and unread.** The alive-dip test was blind at season
   resolution. That is my error, found only on the real arms.
2. **F2:** even where V3 passes, it is a manipulation check on the tracer, not a sensitivity test.
3. **F6:** the null is close to the control.
   - k = 0 on the co-evolved side for 6/10 seeds, and 0/0 on 7, 805 and 806.
   - The turnover guard stands on 4 seeds, and cull20 is the turnover reference.
   - F6's energy-buffer mechanism rests on one probe seed (9902).
4. **F10:** recovery is paired-primary. The P-form reads against its floor, which is d = 0 on 5/10 base seeds,
   holistic.
5. **Seed 806** carries the onset drift flag, and its wave window sits at the edge of the rule's range.
6. **The realised r (0.104) exceeds the pre-registered 0.077.** The seeds differ more than RBT-89's three did,
   so B could not have been returned. A is unaffected: |mean| = 0.180 ≥ r.
7. **The lead is pre-existing (base +0.148).** Class A as RBT-89 defines it is a statement about the shift arm's
   contrast, and the report does not credit the shift with it.
8. **These are this head's founding populations.** None replicates RBT-28's, RBT-71's or RBT-84's. There is one
   economy and one challenge.

## 8. What this decides

The first held-out challenge the programme has run on ten founding populations is crowding. It **does not
disturb the co-evolved body's income lead over the designed body**:
- the lead is +0.15 without the shift and +0.18 with it;
- the shift's cost is resolvable only on the designed body, and small there;
- nobody starved.

So on this challenge the owner's bet reads **"holds up"**, in the sense the protocol allows: survivorship of
standing morphology and gait, with the lead intact. **The falsifier is not met.** The honest boundary: this
challenge was mild, and at the predicted k the random-cull null could not test turnover.

The next epoch's first fix is V3. Read the cull's footprint in `deaths` and in the onset cohort, not in
end-of-season alive.
