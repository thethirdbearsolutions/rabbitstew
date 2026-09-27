# RBT-116 design adversary: re-read of revision 5 (PR #400 @ `8ad0162`)

**Verdict: REGISTER AFTER FIXES.**
- r5 closes 6 of the 9 MUST items, and partly closes the other 3. The answers are real: the veto, T, crossover,
  the named transform, G7's intermediates and the crossing requirement are all fixed as asked.
- Two fixes remain before registration (R5-1 and R5-2). They are text and `power.py` edits, not redesign:
  - **R5-1:** G4 caps the *confirmed* false-positive rate at 0.05, but `power.py` squares EPS again. With the
    rate read at that cap, a U/N gap reopens false HOLISTIC to 0.63.
  - **R5-2:** there is no positive control for the one-nose route. That route is the only basis for "a NEITHER here
    is the *stronger* no", and at plausible one-nose sensitivities a real bypass reads NEITHER 0.74–0.94.

*Probes:*
- `r5_probe.py` / `.txt`: r5's call (trajectory veto and a 16-draw confirmation battery) under r5's named transform
  (§4.2: tanh(2.5 (ln Σ − b)), with b an EMA of the robot's mean ln Σ at τ = 1 s), in the same PW caricature as
  `steer_probe.py`. There are 25 genomes per body, each called on two independent batteries.
- `r5_attack.py` / `.txt`: r5's own `unit()` and `verdict()`, imported unchanged, with only the inputs moved.
- Nothing in `rabbitstew/` was changed.

## The MUST items

| # | item | status | note |
|---|---|---|---|
| 1 | count veto; unscreened draws | **CLOSED** | Trajectory-identity veto, and a 64-draw pool with a reachability screen. `r5_probe.txt`: the two-nose steerer (k 6) passes one call on 0.64 of genomes and is **confirmed on 0.48**. On r3's call it was called STEERS on 0.27, and a real steerer can now no longer be vetoed for tying on food. Blind is NONE. |
| 2 | T undefined, absolute threshold | **CLOSED** | 0.25 × the member's median speed, with the same bar used for the decoy season. T := 0 and a flag when no tick qualifies. The excluded share is reported. |
| 3 | G8(b) cannot fail on T; the orthokinesis claim | **PARTLY** | The claim is withdrawn and T ≈ net approach ÷ path is stated. G8(b) now pays, or declares T untested. **But** see R5-3: under r5's contrast-only transform, a plant keyed on the *signed* reading is itself chemotaxis by r5's own SHOULD 3 ruling. In the caricature no area-restricted-search plant, signed or sign-blind, reaches F > 0 (`r5_probe.txt`: F −0.33 to 0). So expect the "untested but unneeded" branch, which is honest as worded. |
| 4 | holding: inequality, crossover, Q, covariate | **CLOSED** | Crossover is 0 in B, U and N. The rule is (1 + s)(1 − u) ≥ 1.25. Q is derived (part 1 transcribes `hold.py`). The loss-ratio sentence is registered. Two notes (SHOULD R5-6, R5-7): crossover 0 changes the holistic "default operator"; and u_f measured on *hand-built* plants may not be the loss rate of evolved steerers. |
| 5 | transform unnamed | **CLOSED** | Named, with the lean stated and no C-model number cited. **The consequence it draws, "a NEITHER under it is the stronger no", is not yet earned** (R5-2). |
| 6 | G7: one intermediate only | **CLOSED** | Pirouette, lone-nose throttle, same-sign pair and one wheel, in both signs, at 16 × 16 with a paired t bound and printed power. |
| 7 | U/N false-positive gap | **PARTLY** | Confirmation and I8 are added. **But** the power model sets the confirmed rate to EPS², while G4 measures and caps the *confirmed* rate at 0.05. If false passes are genome-persistent (a body that passes once tends to pass again), the confirmed rate is EPS × P(repeat), not EPS². See R5-1. |
| 8 | HOLISTIC without crossing | **CLOSED** | The A test and an exact one-sided McNemar test on discordant units. An A-only result is "INCONCLUSIVE: holistic steers more". |
| 9 | the power re-run | **PARTLY** | Done, at M = 40 with the derived Q and the one-seed row. It inherits R5-1 (squared EPS) and R5-2 (SENS 0.63 is the *two-nose* steerer's), and is priced only at D = 16's plateaus. |

**The SHOULD items:** all 11 are taken in, and SHOULD 4, upgraded to MUST, is done: the burn-in with lesioned smell
is sound, and under the running baseline a lesioned nose reads exactly 0, so its wiring is neutral. SHOULD 3 is
answered by ruling that biased-random-walk chemotaxis is STEERS. That is acceptable, and it is what creates R5-3.

## New and remaining items

### R5-1 (MUST): define EPS as the confirmed rate, cap it where the null survives, and stop squaring it

`r5_attack.txt` uses r5's `verdict()`. Pioneer at 0.02 per call, as registered. The confirmed rates are fed in
directly:

| null scenario (holistic U / N confirmed false-STEERS rate) | HOLISTIC | NEITHER | INCONCL: H steers more |
|---|---|---|---|
| r5 as registered (0.02 per call, squared: 0.0004 / 0.0004) | 0.003 | 0.893 | 0.000 |
| genome-persistent passes, 0.04 / 0.01 per call with P(repeat \| pass) = 0.5: 0.02 / 0.005 | 0.020 | 0.717 | 0.183 |
| **G4's cap read as the confirmed rate: 0.05 / 0.01** | **0.630** | 0.017 | 0.340 |
| 0.05 / 0.05 (high, but no gap) | 0.003 | 0.387 | 0.013 |

- The crossing count (≥ 3 of 40, and ≥ 3 above N) is exactly what a 0.05 confirmed rate reaches by chance. It
  expects 2 of 40, with P(≥ 3) ≈ 0.32 per line.
- **Fix:**
  - G4 reports the **confirmed** false-STEERS rate per fauna, on burn-in finals, and gates it at **≤ 0.005**
    (confirmed; 64 members give 0 of 64 as the only passing count unless G4 is enlarged to about 600 members; the
    alternative is to raise CROSS_K until the null row stays ≤ 0.01 at the measured rate).
  - `power.py` takes EPS_C (and SENS_C) as **measured confirmed rates**, with no squaring. It is re-run with the gap
    at G4's cap as a registered row.
  - I8 compares share_N against the same confirmed EPS_0.

### R5-2 (MUST): a positive control for the one-nose route, and route-specific sensitivity

r5 argues that its transform favours one-nosed (mostly holistic) bodies, and registers that "a NEITHER verdict
under it is the *stronger* no". That claim needs the call to see one-nose steering. Nothing in G8 tests it:
- (a) is the Pioneer compass;
- (c) is a two-nose holistic plant;
- `power.py`'s SENS 0.63 is the two-nose steerer's.

`r5_probe.txt`, under r5's transform and call, one nose at the root, run-and-tumble on the temporal contrast:

| body | F | one call passes | confirmed STEERS |
|---|---|---|---|
| steer1 k 2 | +0.12 | 0.04 | 0.00 |
| steer1 k 8 | +0.14 | 0.08 | 0.00 |
| steer1 k 32 | +0.56 | 0.52 | 0.32 |
| (steer2 k 6, two noses, for reference) | +1.20 | 0.64 | 0.48 |

`r5_attack.txt`, a real bypass at Q_H 0.70 through r5's verdict, at one-nose sensitivities:

| single-call SENS | expected confirmed steerers of 40 at Q 0.70 | p_H 0.5: HOLISTIC / NEITHER |
|---|---|---|
| 0.63 (r5's) | 11.1 | 0.947 / 0.000 |
| 0.35 | 3.4 | 0.527 / 0.020 |
| **0.20** | **1.1** | **0.000 / 0.883** |
| 0.10 | 0.3 | 0.000 / 0.943 |

At p_H 0.75 and SENS 0.20, HOLISTIC is 0.010 and NEITHER 0.737.

**Fix:**
- Add **G8(f):** a one-nose temporal plant on every holistic host. One food sensor on the host's most-moving
  expressed Part, then a global unit on the reading, then a turn command ±w, with w ∈ {4, 16, 64}, best by F on the
  screening draws. Its confirmed share is SENS_1 at the gate.
- Run `power.py` at **min(SENS_c, SENS_1)** for the holistic fauna.
- **"The stronger no" is registered only if G8(f) fires** at a share that gives a p_H 0.5 bypass ≥ 0.8 detection.
  Otherwise the NEITHER sentence says: "steering through a lone nose was below the instrument's confirmed
  sensitivity (…)".
- This matters most for the one-nose steering that PW actually pays: in the caricature, one-nose run-and-tumble
  earns only F 0.12–0.14 at moderate gains, below F_MIN, so it is excluded by F_MIN rather than missed by noise.
  State that too.

### R5-3 (SHOULD): G8(b) must be sign-blind under this transform

Under r5's §4.2, every nose reads a contrast: approach is positive and retreat is negative. So G8(b)'s "slow and
turn more above a threshold" on the **signed** reading is run-and-tumble chemotaxis. By r5's own SHOULD 3 ruling,
that counts as STEERS, and a "0 STEERS" requirement could then fail against a legitimate call. **Key the plant on
|reading|.** That is undirected kinesis under this transform. In the caricature neither version pays (F ≤ 0), so this
changes the text, not the expected outcome.

### R5-4 (SHOULD): G8(a)'s 50% confirmed bar is close to a working instrument's rate

The caricature's two-nose steerer at k 6 is confirmed on 0.48, and at k 32 on 0.60. A 50% pooled bar can fail a
working instrument by chance.
- Either set the bar from a stated fraction of G1's hosts that PASS on stage 2 (for example ≥ 0.6 × their confirmed
  share),
- or plant at the strongest paying rung and report the first paying rung separately.

### R5-5 (SHOULD, for the ruling): cost

About 420 CPU-h per world point at D = 16, so about 850–1,300 CPU-h for 2–3 sweep points. `--draws-final 16` over
D = 4 (about 45% of the cost, §9) should be built and tested at G6 before committing D = 16 at every point.

### R5-6 (SHOULD): the operator sentence

Crossover 0 is the right call, but the holistic search now runs *without* crossover, which was part of its default
operator. The headline's operator sentence should read "mutation-only operators (crossover off in both faunas)"
rather than "each body's default operator".

### R5-7 (SHOULD): measure u_f on evolved steerers too

G6's u_f comes from children of hand-built plants (G8(a) and (c)). Evolved steerers may be more or less robust to
mutation. The assay's loss rate on U's own STEERS members (§5.2) is the evolved u. Print it beside G6's, and, if the
two differ by more than 2×, re-run `power.py` part 1 at the evolved value before the readout's `power.txt` is final.

## What r5 got right that should stay

The trajectory veto; the draw screen; the relative T bar; crossover at 0; the (1 + s)(1 − u) ≥ 1.25 rule with derived
plateaus; the named transform with its lean stated; G7's full intermediate table; confirmation; the McNemar crossing
requirement; the burn-in; I8; the world-point block (no pooling, a gate per point); and r4's planted negatives (d) and
(e).

## Files

| file | what | runtime |
|---|---|---|
| `r5_probe.py` / `.txt` | r5's call under r5's transform, in the PW caricature: 10 bodies × 25 genomes × 2 batteries | about 8 min |
| `r5_attack.py` / `.txt` | r5's `verdict()` / `unit()` with confirmed EPS and one-nose SENS | about 2 min |
