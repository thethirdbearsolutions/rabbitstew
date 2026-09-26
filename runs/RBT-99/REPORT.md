# RBT-99 report: epoch C2, dearer work (work cost 0.03 → 0.08 per kJ) on ten founding populations

**Verdict (RBT-89 §9, as pre-registered): class A, co-evolved wins. The class carries no information about the
event.** The same rule returns A on the no-event base arm's own recovery window and on **23/25 placebo onsets** on
the baseline alone (`placebo.txt`, P3, the RBT-92 readout adversary's method; coordinator ruling 18:45). It reads the
level of the co-evolved lead, which is there before any shift. **The only readout of the event itself is the paired
event − base contrast against the random-cull null (§3).**
- R-body in the recovery window of the shift arm is **+0.519** (95% t(9) [+0.336, +0.702]), positive on
  **10/10** seeds, against a resolvable r = **0.183**. The sign guard needs 8/10, so the margin is 2 seeds.
- The falsifier, **"the designed body wins on the held-out challenge"**, is not met. Class C would need a mean
  ≤ −0.10, and E2 would need the co-evolved fauna bankrupt; it is bankrupt on 0/10 seeds.
- D's test fires on **4/10** seeds (806, 807, 2 and 3), below the 8/10 guard, so the class is A and not D.
- **The co-evolved body holds up by the registered line:** its R-shift is −0.055 [−0.123, +0.013], against the
  bar −r = −0.183. That interval spans 0, so this is an unresolved loss, not a demonstrated absence of one (see
  the A/A note below).

**What the event did. Per the protocol, a C2 result is one body's cheapness, not two bodies' contest.** Every figure
in this list is a paired contrast (`placebo.txt` P4, `score.txt`). The designed body's cost is given against both the
no-event control and the pre-registered null.
- **Most of the verdict is the designed body's collapse, not the co-evolved body's gain.**
  - The no-event baseline already carries R-body **+0.148** [+0.051, +0.245] in the same window.
  - The shift arm exceeds its own control by **+0.371** [+0.162, +0.581], positive on 10/10. That figure is
    co-evolved R-shift minus designed R-shift, per seed.
  - **Designed cost:** −0.426 [−0.621, −0.231] against the control (0/10 positive), and −0.388 [−0.575, −0.201]
    against the null (0/7 positive; n/a on the 3 seeds where the cull emptied the fauna). So the shift took far
    more from the designed body than either no event or a random cull did.
  - **Co-evolved cost:** −0.055 [−0.123, +0.013] against the control, which is unresolved. Against the null it is
    −0.074 [−0.117, −0.031], which resolves and is small: the shift cost the co-evolved body slightly more than a
    random cull of its first ten seasons' excess deaths (k = 0 to 20).
- **Designed turnover was 3.9 to 6.7 times its baseline's in the transient, on 10/10 seeds**, which the F6
  sentence rule requires here. The designed fauna **went extinct on 3/10 seeds** (806, 807, 2) and fell to 4 alive
  on a fourth (3). Extinct seasons count as 0 income (the 13:10 ruling), and that lifts R-body on those seeds.
- **On the 7 seeds where the designed fauna never reached 0,** the shift arm exceeds its control by **+0.205**
  [+0.114, +0.296], 7/7 positive (`score.txt`). The designed R-shift there is −0.262 [−0.323, −0.202], and the
  co-evolved R-shift is −0.057 [−0.148, +0.035]. So even where the comparator survived, the shift took more from
  it than from the co-evolved body.
- **Where the designed fauna survived, it survived by turnover, not unaffected.** In the recovery window its
  mean income is +0.53 to +0.72 on those seeds, while deaths ran 1.4 to 3.5 times the base's. That is the
  adversary's churn-at-capacity mechanism (F2). Its survivors' income is survival-conditioned (F6).
- **The co-evolved body paid about 80% of its price back.** The price by arithmetic is 0.05 × its
  pre-onset kJ, 0.135 to 0.394 per seed (`price.txt`). Its net, R-shift + price, is **+0.206** [+0.151, +0.262],
  positive on 10/10.
  - The committed tables cannot say whether that came from sorting on kJ or from survivor-conditioning of the
    lifetime mean. The report claims neither mechanism; the depth is about 5 events, so "is sorted" is the most
    the protocol allows.
  - A co-evolved "does not hold up" no larger than the price would have been the price. Here it held up anyway.

**What is not read.**
- **Survival.** Deaths are refilled within the season, so alive = 60 carries no information. The one survival fact
  that does carry information is the designed fauna's extinction on 3 seeds, because an empty fauna has no breeders
  and cannot refill.
- **Recovery time.** The registered rule returns d = 0 whenever divergence takes more than 20 seasons to reach h. Its
  numbers are printed in §4, and no recovery claim is made.
- **Any single per-seed value** of the size of the A/A-like per-seed RMS: about 0.10 (coordinator), or 0.077 for
  R-cull20 on these arms (`placebo.txt`).

**A/A caveat (coordinator, 18:30; RBT-96).** The run-to-run null in the arena is about 3 times what was assumed,
and the ecology's own A/A spread (RBT-105, `aa_spread.txt`, due about 20:00 UTC) has not landed.
- The class is not borderline: 10/10 positive, and a lower bound 1.8 r above 0.
- The borderline readings are conditional on that spread: the "holds up" line (co-evolved R-shift −0.055, with an
  interval spanning 0), and the turnover guard (below).
- No unresolved paired difference below is read as an effect.

Everything below re-derives from `runs/RBT-99/readout.txt`, written by `readout.sh` from committed tables alone,
and `runs/RBT-99/score.txt`, written by `score.py` from the same tables plus `price.txt`.

## Provenance

| what | where |
|---|---|
| pre-registration | `runs/RBT-99/PREREGISTRATION.md` (13:05 UTC), Amendment 1 (13:38, answering adversary round 1) and Amendment 2 (14:16, carrying RBT-92's Amendment 3), all before any arm existed; approved by the coordinator at 14:08 |
| seed rule, onsets | RBT-92's: all ten, 10/10 read; `runs/RBT-92/onset.txt`, T = 352–382 |
| baselines | the ten RBT-90 part 2 arms, `runs/RBT-90/forage-SEED/` |
| arms | 10 shift arms and 10 cull arms (`runs/RBT-99/shift-SEED`, `cull-SEED`, `cull-k-SEED.txt`), run by the hive and merged by 18:30; cull20 is RBT-92's (`runs/RBT-92/cull20-SEED`), the same run, as registered |
| readout | `readout.txt`, from `readout.sh` on integration `ce1874ef` plus this branch |
| price | `price.txt` from `price.py` on the ten baselines' pre-onset seasons (restored from `ckpt/rbt-90-SEED`). **Deviation:** it was registered as a gate item to be committed before any arm ended (Amendment 2). It was not; it was computed at 18:40, after the arms ended. It reads only seasons before T, which are byte-identical across arms (V0), so it cannot have been selected on the outcome. Without it, the readout.py part of `readout.txt` is identical (checked with `diff`). |
| scoring | `score.txt` from `score.py`, committed files only |
| round trip | `roundtrip.txt`: in a worktree of the report commit (`0973da5`) holding no bulk, `readout.sh`, `score.py` and `placebo.py` reproduce `readout.txt`, `score.txt` and `placebo.txt` **byte for byte**. Perturbing one cell (`shift-3/seasons.txt`, season 450, holistic income +0.5) moves 12 lines: r (0.1832 → 0.1828), seed 3's recovery R-body (+0.3099 → +0.3149), the mean (+0.5191 → +0.5196) and seed 3's price line |
| tests | `python -m pytest -q` on this branch: 289 passed |
| placebo and paired readouts | `placebo.txt` from `placebo.py`: the RBT-92 readout adversary's P3/P4 method (PR #183, `runs/RBT-92/readout-adversary/probe_readout.py`), reused through `readout.py`'s own functions on committed tables. Added after the coordinator's 18:45 ruling; the registered readout is unchanged |

## 1. Validation, read first (V0–V3)

- **V0, V1 and V2 pass on 10/10 seeds.**
  - **V0:** every arm is identical to its baseline before T, on every `seasons.txt` row and on every
    `lineage-last.txt` row of an individual that died before T.
  - **V1:** the culls are exactly as stated. On **3 seeds (806, 1, 3) the designed k (78, 63, 69) is at least the
    60 alive at T − 1**, so the cull empties the fauna. V1 expects 60 and gets 60 (the F1 fix). Designed R-null on
    those seeds is **n/a** (F3), and R-cull there is labelled "extinction, not turnover".
  - **V2:** the tracer's alive count equals the table's.
- **V3 fails, for the reason RBT-92's report gives, on the same cull20 arms.** The alive dip is 0 on 10/10 seeds,
  because freed slots refill within the season and `seasons.txt` records alive at season end. Holistic
  L(T+60), cull20 − base, is −0.042 [−0.106, +0.022].
- **Consequence, as pre-registered:** the carriage readouts print as **UNVALIDATED** and enter no sentence of this
  report beyond this one. One carriage prediction is scored in §6 and marked as such. For the record,
  designed-side Lc shift − base is −0.18 to −0.31 at every horizon; it is not read.
- **Nothing in V0–V2 blocks the verdict.**

## 2. The co-evolved against designed contrast, before, at and after

R-body is holistic − designed `mean_lifetime_score`, as a window mean; an extinct fauna earns 0. Each cell gives
the mean over 10 seeds, its 95% t(9) interval, and the positive count.

| arm | before [T−100, T) | transient [T, T+60) | **recovery [T+60, T+160)** | tail [T+160, T+200) |
|---|---|---|---|---|
| base | +0.158 [+0.080, +0.236] 9/10 | +0.169 [+0.055, +0.283] 8/10 | +0.148 [+0.051, +0.245] 9/10 | +0.106 [+0.016, +0.196] 8/10 |
| **shift** | +0.158 (identical by V0) | +0.327 [+0.200, +0.454] 9/10 | **+0.519 [+0.336, +0.702] 10/10** | +0.563 [+0.357, +0.770] 10/10 |
| cull | +0.158 | +0.428 [+0.077, +0.779] 9/10 | +0.435 [+0.108, +0.761] 9/10 | +0.469 [+0.154, +0.784] 10/10 |
| cull20 | +0.158 | +0.205 [+0.055, +0.355] 8/10 | +0.191 [+0.084, +0.299] 8/10 | +0.194 [+0.063, +0.326] 8/10 |

**Per seed, recovery window** (`readout.txt`; the base in brackets):
801 +0.076 (+0.019), 804 +0.222 (+0.113), 805 +0.488 (+0.209), 806 +0.870 (−0.042), 807 +0.636 (+0.094),
1 +0.666 (+0.407), 2 +0.837 (+0.018), 3 +0.310 (+0.161), 4 +0.534 (+0.240), 7 +0.552 (+0.261).
The three largest shift − base gaps (806 +0.912, 2 +0.819, 807 +0.542) are the three seeds where the designed fauna went extinct. The fourth D seed, 3, has a gap of +0.149.

**Power** (RBT-89 §7's line):
- The per-seed spread of recovery R-body is sd 0.256, so **r = 0.183**. That is 2.4 times the pre-registered
  expectation of 0.077, because the designed collapse varies so much between seeds.
- Class B was not reachable at the realised spread. The equivalence form, |mean| + r = 0.702, is far from < 0.10.

## 3. What the shift did to each body (R-shift = shift − base, paired per season)

| fauna | transient | recovery | tail |
|---|---|---|---|
| co-evolved | −0.117 [−0.188, −0.046] 2/10 positive | **−0.055 [−0.123, +0.013]** 4/10 | −0.057 [−0.136, +0.022] 4/10 |
| designed | −0.275 [−0.310, −0.240] 0/10 | **−0.426 [−0.621, −0.231]** 0/10 | −0.515 [−0.784, −0.246] 0/10 |

**Per seed, recovery, with the price** (0.05 × pre-onset kJ, `price.txt`), shown as R-shift / price / net
(`readout.txt`, C2 block):

| seed | co-evolved | designed |
|---|---|---|
| 801 | −0.132 / 0.394 / +0.262 | −0.190 / 0.955 |
| 804 | −0.130 / 0.342 / +0.212 | −0.238 / 0.944 |
| 805 | −0.004 / 0.203 / +0.198 | −0.283 / 1.010 |
| 806 | +0.016 / 0.332 / +0.348 | −0.896 / 1.072 (extinct) |
| 807 | −0.174 / 0.247 / +0.074 | −0.716 / 1.009 (extinct) |
| 1 | +0.085 / 0.135 / +0.220 | −0.174 / 0.866 |
| 2 | +0.006 / 0.256 / +0.262 | −0.813 / 0.995 (extinct) |
| 3 | −0.194 / 0.305 / +0.111 | −0.343 / 0.885 (4 alive) |
| 4 | −0.041 / 0.239 / +0.198 | −0.335 / 0.974 |
| 7 | +0.019 / 0.161 / +0.179 | −0.272 / 0.792 |

- The co-evolved transient loss resolves (−0.117). By the recovery window it no longer does.
- **Designed "net" is not read.** It is survival-conditioned: its survivors are, by construction, the robots
  that could pay, which is F6's point. On the extinct seeds it is bounded by the base's income.

**The null.**
- **k, the excess deaths in [T, T+10):** designed 33, 36, 42, 78, 43, 63, 41, 69, 32, 27; co-evolved 20, 0, 1, 2,
  2, 3, 1, 10, 0, 0.
- **Designed R-null** is scored on the 7 uncapped seeds: −0.388 [−0.575, −0.201] in recovery, 0/7 positive. On
  those seeds the shift did far more to designed income than an impulse cull of its first ten seasons' excess.
- **The null sees the first ten seasons only (F7).** The shift arm's designed deaths over [T+10, T+60) were 323
  to 635 per seed, against 38 to 111 in k's window. So R-null reads "more than an impulse cull of the first ten
  seasons' excess", not "more than turnover".
- **Turnover guard**, on the 7/10 seeds with co-evolved k > 0: co-evolved R-null (recovery) is −0.084, and
  |R-null| < r, so the printed answer is YES.
  - But r here is 0.183, and R-null's own interval is −0.074 [−0.117, −0.031] on all ten seeds, which excludes 0.
    The shift cost the co-evolved body slightly more than the cull did.
  - The guard's "YES" is a statement about r, conditional on the A/A spread. It is not a finding of equivalence.
- **Turnover reference, cull20:** R-cull20 in recovery is +0.047 [−0.016, +0.110] co-evolved and +0.004
  [−0.035, +0.042] designed. A random cull of a third moved neither by a resolvable amount.

## 4. Recovery time (primary: paired against the control)

| arm | co-evolved | designed |
|---|---|---|
| shift | recovered within 180 on **9/10**; per seed 127, 98, 46, 0, 0, 3, 0, none, 177, 73 | **0/10**, none on every seed |
| cull | 10/10; median 0 | 7/10; none on the 3 capped seeds |
| cull20 | 9/10; median 15 | 10/10; median 2.5 |

- **These numbers are printed, and no recovery claim is made** (coordinator ruling 18:45). The rule returns d = 0
  whenever divergence takes more than 20 seasons to reach h, so a 0 can mean "never left" or "left slowly", and a
  "none" is not reliably separated from a slow drift.

## 5. Readings owed by the pre-registration

- **The claim line (§2, C2), verbatim:**
  > Claim tested: survivorship of the co-evolved population at an economic boundary the designed body's budget is
  > not expected to survive. That is a different claim from the owner's (it is about one body's cheapness, not two
  > bodies' contest), and a C2 result is reported as such.
- **The claim is met, by income, not by alive.** Alive = 60 is uninformative, because deaths are refilled within the
  season. On 10/10 seeds the co-evolved recovery income was +0.79 to +1.22, never near the basal 0.25, and its cost
  against the control does not resolve.
- **The designed body's budget is exceeded, but not everywhere.** It was bankrupt by D's test on 4/10 seeds and
  solvent by turnover on 6/10.
- **The sentence is:** *at the dearer price, the co-evolved body lost no resolvable income against its control and
  slightly more than a random cull took (−0.074). The designed body lost 0.43 against its control and 0.39 against
  the cull, and survived only by turnover, or not at all.* This is one body's cheapness, not the owner's contest,
  and class A adds nothing to it (P3).
- **"Robust" means survivorship of standing morphology and gait**, not adaptation (§3, RBT-91 option A). With
  depth about 5 events, the co-evolved body "survives" or "is sorted"; it does not "re-adapt". No carriage claim
  is made, because V3 failed.
- **Class tests (8/10 guard):** E1 0/10; D 4/10; E2 0/10.
- **Forbidden readings.** §14's reading 2 applies: this is not a win by bankrupting the comparator, because D did
  not reach its guard. C2's own reading (a) is covered by the section above, and the class-A sentence carries the
  turnover ratio (F6).
  - Reading (b), the price read as maladaptation, does not arise: the co-evolved body held up.
  - Reading (c), pooling with C1 or C3, is not done here. RBT-92's C1 class A is a different claim.
- **Seed 806 carries the drift flag.** Its baseline deaths over [T, T+10) were 54, against 1.5 × 34.3. It is read
  with the flag beside it; it is one of the four D seeds.

## 6. Predictions, scored (`score.txt`)

The amended predictions (Amendments 1 and 2) are the registered set; the original §10 value is in brackets.

- **Class: A, registered at 0.12 [originally 0.07].**
  - Missed: D at 0.30 [originally 0.75], and F, the modal class, at 0.33.
  - **The original design's most exposed claim, that C2 bankrupts the designed population, is falsified by its
    own falsifier (i).** The designed fauna was not bankrupt on **6/10** seeds, and the falsifier fires at ≥ 3/10.
    Amendment 1 had moved toward this (expected to fire, 0.65), on the adversary's F2.
- **Hits:**
  - designed transient deaths ≥ 2 × base on ≥ 8/10 (0.8): 10/10;
  - co-evolved survives on 10/10 (0.85);
  - "holds up" (0.12);
  - K2 ≥ alive on some seed (0.55): 3/10;
  - designed paired recovery "none" on ≥ 8/10 (0.7): 10/10 (scored as registered; the rule is flagged at 18:45, so this is not a recovery claim);
  - co-evolved cull recovery ≤ 20 on ≥ 8/10 (0.6): 9/10 (scored as registered; the rule is flagged at 18:45, so this is not a recovery claim);
  - falsifier (ii) not firing;
  - designed R-shift inside (−0.8, +0.3): −0.426;
  - R-body inside (−0.40, +0.60): +0.519, though the point, +0.10, was far off.
- **Misses:**
  - designed D-half on ≥ 8/10 (0.35): 4/10;
  - designed alive < 12 in the transient on ≥ 7/10 (0.15): 3/10;
  - designed extinct by T+160 on ≥ 5/10 (0.10): 3/10;
  - co-evolved R-shift −0.24: it was −0.055, outside (−0.40, −0.10);
  - co-evolved net +0.03: it was +0.206;
  - K1 median 6: it was 1.5;
  - K2 median 50: it was 41.5;
  - co-evolved R-null ≈ R-shift beyond r (0.65);
  - co-evolved paired recovery "none" on ≥ 7/10 (0.65): 1/10 (scored as registered; the rule is flagged at 18:45, so this is not a recovery claim).
- **Carriage** (unvalidated, scored only for the record): L(T+160) shift − cull within ±0.10, −0.030, HIT (0.5).
- **Brier score** over the 12 probability-stated binary predictions, excluding the class rows and the carriage
  row: **0.201**.
- **What I got wrong, in one line:** I priced the co-evolved body's shock at its full price and expected it to
  stay down. It recovered about 80% of the price within the recovery window (net +0.206 against a mean price of 0.261, `score.txt`). I also under-weighted how
  often the designed fauna would go extinct outright rather than churn: 3/10 extinct, against the 0.10 I gave to
  ≥ 5/10.

## 7. Depth

This is RBT-92's: the same T, so about 5.3 reproduction events inside the transient and recovery windows
(`runs/RBT-92/baseline_depth.txt`).

## 8. What this does not establish

- **A mechanism for the co-evolved recovery of its price.** Sorting on kJ and survivor-conditioning of the lifetime
  mean are not separated by the committed tables. The shift arms' lineage bulk, on `ckpt/rbt-99-shift-SEED`,
  carries per-robot kJ and could separate them. That is a follow-up, not part of this pre-registration.
- **Any carriage claim** (V3 failed).
- **Equivalence** of anything to anything (r = 0.183, and the A/A spread is pending).
