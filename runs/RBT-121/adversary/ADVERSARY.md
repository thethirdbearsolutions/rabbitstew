# RBT-121 adversary: which of the three audits' load-bearing claims hold?

*Adversary for the RBT-121 loophole audit. Read-only on `rabbitstew/`. Every number here comes from a probe in this
folder (`adv_*`, `phys_*`, `noise_*`, `smell_*`, with its `.txt`) or from a committed file cited by path. The
audits reviewed:*
- *A: #396 @ c6dc0c4*
- *B: #395 @ a9a6050*
- *C: #397 @ 791461b*

**Status: partial. Item 1 is complete; items 2–7 follow in later commits on this branch.**

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

### 1h. What the `breed_order=energy` fix costs (neither audit reports it)

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
