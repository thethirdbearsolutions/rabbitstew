# RBT-101 report: epoch C4, the furniture removed (`--shift terrain=flat`) on ten founding populations

C4 is the one perceivable challenge in RBT-89's set. It is **reported apart from C1–C3 and never pooled with them**.

**Registered verdict (RBT-89 §9): class C, "the designed body wins after the shift". The falsifier fires.**
- R-body in the recovery window of the shift arm is **−0.310** (95% t(9) [−0.481, −0.139]), negative on **9/10**
  seeds, with r = 0.171. The sign guard needs 8/10, so the margin is **1 seed**. The smallest negative seed is
  −0.104, at the same size as r.
- Class D, E1 and E2 are each reached on 0/10 seeds.

**What class C certifies here** (the coordinator's lessons 1–3 of 19:35, applied without changing the registered
readout):

> On open ground **both bodies earned more**. Against the no-event control the designed body gained **+0.635**
> [+0.532, +0.739] (10/10) and the co-evolved body **+0.177** [+0.076, +0.278] (9/10). The designed body's larger
> gain turned the co-evolved lead (+0.148 on the base) into a deficit, so the **paired event − base contrast is
> −0.458** [−0.596, −0.320], 0/10 positive. Against the registered random-cull null it is −0.472 [−0.585, −0.359].
> **An unchanged gait predicts most of this.** The solo endpoint probe on season-300 bests, fixed before any arm,
> gives +0.572 designed, +0.247 co-evolved and −0.325 paired. The residual, −0.133 [−0.486, +0.219], does not
> resolve. So the falsifier fires because **the furniture was costing the wheeled designed body about twice what it
> cost the co-evolved bodies**, and removing it paid the designed body back. It is not shown that either body
> *responded* to open ground beyond what its standing gait gives.

- **Unlike C1, the class is the event's.** The same rule returns A on the no-event base (+0.148) and on **23/25**
  placebo onsets of the baseline alone. Only on the shift arm does it return C.
- **The co-evolved body "holds up"** by the registered bar: its R-shift is +0.177, above −r. **It did not lose
  income; it gained less.**
- **Re-wiring (`rewire.py`, pre-registered with its own positive control): NO CHANGE SEEN on both faunas.** The
  holistic readout is blind below about half of the survivors, and the designed one below about 20%. No new use of
  a posture sensor is shown, and **no re-adaptation is claimed**.
- **Survival is uninformative.** Alive is 60 in every season of every arm and window. Deaths refill within the
  season (lesson 5).

Everything below re-derives from `readout.txt`, `rewire.txt`, `placebo.txt` and `arith.txt`, all written from
committed tables alone (`roundtrip.txt`).

## Provenance

| what | where |
|---|---|
| pre-registration | `PREREGISTRATION.md` (posted 13:45 UTC), Amendments 1–3 (14:05, 14:40, 15:15), all before any arm existed; cleared with caveats 15:00; step 0 PASS 15:15 |
| seed rule, onsets | RBT-92's: all ten, 10/10 read; `runs/RBT-92/onset.txt`, T = 352–382; seed 806 carries the drift flag |
| baselines | the ten RBT-90 part 2 arms, `runs/RBT-90/forage-SEED/`. Their `wiring.txt` (`base-SEED/`) was written by `wiring.py` from bulk restored with `scripts/durable.sh restore … rbt-90-SEED`, all at 600/600 (README rule 6) |
| arms | 10 shift arms (`shift-SEED`); **cull arms only on 801, 1, 2 and 4**, the other six have k = 0/0 and their null is the baseline itself (RBT-92 amendment 2); cull20 is RBT-92's (`runs/RBT-92/cull20-SEED`, with `wiring.txt` from its post-run hook) |
| readouts | `readout.txt` (`readout.sh` → RBT-92's `readout.py`), `rewire.txt` (`rewire.py`, control `control360.txt`), `placebo.txt` (`placebo.py`, RBT-99's method with C4's paths), `arith.txt` (`arith.py`) |
| round trip | `roundtrip.txt`: in a worktree of the readout commit, with no bulk present, all four readouts reproduce **byte for byte**.<br>Perturbing `shift-3/seasons.txt` (season 450, holistic income +0.5) moves 9 lines of `readout.txt`: r 0.1710 → 0.1711, seed 3's recovery R-body −0.2450 → −0.2400, and the mean −0.3101 → −0.3096.<br>Perturbing one survivor's g1 in `shift-3/wiring.txt` (+1.0) moves 6 lines of `rewire.txt`, all in the unscored W-acq(g1). The verdict does not move. |
| tests | `python -m pytest -q` on this branch: 289 passed |
| RBT-105 A/A spread | `runs/RBT-105/aa_spread.txt` **had not landed** at this writing. The readings marked *(A/A-conditional)* depend on it. The headline contrasts are 4–6× the per-seed A/A-like RMS in `placebo.txt` (0.077) and do not. |

## 1. Validation, read first

- **V0, V1 and V2 pass on 10/10 seeds** (`readout.txt`).
  - Every arm is identical to its baseline before T, on `seasons.txt` and on `lineage-last.txt`.
  - The culls are exactly as stated.
  - The tracer's alive count equals the table's.
- **V3 fails, as it did for C1 and C2, on the same cull20 arms.** The alive dip is 0 on 10/10 seeds, because the
  slots refill within the season. **The L carriage row is not scored (UNVALIDATED, V3)** (lesson 6). The values are
  printed in `readout.txt` and not read.
- **The re-wiring readout has its own gates, and they pass** (`rewire.txt`):
  - V-W: every C0 and P(s) individual has a wiring row, in all four arms;
  - C0 and its wiring are identical across base, shift, cull and cull20;
  - `CONTROL-FAUNA` PASS at n = 10 for both faunas.

## 2. The co-evolved against designed contrast, and the class rule where there is no event

R-body is holistic − designed `mean_lifetime_score`, as a window mean. Each cell gives the mean over 10 seeds, its
95% t(9) interval, and the positive count.

| arm | before [T−100, T) | transient [T, T+60) | **recovery [T+60, T+160)** | tail [T+160, T+200) |
|---|---|---|---|---|
| base | +0.158 [+0.080, +0.236] 9/10 | +0.169 [+0.055, +0.283] 8/10 | +0.148 [+0.051, +0.245] 9/10 | +0.106 [+0.016, +0.196] 8/10 |
| **shift** | +0.158 (identical by V0) | −0.235 [−0.421, −0.049] 2/10 | **−0.310 [−0.481, −0.139] 1/10** | −0.314 [−0.561, −0.068] 1/10 |
| cull | +0.158 | +0.164 [+0.032, +0.296] 8/10 | +0.162 [+0.053, +0.272] 9/10 | +0.129 [+0.017, +0.240] 8/10 |
| cull20 | +0.158 | +0.205 [+0.055, +0.355] 8/10 | +0.191 [+0.084, +0.299] 8/10 | +0.194 [+0.063, +0.326] 8/10 |

**Per seed, recovery, shift arm (base in brackets):**
801 −0.320 (+0.019), 804 −0.281 (+0.113), 805 −0.522 (+0.209), 806 −0.670 (−0.042), 807 −0.604 (+0.094),
1 +0.118 (+0.407), 2 −0.104 (+0.018), 3 −0.245 (+0.161), 4 −0.313 (+0.241), 7 −0.159 (+0.261).

**Power:**
- The per-seed spread of recovery R-body is sd 0.239, so **r = 0.171**, 2.2× the pre-registered expectation of 0.077.
- Class B was not reachable at this spread. The equivalence form, |mean| + r = 0.481, is far from < 0.10.

**The class rule where there is no event (lesson 1; `placebo.txt`, P3):**
- The rule returns **A** on the base arm's before, recovery and tail windows.
- It returns **A** on **23/25** placebo onsets of the baseline alone, T′ = T − 200 … T + 40 in steps of 10. The
  other two are F.
- It returns **C** only on the shift arm. So **the flip from A to C is the event's**.
- The level it measures moved from +0.148 to −0.310.

## 3. What flat ground did to each body

**Against the no-event control, R-shift = shift − base, paired per season (`readout.txt`):**

| fauna | transient | **recovery** | tail |
|---|---|---|---|
| co-evolved | +0.110 [+0.066, +0.154] 10/10 | **+0.177 [+0.076, +0.278] 9/10** | +0.168 [+0.009, +0.326] 9/10 |
| designed | +0.514 [+0.428, +0.600] 10/10 | **+0.635 [+0.532, +0.739] 10/10** | +0.588 [+0.463, +0.713] 10/10 |

- Per seed, recovery:
  - co-evolved: +0.159, +0.208, +0.058, +0.214, +0.134, +0.431, +0.382, +0.119, −0.039, +0.103;
  - designed: +0.499, +0.601, +0.789, +0.842, +0.832, +0.720, +0.504, +0.525, +0.515, +0.524.
- **Both bodies gain on flat ground, from the first ten seasons on.** The designed body gains 3.6× as much in the
  recovery window.
- The co-evolved gain is resolved, but its lower bound (+0.076) is at the A/A-like per-seed RMS *(A/A-conditional)*.

**The event contrast (lesson 2; `placebo.txt`, P4), recovery window:**

| | vs the control (shift − base) | vs the registered null (shift − cull) |
|---|---|---|
| **paired R-body** | **−0.458 [−0.596, −0.320], 0/10** | **−0.472 [−0.585, −0.359], 0/10**, n = 10 (six are k = 0/0, where shift − cull ≡ shift − base) |
| paired, on the 4 seeds with a real cull only | — | −0.361 [−0.486, −0.236], 0/4 (*post hoc subset, defined by k, not by outcome*) |
| co-evolved R-shift | +0.177 [+0.076, +0.278] | +0.175 [+0.102, +0.249], 10/10 |
| designed R-shift | +0.635 [+0.532, +0.739] | +0.647 [+0.549, +0.746], 10/10 |

**The null.**
- **k, the excess deaths in [T, T+10)**, is 3, 0, 0, 0, 0, 3, 0, 0, 1, 0 co-evolved and 0, 0, 0, 0, 0, 0, 2, 0, 0, 0
  designed. **Six seeds are 0/0** (804, 805, 806, 807, 3, 7).
- Flat ground killed nobody, as a boon should not. The registered excess-deaths null has almost no channel here, so
  R-null ≈ R-shift.
- **The turnover reference is cull20**, a cull of a third of each fauna. Its recovery R-cull20 is +0.047
  [−0.016, +0.110] co-evolved and +0.004 [−0.035, +0.042] designed. A random turnover of that size moves neither
  body by a resolvable amount. The event moved both.
- **Turnover guard**, on the 3/10 seeds with co-evolved k > 0: co-evolved R-null is +0.178, and |R-null| ≥ r, so the
  answer is **no**. The shift did more to co-evolved income than a same-size cull. That is scored on n = 3, and it
  is not evidence about equivalence.

## 4. Arithmetic first: what an unchanged gait predicts (lesson 3; `arith.txt`)

The only unchanged-gait flat-ground measurement fixed before any arm is the endpoint probe (`flat_probe.txt`,
pre-registered §1). It takes each seed's season-300 best of each fauna, **alone**, over 64 paired draws, and
records items per bout on flat minus random ground. That is the axis's own unit, one bout a season.

| | predicted by the probe | observed R-shift (recovery) | residual (observed − predicted) | observed / predicted |
|---|---|---|---|---|
| co-evolved | +0.247 [+0.063, +0.430] | +0.177 [+0.076, +0.278] | −0.070 [−0.316, +0.176] | 0.72 |
| designed | +0.572 [+0.358, +0.786] | +0.635 [+0.532, +0.739] | +0.063 [−0.132, +0.258] | 1.11 |
| **paired** | **−0.325 [−0.644, −0.007]** | **−0.458 [−0.596, −0.320]** | **−0.133 [−0.486, +0.219]** | — |

- **At the mean the probe's arithmetic accounts for the effect.** The designed body gains about what its unchanged
  best gains alone, and the co-evolved body about three quarters of that. The paired residual does not resolve.
  **Nothing here is read as a response to open ground beyond the arithmetic.**
- **Per seed the probe predicts nothing.** The per-seed correlation of the predicted with the observed paired
  contrast is r = −0.04. That is expected from a solo best at season 300 standing in for a population at T in groups
  of four. So the residual's interval is wide (±0.35), and "no residual" is not shown either: **a response of up to
  ±0.35 on the paired contrast would not be visible here** *(A/A-conditional only at the margin; the width is the
  probe's)*.
- **The mechanism the arithmetic points at** is §1's: the obstacles, 0.03–0.3 m tall, stop wheels more than they
  stop evolved gaits. The designed body's solo best is not consistently displaced farther on flat ground
  (`flat_probe.txt`: farther on 3/10 seeds), but it eats 0.16–1.11 more items a bout. This is a statement about the furniture. It is not one about either body's
  adaptation.

## 5. Re-wiring: the C4-specific readout (`rewire.txt`, pre-registered §6 and Amendments 2–3)

**Verdict at T + 160, per fauna, on `new_existing`** (a new direct posture link on a sensor the lineage already
had), against its registered guards: shift − base, shift − cull20 (the divergence null), and the placebo contrast.

| | co-evolved (holistic) | designed |
|---|---|---|
| **verdict** | **NO CHANGE SEEN; blind below f ≈ 0.5 of survivors** | **NO CHANGE SEEN; blind below f ≈ 0.2 of survivors** |
| new_existing, shift − base | +0.012 [−0.017, +0.040], 6/10 | +0.012 [−0.056, +0.080], 5/10 |
| new_existing, shift − cull20 | −0.035 [−0.079, +0.009], 2/10 | −0.027 [−0.097, +0.043], 4/10 |
| placebo contrast (new_existing − new_other), shift − base | +0.013 [−0.048, +0.075] | +0.013 [−0.085, +0.111] |
| depth, shift − base (events) | +0.09 [−0.03, +0.21] | −0.07 [−0.38, +0.24] |
| control at n = 10 (`control360.txt`) | PASS | PASS |

- **No new use of a posture sensor is seen on either body**, at the resolution the positive control certifies.
  C4's claim line asks "whether anything is re-wired during the challenge". The answer, at about 4–5 reproduction
  events and this resolution, is: **nothing that reached half the co-evolved survivors or a fifth of the designed
  ones.**
- **Depth barely moved** (under 0.1 event either way), so the turnover caveat does not apply.
- **The divergence null behaves as the adversary predicted** (round 1, F1).
  - cull20 raises depth at T + 160: +0.38 [+0.10, +0.65] holistic, +0.33 [+0.06, +0.61] designed.
  - It raises new_existing too: +0.047 [+0.010, +0.083] holistic, resolved. The designed +0.038 [−0.034, +0.111]
    does not resolve.
  - A turnover shock alone makes new posture links appear. That is why shift − cull20 was registered as the guard,
    and it makes the guard conservative.
- **Printed, not scored:**
  - **lost** (a direct posture link lost against every ancestor): shift − base is −0.080 [−0.134, −0.026] holistic.
    Against cull20 it is −0.032 [−0.082, +0.019] and does not resolve. The control does not validate this direction
    (it installs, it does not remove), so it is **not read** *(A/A-conditional as well)*.
  - new_grown, new_all and W-acq/W-sort on g1 and g2 are also printed and not read.
- **T + 199** (`rewire.txt`): new_existing, designed, shift − cull20 is −0.070 [−0.140, −0.000]. The upper bound
  is −0.0001, at the edge of FEWER NEW LINKS against the null. It is outside the primary read point and not
  scored. It is reported here because **RBT-107 (a deeper post-event window on C4) depends on this result**.

**For RBT-107:** at T + 160 there is no sign of re-wiring on either fauna, and the readout's resolution is the
limit, not the absence of an instrument. A deeper window is the one way to give a re-wiring time to spread past
f ≈ 0.5 (holistic) or 0.2 (designed). The divergence null to carry forward is cull20. It raises holistic new-link
counts by about +0.047 at T + 160, so any deeper effect must clear that.

## 6. Readings owed by the pre-registration

- **The claim line (RBT-89 §2, C4), verbatim:**
  > **Claim tested:** whether gaits built among clutter hold on open ground, on both bodies, with the contest of C1
  > available if both survive; and, alone in the set, whether anything is re-wired during the challenge.
  - **Gaits built among clutter hold on open ground, on both bodies:** yes. Both gained income, and neither lost
    any.
  - **The contest:** the designed body wins it on open ground, **class C, the owner's falsifier**, by the size the
    unchanged-gait arithmetic predicts.
  - **Re-wiring:** nothing seen, at the stated resolution.
- **"Re-adapts" for what is sorting (§14 item 10):** no lineage is shown to have acquired a posture link it did not
  carry at onset beyond the baseline's and the null's own rate. The report says **"holds" and "gains"**, never
  "re-adapts".
- **Recovery time: not read** (lesson 4). The numbers are in `readout.txt` for the record.
  - The designed "none" on 10/10 is its gain, since the metric does not know the sign.
  - The co-evolved d = 0 on 4/10 are the d = 0 artifact of slow divergence.
- **Class tests:** E1, D and E2 are each 0/10 (`readout.txt`).
- **Forbidden readings (§14):**
  - item 7, C4 is not pooled;
  - item 5, the class is read on the recovery window, and the transient agrees;
  - item 3, no champion reading. The probe's bests enter only the arithmetic, labelled as such.
- **Seed 806** carries the drift flag. Its recovery R-body, −0.670, is the most negative, and it is read with the
  flag beside it, not dropped. Without it the mean is −0.270 [−0.436, −0.105], negative on 8/9 against
  ⌈0.8·9⌉ = 8, so still class C. This is a post hoc check, not a re-pick.
- **The sign guard's margin (coordinator):** 9/10 negative against 8/10, **1 seed**. The smallest negative seed is 2,
  at −0.104, at the size of r and about 1.4× the A/A-like RMS.
  - A replicate could plausibly return F through the sign guard, as RBT-92's could *(A/A-conditional)*.
  - The **paired** contrast, 0/10 positive at −0.458 ± 0.138, has no such margin problem.

## 7. My predictions, scored as mine (Amendment 2 is the registered set)

| prediction (confidence) | outcome | scored |
|---|---|---|
| class: B 0.35, **C 0.30**, F 0.25, A 0.05, D/E 0.05 | **C** | the realised class held my second-highest probability |
| R-body recovery −0.05 (per seed −0.30 to +0.15) | −0.310; per seed −0.670 to +0.118, 5/10 below −0.30 | **wrong** (the size) |
| designed R-shift +0.28 (+0.05 to +0.55) | +0.635; 5/10 above +0.55 | **wrong** (under by half) |
| designed R-shift > 0 on ≥ 8/10 (0.7) | 10/10 | right |
| co-evolved R-shift +0.10 (−0.05 to +0.30) | +0.177; 2/10 above +0.30 | right |
| **designed R-shift > co-evolved (0.75), my most exposed claim** | −0.458 [−0.596, −0.320], 0/10 | **right**. Neither falsifier of it fired |
| "holds up" (0.85) | +0.177 ≥ −0.171 | right |
| k = 0/0 on ≥ 6/10 (0.55); K1 median 0 (0–8), K2 median 0 (0–5) | 6/10; K1 median 0 (max 3), K2 median 0 (max 2) | right |
| recovery, paired: designed "none" on ≥ 5/10 (0.5) | 10/10 | right, **as registered**; the rule is flagged (lesson 4), so this is not a recovery claim |
| recovery, paired: co-evolved ≤ 60 on ≥ 6/10 (0.5) | 6/10 | right, **as registered**; 4 of the 6 are d = 0 |
| L(T+160) shift − base within ±0.10 (0.65) | — | **not scored (UNVALIDATED, V3)** |
| re-wiring, holistic: NO CHANGE SEEN (0.85) | NO CHANGE SEEN | right |
| re-wiring, designed: NO CHANGE SEEN (0.65) | NO CHANGE SEEN | right |
| new_existing shift − base: holistic 0.00 (−0.04, +0.04); designed −0.01 (−0.04, +0.03) | +0.012; +0.012 | right, both |
| depth shift − base −0.1 event (−0.5, +0.3), both faunas | +0.09; −0.07 | right, within range; the holistic sign is wrong |

- **Brier score** over the 8 probability-stated binary predictions (all rows above with a confidence, apart from
  the class row and the unscored carriage row): **0.128**, arithmetic on the table.
- **What I got wrong:** the size. I discounted the solo probe's gains by half for group foraging. In the ecology the
  designed body gained 1.1× its solo best's gain and the co-evolved body 0.7×, so the contrast came out larger than
  the solo probe, not smaller. The direction and the falsifier's live status came from the probe, and both held.

## 8. Caveats the report carries (coordinator's 15:00 ruling, and this readout)

1. **The placebo is a weak guard.** cull20 is the real turnover guard (§5).
2. **cull20 is conservative, not matched.** It raises holistic new-link counts by +0.047 and depth by +0.33 to
   +0.38 event at T + 160, where the boon moved depth by under 0.1.
3. **The readout is structural, not functional.** A RE-WIRED verdict would have meant "acquired along descent
   within about four events", not "used".
4. **The holistic resolution is a sweep detector:** f ≈ 0.5 at n = 10.
5. **C4 is reported apart from C1–C3.**
6. **The class rule measures the lead's level** (lesson 1). Here it flipped from A (base, and placebo onsets) to C
   (shift), so the event did move it, by the size the unchanged-gait arithmetic predicts (lesson 3).
7. **The arithmetic is a solo-best prior.** It explains the mean and not the per-seed values. A population-level
   unchanged-gait prediction (the C0 cohort in groups of four on flat against random ground) is not in the
   committed data. It is the natural next measurement, and it would narrow the ±0.35 residual.
8. **The registered cull null has almost no channel** (k = 0/0 on six seeds), because flat ground killed nobody.
   cull20 is the turnover reference.
9. **Survival and recovery time are not read** (lessons 4–5).
10. **RBT-105's A/A spread had not landed.** Readings marked *(A/A-conditional)* are worded as such: the
    co-evolved gain's lower bound, the sign guard's one-seed margin, the unscored "lost" and T + 199 lines.

## 9. What this decides

On open ground **both bodies earn more, and the wheeled designed body earns much more**. It gains +0.64 per season,
against +0.18 for the co-evolved body. That turns the co-evolved lead of +0.15 into a deficit of −0.31.
**The owner's falsifier, "the designed body wins after the shift", fires on C4.** It fires by the arithmetic of the
furniture: the obstacles were a larger tax on wheels than on evolved gaits, and removing them refunded the wheels.
It does not show that the co-evolved body failed to adapt, since it gained. Nor does it show that the designed body
adapted, since an unchanged best predicts its gain. Nothing was re-wired that the positive control could have
seen.

**For the programme:**
- **The co-evolved body's income lead in the baseline economy was partly bought by the clutter.** It holds up on
  open ground in absolute terms. It loses the contest because the comparator was more handicapped by the clutter
  than it was.
- **A held-out challenge that removes an impediment is a test of how much each body was being impeded**, and here
  the answer was about 2:1 against the wheels.
