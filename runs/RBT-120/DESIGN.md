# RBT-120 design: budget motor capacity

**Designer, 2026-09-27.** This file covers deliverables 1 and 2: the flag and the reporting utility.
The rerun's registration is `PREREGISTRATION.md`.

**Nothing here changes a committed result.**
- The flag is off by default. When off, it is byte-identical and absent from `config.json`.
- Nothing merges into a scored path without a design adversary and the coordinator's ruling.

## 1. The problem, in one paragraph

`world.py` gives each driven DOF a gear of `motor_strength` (4) × the **heavier** of the two masses its joint connects.
A ball joint carries up to three such motors. The mass budget (15.34 kg) caps mass, not gear.

A heavy part therefore counts its mass once per driven DOF of each of its children. **Σgear is unbounded in
branching:** RBT-121 auditor A's 12-child star hub reaches Σgear/(4M) = 30 and burns 16.5 yield per season.

Under RBT-113's down-selection, the holistic D line took about 10× more Σgear than its founders, and its free-spin
work ceiling reached about 2× the designed body's. That was **all of RBT-117's margin**: capped, d = −0.02
(p 0.86).

**A note on the ticket's "Σgear/mass = 1.76"** (auditor A made the same point). The figure is
**Σgear / (motor_strength × mass)**. For the Pioneer:
- each of its 2 driven wheels is keyed to the 13.5 kg chassis;
- so Σgear = 2 × 4 × 13.5 = 108 N·m and M = 15.3367 kg, giving **108 / (4 × 15.3367) = 1.7605** exactly;
- its raw Σgear/mass is 7.04.

Every ratio below is in these units. `rabbitstew.motors` calls it `gear/(ms*mass)`.

## 2. The options (`options.py` → `options.txt`)

Each rule was applied by arithmetic to every member of RBT-113's 12 restored O seed directories (founders, and the
U/D/C lines' generation 23, both faunas) and to the Pioneer. Values are Σgear/(4M) over **every** driven DOF, all motor
modes: per-directory means, then the mean [min, max] over directories. The star-hub column is auditor A's
`probe_static` / `probe_synthetic`.

| rule | Pioneer | holistic founders | holistic U | **holistic D** | holistic C | 12-child star | verdict |
|---|---|---|---|---|---|---|---|
| today: ms × max(child, parent) per DOF | **1.76** | 0.63 | 1.17 | **3.72** [1.62, 5.29] | 0.40 | 30.3 | the allowance |
| (2) key to the **child's** mass | **0.06** | 0.18 | 0.58 | 0.25 | 0.11 | 0.47 | **rejected** |
| (3) one gear per joint, **shared** across a ball joint's DOFs | 1.76 | 0.55 | 0.68 | 1.51 [0.86, **1.98**] | 0.35 | **10.1** | not a budget |
| (1) **cap Σgear ≤ c × ms × M**, c = 1.77, scaled uniformly when over | **1.76, untouched** | 0.62 | 1.11 | **1.69** [1.48, 1.77] | 0.38 | **1.77** | **recommended** |
| (4) budget power, gear²/damping | the same rule as (1) | | | | | | subsumed |

**(2) Child-mass keying: rejected.**
- The Pioneer's wheels weigh 0.46 kg, so it would lose 97% of its motor, a 29× cut. That changes its behaviour and
  every committed designed-body result.
- Re-scaling `motor_strength` to compensate would pay heavy *children* instead of heavy hubs, which is a different
  lever of the same kind.
- It fails the ticket's hard requirement.

**(3) A per-joint budget shared across a ball joint's DOFs: not a budget.**
- It removes the ×3 of a ball joint and leaves the Pioneer (hinges only) untouched.
- But it caps nothing a body can add. A hub's mass is still counted once per driven child. The star hub still reaches
  10×, and the D lines already reach 1.98, above the Pioneer.
- It bounds capacity per joint, not per kilogram, and the mass budget is per kilogram.

**(4) A power budget is (1) under the damping rule.**
- A driven joint's damping is `joint_damping × gear` (`world.py:206`). So a torque motor's no-load speed is
  gear/damping = 1/joint_damping = 20 rad/s for every motor.
- Its full-throttle free-spin power is gear²/damping = 20 × gear.
- **Power is proportional to gear, so budgeting power is budgeting Σgear** with another constant.
- Prefer (1): it is stated in the quantity `world.py` sets, and it does not depend on the damping rule staying as it
  is.
- With (1) as implemented, damping scales with the gear. So the power budget holds too: the free-spin ceiling per
  kilogram is capped at the Pioneer's × 1.77/1.7605.

**(1) The Σgear cap: recommended.**
- It is one dimensionless constant, blind to topology. Branching, ball joints, recessive nodes (auditor A's A4) and
  servos all count against the same total.
- It is the mass-equalisation precedent carried over one quantity.
  - The follow-up paper's mass budget **scales every part's mass down** when a body is over it, keeping geometry.
  - The motor budget **scales every driven gear down by one factor** when Σgear is over it, keeping the body plan and
    the proportions between its motors.
- Nothing is rejected or clamped per joint, so no genome becomes unbuildable and no mutation becomes lethal.

## 3. The recommendation, exactly as implemented

`WorldConfig.motor_budget: float = 0.0`; the CLI flag `--motor-budget C` on `evolve`, `ecology` and `simulate`.
0 means off.

**When C > 0, for each robot** (`world.motor_scale`, applied in `build_xml`):
1. Σgear is the sum over driven DOFs of `motor_strength × max(child mass, parent mass)`: today's rule, after the mass
   budget has scaled the masses.
2. The cap is `C × motor_strength × M`, where M is the robot's own total mass after the mass budget.
3. If Σgear exceeds the cap, **every driven gear is multiplied by cap/Σgear**, and so is each driven joint's damping,
   which is keyed to its gear.
   - Each motor keeps its no-load speed of 20 rad/s. Its torque and its power both fall by the factor.
   - Passive joints are untouched.
4. **Every servo's force is clamped to ±its gear** (`forcerange`). Torque motors are bounded by gear already, since
   ctrl lies in [−1, 1].
   - This comes from auditor A's B1: a position servo on an unlimited hinge winds up, because its bias −kp·q grows with
     q, and a back-driven velocity servo reaches 2 × gear.
   - Without the clamp, the budget's "Σ peak force ≤ C × ms × M" would be false for servos. That would be the next
     lever for a down line.

**C = 1.77.** It is the Pioneer's 1.7605 rounded **up** to two places, exactly as the mass budget rounds its
15.3367 kg up to 15.34.
- **The Pioneer is inside the budget, at 99.5% of it,** and is never scaled.
- A holistic body at the mass budget and exactly at the cap has Σgear = 1.77 × 4 × 15.34 = 108.6 N·m and a free-spin
  ceiling of 0.977 yield per season, against the Pioneer's 108 N·m and 0.972. **This is a matched motor class.**
- The cap is on the robot's **own** mass, not on the mass budget. The rule stays "motor per kilogram", as `world.py`
  means it, and a light body does not get a heavy body's motors.

**Why not a tighter or looser C.**
- Any C < 1.7605 scales the Pioneer and changes every designed-body result. The tests show that C = 1.7 moves it.
- A C well above 1.76 would leave a motor-class mismatch in the holistic body's favour.
- 1.77 is the smallest round value that leaves the Pioneer byte-identical.

### Compatibility: proved in `tests/test_rbt120.py` (24 tests)

| claim | proof |
|---|---|
| **off is byte-identical** | RBT-113's two tiny `evolve` runs, a competitive one and a solo foraging one, with `--motor-budget 0` write the `config.json`, `lineage.jsonl`, `history.json` and `state.json` whose sha256 values were recorded before RBT-113's hook (`test_rbt113.GOLDEN`). `motor_budget` is absent from `config.json` when off (`SimConfig.to_dict`, `EvolutionConfig.to_dict`). Forty random bodies' MJCF are unchanged. The **whole suite passes unchanged**, including every other golden (RBT-96 salt 0, RBT-104, RBT-112, RBT-113 and the ecology goldens). |
| **on, the Pioneer is byte-identical** | At C = 1.77 and at C = 2.0: (a) its MJCF string is identical; (b) a simulated bout's final qpos bytes and its work are identical; (c) **every conventional lineage row of a whole solo foraging `evolve` run (RBT-113's run B) is identical**, while the holistic rows are not. |
| **the checks can fail** | At C = 1.7, (a), (b) and (c) all differ. |
| **over budget** | A body at 3.24× (`random_genotype(66)`) is scaled by one factor to exactly 1.77. Each torque motor's gear/damping is unchanged, its power falls by the factor, and masses and geoms are unchanged. Across 60 random bodies, none exceeds 1.77 or the Pioneer's free-spin ceiling per kg × 1.77/1.7605. |
| **auditor A's tests** | The 12-child star goes from 30× and 16.7 yield to ≤ 1.77 and ≤ 0.98 yield. Position and velocity servos are clamped to ±gear only under the budget: off, the MJCF has no clamp, and on, the force never exceeds gear over a season. |
| **config** | The flag reaches `SimConfig.world` from `evolve`, `ecology` and `simulate`, and round-trips through `config.json`. A negative C is refused. |

**Suite:** 422 passed in a clean `.[dev]` venv with no scipy (mujoco 3.14.0, numpy 2.4.6, x86_64). That is 398 before
this change, plus 24 new tests.

## 4. The reporting utility (deliverable 2)

`rabbitstew/motors.py` measures the **compiled** MuJoCo model, so it reports what the physics sees, budget included.
- **`capacity(genotype, sim)`, per body:**
  - Σgear over every driven DOF and every motor mode (each mode's peak force is its gear), and the torque motors'
    share;
  - mass;
  - **Σgear/(ms × mass)**;
  - the ball-joint share;
  - the **free-spin work ceiling** of the torque motors per bout, in J and in yield (Σ gear²/damping × duration ×
    work_cost);
  - the ratio before any budget, and the factor the budget applied.
- **`summarise` and `report`, per line:** a table.
  `python -m rabbitstew.motors NAME=DIR ...` prints it for any directories of genomes, taking the config from the run's
  `config.json`. `--motor-budget C` reports "as if under C".
- **`runs/RBT-120/motor_report.py SEED_DIR ...`, the RBT-113-shaped table:** founders plus U/D/C, both faunas. Its
  torque-only columns reproduce the readout adversary's `probe_gear.py` exactly on the same 12 directories
  (`probe_gear_O.txt`), and it adds all-mode Σgear and the share
  over budget.
  - `motors_O.txt` is RBT-113's O arms as run.
  - `motors_O_at_1.77.txt` is the same lines as if budgeted.

**Proposed standing rule for the coordinator's synthesis:** every holistic-against-designed readout prints this table
per line beside its verdict, with or without the budget.

## 5. What auditor A found (RBT-121, #396), and what I took from it

Auditor A's PR landed at 20:35, while this was being built. I read `runs/RBT-121/physics/AUDIT.md` in full.

**Taken:**
1. **A1 is this ticket.** Auditor A reached the same rule independently: a cap at c = 1.77, rescaled uniformly,
   damping scaled with the gear, servos capped too. It rejected child keying (29×) and found that per-joint sharing
   leaves the star hub at 10×. The two analyses agree; §2's table is on 12 directories, auditor A's on 6.
2. **B1, servo force not bounded by gear.** This is folded into the budget (§3, point 4). Without it, "the budget
   bounds peak force" would be false. The Pioneer has torque motors only, so it is still byte-identical.
3. **Auditor A's cheap tests 1 and 2** are in `tests/test_rbt120.py`: the Pioneer's MJCF identical at 1.77, and the
   12-child star at ≤ 1.77 and ≤ 0.98 yield.
   - Test 3 (an RBT-113 D member's work falls to at most the designed D line's, about 0.93 yield) needs restored
     arms, so it is in `counterfactual.txt` instead: every O D line's members re-scored under the budget.
     - The D lines' mean work falls from 1.58 to 0.70 yield.
     - The heaviest member burns 0.975, which is within the budgeted ceiling (0.977 at 15.34 kg) but slightly above
       the designed D line's mean of 0.926. The budget bounds capacity, not use.
4. **A2, ghost limbs, bears on what the budget leaves.** 83% of the D line's work is done by children spinning inside
   their parents, unobstructed, and such a rotor burns 99% of its free-spin ceiling.
   - The budget bounds the ceiling. A2 decides how much of it a line can cash as waste.
   - So the rerun's power model takes 0.99 of the budgeted ceiling as the D line's upper bound (`power.py`; the
     designed D line reaches 0.95).
   - A2's own fix (an outward-limb clamp and a ball-joint cone) is **not** a budget, and it is not in this PR.
5. **A4, recessive nodes raise the part cap.** This is irrelevant under the cap: extra motors from extra parts count
   against the same Σgear. Noted, not needed.

**Not taken, as out of scope for a capacity budget; they go to the synthesis's fix list:**
- A2's clamp;
- A3, settle-until-rest, and a motors-off season in readouts;
- A5, the eating geometry;
- B9, soft contacts;
- the reachable-node cap.

### RBT-120 item 5: other capacities the mass budget does not cover

- **Sensor count.** Auditor A's B6: every geom can carry a smell sensor. It is unbudgeted, but it does not pay today
  (blind ≈ decoy ≈ intact).
- **Joint limits.** A2: ball joints have no range and hinges are unlimited 20% of the time. This is what makes ghost
  rotors possible.
- **Damping.** Driven damping is keyed to gear, so it is budgeted with it here. Passive joints are unbilled (B3).
- **Servo force.** B1, now closed under the budget.

None of these is a *capacity* the budget should hold; they belong to the synthesis's rules.

## 6. Limits of the budget

- **It equalises capacity per kilogram, not how capacity is used.** A holistic body can put its whole budget into one
  joint.
- **It does not remove ghost rotors (A2).** A budgeted down line can still burn close to 100% of its ceiling. Its
  ceiling is now the Pioneer's per kilogram.
- **Gear is measured before the mass budget's rounding of the MJCF.** Gears are written to 6 significant figures, so a
  capped body's compiled ratio can read 1.770002. The tests allow 1e-5 relative.
- **What it changes.** It moves holistic founders that are over the budget: 6% of RBT-113's holistic founders
  (`motors_O_at_1.77.txt`). So a budgeted run's holistic lines are not byte-comparable with an unbudgeted run's, even at
  generation 0. The rerun pairs them by seed and founder genome, not by fitness.
