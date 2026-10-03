# RBT-133: author's response to the adversary review

Each finding of `ADVERSARY.md` and what changed. Evidence for the fixes is CI run 37160528583
(`spikes/wasm/ci-run-37160528583/`).

| # | response | where |
|---|---|---|
| F1 MUST | **Fixed.** `locate/ci.sh` tees `compare`, `replay-physics` and `replay-brain` per bout into the artifact; the three platforms' outputs for five bouts are committed, with a per-bout summary. | `ci-run-37160528583/locate/`, `locate-summary.txt`; REPORT §1 |
| F2 MUST | **Fixed.** `check.py` hashes `ticks.bin`; the bank has three more gen-0 bouts whose actuated robots use oscillator, `sin`, `sign`, `integrate`, `relu`, `differentiate`, `height`, `joint_angle`, `joint_velocity`, with 0–6% of ctrl at the clip. All five hosts/runtimes and Chromium: 50/50 state streams and 25/25 tick streams byte-identical. | `bouts.txt`, `check.py`, `ci-run-37160528583/wasm-vs-x86.txt`, `web/chromium-result.txt`; REPORT §3 |
| F3 MUST | **Accepted; retracted.** The page replays the WASM bout; it is the run's scored bout only if runs are scored in WASM (option B). Under today's pipeline it is a re-simulation that drifts. | REPORT Answer 5, §6 A, §7, §8 |
| F4 | **Accepted.** "Two causes seen in three layers" (MuJoCo's build and libm; numpy's BLAS); the sensor layer is stated as not isolated; the erratum pointer is reworded. | REPORT Answer 1, §1, §9 |
| F5 | **Accepted.** `np.tanh` is portable; the brain's arm64 divergence is BLAS alone; linux-arm64 numpy `exp`/`log`/`arccos` differ; tick-0 activations within 2 ULP. | REPORT §1, §2 |
| F6 | **Accepted.** The foraging group bout's 26% physics share and the rescaled +11% / ×0.33 are in §5, marked as an extrapolation; "Python share if anything larger" is withdrawn. | REPORT §5, Answer 3 |
| F7 | **Accepted.** 1.43× is the whole C bout; the saving is credited to the C port. | REPORT §5, Answer 3, §8 |
| F8 | **Accepted.** "Not shown"; the M1 differs from the laptop's record in at least two bouts; open item 1 is the run on the M4. | REPORT §1, §9 |
| F9 | **Accepted, not fixed.** NaN sign bits named as the untested gap; an exploding bout and NaN canonicalisation are open item 6 and part of option B. | REPORT §6 B, §8, §9 |
| F10 | **Fixed** in REPORT §2 and in the `build.sh` comment (the guard is `__AVX__`; the disassembly check is the guarantee). The comment change does not alter the module (same sha256 on CI). | `toolchain/build.sh`; REPORT §2 |
| F11 | **Recorded** as follow-ups for any adoption. | REPORT §2 |
| F12 | **Addressed** with F2 (tick streams, unclipped bouts); the adversary's perturbation results are cited as the instrument check. | REPORT §3 |
| F13 | **Accepted.** A is arena-only (foragers need the food world); every effort figure is labelled an estimate. | REPORT §6, §8 |
| F14 | **Fixed / reworded.** `build_web.sh` records the web module's sha256 and applies the no-SIMD check; the browser is stated as tested on x86 only; playback effort is an expectation. | `web/build_web.sh`; REPORT §7 |
| F15 | **Fixed.** CI `BUILD.txt` and the native-control fingerprint files (uploaded as artifacts) are committed; Apple's compiler vs libm is stated as not separated. | `ci-run-37160528583/BUILD.txt`, `native-vs-x86.txt`; REPORT §4 |
