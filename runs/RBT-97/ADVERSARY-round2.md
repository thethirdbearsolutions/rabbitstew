# RBT-97 adversary, round 2: the report (PR #79) and the answer (PR #86), re-derived and read together

Branch `results/RBT-97-adversary`, with integration `1a4e945` merged in. Every number the author
quotes was re-derived before any judgement below. I re-ran the author's own `bout()` for exactly
two things: the rotated decoy, whose per-robot values are not in the committed readouts, and g500
per seed.

| role | file |
|---|---|
| the P-801 phantom table from its committed per-robot rows | `adversary_round2.py` → `adversary_round2.txt` |
| the W4b control table from its committed rows | `adversary_round2.py` → `adversary_round2_w4b.txt` |
| the fixed verdict line on the round-1 synthetic arms | `adversary_verdict.py` → `adversary_verdict.txt` |
| the rotated decoy per robot and by rotation angle (re-run, 4,480 bouts) | `adversary_rotated.py` → `adversary_rotated.txt` |
| g500 per seed, all five conditions (re-run, 576 bouts) | `adversary_g500.py` → `adversary_g500.txt` |
| the routed motif, from its committed rows | `adversary_routed.py` → `adversary_routed.txt` |

## Verdict

**The headline stands. P-801's compass gain is food-dependent at a = 64 and a = 384 on both
decoys, and the routed motif, the circuit drift can actually build, pays on P-801 at a = 32 and
a = 64.** Every quoted figure reproduces. The author did all six owed items, and pre-registered the
two new conditions before they ran.

Four things remain on the record. None of them moves the P-801 verdict.

## 1. The gait branch: fixed, and shown to be live on real data

On the round-1 synthetic arms, the line at `8713a0d` returns GAIT **0.96 at a = 64 and 1.00 at
a = 384** when true retention is 1.0. The merged line returned 0.17 and 0.16. The food-dependent
side is unchanged (0.96 and 1.00 at R = 0).

The real data now also exercise a non-food verdict. W4b at a = 64 on the static decoy returns
**UNRESOLVED at 25.2%**. So the instrument can say something other than "food-dependent". I
reproduce the 25.2% and its verdict under all three rules.

## 2. The W4b phantom control: exact, but at a = 64 it is not a clean collapse

Motif +1.018 / +1.875 and phantom +0.257 / −0.217 match `docs/artifacts/RBT-67/manipulation_384.txt`
to the digit, on the same seeds. **As a reproduction of the known case, it passes.**

What it shows at a = 64 is a **non-food residual of about 20–25% on the calibration body**:

- Static decoy: +0.257 [+0.053, +0.461], t(df 6), 6/7 robots, 25.2% retention, UNRESOLVED.
- Rotated decoy: +0.217 [+0.025, +0.408], 6/7 robots, 21.3% retention, FOOD-DEPENDENT.

The rotated verdict sits 3.7 points inside a 25% threshold. So the accurate reading for W4b at
a = 64 is "mostly food-dependent, with a resolved non-food component of about a fifth". It is not
"collapses". At a = 384 the collapse is clean on both decoys: −11.5% and −4.9%.

## 3. The rotated decoy against the static one

**Reproduction.** The author's `bout()`, re-run for base, motif and rotated, returns the committed
pooled rotated figures exactly:

| population | a | rotated delta | retention |
|---|---|---|---|
| P-801 | 64 | +0.174 | 5.8% |
| P-801 | 384 | −0.614 | −8.8% |
| W4b | 64 | +0.217 | 21.3% |
| W4b | 384 | −0.092 | −4.9% |

**The per-robot rotated values are not in either committed readout.** The per-robot table has no
rotated column. `adversary_rotated.txt` now commits them. The author should either add the column
to `mechanism.py`'s table or cite this file.

**My round-1 bias concern was right in direction and small in size, and half of it is
withdrawn.**

- Rotated retention exceeds static in three of four cells: P-801 0.8 → 5.8% and −10.7 → −8.8%,
  W4b a = 384 −11.5 → −4.9%. It is lower on W4b at a = 64 (25.2 → 21.3%). The largest gap is
  seven points.
- **The rotated decoy, which depletes exactly like the real field, is also significantly negative
  on P-801 at a = 384: −0.614 [−1.178, −0.049].** So the negative phantom at a = 384 is not an
  artifact of a static attractor. Steering hard on a wrong gradient costs items by itself. I
  withdraw that mechanism.
- Pre-registered predictions scored for P-801: (a) rotated retention above static at both rungs,
  0.75, **holds**. (b) Rotated retention under 25% at both rungs with the motif − rotated interval
  excluding zero, 0.60, **holds** ([+1.018, +4.598] and [+3.780, +11.372]).

**Retention by rotation angle.** This analysis is exploratory and post hoc. The rotated field's
gradient is the true gradient rotated by θ, so a food-dependent gain should shrink as θ moves away
from identity. Mean over bouts:

| \|θ\| | P-801 a = 64 | P-801 a = 384 | W4b a = 64 | W4b a = 384 |
|---|---|---|---|---|
| 30–60° | +44.6% | +9.2% | +44.1% | +29.4% |
| 60–90° | +19.5% | −0.4% | +19.0% | −16.9% |
| 90–120° | +10.1% | −21.9% | +20.2% | −9.1% |
| 120–150° | −1.1% | −5.9% | −3.2% | −24.0% |
| 150–180° | −51.9% | −39.6% | +19.7% | −13.3% |

On P-801 at a = 64 retention falls monotonically with θ, from +45% to −52%. That is food-dependence
seen at a finer grain than the verdict. It also shows the pooled rotated retention is **inflated**
by near-identity bouts, which still carry real direction. So the pooled figure is an upper bound
on the non-food component, and that makes the verdict conservative. W4b at a = 64 is noisier, and
its far bins (+19.7%, se ≈ 0.2 on a 0.9 motif delta) are compatible with §2's residual.

## 4. g500: its sign stands, but its gain is not clearly chemotactic

The direction re-measurement is sound, and the author's withdrawal of "neither sign is clearly its
compass" is correct. g500 drives forward on 63 of 64 bouts under one probe and 64 of 64 under the
other. The low R is spread within bouts, not two modes.

Per seed, though (`adversary_g500.txt`, 64 paired seeds, RBT-38 instrument):

| a | motif − base | rotated − base | antimotif − base | motif − rotated |
|---|---|---|---|---|
| 64 | +1.031, t +1.70, **not separable** | **+1.250, t +2.61** | +0.609, t +0.98 | −0.219, t −0.29 |
| 384 | +1.438, t +2.56 | +0.000, t 0.00 | **+1.234, t +2.11** | +1.438, t +2.34 |

- At a = 64 g500's own gain is not resolved, and the rotated decoy pays at least as much as the
  motif.
- At a = 384 its anti-compass pays nearly as much as its compass.
- **On g500 the gain is largely sign-independent.** The report's line *"whatever g500 gains is
  still food-dependent"* rests on the static phantom alone, and the rotated decoy does not support
  it.
- It is one body of seven. Leaving g500 out moves P-801's rotated retention at a = 64 from 5.8% to
  about 0%, so the pooled verdict is not carried by it. It belongs on the record as the one P-801
  body where the prize has not been shown to be chemotaxis.

## 5. The routed motif on P-801: pays, as pre-registered

From the committed per-robot rows:

- **w = 16 (a = 32): +0.969 [+0.254, +1.684], 6/7**
- **w = 32 (a = 64): +3.018 [+2.026, +4.010], 7/7**

Both PAY under the one-line rule posted before the run. Both point predictions land in their bands:
+0.3 to +1.5 at a = 32, and +1.5 to +3.5 at a = 64.

The W4b routed control on seeds 9000+ reproduces `genotype_motif.txt` exactly (+0.277, +0.879).
Routed and direct agree on P-801 at a = 64: +3.018 against +2.982.

**So "the magnitude drift never reaches is one that demonstrably pays" is now shown on both
populations for a circuit the genotype can represent.** This was round 1's qualification 4, and it
is discharged. The one robot not improved at a = 32 is g100 (−0.078).

Minor: the two routed readouts carry three MuJoCo QACC-instability warnings between them, and no
count of exploded bouts. An exploded robot stops eating, so each cell should print its explosion
count. In my rotated re-run, 4 of 2,240 W4b bouts exploded and none of P-801's.

## 6. Counts: exact

The per-population intervals and the seed-level counts (6/12 at a = 32, 10/12 at a = 64) match
round 1 digit for digit. The correction of "fourteen of fourteen" says exactly what RBT-67's data
hold.

## Credit

- Every owed item was done, and the two new conditions were pre-registered before they ran.
- The gait fix is commented in the code with the reason.
- The two inverted robots are now calibrated through the antimotif against RBT-67, and through the
  motif against PR #11, both exactly. That turns the determinism check into a two-ticket
  cross-reproduction.
- Citing RBT-67's own 25% static phantom on W4b as evidence for the adversary's bias was generous
  and correct.

## What stays on the record, not blocking

1. W4b at a = 64 carries a resolved non-food component of about 20–25% on both decoys (§2).
2. g500's gain is sign-independent and survives the rotated decoy at a = 64 (§4).
3. The per-robot rotated values are committed here, not in the author's readout (§3).
4. Explosion counts are missing from the routed readouts (§5).

Rule II, for this round:

- **Frame:** checked. g500's direction re-read from the committed readout.
- **Calibrate:** checked. W4b motif and phantom against RBT-67, the routed W4b control against
  `genotype_motif.txt`, and the rotated pooled figures reproduced by re-running.
- **Manipulation check:** checked. Retention by rotation angle.
- **Measure:** re-derived from committed rows, and re-run where rows were not committed.
