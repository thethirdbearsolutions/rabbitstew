# RBT-125 adversary: the perception pack (PR #414) and its world-gate registration

*Adversary for RBT-125 (epic RBT-123). Reviewed: PR #414 at head c40ecd5, and the gate registration committed at
5749e97 (tree 0ec395f, from which the designer runs the gate at 23:01 UTC). **No-peek:** I opened no gate output
(`gate/prize/`, `steps/`, `side_effects.txt`, `prize.txt`, `launch.txt`). Every number below comes from my own probes on
committed bodies, logged beside this file. The registration findings were posted on RBT-125 at 22:24 UTC, and the
scipy heads-up at 22:15.*

## Verdicts

| | verdict |
|---|---|
| **Code (PR #414)** | **MERGE AFTER FIXES**: 2 MUST (C1, C2) and 1 MUST shared with the gate (G5) |
| **Gate (REGISTRATION.md)** | **REGISTER AFTER FIXES**: 7 MUST (G1–G7). Every one can be settled before any gate output is read. G4 and G5 may add compute |

**What holds, and was checked:**

| claim | evidence |
|---|---|
| The full suite passes in a clean `pip install -e ".[dev]"` venv with no scipy: **456 passed** | `suite_clean_venv.log` |
| Off is byte-identical: RBT-113's goldens pass with every flag given explicitly at off, and are part of the 456 | same |
| The two config strips (RBT-120's `motor_budget`, RBT-125's perception fields) are correct together: off/off writes neither, each on writes only its own family, and both round-trip through `EvolutionConfig` and `SimConfig` | `probe_strips.txt` |
| The pinned gate tree is #414's in effect. 0ec395f and c40ecd5 give the same digest of `qpos`, work, items and food over 9 cells × w∈{0,3} × 3 seeds + the patched decoy. `runs/RBT-125`, `RBT-103` and `RBT-97` are identical between the two | `probe_tree_parity.txt` |
| The decoy patch is needed, and works in the harness's fork pool. Unpatched, the decoy under G = 2.5 reproduces the true-smell motif in 32/32 seasons; patched, it does not. `check_decoy()` **fails** with the patch removed, so its assertion has teeth | `probe_decoy.txt` |
| §A can fail, and it discriminates: see the P-801 table under G1 | `p801_PW-G2.5.txt`, `p801_PW-G0.txt` |
| The baseline is per robot, over that robot's own food noses. It starts at the first control tick after settle (settle never reads sensors). It restarts with every `Simulation`: one per season in `run_bout`, `run_solo`, `run_group` and every gate script | `simulation.py:195, 297, 583–605`; code read |
| A spinning nose cannot manufacture signal. With the food removed, every nose reads exactly 0 on a full-throttle rod, arm or root, 0.45 m or 1.5 m | `probe_spinner.txt` |
| The surface distance is exact for box, sphere and cylinder, with the cylinder along local z and `size = (r, half-height)`. The brute-force test covers all three under rotation | `simulation.py:502–521`, `test_surface_distance_matches_a_brute_force_surface_sample` |
| `sensor` on the Pioneer is the chassis plus the two drive wheels, and not the casters; `root` is the chassis | tests at `test_rbt125.py:266–310`; code read |
| The CLI flags reach `evolve`, `simulate` and `ecology` through the shared food-argument helper | `cli.py:60–71`; test |

---

## Part 1. The gate registration

### What §A's instrument does on a real population (P-801)

RBT-19's P-801 Pioneers are committed and are not a gate population. I ran the gate's own wrapper on them
(`prize_gate.py --config-from worlds/<cell> --w 3 --decoy 3`, 64 seeds from 7000), exactly as `run_gate.sh` runs a
population:

| cell | bodies signed | prize a = 6, t(n−1) 95% | motif − decoy | decoy retains | zero pairs |
|---|---|---|---|---|---|
| PW-G2.5 | 6/7 (g100 UNDETERMINED) | **+0.820 [+0.512, +1.128]** | **+0.727 [+0.393, +1.060]** | 11% | 256/384 |
| PW-G0 | 7/7 (g100 and g400 signed **+1**) | +0.127 [−0.206, +0.460] | +0.025 [−0.195, +0.244] | 81% | 343/448 |

**What this shows:**
- a = 6 is a reasonable rung.
- The channel moves the prize and its food-dependence by a wide margin on this population.
- At 10 populations, G = 2.5 is unlikely to be underpowered, if the RBT-90 part 2 populations resemble P-801. RBT-106's across-population SD at a = 32 was 0.26 (U) and 0.49 (HP); a t(9) lower bound > 0 needs a mean above about 0.72 × SD.
- Per-body delta SD is about 2.6–3.0 items per season.

### MUST

**G1. PASS is not about the channel.**
- Both PASS conditions (prize LB > 0, motif − decoy LB > 0) are read inside one cell. Nothing compares against G0.
- If PW-G0 passes on the RBT-90 populations too, "PASS at G = 2.5" means only "PW pays a = 6".
- (PW-G − PW-G0) is printed, but it gates nothing.
- **Fix:** register the paired (PW-G − PW-G0) t(9) lower bound > 0 as the condition for any statement that *the channel* pays. Otherwise word the verdict as a statement about the world.
- **Re-signing per cell changes the bodies.** On P-801, g100 is UNDETERMINED under G2.5 but signed +1 under G0, and g400 is −1 under G2.5 but +1 under G0. The base body's travel direction depends on G, because its evolved wiring reads the food sensors.
  - The paired contribution therefore compares different installs.
  - Report it also on the bodies signed the same in both cells.

**G2. Missing populations are silently dropped.** `prize_readout.py` keeps a population only if its file has a ROW (`read()`), and reads a cell once 2 or more populations remain (`if len(rows) < 2: continue`). A population drops without a ROW when:
- every body is UNDETERMINED (NOT READABLE; `routed_populations.py` returns before ROW);
- a best file is missing (STOPPING);
- the run crashes.

The t(n−1) bound then runs on fewer populations, and nothing says so. **Fix:** PASS needs all 10 populations, with the decoy on the same ones, or give a stated rule for a missing one (for example, it counts as prize 0 and decoy retention 100%). Print n per cell.

**G3. The harness-check stop is not implemented.**
- REGISTRATION §D: "a harness check that is DIFFERENT … stops the script."
- `run_gate.sh` writes `harness-801-uniform.txt` and goes straight on to the PW cells. Only `prize_readout.py` compares, and only at read time.
- **Fix:** implement the stop, or amend §D to "nothing in §A is read". The second is fine for inference, since the stop saves only compute.
- (SHOULD) The check exercises only the uniform world, G = 0, w = 16/32, without `--config-from` and without the decoy. Add a second row check through `--config-from`: RBT-106's committed HP-801 row. My tree-parity probe covers the code identity, but not the harness path.

**G4. §B cannot answer R4 as registered.** `probe_step_power.txt` runs `steps.py`'s own `bout()` (same arms, damping step and seeds) on six committed P-801 Pioneers in PW-G2.5.

| body | w3 → 3.4 step (sd) | speed step (sd) | realised speed ratio | zero pairs |
|---|---|---|---|---|
| g0 | +0.16 (0.92) | +0.91 (2.09) | 1.14 | 26/32 |
| g200 | +0.47 (3.54) | −0.13 (0.71) | 1.32 | 14/32 |
| g300 | +0.38 (1.93) | +0.16 (1.65) | **0.49** | 19/32 |
| g400 | +0.22 (2.42) | +0.47 (1.90) | 1.07 | 24/32 |
| g500 | +0.19 (2.83) | −0.03 (1.00) | 1.30 | 22/32 |
| g590 | +0.63 (2.72) | +0.22 (0.79) | 1.15 | 19/32 |

- **(a) The steps have different bases.**
  - The registered line is the nose step w3 → 3.4, but the speed arm is the host at w0 + speed.
  - A speed step pays differently on a steering host than on a non-steering one, so (nose − speed) mixes the step with the base.
  - **Fix:** add a speed arm at w3, and at w1, and compare each nose step with the speed step at the same base.
- **(b) Power.**
  - The per-season SD of the nose step is 2.39, so a per-host SE at 32 seeds is 0.42.
  - At 15 hosts, the t(14) half-width is about ±0.23. **The power for the nose step's own LB > 0 at the kinematic +0.17 is 0.31.**
  - (nose − speed) has a half-width of about ±0.28.
  - COMPARABLE is read from a non-rejection with no equivalence margin, so the expected reading is "TIED, NOSE STEP UNRESOLVED" whatever the truth.
  - **Fix:** use about 128 seeds per host (≈4× §B's compute: about 30 minutes a cell on 4 cores at 0.55 s a season) and state an equivalence margin, or register §B as descriptive.
- **(c) The damping step is not a +25% speed step.**
  - The realised ratio ranges from 0.49 to 1.32 across bodies. g300 is *slowed* by the lower damping, which likely unsettles its gait.
  - Damping ÷ 1.25 also lowers the casters' passive damping (`world.py:212`: passive joints take joint_damping × motor_strength × mass).
  - "Stated per unit of realised speed" is not defined: the formula, per host or pooled, and what happens to hosts at ratio ≤ 1.
  - **Fix:** define it now.

**G5. τ disagrees with RBT-116's MUST 5.** This is shared with the code.
- RBT-116's PREREGISTRATION (r7, `origin/results/RBT-116-design`, L85 and §4.2) names the transform the sweep consumes:
  - `tanh(G · (ln Σ_i − b_r))`, with **τ = 1 s**;
  - Σ_i the committed `_intensity` sum **+ 10⁻⁶**.
- The PR and the gate use **τ = 2 s** and **+ 10⁻¹²**.
- As registered, the gate validates a channel that RBT-116 will not run. The floor matters only when nothing is left standing; τ changes the temporal gain G·τ (and so the lone-nose route and motion gating, S2) by 2×.
- RBT-116 §4.2 also says "every nose reads 0 at spawn". With a per-robot baseline over several noses that is false: at spawn each nose reads its spatial offset, and only a lone nose reads 0.
- **Fix:** before reading, the coordinator rules on one τ. Either RBT-116 adopts 2 s (and fixes the spawn sentence), or the gate adds τ = 1 cells.

**G6. scipy.**
- `prize_readout.py` imports scipy at the top, and `steps.py` imports it in `t_int`. scipy is not a dependency (`pyproject.toml`: `dev = ["pytest>=7"]`), and the import fails in a clean `.[dev]` venv (`smoke_scripts.txt`).
- Under `set -e`, the first `prize_readout.py` call ends the script after the PW cells, so §B, §C and the committed layouts never run.
- `steps.py` runs inside `|| { …; mv …; }`, where errexit is suspended. A crash at its end would still `mv` a truncated `.tmp` over the output. The same holds for `side_effects.py`.
- **Fix:** confirm scipy in the gate venv, record its version in `launch.txt`, and use `&& mv`.

**G7. §C against the ticket and R10.**
- The ticket asks for "income, births, solvency"; R10 asks for "income, births, depth, saturation and solvency". §C measures income and solvency, solo, and nothing else. Births and depth need ecology runs.
  - **Fix:** state them as out of scope for this PR.
  - **Fix:** add **saturation.** Print the median and p90 of |c| per cell on the real bodies (the prize's bodies and §B's hosts). The G = 10 caveat rests on it.
  - `probe_spinner.txt` already shows a full-throttle rod's lone nose at |c| > 0.9 on **25–49% of ticks at G = 2.5** in U, so saturation is not only a G = 10 matter.
- **Coverage.** DESIGN §2 says "the gate's §C measures every row, both in the committed world and in PW". It does not:
  - the corpus has no PW condition;
  - `surface` and `clear_from = geoms` never run in PW;
  - the tumbler has no PW run under `sensor` or `surface`.

  Add the rows, or correct the sentence.
- **A redundant row.** The tumbler with "an unused food nose on its root, under `eat_from = sensor`" is identical to `root` by construction: `_eating_geoms` returns `[geoms[0]]` in both cases, and an unused sensor changes no motion. Confirmed: every season is identical, both arms × 3 seeds (`probe_tumbler_rows.txt`). It checks nothing that `root` does not. Say so, or put the nose on the arm, where it would test whether `sensor` taxes coverage.

### SHOULD

- **S1. The fallback is two shots** (G = 2.5, then G = 10), each one-sided at 2.5%. State the familywise α (≤ 5% one-sided), and keep reporting the G = 10 fallback as such.
- **S2. Motion gates the compass.**
  - DESIGN §1 says "the common temporal term cancels in L − R". It cancels only to first order.
  - The Pioneer's three noses share one baseline, so while the body moves along the gradient each wheel reads tanh(G(±Δx/2 + c)), with c the common lag (≈ τ·d ln S/dt). L − R is then scaled by about sech²(G·c).
  - `probe_motion.txt` (the real `_food_contrast` on a committed Pioneer carried kinematically; L − R moving ÷ static at the same pose):

    | G | v (m/s) | heading from the item | L − R moving ÷ static |
    |---|---|---|---|
    | 2.5 | 0.25 | 90° | 0.98 |
    | 2.5 | 0.25 | 45° | 0.73 |
    | 2.5 | 0.5 | 45° | **0.30** |
    | 10 | 0.25 | 90° | 0.91 |
    | 10 | 0.25 | 45° | **0.07** |
    | 10 | 0.25 | 135° | 0.22 |
    | 10 | 0.5 | 45° | **0.00** |

    At G = 10 the compass is blind while approaching food, and weak while leaving it. The G = 10 caveat is approach-speed gating, not just saturation of the per-nose contrast; audit C's kinematic numbers include this, but the DESIGN text does not.
  - **Fix:** correct the parity table's wheel row, and state the gating in the §A caveat.
  - The table's static "L − R ≈ 2·tanh(G·Δx/2)" is also exact only for a lone pair. On the Pioneer the baseline includes the chassis nose, 0.10 m behind, which adds a small fore–aft common offset.
- **S3. Zero inflation.** PW has 57–77% zero pairs on P-801, so every per-population harness verdict will read "VETOED by the zero count". Say in the readout that the per-population verdict is uninformative in PW, and that the gate is the across-population t bound, as registered.
- **S4. `check_decoy()`'s docstring says "on a legacy world, the patch changes nothing". Nothing asserts it:** at G = 0 the assertion is `reads differ`, which comes from `_intensity`. Add the assertion that G = 0 decoy readings are identical with and without the patch.
- **S5. The decoy rotation is keyed on (seed, gen) only** (`routed_populations.py:127`). All ten populations share one rotation per body slot and seed. This is harmless, but should be stated.

---

## Part 2. The code

### MUST

**C1. `clear_from = geoms` does not close the static-reach leak under `eat_rule = surface`.**
- The clearance measures from geom **centres** (`_clearance_points`, `simulation.py:494–500`). Surface eating reaches from geom **surfaces**.
- A limb longer than about 2 × (clearance − eat_radius) = 0.9 m has surface within reach of spots that are clear of its centre.
- `probe_static_reach.txt`: a **motors-off** rod, which cannot move, 20 seasons, in U:

  | arm (m) | centre, root | centre, geoms | surface, root | **surface, geoms** |
  |---|---|---|---|---|
  | 1.5 | 0.15 | 0.00 | 0.50 | 0.05 |
  | 3.0 | 0.20 | 0.00 | 1.15 | **0.40** |
  | 6.46 | 0.05 | 0.00 | 2.15 | **1.60** |

  Under `surface`, a motionless 6.46 m rod still eats 1.6 items a season with the "fixed" clearance. That is more than twice the blind tumbler's whole income, and exactly the free lunch `clear_from` exists to remove.
- **Fix:** when `eat_rule = surface`, measure the clearance with `_surface_distance` over the eating geoms (or all geoms). Add the motors-off rod as a test: 0 items under `surface` + `geoms`.

**C2. Pin both config strips together with a test.**
- The merge resolved the `to_dict` conflict correctly (`probe_strips.txt`: every combination writes exactly the families that are on, and round-trips).
- Nothing in the suite checks the combination: `test_rbt125.py` never sets `--motor-budget`, and `test_rbt120.py` never sets a perception flag.
- **Fix:** port `probe_strips.py` into `tests/test_rbt125.py`. It covers off/off, each alone and both on, on `EvolutionConfig.to_dict()` and `SimConfig.to_dict()`.

**(G5, shared.)** `smell_tau`'s default and the ln floor must match what RBT-116 consumes. Relatedly, `strip_default_perception` drops `smell_tau` whenever it equals 2.0, even with G > 0. A G = 2.5 run therefore writes a `config.json` that does not state its τ (`probe_strips.txt`, last line). If the default ever moves to RBT-116's 1 s, every such run silently changes meaning on reload. **Fix:** write `smell_tau` whenever `smell_contrast > 0`. The off case is unchanged.

### SHOULD

- **C3. `test_off_pioneer_bout_is_bitwise_the_default` is tautological.** It compares the current code at its defaults with the current code given the same defaults explicitly, never with the pre-pack code. The goldens carry the real proof. I also found the two trees equal on the gate's worlds (tree-parity probe). Rename the test, or compare against a digest recorded from 833ea9d^.
- **C4. The surface rule puts every item at z = 0.** On the committed random terrain (obstacles 0.03–0.30 m tall), a geom resting on an obstacle sits up to 0.3 m above an item beside it. Under `surface` its reach shrinks from 0.35 m to about 0.18 m in the plane, and under `centre` it does not. State the terrain bias in DESIGN §2, or use the item's terrain height.
- **C5. A lone nose is a saturated temporal detector at modest speed.**
  - In U at G = 2.5, G·τ·v/decay = 1.5 at 0.3 m/s. `probe_spinner.txt` shows a full-throttle rod's root nose at median |c| 0.28–0.90, and |c| > 0.9 on 26–49% of ticks.
  - The parity table presents the lone-nose route as "the temporal gradient, free". At these speeds it is closer to a sign detector.
  - This matters for M5's parity statement, since the favoured one-nosed (holistic) bodies get a mostly binary signal. Say so in §1.
- **C6. The level channel's deferral (scope).**
  - With G > 0, *every* food sensor loses the absolute level, including the evolved nose wiring that RBT-90 bodies already carry (P-801's g400/g500/g590 have their own a of −0.2 to −0.56).
  - In PW, "rich and not changing" is exactly the stay-in-patch cue.
  - The gate is unaffected, because the installed motif reads only L − R. But a negative from any sweep point with G > 0 can say only "*contrast-only* perception does not pay", not "perception does not pay".
  - **Fix:** DESIGN §4 should say this in those words, and RBT-129 should carry it into its registration.
- **C7. `clear_from = geoms` is not covered in `clear_spawn_layout`.** The gap is stated in §2 and is fine as stated. It is listed here only for completeness.

### Checked and fine

- **The EMA advances once per `sensor_values` call.** Only `Simulation.step` calls it; the gate's `check_decoy` also does, but on its own throw-away sims.
- **The baseline is advanced before the read.** The (1 − α) factor on (x − b_prev) is 0.99 at Δt = 0.02 s and τ = 2 s.
- **Parked items** (1e6) contribute exp(−1e6/decay) = 0. With nothing standing, the floor makes x constant, and every nose decays to 0 (the probe reads exactly 0).
- **Many noses cannot inflate the signal.** Each nose reads its offset from the noses' mean, so extra noses add no gain.
- **A nose on a fast Part** reads a large carrier, but only in proportion to real changes in ln S along its path. Its correlation with d ln S/dt is +0.23 to +0.52, and it is exactly 0 with no food. That is klinotaxis input, not a gamed baseline.
- **The eating rules against DESIGN §2's tumbler table.**
  - `root`: the arm no longer eats.
  - `sensor`: a noseless rod eats nothing, and a root nose restores exactly `root`.
  - `surface`: it raises a long sweeper's reach; C1 shows this already on a motionless rod.
  - All agree with the code. The magnitudes are §C's to measure.

---

## Probes and logs (`runs/RBT-125/adversary/`)

| file | what it does |
|---|---|
| `suite_clean_venv.log` | the full suite in a clean `pip install -e ".[dev]"` venv, no scipy: 456 passed |
| `smoke_scripts.py` / `.txt` | the gate scripts' imports, and one season in each §C condition. Shows `prize_readout` failing without scipy |
| `probe_decoy.py` / `.txt` | whether the decoy patch is needed and works in a fork pool, and whether `check_decoy()` catches a removed patch |
| `probe_tree_parity.py` / `.txt` | 0ec395f against c40ecd5 on the gate worlds: identical digest |
| `p801_PW-G2.5.txt`, `p801_PW-G0.txt` (+ `.err`) | the gate's wrapper on RBT-19 P-801, the §A instrument on a non-gate population |
| `probe_step_power.py` / `.txt` | §B's `bout()` on six committed Pioneers: step SDs, realised speed ratio and power |
| `probe_motion.py` / `.txt` | the Pioneer's L − R while moving against static: motion gating |
| `probe_spinner.py` / `.txt` | a nose on a spinning Part: saturation, information, and the reading with no food |
| `probe_static_reach.py` / `.txt` | a motors-off rod under every eat_rule × clear_from: the C1 leak |
| `probe_strips.py` / `.txt` | the RBT-120 and RBT-125 config strips together |
| `probe_tumbler_rows.txt` | §C's "root nose under `sensor`" tumbler row against its `root` row: identical, season for season (a one-liner over `side_effects.season`, run from `gate/`) |

Each probe runs from the repo root with the package's Python, `python runs/RBT-125/adversary/<probe>.py`. The
power probe needs scipy. The tree-parity probe runs once per tree, with `PYTHONPATH=<tree>` and cwd `<tree>`.
