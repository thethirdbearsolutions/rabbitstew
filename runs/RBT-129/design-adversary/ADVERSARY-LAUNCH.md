# RBT-129 launch adversary: PR #435 (`results/RBT-129-readiness` at `4464a4e`), and PR #437 (`5043750`)

**Verdict on #435: MERGE AFTER FIXES. Verdict on #437 (RBT-125 §B's nose-step harness, reused): MERGE**, with three
SHOULD items. #437 is covered in §9.

What holds:
- **World blocks:** all 150 match the registered design key for key.
- **`cli.py` refactor:** byte-identical.
- **Pilot and census plans:** they implement r4's points, seeds, arms and fork.
- **Arithmetic:** re-derives.

What must change first:
- **Four MUST items.** Two are guards that do not guard, one is a runner that will roughly double the census wall
  time, and one is the #432 merge. Each is a small, local change.
- **Nothing here was run on the sweep.** Every probe below builds configs, or runs the tests' tiny non-sweep world
  (`TINY`, 2–4 seasons), or runs fixtures on prints.py's own draws.

## Probes (this directory)

| probe | question |
|---|---|
| `probe_launch_blocks.py` → `.txt` | do the blocks match the committed world key for key, and do all 150 points sit on r4's axes? |
| `probe_launch_cli.sh` → `.txt` | is the refactor byte-identical? (the base tree against PR #435, same tiny command lines) |
| `probe_launch_guards.py` → `.txt` | can `check_fair` be bypassed? does the marker reach the blocks after #432? does resume meet the guard? (PR #435 as is, and the adversary's scratch merge of #432 into it) |
| `probe_launch_host.txt` | does `run-lane`'s tree check see an edited launcher? |
| `probe_launch_durable.txt` | does a job wait on `durable.sh`'s sleep? |
| `probe_launch_prints.py` → `.txt` | how much of the "unreachable" share is out of reach under the eating rule? |
| `probe_launch_harness.py` → `.txt` | #437, items (a)–(d) (§9) |

PR #435's own tests pass: 18 of 18 (`tests/test_rbt129_launch.py`).

## 1. Do the launchers implement r4?

**Mostly, yes.** `stages.py plan P,0` shows:

- **Stage P** runs the four pilot points (`c1-p030-U-L`, `c0-p030-U-L`, `c1-p030-PW-G`, `c2-p030-PW-G`) × seeds
  129001–129004.
- **Each pilot chain** is S60 → a snapshot at the season-60 state → S resumed to 300.
  - **M:** forked from the snapshot with `merge_after 60`, `pooled_capacity 120`.
  - **N:** forked the same way, with `merge_null` holistic on odd seeds and conventional on even, on all 4 seeds (r4
    S10).
- **K1** runs per point on seed 129001.
- **Stage 0** runs 150 points × 129001–129003, arm S, seasons 0–59.
- **The seed lock** is per seed, in `/tmp`, held for the whole job.
- **The lane split** puts odd seeds on lane 0 and even seeds on lane 1, with census seed 129003 split between them
  first/last. Every unit is placed once, and the two lanes of a host never share a seed while they run.

**The cost lines are honest in total, but the stated reason for P's excess is wrong.**
- READINESS says r4's P line "left out the planted set at the pilot". It did not: r4's `prior_regime.py` has
  `pilot = 4*4*(h300 + h240 + 0.85*h240 + probes) + 4*plants`.
- The 4.4–6.1 core-h gap has two real sources:
  - **N at full cost.** The plan counts N at the full 240 arm-seasons, where r4 counts 0.85×. That is 16 × 0.2 =
    **+3.2** core-h.
  - **K1's straight run.** 4 × 70 arm-seasons is **+1.6**.
- The arithmetic otherwise re-derives:
  - **P:** 12,760 arm-seasons, 70.9 / 88.6 core-h for the arms, plus probes and planted set, gives 81.4–87.4 at
    20 core-s and 99.2–105.1 at 25.
  - **Stage 0:** 27,000 arm-seasons, 150 / 187.5 core-h, plus 45 core-h of PAYS, gives 195 / 232.5.

  **S1:** correct the sentence in READINESS §3 and in `print_plan`.

**K1 compares too few files.** It compares `lineage.jsonl`, `cohorts.jsonl` and `history.json`. It does not compare
`state.json` or the genome directories, and r4 names `seasons.txt`, which the ecology does not write.
**S3:** compare every file the run writes, except `config.json` (the fork rewrites it), `platform.json`,
`command.txt`, the logs and the done-markers. State that `seasons.txt` is taken as `history.json`.

**The planted set is costed but never emitted.** `probes` writes member probes only (seasons 0 and 300). The planted
set per point (8 hosts a plant, a = 6) has no job, although the plan charges 4 × 0.8 core-h for it. Census check C3
is also unscripted, as READINESS says. **S4:** add a planted-set job per pilot point, or state that the ruled
`steer.py` command line produces it.

## 2. `blocks.py`

**It is correct** (`probe_launch_blocks.txt`).

Against `runs/RBT-107/fresh/base-11/config.json`, over 151 dotted keys, only these differ:
- `seed`, `workers`, `generations` and `ecology.seasons` (arm fields);
- `sim.food.eat_from = root` (the eating-rule candidate);
- `ecology.sweep_log = True`.

Against RBT-90 forage-801, `ecology.breed_stream` also differs, because that config predates the key.

All **150 points** check out against r4's axes:
- **terrain:** flat at c0, random elsewhere;
- **obstacles:** N = 7/14/21/28 at radius 2.6 (U, HP), and **16/32/48/64 at radius 3.6** (PW);
- **price:** `work_cost` equals the point's price;
- **PW food block:** 2 patches × 0.4, radius 4.0, regrow 60, `log`, decay 1.5;
- **HP food block:** 3 patches × 0.6;
- **smell:** `smell_contrast 2.5`, `smell_tau 2` at G, and absent at L.

One harmless detail: c0 blocks keep `random_obstacles = 14` in the config, which flat terrain ignores.

## 3. `prints.py` and the unreachable share

The numbers re-derive from the script: footprints of boxes and cylinders as full extents, and a sunk sphere's cross
section at z = 0.

**"Unreachable" overstates what is out of reach by about 20×.**
- The eating rule is xy-only (an item within 0.35 m, in xy, of an eating geom's centre). Under `eat_from root`, the
  root can stand at an obstacle's edge.
- So an item inside a footprint, but within about 0.20 m of its edge, is eaten from beside it.
- A bump of 0.1 m or less can be driven over.

On prints.py's own 100 arenas (`probe_launch_prints.txt`):

| layout, c | inside any footprint (prints.py) | inside one > 0.1 m tall | also deeper than 0.20 m |
|---|---|---|---|
| U, 1 | 0.124 | 0.061 | **0.006** |
| U, 2 | 0.194 | 0.106 | **0.008** |
| HP, 2 | 0.144 | 0.065 | **0.003** |
| PW, 2 | 0.167 | 0.083 | **0.009** |

**Does it threaten a §8 verdict? No.**
- A common food tax shifts x = H − D by f × (food_D − food_H), because the designed body eats more on random
  terrain (RBT-118 §4a: 1.49 against 1.25). That shift is +0.002 at the deep share, and at most **+0.047** even at
  prints.py's 0.19.
- Both are under δ_i = 0.15 and inside the income noise. So the share cannot manufacture an EARNS call or an
  opposite-sign set.
- It moves the break-even price by at most about 0.047 / 14.7 kJ ≈ 0.003 $/kJ. That is under the UNDECIDED band
  (0.011–0.028).
- It is also part of what T2 reads, as §3.1 already says.

**U is taxed 1.3–1.4× more than HP at the same c.** This is an L × c food-tax term that M2 does not model. The point
random intercept absorbs it.

**S8:**
- Rename the column "inside a footprint".
- Add the deep share as the reach-limited figure.
- Say that the layout difference is absorbed by the point effect.

**NIT-2.** The food-per-cell items are 16 solo seasons of about 0.3–0.5 items each, so the per-season SE is about
0.15. READINESS's "items per 100 cells from 0.49 to 0.19" is within noise; the cell counts, 102 → 33, are solid.
Print the SEs.

## 4. The guards

**MUST L1: `check_fair` does not check fairness.**

It accepts any flag list whose `--` tokens are `ecology` options on the tree. `probe_launch_guards.txt`:

| flag list | PR #435 as is | after #432 merges |
|---|---|---|
| `--sweep-log` | accepted | accepted |
| `--motor-budget 1.77` | accepted | accepted |
| `--seed 7` | accepted | accepted |
| `fair` (no dashes) | accepted | accepted |
| **`--unfair-i-know`** (RBT-128's bypass) | refused | **accepted** |
| `--fair --unfair-i-know` | refused | accepted |

Consequences:
- `emit`, `prelaunch` and every fresh job's re-check would pass a block built with `--unfair-i-know`. Its config has
  **no** `fairness` key and **no** motor budget, cones, ranges or settle.
- The PR's own test enshrines the gap: `stages.check_fair(["--motor-budget", "1.77"])  # a flag the tree has passes`,
  and the tiny runner test uses `"fair": ["--sweep-log"]`.
- The fresh-job re-check reads the world file's `fair` field, not its `argv`. A hand-edited `argv` is never checked.

**Fix:**
- Require the fairness tokens to be exactly `["--fair"]`. Refuse `--unfair-i-know` explicitly.
- After building each block, assert `block["block"]["fairness"] == "fair"` and the preset's values (mass 15.34,
  motor 1.77, cone and hinge π/2, settle 0.01 / 10).
- In `run-lane`, rebuild each fresh job's block with `blocks.block(pid, fair, eat)` from `launch.txt` and refuse on
  any difference from `worlds/<id>.json`.
- Replace the two test lines with refusal tests.

**MUST L2: the host guard sees only `rabbitstew/`, and never compares the session with the launch.**
- `check_host` refuses on uncommitted changes under `rabbitstew/` only.
- With `runs/RBT-129/launch/blocks.py` edited to PW's nominal counts (13/27/40/54) and uncommitted, `check_host`
  **passes** (`probe_launch_host.txt`).
- `emit` records `commit` and `rabbitstew_tree` in `launch.txt`, but `run-lane` never compares them with the
  session's HEAD.
- So ten sessions can run lanes from different code or different launchers, and the arms would no longer be paired.

**Fix:** `run-lane` refuses unless:
- `git rev-parse HEAD:rabbitstew` equals `launch.txt`'s `rabbitstew_tree`;
- `HEAD:runs/RBT-129/launch` is recorded and matches;
- `git status --porcelain -- rabbitstew runs/RBT-129/launch runs/RBT-129/worlds runs/RBT-129/lanes` is empty.

**What is sound:**
- x86_64 is enforced, with exit 3.
- `probes` and `pays` refuse without an existing `--steer` file and a template, with exit 6.
- The fork and resume paths do not re-check fairness. That is correct, since they inherit S's config.

**The weaker check (S5):** `--steer` accepts any existing file, for example `/etc/hosts`. Pin `steer.py`'s ruled
commit or blob hash, and refuse otherwise.

## 5. The `cli.py` refactor and RBT-128 (#432)

**The refactor is byte-identical** (`probe_launch_cli.txt`). I ran three tiny command lines on the base tree `626ca4c`
and on `4464a4e`: a fresh run, a `--merge-after` run, and `--sweep-log` followed by `--resume`. Every output file
is byte-identical: 29–30 files a case, genomes and `state.json` included. The only exception is `platform.json`,
whose `git_sha` and `written_utc` are provenance.

**MUST L3: the #432 merge must put `fair.expand` into `ecology_configs`.**

Merging #432 into #435 conflicts in `cmd_ecology`. The two obvious resolutions are both wrong:
- **Taking #435's side** leaves `EvolutionConfig(fairness=… marker …)` referring to an undefined `marker`.
- **Taking #432's side inside `ecology_configs`** puts `resume`, which returns 0, and the guard inside the function
  the blocks call. Every `fair_pending` block build then raises.

The resolution that works was probed on a scratch merge:
- `marker = fair.expand(args)` sits at the top of `ecology_configs`, feeding `fairness=`.
- `cmd_ecology` keeps the resume branch first, then `expand`, `guard` and `announce`, then `ecology_configs(args)`.

On that tree:
- **A block built with `--fair`** carries `fairness: "fair"`, `mass_budget` 15.34, `motor_budget` 1.77,
  `ball_cone` and `hinge_range` π/2, and `settle_until_rest` 0.01.
- **`ecology_configs`' dict equals the CLI's `config.json`** on every top-level key except `workers`.
- **A tiny `--fair` run** resumes (`--resume --seasons 3`, no `--fair` on the command line) without meeting the guard.
  So does a fork with the merge set.
- **A tiny run with no fairness flag** is refused by the RBT-128 guard, exit 1.

**The fix:** merge #432 with this resolution, and add two tests:
- a `--fair` block carries the marker and the preset values;
- a `--fair` run resumes without the guard.

`expand` is idempotent, so calling it in both places is safe.

**S10: `effector_bias_sigma`.** r4's R1 row says `--fair` carries it. RBT-128's preset leaves it [OPEN] and unset, so
the blocks will not carry it. READINESS should say so, and the coordinator should confirm that r4's row follows
RBT-128's ruling.

## 6. READINESS's claims

**RBT-118 has no registration.** Confirmed: the integration branch's `runs/RBT-118/` holds only `prior/` and
`prior-adversary/`. So the §9.1 fallback applies, and **it was costed**, at +46–57 core-h, giving the programme total
2,090–2,740.

**S2: one anchor has no S arm to fork from.**
- **The gap:** `c0-p030-U-L` (W118-b) is **not a Stage-1 point**. Stage 1's legacy-smell points are c = 1 only. So the
  fallback's M and N there have no S season-60 state to fork.
- **The fix:** add S 0–59 at seeds 129001–129008 there, 2.7–3.3 core-h. Or reuse the census's three season-60
  states, which are exact fork sources, and run five more (1.7–2.1 core-h).
- **Where:** the Stage-1 launcher must include these jobs. The +46–57 is otherwise right.

**Which Stage 0 cells need the new PENDING gates?** All 18 PAYS cells need all of them. No subset can run early.
- **The ruled eating rule (RBT-125 §C).** It sits in every block, so it gates the whole of Stage P and Stage 0, not
  only PAYS. READINESS says so.
- **§A's prize harness** (designed prize at a = 6). It is merged (#430), but it was written for the committed rule. It
  must run under the sweep's block.
- **§B's nose-step against speed-step harness.** It is needed for **both** faunas at all 18 cells, since r4 §5.1 also
  asks the holistic PAYS for "its nose step against a speed step". `runs/RBT-125/gate/steps.py` exists, but it is built
  on RBT-113's designed hosts under the committed eating rule. It needs a sweep-block and holistic-host version.
- **`steer.py` and G8(c)** for the holistic prize, at every cell.

The `pays` guard checks only for `steer.py`. **S5 also covers this:** require the §B harness path and the ruled eating
rule's token before `pays` emits.

**S6: the eating-rule default.** `--eat` defaults silently to the candidate `--eat-from root`, while gate 4c is
pending. Require `--eat` explicitly at `emit` and `prelaunch` until the ruling lands. It is already recorded in
`launch.txt`.

## 7. The runner: `durable.sh` makes every job last at least 20 minutes (MUST L4)

**The problem.** `_ecology` starts `durable.sh every 20 DIR LABEL` beside the run and then waits for both.
`durable.sh`'s loop sleeps first, and checks `DURABLE_WATCH_PID` only after the sleep. Measured with `every 1` on a
3-second stand-in: the job returned after **60 s** (`probe_launch_durable.txt`). At the launcher's 20, **no job returns
in under 20 minutes.**

**The effect on the census.** A census job runs about 10 min at 20 core-s (12.5 min at 25). Hosts 8 and 9 hold 33
census jobs each. Those lanes take **33 × 20 min = 11.0 h**, against the plan's 5.5–7.1 h. Every other lane waits the
same on its census jobs and its short pilot jobs (S60, K1ref, K1fork). The cores sit idle, so the core-hours do not
change. But the census and pilot wall time roughly doubles, and the plan's 5.7–7.1 h figure is wrong.

**The fix:** when the ecology process exits, stop the `every` loop, killing its sleep, and take one synchronous
`durable.sh save`.

**Better still (S):** skip `durable.sh` for jobs shorter than the interval, that is census, K1 and S60, which rerun in
minutes. Every snapshot also creates an undeletable `ckpt/rbt-129-*` branch (sessions get 403 on delete). There are
277 today, and P and 0 would add about 540: 450 census, 64 pilot and 8 K1.

## 8. Smaller items

- **S7: Stage 1 can reuse the census.** Census S 0–59 at seeds 129001–129003 is the same run as Stage 1's S arms'
  first 60 seasons at the 36 Stage-1 points: same block, seed and stream. Resuming Stage 1 from the census states
  saves about 36 core-h. The pilot's S60 also re-runs 12 census jobs, about 4 core-h. Either reuse them, or state that
  the duplication is deliberate as a check. A byte comparison would make a free K1-type control.
- **S9: absolute paths in lane files.** Lane files carry absolute `dir` and `worlds` paths from the emitting host.
  Store them relative to the repository root, so a session checked out elsewhere cannot write outside it.
- **NIT-1: the docstring's `--fair` form fails.** `stages.py`'s docstring shows `emit … --fair '--fair'`, which
  argparse rejects ("expected one argument"). Write `--fair=--fair`, as READINESS does.
- **NIT-3: the tests encode the loophole.** They encode the L1 bypass as intended behaviour (§4).

## 9. PR #437: RBT-125 §B's nose-step harness, reused for Stage 0's designed PAYS cells

`probe_launch_harness.txt` was run on a scratch tree: #435, plus #432 merged as in L3, plus #437's `steps.py`, with the
integration branch's `steps.py` beside it. No physics bout ran. For (a) and (d), the Pool is faked as in #437's own
tests. For (b), a real fork Pool runs an introspection function. #437's own 3 tests pass once `scipy` is installed.

**(a) Does `--config` see everything a Stage 0 block sets? Yes.**
- **Every `--fair` value lives in `"sim"`.** In `c2-p030-PW-G` and `c0-p030-HP-L`, `--fair` changes
  `sim.settle_max`, `sim.settle_until_rest`, `sim.world.ball_cone`, `sim.world.hinge_range` and
  `sim.world.motor_budget`. Only the top-level marker `fairness` lies outside `"sim"`. `mass_budget` is already 15.34
  in the base world, under `sim.synthesis`.
- **Every RBT-125 setting lives in `sim.food`:** `smell_contrast`, `smell_tau`, `eat_from`, `smell`, `decay`, the
  patches and `regrow_delay`.
- **The round trip is exact:** `SimConfig.from_dict(sim).to_dict()` returns every key.
- **What sits outside `"sim"` cannot reach a bout.** The only fairness-adjacent field outside it is
  `mutation.effector_bias_sigma`, which is not in the preset anyway. It is a mutation setting, and a fixed-controller
  host bout never mutates.
- **So no PAYS bout can run silently unfair or on the wrong channel through `--config`.**

Two interface gaps remain:
- **S11: the file `stages.py pays` hands over cannot be read.** `stages.py pays` passes `{world}` =
  `worlds/<id>.json`. That is a *block* (`id`, `axes`, `fair`, `argv`, `block`, …), not a `config.json`. So
  `steps.py --config` on it fails with **KeyError 'sim'**. It fails loudly, not silently, but Stage 0's designed PAYS
  cannot run as wired. Either `emit` writes a real `config.json` per PAYS cell (for example
  `worlds/<id>.config.json`, from `blocks.config_dict`) and `pays` passes that, or `steps.py` accepts a block.
- **S12: a config's fairness is never checked.** `steps.py --config` reads `"sim"` and ignores the `fairness` marker.
  So a `config.json` from a pre-RBT-128 or `--unfair-i-know` run would be accepted, and the bout would run unfair. When
  `--config` is given, assert `cfg.get("fairness") == "fair"`, and print it.

**(b) Do fork children see `SEEDS[:]`? Yes.** Every child pid saw the mutated `SEEDS`, `HOST` and `rp.RUN["cell"]`.
The mutation is safe because `steps.py` pins `get_context("fork")`. The paired bouts carry their seed in the task
tuple anyway, so only the parent reads `SEEDS`.

**(c) Does the host refusal work? Mostly.** `routed.unit_indices`:

| host | result |
|---|---|
| Pioneer, evolved layout (food nose and effector on each wheel) | accepted |
| Pioneer with no food nose | refused |
| Pioneer with the left wheel's nose removed | refused |
| random holistic genotype | refused |

It checks only the wheel nodes' brain layout, not the body. **A Pioneer brain on a reshaped chassis, which
`fair.is_designed` rejects, is accepted.**

**S13:** also require `fair.is_designed(g)` for every line of `--hosts-file`. The designed PAYS cell must run on
designed bodies.

**(d) Are the defaults the registered §B run? Yes.** With the registered argv (`HOSTS_ROOT U-G2.5`, no new flag), the
integration branch's `steps.py` and #437's produce **identical stdout and identical task lists**: 17,760 tasks, seeds
125000–125127. That matches the amended registration's 128 paired seeds (REGISTRATION.md §B).

**Verdict on #437: MERGE.** S11 must be fixed before Stage 0's PAYS cells are emitted, but that fix is on the #435 side
or can be made in either PR. S12 and S13 are one-line guards.

## 10. The list

**MUST**
- **L1:** `check_fair` requires exactly `--fair`, refuses `--unfair-i-know`, and asserts `fairness == "fair"` and the
  preset values in every block. `run-lane` re-derives each fresh job's block from `launch.txt` and refuses on a
  difference.
- **L2:** `run-lane` refuses unless the session's `rabbitstew` and launcher trees equal `launch.txt`'s, and the
  launcher, worlds and lanes are clean.
- **L3:** merge #432 with `fair.expand` in `ecology_configs`, and the guard in `cmd_ecology` after resume. Add the two
  tests.
- **L4:** the runner must not wait on `durable.sh`'s sleep. Take one final save on exit, and preferably no durable
  loop for census, K1 and S60.

**SHOULD**
- **S1:** P's excess comes from N at full cost and from K1, not from the planted set.
- **S2:** add the W118-b S60 jobs to the anchor fallback.
- **S3:** K1 compares every output file.
- **S4:** emit the planted-set jobs, or say that `steer.py` makes them.
- **S5:** pin `steer.py`'s version, and gate `pays` on the §B harness and the eating rule.
- **S6:** make `--eat` explicit until the ruling.
- **S7:** reuse the census and pilot S60 states.
- **S8:** rename "unreachable" and add the deep share.
- **S9:** relative paths in lane files.
- **S10:** state that `effector_bias_sigma` is outside `--fair`.

**SHOULD, for #437 (§9)**
- **S11:** `pays` must hand `steps.py` a real `config.json`, not a block.
- **S12:** `steps.py --config` asserts `fairness == "fair"`.
- **S13:** `--hosts-file` also requires `fair.is_designed`.

**NIT:** NIT-1 to NIT-3.

With L1–L4 fixed, #435 can merge. #437 can merge now, with S11–S13 folded in before Stage 0's PAYS cells are
emitted. Stage P and Stage 0 can then fire as soon as #432 lands and the eating rule is ruled.

---
_Generated by [Claude Code](https://claude.ai/code)_
