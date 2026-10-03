# RBT-129 Stage P (pilot) + Stage 0 (census): readout

Plan: `READOUT-PLAN.md` (`f4a9bff`, pushed before any output was opened). Script: `stageP0_readout.py` →
`stageP0_readout.txt`. Files: `integrity.txt`, `dupverify.txt`, `pilot_constants.json`, `power_stageP.txt`.
Launch `716e2d3`, lane fix `02bf3b6`. Stage P makes no layer call (§4.1). **Stage 1 is not launched, and n is the
coordinator's ruling.**

**Revision after the adversary (#491, CONFIRMED WITH CAVEATS; coordinator's ruling on #490).** This adds the known
founder outcomes and the effective n (§5; MUST 1), what §6.1's registered calls do with them (§5; MUST 2), labels
for the three rules added after the plan with both values (§8; MUST 3), and SHOULD 1–5 (§4, §3(d), §6, §1). New files:
`founders.py` → `founders.txt`. **No registered number changes.**

## Summary

- **Integrity: clean.** All 542 of 542 expected branches are present, plus the 4 `-unit` branches, and all 546 run
  directories restored. The free K1-type control (pilot season 60 against the census run) is 12 of 12 PASS. K1 is PASS
  at `c1-p030-U-L` and `c0-p030-U-L`. It is UNTESTABLE at `c1-p030-PW-G` (129001 extinct pre-merge, and there is no
  re-run on 129002) and at `c2-p030-PW-G` (no seed reached season 60). No point is VOID.
- **More pre-merge extinctions than logged.** The log named 3 at `c2-p030-PW-G`. In fact all **4** of its seeds died
  (at seasons 29, 15, 14 and 32), and so did `c1-p030-PW-G/129001` (season 49).
- **DUP-VERIFY: both REPLACED.** `P/c1-p030-PW-G/129002/M` and `P/c1-p030-U-L/129002/S` each differ from their clean
  re-run only by duplicated rows in `lineage.jsonl` and `cohorts.jsonl`: seasons 176–211 in the first and 73–78 in the
  second. Every other file is byte-identical. The clean re-runs are the data. No registered number changes, because
  the holistic fauna is extinct pre-merge in both units.
- **The pilot cannot supply the per-seed SD under the plan's rule.** No pilot point has 3 or more seeds with both
  faunas alive in seasons 240–299. The holistic fauna is extinct at 129002 and 129003 at both U-L points, and by
  season 240 at every PW-G seed. So `power.py` part 1 keeps the **registered bounds 0.144 and 0.334**. The only
  pilot estimate is 0.275 (2 points × 2 seeds, df 2). It is printed as descriptive and is not a constant.
- **The other constants, as planned:**
  - null y′ SD 0.229, from **4** valid N runs (df 3; the design expected 12, df 11). Seven N runs had a fauna extinct
    at the merge and are invalid for the share test (§6.1 item 2).
  - real/replica drift ratio r = 0.229 / 0.150 = **1.53**.
  - cost per arm-season **23.3 core-s** (median over 15 arms), and **43.7** (the highest point's mean, at
    `c1-p030-U-L`). These replace 20 and 25.
- **Stage 1 power at n = 8** (income layer, |H − D| = 0.4, BH-half threshold):
  - **0.827** at the registered ceiling SD 0.334;
  - 1.000 at the floor 0.144;
  - 0.938 at the descriptive 0.275.

  **On the letter of §4.1 the fallback does not trigger:** power is at least 0.5 at every SD considered.
  **On the substance it fails:**
  - The founder draws are known. Draws 129001, 129004, 129005 and 129006 found a holistic fauna; 129002, 129003,
    129007 and 129008 fail by season 14 (`founders.txt`).
  - So Stage 1 at n = 8 has **at most 4 valid seeds at every point, and at most 3 at 12 of the 36**.
  - At n_valid = 4 the power is **0.381 at SD 0.334** (below 0.5) and **0.510 at SD 0.275** (exact values from the
    adversary; the simulation here gives 0.383 / 0.508).
  - Under §6.1, **every Stage-1 point is PARTIAL or EXCLUDED at n = 8 and n = 12** (§5).
  - The coordinator rules n.
- **Census (Stage 0):**
  - **The holistic fauna is FOUNDING-FAIL at 150 of 150 points.** Its founders are the same draw at every point for
    a given seed (1 founder set per seed over all 150 points). The draws for seeds 129002 and 129003 go extinct at all
    150 points (seasons 11–51). Seed 129001 goes extinct at 38 points.
  - **The designed fauna is FOUNDING-FAIL at 34 of 150 points** (26 PW, 5 U, 3 HP), all at c ≥ 1 or p ≥ 0.053.
  - C1 finds **13 rows** with more than one sign change; they enter R-A's pair list at Stage 2a.
  - Census g0 is ≤ 0.8 at 46 points and ≤ 1.0 at 63. It cannot be computed at 11 points, where both faunas are gone
    in seasons 30–59.

## 1. Integrity (`integrity.txt`)

- **Branches and restore:** all 542 of 542 branches are present, plus the 4 `-unit` branches, and all 546 run
  directories restored.
- **Done-markers:** 542 of 546 are present. The 4 missing are the k1 jobs' K1fork markers, which only later code
  writes. K1's verdict comes from each unit record's `K1.txt`, the registered first source, and agrees with the
  `-unit` branches.
- **Quarantined census jobs:** the four quarantined originals are lost and are not used. Their clean re-runs are on
  their branches. Each has one invocation, its done-marker and state at season 60.
- **Pre-merge extinctions:** every one has its `EXTINCT.txt`. None had an all-empty ckpt60: the snapshot job skipped
  each one, so none has ckpt60 state at all.
- **K1 on PW terrain (SHOULD 4):** K1 was never tested on a PW terrain. Its seed 129001 is extinct pre-merge at
  both PW-G pilot points, and no K1 re-run on 129002 at `c1-p030-PW-G` exists on any branch. Whether that re-run is
  wanted before Stage 1 is for the coordinator. It costs one 65-season run and a 5-season fork.

## 2. DUP-VERIFY (`dupverify.txt`)

Each unit was re-run from its season-60 checkpoint on a `02bf3b6` worktree, using its own lane line, with
`NO_DURABLE=1` and `WORKERS=2`, on python 3.11.15, mujoco 3.14.0 and numpy 2.4.6 (the runs' platform). The re-run
was compared with the saved run by `k1_compare`.

| unit | result | difference |
|---|---|---|
| P/c1-p030-PW-G/129002/M | **REPLACED** | saved lineage +1,974 duplicate rows, cohorts +36 (seasons 176–211); 3,599 other files identical |
| P/c1-p030-U-L/129002/S | **REPLACED** | saved lineage +375 duplicate rows, cohorts +6 (seasons 73–78); 801 other files identical |

## 3. Pilot constants (`stageP0_readout.txt`, `pilot_constants.json`)

**(a) Per-seed SD of H − D** (S arm, seasons 240–299, income = food − p · work / 1000; `last_score` agrees on all
49,391 rows):

| point | valid seeds | H − D per seed | SD |
|---|---|---|---|
| c1-p030-U-L | 2 (129001, 129004) | +0.425, −0.015 | 0.312 |
| c0-p030-U-L | 2 (129001, 129004) | −0.003, −0.334 | 0.234 |
| c1-p030-PW-G | 0 | holistic extinct at every seed by 240; 129001 extinct pre-merge | — |
| c2-p030-PW-G | 0 | all 4 seeds extinct pre-merge | — |

No point has n ≥ 3, so the plan's constant does not exist. **Part 1 of `power.py` keeps the registered 0.144 and
0.334.** This is the plan's rule applied as written, and it is not a substitution. The pooled 0.275 (df 2) is
descriptive only.

**(b) Null y′ SD:** 0.229 over 4 runs (df 3), from `c1-p030-U-L` and `c0-p030-U-L` at seeds 129001 and 129004.
- The 7 other N runs had a fauna extinct at the merge. They are excluded by §6.1 item 2, which says such a seed is
  not valid for the share test. The plan did not state this exclusion; it applies the registered validity rule and
  is disclosed here.
- The kind-offset-removed SD is 0.108 (df 2); it is descriptive.
- The M arms' y′ at the same 4 seeds are −0.445, −0.247, −0.390 and −0.301 (holistic share falling). They are
  descriptive, and no call is made from them.

**(c) Drift ratio:** the replica's shuffle null SD is 0.150 (the mean of `power.txt` §2's four edge-0 rows), so
**r = 1.53**. On df 3 the ratio's 90% interval is wide, about 0.95–4.5 (χ² on df 3). The point estimate is used, as
registered.

**(d) Cost per arm-season:**
- **23.3 core-s** (median over 15 arms) and **43.7** (the mean at `c1-p030-U-L`).
- By point: c0-U-L 22.7, c1-PW-G 9.7 (thin populations).
- **Exclusions (SHOULD 2):** 18 of the 33 S, M and N arms of the 11 units that reached season 60 were excluded:
  - 13 were resumed after a container restore (more than one `--resume` in `command.txt`: 9 with 3, 4 with 2);
  - 3 have no season lines (the N arms whose kept fauna was empty at the merge);
  - 2 are the DUP-VERIFY re-runs, timed on this container rather than a launch host.

  The adversary counts 23 of 38 on a different basis, which also includes the arms of units that went extinct
  pre-merge.
- **Mixed arms (SHOULD 2):** the median of 23.3 mixes single-fauna arms (for example 13.6, 10.1 and 2.7 core-s, where
  the holistic fauna is gone) with two-fauna arms (about 24–58). A Stage-1 arm with both faunas alive is likely to
  cost more than 23.3.
- **The ceiling:** 43.7 is the mean at `c1-p030-U-L` on shared hosts, with two lanes on each 4-core session. The
  per-arm range is wide (2.7–58.4).

## 4. `power.py` re-run (`power_stageP.txt`)

`power.py` now reads `--pilot pilot_constants.json`. Without the flag its defaults are the registered values and the
code is unchanged. With the flag it changes only the part-1 SDs (unchanged here), the core-s in part 4, and the
replica's y′ spread (× 1.53 about each cell's mean). It also prints section 0, the §4.1 test.

| per-seed SD | n 4 | n 6 | **n 8** | n 12 |
|---|---|---|---|---|
| 0.144 (registered floor) | 0.944 | 1.000 | **1.000** | 1.000 |
| 0.334 (registered ceiling) | 0.383 | 0.654 | **0.827** | 0.965 |
| 0.275 (descriptive pilot) | 0.508 | 0.809 | **0.938** | 0.995 |

What else the re-run moves (these are consequences of the constants, not calls):
- **Budget (part 4):**
  - At 23 / 44 core-s, the registered plan (n 8, R-B to 16) is ≤ 3,013–3,232 / 5,326–5,545 core-h, about 75–81 /
    133–139 h of wall on 40 cores. **These are `power.py` part 4's ungated programme totals** (P + 0 + 1 + 2a + 2b),
    not §11.2's gated budget and not the Stage-1 cost. Stage 1 alone, on the same formula, is 1,358–2,512 core-h
    (the adversary's figure). **§11.2's gated table was not re-costed** at 23.3 / 43.7 (SHOULD 1).
  - `power.txt` gave ≤ 2,633–2,852 at 20 core-s and ≤ 3,200–3,419 at 25 core-s.
  - Part 4's header text still says "20 core-s … ceiling 25". That is a printed literal; the rows use the pilot's
    values.
- **Share layer (part 2, and r3 §5′):**
  - With the replica's y′ spread × 1.53, the null SD is 0.22–0.24, and the share WIN at edge 0.15 falls. At g0 0.8 it
    drops from about 0.32 / 0.79 to 0.09 / 0.48 at n 8 (q/36, q/2).
  - RESOLVING under shuffle now holds only for g0 in [0.50, 0.65] at n 8 and n 16. The [0.65, 0.80] band no longer
    resolves at n 16.
  - Under shuffle, the share layer is therefore resolvable at even fewer points than §10.1 expected.
  - These follow mechanically from r = 1.53 on df 3.

## 5. The §4.1 fallback

**On the letter of §4.1 it does not trigger.** Stage 1 at n = 8 has power ≥ 0.5 for the income layer at |H − D| = 0.4,
BH-half threshold, at every SD considered: 0.827 at the registered ceiling. `power.py`'s n is the number of seeds, and
seed validity is not one of its constants. **The coordinator rules n.**

**On the substance it fails, because the founder draws are already known** (`founders.txt`; MUST 1):

| draw (seed) | 129001 | 129002 | 129003 | 129004 | 129005 | 129006 | 129007 | 129008 |
|---|---|---|---|---|---|---|---|---|
| holistic at `c0-p030-U-L`, season 59 | 60 alive | extinct (last 10) | extinct (last 14) | 60 alive | 60 alive | 60 alive | extinct (last 14) | extinct (last 14) |

- **Sources:** 129001–129003 are the census S runs; 129004 is the pilot S; 129005–129008 are the four
  anchor-fallback S 0–59 runs in the P-0 lanes (`ckpt/rbt-129-stage0-c0-p030-U-L-12900[5-8]-S`). The first version
  of this readout did not read the anchor runs.
- **Founder identity:** the holistic founders are the same draw at every point for a given seed (1 founder set per
  seed over all 150 census points). Draws 129002 and 129003 die at all 150 points.
- **Stage 1's seeds:** Stage 1's S arms at 129001–129003 resume from the census state (§11.1 note, ruled 02:22), and
  for 129002 and 129003 that state has no holistic member. `ecology.py` never re-seeds a population. Seeds 129007 and
  129008 run fresh, but their founders are the draws that died by season 14.
- **So at n = 8, at most 4 seeds are valid at every Stage-1 point (1, 4, 5, 6).** At the 12 points where 129001 has
  lost a fauna by season 59, at most 3 are valid:
  - holistic lost: c0-p010-PW-G, c0-p080-PW-G, c1-p010-PW-G, c1-p030-PW-G, c1-p080-PW-G, c2-p010-PW-G, c2-p030-PW-G,
    c2-p080-PW-G, c1-p080-PW-L;
  - designed lost: c2-p080-U-G, c2-p080-HP-G, c1-p030-PW-L.
- **§4.1's power at n_valid = 4:** **0.381 at SD 0.334** and **0.510 at SD 0.275**. These are the adversary's exact
  noncentral-t values; `power_stageP.txt` section 0's simulation gives 0.383 / 0.508. At the registered ceiling this
  is below 0.5.
- **Neither registered fallback fixes it.** Dropping points does not raise the valid seeds per point, and n = 12
  raises them only to about 6.

**What the registered rules do with this (§6.1; MUST 2).** A seed is valid for income only if both faunas are alive
in S through season 239, and for the share test only if both are alive at the merge. Invalid seeds are counted and
reported, never averaged. The call order is EXCLUDED (a fauna extinct by 299 on ≥ 5 of 8 seeds, or ≥ 10 of 16), then
PARTIAL (fewer than 6 of 8, or 12 of 16, valid for the share test; never a WIN). Applied mechanically:
- **At n = 8, every Stage-1 point is PARTIAL or EXCLUDED.**
  - At the 24 points where 129001 founds, at most 4 of 8 seeds are valid at the merge, so the point is PARTIAL-D at
    best, and EXCLUDED-H if any of draws 1, 4, 5 and 6 loses the holistic fauna by 299.
  - At the 9 points where 129001 also loses the holistic fauna, it is extinct on ≥ 5 of 8 seeds, so the point is
    EXCLUDED-H.
  - At the 3 points where 129001 loses the designed fauna, the point is at least PARTIAL.
- **At n = 12 the same holds** under any proportional threshold (at most about 8 valid < 9). §6.1 registers no n = 12
  threshold, so ruling n = 12 also means ruling one.
- **At n = 16,** PARTIAL is avoided only if all 8 new draws found. At a founding rate of 0.5 that probability is
  0.004.
- **This is the registered handling.** The body call becomes a survival call set by which founder draws the seed
  numbers fix. Any change to seeds or founding would be a data-informed amendment, made after the census was seen:
  replacing or skipping draws, re-drawing founders, seeding from survivors, or redefining validity. §5.2 fixes the
  seeds, and §4.2 forbids adding seeds except by a new registration. This readout does not propose or choose one.
- The adversary's `ADVERSARY.md` "Input for ruling n" table gives the expected valid seeds, power, P(EXCLUDED) and
  cost at n = 8, 12 and 16.

## 6. Stage 0 census-layer calls (§5.1, by the registered rules)

- **C2 FOUNDING-FAIL** (extinct at season 59, before refill, on ≥ 2 of 3 seeds; provisional and flagged; never
  EXCLUDED):
  - **Holistic: 150 of 150 points.**
    - Seeds 129002 and 129003 are extinct at every point (seasons 11–51, median 15–19). Seed 129001 is extinct at 38
      points.
    - The holistic founders are identical across points for a given seed: 1 founder set per seed over all 150 points
      × 3 seeds (`founders.txt`; SHOULD 5).
    - So the 150 calls rest largely on 2 founder draws, not on 150 independent foundings. The call is made as
      registered, and this dependence is its main caveat.
    - Founder solvency for the holistic fauna is 0.01–0.03 at every point.
    - §12 prediction 3 registered FOUNDING-FAIL for the holistic fauna "at the poorest points". It occurs everywhere.
  - **Designed: 34 of 150 points** (26 PW, 5 U, 3 HP), all at c ≥ 1 or p ≥ 0.053. The list is in
    `stageP0_readout.txt`.
- **Founder solvency** is per fauna and point in `stageP0_readout.txt`. Designed solvency falls with price and on
  PW, from 0.79 at c0-p010-U-L to 0.01–0.02 at c2-p080-PW-*.
- **The regime early** (seasons 30–59, window-local saturation and viability, `scripts/regime.py`) is per point and
  fauna in the table. Where the holistic fauna survives at all, it survives on one seed, so its figures are
  single-seed.
- **Census g0** (seasons 30–59, faunas pooled, + 0.35): ≤ 0.8 at 46 points and ≤ 1.0 at 63. It is unavailable at 11
  points, where both faunas are gone by season 30–59. It feeds the M/N gate, which the coordinator applies.
- **C1 (monotonicity):** 13 rows have more than one sign change: 9 price rows and 4 clutter rows. They are listed in
  `stageP0_readout.txt`, and each enters R-A's pair list at Stage 2a.
  - The census income difference is undefined at 36 points (no holistic member-seasons in 30–59 on any seed). Those
    points are skipped in the sign count, so a counted "sign change" can span a gap on the grid (SHOULD 3).
  - At almost every defined point the difference rests on seed 129001 alone, so the 13 rows are noisy.
  - This caveat matters most because C1's rows feed refinement.
- **C3** is NOT RUN (not in the P-0 lanes). **PAYS** is read by #467 and #487, not here.
- The side effects (R10) are in the per-point table, against `c1-p030-U-L`. They are descriptive.

## 7. Caveats

- **The deciding caveat:** founding, not power. At most 4 of 8 seeds are valid at every Stage-1 point, so under
  §6.1 every Stage-1 point is PARTIAL or EXCLUDED at n = 8 and n = 12 (§5).

- Every pilot constant is thinner than the design assumed:
  - the per-seed SD is unobtainable;
  - the null SD rests on 4 runs;
  - the cost comes from 15 arms on shared hosts.
- The Stage-1 power answer relies on the registered SD bounds, not on a pilot measurement.
- The census's holistic layer is dominated by the per-seed founder draw. "150 of 150" should not be read as 150
  independent failures.
- The DUP-VERIFY replacements were done as ruled. They change no registered number.
- Stage P makes no layer call. Nothing here is a body, share, perception or retention result.

## 8. Rules added after the plan (MUST 3)

These three rules were not in `READOUT-PLAN.md` (`f4a9bff`). Each is labelled here, with both values where there are
two. None changes a Stage-1 call.

1. **Excluding null runs with a fauna extinct at the merge.** Plan §3(b) says "the SD of y′ over all available N
   runs". The code applying §6.1 item 2 is in `eed9cb1`, after the plan.

   | reading | runs | null y′ SD | r = SD / 0.1497 |
   |---|---|---|---|
   | **used: both faunas alive at the merge** | 4 (df 3) | **0.229** | **1.53** |
   | all 11 N runs (the plan's literal text) | 11 (df 10) | 0.358 | 2.39 |

   **Why the 7 excluded runs are not drift nulls:**
   - At the 4 U-L runs one fauna is absent at the merge, so y′ = 0 by construction.
   - At `c1-p030-PW-G/129002`, y′ = −0.606 only because the population is small (26 at the merge) while the share is
     taken over 120 slots.
   - At `c1-p030-PW-G/129004`, y′ = −1.000 because the kept fauna is extinct by the window.

   Counting them would measure the /120 denominator and extinction, not drift. r feeds only the share layer, which
   §5 shows cannot be called at any Stage-1 point. At r = 2.39 it would be weaker still.
2. **Keeping the registered SD bounds (0.144 / 0.334) when no point has n ≥ 3.** The plan says the pooled SD decides
   §5. That SD is undefined, and the plan gave no fallback. `power.py` `load_pilot` (`29f35a8`) keeps the registered
   bounds and §5 is decided at the ceiling of 0.334, the conservative choice. The first version called this "not a
   substitution"; it is a post-plan choice. The descriptive pilot value is 0.275 (df 2).
3. **The (d) exclusions added in `29f35a8`:** the DUP-VERIFY re-runs and the arms with no season lines. (d) is
   unchanged at 23.35 / 43.72 by excluding the saved DUP arms: they already had more than one `--resume`, and the
   no-season-line arms have no timings. Timing the re-run in place of the saved M arm, as the first pass did, gave
   23.8 / 43.7. That arm was timed on this container, not on a launch host.
