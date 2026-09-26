# RBT-100 readout adversary: PR #194 (`results/RBT-100-design` at `afc5e94`)

I attacked the RBT-100 readout for challenge C3 (scarce food, 12 → 6 items). The designer's files are not edited.
Every income number below comes from committed tables, read through RBT-92's `readout.py` parser, as `score.py` and
`placebo.py` read them. The one exception is `probe_own.sh`. It restores the RBT-90 baselines' bulk from
`ckpt/rbt-90-SEED` into scratch and re-runs the designer's `own_table.py` on it. That regenerates a table from bulk,
which README rule 6 allows; it does not read one from a checkpoint. No new arm was run.

| probe | file |
|---|---|
| round trip, open() audit and six perturbations (a fresh worktree of `afc5e94` for each, no bulk) | `probe_rederive.sh` → `probe_rederive.txt` |
| `base-SEED/own.txt` regenerated from the 600/600 checkpoints | `probe_own.sh` → `probe_own.txt` |
| inputs, arithmetic, extinction coding, power, A/A, D, sign guard, established population, founders | `probe_readout.py` → `probe_readout.txt` (P1–P9) |

## The verdict of this review

- **Class A is computed correctly and follows the pre-registered rule. It stands.**
  - It holds under every coding of the extinct seasons I tried, at 10/10 seeds (P3).
  - It holds in ≥ 99.8% of jittered replicates (P7).
- **The re-derivation is clean** (F1).
  - All 30 C3 arms, the 10 baselines and the 10 cull20 arms are read, with no seed dropped or substituted.
  - All ten `own.txt` tables regenerate byte for byte from 600/600 bulk.
- **Two wording findings must change before merge: F2 and F6.**
  - **F2: the arithmetic paragraph.** "+0.017, arithmetic and nothing beyond it" averages two opposite regimes. The
    same arithmetic also brackets its own prediction from +0.12 to +0.32. So the sentence "not a difference in how
    the two bodies responded" is not supported.
  - **F6: D is half-claimed.** "The designed body's budget was exceeded" and "outlasts a bankrupt comparator" are
    class D's sentences, and D missed its guard. The three non-D seeds are not near misses.
- **The rest are caveats** (F3–F5, F7–F10). F8 carries one sentence to fix: an upper bound was cited as evidence in
  the direction it cannot certify.
- **Nothing here needs a new run.** RBT-105's A/A cannot move the class (F7).

## Findings

### F1 NONE: re-derivation, inputs, and the own tables' provenance

Evidence: `probe_rederive.txt`, `probe_own.txt`, and `probe_readout.txt` P1.

**Round trip.**
- The fresh worktree of `afc5e94` holds 0 untracked or ignored files, and 0 bulk-shaped files under `runs/RBT-100`,
  `RBT-92` and `RBT-90`.
- `readout.py`, `placebo.py` and `score.py` reproduce `readout.txt` (sha256 `9ba42773…`), `placebo.txt`
  (`d99b3f20…`) and `score.txt` (`83d0fb9f…`) **byte for byte**, all exiting 0.

**open() audit.**
- `readout.py` reads shift, cull, founders6, base-own, RBT-90 forage and RBT-92 cull20 on all ten seeds.
- `score.py` reads the same set, minus cull20.
- `placebo.py` reads shift, cull, forage and cull20.
- **Every merged C3 arm is read: 10 shift, 10 cull, 10 founders6.** 0 ckpt or bulk paths are opened.

**Perturbations**, one fresh worktree each; I picked the cells:

| # | cell | what moved |
|---|---|---|
| 1 | `base-3/own.txt`, T−10, designed food +1.0 | score.txt only: seed 3's price 0.611 → 0.623, arithmetic +0.1209 → +0.1221. The own-table V0 line prints "1 differ", but the script continues |
| 2 | `founders6-7`, season 59, co-evolved alive 8 → 12 | FOUNDERS 7/7 → 6/6, qualifier "HOLD on 4/10", two score rows |
| 3 | `cull-805`, T+100, co-evolved +0.5 | only seed 805's cull / R-cull / R-null lines, and shift − cull |
| 4 | `RBT-90/forage-806`, T+100, designed +0.5 | base R-body, designed R-shift, paired and residual (+0.0173 → +0.0178) |
| 5 | `shift-806/own.txt`, recovery, designed net_all_ub +0.3 | the OWN line and "below basal 4/10 → 3/10" |
| 6 | `founders6-4/` deleted | readout prints "founders6 not committed" and exits 0; **score.py crashes (exit 1)** |

**Inputs** (P1).
- Every config has the right seed, `shift_at = T` with `food-items=6`, `cull_at = T` with the cull-k string, or 60
  seasons at `items = 6`.
- Each shift arm's `events.txt` has exactly one food.items = 6 row, from T.
- V0 holds on the raw pre-T rows of all 20 shift and cull arms, compared on the baseline's columns, and on the
  pre-T own rows.
- In `own.txt` (base and shift), alive equals `seasons.txt`'s alive, and starved + aged equals its deaths, on every
  cell from season 1. **0 problems.**

**Own tables from 600/600 bulk.**
- Every `ckpt/rbt-90-SEED` MANIFEST reads 600/600 with no inconsistency note.
- `own_table.py` on each restored run reproduces the committed `base-SEED/own.txt` **byte for byte on 10/10 seeds**:
  1200 rows each, to season 599, reconciled on 1198/1198 cells.

**Suggestions only** (RBT-92 F1 and RBT-99 F1 made the same kind):
- A missing founders6 arm is printed by the readout but crashes `score.py`.
- The own-table V0 mismatch is printed but not enforced.
- `placebo.py` hard-codes the shift arm's D count at 7, as RBT-99's hard-coded 4.

### F2 MUST-FIX (wording): the arithmetic does not show that the paired effect is "nothing beyond" price

Evidence: `probe_readout.txt` P2 and P3.

**1. The +0.017 residual averages two opposite regimes.**

| designed fauna | seeds | paired effect | residual over the arithmetic |
|---|---|---|---|
| extinct in the recovery window | 801, 805, 806, 1, 3 | +0.226 [−0.044, +0.496] | **+0.090** [−0.125, +0.306] |
| survived | 804, 807, 2, 4, 7 | +0.051 [−0.080, +0.181] | **−0.056** [−0.176, +0.065] |

- The extinct seeds carry **82%** of the summed paired effect.
- Where the designed fauna survived, the paired effect is **about half of what the arithmetic predicts**.
- "The paired effect is the price arithmetic" is true only of the ten-seed average, not of the seeds.

**2. The arithmetic's own "unchanged population" is not one that can exist.**
- `score.py` itself prints that an unchanged designed gait nets +0.08 to +0.18, **below the 0.25 basal cost on 10/10
  seeds.** A population like that cannot persist.
- The +0.121 prediction nonetheless keeps it alive on the axis at exactly base − price.
- Now score the unchanged designed population as the same arithmetic implies, extinct and so 0 under the 13:10
  coding, for the whole recovery window. The prediction becomes **+0.316** [+0.242, +0.390], and the residual
  **−0.178 [−0.292, −0.065], which resolves.**
- The truth for an insolvent unchanged population lies between these two, depending on when it would die out.

**So the arithmetic brackets the paired effect, from +0.12 to +0.32. It does not decide the sign of any response
difference.** The observed +0.138 sits near the "unchanged but alive" end. Yet the designed fauna did *not* stay
unchanged:
- It survived on 5/10 seeds that its arithmetic calls insolvent.
- On 3 of them it was solvent, with survivors' own net +0.31 to +0.35 against an unchanged +0.11 to +0.18.

**Required** in the headline, §3 and the ticket summary:
- Replace "What the event did: arithmetic, and nothing beyond it".
- Replace "The paired effect is the price arithmetic of two gaits at half the density, not a difference in how the
  two bodies responded".
- Replace "Net of its own price each body recovered a similar part of it" (see F4 on "similar").

I propose:

> Two unchanged populations that stayed alive at their halved gross would have diverged by +0.12 [+0.07, +0.18]
> (other pre-T windows, the axis scale and an early-season density check give +0.11 to +0.15). The observed paired
> effect is +0.14 [+0.01, +0.27], 8/10. The residual, +0.02 [−0.09, +0.13], averages +0.09 on the five seeds where
> the designed fauna went extinct, which carry 82% of the effect, and −0.06 on the five where it survived. The same
> arithmetic says an unchanged designed gait nets below basal on every seed. Scored as the extinct population that
> implies, the unchanged prediction is +0.32, and the designed fauna did better than that (residual −0.18
> [−0.29, −0.07]). The arithmetic therefore brackets the paired effect without deciding whether either body
> responded better. The design could not have detected a response difference below about 0.15 (F4).

### F3 CAVEAT: how the arithmetic is built, and whether income is linear in food density

Evidence: P2.

**Construction.**
- `score.py` §1 takes `base-SEED/own.txt` over `range(T−40, T)`, so pre-onset rows only.
  - food and work are means over each season's survivors;
  - price = food / 2, with work unchanged;
  - the paired prediction is price(designed) − price(co-evolved).
- **The form is §4's, registered at `c456dd0` (13:03 UTC), before any arm.** It said "the typical designed robot is
  at or below basal after the shift".
- The per-seed numbers were computed by code committed at `3f8dfc7` (19:40), after the arms merged (19:30). The
  inputs are pre-onset, so this is legitimate. It should be labelled "computed after the arms from pre-onset data".

**Choices varied** (paired prediction, then residual):

| variant | prediction | residual |
|---|---|---|
| survivors' food over [T−10, T) | +0.127 | +0.011 |
| over [T−20, T) | +0.125 | +0.013 |
| over [T−40, T) (the report's) | +0.121 | +0.017 |
| over [T−60, T) | +0.119 | +0.019 |
| over [T−100, T) | +0.113 | +0.025 |
| price rescaled by axis / own-net (per seed 0.94–1.09) | +0.146 | −0.008 |
| empirical density response (below) | +0.116 [+0.001, +0.231] | +0.023 |

**The spread is +0.113 to +0.146, and the residual −0.008 to +0.025.** The window was not tuned: every choice leaves
the residual unresolved.

**Linearity.**
- **Pre-onset data cannot test it.** Alive is 60 in every season of [T−100, T) for both faunas, the group size is
  4, and there are 12 items throughout.
- **The only direct test is the first seasons after T.** There the same robots eat at six items, before selection
  can act. Gross food per survivor, shift ÷ base, over [T, T+3):
  - co-evolved **0.488** (per seed 0.44–0.52);
  - designed **0.497** (per seed 0.36–0.58; 805 and 806 sub-linear, 1, 2 and 7 super-linear);
  - [T, T+1): 0.49 and 0.46; [T, T+10): 0.52 and 0.51.
- **Two mechanics of the code support linearity** (§3.1):
  - food regrows instantly at a fresh uniform spot;
  - groups are within-fauna, so one fauna's extinction does not change the other's competition.
- **Linear is defensible on average.** Per seed, the designed response departs from 0.5 by up to ±0.15, and that
  widens the per-seed arithmetic.

### F4 CAVEAT: matched-null power of the residual; "unresolved" is honest, "similar" is not

Evidence: P4.

- **The design could not detect the residual.** Its own sd is 0.153, so the t(9) half-width is 0.110. The minimum
  detectable residual at 5% two-sided and 80% power, n = 10, is **0.152**, about **1.3× the entire arithmetic
  effect** (+0.121).
- **Matched nulls with no price** (paired R-body against base, recovery):
  - cull: sd 0.066, MDE 0.066;
  - cull20: sd 0.104, MDE 0.103.
  - The residual's sd is larger than either because extinction adds between-seed variance (F2).
- **"Unresolved" is the right word.** "Similar part of its price" (23% against 16%, a difference of +0.017) and
  "Neither body can be said to have responded better" read as equivalence, which the design cannot show.

**Required:** replace "similar" with "the difference, +0.017 [−0.092, +0.127], is unresolved; this design could
detect only a difference above ≈ 0.15".

### F5 CAVEAT: extinction coding, and what the extinct seeds carry

Evidence: P3.

**Coding.**
- `Arm.x` sets income 0 from the first alive = 0 season on, per RBT-92 Amendment 2 and the 13:10 ruling. It is
  applied in every window and test.
- Recovery seasons at 0: 801 14/100, 805 44, 806 82, 1 14, 3 55.

**Sensitivity:**

| extinct seasons coded as | paired | residual | shift R-body (class) |
|---|---|---|---|
| **0 (registered)** | **+0.138** [+0.005, +0.271] | +0.017 | +0.286, 10/10, A |
| unchanged-gait net (RBT-99 F5's alternative) | +0.115 [−0.000, +0.231] | −0.006 | +0.263, 10/10, A |
| −0.25 | +0.190 [+0.012, +0.369] | +0.070 | +0.338, 10/10, A |
| dropped (living seasons only) | +0.061 [−0.022, +0.143] | −0.060 | +0.209, 10/10, A |
| extinct seeds excluded (post hoc, n = 5) | +0.051 [−0.080, +0.181] | −0.056 | — |

- **The class does not depend on the coding.**
- **The paired contrast's resolution does.** Its lower bound is above 0 only under the 0 and −0.25 codings.
- The report should say that "+0.138, lower bound +0.006" is the registered coding's figure, and that 82% of it sits
  on the extinct seeds.

**"Falls below basal at an unchanged gait"** is a prediction, not a post-hoc explanation. §4 said it before any arm
(designed at 14 kJ: net − basal −0.06 to +0.09; at 29 kJ: −0.28 to −0.13). Only the per-seed values are post-arm,
from pre-onset data (F3). What was not predicted is that the designed fauna would survive on 5/10 and stay solvent on
3/10 regardless. That belongs beside the sentence (F2).

### F6 MUST-FIX (wording): the report half-claims class D

Evidence: P6.

**Three sentences use D's language for an A verdict.**
- REPORT headline and §4: "The designed body's budget was exceeded, as the protocol expected". That is class D's
  definition, verbatim from §5: "the challenge exceeded the designed body's energy budget".
- REPORT §4: "the class is A, and it is read as 'outlasts a bankrupt comparator' in substance". That is D's sentence.
- The ticket summary and REPORT §5: "D, my mode, fell one seed short".

**D missed its registered guard, and the misses are not near.**

| seed | recovery income | margin over 0.25 | min alive | margin over the floor of 12 |
|---|---|---|---|---|
| 804 | +0.395 | +0.145 | 31 | +19 |
| 807 | +0.444 | +0.194 | 25 | +13 |
| 7 | +0.416 | +0.166 | 60 | +48 |

- Transient incomes on these seeds are ≥ +0.458.
- **Jittering the income triggers** by the A/A-like per-fauna spread gives D ≥ 8/10 in 5.4% of draws at N(0, 0.077)
  and 23% at N(0, 0.11).
- **Four of the seven D seeds fire on the floor alone,** with living-mean recovery income > 0.25: 801, 1, 2 (min 3)
  and 4 (min 7).
- **Binomially,** at a per-seed rate of 0.7, 8/10 or more has probability 0.38. So "one short" is not evidence that D
  was the truth. Given the per-seed margins, the designed body was solvent on three seeds by clear margins.

**Required:**
- Drop "the designed body's budget was exceeded" as a class-level sentence.
- Use the A sentence the rule picks: "outlasts, not holds up (co-evolved R-shift < −r)".
- Where the D test's per-seed result matters, say it per seed:

> D's test fired on 7/10 seeds (extinct on 5, below the floor on 2 more). On 804, 807 and 7 the designed fauna was
> solvent by clear margins (min alive 25–60, recovery income +0.40 to +0.44). On the seven D seeds the class-A lead
> is over a bankrupt comparator (forbidden readings 2 and 12). On the other three it is not.

- "One short of its 8/10 guard" may stay as arithmetic, with "the three passes are not near misses" beside it.

### F7 CAVEAT: the A/A-like spread, on the right scale, and the paired sign guard

Evidence: P5 and P7.

**Per-fauna RMS (recovery):**
- cull − base: co-evolved 0.101 (n = 7, k > 0), designed 0.076;
- cull20 − base: co-evolved 0.096, designed 0.051.

**On the scale of the paired R-body:**
- cull − base: RMS 0.071, mean +0.033;
- cull20 − base: RMS 0.108, mean +0.043;
- pooled: **0.091**, which gives an SE of a ten-seed mean of 0.029.

**Findings.**
- **The report's A/A reference is on the wrong scale.** It uses R-cull20's per-fauna RMS, 0.077 (`placebo.txt`), to
  judge a paired R-body. The paired scale is 0.091–0.108.
- **The mean +0.138 is outside an A/A spread**: 4.8 SE. The A/A contrasts' own means are +0.03 to +0.04. The residual
  +0.017 is 0.6 SE.
- **The lower bound +0.006 is set by between-seed heterogeneity, not A/A noise.** The paired sd is 0.186 against an
  A/A of 0.09, and the heterogeneity is extinction (F2).
- **Four paired per-seed values sit within one paired A/A unit of 0:** 807 +0.003, 1 −0.048, 4 +0.032 and 7 −0.081.
- **Jittered by N(0, 0.05–0.11), the paired contrast keeps ≥ 8/10 positive in only 46–49% of draws.**
  - "Positive on 8/10 (margin 0)" should say that a replicate would be a coin flip on that count.
  - The class's own guard (shift R-body 10/10) holds in ≥ 99.8%.
- **RBT-105 cannot move the class.** It can only confirm the per-seed reading above.

### F8 CAVEAT: "the established population paid its way", and founders6

Evidence: P8 and P9, and `probe_rederive.txt` perturbation 2.

**Survival or income?**
- The registered HOLD (Amendment 2 cont., item 2) is min alive ≥ 12 **and** survivors' own net ≥ 0.25.
- The alive leg is 60 on 10/10 seeds, which is uninformative (lesson 5).
- So the claim is **income-based, and it holds.** Starvation is small:
  - starved share of the recovery window's runners, shift 1.2–2.5%, against base 0.7–1.5%;
  - survivors' own net +0.50 to +0.66;
  - all-runner value if the starved ate nothing, approximately **+0.48 to +0.65**. This is not a strict bound: it
    uses the survivors' mean work.
- **But the report's supporting clause is backwards.** It says that own net "over everyone who ran each season …
  (an upper bound) stayed above basal … on 10/10".
  - `own_table.py`'s own docstring: net_all_ub < 0.25 means below basal "for certain". Above 0.25 it certifies nothing.
  - **Required:** replace it with the starved share and the approximate all-runner value above, or drop it.

**Founders6.**
- **It was pre-registered** (Amendment 2, `71946d1` 14:05 and `b5b1c80` 14:06, pre-data). The rule is HOLD if ≥ 12
  co-evolved alive at season 59, and the contrast prints only where the founders FAIL and the established fauna HOLDS.
- The readout applies it as registered.
- **The conditioning:**
  - The established fauna HOLDS on 10/10, so "contrast on 7/7" is just "founders FAIL on 7/10" restated. It is not a
    second outcome, and it should be reported as the latter.
  - Founder extinction does not refill, so founders FAIL is informative, unlike alive = 60.
- **The founders' 7/10 is 6 clear and 1 borderline.**
  - 801 and 805 are extinct by seasons 20 and 35; 806, 807, 2 and 3 are down to 0–1 by season 40 and 0 by 55.
  - **Seed 7** has 8 alive at 59, but it is bootstrapping: 1 alive at season 40, 11 at 54, 7–9 over 55–59. The
    season-59 threshold cuts a recovering population, and 8 → 12 flips the seed (perturbation 2).
  - Seed 1's founders fell to 4 at season 15 and reached 60.
  - **Required:** "random co-evolved founders failed at six items on 7/10 seeds (on seed 7, 8 alive and rising at
    the season-59 cut)".

### F9 CAVEAT: the scoring is honest, with two corrections

Evidence: `score.txt`, and the per-seed R-body in P7's input.

**What checks out.**
- Every binary row matches its registered threshold and probability, including Amendment 3's restated recovery rows
  (0.8 and 0.6, not §8's 0.85 and 0.7).
- The rows made after the adversary's probes are labelled.
- The Brier sums reproduce: 0.098 over 19, and 0.708 multiclass.

**(a) The R-body recovery point was registered "+0.22 … where both survive".**
- `score.py` scores it on all ten seeds, giving +0.286.
- On the five seeds where both survived, it is **+0.196** [+0.116, +0.276], close to the prediction.
- The all-ten figure is inflated by the extinct seeds (806 +0.515, 805 +0.451, 3 +0.374).
- REPORT §5's "I priced both bodies' shocks too high" should use the registered subset for this row.

**(b) "Every point sits inside its registered range" needs two exceptions.**
- R-body per seed is 9/10 inside: 806 is at +0.515, against a range of −0.05 to 0.50.
- The co-evolved min alive sits at its range's top, as the report says.

### F10 CAVEAT: lessons 1–6, placebo and the guards

- **Lesson 1 is observed.** `placebo.py` is RBT-99's with C3's paths and D = 7, and nothing else differs
  (`diff runs/RBT-99/placebo.py runs/RBT-100/placebo.py`). `placebo.txt` is byte-identical. A fires on the base and
  on 23/25 placebo onsets, and the report says so.
- **Lesson 2 is observed.** Paired event − base and event − cull (+0.106 [−0.045, +0.256], unresolved) are both
  printed.
- **Lesson 3:** see F2 to F4.
- **Lesson 4 is observed.** The recovery rules are printed and scored as registered, and labelled "not a recovery
  claim".
- **Lesson 5 is observed** for co-evolved alive = 60. It applies to the established HOLD's alive leg too (F8).
- **Lesson 6 is observed** in `score.txt` ("NOT SCORED (UNVALIDATED, V3)").
  - But REPORT §1 prints "designed Lc shift − base is −0.22 to −0.30 at every horizon … not read".
  - **Required:** drop the number. An UNVALIDATED value printed in the report invites the reading the lesson forbids.
- **RBT-92 F6 (sign guard):** 10/10, margin +2, robust under jitter (P7). The paired count is fragile (F7).
- **RBT-92 F7 (null power and the turnover guard):**
  - The turnover guard was declared not interpretable a priori (Amendment 2), and it enters no sentence.
  - It is scored on n = 7 co-evolved k > 0 seeds.
  - The co-evolved R-null (−0.475) is the price, which no random cull carries, as the report says.

---
_Generated by [Claude Code](https://claude.ai/code)_
