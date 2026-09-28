# RBT-129: launch readiness

*Written 2026-09-28, 02:00 UTC, on integration at `626ca4c` (#430). It covers the gates of DESIGN r4 §11.1, the
pre-launch prints of §3.1 and §5.3(a), and the Stage P and Stage 0 launchers. **No sweep arm, cell or founder has run.**
The runner was exercised only on a tiny non-sweep world, in the tests.*

## 1. The gates (DESIGN §11.1), gate by gate

| # | gate | status | evidence |
|---|---|---|---|
| 1 | RBT-120 (motor budget) merged | **MET** | #409 `f07700a` (`--motor-budget`, `motor_report.py`); B1–B4 #426–#429 |
| 2 | RBT-124 (physics pack) merged | **MET** | #420 `d7d93df` (`--ball-cone`, `--hinge-range`, `--effector-bias-sigma`, `--settle-until-rest`); adversary FIX-CHECK #423 `3b8927c` |
| 3 | RBT-128 (`--fair` and its guard) merged | **PENDING**, coordinator ETA about 03:00 | Not on integration: `ecology` has no `--fair` option. The launchers take the fairness flags as a parameter (`--fair=...`) and **refuse (exit 4)** until every flag is an `ecology` option on the tree. Tested: `test_the_guards_refuse_on_this_tree` |
| 4a | RBT-125 merged: channel, G registered, eating rules | **MET** | #414/#418 `589cad8`; code ruling `c591a75` |
| 4b | RBT-125 world gate passed on real bodies | **MET**: §A PASS at G = 2.5, τ = 2 s | #430 `626ca4c` (`runs/RBT-125/gate/READOUT.md`: prize +0.614 [+0.276, +0.951]; channel contrast +0.488 [+0.155, +0.822]); adversary #431 `7061d30`, CONFIRMED WITH CAVEATS |
| 4c | the eating rule as RBT-125 rules it (DESIGN §2) | **PENDING** (RBT-125 §C, the eating rules' side effects) | Every block takes the rule as a parameter (`--eat`). The default is the design's candidate, `--eat-from root`, and the launchers print the rule they were given. The coordinator must pass the ruled rule at `emit` |
| 5 | RBT-126 merged (readout, screen; the committed shuffle registered) | **MET** | #415 `e3c9473`; adversary #417 `d1eb1ae`. Not a gate, but present: `--breed-rule` and `--breed-gate none` (#419 `b7987da`, #422 `8cabd7f`), so R_drift may run |
| 6 | RBT-118 adopts the seed coordination at the anchors (§9.1), **or** the sweep's own anchor arms are budgeted | **MET by the fallback** | **RBT-118 has no registration.** Integration's `runs/RBT-118/` holds only the exploratory prior and its adversary (#399, #402). No registration adopts seeds 129001–129008 or the 240–299 window. **The sweep therefore adopts its own M and N arms at the three anchors** (W118-a/b/c; §9.1's fallback), budgeted at +46–57 core-h (§11.2's optional row, r4 S3-4). The programme total becomes **2,090–2,740 core-h**. The anchor arms are Stage-1 arms, so nothing in Stage P or 0 waits on this. If RBT-118 registers the coordination before Stage 1, the coordinator may drop the fallback |
| 7 | RBT-129a merged, with its test list (§5.6) | **MET** | = RBT-130: #424 `6638da9` (fixes `bb3d55d`), adversary #425 `d4c4c73`. Items 1–4 and 6 are covered in `tests/test_rbt130.py` (36 tests). **Item 5, the world-block export, was not in RBT-130; it is in this PR** (`launch/blocks.py`, `tests/test_rbt129_launch.py`) |
| 8 | RBT-116's `steer.py` committed at its ruled version | **PENDING**: RBT-116 (session_01687azyvbVUH3VRGHVw8fiU), PR ETA about 04:00 | Not on integration: `runs/RBT-116/` has no `steer.py`. Stage P's probes and planted set, and Stage 0's 18 PAYS cells, **refuse (exit 6)** until the file exists and its ruled command line is given as a template. Tested: `test_the_steer_guard_refuses_until_the_file_exists` |
| 9 | the design adversary's MUSTs ruled and re-checked | **MET** | #416 (first review, R2-CHECK, R3-CHECK); r4 registered at `7a22d90` (#412) |
| — | RBT-127 (versions in `config.json`); expected, not gating | **MET** | #411 `6aaf5689` (`platform.json` beside each run) |
| — | RBT-129b (moving patches); conditional, unbudgeted | not started | MP has no block. It enters only by its own flag ticket (§3.3) |

**Before Stage P can fire:** RBT-128 must merge (gate 3), and the eating rule must be ruled (4c). **Before the
pilot's probes and the census's PAYS cells:** `steer.py` (gate 8), and for the designed PAYS nose step, RBT-125 §B's
harness. The S, M and N arms and the census arms need only gate 3 and 4c.

## 2. The pre-launch prints (DESIGN §3.1, §5.3(a), adversary S4)

**These use committed fixtures only.** `launch/prints.py` → `launch/prints.txt`:
- 100 fresh arenas per (clutter, layout) for the unreachable share;
- 16 solo seasons per (clutter, layout, fixture) for food per cell;
- terrain and start seeds 0–99 and 1000–1015, not the sweep's.

About 2 minutes on 4 cores. Both prints read each point's world from its block's own `config.json`, the printing path.

**The world-block export (§2, §5.6 item 5).** `launch/blocks.py` builds all 150 points from one table:
- **ids** are `c<c>-p<ppp>-<L>-<s>`, with `c05` and `c15` for the half levels;
- **N** is 0/7/14/21/28 in U and HP, and PW's registered free-area counts 16/32/48/64 at `--obstacle-radius 3.6`;
- **c = 0** is `--terrain flat`.

Each block holds the `ecology` flags and the world as dotted config paths. Those paths are read from the
`config.json` that `ecology` itself writes. `cli.ecology_configs` is a pure extraction from `cmd_ecology`, and RBT-126's
CLI goldens pin its bytes. The test `test_a_block_is_the_config_json_the_ecology_writes` constructs the `Ecology`, which
writes `config.json` and runs no season, and compares. `stages.py emit` exports the launch's blocks to
`runs/RBT-129/worlds/<id>.json`. They are not committed now, because they would carry a pending `--fair`.

**Unreachable items.** This is the share of items inside an obstacle's ground footprint, the registered definition, and
apart, inside one taller than 0.1 m:

| c | U | HP | PW |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0.5 | 0.095 (0.045) | 0.043 (0.018) | 0.035 (0.014) |
| 1 | 0.124 (0.061) | 0.086 (0.036) | 0.098 (0.049) |
| 1.5 | 0.160 (0.085) | 0.118 (0.053) | 0.138 (0.069) |
| 2 | 0.194 (0.106) | 0.144 (0.065) | 0.167 (0.083) |

Clutter taxes food as §3.1 says: at the committed density, 1 item in 8 lies under an obstacle in U. HP and PW sit
lower than U at every level. This PR does not decompose why.

**Food per new cell** covered, in items per 100 new 0.35 m cells (`prints.txt` has every row). The fixtures:
- **the designed body:** the Pioneer driving straight;
- **the holistic stand-in:** RBT-125 §C's blind full-throttle rod.

Both are fixtures, not faunas, and the figures are descriptive. What they show:
- **Clutter shrinks the straight driver's new ground.** In U, 102 cells a season on flat ground falls to 33 at c = 2,
  and its items per 100 cells from 0.49 to 0.19.
- **The spinning rod covers about 30 cells everywhere**, and eats under the root rule.

The sweep's own per-fauna figure comes from `steer.py`'s probed members (§5.3(a)). `stages.py prelaunch` re-runs both
prints under the launch block (`--fair` and the ruled eating rule), to `lanes/prelaunch_prints.txt`.

## 3. The Stage P and Stage 0 launchers (`launch/stages.py`)

`stages.py plan P,0` prints the plan without running anything:

| stage | what | arm-seasons | core-h, 20 core-s | core-h, 25 core-s | DESIGN §11.2 line |
|---|---|---|---|---|---|
| **P** | 4 points (`c1-p030-U-L`, `c0-p030-U-L`, `c1-p030-PW-G`, `c2-p030-PW-G`) × seeds 129001–129004. Per point and seed: S 0–299, a checkpoint at 60, then S resumed; M and N forked from the season-60 state (60–299), N on all 4 seeds (odd seeds holistic, even designed). K1 per point on seed 129001. Probes 0.46–0.83 core-h a seed; planted set 0.8 core-h a point | 12,760 | 81.4–87.4 | 99.2–105.1 | 77–83 / 93–99 |
| **0** | 150 points × seeds 129001–129003, S 0–59; plus 18 PAYS cells | 27,000 | 195.0 | 232.5 | 195 / 232 |

- **P is above its r4 line by 4.4–6.1 core-h.** The r4 table left out two costs: the planted set at the pilot
  (4 × 0.8), and K1's straight comparison run (to season 65, one seed a point).
- **K1 compares two runs**, a straight run to 65 and the fork of the season-60 state with the merge unset. It passes
  when their `lineage.jsonl`, `cohorts.jsonl` and `history.json` are byte-identical. It writes `K1.txt`, the control's
  verdict and no outcome.
- **Programme total:** 2,090–2,740 core-h, the DESIGN total with the adopted anchor fallback. That is inside the brief's
  2,200–2,900 envelope.

**Host layout.** Ten 4-core sessions, two lanes each at WORKERS = 2:
- **Seeds by lane:** lane 0 takes the odd seeds, and lane 1 the even ones.
- **The split seed:** census seed 129003 is split between the classes to balance load. Lane 0 runs its share first and
  lane 1 runs its share last.
- **The lock:** a per-seed lock (`/tmp/rbt129-locks`) makes the rule hard, so a session's two lanes never run one seed
  at once (RBT-107's packing rule).
- **Balance:** every lane carries 1,980–2,040 arm-seasons.
- **Wall time:** 5.7 h at 20 core-s and 7.1 h at 25 for P and 0 together, before probes and PAYS. §11.2 says "about 7 h".

**The runner** (`run-lane`):
- **It refuses (exit 3, 5, 4):**
  - off x86_64;
  - with uncommitted changes under `rabbitstew/`;
  - on a block whose fairness flags the tree lacks.
- **It records:** the command, `run.log`, and a done-marker per job.
- **It resumes:**
  - a job with a `state.json` resumes from it;
  - a job that never finished a season is deleted and rerun;
  - `scripts/durable.sh every 20` snapshots each run directory to its own `ckpt/rbt-129-<path>` branch, with its
    done-markers, and the snapshot is restored when the container is lost;
  - the season-60 checkpoint is saved once to its own branch. If it is lost after S has moved on, the snapshot job
    refuses rather than copying a later state.
- **No-peek:** it prints job names, times and exit codes only.

The whole chain has been exercised on a tiny non-sweep world (`test_the_runner_forks_and_checks_k1_on_a_tiny_world`):
fresh to the checkpoint, snapshot, resume, the M and N forks, and K1, which passes.

### Firing, in minutes, once the gates land

```bash
# after RBT-128 merges (and the eating rule is ruled): on a clean integration checkout
python runs/RBT-129/launch/stages.py prelaunch --fair=--fair --eat="--eat-from root"   # the prints under the launch block
python runs/RBT-129/launch/stages.py plan P,0
python runs/RBT-129/launch/stages.py emit P,0 --fair=--fair --eat="--eat-from root"    # worlds/<id>.json, lanes/P-0/*.jsonl, launch.txt
# commit worlds/ and lanes/ to the launch branch, so that every session runs the same files; then on session h (0-9),
# two harness background tasks:
WORKERS=2 python runs/RBT-129/launch/stages.py run-lane runs/RBT-129/lanes/P-0/host<h>-lane0.jsonl
WORKERS=2 python runs/RBT-129/launch/stages.py run-lane runs/RBT-129/lanes/P-0/host<h>-lane1.jsonl

# after steer.py merges: the pilot's probes and planted set, and the census's PAYS cells, from the ruled command line
python runs/RBT-129/launch/stages.py probes --steer runs/RBT-116/steer.py --steer-cmd '<ruled CLI: {run} {season} {seed} {rng} {point} {out}>'
python runs/RBT-129/launch/stages.py pays   --steer runs/RBT-116/steer.py --pays-cmd  '<ruled CLI: {point} {world} {out}>'
```

`--fair=--fair` stands for RBT-128's merged flag set, whatever it is called. Pass the exact flags it merges.

## 4. Open items for the coordinator

1. **The eating rule** (gate 4c) is still to be ruled. The launch default is the design's candidate, `--eat-from root`.
2. **The anchor fallback is adopted** (gate 6), because RBT-118 has no registration. Please confirm; it costs +46–57
   core-h at Stage 1.
3. **P's cost** is 4.4–6.1 core-h over its r4 line, for the planted set and K1. This is within the envelope, but it is
   a budget line to note.
4. **Census check C3** (the motors-off drift of 20 founders per fauna on c = 2) is not scripted here. It needs the
   probe instrument's motors-off condition, and runs with Stage P's probe set once `steer.py` lands.
5. **Stage 0's designed PAYS** also needs RBT-125 §B's nose-step-against-speed-step harness (pending). It is covered
   by the same `pays` guard.
