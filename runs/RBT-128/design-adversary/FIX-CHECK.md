# RBT-128 FIX-CHECK: #432 at f8f903e

**Verdict: MERGE.**
- Every MUST and SHOULD of `ADVERSARY.md` is closed as the 02:44 ruling set them: M1–M3, S1 (upgraded to MUST) and
  S2–S5.
- The new tests kill 18 of 19 targeted mutants. The survivor is a tolerance nit (F-N1).
- Three NITs remain, none blocking. They can ride any later push.

**Scope.** I checked f8f903e trial-merged with integration c904de1. Integration has since moved to 3d8bb6e, whose
commits after c904de1 touch neither `rabbitstew/` nor `tests/`.

**Evidence** (in this directory):
- `fc_probe.py` → `fc_probe.txt`: the guard, resume, `check`, the shift refusal and S = 0;
- `fc_mutants.py` → `fc_mutants.txt`: 19 mutants of the fixes, run against the PR's tests;
- `fc_suite.txt`: the full suite.

The runs are tiny (≤ 3 seasons or generations, 0.2 s bouts). Nothing here is a registered result.

## The five asks

**(1) Each item is closed, and the new tests kill the mutants of the fixes** (`fc_mutants.txt`).

| item | fix at f8f903e | mutant(s) | result |
|---|---|---|---|
| M1 | DESIGN §3 reworded: S = 0 freezes the Effector-bias walk and does not bound throttle. The amendments table carries the numbers; the code comment on `PRESET` says the same | (text) | closed |
| M2 | `("effector_bias_sigma", 0.0, "--effector-bias-sigma 0")` is in `PRESET`, with `_UNSET` None | dropped; S = 0.05; not printed; `_UNSET` misread so that 0.4 is silently taken as unset | **4/4 killed** |
| M3 | `ecology` is guarded with `mixed=True` | the `--only-fauna` exemption restored | killed |
| S1 (MUST) | `expand` refuses a `--shift` onto a preset field | the refusal removed; the refusal narrowed to the mass budget | **2/2 killed** |
| S2 | an ecology `--fair` run's marker and values are tested, and so is resume of a `--fair` run (evolve and ecology) | ecology writes no marker (**survived at e7b8865, killed now**); the resume note dropped | 2/2 killed |
| S3 | `fair.check(config)` | the marker ignored; the shift ignored; stop at the first deviation; presence checked but not value; the wrong mutation key; a tolerance of 0.05 | 5/6 killed. The tolerance mutant survives (F-N1) |
| S4 | DESIGN §1 names `--structural-rate-scale` and the crossover alignment as left out, with reasons | (text) | closed |
| S5 | DESIGN §3's 19% is reworded as a bias-only residual; no flag | (text) | closed |
| N1–N3 | help text; the refusal's wording; `note_resume` | the note dropped | killed |
| guard, conflict | unchanged | the guard never fires; a conflicting value silently overridden | 2/2 killed |

**(2) `--only-fauna` is guarded, and resume never meets the guard** (`fc_probe.txt` §2).
- A bare `ecology --only-fauna holistic`, `conventional`, and `holistic --lesion-fauna holistic` are each
  **REFUSED**.
- With `--fair` the same run starts, and `check` of its `config.json` is `[]`.
- `ecology --resume` with no flag continues both a `--fair` only-fauna run and a bypassed one.
- `evolve --resume --fair` on a bypassed run continues it and prints that the flag is ignored. No fairness key is
  added: the run keeps its own `config.json`.
- The mutants that put the guard on the resume path are killed for evolve and for ecology.

**(3) `fair.check` returns every deviation** (`fc_probe.txt` §3). Each case is one deviation, applied to a `--fair`
config:
- the marker missing, or `"unfair"`;
- each of the seven values, including small offsets: mass 15.35, motor 1.7605 (the Pioneer's own figure), cone 1.5,
  settle 0.02, settle_max 9.9, S = 1e-6;
- a removed key.

Each gives exactly one deviation, named with its path and flag. The test itself asserts all three on one config.

On an ecology config, `ecology.shift` set to any of these is caught:
- `world.motor_budget=0`;
- `" world.motor_budget =0"` (with spaces);
- `synthesis.mass_budget=40`;
- `world.ball_cone=0`;
- `world.hinge_range=3`.

These are not flagged: `food.work_cost`, `terrain`, `world.motor_strength` and `--world.motor_budget=0`. The last
cannot run: argparse refuses the value, and the shift resolver has no such field. At the CLI, `--fair` refuses the
same five forms before any `config.json` is written.

**(4) `effector_bias_sigma = 0` is expanded, printed and written** (`fc_probe.txt` §4).
- `evolve --fair` prints `… --settle-max 10 --effector-bias-sigma 0`.
- `config.json` has `mutation.effector_bias_sigma = 0.0` for both `evolve` and `ecology`.
- `--fair --effector-bias-sigma 0.4` is refused, and `--fair --effector-bias-sigma 0` is accepted.
- `simulate --fair` omits it, as it should: `simulate` has no mutation flag.

**(5) Suite: 615 passed** (611 before the fixes, plus the four new tests), 0 failed. The command is `python -m pytest -q -p no:cacheprovider`, run in a clean `.[dev]`
venv without scipy (Python 3.11.15, x86_64, mujoco 3.14.0, numpy 2.4.6) on f8f903e merged with c904de1.

## Remaining NITs (not blocking)

- **F-N1.** `check`'s value comparison is exact to 1e-12, and that is right. But no test plants a *small* deviation,
  so a mutant that tolerates ±0.05 survives: settle 0.02 would then pass. One line would pin it: assert that
  `check` flags `sim.settle_until_rest = 0.02`.
- **F-N2.** `check`'s docstring and the DESIGN S3 row say "RBT-129's stages.py calls it". There is no `stages.py` on
  integration yet (RBT-129a). It should read "is to call".
- **F-N3.** DESIGN has two stale lines:
  - l.7 still says the set "is now six flags long". It is seven with S.
  - l.119–121 of the kept-for-the-record bias-only section still says "saturates 54% of the designed body's
    **motors**" and "S = 0 **stops it**". Both mean the Effector biases, as the corrected paragraph above them says.

`world.motor_strength` shifts under `--fair` are allowed. That is consistent with the ruling: the motor budget scales
with the strength, and it binds both faunas. I note it for RBT-129 without a finding.
