# RBT-116 `steer.py`: readings of the registration, and what the next scripts need

`steer.py` implements PREREGISTRATION.md §1.1–§1.4 (r7, with Amendment 1 as revised and Amendment 2) and the reading
rules R5-1, R6-1 and M1/M7 as ruled. Line numbers below are PREREGISTRATION.md's as first cited (after Amendment 1's
first version); Amendment 2's insertion shifts them, so the rows also name their sections. Tests:
`tests/test_rbt116_steer.py`.

**No RBT-116 output exists.** Nothing here has run on W1, its draw pool (`draw_pool("W1")` is generated and pinned by
a test, but no season has run on it) or any RBT-116 host. The tests use fixture worlds (flat, 4 items in a 2 m disc,
10 s; and 8 items, 15 s for the one-nose positive; the contrast channel at G = 2.5 and the registered τ = 1 s) and
fixed test draws, with hand-planted Pioneer bodies.

## Where the text left a choice (each picked for the ruling text's intent)

| # | line(s) | the text | the reading taken | why |
|---|---|---|---|---|
| N1 | L189 | "Solo seasons in the world point" | The **selection's own solo season**: `simulation.run_solo`'s layout (robot 0 of `spawn_layout(2, …)`, `opponent_proxy`), food from the start seed, the draw's terrain seed set as `generation_sim` sets it. Robot 0's spawn is the same as `spawn_layout(1, …)`'s, and a test checks that food and work equal `run_group`'s (RBT-113's `decompose.py` season) exactly. | F must measure what `evolve` selects on. |
| N2 | §1.1 decoy row (L205), L90, L389; **Amendment 2 item 3** | the decoy's θ is re-drawn until no rotated live item lies within 0.8 m of ~~the root~~ **the world's clearance points** at spawn, from "a registered stream keyed on the season's start seed" | θ candidates are U[30°, 330°] from `default_rng([116, 97, start_seed])`, in order. The first candidate that clears is used. **(S-M1)** The clearance test is the world's own rule, read from the season's simulation after the settle, when the food is placed (`world_clearance(sim)`, from `Simulation._clearance_points()`): each root under `clear_from=root`, every geom centre under `clear_from=geoms`, and the 3-D distance to every geom surface (`_surface_distance`) under `clear_from=geoms` with `eat_rule=surface`. The distance is the world's `food.clearance` (0.8 m at W1). | The stream depends only on the start seed, so it is shared across faunas and paired worlds. Which candidate is accepted can depend on the body (its settled root and geoms), which is what the clearance is for; the `redraws` column shows how often. |
| N3 | L255–257 | STEERS needs a stage-2 PASS **and** a confirmation PASS. SMELL-USE is "meets 1 and 3 on stage 2 but fails 2". "Everything else is NONE." | A stage-2 PASS that the confirmation does not repeat is **NONE**, by the letter. It is flagged `pass_unconfirmed` (PASS-UNCONFIRMED in `steer.txt`) beside the call, never as a call. SMELL-USE is read on stage 2 only, and needs no confirmation. | §1.3 names exactly three calls. The flag lets `readout.py` report the unconfirmed passes without changing the call. |
| N4 | L243, L768 | stage 2 runs "all four conditions"; the confirmation repeats the PASS | The confirmation runs **intact and decoy only** (16 × 2 seasons). Lesion and motors-off feed only reported quantities (L, off food). | §9's costing: "confirmation (32 seasons)" and "stage 2 (64 seasons)". |
| N5 | L205 | re-draw until clear | If 4,096 candidates from the stream all fail, the season raises instead of looping. No W1-like layout comes near this: an item's forbidden arc is at most about 64° at 1.5 m. | A loop that cannot end is not an instrument. `gate.py` should report such a draw rather than retry it (see below). |
| N6 | L222 | "ĝ is the unit gradient, at the CoM, of the real, untransformed field" | ĝ is taken at the CoM **at the start of each control tick**, over the items **standing at the start of that tick** (before that tick's eating). v is the CoM displacement over the tick ÷ Δt. | This is the adversary's `steer_real.py` convention (the gradient at `prev`), and it keeps an item eaten on this tick in the field the step moved toward. |
| N7 | L226 | T over "included ticks" | A tick with no standing item has no ĝ, so it is **excluded**, and counts in the excluded share, like a slow tick. | cos∠(v, ĝ) is undefined there. `steer_real.py` skipped such ticks in both sums too. |
| N8 | L224 | v_min = 0.25 × "the member's median \|v\| in its intact season on that draw" | The median runs over **every** control tick of the intact season, before any exclusion, ticks at rest included. A body that rests for half the season or more gets v_min = 0, so all its moving ticks count (conservative: it keeps ticks rather than dropping them); a body that never moves is T := 0, flagged. | This is the literal reading. |
| N9 | L218, L251 | "`traj`: the root's xy path, hashed per tick to 1e-9"; the veto: "differ (by more than 1e-9 at some tick)" | The veto compares the paths themselves: the root body's xy at tick 0 (the settled start) and after every control tick, differing if max \|Δ\| > 1e-9. The rounded-path hash (`traj_hash`) is reported, not used. | Comparing paths avoids a hash's rounding-boundary artefacts. It matches the veto's own wording ("by more than 1e-9 at some tick"). |
| N10 | L251 | "more than half of the 16 draws" | Strictly more than half: 9 or more of 16 (a test pins that 8 of 16 fails). | The literal reading. |
| N11 | L247 (conditions 1, 2) | "the one-sided 95% t lower bound" | This is mean − t(0.95, n−1) · sd/√n, computed without scipy. With zero spread the bound is the mean, so a constant positive difference passes and a constant zero does not. | The limit of the t bound as sd → 0, and `steer_real.py`'s convention. |
| N12 | L205, L391 | the decoy "is applied to item positions before the transform"; the hook "refuses a layout rule that is not rotation-invariant" | The decoy rotates what **both** smell paths read: `Simulation._log_smell` (the contrast channel) and `_intensity` (the legacy reading). A test shows that each reads the rotated layout. Rotation invariance is asserted structurally: the season's simulation class must use the committed layout methods (`_draw_patch_centres`, `_food_spot`, `set_food_seed`, `_install_spots`, `_eat`, `_regrow_spots`), which draw uniformly in a disc about the origin, plus `_clearance_points`, which the decoy's clearance reads. Any override is refused. **(S-S3)** Each method is fingerprinted (defining module, qualified name, bytecode digest) at `steer.py`'s import, and must still be `rabbitstew.simulation`'s `Simulation.<name>` when the check runs, so a module-level monkeypatch of `Simulation` (before or after the import) is refused. `clear_from` and `eat_rule` must be committed rules. | Rotating only `_intensity` gives a decoy that reads the true layout under G > 0, which is the RBT-125 gate's `prize_gate.py` finding. The committed layout rule is the only one that exists, so the assertion guards against a future override. |
| N13 | L159 row (A1) | lesion | `FoodConfig.smell_lesion = True`: every food sensor reads `LESION_CONSTANT` = 0 from the first tick. A test pins that 0 is tanh(G · 0), what a lone nose reads at its own baseline on its first tick. | Amendment 1, item 5. It is the flag RBT-129's R_marker arm uses (its §6.4: "as `steer.py`'s lesion condition does"). |
| N14 | L207 | motors-off: "every actuator command held at 0" | The brain still steps and reads its sensors, but every Effector output is 0 (as `rabbitstew/levers.py`'s motors-off season does). `disp` is the CoM displacement over the season. | This is the committed way of taking the motors off. |
| N15 | L217 | "`cells`: distinct 0.35 m xy cells under any geom" | These are the cells holding any of the robot's **geom centres**, at tick 0 and after every control tick (RBT-113's `probe_food.py` rule). Items per 100 cells is 100 × food ÷ cells. | This is the committed probe's rule. |
| N16 | L220 | "`pen`: the deepest contact penetration (H71)" | It is the largest −dist over the MuJoCo contacts that involve any of the robot's geoms, over the season's control ticks (after the physics substeps of each tick). It can miss a deeper contact inside a tick; `steer.txt`'s header says "pen is sampled per control tick". | It is reported only. |
| N17 | L271 | the relative F_MIN, "printed beside the call" | `F_min_rel` = max(0.25, 0.2 × mean intact food on stage 2), with whether condition 1 holds at it (`c1_rel`). It never changes the call. | The registration marks it [OPEN] and reported only. |
| N18 | L279, L584, L166 | crossing at K, and headlining at K + 2 | `line_reading` returns `crossed_K` and `crossed_K2` for one line: U ≥ k and U − N ≥ k, at k = K and K + 2. The verdict-level K + 2 rule (the three §6.3 tests recomputed with crossing at K + 2) is `readout.py`'s, built on these two flags. | `steer.py` owns the per-line reading, and the across-unit test is the readout's. |
| N19 | L166, L633 | "The U − N SMELL-USE share is printed per probe" | `smell_use_print` prints, per line and probe, the STEERS counts and shares, the SMELL-USE shares in U and N, U − N, and crossing at K and K + 2. The U − N CIs across units (§6.4) are `readout.py`'s. | — |
| N20 | L192 | the screen: "at least half of those hosts eat ≥ 1 item on it" | A draw is admissible iff 2 × (hosts eating ≥ 1) ≥ hosts, with the intact condition only. The extension is the **next 32 of the same registered stream** (`draw_pool(world, extended=True)[64:]`), so it never alters the first 64. The table lists every draw screened, 64 or 96. | "Extended by 32 more draws, once." |
| N22 | Amendment 1 (revised) | "W1's block sets `smell_tau: 1.0` explicitly" | `SMELL_TAU = 1.0`; `run_season` and the command line refuse a world whose contrast channel (`smell_contrast > 0`) runs at another τ. A legacy world (no channel) is not refused, since τ plays no part there. | The code's default is 2.0 (RBT-125 and RBT-129 run there), so a W1 config that forgot the flag would silently run another channel. |
| N23 | §1.2; S-M2 | the lesion must be shown applied | Each season records `food_abs_max`, the largest \|reading\| of any food sensor, read from the brain's inputs after every tick. It is 0 under the lesion. | It pins R_marker's condition (RBT-129) in the season itself, not in a separate simulation. |
| N24 | Amendment 3 item 3 (FC-M2, FC-S1) | a draw with no clear θ | `draw_theta` raises `ThetaRefused`; `_pairs` runs the decoy first, and a refused draw is excluded from every condition of that battery and counted. Each record carries `theta_attempted`, `theta_refused` and `theta_refusal_rate` (printed as "θ refused k/n"). A stage-1 battery with every draw refused cannot stop the genome; a stage-2 or confirmation battery with fewer than `MIN_USABLE` = 2 usable draws is not called (NONE, `too_few_draws`). The veto's "more than half" and the t bounds run over the usable draws. | Which draws refuse depends on the body, so the screen (intact only) cannot catch them; one bad draw must not lose the call. |
| N25 | Amendment 3 item 2 (FC-M2, FC-S3) | W1's block | `REGISTERED_POINTS["W1"]` = G 2.5, τ 1 s, `eat_from root`, `eat_rule surface`, `clear_from root`, `eat_radius` 0.35; the command line (`--world W1`) refuses any difference, a lost `--smell-contrast` included. `run_season` keeps only the τ guard, so fixtures with other eating rules still run. | The code's defaults (legacy channel, τ 2 s, any/centre eating) would otherwise run silently. |
| N26 | Amendment 3 item 2 (#446's minimal guard) | the decoy under surface eating | `world_clearance` adds the eating guard under `eat_rule=surface`: every rotated item ≥ `eat_radius` from every eating geom's surface, on top of the world's clearance points. Under the full surface clearance the guard is implied. Since #446 merged (`01f113d`), `_clearance_points` returns `(_SURFACE_CLEAR, centres, geoms, min_surface)` under surface eating, and `world_clearance` reads it exactly as `_food_spot` does (a test checks that every real layout passes it under three rules). A clearance rule `steer.py` does not know is refused, not guessed. For the Pioneer's compact root the guard never binds (corner reach about 0.62 m, under the 0.8 m centre clearance), so fixture placements are the same before and after #446. | The decoy must never smell an item inside eating reach, whatever the placement code does when #446 lands. |
| N21 | L190 | "64 candidate draws … are fixed in the file per world point" | The pool is generated from a registered key per point (`POOL_KEY["W1"] = (116, 64, 1)`), and a test pins that it is stable. A new world point (W2) needs its own key row before its gate, so that its pool is fixed before any season runs on it. | A seeded stream fixes the pool as firmly as a literal table does, and it stays reviewable. |

## Why the both-wheel G8(f) plants at w ≥ 4 read NONE with F ≈ +3 (FC-M1; `g8f_diag.txt`)

Every such plant **PASSES stage 2 strongly**: F +3.1 to +3.9 with lower bound +1.3 to +2.2, ΔT lower bound +0.13 to
+0.17, and the trajectories differ on 16 of 16 draws. It fails **only condition 1 on the confirmation battery**: F
there falls to +0.6 to +1.5, with lower bound −0.10 to −0.55. F falls on the confirmation draws for **every** variant,
w = 2 included (+3.31 → +1.69); w = 2 just keeps its lower bound above 0 (+0.22). The test battery is unscreened, and its
confirmation draws pay this plant less.

**This is not a call-logic defect.** §1.3 is applied as registered: STEERS needs the F bound, the ΔT bound and the veto
on two independent batteries, and the second battery's F was not distinguishable from 0 at 95%. What it shows is the
planted control's **confirmed sensitivity** below 1, which is exactly what G8(f) measures as SENS_1 (and G8(c) as
SENS_c). It applies to real steerers in the same way, which is why every SENS in `power.py` is a confirmed rate
(R5-1). At the gate the reachability screen removes the draws on which the hosts cannot eat, which should narrow this
gap, but it is measured there, not assumed. Amendment 3 therefore registers G8(f)'s build by a fixture-only majority
rule over three fixture variants (`g8f_rule_probe.txt`), rather than by one fixture battery.

## Not in this PR, and what each needs from `steer.py`

- **`gate.py`** (G1–G9). It builds W1's `SimConfig` with `smell_tau: 1.0` and the eating block (N22, N25), and reports
  each host's θ refusal rate (N24). Its G8(f) planter is Amendment 2's
  rectified unit, shown to steer on the fixture world by a test in its own PR before any gate cell.
  - `screen_draws(hosts, cfg, world)` with the G8(a) and G8(c) hosts. It writes `result["table"]` as the committed
    reachability table and `result["battery"].to_dict()` as the battery JSON that `steer.py --battery` reads. It stops
    the point if `passed` is False.
  - `call_genome` for G1 (stage-2 PASS counts: read `rec["stage2"]["passes"]`, whatever the final call), G4
    (confirmed false-STEERS rate: `rec["call"] == STEERS` on 200 burn-in finals per fauna), G8(a)–(f) (confirmed
    shares; SENS_1 from (f)) and G6's children (parent and child on the same `Battery`).
  - N5's refusal (`RuntimeError`, no clear θ) should be caught per draw and reported.
  - W1's `SimConfig` comes from `world.py`, which is also not in this PR.
- **The G8 planters** ((a)–(f)) produce genomes and nothing else. `steer.py` is body-general, and calls whatever it is
  given. The test file's `two_nose_steerer` and `one_nose_steerer` are fixture plants only. They are not G8(c) or G8(f),
  which are tuned per host on screening draws, as the registration says.
- **`readout.py`**:
  - per probe, `line_reading(calls_U, calls_N, K)` and `smell_use_print`;
  - §6.2–§6.3 across units, and the K + 2 headline rule, from `crossed_K` and `crossed_K2`;
  - I1 (every zero-food-sensor genome has identical intact and decoy trajectories: `rec["stage"] == 1` and
    `rec["stage1_identical"] == 4`, or the identity on every stage-2 draw);
  - I8 from the generation-0 confirmed calls;
  - `steer.txt` rows come from `format_call`, and `steer.py --json` keeps every field.
- **The proposal assay** (§5.2) calls parent and child with `call_genome` on the same `Battery`.

## Validation

- `tests/test_rbt116_steer.py`: 42 tests (24, plus 10 for the adversary's fixes, plus 8 for the FIX-CHECK: θ refusal
  is non-fatal on synthetic and real refusing fixtures, the eating guard, the W1 block, a pre-import patch, and the
  decoy's clearance mirroring the world's placement under three rules).
  - **Planted positives:** a two-nose Pioneer compass and a one-nose run-and-tumble Pioneer (its only food sensor on
    the left wheel) each read STEERS on the full 4 + 16 + 16 battery.
  - **Planted negatives:** a moving body with no food sensor, and one with two unwired noses. Each has intact, decoy
    and lesion trajectories identical tick for tick, and reads NONE at stage 1.
  - The lesion reads the zero-information constant; two noses read ± their offset on the first tick (Amendment 1).
  - The decoy clears the root and rotates both smell paths; the rotation-invariance refusal holds; motors-off does
    no work.
  - The intact season equals the selection's season; T's bar and flag; determinism.
  - The call logic on synthetic seasons: STEERS, SMELL-USE, NONE, the veto at exactly half, and PASS-UNCONFIRMED is
    NONE.
  - The t quantile; the screen's rule, order, extension and failure; K and K + 2, and the SMELL-USE print.
- **The adversary's fixes** (`design-adversary/ADVERSARY-STEER.md`):
  - S-M1: the decoy clears every geom centre, and every geom surface, where a root-only clearance fails on some
    fixture draws;
  - S-M2: the lesion season reads 0 on every food sensor, changes the steerer's path and costs it food;
  - S-M3: a smell-blind body's decoy T equals its intact T tick for tick, so T is read against the real field;
  - S-S2: stage 1 goes on at 3 of 4 identical; the decoy is read on its intact partner's bar; the registered constants
    are pinned;
  - S-S3: a module-level monkeypatch of the layout methods is refused; N22: a world at τ ≠ 1 s is refused.
  - The adversary's `steer_mutants.py`, with the clearance mutant's anchor moved to the new `draw_theta` line, kills
    16 of 16 (`steer_mutants_fixcheck.txt`).
- The planted positives depend on MuJoCo's determinism on one platform. They are fixed bodies on fixed draws, so a
  platform change that moved them would show as a test failure, not as a silent change.
