# RBT-90 part 2: adversary report

This attacks `runs/RBT-90/part2-readout.txt` (PR #118) and the descent supplement. The bulk was restored with `scripts/durable.sh restore` from `ckpt/rbt-90-<seed>`, all ten at 600/600, into a scratch directory outside the tree. Every configuration matches the committed `config.json`. Every number below comes from a file in this directory.

Source of the rules: the Chaotic tool returns only the newest 20 of RBT-90's 63 comments, so I could not read the 17:03 pre-registration text itself. The rules I apply are the constants in `part2_readout.py`, whose docstring says they are the pre-registration's, and they agree with the runners' quotations of the 17:03 text.

## Re-derivation: holds

- **The pooled readout.** `python runs/RBT-90/part2_readout.py` is byte-identical to the committed `part2-readout.txt` (first line of `seam_probe.txt`).
- **Seed 1's full lab, from the bulk.** `scripts/forage_lab.py … holistic 590 64 120` was run unmodified, in 6 min 44 s. The output (`rederive-lab-1.txt`) is byte-identical to `forage-1/lab.txt` apart from the run path in line 1: gait t −1.47, and `no_osc` at 64/64 unchanged.
- **Seed 807's subsystems, from the bulk.** `runs/RBT-84/champion_subsystems.py` was run unmodified. All six whole-subsystem rows are identical to the committed `subsystems.txt`, `no_osc` +0.000, +nan, 64/64 included (`rederive-subsystems-807.txt`).
- **All ten gait t's.** The `lab` column of `gait_blocks.txt` re-runs `forage_lab.trial` unchanged on seeds 8000–8063. It reproduces the committed gait t on all ten seeds.

## Findings

**F1: "no champion beats its own gait" holds, and on these ten champions it holds by construction. CAVEAT.**
- **The verdict is robust.** I added 8 fresh disjoint blocks of 64 draws per champion (`gait_blocks.txt`). None of the 80 readings reaches +2.5; the largest is +1.84 (807, b1). Pooled over 512 fresh draws, the largest is +1.99 (807).
- **Why it holds.** `path_invariance.txt` runs each champion from one spawn under two different food layouts. On all ten, on 4 of 4 spawns, the centre-of-mass path is identical tick for tick: the maximum difference is 0.00e+00 m.
  - A champion whose path ignores the layout meets its real layout as just one more draw from its own null, so E[items − null] = 0 exactly.
  - So the regularity says nothing about the null's strength. The null is not too strong. There is no food-responsive behaviour for it to test.
  - The power ladder shows the null could detect a compass. No champion has one to detect.
- **Also a caveat.** All ten champions are read on one shared block of real layouts. Per-draw (items − null) correlates across champions: mean r +0.131, max +0.398. The committed block is the most negative of the nine blocks (mean t −0.93, against −0.61 to +0.41 for the fresh blocks). So "10/10" is not ten independent readings, although no block puts any champion over the bar.
- **Wording I'd use:** "no champion's path responds to the food layout (10/10)". It is exact, and it entails the gait row.

**F2: "drive is not an oscillator": `no_osc t = +nan` is a real measurement, not a broken instrument. The clause is structural, and the lesion cannot contradict it at n = 64. CAVEAT.**
- **Why every row reads nan.** The lesion zeroes an oscillator's outgoing column (`W[:, i]`, and `W` is `[dst, src]`, `brain.py`), which is correct. From `static_wiring.txt`:
  - 9/10 champions carry no linked oscillator at all.
  - 807's one linked oscillator (unit 15, into units 17 and 23) has no directed path to a live effector.
  - So **0/10 champions carry an oscillator that can reach an effector**, and the lesion is a no-op by construction. A zero-variance difference gives t = nan, and the readout scores `abs(nan) >= 2.5` as False, which is "holds".
- **Positive control: does the instrument register a live oscillator at all?** I ran the same unmodified `champion_subsystems.py` on bests that carry a live oscillator (`osc-control-*.txt`):
  - seed 3 gen 560: `no_osc` +0.297 items, t +1.04, 25/64 zeros;
  - seed 2 gen 580: −0.094, t −0.41, 22/64 zeros;
  - seed 806 gen 340: +0.000, 64/64 zeros. Its oscillator has a static path to an effector, but the path is functionally dead: a saturating unit. So static "live" is an upper bound on function, and "0/10 live" is the safe direction.
  - So the instrument does register an oscillator where one acts. At n = 64 it would not have cleared 2.5 for these effects (power line +0.74 items on seed 3).
- **What the clause rests on.** It rests on the static fact plus the top-unit reading. The lesion arm could not have contradicted it for any contribution of this size. The coordinator's suspicion is confirmed in substance.
- **Wording I'd use:** "no champion carries an oscillator with a path to a live effector (10/10)". This is decidable without simulation, and stronger.

**F3: "holistic median depth in [15, 26]" is not a test of the search. It is met with no selection on reproduction at all. MUST-FIX (the label).**
- **Random-parentage null** (`depth_parentage_null.txt`). It keeps each run's own record of who was alive when, from `lineage.jsonl`, and draws every birth's first parent uniformly from those alive the season before. Across 200 replicates per seed and fauna, the replicates land inside the interval with shares from 0.91 to 1.00, mean 0.98.
- **The designed fauna** is inside on 10/10 too (18.0–22.0).
- **A cruder neutral schedule null** (`depth_null.txt`) gives 0.93 with uniform deaths and 0.01 when the oldest die first. So the interval tests the economy's mortality regime.
- **Required change.** The verdict should read "a property of this economy's demography", not "of the search". The pre-registered count (10/10) itself stands.

**F4: the oscillator SPLIT's counts hold. "A founding-population property" does not follow, and the evidence points to run history. MUST-FIX (the gloss).**
- **Credit.** The counts are clean and bimodal: discarded 0, 0, 1, 0, 2 against acquired 16, 10, 18, 39, 9, with none in 3–7.
- **Outcome tracks which founder's line won** (`split_probe.txt`). The founder(s) that all the living trace to by first parent carry a linked oscillator on 3/5 acquired seeds (806, 2, 3) and on 0/5 discarded seeds.
  - That winner is a run outcome, not a property of the founder set.
- **Two seeds acquired without a carrying winner** (`static_wiring.txt` origins):
  - 807 acquired through non-winning founders plus de novo births.
  - 4 acquired entirely de novo: all of its distinct oscillator-carrying bests trace to mutations born in seasons 127–332, and none to a founder.
- **Early rates at birth do not predict the fate.** Seasons 1–100: 805 0.212 and 7 0.200 were discarded; 4 0.036 was acquired; 1 0.034 was discarded.
- **Founders' rate does not predict it either.** r = +0.30, and the founders' counts overlap completely across the two fates.
- **"Drive" overstates what is counted.** "Linked" oscillator (`wiring()['osc_linked']`: any outgoing link) is carriage. No champion carries a live one (F2), and in the controls a best's oscillator costs −0.09 to +0.30 items, or nothing at all (806 gen 340).
- **Required change.** Report the split as "varies across runs; founding population and history are not separated by one run per population". The decisive test is replicate runs from the same founders with a different breeding stream (RBT-95's per-fauna streams), on the 2+2 seeds nearest the boundary.

**F5: effector drive, NOT DECIDED. Credit the readout; nothing to fix. NONE.**
- One added observation: 806's and 807's champions have no sensor at all with a path to a live effector (`static_wiring.txt`, "any env sensor live False"). They are open-loop bodies, so for them "drive kind" is which unit carries a pattern generator, not which unit carries a response.

**F6: descent seam. No scored regularity reads `descent.txt`. Confirmed. NONE.**
- `seam_probe.txt` perturbs the inputs on a copy of the tree and runs the unmodified readout on it.
- Swapping every `descent.txt` for `descent-590.txt` changes exactly the 5 DAG rows (804, 806, 2, 3, 7) and no tally or verdict line.
- Replacing every `descent.txt`'s numbers with junk changes only the 10 DAG rows.
- The positive control works: setting `oscillator.txt`'s distinct count to 5 on every seed does move the verdict lines.
- The readout does open `descent.txt`, so it would crash if the file were missing, but no verdict depends on its contents.

## Summary

Two findings are MUST-FIX, and both are about labels, not counts:
- **F3:** depth is a property of the demography, not the search.
- **F4:** the split is not shown to be a founding-population property.

Two are CAVEATs:
- **F1:** the gait row holds by construction, because the champions are layout-blind.
- **F2:** "not an oscillator" is structural, and the lesion lacks power.

Every count in the pooled table re-derives, and none changes.
