# RBT-106 pre-registration: is it the size of the prize that decides whether a compass is held?

*Designer's pre-registration, 2026-09-26. **No arm has been launched.** Every number below is read from
a committed readout beside this file, or from a committed file of another ticket, named at the number.
The runs made for it are throwaway checks of at most 20 seasons, or probes that run no ecology (§8).
RBT-104's tooling is imported from integration (RBT-104 is merged, c872e80, with its adversary's PR #181),
never copied or edited. **RBT-104's wave 0 is running.** At the time of writing, its season-150 gate had
read FUTILE on S8-4 (k = 8, n = 51, B = 16; ticket, 20:59), with S8-801 pending. §7.3 covers both
outcomes. The adversary is named by the coordinator.*

**The question** (ticket RBT-106). A correctly wired routed compass pays about 2.5× more in a patchy
world than in RBT-90's uniform one. Every evolution run of the recent phase, RBT-104 included, is in
the uniform world. **Is it the size of the prize, rather than reach, that decides whether selection holds
(or evolves) a compass?**

**The design in one paragraph** (as ruled by the coordinator at 20:28 UTC).
- **The flag** is the existing `--food-patches 3`. It is exactly one config field, `sim.food.patches`,
  and the run is byte-identical at 0 (§1).
- **Its prize**, measured here on the ten part-2 populations with RBT-103's harness unchanged, is
  **+2.103 [+1.542, +2.663] items at a = 64, against +0.844 [+0.618, +1.070] uniform: 2.49×** (§2).
- **The primary** is **P1 (S1-patchy) against RBT-104's S1 (S1-uniform)**: the same planted founders
  (RBT-104's, w = 1), the same ten seeds, one flag.
- **The factorial option** adds **P8 (S8-patchy)**. With RBT-104's S8 it completes a 2 × 2 of reach
  (K = 1, 8) × prize (uniform, patchy), and the interaction is pre-registered with its power.
- **A second option, H**, plants the compass at the **paying** magnitude (w = 32, a = 64) at the default
  reach in both worlds. It asks most directly whether the prize decides that a paying compass is held.
- **The readouts** are RBT-102's structure instrument and RBT-104's function harness, both unchanged,
  each with a positive control run in the patchy world (§6.1). "Held" is read against the operator-alone
  baseline at matched depth, and that baseline's false-positive rate on real genealogies is measured
  (§5).
- **Every "absent" verdict carries its matched-null power** (§6.3).

**Three corrections to the ticket's premises, found before designing:**
1. **RBT-103's "12 items in 3 patches" world is two fields, not one.** It also has `regrow_delay 45`
   (`runs/RBT-103/adversary/worlds/sparse-patchy/config.json`), and `regrow_delay > 0` switches the
   ecology to persistent arenas that carry food between seasons (`Ecology.persistent`, RBT-19). The
   one-field world is `patches = 3` at part 2's instant regrowth. Its prize was unmeasured; it is
   measured here (§2), and it is 2.49×, close to the ticket's "~3×".
2. **The one-field patchy world is richer, not harder.** Base income on the part-2 champions rises
   by +0.229 [+0.170, +0.287] (§2), and the 20-season throwaway runs breed ~1.6× faster (§4). The
   ticket's "harder at 12 items" was read from the regrow-45 world, where nothing regrows within a bout.
   Faster breeding means a deeper window, so every "held" reading is matched by **depth**, not season.
3. **RBT-104's planted founders carry a sub-paying compass.** At w = 1 the motif's gain is a = 2, and
   the operator alone never takes it to a paying rung (RBT-104 adversary `persistence-801.txt`: 0–1% at
   a = 64 at every depth). At t = 0 it is not food-dependent in either world (§3.3).
   - So the primary, S1-patchy against S1-uniform, asks whether a 2.5× prize holds or grows a
     sub-paying **structure** at the default reach. Its "absent" verdict cannot separate "the prize does
     not matter" from "the reach is too short" (§3.4, §6.3).
   - The factorial separates those two.
   - Option H asks the ticket's literal question, whether a **paying** compass is held.

---

## 1. The flag: `--food-patches 3`, one field, byte-identical at 0 (ticket item 1)

`--food-patches N` already exists (RBT-19). It sets `sim.food.patches`; with N > 0, `set_food_seed`
draws N patch centres uniform in the disc from the bout's food seed, and every item, and every instant
regrowth, falls uniformly within `patch_radius` (0.6 m, the default and RBT-103's) of a randomly chosen
centre. The patches are redrawn each bout. At N = 0 `_draw_patch_centres` returns before drawing, so
the food stream is untouched. **No code is added.**

Checked (`one_field.py`, `one_field.txt`, seed 801, 20 seasons, x86_64, MuJoCo 3.14.0):
- **Check 1: byte identity at 0.** Part 2's command with `--food-patches 0` written out passes RBT-104's
  `byte_identity.default` (imported): `seasons.txt` is **byte-identical** to the first 40 rows of
  `runs/RBT-90/forage-801/seasons.txt`, and `config.json` equals the committed one outside seasons,
  generations and workers, with RBT-105's `ecology.breed_stream` (null) tolerated and named.
- **Check 2: one field.** With `--food-patches 3`, `config.json` differs from the committed part-2 one in
  **exactly one field, `sim.food.patches` 0 → 3**. `regrow_delay` stays 0, so persistent arenas stay off.
- **Check 3: the seeded pair differs in the world only.** Two runs loading the same seeded founders at
  patches 0 and 3 save **60 of 60** byte-identical founders of each fauna, and their seasons differ from
  season 0. Both faunas forage in the world, so the holistic fauna's rows differ too (unlike
  `--link-scale`, this flag is not the designed body's alone). That is the world, not a leak.

Tests (`tests/test_rbt106.py`, 8): the flag is one field of the sim config and leaves `regrow_delay` at 0;
`--food-patches 0` is the default; the uniform world draws no patch centre; RBT-106's S1 command is
RBT-104's `run_arm.sh` S1 command token for token; each pair differs by exactly `--food-patches 3`; the
H and P pairs differ only in their founders; `held.py`'s criterion.

## 2. The prize in the one-field patchy world, measured (the ticket's premise)

`prize.sh` runs RBT-103's `routed_populations.py`, unchanged, on each part-2 population's committed-rule
bodies (bests 0, 100, …, 590, restored from `ckpt/rbt-90-SEED` into scratch) with the world taken from
`runs/RBT-106/world-patchy/config.json` (its `--config-from`, RBT-103's own world control): a = 32 and 64,
the rotated decoy at a = 64, 64 paired seeds from 7000. **Harness check:** the restored bodies in their
own world reproduce RBT-103's committed seed-801 row to the digit. `prize.py` pairs each population with
RBT-103's committed uniform row (`prize.txt`):

| | uniform (RBT-103) | one-field patchy | patchy − uniform, t(9) |
|---|---|---|---|
| **a = 64** | +0.844 [+0.618, +1.070], PAYS 8/10 | **+2.103 [+1.542, +2.663]**, PAYS 8/10 | **+1.259 [+0.900, +1.617]; ratio 2.49×** |
| a = 32 | +0.419 [+0.234, +0.604] | +0.887 [+0.537, +1.236] | +0.467 [+0.246, +0.688] |
| base income | 1.308 [1.179, 1.438] | 1.537 [1.399, 1.675] | +0.229 [+0.170, +0.287] |
| gain per unit base income, a = 64 | 0.64 | 1.37 | 2.1× |

- Every population gains in the patchy world (per-population ratios 1.9–3.1×).
- **The patchy gain is chemotaxis:** the rotated decoy leaves it FOOD-DEPENDENT on 9 of 10 populations
  (retaining −21% to +6%), and UNRESOLVED on seed 2.
- Direction signs agree between the worlds on every body both signed. Seed 2 is paired over the 6
  bodies RBT-103 could sign.
- This is close to RBT-103's adversary's two-field figures (+2.267 in P-801's world, +2.489 for P-801's
  own bodies at 12 items in 3 patches with regrow 45). The one-field world keeps the prize.

---

## 3. Seeded, with the seed stated exactly (ticket item 2)

### 3.1 Unseeded has no power, whatever the prize

RBT-102 found 0 carriers of the routed structure in 12,276 part-2 genomes. Drift proposes about **0.26
structural arrivals across all ten 600-season arms** (RBT-102 §2.4; RBT-104 §3.1), half of them
wrong-signed, and the patchy world does not change the proposal rate: the operator draws the same
structures in any world. An unseeded patchy arm would expect about 0.1 correctly signed arrivals in
the whole experiment. So no unseeded arm is proposed. Every arm here loads planted founders.

### 3.2 The founders

**w = 1: RBT-104's founders, byte for byte.** `founders.py SEED 1` calls RBT-104's
`seed_founders.write` (imported) and checks the digest against RBT-104's committed
`founders-digests.txt`. It matches **on all ten seeds**. They are part 2's own sixty designed-body
founders, with RBT-97's routed motif (a global `tanh` unit, bias 0, fed by the two wheel noses at ±1,
feeding both drive Effectors at w) installed at **w = 1 (a = 2)** in the even-i half: 15 at sign +1,
15 at sign −1, ages kept (RBT-104 §3.2). These are the founders of the primary and of the factorial.

**w = 32 (option H only).** The same founders with the motif at **w = 32 (a = 64)**, RBT-103's own
paying install. They are built by the same RBT-104 function with its motif-weight constant set to 32
for the call, so the construction differs in that one number. Their digests are committed in
`runs/RBT-106/founders-digests.txt`, and regenerate identically.

### 3.3 What the seed does at t = 0, in both worlds

**The factorial's four cells** (`t0_patchy.py`). This is RBT-104's design adversary's `founders_t0.py`,
imported and run unchanged, with its world pointed at `world-patchy`. Its uniform twin is RBT-104's
committed `founders-t0-SEED.txt`, the same script in part 2's world. The quantities are over the 30
planted founders of each seed, each against its bare twin, on 16 paired seeds. Cost is seeded − bare
under real smell. Food dependence is (real − decoy) seeded − (real − decoy) bare.

{{T0P}}

**Option H** (`founders_t0.py`, seeds 801 and 4, both worlds in one run). The uniform K = 1 row
reproduces the RBT-104 adversary's `founders-t0-801.txt` to the digit: cost +0.033 [−0.033, +0.100],
F −0.027 [−0.097, +0.043].

| seed | world | bare founder income | H − U, all 30 | **H − U, compass-signed** | F(H) − F(U), compass-signed | S1 − U | F(S1) − F(U) |
|---|---|---|---|---|---|---|---|
| 801 | uniform | 0.440 | +0.446 [+0.071, +0.821] | **+1.017 [+0.436, +1.597]** (15) | +0.500 [+0.108, +0.892] | +0.033 [−0.033, +0.100] | −0.027 [−0.097, +0.043] |
| 801 | patchy | 0.338 | +0.842 [+0.263, +1.420] | **+1.629 [+0.641, +2.617]** (15) | +1.254 [+0.341, +2.167] | −0.075 [−0.186, +0.036] | −0.031 [−0.146, +0.083] |
| 4 | uniform | 0.429 | +0.263 [−0.053, +0.578] | **+0.955 [+0.321, +1.589]** (11) | +0.568 [+0.010, +1.126] | −0.027 [−0.094, +0.039] | −0.008 [−0.085, +0.068] |
| 4 | patchy | 0.333 | +0.679 [+0.063, +1.295] | **+2.051 [+0.700, +3.403]** (11) | +1.659 [+0.511, +2.807] | −0.010 [−0.110, +0.089] | −0.042 [−0.240, +0.157] |

- **Patchy − uniform, H compass-signed:** +0.613 [+0.101, +1.124] (801), +1.097 [+0.159, +2.034] (4).
- The anti-signed H founders lose a little in both worlds, −0.13 to −0.21.
- **The a = 64 compass pays at founding in both worlds, more in the patchy one**, on bare founder
  incomes of only 0.33–0.44. The w = 1 compass does nothing in either world.

### 3.4 What each arm can ask, and why the primary's "absent" is weak evidence against the prize

- **P1 (S1-patchy) against S1 (S1-uniform)**, the primary as ruled. Same founders, same seeds, one
  flag. It asks: *with a sub-paying compass structure planted, does a 2.5× prize make selection hold
  the structure more, or grow it into food-dependent champions, at the default reach?*
  - At t = 0 the w = 1 compass is **not food-dependent in either world** (§3.3).
  - Under the operator alone it never reaches a paying rung (RBT-104 adversary `persistence-801.txt`:
    0–1% at a = 64 at every depth).
  - Growing it needs about 5 doublings of |u·v| (a from 2 to ≳ 32–64) through steps of N(0, 0.4) at
    rate 0.25, within about 25 generations, while the bias walks.
  - That is the reach RBT-104 tests. So **P1 can fail for want of reach even if the prize is what
    matters**, and its "absent" verdict (P-NULL) is worded that way (§6.5).
  - Its positive verdict would be strong: the prize alone suffices, at the default reach.
- **P8 (S8-patchy) against S8 (RBT-104's S8-uniform)**, the factorial option. Here the reach is raised
  and the prize varied. With S1 and P1 it completes the 2 × 2 of reach × prize, and the interaction
  I = [F(P8) − F(P1)] − [F(S8) − F(S1)] separates:
  - **"the prize is too small"**: P1 would evolve;
  - **"the reach is too short"**: S8 would evolve;
  - **"both"**: only P8 evolves, and I > 0.
- **HU against HP**, option H (recommended as a second option). The compass is planted at the paying
  magnitude (a = 64) at the default reach, so neither reach nor masking stands between it and the prize
  at founding:
  - its compass-signed founders earn the prize at t = 0 in both worlds (§3.3);
  - its paying class decays under the operator alone at **u ≈ 0.29 per generation** (the same bias gate
    as RBT-104's S8, §5.1).

  It asks the ticket's question most directly: **with u the same in both worlds, does the larger prize
  hold a paying compass that the uniform prize does not?** That is mutation–selection balance with only
  s varied.

## 4. Side effects: income, survival and turnover in the patchy world (ticket item 6; coordinator 20:28)

**Smoke runs first** (`side.py`; 20 seasons; RBT-90 part 2's command via RBT-104's `short_run.sh`;
RBT-104's seeded founders; seeds 801 and 4; each run's `seasons.txt` and `config.json` committed under
`side/`). These are throwaway runs, and feasibility readings, not results:

| cell | seed | patches | K | designed alive min / last | designed births | designed mean lifetime score | holistic alive min / last | holistic births |
|---|---|---|---|---|---|---|---|---|
| S1U | 801 | 0 | 1 | 60 / 60 | 85 | 0.504 | 16 / 18 | 33 |
| S1U | 4 | 0 | 1 | 60 / 60 | 91 | 0.550 | 30 / 60 | 81 |
| S1P | 801 | 3 | 1 | 60 / 60 | 138 | 0.983 | 19 / 47 | 66 |
| S1P | 4 | 3 | 1 | 60 / 60 | 165 | 0.740 | 27 / 60 | 89 |
| S8U | 801 | 0 | 8 | 39 / 60 | 181 | 0.371 | 16 / 18 | 33 |
| S8U | 4 | 0 | 8 | 60 / 60 | 150 | 0.595 | 30 / 60 | 81 |
| S8P | 801 | 3 | 8 | 48 / 60 | 297 | 1.014 | 19 / 47 | 66 |
| S8P | 4 | 3 | 8 | 42 / 60 | 263 | 0.912 | 27 / 60 | 89 |

the prize at K = 1 (S1P / S1U): designed mean lifetime score x1.95, x1.35; births x1.62, x1.81 (seeds 801, 4)
the prize at K = 8 (S8P / S8U): designed mean lifetime score x2.73, x1.53; births x1.64, x1.75 (seeds 801, 4)
the reach, uniform (S8U / S1U): designed mean lifetime score x0.74, x1.08; births x2.13, x1.65 (seeds 801, 4)
the reach, patchy (S8P / S1P): designed mean lifetime score x1.03, x1.23; births x2.15, x1.59 (seeds 801, 4)
seed 801: holistic rows of S8U byte-identical to S1U's (the flag is the designed body's only): True
seed 4: holistic rows of S8U byte-identical to S1U's (the flag is the designed body's only): True

extinction of either fauna within 20 seasons: none

**What the smoke runs say:**
- **The patchy world is richer at both reaches.** At K = 1 the designed fauna's mean lifetime score is
  ×1.35–1.95 and its births ×1.6–1.8. At K = 8 they are ×1.5–2.7 and ×1.6–1.75.
- **K = 8 costs survival briefly.** The designed fauna dips to 39–48 alive, recovers to 60 by season 20,
  and breeds 1.6–2.2× more. Turnover is faster.
- **P8 combines both.** Its births are 3.1–3.5× those of S1U, so its window will sit far deeper than
  any uniform arm's. This is why every "held" reading is depth-matched, and why baselines run to depth 40.
- **The holistic fauna** is untouched by `--link-scale` (its rows are byte-identical between K = 1 and
  K = 8 on both seeds), and changed by `--food-patches` (it forages in the same world).
- **No fauna went extinct in any cell.**

**Read with the prize table (§2):** the one-field patchy world is richer at every level measured.
- The part-2 champions' base income rises by +0.229 [+0.170, +0.287] (1.18×).
- The seeded founders' 20-season mean lifetime score about doubles.
- Designed-body births rise about 1.6×.

The ticket expected "harder at 12 items". That holds only in the regrow-45 world, where an eaten item
is gone for the bout. In the one-field world an eaten item regrows at once inside a patch, so a robot on
a patch keeps eating. **Lesson 7** (an insolvent population's prediction is a bracket): no cell is
insolvent in 20 seasons, and the patchy cells are richer, so the predictions below are points. The K = 8
cells are the poorest (S8U), and RBT-104's own predictions govern S8.

**Consequence for the design: turnover, hence depth.** At about 1.6× the births, a patchy arm's window
sits deeper than part 2's 14–17.5 generations. So:
- every "held" reading is matched to the **operator-alone baseline at each genome's own depth** (§5.1),
  never at matched season, and baselines run to depth 40;
- the depth each arm reaches is reported beside its verdict (`rbt102.txt`'s window depth).

The operator also acts more often per season in the patchy world. That is part of what "the patchy world"
is, and the depth-matched null absorbs it.

**Side-effect predictions** (window seasons 300–599, paired over usable seeds; `readout.py` prints each):

| # | prediction | confidence |
|---|---|---|
| SE-1 | No P1 arm goes extinct (10 of 10 viable, ≥ 30 alive on average in the window) | 0.90 |
| SE-2 | P1 − S1 window income, designed fauna: t interval above zero | 0.85 |
| SE-3 | P1 has more designed births than S1 on ≥ 8 of 10 seeds, and a deeper window (analyse.py window depth) on ≥ 8 of 10 | 0.80 |
| SE-4 | (factorial) P8 − S8 window income above zero, and no P8 arm extinct | 0.75 |

## 5. The null for "held": the operator-alone persistence baseline (ticket item 3; RBT-104 adversary F6)

### 5.1 The baseline, at every depth, every seed, every cell

`baseline.py` imports RBT-104's `baseline.py`, and through it the adversary's `persistence.py`
`lineage()`, unchanged. Each seed's 30 planted founders are carried down 20 independent lineages of
`mutate_controller` under part 2's MutationConfig, with **no selection and no crossover**, and read with
RBT-91's instruments at every depth from 0 to 40. There is one table per seed and cell:
- `baseline-w1-SEED.txt`, K = 1;
- `baseline-w1-k8-SEED.txt`, K = 8;
- `baseline-w32-SEED.txt`, option H.

The world does not enter. **At K = 8 the pay64 column reproduces RBT-104's `baseline-801.txt` and
`baseline-4.txt` count for count at every depth 0–30.**

Means over the ten seeds (range):

| depth | 1 | 2 | 4 | 8 | 16 | 25 | 40 |
|---|---|---|---|---|---|---|---|
| w = 1, K = 1, structure with its sign (`same`) | 0.93 | 0.85 | 0.72 | 0.49 | 0.23 | 0.12 | 0.05 |
| w = 1, K = 8, paying (own links ≥ 24.71, sign) | 0.75 | 0.55 | 0.31 | 0.13 | 0.035 | 0.013 | 0.005 |
| w = 32, K = 1, paying (own links ≥ 12.52, sign) | 0.71 | 0.49 | 0.25 | 0.07 | 0.013 | 0.005 | 0.002 |

**Option H's compass is erased by the operator as fast as RBT-104's S8's**: u ≈ 0.29 per generation.
- Its own links collapse after a single bias mutation, because at v = 32 a resting drive v·tanh(b)
  above ~1 saturates the Effector. This is RBT-104 §1.4's bias gate, now at K = 1.
- At founding, though, its whole-brain response is intact (median 11.9, against 0.0025 for S8's). So it
  pays at t = 0 (§3.3), where S8's does not.

### 5.2 The "held" statistic (`held.py`)

This is RBT-104's `peek.py` statistic, imported and generalised by one parameter: the criterion,
fixed per cell before any arm.

| cell | criterion (a living genome "hits" if its best predicate unit has…) |
|---|---|
| P1, S1 (w = 1, K = 1) | `same`: the planted structure, with its root founder's sign, at any magnitude. The w = 1 compass never pays at K = 1, so "held" can only mean the structure. |
| P8, S8 (w = 1, K = 8) | `pay64`: own links ≥ 24.7145 with the root's sign. This is RBT-104's own F-b criterion, so S8-patchy is read exactly as RBT-104 reads S8. |
| HU, HP (w = 32, K = 1) | `pay32`: own links ≥ 12.5236 (the a = 32 rung) with the root's sign. It is not the a = 64 rung, because the planted unit reads 24.1 at founding, just below 24.7145, so an a = 64 test would score founders as not paying (40% at depth 0). |

The statistic is read at the end of a season:
- **k** is the number of living hits;
- **n** is the number of living genomes rooted in a planted founder;
- **μ** is the mean of the baseline fraction at each such genome's own depth;
- **B** is the 95th percentile of Binomial(n, μ).

**HELD at a season iff k > B.** An arm is **HELD** iff it is HELD at both 300 and 599. Bare-rooted hits
(de novo carriers) enter k but not n, and every approximation errs toward reading HELD.

### 5.3 How often HELD fires with nothing selecting the compass: measured (`null_genealogy.py`)

RBT-104 §6.2 noted that the living are clustered by descent, so a no-selection arm exceeds B "more
often than 5%", and left it unmeasured. It is measured here:
- **the genealogy** is part 2's own real 600-season one per seed (`lineage.jsonl`, restored), under
  selection on gait and income but with no compass anywhere;
- **the plant** puts the founders at part 2's founders (checked: the bare odd-i founder files equal
  part 2's saved `c0-i`, 30 of 30, every seed);
- **the operator** is run down that genealogy, one `mutate_controller` draw per birth, shared by all
  its descendants;
- **the call** is `held.py`'s own rule;
- 20 replicates per seed and cell.

| cell criterion | HELD at both 300 and 599, over 10 seeds × 20 replicates |
|---|---|
| `same`, w = 1, K = 1 (P1, S1) | **12/200 = 6.0%** |
| `pay64`, w = 1, K = 8 (P8, S8) | **5/200 = 2.5%** |
| `pay32`, w = 32, K = 1 (H) | **2/200 = 1.0%** |

So "HELD" is a conservative call for the paying criteria. For the structure criterion it is near the
nominal 5%, inflated to 6% by clustering. These are the q values under "no effect" in §6.3.

## 6. Readouts, verdicts, power and predictions (ticket items 4 and 5)

### 6.1 The readouts, unchanged, each with a positive control run in the patchy world

- **(a) Structure: RBT-102's `analyse.py`, unchanged.** It gives carriers per season, X (the mean
  carriage over seasons 300–599), window depth, and its own positive control (20 window genomes,
  installs at (w = 1, +) and (w = 8, −), which must detect 40 of 40). **Run in the patchy world**
  (`controls/rbt102-P1-801-20seasons.txt`: P1 founders, 20 seasons, window 10–19): **40 of 40 detected,
  PASSED**; the planted founders read 30 of 60 carriers at season 0. It reads the structure's signs,
  not the world, so it passes in any world.
- **(b) Function: RBT-104's `function.py`, unchanged** (RBT-97/103's harness: F = intact(real smell) −
  intact(rotated decoy) over the bests at 300, 350, …, 590, 64 paired seeds, t(6); FOOD-DEPENDENT if
  the interval excludes zero from above and the zero-count veto passes). **Positive control run in the
  patchy world** (`controls/function-patchy-801.txt`, part 2 seed 801's window champions scored in the
  patchy world through `cross_world.py`):

  | control | must read | read |
  |---|---|---|
  | champion + installed a = 64 motif | FOOD-DEPENDENT | **F +2.556 [+1.422, +3.690], FOOD-DEPENDENT**; the decoy retains 2.1%; attribution FOOD-DEPENDENT |
  | RBT-103's own scoring on the same bodies | a paying motif | motif − bare **+2.576 [+1.044, +4.108]**, decoy − bare +0.020 |
  | bare champions (negative) | not food-dependent | F +0.223 [−0.196, +0.643], **VETOED** by the zero count (not food-dependent) |

- **Per arm, at readout,** the install control is run on that arm's own bests (`function.py --install
  32` → `function-pc.txt`) and must read FOOD-DEPENDENT, and analyse.py's control must pass. An arm
  failing either is **unusable, not a null**.
- **Both worlds, for every arm** (`cross_world.py`). A compass pays about 2.5× more in the patchy
  world, so F of a patchy arm scored in its own world would exceed F of a uniform arm through the
  measuring world alone. **Every arm's bests are scored in both worlds**: the arm's own world is
  `function.py` directly, and the other world goes through `cross_world.py`, which imports
  `function.py` and replaces only the world config. The pre-registered contrasts use the **patchy
  scoring** for both arms of a pair, because a compass is most visible there. The uniform scoring is
  printed beside it.
- **The pipeline was run end to end** on 21-season HU and HP smoke runs
  (`controls/pipeline-smoke-H-801.txt`), not arms and not a verdict. It covers `run_arm.sh`,
  `postrun.sh`, analyse.py, held.py at two seasons, function.py in both worlds, the install control and
  `readout.py`.

### 6.2 The verdicts (`readout.py`; thresholds in code, printed beside every verdict)

"Usable" means viable (no extinction, reached season 599, ≥ 30 alive on average in the window), on
x86_64, and passing both positive controls. **VOID** if fewer than 7 paired seeds are usable. FD means a
line reads FOOD-DEPENDENT in the patchy scoring.

**Primary: the P pair, P1 (S1-patchy) against S1 (RBT-104's S1-uniform).**
- **P-EVOLVED:** P1 FD on **≥ 3** usable seeds **and** the paired F(P1) − F(S1) t(9) interval above
  zero. *At the default reach, a 2.5× prize evolved food-dependent champions from a sub-paying planted
  compass.*
- **P-NULL:** P1 FD on **≤ 1** usable seed **and** that interval not above zero. It is worded against
  §6.3's power and §3.4's reach caveat.
- **NOT DECIDED** otherwise.
- Reported beside it, not in the verdict: structure HELD counts, P1 against S1 (criterion `same`), and
  the paired log-excess log((k + 1)/(nμ + 1)) at 599.

**Factorial option: the 2 × 2 (S1, P1, S8, P8),** patchy-scored, over seeds with all four cells usable.
- **I = [F(P8) − F(P1)] − [F(S8) − F(S1)]**, with its paired t(n − 1) interval. This is the
  pre-registered interaction.
- The verdict, in order:
  - **PRIZE SUFFICES:** P1 FD ≥ 3 and F(P1) − F(S1) > 0;
  - **REACH SUFFICES:** S8 FD ≥ 3 and F(S8) − F(S1) > 0; if both of these hold, **EACH SUFFICES**;
  - **BOTH NEEDED:** I's interval above zero, P8 FD ≥ 3, and P1 and S8 FD ≤ 1;
  - **NEITHER (at K = 8 and a 2.5× prize):** every cell FD ≤ 1 and no paired interval above zero;
  - **NOT DECIDED** otherwise.
- The P8 pair (P8 against S8) also gets the P-pair form (P8-EVOLVED, P8-NULL), and HELD at `pay64`
  against the §5.3 null.
- RBT-104's own verdict governs RBT-104. The factorial reads RBT-104's S1 and S8 arms through
  RBT-106's own post-run reads (§7.3). It does not re-judge them.

**Option H: HU against HP.**
- **SUPPORTED:** #HELD(HP) − #HELD(HU) ≥ 3 **and** the paired log-excess interval above zero. *The
  larger prize held the paying compass where the uniform prize did not.*
- **FALSIFIED-a:** #HELD(HU) ≥ 5 and that interval not above zero. *The uniform prize already holds it,
  and the 2.5× prize added nothing measurable. Here the prize is not what limits holding.*
- **FALSIFIED-b:** #HELD(HP) ≤ 1. *Not even the 2.5× prize held a paying compass against the operator.
  The bias gate decides, not the prize.*
- **NOT DECIDED** otherwise. Function (FD counts and paired F, patchy-scored) is reported beside it.

### 6.3 Matched-null power (`power.py` → `power.txt`)

Layer 1 is imported from RBT-104's adversary: P(a line reads FD | a fraction p of its seven window
champions carries a working compass) is 0.10 at p = 0 (0.05 centred), 0.62 at p = 4/7 and 0.96 at 6/7.
That is the uniform world's per-body spread; the patchy prize is 2.5× larger, so this is conservative.
The verdict layers, where q is the probability that a seed's line carries a working compass in 4 of
its 7 window champions (all figures at n = 10 usable seeds, n = 7 in brackets):

| truth (q for S1, P1, S8, P8) | P-EVOLVED | **P-NULL** | P(I > 0) | PRIZE SUFF. | REACH SUFF. | BOTH NEEDED | NEITHER |
|---|---|---|---|---|---|---|---|
| nothing holds (0, 0, 0, 0) | 0.002 | **0.72** (0.83) | 0.025 | 0.002 | 0.002 | 0.001 | 0.26 (0.47) |
| the prize alone suffices (0, .5, 0, .5) | 0.55 (0.27) | **0.05** (0.18) | 0.03 | 0.55 | 0.001 | 0.004 | 0.001 |
| the prize suffices, weakly (0, .25, 0, .25) | 0.12 | **0.27** (0.47) | 0.02 | 0.12 | 0.001 | 0.006 | 0.04 |
| reach alone suffices (0, 0, .5, .5) | 0.002 | 0.72 | 0.03 | 0.001 | 0.55 | 0.004 | 0.002 |
| both needed (0, 0, 0, .5) | 0.002 | 0.72 | **0.57** (0.36) | 0.002 | 0.002 | **0.26** (0.17) | 0.02 |
| both needed, weakly (0, 0, 0, .3) | 0.002 | 0.72 | 0.24 | 0.002 | 0.002 | 0.09 | 0.07 |

**What the "absent" verdicts can and cannot say.**
- **P-NULL against "the prize alone suffices":** it fires with probability 0.05 at q = 0.5 and 0.27 at
  q = 0.25. So P-NULL is fair evidence against the prize *alone* sufficing at q ≥ 0.5, and weak
  evidence below.
- **P-NULL against "both are needed":** it fires 72% of the time, so **P-NULL says nothing about
  whether the prize matters when reach is also short. Only the factorial can say that.**
- **NEITHER:** it fires 26% of the time even when nothing holds, because bare lines produce FD false
  positives. Its absence is not evidence of an effect.
- **BOTH NEEDED is under-powered** (0.26 at q = 0.5). It is capped by the requirement that P1 and S8
  each read FD ≤ 1 (bare-line false positives at 0.10 per line).
  - I's interval alone detects the interaction with probability 0.57.
  - A factorial that ends NOT DECIDED with I > 0 is reported as "interaction indicated, not decided".

**Option H** (layer 2; q_U, q_P = P(HELD) per seed):
- **The no-effect false-positive rate is measured** (§5.3): 1.0% per seed, so P(SUPPORTED's count |
  q_U = q_P = 0.08) = 0.020 even at an inflated 8%.
- **Under "the prize decides"** (q_U 0.15, q_P 0.60): P(SUPPORTED's count) = **0.85** (0.67 at n = 7);
  P(FALSIFIED-b) = 0.002.
- **Weaker** (q_P 0.40): P(SUPPORTED's count) = 0.50, P(FALSIFIED-b) = 0.05.
- **Under "the uniform prize suffices"** (q_U 0.60, q_P 0.70): P(FALSIFIED-a) = 0.83.

The layer-2 grid is in `power.txt`.

**Stated q under the hypotheses** (not measured; they are the design's, and the confidences in §6.4
come from them):
- **P1: q ≈ 0.05.** The compass is sub-paying and not food-dependent at t = 0 in either world (§3.3),
  and it cannot reach a paying rung without reach.
- **P8: q ≈ 0.15–0.3 if the prize matters.** {{P8Q}}
- **H:** q_P ≈ 0.5 and q_U ≈ 0.3. The compass-signed founders earn the prize at t = 0 in both worlds,
  more in the patchy one (§3.3), against u ≈ 0.29.

### 6.4 Predictions and confidences (fixed before any arm)

| # | prediction | confidence |
|---|---|---|
| **P-0** | **Primary verdict: P-NULL** | **0.72** |
| P-0a | Primary verdict: P-EVOLVED | 0.06 |
| P-0b | Primary verdict: NOT DECIDED | 0.17 |
| P-0c | Primary verdict: VOID | 0.05 |
| P-1 | Structure, P pair: #HELD(P1) − #HELD(S1) ≤ 1 (the prize does not hold a sub-paying structure) | 0.70 |
| P-2 | P1's window carriage X is below 250 per 1,000 on ≥ 8 of 10 seeds (the patchy window is deeper, so the operator leaves less than RBT-104's P-6 figure) | 0.65 |
| F-0 | (if the factorial runs) FACTORIAL: NEITHER 0.40, BOTH NEEDED 0.10, PRIZE SUFFICES 0.04, REACH SUFFICES 0.04, NOT DECIDED 0.34, VOID 0.08 | — |
| F-1 | (if the factorial runs) I's interval above zero | 0.20 |
| F-2 | (if the factorial runs) P8's season-150 gate reads CONTINUE on ≥ 1 of 801 and 4 (§7.2) | 0.40 |
| H-0 | (if H runs) H: SUPPORTED 0.25, FALSIFIED-a 0.30, FALSIFIED-b 0.15, NOT DECIDED 0.25, VOID 0.05 | — |

P-0 to P-0c sum to 1, and so do F-0 and H-0.

**P-0 is the modal outcome**, for the reason in §3.4. It is **not** a verdict on the prize hypothesis,
and the report must say so in its headline. **H-0 leans FALSIFIED-a over SUPPORTED.** At t = 0 the
compass-signed H founders earn +1.0 items in the uniform world as well, on a bare income of about 0.44
(801), which is already an advantage far above u. So the uniform prize may well suffice, and the
larger prize would then add nothing measurable.

### 6.5 The falsifiers, in plain words

*Primary (P-NULL).* We planted the compass's wiring, at the weak strength drift gives it, in half the
founders of ten populations. We then let them evolve for 600 seasons in a world where a working compass
pays about two and a half times more than in RBT-90's (+2.10 against +0.84 items per bout, §2). If the
champions still steer no more by where the food is than the same populations in the uniform world, and
at most one population in ten turns food-dependent, then **a bigger prize alone, at the default reach,
does not make a compass**.
- This says nothing about whether the prize matters once the reach is there. A population that needs
  both would read the same way 72% of the time (§6.3).
- It fails "the prize alone suffices" with probability 0.05 if that were true in half the populations,
  and 0.27 if in a quarter.

*Factorial (NEITHER).* The same, with an eight-times link reach as well, in both worlds. If no cell
evolves food-dependent champions beyond one line and no contrast is positive, then **neither a 2.5×
prize nor ×8 link reach, nor both together, suffices at this depth**. Read with §6.3: NEITHER also
fires 26% of the time when nothing holds, and BOTH NEEDED has power 0.26 at q = 0.5.

*Option H (FALSIFIED-a / FALSIFIED-b).* We planted a compass that already pays, in both worlds, at the
default reach.
- **FALSIFIED-a:** if it is held above what the operator alone leaves in the uniform world too, then
  **the size of the prize is not what decides holding**; the uniform prize is enough.
- **FALSIFIED-b:** if it is not held even where it pays 2.5× more, then **the prize does not decide
  it either; the operator's erasure (the bias gate) does**.

*Scope, all verdicts.* This covers one patchy world (12 items in 3 patches, instant regrowth, random
terrain), RBT-90 part 2's ecology, planted structure, and 600 seasons. It is not "patchiness" in
general. The regrow-45 world is a different ecology (persistent arenas).

## 7. Seeds, arms, cost and packing (ticket item 7)

### 7.1 Arms

| arm | founders | flags beyond part 2's command | role | n |
|---|---|---|---|---|
| **P1** | w = 1 (RBT-104's) | `--food-patches 3` | **primary** (S1-patchy) | 10 |
| S1 | w = 1 | none | RBT-104's arm; read by RBT-106's post-run (§7.3) | (10, RBT-104's) |
| P8 | w = 1 | `--link-scale 8 --food-patches 3` | factorial option (S8-patchy) | 10 |
| S8 | w = 1 | `--link-scale 8` | RBT-104's arm; read by RBT-106's post-run | (10, RBT-104's) |
| HU | w = 32 | none | option H | 10 |
| HP | w = 32 | `--food-patches 3` | option H | 10 |

The seeds are RBT-90 part 2's ten: 801, 804, 805, 806, 807, 1, 2, 3, 4, 7. Depth is 600 seasons.
`run_arm.sh ARM SEED` builds the command from RBT-104's `seed_founders.PART2` (imported), so every arm
shares it by construction. `tests/test_rbt106.py` pins RBT-106's S1 to RBT-104's `run_arm.sh` S1 token
for token, and each pair to exactly one flag apart. `run_arm.sh`:
- regenerates the founders and refuses any digest but the committed one;
- refuses any machine but x86_64 (RBT-96);
- writes `platform.txt` and `command.txt`;
- refuses to relaunch over an existing run (resume it instead).

### 7.2 Waves and gates (`waves.txt`)

Two arms per session side by side at `WORKERS=2`, each with its own
`DURABLE_WATCH_PID=… scripts/durable.sh every 20 runs/RBT-106/ARM-SEED rbt-106-ARM-SEED` loop and its
own final save after `postrun.sh` (README rules 1, 3 and 6). Every checkpoint label is named on the
ticket at launch. Waves are ≤ 10 sessions.

- **Wave A, primary, 5 sessions:** P1 on the ten seeds, paired across seeds.
- **Factorial option, wave A′, 1 session:** P8-801 and P8-4. At the end of season 150, `held.py
  runs/RBT-106/P8-SEED SEED 1 --season 150` reads **only** the P8 arm's living designed genomes against
  the K = 8 baseline, the same statistic RBT-104's gate reads on S8 (`pay64`). No income, no S1, no P1,
  no later season. **STOP the factorial** (launch no more P8) if both seeds read AT OR BELOW
  NO-SELECTION. Otherwise launch wave B: P8 on the other eight seeds, 4 sessions.
  - **If RBT-104's own gate stopped S8 on 801 and 4, P8 still runs wave A′.** The larger prize is
    exactly what might let selection hold the compass against the operator (coordinator, 20:28). P8's
    gate is its own.
  - At t = 0 in the patchy world the K = 8 compass is {{P8T0}} (§3.3), and the wave-0 price is one
    session.
  - The gate is futility-only. It cannot raise a verdict, and the report says it was read.
- **Option H, 2 + 8 sessions:** wave H0 is (HU-801, HP-4) and (HP-801, HU-4). The gate at season 150
  on HP-801 and HP-4 (`held.py … 32 --season 150`, `pay32`) STOPs option H if both read AT OR BELOW
  NO-SELECTION. Otherwise wave H1 runs the other 16 arms, 8 sessions.

### 7.3 The uniform twins are RBT-104's arms; the contingency if they stop

S1 and S8 are RBT-104's arms, run by RBT-104's launcher.
- **Their post-run reads for RBT-106** are held.py at 300 and 599 and function.py in the patchy world.
  `postrun.sh S1 SEED` (or S8) makes them, from `ckpt/rbt-104-ARM-SEED` restored outside the checkout.
  It copies RBT-104's committed `platform.txt`, `rbt102.txt`, `function-pc.txt` and `function.txt`
  (the uniform scoring) rather than recomputing them.
- **If RBT-104's gate stops it after its wave 0**, S1 and S8 exist on 801 and 4 only. Then:
  - the primary needs **S1 on the other eight seeds: 4 sessions**, run from RBT-106's launcher. The
    command is RBT-104's (the test pins it), so the arms are the ones RBT-104 would have run, byte for
    byte;
  - the factorial, if its gate continues, also needs S8 on those eight: 4 sessions.
- These are launched in the same wave as the P arms they pair with.

### 7.4 Cost

Per session, about 51 min of ecology (5.1 s per arm-season, two arms side by side, RBT-104 §5), plus
about 40 min of post-run for the pair. That is RBT-104's 25 min plus the second-world function scoring
and the two held.py reads. So **about 1.5–2.5 h per session.**

| block | sessions | session-hours |
|---|---|---|
| **Primary** (P1 × 10) | **5** | **7.5–12.5** |
| + S1 contingency (if RBT-104 stops) | +4 | +6–10 |
| Factorial wave A′ (P8 on 801, 4) | 1 | 1.5–2.5 |
| + wave B (P8 × 8), if the gate continues | +4 | +6–10 |
| + S8 contingency | +4 | +6–10 |
| Option H (H0 + H1) | 2 + 8 | 15–25 |
| **Everything, worst case** | **32** | **48–80** |
| **Primary + factorial, RBT-104 not stopped** | **10** | **15–25** |

The post-run reads of RBT-104's S1 and S8 arms (restore, held.py twice, one cross-world function.py)
are about 15 min each. They need no ecology, and can run in any session or in the coordinator's.

## 8. What was run for this design (throwaway, not arms; all x86_64, MuJoCo 3.14.0, numpy 2.4.6)

1. **The flag** (`one_field.py`, `one_field.txt`): byte identity at 0 (20 seasons, seed 801), one
   field at 3, the seeded pair's founders identical. **Re-run after merging integration at 25e41a3**
   (RBT-104 merged, RBT-96's salt): still byte-identical, and the seeded S1 run is byte-identical to
   its pre-merge twin.
2. **The prize** (`prize.sh`, `prize.py`, `prize.txt`, `prize/`): RBT-103's harness, ten populations,
   one-field patchy world; the harness check is identical to RBT-103's 801 row.
3. **The founders** (`founders.py`, `founders-digests.txt`): w = 1 matches RBT-104's digests on ten of
   ten seeds; w = 32 regenerates identically.
4. **t = 0** (`t0_patchy.py`, `t0/patchy-t0-*.txt`, ten seeds; `founders_t0.py`, `t0/founders-t0-{801,4}.txt`).
5. **Side effects** (`side.py`, `side/`, 20-season smoke runs of the 2 × 2 on 801 and 4).
6. **Baselines** (`baseline.py`, `baseline/`, 30 tables) and **the null genealogy** (`null_genealogy.py`,
   `null/`, 30 × 20 replicates).
7. **Readout positive controls in the patchy world** (`controls/`): analyse.py 40 of 40;
   function.py's install control, RBT-103's scoring and the bare negative control, on part 2 seed 801.
8. **The pipeline end to end** (`controls/pipeline-smoke-*`) on 21-season HU and HP runs.
9. **Power** (`power.py`, `power.txt`), with the rules' thresholds set on it before any arm. A first
   draft with "≥ 5 FD lines and S1 ≤ 1" had power 0.28 at q = 0.5, and was replaced by ≥ 3 plus the
   paired interval.
10. **Tests** (`tests/test_rbt106.py`, 12). The full suite: **317 passed** (after merging integration).

## 9. Files

| file | role |
|---|---|
| `PREREGISTRATION.md` | this |
| `run_arm.sh`, `command.py`, `waves.txt` | one arm; its command (from RBT-104's PART2); the sessions |
| `postrun.sh` | per-arm post-run steps (and the reads of RBT-104's S1 and S8) |
| `readout.py` | the pre-registered verdicts (P, P8, H pairs; `--factorial`) |
| `held.py` | "held" against the operator-alone baseline (RBT-104's peek.py, generalised) |
| `cross_world.py` | readout (b) in the other world (RBT-104's function.py, world replaced) |
| `founders.py`, `founders-digests.txt` | the seed (RBT-104's seed_founders.py, imported) |
| `one_field.py`, `one_field.txt` | §1 |
| `prize.sh`, `prize.py`, `prize.txt`, `prize/`, `world-patchy/config.json` | §2 |
| `t0_patchy.py`, `founders_t0.py`, `t0/` | §3.3 |
| `side.py`, `side/` | §4 |
| `baseline.py`, `baseline/`, `null_genealogy.py`, `null/` | §5 |
| `controls/` | §6.1 |
| `power.py`, `power.txt` | §6.3 |
| `tests/test_rbt106.py` | the flag is one field; the arms' commands; held.py's criterion |
