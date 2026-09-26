# RBT-102 adversary

The claim is PR #122 (`runs/RBT-102/`). Applied without the magnitude gate to RBT-90 part 2's ten
arms, RBT-91's structural predicate finds 0 carriers of the routed compass structure in 12,276
genomes, and the verdict is NOT HELD.

**Summary.**
- The count reproduces exactly, and the instrument does see carriers.
- The verdict stands, but it is also what pure drift gives on these arms. On a matched null, 81% of
  drift replays read zero, and the pre-registered rule returns NOT HELD on 91 of 100 of them.
- The report's drift reference (RBT-91's 0.042%) comes from different parents. The matched drift
  rate is about 5.5 times lower.
- The post hoc "barrier" in §2.5 is not specific to selection.

There is no MUST-FIX. Two text caveats should go into the report.

Every number below comes from a file in this directory.

| file | what it is |
|---|---|
| `reproduce.txt` | probe 1: the committed `analyse.py`, unmodified, on all ten restored arms |
| `detect.py` / `detect.txt` | probe 2: can the instrument see a carrier? |
| `replay_null.py` / `replay_null.txt` / `replay_null-rows.txt` | probe 3: the matched drift null, one JSON row per arm and replay |
| `scope.py` / `scope.txt` | probe 4: what was read, and the global-only clause |

The arms were restored with `scripts/durable.sh restore runs/RBT-90/forage-SEED rbt-90-SEED`. All
ten MANIFESTs were at 600/600, and no restore printed the mid-write WARNING.

## F1: the count re-derives exactly. NONE.

I ran `runs/RBT-102/analyse.py`, unmodified, on all ten restored arms (the brief asked for two).
- Seven arms are byte-identical to the committed `arm-<seed>.txt`, ignoring the wall-time line.
- Seeds 2, 3 and 804 differ only in line 1, which is the arm's path. The committed files name the
  author's scratchpad.
- Summed over the ten SUMMARY lines: **12,276 genomes, 592 founders and 11,676 births**, with
  0 carriers born, 0 founder carriers and X = 0 in every arm.

`scope.txt` confirms the genome-file count independently: 12,276. Credit: the committed readouts
are exact derivations from the bulk.

## F2: the instrument can see a carrier. NONE. The result is not UNDETECTABLE.

RBT-102's positive control installs a motif and calls the predicate on it directly. `detect.txt`
tests more than that.

**(a) Natural carriers.** RBT-91 has no drift *arms*. Its drift evidence is 200,000 independent
19-step lineages, and the 84 arrivals among them are the only genomes known to carry the structure
without having it written in. I regenerated 24 of them exactly, 12 per pool, using RBT-91's seeding.
Each was saved to JSON and read back through **RBT-102's own `read_genome`** under **part 2's
SimConfig**.
- 24 of 24 were detected, both on their own synthesis and through RBT-102's reader.
- P-801's synthesis config is identical to part 2's.
- The links-alone gains of these carriers run from 0.0000 to 0.87, all sub-paying. That is exactly
  the regime the claim is about.

**(b) RBT-97's route.** I installed RBT-87's motif on P-801 `best_gen0590` at w = 0.25, 1, 8 and 16,
both signs, and read it through the same reader. It was detected 8 of 8. The bare genome read no.

**(c) End to end.** I copied a restored arm (seed 4) and overwrote the genome files of 24
individuals alive in the window: 12 with the motif installed at w = 1 (sub-paying) and 12 with
natural RBT-91 carriers. I then ran `analyse.py` on the copy, unmodified and with the probe on. It
reported:
- X = 3.9722%, equal to the planted expectation;
- 269 seasons with a carrier, equal to the seasons the planted individuals are alive;
- 24 window carriers, of which it signed 6 as compass, 17 as anti-compass and 1 undetermined.

The whole pipeline, including the name mapping, the living sets, the window and the signing, turns
a planted carrier into a reading. So the zero is a reading.

## F3: NOT HELD is what drift alone produces on these arms. CAVEAT, with a text change requested.

The brief asks whether 0 in 12,276 is significantly below drift, with the same predicate, the same
counting and comparable depth. RBT-91's rate cannot answer that, because it comes from other
parents, one depth and independent lineages. So `replay_null.py` builds the matched null.
- For each arm, take its **own founders** and replay its **own pedigree**: every birth, with the
  same first parent and crossover partner.
- Each birth goes through the conventional branch of `ecology._breed`: `crossover_controller` when
  there is a second parent, then one `mutate_controller` with the arm's own MutationConfig.
- The replayed genomes are never scored, so nothing selects on them.
- This keeps RBT-102's counting unit exactly: the same 12,276 genomes, the same depth for every
  genome, and the same shared ancestry.

Results over 100 replays of the ten arms (`replay_null.txt`):

| quantity under matched drift | value |
|---|---|
| **expected carriers among 12,276 genomes** | **0.93** (median 0, range 0–24; heavy-tailed) |
| carrier fraction | 0.0076% of genomes |
| expected de novo arrivals | 0.34 (range 0–10) |
| **ten-arm sets reading zero, RBT-102's observed outcome** | **81 of 100 = 81% [72, 87]**, so P(0 \| drift) ≈ 0.81 |
| pre-registered verdict rule applied to each drift set | **NOT HELD 91**, UNRESOLVED 9, HELD 0 |

**What holds.** The report already says zero "does not show that selection holds the structure
*below* drift". Its estimate of about 0.26 de novo arrivals (P(0) ≈ 0.77) matches the matched
null's 0.34 and 0.81. That is honest and correct, and I credit it.

**What needs saying.** The verdict carries no information about selection. The same rule, applied
to populations that are never selected on, returns NOT HELD 91% of the time. Two places in the
report read stronger than that:
- The headline: "the routed motif's structure is **not carried at all**".
- §2.6: "there is no sub-paying structure for a magnitude barrier to be withholding … the package's
  question … is answered **no**".

The accurate statement is this: the structure is so rarely proposed from these founders at these
depths (about 1 carrier expected per 12,276 genomes) that ten arms of this length cannot tell
selection holding it from drift, or from selection purging it. PREREG §5 already implies this,
since HELD needed at least 4 arms at about 1.7% or more. That is about 220 times the matched drift
carriage. **Requested:** one sentence in the headline and one in §2.6 quoting P(0 | matched drift)
≈ 0.81 and the rule's 91% NOT HELD rate under drift.

**The naive comparison, for the record.** Pricing 12,276 genomes at RBT-91's 0.042% would predict
5.2 carriers and P(0) ≈ 0.006, which would wrongly suggest selection purges the structure. The
report does not make this comparison. It is recorded here because the next reader might (see F4).

## F4: the drift reference is from different parents, about 5.5 times too high. CAVEAT.

§2.4 puts part 2 and RBT-91 "on one denominator". The denominator matches, but the population does
not.
- RBT-91's parents already wire wheel noses into the global brain: 1 of 7 W4b-801 bests and 7 of 60
  P-801 final-60 have at least one such link.
- Part 2's founders have none: 0 of 60 on seed 4 (`detect.txt` (d)).
- On part 2's own tree, drift carriage is **0.0076%**, against RBT-91's **0.042%**.

The verdict does not move, because U = 0 sits below any p_u ≥ 0. Three things do change:
- "the interval does not exclude drift's rate" should cite the matched rate;
- the pre-registered p_u was built on the wrong population;
- any follow-up must pre-register against a matched replay null, not against RBT-91's rate.

## F5: the post hoc "barrier" (§2.5) is not specific to selection or to the economy. CAVEAT.

§2.5 says that "under selection in this economy, wheel-nose input to the global brain is rare, and
it never occurs on both sides", and §2.6 calls the second nose-to-global link "the binding
structural barrier in this economy". The same replay, with no selection, gives:

| over all genomes | real arms | matched drift, mean (range) over 100 sets |
|---|---|---|
| at least 1 nose into a global unit | 956 | 1,244 (501–2,288); 26 of 100 sets ≤ 956 |
| both noses into one global unit | 0 | 7.7 (0–196); **35 of 100 sets read 0** |
| out-half | 11,044 | 11,089 |

The real values sit inside drift's range. The rarity of nose input is set by the operator and by
random founders, not by selection or the economy. Per arm the picture is mixed:
- Seeds 1, 4 and 805 look suppressed: 24 against 140.6, 21 against 113.5, and 68 against 153.1.
- Seed 807 is elevated: 238 against 126.5.

That is a pattern a pre-registered follow-up could test against this null. The report already
labels §2.5 post hoc and not verdict-bearing (credit). **Requested:** drop "under selection" and
"in this economy" from the barrier sentences, or cite the drift comparison beside them.

## F6: scope. Nothing excluded could carry the structure. NONE.

- **Fauna.** Conventional (Pioneer) only. The holistic fauna has no wheel noses, so the predicate is
  undefined there, and the two faunas never merge (`merge_after` null). Accepted.
- **Genomes.** Every genome saved at birth: founders, births, and the 8 founders never logged. This
  is not survivors only. X is computed over the living, but the headline count covers everything
  born.
- **Seasons.** 0–599 in every arm (`scope.txt`).
- **The global-only clause.** A wheel brain may take a link from a neighbouring node, so a root-local
  neuron could in principle route the motif, and RBT-91's predicate would not look at it. But **no
  part-2 genome has a local neuron at all (0 of 12,276)**, because `mutate_controller` adds units to
  the global brain only. Applied to every non-sensor unit, local or global, the predicate's rule
  finds 0. Nothing is hidden by the clause.

## F7: the committed readouts for seeds 2, 3 and 804 name a scratchpad path. NONE, cosmetic.

Line 1 of these three files names a `/tmp/...` directory, not `runs/RBT-90/forage-SEED`. Everything
below that line is identical to the re-run (F1).

## What holds

- The count, 0 in 12,276, is exact and re-derives from the bulk.
- The instrument sees natural and installed carriers, both through RBT-102's reader and end to end.
- The pre-registration was honoured, and the verdict NOT HELD follows from its rule.
- The report's refusal to claim "below drift" is correct, and its de novo estimate matches the
  matched null.

What does not hold is any reading of NOT HELD as a statement about selection. On these arms, drift
gives the same verdict 91% of the time.
