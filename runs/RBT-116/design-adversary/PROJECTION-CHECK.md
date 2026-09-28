# RBT-132 projection check: `runs/RBT-116/k3_projection.py` at integration `914667e`

*2026-09-28, the design adversary. Checked against:*
- *the coordinator's 09:43 ruling on #459 (comment 5867427907), item 2;*
- *DESIGN §12's K3 calibration amendment (09:44, #464);*
- *the implementer's note (#459 comment 5869600478).*

**Pre-data.** The calibration lane has not run. Everything here uses synthetic inputs, plus the δ values of the
fix-check's own fixture plants.

## Verdict: **FIX**

**The projection is sound.**
- On the inputs the calibration will give it, the plug-in model is **conservative at the decision boundary**. The rule
  passes an instrument that cannot reach 0.6 at most 1.3% of the time.
- The per-cell reading is the conservative one, and is faithful to the ruling.
- 20 of 21 mutants die.

**The fix is needed elsewhere.** The rule's "raise the counts to 32 or 64" branch has **no registered way to run**:
- 64 is infeasible under the registered draw pool.
- 32 is marginal.
- Nothing in `steer.py` changes the battery size without touching W1's constants.

This has to be registered before the calibration measures anything, so that every branch of the rule is executable
(M1).

**One reassurance on item 4 first.** The projection only chooses the battery size; it certifies nothing.
- K3 is still measured at every probed point, on that point's own planted plants, at the chosen counts. A plant counts
  there only on real SEEN verdicts.
- So an optimistic projection cannot make the layer pass. It can only launch a probe leg whose K3 then VOIDs, which
  costs budget but not validity.
- That holds as long as K3 runs at the new counts at every point (M1(b) keeps it so).

## 1. The model

| assumption | sound? | direction |
|---|---|---|
| each plant's per-draw ΔT ~ Normal(μ, σ²) | yes. ΔT is a difference of per-season chemotaxis indices, and the t bound is robust at n ≥ 16. `p_c2` matches a seeded simulation of `steer.lower_bound` (the test), and is exactly 0.05 at μ = 0 | neutral |
| σ recovered from `lbdT` | yes, exactly: σ = (dT − lbdT)·√n / t(0.95, n − 1), with n the record's usable draws. Mutants `proj-sd-no-sqrt-n` and `dT_sd-sqrt-n-minus-1` both die | neutral |
| P(c2 at n) by chi-square quadrature | yes. The grid holds the χ² mass (mutants `chi2-range-truncated` and `quadrature-grid-21` die) | neutral |
| P(SEEN) = P(c2)²: stage 2 and the confirmation independent | yes, given the plant: they are disjoint draws of the same plant | neutral |
| the veto (c3) taken as passing | acceptable. c3 is "> half the draws differ", so a plant whose per-draw differ rate is above ½ passes more surely at larger n. Only a plant that squeaked past at 16 with a rate below ½ is overstated. The fix-check saw c3 pass on every plant | slightly anti-conservative, negligible (NIT N1) |
| **the measured μ̂, σ̂ plugged in (the winner's curse)** | see below | **conservative where it matters** |

**Does the measured μ inflate the projection?** I simulated this (`rbt132_projection_check.py/.txt`, 400 calibrations
per scenario):
- **Setup:** 2 cells × (8 (a) + 8 (c)) plants. Each plant's 16 stage-2 draws give (μ̂, σ̂), exactly as `from_planted`
  recovers them, and these feed `k3_projection`'s own rule.
- **FALSE PASS:** the rule picks a count at which the true share is below 0.6 for some kind at some cell.
- **FALSE UNREADABLE:** the rule says unreadable, but 64 would have reached 0.6.

| true per-plant δ = μ/σ (all plants) | true share at 16 / 32 / 64 | true rule | plug-in: FALSE PASS | plug-in: FALSE UNREADABLE | plug-in bias at 16 / 32 / 64 |
|---|---|---|---|---|---|
| 0.20 | 0.04 / 0.09 / 0.23 | unreadable | 0.000 | — | +0.11 / +0.18 / +0.17 |
| 0.30 | 0.10 / 0.26 / 0.59 | unreadable | **0.013** | — | +0.12 / +0.13 / −0.05 |
| 0.35 | 0.14 / 0.38 / 0.76 | 64 | 0.000 | **0.93** | +0.13 / +0.07 / −0.15 |
| 0.40 | 0.21 / 0.51 / 0.88 | 64 | 0.007 | **0.73** | +0.11 / +0.01 / −0.20 |
| 0.50 | 0.37 / 0.76 / 0.98 | 32 | 0.000 | 0.20 | +0.06 / −0.11 / −0.19 |
| 0.70 | 0.72 / 0.97 / 1.00 | 16 | 0.000 | 0.003 | −0.07 / −0.13 / −0.06 |
| fixture-shaped (δ 0.78 … −0.18) | 0.13 / 0.18 / 0.27 | unreadable | 0.000 | — | +0.06 / +0.11 / +0.13 |
| fixture-shaped × 2 | 0.26 / 0.42 / 0.60 | 64 | 0.000 | **0.98** | +0.07 / +0.03 / −0.04 |

**What the simulation shows:**
- **The winner's curse is real, but only where it cannot matter.** The plug-in projected share is inflated by
  +0.06 to +0.18 where the true share is low (P(SEEN) is convex there). Those cases are far below 0.6, and the rule
  still says unreadable.
- **Near the decision, the bias turns negative.** At high n, P(SEEN) is concave in δ, and the rule needs all four
  kind-cells to reach 0.6. So the plug-in is **conservative at the boundary**: FALSE PASS stays ≤ 0.013 in every
  scenario.
- **The cost is FALSE UNREADABLE.** A layer that 64 draws would make readable is declared unreadable 73–98% of the
  time when the true δ is 0.35–0.40. In practice the rule reads a layer only when per-plant δ is about 0.5 or more
  (a true share at 16 of about 0.37 or more).
- **Should the projection use a lower bound on μ? No.** An 80% lower bound on each plant's μ (the second row per
  scenario in the `.txt`) keeps FALSE PASS at 0 but pushes FALSE UNREADABLE to 0.99–1.00 at δ 0.35–0.50, and 0.32 even at
  δ 0.70. It adds conservatism on top of a rule that already has it, and K3 at the points is the real guard. Keep the
  plug-in.
- **If the coordinator wants fewer false unreadables** (optional, S2), give the projection more data per plant rather
  than a different estimator. Run the confirmation battery on **every** (a) and (c) plant at the calibration, which
  gives 32 draws per plant. That cuts FALSE UNREADABLE to 0.41 at δ 0.40 and 0.025 at δ 0.50, and FALSE PASS stays
  ≤ 0.005.

**Does the veto's pass rate at larger n matter?** Only through plants whose per-draw differ rate is below ½. The
calibration record has each plant's `differ` count, so c3 can be projected exactly:
P(c3 at n) = P(Binomial(n, differ/16) > n/2), and P(SEEN) = [P(c2)·P(c3)]². This is cheap; see NIT N1.

## 2. The per-cell reading

**The ruling's text.**
- **First branch:** "≥ 0.45 for both (a) and (c) at both cells". `launches_as_registered` reads it per kind and per
  cell, not pooled. **This is the text.** A pooled reading would let one cell's strength carry the other (the test
  shows it: (8, 8) and (3, 8) would pool to pass).
- **Second branch:** "the smallest powers of 2 at which the projected per-plant SEEN share reaches 0.6 for both kinds".
  The text does not say per cell. `rule` projects each cell on its own plants, takes the **largest** count either cell
  needs, and is unreadable if either cell is. **This is the conservative reading, and the consistent one.**

**How strict the first branch is.** It needs at least 4 of 8 in all four kind-cells. At a true share of 0.45 it
launches as registered only 7.5% of the time, and at 0.60 only 47%. A kind-cell at 0.45 SEEN has K3 false-VOID
0.037. So the first branch rarely launches an unseeing instrument, and falls through to the projection most of the
time.

## 3. Tests and mutants (`rbt132_projection_mutants.py/.txt`)

- **The implementer's 12 projection mutants, re-run: 12 / 12 killed.**
- **My 9 further mutants: 8 killed.** They cover: target 0.5, a cap of 128, the veto from the record ignored, the rule
  taking the first cell, the quadrature grid of 21, the χ² range truncated, `dT_sd` with √(n − 1), and a stage-1 stop
  projected as a null plant.
- **The one survivor is `report-projects-pooled-cells`.** `report()`, the function the calibration lane actually
  prints, builds each cell's projection with `from_planted(paths)`, which **pools both cells' plants**. No test catches
  it: the per-cell test calls `rule()` directly, and the `report` test uses a single file. That is a silent fault in
  the executed decision path (S1).

## 4. Anything else: the raised counts have no registered implementation (M1)

**The rule can choose 32 or 64 stage-2 and confirmation draws. Nothing registered can run them:**

| | 16 (registered) | 32 | 64 |
|---|---|---|---|
| admissible draws needed (4 + 2n) | 36 | 68 | **132** |
| the registered pool (64, once extended by 32) | 96 | 96 | **96: impossible** |
| admissible share needed from 96 | 38% | 71% | > 100% |

- **The shares are tight.** The W1-shaped fixture screen admitted 49 of 64 (77%); a sweep cell's share is unknown.
- **So 64 cannot run.** And 32 fails the gate at any point whose admissible share is under 71%.
- **The constants are global.** `N_STAGE1, N_STAGE2, N_CONFIRM` and `POOL_SIZE, POOL_EXTENSION` are module constants in
  `steer.py`, shared with W1. Raising them in place would break W1's byte identity (its tests pin them).

### MUST

**M1. Register how a raised count runs, pre-data, before the calibration.**
- **(a) Battery size and pool per point, not global.**
  - Add per-point `N_STAGE2`, `N_CONFIRM` and pool size, as `REGISTERED_POINTS`-style rows or a `battery_size(point)`
    lookup. W1 keeps 4 + 16 + 16 and 64 + 32 by default.
  - Thread them through `assign_battery`, `screen_draws` and `draw_pool`.
  - Prove W1 unchanged: the identity run, the kill-sets and `power_tau1.txt`.
- **(b) Planted and probe run at the chosen counts.**
  - "for plants and members alike": `planted`, `probe_members` and `pays` read the same per-point counts.
  - The planted command's K3 at each point then uses real SEEN verdicts at those counts. **This is what makes the
    projection harmless if it is optimistic.**
- **(c) Pool size by a registered rule.**
  - For example: pool = ⌈(4 + 2n) × 64 / 36⌉, extended by half again, from the same `POOL_KEY` stream (`draw_pool`
    already extends the stream without changing the first draws). That gives 121 + 61 at n = 32, and 235 + 118 at
    n = 64.
  - Keep the screen's rule: extend once, then fail the gate.
- **(d) Print the cost beside the pick.**
  - A member's stage 2 runs 4 conditions, so going from 16 to 64 draws roughly quadruples the probe leg's seasons.
  - `k3_projection.report` should print the probe leg's core-hours at the chosen count, so the budget is decided with
    it, not after.

### SHOULD

**S1. Make `report()` project per cell, and test it.**
- Use `per_cell = {p: from_planted([p]) ...}` as the docstring says. (The line reads that way today; the mutant shows
  nothing pins it.)
- Add a test: `report` on two planted files, one strong and one weak. Assert that the rule line reads UNREADABLE or the
  larger count, and never the pooled answer.

**S2. Optional, the coordinator's call.** Run the confirmation battery on every (a) and (c) plant in the calibration
lane. Only `k3_confirm` changes: its `s2.c2 ∧ s2.c3` gate is dropped for the calibration cells. Each plant then gives
32 draws to the projection. In the simulation this halves FALSE UNREADABLE near δ 0.4, at no cost in FALSE PASS.
- It reads nothing new: still controls only.
- Cost: 16 × 2 seasons per plant per cell.

### NIT

- **N1.** Project the veto from each plant's `differ` count (P(Binomial(n, differ/n₀) > n/2)), instead of taking it as
  a certain pass.
- **N2.** A plant with θ refusals has a stage-2 `n` below 16. `from_planted` uses the record's `n` for σ, which is
  correct, but the projection assumes all n draws are usable at the new count. Print the refusal count per plant
  beside its ΔT, so a high-refusal plant is visible.

## Files

In `runs/RBT-116/design-adversary/`:
- `rbt132_projection_check.py/.txt`: the winner's-curse simulation, the lower-bound variant, the 32-draw
  calibration, and the first branch's pass rates.
- `rbt132_projection_mutants.py/.txt`: the implementer's 12 mutants and my 9, with the control.
