# RBT-99 report: epoch C2, dearer work (work cost 0.03 → 0.08 per kJ) on ten founding populations

*Amended at 19:10 UTC after the readout adversary (PR #187, `runs/RBT-99/readout-adversary/`) and the
coordinator's 19:05 ruling. The registered readout is unchanged. The headline below is the adversary's (F2),
adopted as written.*

**Verdict (RBT-89 §9, as pre-registered): class A, co-evolved wins. It stands.**
- R-body in the recovery window of the shift arm is **+0.519** (95% t(9) [+0.336, +0.702]), positive on 10/10
  seeds, with r = 0.183. The sign guard needs 8/10, so the margin is 2 seeds.
- The falsifier, "the designed body wins on the held-out challenge", is not met. Class C and E2 are both reached
  on 0/10 seeds.
- D's test fires on 4/10 seeds, below the 8/10 guard.
- **The rule also returns A where there is no event:** on the no-event baseline's own recovery window, and on
  **23/25 placebo onsets** (`placebo.txt` P3; F4).
- **Unlike C1, the paired event contrast classifies A as well:** shift − base is +0.371 [+0.162, +0.581], 10/10.
  So here the event did move the contrast. What moved it is the arithmetic below.

**What the event did (F2, the adversary's headline):**

> The designed gait costs 3.6 times the co-evolved gait's kJ, so the price alone takes 0.95 per season from the
> designed body and 0.26 from the co-evolved one. Two unchanged populations would have diverged by +0.69; the
> observed divergence is +0.37 [+0.16, +0.58], 10/10. Net of its own price, each body recovered part of the loss:
> the co-evolved body +0.21 (79% of its price), the designed body +0.52 (55%), and more in absolute terms
> (difference −0.32 [−0.50, −0.14]). The paired effect is therefore the co-evolved body's cheapness before the
> event, which is C2's claim. It is not a difference in how the two bodies responded. At an unchanged gait the
> designed fauna would earn below basal on every seed; it stayed solvent on 6/10 seeds only by turnover (3.9–6.7×
> its baseline's deaths) and went extinct on 3.

All figures come from `score.txt`: the arithmetic paired prediction is +0.689 [+0.627, +0.751], and net
co-evolved − net designed is −0.318 [−0.498, −0.138], 2/10 positive.

**Both nets, side by side (F3).** Each net is R-shift + price, where the price is 0.05 × the fauna's pre-onset kJ
from `price.txt`.

| | price | net | share of price recovered | conditioning |
|---|---|---|---|---|
| co-evolved | 0.261 | **+0.207** [+0.151, +0.262], 10/10 | 0.79 | a survivors' lifetime mean, at low turnover (0.96–1.93× base in the transient). The base's own kJ after T is unmeasured; its pre-T drift is worth about ±0.05 on the share. Per-seed shares run 0.30–1.63, at the A/A size. |
| designed | 0.950 | **+0.524** [+0.362, +0.687], 10/10 | 0.55 | survivor-conditioned on the 7 seeds where it survived; pinned by extinction on 3 |

- In absolute income, the designed body recovered more (difference −0.318). As a share of its price it recovered
  less, and that per-seed difference does not resolve (adversary F2).
- Neither scale was registered. **Neither body can be said to have adapted better.**
- The mechanism of either net (sorting on kJ, or survivor-conditioning) is not separated by the committed tables.

**Against the no-event control and against the registered null (F6, F8).** Recovery window:

| | vs the control (shift − base) | vs the null (shift − cull) |
|---|---|---|
| paired R-body | +0.371 [+0.162, +0.581], 10/10 | **+0.315 [+0.161, +0.469], 7/7**, n = 7 uncapped seeds (F3 option (a)) |
| designed cost | −0.426 [−0.621, −0.231], 0/10 | −0.388 [−0.575, −0.201], 0/7 |
| co-evolved cost | −0.055 [−0.123, +0.013], unresolved | −0.074 [−0.117, −0.031], resolved and small |

- On the three capped seeds (806, 1, 3) the null is extinction, so shift − cull is n/a there, as registered.
- **The designed R-null is the price, not turnover.** A random cull carries no price: a cull of 27–43 designed
  robots moved designed income by −0.018 (adversary P4). Designed R-null net of price is +0.566.
- **"Holds up":** co-evolved R-shift −0.055 is within −r = −0.183, as an unresolved loss, not a shown absence of
  one. Against the null the co-evolved loss resolves, at −0.074. The designed body does not hold up by any bar
  (−0.426); at an unchanged gait its R-shift would have been −0.95.

**Seed subsets are post hoc (F5).** "The 7 seeds where the designed fauna never reached 0" is defined on the
outcome, and so is the registered D partition. Every 7-seed figure in this report is **post hoc and
outcome-defined**: shift − base +0.205 [+0.114, +0.296], 7/7. The alternatives agree: 6 non-D seeds +0.215, and 5
neither extinct nor capped +0.206 (adversary P3).
- The three extinct seeds carry 61% of the summed paired effect.
- Coding their extinct seasons at the unchanged-gait income instead of 0 gives +0.382, against +0.371, so the 0
  coding does not inflate the effect.

**What is not read.**
- **Recovery time (F7).** No recovery claim is made from the registered rule. Its numbers are in §4 for the record.
  Of the co-evolved "recovered on 9/10", three (806, 807, 2) are d = 0 artifacts: divergence first reached h at
  T+29, T+31 and T+52. The designed "none on 10/10" is its price, which is 6–9 h.
- **Survival from alive = 60.** Deaths refill within the season. Designed extinction on 3 seeds is the one
  informative survival fact.
- **Any single per-seed value** at the A/A size. The co-evolved per-seed R-shift has RMS 0.106; A/A-like samples
  run 0.077–0.108 (adversary F9).

**Turnover guard (F10).** It prints YES because co-evolved R-null (−0.084) is smaller than r **(n = 7; r is
inflated by the comparator's spread**, while the co-evolved R-null's own paired r is 0.043). It is not a finding of
equivalence.

**A/A (F9).** Jittering per-seed values by the A/A size leaves class A in ≥ 99.4% of draws, for both the level and
the paired contrast. RBT-105's spread cannot move the class or the paired sign. It is a post hoc check on the
per-seed tables.

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
| round trip | `roundtrip.txt`: in a worktree of the report commit (`2e04ebd`) holding no bulk, `readout.sh`, `score.py` and `placebo.py` reproduce `readout.txt`, `score.txt` and `placebo.txt` **byte for byte**. Perturbing one cell (`shift-3/seasons.txt`, season 450, holistic income +0.5) moves 12 lines: r (0.1832 → 0.1828), seed 3's recovery R-body (+0.3099 → +0.3149), the mean (+0.5191 → +0.5196) and seed 3's price line |
| tests | `python -m pytest -q` on this branch: 289 passed |
| readout adversary | PR #187, `runs/RBT-99/readout-adversary/` (written against `b5783ed`); coordinator ruling 19:05; F2–F10 and F12 carried into this text, and `score.py`/`placebo.py` extended for F3, F6 and F12 |
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
(`readout.txt`, C2 block; the designed net is `readout.txt`'s, read with its conditioning, F3):

| seed | co-evolved | designed |
|---|---|---|
| 801 | −0.132 / 0.394 / +0.262 | −0.190 / 0.955 / +0.766 |
| 804 | −0.130 / 0.342 / +0.212 | −0.238 / 0.944 / +0.705 |
| 805 | −0.004 / 0.203 / +0.198 | −0.283 / 1.010 / +0.727 |
| 806 | +0.016 / 0.332 / +0.348 | −0.896 / 1.072 / +0.176 (extinct) |
| 807 | −0.174 / 0.247 / +0.074 | −0.716 / 1.009 / +0.293 (extinct) |
| 1 | +0.085 / 0.135 / +0.220 | −0.174 / 0.866 / +0.692 |
| 2 | +0.006 / 0.256 / +0.262 | −0.813 / 0.995 / +0.183 (extinct) |
| 3 | −0.194 / 0.305 / +0.111 | −0.343 / 0.885 / +0.542 (4 alive) |
| 4 | −0.041 / 0.239 / +0.198 | −0.335 / 0.974 / +0.638 |
| 7 | +0.019 / 0.161 / +0.179 | −0.272 / 0.792 / +0.520 |

- The co-evolved transient loss resolves (−0.117). By the recovery window it no longer does.
- **Both nets are read side by side, each with its conditioning** (headline table; F3). The designed net is
  survivor-conditioned on 7 seeds and pinned by extinction on 3. The co-evolved net is a survivors' mean at low
  turnover. Neither is read alone.

**The null.**
- **k, the excess deaths in [T, T+10):** designed 33, 36, 42, 78, 43, 63, 41, 69, 32, 27; co-evolved 20, 0, 1, 2,
  2, 3, 1, 10, 0, 0.
- **Designed R-null** is scored on the 7 uncapped seeds: −0.388 [−0.575, −0.201] in recovery, 0/7 positive.
  **It is the price, not turnover** (adversary F2). A random cull carries no price: a cull of 27–43 designed robots
  moved designed income by −0.018. Net of the price, designed R-null is +0.566.
- **Paired R-body against the null, shift − cull, n = 7 uncapped seeds: +0.315 [+0.161, +0.469], 7/7**
  (`placebo.txt`; F6). The capped seeds, where the null is extinction, are n/a.
- **The null sees the first ten seasons only (F7).** The shift arm's designed deaths over [T+10, T+60) were 323
  to 635 per seed, against 38 to 111 in k's window. So R-null reads "more than an impulse cull of the first ten
  seasons' excess", not "more than turnover".
- **Turnover guard**, on the 7/10 seeds with co-evolved k > 0: co-evolved R-null (recovery) is −0.084, and
  |R-null| < r, so the printed answer is YES **(n = 7; r is inflated by the comparator's spread**; the co-evolved
  R-null's own paired r is 0.043; F10).
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

- **No recovery claim is made from the registered rule** (coordinator rulings 18:45 and 19:05; F7). The numbers are
  printed for the record only.
- **Co-evolved:** left the band and re-entered it on 6/10 seeds (801, 804, 805, 1, 4, 7; d = 3–177). Three seeds
  (806, 807, 2) show d = 0 only because divergence first reached h at T+29, T+31 and T+52, after the 20-season hold
  was already met. Seed 3 is "none" (adversary P7).
- **Designed:** "none" on 10/10, as its price (6–9 h on every seed) predicts for an unchanged gait.

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
- **The class rule returns A on the no-event baseline and on 23/25 placebo onsets** (F4). Unlike C1, the paired
  event contrast also classifies A (shift − base +0.371, 10/10; shift − cull +0.315, 7/7), so the event did move the
  contrast. That movement is the price arithmetic of the headline.
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
  - designed transient deaths ≥ 2 × base on ≥ 8/10 (0.8): 10/10, right, but set by the pre-onset kJ (F12);
  - co-evolved survives on 10/10 (0.85), right, but set by the pre-onset kJ: its unchanged-gait income would be
    +0.53 to +1.00 on every seed (F12);
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
- **Carriage:** L(T+160) shift − cull within ±0.10 is **not scored (UNVALIDATED, V3)** (18:45 ruling; F12). The
  value, −0.030, is printed and not read.
- **Brier score** over the 12 probability-stated binary predictions, excluding the class rows and the carriage
  row: **0.201**.
- **What I got wrong:**
  - I priced the co-evolved body's shock at its full price and expected it to stay down. Net of price it recovered
    +0.206 of 0.261. But the designed body recovered more in absolute terms (+0.524 of 0.950), which my predictions
    did not anticipate.
  - I under-weighted outright designed extinction: 3/10 seeds, against the 0.10 I gave to ≥ 5/10.

## 7. Depth

This is RBT-92's: the same T, so about 5.3 reproduction events inside the transient and recovery windows
(`runs/RBT-92/baseline_depth.txt`).

## 8. What this does not establish

- **A difference in how the two bodies responded.** Net of its own price, the designed body recovered more in
  absolute terms and less as a share; neither scale was registered (F2, F3).
- **A mechanism for either body's recovery of its price.** Sorting on kJ and survivor-conditioning of the lifetime
  mean are not separated by the committed tables. The shift arms' lineage bulk, on `ckpt/rbt-99-shift-SEED`,
  carries per-robot kJ and could separate them. That is a follow-up, not part of this pre-registration.
- **Any carriage claim** (V3 failed).
- **Equivalence** of anything to anything (r = 0.183, and the A/A spread is pending).
