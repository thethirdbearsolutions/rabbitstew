# RBT-113 / RBT-117 readout adversary

*Reviews PR #393 (`results/RBT-113-readout` @ `3889723`, from integration `b1f7690`). Branch
`results/RBT-113-readout-adversary`, cut from the PR head. The probes are the scripts beside this file, and their
outputs are the `.txt` files. Platform: x86_64, mujoco 3.14.0, numpy 2.4.6, a clean `.[dev]` venv with no scipy.*

## Calls

| | call |
|---|---|
| **RBT-113** | **CONFIRMED-WITH-CAVEATS.** Every number and verdict reproduces, and the verdicts follow the registered rules. The holistic D line's work is real actuation, not numerical pathology. It is bought, however, through a motor-capacity rule that the mass budget does not cap (§3). The holistic U line's food gain is real, but it is coverage, not smell-guided foraging (§4). REPORT.md's wording must change in four places (M2–M4, S1). |
| **RBT-117** | **CONFIRMED-WITH-CAVEATS.** HOLISTIC RESPONDS MORE is the correct output of the registered rule on correct inputs, and the test's level and control are intact. But the whole margin is the holistic D line's larger motor capacity: the up half is a tie (p 0.53), food alone favours the designed body (p 0.01), and capping the holistic D line's work at the designed D line's removes the margin (d −0.02, p 0.86). This belongs to the follow-up paper's class of results: a body-model allowance that only the evolving body can use. The verdict must not be quoted without that sentence (M1). |

---

## 1. Reproducibility

- **Restore:** all 8 `ckpt/rbt-113-*` branches restored at 216/216, and `git diff --quiet -- runs/RBT-113` succeeds
  afterwards (`RESTORE_CLEAN`).
- **Regeneration** (RUNNER §6 commands, 4 workers): **all byte-identical** (`repro.txt`): `decompose.txt`, all 24 `decompose.json` (rewritten in place; `git diff` empty), `readout.txt`, `sigma0_reference.json` and `runs/RBT-117/compare.txt` (exit 0). Decompose took 48.5 min on 4 cores, run alongside the probes.
- **No scored code changed since registration.**
  - The `rabbitstew/` tree is `5dbfbcd373ca` at `ec5f822` and at `3889723`.
  - `git diff ec5f822 3889723` and `git diff ea27eac 3889723` over `rabbitstew/`, `runs/RBT-113/*.py` and `*.sh` are
    empty. The only differences in those paths are the RBT-117 files, which were added later.
  - `git diff ca75e2c 3889723` and `git diff ec60adb 3889723` over `runs/RBT-117/` add only `compare.txt`, plus the
    design-adversary files in the ca75e2c case. `compare.py`, `power.py` and PREREGISTRATION.md are unchanged.
- **Suite:** **398 passed** (229.8 s) in a fresh `.[dev]` venv with no scipy (`ModuleNotFoundError: scipy` confirmed).

## 2. The verdicts follow the registered rules, re-derived independently

`rederive.py` recomputes everything from `lineage.jsonl` and `decompose.json` with its own code. It imports neither
`readout.py` nor `compare.py`, and it computes sign-flip p exactly over all 4096 patterns. Output: `rederive.txt`.

- **RESPONDS (×3).** Each CI lies above 0 and p < 0.05:
  - holistic b_div raw +0.0951 [+0.0830, +0.1072], p 0.0005;
  - designed default +0.0375 [+0.0270, +0.0481];
  - designed Z +0.0365 [+0.0278, +0.0452].

  The h2 values are 0.0930, 0.0672 and 0.0662. All match `readout.txt` to the printed digits.
- **NO CHANGE.** Z − default b_div in σ0 is −0.0014 [−0.0120, +0.0092], inside ±0.05. This matches.
- **σ0:** holistic 0.221249 and designed 0.754487, the same as `sigma0_reference.json`.
- **No VOID.** `readout.txt` shows all 24 per-directory controls and the operator pairing passing. I did not
  re-implement the controls; the regenerated `readout.txt` re-runs them (§1).
- **RBT-117.**
  - d is +0.7685 [+0.4042, +1.1327], with exact p 0.0015 and 11 of 12 seeds positive.
  - c is +0.1574 [−0.0161, +0.3309], p 0.0728, and |c| = 0.157 is below `C_BOUND = 0.8`. No VOID; either condition
    alone would prevent it.
  - Leave-one-seed-out mean d ranges from +0.687 to +0.862.
  - The seed-set checks passed in `compare.py` (12 seeds, 1..12, each under its assigned O arm). The regenerated
    `compare.txt` exits 0.

## 3. Is the holistic D line's work real? (the priority check)

**Numerically, yes.** `probe_work.py` replays 3 random members of every line in every seed directory (576 replays,
both faunas) on decompose's first fixed draw. It instruments every physics substep (output: `probe_work.txt`).

| holistic D line (n = 72) | value | reading |
|---|---|---|
| work at dt/2 and dt/4, same control interval | ratio **1.000** (median), range 0.60–1.04 | converged: genuine integrated work, not integrator chatter |
| share of \|F·v\| from torque motors | 0.94 | no servo pathology (position and velocity servos: 0.03) |
| share of \|F·v\| that is negative (braking) | 0.04 | the motors drive, they do not fight themselves |
| share done in substeps where joint velocity changed sign | 0.02 | no 200 Hz jitter |
| share done with the torque command saturated (\|ctrl\| > 0.98) | 0.60 | full-throttle driving |
| max body speed | median 6.2, max 21 m/s (explosion at 200) | no near-explosions |
| exploded seasons, MuJoCo bad-QACC warnings | 0 / 72, 0 | |
| deepest contact penetration | 66 mm | smaller than the founders' (164 mm) |
| work / full-throttle free-spin ceiling | median 0.85 | the line has pushed its motors to near capacity |

Each replay's work matches `run_group`'s registered value exactly (1.00 in every group). `work_cost` is computed by
one code path for both faunas: `simulation.py:318` accumulates `|actuator_force × actuator_velocity| × dt` over
every substep, and `food_score` subtracts `0.03 × J/1000`. An exploded season books 0 of food and work, so explosion
cannot help a down line.

**What it is physically.** The D line's members hold their torque motors at full throttle. Each joint spins against
its damper, which `world.py:203` makes "the motor's speed limit": terminal speed is gear/damping = 20 rad/s, and the
power burnt is gear²/damping.

**Where the capacity comes from: a motor budget that the mass budget does not cap.** `probe_gear.py` covers every
member of every line (`probe_gear.txt`).

| | Σ torque-motor gear | Σ gear / (4 × mass) | share on ball-joint DOFs | free-spin work ceiling (yield) |
|---|---|---|---|---|
| holistic founders | 22 | 0.36 | 0.68 | 0.20 |
| holistic U | 55 | 0.90 | 0.86 | 0.50 |
| **holistic D** | **221** [87, 323] | **3.66** [1.56, 5.29] | **0.98** | **1.98** [0.78, 2.91] |
| holistic C | 18 | 0.29 | 0.67 | 0.16 |
| designed (every line) | 108 (fixed) | 1.76 | 0 | **0.97** (fixed) |

- `world.py:202` sets each driven DOF's gear to 4 × the **larger** of the two masses its joint connects. A ball
  joint carries up to three such motors (`world.py:217–223`).
- The mass budget (15.34 kg) caps mass, not gear. A heavy part carrying several driven ball joints therefore counts
  its mass once per driven DOF.
- The holistic D line found this lever. Its Σgear is 10× the founders' and 3.7× its own mass-keyed value, and 98% of
  it is on ball joints. Its work ceiling is twice the designed body's.
- The designed body cannot move its ceiling. Its D line already sits at 0.926 yield of work against a ceiling of
  0.97 (95%), with SD about 0.005.

**Verdict on item 3.** This is not a numerical artefact of the spawn-drop or jitter kind. It *is* an artefact of the
follow-up paper's first kind: a weight-class mismatch has become a **motor-class mismatch**. The simulator's body
model grants actuation capacity that the budget meant to equalise the bodies does not bound. Only the evolving body
can grow into it, and selection for waste found it at every seed.

**Consequences.**
- **RBT-113 holistic headline.** b_div (+0.095) and b_down (+0.062 raw, about twice b_up) are real responses of this
  simulator, but a large part of their size measures how far the gear rule lets a body scale its motors. D1 already
  shows the down response is 93% work. The report should name the mechanism (M3).
- **RBT-117** (not registered, descriptive; `rederive.txt`):

  | | holistic − designed | p |
  |---|---|---|
  | up half, final U − C | +0.107 [−0.198, +0.412] | 0.53 (7/12) |
  | down half, final C − D | +0.662 [+0.309, +1.015] | 0.0024 |
  | U − D in food alone | −0.419 [−0.727, −0.112] | 0.010 (designed larger) |
  | U − D in net on decompose's draws | +0.647 [+0.412, +0.882] | 0.0005 |
  | net U − D with the holistic D line's work capped at the designed D line's | −0.022 [−0.298, +0.254] | 0.86 |

  The registered verdict stands as the registered rule's output. But its entire content is the motor-class
  mismatch: remove the holistic D line's excess work and the comparison is NOT DECIDED.

## 4. Is the holistic U line's food gain real?

**The food gain is real, it comes from moving over more ground, and it does not use smell.** `probe_food.py` replays
3 random members of every U line and of the founders, both faunas, on all 4 fixed draws, under three conditions
(`probe_food.txt`):

| holistic | intact | blind (food sensors read 0) | decoy (food sensors smell a mirrored layout) | ground covered (0.35 m cells) | items / 100 cells |
|---|---|---|---|---|---|
| founders | 0.111 | 0.111 | 0.111 | 5 | 2.15 |
| **U line** | **0.854** | **0.913** | **0.934** | **29** | 2.94 |
| designed founders | 0.840 | 0.764 | 0.806 | 40 | 2.12 |
| designed U | 1.316 | 1.153 | 1.295 | 51 | 2.60 |

- **The holistic U line eats because it moves.**
  - Only 39% of sampled U-line members carry any food sensor.
  - Removing or scrambling smell does not reduce intake: intact exceeds decoy in 3% of members, and decoy exceeds
    intact in 8%.
  - Ground covered rises about 6×, while items per cell rise only about 1.4×. `readout.txt`'s correlated response in
    distance (+0.241 founder SD per generation) says the same.
  - The designed body barely uses smell either (intact − decoy +0.02).
- **No scoring loophole was found.** Eating is any geom within 0.35 m (xy) of an item (`simulation.py:466`), eaten
  items regrow at fresh random spots, and every intact replay equals `run_group`'s registered food.
- **The D1 method is as registered.**
  - The 4 draws `(1131, 2131)…(1134, 2134)` are fixed in `decompose.py`.
  - Food share is |Δfood| / (|Δfood| + |Δwork|) on the unit means, per §11.1.
  - Generation 23 is checked by name prefix and count.
  - Founders are regenerated and checked against the lineage.
  - Ratios re-derived: U/founders food 10.6×; D/founders work **45.9×** (D/C 52.4×).
  - Holistic U food exceeds the founders' and C's at 12 of 12 seeds.

## 5. Why RBT-117's prediction (d ≈ −2.8) was so wrong

Both legs of the power model failed, in opposite directions:

| | model E[D] (raw) | observed mean D |
|---|---|---|
| designed | +3.1 to +5.0 | **+1.48** |
| holistic | +0.12 to +1.34 | **+2.25** |

1. **The designed body's response is bounded; the model's is not.** `power.py` runs an infinitesimal Gaussian model
   at the pilot's h2 0.43 and SD 0.709, with no floor or ceiling. In the data:
   - the designed D line hits a floor: food 0.06 and work at 95% of a fixed motor ceiling, so net −0.86 against a
     floor of about −0.97;
   - realised h2 is 0.067, not 0.43.

   The model's E[D_des] of 3.1–5.0 exceeds anything this body can reach: about 1.2 up (U food) plus 0.97 down is
   about 2.2.
2. **The holistic fauna escaped its founder scale in both directions.**
   - The model scaled the holistic response by the zero-inflated founder SD (0.136).
   - The D line created new variance by growing motor capacity (§3), with a work ceiling that rose 10×.
   - The U line started eating by moving.
   - §2 of the registration named the second of these ("discovering eating") as a live escape. It did not foresee
     the first, and the first is the one that carries the margin.
3. **Validity.**
   - **The level holds.** The null is symmetry of d; the C-line control is unaffected (c +0.16, p 0.07); and the
     observed per-seed SD of d (about 0.57) is below the modelled 0.79–0.88.
   - **The control's bar is unaffected.** It is fixed at 0.8, independent of the model's means.
   - **Only the prediction failed, and the construct.** The raw U − D difference turned out to measure mainly the
     difference in the two bodies' **floors**. SCOPE_3 anticipated this ("the down line's room to lose yield by
     working harder"); the registered power model did not quantify it.

## 6. Wording (REPORT.md)

- "learn to eat" / "a real gain in foraging" / "can evolution improve foraging here" (§3, §5): see M2.
- "tenfold": 10.6×, fine. **"fiftyfold": 45.9× from the founders.** Use "about 46-fold", as the coordinator's post
  already does (S2).
- "items per season": each unit is items eaten per 15 s *solo* season, the mean of 4 fixed draws. Say "per 15 s solo
  season" once, so it is not read as an ecology season (N3).
- **"in both directions, on every seed" (§5) is false.**
  - The designed default line at seed 8 has b_up −0.014.
  - The Z designed lines at seeds 8 and 9 have b_up −0.001 and −0.005, and seed Z11's final U − C is −0.011.
  - The holistic Z4 replicate has b_up −0.001 and final U − C −0.018.

  Every *divergence* (b_div) is positive at every unit. The up response is not (M4).
- "food stayed where it was" (holistic D): D food is 0.179 against C's 0.065 and the founders' 0.086; C − D food is
  −0.114 [−0.177, −0.052]. The D line eats about twice as much as the control, a by-product of flailing (N2).
- **RBT-117's reading ("the margin is in the down line, as work; not evidence for reason (b)") is correct but
  incomplete.** It omits that the work is bought by a motor-capacity allowance only the holistic body can use, and
  that removing it removes the margin (M1).
- **SCOPE_4** (registered code, not to change): its closing clause, "a designed win is not by itself evidence against
  the mechanism", is written for the predicted outcome and is inert after a holistic win. Its premise clause still
  applies and matters: because the holistic founders are *less* variable, a holistic win cannot be reason (b)'s
  mechanism. REPORT.md should state that converse explicitly rather than lean on SCOPE_4 (S3).

---

## MUST-FIX (REPORT.md only; no scored file changes)

- **M1. RBT-117 needs its mechanism sentence, beside the verdict wherever it is quoted.** Suggested text: "The margin
  is entirely in the down line. It exists because the holistic body can grow motor capacity that the mass budget does
  not cap: ball-joint gear keyed to the heavier part gives the D line a work ceiling about 2× the designed body's.
  With the holistic D line's work capped at the designed D line's, the difference is −0.02 (p 0.86). In the follow-up
  paper's terms, this is a body-model allowance only the evolving body can use."
  - **Evidence:** `probe_gear.txt`, `probe_work.txt`, `rederive.txt`.
- **M2. Replace "learns to eat" and "a real gain in foraging" with "learns to move, and eats by covering ground".**
  - **Evidence:** blind and decoy eat as much as intact (0.91 and 0.93 against 0.85), 61% of members have no food
    sensor, and ground covered rises 6×.
  - The food gain is real, but it is not evidence that evolution improves smell-guided foraging here. Adjust "Quote
    b_up with its food share when the question is 'can evolution improve foraging here'" to match.
  - **Evidence:** `probe_food.txt`.
- **M3. RBT-113 §3 should name the D line's mechanism.** It is genuine full-throttle actuation, converged under
  timestep refinement, not a numerical artefact. It is bought by growing Σgear 10× through ball joints: 3.7× the
  mass-keyed value against the designed body's fixed 1.76. That is why b_down is about 2× b_up and dominates the
  holistic b_div.
  - **Evidence:** `probe_work.txt`, `probe_gear.txt`.
- **M4. §5's "in both directions, on every seed" is false** (§6 above). Say "diverged at every seed; the up response
  was positive at 11 of 12 designed-default seeds and at every holistic seed (unit mean)".

## SHOULD-FIX

- **S1.** Report the unregistered robustness splits beside RBT-117 as descriptive, labelled not registered: up half
  (p 0.53), food alone (designed larger, p 0.01), work-capped counterfactual (p 0.86).
- **S2.** Change "fiftyfold" to "about 46-fold" (45.9×).
- **S3.** State SCOPE_4's converse in REPORT.md: with the holistic founders the *less* variable (0.229 against
  0.755), a holistic win cannot run through reason (b)'s mechanism. SCOPE_4's closing clause is inert for this
  outcome.
- **S4.** For future benchmarks and the programme: budget motor capacity (for example Σgear ≤ c × mass), or report
  it per line, before holistic-against-designed comparisons in raw yield. Every future raw-yield down line will
  otherwise find this lever. (A note for the ruling; not for this PR.)

## NOTES

- **N1.** Deep contact penetrations appear in several groups: holistic U 271 mm, designed founders 416 mm, designed
  U 573 mm (one exploded member). They appear where there is little work, not in the D lines (66 mm and 32 mm). They
  do not bear on the D-line result but are worth a look for overlapping geoms at build time.
- **N2.** The holistic D line eats about 2× the control (0.179 against 0.065), as a by-product of flailing.
- **N3.** "per season" means per 15 s solo season, the mean of 4 draws.
- **N4.** The low-work groups (founders, C) do not converge under refinement: the ratio ranges 0.13–21 on members
  doing around 1 J. This is immaterial at 0.03 × kJ.
- **N5.** The σ0 table header in `readout.txt` ("in sigma0 units (each directory's own generation-0 SD … in the last
  column)") divides by the pooled σ0, not each directory's own SD. The own SD is only printed. This is cosmetic, in
  registered code, and should not be changed.

## Files

`rederive.py`/`.txt`, `probe_work.py`/`.txt`/`.json`, `probe_gear.py`/`.txt`, `probe_food.py`/`.txt`, and
`repro.txt` (the byte comparison). Every script runs from the repository root. The probes need the arms restored per
RUNNER §6.
