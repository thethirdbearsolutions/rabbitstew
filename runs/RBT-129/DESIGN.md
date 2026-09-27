# RBT-129: the world sweep (DRAFT pre-registration, r3)

> **Status: DESIGN ONLY. Nothing has run and nothing runs from this file.** It is the Phase-2 main programme's
> design (epic RBT-123; plan *Phase 2 plan: the world sweep*, ratified 2026-09-27 at about 21:30 UTC). A design
> adversary follows, then a coordinator ruling. **No arm launches until the gates of §11.1 are met:** the fairness
> set (RBT-120, 124, 125, 128) merged, the RBT-125 world gate passed on real bodies, RBT-126's readout and breeding
> ruling in hand, and this design's own small code ticket (RBT-129a, §5.6) merged.
>
> `power.py` → `power.txt` in this directory holds every power and budget number quoted below. It runs no
> simulator.
>
> **r2** answers the design adversary (PR #416, `runs/RBT-129/design-adversary/ADVERSARY.md` at `3407f98`, REGISTER
> AFTER FIXES) under the coordinator's 22:25 ruling and its 22:42 addendum: all 12 MUST and all 12 SHOULD items are
> taken. §0.1 maps each item to where it is answered. **The breeding rule is not settled:** RBT-126's `--energy-leak
> 0.3` was withdrawn at its adversary's ruling (it fixes a same-mean, higher-variance mutant, so it reads income noise
> as merit). RBT-126 (merged, `d1eb1ae`) then screened 11 rules against planted variance negatives, and **none
> passes**. So, as a design decision (coordinator, 22:56), **the sweep registers the committed shuffle as its primary
> rule**, and every share and spread call reads "under the committed rule" (§5.4). `power.py` stays **parameterised by
> the rule** (lottery = shuffle, energy, leakx:0.3), so a later rule can be substituted by amendment.
>
> **r3** answers the adversary's R2-CHECK (#416 at `d3f5209`, REGISTER AFTER FIXES) under the coordinator's 23:15
> ruling: R2-M1 to R2-M3, S-1 to S-6 and R2-S1, all as written (§0.2). **Under the committed rule the sweep answers
> "which body *earns* more, where", not "which body *persists*"** (§1, §8).

## 0. The design in one table

| question | decision | § |
|---|---|---|
| what is swept | clutter density × work price × food layout × smell channel, 5 × 5 × 3 × 2 = 150 candidate points | 3 |
| full factorial? | **no, except for the cheap census.** A full-factorial **habitability census** (150 points, 3 seeds, 60 seasons), then an **adaptive coarse-to-fine map**: 36 coarse points at n = 8, then at most 16 refinement points chosen by a mechanical rule, and at most 20 points extended to n = 16 | 4 |
| selection | **the ecology at every point**, with the regime stated (R5). `evolve` (imposed selection) appears only inside RBT-116, at its registered points | 5.4 |
| breeding rule | **the committed shuffle, as the primary rule** (none of RBT-126's 11 screened rules passes the variance negatives); `lcb:3` as a secondary, descriptive rule at the 3 anchors only, never in a verdict | 5.4 |
| arms per point and seed | S (side by side, 300 seasons) everywhere; M (merged at season 60, forked from S's season-59 checkpoint; the one-world income column) at points with census g0 ≤ 1.0; N (matched drift null, forked the same way, on half the seeds) only at census g0 ≤ 0.8; the 3 anchors' M and N taken from RBT-118; retention arms R_sel and R_marker at PAYS points ranked by census g0 | 5 |
| per-point outcomes | habitability; income (side by side); fauna share (merged, against the null); perception (intact − decoy, STEERS, planted negatives); regime; R8 levers | 5, 6 |
| per-point calls | body: EXCLUDED / PARTIAL / VOID / H-WIN / D-WIN / CONTINGENT / TIE / SATURATED / UNDECIDED, on the change in share since the merge (y′); income: EARNS-H / EARNS-D / EARNS-TIE; perception, per fauna: PERCEIVES / SMELL-USE / NONE / VOID | 6 |
| multiplicity | Benjamini–Hochberg at q = 0.10 within each family of per-point calls (BY beside it if the cross-point seed correlation is high); Holm at α = 0.05 over four registered map-level tests, fitted on the Stage-1 grid | 7 |
| sub-studies | RBT-118 at three fixed points and up to two rule-chosen ones; RBT-116 at W1 (its own) and one rule-chosen W2 | 9 |
| power | bounded by floors and ceilings with RBT-118's and RBT-121's realised noise (§10) | 10 |
| budget | at most 2,186–2,860 core-h for the sweep itself (55–72 h of wall on ten 4-core sessions), plus optional R_drift and `lcb:3` arms, sub-studies extra | 11 |
| what falsifies "it depends on the world" | ONE BODY DOMINATES or EARNINGS DOMINATED (one body wins every decided point, with no opposite call in either layer), or WORLD-INVARIANT (no world term, no opposite-sign pair), in a registered precedence order (§8) | 8 |

### 0.2 r3: where each R2-CHECK item is answered

| item | the fix | § |
|---|---|---|
| R2-M1 retention | **R_marker** (same economy, founders and motif at a = 6, the motif's food sensors lesioned) is the floor and the planted negative, h = carriage(R_sel) − carriage(R_marker); R_drift descriptive only, if `--breed-gate none` has merged; the carriage readout validated on planted, random and ablated genomes, with its false-carriage rate printed; the per-fauna erosion and births table, and a matched-erosion re-read at one point; the confirmation leg at K3's bars, with R_marker members reading NONE; "not bounded by the saturated band" deleted everywhere and replaced by the regime × trait-value power table; retention points ranked by census g0 | 6.4, 5.2, 8, 11.2, 12 |
| R2-M2 g0 | g0 (the census regime) enters the **share** model only; the income model's terms are c, log p, L, s and c × log p | 7.2 |
| R2-M3 opposite-sign sets | ≥ 2 calls, or 1 corroborated by an M3 break-even whose Fieller interval lies inside [0.01, 0.08]; the same rule, symmetrically, for "no call for the other fauna" | 8 |
| R2-S1 share layer demoted | M only at census g0 ≤ 1.0, as the one-world income column and interference table; N only at census g0 ≤ 0.8; the anchors' share from RBT-118 (coordinated seeds); DEPENDS and ONE BODY DOMINATES moved below their income counterparts, marked not expected to be reachable; §1 and §8 say plainly "earns, not persists"; the savings spent on R2-M1 | 1, 5.2, 5.4, 8, 9.1, 11.2 |
| S-1 | `resolvable()` runs at both 90% bounds and prints both (`power_r3.txt` §5′) | 6.2 |
| S-2 | CONTINGENT's pooled null at the gated df, homogeneity stated, not callable below df 12 (`power_r3.txt` §6b′) | 6.1 |
| S-3 | net income per birth beside the flow at every point; EARNS calls marked MARGINAL where a fauna's per-birth income is below the living cost | 5.3, 6.1 |
| S-4 | VARIANCE-DRIVEN by a two-predictor seed-level fit (the SD term's partial t beats the mean term's, and the mean term's is below 2) | 6.1 |
| S-5 | N at census g0 ≤ 0.8; the 1.0 threshold kept for M only | 5.2 |
| S-6 | the anchors' arms from RBT-118, with coordinated seeds; the sweep's own anchor arms only if RBT-118 does not adopt it | 9.1, 11.1 |

### 0.1 r2: where each adversary item is answered

| item | the fix | § |
|---|---|---|
| M1 merge-time composition | the share statistic is y′ = share(240–299) − share at the merge; both counts at the merge printed per seed; K2 on y′; `power.py` §2, §5 re-run on y′ | 6.1, 5.5, 10.1 |
| M2 pre-merge extinction | share and income tests use only seeds with both faunas alive at the merge (share) or through season 239 (income); fewer than 6 of 8 (12 of 16) valid seeds gives PARTIAL-X, a survival call, never a WIN | 6.1 |
| M3 RESOLVING and the TIE margin | RESOLVING requires P(share TIE \| income edge δ_i) ≤ 0.05 and P(WIN \| δ_i) ≥ 0.80 at q/2, under the registered rule (shuffle) with the planted variance negatives silent, at both 90% bounds of g0, with 1,500 replica seeds | 6.2, 10.1 |
| M4 CONTINGENT | pooled per-kind null variance (df ≈ 108 at Stage 1, kind offset removed); UNDECIDED ∪ CONTINGENT eligible for R-B; CONTINGENT in its own BH family | 6.1, 4.2, 7.1 |
| M5 R-A | a pair is refined when its point estimates differ in sign or its decided calls differ; ranked by \|t₁ − t₂\|; the layer named per pair; C1 pairs named | 4.2 |
| M6 LEVER | defined on the between-fauna difference, for levers R1–R3 do not budget; "cap binding" replaces "at the cap"; both faunas printed | 6.1 |
| M7 perception controls | K3 plants at the fixed rung a = 6 and passes on the behavioural legs; ≥ 8 hosts a plant with registered bars; G8(b) marked untested where kinesis cannot pay; NOWHERE needs a valid layer at ≥ 2/3 of PAYS points | 5.3, 5.5, 8 |
| M8 `--merge-null` | B is a separate label with its own mate pool, stream and lineage names; the tests; the arena-bank transient | 5.6 |
| M9 T4 | a seed-level paired test of f_G − f_L in PW; HP a second stated contrast | 7.3, 10 |
| M10 M2's weights | M2 is fitted at the seed level on logit(clipped share) change, with a point random effect; no 1/SE² weights | 7.2 |
| M11 verdicts | a precedence order; DEPENDS ONLY THROUGH HABITABILITY over decided calls; EARNINGS DOMINATED added; WORLD-INVARIANT reachable | 8 |
| M12 2a/2b order | R-B on Stage-1 points runs beside 2a; R-B on 2a points follows 2a, inside the cap of 20, Stage-1 points ranked first | 4.2, 11.1 |
| S1 | the census's extinction is FOUNDING-FAIL; the census regime is the only habitability proxy at unrun points | 5.1 |
| S2 | c 0 → 0.5 is a change of kind; C1 routes a non-monotone segment to R-A | 3.1 |
| S3 | RBT-129a prints realised free-ground density and sets N from free area; per-point K2 is a BH test with the size bar | 3.1, 5.5, 5.6 |
| S4 | unreachable items and food per new cell per clutter level | 5.3 |
| S5 | M-arm income per fauna as a second income column | 5.3, 7.2 |
| S6 | T2/T3 on the Stage-1 grid; refinement and extension in a sensitivity fit | 7.2, 7.3 |
| S7 | g0 as a covariate in M2; the founders are the operative negative; the false-STEERS rate from founders only | 5.5, 6.3, 7.2 |
| S8 | T1 on income primary, share secondary; PAYS per fauna under the sweep's block | 5.1, 7.3 |
| S9 | the cross-point seed correlation printed, BY beside BH if its mean > 0.3; the level-channel sentences and the `food_level` trigger | 3.4, 7.1 |
| S10 | N on all pilot seeds; scale by the estimate | 4.1 |
| S11 | "fewer points" names the 9 L points first | 4.1 |
| S12 | probes and plants re-costed; `c2-p030-PW-G` in the pilot; M and N forked at 59 | 11.2 |
| coordinator note 1 | RESOLVING and `power.py` parameterised by the rule (lottery, energy, leakx:λ); all printed | 6.2, 10.1 |
| coordinator note 2 | gates add this adversary's MUSTs ruled and re-checked, and RBT-126 merged (its screen found no rule, so shuffle is registered; its drift-gate fix is a gate for §6.4) | 11.1 |
| addendum 22:42 (a) | planted **variance negatives** in the RESOLVING and TIE checks, beside the neutral marker, under each rule: a same-mean variance-only mutant and a 0.9× mean-loss, variance-gain mutant; energy order's TIE safety re-checked against them | 6.2, 10.1 (`power.txt` §7) |
| RBT-125 ruling C6 (22:47) | G-point perception negatives are worded "contrast-only perception does not pay / evolve", NOWHERE inherits the qualifier; the level channel is listed as unswept; τ = 2 s | 2, 3.4, 3.5, 6.3, 8 |
| coordinator 22:56 | shuffle registered as primary; the RESOLVING count under shuffle priced (§6.2: 0–2 of 36 Stage-1 points); `lcb:3` descriptive at the anchors with its feast-or-famine failure printed; a **retention layer** (§6.4); `power.py` kept parameterised | 5.2, 5.4, 6.2, 6.4, 11.2 |
| addendum 22:42 (b) | SATURATED concerns the share and spread layer only; it never reads as "selection cannot act" | 6.1, 6.2, 6.3, 12 |

## 1. What binds this design

**The question.** RBT-123 asks for *a map of where each body plan wins, and where perception pays enough to evolve,
with the allowances closed*. It answers the 2005 proposal (`docs/origins/`) as "it depends on the world, and here is
how", rather than as one verdict that hinges on one setting. Reason (a) of the proposal, that body-specific strategies
exploit their own quirks, **predicts** such a dependence; this design is written so that the dependence can fail to
appear (§8).

**What it can answer under the committed breeding rule (r3, R2-S1).** The sweep registers the committed shuffle
(§5.4), because no rule screened by RBT-126 passes its variance negatives. Under shuffle, births barely spread an
income edge in the committed economy's regime. So the sweep answers **"which body *earns* more, where"** (the income
layer), **where each body can live** (the survival layer), and **where perception evolves or is held** (the perception
and retention layers). It does **not** answer **"which body *persists*"** in a shared world: that head-to-head share
question waits on a breeding rule that passes RBT-126's screen. The share layer is kept as a small, descriptive
one-world column (§5.2).

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
| R4 the world pays perception on the path | the smell channel is an axis, not an assumption. The world gate (RBT-125) must pass before the sweep launches, and the census measures PAYS **per fauna, under the sweep's own block**, on real bodies at 18 cells (§5.1) |
| R5 selection that can see the gain, regime stated | the ecology at every point; RBT-126's regime readout on every arm; a **resolvability check tied to the income TIE margin, under the ruled breeding rule,** decides whether a no-difference share result can be called TIE or only SATURATED (§6.2) |
| R6 operator parity | the default operators for both faunas at every point, stated. If RBT-124/128 rule `--structural-rate-scale` into `--fair`, it applies everywhere |
| R7 behaviour by instrument, with planted negatives | perception is called only by intact − decoy plus RBT-116's STEERS instrument, with its planted positives and negatives re-run **at every point** (§5.3) |
| R8 body levers | the per-line lever report (RBT-120's `motors.py`, extended by RBT-124) on the probed members of both faunas in every arm; a call that goes with a between-fauna lever **difference** is marked LEVER, not WIN (§6.1) |
| R10 controls able to fail, side effects | the drift null N (on the change statistic y′), the planted set at a fixed rung, **the arm's own founders as the operative negative**, the per-point null-centring test K2, the census's side-effect table against the committed world (§5.5) |
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
| smell transform when on | RBT-125's ruled channel, reading tanh(G · (ln S − b)) with b a per-robot running baseline (τ = 2 s, RBT-125's ruled value, with its 1e-12 floor inside the log), at the **registered G** (candidate 2.5). It **replaces** every food sensor's absolute level with contrast; RBT-125's level channel is deferred | RBT-125 (ruling C6), RBT-116 r5 §4.2 |
| breeding rule | **the committed shuffle** (`ecology.py:524-529`), the same at every point (§5.4) | R5; RBT-126 screen; coordinator 22:56 |
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
number is N = round(14 · c · ((R_food − 0.4)/2.6)²), so the nominal density is the same in every layout. **The realised
density is not** (adversary S3): `world.random_terrain` keeps obstacles 0.6 m + footprint/2 from each of the 4 spawns,
with at most 50 × N tries, which excludes about 26% of the 3 m layouts' disc and 14% of PW's. RBT-129a therefore sets N
from the **free** area (the disc less the keep-clear discs), prints the realised count and free-ground density per level
and layout over 100 terrain seeds, and flags any level where the 50N-try cap binds. The table below is nominal until
then. Heights and footprints
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

- **c = 0 → 0.5 is a change of kind** (no obstacles, then some), not only of density, so the monotone-bisection premise
  is weakest on that segment. A non-monotone c = 0 → 0.5 → 1 row is expected possible; census check C1 routes it to R-A.
- **Clutter also taxes food.** Items are placed without regard to obstacles, so some sit inside a footprint, and in PW
  a persistent item can stay under a new terrain for a season. That is part of the world, but it changes what T2 reads.
  The share of items unreachable per clutter level, and each fauna's food per new cell covered, are printed (§5.3).

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

**What the channel is, and what that limits** (adversary S9). RBT-125's channel reads change, not level (a running
baseline, τ = 2 s). So:
- **The smell axis is a swap, not an addition.** At `L` a nose reads the level; at `G` it reads the contrast, and the
  level is gone. T4's G − L is "contrast instead of level". A body using the level for area-restricted search can lose
  at G; a negative G − L at HP is read that way.
- **Every lone nose becomes a temporal-gradient detector at G**, so klinokinesis is cheap for any holistic body with one
  wired food sensor, and STEERS counts it. PERCEIVES is therefore reported **by route** (one nose against two, from the
  wiring readout), as RBT-116 §6.4 does.
- **At rest in a static field the channel reads 0.** Registered sentence: *the sweep cannot detect level-based
  strategies at G points.*
- **Registered wording (RBT-125 ruling C6).** At every smell-G point, a perception negative (NONE, or not PAYS) is
  written **"contrast-only perception does not pay"** or **"contrast-only perception does not evolve"**, never
  "perception does not pay" or "does not evolve". At L points the wording is "level-only perception (legacy smell)
  …", for the same reason.
- **Trigger for a level channel:** if SMELL-USE or PERCEIVES at L points vanishes at the matched G points on ≥ 2 of the
  3 layouts, the `food_level` ticket (RBT-125's flagged source) is opened.

### 3.5 What is not swept, and why

- **The breeding rule** is not an axis. It changes the economy's selection above viability, which would double the
  grid. It is fixed at the committed shuffle (§5.4), and the regime is reported instead.
- **Group size, capacity, item count, the living cost:** held at the committed values (RBT-118 §3 has one magnitude of
  each; sweeping them is a later registration).
- **The founding contest** (merging at season 0) is RBT-118's, at its points (§9.1).
- **The smell level channel** (RBT-125's deferred `food_level` source, a level beside the contrast). At every G point
  the food sensors read contrast only, so **a level channel is an unswept axis**: the sweep says nothing about
  perception that reads level, and every G-point perception negative is worded accordingly (§6.3, §8). §3.4 names the
  trigger that would open it.

## 4. Why coarse-to-fine, and the stages

**A full factorial** of the 150 candidate points at n = 8 would cost 4,952–6,466 core-h (§11), and most of it would
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
| **P** pilot | 4: `c1-p030-U-L` (the committed world under `--fair`), `c0-p030-U-L`, `c1-p030-PW-G`, `c2-p030-PW-G` (the densest terrain: bounds the cost per arm-season from above, and gives C3 a real-body run) | 4, with N on **all** 4 | 300 | measure cost per arm-season under `--fair`, the null's y′ SD per kind, the per-seed SDs; dry-run the logging, the instrument and the planted set | **none** (exploratory) |
| **0** census | the full 5 × 5 × 3 × 2 = 150 | 3 | 60, S only | founding (FOUNDING-FAIL), founder solvency, the regime early; PAYS per fauna at 18 cells | the census layer only |
| **1** coarse map | 27 at G: c ∈ {0, 1, 2} × p ∈ {0.01, 0.03, 0.08} × L ∈ {U, HP, PW}; 9 at L: c = 1 × the same p × L | 8 | 300 | the map | all layers |
| **2a** refinement | ≤ 16 new points by rule R-A | 8 | 300 | locate boundaries | all layers |
| **2b** extension | ≤ 20 UNDECIDED or CONTINGENT points by rule R-B | +8 (n = 16) | 300 | resolve near-boundary points | all layers |
| **3** sub-studies | RBT-118 and RBT-116 at registered points | their own | their own | their own questions | their own |

**What the pilot may change.** After Stage P, `power.py` is re-run with the pilot's measured per-seed SDs, null y′ SD
(12 null runs, df 11) and cost per arm-season. The replica's drift SD is **scaled by the pilot's point estimate** of
the ratio real/replica, not by a 1.5× trigger (adversary S10: six runs cannot see 1.5×). Only those constants may
change. The grid, the rules, the thresholds and the calls may not. If the re-run shows Stage 1 at n = 8 below 0.5
power for the income layer at |H − D| = 0.4 even at the BH-half threshold, the coordinator chooses between n = 12 and
**fewer points, dropped in this registered order: the 9 L points first, then the c = 2 row of U** (S11), before
Stage 1, and says so on the ticket.

### 4.2 Refinement rules (mechanical; computed by a script from the Stage-1 calls alone)

**R-A (new points; adversary M5).** For each pair of Stage-1 points adjacent on the price axis (same c, L, s) or on
the clutter axis (same p, L, s), add the registered midpoint (price 0.018 or 0.053; clutter 0.5 or 1.5) at the same
other levels when **either**
- the two points' **estimates differ in sign** (UNDECIDED points count: a boundary sits where the calls are undecided),
  or
- their decided calls differ: different members of {H-WIN, D-WIN, TIE}, or a WIN beside EXCLUDED or PARTIAL of the
  winner.

**The layer, per pair:** the share layer (ȳ′) where both points are RESOLVING; otherwise the income layer (x̄). The
layer used is printed with each pair.

**Ranking:** by |t₁ − t₂|, the difference of the two points' t statistics on the pair's layer (unit-free), smell G
first; the first 16 are taken. **C1's non-monotone rows** (census) add the pair flanking each extra sign change, ranked
in the same list.

The adversary's probe on the prior map (`probe_ra.txt`) finds this rule refines a truly bracketed boundary with
probability 0.64–1.00, against 0.06–0.63 for r1's rule.

**R-B (more seeds).** Every point whose body call is UNDECIDED **or CONTINGENT** (M4b) gets seeds 9–16, ranked by the
conditional power of the combined test at its first-stage estimate, up to 20 points. **Order (M12):** Stage-1 points
are extended beside Stage 2a (their R-B list is computed and posted with R-A's); Stage-2a points are extended after 2a,
from what remains of the cap of 20, with Stage-1 points ranked first. Its final p-value is the inverse-normal
combination Z = (Z₁ + Z₂)/√2 of the two halves (seeds 1–8 and 9–16), fixed weights, which is valid under data-dependent
extension (Lehmacher & Wassmer 1999).

**No other point, seed or arm may be added** after Stage 1 is seen, except by a new registration.

## 5. Per point: arms, measurements, and why the ecology

### 5.1 The census (Stage 0)

Per point: 3 seeds (129001–129003), arm S only, seasons 0–59. Per fauna:
- **founder solvency**: the share of founders whose mean season net (food − p · kJ) reaches the living cost over their
  12-season runway;
- **founding**: alive at season 59 (booked, and before same-season refill, H53). **This sees the founding runway, not
  viability** (adversary S1, `probe_census.txt`: a fauna at income 0.30 is extinct by season 299 on 100% of seeds, but
  by season 59 on 1%; every committed post-onset extinction came 67–146 seasons after the change of world). So the
  census's extinction is called **FOUNDING-FAIL**, never EXCLUDED;
- **the regime** in seasons 30–59 by RBT-126's readout: breeding-age net income ÷ living cost (saturation), net income
  per birth (viability), offspring by income quintile, deaths by age and by starvation, eligible breeders, median
  energy;
- **side effects (R10)**: income, births, depth, saturation and solvency, printed against `c1-p030-U-L`.

**PAYS, per fauna, on real bodies** at 18 cells (L ∈ {U, HP, PW} × s ∈ {L, G} × c ∈ {0, 1, 2}, at p = 0.03), **under
the sweep's own block** (`--fair` and the ruled eating rule, not the committed rule RBT-125's harness used; adversary
S8):
- **designed PAYS:** RBT-125's world-gate harness: a nose step against a +25% speed step on real designed hosts, and
  RBT-106's prize at a = 6;
- **holistic PAYS:** RBT-116's G8(c) tuned two-nose plant at a = 6 on 8 holistic hosts: its F (intact − decoy food)
  with a lower bound > 0, and its nose step against a speed step as above.

Food margins do not depend on the price, so these 18 cells cover every price. They give the **PAYS** layer (§6.3),
per fauna. c = 2 is measured, not borrowed (open item 8).

**Census checks.**
- **C1** (monotonicity): along each price and clutter row, the census income difference (seeds pooled) changes sign at
  most once. Rows that break it are listed and **enter R-A's pair list** at Stage 2a.
- **C2** (founding): a fauna is **FOUNDING-FAIL** at a point when it is extinct by season 59 on ≥ 2 of 3 census seeds.
  This is a provisional, flagged layer (at a per-seed rate of 0.5 it is a coin toss). Its only uses are: the
  living-cost fallback (§2); C1's rows; and, at the 114 points never run at Stage 1, the map's census layer, where
  **the census regime (net income ÷ living cost, seasons 30–59) is reported as the only habitability proxy, with its
  60-season limit stated**. The map never reports an unrun point as "habitable". Stage 1 overrides the census wherever
  both exist.
- **C3** (rest on the densest terrain, R3): the motors-off displacement of 20 founders per fauna on c = 2. If more than
  2 of 20 drift over 0.25 m, c = 2 is flagged and its calls carry the flag.

### 5.2 The Stage 1–2 arms

Seeds are **common across points** (j = 1…16, seed 129000 + j): the same founders and terrain stream everywhere, so the
axis contrasts are paired by founder set. This makes the per-point tests dependent; §7.1 says how BH is checked
against it.

| arm | what | seasons | seeds |
|---|---|---|---|
| **S** side by side | the two faunas in their own ecologies (60 slots each), as every committed run | 0–299 | all |
| **M** merged (**gated**, below; the one-world income column and the interference table) | `--merge-after 60 --pooled-capacity 120`, **forked from S's season-59 checkpoint** (K1 proves the fork equals a run from 0); then one arena, one pooled capacity | 60–299 | all |
| **N** matched drift null | `--merge-null K` (RBT-129a, §5.6), forked the same way: at season 60, the other fauna is replaced by a separately labelled, independently streamed copy of fauna K (K = holistic on odd seeds, designed on even), **subsampled to the replaced fauna's count at season 59**, so that N starts from M's composition (M1); then merged exactly as M | 60–299 | odd seeds holistic-null, even seeds designed-null (all seeds at the pilot); **only where census g0 ≤ 0.8** (below) |

| **R_sel**, **R_marker** retention (§6.4) | at PAYS points only, ranked by census g0: one fauna's founders all planted carriers (R_sel), and the same with the motif's food sensors lesioned (R_marker, the floor and planted negative); R_drift descriptive only, if `--breed-gate none` has merged | 0–299 | all |

`merge_after` is UNSHIFTABLE in `ecology.py`, so the fork is a resume of S's state at season 59 with the merge set in
the resumed config; RBT-129a adds that path and its test (K1).

**The M/N gate** (coordinator 22:56; r3: R2-S1, S-5, S-6). Under shuffle, RESOLVING is expected at 0–2 of 36 Stage-1
points (`prior_regime.txt`), so the share layer is demoted to a small, descriptive column:
1. **M** runs, as the **one-world income column** and the interference table (the only shared-world evidence in the
   sweep), at every point whose census g0 (seasons 30–59, faunas pooled, + 0.35; the early regime, lower than the late
   one) is ≤ 1.0, with neither fauna FOUNDING-FAIL. Points are ranked by census g0, lowest first, up to 12 Stage-1
   points, 4 Stage-2a points and 6 R-B points.
2. **N** runs only where census g0 ≤ **0.8**, shuffle's actual resolving bound (`power.txt` §5), up to 4 Stage-1
   points, 2 Stage-2a points and 2 R-B points. A share call (WIN, TIE, CONTINGENT) needs N at the point; an M arm without
   N reports y′ descriptively.
3. **The anchors** (`c1-p030-U-L`, `c0-p030-U-L`, `c1-p030-PW-G`) are RBT-118's fixed points, where RBT-118 runs its own
   M and N arms at n = 20 to 1,200 seasons. The sweep **does not re-run them**. It coordinates seeds with RBT-118 (§9.1)
   and takes the anchors' share and one-world income results from RBT-118's arms, read at the sweep's window
   (240–299), labelled as RBT-118's.

At a point with no M arm the share layer reads **SATURATED (not run; census g0 = x)**, and the body call falls to the
income and survival layers, which R-A uses there (§4.2). If the pilot's M arms find the real drift or the real regime
far from the replica's (§4.1), the gate's thresholds are rescaled by the same ratio before Stage 1.

**The merge at season 60.** The holistic founding bottleneck falls at season 11 and refills within one lifespan on
29 of 30 default histories (RBT-118 §2), so a merge before 60 would read the founding lottery, not the bodies. Sixty is
one max age. The income lead's onset (median 40, IQR 24–90) falls before or near it; the read window starts 180 seasons
after the merge.

**The read window: seasons 240–299** for every point outcome: three lifespans after the merge, and past the 90th
percentile of the prior lead onset.

### 5.3 Measurements

**(a) Performance** (arm S, side by side; and arm M, in one world). Per fauna, over seasons 240–299:
- **income flow**: mean over living members and seasons of the season net (food − p · kJ), **with net income per
  birth printed beside it at every point** (adversary S-3: at a point where a fauna is near viability, its starving
  members leave the living average, so the flow sits near the living cost whatever its members earn). This is a flow,
  not the
  season table's survivor-weighted `mean_lifetime_score` (RBT-118 §0), which is also printed for continuity;
- net income per birth; alive, births, deaths (starvation and age); extinction and its season;
- food, work (kJ), path, per season; **items per new cell covered** (R7's coverage-normalised foraging; recorded by
  `steer.py` on the probed members);
- **the M arm's income flow per fauna** in the shared arenas, as a second income column (adversary S5), so that a share
  result and an income result from one world sit side by side;
- per clutter level: the share of items unreachable (inside an obstacle's footprint), and each fauna's food per new
  cell (S4).

**(b) The head-to-head** (arms M and N).
- **Share**: the holistic fauna's share of the 120 pooled slots, mean over seasons 240–299; **the share at the merge**
  (season 60, from both faunas' counts at season 59, which are printed per seed); the change y′ between them (§6.1);
  fixation (one fauna at 0) and its season.
- **Interference**: each fauna's income flow in the merged world minus its S-arm flow, and per-group composition with
  each member's food (RBT-118 §6.3). Printed, not called.
- **The null's role.** The null N gives, at the same point and demography: (i) the **centring check K2**: the
  relabelled change y′ must centre on 0, which the merge's coupling (groupings and breeding order drawn from the
  holistic stream, `ecology.py` docstring) could break; (ii) **the drift SD** of y′ at that point's turnover, pooled
  per kind across points for CONTINGENT (§6.1); (iii) the fixation-time distribution under no body difference.

**(c) Perception** (arm S; the merged world is secondary). At season 0 (founders) and season 300, 20 living members per
fauna per seed (all of them if fewer are alive; a fauna-seed with fewer than 5 is missing, not zero), drawn by a fixed
RNG (129300 + j), are probed solo in the point's world, on draws from that point's
admissible pool (RBT-116 r5's 64-draw pool and reachability screen):
- **intact − decoy food** on 8 draws per member: the rotated decoy (RBT-116 r5), lesion (sensors read 0), motors-off;
- **STEERS**: RBT-116's instrument as ruled (staged 4 + 16 + 16 draws, F_MIN = 0.25, the ΔT bound, the
  trajectory-identity veto, v_min from the member's own speed). The sweep adopts whatever version RBT-116's ruling
  fixes, and uses it unchanged at every point;
- **the planted set, per point** (not per seed), **8 hosts per plant** (adversary M7d): (a) the Pioneer compass plant
  and (c) the tuned holistic two-nose plant, both **at the fixed registered rung a = 6** (the world gate's), not at
  "the first paying rung", which does not exist where the world does not pay (M7a); (b) the paying kinesis plant; (d)
  the sensorless full-throttle tumblers (rod, hinge, ball) and (e) the same tumblers with two unwired food sensors;
  plus a motors-off body. G8(b) is fed from a non-root nose, per the RBT-116 adversary's M5;
- **the founders** (season 0, the same 20 × 8 per fauna per seed) are also the **operative negative** (R10's third
  clause; adversary S7), and the only source of the false-STEERS rate.

**(d) The regime**: RBT-126's readout on every S and M arm, per fauna and per 60-season window.

**(e) The R8 levers** on the same 20 probed members per fauna, **for both faunas**: Σgear/(4M) and **the share of
members whose gear the budget had to scale ("cap binding", RBT-120's `motor_report.py`)**; resting drive; the
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
3. **The ecology's weakness is reported, not hidden.** Where a world pays perception (PAYS) but the share layer is
   SATURATED and no fauna perceives, the map says exactly that (§6.3's cross-tab), without reading it as "selection
   cannot act" (§6.2); that cell is RBT-116's W2 (§9.2), where imposed selection asks the capacity question.

**The breeding rule: the committed shuffle, registered as primary** (coordinator, 22:56; a design decision, not a
ruling on which rule is right).
- **Why no other rule.** RBT-126 (merged, `d1eb1ae`) screened 11 rules against planted variance negatives: **none
  passes** (`runs/RBT-126/BREEDING-RULES.md`, `screen.txt`). Energy order and `--energy-leak 0.3` spread a same-mean,
  higher-variance mutant (RBT-126's adversary, #417; and here, `power.txt` §7: H-WIN 1.00 for the variance mutant under
  both, and leakx:0.3 even spreads the 0.9× mean-loss mutant). The closest, `lcb:3` (rank by the lifetime mean minus 3
  standard errors), fails the two-point same-mean ("feast or famine") mutant at g0 ≤ 1.3 and halves parent depth.
- **What shuffle does.** It spreads neither a gain nor a variance mutant above viability (RBT-126). Under shuffle a
  1.25× forager is indistinguishable from neutral once resident gross income g0 ≳ 0.8, and fixes readily at g0 ≤ 0.5
  (`adv_demography_invasion.txt`).
- **Consequence 1: share calls are read "under the committed rule".** Every share-layer call (WIN, TIE, CONTINGENT,
  SATURATED) is printed with that qualifier.
- **Consequence 2: RESOLVING will often fail.** On the prior arithmetic, 0–2 of the 36 Stage-1 points are expected to
  be RESOLVING under shuffle, 3–12 to take a survival call, and 24–31 to read SATURATED (`prior_regime.txt`; §6.2).
- **Consequence 3: the M/N gate** (§5.2). Running M and N at every point would spend about 550 core-h on a layer the
  priors say is SATURATED almost everywhere. So M runs only where the census regime is ≤ 1.0 (as the one-world income
  column), N only where it is ≤ 0.8, and the anchors' M and N come from RBT-118. The savings fund the retention layer
  and its controls (§6.4), whose own power the regime also bounds (one step later).
- **Consequence 4: the question the sweep answers** (§1, §8). Under shuffle the sweep answers "which body *earns*
  more, where", not "which body *persists*".
- **The starvation sieve reads income variance too.** Under shuffle, the same-mean variance mutant is not spread, but
  it is **selected against** by starvation (`power.txt` §7: y′ −0.37 to −0.48, D-WIN 1.00 at n 16): more zero-income
  seasons mean more deaths at energy 0. That is a real viability cost, not a rule artefact, but it means a share call
  under shuffle reads the income's variance as well as its mean. §6.1's **VARIANCE-DRIVEN** flag carries it.
- **`lcb:3`, secondary and descriptive** (optional; only if RBT-126's follow-up gives it a flag): M and N arms under
  `lcb:3` at the 3 anchors (§9.1's W118-a, -b, -c), 8 seeds. Every `lcb:3` call is printed beside the shuffle call with
  its known failure beside it ("spreads a feast-or-famine same-mean mutant at g0 ≤ 1.3; halves parent depth"). It
  never enters a family, a map statistic or a verdict. The replica here does not implement it.
- **Amendment path.** `power.py` implements the rule as a parameter (lottery, energy, `leakx:λ`). A rule that later
  passes RBT-126's screen can be substituted by amendment, with `power.txt` §2, §5 and §7 re-run under it before any
  arm.
- RBT-126's corpus-regime readout finds that past selection headlines were read in the saturated band, which is why the
  share layer's TIE is gated (§6.2).

### 5.5 Controls (R10)

| id | control | passes when | if it fails |
|---|---|---|---|
| K1 | fork identity | a fork of S's season-59 checkpoint with the merge unset reproduces S's seasons 60–64 byte for byte (`seasons.txt`, `lineage.jsonl`), at every pilot point | the point's M and N arms are VOID |
| K2 | null centring, on y′ (only at points with N: census g0 ≤ 0.8, and RBT-118's anchors) | **pooled** over a stage's points, the null's mean y′ differs from 0 by < 0.05 (t over seeds); **per point**, the null's y′ t test is not rejected under BH at q = 0.10 over points, **and** |mean y′_null| ≤ 0.15 (adversary S3: the size bar alone VOIDs 1 point in 8 by chance under energy order) | pooled: the share layer is VOID for the stage; per point: that point's share call is VOID |
| K3 | planted positives, **on the behavioural legs** (M7a) | of the 16 pooled (a) + (c) hosts at a = 6, ≥ 4 pass the trajectory-identity veto, have a ΔT lower bound > 0, and are called SMELL-USE or STEERS, with ≥ 1 of each kind. F ≥ F_MIN is **not** required here: at a point that does not pay, a planted steerer that reads SMELL-USE shows the instrument can see steering and the world does not pay it. False-VOID rate: 0.011 at a true per-host sensitivity of 0.5, 0.065 at 0.4 (binomial, 16 hosts) | the point's perception layer is VOID |
| K4 | planted negatives | G8(b), (d), (e) and motors-off: no STEERS; intact − decoy CI covers 0. **(d), (e) and motors-off cannot fail** (their intact and decoy trajectories are identical by construction; adversary S7) and are kept as instrument checks only. **G8(b) can fail only where kinesis can reach F ≥ 0.25**; elsewhere the point prints "T's discrimination is untested here" (M7b) | the point's perception layer is VOID |
| K5 | founders, **the operative negative** | the founders' confirmed false-STEERS rate at the point (20 × 8 per fauna per seed, a G4-style confirmed rate) is ≤ 0.05 with its exact upper bound printed; the founders' intact − decoy is the baseline, and a PERCEIVES call needs the evolved population to exceed it | the rate > 0.05: that fauna's perception layer at the point is VOID |
| K6 | the rest check on c = 2 | census C3 | c = 2 calls carry the flag |
| K7 | side effects | printed per point against `c1-p030-U-L` (§5.1) | — |

### 5.6 Code this design needs: RBT-129a (to ticket, same discipline as the fairness set)

Off by default and byte-identical when off, with tests:
1. **`--merge-null KIND`** (adversary M8). At `merge_after`, the other fauna is replaced by **B**, a copy of KIND's
   population subsampled to the replaced fauna's count, and the two are merged. B is a **separate label**, not a second
   `kind = KIND` cohort, because `ecology.py` keys mate choice (line 531), the breeding stream (line 591) and the
   persistent arena bank on `kind`. B has:
   - **its own mate pool** (B breeds only with B);
   - **its own stream**: an independent `SeedSequence` child, as `breed_seed_sequence` does;
   - **its own lineage names**, and KIND's body model.

   **The arena bank at the merge** gets a fresh bank keyed on the merged cohort's labels, i.e. full arenas at season 60
   in PW. M and N see the same transient.

   **Tests:**
   - a B child never has an A parent;
   - B's draws are independent of A's;
   - the arena-bank transient is identical in M and N at one seed;
   - with the flag off, runs are byte-identical.
2. **The fork at season 59** (§5.2): resume S's state with the merge set, and its K1 test.
3. **Merged logging** (RBT-118 §6.2–6.3): per season per fauna (or label), share, deaths split by starvation and age,
   eligible breeders, median energy, and food, work and path means; per group, composition and each member's food; both
   faunas' counts at the merge.
4. **`--obstacle-radius`** (`world.random_radius` is config-only today), so the clutter density of §3.1 is a flag,
   with N set from the free area and the realised count and free-ground density printed per level and layout over 100
   terrain seeds (S3).
5. The world block export (`runs/RBT-129/worlds/<id>.json`), written from one table so that no point is typed by hand.

## 6. Per-point calls

All per-point tests take the **seed as the unit** (n = 8, or 16 after R-B), use a two-sided one-sample t test on the
seed-level statistic, and are corrected by BH at q = 0.10 within their family (§7.1). "BH-significant" below means
rejected by that procedure.

### 6.1 The body call (the map's main layer)

**Valid seeds (adversary M2).** A seed is valid for the share test when **both faunas are alive at the merge** (season
59's counts, printed per seed), and valid for the income test when both are alive in S through season 239. Invalid
seeds are counted and reported, never averaged.

Statistics per valid seed j:
- **share, net of the merge (adversary M1)**: y′_j = (the M arm's mean holistic share over seasons 240–299) − (the
  holistic share at the merge, from the two counts at season 59). Under no body difference the pooled share is close
  to a martingale, so the raw share would read the merge-time head count as a body win: a fauna short by half at the
  merge gives a false D-WIN with probability 0.72–0.79 at q/2 under the lottery (`probe_merge.txt`), against
  0.01–0.05 for y′ under every rule and every merge-time count (`power.txt` §6a);
- **income**: x_j = the S arm's holistic income flow minus the designed one, seasons 240–299 (a paired difference).

Margins: δ_s = 0.10 in y′ (12 of 120 slots); δ_i = 0.15 items a season in income (0.6 × the living cost, and 1.5 × the
selection threshold of about 0.1 item a season that RBT-121 B names). An income TIE at ±0.10 is nearly unreachable at
the realised noise (`power.txt` §1), so the wider margin is registered; even at ±0.15 a TIE needs the noise floor and
n = 16.

The call, in order (the first that applies):
1. **EXCLUDED-H / EXCLUDED-D / NEITHER**: a fauna is extinct in its own S arm by season 299 on ≥ 5 of 8 seeds (≥ 10 of
   16). The point is a survival win for the other (a separate count, §7.2 M1), not a share call.
2. **PARTIAL-H / PARTIAL-D** (M2): fewer than 6 of 8 (12 of 16) seeds are valid for the share test because a fauna
   was extinct at the merge. PARTIAL-X names the fauna that survived. It is a survival call, counted with EXCLUDED in
   M1, and **never a WIN**.
3. **VOID**: K1 or K2 failed at the point.
4. **H-WIN**: the share test on y′ is BH-significant with mean y′ > 0 **and** mean y′ ≥ δ_s.
5. **D-WIN**: the mirror.
6. **CONTINGENT (M4)**: F = var(y′)/σ̂²_null exceeds its one-sided 0.99 point, where σ̂²_null is **the null's y′
   variance pooled per kind over the points that have N (the sweep's gated N points, census g0 ≤ 0.8, and RBT-118's
   anchor nulls, read at the same window), with the kind offset removed. The pooled drift SD is assumed homogeneous
   across those points' regimes (under shuffle, 0.145–0.157 over g0 0.5–1.3, `power.txt` §2). r3 (adversary S-2): the
   df is about (k × 4 − k) per kind from the sweep plus RBT-118's, not r2's 108; CONTINGENT is **not callable** at a
   stage whose pooled per-kind df is below 12, and `power_r3.txt` §6b′ gives its rates at df 6–40. The F test must be
   BH-significant in its own family (§7.1), and neither 4 nor 5 holds. History
   decides the winner at this world, seed by seed. The point's own null serves only K2. CONTINGENT points are
   eligible for R-B (§4.2).
7. **TIE**: TOST on y′ at ±δ_s succeeds (BH within the TIE family), **and** the point is RESOLVING (§6.2).
8. **SATURATED**: the point is not RESOLVING, and none of the above holds.
9. **UNDECIDED**: otherwise.

**MARGINAL (r3, adversary S-3).** An EARNS call is marked **MARGINAL** when either fauna's net income per birth at the
point is below the living cost (0.25): the income of the living is then compressed, and the call is printed with both
per-birth incomes beside it. MARGINAL calls count in the verdicts, flagged.

**The income layer** is called beside it, in this order: **EARNS-H / EARNS-D** (BH-significant, |mean x| ≥ 0.10),
**EARNS-TIE** (TOST at ±δ_i), UNDECIDED. The M arm's per-fauna income (§5.3a) is printed beside it as the one-world
column. The body call is the share call; the income call is its mechanism, and R-A's layer where a pair is not
RESOLVING.

(A share WIN that is VARIANCE-DRIVEN, below, is printed as such and is not a WIN in §8.)

**LEVER (adversary M6).** R8 attributes a fauna difference that **goes with a lever difference** to the lever. So LEVER
is defined on the difference between faunas, on levers that R1–R3 do not already budget, and it is printed for both
faunas at every point. A WIN or EARNS call is marked **LEVER** when the winner's median exceeds the loser's by more than:
- 0.25 in the share of work on contact-free children;
- 0.25 m in motors-off displacement;
- 0.2 in resting drive;
- 0.25 in the share of members whose gear the budget had to scale ("cap binding", RBT-120's `motor_report.py`),
  which replaces r1's "at the cap": a holistic fauna at the Pioneer's motor class is what `--fair` allows, not a lever.

LEVER points are reported and excluded from the win counts of §7 (M1, M4). A fauna that exploits a lever and **loses**
is printed the same way, since the flag is on the difference.

**VARIANCE-DRIVEN (coordinator 22:42 / 22:56).** Under shuffle the starvation sieve selects against income variance
(`power.txt` §7), so a share WIN can come from a difference in the spread of income, not its mean. Every share call
prints each fauna's season-to-season SD of member income and its share of zero-income seasons (M arm, seasons
180–299). **The test (r3, adversary S-4)** asks which explains the WIN better, not whether the mean test failed (at
n 8 a real WIN's mean test often fails). Per seed, regress y′_j on the two faunas' mean-income difference and their
income-SD difference, both standardised, and compare the two partial t statistics. A WIN is marked **VARIANCE-DRIVEN**
when the SD term's partial t in the WIN's direction (the loser has the larger SD) exceeds the mean term's, and the
mean term's is below 2. A
VARIANCE-DRIVEN WIN is counted in M1 and M4 as its own category, and is **not** a WIN in §8's verdicts: it says the
world's starvation risk favours the steadier earner, which is a finding about the world, not about which body earns
more.

### 6.2 Resolvability: when "no difference" may be called TIE (adversary M3)

A point is **RESOLVING** when the replica, at the point's g0, the ruled breeding rule and the point's n, gives **both**:
- P(share TIE on y′ | income edge = δ_i = 0.15) ≤ 0.05; and
- P(share WIN on y′ | income edge = δ_i) ≥ 0.80,

both at q/2, the BH threshold in force once a few points reject, **and** the planted variance negatives stay silent
(coordinator addendum, 22:42):
- P(H-WIN | a **same-mean, variance-only** mutant, 3× the season variance) ≤ 0.05; and
- P(H-WIN | a **0.9× mean-loss, variance-gain** mutant, 3× the variance) ≤ 0.05,

each against a neutral designed side at the point's g0, rule and n, beside the neutral marker (`power.txt` §7). A rule
that reads income variance as merit fails this at the points where it does so, and the point cannot call TIE or WIN
through the share layer there; `power.txt` §7 shows where each rule fails. This ties RESOLVING to the income layer's own TIE
margin: a share TIE at a RESOLVING point excludes an edge the income layer would call non-equivalent. (r1's check used an
edge of 0.25 × g0, 1.3–1.7× δ_i, and let a lottery point at g0 ≈ 1.0 read TIE with a true edge of 0.10 in 41% of runs at
n = 16; `probe_tie_lottery.txt`.)

- **g0** is the point's resident gross income: the mean season net income of the living (food − p · kJ; the M arm,
  seasons 180–299, faunas pooled) plus the replica's 0.35 (its 0.1 work charge and 0.25 living cost). g0 enters as an
  estimate, so **the check is run at both the lower and the upper 90% bounds of g0 over seeds, and the point is
  RESOLVING only if it passes at both**. This takes the adversary's lower bound, and also covers the lottery's
  conservative side, which is the upper one (saturation rises with g0; `power.txt` §5).
- **The rule**: `power.py`'s `resolvable(g0, rule, n)` implements lottery, energy and `leakx:λ` (RBT-126's
  `--energy-leak λ`). The registered rule is **shuffle** (§5.4); `power.txt` §5 and §7 print all three, so that a
  later rule can be substituted by amendment.
- **Replica seeds**: 1,500 per check (r1: 300), because the check sits near its bars in the band g0 0.9–1.1.

Otherwise a no-difference result is **SATURATED**: at that point the **share and spread** of a fauna through births do
not resolve an edge of δ_i. This prevents a lottery-saturated world from being read as evidence that the bodies are
equal (RBT-118 §2: "an income lead is not a fitness lead here").

**Under the registered shuffle** (`power.txt` §5, lottery rows): RESOLVING at g0 ≤ 0.65 (n 8) and ≤ 0.80 (n 16); not
at g0 ≥ 0.9. The planted variance negatives are silent on the merit side (P(H-WIN | variance mutant) ≤ 0.01 at every
g0; §7), so shuffle passes the negatives the energy-ordered rules fail. **On the prior arithmetic
(`prior_regime.py` → `prior_regime.txt`), 0 (pre-fairness work bills) to 2 (the designed bill halved, the holistic
bill × 0.8) of the 36 Stage-1 points are RESOLVING**, both at p = 0.08 in PW; 3–12 take a survival call (the designed
fauna starving at p = 0.08 and at c = 2); the other 24–31 read SATURATED. Expect a body map carried by the income and
survival layers, with the share layer read at a handful of points.

**What SATURATED does not mean (R5, coordinator addendum).** SATURATED is a statement about the share and spread layer
only: births at that point do not resolve an edge of δ_i. No call in this design reads it as "selection cannot act at
this point": the income layer, the perception layer (which reads what is present in the living population, whatever
spread it) and the R8 levers are called at a SATURATED point exactly as elsewhere. Retention (§6.4) is a separate
question with its own power, which the regime **also** bounds, one step later than spread (R2-CHECK §3.1).

### 6.3 Perception, per fauna

Statistic per seed: f_j = the mean over the 20 probed members and 8 draws of (intact − decoy) food at season 300, minus
the same for the seed's founders at season 0 (K5).

- **VOID**: K3, K4 or K5 failed at the point (§5.5).
- **PERCEIVES**: f is BH-significant (family per fauna), mean f ≥ F_MIN = 0.25 (RBT-116's F_MIN), **and** the pooled
  count of confirmed STEERS members over the point's seeds (up to 160) exceeds the upper 95% binomial bound of the
  count expected from **the founders' own confirmed false-STEERS rate at that point** (adversary S7: pooling the
  structurally silent plants would bias the rate toward 0 and make PERCEIVES easier).
- **SMELL-USE**: f passes, STEERS does not. Smell changes what the body does, but the instrument cannot call it
  steering (klinokinesis is inside STEERS by RBT-116's definition; this is the remainder).
- **NONE**: otherwise.
- PERCEIVES and SMELL-USE are reported **by route**: one nose against two (§3.4).

**The world layer PAYS, per fauna** (the census's 18 cells, §5.1): at that cell, the fauna's nose step pays at least
comparably to a speed step, and its planted prize (designed: RBT-106's at a = 6; holistic: the G8(c) plant at a = 6) has a
lower bound > 0. A point takes PAYS from its (L, s, c) cell.

**The reading** of a point's perception is the cross-tab PAYS × RESOLVING × {PERCEIVES, SMELL-USE, NONE}, per fauna:
- PAYS, and PERCEIVES: the world pays perception and the ecology found it;
- PAYS, SATURATED and NONE: the world pays, and this ecology's births do not spread an edge of δ_i; whether a trait
  could still be **held** here is not tested by the sweep (retention is not spread), and this is RBT-116 W2's cell
  (§9.2), where imposed selection asks the capacity question;
- not PAYS, and NONE: the expected result in a coverage world (R4). With K3 on the behavioural legs (§5.5) this cell
  is now **readable**, not VOID by construction. At a G point it is written "contrast-only perception does not pay
  here", never "perception does not pay" (§3.4);
- not PAYS, and PERCEIVES: a surprise, read against the planted set before anything else.

### 6.4 Retention, per fauna (coordinator 22:56; r3: adversary R2-M1)

Whether the world **holds** a paying perception trait once it is present. **The regime bounds this too** (R2-CHECK §3.1,
`design-adversary/probe_retention.txt`): under shuffle, retention is visible for a trait worth 0.1 items at a carrier
income of 0.6, but not at 1.3 unless the trait is worth about 0.4 or more. r2's claim that the saturated band does not
bound retention is withdrawn. Retention is bounded one step later than spread, and it is honest where it cannot be
read (NOT HELD fires falsely at ≤ 0.04).

**Power of HOLDS by regime × trait value** (the adversary's replica; shuffle; n 8; q/2; mean h ≥ 0.10; h against the
marker floor):

| carrier gross income gc | Δ 0.00 (false HOLDS) | Δ 0.10 | Δ 0.20 | Δ 0.40 |
|---|---|---|---|---|
| 0.6 | 0.03 | 0.93 | 1.00 | 1.00 |
| 0.9 | 0.03 | 0.12 | 0.39 | 1.00 |
| 1.3 | 0.03 | 0.06 | 0.09 | 0.24 |

A perception step in PW is worth about 0.17–0.19 items on the kinematic model, and the planted prize at a = 6 is
probably larger. So HOLDS is readable at census g0 ≲ 0.9, and at richer points only for a trait worth ≳ 0.4.

- **Where:** Stage-1 G points with PAYS for that fauna (census, §5.1), at most 12 fauna-points, **ranked by census g0
  (lowest first)**; ties are broken PW before HP before U, then c = 1 before c = 0 before c = 2. Points with census
  g0 > 1.3 are not used.
- **Arms** (R2-M1a):
  - **R_sel(F):** the point's S arm, except that fauna F's 60 founders all carry the planted trait at the fixed rung
    a = 6 (designed: RBT-106's routed compass motif, as G8(a); holistic: the G8(c) tuned two-nose plant). The other
    fauna has random founders in its own ecology, as in S;
  - **R_marker(F):** the same economy, founders and motif at a = 6, with **the motif's food sensors lesioned**, reading
    the transform's zero-information constant, as `steer.py`'s lesion condition does. It is **the floor and the
    planted negative in one arm**. It matches R_sel's turnover and operators exactly, and a motif held for its motor
    effect (gait, speed) is held in both arms, so HOLDS cannot fire on it;
  - **R_drift(F), descriptive only, and only if RBT-126's `--breed-gate none` has merged** (#419, under review):
    the same founders under `--neutral --breed-gate none`, as a second floor printed beside the marker's. It enters no
    call. If the flag has not merged, R_drift is dropped.
- **Carriage** at season 300: the share of F's living members whose genome still carries the planted motif at ≥ half
  its planted weight (a wiring readout).
- **The readout's floors, validated before any arm** (R2-M1b, R10):
  - on the planted founders it must read ≥ 0.95;
  - on random founders of each fauna, its **false-carriage rate** is printed, and it is the readout's floor;
  - on children with the motif's links deleted or halved, it must read absent.

  This matters most for the holistic plant: its two noses sit on two expressed Parts of distinct Nodes, which
  structural mutation can re-express, duplicate or drop, and it has no RBT-80 precedent. If the readout fails any of
  the three on a fauna, that fauna's retention layer is VOID.
- **The behavioural confirmation leg** (R2-M1d): 20 R_sel members per seed, probed at K3's bars (16 hosts pooled,
  the behavioural legs: the trajectory veto, ΔT > 0, SMELL-USE or STEERS). **The same probes on 20 R_marker members
  must read NONE**, a second check able to fail. If either fails, that fauna-point's call is VOID.
- **The operator table** (R2-M1c, R6), per fauna and retention point:
  - the erosion rate u_f per birth: the fraction of a planted carrier's children that lose carriage, measured as
    RBT-116's G6 does, crossover 0;
  - the realised births per season in R_sel and R_marker.

  The holistic operator erodes wiring about 5× faster (R6). So "HOLDS for the designed fauna, not for the holistic" is a
  statement **at the default operators**, printed so. It is re-read at **matched erosion** (`--structural-rate-scale`
  set so that u_H = u_D) at one point at least: the lowest-g0 retention point that has PAYS for both faunas, with
  R_sel and R_marker for both. Only that re-read may be worded as a body-plan comparison of retention.
- **Statistic:** h_j = carriage(R_sel) − carriage(R_marker), per seed.
- **Calls:** **HOLDS**: BH-significant > 0 (family per fauna) and mean h ≥ 0.10. **NOT HELD**: TOST at ±0.10 succeeds,
  or mean h < 0 is BH-significant. **UNDECIDED** otherwise.
- **Reading:** HOLDS shows the world's selection holding contrast-only perception there once present, beside what the
  share layer and PERCEIVES say. HOLDS with PERCEIVES NONE says "held if present, not found from scratch here". At G
  points it is worded "contrast-only perception is held" (§3.4). UNDECIDED at a point with census g0 > 0.9 is the
  expected reading for a small trait and says nothing about the bodies.

## 7. The map's summary statistics (pre-registered)

### 7.1 Families and multiplicity

| family | tests | procedure |
|---|---|---|
| share (WIN) | one per point: y′ ≠ 0 | BH, q = 0.10, over every Stage 1–2 point (K ≤ 52) |
| share (TIE) | one per point: TOST on y′ at ±δ_s | BH, q = 0.10 |
| share (CONTINGENT) | one per point: the F test against the pooled null (M4c) | BH, q = 0.10 |
| null centring (K2) | one per point: the null's y′ t test | BH, q = 0.10 |
| income (EARNS), income (TIE) | one per point each | BH, q = 0.10 each |
| perception, holistic; perception, designed | one per point each | BH, q = 0.10 each |
| retention, holistic; retention, designed (§6.4) | one per fauna-point each | BH, q = 0.10 each |
| map-level tests T1–T4 | four | Holm, α = 0.05 |

- BH controls the directional false discovery rate for sign calls made on rejected points (Benjamini & Yekutieli
  2005) under positive dependence of the one-sided statistics. **For two-sided tests that is not guaranteed** (adversary
  S9), so the correlation of the seed-level statistics across Stage-1 points is printed (mean and maximum over point
  pairs, per layer). **If its mean exceeds 0.3, Benjamini–Yekutieli-adjusted calls are reported beside BH's**, and a
  call that holds under BH only is marked so.
- Stage-1 calls are **provisional**. The final map applies BH once, over all points, after Stage 2, with R-B's
  combined p-values.
- Points of the smell-L subset and the refinement points are in the same families.

### 7.2 The statistics

- **M1 (the call table).** Counts of each body call and each income call, per layout and smell, and overall; the
  survival count (EXCLUDED and PARTIAL, per fauna); the LEVER count; the census layer (FOUNDING-FAIL and the census
  regime) at the unrun points, flagged as such.
- **M2 (the world model; adversary M10, S6, S7).** Fitted **at the seed level**, not on point means, so no 1/SE²
  weight can be unbounded when a point fixes:
  - **share** (secondary; only at points with an M arm): logit(share at 240–299, clipped to [1/240, 1 − 1/240]) −
    logit(share at the merge), on c, log p, L, s, c × log p **and the point's census regime g0** (measured at every
    point and before the read window; the world terms are then net of selection strength, since with a constant edge
    the share still moves with g0, `power.txt` §2), with a random intercept per point;
  - **income** (primary): x_j on **c, log p, L, s and c × log p only**, with a random intercept per point (the
    dispersion term that keeps T1–T3 honest when L × p or L × c is omitted). **g0 does not enter the income model**
    (adversary R2-M2): it is downstream of the axes (the work price and clutter set it), so conditioning on it would
    absorb the effects T2 and T3 test, and the M-arm g0 is missing at gated-out points.
  - **Registered fit:** the **Stage-1 grid only** (orthogonal in c and log p, and not chosen from the data), valid seeds,
    habitable non-VOID points. **Sensitivity fit:** with the Stage-2a points (which R-A places along the boundary,
    collinear in (c, log p)) and the R-B extensions (with the median-unbiased estimate at extended points, since R-B
    selects on a small |z₁|).
  - Coefficients with 95% CIs. Signs are predicted from the prior (§12).
- **M3 (break-even curves).** For each (c, L, s) row with at least two price levels, the price p*(c) at which the fitted
  income effect crosses 0 (a line in p per row, which is what the static arithmetic says it is), with Fieller 95%
  intervals. They are compared with RBT-118's 0.018 (c = 1) and 0.053 (c = 0), which are pre-fairness.
- **M4 (the area shares).** Over the 27 Stage-1 G points, equally weighted: the fractions H-WIN, D-WIN, TIE, CONTINGENT,
  SATURATED, UNDECIDED, EXCLUDED, PARTIAL, VOID, LEVER. The same over the 9 L points, and with the Stage-2a points
  added, each refinement point taking the weight its bisection splits off its parent pair.
- **M5 (the perception map).** Per fauna, the count and positions of PERCEIVES and SMELL-USE, by route; HOLDS and NOT
  HELD at the retention points, beside PERCEIVES; the cross-tab
  of §6.3; the perception gap f_H − f_D per point; and the smell contrast (G − L) at the 9 matched points, read as
  "contrast instead of level" (§3.4).
- **M6 (concordance).** Cohen's κ between the share call's sign and the **M arm's** income sign over points where both
  are decided (one world); the same against the S arm's income (side by side), labelled so; the interference table
  (merged income − side-by-side income, per fauna).
- **M7 (monotonicity).** Along every price and clutter row of the final map, the number of sign changes of the income
  effect; rows with more than one are listed.

### 7.3 The map-level tests (Holm, α = 0.05)

- **T1 (dependence; adversary S8).** On **income**, as primary: M2's income world terms (c, log p, L, s, c × log p)
  jointly zero, a Wald test on the registered (Stage-1) fit. The same test on the share model (net of g0) is reported
  as secondary, outside Holm. r1's data-dependent switch between them is withdrawn.
- **T2 (clutter).** M2's income coefficient on c is zero. Predicted > 0 (clutter favours the holistic fauna).
- **T3 (price).** M2's income coefficient on log p is zero. Predicted > 0 (dearer work favours the body that spends less).
- **T4 (smell; adversary M9).** A **seed-level** paired test in **PW**, the layout the world gate certifies: per seed j,
  d_j = the mean over the three PW points (c = 1; p = 0.01, 0.03, 0.08) and both faunas of (f_G − f_L); a one-sample t
  on the n values of d_j (seeds are common, so G and L at one seed share founders). Predicted > 0. HP's same contrast is
  reported as a second, stated contrast outside Holm; U's is printed. r1's t over 9 heterogeneous points had power
  0.00–0.19 when the channel pays only in PW, which is what R4 and the gate predict (`probe_t4.txt`); the seed-level
  test's power is in `power.txt` §6c.

## 8. What would falsify "it depends on the world"

Verdicts on the framing, from the final map (adversary M11; r3: R2-M3, R2-S1).

**What the sweep answers, plainly.** Under the committed breeding rule (shuffle, §5.4) the sweep answers **"which body
*earns* more, where"**, and where each body can live. It does **not** answer "which body *persists*": the share layer
that would say so resolves at 0–2 of the 36 Stage-1 points (§6.2), and that question waits on a breeding rule that
passes RBT-126's screen. The share-based verdicts are kept below their income counterparts, marked as not expected to be
reachable under the registered rule.

**Terms.** A **decided share call** is H-WIN, D-WIN or TIE; a **decided income call** is EARNS-H, EARNS-D or EARNS-TIE;
a **survival call for fauna Y** is EXCLUDED-(other) or PARTIAL-Y (Y lives where the other does not). LEVER and
VARIANCE-DRIVEN calls are not counted as wins. "Habitable" means neither fauna EXCLUDED or PARTIAL, and not VOID.

**An opposite-sign set** (adversary R2-M3). A set of calls for one fauna counts toward a DEPENDS verdict only if it has
**≥ 2 calls**, or **1 call corroborated by M3**: a break-even p* on that call's (c, L, s) row whose Fieller 95%
interval lies inside the swept price range [0.01, 0.08]. One spurious opposite call is otherwise too cheap: in a map a
single body truly dominates, with 6–12 true-zero points among 36, BH at q 0.10 gives ≥ 1 false opposite call with
probability 0.14–0.24, and ≥ 2 with 0.007–0.028 (`design-adversary/probe_verdicts.txt`). **The same rule applies
symmetrically** to "no call for the other fauna" in the dominance verdicts: those verdicts tolerate **one**
uncorroborated call for the other fauna, and fail at ≥ 2 calls or one corroborated call.

**The verdicts, in registered precedence order** (the first that holds is the verdict; the others that also hold are
printed beneath it):

1. **EARNINGS DEPEND**: T1 (on income) rejects, **and** the income layer has an opposite-sign set (as defined above)
   for each fauna: EARNS-H and EARNS-D, each counted by the ≥ 2 / corroborated rule. A claim about income, not about
   which body persists; stated so.
2. **DEPENDS** (on share; **not expected to be reachable under the registered rule**): T1 rejects, and the share layer
   has an opposite-sign set of WINs for each fauna, by the same rule.
3. **EARNINGS DOMINATED (X)**: EARNS-X at ≥ 1/3 of the habitable points, and the other fauna has **no counting set**
   of WIN, EARNS or survival calls (at most one uncorroborated call). One body never out-earns the other in any world
   tested.
4. **ONE BODY DOMINATES (X)** (on share; **not expected to be reachable under the registered rule**; also bounded by
   the M/N gate, which runs M at ≤ 12 of 36 points): X-WIN at ≥ 1/3 of the points with an M arm, and no counting set
   for the other fauna.
5. **DEPENDS ONLY THROUGH HABITABILITY**: over **decided** calls only: every decided EARNS call (or, if there are share
   WINs, every decided WIN) favours one fauna X, with no counting set for the other, and there is a counting set of
   survival calls for the other fauna Y. Where both live, the ranking does not change; only where each can live does.
6. **WORLD-INVARIANT**: T1 does not reject; **no pair of opposite-sign counting sets** in either layer; and EARNS-TIE at
   ≥ half of the habitable points, or share TIE at ≥ half of the RESOLVING points.
7. **NOT RESOLVED**: none of the above.

Verdicts 3, 4 and 6 falsify "it depends on the world" for the swept range, each in its own way; 1 and 2 confirm it; 5
confirms only a dependence of where each body can live. In practice, under shuffle, both the confirming and the
falsifying verdicts run through the income layer (1, 3, 5, 6).

For perception, per fauna F:
- **PERCEPTION EVOLVES SOMEWHERE (F)**: at least one PERCEIVES call for F, not VOID.
- **HELD WHERE PRESENT (F)**: at least one HOLDS call for F (§6.4), not VOID, reported beside the evolve verdicts, with
  the point's census g0 and the operator table printed (a cross-fauna comparison only at matched erosion).
- **NOWHERE IN THE SWEPT WORLDS (contrast-only at G points; level-only at L points)**: no PERCEIVES call for either fauna, including the G points where the world gate
  passed, **and the perception layer is valid (not VOID) at ≥ 2/3 of the PAYS points, per fauna** (adversary M7c; a
  mostly VOID map cannot reach it). This falsifies "contrast-only perception pays enough to evolve" for the swept range (and level-only perception at L points), not perception in general, and the
  PAYS × RESOLVING cross-tab says whether the world or the ecology is the reason. If the validity condition fails, the
  verdict is **PERCEPTION NOT MEASURED**.

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

**The anchors' share results come from RBT-118** (r3, adversary S-6 and R2-S1). The sweep does not run M or N at
W118-a/b/c. Instead it asks RBT-118's registration to:
- **coordinate seeds:** include the sweep's seeds 129001–129008 (and 129009–129016 if the anchor is extended) among its
  n = 20 at each anchor, under the sweep's world block and `--fair`, with S, M (merge at 60) and N arms;
- **report at the sweep's window:** y′ over seasons 240–299, the one-world income per fauna and the null, so that the
  anchors enter the sweep's map as a column labelled "RBT-118".

If RBT-118's registration does not adopt this, the sweep runs M and N at the anchors itself, from the gate's budget
(r2's cost: 3 × 8 × 1.90 ≈ 46 core-h).

**Rule-chosen points** (at most two, chosen by script after Stage 1): the habitable, non-LEVER, non-MARGINAL Stage-1
point with the largest BH-significant income effect |x̄| for each sign, if one exists (the income layer, since under
shuffle the share layer rarely decides). RBT-118's design then replicates it with fresh seeds (seed base 118000), and
adds what the sweep does not: n = 20, horizons to 1,200 seasons, a founding contest (`merge_after 0`), and a
`breed_order` arm (RBT-118 §6.7–6.8).

### 9.2 RBT-116 (the extradimensional bypass)

- **W1** = `c1-p030-PW-G`: r5's W1 already is this block (PW, G = 2.5, random terrain, 0.03/kJ, `eat-from root`,
  15 s). The sweep adopts r5's settings where they overlap (`--random-start` is an `evolve` setting and has no ecology
  counterpart; it is the one field outside the block).
- **W2** (chosen by script after Stage 1): among the Stage-1 points with L ∈ {HP, PW} and s = G, those with PAYS,
  SATURATED and NONE for both faunas, with PAYS for at least the designed fauna (the Pioneer's valley is RBT-116's
  subject) (§6.3's "pays but the ecology does not select it"); of those, the one with the largest census nose-step
  margin. If there is none, W2 = `c0-p030-PW-G`: the Pioneer's best terrain, which separates a
  terrain effect on the valley from a perception effect. The coordinator may override; W2 must pass RBT-116's own
  gates (G1, G2, G6–G9) before any of its arms.
- RBT-116 costs about 420 core-h a point at D = 16 (PR #400 r5 §5), more than ten Stage-1 points. Two points is the
  ceiling this design assumes.

## 10. Power (`power.txt`; bounded, R11)

**Noise floors and ceilings.**

| quantity | floor | ceiling | source |
|---|---|---|---|
| per-seed SD of the income difference | 0.144 (random terrain, n 29) | 0.334 (flat, n 29) | RBT-118 `pool.txt`, `probe_terrain.txt` |
| per-seed SD of y′, no edge | 0.145–0.157 (replica, shuffle) to 0.18–0.19 (energy order) | 0.36–0.45 (with a per-seed edge SD of 0.1, energy-ordered rules; shuffle 0.15–0.36) | `power.txt` §2 |
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
| income EARNS-TIE at a true 0 (±0.15), noise floor, worst / half | 0.08 / 0.68 | 0.62 / 0.98 |
| income EARNS-TIE, noise ceiling | 0.00 / 0.02 | 0.00 / 0.13 |
| share: see §10.1 | | |
| perception: P(PERCEIVES \| f = 0.25), holistic, M 20, D 8 | 0.20–0.67 (worst) / 0.75–0.99 (half) | |
| perception: P(PERCEIVES \| f = 0.40), holistic | 0.64–0.99 (worst) | |

The price band is the MDE divided by the price slope of the income difference, kJ_D − kJ_H, bounded between 6 and
15.5 kJ a season (14.7 before the fairness set; the fairness set is expected to cut both bills).

### 10.1 The share layer by regime and rule (r2: on y′)

`power.txt` §2, §5, §6, §7: the replica, 500 simulated seeds per row (1,500 for §5); y′ = share(240–299) − share at the
merge; WIN needs |mean y′| ≥ 0.10; power at n 8 (BH worst q/36 / BH half q/2).

| rule | g0 | null y′ SD | WIN at edge 0.10 | WIN at edge 0.15 (= δ_i) | WIN at edge 0.40 | RESOLVING (n 8 / 16) | variance mutant: H-WIN / D-WIN (n 16) |
|---|---|---|---|---|---|---|---|
| **shuffle** (registered) | 0.5 | 0.149 | 1.00 / 1.00 | 1.00 / 1.00 | (composition-capped) | yes / yes | 0.00 / 1.00 |
| **shuffle** | 0.8 | 0.148 | 0.07 / 0.38 | 0.32 / 0.79 | 1.00 / 1.00 | no (0.77) / yes | 0.00 / 1.00 |
| **shuffle** | 1.0 | 0.145 | 0.01 / 0.10 | 0.03 / 0.21 | 0.52 / 0.95 | no / no | 0.00 / 1.00 |
| **shuffle** | 1.3 | 0.157 | 0.00 / 0.02 | 0.00 / 0.05 | 0.03 / 0.19 | no / no | 0.00 / 1.00 |
| energy | 0.5–1.3 | 0.18–0.19 | 1.00 | 1.00 | 1.00 | yes / yes (before the negatives) | **1.00** / 0.00: fails |
| leakx:0.3 (withdrawn) | 0.5–1.3 | 0.16–0.17 | 1.00 | 1.00 | 1.00 | yes / yes (before the negatives) | **1.00** / 0.00, and the 0.9× mean-loss mutant also H-WIN 1.00 at g0 ≥ 0.8: fails |

What this means for the design:
- **Under the registered shuffle the share layer resolves only in poor worlds** (g0 ≤ 0.8), and the prior arithmetic
  puts 0–2 Stage-1 points there (§6.2). Hence the M/N gate (§5.2), and a body map carried by the income and survival
  layers.
- **Energy order and leakx:0.3 resolve everywhere, but they read income variance as merit** (the variance mutant fixes).
  Neither is used. This reproduces RBT-126's screen in this replica.
- **Shuffle reads income variance as demerit** through the starvation sieve (the variance mutant is driven out).
  That is a real viability cost of variance, not a rule artefact, and §6.1's VARIANCE-DRIVEN flag keeps it from being
  read as a body win.
- **y′ removes the merge-composition confound.** With no body edge and one fauna short at the merge, the raw share gives
  a false D-WIN at 0.54–1.00 (k = 30 or 15 of 60) and y′ at 0.01–0.05, under every rule (`power.txt` §6a).
- **CONTINGENT against the pooled null** (df 108): false-fire rate 0.001–0.004. It fires at 0.93–1.00 under the
  energy-ordered rules at the replica's history spread (tau 0.1), and at 0.00–0.02 under shuffle, where that spread
  barely moves the share (`power.txt` §6b).
- **The share TIE** at ±0.10 is reachable under shuffle at a no-edge point (0.54–0.70 at n 16, BH half), but a TIE only
  counts at a RESOLVING point, and those are few.
- **T4 at the seed level in PW** (`power.txt` §6c): at a per-point per-seed SD of 0.14–0.23, power at Δ = 0.25 is
  0.66–0.99 at Holm's first step and 0.90–1.00 at its last (r1's point-level t: 0.00–0.19).
- The replica has fixed types (no evolution), a Poisson season, a fixed 0.1 work charge, and a variance mutant of
  3 × Poisson(m/3). The pilot's M and N arms measure the real drift SD, and the gate and the checks are rescaled by it
  (§4.1).

## 11. Budget, staging and order

### 11.1 Gates and order

1. **Gates (all required before Stage P):**
   - RBT-120 (motor budget) and RBT-124 (physics pack) merged;
   - RBT-128 (`--fair` and the guard) merged;
   - RBT-125 (smell channel with G registered, eating rules, **world gate passed on real bodies**) merged;
   - RBT-126 merged (`d1eb1ae`: the readout script, and the screen under which **the committed shuffle is registered**,
     coordinator 22:56). Its drift-arm fix `--breed-gate none` (#419) is **not** a gate: R_drift is optional and
     descriptive (r3, R2-M1); a `lcb:3` flag only if the descriptive arms are to run (optional);
   - RBT-118's registration has adopted the seed coordination at the anchors (§9.1), or the sweep's own anchor arms
     are budgeted;
   - RBT-129a merged, with its test list (§5.6);
   - RBT-116's `steer.py` committed at its ruled version;
   - **this design's adversary MUSTs ruled and re-checked** by the same adversary on r2 (coordinator note 2).

   RBT-127 (versions in `config.json`) is expected, not gating. RBT-129b (moving patches) is conditional and unbudgeted.
2. **Stage P** (pilot) and **Stage 0** (census) in parallel. Then `power.py` is re-run with the pilot's constants (§4.1),
   and the coordinator rules n for Stage 1.
3. **Stage 1.** Its provisional map is posted; R-A's pairs and R-B's Stage-1 list are computed by script and posted
   before any Stage-2 arm.
4. **Stage 2 (adversary M12):** 2a (R-A's points) and 2b for **Stage-1** points run side by side. 2b for **Stage-2a**
   points follows 2a, from what remains of the cap of 20. Then the final map, BH over all points, the verdicts of §8.
   This puts one more 240-season arm on the critical path (about 1 h).
5. **Stage 3.** RBT-118's fixed points and RBT-116's W1 may run any time after the gates (their worlds are fixed);
   their rule-chosen points wait for Stage 1.

### 11.2 CPU-hours (`prior_regime.txt`, r3 budget; `power.txt` §4 for the ungated version)

Per seed and point at 20 core-s per arm-season: S 1.67 + probes and levers **0.46–0.83** everywhere; M 1.33 behind the
gate; N 0.57 (half the seeds) only at census g0 ≤ 0.8. The changes since r1:
- M and N are **forked from S's season-59 checkpoint** (240 seasons each);
- **M is gated** at census g0 ≤ 1.0 (at most 12 Stage-1, 4 Stage-2a and 6 R-B points), and **N at census g0 ≤ 0.8**
  (at most 4, 2 and 2); the anchors' M and N come from RBT-118 (r3, R2-S1);
- probes are re-costed from RBT-116 §9: 0.46–0.83 core-h a seed, not 0.40;
- the planted set has ≥ 8 hosts a plant (M7d): 0.8 core-h a point;
- the pilot is 4 points (with `c2-p030-PW-G`), with N on all 4 seeds;
- the census has 18 PAYS cells, per fauna, under the sweep's block;
- **retention** (§6.4): R_sel and R_marker at ≤ 12 fauna-points × 8 seeds; readout validation and the erosion table
  (about 0.3 core-h a point); one matched-erosion re-read (both faunas, both arms) at one point;
- **optional:** R_drift as a descriptive floor (+160 core-h, only if `--breed-gate none` has merged); `lcb:3`
  descriptive M and N at the 3 anchors (+46, only if the flag exists).

| stage | at 20 core-s | at 25 core-s |
|---|---|---|
| P pilot (4 points × 4 seeds, N on all) | 77–83 | 93–99 |
| 0 census (150 × 3 seeds × 60 seasons, plus 18 PAYS cells) | 195 | 232 |
| 1 coarse map (36 points × 8 seeds; M at ≤ 12, N at ≤ 4) | 787–894 | 944–1,051 |
| R retention (R_sel + R_marker, ≤ 12 fauna-points; validation; matched-erosion re-read) | 377 | 470 |
| 2a refinement (≤ 16 points × 8; M at ≤ 4, N at ≤ 2) | ≤ 337–384 | ≤ 403–450 |
| 2b extension (≤ 20 points × 8 more; M at ≤ 6, N at ≤ 2) | ≤ 413–473 | ≤ 498–557 |
| **total, at most** | **2,186–2,405** | **2,641–2,860** |
| optional: R_drift; lcb:3 | +160; +46 | +200; +57 |

- Wall time on ten 4-core sessions (40 cores; the programme's usual ceiling of ≤ 10 at a time), packed two arms of
  *different seeds* per session at WORKERS = 2 (RBT-107's packing rule): **55–72 h** at most, the census and pilot about
  7 h of it. Ungated, with M and N at every point, the total would be 2,633–3,419 (`power.txt` §4). The demoted share
  layer's savings pay for the retention controls (R2-S1).
- **Sub-studies, not included:** RBT-116 about 420 core-h a point (840 for two); RBT-118 per its own design
  (about 300 a point at n = 20 and 1,200 seasons, so about 900–1,500 for three to five points).
- **A lean option** for the ruling: Stage 1 at n = 6 and R-B to n = 12, about 22% less, widening the income band by
  24–40% (`power.txt` §1: MDE80 0.205 against 0.165 at the BH-half threshold, 0.400 against 0.286 at the worst).
- **A full factorial** at n = 8 would cost 4,952–6,466 core-h with M and N everywhere (`power.txt` §4), before any
  extension.

## 12. Registered predictions (from the priors; "no" is a finding)

1. **Income layer.** On the pre-fairness arithmetic (`power.txt` §1), EARNS-D on flat ground at p ≤ 0.03, EARNS-H at
   c ≥ 1 for p ≥ 0.03, with the break-even rising as clutter falls. **Under the fairness set** the designed body's
   resting throttle is closed (`effector_bias_sigma`; its D line was 99% saturated), so its work bill is expected to
   fall more than the holistic one, and **the break-evens to rise**: M3's p* above 0.018 at c = 1 and above 0.053 at
   c = 0. T2 > 0 and T3 > 0.
2. **Share layer (under the registered shuffle).** SATURATED at most points, gated out at most (§5.2); RESOLVING at
   0–2 Stage-1 points, at p = 0.08 in PW (`prior_regime.txt`). Where it resolves, share calls follow the M arm's income
   sign (M6's κ > 0.5, one-world column), except where VARIANCE-DRIVEN.
3. **Habitability.** EXCLUDED-D or PARTIAL-H at some p = 0.08 points on c ≥ 1 (RBT-99's 3 of 10, before the fairness
   set, from a changed world rather than from founding). FOUNDING-FAIL for the holistic fauna in the census at the
   poorest points (RBT-100 founders6).
4. **Perception.** NONE at every U point and at every L point (R4). PERCEIVES, if anywhere, at PW-G and HP-G points,
   and first for the designed fauna, whose two noses are fixed at a useful spacing. PERCEIVES-H at no point is a live
   outcome, and it is not evidence against holistic bodies unless the point PAYS for the holistic fauna and its
   retention call (§6.4) is read beside it. At G points every negative here is "contrast-only perception" (§3.4).
5. **The framing.** EARNINGS DEPEND under the registered shuffle (the share layer mostly SATURATED), carried by clutter
   and price (as RBT-118 §4a found), with the layout acting mainly through habitability and perception, and survival
   calls for the holistic fauna at p = 0.08 (the designed fauna starving there).
6. **Retention.** HOLDS for the designed fauna at the retention points with census g0 ≲ 0.9, and UNDECIDED at richer
   ones unless the planted trait is worth ≳ 0.4 items (§6.4's power table); for the holistic fauna, open, and read
   across faunas only at matched erosion.

## 13. Open items

**r1's items, as the adversary answered them and r2 takes them:**
1. CONTINGENT's threshold: its own BH family, against a pooled per-kind null (M4; §6.1, §7.1).
2. LEVER's thresholds: replaced by between-fauna differences and "cap binding" (M6; §6.1).
3. Common seeds: the cross-point correlation is printed, with BY beside BH if its mean exceeds 0.3 (S9; §7.1).
4. The legacy-smell subset: 9 points suffice once T4 is seed-level in PW (M9; §7.3). Crossing with c = 0 (about 320
   core-h) stays optional.
5. The null on half the seeds: pooled per kind for CONTINGENT (M4); on all seeds at the pilot (S10; §4.1).
6. Fixed midpoints: accepted as they are.
7. The replica against the real drift: scaled by the pilot's point estimate of the ratio, not by a 1.5× trigger (S10).
8. PAYS on c = 2: measured, not borrowed (S8; §5.1).

**r2's items, as R2-CHECK answered them:** 1 (both bounds): yes. 2 (verdict 5's reading): right. 3 (LEVER margins):
not raised. 4 (y′ and the matched N): harmless. 5 (variance factor 3): acceptable. 6 (the gate's cap): superseded by
R2-S1. 7 (VARIANCE-DRIVEN): kept as a flag, not a verdict. 8 (retention's dependencies): answered by R_marker (R2-M1).

**New in r3, for the re-read:**
1. **The anchors from RBT-118** (§9.1) depend on RBT-118's registration adopting the seed coordination and the sweep's
   window. If it does not, the sweep's own anchor arms (46 core-h) are the fallback. Is a gate (§11.1) the right place
   for that dependency?
2. **R_marker's lesion** reads the transform's zero-information constant, as `steer.py`'s lesion condition does. At
   L points (no transform) the lesion reads the legacy sensor's zero. Retention is registered at G points only, so this
   matters only if an L point is ever added.
3. **VARIANCE-DRIVEN's two-predictor fit** at n 8 has 5 residual df. Its partial t statistics are noisy, and the flag
   will be conservative (a WIN keeps its call unless the SD term clearly dominates).
4. **MARGINAL** uses the living cost (0.25) as the per-birth bar. The per-birth income includes children that die
   young, so the bar is strict. Should it be half the living cost?
5. **CONTINGENT at df < 12 is not callable.** With N at 0–4 sweep points plus RBT-118's three anchors, it will be
   callable only if RBT-118 reports its anchor nulls at the sweep's window.

## 14. Files

| file | what |
|---|---|
| `DESIGN.md` | this document |
| `power.py` → `power.txt` | r2: income MDE and bands; the share replica on y′ by regime and rule (lottery, energy, leakx:0.3); RESOLVING tied to δ_i; the planted variance negatives (§7); the merge-composition check; CONTINGENT against the pooled null; T4 at seed level; the re-costed budget |
| `power.py 500 r3` → `power_r3.txt` | r3: `resolvable()` at both bounds under shuffle (S-1); CONTINGENT at the gated df (S-2) |
| `prior_regime.py` → `prior_regime.txt` | the Stage-1 points' expected regime and calls under the registered shuffle, from RBT-118's restores (two work-bill scenarios); the r3 budget |
| `design-adversary/` (PR #416) | the adversary's report and probes, which import `power.py`; r2 keeps r1's `merged_history`, `_season`, `_breed`, `INIT`, `AGE`, `Q` and `t_crit` interfaces so that they still run |

Reproduce: `python3 runs/RBT-129/power.py > runs/RBT-129/power.txt` (numpy only; about 20 minutes on 4 cores).
