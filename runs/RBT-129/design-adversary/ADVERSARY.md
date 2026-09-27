# RBT-129 design adversary: PR #412 (`runs/RBT-129/DESIGN.md`, `power.py` at `6b4d003`)

**Verdict: REGISTER AFTER FIXES.** The architecture holds: a full-factorial census, then an adaptive map;
the ecology at every point; S, M and N arms; the resolvability gate on TIE; sub-studies slotted by rule. The arithmetic
of `power.py` and §11 re-derives exactly. But three of the calls can be wrong in the way that matters, and one
registered test cannot pass in the world the design predicts:

- the share statistic reads the **merge-time head count** as a body win (M1), and partial extinction before the merge
  as a WIN (M2);
- a lottery point that becomes RESOLVING at n = 16 reads **TIE with a real edge** at the income layer's own margin
  (M3);
- R-A misses a **bracketed boundary** in up to 94% of cases (M5);
- **T4** has power 0.00–0.19 when the channel pays only in PW, as R4 and the gate predict (M9);
- the perception layer is **VOID by construction** wherever the world does not pay perception (M7).

Each of these has a text fix that keeps the grid, the budget and the stages. Nothing here needs a simulator run to
settle it; all probes are numpy, on the design's own replica.

Everything below is reproducible from this directory (`python3 <probe>.py > <probe>.txt`; the replica probes take
5–15 minutes each). `adv_replica.py` imports the design's `power.py` unchanged and adds one hook: how many of each
fauna are alive at the merge.

| probe | what it tests | § |
|---|---|---|
| `probe_merge.py` → `probe_merge.txt` | (a) merge-time composition, with no body edge; (b) partial extinction before the merge | M1, M2 |
| `probe_tie.py` → `probe_tie_lottery.txt`, `probe_tie_energy.txt` | the share TIE at RESOLVING points, with a true edge | M3 |
| `probe_null_checks.py` → `probe_null_checks.txt` | CONTINGENT's F test; K2 per point; the pilot's null SD | M4, S3, S10 |
| `probe_ra.py` → `probe_ra.txt` | R-A on the design's prior map | M5 |
| `probe_t4.py` → `probe_t4.txt` | T4's power, by where the channel pays | M9 |
| `probe_census.py` → `probe_census.txt` | 60-season against 300-season extinction | S1 |
| `probe_budget.py` → `probe_budget.txt` | §11's arithmetic; probes re-costed from RBT-116 §9; forking M and N | S12 |

## 1. Can each call be wrong in the way that matters?

### 1.1 The N arm is not a null for M's starting point (M1)

N merges a fauna with a copy of itself, so it **always starts at 1 : 1**. M starts at whatever the two ecologies
hold at season 59. Under the lottery, the pooled share is close to a martingale. With no body edge, it stays where
the merge put it.

`probe_merge.txt` (a): edge 0; the holistic fauna holds k of 60 at the merge; n = 8. A false WIN is counted with
the design's own 0.10 margin.

| rule, g0 | k = 60 | 45 | 30 | 15 |
|---|---|---|---|---|
| lottery 0.8: share at merge → share 240–299 | 0.50 → 0.52 | 0.43 → 0.42 | 0.33 → 0.34 | 0.20 → 0.18 |
| lottery 0.8: false D-WIN, q/2 / q/36 | 0.04 / 0.00 | 0.21 / 0.03 | **0.79 / 0.21** | **1.00 / 0.97** |
| lottery 1.3: false D-WIN, q/2 / q/36 | 0.03 / 0.00 | 0.13 / 0.01 | **0.72 / 0.24** | |
| energy 0.8 / 1.3: false D-WIN at k 15, q/2 / q/36 | | | 0.58 / 0.17 (0.8) | **0.95 / 0.59** (0.8), **0.97 / 0.71** (1.3) |
| **change statistic y′ = share − share at merge**, false WIN, q/2, every row | 0.01–0.05 | | | |

**When does this happen?** A slow founding refill leaves one fauna short at season 60. The holistic bottleneck falls
at season 11 and refills "within one lifespan" in the default world (RBT-118 §2). But:

- RBT-100's founders6 had **8–60 holistic and 2–7 designed alive at season 59** (RBT-118 prior §3);
- the design's own RESOLVING worlds are the poor ones (g0 ≤ 0.9: dear work, PW, dense clutter).

So the share layer is most likely to be read exactly where it is most likely to be confounded. In those worlds,
**habitability and founding luck become share WINs**. That is the "DEPENDS from habitability alone" route the brief
asks about.

**MUST 1.**
- Register y′_j = (share over 240–299) − (share at the merge, season 60), or the log-odds change, as the share
  statistic.
- Print both merge-time counts per seed.
- Give K2 the same statistic.
- Alternatively, make N match M's merge-time composition: subsample the copy to the replaced fauna's count. Then the
  null carries M's starting point.
- Either way, `power.py` §2 and §5 are re-run on the chosen statistic.

### 1.2 Partial pre-merge extinction becomes a WIN (M2)

EXCLUDED needs ≥ 5 of 8 extinct seeds in S by season 299. A fauna extinct before season 60 on j ≤ 4 seeds gives
M share 1 on those seeds (y = +0.5), since M is identical to S up to season 59.

`probe_merge.txt` (b), other seeds from the replica null; P(H-WIN) at q/2 / q/36:

| | j = 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| lottery 0.8 | 0.06 / 0.00 | 0.14 / 0.00 | **0.34** / 0.00 | **0.68** / 0.03 |
| energy 1.3 | 0.05 / 0.00 | 0.13 / 0.00 | **0.29** / 0.01 | **0.57** / 0.05 |

**Once a few WINs reject, BH's threshold moves toward q/2, so the q/2 column is the relevant one.** Such a point is a
survival result, not a head-to-head one. With RBT-99's pattern (designed extinct on 3 of 10 at 0.08/kJ), this is
the most likely source of H-WINs at dear-work points. With the flat-ground designed lead at cheap work, one sign
change is then enough for DEPENDS with no head-to-head behind it.

**MUST 2.**
- The share test uses only seeds on which **both faunas are alive at the merge**.
- A point with fewer than 6 such seeds (of 8; 12 of 16) takes a survival call, not a share call:
  - PARTIAL-X, reported in M1's survival count, and never a WIN.
- The same rule applies to income x_j: the seeds where a fauna is extinct in S before 240 are counted, not averaged.

### 1.3 A saturated lottery can pass RESOLVING and read TIE (M3)

RESOLVING asks for power ≥ 0.80 against an edge of **0.25 × g0** (`resolvable()`: 0.20 at g0 0.8, 0.25 at 1.0). That
is 1.3–1.7× δ_i = 0.15, the income layer's own TIE margin. So RESOLVING does not certify that a share TIE excludes an
edge the income layer would call non-equivalent.

**The failure goes through R-B.** A lottery point at g0 = 1.0 is SATURATED at n = 8 (0.64) but RESOLVING at n = 16
(0.96).

`probe_tie_lottery.txt`, g0 1.0, n 16, TIE (TOST ±0.10) at q/2 / q:

| true income edge | 0 | **0.10** (RBT-121 B's selection threshold) | **0.15** (= δ_i) | 0.20 | 0.25 |
|---|---|---|---|---|---|
| P(share TIE) | 0.64 / 0.82 | **0.41 / 0.60** | **0.22 / 0.36** | 0.03 / 0.07 | 0.01 / 0.03 |
| P(H-WIN) at q/2 | 0.01 | 0.16 | 0.36 | 0.75 | 0.90 |

At g0 0.9 (RESOLVING at n 8 and 16), an edge of 0.10 reads TIE at 0.05–0.15 (n 8) and 0.17–0.28 (n 16). At g0 0.8,
TIE is safe (≤ 0.05). **Under energy order, a TIE with an edge ≥ 0.10 is 0.00 everywhere** (`probe_tie_energy.txt`),
because the edge fixes the share.

So "TIE (share, RESOLVING)" at a lottery point with g0 ≈ 0.9–1.1 means "the income edge is below about 0.2 items a
season", not "the bodies are equal". WORLD-INVARIANT counts it at face value.

**MUST 3.** Tie RESOLVING to the TIE margin. A point is RESOLVING for TIE only when the replica, at its g0, its rule
and its n, gives:

- P(share TIE | income edge = δ_i = 0.15) ≤ 0.05; and
- power ≥ 0.80 to call the WIN at δ_i, at the threshold actually used (see S4).

Otherwise the no-difference result is SATURATED.

Also:
- `resolvable()` must implement **the ruled breeding rule**. RBT-126 may rule `energy_leak` or tickets, which the
  replica does not have.
- g0 enters as an estimate. Take the lower 90% bound of g0 over seeds for the lottery (the conservative side), not
  the mean.
- `resolvable()` must use more replica seeds than 300: at g0 0.9 its value (0.88) sits near the 0.80 bar.

### 1.4 CONTINGENT at n = 8 is inert, and it blocks R-B (M4)

- N runs on half the seeds, so at n = 8 the null has 4 seeds (2 of each kind), and the F test is F(0.99; 7, 3) = 27.9.
- CONTINGENT fires with probability 0.03–0.20 even at the replica's largest history-to-history spread (share SD 0.46
  against 0.149).
- At n = 16 it is 6.3, and CONTINGENT fires at 0.08–0.76 (`probe_null_checks.txt` §1).
- If the holistic-copy and designed-copy nulls centre differently (offset 0.2), the null's variance is inflated, and
  the n = 16 rate falls from 0.52 to 0.27.

And a point called CONTINGENT at Stage 1 is **not UNDECIDED, so R-B never extends it**. Its call is then frozen at a
test with df (7, 3). **CONTINGENT absorbs underpowered WINs**, which is exactly the tau = 0.1 case the design names as
its main threat (§10.1: WIN power 0.28–0.39 worst at n 8).

**MUST 4.**
- (a) Compute var(y_null) per kind, pooled over the stage's points (df ≈ 2 × 36 × 1, not 3), with the kind offset
  removed. The point's own null serves only for K2.
- (b) R-B's eligible set is UNDECIDED ∪ CONTINGENT (n = 8).
- (c) Answering open item 1: CONTINGENT enters its own BH family (the F tests), at q = 0.10.

### 1.5 Does LEVER absorb results that should be called? (M6)

Yes, asymmetrically.

- `--fair` carries RBT-120's motor budget, **a Σgear/(4M) cap at 1.77**. The Pioneer sits at 1.7605, just under it,
  by construction (RBT-120 PREREGISTRATION: "the designed side re-runs RBT-113 exactly").
- LEVER flags "Σgear/(4M) **at the cap** on more than half" of the **winning** fauna's members.
- So a holistic fauna that evolves to the **same** motor class as the Pioneer marks every H-WIN as LEVER. The
  Pioneer at 1.76 never trips it.
- R8 attributes a result to a lever *difference* ("a fauna difference that goes with a lever difference"), not to a
  level the fairness set allows.
- LEVER is also read only on the winner, so a win against a fauna exploiting a lever is never examined.

**MUST 6.**
- LEVER is defined on the **difference** between faunas: the winner's median exceeds the loser's by a registered
  margin on a lever that R1–R3 do not already budget.
- "At the cap" is dropped as a flag, and replaced by "cap binding": the share of members the budget had to scale, as
  RBT-120's `motor_report.py` prints it.
- Printed for both faunas at every point.

Open item 2 answered: the other thresholds (resting drive 0.9, contact-free work 0.25, motors-off 0.25 m) are
absolute levels too. Under `--fair` they should all be near 0, so a difference margin is both tighter and fairer.

### 1.6 The S arm and the shared world

- S never shares a world with M or N after season 59. Before that, all three are byte-identical (K1; N copies at 60).
- In S the two faunas share the terrain and start seeds (`ecology.py`: one terrain stream), but not arenas or food.
  So x_j is side by side, as RBT-118 §0 requires ("two separate populations compared, not a contest"). This is
  sound, provided every income claim says so, which §6.1 does.
- The M arm's interference measure (merged income − S income) is the only shared-world income. It is printed, not
  called.

This is acceptable, but **SHOULD 5**: M6's κ between share sign and S-income sign is not a test of the head-to-head,
because the two arms differ in the world as well as in contact. Add the M arm's per-fauna income (seasons 240–299,
shared arenas) as a second income column, so that a share result and an income result in *one* world can be set
side
by side.

### 1.7 `--merge-null` as specified cannot give an independent null (M8)

`ecology.py` keys mate choice (`mates = … kind == kind`, line 531), the breeding stream (`self.rngs[kind]`, line 591)
and the persistent arena bank (`_arena_bank(key)`) on `kind`. A copy of the holistic population that is still
`kind = holistic`:

- interbreeds with the original (crossover rate 0.3);
- draws its children's mutations from the same stream;
- and its share has no identity.

**MUST 8** (for RBT-129a's ticket).
- B is a separate **label** with:
  - its own mate pool;
  - its own stream (an independent `SeedSequence` child, as `breed_seed_sequence` does);
  - its own lineage names;
  - the body model of KIND.
- Tests:
  - a B child never has an A parent;
  - B's draws are independent of A's;
  - with `--merge-null` off, the run is byte-identical.
- State what happens to the persistent arena bank at the merge. The merged cohort gets a fresh bank keyed on the
  cohort's kinds, i.e. full arenas at season 60 in PW. M and N should see the same transient, and a test should show
  they do.

## 2. Do the verdicts follow from the tests?

### 2.1 R-A misses the boundaries it exists to find (M5)

R-A refines a pair only when both calls are *decided and different*. A point near a boundary is UNDECIDED by
construction: its |H − D| is below the MDE. So a row that crosses zero usually reads (D-call, UNDECIDED, H-call), and
**no adjacent pair differs**.

`probe_ra.txt`: the design's own prior map, n 8, q/2, the income-layer fallback. Every coarse pair whose true effects
differ in sign:

| dkJ (fairness scenario) | pair | P(R-A refines) | P(refines under "estimates differ in sign, or decided calls differ") |
|---|---|---|---|
| 14.7 | c0, 0.03–0.08 | 0.55 | 1.00 |
| 14.7 | c1, 0.01–0.03 | 0.63 | 0.96 |
| 10 | **c0, 0.03–0.08** | **0.06** | 0.64 |
| 10 | c1, 0.01–0.03 | 0.29 | 0.97 |
| 6 | c0/c1 at 0.08 (clutter) | 0.53 | 0.99 |

And the pattern (D, UNDECIDED, H) along a price row occurs on 12–30% of rows, where R-A adds nothing.

**MUST 5.**
- R-A flags a pair when the two **point estimates differ in sign**, or their decided calls differ; UNDECIDED
  counts.
- Rank by |t₁ − t₂| (unit-free; the current ranking mixes share and income units), smell G first.
- R-A must also say which layer's estimates it uses at each pair:
  - the share layer where both points are RESOLVING;
  - otherwise income.
- C1's non-monotone rows need a named pair: the pair flanking each extra sign change.

### 2.2 DEPENDS and its rivals

- **DEPENDS can fire from habitability alone** through M1 and M2 (share WINs from composition and partial
  extinction). With MUST 1–2 it cannot.
- **Can it fire from terrain × price confounds (the wheel-tax lesson)?** DEPENDS needs opposite-sign WINs, and the
  record predicts them from terrain and price together: D on flat cheap ground, H on cluttered dear ground. That *is*
  world dependence, and M2's coefficients attribute it.
  - **The risk is attribution, not the verdict.** On the coarse grid c and log p are orthogonal. But R-A's points are
    placed on the boundary, which runs diagonally in (c, p). Refinement points are therefore collinear in (c, log p),
    and they carry the most weight in a WLS fit.
  - **SHOULD 6:** fit M2 on the Stage-1 grid alone as the registered T2/T3 model (orthogonal, not chosen from the
    data), with the refinement points in a stated sensitivity fit.
- **T1 is confounded by the regime.** With a *constant* income edge everywhere, the share still varies with the world:
  at edge 0.10, the share is 0.94 at g0 0.5, 0.61 at 0.8 and 0.515 at 1.3 (`power.txt` §2). So T1 rejects because
  selection strength varies, not because the ranking does.
  - DEPENDS is protected by its opposite-sign requirement, but a T1 rejection alone must not be read as "the bodies
    depend on the world".
  - **SHOULD 7:** add the measured g0 (the regime) to M2 as a covariate, so the world terms are net of selection
    strength; or run T1 on income, and report the share version beside it.
- **WLS weights are infinite at fixation.** Under energy order, the per-seed share SD is 0.000–0.002 at edges ≥ 0.1
  (`power.txt` §2). So 1/SE² is unbounded, and one point decides M2.
  - **MUST 10:** fit the share model on the logit of the (clipped) share, or at the seed level with a seed random
    effect.
  - Estimate a dispersion term (a random-effects meta-regression), so T2/T3 are not anti-conservative when the fit
    omits L × p or L × c.
- **The verdicts overlap, and the falsifying ones are unreachable** (MUST 11).
  - A map with H-WIN at every decided point and EXCLUDED-D elsewhere satisfies both ONE BODY DOMINATES (H) and
    DEPENDS ONLY THROUGH HABITABILITY. Register a precedence order.
  - DEPENDS ONLY THROUGH HABITABILITY: "the only calls that differ are EXCLUDED ones" is undecidable when most calls
    are SATURATED or UNDECIDED. Define it over **decided** calls only: every decided share call (or, under the
    EARNINGS fallback, every decided income call) has one sign, and at least one EXCLUDED point exists for the
    losing fauna.
  - **Asymmetry.** DEPENDS has an income fallback (EARNINGS DEPEND) when the share layer is SATURATED. ONE BODY
    DOMINATES has none, and needs a third of habitable points decided *on share*. Under the lottery, `power.txt`
    predicts SATURATED at most points. So the confirming verdict is reachable and the falsifying one is not.
    - Add **EARNINGS DOMINATED (X)**, parallel to EARNINGS DEPEND.
  - WORLD-INVARIANT needs TIE at half the points. That is unreachable at the noise ceiling (EARNS-TIE 0.02 at n 8,
    §10), and a single spurious EARNS call among 52 points kills it.
    - Allow it at ≥ half the *resolving* points.
    - Replace "no WIN or EARNS call at all" with "no pair of opposite-sign calls, and T1 not rejected".
  - "No single world is the headline" (the plan): fine as written.

### 2.3 The Holm family and adaptivity

- Holm over T1–T4 is valid under any dependence. The family is right, and T2 and T3 being nested in T1 is not a
  problem for Holm.
- Adaptivity touches the *data* T1–T3 are computed on, not the family:
  - R-A chooses design points from Stage-1 outcomes. Under the null of no world terms, the new points' outcomes are
    independent of that choice, up to the common seeds. So the size holds, approximately.
  - R-B extends points *because* |z₁| was small. Their final 16-seed means are biased toward 0, and their SEs halve,
    so WLS gives them the most weight. The inverse-normal combination fixes the p-values, not the estimates.
  - SHOULD 6 (Stage-1 grid for T2/T3), with the bias-adjusted (median-unbiased) estimate at extended points in the
    sensitivity fit, answers both.
- **T1's switch rule** ("if SATURATED at more than half the points, run T1 on income") is data-dependent: it picks
  the test after seeing the calls. **SHOULD 8:** register T1 on income as primary, and share as secondary (outside
  Holm), or choose by the pilot before Stage 1.
- **BH over common seeds** (open item 3). The common seeds induce positive dependence among one-sided statistics
  (PRDS), for which BH holds. For two-sided tests with sign calls, PRDS is not guaranteed.
  - After 240 seasons of different worlds, the cross-point correlation is probably small. It is measurable: correlate
    the seed-level y across Stage-1 points.
  - **SHOULD 9:** print that correlation matrix's mean and max. If the mean exceeds 0.3, report BY-adjusted calls
    beside BH.

### 2.4 Sequencing: R-B uses Stage-2a results, but 2a and 2b run "in parallel" (MUST 12)

- §4.2 R-B extends "every Stage-1 **or Stage-2a** point whose body call is UNDECIDED".
- §11.1 step 3 says R-B is "computed by script and posted before any Stage-2 arm", and step 4 runs 2a and 2b in
  parallel.
- Those cannot all hold. **Fix:** 2b for Stage-1 points runs beside 2a. 2b for 2a points follows 2a, drawn from the
  same cap of 20, with the Stage-1 extensions ranked first. Register that order.
- Wall time barely moves (one more 300-season arm on the critical path, about 1 h; `probe_budget.txt` §4).

## 3. Axes and levels

- **Terrain as an axis (R10: "a primary factor, not a robustness arm").** Met: c = 0 is flat, and c ∈ {1, 2} are
  random, on the coarse grid at every price and layout. The plan's "flat, and 2–3 clutter densities" is honoured.
  - **SHOULD 2:** c = 0 → 0.5 is a change of kind (no obstacles, versus some), not only of density. So the
    monotone-bisection premise is weakest on that segment. The census's C1 covers it only at 60 seasons (see S1).
    State that a 0 → 0.5 non-monotonicity is expected possible, and let C1 route it to R-A.
- **Density is not equal across layouts** (§3.1 claims it is).
  - `world.random_terrain` rejects positions within 0.6 m + footprint/2 of each spawn (`keep_clear`), with at most 50
    × N tries. With 4 spawns, that excludes about 5.6 m² of free area:
    - 26% of the 3 m layouts' 2.6 m disc (21.2 m²);
    - 14% of PW's 3.6 m disc (40.7 m²).
  - At equal N/area, the obstacle density on the free ground is therefore about 15% lower in PW. At c = 2 in the 3 m
    layouts (28 obstacles on 15.6 m² free), the 50N-try cap may also bind.
  - **SHOULD 3:** RBT-129a's `--obstacle-radius` ticket prints the realised obstacle count and free-ground density per
    level and layout, over 100 terrain seeds, and sets N from free area.
- **Clutter also taxes food, not only mobility.** Items are placed with no regard to obstacles, so at c = 2 some sit
  under boxes. In PW, persistent items stay under a new terrain for a season. That is part of "the world", but it
  changes the reading of T2 (a wheel tax).
  - **SHOULD 4:** print the share of items unreachable (inside an obstacle's footprint) per clutter level, and each
    fauna's food per new cell.
- **The price grid** is sound: a log bisection, bracketing both pre-fairness break-evens widely. Open item 6 (a
  boundary below 0.018 stays bracketed) is acceptable for a registered first map.
- **The census cannot classify habitability** (S1).
  - `probe_census.txt`, one fauna at fixed income g:
    - at g 0.30: **100%** of seeds extinct by 299, **1%** by 59;
    - census EXCLUDED 0.00 against Stage 1's 1.00.
  - The committed record agrees: every post-onset extinction came 67–146 seasons after the change of world (RBT-118
    prior §3).
  - A 60-season census sees the founding runway, not viability. The census's EXCLUDED is therefore "extinct within
    one lifespan", and **SHOULD 1** names it so (FOUNDING-FAIL). Its only uses are:
    - the living-cost fallback;
    - C1's rows;
    - the 114 points never run at Stage 1, whose habitability the map must not report as "habitable".
  - Report the census regime (net ÷ living cost, seasons 30–59) as the habitability proxy at those points, with its
    60-season limit stated.
  - Three seeds at ≥ 2 of 3 is a coin toss at a per-seed rate of 0.5. Acceptable only for a flagged, provisional
    layer.
- **Living-cost fallback.** The rule c_L = 0.25 ḡ_L/ḡ_U is registered in advance. That is good. But it changes the
  world *after* seeing the census, for a whole layout.
  - State that such a layout's points are compared with other layouts only in M2 with a layout × fallback term, not
    pooled into T1.

## 4. Perception

### 4.1 PERCEIVES is not instrumented at non-paying points (M7)

K3 requires RBT-116's G8(a) and (c) to pass at the point.
- **G8(a)** is the Pioneer compass "at **the first paying rung**", which RBT-116 defines through G1: some rung with a
  lower bound on F > 0.
- **STEERS** itself requires F ≥ F_MIN = 0.25 (RBT-116 §1.3, condition 1).

In a world that does not pay perception (U by R4, every L point, probably HP), there is no first paying rung. A planted
steerer cannot reach F ≥ 0.25, so G8(a) and (c) cannot pass, and **K3 VOIDs the point by construction**.

The design predicts NONE at every U and L point (§12.4) and reads "not PAYS, and NONE" as a cell of §6.3. **Both are
unreadable**: those points are VOID.

Worse, NOWHERE IN THE SWEPT WORLDS needs only "no PERCEIVES call", and VOID points contribute none. So the
falsifying verdict can be reached on a map that is mostly VOID.

**MUST 7.**
- (a) For K3, plant at a **fixed registered rung** (a = 6, the gate's), and pass K3 on the instrument's
  *behavioural* legs:
  - the trajectory veto;
  - ΔT > 0;
  - SMELL-USE-or-STEERS.

  Keep F ≥ F_MIN for the PERCEIVES call only. At a non-paying point, a planted steerer that reads SMELL-USE shows
  the instrument can see steering, and that the world does not pay it.
- (b) G8(b) (the paying kinesis plant) is uninformative where kinesis cannot reach F ≥ 0.25. State, per point, that
  "T's discrimination is untested here", as RBT-116 does.
- (c) NOWHERE requires the perception layer to be valid (not VOID) at ≥ 2/3 of the PAYS points, per fauna.
- (d) Size K3: 4 hosts per plant gives pass rates in steps of 0.25. At a true sensitivity of 0.5, 0 of 4 pass with
  probability 0.06. RBT-116's bar for (a) is 0.6 × c_G1, and the sweep has no G1. Register the sweep's own bars and
  host numbers (≥ 8 per plant), with their false-VOID rate at the replica's sensitivities.

### 4.2 R10: K4 is mostly a control that cannot fail (S7)

- G8(d) (sensorless tumblers) and G8(e) (unwired noses), and the motors-off body, give intact and decoy trajectories
  that are identical by construction. So "no STEERS" and "intact − decoy CI covers 0" hold exactly.
- Only G8(b) can fail, and (§4.1) only where kinesis pays.
- **SHOULD 7b:** say so in §5.5. Add the arm's own **founders** at the n in use (R10's third clause) as the operative
  negative. K5 already probes 20 × 8 per fauna.
- PERCEIVES' false-STEERS rate must come from the founders (a G4-style confirmed rate, with its exact bound). It
  should not be pooled with the structurally-zero plants, which bias the rate toward 0 and make PERCEIVES easier.

### 4.3 PAYS is measured on one body and one eating rule (S8)

- The census's 12 R4 cells use RBT-125's harness. §A runs on RBT-90 **Pioneer** bodies; §B runs on RBT-113
  **designed** U-line hosts. Both run **under the committed eating rule** ("Everything below uses the committed eating
  rule", REGISTRATION.md).
- The sweep runs RBT-125's *ruled* rule (candidate `eat_from root`) under `--fair`.
- So PAYS is:
  - (i) a designed-body margin, applied to the holistic fauna's PERCEIVES-H reading (§12.4: "not evidence against
    holistic bodies unless the point is … PAYS");
  - (ii) measured under a rule the sweep does not use.
- **SHOULD 8b:**
  - run the 12 cells under the sweep's block (`--fair`, the ruled eating rule);
  - add a holistic PAYS: the G8(c) tuned plant's F at a = 6 on 8 hosts;
  - PAYS per fauna.
  - Open item 8 (c = 2 borrows c = 1): acceptable if marked. Adding c = 2 costs 6 more cells (about 12 core-h).

### 4.4 What the missing level channel limits (S9)

RBT-125's channel is tanh(G(ln S − b)) with a running baseline (τ = 2 s). It reads change, not level: "It drops only
'rich, and not changing'" (RBT-125 DESIGN §1). Consequences for this design:

- **The smell axis is a swap, not an addition.** At `L`, a nose reads the level S/(1+S). At `G`, it reads the
  contrast, and the level is gone (G = 0 is the legacy level).
  - T4's G − L is therefore "contrast instead of level", not "the channel's value".
  - A body that uses the level for area-restricted search (stay where it is rich) can lose at G. A negative G − L at
    HP is interpretable only this way.
  - State it in T4's sentence and M5.
- **Every lone nose becomes a free temporal-gradient detector at G.** Klinokinesis is then cheap for any holistic
  body with one wired food sensor, and STEERS counts it (RBT-116 SHOULD 3).
  - PERCEIVES-H at G points is therefore more reachable than at L for a reason unrelated to body plan. Report
    PERCEIVES by route (one nose against two, from `wiring.txt`-style readouts), as RBT-116 §6.4 does.
- **At rest in a static field, the channel reads 0.** A sit-and-wait strategy in PW's regrowing patches cannot be
  perceived.
  - The perception map is silent on it. Register the sentence: "the sweep cannot detect level-based strategies at G
    points".
  - RBT-125 anticipates the fix (`food_level`, a flagged source) if the sweep finds that the loss matters. The
    design should name its trigger:
    - SMELL-USE or PERCEIVES at L points that vanish at the matched G points, on ≥ 2 of 3 layouts, opens that
      ticket.

### 4.5 T4 cannot pass in the world the design predicts (M9)

T4 is a one-sample t over 9 point values, 3 of each of U, HP and PW at c = 1. R4, the gate (PW cells only) and §12.4
all predict the channel pays in PW, perhaps in HP, and not in U. An effect concentrated in 3 of the 9 points
inflates the between-point SD, and the t collapses.

`probe_t4.txt` (the design's perception noise, n 8), power at Holm's first step / last step:

| where the channel pays | Δ = 0.10 | 0.25 | 0.40 | seed-level test inside the paying layouts, Δ 0.25 |
|---|---|---|---|---|
| **PW only** | 0.04 / 0.16 | **0.01 / 0.19** | **0.00 / 0.14** | 1.00 / 1.00 |
| PW + HP | 0.34 / 0.69 | 0.80 / 1.00 | 0.95 / 1.00 | 1.00 / 1.00 |
| all 9 | 0.97 / 1.00 | 1.00 | 1.00 | 1.00 |

A larger effect in PW makes T4 *less* likely to reject.

**MUST 9.**
- T4 is a seed-level test of (f_G − f_L) averaged over the PW points (the layout the gate certifies), with HP in a
  second, stated contrast.
- Or: a mixed model with layout × smell, and T4 = the PW contrast.
- Open item 4 (cross with c = 0): not needed for power once T4 is seed-level. Adding c = 0's 9 L points would cost
  about 320 core-h for a robustness claim; it is optional.

## 5. Budget and gates

### 5.1 Arithmetic

**Every figure in §11.2 re-derives** (`probe_budget.txt` §1):
- 4.44 core-h a seed-point;
- P 54, 0 174, 1 1,288, 2a 573, 2b 711;
- **2,799** at 20 core-s and **3,431** at 25;
- 70 and 86 h on 40 cores.

The lean option and the full factorial match `power.txt`.

**Under-costed items (SHOULD 12).**
- **Probes.** 0.40 core-h a seed against **0.46–0.83**, re-costed from RBT-116 §9's own figure:
  - 0.35 CPU-s per solo season;
  - a staged battery with 75–100% of members reaching stage 2, since every Pioneer does under the trajectory screen;
  - 80 members a seed (20 × 2 faunas × 2 time points);
  - the low end if the intact − decoy battery reuses STEERS' 16 stage-2 draws, which it should.
- **The planted set.** 0.25 core-h a point against about **0.6–0.8**. This covers G8(b)/(c)/(f)'s tuning grids, the
  battery on about 49 bodies, the 64-draw reachability screen, and a rung scan if (a) keeps "first paying rung".
- **The pilot has no c = 2 point**, so 25 core-s is not bounded above for the densest terrain. 54 obstacles in PW's
  disc means more contacts than the 14 RBT-105 was costed on. Add `c2-p030-PW-G` to Stage P (+18 core-h); it also
  gives C3's rest check a real-body run.

**Savings available.** M and N are byte-identical to S up to season 59 (K1 enforces it). Fork them from S's season-59
checkpoint instead of re-running 0–59: −0.47 core-h a seed at 20 core-s, about −280 core-h in all.

**Net** (`probe_budget.txt` §3): 2,592–3,773 core-h, against the stated 2,799–3,431. The ceiling moves by +10% at
most. No budget verdict changes.

### 5.2 Gates and order

- §11.1's gates are complete for the sweep proper:
  - RBT-120 + 124 → 128;
  - RBT-125 with the gate passed;
  - RBT-126's readout and rule;
  - RBT-129a;
  - `steer.py` at its ruled version.
- Missing:
  - **RBT-129a's test list** (MUST 8);
  - **the ruling of this adversary's MUSTs** before Stage P, since the pilot re-runs `power.py`, and `power.py` must
    carry the revised statistic (y′), RESOLVING (MUST 3) and T4 (MUST 9);
  - **the moving-patch ticket RBT-129b** is correctly conditional and unbudgeted.
- **The order is right** (gates → P + 0 → re-run → 1 → 2a/2b → final), with MUST 12's fix to 2a/2b.
- **Pilot constants (S10).** The pilot's 3 points × 2 null seeds give 6 null runs (df 5).
  - The 90% range of the sample-to-true SD ratio is 0.48–1.49.
  - A true 1.5× discrepancy is detected by "> 1.5" only 42% of the time (`probe_null_checks.txt` §3).
  - Run N on all 4 pilot seeds (12 runs, df 11): +8 core-h. Scale by the point estimate, not by a 1.5× trigger.
- **"n = 12 or fewer points"** (§4.1) contradicts "the grid may not change". Register which: fewer points means
  dropping named ones (e.g. the 9 L points first).

## 6. K2 at a single point VOIDs by chance (S3, and part of MUST 1)

K2 per point fails when the null's mean B-share is off 0.5 by more than 0.15. The null has 4 seeds at n = 8
(`probe_null_checks.txt` §2):

| null SD | P(VOID) per point | expected VOID of 36 | P(≥ 1 of 36) |
|---|---|---|---|
| 0.149 (lottery) | 0.045 | 1.6 | 0.81 |
| **0.199 (energy, the rule §10.1 argues for)** | **0.13** | **4.8** | 0.99 |
| 0.25 (real drift 1.25–1.7× the replica's) | 0.23 | 8.3 | 1.00 |

Under energy order, about one point in eight loses its share call to noise in its own null. **SHOULD 3:** per-point K2
is a test (BH over points, the null's t at q = 0.10) together with the 0.15 size bar, not the size bar alone. Pooled
K2 stays as registered.

## 7. R1–R12, point by point

| rule | met? | note |
|---|---|---|
| R1, R2, R3, R9 | yes | `--fair` everywhere, with the guard. C3 repeats R3 on c = 2; run it at the pilot too (§5.1) |
| R4 | partly | the gate reads PW only; PAYS elsewhere comes from a designed-body margin under the committed eating rule (S8) |
| R5 | partly | regime stated everywhere, and the TIE gate is a real advance. RESOLVING must match the TIE margin (MUST 3) and the ruled rule's replica |
| R6 | yes | defaults stated |
| R7 | **no, as written** | planted positives cannot pass at non-paying points, so those points are VOID (MUST 7); "items per new cell" is recorded by `steer.py` but not in §5.3's outcome list (add it) |
| R8 | partly | LEVER is on absolute levels and the winner only (MUST 6) |
| R10 | partly | N is not M's null for composition (MUST 1); K4's negatives cannot fail (S7); terrain is an axis (met) |
| R11 | yes, with M3 | floors and ceilings throughout; the share layer's model is a replica, so the pilot must re-fit it (S10) |
| R12 | yes | world blocks written before season 0; RBT-127 expected |

## 8. The list

### MUST (before registration)

1. **Share statistic net of the merge:** y′ = share(240–299) − share(60), or N matched to M's merge-time
   composition. Re-run `power.py` §2/§5 on it. (§1.1)
2. **Seeds with a fauna extinct before the merge leave the share test.** A point with < 6 of 8 (12 of 16) valid seeds
   takes a survival call (PARTIAL-X), never a WIN. (§1.2)
3. **RESOLVING tied to the TIE margin:** P(TIE | edge δ_i) ≤ 0.05 and power ≥ 0.80 at δ_i, at the threshold used,
   under the ruled rule, with g0's lower bound and more replica seeds. (§1.3)
4. **CONTINGENT:** pooled per-kind null variance; UNDECIDED ∪ CONTINGENT eligible for R-B; its own BH family. (§1.4)
5. **R-A on estimate signs,** not only on differing decided calls; unit-free ranking; a named layer per pair. (§2.1)
6. **LEVER on between-fauna differences,** "cap binding" not "at the cap"; both faunas printed. (§1.5)
7. **Perception controls valid at non-paying points:** K3 at a fixed rung on the behavioural legs; host numbers and
   bars sized; NOWHERE requires a valid layer at ≥ 2/3 of PAYS points. (§4.1)
8. **RBT-129a's `--merge-null`:** B is a separate label with its own mate pool and stream; the listed tests;
   the arena-bank transient stated. (§1.7)
9. **T4 at the seed level in PW** (HP a second contrast), not a t over 9 heterogeneous points. (§4.5)
10. **M2 on logit share or at the seed level,** with a dispersion term; no unbounded 1/SE² weights. (§2.2)
11. **Verdicts:** a precedence order; DEPENDS ONLY THROUGH HABITABILITY defined over decided calls; EARNINGS
    DOMINATED (X) added; WORLD-INVARIANT made reachable. (§2.2)
12. **2a/2b order:** R-B on Stage-1 points beside 2a; R-B on 2a points after it, inside the cap of 20. (§2.4)

### SHOULD

1. Rename the census's EXCLUDED as FOUNDING-FAIL (60 seasons cannot see viability; `probe_census.txt`); report the
   census regime at unrun points. (§3)
2. State that c 0 → 0.5 is a change of kind; C1 routes it. (§3)
3. Realised free-ground obstacle density per level and layout; per-point K2 as a test. (§3, §6)
4. Items unreachable under obstacles, and food per new cell, per clutter level. (§3)
5. M-arm income per fauna as a second income column. (§1.6)
6. T2/T3 on the Stage-1 grid; refinement and extension in a sensitivity fit. (§2.2, §2.3)
7. g0 as a covariate in M2 (T1 net of selection strength). K4: the founders as the operative negative, and the
   false-STEERS rate from founders only. (§2.2, §4.2)
8. T1 on income as primary, share secondary. PAYS per fauna, under the sweep's block. (§2.3, §4.3)
9. Print the cross-point seed correlation; BY beside BH if its mean exceeds 0.3. The level-channel sentences and the
   `food_level` trigger. (§2.3, §4.4)
10. N on all pilot seeds; scale by the estimate. (§5.2)
11. Resolve "n = 12 or fewer points". (§5.2)
12. Re-cost probes (0.46–0.83 core-h a seed) and plants (0.6–0.8 a point); add a c = 2 PW point to the pilot; fork M
    and N from S at 59. (§5.1)

### Open items (§13), answered

1. CONTINGENT enters its own BH family: MUST 4.
2. LEVER thresholds: replace them with differences: MUST 6.
3. Common seeds: BH is probably fine. Measure it: SHOULD 9.
4. The L subset: 9 points are enough once T4 is seed-level: MUST 9.
5. The null on half the seeds: it moves CONTINGENT's df to 3. Pool per kind: MUST 4. Pilot on all seeds: SHOULD 10.
6. Fixed midpoints: acceptable.
7. The replica against the real drift: 6 pilot runs cannot detect 1.5×: SHOULD 10.
8. PAYS on c = 2: acceptable if marked; +12 core-h to measure it.

## Limits of this review

- Every quantitative probe uses the design's own replica (fixed types, Poisson income, fixed work charge), or normal
  approximations from its SDs. They show that the rules *can* fail at plausible parameters, not how often they will
  in the simulator. The pilot is where that is measured.
- The merge-time composition scenario (M1) assumes a fauna short at season 60. How often that happens under `--fair`
  is unmeasured. RBT-100 founders6 shows it happens in poor worlds, and the census's founder solvency will show where.
- RBT-116's G8/STEERS text is read at PR #400 `8d98da8` (r7). RBT-125's at PR #414 `c40ecd5`. Rulings after those
  heads are not reflected.

---
_Generated by [Claude Code](https://claude.ai/code)_
