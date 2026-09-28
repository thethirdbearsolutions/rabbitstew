# RBT-128 design adversary: `--fair` and the missing-budget guard (#432 at e7b8865)

**Verdict: MERGE AFTER FIXES.** Three MUST, five SHOULD and five NIT items follow.

- **The preset's six values are the ruled ones.** The guard fires on every mixed path I could find. The bypass writes
  nothing, and the tests mostly bite (18 of 20 mutants killed).
- **The [OPEN] item's evidence measures the wrong quantity.** S = 0 freezes the Effector's own bias. It does **not**
  close resting throttle under selection: the network carries the same throttle through neuron biases and link
  weights, and selection saturates it just as fast at S = 0 as unset. The ruling on S should still be **S = 0, in the
  preset**, but for a narrower reason than DESIGN §3 gives. The claim RBT-129 builds on ("the designed body's resting
  throttle is closed") needs a correction.
- **One exemption lets a sweep arm start without the preset:** `ecology --only-fauna`, which RBT-129's retention layer
  uses.

Every number below comes from a script in this directory, with its output beside it as `.txt`:
- The probes import the PR's `rabbitstew/fair.py`, so run them on the PR tree.
- No sweep arm and no RBT-116 cell was run.
- The runs are tiny: at most 4 generations or 3 seasons, with 0.2 s bouts. Nothing in them is a registered result.

| script → output | what |
|---|---|
| `guard_probe.py` → `guard_probe.txt` | every CLI path that starts or resumes a mixed run: its outcome, and the fairness values in its `config.json` |
| `bypass_bytes.sh` → `bypass_bytes.txt` | the same `evolve` and `ecology` command lines on integration (bare) and on the PR (`--unfair-i-know`); every output file compared by sha256 |
| `compose_ecology.py` → `compose_ecology.txt` | `--fair` against the explicit six + bypass, on an `ecology` run carrying every RBT-125/126/130 strip |
| `designed_scan.py` → `designed_scan.txt` | `is_designed` on the fixed constructors and on every committed genome under a `holistic/` or `conventional/` path |
| `mutants.py` → `mutants.txt` | 20 single-edit mutants of `fair.py`, `cli.py` and `evolution.py`, run against the 13 new and 4 edited tests |
| `effective_drive.py` → `effective_drive.txt` | resting drive through the **network**, not only the Effector bias: under selection and under drift, at S unset, S = 0, S = 0 + G = 0, and S = 0 with newborn Effectors at bias 0 |
| `steer_route.py` → `steer_route.txt` | question 3(b): the food-sensor→motor gain under selection and under drift, same rows |
| `suite.txt` | the full suite |

## What holds (checked, no finding)

- **The preset values.**
  - **15.34:** RBT-120 DESIGN l.104, where the Pioneer is 15.3367 kg.
  - **1.77:** RBT-120, where the Pioneer is 1.7605.
  - **Cone and hinge at π/2:** RBT-124 §1, "registered as a range (the ruling)". F1 is met because both come with the
    budget.
  - **Settle ε 0.01 m/s and cap 10 s:** RBT-124 §3, accepted at the 23:35 ruling.
  - Every value is written where its own flag would put it.
- **`cap_on_reachable` is rightly out.** No such flag exists, and RBT-121's fix list puts it at item 10, after the
  preset (item 9). It is not ruled in.
- **Composition.**
  - For `evolve`, the PR's own test covers it.
  - For `ecology`, `compose_ecology.txt` compares `--fair` against the explicit six + `--unfair-i-know`. The config
    carries `--smell-contrast/--smell-tau/--eat-from/--eat-rule/--clear-from`, `--obstacle-radius`,
    `--breed-rule/--breed-stream`, `--sweep-log`, `--work-cost` and `--effector-bias-sigma 0`. The two `config.json`
    files differ **in the `fairness` key alone**, and every strip's value is written.
- **The guard** refuses these (`guard_probe.txt`):
  - bare `evolve`;
  - `evolve --fixed-body <file>`;
  - bare `ecology`;
  - `ecology --from-run`;
  - `simulate` holistic + Pioneer;
  - `simulate` with three robots, two holistic and one Pioneer.

  Nothing is written for a refused run.
  - `--config-from` and `--config` do not exist: argparse refuses them.
  - `--resume` on a directory with no run fails (FileNotFoundError), so it gives no route to a fresh start.
- **Resume.**
  - **`evolve --resume` and `ecology --resume` of a `--fair` run keep `fairness: fair` and all six values**
    (`guard_probe.txt`), with no flag needed.
  - A new run cannot silently drop `--fair` on resume: resume reads the config and takes no sim flags, and
    `--mass-budget 99` on resume is ignored (NIT N3).
  - Old configs never meet the guard.
- **`--unfair-i-know` writes nothing** (`bypass_bytes.txt`). Every output of a 2-generation `evolve` and a 2-season
  `ecology` is sha256-identical to integration's bare run: `config.json`, `history.json`, `lineage.jsonl`,
  `state.json`, `cohorts.jsonl` and every genome. The one exception is `platform.json`, which records the tree's git
  sha and the time (RBT-127) and differs by design. So the four edited CLI tests' byte-identity claims hold.
- **`is_designed`** is right on `pioneer_genotype` (with and without a hidden layer), `drive_straight_genotype` and
  `quadruped_genotype`. It is also right on **120 of 120** committed designed-fauna genomes and 120 of 120 holistic
  ones (`designed_scan.txt`).
- **Suite:** **611 passed** in a clean `.[dev]` venv without scipy (Python 3.11.15, x86_64, mujoco 3.14.0, numpy 2.4.6),
  on e7b8865 trial-merged with integration 626ca4c. The merge is a no-op: the PR already contains 626ca4c. This
  matches the PR's count.

## MUST

### M1. The [OPEN] evidence measures the Effector bias, not the throttle: S = 0 does not close resting throttle under selection

`bias_select.py` selects for, and reports, |tanh(Effector bias)|. But a motor's resting throttle is the Effector's
**output** with the sensors quiet, `clip(Σ tanh(bias + W·activation))` (`brain.py` l.72–104).
- A global or segment neuron with no input outputs tanh(b), a constant. Through a link, that constant is an Effector
  bias by another name.
- Its link weight walks at `weight_sigma` whatever S is, and so does the neuron's bias, unless G = 0 on the designed
  body.
- The designer says so in passing ("a body can still hold a motor on through its sensors and neurons"). The tables
  then read as if S = 0 stops the throttle.

`effective_drive.py` repeats `bias_select.py` exactly: the same founders, the same truncation 10 of 40, 23 rounds and
5 replicates, the same rng. What changes is the quantity:
- **network resting drive**: the mean |output| of each driven DOF over ticks 40–59, stepping the synthesized brain with
  every sensor at 0;
- **selected for**: its mean, which is the D line's direction through whichever gene carries it.

Cells are the network share > 0.9, with the bias-only share in brackets:

| selection | G 0 | G 6 | G 12 | G 23 |
|---|---|---|---|---|
| designed, unset | 28.7% (0.0%) | 92.5% (15.3%) | 94.0% (23.0%) | **97.7%** (36.2%) |
| designed, **S = 0** | 28.7% (0.0%) | 89.5% (0.0%) | 96.0% (0.0%) | **96.5%** (0.0%) |
| designed, S = 0 and G = 0 | 28.7% (0.0%) | 93.8% (0.0%) | 94.8% (0.0%) | **98.0%** (0.0%) |
| holistic, unset | 24.2% (0.8%) | 78.8% (8.2%) | 85.6% (19.9%) | 79.3% (16.7%) |
| holistic, **S = 0** | 24.2% (0.8%) | 81.9% (2.8%) | 88.3% (3.3%) | 86.2% (4.6%) |

| drift alone, 80 lineages | G 0 | G 23 | G 60 | G 150 |
|---|---|---|---|---|
| designed, unset | 28.7% (0.0%) | 41.2% (16.9%) | 53.8% (27.5%) | **71.9%** (54.4%) |
| designed, **S = 0** | 28.7% (0.0%) | 38.1% (0.0%) | 46.2% (0.0%) | **50.6%** (0.0%) |
| designed, S = 0 and G = 0 | 28.7% | 40.6% | 36.9% | 44.4% |
| holistic, unset | 24.2% (0.8%) | 33.5% (11.3%) | 26.6% (18.4%) | **34.4%** (23.6%) |
| holistic, **S = 0** | 24.2% (0.8%) | 24.5% (0.3%) | 17.4% (0.6%) | **19.6%** (0.6%) |

- **Under selection, S = 0 changes nothing about throttle.** With S = 0 the bias-only share stays at 0, as the designer
  reports, while the throttle saturates as fast as unset: 96.5% against 97.7% at G 23. Adding G = 0 does not help
  either (98.0%).
  - "Under directional selection, a bounded S only delays saturation; S = 0 stops it" and "at S = 0 the designed body
    cannot move at all" are true of the gene, not of the motor.
  - This is an R10 problem: the planted positive's instrument cannot see the route that carries the trait.
- **Under drift, S = 0 removes a real part of the walk,** but not all of it. On the designed body the network share
  at G 150 falls from 71.9% to 50.6%, against a founding 28.7%. On the holistic body it falls from 34.4% to 19.6%.
- **Sensors at 0 understates the other routes.** The foraging vocabulary's `up` and `height` sensors are nearly
  constant at rest (30 and 10 of the designed founders' sensors in 10 genomes), so their weights are further walked
  offsets.
- **Consequence for RBT-129.** RBT-129 §2 and §12 prediction 1 ("under the fairness set the designed body's resting
  throttle is closed (`effector_bias_sigma`; its D line was 99% saturated), so its work bill is expected to fall more")
  rest on the throttle claim. Under selection, what closes resting throttle is **its price**: the work price, which is
  one of the sweep's axes. S does not close it.

**Fix.**
- Reword DESIGN §3 and the PR body: S = 0 freezes the **Effector-bias walk**. That removes the unselected drift
  through that gene and protects a sensor-driven response from masking (M2, 3(b)). It does not bound resting
  throttle, which selection reaches through neurons and weights at the same speed.
- Flag RBT-129 §12.1 to the coordinator for a one-line amendment: the premise is "the Effector walk is frozen", not
  "resting throttle is closed".
- R8's lever report should read resting drive from the network with the sensors at their settled values, not from the
  bias. If it reads the bias today, open a ticket.

### M2. Rule S and put `--effector-bias-sigma 0` in the preset before this becomes RBT-129's gate

- RBT-129 §2 (l.156) registers that "every arm runs under `--fair` (RBT-128), which carries … `effector_bias_sigma`".
  Every sweep point prices work, so by the designer's own criterion ("any registration that reads work, throttle or
  the D line") every sweep arm needs S = 0.
- Merged with S unset, the §11.1 gate "RBT-128 merged" is met while the walk stays open on every arm. That is R9's
  exact failure: one flag, set by hand, per config.

**Recommendation (answers 3(c) and 3(d)):**
- Add `("effector_bias_sigma", 0.0, "--effector-bias-sigma 0")` to `PRESET`, with `_UNSET` `None`.
- `simulate` has no mutation flags, and `hasattr` already skips it there.
- The ruled set test and the expansion line change accordingly.

**Why S = 0 and not a bounded S (3(c)).**
- A non-zero S adds only an Effector-bias route to a resting or steering offset. The network already supplies that
  offset under selection: 96.5% saturation at S = 0 (M1), and the gain in 3(b).
- Meanwhile a non-zero S reopens the drift: at S = 0.05, 2.5% of designed Effectors saturate by G 150 on the bias alone
  (`bias_walk_s.txt`). It also reopens the masking of 3(b).
- S = 0 draws the same random numbers as unset, so it costs nothing in the stream.

**Why in the preset, not per registration (3(d)).**
- The only committed registration that wants the walk is a re-reading of pre-fairness lines (RBT-113 and similar).
  Those already run with `--unfair-i-know`, or from their own commit.
- An explicit `--fair --effector-bias-sigma 0.4` is then refused, which is the right outcome.

### M3. `ecology --only-fauna` is exempt, and it is a sweep arm

- RBT-129 §11.2's retention layer (R_sel and R_marker) runs "the planted fauna's ecology only". It uses RBT-130's
  `--only-fauna`, whose seasons are, by construction, "its half of a two-fauna run at the same seed". They are read
  against two-fauna arms under `--fair`.
- A bare `ecology --only-fauna holistic` (or `conventional`, or with `--lesion-fauna`) starts with **no mass budget,
  no motor budget, no ranges and no settle** (`guard_probe.txt`). Nothing warns.
- This is the forgotten-flag artefact R9 exists to stop, on the arms whose physics must match the S arm's.

**Fix.** Drop the exemption: guard every fresh `ecology` (and `evolve`).
- The one existing exemption test flips.
- RBT-130's `_cli` already appends `--unfair-i-know`.
- If the coordinator prefers to keep the exemption, then S3's config check becomes a MUST for RBT-129a's readout
  instead.

## SHOULD

### S1. `--shift` can turn a preset field off mid-run while `config.json` still says fair

- `ecology --fair --shift-at 1 --shift world.motor_budget=0` starts. So does `--shift synthesis.mass_budget=40`.
- The config then reads `fairness: fair, motor 1.77`. Only `history.json`'s `shift` field records that the budget
  was off from season 1 (`guard_probe.txt`).
- RBT-118's stress arms use shifts; a sweep point may too.
- **Fix:** under `--fair`, refuse a shift whose dotted target is a preset field (`synthesis.mass_budget`,
  `world.motor_budget`, `world.ball_cone`, `world.hinge_range`, and `settle_*` if they ever become shiftable).

### S2. Two behaviours the sweep depends on are untested

- **The ecology's marker.** The mutant "`cmd_ecology` writes no fairness marker" **survives** (`mutants.txt`).
  `test_fair_on_ecology_and_simulate` checks only the parsed args, and the one ecology run in the tests is the exempt
  `--only-fauna` one.
- **Resuming a `--fair` run.** `test_resume_needs_no_flag` covers a bypassed run only. Nothing pins that a `--fair`
  run's `fairness` key and values survive `--resume`. They do (`guard_probe.txt`), but no test says so.
- **Add:**
  - a 1-season `ecology --fair` run that asserts `config.json` carries `fairness: fair` and the six (seven, after M2)
    values;
  - an `evolve`/`ecology` resume of a `--fair` run that asserts both are kept.

### S3. A config-level check, for the places the CLI guard cannot reach

The guard does not cover:
- programmatic entry (`Experiment`, `Ecology`, `runs/*/world.py`);
- `--shift`;
- the `--only-fauna` exemption, if kept;
- `--fixed-body <file>` bouts (N4).

All of these meet one point: the arm's `config.json`.

**Fix:** add `fair.check(config_dict) -> list[str]` (the preset fields that differ, plus a missing marker). RBT-129a's
launch dry-run and its readout then refuse an arm that fails it. It is about 15 lines, and it moves the guarantee to
where the claim is read.

### S4. DESIGN should name R6's `structural_rate_scale` as out of the preset, with the reason

- RBT-129 §2 (l.159) defers to this ticket: "If RBT-124/128 rule `--structural-rate-scale` into `--fair`, it applies
  everywhere".
- DESIGN §1 lists `cap_on_reachable` as left out but says nothing on `structural_rate_scale` or the crossover
  alignment (fix-list item 10).
- **Fix:** one row each: "not ruled in; R6 is met by stating the operators (RBT-129 does)".

### S5. Question 3(a): the holistic newborn-Effector residual is real on the gene but immaterial on the motor; no fix

- On the bias alone, the holistic fauna under S = 0 keeps a route the designed body lacks:
  - **newborn Effectors**, drawn with bias N(0, 0.5);
  - **copies of the founders' saturated Effectors**, spread by node duplication.
- The designer's 19% is under bias-targeted selection. Under throttle-targeted selection it is 4.6%
  (`effective_drive.txt`).
- **The proposed fix (founding bias × 0 for new Effectors under S = 0, same draw) does not remove it:** 5.3%. The
  copies carry it.
- **On the throttle it changes nothing:** 83.0% against 86.2% at G 23, and the designed body saturates more (96.5%).
  Under drift it moves the holistic network share at G 150 from 19.6% to 11.2%. That is below the designed body's
  50.6%, so it would widen the drift gap between the faunas, not close it.
- **R6 reading:** there is no parity cost to register at the motor, and the fix buys nothing. Reword DESIGN §3's
  "19%" paragraph as a bias-only residual and do not add a flag.

## NIT

- **N1.** `--fair --motor-budget 0` (or `--ball-cone 0`, or `--settle-until-rest 0`) is silently overridden to the
  preset. An explicit value equal to the parser's default cannot be told from unset. This is the safe direction; say
  so in `--fair`'s help.
- **N2.** A command line that gives all six flags explicitly without `--fair` is refused by the guard. It must add
  `--fair` (accepted, since the values match) or `--unfair-i-know` (which writes no marker). Acceptable; say so in
  the refusal.
- **N3.** `--resume` silently ignores `--fair`, `--unfair-i-know` and any sim flag (`--mass-budget 99` on resume
  starts and changes nothing). The sim flags were ignored before RBT-128 too. Print one line when a fairness flag is
  given with `--resume`.
- **N4.** `is_designed` does not recognise a designed body given by `--fixed-body <file>`. RBT-37's `reevolve-403body`
  used a holistic body file this way. A `simulate` of such a run's conventional champion against a holistic body
  starts unguarded. It is rare, and S3 covers it.
- **N5.** The idempotence mutant (`_fair_expanded` removed) survives because it is equivalent: a second `expand` finds
  every value equal to the preset. The flag is harmless but dead weight.

## 3(b). Does S = 0 remove the route by which a compass or steering evolves? No. It protects it.

**What the probe measures** (`steer_route.py`):
- **Gain:** the mean over food sensors and driven DOFs of |out(s = +0.5) − out(s = −0.5)|.
- **The route:** food sensors to motors. That is the route RBT-97's routed compass uses, and the one RBT-125's
  contrast channel feeds, since it rescales the same food sensors.
- **Setup:** the same selection and drift scheme as M1.

| designed | selection G 6 | G 12 | G 23 | drift G 150 |
|---|---|---|---|---|
| unset | 0.485 (84%) | 0.595 (87%) | 0.998 (93%) | **0.089** (28%) |
| S = 0 | 0.533 (89%) | 0.604 (96%) | 0.862 (98%) | **0.129** (42%) |
| S = 0 and G = 0 | 0.638 (98%) | 1.006 (99%) | 1.279 (96%) | **0.163** (50%) |

(The founders' gain is 0.163 (60%); the share of genomes with gain > 0.1 is in brackets. The holistic rows are in
`steer_route.txt`: its founders carry few food sensors, and S makes no difference there.)

- **Under selection, S = 0 leaves the route open.** The gain grows as fast at G 6 and G 12 and ends at a similar
  level. A steering offset is a resting-drive difference, and M1 shows that the network carries it at S = 0.
- **Under drift, S = 0 slows the erosion of the founders' gain** (0.129 against 0.089 at G 150). A walked Effector bias
  pins its tanh and masks its input: paper 10's masking, one unit downstream.
- **Strand 3's "kept in the best lines but not spread" was the global-bias walk** (RBT-112, `--global-bias-sigma`).
  S does not touch it, and G = 0 holds the gain at its founding level.
- **So S = 0 does not block a smell-driven compass, and removes one way of eroding it.**

## Recommendation on the [OPEN] item, in one place

- **S = 0, in the preset (M2).**
- **Worded as freezing the Effector-bias walk, not as closing resting throttle (M1).**
- **No newborn-Effector fix (S5).**
- The throttle under selection is the work price's business, and R8 should read it from the network.
- Whether RBT-129 also wants G = 0 (designed only, since G does not bind the holistic fauna) is a separate R6 question.
  I do not recommend it here: it would be an asymmetric operator.
