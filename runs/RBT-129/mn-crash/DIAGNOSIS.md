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
  Upstream: google-deepmind/mujoco#3646, with fix PR #3650 (see (b)).

## r2: the fix round for the adversary review (PR #521, ACCEPT WITH CORRECTIONS)

| item | what changed in r2 |
|---|---|
| MAJOR 1: tail framing | (d) rewritten. "Max 16", "not the far tail" and the ~1e-7 extrapolation are **retracted**. The adversary's S result (a horizon of 23) and their broader scan are cited. S, N, census and pilot are stated as not surveyed by this PR. |
| MAJOR 2: "no silent corruption" | (d) now says what the scans do and do not rule out. The only "no earlier overflow" claim kept is for the crashed unit's own trajectory, which a guard-run of that exact trajectory supports. |
| MAJOR 3: forward risk | new section (e). It cites the adversary's estimate of about 55–75% and lists options (a)–(c) without choosing among them. |
| MAJOR 4: re-rank | (c) re-ranked: face-budget (6N) sizing first. Its byte identity off-event and its deltas against the guard were measured here. |
| MINOR 5: upstream | (b) cites #3646 and #3650 and compares their fix with this PR's guard and with 6N. |
| MINOR 6: build recipe | new section "Builds": `diag/build.sh`, every sha, and why shas differ across hosts (paths through ThinLTO symbol names). |
| MINOR 7: raw records | `diag/records/`: round-1 lines transcribed verbatim, round-2 runs written directly. |
| NOTE: marker-only ckpt60 | section "Marker-only ckpt60 branches": all three are extinct-pre-merge snapshots. |

## Provenance (hard rule 3)

| item | value |
|---|---|
| host | Linux-6.18.44-fc-v64-x86_64-with-glibc2.39, Ubuntu 24.04.4, Intel Xeon @ 2.10GHz (same model as host1's `platform.json`), 4 cores |
| python | CPython 3.11.15 |
| venv (`pip freeze`) | absl-py 2.5.0, etils 1.14.0, fsspec 2026.9.0, glfw 2.10.2, **mujoco 3.14.0**, numpy 2.4.6, PyOpenGL 3.1.10, typing_extensions 4.16.0, websockets 17.1, zipp 4.1.0 |
| check | every script asserts `mujoco.__version__ == "3.14.0"` before running |
| pip libmujoco | `libmujoco.so.3.14.0` sha256 `5e7623e3…441000b` |
| source builds | tag 3.14.0 (`9ecbb9d7`) plus a patch, built by `diag/build.sh`. Recipe and shas are in "Builds" below. Round 1's ad-hoc instrumented build had sha256 `37883e94…7020433` (no prefix map, a different directory). |
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
  - The regression commit is `d9b3faf8` ("Remove thread_local EPA data in favor of using mjData stack"), first tagged
    in 3.8.0. That is the adversary's finding, consistent with the versions above.
  - **Reported upstream (r2, MINOR 5):**
    - **google-deepmind/mujoco#3646** reports a cylinder vs convex-mesh contact, a 25-edge horizon, SIGSEGV in
      `projectOriginPlane`, and the same `int[24]`/`addEdge` diagnosis. Its open status and text are from the adversary;
      this session has git access only. It is confirmed here by PR #3650's regression test, which reads "regression
      for #3646: this cylinder/convex hull pair produces a 25-edge horizon, exceeding the former 24-edge limit".
    - **Fix PR #3650** (head `f394095`, 2026-10-03, third party, unmerged) was fetched as `refs/pull/3650/head`. Its
      source change is in `diag/mujoco-upstream-pr3650-f394095.patch` and applies cleanly to 3.14.0. It does three
      things:
      1. it sizes both horizon arrays to the face budget, `6 * iterations`, in `mjc_ccdSize` and in the `mjc_ccd` carve;
      2. `addEdge` stops writing once `nedges > maxFaces(pt)`. That keeps one excess edge as a signal, and the index
         stays below `6N`, because `maxFaces = 6N − nfaces` and `nfaces ≥ 4`;
      3. it moves the existing "out of memory for faces" check (`mju_warning` and `break`) ahead of the `nedges < 3`
         check, so a truncated horizon is read as a capacity limit rather than as a numerical failure.
  - **Comparison of the three fixes:**

    | fix | `nedges ≤ 24` (every trajectory to date except the crash) | `24 < nedges ≤ maxFaces` (this event) | `nedges > maxFaces` |
    |---|---|---|---|
    | this PR's guard | stock | **truncates**: EPA stops at the pre-iteration face | n/a (stops at 24) |
    | 6N sizing (adversary's diff, `diag/mujoco-3.14.0-epa-horizon-6N.patch`) | stock | **converged**: EPA proceeds as if the arrays had always fit | stock's out-of-memory break. Safe only if `nedges ≤ 6N`, which is the adversary's bound (horizon faces are distinct faces). With no bound in `addEdge` this is not enforced, so #3650's extra bound is the stricter fix |
    | #3650 | stock | **converged**, identical to 6N | out-of-memory warning and break, before any write past capacity |

  - 6N and #3650 agree wherever `nedges ≤ maxFaces`, so they agree here. They differ only in the order of
    pathological checks. **#3650 (or whatever upstream merges) is the one to track.**
- **"Test on a newer MuJoCo."** None exists. Older versions without the cap (≤ 3.7.0) were not run on this state. I did
  not try loading the 3.14.0 `.mjb` in them, and their physics differs broadly anyway. So only code reading covers
  them.

## (c) Remedies for later registrations, ranked (r2: re-ranked, MAJOR 4)

### Option sweep on the faulting state

On this exact state (pip 3.14.0, one `mj_step`):

| change | result |
|---|---|
| `ccd_iterations` 10, 20 or 30 (adversary: 21 too) | no fault |
| `ccd_iterations` 33 (adversary), 34, 36, 50 or 100 | **SIGSEGV** |
| `ccd_tolerance` 1e-5, 1e-4 or 1e-3 | no fault |
| `nativeccd` disabled | no fault |
| `geom_margin` 0.001 on all geoms | no fault (46 contacts, not 34) |
| patched builds (guard, 6N, #3650) | no fault |

### What each patched build does at the event

`diag/compare_fix.py`, one `mj_step` from `state_2246`; the dump was regenerated by `repro.sh` in r2.

DELTA_TABLE

- **The guard is not a "slight truncation".** It stops EPA at the pre-iteration face, and that changes the contact
  materially from a converged EPA (the 6N and #3650 builds). r1's wording is withdrawn.
- 6N and #3650 give the same result at this event, as expected (they agree whenever `nedges ≤ maxFaces`).

### Ranking

| rank | remedy | crash risk afterwards | determinism | trajectories that never overflow | at an overflow event | comparability with RBT-129 |
|---|---|---|---|---|---|---|
| **1** | **Face-budget sizing: upstream #3650, or the 6N diff.** Ship it as a pinned `.so` built by `diag/build.sh`, at a fixed absolute path, with its sha256 in `platform.json`. Track #3650's merged successor. | this bug eliminated: memory-safe, with #3650's bound | deterministic | **unchanged, byte for byte.** pip vs 6N and pip vs #3650: 609/609 files identical, c2-p030-U-G/129005 M, 1 merged season. Plus 6N on c1-p080-U-L/129004 M, 1 season: 737/737. | **converged EPA**: what stock would compute had its arrays fit. | **full**: identical to stock 3.14.0 except at events that are undefined behaviour under stock |
| 2 | The guard (`RBT_HZN_GUARD=1`) | eliminated | deterministic | unchanged, byte for byte (r1: 557/557 on c2-p030-U-G/129003; r2 rebuild `43a23d33…`, guard off and on: 737/737 on c1-p080-U-L/129004) | **truncated EPA**: the contact differs from converged (table above). It logs every event to stderr. | full off-event; a different contact at events |
| 3 | `ccd_iterations` ≤ 20 (`4+N ≤ 24` under convexity), or a coarser `ccd_tolerance` | removed (iterations, up to non-convexity) or reduced (tolerance) | deterministic | **changed**: every smooth-geom EPA that ran more than N iterations, or converged under the old tolerance | — | new physics |
| 4 | Exclude sibling self-collision | removes this trigger only; inter-robot deep overlaps remain | deterministic | **changed** for bodies with sibling contact | — | new physics, and a design question |
| 5 | `nativeccd` off, or MuJoCo ≤ 3.7.0 | this bug avoided | deterministic | **changed everywhere** | — | not comparable |
| — | A Python-side guard (NaN check, skip or abort) | **does nothing**: the state is finite, and the fault is inside `mj_step` | — | — | — | — |
| — | A version bump | none available (3.14.0 is newest; `main` has the bug; #3650 is unmerged) | — | — | — | — |

- **Recommendation:** rank 1, tracking #3650. Keep a guard-off instrumented build (or #3650's warning) as the event
  log, so any overflow is recorded in the run's integrity record.
- For any later registration that keeps stock 3.14.0, the CRASHED rule should read "inside libmujoco, in the convex
  collider" rather than "the same instruction". The adversary's NOTE 9 notes that repeated attempts in one process
  configuration do fault at the same place, so for RBT-129's item 5 this is a NOTE only.
- **Not for RBT-129:** RULING item 2 stands, and the pin stays at stock 3.14.0. Continuations are section (e).

## (d) Do other Stage-1 units come close? (r2: rewritten, MAJORs 1–2)

### This PR's survey: what was measured

- **Instrumentation.** The patched build with the guard **off** (stock logic) records only a histogram of horizon sizes
  per EPA iteration, plus a line for every overflow. It does not read outcomes. Physics is byte-identical to pip on
  every tested trajectory without an overflow (Builds).
- **Coverage.** `diag/nearmiss.sh` covered every other Stage-1 **M** unit, 30 of them, from their ckpt60:
  - only the **first 3 merged seasons** of each;
  - `NO_DURABLE=1`, scratch, deleted unread;
  - output in `diag/nearmiss-M-3seasons.txt`.
- **Result.**
  - 4.94e8 EPA iterations, zero overflows, every unit exited 0.
  - Per-unit maximum horizon 10–16 in those 3 seasons.
- **Not surveyed by this PR:**
  - the other 237 seasons of each M unit;
  - all **N** units, all **S** units after ckpt60, the Stage-0 **census** and the **pilot**.

### Retracted (MAJOR 1)

These r1 claims are **withdrawn**:
- "the overall maximum is 16";
- "the crash is not the far tail of ordinary contacts";
- the log-linear extrapolation, "about 1e-7 expected overflows".

The adversary's scans (PR #521, `probe/`; same instrumented build, guard off; 0 overflows in **528 S + 240 M
unit-seasons**, about 1e10 EPA iterations) falsify them:
- An ordinary S unit, **c2-p080-HP-G/129004 S**, reached a horizon of **23**, one below the overflow, within 30 seasons:
  16: 3, 17: 3, 18: 4, 19: 2, 23: 1. Over seasons 60–179 it had 17: 5, 18: 5, 19: 2, 20: 1, 21: 1, 23: 1.
- Two M units from this PR's list, run for 120 seasons, exceed 16: c2-p030-U-G/129005 reached 18, and
  c1-p010-PW-L/129005 reached 17.
- In 16 random S draws over 3 seasons, the maximum was 19.

So **near misses of 17–23 occur in both the S and M arms of ordinary units within tens of seasons.** Overflow risk is
a property of the physics regime (smooth geoms at `ccd_tolerance` 1e-6 and 35 iterations, under deep overlaps). It is
not peculiar to the crashed unit. The fit's tail is a mixture: the rare deep-overlap states sit far above the
log-linear extrapolation. That extrapolation must not be used for any rate.

### The crashed unit (kept, scoped)

- **The run.** From ckpt60 under the guard (`RBT_HZN_GUARD=1`), through the faulting season. Records are in
  `diag/records/r1-crashunit-guard-run.txt`.
  - It ran in two parts; part 1's histogram was lost when the 2 h task limit killed it before the stats destructor
    ran. Overflow lines from both parts were counted.
  - The directory was deleted unread, and the guarded continuation is never a stand-in (RULING item 2).
- **Exactly one overflow, the fatal one:** `nedges 25, EPA iteration 32, nverts 37, nfaces 133`.
  - The guard build is identical to stock up to its first trigger, so this does show that **this one trajectory** had
    no earlier overflow.
  - That rests on identity holding on this trajectory, which was tested on other units, not on this one.
  - It says nothing about any other unit.
- **The tail of part 2.** Horizons 13: 476, 14: 167, 15: 130, 16: 68, 17: 70, 18: 23, 19: 44, 20: 10, 21: 2, 22: 3,
  23: 2, 25: 1.
  - That is near misses up to 23 before the 25, the same pattern as the adversary's S unit.
  - The r1 phrase "far heavier than any other unit's" is withdrawn: it compared late seasons here with 3 early
    seasons elsewhere.

### Silent corruption: what the scans do and do not rule out (MAJOR 2)

- **It is mechanically possible.**
  - At `nedges` 25, `indices[24]` overwrites `edges[0]` and `edges[24]` writes 4 bytes past the arrays. ASan places
    the write in poisoned `mjData` stack (adversary).
  - The SIGSEGV comes from a later *read*, `hznVerts[corrupted edge]`. When that read lands on mapped memory, the
    result is a wrong face and a wrong contact, with no crash.
- **Ruled out:**
  - an overflow in the 90 M unit-seasons surveyed here;
  - an overflow in the adversary's 528 S + 240 M unit-seasons;
  - an earlier overflow in the crashed unit's own trajectory (above).
- **Not ruled out:** a silent overflow anywhere else in Stage 1. That covers roughly 1e5 unit-seasons: S after ckpt60,
  all of N, the remaining M seasons, the census and the pilot.
- **What would settle it.** A full guard-off census, which re-runs each unit exactly up to its first overflow and logs
  it. The adversary costs it at about 100 core-hours for M and N, and 600–800 for S.
- **Until then**, any integrity statement should say that a known memory-safety bug can corrupt without crashing, and
  that no other unit was checked beyond the coverage above.

## (e) Forward risk on stock 3.14.0: RBT-129 continuations (r2, MAJOR 3)

- **The rate.**
  - One observed overflow in roughly 1.0–1.4e5 unit-seasons to date, plus an unknown number of silent ones.
  - Stage 2a, 2b/R-B and their M/N arms add roughly another 1e5 unit-seasons.
  - The adversary estimates **P(≥ 1 further overflow) ≈ 55%** if the hazard is uniform over arms, and **≈ 75%** if it
    is M-specific. That is a Jeffreys-prior posterior on one event, so the intervals are very wide.
  - This PR adds nothing to that estimate except agreement: the near misses in (d) mean no arm can be assumed safe.
- **Under the current ruling, a recurrence:**
  - in M or N is a second CRASHED unit (RULING item 5). It stops M/N lane issuance and holds the readout plan;
  - in S **stops the hive**;
  - that is silent corrupts a unit undetectably.
- **Options**, listed here and not chosen. Choosing is a ruling for the coordinator and the owner.
  - *(Added after the options were written: the coordinator reports that the owner chose **(c)**, and that
    `session_01Pky3gny7iiA4kBkPUcrDtt` packages it. The build for (c) is the **log-only** variant in Builds:
    `diag/mujoco-3.14.0-epa-horizon-log-only.patch`, sha256 `74e1d8a2…`, built at `/tmp/rbt129-mjbuild/logonly`.
    It contains no guard code at all, unlike `mujoco-3.14.0-epa-horizon.patch`, whose guard an environment variable
    turns on. It prints one `RBT_HZN overflow:` line to stderr per overflowing EPA iteration, flushed before stock code
    reads the overflowed arrays, and an optional histogram at exit via `RBT_HZN_STATS`. A crash replay on it is checked
    in (c) once the dump is regenerated: LOGONLY_REPLAY.)*
  - **(a) Stock 3.14.0 plus pre-registered handling.**
    - S is covered by CRASHED or an explicit stop rule.
    - Any crash gets a mechanism check: a re-run under the guard-off instrumented build must log `RBT_HZN overflow`.
    - The integrity section discloses the unverified silent-overflow exposure.
    - Physics unchanged.
  - **(b) A 6N-sized (or #3650) 3.14.0 build for continuations.**
    - Byte-identical on every tested non-overflowing trajectory, and converged EPA at events that are UB under stock.
    - It needs a pinned recipe (Builds), multi-unit identity checks over many seasons, an adversary pass, and a ruling
      amending RULING items 2 and 6 for continuations only, never to re-run the CRASHED unit.
  - **(c) A guard-off instrumented build for continuations.**
    - Byte-identical to stock, and unchanged physics, UB included.
    - But every overflow is logged, so silent corruption becomes visible and a crash's mechanism is attested.
    - It needs the same build and identity discipline as (b).

## Builds (r2, MINOR 6)

- **Recipe.** `diag/build.sh PATCH WORKDIR PIP_VENV OUT_VENV`:
  - source: tag 3.14.0, `9ecbb9d7b5ee623f54745638d36799ff90e6f7cd`, plus `patch -p1`;
  - toolchain: Ubuntu 24.04, clang 18.1.3 (1ubuntu1), LLD 18.1.3, cmake 3.28.3, ninja 1.11.1;
  - flags: `-DCMAKE_BUILD_TYPE=Release` (`-O3 -DNDEBUG`), MuJoCo's defaults (AVX and AVX intrinsics ON, its LTO), and
    `-ffile-prefix-map=<src>=mujoco-3.14.0`; examples, simulate, tests and USD OFF;
  - target: `mujoco`;
  - packaging: the wheel's venv is copied and its `libmujoco.so.3.14.0` replaced.
- **Produced on this host:**

  | build | patch | WORKDIR | sha256 of `libmujoco.so.3.14.0` | `vfmadd` |
  |---|---|---|---|---|
  | pip wheel | none (clang 20.1.8 + LLD 20.1.8, per its `.comment`) | — | `5e7623e30f55bf324d4c9648379ebeba5bcd153ee0304c52eac74bf8d441000b` | — |
  | source, unpatched | none | `$S/bE` | `28d3cbbe43e146cea289a08e9ba5fb59b37766ead1f5e8e69bccbaa2ee8c835a` | 0 |
  | 6N | `mujoco-3.14.0-epa-horizon-6N.patch` | `$S/bA` | `358e960859c39e34f239a9f7a1f846ba920ae35c6c54d376422fd19978d1429d` | 0 |
  | 6N, rebuilt in the same dir | same | `$S/bA` | `358e9608…` (**identical**) | 0 |
  | 6N, another dir | same | `$S/other/dir/bB` | `c4f8c0c4f48da0e8cdbfab8ba8b9d5decc0446fcafabd7236aa9820ba9a2c774` | 0 |
  | #3650 | `mujoco-upstream-pr3650-f394095.patch` | `$S/bC` | `904908e7c6be430417e27173a0d335f3f6a42a908a96136a5a6635495b584258` | 0 |
  | instrumented / guard | `mujoco-3.14.0-epa-horizon.patch` | `$S/bD` | `43a23d33bac49aeb2575b645e31d3606e8d4a0888c72c2bf031dc5e00e3c8b1d` | 0 |
  | **log-only** (no guard code; for option (c)) | `mujoco-3.14.0-epa-horizon-log-only.patch` | `/tmp/rbt129-mjbuild/logonly` | `74e1d8a29d1303108e7b0f8774e9820de103b5307ad0a8c23f0fdbf77e1525ad` | 0 |
  | log-only, rebuilt in the same dir | same | `/tmp/rbt129-mjbuild/logonly` | `74e1d8a2…` (**identical**) | 0 |
  | r1 ad-hoc instrumented | same, no prefix map | `$S/mjsrc` | `37883e94…7020433` | — |

  `$S` is this session's scratchpad.
- **Why the shas differ (the adversary's mismatch).** The output depends on the build's **absolute paths**.
  - `__FILE__` strings depend on the source path; the prefix map removes them.
  - MuJoCo builds with ThinLTO, which names promoted local symbols `.str.1.llvm.<hash>` from each object's path in the
    build directory. Same patch, other directory: `c4f8…` vs `358e…`, with 1218 differing `nm` lines, all of the
    inspected ones those names. Same directory: reproduced exactly.
  - The adversary also used clang 18.1.3, but at other paths. The r1 build had no prefix map.
  - So pinning a build across hosts means fixing WORKDIR and the toolchain image, then checking the sha.
- **Identity** (`diag/identity.sh`; raw output in `diag/records/`):

  | build | unit, merged seasons | files | result |
  |---|---|---|---|
  | r1 instrumented, guard off and on | c2-p030-U-G/129003 M, 1 | 557 | identical to pip |
  | 6N | c2-p030-U-G/129005 M, 1 | 609 | identical to pip |
  | #3650 | c2-p030-U-G/129005 M, 1 | 609 | identical to pip |
  | 6N | c1-p080-U-L/129004 M, 1 | 737 | identical to pip |
  | r2 instrumented `43a23d33…`, guard off and on | c1-p080-U-L/129004 M, 1 | 737 | identical to pip |
  | **log-only** `74e1d8a2…` | c2-p030-U-G/129005 M, 1 | 609 | identical to pip |
  | **log-only** `74e1d8a2…` | c1-p080-U-L/129004 M, 1 | 737 | identical to pip |
  | adversary: instrumented, guard off and on (their build) | c1-p080-U-L/129004 M, 1 | 737 | identical to pip |

  - No overflow occurred in any identity run, so these test the off-event path only.
  - No build uses FMA or fast-math. That is an argument for identity in general, not a proof; adoption should repeat
    identity on several units over many seasons.

## Marker-only ckpt60 branches (r2, NOTE)

- **Checked names-only:** the MANIFEST, the tar member list, and the done-marker's byte size; then the `-record`
  branch's member list, a prefix-only test on `EXTINCT.txt`, and `UNIT.txt` with the season masked.
- **Result:**

  | branch `ckpt/rbt-129-stage1-…-ckpt60` | MANIFEST season | tar holds | `-record` holds | verdict |
  |---|---|---|---|---|
  | `c2-p080-PW-G-129003` | `?` | the done-marker only (61 B) | `EXTINCT.txt` (standard pre-merge text), `KSALT.txt`, `UNIT.txt` "S60 done; extinct pre-merge" | extinct-pre-merge snapshot: **expected** |
  | `c1-p030-PW-G-129008` | `?` | the done-marker only (61 B) | `EXTINCT.txt` (standard), `UNIT.txt` "S60 done; extinct pre-merge" | extinct-pre-merge snapshot: **expected** |
  | `c1-p080-PW-L-129002` | `?` | the done-marker only (61 B) | `EXTINCT.txt` (standard), `KSALT.txt`, `UNIT.txt` "S60 done; extinct pre-merge" | extinct-pre-merge snapshot: **expected** |

- **Why the marker is 61 bytes.** The snapshot job writes `_finish(d, tag, "skipped: extinct pre-merge at season N")`
  (`stages.py`), that is, a timestamp plus that note. A normal ckpt60 marker is 21 bytes, a timestamp only.
- **Consequence.** No anomaly; these are covered by the readout's integrity exception. A census (d) must source these
  units from their `-record` (and `-ksalt`) branches, not from ckpt60.

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
