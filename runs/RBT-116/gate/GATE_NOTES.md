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
| `--smell-decoy rotate` | §3.1 hook 3 | **built here** | `FoodConfig.smell_decoy`, `Simulation._smell_food`: steer.py's decoy promoted. It uses the same θ **stream**, keyed on the start seed alone and so shared by both faunas and by U and N. The θ **accepted** is the stream's first candidate that clears the season's clearance points, so it can differ between bodies (steer.py N2). It includes the clearance re-draw under every rule (#446's guard too) and the rotation-invariance refusal. Tested equal to `steer.run_season(..., "decoy")` tick for tick |
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
| G8 planter (f) | A2, A3 | **built here** | `gate.plant_f`; the registered planter test is `test_g8f_planter_steers_on_the_fixture_world`, and the `fixture` cell repeats it at run time: every later cell refuses without its PASS |
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

## 3. Readings, as ruled

The coordinator ruled these on 2026-10-05 (COORDINATOR-EXPOSED, pre-data), on the #540 adversary's recommendations
(verdict MERGE WITH FIXES). The code follows the rulings.

| | reading | ruling | in the code |
|---|---|---|---|
| H1 | "Generation g" = the population after g rounds of selection, evaluated. B runs `--generations 13`, U and N `--generations 49`; generations 12, 24, 36 and 48 are saved and evaluated | **accepted**: generation 48 is literal; §9 re-costed at 111 generations per unit | `world.py`; `lanes.py cost` |
| H2 | B's draws, fixed before G6 can choose D | **accepted**: B at D16. **I2 is amended to read** "B, U and N differ only in `--smell-decoy` and `--from-population`, and, if G6 chooses another D, `--draws`/`--draws-final`" | `world.B_DRAWS_OPTION` |
| H3 | The screen's G8(a) plants are built at a = 6, before G1 names the first paying rung | **accepted**; a note is printed if the first paying rung is not 6 | `g1` prints `NOTE (H3)`, carried into GATE.txt |
| H4 | Signing by RBT-103's two direction probes (`planters.compass_sign`), both of which must agree | **accepted**; the UNDETERMINED refusals are printed per unit | `designed_hosts`; the `hosts` cell prints every refusal |
| H5 | G2's coverage gain | **CHANGED**: food against food (F is in items, so the gain is blind *food*), and both sides' hosts picked the same way (the hosts rule: the permutation, the motif, both probes agreeing) | `_blind` (food); `designed_hosts` on the RBT-113 side too |
| H6 | G7's replication unit is the host (n = 16 host means), with the 256-pair bound beside it | **accepted**; the full rungs × intermediates table is printed (finding 8). The pass/fail is read at the first paying rung | `_g7_host` runs every rung; `g7_summary`'s `table` |
| H7 | A G8 unit is flagged when it is short of hosts, has no (a) STEERS, has no (c) STEERS, or has a (b) STEERS | **accepted**; each flag's reason is printed per unit | the readout |
| H8 | G9's members (one per unit per fauna per group) and worlds | **accepted**; the readout states that HP uses RBT-129's `regrow_delay` of 0 | the readout |
| H9 | G8(f)'s "sense that turns" is measured per host | **accepted**; the chosen sense is recorded per host | `hosts/unitNN.json` `f_pattern`; printed by `hosts` and `g8` |
| H10 | (c)'s and (f)'s noses are restricted to single-instance Nodes | **accepted** | — |
| H11 | The pilot's plants | **accepted**, conditional on F1; **amended by RBT116-PILOT-10** (below) | `pilot-prep` |
| H12–H15 | G9's 25-point asymmetry rule; the G8(b) grid; DF16's s and plateau at D = 20; the K rule at the larger measured EPS_C | **accepted**; the "approximation" print is kept (H14) | `g6-pick` prints it |
| H16 | A decoy season with no clear θ inside `evolve` raises `DecoyRefused` and stops the run | **accepted**; the lane reports the stop for a ruling | `evolve_run` exits 8 with `STOPPED FOR A RULING (H16)` |
| H17 | I3 | **accepted, reworded**: "U's and N's generation 0 are identical in **names and worlds**", not fitness (N's decoy changes generation 0's evaluated fitness) | for `readout.py` (not built) |
| H18 | settle_max | **10 s**, RBT-128's preset (already in W1_SIM_HASH); §8's "5 s" is superseded | `--fair` |
| H19 (new) | The Effector-bias walk | **ruled explicitly: frozen at σ = 0** (the `--fair` preset), in both faunas | `--fair` |

**H11 amended: ruling RBT116-PILOT-10** (the coordinator, 2026-10-05 about 05:30Z, COORDINATOR-EXPOSED).

**When and on what knowledge.** The ruling came after the gate's W4 `pilot-prep` refused (exit 10, about 05:27Z). It
was made knowing only that the refusal happened: neither the count nor the fauna was known to the coordinator or to the
builder, and neither read the log line. The design options were put to the adversary before acting.

**Why H11 refused.** The refusal came from the builder's reading H11, not from the registration. H11 drew the 8
planted steerers only from PILOT_UNIT's own hosts, and F3 interacts with it: after F3, a unit-1 holistic host that
cannot carry (c) contributes no candidates. With two or fewer carrying hosts, the holistic list held at most 6, so the
refusal was certain whatever F was.

**D, the amended rule.**
- The candidates per fauna are every unit's plants that already have a recorded stage-2 F. No new season is run, and
  nothing is refitted or re-tuned (`gate.pilot_candidates`):
  - designed: every G8(a) plant in the g8 records (each host's, at the first paying rung), plus every G1 plant in
    `g1.json` (the 16 G1 hosts at every rung);
  - holistic: every G8(c) plant in the g8 records (each carrying host's tuned build).
- Excluded: a host that cannot carry (c) (F3), and a plant whose call stopped before stage 2, since neither has a
  recorded F.
- **Both pools require a call that reached stage 2** (M1, the #555 adversary). `g1.json` records an F for every G1
  call, including those stopped at stage 1, so its G1 plants are filtered on their call, as the G8 pool's are.
- Candidates are keyed by (unit, host, rung or w), never by name, because host names repeat across units.
- The 8 with F > 0 nearest F_MIN are taken, ties broken by that key in order (`gate.pick_pilot`). They replace members
  0–7 of PILOT_UNIT's B generation-12 population, as before.
- The 24 generations of U at the chosen D, and the probe, are unchanged.

**A, the fallback.** Both faunas are counted first. If either has fewer than 8 paying candidates:
- `pilot.json` records `{"refused": true, "paying": {…}}` and pilot-prep exits 0;
- nothing is planted, the lane's evolve step is a no-op (`pilot_command`), and pilot-probe leaves the record alone;
- that no-op still passes through the lane's `evolve_run`. It creates `pilot/run/` holding only `command.txt` and
  `run.log`, and saves it as a harmless `ckpt/rbt-116-w1-gate-pilot-run`. A later real run restores it, finds no
  `state.json`, and wipes the directory before launching;
- the readout sets `conditional_sentence`, with "the holding pilot could not be built". That is the registered
  "Otherwise" of SHOULD 11: it never helps HOLISTIC and changes no pass/fail row.

The readout still refuses on a **missing** `pilot.json` (F10).

**The fixes, F1–F11** (the adversary's list, as the coordinator relayed it):

- **F1.** The G6 pilot is not a pass/fail row. An unheld steerer sets `conditional_sentence` in `gate.json`, and the
  readout refuses (non-zero exit) without `pilot.json`.
- **F2.** There is no fallback K. If no K in 3..9 meets R5-1's rule, the readout prints the table and exits 13 for a
  ruling.
- **F3.** The 4 holistic hosts per unit are the permutation's first 4, whatever they carry.
  - A host that cannot carry (c) counts as NONE for (c).
  - (f) runs on all 4, with its own layout: the one-sided Effector Nodes, without (c)'s two-nose requirement.
  - Refusals are printed per unit.
- **F4.** `evolve_run` accepts only exit 3 ("no checkpoint") from a restore. Any other failure exits 7 with REFUSED.
- **F7a.** Each lane pins `HEAD:rabbitstew` and the blob of every script `gate.py` loads, found by importing it, plus
  RBT-113's `world.py` and `lanes.py`.
- **F7b.** The last step before the GO is to re-emit the lanes (`lanes.py emit`) on the final merged tree and commit
  them. `LANES.txt` says so.
- **F10.** The readout refuses on any missing input (G9, G5 under every option, the pilot). `g6-pick` refuses without
  every option's G5 timing. Tuning excludes a draw whose decoy finds no clear θ (`gate.tune`).
- **F11.** The crossover test compares `rng.bit_generator.state` at R = 0 and at R = 1e-300.
- **Notes.**
  - This docstring now covers H1–H19.
  - The "same θ" wording is corrected (§1).
  - `g1_decide`'s unused argument is gone.
  - The `fixture` cell is the run-time G8(f) check.

## 4. Cost

Costed at 0.40 CPU-s per 15 s W1 season (0.37 measured here on `run_solo`); every number scales linearly. The full
tables are in `lanes/LANES.txt` (`lanes.py cost`).

- **The gate, after the burn-ins:** about 45 CPU-h on the priors (range 32–75). Of that, 26 CPU-h is **G6's u_f**: 40
  children, each called on the full battery, for each of about 67 STEERS (a)/(c) plants. The registration's "about
  12–14" did not price that. G8 is about 6, G4 about 3, the pilot about 4, and G7 about 0.9 now that it covers every
  rung (finding 8). The fixture check is about 0.1.
- **The burn-ins** (the arms' B, which the gate needs first): 44 CPU-h at D = 16 (H2).
- **The arms** (24 units, including B at D = 16):

  | draws option | CPU-h | with B also at DF16 |
  |---|---|---|
  | D16 | ≈ 590 | — |
  | D8 | ≈ 423 | ≈ 401 |
  | DF16 | ≈ 431 | ≈ 410 |

  The registration's figures were 510, 330 and 310. The differences are 0.40 against 0.35 s per season, H1's +3
  generations, B at D = 16, and DF16's 672 seasons per generation against the 220 CPU-s §9 assumed.
