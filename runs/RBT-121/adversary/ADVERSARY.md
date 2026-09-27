# RBT-121 adversary: which of the three audits' load-bearing claims hold?

*This is the adversary for the RBT-121 loophole audit. It is read-only on `rabbitstew/`.*

*Every number here comes from a probe in this folder, or from a committed file cited by path. The probes are
`adv_*` (demography and lineage), `phys_*` (physics), `noise_*` and `smell_*`, each with its `.txt`.*

*The audits reviewed:*
- *A: #396 @ c6dc0c4*
- *B: #395 @ a9a6050*
- *C: #397 @ 791461b, plus 846f913*

*The RBT-113 checkpoints were restored with `scripts/durable.sh restore` at 216/216.*

## Verdicts at a glance

| # | claim | verdict | the correction the synthesis needs |
|---|---|---|---|
| 1 | C1 / B4: the breeding lottery is saturated; ×2 never fixes | **HOLDS-WITH-CAVEAT** (mechanism) | Only when resident net income is well above the living cost (g0 ≳ 0.8). At g0 ≤ 0.5 the committed rule fixes a ×1.25 forager. In committed P-801, 61% of holistic children starve, so the economy selects **hard on viability** and weakly above it. "Deaths are nearly all from age" is **WRONG**: 39% holistic, 16% designed. |
| 1e | "probably explains RBT-80's NO VERDICT" | **WRONG** | RBT-80's seeded arms held carriage at 0.96 / 0.72 / 0.92 against no-selection floors of about 0.52. The verdict failed on the drift arm's half depth (5.0 against about 11). Non-carriers earned 0.08–0.64, which is the non-saturated regime. |
| 1f | paper 10's HP − HU is partly selection strength | **OVERSTATED** | Both worlds sit in the saturated band, HP more so. The mechanism cannot favour HP. H8's confound stands as written. |
| 1g | B's 2–3× against C's 0 → 200/200 | consistent | The two are in different income regimes. The synthesis should state the rule as net income ÷ living cost. |
| 1h | C 846f913: "16× flatter; every Δ ≤ +1 loses ground" | **OVERSTATED** | μ = 1.3 is survivor-weighted. Income per birth is about 0.48. The model has no viability sieve, and RBT-80 is the counter-example. |
| 1i | the `breed_order=energy` fix | **cost not reported** | Under hoarding it is a gerontocracy: parents fall from 137 to 71, and age at breeding rises from 31 to 54. That roughly halves depth per season. |
| 2 | A2: 83% of D-line work on embedded joints; 79% embedded | **OVERSTATED** | The metric is sd < −2 cm, which counts any tilted attachment. At least half the volume inside: 17% of pairs and 34% of work. 97% of work is on children touching nothing. The filter is weld-group, not parent: 45–120% more pairs are filtered. The ball cone is the load-bearing fix. |
| 3 | A1: gear table 1.7605 / 30.3 / 10.1 / (c) spares the Pioneer; power ∝ gear | **HOLDS** | The Pioneer margin under c = 1.77 is only 0.5%. Power = 20 × gear holds for torque and ball motors only; velocity servos give 2.81 × gear. |
| 4 | A3: 14 of 240 drift; motors-off food matches intact | **HOLDS-WITH-CAVEAT / OVERSTATED** | The figure is 14 of **120** holistic. "Off" really is zero actuation, confirmed by a limp variant. The food match is 1 item against 1 and is mostly static reach. Part of the drift is terrain rolling. |
| 5 | B3: repeatability 0.14 / 0.004; s below erosion | **HOLDS-WITH-CAVEAT** | The designed 0.004 is the estimator's floor: it reads 0 in 29% of 6-draw subsets, and 12 draws give 0.03–0.1. s ≈ 1.27 Δ/σ_P, independent of repeatability. The hold condition is s > u/(1 − u). |
| 6a | C2: nose step 0–7% against speed 12–37% | **HOLDS-WITH-CAVEAT** | Speed wins in all 18 cells of a 3 × 3 × 2 grid. The individual nose percentages are within Monte Carlo error, and C's two probes disagree on speed (+12% against +31%). |
| 6b | the PW `smell_gain` (centred log contrast) | **OVERSTATED** | The model's "gain 10" is G ≈ 2.5. At G = 10, contrasts saturate and nose steps pay about 2%. Root-centring zeroes root sensors, single-nose smell and temporal smell. The model's eating is not the simulator's (centre of mass + 0.15 m, against any geom centre). |
| 7 | A5: the rod sweeper at +0.61, reachable in about 20 steps | **OVERSTATED** | A 0.45 m arm earns the same (+0.65 to +0.75). The allowance is a blind full-throttle tumbler, not reach, and there is no gradient toward length. |

## What the synthesis should and should not rest on

**Rest on:**
- A1's cap (c), with a test that pins the Pioneer margin;
- the ball-joint cone (plus hinge ranges) as the ghost-rotor fix;
- B's s ≈ i·Δ/σ_P arithmetic, and s > u/(1 − u);
- the qualitative speed-over-nose asymmetry;
- "report motors-off and intact − decoy columns".

**Do not rest on:**
- "the ecology is nearly neutral", as a blanket claim;
- any re-reading of RBT-80 or paper 10 through the lottery;
- "83% of work inside the parent";
- the rod sweeper as an eating-geometry exploit;
- PW's per-step margins at G = 10;
- the designed body being "ranked on noise".

**Rule to state:** "Selection above viability is weak when the net income of solvent members is ≳ 2× the living
cost." That is a parameter of each experiment, measurable from its lineage (`adv_p801_births.py`), not a constant of
the simulator.

## 1. C finding 1 and B §4: "the breeding lottery is saturated"

**Verdict: HOLDS-WITH-CAVEAT for the mechanism, WRONG for the RBT-80 reading, OVERSTATED for paper 10.**

### 1a. Is `probe_demography.py` a faithful replica of `Ecology.step`?

Mostly. The rules match `ecology.py:505-548` line for line:
- **Living cost, gain, age:** energy += gain − cost, then age += 1 (`:510-518`).
- **Death:** energy > 0 and age < max_age survive (`:521-523`).
- **Breeders:** energy ≥ 3.0, shuffled (`:527-529`), breeding while `len(alive) < slots` (`:530-531`).
- **Birth cost:** the parent pays 1.0 and the child starts at 1.0 and age 0 (`:537-538`).
- **Initial energy:** 3.0 matches P-801's config, although the dataclass default is 2.0.

It leaves out two things.
- **Crossover mate choice** (`:531-535`, rate 0.3). My replica includes it, and it changes nothing material.
- **A heterogeneous income distribution.** This omission matters (1c). Every resident earns Poisson(1.3) − 0.1, so
  nobody in the replica sits below the living cost. In the committed run, 60% of births do.

### 1b. "About 50 of 58 above threshold" (`probe_queue.txt`)

**HOLDS.** This was re-derived independently in `adv_p801_births.py`, which counts rows with energy ≥ 3 after
births. Lineage rows are written after births (`ecology.py:548` → `_record` → `_log_lineage`).
- Holistic: 57.8 alive, **49.8** at or above threshold.
- Designed: 55.5 alive, 46.1 at or above threshold.

### 1c. "Deaths are nearly all from age (60)", so income buys nothing: **WRONG as stated**

The same committed lineage (`adv_p801_births.txt`) records every complete life born in seasons 50–500.

| P-801 holistic, income quintile | mean income | lifespan | died of age | seasons eligible | children |
|---|---|---|---|---|---|
| Q1–Q2 | −0.18, −0.02 | 1.9, 3.0 | 0 | 0 | **0.00** |
| Q3 | +0.09 | 8.4 | 0 | 1.6 | **0.05** |
| Q4 | +0.85 | 57.4 | 0.95 | 52.7 | **2.29** |
| Q5 | +1.64 | 59.0 | 1.00 | 57.2 | **2.62** |

- **Only 39% of complete holistic lives end by age; for the designed body it is 16%.**
- The majority of children are sub-cost foragers that starve within a few seasons. corr(income, children) is
  +0.71 (holistic) and +0.78 (designed).
- The economy therefore selects **hard on viability**, meaning income above the 0.25 living cost. It selects only
  weakly **above** viability: Q4 → Q5 is +94% income for +14% children.
- C's mechanism is right about the upper tail, which is the "better than good enough" gradient. It is wrong that
  the rule is "nearly neutral" in general.
- Purifying selection against a mutation that pushes a child below the cost is strong. That is exactly the
  selection a *retention* experiment needs.

### 1d. Robustness of "2× never fixes": it holds only in a high-income band

My replica is `adv_demography.py` (`_invasion.txt`, `_income.txt`). It is C's design: 6 mutants among 60, living
cost 0.25 and 400 seasons, with crossover added.

| resident gross income g0 | ×1.25: share / fix | ×2: share / fix |
|---|---|---|
| 0.30 | 0.90 / 0.90 | 1.00 / 1.00 |
| 0.40 | 0.98 / 0.93 | 1.00 / 1.00 |
| 0.50 | 0.75 / 0.23 | 0.995 / 0.94 |
| 0.60 | 0.51 / 0.00 | 0.90 / 0.33 |
| 0.70 | 0.34 / 0.01 | 0.52 / 0.05 |
| 0.80 | 0.23 / 0.00 | 0.39 / 0.00 |
| 1.00 | 0.21 / 0.01 | 0.20 / 0.01 |
| 1.30 (C's cell) | 0.15 / 0.00 | 0.14 / 0.00 (C: 0.15 / 0.00) ✓ |
| 1.50 | 0.12 / 0.00 | 0.10 / 0.00 |
| 3.00 (HP-like) | 0.13 / 0.00 | 0.06 / 0.00 |

- **Capacity** (30 or 120) and **horizon** (1,500 seasons: ×2 share 0.22, fixation 0.11) do not rescue it at
  g0 = 1.3.
- The lottery **is** saturated once resident net income is above about 2× the living cost (g0 ≳ 0.8).
- Below that, starvation and the delay to reach the threshold do the selecting, and the committed rule fixes a
  1.25× forager readily.
- **Corrected statement:** "When the resident population's net income is well above the living cost (committed
  foraging worlds after the first ~50 seasons: g0 ≈ 1.3), the committed lottery gives almost no advantage to
  foraging better than viability. At incomes near the cost it selects strongly."

### 1e. "This probably explains RBT-80's NO VERDICT": **WRONG**

RBT-80's own committed readout (`docs/artifacts/RBT-80-three-seed-report.txt` §1, §4; `RBT-80-within-arm.txt`)
says the opposite.
1. **The seeded arms held the compass.** Plateau carriage was **0.961 / 0.720 / 0.922** against their own
   no-selection floors of **0.515 / 0.497 / 0.522**, at the arms' realised depth. That is +0.45, +0.22 and +0.40:
   selection held it on every seed.
2. **The NO VERDICT came from the comparator.** The drift arm ran at realised depth **5.0** against about 11 in the
   seeded arms. Its floor is therefore 0.681, and it retained 0.71 / 0.75 / 0.64. Seeded − drift compares
   retention at different depths, which paper 8 §2.4 already flags. On seed B there is also structural loss:
   15.2 carriers lost structurally in the seeded arm.
3. **RBT-80's non-carriers are in the non-saturated regime.** They earned **0.079 / 0.644 / 0.468** against
   carriers' 1.22 / 1.06 / 0.97 (`RBT-80-within-arm.txt`). Seed A's non-carriers are below the 0.25 living cost.
4. **RBT-80 is a retention design, not an invasion.** All 60 founders carry the compass. In a retention replica at
   RBT-80's numbers (`adv_demography_retention.txt`: erosion 0.06 per birth, which puts the no-selection floor near
   0.55 at 300 seasons), the committed lottery holds:

   | non-carrier income (carriers 1.05) | committed lottery | energy order | no selection |
   |---|---|---|---|
   | 0.47 | 0.93 | 0.96 | 0.59 |
   | 0.64 | 0.80 | 0.95 | 0.54 |
   | 0.84 | 0.65 | 0.93 | 0.56 |

   The committed rule reproduces RBT-80's observed 0.72–0.96. Energy order would have raised it only modestly.
- C also cites "carriers out-earn non-carriers by +0.4 to +1.1" as a causal income edge. Paper 8 §2.4 says those
  contrasts are observational and mostly present at season 0 (+0.774 / +0.498 / +0.569 before any selection).
- **Corrected statement:** "RBT-80's seeded arms held carriage well above their own no-selection floor under the
  committed lottery. Its NO VERDICT reflects the drift comparator's lower realised depth, not a neutral economy."

### 1f. Paper 10 (HP 9/10, HU 0/10): **OVERSTATED**

- Paper 10's HU window income is about 1.3–1.5, and HP's is about 1.77 higher (`paper-10-held-not-spread.md:356`).
  Both are in the saturated band of 1d, HP more so.
- C's mechanism therefore predicts that HP selects **no more** on the upper tail than HU, if anything less (×2 share
  0.06 at g0 = 3). It cannot by itself make HP the stronger-selecting world.
- The "more births relieves the lottery" route is real only through more starvation turnover (1c's viability
  sieve), and that has not been measured per arm.
- Paper 10 already lists income, births and depth as unseparated (H8). C adds a hypothesis, not a finding.
- **Corrected statement:** "Paper 10 H8's income, births and depth confound stands; the saturated lottery is not
  evidence for a selection-strength reading of HP − HU."

### 1g. B's "2–3× s" against C's "0 → 200/200": consistent, in different regimes

- B's `ecology_s.py` uses μ 0.25, living cost 0.05 and σ 1.16. That is net 0.20 per season with large noise: the
  **near-threshold** regime. There the shipped lottery already selects (Δ +0.2 → 49% from 10% in 150 seasons), and
  richest-first multiplies s by 2–3.
- C's g0 = 1.3 at cost 0.25 is the **saturated** regime. There the shipped s is about 0, so the ratio is unbounded.
- Neither is general, and **neither states its regime.** B's μ/cost pair (0.25 / 0.05) matches no committed foraging
  run, which all use cost 0.25 with gross income 0.6–3.
- **The synthesis should state the rule in terms of net income ÷ living cost.**

### 1h. C's update at 846f913 (`probe_demography_b.py`, `probe_margin.py`)

- The coordinator asked for this head to be checked; it adds B's additive-Δ model "in the committed foraging
  economy".
- The **config** parameters match the committed runs:
  - living cost 0.25, initial energy 3.0, threshold 3, birth cost 1, max age 60 and 60 slots;
  - checked against `runs/RBT-80/seed*/{seeded,control}/config.json` and `runs/RBT-19/P-801/config.json`;
  - paper 10 §2 states the same economy.
- The **income** parameter does not. μ = 1.3 is the mean lifetime score **of the living**
  (`probe_queue.py` averages `fitness` over adults alive each season), which is survivor-weighted.
  - Per birth, P-801's holistic mean lifetime income is about **0.48**: the quintile means in 1c are −0.18,
    −0.02, +0.09, +0.85 and +1.64.
  - 60% of births earn at most 0.27 and starve.
  - RBT-80's arm means were 0.65 (control) to 1.08 (seeded), and its non-carriers earned **0.08–0.64**
    (`RBT-80-within-arm.txt`).
- The model gives every non-carrier μ = 1.3 and so has no viability sieve. That is why it finds that "every
  Δ ≤ +1 item loses ground under shuffle with u 0.15".
- **RBT-80 is the direct counter-example.** Under the committed shuffle, all three seeded arms held carriage far
  above their no-selection floor (1e). My retention replica with RBT-80's measured non-carrier incomes reproduces
  that.
- **Verdict on 846f913's "16× flatter" and "every Δ up to +1 loses ground": OVERSTATED.** They are right for
  a Δ that sits entirely above viability, which is the case for a nose *step* in an already-solvent body. They
  are wrong for any trait whose loss drops the bearer toward the living cost, and a working compass in RBT-80 was
  such a trait.
- `probe_margin.py`'s margins are item 6's subject.

### 1i. What the `breed_order=energy` fix costs (neither audit reports it)

`adv_demography_ne.txt` covers a neutral population, g0 = 1.3, over seasons 200–400.

| rule | distinct parents | mean age at breeding |
|---|---|---|
| shuffle | 137 | **30.6** |
| energy | 71 | **54.4** |

Under hoarding, energy order is a **gerontocracy**:
- the oldest individuals hold the most energy and pay only 1.0 per child;
- the number of parents halves;
- generation time nearly doubles, so realised mutational depth per season about halves.

Depth mismatch between arms is what already sank RBT-80's contrast. So `energy` is not a free fix. Any design that
adopts it must:
- report depth per arm;
- consider `energy_leak` or tickets, which weight income rather than age × income.

"Energy is what the world paid" is true, but under hoarding, stored energy is mostly **age**.

### Also noticed: the drift arm is not quite drift

- RBT-80's drift arms set `birth_threshold 0`, `living_cost 0` and `starvation false`, but the eligibility test
  `energy >= birth_threshold` (`ecology.py:527`) still applies.
- An individual whose cumulative net gain is below −3 (initial energy 3) is alive but can never breed.
- The "no-selection" arm therefore still selects against persistent net-negative workers (flailers).
- It is small for the designed body. It is not zero for a holistic drift arm under a work cost.

## 2. A2: ghost limbs

**Verdict: OVERSTATED.** The numbers reproduce, but the metric does not measure "inside". The filtered set is
also larger than the audit says.

Checkpoints were restored with `scripts/durable.sh restore … rbt-113-{O1,Z1}` at 216/216. Probes:
`phys_ghost.py`, `phys_weld.py`.

### 2a. Collision filtering

- The compiled models have `contype = conaffinity = 1` on every robot geom, `filterparent` on, and no `<exclude>`
  or `<pair>`. Self-collision is on; only the parent filter removes pairs.
- **The audit misses the weld rule.** MuJoCo filters by *weld group* (`body_weldid`), not by body.
- A FIXED connection adds no joint (`world.py:224`, "welded to its parent"). A limb therefore also passes through
  its **grandparent** across a fixed link, and fixed siblings never collide.
- The weld rule matched `d.contact` on 100% of overlapping pairs.

Filtered same-robot pairs (`phys_weld.txt`):

| group | filtered but not parent–child | parent–child |
|---|---|---|
| founders | 419 | 796 |
| U | 852 | 883 |
| D | 362 | 826 |
| C | 1,414 | 1,172 |

- "A child never collides with its parent" therefore understates the filtered set by 45–120%.
- The contact sensor never fires within a weld group either. This bears on A's B6 item.

### 2b. The metric

- `probe_ghost.py` uses `mj_geomDistance`, a true signed distance, not a centre proxy. It reproduces to two
  decimals: embedded at start 0.73 / 0.79 / 0.79 / 0.52, work share 0.65 / 0.85 / 0.83 / 0.55.
- **But sd < −2 cm fires on any tilted attachment.** The child geom starts at the joint on the parent's surface
  (`synthesis.py:263`), so any tilt sinks a corner of it into the parent.

| D line | audit (sd < −2 cm) | child centre inside parent | ≥ 50% of child volume inside | ≥ 10% inside |
|---|---|---|---|---|
| pairs embedded at start | **0.79** | 0.21 | **0.17** | 0.62 |
| share of work | **0.83** | 0.38 | **0.34** | 0.75 |

- In the founders, U and C, only 4–10% of pairs start at least half inside.
- Many of the audit's "embedded" pairs are FIXED joints, which cannot spin: 14 of 57 in the founders, 15 of 45 in
  U and 22 of 70 in C.
- **What makes the D line's work waste is unobstructed rotation, not embedding.**
  - 97% of the D line's work is on children that touch nothing at all.
  - 19–27% is on children that are contact-free and less than 10% inside: rotors spinning in air.
  - 94% is on ball joints, which have no range (`world.py:217`).
- Work attribution is per tick, per actuator whose child is embedded at that tick. There is no double counting, and
  exact per-substep work gives the same figures.

**Corrected statement:** "83% of the D line's work is on joints whose child overlaps its parent by more than 2 cm,
usually a tilted attachment. About 35% is on children genuinely inside (centre inside, or at least half their
volume). 97% is on children touching nothing."

**Consequence for the fix:**
- The ball-joint cone, plus a range on unlimited hinges, is the load-bearing half.
- The outward-hemisphere clamp alone would not stop free spin. It also misses fixed-link passes through
  grandparents.
- Orientation mutation is **unclamped** (`genetics.py:209`): ±π/2 holds only at founding, so the clamp would have to
  act at synthesis, not at genesis.

## 3. A1: the gear table

**Verdict: HOLDS, with small caveats.** Everything was recomputed from the compiled models (`phys_gear.txt`).

**The numbers:**
- **Pioneer:** Σgear/(4M) = 108 / (4 × 15.337) = **1.7605**. Both drive wheels are keyed to the 13.5 kg chassis.
  15.337 kg is under the 15.34 kg budget, so it is unscaled.
- **Holistic D:** 3.574 (maximum 6.347). Rule (b) gives 1.458. Rule (c) at c = 1.77 gives 1.658, with 91.2% of
  members capped.
- **Star hub:** 1860.2 / (4 × 15.34) = **30.3**, and ÷ 3 under (b) = **10.1**.
- **The bound** Σgear ≤ 12M(1 + the most driven children on one part) is correct.

**Caveats:**
- **(c) leaves the Pioneer untouched by a 0.5% margin** (1.7605 against 1.77). Any change to the Pioneer's masses or
  to the budget will cap it. The closing test should assert this explicitly.
- **The power algebra.** A single hinge built exactly as `world.py:202–223` builds one has a no-load speed of 20.000
  rad/s and power 20.00 × gear at every gear (torque motors; damping = 0.05 × gear).
  - **The proportionality holds only for torque actuators.** A velocity servo settles at 7.5 rad/s, with power
    2.81 × gear. A position servo does not spin under constant ctrl.
  - So "power budget ≡ gear budget" is exact only for torque and ball actuators. Ball joints are forced to torque
    (`synthesis.py:258`) and carry 96% of the D line's gear, so the conclusion stands.
  - Servo gains do come from gear (`world.py:268–277`), so "also cap the servos" is right.

## 4. A3: motors-off drift

**Verdict: HOLDS-WITH-CAVEAT.** There is one real error, and the food claim is **OVERSTATED**.

- **Wrong denominator.** "14 of 240" includes 120 designed members, which never move (`probe_passive.txt`). The
  correct figure is **14 of 120 holistic bodies (12%)**.
- **"Off".** The probe replaces `effector_output` (`brain.py:101`; no bias after it), so ctrl = 0 exactly. For a
  servo joint that is still actuated in principle: a position servo pulls toward q = 0, and a velocity servo brakes.
  - A truly limp variant (every actuator gain and bias zeroed after the settle) gives the same result: 14 drifters,
    displacement within 0.02 m, and 0–3 J of work. The caveat is moot in practice.
- **Mechanism.** A 5 s settle cuts drifters from 14 to 5, but some bodies then drift *more* (0.52 m, 0.57 m, and one
  U member 7.30 m, which drifts 0.00 m on flat ground). Part of the drift is rolling on terrain, not settle residue.
- **"Motors-off food matches intact food" is a small-number coincidence.**
  - It is 1 item against 1 over 30 founders, and 3 against 2 in C.
  - Of 9 motors-off eaters, 5 moved less than 0.25 m, so it is mostly **static reach** (A5's clearance-from-root
    mechanism), not drift.
  - With the 5 s settle, motors-off food fell to 0 in every group. This has not been explained.

**Corrected statement:** "14 of 120 holistic bodies drift more than 0.25 m with motors off, and none of 120 designed
bodies do. Motors-off food is 1–4 items over 30 bouts per group, mostly static reach, and is not evidence that drift
buys food."

## 5. B §3: evaluation noise

**Verdict: HOLDS-WITH-CAVEAT.** The size of s holds. The designed body's "0.004" and "ranked on noise" are
**OVERSTATED**: that number is the estimator's floor.

**Method.** RBT-113 O1 was restored with B's command. B's estimator was checked, and U seed 1 was re-scored on 12
fresh draws: terrains 5131+, 40 members per fauna. Outputs are `noise_components.txt` and `noise_resample.txt`.

**How B's repeatability is computed** (`noise.py`):
- sb² = max(var(member means) − sw²/6, 0);
- rep₂ = sb² / (sb² + sw²/2), from 6 draws.

It floors at 0.

| RBT-113 U seed 1 | holistic | designed |
|---|---|---|
| B's rep₂ | 0.14 | **0.004** |
| B's estimator, all 12 of my draws | 0.21 | 0.078 |
| B's estimator on every 6-of-12 subset: median [5–95%] | 0.16 [0.05, 0.28] | **0.031 [0.000, 0.141]**; exactly 0 in **29%** of subsets |
| between-member SD (two-way ANOVA) | 0.56, F = 2.76, p ≈ 0 | **0.21** (B: 0.056), **F = 1.60, p = 0.015** |
| member × draw SD | 1.47 | 0.95 |
| runs eating 0 items | 49% | 45% |
| distinct genomes | 40/40 | 40/40 |

**What this shows:**
- The designed population is not a set of clones, and its genotypic spread is real (p = 0.015).
- 0.004 is a 6-draw ICC on a zero-inflated score, sitting on its floor. It is not a property of the population.
- **Corrected value:** designed rep₂ is about 0.03–0.1, poorly determined. Holistic is about 0.15–0.25.
- Also, "heritable" is the wrong word for this between-member variance: it is not h².

**Repeatability is not what sets s.**
- B's Monte Carlo s is truncation selection on one carrier. It equals i·Δ/σ_P, with i = 1.27 at the top 25%, to
  within about 0.01.
- Setting the between-member SD to 0 hardly moves it: designed, Δ 0.05 gives 0.090 → 0.101.
- The 0.14 / 0.004 headline is therefore decorative. Δ/σ_P is what matters.

**B's own `selection_s` on the re-measured components:**

| Δ | s, holistic | s, designed |
|---|---|---|
| +0.02 | 0.023 | 0.036 |
| +0.05 | 0.056 | **0.090** |
| +0.10 | 0.115 | 0.188 |

**Erosion units.**
- RBT-113 runs with elites 0, so per-child loss u is per-generation loss, and the units match.
- The hold condition is (1 + s)(1 − u) > 1, i.e. s > u/(1 − u). That is 0.098 at u 0.089, 0.18 at 0.15 and 0.39 at
  0.28, so B's "s > u" is slightly lenient.
- The u values are imported from paper 10 and RBT-112. They have not been re-measured for RBT-113's operator.

**Corrected statement:** "At 2 draws, s ≈ 1.27 Δ/σ_P, with σ_P ≈ 0.7 (designed) to 1.2 (holistic). A +0.02 to
+0.05 gain gets s ≈ 0.02–0.09. That is below u/(1 − u) for u = 0.15 or 0.28, and at the boundary for the designed
body at u_Z = 0.089."

## 6. C finding 2 (the flat nose gradient) and the PW proposal

### 6a. "A nose step buys 0–7%, +25% speed buys 12–37%"

**Verdict: HOLDS-WITH-CAVEAT.** The ordering is robust, but the individual percentages are not resolved.

**The grid** (`smell_grid.txt`): C's model was run unchanged on 3 turn limits (0.25 / 0.5 / 1 rad/s) × 3 heading
noises (0.5 / 1 / 2) × 2 worlds, with n = 200 paired seeds and paired-bootstrap CIs.
- **Speed beats the nose step in all 18 cells.**
  - +25% speed: +13 to +40%, with the lower CI ≥ +5.6 points everywhere.
  - k 1→1.4: −0.8 to +7.6%.
  - k 2→2.4: −1.7 to +9.9%.

**Not resolved:**
- At C's calibrated cell (uniform), k 1→1.4 gives +0.0% [−2.0, +2.0] and k 2→2.4 gives +0.5% [−1.8, +3.0]. C's "+1%
  against +5%" cannot be told apart, from each other or from zero.
- C's own two probes give **+12%** (`probe_gradient`) and **+31%** (`probe_proposal`) for +25% speed in the same
  cell. The Monte Carlo spread is about ±10 points.

**The calibration** is flat across neighbouring cells, not a sharp optimum:
- log-error 0.31–0.36 for (0.25, 1), (0.5, 1) and (0.5, 2);
- C's grid stopped at its noise edge.

The conclusion survives this, but the calibration does not pin the regime.

**"Mutation-sized" differs between the two sides:**
- k + 0.4 is one absolute weight σ (`genetics.py:48`) on a signal of about 0.02.
- +25% speed is a relative change in a phenotype. Per B, one gear mutation has a log-ratio SD of about 1.0, so +25%
  is if anything *small* for speed.

The asymmetry is therefore real, and if anything understated.

**Corrected statement:** "Across a 3×3 neighbourhood of the calibration, +25% speed pays +13–40%, and a one-σ nose
step pays about 0–10%. Single values of a few percent are within Monte Carlo error at n = 200."

### 6b. Does the proposed `smell_gain` (centred log contrast) do what C says?

**Verdict: OVERSTATED.** The numbers are for a different G, and the centring has costs C does not state.

**What holds:**
- The model's `intensity` is `simulation.py:492–512` exactly (sum / mean / log).
- Regrowth matches, both instant and delayed (`simulation.py:421–434` and `:443–486`).
- The reading reaches the brain raw as an activation (`brain.py:97–98`).
- Real bodies see a common mode of about 0.55 against a differential of about 0.03, so **the case for centring is
  sound**.

**What does not:**
1. **The model's GAIN is not the proposal's G** (`smell_proposal_check.txt`).
   - The model computes GAIN·(I_L − I_R) on squashed intensities. The proposal is tanh(G·(ln Σ − ln Σ_root)).
   - In sum mode, d ln Σ/dI ≈ 4 at the typical Σ, so model GAIN 10 ≈ proposal G 2.5. G = 2.5 reproduces C's rows:
     PW k6 2.10 against C's 2.16.
   - At the **proposed G = 10**, per-sensor contrasts saturate. In the simulator, median |c| is 0.56–0.64 and p90 is
     0.93–0.95.
   - Then **k 2→2.4 pays only +2–3%**, against C's +8 to +13%.
   - So C's 846f913 claim that "in PW every single step clears B's 0.1 threshold" (`probe_margin.txt`) describes
     G ≈ 2.5, not the proposed 10. At G = 10 the second step is about +0.05 items.
2. **Root-centring zeroes a root sensor for ever.**
   - Every sampled designed body has 3 food sensors, one of them on the root.
   - A single-nose or root-nose body therefore loses all smell.
   - So does the temporal route (a `differentiate` unit on one sensor, which is klinokinesis), and the absolute food
     level that area-restricted search would use.
   - The proposal turns "perception" into "bilateral spatial contrast only". A per-robot running baseline, or a
     centred channel alongside a level channel, avoids this.
3. **"Exact food rules" is OVERSTATED for eating.**
   - The model eats from the centre of mass + 0.15 m.
   - The simulator eats from **any geom centre** within 0.35 m (`simulation.py:466–475`).
   - Real food-sensor spans are 0.39 m (designed) and 0.54 m (holistic).
   - The model under-credits blind swath, which would favour speed further, so the direction of the conclusion
     is safe.
4. **The nose differential.**
   - C's 0.017 holds for C's 0.3 m geometry (simulator: 0.022 designed / 0.018 holistic).
   - Real bodies' own sensors are further apart and read a median of **0.029 / 0.033** (`smell_sensor_ranges.txt`).

**Corrected statement:** "The model's 'gain 10' corresponds to a centred log-contrast G of about 2.5. At G = 10
contrasts saturate and later nose steps pay about 2%. Root-centring deletes root-sensor, single-sensor and temporal
smell. A PW registration should state G, test at least G ∈ {2.5, 10}, and centre on a running baseline rather than
on the root."

## 7. A5: the rod sweeper at net +0.61

**Verdict: OVERSTATED (misattributed).**

- **The geometry holds.** Dims (5, .05, .05) at size 0.3 give a 6.46 m arm (`genetics.py:201`,
  `genotype.py:262`), scaled ×0.57 to 15.34 kg. `max_scale` 1.2 would even allow about 7.75 m.
- **The payoff does not come from length.** One hinge at full throttle with no sensor, on the same terrain
  (`phys_rod.txt` over 10 draws, `phys_rod2.txt` over 20):

| arm length | net / season, 10 draws | net / season, 20 draws | motors-off food |
|---|---|---|---|
| 0.45 m | +0.65 | +0.75 | 0 |
| 0.9–5 m | +0.41 to +0.80 | — | 0.1–0.4 |
| 6.46 m | +0.91 | +0.71 | 0.1 |

The SE is about ±0.2.
- Every rod travels 2–5 m (5–10 m of path): it is a blind, spinning, tumbling body.
- **A founder-sized arm earns the same.** Length adds only static-reach food with the motor off.
- **There is no gradient toward long arms.** "About 20 steps" is about 24 kept improvements, or about 47 dims
  events on that node at `dims_rate` 0.2, and none of the intermediates is rewarded for length.
- Our 6.46 m arm gives +0.71 on the audit's 20 draws, against its +0.61: about 2 items over 20 draws, which has not
  been traced.

**Corrected statement:** "A single constant full-throttle motor, with no sensor, nets about +0.7 per season at any
arm length from 0.45 m to 6.5 m. That is comparable to the holistic U line (0.85 food, less about 0.26 of work).
Long-arm reach is not reached by selection in steps; the allowance is blind tumbling, which belongs with finding
C2/C3 (coverage), not with the eating geometry."

## What the audits missed

1. **Weld-group filtering** (item 2a).
   - Fixed links merge bodies, so limbs pass through grandparents and fixed siblings never collide.
   - The contact sensor is blind inside a weld group.
   - The outward-limb clamp does not address it.
2. **Orientation mutation is unclamped** (`genetics.py:209`). The ±π/2 range of A2's mechanism holds only at
   founding.
3. **The viability sieve is the ecology's real selection** (item 1c).
   - Neither C nor B measured births against income in a committed lineage.
   - This probe reads it in seconds and should be a standard ecology readout: offspring by income quintile, and the
     share of deaths by age.
4. **`breed_order=energy` changes generation time** (item 1i). Any fix that reorders breeders must report realised
   depth per arm.
5. **The drift arm is not quite drift.**
   - RBT-80's drift arms keep the eligibility test `energy >= birth_threshold` (`ecology.py:527`) with threshold 0.
   - An individual whose cumulative net is below −3 is alive but can never breed.
   - This is small for the designed body, but not zero for a holistic drift arm under a work cost.
6. **Survivor weighting in "income".** Every audit quotes the mean lifetime score of the *living* (about 1.3) as
   the population's income. Per birth it is about 0.48 in P-801. Models parameterised on the former lose the
   selection that actually operates.
7. **The measurement precision of the kinematic probes.**
   - n = 200 cannot resolve the few-percent nose steps C tabulates.
   - The "+25% speed" figure moves by 19 points between C's two probes on the same cell.
   - The synthesis should demand paired CIs on any margin it cites.

