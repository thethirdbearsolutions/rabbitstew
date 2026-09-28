# RBT-129: launch readiness

*Written 2026-09-28, 02:00 UTC, on integration at `626ca4c` (#430). Updated at 02:30 with RBT-128 #432 (`e7b8865`)
merged into this branch, and at 03:00 with the launch adversary's fixes (#439, #441; coordinator ruling 02:22: L1–L4,
every SHOULD, and the §12.1 amendment), and at 03:20 with integration merged in (#432 at `42261bd`, #437 at `4c32cec`),
the eating rule as re-ruled at 03:10 (root + surface), and #441's S11; and at 04:20 with R1 (launch FIX-CHECK #447) and
integration with RBT-125 #446 (`01f113d`) merged in.*

It covers:
- the gates of DESIGN r4 §11.1;
- the pre-launch prints of §3.1 and §5.3(a);
- the Stage P and Stage 0 launchers.

**No sweep arm, cell or founder has run.** The runner was exercised only on a tiny non-sweep world, in the tests.

## 1. The gates (DESIGN §11.1), gate by gate

| # | gate | status | evidence |
|---|---|---|---|
| 1 | RBT-120 (motor budget) merged | **MET** | #409 `f07700a` (`--motor-budget`, `motor_report.py`); B1–B4 #426–#429 |
| 2 | RBT-124 (physics pack) merged | **MET** | #420 `d7d93df` (`--ball-cone`, `--hinge-range`, `--effector-bias-sigma`, `--settle-until-rest`); adversary FIX-CHECK #423 `3b8927c` |
| 3 | RBT-128 (`--fair` and its guard) merged | **MET** | #432 merged at `42261bd` (FIX-CHECK #444), and integration is merged into this branch (L3, below). What the launchers require of every block is listed after this table. On this tree, **all 150 blocks pass** `fair.check` and the launcher's own checks, and a block built with `--unfair-i-know` fails 14 of them |
| 4a | RBT-125 merged: channel, G registered, eating rules | **MET** | #414/#418 `589cad8`; code ruling `c591a75` |
| 4b | RBT-125 world gate passed on real bodies | **MET**: §A PASS at G = 2.5, τ = 2 s | #430 `626ca4c` (`runs/RBT-125/gate/READOUT.md`: prize +0.614 [+0.276, +0.951]; channel contrast +0.488 [+0.155, +0.822]); adversary #431 `7061d30`, CONFIRMED WITH CAVEATS |
| 4c | the eating rule as RBT-125 rules it (DESIGN §2) | **MET**: re-ruled 03:10 to `--eat-from root --eat-rule surface` (coordinator on #436; §C adversary #445) | This is within §2's "as RBT-125 rules it (candidate `eat_from root`)", and the living cost is still not recalibrated per point. It is the launchers' default (`blocks.EAT_RULED`), and **`check_eat` accepts exactly it and nothing else** (R1). It is recorded in `launch.txt` and rebuilt from there by `run-lane`. **Root + surface's side effects are reported beside every call**, e.g. the blind tumbler's +1.30 against +0.70 in U (RBT-125 §C) |
| 4d | the surface-clearance fix under `clear_from = root` (RBT-125 #446) | **MET**: #446 merged at `01f113d` as the minimal guard (no item within `eat_radius` of an eating geom's surface, on top of the root-centre clearance; `food_fallbacks` counted) | **Every surface launch refuses (exit 4) without it** (R1 (2)). `stages.surface_clearance_ok()` probes the behaviour, not the code: a 1.39 m bar root in a root + surface food world, where every item must clear the bar's surface by `eat_radius` and its centre by `clearance`. It reads False on the pre-#446 tree (`fde1824`, checked in a worktree) and True on this one. Tests: `test_r1_the_surface_probe_refuses_a_tree_that_clears_from_the_root_centre` and `..._passes_a_tree_that_clears_by_surface` |
| 5 | RBT-126 merged (readout, screen; the committed shuffle registered) | **MET** | #415 `e3c9473`; adversary #417 `d1eb1ae`. Not a gate, but present: `--breed-rule` and `--breed-gate none` (#419 `b7987da`, #422 `8cabd7f`), so R_drift may run |
| 6 | RBT-118 adopts the seed coordination at the anchors (§9.1), **or** the sweep's own anchor arms are budgeted | **MET by the fallback** | RBT-118 has no registration: `runs/RBT-118/` holds only the exploratory prior and its adversary (#399, #402). The sweep adopts its own M and N arms at W118-a/b/c (+46–57 core-h), for a programme total of **2,090–2,740 core-h**. W118-b needs S seasons 0–59 at seeds 129001–129008 to fork from, because it is not a Stage-1 point; stage **A** makes the four the census and pilot do not (S2, §3) |
| 7 | RBT-129a merged, with its test list (§5.6) | **MET** | = RBT-130: #424 `6638da9` (fixes `bb3d55d`), adversary #425 `d4c4c73`. Items 1–4 and 6 are covered in `tests/test_rbt130.py`. Item 5, the world-block export, is in this PR |
| 8 | RBT-116's `steer.py` committed at its ruled version | **PENDING**: #434, ruled MERGE AFTER FIXES (#440 `fea3bf3`) | `probes` and `pays` refuse (exit 6) unless `steer.py` exists **at its ruled git blob hash** (`--steer-sha`; S5) and every command template is given, including the planted set's (S4) |
| 9 | the design adversary's MUSTs ruled and re-checked | **MET** | #416 (first review, R2-CHECK, R3-CHECK); r4 registered at `7a22d90` (#412) |
| 10 | RBT-125 §B's nose-step harness, for Stage 0's PAYS (coordinator 02:06) | **MET**: #437 merged at `4c32cec`, with the S12 fairness and S13 designed-host guards | `pays` refuses (exit 6) unless the harness file exists at its ruled blob hash (`--steps-harness`, `--steps-sha`) and `--steps-cmd` is given (S5). It hands `steps.py --config` the cell's real `worlds/<id>.config.json`, which `emit` now writes (S11); `test_s11_the_pays_config_json_is_what_steps_py_reads` runs `steps.py` on it |
| — | RBT-127 (versions in `config.json`); expected, not gating | **MET** | #411 `6aaf5689` (`platform.json` beside each run) |
| — | RBT-129b (moving patches); conditional, unbudgeted | not started | MP has no block |

**What the launchers require of every block (L1; coordinator 02:17 (3)).** The fairness tokens must be exactly
`--fair`. `--unfair-i-know`, a hand-set preset flag, or any other list is refused. Every block that `emit`,
`prelaunch`, `pays-prize`, `probes` or `pays` builds must also pass `stages.fair_deviations`:
- the marker `"fairness": "fair"`;
- every value of `rabbitstew.fair.PRESET`, read from the block's own `config.json`;
- RBT-128's `fair.check(config)`, which is required.

`run-lane` rebuilds every fresh job's world block from `launch.txt`'s flags, and refuses one that differs from
`worlds/<id>.json`. Tests: `test_the_fair_guard`, `test_every_block_must_be_the_ruled_set` and
`test_run_lane_refuses_an_edited_block`.

**L3: the #432 resolution.** It is the adversary's scratch-merge resolution:
- `fair.expand` sits at the top of `cli.ecology_configs`, so blocks and arms carry the marker and the preset's
  values;
- `cmd_ecology` keeps the resume branch first, then `expand`, `guard` and `announce`, so a resume never meets the
  guard.

Tests:
- `test_a_fair_block_is_the_config_json_the_ecology_writes_key_for_key`: under `--fair`, the block equals `ecology`'s
  own `config.json` key for key, and every preset value except `effector_bias_sigma` sits in the `"sim"` section,
  which is all the PAYS harnesses read (FIX-CHECK note on #437);
- `test_the_cli_run_under_fair_writes_the_block`: the CLI writes the same config; a run with neither flag is refused;
  a resume passes.

**The final fold is done.** Integration, with #432 (`42261bd`), is merged here:
- `cmd_ecology` takes their resume note, `fair.note_resume`, and their guard on every fresh ecology, `--only-fauna`
  included;
- `ecology_configs` keeps the expansion.

The merge was clean.

**Stage P and Stage 0 can fire** once this PR merges: every gate they need is met. `prelaunch` then re-prints under the
launch block.
**Before the pilot's probes and the census's PAYS legs:** gate 8, `steer.py`.

**The retention arms** (coordinator 02:17 (2)). Every arm built from a block carries `--fair`, including a
single-fauna `--only-fauna` arm, so RBT-128's guard on `--only-fauna` meets no retention arm without it.
**`effector_bias_sigma`** (S10): RBT-128 has ruled S = 0 into `--fair` (`f8f903e`). Every block now carries
`mutation.effector_bias_sigma = 0.0`. It lives in the `mutation` section, which fixed-host harnesses never read, and
does not change a fixed fixture's bout. The prints are unaffected.

## 2. The pre-launch prints (DESIGN §3.1, §5.3(a), adversary S4)

`launch/prints.py --fair=--fair` → `launch/prints.txt`, under the launch block. It uses committed fixtures only, on
draws that are not the sweep's seeds. `prints_prefair.txt` is the same print without `--fair`. The footprint shares
are identical in the two; only the rod's rows differ.

**The world-block export (§2, §5.6 item 5).** `launch/blocks.py` builds all 150 points from one table:
- **ids** are `c<c>-p<ppp>-<L>-<s>`;
- **N** is 0/7/14/21/28 in U and HP, and 16/32/48/64 at `--obstacle-radius 3.6` in PW;
- **c = 0** is `--terrain flat`.

Each block holds the `ecology` flags and the world as dotted config paths. Those paths are read from the
`config.json` that `ecology` itself writes. The launch adversary checked all 150 against r4's axes and the committed
world, key for key.

**Items inside a footprint, and out of reach** (S8). "Inside a footprint" is what DESIGN §3.1 calls "unreachable".
Only the **reach-limited** share is actually out of reach: items inside a footprint taller than 0.1 m (a lower bump can
be driven over) **and** deeper than a root at the edge reaches.
- **Under the ruled root + surface, on this tree with #446** (`prints.txt`): the eat radius, 0.35 m, is measured from
  the root's surface. Footprints are at most 0.7 m across, so **no item is out of reach by geometry**, and the
  reach-limited share is 0 at every level. **`food_fallbacks` is 0** at every clutter level and layout, both in the
  1,200-item fresh arenas and in the fixtures' seasons.
- **The footprint shares under root + surface with #446 are identical** to those without it, and to centre eating's.
  #446's minimal guard leaves a compact-root body's world exactly as it was, and the fixtures' four spawns have compact
  Pioneer roots. The full shares are in the table.
- **Under the old candidate, centre eating** (`prints_prefair.txt`): the reach is the xy radius less the root's
  half-width, 0.20 m, which gives the reach-limited shares after the slash.

| c | U: inside / reach-limited (centre) | HP | PW |
|---|---|---|---|
| 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| 0.5 | 0.095 / 0.005 | 0.043 / 0.002 | 0.035 / 0.003 |
| 1 | 0.124 / 0.006 | 0.086 / 0.002 | 0.098 / 0.005 |
| 1.5 | 0.160 / 0.007 | 0.118 / 0.002 | 0.138 / 0.007 |
| 2 | 0.194 / 0.008 | 0.144 / 0.003 | 0.167 / 0.009 |

**Under centre eating clutter hid 0.2–0.9% of the food out of reach, and under root + surface it hides none**, not up to
19%. The footprint shares themselves are the same under both rules on this tree. By the launch adversary's arithmetic, even the
footprint share could shift x = H − D by at most +0.047, under δ_i = 0.15. U is taxed 1.3–1.4× more than HP at the same
c. That is an L × c term that M2's point random intercept absorbs.

**Food per new cell** (items per 100 new 0.35 m cells, 16 solo seasons each; `prints.txt` prints the SEs, NIT-2):
- **The straight-driving Pioneer:** its new ground falls from 102 cells a season on flat U (SE 1.5) to 33 at c = 2
  (SE 11). Its items per season (0.06–0.50, SE up to 0.22) are too noisy to rank the clutter levels.
- **The blind rod (RBT-125 §C) under `--fair`:** it no longer moves, covering 0.4 cells a season against about 30
  without. The cause is the preset's ±π/2 hinge range, checked by switching the range off. So it is no longer a
  coverage stand-in, and the holistic figure waits for `steer.py`'s probed members (§5.3(a)).

## 3. The Stage P and Stage 0 launchers (`launch/stages.py`)

`stages.py plan P,0` prints the plan without running anything:

| stage | what | arm-seasons | core-h, 20 core-s | core-h, 25 core-s | DESIGN §11.2 line |
|---|---|---|---|---|---|
| **P** | 4 points × seeds 129001–129004 (details below the table) | 12,760 | 81.4–87.4 | 99.2–105.1 | 77–83 / 93–99 |
| **0** | 150 points × seeds 129001–129003, S seasons 0–59; plus the 18 PAYS cells (split below) | 27,000 | 195.0 | 232.5 | 195 / 232 |
| **A** | S seasons 0–59 at W118-b (`c0-p030-U-L`), seeds 129005–129008: the anchor fallback's fork sources that the census (129001–129003) and pilot (129001–129004) do not make (S2) | 240 | 1.3 | 1.7 | inside the fallback's 46–57 |

- **Stage P's four points:** `c1-p030-U-L`, `c0-p030-U-L`, `c1-p030-PW-G` and `c2-p030-PW-G`.
- **Stage P's arms:**
  - S runs seasons 0–299, with a season-60 checkpoint;
  - M and N are forked from that checkpoint;
  - N runs on all 4 seeds.
- **Stage P's extras:** K1 per point; the probes; the planted set per point.
- **P is above its r4 line** (S1) because the plan counts:
  - N at full cost, 16 × 240 arm-seasons, where r4's `prior_regime.py` counts 0.85×: **+3.2** core-h;
  - K1's straight run to 65 plus its fork, 4 × 70 arm-seasons: **+1.6**.

  The planted set was already in r4. The programme total, **2,090–2,740 core-h**, is inside the 2,200–2,900 envelope.
- **K1 compares every output file** (S3), byte for byte: genomes, `state.json`, lineage, cohorts and history. It
  excludes `config.json`, which the fork rewrites, and `platform.json` and the logs. r4's `seasons.txt` is
  `history.json`.
- **A real finding from that comparison:** `ecology` writes `<kind>/final/` only when a run ends, one file per member,
  and never clears it. A resumed or forked run whose population shrank therefore kept the earlier run's surplus
  members there, and a probe reading `final/` would have sampled the dead.
  - **In the launcher:** `run-lane` now clears `final/` before every resume (`stages._clear_final`), and K1 passes.
  - **In the core code:** the bug is still there. It affects any other resumed run, RBT-130's forks included, so it is
    flagged for the coordinator (§4).
- **Stage 1 reuses the census** (S7). Its S arms at seeds 129001–129003 resume from the census's season-60 states,
  saving about 36 core-h. This is a dated pre-data plan note in DESIGN before §11.2. It is justified by the runner
  test's `k1_compare(K1ref, S)`: a checkpointed and resumed run equals the straight run in every file. The pilot's 12
  S60 jobs that repeat census jobs are kept on purpose, as a free byte-comparison control.

**Stage 0's split** (coordinator 02:06; S5). Each of the 18 PAYS cells is L × s × c ∈ {0, 1, 2} at p = 0.03.

| leg | needs | launch |
|---|---|---|
| the 450 census S arms (and stage A) | `--fair` (with `fair.check`), the eating rule | `emit` / `run-lane` |
| designed prize at a = 6, all 18 cells | as above, and RBT-125 §A's merged `prize_gate.py` on its ten hosts (`BODIES_ROOT/forage-SEED`); it reads only the config's `"sim"`, which carries every preset value and the eating rule | `stages.py pays-prize` |
| holistic plant (G8(c)), all 18 cells | `steer.py` at its ruled hash | `stages.py pays`, guarded |
| nose step against a +25% speed step, both faunas, all 18 cells | RBT-125 §B's harness at its ruled hash (#437) | `stages.py pays`, guarded; the harness gets the cell's real `config.json` as `{config_json}`, not the block (#441 S11) |

No cell's PAYS call is complete without §B. The census arms and the designed prize leg can launch without it.

**Host layout.** Ten 4-core sessions, two lanes each at WORKERS = 2:
- lane 0 runs the odd seeds and lane 1 the even ones;
- census seed 129003 is split between them, first on lane 0 and last on lane 1;
- a per-seed lock enforces the rule;
- every lane carries 1,980–2,040 arm-seasons.

**Wall time (L4, re-derived).** No job waits on `durable.sh`:
- **Long jobs** (120 arm-seasons or more: S resumed to 300, M, N) run `durable.sh every 20` in their own process
  group beside the run. The group is killed when the run exits, and the final save goes to the background.
- **Short jobs** (census, S60, K1, stage A) take no snapshot. They rerun in minutes, and each snapshot makes a
  checkpoint branch that sessions cannot delete.
- `test_a_job_never_waits_on_durable_sh` shows that a job returns at once beside a loop that sleeps for 120 s.
- The jobs therefore chain back to back, and the plan's line stands: **5.7 h at 20 core-s, 7.1 h at 25**, for P and 0
  together, before probes and PAYS.

**The runner** (`run-lane`) refuses to start:
- **exit 3:** off x86_64;
- **exit 5 (L2):**
  - the session's `rabbitstew/`, `runs/RBT-129/launch/` or `scripts/` tree differs from the one `launch.txt` records;
  - or anything under those, `worlds/` or `lanes/` is uncommitted;
- **exit 4 (L1):** a world block differs from what `launch.txt`'s flags build, or fails `fair_deviations`.

Lane files hold paths relative to the repository root. A path that is absolute or leaves the repository is refused
(S9). The runner prints job names, times and K1's verdict only. The emitted `probes`, `pays` and `pays-prize` scripts
re-verify every tool's git blob hash where they run, and refuse (exit 6) on a difference (R1 (4);
`test_r1_emitted_scripts_reverify_their_tools`). The whole chain has been exercised on a tiny
non-sweep world: fresh run, snapshot, resume, the M and N forks, and K1 (PASS, and FAIL on a one-byte change).

### Firing, once the gates land

```bash
# once this PR merges: on a clean integration checkout
python runs/RBT-129/launch/stages.py prelaunch --fair=--fair     # --eat defaults to the ruled root + surface
python runs/RBT-129/launch/stages.py plan P,0
python runs/RBT-129/launch/stages.py emit P,0 --fair=--fair   # worlds/, lanes/P-0/, launch.txt
# commit worlds/ and lanes/ (run-lane refuses them uncommitted); every session checks out that commit, then on session h:
WORKERS=2 python runs/RBT-129/launch/stages.py run-lane runs/RBT-129/lanes/P-0/host<h>-lane0.jsonl
WORKERS=2 python runs/RBT-129/launch/stages.py run-lane runs/RBT-129/lanes/P-0/host<h>-lane1.jsonl

# Stage 0's designed prize leg (hosts restored from ckpt/rbt-90-SEED)
python runs/RBT-129/launch/stages.py pays-prize --fair=--fair --bodies BODIES_ROOT

# after steer.py (#434) merges at its ruled version (section B, #437, is merged)
python runs/RBT-129/launch/stages.py probes --fair=--fair \
    --steer runs/RBT-116/steer.py --steer-sha <blob> --steer-cmd '<{run} {season} {seed} {rng} {point} {out}>' \
    --planted-cmd '<{point} {world} {config} {out}>'
python runs/RBT-129/launch/stages.py pays --fair=--fair \
    --steer runs/RBT-116/steer.py --steer-sha <blob> --pays-cmd '<{point} {world} {config} {out}>' \
    --steps-harness <path> --steps-sha <blob> --steps-cmd '<... --config {config_json} ... {out}>'
```

## 4. Open items for the coordinator

1. **`steer.py`** (#434) must land at its ruled version, for the probes, the planted set and the holistic PAYS legs.
2. **The core `final/` bug** (§3): `Ecology._save_populations` never clears `<kind>/final/`. The launcher works
   around it. A one-line core fix would need its own ticket, because it changes what resumed runs leave behind.
3. **Census check C3** (the motors-off drift on c = 2) is not scripted. It runs with the probe instrument's motors-off
   condition once `steer.py` lands, and may belong in the planted-set command.
