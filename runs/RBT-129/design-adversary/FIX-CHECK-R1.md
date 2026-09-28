# RBT-129 R1 final check: PR #435 at `d9a16c2`, on integration `01f113d` (#446 merged)

**Verdict: MERGE.** R1 is closed. The full suite passes (§5). Two optional follow-ups are listed as SHOULD, and neither
blocks Stage P or Stage 0.

Setup:
- **Trial merge:** integration `01f113d` is an ancestor of `d9a16c2`, so the trial merge is a fast-forward to
  `d9a16c2`.
- **Probes:** `probe_r1_guard.txt` (the probe script is inlined in its header), `probe_r1_reach.py` → `.txt`, and
  `suite_r1.txt`.
- **What ran:** config builds, `stages.surface_clearance_ok()` (single solo bodies, no season), and prints' fixtures.
  No sweep arm or cell.

## (1) `check_eat` accepts exactly the ruled rule, which is also the default and the firing lines. Closed

- `check_eat` accepts only `--eat-from root --eat-rule surface`.
- It refuses, with exit 4, `--eat-from root` alone and `… --clear-from geoms`.
- `blocks.EAT_RULED = ("--eat-from", "root", "--eat-rule", "surface")` is the default of `world_argv`, `block`,
  `export` and `blocks.py --eat`.
- READINESS's firing lines use that default ("`--eat` defaults to the ruled root + surface"). Gate 4c reads MET, and
  gate 4d (#446) reads MET.

## (2) The capability guard refuses a tree without #446. Closed, verified both ways

`stages.surface_clearance_ok()` places a 1.39 m bar root in a root + surface food world, 8 draws × 128 items. It
requires every item to clear the root's surface by `eat_radius`, and its centre by `clearance`, with no fallback.
`check_surface_clearance` calls it for every surface launch, in five places:
- `emit`;
- `run-lane` (`check_lane_blocks`);
- `prelaunch`;
- `pays-prize`;
- `probes` and `pays`.

| tree | `surface_clearance_ok()` | root + surface launch |
|---|---|---|
| `d9a16c2`, with #446 | True (0.2 s) | accepted |
| **a scratch copy of `d9a16c2` with `rabbitstew/simulation.py` reverted to pre-#446 (`8e54b41`)** | **False** | **refused, exit 4** |

It probes behaviour, not code, so it would also catch a later regression.

**S1 (minor):** a draw with `food_fallbacks > 0` is skipped (`continue`). A tree on which every draw falls back would
read True vacuously. Require at least one evaluated draw.

## (3) `prints.txt` under the ruled rule: a reach-limited share of 0 and zero fallbacks. Credible

**`prints.txt`'s own argument is per obstacle.** Footprints are at most 0.7 m across, so no item lies deeper than
0.35 m (the surface eat radius) inside any one footprint. That argument is right, but incomplete: obstacles overlap,
and the union of two footprints can be deeper than either.

**The union check.** `probe_r1_reach.txt` asks the harder question on prints' own arenas (seeds 0–99, 100 arenas a
row, G blocks): for each item inside a footprint taller than 0.1 m, is there a point within 0.35 m (16 directions × 7
radii) outside every tall footprint? The answer: **0 items of 7,200** are deeper than 0.35 m from free ground, in U, HP
and PW at c = 1 and c = 2. The tall-footprint shares are 0.036–0.106.

The one idealisation left is height. It assumes the root's surface reaches the ground by the obstacle. A Pioneer
chassis riding above the ground adds a vertical term to the 3-D surface distance. The share is therefore 0 to within
that clearance, not exactly 0.
- **S2:** say "0 by geometry, assuming the root's surface reaches the ground at the obstacle's edge".
- The claim does not affect any verdict: the old centre-rule bound was already 0.2–0.9%.

**`food_fallbacks` = 0 is credible.**
- **The guard is not tight here.** #446's minimal guard adds only "no item within `eat_radius` of an eating geom's
  surface" to the 0.8 m root-centre clearance. For a compact root, 12 items in a 3 m disc (or 2 patches in a 4 m disc)
  almost never exhaust 256 draws.
- **The probe agrees:** 0 fallbacks over the same 600 arenas.
- **Where it could bite:** fallbacks become possible only with long roots, or with a PW patch lying under a spawn.
  That is why the ecology now counts them.

## (4) The `.sh` scripts re-verify their tools' blob hashes where they run. Closed

`write_script` heads every emitted script with `[ "$(git hash-object TOOL)" = "SHA" ] || { …; exit 6; }` per pin,
before any job (`set -e`). The pins:

| script | pins |
|---|---|
| `probes.sh` | `steer.py` |
| `pays.sh` | `steer.py`, §B's `steps.py` |
| `pays-prize.sh` | `prize_gate.py`, `runs/RBT-103/routed_populations.py` |

**S3 (minor): pin the whole import chain.** `routed_populations.py` loads RBT-97's `routed_p801.py` and
`g500_direction.py`, and adds `scripts/` to its path. `steps.py` imports `prize_gate.py`, which loads
`routed_populations.py`. Neither script pins RBT-97's two files, and `pays.sh` pins neither `prize_gate.py` nor
`routed_populations.py`. Pin the whole chain in both scripts. `scripts/` is pinned only by `run-lane`'s tree check.

The script paths are absolute, from the emitting host. That is fine as long as every session uses the same checkout
path, as cloud sessions do.

## (5) The full suite passes in a clean venv, on the trial merge with current integration

The venv is fresh (`python -m venv`; `pip install -e ".[dev]"`; scipy absent). The result is in `suite_r1.txt`:

**659 passed, 1 skipped, 16 warnings in 12 min 25 s.**
- **The skip** is `tests/test_rbt125_harness.py:170`, the harness's scipy cross-check, which is expected without
  scipy.
- **The count** is up from the #447 check's 649 passed. The ten new tests include #446's surface-clearance tests and
  R1's two capability-probe tests.

## The list

**MUST:** none.

**SHOULD (optional, not blocking):**
- **S1:** `surface_clearance_ok` requires at least one draw without fallbacks.
- **S2:** word the reach-limited 0 as conditional on the root reaching the ground.
- **S3:** pin the whole import chain in `pays.sh` and `pays-prize.sh`: `prize_gate.py` and `routed_populations.py`
  (in `pays.sh`), plus RBT-97's `routed_p801.py` and `g500_direction.py` (in both).

**R1 is closed.** #435 can merge, and Stage P and Stage 0 can fire.

---
_Generated by [Claude Code](https://claude.ai/code)_
