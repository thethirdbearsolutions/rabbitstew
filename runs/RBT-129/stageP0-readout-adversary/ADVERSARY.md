# RBT-129 Stage P+0 readout: adversary

PR #490, head `c552a08`, base `claude/new-session-4cao7d`. Every number below was re-derived with my own code from the
`ckpt/rbt-129-stage{0,P}-*` branches, restored with `scripts/durable.sh restore` into a scratch directory. I did not
run the author's `stageP0_readout.py` or `power.py`. The scripts and their outputs are in this directory:

- `branches.py` → `branches.txt`
- `census.py` → `census.txt`
- `pilot.py` → `pilot.txt`
- `cost.py` → `cost.txt`
- `founders.py` → `founders.txt`
- `stage1_points.py` → `stage1_points.txt`
- `power_eff.py` → `power_eff.txt`. This one uses the standard library only: exact noncentral-t integration, no
  simulation.

## Verdict: **CONFIRMED WITH CAVEATS**

Every registered number in the readout reproduces from independent code:
- integrity;
- the census calls;
- constants (a) to (d);
- the power table;
- the budget.

The disclosed post-plan exclusion is the correct reading, and it changes nothing Stage 1 depends on.

The caveat is the item that decides the ruling, and the readout understates it:
- The founder outcome is already known for draws 129001–129008. Only 4 of the 8 found a holistic fauna, and the draws
  that fail do so at every point.
- So Stage 1 at n = 8 has **at most 4 valid seeds at every point, and at most 3 at 12 of the 36 points**.
- On the registered calls (§6.1 items 1–2), **every Stage-1 point is then PARTIAL or EXCLUDED at n = 8 and n = 12**,
  and almost surely at n = 16. The body call becomes a survival call set by the founder lottery, whatever the bodies
  earn.
- The income layer survives on about 4 valid seeds (n = 8), about 6 (n = 12) or about 8 (n = 16).

## 1. Order

- `f4a9bff` (21:36:24Z) adds only `READOUT-PLAN.md`. Every commit that carries output comes later:
  - `eed9cb1` (21:41), the script;
  - `d58b18b` (21:43), integrity;
  - `29f35a8` (22:37);
  - `3da29b9`;
  - `c552a08`.
- The plan is unchanged after `f4a9bff`.
- Git cannot show when the tarballs were first opened. The claim "no branch restored before the plan" rests on the
  author's statement.

**Rules added after the plan:**

1. **The §6.1 item 2 exclusion of null runs**, disclosed.
   - Plan §3(b) says "the SD of y′ over all available N runs". The code applying §6.1 item 2 is already in `eed9cb1`,
     5 minutes after the plan and before the integrity commit. It is still not in the plan.
   - Re-derived (`pilot.py`):

   | reading | runs | null y′ SD | r = SD / 0.1497 |
   |---|---|---|---|
   | valid only (the readout: both faunas alive at the merge) | 4 (df 3) | **0.229** | **1.53** |
   | all 11 N runs (the plan's literal text) | 11 (df 10) | 0.358 | 2.39 |
   | drop only the runs with K extinct at the merge | 6 | 0.178 | 1.19 |

   - The 7 excluded runs are not drift nulls. The 4 U-L runs have one fauna absent at the merge, so y′ = 0 by
     construction. At `c1-p030-PW-G/129002` y′ = −0.606 only because the population collapsed to about 47 while the
     share is taken over 120. At `c1-p030-PW-G/129004` y′ = −1.000 because K is extinct by the window. Counting them
     would measure the /120 denominator and extinction, not drift, so the exclusion is the right reading.
   - **Does it matter?** r feeds only the share layer (part 2 power, the RESOLVING bands, the gate rescale). §6 below
     shows the share call cannot be made at any Stage-1 point under the registered validity rule, so neither r moves
     a Stage-1 call. At r = 2.39 the share layer would be weaker still.
2. **Keeping the registered SD bounds when no point has n ≥ 3** (`29f35a8`, `power.py` `load_pilot`).
   - The plan says the pooled SD "decides §5". It is undefined, and the plan gives no fallback.
   - Keeping 0.144/0.334 and deciding at the ceiling is the conservative default, and DESIGN §4.1 permits only the
     pilot constants to change. It is acceptable, but it is a post-plan choice and is not labelled as one. The readout
     says "not a substitution".
3. **Excluding DUP-VERIFY re-runs and arms with no season lines from (d)** (`29f35a8`).
   - The saved DUP units would be excluded anyway: they have 3 and 5 `--resume` invocations. So (d) is unchanged at
     23.35 / 43.72.

## 2. Integrity

- **Branches.** `branches.py` builds the expected labels from the 20 lane files without `stages.py`: 546 jobs, 526
  run directories and 16 unit records, 542 in all. **0 missing.** Besides these, the remote has the 4 `-unit`
  branches and 48 PAYS branches that are not in the P-0 lanes.
- **Pre-merge extinctions.** The history files agree (`founders.txt`, `pilot.txt`):
  - All 4 `c2-p030-PW-G` seeds have no S beyond the snapshot.
  - `c1-p030-PW-G/129001`: both faunas are dead by season 47–48 (holistic last alive at 14, designed at 47). This
    matches "extinct pre-merge at season 49".
- **K1.** PASS at the two U-L points. UNTESTABLE at `c1-p030-PW-G` (129001 has no season-60 state, and no K1 run
  exists on 129002) and at `c2-p030-PW-G`. I agree with the calls. Neither PW-G point is a Stage-1 point that K1 is
  needed for before Stage 1, but K1 was never tested on a PW terrain.

## 3. DUP-VERIFY

This container has no mujoco, so I could not re-run either unit. What I checked on the saved logs (`pilot.txt`):

- **`c1-p030-PW-G/129002/M`**
  - lineage: 18,400 lines, 16,426 unique; the 1,974 extra lines are exact duplicates, all in seasons 176–211.
  - cohorts: 348 lines, 312 unique; 36 exact duplicates, in the same seasons.
- **`c1-p030-U-L/129002/S`**
  - lineage: 19,625 lines, 19,250 unique; 375 exact duplicates, in seasons 73–78.
  - cohorts: 326 lines, 320 unique; 6 duplicates, in the same seasons.
- After removing duplicates, the lineage rows per (season, fauna) agree with `history.json` in both units (0
  mismatches).
- These counts are exactly those in `dupverify.txt`.
- **No registered number changes:**
  - both units have the holistic fauna extinct at the merge (M: nH 0; S: holistic last alive at 18), so neither enters
    (a) or (b);
  - neither saved arm could enter (d) (more than one `--resume`).
- I could not independently check that every *other* file is byte-identical to the re-run. It rests on `k1_compare`
  in the author's run.

## 4. Power

- **Power reproduces.** Exact integration, t test, α = 0.05 two-sided (BH half), |H − D| = 0.4, n = 8:
  - **0.826** at SD 0.334 (claimed 0.827);
  - **0.939** at SD 0.275 (claimed 0.938);
  - **1.000** at SD 0.144.
- **The budget reproduces.** `power.py` part 4's formula, re-implemented, gives 3,013 / 3,232 / 5,326 / 5,545. These
  are the **ungated** programme totals, not §11.2's gated budget (SHOULD 1).
- **"Fallback not triggered" is correct on the letter of §4.1.**
  - The test is `power.py` re-run with the pilot's constants. Its n is the number of seeds, and seed validity is not a
    constant it models.
  - It is **not** correct on the substance. The effective n at every Stage-1 point is already known to be at most 4
    (§5 below). At n = 4, power is **0.381** at the registered ceiling of 0.334, below 0.5. At the descriptive 0.275
    it is 0.510.
  - So under the ceiling SD, the test §4.1 describes ("Stage 1 at n = 8 below 0.5 power … for the income layer") fails
    once invalid seeds are counted.
  - The coordinator should rule knowing this. Neither registered fallback option fixes it:
    - dropping points does not raise valid seeds per point;
    - n = 12 raises them only to about 6.

## 5. Effective n (the ruling's input)

**Founder draws.** For each seed, the holistic founders are the same 60 at all 150 census points (`census.txt`: 1
distinct founder set per seed over 150 points; the readout checked 3). Founding by draw at `c0-p030-U-L`
(`founders.txt`):

| draw (seed) | 129001 | 129002 | 129003 | 129004 | 129005 | 129006 | 129007 | 129008 |
|---|---|---|---|---|---|---|---|---|
| holistic alive at 59 | 60 | 0 (last 10) | 0 (last 14) | 60 | 60 | 58 | 0 (last 14) | 0 (last 14) |

- Sources: 129001–129003 are census runs; 129004 is the pilot S; 129005–129008 are the anchor-fallback S 0–59 runs
  (`ckpt/rbt-129-stage0-c0-p030-U-L-12900[5-8]-S`).
- Those four anchor runs were produced in the P-0 lanes, but **the readout does not read them**.
- Draws 129002 and 129003 die at all 150 points (by seasons 11–51, median 15–19).
- At both U-L pilot points, every draw alive at 59 was alive at 239 (4 of 4).
- At `c1-p030-PW-G`, draw 129004 dies by season 16.

**At the 36 Stage-1 points** (`stage1_points.txt`):
- 129001 has both faunas at 59 at 24 of the 36.
- At the other 12 it does not: all 9 PW-G points except `c0-p030-PW-G`, `c2-p080-U-G`, `c2-p080-HP-G`,
  `c1-p030-PW-L` and `c1-p080-PW-L`.

**What Stage 1 does with them.**
- The DESIGN §11.1 pre-data note, ruled at 02:22: Stage 1's S at 129001–129003 **resumes from the census state**. For
  129002 and 129003 that state has no holistic member.
- `ecology.py` never re-seeds a population. The only extinction handling is the "everyone died" stop and the merge
  null's "B is empty".
- Seeds 129007 and 129008 run fresh, but their founders are the draw that died by season 14 at `c0-p030-U-L`.
- `launch/stages.py` has no Stage-1 launcher yet.

**Registered handling: yes, fixed by §6.1.**
- A seed is valid for income only if both faunas are alive in S through season 239, and for the share test only if
  both are alive at the merge. Invalid seeds are "counted and reported, never averaged".
- Call order:
  - EXCLUDED if a fauna is extinct by 299 on ≥ 5 of 8 seeds (≥ 10 of 16);
  - else PARTIAL if fewer than 6 of 8 (12 of 16) are valid for the share test, which is "never a WIN".
- Applied mechanically at n = 8:
  - the 24 points where 129001 founds have at most 4 valid seeds (1, 4, 5, 6), so they are **PARTIAL-D** at best, and
    **EXCLUDED** if any of 1, 4, 5, 6 dies by 299;
  - the other 12 have at most 3 valid seeds. Nine of them lose the holistic fauna on 129001 as well, so it is extinct
    on ≥ 5 of 8 seeds and they are **EXCLUDED**. The other three are `c2-p080-U-G`, `c2-p080-HP-G` and
    `c1-p030-PW-L`, which lose the designed fauna on 129001; they are at least **PARTIAL**.
- At n = 16, PARTIAL is avoided only if all 8 new draws found. At q = 0.5 that probability is 0.004.
- Anything else is a **post-hoc amendment** made after the census was seen:
  - replacing or skipping 129002, 129003, 129007 or 129008;
  - re-drawing founders;
  - seeding from survivors;
  - redefining validity.

  §5.2 fixes the seeds (j = 1…16, common across points), and §4.2 forbids adding seeds except by a new registration.
  Such an amendment is possible before Stage 1, but it has to be labelled as informed by the census data.

## Input for ruling n

Assumptions for the table:
- "Benign point" means a point where every draw that founds survives to 239. This is an upper bound. The 12 PW /
  c2-p080 points are worse: at most 3 valid seeds at n = 8, EXCLUDED at 9 of them and at least PARTIAL at the other
  3.
- Draws 129001–129008 are known: 4 of 8 found. New draws (129009+) found with probability q; 4 of 8 at
  `c0-p030-U-L` gives q ≈ 0.5, with a 95% CI of about 0.16–0.84.
- Power is the income t test at |H − D| = 0.4, BH half, averaged over the distribution of valid seeds.
- Cost: S arms only = 36 points × n × 300 seasons × 23.3 / 43.7 core-s. The census resume credits −42 / −79. Seeds with
  the holistic fauna extinct run one fauna and are cheaper. The "power.py Stage 1" column adds M, half N, probes and
  plants, ungated.

| n per point | E[valid seeds], benign point | power @ SD 0.334 | power @ SD 0.275 | P(holistic EXCLUDED), benign | share call possible? | Stage-1 core-h, S arms only (23.3–43.7) | power.py Stage 1, ungated |
|---|---|---|---|---|---|---|---|
| 8 (nominal: 8 valid) | **4** (known: 1, 4, 5, 6) | **0.381** (nominal 0.826) | **0.510** (nominal 0.939) | 0 if all four survive; any 1 loss → EXCLUDED | no: ≤ 4 < 6 → PARTIAL | 559–1,049 | 1,358–2,512 |
| 12 | 6.0 (q 0.5); 5.0–7.0 (q 0.25–0.75) | 0.641 (0.520–0.743) | 0.788 (0.667–0.878) | 0.06 (0.00–0.32)¹ | no: ≤ 8 < 9¹ → PARTIAL | 839–1,573 | 2,023–3,754 |
| 16 | 8.0 (q 0.5); 6.0–10.0 | 0.807 (0.635–0.910) | 0.918 (0.779–0.976) | 0.14 (0.00–0.68) | only if all 8 new draws found (q⁸ = 0.004 at 0.5) | 1,118–2,098 | 2,687–4,996 |

¹ No threshold is registered for n = 12. §6.1 gives only 5 of 8 / 10 of 16 (EXCLUDED) and 6 of 8 / 12 of 16
(PARTIAL). I used the proportional ≥ 8 of 12 and 9 of 12. **Ruling n = 12 also means ruling these thresholds.**

Further points for the ruling:
- **n = 16 at Stage 1 collides with R-B.** R-B's extension is seeds 9–16, and its inverse-normal Z combines halves 1–8
  and 9–16. Stage-1 n = 16 would need R-B re-registered (seeds 17–32) and the 2b budget re-costed.
- **Checking the claimed 3,013–5,545 core-h at n = 8:** it is correct as `power.py` part 4's ungated programme total
  (P + 0 + 1 + 2a + 2b). It is not the Stage-1 cost. Stage 1 alone, on the same formula, is 1,358–2,512. §11.2's gated
  table was not re-run at the pilot cost.
- **The design problem is founding, not power.** Under the registered rules, n decides only how many seeds the income
  layer gets. At every n in {8, 12}, the body (share) call at every Stage-1 point is PARTIAL-D or EXCLUDED-H, set by
  which founder draws the seed numbers happen to fix. Whether to amend founding before Stage 1 is the coordinator's
  call, and it would be data-informed. Options include:
  - re-drawing holistic founders per seed until they found;
  - a founding runway before the census state;
  - dropping draws that fail at the anchor.

## 6. Census

`census.py`, own code, 450 runs:

- **Holistic FOUNDING-FAIL: 150 / 150.** Holistic extinct by 59 at seed 129001 at 38 points, and at 129002 and 129003
  at 150 each.
- **Designed FOUNDING-FAIL: 34 / 150** (26 PW, 5 U, 3 HP). My list is identical to the readout's.
- **g0:** ≤ 0.8 at **46**, ≤ 1.0 at **63**, n/a at **11**. The 11 n/a points are listed in `census.txt` and match.
- **C1: 13 rows** (9 price, 4 clutter), the same rows as the readout's.
  - At 36 points the census income difference is undefined (no holistic member-seasons in 30–59 on any seed). These
    points are skipped in the sign count, so some "adjacent" pairs are not adjacent on the grid.
  - At almost every defined point the difference rests on seed 129001 alone.

## MUST (author)

1. **Put the known founder outcomes in §5 of the readout.**
   - Read the four anchor-fallback runs (129005–129008 at `c0-p030-U-L`, P-0 lanes), and state that 4 of draws
     129001–129008 found (1, 4, 5, 6) and 4 fail by season 14 (2, 3, 7, 8).
   - Replace "if half the seeds are lost, the effective n is about 4" with the fact: at n = 8, at most 4 valid seeds at
     every Stage-1 point, and at most 3 at the 12 points listed in `stage1_points.txt`.
   - Print the §4.1 power at n_valid = 4: 0.381 at SD 0.334, 0.510 at SD 0.275.
2. **State §6.1's mechanical consequence.**
   - With at most 4 of 8 seeds valid at the merge, every Stage-1 point is PARTIAL-D (item 2) or EXCLUDED (item 1) at
     n = 8. The same holds at n = 12 under any proportional threshold, and at n = 16 unless all 8 new draws found.
   - Say that this is the registered handling (invalid seeds counted, never averaged), and that any change to seeds or
     founding would be a data-informed amendment.
   - The readout currently says it "makes no call on it". It need not call it, but it must state what the registered
     rules do.
3. **Label the post-plan rules as such, with both values.**
   - The null-SD exclusion: 0.229 / df 3 / r 1.53 with it, 0.358 / df 10 / r 2.39 over all 11 N runs, and why the
     excluded runs are not drift nulls.
   - Keeping the registered SD bounds and deciding §5 at the ceiling when no pooled SD exists, which the plan did not
     provide for.
   - The (d) exclusions added in `29f35a8`.

## SHOULD (author)

1. Say that 3,013–5,545 is `power.py` part 4's **ungated** programme total. Either re-cost §11.2's gated table at 23.3
   / 43.7, or say it was not re-costed.
2. **Cost (d):**
   - Note that the median 23.3 mixes single-fauna arms (13.6, 10.1, 2.7 core-s) with two-fauna arms (24–58).
   - Note that 23 of 38 arms were excluded.
   - Note that the 43.7 ceiling is `c1-p030-U-L` on shared hosts.
3. **C1:** say that 36 points are undefined and skipped, so a counted "sign change" can span a gap. Say that the 13
   rows mostly rest on seed 129001 alone.
4. **K1:** state that K1 was never tested on a PW terrain. Record whether a K1 re-run on 129002 at `c1-p030-PW-G` is
   wanted before Stage 1.
5. **Founder identity:** say it holds at all 150 points × 3 seeds (1 founder set per seed), not only the 3 checked.
