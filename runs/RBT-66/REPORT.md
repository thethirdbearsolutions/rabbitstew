# RBT-66: the taxonomy re-read on the real axes

`runs/RBT-66/axis_lesion.py`, readouts `docs/artifacts/RBT-66-{control,brake,throttle,sweep,throttle590,sweep-yield-null}.txt`.
Champions pulled by `runs/RBT-66/extract.sh`; nothing bulky committed. n = 64 paired seeds
everywhere, per the programme's standard since RBT-38.

**Pre-registration authorship.** The 12:21 pre-registration of 2026-09-14 was written by the
**RBT-84 delegate**, not by this session, and the resume wake misattributed it. It is run here
unchanged; its four point predictions are scored below as *its author's*, not mine.

## The finding: the taxonomy's instrument cannot adjudicate an axis

A free-running lesion — nose live against nose blanked, robot free to diverge — was the
evidence for all three labels. Against four hand-installed circuits of known axis and sign it
scores **2 of 4**, and it fails in one direction only:

| installed | free-running | frozen, peak over 8 |
|---|---|---|
| steering + | throttle **+0.354** (t +34.1) > steer +0.116 — **wrong axis** | steer +0.342 > thr +0.062 — right |
| steering − | throttle **−0.386** (t −64.4) > steer −0.183 — **wrong axis** | steer −0.587 > thr +0.077 — right |
| throttle + | thr +0.488 > steer +0.023 — right | thr +0.345 > steer +0.114 — right |
| throttle − | thr −0.500 > steer **+0.196 (t +25.6)** — right axis, spurious steer | thr −0.281 > steer −0.020 — right |

It is not uncertain about the steering circuits; it is **confidently wrong**, at t = +34 and
t = −64, the same way twice. The mechanism is asymmetric, which is why it survived: a steering
circuit turns the robot, the turn changes where it goes and what it smells, and the native
controller answers with a different throttle. That throttle difference is a real consequence of
the nose. It is not what the circuit *drives*.

**So a free-running lesion systematically reads steering circuits as throttle circuits.** The
pre-registered rule withdraws any label scored that way ("or the positive control fails").

### The instrument that does work

The pre-registration named two things and treated them as one: *"measure the realised
small-signal response"* and *"nose live against nose blanked on the same paired seed"*. Those
are different measurements and the control separates them. The **frozen-trajectory probe** is
the first: save the brain state, step it forward with the nose at its true value and again with
the nose zeroed, every other sensor held at its current reading, and read the difference per
axis. It isolates the circuit from the closed loop, and being finite by construction it is free
of the divergence that retired the depth-4 path sum (RBT-81). It scores 4 of 4.

Labels are scored on it. **Both instruments are reported for every champion**, because they
disagree on three of four and a reader should see it.

## Verdicts

| champion | label | verdict |
|---|---|---|
| baseline-801 g500 | **brake** | **OUT OF SCOPE** |
| RBT-19 g300 | **throttle** | **CONFIRMED** |
| RBT-10 802-free g590 | **sweep modulator** | **CONFIRMED** |

### brake — OUT OF SCOPE

*"a brake (the baseline's season-500 Pioneer, **kept in the disc by its noses**)"* (line 282),
and line 286: *"Every brake verdict in the table above also stands: each rested on **time inside
the disc and distance from the centre**."* That is where the robot ends up, not which axis is
driven. Recorded and untouched, as the rule requires.

Reported but **not** scored: frozen steer −0.119 (t −17.8), throttle **+0.083** (t +14.8),
|steer| > |throttle| paired +0.036 (t +12.3). Had it been in scope it would **not** have
confirmed — the throttle delta is *positive*, so the nose raises forward drive where "brake"
needs it lowered, and the steering axis carries more. It would have been RELABELLED.

### throttle — CONFIRMED

Frozen: throttle **+0.149** (t +8.44), correct sign; steer +0.080 (t +5.19); paired
|steer| − |throttle| = −0.062 (t −7.75), so throttle exceeds steer. All three clauses met.
Both instruments agree — exactly as the control predicts for a throttle circuit.

### sweep modulator — CONFIRMED, and the original evidence could not have established it

Frozen: steer **−0.190** (t −21.0), throttle +0.153 (t +17.3), paired |steer| − |throttle| =
+0.037 (t +8.40), so the signal is on steer as the label implies.

**The free-running instrument contradicts it** (throttle +0.189 beats steer −0.114, paired
t −7.15). The label is right; the evidence originally offered for it points the other way.
The load-bearing phrase turns out to be *"through the global neurons"* — the direct term is
**exactly 0.000**, every bit of this circuit is routed.

Its yield is a genuine null: mean food delta **exactly 0.000** over 64 paired seeds, and that
was recomputed on its own because a round number invites suspicion
(`RBT-66-sweep-yield-null.txt`). The nose moves yield on **38 of 64** seeds, by up to four items
either way, 17 up and 21 down, and the moves cancel. The nose is not inert; it is unprofitable.

### RBT-19 g590, not in the taxonomy, pulled for completeness

Frozen: steer −0.293 (t −40.3), throttle +0.416 (t +40.1), paired −0.123 (t −33.1). The
**largest axis signals of the four**, on the champion whose behavioural nose effect "evaporated
at 64 paired seeds". Driving an axis hard and earning food are different questions, and this
body separates them.

## Two errors in the document, found before any bout was scored

**1. "All three ride on the chassis nose alone; the wheel pair a Braitenberg circuit needs was
never wired in any arm"** (line 282) is **false for the brake**:

| champion | chassis | wheel L | wheel R | depth-1 `a` / `c` |
|---|---|---|---|---|
| baseline-801 g500 | 5 | **1** | **2** | **+0.861 / −0.861** |
| RBT-19 g300 | 6 | 0 | 0 | 0 / 0 |
| RBT-19 g590 | 4 | **1** | 0 | 0 / 0 |
| RBT-10 802-free g590 | 6 | 0 | 0 | 0 / 0 |

Both of the brake's wheel noses are wired, three links in total, and one reaches the drive
Effectors directly: `s_L = 0`, `s_R = −1.72`, the single-wired-nose signature (`|a| = |c|`,
RBT-78's calibration). Its frozen direct term confirms it from the other side — steer −0.033 =
−throttle +0.033, which is signal into the right Effector and none into the left.

The same claim appears again at line 288 (*"no Pioneer ever wired its two wheel noses into a
pairing, only the chassis nose into a gate"*). "Into a pairing" survives — the left nose's links
do not reach the drive Effectors — but "only the chassis nose" does not.

**2. Prediction 1 conflates absent with unwired.** `steering_terms` returns a **dict on all
four**, not `None`: it requires the wheel noses to *exist*, and they all do.

## The four point predictions (the RBT-84 delegate's)

| # | prediction | conf | outcome |
|---|---|---|---|
| 1 | `steering_terms` returns `None` on all three | 0.9 | **FALSIFIED** — dict on all four |
| 2 | brake scores OUT OF SCOPE | 0.6 | **HELD** |
| 3 | at least one label WITHDRAWN | 0.75 | **FALSIFIED as scored** — see below |
| 4 | at least one label RELABELLED | 0.35 | **FALSIFIED as scored** — the brake would have been, had it been in scope |

Prediction 3 deserves its own sentence, because it turns on the instrument. Scored on the
frozen probe, nothing is withdrawn. Scored on the free-running lesion — the instrument the
taxonomy actually used — the control failure withdraws **all three**. The prediction was right
about the original evidence and wrong about the corrected measurement, and both halves are
worth recording.

## Availability

RBT-10's 802 free-work Pioneer is **not** undecidable. It is at
`origin/claude/determined-shannon-2zb8jp:runs/RBT-10/forage-w0.0-802/conventional/best_gen0590.json`,
which `docs/foraging-world.md` line 111 names. All three champions regenerate from
`runs/RBT-66/extract.sh`.

## One architectural fact

Tick 1 of the frozen probe is exactly zero on every body. `Brain.step` computes
`x = W @ activation + bias`, applies the transfer functions, and *then* writes sensor readings
into the activation vector, so a reading taken at tick *t* cannot reach an Effector before
*t+1*. **A "direct" sensor→Effector link is a two-tick path here.** RBT-81's and RBT-87's
"depth-1 term" is one multiply by `W`, which is this tick-2 output; the conventions agree on the
arithmetic and could be read as off by one.

## What I would attack if I were the adversary

- **The frozen probe holds the non-nose sensors fixed** over its horizon. That is what makes it
  a circuit measurement rather than a behavioural one, but a sensor stream that would really
  have changed is held still, so the 8-tick figure is a counterfactual, not a replay.
- **Peak-over-8 is a summary** and could be hiding sign changes within the horizon. *(Amended
  after the adversary's round: it is not, and the corroboration I claimed here does not exist —
  see "What the adversary established" below.)*
- **The control is on one body.** RBT-45's calibration found the same circuit delivering nominal
  gain on five of seven robots, double on one and sign-reversed on one; a four-circuit control
  on one Pioneer does not exclude that.
- **"Out of scope" is a judgement about a sentence**, not a measurement. I quoted the two lines
  that make the brake behavioural, and a reader who thinks line 282 makes it mechanistic would
  score it RELABELLED instead — the numbers for that are above, deliberately.

## What the adversary established, and three amendments to this report

The RBT-45 delegate attacked this package twice (PRs #47 and #49) and **no verdict moved**. The
horizon of 8 is not load-bearing (constant from h = 4 to h = 64, asymptotic rather than
reversing); the verdicts are small-signal (identical across three decades of lesion scale);
Effector output clipping never fires (0 of 38,400 probe-ticks); the instrument reproduces digit
for digit; and the control now holds **16 of 16** across all four champion bodies rather than
only the one it was calibrated on. Three corrections are owed, and one addition.

**A. "Tick 2 and the peak agree on the axis for every champion" was wrong, and the verdicts rest
on the peak column alone.** Tick 2 adjudicates *nothing* on these champions: exactly `0.000` on
three of four, and on the brake an **exact tie** — `|steer| = |throttle| = 0.03284` — because one
wired nose into one Effector puts identical magnitude on both axes *by construction*. The two
readings cannot corroborate each other; one is silent. What carries the verdicts is the peak
column on its own, and what justifies leaning on it is its control (4 of 4 on the calibration
body, 16 of 16 across all four) together with its insensitivity to horizon and lesion scale —
not a second witness, because there isn't one.

**B. The rule's second clause is a sign test, not an effect-size test.** Exactly, and verified
here to 4.4e-16 over 200,000 random pairs:

> `|steer| − |throttle| = sign(ΔL · ΔR) · min(|ΔL|, |ΔR|)`

Its *sign* is the two Effectors' sign agreement; its *magnitude* is the weaker Effector's
response and nothing else. So `|t| ≥ 2.5` on that clause tests **sign consistency across seeds,
not effect size**. This is the same shape as the `|a| > |c|` test RBT-81 retired, reintroduced on
a different pair of quantities. It overturns nothing — which axis a circuit drives *is* a sign
question, and the gate can shrink the margin toward a tie but cannot flip the sign, so the bias
is conservative — but the clause should be read as what it is.

**C. `a` and `c` mean different things in the ticket and in the instrument.** The ticket writes
`a` = steering and `c` = throttle. `rabbitstew.analysis.steering_terms` writes `a` = the gradient
across the two wheel noses and `c` = their common mode, and since it sums both Effectors **both
of its terms live on the steering axis and it has no throttle channel at all**. On the brake this
report's steering axis equals `steering_terms`' `c`. Nothing here mixes them; the warning is for
the next reader, and RBT-87 is open on that docstring.

**Addition: the probe recovers the axis and the sign, and does not recover the magnitude.** On
the brake, tick 2 per unit of sensor converges to −0.0357 against a one-multiply −0.86117, a
factor of **24**, and it does not resolve in the small-signal limit. It is not the output clip
(which never fires) but the `tanh` on the Effector unit itself: every Effector is `tanh`, so a
perturbation arrives multiplied by `1 − a²`, and across these four bodies the median factor runs
from 0.007 to 0.98. **No number in `docs/artifacts/RBT-66-*.txt` should be quoted as a gain.**
The axis and sign verdicts are unaffected, which is exactly what the sign-test identity in (B)
predicts: `sign(ΔL · ΔR)` survives any per-side attenuation.

**And one correction to this report's own mechanism sentence.** It says *"a throttle circuit does
not leak into steering nearly as hard"*. The direction is right — three of the four free-running
misses across the four bodies are steering read as throttle — but the leak is **not one-way**: on
the sweep body a `THROTTLE +` circuit is read as `steer +`. The asymmetry is a tendency, not a
rule, and an instrument built on free-running lesions can misread either axis.

## Reproduce

```
bash runs/RBT-66/extract.sh
python runs/RBT-66/axis_lesion.py control 64
bash runs/RBT-66/run_champions.sh
```
