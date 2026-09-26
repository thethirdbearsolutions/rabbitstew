# RBT-100 report: epoch C3, scarce food (12 → 6 items) on ten founding populations

*Written at 20:00 UTC on 2026-09-26, after the coordinator's 19:35 wake. It applies the six lessons from the RBT-92 and RBT-99 readout adversaries and the 18:45 and 19:05 rulings. **Amended at 20:25 UTC** after the readout adversary (PR #199, `runs/RBT-100/readout-adversary/`) and the coordinator's 20:06 ruling (CLEAR-WITH-AMENDMENTS, wording only), and with programme lesson 7. The registered readout is unchanged.*

**Verdict (RBT-89 §9, as pre-registered): class A, co-evolved wins. It stands.**
- **The numbers:** R-body in the recovery window of the shift arm is **+0.286** (95% t(9) [+0.191, +0.382]), positive on 10/10 seeds, with r = 0.095. A's sign guard needs 8/10, so its margin is +2 seeds. It holds under every coding of extinct seasons and in ≥ 99.8% of jittered replicates (adversary P3, P7).
- **The falsifier,** "the designed body wins on the held-out challenge", is not met. C and E2 are reached on 0/10 seeds.
- **The sentence the rule selects:** "outlasts, not holds up (co-evolved R-shift < −r)". Co-evolved R-shift is −0.444 against −r = −0.095.

**What class A certifies here: nothing about the shift.** The rule returns A with no event: on the no-event baseline's own recovery window (+0.148, 9/10) and on **23/25 placebo onsets** (`placebo.txt` P3). The class reads the level of the co-evolved lead (lesson 1). The printed class-A text "both surviving above the floor" is a defect in my C3 `verdict_text`: it is false on the seven seeds below. It is reported here, not patched after the data.

**D's test, per seed (adversary F6).** D's test fired on 7/10 seeds: the designed fauna went extinct on 5 (801, 805, 806, 1, 3) and fell below the floor of 12 on 2 more (2, 4). On 804, 807 and 7 the designed fauna was **solvent by clear margins**: min alive 25–60, recovery income +0.40 to +0.44. Those three are not near misses. On the seven D seeds the class-A lead is over a bankrupt comparator (forbidden readings 2 and 12); on the other three it is not. Four of the seven fire on the floor alone.

**What the event did: the arithmetic brackets it, and does not decide it (lesson 3, lesson 7; adversary F2; `score.txt` §1).**

> Halving the items halves every body's gross food and leaves its work bill where it was. The per-seed arithmetic
> below was computed after the arms, from pre-onset data only (the form is §4's, registered before any arm). Before
> T the designed body ate 1.22–1.50 items a season against the co-evolved body's 1.02–1.35, so the shift takes more
> from the designed body: a price of 0.70 against 0.58. At an unchanged gait the designed body's season net falls to
> **+0.08 to +0.18, below the 0.25 basal cost on 10/10 seeds**; the co-evolved body's falls to **+0.29 to +0.59,
> above basal on 10/10**.
>
> Two unchanged populations that stayed alive at their halved gross would have diverged by **+0.12 [+0.07, +0.18]**
> (other pre-T windows, the axis scale and an early-season density check give +0.11 to +0.15). The observed paired
> effect is **+0.14 [+0.01, +0.27], 8/10**. The residual, +0.02 [−0.09, +0.13], averages **+0.09 on the five seeds
> where the designed fauna went extinct, which carry 82% of the effect, and −0.06 on the five where it survived**.
> The same arithmetic says an unchanged designed gait nets below basal on every seed. Scored as the extinct
> population that implies, the unchanged prediction is **+0.32**, and the designed fauna did better than that
> (residual −0.18 [−0.29, −0.07]). **The arithmetic therefore brackets the paired effect, +0.12 to +0.32, without
> deciding whether either body responded better.** The design could not have detected a response difference below
> about 0.15 (F4).

(The last paragraph is the adversary's F2 text, adopted as written, as the ruling allows.)

**What C3 set out to test, answered on its own terms: survivorship at six items.**
- **The established co-evolved population paid its way at six items on 10/10 seeds, by income** (adversary F8). The registered HOLD's alive leg is 60 on every seed and is uninformative (lesson 5); its income leg carries it:
  - survivors' own net +0.50 to +0.66 per seed in the recovery window;
  - starvation was small: the starved share of each recovery season's runners was 1.2–2.5% on the shift arm, against 0.7–1.5% on the base;
  - the all-runner net, if the starved ate nothing, is approximately +0.48 to +0.65. That is an approximation using the survivors' mean work, not a strict bound;
  - it tripped no D trigger on any seed;
  - its pre-onset gait's arithmetic predicts this (unchanged net +0.29 to +0.59). It is survivorship of standing morphology and gait, not adaptation (§3; depth about 5 events).
- **Random co-evolved founders at six items FAIL on 7/10 seeds** (founders6, pre-registered in Amendment 2 before any data; fewer than 12 alive at season 59) and HOLD on 3/10 (804, 1, 4). On seed 7 the founders are 8 alive and rising at the season-59 cut (1 at season 40, 11 at 54), so that FAIL is borderline. Since the established fauna holds on 10/10, the readout's "contrast on 7/7" restates founders FAIL 7/10; it is not a second outcome. Founder extinction does not refill, so founders FAIL is informative, unlike alive = 60.
- **The designed fauna** went extinct on 5/10 seeds, at T+78 to T+146, failed D's test on 7/10 (per seed above), and stayed solvent on 3/10 (804, 807, 7) with survivors' own net +0.31 to +0.35, where an unchanged gait would have earned +0.11 to +0.18. That it survived on 5/10 and stayed solvent on 3/10, against an arithmetic that calls it insolvent on 10/10, was not predicted (F5).
- **Co-evolved alive = 60 in every season is not evidence** (lesson 5): its deaths refill within the season. Designed extinction is informative, because extinction does not refill.

Everything below re-derives from committed files: `readout.txt` (the registered readout), `placebo.txt` and `score.txt`.

## Provenance

| what | where |
|---|---|
| pre-registration | `runs/RBT-100/PREREGISTRATION.md`: posted 13:06 UTC; Amendments 1 (13:39), 2 (14:06, answering adversary round 1; continued 14:07 on P2) and 3 (14:31); all before any arm existed; design approved by the coordinator at 14:55 |
| seeds, onsets | RBT-92's: all ten, 10/10 read; `runs/RBT-92/onset.txt`, T = 352–382. Seed 806 carries RBT-92's drift FLAG |
| baselines | the ten RBT-90 part 2 arms, `runs/RBT-90/forage-SEED/` |
| arms | 10 shift, 10 cull, 10 founders6 (`runs/RBT-100/{shift,cull,founders6}-SEED`, `cull-k-SEED.txt`), run by the hive and merged by 19:35. cull20 is RBT-92's (`runs/RBT-92/cull20-SEED`), the same run, as registered (§1.3) |
| baseline own-net tables | `runs/RBT-100/base-SEED/own.txt`, written by `own_table.py` from the baselines' bulk (restored with `scripts/durable.sh restore … rbt-90-SEED`), as §10 registers. Death counts reconcile on 1198/1198 cells per seed. Pre-T rows equal the shift arms' `own.txt` on 10/10 seeds (`score.txt`, "V0 on the own tables") |
| readout | `readout.txt`, from `python runs/RBT-100/readout.py` on integration `b331cf85` plus this branch |
| placebo and paired readouts | `placebo.txt` from `placebo.py`: RBT-99's `placebo.py` with C3's paths and D count, nothing else changed (the RBT-92 readout adversary's P3/P4) |
| arithmetic and scoring | `score.txt` from `score.py`, committed files only |
| round trip | `roundtrip.txt`: in a worktree of `d32161cd` holding no bulk, `readout.py`, `placebo.py` and `score.py` reproduce `readout.txt`, `placebo.txt` and `score.txt` **byte for byte**. Perturbing one cell (`shift-3/seasons.txt`, season 450, holistic income +0.5) moves 11 lines of each of `readout.txt` and `score.txt`, including r (0.0954 → 0.0957), seed 3's recovery R-body (+0.3737 → +0.3787) and the mean (+0.2862 → +0.2867) |
| tests | `python -m pytest -q`: 289 passed |

## 1. Validation (V0–V3)

- **V0, V1 and V2 pass on 10/10 seeds.** C3-V1 also passes 10/10: `food.items = 6` from T on every shift arm.
- **V3 fails, as it did on RBT-92 and RBT-99, on the same cull20 arms.**
  - The alive dip is 0 on 10/10 seeds, because freed slots refill within the season.
  - Holistic L(T+60), cull20 − base, is −0.042 [−0.106, +0.022].
  - So **carriage is UNVALIDATED**, and the L row is "not scored (UNVALIDATED, V3)" (lesson 6). No carriage value is quoted here (lesson 6; adversary F10).

## 2. The class, and what it measures (lessons 1 and 2)

| | before | transient | **recovery** | tail |
|---|---|---|---|---|
| base R-body | +0.158 [+0.080, +0.236] 9/10 | +0.169 | +0.148 [+0.051, +0.245] 9/10 | +0.106 |
| shift R-body | +0.158 (V0) | +0.214 [+0.138, +0.289] 10/10 | **+0.286 [+0.191, +0.382] 10/10** | +0.424 [+0.267, +0.580] 10/10 |
| cull R-body | +0.158 | +0.160 | +0.181 [+0.059, +0.302] 8/10 | +0.214 |

- **The rule without the event:** class A on the base arm's before, recovery and tail windows, and on 23/25 placebo onsets. The two exceptions are T+20 and T+30, both F (`placebo.txt` P3).
- **The event against the control (paired, recovery, n = 10):**
  - shift − base R-body **+0.138 [+0.006, +0.271], 8/10**, under the registered coding of extinct seasons as 0. That coding matters to the lower bound (adversary F5): with extinct seasons dropped it is +0.061 [−0.022, +0.143], unresolved; coded at the unchanged-gait net, +0.115 [−0.000, +0.231]; coded −0.25, +0.190 [+0.012, +0.369]. The class is A under all four. 82% of the registered figure sits on the five designed-extinct seeds;
  - co-evolved R-shift **−0.444 [−0.494, −0.395]**, 0/10;
  - designed R-shift **−0.583 [−0.682, −0.483]**, 0/10 (extinct seasons at 0).
- **The event against the registered null (shift − cull, n = 10; no cull emptied a fauna):**
  - R-body **+0.106 [−0.045, +0.256], 7/10, unresolved**;
  - co-evolved R-null −0.475 [−0.542, −0.409];
  - designed R-null −0.581 [−0.688, −0.474].

  C3's turnover guard was declared not interpretable a priori (Amendment 2). Its R-null is the price of the halved density, which no random cull carries: R-cull is +0.031 (co-evolved) and −0.002 (designed).
- **Sign guards:** R-body(shift) is positive on 10/10 against the 8 needed (margin +2). The paired contrast is positive on 8/10 (margin 0). D's test counts 7/10 against 8 (margin −1).
- **The A/A spread, on the paired scale (adversary F7).** `placebo.txt`'s 0.077 is a per-fauna RMS and is the wrong scale for a paired R-body. On the paired scale the A/A-like RMS is 0.071 (cull − base) to 0.108 (cull20 − base), pooled **0.091**.
  - **The mean paired effect, +0.138, is 4.8 standard errors outside an A/A spread** (SE of a ten-seed mean 0.029). Its lower bound near 0 comes from between-seed heterogeneity (sd 0.186, which is extinction; F2), not from A/A noise.
  - **The 8/10 paired count would be a coin flip on replication:** four per-seed values (807, 1, 4, 7) sit within one paired A/A unit of 0, and jittered by N(0, 0.05–0.11) the count keeps ≥ 8/10 in only 46–49% of draws. The class's own guard (shift R-body 10/10) holds in ≥ 99.8%.
  - **RBT-105's A/A spread cannot move the class**; it can only confirm the per-seed readings above. D's 7/10 is read per seed (headline), not as "one short".

## 3. Arithmetic first (lesson 3): both nets, side by side

**Source.** Pre-onset seasons [T−40, T) of each seed's baseline `own.txt` (`score.txt` §1). "Unchanged" means food/2 − work, a body's season net at the same gait with half the items. **The per-seed values were computed after the arms, from pre-onset data only**; the form (halve the gross, keep the work) is §4's, registered at `c456dd0` before any arm (adversary F3).

**Variants** (adversary F3, P2): survivors' food over [T−10, T), [T−20, T), [T−60, T) or [T−100, T), price rescaled to the axis, or an empirical density response give a paired prediction of **+0.113 to +0.146** and a residual of −0.008 to +0.025; every choice leaves the residual unresolved. **Linearity** cannot be tested before T (12 items and alive 60 throughout). In the first seasons after T, [T, T+3), gross food per survivor, shift ÷ base, is **0.488** (co-evolved) and **0.497** (designed), per seed 0.36–0.58: linear on average, with per-seed departures of up to ±0.15 on the designed side.

| seed | co-evolved food / work / price / unchanged | designed food / work / price / unchanged |
|---|---|---|
| 801 | 1.057 / 0.236 / 0.528 / +0.292 | 1.494 / 0.573 / 0.747 / +0.174 |
| 804 | 1.221 / 0.205 / 0.610 / +0.405 | 1.365 / 0.566 / 0.682 / +0.116 |
| 805 | 1.024 / 0.121 / 0.512 / +0.391 | 1.453 / 0.606 / 0.727 / +0.121 |
| 806 | 1.082 / 0.199 / 0.541 / +0.342 | 1.497 / 0.643 / 0.748 / +0.105 |
| 807 | 1.150 / 0.148 / 0.575 / +0.427 | 1.433 / 0.605 / 0.716 / +0.111 |
| 1 | 1.345 / 0.081 / 0.673 / +0.591 | 1.356 / 0.520 / 0.678 / +0.158 |
| 2 | 1.148 / 0.154 / 0.574 / +0.420 | 1.421 / 0.597 / 0.711 / +0.113 |
| 3 | 1.156 / 0.183 / 0.578 / +0.395 | 1.221 / 0.531 / 0.611 / +0.080 |
| 4 | 1.178 / 0.144 / 0.589 / +0.445 | 1.393 / 0.584 / 0.696 / +0.112 |
| 7 | 1.154 / 0.096 / 0.577 / +0.481 | 1.300 / 0.475 / 0.650 / +0.175 |

**Nets, side by side.** Recovery window, axis scale; net = R-shift + price.

| | price | R-shift | **net** | share of price recovered | conditioning |
|---|---|---|---|---|---|
| co-evolved | 0.576 | −0.444 [−0.494, −0.395] | **+0.131 [+0.078, +0.185] 10/10** | 0.23 (per seed 0.05–0.42) | a survivors' lifetime mean; the starved share of each recovery season's runners is 1.2–2.5% (adversary F8) |
| designed | 0.697 | −0.583 [−0.682, −0.483] | **+0.114 [+0.018, +0.210] 8/10** | 0.16 (per seed −0.16 to +0.43) | pinned by extinction (axis 0) on the 5 extinct seeds; survivor-conditioned elsewhere |

- **The difference, +0.017 [−0.092, +0.127], 5/10, is unresolved; this design could detect only a difference above ≈ 0.15** (the minimum detectable residual at 80% power, n = 10, is 0.152, about 1.3× the whole arithmetic effect; adversary F4). It is identical to the residual of the paired contrast over its alive-arithmetic, as it must be. It is not a finding of equivalence.
- On the own-net scale (season means over survivors, shift − base) the nets are +0.105 (co-evolved) and +0.137 (designed).
- **Lesson 7: the arithmetic is a bracket, not a point.** The alive end predicts +0.121 and the insolvent end, the unchanged designed fauna scored extinct as its own arithmetic implies, +0.316 [+0.242, +0.390]. The observed +0.138 sits between them; against the alive end the residual is +0.017 (unresolved), against the insolvent end −0.178 [−0.292, −0.065] (the designed fauna did better than an unchanged, insolvent one). The residual's split: +0.090 [−0.125, +0.306] on the five designed-extinct seeds and −0.056 [−0.176, +0.065] on the five where it survived (adversary P2).

## 4. Readings owed by the pre-registration

- **C3's claim line (§2, C3), verbatim:**
  > **Claim tested:** as C2, survivorship at a boundary, here the bootstrap line for food; whether an
  > established population holds where random founders could not. Not the owner's contest claim.
  - Read per seed on founders6: founders FAIL on 7/10 seeds (seed 7 borderline: 8 alive and rising at the season-59 cut) and HOLD on 3/10. Because the established fauna holds on 10/10, the readout's "contrast on 7/7" restates founders FAIL 7/10.
- **"Robust" means survivorship of standing morphology and gait**, not adaptation during the shift (§3, RBT-91 option A). Depth after T is about 5 events on both arms (DEPTH: 5.0 against 5.0), so the co-evolved body "survives" or "is sorted".
- **The sentence is:**

  > At half the food the established co-evolved population paid its way by income on every seed, as its pre-onset
  > gait's arithmetic says it would. Random co-evolved founders at six items failed on 7 of the 10 seeds (on seed 7
  > with 8 alive and rising at the cut). The designed fauna went extinct on 5 seeds and fell below the floor on 2
  > more; on 3 it stayed solvent by clear margins, against an arithmetic that called an unchanged gait insolvent on
  > all 10. The arithmetic brackets the paired effect without deciding whether either body responded better; the
  > difference in their nets, +0.017, is unresolved at a design that could see only ≈ 0.15.
- **This is one body's cheapness at a density, not the owner's contest.** Class A adds nothing to it.
- **Forbidden readings.**
  - 2 and 12 apply **per seed**: on the seven D seeds the class-A lead is over a bankrupt comparator; on 804, 807 and 7 it is not. The class sentence is A's: "outlasts, not holds up".
  - "Holds up" is not earned: co-evolved R-shift −0.444 against −r = −0.095.
  - 13 applies: recovery "none" is the density, not a failure to recover.
- **No recovery claim** (lesson 4). The registered rule is printed in `readout.txt`: shift "none" on 10/10 for both faunas; cull within 20 on 9/10 and 8/10. These are not read.
- **The null** (Amendments 2 and 3: diagnostics only).
  - k is K1 median 4.5 and K2 median 11.
  - The excess mortality is recruits': designed recruit excess over [T, T+30) is +51 to +162 against the onset cohort's +5 to +17, on 10/10 seeds (CLAIM 3).
  - The alive deficit is 0 at T+30 on every seed and fauna except seed 3's designed fauna (15). It becomes positive for the designed fauna from T+40 on the seeds that collapse, as §3.3 (as amended) expected.
- **ECHO:** a holistic deaths peak begins inside the recovery window on 10/10 seeds in both arms, so the echo sentence does not print.
- **Seed 806** carries RBT-92's drift flag. It is one of the D seeds and the largest paired gap (+0.557). It is read with the flag beside it.

## 5. Predictions, scored (`score.txt` §2)

- **Class: A, registered at 0.30.** D was the mode at 0.45; its test fired on 7/10 seeds, and the three passes (804, 807, 7) are not near misses (headline). The multiclass Brier score is 0.708.
- **Most exposed claims, all three standing:**
  - 1, C3 bankrupts the designed body first: D's test counts 7/10, above the falsifier's ≤ 5/10.
  - 2, the established co-evolved population holds: it trips D on 0/10.
  - 3, rescored: recruits carry the designed excess mortality on 10/10.
- **Binary predictions: Brier 0.098 over 19.**
  - Events that happened, with their stated probability:
    - designed extinct on ≥ 3/10 (5/10), 0.50;
    - co-evolved survives 10/10, 0.80;
    - co-evolved trips no D on ≥ 8/10, 0.75;
    - co-evolved R-shift > designed R-shift, 0.65 (the arithmetic predicts almost all of it);
    - "holds up" not earned, 0.95;
    - turnover guard |R-null| ≥ r, 0.95 (not interpretable);
    - CLAIM 3, 0.75;
    - co-evolved own net below basal on ≤ 2/10, 0.70;
    - co-evolved founders FAIL on 3–7/10 (7/10), 0.70;
    - designed founders FAIL on ≥ 8/10 (10/10), 0.80;
    - contrast on ≥ half the founder-fail seeds (7/7), 0.60;
    - co-evolved founders HOLD on ≥ 3/10 (3/10), 0.70;
    - base ECHO on ≥ 8/10, 0.70;
    - depth shift ≤ base, 0.70;
    - both registered recovery-rule rows, 0.80 and 0.60. These are scored as registered and are not a recovery claim.
  - Events that did not happen:
    - designed recovery income below 0.25 on ≥ 8/10 (3/10), 0.20;
    - designed own net below basal on ≥ 8/10 (4/10), 0.60;
    - the echo sentence, 0.25.
  - The founders, own-net and CLAIM 3 predictions were **made after the adversary's probes**, and are labelled so in the pre-registration.
- **Points:**
  - designed min alive: median 1.5, predicted 9;
  - co-evolved min alive: 60, predicted 38. Alive is uninformative (lesson 5);
  - co-evolved recovery income: median +0.588, predicted +0.48;
  - designed recovery income: median +0.351, predicted +0.28;
  - R-body recovery: registered "+0.22 … where both survive". On the five seeds where both survived it is **+0.196 [+0.116, +0.276]**, close to the prediction (adversary F9). `score.txt` scores it on all ten, +0.286, which the extinct seeds inflate (806 +0.515, 805 +0.451, 3 +0.374);
  - co-evolved R-shift: −0.444, predicted −0.60;
  - designed R-shift: −0.583, predicted −0.75;
  - k: K1 median 4.5, predicted 2; K2 median 11, predicted 10.
  - Every point's median sits inside its registered range, with two exceptions to "every value inside": seed 806's per-seed R-body, +0.515, is outside the per-seed range −0.05 to +0.50, and the co-evolved min alive sits at its range's top (60).
- **The conditional row** ("if D, the floor over income") is not scored, because the class is not D. For the record, the floor fires on 2 of the 5 designed seeds not extinct by T+160, and the income trigger on 0.
- **Carriage: not scored (UNVALIDATED, V3).**
- **What I got wrong:**
  - I priced both bodies' shocks too high on the axis. Each recovered part of its price, which the posted predictions did not anticipate. On the registered both-survive subset my R-body point was close (+0.196 against +0.22).
  - My §4 arithmetic said the co-evolved body would have 0.35–0.68. Per seed it is 0.29–0.59.
  - The paired effect I did predict, 0.65 for "co-evolved loses less", lies inside the arithmetic's bracket (+0.12 to +0.32); it does not show a difference in response.
  - D, my mode at 0.45, did not happen: the designed fauna stayed solvent by clear margins on three seeds.

## 6. What this does not establish

- **A difference in how the two bodies responded.** The arithmetic brackets the paired effect (+0.12 alive, +0.32 insolvent) without deciding it, and the net difference, +0.017, is unresolved at an MDE of ≈ 0.15.
- **A mechanism for either body's partial recovery of its price.** Sorting on gait and survivor-conditioning are not separated by the committed tables.
- **Any carriage claim** (V3 failed).
- **Any recovery claim** (lesson 4).
- **Equivalence of anything** (MDE ≈ 0.15). The paired 8/10 count is a coin flip on replication (F7); the mean is 4.8 SE outside an A/A spread.
- **A general "bootstrap line".** Random co-evolved founders held at six items on 3/10 seeds on this head.
