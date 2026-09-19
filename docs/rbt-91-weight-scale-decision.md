# RBT-91: the weight-scale ceiling — decision

**Decision, as restated 2026-09-19 after the two drift-form measurements: option A, on a measured
reason. The structure is proposed, the magnitude is reached by drift, and neither is what
withholds a compass.**

This is the second restatement. The first version chose A on an *asserted* reason and was wrong
about it; the second flipped to B on a pre-registered rule when the structural rate came back
non-zero; this one returns to A on the rule that version pre-registered in turn, after the
measurements the coordinator assigned. Each reversal is recorded below rather than edited away.

## What the three measurements say, at 200,000 lineages per condition

| | baseline `σ = 0.4` | widened `σ = 1.6` |
|---|---|---|
| structural arrivals | **84** of 200,000 (**0.042%**) | 63 of 200,000 (0.032%) |
| chemotactic, re-signed per individual | **36 of 84 = 42.9%** [32.8, 53.5] | 26 of 63 = 41.3% [30.0, 53.6] |
| compasses reaching the realised paying rung | **2 of 36** | 2 of 26 |
| **net: chemotactic AND paying** | **2 in 200,000** | **2 in 200,000** |

**Widening the weight scale four-fold moves none of it.** The structural rate is nominally lower
(z = 1.73, two-sided p = 0.083 — *not* resolvable, so the surprise case I pre-registered did not
fire, though the direction is down and worth a second look if anyone widens further). The
chemotactic fraction is unchanged. The conditional fraction P(realised |a| ≥ rung | structure) is
4.8% [1.9, 11.6] against 6.3% [2.5, 15.2] — overlapping, and at four arrivals apiece the design
resolves only a large move. **The net rate is identical: two lineages in two hundred thousand,
both ways.**

**The pre-registered prediction held.** I predicted, at confidence 0.6, that widening would not
raise the conditional fraction, because `weight_sigma` drives **both** the link-weight step and
the unit-bias step (`genetics.py` 105 and 108) and biases have no reset, so widening it widens the
bias walk and collapses the `sech²(b)` that multiplies the whole gain. It did not raise it.

**So the pre-registered rule returns the decision to A**, and for the first time on a reason that
is measured rather than asserted: *structure is proposed, magnitude is reached by drift, and
neither is what withholds a compass.*

## The open question this leaves, named rather than buried

If neither barrier withholds it, something else does, and **the candidate on the record is that
the compass does not pay on these populations at all.** RBT-69 installed the corrected motif on
P-801 and measured it **negative at every magnitude the source reports a gain at** — −0.328 at
`w = 16`, −0.375 at `w = 32` — with the world ruled out as the explanation. The "first paying
rung" this document scores against is the *source's* number, on the source's substrate, and it
did not replicate here. **That is now the question RBT-91 hands on**: not whether drift can
propose a compass, which it demonstrably can, but whether a compass is worth anything to these
robots. No widening of any operator answers that.

## The re-signing, which is why the arrival rate is not the compass rate

`structural_rate.py` counts the motif's **shape**. Shape is not direction: a circuit steers
*toward* food only if its sign agrees with the way its robot actually drives, and W4b-801's
founders drive backward (−174°), so a descendant driving forward needs the opposite sign to be
chemotactic (RBT-80). Re-signed per individual against its own measured direction of travel,
**36 of 84 arrivals are compasses and 48 are anti-compasses**.

At the first four arrivals this read 1 of 4, and the single compass had a realised gain of
+0.0008 while the largest arrival — −6.33, which an earlier version of this document reported as
"92% of the first paying rung" — turned out to steer the **wrong way**. At n = 84 the fraction is
42.9%, near the coin-flip the mechanism implies, and the 1-of-4 was small-sample noise. Both
readings are recorded because the first one was published.

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

## The 16:21 flip to B, and why it is withdrawn

The measurement at n = 10,000 gave a structural rate of 0.040%, and the pre-registration in force
then said a non-zero rate flips to B. It flipped, correctly, on the rule. Two things then came in
that the rule could not have known: the arrivals are **43% chemotactic, not all of them**, and
**widening the operator moves nothing**. The second is what withdraws the flip, by the rule
pre-registered before *it* ran. The first is what deflates the headline that made the flip look
exciting — "92% of the first paying rung" was an anti-compass.

**B is not refused on cost any more.** It is refused because the thing it changes has been
measured and does not change the outcome.

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
