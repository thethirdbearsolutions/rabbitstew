# RBT-126: the regime of every committed ecology result

This is RBT-121's fix list items 4 and 8, with SYNTHESIS R5 as amended by the synthesis check's M2. It is
**descriptive**: it gives each result's regime, named with its window, and rules on nothing.

- **The instrument:** `scripts/regime.py`, read-only on `rabbitstew/`, with tests in `tests/test_regime.py`.
- **The breeding-rule options** are in `BREEDING-RULES.md`. It recommends no flag (after PR #417, M3).
- **This version carries PR #417's fixes** (the ruling of 22:40): M1, M2, M4 and SHOULD 1–5.
- **For what each published headline can still claim, use PR #417's per-headline table.** This document gives each
  result's regime and says which kind of claim the band bears on. It does not qualify any published positive (M4).
- **The drift-arm gate** is in `DRIFT-GATE.md`.

## What was read

- **201 restored ecology runs** (9 tickets), plus RBT-19's committed lineage. For each one, per fauna and per
  season window:
  - saturation;
  - viability;
  - offspring by lifetime-income quintile;
  - the share of deaths by age, by starvation and by cull;
  - the eligible breeders a season;
  - median energy;
  - depth: distinct parents, age at breeding, and generations per season.
- **Sources:**
  - **RBT-19 P-801:** the committed `runs/RBT-19/P-801/lineage.jsonl`.
  - **RBT-90, 99, 100, 101, 105, 106, 107 and 112:** restored from each run's checkpoint branch (`origin
    ckpt/rbt-<n>-<arm>`: a `MANIFEST` and `run.tar.gz.part*`). Only `lineage.jsonl`, `seasons.txt`, `config.json`
    and `event.txt` were extracted.
  - **RBT-104's S1 and S8** are beyond the ticket's list. They were read too, because S1 is paper 10's uniform
    w = 1 comparator (`runs/RBT-106/S1-*`).
- **Verification** (`verify_restore.py` → `verify_restore.txt`):
  - Every restored lineage was checked against the run's **committed** `lineage-last.txt`. Each member's last row
    (generation, age, evals, fitness, parents, cull rows included) was rebuilt from the restored lineage and
    compared.
  - **201 of 201 runs match, with 0 mismatched rows.**
  - Each checkpoint's `config.json` is identical to the committed one, on all 201 runs.
  - Three checkpoints were taken before their run finished. Their windows stop at the checkpoint:
    - RBT-101 shift-804 at 548 of 600 seasons;
    - RBT-101 shift-805 at 599 of 600;
    - RBT-99 cull-806 at 505 of 600, which cuts its recovery window [T+60, T+160) = [425, 524] at 504.
  - **The fields the band reads** are energy and `last_score`, which `lineage-last.txt` does not carry. So
    `verify_energy.py` → `verify_energy.txt` checks, on every restored run, that every member-season step obeys
    energy_t = energy_{t−1} + last_score − living cost − birth cost × children paid (to the log's rounding), and
    that births per season match `seasons.txt`. PR #417's `adv_energy_books.py` makes the same check on five runs.
  - **Result: 17,746,535 member-season steps, 0 off by more than 0.002 (worst 0.0010, the log's rounding).
    309,600 season-fauna birth rows, 0 mismatched.** RBT-101 shift-804's partial checkpoint has no `seasons.txt`, so
    its births were not compared.
  - Two further checkpoints, `rbt-100-adv-{plain,shift}-901`, are 160-season adversary probes with no committed
    result. They appear in `regime/TABLES.md` only.
- **RBT-80 has no regime figure.** No lineage is committed, and there is no checkpoint branch for any of its nine
  arms. What its committed artefacts do show is in [RBT-80](#rbt-80-not-measured) below.
- **The readout reproduces the adversary's hand count.** On P-801's holistic lives born in seasons 50–500 it finds
  the same 1,001 complete lives. Children by quintile are 0.00 / 0.00 / 0.05 / 2.29 / 2.62, as in
  `runs/RBT-121/adversary/adv_p801_births.txt`.
- **Nothing was run** except the readout and the replica.

## Definitions (`scripts/regime.py`)

- **Income** is a member's gain a season: food minus work, the lineage's `last_score`. A life's income is its
  lifetime mean, the lineage's `fitness`.
- **Net** is income minus the living cost, which is 0.25 in every run read here. Ratios are ÷ the living cost.
- **Eligible** means energy ≥ the birth threshold (3) *before* that season's births. The lineage stores energy after
  births, so a parent's pre-birth energy is its row's energy + birth cost × its children that season.

**Saturation, window-local** (one of two bands; see [the bands](#the-bands-and-what-they-are-about)):
- the mean season income of the members eligible that season, over the window's seasons, minus the cost, ÷ the cost;
- it uses the window's own seasons only.

**Saturation, per life** (M2's wording: the members that reach breeding):
- the mean lifetime net ÷ cost of the complete lives *born* in the window that were ever eligible;
- it follows each life to its death, past the window's end. So in an event arm it mixes pre- and post-event income:
  RBT-99's shift arms read 1.45 for the designed fauna "before" T this way, against 2.60 window-local, which is the
  base's own figure.

**The other columns:**
- **Viability:** the mean lifetime net ÷ cost of *every* complete life born in the window.
- **Offspring by quintile:** complete lives born in the window, split by lifetime income into quintiles. Children are
  the rows whose `parents[0]` names the member, i.e. the breeder that paid. `Q5÷Q4` is the ratio of mean children in
  the top two quintiles: the gradient *above* viability.
- **Deaths:** deaths in the window, by age (last row at age ≥ 59), by starvation, or by cull.
- **Eligible breeders:** the mean a season. **Median energy:** the mean over seasons of the living's median energy,
  after births.
- **Generations per season:** the change in the living's mean pedigree depth across the window, ÷ its length.
- **Living income:** the survivor-weighted mean lifetime score of the living, which is what `seasons.txt` reports.
  It is printed beside the per-birth figures so the two cannot be confused (R5).

## The bands, and what they are about

**The band measures one thing: whether the breeding queue can *spread* a gain above viability.** It is silent on
*retention*, i.e. whether selection holds a trait whose loss pushes its bearer toward the living cost. This
paragraph replaces the first version's reading (PR #417, M1).

- **The calibration is an invasion design.** A better mutant is planted among solvent residents, and the question is
  whether it spreads (`calibration.txt`, `invasion.txt`, below).
- **Run as a retention design, the same replica reads "saturated" in every cell, while selection holds the trait.**
  The adversary's `runs/RBT-126/adversary/adv_band_retention.txt` (PR #417 §1a) runs RBT-80's retention design at
  carrier incomes that match the corpus's ratios. Carriage above the no-selection floor:
  - **+0.42 to +0.44** when the eroded non-carriers earn near the cost, at every income level;
  - +0.05 to +0.08 when the loss leaves them solvent, and nothing at HP-like income.
- **Why:** the regime is a property of the solvent majority, and retention works on the eroded minority.
- **None of this table's sieve columns flags that purging either.** Viability, starvation share and Q5÷Q4 are read
  over all births, where the eroded minority is diluted.
- **So a saturated band bounds claims that something spread, or failed to spread, among solvent members.** It says
  nothing against a retention positive.

### Calibration

`calibration.txt` runs `regime.py` on replica lineages (`breeding_rules.py lineage`, committed shuffle rule, window
150–449, 4 seeds a cell). `invasion.txt` gives the fixation columns.

| replica g0 | saturation, window-local | saturation, per life | ×1.25 fixes | ×2 fixes | band |
|---|---|---|---|---|---|
| 0.4 | 0.90 | 0.30 | 0.85 | 1.00 | selecting |
| 0.5 | 0.91 | 0.68 | 0.18 | 0.87 | selecting |
| 0.6 | 1.20 | 1.05 | 0.01 | 0.27 | transition |
| 0.7 | 1.54 | 1.43 | 0.00 | 0.04 | transition |
| 0.8 | 1.92 | 1.81 | 0.00 | 0.01 | saturated |
| 1.0 | 2.70 | 2.60 | 0.00 | 0.01 | saturated |
| 1.3 | 3.85 | 3.78 | 0.00 | 0.00 | saturated |
| 3.0 | 10.67 | 10.61 | 0.00 | 0.01 | saturated |

**Cutoffs.**
- **Window-local:** saturated ≥ 1.9, transition 1.2 to 1.9, selecting below 1.2.
- **Per life:** saturated ≥ 1.8, transition 1.0 to 1.8, selecting below 1.0.
- **few:** fewer than 10 eligible breeders a season on average. The ratio is then read off a handful of lucky members
  (the replica reads 2.60 window-local at g0 0.3, on its way to extinction), so no band is given.
- **none:** nobody eligible in the window: the fauna is extinct, or never solvent.

**The cutoffs were set after the fact, from the replica. They are insensitive here.** The nearest scored-fauna
headline median is 2.72 window-local (RBT-107 base, H-REP window), and every scored-fauna median is ≥ 2.6. The
band's *assignment* is robust to the cutoffs; its *interpretation* is the paragraph above.

**Two measures, which disagree in the corpus.**
- **M2's measure is the per-life one:** the members that reach breeding. The first version read the band from the
  window-local one alone.
- **In the replica they agree** (1.81 against 1.92 at g0 0.8).
- **In bimodal embodied faunas the window-local measure weights long-lived members up to 57×,** a survivor weighting
  (PR #417 §1d). So both bands are shown below.
- **Where they differ:**
  - P-801's designed fauna is **transition per life** (1.28–1.66), against saturated window-local (2.66–2.99);
  - RBT-99 and RBT-100's shift arms, designed "before", read 1.45 and 1.50 per life. That is partly the per-life
    measure carrying post-shift income back into the window.
- **Every scored-fauna headline median is saturated on both.**

**The windows are the tickets' own.** Each headline window is taken from that ticket's report or pre-registration.
RBT-126 registers no windows and no bands. RBT-105's A/A window [60, 160) is its readout adversary's, not registered.

**The replica is homogeneous; a real population is not.** A saturated figure says the members competing for slots earn
well above the cost. It does not say that no member starves. **Viability, the share of deaths by starvation, and
Q5÷Q4 are the columns for the sieve below them.** P-801's designed fauna is the case in point:
- window-local saturation is 2.7–3.0;
- viability is −1.1 to −1.6;
- 78–92% of its deaths are by starvation;
- Q5 has 10–42× Q4's children.

## Headline results, their kind, and what the band bears on

**The kind of claim decides what the band can say about it:**
- **spread:** a variant rose among solvent members. The band bounds it.
- **retention:** a planted trait was held above an operator or drift floor. The band is silent (above).
- **history:** fate as a function of the breeding stream. The band describes the setting, and does not threaten it.
- **yield:** income or price arithmetic. No reproduction claim.
- **sorting:** a heritable difference against a matched null.

For the published positives, **the per-headline table of PR #417 ("What each headline can still claim") is the
reading to use.** Nothing here says the band qualifies them.

| ticket | headline, as its report states it | kind | read in | fauna read | band in that window: window-local / per life (median [range] over seeds) | what the band bears on |
|---|---|---|---|---|---|---|
| RBT-19 P-801 | yield heritability; the holistic lead from season 19; the null on the probes (`runs/RBT-19/REPORT.md:40-44, 113-153`) | yield; the probes are physics | the whole run, in 100-season blocks | both | **holistic saturated / saturated**, 3.9–4.6 / 3.1–4.1. **Designed saturated / transition**, 2.7–3.0 / 1.3–1.7, over a sieve (viability −1.1 to −1.6) | none on the yield or probe claims |
| RBT-80 | seeded − drift carriage, NO VERDICT; seeded arms 0.96 / 0.72 / 0.92 against floors of about 0.52 (`docs/artifacts/RBT-80-three-seed-report.txt` §1-2) | retention | plateau 250–299 | designed | **not measured**: no lineage (see [below](#rbt-80-not-measured)) | silent on retention. The drift comparator ran a different economy, with the gate (DRIFT-GATE.md) |
| RBT-90 part 2 | open-loop champions; oscillator discarded 5 / acquired 5; depth relabelled as demography (`runs/RBT-90/PART2-VERDICT.md:11-30`) | physics; history count | champions at 590 (window 500–599) | holistic | **saturated / saturated**, 3.56 [3.23, 4.10] / 3.32 [2.74, 3.80]; designed 2.84 / 2.36 | none |
| RBT-99 | R-body class A, +0.519 in recovery; shift − base +0.371, against price arithmetic of +0.689 (`runs/RBT-99/REPORT.md:7-30`) | yield | recovery [T+60, T+160) | both (R-body) | **holistic saturated / saturated**, 3.28 / 2.90. **Designed mixed**: window-local saturated on 4 seeds, transition on 3, few on 3; per life selecting on 7, few on 3. Base: both saturated | none: yield arithmetic, and the carriage readouts are UNVALIDATED (V3) |
| RBT-100 | R-body class A, +0.286 in recovery; shift − base +0.138 (`runs/RBT-100/REPORT.md:5-31`) | yield; survivorship | recovery [T+60, T+160) | both | **holistic transition / transition**, 1.76 / 1.53. **Designed few** on 8 of 10 seeds (1.4 eligible a season; extinct on 5) | none |
| RBT-101 | class C, the falsifier fires: R-body −0.310, "wholly by the arithmetic of the furniture"; re-wiring NO CHANGE (`runs/RBT-101/REPORT.md:5-40`) | yield; the re-wiring null is a spread readout | recovery [T+60, T+160) | both | **saturated / saturated**: holistic 4.22 / 3.85, designed 5.11 / 4.74 | the re-wiring null is under the committed rule |
| RBT-105 | R1 substantial history, 5 flips in 14; R2 founders shift the late oscillator birth rate (`runs/RBT-105/REPORT.md:20-37`) | history | R2: [300, 600); A/A: [60, 160) | holistic | **saturated / saturated**: 3.67 / 3.42 (K = 1) and 3.35 / 3.10 (K = 2) over [300, 600) | describes the setting; does not threaten a history result |
| RBT-106 (paper 10) | H SUPPORTED: HELD HU 0, HP 9, read at 300 and 599 (`runs/RBT-106/H-READOUT.md:11-18`); P1 P-NULL | H: retention; P1: retention null | [0, 300) and [300, 600) | designed | **saturated / saturated in both worlds**: HP 10.8 / 9.0 and 10.2 / 8.2, HU 3.3 / 2.7 and 2.9 / 2.4. P1 3.7–3.8 / 2.4–2.7, over a sieve (viability −0.5) | H: silent. P1: the null is under the committed rule |
| RBT-104 S1 (paper 10's comparator) | S1 primary FD 2 (`runs/RBT-104/REPORT.md` §verdict) | P1's comparator | [0, 300) and [300, 600) | designed | **saturated / saturated**, 2.62–2.66 / 2.08–2.24 | as P1 |
| RBT-107 | H-REP-DES SUPPORTED (fragile) at T+110; H1-DES and H1-PAIR NOT SUPPORTED at T+800 (`runs/RBT-107/hrep/REPORT.md:13-27`, `h1/REPORT.md:17-40`) | sorting against a matched null | [T, T+110) and [T+110, T+800), T = 360 | designed (primary), both for PAIR | **saturated / saturated in every arm and window.** Designed base 2.7–2.9 / 2.3–2.5, cull20 2.7–2.9 / 2.4–2.5, shift **5.7–5.8** / 5.1–5.5; holistic 3.5–4.6 / 3.3–4.4 | H-REP: none (its nulls are regime-matched). H1 nulls: under the committed rule, and **the scored shift arm is not in its nulls' regime**: its designed fauna reads twice the base's and cull20's |
| RBT-112 | Z FALSIFIED: HELD HU 0, HZ 1; s ∈ [0.00, 0.08] (`runs/RBT-112/READOUT.md:16-42, 73-107`) | retention; comparison is regime-matched | [0, 300) and [300, 600) | designed | **saturated / saturated**: HZ 3.81 / 3.31 and 3.43 / 2.96; HU (RBT-106) 3.32 / 2.73 and 2.88 / 2.41 | the comparison: none. The s bound is a property of this economy |

**RBT-106, beside the sieve columns.** HP's designed fauna reads window-local 10.2–10.8 against HU's 2.9–3.3. On the
columns for the sieve, though, HP turns over **more**, not less:

| | deaths by age, [0, 300) / [300, 600) | births per window, median [range] |
|---|---|---|
| HP | 0.27 / 0.33 | 918 [806, 1067] / 832 [794, 909] |
| HU | 0.38 / 0.53 | 663 [612, 771] / 536 [501, 570] |

HP has more births on every seed. The window-local figure is about the queue above viability; the purging channel
that holds a trait is, if anything, more active in HP.

**Which bands differ from saturated.** Only yield and survivorship readings sit outside the saturated band on the
scored fauna:
- RBT-99 and RBT-100's post-shift designed fauna;
- RBT-100's post-shift holistic fauna, which is in the transition band.

**RBT-80, a retention result, is not measured here.**

## RBT-80: not measured

- **No lineage exists for RBT-80's nine arms** in the repo or on any checkpoint branch. `runs/RBT-80/` holds configs
  only, and there is no `ckpt/rbt-80-*`.
- **Its committed artefacts are aggregate:**
  - survivor-weighted mean lifetime scores of the whole arm, per season (`docs/artifacts/RBT-80-series.txt`). Over
    300 seasons they average 1.08 / 1.02 / 1.03 in the seeded arms (seeds A / B / C) and 0.65 in the controls;
  - the seeded arms' plateau carriers at 0.97–1.22 and non-carriers at 0.08 / 0.64 / 0.47
    (`RBT-80-within-arm.txt`, seasons 250–299).
- None of these is a per-member eligible-income figure, so no band is given.
- `BREEDING-RULES.md`'s retention table replays RBT-80's numbers in the replica instead.

## All headline windows, per arm

This is the median [range] over each arm's seeds. Every window is named. The per-seed figures are in
`regime/RBT-<n>.txt`, and the standard 0–49 / 50–149 / 150–299 / 300–449 / 450–599 blocks for every arm are in
`regime/TABLES.md`, which carries the extra columns. Onset-relative windows use each seed's T from
`runs/RBT-92/onset.txt` (RBT-90, 99, 100 and 101), or T = 360 (RBT-107).

| ticket | arm (runs) | fauna | window | band, window-local (runs per band) | band, per life | saturation, window-local | saturation, per life | viability | deaths by age | eligible breeders | Q5÷Q4 children | gen / season |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RBT-19 | P-801 (1) | conventional | 0-99 | saturated | transition | 2.79 | 1.28 | -1.61 | 0.08 | 41.03 | 13.39 | 0.04 |
| RBT-19 | P-801 (1) | conventional | 100-299 | saturated | transition | 2.66 | 1.44 | -1.58 | 0.13 | 45.10 | 42.04 | 0.03 |
| RBT-19 | P-801 (1) | conventional | 300-499 | saturated | transition | 2.93 | 1.66 | -1.13 | 0.17 | 46.92 | 10.22 | 0.04 |
| RBT-19 | P-801 (1) | conventional | 500-599 | saturated | transition | 2.99 | 1.45 | -1.58 | 0.22 | 48.02 | - | 0.03 |
| RBT-19 | P-801 (1) | holistic | 0-99 | saturated | saturated | 3.90 | 3.10 | 0.62 | 0.24 | 40.29 | 1.31 | 0.05 |
| RBT-19 | P-801 (1) | holistic | 100-299 | saturated | saturated | 4.01 | 3.64 | 0.94 | 0.41 | 50.33 | 1.07 | 0.03 |
| RBT-19 | P-801 (1) | holistic | 300-499 | saturated | saturated | 4.38 | 3.81 | 0.94 | 0.37 | 49.52 | 1.18 | 0.02 |
| RBT-19 | P-801 (1) | holistic | 500-599 | saturated | saturated | 4.61 | 4.06 | 0.33 | 0.45 | 50.89 | 5.37 | 0.03 |
| RBT-90 | base (10) | conventional | before [T-100,T) | saturated | saturated | 2.60 [2.47, 2.88] | 2.18 [1.89, 2.65] | 0.69 [0.28, 0.98] | 0.50 [0.45, 0.58] | 51.14 [48.64, 52.44] | 1.04 [0.83, 1.23] | 0.03 [0.02, 0.04] |
| RBT-90 | base (10) | conventional | transient [T,T+60) | saturated | saturated (saturated 9, transition 1) | 2.78 [2.07, 3.29] | 2.28 [1.54, 2.56] | 0.76 [0.10, 1.80] | 0.52 [0.41, 0.74] | 51.17 [48.33, 53.67] | 0.91 [0.56, 1.52] | 0.03 [0.02, 0.05] |
| RBT-90 | base (10) | conventional | recovery [T+60,T+160) | saturated | saturated (saturated 9, transition 1) | 2.75 [2.01, 3.08] | 2.37 [1.62, 3.06] | 0.74 [-0.17, 1.91] | 0.53 [0.37, 0.70] | 51.95 [47.07, 53.93] | 1.08 [0.88, 1.38] | 0.03 [0.03, 0.04] |
| RBT-90 | base (10) | conventional | season-590 champions: 500-599 | saturated | saturated (saturated 8, transition 2) | 2.84 [2.15, 3.52] | 2.36 [1.52, 3.34] | 0.19 [-0.46, 1.43] | 0.58 [0.45, 0.75] | 52.19 [49.39, 54.69] | 1.09 [0.62, 2.52] | 0.03 [0.02, 0.04] |
| RBT-90 | base (10) | holistic | before [T-100,T) | saturated | saturated | 3.41 [2.84, 4.09] | 3.01 [2.60, 4.18] | 1.57 [1.00, 2.21] | 0.60 [0.49, 0.65] | 50.79 [48.11, 52.53] | 1.08 [0.93, 1.42] | 0.04 [0.02, 0.04] |
| RBT-90 | base (10) | holistic | transient [T,T+60) | saturated | saturated | 3.47 [2.63, 4.87] | 3.36 [2.52, 4.23] | 2.02 [0.37, 2.53] | 0.64 [0.40, 0.75] | 52.25 [47.77, 53.38] | 1.11 [0.78, 1.44] | 0.03 [0.03, 0.04] |
| RBT-90 | base (10) | holistic | recovery [T+60,T+160) | saturated | saturated | 3.68 [3.02, 4.11] | 3.43 [2.77, 3.72] | 1.75 [0.91, 2.23] | 0.62 [0.51, 0.71] | 51.75 [50.49, 53.73] | 1.09 [0.74, 1.65] | 0.03 [0.02, 0.04] |
| RBT-90 | base (10) | holistic | season-590 champions: 500-599 | saturated | saturated | 3.56 [3.23, 4.10] | 3.32 [2.74, 3.80] | 0.93 [0.29, 1.51] | 0.63 [0.57, 0.75] | 51.62 [50.49, 53.20] | 1.22 [0.82, 1.69] | 0.03 [0.03, 0.04] |
| RBT-99 | cull (10) | conventional | before [T-100,T) | saturated | saturated | 2.60 [2.47, 2.88] | 2.33 [2.14, 2.69] | 0.77 [0.27, 1.10] | 0.50 [0.45, 0.58] | 51.14 [48.64, 52.44] | 0.92 [0.68, 1.46] | 0.03 [0.02, 0.04] |
| RBT-99 | cull (10) | conventional | transient [T,T+60) | saturated (saturated 7, none 3) | saturated (saturated 7, none 3) | 2.67 [2.37, 3.19] | 2.20 [1.85, 2.70] | 0.92 [0.17, 1.25] | 0.17 [0.00, 0.29] | 51.53 [48.65, 53.18] | 1.22 [0.83, 1.57] | 0.02 [0.01, 0.02] |
| RBT-99 | cull (10) | conventional | recovery [T+60,T+160) | saturated (saturated 7, none 3) | saturated (saturated 7, none 3) | 2.71 [2.38, 3.24] | 2.35 [1.92, 2.71] | 0.82 [0.35, 1.61] | 0.57 [0.47, 0.68] | 50.85 [49.53, 53.24] | 1.06 [0.69, 1.25] | 0.03 [0.02, 0.04] |
| RBT-99 | cull (10) | holistic | before [T-100,T) | saturated | saturated | 3.41 [2.84, 4.09] | 3.00 [2.52, 4.08] | 1.56 [0.97, 2.09] | 0.60 [0.49, 0.65] | 50.79 [48.11, 52.53] | 1.17 [0.90, 1.33] | 0.04 [0.02, 0.04] |
| RBT-99 | cull (10) | holistic | transient [T,T+60) | saturated | saturated | 3.49 [2.69, 5.04] | 3.31 [2.34, 4.76] | 1.89 [1.13, 3.13] | 0.58 [0.43, 0.75] | 52.08 [50.00, 54.50] | 1.08 [0.72, 1.46] | 0.03 [0.02, 0.04] |
| RBT-99 | cull (10) | holistic | recovery [T+60,T+160) | saturated | saturated | 3.64 [2.79, 4.45] | 3.54 [2.32, 4.11] | 1.87 [-0.33, 2.37] | 0.63 [0.48, 0.71] | 51.97 [49.59, 53.73] | 0.87 [0.67, 5.67] | 0.03 [0.03, 0.04] |
| RBT-99 | shift (10) | conventional | before [T-100,T) | saturated | transition (transition 9, saturated 1) | 2.60 [2.47, 2.88] | 1.45 [1.31, 1.84] | 0.24 [-0.14, 0.54] | 0.50 [0.45, 0.58] | 51.14 [48.64, 52.44] | 0.56 [0.38, 1.02] | 0.03 [0.02, 0.04] |
| RBT-99 | shift (10) | conventional | transient [T,T+60) | transition (transition 5, selecting 5) | selecting (selecting 6, transition 4) | 1.29 [0.58, 1.80] | 0.96 [0.82, 1.04] | -0.42 [-0.65, -0.29] | 0.06 [0.03, 0.08] | 22.75 [12.22, 33.65] | 3.91 [1.50, 6.37] | 0.06 [0.04, 0.11] |
| RBT-99 | shift (10) | conventional | recovery [T+60,T+160) | saturated (saturated 4, few 3, transition 3) | selecting (selecting 7, few 3) | 2.03 [1.50, 6.09] | 0.86 [0.47, 1.65] | -0.52 [-0.86, 0.46] | 0.05 [0.00, 0.21] | 32.24 [0.69, 44.68] | 3.23 [1.48, 15.65] | 0.03 [-0.21, 0.04] |
| RBT-99 | shift (10) | holistic | before [T-100,T) | saturated | saturated | 3.41 [2.84, 4.09] | 2.72 [2.13, 4.00] | 1.37 [0.75, 2.03] | 0.60 [0.49, 0.65] | 50.79 [48.11, 52.53] | 1.03 [0.91, 1.24] | 0.04 [0.02, 0.04] |
| RBT-99 | shift (10) | holistic | transient [T,T+60) | saturated | saturated | 2.71 [1.98, 4.60] | 2.61 [1.81, 4.11] | 0.88 [0.07, 2.17] | 0.45 [0.31, 0.62] | 48.33 [46.63, 52.50] | 1.01 [0.66, 1.44] | 0.03 [0.02, 0.04] |
| RBT-99 | shift (10) | holistic | recovery [T+60,T+160) | saturated | saturated | 3.28 [2.37, 4.20] | 2.90 [1.96, 4.09] | 1.26 [0.60, 2.10] | 0.54 [0.45, 0.64] | 51.25 [49.28, 53.42] | 1.01 [0.70, 1.63] | 0.03 [0.03, 0.05] |
| RBT-100 | cull (10) | conventional | before [T-100,T) | saturated | saturated | 2.60 [2.47, 2.88] | 2.21 [1.99, 2.64] | 0.68 [0.29, 1.08] | 0.50 [0.45, 0.58] | 51.14 [48.64, 52.44] | 0.95 [0.65, 1.32] | 0.03 [0.02, 0.04] |
| RBT-100 | cull (10) | conventional | transient [T,T+60) | saturated | saturated | 2.66 [2.13, 3.28] | 2.14 [1.85, 2.77] | 0.61 [0.31, 1.48] | 0.44 [0.24, 0.51] | 51.69 [48.57, 53.77] | 1.09 [0.76, 1.99] | 0.03 [0.01, 0.04] |
| RBT-100 | cull (10) | conventional | recovery [T+60,T+160) | saturated | saturated | 2.71 [2.44, 3.28] | 2.22 [2.00, 3.17] | 0.94 [0.31, 1.78] | 0.55 [0.48, 0.66] | 51.85 [49.65, 54.29] | 1.03 [0.70, 1.28] | 0.03 [0.03, 0.05] |
| RBT-100 | cull (10) | holistic | before [T-100,T) | saturated | saturated | 3.41 [2.84, 4.09] | 3.03 [2.56, 4.20] | 1.58 [1.01, 2.16] | 0.60 [0.49, 0.65] | 50.79 [48.11, 52.53] | 1.07 [0.93, 1.42] | 0.04 [0.02, 0.04] |
| RBT-100 | cull (10) | holistic | transient [T,T+60) | saturated | saturated | 3.46 [2.81, 5.21] | 3.27 [2.48, 4.89] | 1.87 [0.70, 2.72] | 0.59 [0.43, 0.75] | 51.62 [50.00, 54.00] | 1.16 [1.00, 1.46] | 0.03 [0.01, 0.04] |
| RBT-100 | cull (10) | holistic | recovery [T+60,T+160) | saturated | saturated | 3.66 [2.84, 4.80] | 3.43 [2.42, 4.44] | 1.87 [1.05, 2.93] | 0.67 [0.56, 0.72] | 53.11 [49.63, 53.73] | 1.02 [0.61, 1.28] | 0.03 [0.02, 0.04] |
| RBT-100 | shift (10) | conventional | before [T-100,T) | saturated | transition (transition 9, saturated 1) | 2.60 [2.47, 2.88] | 1.50 [1.38, 1.84] | 0.25 [-0.08, 0.50] | 0.50 [0.45, 0.58] | 51.14 [48.64, 52.44] | 0.61 [0.42, 0.92] | 0.03 [0.02, 0.04] |
| RBT-100 | shift (10) | conventional | transient [T,T+60) | selecting | selecting | 0.65 [0.03, 0.77] | 0.41 [0.29, 0.50] | -1.27 [-1.57, -0.99] | 0.12 [0.09, 0.14] | 24.40 [16.43, 29.63] | 67.25 [15.24, 116.26] | 0.04 [0.02, 0.09] |
| RBT-100 | shift (10) | conventional | recovery [T+60,T+160) | few (few 8, transition 2) | few (few 7, selecting 2, none 1) | 5.11 [1.28, 5.80] | 0.59 [0.41, 0.87] | -1.19 [-1.75, -0.85] | 0.01 [0.00, 0.12] | 1.36 [0.17, 29.04] | 23.52 [6.97, 93.49] | 0.04 [-0.01, 0.09] |
| RBT-100 | shift (10) | holistic | before [T-100,T) | saturated | saturated | 3.41 [2.84, 4.09] | 2.38 [1.95, 3.38] | 1.14 [0.59, 1.67] | 0.60 [0.49, 0.65] | 50.79 [48.11, 52.53] | 1.04 [0.76, 1.20] | 0.04 [0.02, 0.04] |
| RBT-100 | shift (10) | holistic | transient [T,T+60) | transition (transition 6, selecting 3, saturated 1) | transition (transition 8, saturated 1, selecting 1) | 1.27 [1.13, 2.22] | 1.25 [0.83, 2.01] | -0.06 [-0.50, 0.75] | 0.38 [0.23, 0.52] | 44.28 [35.13, 49.10] | 1.38 [0.91, 12.17] | 0.03 [0.02, 0.04] |
| RBT-100 | shift (10) | holistic | recovery [T+60,T+160) | transition (transition 8, saturated 2) | transition | 1.76 [1.34, 1.99] | 1.53 [1.14, 1.76] | 0.17 [-0.10, 0.55] | 0.43 [0.35, 0.56] | 45.80 [42.92, 48.52] | 1.02 [0.92, 1.59] | 0.03 [0.02, 0.04] |
| RBT-101 | cull (4) | conventional | before [T-100,T) | saturated | saturated | 2.62 [2.53, 2.88] | 2.27 [2.02, 2.65] | 0.65 [0.51, 0.87] | 0.48 [0.46, 0.54] | 51.14 [49.58, 51.57] | 1.06 [0.75, 1.21] | 0.03 [0.02, 0.04] |
| RBT-101 | cull (4) | conventional | transient [T,T+60) | saturated | saturated (saturated 3, transition 1) | 2.82 [2.26, 3.29] | 2.09 [1.54, 2.34] | 0.92 [0.42, 1.31] | 0.56 [0.45, 0.61] | 51.48 [49.78, 52.53] | 0.91 [0.56, 1.26] | 0.03 [0.03, 0.04] |
| RBT-101 | cull (4) | conventional | recovery [T+60,T+160) | saturated | saturated (saturated 3, transition 1) | 2.67 [2.01, 2.75] | 2.32 [1.62, 2.42] | 0.85 [-0.17, 1.12] | 0.53 [0.37, 0.57] | 51.23 [47.07, 52.23] | 1.13 [0.98, 1.35] | 0.03 [0.03, 0.04] |
| RBT-101 | cull (4) | holistic | before [T-100,T) | saturated | saturated | 3.42 [2.84, 4.07] | 3.17 [2.57, 4.08] | 1.69 [1.03, 2.09] | 0.59 [0.57, 0.64] | 51.09 [50.83, 52.44] | 1.02 [0.85, 1.19] | 0.03 [0.02, 0.04] |
| RBT-101 | cull (4) | holistic | transient [T,T+60) | saturated | saturated | 3.31 [3.02, 5.04] | 2.97 [2.93, 4.76] | 1.61 [1.42, 3.13] | 0.62 [0.60, 0.64] | 52.25 [51.35, 52.87] | 0.95 [0.60, 1.25] | 0.03 [0.03, 0.04] |
| RBT-101 | cull (4) | holistic | recovery [T+60,T+160) | saturated | saturated | 3.35 [3.13, 4.45] | 3.24 [2.94, 4.11] | 1.71 [1.01, 2.37] | 0.64 [0.53, 0.66] | 52.03 [50.84, 52.64] | 1.12 [0.74, 1.18] | 0.03 [0.03, 0.04] |
| RBT-101 | shift (10) | conventional | before [T-100,T) | saturated | saturated | 2.60 [2.47, 2.88] | 3.13 [2.48, 3.66] | 1.18 [0.61, 1.85] | 0.50 [0.45, 0.58] | 51.14 [48.64, 52.44] | 0.96 [0.52, 1.30] | 0.03 [0.02, 0.04] |
| RBT-101 | shift (10) | conventional | transient [T,T+60) | saturated | saturated | 5.76 [4.04, 6.72] | 4.83 [3.74, 6.12] | 3.62 [2.00, 4.55] | 0.67 [0.62, 0.82] | 55.17 [53.95, 56.38] | 0.97 [0.56, 1.59] | 0.03 [0.02, 0.05] |
| RBT-101 | shift (10) | conventional | recovery [T+60,T+160) | saturated | saturated | 5.11 [4.77, 6.61] | 4.74 [4.16, 6.30] | 3.19 [2.66, 5.05] | 0.71 [0.65, 0.80] | 55.20 [53.75, 56.54] | 0.89 [0.59, 1.29] | 0.03 [0.02, 0.04] |
| RBT-101 | shift (10) | holistic | before [T-100,T) | saturated | saturated | 3.41 [2.84, 4.09] | 3.18 [2.68, 4.31] | 1.67 [1.10, 2.26] | 0.60 [0.49, 0.65] | 50.79 [48.11, 52.53] | 1.02 [0.65, 1.33] | 0.04 [0.02, 0.04] |
| RBT-101 | shift (10) | holistic | transient [T,T+60) | saturated | saturated | 4.17 [3.34, 5.47] | 4.03 [3.17, 4.97] | 2.20 [1.37, 3.41] | 0.63 [0.52, 0.73] | 52.73 [50.53, 54.30] | 1.01 [0.58, 1.46] | 0.03 [0.02, 0.04] |
| RBT-101 | shift (10) | holistic | recovery [T+60,T+160) | saturated | saturated | 4.22 [3.78, 5.82] | 3.85 [3.62, 5.94] | 2.12 [1.80, 3.78] | 0.66 [0.59, 0.72] | 53.50 [50.94, 54.18] | 0.92 [0.63, 1.21] | 0.03 [0.02, 0.04] |
| RBT-104 | S1 (10) | conventional | to 300 [0,300) | saturated | saturated (saturated 9, transition 1) | 2.62 [2.25, 2.95] | 2.08 [1.73, 2.50] | 0.32 [0.06, 0.77] | 0.38 [0.37, 0.42] | 48.69 [48.01, 50.26] | 1.09 [0.92, 1.37] | 0.03 [0.03, 0.04] |
| RBT-104 | S1 (10) | conventional | window income [300,600) | saturated | saturated | 2.66 [2.49, 3.14] | 2.24 [1.96, 2.71] | 0.56 [0.06, 1.26] | 0.53 [0.44, 0.58] | 51.72 [50.22, 53.39] | 1.03 [0.70, 1.33] | 0.03 [0.03, 0.04] |
| RBT-104 | S1 (10) | holistic | to 300 [0,300) | saturated | saturated | 3.18 [2.67, 3.69] | 2.82 [2.33, 3.38] | 1.17 [0.55, 1.45] | 0.46 [0.38, 0.55] | 46.73 [43.49, 48.81] | 1.05 [0.88, 1.23] | 0.04 [0.03, 0.04] |
| RBT-104 | S1 (10) | holistic | window income [300,600) | saturated | saturated | 3.57 [3.00, 4.05] | 3.29 [2.71, 3.91] | 1.50 [0.69, 1.99] | 0.62 [0.51, 0.70] | 51.67 [50.45, 53.13] | 1.06 [0.92, 1.27] | 0.03 [0.03, 0.04] |
| RBT-104 | S8 (10) | conventional | to 300 [0,300) | saturated | saturated (saturated 7, transition 3) | 2.65 [2.36, 2.96] | 1.95 [1.58, 2.31] | 0.70 [0.24, 1.22] | 0.26 [0.21, 0.34] | 47.73 [44.87, 49.88] | 1.00 [0.83, 1.26] | 0.04 [0.03, 0.04] |
| RBT-104 | S8 (10) | conventional | window income [300,600) | saturated | saturated (saturated 9, transition 1) | 2.87 [2.34, 3.16] | 2.36 [1.77, 2.68] | 1.16 [0.53, 1.56] | 0.41 [0.34, 0.48] | 52.42 [49.69, 53.28] | 1.00 [0.90, 1.12] | 0.03 [0.03, 0.04] |
| RBT-104 | S8 (10) | holistic | to 300 [0,300) | saturated | saturated | 3.18 [2.67, 3.69] | 2.82 [2.33, 3.38] | 1.17 [0.55, 1.45] | 0.46 [0.38, 0.55] | 46.73 [43.49, 48.81] | 1.05 [0.88, 1.23] | 0.04 [0.03, 0.04] |
| RBT-104 | S8 (10) | holistic | window income [300,600) | saturated | saturated | 3.57 [3.00, 4.05] | 3.29 [2.71, 3.91] | 1.50 [0.69, 1.99] | 0.62 [0.51, 0.70] | 51.67 [50.45, 53.13] | 1.06 [0.92, 1.27] | 0.03 [0.03, 0.04] |
| RBT-105 | b0 (1) | conventional | A/A [60,160) | saturated | saturated | 2.60 | 2.15 | 0.40 | 0.44 | 49.70 | 1.02 | 0.03 |
| RBT-105 | b0 (1) | conventional | R2 [300,600) | saturated | saturated | 2.59 | 2.08 | 0.45 | 0.53 | 51.02 | 1.06 | 0.03 |
| RBT-105 | b0 (1) | holistic | A/A [60,160) | saturated | saturated | 3.21 | 3.28 | 1.34 | 0.57 | 50.77 | 1.13 | 0.05 |
| RBT-105 | b0 (1) | holistic | R2 [300,600) | saturated | saturated | 4.05 | 3.65 | 1.57 | 0.60 | 51.68 | 1.02 | 0.03 |
| RBT-105 | b1 (8) | conventional | A/A [60,160) | saturated | saturated | 2.49 [2.33, 2.69] | 2.01 [1.87, 2.15] | 0.30 [0.01, 0.49] | 0.45 [0.39, 0.53] | 49.03 [47.80, 50.61] | 1.15 [0.90, 1.33] | 0.04 [0.03, 0.04] |
| RBT-105 | b1 (8) | conventional | R2 [300,600) | saturated | saturated (saturated 7, transition 1) | 2.76 [2.26, 3.01] | 2.32 [1.68, 2.64] | 0.71 [0.05, 1.21] | 0.55 [0.43, 0.66] | 51.73 [49.19, 53.40] | 1.07 [0.99, 1.30] | 0.03 [0.03, 0.04] |
| RBT-105 | b1 (8) | holistic | A/A [60,160) | saturated | saturated | 2.94 [2.52, 3.35] | 2.66 [2.29, 3.06] | 1.07 [0.73, 1.39] | 0.56 [0.42, 0.63] | 49.12 [47.40, 50.72] | 1.13 [0.84, 1.33] | 0.04 [0.03, 0.05] |
| RBT-105 | b1 (8) | holistic | R2 [300,600) | saturated | saturated | 3.67 [3.23, 4.04] | 3.42 [2.87, 3.96] | 1.58 [1.25, 2.47] | 0.66 [0.55, 0.77] | 52.35 [51.60, 53.71] | 0.99 [0.83, 1.24] | 0.03 [0.03, 0.04] |
| RBT-105 | b2 (8) | conventional | A/A [60,160) | saturated | saturated | 2.49 [2.33, 2.69] | 2.01 [1.87, 2.15] | 0.30 [0.01, 0.49] | 0.45 [0.39, 0.53] | 49.03 [47.80, 50.61] | 1.15 [0.90, 1.33] | 0.04 [0.03, 0.04] |
| RBT-105 | b2 (8) | conventional | R2 [300,600) | saturated | saturated (saturated 7, transition 1) | 2.76 [2.26, 3.01] | 2.32 [1.68, 2.64] | 0.71 [0.05, 1.21] | 0.55 [0.43, 0.66] | 51.73 [49.19, 53.40] | 1.07 [0.99, 1.30] | 0.03 [0.03, 0.04] |
| RBT-105 | b2 (8) | holistic | A/A [60,160) | saturated | saturated | 2.79 [2.17, 3.65] | 2.64 [2.02, 3.37] | 0.99 [0.29, 1.74] | 0.55 [0.35, 0.63] | 48.15 [46.61, 51.39] | 1.09 [1.00, 1.36] | 0.04 [0.03, 0.05] |
| RBT-105 | b2 (8) | holistic | R2 [300,600) | saturated | saturated | 3.35 [3.12, 3.66] | 3.10 [2.87, 3.41] | 1.30 [1.16, 1.46] | 0.59 [0.58, 0.63] | 51.77 [50.93, 51.99] | 1.04 [0.91, 1.17] | 0.03 [0.03, 0.04] |
| RBT-106 | HP (10) | conventional | to 300 [0,300) | saturated | saturated | 10.80 [8.17, 13.40] | 9.01 [6.57, 11.89] | 3.30 [1.96, 5.88] | 0.27 [0.23, 0.31] | 52.31 [51.34, 53.48] | 1.05 [0.98, 1.15] | 0.04 [0.03, 0.04] |
| RBT-106 | HP (10) | conventional | window income [300,600) | saturated | saturated | 10.18 [7.58, 13.39] | 8.22 [5.92, 11.90] | 2.90 [1.17, 5.64] | 0.33 [0.29, 0.35] | 53.88 [52.77, 54.75] | 1.05 [0.94, 1.25] | 0.03 [0.03, 0.04] |
| RBT-106 | HP (10) | holistic | to 300 [0,300) | saturated | saturated | 3.70 [2.91, 4.45] | 3.10 [2.19, 3.86] | 0.50 [-0.48, 0.78] | 0.29 [0.10, 0.37] | 43.08 [24.24, 46.63] | 1.28 [0.93, 1.98] | 0.04 [0.03, 0.05] |
| RBT-106 | HP (10) | holistic | window income [300,600) | saturated | saturated | 4.70 [3.62, 7.61] | 4.14 [3.09, 7.07] | 1.24 [0.63, 3.03] | 0.46 [0.38, 0.53] | 50.80 [49.22, 52.83] | 1.02 [0.86, 1.29] | 0.03 [0.03, 0.04] |
| RBT-106 | HU (10) | conventional | to 300 [0,300) | saturated | saturated | 3.32 [2.68, 4.33] | 2.73 [2.13, 3.50] | 0.86 [0.40, 1.61] | 0.38 [0.33, 0.43] | 50.04 [48.92, 51.10] | 1.05 [0.97, 1.20] | 0.03 [0.03, 0.04] |
| RBT-106 | HU (10) | conventional | window income [300,600) | saturated | saturated | 2.88 [2.41, 3.08] | 2.41 [1.94, 2.62] | 0.65 [0.36, 0.91] | 0.53 [0.48, 0.57] | 51.98 [50.96, 52.60] | 1.07 [0.85, 1.26] | 0.03 [0.02, 0.04] |
| RBT-106 | HU (10) | holistic | to 300 [0,300) | saturated | saturated | 3.18 [2.67, 3.69] | 2.82 [2.33, 3.38] | 1.17 [0.55, 1.45] | 0.46 [0.38, 0.55] | 46.73 [43.49, 48.81] | 1.05 [0.88, 1.23] | 0.04 [0.03, 0.04] |
| RBT-106 | HU (10) | holistic | window income [300,600) | saturated | saturated | 3.57 [3.00, 4.05] | 3.29 [2.71, 3.91] | 1.50 [0.69, 1.99] | 0.62 [0.51, 0.70] | 51.67 [50.45, 53.13] | 1.06 [0.92, 1.27] | 0.03 [0.03, 0.04] |
| RBT-106 | P1 (10) | conventional | to 300 [0,300) | saturated | saturated | 3.65 [3.24, 3.93] | 2.43 [2.04, 3.04] | -0.51 [-0.84, -0.37] | 0.23 [0.19, 0.26] | 48.50 [46.94, 50.10] | 1.79 [1.49, 3.42] | 0.03 [0.03, 0.04] |
| RBT-106 | P1 (10) | conventional | window income [300,600) | saturated | saturated | 3.82 [3.58, 4.81] | 2.74 [2.19, 3.28] | -0.46 [-0.86, -0.03] | 0.30 [0.25, 0.35] | 51.02 [49.58, 52.26] | 2.02 [1.30, 3.38] | 0.04 [0.03, 0.04] |
| RBT-106 | P1 (10) | holistic | to 300 [0,300) | saturated | saturated | 3.70 [2.91, 4.45] | 3.10 [2.19, 3.86] | 0.50 [-0.48, 0.78] | 0.29 [0.10, 0.37] | 43.08 [24.24, 46.63] | 1.28 [0.93, 1.98] | 0.04 [0.03, 0.05] |
| RBT-106 | P1 (10) | holistic | window income [300,600) | saturated | saturated | 4.70 [3.62, 7.61] | 4.14 [3.09, 7.07] | 1.24 [0.63, 3.03] | 0.46 [0.38, 0.53] | 50.80 [49.22, 52.83] | 1.02 [0.86, 1.29] | 0.03 [0.03, 0.04] |
| RBT-107 | fresh-base (20) | conventional | before [T-100,T) | saturated | saturated | 2.67 [2.26, 3.01] | 2.17 [1.89, 2.57] | 0.62 [0.20, 1.22] | 0.50 [0.41, 0.61] | 51.23 [48.99, 52.53] | 0.92 [0.67, 1.58] | 0.03 [0.02, 0.05] |
| RBT-107 | fresh-base (20) | conventional | to H-REP [T,T+110) | saturated | saturated (saturated 19, transition 1) | 2.72 [2.13, 3.09] | 2.35 [1.69, 2.86] | 0.85 [-0.04, 1.75] | 0.53 [0.40, 0.65] | 52.19 [48.59, 53.41] | 1.02 [0.80, 1.47] | 0.03 [0.02, 0.05] |
| RBT-107 | fresh-base (20) | conventional | to H1 [T+110,T+800) | saturated | saturated | 2.92 [2.44, 3.31] | 2.52 [2.10, 2.95] | 1.13 [0.64, 1.74] | 0.57 [0.51, 0.63] | 52.80 [51.29, 54.12] | 1.01 [0.87, 1.17] | 0.03 [0.03, 0.04] |
| RBT-107 | fresh-base (20) | conventional | H1 tail [T+700,T+800) | saturated | saturated | 2.93 [2.22, 3.96] | 2.56 [1.96, 3.50] | 1.09 [0.28, 2.38] | 0.60 [0.48, 0.75] | 52.99 [51.08, 55.02] | 1.02 [0.58, 1.52] | 0.03 [0.02, 0.05] |
| RBT-107 | fresh-base (20) | holistic | before [T-100,T) | saturated (saturated 19, none 1) | saturated (saturated 19, none 1) | 3.54 [3.13, 5.29] | 3.36 [2.74, 4.85] | 1.80 [1.04, 3.15] | 0.63 [0.44, 0.69] | 51.73 [47.21, 52.88] | 1.00 [0.66, 1.19] | 0.03 [0.03, 0.04] |
| RBT-107 | fresh-base (20) | holistic | to H-REP [T,T+110) | saturated (saturated 19, none 1) | saturated (saturated 19, none 1) | 3.53 [2.99, 4.55] | 3.36 [2.70, 4.33] | 1.75 [0.92, 3.04] | 0.62 [0.43, 0.76] | 52.19 [48.64, 54.45] | 1.08 [0.66, 2.01] | 0.03 [0.02, 0.04] |
| RBT-107 | fresh-base (20) | holistic | to H1 [T+110,T+800) | saturated (saturated 19, none 1) | saturated (saturated 19, none 1) | 3.99 [3.55, 5.04] | 3.80 [3.28, 4.71] | 2.25 [1.78, 3.56] | 0.68 [0.61, 0.78] | 53.17 [51.21, 53.88] | 1.05 [0.92, 1.14] | 0.03 [0.03, 0.04] |
| RBT-107 | fresh-base (20) | holistic | H1 tail [T+700,T+800) | saturated (saturated 19, none 1) | saturated (saturated 19, none 1) | 4.14 [3.31, 5.09] | 3.91 [2.90, 4.99] | 2.10 [1.48, 3.64] | 0.70 [0.59, 0.82] | 52.95 [50.60, 55.87] | 1.02 [0.67, 2.10] | 0.04 [0.02, 0.05] |
| RBT-107 | fresh-cull20 (20) | conventional | before [T-100,T) | saturated | saturated | 2.67 [2.26, 3.01] | 2.20 [1.93, 2.67] | 0.64 [0.18, 1.24] | 0.50 [0.41, 0.61] | 51.23 [48.99, 52.53] | 0.99 [0.71, 1.36] | 0.03 [0.02, 0.05] |
| RBT-107 | fresh-cull20 (20) | conventional | to H-REP [T,T+110) | saturated | saturated | 2.68 [2.40, 2.98] | 2.36 [2.04, 2.62] | 0.83 [0.32, 1.47] | 0.43 [0.36, 0.51] | 51.24 [49.37, 53.30] | 1.03 [0.83, 1.54] | 0.03 [0.02, 0.04] |
| RBT-107 | fresh-cull20 (20) | conventional | to H1 [T+110,T+800) | saturated | saturated | 2.91 [2.58, 3.19] | 2.51 [2.12, 2.90] | 1.05 [0.49, 1.68] | 0.59 [0.48, 0.68] | 52.92 [51.24, 54.05] | 1.00 [0.89, 1.15] | 0.03 [0.03, 0.04] |
| RBT-107 | fresh-cull20 (20) | conventional | H1 tail [T+700,T+800) | saturated | saturated | 2.99 [2.51, 3.50] | 2.52 [2.03, 3.03] | 1.09 [0.41, 1.61] | 0.62 [0.53, 0.75] | 53.22 [51.86, 54.90] | 1.06 [0.60, 1.56] | 0.03 [0.02, 0.05] |
| RBT-107 | fresh-cull20 (20) | holistic | before [T-100,T) | saturated (saturated 19, none 1) | saturated (saturated 19, none 1) | 3.54 [3.13, 5.29] | 3.33 [2.76, 5.00] | 1.84 [1.06, 3.26] | 0.63 [0.44, 0.69] | 51.73 [47.21, 52.88] | 0.99 [0.65, 1.25] | 0.03 [0.03, 0.04] |
| RBT-107 | fresh-cull20 (20) | holistic | to H-REP [T,T+110) | saturated (saturated 19, none 1) | saturated (saturated 19, none 1) | 3.52 [2.81, 5.58] | 3.34 [2.42, 5.03] | 1.84 [1.01, 3.54] | 0.52 [0.36, 0.61] | 52.05 [47.37, 54.37] | 1.00 [0.65, 1.35] | 0.03 [0.02, 0.05] |
| RBT-107 | fresh-cull20 (20) | holistic | to H1 [T+110,T+800) | saturated (saturated 19, none 1) | saturated (saturated 19, none 1) | 3.88 [3.14, 4.90] | 3.63 [2.84, 4.63] | 2.25 [1.43, 2.82] | 0.67 [0.56, 0.75] | 53.07 [50.82, 53.79] | 1.01 [0.86, 1.19] | 0.03 [0.03, 0.04] |
| RBT-107 | fresh-cull20 (20) | holistic | H1 tail [T+700,T+800) | saturated (saturated 19, none 1) | saturated (saturated 19, none 1) | 4.10 [2.96, 5.02] | 3.93 [2.68, 4.89] | 2.10 [1.16, 3.20] | 0.69 [0.62, 0.80] | 53.58 [51.07, 54.67] | 0.89 [0.55, 1.58] | 0.04 [0.02, 0.05] |
| RBT-107 | fresh-shift (20) | conventional | before [T-100,T) | saturated | saturated | 2.67 [2.26, 3.01] | 3.06 [2.70, 3.55] | 1.15 [0.64, 1.92] | 0.50 [0.41, 0.61] | 51.23 [48.99, 52.53] | 0.94 [0.63, 1.25] | 0.03 [0.02, 0.05] |
| RBT-107 | fresh-shift (20) | conventional | to H-REP [T,T+110) | saturated | saturated | 5.69 [4.43, 6.48] | 5.08 [3.78, 6.47] | 3.60 [2.11, 4.91] | 0.69 [0.58, 0.74] | 55.25 [53.55, 56.52] | 0.90 [0.67, 1.38] | 0.03 [0.02, 0.04] |
| RBT-107 | fresh-shift (20) | conventional | to H1 [T+110,T+800) | saturated | saturated | 5.84 [4.83, 6.80] | 5.45 [4.43, 6.41] | 3.90 [2.96, 4.96] | 0.73 [0.67, 0.78] | 55.52 [54.61, 56.28] | 0.99 [0.87, 1.22] | 0.03 [0.03, 0.04] |
| RBT-107 | fresh-shift (20) | conventional | H1 tail [T+700,T+800) | saturated | saturated | 5.79 [4.17, 7.49] | 5.46 [3.43, 7.14] | 3.80 [1.92, 6.02] | 0.77 [0.62, 0.85] | 55.48 [54.02, 57.08] | 0.99 [0.81, 1.45] | 0.03 [0.02, 0.04] |
| RBT-107 | fresh-shift (20) | holistic | before [T-100,T) | saturated (saturated 19, none 1) | saturated (saturated 19, none 1) | 3.54 [3.13, 5.29] | 3.49 [2.90, 5.13] | 1.94 [1.13, 3.35] | 0.63 [0.44, 0.69] | 51.73 [47.21, 52.88] | 1.03 [0.72, 1.56] | 0.03 [0.03, 0.04] |
| RBT-107 | fresh-shift (20) | holistic | to H-REP [T,T+110) | saturated (saturated 19, none 1) | saturated (saturated 19, none 1) | 4.06 [3.91, 5.72] | 3.93 [3.03, 5.08] | 2.19 [1.26, 3.62] | 0.65 [0.51, 0.75] | 52.84 [50.19, 55.08] | 1.03 [0.77, 1.53] | 0.03 [0.03, 0.04] |
| RBT-107 | fresh-shift (20) | holistic | to H1 [T+110,T+800) | saturated (saturated 19, none 1) | saturated (saturated 19, none 1) | 4.39 [3.81, 5.88] | 4.09 [3.57, 5.58] | 2.48 [1.95, 4.04] | 0.68 [0.56, 0.76] | 53.22 [51.76, 54.93] | 1.00 [0.85, 1.21] | 0.03 [0.02, 0.04] |
| RBT-107 | fresh-shift (20) | holistic | H1 tail [T+700,T+800) | saturated (saturated 19, none 1) | saturated (saturated 19, none 1) | 4.57 [3.59, 7.72] | 4.39 [3.52, 7.54] | 2.69 [1.81, 5.96] | 0.70 [0.63, 0.84] | 53.41 [52.06, 56.09] | 1.01 [0.59, 1.32] | 0.03 [0.02, 0.05] |
| RBT-112 | HZ (10) | conventional | to 300 [0,300) | saturated | saturated | 3.81 [3.01, 4.39] | 3.31 [2.39, 3.89] | 1.43 [0.62, 1.73] | 0.39 [0.36, 0.42] | 51.00 [49.52, 52.30] | 1.04 [0.90, 1.24] | 0.03 [0.03, 0.04] |
| RBT-112 | HZ (10) | conventional | window income [300,600) | saturated | saturated | 3.43 [2.52, 4.94] | 2.96 [2.14, 4.66] | 1.03 [0.35, 2.97] | 0.50 [0.48, 0.57] | 52.55 [51.03, 54.76] | 1.01 [0.81, 1.11] | 0.03 [0.03, 0.04] |
| RBT-112 | HZ (10) | holistic | to 300 [0,300) | saturated | saturated | 3.18 [2.67, 3.69] | 2.82 [2.33, 3.38] | 1.17 [0.55, 1.45] | 0.46 [0.38, 0.55] | 46.73 [43.49, 48.81] | 1.05 [0.88, 1.23] | 0.04 [0.03, 0.04] |
| RBT-112 | HZ (10) | holistic | window income [300,600) | saturated | saturated | 3.57 [3.00, 4.05] | 3.29 [2.71, 3.91] | 1.50 [0.69, 1.99] | 0.62 [0.51, 0.70] | 51.67 [50.45, 53.13] | 1.06 [0.92, 1.27] | 0.03 [0.03, 0.04] |

## Rerun

```
python3 -m pytest tests/test_regime.py
python3 scripts/regime.py runs/RBT-19/P-801 --windows 0-99,100-299,300-499,500-599
bash <scratch>/fetch_ck.sh                       # restore: see the header of runs/RBT-126/corpus.py
python3 runs/RBT-126/verify_restore.py CK_DIR    # -> verify_restore.txt
python3 runs/RBT-126/verify_energy.py CK_DIR     # -> verify_energy.txt
python3 runs/RBT-126/corpus.py CK_DIR            # -> regime/RBT-<n>.txt, regime/corpus.json (untracked)
python3 runs/RBT-126/build_regime_md.py          # -> regime/TABLES.md
python3 runs/RBT-126/build_regime_md.py headline # -> regime/HEADLINE.md (the table above)
python3 runs/RBT-126/calibrate.py                # -> calibration.txt
```

`fetch_ck.sh` is committed as `runs/RBT-126/fetch_ck.sh`. It fetches each `ckpt/rbt-<n>-*` branch at depth 1 and
extracts the four files into `CK_DIR/rbt-<n>-<arm>/<arm>/`.

---
_Generated by [Claude Code](https://claude.ai/code)_
