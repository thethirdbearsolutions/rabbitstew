# RBT-118 step 1: what the committed ecology runs say about the two faunas — EXPLORATORY

> **EXPLORATORY. Descriptive only. Nothing here is scored, tested or registered.** It answers RBT-118's instruction
> that "the designer should first establish what the committed runs already say about fauna shares, before any new
> arm". Every number re-derives from committed files: the season tables under `runs/`, plus 47 checkpoint restores
> (`ckpt/*` branches) for the body levers. Neither `rabbitstew/` nor any scored file was changed. No rank
> correlation below is a test. There are many of them, over 10–30 points, and none was named in advance.

## 0. The headline: no committed run has both faunas in one world

**No committed run puts the two faunas in one world.** The only way the ecology can make them share food and space
is `merge_after`, which pools them into one arena under one capacity (`rabbitstew/ecology.py` module docstring and
`slots()`). `merge_after` is `null` in **all 284 committed `config.json` files** (`survey.py`, `survey.txt`). The
programme's own documents say the same:

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
  - which earns more per season (the season table's `mean_lifetime_score`, the energy the world pays net of
    work, which the economy runs on);
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
| **default**: 12 items, uniform, random terrain, 4 per arena, work 0.03/kJ, living cost 0.25 | RBT-90 (10 seeds), RBT-107 fresh base (20 seeds), RBT-71 (3 seeds, older generator), RBT-105 replicate holistic histories (17) | random, both faunas |
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
economy.

| | holistic | designed |
|---|---|---|
| fauna extinct | **1 / 30** (seed 29, season 27) | **0 / 30** |
| fewest alive, seasons 0–59 | median **23** of 60 (range 0–35), at season 11 (range 11–27) | median **60** (range 59–60) |
| income, seasons 0–59 (H − D) | holistic lower on **20 / 30**; median −0.091 | |
| income, last 100 seasons (H − D) | holistic higher on **27 / 29** surviving; median **+0.180** | |
| HOLD: first season from which the 60-season trailing H − D stays > 0 to the end | found on 27 / 29; median **268**, IQR 64–747, range **24–1198** | |

Four points:

- **The holistic founding bottleneck is the economy's arithmetic.**
  - Founders start with 3.0 energy against a 0.25 living cost, so they have 12 seasons of runway.
  - Random holistic bodies mostly cannot feed. RBT-113's founders eat 0.111 against the designed founders' 0.840
    (`runs/RBT-113/readout-adversary/ADVERSARY.md` §4). Here the season-0 holistic food is 0.06 against 0.69
    (`relate.txt` §1).
  - So most holistic founders starve together at season 11, the first season their runway runs out.
  - The fauna then refills to capacity within one lifespan on 29 of 30 seeds.
  - The designed body can move from its first season, and never dips.
- **Seed 29 is this bottleneck failing.** No holistic founder bred before the runway ran out.
  - It is the only holistic extinction among the 30 default-world histories, and among RBT-105's 17 replicate
    histories.
  - It is repeated in RBT-107's shift-29 and cull20-29 only because those arms fork from base-29 at season 360,
    after the extinction (`pool.txt` §B marks both "before the onset").
- **In income, the pattern is "behind early, ahead late".** That is the 2005 proposal's two-phase shape. But the
  phase boundary is not sharp: HOLD spans 24 to 1198 seasons, and on 2 histories the lead never holds.
  - A registration that reads "late" at one fixed depth will classify seeds differently depending on that depth.
  - HOLD is censored by run length: RBT-90's runs end at 599, so none of its HOLDs can be later.
  - On RBT-107's nineteen 1200-season surviving histories alone, HOLD is ≤ 300 on 7, 301–600 on 4, and > 600 on 8
    (665–1198).
  - A late HOLD does not mean the holistic fauna trailed until then. On the eight histories with HOLD > 600, the
    60-season trailing difference was above 0 on **81–98%** of seasons from 60 on (`pool.txt`, column `pos>=60`).
    The lead is usual, but it dips below 0 again until late.
  - The two histories without a HOLD are RBT-90 seeds 801 and 806. Their trailing difference was positive on 62%
    and 50% of seasons.
- **RBT-105's replicate holistic histories (§A′) vary about as much as seeds do** (HOLD 24–588 on the same founders).
  So much of the spread is the holistic fauna's own history, not its founders.

## 3. Across worlds

Sources: `phases.txt`, per arm and window; `pool.txt` §B, every extinction.

| world (from the onset unless stated) | extinctions after the onset | last 100 seasons, H − D income (median; holistic higher on) |
|---|---|---|
| default, random founders (§2) | holistic 1/30 (before any onset) | +0.18; 27/29 |
| default, designed founders planted (RBT-104 S1 / S8, RBT-106 HU, RBT-112 HZ) | none | +0.14 / +0.07 / +0.14 / +0.08; 10/10, 9/10, 9/10, 7/10 |
| **flat terrain** (RBT-101 shift; RBT-107 shift) | none | **−0.37; 2/10** and **−0.33; 4/19** |
| **dearer work, 0.08/kJ** (RBT-99 shift) | **designed 3/10**, 67–106 seasons after the onset | +0.39; 7/7 with the designed fauna alive |
| **scarce food, 6 items** (RBT-100 shift) | **designed 5/10**, 78–146 seasons after the onset | +0.23; 7/7 with designed rows in the window (5 survivors plus 2 dying within it) |
| 8 per arena (RBT-92 shift) | none | +0.22; 9/10 |
| random cull nulls (RBT-92, 99, 100, 101, 107) | only RBT-99 cull seeds 1, 3, 806, where the null's k for the designed fauna (63, 69, 78) was ≥ its 60 alive: **imposed by the cull, not the ecology** | +0.16 to +0.27 |
| **patchy**, designed founders planted with a paying compass (RBT-106 HP) | none | **−0.97; 0/10** |
| patchy, designed founders planted (RBT-106 P1) | none | +0.17; 8/10 |
| **scarce food from founding**, 60 seasons (RBT-100 founders6) | holistic 6/10, designed 5/10 | (see below) |

What the table shows:

- **Which fauna holds its own world depends on the world.** The designed body's income falls below the holistic
  fauna's in the two stress worlds.
  - It is the **only fauna to starve out after a change of world**: 8 of 20 seeds, 67–146 seasons after the onset.
  - The holistic fauna never does.
  - This is paper 9's C2/C3 territory (`docs/paper-9-net-of-arithmetic.md` rows C2, C3). There, the effect is
    arithmetic on the designed body's pre-onset work bill: at 0.08/kJ the unchanged designed fauna "earns less than
    nothing". It is not a difference in how the bodies respond.
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

LEVERS_PLACEHOLDER

## 5. Caveats that bind any reading of §§2–4

- **Separate ecologies (§0).**
  - "Holds the world" here means survives in its own. Income is compared across two populations that never meet.
  - In a merged arena the faunas would share arenas, groups and food items. No committed datum says anything about
    that interference.
  - Nor does any datum speak to the merge's own coupling: after the merge, groupings and breeding order are drawn
    from the holistic stream (`ecology.py` docstring).
- **The income lead is the work-cost coefficient's** (paper 5's abstract: "the cheapness of the evolved gait is a
  property of the work-cost coefficient rather than of the bodies"; §4 here). Any claim that holistic evolution
  "wins late" in this world has to survive a work-cost sweep, and C2 shows the direction it moves.
- **The motor-capacity allowance** (`runs/RBT-113/readout-adversary/ADVERSARY.md` §3). The mass budget caps mass,
  not gear, and only a holistic body can grow gear through ball joints keyed to the heavier part.
  - In these ecology histories the holistic Σgear stays **below** the designed body's (§4). So the allowance is not
    visibly in use here.
  - That is not a guarantee for a world or selection that pays for work (RBT-113's D line found it at every seed).
- **Mass.** The follow-up paper's first artefact (`docs/followup-paper.md` §4.1) was a weight-class mismatch. Here
  every holistic body is scaled to the 15.34 kg budget by season 59 (§4), so mass cannot vary. Σgear and
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
   - share of the pooled capacity;
   - income;
   - **food eaten, work, path**. These are already in `lineage.jsonl`; they need summarising into `seasons.txt`,
     because §4 shows the income difference is a work difference.
3. **Per arena group: its fauna composition and each member's food.** This is the interference measure no committed
   run has: whether a fauna eats less in mixed groups than in pure ones. `cohorts.jsonl` names the members; a
   committed table must carry it.
4. **Registered read points:**
   - the season at which "late" is read, fixed before the data;
   - since HOLD spans 24–1198 (§2), more than one read point, or a rule for the trajectory;
   - fixation defined as one fauna at 0 alive, with a censoring season.
5. **Body levers per season for the holistic fauna:** mass, Σgear, Σgear/(4 × mass), ball-joint share, from genomes
   at birth, as `bodysig.txt` is written now. Also a replay coverage measure on a fixed sample. This lets RBT-113's
   motor-capacity allowance be checked in the merged world, not assumed absent.
6. **At least two worlds, or a work-cost arm.** §3 shows that which fauna survives or leads flips with terrain,
   work cost and food.
7. **Founders.**
   - Random for both faunas. Planted founders make it a comparison of controllers.
   - Or, for the option-1/option-3 question, champions from these histories, stated as such.

## Files

| file | what |
|---|---|
| `survey.py` → `survey.txt`, `runs.tsv`, `alive-series.tsv` | every committed season table: world, dedup, per-fauna alive/extinction/income; the alive series of the distinct tables |
| `phases.py` → `phases.txt` | per arm group, alive and income by fixed window |
| `pool.py` → `pool.txt` | §A the 30 independent default-world histories; §A′ RBT-105 replicates; §B every extinction |
| `levers.py` → `levers.tsv`, `levers.txt` | ckpt restores; mass, Σgear, gear/4m, ball share, food, work, path per snapshot and fauna |
| `relate.py` → `relate.txt` | levers beside success; rank correlations (descriptive) |

`runs.tsv`, `alive-series.tsv` and `levers.tsv` are tables that back claims here. `.gitignore` admits only `*.txt`,
`*.md`, `*.py`, `*.sh` and `config.json` under `runs/` (`runs/README.md`), so these three are force-added.

Reproduce:

```
python runs/RBT-118/prior/survey.py > runs/RBT-118/prior/survey.txt
python runs/RBT-118/prior/phases.py > runs/RBT-118/prior/phases.txt
python runs/RBT-118/prior/pool.py > runs/RBT-118/prior/pool.txt
RBT118_SCRATCH=/some/tmp python runs/RBT-118/prior/levers.py > runs/RBT-118/prior/levers.txt
python runs/RBT-118/prior/relate.py > runs/RBT-118/prior/relate.txt
```

`levers.py` fetches 47 `ckpt/*` branches (about 6 MB each) and deletes each restore after use. It takes about 25
minutes on 4 cores.
