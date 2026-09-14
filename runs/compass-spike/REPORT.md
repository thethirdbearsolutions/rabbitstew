# Compass spike: would a Braitenberg circuit earn anything if the robot simply had it?

**Unticketed.** Run as lead researcher while the coordinator was away, at the user's
request. Not reviewed by anyone. It needs a ticket number if it is kept.

## The question, and why it is the one worth a spike

RBT-45 measured what the *search* does: the crossed pairing is proposed in about 1%
of realistic lineages, and at the default operator it can never rise much above 15%
because drift eats the global brain the circuit must route through. That says
nothing about whether the circuit is worth having. Ten world arms failed to make
sensing pay and every nose that looked useful has evaporated under a proper lesion,
so before anyone spends a 600-season run widening the operator (RBT-42), the cheap
binary question is:

> If a Pioneer simply **had** the circuit, would it eat more?

This needs the world but not evolution. An evolved mower is taken as-is, the compass
is installed by hand straight into the live weight matrix (`W[dst, src]`, exactly
where `brake_or_compass.py` blanks), and the same robot runs with and without it on
the same food layout from the same start.

## Method

| | |
|---|---|
| Robots | RBT-23's conventional bests at seasons 90, 190, 290, 390, 490, 550, 590 (7 individuals) |
| World | that run's own `SimConfig` — 12 items, 3 m disc, no regrowth, eat radius 0.35, smell decay 1.0, 15 s |
| Seeds | **64 paired** — same food layout and start for every condition (RBT-38/39's rule; never 8–16) |
| Unit of analysis | the **robot**, not the bout; every interval bootstraps over the 7 individuals (RBT-45 §6.5) |
| Bouts | 7 × 64 × 32 conditions = 14 336, solo, 1237 s |
| Selection | none anywhere; no breeding, no seasons, no ranking |
| Library changes | none |

**Conditions.** `crossed` installs nose(wheel 1) → effector(wheel 2) and
nose(wheel 2) → effector(wheel 1) — the Braitenberg circuit. `uncrossed` installs
each nose into its own wheel. `sham` installs the crossed topology but sources it
from the wheels' `joint_velocity` sensors instead of their noses: same added drive,
no smell in it. Each at magnitudes 0.5, 1, 2, 4, 8 in **both signs**, since the
motor convention could run either way. `blanked` is the standard reference.

The spike is deliberately **generous to the compass** — both signs, five magnitudes,
best variant allowed to be chosen. To stop that generosity manufacturing a winner,
the seeds are split: the best crossed variant is chosen on 32 seeds and its effect
reported on the 32 it never saw.

Context: baseline solo yield is **1.52 items** per bout (range 1.20–1.70 across the
seven robots), so a compass worth having should move that appreciably.

## Result: nothing, at any setting, and harm at every setting that does anything

| condition | Δ items | 95% CI | condition | Δ items | 95% CI |
|---|---|---|---|---|---|
| blanked | −0.036 | [−0.225, +0.141] | | | |
| crossed +0.5 | **+0.020** | [−0.098, +0.138] | crossed −0.5 | −0.049 | [−0.217, +0.107] |
| crossed +1.0 | −0.011 | [−0.145, +0.105] | crossed −1.0 | −0.132 | [−0.279, +0.036] |
| crossed +2.0 | −0.301 | [−0.578, −0.062] | crossed −2.0 | −0.458 | [−0.699, −0.239] |
| crossed +4.0 | −0.875 | [−1.250, −0.462] | crossed −4.0 | −0.699 | [−1.018, −0.415] |
| crossed +8.0 | −1.446 | [−1.567, −1.279] | crossed −8.0 | −1.377 | [−1.551, −1.163] |

**No crossed setting earns anything.** The best of the ten is +0.020 items with an
interval straddling zero. Below magnitude 2 the circuit is free but inert; from 2
upward it is actively costly, and at 8 it removes −1.45 of the 1.52 items the robot
was eating — it very nearly abolishes foraging.

**Held out, to kill the multiple-comparison objection.** The best crossed variant on
the first 32 seeds was `crossed−0.5` at +0.031 [−0.183, +0.250] — already null. On
the 32 seeds it had never seen it scored **−0.129 [−0.344, +0.067]**. Per robot:
0.00, +0.28, −0.09, −0.66, +0.06, −0.19, −0.31. The best variant does not even
replicate as positive.

**Blanking the noses does nothing** (−0.036, CI spanning zero), replicating the
programme's standing finding on a 7-robot × 64-paired-seed design.

### Crossing makes no behavioural difference

RBT-45's coordinator added the crossed/uncrossed split because "a Braitenberg
circuit that steers toward food is the crossed one". Structurally that was right and
the rates differ sixfold. Behaviourally the distinction is void:

| magnitude | crossed − uncrossed (+ sign) | (− sign) |
|---|---|---|
| 0.5 | +0.083 [−0.013, +0.174] | +0.025 [−0.118, +0.165] |
| 1.0 | −0.004 [−0.098, +0.094] | +0.109 [−0.031, +0.239] |
| 2.0 | +0.060 [+0.018, +0.096] | −0.018 [−0.114, +0.069] |
| 4.0 | −0.062 [−0.105, −0.013] | −0.016 [−0.092, +0.047] |
| 8.0 | +0.038 [+0.009, +0.069] | +0.007 [−0.033, +0.062] |

Every contrast is inside ±0.11 and the three that exclude zero are tiny and
inconsistent in sign. **On this body, wiring the noses across is worth no more than
wiring them straight.**

### The sham control, and where it is imperfect

At magnitude 8 the crossed circuit is *worse* than sham (−0.52 [−0.58, −0.46]), so
the damage there is not merely "you added drive". But at magnitudes 1–2 crossed is
markedly *better* than sham (+0.43, +0.66), which says the sham is a harsher control
than intended: `joint_velocity` is a fast feedback signal and injecting it crossed
builds an unstable loop, where the food signal is slow and acts more like a bias.
So sham over-states the damage attributable to any-signal-at-all. **This does not
rescue the compass** — crossed still never beats baseline — but the clean claim is
"a bolted-on compass earns nothing", not "all the harm is generic".

## What this does and does not license

**Does.** On the Pioneer, in this world, a Braitenberg compass handed to a finished
mower for free earns nothing. There is no magnitude window where it carries useful
information without disturbing the gait: weak is inert, strong is destructive, and
nothing in between steers. That is not a cliff with a chasm — it is a **flat plain
and then a downhill.** There is no gradient for selection to climb even when the
wiring is present, which is a sharper statement of why sensing never evolved than
any of the ten world arms produced, and it is consistent with RBT-45's finding that
HALF sits unpunished at 0.217: at the strengths drift actually delivers (median pair
influence ≈ 0.96, RBT-45 §6.2) the link is in the inert zone, costing nothing and
doing nothing.

**Does not.** Three limits, and the first is serious.

1. **No co-adaptation.** I bolted a circuit onto a finished controller. Evolution
   would tune the rest of the gait around a new link. This answers "does a compass
   bolted onto a finished mower pay?" — no — and not "could a co-adapted compass
   pay?" That is the main escape hatch and it should be said plainly. It also cuts
   both ways: if a compass pays *only* when co-adapted, then it is not reachable one
   mutation at a time, which is the cliff located precisely — not in the wiring,
   which drift supplies at 9%, but in the **simultaneous gait compensation**.
2. **One topology.** I tested the literal Braitenberg circuit, a direct nose →
   opposite-effector link. The nose behaviours that *do* appear in this programme
   run through the global brain at influence 200–500, not direct links. "Direct
   crossed link does not work" is not "no compass architecture works."
3. **One body, one world, solo.** Pioneer only, RBT-23's W4b world only, one robot
   per arena rather than the ecology's four.

## What it means for the filed tickets

I am reasoning from how RBT-42 and RBT-46 were described in RBT-45's thread, not
from having read them; treat this as a flag for their owners rather than a verdict.

- **RBT-42** (widen the operator) rests on proposal rate being the binding
  constraint. RBT-45 said that is true for the crossed circuit specifically. This
  spike says the circuit is not worth proposing: get the crossed rate to 50% and you
  have installed something that earns nothing and, above magnitude 2, starves the
  robot. **The run should not be spent on the strength of RBT-45 alone.**
- **RBT-46's B1** gates on a non-zero crossed rate with RBT-42's operator. That
  condition is still met (RBT-45: 0.0105 ± 0.0036 at realistic depth). It is now
  clearly necessary-but-insufficient, and B1 as written would pass on a circuit this
  spike says is worthless.

The question I would put next, if anyone spends compute here, is the co-adaptation
one, because it is the only surviving route: *hold a crossed circuit fixed in the
genotype and let the rest of the controller evolve around it for a few hundred
seasons.* That is a real run, not a spike, and it is the one experiment that could
still say yes.

## Files

| file | what |
|---|---|
| `spike.py` | the whole thing; `--seeds N` |
| `spike.json` | all 14 336 bouts and the summaries |
| `spike.log` | run log |

```
./v/bin/python runs/compass-spike/spike.py --seeds 64 --workers 4   # ~21 min
```
