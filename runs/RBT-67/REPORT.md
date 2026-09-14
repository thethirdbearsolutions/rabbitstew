# RBT-67 — Bound the compass prize: the dose-response past a = 64, per population

**Delegate report, 2026-09-14.** Branch `results/RBT-67`, off the integration branch at
`8390d97`. Harness `docs/artifacts/RBT-67/compass_dose_response.py`; readouts
`docs/artifacts/RBT-67/{w4b,p801}.{txt,json}`, run log `run.log`; pre-registration
`PREREGISTRATION.md`, posted to the ticket before any bout ran. 7,168 bouts. No library code
touched. Full suite 177 passed before the run.

## Verdict

**There is no turnover inside the range on either population. The curve is still rising at
a = 384, credibly above a = 128 on both, with the climb from 192 to 384 unresolved at 64
seeds.** So the prize is not 0.9 items and it is not bounded by this ladder either:

| population | drives | baseline | best rung | Δ items at best rung (95% CI over robots) | robots improved |
|---|---|---|---|---|---|
| W4b-801 (7 bests) | backward | 1.270 | a = 384 | **+1.875 [+1.243, +2.438]** (+148%) | 7/7 at every rung |
| P-801, all seven | forward | 2.770 | a = 384 | +5.150 [+1.056, +8.703] | 5/7 at every rung |
| P-801, the five forward drivers | forward | 2.688 | a = 384 | **+8.094 [+4.694, +10.000]** (+301%) | 5/5 at every rung |
| P-801, the two backward drivers (g100, g400) | backward | 2.977 | — | −2.211 at a = 384, negative at every rung | 0/2 at every rung |

My pre-registered bet was *peak and turn over* at 0.60 / 0.55. It was wrong on both
populations; the outcome I gave 0.15 / 0.20 is the one that happened. The pre-registered
sharp prediction on P-801 — that the population-level sign anti-compasses g100 and g400 and
"improved" never exceeds 5/7 — held at every rung.

## 1. Frame: direction of travel, measured in this session

`scripts/travel_direction.py` (taken verbatim from `claude/rbt-45-2oa635`, blob `37b98b2`),
run before anything was installed; readouts in `docs/artifacts/RBT-67/travel_direction_*.txt`.

| population | per generation (travel azimuth − body yaw) | pooled | sign used |
|---|---|---|---|
| W4b-801, gens 90–590 | −179.0, +178.6, −168.9, +179.1, −166.1, −171.9, −173.0 | **−174.1°, R 0.756 → BACKWARD** | published motif (+1) |
| P-801, gens 0–590 | −0.1, **+177.9**, −2.9, −0.2, **+169.5**, +16.6, +3.2 | **+9.7°, R 0.325 → FORWARD** | opposite (−1) |

The ticket fixes the sign per population, and that is what was installed. Per generation
(standing rule (c)), P-801's g100 and g400 drive backward, so the population sign is their
anti-compass; PR #11 measured the same two independently. Their rows are in every table
rather than dropped, and the forward-five subgroup is reported alongside the population mean.

## 2. What was installed, and what was read back

`k = a/2` on each of the four links through `scripts/compass_replication.py::install`, which
derives them from `drive_commands(steering=±k, throttle=0)`; the pair delivers `2k(n_L − n_R)`
= `a(n_L − n_R)` to the effector sum. `readback()` asserted on every robot and rung that the
depth-1 change in the path-sum `a` equals the signed installed `a` and the change in `c` is
zero — all 98 assertions passed. Realised `a` at depth 4 (motif.py's quantity), a = 64:

| | g90 | g190 | g290 | g390 | g490 | g550 | g590 |
|---|---|---|---|---|---|---|---|
| W4b realised a | +64.0 | +64.1 | +64.0 | +64.6 | **−82.8** | +64.0 | **+127.2** |
| | g0 | g100 | g200 | g300 | g400 | g500 | g590 |
| P-801 realised a | −64.0 | −64.0 | −64.0 | −64.0 | −64.6 | **+598.3** | −70.0 |

Five nominal, one doubled, one sign-reversed on W4b — exactly the ticket's calibration note,
and now explained: **the depth-4 signed path sum is a linearisation and it diverges on the
robots whose drive effectors sit in loops with |w| > 1.** g490 has a self-loop of −1.827 on
its left drive effector (the alternating series 1 − 1.83 + 3.34 − 6.10 is what "−82.8" is);
g590 feeds its right effector into the global brain at +1.466; P-801's g500 carries evolved
nose wiring (`a_evolved` +6.79, `c` −4.32) through loops that blow the sum up to +598. The
depth-1 term is exact and equals the installed value on every robot. So "realised a" is
reported, as the ticket asks, but on those three robots the number is the readback failing,
not the install. `|a|/|c|` is in the thousands on W4b and infinite (c exactly 0) on six of the
seven P-801 robots: **the common mode is not creeping in and cannot be what limits the curve.**

The behavioural side of the same three robots is worth a line: g490 is the one W4b robot whose
gain does not grow with a (+0.61 at 32, +0.27 at 384); g590 saturates earliest (flat from
128); g500 is flat at about +1.2 at every rung and is the least directionally committed robot
in either set (+16.6°, R 0.63). Whatever the loops do, it is not nothing.

## 3. W4b-801 — the source population

Nose gradient on this substrate: level 0.007–0.705, left-right gap median 0.038 (p95 0.074),
so a × gap runs 1.2 (a = 32) to 14.6 (a = 384) pre-tanh units. Baseline 1.270 items on seeds
7000–7063 against the source's 1.516 on 9000–9063 — a seed-set difference of 0.25 items on
448 bouts, worth knowing when comparing 64-seed baselines across tickets.

| a | items | Δ | 95% CI (robots) | improved | zero Δ / zero-item bouts (of 448) | in-disc m | items/m | rail % |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.270 | — | — | — | — / 152 | 5.40 | 0.238 | 0.0 |
| 32 | 1.705 | +0.435 | [+0.317, +0.571] | 7/7 | 183 / 128 | 6.29† | 0.335 | 0.5 |
| 64 | 2.288 | **+1.018** | [+0.600, +1.460] | 7/7 | 110 / 91 | 4.98 | 0.457 | 1.5 |
| 96 | 2.603 | +1.333 | [+0.842, +1.839] | 7/7 | 102 / 72 | 8.84† | 0.450 | 2.6 |
| 128 | 2.683 | +1.413 | [+0.817, +1.982] | 7/7 | 96 / 83 | 4.97 | 0.530 | 4.7 |
| 192 | 2.897 | +1.627 | [+1.011, +2.165] | 7/7 | 74 / 82 | 4.95 | 0.577 | 9.3 |
| 256 | 2.904 | +1.634 | [+0.962, +2.237] | 7/7 | 80 / 79 | 5.02 | 0.571 | 13.3 |
| 384 | 3.145 | **+1.875** | [+1.243, +2.438] | 7/7 | 66 / 60 | 5.03 | 0.618 | 18.8 |

† one exploded bout in the cell (g290 at 32, g390 at 96/128) inflates that robot's path
metres (16 m and 33 m in a 15 s bout); 8 exploded bouts in 3,584, two of them at baseline.

**Anchors.** a = 64 reproduces the source: +1.018 [+0.600, +1.460] against +0.897 [+0.632,
+1.176], 7/7 both times. a = 32 is higher than the source (+0.435 [+0.317, +0.571] against
+0.246 [+0.147, +0.353]); different seeds and a lower baseline, and I would not read more into
it than that.

**Shape.** Monotone in a. Paired over robots: Δ(384) − Δ(64) = +0.857 [+0.219, +1.562];
Δ(384) − Δ(128) = +0.462 [+0.036, +0.908]; Δ(384) − Δ(192) = +0.248 [−0.098, +0.616]. The
climb is credible to 128 and unresolved from 192 on. Per robot: g290 (+0.42 → +3.11) and g190
(+0.31 → +1.47) are still climbing hard at 384; g390, g550, g590 are flat from about 128;
g490 falls.

**Where the items come from.** Items per in-disc metre rises monotonically, 0.238 → 0.618,
while in-disc path stays at 5.0 m from a = 64 up. The gain is steering, not coverage. The
zero-item bouts fall from 152 to 60 of 448: the compass mostly converts empty bouts into
fed ones.

## 4. RBT-19/P-801 — the second population, opposite sign

Nose gradient: level 0.168–0.860, gap median 0.056 (p95 0.086); a × gap 1.8 to 21.5. Baseline
2.770 items (RBT-69 measured 2.770 on the same seeds and robots — the harness agrees with its
parent to three decimals on the condition they share).

| a | items | Δ (all 7) | 95% CI | improved | Δ forward five | 95% CI (5) | Δ g100 | Δ g400 | items/m | rail % |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 2.770 | — | — | — | — | — | — | — | 0.615 | 5.8 |
| 32 | 3.083 | +0.312 | [−0.714, +1.172] | 5/7 | +1.009 | [+0.541, +1.509] | −2.33 | −0.53 | 0.764 | 3.1 |
| 64 | 4.605 | +1.835 | [−0.033, +3.629] | 5/7 | +3.206 | [+1.969, +4.525] | −2.19 | −1.00 | 1.089 | 3.3 |
| 96 | 6.065 | +3.295 | [+0.516, +5.944] | 5/7 | +5.275 | [+3.125, +7.069] | −2.66 | −0.66 | 1.341 | 4.4 |
| 128 | 7.286 | +4.516 | [+1.009, +7.692] | 5/7 | +7.006 | [+4.031, +8.891] | −2.50 | −0.92 | 1.547 | 5.4 |
| 192 | 7.734 | +4.964 | [+1.163, +8.478] | 5/7 | +7.588 | [+4.281, +9.787] | −2.72 | −0.47 | 1.695 | 8.8 |
| 256 | 7.641 | +4.871 | [+0.967, +8.312] | 5/7 | +7.559 | [+4.266, +9.738] | −2.80 | −0.91 | 1.695 | 10.9 |
| 384 | 7.920 | **+5.150** | [+1.056, +8.703] | 5/7 | **+8.094** | [+4.694, +10.000] | −2.86 | −1.56 | 1.783 | 14.7 |

The population CI is wide because it mixes four robots at +9 to +10 with two at −2 to −3 and
one flat at +1; that is the pre-registered consequence of a per-population sign on a
population whose direction is per-generation, shown rather than averaged away.

**The forward four** (g0, g200, g300, g590; baselines 2.5–3.2) go to 10.4, 9.4, 9.5, 9.8 items
at a = 384 — roughly four times baseline, and g0 goes from 35 zero-item bouts to 8. **The two
backward drivers** lose at every rung: g100 stops eating almost entirely (60 of 64 bouts at
zero by a = 384, in-disc path 4.15 → 1.67 m — it leaves the disc), g400 loses 0.5–1.6.
**g500**, forward but weakly (+16.6°, R 0.63) and the only forward driver with evolved nose
wiring, is flat at about +1.2 at every rung.

**Shape.** Monotone. Paired over the forward five: Δ(384) − Δ(128) = +1.087 [+0.503, +1.641],
Δ(384) − Δ(192) = +0.506 [−0.131, +1.147]. Same reading as W4b: credibly climbing to 128,
unresolved past 192. Items per in-disc metre 0.615 → 1.783 on flat in-disc path (4.0–4.3 m):
steering again. 4 exploded bouts in 3,584, none at baseline.

## 5. The pre-registration, scored

| prediction | W4b | P-801 |
|---|---|---|
| shape: peak and turn over (0.60 / 0.55) | **wrong** — keep climbing (given 0.15) | **wrong** — keep climbing (given 0.20) |
| peak Δ between +1 and +2 (W4b); +1 to +3 on the forward five (P-801) | +1.875 and still rising: inside the band, but the band was a ceiling and there is no ceiling | **wrong by a factor of three** — +8.1 |
| rail % rises monotonically with a | right (0.5 → 18.8) | right (3.1 → 14.7); predicted > 50% at 384 — **wrong** |
| in-disc path falls past the peak, items/m does not | no peak; path flat, items/m rises monotonically — the throttle-loss mechanism is present and never binds | same |
| a = 64 anchor inside [+0.632, +1.176], 7/7; a = 32 near +0.25 | 64: right; 32: +0.435, above | — |
| realised a within 20% with the installed sign on all seven | **wrong** on g490 and g590 (§2: a readback failure) | wrong on g500 (same) |
| \|a\|/\|c\| ≥ 5 everywhere | right (thousands) | right (infinite) |
| g100 and g400 lose at every rung ≥ 64; improved ≤ 5/7 at every rung (0.80) | — | **right at every rung** |

The one thing I got right about the mechanism is that both effectors do pin together more
often as a rises. What I got wrong is the consequence: at 19% of ticks pinned the robot still
gets to the food, and the extra steering is worth more than the lost throttle. The dead-band
argument (translation only when the noses agree to within ~1/a) predicts a 1/a loss of
distance that the flat in-disc path does not show. Both wheels pin with the same sign only
when the steering term outweighs the evolved throttle term on *both* effectors at once, and
the rail column says that is about a fifth of the ticks at a = 384, not most of them; the
rest of the time one wheel is pinned and the other is not, which is a hard turn that still
translates.

## 6. What it does not settle

- **Whether it is still chemotaxis at a = 384.** The manipulation check (travel-frame bearing,
  phantom smell) was run by RBT-69 at a = 64 only and not here. Items per in-disc metre
  tripling on flat path, and zero-item bouts collapsing, are what a compass would do; they are
  not the travel-frame measurement. Cheap to add: `compass_mechanism.py`'s phantom arm at 384.
- **Where the curve ends.** Credibly above 128, unresolved past 192, best at the top rung. A
  ladder to 768 and 1536 would take twenty minutes; I did not run it because the package was
  scoped to 384 and "keep climbing" was a pre-registered outcome to report, not a reason to
  chase.
- **The readback instrument.** `motif.py::steering_gain`'s depth-4 sum should carry a guard for
  loops touching the effectors, or report the depth-1 term alongside; three of fourteen robots
  here return numbers that are not the gain they realise. Filed as a note for RBT-45's author
  rather than fixed, since the script is theirs and on their branch.
- **The population-sign design on P-801.** Two of seven robots were anti-compassed by
  construction. Per-robot signs would have been the sharper experiment; it was not the scoped
  one. The forward-five column is the number RBT-65 should read if it seeds this population.

## 7. What it feeds

- **RBT-65** picks a seeding gain from this curve: on either population the compass is worth
  more at 128 than at 64 (credibly) and is not worse at 384. a = 32 there is a marginal test by
  design; a second arm at 128–192 sits at about 90% of the top of this ladder.
- **RBT-42**'s target magnitude: a ≥ 128 in path-sum units, i.e. k ≥ 64 per link on this body,
  against an operator whose largest single-mutation draw was 2.075 (RBT-77).
- **The "+59% lower bound"** in *The transposed drive* can be restated: at least +148% on the
  W4b bests (+1.875 on 1.270, a = 384, 7/7), and about +300% on P-801's forward drivers with
  their own sign — and both are still lower bounds.

## 8. Files and reproduction

| file | what |
|---|---|
| `docs/artifacts/RBT-67/compass_dose_response.py` | the harness (both populations, ladder, readback, analysis) |
| `docs/artifacts/RBT-67/PREREGISTRATION.md` | written before the run; unchanged since |
| `docs/artifacts/RBT-67/w4b.txt`, `p801.txt` | readouts, including every per-seed difference per robot and rung |
| `docs/artifacts/RBT-67/w4b.json`, `p801.json` | every cell, robot, readback and turnover statistic |
| `docs/artifacts/RBT-67/travel_direction_w4b.txt`, `_p801.txt` | direction of travel, this session |
| `docs/artifacts/RBT-67/run.log` | stdout/stderr of the run, including the 11 MuJoCo instability warnings behind the 12 exploded bouts |
| `docs/artifacts/RBT-23-W4b-801/` | the seven source bests and their config, taken from `claude/rbt-45-2oa635` (blobs identical) |

From the repository root: `python docs/artifacts/RBT-67/compass_dose_response.py 64 4 both`,
about 14 minutes per population on four cores. The subgroup and climb statistics in §3–4 are
computed from the JSON with the snippet in the ticket comment; everything else prints.

## 9. A note on how this ran

This session was blocked for its first half-hour: the shell permission layer refused every
state-changing command and the container had no numpy or mujoco, so the harness and
pre-registration were written and pushed through the GitHub API with no ability to execute
either, and the ticket was told so. The block lifted on a later attempt; from there the run
went as the README said it would. The pre-registration was posted before that happened, so it
stands as written.

## 10. Follow-up, after acceptance: the two open items in §6, and the adversary's first attack

Run at the coordinator's request after PR #14 merged. Scripts and readouts in
`docs/artifacts/RBT-67/` (`manipulation_384.py`, `seedset_anchor.py`, their `.txt`/`.json`/`.log`).

**The seed set is the whole of the baseline gap.** The ladder's own `bout()` at a = 0 and
a = 64 on the source's seeds 9000–9063 returns **baseline 1.516, Δ +0.897 [+0.632, +1.176],
7/7, per-robot [0.44, 0.47, 0.70, 1.09, 0.84, 1.23, 1.50]** — every figure identical to
`verify_independent.py`'s readout on those seeds. Two independently written harnesses agree
to the last decimal on the same seeds, and the 1.270 the ladder read on seeds 7000+ is what
those seeds give. A quarter of an item between two 64-seed sets is worth remembering when
any two tickets' baselines are compared.

**It is still chemotaxis at a = 384, and it is more chemotaxis than at 64.** W4b-801, 7 robots
× 64 seeds from 7000, six conditions, 2,688 bouts; every bearing in the travel frame:

| condition | Δ items (CI over robots) | Δ score | work J | bearing to ascent | turn toward | centroid m | in-disc m | rail % |
|---|---|---|---|---|---|---|---|---|
| base | — | — | 19,390 | 1.534 | +0.124 | 2.83 | 5.40 | 0.0 |
| compass 64 | +1.018 [+0.600, +1.460] | +1.049 | 18,432 | 1.347 | +0.195 | 2.32 | 4.98 | 1.5 |
| **compass 384** | **+1.875 [+1.230, +2.449]** | **+1.834** | 20,808 | **1.265** | **+0.311** | **2.02** | 5.03 | 18.8 |
| phantom 64 | +0.257 [+0.100, +0.411] | +0.272 | 18,708 | 1.449 | +0.171 | 2.33 | 5.02 | 1.7 |
| **phantom 384** | **−0.217 [−0.397, −0.009]** | −0.258 | 20,826 | 1.512 | +0.056 | 1.95 | 4.54 | 18.8 |
| antimotif 384 | −1.094 [−1.205, −0.975] | −1.096 | 19,542 | 2.084 | +0.017 | 5.08 | 1.73 | 8.4 |

- Aim improves monotonically with a (1.534 → 1.347 → 1.265 rad to the smell ascent), the
  turn-toward rate more than doubles from 64 to 384, and the robot ends the season nearer the
  live-item centroid (2.83 → 2.32 → 2.02 m). Pure geometry, no heading convention in it.
- **The phantom collapses the entire gain at 384**: with the sensors fed a decoy layout the
  same install is worth −0.217 [−0.397, −0.009]. At 64 the phantom keeps +0.257 [+0.100,
  +0.411] of the +1.018 — a small non-food component that RBT-69 read as −0.071 [−0.317,
  +0.183] on seeds 9000+; the two are compatible within their CIs, and I report mine as it
  came. At 384 there is no such residual: everything the circuit earns, it earns from the
  food that is actually there.
- The antimotif at 384 aims away (2.084), leaves the disc (in-disc path 1.73 m, centroid
  5.08 m) and loses 1.094 items, 0/7. Same magnitude, opposite sign, opposite everything.

**The pinned fraction costs about four hundredths of an item.** The ecology's own fitness
quantity is `items − 0.03 × work/1000`. Actuator work rises 7% from base to a = 384 (19.4 →
20.8 kJ, worth 0.04 items at the work cost), so Δ score (+1.834) tracks Δ items (+1.875)
within that. Whatever 18.8% of ticks with both wheels pinned costs, it is not paid in the
currency the ecology charges. The phantom-384 row has the same rail fraction (18.8%) and the
same work, and loses items — so the pinning is a property of the gain, not of the food, and
it is the food-tracking that pays for it.
