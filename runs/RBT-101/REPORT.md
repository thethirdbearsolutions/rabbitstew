# RBT-101 report: epoch C4, the furniture removed (`--shift terrain=flat`) on ten founding populations

C4 is the one perceivable challenge in RBT-89's set. It is **reported apart from C1–C3 and never pooled with them**.

**Registered verdict (RBT-89 §9): class C, "the designed body wins after the shift". The falsifier fires.** The
owner's words for it (protocol §9, verbatim) are "the designed body wins on the held-out challenge". Here it won by
gaining more: the co-evolved body **gained less; it did not lose**.
- R-body in the recovery window of the shift arm is **−0.310** (95% t(9) [−0.481, −0.139]), negative on **9/10**
  seeds, with r = 0.171. The sign guard needs 8/10, so the margin is **1 seed**. The class survives leaving any
  seed out, every 100-season window, and one flipped seed (§6).
- Class D, E1 and E2 are each reached on 0/10 seeds.

**What class C certifies here** (the coordinator's lessons 1–3 and 8, and the readout adversary's F2, PR #202; the
registered readout is unchanged):

> On open ground **both bodies earned more**. Measured in the ecology's own arena, the furniture's arithmetic
> (unchanged gaits, four to a group, flat against random ground) pays the wheeled designed body about **+0.94** a
> season and the co-evolved gaits **+0.14 to +0.22**. It predicts a paired contrast of **−0.63 to −0.81**, more than
> the observed **−0.458** [−0.596, −0.320]. So **the falsifier fires wholly by the arithmetic of the furniture**. The
> pre-onset lead was the clutter's tax on wheels. Beyond the arithmetic the contrast moved back toward the co-evolved
> body, by +0.17 [+0.06, +0.29] (arena predictor) or +0.27 [+0.05, +0.49] (same-season split), 8/10 each (*post hoc,
> the adversary's predictor*). The designed population born after the shift foraged worse than the baseline's
> contemporaneous population on both terrains. The data attribute the class to the furniture, not to any body
> adapting, and the non-arithmetic part runs against the designed body. The pre-registered solo-best probe
> (committed before the arms) predicted the direction. It under-predicted the wheels' refund in the arena (+0.57
> against +0.79) and did not predict per seed (r −0.04).

- **The observed contrasts.** Against the no-event control the designed body gained **+0.635** [+0.532, +0.739]
  (10/10) and the co-evolved body **+0.177** [+0.076, +0.278] (9/10); the paired event − base contrast is **−0.458**
  [−0.596, −0.320], 0/10 positive, 3.7× the single-seed paired A/A-like RMS and 12 SE of the A/A mean. Against the
  registered random-cull null it is **−0.472** [−0.585, −0.359] (≡ event − base on the six k = 0/0 seeds; the null
  could absorb ~0.5%).
- **Unlike C1, the class is the event's.** The same rule returns A on the no-event base (+0.148) and on **23/25**
  placebo onsets of the baseline alone. Only on the shift arm does it return C.
- **The co-evolved body "holds up"** by the registered bar: its R-shift is +0.177, above −r. **It did not lose
  income; it gained less.** Against the arena arithmetic it gained what an unchanged gait gains (observed − Z10
  +0.016 [−0.095, +0.128], *post hoc*).
- **Re-wiring (`rewire.py`, pre-registered with its own positive control): NO CHANGE SEEN on both faunas.** The
  holistic readout is blind below about half of the installable survivors, and the designed one below about 20%. No new use of
  a posture sensor is shown, and **no re-adaptation is claimed**.
- **Survival is uninformative.** Alive is 60 in every season of every arm and window. Deaths refill within the
  season (lesson 5).

Everything below re-derives from `readout.txt`, `rewire.txt`, `placebo.txt` and `arith.txt`, all written from
committed tables alone (`roundtrip.txt`). The arena predictors and the same-season split are the readout
adversary's, in `readout-adversary/probe_arena.txt` and `readout-adversary/probe_refund.txt`; those files arrive
with PR #202.

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
| A/A scale | `runs/RBT-105/aa_spread.txt` had not landed at this writing. The paired A/A-like RMS from committed arms is 0.108 (cull20 − base) to 0.123 (real culls) (readout adversary, `probe_readout.txt`, PR #202); the per-fauna RMS in `placebo.txt` is 0.077. The paired contrast is 3.7× the single-seed paired RMS and 12 SE of the A/A mean, so no headline reading is A/A-conditional. |

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
- The co-evolved gain is resolved: 9/10 seeds positive, interval clear of zero.

**The event contrast (lesson 2; `placebo.txt`, P4), recovery window:**

| | vs the control (shift − base) | vs the registered null (shift − cull) |
|---|---|---|
| **paired R-body** | **−0.458 [−0.596, −0.320], 0/10** | **−0.472 [−0.585, −0.359], 0/10**, n = 10 (≡ event − base on the six k = 0/0 seeds; the null could absorb ~0.5%) |
| paired, on the 4 seeds with a real cull only | — | −0.361 [−0.486, −0.236], 0/4 (*post hoc subset, defined by k, not by outcome*) |
| co-evolved R-shift | +0.177 [+0.076, +0.278] | +0.175 [+0.102, +0.249], 10/10 |
| designed R-shift | +0.635 [+0.532, +0.739] | +0.647 [+0.549, +0.746], 10/10 |

**The null.**
- **k, the excess deaths in [T, T+10)**, is 3, 0, 0, 0, 0, 3, 0, 0, 1, 0 co-evolved and 0, 0, 0, 0, 0, 0, 2, 0, 0, 0
  designed. **Six seeds are 0/0** (804, 805, 806, 807, 3, 7).
- Flat ground killed nobody, as a boon should not; designed excess deaths are negative on 7/10 seeds. The
  registered excess-deaths null has almost no channel here, so R-null ≈ R-shift: null − base is +0.014, about 0.5%
  of the event, and the null's minimum detectable effect is 0.157, so −0.472 is 3.0× it (readout adversary, F5).
- **The turnover reference is cull20**, a cull of a third of each fauna. Its recovery R-cull20 is +0.047
  [−0.016, +0.110] co-evolved and +0.004 [−0.035, +0.042] designed. A random turnover of that size moves neither
  body by a resolvable amount. The event moved both.
- **Turnover guard**, scored on n = 3 (the 3/10 seeds with co-evolved k > 0): co-evolved R-null is +0.178, and |R-null| ≥ r, so the
  answer is **no**. The shift did more to co-evolved income than a same-size cull. That is scored on n = 3, and it
  is not evidence about equivalence.

## 4. Arithmetic first: what an unchanged gait predicts (lessons 3 and 8; `arith.txt`, readout adversary F2)

Lesson 8: the arithmetic must be made in the axis's own setting (the arena, groups of four, the population at T),
and the change at one season split into refund and response. The pre-registered solo probe does not meet that; the
readout adversary's arena predictors do, and are **post hoc**.

**Predictors of the paired recovery contrast (observed −0.458 [−0.596, −0.320], 0/10):**

| predictor | registered? | predicted paired contrast | residual (observed − predicted) | per-seed r with observed |
|---|---|---|---|---|
| solo endpoint probe, season-300 bests alone, 64 draws (`arith.txt`) | yes, the pre-registered prior (§1) | −0.325 [−0.644, −0.007] | −0.133 [−0.486, +0.219] | −0.04 |
| the same, with my registered half-discount for group foraging | yes (Amendment 2) | −0.163 | −0.296 [−0.511, −0.080] | — |
| Z10: the same pre-T individuals, paired by name, [T, T+10) (`probe_arena.txt`) | **post hoc** | −0.630 [−0.759, −0.501] | **+0.172 [+0.055, +0.289], 8/10** | +0.62 |
| Z: season T replayed, same groups and start seeds (`probe_arena.txt`) | **post hoc** | −0.701 [−0.982, −0.421] | +0.243 [−0.007, +0.493], 7/10 | +0.46 |
| C0 cohort in groups of four, flat − random, simulated (`probe_refund.txt`) | **post hoc** | −0.806 [−0.934, −0.678] | — | — |

**Per fauna, Z10 against observed R-shift (recovery):**

| | solo probe (prior) | Z10 (arena) | observed | observed − Z10 |
|---|---|---|---|---|
| co-evolved | +0.247 [+0.063, +0.430] | +0.161 [+0.119, +0.203] | +0.177 [+0.076, +0.278] | +0.016 [−0.095, +0.128], 5/10 |
| designed | +0.572 [+0.358, +0.786] | +0.791 [+0.642, +0.939] | +0.635 [+0.532, +0.739] | −0.156 [−0.285, −0.026], 3/10 |

**Same-season split at T + 110** (`probe_refund.txt`, simulated; the harness reproduces a recorded season 32/32):
refund = the base population, flat − random; response = the shift population − the base population, both on flat.

| | refund | response |
|---|---|---|
| co-evolved | +0.222 [+0.162, +0.283], 10/10 | +0.050 [−0.127, +0.227], 7/10 |
| designed | +0.944 [+0.815, +1.072], 10/10 | −0.222 [−0.445, +0.002], 2/10 (on random terrain −0.174 [−0.312, −0.036], 1/10) |
| paired | −0.721 [−0.885, −0.558], 0/10 | **+0.272 [+0.053, +0.491], 8/10** |

The simulated total, −0.450, matches the observed −0.458 (per-seed r +0.80). The work term is +0.001 to +0.018 in
every cell and does not matter.

- **The arithmetic accounts for all of the class, and more.** In the arena the furniture's refund to the wheels
  (+0.79 to +0.94) is larger than the solo probe's +0.57, and every arena predictor puts the paired contrast further
  from zero than was observed.
- **Beyond the arithmetic the contrast moved back toward the co-evolved body**, by +0.17 (Z10) or +0.27
  (same-season split), 8/10 each. Both are **post hoc**, from the adversary's predictors. The co-evolved body sits
  on its arithmetic; the non-arithmetic part is on the designed side: the designed population born after the shift
  foraged worse than the baseline's contemporaneous population, on flat and on random ground alike. No mechanism for
  that is claimed here.
- **The pre-registered prior predicted the direction and was too small.** The solo probe is kept as what was
  registered. With my registered half-discount it predicts −0.163 and leaves −0.296 [−0.511, −0.080] unexplained,
  the wrong sign for the arena's residual; undiscounted it leaves −0.133, which does not resolve. It does not
  predict per seed (r −0.04).
- **The furniture:** the obstacles, 0.03–0.3 m tall, cost wheels more than evolved gaits (§1). The designed solo
  best is not consistently displaced farther on flat ground (`flat_probe.txt`: farther on 3/10 seeds), but it eats
  0.16–1.11 more items a bout. This is a statement about the furniture, not about either body's adaptation.

## 5. Re-wiring: the C4-specific readout (`rewire.txt`, pre-registered §6 and Amendments 2–3)

**Verdict at T + 160, per fauna, on `new_existing`** (a new direct posture link on a sensor the lineage already
had), against its registered guards: shift − base, shift − cull20 (the divergence null), and the placebo contrast.

| | co-evolved (holistic) | designed |
|---|---|---|
| **verdict** | **NO CHANGE SEEN; blind below f ≈ 0.5 of installable survivors** | **NO CHANGE SEEN; blind below f ≈ 0.2 of survivors** |
| new_existing, shift − base | +0.012 [−0.017, +0.040], 6/10 | +0.012 [−0.056, +0.080], 5/10 |
| new_existing, shift − cull20 | −0.035 [−0.079, +0.009], 2/10 | −0.027 [−0.097, +0.043], 4/10 |
| placebo contrast (new_existing − new_other), shift − base | +0.013 [−0.048, +0.075] | +0.013 [−0.085, +0.111] |
| depth, shift − base (events) | +0.09 [−0.03, +0.21] | −0.07 [−0.38, +0.24] |
| control at n = 10 (`control360.txt`) | PASS | PASS |

- **No new use of a posture sensor is seen on either body**, at the resolution the positive control certifies.
  C4's claim line asks "whether anything is re-wired during the challenge". The answer, at about 4–5 reproduction
  events and this resolution, is: **nothing that reached half of the installable co-evolved survivors or a fifth of
  the designed ones.** (Installable: 540/600 holistic survivors can take the control's link; 159/600 grew sensors.)
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
    (it installs, it does not remove), so it is **not read**.
  - new_grown, new_all and W-acq/W-sort on g1 and g2 are also printed and not read.
- **T + 199** (`rewire.txt`): new_existing, designed, shift − cull20 is −0.070 [−0.140, −0.000]. This is one of
  156 printed intervals; **not a finding**.

**For RBT-107:** at T + 160 there is no sign of re-wiring on either fauna, and the readout's resolution is the
limit, not the absence of an instrument. A deeper window is the one way to give a re-wiring time to spread past
f ≈ 0.5 of installable survivors (holistic) or 0.2 (designed). The divergence null to carry forward is cull20. It raises holistic new-link
counts by about +0.047 at T + 160, so any deeper effect must clear that.

## 6. Readings owed by the pre-registration

- **The claim line (RBT-89 §2, C4), verbatim:**
  > **Claim tested:** whether gaits built among clutter hold on open ground, on both bodies, with the contest of C1
  > available if both survive; and, alone in the set, whether anything is re-wired during the challenge.
  - **Gaits built among clutter hold on open ground, on both bodies:** yes. Both gained income, and neither lost
    any.
  - **The contest:** the designed body wins it on open ground, **class C, the owner's falsifier** ("the designed
    body wins on the held-out challenge", protocol §9), wholly by the furniture's arithmetic. It gained more; the
    co-evolved body gained less and did not lose.
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
  at −0.104, about the size of r and within the paired A/A scale (0.108–0.123); **seed 2 is the one seed within A/A
  of 0**. The class is robust around that margin (readout adversary, `probe_readout.txt`):
  - leaving any one seed out gives C on 10/10, and every 100-season window gives C;
  - flipping one seed's sign gives C; flipping two gives F;
  - jittering each seed by the paired A/A scale (s = 0.108) keeps C in 98.4% of draws.
  - The **paired** contrast, 0/10 positive at −0.458 ± 0.138, has no margin problem.

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
| recovery, paired: designed "none" on ≥ 5/10 (0.5) | 10/10 | **not scored (lesson 4)** |
| recovery, paired: co-evolved ≤ 60 on ≥ 6/10 (0.5) | 6/10 | **not scored (lesson 4)**; 4 of the 6 are d = 0 |
| L(T+160) shift − base within ±0.10 (0.65) | — | **not scored (UNVALIDATED, V3)** |
| re-wiring, holistic: NO CHANGE SEEN (0.85) | NO CHANGE SEEN | right |
| re-wiring, designed: NO CHANGE SEEN (0.65) | NO CHANGE SEEN | right |
| new_existing shift − base: holistic 0.00 (−0.04, +0.04); designed −0.01 (−0.04, +0.03) | +0.012; +0.012 | right, both |
| depth shift − base −0.1 event (−0.5, +0.3), both faunas | +0.09; −0.07 | right, within range; the holistic sign is wrong |

- **Brier score** over the 6 scored probability-stated binary predictions (the rows with a confidence, apart from
  the class row, the two recovery rows and the carriage row): **0.087**, arithmetic on the table. The class row's
  multi-class Brier is 0.678, against 0.857 for a uniform guess.
- **What I got wrong:** the size, and where the arithmetic lives. I discounted the solo probe's gains by half for
  group foraging. The arena did the opposite for the wheels: it raised the designed body's unchanged-gait gain from
  the solo probe's +0.57 to +0.79 (Z10). So the arithmetic predicts a larger contrast than the solo probe, and the
  observed one is smaller than the arena's. The direction and the falsifier's live status came from the probe, and
  both held.

## 8. Caveats the report carries (coordinator's 15:00 ruling, and this readout)

1. **The placebo is a weak guard.** cull20 is the real turnover guard (§5).
2. **cull20 is conservative, not matched.** It raises holistic new-link counts by +0.047 and depth by +0.33 to
   +0.38 event at T + 160, where the boon moved depth by under 0.1.
3. **The readout is structural, not functional.** A RE-WIRED verdict would have meant "acquired along descent
   within about four events", not "used".
4. **The holistic resolution is a sweep detector:** f ≈ 0.5 of installable survivors at n = 10.
5. **C4 is reported apart from C1–C3.**
6. **The class rule measures the lead's level** (lesson 1). Here it flipped from A (base, and placebo onsets) to C
   (shift), so the event did move it, wholly by the unchanged-gait arithmetic of the furniture (lesson 3).
7. **The registered arithmetic was a solo-best prior; the arena arithmetic is post hoc.** The solo probe predicted
   the direction but not the size in the arena (+0.57 against +0.79 for the wheels) nor the per-seed values
   (r −0.04). The arena predictors (Z10, the same-season split) are the readout adversary's, made after the
   readout; their residual toward the co-evolved body (+0.17 to +0.27, 8/10) is a hypothesis for RBT-107, not a
   registered result. No mechanism for the designed population's decline is claimed.
8. **The registered cull null has almost no channel** (k = 0/0 on six seeds), because flat ground killed nobody.
   cull20 is the turnover reference.
9. **Survival and recovery time are not read** (lessons 4–5).
10. **RBT-105's A/A spread had not landed.** The paired A/A scale used here (0.108–0.123) is from committed arms.
    The headline readings do not depend on RBT-105; seed 2 is the one seed within A/A of 0.

## 9. What this decides

On open ground **both bodies earn more, and the wheeled designed body earns much more**. It gains +0.64 per season,
against +0.18 for the co-evolved body. That turns the co-evolved lead of +0.15 into a deficit of −0.31.
**The owner's falsifier, "the designed body wins on the held-out challenge" (registered as class C, "the designed
body wins after the shift"), fires on C4.** It fires wholly by the arithmetic of the furniture: in the arena the
obstacles were a tax of about +0.94 a season on wheels and +0.14 to +0.22 on the co-evolved gaits, and removing them
refunded the wheels. The designed body won by gaining more; the co-evolved body gained less and did not lose. It is
not shown that either body adapted. Beyond the arithmetic the contrast moved back toward the co-evolved body (post
hoc, +0.17 to +0.27), because the designed population born after the shift foraged worse. Nothing was re-wired that
the positive control could have seen.

**For the programme:**
- **The co-evolved body's income lead in the baseline economy was bought by the clutter, wholly, and more.** Without
  the clutter's tax on wheels the arithmetic alone would have put the co-evolved body further behind than it ended.
- **A held-out challenge that removes an impediment is a test of how much each body was being impeded.** Here the
  furniture cost the wheels several times what it cost the evolved gaits (+0.79 to +0.94 against +0.14 to +0.22).
- **For RBT-107:** the post hoc residual toward the co-evolved body, and the designed post-shift population's lower
  foraging, are hypotheses to register there, not results here.
