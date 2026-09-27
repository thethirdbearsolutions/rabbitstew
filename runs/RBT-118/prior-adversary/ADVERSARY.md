# RBT-118 step 1, adversary: PR #399 (`runs/RBT-118/prior/ANALYSIS.md` at `d5e60a8`)

**Verdict: CONFIRMED-WITH-CAVEATS.** Every headline number re-derives, but three of the five claims are worded
more strongly than the data allow. Seven MUST-FIX items (§1) change wording, not numbers. None of them overturns the
analysis. Claim 2 changes the most: its "early" phase is the founders' 11-season runway, not an evolutionary phase.

**Addendum (§3, after RBT-121 auditor D, PR #401): the late holistic lead is a random-terrain lead.**
- All 30 histories ran on random terrain.
- The same histories forked onto flat ground reverse the lead on 21/29.
- Clutter costs the designed body about 0.7 items of *food* a season, and nothing in work.
- MUST-FIX 7 adds this. The verdict is unchanged.

This review is EXPLORATORY and descriptive like the PR. I changed nothing under `rabbitstew/` or `runs/RBT-118/prior/`.

| probe (this directory) | reads | checks |
|---|---|---|
| `probe_configs.py` → `.txt` | every committed `config.json` under `runs/` | claim 1 |
| `probe_income.py` → `.txt` | the 30 default-world `seasons.txt` | claim 2: metric, windows, fixed depths, demography |
| `probe_stress.py` → `.txt` | RBT-99, RBT-100 shift arms and RBT-90 | claim 3 |
| `probe_levers.py` → `.txt` | PR #399's `levers.tsv` | claims 4 and 5, and the break-even work price |
| `probe_terrain.py` → `.txt` | the 30 histories' configs; RBT-101 and RBT-107 flat forks against their bases | addendum: D's H56 (clutter) and H53 (refill) |
| `probe_flatwork.py` → `.txt` | 29 flat-fork `ckpt/*` lineages, beside `levers.tsv` | addendum: food and work by terrain |

The p-values below are two-sided sign tests. They describe the data and are not a registered test.

## Claim by claim

### Claim 1: no committed run has both faunas in one world. CONFIRMED, but the count is miscited

`probe_configs.txt`:

| config files under `runs/` | count |
|---|---|
| all `config.json` | 438 |
| with an ecology section | 308 |
| `merge_after` present and null | **284** |
| no `merge_after` key (older than the flag, so None by default) | 24 |
| `merge_after` set | **0** |

- The claim holds, and it holds more strongly than stated: none of the 308 ecology configs is merged.
- "284" is the number of configs that carry the key. It is not the number of committed `config.json` files.
- `survey.txt`, which ANALYSIS.md:13 cites for 284, never prints 284. It prints "runs with a config: 252", which
  counts season tables that have a config beside them.
- 70 season tables have no config: RBT-106 (10) and `RBT-107/hrep/tables` (60).
  - The H-REP tables are cuts of RBT-107 runs whose configs are committed.
  - RBT-106's registered arm table has no merge.

  So the headline stands.
- Seed 29 re-derives: `base-29`'s designed rows are 60 alive in all 1200 seasons.

### Claim 2: extinctions, the bottleneck and "behind early, ahead late". The numbers re-derive; the two-phase reading does not

Four numbers re-derive exactly from the committed tables:
- extinctions 1/30 against 0/30;
- fewest alive: median 23, at season 11;
- 20/30 behind in seasons 0–59;
- 27/29 ahead in the last 100 seasons.

`pool.py` is correct as written. Four points change what the numbers mean.

**(a) "Income" is a lagged, survivor-weighted stock, not a per-season flow.**
- `mean_lifetime_score` is the mean over the **living** of each member's **lifetime-average** gain
  (`ecology.py:572`).
- The gain is food × value − 0.03 × kJ (`simulation.py:527`), before the living cost.
- Mass death therefore raises it: across the season-11 die-off, the holistic value goes from a median 0.121 at
  season 10 to 0.355 at season 13, and it rises on **30/30** histories (`probe_income.txt` §6).
- ANALYSIS.md §0 calls it "the energy the world pays net of work". That is right about what goes in, but it should
  say "lifetime mean over the living".

**(b) The "early" phase is the founders' runway: seasons 0–10, and nothing after.** From `probe_income.txt` §2:

| window | holistic lower on | median H − D | sign p |
|---|---|---|---|
| 0–10 | **30/30** | −0.323 | 2e-9 |
| 11–59 | 19/30 | −0.034 | 0.20 |
| 12–59 | 18/30 | −0.029 | 0.36 |
| 30–59 | **8/29** (holistic *higher* on 21) | +0.058 | 0.02 |
| 0–59 (the PR's window) | 20/30 | −0.091 | 0.10 |

- The PR's 20/30 mixes an 11-season founder deficit that is certain with 49 seasons that are a coin toss or already
  in the holistic fauna's favour.
- The deficit is the initial condition: random holistic bodies mostly cannot move (founders eat 0.07 against 0.69;
  PR §4). The designed founders start with a working body.
- **The null is the obvious one.** Any fauna of random bodies set against a fauna of working bodies with random
  controllers trails until selection has acted once, and that needs no holistic mechanism. The PR's own first
  bullet under §2 says so ("the economy's arithmetic"). The headline then calls it the 2005 proposal's phase.

**(c) The lead is established early, not "somewhere in 24–1198".**
- HOLD is a *last-dip* statistic: the first season after which the trailing mean never again falls to 0 or
  below. It grows with run length and with noise.
- Measured instead as the first season that begins 20 consecutive seasons of H − D > 0, the lead starts by
  season **40** in the median (IQR 24–90). It starts within the first 60 seasons on 19 of 29 histories, and on
  29/30 in all (`probe_income.txt` §3).
- The PR notes that the trailing difference is positive on 81–98% of seasons, but it frames HOLD as "the phase
  boundary". For a registration, the boundary that matters is about season 40. The HOLD range measures how noisy
  the lead is.

**(d) The late lead is robust to window, depth and source. That part is solid** (`probe_income.txt` §4):

| fixed window | holistic higher on | median H − D |
|---|---|---|
| 100–199 | 25/29 | +0.107 |
| 200–299 | 27/29 | +0.148 |
| 300–399 | 27/29 | +0.148 |
| 400–499 | 28/29 | +0.156 |
| 500–599 | 26/29 | +0.195 |
| 1100–1199 (RBT-107 only) | 19/19 | +0.231 |

- The pattern holds within RBT-90 and within RBT-107 separately at every depth, except RBT-90's 300–399 and
  500–599, at 8/10 each.
- The PR's "last 100" mixes depth 500 (RBT-90) with depth 1100 (RBT-107). At one common depth, 500–599, it is
  26/29 rather than 27/29.
- **Independence:** the 30 histories have 30 distinct seeds. Their configs differ only in seed, length and
  `workers` (checked for RBT-90 forage-1 against RBT-107 base-11). RBT-107 does not overlap RBT-90. The overlaps
  are elsewhere:
  - RBT-105's `forage-7-b0` has columns 1–7 equal to RBT-90's `forage-7`, so it is RBT-90's history, not a
    replicate;
  - the fork arms share their base histories (claim 3).

**Survivor bias as a cause of the late lead: ruled out.**
- The founding cull is 500+ seasons (8+ lifespans) before the late window.
- The lever table shows the same lead in per-season lineage food and work over all living members (net +0.23; PR §4).
- If survivor weighting did anything, it would bias *against* the holistic fauna. Its low earners carry more
  energy and so linger longer (auditor C: median energy 23 against 12–17).

### Claim 3: only the designed fauna starves out in the dearer-work and scarce-food worlds, on 8/20. The numbers re-derive; the count needs restating

`probe_stress.txt`:
- **The 20 arms are 10 base histories used twice.** Every RBT-99 and RBT-100 shift arm has pre-onset seasons equal
  to RBT-90's (columns 1–7).
- The 8 extinctions fall on **7 of the 10** base histories. Seed 806 dies in both worlds.
- **These are starvations, not culls.** The shift arms have `cull: null`, and deaths follow the change of price or
  food. The one protocol-imposed case is RBT-99's cull null (k ≥ alive), which the PR labels correctly.
- **The protocol makes them near-certain.** Both worlds are changes to arithmetic.
  - At 0.08/kJ, the designed fauna's pre-change bill (about 19.7 kJ, from PR §4, season 599) costs 1.58 a season
    against about 1.46 food, so it is below zero before the 0.25 living cost.
  - With 6 items instead of 12, food of about 0.73 less 0.59 of work is 0.14, which is below 0.25.
  - The holistic fauna's bill (about 5.3 kJ) leaves it above the living cost in both worlds.

  The survivors are rescues. Designed fewest alive after the onset is 0–7 on 11 of 20 arms, and ≤ 38 on 15 of 20.
  The holistic fauna **never falls below 60**, on 20/20 arms. The PR's "C2/C3 arithmetic" sentence already says
  this, but the headline count should carry it.
- Extinction is censored at season 599, about 220–250 seasons after the onset.

### Claim 4: "the late holistic lead is a work lead, not a food lead". CONFIRMED arithmetically; its size and meaning need stating

**Recount** (`probe_levers.txt`, 29 surviving independent histories at the last snapshot):
- The holistic fauna eats less on 25/29 and works less on 29/29 (median H/D work ratio 0.27).
- It nets more on 27/29.
- The median H − D net splits into a food term of **−0.187** and a work term of **+0.416** items a season.

**Is 0.03/kJ material?**
- **In energy, yes.** The work term is about 1.7 × the living cost (0.25), or about a third of the designed
  fauna's food.
- **It depends on the price.** The static break-even price, below which the designed fauna would net more, is a
  median **0.018/kJ** (range 0.001–0.033, n = 25).
  - At half the current price, the same food and work would leave the holistic fauna ahead on only **14/29**:
    10 whose break-even is below 0.015, plus the 4 where it also eats more.
  - "Late holistic lead" therefore describes this price, as paper 5 already says.
  - Auditor C's finding 3 prices coverage-level work 16× below its break-even, so the designed body's
    wheel-driven 20 kJ is the one bill this price registers.

**What does an income lead mean for success here? Nothing demographic in these runs.**

`probe_income.txt` §5, seasons 500–599:

| | alive | births a season | deaths a season |
|---|---|---|---|
| holistic | 60.0 in every history | 1.55 | 1.55 |
| designed | 60.0 in every history | 1.67 | 1.67 |

- Both faunas are at capacity in **every** history.
- The only trace of the income lead is about 0.18 fewer deaths a season for the holistic fauna (fewer on 23/29).
  That is starvation above the age-out rate.
- Under the committed breeding rule (auditor C, finding 1), an income edge above the threshold is close to neutral
  for offspring. A ×1.25 edge takes a share from 0.10 to 0.11 in 400 seasons.
- So in a merged arena under `breed_order = shuffle`, the prior for the income lead is **near-neutral shares**. The
  lead would act mainly through the starvation-death channel.
- The PR's "Read every H − D as two populations compared, not a contest" is right. It should add: **an income lead
  is not a fitness lead under this breeding rule.**

**Auditor A's findings do not manufacture the work lead:**
- **Ghost limbs (A2)** add *free-spin work* to the holistic bill: 66% of founder work is on embedded joints. They
  therefore work against the holistic fauna's low bill.
- **Eating geometry (A5):** the holistic footprint (0.60–0.67 m²) is smaller than the Pioneer's (0.86 m²).
- **Settle drift (A3):** motors-off food is 0.03–0.13, against about 1.27 late.

What A does bear on is the *meaning* of the holistic work figure, which is partly spin inside the body. A merged
arm should state A2, A3 and A5's flags.

### Claim 5: "the motor-capacity allowance is not in use here". The measure is sound; the wording overclaims

**The restores are right** (`levers.txt`):
- 46/46 MANIFESTs are complete (600/600 or 1200/1200).
- The restored configs equal the committed ones.
- There were 0 build errors.
- `gear()` is RBT-113's `probe_gear` in effect: torque motors only, and the largest component of `actuator_gear`.
- Seasons sampled: 0, 59, 299, 599 and the last (599 or 1199).

**The recount:**
- Holistic Σgear/(4 × mass) at the last snapshot has a median of **0.96**, but a **range of 0.24–2.05**.
  - It is within 0.8–1.2 on only 19/45.
  - It is above 1.2 on 13/45.
  - It reaches 1.76 or more on 1/45 (base-28, 2.05).
- **It rose on 44/45** histories, from a founder median of 0.37 (×2.6), almost all of it onto ball-joint DOFs
  (0.65 → 0.94).
- That is **A1's channel in use**: gear keyed to the heavier mass, per ball-joint DOF. It is simply not used beyond
  the designed body's level.
- "About 1.0" is a mean over histories, not a typical history.

## §1 MUST-FIX (wording, with exact replacements)

1. **ANALYSIS.md:96** (and the RBT-118 post): replace *"In income, the pattern is 'behind early, ahead late'. That
   is the 2005 proposal's two-phase shape."* with:

   > In the season table's lifetime-mean gain, the holistic fauna trails in the founders' runway (seasons 0–10,
   > 30/30), is level in seasons 11–59 (19/30 behind), and leads from about season 40 at the median. It leads on
   > 25–28 of 29 histories at every fixed 100-season depth from 100 to 599. The order resembles the 2005
   > prediction, but it is **not** a test of it. The faunas never compete. The early deficit is random founders
   > that cannot move, against working bodies. The late lead is a work-price lead (§4) on **random terrain**. It
   > would reverse below a median 0.018/kJ, and it reverses on flat ground on 21/29 of the same histories (§3).

   In the headline table, add the 0–10 and 11–59 rows beside 0–59.
2. **HOLD** (ANALYSIS.md:96–103 and §6.4):
   - Call it a last-dip statistic.
   - Add the onset of the lead: the first run of 20 positive seasons, median 40, IQR 24–90.
   - Do not present 24–1198 as the "phase boundary". A registration's "late" read point should be justified from
     the onset, and the spread in last-dip should be reported as noise.
3. **ANALYSIS.md:182 and §5**: replace *"The motor-capacity allowance is not in use in these ecologies"* with:

   > The holistic fauna uses the motor-capacity channel, but not beyond the designed body's level. Σgear/(4 × mass)
   > rose from 0.37 to a median of 0.96 (range 0.24–2.05) on 44/45 histories, almost all of it onto ball joints.
   > It exceeds the designed body's 1.76 on 1/45.

   Drop "about 1.0" as a description of histories.
4. **Claim 3** (§3 table and the post): replace *"8 of 20 seeds"* with:

   > 8 of 20 arms, on 7 of the 10 RBT-90 base histories. The two worlds fork from the same histories, and seed 806
   > dies in both.

   Add:

   > The holistic fauna never falls below 60 after the onset. Both worlds push the designed fauna's unchanged work
   > bill below the living cost, so the extinctions are starvation that the change of world makes arithmetically
   > likely, not a difference in how the bodies respond. Survival is censored at season 599.
5. **Define income** where it is first used (§0 bullet, and the §2 table): *"mean over the living members of their
   lifetime-average gain (food − 0.03 × kJ), before the living cost; survivor-weighted and lagged."* Note that it
   jumps across the season-11 die-off (0.12 → 0.36, 30/30).
6. **ANALYSIS.md:13**: *"all 284 committed `config.json` files"* is not what `survey.txt` prints. Replace it with:

   > all 308 committed ecology configs: 284 carry `merge_after: null`, and 24 predate the key
   > (`probe_configs.txt`).

   Alternatively, have `survey.py` print the count it cites.
7. **Terrain** (§2, §4 and the post): every income, work and lead statement must say *"on random terrain"*. After
   the §3 table's "on flat ground the designed body leads", add:

   > In paired forks of the same 29 histories, flat ground takes the holistic lead from 27/29 to 6/29 (median
   > H − D +0.18 → −0.34). The designed fauna gains 0.69 items of food a season on 29/29, and its work does not
   > change (20.5 → 20.4 kJ). The late holistic lead is therefore conditional on the clutter tax that random
   > terrain levies on the wheeled body's food (RBT-121 D, H56). The work gap is terrain-independent.

   Also rewrite claim 4's headline:

   > On random terrain, the late holistic lead is a work lead (+0.42) larger than a food deficit (−0.19) that
   > clutter keeps small. On flat ground the food deficit is −0.81, and the lead is gone.

## §2 SHOULD

1. **"Income lead ≠ fitness lead."** Add to §4 and §5:
   - both faunas sit at 60/60 in every late history;
   - births are 1.55 against 1.67 a season;
   - under the committed breeding lottery (auditor C, finding 1), an income edge above the threshold is close to
     neutral.

   §6 should then require, per fauna and season: starvation deaths separated from age deaths, the count of
   eligible breeders (energy ≥ 3), and median energy. It should also require a `breed_order` arm or a stated
   reason for none. Otherwise a merged run's shares will read as drift whatever the bodies do.
2. **Claim 4's size:** give the break-even price (median 0.018/kJ, and the 14/29 at half price) next to "work lead".
   That turns paper 5's "property of the coefficient" into a number the rematch can register a sweep around.
3. **RBT-105:** the text says 17 replicates, but there are **16**. `forage-7-b0` is RBT-90's `forage-7`. Fix
   ANALYSIS.md:53 and :92. `levers.py` already says so.
4. **"Last 100 seasons"** mixes depths 500 and 1100. Report 500–599 for all 29 (26/29, +0.195) as the like-for-like
   row, with the last 100 as a secondary row.
5. **§6:** add a motors-off season and a statement of auditor A's A2, A3 and A5 flags to the registration's logging
   list. A2 bears on what "work" means for a holistic body.

## §3 Addendum: RBT-121 auditor D (PR #401, `59fd9b6`), H56 and H53

### H56, the clutter tax: CONFIRMED in these histories. The late lead is a random-terrain lead

**Terrain.** All 30 default-world histories ran on `terrain: random` (`probe_terrain.txt` §1).

**A paired test within each history** (`probe_terrain.txt` §2). RBT-101's shift arms (flat from seasons 352–382)
fork from RBT-90, and RBT-107's fresh shift arms (flat from season 360) fork from RBT-107's base arms. Each flat arm
is compared with its own base history over the last 100 seasons.

| 29 pairs, last 100 seasons | random (base) | flat (fork) |
|---|---|---|
| H − D, median | +0.180 | **−0.339** |
| holistic higher on | 27/29 | **6/29** |

- The designed fauna's income rises by a median **+0.68 on 29/29** pairs. The holistic fauna's rises by +0.10, on
  23/29.
- The lead reverses on **21/29**.

**What changes is the designed body's food, not its work** (`probe_flatwork.txt`). Lineage food and work come from
the 29 flat forks' `ckpt/*` restores, over their last 20 seasons, set against `levers.tsv` for the same histories.

| medians | holistic food | holistic kJ | designed food | designed kJ |
|---|---|---|---|---|
| random | 1.28 | 4.86 | 1.54 | 20.52 |
| flat | 1.41 | 4.90 | **2.21** | 20.44 |

- On flat ground the holistic fauna still works less on 29/29, and the work term is unchanged (+0.44 against +0.42).
- The food term, though, goes from −0.19 to **−0.81**.
- So claim 4's arithmetic holds, and its reading does not. The work gap is a constant of the two bodies. What
  gives the holistic fauna the lead is the clutter tax on the wheeled body's **food**, about 0.7 items a season
  (a third of its flat-ground intake), which random terrain levies and flat ground does not.
- This is D's H56 in the ecology, and it is the main confound in claim 2's "ahead late".

**Caveats:**
- The flat values come after 240 (RBT-101) or 840 (RBT-107) seasons of evolution on flat ground. They are an
  adapted response, not a static one. That makes the reversal a comparison of adapted populations, which is the
  form a registration would use.
- Two restores are partial checkpoints: `rbt-101-shift-804` (MANIFEST 548/600) and `rbt-101-shift-805` (599/600).
  Their 20-season windows end at 548 and 598.
- The committed season tables for both are complete, so §2's table is unaffected.

**For RBT-118's design (MUST).**
- Terrain is a primary factor, not a robustness arm. Any head-to-head on random terrain carries the wheel tax.
- The registration must run both terrains, or register the terrain with its clutter arithmetic stated in advance.
  This is D §5b item 4.

### H53, same-season refill: the extinctions stand; "fewest alive" understates both dips

`alive` is booked after the same season's births (`ecology.py` steps 3–5), so a slot freed by death can refill
before it is recorded. From `probe_terrain.txt` §3:

**Extinctions are unaffected.** A booked 0 means no breeder was left to refill.

**Fewest alive in seasons 0–59:**

| | booked (the PR's figure) | before the refill (alive − births) |
|---|---|---|
| holistic, median | 23 | **20** (range 0–28) |
| designed, median | 60 | **50** (range 43–53) |

- The designed fauna also dips, by about 10.
- The PR's "designed never dips (median 60, range 59–60)" is an artefact of the booking. It should read: "dips to
  a median 50 before same-season refill, against the holistic fauna's 20".

**Late (seasons 500–599):**
- Both faunas are booked at 60 in 100% of seasons.
- Before the refill, their fewest alive is 55 and 54.
- `alive` cannot move late in a separate ecology. This strengthens SHOULD 1: the registration must log deaths by
  cause and pre-refill counts.

**D §5b item 5 (print Σgear/mass).** The PR prints it at seasons 0, 59, 299, 599 and the last (1199 for RBT-107).
The restores and sampling are checked in claim 5 above. The wording fix is MUST-FIX 3.

---
_Generated by [Claude Code](https://claude.ai/code)_
