# RBT-116 `steer.py` design adversary: PR #434 @ `e703f4a` (Amendment 1 @ `c5fbe93`)

**Verdict: MERGE AFTER FIXES.**
- `steer.py` is a faithful and careful implementation of §1.1–§1.4 as ruled. The call logic, the trajectory veto,
  the confirmation, the relative T bar, the draw screen and the K / K + 2 reading all match the rulings.
- Amendment 1 matches the merged code on all five points.
- Four MUST items remain:
  - **S-M1:** the decoy's clearance re-draw ignores the world's own clearance rule. Under `clear_from=geoms`, which
    the fairness block turns on and RBT-125 has merged, 36% of decoy seasons put a phantom item where the real world
    never can.
  - **S-M2, S-M3:** two instrument faults survive the whole test suite. Mutating the lesion so that it never
    applies, or measuring T against the decoy's field, leaves all 24 tests passing. The lesion is RBT-129's
    R_marker launch gate.
  - **S-M4:** **G8(f) as registered cannot build a one-nose steerer.** Every registered variant reads NONE, with
    F < 0, in the PR's own fixture. Only the test's rectified plant steers. Left as written, G8(f) would measure
    SENS_1 ≈ 0 and collapse the holistic power.
- None of this is a redesign: S-M1 to S-M3 are small code and test fixes, and S-M4 is a one-row gate-text fix.

*Probes:*
- All run on the PR's fixture worlds and test draws, or on the committed RBT-113 checkpoint `ckpt/rbt-113-O1` (seed 1
  U finals).
- No RBT-116 arm, gate cell, W1 draw or W1 pool season was run.
- Nothing in `rabbitstew/` or in the PR's files was changed; mutants run in private copies.

| file | what |
|---|---|
| `steer_mutants.py` / `.txt` | 16 single-fault mutants of `steer.py` against the PR's 24 tests: 11 killed, 5 survived |
| `steer_real_checks.py` / `.txt` | (A) decoy clearance against the world's rule, on real bodies; (B) holistic genomes through stage 1, I1; (C) the `_job` worker path and the `SimConfig` round trip |
| `g8f_probe.py` / `.txt` | the registered G8(f) planter shape against the fixture's rectified plant, full `call_genome` |
| `tau_probe.py` / `.txt` | τ = 1 against τ = 2 s in the r5 PW caricature: the design-stage SENS priors |

## 1. Is Amendment 1 faithful to the code?

**Yes, on all five items** (`rabbitstew/simulation.py` @ `626ca4c`):

| A1 item | code | faithful? |
|---|---|---|
| 1. τ = 2 s | `FoodConfig.smell_tau = 2.0`; EMA factor `1 − exp(−control_dt/τ)` (L714) | yes |
| 2. floor 10⁻¹², xy distance from the sensor Part's geom centre, parked items contribute 0 | `_log_smell` (L718–722): `point[:2]`, `+ 1e-12`; parked at `_PARKED` = 10⁶, so exp(−10⁶/1.5) = 0 | yes. The "< 2 × 10⁻⁴" claim checks: 10⁻⁶/S with S ≥ e^(−8/1.5) ≈ 0.0048 across the disc |
| 3. baseline set to the mean on the first control tick, advanced before reading; lone nose 0, several noses their offset | `_smell_base[ri]` is None until the first `sensor_values`, which only `step()` calls (L467). The settle runs in `__init__` with no brain step, and `set_food_seed` precedes the first `step()`. `b = m` on the first call, then the update, then `tanh(G(x − b))` (L713–716) | yes |
| 4. mean over every food Sensor, one term per unit | `ks = [k … if s.source == "food"]` (L707), one entry per Sensor unit | yes |
| 5. lesion = `smell_lesion`, exactly 0 from the first tick, baseline not advanced | `sensor_values` L394–395: under lesion `_food_contrast` is **not called**, and every food sensor `continue`s at 0 (L423–424) | yes |

**One A1 sentence is no longer supported** (see §2): r7 L265, "one-nose steering below F_MIN is excluded by design,
not missed".

## 2. Does τ = 2 s break a power or prior claim from R5 or R6?

**No registered decision rests on the τ = 1 s numbers.** SENS_1, SENS_c, SENS_P, EPS and K are all gate-measured or
gate-chosen on the merged channel, as A1 says. But the **priors move, and one sentence falls.** From `tau_probe.txt`
(r5 caricature and call, 25 genomes × 2 batteries):

| body | τ 1 s: confirmed / F | τ 2 s: confirmed / F |
|---|---|---|
| two-nose steer2 k 6 (`power.py` SENS_C_TWO prior) | 0.48 / +1.20 | **0.40** / +1.15 |
| one-nose steer1 k 32 (SENS_C_ONE prior) | 0.32 / +0.56 | **0.24** / +0.52 |
| one-nose steer1 k 8 (moderate gain) | 0.00 / **+0.14** | 0.00 / **+0.30** |

- **L265 no longer holds at τ = 2.** Moderate-gain one-nose run-and-tumble now earns F +0.30, above F_MIN, and is still
  never confirmed. That steering is *missed*, not excluded.
- **"The stronger no" is now less likely to be registered.** r7's power table 2a shows that a p_H 0.5 bypass at
  SENS_C,H ≈ 0.24 falls below the 0.8 bar. At K = 5, detection is 0.85 at 0.32 and 0.47 at 0.20 (r7 power table 2a), so
  about 0.6 at 0.24 by interpolation.

**S-S1 (SHOULD):**
- Update `power.py`'s priors to SENS_C_TWO 0.40 and SENS_C_ONE 0.24, cited to `tau_probe.txt`.
- Strike or qualify L265 (and R5-2's matching clause in §0) as "at τ = 1 s; at τ = 2 s a moderate one-nose steerer pays
  F ≈ 0.30 and is not confirmed".

**What must be re-measured at the gate on the merged channel** (all already registered as gate-measured; listed so
that none is borrowed):
- SENS_1 (G8(f), see S-M4), SENS_c (G8(c)), SENS_P and c_G1 (G1, G8(a));
- EPS_C (G4), and K by its rule;
- **G7's lone-nose intermediates** (the pirouette and the lone-nose throttle read the temporal channel, whose gain is
  G·τ = 5, not 2.5);
- the G1/G2 prizes;
- G6's σ_P and u_f.

## 3. `steer.py` against every MUST and SHOULD I raised

| item | `steer.py` | status |
|---|---|---|
| M1 count veto → trajectory veto; draw screen | `trajectories_differ` (root xy, 1e-9); `c3 = 2·differ > n`; `screen_draws` (half the hosts, extend 32 once, fail) | **implemented**. Mutants veto-off, veto-at-half and veto-is-food-count (r3's bug restored) are all **killed** |
| M2 T threshold relative; T := 0 flagged; excluded share | `Season.v_min` = 0.25 × median; `chemotaxis_index` → (0, flagged, excl) | implemented. The decoy season reads its intact partner's bar, but the mutant using the decoy's own bar **survives** (S-S2) |
| M3 G8(b) paying and sign-blind | planter is `gate.py`'s (not in the PR) | n/a here |
| M4 crossover / holding | not `steer.py`'s | n/a |
| M5 the named transform | `run_season` uses the world's own channel; the decoy patches `_log_smell` **and** `_intensity` | **implemented**. Mutant decoy-rotates-legacy-only is **killed** |
| M7 / R5-1 confirmation; EPS as the confirmed rate | `call_genome` stage 3; `pass_unconfirmed` is NONE | implemented. Mutant no-confirmation is **killed** |
| M8 / R6-1 K and K + 2; U − N SMELL-USE | `line_reading`, `smell_use_print` | implemented |
| SHOULD 1 θ re-draw for spawn clearance | `draw_theta`: root only, 0.8 m | **partly: S-M1** |
| SHOULD 2 rotation invariance asserted | `assert_rotation_invariant`: structural (layout methods not overridden) | implemented, with a gap (S-S3) |
| SHOULD 3 klinokinesis is STEERS | the call is behavioural | consistent |
| R5-2 G8(f) | planter is `gate.py`'s | **the registered shape cannot pass: S-M4** |
| I1 (a genome with no food sensor is identical, so NONE) | stage 1 | holds on real bodies: `steer_real_checks.txt` B, including two holistic finals with an idle nose, stopped at stage 1 |

**The 21 STEER_NOTES readings:** I accept N1 and N3–N21 as faithful readings of the text. The exceptions:
- **N2** ("the root at spawn") is literal to r7, but r7's own fairness block (L414) flags that `clear_from=geoms`
  "interacts with the decoy's clearance". That flag is now merged (S-M1).
- **N13** is correct, but untested in `run_season` (S-M2).
- **N16** (penetration sampled once per control tick) can miss a deeper intra-tick contact. It is reported only (NIT).

## 4. MUST

### S-M1: the decoy must clear the world's clearance points, not only the root

`steer_real_checks.txt` A uses a fixture world with `clear_from=geoms` and `eat_from=root`, 10 RBT-113 finals per
fauna, and 20 test draws each. The real layout always clears every geom centre by 0.8 m; the decoy's accepted θ does
not:

| fauna | seasons | decoy puts a rotated live item inside 0.8 m of some geom centre |
|---|---|---|
| holistic | 200 | 73 (0.365) |
| designed | 200 | 70 (0.350) |

The nearest phantom item is 0.39 m from a geom centre. That is exactly the "phantom item under the nose at t = 0"
that SHOULD 1 was ruled to remove, now on limbs and wheels rather than on the root.

**Fix:**
- In `run_season`, pass `sim._clearance_points()` to `draw_theta` in place of the root: every geom centre under
  `clear_from=geoms`. Under `eat_rule=surface` (the `_SURFACE_CLEAR` marker), use `sim._surface_distance(...)`.
  Either way, the decoy obeys the rule the world placed the real items by.
- Pin it with a test on a `clear_from=geoms` fixture.
- Amend N2 and §1.1's decoy row to "the world's clearance points at spawn".

### S-M2: a lesion that is never applied passes every test

The mutant that removes `smell_lesion=True` from `run_season` **survives** (`steer_mutants.txt`).
- `test_lesion_is_the_transforms_zero_information_constant` builds its own `Simulation`, and
  `test_lesion_season_changes_only_the_food_readings` uses a sensorless body, whose lesion equals its intact season
  either way.
- `steer.py`'s lesion condition is RBT-129's R_marker launch gate.

**Fix:** a test that `run_season(two_nose_steerer, …, "lesion")`:
- (a) runs with every food reading 0 (record or assert through the `Simulation`);
- (b) differs in trajectory from intact on the fixture draws;
- (c) gives L > 0 on the planted steerer.

### S-M3: T against the decoy's own field passes every test

The mutant that computes ĝ from the *rotated* items in the decoy season **survives**.
- That mutant turns condition 2 (the kinesis guard, MUST 3) into a comparison against the field the body follows.
- The planted positive still STEERS in the fixture, so the suite never looks at what T measures.

**Fix:**
- A synthetic test: a body driven straight at a lone item reads T ≈ +1, and driven straight away T ≈ −1.
- A season test: on the two-nose steerer's decoy seasons, T is computed against `sim.food_pos`, the real items
  (assert T_decoy < T_intact on the mean over the fixture draws, and that ĝ uses the unrotated positions).

### S-M4: G8(f) as registered cannot produce a one-nose steerer

§4.3 G8(f) plants "a global unit on its reading, and a turn command ±w to the Effectors on one side, 2 signs ×
w ∈ {4, 16, 64}". The PR's passing one-nose fixture plant is not that shape: it uses a **ReLU** on −128 × the reading
(turn only while the contrast *falls*) into both wheels. `g8f_probe.txt` runs the full `call_genome` on the PR's
`ONE_NOSE_WORLD` fixture, with a Pioneer host and one wheel nose:

| plant | call | F (stage 2) |
|---|---|---|
| registered shape: tanh, input 1, ±w to one wheel, w ∈ {±4, ±16, ±64} (6 variants) | **NONE ×6** | −1.50 to −0.56 |
| the fixture's: ReLU, input −128, both wheels at w 2 | **STEERS** | +3.31 |
| tanh, input −128, both wheels | NONE | −0.31 |
| ReLU, input −1, one wheel, w 16 | NONE | 0.00 |

The rectifier (asymmetric response to falling against rising contrast) and a high input gain are what make one-nose
run-and-tumble work. A symmetric unit turns as much on approach as on retreat. "Input 1" is my reading, since the
registration does not state the input gain. But even at −128, the tanh plant fails.

If G8(f) is built as registered:
- SENS_1 ≈ 0;
- `power.py`'s holistic SENS = min(SENS_c, SENS_1) ≈ 0, so no holistic crossing could be detected;
- the gate's G8(f) re-run would stop "the stronger no" for the wrong reason.

**Fix:** amend G8(f)'s grid to the shape the fixture proves: a **rectified** unit on the reading, sign × input gain
∈ {32, 128} × w ∈ {2, 8}, to both drive Effectors (or to one side and both). Keep "best by F on screening draws".
Validate the planter on the fixture, as a test in `gate.py`'s PR, before any gate cell.

## 5. SHOULD

- **S-S1: priors after τ = 2 s** (§2). Update `power.py`'s SENS priors, and strike or qualify L265.
- **S-S2: tests for the other three surviving mutants.**
  - `stage1-stops-on-any-identical`: a genome identical on 3 of 4 stage-1 draws must go on to stage 2.
  - `decoy-on-its-own-speed-bar`: assert that the decoy's T uses the intact v_min. A synthetic pair whose bars differ
    will do.
  - `F_MIN-halved`: pin the registered constants (F_MIN, stage sizes, θ range, V_MIN_FRAC, TRAJ_TOL, K and the K + 2
    step, POOL_KEY["W1"]) in one test (R12).
- **S-S3: the rotation-invariance assertion** compares each layout method against `Simulation`'s *current* attribute.
  So a module-level monkeypatch of `Simulation._food_spot` (the pattern RBT-97 and the RBT-113 probes used for smell)
  passes it. Capture the committed functions' identities at `steer.py` import time, or compare `__code__` hashes. It
  should also assert `food.clear_from`/`eat_rule` agreement with the decoy's clearance (after S-M1).

## 6. NIT

- N16: penetration is sampled at control ticks only. It is fine as reported, but say "per control tick" in `steer.txt`'s
  header.
- `Season.v_min`'s median includes ticks at rest. That is the literal reading (N8), but a body that rests for half
  the season gets v_min = 0, so all its moving ticks count. This is conservative and fine; state it in STEER_NOTES.
- θ acceptance depends on the body (the settled root, and after S-M1 the geoms), so two faunas on one draw can see
  different decoys. N2 says so. After S-M1 it will hold more often, so keep the `redraws` column.

## 7. Determinism and the worker path

`steer_real_checks.txt` C:
- `SimConfig.to_dict`/`from_dict` keeps every W1-relevant flag: `eat_from`, `clear_from`, `eat_rule`, `smell_contrast`,
  `smell_tau`, `patches`, `patch_radius`, `regrow_delay`, `settle_until_rest`, `settle_max`, `duration` and
  `random_start`. The field differences are none.
- A call through `_job` (the `ProcessPoolExecutor` path) equals the in-process call exactly.

The PR's `test_determinism` covers repeated in-process runs. The θ stream is keyed on the start seed alone, so it is
shared across faunas and paired worlds, as registered.

Stage 1 on real holistic genomes ran without error. It took 1.9–3.4 s per 8 fixture seasons, and the excluded-tick
share was 0.04–0.30 under the relative bar (`steer_real_checks.txt` B).
