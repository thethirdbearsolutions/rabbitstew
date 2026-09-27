# RBT-120 pre-registration: how large is the holistic selection response when motor capacity is budgeted?

**Designer, 2026-09-27, before any B arm has run.** No B arm may launch until a design adversary has reviewed this
file and the coordinator has ruled.

**What it reuses:**
- RBT-113's design, command line, `readout.py` and `decompose.py`, **all unchanged**;
- RBT-117's `compare.py`, **unchanged**;
- RBT-113's frozen σ0 reference.

**What it adds:** one flag (`--motor-budget 1.77`; `DESIGN.md`), one registered readout (`budget.py`, Q1 and Q2), and
a bounded power model (`power.py`).

**Amended per the coordinator's ruling (21:50) on the design adversary (#410, reviewed on `0ce78e1`: LAUNCH AFTER
FIXES).** MUST 1–3 and SHOULD 1–7 are applied in place; the items are marked [M1]–[M3] and [S1]–[S7]. The launch tree
is unchanged at `7f4fe72`.

**The manipulation is the motor budget: two interventions [M1].**
- **The Σgear cap** scales 6.5% of RBT-113's holistic founders.
- **The servo clamp at ±gear** changes the rest: **34% of founders change**, 27.5% through the clamp alone
  (`design-adversary/probe_clamp.txt`).
- On the evolved O lines the cap does almost all the work (`apportion_O.txt`, 10 members per group per directory, one
  draw). D-line work is 1.68 off, **0.72 with the cap alone**, and 0.717 with cap + clamp. Founders, U and C move by
  ≤ 0.02 either way.
- Every question below is about **the motor budget, cap + clamp**.

## 1. The question

RBT-113's holistic benchmark (b_div +0.095 raw per generation, h2 0.093) and RBT-117's HOLISTIC RESPONDS MORE both
carry a binding caveat. The down line bought its response through a motor-capacity allowance the mass budget does not
cap, and RBT-117's whole margin is that allowance.

**Registered questions:**
- **Q1 (primary):** how large is the holistic fauna's selection response under the motor budget (Σgear cap + servo
  clamp)?
- **Q2 (registered test):** how much of RBT-113's holistic response did the motor budget remove? This is the paired
  difference between the same seeds with and without the budget. [M1]: not "how much was the lever"; the budget is
  cap + clamp.
- **Q3 (registered, secondary; RBT-117-style):** under the motor budget, does the holistic fauna respond more than
  the designed body?

**What the budget leaves on [M2].** It caps capacity and the servo wind-up. Two waste channels stay open to both
faunae:
- **the Effector-bias walk** (resting throttle): 99.2% of the designed D line's effectors, and 21.3% of the holistic
  D line's (auditor B, `RBT-121/ga/effector_bias_lines.txt`);
- **free rotors** on range-less ball joints: 97% of the holistic D line's work is on contact-free children (the
  synthesis's R2).

A budgeted holistic D line therefore has proven routes to its (budgeted) ceiling. The designed D line reached about 95%
of its own by the bias walk. **The ceiling scenario in §6 is the likelier one, not an outer bound.** The rerun
measures the cap, not the cone.

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
- **The holistic lines differ from generation 0 [M1].** 6.5% of founders are scaled by the cap, but **34% change**,
  27.5% through the servo clamp alone (`design-adversary/probe_clamp.txt`). After that they are an independent
  replicate, so they are paired by seed and founder, not by trajectory. Control K7 checks that the change happened.

### 2.1 The registered combination: the gear budget alone, not also the Effector-bias freeze

The coordinator asked (20:40) whether to run with auditor B's `--effector-bias-sigma 0` as well, so that the holistic
number carries neither lever. **I register the gear budget alone**, for four reasons:
1. **Q2 must isolate one lever.** Δ = b_div_O − b_div_B is only "the gear lever" if the budget is the only
   difference. With two changes at once, Δ has no single meaning.
2. **K2 needs it.** The freeze acts through `mutate_controller` as well (auditor B specifies parity), so it would
   change the designed body.
   - K2 (the designed lines are the O arms' byte for byte) would be lost.
   - So would Q3's property that its designed side is RBT-117's exactly.
3. **The flag does not exist yet.** It is the synthesis's fix #3, a GA change that needs its own designer, adversary
   and ruling. Putting it in this registration would put an unreviewed change into a scored path.
4. **Resting throttle is mainly the designed body's lever.** On RBT-113's 12 O directories (`motors_O.txt`), the
   share of Effectors at resting drive above 0.9 is 0.94 on the designed D line and 0.16/0.20 on its U/C lines,
   against **0.24** on the holistic D line and 0.13/0.11 on its U/C lines. The holistic D line's lever was gear. Resting drive is **reported per line** (`motor_report.py`), so if the budgeted holistic D
   line turns to throttle, the table shows it.

**Recommended follow-up, not registered here:** once `--effector-bias-sigma` has landed, a four-arm B+F rerun (the
same seeds, budget plus freeze) costs the same as this one. Against B it isolates the throttle lever for both faunas.

## 3. The quantities (fixed in `budget.py`, statistics from RBT-113's `readout.py`)

These are RBT-113's per-seed-directory statistics for the holistic fauna, in **raw yield per generation**: b_div,
b_up, b_down and h2 (`readout.arm_stats`). The scale is RBT-113's **frozen** holistic σ0 = 0.221249 (the D4
reference), so every number is on RBT-113's scale.

**Verdict precedence [S4].** The rules can overlap, and the code tests them in this order:
- Q1: RESPONDS, then NO RESPONSE, then INCONCLUSIVE.
- Q2: LOWERS, then RAISES, then NO CHANGE, then INCONCLUSIVE.

A RESPONDS or a LOWERS/RAISES whose CI lies wholly inside ±0.05 σ0 is printed with "(within the ±0.05 margin)". It
is then a real but negligible effect.

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

## 4. Controls (`budget.py`; any failure VOIDs Q1 and Q2; each is shown passable and shown able to fail; K6 and K7 added [S6])

| | what | passable | can fail |
|---|---|---|---|
| **K1** | each B line's `config.json` equals the O line's plus `motor_budget` 1.77, and nothing else | a tiny O/B pair (`tests/test_rbt120.py::test_budget_readout_controls_pass_on_a_tiny_arm`) | the budget removed from one line's config |
| **K2** | every conventional lineage row of every B line equals the O line's | the tiny pair; `test_designed_body_is_byte_identical_through_a_whole_solo_run_under_the_budget`; **at full size**, `controls/k2_full_population.txt` (`k2_check.py`: line D, seed 5, 3 generations of 40 + 40 on 2 draws, all 120 designed rows identical, holistic rows diverge from generation 0) | one designed fitness altered |
| **K3** | the holistic founders' generation-0 names and body-plan hashes equal the O line's | the tiny pair | one founder's body hash altered |
| **K4** | every holistic `final/` member of every B line, compiled under its run's config, is within 1.77. It also prints the share the budget had to scale. | the tiny pair | the budget broken in `world.py`, and a planted 3.24× body |
| **K5** | RBT-113's per-seed-directory controls and selection checks (`readout.controls`, `selection_checks`) | as in RBT-113 | as in RBT-113 (`tests/test_rbt113.py`) |
| **K6** | the arm's `commit.txt` `rabbitstew_tree` equals the tree the readout runs on, so K4's recompile is the physics the arm ran | the tiny pair (a `commit.txt` written at the test's tree) | a wrong tree in `commit.txt` |
| **K7** | the servo clamp and cap were live: some generation-0 holistic lineage rows of B differ from O's. probe_clamp predicts 7–19 of 40 per seed; the full-size K2 check moved 13 of 40. | the tiny pair (seed 2: 2 of 6 move; seed 1 moves none at 6, so the fixture uses seed 2) | B's generation-0 rows replaced by O's |

`budget.py` also refuses (non-zero exit) a seed directory that is not a registered B directory: a Z name, a seed
outside its arm, or a repeated seed. Q3 carries RBT-117's own refusals and VOID.

## 5. Order at readout

**Every probe on B uses the budget [M3].** Any probe run on `runs/RBT-120/B*` must build its SimConfig from that seed
directory's `config.json`, or import RBT-120's `world.py` first, and must **assert `sim.world.motor_budget == 1.77`**.
- The registered scripts do: `decompose_budgeted.py`, `levers_budgeted.py`, `motor_report.py`, `apportion.py`,
  `budget.py` (K4).
- RBT-113's and RBT-121's probes that `import world` after putting RBT-113's directory on `sys.path` would silently
  compile B bodies unbudgeted. That includes `probe_gear.py`, `probe_work.py`, `probe_food.py`, `phys_ghost.py`,
  `phys_gear.py` and `bias_walk.py`. They run on B only through `levers_budgeted.py`, which caches RBT-120's `world`
  under that name first and asserts it.

See `RUNNER.md` §6: restore; `decompose_budgeted.py` (RBT-113's `decompose.py`, unchanged, run under RBT-120's
`world.py`); `readout.py` (unchanged, `--reference` the frozen σ0; descriptive); `budget.py` (Q1, Q2);
`compare_budgeted.py` (Q3); `motor_report.py` (deliverable 2, with resting drive); then the per-line lever probes
(`DESIGN.md` §7.6: `probe_static.py`, `phys_ghost.py` and `phys_passive.py`, unchanged, through `levers_budgeted.py`
on B). They commit by role.
**The per-line lever report (R8), a registered descriptive deliverable at readout, on both O and B [M2].** It is
mandatory beside Q3, which is a holistic-against-designed result.
- **resting drive**, both faunae (`motor_report.py`; auditor B's statistic);
- **the share of work on contact-free children** and **the share on children at least half inside** their parent,
  holistic (`phys_ghost.py`, #403's metrics);
- Σgear/(4M) and the share capped (`motor_report.py`);
- the cap/clamp apportioning (`apportion.py`, off / cap / cap + clamp) [S6].

**Out of scope, with the reason:**
- **motors-off** (`phys_passive.py`) bears on the spawn/settle allowance (R3);
- **span, footprint and node counts** (`probe_static.py`) bear on coverage and part-count allowances (R4, A4/A5).

None of these is a motor-capacity channel. They are run and committed as extras only.

The O baselines are committed now: `motors_O*.txt`, `levers_*_O.txt`, `apportion_O.txt`. **All levers are
descriptive:** they enter no verdict, but REPORT.md must quote them beside Q1–Q3. A fauna or arm difference that goes
with a lever difference is attributed to the lever until shown otherwise (R8).
- **The rerun measures the cap, not the cone.** Ball joints stay range-less, so a capped D line can still spend its
  budget on free rotors (DESIGN.md §7.5). The ghost metrics show whether it does.

## 6. The power model, bounded by a counterfactual and a ceiling (`power.py` → `power.txt`)

This applies RBT-113's lesson. RBT-117's unbounded Gaussian model predicted d ≈ −2.8, and it failed because neither
body stayed inside its founder scale. Here, **no quantity is an unbounded Gaussian**:
- **Expected responses are RBT-113's observed per-seed O responses scaled by bounded factors.**
  - **Up half:** ρ_up is the ratio of the U line's final U − C net under the budget to the registered value, from
    `counterfactual.txt` (the U line's own final genomes re-scored under the budget). The U lines are mostly within
    the budget already.
  - **Down half:** the D line's final work W is taken in two scenarios [S3].
    - **Counterfactual, W_cf:** the D line's own final genomes re-scored under the budget, a line that found its motors
      unbudgeted and lost them at once. **It is a scenario, not a floor.** A budgeted D line starts at the founders'
      ceiling of 0.22 and must grow its gear about 3× to reach the cap, so it may not reach W_cf in 24 generations. A
      D line that stops eating rather than wasting is also outside the model. ρ_down → 0 is in the sensitivity table.
    - **Ceiling, W_hi:** min(W_O, 0.99 × the budgeted free-spin ceiling at the D line's own mass). The 0.99 is how
      close ghost rotors come to their ceiling (RBT-121 auditor A, A2 and S1). A body at the mass budget has a
      ceiling of 0.977 yield.
    - Food is the O line's. ρ_down = (C_net − D_food + W) / (C − D)_O.
- **Noise is RBT-113's own replicate noise:** one replicate's deviation, drawn with a random sign from (O − Z)/√2 at
  each seed. The salt-0 and salt-1 lines at a seed are independent holistic replicates.
  - **[S2]** "Conservative" is not shown. Once 34% of founders move, B is an independent replicate of O at the same
    founders, and Var(Δ) = 2σ_w² ≤ 2σ².
  - So `power.txt` also gives every table at noise × √2 (the design adversary's bound). **Both are quoted below.**
- **The designed side is fixed.** Its B lines are its O lines (K2).

**Results** (`power.txt`, 2000 simulated reruns per scenario):

The bounds are real, not assumed. Across the 12 O seeds (`counterfactual.txt`), the D line's work under the budget
at its own genomes is 0.56–0.85, against 0.70–2.60 as registered. Its bounded ceiling W_hi is 0.94–0.97, or W_O
where that is lower (seed 1). Every D member re-scored under the budget stays at or below 0.975: the budgeted ceiling,
and no longer 2× the designed body's.

Probabilities are given at noise × 1 / × √2:

| scenario | E b_div_B (raw / σ0; share of O) | Q1 RESPONDS | E Δ (σ0) | Q2 LOWERS | Q2 INCONCLUSIVE |
|---|---|---|---|---|---|
| O as observed (salt 0) | +0.0975 / +0.441 | | | | |
| **counterfactual** (the D line keeps its own budgeted work) | +0.0575 / +0.260; 59% | 1.000 / 0.997 | +0.181 | **0.996 / 0.929** | 0.004 / 0.071 |
| **ceiling**, the likelier (the D line reaches 0.99 × its budgeted ceiling) | +0.0685 / +0.309; 70% | 1.000 / 1.000 | +0.131 | **0.898 / 0.693** | 0.102 / 0.307 |
| **null**, ρ_down = 1 (the budget changes nothing) | +0.441 | 1.000 | 0.000 | 0.025 / 0.025 (RAISES 0.021 / 0.021; NO CHANGE 0.064 / 0.006) | 0.892 / 0.949 |
| ρ_down = 0 (no down response at all) | | 0.957 / 0.793 | +0.292 | 1.000 / 1.000 | |
| no response at all (E b_div_B = 0) | 0 | **0.024 / 0.024** (NO RESPONSE 0.350 / 0.200) | | | |

- **Q2's power is 0.69–0.90 at the ceiling and 0.93–1.00 at the counterfactual [S2].** Its level holds in both noise
  models: a false LOWERS 0.025 and a false RAISES 0.021.
- **The 80% MDE is about 0.10–0.14 σ0 per generation.** With ρ_up = 1 and a uniform ρ_down, LOWERS is:

  | ρ_down | noise × 1 | noise × √2 |
  |---|---|---|
  | 0.8 | 0.44 | 0.28 |
  | 0.7 | 0.73 | 0.47 |
  | 0.6 | 0.90 | 0.66 |
  | 0.5 | 0.98 | 0.83 |
  | 0.4 | 0.996 | 0.92 |

- **Q2's NO CHANGE is nearly unattainable.** The per-seed replicate SD of b_div is 0.108 σ0, so the CI of Δ cannot
  fit inside ±0.05 σ0 at n = 12 (0.064 / 0.006 under the null). **A null result will read INCONCLUSIVE, not NO
  CHANGE.** That is stated now, so that it is not read later as "the budget did nothing".
- **Q1 cannot fail to RESPOND** in any bounded scenario, because the up half is untouched: ρ_up is 0.80–1.24 and the
  U lines are mostly within the budget. **Q1 is estimation.** Its content is the magnitude, with its CI.
- **Q3** (d = holistic − designed final U − D, raw; observed unbudgeted +0.768), at noise × 1 / × √2:

  | scenario | E d | HOLISTIC | DESIGNED | NOT DECIDED | VOID |
  |---|---|---|---|---|---|
  | counterfactual | −0.163 | 0.001 / 0.001 | 0.029 / 0.038 | **0.970 / 0.961** | 0 / 0 |
  | ceiling | +0.094 | 0.015 / 0.022 | 0.001 / 0.002 | **0.985 / 0.976** | 0 / 0 |
  | **null for Q3's reading [S1]**: the budget changes nothing, E d = RBT-117's | +0.769 | **0.961 / 0.835** | 0 / 0 | **0.039 / 0.165** | 0 / 0 |

  - The control is passable: the C-line VOID rate is 0 in every scenario, with the B C line drawn as a new
    replicate.
  - A NOT DECIDED is informative: if the margin survived the budget, NOT DECIDED would come up only 4–16% of the time.

## 7. The prediction, both ways

**Q1: RESPONDS**, with b_div_B = +0.058 to +0.069 raw per generation (+0.26 to +0.31 frozen σ0). That is **59–70% of
the unbudgeted O lines' +0.0975, and nearer 70%**, since the ceiling scenario is the likelier. The up half is
essentially unchanged, and the down half falls to about a third to a half.

**Q2: THE BUDGET LOWERS THE HOLISTIC RESPONSE**, by +0.13 to +0.18 σ0 per generation (30–41% of the O lines'). The
drop is in b_down, not b_up. The power is 0.69–0.90 at the likelier ceiling, so an INCONCLUSIVE here is a real
possibility (0.10–0.31) and is not "the budget did nothing".

**Q3: NOT DECIDED** (d between −0.16 and +0.09). This agrees with the readout adversary's work-capped d = −0.02.

**What each outcome would mean, fixed now:**

- **Q2 LOWERS, within the predicted range.** The motor budget removed about a third of RBT-113's holistic response.
  - The budgeted b_div becomes the holistic benchmark number **without the gear allowance and the servo wind-up**
    [M2]. It is not "without the lever": the Effector-bias walk and free rotors remain on both faunae.
  - RBT-113's number must be quoted beside it, and so must `apportion_*.txt`'s split between cap and clamp.
- **Q2 LOWERS by more than predicted** (the budgeted response below the counterfactual, under 59%). The D line under
  the budget finds waste more slowly than a line that grew its motors first and lost them. The allowance also sped up
  the response, not only its size.
- **Q2 INCONCLUSIVE, or LOWERS by less than the ceiling scenario** (above 70%). The D line reaches its budgeted
  ceiling and wastes as much as the budget allows, through the channels left open. **Which channel is read from the
  lever report, not assumed [M2]:**
  - **free rotors** (A2) if the contact-free work share of the B D line stays near O's 0.96, and **A2's cone is the
    next fix**;
  - **the bias walk** if the holistic D line's resting drive rises well above O's 0.24 (towards the designed D line's
    0.94), and **`--effector-bias-sigma` is the next fix**;
  - both, if both move.

  This is not "the budget did nothing": NO CHANGE is nearly unattainable at this n (§6).
- **Q2 RAISES.** Not predicted in any bounded scenario (false rate 0.021). The budget would have pushed selection into
  a more effective channel, and that would need a probe before anything else is read.
- **Q1 INCONCLUSIVE or NO RESPONSE.** Not predicted (the up half is untouched). It would mean the U line's coverage
  gain (RBT-113 §4) also depended on motor capacity above the budget. Only 17% of U members are over the budget
  today (`motors_O_at_1.77.txt`), so that would be a surprise and a finding.
- **Q3 NOT DECIDED.** RBT-117's HOLISTIC RESPONDS MORE does not survive the budget, as the caveat says. If the margin
  had survived, this outcome would occur only 4–16% of the time (§6, [S1]). Reason (a)'s perverse form is closed for
  motor capacity. It is not closed for resting throttle or free rotors.
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
- **Readout:** restore (minutes); `decompose_budgeted.py` on 12 directories (about 25 min on 4 cores; RBT-113 took
  about 45 min for 24); `readout.py`, `budget.py`, `compare_budgeted.py` and `motor_report.py` (minutes); the lever
  probes and `apportion.py` (about 10 min).
- **Launch discipline [S5]:** `controls/prelaunch.txt` is no longer committed. Each runner must generate it with
  `prelaunch.sh` on its own machine before `run_arm.sh` will launch.
- **Total: about 3 h from launch to a readout PR.**

## 9. What the adversary should attack first

1. **K2's claim** that the designed lines re-run byte for byte. It is proved on a tiny solo run and on 3 generations at full size (`controls/k2_full_population.txt`), not on a full 24-generation O arm.
2. **The power model's bounds:** whether the counterfactual floor is really a floor, and whether 0.99 × ceiling is
   really a ceiling.
3. **Whether Q2's pairing** (same founders, independent trajectories) makes the sign-flip test valid.
4. **Whether the servo clamp under the budget** changes the holistic founders more than the ticket intended.
5. **What the budget leaves open:** ghost rotors (A2; the cone is out of scope, §5), resting throttle (§2.1), and
   the coverage lever of the up line (RBT-113 §4).
6. **§2.1's choice** to register the gear budget without the Effector-bias freeze.
