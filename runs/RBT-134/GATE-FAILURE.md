# RBT-134: control-gate failure, lane A (GO 0ad0afae)

Written by the designer from the RELAY block alone, plus DESIGN.md and the merged code. No output file was read for
this note. No number from `readout-controls.txt`, from the control JSONs, or from lane B is used here. The only data
figure below is B0's food count of 84, which is public: it is RBT-91's committed baseline, and the RELAY's
`I2 B0: YES YES` says B0 reproduced it.

## 0. What happened, and what DESIGN.md registers for it

Lane A ran B0, C+ and A0. It ran the registered readout over those three, and stopped at the gate (exit 8).

- **The RELAY's VOID list:** `I5 B0, I5 C+, I5 A0, I4 C+`.
- **What passed:**
  - `I2 B0 YES YES`: the arrival set and the responses line for line.
  - `I2 A0 YES`.
  - B0's background prefix, both `all` and `unflagged`, `YES`.
  - `I3 A0 YES`.
- **What else the VOID list tells us.** "B0's own k", "predicate-mismatch" and `I3` are absent from it. So B0's k at
  a = 32 is 0, the generalised predicate agrees with `structural_rate.motif_units` in all three conditions, and no
  control has an unflagged slope-bound violation.

**DESIGN.md §9:** "any failure VOIDs the stage it guards". I1–I7 guard the Pioneer assay. **§13 step 3:** "I1–I7 must
pass" before step 4, the family. **§6.4:** C+ "must PASS. If it does not, the instrument is VOID (I4)".

So the registered outcome is:

> **The Pioneer stage is VOID. P1–P5 did not run, and there is no family verdict.**

DESIGN.md registers **no** remedy beyond this. It names no diagnosis, no amended control and no re-run. Its only rule
about follow-ups is §6's: "No condition is re-run at another value after seeing data. A follow-up value is a new
pre-registration." Everything in §2 below is therefore a proposal for the coordinator and the owner to rule on.

## 1. What each VOID means

### I5 B0, I5 A0, I5 C+: the sham check, one failure counted three times

**What I5 checks.** I5 (§9, with amendment I5-a) requires the `agent`-nose sham predicate's lineage count to lie
inside the central 99% Binomial range of a food count:

- **B0 and A0:** their own food count.
- **C+:** B0's food count.

B0's food count is the committed 84 of 200,000. That gives a range of **[61, 109]**
(`assay.binom_range(200000, 84/200000)`). So B0's sham count is outside [61, 109]. The RELAY does not say in which
direction.

**Why the three failures are very probably one failure:**

- **A0 equals B0 structurally.** `I2 A0 YES` says A0's arrival set equals B0's 84. A0 changes only the bias sigmas, and
  biases do not enter the predicate, which is purely structural. So A0's sham count should be B0's exactly. A0 has the
  same food count too, so A0's check is B0's check again.
- **C+ is almost the same.** C+'s pair event wires only the `food` noses (I5-a). So C+'s `agent` structure is B0's up to
  the index shift after an added unit (§2.2: "a twin of B0 only up to its first event"). C+'s sham count should
  therefore be close to B0's, and I5-a compares it with the same food count of 84.

If B0's sham count is out of range, the other two are expected to be out of range with it. The diagnosis checks this
directly (§3, question 1).

**What the failure can mean.** Three readings, which are not mutually exclusive:

- **(a) The premise is false: the parents are not symmetric between `food` and `agent`.**
  - I5 assumes that a sensor-blind operator gives the sham predicate the same arrival rate as the food predicate.
  - That holds only if the starting structure is symmetric between the two nose types.
  - The parents are evolved champions (`W4b-801-bests`, `P-801-final60`), selected on food. Any food-nose wiring they
    already carry, such as one leg of the routed motif, makes a food arrival within 19 mutations likelier than an agent
    arrival. Wiring the other way would do the opposite.
  - §3's "both pools carry both, on the same parts" is true of the *sensors*. It is not true of their *wiring*, and the
    design did not check that.
  - If (a) holds, I5 was mis-specified. It is not evidence that the pipeline is broken.
- **(b) The test is too strict.** The registered I5 compares a sampled sham count against a range built around a
  sampled food count, treated as exact. Under perfect symmetry, both counts are Poisson(84). Simulated over 200,000
  draws, the registered rule then VOIDs **6.3%** of the time, not 1%. Holding the food count fixed at 84 gives the
  nominal 0.7%. A modest excess within two-sample noise would be this reading.
- **(c) A pipeline fault in the sham predicate.** `assay.predicate(ph, "agent")` reuses the food predicate's code with
  the source swapped. It takes the first agent sensor on each wheel side, as the food version does for food. The code
  path is identical apart from the source, and the food path matches `motif_units` on every lineage (no mismatch VOID).
  A fault specific to the agent path is therefore unlikely, but it is not excluded.

### I4 C+: the positive control failed

C+ must PASS (§6.4): it must reject at α 0.025 against B0, have **k at a = 32 ≥ 6**, and **HOLD** the background clause
(Katz upper bound ≤ 2). This failure means the instrument did not show it can return PASS on a planted, paying motif.
DESIGN.md calls this VOID in its own words, and it is the more serious of the two failures.

Because B0's k is 0, the McNemar p is 0.5^k, so "rejects" and "k ≥ 6" are the same condition. That leaves two ways to
fail:

- **k < 6.** Possible causes:
  - too few pair events, or events refused because the brain is full, or no wheel pair;
  - events that land but whose links-alone |a| falls short of 12.5236, for example because later mutations within the
    19 erode the planted ×16 links, or because the Effector's `sech²` at its own bias shrinks the gain;
  - planted arrivals removed whole by the `sign` flag (F2 option a).
- **The background clause fails.** This is unlikely. N6 says C+'s structureless lineages are mostly event-free default
  lineages. It is still possible if events also create whole-brain gain in lineages without the predicate.

### I3 B0 NO-TOKEN: harmless

B0 has no I3 bound (`CHECK_BOUND` lists A0, P1, P2 and P3). So its readout line is
`I3 B0: slope-bound violations N` with no YES or NO, and the relay prints `NO-TOKEN` for such a line. B0 is not on the
VOID list, so its N is 0: B0 has no unflagged probe above its slope bound. C+'s I3 line has the same shape. This is a
relay cosmetic, not a finding.

## 2. Registered next step and its cost

**Registered:** none beyond VOID (§0). A **re-run as registered** would be pointless:

- B0 and A0 are deterministic twins, so a re-run reproduces I5 B0 and I5 A0 exactly.
- C+ is deterministic too, so a re-run reproduces I4.

**Proposed, for ruling.** Three steps, each gated on the one before.

1. **Diagnosis** (read-only, §3). It settles which reading of I5 holds and which way C+ failed.
   - Cost: under 0.1 CPU-h.
   - The optional parent census in §3 takes seconds.
2. **A pre-data amendment (r4) to the controls only.** "Pre-data" holds because no family condition has run.
   - **It may change:** I5's definition, and C+'s construction if the diagnosis finds a design reason for I4.
   - **It may not change:** any family or check value, n, the rungs, the decision rule or the background clause.
   - **Every new definition is fixed and adversary-checked before anything re-runs.**
   - **Danger:** C+ and I5 would be redesigned after seeing that they failed. To answer that, each change must follow
     from a mechanism found in §3. It must also be checkable on data that does not include the failed counts, such as
     the parent census. A tolerance chosen so that the observed counts pass is not allowed.
   - Candidate I5 forms, for the ruling:
     - a two-sample test of sham against food, which fixes reading (b) only;
     - a sensor-blindness test of each condition's sham count against **B0's sham count**, which is what "the operator
       does not know which sensor is food" actually predicts. This is robust to (a).
   - Cost: the design time, one adversary round and the ruling.
3. **A re-run at the new GO sha.**
   - The lanes refuse JSONs from another head (exit 5). So B0, C+ and A0 re-run too, unless the coordinator rules that
     the existing control JSONs are moved aside and re-made.
   - The full lane A, per §12: about 10 CPU-h for the eight conditions, plus at most about 5 for re-signing.
   - The controls alone: about 3.6 CPU-h (3 × 0.8 × 1.5).
   - If I5 is redefined on recorded quantities (sham and food counts are already in each JSON), I5 itself needs no new
     computation. A new C+ needs its own pass, about 1.2 CPU-h.

**Lane B** (E1, E2, H1) is not guarded by I4 or I5. Those are Pioneer-assay controls, and H1 has its own. But §13 orders
step 5 after step 4.

- **Proposal:** lane B finishes and commits, and its outputs stay unread, beyond its own RELAY tokens, until the r4
  ruling.
- **Reason:** its non-B0 rows are P-condition data, so reading them now would be a peek at the operators before the
  family runs.

## 3. What the diagnosis may read

**Allowed, from `claude/rbt134-runs-A` at the lane's commit:**

| file | what it answers |
|---|---|
| `runs/RBT-134/out/readout-controls.txt` | the I5 lines for B0, A0 and C+ (sham count, range, direction); C+'s line under "Checks and the positive control" (k a32, p, background upper ratio, which clause failed); the I3 lines; the arrival table rows for B0, C+ and A0 only |
| `runs/RBT-134/out/B0.json`, `A0.json`, `C+.json` | `sham`, the arrivals with their units (`a`, `prod`, `func`, `flip`) for C+'s planted arrivals, `pair_events` (events / refused / no_pair) for C+, `bg` for C+'s background clause |

**Also allowed, as committed inputs rather than outputs:** DESIGN.md, the merged code (`assay.py`,
`rabbitstew/genetics.py`), RBT-91's committed `RBT-91-alone-baseline.txt`, and RBT-78's committed parent pools.

**Not to be read:**

- `lane-A.log`. It contains only control output, but it is not on the coordinator's list.
- `readout.txt`. It does not exist, because the lane stopped before writing it.
- Anything on `claude/rbt134-runs-B` beyond its RELAY tokens.
- Any computation of P1–P5. In particular, P2 must not be computed from RBT-91's σ = 4.0 lineages (§11 risk 7).
- RBT-129 run directories, logs and `ckpt/*`, as before.

**The questions, in order:**

1. **Are the three I5 failures one failure?** Check `A0.sham == B0.sham`, and whether `C+.sham` is close to `B0.sham`.
2. **Which way, and how far?** Compare B0's sham count with 84.
   - Inside the two-sample 99% band, about ±2.576·√(84 + sham): reading (b).
   - Far outside it: reading (a) or (c).
3. **Reading (a) against (c).** This step needs a ruling first.
   - Census RBT-78's committed parents, the 7 W4b-801 parents and the P-801 final 60, at depth 0 with no mutation.
   - For each nose type, count how many global units already carry one or both legs of the motif. Run the
     generalised predicate on the parents themselves.
   - This uses no registered condition and no lineage stream.
   - If the parents' food-side wiring explains the direction found in question 2, the reading is (a).
   - If it does not, read `predicate(ph, "agent")` against `motif_units` by hand on a few C+ or B0 sham lineages from
     the JSON indices. That is reading (c).
4. **How did C+ fail?** Look at C+'s k a32 against 6, its background ratio against 2, `pair_events`, and the
   distribution of planted arrivals' links-alone |a| against 12.5236, flagged or unflagged.
   - That separates "the event is rare or refused", "the event lands below the rung" and "the background failed".
   - The first two are design reasons, for example ×16 being too small at the Effector's operating point. The fix
     would then be a new C+ construction fixed in r4. The third would be a finding about N6.

The diagnosis reports in the same form as this note. It states the controls' numbers, which the coordinator now
permits because the family never ran. It does not touch any family or check condition.
