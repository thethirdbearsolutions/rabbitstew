# RBT-91: the weight-scale ceiling — decision

**Decision, as restated 2026-09-19 after the corrected measurement: option A. Structure is
proposed by drift; the motif's own magnitude is never reached, at any weight scale tested; and
widening the weight scale does not relieve it, because what it inflates is the recurrent
background and not the circuit. RBT-97 is not warranted.**

This is the third and final restatement. The ticket has read A (asserted), then B (on a
pre-registered rule), and now A again (on a measurement). Every reversal is below with its date
and what it replaced, because two of them were mine to make and the reasons differ.

## The corrected measurement: the motif's OWN response, not the whole brain's

The quantity every earlier version of this document scored against was the **whole brain's**
small-signal response. That is not a property of the motif. On the arrival this document once
called *"92% of the first paying rung"*, the predicate unit's four links **alone** read
**+0.0036** while the whole brain read −6.33: the recurrence was doing the work. The adversary
found this; the corrected quantity is theirs.

200,000 lineages per condition, `--background 5000` per pool:

| `weight_sigma` | structural arrivals | **links alone ≥ rung** | whole brain ≥ rung | structureless background |
|---|---|---|---|---|
| **0.4** (default) | 84 (0.042%) | **0 of 84** — 0.0% [0.0, 4.4] | 4 of 84 (4.8%) | 26 / 9,996 = **0.26%** |
| **1.6** (pre-registered widening) | 63 (0.032%) | **0 of 63** — 0.0% [0.0, 5.7] | 4 of 63 (6.3%) | 141 / 9,995 = **1.41%** |
| **4.0** (ten× default, post hoc) | 66 (0.033%) | **0 of 66** — 0.0% [0.0, 5.5] | 4 of 66 (6.1%) | 164 / 9,994 = **1.64%** |

**Not one drift-proposed motif's own circuit reaches the paying rung, at any weight scale
tested.** 0 of 84, 0 of 63, 0 of 66. The links-alone median is 0.0000 at both widened scales; the
largest is 3.91 against a rung of 6.87.

**And the widening proves the whole-brain column was background.** As `σ` goes 0.4 → 4.0 the
**structureless** background rises **0.26% → 1.64%**, six-fold, while the whole-brain conditional
fraction sits flat at 4.8 → 6.3 → 6.1%. Widening pumps the recurrent gain of brains that carry no
motif at all. The enrichment over background is real (18× at 0.4, 3.7× at 4.0) and it is **not
the motif's links**, which deliver zero — so it is a correlate: lineages that acquire the
structure are lineages with denser wiring, which have more recurrence.

**The pre-registered prediction held, and more strongly than it was made.** I predicted at
confidence 0.6 that widening would not raise the conditional fraction, because `weight_sigma`
drives **both** the link-weight step and the unit-bias step and biases have no reset. It did not
raise it at 1.6, and it did not raise it at 4.0 either.

## What this withdraws

**"The magnitude is not far away" is withdrawn in full.** It rested on the whole-brain response
of four arrivals, and the whole-brain response is not the circuit's. The corrected reading is the
opposite: **magnitude is the barrier that binds**, the motif's own links never reach the rung, and
**the operator change designed to relieve it does not**.

**"Magnitude is reached by drift"** — the clause in the outcome text pre-written for this branch —
**is false and is not used.** The outcome (A) is the one the rule selects; its stated reason is
corrected here.

**Three of the four original arrivals descend from one parent** (`ce556`, adversary's §2), so the
n = 4 that produced the flip was nearer n = 2 independent draws.

## What still stands

**Structure is proposed** — 84 in 200,000 at the default operator, against the "0 of 10,000"
cited before this ticket, which measured a column that is zero by construction. And **43% of
arrivals are chemotactic** (36 compasses, 48 anti-compasses at n = 84), so the arrival rate is
not the compass rate. The single-weight ceiling is unchanged; both are below.

## RBT-97 is not warranted

B's positive control exists to show that a widened operator moves the proposal rate of usable
motifs. That has now been measured directly, at two widenings including one ten times the
default, and it moves nothing: the primary is zero everywhere. **B is not refused on cost. It is
refused because the thing it changes has been measured and does not deliver what it is for.**

## The open question this hands on, which is not a weight-scale question

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

## The predicate and the denominator, unchanged throughout

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

## The single-weight ceiling, and the census

Measured in the first version and untouched by anything since.

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
