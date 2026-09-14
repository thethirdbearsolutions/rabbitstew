# RBT-58: the pre-registered compass criterion is met, and the compass claim is false

`ce861`, RBT-16's season-590 Pioneer, read at **256 paired seeds** against the criterion fixed on
this issue before the run. Branch `claude/rbt-lowest-unclaimed-ticket-tp6zdu`. Raw output in
`compass_256_abs.txt`.

## The criterion, as pre-registered, is met

> Primary: nearest-item distance while in the disc, intact minus noses blanked. Compass if
> |t| ≥ 2.5 and the 95% interval excludes zero.

| channel | intact | blanked | difference | t |
|---|---|---|---|---|
| **nearest-item distance** | 0.945 m | 0.993 m | **−0.048** | **−3.60** |
| items | 3.086 | 0.168 | +2.918 | +17.63 |
| items per in-disc metre | 0.751 | 0.075 | +0.615 | +19.95 |
| items per cell of new ground | 0.406 | 0.072 | +0.289 | +14.45 |
| in-disc path | 4.111 m | 2.234 m | +1.877 | +12.53 |
| distinct cells swept | 7.605 | 2.328 | +5.277 | +21.70 |
| fraction of time in the disc | 0.537 | 0.999 | −0.462 | −22.96 |

t = −3.60 against a bar of 2.5, interval [−0.074, −0.022], and items per metre rises. **By the
letter of the pre-registration this is a compass.** My pre-registered expectation was that it
would cross, and it crossed.

## It is not a compass, and the criterion was inadequate

One number settles it. The world holds 24 items in a 3 m disc, a density of 0.849 items/m², and a
cell of new ground is 0.7 m square, 0.49 m². A body that sweeps a cell it has not visited before
should encounter **0.416 items** there by chance alone.

**`ce861` gets 0.406 items per cell of new ground. That is 2% below chance.**

Its food-finding per unit of ground covered is indistinguishable from a blind sweeper's. It eats
eighteen times more with its noses on because it **moves** — 7.6 cells against 2.3, on a path of
4.1 m against 2.2 — not because it steers. Blanked, it is nearly stationary: it sits inside the
disc for 99.9% of the season and shuffles over 2.2 m, revisiting cells at 1.04 cells per metre
against the intact robot's 1.85.

**So the noses gate its drive.** It is a throttle, and the largest one in the family by a wide
margin, but the family still has no compass after ten arms.

### Why the criterion let a throttle through

Both of my compass conditions are satisfiable by a change in mobility alone:

- **"Items per metre rises"** compares against a point-robot floor of 0.594 items/m. The blanked
  robot reads 0.075, an eighth of that floor, because it is barely moving. Any change that makes
  an immobile robot mobile will clear this test. RBT-39 makes it worse: the true floor for a real
  body is *higher* than the point-robot rate, so the intact robot's +26% margin per metre shrinks
  or inverts, and on the per-cell measure it has already inverted.
- **"Nearest-item distance falls"** is a byproduct of covering ground in a depleting arena. A robot
  that shuffles inside one already-eaten patch has a *larger* mean distance to the nearest surviving
  item than one that crosses fresh ground. Four point eight centimetres on a 0.945 m baseline, with
  an eat radius of 0.35 m, is not closing on anything.

### The test that should replace it

**Yield per cell of new ground, against the density expectation.** It needs no point-robot
correction because it counts ground actually visited rather than distance travelled, and it cannot
be cleared by moving more. Proposed standing rule:

> No controller is called a compass unless its items per cell of newly visited ground exceeds
> `density × cell_area` by a stated margin, paired, with the per-seed differences shown.

That also answers RBT-39, which asked what the right null is: it is the per-cell density
expectation, not the per-metre swept-corridor rate.

## Two further caveats found in my own rule

1. **The zero-count veto cannot fire on a continuous channel.** `near_in` shows 0 of 256 zeros by
   construction, because it is a mean over ticks. The veto protects integer channels like items and
   is inert exactly where I leaned on it hardest.
2. **This individual was selected for re-reading because it looked strongest at 64 seeds.** Testing
   the same champion on the same statistic at larger n inherits that selection. The pre-registration
   controls the criterion but not the choice of subject, and a clean test would fix the champion by
   a rule independent of the effect being measured.

## Verdict

**`ce861` is a throttle, not a compass. The family's count of compasses after ten world variants,
five seeds and two 600-season persistent runs remains zero.** The three kinds of one-bit nose in
`docs/foraging-world.md` stand, with this as the strongest instance of the throttle.

## Reproducing

```
./runs/RBT-38/extract.sh
python scripts/paired_lesion.py runs/RBT-38/data/RBT-16 conventional 590 256
```
