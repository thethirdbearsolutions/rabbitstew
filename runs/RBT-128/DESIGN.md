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
| `--effector-bias-sigma` | **unset: [OPEN]** (§3) | to be ruled before merge |
| `cap_on_reachable` | **left out** | not ruled in; there is no such flag yet |

**Behaviour:**
- **Expansion.** Every preset flag the command line left unset takes the preset's value.
  - A flag set explicitly to a **different** value is refused (`error: --fair sets --mass-budget 15.34 (got 20.0)`). The preset is a registration, not a default to be half-overridden.
  - A flag set explicitly to the **same** value is accepted.
  - Flags outside the preset, such as `--effector-bias-sigma 0`, stay the registrant's own.
- **Printed.** `--fair expands to: --mass-budget 15.34 --motor-budget 1.77 --ball-cone 1.5707963267948966 --hinge-range 1.5707963267948966 --settle-until-rest 0.01 --settle-max 10`.
- **Written.** Each value lands in `config.json` where its own flag would put it. `"fairness": "fair"` is added at the top level, so the register records how the values got there.
- **Scope.** RBT-125's perception and eating rules (`--smell-contrast`, `--eat-from`, `--eat-rule`, `--clear-from`) are **world** settings, not body fairness, and stay out of the preset. So do RBT-126's breeding flags and RBT-130's `--obstacle-radius`. All of them compose with `--fair` (tested).

## 2. The guard

- **Where it applies.** `evolve` (which always runs both faunas), `ecology`, and a `simulate` bout refuse to start a run that mixes the holistic and designed faunas with neither `--fair` nor `--unfair-i-know`.
  - The ticket's "`bout`" is `simulate` with two genotypes. There is no separate `bout` command.
  - `evolve`'s arena champion bouts run inside `evolve`, so the `evolve` guard covers them.
- **What it prints.** The refusal names the preset's flags and R9's reason. Nothing is written: the run directory gets no `config.json`.
- **What counts as mixed.**
  - `evolve`: always.
  - `ecology`: unless `--only-fauna` is set (RBT-130: one fauna's half of a run).
  - `simulate`: when its genotypes include both a designed body plan (the Pioneer's or the quadruped's, whatever the controller: `fair.is_designed`, on `genetics.body_plan`) and any other. A bout between two holistic bodies, between two Pioneers, or a solo run is exempt.
- **The bypass.** `--unfair-i-know` starts the run with only the flags given, as every run before RBT-128 did, and prints a warning. **It writes nothing extra**, so an old registered command line plus the bypass reproduces its old `config.json` (tested on RBT-113 O1/3/D's committed config).
- **Resume is exempt.** `evolve --resume` and `ecology --resume` return before the guard. A `config.json` with no fairness key (every config before RBT-128) loads and writes itself back byte for byte. This is tested on RBT-113 O1/3/D and on an RBT-120 B arm (B4/11/D, which sets `--motor-budget` alone), and a bypassed run resumes with no flag at all.
- **Programmatic use is not guarded.** `evolve_config`, `Experiment` and `Ecology` are unchanged. The goldens, the readouts, `runs/*/world.py` and the probes build configs this way, so all of them are untouched. The guard protects the command line, which is where the 439 configs came from.

**One consequence to register.** A historical launch script (`runs/*/run_arm.sh` and similar) that is re-run fresh **on this tree** now stops at the guard. It must add `--fair` or `--unfair-i-know`, or be run from its own commit. Its resumes are unaffected. No run registered today is mid-launch from such a script to my knowledge; RBT-120's B arms are complete (#429).

## 3. [OPEN] `--effector-bias-sigma`: a proposal, not in the preset

**Proposal: S = 0 (freeze the Effector biases) for any registration that reads work or throttle.** A bounded S (0.05) only slows the walk under selection (below), so it is not a real alternative for such registrations.

**Evidence.** Both tables use the same stream as RBT-121's `bias_walk.py`: 80 lineages walked by the operator alone. The values are the share of Effectors at resting drive, |tanh(bias)| > 0.9. Sources are RBT-124's `bias_walk_s0.txt` (unset and S = 0) and this ticket's `bias_walk_s.txt`.

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
  - At S = 0 the designed body cannot move at all. The holistic fauna still reaches 19% through **newly drawn
    Effectors**: a born Effector's N(0, 0.5) bias is selected like any other new gene. That is a gene's birth, not the
    walk (RBT-124 §2.2), and it is bounded by the founding spread.
- **What S = 0 costs.** The resting throttle is then fixed at founding, N(0, 0.5) per Effector. A body can still hold a motor on through its sensors and neurons: the Effector's input is unaffected, and the global and segment neurons' biases still mutate.
  - This is the designed body's control space minus one redundant offset per motor, and the same holds for the holistic fauna, so the two faunas stay at parity (B: the flag binds both).
- **Recommendation for the ruling:** put `--effector-bias-sigma 0` in the preset for registrations that read work, throttle or the D line, i.e. every RBT-113-shaped design. Until ruled, the preset leaves it unset, and a registration may pass it explicitly (tested: it composes with `--fair`).

## 4. Tests (`tests/test_rbt128.py`, 13)

| test | what |
|---|---|
| preset is the ruled set | exactly the six (dest, value) pairs; `effector_bias_sigma` and `cap_on_reachable` absent |
| expands to exactly the listed flags | `--fair`'s config = the config with the six flags given explicitly, plus `fairness`; against the bare config it differs in exactly those keys (bare and RBT-113's command line); it round-trips |
| ecology and simulate | the preset applies on both |
| conflicts | a different explicit value is refused, a matching one accepted, `--fair` with `--unfair-i-know` refused; `--effector-bias-sigma 0` composes |
| printed and written | the expansion line is printed; `config.json` carries the values and `"fairness": "fair"` |
| the guard fires | `evolve`, `ecology`, a holistic-vs-Pioneer `simulate` bout; no `config.json` is written |
| the guard is bypassed | `--unfair-i-know` (with a warning) and `--fair`; exempt: two holistic bodies, two Pioneers, a solo run, `ecology --only-fauna` |
| `is_designed` | the Pioneer (rich) and the quadruped yes; 20 random bodies no |
| the bypass writes the old config | RBT-113's registered command line + `--unfair-i-know` builds RBT-113 O1/3/D's committed `config.json`, key for key |
| old configs replay | RBT-113 O1/3/D and RBT-120 B4/11/D load and write themselves back byte for byte (no fairness key) |
| resume needs no flag | a bypassed run resumes with no fairness flag; its config changes only in the extended horizon |
| composes with every strip | `--fair` + RBT-125 smell/eating + RBT-130 obstacle radius + RBT-126 breeding: every strip's value is written, and `--fair` touches none of them |

The pre-RBT-128 CLI tests that start a mixed run from the command line (`test_cli`, `test_morph_protection`,
`test_rbt126`, `test_rbt130`) now pass `--unfair-i-know`. Their byte-identity assertions still hold because the bypass
writes nothing.

**Full suite: 611 passed** (a clean `.[dev]` venv: Python 3.11.15, x86_64, mujoco 3.14.0, numpy 2.4.6), after merging integration at 626ca4c.

## Files

- **`rabbitstew/fair.py`** (new): `PRESET`, `expand`, `announce`, `is_designed`, `guard`.
- **`rabbitstew/cli.py`:**
  - `--fair` and `--unfair-i-know` on `evolve`, `ecology` and `simulate`;
  - expansion in `evolve_config`, `cmd_ecology` and `cmd_simulate`;
  - the guard in `cmd_evolve`, `cmd_ecology` and `cmd_simulate`.
- **`rabbitstew/evolution.py`:** `EvolutionConfig.fairness`, dropped from `config.json` when empty.
- **`tests/test_rbt128.py`**, plus `--unfair-i-know` added to four pre-RBT-128 CLI tests.
- **`runs/RBT-128/bias_walk_s.py`** → **`bias_walk_s.txt`** (drift alone) and **`bias_select.py`** → **`bias_select.txt`** (under selection): the [OPEN] item's evidence.
