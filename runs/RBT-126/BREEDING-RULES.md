# RBT-126 item 3: breeding-rule options in the bodiless replica, with their depth cost

**Recommendation: one flag, `--energy-leak 0.3`.** Each season, energy *above* the birth threshold leaks by 30% before
the season's gain is added, and the season's breeders are taken in descending energy order (the committed shuffle is
kept, so ties still break at random).

- **Its depth cost**, in generations per season against the committed shuffle at the same resident income:
  - **0.90–0.97×** across the saturated band (g0 0.8–3): −3% at g0 0.8–1.3, −9% and −10% at g0 2 and 3.
  - **1.00–1.16×** below it (g0 0.4–0.7).
  - Distinct parents are 0.87–0.92× shuffle's in the band, and the mean age at breeding rises by 0.9–3.2 seasons.
- **For comparison, `energy` order costs 0.55–0.62×** in the same band, with parents halved and breeding age 52–56.
- **What it buys:** a ×1.25 mutant fixes in 0.97–1.00 of runs across the band, where the committed shuffle fixes it
  in 0.00. A ×1.10 mutant fixes in 0.41–0.80.

Every figure here is from the replica, not from bodies. Caveats are listed [at the end](#what-this-does-not-establish).

## The replica

`breeding_rules.py` extends the adversary's `runs/RBT-121/adversary/adv_demography.py`, which is itself an independent
replica of `Ecology.step` (`ecology.py:505-548`). It keeps that replica's rules:
- living cost 0.25, threshold 3, birth cost 1 paid by the breeder, child at energy 1 and age 0;
- initial energy 3, max age 60, staggered founder ages, 60 slots;
- crossover mate choice at rate 0.3;
- gain = Poisson(g) − 0.1 work, so a member's season score is g − 0.1 and its net income is g − 0.35.

**Only the breeders' order differs between rules.** The two leak rules also change the stored energy.

| rule | what it does |
|---|---|
| `shuffle` | committed: the eligible are shuffled and breed in that order while slots are free (`ecology.py:524-529`) |
| `energy` | shuffle, then a stable sort by descending energy (audit C's `--breed-order energy`) |
| `tickets` | the eligible are drawn without replacement with probability ∝ energy (audit C's tickets) |
| `leak:λ` | audit C's leak: *all* stored energy decays, e ← e(1−λ) + gain − cost, and the order is shuffled |
| `leakx:λ` | the leak applies only **above the threshold**, e ← e − λ·max(0, e − 3), before the gain; then energy order. **`--energy-leak λ` is this rule.** |

**Reproduces the adversary.** At g0 1.3 over seasons 200–400, `shuffle` gives 135.7 distinct parents and a breeding
age of 31.2. `energy` gives 72.5 and 54.5. The adversary's `adv_demography_ne.txt` has 137 / 30.6 and 71 / 54.4. The
`shuffle` invasion column matches ADVERSARY 1d within Monte Carlo error: at g0 0.5, ×1.25 gives share 0.77 and fixation
0.18, against the adversary's 0.75 and 0.23.

**Files:**
- measured tables: `depth.txt`, `invasion.txt`, `retention.txt` (the 7 base rules) and `*_x.txt` (`leakx:0.6`,
  `leakx:1.0`);
- small effects: `small.txt` and `small_x.txt`;
- the drift-arm gate cells: `retention_gate.txt`;
- the tables below: `summarise_rules.py` → `rules_tables.md`.

Rerun with `python3 runs/RBT-126/breeding_rules.py depth|invasion|retention|small 200`, adding `--rules …` for the
extra rules. Every cell uses 200 replicates, or 400 for `small` and the gate cells.

## Depth

In a neutral population, where every member earns the same g0, over seasons 200–400:
- **generations per season** is the change in the mean pedigree depth of the living, divided by 200;
- **distinct parents** are counted over those 200 seasons;
- **age at breeding** is the mean age of a parent when it breeds.

"Collapse" means fewer than 50 of 60 alive on average: the rule starves the population out.

**Generations per season,** with the ratio to `shuffle` at the same g0 in brackets:

| rule | g0 0.4 | g0 0.5 | g0 0.6 | g0 0.7 | g0 0.8 | g0 1.0 | g0 1.3 | g0 2.0 | g0 3.0 |
|---|---|---|---|---|---|---|---|---|---|
| shuffle | 0.0315 | 0.0294 | 0.0298 | 0.0303 | 0.0309 | 0.0311 | 0.0318 | 0.0327 | 0.0327 |
| energy | 0.0273 (0.87×) | 0.0218 (0.74×) | 0.0202 (0.68×) | 0.0196 (0.65×) | 0.0193 (0.62×) | 0.0188 (0.60×) | 0.0186 (0.58×) | 0.0181 (0.55×) | 0.0180 (0.55×) |
| tickets | 0.0299 (0.95×) | 0.0271 (0.92×) | 0.0260 (0.87×) | 0.0261 (0.86×) | 0.0258 (0.83×) | 0.0255 (0.82×) | 0.0255 (0.80×) | 0.0254 (0.78×) | 0.0255 (0.78×) |
| leak:0.05 | collapse | 0.0344 (1.17×) | 0.0308 (1.03×) | 0.0304 (1.00×) | 0.0304 (0.98×) | 0.0313 (1.01×) | 0.0322 (1.01×) | 0.0330 (1.01×) | 0.0323 (0.99×) |
| leak:0.2 | collapse | collapse | collapse | 0.0469 (1.55×) | 0.0383 (1.24×) | 0.0331 (1.06×) | 0.0315 (0.99×) | 0.0321 (0.98×) | 0.0332 (1.02×) |
| leakx:0.1 | 0.0331 (1.05×) | 0.0289 (0.98×) | 0.0275 (0.92×) | 0.0268 (0.88×) | 0.0263 (0.85×) | 0.0255 (0.82×) | 0.0253 (0.80×) | 0.0243 (0.74×) | 0.0237 (0.72×) |
| **leakx:0.3** | 0.0364 (1.16×) | 0.0317 (1.08×) | 0.0305 (1.02×) | 0.0303 (1.00×) | 0.0301 (0.97×) | 0.0302 (0.97×) | 0.0307 (0.97×) | 0.0299 (0.91×) | 0.0295 (0.90×) |
| leakx:0.6 | 0.0389 (1.23×) | 0.0328 (1.12×) | 0.0318 (1.07×) | 0.0314 (1.04×) | 0.0310 (1.00×) | 0.0314 (1.01×) | 0.0319 (1.00×) | 0.0316 (0.97×) | 0.0322 (0.98×) |
| leakx:1.0 | 0.0406 (1.29×) | 0.0345 (1.17×) | 0.0327 (1.10×) | 0.0322 (1.06×) | 0.0316 (1.02×) | 0.0322 (1.04×) | 0.0323 (1.02×) | 0.0325 (0.99×) | 0.0325 (0.99×) |

g0 0.3 is omitted: every rule collapses there, including `shuffle`.

**Distinct parents in 200 seasons:**

| rule | g0 0.4 | g0 0.5 | g0 0.6 | g0 0.7 | g0 0.8 | g0 1.0 | g0 1.3 | g0 2.0 | g0 3.0 |
|---|---|---|---|---|---|---|---|---|---|
| shuffle | 179 | 165 | 154 | 147 | 142 | 138 | 136 | 134 | 134 |
| energy | 123 | 86 | 74 | 69 | 68 | 68 | 72 | 79 | 87 |
| tickets | 170 | 159 | 150 | 145 | 142 | 137 | 134 | 133 | 132 |
| leak:0.05 | collapse | 184 | 163 | 152 | 145 | 139 | 136 | 134 | 134 |
| leak:0.2 | collapse | collapse | collapse | 238 | 194 | 155 | 138 | 134 | 134 |
| leakx:0.1 | 157 | 131 | 119 | 112 | 107 | 100 | 96 | 90 | 87 |
| **leakx:0.3** | 177 | 152 | 142 | 134 | 130 | 125 | 121 | 118 | 117 |
| leakx:0.6 | 190 | 163 | 150 | 144 | 139 | 134 | 132 | 130 | 129 |
| leakx:1.0 | 198 | 170 | 155 | 148 | 143 | 138 | 135 | 134 | 134 |

**Mean age at breeding:**

| rule | g0 0.4 | g0 0.5 | g0 0.6 | g0 0.7 | g0 0.8 | g0 1.0 | g0 1.3 | g0 2.0 | g0 3.0 |
|---|---|---|---|---|---|---|---|---|---|
| shuffle | 32.0 | 34.0 | 33.6 | 33.0 | 32.3 | 31.7 | 31.2 | 30.6 | 30.3 |
| energy | 36.3 | 46.0 | 49.5 | 51.3 | 52.3 | 53.5 | 54.5 | 55.4 | 56.1 |
| tickets | 33.6 | 37.3 | 38.2 | 38.5 | 38.7 | 39.2 | 39.2 | 39.2 | 39.3 |
| leak:0.05 | collapse | 29.2 | 32.5 | 33.1 | 32.9 | 32.0 | 31.1 | 30.5 | 30.2 |
| leak:0.2 | collapse | collapse | collapse | 21.2 | 25.9 | 30.1 | 31.5 | 30.8 | 30.3 |
| leakx:0.1 | 30.1 | 34.8 | 36.7 | 37.6 | 38.1 | 39.0 | 39.7 | 40.9 | 42.1 |
| **leakx:0.3** | 27.5 | 31.6 | 32.9 | 33.2 | 33.2 | 33.1 | 33.4 | 33.3 | 33.5 |
| leakx:0.6 | 26.0 | 30.3 | 31.6 | 31.9 | 32.0 | 31.8 | 31.7 | 31.5 | 31.1 |
| leakx:1.0 | 25.0 | 29.0 | 30.6 | 31.2 | 31.3 | 31.2 | 31.1 | 30.8 | 30.6 |

## Fixation: ×1.25 and ×2 mutants across the regime band

This is the adversary's invasion design: 6 mutants with gross income × mult among 60, read at season 400. Each cell
gives the mean share, then the fixation rate. The neutral share is 0.10.

**×1.25:**

| rule | g0 0.3 | g0 0.4 | g0 0.5 | g0 0.6 | g0 0.7 | g0 0.8 | g0 1.0 | g0 1.3 | g0 2.0 | g0 3.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| shuffle | 0.83 / 0.83 | 0.97 / 0.85 | 0.77 / 0.18 | 0.46 / 0.01 | 0.31 / 0.00 | 0.23 / 0.00 | 0.18 / 0.00 | 0.10 / 0.00 | 0.11 / 0.00 | 0.12 / 0.00 |
| energy | 0.83 / 0.83 | 0.99 / 0.99 | 0.99 / 0.99 | 0.98 / 0.98 | 0.99 / 0.99 | 0.99 / 0.99 | 0.99 / 0.99 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| tickets | 0.90 / 0.90 | 0.99 / 0.94 | 0.96 / 0.59 | 0.87 / 0.32 | 0.77 / 0.10 | 0.71 / 0.07 | 0.58 / 0.02 | 0.49 / 0.02 | 0.43 / 0.01 | 0.37 / 0.01 |
| leak:0.05 | 0.55 / 0.55 | 0.95 / 0.95 | 1.00 / 0.96 | 0.91 / 0.48 | 0.63 / 0.07 | 0.32 / 0.01 | 0.20 / 0.00 | 0.13 / 0.00 | 0.10 / 0.00 | 0.10 / 0.00 |
| leak:0.2 | 0.24 / 0.24 | 0.29 / 0.29 | 0.67 / 0.67 | 0.98 / 0.98 | 1.00 / 1.00 | 0.99 / 0.99 | 0.96 / 0.69 | 0.49 / 0.06 | 0.10 / 0.00 | 0.10 / 0.00 |
| leakx:0.1 | 0.85 / 0.85 | 0.97 / 0.97 | 0.98 / 0.98 | 1.00 / 0.99 | 0.99 / 0.99 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| **leakx:0.3** | 0.84 / 0.84 | 0.98 / 0.98 | 1.00 / 0.99 | 0.99 / 0.99 | 0.98 / 0.97 | 0.99 / 0.97 | 1.00 / 0.99 | 1.00 / 0.98 | 1.00 / 1.00 | 1.00 / 1.00 |
| leakx:0.6 | 0.81 / 0.81 | 0.99 / 0.99 | 0.98 / 0.97 | 0.99 / 0.95 | 0.97 / 0.93 | 0.99 / 0.94 | 0.99 / 0.93 | 0.99 / 0.95 | 0.99 / 0.99 | 1.00 / 1.00 |
| leakx:1.0 | 0.76 / 0.76 | 0.99 / 0.99 | 0.99 / 0.98 | 0.99 / 0.94 | 0.98 / 0.93 | 0.98 / 0.84 | 0.96 / 0.80 | 0.98 / 0.88 | 0.99 / 0.95 | 0.98 / 0.98 |

**×2:**

| rule | g0 0.3 | g0 0.4 | g0 0.5 | g0 0.6 | g0 0.7 | g0 0.8 | g0 1.0 | g0 1.3 | g0 2.0 | g0 3.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| shuffle | 1.00 / 1.00 | 1.00 / 1.00 | 0.99 / 0.87 | 0.84 / 0.27 | 0.56 / 0.04 | 0.40 / 0.01 | 0.24 / 0.01 | 0.18 / 0.00 | 0.13 / 0.01 | 0.12 / 0.01 |
| energy | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| tickets | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 0.98 | 1.00 / 0.97 | 1.00 / 0.97 | 0.99 / 0.87 | 0.98 / 0.76 | 0.95 / 0.61 | 0.96 / 0.57 |
| leak:0.05 | 1.00 / 1.00 | 1.00 / 1.00 | 0.99 / 0.99 | 0.98 / 0.94 | 0.91 / 0.42 | 0.63 / 0.07 | 0.29 / 0.01 | 0.17 / 0.01 | 0.10 / 0.00 | 0.12 / 0.00 |
| leak:0.2 | 0.93 / 0.93 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 0.99 | 0.74 / 0.20 | 0.18 / 0.00 | 0.09 / 0.00 |
| leakx:0.1–1.0 | 1.00 / 1.00 in every cell | | | | | | | | | |

**Small effects** (`small.txt` and `small_x.txt`, 400 replicates each, at g0 0.5 / 1.3 / 3.0):

| rule | ×1.00 fixation (share) | ×1.10 fixation (share) |
|---|---|---|
| shuffle | 0.00 / 0.00 / 0.00 (0.10 / 0.10 / 0.09) | 0.01 / 0.00 / 0.01 (0.38 / 0.11 / 0.10) |
| energy | 0.00 / 0.00 / 0.00 (0.08 / 0.10 / 0.11) | 0.49 / 0.69 / 0.85 (0.81 / 0.91 / 0.98) |
| tickets | 0.00 / 0.00 / 0.00 (0.09 / 0.11 / 0.11) | 0.04 / 0.00 / 0.00 (0.57 / 0.22 / 0.20) |
| **leakx:0.3** | 0.00 / 0.00 / 0.00 (0.10 / 0.10 / 0.12) | 0.43 / 0.41 / 0.80 (0.82 / 0.86 / 0.96) |
| leakx:0.6 | 0.01 / 0.00 / 0.00 (0.10 / 0.11 / 0.10) | 0.37 / 0.17 / 0.47 (0.78 / 0.69 / 0.89) |
| leakx:1.0 | 0.01 / 0.00 / 0.00 (0.10 / 0.09 / 0.08) | 0.38 / 0.08 / 0.23 (0.79 / 0.62 / 0.77) |

No rule moves a neutral mutant off its 0.10 share by more than Monte Carlo error.

## Retention of a planted trait at RBT-80's numbers

This follows the adversary's retention design (`adv_demography.py retention`):
- all 60 founders are carriers with gross income 1.05;
- each birth erodes a carrier's child to a non-carrier with probability u = 0.06;
- non-carriers earn gross gn;
- carriage is read at season 300.

The gn values are RBT-80's plateau non-carrier means (`RBT-80-within-arm.txt`): seed A 0.08, seed C 0.47, seed B 0.64.
0.84, and 1.05 (no edge), are added. The replica treats gn as the Poisson mean, so a non-carrier *scores* gn − 0.1;
this is the adversary's convention, kept for comparability.

Each cell is carriage ± SE. The bracket is carriage minus **the same rule's** no-edge floor (gn 1.05), because a
rule's depth cost shows up as a higher floor.

| rule | gn 0.08 | gn 0.47 | gn 0.64 | gn 0.84 | gn 1.05 (floor) |
|---|---|---|---|---|---|
| shuffle | 0.994±0.001 (+0.45) | 0.936±0.003 (+0.39) | 0.817±0.008 (+0.27) | 0.658±0.012 (+0.11) | 0.544±0.013 |
| energy | 0.995±0.001 (+0.32) | 0.959±0.002 (+0.29) | 0.946±0.002 (+0.28) | 0.929±0.003 (+0.26) | **0.670±0.012** |
| tickets | 0.996±0.001 (+0.36) | 0.950±0.002 (+0.32) | 0.912±0.003 (+0.28) | 0.823±0.006 (+0.19) | 0.634±0.011 |
| leak:0.05 | 0.995±0.001 (+0.43) | 0.964±0.002 (+0.39) | 0.892±0.005 (+0.32) | 0.716±0.011 (+0.15) | 0.570±0.013 |
| leak:0.2 | 0.995±0.001 (+0.44) | 0.987±0.001 (+0.44) | 0.973±0.002 (+0.42) | 0.918±0.004 (+0.37) | 0.550±0.013 |
| leakx:0.1 | 0.996±0.001 (+0.39) | 0.959±0.002 (+0.36) | 0.947±0.002 (+0.34) | 0.924±0.003 (+0.32) | 0.603±0.013 |
| **leakx:0.3** | 0.995±0.001 (+0.41) | 0.964±0.002 (+0.38) | 0.947±0.002 (+0.36) | 0.911±0.004 (+0.33) | 0.586±0.012 |
| leakx:0.6 | 0.996±0.001 (+0.43) | 0.966±0.002 (+0.40) | 0.941±0.002 (+0.38) | 0.895±0.004 (+0.33) | 0.562±0.013 |
| leakx:1.0 | 0.996±0.001 (+0.44) | 0.967±0.002 (+0.41) | 0.943±0.002 (+0.39) | 0.893±0.003 (+0.34) | 0.554±0.013 |
| no selection (drift economy, committed gate) | 0.910±0.004 | 0.578±0.012 | 0.570±0.012 | 0.568±0.013 | 0.559±0.014 |
| no selection, gate removed (DRIFT-GATE.md) | 0.565±0.013 | 0.566±0.014 | 0.546±0.013 | 0.559±0.014 | 0.557±0.013 |

- **Under `shuffle`, the margin over the floor falls** from +0.45 to +0.11 as the non-carriers' income rises toward
  the carriers'.
- **Under the energy-ordered rules it stays near +0.3 or more up to gn 0.84.** Under `energy` the floor itself is
  0.67, against 0.54 for shuffle: fewer generations mean less erosion, the depth cost read off as retention.
- **`leakx:0.3`'s floor, 0.586, is within 0.04 of shuffle's.**
- **The drift economy's committed gate is itself the whole of the "no-selection" arm's retention at gn 0.08.**
  Carriage is 0.910 with the gate and 0.565 without it (DRIFT-GATE.md).

## Why `--energy-leak 0.3`, and not the others

- **`energy`:** fixes every ×1.25 and ×2 mutant at g0 ≥ 0.4, and ×1.10 in 0.49–0.85 of runs. Its depth cost is the
  largest of any rule: 0.55–0.62× in the band, the gerontocracy of ADVERSARY 1i.
- **`tickets`:** costs 0.78–0.83× depth in the band. It still fixes ×1.25 in only 0.01–0.07 of runs at g0 ≥ 0.8, and
  ×1.10 not at all above g0 0.5. It is weaker than `leakx:0.3` in the band and dearer in depth.
- **`leak:λ` (audit C's, all energy):** a moving threshold, not an ordering.
  - A member with a steady net n settles at n/λ, so it can breed only if n ≥ 3λ.
  - It selects hard in a narrow band just above that bar: g0 0.5–0.6 at λ 0.05, and 0.7–1.0 at λ 0.2.
  - Below the bar it collapses the population: λ 0.2 at g0 ≤ 0.6.
  - Above the band it is as saturated as `shuffle`: ×1.25 fixes 0.00 at g0 2–3.
  - It is not usable across the regime band.
- **`leakx:λ`:**
  - The leak above the threshold caps the hoard near 3 + n/λ, so the order ranks recent income, not
    age × income.
  - Below the threshold nothing changes, and the leak never takes a member below it, so it starves no one: the
    number alive matches `shuffle` in `depth.txt` at every g0.
  - It does thin the eligible share, because a leaked hoard no longer buffers a bad season. At λ 0.3 the share is
    0.80 against 0.90 at g0 0.8, and 0.95 against 0.96 at g0 1.3. Below the band it thins more: 0.44 against 0.71
    at g0 0.5.
  - λ trades selection on small effects against depth:
    - λ 0.1: depth 0.72–0.85×;
    - λ 0.3: 0.90–0.97×, ×1.10 fixing 0.41–0.80;
    - λ 0.6: 0.97–1.01×, ×1.10 fixing 0.17–0.47;
    - λ 1.0: 0.99–1.04×, ×1.10 fixing 0.08–0.38, with ×1.25 slipping to 0.80–0.88 at g0 0.8–1.3.
  - **λ = 0.3** is the smallest leak whose depth cost stays within 10% everywhere in the band. It still fixes every
    ×1.25 mutant.
  - λ = 0.6 is the alternative when depth parity matters more than small effects.

## The flag (a design; no code in `rabbitstew/` here)

- **`EcologyConfig.energy_leak: Optional[float] = None`, CLI `--energy-leak L`, with 0 < L ≤ 1.** None is the
  committed code path, byte-identical.
- **When set**, in `Ecology.step`:
  1. **Step 2 (`ecology.py:510-518`), before the season's gain is added:** `if e > eco.birth_threshold:
     e -= L * (e - eco.birth_threshold)`, then `e += g - cost` as now. The leak cannot starve anyone, because it
     never takes energy below the threshold, and the threshold is above 0.
  2. **Step 4 (`:524-529`):** keep `rng.shuffle(breeders)`, then `breeders.sort(key=lambda m: -m.record["energy"])`,
     which is stable. The shuffle call is unchanged, so the random stream matches the committed rule's until the
     first birth order differs.
  3. **Record the energy leaked each season** in the history entry (`leaked`), so the energy books still balance.
- **Validation:**
  - refuse L outside (0, 1];
  - refuse it with `living_cost="relative"` or with `--neutral`: a drift arm has no economy to rank by;
  - add it to `UNSHIFTABLE`: the order is fixed for the run.
- **Tests:**
  - a 10-season run with the flag unset is byte-identical to today;
  - with L = 0.3 and threshold 3, a member at energy 10 enters the season at 7.9;
  - three eligible breeders and one free slot give the slot to the richest;
  - a member at energy 2 is not leaked.
- **Registration rule (R5):** an arm that uses it states it, and reports realised generations per season from
  `scripts/regime.py`. Its comparator runs under the same flag, so depth is matched across arms.

## What this does not establish

- **It is a bodiless, one-locus replica.** The mutant's income edge is exact, permanent and additive. Season income
  is Poisson around it. Real bodies have genotype × season noise of σ_P ≈ 0.7–1.2 (R5), heavier tails, and
  correlated traits.
- **λ = 0.3 was chosen on this replica.** It is not tuned on any run's energy distribution. The corpus's median
  energies are in `regime/TABLES.md`. The replica's run from 13 to 79 across g0 0.8–3 (`calibration.txt`).
- **The depth figures are for a neutral population.** Under selection, a rule that fixes a variant faster also
  changes who breeds.
- **Selection on the rule's own noise is not measured**, i.e. a lucky season buying priority. A neutral mutant stays
  at 0.10 under every rule, but that measures drift of a marker, not what a lucky-season premium does to a
  quantitative trait.
- **Nothing here says any committed result would have come out differently under another rule.** That needs runs.

---
_Generated by [Claude Code](https://claude.ai/code)_
