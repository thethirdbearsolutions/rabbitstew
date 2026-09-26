# RBT-110 readout adversary: the out-of-sample refund/response split (C1, C2, C3) and C4's null

Under attack: PR #210 (C1), #220 (C2), #216 (C3), #215 (C4null), and the coordinator's 22:15 verdict **C4-SPECIFIC**.
Every number below comes from a probe in this directory. Each probe is run on restored bulk (README rule 6) or on
the analysts' committed `split.txt` files.

| probe | what it does |
|---|---|
| `probe_reproduce.py` → `.raw`, read by `probe_reproduce_read.py` → `probe_reproduce.txt` | an independent re-implementation of all four new-world reads at T + 110: base, shift, cull20, D = 4 (19,756 group bouts); per-draw noise; a second membership rule |
| `probe_check.py` → `probe_check.txt` | 8 new-world seasons (T + 110 of the shift arm) re-simulated bout for bout, on seeds the analysts did not check, including C4's flat world |
| `probe_pool.py` → `probe_pool.txt` | P1 every pooling; P2 cross-challenge correlation; P3 world-specificity (new − old world); P4 C2 survivorship; P5 C4null by terrain and seed 801; P6 scale |
| `probe_observed.py` → `probe_observed.txt` | the split's TOTAL against the ecology's own recorded gains near T + 110 (the C1 cross-check question) |
| `probe_c3_density.py` → `probe_c3_density.txt` | C3's near-extinct designed populations, matched for arena size |

All probes are post hoc. None changes a registered number.

## Verdict on the verdict

**C4-SPECIFIC stands as the registered outcome.**
- H is SUPPORTED on none of C1–C3.
- Every pooling I could defend excludes +0.27 (F4).

**What the label may be taken to mean must change (F3, MUST-FIX).** C4's own +0.27 is not a response to flat ground:
- The same population difference is present on the old (random) terrain: +0.25, 9/10.
- The no-challenge cull20 null shows the same thing on both terrains: +0.20 and +0.18.

So what is "specific to C4" is a general difference between post-event and no-event populations. At r = 110 it is
matched by turnover. It is not a C4-specific adaptation.

## Findings

### F1: NONE. Fidelity to the pre-registration holds, and an independent re-implementation reproduces every per-seed value.

**Commit order.** In each branch, `probe_split.py` was committed first, then the harness check, then `split.txt`.

| branch | script | check | split |
|---|---|---|---|
| C1 | 20:43:02 | 20:43:39 | 21:36 |
| C2 | 20:45:09 | 20:45:38 | 22:08 |
| C3 | 20:43:28 | 20:43:58 | 21:54 |
| C4null | 20:43:01 | 20:43:49 | 21:30 / 21:54 |

- The issue was created at 20:36:58, and the pre-registration is timed 20:45.
- C4null's check commit also edited `probe_split.py`. The edit only replaced the imported `check` with a local copy that tolerates an aged-out robot; the split code is untouched (diff hunks at lines 40 and 145 only).

**The world is the only change.**
- C1 changes groups of 8 against 4. The remainder forms a smaller last group, which is how `ecology.py` `_challenge` cuts.
- C2 changes `food.work_cost` 0.08 against 0.03.
- C3 changes `food.items` 6 against 12.
- C4null is the adversary's flat against random, unchanged.
- In all four, the draws come from `Random("RBT-101 refund SEED")` with D = 4. The shuffle is `"SEED POP KIND DRAW"`, and the population is the lineage rule at T + r. All three match the adversary's.
- cull20 is read on the new world only, as registered.

**Exclusions are as registered and correct.** I checked each against `state.json` and the lineage.
- C1 seed 2: the shift checkpoint covers seasons < 473, and T + 110 = 492.
- C2 806, 807 and 2: the designed fauna is extinct in the shift arm at T + 110 and T + 190.
- C3 806 and 3: extinct at T + 110.
- C4null 804: the checkpoint covers seasons < 548, and T + 190 = 548.
- Nothing is substituted anywhere.
- C1's coverage rule ("highest season played + 1") would count a partial season: `s92-1`'s lineage reaches 504 while its `state.json` says 504. No read point falls there, so this is harmless.

**Reproduction.**
- `probe_reproduce.py` was written from the pre-registration and `probe_refund.py`, not from the analysts' code.
- It reproduces all 24 per-seed vectors at T + 110 (RESPONSE and RESPONSE_null, per fauna and paired, all four parts) to the printed 3 decimals: max |difference| ≤ 0.0005 (R1).
- C4null's 18 reproduction lines are identical to `runs/RBT-101/readout-adversary/probe_refund.txt`.

### F2: NONE. Harness checks pass, and on the new worlds too.

**The analysts' checks** all reproduce every compared bout to 4 decimals:

| part | check | bouts |
|---|---|---|
| C1 | baseline seed 3, T − 1 | 32/32 |
| C1 | shift arm seed 3, T + 110, recorded groups `[8 ×7, 4]` | 64/64 |
| C2 | baseline T − 1 | 32/32 |
| C2 | shift T + 1 at 0.08 | 32/32 |
| C3 | baseline T − 1 | 32/32 |
| C3 | shift seed 1, T + 110 at 6 items, including a designed arena of 2 | 18/18 |
| C4null | seed 801, T − 1 | 30/30 |

C4null's check has 2 further bouts by robots with no lineage row, which are not compared.

**My checks** (`probe_check.txt`) re-simulate the shift arm's own season T + 110 on two further seeds per part. They use my own world construction on the baseline's config plus the one change.
- C1: 60/60 and 64/64, in groups of 8.
- C2: 29/29 and 29/29.
- C3: 30/30 and 21/21.
- C4: 32/32 and 32/32 on flat ground. No analyst had checked the flat world against a recorded flat season.

The split's new world is the ecology's new world, bout for bout.

### F3: MUST-FIX (wording of the ruling and of paper 9 lesson 8). The split's RESPONSE is not a response to the changed world unless it is read against the old world too; on C4 it is not.

**What RESPONSE measures.** RESPONSE = gain(shift pop, new) − gain(base pop, new).
- It is any difference between the two populations, evaluated on the new world.
- The part that is about the change is RESPONSE(new) − RESPONSE(old), the same two populations on the old world.
- Every analyst printed the old-world line; nobody read it. `probe_pool.txt` P3 reads it at T + 110:

| | RESPONSE, new world | RESPONSE, old world | new − old (world-specific) |
|---|---|---|---|
| **C4 paired** | +0.272 [+0.053, +0.491], 8/10 | **+0.248 [+0.063, +0.433], 9/10** | **+0.024 [−0.115, +0.163], 7/10** |
| C4 designed | −0.222 | −0.174 [−0.312, −0.036], 1/10 | −0.048 [−0.156, +0.060] |
| C4 null, paired | +0.199 | +0.176 [+0.019, +0.333] | +0.023 |
| **C2 designed** | +0.571, 7/7 | +0.096 | **+0.475 [+0.309, +0.640], 7/7** |
| C2 co-evolved | +0.278 | +0.222 | +0.056 [+0.004, +0.108], 8/10 |
| C2 paired | −0.229 | +0.164 | **−0.394 [−0.562, −0.225], 0/7** |
| C3 co-evolved | +0.194 | +0.329 | **−0.134 [−0.208, −0.061], 0/10** |
| C1 paired | −0.008 | −0.030 | +0.022 [−0.202, +0.245] |

**Consequences:**
1. **C4's +0.27 is not a response to flat ground.** The post-event co-evolved − designed difference is as large on random terrain as on flat. The no-challenge null has the same shape, on both terrains.
   - "The first resolved non-arithmetic effect in phase 2" must not be read as an adaptive response to the challenge.
   - At r = 110 it is a general post-event population difference, of the same size and kind as turnover.
   - "C4-SPECIFIC" should be glossed that way, not as "a response that only C4 elicits".
2. **The one clearly world-specific response in the four challenges is C2's designed fauna**: +0.475, 7/7, which is work not done at the new price.
   - Paired, C2's world-specific response resolves toward the designed body (0/7). That is against H.
3. **Post hoc, and not a verdict input: C4's designed decline is resolved net of turnover on the old terrain.**
   - Designed RESPONSE − null on random: −0.151 [−0.282, −0.019], 2/10.
   - On flat: −0.198 [−0.447, +0.052].
   - The designed population that lived through the flat episode is worse on the terrain it no longer faced. That is the shape the coordinator's prior named ("a large refund to relax selection"). It is a hypothesis for RBT-107, not a finding here.

**Fix:**
- The ruling and paper 9 describe C4's RESPONSE as population-general.
- Lesson 8's rule gains one clause: "read the response on the old world as well; only new − old is a response to the change."

### F4: CAVEAT. "Pooled" was undefined. Every defensible pooling excludes +0.27, and the seed-aggregated one is the right primary. (`probe_pool.txt` P1, P2)

| pooling of the C1–C3 paired RESPONSE at T + 110 | mean [95% CI] |
|---|---|
| (a) 24 seed × challenge values as independent, t(23) | −0.076 [−0.207, +0.055] |
| **(b) seed-aggregated (mean of each seed's available challenges), t(9)** | **−0.050 [−0.147, +0.047]** |
| (c) fixed-effect inverse-variance of the 3 challenge means | −0.036 [−0.128, +0.057] |
| (d) the challenge as the unit (3 means), t(2) | −0.085 [−0.396, **+0.226**] |
| (e) DerSimonian–Laird random effects (τ² 0.0016) | −0.044 [−0.153, +0.066] |
| (f) the 6 seeds with all three challenges | −0.116 [−0.233, +0.001] |
| (b) under the played membership rule (F9) | −0.063 [−0.178, +0.052] |

- **The coordinator's two numbers are right.** (a) and (b) reproduce exactly.
- **(b) is the right primary.**
  - C1–C3 share each seed's baseline population, and each RESPONSE subtracts it.
  - The seed is the independent unit.
  - (a) counts a seed up to three times.
- **(a) is not anti-conservative here, but it is not the right model.** The within-seed correlations of the paired RESPONSE across challenges are not positive: r(C1, C2) −0.79, r(C2, C3) −0.74, r(C1, C3) +0.33, on n 6–7. The same-population null correlates +0.07 to +0.74.
- **Even the most conservative pooling, (d), excludes +0.27.** Its CI tops out at +0.226.
- **The rule compared a CI with a point.** As a two-quantity comparison, C4 minus the seed-aggregated C1–C3 value, paired on seed, is +0.322 [+0.125, +0.519], 9/10.
- **The verdict does not depend on the pooling.** Record (b) as the ruling's "pooled", and label the choice post hoc.

### F5: CAVEAT. C4null is correct. "The turnover null matches most of +0.27" is right at r = 110, but the depth story rests on seed 801. (`probe_pool.txt` P3, P5; `probe_reproduce.txt` R3)

**Reproduction.** C4null's 18 lines are identical to RBT-101's adversary. My independent read gives the same per-seed values (F1).

**Construction.**
- cull20 is RBT-92's arm: 20 of each fauna culled at T, group size 4, random terrain.
- It is read on flat ground at T + r, with the adversary's draws. Its shuffle key is `"SEED cull20 KIND DRAW"`.
- That is the registered null.

**At r = 110 the null is 73% of the RESPONSE:** +0.199 against +0.272. Net of the null, +0.072 [−0.183, +0.327]. And by F3 neither the null nor the response is specific to flat ground.

**Time course of the paired RESPONSE and its null:**

| r | RESPONSE | null |
|---|---|---|
| 50 | −0.02 | +0.01 |
| 110 | +0.27 | +0.20 |
| 190 | +0.42 | +0.09 |

The null is non-monotone. At r = 190, seed 801's null is −0.93, with a designed null of +0.69 on flat against −0.05 on random: a flat-specific outlier in one cull20 population.
- Without 801, the r = 190 null is +0.198 [−0.039, +0.436], the same as at r = 110.
- Without 801, the net is **+0.117 [−0.177, +0.411]**, against +0.309 with it. The median of the 9 is +0.25.
- "The pattern grows with depth while the null fades" therefore depends on one seed. Net of the null, growth with depth is not shown.

**The sign guard.** Re-grouping the same populations (the played rule, F9) moves C4's paired RESPONSE to +0.245 and its count from 8/10 to 7/10. Per-seed signs agree on 7/10 seeds.

**Scale.** The per-seed RMS of C4's paired null is 0.33 (P6). That is in simulated single-season gain, noisier than R-body.
- RBT-105's A/A, in its permitted form, is a comparator of scale for a paired R-body contrast: 0.10–0.17 (0.132 at RBT-92's recovery window). It is not a bound and not a null for any event.
- The split's per-seed values sit at or above that scale.
- No single seed of this split, 801 included, is readable alone.

### F6: CAVEAT. C1's weak sim-to-observed agreement is the split's measurement noise, not a harness that misses crowding. The NOT DECIDED stands. (`probe_observed.txt`, `probe_reproduce.txt` R2, `probe_check.txt`)

**The harness is the ecology in 8s.** Three recorded seasons of groups of 8 reproduce bout for bout (64/64, 60/60, 64/64). Group composition is the ecology's, as cut: a shuffled cohort of one fauna in consecutive 8s.

**The +0.22 compares unlike quantities.** R-body is a lifetime-mean axis over [T+60, T+160) (lesson 4). The like-for-like comparison is the ecology's recorded per-bout gains near T + 110:

| comparison | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| mean paired TOTAL, simulated | +0.126 | +0.418 | +0.142 | −0.450 |
| mean paired TOTAL, recorded [T+100, T+120) | +0.024 | +0.396 | +0.120 | −0.448 |
| per-seed r(simulated, recorded window) | +0.13 | +0.37 | +0.63 | +0.81 |
| per-seed r(recorded window, R-body) | +0.85 | +1.00 | +0.65 | +0.88 |

- Per fauna on C1, the recorded window gives co-evolved −0.032 against the simulated +0.001, and designed −0.056 against the simulated −0.125.
- **Why the per-seed r is low on C1:**
  - The noise of one seed's paired RESPONSE over the D = 4 draws is se ≈ 0.20 on C1.
  - The whole between-seed sd is 0.16.
  - On C1, essentially all of the per-seed spread is draw noise.
  - On C4, the true between-seed spread (TOTAL sd 0.22, dominated by the refund) is large enough to show r = 0.8.
- **What this means for the NOT DECIDED.**
  - The between-seed t CI contains that noise by construction, so the CI and the MDE (0.149) are valid. They are wider than a noise-free readout would give.
  - C1 is uninformative seed by seed but not biased.
  - The one mean discrepancy is +0.07 on the designed side of TOTAL, not resolved. It sits in the REFUND (base in 8s against 4s), not in the RESPONSE.
  - +0.27 remains far outside C1's CI under both membership rules. The played rule gives −0.116 [−0.305, +0.072].

**D = 4 was registered and must stay.** A future split that wants per-seed readings needs D ≥ 16.

### F7: CAVEAT. C2's designed RESPONSE, +0.57, stands as worded, conditional on survival. Survivorship cannot produce it. (`probe_pool.txt` P3, P4; R3)

**At r = 50 all 10 seeds are present, and the designed RESPONSE is +0.334 [+0.151, +0.516], 9/10.**
- Conditioning does flatter it:
  - The 3 later-extinct seeds had −0.094, +0.020 and +0.278 at r = 50, a mean of +0.07.
  - The 7 survivors had +0.447.
- If the doomed seeds had kept their r = 50 values, the 10-seed r = 110 mean would be +0.420 [+0.214, +0.626].
- To bring it to 0, the three extinct seeds would need −1.33, more than the entire designed price (REFUND −0.968).

**It is world-specific.** New − old is +0.475 [+0.309, +0.640], 7/7 (F3), so it is a response to the price. The survivors' gaits do less work.

**Under the played rule it is +0.463, 7/7.**

**Recommended wording:** "the designed fauna born under dearer work does better at the dearer price than its no-event contemporaries: +0.57 on the 7 seeds where it survives, +0.33 on all 10 at T + 50".

**RBT-107 consistency (the 21:52 disclosure).**
- RBT-107's garden gives designed A_SB +0.47 and paired −0.173 at about r = 240.
- This split gives +0.45 and −0.13 at r = 190.
- They agree in sign and size.
- **This is not independent confirmation.** The garden measured the same arms' populations at a neighbouring depth on other worlds. The agreement shows the common-garden measurement reproduces across harnesses, not that the effect replicates.

### F8: NONE. C3's small-population caveat does not bite. (`probe_c3_density.txt`)

C3's analyst flagged that the designed shift populations at T + 110 (1, 2, 5, 6 and 15 on 805, 1, 801, 2 and 4) forage in smaller arenas.
- I re-read the baseline's designed population on the 6-item world in arenas of 1, 2, 3 and 4, weighted to the shift population's arena sizes.
- The mean over the five seeds moves from +0.225 as run to +0.239 matched.
- Per seed, the density effect ranges from −0.16 to +0.15, with no sign pattern.
- Fewer mouths per arena is not income on this world. Seed 1's +1.06 is its two robots, not their arena.
- The analyst's post hoc subset (≥ 12 designed alive) is correctly labelled post hoc. The density reading it hinted at is not supported.

### F9: CAVEAT. The shared membership rule drops the robots that age out at the read season, and re-grouping shows how fragile per-seed signs are. (`probe_reproduce.txt` R3, R4)

**The lineage rule** counts a robot "alive at T + r" only if `lineage.jsonl` has a row at that generation. The adversary's rule, inherited by all four analysts, is that rule.
- A robot that plays season s and ages out at its end has no such row.
- At T + 110 this drops 27–56 robots per arm across the 10 seeds, about 3.5% of each population and always the oldest.
- C4null's check tripped on one.

**Including them** (the played rule, from `cohorts.jsonl`) also re-cuts every arena under the same stream. The paired RESPONSE moves as follows:

| part | lineage rule | played rule |
|---|---|---|
| C1 | −0.008 | −0.116 [−0.305, +0.072] |
| C2 | −0.229 | −0.165 |
| C3 | −0.018 | −0.037 |
| C4 | +0.272 | +0.245 [+0.031, +0.458], 7/10 |

- No verdict changes. The seed-aggregated pool is −0.063 [−0.178, +0.052].
- **Test-retest.** The per-seed played − lineage sd is 0.18–0.25, and signs agree on only 5/7 to 7/10 seeds.
- This is paper 9's "jitter the sign guard" in a new place. Counts such as 8/10 and 9/9 in this split are not stable under re-grouping and should not carry sentences.
- The registered rule is the lineage rule, and it stays.

### F10: CAVEAT. Lessons 1–8, as applied.

| lesson | status |
|---|---|
| 1, placebo onsets | Not applicable: no class rule is read. The cull20 null plays the placebo's role. |
| 2, event − null | Applied in all four parts. The net-of-null lines are the ones that change readings (C4). |
| 3, arithmetic first | Applied: REFUND is printed everywhere. |
| 4, no recovery claims | None made. F6 notes that R-body is the lifetime-mean axis. |
| 5, survival under refill | The exclusions use extinction, a non-refilling fact. Correct. |
| 6, UNVALIDATED means unread | Every read is validated (F2). |
| 7, the bracket | C2 and C3 excluded extinct seeds as registered, and stated the conditioning. No bracket was computed. For C2, F7 supplies the missing half, the unconditioned r = 50 value and the break-even −1.33. For C3 the paired n = 8 result is NOT DECIDED either way. |
| 8, the split | Needs the old-world clause (F3). |
| smaller rules | "Jitter the sign guard" is unmet (F9). "Label outcome-defined subsets post hoc" is met by C3. |

---
_Generated by [Claude Code](https://claude.ai/code)_
