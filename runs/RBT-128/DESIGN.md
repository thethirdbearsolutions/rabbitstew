# RBT-128 design: the `--fair` preset and the missing-budget guard

**Designer, 2026-09-28.** This covers RBT-121 fix-list item 9 (`SYNTHESIS.md` R9; auditor D's R2). Its gates are
RBT-120 (the motor budget) and RBT-124 (the physics pack), and both are merged.

**Why.** The mass budget has been set by hand in 439 of 439 configs, so one forgotten flag reopens the original
artefact. The ruled fairness set is now six flags long (`--mass-budget` plus five from RBT-120 and RBT-124), and it
belongs in one flag with a guard behind it.

**Nothing here changes a committed result, and no run's behaviour changes except at start-up:**
- Resuming never meets the guard.
- A registered command line plus `--unfair-i-know` writes its old `config.json` byte for byte.
- `--fair` only fills in flags that already exist.

## Amendments after the design adversary (#438) and the ruling (02:17)

Verdict MERGE AFTER FIXES; `effector_bias_sigma` ruled **S = 0, in the preset**.

| item | change |
|---|---|
| M1 | §3 reworded: S = 0 freezes the **Effector-bias walk**, not resting throttle at the motor (the network still saturates 96.5% under selection; R1 bounds that work). Drift-only network share at G 150: 71.9% → 50.6% |
| M2 | `--effector-bias-sigma 0` is in `PRESET`, printed and written; `--fair --effector-bias-sigma 0.4` is refused |
| M3 | every fresh `ecology` and `evolve` run is guarded, `--only-fauna` included; resume still never meets the guard |
| S1 (MUST) | under `--fair`, an ecology `--shift` onto a preset field (`world.motor_budget`, `synthesis.mass_budget`, `world.ball_cone`, `world.hinge_range`) is refused |
| S2 | tests: an `ecology --fair` run writes the marker and every value; resuming a `--fair` run (`ecology` and `evolve`) keeps them |
| S3 | `fair.check(config) -> [deviations]`: the missing marker, each preset value that differs, a shift onto a preset field; RBT-129's stages.py calls it |
| S4 | `structural_rate_scale` and crossover alignment named as out of the preset (§1) |
| S5 | §3's holistic 19% reworded as a bias-only residual; no flag |
| N1–N3 | `--fair`'s help says a default-valued explicit flag becomes the preset's; the refusal says hand-given values still need `--fair`; a fairness flag on `--resume` prints that it is ignored |

## 1. `--fair`

`rabbitstew/fair.py`, `PRESET`. The flag is available on `evolve`, `ecology` and `simulate`.

| flag | value | ruled by |
|---|---|---|
| `--mass-budget` | 15.34 | the follow-up paper (the Pioneer's 15.337 kg) |
| `--motor-budget` | 1.77 | RBT-120 (#409/#410) |
| `--ball-cone` | π/2 (1.5707963267948966) | RBT-124 (#420): registered together with the budget (F1) |
| `--hinge-range` | π/2 | RBT-124: set together with the cone |
| `--settle-until-rest` | 0.01 | RBT-124 (ε 0.01 m/s) |
| `--settle-max` | 10 | RBT-124 (cap 10 s) |
| `--effector-bias-sigma` | **0** | **ruled 02:17** (#432): it freezes the Effector-bias walk (§3); it does not bound resting throttle |
| `cap_on_reachable` | **left out** | not ruled in; there is no such flag yet (RBT-121 fix list item 10) |
| `--structural-rate-scale` | **left out** | not ruled in; R6 is met by stating the operators, as RBT-129 does |
| crossover alignment | **left out** | not ruled in (fix list item 10) |

**Behaviour:**
- **Expansion.** Every preset flag the command line left unset takes the preset's value.
  - A flag set explicitly to a **different** value is refused (`error: --fair sets --mass-budget 15.34 (got 20.0)`). The preset is a registration, not a default to be half-overridden.
  - A flag set explicitly to the **same** value is accepted.
  - Flags outside the preset, such as `--effector-bias-sigma 0`, stay the registrant's own.
- **Printed.** `--fair expands to: --mass-budget 15.34 --motor-budget 1.77 --ball-cone 1.5707963267948966 --hinge-range 1.5707963267948966 --settle-until-rest 0.01 --settle-max 10 --effector-bias-sigma 0`.
- **Written.** Each value lands in `config.json` where its own flag would put it. `"fairness": "fair"` is added at the top level, so the register records how the values got there.
- **Scope.** RBT-125's perception and eating rules (`--smell-contrast`, `--eat-from`, `--eat-rule`, `--clear-from`) are **world** settings, not body fairness, and stay out of the preset. So do RBT-126's breeding flags and RBT-130's `--obstacle-radius`. All of them compose with `--fair` (tested).

## 2. The guard

- **Where it applies.** `evolve` (which always runs both faunas), `ecology`, and a `simulate` bout refuse to start a run that mixes the holistic and designed faunas with neither `--fair` nor `--unfair-i-know`.
  - The ticket's "`bout`" is `simulate` with two genotypes. There is no separate `bout` command.
  - `evolve`'s arena champion bouts run inside `evolve`, so the `evolve` guard covers them.
- **What it prints.** The refusal names the preset's flags and R9's reason. Nothing is written: the run directory gets no `config.json`.
- **What counts as mixed.**
  - `evolve`: always.
  - `ecology`: always, **`--only-fauna` included** *(amended per the adversary's M3)*: an only-fauna run's seasons are
    its half of a two-fauna run and are read against `--fair` arms (RBT-129's retention layer), so it must carry the
    same physics.
  - `simulate`: when its genotypes include both a designed body plan (the Pioneer's or the quadruped's, whatever the controller: `fair.is_designed`, on `genetics.body_plan`) and any other. A bout between two holistic bodies, between two Pioneers, or a solo run is exempt.
- **The bypass.** `--unfair-i-know` starts the run with only the flags given, as every run before RBT-128 did, and prints a warning. **It writes nothing extra**, so an old registered command line plus the bypass reproduces its old `config.json` (tested on RBT-113 O1/3/D's committed config).
- **Resume is exempt.** `evolve --resume` and `ecology --resume` return before the guard. A `config.json` with no fairness key (every config before RBT-128) loads and writes itself back byte for byte. This is tested on RBT-113 O1/3/D and on an RBT-120 B arm (B4/11/D, which sets `--motor-budget` alone), and a bypassed run resumes with no flag at all.
- **Programmatic use is not guarded.** `evolve_config`, `Experiment` and `Ecology` are unchanged. The goldens, the readouts, `runs/*/world.py` and the probes build configs this way, so all of them are untouched. The guard protects the command line, which is where the 439 configs came from.

**One consequence to register.** A historical launch script (`runs/*/run_arm.sh` and similar) that is re-run fresh **on this tree** now stops at the guard. It must add `--fair` or `--unfair-i-know`, or be run from its own commit. Its resumes are unaffected. No run registered today is mid-launch from such a script to my knowledge; RBT-120's B arms are complete (#429).

## 3. `--effector-bias-sigma 0`: ruled into the preset (02:17), for a narrower reason than this section first gave

**What S = 0 does: it freezes the Effector-bias walk.** Every Effector keeps its founding bias; every other gene,
neuron biases and link weights included, mutates exactly as before (the same one draw, so the stream is unchanged).

**What S = 0 does not do: it does not bound resting throttle at the motor.** *(Corrected per the adversary's M1; the
first draft's tables measured the Effector bias, not the motor.)* A motor's resting throttle is the Effector's output
with the sensors quiet, `clip(Σ tanh(bias + W·activation))`: a neuron with no input outputs a constant, and through a
link that constant is an Effector bias by another name. The adversary's `effective_drive.txt` reads the throttle from
the network (the same founders, truncation and seeds as `bias_select.py`):
- **Under selection for resting drive, S = 0 changes nothing about throttle**: the designed body's network saturates
  **96.5%** of its driven DOFs by G 23 at S = 0, against 97.7% unset (98.0% with G = 0 as well), while the bias-only
  share stays at 0%. What bounds that work is **R1** (the motor budget, now in the preset) and the work price, not S.
- **Under drift alone, S = 0 removes a real part of the walk**: the designed body's network share at G 150 falls from
  **71.9% to 50.6%** (founding 28.7%); the holistic body's from 34.4% to 19.6%.
- **It protects a sensor-driven response**: a walked Effector bias pins its tanh and masks its input. Under drift the
  food-sensor→motor gain erodes less at S = 0 (0.129 against 0.089 at G 150; the adversary's `steer_route.txt`), and
  under selection the steering route is as open at S = 0 as unset.

So the preset carries S = 0 because every registration it serves prices work (RBT-129's sweep does at every point),
and an open Effector walk is unselected drift and masking on top; the claim is "the Effector walk is frozen", not
"resting throttle is closed". **RBT-129 §12.1's premise needs that one-line amendment** (flagged to the coordinator).

**The bias-only evidence (first draft), kept for the record.** It shows what S does to the gene. Both tables use the same stream as RBT-121's `bias_walk.py`: 80 lineages walked by the operator alone. The values are the share of Effectors at resting drive, |tanh(bias)| > 0.9. Sources are RBT-124's `bias_walk_s0.txt` (unset and S = 0) and this ticket's `bias_walk_s.txt`.

Designed body:

| S | G 23 | G 60 | G 150 |
|---|---|---|---|
| unset (= N(0, 0.4)) | 16.9% | 27.5% | **54.4%** |
| 0.2 | 3.8% | 8.8% | 25.0% |
| 0.1 | 1.2% | 1.9% | 8.8% |
| 0.05 | 0.0% | 0.6% | 2.5% |
| **0** | **0.0%** | **0.0%** | **0.0%** |

Holistic body:

| S | G 23 | G 60 | G 150 |
|---|---|---|---|
| unset (= N(0, 0.4)) | 8.1% | 18.2% | **26.1%** |
| 0.2 | 2.4% | 5.7% | 8.0% |
| 0.1 | 1.5% | 1.1% | 1.3% |
| 0.05 | 0.9% | 0.0% | 0.1% |
| **0** | **0.9%** | **0.0%** | **0.1%** |

- **The drift alone** (no selection) saturates 54% of the designed body's motors by G 150 unset. S = 0.1 cuts that to 9%, S = 0.05 to 2.5%, and S = 0 to none.
- **Under directional selection, a bounded S only delays saturation; S = 0 stops it** (`bias_select.py` →
  `bias_select.txt`). This is a planted positive: RBT-113's truncation scheme (the top 10 of 40, 23 rounds, 5
  replicates) run on the operator alone, selecting **for** resting drive, the direction RBT-113's D line took through
  work. Resting-drive share at G 6 / 12 / 23:

  | S | designed | holistic |
  |---|---|---|
  | unset | 69% / 100% / 100% | 46% / 91% / 89% |
  | 0.2 | 27% / 89% / 100% | 5% / 89% / 88% |
  | 0.1 | 1% / 53% / 100% | 3% / 42% / 91% |
  | 0.05 | 0% / 0.2% / **51%** | 0% / 9% / **89%** |
  | **0** | **0% / 0% / 0%** | 4% / 17% / **19%** |

  - Even S = 0.05 lets selection saturate half the designed body's motors, and nearly all the holistic body's, within
    RBT-113's 23 rounds.
  - At S = 0 the designed body's **Effector biases** cannot move at all (its throttle can: see above). The holistic
    fauna's bias-only share still reaches 19%, through newborn Effectors (N(0, 0.5)) and copies of the founders'
    saturated ones spread by node duplication. **That residual is on the gene, not the motor** (adversary S5): under
    throttle-targeted selection it is 4.6%, zeroing newborn biases leaves 5.3% (the copies carry it) and changes
    nothing on the throttle, so no flag is added.
- **What S = 0 costs.** The Effector's own bias is fixed at founding, N(0, 0.5) per Effector. The motor's resting throttle is not fixed: the network still sets it through neurons and weights (above).
  - This is the designed body's control space minus one redundant offset per motor, and the same holds for the holistic fauna, so the two faunas stay at parity (B: the flag binds both).
- **Ruled (02:17): S = 0, in the preset.** An explicit `--fair --effector-bias-sigma 0.4` is refused (tested).

## 4. Tests (`tests/test_rbt128.py`, 17)

| test | what |
|---|---|
| preset is the ruled set | exactly the six (dest, value) pairs; `effector_bias_sigma` and `cap_on_reachable` absent |
| expands to exactly the listed flags | `--fair`'s config = the config with the six flags given explicitly, plus `fairness`; against the bare config it differs in exactly those keys (bare and RBT-113's command line); it round-trips |
| ecology and simulate | the preset applies on both |
| conflicts | a different explicit value is refused, a matching one accepted, `--fair` with `--unfair-i-know` refused; `--effector-bias-sigma 0` composes |
| printed and written | the expansion line is printed; `config.json` carries the values and `"fairness": "fair"` |
| the guard fires | `evolve`, `ecology`, a holistic-vs-Pioneer `simulate` bout; no `config.json` is written |
| the guard is bypassed | `--unfair-i-know` (with a warning) and `--fair`; exempt: two holistic bodies, two Pioneers, a solo run; `ecology --only-fauna` is guarded (M3) |
| `is_designed` | the Pioneer (rich) and the quadruped yes; 20 random bodies no |
| the bypass writes the old config | RBT-113's registered command line + `--unfair-i-know` builds RBT-113 O1/3/D's committed `config.json`, key for key |
| old configs replay | RBT-113 O1/3/D and RBT-120 B4/11/D load and write themselves back byte for byte (no fairness key) |
| resume needs no flag | a bypassed run resumes with no fairness flag; its config changes only in the extended horizon |
| ecology marker and resume (S2) | a 2-season `ecology --fair` writes the marker and every value (`fair.check` = []); `--resume` keeps them and notes the ignored flag; an `evolve --fair` run resumes fair |
| shift refusal (S1) | under `--fair`, `--shift` onto `world.motor_budget`, `synthesis.mass_budget`, `world.ball_cone` or `world.hinge_range` is refused and nothing is written; a world shift (`food.work_cost`) is allowed; the bypass allows anything |
| `fair.check` (S3) | [] on a `--fair` config; names a missing marker, a changed budget, an unset S, a shift onto a preset field; a pre-fairness RBT-113 config fails it |
| composes with every strip | `--fair` + RBT-125 smell/eating + RBT-130 obstacle radius + RBT-126 breeding: every strip's value is written, and `--fair` touches none of them |

The pre-RBT-128 CLI tests that start a mixed run from the command line (`test_cli`, `test_morph_protection`,
`test_rbt126`, `test_rbt130`) now pass `--unfair-i-know`. Their byte-identity assertions still hold because the bypass
writes nothing.

**Full suite: 615 passed** (a clean `.[dev]` venv: Python 3.11.15, x86_64, mujoco 3.14.0, numpy 2.4.6), after merging integration at 76d97d4 (the adversary's #438).

## Files

- **`rabbitstew/fair.py`** (new): `PRESET`, `CONFIG_PATH`, `expand`, `announce`, `note_resume`, `shift_on_preset`, `check`, `is_designed`, `guard`.
- **`rabbitstew/cli.py`:**
  - `--fair` and `--unfair-i-know` on `evolve`, `ecology` and `simulate`;
  - expansion in `evolve_config`, `cmd_ecology` and `cmd_simulate`;
  - the guard in `cmd_evolve`, `cmd_ecology` and `cmd_simulate`.
- **`rabbitstew/evolution.py`:** `EvolutionConfig.fairness`, dropped from `config.json` when empty.
- **`tests/test_rbt128.py`**, plus `--unfair-i-know` added to four pre-RBT-128 CLI tests.
- **`runs/RBT-128/bias_walk_s.py`** → **`bias_walk_s.txt`** (drift alone) and **`bias_select.py`** → **`bias_select.txt`** (under selection): the S = 0 item's evidence.
