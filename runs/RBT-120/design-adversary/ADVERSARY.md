# RBT-120 design adversary: PR #409 @ 0ce78e1, re-reviewed at 7d9782b

## 0. Re-review at head 7d9782b (the current head; this section governs)

**Verdict at 7d9782b: still LAUNCH AFTER FIXES.** Only **MUST 1** is still open. It is two sentences of wording plus one
relabel. The launch tree is now `8229e8d` (the new `motors.py`).

**What changed between 0ce78e1 and 7d9782b:**
- `rabbitstew/motors.py` adds a resting-drive column, which is reporting only. There is **no diff** in `world.py`,
  `cli.py`, `simulation.py`, `evolution.py`, `budget.py`, `power.py`, `run_arm.sh`, `world.py` (RBT-120) or
  `decompose_budgeted.py` (`git diff --stat` is empty). So every physics and scoring finding in §1 carries over unchanged, and
  so do the 8 of 8 mutants (the tests they break are unchanged).
- The suite at 7d9782b: **422 passed** (234 s, same venv).
- `controls/prelaunch.txt` reads tree `8229e8d`, which **equals** `git rev-parse 7d9782b:rabbitstew`.

**Each finding at 7d9782b:**

| finding (§ below) | status at 7d9782b | evidence |
|---|---|---|
| §1 code: correct | **holds** | See above: the physics files are byte-unchanged. |
| **MUST 1**: the clamp moves 132 of the 163 changed founders; "about 6%" is wrong; Q2 is cap + clamp | **OPEN** | PREREGISTRATION.md:41 and DESIGN.md:210 still say 6%. The new §2.1 argues "Q2 must isolate one lever … Δ is only 'the gear lever' if the budget is the only difference". That is the point: the registered budget is **already two changes** (Σgear cap + servo clamp). Relabel Q2 as "cap + servo clamp", and fix the 6% to "6.5% scaled, 34% changed (27.5% by the clamp alone)". |
| **MUST 2**: waste channels left on; R8 lever report | **RESOLVED, except one phrase** | DESIGN §7.4–7.6 and PREREG §2.1/§5 now name resting throttle and free rotors ("the cap, not the cone"). They register resting drive, `probe_static`, `phys_ghost` and `phys_passive` per line, with the O baselines committed before any B arm. **Remaining:** PREREGISTRATION.md:188 still reads "the holistic benchmark number without the lever". Make it "without the gear allowance (and servo wind-up)". |
| **MUST 3**: probes importing RBT-113's `world.py` compile B unbudgeted | **RESOLVED for the registered probes → now SHOULD** | `levers_budgeted.py` caches RBT-120's `world` before exec'ing the probe. I checked it with a stand-in probe that does `sys.path.insert(0, RBT-113); import world` and a `ProcessPoolExecutor`: through the wrapper, main and workers compile at 1.77; run directly, at 0.0. All three probes (`probe_static.py:36`, `phys_passive.py:26`, `phys_ghost.py:28`) use exactly that import. **One gap remains (SHOULD):** unlike `decompose_budgeted.py`, the wrapper has no guard that each seed directory's `config.json` carries 1.77, so running it on an O directory silently budgets O. Its closing `sys.modules['world'] is world` assertion does run, because none of the three probes calls `sys.exit`. Any *other* probe (readout adversary `probe_work.py`, `probe_gear.py`, `probe_food.py`) still needs the wrapper, so say that in RUNNER §6. |
| SHOULD 1: the Q3 null row | open | `power.py` is unchanged. |
| SHOULD 2: the √2 noise bound (ceiling power 0.69) | open | unchanged |
| SHOULD 3: "floor" is a scenario | open | unchanged. §2.1's resting-drive table makes the ceiling scenario *more* likely: the designed D line's route to its ceiling (0.94 resting drive) is open to the budgeted holistic D line. |
| SHOULD 4: verdict precedence | open | unchanged |
| SHOULD 5: the committed prelaunch.txt satisfies the gate | **open, re-confirmed** | prelaunch tree `8229e8d` = the head's tree |
| SHOULD 6: run-level controls (tree, clamp live) | open | unchanged |
| SHOULD 7: Sims credit | **RESOLVED** | DESIGN §7.1 adds (e) Sims 1994a, with the per-effector (= per-DOF) cap that does not bound a hub. The whole-body total is credited as ours, and area keying is not adopted. Crediting the servo clamp to Sims's "not permitted to exceed" is fair. |
| §2.1: the gear budget alone, no bias freeze | **agree** | K2 and Q2's single-lever reading need it. The resting-drive column makes a switch to throttle visible. A B+F follow-up is the right place for the freeze. |

---

*§1–§7 below were written against 0ce78e1. Where the table above says otherwise, it supersedes them.*

**Verdict (at 0ce78e1): LAUNCH AFTER FIXES.** The code is correct. Every MUST item below is a wording change in `runs/RBT-120/*.md`.
None touches `rabbitstew/`, so the launch tree (`7f4fe72`) and its prelaunch stay valid. No redesign is needed.

**What I did:**
- Worked on x86_64 in a clean venv (mujoco 3.14.0, numpy 2.4.6, no scipy).
- Ran the full suite: **422 passed** (243 s).
- Tested whether the new tests can fail: **8 of 8 mutants killed** (`mutants.sh` → `mutants.txt`).
- Ran four probes in this directory, each with its `.txt` output.

## 1. Code: correct (priority 1)

| check | result | evidence |
|---|---|---|
| **Off is byte-identical** in MJCF and `config.json` | **yes** | Goldens `test_off_is_byte_identical_to_the_pre_budget_code` pass, as do RBT-96/104/112/113 and the ecology goldens. The key is dropped in `SimConfig.to_dict` (`simulation.py:98-101`) and `EvolutionConfig.to_dict` (`evolution.py:106-107`). Ecology writes through `evo.to_dict()` (`ecology.py:243`), and `analysis.py:724` ships `sim.to_dict()`. No other `asdict` path exists (grep). `_servo_limit` writes no attribute when off (`world.py:318-326`). |
| **Scaling** | **correct** | The scaled `gear` feeds the damping (`world.py:214`), the torque gear, ball gears, `kp = gear/span` and `kv = gear/vmax`. So gear, damping and both servo gains scale together, and no-load speed stays at 1/joint_damping. Passive damping is untouched. Mutants M1 (gear not scaled), M2 (damping keyed to the unscaled gear) and M8 (a ball joint's DOFs counted once) are each killed. |
| **The budget reaches every compile path** | **yes, for every registered script** | `build_xml` is the only MJCF writer. `Simulation`, `gallery` and `motors` call `build_model` with `sim.world`. `evolve`/`ecology --resume` rebuild from `config.json`. `analyze`/`synergy`/`gallery` read `config.json`. `decompose_budgeted.py` imports RBT-120's `world` ahead of `decompose.py` and asserts it; the child processes receive pre-built sims, so this holds under fork or spawn. `compare.py` and `readout.py` read lineage only. `motor_report.py` reads each seed's `config.json`. **But see MUST 3: the adversary probes do not.** |
| **The Pioneer's 0.5% margin is pinned** | **yes** | `test_pioneer_ratio_is_1_76_and_inside_the_budget` asserts 1.76 < r < 1.77. Its MJCF, a bout and a whole run are identical at 1.77 and differ at 1.7. `probe_pioneer.txt` gives r = 1.760488 and scale 1.0, with the MJCF identical at 1.77, for every brain variant (plain, rich, foraging with RBT-113's sources) × mass budget ∈ {none, 15.34, 10, 5, 30}. The ratio is scale-invariant because gear ∝ mass. `mutate_controller` (`genetics.py:362`) cannot add an Effector, and a caster cannot become driven: `body_signature` holds the effectors. So Σgear stays 108 in all 24 generations. |
| **The new tests can fail** | **yes** | M1–M8 each fail ≥ 1 test: gear, damping, the servo clamp, the cap constant, both `to_dict` deletions, the CLI wiring, and the ball-DOF count. K1–K4 are shown able to fail in `test_budget_readout_controls_can_fail`. |
| **Resume** | **yes** | `run_arm.sh` resumes with `evolve --resume`, whose config comes from `config.json`, so the budget round-trips (`test_off_writes_no_motor_budget_key_and_on_round_trips`). |

**Nit (not blocking):** `cli.py:37` accepts `--motor-budget -1`. It then fails at the first compile, *after* `config.json` is written (`world.py:268`). Validate at parse time in a later PR.

## 2. MUST (before launch; documents only)

### MUST 1: the manipulation is two interventions, and the servo clamp moves 4× more founders than the cap

`probe_clamp.py` → `probe_clamp.txt` covers RBT-113's holistic founders at all 12 seeds (480). Each gets one 15 s flat solo
season, run three ways: off; the Σgear cap alone (`_servo_limit` patched to `{}`); and the registered budget.

| | founders |
|---|---|
| over the cap (scaled) | **31 (6.5%)** |
| carrying a hinge/slider servo | 186 |
| **season changed by the registered budget** | **163 (34%)** |
| of which **within the cap: changed by the servo clamp alone** | **132** |
| season changed by the cap alone | 31, all of them over the cap |

This matches the designer's own K2 at full size (`controls/k2_full_population.txt`): 27 of 40 holistic rows are identical, so 13
changed. At seed 5, `probe_clamp` gives 13 moved, 11 of them by the clamp alone.

The clamp's per-founder effect is **small on average but not everywhere** (`probe_clamp_size.txt`, seeds 1–6, 76 within-cap servo
founders):
- the season score changes in 72% of them;
- the mean |Δscore| is 0.018 yield, **max 0.99**;
- work falls in 46% and rises in 26%.

**Consequences:**
- PREREGISTRATION §2 ("About 6% of founders are over the budget and are scaled") and DESIGN §6 ("It moves holistic founders
  that are over the budget: 6%") are **wrong about what moves**. The figure is 34%, and 81% of it is the clamp.
- **Q2's Δ is the effect of cap + servo clamp**, not of "the lever" (the gear allowance). The clamp closes auditor A's B1,
  which is a different allowance that selection could have been using. It is not part of the mass-keyed gear lever that
  RBT-117's caveat names.
- **Fix:** relabel Q1 and Q2, the §7 outcome readings and the headline. Use "under the motor budget (Σgear cap + servo
  clamp)" and "how much of RBT-113's response the budget removed". Do not use "how much was the lever". Correct the 6% in both
  files to "6.5% scaled, 34% changed (27.5% by the servo clamp alone; `design-adversary/probe_clamp.txt`)".
- **No code change.** Splitting the clamp behind its own flag would be cleaner, but it costs a new tree and a new prelaunch. SHOULD 6
  gives a readout-time apportioning probe instead.

### MUST 2: say what the budget leaves on, and register the R8 lever report that Q2's interpretation depends on

- The budget caps capacity. It leaves **two waste channels** open:
  - the **Effector-bias walk** (resting throttle), which saturates the designed D line: 99.2% of its effectors have resting drive
    > 0.9, against 21.3% for the holistic D line (`RBT-121/ga/effector_bias_lines.txt`);
  - **free rotors**: 97% of the D line's work is on contact-free children (R2).
- A budgeted holistic D line has a proven route to its ceiling: the designed D line's own bias walk, which reached about 95% of it.
  So the **ceiling scenario is the likelier one, not an outer bound**.
- The §7 fork "LOWERS by less than the ceiling ⇒ A2 is the next lever" **cannot tell A2 from the bias walk** without instruments.
- The "budgeted b_div becomes the holistic benchmark number without the lever" (§7) overclaims. It is **without the gear
  allowance (and the servo wind-up)**; the resting-throttle and free-rotor levers remain on both faunae.
- **Fix:**
  1. Reword §7 as above.
  2. Name both channels in the fork.
  3. **Register, as a descriptive deliverable at readout, R8's per-line report on both O and B:** resting drive (the
     `effector_bias_lines.py` statistic) and the contact-free and ≥ ½-inside work shares (`phys_ghost.py`, per line). R8 is
     mandatory for a holistic-against-designed result, and Q3 is one. Motors-off, span and node counts can be marked "not in
     scope", with a reason.

### MUST 3: every probe reused on B directories must compile under the run's own config

- Probes that import `runs/RBT-113/world.py` would **silently compile B bodies unbudgeted**. The readout adversary's `probe_gear.py`,
  `probe_work.py` and `probe_food.py`, and RBT-121's `phys_ghost.py` (`:170`, `world.evolution_config("U", op, seed=seed)`),
  `phys_gear.py` and `bias_walk.py`, do exactly this (grep `import world` / `evolution_config`).
- This is the "budget missing from one compile path" failure. It is not in the registered scripts, but MUST 2's R8 report and
  any readout adversary would hit it.
- **Fix:** add one line to RUNNER §6 and PREREGISTRATION §5. "Any probe run on `runs/RBT-120/B*` builds its SimConfig from that
  seed directory's `config.json`, or imports RBT-120's `world.py` first (as `decompose_budgeted.py` does), and asserts
  `sim.world.motor_budget == 1.77`." Mind the order: `decompose_budgeted.py` inserts RBT-120's directory at `sys.path[0]` *after*
  RBT-113's, so a probe that inserts RBT-113's dir itself before `import world` gets the wrong module unless it asserts.

## 3. SHOULD

1. **Q3 is worth registering, but justify its reading.**
   - §7 reads Q3 NOT DECIDED as "RBT-117's HOLISTIC RESPONDS MORE does not survive the budget". That needs P(NOT DECIDED | the
     margin survives) to be small, and `power.txt` does not print it.
   - `power_adv.py` (`power.py` unchanged, ρ_up = ρ_down = 1, so E d = +0.765) gives **HOLISTIC 0.960, NOT DECIDED 0.040**. It
     gives 0.839 / 0.161 under the doubled noise of SHOULD 2.
   - So a NOT DECIDED is informative (false-NOT-DECIDED 4–16%). Add this row to `power.txt` and quote the 4–16% in §7.
2. **The "conservative noise" claim is not shown.**
   - `power.py` holds O at its observed value and draws one replicate's deviation, so Var(Δ) = σ².
   - Once B diverges at generation 0 (34% of founders move), Var(Δ) = 2σ_w², where σ_w is the within-founder replicate SD.
     That is ≤ σ², but it is not shown to be ≤ σ²/2.
   - At the bound (noise × √2, `power_adv.txt`):
     - Q2 LOWERS is **0.69 at the ceiling** (not 0.90) and 0.93 at the floor;
     - the level stays 0.025 / 0.021;
     - the ρ_down = 0.7 sensitivity falls from 0.73 to 0.47.
   - State the power as 0.69–0.90 (ceiling) and 0.93–1.00 (floor), and state the 80% MDE as roughly 0.10–0.14 σ0.
3. **R11: the "floor" is a scenario, not a bound.**
   - The budgeted D line starts at a ceiling of 0.22 (founders) and must grow its gear about 3× to reach the cap. It may not reach
     W_cf in 24 generations.
   - D food is held at O's, so a D line that stops eating instead of wasting is outside the model.
   - The prereg already reads "LOWERS by more than predicted". Rename "floor" to "counterfactual", and add ρ_down → 0 to the
     sensitivity list.
4. **Verdict precedence.**
   - `decide_q2` tests LOWERS before NO CHANGE. A CI inside (0, +0.05) with p < 0.05 therefore reads LOWERS, not NO CHANGE; the
     rules can overlap, and the code resolves them by order.
   - State the order in §3, and print "(within the ±0.05 margin)" beside a LOWERS whose upper bound is below 0.05. Q1 works the
     same way (RESPONDS before NO RESPONSE).
5. **The prelaunch gate is already satisfied by the committed file.**
   - `controls/prelaunch.txt` is committed at tree `7f4fe72`, which **is** the PR's `rabbitstew/` tree. So `run_arm.sh`'s exit-7
     gate passes on a checkout where `prelaunch.sh` was never run.
   - RUNNER says "do not commit that file", but it is committed. Remove it from the PR (`git rm --cached`, gitignore) so the gate
     forces a fresh run on the runner's machine, or have `run_arm.sh` compare the platform line too.
6. **Add controls for the run, not only the tree.**
   - K4 recompiles `final/` under the *readout's* tree. Add "`B*/commit.txt` `rabbitstew_tree` equals the readout tree".
   - Nothing checks that the servo clamp was live in the run. A cheap positive control is that B's generation-0 holistic rows
     differ from O's at every seed (`probe_clamp` predicts 7–19 of 40 per seed on flat ground).
   - For apportioning, run `probe_clamp`'s three-way re-score on the O and B `final/` populations at readout. That gives
     "Δ attributable to the cap versus the clamp", descriptively.
7. **The Sims credit** (REVIEW §4.2, §10.3).
   - DESIGN does not cite Sims at all, and the options table has no area-rule row. Add the row: per effector = per DOF, mass^⅔.
     It removes the mass-proportional growth but not the ×3 per ball joint or the hub, so it is not a budget. Evaluate it with
     `options.py` or by argument.
   - State: "The whole-body Σgear cap is the programme's own rule. Sims's cap is per effector, i.e. per DOF (Sims 1994), and it
     is not adopted here. The clamp at ±gear echoes his force clamp."
   - REVIEW's "Sims's area rule, applied per joint (our choice)" wording does not apply, because no area rule is used. Do not
     borrow it.

## 4. The rule choice (a–e): sound

- The whole-body cap is the only candidate that bounds a hub. The numbers (`options.txt`) are:
  - child keying cuts the Pioneer 29×;
  - per-joint sharing leaves the D line at up to 1.98 and the star at 10×;
  - a power budget is the same rule under the damping rule;
  - Sims's per-DOF area rule leaves the ×3 per ball joint.
- The uniform rescale keeps the body plan. Its side effect is registered: adding a driven DOF to an over-cap body weakens every
  other motor. That is a new epistasis the unbudgeted world did not have.
- **The 0.5% margin is safe for the designed body**, per §1: its Σgear is structurally fixed at 108 N·m.

## 5. Q1, Q2 and Q3 verdict rules, and the pairing

- **Q1** is honestly labelled as estimation: it cannot fail to RESPOND in any bounded scenario.
- **Q2's sign-flip** is valid for a symmetric null. B and O share founders, the RNG stream and the worlds, and diverge only through
  the budget, so under "no effect" O and B are exchangeable. The level is 0.025 / 0.021 in both noise models. The power is SHOULD 2.
- **Q2's NO CHANGE** is correctly flagged as nearly unattainable (0.064, or 0.006 at √2 noise).
- **Q3:** see SHOULD 1. It is informative, and the VOID rule is passable (0 in all scenarios).

## 6. Controls K1–K5 (R10)

- K1–K4 are each shown passable on a tiny O/B pair and able to fail (`test_budget_readout_controls_can_fail`, faults planted). K5
  is RBT-113's own, tested in `test_rbt113.py`.
- K3 can fail only through a pipeline fault (the budget does not touch the RNG). That is fine as an integrity check, but it is not
  evidence about the budget.
- **Missing:** a control that the clamp operated (SHOULD 6).

## 7. Cost and launch

- `run_arm.sh`:
  - refuses on a dirty `rabbitstew/`, a non-x86_64 machine, or a prelaunch on another tree;
  - resumes per line from `state.json` and restarts a line with no generation 0;
  - records `commit.txt` and `platform.txt`.
- The durable checkpoint loop and the no-peek rules are inherited from RBT-113 RUNNER §0–§5 unchanged.
- The costs (≈ 2–2.5 h on two sessions, ≈ 16 core-hours) are consistent with RBT-113's O arms.
- The only launch-discipline gap is SHOULD 5.

## Files (all in `runs/RBT-120/design-adversary/`)

| file | what |
|---|---|
| `probe_clamp.py` / `.txt` | 480 founders, three ways: cap + clamp, cap alone, off |
| `probe_clamp_size.py` / `.txt` | size of the clamp-only changes |
| `probe_pioneer.py` / `.txt` | the Pioneer's ratio across brain variants × mass budgets, and its MJCF at 1.77 |
| `power_adv.py` / `.txt` | `power.py` unchanged: the Q3 null row, and the √2 noise bound |
| `mutants.sh` / `.txt` | 8 code mutants against `tests/test_rbt120.py` |
