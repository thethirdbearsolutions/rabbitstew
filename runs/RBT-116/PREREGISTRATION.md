# RBT-116 pre-registration (DRAFT): the extradimensional bypass. Do holistic bodies cross the compass valley more readily than the Pioneer?

*Designer's **draft**, revision 4 (2026-09-27, about 21:00 UTC), written under RBT-115 (reason (c) of the 2005
proposal). Revisions 2–4 take in RBT-121's four audits, the audit adversary (PR #403) and the coordinator's notes
(§0). **Design only; no arm may run.** These things gate any arm:*
- *RBT-120's motor budget, merged;*
- *RBT-121's synthesis, the PW world's `smell_gain` flag, and the physics and eating fixes of §8, each through its
  own design review;*
- *a design adversary on this file;*
- *the coordinator's ruling.*

*Nothing here was simulated. The only computation is `power.py` → `power.txt`, a pure-Python caricature of the readout
(§7). Every number from earlier work is cited to its committed file. Places this draft cannot settle are marked
**[OPEN]**, with the default it will use if nobody overrides it.*

**The question.** Conrad's (1990) extradimensional bypass says that extra dimensions in the search space open ridges
around valleys that are impassable in a lower-dimensional one. For evolved bodies, those dimensions are body shape
and the number and placement of sensors. The compass strand has measured one such valley precisely, but only on the
Pioneer:
- a lone food sensor wired to the wheels spins the robot, costing −1.502 items per bout [−1.614, −1.375], and 0 of 7
  robots improved (paper 8, table at L167–172);
- the parts must arrive together, with the right signs;
- the operator proposes the right shape in 84 of 200,000 lineages, and its direction is a coin flip: 30 compass
  against 28 anti (paper 8, L324, L361–372);
- correctly signed, paying proposals arrive at about 1.6–1.9 × 10⁻⁵ per lineage (paper 8, L606–612).

**The bypass predicts that holistic bodies cross this valley where the fixed body cannot.** This design asks whether
they do, with the same selection, the same worlds and the same instrument on both bodies.

**The design in one paragraph.**
- **The instrument (§1).** A *behavioural* definition of crossing, identical on any body:
  - the genome gains food from the *information* in smell: intact against a rotated-smell decoy, as in RBT-97 and
    RBT-104;
  - it moves *up the real gradient* more than under the decoy (a chemotaxis index on its centre of mass);
  - the lesion is reported beside both.

  A body with no food sensor scores exactly zero, by construction.
- **The quantity (§2).** How readily steering appears and is held under selection:
  - both bodies start at their own **coverage peak**: RBT-113's default-operator and Z up-line finals, 24 start
    pairs;
  - they then evolve under imposed truncation on net yield, in `evolve`, in a world where perception pays;
  - both faunas ride in the same run, so every generation's worlds are shared;
  - the readout is the time-averaged share of members that steer, corrected by a matched null line, paired by seed.
- **The world (§4).** Auditor C's perception-demanding world PW (2 patches of 0.4 m, radius 4, own-spot regrowth at
  60 s, `smell=log`, decay 1.5, a centred log-contrast of gain **G = 2.5**, centred on a per-robot running baseline,
  never on the root), with eating from the root and every physics fix of RBT-121 ON. It must pass a registered world gate before launch.
- **The nulls (§5).** Per seed, the **N** line runs the same selection in a world whose smell is a rotated decoy, so
  smell carries no information. An offline **proposal assay** on U's saved generations gives the mutation-only rate.
- **Draws (§2.3).** D = 8 per generation by default, sized by a registered rule so that selection outruns the
  operator's erosion (auditor B's finding 3).
- **Verdicts (§6).** Five outcomes, each fixed before any data:
  - HOLISTIC MORE READILY;
  - PIONEER MORE READILY;
  - NEITHER CROSSES (bounded);
  - NOT MORE READILY (EQUIVALENT);
  - INCONCLUSIVE.

  **NEITHER CROSSES is the expected clean "no".** The Pioneer's prior is at the floor, and the bypass predicts
  specifically that holistic bodies leave it. This holds only if gate G7 shows that the Pioneer's valley still
  exists in the world used: PW could flatten it (§2.2).
- **Operators (§2.4).** Each body uses its default operator, at stated unequal erosion. A matched-erosion arm is
  [OPEN] for a second wave.
- **Power (§7)** at 24 units:
  - under the null (both at the Pioneer's prior), NEITHER CROSSES 0.91 and false HOLISTIC 0.007;
  - a bypass in which half the holistic lines cross is detected at 0.89;
  - a bypass in which a quarter cross is detected at 0.34. This is the design's weak spot, and it is stated.
- **Motor budget (§8).** RBT-120's budget is ON in every run, probe and gate.
- **Cost (§9).** About 190 CPU-h at D = 8: 24 arms, two per session, 12 sessions of about 4 h. About 110 CPU-h if
  G6 allows D = 4.

## 0. Revision 2: what RBT-121's three audits change (about 20:45 UTC)

The first draft (`c8e8389`) was written before auditors A (physics, PR #396, `c6dc0c4`), B (GA, PR #395, `a9a6050`) and
C (ecology, PR #397, `791461b`) reported. Their findings change six things, each decided below and carried into the
sections named.

| audit finding | decision in this design | where |
|---|---|---|
| **B3.** Noise hides perception. At RBT-113's 2 draws the repeatability of fitness is 0.14 (holistic) and 0.004 (designed; corrected to about 0.03–0.1 by the audit adversary, revision 4), so a +0.05 item gain gets s ≈ 0.07, below the operator's own erosion of the wiring. | **Draws are sized, not inherited.** D = 8 by default, set by a registered pre-launch rule (G6). *(Revision 4: the rule is now s_f(Δ) ≥ u_f/(1 − u_f) per fauna, with D ∈ {4, 8, 16}; see §2.3.)* | §2.3, §4.2 G6, §9 |
| **B2 and B's parity note.** Erosion is unequal between bodies. A holistic food route appears in 0.78% of children and is lost in 14.6% of carriers. The holistic operator is about 5× more disruptive to wiring per child. The designed compass erodes at u 0.28 (default) (paper 10). | **The primary comparison is at each body's default operator,** and says so in its headline. The bypass is a claim about the holistic search *as it is*, operator included: the operator is part of the geometry Conrad means. Unequal erosion is stated both ways. Per child, the holistic operator is harsher on wiring overall. Per structure, the designed compass erodes faster (0.28 against 0.146). A matched-erosion arm (`--structural-rate-scale K`, B2b) is **[OPEN]** for a second wave. | §2.4, §6.3 headline |
| **C2 and C's PW.** Coverage is the downhill path in every committed world: a nose step pays 1–5% while +25% speed pays 31–37%. Auditor C proposes PW. | **The world is PW** (§4.1). HP, the placeholder in draft 1, is **withdrawn as an arm world**: by C's own numbers it fails this design's G2 before any run. It stays only as a gate comparison row. PW's new `smell_gain` knob is a gated prerequisite with its own design review. | §4 |
| **C1 and B4.** The ecology's breeding lottery is near-neutral above the threshold. | **Not applicable.** This design never runs the ecology; truncation in `evolve` ranks on fitness directly. If an ecology arm is ever added to RBT-116, it registers `breed_order=energy`. | §2.2 |
| **A2, A3, A4, A5 and C4.** Holistic-only allowances: ghost limbs (83% of the D line's work on embedded joints), settle drift (14 of 240 bodies move > 0.25 m with motors off), a part cap raised by recessive nodes, and eating from any geom centre (a sensorless 6.5 m rod nets +0.61). | **All the fixes are ON in every run, probe and gate.** None of them touches the designed body: A2, A3 and A5-extent read 0 on it, and A4 does not apply. So each one removes a holistic-only substitute for steering at no cost to parity. The fixes are `outward_limbs` with `ball_cone`, `settle_until_rest`, `cap_on_reachable`, `max_extent`, `clear_from=geoms` and **`eat_from=root`**. `eat_from=sensor` is rejected (§4.1). Any fix not merged by launch is **reported instead**, per member: embedded-work share, motors-off displacement, span and eating footprint. | §4.1, §8 |
| **A3 and C7.** The readouts need a motors-off season and an intact − decoy column. | **Added to the battery.** A fourth condition, **motors-off**, is the null for "moves by itself". **Items per new 0.35 m cell** is added beside it. F *is* the intact − decoy column. | §1.2 |
| **B1.** The Effector-bias walk is unbounded and saturates motors. | **ON, as RBT-120 budgets it,** in both faunas (B's fix passes the flag through both operators). | §8 |

**Revision 3 (about 20:50 UTC): the coordinator's 20:55 note, and auditor D's history (PR #401, `59fd9b6`,
`runs/RBT-121/history/HISTORY.md` §3–4).**

| item | decision | where |
|---|---|---|
| breed order | **Moot for the primary.** Selection is imposed truncation in `evolve`, which ranks on fitness directly. There is no ecology arm. | §2.2 |
| draws, against PW's measured margin | Δ is registered as **half the first weak nose's margin**. C's `probe_margin.txt` (#397 @ `846f913`) puts it at +0.220 items per season in PW (nose steps +0.17 to +0.20), so the default is Δ = 0.10. It is replaced by half of G7's measured smallest paying prize on real bodies, if that differs. | §2.3 |
| **R7:** every control shown able to fail, on the arm's own founders, before launch | New gate **G8**. On each unit's own generation-0 members: a tuned holistic steering plant must make the STEERS call fire; a Pioneer compass plant must fire; and a Pioneer **throttle** plant (smell drives speed, not heading) must stay silent. | §4.2, §5.3 |
| **R6 and R4:** a world manipulation registers its side effects; perception must pay and be shown to | New gate **G9**, a census of PW against HP and RBT-113's world: income, work, net, cells covered, items per cell, and **solvency** (the share of members with net > 0) for founders, blind finals and planted steerers. U − N side effects are printed beside the verdict. | §4.2, §6.3 |
| **H35:** direction of travel is undefined on holistic bodies | **T sidesteps it:** it uses centre-of-mass velocity against the field's gradient, with no body frame and no "front". Only the G8 holistic plant needs a heading, and it measures one first (R9). | §1.2, §4.2 |
| **H71 and A's B9:** contact penetration on random terrain | **Terrain: `--terrain random`,** as in RBT-113, since the starts evolved there. The deepest contact penetration is recorded per probed season. Members above 0.10 m are flagged, and the verdict is recomputed without them as a registered sensitivity. | §4.1, §6.3 |
| **R2:** fairness defaults | **A registered fairness block** (§8.1): mass budget, gear budget, Effector-bias walk, outward limbs and ball cone, settle, reachable-node cap, extent, clearance and eating rule. Each is marked on or reported instead, with the design pinning the flags so that nothing depends on a default. | §8.1 |

**Revision 4 (about 21:00 UTC): the RBT-121 audit adversary** (PR #403, `runs/RBT-121/adversary/ADVERSARY.md` @
`e9096cb`; the coordinator accepted all its verdicts at 21:20).

| adversary finding | decision | where |
|---|---|---|
| **§6b.** C's "gain 10" is a centred log-contrast of about G = 2.5. At G = 10 contrasts saturate (median \|c\| about 0.6), and later nose steps pay about 2%. **Root-centring zeroes a root sensor, a single nose, and temporal (klinokinesis) smell**, and every designed body has a root food sensor. | **G is registered explicitly as the centred log-contrast gain, default G = 2.5,** with G ∈ {2.5, 10} tested at the gate. **Root-centring is refused.** The transform must centre on a **per-robot running baseline**, or add a centred channel beside the level channel; the `smell_gain` designer chooses which, under the requirements in §4.1. Draft 3's step-down rule {10, 5, 3} is replaced. | §2.2, §4.1, §4.2 G7 |
| **§5 (noise).** s ≈ 1.27 Δ/σ_P, with σ_P ≈ 0.7 (designed) to 1.2 (holistic) at 2 draws. A structure is held only if **s > u/(1 − u)**. The designed body's rep₂ is about 0.03–0.1, not 0.004. | **The draws rule is re-derived.** For each fauna, s_f(Δ) ≥ u_f/(1 − u_f): 0.39 for the designed compass (u 0.28), 0.17 for a holistic route (u 0.146). D ∈ {4, 8, 16}, with σ_P measured by G6 in the registered world at the registered G. Δ is the real-body first paying step measured at the gate. The 0.004 is corrected. | §2.3, §9 |
| **PW's margins describe G ≈ 2.5.** | The Δ default (C's +0.220 first weak nose) holds only at G = 2.5. At G = 10, Δ comes from the gate alone. | §2.3 |
| **§7 (eating).** The live allowance is blind, full-throttle tumbling at any arm length, about +0.7 per season. | **Added to G8's planted negatives:** (d) a sensorless full-throttle tumbler (A's S2-type rod) and (e) the same body carrying two *unwired* food sensors. Both must be NONE. (d) is exact by construction; (e) is the real test. | §4.2 G8 |
| **§2 (ghosts).** The load-bearing fix is the **ball-joint cone plus hinge ranges**, not the outward clamp. Filtering is by weld group, and orientation mutation is unclamped (`genetics.py:209`). | §3.2 and §8.1 now require **`ball_cone` + hinge ranges**. The outward clamp is "wanted", not required. | §3.2, §8.1 |
| **`energy` breed order costs depth** (a gerontocracy). | Moot: no ecology arm. Any future ecology arm weighs `energy_leak` or tickets, not `energy` alone. | §2.2 |

**Also changed, for cost** (D = 8 quadruples the per-generation cost): the C line is replaced by an offline **proposal
assay** on the U line's saved generations (§5.2). It is a cheaper and more direct measure of quantity (i): one operator
child per member, with no selection, screened by the steering battery. This is paper 8's method, made body-general.

---

---

## 1. What "crossing the valley" means, on any body

### 1.1 Why not the compass instrument

The existing instrument cannot be used as it stands:
- The compass is a routed wiring motif, a global unit fed ± by the two wheel noses and driving both drive
  Effectors.
- It is detected by a structure predicate and an own-link small-signal gain (`runs/RBT-91/structural_rate.py:76–165`).
- Every step assumes the Pioneer's layout: `_wheel_noses`, `drive_effector_units` ("Pioneer-shaped bodies only",
  `rabbitstew/fixed.py:218–225`), and the antiparallel wheel axes that make the effector *sum* the steering axis.
- RBT-103 found that `unit_indices` raises on every holistic champion (REPORT.md L211–215).

A holistic body can steer in ways the motif does not name:
- two noses on Parts of different Nodes, read through a global differencing unit;
- a nose on a swinging limb, sampling the field actively;
- a lone nose read through a `differentiate` unit while the body moves, which is temporal klinotaxis
  (`brain.py:90–93`);
- an asymmetric gait whose turning rate a single nose modulates.

**Any wiring definition would either miss these or reward look-alikes. The definition is therefore behavioural.**

### 1.2 The probe battery (`steer.py`, to be written after the ruling; specified here)

**One genome, one fixed battery of solo seasons.** The battery uses:
- the registered world (§4), with the motor budget ON;
- a random start, with the terrain and start seeds fixed in the file, identical for every genome, line, fauna and
  generation.

Four conditions are run on the same draws:

| condition | the `food` sensors read | everything else |
|---|---|---|
| **intact** | the real field | unchanged |
| **decoy** | the **live** layout rotated about the world origin by θ, uniform in [30°, 330°], drawn per draw from a fixed stream | unchanged: eating, regrowth, depletion and the real items |
| **lesion** | 0 | unchanged |
| **motors-off** | the real field | every actuator command held at 0 for the whole season (auditor A's `probe_passive.py` `season(..., off=True)`): the null for "moves, and eats, by itself" (A3) |

- **The decoy is RBT-97's `RotatedSmell`** (`runs/RBT-97/mechanism.py:80–100`), promoted into the package (§3.3).
  - It keeps the item count, the patch geometry and the depletion, and removes only the correlation with where the
    food is.
  - It replaced a static decoy that biased the reading because it never depletes (paper 8, L528–545).
  - The arena and the patch centres are discs about the origin, so the rotation maps the field's distribution to
    itself.
- **RBT-113's `probe_food.py` mirror** is the 180° special case, and is not used. A single fixed angle lets a body
  whose travel correlates with its start position read a structured decoy.
- **Only `food` is patched.** The `agent` smell reads 0 solo in every condition.
- The patch is on the *field*, not the wiring, so it is identical on any body.
- **Under PW's `smell_gain`** (§4.1), the rotation is applied to the item positions *before* the sensor transform. So
  the decoy nose sees a correctly transformed reading of a wrong layout, whatever the transform is (sum, log, or
  centred contrast).

**Per season it records:**
- `food`: items eaten;
- `work`: work cost, in yield units;
- `cells`: distinct 0.35 m xy cells visited by any geom, and **items per 100 new cells** (auditor C's finding 7
  column, as in `probe_food.py`), so that coverage is visible beside every food number;
- `disp_off`: the centre-of-mass displacement in the motors-off season;
- `pen`: the deepest contact penetration of the season (A's `probe_work` measure), for H71;
- **the chemotaxis index T.** Let v be the horizontal velocity of the robot's centre of mass at each control tick,
  and ĝ the unit gradient of the **real** smell field at the centre of mass. The field is the same sum of
  `exp(−d/decay)` terms that `_intensity` squashes; the squash is monotone, so it does not change the direction. The
  gradient is computed analytically. In PW the field is the same sum at decay 1.5, and T ignores the sensor
  transform: `log` and the centred gain change what a nose reads, not where the food is. Then:

  > T = Σ |v| cos∠(v, ĝ) / Σ |v|, over ticks with |v| > 0.05 m/s

  - T is the speed-weighted share of the path run up the real gradient, and lies in [−1, 1].
  - **T needs no direction of travel** (H35). It uses the centre of mass's own velocity and the field's gradient, so
    a body that goes backwards, sideways or rolling is scored the same way. This is also why T works on bodies with
    no defined front.
  - Under the decoy, T is still computed against the **real** field.
  - A body that follows the decoy therefore reads T ≈ 0 there.

**Why T as well as food.** Food gain from smell alone passes *kinesis*: slowing down or speeding up with intensity,
without turning. RBT-106's adversary found 26 of 70 compass-lesioned Pioneers moving by ≥ 0.25 items between real
and decoy smell (F6). T separates kinesis from steering:
- **orthokinesis** changes the weights of path segments, not their headings, so T is unchanged in expectation;
- **klinokinesis and klinotaxis** bias the heading toward the source, so T rises. That is directed turning, which is
  what the ticket means by the compass.

### 1.3 The individual call

The battery runs in two stages, so that sensorless and inert bodies cost little:
- **Stage 1 (screen):** 4 draws, intact and decoy only.
  - A genome passes the screen if its mean paired F₁ = food_intact − food_decoy is > 0.
  - Stage-1 draws are **not** reused in the call.
- **Stage 2 (call):** 16 fresh paired draws, all four conditions, for screened genomes only.

Per genome, over the 16 stage-2 draws:
- **F** = mean(food_intact − food_decoy), the food gained from smell *information*, in items per season;
- **ΔT** = mean(T_intact − T_decoy);
- **L** = mean(food_intact − food_lesion), reported only.

**A genome STEERS** iff all of the following hold:
1. F ≥ **F_MIN = 0.25** items per season, and the one-sided 95% t lower bound on F is > 0.
2. The one-sided 95% t lower bound on ΔT is > 0.
3. **The zero-count veto:** at most half of the 16 paired draws have food_intact = food_decoy exactly
   (RBT-104 `function.py` L164–174).

**A genome is SMELL-USE** if 1 and 3 hold but 2 fails: it uses smell without directed turning. This is reported, and
it is **not** a crossing. **Otherwise it is NONE.**

**Why F_MIN = 0.25.** It is:
- about the size of kinesis noise between real and decoy smell (RBT-106 F6);
- about half of the smallest *paying* compass prize the strand measured: the routed motif at w = 16 gained +0.277
  in the uniform world (paper 8, L487–491), and a = 32 gained +0.887 in the patchy world (`runs/RBT-106/prize.txt`).

**[OPEN] F_MIN is absolute, in items.** A body with a lower base income may gain fewer items for the same steering.
The adversary should attack this. The alternative, max(0.25, 0.2 × food_intact), is pre-computed in the readout
and printed beside the call, but it is not the call.

### 1.4 Coverage is rejected, by construction and by control

- **A body with no food sensor** runs byte-identical intact, decoy and lesion seasons. So F = ΔT = L = 0 exactly, the
  zero-count veto fires, and it is NONE. That is the ticket's "a blind body that eats by sweeping must score zero",
  and it is checked on every such genome (§5.3, control I1).
- **A body with noses it does not use** has F and ΔT of 0 in expectation. Its false-STEERS rate is measured on
  RBT-113's up-line finals of both faunas, the programme's certified coverage foragers (ADVERSARY §4), and gated at
  ≤ 0.05 (§4.2, G4).
- **A body that eats by kinesis** fails condition 2 and is SMELL-USE.

### 1.5 From individuals to lines

- **Share.** At a probe generation t, the share of a line is the fraction of its **M = 16** probed members that
  STEER. The members are drawn by a fixed rng from that generation's saved population.
- **A_f.** Per unit (§2.2) and fauna f:

  > A_f = mean over t ∈ {12, 24, 36, 48} of [share_U(t) − share_N(t)]

  That is the **time-averaged, null-corrected share that steers**. "More readily" means sooner and more often, and a
  time average rewards both. It also still ranks two faunas that both reach the ceiling by when they got there.
- **A line has CROSSED** if, at generation 48, share_U ≥ 0.25 and share_U − share_N ≥ 0.25.
  - This means 4 or more of 16 members steer, 4 or more above the null line.
  - It is the line-level count used for the floor verdict.

## 2. The measured quantity, and why

### 2.1 The three candidates

| candidate | what it measures | verdict |
|---|---|---|
| (i) the proposal rate under mutation alone | whether steering genomes are *near* the population in the operator's geometry | **secondary** (the proposal assay, §5.2) |
| (ii) the rate at which steering appears and is held under selection | proposal × conversion: the bypass's operational prediction | **primary** |
| (iii) the depth of the valley on each body | the fitness cost of the intermediate steps | **descriptive** (§6.4) |

**Why (ii) is primary.** Conrad's claim is about *ridges*: paths along which fitness does not fall. A high proposal
rate into a deep valley does not cross it, and a shallow valley with no proposals is not crossed either. Only
appearance *under selection* integrates both, which is the sense of "more readily" in the ticket.

**Why (iii) is only descriptive.** Depth needs the intermediate steps to be identified, and on an arbitrary body they
can only be identified by a wiring motif, which §1.1 rules out. The behavioural proxy (§6.4) is the net yield of
SMELL-USE and wrong-signed members against NONE members. It is reported, not tested.

**Why (i) is secondary.** It is cheap: an offline assay on the U line's saved generations. But on its own it
cannot distinguish a bypass from a nearby cliff.

### 2.2 Why `evolve` with truncation, not the ecology, and not a plant

**The ecology cannot power this.**
- Selection on a planted, paying compass there is s = 0.01, with a 95% interval of [0.00, 0.08] (RBT-112
  `READOUT.md`; `instrument.txt` L54).
- Unseeded, the Pioneer's expected de novo arrivals are **about 0.26 across all ten 600-season arms combined**, not per
  arm (`runs/RBT-102/REPORT.md` L140–142), and about half of them would be wrong-signed.
- A zero there becomes informative only at about 184,000 genomes (paper 10, L236–239).
- The ecology also couples the world to births, density and depth (RBT-106 H8), so a world that pays more changes
  more than the prize.
- Its breeding lottery is near-neutral above the birth threshold (auditors C1 and B4). **For this design the breed
  order is moot:** imposed truncation in `evolve` ranks on fitness directly. (Any future ecology arm weighs
  `energy_leak` or tickets rather than `energy` alone, which costs depth: the audit adversary's gerontocracy.) A 2× forager fixes in 0 of 200
  replicates under the committed shuffle. **If an ecology arm is ever added to this ticket, it registers
  `breed_order=energy`.**

**`evolve` with RBT-113's truncation hook has what this needs** (`--truncation 0.25 --line up|down|control`):
- selection intensity of about 1.27;
- discrete generations;
- solo scoring;
- byte-exact resume;
- both faunas in one run, so that every generation's worlds are shared between the bodies.

**The start is each body's coverage peak**, not random founders, and not a plant.
- **Where the starts come from.** RBT-113 selected both faunas up on the same currency (solo net yield), in the same
  worlds, for 24 generations. Both learned to eat by moving, not by smelling:
  - holistic U line: intact 0.854, blind 0.913, decoy 0.934;
  - designed U line: intact − decoy +0.02 (ADVERSARY §4).

  **These final populations are the valley floor**: the local peak from which the bypass has to find a ridge.
- **Units.** 12 default-operator starts (`O1/1` … `O4/12`) and 12 Z starts (`Z1/Z1` … `Z4/Z12`), each a pair
  (holistic, designed).
  - The Z holistic lines are independent replicates (salt 1).
  - The Z designed lines evolved under frozen global biases. As starting populations they are simply 12 more coverage
    foragers.
  - Every unit in this design runs the **default** operator. Start type (O or Z) is a registered sensitivity split
    (§6.3).
- **What this matches.** History, selection and currency: a behavioural match, not a structural one. That is the
  only kind of match two different body spaces admit.
- **What it does not match.** The holistic starts carry fewer noses (39% have any food sensor), and the Pioneer
  always has three.
  - This is not corrected. Acquiring and placing sensors *is* one of the bypass's extra dimensions.
  - It is reported as the share of each fauna's members with ≥ 2 food sensors on distinct Nodes, at every probe.
- **Why not plant.** Planting cannot be made identical:
  - the routed motif exists only on the Pioneer's layout;
  - a hand-built holistic compass would be one body chosen by the designer;
  - planting measures *holding*, not *crossing*. The strand already knows the Pioneer holds a paying compass in the
    patchy world (RBT-106 HP: 9 of 10 HELD).

  **Planting is used only where it is honest: as the instrument's and the world's positive controls (§4.2).** The
  enrichment in this design is strong truncation selection, the coverage-peak start, and a world where perception
  pays. None of the three favours either body by construction.
- **[OPEN] A random-founder start (R).** It is RBT-113's own start, and would allow the bypass to run through a body
  built from scratch. It is **not in this wave**, because of its cost (another 70+ CPU-h). If this design reads
  NEITHER CROSSES, R is the natural next test, and the registration says so.

**The Pioneer's expected floor, and the risk PW poses to it.** A 48-generation line of 40 has about 1,920 births.
In the committed worlds, at about 2 × 10⁻⁵ correctly signed, paying proposals per lineage, that gives **p_P ≈ 0.04
lines** crossing. This is an assumption in `power.py`, not a registered arm.
- In the committed worlds the valley on the Pioneer is expected to hold. **That is not a flaw of the design: it is
  the valley.** The bypass predicts specifically that holistic lines leave the floor, so the design's power is set
  for detecting holistic crossing against a Pioneer at or near the floor (§7).
- **But PW is built to make small nose steps pay.** Auditor C predicts that an installed compass at a = 6 pays there.
  That may also flatten the Pioneer's valley, the one whose crossing is the question.
  - If PW removes the valley on the Pioneer, "both cross" becomes likely. That reads INCONCLUSIVE 0.94 of the time
    at n = 24 (§7), and it is no longer a test of a bypass.
  - The world must therefore **pay the peak but keep the valley**. Gate G7 (§4.2) measures the Pioneer's valley in
    the candidate world: the lone-nose (pirouette) cost at the smallest paying compass gain.
  - **Registered rule:** G7 and G2 are run at G = 2.5 and at G = 10. **G = 2.5 is primary** (the regime C's margins
    describe), if it passes both G2 (perception beats coverage) and G7 (the valley is still there). Otherwise G = 10,
    if it passes both. If neither passes, nothing launches, and the coordinator rules. At G = 10 later nose steps pay
    only about 2% (the audit adversary's §6b), so G = 10 is a fallback, not a preference.

### 2.3 Draws: selection must outrun erosion (auditor B's finding 3, as corrected by the audit adversary's §5)

**The condition.**
- Under this design's truncation (top 10 of 40), a carrier of a gain Δ gets **s ≈ 1.27 Δ / σ_P**, where σ_P is the
  phenotypic SD of the ranked fitness (the audit adversary's §5).
- A structure eroded at rate u per child is held only if **s > u/(1 − u)**:
  - **0.39** for the designed compass (u = 0.28 at the default operator, paper 10);
  - **0.17** for a holistic food route (u = 0.146 among carriers, B2).
- At RBT-113's 2 draws, σ_P was about 0.7 (designed) and 1.2 (holistic), and the designed body's repeatability was
  about 0.03–0.1. B's 0.004 is corrected by the adversary.
- **So at 2 draws, selection holds only gains large enough to be allowances.** A crossing test run there would
  measure the operators, not the valley.

**What D buys, from RBT-113's components** (illustration, not the rule). B's `noise.txt` gives between-member SD and
member × draw SD of 0.056 and 1.343 (designed) and 0.336 and 1.158 (holistic), so σ_P(D) = √(σ_G² + σ_e²/D):

| D | σ_P designed | σ_P holistic | s, designed, Δ = 0.10 / 0.22 | s, holistic, Δ = 0.10 / 0.22 |
|---|---|---|---|---|
| 4 | 0.67 | 0.66 | 0.19 / 0.42 | 0.19 / 0.42 |
| 8 | 0.48 | 0.53 | 0.27 / 0.59 | 0.24 / 0.53 |
| 16 | 0.34 | 0.44 | 0.37 / 0.82 | 0.29 / 0.63 |

- A step of the size of PW's first weak nose (+0.22 at G = 2.5) is held on both bodies from D = 4.
- A step of half that is held on the holistic body from D = 4, and on the designed body only near D = 16.

**The registered rule (G6).**
1. **Δ is the first paying step, measured on real bodies at the gate** in the registered world and at the registered
   G:
   - on the designed body, G7's smallest paying rung's prize;
   - on the holistic body, G8(c)'s median F at the tuned plant's smallest paying w.

   The smaller of the two is used. Until the gate runs, the working value is C's kinematic first weak nose, +0.22,
   which is valid at G = 2.5 only. At G = 10, Δ comes from the gate alone.
2. **σ_P** is measured by B's `noise.py` method on each fauna's generation-0 start members, in the registered world,
   at D = 4, 8 and 16.
3. **D is the smallest of {4, 8, 16}** at which s_f(Δ) ≥ u_f/(1 − u_f) for both faunas.
4. If none passes, D = 16, and the headline carries the sentence "at the registered draws, selection on the first
   paying step (Δ = …, s = …) was weaker than the erosion of the structure that carries it (u/(1 − u) = …); a
   NEITHER verdict is conditional on that."
5. s at Δ/2 is printed beside the rule, as the margin for real bodies realising less than the gate's step.

**The cost default is D = 8** (§9); D = 16 roughly doubles it. **[OPEN]:** auditor B's `--draws-final K`
(re-scoring the truncation boundary only) would buy most of the benefit for less. It is new code. If it merges first,
G6 tests it as a fourth option.

### 2.4 Operators: the comparison is made at each body's default operator, at unequal erosion

- The holistic operator erodes wiring about 5× more than the designed one per child (B, `parity.py`: 8.4% against
  1.6% of links lost). A holistic food route appears in 0.78% of children and is lost in 14.6% of carriers (B2).
- **The designed compass erodes faster per structure,** though: u = 0.28 at the default operator, against 0.146 for a
  holistic route. So "unequal erosion" does not favour either body in one direction. It is a different geometry.
- **The primary comparison uses each body's default operator,** as RBT-113 did. The bypass is a claim about the
  holistic search space *as explored by its operator*. Conrad's ridges are ridges of the operator's neighbourhood,
  not of an abstract space.
- The headline states this: "at each body's default operator; the holistic operator erodes wiring about 5× more per
  child, and the designed compass about 2× more per structure."
- **[OPEN]:** a second wave at matched erosion, with `--structural-rate-scale K` chosen so that holistic route loss
  among carriers is about the designed compass's u. It is auditor B's 2b, new code. It would ask whether a holistic
  advantage (or its absence) survives equal erosion. It is not in this wave.

## 3. The mechanism: what must be added before any arm

### 3.1 This design's own hooks

Three small hooks are needed, each off by default and byte-identical when off. They follow RBT-113's pattern:
digests recorded on the pre-hook code, with tests. They come as a separate code PR, after the ruling.

1. **`evolve --from-population KIND=DIR`.** Start a fauna from a saved `final/` population, exactly as saved: no
   weight redraw (unlike `--holistic-seed`), and N must equal the saved count.
2. **`evolve --save-every K`.** Write each fauna's population at generations divisible by K, to
   `<kind>/gen-<t>/`. This is bulk, kept on the checkpoint branch.
3. **`--smell-decoy rotate`** (`evolve` and `Simulation`). Food sensors read the live layout rotated about the
   origin by θ ~ U[30°, 330°].
   - θ is drawn per season from a registered stream keyed on the season's start seed, so it is shared across the
     faunas and the paired worlds.
   - This is RBT-97's `RotatedSmell`, promoted. The N line uses it throughout evolution, and `steer.py` uses it for
     the decoy condition.
   - A test pins that the rotation leaves eating, regrowth and the real items untouched, and that a sensorless genome
     runs byte-identically under it.
   - The rotation is applied to the item positions before any sensor transform, including PW's `smell_gain`.

### 3.2 Gated prerequisites from other tickets (each through its own designer, adversary and ruling)

| prerequisite | source | required? | if not merged by launch |
|---|---|---|---|
| motor budget (gear cap, with the Effector-bias walk bounded) | RBT-120; A1, B1 | **required** | nothing launches |
| `smell_gain` (centred log-contrast, gain G, centred on a per-robot running baseline or as a second channel beside the level; **never root-centred**) | auditor C's §2 and PW; the audit adversary's §6b | **required** for PW | nothing launches in PW. PW at gain 1 may be gated as a fallback world (C: smell ÷ blind 1.64); the coordinator rules |
| `eat_from=root` | auditor C's §4 | required | committed eating rule, with span and footprint reported per member and the caveat in the headline |
| `ball_cone` + hinge ranges (the load-bearing ghost fix; the audit adversary's §2) | A2 | required | embedded-work share reported per probed member; a STEERS member with over 50% of its work on embedded joints is flagged in the headline |
| `outward_limbs` (orientation clamp; orientation mutation is unclamped at `genetics.py:209`) | A2 | wanted | embedded pairs at build reported |
| `settle_until_rest` | A3 | required | motors-off displacement reported (it is anyway, §1.2) |
| `cap_on_reachable` | A4 | wanted | recessive-node count reported |
| `max_extent`, `clear_from=geoms` | A5 | wanted | span and footprint reported |
| `--draws-final K` | B3 | optional (§2.3) | D ∈ {4, 8, 16} by G6 |
| `--structural-rate-scale K` | B2b | not in this wave | — |

"Required" means the design waits for it. The coordinator may downgrade any row to "reported instead", but must rule
it before launch, and the readout states it.

## 4. The world

### 4.1 The world: PW

**PW** is auditor C's perception-demanding world (`runs/RBT-121/ecology/AUDIT.md`, "Perception-demanding world"),
on RBT-113's `evolve` world:

```
--brain-model foraging --food-items 12 --eat-radius 0.35 --work-cost 0.03 --duration 15 --mass-budget 15.34
--conventional-topology --terrain random --random-start --score food
--food-patches 2 --patch-radius 0.4 --food-radius 4.0 --regrow-delay 60 --smell log --food-decay 1.5
--smell-gain G            # new; the centred log-contrast gain, G = 2.5 primary, 10 fallback (§2.2);
                          # centred on a per-robot running baseline (or a second channel), never on the root
--eat-from root           # new (C §4)
+ the RBT-120 budget and the A2–A5 physics flags (§3.2, §8)
```

- **What PW pays.** In auditor C's calibrated kinematic model (`probe_proposal.txt`), an evolved-range nose earns
  3.66× a blind body of equal speed, and beats a blind body at twice the speed by 1.73×. One nose-gain step pays
  +4 to +13% against +16% for 25% more speed; in the committed worlds it paid +1 to 5% against +31 to 37%.
- **These are kinematic numbers.** The gate (§4.2) re-measures them on real bodies before anything runs.
- **Terrain is `--terrain random`,** as in RBT-113, where both start populations evolved. The designed body sinks up to
  0.35–0.57 m in contact on it (H71; RBT-113 readout adversary N1; A's lower-ranked soft contacts), and there is no
  fix yet. So the deepest penetration is recorded per probed season (§1.2), and a registered sensitivity drops every
  member above 0.10 m (§6.3).
- **`regrow-delay 60` exceeds the 15 s season,** so eaten items do not return within a season: depletion is real, and
  the memoryless field that rewards pure coverage (C §5) is gone.
- **The living-cost recalibration C asks for is not needed.** This design never runs the ecology, and `evolve` has no
  living cost.

**What the smell transform must satisfy** (the audit adversary's §6b). The `smell_gain` flag has its own designer.
RBT-116 accepts any transform that meets all four of these:
1. **A root sensor is not zeroed.** Every designed body has one (the chassis nose), and holistic roots may too.
   Root-centring fails this.
2. **A single nose and temporal (klinokinetic) smell still carry information.** Root-centring also fails this: a
   lone off-root nose would read only its offset from the root.
3. **The same transform applies to every food sensor of every body.**
4. **The decoy rotation happens before the transform** (§1.2).

A per-robot running baseline (subtract the robot's own recent mean intensity) meets all four. So does a second,
centred channel beside the unchanged level channel. The second also keeps the start populations' existing level
wiring meaningful, which the designer of `smell_gain` should weigh.

**Why eat from the root.** Of the three eating rules, root eating is the one that keeps parity between the bodies:
- **The committed rule** (any geom centre) rewards span and limb sweeping: a sensorless 6.5 m rod nets +0.61
  (A5). Only the holistic body can grow that.
- **`eat_from=sensor`** makes the mouth the nose. That would select for carrying food sensors *because they eat*,
  whatever steering they do. It would raise the holistic nose supply for a reason unrelated to perception, which
  confounds the bypass in its favour, and it would make a sensorless coverage forager eat nothing, which breaks
  §1.4's coverage null. **Rejected.**
- **`eat_from=root`** gives every body one mouth, at its root. The Pioneer's root is its chassis, which carries its
  centre nose. The prize of an installed compass changes under it, so G1 is measured under it, never borrowed from
  RBT-106.

**HP** (RBT-106's patchy world, the placeholder in draft 1) is withdrawn as an arm world. In auditor C's model, a
nose step there pays +1 to 4% against +37% for speed, so it would fail G2 by construction. It appears in the gate
as a comparison row only.

### 4.2 The world gate (pre-launch; `gate.py`, after the ruling)

The gate is run on the candidate world with the motor budget ON, through `steer.py` itself:

| | check | pass |
|---|---|---|
| **G1** | **Perception pays, on the Pioneer** (PW, and HP as a comparison row). RBT-106's routed w = 32 compass, signed per host by its measured travel direction (`scripts/travel_direction.py`), installed in 16 designed RBT-113 up-line finals (`routed_p801.py install`). | Mean F ≥ 0.5 items per season, and ≥ 12 of 16 hosts STEER. The share that steer is Q_P's sensitivity factor in `power.py`. |
| **G2** | **Perception beats coverage.** The G1 hosts' F against the coverage those same lines bought: the lesioned (blind) yield of the designed U finals minus the lesioned yield of RBT-113's designed founders. | F ≥ the coverage gain, i.e. one working compass is worth at least RBT-113's 24 generations of coverage selection. |
| **G3** | **The instrument sees a holistic steerer.** A hand-built holistic compass, HC, is written as JSON: two food sensors on laterally placed Parts of **different** Nodes (twins of one mirrored Node sum in the global brain, `synthesis.py:323–331`), a global differencing unit, asymmetric effector outputs, and a defined direction of travel. 4 variants (sign × gain). | At least one variant STEERS with F ≥ 0.5. The holistic Q_H sensitivity is the share of its 16 seeded-noise replicates that STEER. |
| **G4** | **False positives are bounded.** `steer.py` runs on 64 members of each fauna's RBT-113 U finals, and 64 founders. | False STEERS ≤ 0.05 per fauna and group (this sets EPS). Every zero-food-sensor genome gives F = ΔT = L = 0 exactly. |
| **G5** | **Timing.** 2 generations of one unit's U line. | Seconds per generation are recorded, and §9 is re-costed from them. |
| **G8** | **R7: the STEERS call can fire, and can stay silent, on the arms' own founders.** On 4 generation-0 designed and 4 generation-0 holistic members of **every** unit (192 hosts): **(a) Pioneer compass plant:** RBT-106's routed motif at the smallest paying rung from G7, signed by the host's measured travel direction (`scripts/travel_direction.py`, H35). **(b) Pioneer throttle plant:** the chassis food nose to a global tanh unit that drives both wheels with opposite signs (the *difference*, the throttle axis, `fixed.py:9–26`), at the same gain. This is smell → speed with no heading term: pure orthokinesis, by the Pioneer's geometry. **(c) Holistic tuned plant** (`plant_holistic.py`, after the ruling): measure the host's mean centre-of-mass heading in one intact season; pick the two expressed Parts of distinct Nodes most separated across that heading; give each a food sensor; add a global tanh unit (bias 0) fed ± by them, linked with +w and −w to the Effectors of the Parts on either side of the heading. Try 2 signs × w ∈ {4, 16, 64} on 4 screening draws, keep the best by F, and call it on 16 fresh draws. | (a) STEERS on ≥ 75% of hosts, pooled. (b) **STEERS on 0 hosts**; SMELL-USE or NONE is allowed, and SMELL-USE is the expected call. (c) STEERS on ≥ 25% of holistic hosts, pooled, and on ≥ 1 host in ≥ 18 of 24 units. The realised shares set Q_P and Q_H in `power.py`, which is re-run before launch. A unit whose own (a) or (c) fails is flagged; if more than 4 units are flagged, nothing launches. **Planted negatives** (the audit adversary's §7): (d) a sensorless full-throttle tumbler (A's S2 rod on an unlimited hinge, and a ball-joint variant), and (e) the same bodies each carrying two **unwired** food sensors on distinct Nodes. Each is run on 16 draws. **Both must be NONE on every body.** (d) is exact by construction (identical seasons), and it checks the pipeline. (e) is the real test: a coverage body with idle noses. |
| **G9** | **R4 and R6: the census, and a world's side effects.** In PW (at the G7 gain), HP and RBT-113's world, each on the same 16 draws: RBT-113's holistic and designed founders, their U finals intact and blind, and the G8(a) planted Pioneers. | Printed, not pass/fail: food, work, net, cells covered, items per 100 cells, speed, and **solvency** (the share with net > 0). G2 is read off this table. A world change that moves solvency or income by more than 25% for one body and not the other is named in the headline as "not the only difference" (R6). |
| **G6** | **Draws** (§2.3). B's `noise.py` method on each fauna's generation-0 starts, at D = 4, 8 and 16, in the registered world and at the registered G. | This sets D (§2.3). Not a pass/fail gate. |
| **G7** | **The valley is still there, on the Pioneer,** at G = 2.5 and at G = 10 (§2.2). On the G1 hosts: the routed compass at a = 2, 6, 16 and 32, correctly signed (the ladder), and the single-nose wiring at the same gains (the pirouette, paper 8's c). | The smallest paying rung is the first a whose prize has a lower bound > 0. At that rung the lone-nose cost is ≤ −0.25 items per season with an upper bound < 0: the intermediate step is downhill. If not, step `smell_gain` down (§2.2). The full ladder and lone-nose table is printed in the headline as the Pioneer's valley in this world. |

- **If G3 cannot be built to pass,** the instrument's holistic sensitivity is unshown and the design does not launch.
  The fallback of loading the Pioneer compass through the holistic path proves only the code path, and is not
  accepted as G3.
- **G2 and G7 pull in opposite directions,** by design. G2 wants the peak high, and G7 wants the Pioneer's
  intermediate step still downhill. A world that passes both is one in which the valley exists and is worth crossing.
  The G7 rule chooses the largest gain that passes both.
- **[OPEN] G2 may be too strict for any world auditor C can build tonight.** If so, the coordinator rules whether a
  weaker G2 (for example F ≥ 0.5 × the coverage gain) is acceptable. It must be ruled before the arms run, and the
  readout states whichever was used.

## 5. Arms, lines and nulls

### 5.1 One arm = one unit

An arm is one start pair (RBT-113 seed directory `O1/1` … `Z4/Z12`, j = 1 … 24), running two `evolve` runs in
sequence:

| line | selection | smell during evolution | purpose |
|---|---|---|---|
| **U** | truncation 0.25, up, on solo net yield | real | the treatment |
| **N** | truncation 0.25, up, on solo net yield | **rotated decoy** (§3.1) | the **matched null**: identical selection and inputs, no information in smell |

**Shared by U and N:**
- the evolve seed 116000 + j and both faunas;
- N = 40, and D draws per generation (§2.3, set by G6);
- G = 48 generations (0 … 47 evaluated, probed at their end);
- `--elites 0`, solo throughout;
- the world (§4.1) and every prerequisite flag (§3.2);
- `--from-population` for both faunas, with `--save-every 12`.

It follows that:
- U and N share every generation's worlds;
- both faunas in a run share them too;
- the generation-0 populations are identical across U and N.

### 5.2 The nulls, and the proposal assay

- **N: the primary null.** It holds constant everything except smell's information: the same selection, the same
  sensor input statistics (the rotated live layout) and the same currency. So:
  - any STEERS it produces is the instrument's false-positive rate on bodies selected for yield;
  - or it is steering-like behaviour that pays for reasons other than smell.

  Either way it is subtracted.
- **The proposal assay (quantity (i); replaces draft 1's C line).** At each saved U generation (0, 12, 24, 36, 48),
  every member gets one child by its fauna's own operator, with no crossover and no selection (paper 8's method,
  made body-general). Each child runs stage 1 of the battery; screened children run stage 2.
  - The per-fauna **proposal rate** is the share of children that STEER whose parent did not, per mutation.
  - The **loss rate** is the share of STEERS parents whose child does not.

  Both are reported with exact CIs and never enter a verdict. The loss rate is the behavioural twin of auditor B's
  route loss (14.6%) and of paper 10's u.
- **The decoy probe inside each genome** (§1.2) is the per-individual null, the third layer.

### 5.3 Controls (checked by `readout.py`; VOID per fauna and scope, as in RBT-113 §6)

- **I1.** Every probed genome with no food sensor reads F = ΔT = L = 0 exactly. One exception voids the instrument
  for the whole readout.
- **I2.** The configs are the registered ones. U and N differ only in `--smell-decoy`, and every §3.2 flag in use is
  identical on both.
- **I3.** Generation 0 is identical (names and fitness) on U and N, in both faunas, and equals the saved start
  population.
- **I4.** The worlds are shared: `(terrain_seed, start_seeds)` per generation is identical across U and N.
- **I5.** The selection mechanics hold: every U and N parent is in the top k of its generation.
- **I6.** The run is complete: 48 generations, and saved populations at 12, 24, 36 and 48 (generation 47's end, named
  48).
- **I7.** The unit's own G8 controls (a), (b) and (c), run before launch on its generation-0 hosts, are carried into
  the readout. A unit that G8 flagged is reported, and dropped in a registered sensitivity. This is the programme's
  rule since RBT-104's VOID (R7): controls run on the arm's own hosts, "at a stated s, not arithmetic reachability"
  (paper 10, L565–570).

## 6. Statistics and verdicts (`readout.py`; constants fixed before any data)

### 6.1 Per unit

For each unit and fauna f ∈ {H, P}, the readout computes:
- **A_f**, as in §1.5;
- **crossed_f**, the line-level call at generation 48.

Also reported per fauna, with no verdict:
- the proposal and loss rates from the assay (§5.2);
- per member: motors-off food and displacement, items per new cell, span and footprint, Σgear/(4 × mass), and the
  embedded-work share (§1.2, §8);
- the mean F and ΔT of U members;
- the share with ≥ 2 food sensors on distinct Nodes;
- food against work (RBT-113's D1 decomposition) at generations 0 and 48.

### 6.2 Across units (n = 24, paired by unit)

- d_j = A_H,j − A_P,j, with its mean, two-sided 95% t CI, and sign-flip p (20,000 draws, since n > 16).
- k_H and k_P, the number of crossed lines per fauna, each with an exact one-sided 95% upper bound.
- A fauna **CROSSES** if the CI on its mean A excludes 0 above and its sign-flip p is < 0.05.

### 6.3 The verdicts, in order (as in `power.py`)

1. **HOLISTIC MORE READILY:** the CI on d excludes 0 above, p < 0.05, and the holistic fauna CROSSES.
2. **PIONEER MORE READILY:** the CI on d excludes 0 below, p < 0.05, and the Pioneer CROSSES.
3. **NEITHER CROSSES:** the exact upper 95% bound on P(a line crosses) is below **0.25** for both faunas.
   - In words: "in fewer than one line in four, on either body, does steering appear and hold within 48 generations
     of truncation selection in a world where perception pays."
   - **This is the bypass's clean "no".** The fixed body's valley holds, as expected, and the extra dimensions did
     not open a way round it at this depth.
4. **NOT MORE READILY (EQUIVALENT):** the CI on d lies inside ±**0.025**, and at least one fauna has k ≥ 3.
   - 0.025 is half the mean d of the weakest bypass of interest: a quarter of holistic lines crossing against the
     Pioneer's 0.04.
   - At n = 24 it almost never fires (`power.txt`), and the draft says so rather than widen it. A wider margin would
     call real bypasses "equivalent": in a trial of the model at ±0.15, a weak bypass read EQUIVALENT 52% of the
     time (not committed; reproduce by setting `DELTA_EQ = 0.15` in `power.py`).
5. **INCONCLUSIVE** otherwise.

**The headline is one sentence per verdict, fixed in code.** It gives:
- the verdict;
- the design (from the coverage peak, 48 generations, truncation, the world);
- d and each A with its CI;
- k_H and k_P with their bounds;
- the SMELL-USE shares beside the STEERS shares, so that kinesis is visible;
- the operator sentence (§2.4) and, if G6 failed, the draws sentence (§2.3);
- the Pioneer's measured valley in this world, from G7: the ladder's prizes and the lone-nose costs;
- the sentence *"The Pioneer's valley is a measured property of the fixed body; a holistic crossing is evidence for
  the bypass only in this world and at this depth, and a NEITHER is evidence against it only to the stated bound."*

**Sensitivity splits (reported only; no verdict):**
- O starts against Z starts;
- F_MIN relative instead of absolute (§1.3);
- the verdicts with N's share pooled over units (the mean of share_N at each t) in place of the per-unit N;
- the verdicts dropping every unit whose F_MIN-relative or motor-class flag fires on any STEERS member;
- the verdicts with every member of penetration above 0.10 m excluded (H71);
- **R6 at the line level:** U − N at generation 48, per fauna, in food, work, speed, cells covered and nose count, with
  CIs, printed beside the verdict.

### 6.4 Valley depth (descriptive)

The readout reports depth on each body, pooled over units, from the proposal assay and the U probes:
- the net yield of SMELL-USE members, and of members with F ≤ −0.25 (smell used *against* food, the behavioural
  anti-compass), each against NONE members of the same line and generation;
- the net yield of the first STEERS members in a U line against their generation's mean.

These estimate how far down the intermediate steps sit, and whether the holistic space has intermediates that do not
cost at all. The latter is the bypass's mechanism, if it is there. No test is made.

### 6.5 Stated both ways

- **If holistic bodies do cross more readily,** the reading is: "in this world, from a matched coverage peak,
  body-and-brain evolution finds directed smell-following where the fixed body does not."
  - It must still survive the follow-up paper's audit: the steerers' bodies and motor use are compared against the
    budget, and a crossing bought by a new allowance is reported as such (RBT-121).
- **If neither crosses, or the Pioneer crosses as readily or more,** that is a clean "no" for reason (c) at this
  design. It is written up as a finding, not a failure to rescue the proposal.

## 7. Power at the registered n (`power.py` → `power.txt`)

**The model.** Per unit and fauna:
- the U line crosses with probability p_f, at a uniform generation, then sweeps linearly to a plateau Q_f over 12
  generations;
- N, and U before crossing, sit at the false-STEERS rate EPS = 0.02;
- 16 members are probed per line at 12, 24, 36 and 48 generations, binomially.

**The bounds are explicit.** A_f lies in [−EPS, Q_f], and Q_f folds in the instrument's sensitivity from G1 and G3.
This is RBT-113's lesson: its unbounded Gaussian model promised the designed body a response of 3.1–5.0 that the body
could not reach. The observed value was 1.48 (ADVERSARY §5).

**Results at n = 24** (300 simulated readouts per row):

| scenario (p_H, p_P) | HOLISTIC MORE | PIONEER MORE | NEITHER | EQUIV | INCONCL |
|---|---|---|---|---|---|
| null: both at the prior floor (0.04, 0.04) | 0.007 | 0 | **0.910** | 0 | 0.083 |
| null: neither ever crosses | 0.007 | 0 | 0.993 | 0 | 0 |
| weakest bypass of interest (0.167, 0.04) | 0.160 | 0 | 0.317 | 0 | 0.523 |
| weak bypass (0.25, 0.04) | **0.340** | 0 | 0.090 | 0.003 | 0.567 |
| bypass (0.5, 0.04) | **0.893** | 0 | 0 | 0 | 0.107 |
| strong bypass (0.75, 0.04) | 1.000 | 0 | 0 | 0 | 0 |
| bypass with low plateau (0.5, Q_H 0.25) | 0.600 | 0 | 0.053 | 0 | 0.347 |
| both cross equally (0.5, 0.5) | 0.030 | 0.027 | 0 | 0 | 0.943 |
| both at ceiling (1, 1; Q 0.8) | 0.027 | 0.023 | 0 | 0 | 0.950 |
| Pioneer more (0.1, 0.5) | 0 | **0.680** | 0 | 0 | 0.320 |

**How to read this:**
- **Level:** false HOLISTIC ≤ 0.030 in every scenario without a holistic advantage, including at the ceiling.
- **The clean "no" is reachable where it is expected.** At the Pioneer's prior floor, NEITHER CROSSES fires 0.91 of
  the time.
- **A weak bypass is the weak spot.** It is detected at 0.34, and is otherwise mostly INCONCLUSIVE, not NO:
  NEITHER fires 0.09, because the effective crossing rate after late crossings is below 0.25.
- **Equivalence is out of reach at n = 24.** "Both cross equally" returns INCONCLUSIVE. The draft accepts this: the
  scenario the bypass argues against, the Pioneer crossing too, is the one the prior makes least likely.
- **n = 12 is not enough.** Under the null, NEITHER CROSSES fires only 0.37 (`power.txt`, n = 12 section),
  so 24 units it is.

**[OPEN] The weak spot has two cures,** each about +50% cost:
- G = 72 generations;
- 36 units, which would need new start populations, since RBT-113 has 24.

The adversary and the ruling decide whether either is bought.

## 8. The motor budget, and every RBT-121 fix

RBT-120's budget is **ON in every `evolve` run, every probe (`steer.py`), and every gate check,** with the
Effector-bias walk bounded as RBT-120 registers it (B1, passed through both faunas' operators).
- The flag and its value are taken from RBT-120's merged registration, and pinned in the arm's command builder
  (`world.py`, after the ruling).
- **The start populations** were evolved without a budget.
  - The readout reports, per fauna, the share of generation-0 members over the budget, and how RBT-120's rule treats
    them.
  - If the rule clamps them at build, they enter as clamped.
  - **[OPEN] If the rule rejects them** rather than clamping, the design waits for a ruling on how to fill the
    population.
  - The RBT-113 holistic U finals sit at Σgear/(4 × mass) = 0.90, against the designed body's fixed 1.76 and the D
    line's 3.66 (`probe_gear.txt`). Auditor A's recommended cap is c = 1.77. So most are expected to fit any budget
    that keeps the Pioneer legal.
- **Per probe,** each probed member's Σgear, its ratio to 4 × mass, and its ball-joint share are recorded
  (`probe_gear.py`'s measures). Any STEERS member is reported with its motor class beside it (§6.5).

**The physics and eating fixes are ON too** (§3.2): `outward_limbs` with `ball_cone` (A2), `settle_until_rest` (A3),
`cap_on_reachable` (A4), `max_extent` with `clear_from=geoms` (A5), and `eat_from=root` (C4).
- **Why this costs parity nothing:** on the designed body, auditor A measured 0 embedded pairs, 0 m motors-off drift,
  no recessive nodes and a 0.42 m largest extent. Each fix removes a substitute for steering that only the holistic
  body could buy.
- **Why it matters here:** a holistic "crossing" bought through a ghost rotor, a settle topple or a long sweeping arm
  would be the follow-up paper's artefact again. With the fixes ON, the remaining routes to food are moving, and
  moving well.
- **The fixes change the Pioneer's numbers** (eating from the root changes what its compass is worth). So every
  Pioneer figure in the gate is re-measured under them, and none is borrowed from RBT-106.

### 8.1 The registered fairness block (R2)

`world.py` pins every row below explicitly on every command line, so that nothing depends on a default.

| row | setting | the designed body | status |
|---|---|---|---|
| mass budget | `--mass-budget 15.34` (the Pioneer's mass) | unchanged: it is the reference | existing flag |
| gear budget | RBT-120's rule and cap. A recommends Σgear ≤ c × 4 × mass per part at c = 1.77 | inside the budget by construction (1.76) | **required** (RBT-120) |
| Effector-bias walk | bounded as RBT-120 registers it (B1's `--effector-bias-sigma` or a reset), through **both** operators | affected, and at parity by B's design | **required** (RBT-120) |
| global-bias walk | default (not frozen): the default operator (§2.4) | — | existing |
| ball cone + hinge ranges | ON (A2; the load-bearing fix) | no effect (0 embedded pairs) | required |
| outward limbs (orientation clamp) | ON if merged (A2) | no effect | wanted |
| settle until rest | ON, 0.01 m/s, cap 5 s (A3) | no effect (0 m drift) | required |
| part cap on reachable nodes | ON (A4) | n/a | wanted |
| max extent | 0.6 m (A5) | no effect (largest 0.42 m) | wanted |
| clearance from geoms | ON (A5) | small (regrowth placement only) | wanted |
| eating rule | `eat_from=root` (C4) | eats from the chassis; its compass prize is re-measured (G1, G7) | required |
| terrain | `--terrain random`, penetration recorded (H71) | sinks up to 0.35–0.57 m, unfixed | existing; reported |
| controller topology | `--conventional-topology` (the designed controller evolves) | as in RBT-113 | existing |
| draws | D from G6 | — | existing flag |
| vocabulary | `--brain-model foraging` | three food noses, fixed (chassis and two wheels) | existing |

A row that is "required" and not merged by launch stops the launch, unless the coordinator downgrades it to
"reported instead" (§3.2). The readout prints this table as it actually ran, from each run's `config.json`.

## 9. Cost and packing

**Per generation.** RBT-113 measured 12.6–15.5 s per generation on 4 workers, about 50 CPU-s, for N = 40 × 2
faunas × 2 draws: 160 solo seasons (PREREGISTRATION §9, §11.5). At D = 8 that is 640 seasons, about 200 CPU-s.
Coverage foragers move more than founders, so this design budgets ×1.25: **about 250 CPU-s at D = 8** and about
125 CPU-s at D = 4. G5 re-costs this in PW.

| item | CPU-h at D = 8 | at D = 4 |
|---|---|---|
| one `evolve` run (48 generations) | 3.3 | 1.7 |
| one arm's evolution (U and N) | 6.7 | 3.3 |
| probes per arm: 9 probe points (generation 0 once; 12, 24, 36, 48 × 2 lines) × 2 faunas × 16 members. Stage 1 is 8 seasons; stage 2 is 64 seasons (4 conditions × 16) for an assumed 20%; 0.35 s per season | 0.6 | 0.6 |
| proposal assay per arm: 5 generations × 2 faunas × 40 children, same two stages, an assumed 10% screened | 0.55 | 0.55 |
| **one arm, total** | **about 7.9** | **about 4.5** |
| **24 arms** | **about 190** | **about 110** |
| *(at D = 16: about 13.3 CPU-h of evolution + 1.15 of probes per arm, so about 350 CPU-h for 24 arms, 12 sessions of about 7.5 h)* | | |
| gate (G1–G9; G8 is 192 hosts × up to 7 variants × about 24 seasons) | about 5 (one session, before the wave) | same |
| readout | minutes | minutes |

**Packing.** This follows RBT-113's RUNNER and `runs/README.md`:
- two arms per session, side by side at `WORKERS=2` on 4 cores, each with the durable loop;
- about 4 h per session at D = 8 (budgeted at 5 h), or about 2.3 h at D = 4 (budgeted at 3 h);
- **12 sessions, in two waves of 6: about 48–60 session-hours at D = 8, 28–36 at D = 4.** A unit's U and N lines
  stay in one arm, so pairing never crosses sessions. The probes and the assay run at the arm's end, in the same
  session.
- **If a session is lost,** its two units are dropped, and the readout runs at reduced n. It is not re-simulated;
  `power.py` is re-run at the realised n and printed.

**Committed per arm:** `config.json` ×2, `command.txt`, `steer.txt` (per probed member and condition; `.txt` so
the allowlist admits it), `assay.txt`, `platform.txt` and `commit.txt`. The bulk (saved generations,
`lineage.jsonl`) goes on `ckpt/rbt-116-<ARM>`.

**Cheaper fallbacks, if the ruling wants them:**
- N on 12 of the 24 units, with the pooled-N subtraction as primary: −25%;
- G = 36: −25%, weakening detection of late crossings.

n is not cut below 24, and D is not cut below what G6 requires.

## 10. What the design adversary should attack first

1. **Does T separate steering from kinesis on a real holistic body,** and not only on HC? For example, a body whose
   gait turns more when smell is high will read T > 0. The draft counts that as klinokinesis, which is chemotaxis.
2. **The absolute F_MIN,** across bodies with different base incomes (§1.3).
3. **Whether the coverage-peak start favours either body.** The holistic finals carry few noses; the designed
   finals carry three unwired ones. And whether R (random founders) should be primary instead.
4. **Whether N is a fair null.** Selecting for yield under a rotated decoy may push bodies toward *ignoring* noses,
   while U's bodies are free to keep them. Then share_N may sit below U's true false-positive rate. The pooled-N
   split and G4's false-positive rate on RBT-113's finals are printed beside it (§6.3).
5. **The Pioneer's prior p_P ≈ 0.04, in PW.** PW is built to make small nose steps pay, so it may flatten the very
   valley under test (§2.2). Is G7's criterion (a lone nose costs ≥ 0.25 items per season at the smallest paying
   rung) the right one? Is the gain step-down rule sound?
6. **G2 against G7,** and whether PW's centred `smell_gain` treats the bodies alike. A root-centred contrast zeroes
   any nose on the root: the Pioneer's chassis nose, and every holistic root nose. A running-baseline contrast would
   turn a lone nose into a temporal-gradient detector, which helps one-nosed bodies (mostly holistic). The transform
   must be ruled with this in mind.
7. **`eat_from=root` against the committed rule.** It removes a holistic-only coverage allowance (A5). Does it also
   remove a legitimate holistic strategy, such as a body whose mouth is best placed off-root? The draft judges that
   parity wins.
8. **D = 8 and the unequal erosion (§2.3, §2.4).** Is s(0.10) ≥ 0.30 the right rule? Should the matched-erosion arm
   be in this wave?
9. **Whether 48 generations is "readily"** in Conrad's sense, or merely "within a budget".

## 11. Dependencies and status

| gate | status at revision 3 (about 20:50 UTC) |
|---|---|
| RBT-120 motor budget (with the Effector-bias walk) merged | pending (its designer's PR targets about 23:30) |
| RBT-121 audits A, B and C | **reported** (PRs #396, #395, #397); taken in (§0) |
| RBT-121 synthesis | pending |
| `smell_gain`, `eat_from`, and the A2–A5 physics flags | each needs its own designer, adversary and ruling (§3.2) |
| this design's hooks (§3.1; a code PR with byte-identity tests) | not started; after the ruling |
| `steer.py`, `gate.py`, `plant_holistic.py`, `readout.py`, `world.py`, `run_arm.sh` | specified here; written after the ruling |
| world gate G1–G9 | after the hooks and prerequisites, in PW |
| auditor D (history, #401) | **reported**; R2, R4, R6, R7, H35 and H71 are taken in (§0, revision 3) |
| design adversary, coordinator ruling | pending |
