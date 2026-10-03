# RBT-133 spike: cross-platform determinism through WebAssembly — readout

**Question (Ethan, 2026-10-03).** Can rabbitstew get bit-identical results on ARM (the M4 laptop) and x86 (cloud
containers) by running physics, and if needed the brain, as WebAssembly instead of writing its own engine?

**Answer.**

1. **The divergence is everywhere, not only "in the physics".** On both arm64 platforms tried, three layers each diverge
   from x86 independently: MuJoCo's model compiler, MuJoCo's step (open loop, from x86's own compiled model and state:
   the first `mj_step` differs), and the brain (numpy, fed x86's recorded sensor readings: 1 ULP at tick 1). Linux-arm64
   and macOS-arm64 also differ from each other. The Python-side XML is identical on all three. x86 Intel and x86 AMD
   agree bit for bit (§1).
2. **WASM fixes it for the bout.** MuJoCo 3.14.0 + the RBT-129 patch builds to WASM (Emscripten 4.0.10, `-ffp-contract=off`,
   no SIMD, no relaxed SIMD; the build reproduces byte for byte on a fresh CI runner). With the arena bout's sensors and
   brain ported to C in the same module, **two pinned bouts (open loop and closed loop) are byte-identical on x86 Intel,
   x86 AMD, linux-arm64 and macOS-arm64 (Apple M1), under Node 20, 22 and 24, and in headless Chromium**: every physics
   state after every `mj_step` (3,200 per bout), and every tick's sensors, activations and ctrl (§2, §3).
3. **Cost.** WASM physics is **1.43×** native on the same machine. But today's bout is 82% Python: the whole bout in WASM
   is **0.23×** today's cost per bout (~4.6–5.8 core-s per arm-season against DESIGN.md §11.2's 20–25, bout share only);
   Python driving WASM physics alone would be ~1.08× (§5).
4. **Recommendation: keep the one-platform rule for the RBT-129 sweep; adopt WASM first where it is cheap and opens
   something new (champion export to the browser, deterministic replay), and build a whole-bout WASM backend as its own
   ticket only if laptop↔cloud pairing becomes a requirement.** The work, the parts that must also become deterministic
   outside the bout, and an estimate are in §6.
5. **The browser.** The same module runs in Chromium and reproduces the Node/x86 bytes. Live three.js playback of
   champions is a direct consequence, not a further research question (§7).

Every number below is re-derivable from the committed scripts; CI runs are on branch `wasm-determinism-spike`
(workflow `.github/workflows/rbt133-wasm-spike.yml`, branch-only).

## Files by role

| role | path |
|---|---|
| step 1 probe (gen-0 fingerprint, closed-loop record/compare, open-loop physics and brain replays, numpy/libm probe) | `spikes/wasm/locate/probe.py`, `spikes/wasm/locate/ci.sh` |
| step 1 x86 references (two gen-0 bouts of RBT-96 seed 201, recorded on this session's x86 container) | `spikes/wasm/locate/ref-x86/` |
| step 1 readout (CI run 37157969294: x86 AMD EPYC, linux-arm64, macOS M1) | `spikes/wasm/locate/ci-run-37157969294/compare.txt`, `*/gen0.txt`, `*/numpy-probe.txt`, `*-summary.json` |
| WASM build, reproducible | `spikes/wasm/toolchain/build.sh`, expected hashes `spikes/wasm/toolchain/EXPECTED.txt` |
| native control build (same source and harness, same FP flags, host compiler and libm) | `spikes/wasm/toolchain/build_native.sh` |
| the bout in C (arena sensors, brain, settle, explosions, fitness) | `spikes/wasm/harness/rbt_wasm.c` |
| bout export (XML, MJB, post-settle state, ctrl, brains) | `spikes/wasm/pack.py` → `spikes/wasm/packs/{conventional-0,holistic-0}/` |
| checker (state rows hashed exactly as the probe hashes them) | `spikes/wasm/check.py` |
| step 3 runner and x86 WASM fingerprints | `spikes/wasm/run_wasm.sh`, `spikes/wasm/ref-wasm-x86/` |
| step 3 readout (CI run 37158742068) | `spikes/wasm/ci-run-37158742068/wasm-vs-x86.txt`, `wasm-fingerprints.txt` |
| browser | `spikes/wasm/web/{build_web.sh,index.html,drive.mjs,chromium-result.txt}` |
| cost | `spikes/wasm/bench.py`, `spikes/wasm/bench.txt` |

## 1. Where ARM and x86 part ways (step 1)

**Method.** RBT-96's arena config (seed 201, generation 0, `brain_model: rich`) re-run on four machines. Inside one tick
the order is sensors → brain → ctrl → physics, so the first quantity that differs names the layer that introduced the
difference. Two open-loop replays isolate the layers: x86's compiled model and post-settle state driven by x86's ctrl
sequence through the local MuJoCo, and x86's recorded sensor readings fed to the local `RuntimeBrain`. Positive control:
the same machine re-recording, replaying and recompiling gives no difference anywhere.

**Is the macOS runner the laptop?** Nearly. Its gen-0 row reproduces the laptop's (RBT-85 `base-201`) `c_best 0.991400`,
`c_mean 0.399852` and `h_mean 0.487005` to the printed digit, but not `h_best` (0.546899 against 0.537182). So the Apple
M1 runner is a close proxy for the M4, not a proven one (open item 1). The cloud row (RBT-96 `s0-201`) is reproduced
exactly by this container and by the AMD runner (40/40 bouts bit-identical).

| platform pair | XML | compiled model (MJB) | settle (200 steps, ctrl 0) | open-loop physics from x86's model and state | brain on x86's sensors | gen-0 row |
|---|---|---|---|---|---|---|
| x86 Intel ↔ x86 AMD EPYC | same | same | same | same, 3,000/3,000 steps | same | same, 40/40 bouts |
| x86 ↔ linux-arm64 | same | **differs** | differs at step 0 | **differs at step 0** | **differs at tick 1** (1 ULP) | differs (`c_best` 1.000000) |
| x86 ↔ macOS-arm64 (M1) | same | **differs** | differs at step 0 | **differs at step 0** | **differs at tick 1** (1 ULP) | differs (`c_best` 0.991400, = laptop) |
| linux-arm64 ↔ macOS-arm64 | same | same (conventional) / differs (holistic) | same / differs at step 11 | — | — | differ from each other |

(both bouts; `ci-run-37157969294/compare.txt`.) The linux-arm64 ↔ macOS pair on the wheeled bout is the sharpest
single result: the same compiled model, a bit-identical 200-step settle and identical tick-0 sensors, brain and ctrl, then
MuJoCo's **second** substep under non-zero ctrl differs. Two arm64 builds of one wheel disagree inside the step.

**Mechanisms, from the numpy/libm probe and the MuJoCo source.**
- *MuJoCo, x86 vs arm64:* the linux-aarch64 wheel of MuJoCo 3.14.0 contains **11,432 scalar fused multiply-adds**
  (`fmadd` 10,290, `fmsub` 918, `fnmadd` 104, `fnmsub` 120); the x86_64 wheel contains **none**
  (`locate/fma_count.txt`). A fused `a*b+c` rounds once instead of twice, so every one of them is a place where arm64
  and x86 can differ in the last bit. The x86 wheel's hand-written AVX paths (`mjUSEPLATFORMSIMD`) are **not** a source
  here: a scalar build of the same source with AVX off replays the x86 wheel's open loop bit for bit over all 3,000
  steps of both bouts (§2). (The macOS wheel is a universal Mach-O this container cannot disassemble; its FMA count is
  unmeasured.)
- *MuJoCo, linux-arm64 vs macOS:* the libm. Apple's `sin`, `cos`, `tanh`, `exp` give different bits from glibc's on the
  probe's 4,096 inputs (`math.*` and `np.*` alike); glibc's scalar libm agrees between x86 and linux-arm64.
- *The brain:* `W @ a` goes to BLAS `gemv` (OpenBLAS kernels differ between x86 and arm64; macOS uses Accelerate);
  all three platforms give different bits for the 40×40 and 12×12 products. On macOS `np.tanh` and `np.sin` differ
  from x86 too.
- *Inside x86:* `np.tanh` ≠ `math.tanh` on the same machine (numpy dispatches its own AVX-512 kernels). Both x86 hosts
  here have AVX-512, so they agree; an x86 host **without** AVX-512 is untested and may not (open item 3).

So RBT-96 §5's "in the physics" is right but incomplete: the physics is one of three independent sources, and fixing
any one of them leaves the other two (proposed erratum pointer in §9).

## 2. The WASM build (step 2)

`spikes/wasm/toolchain/build.sh OUTDIR` (`spikes/wasm/toolchain/EXPECTED.txt`):
- Emscripten **4.0.10** (MuJoCo's own `wasm/README.md` pin), emsdk commit `96c657fc`, release `8103ffed`;
- MuJoCo **3.14.0** commit `9ecbb9d7`, **the RBT-129 patch** `mujoco-3.14.0-rbt129-epa-log.patch` (sha256 checked; the
  module reports its build id `rbt129-epa-instr/3 … guard-off count-and-log`, so the patched engine is the one linked);
- single-threaded, no embind bindings, static `libmujoco.a` (LTO) linked into the harness;
- `-O3 -ffp-contract=off -fno-fast-math`; no `-msimd128`, no `-mrelaxed-simd`. The script **disassembles the module and
  refuses it** if any SIMD or relaxed instruction is present (0 and 0), and refuses a forbidden flag in
  `compile_commands.json`. `mjUSEPLATFORMSIMD` is never defined under Emscripten, so MuJoCo takes its scalar paths;
- libm is Emscripten's musl, compiled to WASM: the same instructions on every host.

**Reproducible:** a fresh `ubuntu-24.04` runner built `rbt_wasm.wasm` with the same sha256 as this session
(`d48ef3e9…`; CI run 37158742068, job `wasm-build`, "REPRODUCED"). Build time ~2 min on 4 cores; module 2.9 MB.

**The RBT-129 patch and the FP flags change nothing on x86.** The same patched source built natively with the same
discipline (`toolchain/build_native.sh`: clang 18, AVX off, `-ffp-contract=off`) and driven by the harness's open loop
reproduces the pip wheel's x86 reference recording bit for bit, 3,000/3,000 steps in both bouts
(`check.py` against `locate/ref-x86/*/steps.txt`). So on x86 the patch is log-only as RBT-129 intends, and the wheel's
AVX paths do not alter these bouts.

The harness (`harness/rbt_wasm.c`, ~450 lines) is `Simulation.settle` (plain), `Simulation.step`, the rich sensor set
(contact, oscillator, target/opponent direction and distance, up, velocity, height, joint angle and velocity),
`RuntimeBrain.step` with all seven transfer functions, `effector_output`, the explosion check, and `zero_sum_fitness`,
with every sum in a fixed left-to-right order. Inputs come from `pack.py`, which re-derives the brains from the
committed genotypes and asserts that this checkout generates the recording's XML. **Fidelity check against the Python
bout on x86:** the WASM-compiled model and the 200-step settle are bit-identical to native Python's; tick-0 sensors are
identical, activations within 1 ULP (glibc/musl `tanh` against numpy's); by tick 20 the gap is ~1e-15, the same order as
the cross-platform gap of §1. So the port reproduces the Python bout to ULP level, and then diverges from it chaotically
exactly as another platform would. It is a faithful port, not a bit-identical one: it cannot be, since the Python bout
is not bit-identical to itself across machines.

## 3. Determinism (step 3)

The same `rbt_wasm.wasm` (built once, on the CI x86 runner) run on each platform; each run's state stream
(time, qpos, qvel, act, qacc_warmstart after every `mj_step`) compared with this session's x86 run.

| host | Node | conventional open loop | conventional bout | holistic open loop | holistic bout |
|---|---|---|---|---|---|
| x86 Intel Xeon (this session) | 22.22.0 | `d4a76c18` | `464197df` | `4678494e` | `ce2630d3` |
| x86 AMD EPYC (CI) | 22.22.0 | identical | identical | identical | identical |
| linux-arm64 (CI) | 22.22.0 | identical | identical | identical | identical |
| linux-arm64 (CI) | 24 | identical | identical | identical | identical |
| macOS-arm64, Apple M1 (CI) | 22.22.0 | identical | identical | identical | identical |
| macOS-arm64, Apple M1 (CI) | 20 | identical | identical | identical | identical |
| headless Chromium 141 (this session) | — | identical | identical | identical | identical |

"Identical" is byte-for-byte on the whole `states.bin` (3,000 or 3,200 rows), and for the closed-loop bouts also on
`ticks.bin` (every tick's sensors, activations and ctrl): 20/20 state streams and 10/10 tick streams
(`ci-run-37158742068/wasm-vs-x86.txt`). The bouts' fitnesses are therefore identical to the last bit
(conventional 0.993301 / 0.006699, holistic 0.508598 / 0.491402: `ref-wasm-x86/`).

**Is the test able to see a difference?** Yes: the same harness built natively diverges from the WASM build on the same
x86 machine at step 12 (conventional, open loop) and step 72 (holistic), and native x86 diverges from native arm64 at
step 0 (§1). The fingerprint is a sha256 of every state byte, so a single ULP anywhere fails it.

## 4. Control: is it WASM, or just the build flags?

`toolchain/build_native.sh` builds the same patched source and the same harness natively, with the WASM build's
discipline: scalar paths (AVX off), `-ffp-contract=off`, no fast-math. If that reproduced across platforms, WASM would
not be what buys determinism.

RESULT-NATIVE-CONTROL

## 5. Cost (step 4)

One core each, the same two 15 s bouts, 20 repetitions (`bench.py`, `bench.txt`; this session's Xeon @ 2.1 GHz):

| path | s per bout | relative to native C | relative to today |
|---|---|---|---|
| today: `run_bout` (Python sensors + numpy brain + the pip wheel's MuJoCo) | 0.299 | — | 1.00 |
| of which inside `mj_step` | 0.054 (18%) | — | — |
| the C harness, native (scalar MuJoCo) | 0.048 | 1.00 | 0.16 |
| the C harness, WASM under Node 22 | 0.069 | **1.43** | **0.23** |

On the M1 runner the WASM bout takes 0.078–0.099 s (CI log), the same order.

Scaled to DESIGN.md §11.2's 20–25 core-s per arm-season on today's path:
- **Python driving WASM MuJoCo** (sensors and brain stay in Python): only the 18% physics share pays the 1.43×, so
  ~21.6–27.0 core-s, **+8%**. But this option does **not** give determinism by itself (§1: the brain and the sensors'
  numpy diverge too), so it would also need a deterministic Python brain (no BLAS, fixed-order sums, transcendental
  functions from the WASM libm), which costs more Python time again, unmeasured.
- **The whole bout in WASM**: ~4.6–5.8 core-s for the bout share, **×0.23**. The arm-season's non-bout share (breeding,
  bookkeeping, I/O) is not in this number; at most it can only raise it toward the bout's share of today's 20–25.

The caveat on both: the spike's bouts are the arena's; an ecology arm-season is foraging (smell, eating, regrowth), whose
Python share is if anything larger (`_intensity` per sensor per tick), so the whole-bout saving is unlikely to shrink.

## 6. What adoption would take

Three ways, in the order I would do them.

**A. Champion export and deterministic replay (small, ~2–4 days).** `pack.py` already turns a recorded bout into a
self-contained input; generalise it to "a genotype pair + SimConfig → pack", add the foraging items as static geoms, and
ship the module with a page (§7). No change to how runs are made; nothing in the registered pipeline moves.

**B. A selectable whole-bout WASM backend (`--engine wasm`) (~2–3 weeks to parity, then validation).**
- Port the rest of `Simulation` to C: the food world (smell intensity and contrast with its running baseline, eating,
  regrowth, patchy and persistent food, the agent sensor), waypoints and hold time, `settle_until_rest` with kinetic
  damping, the score family (`closeness`, `time_at_target`, `progress`, `upright`, the score vector), actuator work
  accounting, and trajectory recording. About 1,000 lines of `simulation.py` becomes ~1,500 of C.
- Move the **lift pass** into the module: `build_model` compiles once natively to measure the lift, and that compile is
  platform-dependent (§1, MJB differs).
- Any randomness inside a bout (food placement uses `self._food_rng`) must be drawn in Python, where numpy's generators are
  bit-stable, and passed in, or reimplemented in C to the bit.
- A bridge: `wasmtime` from Python (wheels exist for all three platforms; per-bout calls, so call overhead is
  irrelevant) or a pool of Node workers. Untested here; `wasmtime`'s speed against V8 is open item 4.
- **Two implementations of one simulation is the real cost.** It needs golden tests holding the two within a stated ULP
  tolerance on the first ticks of a bank of bouts (as §2 does for two bouts), or the Python path retired for runs and
  kept only as reference. The RBT-129 sweep's registered numbers come from the Python path, so a backend change mid-sweep
  would need a ruling.

**C. Everything around the bout.** Bit-identical *runs* (not bouts) also need every float that feeds back into evolution
to agree: fitness means and ranking (numpy reductions), mutation arithmetic, synthesis. Step 1 found the XML identical on
all platforms, but only because it is written at 6 significant digits (`world._fmt`, `:g`): a value within an ULP of a
rounding boundary would still flip (rare, not impossible). `rng.normal` is bit-stable by numpy's policy except in its
`exp`/`log` tails. An audit of these, and a cross-platform CI job running a short whole run (a few generations of the
arena and of an ecology) on all three platforms, is ~1 week and is what would justify retiring the one-platform rule.

## 7. Champions in the browser

The same harness linked with `-sENVIRONMENT=web` (`web/build_web.sh`, 2.9 MB WASM + 135 kB of packs) runs in headless
Chromium 141 and reproduces the Node/x86 state streams byte for byte (`web/chromium-result.txt`). So a champion bout
played live in a page is **the same bout** the run scored, not a re-simulation that drifts. rabbitstew's replay page
(`visualizer.py`) already draws bodies with three.js from per-frame positions and quaternions; live playback means reading
`geom_xpos`/`geom_xmat` from the module's memory each frame instead of from a `.traj` file, which is a few dozen lines.
For games and art, where the creature reacts to a player rather than replaying a bout, determinism is no longer the
point but the module still is: the brain and sensors are already in it, so "a champion, live, in a page" needs only an
input hook for the player's object. Upstream's own `@mujoco/mujoco` npm package (embind bindings of the whole API) is
the alternative for richer scenes; it is built without the RBT-129 patch and without the FP discipline here, so it is
fine for art and not for evidence.

## 8. Recommendation

- **For the research programme: keep "paired arms on one platform" and `platform.json`.** It is cheap and correct, and
  §1 confirms that x86 Intel and x86 AMD agree bit for bit, the case the cloud depends on. Do not change engines under
  the RBT-129 sweep.
- **Adopt WASM first as A** (export and replay), which costs days, touches nothing registered, and gives Ethan's games and
  art a deterministic, portable creature.
- **Build B + C only when a design needs laptop↔cloud pairing, or when the speed is wanted for itself.** If B is built,
  it is ~4× cheaper per bout than today's path, so the port pays for itself in core-hours over any sweep the size of
  RBT-129 (2,000+ core-h); but it must be the only engine for the runs that use it, with golden tests, not a second one
  run beside the first.
- **No in-house engine.** Nothing here needs one: MuJoCo itself is deterministic once its build and libm are fixed, and
  WASM fixes both by construction.

## 9. What is and is not claimed

- **Claimed:**
  - the four layers of §1 and which of them diverge on these platforms, for these two bouts;
  - byte-identical WASM state and tick streams for the two pinned bouts across five host/runtime combinations and
    Chromium;
  - a reproducible WASM build of MuJoCo 3.14.0 + the RBT-129 patch;
  - the cost ratios of §5 on one Xeon core.
- **Not claimed:**
  - that the M1 runner is the M4 laptop (3 of 4 gen-0 statistics match; open item 1);
  - anything about a whole evolutionary run, the ecology or the foraging world in WASM (not ported);
  - that an x86 host without AVX-512 reproduces the cloud (open item 3);
  - a measured cost of a deterministic-Python brain or of `wasmtime`.
- **This spike pre-registered nothing**; its readouts are descriptive.
- **Proposed erratum pointer (for the coordinator, not made here):** `runs/RBT-96/REPORT.md` §5, "ARM M4 against x86
  diverges at generation 0 in the arena, in the physics": the physics is one of three independent sources; the model
  compiler and the brain's BLAS/libm diverge too (this file §1).

**Open items.** (1) Run `spikes/wasm/locate/probe.py gen0` and `spikes/wasm/run_wasm.sh` on the M4 itself: the first
says whether the laptop equals the M1 runner, the second is the actual question on the actual machine (~1 minute each).
(2) Seed more bouts (holistic bodies with ball and slider joints, an exploding body, contacts with terrain) into the
fingerprint bank before relying on it. (3) An x86 host without AVX-512. (4) `wasmtime` throughput against Node.
