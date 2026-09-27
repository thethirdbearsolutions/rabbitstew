# RBT-129 r2 check: PR #412 at `215494c`, against ADVERSARY.md (`3407f98`)

**Verdict: REGISTER AFTER FIXES.**

- **All 12 MUSTs from the first review are closed in substance.** The item-by-item check is in §1.
- **Three new MUST items (R2-M1 to R2-M3) come from r2's own changes.** They are:
  - the retention layer as designed;
  - the regime covariate in the income model;
  - the confirming verdict's single-call trigger.

  Each is a text or arm-assignment fix within the r2 budget.
- **On the share layer** (§2), plainly: under the registered shuffle it is **no longer worth its compute as a
  map layer**. It should stay as a small, descriptive one-world column, not as the head of the verdict order.
- The income layer can carry the map's verdicts honestly once R2-M2 and R2-M3 are fixed.
- The retention layer is **not** unbounded by the saturated band, as r2 claims. It is instrumented below R7/R10 as
  written (R2-M1).

New probes in this directory (numpy only, on the same replica demography as `power.py`):

| probe | what it tests |
|---|---|
| `probe_retention.py` → `probe_retention.txt` | carriage under shuffle against r2's R_drift floor and a same-economy marker floor, by regime and by the trait's value |
| `probe_verdicts.py` → `probe_verdicts.txt` | how often one false opposite-sign EARNS call turns a dominated map into EARNINGS DEPEND |

## 1. The 12 MUSTs from the first review

| MUST | r2 | status |
|---|---|---|
| M1 composition | y′ = share(240–299) − share at the merge; N subsampled to M's merge-time count; K2 on y′; `power.txt` §6a reproduces the check (raw false D-WIN 0.54–1.00, y′ 0.01–0.05) | **closed** |
| M2 pre-merge extinction | valid seeds; PARTIAL-X is a survival call, never a WIN | **closed** |
| M3 RESOLVING | tied to δ_i (P(TIE \| 0.15) ≤ 0.05, P(WIN \| 0.15) ≥ 0.80 at q/2); both 90% bounds of g0; 1,500 replica seeds; variance negatives silent | **closed**, with S-1 below: `power.py`'s `resolvable()` docstring still says "the lower 90% bound", not both |
| M4 CONTINGENT | pooled per-kind null; own BH family; eligible for R-B | **closed**, with S-2 below: df "≈ 108" assumes N at all 36 points, but the M/N gate runs N at ≤ 12 |
| M5 R-A | the signs of the estimates; \|t₁ − t₂\|; the layer named | **closed** |
| M6 LEVER | between-fauna differences; "cap binding" | **closed** |
| M7 perception controls | K3 at a = 6 on the behavioural legs, 16 hosts pooled, bars and false-VOID rate stated; G8(b) marked untested; NOWHERE needs a valid layer at ≥ 2/3 of PAYS points; PERCEPTION NOT MEASURED otherwise | **closed** |
| M8 `--merge-null` | a separate label, mate pool, stream and names; the tests; the arena transient | **closed** |
| M9 T4 | seed-level PW contrast; power 0.66–0.99 at Holm's first step (`power.txt` §6c) | **closed** |
| M10 M2 weights | seed level, logit(clipped share) change, random intercept per point | **closed for share**; the income model has a new defect (R2-M2) |
| M11 verdicts | a precedence order; decided calls only; EARNINGS DOMINATED; WORLD-INVARIANT reachable | **closed as asked**; a new asymmetry (R2-M3) |
| M12 2a/2b order | as proposed | **closed** |

All 12 SHOULD items are taken as proposed. Among r2's own open items:

- **Item 1 (both bounds):** yes. Under shuffle the binding side is the upper one, and passing at both is what M3
  needed.
- **Item 2 (verdict 5):** r2's reading is right.
- **Item 4 (y′ and the matched N):** taking both is harmless.
- **Item 5 (variance factor 3):** acceptable, since shuffle never calls the variance mutant a WIN, and RBT-126's
  mutants can replace it by amendment.
- **Item 7:** keep VARIANCE-DRIVEN as a flag, not a verdict.
- **Items 6 and 8:** answered in §2 and §3 below.

## 2. With RESOLVING at 0–2 of 36 under shuffle, what can the share layer still answer?

r2's own numbers:
- RESOLVING needs g0 ≤ 0.65 at n 8, or ≤ 0.80 at n 16 (`power.txt` §5).
- The prior arithmetic puts **0–2 of 36 Stage-1 points** there, both at p = 0.08 in PW (`prior_regime.txt`).
- The same arithmetic puts **3–12 points into survival calls**: the designed fauna starving at p = 0.08 and at c = 2.

The resolving band and the starving band are the same corner of the grid, so a point that resolves is likely to be
PARTIAL or EXCLUDED first, and never reach a share call.

A WIN does not need RESOLVING; only TIE does. But under shuffle at g0 1.0, even an edge of 0.40 items is called at only
0.52 / 0.95 (q/36 / q/2; `power.txt` §10.1). Where a WIN does fire, VARIANCE-DRIVEN may take it: shuffle's starvation
sieve drives out a same-mean, higher-variance fauna (y′ −0.37 to −0.48).

**So the share layer is expected to produce 0–2 body calls on the whole map**, and possibly none that survive PARTIAL
and VARIANCE-DRIVEN. The effects on the verdicts:

- **Verdict 1 (DEPENDS)** needs share WINs of both signs. It is unreachable in expectation.
- **Verdict 3 (ONE BODY DOMINATES)** needs X-WIN at a third of the habitable points. It is unreachable by
  construction, because the M/N gate runs M at ≤ 12 of 36 points.

These two verdicts are therefore dead text under shuffle. They are harmless only because EARNINGS DEPEND and EARNINGS
DOMINATED sit beneath them.

**Compute.** M + N at the gated points is about 330 core-h at 20 core-s:
- Stage 1: 12 × 8 × 1.90 core-h;
- Stage 2a: 4 × 8 × 1.90;
- Stage 2b: 6 × 8 × 1.90.

That is about 14% of the sweep. What it buys:
- (a) the **M arm's one-world income** and the interference table (S5). This is the only shared-world evidence in the
  sweep, and it is worth keeping;
- (b) a share layer that decides 0–2 points.

The anchors (`c1-p030-U-L`, `c0-p030-U-L`, `c1-p030-PW-G`) are also RBT-118's fixed points, where RBT-118 runs its own
M arms at n = 20 to 1,200 seasons. The sweep's M/N there duplicates it at a smaller n.

**Recommendation (R2-S1, for the ruling):**
- Keep **M** (not N) at the gated points as a one-world income column.
- Run **N** only where the census g0 is ≤ 0.8 (shuffle's actual resolving bound, rather than the gate's 1.0). Take the
  anchors' share results from RBT-118 rather than re-running them.
- Move verdicts 1 and 3 below their income counterparts, or mark them "not expected to be reachable under the
  registered rule".
- Spend the roughly 150–250 core-h saved on R2-M1's retention controls and on hosts.

If the ruling prefers the share layer intact, the design should at least say in §8, as it already says in §6.2 and
§12.2, that the confirming and falsifying verdicts both run through the income layer in practice.

**Does the income layer carry the verdicts honestly?** Mostly. EARNINGS DEPEND is correctly worded as "a claim about
income, not about which body persists", and the side-by-side S arm is the right source for it. Two defects remain:

- **R2-M2 (MUST): g0 must not enter the income model.** §7.2 fits "income: x_j on the same terms", and the same terms
  include **the point's measured g0**. That g0 is taken from the **M arm, seasons 180–299**. Two problems follow:
  - **(a) Most points have no g0.** The M/N gate leaves 24+ of 36 Stage-1 points with no M arm, so the registered
    income fit, T1 (primary), T2 and T3 would drop them or fail.
  - **(b) g0 is downstream of the axes.** It is the resident net income, which the work price and clutter set. So
    conditioning T2/T3 on it absorbs the very price and clutter effects they test.

  **Fix:** g0 (or better, the census regime, which is measured at every point and before the read window) enters only
  the **share** model. The income model's terms are c, log p, L, s and c × log p.

- **R2-M3 (MUST): one opposite-sign EARNS call is too cheap a trigger.** EARNINGS DEPEND needs T1 to reject and
  **≥ 1** EARNS-H and **≥ 1** EARNS-D. In a map where one body truly dominates, but a few points sit at a break-even
  inside the grid (which is where R-A will put its refinement points), BH at q 0.10 produces a spurious opposite call
  quite often (`probe_verdicts.txt`, 36 points, n 8, the design's noise):

  | true-zero points among 36 | P(≥ 1 false EARNS-D) | P(≥ 2) | P(≥ 1 at BH q 0.05) |
  |---|---|---|---|
  | 3 | 0.077 | 0.001 | 0.045 |
  | 6 | **0.136** | 0.007 | 0.077 |
  | 12 | **0.236** | 0.028 | 0.134 |

  T1 rejects in such a map anyway, because the H lead's size varies with price. So in 8–24% of truly dominated maps,
  the verdict flips from EARNINGS DOMINATED (a falsifier) to EARNINGS DEPEND (the predicted confirmation).

  **Fix:** an opposite-sign set counts for DEPENDS / EARNINGS DEPEND only if it has **≥ 2 calls**, or one call
  corroborated by M3: a break-even p* with a Fieller interval lying inside the swept price range on that row. The
  same rule applies to "no call for the other fauna" in verdicts 3 and 4, so the two sides are symmetric.

- **S-3: income of the living is compressed at marginal points.** The income flow is "of living members". At a point
  where one fauna is near viability, the starving members leave the average, so its flow sits near the living cost
  whatever its members earn (R5: "say which").
  - Print net income per birth beside the flow at every point.
  - Mark EARNS calls at points where either fauna's per-birth income is below the living cost.

## 3. The retention layer (§6.4): instrumented per R7 and R10?

Not yet. There are three problems, and a single fix covers most of them.

### 3.1 The saturated band does bound retention under shuffle

r2's premise is: "The saturated band bounds spread, not retention … the one perception question the sweep can ask
everywhere". It rests on RBT-80's seeded arms. But RBT-126's own replica (`runs/RBT-126/retention.txt`) shows, under
shuffle:

- carriage at 300 falls from **0.99** to **0.54** as the non-carriers' income gn rises from 0.08 to the carriers' 1.05;
- the floor is 0.54–0.58.

RBT-80's non-carriers earned 0.08–0.64 against carriers at about 1.05. That is a trait worth 0.4–1.0 items. Retention
is visible at that size.

`probe_retention.txt` asks the sweep's question: a trait of value Δ, in a fauna at carrier income gc, under shuffle,
with r2's HOLDS call (n 8, q/2, mean h ≥ 0.10).

| gc (regime) | Δ 0.10 | Δ 0.20 | Δ 0.40 |
|---|---|---|---|
| 0.6 | 0.95 | 1.00 | 1.00 |
| 0.9 | **0.10** | **0.44** | 1.00 |
| 1.3 | **0.03** | **0.06** | **0.22** |

A perception step in PW is worth about 0.17–0.19 items on the kinematic model (`probe_gprop.txt`), with the planted
prize at a = 6 probably larger. So at a rich PAYS point retention reads UNDECIDED, not HOLDS.

The saturated band bounds retention one step later than it bounds spread (compare §2: the share layer resolves
δ_i = 0.15 only at g0 ≤ 0.65–0.8), but it does bound it. NOT HELD almost never fires falsely (≤ 0.02), so the layer is
honest. It is just mostly UNDECIDED where the share layer is SATURATED.

**Fix, part of R2-M1:**
- Delete "not bounded by the saturated band" (§5.4, §6.2, §6.4, §8, §12.6). Replace it with a power table by regime
  × trait value, in this form.
- Rank the retention points by census g0 as well as by layout, so that the ≤ 12 fauna-points are spent where HOLDS
  can be read.

### 3.2 The floor and the planted negative (R7, R10)

**R_drift** (`--neutral --breed-gate none`) differs from R_sel in four ways at once:
- no living cost;
- no starvation;
- deaths by age only;
- a different turnover (1.33 against 1.00 births a season at gc 0.6 in the replica).

It also depends on a flag that is **designed but not yet code** (`--breed-gate none`; r2 open item 8). Without it,
RBT-126's DRIFT-GATE shows the "no-selection" floor is itself selected: carriage 0.91 where no gate gives 0.55.

In the replica the two floors come out close (0.53–0.57 either way; `probe_retention.txt`). But R_drift is not the
control R7 asks for.

The planted compass at a = 6 changes **motor output**, not only what the body knows. So carriage above R_drift can
come from:
- the motif's effect on gait or speed;
- or the vulnerability of its wiring to the operators;

and not from perception. R7 requires behaviour by instrument with a planted negative. For retention, the negative is
**the same motif fed with no information**.

**R2-M1 (MUST), fix:**
- **(a) Floor and negative in one arm:** add **R_marker(F)**. It is the same economy, the same founders and the same
  motif at a = 6, with the motif's food sensors **lesioned** (reading the transform's zero-information constant, as
  `steer.py`'s lesion condition does).
  - Carriage(R_marker) is the floor. It matches R_sel's turnover and operators exactly.
  - It is a planted negative that HOLDS must not fire on: a motif held for its motor effect is held in both arms.
  - The call becomes h = carriage(R_sel) − carriage(R_marker).
  - This removes the dependence on `--breed-gate none`, and R_drift can be dropped. R_drift may also be kept as a
    descriptive second floor; the cost is the same.
- **(b) Readout floors:** before any arm, the carriage readout ("motif at ≥ half its planted weight, confirmed
  behaviourally on 20 members") is validated on three sets:
  - planted founders, where it must read ≥ 0.95;
  - random founders, whose **false-carriage rate** is printed and is the readout's floor;
  - children with the motif's links deleted or halved.

  This matters for the holistic plant (G8(c)): it sits on two expressed Parts of distinct Nodes, and structural
  mutation can re-express, duplicate or drop them. There is no RBT-80 precedent (r2 open item 8). A readout that
  cannot fail on the holistic body is R10's "control not shown able to fail".
- **(c) Operator table (R6):**
  - Print per fauna, per retention point, the erosion rate u_f per birth: the fraction of a planted carrier's
    children that lose carriage, measured as RBT-116's G6 does, crossover 0.
  - Print the realised births per season in R_sel and R_marker.
  - The holistic operator erodes wiring about 5× faster (R6). So "HOLDS for the designed fauna, not for the holistic"
    is a statement at the default operators, and must be printed so. It is not a body-plan comparison unless it is
    re-read at matched erosion (`--structural-rate-scale`) at one point at least.
- **(d) Confirmation leg:**
  - "Confirmed behaviourally on 20 members by STEERS-or-SMELL-USE" needs the same K3 bars as the perception layer
    (16 hosts, the behavioural legs).
  - The same probes on R_marker members, where the motif is lesioned, must read NONE. That is a second check able to
    fail.

### 3.3 Cost

Replacing R_drift by R_marker costs nothing extra. Keeping both adds about 160 core-h (12 × 8 × 1.67).

The readout validation in (b) is solo probes: about 0.1 core-h a retention point. The erosion table in (c) is about
40 children × 2 faunas × 16 draws a point, about 0.2 core-h. So R2-M1 costs well under 10 core-h, or +160 if both
floors are kept.

## 4. Smaller items (SHOULD)

- **S-1.** `power.py`'s `resolvable()` docstring says "the lower 90% bound". Make it run at both bounds as §6.2
  registers, and print both.
- **S-2.** CONTINGENT's pooled null: with N at ≤ 12 points (fewer if R2-S1 is taken), df is about 12 × 4 − 12 per
  kind, not 108.
  - Re-run `power.txt` §6b at the gated df.
  - State that the pooled drift SD is assumed homogeneous across the gated points' regimes. At shuffle's g0 0.5–1.3
    the null SD is 0.145–0.157, which is fine.
- **S-3.** Income per birth beside the income flow at marginal points (§2).
- **S-4.** VARIANCE-DRIVEN fires when the mean-income test is *not* significant. At n 8 that is common for real WINs.
  Use a test for the direction of evidence instead: flag when the income-SD difference explains the WIN better than
  the mean difference, in a two-predictor seed-level fit. Or require a TOST on the mean income difference.
- **S-5.** The M/N gate's census threshold (g0 ≤ 1.0) is generous against shuffle's 0.8. Keep it only if M is run for
  the one-world income column (R2-S1). For N alone, use 0.8.
- **S-6.** The anchors duplicate RBT-118's fixed points. Coordinate seeds, or take the share result from RBT-118.
- **R2-S1.** The share layer's role (§2 above), for the ruling.

## 5. The list

**MUST**
- **R2-M1** Retention:
  - a same-economy lesioned-motif marker as the floor and planted negative;
  - carriage-readout floors validated on planted, random and ablated genomes;
  - a per-fauna erosion and turnover table, with cross-fauna HOLDS worded at the default operators;
  - behavioural confirmation at K3's bars;
  - delete "not bounded by the saturated band", and register the regime × value power table.
- **R2-M2** No g0 in the income model: it is missing at gated-out points and downstream of the axes. The census
  regime, if anything, goes in the share model only.
- **R2-M3** DEPENDS and EARNINGS DEPEND need ≥ 2 opposite-sign calls, or one corroborated by a break-even inside the
  grid. The same rule applies to the "no call for the other fauna" clauses.

**SHOULD:** S-1 to S-6, and R2-S1 (demote the share layer to a descriptive one-world column; N only at census
g0 ≤ 0.8; anchors from RBT-118).

With these three MUSTs, the design is ready to register once its gates are met. Those gates include
`--breed-gate none`, which is needed only if R_drift is kept.

## Limits

- The retention and verdict probes are replicas: fixed types, Poisson income, and erosion as a single rate u = 0.06
  (RBT-80's figure, as RBT-126 uses it). They show where the calls can and cannot be read. The pilot and the erosion
  table measure the real numbers.
- r2 was read at `215494c`, and RBT-126 at the integration branch head `e3c9473`.

---
_Generated by [Claude Code](https://claude.ai/code)_
