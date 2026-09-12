# RBT-21, world fan-out arm W6': moderately expensive movement (work cost 0.08 per kJ, 12 items, seed 801)

One flag changed from the baseline `forage-801`: `--work-cost 0.08`. Everything else exactly as the issue's
command line. Base commit `e75abd9` on `claude/new-session-4cao7d`; 139 tests passed before the run.

**Result in one line.** Both populations went extinct again: the wheeled side at season 13, the holistic side at
season 26. The run asked for 600 seasons and ended at 26. RBT-18's break-even arithmetic was right about the
individual it was about (the 1.1 kJ blind mower `h0-7` still bred, four times) and wrong about the population:
the limit at this coefficient is not the adults' work bill but the newborns', because a child is born with
exactly `birth_cost` = 1 energy and at 0.08 per kJ a Pioneer newborn's random driving spends that in one season.

**About the coefficient.** This arm leans on the work-cost coefficient that `docs/foraging-world.md` flags as the
place a thumb could rest, and everything below is a finding about that coefficient at this value. The within-run
lesion results are interpreted; the holistic-versus-wheeled comparison is not, since at 0.08 per kJ the two
bodies' random work budgets (73% of lumps under 0.1 kJ against a Pioneer median of 17.5 kJ) decide the outcome
before anything is selected.

## Ecology readout

`fitness` / "mean gain" throughout is the mean over an individual's seasons of (items eaten x 1) minus
0.08 x kJ, **before** the 0.25 basal cost; an individual is solvent only above +0.25. Full per-season table in
`history.txt`.

| season | hol alive | births | deaths | hol mean gain | wheel alive | births | deaths | wheel mean gain |
|---|---|---|---|---|---|---|---|---|
| 0 | 59 | 3 | 4 | -0.007 | 60 | 2 | 2 | -1.161 |
| 1 | 60 | 2 | 1 | +0.040 | 39 | 4 | 25 | -0.393 |
| 2 | 60 | 0 | 0 | +0.017 | 28 | 6 | 17 | -0.029 |
| 3 | 59 | 1 | 2 | +0.016 | 15 | 0 | 13 | +0.046 |
| 4 | 56 | 1 | 4 | +0.008 | 9 | 1 | 7 | +0.116 |
| 6 | 50 | 0 | 2 | +0.008 | 6 | 0 | 2 | +0.192 |
| 8 | 44 | 0 | 4 | +0.001 | 3 | 0 | 1 | +0.169 |
| 10 | 37 | 0 | 3 | +0.009 | 2 | 1 | 2 | +0.278 |
| 11 | 3 | 0 | 34 | +0.164 | 1 | 0 | 1 | +0.498 |
| 13 | 3 | 0 | 0 | +0.136 | 0 | 0 | 1 | extinct |
| 14 | 3 | 1 | 1 | +0.192 | | | | |
| 19 | 3 | 1 | 0 | +0.206 | | | | |
| 22 | 1 | 0 | 2 | +0.344 | | | | |
| 25 | 1 | 0 | 0 | +0.294 | | | | |
| 26 | 0 | 0 | 1 | extinct | | | | |

Seasons 32, 60, 100, 200, 300, 400, 500 and 599 do not exist.

**Wheeled: real selection for economy, then extinction at season 13.** This is the one thing the arm does that
RBT-18 did not. At 0.15 per kJ half the Pioneer founders were over the one-season death line and thirty died in
season 0; at 0.08 **none** was (worst season-0 gain -2.55 against the -2.75 that empties 3 energy in one season),
and the founders were sorted rather than wiped: 51 of the 60 season-0 rows show a negative gain, two individuals
died in season 0 and 25 in season 1 (the 25 all ended season 0 with energy left, between 0.20 and 1.38, and spent
it in one more season), and the population's mean gain climbed monotonically from -1.161 to +0.498 over thirteen
seasons as the expensive drivers were removed. That is selection for economy acting on the designed body, from season 0, which the docs record
nowhere else in the fan-out except the six-item arm. It bred 16 children against RBT-18's 1. It went extinct
anyway, at 60, 39, 28, 15, 9, 8, 6, 4, 3, 3, 2, 1, 0 over seasons 0 to 13, because sorting 60 founders on a body
whose cheapest survivor still spends 13 kJ leaves too few of them: only three wheeled individuals in the whole
run ever covered the basal cost (`c0-2` +0.37, `c0-4` +0.46, and the child `ce75` +0.38 on two seasons).

**Wheeled: the newborns are the mechanism.** A child starts with `birth_cost` = 1 energy
(`rabbitstew/ecology.py:256`). A Pioneer newborn spends 13 to 23 kJ a season, which at 0.08 is 1.0 to 1.8 energy,
so it is bankrupt in its first season unless it eats two items immediately. Ten of the sixteen wheeled children
lived one season or less (`ce63`, `ce65`, `ce66`, `ce67`, `ce69`, `ce70`, `ce72`, `ce73`, `ce74`, `ce76`), and none
lived past three. The population therefore could not recruit even while its surviving adults were getting better:
`c0-4`, mean gain +0.46 and solvent at +0.21 a season, bred four children and buried all four. At this
coefficient the wheeled side is not starved as adults; it is sterilised through its offspring.

**Holistic: the baseline's bottleneck, plus a pre-wave bleed, and no recovery.** The season-11 starvation wave
arrives exactly as in the baseline (34 deaths at season 11), but two things differ. First, 23 lumps die in seasons
4 to 10 before the wave; 8 of them aged out at 60, and all 15 that starved had a non-positive lifetime mean gain
(median -0.036, worst -0.319): the work cost charges the tail of lumps that move. Second, the remnant is 3, not the baseline's 7, and it never recovers:
3 at seasons 11 to 21, 1 from 22, extinct at 26. Of the 34 in the wave, **none** had a positive lifetime mean gain
(max +0.000) — they are the founders that never ate, starving on birth energy on schedule. Three holistic
individuals in the entire run covered the basal cost, and two of them (`h0-49` +0.44, `h0-59` +0.62) were already
59 seasons old at season 0 and aged out at seasons 8 and 3 respectively. The population's whole future was one
individual.

**Holistic: `h0-7`, and why it could not refound the population.** `h0-7` is the same individual RBT-18 identified
as plausibly the baseline's single founder, and this run settles that it is the same lump: its probe numbers here
(0.50 items, 2.9 m path, 1.1 kJ) are identical to RBT-18's to two decimals on the same seed, as are `h0-49`'s and
`c0-8`'s. Its per-season gains are +0.909 in a season it eats one item and -0.091 in a season it does not, so it
spends 1.14 kJ a season and ate 10 items in 26 seasons: a realised yield of **0.385 items a season**, not the 0.50
its solo probe suggests, because in the ecology it shares the arena with three others. At 0.08 that is a mean gain
of +0.294 against a basal cost of 0.25, a net of **+0.044 a season** — solvent, and it did breed four times, but
one of those births came only from a four-item windfall at season 14 (`last_score` +3.909, its energy jumping 1.24
to 3.90). Twenty-three seasons of that net buy one unit of energy; a birth costs one.

**All ten holistic children failed, and this is the finding.** Nine of the ten had a lifetime mean gain within
0.05 of zero and died at age 3 or 4, which is what 1 energy buys at a 0.25 basal cost; the tenth (`he69`, +0.125)
lasted six seasons and still never covered the basal cost. No holistic child in the run reached +0.25. `h0-49`,
the season-0 best and the second-most-solvent lump, bred four children with the same result. Mutation from an
eating lump does not produce an eating lump often enough, and with one eater alive there is no population in which
to select the rare one that does.

**Founders.** Holistic 1 of 1 at the last season with survivors (season 25); wheeled 1 of 1 at season 12. Both
lineages end.

**Crossover.** Holistic mean gain exceeds wheeled at season 0 (-0.007 against -1.161) and holds the lead through
season 3; from season 4 to the wheeled extinction at 13 the wheeled side leads (+0.116 to +0.498 against +0.001 to
+0.164), because its survivors are a selected remnant of two to nine while the holistic side is still 37 to 56
non-eating founders. Neither number means what the baseline's crossover at season 83 means.

**Yield heritability.** Not measurable on either side. With `min_evals` = 5, one holistic child qualifies (`he69`)
and none on the wheeled side, against the 10 the estimator needs. No correlation is reported. Baseline 0.51 /
0.24–0.39.

## Probes (eight fresh seeds each, robot alone in the arena; `probe.txt`)

Bests exist at holistic seasons 0, 10 and 20 and wheeled seasons 0 and 10; the issue's 0, 100, 300 and 590 do not
all exist and the command as issued returns only the season-0 rows (`probe_asissued.txt`). Both `<kind>/final/`
directories are empty, since both populations were extinct. The holistic best at 10 and 20 is the same individual.
**Every best in the run is a generation-0 founder**: `h0-49` (age 59 at season 0), `h0-7` (27), `c0-8` (32) and
`c0-4` (43). Twenty-six children were born across both populations and not one became a best or bred, so no
lineage in this run has a grandparent; what follows is selection among founders inside one generation.

| best | sensors | intact items / path / work | items per kJ | no_food | no_env | no_local |
|---|---|---|---|---|---|---|
| hol s0 `h0-49` (4 parts, 29 units) | oscillator, up | 0.00 / 2.3 m / 0.7 kJ | 0.00 | 0.00, path and work unchanged | 0.00 / 1.9 m | 0.12 / 0.9 m / 0.3 kJ (0.40) |
| hol s10+s20 `h0-7` (4 parts, 20 units) | joint_angle x4 | 0.50 / 2.9 m / 1.1 kJ | 0.45 | 0.50 / 2.9 m / 1.1 kJ (0.45) | 0.50 / 2.9 m / 1.1 kJ (0.45) | 0.62 / 2.8 m / 1.0 kJ (0.62) |
| wheel s0 `c0-8` (Pioneer, 24 units) | food x3, agent x3, contact, height, joint_velocity x2, up x3, velocity x3 | 0.88 / 7.5 m / 22.9 kJ | 0.038 | 0.38 / 4.0 m / 21.7 kJ (0.018) | 0.12 / 3.6 m / 17.0 kJ (0.007) | 0.12 / 3.6 m / 17.0 kJ (0.007) |
| wheel s10 `c0-4` (Pioneer, 24 units) | same stock layout | 0.50 / 8.8 m / 15.0 kJ | 0.033 | **1.00** / 9.7 m / 15.7 kJ (0.064) | 0.50 / 5.6 m / 10.1 kJ (0.050) | 0.50 / 5.6 m / 10.1 kJ (0.050) |

One sentence per best:

- `h0-49` eats nothing alone under any lesion, has no nose, and no sensor matters; its solvency in the ecology
  (+0.44) came from where the food and its group mates fell, and it aged out at season 8.
- `h0-7` carries four joint-angle sensors and no nose, and blanking them, or every sensor, changes neither path,
  work nor yield to two decimals; silencing its local brains raises its yield a quarter on a tenth less work, so
  no sensor matters and the local brains are a small drag — the same blind mower the baseline found.
- `c0-8` is nose-dependent: blanking food and agent more than halves its yield (0.88 to 0.38) and its economy
  (0.038 to 0.018 items per kJ), and blanking every environmental sensor leaves 0.12; but its noses buy half an
  item, 0.5 energy, against a work bill of 1.8 energy a season at this coefficient, and it died at season 10.
- `c0-4`, the most economical Pioneer selection actually favoured, is **nose-hindered** by the same lesion:
  blanking food and agent doubles its yield (0.50 to 1.00) and its economy (0.033 to 0.064 items per kJ) on a
  slightly longer path, a >25% change in the harmful direction.

**`c0-8` wiring, since `no_food` halves its yield** (`wiring.txt`). 24 units, 16 sensors, 6 tanh neurons, 2
effectors both driven and both environment-driven, none oscillator-driven, 120 links, mean |weight| 0.87,
centralisation 1.0 (all six neurons global), 6 cyclic units, mean sensor path 2.0. Food sensors on parts 0, 1 and
2 — the chassis and both drive wheels — and agent sensors on the same three parts: the designed Pioneer's stock
nose layout with a random dense controller, the Braitenberg pairing the docs say is available to the designed body
from the start. `c0-4` has the identical descriptor row and the identical sensor placement (mean |weight| 0.886),
which is the point of the pair: same body, same noses, same wiring topology, opposite lesion sign.

## Against the baseline and RBT-18

Baseline and RBT-18 figures from `docs/foraging-world.md` and RBT-18's report.

| | baseline (0.03/kJ) | RBT-18 (0.15/kJ) | this arm (0.08/kJ) |
|---|---|---|---|
| holistic population | 60 → 7 at s11, 60 again by 32, full to 599 | 60 → 2 at s11, extinct at 33 | 60 → 3 at s11, extinct at 26 |
| pre-wave bleed, holistic s4–s10 | not in the docs | not reported | 23 deaths, 15 of them starvation |
| wheeled population | kept 16 of 60 at s39, full to 599 | 31, 8, 2, 0 over s0–s3 | 39, 28, 15, …, 0 over s1–s13 |
| wheeled deaths in season 0 | not in the docs | 30 | 2 |
| wheeled mean gain, first/last season alive | +0.96 at s100 | -1.60 → -0.47 (s0–s2) | -1.161 → +0.498 (s0–s11) |
| children born, hol / wheel | full populations for 600 seasons | 1 / 1 | 10 / 16 |
| individuals ever solvent (mean gain ≥ 0.25) | populations at +1.0 and above | 1 holistic | 3 holistic, 3 wheeled |
| holistic founders in final ancestry | 1 of 60 | 1 of 1 at s32 | 1 of 1 at s25 |
| holistic mean gain, s100/300/500/599 | +1.02 / +1.19 / +1.63 / +1.41 | none; +0.32 at s32 | none; +0.294 at s25 |
| holistic best, items per kJ | s100 2.25 on 4.8 = 0.47; s300 1.75 on 2.3 = 0.76 | `h0-7` 0.50 on 1.1 = 0.45 | `h0-7` 0.50 on 1.1 = 0.45 |
| wheeled best, items per kJ | random ~1 on 17.5 = 0.06; s100 1.0 on 20 = 0.05 | `c0-8` 0.88 on 22.9 = 0.038 | `c0-8` 0.038; `c0-4` 0.50 on 15.0 = 0.033 |
| holistic best path, s0 / 10 / 20 | 2.3 / 2.9 / 3.9 m | 2.3 / 2.9 / 2.9 m | 2.3 / 2.9 / 2.9 m |
| sensor lesion on any holistic best | none changes yield | none changes yield | none changes yield |
| nose-dependent controller | Pioneer s0 (5/6 of food), s500 (a brake) | Pioneer s0 only (57%), dead at s2 | Pioneer s0 `c0-8` (57%), dead at s10 |
| nose-hindered controller | s20 and s30 Pioneers eat more blanked | not reported | `c0-4`, the selected survivor: 2x blanked |
| yield heritability, hol / wheel | 0.51 / 0.24–0.39 | not measurable | not measurable (1 / 0 qualifying children) |

## Does making path length cost something, without emptying the world, give sensing a slope?

No, and 0.08 per kJ does not stop emptying the world either, so the "without" half of the question is still
unmet on this seed. But the arm fails differently from RBT-18 and the difference is the result. At 0.15 the
wheeled side was wiped in season 0 before selection could act; at 0.08 it was *sorted* — nobody died of one
season's work, 51 of 60 season-0 rows were net-negative and were removed over thirteen seasons while the population's
mean gain climbed from -1.161 to +0.498, which is the clearest selection for economy on the designed body
anywhere in the fan-out. So 0.08 is inside the range where selection acts on the wheeled side. What it is outside
is the range where a population can recruit: a child gets exactly 1 energy, and at 0.08 per kJ a Pioneer newborn's
13 to 23 kJ of random driving spends that before it can eat twice, so ten of sixteen wheeled children lived one
season or less and the best-fed adult in the run buried all four of its own. On the holistic side the same
coefficient is nearly irrelevant to the median lump (73% spend under 0.1 kJ) and decisive for the tail: 15 lumps
starved in the seasons before the wave, every one of them net-negative over its life, and of the three lumps that were ever solvent, two were 59 seasons
old at the start. The one that was not, `h0-7`, realises 0.385 items a season in a shared arena rather than the
0.50 its solo probe shows, which puts its break-even work cost at 0.135 / 1.139 = **0.119 per kJ** and its net at
0.08 at **+0.044 a season**, a third of the +0.12 that RBT-18's arithmetic projected from the solo figure. It
still bred, four times, as that arithmetic predicted; what the arithmetic could not see is that the offspring of
a lump that eats do not eat, and ten of ten died under the basal cost.

And where selection did get to express a preference about noses, it preferred their absence. The two Pioneer bests
are the same body with the same stock three-nose layout and the same controller topology: `c0-8`, best at season
0, loses 57% of its food when the noses are blanked; `c0-4`, the founder that survived ten seasons of selection
for economy to become the best at season 10, eats **twice** as much with them blanked. That is not a nose getting
worse — both are generation-0 founders, and no child on either side in this run ever became a best or bred — it
is selection on economy choosing the founder whose nose is a hindrance over the founder whose nose works, because at 0.08 per kJ
`c0-8`'s working nose bought 0.5 energy against a 1.8-energy work bill. Charging for path length made the nose's
half-item worth less relative to the wheels' cost, not more. On this seed, at this coefficient, the slope points
away from sensing.

## Contradictions with the docs, stated plainly

1. **"A lump's budget never depended on the work cost"** (`docs/foraging-world.md`, the sparse pair) holds for
   three quarters of the lumps and not for the tail. Of 59 holistic founders, 43 (73%) spent under 0.1 kJ in
   season 0, but five spent over 1.25 kJ, four spent over 3.1 kJ (a whole basal cost at this coefficient) and the
   worst spent 21.6 kJ, which is a Pioneer's budget in a lump's body. RBT-18 made this point about the one lump
   that mattered; the distribution says it is a tail of four or five, and 15 lumps starved in seasons 4 to 10 here
   before the non-eaters' wave arrived, all of them net-negative over their lives.
2. **The docs' fan-out lesson that "a world variant is only informative at a density and economy where random
   founders form a breeding population"** is confirmed and narrowed. RBT-18's arithmetic put the highest
   informative work cost near 0.1 per kJ; that figure came from a solo probe yield of 0.50 items a season, and the
   realised ecology yield of the same individual is 0.385, so the honest break-even for `h0-7` is 0.119 and the
   honest ceiling for a *population* on seed 801 is below 0.08. A further arm on this axis should sit at 0.05 or
   0.04, not at 0.1.
3. **The pre-registered expectations of this package were wrong in both directions.** "The holistic side
   bottlenecks at season 11 and recovers more slowly than the baseline" — it did not recover at all. "The wheeled
   side bottlenecks hard" — it went extinct. "Whether any surviving lineage becomes nose-dependent is the finding"
   — no lineage survived and no individual in the run has a grandparent, so the finding had to come from selection
   among founders instead.
4. **Not a tuning suggestion, but the knob this arm actually landed on is not the work cost.** `birth_cost` = 1 is
   both what the parent pays and all the child gets, so newborn viability is fixed at four seasons of basal cost
   and, for a Pioneer, less than one season of work. Every extinction in the fan-out so far has run through
   newborns or through founders starving on birth energy. I have not changed it and am not proposing a value; it
   is where I would look before another work-cost arm.

## Champions

None to lab. Every best in the run is a generation-0 founder, both populations are extinct, and `h0-7` is the
baseline's lump already described in the docs rather than anything this arm produced. Nothing here is called
anything.

## Files

`runs/RBT-21/W6b-801/` (config.json, history.json, lineage.jsonl, holistic/best_gen0000-0020.json,
conventional/best_gen0000.json and best_gen0010.json; `<kind>/final/` are empty, both populations extinct),
`W6b-801.log`, `history.txt`, `probe.txt`, `probe_asissued.txt`, `lineage_readout.txt`, `wiring.txt`,
`economy_readout.txt`, `economy_readout2.txt`, `economy_readout3.txt`, and this report. `runs/` is gitignored and
was added with `git add -f`.
