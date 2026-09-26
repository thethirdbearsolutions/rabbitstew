# RBT-92 report: the first epoch, crowding (group size 4 → 8) on ten founding populations

**Verdict (RBT-89 §9, as pre-registered): class A, co-evolved wins.** R-body in the recovery window of the
shift arm is **+0.180** (95% t(9) [+0.077, +0.284]), positive on **8/10** seeds, against a resolvable r =
**0.104**. The falsifier, **"the designed body wins after the shift"**, is not met (class C needs mean ≤ −0.10).

**What class A certifies here** (amended after the readout adversary, PR #183; coordinator ruling 18:45):

> Under crowding the co-evolved body kept the income lead it already had over the designed body: +0.18
> [+0.08, +0.28] with the shift and +0.15 [+0.05, +0.25] without it, on the same seeds and windows. The
> pre-registered rule scores this class A. The same rule returns A on the no-event baseline, so it certifies that
> the lead persisted, not that the co-evolved body withstood crowding better. Crowding's differential effect on
> the two bodies is +0.03 [−0.04, +0.10]. That is unresolved, and it is the size of what a random cull of a third
> of each fauna does (+0.04). Neither body's income fell by more than r.

- **The rule measures the lead's level, not robustness to the shift.** Applied with no shift at all, it returns
  class A on the no-event baseline's recovery window, and on **23/25** placebo onsets of the baseline alone
  (adversary F2, `readout-adversary/probe_readout.txt` P3).
- **"Holds up" is met by both bodies.** The bar is R-shift ≥ −r = −0.104. Co-evolved R-shift is −0.020
  [−0.073, +0.034] and designed is −0.052 [−0.091, −0.013], so both clear it even at the interval's lower end.
  "Holds up" therefore does not tell the two bodies apart.
- **"Survives" carries no information in this ecology.** Alive is 60 in every season of [T − 100, T + 200) in all
  37 runs. The minimum window income is 0.69, against the 0.25 basal bar. Neither body could have failed to
  survive.
- **The designed body's crowding cost** is −0.052 [−0.091, −0.013] against the no-event control. Against the
  pre-registered random-cull null it is **−0.037 [−0.081, +0.006], which does not resolve**. The co-evolved
  body's cost is −0.020 [−0.073, +0.034] against the control.

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
  - **That fix repairs only the manipulation half** (adversary F8). A random cull's effect on L is not guaranteed to
    be negative, because refill births go to C0's survivors. L needs an effect it must register, such as a cull of
    whole lineages.

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
- **The designed body's cost is printed against both references** (adversary F3):
  - against the no-event control: −0.052 [−0.091, −0.013] in the recovery window;
  - against the pre-registered null, the random cull of the same size: **−0.037 [−0.081, +0.006], which does not
    resolve**.
  - Random culls of 1–10 designed robots themselves lower designed income, by amounts of the order of −0.05 (R-cull
    per seed +0.155, −0.065, −0.122, −0.096, −0.016). So no statement is made that crowding resolvably cost the
    designed body.
- The co-evolved body's cost resolves against neither reference. That is the opposite of my prediction (§6),
  though the difference between the two bodies does not resolve either.
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

- **No recovery claim is made** (adversary F4; coordinator ruling).
  - d = 0 records "had not yet diverged", not "recovered". `mean_lifetime_score` is a lifetime mean, so the paired
    difference starts at 0 at T and grows slowly (lag-1 autocorrelation 0.69).
  - The rule accepts the first 20-season run inside h, so it returns d = 0 whenever divergence takes more than 20
    seasons to reach h.
  - In fact **every shift seed leaves the band**, on both faunas. On the six d = 0 seeds the co-evolved shift arm
    first leaves it between T+21 and T+133, and stays out for 1 to 81 of the 160 seasons.
  - The count of d = 0 seeds depends on h: 0/10 at 0.5 SD, 1/10 at 1 SD, 4/10 at 1.5 SD, 6/10 at the registered
    2 SD.
  - The numbers above stay printed, as registered, and are not read.
- **The P-form** (against the pre-event plateau; secondary) has its floor printed: the base's own d is 0 on
  5/10 seeds, holistic.

## 5. Readings owed by the pre-registration

- **The claim line (RBT-89 §2, C1):** "under a shift both bodies survive, does the co-evolved body out-earn the
  designed one, draw, or lose." Both survive on 10/10 seeds, at alive = 60 throughout, though survival could not
  have failed here. The co-evolved body out-earns the designed one by the rule, **class A**, and it out-earned it
  by the same rule without the shift.
- **"Robust" means survivorship of standing morphology and gait**, not adaptation (§3, RBT-91 option A).
  - Depth inside the transient and recovery windows is about 5 reproduction events (`baseline_depth.txt`,
    median 5.0).
  - The shift left no resolvable mark on co-evolved income.
  - So the sentence is the one at the head of this report: **the co-evolved body kept the lead it already had**.
    It is not "withstood crowding better", and it is not "re-adapts".
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
  - Neither founding half carries the verdict alone. The 0.011 split is a tenth of one seed's A/A-like
    difference (adversary F5), and **no per-seed value in this table can be read alone**.

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
| designed survives on 10/10 (0.85) | 10/10 | right, but uninformative in this ecology (alive pinned at 60) |
| K1 median 6, K1 ≤ 10 on ≥ 8/10 (0.6) | median 0; ≤ 10 on 10/10 | median wrong, clause right |
| K2 median 3 | median 0.5 | wrong |
| \|holistic R-null\| > r and close to R-shift (0.6), on k > 0 seeds | −0.051, below r | **wrong** |
| recovery, paired: shift holistic "none" on ≥ 7/10 (0.6) | none on 0/10 | **wrong** by the rule's letter; the rule could not return "none" for a slow divergence (F4) |
| recovery, paired: shift designed ≤ 60 on ≥ 6/10 (0.5) | 9/10 | right |
| recovery, paired: culls ≤ 20 on ≥ 8/10, both faunas (0.6) | cull 10/10 and 8/10; cull20 5/10 holistic, 8/10 designed | **wrong** (cull20 holistic) |
| L(T+160) shift − cull within ±0.10 (0.55) | (not read) | **not scored** (UNVALIDATED, V3) |
| class D not met (0.9) | 0/10 | right, but uninformative (minimum income 0.69 against 0.25) |

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
8. **F5, A/A-like spread:** the per-seed spread of shift − base R-body (RMS 0.102) equals that of a random cull
   (0.108–0.113). The +0.032 differential is a third of one seed's A/A-like difference. The between-seed intervals
   stand, but no per-seed value is read alone. RBT-105's A/A spread is a post-hoc check on this, not a gate.
9. **F6, the sign guard is met with zero margin:** 8/10 positive against ⌈0.8n⌉ = 8, and the smallest positive seed
   (804, +0.091) is below the per-seed A/A-like RMS. A replicate of the shift arms would plausibly return F through
   the sign guard (roughly 1 in 10 to 1 in 5), not through the mean.
10. **F7, the turnover guard is scored on n = 4** (seeds with co-evolved k > 0). At n = 4 its t(3) half-width is
    about 1.5 × r, so its "YES" is not evidence of equivalence. The differential's equivalence form is
    |0.032| + 0.073 = 0.105, not < 0.10, so neither an effect of crowding on the contrast nor its absence is shown.
11. **F8, carriage:** the V3 fix proposed in §1 repairs only its manipulation half. L's own validation needs an
    effect L must register. No L number is scored anywhere in this report.
12. **These are this head's founding populations.** None replicates RBT-28's, RBT-71's or RBT-84's. There is one
   economy and one challenge.

## 8. What this decides

The first held-out challenge the programme has run on ten founding populations is crowding. **Under it the
co-evolved body kept the income lead it already had** over the designed body: +0.15 without the shift and +0.18
with it. Crowding's differential effect on the two bodies, +0.03 [−0.04, +0.10], does not resolve. Neither body's
income fell by more than r, and nothing starved, but survival could not have failed in this ecology.

**The falsifier, "the designed body wins after the shift", is not met.** What the result does not show is that
the co-evolved body withstands crowding better than the designed one. The pre-registered rule certifies that the
lead persisted, and it would have said the same with no shift at all. The honest boundary: this challenge was mild,
the random-cull null could not test turnover, and the sign guard was met with no margin.

**For the next epoch:**
- The class rule needs a paired form (shift − base) if it is to measure robustness to a challenge rather than the
  lead's level.
- The recovery-time rule needs a hold that cannot be met before divergence has had time to show.
- V3 needs a manipulation read in `deaths` and an L check against an effect L must register.
