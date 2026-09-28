# RBT-129: the probe, holistic PAYS and designed prize legs — launch status

*2026-09-28, 05:20 UTC; updated 06:20 with the legs adversary's fixes (#457: L-1, L-2, S-1–S-4). The branch holds
integration through #456 (fix1/fix1b, `7f8bfea`). This PR does not touch, read or re-pin Stage P and Stage 0, which
run from #456's commit. **Nothing here has run.***

## Summary

| leg | status | runners × hours | waits on Stage P/0 outputs? |
|---|---|---|---|
| **designed prize at a = 6** (`pays-prize`; Stage 0's designed PAYS leg, all 18 cells) | **READY**: emitted in `lanes/pays-prize/` (launch record and 3 runner scripts) | 3 runners × about 4–6 h (60 jobs each); 180 jobs, about 48–72 core-h | **No.** It runs on RBT-125 §A's ten designed hosts (restored from `ckpt/rbt-90-SEED`) in the PAYS cells' own `config.json` |
| **holistic PAYS**: the G8(c) two-nose plant's F on 8 holistic hosts, at all 18 cells | **BLOCKED** (B1, B2, B4) | — | no |
| **designed nose step against a +25% speed step** (`pays-steps`; the designed half of Stage 0's nose-step leg, all 18 cells) | **READY**: emitted in `lanes/pays-steps/` | 3 runners × about 3 h (6 cells each); 18 cells × about 17,500 seasons × 0.36 core-s, about 31 core-h | **No.** RBT-125 §B's `steps.py` (#437), unchanged, on its registered hosts (RBT-113 O1's 15 designed finals, from `ckpt/rbt-113-O1`) and 128 seeds, in each cell's verified `worlds/config/<id>` (L-1) |
| **holistic nose step** at all 18 cells | **BLOCKED** (B3) | — | no |
| **Stage P probes**: 20 members per fauna per seed at seasons 0 and 300, plus the planted set per point | **BLOCKED** (B1–B4) | — | **Yes.** The members are Stage P's S-arm members, so this leg waits for Stage P to report DONE (about 10:00–11:30) whatever else is fixed |

## The two designed legs, as emitted (`pays-prize` and `pays-steps`)

- **`lanes/pays-prize/launch.txt` and `lanes/pays-steps/launch.txt`** each record:
  - the commit the legs were emitted on;
  - the pinned trees: `rabbitstew/` and `scripts/` equal to `ce69f17`'s, and `runs/RBT-129/launch/` equal to this PR's;
  - `--fair` and `--eat-from root --eat-rule surface`;
  - the 18 cells;
  - **per leg, exactly the tools it runs, with their import chain** (S-1):
    - prize: `prize_gate.py`, `routed_populations.py`, RBT-97's `routed_p801.py` and `g500_direction.py`;
    - steps: the same four, plus `steps.py`.

    `steer.py` is not pinned, so RBT-132's change to it cannot stop the designed legs.
- **Every leg reads only verified files** (L-1).
  - The prize leg's `--config-from` and the step leg's `--config` are both the cell's `worlds/config/<id>`
    directory: the file `verify` rebuilds and checks.
  - A committed edit to it (motor budget, centre eating) is refused with exit 4. Tested:
    `test_l1_an_edited_steps_input_is_refused`.
- **Each `runnerK.sh` starts with its leg's host guards** (`stages.py verify`):
  - **exit 3:** not x86_64;
  - **exit 5:** the pinned trees are not launch.txt's, or the checkout is not clean;
  - **exit 4:** the fairness or eating flags are not exactly the ruled ones, #446's surface clearance is missing, or a
    cell's `config.json` is not what the flags build or fails `fair.check`;
  - **exit 6:** a tool blob has changed.
- **Each runner then restores the hosts it needs**, and refuses with exit 7 if one is missing:
  - the prize leg: RBT-90's ten, about 86 MB and 4 s each;
  - the step leg: RBT-113 O1, 35 MB and 2 s.
- **The jobs are resumable:** each output is promoted only on its `ROW` (prize) or `STEP` rows (steps), as
  `run_gate.sh`'s `promote` does.
- **Outputs are saved durably** (S-3).
  - After each promoted job, the runner snapshots that cell's output directory to its own checkpoint branch
    (`ckpt/rbt-129-stage0-pays-<id>-prize` or `-steps`).
  - At the top of a runner, missing cell directories are restored from those branches. A reclaimed container therefore
    redoes nothing it had promoted.
  - Cells, not jobs, are split over runners (`split_by_cell`), so each cell directory and its branch belong to one
    runner only.
- **Fire them** (S-2, S-4):
  - **Check out the legs' launch commit.** Each runner's session checks out the commit that carries
    `lanes/pays-*/`, which the PR comment names. Never check out integration's head; `verify` would refuse it with
    exit 5 as soon as a pinned tree moves.
  - **Start each runner as a harness background task** (the Bash tool's `run_in_background`), one per 4-core session:
    `bash runs/RBT-129/lanes/pays-prize/runnerK.sh` and `bash runs/RBT-129/lanes/pays-steps/runnerK.sh`, for K = 0, 1, 2.
  - **Never** use `nohup`, a trailing `&` or `setsid`.
  - **Never `pkill` a runner by name:** kill its children by pid. A by-name kill this morning orphaned ecology
    children, which then wrote into the restarted lanes' run directories.
  - Each script's header says the same.
  - To fit the session ceiling, re-emit with another `--runners`. P/0 hold 10 sessions until about 10:00–11:30.
- **Hours:** RBT-125's gate ran each `prize_gate.py` host × cell in about 4 minutes on 4 procs, under the committed
  eating rule without `--fair`. `--fair`'s settle-until-rest adds up to 10 s of settle per bout. So the estimate is
  4–6 min a job, 48–72 core-h.
- **The step leg:** 15 hosts × 9 arms × 128 seeds, about 17,500 seasons a cell. A fixture season timed here under the
  fair PW block took 0.36 core-s, so a cell is about 1.75 core-h (26 min on 4 procs), and **about 31 core-h** for 18.
- **Together, the designed legs are about 80–105 core-h, over the r4 PAYS line** (45 core-h for all 18 cells, every
  leg, holistic included). This is flagged here and not trimmed: hosts and seeds are RBT-125's registered harness.
  Trimming would be the coordinator's call, e.g. fewer prize hosts, or fewer §B seeds (`--seeds`).
- **The prelaunch prints** were re-run on this tree. `lanes/prelaunch_prints.txt` is byte-identical to #451's.

### Parity with RBT-125's registered harness (L-2)

| | RBT-125 `run_gate.sh` (registered) | this leg |
|---|---|---|
| prize hosts | RBT-90's ten (`forage-SEED`) | the same, from `ckpt/rbt-90-SEED` |
| prize command | `prize_gate.py --run … --config-from worlds/<cell> --label … --w 3 --procs 4` | the same, with `--config-from worlds/config/<id>` |
| decoy | `--decoy 3` at the PW cells (PW-G2.5, PW-G10, PW-G0); none at U or HP | **`--decoy 3` at the six PW cells**; none at U or HP |
| prize seeds | the harness's own (64 from 7000) | the same (not overridden) |
| step harness | `steps.py HOSTS_ROOT <cell>`, RBT-113 O1's 15 hosts, 128 seeds from 125000 | the same, with `--config worlds/config/<id>` |
| world | RBT-90's world with the cell's food block, the committed eating rule, no `--fair` | the sweep's block: `--fair`, root + surface, the cell's clutter and smell |

The world row is the only difference, and it is the one DESIGN §5.1 asks for ("under the sweep's own block").

## What blocks the probe and holistic legs (each needs a ruling or code this PR must not invent)

**For RBT-132's probe emit** (fix1b's adversary note): `probe_jobs` targets each pilot unit's `S` at seasons 0 and
300. **A unit with `EXTINCT.txt` has no season-300 S and must be skipped** (and reported as extinct pre-merge, per
DESIGN M2), never probed.

- **B1. `steer.py` refuses RBT-129's G points.**
  - `run_season` calls `assert_registered_channel`, which raises unless `smell_tau == 1.0` (RBT-116 Amendment 1,
    revised, and STEER_NOTES N22).
  - RBT-129 runs τ = 2 s (the 02:10 ruling; RBT-116's own amendment says so).
  - So `steer.py` cannot run at 2 of the 4 pilot points (`c1-p030-PW-G`, `c2-p030-PW-G`) or at 9 of the 18 PAYS
    cells.
  - The CLI also refuses every RBT-129 point through `assert_world_point` (`REGISTERED_POINTS` holds only W1). The
    Python API skips that check but not the τ guard.
  - **Needs:** RBT-116 to register RBT-129's points in `REGISTERED_POINTS`, with τ = 2 s, and to check τ per point.
    This is a change to RBT-116's instrument: its designer, then an adversary.
- **B2. No draw pools or batteries for RBT-129's points.**
  - §5.3(c) probes on "that point's admissible pool (RBT-116 r5's 64-draw pool and reachability screen)".
  - `draw_pool` needs a `POOL_KEY` row per point, and only W1 has one.
  - `screen_draws` needs the G8(a) and G8(c) positive-control hosts, which `gate.py` supplies. **`gate.py` is not in
    the tree** (STEER_NOTES: "Not in this PR").
  - **Needs:** pre-data `POOL_KEY` rows for the 4 pilot points and the 18 PAYS cells, and RBT-116's `gate.py` planters.
- **B3. The planted set and a holistic nose step do not exist as code.**
  - G8(a)–(e) and the motors-off body are `gate.py`'s planters, which are not in the tree.
  - `probes --planted-cmd` has no command to point at.
  - The holistic PAYS leg's G8(c) plant is the same planter.
  - `steps.py` refuses non-designed hosts (S13), so the **holistic** nose step needs a holistic step harness, or a
    ruling that holistic PAYS is G8(c)'s F alone. The designed nose step is not blocked; it is `pays-steps`.
- **B4. The probe members.**
  - They are Stage P's S-arm members at seasons 0 and 300.
  - Season 300 exists only when Stage P reports DONE.
  - Season 0 is in the same directories, which no-peek forbids reading while P runs.

**`stages.py probes` and `pays` stay guarded.** They refuse without `steer.py` at a pinned blob, both command
templates, and (for `pays`) the §B harness at its pinned blob. Their scripts now carry the same launch record and
`verify` header as the prize leg. Once B1–B3 land, emitting them is one command each, as READINESS §3 shows.
