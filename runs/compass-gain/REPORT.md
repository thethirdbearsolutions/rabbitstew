# The compass is not missing from the search. It is 30 times too small.

**Lead-researcher measurement, unreviewed. It corrects a finding of my own — see §5.**
File analysis only: no simulation, no new runs. 180 evolved robots, 19,892 link weights,
three search depths. Scripts `steering_gain.py`, `weight_scale.py`; raw output `survey.log`.

## 1 What RBT-61 handed us

RBT-61 was filed, and then withdrawn by its own author, in the same night. The withdrawal is the
valuable half. The Pioneer's two drive wheels hinge about their own outward normals (world-frame
axis dot product exactly −1.0000), so on this body the **sum** of the two effector commands is the
steering axis and their **difference** is the throttle — the transpose of a textbook differential
drive. The spike had installed the same sign on all four links, putting the common mode on the
steering axis: a smell-gated pirouette, never a compass.

Corrected, the circuit works. A 4-link antisymmetric motif, hand-installed on 7 evolved Pioneers
across 64 paired seeds, earns **+0.897 items on a 1.516 baseline — +59%, 7/7 robots**. So the world
does reward chemotaxis, richly. That closes a question ten world arms failed to answer.

It opens a sharper one, which RBT-61 states and explicitly leaves untested:

> *"+0.897 is an upper bound on the prize, not evidence the search can find it. The explanation for
> 600 seasons of blind mowers becomes 'the operator essentially never proposes the motif that pays,
> at the magnitude at which it pays' — a claim about the search, testable, and untested."*

This tests it.

## 2 The quantity

Write the signed linearised gain from wheel nose *i* to the steering axis as
`s_i = g[n_i→e1] + g[n_i→e2]`, and split the pair into the two terms that have opposite fates:

| term | what it puts on the steering axis | RBT-61 measured |
|---|---|---|
| `a = (s₁ − s₂)/2` | `a·(n₁ − n₂)` — the gradient. **The compass.** | a=16 null; a=32 **+0.246**; a=64 **+0.897** |
| `c = (s₁ + s₂)/2` | `c·(n₁ + n₂)` — turn harder when anything smells. The pirouette. | the withdrawn spike: **−1.502** |

`a` is exactly RBT-61's `k`. A **single** wired nose forces `|a| = |c|`: half compass, half pirouette,
and the pirouette half is the more strongly measured of the two effects.

Two gains are reported because they bracket the truth. **DIRECT** is the weight on a nose→effector
link — precisely the quantity RBT-61 installed into, no linearisation at all. **PATH** is the signed
path sum to depth 4 through the whole network, which counts routes through the global brain but
linearises tanh at the origin; since tanh only ever attenuates, PATH is an **upper bound**.
Conservative in the direction of the claim.

> **RBT-81:** PATH is *not* an upper bound. The depth-4 sum is a truncation of a series that diverges on every committed Pioneer best (spectral radius 1.57–4.92; RBT-67's adversary, RBT-78's `truncation.py`), so its value is set by where the counting stopped. `steering_gain.py` now reports the depth-1 term and prints ρ beside the path column; this report's figures are left as reported.

## 3 What 180 evolved robots carry

| arm | depth | both noses wired | gradient-dominant (\|a\|>\|c\|) | **best \|a\| among those** | a≥32 **and** gradient-dominant |
|---|---|---|---|---|---|
| P-801 baseline | 23 | 0/60 | 0/60 | — | **0** |
| A30-801 | 39 | 10/60 | 6/60 | 14.81 | **0** |
| A15-801 | 78 | 4/60 | 3/60 | 16.26 | **0** |

Those are the PATH figures — the generous bound. On DIRECT, the route actually measured, the best
gradient-dominant individual in the entire corpus carries **a = 0.548**, against 32 for +0.25 items.

> **RBT-81:** "gradient-dominant" (`|a| > |c|`) is algebraically `s₁·s₂ < 0`, a sign test with no magnitude in it (RBT-78's adversary); the PATH columns above are depth-4 truncations of a divergent series. `steering_gain.py` now reports the balance ratio `r = min(|s₁|,|s₂|)/max(|s₁|,|s₂|)` and the sign separately, with no threshold; the table stands as reported.

**Three conditions, each individually met sometimes, jointly met never.** The topology turns up in
7–17% of a wheeled population. Of those, roughly half have the gradient outweighing the common mode.
Of those, **none, in 180 robots at any depth, reach a magnitude that pays.** The best compass in the
corpus sits at a = 16.3 — RBT-61's own null point, +0.054 items [−0.040, +0.158].

## 4 Why: the operator has a weight scale, and it is ~3

The motif needs per-link weights of w = 16 (a = 2w = 32, +0.25 items) to w = 32 (+0.90).

| arm | depth | links | median \|w\| | p99 | **max** | \|w\|≥8 | ≥16 | ≥32 |
|---|---|---|---|---|---|---|---|---|
| baseline | 23 | 7,247 | 0.85 | 3.07 | 4.65 | **0** | 0 | 0 |
| A30-801 | 39 | 5,088 | 0.98 | 3.94 | 5.52 | **0** | 0 | 0 |
| A15-801 | 78 | 7,557 | 1.13 | 4.33 | **6.11** | **0** | 0 | 0 |

**Not one weight in 19,892 reaches 8** — the magnitude at which the compass is still null. The paying
magnitude is 2.6× beyond the extreme of the whole corpus; the strong one 5.2× beyond.

This is not an accident of these runs, it is the operator's stationary scale. `mutate_weights`
perturbs each link with p=0.25 by N(0,0.4), and with p=0.02 of those redraws it from N(0,1). Nothing
bounds a weight, but the reset truncates the walk, giving

  σ(d) ≈ √(1 + 0.0392·d)  →  1.38 at depth 23, 1.59 at 39, **2.01 at 78**

against observed 1.25, 1.47, 1.72 (median/0.6745). The law holds in form and runs ~12% under the
pure-drift prediction, as selection against extreme weights should make it. Inverting it: the typical
link reaches w = 16 at **depth ≈ 6,500**. The deepest arm this programme has ever run reached 78.

At depth 78 the four-link combination has SD 2σ ≈ 3.4, so P(|a| ≥ 32) ≈ **10⁻⁷⁷** — before requiring
that the four links exist at all, and with the right signs. This is not a near miss.

## 5 Correction: this reverses my own finding of five hours ago

`SUPERSEDED-FINDING.md` in this directory, written while the Chaotic server was down and **never
posted**, concluded from the same populations:

> *"The structural precondition for a Braitenberg compass is present in 7 to 17 percent of the
> wheeled population... So the bottleneck is **not** that the circuit is never proposed."*

The topology counts in it are right and replicate here. **The conclusion drawn from them is wrong**,
and it is wrong the same way RBT-61's spike was wrong. It rested on `analysis.sensor_influence`,
which sums **absolute** weights along each path and clips them at 3.0. An unsigned, clipped sum
cannot distinguish a compass from a pirouette, and cannot see a magnitude shortfall at all — the two
things that turn out to decide the question. I was counting wiring and calling it a circuit.

Corrected: the bottleneck is not proposal of the *topology*, which is common. It is proposal of the
topology **with the antisymmetric sign structure and at a weight scale the operator reaches once in
10⁷⁷**. My "the wiring turns up routinely and earns nothing" was the right observation attached to
the wrong cause: it earns nothing because at w ≈ 1 it is in RBT-61's inert zone, not because a
pairing is intrinsically useless.

I have left the superseded note in place beside this one rather than editing it away.

## 6 What this licenses, and what it does not

**Licensed.** The 600 blind seasons are explained by a magnitude gap, not an absence of proposal and
not an absent prize. The prize is +59% and the search cannot reach it; those are now separate,
measured facts. RBT-42's correlated-link operator addresses *topology* — it would raise the crossed
rate from 1% to 50% and still deliver w ≈ 1 circuits sitting in the inert zone. **On this evidence
RBT-42 as scoped does not fix the problem it is aimed at.** What would: raising the weight scale
(a larger `weight_sigma`, a heavier-tailed step, or a per-link gain gene), which is a smaller change
than any world arm and is untried.

**Not licensed.** Four limits, the first serious.

1. **PATH linearises tanh.** Effective indirect gains are lower than reported, so §3's counts are an
   upper bound. The DIRECT column has no such problem and is far more damning, and the `|a|>|c|`
   *ratio* is more robust to linearisation than either magnitude. But no bolted-on install was run.
2. **RBT-61's payoff curve is 7 robots from one run** (its own stated caveat), solo bouts only, and
   unbounded above — a=64 was the top of every sweep. The thresholds I compare against inherit that.
3. **Co-adaptation is untested on both sides.** RBT-61 bolted a circuit onto a finished controller;
   I measured finished controllers. Neither says what an evolved population does with a compass it
   grew around. That remains the one experiment that could overturn either result.
4. **One body.** The holistic populations carry no food nose on both wheels at any depth, so the
   whole analysis is Pioneer-only. For an arbitrary lump the steering axis is not the effector sum
   and this decomposition does not apply.

## 7 Pre-registration for the obvious next arm

Stated before running, with the verdict rule fixed:

> **Raise `weight_sigma` from 0.4 to 2.0** (stationary σ ≈ 10 at depth 78, still short of 16) and run
> the A15 configuration on seeds 801–805. **Prediction: still blind.** I expect the per-cell yield
> null to be unbeaten and `a ≥ 32` gradient-dominant individuals to remain at **0/300**, because 10
> is under the threshold and because the same larger steps that build the compass also destroy the
> mowing gait it would have to improve on. **Confidence 0.7.**
> **Falsifier:** any seed producing a gradient-dominant individual at a ≥ 32 whose lineage persists
> 50 seasons. **I will report this whichever way it lands**, and a null here points at the gain gene
> rather than the step size.
