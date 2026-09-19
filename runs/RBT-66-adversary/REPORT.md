# RBT-66 adversary pass

Named adversary: the RBT-45 delegate, who filed RBT-66. Work done in a fresh worktree of the
integration head `011567c`, which carries PR #42. Every number below is re-derived from the
committed readouts or from the champions `runs/RBT-66/extract.sh` pulls; nothing is quoted
from the ticket.

**Nothing I found changes a verdict.** The three labels stand as reported: brake OUT OF
SCOPE, throttle CONFIRMED, sweep modulator CONFIRMED. Four separate attempts to break them
failed, and the failures are worth more than the attempts, so they are reported first.

## What I could not break

**1. The instrument reproduces exactly.** `runs/RBT-66/axis_lesion.py` re-run on the same
seeds returns the committed per-seed values digit for digit. `extract.sh` pulls all three
champions from the three branches it names, with no manual step.

**2. The yield null re-derives exactly** (coordinator's line 4). From the 64 integers
committed in `docs/artifacts/RBT-66-sweep-yield-null.txt`: n = 64, sum = 0, mean = 0.000000,
sd = 1.3916, 38 nonzero (17 positive, 21 negative), largest |delta| = 4. Every figure in the
report matches. "Not inert, unprofitable" is the right reading of it.

**3. The horizon of 8 is not load-bearing** (coordinator's line 1). I re-ran the frozen probe
with the horizon opened to 64 ticks — 1.28 s of held sensors, eight times the published
window and eighty-five times the direct path length — and derived every horizon from the same
trajectories (`horizon.py`, n = 64 paired seeds, the same seeds):

| champion | h=3 | h=4 | h=8 (published) | h=16 | h=32 | h=64 |
|---|---|---|---|---|---|---|
| brake | steer − | steer − | **steer −** | steer − | steer − | steer − |
| throttle (g300) | throttle + | throttle + | **throttle +** | throttle + | throttle + | throttle + |
| sweep | steer − | steer − | **steer −** | steer − | steer − | steer − |
| g590 (unscored) | steer + | throttle + | throttle + | throttle + | throttle + | throttle + |

The axis and its sign are constant from h = 4 to h = 64 on all four, and the readings
asymptote rather than reverse — the "what happens past the horizon" question resolves in the
instrument's favour. The verdict also survives changing the *summary*: mean over ticks 2..h,
and each axis at its own argmax, give the same winner as the published peak-joint argmax.

**4. The verdicts are small-signal properties, not artifacts of blanking.** The probe zeroes
the nose outright, and everything on the path is `tanh`, so I expected a large-signal
artifact — this is the defect RBT-81's adversary found in their own drive value and fixed
with "halve the drive until the reading stops moving". I scaled the lesion instead of
blanking it, `r → r(1−k)`, and divided by k (`small_signal.py`, n = 16):

| k | 1.0 (published) | 0.5 | 0.1 | 0.01 | 0.001 |
|---|---|---|---|---|---|
| brake | steer − | steer − | steer − | steer − | steer − |
| throttle | throttle + | throttle + | throttle + | throttle + | throttle + |
| sweep | steer − | steer − | steer − | steer − | steer − |

Winner and sign identical at every scale across three decades. My hypothesis was wrong.

**5. Effector output clipping never fires.** `effector_output` clips to ±1, which would zero
a perturbation on a saturated side. Measured at the verdicts' own probe points: **0 of 38,400
probe-ticks clipped**, on any side, on any of the four champions. Also wrong.

## The two-tick convention (coordinator's line 3) — checked, and the tickets agree

`one_multiply.py`, on the brake genome, which is the only champion with a direct nose →
Effector link:

| | steering | throttle |
|---|---|---|
| one multiply, `W[e_L, n]` and `W[e_R, n]` read off the matrix | −0.86117 | +0.86117 |
| `steering_terms(ph, depth=1)`: `s_L = 0`, `s_R = −1.72235` → on `(L+R)/2` | −0.86117 | — |
| frozen probe, tick 1 | **0.000000** | **0.000000** |
| frozen probe, tick 2 | −0.0146 to −0.3836 | +0.0146 to +0.3836 |

Tick 1 is exactly zero, as the report says, and **tick 2 agrees with one multiply in sign and
in which Effector carries the signal**. RBT-81's and RBT-87's "depth-1" and RBT-66's "tick 2"
are the same one multiply. The two tickets are not off by one.

**What does not agree is the magnitude, and that does not go away in the small-signal limit.**
Tick 2 divided by the sensor delta converges to −0.0357 as k → 0, against a one-multiply
prediction of −0.86117: a factor of **24**, on a genome where the weight is known exactly. The
cause is not the output clip (§5 above) but the `tanh` on the Effector unit itself —
`Brain.__init__` gives every Effector `tanh`, so a perturbation arrives multiplied by
`1 − a²` at the operating point. Measured at the verdicts' probe points (`attenuation.py`,
n = 16):

| champion | left `1−a²` median | right `1−a²` median | min/max of the two, median | fraction of ticks below 0.5 |
|---|---|---|---|---|
| brake | 0.1034 | 0.0148 | 0.054 | 0.84 |
| throttle (g300) | 0.7367 | 0.0274 | 0.040 | 0.93 |
| sweep | 0.0436 | 0.0068 | 0.008 | 0.95 |
| g590 (control body) | 0.9779 | 0.1247 | 0.128 | 0.76 |

This is the same conclusion RBT-81's adversary reached about the depth-1 term by a different
route: **the instrument recovers the axis and the sign, and does not recover the magnitude.**
No number in `docs/artifacts/RBT-66-*.txt` should be read as a gain.

## Three corrections, none of which moves a verdict

**A. "Tick 2 and the peak agree on the axis for every champion" overstates the agreement.**
The report offers this as corroboration. Tick 2 adjudicates **nothing** on any champion: it is
exactly 0.000 on three of four (no direct wiring at all) and on the brake it is an exact tie —
`|steer| = |throttle|` to five places, paired difference −0.00000 at t = +0.27 — because one
wired nose reaching one Effector puts identical magnitude on both axes by construction. The
two readings cannot agree or disagree; one of them is silent. The verdicts rest on the
peak column alone. That column is validated (the control recovers 4 of 4 on it, and §3–§4
above show it is insensitive to the horizon and to the lesion scale), so the verdicts stand —
but the corroboration claimed for them is not there. Worth noting that tick 2 is a working
instrument, not a broken one: on the control body's *installed* direct circuits it resolves
all four, and on that same body's native nose it correctly reads 0.000.

**B. The verdict rule's second clause is a sign test.** `|steer| − |throttle|` is not a
magnitude comparison. With steering `(L+R)/2` and throttle `(L−R)/2`, exactly:

    |steer| − |throttle| = sign(ΔL · ΔR) · min(|ΔL|, |ΔR|)

verified to 4.4e-16 over 200,000 random pairs. So the clause's **sign** is `sign(ΔL·ΔR)` and
its **magnitude** is the weaker Effector's response and nothing else. This is the same shape
as the `|a| > |c|` test RBT-81 retired — *"the sign test `s_L·s_R < 0` with no magnitude in it"* —
reintroduced on a different pair of quantities without anyone noticing. The rule's `|t| ≥ 2.5`
threshold is therefore a test of *sign consistency across seeds*, not of effect size: it will
pass on an arbitrarily small effect that is consistently signed. It explains the readouts too —
the axis deltas run 0.1–0.4 while the clause that separates them runs 0.02–0.06, because the
asymmetric `tanh` gate in the table above crushes `min(|ΔL|, |ΔR|)` specifically.

This does not overturn anything. Which axis a circuit drives *is* a sign question, and the
gate asymmetry cannot flip `sign(ΔL·ΔR)` — it can only shrink the margin toward a tie, which
is conservative. But the clause should be described as what it is.

**C. `a` and `c` mean different things in the ticket and in the instrument.** RBT-66's
description assigns `a` to the steering axis and `c` to the throttle axis. `steering_terms`
assigns `a` to the gradient *across the two wheel noses* and `c` to their common mode — and
`onto_steering` sums both Effectors, so **both of its terms live on the steering axis and it
has no throttle channel at all**. On the brake the probe's steering axis equals
`steering_terms`' `c` (−0.861), the letter the ticket gives to throttle. Nothing in RBT-66 is
wrong because of it — the report never mixes them — but the collision is a live trap for the
next reader, and RBT-87 is already open on that docstring.

## On CONFIRMED for the sweep modulator (coordinator's line 2)

The coordinator asks whether a label whose own original evidence contradicts it should be
called confirmed, or relabelled-by-instrument. My answer: **CONFIRMED is right, and the report
is right to say so in the same breath as the contradiction.**

The pre-registration fixed the rule before the data, and it scores the label against the
world, not against the argument that first produced it. The label says the circuit acts on
the sweep — the steering axis — and on the instrument that passes its control, it does, at
t = −21.0, at every horizon from 4 to 64 and at every lesion scale down to 0.001. A rule that
demoted a correct label because its original evidence was bad would be scoring provenance,
and the programme has a better place to put that fact: the report already records it, twice,
in the verdict line itself.

The honest asymmetry is this. The label is confirmed; the *reasoning* that produced it is
withdrawn, because the free-running lesion that produced it reads steering circuits as
throttle circuits. Those are separable and both belong in `docs/foraging-world.md`. Whoever
first wrote "sweep modulator" was right for a reason they could not have had.

## What I did not test

- **The control is still on one body.** The report names this itself. RBT-45's calibration
  found the same circuit delivering nominal gain on five robots of seven, double on one and
  sign-reversed on one; four circuits on one Pioneer does not exclude that, and my
  attenuation table shows the four bodies differ by 20× in how much of a perturbation
  survives. Installing the control circuits on the other three champions is the test, it is
  cheap, and it is not done here.
- **"Out of scope" for the brake is a judgement about a sentence.** I agree with it on the
  two lines quoted, and I note the report deliberately publishes the numbers for the other
  reading.
