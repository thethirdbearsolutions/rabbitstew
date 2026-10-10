# RBT-134: control-gate failure, lane A (GO 0ad0afae)

## How this note was written

The designer wrote it from three sources only: the RELAY block, DESIGN.md and the merged code. **No output file was
read.** Nothing here comes from `readout-controls.txt`, the control JSONs or lane B.

The only data figure below is B0's food count of 84. It is public: RBT-91's committed baseline, and the RELAY's
`I2 B0: YES YES` says B0 reproduced it.

r2 answers the adversary's review of r1 (#571, REQUEST-CHANGES) and the coordinator's ruling on it (§2).

## 0. What happened, and what DESIGN.md registers for it

Lane A ran B0, C+ and A0. It then ran the registered readout over those three, and stopped at the gate (exit 8).

**The RELAY:**
- VOID list: `I5 B0, I5 C+, I5 A0, I4 C+`.
- Passed: `I2 B0 YES YES` (arrival set and responses, line for line); `I2 A0 YES`; B0's background prefix `all` and
  `unflagged`, both `YES`; `I3 A0 YES`.

**Absent from the VOID list:** "B0's own k", "predicate-mismatch" and `I3`. So:
- B0's k at a = 32 is 0;
- the generalised predicate agrees with `structural_rate.motif_units` in all three conditions;
- no control has an unflagged slope-bound violation.

**What DESIGN.md registers:**
- §9: "any failure VOIDs the stage it guards". I1–I7 guard the Pioneer assay.
- §13 step 3: "I1–I7 must pass" before step 4, the family.
- §6.4: C+ "must PASS. If it does not, the instrument is VOID (I4)".

So the registered outcome is:

> **The Pioneer stage is VOID. P1–P5 did not run. There is no family verdict.**

DESIGN.md registers **no** remedy beyond this: no diagnosis, no amended control and no re-run. Its only rule about
follow-ups is §6's: "No condition is re-run at another value after seeing data. A follow-up value is a new
pre-registration." Everything in §§2–5 is therefore a plan, under the coordinator's ruling. **The owner has not
approved running the diagnosis.**

## 1. What each VOID means

### I5 B0, I5 A0, I5 C+: the sham check

**What I5 checks.** I5 (§9, with amendment I5-a) requires the `agent`-nose sham predicate's lineage count to lie
inside the central 99% Binomial range of a food count:
- for B0 and A0, their own food count;
- for C+, B0's food count.

B0's food count is the committed 84 of 200,000. The range is **[61, 109]** (`assay.binom_range(200000, 84/200000)`).
B0's sham count is therefore outside [61, 109]. The RELAY does not say in which direction.

**B0 and A0: one failure.** A0 changes only the bias sigmas, and biases do not enter the predicate, which is purely
structural. `I2 A0 YES` says A0's arrival set equals B0's 84. So A0's sham count should be B0's exactly, against the
same food count. A0's failure is B0's failure counted again.

**C+: expected to move with B0, and possibly raised by the pair event itself.** The event (`genetics._pair_event`) adds
a `tanh` unit k with opposite-signed in-links from the two **food** noses. It also adds **same-signed out-links to both
wheel Effectors**. Those out-legs are exactly the Effector half of the predicate, whatever the source. So an `agent`
arrival on k needs only two opposite-signed in-links from the agent noses. C+'s sham count is therefore expected to be
near B0's, but it can be **raised** by the events. I5-a's comparison of C+ against B0's food count can fail by
construction, as I5-a itself found for the sham-against-own-food comparison.

**Three readings of the B0 failure, not mutually exclusive:**

- **(a) The premise is false: the parents are not symmetric between `food` and `agent`.**
  - I5 assumes that a sensor-blind operator gives the sham predicate the same arrival rate as the food predicate.
  - That holds only if the starting structure is symmetric between the two nose types.
  - The parents (`W4b-801-bests`, `P-801-final60`) are evolved champions, selected on food. Any food-nose wiring they
    carry, such as one leg of the motif, makes a food arrival within 19 mutations likelier than an agent arrival.
    Wiring the other way would do the opposite.
  - §3's "both pools carry both, on the same parts" is true of the *sensors*. It is not true of their *wiring*, and
    this was not checked.
  - B0's operator does not branch on food against agent. `mutate_controller` reads a sensor's source only to find
    `oscillator`, and reads `food` only inside the pair event, which is off in B0.
- **(b) The test is too strict.** The registered I5 compares a sampled sham count with a range built around a sampled
  food count, as if the food count were exact.
  - Under perfect symmetry, both counts are Poisson(84). Simulated over 200,000 draws, the registered rule then VOIDs
    **6.3%** of the time, against 0.7% when the food count is held fixed.
  - Caveat: food and sham are counted on the **same** lineages, and a lineage can carry both. The 6.3% treats the two
    counts as independent. A positive covariance narrows the true spread of the difference, so 6.3% is an upper-side
    figure.
- **(c) A pipeline fault in the sham predicate.** `assay.predicate(ph, "agent")` is the food predicate's code with the
  source swapped, and the food path matches `motif_units` everywhere. A fault specific to the agent path is unlikely,
  but not excluded.

### I4 C+: the positive control failed

C+ must PASS (§6.4). That means three things:
- it rejects at α 0.025 against B0;
- its **k at a = 32 is at least 6**;
- it **HOLDS** the background clause (Katz upper bound ≤ 2).

So the instrument has not shown it can return PASS on a planted, paying motif. DESIGN.md calls this VOID in its own
words. It is the more serious of the two failures.

B0's k is 0, so the McNemar p is 0.5^k, and "rejects" is the same as "k ≥ 6". C+ therefore failed on k (supply, rung
or flag; §3.3) or on the background clause.

### I3 B0 NO-TOKEN: harmless

B0 has no I3 bound: `CHECK_BOUND` lists only A0, P1, P2 and P3. Its readout line is `I3 B0: slope-bound violations N`,
with no YES or NO, so the relay prints `NO-TOKEN`. B0 is not on the VOID list, so N is 0. C+'s I3 line has the same
shape. This is a relay cosmetic, not a finding.

## 2. Rulings recorded (coordinator, 2026-10-10, on #571's review)

1. **Option (i) is adopted.** The decision table in §3 is registered **before any control output is read**. The
   diagnosis returns **only the categorical outcome** (§4). The r4 controls are the ones the table assigns to that
   outcome, and nothing else.
2. **Reading control numbers is permitted only after this decision table is merged.** Even then, only the diagnosis
   reads them, and it relays categories (§4.3). The diagnosis itself waits for the owner's approval.
3. **A new C+ may be derived only from committed inputs** (the merged code and DESIGN.md). It must be validated on a
   **held-out seed set**, not `MASTER_SEED 20260912`, before it is registered (§3.4).
4. **Regeneration in the diagnosis is restricted to B0 lineages.** No registered condition other than B0 is
   regenerated.

## 3. The decision table (registered before any control output is read)

### 3.1 Changes in r4 whatever the outcome

These follow from the code and from the simulation above, not from any control number.

- **U1. C+ and P5 leave I5.** The pair event pre-builds the Effector legs for any source (§1), so these two conditions
  are not sensor-blind in a way the sham can test. Their sham counts stay in the readout, **descriptively**. I4 still
  guards C+, and the ceiling still guards P5.
- **U2. I5's test becomes paired and exact.** The registered test treats a sampled count as exact (reading (b)). r4
  replaces it with a two-sided exact test on **discordant lineages**: d lineages carry exactly one of the two predicate
  sets being compared, and the test asks whether one side's share of d is Binomial(d, ½) at the 99% level.
  - `assay.py` records the sham lineage indices (`sham_ids`), not just the count. This is a `runs/RBT-134/` change
    only.
  - What the two sets are depends on §3.2's outcome.

### 3.2 I5 outcome → I5 form

The diagnosis assigns exactly one category. Steps I5-1 to I5-3 are in §4.

| category | when (§4) | I5 in r4 (sensor-blind conditions A0, P1–P4, plus B0 where it applies) | role |
|---|---|---|---|
| **I5-B** (reading b) | the regenerated B0 food and sham sets are **not** rejected by U2's paired test at 99% | per condition, U2's paired test of its **sham set against its own food set**, at 99% | **unchanged:** an instrument control on the food/agent symmetry of the predicate under a sensor-blind operator |
| **I5-A** (reading a) | B0's paired test rejects, **and** the swap test is EXACT | per condition, U2's paired test of its **sham set against B0's sham set**, matched by lineage index, at 99% | **changed: an operator sensor-blindness check, no longer an instrument control** (see below) |
| **I5-C** (reading c) | A0's sham count ≠ B0's; **or** the B0 regeneration does not reproduce B0's 84 food lineages and B0's recorded sham count; **or** the swap test is NOT EXACT | the fault is found and fixed in a PR with a regression test, adversary-checked; then **I5-1 to I5-3 run once more** on the fixed code; I5 is then I5-B's or I5-A's form, as that second pass decides | as that form |
| **ESCALATE** | the second I5-C pass is I5-C again | none: the Pioneer stage stays VOID; no r4 re-run; the owner decides | — |

**What I5-A's form gives up, stated plainly:**
- B0's own I5 becomes vacuous: B0 compared with itself.
- A0's I5 becomes an identity check, because A0 is B0's structural twin.
- The food/agent symmetry check is **dropped**. I5 would no longer test the predicate. It would test the operator: does
  the condition change the agent-arrival lineages that B0 makes?
- The instrument-level evidence that remains is the swap test's exactness. It shows the predicate code and B0's operator
  are source-agnostic lineage by lineage. That fact is recorded in r4.
- B0's food/agent asymmetry is reported **descriptively**, as a property of the parents.

### 3.3 C+ failure mode → C+ change

Let:
- **A** = C+'s arrivals;
- **k** = C+'s k at a = 32, as registered: unflagged arrivals only, whole-arrival rule;
- **k_raw** = C+'s arrivals whose maximum |a| is at least 12.5236, flags included;
- **ev / ref / np** = `pair_events` events / refused / no_pair.

The categories are exhaustive, given that C+ failed.

| category | when | C+ change in r4 (derived from committed code only) |
|---|---|---|
| **C+-BG** | k ≥ 6 (so it rejects) and the Katz upper bound > 2 | **ESCALATE.** No C+ change can pass a background clause that the event itself fails without changing the clause, which r4 may not touch. This is a finding against N6. The stage stays VOID and the owner decides. |
| **C+-FLAG** | k < 6 ≤ k_raw | **ESCALATE.** The event's own unit is `tanh` and is never flagged. So the binding item is the registered `sign` rule (F2) on the motif's other units. That is an instrument rule, not a C+ parameter. |
| **C+-RUNG** | k_raw < 6 and A ≥ 84 + 6 (enough new motifs; too few reach the rung) | **Scale ladder.** `pair_event_scale` 16 → 32 → 64, the first that passes §3.4 |
| **C+-SUPPLY-RARE** | k_raw < 6, A < 90, and ref + np ≤ ev / 2 | **Rate ladder.** `pair_event_rate` 0.005 → 0.02 → 0.05, the first that passes §3.4 |
| **C+-SUPPLY-REFUSED** | k_raw < 6, A < 90, and ref + np > ev / 2 | **Rate ladder as above, with C+'s `max_units_per_brain` 12 → 16** (a `MutationConfig` field: no `rabbitstew/` change) |

Each ladder changes only the one named field. Everything else in C+ is as registered: bias 0, the `tanh` unit, the
other fields. If no rung of the ladder passes §3.4, the outcome is **ESCALATE**.

### 3.4 Held-out validation of a new C+

1. Each candidate value, in ladder order, is run with B0 at the held-out **`MASTER_SEED 20261011`**. The pools are the
   same, at 100,000 lineages per pool, with the registered pipeline.
2. The first candidate that PASSes the registered rule against that seed's B0 is registered: k ≥ 6, the McNemar test
   at α 0.025, and the Katz upper bound ≤ 2.
3. Only then does it run at `MASTER_SEED 20260912`, in r4.
4. The held-out runs are reported in full. They are a tuning set and are never pooled with the registered run.

### 3.5 Putting it together

- **r4 =** U1 + U2 + the I5 form from §3.2 + the C+ change from §3.3.
- **Any ESCALATE** means no r4 re-run: the Pioneer stage stays VOID, and the owner decides.
- **r4 may not change:** any family or check value, n, the rungs, the decision rule, the background clause or the
  `sign` rule. It is adversary-checked and ruled before anything re-runs.

## 4. The diagnosis (plan only: not approved to run)

### 4.1 What it may read

**Only after this table is merged and the owner approves:**

| source | what it is for |
|---|---|
| `runs/RBT-134/out/readout-controls.txt` on `claude/rbt134-runs-A` | the I5 and I4 lines; C+'s line under "Checks and the positive control" (k, p, background upper ratio); the arrival-table rows for B0, C+ and A0 |
| `runs/RBT-134/out/B0.json`, `A0.json`, `C+.json` on the same branch | `sham`; `arrivals` with their units (`a`, `flip`) for k and k_raw; `pair_events`; `bg` for C+'s background clause |
| committed inputs | DESIGN.md, the merged code, RBT-91's `RBT-91-alone-baseline.txt`, and RBT-78's parent pools |

**It may not read:**
- `lane-A.log`;
- anything on `claude/rbt134-runs-B` beyond its RELAY tokens;
- any computation of P1–P5. In particular, it must not compute P2 from RBT-91's σ = 4.0 lineages (§11 risk 7);
- RBT-129 run directories, logs and `ckpt/*`.

**It may regenerate** B0 lineages only (ruling 4).

### 4.2 Steps

- **I5-1.** If `A0.sham ≠ B0.sham`, the category is **I5-C**. Stop the I5 steps.
- **I5-2. Regenerate B0's 200,000 lineages, predicate only (no probes).** Record per lineage whether it is a food
  arrival and whether it is a sham arrival.
  - If the food set is not RBT-91's 84 lineages, or the sham total is not `B0.sham`, the category is **I5-C**.
  - Otherwise apply U2's paired test to the food and sham sets: not rejected → **I5-B**; rejected → I5-3.
- **I5-3. The swap test.** Regenerate the same B0 lineages from parents whose sensors have `food` and `agent`
  relabelled into each other. Nothing else changes; B0's operator does not branch on the two (§1).
  - **EXACT** means the swapped food set equals the original sham set, and the swapped sham set equals the original
    food set, lineage by lineage → **I5-A**.
  - Anything else → **I5-C**.
  - **Preconditions**, checked on the committed parents before any lineage is regenerated. If either fails, the swap
    test cannot tell (a) from (c), and I5-3 returns **ESCALATE**:
    1. Every parent carries both a `food` and an `agent` sensor on each drive wheel. The predicate takes the first
       sensor of a source on each side, and mutation can add sensors whose source it draws from the vocabulary,
       unswapped. So a wheel side without both types could change which nose the predicate reads.
    2. Synthesizing a relabelled parent gives the original phenotype with only the two sources swapped: the same unit
       order and the same links.
- **C+.** From `readout-controls.txt` and `C+.json`, compute k, k_raw, A, ev, ref and np, and assign §3.3's category.

### 4.3 What it relays

Only these tokens:
- `I5: I5-B | I5-A | I5-C | ESCALATE`
- `C+: C+-BG | C+-FLAG | C+-RUNG | C+-SUPPLY-RARE | C+-SUPPLY-REFUSED`
- `I5-2 reproduction: YES | NO`
- `swap: EXACT | NOT-EXACT | not run`

No count, k, p, ratio or sham figure is relayed. The diagnosis commits its working, with the numbers, to its own
branch. That branch is read only after r4 is registered and adversary-checked.

## 5. Cost

| item | basis | CPU-h |
|---|---|---|
| I5-2 and I5-3 | two predicate-only regenerations of B0's 200,000 lineages: mutation and synthesis, no probes | about 1 at most |
| C+ category | reading the JSON | negligible |
| §3.4 held-out validation, if a ladder applies | held-out B0, plus up to 3 candidates, each about 0.8 × 1.5 (§12) | at most about 5 |
| the r4 re-run at the new GO sha | the full lane A, per §12; the lanes refuse JSONs from another head, so the controls re-run too | about 10, plus at most about 5 for re-signing |

**Lane B** (E1, E2, H1) is not guarded by I4 or I5, but §13 orders step 5 after step 4.
- **Proposal:** lane B finishes and commits, and its outputs stay unread, beyond its RELAY tokens, until r4 is ruled.
- **Reason:** its non-B0 rows are data on the P conditions.
