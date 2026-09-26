# RBT-92 readout adversary: PR #178 (`results/RBT-92-design` at `0dbcdee`)

I attacked the RBT-92 readout for challenge C1 (crowding, group size 4 → 8). The designer's files are not
edited. Every number below comes from committed tables, through `readout.py`'s own parser. No ckpt and no bulk
were read, and no new arm was run.

**Base.** My branch is `0dbcdee` merged with integration `claude/new-session-4cao7d` at `3791af5`, giving merge
commit `6c80b44`. The branch carries all 27 arms and the ten RBT-90 part 2 baselines.

| probe | file |
|---|---|
| round trip and perturbations (fresh worktrees) | `probe_rederive.sh` → `probe_rederive.txt` |
| inputs, platform, the class rule, A/A-like references, recovery, tail, V3 | `probe_readout.py` → `probe_readout.txt` |

## The verdict of this review

- **Class A is computed correctly and follows the pre-registered rule.** It stands as the pre-registered class.
- **Three sentences in the report must change before it merges.** They are F2, F3 and F4.
  - F2: the rule measures the level of the lead, not robustness to the shift.
  - F3: the designed-body cost does not resolve against the pre-registered null.
  - F4: "never left the control's band" is false.
- **Nothing here needs a new run.**
- **The verdict need not wait for RBT-105** (F5), though the wording should carry the fragility that F5 and F6
  measure.

## Findings

### F1 NONE: re-derivation, inputs, and whether any seed was dropped

- **Round trip.** I ran `readout.py` in a fresh worktree of `6c80b44`. The worktree holds no untracked or ignored
  files, and has 0 bulk-shaped files under `runs/RBT-92` and `runs/RBT-90`. The output is **byte-identical** to
  the committed `readout.txt` (sha256 `dc9605fe…`). (`probe_rederive.txt` §0)
- **Perturbations.** Each ran in its own fresh worktree.
  1. **A baseline cell.** I set `runs/RBT-90/forage-2` season 482, designed income, to +1.0.
     - Seed 2's base recovery R-body moved from +0.0177 to +0.0077.
     - The base recovery mean moved from +0.1481 to +0.1471.
     - Designed R-shift moved from −0.0518 to −0.0528.
     - These are exactly the lines that should move, and no others.
  2. **Seed 806 shift arm.** I lowered holistic income by 0.2 across the recovery window.
     - The shift recovery mean moved from +0.1803 to +0.1603, and r from 0.1037 to 0.1313.
     - The class stays A, because 806 was already negative.
  3. **The descent DAG.** I re-parented every post-T holistic birth in `shift-7/lineage-last.txt`.
     - Only the CARRIAGE section changed.
     - V0–V2 still pass, and R-body and the verdict are untouched. (This test also serves F8.)
  4. **A removed arm.** I deleted `shift-806/`.
     - The readout prints `806: … not read`, `seeds read: 9/10`, and a class on 8/9.
     - It exits 0. That is printed, not silent, but a missing arm is not a hard failure.
     - Suggestion only: exit non-zero when the seed rule's exclusion did not fire.
  5. **A substituted seed.** I copied 805's `seasons.txt` into `shift-806`.
     - V0 fails: "730 pre-onset rows differ".
     - The readout refuses to read the shift and exits 1.
- **Inputs** (`probe_readout.txt` P1).
  - **27/27 arm directories were read**, plus 10/10 baselines.
  - Each arm's `config.json` has the right seed, the event at the right season, and the right flag. That is
    `group-size=8`; the cull-k counts; or `holistic=20,conventional=20`.
  - The event season equals `onset.txt`'s T.
  - `events.txt` carries exactly those culls at T and nowhere else.
  - The three k = 0/0 seeds (805, 806, 7) have no cull directory, so the baseline is read.
  - Every table runs from season 0 to 599.
  - No seed was dropped or substituted.

### F2 MUST-FIX (wording): the pre-registered rule measures the lead's level, not robustness to the shift, and class A fires with no shift at all

Evidence: `probe_readout.txt` P3.

**`classify()` applied to arms and windows that contain no crowding:**

| arm, window | R-body | r | positive | class |
|---|---|---|---|---|
| base (no event), recovery | +0.148 | 0.097 | 9/10 | **A** |
| base, before | +0.158 | 0.078 | 9/10 | **A** |
| cull20, recovery | +0.191 | 0.108 | 8/10 | **A** |
| cull (k = 0–10), recovery | +0.158 | 0.135 | 7/10 | F (the sign guard) |
| **shift, recovery (the verdict)** | **+0.180** | **0.104** | **8/10** | **A** |
| **shift − base, paired, recovery** | **+0.032** | **0.073** | 6/10 | **B by the rule's letter** (\|m\| < 0.10, r ≤ 0.10, n ≥ 8), though the F8 equivalence form fails by 0.005 (0.105) |

**Placebo onsets on the baseline alone.**
- I moved a fake T' from T − 200 to T + 40 in steps of 10 and scored base R-body over [T' + 60, T' + 160).
- **The rule returns A on 23/25 placebo onsets.** The two misses are F, at 7/10 positive.

**So the pre-registered class-A rule measures one thing: whether the co-evolved lead is present in the shift arm's
recovery window.** It was present before the event, it is present with no event, and it is present after a random
cull of a third of each fauna. The only readout that measures the *shift* is the paired one, and it does not
resolve. Class A is still the correct pre-registered class; the rule was written that way, and I do not propose
re-scoring. The report must say plainly what it certifies.

**"Survives" carries no information in this ecology.**
- Alive is 60 in every season of [T − 100, T + 200) in all 37 runs.
- It dips below 60 only during the founder crash, in seasons 5–31 of the RBT-90 baselines (which the arms inherit).
- Deaths are refilled by births in the same season (P8).
- The minimum window income is 0.741 holistic and 0.690 designed, against D/E's 0.25.
- Neither body could fail to "survive". "Survives the shift" and "nothing starved" are true, but they are not
  evidence.

**"Holds up" is met by both bodies** (P4).
- The pre-registered bar is R-shift ≥ −r = −0.104.
  - Co-evolved: −0.020 [−0.073, +0.034].
  - Designed: −0.052 [−0.091, −0.013].
  - **Both clear it, even on the interval's lower end.**
- So "holds up" does not tell the two bodies apart.
- **Unregistered sensitivity, for the record only:** measured against each fauna's own paired r, the co-evolved body
  holds up (−0.020 ≥ −0.053) and the designed body does not (−0.052 < −0.039).

**Required in REPORT.md** (headline, §5 and §8, and the ticket summary):
- Say in one sentence that the rule returns A on the no-event baseline, and at 23/25 placebo onsets.
- Say that "holds up" is met by both bodies.
- Replace "survives the shift and keeps its lead" and §8's "the owner's bet reads 'holds up'" with the strongest
  sentence the data support. I propose:

> Under crowding the co-evolved body kept the income lead it already had over the designed body: +0.18
> [+0.08, +0.28] with the shift and +0.15 [+0.05, +0.25] without it, on the same seeds and windows. The
> pre-registered rule scores this class A. The same rule returns A on the no-event baseline, so it certifies that
> the lead persisted, not that the co-evolved body withstood crowding better. Crowding's differential effect on
> the two bodies is +0.03 [−0.04, +0.10]. That is unresolved, and it is the size of what a random cull of a third
> of each fauna does (+0.04, F5). Neither body's income fell by more than r.

Its answer to the brief:
- **Q:** "Could class A fire with no shift?" **A:** Yes. It fires on the base arm itself.
- **Q:** Does the rule measure robustness? **A:** No. It measures the persistence of the pre-existing lead.

### F3 MUST-FIX (wording): the designed body's crowding cost does not resolve against the pre-registered null

- The report and the ticket say that crowding cost the designed body "a little and resolvably: R-shift −0.052
  [−0.091, −0.013]".
- **That is against the no-event control.** The pre-registered null (§7) is the random cull of the same size.
  - **Against it, designed R-null in the recovery window is −0.037 [−0.081, +0.006].** It does not resolve.
  - `readout.txt` already prints this, in the R-null block.
- **Random culls of 1–10 designed robots also lower the designed body's income.**
  - Designed R-cull in the transient is −0.016 [−0.033, −0.000], negative on every seed where anything was culled.
  - In the recovery window the per-seed values are +0.155, −0.065, −0.122, −0.096 and −0.016 (`readout.txt`
    R-cull; P5(a)).
  - A generic perturbation moves this fauna by amounts of the order of −0.05.
- **Required:**
  - The sentence must carry both numbers: "−0.052 against the no-event control, −0.037 [−0.081, +0.006] against
    the pre-registered random-cull null (unresolved)".
  - It must drop "resolvably" as a statement about crowding.
  - The null is weak (F7), which cuts both ways. That is the reason to print both numbers, not to prefer the
    flattering one.

### F4 MUST-FIX (factual): "on six of ten seeds the co-evolved shift arm never left the control's band" is false; "0 on 6/10" is an artifact of the d = 0 hold

Evidence: `probe_readout.txt` P6 and P6(b).

**Every shift seed leaves the band, on both faunas.** Each one has seasons in [T, T + 160) with
|x_shift − x_base| > h, where h = 2 SD as `readout.py` uses it.

| holistic shift, d = 0 seed | first out of the band | seasons out of 160 |
|---|---|---|
| 806 | T+25 | 1 |
| 807 | T+133 | 6 |
| 1 | T+29 | 23 |
| 2 | T+25 | 81 |
| 4 | T+21 | 27 |
| 7 | T+40 | 72 |

**Why d = 0.**
- The recovery rule accepts the first d ≥ 0 at which 20 consecutive seasons stay within h. At d = 0 that window
  is [T, T + 20).
- The two arms are byte-identical at T − 1 (P2).
- `mean_lifetime_score` is the living robots' mean of `score_sum / evals` over each robot's whole life
  (`rabbitstew/ecology.py`, `_record`). A robot alive at T carries all its pre-T seasons.
- The column's lag-1 autocorrelation is 0.69 (median over 20 fauna-seeds; range 0.50–0.90).
- So the paired difference starts at 0 and grows slowly. On the d = 0 seeds it reaches h only at T + 21 or later,
  after the hold is already satisfied.
- **d = 0 records "had not yet diverged", not "recovered".**

**It depends on h** (P6), for the shift arm, holistic:

| h | d = 0 | "none" |
|---|---|---|
| 0.5 SD | 0/10 | 10/10 |
| 1 SD | 1/10 | 6/10 |
| 1.5 SD | 4/10 | 3/10 |
| 2 SD (as registered) | 6/10 | 0/10 |

**Exits are not specific to the shift.** cull20 leaves the band on 10/10 seeds, both faunas. The 1–10-robot culls
leave it on 4/10 holistic and 5/10 designed.

**Required:**
- Strike "never left the control's band" from §4 and from the ticket summary.
- State that the paired recovery-time readout, as registered, returns d = 0 whenever divergence takes more than 20
  seasons to reach h. So "recovered on 10/10, median 0" is not a finding about recovery.
- The numbers stay printed, as registered.
- No recovery claim should be made.
- The prediction "shift holistic none on ≥ 7/10" is still scored wrong by the rule's letter. The report should add
  that the rule could not return "none" for a slow divergence.

### F5 CAVEAT: ecology A/A evidence in the committed data; the +0.032 is a third of a single-seed A/A difference; RBT-105 is not needed for the class

Evidence: `probe_readout.txt` P5.

**A random cull of 1–3 robots is the closest A/A in the committed data.**
- It diverges one fauna from its baseline at T, exactly as a challenge arm does, with an intervention whose
  expected effect on the mean is about 0.
- P2 confirms that the other fauna stays byte-identical to season 599.
- **Per-fauna RMS of x_cull − x_base (the recovery-window mean):**

  | sample | RMS |
  |---|---|
  | k ≤ 3 (n = 7) | **0.090** |
  | all k > 0 (n = 9) | **0.100** |
  | transient window | 0.044 |
  | tail window | 0.137 |
  | cull20, all 20 fauna-seeds | 0.077 |

**The same at the level of R-body** (arm − base per seed, recovery):

| contrast | seeds | RMS |
|---|---|---|
| cull − base | 7 | **0.113** |
| cull20 − base | 10 | **0.108** (mean +0.043) |
| **shift − base** | 10 | **0.102** (mean **+0.032**) |

**What this means:**
- The shift's per-seed differential spread is the A/A-like spread. **The +0.032 is about a third of one seed's
  A/A difference**, and smaller than what a random cull of a third does to the same contrast (+0.043).
- Against RBT-96's warning: the report's intervals are between-seed t intervals of per-seed paired differences.
  Run-to-run noise is already inside them. They are **not** built on an assumed noise figure. The pre-registered
  0.077 was such a figure, and the realised r of 0.104 replaced it.
- **So the intervals stand, but no per-seed value can be read alone.** That includes the Amendment 4
  founding-half table: its 0.011 split is one tenth of a per-seed A/A difference.

**On RBT-105:**
- Its `aa_spread.py` is holistic-only, because the designed fauna is byte-identical across replicates by
  construction.
- Its replicates diverge from season 0. It calls itself an **upper bound** for a challenge arm's recovery window.
- It therefore **cannot** test the designed-body cost (F3), which is the only resolved R-shift. It can only bound
  the holistic per-seed spread that this section already estimates at about 0.09–0.10.
- The class is a level statement, 1.7 × r, and it holds on the base at 23/25 placebo onsets. RBT-105 cannot move it.
- **Recommendation:** record the verdict now with F2–F4's wording and F6's fragility line. Read RBT-105's
  recovery-window RMS against the 0.09–0.10 here as a post-hoc check. If it is much larger (> 0.2 per fauna), the
  between-seed intervals remain valid but the per-seed table should be dropped from the report.

### F6 CAVEAT: the sign guard is met with zero margin

- Shift recovery R-body is positive on exactly 8/10. The guard is ⌈0.8n⌉ = 8.
- The smallest positive seed is 804, at +0.091, below the A/A-like per-seed RMS of 0.10–0.11.
- **The cull arm is a 1–10-robot random perturbation of the baseline** (the baseline itself on the three 0/0
  seeds).
  - It reads **F**, because 804 and 801 change sign under a cull of one holistic robot.
  - The base reads 9/10.
- **Illustration, not a test** (P5(e)). I jittered the per-seed values by N(0, s) and re-applied the rule:

  | s | class A |
  |---|---|
  | 0.05 | 98% |
  | 0.08 | 91% |
  | 0.11 | 80% |

  The rest were F.
- **Required in the caveats:** "a replicate of the shift arms would plausibly return F (roughly 1 in 10 to 1 in 5),
  through the sign guard, not the mean".

### F7 CAVEAT: the null's power, the r line and the equivalence form

- **The r line is correct.** It is sd 0.1450 × t(9) 2.262 / √10 = 0.1037, and the season-noise line is 0.0069.
- **The equivalence form beside B is correct**, but moot for A.
- **The same form on the differential** (P4) is |0.032| + 0.073 = 0.105, which is not < 0.10. So neither an effect
  of crowding on the contrast nor its absence is shown. "Unresolved" is the right word; "the shift did nothing" would
  over-claim.
- **The turnover guard is scored on n = 4.** It compares |−0.051| with an r taken from n = 10 level spread. One of
  the four is seed 1, at −0.195. At n = 4 the t(3) half-width is 0.154, about 1.5 × r.
  - The report already says this is "not evidence of equivalence", and that is right.
  - It should also drop "YES" from the headline list in the ticket summary, or add "(n = 4)" beside it.
- **"Holds up" uses the level r (0.104) as its bar.** That is about twice the paired r for R-shift. See F2 for the
  consequence.

### F8 CAVEAT: V3, and what failed

**The alive half is as the designer says.**
- In season T, cull20 has births = deaths = 20–23 per fauna, against 0–6 in the base.
- End-of-season alive is 60/60 on 10/10 seeds (P8).
- The alive column is structurally blind to a same-season refill.

**The L half also failed, and it is not a column choice.**
- L(T+60), cull20 − base, is −0.042 [−0.106, +0.022].
- A random cull's effect on L is not guaranteed to be negative. The refill births go to the survivors of C0, which
  raises their chance of a living descendant.
- So "the known-present effect" was not known-present for L.
- **The proposed fix ("read the cull in `deaths`") repairs only the manipulation half.** It would pass trivially and
  would not validate L. The next epoch needs an effect L must register, for example a cull of whole lineages.
- REPORT.md §1 says the L half does not resolve. It should add that the fix does not address it.

**Containment holds.**
- Perturbation 3 of F1 changed only the CARRIAGE section.
- In `readout.py`, R-body, the R-contrasts, recovery, the class and the guards read `seasons.txt` only.
- No carriage number can reach an income readout.

**Carriage numbers do enter two sentences,** against §7's "They do not enter any sentence of the report":
- §1 lists the L differences "for the record". That is tolerable as a record, and was added on request.
- **§6 scores "L(T+160) shift − cull within ±0.10" as "right".** That is a reading of an UNVALIDATED number.
  - It must be "not scored (UNVALIDATED, V3)".
  - The same applies to the ticket summary's "Right: … L shift − cull within ±0.10".

### F9 NONE: the tail window

Evidence: P7.

| contrast | tail value | 95% interval | positive |
|---|---|---|---|
| R-body(shift) − R-body(base) | +0.095 | [−0.010, +0.201] | 7/10 |
| **cull20 − base** | **+0.088** | [−0.014, +0.191] | 8/10 |
| the base's own drift, recovery → tail | −0.042 | [−0.092, +0.008] | — |
| R-body(cull) − R-body(base), 7 seeds | RMS 0.156 | — | — |

- The shift's tail divergence is unresolved.
- It is matched by a random cull of a third, and it partly reflects the base drifting down.
- The per-fauna A/A-like RMS in the tail is 0.137, which is larger than in any other window.
- **The report is right not to lean on the tail.** It is reported and not scored, as pre-registered.

### F10 NONE: the platform

Evidence: P2.

- **V0 holds at the level of the raw text**, not only the parsed floats.
  - It covers every pre-T row of all 27 arms, on the five columns shared with the RBT-90 baselines (alive, births,
    deaths, mean and best score).
  - The arms carry two extra columns (`mean_age`, `max_age`) that the baselines lack. That is why a whole-row
    comparison differs, and `readout.py` compares fields.
- The first differing season is exactly T, for both faunas in shift and cull20.
- **After T:** the five faunas with k = 0 in a cull arm are byte-identical to the baseline through **season 599**:
  801 designed, 807 co-evolved, 1 designed, 2 co-evolved and 3 co-evolved.
- So the hive's machines and the RBT-90 machines share the float path through 240 post-T seasons of simulation, not
  only up to T.
- It also confirms that the two faunas' streams are fully separate: one fauna's cull never touches the other. That
  makes R-body a contrast of two independent simulations, so its A/A variance is the sum of the two faunas'.

### F11 CAVEAT: the scoring of the predictions

I checked every row of §6 against `PREREGISTRATION.md` §10 as amended by Amendment 3: the recovery predictions
restated as paired, the cull clause at 0.6, and "V3 passes", "B(T+160)" and "base 0 on 10/10" withdrawn.

**Every number and every right/wrong is as stated, except these:**
- **The L row is scored "right".** It must be "not scored" (F8).
- **"Designed survives on 10/10 (0.85)" and "class D not met (0.9)" are scored "right"**, but neither could have
  failed: alive is pinned at 60, and the minimum income is 0.69 against 0.25 (F2). They should read "right, but
  uninformative in this ecology".
- **"R-body before +0.12" is scored "within its spread, high".** The outcome is +0.158 [+0.080, +0.236], so that
  is fair.

**The wrongs are all owned**, including the mechanism. The scoring is honest. The two fixes above are about
not banking uninformative or unvalidated rights.

---
_Generated by [Claude Code](https://claude.ai/code)_
