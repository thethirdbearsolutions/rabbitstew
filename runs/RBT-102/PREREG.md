# RBT-102 pre-registration: does selection hold the routed motif's structure at sub-paying magnitude above drift's proposal rate?

Written 2026-09-26, before any RBT-90 part-2 arm is restored. At the time of writing, the ten
`ckpt/rbt-90-<seed>` snapshots stood at seasons 119–216 of 600 (MANIFESTs 12:43–12:47 UTC). Under
the coordinator's ruling (RBT-102, 13:10), none may be read until its final snapshot is posted on
RBT-90. This file, `analyse.py`, `aggregate.py`, `prereg_inputs.py` and `prereg_inputs.txt` are
committed before the first restore.

## 0. What happened to the original package

RBT-80's saved-at-birth genomes and lineage were **never committed, by design**. Its description
says "genomes and lineage stay out", and `.gitignore` keeps `runs/**` out of the repository except
`.md`, `.py`, `.sh`, `.txt` and `config.json`. No branch holds them, `ckpt/*` included. The W4b-801
founders are not committed anywhere either. A pre-RBT-95 ecology run does not reproduce from its
config. So the bound in `REPORT.md` §1 is all that RBT-80's own data can give. The data for the
question is therefore RBT-90 part 2 (ruling (c)).

## 1. Data, and every difference from RBT-80's control arm

The data are the ten RBT-90 part-2 arms, seeds 1, 2, 3, 4, 7, 801, 804, 805, 806 and 807. Each is
600 seasons, post-RBT-95, with every genome saved at birth. Each is restored with
`scripts/durable.sh restore runs/RBT-90/forage-SEED rbt-90-SEED` only after its final snapshot.
`analyse.py` also refuses any arm whose `state.json` is below 600.

The fauna analysed is the **conventional (Pioneer) fauna only**. The predicate needs wheel `food`
noses and drive Effectors, and the holistic fauna's evolved bodies have neither. The two faunas are
never merged (`merge_after` null).

`part2-dryrun/config.json` is `rabbitstew.cli ecology` run with `part2_run.sh`'s exact flags,
`--seasons 0` and `--seed 999`. Diffed field by field against `runs/RBT-80/seed{A,B,C}/control/config.json`:

| field | RBT-80 control | RBT-90 part 2 | matters? |
|---|---|---|---|
| founders (`seed_conventional`, `seed_holistic`) | `runs/RBT-80/seedX/founders/control`: W4b-801 evolved, backward-driving Pioneers (never committed) | **random fresh founders** (`initial_population`) | **yes.** Part 2 starts naive. RBT-80's control started from evolved directional drivers. |
| `sim.food.regrow` | false | **true** | yes. It is the dense baseline economy (RBT-10/28) and changes what pays. |
| `ecology.seasons` / `generations` | 300 | **600** | yes. The window is placed in the second half (§3). |
| `seed` | 801 / 802 / 803 | 1, 2, 3, 4, 7, 801, 804–807 | the replicate |
| `workers` | 4 | 1 (or 4) | no. The coordinator's ruling says byte-identical. |
| `cull`, `cull_at`, `shift`, `shift_at`, `morph_protection` | absent (pre-dates them) | null / 0 | no. These are off. |

Every other field is identical: the mutation operator (`add_link_rate` 0.15, `remove_link_rate`
0.1, `weight_sigma` 0.4), the ecology economy, capacity 60, crossover 0.3, `fixed_body` pioneer,
`conventional_topology` true and brain model foraging.

**What this cannot give.** RBT-80's *seeded* and *drift* arms have no counterpart in part 2. The
drift comparison is RBT-91's measured proposal rate, **not a matched drift arm**. The mutation-only
chain in `prereg_inputs.txt` is a secondary reference only. It has no crossover and no demography.

## 2. Instruments (imported, not modified)

- **Predicate:** `runs/RBT-91/structural_rate.py:motif_units`, imported through
  `runs/RBT-91/resign_arrivals.py`. A global non-sensor unit qualifies when both wheel noses link
  into it with opposite signs and it links out to both drive Effectors with the same sign. Signs are
  taken on the summed weight per pair. There is no magnitude anywhere.
- **Magnitude beside it** (never gating): `small_signal_a` (whole brain) and `links_alone_a` (the
  predicate unit's own four links), both from `structural_rate.py`. Paying rung: 6.8664.
- **Direction:** `resign_arrivals.heading` at RBT-80's reference probe, 16 seeds × 15 s. The
  undetermined band is `MARGIN` = 15°, RBT-91's: a carrier heading within 15° of sideways leaves
  both numerator and denominator.
- **Re-signing:** RBT-91's rule. `signed = a` when the carrier drives backward (|heading| > 90°),
  else `-a`. Positive is a COMPASS; zero or negative is an ANTI-COMPASS. The rule is a fact about
  the circuit and not about the founders: the published motif is the compass for a backward driver
  (RBT-97). The re-signed quantity is the whole-brain `a`, as RBT-91 signed its 84 arrivals. The
  links-alone sign and whether it agrees are reported beside it.
- **Depth:** reproductions along the mutated line (`parents[0]`), with founders at 0. Each birth is
  one `mutate_controller` call, after crossover in 30% of births (`ecology._breed`). This is RBT-91's
  unit of k.

## 3. Quantities

Per arm (`analyse.py`):

- **C(s)**: carriers ÷ living conventional individuals at season s, for every season 0–599. The
  living set is the `lineage.jsonl` rows for that season, excluding `death` rows.
- **X**: the mean of C(s) over the **window, seasons 300–599**. This is the carriage statistic.
- **Births:** carriers born. **De novo** means no parent carries; the rest are inherited. Also
  reported: births at depth 17–21 carrying (the like-for-like at RBT-91's k = 19), and founders
  carrying.
- **Signing:** every distinct carrier genotype alive at any season in the window, probed once.
  Reported per arm: compass, **anti-compass (the inversion count)** and undetermined.

**The denominator, stated once.** It is *genomes carrying the structure, as a fraction of genomes
present*. For RBT-91 this is lineages after 19 `mutate_controller` steps from committed evolved
parents with no selection: **84 of 200,000 = 0.042% [0.0339, 0.0520]** (Wilson 95%, decision
doc). For RBT-102 it is living conventional individuals, averaged over window seasons, under
selection. The window's mean depth is printed beside X. The drift reference is quoted at k = 19,
whatever depth the window reaches. Drift's expected carriage grows with depth, so a window much
deeper than 19 makes the comparison *favour* HELD, and I will say so if it happens.

## 4. Verdict rule (carriage)

The positive control runs first on every arm and must pass on all ten, or there is **no verdict**.
With the ten arm values X₁…X₁₀, mean X̄ and t(9) 95% interval [L, U] = X̄ ± 2.262·SD/√10, and
p_u = 0.0520% (the upper Wilson bound of RBT-91's rate):

- **HELD ABOVE DRIFT** iff L > p_u.
- **NOT HELD** iff U ≤ p_u.
- **UNRESOLVED** otherwise.

## 5. Resolvable effect size at ten seeds

The half-width is 0.715 × SD. Carriage is likely to be all-or-nothing by arm, so the arithmetic
below takes k arms at a common level c, with the rest at 0:

- **HELD** resolves only if **k ≥ 4**. Then L = 0.031c at k = 4 (0.123c at 5, 0.231c at 6), so
  HELD also needs c ≳ 1.7% at k = 4: about one carrier alive in every window season. With k = 1–3
  arms carrying, L < 0 whatever c is, and the result is UNRESOLVED.
- **NOT HELD** needs U ≤ 0.052%. With one arm carrying, U = 0.326·X_arm, so that arm's X must stay
  ≤ 0.16%. That is one carrier (1/60 = 1.67%) alive for at most about 29 of the 300 window seasons.
  One carrier lineage persisting longer in a single arm makes the verdict UNRESOLVED, not NOT HELD.

## 6. Signing (primary readout of *what* is carried)

- **The inversion count is primary:** the number of anti-compasses among resolved window carriers,
  pooled over arms and given per arm.
- **The compass fraction** is reported with a Wilson interval against the 50% null (sign symmetry
  of the proposal; RBT-91) and against RBT-91's drift arrivals, 42.2% [32.1, 52.9].
- **Selection holding a compass** would show as a compass fraction whose Wilson lower bound
  exceeds 50%.
- **Fewer than 10 resolved carriers** in total means the fraction is reported and **not
  interpreted**.

## 7. Prediction, confidence and falsifier

Inputs, measured without reading any arm (`prereg_inputs.txt`):
- **Founder rate:** part-2 founders carry the structure at 0 of 6,000 [0, 0.064%].
- **Matched mutation-only chain at k = 19:** 1 of 6,000 = 0.017% [0.003, 0.094], consistent with
  RBT-91's 0.042%.
- **Per-birth proposal rate:** about 0.042% / 19 ≈ 2 × 10⁻⁵.
- **Expected de novo arrivals:** RBT-80 realised 5–11 births per slot over 300 seasons, so an arm
  has roughly 600–1,300 conventional births over 600 seasons. That makes about **0.03 de novo
  arrivals per arm and about 0.3 across all ten**. The motif's own links never reach the paying
  rung (RBT-91: 0 of 84), so selection cannot see the motif itself. Anything that arrives drifts or
  hitchhikes.

**Point prediction.** X̄ = **0.000%**, with no carrier alive in any window season in at least 9 of
10 arms, and **verdict NOT HELD**. Confidence **0.65**, with UNRESOLVED at 0.27 (one to three arms
catch a lucky arrival that persists) and HELD at 0.08. Signing: fewer than 10 resolved window
carriers in total (confidence 0.85), so the compass fraction is not interpretable. Inversion
count: 0 to 3.

**Falsifiers:**
- the verdict is HELD, or 4 or more arms have X > p_u;
- 5 or more de novo arrivals across the ten arms (the per-birth reasoning above is then wrong by
  more than 10×);
- 10 or more resolved window carriers with a compass fraction whose Wilson interval excludes 50%.

## 8. Positive control (runs first, in every arm)

In each arm, 20 genomes are sampled uniformly (seed 102) from those alive in the window.
`scripts/genotype_motif.install` (RBT-87's routed motif) is applied at (w = 1, sign +) and (w = 8,
sign −), and the predicate must detect all 40. An install the validator rejects counts against the
control; it does not count as a predicate miss, and it is reported separately. The bare genomes'
carriage is recorded beside it. The dry run on 20 independent part-2 founders detected 40 of 40 and
read 0 of 20 bare.

## 9. Budget, measured before any arm

The predicate costs 0.71 ms per genome, which is about 1 s for about 1,300 genomes. The reference
probe costs 5.2 s per carrier, single core. Four cores and fewer than 50 window carriers per arm
puts an arm under 2 minutes. The first finished arm is analysed alone and its wall time is posted
before the rest. If probing would exceed about 2 h (more than about 5,500 carriers in total), I
stop and say so on the ticket so the work can be split across sessions.

## 10. What is not done

- There is no new evolution and no tuning.
- No part-2 arm is read before its final snapshot is posted.
- The window, rule, probe and margin are fixed above and will not be changed after an arm is read.
- The adversary is named by the coordinator at in_review.
