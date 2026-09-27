# RBT-121 synthesis check: `runs/RBT-121/SYNTHESIS.md` @ 92d5ba4 (PR #405)

**Checked against:**
- the four audits, with their "Corrections after #403" blocks;
- `adversary/ADVERSARY.md` (e9096cb);
- `ecology/probe_gprop.txt`;
- `runs/RBT-118/prior/ANALYSIS.md` §4a, and the prior-adversary line "reverse the lead on 21/29";
- `docs/prior-art/REVIEW.md` on `results/RBT-122-prior-art`. Only the Sims and Taylor lines were checked; the full
  citation check belongs to #404.

**Verdict:** four MUST items and six SHOULD items. The rest of the synthesis matches the corrected sources.

## MUST

**M1. The headline overclaims the 18-cell grid and the free rotors** ("Why this exists", blockquote 1).
- The grid is C's *kinematic* model, not the simulator. The nose step is not "nothing measurable" in every cell: it
  ranges from −0.8% to +9.9%, and is resolved above zero in some cells. It is unresolved only at the calibrated cell
  (ADVERSARY §6a).
- Free-spinning limbs were bought under RBT-113's **down** selection on net yield (PREREGISTRATION.md:91, 341–342).
  They are how the simulator lets a body *spend* capacity. They are not something it pays when selection is for food.

Replace the first blockquote with:

> **At present the simulator pays more readily for blind motion (coverage, and full throttle) than for perception,
> and it lets unbudgeted motor capacity be spent on free-spinning limbs.** In a kinematic forager under the world's
> food and smell rules, +25% speed pays +13–40% against 0–10% for a one-σ nose step, in all 18 cells of the regime
> grid. On real bodies, a blind single-motor tumbler nets about +0.7 a season, and RBT-113's U line ate as much
> blind as intact.

**M2. R5 and fix #4 use the wrong regime metric.**
- "Net income **per birth** ÷ living cost" would classify P-801 as unsaturated. Its per-birth income is about 0.48,
  because 60% of births starve. Yet P-801 is the saturated case: +94% income buys +14% children.
- The saturation threshold (g0 ≳ 0.8 gross, i.e. net ≈ 2× cost; ADVERSARY §1d) is a property of the **solvent**
  members.

Replace, in R5's Rule, "net income per birth ÷ living cost" with:

> net income of members that reach breeding age ÷ living cost (the saturation measure), beside net income per birth
> (the viability measure)

Make the same change in fix #4. Offspring by income quintile stays the direct measure of both.

**M3. R4's G = 2.5 paragraph misreads `probe_gprop.txt` on HP, and drops the SEs.**
- For HP at G = 2.5, k 1→1.4 gives **+0.360 ± 0.054**, against **+0.357 ± 0.056** for speed: a tie, not "speed still
  leads".
- The "committed worlds" rows are the committed *layouts* with the *new* sensor.
- At G = 10 the first steps pay *more* than at G = 2.5. The first weak nose gives +0.36 against +0.18 in PW, and
  +0.44 against +0.14 in HP.

Replace the three sub-bullets from "C's follow-up probe" to "the default candidate" with:

> C's follow-up probe (`probe_gprop.txt`: kinematic, n = 300 paired seeds, ± SE) uses the proposal's own sensor with
> running-baseline centring.
> - **In PW at G = 2.5:**
>   - the first weak nose pays +0.18 ± 0.05 items a season;
>   - the steps k 1→1.4 and 2→2.4 pay +0.19 ± 0.04 and +0.17 ± 0.03;
>   - +25% speed pays +0.17 ± 0.05. Every step ties speed.
> - **At G = 10**, contrasts saturate: the first weak nose pays more (+0.36 ± 0.08), but the second step falls to
>   +0.08 ± 0.02.
> - **In the committed layouts with this sensor at G = 2.5:**
>   - HP: the first step ties speed (+0.36 ± 0.05 each), and speed leads the second (+0.20 ± 0.04).
>   - Uniform: speed leads about 2× (+0.19 ± 0.04 against +0.09 ± 0.03).
> - Root-centring and running-baseline centring score alike here, because the model has no root sensor. The choice of
>   a running baseline rests on ADVERSARY §6b, not on this probe.
> - G = 2.5 with a running baseline is the default candidate. The world gate confirms it on real bodies.

**M4. R4's last lever and fix #7 claim that eating rules stop blind tumbling from paying.**
- The tumbler's +0.7 comes from travel: 2–5 m of displacement and 5–10 m of path (ADVERSARY §7).
- `eat_from=root` or surface eating removes only its static-reach food, 0.1–0.4 with the motor off.
- Coverage is priced by the work price and the world layout.

Replace R4's last lever with:

> eating rules that stop span and flailing sweep from substituting for steering: `eat_from`, surface eating, and
> clearance from the geoms (C4, A5). These do not remove a tumbler's coverage income; the work price (C3) and the
> patch layout do.

In fix #7, change "why first" to:

> stops span and thrash-sweep paying as foraging (C4); the tumbler's coverage is fix 13's and fix 5's

Consider moving fix #13 (the work price) above fix #7, since it is the only listed lever on blind-motion income apart
from the layout.

## SHOULD

**S1. R3's rule needs its caveat.**
- A 5 s settle cut the drifters from 14 to 5, but some bodies then drifted *more*: 0.52 m, 0.57 m, and 7.30 m on
  terrain against 0.00 m flat.
- Motors-off food then fell to 0 in every group, which has not been explained (ADVERSARY §4).

Add to R3:

> Part of the drift is terrain rolling, not settle residue. A fixed-length 5 s settle cut drifters from 14 to 5 but
> lengthened some drifts, so the closing test runs on the registered terrain, not only on flat ground.

**S2. R2 omits two consequences of the weld group.** Add:

> fixed siblings never collide, and the contact sensor is blind inside a weld group (ADVERSARY §2a)

This bears on R8's lever report and on A's B6 item.

**S3. R5's imposed-selection bullet loses the caveat on u.** Add:

> The u values (0.089, 0.15, 0.28) are from paper 10 and RBT-112, not re-measured for RBT-113's operator (ADVERSARY
> §5).

**S4. R5 prefers `energy_leak` or tickets without evidence.** Only `energy` order was measured for its depth cost.

Replace "Prefer `energy_leak` or tickets" with:

> `energy_leak` and tickets weight income rather than age × income, but their depth cost is unmeasured; measure it
> before preferring either.

**S5. "What the audits missed" items that are lost.** Add to R10:

> A drift or no-selection control has no breeding gate: with threshold 0, `energy >= birth_threshold`
> (`ecology.py:527`) still bars members whose cumulative net is below −initial energy.

Add to R5, or to R11:

> Income quoted as the mean lifetime score of the living is survivor-weighted (P-801: 1.3 among the living, 0.48 per
> birth); say which. Any cited margin from a Monte Carlo probe carries a paired CI (C's two probes differ by 19 points
> on one cell).

**S6. Qualify the ecology blockquote to the one lineage measured.** Replace "The ecology selects hard on staying
alive, and weakly on anything above that." with:

> In the one committed lineage measured (P-801), the ecology selects hard on staying alive and weakly on anything
> above that.

## Checked and correct

- **R1:** the gear figures, the 0.5% Pioneer margin and "the extent earns nothing".
- **R2:** 97%, 94%, about a third inside, the weld group, `genetics.py:209`.
- **R3:** 14 of 120.
- **R5:** 1.27 Δ/σ_P and u/(1 − u); rep₂ 0.03–0.1; 60% starve; 39% by age; the gerontocracy figures (137 → 71,
  31 → 54).
- **R4:** the 13–40% and 0–10% figures.
- **"Committed results":** RBT-80, paper 10 H8, and RBT-113/117 match the corrected forms.
- **RBT-118:** "reverses on flat ground on 21 of 29" matches `prior-adversary/ADVERSARY.md:9`.
- **Fix-list order:** defensible. The gear budget is the only allowance with committed damage. The cone is the sink
  for it. The effector bias is tiny. The readout needs no code. M4's reorder is optional.
