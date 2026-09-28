# RBT-129 launch FIX-CHECK: PR #435 at `1155e33`, trial-merged on integration `4c32cec`

**Verdict: MERGE AFTER FIXES, with one item left.**

- **The launch adversary's four MUSTs (L1–L4) are closed**, and so are all the SHOULDs.
- **What is not done:** the eating rule re-ruled at 03:10 (`--eat-from root --eat-rule surface`, comment on #436) is
  **not implemented**. `stages.py` refuses it, and nothing guards the surface-clearance fix it depends on (§8).
- **The fix is small** (**R1**, below). Stage P and Stage 0 cannot be emitted under the ruled rule until it lands.
- **Everything else is ready to fire.**

**How this was checked.**
- **Trial merge:** #435 at `1155e33` merged into integration at `4c32cec` without conflict (`3303ba2`). #432 is
  `42261bd` and #437 is `4c32cec` on integration.
- **Probe:** `probe_fixcheck_launch.py` → `probe_fixcheck_launch.txt`. It builds configs and runs the tests' tiny
  non-sweep world (2–3 seasons) only. No sweep arm, cell or founder was run.
- **Suite:** the full suite ran in a clean `.[dev]` venv without scipy (§9).

## (1) L1: blocks require `--fair` and pass `fair.check`. Closed

`check_fair` accepts only exactly `["--fair"]`. It refuses, with exit 4, each of:
- the empty list;
- `--unfair-i-know`;
- `--fair --unfair-i-know`;
- `--motor-budget 1.77`;
- `--sweep-log`;
- `fair`.

`check_block` runs `fair_deviations`, which requires:
- the marker `"fairness": "fair"`;
- every preset value, found by key;
- RBT-128's own `fair.check(config)`. It refuses if `fair.check` is missing from the tree.

A block built with `--unfair-i-know` is refused with 14 listed deviations. A `--fair` block carries `fairness: "fair"`
and all **seven** preset values:
- `sim.synthesis.mass_budget` 15.34;
- `sim.world.motor_budget` 1.77;
- `ball_cone` and `hinge_range` π/2;
- `sim.settle_until_rest` 0.01;
- `sim.settle_max` 10;
- `mutation.effector_bias_sigma` 0.

Where the checks run:
- `emit`, `prelaunch`, `pays-prize`, `probes` and `pays` check every block they build.
- `run-lane` re-derives every fresh job's block from `launch.txt`'s flags and refuses an edited one
  (`check_lane_blocks`).
- The test that enshrined the gap is inverted: `test_the_fair_guard` now asserts exit 4 on all of the above, plus
  `--fair-v2` and `--fair --seed 7`.

## (2) L2: `run-lane` refuses any other tree. Closed, but it checks three trees, not the whole commit

`check_host` compares `HEAD:<t>` with `launch.txt`'s `tree:<t>` for `rabbitstew`, `runs/RBT-129/launch` and `scripts`.
It also refuses anything uncommitted under those three trees, `worlds/` and `lanes/`.

| case | result |
|---|---|
| matching record, clean tree | accepted |
| a record with another `rabbitstew` tree | refused, exit 5 |
| an uncommitted edit to `launch/blocks.py` | refused, exit 5 |
| an uncommitted edit to `runs/RBT-125/gate/steps.py` | **accepted** |

The coordinator's brief says "the whole tree". The fix pins the three trees every `run-lane` job executes. That is
sufficient for the S, M and N arms, K1 and the census, whose code lives only there.

The PAYS and probe jobs are different. `prize_gate.py`, `steps.py` and `steer.py` run as emitted `.sh` scripts, not
through `run-lane`.
- `probes` and `pays` pin `steer.py` and the §B harness by blob hash **at emit time**.
- The session that later runs the `.sh` checks nothing.
- `pays-prize` pins nothing about `prize_gate.py`.

**S1:** prefix every emitted `.sh` with a check that each file's blob hash is the one recorded at emit (and
`prize_gate.py`'s too), or run those jobs through `run-lane`.

## (3) L3: `fair.expand` sits in `ecology_configs` and the guard in `cmd_ecology`. Closed

`ecology_configs` calls `fair.expand`. `cmd_ecology` keeps the resume branch first, then calls `expand`, `guard` and
`announce`.

On the trial merge, with the tiny world:
- **A fresh `--fair` run** writes a `config.json` with `fairness 'fair'`, and `fair.check` finds nothing wrong.
- **`--resume` with no flags** exits 0. It never meets the guard.
- **A fresh run with no fairness flag** is refused by the guard, exit 1.

`test_a_fair_block_is_the_config_json_the_ecology_writes_key_for_key` and `test_the_cli_run_under_fair_writes_the_block`
pin it.

## (4) L4: no job waits on `durable.sh`. Closed; the wall clock re-derives

- **Short jobs take no snapshot.** Jobs under 120 arm-seasons (census, S60, K1, stage A) never snapshot.
- **Long jobs never block the lane.** A long job's `durable.sh every 20` runs in its own process group and is killed,
  sleep and all, when the run exits. The final save goes to the background.
- **Measured:** against a local bare remote, `stages._ecology(long=True)` on a 3-season tiny run returned after
  **1.3 s**. r1 waited 20 minutes. `test_a_job_never_waits_on_durable_sh` shows the same beside a 120-s sleep.

**The wall clock.** `stages.py plan P,0` gives lanes of 1,980–2,040 arm-seasons. At WORKERS = 2, a lane runs one
arm-season in 10 s at 20 core-s, or 12.5 s at 25. That gives 2,040 × 10 s = **5.7 h**, or **7.1 h** at 25 core-s,
before probes and PAYS. This is READINESS's figure, and it now holds.

Two notes:
- Each long job pushes a snapshot branch. That is about 64 pilot run directories, down from about 540 in r1.
- The final background save can still be running when the lane's next job starts. This is harmless, because they
  write different run directories.

## (5) The SHOULDs. All taken

| item | status |
|---|---|
| **S1, the cost narrative** | `print_plan` and READINESS §3 now attribute P's excess correctly: N at full cost (+3.2 core-h) and K1 (+1.6). "The planted set was in r4" |
| **S2, W118-b S60 jobs** | Stage **A** makes S 0–59 at `c0-p030-U-L` for the seeds the census and pilot do not (129005–129008 with P). That is 240 arm-seasons, 1.3–1.7 core-h, charged to the anchor fallback |
| **S3, K1 compares all files** | `k1_compare` compares every output file: genomes, `state.json`, lineage, cohorts, history. It excludes `config.json`, `platform.json`, `command.txt` and the logs. The every-file comparison found a real bug, now fixed: the ecology never clears `<kind>/final/`, so a resumed run whose population shrank kept dead members there. `_clear_final` runs before every resume |
| **S4, the planted set is emitted** | `probes` requires `--planted-cmd` and emits one planted-set job per pilot point |
| **S5, the pays guard** | `probes` and `pays` require `steer.py` at a given blob hash (`--steer-sha`). `pays` also requires §B's harness at its hash (`--steps-harness`, `--steps-sha`) and the eating rule. The designed prize leg is split out as `pays-prize` (`prize_gate.py` on §A's ten hosts). It needs neither `steer.py` nor §B, and it checks that the hosts exist (exit 7) |
| **S6, `--eat` explicit** | There is no default. Every launching command refuses without it, and it is recorded in `launch.txt`. See §8 for why the whitelist is now wrong |
| **S7, census reuse** | DESIGN carries a pre-data plan note. Stage 1 resumes the census's season-60 states at seeds 129001–129003, saving about 36 core-h. The pilot's 12 repeats are kept on purpose, as a byte-compare control |
| **S8, "unreachable" reworded** | `prints.txt` now reads "inside a footprint", with the reach-limited share beside it (0.005–0.009 at c ≥ 0.5 in U). See §8 on the eating rule |
| **S9, relative paths** | Lane files hold paths relative to the repository root. `absolute()` refuses a path that is absolute or `..` |
| **S10, `effector_bias_sigma`** | Closed by RBT-128 itself: the preset now carries 0 |

## (6) S11: `pays` hands `steps.py` a real `config.json`. Closed

- **The file:** `world_config_dirs` writes `worlds/config/<id>/config.json` from `blocks.config_dict`, and checks the
  block first. `pays` formats `{config_json}` with it.
- **Probe:** `SimConfig.from_dict(raw["sim"])` parses it, `fairness` is `'fair'`, and `fair.check` finds nothing
  wrong.
- **Integration's `steps.py`,** as merged from #437, refuses a `--config` whose `fairness` is not `"fair"` (S12) and a
  host that is not `fair.is_designed` (S13).
- **The remaining gap:** `pays` formats both `{world}` (the block) and `{config_json}`, and a template that passes
  `{world}` to `--config` still fails with `KeyError 'sim'`. The docstring says so. That is acceptable.

## (7) The §12.1 pre-data amendment. Present and correct

DESIGN §12.1 now carries this amendment:

> "Resting throttle is closed" is wrong. `--effector-bias-sigma 0` freezes the Effector bias walk, but a network can
> still saturate resting drive through its neurons and links (96.5%, RBT-128 adversary `effective_drive.py`); R1's
> motor budget is what bounds the work. The prediction's direction stands; its stated mechanism does not.

That is the right correction. It is also consistent with ADVERSARY-437's S3: pre-fairness PAYS hosts carry the bias
walk.

## (8) The eating rule, re-ruled to root + surface. **Not implemented (R1)**

`probe_fixcheck_launch.txt`:
- **The candidate is unchanged.** `blocks.EAT_CANDIDATE` is still `("--eat-from", "root")`, and READINESS's firing
  lines read `--eat="--eat-from <ruled>"`.
- **The whitelist refuses the ruled rule.** `check_eat` accepts only `--eat-from X`, exactly two tokens, with X in
  {any, root, sensor}. `check_eat(--eat-from root --eat-rule surface)` is **refused (exit 4)**, and so is the same
  rule with `--clear-from geoms`. So `prelaunch`, `emit`, `pays-prize`, `probes` and `pays` cannot run under the ruled
  rule at all.
- **Nothing guards the missing surface-clearance fix.** A block built with the ruled rule carries `eat_from root`,
  `eat_rule surface` and no `clear_from`, which means the default, root. On this tree,
  `Simulation._clearance_points()` for that config measures from **the root centre only**. That is the clearance leak
  in RBT-125 BC's MUST 2: under `surface`, food is placed within a limb's surface reach but clear of the root.
  - Under root eating, BC measured the motors-off rod at 0 items, because a compact root's surface reach
    (≈ 0.35 + 0.15–0.26 m) is inside the 0.8 m clearance.
  - BC names the residual risk: "An elongated root, if synthesis allows one at the fixed root volume, could still
    reach past 0.8 m".
  - The fix (surface implies surface-distance clearance) is the RBT-125 designer's pending PR.
- **So does `prelaunch` guard against the fix's absence? No.** Today it refuses the ruled rule outright, through
  `check_eat`. Once `check_eat` is widened, nothing would stop a launch on a tree without the clearance fix.

**R1 (MUST):**
- (a) `check_eat` accepts the ruled rule exactly: `--eat-from root --eat-rule surface`, plus `--clear-from geoms` if
  the RBT-125 fix ends up spelled that way. `blocks.EAT_CANDIDATE` and the READINESS firing lines become the ruled
  rule.
- (b) `check_block` (or `check_eat`) refuses a surface block unless the tree measures clearance by surface distance
  under `eat_rule = surface`. The simplest test builds one `Simulation` under the block and asserts
  `_clearance_points() is _SURFACE_CLEAR`, which is exactly what the probe checks. Or it pins the rabbitstew tree to
  the fix's commit.
- (c) Re-run `prints.txt` under the ruled rule at `prelaunch`. Its reach-limited share assumes the xy **centre** rule.
  Under `surface`, the reach is 0.35 m from the root's **surface**, so the share changes. It is probably smaller, and
  the definition should say which rule it assumes.

## (9) The full suite, in a clean `.[dev]` venv without scipy, on the trial merge

The venv was fresh (`python -m venv`; `pip install -e ".[dev]"`, where `dev = ["pytest>=7"]`), and scipy is absent
(`import scipy` gives ModuleNotFoundError). The result is in `suite_fixcheck.txt`:

**649 passed, 1 skipped, 16 warnings in 11 min 53 s.**
- **The skip** is `tests/test_rbt125_harness.py:170`, the harness's scipy cross-check of its own t quantile, which
  `importorskip`s scipy. It is expected in a scipy-free venv.
- **Nothing depends on scipy:** #437's merged `steps.py` now uses a scipy-free t quantile (`d41765f`).

## The list

**MUST**
- **R1:** the ruled eating rule (`--eat-from root --eat-rule surface`):
  - accepted by `check_eat`;
  - the candidate and the firing lines;
  - a guard that the tree carries the surface-clearance fix;
  - `prints.txt` re-run under it.

**SHOULD**
- **S1:** the emitted `.sh` scripts for `probes`, `pays` and `pays-prize` verify their tools' blob hashes on the
  session that runs them, `prize_gate.py` included.

Once R1 lands (with the RBT-125 clearance fix merged first, or R1(b) refusing until it is), #435 can merge, and
Stage P and Stage 0 can fire. The coordinator can check R1 against this file's §8 without another adversary pass.

---
_Generated by [Claude Code](https://claude.ai/code)_
