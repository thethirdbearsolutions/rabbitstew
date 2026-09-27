# Held, Not Spread

Payoff, operator erosion and the strength of selection on a planted compass.

*Tenth paper in the Rabbitstew series, written under Chaotic RBT-114. **Draft, revised after paper
adversary round 1** (PR #375, `docs/paper-10/adversary/PAPER-ADVERSARY.md`, F1–F28; the coordinator's
13:05 ruling on RBT-114, Chaotic: F1–F19 applied as proposed with the rulings on F3(a), F5, F8, F17 and
F20, and NOTEs F23, F24 and F26 applied). It continues strand 3 from paper 8
(`docs/paper-8-the-prize-the-proposal-rate-and-the-magnitude-gap.md`), which explained why six hundred
seasons produced no compass. This paper reports what happened when a paying compass was **planted**, and
what stops selection from keeping it and spreading it. Every result it reports is closed: each has been
through its own readout adversary and a coordinator ruling, and this paper's wording is bound by the
merged report after that ruling. **No sentence here is stronger than the merged `READOUT.md`,
`REPORT.md` or `ADVERSARY.md` it cites**, and where an adversary narrowed a claim, the narrowed form is
the one used: RBT-106 H's H8 (the patchy world also raised births, income and turnover) and RBT-112's A3
(the accepted wording of its verdict). No new simulation or ecology run was made for this paper. Every
number is cited to a committed file on the integration branch `claude/new-session-4cao7d`. The
headline numbers are recomputed or quoted from those files by `docs/paper-10/rederive.py`, whose printed
output is `docs/paper-10/rederive.txt`; the bracketed tags in the text ([W2], [E4], [Z3] and so on) are
that file's row ids. Where a figure goes beyond what a merged report registered, the text labels it
**post hoc** and says whose it is. Quotations from the coordinator's Chaotic comments, rather than from a
committed file, are cited as Chaotic. RBT-107 is outside this paper: nothing from it is read or cited.*

---

## Abstract

**Every result in this paper is for one population: the designed Pioneer wheeled body with an evolved
brain, the "conventional" fauna of RBT-90 part 2's ecology, seeded from planted founders.** It is not a
result about co-evolved bodies. Paper 5's positive result, evolved locomotion and a heritable foraging
yield, is on the co-evolved (holistic) side; nothing here extends it. **The compass instrument is defined
on the Pioneer's wheel layout.** RBT-103's report states that it raises on every holistic champion
checked, though no committed file records which or how many (RBT-102 adversary F6: the holistic fauna has
no wheel noses). Nothing here says whether an evolved body could carry a compass of another shape.

Paper 8 split "why no compass" into a prize, a proposal rate and a magnitude gap. This paper follows the
compass once the proposal and the magnitude are supplied by hand, by planting it in half the founders.

- **The prize depends on the world.** On the ten founding populations of RBT-90 part 2, a routed compass
  installed at a = 64 is worth **+0.844 [+0.618, +1.070]** items per bout in the uniform world, and
  **+2.103 [+1.542, +2.663]** in a one-field patchy world (12 items in 3 patches), 2.49 times as much
  [W1, W2, W4]. In P-801's patchy world it is +2.267 [W7]. That the size follows patchiness is
  RBT-103's exploratory finding.
- **A 2.5× prize alone did not make a compass from a sub-paying planted structure** (RBT-106 P1:
  **P-NULL**, 0 COMPASS lines of 7 usable). At the usable n = 7 the test misses "the prize alone
  suffices" with probability 0.22 if it held in half the populations, and 0.58 if in a quarter [P4].
- **Link reach was not tested.** RBT-104 is **VOID**: its install control could not see a compass in the
  hosts it built [V1].
- **Selection held a planted *paying* compass in the patchy world, and lost it in the uniform one**
  (RBT-106 H: **SUPPORTED**; HELD on 9 of 10 seeds against 0 of 10; COMPASS lines 10 against 0) [H1,
  H2]. In the ruling's required sentence (RBT-106 H8; ruling 08:20, Chaotic): "The operator erodes the
  compass at the same rate per generation in both worlds (u ≈ 0.29), and the patchy arms bred more
  generations. In the world where a working compass pays about 2.5× more, which also raised income and
  turnover, the paying compass was held on 9 of 10 seeds; in the uniform world on none." This is
  **holding, not de novo evolution** (the 08:20 ruling).
- **About two thirds of the operator's erosion is the global-bias walk** (the coordinator's "about two
  thirds", 08:28 on RBT-112, Chaotic; 68% of u(8) by this paper's post hoc division [E4]). With no
  selection, a planted paying compass is lost at u = **0.282** per generation; freezing the global biases
  cuts that to **0.089** [E1, E2], close to the structure's own decay of 0.067 [E3].
- **With the walk frozen, selection still did not raise the compass's population share in the uniform
  world** (RBT-112: **FALSIFIED**; HELD 1 of 10 against 0 of 10). In the accepted wording (A3), **the
  bias walk is not what stops selection holding the compass in the population**; selection's advantage on
  it is below ~0.1 per generation (the registered limit; the arms' own model-based likelihood puts it at
  **0–0.08** [Z10]). With the global biases frozen the host also changed (SE-Z failed), so a change in s
  itself is not handled. **This does not say the operator is irrelevant:** under the frozen operator the
  income-best lines carry the compass and use it (**5 COMPASS lines against 0**; carrying champions **31 of
  70 against 5 of 70**, a post hoc, print-only count from RBT-112's `sensitivity.txt` S1) [Z2, Z4], and
  under the default operator they do neither.

So, on this body **and in the uniform world**, **the operator decides how much compass is left for the
best lines to use; it does not decide whether selection raises the compass's share in the population.**
In the uniform world selection did not do that under either operator. In the patchy world only the
default operator was run, so this sentence says nothing about it. The limit the programme now names is
**selection's strength on the compass**, "not only the operator" (the coordinator's 12:20 ruling on
RBT-112, Chaotic).

---

## Summary table

All on the fixed-body (Pioneer) controller population, RBT-90 part 2's ten seeds (801, 804, 805, 806,
807, 1, 2, 3, 4, 7), 600 seasons, window seasons 300–599. The co-evolved fauna shares every ecology and
is neither planted nor read.

| ticket | question | registered verdict | n usable | the numbers | power for the null or "not held" at the usable n | wording, as ruled |
|---|---|---|---|---|---|---|
| **RBT-102** | does selection carry the routed structure above drift? (no planting) | NOT HELD, **not informative about selection** | 10 arms, 12,276 genomes | 0 carriers; a matched drift null reads 0 in 81 of 100 replays [D1] | the rule reads NOT HELD on 91 of 100 pure-drift replays; a zero is informative only at ~184,000 genomes [D2] | "RBT-102 contributes nothing to strand 3's question about selection" (`REPORT.md` §2.6) |
| **RBT-103** | does the compass pay on populations it did not come from? | a property of this world (8/10 at a = 64) | 10 | +0.844 [+0.618, +1.070] uniform; +2.267 [+1.461, +3.072] P-801 world [W6, W7] | — | "its size depends on the food's patchiness" (**exploratory**) |
| **RBT-104** | does link reach ×8 let selection keep a compass? | **VOID** | 2 of 10 S8 | install control fails on 8 of 10 S8 arms [V2] | none: "VOID carries no power figure because it is not a reading of H" | "VOID; the instrument could not see" (ruling, 01:52, Chaotic) |
| **RBT-106 P1** | does a 2.5× prize make a compass from a sub-paying planted structure (w = 1, a = 2)? | **P-NULL** | 7 of 10 | 0 COMPASS lines; paired F(P1) − F(S1) +0.049 [−0.242, +0.340] [P1] | misses "the prize alone suffices" 0.22 (q = 0.5), 0.58 (q = 0.25) [P4] | "A 2.5× prize alone, at default reach, did not evolve a compass from the sub-paying planted structure" (ruling, 06:06) |
| **RBT-106 H** | does selection hold a planted *paying* compass (w = 32, a = 64), uniform (HU) against patchy (HP)? | **SUPPORTED** | 10 of 10 | HELD HU 0, HP 9; COMPASS HU 0, HP 10; paired F +3.858 [+2.965, +4.750] [H1–H3] | HU's 0: FALSIFIED-a's count (#HELD(HU) ≥ 5) would have been met with probability 0.834 under "the uniform prize suffices" (q_U 0.60); the verdict also needs the log-excess condition, which can only lower it [H8] | H8: "The operator erodes the compass at the same rate per generation in both worlds (u ≈ 0.29), and the patchy arms bred more generations. In the world where a working compass pays about 2.5× more, which also raised income and turnover, the paying compass was held on 9 of 10 seeds; in the uniform world on none." |
| **RBT-112** | with the global-bias walk frozen (u 0.282 → 0.089), does selection hold it in the uniform world (HZ against HU)? | **FALSIFIED** (function FOLLOWS is reported beside the verdict, not in it) | 10 of 10 | HELD HU 0, HZ 1; COMPASS HU 0, HZ 5; carrying champions 5/70 against 31/70 (post hoc, `sensitivity.txt` S1) [Z1, Z2, Z4] | FALSIFIED fires with probability 0.000–0.054 at s = 0.2, 0.04–0.26 at s = 0.12, at the realised n; s ∈ [0.00, 0.08] [Z9, Z10] | A3: "The bias walk is not what stops selection holding the compass in the population. Selection's advantage on it is below ~0.1 per generation (the registered limit; the arms' own likelihood puts it at 0–0.08). With the global biases frozen the host also changed (SE-Z failed, income +0.160), so a change in s itself is not handled. This does not say the operator is irrelevant" |

**Sources.** `runs/RBT-102/REPORT.md`, `informative_n.txt`; `runs/RBT-103/REPORT.md`,
`adversary/world_matrix.txt`; `runs/RBT-104/REPORT.md`, `readout.txt`,
`readout-adversary/READOUT-ADVERSARY.md`; `runs/RBT-106/P1-READOUT.md`, `P1-readout.txt`,
`p1-adversary/`; `runs/RBT-106/H-READOUT.md`, `H-readout.txt`, `h-adversary/`;
`runs/RBT-112/READOUT.md`, `readout.txt`, `erasure.txt`, `power.txt`, `readout-adversary/`. Every cell
re-derives in `docs/paper-10/rederive.txt`.

**Precision.** Rows that recompute a paired interval from per-seed values printed to three places can
differ from the readout's own line in the third decimal: [H4] gives +1.771 [+1.420, +2.123] against the
readout's [+1.419, +2.122]. The text prints the readout's figure.

---

## 0. What this paper is, and what it is not

**What it is.** A synthesis of five closed tickets on one population. The measurements are the tickets'.
What the paper adds:
- **the frame**: *held* (a population share above what the operator alone leaves), *used* (the
  income-best lines steer by the compass) and *proposed* (the structure arises), kept apart throughout;
- **one post hoc division** (the share of the erosion that is the global-bias walk, [E4]) and **one post
  hoc application** of the RBT-112 readout adversary's balance-point formula to the default operator
  [M1], both labelled;
- **the power** of every absent verdict at its usable n, in one place (§7).

**It is not a finding that a compass evolves.** Every compass that paid in a *scored* arm was planted at
the paying magnitude. The one exception outside the rules is **P1-805**, a COMPASS line grown from the
sub-paying w = 1 founders, whose pair is unusable because S1-805's install control failed
(`P1-READOUT.md`, "Sensitivity"; not scored, and not food-dependent when uniform-scored, +0.529). The one
scored test of a sub-paying planted structure, P1, is P-NULL. H is "holding, not de novo evolution" (the
08:20 ruling on RBT-106, Chaotic).

**It is not a finding about evolved bodies.** The compass is the routed motif on the Pioneer body's two
wheel noses. The co-evolved fauna shares every ecology in these arms, is not planted and is not read.

**It is not a finding that the prize, alone, decided holding.** RBT-106 H changed one flag, the food's
patchiness. That flag raised the prize about 2.5×, and it also raised births, income and depth (H8).

**It is not a finding that the operator does not matter.** RBT-112's registered label, "the operator is
not the stall", is ruled to be read with its gloss (A3; §5).

**On the title.** "Held" is RBT-106 H's positive result in the patchy world. "Not spread" is RBT-112's
result in the uniform world: with the erosion cut by two thirds, the best lines kept and used the
compass on five seeds of ten, and selection did not raise its population share above the operator-alone
level. In the patchy
world the population share *was* above that level on 9 of 10 seeds; the title does not deny it.

---

## 1. The design, in one page

**The ecology.** RBT-90 part 2's dense foraging world (`docs/foraging-world.md`): arenas of four robots
share 12 food items in a 3 m disc; income is food eaten less 0.03 per kJ of work and a basal 0.25 a
season; a robot breeds at energy 3 and dies at 0 or at age 60. Two faunas of sixty live in separate arena
banks:
- the **co-evolved** (holistic) fauna, bodies and brains from random morphologies;
- the **designed** fauna, the Pioneer wheeled body with an evolvable brain under
  `--conventional-topology`.

**The population read here** is the designed fauna, seeded from planted founders by
`--from-conventional` (`config.json`: `seed_conventional`, e.g. `runs/RBT-106/HP-4/config.json`,
`runs/RBT-112/HZ-4/config.json`). Every verdict, income, birth count and function reading in §3–§6 is
that fauna's.

**The compass.** RBT-97's routed motif: a global `tanh` unit, bias 0, fed by the two wheel noses at ±1
and feeding both drive Effectors at weight w. Its gain is a = 2w. It was installed in the even half of
part 2's own sixty designed-body founders, fifteen at each sign (`runs/RBT-106/PREREGISTRATION.md` §3.2):
- **w = 1 (a = 2)**, RBT-104's founders: a sub-paying structure, never taken to a paying rung by the
  operator alone and not food-dependent at t = 0 in either world (same, "Three corrections to the
  ticket's premises", item 3; §3.3);
- **w = 32 (a = 64)**, option H's founders: RBT-103's own paying install.

**The worlds.**
- **Uniform:** RBT-90 part 2's, 12 items, no patches, instant regrowth.
- **One-field patchy:** the same config with `--food-patches 3`, so exactly one field differs,
  `sim.food.patches` 0 → 3 (`runs/RBT-106/one_field.txt`, check 2). It is *not* P-801's world, which has
  26 items and no regrowth within a bout (RBT-103, "The worlds, correctly described").

**The instruments**, each with a positive control in each arm:
- **HELD** (RBT-106 §10.2): the planted-rooted living carry a paying compass (own links ≥ 12.52 with the
  root's sign, `pay32`) above the operator-alone bound B at matched depth, at **both** seasons 300 and
  599, counted on planted-rooted genomes only (k_planted). B is the 95th percentile of the no-selection
  table at the arm's own n and depth. RBT-112 reads it against its own operator's table.
- **COMPASS line** (function): the arm's seven window champions (300, 350, …, 590) are food-dependent
  (`function.py`'s primary call) **and** the compass attribution is food-dependent (removing the compass's
  input links removes the gain, and the rotated decoy does not keep it). Scored in the patchy world
  ("patchy-scored") unless stated.
- **Usability:** an arm is usable if it is viable, on x86_64, on the certified code, analyse.py's
  control passed, and its install control (an a = 64 motif installed on its own bests, at the host's own
  scale) reads food-dependent.
  Unusable arms leave the rules; they are not nulls.

**Depth.** Reproduction is slot-limited, so 600 seasons is about twenty generations, not six hundred
(README, RBT-59). The window depth was 14.1–17.6 in RBT-106 H [H6], and the planted-rooted living at 599
in RBT-112 sat at mean depth 17.3–23.5 (`runs/RBT-112/readout.txt`). All erosion rates below are **per
generation**.

---

## 2. The prize, by world

**On the ten new founding populations the compass pays in the uniform world.** Installed at a = 64 on each
population's own bodies, it is worth **+0.844 [+0.618, +1.070]** items per bout, and pays by the
pre-registered rule on 8 of 10 (`runs/RBT-103/REPORT.md`, "The result"; [W6, W8]). The report, revised
per its adversary's F3 and the 17:45 ruling, quotes the t(9) interval rather than the count: two of the
eight clear zero by less than 0.1 items, and "A significance count measures power in the world it is
taken in".

**It pays more where food is patchy** (exploratory).
- In P-801's world (26 items in 3 patches, no regrowth within a bout) the same ten populations' bodies
  gain **+2.267 [+1.461, +3.072]** [W7]; all ten gain more there, at 1.85× to 3.38× their home gain.
- One food factor at a time, on P-801's bodies: 12 items in 3 patches gives +2.489, and 26 uniform items
  only +1.308. **"Density" and "regrowing" are withdrawn; the size follows patchiness**
  (`runs/RBT-103/REPORT.md`, "Its size depends on the food's patchiness (exploratory)").
- That world control was decided after eight rows had been read, and no attribution rule was posted
  before it ran. The report labels it **EXPLORATORY** (same, adversary F5).
- The report carries two residuals rather than resolving them: seeds 807 and 2 barely rise in P-801's
  world, and a home advantage is not excluded (same, "(a) Heterogeneity", "(b)").

**In the one-field patchy world of RBT-106** (12 items in 3 patches, instant regrowth), measured before
any arm on the same ten populations' bodies:
- the prize at a = 64 is **+2.103 [+1.542, +2.663]** against the uniform world's +0.844, a paired
  difference of **+1.259 [+0.900, +1.617]**, 10/10 [W3q] ([W3] recomputes the lower bound as +0.901
  from per-seed values);
- the ratio of means is **2.49×**, and 1.93× to 3.13× by seed [W4];
- the patchy decoy verdicts are FOOD-DEPENDENT on 9 of 10 and unresolved on 1 (`runs/RBT-106/prize.txt`);
- the world is **richer**, not harder: base income +1.537 against +1.308 [W5q], and the
  throwaway runs bred about 1.6× faster (`PREREGISTRATION.md`, "Three corrections to the ticket's
  premises", item 2; §4).

So "the patchy world" in §4 means a world where the compass pays about 2.5× more **and** the base
economy is richer and faster-breeding. Those cannot be separated by the flag that makes it.

---

## 3. What did not make or keep a compass

### 3.1 No planting: RBT-102's zero carries no information about selection

In ten founding populations under selection, **0 of 12,276 genomes** carry the routed compass structure at
any magnitude, and the instrument can see it: 40 of 40 installed motifs detected in every arm, and 24
carriers planted end to end detected (`runs/RBT-102/REPORT.md`, headline and §2.1).

The readout adversary built a drift null on each arm's own founders and pedigree. It reads zero in **81 of
100** replays, and the pre-registered rule reads NOT HELD on **91 of 100** pure-drift replays. A zero
would become informative at about **184,000 genomes, 150 arms** of this size [D1, D2]. The ruling: RBT-102
"contributes nothing to strand 3's question about selection" (same, §2.6). The structure is rarely
*proposed* from these founders at these depths; that is paper 8's proposal rate, not a statement about
selection.

### 3.2 Link reach: RBT-104 is VOID, and the instrument could not see

RBT-104 raised the designed fauna's link scale ×8 (S8) against ×1 (S1), with w = 1 planted founders, to
ask whether reach lets selection keep a compass.

**Scored: VOID** [V1]. The per-arm install control failed on 8 of 10 S8 arms, leaving 2 usable against
the 7 required [V2].

**Why: the report's post hoc account** (`runs/RBT-104/REPORT.md`, "Why VOID", which heads it as POST HOC
probes; adopted as the reading of the VOID by the 01:52 ruling, Chaotic). Bullets 1–3 are all post hoc:
- the control installs the a = 64 motif at the **default** scale (inputs ±1, output 32), and nothing
  applies the arm's ×8 to it;
- in a ×8 host the drive Effectors are saturated on 91–96% of ticks, so only 2–8% of the installed
  compass's effect reaches them (the readout adversary's `sat_probe.txt`, §1.2);
- three S1 hosts that pass fail 3 of 3 once scaled ×8,
  and the same control built at the arm's own scale (±8, 256) passes on 5 of 5 failing S8 hosts and 3 of 3
  synthetic ones (the readout adversary's probes, §1.3).

In the adversary's words, "*A compass built at the default scale is invisible in a host built at ×8.*"
**RBT-104 answers nothing, either way, about whether reach lets selection keep a compass.** The ruling
had this paper cite RBT-104 as "VOID; the instrument could not see", with those probes post hoc (01:52; relaxed by the
13:05 ruling on RBT-114 to allow the report's account above, so labelled). VOID carries no power figure.
The report also prints a counterfactual figure, **the report's, not a reading**: had the arms been
usable, the registered P(SUPPORTED | H) was ≤ 0.11–0.14 at n = 10 and ≤ 0.023–0.028 at n = 7
(`REPORT.md`, "Matched-null power").

One sentence is post hoc and of record (the readout adversary's F4, adopted at 01:52 and recorded at the
02:00 closure), and is used in §9: *a uniform link scale cannot supply the compass's magnitude relative
to its host, because it scales both*.

### 3.3 A 2.5× prize on a sub-paying structure: RBT-106 P1 is P-NULL

P1 evolved the w = 1 planted founders (a = 2, sub-paying) for 600 seasons in the one-field patchy world,
paired by seed with RBT-104's S1 arms in the uniform world, which are the same founders under the same
operator.

**Scored: P-NULL.** Of 7 usable pairs, **0** P1 lines are COMPASS lines, and so are 0 S1 lines. The
paired F(P1) − F(S1), patchy-scored, is **+0.049 [−0.242, +0.340]** (t(6)) [P1, P3]
(`runs/RBT-106/P1-READOUT.md`, "Verdict").
- **Usability:** P1-801, P1-7 and S1-805 fail their install controls on interval, not by construction
  (median transmission 0.39–0.60 across P1 arms and 0.35–0.61 across S1 arms, 0.390–0.443 on the three
  failing ones, against 0.04–0.08 for RBT-104's ×8 hosts). P1-801's failure is
  heterogeneity across its bodies, not saturation (the P1 adversary's A2).
- **No usability choice moves the verdict.** Over all ten pairs the paired F is +0.254 [−0.205, +0.714]
  [P2], with one COMPASS line among all 20 arms: **P1-805**, grown from the sub-paying founders, F
  +1.942 with compass attribution FOOD-DEPENDENT, whose pair is unusable (`P1-READOUT.md`,
  "Sensitivity"; a single case, not a pattern). Adding back any one
  unusable pair leaves P-NULL (ruling, 06:06, Chaotic).
- **Structure.** HELD on S1 1 (seed 804), on P1 0; the paired log-excess, P1 − S1, is −1.559 [−2.983,
  −0.136] (`P1-readout.txt`). P1 kept *less* of the planted structure, relative to the no-selection
  expectation at its depth, than S1 did.
- **Side effects:** P1 − S1 window income +0.384 [+0.297, +0.471]; more births on 10/10; a deeper window
  on 8/10 (`P1-READOUT.md`, predictions SE-2, SE-3).

**The ruled sentence** (06:06, Chaotic): "A 2.5× prize alone, at default reach, did not evolve a compass
from the sub-paying planted structure. This test would have missed a real 'prize suffices' effect about 1
time in 5 at q = 0.5, and more often than not at q = 0.25." At the usable n = 7, on the measured patchy
bare-line model, P-NULL misses "the prize alone suffices" with probability **0.215** at q = 0.5 and
**0.579** at q = 0.25; it is fair evidence against that hypothesis only at q ≥ 0.6, where the miss rate is
≤ 0.116 [P4] (`p1-adversary/power_n7.txt`). Under "both reach and prize are needed", P-NULL fires with
probability 0.83–0.93, so **it says nothing about the prize once reach is there** (`P1-READOUT.md`).

---

## 4. What held a paying compass: RBT-106 H

H planted the **paying** compass (w = 32, a = 64) in half of the same founders, at the default link
reach, and evolved each population twice for 600 seasons: once in the uniform world (**HU**) and once in
the one-field patchy world (**HP**).

**Scored: SUPPORTED** (`runs/RBT-106/H-READOUT.md`, "Verdict"):
- **HELD: HU 0, HP 9** (HP-807 is the one patchy arm not held) [H1]; the paired log-excess at 599, HP −
  HU, is **+2.240 [+1.556, +2.925]**. The rule was #HELD(HP) − #HELD(HU) ≥ 3 with that interval above
  zero.
- **Usable: 10 of 10.** All 20 install controls read food-dependent.

**Function follows** (reported, not in the verdict):
- **COMPASS lines: HU 0, HP 10** [H2];
- paired F(HP) − F(HU), patchy-scored, **+3.858 [+2.965, +4.750]**; uniform-scored +0.925 [+0.610,
  +1.241] [H3, H7];
- compass-lesion gain, patchy-scored: HU +0.520 [−0.041, +1.080], HP +4.804 [+4.059, +5.549].

**What the readout adversary established** (`runs/RBT-106/h-adversary/ADVERSARY.md`; ruling 08:20, Chaotic):
- **HELD is not demography (H1).** Run on each arm's **own** genealogy, the no-selection null gives HELD in
  0.7% of HP replicates under the full operator and 1.3% under mutation alone [H9]. At q = 0.013,
  P(#HELD(HP) ≥ 9 of 10) is about 10⁻¹⁶, and the size of the SUPPORTED count is 2.2 × 10⁻⁴ [H11].
- **HU's "not held" is "not just" lineage loss.** Five HU arms lost their planted-rooted lineages by 599
  (n = 0): 801, 804, 805, 807 and 7. Three of them, 804 (k_planted 3 > B 1), 805 (2 > 1) and 7 (3 > 2),
  read above the operator-alone bound at 300 before the lineage vanished (`H-readout.txt`, HU rows). In
  the other five the planted lineages survived (n = 19–60), and **every one** reads k_planted = 0 at 599
  [H10]. In the uniform world the compass was eroded out of surviving planted lineages too; losing a
  lineage is demography, not the operator's per-generation erosion.
- **The function is the planted unit steering by smell (H2).** On two F12-flagged and two unflagged HP
  arms, cutting only the planted unit's input removes 0.99–1.01 of the compass gain; its drifted bias's
  resting drive earns nothing by itself; and resetting that bias to 0 *lowers* income, so the drift is
  co-adapted.
- **Every number re-derives (H7)**, and 40 of 40 held files and 242 of 242 evidence files regenerate
  byte-identically from the checkpoints (H10).
- **F12's masking heuristic (H5).** It flagged HP-804, HP-805 and HP-806 (planted units with drifted biases
  driving 3–7 at rest), yet all three controls pass with the design's largest F and their installs are
  detected. Without the three, the registered rule still reads SUPPORTED (+2.304 [+1.257, +3.352];
  `H-sensitivity.txt`). H5's caveat: the heuristic's premise, that a resting drive above 1 masks the
  control, "failed on evolved hosts … Don't reuse it as a masking criterion without the increment test".

**The wording (H8, MUST-FIX, applied).** The first readout said the erosion was the same and only the
prize differed, so "the size of the prize decided" holding. That is false by the readout's own side
effects. The ruled sentence:

> "The operator erodes the compass at the same rate per generation in both worlds (u ≈ 0.29), and the
> patchy arms bred more generations. In the world where a working compass pays about 2.5× more, which also
> raised income and turnover, the paying compass was held on 9 of 10 seeds; in the uniform world on none."

The side effects it refers to [H4–H6]:
- window income HP − HU **+1.771 [+1.419, +2.122]**;
- births **1,668–1,861** in HP against **1,132–1,341** in HU, HP more on 10/10;
- window depth HP 14.3–17.6 against HU 14.1–16.6.

Because erosion is equal per generation and HP bred more generations, per season the compass was eroded,
if anything, *more* in HP (H8). The design isolates **patchiness**. The ~2.5× prize is its measured,
hypothesised mechanism, "not the only difference" (ruling, 08:20; H8's own phrase is "not the only thing
that differed"). The registered verdict label,
"the larger prize held the paying compass where the uniform prize did not", is the pre-registration's and
stays.

**Caveats, recorded in the report (H3 and H4, as the 08:20 ruling required):**
- **H3: HELD and function score different genomes in the drifted arms.** HELD reads the planted unit's own
  links alone, so a unit whose bias has walked reads as lost even when it still steers. HP-806's seven
  champions include no `pay32` hit, yet all steer through the planted unit. HELD **under-counts** what
  selection kept working.
- **H4: HP-807's install increment is not detected** (+0.935 [−0.124, +1.995]); in the h-adversary's words,
  "Its pass may be carried by its host's own compass". Without HP-807 the result is still SUPPORTED,
  log-excess +2.496 [+2.081, +2.912].

**Power at the usable n = 10** [H8]. SUPPORTED's count fires under no effect with probability ≤ 0.020 at
null rates up to 0.08 (measured 0.01); the worst case over q, with q_U = q_P, is 0.132 at q = 0.5 (H7).
On the arms' own genealogies the null rate is about 0.013, where the size is 2.2 × 10⁻⁴ [H11]. HU's zero
is the absent-type reading: **FALSIFIED-a's count** (#HELD(HU) ≥ 5) would have been met with probability
**0.834** under "the uniform prize suffices" (q_U = 0.60, q_P = 0.70), and was not; the verdict also needs
the log-excess condition, which can only lower that. So the uniform world's failure to hold is not a
low-power miss of a common effect; it could miss a rare one (at q_U ≈ 0.15 the count's probability is
0.010).

**What it establishes, in the ruling's words** (08:20, Chaotic): "In this simulator, **natural selection
can hold a planted, working perceptual structure (a food compass) against the mutation operator's
erosion**, in a world where it pays about 2.5× more. … This is **holding, not de novo evolution.**" On
this paper's population rule: on the Pioneer body's controller, planted at the paying magnitude.

---

## 5. The operator: what the erosion is, and what freezing it changed

### 5.1 About two thirds of the erosion is the global-bias walk

RBT-104's readout adversary traced the operator's erasure of a planted paying compass to "the bias gate"
(`READOUT-ADVERSARY.md` §5.1(i)). The mechanism is in its §5.2, quoting RBT-106 §5.1: a planted w = 32
unit's resting drive v·tanh(b) saturates its Effector once the unit's bias b walks. The global bias steps at `weight_sigma` whatever the link scale
(`rabbitstew/genetics.py`, as RBT-112's description notes, Chaotic). The adversary quoted
u ≈ 0.29 per generation for RBT-106's w = 32 at K = 1, and costed a flag, `--global-bias-sigma S`, that
freezes only the global units' biases at S = 0 without changing the random stream. RBT-112 built it and
re-ran RBT-106's operator-alone baseline with it, before any arm (`runs/RBT-112/DECISION.md`, rule fixed
first; `erasure.txt`):

| | default operator | global biases frozen (S = 0) |
|---|---|---|
| pay32 persistence at depth 8, pooled over 6,000 lineages | 0.0710 | 0.4737 |
| **u(8) = 1 − f(8)^(1/8), per generation** (the primary) | **0.282** [E1] | **0.089** [E2] |
| the structure's own decay, u(8) on `same` | 0.097 | 0.067 [E3] |
| pay32 persistence at depth 16 | 0.0127 | 0.2452 [E6] |

- The default run reproduces RBT-106's committed tables at every depth on all ten seeds [E0].
- Per seed, S = 0 − default is **−0.193 [−0.201, −0.185]** per generation, 0 of 10 seeds positive [E5].
- **Post hoc (this paper):** freezing the global biases removes (0.282 − 0.089) / 0.282 = **68%** of the
  primary u(8) [E4], the coordinator's "about two thirds" (08:28 on RBT-112, Chaotic). The remainder is
  near the structure's own decay under S = 0 (0.089 against 0.067).
- The ticket's u ≈ 0.29 is u(1) = 0.292; the registered estimator reads 0.282. Where this paper says
  "u ≈ 0.28" it means the latter.
- The registered decision was u ≤ 0.12 → the arm is worth running. It read **WORTH RUNNING**.

### 5.2 With the walk frozen, the best lines keep the compass and use it on half the seeds

RBT-112 ran **HZ** = HU + `--global-bias-sigma 0` on the same ten seeds, in the **uniform** world, with
RBT-106's HU as the paired control. The rules were SUPPORTED iff #HELD(HZ) − #HELD(HU) ≥ 3, and FALSIFIED
iff #HELD(HZ) ≤ 1 with at most two seeds LOST (planted roots gone).

**Scored: FALSIFIED**, with **function FOLLOWS** reported beside it (`runs/RBT-112/READOUT.md` §1; [Z8]):
- **HELD: HU 0, HZ 1** (seed 805); LOST 1 (seed 4); usable 10 of 10 [Z1]. Planted roots were alive on 9
  of 10 seeds.
- **COMPASS lines: HU 0, HZ 5** (801, 4, 804, 805, 1) [Z2].
- **Paired F(HZ) − F(HU): +1.654 [+0.785, +2.523]** patchy-scored, and **+0.468 [+0.290, +0.646]**
  scored in the uniform world the arms lived in [Z3].
- **Champions carrying a paying planted unit: HZ 31 of 70, HU 5 of 70**; paired per seed +2.6 [+1.4,
  +3.8] of 7 [Z4] (`sensitivity.txt` S1, post hoc and print-only, re-derived by the readout adversary).

**The verdict, in the accepted wording** (A3; ruling 12:20, Chaotic; `READOUT.md` §1):

> **FALSIFIED** (registered). With the designed body's global biases frozen (host and planted), selection
> did not hold the planted paying compass above what that operator alone leaves: 1 of 10 seeds held
> (805), against 0 of 10 under the default operator, with planted roots alive on 9 of 10. **The bias walk
> is not what stops selection holding the compass in the population.** Selection's advantage on it is
> below ~0.1 per generation (the registered limit; the arms' own likelihood puts it at 0–0.08). With the
> global biases frozen the host also changed (SE-Z failed, income +0.160), so a change in s itself is not
> handled. **This does not say the operator is irrelevant:** under S = 0 the compass persists at the
> operator-alone level, and the income-best lines carry it and use it (5 COMPASS lines against 0;
> champions carrying 31 of 70 against 5 of 70). Under the default operator they do neither. What the
> operator decides is how much compass is left for the best lines to use. What it does not decide is
> whether selection raises its frequency: it does not, under either operator.

**What the readout adversary established** (`runs/RBT-112/readout-adversary/ADVERSARY.md`):
- **A1: the instrument could fire.** At readings with n ≥ 10, HELD needed k_planted above B/n of
  0.48–0.60 at 300 and 0.22–0.38 at 599: a real bar, not a ceiling (seed 2 at 599, n = 3, needed every
  genome). On each HZ arm's own genealogy, on the six seeds with n ≥ 40 at both readings, the S = 0 null's
  95th percentile is at or above B at every reading but one (seed 1 at 300), so the registered bar was, if
  anything, lenient. Only 805 clears its own null (0 of 200 replicates reach its count). The 300 reading was binding
  on 7 of the 8 seeds that were neither HELD nor LOST.
- **A4: FUNCTION FOLLOWS is robust.** It keeps ≥ 3 COMPASS lines after losing the two most marginal; the
  paired F's lower bound stays ≥ +0.372 with any two seeds removed; 9 of 10 seeds are positive [Z3].
- **A5: seed 4's LOST and seed 805's HELD are genuine.** Seed 4's bare-rooted carriers all have a planted
  ancestor through crossover, which the registered root rule excludes by design, and its champions run on
  those crossover-carried compasses (A4). 805's HELD is one clade (c0-12, 53 of 60 at 599).
- **A8: the design's power model tied champion carriage to population HELD, and the arms break that
  tie**: 5 COMPASS lines with 1 HELD. "The champions are enriched for the compass, because it pays in
  income, without selection raising its frequency."

**SE-Z failed, upward.** HZ's window income is **+0.160 [+0.050, +0.271]** above HU's [Z5]; births (+6.3
[−44.6, +57.2]) and depth do not differ [Z6]. So the treatment is "global biases frozen (host and
planted)", not "the planted unit's bias walk" alone, and the s the arms measure is HZ's host's s.

---

## 6. Held, used and spread: one population, three readings

Put the three planted-compass contrasts side by side. Each row is a separate registered test on the
fixed-body (Pioneer) population, with HU as the shared control. **No registered contrast compares HP with
HZ**; they differ in world and operator, and the table does not pair them.

| arm (world, operator) | HELD (population share above the operator-alone bound) | COMPASS lines (the best lines use it) | champions carrying a paying planted unit | window income against HU |
|---|---|---|---|---|
| **HU** (uniform, default) | 0 of 10 | 0 of 10 | 5 of 70 | — |
| **HP** (patchy, default) | **9 of 10** | **10 of 10** | not printed in this form | +1.771 [+1.419, +2.122] |
| **HZ** (uniform, biases frozen) | 1 of 10 | **5 of 10** | **31 of 70** | +0.160 [+0.050, +0.271] |

Sources: [H1–H4], [Z1–Z5]. RBT-106's F12 print (`f12-H.txt`) counts HP's planted-type units by resting
drive, not as paying carriers, so the HP cell is left empty rather than recomputed.

**What the rows show, in the rulings' words:**
- **Uniform world, default operator (HU):** the compass is neither held nor used. It was eroded out of
  surviving planted lineages as well as lost with them (§4).
- **Patchy world, default operator (HP):** held and used, against the same per-generation erosion and more
  generations of it. The world also raised income and turnover (H8).
- **Uniform world, frozen biases (HZ):** used by the best on 5 of 10 seeds, not held. "What the operator decides is how
  much compass is left for the best lines to use. What it does not decide is whether selection raises its
  frequency" (A3).

**How weak is selection on it in the uniform world?** The arms' own likelihood (the readout adversary's
BetaBinomial profile under the design's mutation–selection recursion, u fixed at 0.089) gives, with ρ
profiled, an MLE of s = 0.01 and a 95% profile interval of **s ∈ [0.00, 0.08]** (`instrument.txt` (3),
"rho profile" line; [Z10]). `READOUT.md` §2's "The MLE is s = 0.00" is the ρ = 0.10 line of the same
section, whose interval is [0.00, 0.03]. The adversary also prints the
recursion's balance point: "with u = 0.089, x can stay above 0 only if (1 + s)(1 − u) > 1, i.e.
s > u / (1 − u) = 0.098; below it the share decays towards 0 whatever s is" [Z11]. The interval lies below
that point [M2]. Both are **model-based**; the likelihood treats the two readings as independent; and
both measure HZ's host's s (SE-Z).

**Post hoc (this paper), on the same formula, not measured.** Under the default operator (u(8) = 0.282)
the balance point is s > 0.39; at the ticket's u(1) = 0.292 it is s > 0.41 [M1]. This does **not** say
what s was in HP. HELD is read against the operator-alone bound at two finite depths, not at a balance,
and under the same recursion it fires below the balance point (at S = 0, s = 0.089, just under 0.098,
gives E#HELD ≈ 2 of 10 at ρ 0.10; `instrument.txt` (2)). So HP's 9 of 10 does not by itself imply s of that order.
**No s was estimated for HP**, and the patchy world changed more than the prize.

**A9's clade route.** Selection can also act through the denominator: planted-rooted living at 599 were
**386 of 600 in HZ against 199 in HU**, paired +18.7 [−9.4, +46.8] per seed [Z7]. If planted clades
out-reproduce bare ones early and are then eroded inside at the operator's rate, k_planted / n misses it.
The interval includes 0; A9 is a caution against reading FALSIFIED as "selection never acts on the
compass", and not evidence for SUPPORTED (`readout-adversary/ADVERSARY.md` A9).

---

## 7. Power at the usable n, for every null and "not held"

| verdict | usable n | what it could have missed | source |
|---|---|---|---|
| RBT-102 NOT HELD | 10 arms, 12,276 genomes | anything: pure drift reads NOT HELD on 91 of 100 replays; P(0 carriers \| matched drift) = 0.81 [0.72, 0.87]; informative at ~184,000 genomes (100–230 arms across the null's interval) | [D1, D2]; `REPORT.md` headline |
| RBT-104 VOID | 2 of 10 S8 | not a reading of H, so no power figure. The report's counterfactual figure, not a reading: had the arms been usable, P(SUPPORTED \| H) ≤ 0.11–0.14 at n = 10, ≤ 0.023–0.028 at n = 7 | `REPORT.md`, "Matched-null power" |
| RBT-106 P1 P-NULL | 7 pairs | "the prize alone suffices": missed with 0.215 at q = 0.5, 0.579 at q = 0.25, 0.116 at q = 0.6; fires 0.83–0.93 under "both needed", so silent on reach | [P4]; `p1-adversary/power_n7.txt` |
| RBT-106 H, HU's 0 held (FALSIFIED-a not fired) | 10 pairs | FALSIFIED-a's count (#HELD(HU) ≥ 5) would have been met with 0.834 under "the uniform prize suffices" (q_U 0.60), and 0.010 at q_U 0.15; the verdict also needs the log-excess condition, which can only lower these | [H8]; `H-readout.txt` |
| RBT-106 H, HP-807 not held | 1 arm | one seed; its line is food-dependent through the compass (F +4.538), and 6 bare-rooted genomes carry it by crossover. Its install increment is not detected, so its control's pass "may be carried by its host's own compass" (h-adversary H4) | `H-READOUT.md`, "Beside the verdict" |
| RBT-112 FALSIFIED | 10 pairs | P(#HELD(HZ) ≤ 1) at the realised n and depth (ρ 0 / 0.10 / 0.30): **0.000 / 0.008 / 0.054 at s = 0.2**; 0.038 / 0.160 / 0.263 at s = 0.12; 0.320 / 0.380 / 0.431 at s = 0.089. Design anchors at s = 0.2: 0.005 at n = 40, the anchor `READOUT.md` names as relevant; 0.108 in the genealogy scenario, where the count would read FALSIFIED-ROOTS; the design adversary's pessimistic M15, 0.214. Likelihood (ρ profiled): s ∈ [0.00, 0.08] | [Z9, Z10, Z12]; `READOUT.md` §2; M15 from `runs/RBT-112/adversary/ADVERSARY.md` |

**How to read the RBT-112 row.** FALSIFIED is **strong evidence against a population-level selective
advantage of s ≥ 0.2**, and weaker below s ≈ 0.12 (`READOUT.md` §2, "What this says"). "In words, if
selection held the compass in the population it did so weakly, below ~0.1–0.15 per generation, even with
the erasure cut to 0.089" (same).

**One run per founding population.** Every per-seed class above (805 HELD, HP-807 not, seed 4 LOST) is one
breeding history. RBT-105 showed, on the **co-evolved** fauna's oscillator fate, that from byte-identical
founders a different breeding history reversed the fate in 5 of 14 decided replicates (95% interval
0.13–0.65) [A1] (`runs/RBT-105/REPORT.md`, the adopted paragraph). It did not vary the designed fauna's
history, which it held identical, so it measures nothing about this population's per-seed variance; and
its A/A spread is a comparator for paired co-evolved − designed income contrasts only [A2], so it is not
used here as a scale for the designed-fauna incomes of §4–§6. It bears on the nulls in one way: **a
per-seed count is a count over histories, not over founder properties**, which is how every rule above
was registered.

---

## 8. Limits

- **Holding is not invention.** Every compass that paid in a scored arm was planted at a = 64. The one
  exception, P1-805, grew a COMPASS line from the sub-paying w = 1 founders outside the rules (its pair is
  unusable) and is a single case, not a pattern. The only scored sub-paying test, P1, is P-NULL at n = 7,
  and RBT-102's zero is uninformative. H is "holding, not de novo evolution" (the 08:20 ruling on
  RBT-106, Chaotic; §3).
- **The patchy world changed more than the prize.** `--food-patches 3` raised the compass's prize about
  2.5×, and also raised window income (+1.771), births (10/10) and depth (H8). HP bred more generations,
  so it was eroded more per season, not less. Which of these held the compass is not separated.
- **SE-Z failed.** Freezing the global biases also changed the host: HZ's window income rose +0.160
  [+0.050, +0.271]. So RBT-112's s is HZ's host's s, and "a change in s itself is not handled" (§10.4 F3 of
  its pre-registration; A3).
- **A9's clade route.** Selection acting through the expansion of planted clades, rather than through the
  carrier share within them, would not appear in k_planted / n. The paired n difference, +18.7 [−9.4,
  +46.8], does not resolve (§6).
- **"Shown passable."** RBT-112's pre-launch HELD control showed only that HELD can fire when every
  planted-rooted genome pays (k = n), not that it can fire at a plausible s. Its passability was carried
  by the power model and confirmed at the realised n (A1, A6). The programme rule adopted at 12:20
  (Chaotic): "**'per-arm controls shown passable' means a modelled or simulated positive at a stated s,
  not arithmetic reachability at k = n**." It is added after RBT-104's rule to run every per-arm control on
  the arm's own founders before launch, "and show it can pass" (02:00, Chaotic).
- **HELD and function score different genomes.** HELD reads the planted unit's own links on planted-rooted
  genomes; function reads the champions whole. HP-806's champions steer through a drifted planted unit and
  are not `pay32` hits (H3); seed 4's HZ champions run on compasses carried by crossover into bare-rooted
  genomes (A4, A5). HELD under-counts in the first case and excludes the second by design.
- **One body, one patchy world, one depth.** The Pioneer's two wheel noses; the one-field world (12 items in
  3 patches, instant regrowth); 600 seasons, about 14–23 generations deep in the window. RBT-103's size
  finding is exploratory.
- **Model-based s.** The likelihood interval and the balance point use the design's mutation–selection
  recursion with u fixed; §6's default-operator arithmetic is this paper's, post hoc, and not a
  measurement.

---

## 9. Next steps

No new claim is made here; each item is a question the closed tickets leave, and the ticket or ruling that
names it.

1. **Selection strength, not only the operator.** RBT-112's ruling: "The limit is selection's strength
   on the compass (s < ~0.1), not only the operator" (12:20, Chaotic). In the uniform world, under the
   frozen operator, the best lines on 5 of 10 seeds use the compass and the population share is not held
   above the operator-alone level; under the default operator in the patchy world it is held above the
   operator-alone bound on 9 of 10 seeds. The open quantity is s itself, by world and by operator, measured rather than bounded,
   with SE-Z's host change and A9's clade route in the design.
2. **RBT-113, the evolvability benchmark: filed, not run.** A back-pocket calibration of how strongly this
   simulator responds to selection: replicate lines selected up and down on one heritable trait, with
   unselected controls, under the default operator and any candidate setting, giving a realised
   heritability with an interval across seeds. Its ticket names the trigger: "RBT-112's operator change is
   adopted, or proposed for adoption, so we can measure evolvability before and after" (RBT-113,
   description, Chaotic). This paper does not propose that adoption.
3. **The proposal rate, for de novo.** Holding a planted compass does not bear on whether one arises. Paper
   8 puts the drift proposal of a *paying* routed compass at order 10⁻⁵ per lineage or below; RBT-102 says
   a zero becomes informative against matched drift only at about 184,000 genomes; P1 shows a 2.5× prize
   alone did not lift a sub-paying structure at n = 7. Any de novo test is sized by those numbers and
   registered against a matched replay null (RBT-102 §2.7).
4. **Reach, relative to the host.** RBT-104's question is unanswered. Its post hoc F4 names the variable: a
   compass's drive relative to its host's drive on the same Effectors, which a uniform link scale cannot
   change. A test of it, like every other, runs its per-arm control on its own founders and shows it
   passable at a stated s before launch.

---

## 10. Conclusion

Paper 8 ended on the magnitude gap: drift proposes the compass's structure and never its magnitude. This
paper supplied the magnitude by hand, on the Pioneer body's controller, and asked what selection does with
it.

Where the compass paid about two and a half times more, in a world that was also richer and bred faster,
selection held a planted paying compass on nine founding populations of ten, and every line's champions
were food-dependent through it. Where it paid less, it was held on no seed. Five of ten lost their
planted-rooted lineages by season 599, three of them after reading above the operator-alone bound at 300.
In the five where planted lineages survived, none of their living carried a paying compass. About two
thirds of the operator's erosion is one mutation, the walk of the global biases. Freezing it left the
compass in the best lines of half the uniform-world populations (5 of 10), which used it, but selection
did not raise its share of the population above what the operator alone leaves. On the arms' own
likelihood (model-based, for the frozen-bias host, whose income also rose; the registered limit is below
~0.1) its advantage there is between nothing and about eight percent a generation, and a change in s
itself is not handled.

So the planted compass is **held** in the world where it pays about 2.5× more, which is also richer and
faster-breeding, **used** by the best where the operator leaves it, and **not spread**, in the uniform
world, where selection on it is weak. Whether a compass can arise, rather than be kept, is the
proposal-rate question, and this paper does not reach it. Whether any of this holds for a co-evolved body
is not a question these arms can ask.

---

## Sources

Every row cites the committed file its number re-derives from; `docs/paper-10/rederive.txt` row ids in
brackets.

| claim | file | rows |
|---|---|---|
| The prize, uniform +0.844 and one-field patchy +2.103, 2.49×, base incomes | `runs/RBT-106/prize.txt` | W1–W5, W3q, W5q |
| The prize in P-801's world +2.267; own world 8/10 PAYS, P-801 world 4/10 | `runs/RBT-103/adversary/world_matrix.txt`; `runs/RBT-103/REPORT.md` | W6–W8 |
| Patchiness, not density or regrowth (exploratory) | `runs/RBT-103/REPORT.md`, "Its size depends on the food's patchiness" | — |
| 0 of 12,276; drift reads 0 in 81/100 and NOT HELD in 91/100; ~184,000 genomes | `runs/RBT-102/REPORT.md`; `informative_n.txt`; `adversary/replay_null.txt` | D1, D2 |
| RBT-104 VOID; the control's scale; the post hoc probes; F4 | `runs/RBT-104/readout.txt`; `REPORT.md`; `readout-adversary/READOUT-ADVERSARY.md` §1, §5 | V1, V2 |
| The erosion: u(8) 0.282 → 0.089; structure's own 0.067; per seed −0.193; 68% (post hoc) | `runs/RBT-112/baseline/baseline-w32[-S0]-SEED.txt`; `runs/RBT-106/baseline/baseline-w32-SEED.txt`; `runs/RBT-112/erasure.txt`, `DECISION.md` | E0–E6 |
| P1: P-NULL, 7 usable, paired F +0.049, all-ten +0.254; power at n = 7 | `runs/RBT-106/P1-readout.txt`; `P1-READOUT.md`; `p1-adversary/ADVERSARY.md`, `power_n7.txt` | P0–P4 |
| H: HELD 0/9, COMPASS 0/10, paired F +3.858, income +1.771, births, depth, power at n = 10 | `runs/RBT-106/H-readout.txt`; `{HU,HP}-SEED/held-{300,599}.txt`; `H-READOUT.md` | H1–H8, H10 |
| H's own-genealogy null 0.7% / 1.3%; size 2.2 × 10⁻⁴; the split lesion; H3, H4, H8 | `runs/RBT-106/h-adversary/ADVERSARY.md`, `ownnull_pool.txt`, `rederive.txt` | H9, H11 |
| RBT-112: HELD 0/1, LOST 1, COMPASS 0/5, paired F +1.654 / +0.468, carriers 5/70 against 31/70, SE-Z +0.160, planted-rooted n 199 against 386 | `runs/RBT-112/readout.txt`; `READOUT.md`; `sensitivity.txt` | Z1–Z8 |
| Power at the realised n; the likelihood of s; the balance point; the design anchors | `runs/RBT-112/readout-adversary/instrument.txt`; `runs/RBT-112/power.txt`; M15 from `runs/RBT-112/adversary/ADVERSARY.md` | Z9–Z12 |
| The balance point at the default operator (post hoc, this paper) | the rows above | M1, M2 |
| A1, A3–A9 | `runs/RBT-112/readout-adversary/ADVERSARY.md` | — |
| RBT-105: 5 of 14 flips, 0.13–0.65; the A/A citation | `runs/RBT-105/REPORT.md` | A1, A2 |
| The planted founders (w = 1, w = 32); the one-field world | `runs/RBT-106/PREREGISTRATION.md` §2, §3.2; `one_field.txt` | — |
| Rulings: RBT-102 16:55; RBT-103 17:45 (2026-09-26); RBT-104 01:52, 02:00; RBT-106 P1 06:06, H 08:20; RBT-112 08:28, 12:20 (2026-09-27) | Chaotic RBT-102, RBT-103, RBT-104, RBT-106, RBT-112 | — |
| RBT-113's scope and trigger | Chaotic RBT-113, description | — |
| The magnitude gap; the proposal rate | `docs/paper-8-the-prize-the-proposal-rate-and-the-magnitude-gap.md` | — |
