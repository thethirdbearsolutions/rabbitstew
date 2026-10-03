# RBT-133 spike: cross-platform determinism through WebAssembly — readout

**Question (Ethan, 2026-10-03).** Can rabbitstew get bit-identical results on ARM (the M4 laptop) and x86 (cloud
containers) by running physics, and if needed the brain, as WebAssembly instead of writing its own engine?

**Amended after the adversary review** (`adversary/ADVERSARY.md`, findings F1–F15). Changes from the first version:
- §1: the replay evidence is now committed, not cited from job logs (F1); "three independent sources" becomes **two
  causes seen in three layers** (F4); the numpy/libm table is corrected (`np.tanh` is portable; linux-arm64's numpy
  `exp`/`log`/`arccos` differ) (F5); the M1 runner is **not shown to be** the laptop (F8).
- §3: the fingerprint now covers `ticks.bin` (sensors, activations and ctrl at every tick), and the bank has three more
  bouts chosen so the actuated robots use the oscillator, `sin`, `sign`, `integrate`, `relu`, `height`, `joint_angle`
  and `joint_velocity`, with little clipping (F2, F12).
- §5: the foraging group bout's physics share (26%, not 18%) and the corrected scaling; the saving is credited to the
  C port, not to WASM (F6, F7).
- §6–§8: the browser replays the **WASM** bout, which is the run's scored bout only if the run was scored in WASM;
  under today's pipeline it is a re-simulation that drifts (F3). Option A's scope is arena-only; estimates are labelled
  estimates (F13, F14). NaN sign bits are named as the untested gap in "by construction" (F9). The build note on
  `mjUSEPLATFORMSIMD` is corrected (F10).

**Answer.**

1. **Two causes, seen in three layers.** On both arm64 platforms tried, the model compiler, the MuJoCo step and the
   brain each diverge from x86 when given identical inputs (§1). The causes are (a) **how MuJoCo is compiled**: the
   aarch64 wheel contains 11,432 fused multiply-adds and the x86 wheel none, and on macOS the host libm and compiler
   differ besides; one no-FMA build fixes compile and step together between Linux x86 and Linux arm64 (§4); and
   (b) **numpy's BLAS** for the brain's `W @ a`. The Python-side XML is identical on all three; x86 Intel and x86 AMD
   agree bit for bit.
2. **WASM fixes it for the bout.** MuJoCo 3.14.0 + the RBT-129 patch builds to WASM (Emscripten 4.0.10,
   `-ffp-contract=off`, no SIMD, no relaxed SIMD; the build reproduces byte for byte on a fresh CI runner). With the
   arena bout's sensors and brain ported to C in the same module, **five pinned bouts, open loop and closed loop, give
   byte-identical physics state streams and byte-identical per-tick sensor/activation/ctrl streams** on x86 Intel, x86
   AMD, linux-arm64 and macOS-arm64 (Apple M1), under Node 20, 22 and 24, and in headless Chromium (§3).
3. **Cost.** The WASM bout is 1.43× the same C bout built natively. Against today's Python bout it is 0.23× on the
   arena bout and about **0.33×** on a foraging group bout, but almost all of that saving comes from moving the bout out
   of Python into C, not from WASM (native C alone is 0.16×). Python driving WASM physics alone is ~+8–11% and does not
   by itself give determinism (§5).
4. **WASM is sufficient, not strictly necessary.** A native build with FMA contraction off already agrees between Linux
   x86 and Linux arm64; only macOS still differs, through its libm and compiler (§4). A native build with a bundled libm
   is the untested cheaper alternative (open item 5).
5. **Recommendation:** keep the one-platform rule for the RBT-129 sweep; adopt WASM first for **portable champions**
   (games, art, a page that runs a creature live); build a whole-bout WASM backend as its own ticket only if
   laptop↔cloud pairing, or the ~3× speed, is wanted. The browser runs the module and reproduces its bytes; it shows
   the run's own scored bout only once runs are scored in WASM (§6–§8).

Every number below is re-derivable from the committed scripts; CI runs are on branch `wasm-determinism-spike`
(workflow `.github/workflows/rbt133-wasm-spike.yml`, branch-only).

## Files by role

| role | path |
|---|---|
| the bout bank (name, seed, population, gen-0 bout) | `spikes/wasm/bouts.txt` |
| step 1 probe (gen-0 fingerprint, closed-loop record/compare, open-loop physics and brain replays, numpy/libm probe) | `spikes/wasm/locate/probe.py`, `spikes/wasm/locate/ci.sh` |
| step 1 x86 references (recorded on this session's x86 container) | `spikes/wasm/locate/ref-x86/` |
| step 1 readouts | `spikes/wasm/locate/ci-run-37157969294/` (first run, two bouts), `spikes/wasm/locate/ci-run-RUN2/` (five bouts, with the replays) |
| FMA count in the pip wheels | `spikes/wasm/locate/fma_count.txt` |
| WASM build, reproducible | `spikes/wasm/toolchain/build.sh`, expected hashes `spikes/wasm/toolchain/EXPECTED.txt` |
| native control build (same source and harness, same FP flags, host compiler and libm) | `spikes/wasm/toolchain/build_native.sh` |
| the bout in C (arena sensors, brain, settle, explosions, fitness) | `spikes/wasm/harness/rbt_wasm.c` |
| bout export (XML, MJB, post-settle state, ctrl, brains) | `spikes/wasm/pack.py` → `spikes/wasm/packs/*/` |
| checker (state rows hashed as the probe hashes them; `ticks.bin` hashed) | `spikes/wasm/check.py` |
| step 3 runners and x86 fingerprints | `spikes/wasm/run_wasm.sh`, `spikes/wasm/run_native.sh`, `spikes/wasm/ref-wasm-x86/`, `spikes/wasm/ref-native-x86/` |
| step 3 readouts | `spikes/wasm/ci-run-37158742068/` (first run, two bouts, states only), `spikes/wasm/ci-run-RUN2/` (five bouts, states and ticks; native control; CI `BUILD.txt`) |
| browser | `spikes/wasm/web/{build_web.sh,index.html,drive.mjs,chromium-result.txt}` |
| cost | `spikes/wasm/bench.py`, `spikes/wasm/bench.txt`; the adversary's foraging bench `adversary/bench_adv.{py,txt}` |
| adversary review | `spikes/wasm/adversary/` |

## 1. Where ARM and x86 part ways (step 1)

**Method.** RBT-96's arena config (`brain_model: rich`), generation 0, re-run on four machines for the five bouts of
`bouts.txt`. Inside one tick the order is sensors → brain → ctrl → physics, so the first quantity that differs names the
layer that introduced the difference. Two open-loop replays isolate layers: x86's compiled model and post-settle state
driven by x86's ctrl sequence through the local MuJoCo, and x86's recorded sensor readings fed to the local
`RuntimeBrain`. Positive control: the same machine re-recording, replaying and recompiling gives no difference
anywhere (and the adversary re-derived both replays exactly, `adversary/rederive.txt`). The **sensor layer was not
isolated** (sensors are read from a state that already differs).

STEP1-TABLE

**Is the macOS runner the laptop? Not shown.** Its gen-0 row matches the laptop's (RBT-85 `base-201`) `c_best`, `c_mean`
and `h_mean` to the printed digit but not `h_best` (0.546899 against 0.537182); since `h_mean` agrees to six digits, at
least two holistic bouts must differ with cancelling deltas (`adversary/evidence.txt` §2). RBT-85 recorded no
`platform.json`, so the laptop's numpy and Python are unknown. The M1 runner is an Apple-silicon macOS host, which is
what the conclusions need; whether it reproduces the M4 is open item 1. The cloud row (RBT-96 `s0-201`) is reproduced
exactly by this container and by the AMD runner (40/40 bouts bit-identical).

**Mechanisms.**
- *MuJoCo, x86 vs linux-arm64: FMA contraction.* The linux-aarch64 wheel of MuJoCo 3.14.0 contains **11,432 scalar
  fused multiply-adds** (`fmadd` 10,290, `fmsub` 918, `fnmadd` 104, `fnmsub` 120); the x86_64 wheel contains **none**
  (`locate/fma_count.txt`). A fused `a*b+c` rounds once instead of twice. The control of §4 confirms it is sufficient:
  built with contraction off, linux-arm64 matches x86 to the bit. The x86 wheel's AVX paths are **not** a source: a
  scalar build replays the x86 wheel's open loop bit for bit (§2). (The macOS wheel is a universal Mach-O this
  container cannot disassemble; its FMA count is unmeasured.)
- *MuJoCo, macOS: more than FMA.* Even built with contraction off, macOS differs (§4). Apple's `sin`, `cos`, `exp` and
  `tanh` give different bits from glibc's on the probe's inputs (`math.*`; numpy's `sin`, `cos`, `exp`, `log`, `arccos`
  too). Its compiler differs as well; the two were not separated (F15).
- *The brain: BLAS.* `W @ a` goes to BLAS `gemv`. The 40×40 and 12×12 products differ on both arm64 platforms (OpenBLAS
  arm64 kernels on Linux; Accelerate on macOS). `np.tanh` is bit-identical on all three platforms, so the brain's arm64
  divergence is BLAS alone, and it first shows at tick 1 because `W @ 0 = 0` at tick 0.
- *numpy elsewhere:* linux-arm64's numpy `exp`, `log` and `arccos` also differ from x86's (its SIMD kernels); the
  arena brain does not use them.
- *Inside x86:* `np.tanh` ≠ `math.tanh` on the same machine (numpy dispatches its own kernels). Both x86 hosts here have
  AVX-512, so they agree; an x86 host **without** AVX-512 is untested (open item 3).

So RBT-96 §5's "in the physics" is right but incomplete: the brain diverges too, on a separate cause (proposed erratum
pointer in §9).

## 2. The WASM build (step 2)

`spikes/wasm/toolchain/build.sh OUTDIR` (`spikes/wasm/toolchain/EXPECTED.txt`):
- Emscripten **4.0.10** (MuJoCo's own `wasm/README.md` pin), emsdk commit `96c657fc`, release `8103ffed`;
- MuJoCo **3.14.0** commit `9ecbb9d7`, **the RBT-129 patch** `mujoco-3.14.0-rbt129-epa-log.patch` (sha256 checked; the
  module reports its build id `rbt129-epa-instr/3 … guard-off count-and-log`, so the patched engine is the one linked);
- single-threaded, no embind bindings, static `libmujoco.a` (LTO) linked into the harness;
- `-O3 -ffp-contract=off -fno-fast-math`; no `-msimd128`, no `-mrelaxed-simd`. The script **disassembles the module and
  refuses it** if any SIMD or relaxed instruction is present (0 and 0), and refuses a forbidden flag in
  `compile_commands.json`. `mjUSEPLATFORMSIMD` *is* defined (MuJoCo's default), but its AVX code is guarded by `__AVX__`,
  which Emscripten never defines, so the scalar paths are taken; the disassembly check is the guarantee (F10);
- libm is Emscripten's musl, compiled to WASM: the same instructions on every host.

**Reproducible:** a fresh `ubuntu-24.04` runner built `rbt_wasm.wasm` with the same sha256 as this session
(`d48ef3e9…`; its `BUILD.txt` is committed in `ci-run-RUN2/`). Build ~2 min on 4 cores; module 2.9 MB.

**The RBT-129 patch and the FP flags change nothing on x86.** The same patched source built natively with the same
discipline (`toolchain/build_native.sh`: clang 18, AVX off, `-ffp-contract=off`) and driven open loop reproduces the pip
wheel's x86 reference recording bit for bit, 3,000/3,000 steps in both original bouts (`check.py` against
`locate/ref-x86/*/steps.txt`).

**The harness** (`harness/rbt_wasm.c`, ~450 lines) is `Simulation.settle` (plain), `Simulation.step`, the rich
sensor set (contact, oscillator, target/opponent direction and distance, up, velocity, height, joint angle and velocity),
`RuntimeBrain.step` with all seven transfer functions, `effector_output`, the explosion check, and `zero_sum_fitness`,
with every sum in a fixed left-to-right order. `pack.py` re-derives the brains from the committed genotypes and asserts
that this checkout generates the recording's XML. **Fidelity.** On x86 the WASM-compiled model and the 200-step settle
are bit-identical to native Python's; tick-0 sensors are identical and activations within 2 ULP; the adversary loaded
the harness's own state at each of the 750 ticks back into Python and found `sensor_values` agreeing to ≤4.4e-16,
and every sensor type × axis on every part of four robots agreeing to ≤3.3e-16 (`adversary/faithful.txt`). The
closed-loop gap between C and Python then grows at the same rate as the x86↔arm64 gap. It is a faithful port, not a
bit-identical one. Off the tested path: `relu(NaN)`, `sign(-0.0)`, and effectors summing ≥ 8 units differ in edge
cases, and `pack.py` does not refuse `score != "distance"` (F11; follow-ups for any adoption).

## 3. Determinism (step 3)

The same `rbt_wasm.wasm` (built once, on the CI x86 runner) run on each host; each run's state stream (time, qpos,
qvel, act, qacc_warmstart after every `mj_step`) and, for the closed loop, its tick stream (every tick's sensors,
activations and ctrl) compared with this session's x86 run.

STEP3-TABLE

**Is the test able to see a difference?** Yes, for both streams.
- Physics (adversary `perturb.txt`): one ULP in one `init_state` qpos moves the state stream from row 0; one ULP in one
  unclipped ctrl entry from row 400; one digit of one mass in the XML from row 0.
- Brain (adversary `perturb_sweep.txt`, on the first two bouts): a one-ULP change to a single W entry moved the tick
  stream for 35/40 of the actuated holistic robot's entries and 5/5 of the non-actuated one's, and the state stream for
  18/40, 0/5, 131/150 and 144/150. That gap is why `ticks.bin` is now fingerprinted, and why three bouts with richer,
  little-clipped brains were added (ctrl at ±1: 0–6% of entries, against 62% in `holistic-0`).
- The same harness built natively diverges from the WASM build on the same x86 machine (step 12 and step 72 in the
  first two bouts), and native x86 diverges from native arm64 at step 0 (§1).

## 4. Control: is it WASM, or just the build flags?

`toolchain/build_native.sh` builds the same patched source and the same harness natively, with the WASM build's
discipline: scalar paths (AVX off), `-ffp-contract=off`, no fast-math.

NATIVE-TABLE

So: **between Linux x86 and Linux arm64 the build flags are the whole MuJoCo story**. Forbid FMA contraction and take
the scalar paths, and MuJoCo, the harness and glibc agree to the bit. **macOS differs even then**; what is left is
Apple's libm and compiler (not separated here). WASM removes both at once, because the module brings its own libm and no
host compiler touches it after the build.

This opens a cheaper option than WASM, **untested**: a native build with `-ffp-contract=off`, scalar paths, and a libm
**linked in** rather than taken from the host (musl's, or a correctly rounded one such as CORE-MATH), which should make
macOS agree too, at native speed instead of 1.43×. It is the same discipline WASM imposes, done by hand, and each
platform's binary becomes a separate artifact to verify (WASM ships one). Open item 5.

## 5. Cost (step 4)

One core each, 20 repetitions (`bench.py`, `bench.txt`; this session's Xeon @ 2.1 GHz), on the two original arena bouts:

| path | s per bout | relative to native C | relative to today |
|---|---|---|---|
| today: `run_bout` (Python sensors + numpy brain + the pip wheel's MuJoCo) | 0.299 | — | 1.00 |
| of which inside `mj_step` | 0.054 (18%) | — | — |
| the C harness, native (scalar MuJoCo) | 0.048 | 1.00 | 0.16 |
| the C harness, WASM under Node 22 | 0.069 | **1.43** | **0.23** |

The adversary re-ran it (1.41×, ×0.23; the timing proxy adds 0–3%, `adversary/bench_rerun.txt`, `bench_adv.txt`).
On the M1 runner the WASM bout takes 0.078–0.099 s.

**What the ratios mean (F7).** 1.43× is the whole C bout in WASM against the same C built natively: physics, sensors and
brain. The ×0.23 comes from leaving Python, not from WASM.

**Scaling to DESIGN.md §11.2's 20–25 core-s per arm-season.** An arm-season is an ecology season, i.e. a foraging
group bout, not the arena bout measured above. The adversary measured one (RBT-105 config, four robots, gen-0 founders):
0.65 s per group bout, **26%** inside `mj_step` (19–32% per bout) (`adversary/bench_adv.txt`). So the Python share
there is *smaller*, not larger, than in the arena, and:
- **Python driving WASM MuJoCo**: the physics share pays 1.43×, so ~**+11%** (~22–28 core-s). It does **not** give
  determinism by itself (the brain diverges through BLAS), so it also needs a deterministic Python brain (no BLAS,
  fixed-order sums), unmeasured, plus the Python↔WASM call overhead, unmeasured.
- **The whole bout in WASM**: if the foraging bout's non-physics share ported to C as efficiently as the arena's did,
  ~**×0.33** (~6.7–8.4 core-s for the bout share; ~3× cheaper). This is an extrapolation: the food world (smell,
  eating, regrowth) is not ported, and the arm-season's non-bout share (breeding, bookkeeping, I/O) is not in it.

## 6. What adoption would take (estimates, not measurements)

**A. Portable champions (arena now; foraging needs part of B).** `pack.py` already turns a recorded bout into a
self-contained input; generalise it to "a genotype pair + SimConfig → pack". That covers arena champions, a few days.
The programme's current champions are ecology foragers, which need the food world in C (B's first item) before they can
be exported. Nothing in the registered pipeline moves.

**B. A selectable whole-bout WASM backend (`--engine wasm`).**
- Port the rest of `Simulation` to C: the food world (smell intensity and contrast with its running baseline, eating,
  regrowth, patchy and persistent food, the agent sensor), waypoints and hold time, `settle_until_rest` with kinetic
  damping, the score family, actuator work accounting, trajectory recording. My estimate is ~1,500 lines of C and 2–3
  weeks to parity, unmeasured.
- Move the **lift pass** into the module: `build_model` compiles once natively to measure the lift, and that compile is
  platform-dependent (§1).
- Draw any in-bout randomness (food placement) in Python, where numpy's generators are bit-stable, and pass it in.
- A bridge: `wasmtime` from Python or a pool of Node workers (untested; open item 4).
- Handle NaN: WASM leaves the sign bit of a computed NaN unspecified, and the module can observe it (`f64.copysign`,
  `i64.reinterpret_f64`). No tested bout exploded; an exploding bout must be added to the bank, and the harness should
  canonicalise NaN before any branch or hash (F9).
- **Two implementations of one simulation is the real cost.** It needs golden tests holding the two within a stated
  tolerance on the first ticks of a bank of bouts (as §2 does for five), or the Python path retired for runs that use
  WASM. The RBT-129 sweep's registered numbers come from the Python path, so a backend change mid-sweep would need a
  ruling.

**C. Everything around the bout.** Bit-identical *runs* also need every float that feeds back into evolution to agree:
fitness means and ranking, mutation arithmetic, synthesis. The XML agreed on every bout because it is written at 6
significant digits (`world._fmt`, `:g`); a value within an ULP of a rounding boundary would still flip (rare, not
impossible). `rng.normal` is bit-stable by numpy's policy except in its `exp`/`log` tails. An audit, plus a CI job
running a few generations of the arena and of an ecology on all three platforms, is what would justify retiring the
one-platform rule (my estimate: about a week).

## 7. Champions in the browser

The same harness linked for the web (`web/build_web.sh`: a separate 2.9 MB module, its sha256 recorded and the same
no-SIMD disassembly check applied) runs in headless Chromium 141 on x86. It reproduces the Node/x86 **state and tick
streams** of all five bouts byte for byte (`web/chromium-result.txt`). The browser was tested on x86 only; that the
same page reproduces on an arm64 browser follows from the Node results, but was not run.

**What that does and does not mean (F3).** The page replays the **WASM** bout exactly. Today's runs are scored on the
Python/pip-wheel path, and the WASM bout departs from that at the first bout step (row 200 of the conventional bout;
its opponent ends 79.3 m from the centre in WASM against 127.7 m in the scored bout). So **under today's pipeline a
champion played in the page is a faithful re-simulation that drifts**, exactly as a laptop replay of a cloud run does.
It is the run's own scored bout only if runs are scored in WASM (option B).

For games and art that is mostly beside the point: there the creature reacts to a player rather than replaying a bout,
and the module already carries the brain and sensors, so "a champion, live, in a page" needs an input hook and a
renderer. rabbitstew's replay page (`visualizer.py`) already draws bodies with three.js from per-frame positions and
quaternions; reading them from the module's memory instead of a `.traj` file is, I expect, a small change (not built
here). Upstream's own `@mujoco/mujoco` npm package (embind bindings of the whole API) is the alternative for richer
scenes; it lacks the RBT-129 patch and this FP discipline, so it is fine for art and not for evidence.

## 8. Recommendation

- **For the research programme: keep "paired arms on one platform" and `platform.json`.** It is cheap and correct, and
  §1 confirms that x86 Intel and x86 AMD agree bit for bit, the case the cloud depends on. Do not change engines under
  the RBT-129 sweep.
- **Adopt WASM first for portable champions** (A): days for arena champions, more once the food world is ported. It
  touches nothing registered and gives Ethan's games and art a creature that behaves the same on every device.
- **Build B + C only when a design needs laptop↔cloud pairing, or the speed is wanted for itself.** The ~3× saving per
  bout is real but is the C port's, not WASM's; if B is built it must be the only engine for the runs that use it, with
  golden tests.
- **If native speed matters more than one binary**, the §4 control says what a native path must do: no FMA
  contraction, scalar paths, and a bundled libm. It is untested on macOS with a bundled libm (open item 5).
- **No in-house engine.** Nothing here needs one: MuJoCo itself reproduces across platforms once its build and its libm
  are fixed. WASM fixes both by construction, apart from NaN sign bits, which an exploding bout would exercise
  (open item 6).

## 9. What is and is not claimed

- **Claimed:**
  - for these five bouts, which layers diverge on these platforms, and that two causes (MuJoCo's build and libm;
    numpy's BLAS) account for them;
  - byte-identical WASM state streams and tick streams for the five bouts, open and closed loop, across six
    host/runtime combinations and Chromium on x86;
  - a reproducible WASM build of MuJoCo 3.14.0 + the RBT-129 patch;
  - that a native no-FMA build agrees between Linux x86 and Linux arm64, and not on macOS;
  - the arena cost ratios of §5 on one Xeon core.
- **Not claimed:**
  - that the M1 runner reproduces the M4 laptop (it is shown to differ from the laptop's RBT-85 record; open item 1);
  - anything about a whole evolutionary run, the ecology or the foraging world in WASM (not ported); the foraging cost
    figure is an extrapolation;
  - that an x86 host without AVX-512 reproduces the cloud (open item 3);
  - determinism through NaN (no tested bout exploded);
  - a measured cost of a deterministic-Python brain or of `wasmtime`; the effort figures in §6.
- **This spike pre-registered nothing**; its readouts are descriptive.
- **Proposed erratum pointer (for the coordinator, not made here):** `runs/RBT-96/REPORT.md` §5, "ARM M4 against x86
  diverges at generation 0 in the arena, in the physics": the brain diverges too, through numpy's BLAS, and the model
  compiler before the first step (this file §1).

**Open items.** (1) Run `spikes/wasm/locate/probe.py gen0` and `spikes/wasm/run_wasm.sh` on the M4 itself: the first
says whether the laptop equals the M1 runner, the second is the actual question on the actual machine (~1 minute each).
(2) Grow the bank: a ball- and slider-jointed actuated body, an exploding body, terrain contact. (3) An x86 host without
AVX-512. (4) `wasmtime` throughput against Node. (5) A native build with a bundled libm on macOS. (6) NaN
canonicalisation and an exploding bout (F9).
