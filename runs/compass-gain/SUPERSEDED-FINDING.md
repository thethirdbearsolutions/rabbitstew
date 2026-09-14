# The wiring a compass needs is common, and it does nothing (RBT-61, interim)

Filed as a repo note because the Chaotic server is unreachable; to be raised as an issue when it
returns. File analysis only, no simulation, on populations already saved by RBT-60.

## What was asked

RBT-45 measured, with no world and no selection, how often drift alone carries a two-nose pairing:
9.1% of lineages at depth 19, 35.8% at depth 100, with the *crossed* circuit at 1.3% and 8.6%.
RBT-60 then ran real selection to depth 39 and 78. So its final populations test drift against
selection directly.

## What the final populations carry

Food sensors with non-zero static influence on the effectors, 60 saved genotypes per population.

| arm | depth | population | any nose wired | **both wheel noses** | one wheel nose | chassis nose |
|---|---|---|---|---|---|---|
| A30 | 39 | wheeled | 100% | **17%** (10/60) | 33% | 100% |
| A15 | 78 | wheeled | 100% | **7%** (4/60) | 93% | 100% |
| A30 | 39 | holistic | 0% | 0% | 0% | 0% |
| A15 | 78 | holistic | 20% | 0% | 10% | 12% |

## The finding

**The structural precondition for a Braitenberg compass is present in 7 to 17 percent of the wheeled
population, and the population is blind.** RBT-60's lesion probes put both arms' holistic champions
at bit-identical on 64 of 64 bouts, and the wheeled champions at no effect or a harmful one.

So the bottleneck is **not** that the circuit is never proposed. Four individuals in sixty at depth
78, and ten in sixty at depth 39, have both wheel noses wired to the drive. The wiring turns up
routinely and earns nothing, which means a pairing carrying random weights does no useful work.

One caution on the drift comparison: RBT-45's curve started from RBT-23's final genotypes, which
already carried a 21.7% half-pairing, so it is not a like-for-like baseline for these populations
and the apparent shortfall at depth 78 (7% observed against a drift curve that would suggest around
30%) should not be read as measured suppression without a matched control.

## Why this matters more than it looks

Ten world variants and three search depths have been spent looking for a compass. **Nobody has ever
built one and checked that it works.** The programme's entire premise is that a crossed pairing
would pay if only evolution found it, and that premise is untested while the wiring for it sits
inert in a tenth of every wheeled population.

The next experiment is therefore not another world and not another search: hand-wire the circuit,
probe it against the per-cell null, and find out whether the target exists.
