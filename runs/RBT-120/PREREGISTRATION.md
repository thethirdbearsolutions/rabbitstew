# RBT-120 pre-registration: how large is the holistic selection response when motor capacity is budgeted?

**Designer, 2026-09-27, before any B arm has run.** No B arm may launch until a design adversary has reviewed this
file and the coordinator has ruled.

**What it reuses:**
- RBT-113's design, command line, `readout.py` and `decompose.py`, **all unchanged**;
- RBT-117's `compare.py`, **unchanged**;
- RBT-113's frozen σ0 reference.

**What it adds:** one flag (`--motor-budget 1.77`; `DESIGN.md`), one registered readout (`budget.py`, Q1 and Q2), and
a bounded power model (`power.py`).

## 1. The question

RBT-113's holistic benchmark (b_div +0.095 raw per generation, h2 0.093) and RBT-117's HOLISTIC RESPONDS MORE both
carry a binding caveat. The down line bought its response through a motor-capacity allowance the mass budget does not
cap, and RBT-117's whole margin is that allowance.

**Registered questions:**
- **Q1 (primary):** how large is the holistic fauna's selection response when motor capacity is budgeted?
- **Q2 (registered test):** how much of RBT-113's holistic response was the lever? This is the paired difference
  between the same seeds with and without the budget.
- **Q3 (registered, secondary; RBT-117-style):** with motor capacity budgeted, does the holistic fauna respond more
  than the designed body?

## 2. Arms and pairing (`world.py`, `run_arm.sh`)

- **Four arms, B1–B4,** on RBT-113's default-operator seed blocks (1–3, 4–6, 7–9, 10–12): 12 seeds, each with U, D
  and C lines.
- **The command line is RBT-113's O arms' plus `--motor-budget 1.77`, and nothing else.** `world.py` imports
  RBT-113's `world.py` and appends the flag. A test shows the configs differ only in `sim.world.motor_budget`.
- **No Z arms.** Z does not reach the holistic fauna (RBT-113), so its salt-1 replicates would add holistic replicates
  but no new question. They are left out to halve the cost. The O arms' salt-1 twins (Z1–Z4) are used only as
  **replicate noise** in the power model.
- **Pairing with RBT-113's O arms at each seed:**
  - the same founder genomes (the budget does not touch the RNG streams; control K3);
  - the same worlds every generation (control K5, via readout.py's world check against U/D/C, plus K1);
  - **the designed body's lines are the O arms' lines byte for byte** (K2). The Pioneer is inside the budget
    (1.7605 < 1.77), so the designed side re-runs RBT-113 exactly. This is a free end-to-end control.
- **The holistic lines differ from generation 0.** About 6% of founders are over the budget and are scaled
  (`motors_O_at_1.77.txt`). After that they are an independent replicate, so they are paired by seed and founder, not
  by trajectory.

## 3. The quantities (fixed in `budget.py`, statistics from RBT-113's `readout.py`)

These are RBT-113's per-seed-directory statistics for the holistic fauna, in **raw yield per generation**: b_div,
b_up, b_down and h2 (`readout.arm_stats`). The scale is RBT-113's **frozen** holistic σ0 = 0.221249 (the D4
reference), so every number is on RBT-113's scale.

**Q1.** Per seed, b_div_B, over 12 seeds, with a t 95% CI and an exact sign-flip p. The verdict is RBT-113's rule,
applied on the frozen scale:
- **RESPONDS** if the CI lower bound is > 0 and p < 0.05;
- **NO RESPONSE at the powered effect** if the CI upper bound is < 0.05 σ0 per generation (RBT-113's MDE_DIV);
- otherwise **INCONCLUSIVE**.

Printed beside it: b_up, b_down, h2 and the D1 food/work split (decompose.json), each against the O lines at the same
seeds.

**Q2.** Per seed, **Δ = b_div_O − b_div_B** (holistic, raw), where O is RBT-113's salt-0 line at that seed. The test
is the exact sign-flip over 2^12 patterns, in frozen σ0.
- **THE BUDGET LOWERS THE HOLISTIC RESPONSE by x [CI]** if the CI lower bound is > 0 and p < 0.05. The share of the
  O lines' b_div is printed.
- **THE BUDGET RAISES THE HOLISTIC RESPONSE** if the CI upper bound is < 0 and p < 0.05.
- **NO CHANGE within ±0.05 σ0** if the CI lies within ±0.05 (RBT-113's EQUIV_OP).
- otherwise **INCONCLUSIVE**.

Δ is also printed on b_up and b_down (descriptive; the prediction below says where it should fall).

**Q3.** RBT-117's `compare.py`, unchanged, on the B seed directories (`compare_budgeted.py` swaps only the seed-set
check's arm map, O1–O4 → B1–B4). The primary d is final U − D, holistic minus designed, in raw net yield, with an
exact sign-flip. The verdicts are HOLISTIC RESPONDS MORE, DESIGNED RESPONDS MORE or NOT DECIDED. VOID applies iff the
C-line control has p < 0.05 and |c| ≥ C_BOUND = 0.8, or an RBT-113 control fails. SCOPE_1–SCOPE_4 are printed as
registered. The designed side equals RBT-117's exactly (K2).

## 4. Controls (`budget.py`; any failure VOIDs Q1 and Q2; each is shown passable and shown able to fail)

| | what | passable | can fail |
|---|---|---|---|
| **K1** | each B line's `config.json` equals the O line's plus `motor_budget` 1.77, and nothing else | a tiny O/B pair (`tests/test_rbt120.py::test_budget_readout_controls_pass_on_a_tiny_arm`) | the budget removed from one line's config |
| **K2** | every conventional lineage row of every B line equals the O line's | the tiny pair; `test_designed_body_is_byte_identical_through_a_whole_solo_run_under_the_budget`; **at full size**, `controls/k2_full_population.txt` (`k2_check.py`: line D, seed 5, 3 generations of 40 + 40 on 2 draws, all 120 designed rows identical, holistic rows diverge from generation 0) | one designed fitness altered |
| **K3** | the holistic founders' generation-0 names and body-plan hashes equal the O line's | the tiny pair | one founder's body hash altered |
| **K4** | every holistic `final/` member of every B line, compiled under its run's config, is within 1.77. It also prints the share the budget had to scale. | the tiny pair | the budget broken in `world.py`, and a planted 3.24× body |
| **K5** | RBT-113's per-seed-directory controls and selection checks (`readout.controls`, `selection_checks`) | as in RBT-113 | as in RBT-113 (`tests/test_rbt113.py`) |

`budget.py` also refuses (non-zero exit) a seed directory that is not a registered B directory: a Z name, a seed
outside its arm, or a repeated seed. Q3 carries RBT-117's own refusals and VOID.

## 5. Order at readout

See `RUNNER.md` §6: restore; `decompose_budgeted.py` (RBT-113's `decompose.py`, unchanged, run under RBT-120's
`world.py`); `readout.py` (unchanged, `--reference` the frozen σ0; descriptive); `budget.py` (Q1, Q2);
`compare_budgeted.py` (Q3); `motor_report.py` (deliverable 2). They commit by role.

## 6. The power model, bounded by each body's floor and ceiling (`power.py` → `power.txt`)

This applies RBT-113's lesson. RBT-117's unbounded Gaussian model predicted d ≈ −2.8, and it failed because neither
body stayed inside its founder scale. Here, **no quantity is an unbounded Gaussian**:
- **Expected responses are RBT-113's observed per-seed O responses scaled by bounded factors.**
  - **Up half:** ρ_up is the ratio of the U line's final U − C net under the budget to the registered value, from
    `counterfactual.txt` (the U line's own final genomes re-scored under the budget). The U lines are mostly within
    the budget already.
  - **Down half:** the D line's final work W lies between a floor and a ceiling.
    - **Floor, W_cf:** the D line's own final genomes re-scored under the budget, a line that found its motors
      unbudgeted and lost them at once.
    - **Ceiling, W_hi:** min(W_O, 0.99 × the budgeted free-spin ceiling at the D line's own mass). The 0.99 is how
      close ghost rotors come to their ceiling (RBT-121 auditor A, A2 and S1). A body at the mass budget has a
      ceiling of 0.977 yield.
    - Food is the O line's. ρ_down = (C_net − D_food + W) / (C − D)_O.
- **Noise is RBT-113's own replicate noise:** one replicate's deviation, drawn with a random sign from (O − Z)/√2 at
  each seed. The salt-0 and salt-1 lines at a seed are independent holistic replicates. B shares O's founders, so
  this overstates B's noise, which is conservative.
- **The designed side is fixed.** Its B lines are its O lines (K2).

**Results** (`power.txt`, 2000 simulated reruns per scenario):

The bounds are real, not assumed. Across the 12 O seeds (`counterfactual.txt`), the D line's work under the budget
at its own genomes is 0.56–0.85, against 0.70–2.60 as registered. Its bounded ceiling W_hi is 0.94–0.97, or W_O
where that is lower (seed 1). Every D member re-scored under the budget stays at or below 0.975: the budgeted ceiling,
and no longer 2× the designed body's.

| scenario | E b_div_B (raw / σ0; share of O) | Q1 | E Δ (σ0) | Q2 LOWERS / NO CHANGE / INCONCL. / RAISES |
|---|---|---|---|---|
| O as observed (salt 0) | +0.0975 / +0.441 | | | |
| **floor** (the D line keeps its counterfactual work) | +0.0575 / +0.260; 59% | RESPONDS 1.000 | +0.181 | **0.996** / 0.000 / 0.004 / 0.000 |
| **ceiling** (the D line reaches 0.99 × its budgeted ceiling) | +0.0685 / +0.309; 70% | RESPONDS 1.000 | +0.131 | **0.898** / 0.000 / 0.102 / 0.000 |
| **null**, ρ_down = 1 (the budget changes nothing) | +0.441 | RESPONDS 1.000 | 0.000 | 0.025 / 0.064 / 0.892 / 0.021 |
| no response at all (E b_div_B = 0) | 0 | RESPONDS **0.021**, NO RESPONSE 0.356 | | |

- **Q2's level holds:** a false LOWERS in 2.5% and a false RAISES in 2.1% of null reruns. Its sensitivity, with
  ρ_up = 1 and a uniform ρ_down: LOWERS 0.44 at ρ_down 0.8, 0.73 at 0.7, 0.90 at 0.6 and 0.98 at 0.5. **The 80% MDE
  is Δ ≈ 0.10 σ0 per generation.**
- **Q2's NO CHANGE is nearly unattainable.** The per-seed replicate SD of b_div is 0.108 σ0, so the CI of Δ cannot
  fit inside ±0.05 σ0 at n = 12 (0.064 under the null). **A null result will read INCONCLUSIVE, not NO CHANGE.** That
  is stated now, so that it is not read later as "the budget did nothing".
- **Q1 cannot fail to RESPOND** in any bounded scenario, because the up half is untouched: ρ_up is 0.80–1.24 and
  the U lines are mostly within the budget. **Q1 is estimation.** Its content is the magnitude, with its CI.
- **Q3** (d = holistic − designed final U − D, raw; observed unbudgeted +0.768):

  | scenario | E d | HOLISTIC | DESIGNED | NOT DECIDED | VOID |
  |---|---|---|---|---|---|
  | floor | −0.163 | 0.000 | 0.026 | **0.974** | 0.000 |
  | ceiling | +0.086 | 0.006 | 0.000 | **0.994** | 0.000 |

  The control is passable: the C-line VOID rate is 0 in both scenarios, with the B C line drawn as a new replicate.

## 7. The prediction, both ways

**Q1: RESPONDS**, with b_div_B = +0.058 to +0.069 raw per generation (+0.26 to +0.31 frozen σ0), which is
**59–70% of the unbudgeted O lines' +0.0975**. The up half is essentially unchanged, and the down half falls to about
a third to a half.

**Q2: THE BUDGET LOWERS THE HOLISTIC RESPONSE**, by +0.13 to +0.18 σ0 per generation (30–41% of the O lines'). The
drop is in b_down, not b_up.

**Q3: NOT DECIDED** (d between −0.16 and +0.09). This agrees with the readout adversary's work-capped d = −0.02.

**What each outcome would mean, fixed now:**

- **Q2 LOWERS, within the predicted range.** The lever carried about a third of RBT-113's holistic response. The
  budgeted b_div becomes the holistic benchmark number without the lever, and RBT-113's must be quoted beside it.
- **Q2 LOWERS by more than predicted** (the budgeted response below the floor, under 59%). The D line under the
  budget finds waste more slowly than a line that grew its motors first and lost them. The lever also sped up the
  response, not only its size.
- **Q2 INCONCLUSIVE, or LOWERS by less than the ceiling scenario** (above 70%). The D line reaches its budgeted
  ceiling and wastes as much as the gear allowed, through other means: ghost rotors at full throttle (auditor A's
  A2). The budget then bounds the ceiling but not the waste, and **A2 is the next lever to close.** This is not "the
  budget did nothing": NO CHANGE is nearly unattainable at this n (§6).
- **Q2 RAISES.** Not predicted in any bounded scenario (false rate 0.021). The budget would have pushed selection into
  a more effective channel, and that would need a probe before anything else is read.
- **Q1 INCONCLUSIVE or NO RESPONSE.** Not predicted (the up half is untouched). It would mean the U line's coverage
  gain (RBT-113 §4) also depended on motor capacity above the budget. Only 17% of U members are over the budget
  today (`motors_O_at_1.77.txt`), so that would be a surprise and a finding.
- **Q3 NOT DECIDED.** RBT-117's HOLISTIC RESPONDS MORE does not survive the budget, as the caveat says. Reason (a)'s
  perverse form is closed for motors.
- **Q3 DESIGNED RESPONDS MORE.** Possible at the floor (0.026). With capacity equal per kilogram, the designed body's
  larger food response (RBT-117's food-alone split) shows through.
- **Q3 HOLISTIC RESPONDS MORE.** Not predicted (0.006 at most). The holistic margin would survive a matched motor
  class, and the next suspects are ghost rotors and coverage, not capacity. **Either way it is not evidence for
  reason (b)**, because the holistic founders are the less variable (SCOPE_4).

## 8. Cost

- **Arms:** 4 arms of 9 `evolve` runs each, the same size as RBT-113's O arms. RBT-113 took about 1.9 h per arm
  (2.5 h for the slowest) with two arms side by side at WORKERS=2.
  - **Plan:** two runner sessions with two arms each, so **about 2–2.5 h wall-clock and about 16 core-hours**.
  - Four sessions with one arm each at WORKERS=4 would take about 1–1.3 h wall-clock at the same core-hours.
- **The designed side is re-computed and is byte-identical.** That is about half the compute, and it is the price of
  K2.
- **Readout:** restore (minutes), then `decompose_budgeted.py` on 12 directories (about 25 min on 4 cores; RBT-113
  took about 45 min for 24), then `readout.py`, `budget.py`, `compare_budgeted.py` and `motor_report.py` (minutes).
- **Total: about 3 h from launch to a readout PR.**

## 9. What the adversary should attack first

1. **K2's claim** that the designed lines re-run byte for byte. It is proved on a tiny solo run and on 3 generations at full size (`controls/k2_full_population.txt`), not on a full 24-generation O arm.
2. **The power model's bounds:** whether the counterfactual floor is really a floor, and whether 0.99 × ceiling is
   really a ceiling.
3. **Whether Q2's pairing** (same founders, independent trajectories) makes the sign-flip test valid.
4. **Whether the servo clamp under the budget** changes the holistic founders more than the ticket intended.
5. **What the budget leaves open:** ghost rotors (A2), and the coverage lever of the up line (RBT-113 §4).
