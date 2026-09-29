# RBT-129 amendment F (founding): adversary report

PR #493, head `7b67b11`, base `claude/new-session-4cao7d` at `b4f10e7`. Files reviewed: `AMENDMENT-FOUNDING.md`, the
DESIGN.md diff (§15 pointer only), `founding-amendment/founding_expect.py → .txt`. Background: #490/#491, the ruling on
#490 (comment 5880596624), `stageP0-readout{,-adversary}/`, `rabbitstew/ecology.py`, `rabbitstew/evolution.py`, and the
named tests.

The re-derivation uses my own code, `rederive.py → rederive.txt`, plus a Monte Carlo check (`mc_check.py → mc_check.txt`). All of it is stdlib. It reads committed text only and runs no simulator. No
ecology run was made.

## Verdict: **ADOPT-WITH** (5 MUST, 8 SHOULD)

Option (a) is the right choice among (a)–(d), and its mechanism is sound:
- the salts are key-safe;
- a single-fauna screen is the same criterion as the S arm's pre-merge founding;
- K-SALT is a valid byte-compare.

The headline numbers reproduce as arithmetic: 7.67 / 6.03, 0.29 / 0.78, the n-power row, 0.790 / 0.902, 878–985 and
1,504–1,611. Three problems remain:
- one input is wrong: seed 129004 at `c1-p030-PW-G`;
- the plug-in headline is circular by construction, and the power is computed for the wrong validity (59, not 239);
- two spec statements do not work as written: the anchor-fallback fork source, and the "≤ 47 worst case".

None of these overturns (a). They move the honest expectation at the 24 points:
- from **7.7** valid seeds to **about 5.4–7.2**;
- from **22.5** points not PARTIAL to **about 15–20.5**;
- from mean income power **0.79 / 0.90** to **about 0.56–0.74 / 0.68–0.84**.

The owner should approve cost against that range, not against the plug-in alone.

## 1. Criterion consistency (alone vs two-fauna): **consistent**

- **Stage-1 validity is pre-merge.** DESIGN §6.1 defines it on the S arm:
  - share: both faunas alive at season 59;
  - income: both alive in S through 239.
- **The S arm never merges.** It is "the two faunas in their own ecologies" for all 300 seasons (§5.2). Competition
  exists only in M/N, from season 60. So "founding in competition" is not a Stage-1 validity criterion anywhere.
  Founding alone and founding in S are the same criterion.
- **The code agrees.** In `ecology.py` `step()`:
  - pre-merge cohorts are per fauna, with one world per cohort and separate arena banks;
  - the terrain stream is drawn once per season whatever the populations are, before the cohort loop;
  - `only_fauna` draws the dropped fauna's founders from its own stream, claims their names, then drops them;
  - child names are prefixed per kind (`he…`/`ce…`), and founder names too (`h0-…`/`c0-…`), so names cannot couple the
    faunas.
  - `tests/test_rbt130.py::test_one_fauna_alone_is_its_half_of_the_two_fauna_run` asserts byte-identity. But it covers
    only 5 seasons of a toy breeding config, not the sweep's block (SHOULD 3).
- **The rule does not mix criteria**, provided the salt-0 source runs share the census config. Those runs are:
  - census S for 129001–3;
  - pilot S for 129004, 300 seasons;
  - A-stage anchor-fallback S for 129005–8.
  The amendment asserts they share the config but does not show it (SHOULD 3).

## 2. What the salt selects

- **The salt replaces the whole holistic stream.** `spawn_streams` swaps child `(0,)` for `SeedSequence(seed,
  spawn_key=(0, s))`. The founders, their staggered ages, and every later holistic draw (groupings, breeding, mutation,
  culls) move with it. At PW points the holistic arenas' food seeds are holistic draws too (`EcologyConfig.breed_stream`
  docstring), so the salt also redraws the holistic fauna's PW food layouts. That is not selected at W118-b, which is U
  with instant regrowth, but it is a difference from the unsalted run.
- **The label "among founder draws that establish at W118-b" is not accurate** (§0, T1, T4). §2.0's last bullet and
  T12 say so correctly, but the label is what every map carries (R5) (**MUST 4**).
- **A founders-only screen is possible.** It is the mirror of RBT-105's `breed_stream`: founders from the salted key,
  history from a fixed stream. It needs new code, because the salt × `breed_stream` composition is refused today. It
  would still select founders jointly with whichever history stream is fixed.
  - The gain in interpretability is small: the failing draws die by season 10–14, inside the founders' own energy
    runway, so what is selected is mostly the founders.
  - I agree with T12 that it is not worth a code cycle. The label must be fixed instead.
- **Key safety holds.** The two-long salt keys are `(0, s)` and, for the designed salt, `(1, t)`. They cannot equal:
  - the unsalted children `(i,)`;
  - the three-long `breed_seed_sequence` key `(0, 0, K)`;
  - the three-long `merge_null_seed_sequence` key `(i, 1, 0)`;
  - each other, since the first index differs.
  No code calls `.spawn()` on a child sequence (grep), so no grandchild `(i, n)` can alias a salt key.
  - **Correction:** the null key *does* have a test,
    `tests/test_rbt130.py::test_the_null_stream_is_independent_of_every_other_stream`, which covers holistic salts
    1–5. RBT-129c must extend it, and the breed-key test, to designed keys `(1, t)` (SHOULD 6).
- **K-SALT is a valid control.** Designed rows are per-population in `history.json`, and the designed lines in
  `lineage.jsonl` are identifiable. Nothing designed-side depends on the holistic population before the merge:
  - the terrain draw is unconditional;
  - names are kind-prefixed;
  - arena banks are per cohort.

  The 72 point-seeds (129002–3 × 36) is the right count.

## 3. Expected validity and power

### 3a. An input error: 129004 at `c1-p030-PW-G`

`founding_expect.py` hard-codes `PILOT4["c1-p030-PW-G"] = (True, True)`. The committed record says otherwise:
- `stageP0-readout-adversary/founders.txt` gives holistic last alive **16**, designed last alive 93;
- `pilot.txt` (b) gives the N arm at the merge as `nK 10 nO 0`: designed 10, holistic 0.

So 129004's holistic fauna is dead by season 16. §1's sentence "It survives to the merge at `c1-p030-PW-G`" is true
only of the designed fauna. 129004 is a W118-b founder that died at **both** PW-G points where it was tried.

Corrected class-B E[valid] (`rederive.txt` §3):
- plug-in: **0.00**, not 0.29;
- Jeffreys: **0.56**, not 0.78.

Class A is unchanged (**MUST 1**).

### 3b. The plug-in p_H is 1 at every class-A point by construction

Class A is defined as "129001 has both faunas at 59", and p_H is 129001's record at the point. So plug-in p_H = 1 at
all 24 class-A points, apart from pilot seed 129004 at `c1-p030-U-L`, which also survived. The 7.67 therefore assumes
perfect transfer. It is not an estimate, and §5's "the truth probably lies … nearer the plug-in" has no support.

The evidence on transfer is two founded draws: 129001 at 36 Stage-1 points, and 129004 at 3.
- **U/HP:** 2 of 2 draws survive everywhere they were seen.
- **PW:** 129001's holistic fauna is alive at 3 of 12 PW Stage-1 points, with **3, 10 and 18** members. 129004 is
  0 of 2.

Two class-A points are PW: `c0-p030-PW-G`, where 129001 has H = 3, and `c1-p010-PW-L`, where H = 10. The plug-in calls
both P(PARTIAL) = 0.00. Pooled by food family, both are P(PARTIAL) ≈ 0.98.

### 3c. Income validity is "alive through 239", not "alive at 59"

§5 prices income power off 59-validity. §6.1 defines the income test on survival through 239. The census stops at 59,
and the census note (§5.1, S1) says a weak fauna is extinct by 299 on 100% of seeds but by 59 on 1%.

Class-A points with fragile counts at 59:
- `c1-p080-HP-L`: designed at 1, 7 and 58;
- `c1-p010-PW-L`: holistic at 10;
- `c0-p030-PW-G`: holistic at 3.

The plug-in counts every one of these as a sure valid seed. In `rederive.py`, T is the count at season 59 that a fauna
must reach to be counted alive. T = 10 or 30 stands in for survival to 239 (**MUST 2**).

### 3d. The re-derived table

From `rederive.txt` §3: the 24 class-A points at n = 8, with income power as the mean over the 24 points at SD 0.334 /
0.275.

| model | E[valid] | not PARTIAL | mean income power |
|---|---|---|---|
| amendment plug-in (reproduced) | 7.67 | 22.5 | 0.789 / 0.901 |
| amendment pessimistic, Jeffreys on p_H only (reproduced) | 6.03 | 17.0 | 0.636 / 0.773 |
| Jeffreys on p_H **and** p_D (the amendment shrinks only p_H) | 5.61 | 13.8 | 0.587 / 0.725 |
| p_H pooled by food family, plug-in | 7.21 | 20.5 | 0.735 / 0.842 |
| pooled by family, Jeffreys on both | 5.81 | 15.8 | 0.607 / 0.739 |
| T = 10, plug-in | 7.11 | 20.5 | 0.729 / 0.834 |
| T = 30, plug-in | 6.67 | 19.0 | 0.679 / 0.776 |
| T = 30, pooled by family, Jeffreys on both | 5.41 | 14.8 | 0.559 / 0.679 |
| registered, for reference (reproduced) | 3.88 | 0.0 | 0.365 / 0.487 |

**Reading:** (a) roughly doubles the valid seeds against the registered design under every model. The claim of
"about 7.7 of 8" should read **about 5.4–7.7, central about 6.5–7**. The claim of "22 of 24 escape PARTIAL" should read
**about 15–20**.

**Power by valid n.** My independent route computes P(|T| > c) = E_Z[F_χ²(df (Z+δ)²/c²)], and a 400,000-draw Monte
Carlo confirms it. It reproduces 0.382 / 0.510, 0.529 / 0.686, 0.653 / 0.810, 0.752 / 0.891 and **0.826 / 0.939** at
n = 4–8.
- At n = 2 the amendment's 0.148 / 0.185 is a quadrature error: its χ² grid misses the df = 1 singularity. The
  correct values are **0.108 / 0.129**, and the Monte Carlo gives 0.108 / 0.129. The error is inherited from
  `power_eff.py` and moves the means by about 0.001 (nit, SHOULD 7).
- §0's "Registered: 0.381 / 0.510" is the n = 4 value. The registered 24-point mean is 0.365 / 0.488 (SHOULD 7).

**129001's record** (it founds at W118-b but loses a fauna at 12 points) is handled correctly as a known seed. Those 12
points are correctly left as survival calls. The only defect is that the same record is reused as the transfer
estimate, which is the circularity in 3b.

## 4. Free parameters

Fixed:
- the anchor;
- single-fauna S 0–59 at the census config;
- the salt order 0…20, first pass kept;
- the cap of 20, falling back to salt 0 labelled SCREEN-CAPPED;
- the stop rule, ≥ 3 of 16;
- the thresholds ⌈5n/8⌉ and ⌈3n/4⌉, which reproduce 5/6 and 10/12 (checked);
- the recorded (s_j, t_j) values;
- seeds 1–16 screened before Stage 1.

Nothing about the screen is chosen after its data. Four points remain.
- **"≥ 1 alive at 59" is too weak for the stated purpose.** The stated purpose is "two established populations". A
  draw with 1–3 survivors at W118-b would pass. It has not happened (the outcome is bimodal, 0 against 58–60), so a
  threshold of **≥ 30 of 60** changes nothing on draws 1–8 and costs nothing. It does keep a marginal founder from
  becoming a near-certain invalid seed at every Stage-1 point. Keeping §5.1's definition for consistency is defensible
  only if a pass below 30 is at least flagged (SHOULD 2).
- **The stop rule is tied to 16 seeds, but Stage 1 uses seeds 1–8.** With 2 of seeds 1–8 capped, every point has at
  most 6 valid seeds, one short of PARTIAL (< 6) at the first world loss. Stop at **≥ 2 capped among seeds 1…n** as
  well. At q = 0.157, P = 0.006, so it is cheap insurance (SHOULD 1).
- **T5's gate ranks by "census g0, faunas pooled".** The holistic fauna is absent on 2 of 3 census seeds almost
  everywhere, so g0 is mostly the designed fauna's regime. It is unspecified whether g0 pools over all census seeds or
  over 129001 only. That is left to the implementer after the data (SHOULD 4).
- **The anchor-fallback fork source does not exist as specified.** F5 and T7 say the anchor fallback forks M/N from
  "the passing screen attempt's S 0–59 state". Screen attempts are single-fauna (`only_fauna`), so that state has one
  fauna, and M/N need both.
  - The spec must name a two-fauna S 0–59 at (s_j, t_j) at W118-b as the fork source. That costs 3.1 / 6.2 core-h for
    8 / 16 seeds at 23.35 core-s, or 5.8 / 11.7 at 43.72.
  - The alternative is new code that composes two single-fauna states (**MUST 3**).

## 5. Scope creep

- **T5 is necessary.** As registered, "neither fauna FOUNDING-FAIL" admits no point, because the holistic fauna fails
  at 150 of 150. Replacing the clause is minimal. T5 also adds two rules, and both are data-informed choices to be
  labelled as such:
  - "M only on seeds valid at the merge" is sensible;
  - "a point where M runs on no seed frees its slot" is a new reallocation rule.

  T5 also re-admits about **171 / 320 core-h** of M + N. The literal registered gate would never have spent it. The
  amendment's "+28 / +52" is measured against the nominal gated figure, so that should be said (SHOULD 4).
- **Other changes beyond founding:**
  - T6, thresholds at any n: needed for F6, and fine;
  - T10, the resume credit: a consequence, and fine;
  - T3: an exception to "Stage 1 overrides the census", and fine.

  Nothing else.
- **RBT-118 / W118-b.** T7 treats only W118-b as selected. But §9.1 asks RBT-118 to put the sweep's seeds among its
  n = 20 at **all three** anchors. With salts, RBT-118's sample would then mix 8 (or 16) screened seeds with 12 (or 4)
  unscreened ones at W118-a and W118-c as well. T7 must say how the "RBT-118" anchor column handles that mix (SHOULD 5).
  - Asking RBT-118's registration to carry salts is itself a request to another study. It is fine as a request, since
    §9.1 already has a fallback if RBT-118 declines.

## 6. Cost (re-derived, `rederive.txt` §6–7)

- **Screen, expected: reproduced.**
  - 5.2 (q = 0.5) and 8.2 (q = 0.157) core-h at 13.6 core-s single-fauna. 13.6 is the committed W118-b S arm with the
    holistic fauna dead, from `cost.txt`, so it is well grounded.
  - 9.0 and 14.1 at 23.35.
- **Screen, "≤ 47 worst case": not a worst case.** It assumes every failed attempt dies by season 15, an assumption
  resting on 4 draws. The true bound, with every seed capped (416 attempts) and each attempt living to 59, is
  **94 core-h at 13.6** and **162 at 23.35**. Either relabel the figure, or add a kill rule (MUST 5).
- **Stage 1, gated, n = 8: reproduced exactly.**
  - The components are S 693–799, M 149, N 21 and plants 29, giving 892–999; less the amended credit of 14, that is
    **878–985**.
  - At 43.72 core-s: **1,504–1,611**. The +28 / +52 against the registered credit is also reproduced.
  - This is an upper bound. At 6 points 129001 has both faunas dead by 59, and Stage-1 seeds that die early cost almost
    nothing.
- **Unpriced:**
  - the MUST 3 fork source: 3–12 core-h;
  - the SHOULD 3 salt-0 re-run: 2.9–5.1 core-h.

## 7. Options

- **(c) per-point screen: rejection correct.** It selects on the measured outcome, erases EXCLUDED-H, and breaks common
  seeds.
- **(d) replace failing seeds: rejection correct.** It redraws the designed founders and the shared terrain jointly
  with holistic founding, and it collides with R-B's seeds 129009+.
- **(b) runway: rejection justified as a primary.** It has no feasibility evidence, changes every world, forfeits every
  census state, and the failing draws die at 10–14, inside the runway length that matters. Keeping it as the stop-rule
  fallback is right.
- **Redefining validity: rejection correct (§4).**
- **Anchor choice.** W118-b is correct over W118-a (`c1-p030-U-L`), which is a Stage-1 point, and over a PW anchor
  (selection on the PW outcome).
- **(a) is the best of the set.** Its asymmetry (4 of 8 holistic draws fail, 0 of 8 designed) is disclosed and reported
  as a layer.

## MUST (before the ruling adopts the text)

1. **Correct the 129004 input** at `c1-p030-PW-G`: holistic dead by season 16; designed alive at the merge and dead by
   93. Fix §1's sentence and the class-B figures to 0.00 / 0.56.
2. **Restate expected validity and power honestly.** Say that plug-in p_H = 1 on class A by construction. Report the
   range in 3d, including Jeffreys on p_D, family pooling and a T proxy for 239-validity. Label income power at
   59-validity an upper bound. Delete "nearer the plug-in". Suggested headline: **about 5.4–7.7 valid of 8; about
   15–20 of 24 escape PARTIAL; mean income power about 0.56–0.79 / 0.68–0.90.**
3. **Fix the anchor-fallback fork source** (F5, T7): a two-fauna S 0–59 at (s_j, t_j) at W118-b, costed, or new code.
4. **Fix the claim label** in §0, T1, T4 and every map: "among holistic and designed **stream draws (founders and their
   early history)** that establish at W118-b".
5. **Relabel "≤ 47 worst case"** as "≤ 47 if failed attempts die by season 15". State the true bound, 94 / 162 core-h,
   or add a rule that kills an attempt at season 30 with fewer than N members.

## SHOULD

1. Stop rule: also stop at **≥ 2 SCREEN-CAPPED among seeds 1…n**.
2. Criterion: **≥ 30 of 60 alive at 59** (identical on draws 1–8). Otherwise flag passes below 30 as MARGINAL-FOUNDER.
3. Re-run salt 0 **alone** for seeds 1–8 (2.9–5.1 core-h), byte-compared against the census and pilot halves for
   129001–4. This tests RBT-130's claim at the sweep's block and makes the screen uniform. Otherwise, show a config diff
   of the four source-run families.
4. T5: fix g0's definition for the gate (which seeds and faunas it pools). Label the slot-freeing rule data-informed.
   Disclose the about 171 / 320 core-h of M + N it re-admits.
5. T7: state how the RBT-118 anchor column treats mixed screened and unscreened seeds at W118-a/b/c. Report the sweep's
   seeds separately.
6. Key-safety text: cite the existing null-key test. RBT-129c extends it, and the breed-key test, to designed keys
   `(1, t)`.
7. Fix §0's "Registered 0.381 / 0.510" to 0.365 / 0.488 (the 24-point mean), and the n = 2 power to 0.108 / 0.129.
8. Make the pessimistic row shrink p_D as well as p_H.

## Rulings the coordinator needs

1. **Option (a): ADOPT, with MUST 1–5.** Recommended. It is the only option that removes draw failures and keeps world
   failures, common seeds and R-B's seeds.
2. **n = 8: ADOPT.** Even on the pessimistic models (about 5.4–6 valid seeds), n = 8 escapes PARTIAL at most U/HP
   points, and R-B's pre-screened seeds 9–16 remain the extension path. Do not pre-commit to n = 12.
3. **T5, the M/N gate: ADOPT with SHOULD 4.** Without it, M and N never run.
4. **The claim label: ADOPT as amended by MUST 4.** T7 (W118-b): adopt, with SHOULD 5 extending it to W118-a/c.
5. **The stop rule: ADOPT, tightened by SHOULD 1.** (b) as fallback: adopt.
6. **The screen criterion: prefer ≥ 30 of 60** (SHOULD 2). Registering it now is costless because draws 1–8 are
   bimodal.
7. **Cost for the owner:**
   - screen: 5–14 core-h expected (bound 94 / 162);
   - fork source: +3–12;
   - optional salt-0 re-run: +3–5;
   - Stage 1 at n = 8: 878–985 / 1,504–1,611, reproduced, and an upper bound.

## Files

| file | what |
|---|---|
| `ADVERSARY.md` | this report |
| `rederive.py → rederive.txt` | independent power (Simpson over Z plus the incomplete gamma), the pilot parsed from committed files, validity models, the screen's cap and stop, and the screen and Stage-1 cost. Stdlib; about 3 s |
| `mc_check.py → mc_check.txt` | Monte Carlo check of the power at n = 2, 3, 4 and 8 (400,000 draws a cell, seed 129) |

Reproduce: `python3 runs/RBT-129/founding-amendment-adversary/rederive.py > runs/RBT-129/founding-amendment-adversary/rederive.txt`.
