# Founding-population diversity: a measured definition (RBT-90, part 1)

Every "the search does X" sentence in this programme rests on one or two founding populations.
RBT-84 showed the cost: seed 801 discards oscillator drive, seed 807 acquires it, and the two
happened to share a base rate of 0.483 for the drive composite by luck. A ten-seed sweep can only
decide which regularities are properties of the search if the ten founding populations are known to
be ten draws from a wide distribution and not a narrow one. This document states what that means,
in numbers that regenerate from a committed `config.json` with no simulation, and applies it to the
five seeds the programme has run.

Script: `runs/RBT-90/founder_diversity.py`. Readouts: `docs/artifacts/founders-<seed>.txt` (one per
seed), `docs/artifacts/RBT-90-calibration.txt` (the set), `docs/artifacts/RBT-90-reference.txt`
(the generator). Re-derivation is `tests/test_founder_diversity.py`.

## What is measured, per seed, from the sixty founders alone

A holistic founding population is a pure function of the run's `seed`, its mutation vocabulary and
the ecology `capacity` (`initial_population` → `random_genotype`; RBT-28's adversary, RBT-84's
`reproducible.py`). The five calibration configs differ only in the food economy, the worker count
and the seed, none of which the founders read; the script refuses a config whose vocabulary or
capacity differs from seed 801's.

1. **Base rates**, on `runs/RBT-28/adversary_founders.py::wiring` imported rather than
   reimplemented, so they are the same measurement as RBT-28's and RBT-84's: the fraction of
   founders with a **link-driven effector** (a live effector with a link into it), with a **linked
   oscillator** (an oscillator sensor with an outgoing link), and the **composite** "drive, no
   oscillator" (both). Seeds 801 and 807 reproduce RBT-84's pre-registered 40/13/29 and 38/15/29
   exactly. The composite carries RBT-84 section 5's caveat: "a link into a live effector" is also
   satisfied by a fan-out from a central driver, so it reads as more than it measures.
2. **Size distributions**: parts, units, nodes and links per founder (min, quartiles, max, histogram).
3. **Bodies**: the full body signature (RBT-28's `shape_sig`: node shapes in order plus each node's
   unit kinds and sources) and the coarser **shape multiset** (sorted node shapes, order and brains
   dropped). The full signature is never shared between random draws (0 of 60 in all ten pairs,
   60 of 60 distinct within every seed), so on its own it has no resolution; the shape multiset is
   shared by 36 to 52 of 60 founders across a pair (either direction) and is what separates a wide draw from a narrow
   one at the body level.
4. **Direction of travel: not measured.** It needs the direction probe (`scripts/travel_direction.py`:
   sixteen MuJoCo bouts per genome, 300 genomes here), and for a random body the axis "forward" is
   read against has to be defined first: RBT-69's is the Pioneer chassis yaw, which a holistic
   founder does not have. This is the named missing measurement of part 1. It matters where an
   installed circuit's sign is at stake, which in this programme is the conventional (Pioneer)
   population, whose founders share one body by construction.

## The reference: what a typical draw looks like

The generator's own distribution, seeds 1 to 200 under seed 801's config, sixty founders each
(`docs/artifacts/RBT-90-reference.txt`). This is what the thresholds below are read from; it is not
a calibration and no arm has been run on any of these seeds.

| statistic | min | p5 | q25 | median | q75 | p95 | max |
|---|---|---|---|---|---|---|---|
| link-driven effector | 0.517 | 0.567 | 0.633 | 0.667 | 0.700 | 0.767 | 0.817 |
| linked oscillator | 0.083 | 0.133 | 0.183 | 0.217 | 0.250 | 0.300 | 0.383 |
| composite (drive, no osc) | 0.367 | 0.417 | 0.467 | 0.500 | 0.550 | 0.617 | 0.700 |
| parts, median | 2 | 3 | 3.5 | 4 | 4 | 4 | 5 |
| units, median | 12 | 13 | 14.5 | 16 | 17.5 | 20 | 23 |

The composite's standard deviation across seeds is 0.064, which at n = 60 is the binomial value:
seed-to-seed variation in a base rate is sampling variation and nothing else. One seed in nine
(11.5%) lands on exactly 29/60 = 0.483.

## The rule

A set of founding seeds is **diverse enough** for a sweep when:

1. **Bodies are distinct** (pass/fail). Every pair of seeds shares at most 1 of 60 full body
   signatures, and every seed has at least 58 of 60 distinct. Random draws pass this trivially;
   it exists to catch what RBT-28's adversary found, five arms started from one population
   (60 of 60 shared), and a `holistic_seed` template population (1 of 60 distinct).
2. **The set spans the generator** (pass/fail). The seeds' composite base rates reach both
   quartiles of the reference: at least one seed at or below 0.467 and at least one at or above
   0.550. A set of ten random draws passes this 92% of the time (five draws: 63%; estimated by
   resampling the 200 reference seeds); a set that fails is a narrow draw on the one statistic the
   programme's regularities are stated in, and is widened by adding seeds, never by swapping them.
   The link-driven-effector and linked-oscillator spans are reported beside it and not ruled on.
3. **Outliers are named, not excluded** (a label). A seed whose base rates or size medians fall
   outside the generator's central 90% band is kept and named, so that a regularity that splits in
   part 2 can be read against it. The first draft of this rule had the clause as pass/fail; seed 805
   failed it, and excluding an atypical founding population would narrow the sweep, which is the
   opposite of what the rule is for. That change is recorded here and on the ticket.

## Calibration on seeds 801, 804, 805, 806, 807

| seed | link-driven effector | linked oscillator | composite | parts median | units median | distinct bodies | distinct shapes |
|---|---|---|---|---|---|---|---|
| 801 | 40/60 = 0.667 | 13/60 = 0.217 | 29/60 = 0.483 | 3 | 15 | 60/60 | 28/60 |
| 804 | 38/60 = 0.633 | 12/60 = 0.200 | 29/60 = 0.483 | 4 | 17 | 60/60 | 32/60 |
| 805 | 35/60 = 0.583 | 19/60 = 0.317 | 21/60 = 0.350 | 4 | 15.5 | 60/60 | 33/60 |
| 806 | 41/60 = 0.683 | 15/60 = 0.250 | 31/60 = 0.517 | 4 | 14 | 60/60 | 30/60 |
| 807 | 38/60 = 0.633 | 15/60 = 0.250 | 29/60 = 0.483 | 3.5 | 14 | 60/60 | 32/60 |

Pairwise, 0 of 60 full signatures are shared in every pair; 36 to 52 of 60 shape multisets are, either direction.

- Clause 1, bodies: **PASS**.
- Clause 2, span: **FAIL**. Composite rates run 0.350 to 0.517; no seed reaches the upper quartile
  0.550. Three of the five sit on exactly 0.483 (the chance of that under the reference is about
  1%). The five seeds the programme has run are a narrow draw on the upper side of the composite:
  every "the search does X" result so far comes from populations at or below the generator's median
  rate of effector drive without oscillator.
- Clause 3, outliers: **seed 805**, on two statistics. Its composite 0.350 is below every one of the
  200 reference seeds (minimum 0.367) and its linked-oscillator rate 0.317 is above the 95th
  percentile. RBT-71's three-seed results (804, 805, 806) therefore include one founding population
  that is rarer than 1 in 200 on the drive composite. Nothing in RBT-71's claims turns on that rate,
  and this is a label: 805 stays in any set it is part of.

**Verdict: the five are not diverse enough under clauses 1 and 2 as stated.** Part 2's ten seeds
must include draws that reach the composite's upper quartile; the five existing seeds cannot be
the sweep on their own, and adding five more random seeds gives a set that passes clause 2 with
probability about 0.9, to be checked with this script before any arm is launched.

## What this is not

Not a claim that any base rate predicts an outcome; RBT-84's two seeds shared a rate and split on
the outcome. Not a simulation result: nothing here has been run. Not the direction-of-travel
measurement, which is named above as missing. The `wiring` classifier's fan-out weakness is
inherited and not repaired here.
