# RBT-129 M/N crash: diagnosis of `1/c2-p030-U-G/129001/M` (RULING.md item 7, "Mechanism")

- **Session:** the crash-only diagnosis session (`session_01GAr8Z2P2WFgeKSprmcGqai`), started after the Stage-1 readout
  was ruled (#517, #519). Coordinator: `session_017eUHGNdTSsoVFAtLaJWehF`.
- **Scope (RULING item 7):**
  - This file reports the mechanism only. It gives no season, fauna, member, group composition or population figure.
  - Any fix applies to **later registrations only**. Nothing here changes a Stage-1 record, the readout or a registered
    plan. The RBT-129 pin stays at 3.14.0, and nothing is wired into `runs/RBT-129/launch`.
- **Result in one line:** a **MuJoCo 3.14.0 bug**. EPA's horizon arrays are a fixed 24 ints, and `addEdge` writes into
  them with no bounds check. A deep self-penetration of two sibling parts of one robot (a box and a cylinder) produced
  a 25-edge horizon. The overflow corrupts memory, and the process faults at whatever reads the corrupted pointer next
  (`projectOriginPlane`+5 on host1; `mj_narrowphase` in the standalone replay here). No NaN, no Inf, no exploded state.

## Provenance (hard rule 3)

| item | value |
|---|---|
| host | Linux-6.18.44-fc-v64-x86_64-with-glibc2.39, Ubuntu 24.04.4, Intel Xeon @ 2.10GHz (same model as host1's `platform.json`), 4 cores |
| python | CPython 3.11.15 |
| venv (`pip freeze`) | absl-py 2.5.0, etils 1.14.0, fsspec 2026.9.0, glfw 2.10.2, **mujoco 3.14.0**, numpy 2.4.6, PyOpenGL 3.1.10, typing_extensions 4.16.0, websockets 17.1, zipp 4.1.0 |
| check | every script asserts `mujoco.__version__ == "3.14.0"` before running |
| pip libmujoco | `libmujoco.so.3.14.0` sha256 `5e7623e3…441000b` |
| source build | tag 3.14.0 (`9ecbb9d7`), clang, Release, plus `diag/mujoco-3.14.0-epa-horizon.patch`; sha256 `37883e94…7020433`. **Byte-identical to the pip wheel on this workload** (identity test below). |
| tree | `rabbitstew/` at HEAD is the pinned tree `144b3b6`, so the code that ran is the code that crashed |
| sources | only `ckpt/rbt-129-stage1-<point>-<seed>-ckpt60` branches. **The quarantined `ckpt/rbt-129-stage1-c2-p030-U-G-129001-M` was never fetched, listed or read.** |

## (a) Deterministic reproduction

1. **Fork M from ckpt60, as REPRO-host7 did.**
   - `fork_config`'s settings (`merge_after` 60, `pooled_capacity` 120).
   - `--resume --seasons 300`, `WORKERS=1`, `NO_DURABLE=1`, `PYTHONFAULTHANDLER=1`, in a scratch directory outside
     `runs/`. No save and no branch.
   - The run went past 2 h on this host: a 7000 s timeout, then one resume of the same scratch directory. The host was
     shared with the build and the survey below at the time. The ruling's 2 h stop is for the item-7 second-host check;
     this is the diagnosis that item 7 allows afterwards. Wall time is not reported.
   - **It exited 139 (SIGSEGV),** with the faulthandler stack `simulation.py:472 step` ← `:518 run` ← `:1008 run_group`
     ← `evolution.py:167/197` ← `ecology.py:513 _challenge` ← `:734 step` ← `:893 run`. That is host1's WORKERS=1
     stack. **So this is a third host, and a third reproduction.**
2. **Bisect.** The run directory as it stood before the faulting season (its last `state.json`) is resumed under
   `diag/trace.py count`. That script counts every `mj_step` (shimmed into `rabbitstew.simulation`) and every
   `Simulation`.
   - Twice, the counter at the fault read **[simulation 13 of that season's challenge, `mj_step` 2246 of that
     simulation, 60046 in total]**. The resume faults at the same step every time (cf. the ruling's "each resume
     crashed within about 20 s").
3. **Dump.** `trace.py dump` saves `model.mjb` and `mj_getState(mjSTATE_INTEGRATION)` before steps 2238–2246.
4. **Standalone.**
   - `diag/replay.py DUMP 2246 step` loads the model and the state, and **one `mj_step` segfaults**.
   - `state_2245` steps cleanly.
   - So the fault is a pure function of (model, physics state), with no ecology and no history.
5. **The state is sane.**
   - qpos, qvel, xpos, xmat, geom_xpos and geom_xmat are all finite.
   - max |qpos| = 1.95, max |qvel| = 55.8, max |geom_xpos| = 2.55.
   - **Not NaN/Inf**, not a zero-size geom, and no exploded robot. (The adversary's NOTE 6 first hypothesis, "keeps
     stepping an exploded robot", is **not** the mechanism.)

The dump files stay in scratch, uncommitted. They encode one group's bodies, and RULING item 7 forbids reporting a
member or a group composition. `diag/repro.sh` regenerates them from ckpt60. It condenses the commands run here and
has not been re-run end to end as one script.

### The contact pair

- **Geom A: box**, half-sizes (0.160, 0.124, 0.040).
- **Geom B: cylinder**, radius 0.108, half-length 0.095.
- Both have margin 0 and gap 0, `ccd_iterations` 35 and `ccd_tolerance` 1e-6 (MuJoCo defaults; the XML sets neither),
  with nativeccd on.
- **Both belong to one robot.** They are two sibling parts, children of the same free-jointed root body: the box on a
  ball joint (cone 1.571 rad), the cylinder on a hinge (range ±1.497 rad). MuJoCo's parent filter excludes parent–child
  pairs only, so siblings collide, and the model has no `<exclude>` for them.
- **It is self-collision, not inter-fauna contact** (cf. ADVERSARY.md's informative-missingness guess).
- **They are deeply interpenetrated** (`mj_geomDistance`):

  | step | 2238 | 2240 | 2242 | 2244 | 2245 | **2246** |
  |---|---|---|---|---|---|---|
  | signed distance (m) | −0.080 | −0.081 | −0.083 | −0.085 | −0.086 | **−0.100** |

  The overlap is about 0.1 m, against part sizes of 0.1–0.16 m. It is sustained and deepening, not a one-step glitch.
  The step into 2246 has a qvel spike (55.8). The poses at 2246 are in `replay.py … info 30 32` (scratch); they are
  ordinary positions inside the arena.

## (b) Root cause

- **Where.** `src/engine/engine_collision_gjk.c` (3.14.0, identical on `main` today), in EPA, reached from `mjc_ccd`
  for the box–cylinder pair: `mjc_ccd` → `gjk` → `polytope4` → `epa` → `horizon`/`horizonRec` → `addEdge`.
- **The polytope buffer.** `mjc_ccd` carves it from `config->buffer` as verts `5+N`, faces `6N`, map `6N`, and
  **horizon indices `int[24]`, horizon edges `int[24]`** (`mjc_ccdSize`, lines 2381–2386 on main), with N =
  `ccd_iterations` = 35.
- **No bounds check.** `addEdge` does `edges[nedges] = …; indices[nedges++] = …`. `epa` checks `nedges > maxFaces(pt)`,
  but **never `nedges > 24`**.
- **The bound is larger than the cap.**
  - At EPA iteration k the polytope has `init + k + 1` vertices (init ≤ 5).
  - On a convex polytope the horizon is a simple cycle that avoids the new vertex, so `nedges ≤ init + k ≤ 4 + N`.
  - That is up to 39 at N = 35: **the 24-entry arrays are too small by design whenever N > 20.**
- **What happened here** (instrumented build, guard off, same state):
  `RBT_HZN overflow: nedges 25 (cap 24), EPA iteration 32, nverts 37, nfaces 133, geom box/cylinder`.
  - The 25th `indices[]` write lands on `edges[0]`, and the 25th `edges[]` write lands past the arrays in the shared
    buffer.
  - Attaching faces then reads a corrupted `hznEdge`, so `hznVerts[hznEdge]` is an out-of-bounds stack read, and
    `pt->verts[garbage]` is passed to `attachFace` → `projectOriginPlane(face->v, pt->verts[v3].vert, …)`.
- **host1's fault** is `projectOriginPlane`+5 = `vmovsd 0x10(%rsi)`: a read of `v1[2]` where `rsi` = `pt->verts[v3]`
  is that garbage pointer (the instruction disassembled from the pip `.so`, offset 0x1aeb65). It matches exactly.
- **The fault site is not stable.**
  - In the standalone replay (a different process layout), the corrupted data is read first in `mj_narrowphase`+5281:
    `mov (%rdx)` with `rdx = 0x7fff00000001`. That is a heap pointer whose low 32 bits were overwritten with the int 1,
    which is the mark of a small-int (horizon) write.
  - **Same overflow, different victim.**
  - So the instruction-equality test in RULING item 5 can fail for this one bug. Two crashes from one overflow can
    fault at different instructions.
- **Why this pair.**
  - The cylinder is a smooth (non-discrete) geom. EPA then uses `ccd_tolerance` 1e-6 rather than finite convergence,
    so it keeps adding support points up to the iteration cap.
  - A deep overlap gives a large polytope. Here a support point at iteration 32 saw a region bounded by 25 edges.
- **Proof that the overflow is the cause.** The instrumented build with `RBT_HZN_GUARD=1`, which stops EPA at the
  current best face when the horizon exceeds 24, steps the same state **without fault**. Over that one `mj_step` it
  logged 91 EPA iterations, and exactly one had a horizon over 24.
- **Upstream.**
  - Not fixed. PyPI's newest is 3.14.0. On `main`, `engine_collision_gjk.c` differs from 3.14.0 only in capsule
    multicontact and `alignedFaces`; the horizon code and `int[24]` are unchanged. The changelog has no EPA-horizon
    entry.
  - **It is a regression:**
    - 3.3.0: horizon stack-allocated `6 + max_iterations`.
    - 3.6.0 and 3.7.0: `static int index_data[6 + mjMAX_EPA_ITERATIONS]`.
    - From 3.8.0: carved from the shared buffer at a fixed 24.
  - The GitHub API for google-deepmind/mujoco is not reachable from this session, so I did not search issues there. An
    upstream report (state + model reproduce in one `mj_step`) is for the owner to file.
- **"Test on a newer MuJoCo."** None exists. Older versions without the cap (≤ 3.7.0) were not run on this state: an
  `.mjb` from 3.14.0 does not load in older versions, and their physics differs broadly anyway. So only code reading
  covers them.

## (c) Remedies for later registrations, ranked

On this exact state (pip 3.14.0, one `mj_step`):

| change | result |
|---|---|
| `ccd_iterations` 10, 20 or 30 | no fault |
| `ccd_iterations` 34, 36, 50 or 100 | **SIGSEGV** |
| `ccd_tolerance` 1e-5, 1e-4 or 1e-3 | no fault |
| `nativeccd` disabled | no fault |
| `geom_margin` 0.001 on all geoms | no fault (46 contacts, not 34) |
| patched 3.14.0, guard on | no fault |

| rank | remedy | crash risk afterwards | determinism | trajectories that never crash | comparability with RBT-129 |
|---|---|---|---|---|---|
| **1** | **Patched 3.14.0 with a horizon bounds check** (`diag/mujoco-3.14.0-epa-horizon.patch` with the guard made unconditional, or better, upstream sizing the arrays `4 + N` (`5 + N` is safe)). Ship it as a pinned wheel or `.so` with its sha256 in `platform.json`. | eliminated for this bug | deterministic | **unchanged, byte for byte**: the guard acts only when `nedges > 24`, which the stock code turns into memory corruption. Shown: pip vs patched, guard off vs on, identical in all 557 files of a full merged season (`diag/identity.sh`) | **full**, except on a trajectory that would have overflowed, which then continues with a slightly truncated EPA contact instead of UB |
| 2 | `ccd_iterations` ≤ 20 (the convexity bound makes `4+N ≤ 24`), or a coarser `ccd_tolerance` (1e-5) | removed (iterations ≤ 20, up to numerical non-convexity), or reduced (tolerance) | deterministic | **changed**: every EPA result on smooth geoms that ran more than N iterations, or converged under the old tolerance, differs, so trajectories diverge early | new physics: not comparable step by step; only at the level of the ecology's statistics |
| 3 | Exclude sibling self-collision (`<contact><exclude>` per sibling pair, or per-robot contype bits) | removes this trigger (deep sibling overlap); not the bug: inter-robot deep overlaps can still overflow | deterministic | **changed** for every body with sibling contact (a morphology-dependent physics change) | new physics, and it changes what bodies can do, which is a design question |
| 4 | `nativeccd` off (libccd) | this bug avoided (different code) | deterministic | **changed everywhere** (a different collider) | not comparable |
| 5 | MuJoCo ≤ 3.7.0 (no cap) | this bug absent by code reading | deterministic | **changed everywhere** (seven versions of solver and collision changes) | not comparable |
| — | A Python-side guard (NaN check, then skip or abort) | **does nothing**: the state is finite, and the fault is inside one `mj_step` | — | — | — |
| — | A version bump | none available (3.14.0 is newest; `main` has the bug) | — | — | — |

- **Recommendation:** remedy 1, plus filing upstream.
- For any future registration that keeps stock 3.14.0, make the **CRASHED rule's instruction-equality test** read
  "inside libmujoco, in the convex collider (`mjc_ccd` / `mj_narrowphase` frames)", not "the same instruction". This
  bug can fault at different instructions from one overflow (above).
- Not for RBT-129: item 2 of the ruling stands, and the RBT-129 pin stays at stock 3.14.0.

## (d) Do other Stage-1 units come close?

- **Instrumentation.** The patched build, guard **off** (stock logic, byte-identical physics as shown), records only a
  histogram of horizon sizes per EPA iteration. It does not read outcomes.
  - `diag/nearmiss.sh` forks each other Stage-1 M unit (30 units, from their ckpt60) and runs its **first 3 merged
    seasons**, `NO_DURABLE=1`, in a scratch directory deleted unread.
  - Only the histogram line and the exit code are kept: `diag/nearmiss-M-3seasons.txt`.
- **Result** (`diag/tail.py`): **4.94e8 EPA iterations, zero overflows**, and every unit exited 0.
  - Per-unit maximum horizon ranges over 10–16; the overall maximum is **16**, against an overflow at 25.
  - Pooled counts by horizon size: 13: 88, 14: 33, 15: 7, 16: 1.
  - A log-linear tail fit (n = 8–15) falls by a factor of 0.17 per edge. Extrapolated to 25, it gives about 1e-7
    expected overflows in all these iterations.
- **So the crash is not the far tail of ordinary contacts.** It needs a specific state: a sustained deep overlap of a
  smooth geom, here two sibling parts of one body. The tail flattening above 13 suggests that such a sub-population of
  deep contacts exists. The crashed unit (next item) shows it strongly.
- **Caveat on scope.** The survey covers the first 3 merged seasons per unit. The crashed unit's near misses came late
  in its run. So a unit that is clean at 3 seasons can still approach the cap later.
- **The crashed unit itself**, from ckpt60 under the guard (`RBT_HZN_GUARD=1`), up to and including the faulting
  season, then stopped.
  - It ran in two parts: the first hit this session's 2 h background-task limit and was resumed from its own scratch
    state. Overflow lines from both parts' stderr were counted. The run directory was deleted unread, and its guarded
    continuation past the fault is never a stand-in (RULING item 2).
  - **Exactly one overflow in the whole run, and it is the fatal event:** `nedges 25, EPA iteration 32, nverts 37,
    nfaces 133, cylinder/box`, the same numbers as the standalone dump. There was no earlier overflow, so **the stock
    trajectory was not silently corrupted before it crashed.**
  - **But this unit's tail is far heavier than any other unit's.** The second part, which ends with the faulting season,
    has horizons of 13: 476 (more than 12's 335, so the tail is not monotone), 14: 167, 15: 130, 16: 68, 17: 70, 18: 23,
    19: 44, 20: 10, 21: 2, 22: 3, 23: 2, 25: 1. That is **154 EPA iterations at 17–23**, against a maximum of 16 across
    all 30 other units. The length of the second part is not reported (RULING item 7).
  - **So the bad state built up over time**, near misses at 20–23 before the 25. The likely driver is sustained deep
    sibling overlap in particular bodies, not a one-off spike.
- **A caveat for the integrity question NOTE 6 raises.** A stock overflow need not crash: it can corrupt memory and
  continue silently. The survey above finds no overflow, so in those 90 unit-seasons no M trajectory was touched. It
  covers 3 of 240 seasons per unit, so it is a sample, not a proof. A full-length guard-off census of every Stage-1
  unit would settle it, at about the cost of re-running Stage 1. That is for a later registration's integrity check,
  not for this readout.

## Files

- `diag/trace.py`: in-process `mj_step` counter and pre-fault state dumper.
- `diag/replay.py`: standalone replay, geom info, and option experiments.
- `diag/repro.sh`: the full chain from ckpt60.
- `diag/mujoco-3.14.0-epa-horizon.patch`: instrumentation and an opt-in guard (`RBT_HZN_STATS`, `RBT_HZN_GUARD`).
- `diag/identity.sh`: pip vs patched, byte identity.
- `diag/nearmiss.sh`, `diag/tail.py`, `diag/nearmiss-M-3seasons.txt`: the near-miss survey.
- **Not committed:** the run directories, `model.mjb` and the states (member data). All scratch run directories,
  snapshots, logs and the dump were deleted at the end of the session. No ecology outcome line (alive, births, deaths,
  scores) was displayed in this session: logs were only grepped for the faulthandler block, the MuJoCo warning prefix,
  or the `RBT_HZN` lines.
- **Disclosure.**
  - One early progress check displayed the scratch fork's `state.json` season counter while it was still a few seasons
    past the merge. That is far from the fault, and it is not reported.
  - The faulting season was read into a file to bound the guard run, and was never displayed.
  - Two QACC warning lines were displayed in full; they carry only a DOF index and an in-bout simulation time.
- **One unplanned observation.** The crashed unit's stock run log carried 140 `WARNING: Nan, Inf or huge value in
  QACC` lines (MuJoCo's auto-reset) before the fault. Only the prefix was counted. These are unrelated to the fault:
  the faulting state is finite, and MuJoCo's reset never yields a NaN state. The volume is an integrity note for later
  registrations (`mjWARN_BADQACC` resets are silent physics discontinuities).
- `MUJOCO_LOG.TXT`, which MuJoCo writes into the cwd on every warning, was moved out of the repo root.

---
_Generated by [Claude Code](https://claude.ai/code)_
