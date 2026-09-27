# RBT-129: the world sweep (DRAFT pre-registration)

> **Status: DESIGN ONLY. Nothing has run and nothing runs from this file.** It is the Phase-2 main programme's
> design (epic RBT-123; plan *Phase 2 plan: the world sweep*, ratified 2026-09-27 at about 21:30 UTC). A design
> adversary follows, then a coordinator ruling. **No arm launches until the gates of §11.1 are met:** the fairness
> set (RBT-120, 124, 125, 128) merged, the RBT-125 world gate passed on real bodies, RBT-126's readout and breeding
> ruling in hand, and this design's own small code ticket (RBT-129a, §5.6) merged.
>
> `power.py` → `power.txt` in this directory holds every power and budget number quoted below. It runs no
> simulator.

## 0. The design in one table

| question | decision | § |
|---|---|---|
| what is swept | clutter density × work price × food layout × smell channel, 5 × 5 × 3 × 2 = 150 candidate points | 3 |
| full factorial? | **no, except for the cheap census.** A full-factorial **habitability census** (150 points, 3 seeds, 60 seasons), then an **adaptive coarse-to-fine map**: 36 coarse points at n = 8, then at most 16 refinement points chosen by a mechanical rule, and at most 20 points extended to n = 16 | 4 |
| selection | **the ecology at every point**, with the regime stated (R5). `evolve` (imposed selection) appears only inside RBT-116, at its registered points | 5.4 |
| arms per point and seed | S (side by side, 300 seasons), M (merged at season 60, to 300), N (matched drift null, on half the seeds) | 5 |
| per-point outcomes | habitability; income (side by side); fauna share (merged, against the null); perception (intact − decoy, STEERS, planted negatives); regime; R8 levers | 5, 6 |
| per-point calls | body: H-WIN / D-WIN / TIE / CONTINGENT / SATURATED / UNDECIDED / EXCLUDED; perception, per fauna: PERCEIVES / SMELL-USE / NONE / VOID | 6 |
| multiplicity | Benjamini–Hochberg at q = 0.10 within each family of per-point calls; Holm at α = 0.05 over four registered map-level tests | 7 |
| sub-studies | RBT-118 at three fixed points and up to two rule-chosen ones; RBT-116 at W1 (its own) and one rule-chosen W2 | 9 |
| power | bounded by floors and ceilings with RBT-118's and RBT-121's realised noise (§10) | 10 |
| budget | at most about 2,800–3,400 core-h for the sweep itself (70–86 h of wall on ten 4-core sessions), sub-studies extra | 11 |
| what falsifies "it depends on the world" | one body wins every decided point with no opposite call in either layer, or no world term is detectable (§8) | 8 |

## 1. What binds this design

**The question.** RBT-123 asks for *a map of where each body plan wins, and where perception pays enough to evolve,
with the allowances closed*. It answers the 2005 proposal (`docs/origins/`) as "it depends on the world, and here is
how", rather than as one verdict that hinges on one setting. Reason (a) of the proposal, that body-specific strategies
exploit their own quirks, **predicts** such a dependence; this design is written so that the dependence can fail to
appear (§8).

**Why a sweep, from the record.**
- The late holistic income lead of the default world is a work-price lead on random terrain. It reverses below a
  median 0.018/kJ, and on flat ground at 0.03/kJ (RBT-118 prior §4, §4a; 21 of 29 paired histories).
- The terrain taxes the designed body's food, not its work: about 0.7 items a season (`probe_flatwork.txt`).
- The break-even price moves with the terrain: 0.018/kJ random (range 0.001–0.033, defined on 25/29), 0.053/kJ flat
  (range 0.004–0.081).
- Which fauna holds its own world depends on the world (RBT-118 §3): the designed fauna is the only one to starve after
  a change of world (8 of 20 stress arms), and in the patchy world the lead goes to whichever fauna carries a compass.
- The world pays blind motion more readily than perception (R4), and the ecology selects hard on viability and weakly
  above it, as a function of income ÷ living cost (R5; RBT-121 adversary §4).
- **All of these are pre-fairness numbers.** The motor budget, joint ranges, `effector_bias_sigma` and
  settle-until-rest will move both bodies' work bills. The break-evens above are therefore priors for where to look,
  not predictions of where the boundary is. The price axis brackets them widely (§3.2) for that reason.

**How others varied the world** (`docs/prior-art/REVIEW.md`, as corrected by its citation check).
- **Auerbach & Bongard (2014)** varied environmental complexity and found that complex environments evolved more
  complex bodies **only when complexity carried a cost**. Here, the work price is that cost, and it is an axis.
- **Miras & Eiben (2019):** environments that look different to people can select for the same bodies. So "we changed
  the world" is not evidence that the selection changed; the regime and the levers are measured at every point
  (§5.3), and T1 tests whether the world terms matter at all.
- **Kussell & Leibler (2005), Stephens (1991):** sensing beats blind strategies only when the world changes often
  enough, and tracking is least valuable when uninformed alternatives already pay about the same. This motivates the
  conditional moving-patch layout (§3.3), and predicts NONE in U.
- **Stanton & Channon (2013):** many difficulties at once beat a ramp. Each point here is its own world from founding,
  not a ramp from an easier one.
- None of the reviewed systems evolves bodies in a physics ecology beside a designed body (REVIEW §2), so no prior map
  exists to compare with.

**How R1–R12 (`runs/RBT-121/SYNTHESIS.md`) are met.**

| rule | how this design meets it |
|---|---|
| R1 budgets, R2 ranges, R3 rest, R9 fairness defaults | every arm runs under `--fair` (RBT-128), which carries RBT-120's motor budget at c = 1.77, RBT-124's cone/hinge ranges, `effector_bias_sigma` and settle-until-rest, and the mass budget 15.34. The guard refuses a mixed-fauna run without it. R3's closing test is repeated on the densest registered terrain (census check C3, §5.1) |
| R4 the world pays perception on the path | the smell channel is an axis, not an assumption. The world gate (RBT-125) must pass before the sweep launches, and the census measures the nose-step and speed-step margins on real bodies at 12 cells (§5.1) |
| R5 selection that can see the gain, regime stated | the ecology at every point; RBT-126's regime readout on every arm; a **resolvability check** decides whether a no-difference share result can be called TIE or only SATURATED (§6.2) |
| R6 operator parity | the default operators for both faunas at every point, stated. If RBT-124/128 rule `--structural-rate-scale` into `--fair`, it applies everywhere |
| R7 behaviour by instrument, with planted negatives | perception is called only by intact − decoy plus RBT-116's STEERS instrument, with its planted positives and negatives re-run **at every point** (§5.3) |
| R8 body levers | the per-line lever report (RBT-120's `motors.py`, extended by RBT-124) on the probed members of every arm; a body call that coincides with a lever flag is marked LEVER, not WIN (§6.1) |
| R10 controls able to fail, side effects | the drift null N, the planted set, the null-centring check K2, the census's side-effect table against the committed world (§5.5) |
| R11 bounded power, no single seed | §10: every power number is bounded by a floor and a ceiling on the effect and on the noise; the seed is the unit, n ≥ 8 |
| R12 corrections propagate | `config.json` carries platform and versions (RBT-127); every world block is written to the run before season 0 |
| plan: "no single world is the headline; terrain and price beside any income claim" | every call is a point call carrying its world block; the headline is the map's summary statistics (§7) |

## 2. The world block

Every point is one **world block**: a flat dictionary of dotted config paths, written into each arm's `config.json`
before season 0, and exported as `runs/RBT-129/worlds/<id>.json` at launch. RBT-116's and RBT-118's designs take the
same block as their world parameter (§9). The point id is `c<clutter>-p<price>-<layout>-<smell>`, e.g.
`c1-p030-PW-G`.

**Fixed in every block** (not axes):

| field | value | source |
|---|---|---|
| fairness | `--fair` (RBT-128's ruled set) | R9 |
| eating rule | as RBT-125 rules it (candidate: `eat_from root`), the same at every point | R4, C4 |
| smell transform when on | RBT-125's ruled channel, reading tanh(G · (ln S − b)) with b a per-robot running baseline, at the **registered G** (candidate 2.5) | RBT-125, RBT-116 r5 §4.2 |
| breeding rule | as RBT-126 rules it, **the same at every point** (§5.4) | R5 |
| ecology | capacity 60 per fauna, pooled 120 after a merge; group size 4; initial energy 3.0; birth threshold 3.0; birth cost 1.0; max age 60; staggered founder ages | the committed default world (RBT-90, RBT-107) |
| living cost | 0.25 a season at every point, **not recalibrated per point** (see below) | the committed default world |
| bout | one 15 s foraging season in a shared arena of 4; food items 12, value 1, eat radius 0.35 | the committed default world |
| founders | random bodies for the holistic fauna; the Pioneer with random controllers for the designed fauna. No planted founders (RBT-118 §3: planted founders make it a comparison of controllers) | RBT-118 §6.7 |
| operators | the defaults, stated (R6) | R6 |

**The living cost is not recalibrated per point.** Recalibrating it per layout or per price would tune each world to
the bodies' founder incomes, which is the tuning the plan forbids ("tuning one world until holistic bodies do something
interesting would repeat the weight-class artefact in a subtler form"). The regime that results is measured and reported
at every point, and the habitability census says where a fauna cannot live. **One registered fallback:** if the census
finds a layout uninhabitable for *both* faunas at more than half of its 50 census points, that layout's living cost
is set by the rule c_L = 0.25 × ḡ_L / ḡ_U, with ḡ the mean over the two faunas (equal weights) of the founders' median
gross income in seasons 0–10 at `c1-p030-*-G`. The change is then reported as a world change beside every call in
that layout.

## 3. Axes and levels

### 3.1 Terrain: clutter density c

**Definition.** c is obstacle density relative to the committed random terrain: 14 obstacles within 2.6 m, about
0.66 per m². Obstacles lie within R_food − 0.4 m (2.6 m for the 3 m layouts, 3.6 m for PW's 4 m disc), and their
number is N = round(14 · c · ((R_food − 0.4)/2.6)²), so the density is the same in every layout. Heights and footprints
keep their committed log-uniform ranges (0.03–0.3 m, 0.15–0.7 m). c = 0 is `terrain flat`, as in RBT-101/107's flat
arms. Terrain is redrawn every season from the terrain stream, as in the committed ecology.

| level | N (3 m layouts) | N (PW) | why |
|---|---|---|---|
| **0** (flat) | 0 | 0 | the designed body's best ground; the RBT-118 reversal |
| 0.5 | 7 | 13 | refinement only (between 0 and 1) |
| **1** | 14 | 27 | the committed random terrain |
| 1.5 | 21 | 40 | refinement only (between 1 and 2) |
| **2** | 28 | 54 | the wheel tax doubled; tests whether the tax is monotone, or traps the wheels |

Bold levels form the coarse grid. The committed data give one density only, so whether the wheel tax is linear in c is
unknown. c = 2 is the highest level because R3's drift and trapping grow with clutter; census check C3 flags it if the
settle fails there.

### 3.2 Work price p

**Levels (per kJ): 0.01, 0.018, 0.03, 0.053, 0.08.** The coarse grid is {0.01, 0.03, 0.08}, and the refinements are
{0.018, 0.053}.
- 0.03 is the committed price (paper 5).
- 0.018 and 0.053 are RBT-118's median break-evens on random and flat terrain. They are also, within 5%, the geometric
  midpoints of the coarse levels (0.0173 and 0.049), so the refinement is a bisection in log price.
- 0.01 lies below the random-terrain break-even's median and near the bottom of its range; 0.08 is above the flat
  break-even's range top (0.081 at season 599 is the one exception), and is RBT-99's stress level, where 3 of 10
  unchanged designed faunas starved.
- The range is 8×. It is wide on purpose: the fairness set will move both bodies' work bills, and so the break-evens.
- **Not swept:** a price that makes blind coverage's optimum speed interior (C3's lump break-even is about 0.47/kJ,
  16× the committed price). At such a price the census would find the committed economy uninhabitable. It is left
  to a later registration with a recalibrated economy.

### 3.3 Food layout L

| layout | definition (flags) | what it asks |
|---|---|---|
| **U** (uniform, instant) | the committed world: 12 items uniform over a 3 m disc, instant regrowth at a fresh random spot, `smell sum`, decay 1.0 | coverage; no depletion (C5); nothing to remember |
| **HP** (patchy) | RBT-106's HP world: `--food-patches 3 --patch-radius 0.6`, otherwise U | concentrated food with instant regrowth inside the patches |
| **PW** (perception-demanding) | `--food-patches 2 --patch-radius 0.4 --food-radius 4.0 --regrow-delay 60` (own-spot regrowth, arena food carried across seasons), `--smell log --food-decay 1.5` | depletion, and patches that a blind body misses |
| MP (moving patches, **conditional**) | PW, with each arena's patch centres redrawn every k seasons (k registered in RBT-129b) | a world that changes often enough to repay a sensor (Kussell & Leibler 2005) |

- The smell combination rule and decay are part of the layout (PW's `log`/1.5), not part of the smell axis. The smell
  axis toggles only the RBT-125 channel. This keeps the smell axis a one-knob contrast; its cost is that "legacy smell"
  in PW is not the committed smell. That is stated wherever a PW-legacy point is cited.
- **MP is conditional.** The code has no moving patches (`simulation.py:set_food_state`: in a persistent arena the spots
  and centres "do not move"). In PW's persistent arenas a patch site is fixed across seasons, so a body could in
  principle learn a place without smelling it. The rotated decoy separates the two (it moves the smell field, not the
  food), but MP removes the possibility. MP enters Stage 2 only if a flag ticket (RBT-129b) lands with the same
  review discipline, at three points (c1 × {0.01, 0.03, 0.08} × G). It is not budgeted in the core total.
- **Rotation invariance.** The decoy is valid only when the layout's distribution is rotation-invariant (RBT-116
  adversary §2.3). U, HP, PW and MP all draw patch centres and items uniformly in a disc
  (`simulation.py:_draw_patch_centres`), and the clutter is not rotated. So every registered layout qualifies. The
  instrument's own assertion is kept.

### 3.4 Smell s

**Levels: `L` (legacy, no transform) and `G` (the RBT-125 channel at its registered G).**
- G is RBT-125's to register; the candidate is 2.5 (`probe_gprop.txt`). G = 10 is not a level: if RBT-125 registers 10,
  then 10 is G.
- If the world gate fails, the sweep runs `L` only, and the perception map is reported as "not measured: the world
  gate failed", not as a finding about perception.

### 3.5 What is not swept, and why

- **The breeding rule** is not an axis. It changes the economy's selection above viability, which would double the
  grid. It is fixed at RBT-126's ruling, and the regime is reported instead (§5.4).
- **Group size, capacity, item count, the living cost:** held at the committed values (RBT-118 §3 has one magnitude of
  each; sweeping them is a later registration).
- **The founding contest** (merging at season 0) is RBT-118's, at its points (§9.1).

## 4. Why coarse-to-fine, and the stages

**A full factorial** of the 150 candidate points at n = 8 would cost about 5,300 core-h (§11), and most of it would
buy precision far from any boundary. At the corners of the prior map, predicted |H − D| is 0.4–1.5 items a season
(`power.txt` §1). A **fractional factorial** would alias the terrain × price interaction, which is the one interaction
the record already shows (the break-even moves from 0.018 to 0.053 between terrains). So:

- **The census is full factorial** (150 points, cheap), because habitability and the regime can change anywhere,
  including non-monotonically.
- **The map is coarse-to-fine.** The two continuous axes, price and clutter, are expected to act monotonically on the
  income difference: dearer work favours the body that spends less, and clutter taxes wheels (RBT-118 §4, §4a).
  Bisection along a monotone axis finds a boundary at a fraction of a factorial's cost. Layout and smell are
  categorical, so they are crossed in full at the coarse stage (layout) or on a registered subset (smell).
- **Monotonicity is itself checked, not assumed.** The census's full grid and the Stage-1 grid both test it (§7, M7). A
  non-monotone axis sends its extra points to Stage 2a by the same rule.

### 4.1 The stages

| stage | points | seeds | seasons | purpose | calls |
|---|---|---|---|---|---|
| **P** pilot | 3: `c1-p030-U-L` (the committed world under `--fair`), `c0-p030-U-L`, `c1-p030-PW-G` | 4 | 300 | measure cost per arm-season under `--fair`, the null's share SD, the per-seed SDs; dry-run the logging, the instrument and the planted set | **none** (exploratory) |
| **0** census | the full 5 × 5 × 3 × 2 = 150 | 3 | 60, S only | habitability, founder solvency, the regime early; R4 margins at 12 cells | habitability layer only |
| **1** coarse map | 27 at G: c ∈ {0, 1, 2} × p ∈ {0.01, 0.03, 0.08} × L ∈ {U, HP, PW}; 9 at L: c = 1 × the same p × L | 8 | 300 | the map | all layers |
| **2a** refinement | ≤ 16 new points by rule R-A | 8 | 300 | locate boundaries | all layers |
| **2b** extension | ≤ 20 UNDECIDED points by rule R-B | +8 (n = 16) | 300 | resolve near-boundary points | all layers |
| **3** sub-studies | RBT-118 and RBT-116 at registered points | their own | their own | their own questions | their own |

**What the pilot may change.** After Stage P, `power.py` is re-run with the pilot's measured per-seed SDs, null share
SD and cost per arm-season. Only those constants may change. The grid, the rules, the thresholds and the calls may
not. If the re-run shows Stage 1 at n = 8 below 0.5 power for the income layer at |H − D| = 0.4 even at the BH-half
threshold, the coordinator chooses n = 12 or fewer points before Stage 1, and says so on the ticket.

### 4.2 Refinement rules (mechanical; computed by a script from the Stage-1 calls alone)

**R-A (new points).** For each pair of Stage-1 points adjacent on the price axis (same c, L, s) or on the clutter axis
(same p, L, s) whose **body calls differ**, add the registered midpoint (price 0.018 or 0.053; clutter 0.5 or 1.5) at
the same other levels. Two calls differ when they are different members of {H-WIN, D-WIN, TIE}, or when one is a WIN
and the other is EXCLUDED of the winner. The body call is the share layer's; where the share layer is SATURATED at both
ends, the income layer's (§6.1). Pairs are ranked by |difference of the two points' share effects| (income effects for
income-layer pairs), smell G first, and the first 16 taken.

**R-B (more seeds).** Every Stage-1 or Stage-2a point whose body call is UNDECIDED gets seeds 9–16, ranked by the
conditional power of the combined test at its Stage-1 estimate, up to 20 points. Its final p-value is the inverse-normal
combination Z = (Z₁ + Z₂)/√2 of the two halves (seeds 1–8 and 9–16), fixed weights, which is valid under data-dependent
extension (Lehmacher & Wassmer 1999).

**No other point, seed or arm may be added** after Stage 1 is seen, except by a new registration.

## 5. Per point: arms, measurements, and why the ecology

### 5.1 The habitability census (Stage 0)

Per point: 3 seeds (129001–129003), arm S only, seasons 0–59. Per fauna:
- **founder solvency**: the share of founders whose mean season net (food − p · kJ) reaches the living cost over their
  12-season runway;
- **survival**: alive at season 59 (booked, and before same-season refill, H53);
- **the regime** in seasons 30–59 by RBT-126's readout: breeding-age net income ÷ living cost (saturation), net income
  per birth (viability), offspring by income quintile, deaths by age and by starvation, eligible breeders, median
  energy;
- **side effects (R10)**: income, births, depth, saturation and solvency, printed against `c1-p030-U-L`.

**R4 margins on real bodies** at 12 cells (L ∈ {U, HP, PW} × s ∈ {L, G} × c ∈ {0, 1}, at p = 0.03): RBT-125's world-gate
harness (a nose step against a +25% speed step on real hosts, and RBT-106's prize at a = 6). Food margins do not
depend on the price, so these 12 cells cover every price. They give the **PAYS** layer (§6.3).

**Census checks.**
- **C1** (monotonicity): along each price and clutter row, the census income difference (seeds pooled) changes sign at
  most once. Rows that break it are listed and **enter R-A's pair list** at Stage 2a.
- **C2** (habitability): a fauna is **EXCLUDED** at a point when it is extinct by season 59 on ≥ 2 of 3 census seeds.
  Stage 1 overrides the census wherever both exist.
- **C3** (rest on the densest terrain, R3): the motors-off displacement of 20 founders per fauna on c = 2. If more than
  2 of 20 drift over 0.25 m, c = 2 is flagged and its calls carry the flag.

### 5.2 The Stage 1–2 arms

Seeds are **common across points** (j = 1…16, seed 129000 + j): the same founders and terrain stream everywhere, so the
axis contrasts are paired by founder set. This makes the per-point tests positively dependent, which BH tolerates.

| arm | what | seasons | seeds |
|---|---|---|---|
| **S** side by side | the two faunas in their own ecologies (60 slots each), as every committed run | 0–299 | all |
| **M** merged | `--merge-after 60 --pooled-capacity 120`: identical to S up to season 59, then one arena, one pooled capacity | 0–299 | all |
| **N** matched drift null | `--merge-null K` (RBT-129a): at season 60, one fauna's ecology is replaced by an independent-stream copy of the other (K = holistic on odd seeds, designed on even), labelled B; then merged exactly as M | 0–299 | odd seeds holistic-null, even seeds designed-null |

**The merge at season 60.** The holistic founding bottleneck falls at season 11 and refills within one lifespan on
29 of 30 default histories (RBT-118 §2), so a merge before 60 would read the founding lottery, not the bodies. Sixty is
one max age. The income lead's onset (median 40, IQR 24–90) falls before or near it; the read window starts 180 seasons
after the merge.

**The read window: seasons 240–299** for every point outcome: three lifespans after the merge, and past the 90th
percentile of the prior lead onset.

### 5.3 Measurements

**(a) Side-by-side performance** (arm S). Per fauna, over seasons 240–299:
- **income flow**: mean over living members and seasons of the season net (food − p · kJ). This is a flow, not the
  season table's survivor-weighted `mean_lifetime_score` (RBT-118 §0), which is also printed for continuity;
- net income per birth; alive, births, deaths (starvation and age); extinction and its season;
- food, work (kJ), path, per season.

**(b) The head-to-head** (arms M and N).
- **Share**: the holistic fauna's share of the 120 pooled slots, mean over seasons 240–299; fixation (one fauna at 0)
  and its season.
- **Interference**: each fauna's income flow in the merged world minus its S-arm flow, and per-group composition with
  each member's food (RBT-118 §6.3). Printed, not called.
- **The null's role.** The null N gives, at the same point and demography: (i) the **centring check K2**: the
  relabelled share must centre on 0.5, which the merge's coupling (groupings and breeding order drawn from the holistic
  stream, `ecology.py` docstring) could break; (ii) **the drift SD** of the share at that point's turnover; (iii) the
  fixation-time distribution under no body difference.

**(c) Perception** (arm S; the merged world is secondary). At season 0 (founders) and season 300, 20 living members per
fauna per seed (all of them if fewer are alive; a fauna-seed with fewer than 5 is missing, not zero), drawn by a fixed
RNG (129300 + j), are probed solo in the point's world, on draws from that point's
admissible pool (RBT-116 r5's 64-draw pool and reachability screen):
- **intact − decoy food** on 8 draws per member: the rotated decoy (RBT-116 r5), lesion (sensors read 0), motors-off;
- **STEERS**: RBT-116's instrument as ruled (staged 4 + 16 + 16 draws, F_MIN = 0.25, the ΔT bound, the
  trajectory-identity veto, v_min from the member's own speed). The sweep adopts whatever version RBT-116's ruling
  fixes, and uses it unchanged at every point;
- **the planted set, per point** (not per seed): RBT-116's G8 plants, 4 hosts each: (a) the Pioneer compass plant at
  the first paying rung and (c) the tuned holistic two-nose plant (positives); (b) the paying kinesis plant, (d) the
  sensorless full-throttle tumblers (rod, hinge, ball) and (e) the same tumblers with two unwired food sensors
  (negatives); plus a motors-off body. The planted set's calls are what make a point's perception layer valid (§6.3).
  G8(b) is fed from a non-root nose, per the RBT-116 adversary's M5.

**(d) The regime**: RBT-126's readout on every S and M arm, per fauna and per 60-season window.

**(e) The R8 levers** on the same 20 probed members per fauna: Σgear/(4M) and the share capped; resting drive; the
share of work on contact-free children and the share at least half inside (`phys_ghost.py`); motors-off displacement
and food; span; reachable and recessive node counts. Under `--fair` most of these should be closed; they are measured,
not assumed.

### 5.4 The ecology, not `evolve`, at every point

**Decision: every point's map outcomes come from the ecology.** Reasons:
1. **The deliverable is what each world selects.** "Where perception pays enough to evolve" is a statement about the
   world's own selection. Imposed truncation selection sees gains the ecology cannot (R5: s ≈ 1.27 Δ/σ_P at 2 draws,
   against a lottery that is near-neutral above viability at g0 ≳ 0.8), so an `evolve` map would answer a different
   question: whether a body *can* get there under an experimenter's selection. RBT-113 already answers that in
   general (both bodies respond).
2. **A head-to-head needs a shared world**, and only the ecology has one (`merge_after`). `evolve` scores each body
   alone.
3. **The ecology's weakness is reported, not hidden.** Where a world pays perception (PAYS) but the ecology saturates
   and no fauna perceives, the map says exactly that (§6.3's cross-tab), and that cell is RBT-116's W2 (§9.2), where
   imposed selection asks the capacity question.

**The breeding rule** is RBT-126's to rule, and is one rule for every point.
- Under the committed lottery, a 1.25× forager is indistinguishable from neutral once resident gross income g0 ≳ 0.8,
  and fixes readily at g0 ≤ 0.5 (`adv_demography_invasion.txt`). So the share layer's resolving power depends on each
  point's regime, and the resolvability check (§6.2) carries that.
- Under energy order, the same mutant fixes at g0 = 1.3 in 200 of 200 replicates, at a depth cost (parents 137 → 71).
  `power.txt` §2 gives the share layer's power under both rules.

### 5.5 Controls (R10)

| id | control | passes when | if it fails |
|---|---|---|---|
| K1 | byte identity | S and M at one seed are identical to season 59 (`seasons.txt`, `lineage.jsonl`) | the point's M arms are VOID |
| K2 | null centring | pooled over a stage's points, the null's B-share differs from 0.5 by < 0.05 (t over seeds), and at no single point by > 0.15 | if pooled: the share layer is VOID for the stage; if per point: that point's share call is VOID |
| K3 | planted positives | RBT-116's G8(a), (c) pass rates at the point | the point's perception layer is VOID |
| K4 | planted negatives | G8(b), (d), (e) and motors-off: no STEERS; intact − decoy CI covers 0 | the point's perception layer is VOID |
| K5 | founders | the founders' intact − decoy (season 0) is the baseline; a PERCEIVES call needs the evolved population to exceed it | — |
| K6 | the rest check on c = 2 | census C3 | c = 2 calls carry the flag |
| K7 | side effects | printed per point against `c1-p030-U-L` (§5.1) | — |

### 5.6 Code this design needs: RBT-129a (to ticket, same discipline as the fairness set)

Off by default and byte-identical when off, with tests:
1. **`--merge-null KIND`**: at `merge_after`, replace the other fauna with a copy of KIND's population drawn by an
   independent stream (`--breed-stream`'s mechanism), labelled B, and merge.
2. **Merged logging** (RBT-118 §6.2–6.3): per season per fauna, share, deaths split by starvation and age, eligible
   breeders, median energy, and food, work and path means; per group, composition and each member's food.
3. **`--obstacle-radius`** (`world.random_radius` is config-only today), so the clutter density of §3.1 is a flag.
4. The world block export (`runs/RBT-129/worlds/<id>.json`), written from one table so that no point is typed by hand.

## 6. Per-point calls

All per-point tests take the **seed as the unit** (n = 8, or 16 after R-B), use a two-sided one-sample t test on the
seed-level statistic, and are corrected by BH at q = 0.10 within their family (§7.1). "BH-significant" below means
rejected by that procedure.

### 6.1 The body call (the map's main layer)

Statistics per seed j:
- **share**: y_j = the M arm's mean holistic share over seasons 240–299, minus 0.5;
- **income**: x_j = the S arm's holistic income flow minus the designed one, seasons 240–299 (a paired difference).

Margins: δ_s = 0.10 in share (12 of 120 slots); δ_i = 0.15 items a season in income (0.6 × the living cost, and
1.5 × the selection threshold of about 0.1 item a season that RBT-121 B names). An income TIE at ±0.10 is nearly
unreachable at the realised noise (`power.txt` §1), so the wider margin is registered; even at ±0.15 a TIE needs the
noise floor and n = 16.

The call, in order (the first that applies):
1. **EXCLUDED-H / EXCLUDED-D / NEITHER**: a fauna is extinct in its own S arm by season 299 on ≥ 5 of 8 seeds (≥ 10 of
   16). If one is, the point is a survival win for the other (a separate count in §7, not a share call).
2. **VOID**: K1 or K2 failed at the point.
3. **H-WIN**: the share test is BH-significant with mean y > 0 **and** mean y ≥ δ_s.
4. **D-WIN**: the mirror.
5. **CONTINGENT**: the seeds' share variance exceeds the null's at that point, F = var(y)/var(y_null) above its
   one-sided 0.99 point, and neither 3 nor 4 holds. History decides the winner at this world, seed by seed
   (`power.txt` §2: a per-seed spread of 0.1 item a season in the edge alone turns the share SD from 0.15 to 0.37).
6. **TIE**: TOST on y at ±δ_s succeeds (BH within the TIE family), **and** the point is RESOLVING (§6.2).
7. **SATURATED**: the point is not RESOLVING, and none of the above holds.
8. **UNDECIDED**: otherwise.

**The income layer** is called beside it, in this order: **EARNS-H / EARNS-D** (BH-significant, |mean x| ≥ 0.10),
**EARNS-TIE** (TOST at ±δ_i), UNDECIDED. The body call is the share call. The income call is its mechanism, and the
fallback for R-A where the share layer is SATURATED at both ends of a pair.

**LEVER.** R8 says a fauna difference that goes with a lever difference is attributed to the lever until shown
otherwise. A WIN or EARNS call is marked **LEVER** when the winning fauna's probed members exceed, on median, any of:
Σgear/(4M) at the cap on more than half of them; resting drive above 0.9; a contact-free work share above 0.25; a
motors-off displacement above 0.25 m. LEVER points are reported and excluded from the win counts of §7 (M1, M4).

### 6.2 Resolvability: when "no difference" may be called TIE

A point is **RESOLVING** when `power.py`'s `resolvable(g0, rule, n)`, fed that point's measured regime, the ruled
breeding rule and the point's n, gives power ≥ 0.80 to call a 1.25× income edge at q/2. The replica charges a fixed
0.1 of work a season, so the point's g0 is its mean season net income of the living (food − p · kJ; the M arm, seasons
180–299, both faunas pooled) plus 0.1. `power.txt` §5 tabulates the check by regime. Otherwise a no-difference result is **SATURATED**: the ecology
at that point cannot tell the bodies apart through births, whatever the bodies do. This prevents a lottery-saturated
world from being read as evidence that the bodies are equal (RBT-118 §2: "an income lead is not a fitness lead
here").

### 6.3 Perception, per fauna

Statistic per seed: f_j = the mean over the 20 probed members and 8 draws of (intact − decoy) food at season 300, minus
the same for the seed's founders at season 0 (K5).

- **VOID**: K3 or K4 failed at the point.
- **PERCEIVES**: f is BH-significant (family per fauna), mean f ≥ F_MIN = 0.25 (RBT-116's F_MIN), **and** the pooled
  count of confirmed STEERS members over the point's seeds (up to 160) exceeds the upper 95% binomial bound of the
  count expected from the point's own false-STEERS rate (its planted negatives and its founders pooled; RBT-116's EPS
  otherwise).
- **SMELL-USE**: f passes, STEERS does not. Smell changes what the body does, but the instrument cannot call it
  steering (klinokinesis is inside STEERS by RBT-116's definition; this is the remainder).
- **NONE**: otherwise.

**The world layer PAYS** (from the census's 12 cells, §5.1): RBT-125's gate criterion at that cell (the nose step's
margin is at least comparable to the speed step's, and the prize's lower bound at a = 6 is > 0). A point takes PAYS
from its (L, s, c) cell; c = 2 points take it from c = 1, and are so marked.

**The reading** of a point's perception is the cross-tab PAYS × RESOLVING × {PERCEIVES, SMELL-USE, NONE}:
- PAYS, and PERCEIVES: the world pays perception and the ecology found it;
- PAYS, SATURATED and NONE: the world pays, but this ecology does not select it (RBT-116 W2's cell, §9.2);
- not PAYS, and NONE: the expected result in a coverage world (R4);
- not PAYS, and PERCEIVES: a surprise, read against the planted set before anything else.

## 7. The map's summary statistics (pre-registered)

### 7.1 Families and multiplicity

| family | tests | procedure |
|---|---|---|
| share (WIN) | one per point: y ≠ 0 | BH, q = 0.10, over every Stage 1–2 point (K ≤ 52) |
| share (TIE) | one per point: TOST at ±δ_s | BH, q = 0.10 |
| income (EARNS), income (TIE) | one per point each | BH, q = 0.10 each |
| perception, holistic; perception, designed | one per point each | BH, q = 0.10 each |
| map-level tests T1–T4 | four | Holm, α = 0.05 |

- BH controls the directional false discovery rate for sign calls made on rejected points (Benjamini & Yekutieli
  2005), and holds under the positive dependence that common seeds induce.
- Stage-1 calls are **provisional**. The final map applies BH once, over all points, after Stage 2, with R-B's
  combined p-values.
- Points of the smell-L subset and the refinement points are in the same families.

### 7.2 The statistics

- **M1 (the call table).** Counts of each body call and each income call, per layout and smell, and overall; the
  survival-win count (EXCLUDED); the LEVER count.
- **M2 (the world model).** A weighted least-squares fit of the point-level share effect ȳ (weights 1/SE²) on
  c, log p, L, s and c × log p, over habitable, non-VOID points. The same fit for the income effect x̄. Coefficients with
  95% CIs are reported. Signs are predicted from the prior (§12).
- **M3 (break-even curves).** For each (c, L, s) row with at least two price levels, the price p*(c) at which the fitted
  income effect crosses 0 (a line in p per row, which is what the static arithmetic says it is), with Fieller 95%
  intervals. They are compared with RBT-118's 0.018 (c = 1) and 0.053 (c = 0), which are pre-fairness.
- **M4 (the area shares).** Over the 27 Stage-1 G points, equally weighted: the fractions H-WIN, D-WIN, TIE, CONTINGENT,
  SATURATED, UNDECIDED, EXCLUDED, VOID, LEVER. The same over the 9 L points, and with the Stage-2a points added, each
  refinement point taking the weight its bisection splits off its parent pair.
- **M5 (the perception map).** Per fauna, the count and positions of PERCEIVES; the cross-tab of §6.3; the
  perception gap f_H − f_D per point; and the smell contrast (G − L) at the 9 matched points.
- **M6 (concordance).** Cohen's κ between the share call's sign and the income call's sign over points where both are
  decided; the interference table (merged income − side-by-side income, per fauna).
- **M7 (monotonicity).** Along every price and clutter row of the final map, the number of sign changes of the income
  effect; rows with more than one are listed.

### 7.3 The map-level tests (Holm, α = 0.05)

- **T1 (dependence).** The world terms of M2's share model (c, log p, L, s, c × log p) jointly zero: a Wald test.
  If the share layer is SATURATED at more than half the points, T1 is run on the income model instead, and the verdict
  says so.
- **T2 (clutter).** M2's income coefficient on c is zero. Predicted > 0 (clutter favours the holistic fauna).
- **T3 (price).** M2's income coefficient on log p is zero. Predicted > 0 (dearer work favours the body that spends less).
- **T4 (smell).** Over the 9 matched (c = 1) points, the mean over points and both faunas of (f_G − f_L) is zero:
  one paired test over the 9 points, with each point's value the mean of the two faunas' differences. Predicted > 0.
  The per-fauna means are reported, not tested.

## 8. What would falsify "it depends on the world"

Verdicts on the framing, from the final map:

- **DEPENDS (confirmed)**: T1 rejects, **and** the share layer has at least one H-WIN and at least one D-WIN, not LEVER.
  If the share layer is SATURATED at more than half the points, the weaker **EARNINGS DEPEND** applies instead, with
  EARNS-H and EARNS-D in place of the WINs, and it is stated as a claim about income, not about which body persists.
- **ONE BODY DOMINATES (X)**: every decided share call (at least a third of the habitable, non-VOID points) is X-WIN
  or EXCLUDED-(other), **and** the income layer has no call for the other body at a point where both live. This
  falsifies the framing for the swept range: one body wins in every world tested.
- **WORLD-INVARIANT**: T1 does not reject, TIE (share, RESOLVING) or EARNS-TIE at at least half the points, and no WIN
  or EARNS call at all.
- **DEPENDS ONLY THROUGH HABITABILITY**: the only calls that differ across points are EXCLUDED ones. The bodies'
  ranking does not change where both can live; only where each can live does.
- **NOT RESOLVED**: none of the above.

For perception:
- **PERCEPTION EVOLVES SOMEWHERE (fauna F)**: at least one PERCEIVES call for F, not VOID.
- **NOWHERE IN THE SWEPT WORLDS**: no PERCEIVES call for either fauna, including the G points where the world gate
  passed. This falsifies "perception pays enough to evolve" for the swept range, and the PAYS × RESOLVING cross-tab
  says whether the world or the ecology is the reason.

A "depends" verdict is expected on prior grounds (§12; RBT-118 §4a). It is new only if it survives the fairness set,
and if the dependence is not the terrain reversal alone. M2's coefficients say which axes carry it.

## 9. How the sub-studies slot in

Sub-studies are **separate registrations** with their own designers, adversaries, rulings and families. The sweep
supplies their world blocks (§2), RBT-129a's null and logging, and a column in the final map. Their results are not
pooled into the sweep's families.

### 9.1 RBT-118 (the head-to-head rematch)

**Fixed points** (registered now):

| id | block | why |
|---|---|---|
| W118-a | `c1-p030-U-L` | the committed default world, under `--fair` |
| W118-b | `c0-p030-U-L` | RBT-118 §4a's reversal on flat ground |
| W118-c | `c1-p030-PW-G` | the perception world (shared with RBT-116's W1) |

**Rule-chosen points** (at most two, chosen by script after Stage 1): the habitable, non-LEVER Stage-1 point with the
largest BH-significant |ȳ| for each sign, if one exists. RBT-118's design then replicates it with fresh seeds (seed
base 118000), and adds what the sweep does not: n = 20, horizons to 1,200 seasons, a founding contest (`merge_after 0`),
and a `breed_order` arm (RBT-118 §6.7–6.8).

### 9.2 RBT-116 (the extradimensional bypass)

- **W1** = `c1-p030-PW-G`: r5's W1 already is this block (PW, G = 2.5, random terrain, 0.03/kJ, `eat-from root`,
  15 s). The sweep adopts r5's settings where they overlap (`--random-start` is an `evolve` setting and has no ecology
  counterpart; it is the one field outside the block).
- **W2** (chosen by script after Stage 1): among the Stage-1 points with L ∈ {HP, PW} and s = G, those with PAYS,
  SATURATED and NONE for both faunas (§6.3's "pays but the ecology does not select it"); of those, the one with the
  largest census nose-step margin. If there is none, W2 = `c0-p030-PW-G`: the Pioneer's best terrain, which separates a
  terrain effect on the valley from a perception effect. The coordinator may override; W2 must pass RBT-116's own
  gates (G1, G2, G6–G9) before any of its arms.
- RBT-116 costs about 420 core-h a point at D = 16 (PR #400 r5 §5), more than ten Stage-1 points. Two points is the
  ceiling this design assumes.

## 10. Power (`power.txt`; bounded, R11)

**Noise floors and ceilings.**

| quantity | floor | ceiling | source |
|---|---|---|---|
| per-seed SD of the income difference | 0.144 (random terrain, n 29) | 0.334 (flat, n 29) | RBT-118 `pool.txt`, `probe_terrain.txt` |
| per-seed SD of the share, no edge | 0.149 (replica, lottery, g0 0.5) | 0.367 (with a per-seed edge SD of 0.1) | `power.txt` §2 |
| member × draw SD of food | 0.945 (designed) | 1.469 (holistic) | `noise_components.txt` |
| cost per arm-season | 20 core-s (RBT-105 measured) | 25 core-s | §11 |

**Effect floors and ceilings.**
- Income: the floor is 0 (at a break-even, by definition). The ceiling at the coarse corners is about 1.5 items a
  season on the pre-fairness arithmetic (`power.txt` §1's prior map). The design's resolving power is therefore stated
  as the **width of the UNDECIDED band around a boundary**, not as power at one effect.
- Share: the floor is the null; the ceiling is fixation. The replica gives both, by regime and rule (`power.txt` §2).
- Perception: the floor is 0 (the committed worlds: RBT-113 holistic −0.080, designed +0.021); the ceiling is a
  finished nose in PW at G = 2.5, +1.77 items. That ceiling is a kinematic number (C's model); per the RBT-116
  adversary's M5 it bounds, and is not cited as a real-body effect.

**What the design resolves** (BH at q = 0.10; "worst" is the one-rejection threshold q/K, "half" is q/2):

| layer | n = 8 | n = 16 (after R-B) |
|---|---|---|
| income MDE80, noise floor | 0.29 (worst, K = 36) / 0.17 (half) | 0.16 / 0.11 |
| income MDE80, noise ceiling | 0.66 / 0.38 | 0.37 / 0.25 |
| the UNDECIDED price band around a break-even (half-width, noise floor, BH half) | 0.011–0.028 $/kJ | 0.007–0.018 $/kJ |
| income TIE at a true 0 (±0.15) | see `power.txt` §1 | |
| share: see §10.1 | | |
| perception: P(PERCEIVES \| f = 0.25), holistic, M 20, D 8 | 0.20–0.67 (worst) / 0.75–0.99 (half) | |
| perception: P(PERCEIVES \| f = 0.40), holistic | 0.64–0.99 (worst) | |

The price band is the MDE divided by the price slope of the income difference, kJ_D − kJ_H, bounded between 6 and
15.5 kJ a season (14.7 before the fairness set; the fairness set is expected to cut both bills).

### 10.1 The share layer by regime

SHARE_TABLE_PLACEHOLDER

## 11. Budget, staging and order

### 11.1 Gates and order

1. **Gates (all required before Stage P):** RBT-120 (motor budget) and RBT-124 (physics pack) merged; RBT-128
   (`--fair` and the guard) merged; RBT-125 (smell channel with G registered, eating rules, **world gate passed on real
   bodies**) merged; RBT-126's readout script committed and its breeding rule ruled; RBT-129a merged; RBT-116's
   `steer.py` committed at its ruled version. RBT-127 (versions in `config.json`) is expected, not gating.
2. **Stage P** (pilot) and **Stage 0** (census) in parallel. Then `power.py` is re-run with the pilot's constants (§4.1),
   and the coordinator rules n for Stage 1.
3. **Stage 1.** Its provisional map is posted; R-A and R-B are computed by script and posted before any Stage-2 arm.
4. **Stage 2a and 2b** in parallel. Then the final map, BH over all points, the verdicts of §8.
5. **Stage 3.** RBT-118's fixed points and RBT-116's W1 may run any time after the gates (their worlds are fixed);
   their rule-chosen points wait for Stage 1.

### 11.2 CPU-hours (`power.txt` §4)

Per seed and point: S 1.67 + M 1.67 + N 0.71 (half the seeds) + probes and levers 0.40 = **4.4 core-h** at 20 core-s
per arm-season (5.5 at 25). The planted set adds about 0.25 core-h per point.

| stage | at 20 core-s | at 25 core-s |
|---|---|---|
| P pilot (3 points × 4 seeds) | 54 | 66 |
| 0 census (150 × 3 seeds × 60 seasons, plus 12 R4 cells) | 174 | 212 |
| 1 coarse map (36 points × 8 seeds) | 1,288 | 1,579 |
| 2a refinement (≤ 16 points × 8) | ≤ 573 | ≤ 702 |
| 2b extension (≤ 20 points × 8 more) | ≤ 711 | ≤ 872 |
| **total, at most** | **2,799** | **3,431** |

- Wall time on ten 4-core sessions (40 cores; the programme's usual ceiling of ≤ 10 at a time), packed two arms of
  *different seeds* per session at WORKERS = 2 (RBT-107's packing rule): 70–86 h at most (the census and pilot about 6 h of it).
- **Sub-studies, not included:** RBT-116 about 420 core-h a point (840 for two); RBT-118 per its own design
  (about 300 a point at n = 20 and 1,200 seasons, so about 900–1,500 for three to five points).
- **A lean option** for the ruling: Stage 1 at n = 6 and R-B to n = 12 costs 2,160–2,646 core-h (23% less), and widens the income
  band by 24–40% (`power.txt` §1: MDE80 0.205 against 0.165 at the BH-half threshold, 0.400 against 0.286 at the worst).
- **A full factorial** at n = 8 would cost 5,368 core-h at 20 core-s (6,580 at 25), before any
  extension.

## 12. Registered predictions (from the priors; "no" is a finding)

1. **Income layer.** On the pre-fairness arithmetic (`power.txt` §1), EARNS-D on flat ground at p ≤ 0.03, EARNS-H at
   c ≥ 1 for p ≥ 0.03, with the break-even rising as clutter falls. **Under the fairness set** the designed body's
   resting throttle is closed (`effector_bias_sigma`; its D line was 99% saturated), so its work bill is expected to
   fall more than the holistic one, and **the break-evens to rise**: M3's p* above 0.018 at c = 1 and above 0.053 at
   c = 0. T2 > 0 and T3 > 0.
2. **Share layer.** Under the committed lottery, SATURATED at most points above the lowest-income worlds (the
   committed economy sits near g0 ≈ 1.3); resolving mainly at p = 0.08, in PW and at c = 2, where incomes fall. Under
   energy order, share calls follow the income calls' signs (M6's κ > 0.5).
3. **Habitability.** EXCLUDED-D at some p = 0.08 points on c ≥ 1 (RBT-99's 3 of 10, before the fairness set, from a
   changed world rather than from founding).
4. **Perception.** NONE at every U point and at every L point (R4). PERCEIVES, if anywhere, at PW-G and HP-G points,
   and first for the designed fauna, whose two noses are fixed at a useful spacing. PERCEIVES-H at no point is a live
   outcome, and it is not evidence against holistic bodies unless the point is RESOLVING and PAYS.
5. **The framing.** DEPENDS, carried by clutter and price (as RBT-118 §4a found), with the layout acting mainly
   through habitability and perception.

## 13. Open items for the design adversary

1. **CONTINGENT's threshold** (F at the null's 0.99 point) was chosen, not derived. Should it enter BH?
2. **The LEVER thresholds** (§6.1) are round numbers. Are they tight enough under `--fair`, where the levers should be
   closed?
3. **Common seeds across points** trade independence for pairing. Is BH's positive-dependence condition met, given
   that the same founders appear at every point?
4. **The legacy-smell subset** is 9 points at c = 1. Is that enough to call T4, or should it be crossed with c = 0?
5. **The null on half the seeds**, alternating kinds, assumes the share drift SD depends little on which fauna is
   copied. The pilot measures it.
6. **R-A's midpoint levels** are fixed. A boundary between 0.01 and 0.018 is then located only to that bracket.
7. **The resolvability check** uses a replica, not the simulator. The pilot's null measures the real drift SD; if it is
   more than 1.5× the replica's, the check's power figure is scaled by the ratio.
8. **PAYS on c = 2** is borrowed from c = 1.

## 14. Files

| file | what |
|---|---|
| `DESIGN.md` | this document |
| `power.py` → `power.txt` | income MDE and bands; share replica by regime and rule; perception power; budget |

Reproduce: `python3 runs/RBT-129/power.py > runs/RBT-129/power.txt` (numpy only; about 15 minutes).
