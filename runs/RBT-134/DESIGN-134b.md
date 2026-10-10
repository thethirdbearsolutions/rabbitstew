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

**The owner's choice (2026-10-10, first-hand, OWNER-DECISIONS-2026-10-10 item 7).** RBT-134b is chosen; the cost cap
is **30 CPU-h with trims** (§8), covering validation, the registered run and any re-signing; "accept quoting",
which accepts #574's departure from GATE-FAILURE §4.3 (it bears on #574, not on this document). This revision
applies the reviews of head f39a262d (reviewer: B1, M1–M5, N1–N3; code adversary: MINOR 1–3, NIT a–d) and the
adversary's re-check of 98c7f5bb (round 2: MINOR A, MINOR B, NIT a, NIT b), and is drafted by a second, fresh session.

**Blindness: what each drafting session was given.** Two sessions drafted this document: the original drafter
(commits 15e028f and f39a262) and a second, fresh session that made the review fixes. Neither opened `OPTIONS.md`,
the branches `claude/rbt134-diagnosis`, `claude/rbt134-runs-A` or `-B`, any file under `runs/RBT-134/out/`, or any
RBT-129 output. The fixing session also opened neither PR #574's body nor its comments; the original drafter's one
read of #574 is (c). Both read `DESIGN.md`, `GATE-FAILURE.md`, `LAUNCH.md`, the merged code (`assay.py`, the
`rabbitstew` package, `runs/RBT-91/structural_rate.py`, `runs/RBT-78/reconcile.py`) and the committed parent pools.
Beyond that, exactly this reached them:

- **(a) The original drafter's brief (coordinator, 17:27:56Z)** carried:
  - the diagnosis category **C+-BG** and its meaning: C+ was detected (k ≥ 6), but the planted event raised
    whole-brain gain outside the motif beyond the background clause's bound;
  - that the I5 outcome was still pending;
  - one design suggestion, verbatim: "e.g. a remnant-proof background that silences any global unit with any food
    in-link". The coordinator took it from the OPTIONS note. That is why §4.5 calls it "the coordinator's example",
    and it is where the word "remnant" entered the design;
  - no figures.
- **(b) The drafter's exposure at 17:45:11Z.** A `git log` printed the base-history commit bodies of #574 and #575.
  They contain no numbers, but they name the kinds of figures #574 quotes and list the OPTIONS options. This document
  had already been written, by 17:43:42Z. The first design commit followed at 17:45:28Z.
- **(c) The drafter's read of PR #574's body at 18:24:26Z.** It saw C+'s k magnitude and the Katz upper bound. This
  came after both design commits (17:45:28Z and 17:48:37Z) and after the push at 17:55:13Z. Nothing in the drafter's
  commits depends on it. The wording it could bear on ("fully explained", "runs into the thousands") is revised here
  by the second session (§1.2, §7).
- **(d) The fixing session's brief (coordinator, 2026-10-10)** carried:
  - the owner's decision above;
  - C+-BG with the meaning in (a), and the I5 result as tokens only: **I5-A**, with I5-2 reproduction YES and the swap
    EXACT;
  - the two review comments on #576 (no outcome figures; the reviewer's B1 quotes OPTIONS' cost estimate for its
    option (b), about 20 CPU-h, a cost and not an outcome) and this exposure record;
  - no figures.

  A later coordinator message passed on the #577 adversary's note on trims (ii) and (iii) and released
  OWNER-DECISIONS-2026-10-10 item 7, which the fixing session then read. Item 7 carries no figures. It records the
  owner's chosen option verbatim (trims (i)–(iv); "Base cost is about 28–30"; stop and ask before a ladder climb past
  30) and the coordinator's readings: the cap covers all of 134b; the stop rule applies to any projected overrun; trim
  (iv)'s swap is the diagnosis's I5-3; lane B is read only after 134b registers.

The terminal plant (§3.3) and the negative control C− (§4.4) are the original drafter's own; neither was in (a).

The only data figures used are public ones that DESIGN.md already cites:
- B0's 84 arrivals;
- B0's registered background prefix, 22 of 9,990 unflagged;
- RBT-91's rows.

**What was run to design this.** The scripts read only the committed parents and the code. The first two mutate no
lineage; `timing.py` mutates the default operator's lineages at throwaway seed 1 (as the tests do), runs the re-sign heading
probe on six of them, and prints only CPU times.

| script → output | what it does |
|---|---|
| `design-134b/parent_checks.py` → `parent_checks.txt` | Per committed parent (67): plant visibility V, the two swap preconditions S1 and S2, brain sizes, drive-Effector biases, and the depth-0 yield of a C+ plant (a design seed, `SeedSequence([134, 2, parent])`) |
| `design-134b/cplus_price.py` → `cplus_price.txt` | Stdlib arithmetic on those numbers and the operator's rates: C+'s yield and remnant share per plant, and its k and remnant load at each candidate rate |
| `design-134b/timing.py` → `timing.txt` | CPU per lineage of each 134b step, and per re-sign heading probe, on throwaway seed 1 with the default operator; it prints CPU time only (the §8 costs) |

`timing.txt` (one core, the slower of the two hosts this session ran on): a lineage with its final predicates takes
about 10 ms, a tracked lineage about 30 ms, a background probe under 1 ms, a swap regeneration about 11 ms, and a
re-sign heading probe about 6.4 CPU-s per robot. The first host was about 30% faster.

---

## 0. Summary

1. **Why C+ failed the clause, from mechanism alone (§1).**
   - The pair event plants its unit partway down the lineage. The default operator then erodes the plant.
   - A drive wheel's local brain holds only 1–8 links, so `remove_link` pops a planted out-leg at about 1–5% per
     step. A reset to N(0, 1) can flip a leg's sign.
   - About 31% of plants end as **remnants**: a ×16 half-circuit that no longer satisfies the predicate. r3's measure
     counts a remnant as a "structureless" lineage, and its whole-brain gain is huge.
   - At r3's rate of 0.005 per mutation, about 9% of lineages are planted. On the pricing's upper-side assumptions
     (§3.2), the remnants alone come to about **13× B0's background rate** (`cplus_price.txt`), so the clause would
     fail. That is the C+-BG category, explained on the priced mechanism without reading any control output; I9 and
     the held-out readings (§4.3, §5) are what confirm it.
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
       clearly, on the held-out seeds. It runs on its background block only, and it is sealed: only its YES/NO
       token is read before the registered readout.
   - A pre-registered **EXCLUSION-FLAG** marks any verdict whose excluded remnants could by themselves have used up
     the clause's margin (§4.6).
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
   - It runs on B0 at the held-out seeds and on A0 and P1–P4 at `MASTER_SEED`. On B0 at `MASTER_SEED` the
     diagnosis's EXACT swap is cited, not re-run.
   - The food/agent symmetry test becomes descriptive.
5. **Carried over unchanged:** the family (P2, P3), Holm m = 2 (k ≥ 6, then k ≥ 5), the checks A0, P1, P4 and P5 with
   their bounds, n = 200,000 per condition, the rungs, the decision rule, `MASTER_SEED 20260912` for the registered
   run, the streams, I1–I3 and I6–I8, and the holistic stage (§7).
6. **Costs against the owner's 30 CPU-h cap (§8).** With trims (i)–(iv) and every line priced at ×1.5 over measured
   CPU, validation is about 7.7 CPU-h, plus 2.4 per ladder climb (at most 4.8). The registered run is about 14.1.
   Re-signing at its full cap is about 9.1. **Base 21.8 fits; base plus re-signing at its cap (30.9) and the worst
   case (35.7) exceed 30.** Nothing is trimmed without a ruling. A registered stop rule returns to the owner before any
   run, ladder climb or re-signing that would take 134b past 30. Lane B is not re-run.

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
- In the 40,000-lineage background, that is about **1,135 remnants**. The pricing **assumes** each is a hit at
  6.8664 (a remnant keeps one or both ×16 legs; this is an upper-side assumption, not a measurement).
- B0's registered rate is about 88 hits per 40,000 (22 of 9,990).
- So the remnants alone are about **12.9×** B0's rate (`cplus_price.txt`, last row), against a margin of 2.
- C+ rejecting with that much supply is also expected: at r3's rate `cplus_price.txt` prices E[k a32] at 4,080
  (w = 0.5) to 8,161 (w = 1), its last row.

This is C+-BG explained on the priced mechanism, derived from code and parents, and it is a finding against N6 as
GATE-FAILURE §3.3 said. The mechanism is priced, not observed: I9 (§4.3) and the held-out comparison of each C+ rung's
never-structured background with B0's (§5) are what will confirm it. On that account, the defect is in **how the
measure classifies remnants**. It is not in the plant:
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
| background guards | none (N6 conceded C+ did not test it) | **I9** (remnant-proof identity), **C−** (must fail; validation; sealed) and the descriptive **EXCLUSION-FLAG** (§4.3, §4.4, §4.6) |
| I5 | sham count within the 99% binomial range of a food count (I5-a for C+ and P5) | **I5-S**, the swap identity, on every sensor-blind condition (on B0 at `MASTER_SEED`, the diagnosis's EXACT, cited); the symmetry test is descriptive (§6) |
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

**The table's biases, stated beside it (`cplus_price.py`'s header).**
- **Planted counts are upper bounds.** The pricing ignores refusals (`max_units_per_brain`) and wheel sides without a
  pair.
- **Remnant columns are upper bounds.** Every remnant is assumed a hit at 6.8664. Hazards are held at the parent's
  link counts, though `add_link` at 0.15 grows the wheel brains and lowers the out-leg hazard later.
- **E[k] ignores the bias walks** of b_k and b_E after the plant; w covers that, and only that.

- **L1 is at the family's scale.** P2 and P3 are bounded at ≤ 29, and the first Holm step needs k ≥ 6. A positive
  control should show the pipeline returning PASS at the effect size it is meant to detect, not at 100× it.
- **Margin for k: ACCEPT_K = 20 is a design margin.** E[k] ≥ 43 even at w = 0.5, so k ≥ 20 on each held-out seed
  (§5.2) costs L1 little. Its purpose is the registered seed: if the rung's true mean were as low as 13, the Poisson
  tail P(k < 6) would be 0.0107 there. A mean that low is unlikely to clear 20 on two seeds, but that is not a
  guarantee. The bar is a margin chosen now, not a bound derived from passing twice.
- **Belt and braces.** L1's remnants are about 0.13× B0's rate. So L1 would very likely hold even under r3's measure,
  and C+'s PASS does not rest on the new measure alone. I9 tests the measure separately (§4.3). The r3-measure reading
  is printed beside every verdict, descriptively.
- **Why a ladder, and why it climbs.**
  - The only way L1 can miss is a yield far below the price: a deeper bias walk, or a pipeline fault, which I9 and I3
    catch.
  - Climbing raises k. It also raises remnants, which the new measure excludes and r3's would not.
  - L3 is the last rung. Past it, an unaccepted C+ means the yield is below about 1/85 of the price (L3's priced
    1,692 against the bar of 20) or a guard failed, and that is an ESCALATE.

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

`assay.lineage_134b(track=True)` synthesises after every step and records ever-structured. It adds about 13–15 ms per
background lineage (`timing.txt`), and it changes no stream: synthesis draws nothing.

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

**What C− runs (trims ii and iii, §8).** Only its background block: the first 20,000 lineages per pool (n = n_bg),
all tracked and probed. That is everything its requirement reads. It has no swap regeneration; I5-S on B0 already
tests the pipeline's source-agnosticism at each held-out seed, and C− is not a registered condition.

**C− is sealed (review M2, adversary NIT a and round-2 NIT a).** At the same seed, C− and P2 make the **same link
steps lineage by lineage**. `mutate_weights` draws each link step as z × 4.0 in both: `rng.normal(0, 4.0)` for C−'s
`weight_sigma`, and `rng.normal(0, 1) × 4.0` for P2's `link_sigma`, from the same main-stream draw. Only the **bias
steps** differ: C−'s are N(0, 4.0), P2's are N(0, 0.4). The predicate is structural, so C−'s food set at a held-out
seed **is** P2's food set there. Its k and background differ from P2's only through the biases, so they would partly
preview P2's. So:
- `chunk_134b` records **no** arrival, food set or sham set for C−: only its background rows;
- its held-out readout prints only the token `C− fails clearly: YES/NO`. Its table row reads "sealed", and its counts
  and bound are not printed;
- its JSON stays on the held-out output branch, unread, until the registered run's readout, where its counts may be
  printed beside P2's;
- only the token is relayed.

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

**EXCLUSION-FLAG (registered now; review M5).** Let, among a condition's unflagged background lineages, the
**remnant share** be the share that were structured at some depth 0–18 but not at 19: exactly the lineages r3's
measure counted and the new measure leaves out. Let x₀/n₀ be B0's never-structured hit rate at the same seed. A
condition is **flagged** iff

> its remnant share − B0's remnant share ≥ x₀/n₀.

The flag is printed in the readout table and beside every C+ and family verdict (`assay.exclusion_flag`). It is
descriptive and does not change a verdict.

**Why this threshold, and not "> 2× B0's ever-structured share".**
- It is in the clause's own units. The clause allows the candidate's background to reach twice B0's, an extra x₀/n₀.
  The flag fires when the excess remnants, were every one a hit, would on their own use up that whole margin. Below
  it, no assumption about the left-out lineages could have moved a point ratio of 1 past 2. At or above it, the exclusion
  could have carried the verdict, and the reader should weigh the r3-measure bound printed beside it.
- A ratio of shares would be noisy and unanchored. B0's remnant share is of the order of the arrival rate, a few
  tens of lineages in 40,000 at most, so "2×" would flag on sampling noise in some conditions and miss large
  absolute exclusions in others. It also says nothing about the clause.
- Of the C+ rungs, only L3 is expected to be flagged (priced remnants about 0.13×, 0.54× and 2.7× B0's hits for
  L1, L2 and L3; §3.2). I9 already shows its exclusions are exact, so a C+ flag says only that the rung makes many
  remnants.
- For P2 and P3 the flag marks exactly the case §11 risk 2 worries about: a background held only because the
  operator's own transient structures were left out.

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
python runs/RBT-134/assay.py run134b C-   --seed S --go --n 20000 --n-bg 20000   # background block only, sealed
python runs/RBT-134/assay.py run134b C+L1 --seed S --go
python runs/RBT-134/assay.py validate134b                             # reads both seeds; runs nothing
```

- C+L2 runs on both seeds only if `validate134b` says `WAITING: run C+L2`. C+L3 follows the same rule.
- Before saying `WAITING` for a climb, `validate134b` applies the cost stop rule (§8). If the climb would take 134b
  past 30 CPU-h, it says `STOP-COST` instead: nothing more runs, and the owner decides.
- Outputs go to `runs/RBT-134/out/134b-S/`, on a branch of their own, as in LAUNCH.md.

### 5.2 Acceptance (fixed now)

A C+ rung is **ACCEPTED at a seed** iff, against that seed's B0:
- it PASSes the registered rule: McNemar one-sided p ≤ 0.025, k a32 ≥ 6, and the §4.2 clause HOLDS on the §4.1 measure;
- **k a32 ≥ 20**;
- I9 holds.

### 5.3 Outcome table (fixed now; `assay.validation_summary`)

The first matching row wins.

| condition | outcome |
|---|---|
| on **either** held-out seed: C− does not fail (lower bound ≤ 2), **or** I5-S B0 fails, **or** any VOID item | **ESCALATE**: the background or the sham redesign is broken; nothing registers; the owner decides |
| rung L*j* ACCEPTED on both seeds, and no earlier rung was | **REGISTER C+ = L*j*** |
| rung L*j* not ACCEPTED on both, L*j*+1 has not yet run on both, and the climb passes the cost stop rule (§8) | **WAITING**: run L*j*+1 on both seeds |
| as the row above, but the climb fails the cost stop rule | **STOP-COST**: nothing more runs; the owner decides |
| no rung ACCEPTED on both seeds | **ESCALATE** |

**Reporting.**
- Each seed's readout (`readout134b --seed S`) is committed in full, together with the summary.
- The two seeds are **never pooled**, with each other or with the registered run. They are a tuning set.
- The relay is the same as LAUNCH.md's: only the summary's last line, YES/NO tokens and SHA256s.
- Held-out readouts print no family or check condition, and C− only as its token (§4.4), so reading them in full
  previews no family figure. C−'s JSON is sealed until the registered readout.

---

## 6. The sham control, robust to the diagnosis

### 6.1 The registered form: I5-S, a swap identity

For the **sensor-blind** conditions, as follows (`assay.check_swap_134b`):
- at the held-out seeds, **B0** (C− has no swap; trim iii, §8);
- at `MASTER_SEED`, **A0, P1, P2, P3 and P4**. **B0's** I5-S there is the RBT-134 diagnosis's swap token, **EXACT**,
  cited and not re-run (trim iv; the diagnosis relayed I5-A, I5-2 reproduction YES, swap EXACT). Its I5-3
  regenerated B0's 200,000 lineages at `MASTER_SEED` from swapped parents and tested this same identity. 134b's B0
  lineages are those lineages: `lineage_134b` keys r3's streams (`test_134b_lineages_are_r3_lineages`), and I2 B0
  checks the 84 line for line in the registered run.

For each:
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
effect on arrival counts. On B0 at the master seed it is the diagnosis's EXACT swap, which 134b cites (§6.1).

The diagnosis relays exactly one of four tokens (GATE-FAILURE §4.3).

| I5 token | what it means for 134b | I5 in 134b | validation |
|---|---|---|---|
| **I5-B** | B0's food and sham sets are not distinguishable by the paired test; the swap may not have run | I5-S as §6.1, with B0's swap re-run at `MASTER_SEED`, as there would be no EXACT to cite (moot: the token received is I5-A); U2 descriptive. I5-S's preconditions S1 and S2 are already verified on all 67 committed parents (`parent_checks.txt`) | as §5 |
| **I5-A** | B0's sets differ, and the swap was EXACT: an asymmetry in the parents, with a source-agnostic pipeline | I5-S as §6.1 (the diagnosis's EXACT is the same identity on B0 at the master seed); U2 descriptive, reported as the parents' asymmetry | as §5 |
| **I5-C** | a pipeline fault | 134b waits for the fault's fix PR (GATE-FAILURE §3.2: regression test, adversary-checked). Validation runs on code that includes it, and I5-S B0 must hold there; B0's swap is then also re-run at the master seed, since the faulty diagnosis gives nothing to cite. If the fix changes the **food** path, so that B0 no longer reproduces RBT-91's 84 at the master seed (I2), that is beyond 134b's scope → **ESCALATE** | after the fix merges |
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
- **Lane B and the holistic stage** (E1, E2, H1, H2, E3). The predictions in DESIGN.md §10 for the checks; the
  family's are restated for the new measure in §10.

**Lane B is not re-run (trim i).** Its committed E1, E2 and H1 outputs (`claude/rbt134-runs-B`, GO 0ad0afae) are used
as they are.
- **Why they still apply.** 134b changes only C+'s rate, the background measure and I5's form. E1, E2 and H1 read
  none of these. Their conditions' fields are r3's (`CONDITIONS_134B[c] == CONDITIONS[c]` for A0 and P1–P5, tested),
  and `e1_parity.py`, `e2_erasure.py` and `h1_census.py` are unchanged. E1's C+ row is r3's C+ (rate 0.005), not
  134b's; it is not a 134b item and is read as r3's.
- **When they are unsealed.** They stay sealed, beyond their RELAY tokens, until **after the owner's GO for the
  registered run**: the registration amendment (§9 step 3) has merged and the owner has given that GO. They are then
  unsealed and read **before the registered run's readout**. At that point nothing in them can steer any 134b choice
  or the decision to run, because both are fixed. And E1's stream identity (I2) is a control, so it is known before
  the family is read.
- If the registration amendment, or any later fix, changes one of those three scripts or `assay.CONDITIONS`, the lane
  B outputs no longer apply. The owner then decides; a re-run is not in the cost cap.

**Controls of the registered 134b run.** Any failure VOIDs the stage it guards.

| id | requirement |
|---|---|
| I1–I3, I6, I7 | as DESIGN.md §9 |
| I4 | the registered C+ rung PASSes (§5.2's rule without the k ≥ 20 tuning bar) |
| I5 | I5-S on A0 and P1–P4; on B0, the diagnosis's EXACT, cited (§6.1) |
| I8 | as DESIGN.md §9 (holistic H2) |
| **I9** | on C+ and P5 (§4.3) |

**Why nothing else changes.** C+-BG is explained, on the priced mechanism, by the measure's treatment of remnants and
by C+'s rate (§1). I9 and the held-out readings are what confirm that mechanism; it has not been observed. On that
account, neither the family's power nor its rule entered the failure. Any further change would be tuning after a failure,
which §6.3 of DESIGN.md forbids.

**Code (this PR).** Changes are confined to `runs/RBT-134/assay.py` and the tests:
- The r3 path is unchanged: `run`, `chunk`, `readout` and `CONDITIONS`. Only `check_i2` and `check_i3` are factored out
  of `readout`, with the same output.
- The 134b path is new: `CONDITIONS_134B`, `lineage_134b`, `chunk_134b`, `run134b`, `check_swap_134b`, `bg_never`,
  `i9_leaks`, `i5s`, `katz_lower`, `exclusion_flag`, the cost stop rule (`cost_gate_134b`, `spent_134b`,
  `resign_cost_h`), `readout134b` and `validate134b`.
- Tests are in `tests/test_rbt134b.py`.
- Nothing under `rabbitstew/`, `scripts/` or `runs/RBT-129/` is touched.
- The lane wiring for the registered run (a 134b lane A) is written at registration, with tests, after validation.
  It must call `cost_gate_134b` before re-signing (§8).
- **Two code facts the design rests on, now tested** (review N2):
  - `_pair_event` is the last operation of `mutate_controller` before validation (`genetics.py:514`), so a plant is in
    the genotype its step returns, and the tracked predicate sees it at that depth;
  - no committed parent satisfies the food or the agent predicate at depth 0 (0 of 67).

---

## 8. Costs (CPU-h), against the owner's cap of 30

**Basis.** `design-134b/timing.txt`, CPU time on one core, × a 1.5 margin on every line; the constants are
`assay.COST_H`, `RESIGN_S` and `RESIGN_RESERVE_H`. The committed timings are from the slower of the two hosts this
session ran on: the first host measured about 7.2 ms per lineage, the second 9.6–10.3 ms. Pricing from the slower one
is the conservative choice; on the faster one every compute line is about 30% lower.

| unit | basis (`timing.txt`) | ×1.5 |
|---|---|---|
| a full 134b condition | 160,000 lineages × 10.3 ms + 40,000 tracked and probed × 30.9 ms ≈ 0.80 CPU-h | **1.2 CPU-h** |
| C− (background block only, trim ii) | 40,000 tracked and probed × 30.9 ms ≈ 0.34 CPU-h | **0.55 CPU-h** |
| a swap regeneration (I5-S) | 200,000 × 10.6 ms ≈ 0.59 CPU-h | **0.9 CPU-h** |
| re-signing one robot | one reference heading probe (16 seeds × 15 s): 6.42 s mean, 6.62 s max on 6 B0 lineages here; the code adversary measured 6.8 s; **6.8 s** is used | **10.2 s** |

**The trims (owner: "30 CPU-h with trims").**
- **(i)** No lane B re-run (§7, where its unsealing point is fixed). Saves about 5.5.
- **(ii)** C− runs on its background block only, n = n_bg (§4.4).
- **(iii)** No C− swap (§4.4, §6.1).
- **(iv)** At `MASTER_SEED`, I5-S B0 cites the RBT-134 diagnosis's EXACT swap instead of re-running it (§6.1).

| item | basis | CPU-h |
|---|---|---|
| validation, per held-out seed | B0 1.2 + C+L1 1.2 + C− 0.55 + B0 swap 0.9 | 3.85 |
| **validation, both seeds** | | **7.7** |
| **registered run** (after the amendment and a GO) | 8 conditions (B0, C+, A0, P1–P5) × 1.2 + 5 swaps (A0, P1–P4) × 0.9 | **14.1** |
| **base** | | **21.8** |
| re-signing, at its cap | DESIGN.md §12's cap, 8 × 400 robots × 10.2 s | **9.1** |
| **base + re-signing at its cap** | | **30.9** |
| each further ladder rung | 1.2 × 2 seeds | 2.4 (at most 2 rungs: 4.8) |
| **base + worst case** (two climbs, re-signing at its cap) | | **35.7** |
| lane B | not re-run (trim i) | 0 |
| design-time (this PR) | parent checks, pricing, timing | < 0.05 |

**Stated plainly: on this pricing, the worst case exceeds the 30 CPU-h cap.** Base (21.8) fits. Base plus
re-signing at its full cap (30.9) does not, and neither does any ladder climb on top of that (33.3 with one, 35.7 with
two). Nothing is trimmed here to make it fit: that needs an owner ruling. What the design does instead:
- **The stop rule (below) guarantees the cap is not crossed.** It compares the CPU actually spent plus the margined
  estimates of what remains. So the outcome depends on what validation actually spends. Unmargined, validation
  costs about 5.1 CPU-h on the slower host and about 3.5 on the faster.
  - **Without a climb,** the registered run's first item passes if validation spent at most 6.8
    (30 − 1.2 − 12.9 − 9.1). It would pass on either host.
  - **A ladder climb** passes only if spent is at most 4.4 (30 − 2.4 − 14.1 − 9.1). It would stop on the slower host
    and pass on the faster. A second climb faces the same 4.4 limit after the first rung's spend (about 6.7 and
    4.6), so it stops on either host.
- **Unmargined**, the same items come to about 14.5 at base and 23.8 in the worst case.
- **Levers for the owner, none applied:**
  - The re-signing reserve is DESIGN.md §12's cap on all 8 conditions. A0 cannot re-sign anything: DESIGN.md §9's I3
    bounds its k at 0 at every own-link rung, a16 included (a proof, DESIGN.md §10). Without it the reserve is 7.9.
  - The reserve could be priced at the registered run's actual eligible count once it is known. The re-signing gate
    already uses the actual count; only the reserve held earlier uses the cap.
  - The margin could be ×1.25 on a measured run host.
  - The cap could be raised.

**The cost stop rule (registered).**
- **What is counted.** Every `run134b` chunk (2,000 lineages) records its worker CPU, and the run appends it to
  `out/134b-S/cpu-ledger.jsonl` as each chunk completes. The ledger is never relayed. **Spent** is the sum over every
  ledger at every seed (`spent_134b`).
- **A killed run** (round-2 NIT b) still counts every chunk it finished. Two things are not counted:
  - the chunks in flight when it was killed: at most one per worker, about a minute each;
  - process start-up.
  So spent is low by at most a few CPU-minutes per killed run. If runs are killed repeatedly, the runner adds the
  shortfall by hand, as a ledger line with `"cond": "untracked"`.
- **What is still to come** (round-2 MINOR B) is every registered item with no output yet at `MASTER_SEED`, at its
  planning cost (`registered_to_come`), plus the re-signing reserve (9.1). At a held-out seed, that is the whole
  registered run (14.1). At `MASTER_SEED`, it is the items not yet run. So the **whole** registered run is checked
  before its first item.
- **When the rule is checked:**
  - **before every `run134b`**: spent + the run's own estimate + still to come (excluding the run itself);
  - **after every chunk of every run** (review R2): spent + this run's measured CPU so far + its remaining chunks at
    their measured mean + still to come. If that passes 30, the run cancels its unstarted chunks, lets the chunks in
    flight finish (they enter the ledger), writes **no** output and exits `STOP-COST`. So a run that turns out
    costlier than priced stops early, and cannot carry spent past the cap mid-run. The chunks in flight, at most one
    per worker (about a minute each), are the only overshoot past the trigger, and the trigger fires while the
    still-to-come reserve (at least 9.1) is unspent;
  - **before a ladder climb** (`validate134b`): spent + the rung on both seeds + still to come;
  - **before re-signing** in the registered run (wired at registration): spent + the re-signing's own estimate (its
    eligible robots × 10.2 s).
- **If any of these would exceed 30 CPU-h, stop and return to the owner.** The output is `STOP-COST`, with spent and
  the projection, and nothing further runs until the owner rules. As the coordinator reads OWNER-DECISIONS-2026-10-10
  item 7, this applies to any projected overrun, which is stricter than the owner's wording (a ladder climb). The rule
  never alters a verdict or a registered value. If re-signing is stopped, the registered verdicts stand; re-signing is
  a secondary.

Run the validation on a host with no RBT-129 Stage-2a lane and no RBT-116 gate lane, as LAUNCH.md requires.

---

## 9. Order of work and approvals

1. **This PR**, design and code. Then review: an adversary check, then the coordinator. The RBT-134 diagnosis's I5
   token selects §6.2's row. Nothing runs.
2. **The owner's GO for the validation** (§5). Validation runs, commits, and relays tokens. A ladder climb passes
   the cost stop rule first (§8).
3. **The registration amendment** sets `CPLUS_REGISTERED` and adds the 134b lane wiring with tests, including the
   cost stop rule before re-signing. It is reviewed, and the owner gives a GO for the registered run, which is
   first-hand: it spends the cost cap. **RBT-134b is registered when this amendment merges.**
4. **Lane B is unsealed** (§7): its committed E1, E2 and H1 outputs are read **after the owner's GO for the
   registered run** (step 3) **and before its readout** (step 5). Nothing is re-run.
5. **The registered run** at `MASTER_SEED`, in DESIGN.md §13's order (controls, the gate, checks, P2 first, then P3),
   with this document's controls, then its readout. C−'s sealed held-out counts may be printed there.

---

## 10. Predictions, both ways (fixed now; credences)

| id | prediction | credence | if wrong |
|---|---|---|---|
| V1 | `validate134b` ends **REGISTER C+ = C+L1** | 0.7 | yield below a quarter of the price (a bias walk or a fault I3/I9 shows), or a broken guard below |
| V1′ | `validate134b` ends **REGISTER** some rung (L1, L2 or L3) | 0.8 | as V1 beyond L3's reach (the price wrong by more than about 85×), or a broken guard below. Under the cap a climb may end in `STOP-COST` first (§8); V1′ is then decided by the owner's ruling, not by the ladder |
| V2 | C− fails clearly (lower bound > 2) on both seeds | 0.9 | the pump in r3's background was largely remnants of transient structure; the never-structured measure then lacks power, and the outcome is ESCALATE |
| V3 | I9 holds for every C+ rung run | 0.97 | a leak path not in §1, such as a plant invisible to the predicate after a later change: a code fault |
| V4 | I5-S B0 holds on both seeds | 0.97 | a source-dependent path in the predicate, synthesis or operator (reading c), absent at `MASTER_SEED` (the diagnosis's EXACT) but present at a held-out seed |
| V5 | B0's never-structured background is within sampling of r3's 22 of 9,990 rate on both seeds | 0.85 | transient structures are hits more often than expected; reported, not tuned (§4.7) |

**What V1 rests on (review M3).** Not on the price being tight. L1 is accepted with k ≥ 20 on both seeds, against a
priced E[k] of 43–85. So V1 holds if the true yield is anywhere above about a quarter of the w = 1 price: the price
may overstate the yield up to about 4×. L2 and L3 extend that to about 17× and 85× (V1′). The remaining 0.3 on V1 is
for a price more than 4× high, which is possible: the mechanism is priced, not observed. It also covers a broken
guard.

**The family, restated for the never-structured measure (review M4; fixed before validation).** DESIGN.md §10's
primary predictions carry over, because k and its test do not change. The background half changes, because the new
measure can only lower a condition's background (§4.6). These credences replace DESIGN.md §10's P2, P3 and family
rows for 134b:

| id | prediction | credence | if wrong, it means |
|---|---|---|---|
| P2-b | **NULL**: k < 6 | 0.55 (as r3) | default-size biases leave enough sub-saturating b_k for wide links to pay (r3's reading, unchanged) |
| P2-bg | P2's never-structured background ratio is ≥ 2 (point estimate) | 0.75 | P2's r3-measure excess, if any, was largely its own remnants of transient structure: then its EXCLUSION-FLAG should be set, and r3's bound printed beside it will differ from 134b's |
| P3-b | **MOVES-WITH-BACKGROUND**: k ≥ 6, never-structured clause fails | 0.40 (r3: 0.45) | if **PASS** (0.12): resetting biases tames recurrence, or the background it raises lies in remnants (read with the flag and r3's bound); if **NULL** (0.48): the reset's N(0, 0.5) leaves f(b_k) too large against v ≈ 4.5 |
| flag | neither P2 nor P3 carries the EXCLUSION-FLAG | 0.8 | wide links make transient structures common enough that the exclusion could carry a verdict; that verdict is then read beside r3's bound |
| family-b | **no PASS** | 0.8 (r3: 0.65) | — |

**family-b follows from the rows above (review R1).**
- **P(P2 PASSes) ≤ 0.11.** P2 PASSes only if it rejects (1 − 0.55 = 0.45) and its clause holds. The clause holds
  only if the Katz upper bound is ≤ 2, which needs the point ratio below 2: P2-bg leaves that at 0.25 at most. So the
  bound is 0.45 × 0.25 ≈ 0.11, treating rejection and the background as independent. If anything they are positively
  dependent: a wide link step that lets circuits pay also pumps whole-brain gain. That makes a PASS rarer, not
  commoner.
- **P(P3 PASSes) = 0.12**, its row.
- **P(some PASS)** therefore lies between 0.12 (the PASSes coincide) and 0.11 + 0.12 = 0.23 (they never coincide).
  P3 shares P2's link steps, so the two are positively correlated. Take about 0.2.
- **So P(no PASS) ≈ 0.8.**

r3's family row (0.65) is not carried over: by the same arithmetic on r3's own rows (P2 NULL 0.55, P3
MOVES-WITH-BACKGROUND 0.45), it was already lower than those rows imply. The never-structured measure can only lower
a background. It moves the rows towards PASS slightly (P3's PASS share), and family-b is recomputed from them, not
nudged from r3's figure. The shift is bounded by C−: a pump with r3's 6.9× must still read clearly above 2 on the new
measure (V2).

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
7. **Cost.** On ×1.5 pricing from the slower measured host, the worst case (35.7) and base plus re-signing at its
   cap (30.9) exceed the 30 CPU-h cap (§8). The stop rule returns to the owner before any run, climb or re-signing
   could cross 30, so the cap holds. The price is that a ladder climb may stop for a ruling (§8 gives when).
8. **Lane B is not re-run** (§7). Its outputs come from the r3 GO sha. They apply only while the scripts and fields
   they used are unchanged, which is tested for the fields.

---

## 12. Files

- `runs/RBT-134/DESIGN-134b.md`: this document.
- `runs/RBT-134/assay.py`: the 134b path (§7, "Code (this PR)").
- `runs/RBT-134/design-134b/parent_checks.py` and `.txt`: V, S1, S2, brain sizes, b_E and Y0 on the committed parents.
- `runs/RBT-134/design-134b/cplus_price.py` and `.txt`: the ladder's arithmetic.
- `runs/RBT-134/design-134b/timing.py` and `.txt`: CPU per lineage of each 134b step (throwaway seed 1), for §8.
- `tests/test_rbt134b.py`:
  - the guard and the constants;
  - the trimmed swaps, the cost envelope against the cap, and the cost stop rule (including a ladder climb that stops);
  - C− sealed (token only; background rows only), and I5-S B0 cited at `MASTER_SEED`;
  - the EXCLUSION-FLAG;
  - the two code facts (§7), and that 134b's lineages are r3's;
  - plants are structure, and unplanted lineages are B0's (throwaway seed 1, an artificial rate);
  - the swap exchanges the two predicates;
  - V on every parent;
  - the readout, I9, I5-S, C− and the validation summary on synthetic records.
