# RBT-116 at W1: the code prerequisites, the gate runner, and the readings taken

*2026-10-04, the RBT-116 builder. The ruling: RBT-116 is ungated at **one** world point, **W1 exactly as registered**
(the coordinator, 2026-10-04, after the owner's decision). Everything else in `PREREGISTRATION.md` stands.*

**No RBT-116 output exists.** No arm, burn-in, gate cell, draw screen or battery has run on W1, its pool or any RBT-116
host. Every test uses fixture worlds and fixture bodies. The lanes are **emitted, not launched**: each refuses without
`RBT116_GATE_GO=1`.

## 1. Every prerequisite, and its status

Sources: §3.1 (the hooks), §3.2 (gated prerequisites), §8 (the fairness block), §11 (the scripts).

| prerequisite | where registered | status | how |
|---|---|---|---|
| `evolve --from-population KIND=DIR` | §3.1 hook 1 | **built here** | `evolution.load_population`; exactly as saved, the count must equal N; a start member that fails to build is replaced by a copy (§2.2), drawn by a fixed rng and reported in `from_population.json` |
| `evolve --save-every K` | §3.1 hook 2 | **built here** | `<kind>/gen<NNNN>/NNN.json` + `fitness.txt`, readable by hook 1 |
| `--smell-decoy rotate` | §3.1 hook 3 | **built here** | `FoodConfig.smell_decoy`, `Simulation._smell_food`: steer.py's decoy promoted (same θ stream, the clearance re-draw under every rule including #446's guard, the rotation-invariance refusal); tested equal to `steer.run_season(..., "decoy")` tick for tick |
| `--smell-decoy zero` (the lesion) | §3.1 hook 3; A1 item 5 | **exists** (RBT-130) | the flag maps to `FoodConfig.smell_lesion` |
| `evolve --crossover-rate R` | §3.1 hook 4; MUST 4 | **built here** | the CLI flag; `EvolutionConfig.crossover_rate` existed, and its coin is drawn at R = 0 too |
| `evolve --draws-final K` | §3.1 hook 5; R5-5 | **built here** | ranks k−5 … k+5 re-scored on K extra draws from their own stream (keyed on seed and generation: shared by both faunas and by U and N, and no other stream moves) |
| gear budget (RBT-120) | §3.2, §8 | exists | `--motor-budget 1.77`, in `--fair` |
| Effector-bias walk bounded in both operators | §3.2, §8 | exists | `--effector-bias-sigma` (RBT-124); `--fair` (RBT-128's ruled preset) **freezes** it at 0 |
| the smell transform, tanh(G·(ln Σ − b_r)), per-robot EMA, τ = 1 s, G = 2.5 | §4.2, A1 | exists (RBT-125) | `--smell-contrast 2.5 --smell-tau 1.0`, set explicitly in `world.py` (the code's default τ is 2.0); steer.py refuses another τ |
| `eat_from=root` (root = Node 0's first instance; Pioneer root = chassis) | §3.2, SHOULD 5 | exists (RBT-125) | `test_rbt125.py::test_the_pioneers_root_is_its_chassis` |
| `--eat-rule surface`, `--clear-from root` + #446's eating guard | A1 item 6, A3 item 2 | exists (RBT-125, #446) | in `world.py`'s W1 block |
| ball cone + hinge ranges | §3.2 (required) | exists (RBT-124) | in `--fair` |
| settle until rest (0.01 m/s) | §3.2 (required), §8 | exists (RBT-124) | in `--fair`; the cap is the code's 10 s (§8 says 5 s; `--fair` registers 10) |
| mass budget 15.34 | §8 | exists | in `--fair` |
| `outward_limbs` | §3.2 (wanted) | **missing** | not merged; §3.2 then requires per-member reporting (embedded pairs, recessive nodes, span, footprint): `readout.py`'s |
| `cap_on_reachable` | §3.2 (wanted) | **missing** | not ruled into `--fair` |
| `max_extent` 0.6 m | §3.2 (wanted) | **missing** | not merged |
| `clear_from=geoms` | §3.2 (wanted) | exists, **not used** | Amendment 3 registers `--clear-from root` |
| `--structural-rate-scale` | §3.2 | not in this wave | — |
| `steer.py` (the battery) | §1, §11 | exists (#434, #454) | untouched |
| G8 planters (a), (b), (d), (e) | §4.3 | exists (`planters.py`, RBT-132) | reused as RBT-129 ruled them |
| G8 planter (c) at RBT-116's grid | §4.3 G8(c) | **built here** | `gate.plant_c`: ±w per link, w ∈ {4, 16, 64}, 2 signs (planters.py splits a total a = 6, RBT-129's ruling) |
| G8 planter (f) | A2, A3 | **built here** | `gate.plant_f`; the registered planter test is `test_g8f_planter_steers_on_the_fixture_world` |
| G7's intermediates | MUST 6 | **built here** | `gate.plant_g7` |
| `world.py`, `gate.py` | §11 | **built here** | `runs/RBT-116/world.py`, `runs/RBT-116/gate/` |
| `power.py` at the gate's inputs | §7 | **built here** | `gate.power_rerun` (power.py itself untouched) |
| `readout.py`, `run_arm.sh`, the proposal assay | §5.2, §6, §11 | **missing** | arms-phase and readout-phase; not needed for the gate |

**Byte identity.** `hooks_identity.txt` holds digests printed on the pre-hook commit `2b57e39`. They cover two
`evolve` runs (RBT-113's truncation protocol in W1's block under `--fair`, and the competitive default): every file
they write. They also cover four W1 seasons. `test_hooks_off_are_byte_identical_to_the_pre_hook_code` re-runs them
with the hooks unset and set explicitly off. The digests are platform-specific: x86_64, mujoco 3.14.0, numpy 2.4.6.

**Carried, not done:** the coordinator's NIT on `steer.txt` (print `food_fallbacks`). `steer.py` is untouched here, so
W1's identity scripts and the RBT-116 kill-sets keep their reference.

## 2. The gate runner

`gate/gate.py CELL` covers every §4.3 row, through `steer.py`. `gate/lanes.py emit` writes the lane scripts and
`LANES.txt`. Waves:

| wave | lanes | cells |
|---|---|---|
| 0 | 8 × `b-<ARM>` | the 24 burn-ins B (the arms' first run; the gate needs their finals) |
| 1 | `gate-a`, `g6-noise`, `g5` | config, hosts, screen, G1 + G2, G8 (d)(e); σ_P; G5 timing under all three draws options |
| 2 | 6 × `g8`, 4 × `g4`, `g7`, 2 × `g9` | G8 (a)(b)(c)(f) on 192 hosts; G4 at 200 per fauna; G7; G9 |
| 3 | 8 × `g6u` | u_f: 40 children of every STEERS (a) and (c) plant |
| 4 | `g6-pilot` | G6's choice (cheapest passing option), the SHOULD 11 pilot and its probe |
| 5 | `readout` | `GATE.txt`: every row; `power.py` at the measured inputs (K by the R5-1 rule, SENS_C,H = min((c), (f)), plateaus at the chosen D); "the stronger no" |

## 3. Readings the registration leaves open (each a default, for the ruling)

- **H1, generation numbering.** "Generation g" = the population after g rounds of selection, evaluated. So B runs
  `--generations 13` and U and N run `--generations 49`, and generations 12, 24, 36 and 48 are saved and evaluated.
  That is 111 generations per unit against §9's 108. RBT-113's convention would make "generation 48" the 47th round.
- **H2, B's draws.** G6 measures σ_P on B's finals, so B runs before D is chosen. Default: D = 16, the registration's
  fallback. DF16 for B saves about 22 CPU-h.
- **H3, the screen's (a) rung.** The screen needs G8(a) plants before G1 names the first paying rung. Default:
  a = 6 (RBT-129's registered rung). G1 and everything after it run on the battery this screen admits.
- **H4, signing.** RBT-103's two direction probes (`planters.compass_sign`, which RBT-125 §B used), and both must
  agree. The `td` probe is `scripts/travel_direction.py`'s measure.
- **H5, G2.** The coverage gain is the mean blind (lesion) net, on the stage-2 draws, of the 16 G1 hosts, minus that
  of one RBT-113 U final from each G1 unit.
- **H6, G7.** The replication unit is the host: n = 16 host means, one-sided 95% t. The 256-pair bound is printed
  beside it. The lone nose is the left wheel's. The same-sign pair drives the steering axis. Outputs use ±w at the
  first paying rung (w = a/2), with routed.install's conventions.
- **H7, a flagged unit (G8).** A unit is flagged when it is short of hosts, has no (a) STEERS, has no (c) STEERS, or
  has a (b) STEERS. More than 4 flagged units means no launch.
- **H8, G9's members.** One member per unit per fauna per group, which keeps G9 near 1.5 CPU-h. The worlds:
  - HP: RBT-129's HP layout (3 patches, 0.6 m, 3 m disc, decay 1.0) with W1's other settings;
  - RBT-113's world: its own committed command line;
  - RBT-113's world with root surface eating, for SHOULD 6.
- **H9, G8(f)'s "sense that turns".** Of two senses, the common command to every one-sided Effector and opposite
  commands either side, the planter uses the one whose constant drive changes the root's net yaw more in one intact
  season. On the Pioneer it picks the common command, Amendment 3's steering axis.
- **H10, single-instance Nodes.** A Node's Sensor is expressed on every instance of that Node. So (c)'s two noses and
  (f)'s one nose are restricted to single-instance Nodes. This is the narrowing RBT-129 ruled (S4).
- **H11, the pilot's plants.** Unit 1's own (a) plants at every G1 rung and (c) plants at every w. The 8 per fauna with
  stage-2 F > 0 nearest F_MIN replace members 0–7. "Held" means a confirmed share ≥ 0.25 × that fauna's SENS: SENS_C,P,
  or SENS_C,H = min((c), (f)).
- **H12, G9's asymmetry.** For each census quantity, compare the relative move of the RBT-113 finals from RBT-113's
  world to W1 between faunas. A gap above 25 points is named "not the only difference".
- **H13, the G8(b) grid.** planters.py's q ∈ {0.2, 0.5} × k ∈ {2.5, 10} × the turn sign, with the brake fixed to the
  slowing sign (RBT-129's ruling). The registration names the axes only.
- **H14, DF16's s.** s is computed at D + K = 20 draws (the boundary). The plateau is computed by power.py's holding
  model at D = 20, which does not model a boundary-only re-ranking (an approximation, printed as such).
- **H15, the K rule's EPS.** power_rerun uses the larger fauna's measured EPS_C as the baseline. The registered cap row
  (0.05 against 0.01) is unchanged.
- **H16, a decoy season with no clear θ inside `evolve`.** `DecoyRefused` raises, so the run stops. The registration
  rules only the battery's case (excluded and counted). At W1's layout the adversary found 0 refusals in 612 draws.
- **H17, I3.** "U's and N's generation 0 are identical (names and fitness)" can hold for names only. N's decoy changes
  generation 0's evaluated fitness. This is the readout's to word.
- **H18, settle_max.** §8 says "cap 5 s". `--fair` registers 10 s (RBT-128), and W1 runs `--fair`.

## 4. Cost

Costed at 0.40 CPU-s per 15 s W1 season (0.37 measured here on `run_solo`); every number scales linearly. The full
tables are in `lanes/LANES.txt` (`lanes.py cost`).

- **The gate, after the burn-ins:** about 44 CPU-h on the priors (range 32–74). Of that, 26 CPU-h is **G6's u_f**: 40
  children, each called on the full battery, for each of about 67 STEERS (a)/(c) plants. The registration's "about
  12–14" did not price that. G8 is about 6, G4 about 3 and the pilot about 4.
- **The burn-ins** (the arms' B, which the gate needs first): 44 CPU-h at D = 16 (H2).
- **The arms** (24 units, including B at D = 16):

  | draws option | CPU-h | with B also at DF16 |
  |---|---|---|
  | D16 | ≈ 590 | — |
  | D8 | ≈ 423 | ≈ 401 |
  | DF16 | ≈ 431 | ≈ 410 |

  The registration's figures were 510, 330 and 310. The differences are 0.40 against 0.35 s per season, H1's +3
  generations, B at D = 16, and DF16's 672 seasons per generation against the 220 CPU-s §9 assumed.
