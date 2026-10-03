# RBT-133 adversary: the WASM determinism spike's readout (`spikes/wasm/REPORT.md` @ 70e201b)

Adversary: a named subagent of session `session_01SKMyq7aQvFsy471ZvMZcPq`, x86 only (Intel Xeon @ 2.10 GHz, 4 cores,
Python 3.11.15, mujoco 3.14.0, numpy 2.4.6, Node 22.22.0). The ARM evidence is the committed CI output; nothing here ran
on arm64. Read at 5df6577, re-read at 70e201b (§1's mechanism correction and §4's native control landed while this ran).
Nothing outside `spikes/wasm/adversary/` was changed.

**Verdict: the central result holds; three claims built on it do not, as written.** The same `rbt_wasm.wasm` gives the
same physics state stream on x86 and arm64 for the two pinned bouts, the instrument can see a one-ULP change, and the C
port is faithful to the Python bout far beyond what the report itself shows. But (M1) §1's isolation table rests on
replay outputs that are in no committed file; (M2) "every tick's sensors, activations and ctrl" is not measured by the
committed fingerprint, which is blind to most of the holistic bout's brain; and (M3) §7's "the same bout the run
scored" is false under today's pipeline.

## Probes

All under this directory; `rederive.sh DIST NATIVE_BIN SCRATCH` re-runs every one and rewrites its readout.

| probe | → | covers |
|---|---|---|
| `perturb.py` | `perturb.txt`, `perturb_sweep.txt` | positive controls: one input +1 ULP (W, bias, init state, ctrl, an XML digit); every non-zero W entry of every robot one at a time; an empty `states.bin` |
| `faithful.py` | `faithful.txt` | the harness against the Python reference recordings: closed-loop gap per tick; **teacher-forced** sensors (Python `sensor_values` on the harness's own state at every tick); teacher-forced brain and effectors |
| `semcheck.c`, `semcheck.py` | `semcheck.txt` | the branches the bouts never take: every sensor source × axis on every part of all four robots (hinge, slide, ball, free), with and without an opponent; random brains with all seven transfer functions, zeros, −0.0, 1e300, NaN |
| `evidence.py` | `evidence.txt` | re-derivations from committed files only: bout coverage and ctrl clipping; gen-0 identity per platform; the laptop row; the numpy/libm probe table; which readouts contain the replays |
| `rederive.sh` | `rederive.txt` | WASM fingerprints here vs `ref-wasm-x86/`; WASM compile and settle vs the wheel; harness open loop vs the wheel's recording; probe.py's same-platform replays |
| `bench.py` (unchanged), `bench_adv.py` | `bench_rerun.txt`, `bench_adv.txt` | §5's numbers re-run; the timing proxy's overhead; the mj_step share of a **foraging** group bout |

## Re-derived first (credit where it holds)

- **WASM fingerprints reproduce here.** This container's module (sha256 `d48ef3e9…`, = `EXPECTED.txt`) gives all four
  committed x86 fingerprints (`rederive.txt`). The CI comparisons are genuine: each runner hashes the `states.bin` it
  wrote and diffs against the committed reference; no `--write-ref` in CI; an empty `states.bin` hashes to `e3b0c442…`
  and cannot pass the diff (`perturb.txt`).
- **The instrument sees one ULP in the physics.** +1 ULP in one `init_state` qpos moves the open-loop stream at row 0;
  in one unclipped ctrl entry at tick 100, at row 400/402; one digit of one mass in the XML, at row 0; one conventional
  W entry, at row 204 (`perturb.txt`). Sweeping every non-zero W entry: 131/150 and 144/150 move the conventional
  bout's fingerprint (`perturb_sweep.txt`).
- **probe.py's open-loop replays isolate what they say.** Restoring time, qpos, qvel, act and qacc_warmstart plus
  `mj_forward` reproduces the same-platform recording over 3,000/3,000 steps, both bouts; the brain replay reproduces
  750/750 ticks; the XML recompiles to the same MJB (`rederive.txt`). Brain weights are copied from the genotype
  verbatim (`synthesis.py` l.313–331), so a brain-replay difference is BLAS/libm, not synthesis.
- **"x86 Intel ↔ x86 AMD agree bit for bit": 40/40 gen-0 bouts, fitness and distance hex** (`evidence.txt` §2); both
  arm64 platforms 0/40.
- **The x86 wheel = the scalar no-FMA build (§2's new claim): holds.** `rbt_native` open loop reproduces the wheel's
  recording 3,000/3,000 rows in both bouts; WASM's compiled MJB equals the wheel's and its 200-step settle is
  bit-identical (first differing row 200 / 208, the first bout step) (`rederive.txt`).
- **The C port is faithful, more strongly than §2 shows** (F11). §2 shows ULP agreement for ~20 ticks, then chaos. The
  teacher-forced check removes the chaos: Python's `sensor_values`, evaluated on the harness's **own** state at each of
  the 750 ticks, agrees with the harness's readings to ≤ 4.4e-16 in both bouts, for both the WASM and native builds; the
  Python brain fed the harness's sensor stream stays within 5.7e-15 / 1.9e-13; `effector_output` on the harness's
  activations gives its ctrl bit for bit at 750/750 ticks (`faithful.txt` B, C). Off the bouts' path, every sensor
  source × axis on every part of all four robots agrees to ≤ 3.3e-16 (`semcheck.txt`). "Faithful to ULP level, then
  chaotic divergence" is honest: the closed-loop gap grows at the cross-platform rate (conventional sensors 3.5e-12 at
  tick 50, 6.4e-5 at 100; x86↔linux-arm64 1.8e-9 and 3.4e-2; holistic 4.7e-11 at 200 and 2.4e-8 at 400 against
  5.0e-11 and 2.5e-8).
- **§5's arithmetic reproduces** (`bench_rerun.txt`: 1.41×, ×0.23, ×1.07), and bench.py's timing proxy costs only 0–3%
  of the Python bout (`bench_adv.txt` §1).
- **No JS math in the module.** Its imports are WASI/Emscripten syscalls and clocks only; no `Math.*` reaches a float
  in the bout.

## Findings

| # | sev | claim (REPORT §) | verdict | evidence |
|---|---|---|---|---|
| F1 | **MUST** | §1 table and Answer 1: open-loop physics "differs at step 0" and brain "differs at tick 1 (1 ULP)" on both arm64; Intel↔AMD "3,000/3,000 steps" | **unverifiable from the checkout** (method holds) | `evidence.txt` §4; `locate/ci.sh` |
| F2 | **MUST** | §3, Answer 2, §9: "every tick's sensors, activations and ctrl", "10/10 tick streams" | **does not hold as evidence**; the state claim holds | `perturb_sweep.txt`, `evidence.txt` §1, §4; `check.py` |
| F3 | **MUST** | §7, Answer 5, §6 A, §8: a champion played in the page "is the same bout the run scored"; "deterministic replay" | **does not hold** under today's pipeline | `rederive.txt`, `faithful.txt` A |
| F4 | SHOULD | Answer 1, §1, §9 erratum: "three independent sources … fixing any one leaves the other two" | **partly holds**: two causes shown, three layers | §1 + §4 of REPORT, `rederive.txt` |
| F5 | SHOULD | §1 mechanisms: macOS `np.tanh` differs; "math.* and np.* alike"; tick-0 activations "within 1 ULP" | **partly holds** | `evidence.txt` §3, `faithful.txt` A |
| F6 | SHOULD | §5, Answer 3, §8: arena bout scaled to DESIGN §11.2's arm-season; "Python share if anything larger"; "~4× cheaper" | **partly holds**: wrong direction for the ecology | `bench_adv.txt` §2 |
| F7 | NOTE | Answer 3: "WASM physics 1.43× native"; "whole bout in WASM ×0.23"; "Python driving WASM ~1.08×" | holds as arithmetic; framing loose | `bench_rerun.txt` |
| F8 | SHOULD | §1: "Is the macOS runner the laptop? Nearly … a close proxy" | **does not hold**: they are shown to differ | `evidence.txt` §2 |
| F9 | SHOULD | §8 "WASM fixes both by construction"; Answer 2 "WASM fixes it for the bout" | **partly holds**: untested where WASM is nondeterministic by spec | disassembly (`f64.copysign` ×14) |
| F10 | NOTE | §2 and `build.sh`: "`mjUSEPLATFORMSIMD` is never defined under Emscripten" | **false; outcome holds** for another reason | `/opt/rbt133-wasm/build-wasm/build.ninja` |
| F11 | NOTE | §2: the C port reproduces the Python bout to ULP level | **holds**, strengthened; four off-path differences | `faithful.txt`, `semcheck.txt` |
| F12 | NOTE | §3: "Is the test able to see a difference? Yes" | **holds for physics**; not for the brain (F2) | `perturb.txt` |
| F13 | SHOULD | §6: effort figures; A is "~2–4 days" | **overstated scope**: estimates, arena-only | `simulation.py`, `ecology.py` |
| F14 | NOTE | Answer 5, §7: "the same module runs in Chromium"; playback "a few dozen lines"; "not a further research question" | **partly holds** | `web/build_web.sh` |
| F15 | SHOULD | §2 "reproduces byte for byte on a fresh CI runner"; §4 native-control table | **rests on job logs**, not committed outputs | `ci-run-37158742068/`, `ci-run-37159296036-native.txt` |

### F1. §1's isolation evidence is in no committed file. **MUST.**

The table's key cells say that arm64's MuJoCo differs from x86's at the first open-loop step from x86's own model and
state, and that arm64's brain differs from x86's at tick 1 by 1 ULP on x86's own sensor readings. This is the
localisation the whole readout rests on, and it is the probe's purpose. The report cites
`ci-run-37157969294/compare.txt`. That file holds only `probe.py compare` output (closed loop). No committed file
contains `replay-physics` or `replay-brain` output (`evidence.txt` §4). `ci.sh` redirects `numpy-probe` and `gen0` into
`$OUT` but prints the three per-bout probes to stdout only, so they live in GitHub job logs, which expire. The Intel↔AMD
"3,000/3,000 steps" is in the same position. (The AMD closed loop is committed and identical at every tick, so that
cell is supported anyway.)

The method itself holds: same-platform replays are exact here (`rederive.txt`). Brain weights are not recomputed on
the platform. Tick 0 must agree because `W @ 0 = 0` and `np.tanh` is portable (F5). So a first difference at tick 1 is
what BLAS-only divergence predicts.

**Fix.** `tee` the `compare`, `replay-physics` and `replay-brain` output in `ci.sh` into `$OUT/<bout>.txt`, re-run
the locate job, and commit the three platforms' files. Until then, mark these cells "CI log, not committed".

### F2. The fingerprint does not measure ticks, and it is blind to most of the holistic brain. **MUST.**

- **What is hashed.** `check.py` hashes `states.bin` and prints `result.txt`. Its FNV digest is also over state rows
  only. `ticks.bin` is written and never hashed or compared in any committed file: `wasm-fingerprints.txt` has no tick
  line, and neither does `chromium-result.txt`. "10/10 tick streams" has no committed instrument behind it.
- **Positive control on the brain** (`perturb_sweep.txt`). Each non-zero W entry was raised by +1 ULP, one at a time,
  and the bout re-run:

  | robot | entries whose change moves the state fingerprint | entries whose change moves `ticks.bin` |
  |---|---|---|
  | holistic robot 0 (the only actuated one) | 18/40 | 35/40 |
  | holistic robot 1 | 0/5 | 5/5 |
  | conventional robots | 131/150 and 144/150 | |

- **Why the holistic bout is so blind.**
  - Holistic robot 1 drives **no actuator**. Its brain and sensors cannot reach the physics at all.
  - 62% of the holistic bout's ctrl entries sit at the ±1 clip, and actuator 0 is constant (`evidence.txt` §1).
- **What never reaches any state stream** (`evidence.txt` §1):
  - the oscillator sensor (only on holistic robot 1), `abs` and `relu` (also only there);
  - `sin`, `sign` and `integrate` (in no bout);
  - `height` and `joint_angle` (in no bout).

So for the brain, the cross-platform identity is tested by the conventional bout and about half of one holistic robot.
It is not tested "every tick".

**Fix.**
- Add `ticks.bin`'s sha256 to `check.py`'s fingerprint and re-run the five hosts and Chromium. Or drop "every tick's
  sensors, activations and ctrl" and "10/10 tick streams".
- Add at least one bout whose actuated robots use oscillator, `sin`, `integrate` and `joint_angle` (open item 2).

### F3. The browser bout is not the bout the run scored. **MUST.**

§7 says "a champion bout played live in a page is **the same bout** the run scored, not a re-simulation that drifts".
Answer 4 and §8 A sell "deterministic replay" on it. But runs are scored on the Python/pip-wheel path, and the harness
is a faithful port that diverges from that path. §2 says so itself. The divergence starts at the first bout step:
- **First differing state row:** 200 conventional, 208 holistic (`rederive.txt`).
- **Endpoints (conventional):** the opponent ends 79.3 m from the centre in WASM against 127.7 m in the scored Python
  bout. Fitness is 0.993301 against 0.982106. The two runs match at ULP level for about 20 ticks
  (`faithful.txt` A; the distances are from `ref-wasm-x86/` and `locate/ref-x86/*/summary.json`).

What the page replays bit for bit is the **WASM** bout. That bout matches the run's score only if the run was scored in
WASM, which is option B. Under A, the page shows a re-simulation that drifts, exactly as a laptop replay of a cloud
bout drifts today.

**Fix.**
- Restate §7, Answer 5 and §6 A: "portable and self-consistent (every viewer sees the same WASM bout); the same as the
  scored bout only once runs are scored in WASM (B)".
- A champion page under A should show the WASM bout's own fitness, not the run's.

### F4. Two causes, three layers. **SHOULD.**

The model compiler and the step are both MuJoCo's arithmetic as built in each wheel. §1's own corrected mechanism and
§4's control now show it: a no-FMA scalar build agrees across Linux x86 and arm64 on **both** compile and step. The
bout-mode harness compiles the XML itself, and its fingerprints agree. So the evidence is not three independent
sources. It is:
1. **MuJoCo's build** (FMA contraction on aarch64; Apple's libm, and possibly its compiler, on macOS), seen in two layers;
2. **numpy**: BLAS `gemv` (`evidence.txt` §3), plus `np.sin`/`np.cos` on macOS.

"Fixing any one leaves the other two" is wrong for the first two: one build fix clears both. The **sensor layer** was
never isolated, because no probe replays sensors from x86's state. It is untested, not clean. §9 says "the four layers",
§1 says three.

**Fix.** Rephrase Answer 1 and the RBT-96 erratum pointer:
- "two independent causes: MuJoCo's build/libm, seen in compile and step; numpy's BLAS/libm, seen in the brain";
- "the sensor layer is not isolated".

### F5. Mechanism text against the committed probe. **SHOULD.**

- **`np.tanh` is bit-identical on all three platforms** (`evidence.txt` §3: same hash on x86, linux-arm64 and macOS).
  So "On macOS `np.tanh` and `np.sin` differ" is wrong for `np.tanh`, and §1's "`math.*` and `np.*` alike" is wrong for
  tanh. Only `math.tanh` differs on macOS.
- **Consequences:**
  - The brain's transfer functions are not a cross-platform source on these platforms. `np.tanh` is the only one the
    bouts use. The brain's divergence is BLAS alone, plus `np.sin` on macOS for `sin` units.
  - Open item 3's AVX-512 rationale is weak for tanh: numpy's tanh gives the same bits on ASIMD as on AVX-512.
- **Where numpy does differ on linux-arm64:** `np.exp`, `np.log` and `np.arccos`, while glibc's `math.*` agrees. The
  report says only the latter.
- **Tick-0 activations** differ from Python's by **2** ULP on the conventional bout (unit 15, `tanh(bias)`), not
  "within 1 ULP" (`faithful.txt` A).

### F6. The arm-season extrapolation uses the wrong bout. **SHOULD.**

DESIGN §11.2's 20–25 core-s is an **ecology** arm-season: foraging, groups of 4 (`ecology.py` `group_size`), food
smell. §5 scales a 2-robot arena bout with no food. It then says the foraging bout's Python share is "if anything
larger, so the whole-bout saving is unlikely to shrink".

**Measured** (`bench_adv.txt` §2, RBT-105 `forage-2-b2` config, gen-0 founders, 2 holistic + 2 conventional, 10 group
bouts): `mj_step` is **26%** of a foraging group bout (19–32%), against the arena's 18%. The Python share is smaller,
not larger.

**Rescaled**, as a rough estimate, before the cost of food smell in C:

| option | REPORT (arena) | rescaled (foraging) |
|---|---|---|
| Python driving WASM | +8% | **+11%** |
| whole bout in WASM, cost ratio | ×0.23 | about 0.26 × 1.29 (WASM bout ÷ wheel `mj_step`, arena) ≈ **×0.33** |
| whole bout in WASM, per arm-season | 4.6–5.8 core-s | about **6.7–8.4 core-s** |
| §8's saving | "~4× cheaper" | about **3×** |

The direction of the recommendation is unchanged.

**Fix.** State the arm-season figures as an arena-bout proxy, or replace them with a foraging group bout. Delete
"if anything larger".

### F7. Cost framing. NOTE.

- **"WASM physics is 1.43× native."** This is the whole C bout (compile, settle, sensors, brain) in WASM against the
  native-scalar build, not physics alone. It is close enough, because physics dominates the C bout.
- **The ×0.23 is the port to C, not WASM.** Native C is ×0.16, and the WASM penalty is 1.43×. Answer 3 should say so,
  especially now that §4 proposes a native deterministic build.
- **"Python driving WASM ~1.08×" omits the boundary cost.** It omits the Python↔WASM boundary: 3,200 `mj_step` calls a
  bout, plus per tick every sensor's reads of module memory and `mj_objectVelocity` calls. The bridge is unmeasured
  (open item 4). The figure is a lower bound, for an option §5 already says does not give determinism.

### F8. The M1 is not the laptop. **SHOULD.**

§1 answers "Nearly", and §9 says "3 of 4 gen-0 statistics match". But one statistic **differs**, so the two machines
disagree on at least one holistic bout: that much is established, not merely unproven. The pattern also says more
(`evidence.txt` §2):
- `h_best` differs by 0.0097, while `h_mean` agrees to 6 digits.
- If only the `h_best` bout differed, the mean would move by ≥ 0.000486. So at least two bouts differ, with deltas
  that cancel to below 1e-6.
- RBT-85 predates `platform.json` (RBT-127). The laptop's numpy and MuJoCo versions are unrecorded, so the M1/M4
  difference may be software rather than silicon.

**Fix.** Say "the M1 runner is not the M4 laptop as run for RBT-85 (≥ 2 holistic bouts differ; software versions
unrecorded)". Open item 1 stands, and is more necessary than §1 implies.

### F9. "By construction" skips WASM's one nondeterminism. **SHOULD.**

WASM leaves the sign and payload of a NaN produced by arithmetic nondeterministic. x86 and arm64 hardware produce
default NaNs with different sign bits, and V8 does not canonicalise them. This module can observe them:
- it writes raw bits to `states.bin`;
- it contains `f64.copysign` ×14 and `i64.reinterpret_f64` ×62 (disassembly in `/opt/rbt133-wasm/rbt_wasm.wat`).

The only place NaNs arise is an exploding body: `qpos`/`qvel` non-finite, or MuJoCo's own bad-state reset. Neither
pinned bout explodes (`exploded 0`, both robots). The fingerprint could then differ spuriously, or the trajectory could
differ for real if a NaN's sign is consumed. Untested either way.

**Fix.** Make an exploding bout a precondition of "fixes it for the bout" (it is already in open item 2), and soften
§8's "by construction".

### F10. The SIMD guard is not what the build says. NOTE.

`build.sh` (l.16–17) and §2 say `mjUSEPLATFORMSIMD` "is never defined for Emscripten". In this container's WASM build it
is defined: `-DmjUSEPLATFORMSIMD` appears 73 times in `build-wasm/build.ninja`. The WASM `cmake` line does not pass
`-DMUJOCO_ENABLE_AVX_INTRINSICS=OFF`, which the native line does.

MuJoCo still takes its scalar paths, because its AVX code needs `__AVX__` too (`engine_util_blas_avx.h` l.19,
`engine_support.c` l.38), and Emscripten without `-mavx` does not define it. The disassembly check (0 SIMD
instructions) is the real guarantee, and it holds.

**Fix.** Correct the comment and the report, and pass the flag explicitly.

### F11. The port is faithful; the residual differences are off the reachable path. NOTE.

Holds (see "re-derived" above). `semcheck.txt` also checks all seven transfer functions on random recurrent brains:
- Gaps stay at ULP level except in one chaotic network. There, a numpy brain with left-to-right sums parts from numpy's
  own BLAS run at step 22, against the harness's step 23: chaos, not semantics.

Differences found, none reachable in today's bouts:
1. `relu(NaN)` is 0 in C and NaN in numpy. NaN never reaches a brain: the explosion check stops a robot first.
2. `sign(-0.0)` is −0.0 in C and +0.0 in numpy. Harmless to `W a`, but visible in `ticks.bin` bytes.
3. An effector with ≥ 8 units is summed left to right in C and pairwise in numpy (`.sum()`). This is ULP-level.
4. `pack.py` refuses food, waypoints, `settle_until_rest` and `opponent_proxy`, but **not `score`**. A
   `time_at_target` or `closeness` arena config would pack silently, and the harness would score it with
   `zero_sum_fitness`. Add `cfg.score != "distance"` to the refusal before A generalises `pack.py`.

### F12. The positive control covers physics, not the brain. NOTE.

Holds for physics (F2 covers the brain). One trap is worth recording: a +1 ULP change to a ctrl entry already at the
±1 clip is invisible (`perturb.txt`, holistic tick 100), because MuJoCo clamps ctrl.

### F13. §6's scope and effort. **SHOULD.**

- **A ("~2–4 days") covers only arena champions.** The programme's live champions are ecology foragers (RBT-90
  onwards) whose brains read food smell. Replaying or showcasing one needs B's food world:
  - `_intensity` and the contrast baseline;
  - eating and regrowth;
  - the food RNG.

  "Add the foraging items as static geoms" does not reproduce a forager's behaviour.
- **The figures are estimates, none measured:** 2–4 days, 2–3 weeks, ~1 week, and "1,000 lines → ~1,500 of C". Label
  them as such.
- **§8's "the port pays for itself over any sweep the size of RBT-129" needs two qualifications:**
  - the same section rules out using it under RBT-129;
  - its saving is F6's ~3×, not ~4×.

### F14. The browser build is a separate binary. NOTE.

`build_web.sh` relinks the harness: `-sENVIRONMENT=web`, a preloaded FS, and no `-ffile-prefix-map`. It runs no
disassembly check and records no sha256. It was run in Chromium on x86 only. The bytes match, which is the important
part, but Answer 5's "the same module" should read "the same harness and library, relinked".

Two §7 statements are expectations, not results:
- "live playback is a few dozen lines";
- "a direct consequence, not a further research question".

### F15. Build reproducibility and the native control rest on job logs. **SHOULD.**

- The "REPRODUCED" check never fails the job, and its output is in the log only. `ci-run-37158742068/` holds the
  fingerprints, not the CI build's `BUILD.txt`.
- `ci-run-37159296036-native.txt` is a hand summary of two runs' logs ("job logs").
- Answer 3 compresses §4's "Apple's libm and its compiler" to "through its libm". The compiler (Apple clang 17 against
  clang 18) was not separated.

**Fix.** Commit the CI `BUILD.txt` and the native runs' `fingerprint.txt` files.

## The three corrections that matter most

1. **Commit the evidence §1 stands on (F1, F15).** Tee `replay-physics`, `replay-brain` and `compare` into the CI
   artifact, re-run the locate job, and commit it. Do the same for the CI build's `BUILD.txt` and the native-control
   fingerprints.
2. **Either measure the ticks or stop claiming them (F2).** Add `ticks.bin` to the fingerprint and re-run the five
   hosts and Chromium. Add a bout whose *actuated* robots use oscillator, `sin`, `integrate` and `joint_angle`, and
   whose ctrl is not mostly clipped, so that the brain's cross-platform identity is actually under test. Until then,
   the claim is "the physics state stream".
3. **Retract "the same bout the run scored" (F3), and fix the numbers that feed the recommendation (F4, F6).** The
   WASM page replays a re-simulation of the scored bout, which matches the run only under B. "Three independent
   sources" is two causes in three layers. The arm-season saving, measured on a foraging group bout, is about ×0.33
   (≈ 3×), not ×0.23, and the Python share is smaller there, not larger.
