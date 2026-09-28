# RBT-124 FIX-CHECK: #420 @ a5c9014 against the design adversary's #423

**Design adversary, 2026-09-28.** This re-checks the ruled fixes: M1–M3, S1–S8, and M2 ruled for option 1, the
ball-mounted steerable wheel. The fixes are on #420 at `a5c9014` (4145049, d5117b0, and a merge of 7a22d90). The
probes are in `fixcheck/`, each with its output beside it. They run on `a5c9014` against restored RBT-113 O1
(216/216), and none of them writes into any run.

## Verdict: **MERGE AFTER FIXES**

The fixes are small. No further adversary round is needed once F1 lands.

**Every item is fixed as ruled:**
- M1–M3 hold.
- S1–S8 are applied, S5 included.
- Everything is byte-identical when off, including against integration's new head.
- The trial merge's suite passes.

**M2's wheel is fair by construction (R6).** It cannot carry a rotor, and it is exactly what the ruling asked for.

**One thing it does reopen, which no text yet says (F1):**
- With round children, A's own embedded-rotor test fails the ticket's bar under the ranges alone: **0.338** of the
  unfixed work against a bar of ≤ 0.1.
- The D fixture keeps half of its contact-free work.
- Only RBT-120's motor budget brings the rotor test back under the bar (0.019).
- So under M2, **R2 is closed only together with R1**. The pack's ranges must be registered with the budget, and a
  test and a warning should say so.

| # | | item |
|---|---|---|
| F1 | MUST (small) | Under M2, register the ranges **only with `--motor-budget`**, and say so in DESIGN §1.2/§8. Add the round-child S1 test (ranges + budget 1.77 ≤ 0.1 of unfixed work; ranges alone is 0.34), and make the CLI warn when `--ball-cone` is set without `--motor-budget` |
| F2 | note | The coordinator's "D fixture 183 J" is the first draft's figure. Under M2 the fixture reads 16,210 J, of which 16,092 J is its ball wheels' spin and 15,923 J is airborne. That is S1's residual, correctly booked; the test excludes wheel work from its ≥ 90% criterion, as it should |

---

## M1: the leaf rule (`fc_launder.py` → `fc_launder.txt`)

**In place.**
- `is_wheel(part, leaf)`, with `leaf_parts` computed in `build_xml` only when a range flag is set.
- The first review's propellers now fall to **0.006 (blade fixed), 0.008 (blade on a ball) and 0.007 (sphere
  propeller)**.
- The bladed hinge hub keeps only its nine bladeless leaf wheels (135 kJ, 94.5 kJ of it contact-free, which is S1's
  residual).
- **The Pioneer is bit-identical:** 27,662 J off, on, and under the budget.

## M2: the ball-mounted steerable wheel

### Structure, and byte-identity when off

- **DOF and actuator counts are right** (`fc_launder.txt`, nv and nu off/on):
  - a ball wheel adds exactly one DOF, the spin hinge (bw-air: 9 → 10; the 12-wheel hub: 42 → 54);
  - the actuator count is unchanged (3 → 3, 36 → 36);
  - a non-leaf round part adds nothing (bw-blade: 9/9);
  - box children add nothing (hub12-box-emb: 42/42);
  - the twist DOF's motor drives the spin, and dofs 1–2 steer the coned ball.
- The parent filter is restored by explicit `<exclude>`s against the parent's weld group. That is what MuJoCo's
  `filterparent` filtered before, now that a massless mount body sits between them. The `<contact>` element is
  written only when a ball wheel exists.
- **Off, the MJCF is byte-identical, body by body** (`fc_identity.py`). All 960 holistic and designed bodies of
  RBT-113 O1, 200 random holistic genotypes and 10 Pioneers hash identically on integration `d4c4c73` and on
  `a5c9014`.

### Can it launder a rotor? (`fc_launder.txt`)

Everything below is at full throttle, with ranges π/2, off → on:

| body | work off (J) | work on (J) | on/off | + budget 1.77 (J) | budget/off |
|---|---|---|---|---|---|
| bw-blade: sphere on a ball carrying a FIXED blade | 45,290 | 204 | **0.004** | | |
| bw-air: sphere on a ball, leaf, in the air (S1's residual) | 47,280 | 16,180 | 0.342 | | |
| bw-heavy: large cylinder on a ball, leaf, in the air | 17,617 | 8,538 | 0.485 | 8,538 | 0.485 |
| **hub12-bw-emb**: A's S1 hub, 12 **sphere** children embedded (0, π/2, 0) | 549,986 | **185,918** | **0.338** | 10,421 | **0.019** |
| hub12-bw-out: the same, oriented outward | 549,779 | 186,303 | 0.339 | 11,150 | 0.020 |
| hub12-box-emb: A's S1 as registered (box children) | 549,268 | 3,007 | 0.005 | 224 | 0.000 |
| Pioneer (rng 0) | 27,662 | 27,662 | 1.000 | 27,662 | 1.000 |

- **The leaf rule holds.** A ball wheel carrying anything is coned: bw-blade falls to 0.004. A round part cannot
  carry an off-axis mass without a child; its geom's centre lies on the spin axis by construction.
- **What is left is the airborne wheel (S1).** A spinning round leaf dissipates its motor's free-spin power in joint
  damping, whether or not it touches anything.
  - One ball wheel in the air burns 16 kJ a season, the same as a hinge wheel.
  - Twelve on A's hub burn **186 kJ, 0.338 of the unfixed rotor, embedded or outward alike**.
  - The ticket's test ("A's spinning embedded-rotor genotype burns at most 0.1 of its unfixed work") therefore
    **passes only because A's children are boxes**. Round children fail it under the ranges alone.
  - Round leaves on ball joints are the commonest round part the holistic encoding builds: 371 in 480 bodies.
- **The budget closes it.** Under RBT-120's budget (1.77) the round-child hub falls to **0.019–0.020**, because the
  budget caps Σgear per body, and so caps the free-spin power however many wheels a body carries.
  - The Pioneer is inside the budget and unchanged.
  - bw-heavy is inside it too (0.485 with or without). That is one wheel at its own gear, which is the Pioneer's
    allowance per wheel.
- **Hence F1.** Under M2, R2's "no free rotor" is kept only in combination with R1. The first draft's pack closed
  free rotors on its own (hub 0.005). The ruled parity wheel gives back the airborne share, and only the budget
  bounds it. That is a sound trade under R6, but it must be registered as a pair:
  - `--ball-cone` without `--motor-budget` should warn, as a lone range flag already does;
  - a test should pin the round-child hub under ranges + budget.

### Fairness (R6)

- **By construction, yes.** Both faunas now have a wheel their encoding actually builds: the Pioneer's leaf
  cylinders on x hinges, and the holistic fauna's round leaves on ball joints. The same leaf rule binds both, and
  both burn the same airborne residual per wheel.
- The ball wheel is if anything the richer wheel (steerable within the cone). But it is the ball joint's own twist
  DOF re-expressed, so it grants no DOF or actuator the genotype did not already carry.

### The U line's food, on my own draws (`fc_lines.py` → `fc_lines.txt`)

All 120 holistic U finals and all 120 D finals of RBT-113 O1 (seeds 1–3), on all four registered draws, one plain
season each. No season exploded under any variant.

| variant | U food / season (4 draws) | U, draw 1131 | U work (J) | D food | D work (J) |
|---|---|---|---|---|---|
| off | **1.18** | 0.60 | 7,337 | 0.09 | 50,664 |
| ranges (M1 + M2) | **0.34** | 0.29 | 1,943 | 0.09 | 12,981 |
| pack (ranges + settle 0.01) | **0.38** | 0.15 | 1,987 | 0.02 | 12,987 |
| ranges, ball wheels **without** the leaf rule | 0.33 | 0.23 | 1,963 | 0.09 | 13,344 |
| ranges + motor budget 1.77 | 0.37 | 0.22 | 1,883 | 0.06 | 6,544 |

- **The designer's figure is borne out in direction but is sample-dependent in size.** They report 0.98 → 0.14
  (ranges) → 0.22 (pack) on their rng-124 sample: 5 per directory over O1 and Z1, 14–22% kept. On all 120 O1 U finals
  I get 1.18 → 0.34 → 0.38 (29–32% kept). On draw 1131 alone (0.60 → 0.29) it matches their draw-0 reading (0.33) to
  within one member's items. Registration should quote a range of 0.14–0.34, not one number.
- **The remaining drop is the loophole closing, not an unfairness left in the rule.** Each of the rule's other
  moving parts can be taken out without recovering the food:
  - **dropping the leaf rule** (every round part on a ball joint spins, children and all) recovers nothing: 0.33
    against 0.34;
  - **adding the budget** costs nothing: 0.37;
  - so the lost food is on what the cone binds that no wheel rule touches, i.e. **non-round limbs on ball joints
    swinging past π/2**. In the first review's `wheels.txt` split, that is the U line's "ball, limb" work (32% off).
- Such a whirl is the open-loop gait that `../walker.txt` shows reaching the maximum angle π: a free rotation that no
  real joint of this kind allows. An honest stride within ±1.3 rad is bit-identical under π/2 (`../walker.txt`). The
  designed body has no such DOF to lose. **No residual unfairness is visible at this n.**
- **The D line** keeps 12.98 kJ of its 50.7 kJ (26%) under the ranges; the designer reports 26% (44.7 → 11.8 kJ).
  The budget halves that to 6.5 kJ. Almost all of the rest is airborne ball-wheel spin (S1 and F1).

## M3: the lever report reads each run's physics (`fc_levers_config.py` → `fc_levers_config.txt`)

**Fixed.**
- On the RBT-113 D fixture under a pack `config.json`, the report with no flags now equals the report with the flags
  repeated.
- It prints the physics it used: `physics used: motor_budget 0, ball_cone 1.5708, hinge_range 1.5708,
  settle_until_rest 0.01 (settle_max 10)`.
- **F2:** the figure is **16,210 J, not 183 J**. 183 J was the first draft's fixture reading. Under M2, 16,092 J of
  it is the fixture's ball wheels' spin, and 15,923 J of that is airborne. The report books it in `wheel J` and
  `wh.free`, as S1 asked.

## The SHOULD items

All eight are applied, per DESIGN's amendment table, checked in the code:
- **S1:** the `wheel J` and `wh.free` columns.
- **S2:** `check_ranges` refuses a cone outside (0, π) or a range ≤ 0, and `Simulation` refuses a negative ε or
  `settle_max` < `settle_time`. A lone range flag warns.
- **S3:** the help text describes kinetic damping.
- **S4:** solo-only scope, §3.2.
- **S5:** registered as a side effect in DESIGN §3.3. Before a locomotion or foraging reading under the pack, either
  fix 12 is in or `pen>1cm` is printed per line.
- **S6:** `--draw` repeats and pools.
- **S7:** "ctrl 0" is documented in the `levers` docstring and header.
- **S8:** exploded seasons are counted apart (`expl`) and kept out of the work, food and share means.

## Composition with integration's head

Trial merge of `a5c9014` + integration `d4c4c73` (RBT-130's sweep hooks, RBT-120 B2, RBT-129 r4):
- **Merge:** clean, with no conflicts.
- **`combo.py`** (the first review's; `fixcheck/combo_base2.txt`, `fixcheck/combo_trial2.txt`):
  - default `config.json` (bare `evolve`, and RBT-113's foraging line) is identical to integration's, bare and with
    every flag passed explicitly off;
  - RBT-113's golden digests match with every flag passed explicitly off (RBT-120, RBT-124 and RBT-125);
  - the Pioneer's MJCF is identical under cone + range + budget 1.77;
  - with every flag on at once, the config round-trips and a Pioneer season runs.
- **Full suite** in a clean `.[dev]` venv (Python 3.11.15, mujoco 3.14.0, numpy 2.4.6, no scipy): **596 passed** (7 min 31 s; its 15 warnings are RBT-126's intended breed-rule screen warnings).

## Files (`fixcheck/`)

| probe | output | question |
|---|---|---|
| `fc_launder.py` | `fc_launder.txt` | M1 and M2: laundering through hinge and ball wheels; DOF and actuator counts; the budget |
| `fc_lines.py` | `fc_lines.txt` | M2: the U line's food and the D line's work, 120 bodies × 4 draws; the leaf rule's cost; the budget |
| `fc_identity.py` | `fc_identity.txt` | M2: the MJCF off, body by body, integration vs `a5c9014` |
| `fc_levers_config.py` | `fc_levers_config.txt` | M3 |
| `../combo.py` | `combo_base2.txt`, `combo_trial2.txt` | composition with integration `d4c4c73` |
