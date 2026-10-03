# RBT-116 design adversary: the extradimensional-bypass pre-registration (PR #400 @ `62fbc97`, revision 3)

**Verdict: REDESIGN (narrow).** The question, the world family, the start points, the N line and the fairness block
are sound and should be kept. But three parts of the machinery would decide the answer before the bodies do:

1. **The instrument.** The STEERS call cannot see the steering it was built for in PW. The zero-count veto was
   borrowed from a readout where exact ties meant "smell unused". In PW, where eating is sparse, it rejects most
   real steerers.
2. **Holding.** The rule that sets the draws (G6: "s ≥ u") is the wrong inequality, and crossover is left out of
   erosion entirely. At the registered settings, a steerer at F_MIN is essentially never held.
3. **The verdict.** HOLISTIC MORE READILY can fire when no line has crossed, and it can be produced by a U/N
   false-positive gap the design itself anticipates (§10.4).

Each of these is fixable in the text and in cheap code, with no new world and no new starts, so this is not a
start-again. But together they change the power table and the gates, so the fixed version needs a re-read before it
registers. There are 9 MUST items and 11 SHOULD items (§9).

**Against the held revision 4** (`results/RBT-116-design-r4-wip` @ `577ef9e`, read after this review was
written):

| MUST | r4's status |
|---|---|
| 1. count veto | **not addressed**: the veto is unchanged (r4 L216) |
| 2. T | **not addressed** |
| 3. G8(b) | **partly**: G8(b) now reads a live chassis nose under a running baseline, so it is no longer trivially silent. But it still cannot fail on T, because it does not pay (F), and klinokinesis is still classed as steering (r4 L197, L809) |
| 4. holding | **partly**: s > u/(1 − u) is adopted. Crossover is still unpinned, and its loss is still unmeasured (the assay is still "no crossover", r4 L566). Q_f is still asserted |
| 5. smell transform | **mostly**: root-centring is refused, and the requirements in r4 §4.1 are the right ones. It remains to register the chosen transform and to measure every PW number on it |
| 6. G7 intermediates | not addressed |
| 7, 8, 9 | not addressed |

r4's planted negatives (d) and (e) are good, and they close a hole this review would otherwise have raised.

*Everything below is either a caricature (kinematic, `steer_probe.py`, `hold.py`, `power_attack.py`) or a
read-only real-body probe (`steer_real.py`, on RBT-113's O1 U finals from `ckpt/rbt-113-O1`). Nothing in
`rabbitstew/` was changed. The designer's line numbers are to `runs/RBT-116/PREREGISTRATION.md` @ `62fbc97`
("PR L…").*

---

## 1. Can STEERS fail, and can it pass? (R3, R7)

### 1.1 The probe

`steer_probe.py` reproduces PW's layout and rules as auditor C's kinematic model does:
- 2 patches of 0.4 m in a 4 m disc, 0.8 m clearance, regrowth at 60 s, `log`, decay 1.5;
- `random_start` as coded: 1.5–2.5 m out, heading within ±135° of the centre (`simulation.py:585–601`);
- **eating from a root point**, as registered;
- C's realistic regime: v 0.25 m/s, heading noise 1 rad/√s, turn limit 0.5 rad/s, nose gain 10 on the two-nose
  difference.

It runs the registered stage-2 call (16 paired draws, intact against RBT-97's rotated live layout, F, T and ΔT as in
PR L165–204) on 30 genomes per body, each with its own 16 draws. It reports the share of each body called STEERS,
and the same share with the veto removed.

`steer_probe.txt`:

| body | what it is | STEERS | STEERS without the veto | mean F | mean ΔT | draws with food_i = food_d (of 16) |
|---|---|---|---|---|---|---|
| blind | coverage | 0.00 | 0.00 | 0 | 0 | 16.0 |
| ortho a 0.6 / 0.9 / 1.2 | smell slows it (the G8(b) throttle, as a point) | 0.00 | 0.00 | −0.06 to −0.18 | ≈ 0 | 15.2–15.3 |
| klino b 3 / 8 | smell makes it turn more, undirected | 0.00 | 0.00 | −0.08 / −0.05 | ≈ 0 | 15.0–15.6 |
| ARS q 0.5 / 0.6 / 0.7 | area-restricted search (slow and tortuous above a threshold) | 0.00 | 0.00 | −0.27 to −0.34 | −0.04 to −0.06 | 14.5–14.8 |
| orbit | constant arc, with smell-slowed speed | 0.00 | 0.00 | −0.10 | +0.01 | 15.3 |
| sweep | CoM below the T threshold; a root mouth sweeps a 0.4 m circle | 0.00 | 0.00 | −0.05 | 0 (T undefined, set to 0) | 15.7 |
| **steer2 k 6** | **C's calibrated two-nose klinotaxis (the G3/G8(c) kind)** | **0.27** | 0.63 | **+1.29** | +0.37 | 10.2 |
| steer2 k 32 | the same, stiffer | 0.30 | 0.70 | +1.42 | +0.42 | 10.0 |
| steer1 k 2 | one nose, temporal (turns on a falling reading): the §1.1 lone-nose route | 0.00 | 0.00 | +0.09 | +0.09 | 14.1 |
| **steer1 k 8** | the same, stronger | **0.00** | 0.20 | **+0.43** | +0.30 | 11.5 |

**Finding M1: the zero-count veto makes the call nearly blind to real steering in PW.**
- The two-nose steerer earns +1.3 items a season from smell: 2.8× the blind income, and 5× F_MIN. It is still
  called STEERS on only 27% of genomes.
- Its ΔT is large (+0.37), and F's lower bound clears 0. It fails on PR L203–204: "at most half of the 16 paired
  draws have food_intact = food_decoy exactly".
- In PW a season eats 0.5 items blind and about 2 steered. So on most draws **both** conditions eat 0 or 1: the
  steerer never reached a patch, or reached it only late.
- The one-nose temporal steerer (steer1 k 8, F = +0.43, above F_MIN) is called STEERS on **0 of 30** genomes. It
  is the one route §1.1 names as holistic-specific ("a lone nose read through a `differentiate` unit").
- **The veto is a transplant.** In RBT-104 (`function.py:164–171`) it guarded a readout where an exact 0 meant that
  smell changed nothing. In an integer, sparse, depleting world, an exact 0 means "no patch this draw".

**Finding M2: the battery's draws are fixed "identical for every genome, line, fauna and generation" (PR
L131–133).** Combined with the veto, whether *any* genome can pass is then largely a property of the 16 registered
draws: how many of them put a patch within reach in 15 s. The design never inspects this. A draw set with 9
hopeless layouts would make the instrument unable to fire on anything.

**The fix (MUST 1):**
- **Replace the count veto with a trajectory veto:** a genome is vetoed if its intact and decoy seasons are
  *identical in trajectory* (the root path to 1e-9) on more than half the draws. That is what "smell changes
  nothing" means, and it still catches every sensorless or unused-nose genome exactly.
- **Screen the registered draw set:** print, per draw, the reachability of a patch (the steer2 caricature's intact
  food on that draw). Drop or replace draws on which the positive control eats 0 intact.
- Re-price G3 and G8(c) on the new call.

### 1.2 Can a body pass without steering?

**No false STEERS appeared in the caricature, in any non-steering body.** The four specific routes asked about:

- **Coverage correlated with the start position.** It cannot pass through the decoy on its own.
  - The start (random bearing, 1.5–2.5 m) and the patch centres (uniform in the disc,
    `simulation.py:388–395`) are both rotation-invariant and independent.
  - So a rotated layout has the same joint distribution with the start as the real one. F and ΔT have expectation 0
    for any body that ignores its noses, whatever its path.
  - Blind: F = ΔT = 0 exactly, the 16/16 veto fires, and it is NONE.
  - **Residue:** the clearance rule places real items ≥ 0.8 m from the robot's root (`simulation.py:446–464`), but a
    rotated item can land on the start. The decoy therefore sometimes offers a phantom item under the nose at t = 0,
    which the real layout never does. The effect is small, but it is a difference between intact and decoy that is
    not information. **SHOULD 1:** re-draw θ (from the same stream) until no rotated live item is within the
    clearance of the root at spawn, and test it.
- **The RotatedSmell artefact** (rotation about the origin, patches not centred). This is not an artefact in PW:
  the patch centres are uniform in the disc about the origin, so the rotation preserves their distribution. It
  **would** become one under any layout that is not rotation-invariant (a fixed patch site, `clear_from=geoms`
  applied at placement, or an arena that is not a disc). **SHOULD 2:** `--smell-decoy rotate` asserts, at
  construction, that the food layout rule is rotation-invariant, and refuses otherwise (R15).
- **Eating from the root when the root is not the nose.** This cannot create STEERS, because the call reads food
  and CoM motion, not wiring. It does cost holistic *sensitivity*, though. A body whose mouth is a swinging root
  limb and whose CoM creeps (the `sweep` body) has T undefined (Σ|v| = 0 over > 0.05 m/s ticks) and can at best be
  SMELL-USE.
  - On real bodies this is not exotic: the first RBT-113 holistic U final probed spends **75%** of its control ticks
    below 0.05 m/s of CoM speed (`steer_real.py` timing check).
  - **MUST 2:** register T's value when Σ|v| = 0 (the draft leaves it 0/0), report the share of ticks excluded per
    member, and set the threshold relative to the member's own median speed (for example 0.25 × median |v|), not
    at 0.05 m/s absolute. Otherwise slow bodies are ruled out of STEERS by speed.
- **An orbiter.** T averages to about 0 over a closed orbit, so an orbiter is NONE unless its orbit centre drifts up
  the gradient. That is steering, and it is correctly called.

### 1.3 Does T really separate kinesis from taxis?

The draft's argument (PR L180–185) is that "orthokinesis changes the weights of path segments, not their headings,
so T is unchanged in expectation." **That is not right, and it matters for G8(b).**
- Σ|v| cos∠(v, ĝ) Δt = ∫ ĝ · dx. For a single source, this is −Δ(distance to the source) exactly. For PW's sum of
  exponentials it is approximately −Δ(distance to the patch).
- So **T ≈ net approach / path length**. It is independent of speed only along a *fixed* path.
- Kinesis does not keep the path fixed in time: it produces **aggregation** (a random walker slowed where the reading
  is high accumulates there). That is net approach, so T rises.
- In the caricature this did not produce false STEERS, **but only because no kinesis body could pay in PW's 15 s**
  (every kinesis F is negative: slowing costs more coverage than dwelling gains). The call's condition 1 rejected
  them, and condition 2 was never tested.
- **So G8(b) (the Pioneer throttle plant) will "stay silent" for the same reason.** It tests F, not T: a negative
  control that cannot fail on the condition it is there to guard (D's P3).

**MUST 3:** G8(b) must be tuned to **pay** (F ≥ 0.25 on its hosts, for example an area-restricted-search throttle:
slow and turn more above a reading threshold, with no heading term). It is registered as passing only if it is then
called SMELL-USE and not STEERS. If no kinesis plant can reach F ≥ 0.25 in PW, say so in the registration: T is
then untested but also unneeded. Either way, delete the claim that orthokinesis leaves T unchanged in expectation.

**The design also classes klinokinesis as steering** ("a body whose gait turns more when smell is high will read
T > 0. The draft counts that as klinokinesis, which is chemotaxis", PR L754–755). Undirected turning-rate
modulation is kinesis in the ethology the design cites. It is not the compass's directed turning. **SHOULD 3:**
either say that STEERS means "moves up-gradient by any means, including kinesis", which weakens the link to the
compass valley, or add a kinesis-matched control as in MUST 3.

### 1.4 Real bodies (`steer_real_pw.txt`, `steer_real_committed.txt`)

`steer_real_pw.txt` probes RBT-113 O1 seeds 1–3: U finals, 5 per fauna per seed (30 bodies × 16 paired draws).
The world is PW's layout, but at gain 1 and with committed eating, because the two new flags do not exist yet.

| | holistic (n 15) | designed (n 15) |
|---|---|---|
| STEERS / SMELL-USE | 0 / 0 | 0 / 0 |
| mean F; mean ΔT | +0.17; +0.04 | +0.17; −0.02 |
| mean draws with food_i = food_d (of 16) | **13.1** | **12.3** |
| members with ≥ 11 tied draws | 11 of 15 | 10 of 15 |
| members with ≥ 75% of ticks below 0.05 m/s | **4 of 15** (0.76, 0.80, 0.96, 0.96) | 0 |

**What the real bodies add:**
- **No false STEERS, on 30 coverage foragers.** This is a small G4. The decoy and T do not manufacture steering
  out of RBT-113's movers.
- **Condition 1 is not safe from noise on its own.** One designed final (seed 2, `035`) reaches F = +1.19 with a
  lower bound of +0.24. It is saved by ΔT, and by the veto. With the veto replaced (MUST 1), that member is called
  SMELL-USE: the call worked as designed, and ΔT is doing real work here.
- **The veto's arithmetic holds on real bodies too:** the typical member ties on 12–13 of 16 draws. At PW's
  income, any real steerer among these hosts would be vetoed (MUST 1).
- **T rests on a thin slice of some holistic paths:** 4 of 15 holistic finals move their CoM faster than 0.05 m/s
  on only 4–24% of ticks (MUST 2).
- **T has large per-body offsets** (the designed `002` and `014` read T ≈ −0.7 to −0.9 in both conditions). Only ΔT
  is interpretable, as the design already says.

`steer_real_committed.txt` repeats this in RBT-113's own world (uniform food, instant regrowth, a higher
income). The result is again 0 STEERS: 0 SMELL-USE among the holistic finals and 1 among the designed. **Even
there, members tie on 11.5 (holistic) and 10.7 (designed) of 16 draws.** So the count veto is borderline in the
committed world as well, not only in PW.

## 2. Is the comparison fair?

### 2.1 Holding: G6's rule is the wrong inequality, and crossover is missing from erosion (MUST 4)

- **G6** (PR L341–347) sets D so that s(Δ) ≥ 0.30, "the larger erosion (0.28) rounded up".
- But a carrier lineage under selection s and loss u grows by (1 + s)(1 − u) per generation. It persists only if
  **s > u / (1 − u)**:
  - 0.39 for the designed compass's u = 0.28;
  - 0.17 for B's holistic route loss of 0.146.
- At s = 0.30 and u = 0.28, a steering lineage **shrinks** by 6% a generation.
- **And u is not the erosion that `evolve` applies.** Every measured loss rate is mutation-only: paper 10's u, B2's
  14.6% and B's `parity.py` (`mutate` / `mutate_controller` only). But the registered runs cross over at the
  committed **0.5** (`evolution.py:49`; RBT-113's `config.json` records `"crossover_rate": 0.5`). §5.1 and the
  fairness block (§8.1) never pin it.
- The holistic crossover is B's prefix cut, with `c.child %= n` rewiring links to arbitrary nodes (B's audit
  L279–330): the operator B flags as the most disruptive in the programme. A steerer crossed with a non-steerer
  loses its route with a probability nobody has measured.

`hold.py` simulates the registered truncation (N 40, top 10, crossover 0.5, `--elites 0`). It uses B's measured
background and draw SDs and starts from one carrier (a proposal). It reports P(the line crosses by the design's own
rule at generation 48), and the plateau share from a saturated start (the power model's Q). From `hold.txt`:

| D | Δ (items) | u | cx (loss when crossed with a non-carrier) | holistic P(cross) / Q | designed P(cross) / Q |
|---|---|---|---|---|---|
| 8 | 0.25 (F_MIN) | 0.146 | 0 | 0.175 / 0.59 | 0.245 / 0.64 |
| 8 | 0.25 | 0.146 | 0.5 | 0.043 / 0.29 | 0.065 / 0.37 |
| 8 | 0.25 | **0.28** | 0 | 0.048 / 0.12 | 0.048 / 0.19 |
| 8 | 0.25 | 0.28 | 0.5 | **0.000 / 0.006** | **0.000 / 0.011** |
| 8 | 0.50 | 0.146 | 0.5 | 0.357 / 0.76 | 0.448 / 0.78 |
| 8 | 0.50 | 0.28 | 0.5 | 0.220 / 0.51 | 0.305 / 0.59 |
| 2 | 0.25 | any | any | ≤ 0.045 | ≤ 0.030 |

**What this means:**
- **A steerer at F_MIN, eroded at the designed compass's rate and disrupted by crossover, is never held at D = 8.**
  Only steerers worth about 0.5 items a season hold reliably.
- So the design's floor verdict (NEITHER) can be reached by erosion alone, on either body.
- **The unequal per-structure erosion is a direct lever on the primary outcome.** At Δ = 0.25, D = 8 and cx = 0,
  the same steerer is held 0.175 of the time at the holistic u and 0.048 at the designed u.
  - **A HOLISTIC verdict can therefore be produced by the operators' loss rates, with no difference in the
    valley.**
  - The design's reply (the operator is part of Conrad's geometry, PR L363–365) is defensible. But §2.4's claim
    that unequal erosion "does not favour either body in one direction" is wrong for the *holding* half of the
    primary, which is exactly where per-structure loss acts.
- **The power model's Q = 0.5 is unanchored:** `hold.py` gives plateaus from 0.01 to 0.8 across the registered
  parameter range.

**The fix (MUST 4):**
- **Pin `--crossover` on every command.**
  - Either set 0 in both faunas. This is cleanest: the proposal assay is mutation-only, and so is every loss rate in
    the design (R8: "same operator and crossover").
  - Or keep 0.5, and measure crossover loss in the assay and in G6.
- **Rewrite G6's criterion as (1 + s(Δ))(1 − u_eff) ≥ 1 + margin,** with u_eff the measured loss including
  crossover, and Δ the prize of a STEERS-level steerer (F_MIN), not C's kinematic "first weak nose".
- **Derive Q_f in `power.py` from the realised s and u** (the equilibrium share, or `hold.py`'s simulation), not a
  constant 0.5.
- **Make the assay's loss-rate ratio (H : P) a registered interpretive covariate.** A HOLISTIC verdict with the
  holistic loss rate below half the designed one carries the sentence "consistent with lower erosion of steering
  under the holistic operator".

### 2.2 The start points

- **Both start populations are RBT-113 finals.** They were evolved under the committed eating rule, with no motor
  budget, no outward limbs, no settle and no extent cap, in RBT-113's world (a 3 m disc, uniform food, instant
  regrowth, `sum`, decay 1).
- **Under PW with every fix ON, they are not at a peak, and not equally far from one.**
  - The Pioneer loses its wheels' eating reach (root = chassis). Its body is otherwise unchanged by A2–A5.
  - The holistic finals are **rebuilt**: outward limbs move embedded parts, `max_extent` 0.6 m and
    `cap_on_reachable` can change what builds at all, and root eating removes the limb mouths their coverage used
    (A5).
- The first generations of both U and N will therefore be spent re-adapting to PW's physics and mouth. That is
  selection for **root coverage**, the downhill path C finds everywhere, and it spends the 48-generation budget
  unequally.
- The design's G9 census prints founders and finals in PW, but gates nothing. "The valley floor" (PR L291) is
  asserted for a world the starts never saw.

**SHOULD 4, or MUST if the ruling keeps "coverage peak" in the headline:**
- Run a **shared burn-in**: 12 generations of U-style selection in PW with every fix ON and **lesioned smell**, from
  the RBT-113 finals, per unit and fauna. Its final population is the generation-0 of both U and N.
- This makes the start a coverage peak **in the world used**, for both bodies, at about +25% of evolution cost. It
  also removes the re-adaptation transient from the A_f time average, whose first probe is at generation 12.
- **Also:** state what `max_extent` does to an over-extent start member (clamp, or reject and refill; PR L672 leaves
  the gear case [OPEN], and extent has the same problem).

### 2.3 Same draws for both bodies? Is PW neutral?

- **Draws:** yes. Both faunas in one `evolve` run share every generation's `(terrain_seed, start_seeds)` (I4), and
  the battery's draws are fixed. Good. But see M2 on what fixed draws do to the veto.
- **Is PW neutral between wheels and limbs?** It cannot be judged, because **PW's defining knob is not defined.**
  - `smell_gain` is "a centred contrast" with two candidate forms (C's AUDIT L159–160):
    `tanh(G · (ln Σ − ln Σ_root))`, or a per-robot running baseline.
  - **Every PW number the design cites comes from neither.** C's model applies the gain to the raw left − right
    difference of two noses (`probe_world.py`: `diff = GAIN * (il - ir)`, with no root, no centring and no per-nose
    tanh). That includes the 3.66× peak, the +0.220 first-nose margin behind Δ = 0.10, and the +4–13% nose step.
  - The two candidates have **opposite parity effects**, and the draft sees half of it (§10.6):
    - **Root-centred** zeroes every root nose: the Pioneer's chassis nose, every holistic nose on the root, and
      **G8(b)'s throttle plant, whose input would be identically 0**. That makes it a control that cannot fail,
      in the plainest way. It also leaves a holistic body with one nose on its root blind.
    - **Running baseline** turns every lone nose into a temporal-gradient detector. That favours one-nosed bodies,
      mostly holistic (39% carry any food nose, PR L301), and it changes paper 8's pirouette arithmetic on the
      Pioneer.
  - The same world name would therefore carry an anti-holistic or a pro-holistic bias, depending on a line of
    code that is not yet written.

**MUST 5:**
- The registration **names the transform** (the formula, the reference reading, and what a lone root nose reads).
- G1, G2, G6's Δ, G7 and G8 are re-measured on it.
- **No PW number from C's kinematic model is cited as support** for a transform it did not simulate.
- G8(b)'s throttle plant is fed by a **non-root** nose (a wheel nose driving the throttle axis) so that it is
  not trivially silent.

**`eat_from=root` (the choice between eating rules):** the draft's reasoning is sound. The committed rule pays span
(A5), and `sensor` pays nose-carrying for its own sake. Keep root. Two costs should be registered:
- **SHOULD 5:** define "root" on a holistic body after `outward_limbs`: Node 0's first Part, or the part with the
  largest mass? Pin it with a test that the Pioneer's root is the chassis (R12).
- **SHOULD 6:** report, per fauna at generation 0, the share of income lost from the committed rule to root
  eating. This is the R6 side effect of the eating change. It is likely much larger for the holistic starts, which
  ties back to §2.2.

### 2.4 Motor budget and the A2–A5 fixes

The fairness block is complete for the rows it lists, and "reported instead" is a sensible downgrade. **Missing
rows:**
- **crossover rate** (MUST 4);
- **the smell transform** (MUST 5);
- **T's speed threshold** (MUST 2);
- **the decoy's θ stream and clearance** (SHOULD 1).

Add them to §8.1, pinned on every command.

## 3. Gate G7: is the valley still there on the Pioneer?

The gate is well aimed, but it is under-specified, and it is too narrow to support the NEITHER verdict's reading.

- **It tests one intermediate:** paper 8's lone-nose pirouette. The Pioneer's valley in PW is "still there" only if
  **every** one-step intermediate from the coverage peak toward the compass is non-paying. At least three others
  exist in the Pioneer's operator:
  - a lone nose to the **throttle** axis (kinesis: G8(b)'s plant);
  - both wheel noses with the **same** sign (the sum drives the throttle);
  - a lone nose onto one wheel.

  If any of these pays in PW (C's model says a weak nose pays +0.22 there), the Pioneer has a ridge that paper 8's
  valley did not have. A clean "NEITHER" would then be read as a valley that did not exist. **MUST 6:** G7 measures
  the prize of every one-step intermediate in this list at the smallest paying rung. It passes only if none has a
  lower bound > 0. The table is printed as the Pioneer's valley.
- **Which nose is the lone nose?** Under a root-centred transform, the chassis nose reads 0, so the pirouette has to
  be a wheel nose. Say so (MUST 5).
- **"The first a whose prize has a lower bound > 0"** needs its n: hosts × draws, and the CI method. With 16 hosts
  and PW's sparse eating, the smallest paying rung is a noisy object. Register 16 hosts × 16 draws and a paired t
  bound, and compute G7's power at the expected prize. **SHOULD 7.**
- **The gain step-down is sound as a rule.** G2 and G7 pull in opposite directions, and "largest passing gain" is
  well defined. But G2 as written (F ≥ the coverage gain that RBT-113's 24 generations bought) is measured in a
  world whose eating rule changed. Measure both terms in PW with every fix ON.

## 4. Power (R10; the RBT-117 lesson)

**Is `power.py` bounded?**
- A_f is bounded in [−EPS, Q_f], and that is honest.
- But Q_f = 0.5 is **asserted**, and `hold.py` shows that the registered D, u and crossover give Q ∈ [0.01, 0.8]
  depending on Δ. The bound is a parameter, not a measurement (MUST 4).
- EPS is one number for U and N, both faunas, every generation.

**`power_attack.py`** imports the design's own `verdict()` unchanged and moves only the generator
(`power_attack.txt`, n = 24, 300 readouts per row):

| scenario | HOLISTIC | NEITHER | INCONCL. | HOLISTIC while NEITHER's bound also holds |
|---|---|---|---|---|
| the design's null (EPS 0.02 in U and N) | 0.007 | 0.900 | 0.087 | 0.003 |
| **null; the holistic N sheds noses: EPS_U 0.04, EPS_N 0.01** | **0.540** | 0.397 | 0.063 | 0.507 |
| null; holistic EPS_U 0.05 (the G4 cap), EPS_N 0.01 | 0.690 | 0.250 | 0.060 | 0.607 |
| null + ONE holistic unit at share 0.75 throughout | 0.000 | 0.780 | 0.220 | 0 |
| null + ONE holistic unit at 1.0 throughout | 0.003 | 0.763 | 0.233 | 0 |
| every holistic line plateaus at 0.15 (never "crosses" by PR L238) | 0.800 | 0.080 | 0.120 | 0.247 |
| bypass p 0.5 but plateau 0.12 (`hold.py`, u 0.28) | 0.240 | **0.697** | 0.063 | 0.220 |

**Findings:**

1. **MUST 7: the null correction is fragile to a U/N false-positive gap, and the design predicts that gap.**
   - N's smell is a *misleading* signal: a rotated live layout, not silence.
   - So in N every residual nose→motor coupling is actively costly, and truncation purges it. In U the same
     coupling is neutral or pays.
   - The design names this risk (§10.4) and prints diagnostics beside the verdict. But a gap of 0.04 against 0.01 in
     the holistic fauna alone turns the null into **false HOLISTIC 0.54**.
   - **The fix: a confirmation battery.** A STEERS call must repeat on 16 fresh draws before it counts. That takes
     EPS to about EPS² (0.02 → 0.0004 if independent), and makes any U/N gap in EPS negligible against real
     shares. The cost is about +50% of probing, which is about 0.3 CPU-h per arm.
   - **And a registered check:** EPS measured on generation 0, which is identical in U and N, is printed beside
     share_N(12…48). A drop in share_N below the generation-0 rate is flagged as purging.
2. **MUST 8: HOLISTIC MORE READILY must require crossing.**
   - As coded, a significant d with a significant A_H fires HOLISTIC even when **no holistic line crossed** (all
     plateaus 0.15: HOLISTIC 0.80). It also fires when NEITHER's own bound holds at the same time: 0.25 of
     readouts there, and 0.51 in the EPS-gap null.
   - The code's ordering hides this. The report would headline "crosses more readily" while its line-level count
     says that fewer than 1 line in 4 crossed on either body.
   - **The fix:** HOLISTIC also requires k_H ≥ k*, for example an exact one-sided test of k_H against k_P on
     paired units (McNemar-style, on discordant units). Symmetrically for PIONEER. Otherwise, rename the A-based
     verdict "HOLISTIC STEERS MORE" and keep "crosses" for the count.
3. **One influential seed does nothing.** A single holistic unit at share 1.0 throughout never produces HOLISTIC
   (0.003). The t CI and the sign-flip p absorb it. R10's clause is satisfied. **Say so in §7.**
4. **NEITHER CROSSES fires on a real bypass with a low plateau** (0.70 at p 0.5, Q 0.12). Given `hold.py`, low
   plateaus are the expected shape of a real crossing at u = 0.28. **SHOULD 8:** the NEITHER sentence says
   "steering did not reach and hold 1 member in 4 in more than 1 line in 4", and does not say that the "extra
   dimensions did not open a way round it".

**Is a weak bypass (power 0.34) worth running? Yes, with the cheap cures instead of the expensive ones.**
- The expensive cures are +50% cost each (G = 72, or 36 units).
- The binding noise at low shares is **binomial probing noise**, and probing is about 8% of an arm's CPU (§9: 0.6 of
  7.9 CPU-h).
- The cheap cures:
  - probe **all 40 members** (M = 40);
  - use a confirmation battery (MUST 7), which lets CROSS_SHARE fall to 0.125.
- The `power_attack.txt` "Cures" section prices them in the design's own model (P(HOLISTIC) / P(NEITHER) /
  P(INCONCL.)):

| design variant | null | weak bypass (p 0.25, Q 0.5) | weak bypass, Q 0.3 | bypass p 0.5, Q 0.15 | null with a holistic EPS gap (×2.5 / ×0.5) |
|---|---|---|---|---|---|
| as registered (M 16, EPS 0.02, CROSS 0.25) | 0.00 / 0.92 / 0.07 | 0.34 / 0.06 / 0.60 | 0.18 / 0.26 / 0.56 | 0.36 / **0.48** / 0.16 | **0.64** / 0.28 / 0.07 |
| M = 40 | 0.00 / 0.88 / 0.11 | 0.35 / 0.08 / 0.58 | 0.27 / 0.28 / 0.45 | 0.48 / 0.46 / 0.06 | 0.73 / 0.22 / 0.05 |
| M = 40, confirmation (EPS 0.002, sensitivity × 0.75), CROSS 0.125 | 0.00 / 0.90 / 0.10 | 0.44 / 0.07 / 0.49 | 0.32 / 0.12 / 0.55 | 0.59 / 0.07 / 0.34 | 0.12 / 0.76 / 0.12 |
| … plus MUST 8 (an exact paired test on crossed lines) | 0.01 / 0.91 / 0.08 | 0.37 / 0.07 / 0.56 | 0.24 / 0.08 / 0.66 | 0.24 / 0.14 / 0.61 | **0.00** / 0.89 / 0.10 |

**Reading:**
- **More members plus confirmation is the cheap cure.** It raises weak-bypass detection from 0.34 to 0.44, and a
  low-plateau bypass from 0.36 to 0.59. It **stops a real low-plateau bypass reading as the clean "no"** (NEITHER
  0.48 → 0.07). The cost is roughly 1 CPU-h per arm, not +50%.
- **Confirmation alone does not close the EPS-gap hole** (0.12 false HOLISTIC remains). That is because the A-test
  has no minimum effect: a handful of units with tiny consistent positive differences pass a sign-flip test.
- **MUST 8's crossing requirement closes it** (0.00), at the price of some power at low plateaus (0.59 → 0.24),
  which goes to INCONCLUSIVE and not to NEITHER.
- **The recommendation is the last row.** Buy G = 72 only if the re-run `power.py` (MUST 9) still leaves the weak
  bypass below 0.5.

## 5. Nulls

- **Does N match everything except information? Mostly.**
  - `evolve` has no births, depth or density, so R6's demographic channels do not exist here. That is a real
    strength of `evolve` over the ecology.
  - **Income:** U's income can rise with steering and N's cannot. That is the treatment, not a side effect.
  - **Misinformation:** N's decoy *penalises* nose use (§4, MUST 7). That is a second channel: N is "information
    removed **and** nose use taxed". Two alternatives would each isolate one part:
    - a lesioned-smell N (no information, no tax, but input statistics differ);
    - an N whose θ is fixed per lineage (still misleading).

    Neither is clean. **The confirmation battery (MUST 7) makes the choice matter much less.** SHOULD 9: print U − N
    in nose count, and in the share of members with any nose→effector path of gain > 0.1, at every probe (R6 at
    the wiring level, not only behaviour).
- **Is the offline proposal assay a valid mutation-only rate? Not as specified.**
  - (a) **It is mutation-only while the lines are not** (crossover 0.5). MUST 4 resolves this either way.
  - (b) **Misclassification swamps the rate.** "Children that STEER whose parent did not" counts every true steerer
    parent called NONE (sensitivity is 0.27–0.63 per call, §1.1) whose child is called STEERS. At a steering share of
    10% and sensitivity 0.5, that is about 2.5% of children, against a true rate near 2 × 10⁻⁵.
  - **Fix:** call parent and child on the **same** draws, and require the parent to be NONE on a confirmation
    battery too. Or report the rate only among parents with F ≤ 0 on both batteries.
  - (c) **It is powerless for the Pioneer's known rate.** About 9,600 children per fauna, against 84 of 200,000 in
    paper 8, bounds the rate only above about 3 × 10⁻⁴ (3/9,600). State that it detects rates above that, and cannot
    confirm paper 8's.
  - (d) **The stage-1 screen** "F₁ > 0 on 4 draws" misses a real steerer whenever all 4 draws tie at 0: about 15%
    of the time for steer2 k 6, and more for weak steerers.

  **SHOULD 10:** (b), (c) and (d). The assay never enters a verdict, which is why these are SHOULD.

## 6. Verdict logic

- **Can two verdicts fire at once?** In code, no: they are ordered. In substance, yes: HOLISTIC and NEITHER's
  conditions are both true in up to 0.61 of readouts in the scenarios above (MUST 8).
- **Can none fire?** No: INCONCLUSIVE catches the rest.
- **Is INCONCLUSIVE priced honestly?** It is honestly printed (0.94 when both cross), but it is priced with
  Q = 0.5. With `hold.py` plateaus, the realistic mass moves from INCONCLUSIVE into **NEITHER** (§4, finding 4),
  which is the more dangerous direction: a real low-plateau bypass reads as the clean "no". Re-run `power.py` with
  Q from MUST 4 before registering.
- **EQUIVALENT** is unreachable, and the draft says so. Fine.

## 7. Prerequisites, and which could change the answer if mis-built

| prerequisite | changes the answer if mis-built? | how |
|---|---|---|
| `smell_gain` (the centred contrast) | **yes, in either direction** | root-centred blinds root noses (anti-holistic, and G8(b) silent by construction); running baseline makes lone noses temporal sensors (pro-holistic). MUST 5. |
| `--smell-decoy rotate` | **yes** | it must rotate only `food` sources, before the transform, with the θ stream shared across faunas and U/N, and pass the sensorless byte-identity test. A decoy that also rotates the root reference under a root-centred transform is fine; one that rotates *after* the transform is not a decoy. |
| `eat_from=root` | **yes** | the definition of the holistic "root" after outward limbs decides how much holistic income survives (SHOULD 5, 6) |
| `outward_limbs` + `ball_cone` | **yes, via the starts** | they rebuild holistic start members (§2.2) |
| `max_extent`, `cap_on_reachable` | **yes, via the starts** | whether an over-cap start is clamped or rejected changes generation 0 |
| gear budget (RBT-120) | moderately | the Pioneer sits inside by construction. A cap that clamps holistic motors changes their coverage speed, and hence the downhill competitor to steering |
| `effector_bias_sigma` | moderately | B's fix must reach **both** operators. If only one gets it, one fauna saturates motors |
| `settle_until_rest` | little | affects motors-off and the start transient |
| `clear_from=geoms` | little, but it interacts with the decoy | the clearance for rotated items (SHOULD 1) |
| **crossover rate (not listed)** | **yes** | `hold.py`: cx 0.5 against 0 moves P(cross) at Δ 0.25 from 0.175 to 0.043 (holistic, u 0.146). MUST 4. |
| `--from-population` | yes if it redraws | I3 catches it |
| draws (G6) | yes | MUST 4 |
| `steer.py`'s T (the CoM definition, the threshold, Σ|v| = 0) | yes | MUST 2 |

## 8. What the four audits flag that the design does not take in

- **B, crossover** (`c.child %= n`, the prefix-cut length bias, B L279–330): not mentioned. It is the operator the
  lines run under (MUST 4).
- **B, "the designed U line is ranked on noise"** (B L206–208, with repeatability 0.004). At D = 8 the designed
  fauna's selection still rests mainly on the draw noise. G6 should print both faunas' repeatability at the chosen D,
  and a planted +Δ allele pilot (B's own "cheap test", L221–223), which the design omits. **SHOULD 11:** run B's
  pilot on one unit per fauna in PW. It is the direct test of MUST 4's hold arithmetic.
- **A, H71 (penetration).** The sensitivity drops members over 0.10 m. If the designed body routinely sinks 0.35 m
  on random terrain, that sensitivity drops most Pioneers and becomes degenerate. Print the share dropped per fauna,
  and treat a split that drops > 50% of one fauna as not interpretable.
- **C, the kinematic margins** are a point forager with a 0.15 m half-span mouth (`probe_world.py` `HALFSPAN`). Under
  root eating the half-span is 0. Every Δ, G2 and G7 number must come from the gate (MUST 5), which the draft
  already half-says (PR L428).
- **D, P3 (instruments that could not fail).** G8(b) as specified (MUST 3 and MUST 5) and the count veto (MUST 1)
  are both instances.
- **D, R8 (nulls matched in operator and crossover):** the assay against the lines (MUST 4).

## 9. MUST and SHOULD

**MUST (before registration):**

1. **Veto.** Replace the zero-count veto with a trajectory-identity veto, screen the fixed draws for reachability,
   and re-price G3 and G8(c). *Evidence:* `steer_probe.txt`. A two-nose steerer with F +1.29 is called STEERS 0.27
   (0.63 without the veto). A one-nose temporal steerer with F +0.43 is called STEERS 0.00.
2. **T.** Define T when Σ|v| = 0, report the excluded-tick share, and make the speed threshold relative to the
   member's median speed. *Evidence:* a real holistic U final spends 75% of its ticks below 0.05 m/s (§1.2, §1.4).
3. **G8(b).** It must pay (F ≥ 0.25) to be a negative control on T, and must be fed by a non-root nose. Delete
   "orthokinesis leaves T unchanged in expectation": T ≈ net approach / path length, and kinesis aggregates.
   *Evidence:* every kinesis caricature has F < 0, so it is rejected by F, and condition 2 is never exercised.
4. **Holding.** Pin crossover; rewrite G6 as (1 + s)(1 − u_eff) ≥ 1 + margin at Δ = F_MIN; derive Q_f from it; and
   make the assay's loss-rate ratio a registered covariate of a HOLISTIC verdict. *Evidence:* `hold.txt`.
5. **The smell transform.** Name it, re-measure every PW number on it, and cite no C-model number for it.
   *Evidence:* C's `probe_world.py` gains the raw two-nose difference, with no centring (§2.3).
6. **G7.** Test every one-step intermediate, not only the pirouette.
7. **The null.** A confirmation battery for every STEERS call, plus the generation-0 EPS check on share_N.
   *Evidence:* `power_attack.txt`, EPS_U 0.04 against EPS_N 0.01 gives false HOLISTIC 0.54.
8. **HOLISTIC and PIONEER require crossing** (k), or the A-verdict is renamed. *Evidence:* `power_attack.txt`,
   plateau 0.15 gives HOLISTIC 0.80, with 0.25 of readouts also meeting NEITHER.
9. **Re-run `power.py`** with EPS_U ≠ EPS_N, Q from MUST 4, the confirmation battery, and M = 40. Print the
   one-influential-seed row (§4, finding 3).

**SHOULD:**

1. Re-draw θ so that no rotated item lies within the clearance of the spawn.
2. `--smell-decoy rotate` refuses a layout rule that is not rotation-invariant.
3. Say whether STEERS includes klinokinesis, and adjust the ticket wording.
4. A shared, smell-lesioned burn-in of 12 generations in PW with every fix ON, as generation 0 of U and N; and state
   the over-cap start rule.
5. Define the holistic "root", with a Pioneer-root = chassis test.
6. Report generation-0 income lost to root eating, per fauna (R6).
7. G7's n and CI method, and its power.
8. The NEITHER sentence bounded to what it measures.
9. U − N wiring diagnostics at every probe.
10. The proposal assay: same-draw calls, a confirmed-NONE parent, and its detection floor stated.
11. B's planted +Δ holding pilot, one unit per fauna, in PW.

**Kept as it is (the design got these right):**
- the behavioural definition;
- the rotated live decoy instead of a mirror or a static layout;
- root eating over sensor eating;
- `evolve` truncation over the ecology;
- shared worlds, and I1–I7;
- the refusal to widen DELTA_EQ;
- the fairness block's "reported instead" discipline;
- n ≥ 24.

## Files

| file | what | runtime |
|---|---|---|
| `steer_probe.py` / `.txt` | the registered call on kinematic bodies in PW (30 genomes × 16 draws each) | about 10 min |
| `hold.py` / `.txt` | truncation holding: P(cross) and plateau Q against Δ, u, crossover and D | 80 s |
| `power_attack.py` / `.txt` | the design's `verdict()` under an EPS gap, an outlier, low plateaus, and the cures | about 3 min |
| `steer_real.py` / `steer_real_pw.txt` / `steer_real_committed.txt` | the registered call on RBT-113 O1 U finals (real bodies, read-only), PW at gain 1 with committed eating, and RBT-113's world | about 10 min each |
