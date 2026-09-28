# RBT-116 `steer.py` FINAL check: PR #434 @ `3b23095`, trial-merged on integration `716e2d3`

**Verdict: MERGE.** FC-M1 and FC-M2 are closed, and every item below passes. No new MUST.

*Seasons ran only on the PR's fixture worlds and test batteries. No RBT-116 arm, gate cell or W1 pool draw was run.
Probes are under `runs/RBT-116/design-adversary/`.*

## The six checks

| # | check | result | evidence |
|---|---|---|---|
| 1 | Amendment 3's rule is fixture-only and pre-data, and the registered builds read STEERS on a majority of fixture variants at τ = 1 under root + surface | **PASS** | The rule (3 fixture variants, majority of 2 of 3) is committed in `a784bdf` (03:44), before its result in `90859f5` (03:59), and cites no gate or W1 output. **Independent reproduction** (`g8f_rule_repro.txt`): (32, +16) 2/3; (32, +64) 3/3; (128, +2) 3/3; (128, +16) 2/3. This is exactly the PR's table. F2, W1's eating block (root + surface + #446 guard), reads STEERS on all four. The one-side grid (A) is struck, correctly: 0 of 12 steer on any variant. |
| 2 | Not a call-logic defect: the confirmation battery is independent and correctly seeded, and an unscreened test battery explains the F drop | **PASS, agreed** | `confirm_probe.txt`: **(b)** swapping stage 2 and the confirmation moves the low F with the *draws* (w 4: F +1.50 on the old confirmation draws wherever they sit; w 2: the two F values swap exactly). **(c)** The confirmation draws computed alone give byte-equal F and bound, so there is no state leak between seasons. **(d)** The confirmation draws are poorer for this plant (intact food 7.69 against 9.56 for w 4; lesioned 0.44 against 0.94; a sensorless mover 0.94 against 1.19). **(e)** The draws are disjoint, and θ is keyed on the start seed alone. So the drop is draw variance on an unscreened battery; at the gate the draw screen admits only reachable draws. It does bear on real steerers, as a confirmed sensitivity below 1, which is exactly what G8(f) and R5-1 measure, not a defect. |
| 3 | W1's block matches RBT-129's eating rule and clearance exactly | **PASS** | `steer.REGISTERED_POINTS["W1"]` = {eat_from root, eat_rule surface, clear_from root, eat_radius 0.35, smell_contrast 2.5, smell_tau 1.0}. RBT-129's `blocks.EAT_RULED` is `("--eat-from", "root", "--eat-rule", "surface")`, and its clearance is #446's minimal guard (READINESS 4c/4d). PREREGISTRATION L519 and L833 state the same, struck through where changed. `world_clearance` reads `_clearance_points()`'s `(_SURFACE_CLEAR, centres, geoms, min_surface)` tuple exactly as `Simulation._food_spot` does, plus the eating guard. NIT below. |
| 4 | A θ refusal is excluded, counted and reported, never fatal, and the 14–16% fixture now gets a call | **PASS** | `refusal_call.txt`: on the fixture that refused before (clear_from geoms + surface), the call completes with **θ refused 5/36** (a rate of 0.139) in the record and in `steer.txt`'s row. The two-nose steerer is STEERS and the G8(f) build PASS-UNCONFIRMED; nothing raises. Under W1's block, 0/36 are refused. `MIN_USABLE = 2` covers a stage left with too few draws. |
| 5 | Power and the priors under root + surface still reproduce r7's 0.847 / 0.793 | **PASS** | `power.py` on the trial merge regenerates `power_tau1.txt` **byte-identically**, and that file equals r7's `power.txt` (0.847 at K; 0.873 at K / **0.793** headlined). `prior_surface_probe.txt`: the centre-rule reference reproduces my r5 priors (0.48 / 0.32). Under surface reach, min(SENS_C) is 0.32 at the Pioneer chassis and 0.40 at h 0.35. Never below r7's 0.32, so the registered power does not fall. |
| 6 | Full suite in a clean venv on the trial merge with integration `716e2d3` or later | **PASS** | Fresh venv, `pip install -e .[dev]`, `import scipy` fails. The merge of `origin/results/RBT-116-steer` (`3b23095`) into `716e2d3` is clean (`21e1b87`). **701 passed, 1 skipped**, 16 warnings (RBT-126 breed-rule UserWarnings), 644 s. The skip is `test_rbt125_harness`'s optional scipy cross-check (`pytest.importorskip("scipy.stats")`), as expected without scipy. |

## NIT

- **The world's fallback against the decoy's exclusion.** After 256 failed placements, `_food_spot` uses the last
  candidate anyway and counts it in `food_fallbacks`. So a real item can, rarely, sit inside the clearance, while
  the decoy's θ re-draw never accepts one. At W1's parameters neither happens (0 refusals in 612 draws; fallbacks are
  RBT-125's counter). Print `food_fallbacks` beside the θ-refusal count in `steer.txt`, so that both sides of the
  rule are visible.
- **The rule's F1 is the tightest variant.** (32, +16) and (128, +16) are PASS-UNCONFIRMED there, which is the
  item-2 draw effect. The majority rule handles it as registered. Nothing to change.

## Files

| file | what |
|---|---|
| `g8f_rule_repro.py` / `.txt` | independent reproduction of Amendment 3's 4 registered builds on F1–F3 |
| `confirm_probe.py` / `.txt` | the confirmation-drop diagnosis: swap, isolation, draw quality, seeding |
| `refusal_call.py` / `.txt` | the formerly refusing fixture and W1's block, full calls |
