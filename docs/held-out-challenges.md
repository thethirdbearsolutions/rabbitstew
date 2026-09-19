# Held-out challenges: the protocol and the pre-registration template (RBT-89)

**Status.** A design document, child of the phase-2 epic RBT-88. It defines the challenge set, the
comparator, the axis, the null and the verdict rule *before* any run that uses them, and it gives
the template a future arm fills in. **No simulation was run for this document; every number in
it is cited to the ticket or committed readout it comes from**, and where the programme does not
have a number the document says so and names the measurement that would produce it (§13).
Filed for review with a named adversary, whose job is to find the reading this protocol would
let a hopeful author take (§14).

The owner's goal, in the owner's words: a methodology for evolving morphologies that "hold up
against novel environmental challenges" and "outcompete or at least fight to a draw" against "a
top-down-engineered body with a brain grafted in" (project doc *Research goals, aesthetics and
endpoint*). No arm to date has had a held-out environment: every arm evolves and is read in the
same world (RBT-88). This document is that instrument. "All in on evolution" is the reading it
protects against, not with.

---

## 1. The baseline the challenges are held out from

"Held out" means: a world the population never sees during evolution. The evolution phase of
every challenge arm is the **dense foraging baseline**, exactly the configuration RBT-10 ran on
seeds 802 and 803 and RBT-71 ran on 804, 805 and 806 (`runs/RBT-71/forage-80x/config.json`):

```
rabbitstew ecology --seasons 600 --capacity 60 --challenge foraging --group-size 4 \
  --brain-model foraging --food-items 12 --food-radius 3 --eat-radius 0.35 --food-decay 1.0 \
  --work-cost 0.03 --living-cost 0.25 --initial-energy 3 --birth-threshold 3 --birth-cost 1 \
  --duration 15 --mass-budget 15.34 --conventional-topology --terrain random --random-start \
  --score food --seed SEED
```

with `--max-age 60` (the default; every ecology arm in the programme ran at it, RBT-59) and
founders' ages staggered over `[0, 60)` (the default). The economy: energy from eating minus a
basal cost of 0.25 a season and a work cost of 0.03 per kJ of actuator work; breed at 3, pay 1;
die at zero energy or at age 60; no fitness function, no ranking (RBT-10). Two populations live in
it, each in its own bank of arenas of four robots sharing twelve items in a 3 m disc: the
**co-evolved** (holistic) population, bodies and brains from random morphologies, and the
**designed** (conventional) population, the Pioneer body with an evolvable brain.

What the baseline has established, and what a challenge is read against (RBT-71 A, closing
comment; RBT-10, closing comment):

| quantity | 801 | 802 (w 0.03 / 0) | 803 (w 0.03 / 0) | 804 | 805 | 806 | source |
|---|---|---|---|---|---|---|---|
| holistic minimum alive at the season-11 wave | 7 | 31 / 32 | 42 / 36 | 26 | 8 | 28 | RBT-10, RBT-71 |
| sustained crossover (holistic income > designed) | 83 | 18 / 30 | 11 / 19 | 17 | 27 | 22 | RBT-10, RBT-71 |
| mean holistic − designed income, seasons 100–599 | (+0.46 at 599) | +0.21 / +0.13 | +0.13 / +0.19 | +0.212 | +0.109 | +0.045 | RBT-10 §3, RBT-71 `readout-all.txt` |
| fraction of seasons 100–599 holistic leads | — | — | — | 0.976 | 0.832 | 0.702 | RBT-71 |
| holistic yield heritability (evals ≥ 5) | 0.51 | 0.32 / 0.44 | 0.28 / 0.28 | 0.399 | 0.382 | 0.337 | RBT-10, RBT-71 |
| designed yield heritability | 0.24–0.39 | 0.14 / 0.39 | 0.20 / 0.25 | 0.229 | 0.276 | 0.252 | RBT-10, RBT-71 |
| holistic founders in the final ancestry | 1 | 3 / 3 | 3 / 3 | 1 | 1 | 3 | RBT-10, RBT-71 |
| median descent depth at 599 (holistic / designed) | — | — | — | 22 / 19 | 20 / 18 | 22 / 21 | RBT-71 |

The designed side's income is flat at +0.8 to +1.1 a season throughout in every run (RBT-10 §5);
806 ends at parity (RBT-71 closing). Every co-evolved best is a blind mower: no nose lesion changes
its yield on five seeds (RBT-10 §5), and twenty champions across two founding populations do not
beat their own trajectory-preserving null (RBT-84, RBT-39). Depth: 600 seasons is a median of
~20 reproduction events, fitting **depth ≈ 2 × seasons ÷ max_age** (RBT-59: median 20, range 18–24
over fourteen population-rows).

**What the robots can sense at all.** The foraging brain's sensor vocabulary is `contact`, `up`,
`velocity`, `joint_angle`, `joint_velocity`, `height`, `oscillator`, `food`, `agent`
(`rabbitstew/genotype.py`, `FORAGING_SENSOR_SOURCES`). The `food` and `agent` sensors read only the
summed intensity of the smell at the sensing segment, no direction (RBT-17). **There is no sensor
for energy, work, age, season, or the number of items in the world.** Anything a challenge changes
in those quantities is invisible to every robot by construction.

---

## 2. The challenge set

Four challenges. Each is **one flag changed** from the baseline command in §1, applied at a
pre-registered onset season (§5) to a population that evolved under the baseline. Each was chosen
because the programme has already measured its endpoint on random founders, so the arm's result
can be read against a known number rather than a guess.

| id | challenge | the one flag | measured endpoint (random founders, from season 0) | perceivable? | kind |
|---|---|---|---|---|---|
| **C1** | crowding: eight robots per arena | `--group-size 8` | no extinction; population incomes near parity; the designed *bests* out-eat the co-evolved bests two to one (RBT-17) | in principle by `agent`; never wired by an evolved robot | competition |
| **C2** | dearer work | `--work-cost 0.08` | both populations extinct, designed at season 13, co-evolved at 26 (RBT-21, W6′) | **no**, by construction | budget |
| **C3** | scarce food, at the bootstrap line | `--food-items 6` | co-evolved starved out by season 15; designed bottlenecked to 11 by 17 and extinct at 51 (`docs/foraging-world.md`, "Six items") | in principle by `food`; the evolved side does not read it | budget |
| **C4** | the furniture removed | `--terrain flat` | none measured in the ecology | **yes**, by `contact`, `height`, `up`, joint sensors, at weights the operator does reach | perceivable |

### C1. Crowding: `--group-size 8`

RBT-17 ran eight robots per arena at twelve items from season 0 on seed 801. Holistic 59 → 3 at
season 11 (one bad season from extinction), back to 60 by 38; no extinction on either side;
crossover at 45; hundred-season mean incomes holistic +0.98 / +0.93 / +1.00 against designed
+0.81 / +0.92 / +0.96 over seasons 100–199 / 300–399 / 500–599; founders 1 / 5; heritability
0.34 / 0.27. **On the income axis the two populations were nearly equal** (the baseline's late
holistic lead of +0.5 to +0.7 shrank to +0.05 to +0.15); what reversed was the *bests*: in eights
the designed season-590 best ate 2.34 items per robot against the co-evolved 1.14, and the
co-evolved bests spent 7–14 kJ a season for 0.9–1.5 items where the baseline's spent 2–6 kJ for
2.1–2.5. So RBT-88's "reverses at eight robots" is a statement about champions; on the population
axis this document uses, C1's measured endpoint is **parity, not reversal**. A future arm's point
prediction for C1 must say which it expects and why.

Perception: eight robots double the `agent` smell in the arena, so crowding is perceivable in
principle. In practice no co-evolved individual in the final population of 60 carried an `agent`
sensor, and the designed side, which carries three by design, lost 0.12 of 2.34 items per robot
when they were blanked, inside the seed noise of 0.6–0.7 (RBT-17 §3). **C1 is unperceived by the
evolved side and unused by the designed side.** It selects on how a standing gait shares a
depleted field.

Capacity 60 ÷ 8 leaves one group of four each season (RBT-17); the arm reports which robots that
group held, since a group of four in an eight-robot economy is the baseline world.

**Claim tested:** the owner's own, in full: under a shift both bodies survive, does the co-evolved
body out-earn the designed one, draw, or lose. C1 is the only challenge in the set that can
return every class in §9.

### C2. Dearer work: `--work-cost 0.08`

The work-cost coefficient is what buys cheapness: under 0.03 the co-evolved bests on 801 and 802
mow on 2–6 kJ a season; under 0 they are whatever drift leaves, and 803's free-arm bests spend
12–16 kJ (RBT-10 §5). The designed side spends 14–29 kJ a season in every probed best (RBT-10 §2).
At 0.08 per kJ random founders of both kinds went extinct (RBT-21, W6′: designed at season 13,
co-evolved at 26), by a different route from 0.15 (RBT-18, W6: designed at 3, co-evolved at 33):
at 0.08 the designed founders were sorted over thirteen seasons with mean gain climbing from −1.16
to +0.50, "the clearest selection for economy on the designed body in the fan-out", and extinction
came through newborns, who start with `birth_cost` = 1 energy and spend it on random driving before
eating twice (`docs/foraging-world.md`, W6′ row and the RBT-21 lesson).

Arithmetic on those cited figures, not a measurement: a designed robot at 14–29 kJ is charged
0.42–0.87 a season at 0.03 and **1.1–2.3 at 0.08**, against a designed income of +0.8 to +1.1
(RBT-10 §5). A co-evolved mower at 2–6 kJ is charged 0.16–0.48 at 0.08. **C2 is therefore
expected to bankrupt the designed population unless its evolved brains are already far cheaper
than any probed best, and a future arm must predict that outright** (§9, outcome class D). It is
kept in the set because it is the one challenge no robot can perceive by construction: nothing in
the vocabulary reads energy or work. C2 selects on kJ per item and on nothing else, which is the
purest form of "standing morphology and gait only" the programme can pose.

A rung with no measured endpoint, `--work-cost 0.05`, is the same challenge at a smaller
magnitude; an arm may pre-register it instead, and must say that its endpoint is unmeasured.

**Claim tested:** survivorship of the co-evolved population at an economic boundary the designed
body's budget is not expected to survive. That is a different claim from the owner's (it is about
one body's cheapness, not two bodies' contest), and a C2 result is reported as such.

### C3. Scarce food: `--food-items 6`

Below roughly six to twelve items in a 3 m disc nothing random forms a breeding population, so the
baseline result is stated *at a density* (RBT-71 description, Deliverable B). The programme's
own six-item arm: the co-evolved population starved out at season 15 (37 deaths at season 11, two
survivors eating a twelfth of an item a season); the designed population bottlenecked to 11 by
season 17 with a positive mean gain of +0.32, held at five to nine for twenty seasons, and went
extinct at season 51 anyway, "at that size a couple of unlucky seasons remove the eaters faster
than they breed" (`docs/foraging-world.md`, "Six items"). At three items both populations are
extinct by season 24–31 (same doc, sparse arm). RBT-19's persistent world found the same line from
the other side: twelve spots at a 45 s regrow delay settle at a season-start crop of 5.8 and
bankrupt the founders (RBT-19, coordinator comment).

Arithmetic, not a measurement: a blind mower's yield is path × twice the eat radius × the food
density (`docs/foraging-world.md`, line 79), so halving the items halves a mower's income, from
the +1.0 to +1.3 plateau (RBT-10 §5) to about +0.5 to +0.65, still above the 0.25 basal cost; the
designed side's income halves from +0.8 to +1.1 to about +0.4 to +0.55 against a work charge of
0.42–0.87 plus 0.25 basal. **C3, like C2, is expected to bankrupt the designed population first**,
and a future arm predicts that in its template. The untested question C3 poses is whether an
*established* population, unlike random founders, can hold at the bootstrap line: the six-item arm
above is the founders' number, not an evolved population's.

Perception: the `food` sensor reads summed intensity, so a halved density is a halved reading in
principle. In practice not one co-evolved best in five seeds changes its yield when the food sensor
is blanked (RBT-10 §5; RBT-17 §5: 49 of 60 final lumps carry food sensors that change nothing), so
**C3 is unperceived by the evolved side**; the designed side's nose, where it does anything, is a
brake, a throttle or a sweep modulator, never a compass (RBT-66; `docs/foraging-world.md` §"The
rule that stands").

**Claim tested:** as C2, survivorship at a boundary, here the bootstrap line for food; whether an
established population holds where random founders could not. Not the owner's contest claim.

### C4. The furniture removed: `--terrain flat`

The baseline resamples fourteen random obstacles every season (heights 0.03–0.3 m, footprints
0.15–0.7 m, `runs/RBT-71/forage-804/config.json`). Paper 3 established, in the arena, that both
populations' champions win by driving until "the furniture" stops them ("straight ahead and let
the furniture stop me", `docs/paper-3-let-the-furniture-stop-me.md`, abstract). Whether the
foraging gaits are likewise built around clutter has never been measured: every probe in the
family runs the best on the run's own terrain. **C4 removes the obstacles**, which is the one
terrain-class change that (a) is a genuine held-out world for a population that evolved among
clutter, (b) has no built-in bias toward either body, and (c) leaves the food and the economy
untouched. The other classes are excluded: `plateau` is a raised disc "higher than the fixed
body's wheel radius, so it cannot be driven up" (`rabbitstew/world.py`), which is a challenge
designed against the Pioneer and would be the hopeful author's choice; `rails` are 0.1 m bars whose
traversability by either body is unmeasured; a changed obstacle *count* (`--obstacles 28`) is the
same distribution, not a held-out one.

Perception: obstacles are perceived through `contact`, `height`, `up`, `joint_angle` and
`joint_velocity`, sensors that evolved bests do wire and do use: RBT-10's 803 season-100 best loses
59% of its yield when its height input is blanked; RBT-17's holistic bests carry `height` and
`joint_angle`; 802's season-590 designed best is a 16 m runaway with every sensor blanked. These
are one-bit contact and posture readings, expressible at the w ≈ 1 the operator lives at (RBT-62:
median |w| 0.85–1.13), not a gradient. **C4 is the one challenge the robots can perceive with
the wiring they have**, so it is a different kind from C1–C3: adaptation *during* the challenge is
not excluded by the weight ceiling, only by depth (§10). A future arm reports C4 separately from
the unperceived three and does not pool them.

**Claim tested:** whether gaits built among clutter hold on open ground, on both bodies, with the
contest of C1 available if both survive; and, alone in the set, whether anything is re-wired
during the challenge.

### Excluded candidates, and why

- **The persistent world** (RBT-19): three flags (`--food-items 26 --food-patches 3
  --patch-radius 0.6 --regrow-delay 45`), and it buys its gradient partly out of heritability
  (0.51 → 0.25). Not one flag; not a challenge but a different world.
- **Smell changes** (`--smell`, `--food-decay`; RBT-13, RBT-22): they change the instrument the
  robots read, not the world they live in, and every evolved side is blind to the instrument anyway.
- **The arena bout in any form**: disqualified as an axis (§6) and not a world.
- **Season length** (`--duration`): cannot be varied alone, because with instant random regrowth
  food arrives as a standing crop at each spawn (RBT-20, W3′: both extinct by season 9).
- **The merged arena** (`--merge-after`, RBT-3): machinery in place, nothing run on it; it makes the
  other population an opponent and reintroduces RBT-74's covariate. Not used here.

---

## 3. What the robots can and cannot perceive, and what that makes a challenge

The fact (RBT-62, RBT-67, RBT-87, RBT-78, RBT-91): not one weight in 19,892 evolved links
reaches 8 (RBT-62), and the ceiling is the operator's own stationary distribution, not a clamp and
not selection, so no depth moves it (RBT-91, `docs/rbt-91-weight-scale-decision.md`, whose
figures are cited and not restated here). A correctly wired compass is null at a = 16 and pays
from a = 32 (RBT-67, RBT-69; "perception pays at 16–32" in the tickets means this rung), and the
prize is still rising at a = 384 with no turnover (RBT-67). The encoding cannot express the direct
four-link motif; the routed motif reads at depth 2 (RBT-87); drift never proposes the direct one
(0 of 10,000, RBT-78), and no instrument on the head has counted proposals of the routed one
(RBT-91 adversary round, `docs/runs/RBT-91-adversary.txt`, which also shows that the routed
motif's magnitude is a product of four free weights and the interneuron's slope, so what binds is
the structure and, under drift, the operating point, not the single-weight scale). Two things
follow. The ceiling is not a compute problem: a larger machine buys seasons, and seasons do not
move a stationary distribution. And under the operator as it stands the robots do not perceive the
challenges below at any depth this programme will reach.

Consequence for this protocol, which RBT-91 decides and this document states in both forms:

- **Under option A (leave the operator, RBT-91)**: C1, C2 and C3 are **unperceived**. C2 by
  construction (no sensor reads energy or work); C1 and C3 because the sensor that could read them
  is carried and not wired on the evolved side, and, on the designed side, wired at magnitudes
  that do not steer. **These challenges select on standing morphology and gait only.** "Robust
  against a novel challenge" then means **survivorship of standing morphology and gait through a
  shift, not adaptation during it** (the words of the RBT-91 decision,
  `docs/rbt-91-weight-scale-decision.md`), which is faithful to Gould, whose events select on
  what is already there. This must be written in every C1–C3 pre-registration in those words,
  and the axis (§6) and the falsifier (§9) are claims about realised income, never about
  perception: a class-A result says the co-evolved body earned more under the shift, not that it
  sensed the shift.
- **C4 is perceivable under either option**, because contact and posture are one-bit readings at
  w ≈ 1. It is the one challenge on which "re-adapts" could mean a new use of an existing sensor.
- **Under option B (widen the operator)**: no challenge arm runs under the widened operator until
  RBT-91's positive control has passed and been adversaried, and a challenge arm under it is a
  different arm from one under option A; the two are never pooled.

---

## 4. The fair comparator

**The comparator is the designed population that every ecology run already carries**: sixty
Pioneer bodies (`rabbitstew/fixed.py`, `pioneer_genotype`, rich sensors, the foraging sources) with
random-weight brains at season 0, evolved in the same economy, in the same run, under
`--conventional-topology` so that the brain's topology evolves as well as its weights and only the
body differs between the populations (RBT-10 command). This is the comparator RBT-71 A measured
against on four founding seeds and the one whose income is heritable even under drift (0.24–0.35 on
the neutral controls' designed side, 3 of 3 seeds, RBT-71 closing).

**How many seasons the graft's brain gets: exactly the seasons the co-evolved population gets
before the onset, T (§5), in the same run.** Not fewer, not more. Why:

1. **Same seasons is same depth.** Depth is set by `max_age`, not by the economy or the body:
   fourteen population-rows at `max_age` 60 all land at 18–24 reproduction events in 600 seasons,
   designed and co-evolved alike (RBT-59; RBT-71: designed 18–21, co-evolved 20–22). A graft that
   evolved for fewer seasons would be a handicapped comparator; one that evolved for more would be
   a head start. At T = 400 the law gives ≈ 13 events for both.
2. **The designed side's income plateaus early**, at +0.8 to +1.1 from about season 30 in every
   run (RBT-10 §5; RBT-71 100/300/500/599 columns), so extra seasons would not move it; the
   co-evolved side plateaus at +1.0 to +1.3 from season 30 on fresh seeds (RBT-10 §5). Both are on
   their plateau by T.
3. **"Grafted in" is satisfied and "hand-tuned" is excluded.** The brain arrives by the same
   selection the co-evolved brains arrive by. No controller loaded from another run
   (`--from-conventional`), no constant-drive controller (`rabbitstew fixed --drive`), no controller
   from an arena run (whose score carried no heredity, RBT-74) is a comparator under this protocol.

**Separate RNG streams: a prerequisite build, not an assumption.** RBT-85 gives `Experiment`
(the arena) three streams, `SeedSequence(seed).spawn(3)` → holistic, conventional, terrain, with a
byte-identity test; its pre-registration states "the ecology keeps its own single stream,
untouched" (RBT-85, pre-registration comment). On the integration head the ecology draws
founders of both populations, their staggered ages, the per-season terrain and start seeds, the
grouping permutation and every breeding decision from one generator
(`rabbitstew/ecology.py`, `self.rng = np.random.default_rng(evo.seed)`). So today a change to one
population's flag moves the other population's draws from the first season on, which is exactly
the defect RBT-74 found made pairing by seed harmful (paired SE 0.073 against unpaired 0.063,
correlation −0.41). **Before any challenge arm runs, `Ecology` gets the same three streams**,
with the terrain-and-start stream shared by both populations (they must meet the same worlds) and
the same pinning test: two runs at one seed differing only in the challenge flag write
byte-identical `lineage-last.txt` rows for whichever population the flag does not touch until the
population composition itself diverges. This is a build ticket, filed separately; it is one flag's
worth of change and is pre-registered as such.

Within a run the two populations do not meet (separate arena banks, RBT-19's per-fauna rule), so
the opponent covariate of RBT-74 does not arise here. What both populations share is the terrain
and start sequence, which is why that stream stays shared.

---

## 5. The onset: how a population that evolved under the baseline meets the challenge

The ecology is not resumable and has no mid-run flag switch. What exists on the integration head
is `--from-run RUN` (`--from-holistic`, `--from-conventional`): start both populations from a saved
run's `<kind>/final/` (`rabbitstew/ecology.py`, `load_population`). What it restores and what it
does not (`Ecology.__init__`, lines 154–168):

| carried into stage 2 | reset at stage 2 |
|---|---|
| every individual's body and brain | **energy, to `--initial-energy` (3) for everyone** |
| every individual's **age** (so the cohort structure survives the onset) | evaluations and score sum (income history starts again) |
| the population's composition at T (all 60 of each kind) | **descent: `parents` is cleared**, so the stage-2 lineage does not reach stage-1 ancestors |
| | the RNG stream (a new seed for stage 2) |

So the protocol's onset is **two-stage**:

- **Stage 1**: the baseline command of §1 for T seasons, `--out runs/<TICKET>/stage1-<seed>`.
- **Stage 2, three arms from the same saved population**, each `--from-run runs/<TICKET>/stage1-<seed>
  --seasons W --seed <seed2>`:
  - **challenge**: the baseline command plus the one challenge flag;
  - **control**: the baseline command, no flag changed;
  - **null**: the baseline command, no flag changed, with the random cull of §8 applied at season 0
    of stage 2.

The energy reset applies to all three arms identically, so it cancels in every between-arm
contrast (challenge − control, challenge − null) but **not** in a before/after contrast against
stage 1: everybody starts stage 2 with 3 energy, which alone postpones starvation by up to
(3 − 1)/0.25 = 8 seasons relative to a newborn. Therefore **"before" is read from the control arm's
stage 2, never from stage 1's last seasons**, and stage 1's tables serve only to place the onset
(§8) and to state the plateau. The cleared descent means founder survival and descent depth across
the onset cannot be read from `lineage-last.txt`; the stage-2 depth counts from T.

**Build item, named and not assumed**: a true mid-run onset (`--shift-at SEASON` with the one flag
taking effect from that season, energy and descent intact) is a small change to `Ecology.step`; it
removes the energy reset and the descent break. Until it lands, the two-stage route above is the
protocol, and every pre-registration states which route it used. The two routes are not pooled.

Budget: T = 400 and W = 200 keep an arm at the family's 600 seasons; at RBT-71's four workers a
600-season baseline run is about 65 minutes (RBT-19) to four hours (RBT-10), and C1's eight-robot
seasons are slower (RBT-17: ~9 s a season at three workers).

---

## 6. The axis: realised income in the shared economy

**The quantity is `mean_lifetime_score`** in the committed per-season table, and every readout
on it is a claim about what a body earned, never about what it perceived (§3; RBT-91). It is
the value in `seasons.txt` (one row per season and population, RBT-86): the mean over living
individuals of their lifetime mean
per-season score, where a season's score is food eaten times its value minus the work cost of that
season's actuator effort; the basal cost is charged separately and is not in the number (RBT-10
§1). It is what RBT-71 A read on four seeds and what carries heredity even under drift.

**Never the arena bout score**, which carried no heritable signal anywhere in the family (RBT-71
description; RBT-74: body-changed children 0.11–0.26 read as "almost entirely noise", conventional
0.00–0.08) and reads the opponent (RBT-74: opponent composition predicted 103% of the headline).

**Never the merged arena** (RBT-3): "shared economy" in this document means the same economy rules
in separate arena banks, which is the measured configuration. Sharing an arena would make the other
population an opponent and the opponent a covariate (RBT-74's README rule).

The three readouts, all from `seasons.txt`, all windowed relative to the onset (window edges in
§8):

| readout | definition | what it answers |
|---|---|---|
| **R-body** (primary) | mean over the readout window of (co-evolved − designed) `mean_lifetime_score`, challenge arm, per seed | the owner's question: which body earns more under the challenge |
| **R-shift** | per population, mean over the window of (challenge − control) `mean_lifetime_score`, per seed | what the challenge cost each body, read against the population's own unchallenged course |
| **R-null** | per population, (challenge − null), per seed | whether the challenge did more than a turnover event of the same size would |

Beside every income number: `alive`, `births`, `deaths` for the same window, and the per-seed
list with the zero count (RBT-38 standing rule). An extinction is `alive` reaching 0 and is its own
outcome class (§9), never averaged into an income.

---

## 7. The effect size an n can resolve, and the n for the smallest effect worth claiming

**The smallest effect worth claiming on R-body is 0.10 items per robot per season.** Reason: it is
the smallest sustained lead the programme has accepted as a lead (RBT-71: seed 805 at +0.109 over
seasons 100–599 was read as a lead; seed 806 at +0.045 was read as "ends at parity"), and it is
the threshold RBT-74 and RBT-85 pre-registered for the arena's paired mean (±0.10, a different
unit, cited for the form).

**What the programme knows about the spread of that quantity between seeds.** The seven
committed 500-season leads on fresh seeds are +0.21, +0.13, +0.13, +0.19 (RBT-10: 802 and 803 at
work cost 0.03 and 0) and +0.212, +0.109, +0.045 (RBT-71: 804, 805, 806). **Arithmetic on those
cited values, not a measurement**: mean 0.147, standard deviation 0.061, on seven values of which
the 802 and 803 pairs share founders (so the effective n is nearer five). Two standard errors of a
mean of n such seeds:

| n seeds | 2 SE (500-season windows) |
|---|---|
| 4 | 0.061 |
| 6 | 0.050 |
| 10 | 0.039 |

So **on a 500-season window, n = 4 would resolve 0.10, and n = 6 resolves 0.05.** But the
protocol's readout windows are 60 and 100 seasons (§8), and the spread of a 100-season mean is
larger: RBT-17's three hundred-season means on one run vary 0.93–1.00 (co-evolved) and 0.81–0.96
(designed), so the within-run block-to-block variation of a single population's 100-season mean is
of order 0.05–0.08 before any between-seed term. **The between-seed SD of a windowed lead was
measured for this document's review from the committed tables alone** (`runs/RBT-89/window_sd.py`
on `runs/RBT-71/forage-80x/seasons.txt`, readout `docs/artifacts/RBT-89-window-sd.txt`; a file
analysis, not a run), on three seeds, 804, 805 and 806, which is three draws (801's and RBT-10's
tables are not on the integration head):

| window | pooled between-seed SD of the lead | r = 2 SD/√n at n = 4 / 6 / 10 |
|---|---|---|
| 60 seasons | 0.111 | 0.111 / 0.091 / 0.070 |
| 100 seasons | 0.108 | 0.108 / 0.088 / 0.068 |
| 500 seasons | 0.084 (three seeds; 0.061 on the seven values above) | 0.084 / 0.069 / 0.053 |

So **on the protocol's own 100-season recovery window, four seeds cannot reach class B at all
(r = 0.108 > 0.10) and six seeds can, just (r = 0.088)**. That is why **n = 6 seeds is the
protocol's floor** (it also matches RBT-92's "≥ 6 founding seeds passing the diversity rule"), and
why ten is the number an arm should want. The SD of three values carries its own error of about
±40%, so every arm recomputes the line from its own stage-1 tables and quotes both figures; if the
realised r exceeds 0.10, the protocol returns only classes A, C, D, E or F for that arm (§9).

**The power lines the scripts print, quoted, so the template's line has a form.** Every lesion
readout in the family prints its resolving power; the income readout must do the same.

- `scripts/forage_lab.py` (per champion, 64 paired draws): "`power at n = 64 draws: |t| >= 2.5
  resolves a lesion difference of +0.97 items or larger (median per-draw sd of the paired
  difference 3.09).`" and "`resolving 25% of intact (0.70 items) needs about 115 draws. THIS n
  CANNOT TEST a 25% effect.`" (RBT-84, `runs/RBT-84/lab_g590.txt`; the other bests read +0.62 to
  +0.72). This is why no lesion effect is claimed without n ≥ 64 paired and the bar at that n is
  ~+0.93 items (RBT-38, RBT-28, RBT-84; `runs/RBT-84/champion_units_t.txt`).
- `runs/RBT-74/readout.py` (per arm, four paired seeds): "`instrument: unprotected final-fifth
  checkpoint SD 0.127 (mean over seeds) -> SD of a final-fifth mean 0.038; paired difference of two
  such means has SD 0.054; smallest paired mean difference resolvable at 2 SE with n=4: 0.054
  (checkpoint noise only) versus 0.146 from the observed spread of the paired differences (includes
  seed-to-seed drift)`" (`runs/RBT-74/readout.txt`). RBT-74's observed +0.064 sat inside 0.146 and
  was reported as "the instrument could not see an effect of this size", not as "no effect"; RBT-74's adversary showed that +0.064 was the opponent's composition (predicted +0.066), and
  RBT-85's rerun of the same eight seeds under paired streams reads −0.049, 95% t(3)
  [−0.122, +0.025] (RBT-85 adversary round).
- RBT-85's pre-registration, for the same instrument under separate streams: "2 SE of the paired
  mean lands at ~0.08, between 0.05 and 0.12 (confidence 0.6)", a prediction, with the realised
  figure to be computed three ways and quoted.

**The challenge arm's readout script prints the RBT-74 line for the income axis**, in this form,
from `seasons.txt` alone: `instrument: control-arm window SD of mean_lifetime_score <s> -> SD of a
W-season window mean <s/√W>; paired (co-evolved − designed) window difference SD <…>; smallest
R-body resolvable at 2 SE with n=<n> seeds: <…> (season noise only) versus <…> from the observed
spread of the per-seed differences.` Both figures are quoted in the report; the verdict rule (§9)
uses the larger.

---

## 8. The null, the cohort cycle, and where the onset goes

### The natural cohort cycle, measured first

RBT-80 found that a drift arm (no starvation, free breeding, turnover by `max_age` only) undergoes
a mass replacement late in the run: mean age 40.1 → 9.1 between seasons 290 and 299, **40 of 60
individuals turned over in ten seasons, identically in all three seeds**, and in none of the
selected arms (7–14 of 60 in the same window) (RBT-80, three-seed report §5). It is the
staggered founder cohort ageing out together under `max_age`; it showed up because the delegate
checked the readout point's demographic state instead of reading it, and it moved the verdict
quantity by +0.14 on one seed and −0.15 on another. **A challenge placed on such a transient reads
the transient.**

Selected arms have not shown a 40-of-60 transient, but the cycle has never been measured on a
selected ecology arm as such (§13). So the protocol measures it, per seed, from stage 1 before the
onset is fixed:

- `rabbitstew history runs/<TICKET>/stage1-<seed>/history.json` prints per season and population
  alive, births, deaths, mean age and max age (`rabbitstew/cli.py`, the `history` command).
- **A turnover peak is any ten-season window in which `deaths` for one population reach 20 of 60**
  (a third of capacity; half the RBT-80 drift transient; above the 14 of 60 the selected arms
  showed). The season-11 starvation wave (30–41 deaths on every seed, §1) is one by definition and
  is the founding bottleneck, not the cycle.
- **The onset T is placed at least 20 seasons after the last peak, and the readout windows must not
  contain a season at which the founding stagger predicts one** (multiples of `max_age` = 60 from
  the season-11 wave, i.e. 71, 131, 191, 251, 311, 371, 431, 491, 551, are the candidates; whether
  they carry a peak on a selected arm is what the measurement shows). Default **T = 400** when no
  peak after season 100 exists on the seed; otherwise the pre-registration states the seed's T and
  why.
- **Build item under RBT-86's rule**: `seasons.txt` today carries `season, population, alive,
  births, deaths, mean_lifetime_score, best_lifetime_score` (`runs/RBT-71/measure.py`,
  `SEASON_KEYS`) and not `mean_age` or `max_age`, which are in `history.json` only. The challenge
  arm's summariser adds `mean_age` and `max_age` as columns, so the cycle is re-derivable from the
  committed table by someone who never held the bulk.

### The readout windows, relative to onset

Onset is season 0 of stage 2. Windows, fixed before the run:

| window | seasons of stage 2 | what it is for |
|---|---|---|
| **transient** | [0, 60) | one `max_age`: every individual alive at onset is dead or replaced by its end |
| **recovery** (primary for R-body) | [60, 160) | the first hundred seasons in which nobody alive evolved under the baseline |
| **tail** | [160, 200) | reported, not scored; a check that the recovery window was not a second transient |

"Recovery time" is the first season of stage 2 from which the challenge arm's `mean_lifetime_score`
stays within the control arm's own window spread (§7's line) of the control for 20 consecutive
seasons; reported per population per seed; "not within W" is a legitimate value.

### The null: a random cull of the same size, at the same season

**In the owner's terms: a change at the challenge boundary is read against the population's own
turnover.** The null arm is stage 2 with no flag changed and, at its season 0, **k randomly chosen
living individuals of each population removed**, where k is that population's *excess deaths* in
the challenge arm's first ten seasons: deaths in the challenge arm over seasons [0, 10) minus deaths
in the control arm over the same seasons, floored at 0. The freed slots refill by the economy's
own breeding, which is what "re-seeding" means here: the population re-seeds itself from its own
breeders. The null's k therefore depends on the challenge arm having run, which is fine: the
*rule* for k is pre-registered, k is not.

- The alternative reading, refilling the culled slots with **fresh random founders**, is not this
  protocol's null: it injects founder-quality variation (RBT-84: two founding populations differed
  in oscillator-drive base rate 25% against 22% and in what selection did with it), which RBT-90
  exists to control, and it would read as a second founding, not a turnover.
- If k = 0 for a population (the challenge killed nobody beyond the control in ten seasons), the
  null arm for that population is the control arm and R-null for it equals R-shift; the report says
  so.
- **Mechanism, a build item**: no flag culls today. The nearest thing on the head is to copy
  stage 1's `final/` directory, delete k randomly chosen genotype files per population (drawn from
  a stated RNG seed, the list committed as `cull-<seed>.txt`), and `--from-run` the copy;
  `load_population` cycles the remaining files to fill 60 slots, so this **clones** survivors rather
  than leaving slots free, which is not the null. A `--cull SEASON:K` flag that removes K random
  living individuals and leaves their slots free is the build; until it lands the null arm cannot
  be run honestly, and a pre-registration that lacks it says so and scores R-null as not run.
- **Validation before use**: the instrument that reads the event is validated on the cull before it
  reads the challenge (RBT-92's rule). Concretely, R-null on a seed's control against its own cull
  at k = 20 (the peak threshold) must be resolvable by §7's line, or the instrument cannot see a
  turnover and cannot be trusted to see the challenge.

---

## 9. The verdict rule and the falsifier

**The falsifier, in the owner's own words: "the designed body wins on the held-out challenge."**

Scored on R-body in the recovery window, per seed, n ≥ 6 seeds passing RBT-90's diversity rule,
with `r` the larger of the two resolvable figures the readout prints (§7). Outcome classes, each
its own line in the report, never merged:

| class | rule | reads as |
|---|---|---|
| **A. co-evolved wins** | mean R-body ≥ +0.10 **and** ≥ 5 of 6 seeds positive (≥ 8 of 10 at n = 10) **and** \|mean\| ≥ r | the aesthetic bet holds on this challenge |
| **B. draw** | \|mean R-body\| < 0.10 **and** \|mean\| ≥ r would have been resolvable, i.e. r ≤ 0.10 | "fight to a draw", the owner's second acceptable outcome, and it is only a draw if the instrument could have seen a win. **Reachable only at n ≥ 6 on the measured spread** (§7: r = 0.108 at four seeds, 0.088 at six); an arm whose realised r exceeds 0.10 cannot return B and says so before it runs |
| **C. designed wins** | mean R-body ≤ −0.10 **and** ≥ 5 of 6 seeds negative **and** \|mean\| ≥ r | **the falsifier**; the owner's sentence, written down before the run |
| **D. designed bankrupt** | in the transient or recovery window, on ≥ 5 of 6 seeds, the designed population's window mean income falls below the basal cost 0.25, **or** its `alive` falls below 12 of 60 (a fifth of capacity; the six-item designed population held five to nine for twenty seasons and then went extinct, `docs/foraging-world.md`), **or** it reaches 0, while the co-evolved population does none of these | the challenge exceeded the comparator's energy budget; **not** class A, whatever R-body reads on the seeds where both survive. The test has the same income form as class E, so a comparator reduced to four starving robots is D, not A |
| **E. both fail** | both populations reach 0, or the co-evolved population's window mean income falls below the basal cost 0.25 on ≥ 5 of 6 seeds | neither body holds up |
| **F. unresolved** | anything else, including \|mean\| < r | the instrument could not see an effect of this size; report the size |

The sign counts: with n = 6, six of six same sign has two-sided probability 2/64 = 0.031 under
no effect, five of six 14/64 = 0.22 (arithmetic, binomial); with n = 10, nine of ten is 0.021 and
eight of ten 0.11. **The sign clause is therefore a guard, not the verdict**; the mean against r is
the verdict, and the report prints both. An arm that wants the sign count to carry weight needs
ten seeds, and says so.

Rules that bind the classes:

- **Class D is not a win, and it is tested by income, not by extinction.** A challenge that
  bankrupts the designed body measures its energy budget (C2 and C3 are expected to; §2), which is
  a fact about wheels at 14–29 kJ, not about the co-evolved body's robustness. A comparator that
  survives at four robots on 0.05 a season is bankrupt in every sense but the literal one, and the
  D test says so; class A is reachable only against a comparator that is neither extinct, nor
  below a fifth of capacity, nor below its basal cost. It is reported as D, with the co-evolved side's own R-shift beside
  it, and the sentence "holds up against the challenge" is earned only if the co-evolved side's
  income in the recovery window is within r of its control (R-shift ≥ −r). Otherwise it is
  "outlasts a bankrupt comparator", which is a different sentence.
- **R-shift and R-null are reported whichever class R-body lands in.** A class-A result whose
  R-null shows the cull did the same to income as the challenge is a class-A result about
  turnover, and the report says so.
- **A favourable readout that was not pre-registered is post hoc and unproven**, however
  consistent (project doc *Research goals*). Windows, T, k's rule, n and r's form are fixed here;
  the point prediction is fixed in the template before stage 2 launches.
- **A partial read of a running arm is not a result.** No R-body is computed before every seed's
  stage 2 has ended.

---

## 10. Expected depth

By RBT-59's law, depth ≈ 2 × seasons ÷ `max_age` (median 20 at 600 seasons, range 18–24):

| phase | seasons | expected reproduction events along a lineage |
|---|---|---|
| stage 1 to onset | T = 400 | ≈ 13 |
| stage 2, transient window | 60 | ≈ 2 |
| stage 2, transient + recovery | 160 | ≈ 5 |
| stage 2, whole | W = 200 | ≈ 7 |
| whole arm | 600 | ≈ 20 |

Measured afterwards with RBT-59's `depth.py` logic on stage 2's `lineage-last.txt` (RBT-71's
`measure.py` reports it as "depth … median (min–max), 2S/A, ratio"), per population, per arm.
**"Re-adapts" inside the recovery window means at most about five sequential mutations along any
lineage.** That is the honest scale of what a class-A result can mean: survivorship and sorting of
standing variation, not a search. C1's from-season-0 endpoint took 45 seasons to cross over
(RBT-17), about 1.5 events, which is a sorting timescale and is consistent with this.

---

## 11. What a challenge arm owes the repository

By role (RBT-86, `runs/README.md`), for stage 1 and each of the three stage-2 arms, per seed:
`config.json`; `seasons.txt` with the added `mean_age` and `max_age` columns; `lineage-last.txt`;
the cull list `cull-<seed>.txt`; the readout script and its printed readout including the power
line of §7 and the cohort-cycle table of §8; `REPORT.md` carrying the filled template of §12
verbatim as posted on the ticket, with a diff if anything was amended and when. Genomes,
`history.json`, `lineage.jsonl`, `cohorts.jsonl` stay out. The round trip is checked from a
checkout that never held the bulk and shown to fail on a perturbed cell (RBT-71's standard).

---

## 12. The pre-registration template

Copy this into the ticket before stage 2 launches. Every field is filled; "unmeasured" is a legal
value only in the fields that say so.

```
PRE-REGISTRATION: held-out challenge <C1|C2|C3|C4>, ticket <RBT-…>

1. Challenge and flag.  <one flag, its baseline value → its challenge value>, on the baseline
   command of docs/held-out-challenges.md §1 at integration head <hash>.  Measured endpoint on
   random founders: <the ticket and number>.  Kind: <competition | budget | perceivable>.
2. Perception.  What the robots can sense about this change: <sensor(s) or "nothing, by
   construction">.  What they do sense in practice: <cited lesion facts>.  Statement, in
   these words if the challenge is unperceived: "this challenge selects on standing morphology
   and gait only; robust means survivorship of standing morphology and gait through the shift,
   not adaptation during it; the axis and the falsifier are claims about income, not perception."  RBT-91 option in force: <A | B, with the positive-control ticket>.
3. Comparator.  The designed population of the same run, brain evolved for T = <…> seasons
   under --conventional-topology, no loaded or hand-set controller.  Ecology RNG streams:
   <build ticket, hash>; byte-identity check on the untouched population: <will be printed as …>.
4. Seeds.  <list, n ≥ 6>, each passing RBT-90's diversity rule; per seed the founder base rates
   for link-driven effector, linked oscillator and their composite, and pairwise shared body
   signatures: <numbers or "founders-<seed>.txt committed">.
5. Onset.  Route: <two-stage --from-run | --shift-at, hash>.  Cohort cycle measured on stage 1:
   per seed, the ten-season deaths peaks after season 100: <list or none>.  T per seed: <…>,
   ≥ 20 seasons after the last peak; predicted stagger seasons inside the windows: <list or none>.
   Energy reset at onset: <yes under two-stage; "before" is read from the control arm | no>.
6. Axis and windows.  mean_lifetime_score from seasons.txt.  Transient [0, 60), recovery
   [60, 160) primary, tail [160, 200).  R-body, R-shift, R-null as defined in §6.
7. Null.  Random cull of k per population at stage-2 season 0, k = excess deaths of the challenge
   arm over the control in [0, 10); cull RNG seed <…>; mechanism <--cull flag, hash | not
   available: R-null scored as not run>.  Instrument validation on a k = 20 cull: <result or
   "to be run before the challenge arms are read">.
8. Resolvable effect size.  From stage 1's last 100 seasons (control-arm form of §7's line), the
   readout prints: "<line>".  r = <the larger figure>.  Smallest effect worth claiming: 0.10.
   n = <…> seeds resolves <…>.
9. Verdict rule.  §9's classes A–F, with r from field 8, on the recovery window.  The sign
   clause is a guard; the mean against r is the verdict.
10. Point prediction, with confidence.  Class: <A|B|C|D|E|F>, confidence <p>.  R-body in the
    recovery window: <value>, per-seed range <…>.  Designed population: <survives | bankrupt by
    season …>, confidence <p>.  Co-evolved population: R-shift <value>.  R-null against R-shift:
    <which is larger and by how much>.  Recovery time: <seasons or "not within W">.  Stated
    reasons, so the prediction can embarrass its author: <…>.
11. Falsifier, in the owner's words.  "The designed body wins on the held-out challenge":
    class C by the rule.  Also falsified if: <the author's own secondary prediction that would
    hurt most>.
12. Expected depth.  Stage 1 ≈ 2T/60 = <…>; stage 2 ≈ 2W/60 = <…>; measured afterwards with
    depth.py per population per arm and quoted beside the prediction.
13. What is committed.  §11's list, by role.
14. Adversary.  <name>, whose brief is the reading in §14 the author is most exposed to.
15. Amendments.  None after stage 2 launches except those that touch data that does not yet
    exist, posted as such, with the reason.
```

---

## 13. Numbers the programme does not have, and the measurement that would produce each

| needed for | missing number | measurement (no run needed unless stated) |
|---|---|---|
| §7, r | between-seed SD of a **100-season windowed** income lead on more than three seeds | measured on RBT-71's 804/805/806 for this document's review (0.108; `runs/RBT-89/window_sd.py`); RBT-10's four tables are not on the integration head; the first challenge arm computes its own from stage 1 and quotes both |
| §8, onset placement | the cohort cycle on a **selected** ecology arm (RBT-80 measured it on drift arms only) | `rabbitstew history` on any committed baseline run's `history.json` (bulk, not committed) or on the challenge arm's own stage 1; ten-season deaths peaks after season 100; then the `mean_age` column in `seasons.txt` |
| §2 C1, prediction | population income at eight robots on a fresh seed (RBT-17 is one seed, 801) | the C1 arm itself; no prior needed beyond RBT-17's parity |
| §2 C2, C3, prediction | income of an **evolved** designed population at work cost 0.08 or six items (both endpoints are founders') | the arms themselves; the arithmetic in §2 is the prediction's prior |
| §2 C4, endpoint | any measurement of a foraging population on flat terrain | `scripts/forage_probe.py` with the run's config at `--terrain flat` on committed bests, 64 paired draws, before the arm: a probe, not a run of the arm |
| §5, onset | a mid-run onset that keeps energy and descent | the `--shift-at` build; until then the energy reset is stated |
| §8, null | a cull that leaves slots free | the `--cull` build; until then R-null is "not run" |
| §4, streams | per-population RNG streams in the ecology | the ecology half of RBT-85, with its pinning test |
| §10 | depth reached inside a 160-season window, measured | stage 2's `lineage-last.txt` through `depth.py`; RBT-59's law is the prediction |

---

## 14. Readings this protocol forbids, listed for the adversary

The adversary's brief is to find the reading a hopeful author could still take. The ones this
document has tried to close:

1. **Picking the challenge after seeing the population.** The set is fixed here; an arm names its
   challenge from §2 before stage 1 runs.
2. **Choosing a challenge that bankrupts the comparator and calling it a win.** Class D exists for
   C2 and C3, is tested by income and by a capacity floor and not only by extinction (the
   adversary's finding: an extinction-only D let a four-robot starving comparator read as class A),
   and "holds up" needs R-shift ≥ −r on the co-evolved side.
3. **Reading the champion where the population lost.** The axis is population income; the bests'
   two-to-one reversal at eight robots (RBT-17) is not R-body.
4. **Choosing the readout window after the curve is drawn.** Windows are fixed relative to onset;
   "disruption curves are the most readable curves there are" (*Research goals*, cautions).
5. **Reading the transient.** Onset is placed off the measured cohort cycle; the recovery window is
   primary; a class-A result at the transient is class F.
6. **Calling a draw what the instrument could not see.** Class B requires r ≤ 0.10; otherwise F.
7. **Pooling a perceived challenge (C4) with the unperceived three.** Reported separately.
8. **Pairing by seed without the streams.** The ecology stream build is a prerequisite; until it
   lands an arm says its arms are paired on founders only, per RBT-74.
9. **A graft that is not a graft.** The comparator's brain comes from the same run, same seasons,
   same operator; nothing loaded, nothing constant.
10. **"Re-adapts" for what is sorting.** Depth inside the recovery window is ≈ 5 events; the
    report uses "survives" or "is sorted" unless a lineage can be shown to have acquired something
    it did not carry at onset, by RBT-84's descent tracer, which the two-stage route cannot run
    across the onset (§5).
11. **A run made for this document.** None was. Every number above is cited or is labelled
    arithmetic on cited numbers.

---

### Sources cited

RBT-10, RBT-13, RBT-14, RBT-15, RBT-17, RBT-18, RBT-19, RBT-20, RBT-21, RBT-22, RBT-28, RBT-38,
RBT-39, RBT-59, RBT-62, RBT-66, RBT-67, RBT-71, RBT-74, RBT-78, RBT-80, RBT-84, RBT-85, RBT-86,
RBT-87, RBT-88, RBT-90, RBT-91, RBT-92, RBT-3; `docs/foraging-world.md`;
`docs/paper-3-let-the-furniture-stop-me.md`; `runs/RBT-71/readout-all.txt`,
`runs/RBT-71/measure.py`, `runs/RBT-74/readout.txt`, `runs/RBT-84/lab_g590.txt`,
`runs/RBT-84/champion_units_t.txt`, `docs/artifacts/RBT-80-three-seed-report.txt`;
`rabbitstew/ecology.py`, `rabbitstew/evolution.py`, `rabbitstew/genotype.py`, `rabbitstew/world.py`,
`rabbitstew/cli.py`; project docs *Research goals, aesthetics and endpoint* and *State of the
programme, 2026-09-19*.
