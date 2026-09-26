# Net of Arithmetic

Four sudden changes, two bodies, and what the held-out challenges could and could not see.

*Ninth paper in the Rabbitstew series, written under Chaotic RBT-109. **Draft, filed for review;
nothing in it has been adversaried as a paper.** Every challenge result it reports has been through
its own readout adversary and a coordinator ruling, and this paper's wording is bound by the merged
report after that round: **no sentence here is stronger than the merged `REPORT.md` it cites**, and
where an adversary narrowed a claim, the narrowed form is the one used. It reports RBT-89's held-out
challenge set (`docs/held-out-challenges.md`) on RBT-90 part 2's ten founding populations: **C1
crowding** (RBT-92), **C2 dearer work** (RBT-99) and **C3 scarce food** (RBT-100), all closed, and
**C4 flat terrain** (RBT-101), **under its readout adversary as this is written; §3.4 is a marked
stub** and is filled from the merged report when RBT-101 closes. No new run was made for this paper.
Every number is cited to a committed file on the integration branch. The summary table's figures and
the power figures of §8 are recomputed from those files by `docs/paper-9/rederive.py`, whose printed
output is `docs/paper-9/rederive.txt`; the bracketed tags in the text ([S3], [P1] and so on) are that
file's row ids. Where a re-derivation goes beyond what a merged report says, the text says so and
labels it post hoc. Placeholders for results that had not merged when this was written are marked
**[PENDING: …]**.*

---

## Abstract

A population of co-evolved bodies and a population of designed wheeled bodies with evolved brains
foraged side by side in the same economy for 352 to 382 seasons, on ten founding populations. Then
one thing about their world changed and stayed changed: eight robots to an arena instead of four
(C1), work priced at 0.08 per kJ instead of 0.03 (C2), six food items instead of twelve (C3), or
the obstacles removed (C4). The owner's question was whether the co-evolved body holds up against
a novel challenge, and whether it beats or at least draws with the designed body. The protocol
fixed a class rule, a comparator, a null and the windows before any arm ran.

On C1–C3 the registered rule returned **class A, co-evolved wins**, every time. **It returns the
same class with no event at all**: on the no-event baseline's own recovery window and on 23 of 25
placebo onsets, in every challenge [S4, S9, S16]. The co-evolved body already led by +0.16 before the onset
(`runs/RBT-92/REPORT.md` §2), and the rule measured that lead. The only readout that speaks to an
event is the paired contrast, event arm minus no-event baseline, and read that way the three
challenges say three different things. Crowding's differential effect is **+0.03 [−0.04, +0.10],
unresolved** [S3]. Dearer work's resolves, **+0.37 [+0.16, +0.58]**, but the price alone, applied to
two populations that change nothing, predicts **+0.69**: the designed gait burns 3.6 times the
co-evolved gait's kJ before the event [S6, S11]. Scarce food's paired effect, **+0.14 [+0.01, +0.27]**
under the registered coding, lies inside the bracket its arithmetic sets, **+0.12** if the unchanged
designed population stayed alive and **+0.32** if it went extinct as its arithmetic says it must
[S12–S15]. **No resolved event effect exceeds the upper end of what its unchanged-population
arithmetic attributes to differences the two bodies carried before the event**, and no difference in how the two bodies
*responded* is shown: C3's residual is +0.02 at a minimum detectable effect of about 0.15 [S17], and
C2's one resolved residual favours the designed body on an unregistered scale (`runs/RBT-99/REPORT.md`,
"Both nets"). What C2 and C3 do establish is survivorship of the co-evolved body's standing gait at a
price and a density at which an unchanged designed gait would be insolvent on every seed.

The reusable result is the instrument. Seven lessons came out of the three readout adversaries and
the coordinator's rulings on them, each of which changed what a registered readout was allowed to
say (§6). What would answer the owner's question is depth and a common garden (RBT-107), at a power
this programme has not yet had (§8).

---

## Summary table

Recovery window [T+60, T+160), ten seeds, 95% t(9) intervals, positive counts. "Paired" is the
event arm's co-evolved − designed income minus the no-event baseline's, per seed, which equals
co-evolved R-shift − designed R-shift. "Arithmetic" is what the event does to two populations that
change nothing, computed from pre-onset quantities. "Residual" is paired − arithmetic.

| challenge | registered class | class with no event | paired effect | arithmetic (unchanged populations) | residual | verdict, in the merged report's words |
|---|---|---|---|---|---|---|
| **C1** crowding, group size 4 → 8 (RBT-92) | **A**, +0.180 [+0.077, +0.284], 8/10, r 0.104 | **A** on the base (+0.148, 9/10); A on 23/25 placebo onsets | **+0.032 [−0.041, +0.105]**, 6/10 [S3] | none registered; there is no resolved effect to account for | = the paired effect, unresolved (MDE ≈ 0.10 [S5]) | "Under crowding the co-evolved body kept the income lead it already had … it certifies that the lead persisted, not that the co-evolved body withstood crowding better." |
| **C2** dearer work, 0.03 → 0.08 per kJ (RBT-99) | **A**, +0.519 [+0.336, +0.702], 10/10, r 0.183 | **A** on the base; 23/25 placebo onsets | **+0.371 [+0.162, +0.581]**, 10/10 [S7]; against the registered null, n = 7: +0.315 [+0.161, +0.469], 7/7 | **+0.689** [+0.627, +0.751] (price × pre-onset kJ, both alive) [S6]; +0.631 if the insolvent unchanged designed fauna is scored extinct (post hoc, this paper) [S11b] | **−0.318 [−0.498, −0.138]**, 2/10 [S8]: the designed body recovered more absolute income; as a share of price, the difference is unresolved | "The paired effect is therefore the co-evolved body's cheapness before the event, which is C2's claim. It is not a difference in how the two bodies responded." |
| **C3** scarce food, 12 → 6 items (RBT-100) | **A**, +0.286 [+0.191, +0.382], 10/10, r 0.095 | **A** on the base; 23/25 placebo onsets | **+0.138 [+0.006, +0.271]**, 8/10, extinct seasons at 0 as registered [S13]; +0.061 [−0.022, +0.143] with them dropped | bracket **+0.121** (alive) to **+0.316** (unchanged designed fauna extinct, as its arithmetic implies) [S12, S15] | **+0.017 [−0.092, +0.127]** against the alive end [S14]; −0.178 [−0.292, −0.065] against the insolvent end; MDE ≈ 0.15 [S17] | "The arithmetic brackets the paired effect, +0.12 to +0.32, without deciding whether either body responded better. The design could not have detected a response difference below about 0.15." |
| **C4** flat terrain (RBT-101) | **[PENDING: RBT-101 readout adversary]** | [PENDING] | [PENDING] | the solo-probe terrain arithmetic (`runs/RBT-101/flat_probe.txt`), [PENDING] | [PENDING] | [PENDING] |

Sources: `runs/RBT-92/REPORT.md` and `readout.txt`; `runs/RBT-92/readout-adversary/probe_readout.txt`
P3–P4; `runs/RBT-99/REPORT.md`, `score.txt`, `placebo.txt`, `price.txt`,
`readout-adversary/probe_readout.txt` P2; `runs/RBT-100/REPORT.md`, `score.txt`, `placebo.txt`,
`readout-adversary/probe_readout.txt` P2–P4; re-derived in `docs/paper-9/rederive.txt`. The C1
interval re-derives as [−0.040, +0.105] from the per-seed values printed to three places; the
report's [−0.041, +0.105] is from full precision (`probe_readout.txt` P4).

---

## 0. What this paper is, and what it is not

It is a synthesis of four pre-registered arms and their readout adversaries. The measurements are
the tickets'. What the paper adds is the frame, class rule against paired contrast against
arithmetic, applied the same way to every challenge; one post hoc re-derivation (C2's insolvent end,
§3.2), labelled as such; the power arithmetic of §8; and a catalogue of what the three adversary
rounds taught the instrument.

It is **not** a finding that the co-evolved body is more robust to sudden change than the designed
one. The registered rule said A on all three closed challenges, and the paper's first result is
that the rule could not have said anything else about C1–C3. It is not a
finding that the two bodies respond the same, either: "unresolved" in this paper never means
"equal", and §4 gives the effect sizes the design could not have seen. It is not a claim about
adaptation. Inside the recovery window a lineage has had about five reproduction events
(`runs/RBT-92/baseline_depth.txt`: median 5.0 on both faunas, range 3–7), so the protocol's own
words apply: a body "survives" or "is sorted" and does not "re-adapt" (`docs/held-out-challenges.md`
§10, §14 item 10). And it is not a claim about any founding population but these ten, in one
economy.

It is the paper the owner agreed to at 20:25 UTC on 2026-09-26: phase 2 written up as it stands,
rather than more challenge epochs of the same kind (RBT-109, description).

---

## 1. The design, in one page

**The world.** The dense foraging baseline (`docs/held-out-challenges.md` §1): arenas of four robots
sharing twelve food items in a 3 m disc; energy from eating, a basal cost of 0.25 a season and a
work cost of 0.03 per kJ of actuator work; breed at 3, pay 1; die at zero energy or age 60. Two
populations of sixty live in separate arena banks: the **co-evolved** (holistic) population, bodies
and brains from random morphologies, and the **designed** population, the Pioneer wheeled body with
an evolvable brain under `--conventional-topology`, evolved in the same run for the same seasons on
its own RNG stream (§4 of the protocol; RBT-95). No robot has a sensor for energy, work, age or the
number of food items (protocol §1).

**The founding populations.** The ten RBT-90 part 2 seeds (801, 804, 805, 806, 807, 1, 2, 3, 4, 7),
all read, none dropped (`runs/RBT-92/SEED-RULE.md`). Each seed's RBT-90 run is its no-event
**baseline**, byte-identical to every event arm up to the onset (V0 passed on 10/10 seeds in every
challenge: `runs/RBT-92/REPORT.md` §1, `runs/RBT-99/REPORT.md` §1, `runs/RBT-100/REPORT.md` §1).

**The onset.** Season T = 352–382 per seed, placed off the cohort cycle (`runs/RBT-92/onset.txt`).
At T one flag changes and stays changed (`--shift-at T --shift FLAG=VALUE`). The null arm removes a
random k of each fauna at T instead, k being that fauna's excess deaths in the event arm's first ten
seasons; cull20 removes twenty of each and is the turnover reference (RBT-92 Amendment 2).

**The axis.** `mean_lifetime_score` from each arm's `seasons.txt`: a living robot's lifetime mean
per-season score, averaged over the living. **R-body** is co-evolved − designed on that axis;
**R-shift** is event − baseline for one fauna; **R-null** is event − null.

**The windows.** Transient [T, T+60), **recovery [T+60, T+160)**, which is primary, and tail
[T+160, T+200). The transient is one `max_age`: every individual alive at the onset is dead by its
end (protocol §8; checked on the C2 event arms, `runs/RBT-99/readout-adversary/probe_readout.txt` P9).

**The class rule** (protocol §9). Class A when mean R-body in the recovery window of the event arm
is ≥ +0.10, positive on ≥ 8 of 10 seeds, and |mean| ≥ r, where r is the larger of the season-noise
line and the t(9) half-width of the per-seed values; C is the mirror, the falsifier; D and E are
bankruptcy classes tested by income below 0.25 or alive below 12; B needs r ≤ 0.10; F is the rest.

**What was not built.** Carriage of pre-event body structure (the descent tracer's L) was
registered, but its validation, V3, failed on the same cull20 arms in every challenge, so it is
unread everywhere (§6, lesson 6). Recovery time was registered and is unread (§6, lesson 4).

---

## 2. The registered rule measured the pre-existing lead

Before any event, in [T−100, T), the co-evolved body out-earned the designed body by **+0.158
[+0.080, +0.236]**, positive on 9/10 seeds; on the no-event baseline's recovery window it still did,
**+0.148 [+0.051, +0.245]**, 9/10 (`runs/RBT-92/REPORT.md` §2; the same baseline and T serve all
three challenges). Both clear the class-A bar. So the rule, applied to an arm and a window with no
event in them, returns A.

The C1 readout adversary made this a test rather than an observation. It moved a fake onset T′
from T−200 to T+40 in steps of ten and applied the registered rule to the baseline alone over
[T′+60, T′+160): **A on 23 of 25 placebo onsets**, the two misses being F by the sign guard at 7/10
(`runs/RBT-92/readout-adversary/probe_readout.txt` P3). C2 and C3 share the baseline and the onsets,
so their `placebo.txt` returns the same 23/25 by construction [S4, S9, S16].

| arm, window | C1 | C2 | C3 |
|---|---|---|---|
| baseline, before | A (+0.158) | A | A |
| baseline, recovery | A (+0.148) | A | A |
| placebo onsets, baseline alone | A on 23/25 | A on 23/25 | A on 23/25 |
| **event arm, recovery (the verdict)** | **A** (+0.180) | **A** (+0.519) | **A** (+0.286) |
| paired event − base, recovery | +0.032, 6/10: B by the rule's letter; its equivalence form fails by 0.005 | +0.371, 10/10: A by the rule's letter | +0.138, 8/10: positive count at the guard, zero margin |

Sources: `runs/RBT-92/readout-adversary/probe_readout.txt` P3; `runs/RBT-99/placebo.txt` P3,
`runs/RBT-99/readout-adversary/READOUT-ADVERSARY.md` F4; `runs/RBT-100/placebo.txt` P3,
`runs/RBT-100/REPORT.md` §2.

**What this means, in the words the coordinator ruled at 18:45 (RBT-92):** "The class rule measures
the level of the lead, not robustness to the event." Every class A in C1–C3 is correct under the rule
as registered, and none was re-scored. But none of them is evidence about the event: a null event
also returns A.

Three consequences follow, each stated in the merged reports:

- **C1.** "The pre-registered rule scores this class A. The same rule returns A on the no-event
  baseline, so it certifies that the lead persisted, not that the co-evolved body withstood crowding
  better." (`runs/RBT-92/REPORT.md`, headline.)
- **C2.** "The rule also returns A where there is no event … Unlike C1, the paired event contrast
  classifies A as well … So here the event did move the contrast. What moved it is the arithmetic
  below." (`runs/RBT-99/REPORT.md`, headline.)
- **C3.** "What class A certifies here: nothing about the shift." (`runs/RBT-100/REPORT.md`,
  headline.)

The sign guard is a second, smaller fragility. On C1 the event arm was positive on exactly 8/10
against a guard of 8; jittering the per-seed values by the A/A-like spread returns F in roughly 1 in
10 to 1 in 5 replicates (`runs/RBT-92/REPORT.md` §7 item 9). On C2 and C3 the event arm's guard has a
two-seed margin and holds in ≥ 99.4% and ≥ 99.8% of jittered replicates
(`runs/RBT-99/REPORT.md`, "A/A"; `runs/RBT-100/REPORT.md` §2), but C3's *paired* contrast, at 8/10,
"would be a coin flip on replication" (same, §2).

---

## 3. Each event, net of its arithmetic

The coordinator's 19:05 ruling on RBT-99 set the rule this section follows: "before reading any
event contrast, compute what the event does to an **unchanged** population by arithmetic from
pre-onset quantities … Only the residual can be a response." The 20:06 ruling on RBT-100 added that
where the arithmetic says an unchanged population is insolvent, the prediction is a bracket, alive
against extinct.

### 3.1 C1, crowding: no resolved effect to account for

**What the event did.** Eight robots to an arena from T; capacity 60 ÷ 8 leaves one group of four
each season, identically on both faunas and every seed, so 6.7% of robot-seasons after T were in the
small group on both sides (`runs/RBT-92/REPORT.md` §5, "Remainder groups").

**The paired effect is unresolved.** Co-evolved R-shift −0.020 [−0.073, +0.034], designed −0.052
[−0.091, −0.013], difference **+0.032 [−0.041, +0.105]**, 6/10 (`runs/RBT-92/REPORT.md` §3; [S1–S3]).
A random cull of a third of each fauna moves the same contrast by +0.043 (cull20 − base,
`runs/RBT-92/readout-adversary/READOUT-ADVERSARY.md` F5), and the equivalence form, |0.032| + 0.073 =
0.105, is not below 0.10, "so neither an effect of crowding on the contrast nor its absence is shown"
(same, F7).

**The designed body's cost does not resolve against the registered null.** −0.052 against the
no-event control, **−0.037 [−0.081, +0.006]** against the random cull of the same size
(`runs/RBT-92/REPORT.md` §3). The report makes no statement that crowding resolvably cost the
designed body.

**No arithmetic was registered for C1, and none is needed here**: there is no resolved effect for
it to account for. The designer's own pre-registered mechanism, that crowding halves the density a
mower's yield rides on so the cheap mowers would lose most, was scored wrong: "They lost the least"
(`runs/RBT-92/REPORT.md` §6). Both populations stayed at capacity and nobody starved.

**The sentence** (`runs/RBT-92/REPORT.md`, headline, the adversary's F2 text): "Under crowding the
co-evolved body kept the income lead it already had over the designed body: +0.18 [+0.08, +0.28]
with the shift and +0.15 [+0.05, +0.25] without it, on the same seeds and windows. … Crowding's
differential effect on the two bodies is +0.03 [−0.04, +0.10]. That is unresolved, and it is the
size of what a random cull of a third of each fauna does (+0.04). Neither body's income fell by more
than r."

### 3.2 C2, dearer work: the price takes more than was lost

**The arithmetic.** Income is food eaten minus the work cost times kJ. At an unchanged gait the shift
from 0.03 to 0.08 removes 0.05 × kJ from every robot, and by T+60 every robot alive was born after T,
so an unchanged population's recovery R-shift is −price
(`runs/RBT-99/readout-adversary/READOUT-ADVERSARY.md` F2). Before T the designed gait spent **19.0
kJ** a season against the co-evolved gait's **5.2**, a ratio of 3.6 [S11], so the price is **0.950**
for the designed body and **0.261** for the co-evolved one (`runs/RBT-99/price.txt`). Two unchanged
populations would have diverged by **+0.689 [+0.627, +0.751]** [S6].

**The observed paired effect is smaller than that.** **+0.371 [+0.162, +0.581]**, 10/10 [S7], about
54% of the arithmetic. Against the registered null on the seven seeds where the cull did not empty
a fauna it is +0.315 [+0.161, +0.469], 7/7 (`runs/RBT-99/REPORT.md`, headline table).

**The insolvent end, applied after the fact (this paper, post hoc).** Lesson 7 postdates C2's
ruling, and the merged report quotes only the alive end. It applies to C2 as it does to C3: the
unchanged designed gait at 0.08 earns **−0.140 to +0.092**, below the 0.25 basal cost on every seed
[S11d] (the adversary's figure, `probe_readout.txt` P2). Scored as the extinct population that
implies, the prediction is **+0.631 [+0.577, +0.684]** [S11b]. **So C2's bracket is +0.63 to +0.69,
and the observed +0.37 lies below both ends.** Unlike C3, the insolvent end is the *smaller*
prediction here, because an unchanged designed fauna at 0.08 earns less than nothing and extinction
scores 0. The re-derivation reads the base designed recovery income from the adversary's committed
P2 table; it changes no sentence of the report, and it is offered as the consistent application of
lesson 7, not as a finding the report's adversary reviewed.

**The residual favours the designed body, on a scale nobody registered.** Net of its own price each
body recovered part of its loss: the co-evolved body **+0.207 [+0.151, +0.262]** (79% of its price),
the designed body **+0.524 [+0.362, +0.687]** (55%). In absolute income the designed body recovered
more, **−0.318 [−0.498, −0.138]** [S8]; as a share of price the co-evolved body recovered more, +0.29
[−0.02, +0.61], unresolved (`runs/RBT-99/readout-adversary/READOUT-ADVERSARY.md` F2). Each net
carries its conditioning: the designed one is "survivor-conditioned on the 7 seeds where it survived;
pinned by extinction on 3", the co-evolved one "a survivors' lifetime mean, at low turnover"
(`runs/RBT-99/REPORT.md`, "Both nets"). The merged report's conclusion: "Neither scale was registered.
**Neither body can be said to have adapted better.**"

**The sentence** (`runs/RBT-99/REPORT.md`, headline, the adversary's F2 text): "The paired effect is
therefore the co-evolved body's cheapness before the event, which is C2's claim. It is not a
difference in how the two bodies responded. At an unchanged gait the designed fauna would earn below
basal on every seed; it stayed solvent on 6/10 seeds only by turnover (3.9–6.7× its baseline's
deaths) and went extinct on 3."

### 3.3 C3, scarce food: inside the bracket

**The arithmetic.** Halving the items halves every body's gross food and leaves its work bill where
it was. From the baselines' own pre-onset seasons [T−40, T), the designed body ate 1.22–1.50 items a
season against the co-evolved body's 1.02–1.35, so the halving takes more from it: a price of
**0.697** against **0.576** (`runs/RBT-100/score.txt` §1). At an unchanged gait the designed season
net falls to +0.08 to +0.18, **below basal on 10/10 seeds**; the co-evolved net to +0.29 to +0.59,
**above basal on 10/10** (same). The per-seed values were computed after the arms, from pre-onset
data only; the form was registered before any arm (`runs/RBT-100/REPORT.md` §3).

**Linearity** cannot be tested before T, where alive is 60 and the items are 12 throughout; in the
first three seasons after T, before selection can act, gross food per survivor, event ÷ baseline, is
**0.488** (co-evolved) and **0.497** (designed), per seed 0.36–0.58 (`runs/RBT-100/readout-adversary/probe_readout.txt` P2).

**The bracket.** Two unchanged populations that stay alive predict **+0.121 [+0.066, +0.176]** [S12];
other pre-T windows, an axis-scale correction and an empirical density response give +0.113 to +0.146
(`probe_readout.txt` P2). Scoring the unchanged designed fauna as the extinct population its own
arithmetic implies predicts **+0.316 [+0.242, +0.390]** [S15]. The observed **+0.138 [+0.006,
+0.271]**, 8/10 [S13], sits between them. Against the alive end the residual is **+0.017 [−0.092,
+0.127]**; against the insolvent end it is −0.178 [−0.292, −0.065], "the designed fauna did better
than an unchanged, insolvent one" (`runs/RBT-100/REPORT.md` §3).

**The residual splits by extinction.** +0.090 on the five seeds where the designed fauna went extinct,
which carry 82% of the effect, and −0.056 on the five where it survived (same). The lower bound of
the paired effect depends on the coding of extinct seasons: +0.061 [−0.022, +0.143], unresolved, with
them dropped; +0.190 at −0.25 (`runs/RBT-100/REPORT.md` §2). The class is A under all four codings.

**Nets side by side.** Co-evolved **+0.131** (23% of its price recovered), designed **+0.114** (16%);
the difference, +0.017, "is unresolved; this design could detect only a difference above ≈ 0.15"
[S17] (`runs/RBT-100/REPORT.md` §3).

**The sentence** (`runs/RBT-100/REPORT.md`, headline, the adversary's F2 text): "The arithmetic
therefore brackets the paired effect, +0.12 to +0.32, without deciding whether either body responded
better. The design could not have detected a response difference below about 0.15."

### 3.4 C4, flat terrain — STUB, pending RBT-101

> **[PENDING: RBT-101.]** C4 is under its readout adversary (report PR #193; the adversary's PR to
> come; session_01PE2cfEntg4vnvzqMKAGQNC). This section is filled from the **merged** `REPORT.md`
> and the coordinator's ruling when RBT-101 closes, and no number from the unmerged report is used
> here. The protocol requires C4, the one challenge the robots can perceive with the wiring they
> have, to be reported **separately** from C1–C3 and never pooled with them
> (`docs/held-out-challenges.md` §2 C4, §14 item 7); this section and its table row are kept apart
> for that reason, and §2's and §4's statements about "every challenge" are statements about
> C1–C3 until it is filled.

**TODO when RBT-101 closes (in this order):**

1. The registered class, R-body in the recovery window with its interval, positive count, r and
   the sign-guard margin, in the merged report's post-adversary words.
2. The class on the no-event baseline and on placebo onsets (lesson 1). Whether the event changed
   the class relative to the baseline, which on C1–C3 it did not.
3. The paired event − base contrast and event − null, with the k = 0/0 seeds named (lesson 2).
4. The arithmetic: the solo-probe terrain prediction (`runs/RBT-101/flat_probe.txt`, registered
   before the arms), its paired prediction, the residual and its interval, and whatever the adversary
   ruled about solo flat ground against arena flat ground and about per-seed predictive power
   (lesson 3). Whether a bracket applies (lesson 7).
5. The re-wiring readout, the one C4-specific registered readout: its verdict per fauna, its blind
   spot (the effect size below which it cannot see), and its null.
6. Lessons 4–6 as applied (recovery, survival, carriage).
7. The summary table's C4 row; the abstract's and §0's sentences about C4; §4 and §9 if C4 changes
   the "no response difference shown" statement; §8 if the ruling changes RBT-107's premise.
8. The Sources table rows for `runs/RBT-101/`.

---

## 4. No difference in response between the bodies is shown

Put the three residuals side by side, each read against its own design's power.

| challenge | what the residual is | value | resolves? | minimum detectable at n = 10, 80% power |
|---|---|---|---|---|
| C1 | the paired effect itself (no arithmetic) | +0.032 [−0.041, +0.105] | no | 0.101 [S5] |
| C2 | paired − arithmetic (alive end), = net co-evolved − net designed | −0.318 [−0.498, −0.138] | **yes, toward the designed body**, in absolute income | 0.250 [S10] |
| C2 | the same, as a share of price | +0.29 [−0.02, +0.61] | no | — |
| C3 | paired − arithmetic (alive end) | +0.017 [−0.092, +0.127] | no | 0.152 [S17] |

The minimum detectable effect uses the residual's own between-seed sd and the RBT-100 adversary's
form, (t₀.₉₇₅ + t₀.₈₀) × sd ⁄ √n (`runs/RBT-100/readout-adversary/probe_readout.txt` P4, which gives
0.152 for C3; `docs/paper-9/rederive.txt` reproduces it and applies the same form to C1 and C2).

So:

- **No residual resolves in the co-evolved body's favour.** C1's and C3's do not resolve at all; C3's
  design could not have seen one smaller than about 0.15, which is **1.3 times the whole alive-end
  arithmetic effect** (`runs/RBT-100/readout-adversary/READOUT-ADVERSARY.md` F4).
- **The one residual that resolves goes the other way**, and on a scale that was not registered.
  Net of its price the designed body recovered more absolute income than the co-evolved body in C2;
  as a share of price it recovered less, unresolved. The designed net is inflated by survivor
  conditioning on seven seeds and pinned by extinction on three. The merged report's reading is
  that neither body can be said to have adapted better, and this paper does not go past it.
- **"Not shown" is not "equal".** None of these designs can show equivalence. C1's equivalence form
  fails by 0.005; C2's and C3's MDEs are 0.25 and 0.15.

The summary sentence, in the coordinator's words (RBT-107, 20:28 UTC): "every event effect so far lies
inside its unchanged-population arithmetic; no response difference is shown, at an MDE of ≈ 0.15
(n = 10)". This paper's re-derivation sharpens "inside" for C2 (§3.2): the effect is below both ends
of C2's bracket, so the arithmetic accounts for all of it and more. And the MDE differs by challenge:
about 0.10 on C1, 0.15 on C3, 0.25 on C2, where extinction on three seeds widened the between-seed
spread.

---

## 5. What C2 and C3 did establish: survivorship of a standing gait

C2 and C3 were registered as budget challenges, whose claim is not the owner's contest but
"survivorship of the co-evolved population at an economic boundary the designed body's budget is not
expected to survive" (protocol §2, C2; C3 "as C2, … here the bootstrap line for food"). On those terms
both are answered, and both answers are arithmetic of the pre-onset gait.

- **C2.** The co-evolved recovery income was +0.79 to +1.22 on 10/10 seeds, never near basal, and its
  cost against the control does not resolve (−0.055 [−0.123, +0.013]); against the registered null it
  resolves and is small (−0.074 [−0.117, −0.031]) (`runs/RBT-99/REPORT.md` §5, headline table). Its
  unchanged-gait income at 0.08 would have been +0.53 to +1.00, above basal on every seed
  (`runs/RBT-99/readout-adversary/READOUT-ADVERSARY.md` F2). The designed fauna failed D's test on
  4/10, went extinct on 3, and stayed solvent on 6/10 "only by turnover".
- **C3.** "At half the food the established co-evolved population paid its way by income on every
  seed, as its pre-onset gait's arithmetic says it would" (`runs/RBT-100/REPORT.md` §4): survivors'
  own net +0.50 to +0.66, a starved share of 1.2–2.5% of each season's runners. **Random co-evolved
  founders at six items failed on 7/10 seeds** (pre-registered; seed 7 borderline, 8 alive and rising
  at the season-59 cut). The designed fauna went extinct on 5/10 seeds, fell below the floor of 12 on
  2 more, and on 3 (804, 807, 7) "stayed solvent by clear margins, against an arithmetic that called
  an unchanged gait insolvent on all 10".

Two cautions travel with these. **Survival read from alive = 60 carries no information** (§6, lesson
5): the co-evolved claims rest on income, and the informative survival facts are the ones that
cannot refill, designed extinction and founders6. And **class D was not reached on either
challenge**, so neither is a class-D result: C2's D test fired on 4/10 and C3's on 7/10, both below the
8/10 guard, and on the seeds where D did not fire the class-A lead is not over a bankrupt comparator
(`runs/RBT-100/REPORT.md`, "D's test, per seed").

The designed fauna's partial solvency is the one thing in C2–C3 that the arithmetic did not
predict: an unchanged designed gait is insolvent on every seed in both challenges, and the designed
fauna stayed solvent on 6/10 (C2) and 3/10 (C3). Whether that is sorting on gait, turnover of a
lifetime mean, or survivor conditioning, "the committed tables" do not separate
(`runs/RBT-99/REPORT.md` §8; `runs/RBT-100/REPORT.md` §6).

---

## 6. The instrument lessons

Every one of these was found by someone other than the designer: a readout adversary, and then a
coordinator ruling that carried it to the challenges not yet read. C3's designer applied lessons 1–6
before its readout adversary saw it, and the adversary still found the seventh. They are the
reusable result: none depends on the ecology's details, and each is a rule a future event readout
can follow before it runs. Paper 7's catalogue form is kept (what the instrument said, why it was
wrong, what caught it, the rule).

| # | lesson | where it bit | what the registered readout said | what caught it | the rule now |
|---|---|---|---|---|---|
| 1 | **Placebo onsets.** Apply the class rule to the no-event baseline and to fake onsets before reading it on the event. | C1 | class A, read in the first summary as "the co-evolved body survives crowding and keeps its lead" | RBT-92 readout adversary F2 (A on the base; 23/25 placebo onsets) | "Every challenge readout … must report the class on the no-event baseline and on placebo onsets beside the event arm" (coordinator, 18:45 on RBT-92) |
| 2 | **Paired event − base, and event − null.** The only readout that speaks to the event is the per-seed paired contrast against the no-event baseline, and against the random-cull null. | C1, C2 | the designed body's crowding cost "resolves", read against the control only | RBT-92 adversary F3: against the registered null it is −0.037 [−0.081, +0.006] | "The paired event − base contrast against the random-cull null is the only readout that speaks to the event" (18:45) |
| 3 | **Arithmetic first.** Compute what the event does to an unchanged population from pre-onset quantities; only the residual can be a response. | C2 | "most of the verdict is the designed body's collapse"; the co-evolved body "got back about 80% of its price", read alone | RBT-99 adversary F2, F3: the price predicts +0.69; the designed body recovered more in absolute terms | coordinator, 19:05 on RBT-99 |
| 4 | **No recovery claim from d = 0.** A lifetime-mean axis starts every paired difference at 0 and moves slowly (lag-1 autocorrelation 0.69); a 20-season hold starting at T is met before divergence can show. | C1, C2 | "never left the control's band on 6 seeds"; "returned within 180 seasons on 9/10" | RBT-92 adversary F4 (every seed leaves the band; d = 0 count depends on h: 0/10 at 0.5 SD to 6/10 at 2 SD); RBT-99 adversary F7 | "The registered recovery-time rule cannot return 'none' for a slow divergence. Report its numbers as registered, and make no recovery claims from them" (18:45) |
| 5 | **Survival is uninformative under refill.** Deaths are refilled by births within the season and `alive` is recorded at season end, so alive = 60 is the ecology's state, not a result. | C1–C3 | "both survive" scored as a hit | RBT-92 adversary F2 (alive = 60 in every season of [T−100, T+200) in all 37 runs; minimum window income 0.69 against 0.25) | only non-refilling facts count: extinction, founders that fail to bootstrap, income below basal |
| 6 | **UNVALIDATED means unread.** A readout whose validation failed enters no sentence, including a prediction scored "right" and a number printed "for the record". | C1–C3 | carriage L scored "right"; designed Lc printed "not read" | RBT-92 adversary F8; RBT-99 F12; RBT-100 F10 | V3 failed by design (a same-season refill hides the cull from `alive`), and its proposed fix repairs only the manipulation half: validating L needs an effect L must register, such as a cull of whole lineages (RBT-92 §1) |
| 7 | **The bracket.** When the arithmetic says an unchanged population is insolvent, lesson 3's prediction is two numbers, alive and extinct, and the residual is read against both. | C3 (and C2, §3.2) | "arithmetic, and nothing beyond it"; "not a difference in how the two bodies responded"; "a similar part of its price" | RBT-100 adversary F2, F4 | coordinator, 20:06 on RBT-100, adopted programme-wide |

Six smaller rules came out of the same rounds and bind the same readouts:

- **Judge a paired contrast on the paired A/A scale.** The per-fauna A/A-like RMS (0.077) is the
  wrong scale for R-body; the paired one is 0.071–0.108, pooled 0.091 (`runs/RBT-100/readout-adversary/READOUT-ADVERSARY.md` F7).
- **Jitter the sign guard.** A count met with zero margin is a coin flip on replication; say so
  (RBT-92 F6; RBT-100 F7).
- **Label outcome-defined subsets post hoc**, including the registered D partition, and show the
  alternatives (RBT-99 F5).
- **Show the extinction coding's sensitivity** beside a registered coding that sets an interval's
  lower bound (RBT-100 F5).
- **Do not borrow a class's sentence for a class that missed its guard.** "Outlasts a bankrupt
  comparator" is D's; D missed on C3, and its three non-D seeds were not near misses (RBT-100 F6).
- **An upper bound certifies only one direction.** "Above basal" from an upper bound certifies
  nothing (RBT-100 F8).

What they have in common is paper 7's class, in a new place: each is a registered readout that
computed correctly and answered a different question from the one its sentence asked. The class
rule answered "is there a lead?" and was read as "who withstood the event?"; the recovery rule
answered "had they diverged yet?" and was read as "had they recovered?"; `alive` answered "did the
economy refill the slots?" and was read as "did they survive?"; the paired contrast answered "how did
the two bodies' pre-onset differences meet the event?" and was read as "who responded better?".

---

## 7. The calibration beside it

**The arena's A/A null (RBT-96).** Two runs identical except for the holistic RNG stream, on four
seeds, differ by an RMS of **0.128** in the arena's final-fifth score, three times the designer's
prediction; at n = 4 the resulting 95% null half-width is **h = 0.178**, so the programme's ±0.10
arena rule was unsound at n = 4 (`runs/RBT-96/REPORT.md` §3–§4). Most of it is one seed's discovery
event, "the null behaving as a search". It is a different instrument (the arena, not the ecology) and
is cited here as the programme's warning that an assumed noise figure can be three times too small.

**The ecology's A/A-like spread, from the committed arms.** RBT-105's founder-sharing replicates had
not merged when C1–C3 were read, so each readout adversary built an A/A-like reference from the
committed cull contrasts, which diverge one fauna from the baseline at T by an intervention with an
expected effect near 0 on the mean: per fauna, RMS **0.077–0.10**; on the paired R-body scale, **0.071
(cull − base) to 0.108 (cull20 − base), pooled 0.091** (`runs/RBT-92/readout-adversary/READOUT-ADVERSARY.md`
F5; `runs/RBT-100/readout-adversary/probe_readout.txt` P5). The between-seed t intervals in this paper
carry run-to-run noise inside them by construction, so they do not depend on this figure; what does
is any reading of a single seed, and none is made.

- **RBT-108 (the arena A/A at n = 16):** **[PENDING: RBT-108 merge; cite its REPORT and readout here,
  with the extended RMS and h, and whether RBT-96's 0.128 and the "9 seeds for ±0.10" line stand.]**
- **RBT-105 (the ecology A/A, `runs/RBT-105/aa_spread.txt`):** **[PENDING: RBT-105 merge; quote its
  recovery-window per-fauna RMS against the 0.08–0.11 used above.]** The adversaries ruled in
  advance what it can and cannot move: it is holistic-only (the designed fauna is byte-identical
  across its replicates by construction), it diverges from season 0 and so is an upper bound for a
  challenge arm's recovery window, and it **cannot move any class or paired sign in C1–C3**
  (`runs/RBT-92/readout-adversary/READOUT-ADVERSARY.md` F5; RBT-99 F9; RBT-100 F7). If its RMS is much
  larger than 0.2 per fauna, the between-seed intervals stand but the per-seed tables should not be
  printed (RBT-92 F5).

---

## 8. What would answer the question

The question the challenge set was built for is not the one it answered. It answered: *does a
standing lead survive a change, and does a cheap gait outlast a dear one?* Yes, on these seeds, and
both are statements about the bodies before the event. The owner's question, whether the co-evolved
body *holds up* better, needs a readout of response, and the challenge set's design could not supply
one, for three reasons this paper can state exactly.

**Depth.** The recovery window holds about five reproduction events (`runs/RBT-92/baseline_depth.txt`).
"Re-adapts" at five events is sorting of standing variation at most (protocol §10). RBT-107, filed at
19:35 with the owner's budget, proposes to extend the C4 event arms from their checkpoints to a post-event
window of roughly twenty events **[PENDING: cite `runs/RBT-107/depth.txt` on integration; the design
draft measures 2.7–3.3 reproduction events per 100 seasons after T and proposes scoring at T + 800,
about 22 events (RBT-107, designer's comment 19:55)]**.

**Arithmetic.** A population readout carries the event's arithmetic, which on C2 and C3 was larger
than any residual the design could see. RBT-107's primary readout is a **common garden**: the fauna
alive late in the event, baseline and cull20 arms, all scored on the same fixed worlds, so that the
event's arithmetic cancels by construction; its positive control is C2 in the same garden, where both
populations are priced at 0.08 (RBT-107, designer's comment 19:55; coordinator 20:28).

**Power.** At n = 10 the smallest paired effect the ecology could detect at 80% power was about 0.10
on C1, 0.15 on C3 and 0.25 on C2 (§4). The table below gives the MDE at larger n for each of the
spreads this programme has measured, taking the n = 10 sd as the planning value [P1–P5].

| planning sd | source | n = 10 | n = 16 | n = 20 | n = 30 | n = 40 | n for MDE 0.10 | n for MDE 0.05 |
|---|---|---|---|---|---|---|---|---|
| 0.091 | ecology paired A/A-like RMS [P1] | 0.091 | 0.068 | 0.060 | 0.048 | 0.041 | 9 | 28 |
| 0.101 | C1 paired event − base [P2] | 0.101 | 0.076 | 0.067 | 0.054 | 0.046 | 11 | 35 |
| 0.153 | C3 residual [P4] | 0.152 | 0.115 | 0.101 | 0.081 | 0.070 | 21 | 76 |
| 0.251 | C2 residual [P3] | 0.250 | 0.188 | 0.166 | 0.133 | 0.114 | 52 | 201 |
| 0.128 | arena A/A RMS, RBT-96 [P5] | 0.127 | 0.096 | 0.085 | 0.068 | 0.058 | 15 | 54 |

MDE = (t₀.₉₇₅,n−1 + t₀.₈₀,n−1) × sd ⁄ √n, two-sided 5%, 80% power (`docs/paper-9/rederive.py`).

Three readings of it:

1. **If a common garden removes the arithmetic and leaves a spread near the ecology's paired A/A
   (0.09), ten seeds detect a response difference of about 0.09 and sixteen about 0.07.** That is at
   the protocol's smallest effect worth claiming, 0.10 (protocol §7). This is conditional: no garden
   readout's between-seed spread has been measured on the event arms, and a garden that inherits
   extinction heterogeneity as C2 and C3 did would sit nearer the lower rows.
2. **If the readout keeps a residual with C3's spread, n ≈ 21 reaches 0.10; with C2's, n ≈ 52.** At
   ten seeds, the readout the challenge set used could not have seen a response difference the size
   of its own arithmetic.
3. **Halving the MDE costs about four times the seeds on every row.** A 0.05 response difference is
   out of reach of any design in the programme's current budget unless the garden's spread is well
   below the A/A-like 0.09.

The coordinator's 20:28 instruction to RBT-107 is the same point in operational form: state the
garden readout's MDE at n = 10, and if n = 10 cannot see an effect of the size that would matter
(≤ 0.10), propose more seeds as a costed option rather than dilute the design. **[PENDING: RBT-107's
registered MDE and seed count, when its pre-registration clears its adversary.]**

What would change this paper's answer: a common-garden readout at twenty events that resolves a
response difference, in either direction, larger than the ecology's paired A/A spread, on a
pre-registered statistic with a pre-registered null. Nothing in C1–C3 is evidence for or against
such a difference.

---

## 9. Limitations

- **Ten founding populations, one economy, one onset per seed.** Every class, contrast and residual
  here is for RBT-90 part 2's ten seeds, at T = 352–382, in the dense foraging baseline. None
  replicates RBT-28's, RBT-71's or RBT-84's populations (`runs/RBT-92/REPORT.md` §7 item 12).
- **The null was weak.** On C1 the registered cull removed 0–3 co-evolved robots (k = 0 on 6/10
  seeds), so the turnover guard was scored on n = 4; on C2 the designed k reached or exceeded 60 on
  three seeds and the null was extinction there; on C3 the turnover guard was declared not
  interpretable in advance (`runs/RBT-92/REPORT.md` §3; `runs/RBT-99/REPORT.md` §3;
  `runs/RBT-100/REPORT.md` §2). cull20 is the turnover reference throughout.
- **Seed 806 carries an onset-drift flag** (its baseline deaths over [T, T+10) were 54 against a
  period mean of 34.3) and is read with the flag in every challenge (`runs/RBT-92/readout.txt`).
- **The arithmetic is per population, linear, and computed after the arms** from pre-onset data. On
  C3 its linearity was checked only in the first three post-onset seasons, and per seed the designed
  response departs from linear by up to ±0.15 (`runs/RBT-100/readout-adversary/READOUT-ADVERSARY.md` F3).
- **C2's insolvent end (§3.2) is this paper's own post hoc re-derivation**, not reviewed by C2's
  readout adversary, and it is not used to change any merged sentence.
- **The ecology A/A is pending** (§7). The paired intervals do not depend on it; per-seed readings,
  none of which are made, would.
- **Carriage and recovery are unread** throughout (lessons 4, 6), so nothing here says which
  lineages carried what through any event.
- **C4 is missing** (§3.4) until RBT-101 closes, and when it lands it is reported apart, as the one
  perceivable challenge.

---

## 10. Conclusion

On three held-out challenges the registered rule said the co-evolved body wins, and the rule would
have said so without the challenge. Read the only way that speaks to the event, as a paired contrast
against the unchanged course of the same population, the challenges said: crowding did nothing the
design could resolve to either body's lead; dearer work widened the lead by less than the price of the
designed body's costlier gait; scarce food widened it by an amount the food arithmetic brackets on
both sides. The co-evolved body's standing gait was cheap enough to pay its way through dearer work
and half the food, on every seed, which is what C2 and C3 set out to test and what the arithmetic of
that gait predicted before either event. No difference in how the two bodies responded is shown, at
the effect sizes the design could see.

The owner's question, whether a co-evolved body holds up against a novel challenge better than a
designed body with a grafted brain, is still open, and this paper says what would close it: depth
enough for a response to exist, a common garden so the event's arithmetic cancels, and enough seeds
that a response of the size worth claiming can be seen. Seven lessons were learned on the way
here, each found by someone asked to attack a readout. Those lessons, and not the three class-A
verdicts, are what phase 2 leaves to phase 3.

---

## Sources

Every row cites the committed file its number comes from; `docs/paper-9/rederive.txt` row ids in
brackets.

| Claim | File | Rows |
|---|---|---|
| The protocol: baseline, challenge set, windows, class rule, depth ≈ 2 × seasons ÷ 60 | `docs/held-out-challenges.md` §1–§10 | — |
| Seeds, onsets T = 352–382, seed 806 drift flag | `runs/RBT-92/SEED-RULE.md`, `onset.txt`, `readout.txt` | — |
| Depth in [T, T+160): median 5.0 on both faunas | `runs/RBT-92/baseline_depth.txt` | — |
| Baseline R-body before +0.158, recovery +0.148 | `runs/RBT-92/REPORT.md` §2; `runs/RBT-92/readout.txt` | — |
| C1 class A +0.180 [+0.077, +0.284], r 0.104; R-shifts; paired +0.032; designed R-null −0.037 | `runs/RBT-92/REPORT.md`; `runs/RBT-92/readout.txt` | S1–S3, S5 |
| C1 class on the base, placebo 23/25, paired sd, equivalence 0.105; A/A-like RMS; sign-guard jitter; recovery-band exits | `runs/RBT-92/readout-adversary/probe_readout.txt` P3–P6; `READOUT-ADVERSARY.md` F2–F8 | S4 |
| C2 class A +0.519, r 0.183; nets; shift − cull n = 7; headline wording | `runs/RBT-99/REPORT.md` | — |
| C2 price per seed and fauna; kJ 19.0 / 5.2 | `runs/RBT-99/price.txt` | S6, S11 |
| C2 arithmetic +0.689, observed +0.371, residual −0.318, share difference | `runs/RBT-99/score.txt`; `runs/RBT-99/readout-adversary/probe_readout.txt` P2 | S6–S8, S10 |
| C2 insolvent end +0.631 and unchanged designed income −0.140..+0.092 (post hoc, this paper) | `runs/RBT-99/readout-adversary/probe_readout.txt` P2 ("base con inc"), `runs/RBT-99/price.txt` | S11b–S11d |
| C2 placebo 23/25; per-seed paired values | `runs/RBT-99/placebo.txt` P3–P4 | S7, S9 |
| C3 class A +0.286, r 0.095; D per seed; nets; founders6; wording | `runs/RBT-100/REPORT.md` | — |
| C3 per-seed arithmetic, alive end +0.121, residual +0.017 | `runs/RBT-100/score.txt` §1 | S12, S14 |
| C3 insolvent end +0.316; linearity 0.488 / 0.497; variants +0.113..+0.146; extinction coding; MDE 0.152; paired A/A 0.091 | `runs/RBT-100/readout-adversary/probe_readout.txt` P2–P5 | S15, S17, P1 |
| C3 placebo 23/25; per-seed paired values | `runs/RBT-100/placebo.txt` P3–P4 | S13, S16 |
| Arena A/A RMS 0.128, h 0.178, 9 seeds for ±0.10 | `runs/RBT-96/REPORT.md` §3–§4 | P5 |
| Power table | `docs/paper-9/rederive.py` → `rederive.txt` | P1–P6 |
| Lessons 1–7 and the rulings | Chaotic RBT-92 (18:45, 18:50), RBT-99 (19:05, 19:10), RBT-100 (20:06, 20:14); the readout adversaries' `READOUT-ADVERSARY.md` under each `runs/RBT-NN/readout-adversary/` | — |
| RBT-107's depth and common-garden design | Chaotic RBT-107 (designer 19:55, coordinator 20:28); **[PENDING: `runs/RBT-107/` on integration]** | — |
| C4 | **[PENDING: `runs/RBT-101/REPORT.md` and its readout adversary, when merged]**; `runs/RBT-101/flat_probe.txt` (registered before the arms) | — |
| Instrument taxonomy | `docs/paper-7-five-instruments.md` | — |
