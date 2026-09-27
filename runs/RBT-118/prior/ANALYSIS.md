# RBT-118 step 1: what the committed ecology runs say about the two faunas — EXPLORATORY

> **EXPLORATORY. Descriptive only. Nothing here is scored, tested or registered.** It answers RBT-118's instruction
> that "the designer should first establish what the committed runs already say about fauna shares, before any new
> arm". Every number re-derives from committed files: the season tables under `runs/`, plus 46 checkpoint restores
> (`ckpt/*` branches) for the body levers. Neither `rabbitstew/` nor any scored file was changed. No rank
> correlation below is a test. There are many of them, over 10–30 points, and none was named in advance.
>
> **Revised after the step-1 adversary** (PR #402, `runs/RBT-118/prior-adversary/ADVERSARY.md`, CONFIRMED-WITH-CAVEATS),
> under the coordinator's ruling. All six MUST-FIX items and all five SHOULD items are taken, with the adversary's
> wording. Every number the revision cites is printed by this directory's own scripts (`pool.txt`, `relate.txt`,
> `survey.txt`, `terrain.txt`). §4a adds the terrain check (auditor D's H56).

## 0. The headline: no committed run has both faunas in one world

**No committed run puts the two faunas in one world.** The only way the ecology can make them share food and space
is `merge_after`, which pools them into one arena under one capacity (`rabbitstew/ecology.py` module docstring and
`slots()`). No committed ecology config sets it: of all **308 committed ecology configs**, 284 carry
`merge_after: null` and 24 predate the key (`survey.txt`). The programme's own documents say the same:

- `docs/foraging-world.md:294`: "The machinery is now in place, and nothing has been run on it (RBT-3)";
- `docs/held-out-challenges.md:378`: "Never the merged arena".

In every committed run, each fauna lives in its **own** ecology:

- its own capacity (60);
- its own bank of arenas: before a merge, each cohort is `(kind,)` with its own `arenas[key]`
  (`ecology.py:230, 260–267, 495–497`);
- its own births and deaths.

The two faunas share only the seed, the terrain and start stream, and the rules of the economy. So:

- **No fauna share of one world, no competitive exclusion and no time to fixation can be read from the committed
  data.** RBT-118's ticket says "the ecology already runs both faunas in one world: in RBT-107, seed 29's co-evolved
  fauna went extinct and the designed fauna lived alone from season 27". That is not what happened.
  - Seed 29's holistic fauna starved out of **its own** ecology at season 27. The designed fauna was never in it.
  - The designed fauna's own ecology stayed at 60 of 60 for all 1200 seasons (`runs/RBT-107/fresh/base-29/seasons.txt`).
  - The two were side by side, never in contact.
- What the data *can* describe is **side-by-side survival and income under matched seeds and worlds**:
  - which fauna goes extinct in its own ecology, and when;
  - which earns more **on random terrain**, the only terrain of the default world (§4a shows the lead reverses on
    flat ground): **"income"** throughout is the season table's `mean_lifetime_score`. That is the mean over
    the living members of their lifetime-average gain (food − 0.03 × kJ), before the living cost. It is
    survivor-weighted and lagged, not a per-season flow. Across the season-11 die-off the holistic value jumps from a
    median 0.123 at season 10 to 0.360 at season 13, rising on 29/29 surviving histories (`pool.txt`), with no
    change in the bodies;
  - how both depend on the world and on the body-model levers.

  That is what follows. Read every "H − D" below as *two separate populations compared*, not as a contest.

## 1. What is committed

`survey.py` reads all **322** committed `seasons.txt` tables and writes `runs.tsv`, one row per table, with world, protocol and per-fauna alive and income summaries.

- **78 tables are byte copies of others, or line-for-line prefixes of them.** These are RBT-99's arms re-read by
  RBT-100/101, RBT-106's HU re-read by RBT-112, and H-REP's cuts of RBT-107's fresh arms.
- **244 tables are distinct.**
- Grouped by world (`phases.txt` has every group):

| world | arms (distinct tables) | founders |
|---|---|---|
| **default**: 12 items, uniform, random terrain, 4 per arena, work 0.03/kJ, living cost 0.25 | RBT-90 (10 seeds), RBT-107 fresh base (20 seeds), RBT-71 (3 seeds, older generator), RBT-105 replicate holistic histories (16; its `forage-7-b0` is RBT-90's `forage-7`) | random, both faunas |
| default, **designed founders planted** | RBT-104 S1, S8; RBT-106 HU; RBT-112 HZ (10 each) | holistic random; designed = registered controllers |
| **patchy** (`food.patches` 3) | RBT-106 HP, P1 (10 each), side S8P (2 × 20 seasons) | as above, planted designed |
| **flat terrain** from the onset | RBT-101 shift (10), RBT-107 shift (20) | random |
| **dearer work** 0.08/kJ from the onset | RBT-99 shift (10) | random |
| **scarce food** 6 items from the onset | RBT-100 shift (10) | random |
| **scarce food from founding** (6 items, 60 seasons) | RBT-100 founders6 (10) | random |
| **8 per arena** from the onset | RBT-92 shift (10) | random |
| random **cull** nulls | RBT-92 cull/cull20, RBT-99/100/101 cull, RBT-107 cull20 | random |
| **no living cost** (neutral drift) | RBT-71 neutral (3) | random |

**The shift and cull arms of RBT-92/99/100/101 fork from RBT-90's histories at their onset. RBT-107's fork from its
base arms.** Their pre-onset seasons are those histories again, and are counted once (§2).

## 2. The default world: 30 independent histories

`pool.py` → `pool.txt` §A. The histories are RBT-90 forage (10 seeds) and RBT-107 fresh base (20 seeds). Both use
random founders for both faunas, run 600 and 1200 seasons respectively, and are otherwise identical in world and
economy. **All 30 run on random terrain.** Every income, work and lead figure in this section is on random terrain;
on flat ground the late lead reverses (§4a).

| | holistic | designed |
|---|---|---|
| fauna extinct | **1 / 30** (seed 29, season 27) | **0 / 30** |
| fewest alive, seasons 0–59, as booked (after same-season births) | median **23** of 60 (range 0–35), at season 11 (range 11–27) | median 60 (range 59–60) |
| fewest alive, seasons 0–59, **before same-season refill** (alive − births; H53) | median **20** (range 0–28) | median **50** (range 43–53) |
| income (lifetime mean over the living, §0), seasons **0–10**: the founders' runway | holistic lower on **30 / 30**; median −0.323 | |
| income, seasons **11–59** | holistic lower on 19 / 30 (a coin toss); median −0.034 | |
| income, seasons 0–59 (the first version's window, mixing the two above) | holistic lower on 20 / 30; median −0.091 | |
| **lead onset**: first season beginning 20 consecutive seasons of H − D > 0 | found on 29 / 29 surviving; median **40**, IQR **24–90**, range 16–214; before season 60 on 19 | |
| income, seasons **500–599** (the one depth all histories reach) | holistic higher on **26 / 29**; median **+0.195** | |
| income, last 100 seasons (depth 500 on RBT-90, 1100 on RBT-107; secondary) | holistic higher on 27 / 29; median +0.180 | |
| HOLD, a **last-dip** statistic: first season from which the 60-season trailing H − D stays > 0 to the end | found on 27 / 29; median 268, range 24–1198. It grows with run length and noise, and is not a phase boundary | |
| alive, births and deaths a season, 500–599 | 60 in every history; 1.53 each | 60 in every history; 1.72 each |

Four points:

- **The holistic founding bottleneck is the economy's arithmetic.**
  - Founders start with 3.0 energy against a 0.25 living cost, so they have 12 seasons of runway.
  - Random holistic bodies mostly cannot feed. RBT-113's founders eat 0.111 against the designed founders' 0.840
    (`runs/RBT-113/readout-adversary/ADVERSARY.md` §4). Here the season-0 holistic food is 0.06 against 0.69
    (`relate.txt` §1).
  - So most holistic founders starve together at season 11, the first season their runway runs out.
  - The fauna then refills to capacity within one lifespan on 29 of 30 seeds.
  - The designed body can move from its first season. Before same-season refill it dips to a median of 50 (range
    43–53), against the holistic fauna's 20 (range 0–28). Booked `alive` hides this because births refill freed
    slots in the same season (`ecology.py` steps 3–5; `pool.txt`, "BEFORE same-season refill";
    `runs/RBT-118/prior-adversary/probe_terrain.txt` §3, H53).
- **Seed 29 is this bottleneck failing.** No holistic founder bred before the runway ran out.
  - It is the only holistic extinction among the 30 default-world histories, and none of RBT-105's 16 replicate
    histories goes extinct.
  - It is repeated in RBT-107's shift-29 and cull20-29 only because those arms fork from base-29 at season 360,
    after the extinction (`pool.txt` §B marks both "before the onset").
- **The order of the income difference on random terrain, stated exactly (adversary MUST-1):** in the season
  table's lifetime-mean gain, the holistic fauna trails in the founders' runway (seasons 0–10, 30/30), is level in seasons 11–59 (19/30
  behind), and leads from about season 40 at the median. It leads on 25–28 of 29 histories at every fixed
  100-season depth from 100 to 599 (`pool.txt`, per fixed window). The order resembles the 2005 prediction, but it
  is **not** a test of it.
  - The faunas never compete.
  - The early deficit is random founders that cannot move, set against working bodies. Any fauna of random bodies
    against working bodies with random controllers would trail until selection had acted once. That needs no
    holistic mechanism.
  - The late lead is a work-price lead on random terrain (§4). It would reverse below a median 0.018/kJ, and it
    reverses on flat ground at the current price (§4a).
- **HOLD is a last-dip statistic, not the phase boundary (MUST-2).** The lead starts at the onset: median 40,
  IQR 24–90.
  - A registration's "late" read point should be justified from the onset.
  - The spread of HOLD (24–1198) is reported as a measure of how noisy the lead is.
  - HOLD is censored by run length: RBT-90's runs end at 599, so none of its HOLDs can be later.
  - On RBT-107's nineteen 1200-season surviving histories alone, HOLD is ≤ 300 on 7, 301–600 on 4, and > 600 on 8
    (665–1198).
  - A late HOLD does not mean the holistic fauna trailed until then. On the eight histories with HOLD > 600, the
    60-season trailing difference was above 0 on **81–98%** of seasons from 60 on (`pool.txt`, column `pos>=60`).
    The lead is usual, but it dips below 0 again until late.
  - The two histories without a HOLD are RBT-90 seeds 801 and 806. Their trailing difference was positive on 62%
    and 50% of seasons.
- **RBT-105's 16 replicate holistic histories (§A′) vary about as much as seeds do** (HOLD 24–588 on the same
  founders). So much of the spread is the holistic fauna's own history, not its founders.
- **An income lead is not a fitness lead here (SHOULD-1; random terrain).**
  - In seasons 500–599 both faunas sit at 60 of 60 in every history. Births equal deaths: 1.53 a season holistic,
    1.72 designed.
  - The only demographic trace of the lead is fewer deaths a season for the holistic fauna, on 23/29 (`pool.txt`).
    That is starvation above the age-out rate.
  - Under the committed breeding rule, an income edge above the birth threshold is close to neutral for offspring
    (the adversary's auditor C, finding 1). So the prior for a merged arena is near-neutral shares, with the lead
    acting mainly through starvation deaths.

## 3. Across worlds

Sources: `phases.txt`, per arm and window; `pool.txt` §B, every extinction.

| world (from the onset unless stated) | extinctions after the onset | last 100 seasons, H − D income (median; holistic higher on) |
|---|---|---|
| default, random founders, **random terrain** (§2) | holistic 1/30 (before any onset) | +0.18; 27/29 (500–599: +0.195; 26/29), **on random terrain** |
| default, designed founders planted (RBT-104 S1 / S8, RBT-106 HU, RBT-112 HZ) | none | +0.14 / +0.07 / +0.14 / +0.08; 10/10, 9/10, 9/10, 7/10 |
| **flat terrain** (RBT-101 shift; RBT-107 shift) | none | **−0.37; 2/10** and **−0.33; 4/19** |
| **dearer work, 0.08/kJ** (RBT-99 shift) | **designed 3/10**, 67–106 seasons after the onset; holistic never below 60 | +0.39; 7/7 with the designed fauna alive |
| **scarce food, 6 items** (RBT-100 shift) | **designed 5/10**, 78–146 seasons after the onset; holistic never below 60 | +0.23; 7/7 with designed rows in the window (5 survivors plus 2 dying within it) |
| 8 per arena (RBT-92 shift) | none | +0.22; 9/10 |
| random cull nulls (RBT-92, 99, 100, 101, 107) | only RBT-99 cull seeds 1, 3, 806, where the null's k for the designed fauna (63, 69, 78) was ≥ its 60 alive: **imposed by the cull, not the ecology** | +0.16 to +0.27 |
| **patchy**, designed founders planted with a paying compass (RBT-106 HP) | none | **−0.97; 0/10** |
| patchy, designed founders planted (RBT-106 P1) | none | +0.17; 8/10 |
| **scarce food from founding**, 60 seasons (RBT-100 founders6) | holistic 6/10, designed 5/10 | (see below) |

What the table shows:

- **Which fauna holds its own world depends on the world.** The designed body's income falls below the holistic
  fauna's in the two stress worlds.
  - It is the **only fauna to starve out after a change of world**: **8 of 20 arms, on 7 of the 10 RBT-90 base
    histories** (MUST-4). The two worlds fork from the same histories, and seed 806 dies in both. The extinctions
    come 67–146 seasons after the onset.
  - The holistic fauna never falls below 60 after the onset, on 20/20 arms (`terrain.txt` §4).
  - Both worlds push the designed fauna's unchanged work bill below the living cost. The extinctions are therefore
    starvation that the change of world makes arithmetically likely, not a difference in how the bodies respond.
    This is paper 9's C2/C3 reading (`docs/paper-9-net-of-arithmetic.md` rows C2, C3): at 0.08/kJ the unchanged
    designed fauna "earns less than nothing".
  - Survival is censored at season 599.
- **On flat ground the designed body leads**, as a wheeled body should.
- **In the patchy world, the lead goes to whichever fauna carries the compass.**
  - Where the designed founders carry RBT-106's planted compass (HP), the designed fauna leads on every seed.
  - Where they carry RBT-104's S1 controller (P1), the holistic fauna leads on 8 of 10.
  - With planted founders, this is not a body comparison at all.
- **Scarce food from founding is the one regime where the faunas' survival is open.** RBT-100 founders6 runs 60
  seasons at 6 items:
  - holistic alone survives on 3 seeds (1, 4, 804);
  - designed alone on 4 (2, 3, 806, 807);
  - both on 1 (7);
  - neither on 2 (801, 805).
  - Survivors are few (8–60 holistic, 2–7 designed at season 59).
  - Holistic extinction comes at seasons 16–54 and designed at 26–43, **both within one lifespan**. This is the
    same founding-runway effect as §2, in a world too poor for most founders of either kind.

## 4. Body-model levers

`levers.py` → `levers.tsv`, `levers.txt`, and `relate.py` → `relate.txt`. Each history is restored from its
checkpoint (MANIFEST consistent; restored `config.json` equal to the committed one on every run). Each living
genome is built at seasons 0, 59, 299, 599 and the last, with RBT-113 readout adversary's `probe_gear.py` measure.
Food, work and path come from the lineage's per-season log, over the 20 seasons ending at the snapshot.

Levers were measured on 46 histories: RBT-90's 10, RBT-107 base's 20, and RBT-105's 16 replicates. All 46
restored with 0 build errors. All ran on **random terrain**. Means over histories of each fauna's living population
(`relate.txt` §1):

| season | fauna | mass (kg) | Σgear | Σgear / (4 × mass) | ball-joint share | food (items) | work (J) | path (m) | net = food − 0.03 × kJ |
|---|---|---|---|---|---|---|---|---|---|
| 0 (founders) | holistic | 15.12 | 22.4 | 0.37 | 0.65 | 0.07 | 1 036 | 0.20 | 0.04 |
| 0 | designed | 15.34 | 108.0 | 1.76 | 0 | 0.69 | 19 413 | 3.08 | 0.11 |
| 59 | holistic | 15.32 | 55.0 | 0.90 | 0.94 | 0.99 | 4 770 | 1.81 | 0.84 |
| 59 | designed | 15.34 | 108.0 | 1.76 | 0 | 1.24 | 17 180 | 2.22 | 0.73 |
| 599 | holistic | 15.33 | 62.3 | 1.02 | 0.94 | 1.24 | 5 276 | 2.25 | 1.09 |
| 599 | designed | 15.34 | 108.0 | 1.76 | 0 | 1.46 | 19 691 | 1.89 | 0.87 |
| last | holistic | 15.33 | 62.9 | 1.03 | 0.94 | 1.27 | 5 181 | 2.26 | 1.11 |
| last | designed | 15.34 | 108.0 | 1.76 | 0 | 1.47 | 19 800 | 1.84 | 0.88 |

What it describes:

- **On random terrain, the late holistic lead is a work lead (+0.42) larger than a food deficit (−0.19) that clutter
  keeps small; on flat ground the food deficit is about −0.7 and the lead is gone (§4a).**
  - At the last season, the holistic fauna eats **less** than the designed one on **25 of 29** histories (median
    −0.19 items).
  - It spends less work on **29 of 29** (median −13.9 kJ, about a quarter of the designed body's).
  - It nets more on 27 of 29.
  - Across histories, the late H − D income tracks the food gap (ρ +0.75) more than the work gap (ρ +0.17). The work
    gap is always large, and the food gap decides by how much.
  - The median H − D net splits into a food term of **−0.187** and a work term (0.03 × kJ saved) of **+0.416**
    items a season. The work term is about 1.7 × the living cost.
  - **Break-even price on random terrain (SHOULD-2):** with the same food and work, the designed fauna would net more below a median
    **0.018/kJ** (range 0.001–0.033; defined on 25/29, the rest eat at least as much). At half the current price
    (0.015/kJ) the holistic fauna would net more on only **14/29** (`relate.txt` §4).
  - This is paper 5's "cheapness of the evolved gait … a property of the work-cost coefficient", given a number a
    registration can sweep around.
  - What "work" means for a holistic body is itself open. The adversary's auditor A (A2) finds much of the
    holistic founders' work is free spin on embedded joints. That raises the holistic bill, so it does not
    manufacture the lead, but it bears on its meaning.
- **The holistic fauna uses the motor-capacity channel, but not beyond the designed body's level (MUST-3).**
  - Σgear/(4 × mass) rose from a founder median of 0.38 to a median of **0.96** (range **0.24–2.05**) on **44/45**
    histories, almost all of it onto ball joints (ball-joint share 0.65 → 0.94). That is RBT-113's channel in use:
    gear keyed to the heavier part, per ball-joint DOF.
  - At the last snapshot it is within 0.8–1.2 on 19/45 and above 1.2 on 13/45. It reaches the designed body's 1.76
    on 1/45 (RBT-107 seed 28, 2.05) (`relate.txt` §1).
  - RBT-113's D line reached 3.66 under selection for work. The ecology charges for work, and gear stays below the
    designed body's level. In a contest that pays for force (a shoving bout), that would not be expected to hold.
- **Mass is pinned.** Every holistic body is scaled to the 15.34 kg budget from season 59 on (15.32–15.34 mean). Any
  rank correlation with mass after season 0 is over a spread of a few grams, and is not read.
- **Coverage (path) is not where the lead is.** The holistic fauna moves further per season than the designed fauna
  late (2.26 m against 1.84 m; holistic longer on 19 of 29), but path's rank correlation with late H − D income is
  −0.04. RBT-113 found the holistic U line's food gain was coverage, not smell. Here, coverage is present but not
  what separates histories.
- **Rank correlations over the 30 independent histories** (`relate.txt` §3; descriptive only, many comparisons):
  - Founder levers relate to the founding bottleneck. Founders that already move and spend (Σgear ρ +0.47, path
    +0.59, food +0.57, work +0.52) leave more holistic survivors in seasons 0–59.
  - They say almost nothing about late success (|ρ| ≤ 0.37 with late H − D).
  - Season-59 food and net income go with early success (ρ +0.83, +0.88), which is partly the same quantity
    measured twice.
  - No lever at 59 or later ranks the late income or the HOLD season beyond |ρ| 0.58. The largest are last-season
    net +0.58 and food +0.54, again partly the same quantity.
  - Nothing here identifies a body-model lever that predicts which histories the holistic fauna leads, beyond its
    own income.

## 4a. Terrain: does the random terrain explain the lead? (auditor D's H56)

`terrain.py` → `terrain.txt`; the flat-terrain restores are in `levers-flat.tsv`/`.txt`. RBT-107's 20 shift arms
were restored with 0 build errors and configs equal to the committed ones.

**All 30 default histories run on random terrain** (`terrain.txt` §1). The committed data hold a paired test bed.
RBT-107's shift arms (onset 360) and RBT-101's (onsets 352–382) fork from those same histories and switch to flat
ground: same seed, same founders, same streams.

| paired window | H − D, base (holistic ahead) | H − D, flat (holistic ahead) | designed change, flat − base | holistic change | flat below base |
|---|---|---|---|---|---|
| RBT-107, onset+140..+239 (n = 19) | +0.217 (18/19) | **−0.391 (1/19)** | +0.642 (up on 19/19) | +0.098 (up on 13) | 19/19 |
| RBT-107, 1100–1199 (n = 19) | +0.231 (19/19) | **−0.332 (4/19)** | +0.703 (up on 19/19) | +0.104 (up on 14) | 18/19 |
| RBT-101, onset+140..+239 (n = 10) | +0.122 (8/10) | **−0.358 (2/10)** | +0.625 (up on 10/10) | +0.115 (up on 10) | 9/10 |

The reversal is immediate: in the first 100 seasons after the onset the holistic fauna leads on only 2/19
(`phases.txt`, RBT-107 shift).

**Reconciling with the adversary's pairing** (PR #402 addendum): it pairs the last 100 seasons of all 29 flat arms
(RBT-107 at 1100–1199 and RBT-101 at 500–599) and finds the holistic fauna ahead on 6/29. The table above uses
different windows: onset + 140..+239, plus RBT-107's 1100–1199. Its 1100–1199 row is the same window (4/19). RBT-101's row runs from onset + 140 (seasons 492–522) to 599, close
to 500–599 (2/10). The two also sum to 6/29. Both pairings show the reversal.

**Where the terrain acts** (medians over RBT-107's restores; base → flat, living population, 20-season window):

| season | fauna | food (items) | work (kJ) | path (m) | net |
|---|---|---|---|---|---|
| 599 | holistic | 1.25 → 1.39 | 5.18 → 5.53 | 2.29 → 2.44 | 1.11 → 1.21 |
| 599 | designed | **1.49 → 2.15** | 19.84 → 20.03 | **1.92 → 2.73** | 0.90 → 1.56 |
| 1199 | holistic | 1.36 → 1.47 | 4.86 → 4.83 | 2.44 → 2.33 | 1.16 → 1.28 |
| 1199 | designed | **1.56 → 2.21** | 20.71 → 20.55 | 1.79 → 2.24 | 0.93 → 1.64 |

- **H56 is supported descriptively.** The default world's holistic income lead depends on the random terrain. On
  flat ground the designed fauna leads on 15–18 of 19 paired RBT-107 seeds (8 of 10 on RBT-101) at the same work price.
- **The terrain taxes the designed body's food, not its work.** On flat ground its work bill is unchanged (about
  20 kJ), while it travels further and eats about 0.65 items a season more. The holistic fauna gains about 0.1.
- **The break-even price moves.** On flat ground it is a median **0.053/kJ** at season 599 (0.057 at 1199), against
  0.018 on random terrain (§4). So at the current 0.03/kJ the designed fauna nets more on 17/19 (16/19 at 1199).
- **What that makes of §2 and §4.** The late holistic lead is conditional on two settings of the world, not only
  one: the work price (it reverses below about 0.018/kJ) and the random terrain (it reverses on flat ground at
  0.03/kJ).
  - In the §4 split, the terrain is what keeps the food term small (−0.19): on flat ground the food deficit is
    about −0.7 (difference of the fauna medians above) and swamps the work saving.
  - Neither setting was designed against either body. Random terrain is the follow-up paper's chosen fair
    ground, and 0.03/kJ is paper 5's.
  - The registration still has to choose them, and should sweep both (§6).
- Limits: one onset and one magnitude per ticket; both faunas keep evolving after the onset; RBT-101's paired window
  is cut at season 599. The flat-terrain lever table covers RBT-107 only (RBT-101 has no restore here).

## 5. Caveats that bind any reading of §§2–4

- **Separate ecologies (§0).**
  - "Holds the world" here means survives in its own. Income is compared across two populations that never meet.
  - In a merged arena the faunas would share arenas, groups and food items. No committed datum says anything about
    that interference.
  - Nor does any datum speak to the merge's own coupling: after the merge, groupings and breeding order are drawn
    from the holistic stream (`ecology.py` docstring).
- **An income lead is not a fitness lead** under the committed breeding rule (§2): both faunas sit at capacity, and
  an edge above the birth threshold is near-neutral for offspring.
- **The income lead also needs random terrain** (§4a): on flat ground the designed fauna leads.
- **The income lead is the work-cost coefficient's** (paper 5's abstract: "the cheapness of the evolved gait is a
  property of the work-cost coefficient rather than of the bodies"; §4 here). Any claim that holistic evolution
  "wins late" in this world has to survive a work-cost sweep, and C2 shows the direction it moves.
- **The motor-capacity allowance** (`runs/RBT-113/readout-adversary/ADVERSARY.md` §3). The mass budget caps mass,
  not gear, and only a holistic body can grow gear through ball joints keyed to the heavier part.
  - In these ecology histories the holistic fauna uses the channel (Σgear/(4 × mass) rose on 44/45), but not beyond
    the designed body's level (1/45 at or above 1.76; §4).
  - That is not a guarantee for a world or selection that pays for work (RBT-113's D line found it at every seed).
- **Mass.** The follow-up paper's first artefact (`docs/followup-paper.md` §4.1) was a weight-class mismatch. Here
  the holistic population's mean mass sits at the 15.34 kg budget from season 59 on (15.32–15.33 kg, §4), so mass barely
  varies. Σgear and
  Σgear/(4 × mass) therefore rank identically.
- **The spawn drop** (`docs/followup-paper.md` §4.2) is settled out by the protocol now in force, in every run read
  here. It is noted because an arena rematch (RBT-118 option 1) would reintroduce spawning.
- **Coverage.** The only committed coverage proxy is **path length** per season from `lineage.jsonl`. RBT-113's
  cells-covered measure (`probe_food.py`) needs replays and was not run.
- **Planted founders** (RBT-104, 106, 112) make those arms comparisons of particular controllers, not of body
  models.
- **Seeds are few per world** (10–30), and the stress worlds are one magnitude each.

## 6. What a registration would need to log (for RBT-118 option 2, one shared world)

The committed logs are nearly sufficient for a merged run. The season table already writes one row per fauna after
a merge (`docs/foraging-world.md:294`). What a registered head-to-head needs in addition, or fixed in advance:

1. **A merged arm at all:**
   - `--merge-after M` (M = 0 for a founding contest; M > 0 so that each fauna first passes its founding bottleneck,
     §2);
   - `--pooled-capacity` fixed, or its default of 120 stated.

   A matched **null** is needed too. For example, a merged run of one fauna against a relabelled copy of itself,
   or a random-label merge, to give the drift distribution of shares and fixation times under a pooled capacity.
   Without that, a share has no reference.
2. **Per season, per fauna, in the merged arena:**
   - alive, births, deaths split by starvation and old age;
   - the count of eligible breeders (energy ≥ the birth threshold) and median energy. Without these, a merged run's
     shares will read as drift whatever the bodies do (§2);
   - share of the pooled capacity;
   - income;
   - **food eaten, work, path**. These are already in `lineage.jsonl`; they need summarising into `seasons.txt`,
     because §4 shows the income difference is a work difference.
3. **Per arena group: its fauna composition and each member's food.** This is the interference measure no committed
   run has: whether a fauna eats less in mixed groups than in pure ones. `cohorts.jsonl` names the members; a
   committed table must carry it.
4. **Registered read points:**
   - the season at which "late" is read, fixed before the data and justified from the lead's onset (median 40,
     IQR 24–90, §2), not from HOLD, which is a last-dip statistic;
   - more than one read point, or a rule for the trajectory; report the last-dip spread as noise;
   - fixation defined as one fauna at 0 alive, with a censoring season.
5. **Body levers per season for the holistic fauna:** mass, Σgear, Σgear/(4 × mass), ball-joint share, from genomes
   at birth, as `bodysig.txt` is written now. Also a replay coverage measure on a fixed sample. This lets RBT-113's
   motor-capacity allowance be checked in the merged world, not assumed absent.
6. **At least two worlds, or a work-cost arm.** §3 shows that which fauna survives or leads flips with terrain,
   work cost and food.
7. **Founders.**
   - Random for both faunas. Planted founders make it a comparison of controllers.
   - Or, for the option-1/option-3 question, champions from these histories, stated as such.
8. **A `breed_order` arm, or a stated reason for none.** Under the committed breeding lottery an income edge is
   near-neutral (§2), so the rule that turns income into births decides what a share can show.
9. **A motors-off season, and the adversary's auditor A flags stated:** A2 (free-spin work on embedded joints), A3
   (settle drift) and A5 (eating geometry). A2 bears on what "work" means for a holistic body, and so on the
   work-price lead of §4.
10. **A work-price sweep bracketing the break-even** (median 0.018/kJ on random terrain, 0.053 on flat, §§4, 4a),
    and random and flat terrain both, since the lead reverses between them (§4a).

## Files

| file | what |
|---|---|
| `survey.py` → `survey.txt`, `runs.tsv`, `alive-series.tsv` | every committed season table: world, dedup, per-fauna alive/extinction/income; the alive series of the distinct tables |
| `phases.py` → `phases.txt` | per arm group, alive and income by fixed window |
| `pool.py` → `pool.txt` | §A the 30 independent default-world histories; §A′ RBT-105 replicates; §B every extinction |
| `levers.py` → `levers.tsv`, `levers.txt` | ckpt restores; mass, Σgear, gear/4m, ball share, food, work, path per snapshot and fauna |
| `relate.py` → `relate.txt` | levers beside success; rank correlations (descriptive); gear distribution; break-even price |
| `levers.py --flat` → `levers-flat.tsv`, `levers-flat.txt`; `terrain.py` → `terrain.txt` | §4a: RBT-107's flat-terrain arms restored, and the terrain check; also the stress arms' holistic minimum |

`runs.tsv`, `alive-series.tsv`, `levers.tsv` and `levers-flat.tsv` are tables that back claims here. `.gitignore` admits only `*.txt`,
`*.md`, `*.py`, `*.sh` and `config.json` under `runs/` (`runs/README.md`), so these four are force-added.

Reproduce:

```
python runs/RBT-118/prior/survey.py > runs/RBT-118/prior/survey.txt
python runs/RBT-118/prior/phases.py > runs/RBT-118/prior/phases.txt
python runs/RBT-118/prior/pool.py > runs/RBT-118/prior/pool.txt
RBT118_SCRATCH=/some/tmp python runs/RBT-118/prior/levers.py > runs/RBT-118/prior/levers.txt
python runs/RBT-118/prior/relate.py > runs/RBT-118/prior/relate.txt
RBT118_SCRATCH=/some/tmp python runs/RBT-118/prior/levers.py --flat > runs/RBT-118/prior/levers-flat.txt
python runs/RBT-118/prior/terrain.py > runs/RBT-118/prior/terrain.txt
```

`levers.py` fetches 46 `ckpt/*` branches (about 6 MB each) and deletes each restore after use. It takes about 25
minutes on 4 cores.
