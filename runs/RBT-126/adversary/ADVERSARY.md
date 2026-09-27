# RBT-126 adversary: PR #415 at `97f0e06`

**Verdict: MERGE AFTER FIXES.**

- **The numbers are right.** Every corpus figure I re-derived matches. The restore holds, P-801 reproduces, and the
  tests pass.
- **What the band means is wrong as stated.** "Saturated" is calibrated on **spread**: a better mutant invading. It
  says nothing about **retention**: a trait held against erosion.
  - Run as a retention design, the PR's own replica reads "saturated" in every cell (2.7–10.7), while selection holds
    the trait up to +0.44 above its floor.
  - Four of the six selection-dependent headlines are retention readouts, or rest on one: RBT-80, RBT-106 H and P1,
    and RBT-112.
  - So "every selection-dependent headline was read in the saturated band" must not be stated as qualifying them,
    and in particular not their positives.
  - It does bound the **nulls** (RBT-106 P1, RBT-112 Z, RBT-107 H1) and any **spread** reading.
- **The recommended `--energy-leak 0.3` selects on variance.**
  - In the PR's own replica, a mutant with the **same mean** income but lumpier seasons fixes in 0.83–1.00 of runs.
  - A mutant with **10% less mean** income, lumpier, fixes in 0.98 of runs at g0 3.
  - That is the opposite artefact: a strong sieve that reads noise as merit. It cannot be recommended as it stands.
- **The drift-gate correction is right.** The RBT-71 counts reproduce exactly. The holistic figure is a lower bound,
  though, not a measurement.

Probes, outputs and logs are all in `runs/RBT-126/adversary/`. Every probe imports the PR's own replica and readout
unchanged, except `adv_rederive.py`, which is written from `ecology.py` alone.

## What each headline can still claim

This is for the errata and progress report 2. "Null shares the regime" asks whether the comparator ran in the same
economy as the scored arm, so that a lottery effect would be common to both and cancel.

| headline | design | comparator | null shares the regime? | does the saturated band threaten it? | what survives (one sentence) |
|---|---|---|---|---|---|
| **RBT-105** R1 (5 flips in 14, p 0.009), R2 (T +2.35, p 0.011) | fate by breeding history; no fitness quantity enters the rule (PREREGISTRATION:146-176) | R1: a chosen q = 0.1. R2: a label permutation among replicates that differ only in `--breed-stream` (prereg:25-57) | **yes**: every replicate has the same economy, and only the holistic breeding RNG differs | **No.** It is a history result, not a selection one, and a lottery-dominated economy is the setting it describes. REGIME.md's "yes" in the selection column misfiles it. | "In the committed economy, with the holistic fauna's eligible members earning 3.4–3.7× the living cost, the oscillator's fate turned on breeding history in 5 of 14 decided replicates, and the founders shifted its late birth rate." |
| **RBT-106 H** HELD HU 0, HP 9 | retention: compass planted in half the founders, erosion u ≈ 0.29 per generation | an operator-only persistence table (no selection, "the world does not enter", PREREG:296-302); false-positive rate 1.0% measured on real part-2 genealogies; HP against HU paired by seed | the floor is regime-free by construction; HP and HU share the rule and the cost but **not the income**: +1.77 income, more births on 10 of 10 (H-READOUT:176-179) | **No, for the positive.** Saturation weakens selection and cannot manufacture a HELD, and the false-positive rate was measured on the committed economy. The band also does not predict the sign of HP − HU; see §1c. | "The planted compass was held above operator-alone persistence on 9 of 10 HP seeds and 0 of 10 HU seeds, in an economy whose queue is saturated in both worlds. So what held it was not ranking among solvent members, and is most plausibly the viability sieve purging carriers' losses. H8's income, births and depth confound stands." |
| **RBT-106 P1** P-NULL; RBT-104 S1 its comparator | retention of the sub-paying w = 1 compass; verdict on function (0 of 7 COMPASS lines) | S1: the same founders, uniform world | same rule and cost; P1 − S1 income +0.38 and more births on 10 of 10 (P1-READOUT:107-108) | **Yes, as a caveat on the null.** A saturated queue cannot spread a small edge (replica ×1.25 at g0 1.3: share 0.10, fixation 0.00), and a w = 1 compass's loss may not reach the sieve. | "Under the committed rule, in the patchy world, the w = 1 compass was not held on any usable seed. That says nothing about whether the prize suffices under a rule that selects above viability (the null already misses 'prize suffices' with probability 0.22)." |
| **RBT-107 H-REP-DES** supported (fragile); **H1-DES and H1-PAIR** not supported | common garden: G_shift − G_base, and net of cull20; Yuen IUT (prereg:190-209, 711-716, 920-931) | base and cull20 arms, paired by fresh seed on founders, worlds and streams (prereg:758-766) | **only partly.** Base and cull20 share the regime (designed 2.7–2.9). The scored **shift** arm does not: its designed fauna reads 5.7–5.8, twice as deep, and flat ground refunds +0.78 (hrep/REPORT:123) | For **H-REP**, no: a garden difference against a matched null is sorting plus drift, and the IUT already nets out the cull20 turnover shock. For the **H1 nulls**, yes: the shift arm is the most saturated arm in the corpus. | "A fragile, heritable garden difference after the shift, at T+110, survives. The absence of one at T+800 is a statement about the committed (saturated) rule, and should not be read as 'no adaptation under selection'." |
| **RBT-112** Z FALSIFIED: HELD HU 0, HZ 1; s ∈ [0.00, 0.08] | retention, planted as H; s by BetaBinomial likelihood with u = 0.089 (READOUT:87-91) | HZ against HU paired by seed, each read against its own operator table | **yes**: same world and rule; births +6.3 [−44.6, +57.2] and depth +0.33 do not differ (READOUT:21, 61-64). Income is +0.16. | **Not for the comparison**, which is regime-matched. Yes for the **generalisation**: the s bound is a property of this economy. | "Removing the global bias did not make the compass held in the uniform world under the committed rule; its s there is ≤ 0.08. Whether a selecting rule would hold it is untested." |
| **RBT-80** seeded − drift NO VERDICT; seeded carriage 0.96 / 0.72 / 0.92 against floors of about 0.52 | retention | an analytic floor at the arm's own depth; and a drift arm with a **different** economy (cost 0, threshold 0, and the gate of item 4) | **no**, for the drift arm | Not measured; there is no lineage. The replica (§1a) says the band does not threaten retention of a trait whose loss nears the cost, and seed A's non-carriers earn 0.08, below it. | ADVERSARY 1e's corrected statement stands: "the seeded arms held carriage well above their own no-selection floors; the NO VERDICT reflects the drift comparator's depth, and, per DRIFT-GATE.md, that comparator was not selection-free." |

**The one-line version for the errata:**
- The committed rule cannot be relied on to **spread** a better variant among solvent members (the band).
- It **can** hold a trait whose loss pushes its bearer toward the living cost (the sieve).
- The positives in the corpus (RBT-80's seeded arms, RBT-106 H, RBT-107 H-REP) are the second kind, or are sorting
  measured against a matched null. They stand.
- The nulls (P1, Z, H1) are regime-bound, and should say "under the committed rule".

## 1. Do the bands mean what the readout says?

### 1a. "Saturated" does not mean selection could not act: the PR's replica, run as a retention design

`adv_band_retention.py` runs `breeding_rules.run` (committed shuffle, unchanged) in RBT-80's retention design:
- 60 carriers at gross gc;
- erosion u 0.06 per birth to a non-carrier at gross f × gc;
- 300 seasons, 200 replicates a cell.

The PR's `scripts/regime.py` reads 8 replicates a cell over seasons 150–299 (`adv_band_retention.txt`).

| carriers gc (≈ corpus ratio) | non-carriers f × gc | carriage − floor (floor 0.55–0.57) | regime.py window-local → band | viability | starvation share of deaths | Q5÷Q4 |
|---|---|---|---|---|---|---|
| 1.05 (RBT-80) | 0.11 | **+0.439** | 2.90 → saturated | +2.18 | 0.10 | 1.06 |
| 1.05 | 0.47 | **+0.378** | 2.81 → saturated | +2.18 | 0.09 | 1.00 |
| 1.05 | 0.63 | **+0.266** | 2.72 → saturated | +2.00 | 0.09 | 0.78 |
| 1.10 (HU, ~3) | 0.11 / 0.50 / 0.88 | **+0.421 / +0.348 / +0.078** | 3.12 / 2.98 / 2.90 → saturated | +2.3 to +2.5 | 0.05–0.10 | 0.93–1.01 |
| 1.30 (HZ, P1, ~3.8) | 0.13 / 0.59 / 1.04 | **+0.441 / +0.323 / +0.070** | 3.86 / 3.59 / 3.55 → saturated | +2.9 to +3.2 | 0.03–0.09 | 0.86–1.14 |
| 3.00 (HP, ~10.7) | 0.30 / 1.35 / 2.40 | **+0.416 / +0.053 / −0.013** | 10.66 / 8.65 / 9.68 → saturated | +8 to +10 | 0.00–0.06 | 0.82–1.22 |

**Every cell reads saturated, and none of the sieve columns flags the selection either.** Viability is +2 to +10,
starvation is at most 10% of deaths, and Q5÷Q4 is about 1.
- The reason: the regime is a property of the **majority**, the solvent carriers, while retention works on the
  eroded **minority**.
- In the saturated band, a loss that drops its bearer toward the living cost is purged hard (+0.42 to +0.44 at every
  income level).
- A loss that leaves the bearer solvent is barely purged (+0.05 to +0.08; nothing at HP-like income).
- And spread of a gain is nil (invasion ×1.25: fixation 0.00; `invasion.txt`).

So the band is a statement about **spread above viability**. It is not about whether selection acts.
- REGIME.md's headline paragraph and its column "turns on reproduction above viability?" read as if the band
  qualified every row marked "yes".
- It qualifies only spread claims and nulls. It is **silent on retention positives**.
- This matches paper 10's own title ("held, not spread"). The band explains why the corpus sees holding without
  spreading.

The replica's u is 0.06, RBT-80's figure. Paper 10's operator erodes at about 0.29 per generation, which lowers every
carriage, but not which band is read.

### 1b. Transfer from the bodiless replica to bodies

- **The calibration maps a homogeneous Poisson population.** There, g0 0.8 corresponds to window-local 1.92
  (`calibration.txt`). Embodied faunas are bimodal: a solvent queue over a starving tail (P-801 designed:
  window-local 2.7–3.0, viability −1.1 to −1.6).
- **REGIME.md says this** ("The replica is homogeneous…"). But the headline paragraph then uses the window-local
  figure alone.
- **What transfers is the spread statement.** For the solvent queue, the lottery among eligible members is the same
  mechanism in both. The replica's ×1.25 and ×2 fixations at each headline's ratio are 0.00–0.01 (`invasion.txt`):
  - HU and RBT-107 base, at about g0 1.0–1.1: shares 0.18 and 0.24;
  - HZ, P1 and RBT-105 holistic, at about 1.2–1.3: shares 0.10 and 0.18;
  - RBT-107 shift, at about 2: shares 0.11 and 0.13;
  - HP, at about 3: shares 0.12 and 0.12.
- **What does not transfer is anything about retention or the sieve** (§1a).

### 1c. "HP sits about 3× deeper in the band"

This is true of the window-local figure (10.2–10.8 against 2.9–3.3), and I re-derived it. But on the PR's own sieve
columns, HP's designed fauna has **more** turnover by starvation than HU's:
- deaths by age are 0.27 / 0.33 in HP against 0.38 / 0.53 in HU (REGIME.md rows; re-derived in `adv_rederive.txt`);
- HP also has more births on 10 of 10 seeds.

So the purging channel that holds a trait is, if anything, more active in HP. Written without the sieve columns, "3×
deeper" invites the reading that HP selects less, which the H result contradicts. ADVERSARY 1f's "if anything less"
was about the upper tail only.

### 1d. The per-life and window-local measures disagree on the band

- **M2 asked for** "net income of members that reach breeding age". That is the PR's **per-life** column. The band
  is read from the **window-local** one.
- **They agree in the replica** (1.81 against 1.92 at g0 0.8), but **not in the corpus**:
  - P-801 designed: per life 1.28–1.66, which is **transition**, against 2.66–2.99 window-local;
  - RBT-99 and RBT-100 shift designed, "before": 1.45 and 1.50;
  - the lower ends of HU's [300, 600) (1.94) and RBT-107 base H-REP (1.69).
- **Window-local weights by eligible member-seasons,** so long-lived members count up to 57×. That is a survivor
  weighting of the kind R5 warns about.
- **The headline medians stay ≥ 1.9 either way,** so the claim survives, but the choice needs a sentence.

### 1e. Are the windows registered?

- **No RBT-126 registration exists.** The ticket (Chaotic RBT-126) names no windows or bands.
- **The windows are each ticket's own read windows,** taken from its report or prereg. RBT-105's [60, 160) A/A is the
  readout adversary's, not registered (RBT-105 READOUT-ADVERSARY:261). They are not chosen after the fact in any way
  that moves a band.
- **The cutoffs 1.9 and 1.2 were set post hoc from the replica.** They are **insensitive** here: the nearest headline
  median is 2.72 (RBT-107 base), and every scored-fauna median is ≥ 2.6.
- **The band assignment is robust to the cutoffs; its interpretation is not (§1a).**

## 2. The numbers

- **Corpus rows re-derived** (`adv_rederive.py` → `adv_rederive.txt`).
  - The code is independent, written from `ecology.py` (pre-birth energy = row energy + birth cost × children paid
    that season, payer = `parents[0]`).
  - All ten cells match REGIME.md to two decimals, on the median and the range, for window-local saturation,
    eligible breeders and deaths by age:
    - RBT-106 HP and HU, both windows, and P1 [300, 600);
    - RBT-107 fresh-base H-REP and H1, and fresh-shift H1;
    - RBT-112 HZ, both windows.
  - Example: HP [0, 300) is 10.80 [8.17, 13.40] with 52.31 eligible and deaths by age 0.27. HZ [300, 600) is 3.43
    [2.52, 4.94].
- **The restore.**
  - I fetched all 203 `ckpt/*` branches myself with `fetch_ck.sh`.
  - `verify_restore.py` then gives output byte-identical to the committed `verify_restore.txt`: **201 of 201 with 0
    mismatched**, and 2 adversary probes with no committed result.
- **The fields the band reads.**
  - The restore check compares last rows only (generation, age, evals, fitness, parents). **Energy and last_score,
    which the band reads, are not in `lineage-last.txt`.**
  - `adv_energy_books.py` closes this. On five runs (HP-1, HU-804, fresh-shift-11, HZ-7, RBT-99 shift-805), every
    member-season step obeys energy_t = energy_{t−1} + last_score − 0.25 − 1 × children paid: 415,414 steps, worst
    error 0.0010, which is the log's rounding.
  - Births per season match `seasons.txt` on all 7,200 season-fauna rows.
- **P-801.**
  - `regime.py runs/RBT-19/P-801 --windows 50-500` gives holistic: 1,001 complete lives, children by quintile 0.00 /
    0.00 / 0.05 / 2.29 / 2.62, with quintile bounds, incomes, lifespans, age-deaths and eligible seasons identical to
    `adv_p801_births.txt`.
  - Designed: 1,955 lives, 0.00 / 0.00 / 0.00 / 0.26 / 5.11. The eligible seasons in Q4 read 4.0 against 3.9.
- **Tests.**
  - The venv is clean, `pip install -e '.[dev]'`, and scipy is absent (import fails).
  - `tests/test_regime.py`: **6 passed**. Full suite: **404 passed** in 259 s.

## 3. `--energy-leak 0.3`

- **×1.25 fixing at 0.97–1.00 reproduces.** `adv_leak_artefact.txt` gives 0.99–1.00 at g0 1.0, 1.3 and 3.0, with
  200 replicates.
- **It is plausible at the stated depth,** because the leak caps hoards (so parent age does not climb) while the
  order is a truncation. About 1–2 slots a season go to the top of about 53 eligible, ranked by a roughly 3-season
  moving sum of income. That is very strong selection bought without a gerontocracy.
- **That strength is the problem.**

**It reads variance as selection** (`adv_leak_artefact.py`: 6 mutants among 60, 400 seasons, 200 replicates; neutral
share 0.10):

| mutant | g0 | shuffle: share / fixation | **leakx:0.3: share / fixation** |
|---|---|---|---|
| same mean, lumpy: Poisson(2g) in half the seasons, else 0 | 1.0 / 1.3 / 3.0 | 0.02 / 0.00 in every cell | **0.96 / 0.83, 0.99 / 0.97, 1.00 / 1.00** |
| 0.9× the mean, lumpy (a mean **loss**) | 1.0 / 1.3 / 3.0 | 0.01 / 0.00 in every cell | **0.39 / 0.03, 0.76 / 0.29, 0.99 / 0.98** |
| same mean, feast or famine (2g or 0) | 3.0 | 0.03 / 0.00 | **1.00 / 1.00** |

- **Shuffle purges variance, and leakx:0.3 rewards it,** strongly, and above g0 1.3 more than it rewards a 10% mean
  advantage.
- **In bodies, season-to-season variance is not a nuisance parameter:**
  - the patchy world's income is lumpy by design;
  - holistic σ_P is about 1.2 against about 0.7 designed (R5);
  - a flailer's "found a patch" season is exactly the lucky streak this rule promotes.
- So under this flag a trait that raises variance, such as a wandering gait in patches, would read as selected. So
  would a fauna whose members are noisier. That is the "strong sieve that reads everything as selection" the brief
  asked about.
- The PR's own caveat ("selection on the rule's own noise is not measured … a neutral mutant stays at 0.10") names
  the gap. The neutral-marker test cannot see it; a variance-only mutant does.

**R6 parity across faunas.**
- **Merged cohorts.** `Ecology.step` pools both faunas' breeders into one list after `--merge-after` (`ecology.py:524`,
  the cohort loop). The designed `breeders.sort(key=-energy)` would then give every freed slot to the richer fauna.
  The leak caps each hoard near 3 + n/λ, so a fauna at net 2.6 (HP designed) outranks one at 0.9. The design
  must sort within fauna, or refuse with `merge_after`.
- **Depth.** The depth cost depends on the income level: 0.97× at g0 1.3, 0.90× at g0 3. HP designed (about g0 3)
  and holistic (about g0 1.2–1.3) would therefore be depth-mismatched by about 7% under the same flag. Report it per
  fauna.
- **Noise.** Its selection intensity depends on each fauna's income noise (above), which differs by about 1.7×.

## 4. The drift gate

- **The correction is right.**
  - Children start at `eco.birth_cost` (`ecology.py:539`), which is 0 under `--neutral` (`cli.py:354-355`).
  - The gate is `energy >= birth_threshold` (`:524`), so a child is barred whenever its cumulative gain is below 0,
    not −3.
  - The same two lines are in RBT-71's code tree (`f3aa69d`, `ecology.py:311, 325`).
  - ADVERSARY's "`:527`" and "−3 for everyone" describe founders only.
- **The RBT-71 counts reproduce exactly** (inline check against `lineage-last.txt`):
  - founders barred: designed 18 / 16 / 14 and holistic 1 / 3 / 1;
  - children barred: designed 115 / 103 / 94 and holistic 49 / 50 / 51.
- **The holistic figure is a lower bound, not a measurement.**
  - 483 of 599, 455 of 600 and 491 of 597 holistic children have `fitness` **0.0000** at the log's 4 dp.
  - A child whose true lifetime gain is −0.00004 a season, for example a motionless body's work, is barred for life
    and prints as 0.
  - So the holistic barred share is anywhere from 8–9% to about 90%, undetermined from `lineage-last.txt`. The
    designed figure (16–19%) has no such cases (0 exact zeros).
- **The RBT-99 counterfactual bracket is [0.000, 0.24–0.34].**
  - "RBT-71's 16–19% sit inside this bracket" is true of any figure between 0 and 0.34, so it adds nothing.
  - Keep the bracket, and drop the sentence.
- **The `--breed-gate none` design is sound as specified:**
  - it is byte-identical when unset;
  - it is refused outside `--neutral`;
  - `alive` holds only evaluated members at `:524`.

## MUST

1. **REGIME.md: say what the band is about.**
   - Replace "Read descriptively, every selection-dependent headline … was read … in the saturated band" with a
     statement that the band measures whether the queue can **spread** a gain above viability. It is silent on
     **retention** of a trait whose loss nears the cost.
   - Cite §1a's table or re-run it.
   - Split the column "turns on reproduction above viability?" into spread, retention, history and yield. On that
     split:
     - RBT-105 is **history**;
     - RBT-106 H, RBT-112 and RBT-80 are **retention**;
     - RBT-107 is garden **sorting** against a matched null;
     - only the nulls and any "spread" wording are qualified by the band.
2. **REGIME.md, the RBT-106 row: "HP sits about 3× deeper in the band".** Either drop it, or pair it with deaths by
   age (0.27 / 0.33 in HP against 0.38 / 0.53 in HU) and births. On the sieve, HP turns over more.
3. **BREEDING-RULES.md: withdraw the recommendation of `--energy-leak 0.3` as it stands.**
   - It fixes a same-mean, higher-variance mutant in 0.83–1.00 of runs, and a 0.9× lumpy mutant in 0.98 at g0 3
     (§3).
   - Any rule recommended must report, as planted negatives (R10), a variance-only mutant and a mean-loss,
     variance-gain mutant beside the neutral marker.
   - The flag's design must also sort within fauna, or refuse `--merge-after`.
4. **The errata and progress report must not say the band "qualifies" the published positives.** Use the table above.
   This is for the coordinator, but it is the reason the PR must not merge with the headline paragraph as written.

## SHOULD

1. Show both bands in the headline table: per-life (M2's measure) and window-local. Say why the band is read from
   window-local (§1d); P-801 designed is transition per life.
2. RBT-107 row: note that the scored shift arm (designed 5.7–5.8) is not in its nulls' regime (2.7–2.9).
3. In REGIME.md, state that the windows are the tickets' own, not registered by RBT-126, and that the cutoffs are post
   hoc but insensitive (nearest scored median 2.72).
4. Commit `adv_energy_books.py` or its equivalent into the verification. The restore check does not cover energy or
   last_score.
5. DRIFT-GATE.md:
   - state the holistic 8–9% as a lower bound (the 4-dp zeros);
   - drop "sit inside this bracket".
6. BREEDING-RULES.md: report the depth cost per fauna income level for any flag. It differs by 7% between HP-like and
   holistic incomes.

## Files

- `adv_band_retention.py` → `.txt`: the retention replica read by `regime.py` (§1a).
- `adv_leak_artefact.py` → `.txt`: the variance mutants under shuffle and leakx:0.3 (§3).
- `adv_rederive.py` → `.txt`: independent corpus rows (§2).
- `adv_energy_books.py` → `.txt`: the energy and births books on five restored runs (§2).
- `logs.txt`: the restore diff, the test runs, P-801, and the RBT-71 recount.

---
_Generated by [Claude Code](https://claude.ai/code)_
