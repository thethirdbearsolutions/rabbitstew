# RBT-116 pre-registration (DRAFT): the extradimensional bypass. Do holistic bodies cross the compass valley more readily than the Pioneer?

*Designer's **draft**, 2026-09-27, written under RBT-115 (reason (c) of the 2005 proposal). **Design only; no arm may
run.** Four things gate any arm:*
- *RBT-120's motor budget, merged;*
- *RBT-121's synthesis, and auditor C's perception-demanding world (§4);*
- *a design adversary on this file;*
- *the coordinator's ruling.*

*Nothing here was simulated. The only computation is `power.py` → `power.txt`, a pure-Python caricature of the readout
(§7). Every number from earlier work is cited to its committed file. Places this draft cannot settle are marked
**[OPEN]**, with the default it will use if nobody overrides it.*

**The question.** Conrad's (1990) extradimensional bypass says that extra dimensions in the search space open ridges
around valleys that are impassable in a lower-dimensional one. For evolved bodies, those dimensions are body shape
and the number and placement of sensors. The compass strand has measured one such valley precisely, but only on the
Pioneer:
- a lone food sensor wired to the wheels spins the robot, costing −1.502 items per bout [−1.614, −1.375], and 0 of 7
  robots improved (paper 8, table at L167–172);
- the parts must arrive together, with the right signs;
- the operator proposes the right shape in 84 of 200,000 lineages, and its direction is a coin flip: 30 compass
  against 28 anti (paper 8, L324, L361–372);
- correctly signed, paying proposals arrive at about 1.6–1.9 × 10⁻⁵ per lineage (paper 8, L606–612).

**The bypass predicts that holistic bodies cross this valley where the fixed body cannot.** This design asks whether
they do, with the same selection, the same worlds and the same instrument on both bodies.

**The design in one paragraph.**
- **The instrument (§1).** A *behavioural* definition of crossing, identical on any body:
  - the genome gains food from the *information* in smell: intact against a rotated-smell decoy, as in RBT-97 and
    RBT-104;
  - it moves *up the real gradient* more than under the decoy (a chemotaxis index on its centre of mass);
  - the lesion is reported beside both.

  A body with no food sensor scores exactly zero, by construction.
- **The quantity (§2).** How readily steering appears and is held under selection:
  - both bodies start at their own **coverage peak**: RBT-113's default-operator and Z up-line finals, 24 start
    pairs;
  - they then evolve under imposed truncation on net yield, in `evolve`, in a world where perception pays;
  - both faunas ride in the same run, so every generation's worlds are shared;
  - the readout is the time-averaged share of members that steer, corrected by a matched null line, paired by seed.
- **The world (§4).** Auditor C's perception-demanding world by default. RBT-106's patchy world is the placeholder.
  Either must pass a registered world gate before launch.
- **The nulls (§5).** Per seed:
  - **N:** the same selection, but in a world whose smell is a rotated decoy, so smell carries no information;
  - **C:** random parents, which gives the mutation-only proposal rate.
- **Verdicts (§6).** Five outcomes, each fixed before any data:
  - HOLISTIC MORE READILY;
  - PIONEER MORE READILY;
  - NEITHER CROSSES (bounded);
  - NOT MORE READILY (EQUIVALENT);
  - INCONCLUSIVE.

  **NEITHER CROSSES is the expected clean "no".** The Pioneer's prior is at the floor, and the bypass predicts
  specifically that holistic bodies leave it.
- **Power (§7)** at 24 units:
  - under the null (both at the Pioneer's prior), NEITHER CROSSES 0.91 and false HOLISTIC 0.007;
  - a bypass in which half the holistic lines cross is detected at 0.89;
  - a bypass in which a quarter cross is detected at 0.34. This is the design's weak spot, and it is stated.
- **Motor budget (§8).** RBT-120's budget is ON in every run, probe and gate.
- **Cost (§9).** About 90 CPU-h: 24 arms, two per session, 12 sessions of about 2–2.5 h.

---

## 1. What "crossing the valley" means, on any body

### 1.1 Why not the compass instrument

The existing instrument cannot be used as it stands:
- The compass is a routed wiring motif, a global unit fed ± by the two wheel noses and driving both drive
  Effectors.
- It is detected by a structure predicate and an own-link small-signal gain (`runs/RBT-91/structural_rate.py:76–165`).
- Every step assumes the Pioneer's layout: `_wheel_noses`, `drive_effector_units` ("Pioneer-shaped bodies only",
  `rabbitstew/fixed.py:218–225`), and the antiparallel wheel axes that make the effector *sum* the steering axis.
- RBT-103 found that `unit_indices` raises on every holistic champion (REPORT.md L211–215).

A holistic body can steer in ways the motif does not name:
- two noses on Parts of different Nodes, read through a global differencing unit;
- a nose on a swinging limb, sampling the field actively;
- a lone nose read through a `differentiate` unit while the body moves, which is temporal klinotaxis
  (`brain.py:90–93`);
- an asymmetric gait whose turning rate a single nose modulates.

**Any wiring definition would either miss these or reward look-alikes. The definition is therefore behavioural.**

### 1.2 The probe battery (`steer.py`, to be written after the ruling; specified here)

**One genome, one fixed battery of solo seasons.** The battery uses:
- the registered world (§4), with the motor budget ON;
- a random start, with the terrain and start seeds fixed in the file, identical for every genome, line, fauna and
  generation.

Three conditions are run on the same draws:

| condition | the `food` sensors read | everything else |
|---|---|---|
| **intact** | the real field | unchanged |
| **decoy** | the **live** layout rotated about the world origin by θ, uniform in [30°, 330°], drawn per draw from a fixed stream | unchanged: eating, regrowth, depletion and the real items |
| **lesion** | 0 | unchanged |

- **The decoy is RBT-97's `RotatedSmell`** (`runs/RBT-97/mechanism.py:80–100`), promoted into the package (§3.3).
  - It keeps the item count, the patch geometry and the depletion, and removes only the correlation with where the
    food is.
  - It replaced a static decoy that biased the reading because it never depletes (paper 8, L528–545).
  - The arena and the patch centres are discs about the origin, so the rotation maps the field's distribution to
    itself.
- **RBT-113's `probe_food.py` mirror** is the 180° special case, and is not used. A single fixed angle lets a body
  whose travel correlates with its start position read a structured decoy.
- **Only `food` is patched.** The `agent` smell reads 0 solo in every condition.
- The patch is on the *field*, not the wiring, so it is identical on any body.

**Per season it records:**
- `food`: items eaten;
- `work`: work cost, in yield units;
- **the chemotaxis index T.** Let v be the horizontal velocity of the robot's centre of mass at each control tick,
  and ĝ the unit gradient of the **real** smell field at the centre of mass. The field is the same sum of
  `exp(−d/decay)` terms that `_intensity` squashes; the squash is monotone, so it does not change the direction. The
  gradient is computed analytically. Then:

  > T = Σ |v| cos∠(v, ĝ) / Σ |v|, over ticks with |v| > 0.05 m/s

  - T is the speed-weighted share of the path run up the real gradient, and lies in [−1, 1].
  - Under the decoy, T is still computed against the **real** field.
  - A body that follows the decoy therefore reads T ≈ 0 there.

**Why T as well as food.** Food gain from smell alone passes *kinesis*: slowing down or speeding up with intensity,
without turning. RBT-106's adversary found 26 of 70 compass-lesioned Pioneers moving by ≥ 0.25 items between real
and decoy smell (F6). T separates kinesis from steering:
- **orthokinesis** changes the weights of path segments, not their headings, so T is unchanged in expectation;
- **klinokinesis and klinotaxis** bias the heading toward the source, so T rises. That is directed turning, which is
  what the ticket means by the compass.

### 1.3 The individual call

The battery runs in two stages, so that sensorless and inert bodies cost little:
- **Stage 1 (screen):** 4 draws, intact and decoy only.
  - A genome passes the screen if its mean paired F₁ = food_intact − food_decoy is > 0.
  - Stage-1 draws are **not** reused in the call.
- **Stage 2 (call):** 16 fresh paired draws, all three conditions, for screened genomes only.

Per genome, over the 16 stage-2 draws:
- **F** = mean(food_intact − food_decoy), the food gained from smell *information*, in items per season;
- **ΔT** = mean(T_intact − T_decoy);
- **L** = mean(food_intact − food_lesion), reported only.

**A genome STEERS** iff all of the following hold:
1. F ≥ **F_MIN = 0.25** items per season, and the one-sided 95% t lower bound on F is > 0.
2. The one-sided 95% t lower bound on ΔT is > 0.
3. **The zero-count veto:** at most half of the 16 paired draws have food_intact = food_decoy exactly
   (RBT-104 `function.py` L164–174).

**A genome is SMELL-USE** if 1 and 3 hold but 2 fails: it uses smell without directed turning. This is reported, and
it is **not** a crossing. **Otherwise it is NONE.**

**Why F_MIN = 0.25.** It is:
- about the size of kinesis noise between real and decoy smell (RBT-106 F6);
- about half of the smallest *paying* compass prize the strand measured: the routed motif at w = 16 gained +0.277
  in the uniform world (paper 8, L487–491), and a = 32 gained +0.887 in the patchy world (`runs/RBT-106/prize.txt`).

**[OPEN] F_MIN is absolute, in items.** A body with a lower base income may gain fewer items for the same steering.
The adversary should attack this. The alternative, max(0.25, 0.2 × food_intact), is pre-computed in the readout
and printed beside the call, but it is not the call.

### 1.4 Coverage is rejected, by construction and by control

- **A body with no food sensor** runs byte-identical intact, decoy and lesion seasons. So F = ΔT = L = 0 exactly, the
  zero-count veto fires, and it is NONE. That is the ticket's "a blind body that eats by sweeping must score zero",
  and it is checked on every such genome (§5.3, control I1).
- **A body with noses it does not use** has F and ΔT of 0 in expectation. Its false-STEERS rate is measured on
  RBT-113's up-line finals of both faunas, the programme's certified coverage foragers (ADVERSARY §4), and gated at
  ≤ 0.05 (§4.2, G4).
- **A body that eats by kinesis** fails condition 2 and is SMELL-USE.

### 1.5 From individuals to lines

- **Share.** At a probe generation t, the share of a line is the fraction of its **M = 16** probed members that
  STEER. The members are drawn by a fixed rng from that generation's saved population.
- **A_f.** Per unit (§2.2) and fauna f:

  > A_f = mean over t ∈ {12, 24, 36, 48} of [share_U(t) − share_N(t)]

  That is the **time-averaged, null-corrected share that steers**. "More readily" means sooner and more often, and a
  time average rewards both. It also still ranks two faunas that both reach the ceiling by when they got there.
- **A line has CROSSED** if, at generation 48, share_U ≥ 0.25 and share_U − share_N ≥ 0.25.
  - This means 4 or more of 16 members steer, 4 or more above the null line.
  - It is the line-level count used for the floor verdict.

## 2. The measured quantity, and why

### 2.1 The three candidates

| candidate | what it measures | verdict |
|---|---|---|
| (i) the proposal rate under mutation alone | whether steering genomes are *near* the population in the operator's geometry | **secondary** (the C line, §5.2) |
| (ii) the rate at which steering appears and is held under selection | proposal × conversion: the bypass's operational prediction | **primary** |
| (iii) the depth of the valley on each body | the fitness cost of the intermediate steps | **descriptive** (§6.4) |

**Why (ii) is primary.** Conrad's claim is about *ridges*: paths along which fitness does not fall. A high proposal
rate into a deep valley does not cross it, and a shallow valley with no proposals is not crossed either. Only
appearance *under selection* integrates both, which is the sense of "more readily" in the ticket.

**Why (iii) is only descriptive.** Depth needs the intermediate steps to be identified, and on an arbitrary body they
can only be identified by a wiring motif, which §1.1 rules out. The behavioural proxy (§6.4) is the net yield of
SMELL-USE and wrong-signed members against NONE members. It is reported, not tested.

**Why (i) is secondary.** It is cheap, because the C line rides along. But on its own it cannot distinguish a
bypass from a nearby cliff.

### 2.2 Why `evolve` with truncation, not the ecology, and not a plant

**The ecology cannot power this.**
- Selection on a planted, paying compass there is s = 0.01, with a 95% interval of [0.00, 0.08] (RBT-112
  `READOUT.md`; `instrument.txt` L54).
- Unseeded, the Pioneer's expected de novo arrivals are **about 0.26 across all ten 600-season arms combined**, not per
  arm (`runs/RBT-102/REPORT.md` L140–142), and about half of them would be wrong-signed.
- A zero there becomes informative only at about 184,000 genomes (paper 10, L236–239).
- The ecology also couples the world to births, density and depth (RBT-106 H8), so a world that pays more changes
  more than the prize.

**`evolve` with RBT-113's truncation hook has what this needs** (`--truncation 0.25 --line up|down|control`):
- selection intensity of about 1.27;
- discrete generations;
- solo scoring;
- byte-exact resume;
- both faunas in one run, so that every generation's worlds are shared between the bodies.

**The start is each body's coverage peak**, not random founders, and not a plant.
- **Where the starts come from.** RBT-113 selected both faunas up on the same currency (solo net yield), in the same
  worlds, for 24 generations. Both learned to eat by moving, not by smelling:
  - holistic U line: intact 0.854, blind 0.913, decoy 0.934;
  - designed U line: intact − decoy +0.02 (ADVERSARY §4).

  **These final populations are the valley floor**: the local peak from which the bypass has to find a ridge.
- **Units.** 12 default-operator starts (`O1/1` … `O4/12`) and 12 Z starts (`Z1/Z1` … `Z4/Z12`), each a pair
  (holistic, designed).
  - The Z holistic lines are independent replicates (salt 1).
  - The Z designed lines evolved under frozen global biases. As starting populations they are simply 12 more coverage
    foragers.
  - Every unit in this design runs the **default** operator. Start type (O or Z) is a registered sensitivity split
    (§6.3).
- **What this matches.** History, selection and currency: a behavioural match, not a structural one. That is the
  only kind of match two different body spaces admit.
- **What it does not match.** The holistic starts carry fewer noses (39% have any food sensor), and the Pioneer
  always has three.
  - This is not corrected. Acquiring and placing sensors *is* one of the bypass's extra dimensions.
  - It is reported as the share of each fauna's members with ≥ 2 food sensors on distinct Nodes, at every probe.
- **Why not plant.** Planting cannot be made identical:
  - the routed motif exists only on the Pioneer's layout;
  - a hand-built holistic compass would be one body chosen by the designer;
  - planting measures *holding*, not *crossing*. The strand already knows the Pioneer holds a paying compass in the
    patchy world (RBT-106 HP: 9 of 10 HELD).

  **Planting is used only where it is honest: as the instrument's and the world's positive controls (§4.2).** The
  enrichment in this design is strong truncation selection, the coverage-peak start, and a world where perception
  pays. None of the three favours either body by construction.
- **[OPEN] A random-founder start (R).** It is RBT-113's own start, and would allow the bypass to run through a body
  built from scratch. It is **not in this wave**, because of its cost (another 70+ CPU-h). If this design reads
  NEITHER CROSSES, R is the natural next test, and the registration says so.

**The Pioneer's expected floor.** A 48-generation line of 40 has about 1,920 births. At about 2 × 10⁻⁵ correctly
signed, paying proposals per lineage, that gives **p_P ≈ 0.04 lines** crossing. This is an assumption in `power.py`,
not a registered arm: truncation may climb a sub-paying ladder that the ecology could not.
- The valley on the Pioneer is expected to hold. **That is not a flaw of the design: it is the valley.**
- The bypass predicts specifically that holistic lines leave the floor. So the design's power is set for detecting
  holistic crossing against a Pioneer at or near the floor (§7).

## 3. The mechanism: what must be added before any arm

Three small hooks are needed, each off by default and byte-identical when off. They follow RBT-113's pattern:
digests recorded on the pre-hook code, with tests. They come as a separate code PR, after the ruling.

1. **`evolve --from-population KIND=DIR`.** Start a fauna from a saved `final/` population, exactly as saved: no
   weight redraw (unlike `--holistic-seed`), and N must equal the saved count.
2. **`evolve --save-every K`.** Write each fauna's population at generations divisible by K, to
   `<kind>/gen-<t>/`. This is bulk, kept on the checkpoint branch.
3. **`--smell-decoy rotate`** (`evolve` and `Simulation`). Food sensors read the live layout rotated about the
   origin by θ ~ U[30°, 330°].
   - θ is drawn per season from a registered stream keyed on the season's start seed, so it is shared across the
     faunas and the paired worlds.
   - This is RBT-97's `RotatedSmell`, promoted. The N line uses it throughout evolution, and `steer.py` uses it for
     the decoy condition.
   - A test pins that the rotation leaves eating, regrowth and the real items untouched, and that a sensorless genome
     runs byte-identically under it.

**RBT-120's motor-budget flag** is used as that ticket registers it (§8).

## 4. The world

### 4.1 Default and placeholder

- **Default: auditor C's perception-demanding world** (RBT-121, due about 22:15 UTC), as the coordinator's synthesis
  adopts it.
- **Placeholder W0,** until then: RBT-113's `evolve` world with RBT-106's patches.
  - The flags are `--brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0
    --work-cost 0.03 --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start
    --score food --food-patches 3` (patch radius 0.6, regrow delay 0).
  - There, the compass's prize is 2.49× the uniform world's: a = 64 gains +2.103 [+1.542, +2.663] against +0.844
    (`runs/RBT-106/prize.txt`).
  - W0 is a placeholder, not a choice. It raises income and births as well as the prize (RBT-106 H8), and it has not
    been shown to make perception pay more than coverage.

**Whichever world is used must pass the gate in §4.2 before launch.** If W0 fails the gate and auditor C's world is
not ready, nothing runs.

### 4.2 The world gate (pre-launch; `gate.py`, after the ruling)

The gate is run on the candidate world with the motor budget ON, through `steer.py` itself:

| | check | pass |
|---|---|---|
| **G1** | **Perception pays, on the Pioneer.** RBT-106's routed w = 32 compass, signed per host by its measured travel direction (`scripts/travel_direction.py`), installed in 16 designed RBT-113 up-line finals (`routed_p801.py install`). | Mean F ≥ 0.5 items per season, and ≥ 12 of 16 hosts STEER. The share that steer is Q_P's sensitivity factor in `power.py`. |
| **G2** | **Perception beats coverage.** The G1 hosts' F against the coverage those same lines bought: the lesioned (blind) yield of the designed U finals minus the lesioned yield of RBT-113's designed founders. | F ≥ the coverage gain, i.e. one working compass is worth at least RBT-113's 24 generations of coverage selection. |
| **G3** | **The instrument sees a holistic steerer.** A hand-built holistic compass, HC, is written as JSON: two food sensors on laterally placed Parts of **different** Nodes (twins of one mirrored Node sum in the global brain, `synthesis.py:323–331`), a global differencing unit, asymmetric effector outputs, and a defined direction of travel. 4 variants (sign × gain). | At least one variant STEERS with F ≥ 0.5. The holistic Q_H sensitivity is the share of its 16 seeded-noise replicates that STEER. |
| **G4** | **False positives are bounded.** `steer.py` runs on 64 members of each fauna's RBT-113 U finals, and 64 founders. | False STEERS ≤ 0.05 per fauna and group (this sets EPS). Every zero-food-sensor genome gives F = ΔT = L = 0 exactly. |
| **G5** | **Timing.** 2 generations of one unit's U line. | Seconds per generation are recorded, and §9 is re-costed from them. |

- **If G3 cannot be built to pass,** the instrument's holistic sensitivity is unshown and the design does not launch.
  The fallback of loading the Pioneer compass through the holistic path proves only the code path, and is not
  accepted as G3.
- **[OPEN] G2 may be too strict for any world auditor C can build tonight.** If so, the coordinator rules whether a
  weaker G2 (for example F ≥ 0.5 × the coverage gain) is acceptable. It must be ruled before the arms run, and the
  readout states whichever was used.

## 5. Arms, lines and nulls

### 5.1 One arm = one unit

An arm is one start pair (RBT-113 seed directory `O1/1` … `Z4/Z12`, j = 1 … 24), running three `evolve` runs in
sequence:

| line | selection | smell during evolution | purpose |
|---|---|---|---|
| **U** | truncation 0.25, up, on solo net yield | real | the treatment |
| **N** | truncation 0.25, up, on solo net yield | **rotated decoy** (§3.3) | the **matched null**: identical selection and inputs, no information in smell |
| **C** | random parents, k = 10 (RBT-113's control) | real | the mutation-alone rate (candidate (i)) |

**Shared across U, N and C:** the evolve seed 116000 + j, both faunas, N = 40, D = 2 draws per generation, G = 48
generations (0 … 47 evaluated, probed at their end), `--elites 0`, solo throughout, the world (§4), the motor budget,
and `--from-population` for both faunas, with `--save-every 12`.
- At a unit, U, N and C share every generation's worlds.
- Both faunas in a run share them too.
- The generation-0 populations are identical across U, N and C.

### 5.2 The nulls

- **N: the primary null.** It holds constant everything except smell's information: the same selection, the same
  sensor input statistics (the rotated live layout) and the same currency. So:
  - any STEERS it produces is the instrument's false-positive rate on bodies selected for yield;
  - or it is steering-like behaviour that pays for reasons other than smell.

  Either way it is subtracted.
- **C: the mutation-alone rate.** share_C(t) − share_N(t) per fauna is quantity (i), reported with a CI and never
  in a verdict.
- **The decoy probe inside each genome** (§1.2) is the per-individual null, the third layer.

### 5.3 Controls (checked by `readout.py`; VOID per fauna and scope, as in RBT-113 §6)

- **I1.** Every probed genome with no food sensor reads F = ΔT = L = 0 exactly. One exception voids the instrument
  for the whole readout.
- **I2.** The configs are the registered ones. U, N and C differ only in `--line` and `--smell-decoy`.
- **I3.** Generation 0 is identical (names and fitness) on U, N and C, in both faunas, and equals the saved start
  population.
- **I4.** The worlds are shared: `(terrain_seed, start_seeds)` per generation is identical across U, N and C.
- **I5.** The selection mechanics hold: every U and N parent is in the top k of its generation. C passes RBT-113's
  control-unselected check.
- **I6.** The run is complete: 48 generations, and saved populations at 12, 24, 36 and 48 (generation 47's end, named
  48).
- **I7.** The per-unit re-check of G1 and G4. The planted-compass positive control is re-run on 4 of the unit's own
  generation-0 designed hosts, and must STEER in ≥ 3. This follows the programme's rule since RBT-104's VOID: controls
  run on the arm's own hosts, "at a stated s, not arithmetic reachability" (paper 10, L565–570).

## 6. Statistics and verdicts (`readout.py`; constants fixed before any data)

### 6.1 Per unit

For each unit and fauna f ∈ {H, P}, the readout computes:
- **A_f**, as in §1.5;
- **crossed_f**, the line-level call at generation 48.

Also reported per fauna, with no verdict:
- A_C,f, the C-line analogue;
- the mean F and ΔT of U members;
- the share with ≥ 2 food sensors on distinct Nodes;
- food against work (RBT-113's D1 decomposition) at generations 0 and 48.

### 6.2 Across units (n = 24, paired by unit)

- d_j = A_H,j − A_P,j, with its mean, two-sided 95% t CI, and sign-flip p (20,000 draws, since n > 16).
- k_H and k_P, the number of crossed lines per fauna, each with an exact one-sided 95% upper bound.
- A fauna **CROSSES** if the CI on its mean A excludes 0 above and its sign-flip p is < 0.05.

### 6.3 The verdicts, in order (as in `power.py`)

1. **HOLISTIC MORE READILY:** the CI on d excludes 0 above, p < 0.05, and the holistic fauna CROSSES.
2. **PIONEER MORE READILY:** the CI on d excludes 0 below, p < 0.05, and the Pioneer CROSSES.
3. **NEITHER CROSSES:** the exact upper 95% bound on P(a line crosses) is below **0.25** for both faunas.
   - In words: "in fewer than one line in four, on either body, does steering appear and hold within 48 generations
     of truncation selection in a world where perception pays."
   - **This is the bypass's clean "no".** The fixed body's valley holds, as expected, and the extra dimensions did
     not open a way round it at this depth.
4. **NOT MORE READILY (EQUIVALENT):** the CI on d lies inside ±**0.025**, and at least one fauna has k ≥ 3.
   - 0.025 is half the mean d of the weakest bypass of interest: a quarter of holistic lines crossing against the
     Pioneer's 0.04.
   - At n = 24 it almost never fires (`power.txt`), and the draft says so rather than widen it. A wider margin would
     call real bypasses "equivalent": in a trial of the model at ±0.15, a weak bypass read EQUIVALENT 52% of the
     time (not committed; reproduce by setting `DELTA_EQ = 0.15` in `power.py`).
5. **INCONCLUSIVE** otherwise.

**The headline is one sentence per verdict, fixed in code.** It gives:
- the verdict;
- the design (from the coverage peak, 48 generations, truncation, the world);
- d and each A with its CI;
- k_H and k_P with their bounds;
- the SMELL-USE shares beside the STEERS shares, so that kinesis is visible;
- the sentence *"The Pioneer's valley is a measured property of the fixed body; a holistic crossing is evidence for
  the bypass only in this world and at this depth, and a NEITHER is evidence against it only to the stated bound."*

**Sensitivity splits (reported only; no verdict):**
- O starts against Z starts;
- F_MIN relative instead of absolute (§1.3);
- the verdicts with the C line as the null in place of N.

### 6.4 Valley depth (descriptive)

The readout reports depth on each body, pooled over units, from the C and U probes:
- the net yield of SMELL-USE members, and of members with F ≤ −0.25 (smell used *against* food, the behavioural
  anti-compass), each against NONE members of the same line and generation;
- the net yield of the first STEERS members in a U line against their generation's mean.

These estimate how far down the intermediate steps sit, and whether the holistic space has intermediates that do not
cost at all. The latter is the bypass's mechanism, if it is there. No test is made.

### 6.5 Stated both ways

- **If holistic bodies do cross more readily,** the reading is: "in this world, from a matched coverage peak,
  body-and-brain evolution finds directed smell-following where the fixed body does not."
  - It must still survive the follow-up paper's audit: the steerers' bodies and motor use are compared against the
    budget, and a crossing bought by a new allowance is reported as such (RBT-121).
- **If neither crosses, or the Pioneer crosses as readily or more,** that is a clean "no" for reason (c) at this
  design. It is written up as a finding, not a failure to rescue the proposal.

## 7. Power at the registered n (`power.py` → `power.txt`)

**The model.** Per unit and fauna:
- the U line crosses with probability p_f, at a uniform generation, then sweeps linearly to a plateau Q_f over 12
  generations;
- N, and U before crossing, sit at the false-STEERS rate EPS = 0.02;
- 16 members are probed per line at 12, 24, 36 and 48 generations, binomially.

**The bounds are explicit.** A_f lies in [−EPS, Q_f], and Q_f folds in the instrument's sensitivity from G1 and G3.
This is RBT-113's lesson: its unbounded Gaussian model promised the designed body a response of 3.1–5.0 that the body
could not reach. The observed value was 1.48 (ADVERSARY §5).

**Results at n = 24** (300 simulated readouts per row):

| scenario (p_H, p_P) | HOLISTIC MORE | PIONEER MORE | NEITHER | EQUIV | INCONCL |
|---|---|---|---|---|---|
| null: both at the prior floor (0.04, 0.04) | 0.007 | 0 | **0.910** | 0 | 0.083 |
| null: neither ever crosses | 0.007 | 0 | 0.993 | 0 | 0 |
| weakest bypass of interest (0.167, 0.04) | 0.160 | 0 | 0.317 | 0 | 0.523 |
| weak bypass (0.25, 0.04) | **0.340** | 0 | 0.090 | 0.003 | 0.567 |
| bypass (0.5, 0.04) | **0.893** | 0 | 0 | 0 | 0.107 |
| strong bypass (0.75, 0.04) | 1.000 | 0 | 0 | 0 | 0 |
| bypass with low plateau (0.5, Q_H 0.25) | 0.600 | 0 | 0.053 | 0 | 0.347 |
| both cross equally (0.5, 0.5) | 0.030 | 0.027 | 0 | 0 | 0.943 |
| both at ceiling (1, 1; Q 0.8) | 0.027 | 0.023 | 0 | 0 | 0.950 |
| Pioneer more (0.1, 0.5) | 0 | **0.680** | 0 | 0 | 0.320 |

**How to read this:**
- **Level:** false HOLISTIC ≤ 0.030 in every scenario without a holistic advantage, including at the ceiling.
- **The clean "no" is reachable where it is expected.** At the Pioneer's prior floor, NEITHER CROSSES fires 0.91 of
  the time.
- **A weak bypass is the weak spot.** It is detected at 0.34, and is otherwise mostly INCONCLUSIVE, not NO:
  NEITHER fires 0.09, because the effective crossing rate after late crossings is below 0.25.
- **Equivalence is out of reach at n = 24.** "Both cross equally" returns INCONCLUSIVE. The draft accepts this: the
  scenario the bypass argues against, the Pioneer crossing too, is the one the prior makes least likely.
- **n = 12 is not enough.** Under the null, NEITHER CROSSES fires only 0.37 (`power.txt`, n = 12 section),
  so 24 units it is.

**[OPEN] The weak spot has two cures,** each about +50% cost:
- G = 72 generations;
- 36 units, which would need new start populations, since RBT-113 has 24.

The adversary and the ruling decide whether either is bought.

## 8. The motor budget

RBT-120's budget is **ON in every `evolve` run, every probe (`steer.py`), and every gate check.**
- The flag and its value are taken from RBT-120's merged registration, and pinned in the arm's command builder
  (`world.py`, after the ruling).
- **The start populations** were evolved without a budget.
  - The readout reports, per fauna, the share of generation-0 members over the budget, and how RBT-120's rule treats
    them.
  - If the rule clamps them at build, they enter as clamped.
  - **[OPEN] If the rule rejects them** rather than clamping, the design waits for a ruling on how to fill the
    population.
  - The RBT-113 holistic U finals sit at Σgear/(4 × mass) = 0.90, against the designed body's fixed 1.76 and the D
    line's 3.66 (`probe_gear.txt`). So most are expected to fit any budget that keeps the Pioneer legal.
- **Per probe,** each probed member's Σgear, its ratio to 4 × mass, and its ball-joint share are recorded
  (`probe_gear.py`'s measures). Any STEERS member is reported with its motor class beside it (§6.5).

## 9. Cost and packing

**Per generation.** RBT-113 measured 12.6–15.5 s per generation on 4 workers, about 50 CPU-s, for N = 40 × 2
faunas × 2 draws (PREREGISTRATION §9, §11.5). Coverage foragers move more than founders, so this design budgets
×1.5: **75 CPU-s**. G5 re-costs this.

| item | CPU-h |
|---|---|
| one `evolve` run (48 generations) | 1.0 |
| one arm (U, N, C) | 3.0 |
| probes per arm: 13 probe points (generation 0 once; 12, 24, 36, 48 × 3 lines) × 2 faunas × 16 members. Stage 1 is 8 seasons each; stage 2 is 48 seasons for an assumed 20% of members; 0.35 s per season | about 0.75 |
| **one arm, total** | **about 3.75** |
| **24 arms** | **about 90** |
| gate (G1–G5) | about 1 (one session, before the wave) |
| readout | minutes |

**Packing.** This follows RBT-113's RUNNER and `runs/README.md`:
- two arms per session, side by side at `WORKERS=2` on 4 cores, each with the durable loop;
- about 1.9 h of `evolve` plus about 0.4 h of probes (run at the arm's end, WORKERS=2): **about 2.3 h per session,
  budgeted at 3 h**;
- **12 sessions, 28–36 session-hours**, in two waves of 6. A unit's own three lines stay in one arm, so pairing
  never crosses sessions.
- **If a session is lost,** its two units are dropped, and the readout runs at reduced n. It is not re-simulated;
  `power.py` is re-run at the realised n and printed.

**Committed per arm:** `config.json` ×3, `command.txt`, `steer.json` (per probed member and condition; written as
`steer.txt` so the allowlist admits it), `platform.txt` and `commit.txt`. The bulk (saved generations,
`lineage.jsonl`) goes on `ckpt/rbt-116-<ARM>`.

**Cheaper fallbacks, if the ruling wants them:**
- drop the C line: −1/3, about 60 CPU-h, losing quantity (i);
- G = 36: −1/4, weakening detection of late crossings.

n is not cut below 24.

## 10. What the design adversary should attack first

1. **Does T separate steering from kinesis on a real holistic body,** and not only on HC? For example, a body whose
   gait turns more when smell is high will read T > 0. The draft counts that as klinokinesis, which is chemotaxis.
2. **The absolute F_MIN,** across bodies with different base incomes (§1.3).
3. **Whether the coverage-peak start favours either body.** The holistic finals carry few noses; the designed
   finals carry three unwired ones. And whether R (random founders) should be primary instead.
4. **Whether N is a fair null.** Selecting for yield under a rotated decoy may push bodies toward *ignoring* noses,
   while U's bodies are free to keep them. Then share_N may sit below U's true false-positive rate. C is printed as
   the alternative null (§6.3).
5. **The Pioneer's prior p_P ≈ 0.04 under truncation.** If truncation climbs the sub-paying ladder (w = 8 → 16 → 32),
   the Pioneer may cross far more often. That would make "both cross" plausible, and equivalence unreachable.
6. **The world gate's G2,** and whether auditor C's world changes the Pioneer's sensor supply or income in ways that
   touch only one body (RBT-106 H8's lesson).
7. **Whether 48 generations is "readily"** in Conrad's sense, or merely "within a budget".

## 11. Dependencies and status

| gate | status at drafting (20:35–23:00 UTC) |
|---|---|
| RBT-120 motor budget merged | pending (its designer's PR targets about 23:30) |
| RBT-121 auditor C's world and the synthesis | pending (about 22:15 and later) |
| hooks §3 (a code PR with byte-identity tests) | not started; after the ruling |
| `steer.py`, `gate.py`, `readout.py`, `world.py`, `run_arm.sh` | specified here; written after the ruling |
| world gate G1–G5 | after the hooks, on the ruled world |
| design adversary, coordinator ruling | pending |
