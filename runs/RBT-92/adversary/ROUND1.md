# RBT-92 adversary round 1: the design, before any arm

Adversary for RBT-92's design (PR #74, merged at `292d6c5`; Amendment 1 in PR #76 at `a3658f9`). I read none of the designer's reasoning beyond what is on the ticket and in `runs/RBT-92/`. Branch `results/RBT-92-adversary`; every probe and readout is under `runs/RBT-92/adversary/`. I read no RBT-90 part 2 output: every probe runs on RBT-71's committed tables (closed ticket), on the throwaway short runs of `shared_baseline_runs.sh`, or on one throwaway seed of my own (9902, not in the ten). Probe C reads demography, energy, groups and genomes only, never an income column.

**Summary.**
- **The re-derivations all reproduce**: the shared baseline to the sha256, the cohort cycle to the byte, and the smoke test.
- **The design is sound where it matters most.**
  - The control is clean: nothing outside `runs/` and `docs/` changed since `852dcac` except one test.
  - The t(n−1) power line is right.
  - V0 is format-compatible with RBT-90's tables.
- **Three findings must be fixed before launch.** They are small, and none touches the seed rule, n, windows or axis:
  - F1, the onset rule reads the control's post-onset deaths;
  - F3, B and S have no range at this digest;
  - F4, an extinct co-evolved fauna drops out of R-body, and class E hides a co-evolved collapse.
- **F5, C1's remainder group, is owed by the protocol.** It is written from the bulk, so it can follow launch.
- **The rest are caveats to carry into the report.**

| # | finding | verdict |
|---|---|---|
| F1 | the onset rule reads the control's post-onset deaths [T, T+10), the window k is sized on (§15 a) | **must fix before launch** (free: a pre-onset form exists) |
| F2 | V3 is a manipulation check, not a sensitivity test (§15 b) | report caveat |
| F3 | the body digest changes on 85% of births; B and S read 0.000–0.02 on the base by T+60–T+79 (§15 c) | **must fix before launch** (drop B and S, or pre-register a graded measure) |
| F4 | an extinct fauna drops its seed out of R-body, the guard and R-shift; class E reads a co-evolved collapse as "both fail" (§15 d) | **must fix before launch** |
| F5 | C1's remainder group is not reported, which the protocol requires | fix before the bulk is discarded; not a launch blocker (measured confound 0 at equal alive) |
| F6 | the null's channel (excess deaths in ten seasons) is nearly empty: k = 2 / 0 on the probe seed, energy buffers of 46–58 seasons, alive at 60 throughout | report caveat: R-null ≈ R-shift on most seeds, and the turnover guard is weak |
| F7 | the RBT-90 control on `852dcac` | no leak (credit) |
| F8 | class order A–F | sound apart from F4; print the equivalence form beside B |
| F9 | r at n = 10 | honest (credit) |
| F10 | the recovery-time floor: d = 0 on 57% of no-event onsets; recovery is measured against P, not against the control | report caveat and an unlisted deviation; restate three predictions |
| — | §8's "no solution" sentence | overstated, holds in substance: correct it |

## 1. Re-derivations (from a fresh integration checkout, `292d6c5`; 258 tests pass)

| what | result | readout |
|---|---|---|
| `shared_baseline_runs.sh` + `shared_baseline_check.py`, seed 801 | **identical to the designer's file, sha256 prefixes included** (`6018e0a9f5ec7965`, `9a405946df857ff4`): lineage 1185/1185, cohorts 20/20, history 20/20, 183 genomes, first difference at season 10, groups `[4, 5, 8]` at 10, 20 + 20 cull rows | `rederive_sbc_801.txt` |
| the same, seed 9901 | **identical** (1200/1200, 185 genomes, `7c1af2377d4ef9d4`) | `rederive_sbc_9901.txt` |
| `cohort_cycle.py` | **byte-identical** to `cohort_cycle.txt` | `rederive_cohort_cycle.txt` |
| the lag-60 peak, independently (numpy, not the designer's code) | peak lag in 30..90 is **60 on 12/12** population-runs; acf60 +0.415 to +0.670 selected, +0.878 to +0.883 drift, as stated | `probe_acf.txt` |
| `smoke.sh 801 9901` | **identical** to `smoke.txt` (V3 prints FAIL at n = 2, t(1), as it must) | `rederive_smoke.txt` |
| §8's rule "has no solution on a selected arm" | **overstated; holds in substance.** Read literally (no peak window, either fauna, ending within 20 seasons before T), it has solutions on 804 (T = 178–182, 312–314) and 805 (184–192, 253–257, 317). It has **none on 806** anywhere in [120, 400], and **none in [340, 400] on 3/3**. So it has no solution *guaranteed per seed* in the design's range, which is what forces the change. **Please correct the sentence** (report caveat). | `probe_s8_rule.txt` |

Credit where it is due: two runs on two machines give the same sha256. The byte-identity of arms before T is established, not assumed.

## 2. The four exposures the designer listed (§15)

### (a) The onset rule reads the baseline's deaths around T. Is that selection on the outcome? **Yes in form, small in size; free to remove. Must fix before launch.**

D(T) sums deaths over [T − 10, T + 10). The half [T, T + 10) is **the control's post-onset outcome**, and it is exactly the window `cull_k.py` subtracts from the shift arm's deaths to size the null. RBT-89 §8 measures the cycle "from the control arm's pre-onset seasons before T is fixed". That makes this a deviation, and it is **not in the designer's list**.

Probe A (`probe_onset_selection.txt`) splits every death on RBT-71's forage runs into two kinds. **Age-outs** (last row at age 59) are fixed by the age structure at T − 1, so they are shared by every arm. **Starvation deaths** are the control's own post-onset luck. The decomposition equals `seasons.txt`'s deaths in 1200/1200 cells per run.

- At the trough rule's T, post-onset starvation deaths sit **6.9 below** their mean over the candidate range (both faunas, mean of 3 runs: −4.6, −9.7, −6.6).
- A rule that reads only pre-onset state gets **−4.9**. That rule is: deaths [T − 10, T) plus the age-outs due in [T, T + 10), known at T − 1.
- Starvation is phase-locked to the wave, so most of the trough's low starvation is predictable. The part bought by reading post-onset data is **2.0 deaths on average**: 6 on 804 (T 370 against the pre-onset rule's 367: −4.6 against +1.4) and 0 on 805 and 806, where both rules pick the same T.

**Effect:** none on the primary R-body, which is the shift arm's own contrast. It enters k, biasing it upward by about the size above (a larger null makes the turnover guard fire more readily), and it enters the transient R-shift. **Fix:** replace D(T) with the pre-onset form above. `lineage-last.txt` gives the ages at T − 1. The cost is nothing, since `onset.txt` does not exist yet.

### (b) Validation moved from income to carriage and alive. **The reason holds; the replacement is a manipulation check, not a sensitivity test. Report caveat.**

The designer is right that a random cull selects on nothing, so its income effect is not known to be non-zero. Requiring the instrument to "see" it could reject a correct instrument. That is a good catch on RBT-89 §8.

But V3's two tests are both **guaranteed by construction**. The paired alive dip over [T, T + 10) *is* the cull. L(T + 60) must fall when 20 of about 60 C0 members are removed, because they lose all their post-T offspring.

So V3 shows that the tracer reads the file it was given. It does not show that the tracer resolves an effect the size the shift produces: k's predicted median is 6, not 20. It also validates L only, not B or S (see F3), and not income.

**Ask:** rename V3 "manipulation check (L, alive)". Print the smallest L difference cull20 − base resolves at this n, beside shift − base. The prediction "V3 passes, 0.85" is close to certain and should not be scored as a prediction.

### (c) The body-structure digest's granularity. **B and S have no range. Must fix before launch.**

Probe E (`probe_digest_inheritance.txt`) compares each holistic child's `tables.py` digest with its parents' digests (either parent, since `crossover_rate` is 0.3).

| run | holistic births with both genomes | `tables.py` digest inherited | coarse order-free digest inherited | full `body_signature` inherited |
|---|---|---|---|---|
| probe C plain, seed 9902, seasons 0–229 | 511 | **75/511 (14.7%)** | 159/511 (31%) | 0/511 |
| `shared_baseline_runs.sh` plain 801, seasons 0–19 | 33 | 4/33 | 7/33 | 0/33 |
| the same, 9901 | 56 | 14/56 | 24/56 | 2/56 |

The digest changes on nearly every birth. The coarse, order-free digest does too: node count, sorted shapes, sorted joint types and connection count. So this is **the operator, not only the granularity**: `mutate` edits discrete structure in most children (the joint type, connection graph, recursive limit and motor/mirror columns change most).

At T + 60 every living holistic individual is at least one birth from C0, and usually two or more. B = "digest equals a C0 ancestor's" therefore sits near 0 in **every** arm, base included.

Measured on probe C (`probe_shift_dynamics.txt` §4, `readout.py`'s own `Arm.carriage`, T = 150):

| arm | T+30 | T+60 | T+79 |
|---|---|---|---|
| plain: L / B / S | 0.550 / 0.467 / 0.500 | 0.367 / **0.017** / 0.018 | 0.333 / **0.000** / 0.000 |
| shift: L / B / S | 0.567 / 0.533 / 0.500 | 0.483 / 0.083 / 0.089 | 0.450 / 0.033 / 0.036 |

At T+30, B is carried by C0 members still alive, since `anc0` counts an individual as its own ancestor. By T+60 it is at 0.02 and by T+79 at 0. The pre-registered marks T+160 and T+199 are 80–120 seasons past that. **L has range (0.33–0.48); B and S do not.** 56–60 distinct digests among 60 living holistic individuals in every season read confirms it: almost every individual is its own structure.

Consequences:
- B and S cannot distinguish the shift from the base.
- The prediction "B(T+160) shift − base within ±0.10, 0.55" is near-certain under the floor, so it is not a prediction.
- The ticket's named readout, "the survivors' carriage of pre-event body structure", is carried by L alone.

**Fix, one of:**
- drop B and S from every sentence and say that carriage is lineage carriage (L), not structure carriage; or
- pre-register a graded measure, for example the fraction of a C0 ancestor's segments and joints retained (an edit distance), with its range shown on the base before launch.

### (d) R-body skips seasons where a fauna is extinct and relies on D/E. **Survivor bias, and class E mislabels a co-evolved collapse. Must fix before launch.**

`rbody()` (readout.py:180) keeps only seasons in which both faunas are alive. A seed whose holistic fauna dies in the recovery window returns NaN, and `stat()` drops it. The mean, the sign guard (`guard = ceil(0.8·nn)`, line 433) and r are then computed on the **survivors only**. D does not catch this, because D is the *designed* side's bankruptcy. E needs ⌈0.8n⌉ = 8/10 seeds.

**Holistic extinction on up to 7 of 10 seeds therefore leaves the verdict computed on the 3–9 seeds where it survived**, which biases it toward the co-evolved body. The R-SHIFT section has the same skip (the `alive` test in its comprehension).

A related gap sits in the protocol itself (RBT-89 §9). E reads "both populations reach 0, **or** the co-evolved population's window mean income falls below 0.25". A co-evolved collapse beside a thriving designed fauna therefore reads **"E. both fail"**, which is described as "neither body holds up". **There is no mirror of D.** The one outcome most damaging to the aesthetic bet would be reported under the wrong sentence.

**Fixes:**
1. No seed leaves R-body. An extinct fauna earns 0 in the seasons it is extinct: `tables.py` already writes 0.0 rows for the shift arm. The guard's denominator is n, not the survivors.
2. Split E:
   - **E1, both fail**: both faunas reach 0, or both fall below 0.25.
   - **E2, co-evolved bankrupt, designed not**: D's test with the faunas swapped, on ⌈0.8n⌉/n seeds. It is reported **with the falsifier** ("the designed body wins after the shift"), as its strongest form.
3. Post E2 as a deviation from RBT-89 §9, forced by the table's own text.

## 3. What was not listed

### F5. Remainder groups at 60 ÷ 8. **The protocol requires them reported and the design does not. Fix before the bulk is discarded; not a launch blocker.**

C1 (§2): "Capacity 60 ÷ 8 leaves one group of four each season (RBT-17); **the arm reports which robots that group held**, since a group of four in an eight-robot economy is the baseline world." Neither `tables.py` nor `readout.py` reports it.

The size of the leak depends on alive mod 8, which differs between faunas (grouping is per fauna: `rabbitstew/ecology.py:296–297`, a permutation cut into chunks):

- at N = 48 or 56, nobody is in a small group;
- at N = 47, 7 robots (14.9%) sit in a group of 7;
- at N = 57, 49 or 41, **one robot forages alone** on twelve items.

The robot-weighted mean group size runs from 7.64 to 8.00. Suppose income were proportional to 1/size, an upper bound. Then the fauna's mean moves by up to **9%** with N mod 8 alone, which is 0.05–0.09 items at incomes of 0.5–1.0. That is of the order of the 0.10 threshold. It enters R-body whenever the faunas sit at different N.

**Measured on probe C** (`probe_shift_dynamics.txt` §3). Both faunas sit at alive = 60 in every season from T to T+79, so there is one group of 4 per fauna per season: 320/4800 robot-seasons (6.7%), no robot alone, robot-weighted mean group size 7.73 on both sides. **On this seed the between-fauna confound is exactly 0**, because the faunas have equal N. The treatment is diluted by 6.7% on both sides alike. The confound appears only when alive differs between faunas, which a starvation wave can cause.

So I downgrade the urgency. The report is **owed by the protocol** and must be written from `cohorts.jsonl` while the bulk exists (the ckpt snapshots keep it). It is not a launch blocker.

**Fix:** `tables.py` writes `groups.txt` from `cohorts.jsonl` (season, fauna, group sizes, names in groups smaller than 8). `readout.py` prints, per window and fauna, the share of robot-seasons in groups smaller than 8, beside R-body. 

### F6. The null's channel, measured. **Report caveat: on the probe seed the shift kills almost nobody, so k ≈ 0 and R-null ≈ R-shift.**

I expected a lag: an income cut becomes a death only when the energy runs out, so much of the excess would fall after T + 10. Probe C (seed 9902, shift at 150, one seed, **an artifact, not an effect size**; `probe_shift_dynamics.txt`) shows something stronger.

- **The energy buffer at T − 1.**
  - Holistic: median energy 14.6 (quartiles 6.9–35.6), which is **58 seasons** to starve at zero income.
  - Conventional: median 11.5, which is **46 seasons**.
  - Only 7/60 and 12/60 would starve inside [T, T + 10) even at zero income.
  - Energy per head is 23 and 14 at T − 1.
- **The economy is slot-limited, not energy-limited.**
  - Alive is 60 in every season of both arms from T to T + 79.
  - Births equal deaths in every window.
  - The shift's excess deaths by window after T:
    - holistic: +2, +5, −4, −4, −5, −2;
    - conventional: −2, −1, −5, −6, −2, −9;
    - cumulative to T + 80: −8 and −25.
  - **cull_k.py's k = 2 (holistic) and 0 (conventional).**

**Consequences:**
- The null is close to the control on most seeds. With k = 0 its course *is* the control's, and the protocol says R-null = R-shift must then be stated.
- The turnover guard compares the shift against an almost-null disturbance.
- V3's k = 20 is an order of magnitude larger than the shift's demographic footprint (F2).
- Class D's and E's alive floors are unlikely to bind; their income tests carry them.

None of this is wrong by the protocol. But the pre-registration's "R-null: |holistic R-null| > r and close to R-shift, 0.6" becomes close to automatic when k ≈ 0. **The report should state, per seed, whether k was 0 and so R-null = R-shift by construction, and score that prediction only on seeds with k > 0.**

T = 150 on seed 9902 is younger than the design's T ≈ 370. RBT-71's forage runs show 11.6–17.6 starvation deaths per ten seasons at [340, 400] (probe A), so k may be larger at the real T. The designer predicts K1 median 6, which is consistent with this.

### F7. Using RBT-90's arm as the control. **No leak. Credit.**

- `git diff --name-only 852dcac origin/claude/new-session-4cao7d` outside `runs/` and `docs/` is **one file**, `tests/test_founder_diversity.py`. No code the runs execute changed.
- V0 compares the arms' pre-T `seasons.txt` rows with the control's by string. Both are written by RBT-71's `summarise` formatting (`str(h[k])`), so V0 cannot fail on formatting alone.
- The byte-identity above holds on this head.
- Residual risk: a future PR that touches `rabbitstew/` before the arms launch. V0 would catch it.

### F8. Are classes A–F well ordered? **Yes, apart from E (above).**

- E > D > A > C > B > F follows RBT-89 §9's precedence (D before A is the protocol's own rule).
- Letting B win the B/F overlap when |mean| < r ≤ 0.10 matches B's own text: "only a draw if the instrument could have seen a win".
- **Caveat to print:** B is |mean| < 0.10 with r ≤ 0.10. A mean of −0.09 with r = 0.10 is a "draw" whose interval reaches −0.19. Print the equivalence form beside it (|mean| + r < 0.10: the interval inside ±0.10), so a reader sees which draw it is.

### F9. Is r at n = 10 honestly computed? **Yes. Credit.**

- The `T975` table is right at every df used: t(5) 2.571, t(7) 2.365, t(9) 2.262.
- §8's table re-derives: 0.108·2.571/√6 = 0.1134 and 0.108·2.262/√10 = 0.0773.
- The readout takes the larger of the season-noise term and the observed per-seed t-half-width. The season term ignores autocorrelation, which the output says, but the seed term contains it.
- Two small points:
  - after an extinction (F4), `hw_seed` uses nn − 1 degrees of freedom while the season term uses n − 1. F4's fix removes the mismatch.
  - r is computed from the same per-seed values as the mean. That is standard for a t-interval, and it is what RBT-89 §7 asks for.

### F10. The recovery-time floor. **The instrument is noisy on an arm with no event. Report caveat, and one prediction to re-state.**

Probe B (`probe_recovery_floor.txt`) runs `readout.py`'s recovery rule (20 consecutive seasons inside P ± 2 SD) on RBT-71's control-like forage runs, at all 61 candidate T in [340, 400], on both faunas:

- **d = 0 on 209/366 onsets** (57%);
- d ≤ 20 on 258/366;
- "none" on 0/366;
- the tail reaches 134 seasons (806 holistic).

For independent seeds, "base 0 on 10/10" at 0.57 each has probability of about 0.004. The pre-registered 0.8 is off by the instrument, not by the biology. "Cull and cull20 ≤ 20 on ≥ 8/10, 0.7" is also nearly the base rate (70%).

Protocol §8 defines recovery against the **control** ("stays within the control arm's own window spread … of the control"). The design's primary form is against the pre-event plateau P, with the paired form in brackets. **That is an unlisted deviation.**

**Ask:**
- make the paired (arm − base) form primary, as the protocol has it;
- print the base's own d distribution as the floor;
- restate the recovery predictions against that floor.

## 4. Protocol fidelity, line by line against `docs/held-out-challenges.md`

**Quotes.** Amendment 1 (PR #76, `a3658f9`) quotes the C1 claim line, the §3 statement and §14's forbidden readings **verbatim**. I diffed them against the doc; they match. There is one typo: item 11's last line, "arithmetic on cited numbers.", is duplicated. §2's perception statement is in the template's words (field 2).

The **merged** PREREGISTRATION.md (`292d6c5`) still paraphrases, so the gap closes when #76 merges.

| template field / section | design | fidelity |
|---|---|---|
| 1 challenge, head hash, endpoint, kind | C1, RBT-17's endpoint quoted as parity; kind "competition" | ✓; head hash to be filled at launch |
| 2 perception, in the template's words; RBT-91 option | ✓ verbatim; option A | ✓ |
| 3 comparator; byte-identity through T − 1 | same-run designed fauna; identity re-derived here | ✓ |
| 4 seeds ≥ 6 passing the diversity rule, founder base rates | all ten, rule committed before any output; base rates from `RBT-90-head-founders.txt` | ✓ |
| 5 onset: cycle measured on the **control's pre-onset seasons**; T ≥ 20 after the last peak; stagger seasons inside the windows | trough rule reads **[T − 10, T + 10)**; stagger clause answered (phase drifts about 3 a cycle) | **deviation 1**, which holds in substance (probe D) with the sentence overstated. **Unlisted: reads post-onset control data (F1)** |
| 6 axis and windows | `mean_lifetime_score`; 60/100/40 | ✓ |
| 7 null: k over [T, T + 10), floored, per fauna; impulse; validation at k = 20 **on income** | ✓ rule; validation moved to V0–V3 | **deviation 2**: the reason holds; the replacement is a manipulation check (F2) |
| 8 power line, r the larger | ✓, with t(n−1) instead of 2 SE | **deviation 3** holds and is stricter (credit) |
| 9 classes A–F | ✓ as written, B over F in the overlap | **deviation 5** holds by B's own text. **E mislabels a co-evolved collapse (F4), a protocol gap to amend** |
| 10 point predictions with confidences | ✓ full | two are near-certain by construction (V3, B shift − base) and one is off by the instrument (base recovery 0 on 10/10) |
| 11 falsifier in the owner's words | ✓, plus a secondary | ✓ |
| 12 depth | ✓ | ✓ |
| 13 committed files | ✓ | add `groups.txt` (F5), before the bulk goes |
| §5: three runs per seed; the control launched first | control = RBT-90's arm | **deviation 4** holds (byte-identity re-derived; no code drift, F7) |
| §8 recovery time "within the control's spread **of the control**" | primary against the pre-event plateau P | **unlisted deviation (F10)** |
| C1: "the arm reports which robots that group held" | not reported | **unlisted omission (F5)** |

**Deviations 1–5 are each forced by a measurement, and each measurement holds.** Deviation 1's sentence needs correcting (probe D). The unlisted ones are F1, F5 and F10; F4's E2 would be a new deviation.

## 5. What I would change, in one list

**Must fix before launch** (none moves the seed rule, n, windows or axis; all are before any data they touch exists):
1. **F1**: onset from pre-onset state only (deaths [T − 10, T) plus age-outs due in [T, T + 10)).
2. **F3**: drop B and S from every sentence, or pre-register a graded structure measure with its range shown on the base.
3. **F4**: no seed leaves R-body; the extinct fauna earns 0; guard over n; split E into E1 and E2, with E2 reported with the falsifier.

**Fix before the bulk is discarded:** F5 (`groups.txt`, the small-group share).

**Report caveats:** the §8 sentence (probe D); V3 is a manipulation check (F2); the null's near-empty channel, with k = 0 seeds stated as R-null = R-shift by construction (F6); the equivalence form beside B (F8); recovery time paired and against its floor, with the three recovery predictions restated (F10).

Credit, plainly:
- the shared-baseline check is exact and reproduces across machines;
- the seed rule was committed before any output and selects nothing;
- the t(n−1) power line is right and stricter than the protocol's;
- the V2 round trip already caught a real bug;
- the cohort cycle is measured, reproduces, and does force a rule change;
- the verbatim quotes are right.
