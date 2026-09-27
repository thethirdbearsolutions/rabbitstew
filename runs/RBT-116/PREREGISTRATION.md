# RBT-116 pre-registration (DRAFT r5): the extradimensional bypass. Do holistic bodies cross the compass valley more readily than the Pioneer?

*Designer's **draft, revision 5** (2026-09-27, about 21:30 UTC), written under RBT-115 (reason (c) of the 2005 proposal).
It answers the design adversary's REDESIGN (narrow) verdict (PR #408, `runs/RBT-116/design-adversary/ADVERSARY.md` @
`e51aabf`), and the coordinator's ruling (22:15), which accepts all 9 MUST and 11 SHOULD items and raises SHOULD 4
to a MUST. §0 maps every item to the text. Revisions 1–4 (`c8e8389`, `88d95d7`, `62fbc97`, `577ef9e`) are
superseded, and their decisions are carried here where they still stand.*

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
  - with **crossover pinned at 0**;
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
- **Power (§7)** at 24 units, 40 members probed, with confirmation and plateaus derived from holding:
  - under the null, NEITHER 0.87 and false HOLISTIC 0.000;
  - under a U/N false-positive gap, false HOLISTIC 0.000;
  - a bypass in half the lines, 0.94;
  - a weak bypass (a quarter of lines), 0.36 [OPEN: G = 72].
- **Cost (§9).** About 420 CPU-h per world point at D = 16, or about 240 at D = 8. The gate decides D.

---

## 0. How revision 5 answers the design adversary and the ruling

| item | the adversary's finding (§9 wording, abridged) | r5's answer | where |
|---|---|---|---|
| **MUST 1** | the count veto blinds the call in PW (a two-nose steerer at F +1.29 is called STEERS on only 27%; a one-nose temporal steerer on 0%); the fixed draws are unscreened | **The count veto is replaced by a trajectory-identity veto.** The battery's draws are chosen from a 64-draw pool by a registered reachability screen on the positive controls. G8(a) and G8(c) are priced on the new call. | §1.1, §1.3 |
| **MUST 2** | T is undefined when Σ\|v\| = 0; 75% of a real holistic final's ticks are below 0.05 m/s | T's speed threshold is **0.25 × the member's own median CoM speed** (intact season). T := 0 and flagged when no tick qualifies. The excluded-tick share is reported per member. | §1.2 |
| **MUST 3** | G8(b) cannot fail on T because it never pays; it is fed by the root; "orthokinesis leaves T unchanged" is wrong (T ≈ net approach ÷ path) | **The claim is deleted,** and §1.2 states T ≈ net approach ÷ path length, which kinesis can raise by aggregation. G8(b) is now a **tuned, paying** area-restricted-search plant fed by a **wheel** nose: it must reach F ≥ 0.25 and then be called SMELL-USE or NONE, never STEERS. If no kinesis plant can pay, the registration says T is untested there. | §1.2, §4.3 G8(b) |
| **MUST 4** | G6 is the wrong inequality; crossover is missing from erosion; Q is asserted; the H:P loss ratio can decide a HOLISTIC verdict | **`--crossover-rate 0` in both faunas** (a new hook; every cited loss rate is mutation-only). G6 is now **(1 + s(F_MIN))(1 − u_f) ≥ 1.25 for both faunas**, with u_f measured on planted steerers, and D ∈ {8, 16}. **Q_f is derived** by the holding simulation at the measured s and u (`power.py` part 1). **The H:P loss ratio is a registered covariate** with a fixed sentence. | §2.4, §6.3, §7 |
| **MUST 5** | the smell transform is unnamed; every PW number came from C's un-centred model | **Named** (§4.2): a per-robot running-baseline log-contrast, `tanh(G · (ln Σ_i − b_r))`, with b_r the robot's EMA of its mean ln Σ over its food sensors (τ = 1 s), at G = 2.5. What a lone root nose reads is stated. **No number from C's kinematic model is cited in support.** G1, G2, Δ, G7 and G8 are all measured at the gate on this transform. G8(b) uses a non-root nose. | §4.2, §4.3 |
| **MUST 6** | G7 tests only the pirouette | G7 tests **every one-step intermediate**: pirouette (lone wheel nose → steering axis), lone-nose throttle, same-sign pair, and one-wheel. At 16 hosts × 16 draws, with a paired t bound. It passes only if none pays. | §4.3 G7 |
| **MUST 7** | a U/N false-positive gap gives false HOLISTIC 0.54 | **Every STEERS call must repeat on a 16-draw confirmation battery.** Generation 0's false-positive rate (identical U and N) is printed beside share_N(t), and a fall below it is flagged as purging. | §1.3, §5.3 I8 |
| **MUST 8** | HOLISTIC fires with no line crossed | **HOLISTIC (and PIONEER) MORE READILY require the A test AND an exact one-sided paired test on crossed lines** (discordant units). An A-only result is reported as "INCONCLUSIVE: holistic steers more, no line-level crossing". | §6.3 |
| **MUST 9** | re-run power with EPS_U ≠ EPS_N, derived Q, confirmation and M = 40; print the one-seed row | Done (`power.txt`). The crossing call moves from a share threshold to a count (≥ 3 of 40 confirmed, and ≥ 3 above N), because a share of 0.125 is unreachable for a trait held at Q < 0.31 after confirmation's sensitivity. The equivalence margin is rescaled. | §1.4, §7 |
| **SHOULD 1** | a rotated item can land on the spawn | θ is re-drawn from the same stream until no rotated live item lies within the clearance (0.8 m) of the root at spawn. Tested. | §1.1 |
| **SHOULD 2** | the rotation is valid only for rotation-invariant layouts | `--smell-decoy rotate` asserts, at construction, that the food layout rule is rotation-invariant, and refuses otherwise (R15). | §3.1 |
| **SHOULD 3** | is klinokinesis steering? | **Yes, if it approaches food up the real gradient:** STEERS means "uses smell information to approach food", which includes biased-random-walk chemotaxis. The ticket's "directed turning" is restated as "**directed movement toward food**". G8(b) measures whether undirected kinesis alone reaches the T bar. | §1.3 |
| **SHOULD 4 → MUST** | the starts are not at a peak in the world used | **A shared burn-in:** 12 generations of U-style truncation in the world point, with **lesioned smell** and every fix ON, from the RBT-113 finals, per unit and fauna. Its final population is generation 0 of U and N. The start-member rule for failed builds is stated. | §2.2 |
| **SHOULD 5** | what is the holistic "root"? | The root is the body synthesised from Node 0's first instance (`synthesis.py`'s root). A test pins that the Pioneer's root is the chassis. | §3.2 |
| **SHOULD 6** | income lost to root eating | Printed per fauna at the start (before burn-in): the committed rule against root eating. | §4.3 G9 |
| **SHOULD 7** | G7's n, CI and power | 16 hosts × 16 draws, paired t, with power at the expected prize printed. | §4.3 G7 |
| **SHOULD 8** | NEITHER's sentence overclaims | Rewritten: "confirmed steering did not reach and hold ≥ 3 of 40 members in more than 1 line in 4, on either body." | §6.3 |
| **SHOULD 9** | U − N wiring diagnostics | Nose count, and the share of members with any food-sensor → Effector path of gain > 0.1, per probe, U against N. | §6.4 |
| **SHOULD 10** | the proposal assay misclassifies | Parent and child are called on the **same** draws. The parent must be NONE on a confirmation battery too. The assay's detection floor (about 3 × 10⁻⁴ per child) is stated, and it cannot confirm paper 8's rate. Stage 1 no longer uses a count screen. | §5.2 |
| **SHOULD 11** | B's planted +Δ holding pilot | Part of G6: one unit per fauna, a planted steerer at F ≈ F_MIN, run 24 generations under the registered D. It must be held. | §4.3 G6 |
| **ruling: the world as a parameter** | the owner may adopt a world sweep | §4 is a parameter block. Every world point gets its own G1, G2, G7 and G9, its own power re-run and its own verdict. W1 is PW under the named transform. | §4 |

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
| **decoy** | the **live** layout rotated about the world origin by θ ~ U[30°, 330°], drawn per draw from a registered stream, and **re-drawn until no rotated live item lies within 0.8 m of the root at spawn** (SHOULD 1). The rotation is applied to item positions **before** the transform. | unchanged: eating, regrowth, depletion and the real items |
| **lesion** | 0 (before the transform: the raw sum is set to the transform's zero-information value, so a lesioned nose reads a constant) | unchanged |
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

**F_MIN.** 0.25 is about the size of kinesis noise between real and decoy smell (RBT-106 F6). **[OPEN]** Its
absolute form is kept. The relative variant, max(0.25, 0.2 × food_intact), is printed beside the call.

### 1.4 From individuals to lines

- All **M = 40** members of a line are probed at generations 12, 24, 36 and 48 (MUST 9). share(t) is the fraction
  that STEER.
- **A_f** = mean over those t of [share_U(t) − share_N(t)], per unit and fauna: the time-averaged, null-corrected
  share. "More readily" means sooner and more often.
- **A line has CROSSED** if, at generation 48, U has **≥ 3 confirmed steerers of 40, and ≥ 3 more than N.**
  - The r4 share threshold (0.25, then 0.125) is dropped. After confirmation, a true steerer is called STEERS with
    probability about SENS² (about 0.4 at the adversary's measured single-call 0.63). A trait held at a plateau below
    about 0.31 could then never "cross", and a real low-plateau bypass would read as the clean "no" (`power.txt`).
  - With the confirmed false-positive rate about EPS² (≤ 0.0025 even at the G4 cap), 3 of 40 is far outside noise.

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
  likely, and that reads INCONCLUSIVE 0.81–0.96 at n = 24 (`power.txt`).
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
    plateaus at Q ≈ 0.15 under truncation. Q ≈ 0.47 needs about 1.39 (`power.txt` part 1).
  - If neither passes, D = 16, and the headline carries: "at the registered draws, a steerer at F_MIN grew by only
    (1 + s)(1 − u) = … per generation on the [fauna]; a NEITHER verdict is conditional on that."
  - Both faunas share one D, because they share every run.
- **Plateaus.** Q_f is derived by `power.py` part 1 (the adversary's `hold.py`, transcribed at crossover 0) from the
  measured σ_P, u_f and D, and `power.py` is re-run before launch. On the priors, D = 16 gives Q_H ≈ 0.70 and
  Q_P ≈ 0.47. D = 8 gives 0.57 and 0.15.
- **The H:P loss-ratio covariate.** The assay measures each fauna's loss rate on its own lines (§5.2). **If a HOLISTIC
  verdict fires with u_H < 0.5 × u_P**, it carries: "consistent with lower erosion of steering under the holistic
  operator; the comparison is at each body's default operator." Symmetrically for PIONEER.
- **The default operators** (unchanged from r2): the bypass is a claim about the holistic space *as explored by its
  operator*. The headline states the realised u_H and u_P.

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
| `--draws-final K` (boundary re-scoring) | B3 | optional: G6 tests it as a third option if merged | yes, through holding |
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
| smell | `--smell log --food-decay 1.5`, plus the transform of §4.2 at **G = 2.5** |
| eating | `--eat-radius 0.35 --eat-from root` |
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
- Σ_i(t) = Σ_items exp(−d_i/decay) + 10⁻⁶, over live items, at the sensor's geom centre in xy (the committed
  `_intensity` sum, before any squash);
- ℓ_i(t) = ln Σ_i(t);
- b_r(t) is the robot's **running baseline**: an exponential moving average, time constant **τ = 1 s**, of the mean of
  ℓ_i over its food sensors. It is initialised at t = 0 to that mean, so every nose reads 0 at spawn;
- **reading_i(t) = tanh(G · (ℓ_i(t) − b_r(t))), with G = 2.5.**

**What each body's noses read:**
- **A lone nose** (any Part, **including the root**) reads the temporal contrast of its own reading against its recent
  past, ≈ G·τ·d(ln Σ)/dt while it moves.
- **Several noses** each read their deviation from the robot's recent mean: lateral contrast plus temporal contrast.
- **The Pioneer's three noses** (chassis and two wheels) all read live signals. The chassis nose is **not** zeroed.
- **Lesion** sets Σ_i to a constant for every sensor, so every reading decays to 0.

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
- a **NEITHER** verdict under it is the *stronger* "no": the transform was generous to the bypass.

**[OPEN]** A level-plus-centred two-channel alternative is the transform designer's option. If it is chosen instead,
this section is rewritten before the gate, and no gate result carries across.

**G ∈ {2.5, 10}.** G = 2.5 is primary. At G = 10, contrasts saturate (median |c| about 0.6) and later nose steps pay
about 2% (the audit adversary's §6b). G = 10 is used only if G = 2.5 fails G2 and G = 10 passes both G2 and G7, and it
is then a different world point, with its own column.

### 4.3 The per-world gate (pre-launch; `gate.py`, after the ruling; every fairness row ON, through `steer.py`)

| | check | pass |
|---|---|---|
| **G1** | **Perception pays, on the Pioneer.** RBT-106's routed compass installed at a ∈ {2, 6, 16, 32}, signed per host by its measured travel direction (`scripts/travel_direction.py`, H35), in 16 burn-in-final designed hosts from 16 units. 16 stage-2 draws. | Some rung has a mean F with a lower bound > 0, and at the smallest such rung (the **first paying rung**) ≥ 12 of 16 hosts PASS on stage 2. |
| **G2** | **Perception beats coverage, in this world with every fix ON.** The first paying rung's F on the G1 hosts, against the coverage gain the burn-in bought: burn-in-final blind yield minus RBT-113-final blind yield, both measured here. | F ≥ that coverage gain. **[OPEN]:** a weaker G2 (≥ 0.5×) needs the coordinator's ruling. |
| **G6** | **Holding** (§2.4). σ_P by B's `noise.py` method at D ∈ {4, 8, 16} on burn-in finals. u_f from 40 children of each STEERS host of G8(a) and G8(c), same draws, crossover 0. **SHOULD 11:** B's planted-Δ pilot: one unit per fauna, 8 planted steerers at F ≈ F_MIN, 24 generations of U at the chosen D. | Sets D by (1 + s_f)(1 − u_f) ≥ 1.25. The pilot's steerers must be held: confirmed share at generation 24 ≥ 0.25 × the confirmed sensitivity. Otherwise, conditional-sentence mode (§2.4). |
| **G7** | **The Pioneer's valley is still there** (MUST 6, SHOULD 7). On the G1 hosts, at the first paying rung's gain, 16 hosts × 16 draws, each against the unmodified host: **(i)** the pirouette (one wheel nose → a global unit → both drive Effectors, the steering axis; paper 8's c); **(ii)** the lone-nose throttle (one wheel nose → the difference axis); **(iii)** the same-sign pair (both wheel noses + → one unit → both Effectors); **(iv)** one wheel (one wheel nose → that wheel's Effector only). Both signs of each. | Passes only if **no intermediate has a paired-t lower bound > 0** on its prize. Its power to detect a prize of +0.10 at 16 × 16 is printed (SHOULD 7). The full table (rungs × intermediates) is printed as the Pioneer's valley in this world. If G7 fails, the valley is not there, and the point is reported as such, not run. |
| **G8** | **The call can fire, and stay silent, on the arms' own hosts** (R7). 4 designed and 4 holistic burn-in-final hosts from every unit (192): **(a)** the Pioneer compass plant at the first paying rung; **(b)** **a paying kinesis plant (MUST 3)**: one **wheel** nose → a thresholded global unit → throttle (slow) and a fixed-sign turn (turn more above the threshold): area-restricted search with no heading term, tuned over threshold × gain × turn sign on 4 screening draws to maximise F; **(c)** the holistic tuned plant: two food sensors on the two expressed Parts of distinct Nodes most separated across the host's measured CoM heading, a global unit fed ±, linked ±w to the Effectors either side, 2 signs × w ∈ {4, 16, 64}, best by F on screening draws; **(d)** a sensorless full-throttle tumbler (A's S2 rod, hinge and ball variants); **(e)** the same bodies with two **unwired** food sensors. | **(a)** STEERS (confirmed) on ≥ 50% of hosts, pooled (the r4 bar of 75% assumed the count veto; it is re-priced on the new call from the adversary's steer2 sensitivity). **(b)** Among hosts where it reaches F ≥ 0.25, **0 STEERS**. If it reaches F ≥ 0.25 on fewer than 4 hosts, the registration states that undirected kinesis cannot pay in this world, so T's discrimination is untested but unneeded here. **(c)** STEERS on ≥ 20% of holistic hosts pooled, and on ≥ 1 host in ≥ 18 of 24 units. **(d)** and **(e)**: NONE on every body. The realised (a) and (c) shares set SENS for `power.py`; G4's rate sets EPS. More than 4 units flagged: no launch. |
| **G4** | **False positives.** `steer.py` on 64 burn-in-final members per fauna, all four conditions. | Confirmed false STEERS ≤ 0.05 per fauna (sets EPS). Every zero-food-sensor genome gives identical trajectories, so it is NONE. |
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
    rate** is the share of children of STEERS parents that are not STEERS: the per-fauna u behind §2.4's covariate.
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
- **I8 (MUST 7).** EPS_0, the confirmed false-STEERS share at generation 0 (identical in U and N), is printed beside
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
   McNemar p on (b, c) < 0.05 (MUST 8).
2. **PIONEER MORE READILY:** mirrored.
3. **NEITHER CROSSES:** the exact upper 95% bound on P(a line crosses) is below 0.25 for both faunas. The sentence is
   (SHOULD 8): *"On neither body did confirmed steering reach and hold ≥ 3 of 40 members in more than 1 line in 4,
   within 48 generations of truncation selection, at world point W."*
4. **EQUIVALENT:** the CI on d lies inside ±**0.015** and min(k_H, k_P) ≥ 3.
   - Both bodies must have crossed.
   - 0.015 is half the mean d of the weak bypass at this readout.
   - It is kept narrow and almost never fires, which is stated rather than widened.
5. **INCONCLUSIVE: holistic steers more, no line-level crossing:** the A test passes and the crossing test does not.
   Reported as such, never as HOLISTIC.
6. **INCONCLUSIVE** otherwise.

**The headline is fixed in code, one per world point.** It gives:
- the verdict and the design sentence;
- d and each A with CIs, k_H and k_P with bounds, (b, c);
- STEERS and SMELL-USE shares;
- **the covariates:**
  - the realised u_H and u_P, with the loss-ratio sentence (§2.4) when it applies;
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
- **the share of members with any food-sensor → Effector path of absolute gain > 0.1.**

### 6.5 Valley depth (descriptive)

From the assay and U's probes, per fauna:
- the net yield of SMELL-USE members, and of members with F ≤ −0.25 (smell used against food), against NONE members
  of the same line and generation;
- the net yield of the first STEERS members against their generation's mean.

On the Pioneer, G7's table is the valley. On the holistic body, this is the only depth measure, and it is
descriptive.

## 7. Power (`power.py` → `power.txt`, re-run at the gate with the measured inputs)

**Part 1: holding** (crossover 0, Δ = F_MIN, B's RBT-113 noise, the priors u):

| fauna | D | u | s | (1 + s)(1 − u) | plateau Q |
|---|---|---|---|---|---|
| holistic | 8 | 0.146 | 0.60 | 1.37 | 0.57 |
| holistic | 16 | 0.146 | 0.72 | 1.47 | 0.70 |
| designed | 8 | 0.28 | 0.66 | 1.20 | 0.15 |
| designed | 16 | 0.28 | 0.93 | 1.39 | 0.47 |

On the priors, G6 picks **D = 16**: at D = 8 the designed compass grows at only 1.20 and plateaus at 0.15.

**Part 2: the readout**, at n = 24, M = 40, SENS 0.63 per call (0.40 confirmed), EPS 0.02 per call (0.0004 confirmed),
and D = 16's plateaus (Q_H 0.70, Q_P 0.47). 300 readouts per row:

| scenario | HOLISTIC | PIONEER | NEITHER | EQUIV | INCONCL (H steers, not crossed) | INCONCL |
|---|---|---|---|---|---|---|
| null: both at the Pioneer's prior floor (p 0.04) | **0.000** | 0 | **0.873** | 0 | 0.003 | 0.123 |
| null: neither ever crosses | 0 | 0 | 1.000 | 0 | 0 | 0 |
| null + U/N EPS gap, holistic 0.04 vs 0.01 | **0.000** | 0 | 0.893 | 0 | 0 | 0.107 |
| null + U/N EPS gap at the G4 cap, 0.05 vs 0.01 | **0.000** | 0 | 0.877 | 0 | 0 | 0.123 |
| null + one holistic unit at share 1.0 | 0.003 | 0 | 0.770 | 0 | 0 | 0.227 |
| weak bypass, p_H 0.25 | **0.363** | 0 | 0.053 | 0 | 0.043 | 0.540 |
| bypass, p_H 0.5 | **0.940** | 0 | 0 | 0 | 0.007 | 0.053 |
| strong bypass, p_H 0.75 | 1.000 | 0 | 0 | 0 | 0 | 0 |
| bypass p_H 0.5, holistic held at the designed u (Q 0.24) | 0.583 | 0 | 0 | 0 | 0.093 | 0.323 |
| bypass p_H 0.5 at a low plateau (Q 0.12) | 0.097 | 0 | **0.373** | 0 | 0.217 | 0.313 |
| both cross, p 0.5 each (unequal u) | 0.040 | 0.003 | 0 | 0 | 0.143 | 0.813 |
| both cross, p 0.5, equal u | 0.010 | 0.020 | 0 | 0 | 0.010 | 0.960 |
| Pioneer more, p_H 0.1, p_P 0.5 | 0 | **0.470** | 0 | 0 | 0 | 0.530 |

**Reading:**
- **Level.**
  - Under every null, including the U/N false-positive gap that gave false HOLISTIC 0.54 in r3, HOLISTIC fires at most
    0.003. Confirmation plus the crossing test closes the gap.
  - **One influential unit** at share 1.0 moves HOLISTIC to 0.003: the t CI, the sign-flip p and the crossing test
    all absorb it (R10).
- **The clean "no" is reachable where expected:** NEITHER 0.87 at the Pioneer's prior floor.
- **Detection:**
  - a bypass in half the lines, 0.94;
  - with the holistic body held at the designed body's erosion, 0.58;
  - a weak bypass (a quarter of lines), **0.36**, which is the weak spot.
- **A real bypass at a very low plateau (Q 0.12) still reads NEITHER 0.37.** That is a trait held in about 1 member in
  8, which the instrument confirms in about 1 in 20. NEITHER's sentence is bounded accordingly (§6.3), and G6's rule
  exists to keep plateaus above this.
- **Unequal erosion leans toward HOLISTIC when both cross** (HOLISTIC 0.040, "H steers more" 0.143, against 0.010 and
  0.010 at equal u). That is the adversary's point, and it is why the loss-ratio covariate is registered.
- **[OPEN] The weak spot.** The adversary's rule: buy G = 72 only if the re-run leaves the weak bypass below 0.5. It
  does (0.36). Whether to buy +50% at each world point is for the coordinator, in the light of the sweep's budget.
  This model cannot price G = 72 honestly, because p itself grows with G.

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
| eating | `--eat-from root` (root = Node 0's first instance) | eats from the chassis |
| **smell transform** | §4.2 at the world point's G (MUST 5) | all three noses live |
| **T's speed threshold** | 0.25 × the member's median CoM speed per intact season (MUST 2) | — |
| **decoy** | rotate; θ stream keyed on the start seed; re-drawn for spawn clearance; rotation-invariance asserted (SHOULD 1, 2) | — |
| terrain | `--terrain random`, penetration recorded (H71) | sinks up to 0.35–0.57 m, unfixed |
| draws | D from G6 | — |
| vocabulary | `--brain-model foraging` | three food noses |

The readout prints this table as run, from each run's `config.json`.

## 9. Cost and packing (per world point)

**Per generation**, extrapolated from RBT-113's 50 CPU-s at D = 2, ×1.25 for movers: **about 250 CPU-s at D = 8,
and about 500 at D = 16.** G5 re-costs this.

| item | CPU-h at D = 16 | at D = 8 |
|---|---|---|
| evolution per unit: B 12 + U 48 + N 48 = 108 generations | 15.0 | 7.5 |
| probes per unit: 9 probe points × 2 faunas × 40 members; stage 1 (8 seasons), stage 2 (64 seasons, for an assumed 20%), confirmation (32 seasons, for an assumed 10%); 0.35 s per season | 1.7 | 1.7 |
| proposal assay per unit (400 children, the same stages, with parent confirmation) | 0.8 | 0.8 |
| **one unit** | **about 17.5** | **about 10** |
| **24 units** | **about 420** | **about 240** |
| gate (G1, G2, G4–G9, draw screen) | about 10 | about 8 |

**Packing** (RBT-113's RUNNER; `runs/README.md`):
- **one arm per session at `WORKERS=4`**, with the durable loop. That is about 4.4 h per session at D = 16
  (budgeted at 6 h), or 2.5 h at D = 8.
- **24 sessions per world point.** They run in waves of 6–8.
- A unit's B, U and N stay in one arm, so pairing never crosses sessions.
- A lost session drops its unit, and the readout re-runs `power.py` at the realised n. It is not re-simulated.

**Cheaper options, for the ruling:**
- `--draws-final 16` over a D = 4 base (auditor B's hook) re-scores only the truncation boundary. It costs about as
  much as D = 7, which is about 45% of D = 16. G6 tests it if it merges.
- N on 12 of the 24 units, with pooled-N subtraction: −30%.

n is not cut below 24, and D is not cut below G6's rule.

**Committed per arm:**
- `config.json` ×3, `command.txt`, `platform.txt`, `commit.txt`;
- `steer.txt` (per probed member, condition and draw);
- `assay.txt`;
- `wiring.txt` (§6.4).

The bulk goes to `ckpt/rbt-116-<W>-<unit>`.

## 10. What the re-read should attack first

1. **The trajectory-identity veto.** Can a genome whose smell changes its path only trivially (sub-millimetre)
   escape the veto and pass by noise? Condition 1's F bound and confirmation should stop it. Is that enough, or does
   the veto need a path-difference threshold instead of 1e-9?
2. **The named transform's lean** (§4.2). Is "a NEITHER under a generous transform is the stronger no" sound? Is
   τ = 1 s right for 15 s seasons and PW's patch spacing?
3. **G8(b).** Can an area-restricted-search plant on a wheel nose pay in W1? If not, is "T untested but unneeded"
   honest?
4. **The burn-in.** Is 12 generations with lesioned smell enough to reach a coverage peak in W1, for both bodies, and
   does it select against noses? Lesioned noses are neutral, and wiring erodes under drift at 0.42× (B5).
5. **G6's margin (1.25), and D = 16's cost at each world point.**
6. **The crossing count (≥ 3 of 40, ≥ 3 above N)**, in place of a share.

## 11. Dependencies and status

| item | status (about 21:30 UTC) |
|---|---|
| RBT-121 audits A–D and the audit adversary | reported and taken in |
| RBT-116 design adversary (PR #408, `e51aabf`) and ruling (22:15) | taken in (§0) |
| RBT-120 gear budget (with the Effector-bias walk) | pending |
| smell transform flag (§4.2), `eat_from`, ball cone and hinge ranges, settle | each needs its own designer, adversary and ruling |
| this design's hooks (§3.1) | after the ruling; a code PR with byte-identity tests |
| `steer.py`, `gate.py`, `readout.py`, `world.py`, `run_arm.sh`, the G8 planters | specified here; written after the ruling |
| per-world gates | after the prerequisites and hooks |
| the owner's world-sweep decision | pending; §4 is ready for 1–3 points |
| re-read by the design adversary; the coordinator's ruling | pending |
