# RBT-69: the antisymmetric compass, re-run on a second substrate

`scripts/compass_replication.py`, readouts in `RBT-69-compass-replication.txt` (RBT-19's own
world) and `RBT-69-compass-replication-w4.txt` (reshaped towards W4'). 13,440 bouts across
the two: 7 committed Pioneer bests from `runs/RBT-19/P-801`, 64 paired seeds, three
conditions, seven magnitudes, two worlds.

## Verdict

**The control replicates decisively. The headline gain does not replicate here.**

The common-mode motif — the same four links all one sign, the error RBT-61 made — behaves
exactly as RBT-61 and RBT-64 describe. At `w >= 2` it stops being a forager and becomes a
pirouette: displacement collapses from 2.00 m to 0.20 m, accumulated yaw rises from 2.28 to
2.96 turns, and yield goes from 2.770 items to 0.062, which is −2.708 ± 0.193 and 0 of 7
robots improved. That is about as clean a confirmation of the sign analysis as the harness
can give: the common mode really does land on the steering axis and destroy locomotion.

The antisymmetric motif — the compass — does **not** reproduce a +59% gain on this
substrate. It is null at low gain (+0.143 ± 0.195 items at `w = 1`, 4 of 7 robots) and
**negative** at exactly the magnitudes where the source reports its result (−1.154 ± 0.204 at
`w = 16`; −0.549 ± 0.245 at `w = 32`). The dose-response runs the opposite way: the source
reports a monotonic climb topping out at the largest gain it tried, and here yield falls
monotonically from `w ~ 1` upward.

## What this is not

It is **not** a refutation of the +0.897 figure on its own substrate, which cannot be
re-run from this repository at all. The source's own limitations section already restricts it
to "seven robots from one run, solo bouts." Two measurements on different populations
disagreeing is a limit on generality, not a contradiction — but see below: the obvious
explanation, that the worlds differ, has now been tested and does not hold.

What it does bear on is the broader claim — that the world rewarded chemotaxis "richly and
had done so throughout." This run is a counterexample to *throughout*. In this world, on
these robots, a correctly wired hand-installed compass earns nothing at any gain.

## Artifacts ruled out

A null is only worth reporting if the apparatus could have shown the effect. Three checks:

- **The nose is not saturated.** Over real bouts the wheel nose spans 0.168–0.860 with a
  median left-right gap of 0.056 (p95 0.086). RBT-22's concern about the summed squash
  flattening at high density does not apply here — and `log` is *worse* on this substrate
  (gap 0.039), so the gradient is real and `sum` carries more of it. This check is in the
  script and prints with every readout.
- **The motif mostly lands on a clean slate.** Four of the seven robots (generations 0, 100,
  200, 300) have *zero* pre-existing wiring out of either wheel nose, so the installed
  circuit is not fighting an evolved one. Three (400, 500, 590) carry some.
- **It is not tanh saturation at the effectors.** The obvious explanation for high gain
  hurting would be the drive commands pinning at the rail, and that is not what happens:
  0.1–1.0% of effector ticks exceed |0.99|, and the fraction *falls* as gain rises.

## The world is not the explanation

**An earlier version of this document hypothesised that the null came from RBT-19's world
being patchy and depleting, "rather than the baseline's instant regrowth at uniformly random
positions". That hypothesis was wrong on its premise and is now also refuted by test.**

The source's own script — `runs/sim-audit/verify_independent.py`, added by PR #5 — names its
substrate in its first lines: `runs/RBT-23/W4b-801`, generations 90-590, seeds 9000-9063.
That is **W4': 12 items and no regrowth at all**, which is *more* depleting than RBT-19's
patchy world with its 45 s delay, not less. The premise was simply wrong.

So the second arm reshapes RBT-19's config towards W4' — 12 items, no patches, no regrowth —
and re-runs everything (`world=w4`). The baseline moves to **1.219 items**, close enough to
the source's **1.516** that the world is approximately matched. The compass stays negative at
every magnitude the source reports a gain at:

| w | source Δ | this, W4'-shaped |
|---|---|---|
| 8 | +0.054 | — |
| 16 | +0.246 | **−0.328 ± 0.069**, 1/7 |
| 32 | **+0.897** | **−0.375 ± 0.077**, 3/7 |

Matching the world did not recover the gain. The common mode pirouettes here too (0.20 m,
0/7 at w >= 4), so the harness is behaving. **Whatever separates this result from the
source's, it is not the shape of the world.**

## What is left, and what would settle it

The remaining differences are the **robot population** (RBT-19's persistent-world lineage
against RBT-23's W4' lineage) and anything methodological not visible in the source's script.
The installation is not the difference: `install()` here and `verify_independent.py` write the
same four weights with the same signs at the same magnitudes.

A caveat that cuts against this document, not for it: RBT-19's robots are **off-distribution**
in a W4'-shaped world. They evolved somewhere else, so running them there could break whatever
a compass would otherwise augment, and that is a live alternative to "the population is what
differs".

What would settle it is running the motif on **RBT-23's own bests**. Those are not in the
repository — and neither is `runs/RBT-23/W4b-801` itself, which means `verify_independent.py`,
the script offered as the programme's independent verification of this number, **cannot be
executed by anyone from a fresh checkout**. That is RBT-68 blocking the check it most needs to
unblock.

Pending that, the defensible statement is narrow: **the instrument defect is confirmed; the
size and generality of the corrected prize are unestablished, and currently unestablishable
from the repository.**

## Notes on method

- The signs are never typed out. `install()` derives all four weights from
  `fixed.drive_commands(steering=..., throttle=0)`, so the script doubles as the worked
  example of the helper RBT-64 added.
- The crossed pair was not run separately: with the same sign it puts `w(n1 + n2)/2` on the
  steering axis, the same axis as the common mode at half the gain, so one control covers
  both. That is also why the source reports the crossed pair and RBT-64 reports the common
  mode with the same −1.502 figure.
- Everything here runs off committed artifacts, so it is reproducible from the repository
  alone: `python scripts/compass_replication.py 64 4 [native|w4]`, about ten minutes per
  world on four cores. That is the property the source's own verification script lacks.

## Resolution (coordinator, 2026-09-14)

The verdict above stands for this population, and the reason is now known. The two
substrates drive in opposite directions relative to the Pioneer's designed front
(`scripts/travel_direction.py`, on `claude/rbt-45-2oa635`): the seven `RBT-19/P-801` bests
used here drive **forward** (pooled travel azimuth minus body yaw +5.1°, six of seven within
±10°), and the seven `RBT-23/W4b-801` bests the +0.897 was measured on drive **backward**
(−174.1°, all seven). Nothing in a foraging ecology rewards nose-first over tail-first, so a
lineage's direction of travel is free and each lineage froze onto one arbitrarily.

An identical antisymmetric motif is therefore a compass for the W4′ population and an
anti-compass for this one, and the −1.154 at `w = 16` here is the same circuit as the +0.246
there with its sign inverted by the substrate. On its own substrate, now committed under
`docs/artifacts/RBT-23-W4b-801/`, the +0.897 reproduces to three decimals, is food-dependent
(a phantom-smell control collapses it to −0.071) and improves travel-frame bearing; it is
genuine chemotaxis. Neither measurement was wrong and the installation was never the
difference, as §"What is left" above narrowed it to.

Consequences, adopted as standing rules on RBT-69: measure direction of travel per population
(per generation, not per run) before installing any sensorimotor circuit; verify chemotaxis
in the travel frame, never against chassis yaw; the sign of a hand-installed circuit is a
property of the population, not the body. The patch-abandonment hypothesis in §"A hypothesis"
was refuted on its premise and by test before the direction-of-travel explanation arrived;
it is left in place per convention. Full chain on RBT-69 and PR #5.
