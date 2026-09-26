# RBT-104 pre-registration: is magnitude the cause?

*Designer's pre-registration, 2026-09-26. **No arm has been launched.** Every number below is read
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
magnitude drift gives it, and differ in the flag alone (S1: K = 1; S8: K = 8). A secondary arm (U8)
runs part 2 itself at K = 8. It carries the ticket's literal question and measures the flag's side
effects against part 2, which it can cite because the flag at its default is byte-identical to
part 2 (§2, §7). The readouts are RBT-102's structural instrument and RBT-97/103's decoy harness,
each with a positive control that has been run (§4).

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

**The control.** For the reach alone it is **RBT-90 part 2, cited**. U8 is part 2's command,
seeds, founders, worlds and every stream, with `--link-scale 8` added, and nothing else. The flag
at 1.0 reproduces `runs/RBT-90/forage-801/seasons.txt` byte for byte (§7, check 1), and at 8 it
leaves the holistic fauna byte-identical and moves only the designed-body links (check 2). So
U8 − part 2 is paired on every seed. **For the primary contrast** the control is S1, which runs
on the same seeds with the same seeded founders.

**Quantities, from each arm's `seasons.txt`** (RBT-71's summary, committed per arm):
- **Income:** the window mean (seasons 300–599) of the designed fauna's mean lifetime score.
- **Survival:** the window mean alive, births and deaths, and extinction.
- **Viability:** the fauna never dies out, reaches season 599, and averages ≥ 30 alive in the
  window.

**Pre-registered predictions** (U8 − part 2, paired over 10 seeds, t(9)):

| # | prediction | confidence |
|---|---|---|
| S-1 | No arm of any kind goes extinct (30 of 30 viable) | 0.80 |
| S-2 | Income falls under the raised reach: U8 − part 2 window income has its t(9) interval below zero | 0.55 |
| S-3 | The fall, if any, is less than half of part 2's income (U8 ≥ 0.5 × part 2 on ≥ 8 of 10 seeds) | 0.70 |
| S-4 | Turnover rises: U8 has more births than part 2 on ≥ 7 of 10 seeds | 0.60 |

S-2 is at barely better than even. The only evidence is mechanism: saturated units are
coarser controllers. S-4 is weakly informed by the 20-season feasibility run (§7, check 3). It is
a feasibility observation and was not used to choose K.

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
null**, and fewer than 7 usable S8 arms make the verdict VOID. This finding, and §1.4's, were made
before any arm and moved the §6 probabilities: P-1 went from 0.35 to 0.30, P-2 from 0.35 to 0.33,
P-4 from 0.08 to 0.15 and P-7 from 0.50 to 0.40. The first values were in this file's draft and
were never posted.

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
unseeded arm.** U8 is run anyway, as the literal arm and the side-effect arm, and its structural
and functional results are reported descriptively with this power statement. It carries no verdict.

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
| **U8** | part 2's own | **8** | literal arm; side effects against part 2, cited | 10 |
| part 2 | part 2's own | absent | U8's control: **cited, not re-run** | (10, committed) |

**30 arms**, in three waves of 10 or fewer:
- **wave 1:** S1 and S8 on 801, 804, 805, 806 and 807;
- **wave 2:** S1 and S8 on 1, 2, 3, 4 and 7;
- **wave 3:** U8 on all ten.

Any session still PENDING 3 minutes after launch is poked once a slot frees (ticket, Gate).

**Per arm, the runner:**
1. launches `run_arm.sh` and `scripts/durable.sh every 20 runs/RBT-104/ARM-SEED rbt-104-ARM-SEED`
   as harness background tasks, with `DURABLE_WATCH_PID` set (README rule 1), and names the label
   on the ticket (rule 3);
2. after season 599, runs:
   - `measure.summarise` → `seasons.txt` and `lineage-last.txt`;
   - `analyse.py` → `rbt102.txt`;
   - `function.py` → `function.txt`;
   - `function.py --install 32` → `function-pc.txt`;
   - U8 runners only: restore `ckpt/rbt-90-SEED` into a scratch directory and run `function.py`
     on it → `runs/RBT-104/part2-SEED-function.txt`;
3. runs **`durable.sh save` once more** (rule 6), commits the per-arm files by role (config,
   tables, readouts), pushes to `results/RBT-104-ARM-SEED`, and opens a PR against integration.

`readout.py` reads the lot from the checkout. It refuses a partial read: **NOT READ** until all 20
primary arms have reached season 599.

**Cost:**
- **Ecology:** the committed rate is about 6 s per season on four cloud cores (RBT-92
  pre-registration, state doc §2). This container measured a median of 10.5 s at K = 1 and 9.9 s
  at K = 8 over 20 seasons (`run.log`s of checks 1 and 2). That makes **1.0–1.8 h per arm**.
- **Post-run:** analyse ≈ 10 min, dominated by probing window carriers, whose number in a seeded arm
  is in the hundreds. function.py is 1,344 bouts, plus 1,568 for the install control, ≈ 0.22 core-h
  (0.275 s per bout, RBT-103).
- **Total:** about 1.3–2.1 session-hours per arm. **30 arms ≈ 40–63 session-hours, and about
  6–7 wall-hours in three waves.** The U8 runners' part-2 function readouts add about 0.1 h each.

---

## 6. Predictions, confidences, and the falsifier

**The verdict** (`readout.py` §4, over the 10 seeds; "usable" = viable with both positive
controls passing):
- **VOID** if fewer than 7 of 10 S8 arms are usable. The side effect, not magnitude, is then what
  was measured.
- **SUPPORTED** if S8 has food-dependent champions on **≥ 5** usable seeds, S1 on **≤ 1**, and the
  paired F(S8) − F(S1) has its t(9) interval above zero.
- **FALSIFIED** if S8 has food-dependent champions on **≤ 1** usable seed and the paired
  F(S8) − F(S1) interval does not lie above zero.
- **NOT DECIDED at ten** otherwise.

Readout (a) is reported beside the verdict and does not enter it. It is the paired X(S8) − X(S1)
with t(9), plus the count of paying compass carriers in each arm. The reason: carriage can rise for
reasons that are not chemotaxis (RBT-80's within-arm contrasts were observational), and the ticket
asks whether chemotaxis evolves.

**The falsifier, in plain words.** *We planted the compass's wiring in half the founders, in every
population. We gave the robots a mutation reach eight times the default, so that the planted
wiring is strong enough to pay from the first season. We
ran ten populations for 600 seasons, and they stayed alive and kept foraging. If their champions
then still steer no more by where the food is than the same populations at the default reach,
then missing magnitude is not what stood between these robots and chemotaxis, or not the only
thing. Strand 3's explanation is wrong or incomplete.*

**Predictions:**

| # | prediction | confidence |
|---|---|---|
| P-1 | **SUPPORTED** (the magnitude hypothesis's own prediction) | 0.30 |
| P-2 | FALSIFIED | 0.33 |
| P-3 | NOT DECIDED | 0.22 |
| P-4 | VOID (chiefly by the saturation of §2 failing S8's install controls) | 0.15 |
| P-5 | S1 has food-dependent champions on ≤ 1 of 10 | 0.85 |
| P-6 | Carriage X(S8) − X(S1) has its t(9) interval above zero | 0.50 |
| P-7 | S8 has ≥ 1 paying compass carrier in the window on ≥ 5 of 10 seeds | 0.40 |
| P-8 | U8: ≤ 2 de novo arrivals in total, and food-dependent champions on ≤ 1 of 10 | 0.80 |
| P-9 | Part 2's own champions read not food-dependent on ≥ 9 of 10 | 0.80 |

**Reading a FALSIFIED outcome.** Readout (a) splits it in two, and the report names which:
- **(F-a)** S8 has paying compass carriers in the window, on their own links and correctly signed,
  on at least one usable seed, and still no food-dependent champions. The compass was present at magnitude and was not used or
  not selected. This is the strong falsification: magnitude is not sufficient.
- **(F-b)** S8's window carriers have lost their own-link magnitude, through the bias walk of §1.4
  or through loss of structure. The magnitude could be supplied but not held. Magnitude as a
  single reach is then not the cause as stated, and the bias gate of §1.4 is a second barrier.

**Why P-1 is not higher.** The prize is real in this world: an installed a = 64 motif pays +0.844
on average, on 8 of 10 part-2 populations (RBT-103). But the one committed experiment that planted
a *paying* routed compass and let selection run, RBT-80 at w = 32 on W4b-801 for 300 seasons,
returned **NO VERDICT** on whether selection held it. Its seeded-minus-drift carriage was +0.253,
−0.030 and +0.286 (paper 8 §2.4). Drift also erodes a compass's *direction*: in its drift arms,
direction inversions ran at 12–18 per arm against 2–3 under seeding. And RBT-102 found that under
selection in this economy no genome wires both noses into the global brain at all. That is
consistent with selection working *against* nose inputs, and it would work against the planted
input half in S8 as well.

**Why P-1 is not lower.** In S8 the planted motif's own-link response is already twice the paying
rung. The flag keeps each step's size relative to the weight it moves, so the motif erodes no
faster than a default-scale circuit erodes at its own scale. And half the planted carriers are
correctly signed for whatever direction the population settles on. Against that, at founding the
S8 host brains mask the planted compass (§2, saturation), and selection has to undo that first.

---

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
6. **The drift ladder and the saturation analysis** (`drift-reach-k{1,4,6,8}.txt`,
   `saturation.txt`, `anatomy.txt`), §1.2 and §1.4. At K = 1 the ladder reproduces RBT-91's
   committed arrivals line for line.
7. **Tests:** `tests/test_link_scale.py`, 6 tests, covering:
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
| `runs/RBT-104/short_run.sh`, `byte_identity.py`, `byte_identity.txt` | §7 checks 1 and 2 |
| `runs/RBT-104/function-controls-801.txt` | §4.2 controls |
