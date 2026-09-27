# RBT-121 audit C: ecology and economy

**Question:** does the world pay perception, steering and adaptation more than their cheap substitutes
(coverage, speed, flailing, size, crowding)? Where does the economy reward the substitute?

**Scope:** read-only on `rabbitstew/`. Probes are in this directory; every number below comes from a
file here or a committed file cited by path.

## Corrections after the adversary (#403)

The coordinator accepts all of #403's verdicts (`runs/RBT-121/adversary/ADVERSARY.md` at e9096cb), and so do I. The
statements below replace the corresponding claims in the body. The body is left as written, so the record shows what
was corrected.

1. **Finding 1 (the saturated lottery): HOLDS-WITH-CAVEAT, for the mechanism only.** From #403:
   - "Deaths are nearly all from age" is **wrong**. Only 39% of complete holistic lives in P-801 end by age, and
     16% of designed ones.
   - 60% of births earn at most 0.27 and starve.
   - The economy selects **hard on viability** (income above the 0.25 living cost) and weakly above it: Q4 → Q5 is
     +94% income for +14% children.
   - Corrected statement (#403 1d): *"When the resident population's net income is well above the living cost
     (committed foraging worlds after the first ~50 seasons: g0 ≈ 1.3), the committed lottery gives almost no
     advantage to foraging better than viability. At incomes near the cost it selects strongly."*
   - The rule is a parameter of each experiment, net income ÷ living cost, measurable from its lineage. It is not a
     constant of the simulator.
2. **"Probably explains RBT-80's NO VERDICT": WITHDRAWN (#403: WRONG).**
   - RBT-80's seeded arms held carriage at 0.96 / 0.72 / 0.92, against their own no-selection floors of about 0.52.
   - The NO VERDICT came from the drift comparator's lower realised depth (5.0 against about 11).
   - Non-carriers earned 0.08–0.64, the non-saturated regime.
   - Corrected statement: *"RBT-80's seeded arms held carriage well above their own no-selection floor under the
     committed lottery. Its NO VERDICT reflects the drift comparator's lower realised depth, not a neutral
     economy."* The "carriers out-earn non-carriers" contrast is also observational and mostly present at season 0
     (paper 8 §2.4). It is not an income edge I may cite.
3. **The paper 10 re-reading: WITHDRAWN (#403: OVERSTATED).**
   - Both worlds sit in the saturated band, HP more so, so this mechanism cannot favour HP.
   - Corrected statement: *"Paper 10 H8's income, births and depth confound stands; the saturated lottery is not
     evidence for a selection-strength reading of HP − HU."*
4. **846f913's "16× flatter than B" and "every Δ ≤ +1 loses ground": OVERSTATED.**
   - μ = 1.3 in `probe_demography_b.py` is survivor-weighted (the mean over the living). Per birth, P-801's income is
     about 0.48, and the model has no viability sieve.
   - Those two statements hold only for a Δ that lies entirely above viability: a nose *step* in an already-solvent
     body. They do not hold for a trait whose loss pushes its bearer toward the living cost, as a working compass
     did in RBT-80.
   - B's and my numbers are consistent but sit in different income regimes (#403 1g).
5. **Finding 2 (flat nose gradient, steep speed gradient): HOLDS-WITH-CAVEAT.**
   - Speed beats the nose step in all 18 cells of #403's 3 × 3 × 2 grid.
   - The individual nose percentages (0–7%) are within Monte Carlo error at n = 200. My two probes disagree on the
     +25% speed return (+12% in `probe_gradient` against +31% in `probe_proposal`), a spread of about ±10 points.
   - Corrected statement: *"Across a 3×3 neighbourhood of the calibration, +25% speed pays +13–40%, and a one-σ nose
     step pays about 0–10%."*
   - The calibration is flat across neighbouring cells. It does not pin the regime.
6. **PW `smell_gain`: OVERSTATED.**
   - The model's `GAIN` 10 (on squashed intensities) corresponds to the proposal's centred log contrast at G ≈ 2.5.
   - At G = 10, contrasts saturate.
   - Root-centring deletes root-sensor, single-nose and temporal smell, together with the absolute level that
     area-restricted search needs.
   - My model eats from the centre of mass + 0.15 m, not from any geom centre within 0.35 m. That under-credits blind
     swath, so the bias favours speed, the same direction as the conclusion.
   - 846f913's "in PW every single step clears B's 0.1" described G ≈ 2.5, not the proposed 10.
7. **`breed_order=energy` costs depth (#403 1i).**
   - Under hoarding it is a gerontocracy: distinct parents fall from 137 to 71, and age at breeding rises from 31 to
     54.
   - That roughly halves mutational depth per season, and a depth mismatch is what sank RBT-80's contrast.
   - Any design adopting it must report depth per arm and consider `energy_leak` or tickets (weighting income
     rather than age × income).

### PW restated, with G stated and tested (`probe_gprop.py` / `.txt`)

**The sensor is now the proposal's, not the model's `GAIN`:** each nose reads c = tanh(G · (ln Σ_nose − b)).
- b is a **per-robot running mean** of ln Σ over the robot's noses, with τ = 2 s (the recommended centring).
- Root-centred b is shown for comparison.
- Regime: calibrated steering (turn 0.5 rad/s, noise 1.0), k = 6, v = 0.25 m/s, n = 300 paired seeds.
- Values are in items per season, as paired differences ± SE.

| world | centring | G | blind | k6 − blind | first nose k0.4 − blind | step k1→1.4 | step k2→2.4 | +25% speed (blind) |
|---|---|---|---|---|---|---|---|---|
| **PW** | **running** | **2.5** | 0.69 | **+1.77 ± 0.16** | **+0.18 ± 0.05** | **+0.19 ± 0.04** | **+0.17 ± 0.03** | +0.17 ± 0.05 |
| PW | running | 10 | 0.69 | +1.63 ± 0.15 | +0.36 ± 0.08 | +0.25 ± 0.05 | +0.08 ± 0.02 | +0.17 ± 0.05 |
| PW | root | 2.5 | 0.69 | +1.86 ± 0.16 | +0.18 ± 0.05 | +0.19 ± 0.04 | +0.17 ± 0.04 | +0.17 ± 0.05 |
| PW | root | 10 | 0.69 | +1.99 ± 0.17 | +0.60 ± 0.10 | +0.29 ± 0.05 | +0.05 ± 0.01 | +0.17 ± 0.05 |
| committed HP | running | 2.5 | 0.90 | +2.01 ± 0.17 | +0.14 ± 0.11 | +0.36 ± 0.05 | +0.20 ± 0.04 | +0.36 ± 0.06 |
| committed HP | running | 10 | 0.90 | +1.79 ± 0.17 | +0.44 ± 0.13 | +0.17 ± 0.05 | +0.07 ± 0.02 | +0.36 ± 0.06 |
| committed uniform | running | 2.5 | 0.86 | +0.93 ± 0.07 | +0.09 ± 0.03 | +0.09 ± 0.03 | +0.09 ± 0.03 | +0.19 ± 0.04 |
| committed uniform | running | 10 | 0.86 | +0.92 ± 0.07 | +0.22 ± 0.05 | +0.11 ± 0.03 | +0.05 ± 0.02 | +0.19 ± 0.04 |

**The restated proposal.** PW is the layout (2 patches of radius 0.4 m in a 4 m disc, own-spot regrowth after 60 s,
log smell, decay 1.5) plus a centred log-contrast food channel at **G = 2.5**, centred on a **per-robot running
baseline** (τ ≈ 2 s).
- Following #403, the raw level channel is kept alongside the centred one, so that temporal and absolute-level
  smell survive. This probe does not test that: in the model, a level channel is simply unused.
- **At G = 2.5:**
  - a finished nose is worth +1.8 items per season over blind at equal speed and body;
  - the first weak nose and each one-σ step are worth +0.17 to +0.19;
  - that clears B's ≈ 0.1 threshold and matches a +25% speed step (+0.17).
- **At G = 10:** early steps pay more, but the second step drops to +0.08 (saturation, as #403 found), below the
  threshold.
- **Root and running centring give the same result in this model**, because the model has no root, single-nose or
  temporal sensor. The choice of running rather than root centring rests on #403's argument about real bodies, not
  on this probe.

**What the gprop table changes: the sensor is the lever, and the layout is secondary.**
- With the centred channel at G = 2.5, even the committed HP world gives nose steps of +0.36 and +0.20, against a
  speed step of +0.36.
- The committed uniform world gives steps of about +0.09, against speed +0.19. That is borderline against B's
  threshold.
- So PW's layout matters mainly in the uniform case and for the cost of speed. It is not needed to make the steps
  visible.

**Still model-only.** The confirming test on real bodies is unchanged: RBT-106's prize harness at an installed
weight a = 6, with the centred channel at G ∈ {2.5, 10}. It must state G. Energy-order breeding (item 7) is no
longer a precondition. It is an option whose depth cost must be reported.

## Answer in one paragraph (original, superseded where the corrections above say so)

**The world does ask for perception, but the programme cannot hear it.**
- At the peak, a well-steered two-nose forager eats 2.5–5× a blind one of equal speed in every committed
  world (`probe_world.txt`).
- The path to that peak is flat. From where the populations actually are, one mutation-sized step in nose gain
  buys 0–7% more food, while +25% speed buys 12–37% (`probe_gradient.txt`, `probe_proposal.txt`). The nose
  differential is tiny: median |ΔI| = 0.017 across a 0.3 m body, and the evolved weights stop at about 6.
- Worse, **the ecology barely rewards a better forager at all.** Breeding is a uniform lottery among everyone
  above the birth threshold, and in the committed economy about 50 of 58 individuals sit above it every season
  (`probe_queue.txt`). So a mutant that forages **2× as well** goes from a 10% to a 15% share in 400 seasons
  and never fixes (0/200). One that forages 1.25× as well is indistinguishable from neutral
  (`probe_demography.txt`).
- The same lottery with the breeders taken in energy order fixes the 1.25× mutant in 200 of 200 replicates.

"Perception from scratch: not yet" is overdetermined:
- a flat sensor gradient;
- a steep speed gradient;
- a nearly neutral reproductive rule on top of both.

## Ranked findings

Ranking = (evidence it already shaped a committed result) × (size) ÷ (cost to fix).

### 1. The breeding lottery is saturated, so above the threshold, foraging quality is nearly neutral

**The mechanism** (`ecology.py:524-545`):
- Every living individual with energy ≥ `birth_threshold` (3.0) is shuffled uniformly and breeds in that order
  while a slot is free.
- Slots open only through deaths.
- Energy above the threshold buys nothing except the right to enter the lottery again next season. The birth
  cost (1.0) is small against what the individuals hold.

**Measured in the committed persistent run** (`runs/RBT-19/P-801/lineage.jsonl` → `probe_queue.txt`):

| seasons 50–600 | alive | births / season | at or above threshold after breeding | median energy |
|---|---|---|---|---|
| holistic | 57.9 | 2.1–2.3 | **49–50** | **22.6–23.7** |
| designed | 55 | 3.9–5.3 | 45–48 | 12–17 |

- The living cost (0.25) is a fifth of the mean income (about 1.3). Starvation is rare, deaths are nearly all
  from age (60), and energy is hoarded at about 8× the threshold.
- A lineage's reproductive success is about (seasons spent eligible) × (1 / number eligible). For any forager
  above about 0.5 items a season, that is almost its whole life, whatever it eats.

**The probe** (`probe_demography.py`: a bodiless replica of `Ecology.step`; 60 slots; gains Poisson; 6
mutants planted; 400 seasons; 200 replicates; neutral share 0.10):

| mutant income | committed lottery: share / fixation | energy order | energy-weighted tickets | 20% energy leak / season | living cost = mean income |
|---|---|---|---|---|---|
| ×1.00 | 0.10 / 0.00 | 0.10 / 0.00 | 0.11 / 0.00 | 0.09 / 0.00 | 0.08 / 0.08 |
| ×1.25 | **0.11 / 0.00** | **1.00 / 1.00** | 0.58 / 0.02 | 0.48 / 0.06 | 0.99 / 0.99 |
| ×2.00 | **0.15 / 0.00** | 1.00 / 1.00 | 0.99 / 0.84 | 0.69 / 0.12 | 1.00 / 1.00 |

The ecology's own default living cost (0.05) is the same: a ×2 mutant ends at 0.13.

**Coordination with auditor B (PR #395, finding 4).**
- This is the same mechanism B found independently, and B is credited for it. B's fix is also the right
  form: a stable sort by energy after the existing shuffle, so that the random stream stays byte-identical.
- B's synthetic model uses the EcologyConfig default economy: living cost 0.05, μ 0.25, σ 1.16.
- Every committed *foraging* ecology instead ran living cost 0.25 and initial energy 3.0, at a measured income
  of about 1.3 (P-801).
- `probe_demography_b.py` re-runs B's additive-Δ model in that economy. It keeps B's σ 1.16 and B's erosion
  u 0.15, plants 6 carriers of 60, runs 300 seasons and 200 replicates. Neutral share is 0.10.

| Δ items/season | shuffled: share, s/season | energy order: share, s | shuffled, u 0.15 | energy, u 0.15 |
|---|---|---|---|---|
| +0.05 | 0.10, −0.0001 | 0.35, +0.0051 | 0.03, −0.0048 | 0.17, +0.0022 |
| +0.10 | 0.11, +0.0005 | 0.63, +0.0090 | 0.02, −0.0057 | 0.39, +0.0059 |
| +0.20 | 0.13, +0.0009 | 0.95, +0.0173 | 0.02, −0.0053 | 0.78, +0.0114 |
| +0.50 | 0.18, +0.0021 | 1.00, +0.031 | 0.03, −0.0041 | 0.85, +0.0099 |
| +1.00 | 0.18, +0.0023 | 1.00, +0.024 | 0.04, −0.0036 | 0.86, +0.0072 |

s is a logit-linear fit to the mean share. It under-reads the curves that saturate early.

**The refinement.** In the committed foraging economy, the shuffled lottery is about **16× flatter than B's
default-economy numbers**: at Δ +0.10, s is +0.0005 per season against B's +0.008.
- With B's erosion, **every Δ up to a full extra item per season loses ground** (share 0.02–0.04).
- Energy order restores s of about +0.006 to +0.011 per season under erosion, and holds carriers at 0.39–0.86.
  B's +0.10 cell under erosion (41%) matches this one (39%).
- **The two audits agree on the mechanism and the fix.** This one adds that the committed runs sat in the
  flattest version of it.

**Already shaped a committed result: yes, most likely.**
- **RBT-80 / RBT-65 (paper 5 §2.3, paper 8 §2.4):** the seeded compass arm out-earns its control by
  +0.37 to +0.43 items a season, and carriers out-earn non-carriers by +0.4 to +1.1. Yet HELD came back
  **NO VERDICT**, with seeded − drift carriage of +0.25, −0.03 and +0.29. Under this rule, an income edge of
  30–80% is worth almost nothing in offspring, so that is what this economy predicts.
- **The drift arm:** RBT-79's note that "flattening the economy did not give that run a usable control" reads
  differently once the selected arm's economy is itself nearly flat above the threshold.
- **Paper 10 (HELD 9/10 in HP, 0/10 in HU):** needs re-reading, not retraction. HELD is measured against a
  no-selection bound, so a weak selection makes it conservative. But the patchy world also raised births
  (paper 10 flags this), and more births per season is exactly what relieves the saturated lottery. **Part of
  the HP–HU difference may be selection strength rather than what the compass pays in each world.**
- **Every ecology heritability or yield-response estimate** runs under near-neutral selection above a floor.

**Fix** (behind a flag, off by default so that runs stay byte-identical):
- `EcologyConfig.breed_order = "shuffle" | "energy" | "tickets"`. `"energy"` takes the breeders in descending
  energy and draws from the stream only for ties and mate choice.
- It is not a rank on score: energy is what the world paid. It keeps the "absolute economy" claim.
- A softer alternative is `energy_leak = 0.2` (no hoarding).

**Cost:** about 10 lines in `step()`.

**Cheap test:** `probe_demography.py`. Then a real 150-season ecology with 6 seeded compass carriers
(RBT-80's founders) under `breed_order=energy` against `shuffle`, reading carriage. The prediction is that
carriage rises under `energy` and sits at drift under `shuffle`.

### 2. The sensor gradient is flat and the speed gradient is steep: coverage is the downhill path

**The peak exists** (`probe_world.txt`: a kinematic point forager with the world's exact food rules and smell
function, n = 200, v = 0.25 m/s, turn limit 2 rad/s):

| world | blind best | smell, k = 6 | smell, ideal | ideal ÷ blind |
|---|---|---|---|---|
| default uniform (12, sum) | 1.10 | 3.03 | 4.42 | 4.0× |
| RBT-106 HP (12 in 3 patches) | 1.39 | 6.81 | 8.72 | 6.3× |
| RBT-19 persistent (26 in 3 patches, delay 45) | 2.60 | 10.5 | 13.79 | 5.3× |

At equal speed and equal body, perception pays several-fold. **The world is not what forbids it.**

**Calibrating to real bodies** (`probe_calibrate.txt`):
- The one real-body measurement of a working nose is RBT-106's installed compass at a = 64: ×1.65 in the
  uniform world, ×2.37 in the patchy one.
- Turn limit 0.5 rad/s with heading noise 1 rad/√s at k = 64 reproduces ×2.10 and ×2.67 in the model, the
  closest cell of the grid.
- That is the "realistic" regime used below.

**The path, in the realistic regime** (`probe_gradient.txt`, `probe_proposal.txt`):

| world | blind | smell, k = 6 | +25% speed | nose gain k 1→1.4 | k 2→2.4 | blind at 2× speed ÷ smell |
|---|---|---|---|---|---|---|
| default uniform | 0.81 | 0.95 (×1.17) | **+31%** | +1% | +5% | blind wins, ×1.9 |
| RBT-106 HP | 0.90 | 1.21 (×1.34) | **+37%** | +1% | +4% | blind wins, ×1.5 |

**The reason:**
- The nose differential across 0.3 m is median 0.017 in the committed worlds (sum and log alike; mean mode is
  0.008).
- At the weights evolution reaches (≤ 6.1, paper 5), that moves a turn command by tanh(0.1) ≈ 10% of
  authority.
- Speed, meanwhile, pays linearly: with instant random regrowth the uniform world is a memoryless Poisson
  field, and blind intake ≈ ρ · 2(0.35 + half-span) · v · T.

**Already shaped a committed result: yes.**
- **RBT-113's U line** (ADVERSARY §4): ground covered ×6, items per cell ×1.4, and blind = decoy = intact.
- **Papers 5–6:** the blind mower.
- **RBT-80:** the unseeded control never evolves a compass (0/1,300 genotypes).

**Fix (flagged):** a food-sensor contrast knob, so that the nose differential across a body length is O(0.1–1)
in sensor units rather than 0.02. Options:
- `FoodConfig.smell_gain` applied to a centred reading. A raw multiplier also scales the baseline, so it
  should be centred: for example `tanh(G · (ln Σ − ln Σ_root))`, or a per-robot running baseline.
- A new `smell = "contrast"` mode.

This is the lever the world controls. Turn authority belongs to the body (audit A). The proposal below
(§ "Perception-demanding world") uses it.

**Cheap test:** `probe_proposal.py` (the kinematic model). Then RBT-106's prize harness (installed compass)
at an **evolved-range** weight a = 6 rather than 64, with and without the knob. The prize should become
positive at a = 6 only with it.

### 3. Work is priced so low that moving is always profitable and speed is never priced

- **The work cost is 0.03 per kJ.** Paper 5's season-100 holistic best walked 11.9 m on 4.8 kJ for
  2.25 items. That is 0.19 items per metre against 0.012 of work per metre: **a 16:1 return on moving**.
  - The RBT-113 U line took 0.91 items for 0.14 of work.
  - The Pioneer took about 1 item for 0.6 (about 20 kJ).
- **Break-even price for lump coverage** is about 0.47 per kJ, 16× the current one.
- Work grows with speed but intake grows linearly with it, so under 0.03 the optimum speed is "as fast as the
  body can go". The price only registers flailing: RBT-113's D line burned 1.52 of work (about 51 kJ) per
  15 s.
- **The RBT-113 D line shows it prices waste. It does not show it prices coverage against steering.**

**Could affect:** anything that reads "held" or "pays" as net yield. A nose's value is measured against a
free alternative.

**Fix (flagged):** `FoodConfig.work_cost` raised in a new world, or `work_exponent > 1` (charge ∝ power²).
Either way:
- blind coverage's optimum speed becomes interior;
- a founder cohort stays solvent, with the living cost recalibrated as in `foraging-world.md`'s procedure.

**Cheap test:** a blind straight mover's net yield against gait amplitude for 3 founders (existing bodies, a
speed sweep), at 0.03 and at the proposed price. The optimum should move from the edge of the range into its
interior.

### 4. Eating from any geom centre makes span and flailing a substitute for steering

`simulation.py:466-475`: an item is eaten when **any** geom centre comes within 0.35 m in xy.
- Blind intake scales with the swept width 2(0.35 + reach). Paper 6's null found that body width multiplies
  the path-replay yield by ×1.54–2.87.
- Limbs that thrash sweep ground the body never crosses. RBT-113's D line ate 2× its control (0.179 against
  0.065) purely as a by-product of flailing.
- This is the size and flailing substitute, and it acts across bodies: the holistic body can grow reach, the
  designed body cannot.

**Fix (flagged):**
- `FoodConfig.eat_from = "any" | "root" | "sensor"`: only the root part, or only parts that carry a food
  sensor, eat. This makes the mouth the nose.
- And/or `eat_max_speed`: a part eats only while its xy speed is ≤ v_eat (handling). That kills thrash-sweeping
  and decouples speed from intake.

**Cheap test:** replay RBT-113 D- and U-line members under `eat_from=root`. The D line's food excess over C and
the U line's items per cell covered should both fall, and the Pioneer should be unaffected (its nose parts are
its eaters).

### 5. Instant random regrowth: a memoryless world with no depletion, so no competition and nothing to learn

- With `regrow_delay = 0`, an eaten item reappears uniformly at random (outside 0.8 m of any robot). The
  density never falls.
- New ground always pays ρ per unit area, and coverage never exhausts.
- In groups of four, no robot's eating costs any other a thing. The "shared food" of the ecology is not shared,
  and **solo and group scoring coincide** except for collisions and the clearance rule.
- There is nothing to adapt to within a season: no depletion, no gradient that changes, no patch to leave.
- The clearance rule moves regrowth away from occupied ground, which rewards travel further.

**Crowding tricks:** none pay in this world, because there is no rivalry to exploit.
- In the persistent world (`regrow_delay` 45 s, arenas carried across seasons), depletion is real. There,
  interference competition becomes possible:
  - reach wins races to an item (finding 4);
  - a body with an `agent` sensor can tail a conspecific into a patch (kleptoparasitism);
  - one group's harvest lowers the next group's crop (arena luck, random, not exploitable).
- **Not probed; flagged as the next audit target** if the persistent world becomes the default.

**Fix:** no code. Make `regrow_delay > duration` (own-spot regrowth) part of any perception experiment, as the
proposal does.

**Test:** `probe_world.py` rows 3 and 4 against 1 and 2.

### 6. Exploding refunds the work bill (small; no evidence of use)

- `food_score` returns 0 for an exploded robot (`simulation.py:524-526`).
- For a flailer whose work exceeds its food (net < 0), E[gain] = (1 − p) · net + p · 0 **rises** with the
  explosion probability p. The forfeit is a floor, not a penalty.
- It does not arise under the current selection for food. It would under a steep work price (finding 3's fix)
  or under D-line selection.

**Fix (flagged):** forfeit = min(0, net at the last stable tick), or the season's living cost doubled.

**Test:** count exploded rows with negative pre-explosion net in any ecology lineage.

### 7. Measurement: every yield metric credits coverage as foraging

- `_eat`, `food_score`, `realised_heritability` and the ecology's gain count items however they were met.
- Perception is attributed only by separate instruments:
  - lesion and decoy (`paired.py`, RotatedSmell);
  - `forage_null`, which replays a robot's own path.
- RBT-113 had to discover coverage after the fact (ADVERSARY §4).
- PAYS (RBT-106) is sound as a ceiling measure: an installed compass with a phantom-smell control. But it
  measures what a *working* nose pays, not whether evolution can reach one (finding 2).

**Fix (no scored code):** any result that says "foraging", "food-dependent" or "yield" should report two
columns beside the raw yield:
1. **intact − decoy** per member (ADVERSARY §4's protocol);
2. **items per new 0.35 m cell covered**.

The label "foraging" then requires intact − decoy > 0.

**Test:** apply both columns to RBT-113's U line. They should reproduce ADVERSARY §4 (≈ 0, ×1.4).

### 8. Smaller items

- **Living cost defaults disagree.**
  - `EcologyConfig.living_cost` defaults to 0.05, calibrated on the solo closeness challenge (README).
  - Every foraging run sets 0.25.
  - `foraging-world.md:31-33`'s example uses 0.1 and 0.05.
  - None of these binds against a 1.3 income. This belongs with finding 1.
- **Age and demography routes:**
  - no senescence cost;
  - no benefit to dying early;
  - a child starts at 1.0 (the birth cost) and needs +2 net to breed.
- **Solo benchmark against group ecology:** equivalent in the instant-regrowth world (finding 5). They differ
  only in persistent arenas.
- **Salmon (2003):** the origin of "holistic/embodied evolution". It says nothing about the energy economy
  (`docs/origins/README.md:15-17`), so nothing in this design is fixed by it.

## Perception-demanding world (proposal)

**Parameter set PW.** Every item is a flag, and everything else is at its committed value:

| knob | committed | PW | why |
|---|---|---|---|
| `food.patches` / `patch_radius` | 0 or 3 / 0.6 | **2 / 0.4** | concentrated food: blind lines miss patches, and a nose finds them |
| `food.radius` | 3.0 | **4.0** | more empty ground between patches, so coverage wastes more of its path |
| `food.regrow_delay` | 0 (instant, random) | **60 s** (own spot, longer than the bout) | depletion: no memoryless Poisson field, and a patch empties (finding 5) |
| `food.smell` / `decay` | sum / 1.0 | **log / 1.5** | the patches are smellable from further off |
| **new** `food.smell_gain` (centred contrast) | none (1) | **10** | the nose differential reaches the range evolved weights can use (finding 2) |
| items, value, eat_radius, duration | 12, 1, 0.35, 15 s | unchanged | |

**Recommended with it** (not in the probe's numbers):
- `eat_from = root|sensor` (finding 4);
- `breed_order = energy` (finding 1), without which no world helps;
- a living cost recalibrated to PW's founder income.

**The margin** (`probe_proposal.txt`: n = 200 solo bouts per cell; realistic regime, calibrated to RBT-106;
link gain k = 6, the evolved ceiling; v = 0.25 m/s; same body and same speed):

| world | blind best | smell | smell ÷ blind | +25% speed | nose k 1→1.4 | nose k 2→2.4 | smell ÷ blind at **2× speed** |
|---|---|---|---|---|---|---|---|
| committed uniform | 0.81 ± 0.07 | 0.95 ± 0.08 | 1.17 | +31% | +1% | +5% | 0.54 |
| committed HP (RBT-106) | 0.90 ± 0.14 | 1.21 ± 0.16 | 1.34 | +37% | +1% | +4% | 0.65 |
| uniform + gain 10 | 0.81 | 1.83 ± 0.09 | 2.25 | +31% | +10% | +11% | 1.03 |
| HP + gain 10 | 0.90 | 2.90 ± 0.21 | 3.23 | +37% | +16% | +8% | 1.55 |
| PW world, gain 1 | 0.59 ± 0.12 | 0.96 ± 0.17 | 1.64 | +16% | +4% | +7% | 0.78 |
| **PW (gain 10)** | **0.59 ± 0.12** | **2.16 ± 0.22** | **3.66** | **+16%** | **+4%** | **+13%** | **1.73** |
| PW, gain 20 | 0.59 | 2.27 ± 0.22 | 3.85 | +16% | +23% | +6% | 1.82 |

**Reading:**
- In PW, the evolved-range nose out-earns a blind body of equal speed and body **3.7×**. It even beats a
  blind body going **twice as fast** by 1.7×.
- One mutation-sized step in nose gain now pays about as much as +25% speed (+4 to +13% against +16%). In the
  committed worlds it paid 1–5% against 31–37%.
- **The sensor gain is the larger lever; the world layout is the second.**
  - PW's layout alone takes ×1.17 → ×1.64 and halves the return on speed.
  - The gain alone takes it → ×2.25.
  - Together they reach ×3.66.

**In auditor B's units** (PR #395, finding 3: at 2 draws, a gain must be ≥ about 0.1 items per season to
out-select the operator's erosion). `probe_margin.txt`: n = 300, one 15 s bout = one season, calibrated regime:

| world | blind | full nose (k 6) − blind | first weak nose (k 0.4) − blind | one step k 1→1.4 | one step k 2→2.4 |
|---|---|---|---|---|---|
| committed uniform | 0.88 | +0.19 | **+0.003** | +0.007 | +0.017 |
| committed HP (RBT-106) | 1.03 | +0.44 | **+0.033** | +0.017 | +0.037 |
| **PW (gain 10)** | 0.49 | **+1.75** | **+0.22** | **+0.20** | **+0.17** |

- In the committed worlds, only a *finished* nose clears B's 0.1 threshold. Every step on the way to it is worth
  0.003–0.037 items, which is below the threshold at 2 draws and near it even at 8.
- In PW, **the first weak nose and every single step clear it by about 2×**, and a finished nose clears it 17×.
- So PW needs no extra draws for the steps to be visible. B's `--draws` table stays the fallback for the
  committed worlds.
- Under the shuffled breeding rule, even +1.75 is not enough (see finding 1's B table), so PW must run with
  `breed_order=energy`.

**Blind income drops** (0.59 against 0.81 items per bout), so the living cost must be recalibrated so that
founders stay solvent.

**Confirming test on real bodies:**
- RBT-106's prize harness in PW at an installed compass weight of **a = 6** (not 64). Predicted prize > 0 with
  the interval excluding zero; at a = 6 in the committed HU it should not.
- Then a 150-season ecology in PW with `breed_order=energy`, unseeded. The target for "perception from
  scratch" is intact − decoy > 0 in the living population (finding 7's column).

## Files

| file | what |
|---|---|
| `probe_world.py` / `.txt` | kinematic forager with the world's exact food and smell rules; blind against smell at equal speed in the committed worlds |
| `probe_gradient.py` / `.txt` | turn authority and heading noise; marginal returns of nose gain against speed |
| `probe_calibrate.py` / `.txt` | calibration of the steering regime to RBT-106's installed-compass prize |
| `probe_demanding.py` / `.txt` | the first world sweep (unit sensor gain) |
| `probe_proposal.py` / `.txt` | the proposed world against the committed ones, realistic regime |
| `probe_queue.py` / `.txt` | the saturated breeding lottery, measured in RBT-19 P-801 |
| `probe_demography.py` / `.txt` | mutant fixation under the committed and candidate breeding rules |
| `probe_demography_b.py` / `.txt` | auditor B's additive-Δ model (PR #395) re-run in the committed foraging economy |
| `probe_gprop.py` / `.txt` | the PW sensor as proposed (centred log contrast, running or root baseline) at G ∈ {2.5, 10} |
| `probe_margin.py` / `.txt` | smell margins in items per season, against B's 0.1 threshold |

**Caveat:** the foraging probes are kinematic. They measure what the *world* pays for a steering policy, not
what a body can do. The steering regime is calibrated to one real measurement (RBT-106). The confirming test
for each fix is named under it, and uses real bodies.
