# RBT-38: which nose-dependence results in this family are real?

Every lesion probe in the foraging family ran its modes over the same seed list and then
reported each mode's own standard error, comparing the means as if the samples were
independent. This re-reads every standing claim at **64 paired seeds** through one shared
helper, with the per-seed differences kept and shown.

Branch `claude/rbt-lowest-unclaimed-ticket-tp6zdu`. Verdict rule posted on the issue at 21:16
UTC, **before any number was run or looked at**; raw output in `sweep.txt` and `pair_rbt21.txt`.
No champion, config or seed was changed: this is re-analysis plus more draws of existing
genotypes.

## The rule, as pre-stated

1. Nose-dependence needs |t| ≥ 2.5 on items, paired, n = 64.
2. Compass additionally needs nearest-item distance to fall at |t| ≥ 2.5 **and** items per metre to rise.
3. Brake if what moves is time in the disc.
4. Throttle or sweep modulator if path shape moves at unchanged yield per cell.
5. **Zero-count veto**: no effect is real if the lesion changes nothing on more than half the seeds, whatever its t.
6. The RBT-21 pair additionally needs its difference-of-differences interval to exclude zero.

## Every claim, before and after

`items` is intact minus noses blanked. "Published" is the figure standing in
`docs/foraging-world.md` or an arm's report, with the n it was read at.

| # | Claim | Arm | Published (n) | Re-read, n = 64 | t | zeros | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | season-500 Pioneer, 88% | baseline-801 | 88% (8) | 1.812 → 0.312, **+1.500** | **+6.64** | 19 | **survives** — and it is a brake (time in disc t = +8.50) |
| 2 | season-590 Pioneer, 58%, "strongest in the family" | RBT-17 | 58% (8) | 1.625 → 1.062, **+0.562** | **+3.14** | 20 | **survives at 35%, not 58%** — a brake (time in disc t = +6.54) |
| 3 | season-590 Pioneer | RBT-16 | in the record | 3.344 → 0.234, **+3.109** | **+8.18** | 7 | **survives, 93%** — the strongest real effect in the family, see below |
| 4 | `c0-4`, yield doubles blanked | RBT-21 | 2.0× (8) | 0.547 → 1.156, **−0.609** | **−4.19** | 25 | **survives at 2.11×** — a nose that costs its bearer |
| 5 | g390 mower "carries a nose it never reads" | RBT-13 | asserted (8) | 2.094 → 2.094, **+0.000** | — | **64/64** | **survives, emphatically**: 64 of 64 bouts bit-identical |
| 6 | `c0-8`, 57% | RBT-21 | 57% (8) | 0.953 → 0.672, +0.281 | +1.61 | 19 | **dies** — CI [−0.061, +0.623] |
| 7 | season-0 Pioneer, 57% | RBT-18 | 57% (8) | identical to #6 — the same founder | +1.61 | 19 | **dies** |
| 8 | founder's nose, 74% | RBT-20 | 74% (8) | 2.797 → 1.812, +0.984 | +2.39 | 13 | **dies**, narrowly: 35%, and t misses 2.5 |
| 9 | season-590 Pioneer, 57% | RBT-13 | 57% (16) | 1.359 → 0.969, +0.391 | +2.15 | 21 | **dies**: 29%, t under the bar |
| 10 | season-500, "closer to food without its nose" | RBT-17 | asserted (8) | 1.609 → 1.438, +0.172 | +1.04 | 28 | **dies**: nothing separable, nearest-item t = +1.95 |
| 11 | season-20 Pioneer, nose-hindered | baseline-801 | asserted (8) | 1.172 → 1.344, −0.172 | −1.12 | **38** | **dies**, and is vetoed: 59% of seeds unmoved |
| 12 | season-30 best, ate more with sensors off | baseline-801 | asserted (8) | 1.156 → 1.016, +0.141 | +0.84 | 32 | **dies** |
| 13 | season-100 Pioneer | RBT-16 | in the record | 2.688 → 2.297, +0.391 | +1.50 | 18 | **dies** |
| 14 | season-590 Pioneer, 28% | RBT-23 | 28% (8) | 1.219 → 1.375, −0.156 | −1.00 | **36** | **dies**, and is vetoed: 56% unmoved |
| 15 | season-300 Pioneer, 27% | RBT-22 | 27% / 33% / 15% (16) | 1.266 → 1.234, +0.031 | +0.14 | 28 | **dies** — the case that motivated this ticket |

**Five survive of fifteen.** Four of those five are nose effects on yield; the fifth (#5) is a
null claim that survives by being exactly, bit-identically null.

## Three things the re-read changes

**The eight-seed readings were biased upward, not merely noisy.** Every claim that moved, moved
the same way: 88% → 83%, 58% → 35%, 74% → 35%, 57% → 29%, 57% → 29%, 28% → −13%, 27% → +2%. Not
one published effect got larger. That is what selecting a champion on a small probe and then
reporting that probe does.

**The zero-count veto earned its place.** Claims 11 and 14 have more than half their seeds
bit-identical between the modes. They were reported as smooth percentage biases. They are not
biases of any size; they are a handful of bouts where the lesion happened to matter.

**Pairing was rarely the problem; n was.** For most claims the paired and unpaired SEs are within
a few percent (`c0-8`: 0.175 and 0.175). The pairing correction matters for the arms where the
modes' spreads differ (#2: 0.179 paired against 0.240 unpaired; #4: 0.145 against 0.181), and it
helps there. But the reason eight-seed effects evaporated is sample size, not the error term. Both
fixes were needed; only one was the headline.

## The one finding this re-read adds

**RBT-16's season-590 Pioneer is the strongest nose effect in the family and the closest thing to
a compass anywhere in it.** With its noses blanked it eats 0.234 items against 3.344 intact, a 93%
loss at t = +8.18 with only 7 of 64 seeds unmoved. Unlike every other survivor it is not a brake:
it spends **less** time in the disc with its noses on (t = −11.13) and takes **more items per
metre** of in-disc path (+0.589, t = +8.73). It goes in, eats, and leaves.

By the rule as pre-stated it is **not** a compass, and I am not going to call it one: the rule
requires nearest-item distance to fall at |t| ≥ 2.5 and it reads t = −2.00. It is in the right
direction and under the bar. Reading that one channel at more seeds until it crosses would be
choosing the sample size after seeing the statistic, so it is not a rescue and I have not run it.
It is a **new pre-registered question**: does this individual close on food? That deserves its own
ticket with its n fixed in advance, and it is the first time in this family that question has been
worth asking.

## What the docs should now say

The summary line "no Pioneer ever wired its two wheel noses into a pairing, only the chassis nose
into a gate" keeps its wiring half, which this ticket did not test. Its behavioural half is now
supported by three effects rather than a dozen, and one of those three does not behave like a gate.

## Files

`pair_rbt21.txt` (the RBT-21 pair, full per-seed lists), `sweep.txt` (the other thirteen),
`extract.sh`, `sweep.sh`, and `rabbitstew/paired.py` plus `scripts/paired_lesion.py` on the
branch, with nine tests.

The extracted champions under `data/` are **not committed**. They are byte-identical copies of
genotypes already in the repository on the branches `extract.sh` names, and that script
regenerates them exactly, so committing them would have added twenty-four thousand lines of
duplicate JSON to a review.

## Reproducing

```
git fetch origin results/RBT-21 results/RBT-13 results/RBT-16 results/RBT-18 results/RBT-22 \
    results/baseline-801 claude/wizardly-johnson-4c9hvn claude/rbt-20-mtqdsp \
    claude/rbt-lowest-unclaimed-ticket-55orfd
./runs/RBT-38/extract.sh                                   # pulls every champion out of those branches
./runs/RBT-38/sweep.sh                                     # all thirteen, about twenty minutes
python scripts/paired_lesion.py runs/RBT-38/data/RBT-21 conventional 0,10 64   # the pair
```
