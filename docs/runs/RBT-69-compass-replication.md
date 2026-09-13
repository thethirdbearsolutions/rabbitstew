# RBT-69: the antisymmetric compass, re-run on a second substrate

`scripts/compass_replication.py`, readout in `RBT-69-compass-replication.txt`.
6,720 bouts: 7 committed Pioneer bests from `runs/RBT-19/P-801`, 64 paired seeds, three
conditions, seven magnitudes.

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

It is **not** a refutation of the +0.897 figure on its own substrate. Different robots, a
different world, and the source's own limitations section already restricts it to "seven
robots from one run, solo bouts." Two measurements on different substrates disagreeing is a
limit on generality, not a contradiction.

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

## A hypothesis, not a finding

The high-gain compass makes robots travel further while eating less — displacement rises
2.00 m → 4.38 m at `w = 32` as yield falls. RBT-19's world is patchy (3 patches, 45 s regrow
delay) rather than the baseline's instant regrowth at uniformly random positions. A circuit
that chases the global smell gradient may pull a robot *between* patches, out of ground it
was already harvesting — which would make a compass pay in an instant-regrow world and not
in a depleting patchy one. That is consistent with this family's recurring result that the
nose that works is a brake rather than a compass, but the mechanism is **not** established
here and would need its own arm.

## Notes on method

- The signs are never typed out. `install()` derives all four weights from
  `fixed.drive_commands(steering=..., throttle=0)`, so the script doubles as the worked
  example of the helper RBT-64 added.
- The crossed pair was not run separately: with the same sign it puts `w(n1 + n2)/2` on the
  steering axis, the same axis as the common mode at half the gain, so one control covers
  both. That is also why the source reports the crossed pair and RBT-64 reports the common
  mode with the same −1.502 figure.
- Everything here runs off committed artifacts, so it is reproducible from the repository
  alone: `python scripts/compass_replication.py 64 4`, about ten minutes on four cores.
