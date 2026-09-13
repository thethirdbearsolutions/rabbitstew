# RBT-59: seasons are not generations

Every design decision in the foraging fan-out is denominated in **seasons**. Selection is
denominated in **reproduction events**. This measures the conversion rate across every completed
arm, and what sets it. File analysis only: no simulation, no selection, no new runs.

Pre-registration on the issue, before any number was computed. Branch
`claude/rbt-lowest-unclaimed-ticket-tp6zdu`; raw output in `depth.json`, `mechanism.json`,
`selection.json`.

## 1. The conversion rate is about 30 to 1, and it does not move

Fourteen population-rows across ten arms, all at `max_age` 60, all reaching season 599.
First-parent chain length from an individual alive at the end back to a founder is the number of
sequential mutations that lineage underwent, because `Ecology._breed` applies exactly one mutation
per reproduction and sets `parents[0]` to the individual copied from.

| | median depth | seasons per reproduction |
|---|---|---|
| range over all fourteen rows | **18 to 24** | **25 to 33** |
| median | 20 | 30 |

Depths in order: 18, 18, 19, 19, 19, 20, 20, 20, 21, 22, 23, 23, 23, 24. Over those same rows mean
energy gain spans 0.69 to 1.70, a factor of 2.5, across the baseline, long-range smell, normalised
smell, depletion, a crowded arena and the patchy persistent world.

**Pearson r(mean gain, median depth) = −0.153.** Expectation 3 of the pre-registration, that
richer arms search deeper, is **falsified**.

## 2. Why: births are slot-limited, not energy-limited

| check | result |
|---|---|
| births per season ÷ deaths per season | **1.000 in all fourteen rows**, to three decimals |
| share of the living at or above the birth threshold | 70% to 93%, **median 89%** |
| mean energy of the living, against a threshold of 3.0 | **13.9 to 40.8** |
| Pearson r(mean gain, births per season) | **−0.463** |

A birth needs a free slot; slots open only on a death; deaths are dominated by old age. The
reproduction rate is therefore pinned to the death rate however rich the world is, and surplus does
not become children — the median individual holds five to thirteen times what it needs to breed and
cannot. Expectation 4 is **confirmed**.

**Consequence.** Every economy arm in the fan-out — work cost, density, depletion, patches,
crowding — varied a parameter that does not control the search rate. That is a property of the
ecology nobody had measured, not a criticism of any delegate.

## 3. A prediction of mine that failed, and what it changes

I predicted on the issue, before running it, that if 89% of a population qualifies to breed and
parents are drawn in random order from the qualifying set, then selection would be nearly absent:
under 0.3 standard deviations of difference in lifetime yield between individuals that ever bred
and those that never did, age controlled.

**Wrong.** Age-controlled standardised difference: median **+0.43 SD**, range +0.03 to +0.85, and
**10 of 14 rows exceed my 0.3 bound**. Raw, uncontrolled, the median is +0.97 SD.

Selection in this ecology is real and it operates through **differential survival to breeding**,
not through who gets picked when a slot opens. Individuals that bred have mean age 45 to 58;
those that never bred, 10 to 44. The low earners starve before they get a chance at a slot.

One interpretive note, offered after the fact and labelled as such: controlling for age removes
part of the causal pathway, because living longer is *how* a good forager converts yield into
offspring. The age-controlled +0.43 is therefore a lower bound on selection strength, and I am
reporting it as the answer because that is what I committed to.

## 4. What this means, and the law it suggests

The programme's diagnosis has been that ten worlds failed to reward sensing. The measurements say
something narrower and more fixable:

- Selection per generation is **decent**, about 0.43 SD.
- The search is about **twenty generations deep**.
- RBT-45 measured the crossed Braitenberg circuit arriving in **1.3%** of lineages of that depth.

Twenty generations at 0.43 SD is not enough to assemble a multi-step circuit that arrives in one
lineage in seventy-seven. **The programme has not been running an underpowered world. It has been
running an underpowered search, and buying seasons when it needed generations.**

Every arm ran at `max_age` 60 for 599 seasons and landed at depth 20, which fits

> **depth ≈ 2 × seasons ÷ max_age**

to within the observed spread (predicted 20.0, measured median 20, range 18 to 24). `max_age` is
the only term in that expression the programme has never varied. If the law holds, `max_age` 15
would buy **four times the search depth at identical compute**.

That is a prediction, not a result: one value of `max_age` cannot test a law with `max_age` in it.
Filed as its own arm with the test fixed in advance.

## Files

`depth.py` / `depth.json`, `mechanism.py` / `mechanism.json`, `selection.py` / `selection.json`,
`extract.sh`. The extracted lineage logs under `data/` are not committed: they are byte-identical
copies of files on nine other branches and `extract.sh` regenerates them.

## Reproducing

```
git fetch origin results/RBT-13 results/RBT-16 results/RBT-18 results/RBT-21 results/RBT-22 \
    results/baseline-801 claude/wizardly-johnson-4c9hvn claude/rbt-20-mtqdsp \
    claude/rbt-lowest-unclaimed-ticket-55orfd
./runs/RBT-59/extract.sh
python runs/RBT-59/depth.py && python runs/RBT-59/mechanism.py && python runs/RBT-59/selection.py
```
