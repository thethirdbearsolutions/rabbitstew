# RBT-116 pre-registration (r7, for registration): the extradimensional bypass. Do holistic bodies cross the compass valley more readily than the Pioneer?

*Designer's **revision 7** (2026-09-27, about 21:50 UTC). **r7 adds the coordinator's binding R6-1 and R6-2** (ruling at
22:05 on the adversary's `R6-CHECK.md` @ `3f2bfc7`, which read REGISTER), as registered text before merge (§0, r7
table). Revision 6 was, written under RBT-115 (reason (c) of the 2005 proposal).
r5 answered the design adversary's REDESIGN (narrow) verdict (PR #408, `ADVERSARY.md` @ `e51aabf`) and the
coordinator's ruling (22:15). **r6 answers the adversary's re-read of r5** (`R5-CHECK.md` @ `82211af`: REGISTER AFTER
FIXES) and the coordinator's ruling on it (21:55): R5-1 and R5-2 as MUST; R5-3, R5-4 and R5-5 as SHOULD; R5-6 and
R5-7, the adversary's further SHOULDs, are also taken. §0 maps every item to the text. Revisions 1–5 (`c8e8389`,
`88d95d7`, `62fbc97`, `577ef9e`, `8ad0162`) are superseded.*

> ## Amendment 1 (pre-data), 2026-09-28, revised 02:45 UTC: the smell transform is the merged RBT-125 channel, at RBT-116's registered τ = 1 s
>
> **Revision (coordinator's ruling at 02:38 on PR #434, pre-data).** Amendment 1 as first committed (`c5fbe93`) also
> moved τ from 1 s to 2 s, to match RBT-125's code default. That move is **struck**: RBT-116 **keeps τ = 1 s as
> registered at r7**, on its own power grounds (Amendment 2 records the τ probe and the power re-run). Items 2–5 below
> (the floor, the first-tick baseline, the mean over every food sensor, the lesion) stand. W1's block sets
> `smell_tau: 1.0` **explicitly** (the code's default is 2.0), and `steer.py` refuses a world whose `smell_tau`
> differs from the registration's. RBT-125's channel and the RBT-129 sweep keep τ = 2 s (the coordinator's 02:10
> ruling); where RBT-116 runs at a sweep point, its arms carry τ = 1 s, and the difference is named in both
> registrations. The first version's heading was "the smell transform is the merged RBT-125 channel (τ = 2 s)".
>
> **No RBT-116 output exists.** No arm, gate cell, draw screen or battery of this design has been run; `steer.py`
> is committed after this amendment, and only its unit tests have run (on fixture worlds, not on W1).
>
> **What changed.** §4.2 (and every place that restates it: §0's MUST 5 row, §1.1's lesion row) now names the transform
> exactly as merged in `rabbitstew/simulation.py` (`Simulation._food_contrast`, `_log_smell`; `FoodConfig.smell_contrast`,
> `smell_tau`, `smell_lesion`), which RBT-125's world gate validated (§A PASS at G = 2.5, `runs/RBT-125/gate/READOUT.md`):
> 1. ~~**τ = 2 s, not 1 s** (`FoodConfig.smell_tau`, CLI `--smell-tau`, default 2.0; written into `config.json`
>    whenever `smell_contrast > 0`).~~ **[revised] τ = 1 s, as registered at r7**, set explicitly
>    (`FoodConfig.smell_tau = 1.0`, CLI `--smell-tau 1.0`; the code's default is 2.0, and `config.json` states τ
>    whenever `smell_contrast > 0`).
> 2. **The floor is 10⁻¹² inside the log, not 10⁻⁶**: ℓ_i = ln(Σ_items exp(−d_i/decay) + 10⁻¹²), d_i the xy
>    distance from the sensor Part's geom centre. Eaten (parked) items sit at 10⁶ m and contribute exactly 0. This is
>    the channel's own sum (`_log_smell`), not the legacy `_intensity` sum: the `--smell` mode plays no part.
> 3. **The baseline starts at the robot's first reading, and only a lone nose reads 0 there.** b_r is initialised to
>    the mean of ℓ_i over the robot's food sensors on its **first control tick of the season** (after the settle, with
>    the season's layout in place), and is then advanced once per control tick, by the factor 1 − e^(−Δt/τ), **before**
>    the noses are read against it. So on that first tick a lone nose reads exactly 0, but each of several noses reads
>    tanh(G·(ℓ_i − mean ℓ)): its spatial offset, not 0. r7's "every nose reads 0 at spawn" was false for any body with
>    two or more noses (RBT-125 adversary G5).
> 4. **The mean runs over every `food` Sensor of the robot**, one term per Sensor unit (the chassis and both wheels
>    on the Pioneer; every expressed food Sensor on a holistic body; two Sensors on one Part count twice). No nose is
>    the reference, so none is zeroed.
> 5. **The lesion is `FoodConfig.smell_lesion`** (RBT-130, the flag RBT-129's R_marker arm uses): every food sensor
>    reads the channel's zero-information constant, **exactly 0, from the first tick** (the reading of any nose at its
>    own baseline). The baseline is not advanced. r7 described it as "Σ_i set to a constant, so every reading decays to
>    0"; the reading is the same constant, reached at once rather than by decay.
>
> 6. **The eating distance rule is surface** (added 2026-09-28, pre-data, on the coordinator's 03:10 addendum: RBT-125's
>    eating rule is re-ruled to `--eat-from root --eat-rule surface`, PR #436 and its §C adversary #445). r5–r7 said
>    `--eat-from root` and left the distance rule at the code's default, `centre` (an item within 0.35 m, in xy, of the
>    root's geom centre). W1 now eats an item within 0.35 m (3-D, the item at z = 0) of the **root Part's surface**
>    (`Simulation._surface_distance`). Under `clear_from=geoms` the world's clearance is then also measured from every
>    geom's surface, and the decoy's re-draw follows it (Amendment 2, item 3). **What depends on it:** `steer.py` itself
>    does not: it reads the world's eating and clearance rules and hard-codes neither. The test fixtures eat by the
>    code's default (`any`, `centre`); `fixture_eat_probe.py` → `fixture_eat_probe.txt` re-runs every fixture body and
>    every plant of `design-adversary/g8f_probe.py` under both rules at τ = 1 s, and **every call is the same under
>    both** (the planted positives STEERS, the planted negatives NONE at stage 1, the registered G8(f) shape NONE, the
>    rectified −128 plant STEERS; F moves, e.g. the one-nose positive +3.31 → +2.31). The power inputs do not depend
>    on it: the SENS priors come from the r5 caricature, whose mouth is a point, where the surface and centre
>    distances coincide; every rate is measured at the gate in W1, under this rule. So power does not move.
>
> **Why** (items 2–5; the τ part of this paragraph is superseded by the revision above). RBT-125's design adversary (G5, `runs/RBT-125/adversary/ADVERSARY.md`) found that the merged channel used
> τ = 2 s and 10⁻¹², while this registration said τ = 1 s and 10⁻⁶, so the RBT-125 gate would validate a channel
> RBT-116 would not run. The ruling on that review (its M5, `runs/RBT-125/gate/REGISTRATION.md` A1.5) kept the code
> at τ = 2 s with the 10⁻¹² floor, and said RBT-116's registration would be amended to it. RBT-129's registered world
> block already uses that channel (`runs/RBT-129/DESIGN.md` §2, "τ = 2 s, RBT-125's ruled value, with its 1e-12
> floor"), and RBT-129 §11.1 gates on `steer.py` reading the same transform.
>
> ~~**What it moves.** A lone nose's temporal gain is G·τ, so doubling τ doubles it: at W1 (G = 2.5, decay 1.5), a nose
> approaching one item head-on at 0.3 m/s reads about tanh(2.5 · 2 · 0.3 / 1.5) = tanh(1.0). The lone-nose route is
> closer to a sign detector than r7's text implies (RBT-125 adversary C5). The design-stage caricature numbers for
> the one-nose route (`design-adversary/r5_probe.txt`, cited in §1.3 and R5-2: F +0.12 to +0.14 at moderate gains)
> were computed at τ = 1 s and stay what they were, priors. Nothing registered is decided by them: SENS_1 is measured
> by G8(f) at the gate on the merged channel, and `power.py` is re-run there.~~ **[revised]** τ stays at 1 s, so the
> lone nose's temporal gain is r7's G·τ = 2.5 at W1, and the design-stage caricature priors (`r5_probe.txt`, at τ =
> 1 s) are the ones r7's power was built on (Amendment 2). The floor changes ln Σ by less than
> 2 × 10⁻⁴ whenever any item stands in W1's disc (RBT-125 REGISTRATION A1.5), and when none stands, every nose reads
> the same floor under either value.
>
> **How the text is kept.** The superseded r7 wording is struck through in place (~~like this~~), with the amended
> wording beside it marked **[A1]**. Nothing else in r7 changes. On the command line W1's transform is
> ~~`--smell-contrast 2.5 --smell-tau 2.0`~~ **`--smell-contrast 2.5 --smell-tau 1.0`**.

> ## Amendment 2 (pre-data), 2026-09-28: G8(f)'s one-nose plant is rectified; τ = 1 s kept on power grounds; the decoy clears the world's clearance points
>
> **No RBT-116 output exists.** Everything cited here is a fixture or caricature probe, not an RBT-116 arm, gate cell,
> W1 draw or host. Rulings: the coordinator's 02:25 (MERGE AFTER FIXES) and 02:38 (τ) comments on PR #434, on the
> design adversary's `design-adversary/ADVERSARY-STEER.md` (S-M1, S-M4, S-S1).
>
> **1. G8(f) is a rectified one-nose unit (S-M4).** r7's G8(f) read: *"one food sensor on the host's most-moving
> expressed Part (the largest mean geom speed in one intact season), a global unit on its reading, and a turn command
> ±w to the Effectors on one side of the measured heading, 2 signs × w ∈ {4, 16, 64}, best by F on screening draws."*
> As registered, that plant cannot steer: `design-adversary/g8f_probe.txt` (the PR's one-nose fixture world, the full
> 4 + 16 + 16 battery, a Pioneer host with one wheel nose) reads NONE on all six registered variants (a tanh unit at
> input weight 1, ±w ∈ {4, 16, 64} to one wheel; F −1.50 to −0.56), NONE for a tanh unit at input −128 (F −0.31) and
> for a rectified unit at input −1 (F 0.00), and **STEERS only for a rectified unit at input −128** (F +3.31). A
> symmetric unit turns as much while the contrast rises as while it falls; run-and-tumble needs the asymmetry and a
> high input gain. **G8(f) now reads:** one food sensor on the host's most-moving expressed Part (unchanged); a global
> unit with the **rectified** transfer (`relu`, `tanh(max(x, 0))`) fed by the reading at input weight **−g, g ∈ {32,
> 128}** (it turns while the contrast falls); linked **±w, w ∈ {4, 16, 64}**, to the Effectors on one side of the
> measured heading (unchanged); best of the 2 signs × 2 gains × 3 w = 12 variants by F on the screening draws. The grid
> is chosen from `g8f_probe.txt` alone: 128 is the probe's steering gain, the registered maximum; 32 is the one step
> below it that the adversary proposed; gain 1 failed. No gate output exists or informs it. **`gate.py`'s planter
> must be shown to build a steerer on the fixture world (a test in its PR) before any gate cell**, since the probe's
> steering plant drove both drive wheels and this one drives one side.
>
> **2. τ = 1 s is kept, on power grounds (S-S1; the 02:38 ruling).** The design-stage priors, from
> `design-adversary/tau_probe.txt` (r5's caricature and call, G 2.5, 25 genomes × 2 batteries per cell):
>
> | body | τ | single PASS | confirmed | mean F | mean ΔT |
> |---|---|---|---|---|---|
> | two-nose steer2 k 6 | 1 s | 0.64 | **0.48** | +1.198 | +0.374 |
> | two-nose steer2 k 6 | 2 s | 0.52 | 0.40 | +1.145 | +0.362 |
> | one-nose steer1 k 8 | 1 s | 0.08 | 0.00 | +0.142 | +0.227 |
> | one-nose steer1 k 8 | 2 s | 0.12 | 0.00 | +0.297 | +0.241 |
> | one-nose steer1 k 32 | 1 s | 0.52 | **0.32** | +0.562 | +0.346 |
> | one-nose steer1 k 32 | 2 s | 0.44 | 0.24 | +0.520 | +0.322 |
>
> At τ = 2 s the holistic SENS_C is min(0.40, 0.24) = 0.24, and `power.py --tau2-priors` (`power_tau2.txt`) detects a
> p_H 0.5 bypass at 0.727 at K = 5 and **0.397 headlined** (at K and K + 2), below the 0.8 bar. At τ = 1 s the priors
> are r7's (0.48 / 0.32), and `power.py` on the current code (`power_tau1.txt`, byte-identical to r7's `power.txt`)
> gives r7's registered **0.847 at K and 0.793 headlined**. r7 registered τ = 1 s before any RBT-116 data, and its power
> claim was built on it; Amendment 1's move to 2 s had no RBT-116 reason. So τ = 1 s is kept (Amendment 1, revised).
> SENS_1 and every other rate are still measured at the gate, on the channel at τ = 1 s.
>
> **Disclosure.** RBT-125's gate ran a descriptive τ = 1 s sensitivity cell (PW-G2.5-tau1, `runs/RBT-125/gate/`), in
> which an installed compass was paid more than at τ = 2 s. **That datum is not the basis for keeping τ = 1 s**, and it
> answers a different question (the channel's prize, not this instrument's sensitivity). The basis is the fixture
> probe above and r7's registered power.
>
> **r7 L265 (§1.3, "one-nose steering below F_MIN is excluded by design, not missed") stands at τ = 1 s.** For the
> record (the adversary's S-S1): at τ = 2 s a moderate-gain one-nose steerer (steer1 k 8) earns F +0.30, above F_MIN,
> and is never confirmed, so at τ = 2 s that sentence would not hold. It is moot at the registered τ.
>
> **3. The decoy clears the world's clearance points (S-M1).** §1.1's decoy row re-draws θ until no rotated live item
> lies within the clearance of **the points the world's own clearance rule measures from at spawn**
> (`Simulation._clearance_points()`): the root under `clear_from=root`, every geom centre under `clear_from=geoms`, and
> the 3-D distance to every geom's surface under `clear_from=geoms` with `eat_rule=surface`. r7's "of the root at
> spawn" let 35–37% of decoy seasons put a phantom item within 0.8 m of a geom centre under `clear_from=geoms`, where the
> real layout never can (`design-adversary/steer_real_checks.txt` A).
>
> r7 text is kept struck through in place, with the amended text marked **[A2]**.

***Design only; no arm may run.*** *Any arm is gated on all of these:*
- *the code prerequisites of §3.2: RBT-120's gear budget, the ball cone and hinge ranges, the smell transform flag,
  `eat_from`, and settle;*
- *this design's own hooks (§3.1);*
- *the per-world gate (§4.3);*
- *a re-read by the same design adversary;*
- *the coordinator's ruling.*

*Nothing here was simulated except `power.py` → `power.txt` (pure Python). Every number from earlier work is cited to
its committed file or PR head. Places this draft cannot settle are marked **[OPEN]**, with the default it will use.*

---

**The question.** Conrad's (1990) extradimensional bypass says that extra dimensions in a search space open ridges
around valleys that are impassable in a lower-dimensional one. For evolved bodies, those dimensions are body shape
and the number and placement of sensors. The compass strand measured one such valley, on the Pioneer only:
- a lone food sensor wired to the wheels spins the robot, costing −1.502 items per bout [−1.614, −1.375], with 0 of
  7 robots improved (paper 8, L167–172);
- the parts must arrive together, with the right signs;
- the operator proposes the right shape in 84 of 200,000 lineages, and its direction is a coin flip (paper 8, L324,
  L361–372);
- correctly signed, paying proposals arrive at about 1.6–1.9 × 10⁻⁵ per lineage (paper 8, L606–612).

**The bypass predicts that holistic bodies cross where the fixed body cannot.** This design asks whether they do, with
the same selection, the same worlds and the same instrument on both bodies. Either answer is a finding: "holistic
bodies cross no more readily" is registered as a clean, publishable outcome (§6).

**The design in brief.**
- **Instrument (§1).** STEERS is behavioural and body-general:
  - the genome gains food from the *information* in smell (intact against RBT-97's rotated live layout), with F ≥ 0.25
    items per season;
  - it approaches food up the real gradient more than under the decoy (ΔT > 0);
  - its intact and decoy trajectories differ (a trajectory-identity veto);
  - and it **repeats all of this on a confirmation battery.**

  Sensorless and idle-nosed bodies are NONE exactly or in expectation, and planted negatives prove it.
- **Quantity (§2).** How readily steering appears and is held under imposed truncation in `evolve`:
  - starting from each body's own coverage peak **in the world used**: RBT-113's up-line finals plus a 12-generation
    burn-in with lesioned smell;
  - with **mutation-only operators** (crossover pinned at 0 in both faunas);
  - with draws sized so that a steerer at F_MIN outgrows its measured erosion (§2.4).
- **World (§4).** It is **a parameter block**, and each world point gets its own gates and its own verdict. The first
  point, W1, is auditor C's PW layout under a **named** smell transform: a per-robot running-baseline log-contrast at
  G = 2.5. Further points come from the owner's world sweep, if adopted.
- **Nulls (§5).**
  - N is the same selection under decoy smell.
  - Share_N is checked against generation 0's false-positive rate for purging.
  - A corrected proposal assay gives the mutation-only rate.
- **Verdicts (§6).** HOLISTIC or PIONEER MORE READILY now **requires line-level crossing**, by an exact paired test.
  **NEITHER CROSSES** is bounded to what it measures. The loss-ratio and transform covariates are printed with any
  verdict.
- **Power (§7)** at 24 units and 40 members probed, with **confirmed** rates entered directly (never squared),
  plateaus derived from holding, and the holistic sensitivity taken as the smaller of the two-nose and one-nose
  routes. The crossing count is **K = 5** of 40 (and ≥ 5 above N), chosen so that the U/N gap at G4's cap stays
  ≤ 0.01 false HOLISTIC:
  - under the null, NEITHER 0.92 and false HOLISTIC 0.000;
  - with the gap at G4's cap, false HOLISTIC 0.003;
  - a bypass in half the lines, 0.85 (0.93 if steerers are two-nosed); **0.79 headlined**, since a HOLISTIC
    headline must also hold at K + 2 (R6-1);
  - a weak bypass (a quarter of lines), 0.32 [OPEN: G = 72].
- **Cost (§9).** Per world point: about 510 CPU-h at D = 16; about 330 at D = 8; about 320 with `--draws-final 16`
  over D = 4. G6 decides which, and **both costs are registered** for the ruling (R5-5).

---

## 0. How revision 5 answers the design adversary and the ruling

| item | the adversary's finding (§9 wording, abridged) | r5's answer | where |
|---|---|---|---|
| **MUST 1** | the count veto blinds the call in PW (a two-nose steerer at F +1.29 is called STEERS on only 27%; a one-nose temporal steerer on 0%); the fixed draws are unscreened | **The count veto is replaced by a trajectory-identity veto.** The battery's draws are chosen from a 64-draw pool by a registered reachability screen on the positive controls. G8(a) and G8(c) are priced on the new call. | §1.1, §1.3 |
| **MUST 2** | T is undefined when Σ\|v\| = 0; 75% of a real holistic final's ticks are below 0.05 m/s | T's speed threshold is **0.25 × the member's own median CoM speed** (intact season). T := 0 and flagged when no tick qualifies. The excluded-tick share is reported per member. | §1.2 |
| **MUST 3** | G8(b) cannot fail on T because it never pays; it is fed by the root; "orthokinesis leaves T unchanged" is wrong (T ≈ net approach ÷ path) | **The claim is deleted,** and §1.2 states T ≈ net approach ÷ path length, which kinesis can raise by aggregation. G8(b) is now a **tuned, paying** area-restricted-search plant fed by a **wheel** nose: it must reach F ≥ 0.25 and then be called SMELL-USE or NONE, never STEERS. If no kinesis plant can pay, the registration says T is untested there. | §1.2, §4.3 G8(b) |
| **MUST 4** | G6 is the wrong inequality; crossover is missing from erosion; Q is asserted; the H:P loss ratio can decide a HOLISTIC verdict | **`--crossover-rate 0` in both faunas** (a new hook; every cited loss rate is mutation-only). G6 is now **(1 + s(F_MIN))(1 − u_f) ≥ 1.25 for both faunas**, with u_f measured on planted steerers, and D ∈ {8, 16}. **Q_f is derived** by the holding simulation at the measured s and u (`power.py` part 1). **The H:P loss ratio is a registered covariate** with a fixed sentence. | §2.4, §6.3, §7 |
| **MUST 5** | the smell transform is unnamed; every PW number came from C's un-centred model | **Named** (§4.2): a per-robot running-baseline log-contrast, `tanh(G · (ln Σ_i − b_r))`, with b_r the robot's EMA of its mean ln Σ over its food sensors (τ = 1 s, ~~**[A1] τ = 2 s**~~ retained by the A1 revision; **[A1]** floor 10⁻¹² in the log), at G = 2.5. What a lone root nose reads is stated. **No number from C's kinematic model is cited in support.** G1, G2, Δ, G7 and G8 are all measured at the gate on this transform. G8(b) uses a non-root nose. | §4.2, §4.3 |
| **MUST 6** | G7 tests only the pirouette | G7 tests **every one-step intermediate**: pirouette (lone wheel nose → steering axis), lone-nose throttle, same-sign pair, and one-wheel. At 16 hosts × 16 draws, with a paired t bound. It passes only if none pays. | §4.3 G7 |
| **MUST 7** | a U/N false-positive gap gives false HOLISTIC 0.54 | **Every STEERS call must repeat on a 16-draw confirmation battery.** Generation 0's false-positive rate (identical U and N) is printed beside share_N(t), and a fall below it is flagged as purging. | §1.3, §5.3 I8 |
| **MUST 8** | HOLISTIC fires with no line crossed | **HOLISTIC (and PIONEER) MORE READILY require the A test AND an exact one-sided paired test on crossed lines** (discordant units). An A-only result is reported as "INCONCLUSIVE: holistic steers more, no line-level crossing". | §6.3 |
| **MUST 9** | re-run power with EPS_U ≠ EPS_N, derived Q, confirmation and M = 40; print the one-seed row | Done (`power.txt`). The crossing call moves from a share threshold to a count (r5: ≥ 3 of 40 confirmed, and ≥ 3 above N; **r6: K = 5, by R5-1's rule**), because a share of 0.125 is unreachable for a trait held at Q < 0.31 after confirmation's sensitivity. The equivalence margin is rescaled. | §1.4, §7 |
| **SHOULD 1** | a rotated item can land on the spawn | θ is re-drawn from the same stream until no rotated live item lies within the clearance (0.8 m) of the root at spawn. Tested. | §1.1 |
| **SHOULD 2** | the rotation is valid only for rotation-invariant layouts | `--smell-decoy rotate` asserts, at construction, that the food layout rule is rotation-invariant, and refuses otherwise (R15). | §3.1 |
| **SHOULD 3** | is klinokinesis steering? | **Yes, if it approaches food up the real gradient:** STEERS means "uses smell information to approach food", which includes biased-random-walk chemotaxis. The ticket's "directed turning" is restated as "**directed movement toward food**". G8(b) measures whether undirected kinesis alone reaches the T bar. | §1.3 |
| **SHOULD 4 → MUST** | the starts are not at a peak in the world used | **A shared burn-in:** 12 generations of U-style truncation in the world point, with **lesioned smell** and every fix ON, from the RBT-113 finals, per unit and fauna. Its final population is generation 0 of U and N. The start-member rule for failed builds is stated. | §2.2 |
| **SHOULD 5** | what is the holistic "root"? | The root is the body synthesised from Node 0's first instance (`synthesis.py`'s root). A test pins that the Pioneer's root is the chassis. | §3.2 |
| **SHOULD 6** | income lost to root eating | Printed per fauna at the start (before burn-in): the committed rule against root eating. | §4.3 G9 |
| **SHOULD 7** | G7's n, CI and power | 16 hosts × 16 draws, paired t, with power at the expected prize printed. | §4.3 G7 |
| **SHOULD 8** | NEITHER's sentence overclaims | Rewritten: "confirmed steering did not reach and hold ≥ K of 40 members in more than 1 line in 4, on either body." | §6.3 |
| **SHOULD 9** | U − N wiring diagnostics | Nose count, and the share of members with any food-sensor → Effector path of gain > 0.1, per probe, U against N. | §6.4 |
| **SHOULD 10** | the proposal assay misclassifies | Parent and child are called on the **same** draws. The parent must be NONE on a confirmation battery too. The assay's detection floor (about 3 × 10⁻⁴ per child) is stated, and it cannot confirm paper 8's rate. Stage 1 no longer uses a count screen. | §5.2 |
| **SHOULD 11** | B's planted +Δ holding pilot | Part of G6: one unit per fauna, a planted steerer at F ≈ F_MIN, run 24 generations under the registered D. It must be held. | §4.3 G6 |
| **ruling: the world as a parameter** | the owner may adopt a world sweep | §4 is a parameter block. Every world point gets its own G1, G2, G7 and G9, its own power re-run and its own verdict. W1 is PW under the named transform. | §4 |

**Revision 6: the re-read of r5** (`R5-CHECK.md` @ `82211af`) **and the 21:55 ruling.**

| item | finding | r6's answer | where |
|---|---|---|---|
| **R5-1 (MUST)** | G4 caps the *confirmed* false-positive rate, but `power.py` squared EPS again. At G4's cap, a U/N gap reopens false HOLISTIC to 0.63. | **Every rate is a confirmed rate, entered directly and never squared.** G4 is enlarged to **200 members per fauna**, and passes only if the exact upper 95% bound on the confirmed rate is ≤ 0.05. The point estimate is EPS_C. **The crossing count is re-chosen by a registered rule:** K is the smallest value with false HOLISTIC ≤ 0.01 at the gap at G4's cap (0.05 against 0.01), on 600 readouts. On the priors, K = 5. The gap-at-the-cap row is registered. I8 uses the same confirmed EPS_0. | §1.4, §4.3 G4, §5.3 I8, §7 |
| **R5-2 (MUST)** | No positive control for the one-nose route. "The stronger no" is unearned, and at one-nose sensitivities a real bypass reads NEITHER 0.74–0.94. | **New G8(f):** a one-nose temporal plant on every holistic host. Its confirmed share is SENS_1. The holistic power uses **min(SENS_c, SENS_1)**. **"The stronger no" is registered only if** the gate's re-run of `power.py` at that minimum detects a half-lines bypass at ≥ 0.8. Otherwise the NEITHER sentence names the lone-nose sensitivity limit. It is also stated that moderate-gain one-nose run-and-tumble earns below F_MIN in PW (F 0.12–0.14), so it is excluded by F_MIN, not missed. | §1.3, §4.2, §4.3 G8(f), §6.3, §7 |
| **R5-3 (SHOULD)** | G8(b) keyed on a signed contrast is run-and-tumble, which is STEERS | **G8(b) is keyed on \|reading\|:** undirected kinesis under this transform. | §4.3 G8(b) |
| **R5-4 (SHOULD)** | G8(a)'s 50% bar is close to a working instrument's rate | **G8(a)'s bar is relative:** a pooled confirmed share ≥ 0.6 × G1's hosts' confirmed share at the same rung. | §4.3 G1, G8(a) |
| **R5-5 (SHOULD)** | D = 16 costs about 420 CPU-h per point | **`--draws-final K` is built as this design's hook 5** and tested at G6 beside D ∈ {8, 16}. Both costs are registered, and the ruling chooses. | §3.1, §4.3 G6, §9 |
| **R5-6 (SHOULD)** | crossover 0 changes the holistic "default operator" | The operator sentence reads **"mutation-only operators (crossover off in both faunas)"**. | §2.4, §6.3 |
| **R5-7 (SHOULD)** | u_f from hand-built plants may not be evolved steerers' loss | **The evolved u** (the assay's loss rate on U's own STEERS members) is printed beside G6's. If the two differ by more than 2×, `power.py` part 1 is re-run at the evolved value before the readout's `power.txt` is final. | §2.4, §5.2 |

**Revision 7: the 22:05 ruling, R6-1 and R6-2 (binding).**

| item | r7's text | where |
|---|---|---|
| **R6-1** | A HOLISTIC (or PIONEER) verdict is **headlined only if it also holds at K + 2**. Otherwise it reads "INCONCLUSIVE: crossing not robust to a rise in U's false-positive rate". **The U − N SMELL-USE share is printed per probe.** `power.txt` part 2c prices the rule: at the gap at G4's cap, headlined HOLISTIC 0.000; a half-lines bypass, 0.79 (0.91 two-nosed). | §6.3, §6.4, §7 |
| **R6-2** | "The stronger no", and the NEITHER sentence's sensitivity clause, are **evaluated at readout**: at the plateau from the **chosen** draws option, and at the **larger** of the hand-built u_f (G6) and the evolved u (the assay, R5-7), recomputed by `power.py` part 1. If the check fails, NEITHER names the limit, **stating the plateau and SENS_C at which a crossing would have been visible.** | §4.2, §6.3 |
| draws option | Unchanged: the cheapest option that passes G6, with both costs printed (about 310 CPU-h under `--draws-final`, about 510 at D = 16, per world point). R6-2 covers the plateau that is not yet measured. | §2.4, §9 |

Earlier decisions carried forward unchanged:
- the behavioural definition;
- the rotated live decoy;
- root eating over sensor eating;
- `evolve` truncation over the ecology (so the breed order is moot);
- 24 paired units from RBT-113's O and Z starts;
- the default operators, at stated unequal erosion;
- the fairness block;
- `--terrain random`, with penetration recorded;
- a motors-off condition;
- the census;
- EQUIVALENT never widened to swallow a bypass.

---

## 1. The instrument: what "crossing the valley" means on any body

### 1.1 The battery and its draws (`steer.py`, written after the ruling)

- **Solo seasons** in the world point (§4), with every fairness row ON (§8).
- **The draw pool.** 64 candidate draws (terrain seed, start seed) are fixed in the file per world point.
- **The reachability screen** (MUST 1, M2). Before any arm, the positive-control hosts of G8(a) and G8(c) run every
  pool draw intact. A draw is **admissible** if at least half of those hosts eat ≥ 1 item on it. The admissible draws,
  in pool order, are assigned:
  - stage 1: 4 draws;
  - stage 2: 16 draws;
  - confirmation: 16 draws.

  If fewer than 36 draws are admissible, the pool is extended by 32 more draws, once. If that still fails, the world
  point fails its gate. The per-draw reachability table is committed.
- **Conditions,** on the same draws:

| condition | the `food` sensors read | everything else |
|---|---|---|
| **intact** | the real field, through the world's transform | unchanged |
| **decoy** | the **live** layout rotated about the world origin by θ ~ U[30°, 330°], drawn per draw from a registered stream, and ~~**re-drawn until no rotated live item lies within 0.8 m of the root at spawn**~~ **[A2] re-drawn until no rotated live item lies within 0.8 m of the world's clearance points at spawn** (the root, every geom centre under `clear_from=geoms`, or every geom surface under `eat_rule=surface`) (SHOULD 1; S-M1). The rotation is applied to item positions **before** the transform. | unchanged: eating, regrowth, depletion and the real items |
| **lesion** | 0 ~~(before the transform: the raw sum is set to the transform's zero-information value, so a lesioned nose reads a constant)~~ **[A1]** (`FoodConfig.smell_lesion`: every food sensor reads the channel's zero-information constant, exactly 0, from the first tick) | unchanged |
| **motors-off** | the real field | every actuator command held at 0 (A3's null for "moves by itself") |

- Only `food` is patched. `agent` reads 0 solo.
- The patch is on the field, not the wiring, so it is identical on any body. The decoy's validity needs a
  rotation-invariant layout: the arena disc and the patch centres, uniform in the disc about the origin. The hook
  asserts this (SHOULD 2).

### 1.2 What each season records

- `food` (items eaten) and `work` (in yield units);
- `cells`: distinct 0.35 m xy cells under any geom, and items per 100 new cells (C7);
- `traj`: the root's xy path, hashed per tick to 1e-9, for the trajectory veto;
- `disp_off`: CoM displacement in the motors-off season;
- `pen`: the deepest contact penetration (H71);
- **T, the chemotaxis index** (MUST 2):
  - v is the CoM horizontal velocity per control tick. ĝ is the unit gradient, at the CoM, of the **real, untransformed**
    field Σ exp(−d/decay), computed analytically. The transform changes what a nose reads, not where food is.
  - Ticks are included if |v| > v_min = **0.25 × the member's median |v| in its intact season on that draw.** The same
    v_min is used for that draw's decoy season, so the pair is compared on the same speed bar.
  - T = Σ|v| cos∠(v, ĝ) / Σ|v| over included ticks. **If no tick is included, T := 0 and the draw is flagged.**
  - The excluded-tick share and the flagged-draw count are reported per member.
  - **T needs no direction of travel** (H35). A body moving backwards, sideways or rolling is scored the same way.
- **What T measures** (MUST 3). Σ|v| cos∠(v, ĝ) Δt = ∫ĝ · dx, which is the net approach up the gradient; for one
  source it is exactly −Δ(distance). So **T ≈ net approach ÷ path length.**
  - It is *not* invariant to kinesis. A walker slowed where the reading is high aggregates there, and that is net
    approach.
  - The draft-1 claim that orthokinesis leaves T unchanged is withdrawn. Whether undirected kinesis can clear the T
    bar in a given world is measured by G8(b).

### 1.3 The call

**Stage 1 (screen).** On 4 draws, intact and decoy. A genome goes on to stage 2 unless its intact and decoy
trajectories are **identical on all 4**.
- There is no food-count screen. It missed real steerers whenever all 4 draws tied (the adversary's §5(d)).
- A sensorless or idle-nosed genome stops here exactly.

**Stage 2 (call).** On 16 draws, all four conditions. Per genome:
- **F** = mean(food_intact − food_decoy): the food gained from smell *information*, in items per season;
- **ΔT** = mean(T_intact − T_decoy);
- **L** = mean(food_intact − food_lesion), and the motors-off food, reported only.

**A genome PASSES** iff all three hold:
1. F ≥ **F_MIN = 0.25**, and the one-sided 95% t lower bound on F is > 0;
2. the one-sided 95% t lower bound on ΔT is > 0;
3. **the trajectory-identity veto** (MUST 1): intact and decoy root trajectories differ (by more than 1e-9 at some
   tick) on more than half of the 16 draws. This is what "smell changes nothing" means. It catches every sensorless
   or unused-nose genome exactly, and it does not penalise a steerer that ties on food because no patch was in reach.

**A genome STEERS** iff it PASSES on stage 2 **and PASSES again on the 16 confirmation draws** (MUST 7).
- A genome that meets 1 and 3 on stage 2 but fails 2 is **SMELL-USE**, which is reported and not a crossing.
- Everything else is **NONE**.

**What STEERS includes** (SHOULD 3). STEERS means "uses smell information to approach food": food gained from
information (F), and net up-gradient approach beyond the decoy's (ΔT), repeated.
- This includes biased-random-walk chemotaxis (klinokinesis that produces net approach), because that is how a
  one-nosed body with temporal smell steers. It is also why §4.2's transform is chosen with care.
- The ticket's "directed turning toward food" is restated as **"directed movement toward food"**.
- Whether *undirected* kinesis can pass is tested by G8(b), not assumed.
- **One-nose steering below F_MIN is excluded by design, not missed** (R5-2). In the adversary's PW caricature under
  this transform, one-nose run-and-tumble at moderate gains earns F +0.12 to +0.14 (`r5_probe.txt`, steer1 k 2 and
  k 8). That is below F_MIN, so it is not STEERS whatever the noise. Only strong one-nose steering (k 32, F +0.56)
  clears the bar, and G8(f) measures how often the call confirms it.

**F_MIN.** 0.25 is about the size of kinesis noise between real and decoy smell (RBT-106 F6). **[OPEN]** Its
absolute form is kept. The relative variant, max(0.25, 0.2 × food_intact), is printed beside the call.

### 1.4 From individuals to lines

- All **M = 40** members of a line are probed at generations 12, 24, 36 and 48 (MUST 9). share(t) is the fraction
  that STEER.
- **A_f** = mean over those t of [share_U(t) − share_N(t)], per unit and fauna: the time-averaged, null-corrected
  share. "More readily" means sooner and more often.
- **A line has CROSSED** if, at generation 48, U has **≥ K confirmed steerers of 40, and ≥ K more than N,** with
  **K = 5** on the priors.
  - **K is set by a registered rule** (R5-1): the smallest K at which the U/N false-positive gap at G4's cap (a
    confirmed 0.05 in U against 0.01 in N, holistic) gives false HOLISTIC ≤ 0.01, on 600 readouts of `power.py` part
    2a. The rule is re-run at the gate with the measured EPS_C and SENS_C, and the K it returns is registered before
    any arm.
  - **Why a count, not a share.** After confirmation a true steerer is called STEERS with the confirmed sensitivity
    SENS_C (about 0.3–0.5), so a share threshold would be unreachable for a trait held at a moderate plateau.
  - **Why K = 5, not 3.** At a confirmed false-positive rate of 0.05, 3 of 40 is reached by chance in about a third of
    lines, and the U/N gap then gives false HOLISTIC 0.63 (R5-1). At K = 5 it gives 0.007 (`power.txt` 2a).
  - **What it costs:** a real bypass at a low plateau or a low sensitivity is detected less often (§7), and NEITHER's
    sentence is bounded to say so.

## 2. The measured quantity, and the protocol

### 2.1 Why "appears and is held under selection" is primary

| candidate | measures | role |
|---|---|---|
| (i) proposal rate under mutation alone | how near steering genomes are, in the operator's geometry | **secondary**: the assay, §5.2 |
| (ii) appearance and hold under selection | proposal × conversion: the bypass's operational prediction | **primary** |
| (iii) valley depth | the cost of intermediate steps | **descriptive**, §6.5; and, on the Pioneer, gate G7 |

Conrad's claim is about ridges: paths along which fitness does not fall. A high proposal rate into a deep valley does
not cross it, and only (ii) integrates both. (iii) needs intermediates, which on an arbitrary body only a wiring
motif could name. So it is descriptive for the holistic body and gated for the Pioneer.

### 2.2 `evolve` with imposed truncation; the starts; the burn-in

**Why `evolve`, not the ecology.**
- In the ecology the pull on a paying compass is s = 0.01 [0.00, 0.08] (RBT-112).
- Unseeded arrivals are about 0.26 across all ten 600-season arms combined (RBT-102 L140–142).
- Its breeding lottery is near-neutral above the birth threshold (auditors C1 and B4), and energy order costs depth
  (the audit adversary).
- `evolve --truncation 0.25 --line up` (RBT-113) ranks on fitness directly, with discrete generations and solo
  scoring, and **both faunas share every generation's worlds in one run.** The breed order is moot here.

**Starts.** Each unit j = 1 … 24 is one RBT-113 seed directory, `O1/1` … `O4/12` and `Z1/Z1` … `Z4/Z12`: its holistic
and designed **up-line final** populations (40 each), restored from `ckpt/rbt-113-*`.
- In RBT-113's world both learned to eat by moving, not smelling (ADVERSARY §4).
- The Z holistic lines are independent replicates. The Z designed lines are coverage foragers evolved under frozen
  global biases.
- Start type (O or Z) is a registered sensitivity split.

**The burn-in (SHOULD 4, ruled MUST).** The starts are coverage foragers of *another* world, and under the fixes they
are rebuilt unequally (A2–A5 rebuild holistic bodies; root eating removes their limb mouths). So, per unit:
- **B:** 12 generations of U-style truncation, in the world point, with every fix ON and **smell lesioned** (§3.1,
  `--smell-decoy zero`), from the RBT-113 finals.
- **B's generation-12 population is generation 0 of both U and N.** It is the coverage peak **in the world used**,
  for both bodies, reached by the same selection.
- Burn-in costs 12 generations per unit, against U's and N's 96.

**Start members that fail to build** under the fixes (over the gear cap, over `max_extent`, or unbuildable after
`outward_limbs`) are **clamped at build** where the fix clamps. Where it rejects, the member is replaced by a copy of
a buildable member of the same start population, drawn by a fixed rng. Per fauna, the count clamped and replaced is
reported. The burn-in absorbs the transient either way.

### 2.3 The Pioneer's floor, and the world's risk to it

A 48-generation line of 40 has about 1,920 births. In the committed worlds, at about 2 × 10⁻⁵ correctly signed,
paying proposals per lineage, p_P ≈ 0.04 lines would cross. **That is the valley, not a flaw.**
- But a world that pays small nose steps may also flatten the Pioneer's valley. If it does, "both cross" becomes
  likely, and that reads INCONCLUSIVE 0.95–0.98 at n = 24 (`power.txt`).
- The world must therefore **pay the peak but keep the valley**. G2 checks the peak and G7 checks the valley, **per
  world point** (§4.3).

### 2.4 Holding: crossover, erosion, draws and plateaus (MUST 4)

- **Crossover is pinned at 0 in both faunas** (`evolve --crossover-rate 0`, a new hook, §3.1).
  - Every loss rate in this design is mutation-only: paper 10's u, auditor B's route loss, B's `parity.py`, and the
    assay.
  - At the committed 0.5, the holistic prefix crossover disrupts routes at an unmeasured rate. `hold.txt` shows that
    this alone moves P(cross) at Δ 0.25 from 0.175 to 0.043.
  - A crossover arm is **[OPEN]** for a later wave, with its loss measured first.
- **Erosion u_f** is measured at the gate (G6), on planted steerers of each fauna: G8(a) Pioneer compass hosts, and
  G8(c) tuned holistic plants.
  - Each host gets 40 children by its fauna's operator at crossover 0. u_f is the share of children of STEERS parents
    that are not STEERS, with parent and child called on the same draws.
  - The priors are B2's 0.146 (holistic route) and paper 10's 0.28 (designed compass).
- **Selection** on a steerer at Δ = F_MIN is s_f ≈ 1.27 Δ/σ_P,f(D). σ_P is measured by B's `noise.py` method on the
  burn-in's final members, at D ∈ {4, 8, 16}.
- **The draws rule (G6):** D is the smallest of **{8, 16}** at which **(1 + s_f)(1 − u_f) ≥ 1.25 for both faunas**.
  - The margin is 0.25, not 0.10, because the holding simulation shows a lineage growing at 1.20 per generation still
    plateaus at Q ≈ 0.14 under truncation. Q ≈ 0.50 needs about 1.39 (`power.txt` part 1).
  - If neither passes, D = 16, and the headline carries: "at the registered draws, a steerer at F_MIN grew by only
    (1 + s)(1 − u) = … per generation on the [fauna]; a NEITHER verdict is conditional on that."
  - Both faunas share one D, because they share every run.
- **Plateaus.** Q_f is derived by `power.py` part 1 (the adversary's `hold.py`, transcribed at crossover 0) from the
  measured σ_P, u_f and D, and `power.py` is re-run before launch. On the priors, D = 16 gives Q_H ≈ 0.70 and
  Q_P ≈ 0.50. D = 8 gives 0.61 and 0.14.
- **The H:P loss-ratio covariate.** The assay measures each fauna's loss rate on its own lines (§5.2). **If a HOLISTIC
  verdict fires with u_H < 0.5 × u_P**, it carries: "consistent with lower erosion of steering under the holistic
  operator; the comparison is at each body's default operator." Symmetrically for PIONEER.
- **Mutation-only operators** (R5-6). Each fauna uses its default *mutation* operator (`mutate` /
  `mutate_controller`), with crossover off in both. The bypass is a claim about the holistic space *as explored by its
  operator*, so the headline states: "at mutation-only operators (crossover off in both faunas); realised
  u_H = …, u_P = …".
- **Evolved u** (R5-7). The assay's loss rate on U's own STEERS members (§5.2) is printed beside G6's hand-built u_f.
  If the two differ by more than 2× on either fauna, `power.py` part 1 is re-run at the evolved value, and the readout's
  `power.txt` uses it.

## 3. The mechanism

### 3.1 This design's hooks (a code PR after the ruling; each off by default and byte-identical when off, with digests on the pre-hook code)

1. **`evolve --from-population KIND=DIR`.** Start a fauna from a saved population, exactly as saved: no weight redraw,
   and N must equal the saved count.
2. **`evolve --save-every K`.** Write each fauna's population at generations divisible by K (bulk, to the checkpoint
   branch).
3. **`--smell-decoy rotate|zero`** (`evolve` and `Simulation`).
   - `rotate`: RBT-97's `RotatedSmell`, promoted. θ comes from a registered stream keyed on the season's start seed
     (shared across faunas and the paired worlds), with the spawn-clearance re-draw (SHOULD 1). The rotation is
     applied before any transform. It **refuses a layout rule that is not rotation-invariant** (SHOULD 2).
   - `zero`: the lesion, used by the burn-in and the battery.
   - Tests: eating, regrowth and the real items are untouched; a sensorless genome runs byte-identically under both
     modes.
4. **`evolve --crossover-rate R`** (MUST 4), passed to `EvolutionConfig.crossover_rate`. The draw at
   `evolution.py:501–503` is still made at R = 0, so the random stream is unchanged. The committed default (0.5) is
   byte-identical.
5. **`evolve --draws-final K`** (R5-5; auditor B's proposal). Before truncation, the members ranked k − 5 to k + 5 on
   the D-draw mean are re-scored on K extra draws, shared by the generation, and ranked on all D + K draws. Off by
   default, with no extra draws made, so the run is byte-identical. Tests: identical rankings off; the boundary set is
   exactly ranks k − 5 … k + 5; the extra draws are shared across faunas and lines.

### 3.2 Gated prerequisites (each through its own designer, adversary and ruling)

| prerequisite | source | required? | could it change the answer if mis-built? (adversary §7) |
|---|---|---|---|
| gear budget; the Effector-bias walk bounded **in both operators** | RBT-120; A1, B1 | **required** | moderately: a cap that clamps holistic motors changes coverage speed, steering's competitor |
| **the smell transform, as named in §4.2** | C §2; audit adversary §6b; MUST 5 | **required** | **yes, in either direction**: hence named, and its bias stated (§4.2) |
| `eat_from=root`, with **root = the body synthesised from Node 0's first instance**, tested so that the Pioneer's root is the chassis (SHOULD 5) | C §4 | **required** | yes: it decides how much holistic income survives |
| `ball_cone` + hinge ranges (the load-bearing ghost fix) | A2; audit adversary §2 | **required** | yes, via the starts; the burn-in absorbs it |
| `settle_until_rest` | A3 | **required** | little |
| `outward_limbs` (orientation clamp; orientation mutation is unclamped at `genetics.py:209`) | A2 | wanted | via the starts |
| `cap_on_reachable` | A4 | wanted | via the starts |
| `max_extent` 0.6 m, `clear_from=geoms` | A5 | wanted | small; it interacts with the decoy's clearance |
| `--draws-final K` | B3; R5-5 | **built here** (§3.1, hook 5) and tested at G6 | yes, through holding |
| `--structural-rate-scale K` | B2b | not in this wave | — |

**"Required" means the design waits for it.** The coordinator may downgrade a row to "reported instead" before launch,
and the readout states it. **A "wanted" row not merged** is reported per member: embedded pairs, recessive nodes, span
and footprint.

## 4. The world, as a parameter block

### 4.1 The block

A **world point** W is one fixed set of values for these parameters:

| parameter | W1 (the first point) |
|---|---|
| food layout | `--food-items 12 --food-patches 2 --patch-radius 0.4 --food-radius 4.0 --regrow-delay 60` (own-spot regrowth, beyond the 15 s season) |
| smell | `--smell log --food-decay 1.5`, plus the transform of §4.2 at **G = 2.5** (**[A1]** `--smell-contrast 2.5 --smell-tau 1.0`, τ set explicitly; ~~`--smell-tau 2.0`~~) |
| eating | `--eat-radius 0.35 --eat-from root` **[A1, item 6]** `--eat-rule surface` (RBT-125's re-ruled rule) |
| price | `--work-cost 0.03` |
| terrain | `--terrain random --random-start` |
| season | `--duration 15` |
| everything else | the fairness block (§8), identical at every point |

- **Each world point is a separate registered comparison.** It has its own gate (§4.3: G1, G2, G6, G7, G8, G9), its
  own draw pool and screen, its own `power.py` re-run, its own 24 units, and its own verdict.
- Points are **not pooled**. If the owner's world sweep (terrain × work price × patchiness × smell contrast) is
  adopted, RBT-116 runs at the 2–3 sweep points the coordinator names. Each is registered by adding a column to the
  table above, before any of its arms.
- A point that fails its gate is reported as "world point failed the gate: [row]". It is not run.
- **W1 is PW's layout under the named transform, not "PW" as auditor C measured it.** C's model applied a raw gain to
  the two-nose difference (the adversary's §2.3), so no C number is cited for W1 (MUST 5). Everything W1 pays is
  measured at its gate.

### 4.2 The smell transform, named (MUST 5; the audit adversary's §6b)

For food sensor i on robot r at control tick t:
- ~~Σ_i(t) = Σ_items exp(−d_i/decay) + 10⁻⁶, over live items, at the sensor's geom centre in xy (the committed
  `_intensity` sum, before any squash);~~
  **[A1]** Σ_i(t) = Σ_items exp(−d_i/decay) + **10⁻¹²**, d_i the xy distance from the sensor Part's geom centre (parked
  items contribute 0). This is the channel's own sum (`Simulation._log_smell`), not the legacy `_intensity`;
- ℓ_i(t) = ln Σ_i(t);
- ~~b_r(t) is the robot's **running baseline**: an exponential moving average, time constant **τ = 1 s**, of the mean of
  ℓ_i over its food sensors. It is initialised at t = 0 to that mean, so every nose reads 0 at spawn;~~
  **[A1]** b_r(t) is the robot's **running baseline**: an exponential moving average, time constant **τ = 1 s**
  (~~τ = 2 s~~, struck by the A1 revision; `smell_tau: 1.0` set explicitly)
  (factor 1 − e^(−Δt/τ) per control tick), of the mean of ℓ_i over **every food Sensor of the robot**. It is
  initialised to that mean on the robot's **first control tick of the season** and advanced before the noses are read.
  So on that tick a lone nose reads exactly 0, and each of several noses reads its spatial offset tanh(G·(ℓ_i − mean));
- **reading_i(t) = tanh(G · (ℓ_i(t) − b_r(t))), with G = 2.5.**

**What each body's noses read:**
- **A lone nose** (any Part, **including the root**) reads the temporal contrast of its own reading against its recent
  past, ≈ G·τ·d(ln Σ)/dt while it moves (τ = 1 s, so G·τ = 2.5 at G = 2.5; ~~**[A1]** τ = 2 s, so G·τ = 5~~).
- **Several noses** each read their deviation from the robot's recent mean: lateral contrast plus temporal contrast.
- **The Pioneer's three noses** (chassis and two wheels) all read live signals. The chassis nose is **not** zeroed.
- ~~**Lesion** sets Σ_i to a constant for every sensor, so every reading decays to 0.~~ **[A1]** **Lesion**
  (`FoodConfig.smell_lesion`) makes every food sensor read the zero-information constant, exactly 0, from the first tick.

**Why this transform, and which way it leans.** It meets r4's four requirements:
1. no root nose is zeroed;
2. single-nose and temporal smell stay informative;
3. it is the same transform on every sensor of every body;
4. the decoy rotation happens before it.

Root-centring (C's first form) fails 1 and 2. It would blind the Pioneer's chassis nose, every holistic root nose, and
any throttle plant fed by the root.

The price is a stated lean. **The running baseline turns every lone nose into a temporal-gradient detector,** which
favours one-nosed bodies, and those are mostly holistic (the adversary's §2.3). It also changes paper 8's pirouette
arithmetic on the Pioneer, which is why G7 re-measures the valley on it. The registered consequences:
- a **HOLISTIC** verdict carries: "under a smell transform that makes a lone nose a temporal-gradient sensor";
- a **NEITHER** verdict under it is the *stronger* "no": the transform was generous to the bypass. **This sentence is
  registered only if G8(f) shows the call can see lone-nose steering** (§4.3: the re-run detects a half-lines bypass
  at ≥ 0.8 at min(SENS_c, SENS_1); R5-2). **The check is re-evaluated at readout** (R6-2): at the plateau from the
  chosen draws option, and at the larger of G6's hand-built u_f and the assay's evolved u, through `power.py` part 1,
  with the same ≥ 0.8 criterion and the headline rule at K + 2. Otherwise the NEITHER sentence instead adds: "steering through a lone nose was
  below the instrument's confirmed sensitivity (SENS_1 = …), so this NEITHER does not cover that route; a crossing
  would have been visible at a plateau of … and a confirmed sensitivity of …" (R6-2).

**[OPEN]** A level-plus-centred two-channel alternative is the transform designer's option. If it is chosen instead,
this section is rewritten before the gate, and no gate result carries across.

**G ∈ {2.5, 10}.** G = 2.5 is primary. At G = 10, contrasts saturate (median |c| about 0.6) and later nose steps pay
about 2% (the audit adversary's §6b). G = 10 is used only if G = 2.5 fails G2 and G = 10 passes both G2 and G7, and it
is then a different world point, with its own column.

### 4.3 The per-world gate (pre-launch; `gate.py`, after the ruling; every fairness row ON, through `steer.py`)

| | check | pass |
|---|---|---|
| **G1** | **Perception pays, on the Pioneer.** RBT-106's routed compass installed at a ∈ {2, 6, 16, 32}, signed per host by its measured travel direction (`scripts/travel_direction.py`, H35), in 16 burn-in-final designed hosts from 16 units. 16 stage-2 draws. | Some rung has a mean F with a lower bound > 0, and at the smallest such rung (the **first paying rung**) ≥ 12 of 16 hosts PASS on stage 2. The hosts' **confirmed** STEERS share at that rung, c_G1, is recorded for G8(a)'s bar (R5-4). |
| **G2** | **Perception beats coverage, in this world with every fix ON.** The first paying rung's F on the G1 hosts, against the coverage gain the burn-in bought: burn-in-final blind yield minus RBT-113-final blind yield, both measured here. | F ≥ that coverage gain. **[OPEN]:** a weaker G2 (≥ 0.5×) needs the coordinator's ruling. |
| **G6** | **Holding** (§2.4). σ_P by B's `noise.py` method at D ∈ {4, 8, 16}, **and under `--draws-final 16` over D = 4** (R5-5), on burn-in finals. u_f from 40 children of each STEERS host of G8(a) and G8(c), same draws, crossover 0. **SHOULD 11:** B's planted-Δ pilot: one unit per fauna, 8 planted steerers at F ≈ F_MIN, 24 generations of U at the chosen D. | Sets D by (1 + s_f)(1 − u_f) ≥ 1.25. For `--draws-final`, s_f is computed at the truncation boundary, where it acts. Every passing option is printed with its cost (§9); the cheapest passing option is the default, and the ruling may choose another. The pilot's steerers must be held: confirmed share at generation 24 ≥ 0.25 × the confirmed sensitivity. Otherwise, conditional-sentence mode (§2.4). |
| **G7** | **The Pioneer's valley is still there** (MUST 6, SHOULD 7). On the G1 hosts, at the first paying rung's gain, 16 hosts × 16 draws, each against the unmodified host: **(i)** the pirouette (one wheel nose → a global unit → both drive Effectors, the steering axis; paper 8's c); **(ii)** the lone-nose throttle (one wheel nose → the difference axis); **(iii)** the same-sign pair (both wheel noses + → one unit → both Effectors); **(iv)** one wheel (one wheel nose → that wheel's Effector only). Both signs of each. | Passes only if **no intermediate has a paired-t lower bound > 0** on its prize. Its power to detect a prize of +0.10 at 16 × 16 is printed (SHOULD 7). The full table (rungs × intermediates) is printed as the Pioneer's valley in this world. If G7 fails, the valley is not there, and the point is reported as such, not run. |
| **G8** | **The call can fire, and stay silent, on the arms' own hosts** (R7). 4 designed and 4 holistic burn-in-final hosts from every unit (192): **(a)** the Pioneer compass plant at the first paying rung; **(b)** **a paying kinesis plant (MUST 3)**: one **wheel** nose → a global unit keyed on the **magnitude \|reading\|** (R5-3: under this transform a signed reading is run-and-tumble, which is STEERS) and thresholded → throttle (slow) and a fixed-sign turn (turn more above the threshold): area-restricted search with no heading term, tuned over threshold × gain × turn sign on 4 screening draws to maximise F; **(c)** the holistic tuned plant: two food sensors on the two expressed Parts of distinct Nodes most separated across the host's measured CoM heading, a global unit fed ±, linked ±w to the Effectors either side, 2 signs × w ∈ {4, 16, 64}, best by F on screening draws; **(d)** a sensorless full-throttle tumbler (A's S2 rod, hinge and ball variants); **(e)** the same bodies with two **unwired** food sensors; **(f)** **a one-nose temporal plant on every holistic host** (R5-2): one food sensor on the host's most-moving expressed Part (the largest mean geom speed in one intact season), ~~a global unit on its reading, and a turn command ±w to the Effectors on one side of the measured heading, 2 signs × w ∈ {4, 16, 64}, best by F on screening draws.~~ **[A2]** a global **rectified** unit (`relu`) fed by its reading at input weight −g, g ∈ {32, 128}, and a turn command ±w to the Effectors on one side of the measured heading, 2 signs × 2 gains × w ∈ {4, 16, 64}, best by F on screening draws; the planter is shown to steer on the fixture world before any gate cell (S-M4). | **(a)** STEERS (confirmed) on a pooled share ≥ **0.6 × c_G1** (R5-4: relative to G1's hosts at the same rung, not a fixed 50%). **(b)** Among hosts where it reaches F ≥ 0.25, **0 STEERS**. If it reaches F ≥ 0.25 on fewer than 4 hosts, the registration states that undirected kinesis cannot pay in this world, so T's discrimination is untested but unneeded here. **(c)** STEERS on ≥ 20% of holistic hosts pooled, and on ≥ 1 host in ≥ 18 of 24 units. **(d)** and **(e)**: NONE on every body. **(f)** is not pass/fail; its confirmed share is **SENS_1**. `power.py` takes SENS_C,P from (a) and **SENS_C,H = min((c), (f))**, and EPS_C from G4. **"The stronger no" (§4.2) is registered only if** the re-run detects a half-lines bypass (p_H 0.5) at ≥ 0.8 at that SENS_C,H. On the priors, that needs SENS_C,H of about 0.30 or more (`power.txt` 2a). More than 4 units flagged: no launch. |
| **G4** | **False positives, confirmed** (R5-1). `steer.py`, with the confirmation battery, on **200** burn-in-final members per fauna, all four conditions. | The **exact upper 95% bound on the confirmed false-STEERS rate is ≤ 0.05** per fauna (that is, about 4 or fewer of 200). The point estimate is EPS_C for `power.py`, and K is re-chosen by §1.4's rule. Every zero-food-sensor genome gives identical trajectories, so it is NONE. |
| **G5** | **Timing.** 2 generations of one unit's U at the chosen D. | Seconds per generation are recorded, and §9 is re-costed. |
| **G9** | **The census, and side effects** (R4, R6; SHOULD 6). In W, HP and RBT-113's world, on the same draws: RBT-113 founders, RBT-113 U finals (intact and blind), burn-in finals, and the G8(a) planted Pioneers. | Printed: food, work, net, cells, items per 100 cells, speed, and solvency (the share with net > 0). **Per fauna, the income lost from the committed eating rule to root eating** on the RBT-113 finals (SHOULD 6). A body-asymmetric move > 25% is named "not the only difference" in the headline. |

(r3's G3, a hand-built holistic compass, is subsumed by G8(c), which plants on the arms' own hosts.)

## 5. Arms, lines, nulls

### 5.1 One arm = one unit

Per unit j (1 … 24) and world point W, three `evolve` runs in sequence. Each carries both faunas.

| run | selection | smell during evolution | generations | start |
|---|---|---|---|---|
| **B** (burn-in) | truncation 0.25, up, on solo net yield | **lesioned** (`--smell-decoy zero`) | 12 | RBT-113 U finals, `--from-population` |
| **U** | the same | real | 48 | B's generation 12 |
| **N** | the same | **rotated decoy** (`--smell-decoy rotate`) | 48 | B's generation 12 |

**Shared by all three runs:**
- the evolve seed 116000 + j, N = 40 per fauna, D from G6;
- **`--crossover-rate 0`**, `--elites 0`, solo throughout;
- the world point's block, the fairness block, and `--save-every 12`.

It follows that U and N share generation 0 and every generation's worlds. Both faunas share them too.

### 5.2 Nulls, and the proposal assay

- **N: the primary null.** It holds constant the selection, the input statistics (a rotated live layout) and the
  currency, and removes only smell's information. It also **taxes nose use**, because misinformation is costly: the
  adversary's second channel. The confirmation battery (§1.3) makes that channel matter little (`power.txt`: the EPS
  gap rows), and control I8 watches it.
- **The proposal assay (quantity (i); SHOULD 10).** At U's saved generations 0, 12, 24, 36 and 48, every member gets
  one child by its fauna's operator at crossover 0.
  - Parent and child are called **on the same draws** (stage 2 and confirmation).
  - The **proposal rate** is the share of children that STEER among parents that are **confirmed NONE**. The **loss
    rate** is the share of children of STEERS parents that are not STEERS: the **evolved u** per fauna, behind §2.4's
    covariate and R5-7's check against G6's hand-built u_f.
  - Both come with exact CIs and never enter a verdict.
  - **Detection floor:** about 9,600 children per fauna bound a proposal rate only above about 3 × 10⁻⁴. The assay
    cannot confirm paper 8's 2 × 10⁻⁵, and says so.
- **The decoy inside each genome's call** is the per-individual null.

### 5.3 Controls (`readout.py`; VOID per fauna and scope, as in RBT-113 §6)

- **I1.** Every probed genome with no food sensor has identical intact and decoy trajectories, so it is NONE. One
  exception voids the instrument.
- **I2.** The configs are the registered ones. B, U and N differ only in `--smell-decoy` and `--from-population`.
  Crossover is 0 in all.
- **I3.** U's and N's generation 0 are identical (names and fitness) and equal B's generation 12.
- **I4.** The worlds are shared: `(terrain_seed, start_seeds)` per generation is identical across U and N.
- **I5.** Every U, N and B parent is in the top k of its generation.
- **I6.** Complete: every run has all its generations, and U and N have saved populations at 12, 24, 36 and 48.
- **I7.** The unit's own G8 results are carried in. A flagged unit is dropped in a registered sensitivity.
- **I8 (MUST 7; R5-1).** EPS_0, the **confirmed** false-STEERS share at generation 0 (identical in U and N; the same
  confirmed quantity as G4's EPS_C), is printed beside
  share_N(12 … 48) per fauna. If share_N(t) < EPS_0 minus its binomial 95% bound, pooled over units, it is **flagged as
  purging**, and the verdict carries "N may understate U's false-positive rate".

## 6. Statistics and verdicts (`readout.py`; constants fixed before any data)

### 6.1 Per unit and fauna

- A_f (§1.4), and crossed_f at generation 48.
- Reported beside them: mean F, ΔT and SMELL-USE share; excluded-tick share; nose supply (≥ 2 food sensors on
  distinct Nodes); food against work at generations 0 and 48; motor class (Σgear/(4 × mass)); penetration.

### 6.2 Across units (n = 24, paired by unit)

- d_j = A_H,j − A_P,j, with mean, t CI and sign-flip p (20,000 draws).
- k_H and k_P, each with an exact one-sided 95% upper bound.
- b and c: the discordant units (H crossed and P did not; P crossed and H did not).

### 6.3 Verdicts, in order (as coded in `power.py`)

1. **HOLISTIC MORE READILY:** the CI on d excludes 0 above, the sign-flip p < 0.05, **and** the exact one-sided
   McNemar p on (b, c) < 0.05 (MUST 8). **It is headlined only if the same three conditions also hold with crossing
   recomputed at K + 2** (R6-1). Otherwise it reads **"INCONCLUSIVE: crossing not robust to a rise in U's
   false-positive rate"**, and the K and K + 2 results are both printed.
2. **PIONEER MORE READILY:** mirrored, with the same K + 2 rule.
3. **NEITHER CROSSES:** the exact upper 95% bound on P(a line crosses) is below 0.25 for both faunas. The sentence is
   (SHOULD 8): *"On neither body did confirmed steering reach and hold ≥ K of 40 members in more than 1 line in 4,
   within 48 generations of truncation selection at mutation-only operators, at world point W."* It is followed by
   §4.2's transform sentence: either the stronger no, or the lone-nose sensitivity limit (R5-2). **That sentence is
   chosen at readout** (R6-2): by `power.py` at the chosen draws option's plateau and the larger of the hand-built and
   evolved u. If detection of a half-lines bypass falls below 0.8 there, NEITHER names the limit and states the plateau
   and the SENS_C at which a crossing would have been visible.
4. **EQUIVALENT:** the CI on d lies inside ±**0.015** and min(k_H, k_P) ≥ 3.
   - Both bodies must have crossed.
   - 0.015 is half the mean d of the weak bypass at this readout.
   - It is kept narrow and almost never fires, which is stated rather than widened.
5. **INCONCLUSIVE: holistic steers more, no line-level crossing:** the A test passes and the crossing test does not.
   Reported as such, never as HOLISTIC.
6. **INCONCLUSIVE** otherwise.

**The headline is fixed in code, one per world point.** It gives:
- the verdict and the design sentence;
- d and each A with CIs, k_H and k_P with bounds, (b, c), and the registered K, with the same at K + 2 (R6-1);
- STEERS and SMELL-USE shares;
- **the covariates:**
  - the operator sentence: "mutation-only operators (crossover off in both faunas)" (R5-6), with the realised u_H and
    u_P (hand-built and evolved), and the loss-ratio sentence (§2.4) when it applies;
  - the transform sentence (§4.2);
  - D, with the conditional sentence (§2.4) when it applies;
  - I8's purging flag;
  - G9's "not the only difference" when it applies;
- **the Pioneer's valley at W:** G7's table;
- the sentence *"The Pioneer's valley is a measured property of the fixed body at this world point; a holistic
  crossing is evidence for the bypass only at this point and depth, and a NEITHER is evidence against it only to the
  stated bound."*

**Registered sensitivities** (reported, no verdict):
- O starts against Z starts;
- F_MIN relative;
- pooled share_N in place of the per-unit N;
- units flagged by G8 dropped;
- members with penetration > 0.10 m excluded. The share dropped is printed per fauna, and a split dropping > 50% of
  one fauna is marked uninterpretable.

### 6.4 R6 and wiring diagnostics (SHOULD 9)

At every probe, U − N per fauna, with CIs:
- food, work, speed and cells covered;
- nose count;
- **the share of members with any food-sensor → Effector path of absolute gain > 0.1;**
- **the SMELL-USE share** (R6-1): a rise in U's SMELL-USE over N's is the signature of a U-side false-positive drift
  that the K + 2 rule guards against.

### 6.5 Valley depth (descriptive)

From the assay and U's probes, per fauna:
- the net yield of SMELL-USE members, and of members with F ≤ −0.25 (smell used against food), against NONE members
  of the same line and generation;
- the net yield of the first STEERS members against their generation's mean.

On the Pioneer, G7's table is the valley. On the holistic body, this is the only depth measure, and it is
descriptive.

## 7. Power (`power.py` → `power.txt`, re-run at the gate with the measured inputs)

**Every rate below is a confirmed rate** (after the confirmation battery), entered directly and never squared (R5-1).
The gate replaces each prior with its measurement: SENS_C,P from G8(a); SENS_C,H = min(G8(c), G8(f)); EPS_C from
G4; u_f and σ_P from G6.

**Part 1: holding** (crossover 0, Δ = F_MIN, B's RBT-113 noise, the priors u):

| fauna | D | u | s | (1 + s)(1 − u) | plateau Q |
|---|---|---|---|---|---|
| holistic | 8 | 0.146 | 0.60 | 1.37 | 0.61 |
| holistic | 16 | 0.146 | 0.72 | 1.47 | 0.70 |
| designed | 8 | 0.28 | 0.66 | 1.20 | 0.14 |
| designed | 16 | 0.28 | 0.93 | 1.39 | 0.50 |

On the priors, G6 picks **D = 16**, or `--draws-final` if it passes. At D = 8 the designed compass grows at only 1.20
and plateaus at 0.14.

**Part 2a: choosing K** (R5-1). Priors: SENS_C,P 0.48 and EPS_C 0.005. The cap cell uses 600 readouts; the others 150.

| K | false HOLISTIC, gap at G4's cap (0.05 vs 0.01) | false HOLISTIC, gap 0.02 vs 0.005 | P(HOLISTIC), p_H 0.5 bypass, SENS_C,H 0.48 / 0.32 / 0.20 | P(NEITHER), same, SENS_C,H 0.20 |
|---|---|---|---|---|
| 3 | **0.628** | 0.007 | 0.95 / 0.84 / 0.73 | 0.000 |
| 4 | 0.125 | 0.000 | 0.95 / 0.89 / 0.72 | 0.000 |
| **5** | **0.007** | 0.000 | 0.90 / 0.85 / 0.47 | 0.047 |
| 6 | 0.000 | 0.000 | 0.95 / 0.80 / 0.30 | 0.113 |
| 7 | 0.000 | 0.000 | 0.94 / 0.75 / 0.06 | 0.380 |

**K = 5** is the smallest K with false HOLISTIC ≤ 0.01 at the cap.
- r5's K = 3 would have given false HOLISTIC 0.63 there, which reproduces the adversary's R5-1 figure.
- Raising K costs sensitivity on weakly detected steerers. At a confirmed 0.20, a half-lines bypass is detected at
  0.47 with K = 5 and 0.06 with K = 7. That is why "the stronger no" is conditional on G8(f) (§4.2).

**Part 2b: the readout at K = 5.** SENS_C,H = min(0.48 two-nose, 0.32 one-nose) = 0.32, SENS_C,P 0.48, EPS_C 0.005,
D = 16's plateaus (Q_H 0.70, Q_P 0.50); 300 readouts per row.

| scenario | HOLISTIC | PIONEER | NEITHER | EQUIV | INCONCL (H steers, not crossed) | INCONCL |
|---|---|---|---|---|---|---|
| null: both at the Pioneer's prior floor (p 0.04) | **0.000** | 0.003 | **0.923** | 0 | 0.003 | 0.070 |
| null: neither ever crosses | 0 | 0 | 1.000 | 0 | 0 | 0 |
| **null + U/N gap at G4's cap (0.05 vs 0.01), registered** | **0.003** | 0 | 0.773 | 0 | 0.210 | 0.013 |
| null + U/N gap 0.02 vs 0.005 | 0.003 | 0 | 0.910 | 0 | 0.040 | 0.047 |
| null + one holistic unit at share 1.0 | 0.000 | 0 | 0.780 | 0 | 0.007 | 0.213 |
| weak bypass, p_H 0.25 | **0.320** | 0 | 0.077 | 0 | 0.060 | 0.543 |
| bypass, p_H 0.5 | **0.847** | 0 | 0 | 0 | 0.030 | 0.123 |
| bypass, p_H 0.5, SENS_C,H 0.48 (two-nose) | 0.930 | 0 | 0.003 | 0 | 0.010 | 0.057 |
| bypass, p_H 0.5, SENS_C,H 0.20 (weak one-nose) | 0.527 | 0 | 0.020 | 0 | 0.193 | 0.260 |
| strong bypass, p_H 0.75 | 0.993 | 0 | 0 | 0 | 0 | 0.007 |
| bypass p_H 0.5, holistic held at the designed u (Q 0.21) | 0.010 | 0 | **0.827** | 0 | 0.070 | 0.093 |
| both cross, p 0.5 each (unequal u) | 0.003 | 0.013 | 0 | 0 | 0.003 | 0.980 |
| both cross, p 0.5, equal u | 0 | 0.040 | 0 | 0 | 0.007 | 0.953 |
| Pioneer more, p_H 0.1, p_P 0.5 | 0 | **0.667** | 0 | 0 | 0 | 0.333 |

**Part 2c: the headline rule at K + 2** (R6-1; 300 readouts):

| scenario | HOLISTIC at K = 5 | headlined (holds at K = 5 and K + 2 = 7) |
|---|---|---|
| null + U/N gap at G4's cap (0.05 vs 0.01) | 0.007 | **0.000** |
| null + U/N gap 0.02 vs 0.005 | 0.000 | 0.000 |
| bypass, p_H 0.5 (SENS_C,H 0.32) | 0.873 | **0.793** |
| bypass, p_H 0.5, two-nose (SENS_C,H 0.48) | 0.927 | 0.913 |
| bypass, p_H 0.5, weak one-nose (SENS_C,H 0.20) | 0.583 | 0.087 |
| weak bypass, p_H 0.25 | 0.307 | 0.227 |

The rule removes the residual null at G4's cap. It costs about 0.08 at the prior sensitivity, and much more for weakly
detected steerers, whose HOLISTIC becomes INCONCLUSIVE rather than a headline. R6-2 makes the NEITHER side
symmetric: it names the sensitivity limit rather than claiming a stronger no.

**Reading** (parts 2a and 2b):
- **Level.** Under every null, HOLISTIC fires at most 0.003. That includes the registered gap at G4's cap, where r5
  gave 0.63. One influential unit gives 0.000 (R10). When the gap is present, its mass goes to "INCONCLUSIVE: holistic
  steers more, not crossed" (0.21), which is the right place for it.
- **The clean "no" is reachable where expected:** NEITHER 0.92 at the Pioneer's prior floor.
- **Detection.**
  - A bypass in half the lines is detected at 0.85 at the one-nose prior sensitivity, and 0.93 if steerers are
    two-nosed. At a weak one-nose sensitivity (0.20) it falls to 0.53, but it then reads INCONCLUSIVE, not NEITHER
    (0.02).
  - **A weak bypass (a quarter of lines) is detected at 0.32:** the weak spot.
- **A bypass held only at the designed body's erosion (Q 0.21) reads NEITHER 0.83.** That is a holistic trait held in
  about 1 member in 5 and confirmed in about 1 in 15, below K. NEITHER's sentence is bounded to "≥ K of 40" (§6.3).
  G6 prints the realised plateaus, so a reader can see whether this regime applies.
- **Unequal erosion no longer leans toward HOLISTIC when both cross:** 0.003 against the Pioneer's 0.013–0.040. At
  K = 5 the Pioneer's larger SENS_C,P offsets its lower plateau. The loss-ratio covariate stays registered.
- **[OPEN] The weak spot.** It is still below 0.5, so by the adversary's rule G = 72 is a candidate: +50% per world
  point. This model cannot price G = 72 honestly, because p itself grows with G. It is left to the ruling.

## 8. The registered fairness block (R2), pinned on every command line by `world.py`

| row | setting | the designed body |
|---|---|---|
| mass budget | `--mass-budget 15.34` | the reference |
| gear budget | RBT-120's rule and cap (A recommends c = 1.77) | inside by construction (1.76) |
| Effector-bias walk | bounded as RBT-120 registers it, through **both** operators | at parity |
| global-bias walk | default (not frozen) | — |
| **crossover** | **`--crossover-rate 0`** in both faunas (MUST 4) | — |
| operators | each fauna's default (`mutate` / `mutate_controller`), `--conventional-topology` | the designed controller evolves |
| ball cone + hinge ranges | ON (required) | no effect |
| settle until rest | ON, 0.01 m/s, cap 5 s | no effect |
| outward limbs, reachable-node cap, max extent 0.6 m, clearance from geoms | ON if merged (wanted) | no effect / small |
| eating | `--eat-from root` (root = Node 0's first instance) **[A1, item 6]** `--eat-rule surface` | eats from the chassis's surface |
| **smell transform** | §4.2 at the world point's G (MUST 5) | all three noses live |
| **T's speed threshold** | 0.25 × the member's median CoM speed per intact season (MUST 2) | — |
| **decoy** | rotate; θ stream keyed on the start seed; re-drawn for spawn clearance; rotation-invariance asserted (SHOULD 1, 2) | — |
| terrain | `--terrain random`, penetration recorded (H71) | sinks up to 0.35–0.57 m, unfixed |
| draws | D from G6 | — |
| vocabulary | `--brain-model foraging` | three food noses |

The readout prints this table as run, from each run's `config.json`.

## 9. Cost and packing (per world point)

**Per generation**, extrapolated from RBT-113's 50 CPU-s at D = 2, ×1.25 for movers: **about 250 CPU-s at D = 8,
about 500 at D = 16, and about 220 under `--draws-final 16` over D = 4.** For the last, the base is 125 CPU-s, plus 11
boundary members × 2 faunas × 16 extra draws at about 0.35 s. G5 re-costs all three.

**Probing is dearer than r5 assumed.** Under the trajectory screen, every body whose smell changes its path goes on
to stage 2: every Pioneer, and every holistic body with a wired nose. So this costing assumes 75% reach stage 2
(r5 assumed 20%).

| item | CPU-h at D = 16 | at D = 8 | `--draws-final 16` over D = 4 |
|---|---|---|---|
| evolution per unit: B 12 + U 48 + N 48 = 108 generations | 15.0 | 7.5 | 6.6 |
| probes per unit: 9 probe points × 2 faunas × 40; stage 1 (8 seasons); stage 2 (64 seasons, for 75%); confirmation (32 seasons, for 10%); 0.35 s per season | 4.1 | 4.1 | 4.1 |
| proposal assay per unit (400 children, the same stages, with parent confirmation) | 2.1 | 2.1 | 2.1 |
| **one unit** | **about 21** | **about 14** | **about 13** |
| **24 units** | **about 510** | **about 330** | **about 310** |
| gate (G1, G2, G4 at 200 per fauna, G5–G9, draw screen, the `--draws-final` test) | about 14 | about 12 | about 12 |

**Both registered costs, for the ruling (R5-5):** about 510 CPU-h per world point at D = 16, and about 310 under
`--draws-final 16`, if G6 finds that it holds. For 2–3 sweep points that is 1,000–1,500 against 600–950 CPU-h.

**Packing** (RBT-113's RUNNER; `runs/README.md`):
- **one arm per session at `WORKERS=4`**, with the durable loop. That is about 5.3 h per session at D = 16
  (budgeted at 7 h), about 3.5 h at D = 8, or about 3.3 h under `--draws-final`.
- **24 sessions per world point.** They run in waves of 6–8.
- A unit's B, U and N stay in one arm, so pairing never crosses sessions.
- A lost session drops its unit, and the readout re-runs `power.py` at the realised n. It is not re-simulated.

**A further cheaper option, for the ruling:** N on 12 of the 24 units, with pooled-N subtraction, saves about 30%.

n is not cut below 24, and D is not cut below G6's rule.

**Committed per arm:**
- `config.json` ×3, `command.txt`, `platform.txt`, `commit.txt`;
- `steer.txt` (per probed member, condition and draw);
- `assay.txt`;
- `wiring.txt` (§6.4).

The bulk goes to `ckpt/rbt-116-<W>-<unit>`.

## 10. What the re-read should attack first

1. **K's rule** (§1.4, `power.txt` 2a). Is "false HOLISTIC ≤ 0.01 at G4's cap, on 600 readouts" the right criterion?
   Is re-choosing K at the gate, from measured rates, sound, given that it happens before any arm?
2. **G8(f)'s plant.** Is "the most-moving Part, turn on one side" a fair one-nose steerer on arbitrary bodies? And
   is "stronger no only if detection ≥ 0.8 at min(SENS)" the right condition?
3. **The low-plateau regime.** A holistic trait held only at the designed body's erosion reads NEITHER 0.83. Is
   NEITHER's "≥ K of 40" sentence enough, or should NEITHER also require G6's realised plateaus to exceed a floor?
4. **`--draws-final`'s holding.** It is equivalent to D = 16 only at the boundary. Is s at the boundary the right
   quantity for (1 + s)(1 − u)?
5. **Probe cost** (75% to stage 2): whether stage 1 should keep a weak F screen after all, now that the trajectory
   veto carries the null.

## 11. Dependencies and status

| item | status (about 21:50 UTC; r7) |
|---|---|
| RBT-121 audits A–D and the audit adversary | reported and taken in |
| RBT-116 design adversary (PR #408, `e51aabf`) and ruling (22:15) | taken in (§0, r5) |
| the adversary's re-read of r5 (`R5-CHECK.md` @ `82211af`) and ruling (21:55) | taken in (§0, r6) |
| the adversary's re-read of r6 (`R6-CHECK.md` @ `3f2bfc7`: REGISTER) and ruling (22:05) | R6-1 and R6-2 taken in as registered text (§0, r7) |
| RBT-120 gear budget (with the Effector-bias walk), and RBT-124 and RBT-125 (per the coordinator's 21:55 note) | pending |
| smell transform flag (§4.2), `eat_from`, ball cone and hinge ranges, settle | each needs its own designer, adversary and ruling |
| this design's hooks (§3.1, including `--draws-final`) | after the ruling; a code PR with byte-identity tests |
| `steer.py`, `gate.py`, `readout.py`, `world.py`, `run_arm.sh`, the G8 planters ((a)–(f)) | specified here; written after the ruling |
| per-world gates | after the prerequisites and hooks |
| the owner's world-sweep decision | pending; §4 is ready for 1–3 points |
| registration | approved at 22:05 subject to R6-1 and R6-2; the merge of #400 with #408 is the coordinator's |
| the RBT-129 sweep choosing the world points | pending |
