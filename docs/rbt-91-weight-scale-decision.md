# RBT-91: the weight-scale ceiling — decision

**Decision, as restated 2026-09-19 after the measurement this ticket deferred: option B's
positive control is now warranted. The structural rate is not zero.**

This reverses the first version of this document, which chose option A. It reverses it by the
rule that version's successor pre-registered before looking, and the paragraph below records what
was claimed, what was wrong with it, and what replaced it.

## The measurement that decided it

**Does drift propose the routed motif's structure?** The predicate — a global non-sensor unit
with incoming links from *both* wheel `food` noses of **opposite** sign and outgoing links to
*both* drive Effectors of the **same** sign, signs taken on summed weights so cancelling links do
not count — counted over RBT-78's denominator unchanged (19 `mutate_controller` mutations from
committed parents, 5,000 lineages per pool, `add=0.15 rem=0.1`, master seed 20260912, its
generator imported rather than reimplemented):

| pool | lineages | structure present | rate |
|---|---|---|---|
| W4b-801 bests | 5,000 | 3 | 0.060% |
| P-801 final 60 | 5,000 | 1 | 0.020% |
| **both** | **10,000** | **4** | **0.040%** |

**The predicate can say yes**, which is the only thing that makes a rate meaningful: on motifs
installed through `genotype_motif.install` it fires 6 of 6 across three magnitudes and both signs,
and reads 0 on the bare parent. The drive is calibrated rather than assumed — the reading is flat
from 0.05 down to 0.001 and saturates only at 1.0.

**And the magnitude is not far away either.** Measured through the same probe, an installed motif
at the **first paying rung** (RBT-69's +0.246 at `w = 16`) has a realised small-signal steering
response of **6.87**; the null rung (`w = 8`, +0.054 with a CI spanning zero) reads **3.57**. The
four drift-proposed structures read:

| lineage | realised `a` | against the first paying rung |
|---|---|---|
| W4b-801 #176 | **−6.332** | **92%** |
| P-801 #109 | +0.471 | 7% |
| W4b-801 #3550 | −0.252 | 4% |
| W4b-801 #2430 | +0.001 | 0% |

Readout `docs/artifacts/RBT-91-structural-rate.txt`; script `runs/RBT-91/structural_rate.py`.

## The correction, dated, rather than an edit

**What the first version claimed.** That there were two barriers, that magnitude was the smaller
and structure the larger, and that option B should therefore be declined because widening the
weight scale removes only the smaller one.

**Why that was wrong, in three places.**

1. **The magnitude arithmetic was the *installed* motif's.** `genotype_motif.install` pins the two
   nose→interneuron links at ±1 and puts `w` on the two interneuron→Effector links, so `a = 2w`
   and the first paying rung needs `|w| ≥ 16` — the `~1 × 10⁻⁷` figure of the 16:02 correction.
   **That is one corner of the region, not the region.** An evolved copy has all four links free
   and the interneuron's bias free, and its linearised gain is a product,
   `a = (u_L − u_R)(v_L + v_R)/2 · sech²(b)`, so four links at `|w| ≈ 2.83` already give `a = 16`
   and no link needs 8 (adversary, RBT-89 delegate). At the asymptote `|a| ≥ 32` is **1.32%**
   before the bias slope and **0.055%** after, against my 1 × 10⁻⁷.
2. **"A ceiling no amount of running removes" is true of a single weight and false of the motif's
   magnitude.** The single-weight result stands exactly as measured (below). The motif's magnitude
   is common at the asymptote, and the asymptote is ~200 mutations of depth, ~6,000 seasons by
   RBT-59's law. The accurate form is **"no run this programme has made"**, not "no amount of
   running".
3. **The reopening condition named an instrument that does not exist.** It asked for the routed
   motif's structural rate "with RBT-78's instrument", whose DIRECT column is **exactly zero on
   the routed motif by construction** (RBT-87) and whose PATH column is not a quantity (RBT-81).
   The "0 of 10,000" that the two-barrier ordering rested on therefore never said what it was
   used to say.

**And the bias is a barrier the first version did not name.** `mutate_weights` steps biases with
no reset and no clamp, so unlike weights they have no stationary distribution: `sd(b) = 0.2·√depth`
and the tanh slope collapses, median `sech²(b)` 0.74 at depth 20, 0.085 at 200, 0.001 at 1,000.
It runs against the motif, not for it.

## What still stands: the single-weight ceiling

Unchanged, and none of the above touches it.

| quantity | value |
|---|---|
| clamp on `link.weight` | **none** (`freq` and `dims` are clipped; weights are not) |
| operator, on 57 of 57 committed configs | `weight_rate` 0.25, `weight_sigma` 0.4, `weight_reset_rate` 0.02 |
| per weight per mutation | `P(step)` 0.245, `P(reset)` 0.005 |
| committed bests (127 genotypes, 9,637 links) | max \|w\| **5.200**, p99 2.97, 0.00% ≥ 8 |
| drift only, depth 10 / 20 (the realised depth) | max 4.745 / 5.008, 0.00% ≥ 8 |
| operator asymptote (20,000 mutations) | rms **2.938**, 1.96% ≥ 8, 0.03% ≥ 16, 0.00% ≥ 32 |
| predicted asymptote | variance 8.84, rms 2.97 |

A *single* weight's scale is the operator's stationary distribution — not a clamp, and not
selection, since drift from the committed bests reproduces the ceiling at the realised depth with
nothing selecting. That is a ceiling no run length removes. It is simply not the quantity the
motif needs, which is a product of four weights and a slope.

**Census scope**, since it is not obvious: the 127 bests are **one run** (`runs/RBT-19/P-801`,
conventional and holistic) plus the seven W4b-801 bests under `docs/artifacts/`, which live there
because `runs/RBT-23/W4b-801` is committed nowhere (RBT-68, RBT-86).

## The decision

The pre-registration posted before this measurement ran said: *a rate of zero closes A on a
measured reason; a non-zero rate flips to B's positive control, with this rate as its baseline.*
**The rate is non-zero. So the decision flips**, and it flips on the rule rather than on a reading
of the numbers after the fact.

The reason A was declined-in-reverse is now measured rather than asserted: **structure arrives at
0.040% over this denominator, and one of the four arrivals is already at 92% of the realised
response of the first paying rung.** A compass is not far outside what drift proposes at the
depth this programme actually reaches; what it lacks is magnitude, and magnitude is exactly what
option B changes.

**What B now owes, unchanged from the ticket:** install nothing, evolve under the widened operator
on one seed, and show (i) the weight distribution reaches 16–32 in evolved links and (ii) the
proposal rate of gradient-correct motifs moves off **0.040%**, which is now a baseline rather than
a zero. One flag, never combined with another change in the same arm, and no arm runs under it
until that control has passed and been adversaried.

## Three things that cut against this decision, stated rather than buried

1. **"The first paying rung" is the source's number, and it did not replicate here.** RBT-69 ran
   the corrected motif on P-801 and found it **negative at every magnitude the source reports a
   gain at** (−0.328 at `w = 16`, −0.375 at `w = 32`, W4'-shaped), and the world was ruled out as
   the explanation. So reaching the magnitude may buy nothing on these populations. B's positive
   control is the thing that would settle that, which is an argument for running it — but nobody
   should read this decision as "a compass is about to appear".
2. **n = 4.** The rate is four lineages in ten thousand and the 92% figure is the maximum of four
   draws. The rate's confidence interval is wide and the document should not be quoted as though
   0.040% were precise.
3. **The predicate does not check that the sign is chemotactic.** It requires opposite-sign in and
   same-sign out, which is the motif's shape; whether a given arrival steers *toward* food depends
   on the individual's own direction of travel, and W4b-801's founders drive backward (RBT-80).
   Re-signing per individual is the measurement that would say how many of the four are compasses
   rather than anti-compasses, and it has not been done. Roughly half should be expected to be
   anti-compasses.

## Consequence for the held-out challenge protocol (RBT-89)

For **the unperceived challenges** — C1, C2 and C3 — "robust against novel challenges" means
**survivorship of standing morphology and gait through a shift**, not adaptation during it, and
the axis and the falsifier are claims about income, not perception. C4 is perceivable at `w ≈ 1`
and is reported apart. None of that changes under this decision: it is a statement about what the
*standing* populations can sense, and no challenge arm runs under a widened operator until B's
positive control has passed.
