# RBT-104 pre-registration: is link-weight reach the cause?

*Designer's pre-registration, 2026-09-26. **Amended at 19:xx UTC** per the coordinator's 18:40 ruling on
the design adversary (PR #181, `runs/RBT-104/adversary/`):
- F2, F5, F6 and F7 are applied;
- F4, F8 and F9 get a sentence each (§3.2, §4.2, §5);
- **U8 is dropped**;
- **wave 0 is a pre-registered futility gate** (§6.2).

The adversary's files are merged onto this branch and cited in place. **No arm has been launched.** Every number below is read
from a committed file or from a readout this design generated and commits beside it; the file is
named at each number. The runs made for it are throwaway checks of the tooling, listed in §7, and
none is an arm. The adversary is named by the coordinator.*

**The question** (ticket RBT-104). Strand 3's explanation for "600 seasons produced no compass" is
magnitude: drift proposes the routed compass's structure, a correctly wired compass pays as
chemotaxis, and the operator never makes the structure's own gain big enough to be worth anything
(paper 8). This arm tests that causally. **If the designed body's weight reach is raised past the
compass's threshold, does chemotaxis evolve under selection?**

**The design in one paragraph.** One new flag, `--link-scale K`, sets the scale of the designed
body's link-weight space, and K = 8 (§1). The structure is **planted**, because under selection in
this economy it is never proposed at all (§3.1). So the primary contrast is two arms on RBT-90
part 2's ten seeds that load the same founders, half of which carry the routed motif at the
magnitude drift gives it, and differ in the flag alone (S1: K = 1; S8: K = 8). The flag at its
default is byte-identical to RBT-90 part 2 (§7). The readouts are RBT-102's structural instrument
and RBT-97/103's decoy harness, each with a positive control that has been run (§4).

The arms run in two stages. **Wave 0** (S1 and S8 on seeds 801 and 4) carries a pre-registered
futility gate at season 150 (§6.2). It checks whether S8 holds its planted compass's paying
magnitude above what the operator alone leaves at that depth. If it does not, on both seeds, the
ticket stops there. **What this tests is uniform link-weight reach, with biases unscaled, on a
planted structure, in RBT-90's uniform world.** It is not "magnitude" in general (§1.4, §6).

---

## 1. The binding parameter and its value

### 1.1 What the operator does, read from the code

`rabbitstew/genetics.py`, `MutationConfig` and `mutate_controller`, the designed body's operator
(`Ecology._breed`, one call per birth):

| draw | distribution | rate per mutation | governed by |
|---|---|---|---|
| a link's step | N(0, 0.4) | 0.25 × 0.98 = 0.245 | `weight_sigma` |
| a link's reset | N(0, **1.0**) | 0.25 × 0.02 = 0.005 | hard-coded |
| a **new link** | N(0, **1.0**) | `add_link_rate` 0.15 per brain | hard-coded |
| a unit's bias step | N(0, 0.4) | 0.25 | `weight_sigma` (the same field) |
| a new neuron's bias | N(0, 0.5) | `add_unit_rate` 0.1 | hard-coded |
| a founder's link | N(0, 1.0) | at founding | `fixed.randomize_weights` |

**Nothing clamps a weight or a bias.** So the "weight ceiling" in the ticket does not exist as a
parameter. Paper 8 §4.1's rms-3 ceiling is the walk's stationary scale, which the 0.005 reset sets
and which is reached at depth ~1,000. At the depth these runs reach (window depth 14.0–17.5 in
part 2, `runs/RBT-102/aggregate.txt`; 19 in RBT-91), a link has been reset with probability
1 − 0.995¹⁹ ≈ 9%. **What sets a proposed structure's magnitude at this depth is the draw scale:**
new links born at N(0, 1), plus a step walk of sd 0.4·√(0.25·19) ≈ 0.87.

`weight_sigma`, the one existing knob, is not a weight-only change. It drives the bias walk too,
and the bias walk has no reset; paper 8 §4.2 and §6.2 measured that widening it pumps the
recurrent gain of every brain and collapses the `tanh` slope. It is therefore not the flag.

### 1.2 What the 84 arrivals are made of

`runs/RBT-104/anatomy.txt` regenerates RBT-91's 84 default-scale arrivals from their lineage
seeds. All 84 links-alone values equal `docs/artifacts/RBT-91-alone-baseline.txt`. Per arrival it
prints the predicate unit's function, its bias and the motif's four weights:

- The four weights are small. The **linear gain |(u_L − u_R)(v_L + v_R)/2| has median 1.48 and a
  maximum of 7.36**, against the a = 64 at which the routed motif pays on 8 of 10 part-2
  populations (RBT-103, `docs/artifacts/RBT-103-seed-*.txt`, ROW lines).
- **25 of 84 read no small-signal response at all**: `sign` (12), `differentiate` (7), `integrate`
  (4) and `relu` (2). For `sign` and `differentiate` that holds at any weight scale. This is a
  barrier magnitude cannot remove, and it is stated here so the arm is not credited with removing
  it.
- The `tanh` arrivals that respond are attenuated by their bias. Many sit at |b| > 1.5, where
  sech² < 0.2.

So paper 8's conclusion stands (the own-link gain is short by an order of magnitude) and so does
its warning about `weight_sigma`. **The reach, as a parameter, is the scale of the link-weight
draws, decoupled from the bias.** §1.4 shows that the bias then gates what that scale can deliver.

### 1.3 The flag

`--link-scale K` (`MutationConfig.link_scale`, default 1.0):
- **founders:** every designed-body founder's link weights are multiplied by K at founding
  (`genetics.scale_links`, called in `Ecology.__init__`), whether the founders are drawn or
  loaded;
- **operator:** every link-weight draw of the designed body's operator is multiplied by K. That
  covers a new link's N(0, 1), a reset's N(0, 1) and a step's N(0, 0.4).
- **untouched:** unit biases, the holistic fauna, and every random stream. The flag multiplies
  draws and never makes one.

**Why the founders too, and not the operator alone.** With the operator alone at K = 8, every
existing gait link (|w| of order 1) would be hit by steps of sd 3.2 at rate 0.245 per birth. That
scrambles the parent's controller in one or two births, so heritability collapses and the arm
measures a meltdown. Scaling the founders' links as well starts the whole link space at the scale
the operator will hold it at, so **each step keeps its default size relative to the weights it
moves**. The only thing that changes is the absolute scale of every link against every bias and
every `tanh`, which is exactly the magnitude in question. (Under the operator alone the space
converges to this scale anyway, and the founders' flag removes the transient.)

The value is set **from start** (season 0), which the ticket allows. At 1.0 the run is the run as it
was, byte for byte (§7, check 1).

### 1.4 The value: K = 8, and what it does and does not reach

**The rule as first posted, and how it failed.** At 16:47 UTC, before any run at K > 1, the ticket
recorded this rule: *the smallest K in {4, 6, 8} at which the top decile of drift's default-scale
arrivals clears the a = 64 rung on its own links.* It rested on a prediction. Under the flag every
link is exactly K times larger and the bias is not, so the motif's linear gain scales as K², and
so, it was assumed, would its small-signal links-alone response. The rungs on the arrivals' own
links are 6.2831 (a = 16, the null rung), 12.5236 (a = 32, pays on 5 of 10 part-2 populations) and
**24.7145** (a = 64, pays on 8 of 10) (`runs/RBT-72-adversary/probe_rung.txt`). The top decile of
the 84 is **0.6195** (`drift-reach-k1.txt`), so the prediction ran:
- K = 4: 9.91;
- K = 6: 22.30;
- **K = 8: 39.65, which clears by 1.60×.**

**Verified, and the prediction is wrong** (`runs/RBT-104/drift-reach-k{1,4,6,8}.txt`). This is
RBT-91's instrument, imported unchanged, with the parents' links scaled and the one field set,
over the same 200,000 lineages:

| K | structural arrivals | own links ≥ 6.28 (a = 16) | ≥ 12.52 (a = 32) | **≥ 24.71 (a = 64)**, Wilson 95% | top decile | max | structureless whole-brain ≥ 24.71 |
|---|---|---|---|---|---|---|---|
| 1 | 84 | 0 | 0 | **0**, [0.0, 4.4]% | 0.62 | 1.26 | 0 of 3,998 |
| 4 | 84 | 8 | 1 | **0**, [0.0, 4.4]% | 5.49 | 16.83 | 69 (1.73%) |
| 6 | 84 | 10 | 6 | **1**, [0.2, 6.4]% | 6.73 | 37.60 | 68 (1.70%) |
| 8 | 84 | 10 | 8 | **3**, [1.2, 10.0]% | 7.93 | 57.00 | 76 (1.90%) |

At K = 1 the arrival list is identical to `RBT-91-alone-baseline.txt` line for line (the
self-check printed in `drift-reach-k1.txt`). The structural count is 84 at every K, because signs
are scale-free.

**Why** (`runs/RBT-104/saturation.py` and `saturation.txt`, all 84 arrivals at K = 1 and K = 8).
The output link multiplies the interneuron's **resting** output f(b) as well as the signal. The
bias is not scaled, so the resting drive v·f(b) on the Effector grows with K and saturates it:
- Of the 33 `tanh` arrivals that respond at K = 1, the **4** whose resting drive stays below 1 at
  K = 8 scale close to K² (median ratio 42.8; 64 would be exact).
- The **29** whose resting drive exceeds 1 **collapse** (median ratio 0.2).
- The 25 zero-response arrivals of §1.2 stay at zero.

A paying routed compass therefore needs a large v **and** |v·f(b)| below about 1 **at once**,
which means an interneuron bias near zero. The bias walks with sd ≈ 0.2·√d and has no reset.
Scaling the biases as well would drive f(b) to ±1, which is worse.

**No uniform link scale puts drift's own proposals past the rung in bulk, and this is a
correction to paper 8's reading.** "Magnitude withholds it" treats the gap as a scale. It is a
scale gated by the interneuron's bias through Effector saturation. (Posted on the ticket at
17:58 UTC, before this pre-registration.)

**The value, on a measured rule: K = 8**, the K on the ladder that puts the most arrivals past
a = 64 (3 of 84, against 0 at K = 1). It is also the ladder's largest, and a larger K was not
tried, because the structureless side effect is already flat at about 1.8% from K = 4. **For the
planted motif of §3.2, whose bias is 0 at founding, K = 8 clears the rung with margin**: its own
links read median 46.0 (range 30.4–55.5) against 24.71, which is 1.9× (§7, check 4). That is the
primary arms' "past the threshold, with margin". The drift ladder is the literal arm's.

K = 8 is not an extreme reach in the operator's own terms. The default operator's asymptote already
holds 0.03% of links at |w| ≥ 16 (paper 8 §4.1). At K = 8 the typical link is |w| ≈ 8, and the
new-link draw is N(0, 8).

## 2. Side effects on gait and income, and the control

A larger link scale saturates `tanh` units, so the gait that currently pays is evolved in a more
bang-bang regime. This is the side effect the ticket warns of (RBT-90 part 2: no champion beats its
own gait, `runs/RBT-90/part2-readout.txt`).

**The control** is S1, which runs on the same seeds with the same seeded founders, so S8 − S1 is
the reach's side effect with the seed present. (The unseeded arm U8, whose control was RBT-90 part 2
cited, was dropped at 18:40 because it carries no verdict. The flag's byte identity to part 2 still
anchors S1 to the committed baseline: §7, checks 1 and 2.)

**Quantities, from each arm's `seasons.txt`** (RBT-71's summary, committed per arm):
- **Income:** the window mean (seasons 300–599) of the designed fauna's mean lifetime score.
- **Survival:** the window mean alive, births and deaths, and extinction.
- **Viability:** the fauna never dies out, reaches season 599, and averages ≥ 30 alive in the
  window.

**Pre-registered predictions** (S8 − S1, paired over 10 seeds, t(9)):

| # | prediction | confidence |
|---|---|---|
| S-1 | No primary arm goes extinct (20 of 20 viable) | 0.80 |
| S-2 | Income falls under the raised reach: S8 − S1 window income has its t(9) interval below zero | 0.55 |
| S-3 | The fall, if any, is less than half of S1's income (S8 ≥ 0.5 × S1 on ≥ 8 of 10 seeds) | 0.70 |
| S-4 | Turnover rises: S8 has more births than S1 on ≥ 7 of 10 seeds | 0.60 |

S-2 is at barely better than even. The only evidence is mechanism: saturated units are coarser
controllers. S-4 is weakly informed by the 20-season feasibility run (§7, check 3), which was a
feasibility observation and was not used to choose K.

**If the side effect dominates** (fewer than 7 of 10 S8 arms viable), the verdict is **VOID**, not
a falsification (§6).

**The side effect that bears on the compass directly: saturation.** At founding, the planted S8
carriers are paying on their own links (median 46.0) but **not in their host brains**. Their
**whole-brain** small-signal response has median **0.0025**, p75 0.206, and only **2 of 30** reach
24.71. The same founders at K = 1 read median 0.373. (This is RBT-91's probe on seed 801's founders,
§7 check 4.) A random brain at eight times the scale drives its Effectors into saturation at the
probe's operating point, so a compass's contribution does not reach the wheels.

So whether S8's planted compass can act depends on selection evolving host brains that leave the
drive Effectors in range. That is part of what "raising the reach" does, and it is measured, not
assumed away:
- readout (b) is behavioural, so it sees whatever the evolved host does;
- the **per-arm install control** (§4.2) asks whether an installed a = 64 motif is food-dependent
  **on that arm's own champions**.

An S8 arm whose champions mask an installed compass fails that control. It is **unusable, not a
null**, and fewer than 7 usable S8 arms make the verdict VOID. **The VOID probability is unmeasured on K = 8 hosts** (adversary F8). The only K = 8-host
behavioural reading is at t = 0, and there the planted compass does not steer (§3.2). No evolved
K = 8 host exists before the arms.

---

## 3. Why the structure is planted, and how

### 3.1 The literal arm has no power

RBT-102 put all 12,276 part-2 genomes through RBT-91's predicate and found **0 carriers**
(`runs/RBT-102/aggregate.txt`). The absent half is the input side: no genome has a global unit fed
by both wheel noses (`runs/RBT-102/supp_partial.txt`). Drift's own rate predicts about 0.26 de novo
arrivals across all ten 600-season arms (RBT-102 §2.4, 2 × 10⁻⁵ per birth over 11,676 births). About
half of those would be wrong-signed for their carrier (paper 8 §3.4, 30 of 58 on own links).
`--link-scale` cannot move that rate, because signs are scale-free (§1.4 table).

So an unseeded arm expects **about 0.1–0.3 correctly signed arrivals in the whole experiment**, at
any reach, and at K = 8 about 4% of arrivals reach the rung (§1.4). Under the magnitude hypothesis taken as wholly true, "no food-dependent champion"
would still happen with probability ≳ 0.75. **The ticket's falsifier cannot fairly fire on an
unseeded arm.** P(no food-dependent champion | H) ≥ 0.995 for one (its power statement, kept in this design's superseded `power.txt`). The unseeded arm was
therefore **dropped** (coordinator, 18:40). If the verdict is SUPPORTED, it is the follow-up that
asks whether drift's own proposals get there.

### 3.2 The seed

`runs/RBT-104/seed_founders.py SEED`:
1. It draws **part 2's own sixty designed-body founders** for that seed, exactly as the ecology
   draws them. It asserts that the configuration equals the committed
   `runs/RBT-90/forage-SEED/config.json` outside seasons, generations and workers. The bare
   founders are byte-identical to those a part-2 run saves (§7).
2. It installs RBT-97's routed motif (the installer RBT-103 used: a new global `tanh` unit, bias 0,
   fed by the two wheel noses at ±1, feeding both drive Effectors at w) **at w = 1** in half of
   them:
   - i % 4 == 0 gets sign +1 (15 founders);
   - i % 4 == 2 gets sign −1 (15 founders);
   - odd i stays bare (30 founders).
3. It keeps each founder's drawn age.

The weights are the typical geometry of a drift proposal at the default scale. §1.2 gives
|u|, |v| of order 1, and a linear gain of 2 sits at the 60th percentile of the arrivals' |linear a|
(50 of 84 are at or below it; median 1.48, `anatomy.txt`).
Both signs are planted because a compass's sign belongs to the direction the population will
drive, which no founder has yet (paper 8 §2.3).

The founders are bulk and are not committed. Each seed's `SHA256SUMS` digest is committed in
`runs/RBT-104/founders-digests.txt`, and `run_arm.sh` refuses founders that do not match.

**What the seed reads as, through readout (a)'s instrument** (§7, check 4, seed 801): **30 of 60**
founders carry the structure in both arms. Their own-link response is
- **median 0.766 (range 0.445–0.978) at K = 1:** sub-paying, and inside drift's own range (its
  largest arrival reads 1.262);
- **median 46.0 (range 30.4–55.5) at K = 8:** above the a = 64 rung of 24.71.

So S8 plants a structure that is paying in magnitude **if it is correctly signed and if a gait
exists to steer**. S1 plants the same structure with its magnitude withheld.

**What the seed costs and does at t = 0** (coordinator's condition 2; adversary F4). There are two
readouts of the 30 planted founders per seed, each against its bare twin (the identical part-2
founder), on 16 paired bouts from 7000.
- **Income** (`seed_income.py`, `seed_income.txt`; t over the ten seeds):
  - **K = 1:** planted − bare **+0.011 [−0.015, +0.037]**. No cost.
  - **K = 8:** **+0.064 [+0.002, +0.126]**.
  - Seed 801 alone reads −0.0896 [−0.2634, +0.0843] at K = 8. That is the adversary's −0.090
    [−0.263, +0.084] (`adversary/founders-t0-801.txt`), the same number from independent code.
  - The pooled +0.064 is ten seeds, not one. It is not a gain in food dependence.
- **Cost and food dependence together** (the adversary's `founders_t0.py`, run unchanged on all ten
  seeds: `founders-t0-SEED.txt`, pooled by `t0_pool.py` into `t0_pool.txt`). Here F is
  real − rotated decoy, and F seeded − F bare is the planted compass's own food dependence:

{{T0}}

**So neither arm's seed costs its founders income at t = 0, and in S8 the planted compass does
not steer at t = 0.** This is the behavioural form of §2's masking, and it is why §6.0's baseline
decides so much.

**What the primary contrast asks, stated exactly.** Given the structure present at founding, and
with all else paired, does raising the reach from 1 to 8 make selection produce **food-dependent
champions** and **carry the structure more** than at the default reach?

In S8 that includes whatever selection must do to keep a planted compass paying. Per §1.4 and §2,
that means holding its interneuron's bias near zero (the bias walks, and at v ≈ 8 a resting
output above ~1/8 saturates the Effector) and evolving a host brain that leaves the drive
Effectors in range. The magnitude hypothesis says that once the magnitude is within reach,
selection does this. That is the magnitude
hypothesis conditional on structure. It is the part of strand 3's explanation that is testable at
all in this economy. A negative answer falsifies "magnitude withholds it". A positive answer
supports it, and still leaves the structural barrier of §3.1 standing. The report will say so in
its headline whichever way it goes.

---

## 4. Readouts, each with a positive control that has been run

### 4.1 (a) Structure: RBT-102's instrument, unchanged

`python runs/RBT-102/analyse.py runs/RBT-104/ARM-SEED > runs/RBT-104/ARM-SEED/rbt102.txt`

The instrument is RBT-91's predicate without the magnitude gate. It reads every genome saved at
birth, and gives carriers per season over the living designed fauna, **X** (the mean carriage
over seasons 300–599), de novo arrivals, and every distinct window carrier signed at the
reference probe (16 × 15 s). Read from its output:
- **X per arm**, as carriers per 1,000;
- **paying compass carriers.** These are the distinct window carriers whose **own-link** response,
  re-signed by their own heading with RBT-102's rule, is ≥ 24.7145 (the a = 64 rung).
  `readout.py` re-reads them from the analyse table.

- **paying in host**: carriers that also have a **re-signed whole-brain** response ≥ 13.3549, the
  whole-brain reading of the installed a = 64 motif (`probe_rung.txt`, antisymmetric part at
  w = 32). This is F-a's in-host reading (§6.1, adversary F5).

This deliberately does not use analyse.py's own "COMPASS" column, which signs the whole-brain
response (paper 8 W12), or its `alone_reaches_rung`, which uses the superseded 6.8664.

**Positive control, in every arm, before any number.** analyse.py installs RBT-87's motif at
(w = 1, +) and (w = 8, −) in 20 window genomes, and it must detect 40 of 40. **Run:** on throwaway
6-season S1 and S8 runs of seed 801 (the pre-registered founders), it detected **40 of 40 in
both**. The planted founders read **30 of 60** carriers at season 0 in both arms, directly through
RBT-91's predicate (§7, check 4). The predicate says yes under the raised reach.

### 4.2 (b) Function: RBT-97/103's decoy harness on the evolved champions

`python runs/RBT-104/function.py --run runs/RBT-104/ARM-SEED > .../function.txt`

**Bodies:** the designed fauna's bests at seasons 300, 350, 400, 450, 500, 550 and 590 (the second
half, RBT-102's window), as each stands, **at its evolved gains**.

**The bout** is RBT-103's `income_bout`, called unchanged with w = 0 on the genotype handed to it.
It uses the same Simulation, the same `RotatedSmell` decoy (the live layout rotated about the
centre, with one angle per body and seed from [seed, gen, 97]), and 64 paired seeds from 7000.

**PRIMARY, F = intact(real smell) − intact(rotated decoy)**, the per-body mean over the 64 seeds,
with t(6) over the seven bodies:
- **FOOD-DEPENDENT** if the interval excludes zero from above and RBT-38's zero-count veto passes
  (more than half the seeds exactly equal means smell is unused: vetoed);
- a population's champion line is food-dependent iff its F is.

For an installed motif, F is exactly RBT-103's "motif − decoy". **Calibration from committed
files:** in RBT-103's decoy readouts that interval excludes zero on **8 of the 8** part-2
populations where an installed a = 64 motif paid (`docs/artifacts/RBT-103-decoy-*.txt`).

**Attribution** (reported, not in the verdict). The base is the champion **compass-lesioned**:
every link from a wheel's food nose into a global unit is removed, which is the input half of the
routed motif, the only compass the genotype can hold. RBT-103's retention rule is then applied
unchanged:
- gain = intact − lesioned;
- decoy = intact(rotated) − lesioned;
- the compass is food-dependent if the decoy retains < 25% of the gain and gain − decoy excludes
  zero.

**Positive controls, run** (§7, check 5, on part 2 seed 801's committed-rule bodies, gens
0–590, restored from `ckpt/rbt-90-801` into a scratch directory, never over the committed files):

| control | what it must read | read |
|---|---|---|
| RBT-103's own scoring of an installed a = 64 motif, same harness | +0.857 [+0.549, +1.166] and decoy +0.203 [+0.047, +0.359], to the digit (`RBT-103-decoy-801.txt`) | **+0.857 [+0.549, +1.166]; decoy +0.203 [+0.047, +0.359], retains 23.7%: to the digit** |
| function.py's F on the champion + installed a = 64 motif (gens 0–590) | FOOD-DEPENDENT | **F +0.654 [+0.428, +0.880], FOOD-DEPENDENT** (= RBT-103's motif − decoy); attribution: gain +0.862, decoy retains 24.1%, FOOD-DEPENDENT |
| **the raised-reach geometry:** motif at inputs ±8, output 8 (a = 128, S8's planted motif as it stands at founding), gens 0–590 | FOOD-DEPENDENT, and it pays (attribution gain > 0) | **F +1.379 [+0.855, +1.904], FOOD-DEPENDENT**; gain +1.542 [+0.908, +2.177] (it pays, 7/7 bodies), decoy retains 10.6% |
| negative control: the bare part-2 champions, gens 300–590 | not food-dependent | **F +0.033 [−0.141, +0.208], not food-dependent**; no compass gain (intact and compass-lesioned read the same on every body). On gens 0–590 the bare champions read F +0.074 [−0.045, +0.192], vetoed by the zero count |

**In every arm, at readout:** the same install control (`function.py --install 32`, the a = 64
motif signed per body) is run on that arm's own seven bodies, into `function-pc.txt`, and must
read FOOD-DEPENDENT. **An arm whose (a) or (b) positive control fails is unusable for (b)**, and
it leaves the counts rather than entering them as a null.

**Three limits of these controls** (adversary F8):
- **(b)'s K = 8-geometry control ran on K = 1 hosts** (part 2's champions). It shows the geometry
  pays when a host lets it through, not that a K = 8 host will. The per-arm install control is the
  guard for that.
- **The controls used gens 0–590, while the verdict reads gens 300–590.** The per-arm controls use
  the verdict's own bodies.
- **Bare lines sit near the zero-count veto.** Part 2's bare champions at gens 300–590 had 213 of
  448 paired seeds exactly equal (47.5%, the veto is at 50%). A bare line will often read "VETOED"
  rather than "not food-dependent", and both count as not food-dependent.

---

## 5. Seeds, arms, depth and cost

**Seeds:** RBT-90 part 2's ten, **801, 804, 805, 806, 807, 1, 2, 3, 4 and 7**. The subset question
does not arise, because all ten are used. Ten are needed for the across-population rules in the
form RBT-90 and RBT-103 use them.

**Depth:** 600 seasons, part 2's own (window depth 14.0–17.5, the depth at which paper 8's
magnitude figures were taken). The readout window is **seasons 300–599**. So **N = 300 seasons**:
the magnitude hypothesis predicts food-dependent S8 champions from season 300 on, and a carriage
gap by then.

**Arms** (`runs/RBT-104/run_arm.sh ARM SEED`, part 2's command verbatim plus the arm's flags):

| arm | founders | `--link-scale` | role | n |
|---|---|---|---|---|
| **S1** | seeded (§3.2) | absent (1.0) | primary control | 10 |
| **S8** | seeded, the same files | **8** | primary treatment | 10 |

(U8 is dropped, coordinator 18:40. RBT-90 part 2 is no longer a control in any rule. It stays the
byte-identity anchor of §7.)

**20 arms, 10 runner sessions, two arms per session side by side at `WORKERS=2`**, which is
`run_arm.sh`'s default. **S1 and S8 of the same seed never share a session.** The schedule is
`runs/RBT-104/waves.txt`:
- **wave 0, 2 sessions:** (S1-801, S8-4) and (S8-801, S1-4). The futility gate is read on S8-801
  and S8-4 at season 150 (§6.2), and all four arms continue to 600 whatever it reads.
- **wave 1, 8 sessions** (only if the gate does not stop): the other eight seeds' S1 and S8, paired
  across seeds.

Each arm keeps its own `durable.sh every` loop and its own final save (README rules 1 and 6).
Workers do not change a run: the RBT-90 ruling found workers 1 and 4 byte-identical, and the
adversary resumed a K = 8 run byte for byte (F1). Any session still PENDING 3 minutes after launch
is poked once a slot frees (ticket, Gate).

**Per arm, the runner:**
1. launches `run_arm.sh` and `scripts/durable.sh every 20 runs/RBT-104/ARM-SEED rbt-104-ARM-SEED`
   as harness background tasks, with `DURABLE_WATCH_PID` set (README rule 1), and names the label
   on the ticket (rule 3). `run_arm.sh` writes `platform.txt` and refuses any machine but x86_64;
2. **wave 0's S8 runners only, once the arm has finished season 150:**
   `peek.py runs/RBT-104/S8-SEED SEED > runs/RBT-104/S8-SEED/peek-150.txt`. They commit and push
   it at once and post it on the ticket. Nothing else of any running arm is read (§6.2);
3. after season 599, runs:
   - `measure.summarise` → `seasons.txt` and `lineage-last.txt`;
   - `analyse.py` → `rbt102.txt`;
   - `function.py` → `function.txt`;
   - `function.py --install 32` → `function-pc.txt`;
   - S8 only: `peek.py … --season 300` → `peek-300.txt`, and `--season 599` → `peek-599.txt`;
4. runs **`durable.sh save` once more** (rule 6), commits the per-arm files by role (config, tables,
   readouts, `platform.txt`), pushes to `results/RBT-104-ARM-SEED`, and opens a PR against
   integration.

`readout.py` reads the lot from the checkout. It refuses a partial read: **NOT READ** until all 20
primary arms have reached season 599 on the platform.

**Cost** (adversary F9, at the house packing):
- **Ecology:** about 5.1 s per arm-season with two arms side by side at `WORKERS=2` (coordinator,
  17:02), so a pair takes about **51 min**. (On this design's container one arm at `WORKERS=4`
  ran at 10.5 s per season, so a slow runner could take up to about 1.8 h.)
- **Post-run:** about 25 min per pair.
- **Total:** about 1.3–2.2 h per session. **10 sessions ≈ 13–22 session-hours, the coordinator's
  15–20. Wave 0 takes about 2–4 session-hours, and a stop at the gate saves the other 8
  sessions.**

---

## 6. Predictions, confidences, and the falsifier

### 6.0 The operator-alone baseline (adversary F6)

The adversary ran the planted founders down 600 independent lineages per seed and K, using part
2's MutationConfig with **no selection and no crossover**, and read them with RBT-91's
instruments unchanged (`adversary/persistence-{801,4}.txt`).
`baseline-{801,4}.txt` re-runs the same `lineage()` at every depth 0–30. At the adversary's
depths it reproduces their table exactly.

| depth (generations) | 0 | 1 | 2 | 4 | 8 | 16 (≈ window) |
|---|---|---|---|---|---|---|
| structure, K = 1 and K = 8 alike (801) | 100% | 94% | 88–89% | 76–78% | 55–58% | 29–31% |
| **paying at K = 8** (same sign as planted, own links ≥ 24.71), 801 (4) | 100% | 74% (75) | 54% (56) | 31% (30) | 13% (11) | **2% (3)** |

**At K = 8 the operator erases the planted compass's paying magnitude with a half-life of about
two generations.** The loss is u ≈ 0.25 per generation, consistent with §1.4's bias gate acting on
the planted unit. The structure itself decays at the same rate at both K (a half-life of about
8–10 generations).

Selection can hold a paying class only if its advantage exceeds u. At t = 0 in S8 it has no
measured advantage: the planted compass does not steer in a K = 8 host (§3.2, all ten seeds). **So
FALSIFIED (F-b) is close to the operator's default outcome.** It is informative only as a
comparison against this baseline, which is how it is defined below. The wave-0 gate (§6.2) reads
that comparison at season 150, before 16 of the 20 arms are spent.

### 6.1 The verdict

Rules in `readout.py` §4, over the 10 seeds. "Usable" means viable, on the platform, with both
positive controls passing.
- **VOID** if fewer than 7 of 10 S8 arms are usable. The side effect, not link-weight reach, is
  then what was measured.
- **SUPPORTED** if S8 has food-dependent champions on **≥ 5** usable seeds, S1 on **≤ 1**, and
  the paired F(S8) − F(S1) has its t(9) interval above zero.
- **FALSIFIED** if S8 has food-dependent champions on **≤ 1** usable seed and the paired
  F(S8) − F(S1) interval does not lie above zero. It is read in one of three branches:
  - **(F-b) not held.** S8 held its paying compass above the operator-alone bound on **≤ 1**
    usable seed. "Held" on a seed means that `peek.py`'s statistic exceeds the no-selection 95%
    bound B at matched depth at **both** season 300 and season 599 (§6.2 gives the statistic).
    Reading: *at uniform link reach ×8 the operator erased the planted compass faster than
    selection held it.*
  - **(F-a) held and working, not used.** S8 held on **≥ 2** usable seeds, and on **≥ 2** usable
    seeds its window carriers include **≥ 10 distinct carriers, and ≥ 10% of its window carriers,
    that pay in host**. "Pays in host" means re-signed own links ≥ 24.7145 **and** re-signed
    whole-brain response ≥ 13.3549, the whole-brain reading of the installed a = 64 motif
    (`probe_rung.txt`, antisymmetric part at w = 32). Reading: *a compass that worked in its host
    was carried, and selection still did not turn it into food-dependent champions: link-weight
    reach is not sufficient.* This is the strong branch.
  - **(F-m) held, masked.** S8 held on ≥ 2 usable seeds, but the in-host threshold is not met.
    Reading: *the magnitude was kept on the compass's own links, and its host masked it.*
- **NOT DECIDED at ten** otherwise.

Readout (a)'s carriage X(S8) − X(S1) is reported beside the verdict and does not enter it.

**The falsifier, in plain words.**

*We planted the compass's wiring in half the founders, in every population, and gave the robots
a link-weight reach eight times the default. The planted wiring was then strong enough on its own
links to pay, but masked by its host brain at founding. We ran ten populations for 600 seasons, and
they stayed alive and kept foraging. If their champions then still steer no more by where the food
is than the same populations at the default reach, then missing **link-weight reach** is not what
stood between these robots and chemotaxis, or not the only thing.*

*It speaks for this world only.* RBT-90's world has 12 uniform items, instant regrowth and random
terrain. There the prize at a = 64 is **+0.844 [+0.618, +1.070]** (RBT-103, ten populations),
against **+2.267 [+1.461, +3.072]** for the same bodies in a patchy world (RBT-103's adversary,
coordinator's 17:46 note). A null here does not speak to patchy worlds, and a patchy-world arm
(a second flag) is the natural follow-up.

*It speaks only for reach delivered by scaling links.* It does not cover magnitude reached any
other way, such as a bias held near zero or a desaturated host (§1.4; adversary F5).

*It fails "most populations", not "all"* (§6.3).

### 6.2 Wave 0: the futility gate, fixed before it runs

Wave 0 is S1 and S8 on **seeds 801 and 4**: two sessions, run to 600 seasons as ordinary primary
arms that count in the verdict.

**One reading, at the end of season 150, of S8-801 and S8-4 only.** `peek.py` reads the S8 arm's
living designed-body genomes at season 150 through RBT-91's instruments, and nothing else: no
income, no S1, no season after 150.
- **k** = living genomes that pay: the root's sign, and own-link |a| ≥ 24.7145. A genome whose root
  is a bare founder counts at either sign.
- **n** = living genomes whose first-parent root is a planted founder.
- **μ** = the mean over those n of the operator-alone paying fraction at each genome's own depth
  (`baseline-SEED.txt`).
- **B** = the 95th percentile of Binomial(n, μ).

**Rule, one-sided:**
- A seed is **FUTILE** if k ≤ B.
- **If both seeds are FUTILE, the ticket stops**: no further arm is launched. The four wave-0 arms
  finish, and the ticket reports *"at uniform link-weight reach ×8, biases unscaled, in this
  uniform world, the operator erases the planted compass faster than selection holds it (F-b by
  construction)"*.
- **Otherwise wave 1 launches.**

The peek is futility-only. It cannot raise a SUPPORTED verdict, and the report says it happened.

Every approximation errs towards **continuing**:
- bare-rooted payers enter k but not n;
- the living population is clustered by descent, so under no selection it exceeds the binomial B
  more than 5% of the time;
- depth is capped at 30, beyond the window.

At season 150 the matched depth is about 4–6 generations (depth ≈ 2 × seasons ÷ max_age = 5, RBT-59; paper 8 §3.1), where the baseline pays at roughly
20–30%. So the gate asks whether selection has held more of a paying compass than drift keeps.

A smoke run of the peek on the 6-season S8-801 run (season 5, mean depth 0.55) read k = 28 of
n = 31 with B = 30. That is FUTILE, as expected before selection has had time, and it is not a gate
reading.

**P(STOP | H).** If H holds and a population keeps a paying compass with probability q, a seed
reads CONTINUE with probability about q, so P(STOP | H) ≈ (1 − q)², which is 0.25 at q = 0.5.
That is the gate's price, accepted by the coordinator's ruling for the saving of 16 arms.

### 6.3 Matched-null power, with q stated (adversary F7; coordinator's condition 1)

The layers come from the adversary's `power.txt`, which supersedes this design's first
`power.txt`. That file had only the verdict layer, and at d = 0.82 it agrees.
- **Per line:** readout (b) reads FOOD-DEPENDENT with probability 0.100 on bare lines (0.047
  centred). Against the fraction p of the seven window champions carrying a working a = 64
  compass, it reads 0.23 at p = 0.29, 0.62 at 0.57, 0.96 at 0.86, and 1.00 at 1.
- **q under H, stated: q_H = 0.5.** Under H, a correctly signed compass that works in its host
  earns the uniform-world prize, +0.84 items, about half a baseline income (seed 801's bests read
  1.28–1.73 at base, `RBT-103-seed-801.txt`). That gives it a selective advantage of order
  s ≈ 0.5 against the operator's loss u ≈ 0.25. At mutation–selection balance it is then kept by
  about 1 − u/s ≈ half the lineages that carry it, if selection gets a grip before the paying class
  decays (about 2–4 generations) through a masking host. q_H = 0.5 is the design's figure for
  "a population ends with food-dependent champions under H"; it is not a measurement.
- **At q_H = 0.5** (`adversary/power.txt`):
  - **P(FALSIFIED's count | H)** is **0.011** at n = 10, or 0.062 at the VOID floor n = 7;
  - **P(SUPPORTED's count | H)** is **0.623** at n = 10 (0.227 at n = 7), capped by
    P(S1 ≤ 1 | S1 has no compass) = 0.735–0.921. So **P(SUPPORTED | H) ≈ 0.46–0.57** at n = 10,
    before the paired-F condition;
  - **P(the gate stops | H) ≈ 0.25** (§6.2).
- **If H means less** (q ≈ 0.2–0.3), P(FALSIFIED's count | H) is 0.15–0.38 at n = 10. The report
  words FALSIFIED as *"selection kept a food-dependent compass in no more than one population in
  ten"*, beside these numbers.
- **The branches:** taking "held" as "keeps a paying compass" (probability q per seed), P(F-b's
  "held on ≤ 1 seed" | H at q_H = 0.5) ≈ P(Binomial(10, 0.5) ≤ 1) ≈ 0.011. F-b is informative against H, but only relative to the §6.0 baseline, which the "held"
  test uses.

### 6.4 Predictions

Revised from the first draft (P-1 0.30, P-2 0.33, P-3 0.22, P-4 0.15) for F6 and the gate, before
any arm:

| # | prediction | confidence |
|---|---|---|
| P-0 | **The gate stops the ticket after wave 0** (F-b by construction) | 0.45 |
| P-1 | SUPPORTED | 0.15 |
| P-2 | FALSIFIED after the full 20 arms: F-b 0.08, F-m 0.06, F-a 0.03 | 0.17 |
| P-3 | NOT DECIDED | 0.13 |
| P-4 | VOID | 0.10 |
| P-5 | S1 has food-dependent champions on ≤ 1 of the usable seeds | 0.85 |
| P-6 | S1's window carriage X is below 250 per 1,000 on ≥ 8 of 10 seeds. The operator alone leaves the structure in about 30% of planted lineages at window depth, and half the founders are planted, so about 150 per 1,000 | 0.60 |
| P-7 | S8 holds above the no-selection bound at 300 and 599 on ≥ 2 usable seeds (if wave 1 runs) | 0.35 |

P-0 to P-4 sum to 1.

**P-0 is the modal outcome.** At t = 0 the planted compass has no measured benefit in a K = 8 host
(§3.2), the paying class halves every two generations (§6.0), and the prize in this world is
modest. So the operator's arithmetic is more likely than selection to decide wave 0.

**P-1 is not negligible.** Once a host lets it through, a working compass is worth about half an
income. Four generations is enough for selection to hold a class with s ≈ 0.5 above a class
decaying at 0.25. And RBT-80, which planted a paying routed compass in a K = 1 host, found a
seeded-minus-drift carriage of +0.25 on two of three seeds (paper 8 §2.4).

## 7. What was run for this design (throwaway, not arms)

All of these are committed as readouts under `runs/RBT-104/`, or quoted from a scratch run's
output where stated.

1. **Check 1: byte identity at the default** (`byte_identity.txt`). `short_run.sh 801 20` is part
   2's command with no new flag, on the new code. Its `seasons.txt` is **byte-identical** to the
   first 40 rows (20 seasons × 2 faunas) of `runs/RBT-90/forage-801/seasons.txt`. Its
   `config.json` is equal to the committed one outside seasons, generations and workers, and
   `link_scale` is not written at the default. After integration was merged in (RBT-105 had added
   `ecology.breed_stream`, written as null), an 8-season re-run is still byte-identical. Its
   config differs from the committed one only by that null field, which the comparison names.
   `seed_founders.py` gives the same founder digests.
   **Platform** (coordinator's condition 3, RBT-96): every check here ran on **x86_64, MuJoCo
   3.14.0, numpy 2.4.6**. The byte identity to RBT-90 part 2 is itself the confirmation that part 2
   ran on the same kind of machine, because RBT-96 found that an ARM run diverges from an x86 one
   at generation 0. Every arm records `platform.txt` (the machine, MuJoCo and numpy), and
   `run_arm.sh` refuses to start off x86_64. `readout.py` prints the platforms and warns on any
   other. The one cited control, part 2, is x86_64 by that identity.
2. **Check 2: the flag acts where it should** (`byte_identity.txt`). The same run with
   `--link-scale 8` has holistic rows byte-identical to the default run's. **60 of 60** designed
   founders are the default founder with every link weight ×8 and every unit, biases included,
   unchanged.
3. **Feasibility at K = 8** (the check-2 run, 20 seasons). The designed fauna stayed alive
   throughout. Its alive count dipped to 42 at season 10 and was back to 60 by season 16, with
   more births than the default run. This is **not a result and did not choose K**; it shows only
   that the arm can be run.
4. **The seed** (`seed_founders.py`, seed 801). The bare founders equal a part-2 run's saved
   founders; the seeded ones have one more global unit; all ages are kept. RBT-91's predicate reads
   **30 of 60** carriers at founding in both S1 and S8, with own-link medians of 0.766 and 46.0
   and whole-brain medians of 0.373 and 0.0025. analyse.py on the 6-season S1 and S8 runs passes
   its positive control **40 of 40** in both. On S8 with the probe on, its table parses in
   `readout.py` for 51 of 51 window carriers, 19 of which re-sign as paying compasses on their
   own links.
5. **Readout (b)'s controls** (`function-controls-801.txt`), as tabled in §4.2.
6. **The seed at t = 0**: `seed_income.txt`, and `founders-t0-*.txt` pooled in `t0_pool.txt`
   (§3.2). **Matched-null power**: the adversary's `adversary/power.txt` (§6.3); this design's own
   `power.txt` is kept but superseded.
   **The operator-alone baseline**: `adversary/persistence-{801,4}.txt` and `baseline-{801,4}.txt`
   (§6.0), the latter reproducing the former at every depth they share.
   **The gate**: `peek.py`, smoke-tested on the 6-season S8-801 run (§6.2).
   **Config tolerance** (adversary F2): `configcmp.py` with `tests/test_rbt104_configcmp.py`.
7. **The drift ladder and the saturation analysis** (`drift-reach-k{1,4,6,8}.txt`,
   `saturation.txt`, `anatomy.txt`), §1.2 and §1.4. At K = 1 the ladder reproduces RBT-91's
   committed arrivals line for line.
8. **Tests:** `tests/test_link_scale.py`, 6 tests, covering:
   - every link draw is scaled and no bias is;
   - the default is the old operator;
   - the holistic operator ignores the flag;
   - config.json writes `link_scale` only when set, and round-trips;
   - the CLI flag;
   - the ecology scales designed founders only and draws nothing.

   The full suite: **290 passed**.

## 8. Files

| file | role |
|---|---|
| `rabbitstew/genetics.py`, `ecology.py`, `evolution.py`, `cli.py` | the flag |
| `tests/test_link_scale.py` | its tests |
| `runs/RBT-104/run_arm.sh` | one arm |
| `runs/RBT-104/seed_founders.py`, `founders-digests.txt` | the seed |
| `runs/RBT-104/function.py` | readout (b) |
| `runs/RBT-104/readout.py` | the pre-registered verdict |
| `runs/RBT-104/drift_reach.py`, `drift-reach-k{1,4,6,8}.txt` | §1.4 |
| `runs/RBT-104/anatomy.py`, `anatomy.txt` | §1.2 |
| `runs/RBT-104/saturation.py`, `saturation.txt` | §1.4, why K² fails |
| `runs/RBT-104/seed_income.py`, `seed_income.txt` | §3.2, the seed's cost at t = 0 |
| `runs/RBT-104/power.py`, `power.txt` | the first matched-null power, superseded by `adversary/power.txt` (§6.3) |
| `runs/RBT-104/adversary/` | the design adversary's report and probes (PR #181), cited in place |
| `runs/RBT-104/baseline.py`, `baseline-{801,4}.txt` | §6.0 and §6.2, the operator-alone baseline at every depth |
| `runs/RBT-104/peek.py` | §6.2, the futility gate, and the F-b window readings |
| `runs/RBT-104/waves.txt` | §5, the sessions |
| `runs/RBT-104/founders-t0-*.txt`, `t0_pool.py`, `t0_pool.txt` | §3.2, t = 0 on ten seeds |
| `runs/RBT-104/configcmp.py`, `tests/test_rbt104_configcmp.py` | adversary F2 |
| `runs/RBT-104/short_run.sh`, `byte_identity.py`, `byte_identity.txt` | §7 checks 1 and 2 |
| `runs/RBT-104/function-controls-801.txt` | §4.2 controls |
