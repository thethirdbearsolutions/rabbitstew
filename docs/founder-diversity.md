# Founding-population diversity: a measured definition (RBT-90, part 1)

Every "the search does X" sentence in this programme rests on one or two founding populations.
RBT-84 showed the cost: seed 801 discards oscillator drive, seed 807 acquires it, and the two
happened to share a base rate of 0.483 for the drive composite by luck. A ten-seed sweep can only
decide which regularities are properties of the search if the ten founding populations are known to
be ten draws from a wide distribution and not a narrow one. This document states what that means,
in numbers that regenerate from a committed `config.json` with no simulation, and applies it to the
five seeds the programme has run.

Script: `runs/RBT-90/founder_diversity.py`. Readouts: `docs/artifacts/founders-<seed>.txt` (one per
seed), `docs/artifacts/RBT-90-calibration.txt` (the set), `docs/artifacts/RBT-90-reference.txt` and
**`RBT-90-reference.json`, which is authoritative** (the generator), `docs/artifacts/RBT-90-part2-seeds.txt`
(the ten seeds for part 2). Re-derivation is `tests/test_founder_diversity.py`. The adversary's
round (the ems6yl delegate, PR #55): `runs/RBT-90/adversary_probes.py` and `adversary_direction.py`,
readouts `docs/artifacts/RBT-90-adversary-probes.txt` and `RBT-90-adversary-direction-<seed>.txt`.
Rates are written as `k/60` everywhere: the rule's thresholds are achievable values that many seeds
sit on exactly, so a three-decimal print cannot re-derive the rule's own pass rates (probe 1 found
0.89 and 0.55 from the rounded text against 0.925 and 0.620 from the exact rates).

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
   unit kinds and sources). It is never shared between random draws (0 of 60 in all ten pairs,
   60 of 60 distinct within every seed) and is 60 of 60 shared between five arms started from one
   population (RBT-28's adversary), which is the discrimination clause 1 needs. The coarser **shape
   multiset** (sorted node shapes) is reported and read by no clause: the adversary's probe 2 showed
   it is a strict coarsening of the full signature (1,864 within-seed pairs share a multiset and not
   a signature, none the other way), its 52-multiset space is saturated by the generator's hardcoded
   three-shape vocabulary, and the calibration set's 36 to 52 of 60 shared is the 4th to 94th
   percentile of what any two random seeds give. It separates nothing the signature does not.
4. **Direction of travel: RBT-69's forward/backward split is undefined on a holistic founding
   population, shown rather than assumed.** The adversary's `adversary_direction.py` runs the probe
   in each body's own root frame (sixteen bouts per founder, about five minutes per seed). The
   machinery is not Pioneer-specific; what a random body lacks is the zero point, so the per-founder
   mean direction is not comparable across founders. What is defined is the within-body
   concentration R, which decides whether a circuit could be signed against that body. On seed 801:
   the resultant of the per-founder mean directions is 0.025 against 0.135 expected under exact
   isotropy at n = 43, positive evidence of no population-level axis; 14 of 43 movers travel in a
   fixed direction in their own frame (R at or above 0.6); 17 of 60 founders never move a millimetre
   in a tick, so for them the statistic is undefined by immobility whatever axis is chosen. The same
   holds on all five calibration seeds (sixty founders, sixteen bouts each; every resultant below its
   isotropic expectation):

   | seed | movers | never moved | resultant of mean directions | isotropic expectation | movers with R ≥ 0.6 |
   |---|---|---|---|---|---|
   | 801 | 43 | 17 | 0.025 | 0.135 | 14 |
   | 804 | 42 | 18 | 0.060 | 0.137 | 9 |
   | 805 | 36 | 24 | 0.131 | 0.148 | 11 |
   | 806 | 45 | 15 | 0.107 | 0.132 | 11 |
   | 807 | 44 | 16 | 0.100 | 0.134 | 10 |

   Every `founders-<seed>.txt` carries its seed's row from that probe's readout, and a candidate seed
   for part 2 is measured on it too. The split stays measurable on the conventional Pioneer
   population, which has a designed front and is where an installed circuit's sign is at stake.

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
(11.5%) lands on exactly 29/60 = 0.483. As `k/60`: the composite's quartiles are 28/60 and 33/60,
the linked oscillator's 11/60 and 15/60, the link-driven effector's 38/60 and 42/60; twelve seeds sit
on each composite quartile exactly, which is why the `.json` and not the `.txt` is the authority.

## The rule

A set of founding seeds is **diverse enough** for a sweep when:

1. **Bodies are distinct** (pass/fail). Every pair of seeds shares at most 1 of 60 full body
   signatures, and every seed has at least 58 of 60 distinct. Random draws pass this trivially;
   it exists to catch what RBT-28's adversary found, five arms started from one population
   (60 of 60 shared), and a `holistic_seed` template population (1 of 60 distinct).
2. **The set spans the generator** (pass/fail), on two statistics. The seeds' composite base rates
   reach both quartiles of the reference (at least one seed at or below 28/60 and at least one at or
   above 33/60), **and** their linked-oscillator rates reach both of theirs (at or below 11/60 and at
   or above 15/60). The oscillator clause is explicit because the composite is half an instruction
   about fan-out (r² 0.50 with link-driven effector, 0.27 with linked oscillator over the reference)
   and spanning it is almost uninformative about spanning the oscillator rate (0.952 against a 0.949
   base rate), which is the quantity part 2 measures; the adversary's probe 3. A set of ten random
   draws passes the composite span 92.5% of the time, the oscillator span 94.9%, both 88%; a set that
   fails is a narrow draw and is widened by adding seeds, never by swapping them. The link-driven-
   effector span is reported beside them and not ruled on.
3. **Outliers are named, not excluded** (a label). A seed whose base rates or size medians fall
   outside the generator's central 90% band is kept and named, so that a regularity that splits in
   part 2 can be read against it. The first draft of this rule had the clause as pass/fail; seed 805
   failed it, and excluding an atypical founding population would narrow the sweep, which is the
   opposite of what the rule is for. That change is recorded here and on the ticket. The adversary's
   probe 4 then showed the draft clause was miscalibrated rather than seed 805 unlucky: only 153 of
   200 reference seeds are inside the band on all five statistics, so as pass/fail it would have
   admitted 6.4% of random ten-sets.

## Calibration on seeds 801, 804, 805, 806, 807

| seed | link-driven effector | linked oscillator | composite | parts median | units median | distinct bodies | distinct shapes |
|---|---|---|---|---|---|---|---|
| 801 | 40/60 = 0.667 | 13/60 = 0.217 | 29/60 = 0.483 | 3 | 15 | 60/60 | 28/60 |
| 804 | 38/60 = 0.633 | 12/60 = 0.200 | 29/60 = 0.483 | 4 | 17 | 60/60 | 32/60 |
| 805 | 35/60 = 0.583 | 19/60 = 0.317 | 21/60 = 0.350 | 4 | 15.5 | 60/60 | 33/60 |
| 806 | 41/60 = 0.683 | 15/60 = 0.250 | 31/60 = 0.517 | 4 | 14 | 60/60 | 30/60 |
| 807 | 38/60 = 0.633 | 15/60 = 0.250 | 29/60 = 0.483 | 3.5 | 14 | 60/60 | 32/60 |

Pairwise, 0 of 60 full signatures are shared in every pair (36 to 52 of 60 shape multisets, reported only).

- Clause 1, bodies: **PASS**.
- Clause 2, span: **FAIL on both statistics.** Composite rates run 21/60 to 31/60; no seed reaches
  the upper quartile 33/60. Linked-oscillator rates run 12/60 to 19/60; no seed reaches the lower
  quartile 11/60. Three of the five sit on exactly 29/60 (the chance of that under the reference is
  about 1%). The five seeds the programme has run are a narrow draw: on the composite at the upper
  side, on the oscillator at the lower side, and (reported) on link-driven effector at the upper
  side, each for its own reason. Every "the search does X" result so far comes from populations at
  or below the generator's median rate of effector drive without oscillator.
- Clause 3, outliers: **seed 805**, on two statistics. Its composite 0.350 is below every one of the
  200 reference seeds (minimum 0.367) and its linked-oscillator rate 0.317 is above the 95th
  percentile. RBT-71's three-seed results (804, 805, 806) therefore include one founding population
  that is rarer than 1 in 200 on the drive composite. Nothing in RBT-71's claims turns on that rate,
  and this is a label: 805 stays in any set it is part of.

**Verdict: the five are not diverse enough under clauses 1 and 2 as stated**, whichever of the
three axes clause 2 is read on. Part 2's ten seeds must include draws that reach the composite's
upper quartile and the oscillator's lower one; the five existing seeds cannot be the sweep on their own.

## The ten seeds for part 2, chosen before any run

The rule, decided by the coordinator on the ticket and implemented as `--choose 10`: the five
calibration seeds are kept (every population the programme has already read), the candidates are
seeds 1 to 200 (the committed reference), and the further five are the lexicographically first
five-seed combination by seed number whose union with the five passes clauses 1 and 2. The choice
is deterministic from committed files and is written to `docs/artifacts/RBT-90-part2-seeds.txt`.
Result: combinations (1, 2, 3, 4, 5) and (1, 2, 3, 4, 6) fail; **(1, 2, 3, 4, 7) passes**, seed 2
reaching the composite's upper quartile (37/60) and seed 7 the oscillator's lower one (11/60). The
ten are **801, 804, 805, 806, 807, 1, 2, 3, 4, 7**; their direction rows are measured before the run.

One thing to read the sweep against: five of the ten are the calibration set, which sits at or
below the composite's median, so the ten are low-skewed on that statistic by construction. A
regularity that holds on 8 of 10 is therefore reported split by composite half as well as pooled.

## What this is not

Not a claim that any base rate predicts an outcome; RBT-84's two seeds shared a rate and split on
the outcome. Not a simulation result beyond the direction probe's sixteen solo bouts per founder,
which read a body's own travel and no economy. Not RBT-69's split, which is shown to be undefined on
this population rather than measured. The `wiring` classifier's fan-out weakness is inherited and
not repaired here; the oscillator clause is the rule's answer to it.
