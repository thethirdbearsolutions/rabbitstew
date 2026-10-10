# RBT-134b design (draft pre-registration, DESIGN ONLY): the positive control and the background clause, redesigned

**Status.** This is a draft for review. Nothing here has been launched. No RBT-134 condition has been run, and no
lineage has been mutated at `MASTER_SEED 20260912` or at either held-out seed.

The held-out validation (§5) runs only after review and an owner GO. The registered run (§7) runs only after the
validation, a registration amendment, its own review and the owner's GO.

**Mandate.** The owner decided this first-hand on 2026-10-10: "Follow your recommendations", recorded in
OWNER-DECISIONS-2026-10-10 item 6. RBT-134b's positive control and background clause are designed by a fresh session
that is blind to the RBT-134 control numbers. This document changes only:
1. the construction of C+ (§3);
2. the background measure, together with the clause's guards (§4).

It also specifies:
- a held-out validation of both (§5);
- the sham control I5 in a form that holds whichever I5 category the RBT-134 diagnosis returns (§6).

Everything else is carried over from `DESIGN.md` r3 (with amendments C1 and I5-a), unchanged (§7).

**Blindness.** The designer read only:
- `DESIGN.md`, `GATE-FAILURE.md` and `LAUNCH.md`;
- the merged code (`assay.py`, the `rabbitstew` package, `runs/RBT-91/structural_rate.py`, `runs/RBT-78/reconcile.py`);
- the committed parent pools.

The designer did not open `OPTIONS.md`, the branch `claude/rbt134-diagnosis`, `claude/rbt134-runs-A` or `-B`, any file
under `runs/RBT-134/out/`, or any RBT-129 output. The only RBT-134 outcome known here is the category token **C+-BG**:
C+ rejected (k ≥ 6), and the background clause failed. The only data figures used are public ones that DESIGN.md
already cites:
- B0's 84 arrivals;
- B0's registered background prefix, 22 of 9,990 unflagged;
- RBT-91's rows.

**What was run to design this.** Both scripts read only the committed parents and the code. Neither mutates a lineage.

| script → output | what it does |
|---|---|
| `design-134b/parent_checks.py` → `parent_checks.txt` | Per committed parent (67): plant visibility V, the two swap preconditions S1 and S2, brain sizes, drive-Effector biases, and the depth-0 yield of a C+ plant (a design seed, `SeedSequence([134, 2, parent])`) |
| `design-134b/cplus_price.py` → `cplus_price.txt` | Stdlib arithmetic on those numbers and the operator's rates: C+'s yield and remnant share per plant, and its k and remnant load at each candidate rate |

Timings are measured on a throwaway seed (1) and are not committed: 19 `mutate_controller` steps take about 8.5 ms
per lineage, and a synthesis plus predicate at every depth adds about 14.5 ms.

---

## 0. Summary

1. **Why C+ failed the clause, from mechanism alone (§1).**
   - The pair event plants its unit partway down the lineage. The default operator then erodes the plant.
   - A drive wheel's local brain holds only 1–8 links, so `remove_link` pops a planted out-leg at about 1–5% per
     step. A reset to N(0, 1) can flip a leg's sign.
   - About 31% of plants end as **remnants**: a ×16 half-circuit that no longer satisfies the predicate. r3's measure
     counts a remnant as a "structureless" lineage, and its whole-brain gain is huge.
   - At r3's rate of 0.005 per mutation, about 9% of lineages are planted. The remnants alone then come to about
     **13× B0's background rate** (`cplus_price.txt`), so the clause has to fail. That is the C+-BG category,
     predicted without reading any control output.
2. **New background measure (§4).**
   - The background is read on **never-structured** lineages: the predicate held at no depth from 0 to 19.
   - The rung (6.8664), the `sign`-flag rule, the 40,000 lineages and the clause (one-sided 95% Katz upper bound on
     candidate/B0 ≤ 2) are unchanged.
   - A remnant is excluded by definition, because its plant was structure at the depth it was made. This holds on all
     67 parents (check V).
   - Two new guards:
     - **I9:** on a pair condition, every never-structured background lineage equals B0's lineage for the same index,
       exactly.
     - **C−:** a known whole-brain pump (RBT-91's coupled `weight_sigma 4.0`) must still **fail** the new clause
       clearly, on the held-out seeds.
3. **New C+ (§3).**
   - The plant is r3's, unchanged: a `tanh` unit, ×16 links, bias 0, wired by the operator mid-lineage.
   - Only the rate changes, to a ladder 5×10⁻⁵ → 2×10⁻⁴ → 10⁻³ per mutation, chosen at the held-out seeds.
   - The first rung is priced at E[k] ≈ 43–85 per 200,000. That is the family's scale (P2 and P3 are bounded at
     ≤ 29), not thousands, and its remnants would be only about 0.13× B0's rate even under r3's measure.
4. **I5 becomes I5-S, a swap identity (§6).**
   - Regenerate a sensor-blind condition from parents with `food` and `agent` relabelled into each other.
   - Its food set must equal the original sham set, and its sham set the original food set, lineage by lineage.
   - This is exact under any food/agent asymmetry of the parents, so it is the same test for every category the
     diagnosis can return. Its preconditions hold on all 67 parents (S1, S2).
   - The food/agent symmetry test becomes descriptive.
5. **Carried over unchanged:** the family (P2, P3), Holm m = 2 (k ≥ 6, then k ≥ 5), the checks A0, P1, P4 and P5 with
   their bounds, n = 200,000 per condition, the rungs, the decision rule, `MASTER_SEED 20260912` for the registered
   run, the streams, I1–I3 and I6–I8, and the holistic stage (§7).
6. **Costs.** Validation is about 12 CPU-h, plus at most about 6 if the ladder climbs. The registered run is about 17,
   plus at most about 5 for re-signing (§8).

---

## 1. What failed, by mechanism (no control output read)

### 1.1 The plant and what the default operator does to it

The event (`genetics._pair_event`, `assay.CONDITIONS["C+"]`) does the following:
- It appends a global `tanh` unit k with bias 0.
- It adds in-links from the left and right wheel `food` noses, of opposite sign.
- It adds out-links to both drive Effectors, of the same sign.
- Each link's magnitude is |N(0, 1)| × 16.
- All its draws come from `aux_rng`.

The default operator keeps acting on every later step (`mutate_controller`, add 0.15, rem 0.1). Per later step, the
hazards to a plant are:

| hazard | rate per later step | effect |
|---|---|---|
| `remove_unit` picks k | 0.06 / (n_global + 1) | clean: unit and links gone |
| `remove_link` pops an in-leg (global brain, 46–110 links) | 0.1 × 2 / (L_g + 2) | **remnant** |
| `remove_link` pops an out-leg (wheel brains, **1–8 links**) | 0.1 × (1/(L_L+1) + 1/(L_R+1)) | **remnant** |
| a leg reset to N(0, 1) (`weight_rate` 0.25 × `weight_reset_rate` 0.02, 4 legs) | 0.02 | **remnant** half the time (sign); otherwise too small for the rung |
| k re-typed to `sign` / `differentiate` / `abs` (deaf at b_k ≈ 0 under ±drive, `brain.py:84-92`) | 0.05 × 3/7 | the structure stays, but reads about 0 |

Source: `parent_checks.txt` (per-parent link counts) and `cplus_price.py`.

**A remnant** is a lineage whose plant lost one leg, or whose leg's sign flipped:
- it fails the predicate, so r3 counts it as **structureless**;
- it still carries one or both ×16 nose → k → Effector paths, so its whole-brain |a| is far above 6.8664.

Averaged over the parents and the plant depth, **31%** of plants become remnants. A depth-0 plant reads ≥ 12.5236 in
**94%** of draws (mean Y0; 0.865–0.985 by parent), and **45%** of plants reach depth 19 intact and paying, before bias
walks (`cplus_price.txt`).

### 1.2 Why that fails r3's clause at r3's rate

- At 0.005 per mutation, 1 − 0.995¹⁹ ≈ 9.1% of lineages are planted, about 18,000 per 200,000.
- In the 40,000-lineage background, that is about **1,135 remnants**, each very likely a hit at 6.8664.
- B0's registered rate is about 88 hits per 40,000 (22 of 9,990).
- So the remnants alone are about **12.9×** B0's rate (`cplus_price.txt`, last row), against a margin of 2.
- C+ rejecting with that much supply is also expected: E[k] runs into the thousands.

This is C+-BG, derived from code and parents, and it is a finding against N6 as GATE-FAILURE §3.3 said. The defect is
in **how the measure classifies remnants**. It is not in the plant:
- r3's background asks whether whole-brain gain rises in lineages that **do not carry the circuit**;
- a remnant is the eroded circuit, not the absence of one;
- any real operator that proposes circuits mid-lineage makes remnants too, in proportion to its proposal rate.

### 1.3 What the parents settle in advance (`parent_checks.txt`, 67 of 67 on each)

- **V (plant visibility).** A plant on the parent, under all four sign combinations, is a predicate unit of the
  synthesised phenotype. `_wheel_pairs` and the predicate read the same noses and Effectors. `mutate_controller` never
  changes the body or its sensors, so this holds at every depth. **A plant is structure at the depth it is made.**
- **S1.** Each drive wheel carries both a `food` and an `agent` sensor, on the same parts.
- **S2.** Synthesising the food↔agent relabelled parent gives the original phenotype with only the two sources
  swapped: the same unit order, links, functions and biases.

---

## 2. What changes, and what does not

| item | r3 (`DESIGN.md`) | 134b |
|---|---|---|
| C+ plant | pair event, ×16, bias 0, `tanh` | **unchanged** |
| C+ rate | 0.005 per mutation | **ladder 5×10⁻⁵, 2×10⁻⁴, 10⁻³**, chosen on held-out seeds (§3, §5) |
| background measure | unflagged lineages **structureless at depth 19**, whole-brain \|a\| ≥ 6.8664, first 20,000 per pool | unflagged lineages **never structured at any depth 0–19**; the same rung and lineages (§4.1) |
| background clause | one-sided 95% Katz upper bound on the ratio ≤ 2 | **unchanged** |
| background guards | none (N6 conceded C+ did not test it) | **I9** (remnant-proof identity) and **C−** (must fail; validation) (§4.3, §4.4) |
| I5 | sham count within the 99% binomial range of a food count (I5-a for C+ and P5) | **I5-S**, the swap identity, on every sensor-blind condition; the symmetry test is descriptive (§6) |
| everything else | §§2–13 | **unchanged** (§7) |

---

## 3. The new C+

### 3.1 Construction

- C+ is r3's event with fields `pair_event_scale 16`, `pair_event_zero_bias True` and `pair_event_rate r`. All its draws
  come from `aux_rng`, so its main stream is B0's, draw for draw.
- The registered r is the first rung of `CPLUS_LADDER = (5e-5, 2e-4, 1e-3)` accepted on **both** held-out seeds (§5).
  `assay.CONDITIONS_134B["C+L1".."C+L3"]` are those rungs.
- The rung is entered into `assay.CPLUS_REGISTERED` by the registration amendment, after validation. Until then,
  `run134b` refuses every `MASTER_SEED` run.

### 3.2 Why these rates (from `cplus_price.txt`; no control figure)

| rate | planted per 200,000 | E[k a32], w = 1 | E[k], w = 0.5 | P(k ≥ 6) at w = 0.5 | remnants in 40,000 (upper) | as a share of B0's rate |
|---|---|---|---|---|---|---|
| **5×10⁻⁵ (L1)** | 190 | 85 | 43 | ≈ 1 | 12 | 0.13× |
| 2×10⁻⁴ (L2) | 759 | 341 | 170 | ≈ 1 | 47 | 0.54× |
| 10⁻³ (L3) | 3,766 | 1,692 | 846 | ≈ 1 | 235 | 2.7× |
| 5×10⁻³ (r3) | 18,169 | 8,161 | 4,080 | ≈ 1 | 1,135 | 12.9× |

w ∈ [0.5, 1] covers what the pricing leaves out: the walks of b_k and b_E after the plant.

- **L1 is at the family's scale.** P2 and P3 are bounded at ≤ 29, and the first Holm step needs k ≥ 6. A positive
  control should show the pipeline returning PASS at the effect size it is meant to detect, not at 100× it.
- **Margin for k.** E[k] ≥ 43 even at w = 0.5. The acceptance rule (k ≥ 20 on each held-out seed, §5.2) leaves
  P(k < 6 at the registered seed) at about 1% or less, even if the true mean is as low as about 13.
- **Belt and braces.** L1's remnants are about 0.13× B0's rate. So L1 would very likely hold even under r3's measure,
  and C+'s PASS does not rest on the new measure alone. I9 tests the measure separately (§4.3). The r3-measure reading
  is printed beside every verdict, descriptively.
- **Why a ladder, and why it climbs.**
  - The only way L1 can miss is a yield far below the price: a deeper bias walk, or a pipeline fault, which I9 and I3
    catch.
  - Climbing raises k. It also raises remnants, which the new measure excludes and r3's would not.
  - L3 is the last rung. Past it, an unaccepted C+ means the pricing is wrong by more than 20×, and that is an
    ESCALATE.

### 3.3 Considered and not chosen

- **A terminal plant** (plant after step 19 only). It cannot leave remnants, so C+ would pass r3's measure trivially.
  But it would exercise neither erosion nor the remnant handling the family needs. Mid-lineage, C+ is a proxy for a
  real circuit-proposing operator, and I9 then tests that the new measure removes exactly its remnants.
- **A bigger scale or a pinned b_E.** The rung failure is not what failed (k ≥ 6 was met). Changing the plant would
  change two things at once.

---

## 4. The background, redesigned

### 4.1 The measure (registered)

The background is the share of the first 20,000 lineages per pool (40,000) that:
- (i) carry no `sign`-flip flag on the whole-brain probe (r3's rule, unchanged);
- (ii) are **never structured**: the food predicate (`assay.predicate`, which equals `structural_rate.motif_units`)
  holds at no depth from 0 (the parent) to 19;
- (iii) have whole-brain |a| ≥ 6.8664.

`assay.lineage_134b(track=True)` synthesises after every step and records ever-structured. It costs about 14.5 ms per
background lineage, and it changes no stream: synthesis draws nothing.

### 4.2 The clause (unchanged)

The clause **HOLDS** iff the one-sided 95% Katz upper bound on candidate/B0 is ≤ 2, on the two §4.1 counts. It is the
same rule for every condition, as in DESIGN.md §4. The verdict table (PASS, MOVES-WITH-BACKGROUND, NULL) is unchanged.

### 4.3 I9: the measure is remnant-proof, checked lineage by lineage (every pair condition: C+, P5)

`assay.chunk_134b` records, for every lineage, whether a pair event **planted** in it. For a planted lineage outside
the background block, it re-runs the lineage tracked, deterministically. I9 holds iff all of the following hold:

- **(a)** Every planted lineage is ever-structured. This follows from V; the check guards the code.
- **(b)** Every never-structured background row of the condition is unplanted, and **equals B0's row for the same
  lineage**: the same structured flag, the same |a| (exact float), the same `sign` flag and the same ever-structured
  flag.
- **(c)** The condition's food set and sham set, restricted to unplanted lineages, equal B0's sets restricted the same
  way.

**Why it must hold.**
- An unplanted pair-condition lineage drew its event coins from `aux_rng` only. A refused or no-pair event changes
  nothing.
- So its main stream and genotype are B0's, and so is its phenotype (`test_a_plant_is_structure_and_an_unplanted_lineage_is_b0s`).
- Under the new measure, a pair condition's background is therefore B0's background minus its planted lineages, value
  for value.

A failure of I9 means a remnant, or another planted effect, leaked into the background. **It VOIDs.** This is what N6
said C+ could not show, now shown directly.

### 4.4 C−: the new clause can still fail (held-out validation only)

**The risk.** A measure that excludes lineages might lose its power against a real pump.

**The condition.** C− is RBT-91's coupled `weight_sigma 4.0`:
- its links are P2's;
- on r3's measure it read 151 of 9,967 unflagged against B0's 22 of 9,990, about 6.9× (DESIGN.md §6.4).

**The requirement.** On each held-out seed, C−'s one-sided 95% Katz **lower** bound on the never-structured ratio must
be **> 2**. "Fails the clause" is required clearly, not just "upper bound > 2".

**The arithmetic.** The new measure drops only ever-structured lineages. Under the default operator these are about as
rare as arrivals (84 per 200,000 at depth 19). Even at several times that, they are a negligible share of 40,000. So a
pump with r3's 6.9× is expected to stay far above 2.

C− does not run at `MASTER_SEED`: its lineages share P2's links, and DESIGN.md §11 risk 7 forbids computing P2 before
the readout.

### 4.5 The coordinator's example: silencing every global unit with a food in-link

This was considered as the registered measure, and not adopted:

- **It blinds the clause to the commonest pump route.** A one-nose half-circuit (food → global unit → Effectors) is how
  a wide link step raises whole-brain gain without differencing. That is exactly what the clause exists to catch.
  Silencing every food-fed global unit leaves only direct local nose → Effector links, so P2 and P3 could pump through
  global units unseen.
- **It moves the operating point.** If silencing means deleting the unit's out-links, it also removes its resting drive
  into the Effectors (RBT-104's resting-drive mechanism, DESIGN.md §1), and so raises every other path's slope. Clamping
  the output instead needs a new probe convention.
- **It is not specific to remnants.** It removes every food-fed unit in every condition, not only the units descended
  from a circuit.

The never-structured measure removes only lineages that carried the circuit, keeps r3's probe exactly, and is checked
lineage by lineage (I9).

### 4.6 What the new measure gives up, stated plainly

- **An operator's own remnants are not counted against it.** For P2 and P3, a lineage that held a circuit at some depth
  and lost it does not enter their background, whatever its gain. That is the intended meaning ("whole-brain gain in
  lineages that never carried the circuit"), but it can only lower a condition's background.
- **Two mitigations, both descriptive:**
  - every family and C+ verdict line also prints the ratio upper bound on **r3's measure**, marked descriptive
    (`readout134b`);
  - the readout table prints each condition's remnant count (ever-structured, not structured at 19).
- A PASS whose r3-measure bound exceeds 2 is reported as a PASS **with that flag**. The decision rule itself is not
  changed by it.
- **The background is a selected subset** (DESIGN.md §11 risk 5): more so for conditions with many transient
  structures. The excluded count is printed per condition.

### 4.7 Power

- For B0 the denominator changes by the ever-structured share alone, so P(HOLDS) is DESIGN.md §7's to first order: 0.998
  unchanged, 0.95 at 1.25×, 0.67 at 1.5× and 0.05 at 2×.
- The validation prints B0's never-structured count on each held-out seed.
- **No power figure is re-derived from it.** If the held-out B0 counts differ from r3's by more than sampling, that is
  reported and the owner rules. The margin is not re-tuned.

---

## 5. Held-out validation (runs only after review and an owner GO)

### 5.1 What runs

- **Seeds.** `MASTER_SEED 20261101` and `20261102` (`assay.HELDOUT_SEEDS`). Neither is 20260912 nor GATE-FAILURE §3.4's
  20261011.
- **Protocol.** The same pools, 100,000 lineages per pool, 20,000 background lineages per pool, and the registered
  pipeline. Only the seed changes.
- **Guard.** `run134b` refuses any other seed, and any condition but B0, C+L1–L3 and C−, at a held-out seed.

**Commands**, in order, per seed S (every run needs `--go`, which records the owner's GO):

```
python runs/RBT-134/assay.py run134b B0   --seed S --go
python runs/RBT-134/assay.py run134b B0   --seed S --go --swap      # I5-S on B0
python runs/RBT-134/assay.py run134b C-   --seed S --go
python runs/RBT-134/assay.py run134b C-   --seed S --go --swap      # I5-S on C-
python runs/RBT-134/assay.py run134b C+L1 --seed S --go
python runs/RBT-134/assay.py validate134b                             # reads both seeds; runs nothing
```

- C+L2 runs on both seeds only if `validate134b` says `WAITING: run C+L2`. C+L3 follows the same rule.
- Outputs go to `runs/RBT-134/out/134b-S/`, on a branch of their own, as in LAUNCH.md.

### 5.2 Acceptance (fixed now)

A C+ rung is **ACCEPTED at a seed** iff, against that seed's B0:
- it PASSes the registered rule: McNemar one-sided p ≤ 0.025, k a32 ≥ 6, and the §4.2 clause HOLDS on the §4.1 measure;
- **k a32 ≥ 20**;
- I9 holds.

### 5.3 Outcome table (fixed now; `assay.validation_summary`)

The first matching row wins.

| on **every** held-out seed | outcome |
|---|---|
| C− does not fail (lower bound ≤ 2), **or** I5-S B0 or I5-S C− fails, **or** any VOID item | **ESCALATE**: the background or the sham redesign is broken; nothing registers; the owner decides |
| rung L*j* ACCEPTED on both seeds, and no earlier rung was | **REGISTER C+ = L*j*** |
| rung L*j* not ACCEPTED on both, and L*j*+1 has not yet run on both | **WAITING**: run L*j*+1 on both seeds |
| no rung ACCEPTED on both seeds | **ESCALATE** |

**Reporting.**
- Each seed's readout (`readout134b --seed S`) is committed in full, together with the summary.
- The two seeds are **never pooled**, with each other or with the registered run. They are a tuning set.
- The relay is the same as LAUNCH.md's: only the summary's last line, YES/NO tokens and SHA256s.
- Held-out readouts carry no RBT-134 condition other than B0, so reading them in full does not unblind any family
  figure.

---

## 6. The sham control, robust to the diagnosis

### 6.1 The registered form: I5-S, a swap identity

For every **sensor-blind** condition (B0, A0, P1, P2, P3, P4; at the held-out seeds B0 and C−):
1. Regenerate all 200,000 lineages from the same seeds, from parents with every `food` and `agent` sensor relabelled
   into each other. Run the predicate only, with no probes (`run134b … --swap`).
2. **I5-S holds** iff the swapped run's **food** set equals the original run's **sham** set, and its **sham** set equals
   the original's **food** set, lineage by lineage.

**Why it is the right test whichever category comes back.**
- A sensor-blind operator never branches on `food` against `agent`. `mutate_controller` reads a sensor's source only
  for `oscillator`, and `food` only inside the pair event, which is off in these conditions. `_link_sources` lists
  units without reading their source.
- S1 and S2 hold on all 67 parents.
- So the identity is **exact** whatever the parents' food/agent asymmetry, and whatever the sampling noise.
- It fails only if the predicate's two source paths differ, or the operator or synthesis is not source-agnostic: that
  is, on a pipeline fault, reading (c).
- It tests more than r3's I5 did (lineage by lineage, not counts), and it cannot fail by chance.

**What it gives up.** I5 no longer tests that food and agent arrivals are equally frequent. That symmetry is a property
of the evolved parents, not of the instrument (GATE-FAILURE §1, reading a).
- U2's paired exact test of B0's food set against its sham set is printed **descriptively**, as a property of the
  parents.
- C+ and P5 are not sensor-blind (U1). Their sham sets are descriptive, and I9 (c) checks them against B0 on the
  unplanted lineages.

### 6.2 Decision table by the RBT-134 diagnosis's I5 token (fixed now)

**Token received (coordinator, 2026-10-10, category only, no numbers): I5-A.** So the row that applies is I5-A.

r2's form for I5-A (each condition's sham set tested against B0's sham set by a paired test) is not adopted for P1–P4.
Those operators change link magnitudes and signs on the main stream's own draws. Their sham sets therefore differ from
B0's lineage by lineage even under perfect sensor-blindness, and P2 is expected to move arrivals of both kinds. A paired
test against B0's sham set would then reject for reasons that have nothing to do with which sensor is food.

I5-S is the exact form of the same sensor-blindness question. It holds for any sensor-blind operator, whatever its
effect on arrival counts. On B0 at the master seed it is the diagnosis's EXACT swap.


The diagnosis relays exactly one of four tokens (GATE-FAILURE §4.3).

| I5 token | what it means for 134b | I5 in 134b | validation |
|---|---|---|---|
| **I5-B** | B0's food and sham sets are not distinguishable by the paired test; the swap may not have run | I5-S as §6.1; U2 descriptive | as §5 |
| **I5-A** | B0's sets differ, and the swap was EXACT: an asymmetry in the parents, with a source-agnostic pipeline | I5-S as §6.1 (the diagnosis's EXACT is the same identity on B0 at the master seed); U2 descriptive, reported as the parents' asymmetry | as §5 |
| **I5-C** | a pipeline fault | 134b waits for the fault's fix PR (GATE-FAILURE §3.2: regression test, adversary-checked). Validation runs on code that includes it, and I5-S B0 and I5-S C− must hold there. If the fix changes the **food** path, so that B0 no longer reproduces RBT-91's 84 at the master seed (I2), that is beyond 134b's scope → **ESCALATE** | after the fix merges |
| **ESCALATE** | two I5-C passes; a failed swap precondition is ruled out by S1 and S2 on the committed parents | nothing proceeds; the owner decides whether 134b goes on with I5-S | not run until the owner rules |

---

## 7. Carried over from DESIGN.md r3, unchanged

- **The family.** P2 (`link_sigma 4.0`) and P3 (P2 + `bias_reset_rate 0.2`), Holm at 0.05 with m = 2 (k ≥ 6, then
  k ≥ 5), the McNemar test against B0, and the verdicts PASS, MOVES-WITH-BACKGROUND and NULL. The background reading is
  §4.1's.
- **The checks.** A0 (bound 0), P1 (≤ 2), P4 (ceiling 2.96) and P5 (ceiling 0.01), with I3 as registered (C1 for P4).
- **The protocol.** n = 100,000 lineages per pool (200,000 per condition), 20,000 background lineages per pool, depth
  19, add 0.15 and rem 0.1, the pools, `MASTER_SEED 20260912`, and the main and aux streams.
- **The rungs and rules.** The rungs 6.2831, 12.5236 (primary) and 24.7145, and 6.8664 for the background. The `sign`
  rule (F2, option a). Re-signing, capped at 400.
- **The controls I1, I2, I3, I6 and I7.** B0 must reproduce RBT-91's 84 line for line. B0's **r3-measure** background
  prefix (26 of 9,996 and 22 of 9,990) is kept as a continuity control. B0's own k must be 0.
- **Lane B and the holistic stage** (E1, E2, H1, H2, E3). The predictions in DESIGN.md §10 for the family and the
  checks.

**Controls of the registered 134b run.** Any failure VOIDs the stage it guards.

| id | requirement |
|---|---|
| I1–I3, I6, I7 | as DESIGN.md §9 |
| I4 | the registered C+ rung PASSes (§5.2's rule without the k ≥ 20 tuning bar) |
| I5 | I5-S on B0, A0 and P1–P4 (§6.1) |
| I8 | as DESIGN.md §9 (holistic H2) |
| **I9** | on C+ and P5 (§4.3) |

**Why nothing else changes.** C+-BG is fully explained by the measure's treatment of remnants and by C+'s rate (§1).
Neither the family's power nor its rule entered that failure. Any further change would be tuning after a failure,
which §6.3 of DESIGN.md forbids.

**Code (this PR).** Changes are confined to `runs/RBT-134/assay.py` and the tests:
- The r3 path is unchanged: `run`, `chunk`, `readout` and `CONDITIONS`. Only `check_i2` and `check_i3` are factored out
  of `readout`, with the same output.
- The 134b path is new: `CONDITIONS_134B`, `lineage_134b`, `chunk_134b`, `run134b`, `bg_never`, `i9_leaks`, `i5s`,
  `katz_lower`, `readout134b` and `validate134b`.
- Tests are in `tests/test_rbt134b.py`.
- Nothing under `rabbitstew/`, `scripts/` or `runs/RBT-129/` is touched.
- The lane wiring for the registered run (a 134b lane A) is written at registration, with tests, after validation.

---

## 8. Costs (CPU-h)

| item | basis | CPU-h |
|---|---|---|
| a 134b assay condition | r3's ≈ 0.8 (DESIGN.md §12) + 40,000 tracked lineages × 14.5 ms ≈ 0.16 | ≈ 1.0 |
| a swap regeneration (I5-S) | 200,000 × ≈ 10 ms (mutation 8.5 ms + synthesis + two predicates; no probes) | ≈ 0.55 |
| **validation, per held-out seed** | B0, C−, C+L1 (3 × 1.0) + 2 swaps (1.1), × 1.5 margin | ≈ 6 |
| **validation, both seeds** | | **≈ 12** |
| each further ladder rung | 1.0 × 1.5 × 2 seeds | ≈ 3 (at most 2 rungs: ≤ 6) |
| **registered run** (after the amendment and a GO) | 8 conditions × 1.0 + 6 swaps × 0.55, × 1.5 | **≈ 17** |
| re-signing | as DESIGN.md §12 | ≤ 5 |
| lane B, if it is re-run at the new GO sha | as LAUNCH.md | ≈ 5.5 |
| design-time (this PR) | parent checks + pricing | < 0.01 |

Run the validation on a host with no RBT-129 Stage-2a lane and no RBT-116 gate lane, as LAUNCH.md requires.

---

## 9. Order of work and approvals

1. **This PR**, design and code. Then review: an adversary check, then the coordinator. The RBT-134 diagnosis's I5
   token selects §6.2's row. Nothing runs.
2. **The owner's GO for the validation** (§5). Validation runs, commits, and relays tokens.
3. **The registration amendment** sets `CPLUS_REGISTERED` and adds the 134b lane wiring with tests. It is reviewed,
   and the owner gives a GO for the registered run, which is first-hand: it spends the cost cap.
4. **The registered run** at `MASTER_SEED`, in DESIGN.md §13's order (controls, the gate, checks, P2 first, then P3),
   with this document's controls.

---

## 10. Predictions, both ways (fixed now; credences)

| id | prediction | credence | if wrong |
|---|---|---|---|
| V1 | `validate134b` ends **REGISTER C+ = C+L1** | 0.75 | yield below a quarter of the price (a bias walk or a fault I3/I9 shows), or a broken guard below |
| V2 | C− fails clearly (lower bound > 2) on both seeds | 0.9 | the pump in r3's background was largely remnants of transient structure; the never-structured measure then lacks power, and the outcome is ESCALATE |
| V3 | I9 holds for every C+ rung run | 0.97 | a leak path not in §1, such as a plant invisible to the predicate after a later change: a code fault |
| V4 | I5-S B0 and I5-S C− hold on both seeds | 0.95 | a source-dependent path in the predicate, synthesis or operator (reading c) |
| V5 | B0's never-structured background is within sampling of r3's 22 of 9,990 rate on both seeds | 0.85 | transient structures are hits more often than expected; reported, not tuned (§4.7) |

---

## 11. Risks

1. **The pricing ignores bias walks after the plant.** The factor w covers it, and the ladder and the k ≥ 20 bar
   absorb it.
2. **The new measure can only lower a condition's background** (§4.6). C− guards its power, and r3's reading is
   printed beside every verdict.
3. **The C− requirement is set at its comparison seeds, not at `MASTER_SEED`**, because of DESIGN.md §11 risk 7.
4. **I5-S tests the pipeline's source-agnosticism, not the parents' symmetry.** That is deliberate (§6.1), and
   the symmetry is reported.
5. **Held-out results are a tuning set.** The registered run is the only test, and nothing is pooled.
6. **CPU contention with RBT-129.** As LAUNCH.md.

---

## 12. Files

- `runs/RBT-134/DESIGN-134b.md`: this document.
- `runs/RBT-134/assay.py`: the 134b path (§7, "Code (this PR)").
- `runs/RBT-134/design-134b/parent_checks.py` and `.txt`: V, S1, S2, brain sizes, b_E and Y0 on the committed parents.
- `runs/RBT-134/design-134b/cplus_price.py` and `.txt`: the ladder's arithmetic.
- `tests/test_rbt134b.py`:
  - the guard and the constants;
  - plants are structure, and unplanted lineages are B0's (throwaway seed 1, an artificial rate);
  - the swap exchanges the two predicates;
  - V on every parent;
  - the readout, I9, I5-S, C− and the validation summary on synthetic records.
