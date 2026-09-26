# RBT-101 adversary round 1: the C4 design (flat terrain)

Branch `results/RBT-101-adversary`, cut from integration at `099f18b` (PR #89 merged). Scope: what is C4-specific.
RBT-92's shared instrument has its own adversary. Every number below re-derives from the scripts in this
directory. The bulk they read is the RBT-90 part 2 baselines, restored from `ckpt/rbt-90-SEED`: seed 2 at
434/600, the other nine at 600/600. Two probe pairs come from `ckpt/rbt-92-adv-*-9902` and
`ckpt/rbt-100-adv-*-901`. No income column is read anywhere.

| file | what it shows |
|---|---|
| `turnover_probe.py` → `turnover_probe.txt` | probe A: on baseline arms (no terrain change), how `new` moves with reproduction depth and births, and a non-posture placebo; pseudo-onsets every 20 seasons |
| `pair_null.py` → `pair_null.txt` | probe B: `new` in two same-seed pairs diverged by an unperceived event (T + 60 only); the size of natural new links against the installed reflex |
| `hit_anatomy.py` → `hit_anatomy.txt` | probe C: what a natural `new` hit is made of, sensors gained or links added |
| `start_seed_rerun.txt` | §3's PASS, re-run from scratch on this container |

Reproduce with `scripts/durable.sh restore runs/RBT-101/data/adv/forage-SEED rbt-90-SEED`, then
`PYTHONPATH=. python runs/RBT-101/adversary/turnover_probe.py digest <dir>` per run, then the three readouts.

**Round-trip first.** My digest (`turnover_probe.py digest`, which calls `wiring.digest` unchanged) reproduces
`control/801.txt`'s g1 on 240/240 rows. Probe C counts **100/600 holistic and 54/600 designed** natural hits over
139 → 300, exactly the hits behind `control.txt`'s no-install means (0.167 and 0.090). **The instrument reads
what it says it reads.**

---

## Credit, stated plainly

- **The positive control exists, on the right bodies, before any arm.** It uses the real evolved bodies of this
  economy, with RBT-66's rule applied as written, and a failure at n = 6 was declared before any data. That is
  better than most mechanistic readouts in this programme got.
- **The installed reflex is not an easy target in magnitude.** Among natural hits, the g1 gain over the best C0
  ancestor has a median of **2.53** (quartiles 1.20–4.30) on the holistic fauna and **0.90** (0.69–1.44) on the
  designed (`pair_null.txt`, tail). The installed reflex adds **1.0**, or 0.5. That is at or below what nature
  produces, so the control is conservative on magnitude.
- **The liveness probe is RBT-66's frozen-trajectory probe, not a free-running lesion.** `control.py
  probe_response` saves the activation and `_prev_input`, steps 8 ticks with the posture inputs live and again
  zeroed, restores, and holds every other sensor. The frozen probe is the one that reads steering correctly. It
  is reported and not gated, which is right, and "RE-WIRED means wiring acquired, not shown to be used" is said
  in the pre-registration's own words.
- **The depth figure is right.** Probe A measures the mean number of births from a T + 160 survivor back to its
  nearest C0 ancestor. It is **4.2–4.6** in the onset region, against the pre-registration's "about five".
- **Quotes are verbatim.** After whitespace normalisation, all three blockquotes (the §2 C4 perception paragraph
  with the claim line, the §3 C4 bullet and the §14 list) are exact substrings of
  `docs/held-out-challenges.md`.
- **C4 is reported apart from C1–C3.** `rewire.py` heads every fauna block "C4 is reported separately …", and
  `readout.sh` labels its output C4.
- **Choosing `new` over the mean statistics** is disclosed as exposure 1, with its whole history committed
  (`control_stats.txt`).

---

## Findings, hardest first

### F1. The re-wiring readout has no null for "diverged without a posture reason". MUST FIX before launch.

The ticket's hardest question was whether the readout would fire on drift alone, with no terrain change. The
design has two noise models, and **neither can produce that false positive.**
- The between-seed model has mean 0 by construction; §6.4 says so.
- The half-split splits one seed's P, the same survivors of the same run, into halves. It measures sampling
  noise inside one population. It cannot contain a difference between two trajectories that diverged at T.

So the "false positives ≤ 10%" criterion does not test the question.

**Probe A (`turnover_probe.txt`): `new` moves with turnover when nothing changes.** Baseline arms only, 162
pseudo-onset windows per fauna over 10 seeds, seed means removed:

| fauna | `new` against reproduction depth | `new` against births | depth against births |
|---|---|---|---|
| holistic | slope **+0.053 per event**, r +0.23 | +0.092 per 100 births, r +0.22 | r +0.59 |
| designed | +0.019 per event, r +0.08 | +0.016 per 100 births, r +0.06 | r +0.33 |

The windows overlap (T every 20, width 160), so the r values are not independent draws. Read the slope and its
sign, not a p-value.
- **The holistic slope is the concern.** A challenge that adds one reproduction event along a lineage moves
  holistic `new` by about +0.05 with nothing re-wired. One that removes one moves it by about −0.05 and prints
  FEWER NEW LINKS.
- C4 is a boon on the endpoint probe (`flat_probe.txt`: +0.57 and +0.25 items a bout solo). A boon changes
  energy, then deaths, then free slots, then births: a change in turnover, in a direction nobody has measured.

**How big the real test's noise is.**
- In the onset region (pseudo-T 340–420), baseline `new` has between-seed sd **0.052** on the holistic fauna
  and **0.032** on the designed (probe A, per-seed means). The control's window (T_cal = 140) gives **0.152**
  and **0.063**.
- The two same-seed diverged pairs (probe B, unperceived events, T + 60) give shift − plain in `new` of
  **0.000, −0.050, +0.050, −0.033**.
- The t-test on real shift − base differences will therefore be tighter than the control suggests. Arithmetic,
  not a measurement: at a per-seed sd of 0.05 and n = 10, the half-width is 2.262 × 0.05 / √10 = **0.036**.
  That is below the +0.053 that one extra reproduction event buys the holistic fauna.
- So a turnover shift of about one event could fire RE-WIRED on the holistic fauna with no new use of any
  sensor. I cannot measure the per-seed sd of shift − base at T + 160 without paired arms that run that far.
  That is the gap. It is not a result.

**Why the cull arm does not close it (F3).** k counts excess deaths clipped at 0, and a boon's turnover change
need not be excess deaths.

**The fix.** All three parts are cheap, and none needs a new arm:
1. **A placebo readout in the same tables.** `new_other` is the same statistic on non-posture sensors. The
   bodies carry `food`, `agent`, `oscillator` and `velocity`. Flat ground gives no posture-specific reason to
   wire the first three. `velocity` should be shown separately, since obstacles change it too; probe A's
   `g1_other` includes it and is only a sketch. `wiring.py` adds
   one column, g1_other; probe A's `g1_other` is the code. RE-WIRED should need the posture contrast to exceed
   the placebo's: shift − base on (new − new_other), with the interval above 0. Or, at the least, a placebo
   that also excludes 0 in the same direction prints **TURNOVER, not re-wiring**. The placebo does not track
   posture `new` tightly in the baseline (within-seed r = +0.12 holistic), so this is a noisy guard, not a
   perfect one. Its own positive control is free: the installed reflex does not touch it.
2. **Reproduction depth printed per arm**, the mean births from P(T + 160) back to C0, with shift − base. A
   RE-WIRED verdict beside a depth change of more than about half an event gets that caveat in the verdict
   line.
3. **cull20 as the divergence null for `rewire.py`.** It is a same-seed, same-T arm that diverges with no
   terrain change, and it exists on every seed with no cost to C4. Add shift − cull20 as a third interval, or
   at least print cull20 − base on `new` as the measured drift-plus-turnover null. This needs `wiring.txt` on
   RBT-92's cull20 arms, which `readout.sh` already links but nobody computes. It must be computed while their
   genomes exist: a post-processing line in RBT-92's run sequence, before those arms run. **This is the
   launch-blocking part**, because the bulk goes with the container.

### F2. On the holistic fauna, half of what `new` counts is a new body part, not a new use of a sensor. MUST FIX (a definition, cheap).

Probe C (`hit_anatomy.txt`, 139 → 300, all ten seeds):
- holistic: **52 of the 100** natural hits carry more posture sensors than every C0 ancestor (limbs or joints
  gained);
- designed: **0 of 54**.

§3 of the protocol, quoted by the pre-registration, says C4 "re-adapts" could mean "a new use of an existing
sensor". The control installs only on existing sensors, so it validates that case, but the scored statistic
also fires on morphological growth. On flat ground a body change is a live response. It is interesting, but it
is not what the claim line's "re-wired" names, and it is what C1–C3 call sorting of standing morphology plus
mutation.

**Fix.** `wiring.txt` already carries `ns`. Score `new` only over survivors whose `ns` does not exceed their C0
ancestors' maximum (**new_existing**), and print new_grown (ns larger) beside it, unscored. Re-run `control.py
analyse`, since the baseline noise falls and the resolution should improve. Say in §6.6 which one the verdict
is about.

### F3. k = 0/0 does not bite the income readout, but it does bite the re-wiring rule. MUST FIX (a wording and rule change).

- **Income:** RBT-92's amendment 2 item 6 (on integration via #87) handles 0/0 correctly. There is no event,
  so the null is the baseline, R-null = R-shift, and the seed says so. For C4's income readout that is closed.
- **Re-wiring:** on a 0/0 seed, `rewire.py` sets cull to the baseline, so shift − cull is identical to
  shift − base. **The "two intervals" rule becomes one interval on that seed**, and on the seeds with a cull it
  stays two. The designer puts k = 0/0 on ≥ 6/10 seeds at 0.55. So the rule's second guard, "against the same
  turnover", is absent on most seeds, in exactly the challenge where turnover moves the wrong way for an
  excess-deaths null (F1). Across seeds, the second contrast is also a mixture of two different things.
- **Fix:**
  - Say plainly in §6.5 that on 0/0 seeds the rule is one interval.
  - Make F1's third part, shift − cull20, the second guard on every seed. It is the same arm on every seed,
    so it is not a mixture.
  - Keep shift − cull printed.

### F4. The positive control's PASS is a sweep detector on the holistic fauna, at the wrong window. REPORT CAVEAT, plus one line.

- PASS is defined at f = 1.0, with every installable survivor carrying the new link. That is a sweep to
  fixation within about four reproduction events. At n = 7–9 it is also the only f the holistic readout sees
  (0.5 at n = 10). The pre-registration says so (§6.6), and the 0.85 on NO CHANGE SEEN holistic is close to a
  statement about the instrument, as the designer concedes.
- **The caveat:** the verdict sentence must carry the resolved f ("NO CHANGE SEEN, blind below f ≈ 0.5 of
  survivors"). A bare "NO CHANGE SEEN" must never be read as "did not re-wire". `rewire.py` prints the smallest
  f already, so this is a reporting rule.
- **One line to add:** the control runs at T_cal = 140, and the arms read at T ≈ 340–420. There, baseline
  `new` is lower (holistic 0.100 against 0.167) and far less noisy between seeds (sd 0.052 against 0.152). So
  the control understates the real test's power, which is fine for detection. It also means the real test sees
  small systematic biases the control never exercised (F1). Re-run `control.py extract` at T_cal = the
  median onset once RBT-92's `onset.txt` exists (it does not yet). The checkpoints hold all 600 seasons.

### F5. The start-seed check after a terrain shift: PASS confirmed. No action.

**Code:** `rabbitstew/ecology.py:465` draws from the TERRAIN stream every season, whatever the terrain. The
terrain seed is used only when `world.terrain == "random"` (line 467), and `draw_start_seeds` draws from the
same stream next (468). So a flat season consumes exactly what a random season consumes. That is RBT-95's
amendment, as stated.

**Re-run:** from scratch on this container, `start_seed_runs.sh` at 801 and 9901, then `start_seed_check.py`,
into `start_seed_rerun.txt`. **PASS on both seeds, and the file matches the committed `start_seed_check.txt`**. The pre-onset lineage digests are the same (`6018e0a9f5ec7965` at 801, `7c1af2377d4ef9d4` at 9901). Start seeds are equal in 20/20 seasons, 10/10 after the onset, and in 40/40 cohort rows. The run is deterministic across containers.

**Nothing else diverges before T.** lineage, cohorts and history are byte-identical before 10, and the configs
differ only in `ecology.shift` and `ecology.shift_at`. After T, seat assignments differ from 11, since they come
from each fauna's own stream once a death differs. §3's "share every start position" is right about positions,
but not about who stands in them. That is the challenge acting, and the pre-registration says so.

### F6. Protocol fidelity. PASS, one nit.

- Quotes are verbatim and C4 is reported separately (credit, above).
- **Nit:** §13 of the protocol names `scripts/forage_probe.py` for the endpoint prior. The designer wrote
  `flat_probe.py`, which runs "as scripts/forage_probe.py runs it" (its docstring). It is fine as a prior, since
  it enters no verdict. The report should say it is a re-implementation, not the named script.

---

## Verdicts

| # | finding | verdict |
|---|---|---|
| F1 | no divergence or turnover null for the re-wiring readout; `new` moves about +0.05 per reproduction event on the holistic fauna with no terrain change | **must fix before launch.** The cheap part (wiring on RBT-92's cull20 arms) is time-critical |
| F2 | 52/100 holistic hits are new posture sensors, not new uses of existing ones | **must fix before launch** (a definition; re-run the control) |
| F3 | k = 0/0 collapses the two-interval rule to one on most predicted seeds | **must fix before launch** (use cull20 as the second guard; say so) |
| F4 | the holistic control PASS is a sweep detector, and it was calibrated at T = 140, not at the onset | report caveat, plus re-running the control at the median onset |
| F5 | start seeds after a terrain shift | PASS, confirmed by code and re-run |
| F6 | quotes, separation | PASS; the flat_probe nit is a report caveat |

The income side of C4 is RBT-92's instrument, and nothing C4-specific in it concerns me beyond what RBT-92's
adversary owns. The re-wiring readout is the novel part. It is well built and honestly limited, but as written
it cannot tell re-wiring from a change in how fast lineages turn over, or from growing a limb.
