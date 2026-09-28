# RBT-129 Stage P (pilot) + Stage 0 (census): readout

Plan: `READOUT-PLAN.md` (`f4a9bff`, pushed before any output was opened). Script: `stageP0_readout.py` →
`stageP0_readout.txt`. Files: `integrity.txt`, `dupverify.txt`, `pilot_constants.json`, `power_stageP.txt`.
Launch `716e2d3`, lane fix `02bf3b6`. Stage P makes no layer call (§4.1). **Stage 1 is not launched, and n is the
coordinator's ruling.**

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

  **The §4.1 fallback does not trigger:** power is at least 0.5 at every SD considered. The coordinator rules n.
- **Census (Stage 0):**
  - **The holistic fauna is FOUNDING-FAIL at 150 of 150 points.** Its founders are the same draw at every point for
    a given seed, and the draws for seeds 129002 and 129003 go extinct at all 150 points (seasons 11–51). Seed 129001
    goes extinct at 38 points.
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
- Arms resumed after a container restore were excluded (more than one `--resume` in `command.txt`), as were arms
  with no season lines and the DUP-VERIFY re-runs, which were timed here rather than on a launch host.
- The per-arm range is wide (2.7–58.4) because two lanes shared each 4-core host.

## 4. `power.py` re-run (`power_stageP.txt`)

`power.py` now reads `--pilot pilot_constants.json`. Without the flag its defaults are the registered values and the
code is unchanged. With the flag it changes only the part-1 SDs (unchanged here), the core-s in part 4, and the
replica's y′ spread (× 1.53 about each cell's mean). It also prints section 0, the §4.1 test.

| per-seed SD | n 4 | n 6 | **n 8** | n 12 |
|---|---|---|---|---|
| 0.144 (registered floor) | 0.944 | 1.000 | **1.000** | 1.000 |
| 0.334 (registered ceiling) | 0.383 | 0.654 | **0.827** | 0.965 |
| 0.275 (descriptive pilot) | 0.508 | 0.809 | **0.938** | 0.995 |

BUDGET_AND_SHARE

## 5. The §4.1 fallback

**It does not trigger.** Stage 1 at n = 8 has power ≥ 0.5 for the income layer at |H − D| = 0.4, BH-half threshold,
at every SD considered: 0.827 at the registered ceiling. Neither n = 12 nor dropping points is called for by the
registered test. **The coordinator rules n.**

What the registered test does not see, stated plainly:
- The power is per *valid* seed.
- The census shows the holistic founder draws for seeds 129002 and 129003 failing at every point. Stage 1's S arms
  at seeds 129001–129003 resume from the census states, so at every Stage-1 point at least 2 of the 8 seeds start
  with no holistic fauna.
- In the pilot, 2 of 4 seeds lost the holistic fauna even in the committed world.
- If half the seeds are lost, the effective n is about 4, where the table gives 0.38–0.51 at SD 0.275–0.334.
- §6.1's EXCLUDED rule (a fauna extinct on at least 5 of 8 seeds) would then read these points as survival calls
  rather than income calls.
- This is a founding question for the coordinator, not a power constant, and this readout makes no call on it.

## 6. Stage 0 census-layer calls (§5.1, by the registered rules)

- **C2 FOUNDING-FAIL** (extinct at season 59, before refill, on ≥ 2 of 3 seeds; provisional and flagged; never
  EXCLUDED):
  - **Holistic: 150 of 150 points.**
    - Seeds 129002 and 129003 are extinct at every point (seasons 11–51, median 15–19). Seed 129001 is extinct at 38
      points.
    - The holistic founders are identical across points for a given seed: the same 60 founders, with the same
      node-count fingerprint at the 3 points checked (c0-p010-U-L, c1-p030-PW-G, c2-p080-HP-G).
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
  - The census income difference at most points rests on one holistic seed, which makes these sign changes noisy.
  - This caveat matters most because C1's rows feed refinement.
- **C3** is NOT RUN (not in the P-0 lanes). **PAYS** is read by #467 and #487, not here.
- The side effects (R10) are in the per-point table, against `c1-p030-U-L`. They are descriptive.

## 7. Caveats

- Every pilot constant is thinner than the design assumed:
  - the per-seed SD is unobtainable;
  - the null SD rests on 4 runs;
  - the cost comes from 15 arms on shared hosts.
- The Stage-1 power answer relies on the registered SD bounds, not on a pilot measurement.
- The census's holistic layer is dominated by the per-seed founder draw. "150 of 150" should not be read as 150
  independent failures.
- The DUP-VERIFY replacements were done as ruled. They change no registered number.
- Stage P makes no layer call. Nothing here is a body, share, perception or retention result.
