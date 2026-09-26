# RBT-100 report: epoch C3, scarce food (12 → 6 items) on ten founding populations

*Written at 20:00 UTC on 2026-09-26, after the coordinator's 19:35 wake. It applies the six lessons from the RBT-92 and RBT-99 readout adversaries and the 18:45 and 19:05 rulings. Those lessons change the wording only: the readout ran as registered.*

**Verdict (RBT-89 §9, as pre-registered): class A, co-evolved wins.**
- **The numbers:** R-body in the recovery window of the shift arm is **+0.286** (95% t(9) [+0.191, +0.382]), positive on 10/10 seeds, with r = 0.095.
- **The margins:** A's sign guard needs 8/10, so its margin is +2 seeds. **Class D, designed bankrupt, fired on 7/10 seeds, one short of its 8/10 guard** (margin −1).
- **The falsifier,** "the designed body wins on the held-out challenge", is not met. C and E2 are reached on 0/10 seeds.

**What class A certifies here: nothing about the shift.**
- **The rule returns A with no event.** It gives A on the no-event baseline's own recovery window (+0.148, 9/10) and on **23/25 placebo onsets** (`placebo.txt` P3). The class reads the level of the co-evolved lead (lesson 1).
- **The designed body is not a solvent rival.** Its fauna failed D's test on 7/10 seeds and went extinct on 5. Forbidden readings 2 and 12 apply: this is not a win over a solvent comparator, even though D missed its guard by one seed.
- **The printed class-A sentence is wrong for this run.** "Both surviving above the floor" is false on 7/10 seeds. That is a text defect in my `verdict_text` for C3, reported here and not patched after the data.

**What the event did: arithmetic, and nothing beyond it (lesson 3; `score.txt` §1).**

> Halving the items halves every body's gross food and leaves its work bill where it was. Before T the designed
> body ate 1.22–1.50 items a season against the co-evolved body's 1.02–1.35. So the shift takes more from the
> designed body: a price of 0.70 against 0.58. At an unchanged gait the designed body's season net falls to
> **+0.08 to +0.18, below the 0.25 basal cost on 10/10 seeds**. The co-evolved body's falls to **+0.29 to +0.59,
> above basal on 10/10**. Two unchanged populations would have diverged by **+0.121 [+0.066, +0.176]**. The observed
> paired effect is **+0.138 [+0.006, +0.271], 8/10**. The residual, **+0.017 [−0.092, +0.127]**, does not resolve.
> Net of its own price each body recovered a similar part of it: co-evolved +0.131 (23%), designed +0.114 (16%). The
> difference is +0.017, unresolved. The paired effect is the price arithmetic of two gaits at half the density,
> not a difference in how the two bodies responded.

**What C3 set out to test, answered on its own terms: survivorship at six items.**
- **The established co-evolved population paid its way at six items on 10/10 seeds.**
  - Its season own net over everyone who ran each season, starved recruits included (an upper bound, `own.txt`), stayed above basal in the recovery window on 10/10 seeds, and on 0/10 did it fall below.
  - Survivors' own net was +0.50 to +0.66 per seed.
  - It tripped no D trigger on any seed.
  - That is what its pre-onset gait predicts by arithmetic (unchanged net +0.29 to +0.59). It is survivorship of standing morphology and gait, not adaptation (§3; depth about 5 events).
- **Random co-evolved founders at six items failed on 7/10 seeds** (founders6, fewer than 12 alive at season 59) and held on 3/10 (804, 1, 4). The contrast sentence, "an established population holds where random founders could not", prints on **7/7** founder-fail seeds.
  - The readout prints the qualifier: "founders HOLD on 3/10 seeds read; contrast on 7/7". Since 3 < ⌈10/2⌉, the survivorship-only sentence is not triggered.
  - The contrast holds, but it is carried by the established gait's arithmetic, not by a response to the shift.
- **The designed body's budget was exceeded, as the protocol expected** (§2, C3).
  - It was extinct on 5/10 seeds, at T+78 to T+146.
  - It failed D's test on 7/10.
  - Its own net over all runners was below basal on 4/10.
  - It stayed solvent on 3/10 (804, 807, 7), with survivors' own net +0.31 to +0.35. An unchanged gait would have earned +0.11 to +0.18 there.
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
| round trip | `roundtrip.txt`, from `roundtrip.sh` |
| tests | `python -m pytest -q` (see the PR) |

## 1. Validation (V0–V3)

- **V0, V1 and V2 pass on 10/10 seeds.** C3-V1 also passes 10/10: `food.items = 6` from T on every shift arm.
- **V3 fails, as it did on RBT-92 and RBT-99, on the same cull20 arms.**
  - The alive dip is 0 on 10/10 seeds, because freed slots refill within the season.
  - Holistic L(T+60), cull20 − base, is −0.042 [−0.106, +0.022].
  - So **carriage is UNVALIDATED**, and the L row is "not scored (UNVALIDATED, V3)" (lesson 6). For the record only, designed Lc shift − base is −0.22 to −0.30 at every horizon. It is not read.

## 2. The class, and what it measures (lessons 1 and 2)

| | before | transient | **recovery** | tail |
|---|---|---|---|---|
| base R-body | +0.158 [+0.080, +0.236] 9/10 | +0.169 | +0.148 [+0.051, +0.245] 9/10 | +0.106 |
| shift R-body | +0.158 (V0) | +0.214 [+0.138, +0.289] 10/10 | **+0.286 [+0.191, +0.382] 10/10** | +0.424 [+0.267, +0.580] 10/10 |
| cull R-body | +0.158 | +0.160 | +0.181 [+0.059, +0.302] 8/10 | +0.214 |

- **The rule without the event:** class A on the base arm's before, recovery and tail windows, and on 23/25 placebo onsets. The two exceptions are T+20 and T+30, both F (`placebo.txt` P3).
- **The event against the control (paired, recovery, n = 10):**
  - shift − base R-body **+0.138 [+0.006, +0.271], 8/10**;
  - co-evolved R-shift **−0.444 [−0.494, −0.395]**, 0/10;
  - designed R-shift **−0.583 [−0.682, −0.483]**, 0/10 (extinct seasons at 0).
- **The event against the registered null (shift − cull, n = 10; no cull emptied a fauna):**
  - R-body **+0.106 [−0.045, +0.256], 7/10, unresolved**;
  - co-evolved R-null −0.475 [−0.542, −0.409];
  - designed R-null −0.581 [−0.688, −0.474].

  C3's turnover guard was declared not interpretable a priori (Amendment 2). Its R-null is the price of the halved density, which no random cull carries: R-cull is +0.031 (co-evolved) and −0.002 (designed).
- **Sign guards:** R-body(shift) is positive on 10/10 against the 8 needed (margin +2). The paired contrast is positive on 8/10 (margin 0). D's test counts 7/10 against 8 (margin −1).
- **The A/A spread.** RBT-105's ecology A/A spread (`runs/RBT-105/aa_spread.txt`) was not yet committed when this was written. The A/A-like reference here is R-cull20's per-seed RMS, 0.077 (`placebo.txt`).
  - The paired contrast's 8/10 and D's 7/10 are both **borderline, and conditional on that spread**.
  - A spread of that size can move one seed either way. So "D missed by one seed" and "the paired contrast is positive on 8/10" are read as conditional on it.

## 3. Arithmetic first (lesson 3): both nets, side by side

**Source.** Pre-onset seasons [T−40, T) of each seed's baseline `own.txt` (`score.txt` §1). "Unchanged" means food/2 − work, a body's season net at the same gait with half the items.

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
| co-evolved | 0.576 | −0.444 [−0.494, −0.395] | **+0.131 [+0.078, +0.185] 10/10** | 0.23 (per seed 0.05–0.42) | a survivors' lifetime mean. The upper bound over all runners, starved recruits included, sits within 0.02 of it (`readout.txt` OWN) |
| designed | 0.697 | −0.583 [−0.682, −0.483] | **+0.114 [+0.018, +0.210] 8/10** | 0.16 (per seed −0.16 to +0.43) | pinned by extinction (axis 0) on the 5 extinct seeds; survivor-conditioned elsewhere |

- **The difference is +0.017 [−0.092, +0.127], 5/10: unresolved.** It is identical to the residual of the paired contrast over its arithmetic, as it must be.
- On the own-net scale (season means over survivors, shift − base) the nets are +0.105 (co-evolved) and +0.137 (designed). **Neither body can be said to have responded better.**
- The event's whole paired effect is +0.138, against an arithmetic +0.121. It is the designed body's larger gross intake, halved.

## 4. Readings owed by the pre-registration

- **C3's claim line (§2, C3), verbatim:**
  > **Claim tested:** as C2, survivorship at a boundary, here the bootstrap line for food; whether an
  > established population holds where random founders could not. Not the owner's contest claim.
  - Read per seed on founders6: founders HOLD on 3/10 seeds, and the contrast holds on 7/7 of the others.
- **"Robust" means survivorship of standing morphology and gait**, not adaptation during the shift (§3, RBT-91 option A). Depth after T is about 5 events on both arms (DEPTH: 5.0 against 5.0), so the co-evolved body "survives" or "is sorted".
- **The sentence is:**

  > At half the food the established co-evolved population paid its way on every seed, as its pre-onset gait's
  > arithmetic says it would. On 7 of the 10 seeds random co-evolved founders could not do that. The designed
  > body's budget was exceeded: an unchanged gait would earn below basal on every seed, and it went extinct on 5.
  > Neither body recovered more of its own price than the other.
- **This is one body's cheapness at a density, not the owner's contest.** Class A adds nothing to it.
- **Forbidden readings.**
  - 2 and 12 apply: the comparator was bankrupt by D's test on 7/10. The class is A, and it is read as "outlasts a bankrupt comparator" in substance.
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

- **Class: A, registered at 0.30.** D was the mode at 0.45 and missed its guard by one seed. The multiclass Brier score is 0.708.
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
  - R-body recovery: +0.286, predicted +0.22;
  - co-evolved R-shift: −0.444, predicted −0.60;
  - designed R-shift: −0.583, predicted −0.75;
  - k: K1 median 4.5, predicted 2; K2 median 11, predicted 10.
  - Every point sits inside its registered range, except that the co-evolved min alive sat at its range's top.
- **The conditional row** ("if D, the floor over income") is not scored, because the class is not D. For the record, the floor fires on 2 of the 5 designed seeds not extinct by T+160, and the income trigger on 0.
- **Carriage: not scored (UNVALIDATED, V3).**
- **What I got wrong:**
  - I priced both bodies' shocks too high. Each recovered about a fifth of its price, which the posted predictions did not anticipate.
  - My §4 arithmetic said the co-evolved body would have 0.35–0.68. Per seed it is 0.29–0.59.
  - The paired effect I did predict, 0.65 for "co-evolved loses less", is almost all arithmetic.
  - D, my mode, fell one seed short.

## 6. What this does not establish

- **A difference in how the two bodies responded.** Net of its own price the difference is +0.017, unresolved.
- **A mechanism for either body's partial recovery of its price.** Sorting on gait and survivor-conditioning are not separated by the committed tables.
- **Any carriage claim** (V3 failed).
- **Any recovery claim** (lesson 4).
- **Equivalence of anything.** The A/A spread is pending, and the borderline counts (D 7/10, paired 8/10) are conditional on it.
- **A general "bootstrap line".** Random co-evolved founders held at six items on 3/10 seeds on this head.
