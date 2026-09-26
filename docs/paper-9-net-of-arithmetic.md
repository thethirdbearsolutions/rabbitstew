# Net of Arithmetic

Four sudden changes, two bodies, and what the held-out challenges could and could not see.

*Ninth paper in the Rabbitstew series, written under Chaotic RBT-109. **Draft, revised after paper
adversary rounds 1 and 2** (PR #205, `docs/paper-9/adversary/PAPER-ADVERSARY.md`, F1–F33; coordinator
rulings on RBT-109 at 20:52 and 21:05 UTC, every finding accepted and applied). The adversary's files
arrive with PR #205, which merges with or before this paper's PR. Every challenge
result it reports has been through its own readout adversary and a coordinator ruling, and this
paper's wording is bound by the merged report after that round: **no sentence here is stronger than
the merged `REPORT.md` it cites**, and where an adversary narrowed a claim, the narrowed form is the
one used. It reports RBT-89's held-out challenge set (`docs/held-out-challenges.md`) on RBT-90 part
2's ten founding populations: **C1 crowding** (RBT-92), **C2 dearer work** (RBT-99), **C3 scarce
food** (RBT-100) and **C4 flat terrain** (RBT-101), all closed. As the protocol requires, C4, the one
perceivable challenge, is reported apart from C1–C3 and never pooled with them. No new run was made
for this paper. Every number is cited to a committed file on the integration branch. The summary
table's paired effects, arithmetic and residuals, and the power figures of §8, are recomputed or
quoted from those files by `docs/paper-9/rederive.py`, whose printed output is `docs/paper-9/rederive.txt`; the bracketed tags
in the text ([S3], [P1] and so on) are that file's row ids. Where a figure goes beyond what a merged
report registered, the text labels it **post hoc** and says whose it is. Quotations from a designer's
or the coordinator's Chaotic comments, rather than from a committed file, are cited as Chaotic.
Results that had not merged when this was written are marked **[PENDING: …]**; the paper's final
argument waits on one of them, RBT-110.*

---

## Abstract

A population of co-evolved bodies and a population of designed wheeled bodies with evolved brains
foraged side by side in the same economy for 352 to 382 seasons, on ten founding populations. Then
one thing about their world changed and stayed changed: eight robots to an arena instead of four
(C1), work priced at 0.08 per kJ instead of 0.03 (C2), six food items instead of twelve (C3), or
the obstacles removed (C4). The owner's question was whether the co-evolved body holds up against
a novel challenge, and whether it beats or at least draws with the designed body. The protocol
fixed a class rule, a comparator, a null and the windows before any arm ran.

On C1–C3 the registered rule returned **class A, co-evolved wins**. **It returns A with no event at
all**: on the no-event baseline's own recovery window, and on 23 of 25 placebo onsets. That is one
test on the shared baseline, which serves every challenge [S4]. So on C1–C3 the class carries no
information about the event. On C2 its size also carries the price arithmetic. On C4 the event
flipped the class to **C, the owner's falsifier**, "the designed body wins on the held-out
challenge", and the post hoc arena arithmetic accounts for all of the flip.

The only readouts that speak to an event are the paired contrasts: event arm minus the no-event
baseline, and event arm minus the random-cull null. Read that way, **no paired effect exceeds its unchanged-population arithmetic on C2 and C3, or on C4 on the post hoc
arena predictors**:

- **Crowding:** the differential effect is **+0.03 [−0.04, +0.10], unresolved** [S3].
- **Dearer work:** **+0.37 [+0.16, +0.58]**, less than the **+0.69** that the price alone predicts,
  because the designed gait burns 3.6 times the co-evolved gait's kJ [S6, S11].
- **Scarce food:** **+0.14 [+0.01, +0.27]** under the registered coding. That lies inside the
  bracket its arithmetic sets: **+0.12** if the unchanged designed population stayed alive, and
  **+0.32** if it went extinct, as its arithmetic implies. Against the null the effect is **+0.11
  [−0.05, +0.26], unresolved** [S12–S15, S13n].
- **Flat terrain (reported apart):** **−0.46 [−0.60, −0.32]**, which the furniture's arithmetic,
  measured in the arena itself, over-predicts at **−0.63 to −0.81** (post hoc, the readout adversary's
  predictors) [S18, S21]. The registered prior, a solo probe, under-predicts it (−0.33, or −0.16 with
  its registered discount) [S28, S30].

**Non-arithmetic residuals resolve in opposite directions.** C2's residual resolves against both ends of its bracket, toward the designed body. C4's resolves toward the co-evolved body against two of the three post hoc arena predictors (Z10 and the same-season split; not Z), and toward the designed body against its registered prior with the registered discount. On C2, net of its
price, the designed body recovered more absolute income: −0.32 [−0.50, −0.14] against the alive end,
and −0.26 [−0.45, −0.07] against the insolvent end (post hoc, this paper). That is an unregistered
scale, survivor-conditioned [S8, S11c]. On C4 the contrast moved back toward the co-evolved body:
+0.17 [+0.06, +0.29] or +0.27 [+0.05, +0.49], 8/10 each. That is on post hoc arena predictors, and a
hypothesis, not a finding [S22, S26]. The co-evolved body sits on its arithmetic there; the
non-arithmetic part is on the designed side. Against C4's registered prior the residual runs the other
way: −0.30 [−0.51, −0.08] with the registered discount, toward the designed body, and −0.13, unresolved,
without it [S29, S31]. So C4's direction depends on the predictor. The paper builds no single narrative from the two. **[PENDING: RBT-110,** which tests
C4's refund/response split out of sample on C1–C3.**]**

What C2 and C3 do establish is the survivorship of the co-evolved **population, by income**. It
paid its way at a price and at a density where an unchanged designed gait would be insolvent on
every seed.

The reusable result is the instrument. Eight lessons came out of the four readout adversaries and
the coordinator's rulings on them. Each changed what a registered readout was allowed to say (§6).
What would answer the owner's question is depth and a common garden (RBT-107), at a power this
programme has not yet had (§8).

---

## Summary table

Recovery window [T+60, T+160), ten seeds, 95% t(9) intervals, positive counts.
- **Paired** is the event arm's co-evolved − designed income minus the no-event baseline's, per
  seed. It equals co-evolved R-shift − designed R-shift.
- **Arithmetic** is what the event does to two populations that change nothing.
- **Residual** is paired − arithmetic.

C4 is in its own block, as the protocol requires; it is not pooled with C1–C3.

| challenge | registered class | class with no event | paired effect (event − base; event − null) | arithmetic (unchanged populations) | residual | verdict, in the merged report's words |
|---|---|---|---|---|---|---|
| **C1** crowding, group size 4 → 8 (RBT-92) | **A**, +0.180 [+0.077, +0.284], 8/10, r 0.104 | **A** on the base (+0.148, 9/10); A on 23/25 placebo onsets | **+0.032 [−0.041, +0.105]**, 6/10 [S3f]; designed R-null −0.037 [−0.081, +0.006] | none registered; there is no resolved effect to account for | = the paired effect, unresolved (MDE ≈ 0.10 [S5]) | "Under crowding the co-evolved body kept the income lead it already had … it certifies that the lead persisted, not that the co-evolved body withstood crowding better." |
| **C2** dearer work, 0.03 → 0.08 per kJ (RBT-99) | **A**, +0.519 [+0.336, +0.702], 10/10, r 0.183 | **A** on the base; 23/25 placebo onsets | **+0.371 [+0.162, +0.581]**, 10/10 [S7f]; against the null, n = 7: +0.315 [+0.161, +0.469], 7/7 | **+0.689** [+0.627, +0.751] (0.05 × pre-onset kJ, both alive) [S6]; +0.631 [+0.577, +0.684] with the insolvent unchanged designed fauna scored extinct (**post hoc, this paper**) [S11b] | **−0.318 [−0.498, −0.138]**, 2/10 [S8]; **−0.260 [−0.448, −0.071]**, 2/10, against the insolvent end (post hoc) [S11c]: toward the designed body at both ends, in absolute income; as a share of price, unresolved | "The paired effect is therefore the co-evolved body's cheapness before the event, which is C2's claim. It is not a difference in how the two bodies responded." |
| **C3** scarce food, 12 → 6 items (RBT-100) | **A**, +0.286 [+0.191, +0.382], 10/10, r 0.095 | **A** on the base; 23/25 placebo onsets | **+0.138 [+0.006, +0.271]**, 8/10, extinct seasons at 0 as registered [S13f]; +0.061 [−0.022, +0.143] with them dropped; against the null **+0.106 [−0.045, +0.256]**, 7/10, unresolved [S13n] | bracket **+0.121** (alive) to **+0.316** (unchanged designed fauna scored extinct, as its arithmetic implies) [S12, S15] | **+0.017 [−0.092, +0.127]** against the alive end [S14]; −0.178 [−0.292, −0.065] against the insolvent end; MDE ≈ 0.15 [S17] | "The arithmetic therefore brackets the paired effect, +0.12 to +0.32, without deciding whether either body responded better. The design could not have detected a response difference below about 0.15." |

| perceivable challenge | registered class | class with no event | paired effect (event − base; event − null) | arithmetic (unchanged populations) | residual | verdict, in the merged report's words |
|---|---|---|---|---|---|---|
| **C4** flat terrain (RBT-101) | **C, the falsifier**, −0.310 [−0.481, −0.139], 9/10 negative, r 0.171, margin 1 seed | **A** on the base; 23/25 placebo onsets; **C only on the event arm** | **−0.458 [−0.596, −0.320]**, 0/10 [S18f]; against the null **−0.472 [−0.585, −0.359]** (≡ event − base on the six k = 0/0 seeds) [S19] | registered prior (solo probe): −0.325 [S28], −0.163 with its registered discount [S30]; arena, **post hoc**: **−0.630** (Z10) [S21], −0.701 (Z), −0.806 (simulated C0) [S27]; same-season refund −0.721 [S25] | registered prior: −0.133, unresolved [S29]; **−0.296 [−0.511, −0.080], toward the designed body**, with its discount [S31]. Post hoc: **+0.172 [+0.055, +0.289]**, 8/10, against Z10 [S22]; same-season response **+0.272 [+0.053, +0.491]**, 8/10 [S26]. **The direction depends on the predictor** | "So the falsifier fires wholly by the arithmetic of the furniture … Beyond the arithmetic the contrast moved back toward the co-evolved body … (post hoc, the adversary's predictor)." |

**Sources.** Every cell is from a committed file, re-derived in `docs/paper-9/rederive.txt`:
- C1: `runs/RBT-92/REPORT.md`, `readout.txt`, `readout-adversary/probe_readout.txt` P3–P4.
- C2: `runs/RBT-99/REPORT.md`, `score.txt`, `placebo.txt`, `price.txt`,
  `readout-adversary/probe_readout.txt` P2.
- C3: `runs/RBT-100/REPORT.md`, `score.txt`, `placebo.txt`, `readout-adversary/probe_readout.txt`
  P2–P4.
- C4: `runs/RBT-101/REPORT.md`, `placebo.txt`, `readout-adversary/probe_arena.txt`,
  `probe_refund.txt`.

**Precision.** The [S…f] rows quote each readout's full-precision line, and the printed intervals
are those. The unsuffixed [S1], [S3], [S7], [S13], [S18] and [S28]–[S31] rows recompute the same statistic from
per-seed values printed to three places, so their bounds can differ in the third decimal. For
example, [S3] gives [−0.040, +0.105] against [S3f]'s [−0.0405, +0.1049]. The C4 registered-prior residuals are printed as
`runs/RBT-101/REPORT.md` §4 gives them; [S31] recomputes −0.296 as [−0.511, −0.081] against the
report's [−0.511, −0.080].

---

## 0. What this paper is, and what it is not

**What it is.** A synthesis of four pre-registered arms and their readout adversaries. The
measurements are the tickets'. What the paper adds:
- **the frame**, class rule against paired contrast against arithmetic, applied the same way to
  every challenge;
- **one post hoc re-derivation** (C2's insolvent end, §3.2), labelled as such;
- **the power arithmetic** of §8;
- **a catalogue** of what the four adversary rounds taught the instrument.

**It is not a finding that the co-evolved body is more robust to sudden change than the designed
one.** The registered rule said A on C1–C3. It returns the same class with no event, so on those
three its A carries no information about the event. On C4 it said C, and on the post hoc arena
arithmetic that flip is the furniture's.

**It is not a finding that the two bodies respond the same, either.** "Unresolved" in this paper
never means "equal", and §4 gives the effect sizes each design could not have seen. Two residuals
that do resolve point in opposite directions. Both rest on an unregistered scale or a post hoc
predictor.

**It is not a claim about adaptation.** Over the transient plus recovery windows, [T, T+160), a
lineage has had about five reproduction events (`runs/RBT-92/baseline_depth.txt`: median 5.0 on
both faunas, range 3–7 co-evolved and 3.5–6.0 designed). So the protocol's own words apply: a body
"survives" or "is sorted" and does not "re-adapt" (`docs/held-out-challenges.md` §10, §14 item 10).
C4's re-wiring readout saw no change at the resolution its positive control certifies (§3.4).

**It is not a claim about any founding population but these ten**, in one economy.

It is the paper the owner agreed to at 20:25 UTC on 2026-09-26: phase 2 written up as it stands,
rather than more challenge epochs of the same kind (RBT-109, description).

---

## 1. The design, in one page

**The world.** The dense foraging baseline (`docs/held-out-challenges.md` §1).
- Arenas of four robots share twelve food items in a 3 m disc.
- Energy comes from eating. The basal cost is 0.25 a season, and the work cost is 0.03 per kJ of
  actuator work.
- A robot breeds at 3 and pays 1, and dies at zero energy or at age 60.
- Two populations of sixty live in separate arena banks:
  - the **co-evolved** (holistic) population, bodies and brains from random morphologies;
  - the **designed** population, the Pioneer wheeled body with an evolvable brain under
    `--conventional-topology`, evolved in the same run for the same seasons on its own RNG stream
    (protocol §4; RBT-95).
- No robot has a sensor for energy, work, age or the number of food items (protocol §1). Obstacles
  are perceivable through contact and posture sensors, which is why C4 is the one perceivable
  challenge (protocol §2, C4).

**The founding populations.** The ten RBT-90 part 2 seeds (801, 804, 805, 806, 807, 1, 2, 3, 4, 7),
all read, none dropped (`runs/RBT-92/SEED-RULE.md`). Each seed's RBT-90 run is its no-event
**baseline**, byte-identical to every event arm up to the onset. V0 passed on 10/10 seeds in every
challenge (`runs/RBT-92/REPORT.md` §1, `runs/RBT-99/REPORT.md` §1, `runs/RBT-100/REPORT.md` §1,
`runs/RBT-101/REPORT.md` §1).

**The onset.** Season T = 352–382 per seed, placed off the cohort cycle (`runs/RBT-92/onset.txt`).
At T one flag changes and stays changed (`--shift-at T --shift FLAG=VALUE`).
- **The null arm** removes a random k of each fauna at T instead, where k is that fauna's excess
  deaths in the event arm's first ten seasons.
- **cull20** removes twenty of each fauna. It is the turnover reference (RBT-92 Amendment 3,
  `runs/RBT-92/PREREGISTRATION.md`; `runs/RBT-92/REPORT.md` §3).

**The axis.** `mean_lifetime_score` from each arm's `seasons.txt`: a living robot's lifetime mean
per-season score, averaged over the living.
- **R-body** is co-evolved − designed on that axis.
- **R-shift** is event − baseline for one fauna.
- **R-null** is event − null.

**The windows.** Transient [T, T+60), **recovery [T+60, T+160)**, which is primary, and tail
[T+160, T+200). The transient is one `max_age`, so every individual alive at the onset is dead by
its end (protocol §8; checked on the C2 event arms, `runs/RBT-99/readout-adversary/probe_readout.txt`
P9).

**The class rule** (protocol §9).
- **A:** mean R-body in the recovery window of the event arm is ≥ +0.10, positive on ≥ 8 of 10
  seeds, and |mean| ≥ r. Here r is the larger of the season-noise line and the t(9) half-width of
  the per-seed values.
- **C:** the mirror image of A, and the falsifier.
- **D and E:** bankruptcy classes, tested by income below 0.25 or alive below 12.
- **B:** needs r ≤ 0.10.
- **F:** everything else.

**What was not read.**
- **Carriage** of pre-event body structure (the descent tracer's L) was registered, but its
  validation, V3, failed on the same cull20 arms in every challenge. It is unread everywhere (§6,
  lesson 6).
- **Recovery time** was registered and is unread (§6, lesson 4).

---

## 2. The registered rule measured the pre-existing lead on C1 and C3; on C2 it also carries the price; on C4 the event flipped it

**The lead before any event.** In [T−100, T) the co-evolved body out-earned the designed body by
**+0.158 [+0.080, +0.236]**, positive on 9/10 seeds. On the no-event baseline's recovery window it
still did: **+0.148 [+0.051, +0.245]**, 9/10 (`runs/RBT-92/REPORT.md` §2). The same baseline and T
serve all four challenges. Both values clear the class-A bar. So the rule, applied to an arm and a
window with no event in them, returns A.

**The C1 readout adversary made this a test.** It moved a fake onset T′ from T−200 to T+40 in steps
of ten, and applied the registered rule to the baseline alone over [T′+60, T′+160). The result is
**A on 23 of 25 placebo onsets**; the two misses are F by the sign guard at 7/10
(`runs/RBT-92/readout-adversary/probe_readout.txt` P3).

**It is one test, not four replications.** C2, C3 and C4 share the baseline and the onsets. The identical
sequence, AAAAAAAAAAAAAAAAAAAAAAFFA, is printed by construction in C1's
`runs/RBT-92/readout-adversary/probe_readout.txt` P3 (RBT-92 has no `placebo.txt`) and in
`runs/RBT-99/placebo.txt`, `runs/RBT-100/placebo.txt` and `runs/RBT-101/placebo.txt` P3 [S4, S9,
S16, S20]. The C1–C3 comparison is `docs/paper-9/adversary/probe_paper.txt` B; C4's sequence is
checked against its own `placebo.txt` (paper adversary round 2, F29); and
`runs/RBT-99/readout-adversary/READOUT-ADVERSARY.md` F4 calls it "RBT-92's result by construction".

| arm, window | C1 | C2 | C3 | C4 (apart) |
|---|---|---|---|---|
| baseline, before | A (+0.158) | A | A | A |
| baseline, recovery | A (+0.148) | A | A | A |
| placebo onsets, baseline alone | A on 23/25 (one test on the shared baseline) | same | same | same |
| **event arm, recovery (the verdict)** | **A** (+0.180) | **A** (+0.519) | **A** (+0.286) | **C** (−0.310) |
| paired event − base, recovery | +0.032, 6/10: B by the rule's letter; its equivalence form fails by 0.005 | +0.371, 10/10: A by the rule's letter | +0.138, 8/10: positive count at the guard, zero margin | −0.458, 0/10 |

Sources: `runs/RBT-92/readout-adversary/probe_readout.txt` P3; `runs/RBT-99/placebo.txt` P3,
`runs/RBT-99/readout-adversary/READOUT-ADVERSARY.md` F4; `runs/RBT-100/placebo.txt` P3,
`runs/RBT-100/REPORT.md` §2; `runs/RBT-101/placebo.txt` P3, `runs/RBT-101/REPORT.md` §2.

**What this means.** The coordinator ruled at 18:45 on RBT-92 (Chaotic): "The class rule measures the
level of the lead, not robustness to the event." Every class in C1–C4 is correct under the rule as
registered, and none was re-scored. The four challenges say different things about what the class
carries:

- **C1.** "The same rule returns A on the no-event baseline, so it certifies that the lead persisted,
  not that the co-evolved body withstood crowding better." (`runs/RBT-92/REPORT.md`, headline.)
- **C2.** The class carries the price arithmetic as well as the lead. "The rule also returns A where
  there is no event … Unlike C1, the paired event contrast classifies A as well … So here the event did
  move the contrast. What moved it is the arithmetic below." (`runs/RBT-99/REPORT.md`, headline.)
- **C3.** "What class A certifies here: nothing about the shift." (`runs/RBT-100/REPORT.md`, headline.)
- **C4.** "Unlike C1, the class is the event's. … Only on the shift arm does it return C." The
  event's own contribution is the furniture's arithmetic, on the post hoc arena predictors (§3.4)
  (`runs/RBT-101/REPORT.md`, headline).

**The sign guard is a second, smaller fragility.**
- **C1.** The event arm was positive on exactly 8/10, against a guard of 8. Jittering the per-seed
  values by the A/A-like spread returns F in roughly 1 in 10 to 1 in 5 draws. That is "an
  illustration, not a test" (`runs/RBT-92/readout-adversary/READOUT-ADVERSARY.md` F6 and
  `probe_readout.txt` P5(e); `runs/RBT-92/REPORT.md` §7 item 9).
- **C2 and C3.** The event arm's guard has a two-seed margin, and holds in ≥ 99.4% and ≥ 99.8% of
  jittered replicates (`runs/RBT-99/REPORT.md`, "A/A"; `runs/RBT-100/REPORT.md` §2). But C3's
  *paired* count of 8/10 "would be a coin flip on replication" (same, §2).
- **C4.** The margin is one seed. The class survives leaving any seed out, every 100-season window,
  one flipped seed, and 98.4% of jitters at the paired A/A scale (`runs/RBT-101/REPORT.md` §6).

---

## 3. Each event, net of its arithmetic

The coordinator's 19:05 ruling on RBT-99 (Chaotic) set the rule this section follows: "before
reading any event contrast, compute what the event does to an **unchanged** population by arithmetic
from pre-onset quantities … Only the residual can be a response." Two later rulings added to it:
- **20:06, on RBT-100:** where the arithmetic says an unchanged population is insolvent, the
  prediction is a bracket, alive against extinct.
- **20:40, on RBT-101:** make the arithmetic in the axis's own setting, and split refund from
  response at one season.

### 3.1 C1, crowding: no resolved effect to account for

**What the event did.** From T there are eight robots to an arena. Capacity 60 ÷ 8 leaves one group
of four each season, identically on both faunas and every seed. So 6.7% of robot-seasons after T
were in the small group, on both sides (`runs/RBT-92/REPORT.md` §5, "Remainder groups").

**The paired effect is unresolved.**
- Co-evolved R-shift is −0.020 [−0.073, +0.034] and designed −0.052 [−0.091, −0.013]. The difference
  is **+0.032 [−0.041, +0.105]**, 6/10 (`runs/RBT-92/REPORT.md` §3; [S1f, S2, S3f]).
- A random cull of a third of each fauna moves the same contrast by +0.043 (cull20 − base,
  `runs/RBT-92/readout-adversary/READOUT-ADVERSARY.md` F5).
- The equivalence form, |0.032| + 0.073 = 0.105, is not below 0.10, "so neither an effect of
  crowding on the contrast nor its absence is shown" (same, F7).

**The designed body's cost does not resolve against the registered null.** It is −0.052 against the
no-event control and **−0.037 [−0.081, +0.006]** against the random cull of the same size
(`runs/RBT-92/REPORT.md` §3). The report makes no statement that crowding resolvably cost the
designed body.

**No arithmetic was registered for C1, and none is needed**: there is no resolved effect for it to
account for. The designer's own registered mechanism was that crowding halves the density a mower's
yield rides on, so the cheap mowers would lose most. It was scored wrong: "They lost the least"
(`runs/RBT-92/REPORT.md` §6). That ordering holds only on the means, and the difference is
unresolved (same, §6: "the other way on the means (+0.032 unresolved)"). Both populations stayed at
capacity, and nobody starved.

**The sentence** (`runs/RBT-92/REPORT.md`, headline, the adversary's F2 text): "Under crowding the
co-evolved body kept the income lead it already had over the designed body: +0.18 [+0.08, +0.28]
with the shift and +0.15 [+0.05, +0.25] without it, on the same seeds and windows. … Crowding's
differential effect on the two bodies is +0.03 [−0.04, +0.10]. That is unresolved, and it is the
size of what a random cull of a third of each fauna does (+0.04). Neither body's income fell by more
than r."

### 3.2 C2, dearer work: the price takes more than was lost

**The arithmetic.**
- Income is food eaten minus the work cost times kJ. At an unchanged gait, the shift from 0.03 to
  0.08 removes 0.05 × kJ from every robot.
- By T+60 every robot alive was born after T, so an unchanged population's recovery R-shift is
  −price (`runs/RBT-99/readout-adversary/READOUT-ADVERSARY.md` F2).
- Before T the designed gait spent **19.0 kJ** a season against the co-evolved gait's **5.2**, a
  ratio of 3.6 [S11]. So the price is **0.950** for the designed body and **0.261** for the
  co-evolved one (`runs/RBT-99/price.txt`).
- Two unchanged populations would have diverged by **+0.689 [+0.627, +0.751]** [S6]. `price.txt` was
  computed after the arms, from pre-onset seasons only. That is a disclosed deviation that could not
  have been tuned (`runs/RBT-99/readout-adversary/READOUT-ADVERSARY.md` F11).

**The observed paired effect is smaller than that.** It is **+0.371 [+0.162, +0.581]**, 10/10
[S7f], about 54% of the arithmetic. Against the registered null, on the seven seeds where the cull
did not empty a fauna, it is +0.315 [+0.161, +0.469], 7/7 (`runs/RBT-99/REPORT.md`, headline table).
The RBT-99 adversary's reading at this end is: "all of the paired effect, and more, to the kJ gap"
(F2).

**The insolvent end (post hoc, this paper).** Lesson 7 postdates C2's ruling, and the merged report
quotes only the alive end. This paper applies the bracket to C2 after the fact:
- The unchanged designed gait at 0.08 earns **−0.140 to +0.092**. That is below the 0.25 basal cost
  on every seed, and below 0 on 9/10 [S11d] (the adversary's figure, `probe_readout.txt` P2).
- Scored as the extinct population that implies, the prediction is **+0.631 [+0.577, +0.684]**
  [S11b].
- **So C2's bracket is +0.63 to +0.69, and the observed +0.37 lies below both ends.**
- The residual against the insolvent end is **−0.260 [−0.448, −0.071]**, 2/10 [S11c]. So **C2's
  non-arithmetic part resolves toward the designed body at both ends of the bracket**. The "more"
  in "all of it, and more" is the designed body beating its own unchanged arithmetic.
- Unlike C3, the insolvent end is the *smaller* prediction here. On 9/10 seeds an unchanged designed
  fauna at 0.08 earns less than nothing, and extinction scores 0.
- The re-derivation takes the base designed fauna's income from the adversary's committed P2 table.
  That is **recovery-window** income, not a pre-onset quantity as lesson 3 frames the arithmetic.
  It changes no sentence of the report, and enters no verdict.

**The residual favours the designed body, on a scale nobody registered.** Net of its own price, each
body recovered part of its loss:
- the co-evolved body **+0.207 [+0.151, +0.262]** (79% of its price);
- the designed body **+0.524 [+0.362, +0.687]** (55%).

In absolute income the designed body recovered more, **−0.318 [−0.498, −0.138]** [S8]. As a share of
price the co-evolved body recovered more, +0.29 [−0.02, +0.61], which is unresolved
(`runs/RBT-99/readout-adversary/READOUT-ADVERSARY.md` F2).

Each net carries its conditioning (`runs/RBT-99/REPORT.md`, "Both nets"):
- the designed net is "survivor-conditioned on the 7 seeds where it survived; pinned by extinction
  on 3";
- the co-evolved net is "a survivors' lifetime mean, at low turnover".

The merged report's conclusion: "Neither scale was registered. **Neither body can be said to have
adapted better.**"

**The sentence** (`runs/RBT-99/REPORT.md`, headline, the adversary's F2 text): "The paired effect is
therefore the co-evolved body's cheapness before the event, which is C2's claim. It is not a
difference in how the two bodies responded. At an unchanged gait the designed fauna would earn below
basal on every seed; it stayed solvent on 6/10 seeds only by turnover (3.9–6.7× its baseline's
deaths) and went extinct on 3."

### 3.3 C3, scarce food: inside the bracket

**The arithmetic.** Halving the items halves every body's gross food and leaves its work bill where
it was.
- In the baselines' own pre-onset seasons [T−40, T), the designed body ate 1.22–1.50 items a season
  against the co-evolved body's 1.02–1.35.
- So the halving takes more from the designed body: a price of **0.697** against **0.576**
  (`runs/RBT-100/score.txt` §1).
- At an unchanged gait the designed season net falls to +0.08 to +0.18, **below basal on 10/10
  seeds**. The co-evolved net falls to +0.29 to +0.59, **above basal on 10/10** (same).
- The per-seed values were computed after the arms, from pre-onset data only. The form was
  registered before any arm (`runs/RBT-100/REPORT.md` §3).

**Linearity** cannot be tested before T, where alive is 60 and the items are 12 throughout. It was
checked over the first 1 to 10 seasons after T, before selection can act. Gross food per survivor,
event ÷ baseline, over [T, T+3) is **0.488** (co-evolved) and **0.497** (designed). Per seed the
designed values run 0.355–0.583 (`runs/RBT-100/readout-adversary/probe_readout.txt` P2).

**The bracket.**
- Two unchanged populations that stay alive predict **+0.121 [+0.066, +0.176]** [S12]. Other pre-T
  windows, an axis-scale correction and an empirical density response give +0.113 to +0.146
  (`probe_readout.txt` P2).
- The unchanged designed fauna, scored as the extinct population its own arithmetic implies,
  predicts **+0.316 [+0.242, +0.390]** [S15].
- The observed **+0.138 [+0.006, +0.271]**, 8/10 [S13f], sits between them.
- Against the alive end the residual is **+0.017 [−0.092, +0.127]**. Against the insolvent end it is
  −0.178 [−0.292, −0.065]: "the designed fauna did better than an unchanged, insolvent one"
  (`runs/RBT-100/REPORT.md` §3).

**Against the registered null the paired effect does not resolve.** It is **+0.106 [−0.045,
+0.256]**, 7/10 [S13n] (`runs/RBT-100/REPORT.md` §2). The C3 null is price-blind: R-cull is +0.031
co-evolved and −0.002 designed (same).

**The residual splits by extinction.** It is +0.090 on the five seeds where the designed fauna went
extinct, and −0.056 on the five where it survived (`runs/RBT-100/REPORT.md` §3). The extinct seeds
carry 82% of the paired effect (same, headline and §2).

The lower bound of the paired effect depends on how extinct seasons are coded:
- dropped: +0.061 [−0.022, +0.143], unresolved;
- coded at −0.25: +0.190 (`runs/RBT-100/REPORT.md` §2).

The class is A under all four codings.

**Nets side by side.** Co-evolved **+0.131** (23% of its price recovered), designed **+0.114** (16%).
The difference, +0.017, "is unresolved; this design could detect only a difference above ≈ 0.15"
[S17] (`runs/RBT-100/REPORT.md` §3).

**The sentence** (`runs/RBT-100/REPORT.md`, headline): "The arithmetic therefore brackets the paired
effect, +0.12 to +0.32, without deciding whether either body responded better. The design could not
have detected a response difference below about 0.15."

### 3.4 C4, flat terrain: the falsifier fires, wholly by the furniture's arithmetic on the arena predictors (reported apart)

C4 is the one challenge the robots can perceive with the wiring they have. The protocol requires it
to be reported apart from C1–C3 and never pooled with them (`docs/held-out-challenges.md` §2 C4, §14
item 7). Nothing in this section enters §2's or §4's statements about C1–C3.

**The registered verdict: class C.** The owner's words for it are "the designed body wins on the
held-out challenge" (protocol §9).
- R-body in the recovery window is **−0.310 [−0.481, −0.139]**, negative on 9/10, with r = 0.171
  and a sign-guard margin of 1 seed. D, E1 and E2 are each 0/10 (`runs/RBT-101/REPORT.md`, headline).
- In the report's words, the designed body won by gaining more: "the co-evolved body **gained less;
  it did not lose**".
- On open ground **both bodies earned more**. Against the no-event control the designed body gained
  **+0.635 [+0.532, +0.739]**, 10/10, and the co-evolved body **+0.177 [+0.076, +0.278]**, 9/10 (same,
  §3).

**The paired contrast.**
- Event − base is **−0.458 [−0.596, −0.320]**, 0/10 [S18f].
- Event − null is **−0.472 [−0.585, −0.359]**. That is "≡ event − base on the six k = 0/0 seeds; the
  null could absorb ~0.5%" [S19] (`runs/RBT-101/REPORT.md`, headline). Flat ground killed nobody, so
  the registered excess-deaths null has almost no channel here (same, §3).
- cull20, the turnover reference, moves neither body resolvably.

**The arithmetic, in the axis's own setting (lesson 8; all arena predictors post hoc).**
- **The registered prior** was a solo probe of the season-300 bests (`runs/RBT-101/flat_probe.txt`,
  committed before the arms). It predicts −0.325 [S28], with residual **−0.133 [−0.486, +0.219]**,
  unresolved [S29], and does not predict per seed (r −0.04). With the registered half-discount for
  group foraging (Amendment 2) it predicts −0.163 [S30] and leaves **−0.296 [−0.511, −0.080], resolved
  toward the designed body** [S31] (`runs/RBT-101/REPORT.md` §4). Under the registered prior as
  registered, the flip is not wholly arithmetic, and the part beyond it favours the designed body.
- **The readout adversary's arena predictors** use unchanged gaits, four to a group, flat against
  random ground. They all predict *more* than was observed (same, §4, table):
  - **Z10:** the same pre-T individuals, paired by name, over [T, T+10): **−0.630 [−0.759, −0.501]**
    [S21];
  - **Z:** season T replayed: −0.701, residual +0.243 [−0.007, +0.493], 7/10, unresolved;
  - **the simulated C0 cohort:** −0.806 [S27].
- **The refund.** In the arena the furniture's refund to the wheels is about +0.94 a season, against
  +0.14 to +0.22 for the co-evolved gaits.

The report's reading (headline), on the arena predictors: "So **the falsifier fires wholly by the
arithmetic of the furniture**. The pre-onset lead was the clutter's tax on wheels." **So the direction
of C4's non-arithmetic part depends on the predictor**: toward the designed body on the registered
prior with its registered discount, toward the co-evolved body on the post hoc arena predictors. The
20:40 ruling adopts the arena reading; this paper follows it and prints both.

**Beyond the arithmetic (post hoc).** The contrast moved back toward the co-evolved body.
- **Against Z10:** **+0.172 [+0.055, +0.289]**, 8/10 [S22].
- **Same-season split at T+110:** the refund is the base population, flat − random; the response is
  the shift population − the base population, both on flat. The paired refund is **−0.721 [−0.885,
  −0.558]**, 0/10 [S25], and the paired response is **+0.272 [+0.053, +0.491]**, 8/10 [S26]
  (`runs/RBT-101/REPORT.md` §4; `readout-adversary/probe_refund.txt`).
  - The simulated total, −0.450, matches the observed −0.458 [S24].
- **Per fauna, against Z10,** "the co-evolved body sits on its arithmetic" (+0.016 [−0.095,
  +0.128]). The non-arithmetic part is on the designed side (−0.156 [−0.285, −0.026]).
- **The designed population born after the shift foraged worse** than the baseline's contemporaneous
  population in one simulated season (T+110, post hoc). Its response is −0.222 [−0.445, +0.002], 2/10,
  on flat ground, which does not resolve, and −0.174 [−0.312, −0.036] on random ground, which does
  [S27b, S27c]: **resolved on random ground only**. The report says "on flat and on random ground
  alike". **No mechanism is claimed.**

The coordinator's 20:40 ruling on RBT-101 (Chaotic) is binding here. These are "the first resolved
non-arithmetic effects in phase 2. They are post hoc (the adversary's predictor, chosen after the
arms) … **a hypothesis for RBT-107 to confirm prospectively, not a finding.**" In this paper's own
voice: C2's residual, −0.318, resolved earlier (RBT-99 closed at 19:10), toward the designed body.
What C4 carries is **the first resolved residual in the co-evolved body's favour, on a post hoc
predictor**.

**Re-wiring, the one C4-specific readout: NO CHANGE SEEN on both faunas.** It was pre-registered with
its own positive control.
- It is blind below about half of the installable co-evolved survivors, and below about a fifth of
  the designed ones.
- "No new use of a posture sensor is shown, and **no re-adaptation is claimed**"
  (`runs/RBT-101/REPORT.md`, headline).

**Lessons 4–6 as applied** (`runs/RBT-101/REPORT.md` §1, §6):
- Recovery time is not read.
- Survival is uninformative: alive is 60 in every season of every arm.
- The L carriage row is not scored (UNVALIDATED, V3).

**Seed 806** carries the drift flag. Without it the mean is −0.270, 8/9, still C (post hoc check, not
a re-pick; same, §6).

**The sentence** (`runs/RBT-101/REPORT.md` §9): "The designed body won by gaining more; the
co-evolved body gained less and did not lose. It is not shown that either body adapted. Beyond the
arithmetic the contrast moved back toward the co-evolved body (post hoc, +0.17 to +0.27), because the
designed population born after the shift foraged worse."

---

## 4. Response: what the residuals show, and in which direction

Put the residuals side by side, each read against its own design's power. C4 is kept in its own
rows.

| challenge | what the residual is | value | resolves? | registered? | minimum detectable at n = 10, 80% power |
|---|---|---|---|---|---|
| C1 | the paired effect itself (no arithmetic) | +0.032 [−0.041, +0.105] | no | yes (the contrast) | 0.101 [S5] |
| C2 | paired − arithmetic, alive end (= net co-evolved − net designed) | −0.318 [−0.498, −0.138] | **yes, toward the designed body**, in absolute income | the price and the net were adopted in Amendment 1 (Amendment 2 gated `price.txt`, which was computed late, from pre-onset seasons); the absolute-income scale of the net was not registered | 0.250 [S10] |
| C2 | paired − arithmetic, insolvent end | −0.260 [−0.448, −0.071] [S11c] | **yes, toward the designed body** | **post hoc, this paper** | — |
| C2 | the same, as a share of price | +0.29 [−0.02, +0.61] | no | not registered | — |
| C3 | paired − arithmetic, alive end | +0.017 [−0.092, +0.127] | no | the form was registered; per-seed values after the arms | 0.152 [S17] |
| C3 | paired − arithmetic, insolvent end | −0.178 [−0.292, −0.065] | yes: the designed fauna did better than an unchanged, insolvent one | lesson 7, 20:06 | — |
| **C4 (apart)** | paired − registered prior (solo probe), undiscounted | −0.133 [−0.486, +0.219] [S29] | no | yes, the registered prior | — |
| **C4 (apart)** | paired − registered prior, with its registered half-discount | −0.296 [−0.511, −0.080], 2/10 [S31] | **yes, toward the designed body** | yes (Amendment 2) | — |
| **C4 (apart)** | paired − arena arithmetic (Z10) | +0.172 [+0.055, +0.289], 8/10 | **yes, toward the co-evolved body** | **post hoc**, the readout adversary's predictor | 0.163 [S23] |
| **C4 (apart)** | paired − arena arithmetic (Z) | +0.243 [−0.007, +0.493], 7/10 | no | **post hoc** | — |
| **C4 (apart)** | same-season response, paired (refund −0.721 [S25]) | +0.272 [+0.053, +0.491], 8/10 [S26] | **yes, toward the co-evolved body** | **post hoc** | — |

**How the MDE is computed.** Each residual's own between-seed sd, in the RBT-100 adversary's form,
(t₀.₉₇₅ + t₀.₈₀) × sd ⁄ √n (`runs/RBT-100/readout-adversary/probe_readout.txt` P4, which gives 0.152
for C3). `docs/paper-9/rederive.txt` reproduces that figure and applies the same form to C1, C2 and
C4.

**What the table shows:**

- **No registered residual resolves in the co-evolved body's favour, and the one registered C4
  residual that resolves runs toward the designed body** (−0.296, the registered prior with its
  registered discount). C1's and C3's (alive end) do not resolve at all. C3's design could not have seen one smaller than about 0.15, which is **1.3
  times the whole alive-end arithmetic effect** (`runs/RBT-100/readout-adversary/READOUT-ADVERSARY.md`
  F4).
- **The residuals that do resolve point both ways, and none of them is a registered response
  readout.**
  - C2's resolves toward the designed body at both ends of its bracket, in absolute income. That
    scale was unregistered, and the net is survivor-conditioned on seven seeds and pinned by
    extinction on three. The merged report's reading is that neither body can be said to have
    adapted better.
  - C4's resolves toward the co-evolved body on the post hoc arena predictors, and toward the
    designed body on the registered prior with its registered discount. Its direction depends on the
    predictor. The 20:40 ruling adopts the arena reading and calls it a hypothesis, not a finding.
  - Both locate the difference between the bodies' residuals mainly on the designed side, yet they
    push the contrast in opposite directions. In C2 both bodies beat their unchanged arithmetic, and
    the designed body beat it by more in absolute income. In C4 the co-evolved body sat on its
    arithmetic, and the designed population born after the shift foraged worse. No mechanism is
    claimed for either.
  - **This paper builds no single narrative from them, and in particular not "the designed body
    declines after an event"**: C2 is a counter-example, on its own scale.
- **"Not shown" is not "equal".** None of these designs can show equivalence. C1's equivalence form
  fails by 0.005, and the MDEs run from 0.10 to 0.25.

**How this revises the coordinator's summary** (RBT-107, 20:28 UTC, Chaotic): "every event effect so
far lies inside its unchanged-population arithmetic; no response difference is shown, at an MDE of
≈ 0.15 (n = 10)". That was written before C4 closed. As the evidence now stands:
- **C1–C3.** No registered response difference is shown, at MDEs of about 0.10 (C1), 0.15 (C3) and
  0.25 (C2).
- **C2's effect lies below both ends of its bracket.** The alive-end reading, "all … and more", is
  the RBT-99 adversary's. The insolvent end is this paper's post hoc addition.
- **C4 carries the first resolved residual in the co-evolved body's favour, on a post hoc
  predictor.** It is not the first resolved non-arithmetic residual: C2's resolved first, toward the
  designed body.
- **Which residuals resolve, against which predictions.** C2's residual resolves against both ends of its bracket, toward the designed body. C4's resolves toward the co-evolved body against two of the three post hoc arena predictors (Z10 and the same-season split; not Z), and toward the designed body against its registered prior with the registered discount. Only C2's meets "resolves against every end of its prediction". C3's insolvent-end residual (−0.178) resolves toward the designed body, but C3's
  alive-end residual does not, so under lesson 7 C3 is undecided.

> **[PENDING: RBT-110.]** RBT-110 was pre-registered at 20:45 and is running. It applies C4's
> same-season refund/response split, out of sample, to C1–C3, and adds C4's missing cull20 null.
> Whether the C4 pattern generalises decides how this section ends. This section is rewritten from
> RBT-110's merged report, in its post-adversary wording. Until then, no number from it is used.

---

## 5. What C2 and C3 did establish: survivorship of the co-evolved population, by income

**C2 and C3 were registered as budget challenges.** Their claim is not the owner's contest but
"survivorship of the co-evolved population at an economic boundary the designed body's budget is not
expected to survive" (protocol §2, C2; C3 "as C2, … here the bootstrap line for food"). On those terms
both are answered by income. Both answers agree with what the pre-onset gait's arithmetic implies.

**C2.**
- The co-evolved recovery income was +0.79 to +1.22 on 10/10 seeds, never near basal.
- Its cost against the control does not resolve (−0.055 [−0.123, +0.013]). Against the registered
  null it resolves and is small (−0.074 [−0.117, −0.031]) (`runs/RBT-99/REPORT.md` §5, headline
  table).
- Its unchanged-gait income at 0.08 would have been +0.53 to +1.00, above basal on every seed
  (`runs/RBT-99/readout-adversary/READOUT-ADVERSARY.md` F2).
- The designed fauna failed D's test on 4/10 seeds, went extinct on 3, and stayed solvent on 6/10
  "only by turnover".

**C3.** "At half the food the established co-evolved population paid its way by income on every
seed, as its pre-onset gait's arithmetic says it would" (`runs/RBT-100/REPORT.md` §4).
- Survivors' own net was +0.50 to +0.66.
- The starved share of each season's runners was 1.2–2.5% on the shift arm, against 0.7–1.5% on the
  base.
- **Random co-evolved founders at six items failed on 7/10 seeds.** This was pre-registered. Seed 7
  is borderline: 8 alive and rising at the season-59 cut.
- The founders **held on 3/10 seeds** (804, 1, 4), so no general "bootstrap line" is established
  (`runs/RBT-100/REPORT.md` §6).
- The designed fauna went extinct on 5/10 seeds and fell below the floor of 12 on 2 more. On 3 seeds
  (804, 807, 7) it "stayed solvent by clear margins, against an arithmetic that called an unchanged
  gait insolvent on all 10".

**Two cautions travel with these.**
- **Survival read from alive = 60 carries no information** (§6, lesson 5). The co-evolved claims rest
  on income. The informative survival facts are the ones that cannot refill: designed extinction,
  and founders6.
- **Class D was not reached on either challenge,** so neither is a class-D result. C2's D test fired
  on 4/10 seeds and C3's on 7/10, both below the 8/10 guard. On the seeds where D did not fire, the
  class-A lead is not over a bankrupt comparator (`runs/RBT-100/REPORT.md`, "D's test, per seed").

**On the mean, neither body lost its full unchanged-gait price in C2 or C3, and the designed fauna
stayed partly solvent.** Per seed it varies: in C3 the designed share of price recovered runs −0.16
to +0.43 (`runs/RBT-100/score.txt` §1). Both bodies' nets resolve above 0 in both challenges:
- C2: co-evolved +0.207, designed +0.524 (`runs/RBT-99/REPORT.md`, "Both nets");
- C3: co-evolved +0.131, designed +0.114 (`runs/RBT-100/score.txt` §1).

Whether that is sorting (on kJ, or on gait) or survivor-conditioning of the lifetime mean, the
committed tables do not separate (`runs/RBT-99/REPORT.md` §8; `runs/RBT-100/REPORT.md` §6).

---

## 6. The instrument lessons

**Who found them.** Every one of these was found by someone other than the designer: a readout
adversary, and then a coordinator ruling that carried it to the challenges not yet read.
- C3's designer applied lessons 1–6 before its readout adversary saw the report. The adversary still
  caught two lapses (RBT-100 F8, F10), and found the seventh lesson.
- C4's adversary found the eighth.

**Why they are the reusable result.** Each is a rule a future event readout can follow before it
runs. Two of the failures they caught came from this ecology's axis and refill: lesson 4 (a
lifetime-mean axis with lag-1 autocorrelation 0.69) and lesson 5 (within-season refill). The rules
travel; those two failures were this ecology's.

The catalogue form is paper 7's. For each lesson: what the instrument said, why it was wrong, what
caught it, and the rule. Where "what the readout said" quotes a designer's Chaotic summary rather
than a committed file, it is marked Chaotic.

| # | lesson | where it bit | what the readout said | what caught it | the rule now |
|---|---|---|---|---|---|
| 1 | **Placebo onsets.** Apply the class rule to the no-event baseline and to fake onsets before reading it on the event. | C1 | class A, read as "the co-evolved body survives crowding and keeps its lead" (designer's summary, RBT-92, 18:11, Chaotic) | RBT-92 readout adversary F2 (A on the base; 23/25 placebo onsets) | "Every challenge readout … must report the class on the no-event baseline and on placebo onsets beside the event arm" (coordinator, 18:45 on RBT-92, Chaotic) |
| 2 | **Paired event − base, and event − null.** The only readout that speaks to the event is the per-seed paired contrast, against the no-event baseline and against the random-cull null. | C1, C2 | the designed body's crowding cost "resolves", read against the control only | RBT-92 adversary F3: against the registered null it is −0.037 [−0.081, +0.006]; RBT-99 adversary F6 (C2's shift − cull, not printed) | "The paired event − base contrast against the random-cull null is the only readout that speaks to the event" (18:45) |
| 3 | **Arithmetic first.** Compute what the event does to an unchanged population from pre-onset quantities; only the residual can be a response. | C2 | "most of the verdict is the designed body's collapse"; the co-evolved body "got back about 80% of its price", read alone (designer's summary, RBT-99, 18:42, Chaotic) | RBT-99 adversary F2, F3: the price predicts +0.69; the designed body recovered more in absolute terms | coordinator, 19:05 on RBT-99 (Chaotic) |
| 4 | **No recovery claim from d = 0.** A lifetime-mean axis starts every paired difference at 0 and moves slowly (lag-1 autocorrelation 0.69); a 20-season hold starting at T is met before divergence can show. | C1, C2 | "it never left the band on 6 seeds" (RBT-92, 18:11, Chaotic); "returned to the control's band within 180 seasons: 9/10" (RBT-99, 18:42, Chaotic) | RBT-92 adversary F4 (every seed leaves the band; the d = 0 count depends on h, 0/10 at 0.5 SD to 6/10 at 2 SD); RBT-99 adversary F7 | "The registered recovery-time rule cannot return 'none' for a slow divergence. Report its numbers as registered, and make no recovery claims from them" (18:45) |
| 5 | **Survival is uninformative under refill.** Deaths are refilled by births within the season, and `alive` is recorded at season end, so alive = 60 is the ecology's state, not a result. | C1–C4 | "both survive", scored as a hit | RBT-92 adversary F2 (alive = 60 in every season of [T−100, T+200) in all 37 runs; minimum window income 0.69 against 0.25) | "Survival is uninformative in this ecology" (18:45). The survival facts that count are the non-refilling ones (the RBT-99 designer, 18:46, Chaotic; RBT-100 adversary F8): extinction, founders that fail to bootstrap, income below basal |
| 6 | **UNVALIDATED means unread.** A readout whose validation failed enters no sentence, including a prediction scored "right" and a number printed "for the record". | C1–C4 | carriage L scored "right"; designed Lc printed "not read" | RBT-92 adversary F8; RBT-99 F12; RBT-100 F10 | V3 failed by design: a same-season refill hides the cull from `alive`. Its proposed fix repairs only the manipulation half; validating L needs an effect L must register, such as a cull of whole lineages (RBT-92 §1) |
| 7 | **The bracket.** When the arithmetic says an unchanged population is insolvent, lesson 3's prediction is two numbers, alive and extinct, and the residual is read against both. | C3; applied to C2 post hoc by this paper (§3.2) | "arithmetic, and nothing beyond it"; "not a difference in how the two bodies responded"; "a similar part of its price" | RBT-100 adversary F2, F4 | coordinator, 20:06 on RBT-100 (Chaotic), adopted programme-wide at the 20:14 close |
| 8 | **Arithmetic in the axis's own setting; split refund from response at one season.** Make the unchanged-population prediction in the setting the axis is measured in (the arena, groups of four, the population at T), not in a solo probe of the best. Where the harness allows, split the change at one season into refund (the base population on the new world) and response (the event population against the base population on the same world). | C4 | "the obstacles were about twice the tax on wheels … **No response beyond the unchanged-gait arithmetic is shown**", from a solo probe that predicted −0.325 (designer's summary, RBT-101, 19:38, Chaotic) | RBT-101 readout adversary F2 (the post hoc arena predictors give −0.63 to −0.81; the refund is 4–7× on wheels: That is 4–7×, not "about twice"; the post hoc residual runs the other way) | coordinator, 20:40 on RBT-101 (Chaotic): "That split is a common garden in miniature." **[PENDING: RBT-110's out-of-sample test on C1–C3]** |

Six smaller rules came out of the same rounds, and bind the same readouts:

- **Judge a paired contrast on the paired A/A scale.** The per-fauna A/A-like RMS (0.077) is the
  wrong scale for R-body. The paired one is 0.071–0.108, pooled 0.091, on C3's arms
  (`runs/RBT-100/readout-adversary/READOUT-ADVERSARY.md` F7), and 0.108–0.123 on C4's
  (`runs/RBT-101/readout-adversary/probe_readout.txt` P4).
- **Jitter the sign guard, and report the rate.** A count met with zero margin can be close to a coin
  flip on replication:
  - C3's paired 8/10 keeps ≥ 8/10 in only 46–49% of draws (RBT-100 F7);
  - C1's class returned F in roughly 1 in 10 to 1 in 5 draws (RBT-92 F6).
- **Label outcome-defined subsets post hoc**, including the registered D partition, and show the
  alternatives (RBT-99 F5).
- **Show the extinction coding's sensitivity** beside a registered coding that sets an interval's
  lower bound (RBT-100 F5).
- **Do not borrow a class's sentence for a class that missed its guard.** "Outlasts a bankrupt
  comparator" is D's sentence. D missed on C3, and its three non-D seeds were not near misses (RBT-100
  F6).
- **An upper bound certifies only one direction.** "Above basal" from an upper bound certifies
  nothing (RBT-100 F8).

**What they have in common is paper 7's class, in a new place.** Each is a registered readout that
computed correctly and answered a different question from the one its sentence asked:

| readout | the question it answered | how it was read |
|---|---|---|
| the class rule | is there a lead? | who withstood the event? |
| the recovery rule | had they diverged yet? | had they recovered? |
| `alive` | did the economy refill the slots? | did they survive? |
| the paired contrast | how did the two bodies' pre-onset differences meet the event? | who responded better? |
| C4's solo probe | what does open ground give one best alone? | what does it give a population in the arena? |

---

## 7. The calibration beside it

**The arena's A/A null (RBT-96).** Two runs identical except for the holistic RNG stream, on four
seeds, differ by an RMS of **0.128** in the arena's final-fifth score.
- That is three times the designer's prediction.
- At n = 4 the resulting 95% null half-width is **h = 0.178**, so the programme's ±0.10 arena rule
  was unsound at n = 4 (`runs/RBT-96/REPORT.md` §3–§4).
- Most of the spread is one seed's discovery event, "the null behaving as a search". The designer
  offers that reading as "a description, not a result" (same, §3).
- It is a different instrument, the arena rather than the ecology. It is cited here as the
  programme's warning that an assumed noise figure can be three times too small.

**The ecology's A/A-like spread, from the committed arms.** RBT-105's founder-sharing replicates had
not merged when C1–C4 were read. So each readout adversary built an A/A-like reference from the
committed cull contrasts, which diverge one fauna from the baseline at T by an intervention with an
expected effect near 0 on the mean. Each figure below belongs to its own ticket:

| ticket | per fauna | paired R-body scale | source |
|---|---|---|---|
| RBT-92 (C1) | 0.090 (k ≤ 3) to 0.100 (all k > 0); cull20 0.077 | cull − base **0.113**; cull20 − base 0.108; shift − base 0.102 | `runs/RBT-92/readout-adversary/READOUT-ADVERSARY.md` F5 |
| RBT-99 (C2) | 0.077–0.086 | cull20 − base 0.108 | `runs/RBT-99/readout-adversary/READOUT-ADVERSARY.md` F9 |
| RBT-100 (C3) | 0.051–0.101 | cull − base **0.071**; cull20 − base 0.108; **pooled 0.091** | `runs/RBT-100/readout-adversary/probe_readout.txt` P5 |
| RBT-101 (C4) | 0.077 (cull20) | cull20 − base 0.108; the four real culls 0.123 | `runs/RBT-101/readout-adversary/probe_readout.txt` P4 |

So the paired scale runs **0.071–0.123** across the four tickets.

The between-seed t intervals in this paper carry run-to-run noise inside them by construction, so
they do not depend on this figure. What does depend on it is any reading of a single seed, and none
is made.

**RBT-108 (the arena A/A at n = 16).** **[PENDING: RBT-108 merge. Cite its REPORT and readout here,
with the extended RMS and h, and say whether RBT-96's 0.128 and the "9 seeds for ±0.10" line
stand.]**

**RBT-105 (the ecology A/A, `runs/RBT-105/aa_spread.txt`).** **[PENDING: RBT-105 merge. Quote its
recovery-window per-fauna RMS against the per-fauna figures in the table above.]** The adversaries
ruled in advance what it can and cannot move:
- it is holistic-only: the designed fauna is byte-identical across its replicates by construction;
- it diverges from season 0, so it is an upper bound for a challenge arm's recovery window;
- **it cannot move any class in C1–C3, or C2's paired sign** (RBT-92 F5 and RBT-100 F7 for the class;
  RBT-99 F9 for C2's paired sign). C3's paired 8/10 is already a coin flip under jitter (RBT-100 F7);
- C4's paired contrast is 12 SE of an A/A mean, so C4's reading does not wait on it
  (`runs/RBT-101/REPORT.md`, provenance).

If its RMS is much larger than 0.2 per fauna, the between-seed intervals stand, but the per-seed
tables should not be printed (RBT-92 F5).

---

## 8. What would answer the question

**The question the challenge set was built for is not the one it answered.** It answered two
questions:
- *Does a standing lead survive a change?* Yes, on these seeds, on C1–C3.
- *Does a cheap gait outlast a dear one?* Yes, by income, on C2 and C3.

C4 answered a third: *how much was each body being impeded by the furniture?* The wheels were
impeded several times more than the evolved gaits.

All three are statements about the bodies before the event. The owner's question, whether the
co-evolved body *holds up* better, needs a readout of response. The challenge set's registered
readouts could not supply one, for three reasons this paper can state exactly.

**Depth.** Over the transient plus recovery windows, [T, T+160), a lineage has about five
reproduction events (`runs/RBT-92/baseline_depth.txt`). "Re-adapts" at five events is sorting of
standing variation at most (protocol §10), and C4's re-wiring readout saw no change at that depth, at its resolution: blind below about half of
the installable co-evolved survivors and a fifth of the designed ones.

RBT-107, filed at 19:35 with the owner's budget, proposes to extend the C4 event arms from their
checkpoints to a post-event window of roughly twenty events. **[PENDING: cite `runs/RBT-107/depth.txt`
on integration. The design draft measures 2.7–3.3 reproduction events per 100 seasons after T, and
proposes scoring at T + 800, about 22 events (RBT-107, designer's comment 19:55, Chaotic).]**

**Arithmetic.** A population readout carries the event's arithmetic. On C2 and C3, and on C4 (apart), that
arithmetic was as large as or larger than any residual the design could see. On C4 the post hoc arena predictors, not
the registered solo probe, are the reading the ruling adopted (lesson 8).

RBT-107's primary readout is a **common garden**:
- the fauna alive late in the event, baseline and cull20 arms, are all scored on the same fixed
  worlds, so the event's arithmetic cancels by construction;
- its positive control is C2 in the same garden, where both populations are priced at 0.08 (RBT-107,
  designer's comment 19:55; coordinator 20:28; both Chaotic).

C4's same-season split is that garden in miniature (lesson 8). RBT-110 is testing whether its
pattern holds on C1–C3. **[PENDING: RBT-110.]**

**Power.** At n = 10 the smallest effect the ecology could detect at 80% power was about 0.10 on C1,
0.15 on C3, 0.16 on C4's post hoc residual and 0.25 on C2 (§4). The table below gives the MDE at
larger n for each of the spreads this programme has measured, taking the n = 10 sd as the planning
value [P1–P5].

| planning sd | source | n = 10 | n = 16 | n = 20 | n = 30 | n = 40 | n for MDE 0.10 | n for MDE 0.05 |
|---|---|---|---|---|---|---|---|---|
| 0.091 | ecology paired A/A-like RMS, C3's arms [P1] | 0.091 | 0.068 | 0.060 | 0.048 | 0.041 | 9 | 28 |
| 0.101 | C1 paired event − base [P2] | 0.101 | 0.076 | 0.067 | 0.054 | 0.046 | 11 | 35 |
| 0.153 | C3 residual [P4] | 0.152 | 0.115 | 0.101 | 0.081 | 0.070 | 21 | 76 |
| 0.251 | C2 residual [P3] | 0.250 | 0.188 | 0.166 | 0.133 | 0.114 | 52 | 201 |
| 0.128 | arena A/A RMS, RBT-96 [P5] | 0.127 | 0.096 | 0.085 | 0.068 | 0.058 | 15 | 54 |

MDE = (t₀.₉₇₅,n−1 + t₀.₈₀,n−1) × sd ⁄ √n, two-sided 5%, 80% power (`docs/paper-9/rederive.py`).

Three readings of it:

1. **A garden near the ecology's paired A/A spread would reach the protocol's threshold.** If a
   common garden removes the arithmetic and leaves a spread near 0.09, ten seeds detect a response
   difference of about 0.09, and sixteen about 0.07. That is at the protocol's smallest effect worth
   claiming, 0.10 (protocol §7).
   - This is conditional. No garden readout's between-seed spread has been measured on the event
     arms.
   - A garden that inherits extinction heterogeneity, as C2 and C3 did, would sit nearer the lower
     rows.
2. **A readout with the challenges' own residual spread needs many more seeds.** With C3's spread,
   n ≈ 21 reaches 0.10; with C2's, n ≈ 52. At ten seeds, the readout the challenge set used could
   not have seen a response difference the size of its own C3 arithmetic.
3. **Halving the MDE costs three to four times the seeds** (the rows give ratios of 3.1–3.9). A 0.05
   response difference is out of reach of any design in the programme's current budget, unless the
   garden's spread is well below the A/A-like 0.09.

**RBT-107's instructions.** The coordinator's 20:28 instruction (Chaotic) is the same point in
operational form: state the garden readout's MDE at n = 10, and if n = 10 cannot see an effect of the
size that would matter (≤ 0.10), propose more seeds as a costed option rather than dilute the design.
The coordinator's 20:40 ruling on RBT-101 adds that C4's post hoc residual is RBT-107's hypothesis to
confirm prospectively. **[PENDING: RBT-107's registered MDE and seed count, when its pre-registration
clears its adversary.]**

**[PENDING: RBT-110.]** RBT-110 was pre-registered at 20:45 and is running. It applies C4's
refund/response split out of sample to C1–C3, and it adds C4's missing cull20 null.
- If the pattern generalises, a response readout may already be available at five events on the
  committed arms.
- If it does not, C4's post hoc residual stands alone, beside C2's residual in the other direction.

This paragraph is rewritten from RBT-110's merged report.

**What would change this paper's answer.** A pre-registered readout that resolves a response
difference, in either direction, larger than the ecology's paired A/A spread, with a pre-registered
null: a common garden at twenty events, or RBT-110's split on C1–C3. C4's post hoc residual is the
first resolved sign of a difference in the co-evolved body's favour; C2's, on an unregistered scale,
runs the other way. Nothing registered in C1–C4 yet shows one.

---

## 9. Limitations

- **Ten founding populations, one economy, one onset per seed.** Every class, contrast and residual
  here is for RBT-90 part 2's ten seeds, at T = 352–382, in the dense foraging baseline. None
  replicates RBT-28's, RBT-71's or RBT-84's populations (`runs/RBT-92/REPORT.md` §7 item 12).
- **The null was weak.**
  - On C1 the registered cull removed 0–3 co-evolved robots (k = 0 on 6/10 seeds), so the turnover
    guard was scored on n = 4.
  - On C2 the designed k reached or exceeded 60 on three seeds, and the null was extinction there.
  - On C3 the turnover guard was declared not interpretable in advance.
  - On C4, k was 0/0 on six seeds, so event − null ≡ event − base there.
  - Sources: `runs/RBT-92/REPORT.md` §3; `runs/RBT-99/REPORT.md` §3; `runs/RBT-100/REPORT.md` §2;
    `runs/RBT-101/REPORT.md` §3. cull20 is the turnover reference throughout.
- **Seed 806 carries an onset-drift flag**: its baseline deaths over [T, T+10) were 54, against a
  period mean of 34.3. It is read with the flag in every challenge (`runs/RBT-92/readout.txt`;
  `runs/RBT-99/REPORT.md` §5; `runs/RBT-100/REPORT.md` §4; `runs/RBT-101/REPORT.md` §6).
- **The arithmetic was computed after the arms,** from pre-onset data, on C2 and C3. It is per
  population and linear. On C3 its linearity was checked over the first 1 to 10 post-onset seasons.
  Per seed, the designed response departs from 0.5 by −0.145 to +0.083
  (`runs/RBT-100/readout-adversary/probe_readout.txt` P2).
- **On C4 the arena arithmetic and both residuals are post hoc,** the readout adversary's predictors,
  chosen after the arms. The registered prior, the solo probe, predicted the direction and not the
  size or the per-seed values (`runs/RBT-101/REPORT.md` §8 item 7).
- **C2's insolvent end and its residual (§3.2) are this paper's own post hoc re-derivation.** They
  use recovery-window base income, and change no merged sentence.
- **The ecology A/A is pending** (§7). The paired intervals do not depend on it. Per-seed readings
  would, and none are made.
- **Carriage and recovery are unread** throughout (lessons 4, 6), so nothing here says which lineages
  carried what through any event. C4's re-wiring readout is structural, not functional
  (`runs/RBT-101/REPORT.md` §8 item 3).
- **RBT-110 is pending.** The paper's synthesis of response waits on it.

---

## 10. Conclusion

**C1–C3.** On three held-out challenges the registered rule said the co-evolved body wins, and it
says the same with no challenge. Read the only way that speaks to the event, as a paired contrast
against the unchanged course of the same population:
- crowding did nothing the design could resolve to either body's lead;
- dearer work widened the lead by less than the price of the designed body's costlier gait;
- scarce food widened it by an amount its arithmetic brackets on both sides, and not resolvably
  against its null.

The co-evolved population paid its way through dearer work and half the food, by income, on every
seed. That is what C2 and C3 set out to test, and what that gait's pre-onset arithmetic implies. No
registered response difference is shown on C1–C3, at the effect sizes the design could see.

**C4.** On the one perceivable challenge the falsifier fired: the designed body wins on open ground.
On the post hoc arena arithmetic it won wholly by the
furniture's refund to the wheels. The co-evolved lead had been the clutter's tax on
wheels, and the co-evolved body gained less and did not lose.

**The residuals.** Beyond the arithmetic, residuals resolve in opposite directions. C2's residual resolves against both ends of its bracket, toward the designed body. C4's resolves toward the co-evolved body against two of the three post hoc arena predictors (Z10 and the same-season split; not Z), and toward the designed body against its registered prior with the registered discount. C2's is on an unregistered scale; C4's co-evolved-ward residuals are on post hoc predictors.

Whether C4's is a pattern or a single challenge's accident is what RBT-110 is testing now
**[PENDING: RBT-110]**.

**What is still open.** The owner's question, whether a co-evolved body holds up against a novel
challenge better than a designed body with a grafted brain, is still open. This paper says what would
close it:
- depth enough for a response to exist;
- a common garden, so that the event's arithmetic cancels;
- enough seeds that a response of the size worth claiming can be seen.

**What phase 2 leaves to phase 3.** Eight lessons were learned on the way here, each found by someone
asked to attack a readout. Those lessons, and not the four registered classes, are what phase 2
leaves to phase 3.

---

## Sources

Every row cites the committed file its number comes from; `docs/paper-9/rederive.txt` row ids in
brackets. Quotations from Chaotic comments are marked as such in the text.

| Claim | File | Rows |
|---|---|---|
| The protocol: baseline, challenge set, windows, class rule, depth ≈ 2 × seasons ÷ 60 | `docs/held-out-challenges.md` §1–§10 | — |
| Seeds, onsets T = 352–382, seed 806 drift flag | `runs/RBT-92/SEED-RULE.md`, `onset.txt`, `readout.txt` | — |
| cull20 as the turnover reference (Amendment 3) | `runs/RBT-92/PREREGISTRATION.md`; `runs/RBT-92/REPORT.md` §3 | — |
| Depth in [T, T+160): median 5.0; range 3–7 co-evolved, 3.5–6.0 designed | `runs/RBT-92/baseline_depth.txt` | — |
| Baseline R-body before +0.158, recovery +0.148 | `runs/RBT-92/REPORT.md` §2; `runs/RBT-92/readout.txt` | — |
| C1 class A +0.180 [+0.077, +0.284], r 0.104; R-shifts; paired +0.032; designed R-null −0.037 | `runs/RBT-92/REPORT.md`; `runs/RBT-92/readout.txt`; `readout-adversary/probe_readout.txt` P4 | S1–S3, S1f, S3f, S5 |
| C1 class on the base, placebo 23/25, equivalence 0.105; A/A-like RMS; sign-guard jitter; recovery-band exits | `runs/RBT-92/readout-adversary/probe_readout.txt` P3–P6; `READOUT-ADVERSARY.md` F2–F8 | S4 |
| The identical placebo sequence in all four files | `runs/RBT-92/readout-adversary/probe_readout.txt` P3; `runs/RBT-99/placebo.txt`, `runs/RBT-100/placebo.txt`, `runs/RBT-101/placebo.txt` P3; `docs/paper-9/adversary/probe_paper.txt` B (C1–C3, PR #205) | S4, S9, S16, S20 |
| C2 class A +0.519, r 0.183; nets; shift − cull n = 7; headline wording | `runs/RBT-99/REPORT.md` | — |
| C2 price per seed and fauna; kJ 19.0 / 5.2 | `runs/RBT-99/price.txt` | S6, S11 |
| C2 arithmetic +0.689, observed +0.371, residual −0.318, share difference | `runs/RBT-99/score.txt`; `runs/RBT-99/placebo.txt` P4; `runs/RBT-99/readout-adversary/probe_readout.txt` P2 | S6–S8, S7f, S10 |
| C2 insolvent end +0.631, its residual −0.260, unchanged designed income −0.140..+0.092 (post hoc, this paper) | `runs/RBT-99/readout-adversary/probe_readout.txt` P2 ("base con inc"), `runs/RBT-99/price.txt` | S11b–S11d |
| C2 placebo 23/25 | `runs/RBT-99/placebo.txt` P3 | S9 |
| C3 class A +0.286, r 0.095; D per seed; nets; founders6; wording | `runs/RBT-100/REPORT.md` | — |
| C3 per-seed arithmetic, alive end +0.121, residual +0.017; nets | `runs/RBT-100/score.txt` §1 | S12, S14 |
| C3 event − base +0.138, event − null +0.106 | `runs/RBT-100/placebo.txt` P4 | S13, S13f, S13n |
| C3 insolvent end +0.316; linearity; variants +0.113..+0.146; extinction coding; MDE 0.152; paired A/A 0.071 / 0.091 | `runs/RBT-100/readout-adversary/probe_readout.txt` P2–P5 | S15, S17, P1 |
| C3 placebo 23/25 | `runs/RBT-100/placebo.txt` P3 | S16 |
| C4 class C −0.310, r 0.171; R-shifts +0.635 / +0.177; re-wiring; seed 806; wording | `runs/RBT-101/REPORT.md` | — |
| C4 event − base −0.458, event − null −0.472, placebo 23/25 | `runs/RBT-101/placebo.txt` P3–P4 | S18, S18f, S19, S20 |
| C4 registered prior (solo probe) −0.325, residual −0.133; with the half-discount −0.163, residual −0.296 | `runs/RBT-101/flat_probe.txt`, `arith.txt`; `runs/RBT-101/REPORT.md` §4 | S28–S31 |
| C4 arena predictors Z10 −0.630, Z −0.701; residual +0.172; per-fauna residuals (post hoc) | `runs/RBT-101/readout-adversary/probe_arena.txt` | S21, S22, S22f, S23 |
| C4 simulated C0 −0.806; same-season refund −0.721, response +0.272; designed response flat / random; simulated total −0.450 (post hoc) | `runs/RBT-101/readout-adversary/probe_refund.txt` | S24–S27c |
| C4 paired A/A 0.108–0.123 | `runs/RBT-101/readout-adversary/probe_readout.txt` P4 | — |
| Arena A/A RMS 0.128, h 0.178, 9 seeds for ±0.10 | `runs/RBT-96/REPORT.md` §3–§4 | P5 |
| Power table | `docs/paper-9/rederive.py` → `rederive.txt` | P1–P6 |
| Lessons 1–8 and the rulings | Chaotic RBT-92 (18:11, 18:45, 18:50), RBT-99 (18:42, 18:46, 19:05, 19:10), RBT-100 (20:06, 20:14), RBT-101 (19:38, 20:40, 20:45); the readout adversaries' `READOUT-ADVERSARY.md` under each `runs/RBT-NN/readout-adversary/` | — |
| RBT-107's depth and common-garden design | Chaotic RBT-107 (designer 19:55, coordinator 20:28); **[PENDING: `runs/RBT-107/` on integration]** | — |
| RBT-110 | **[PENDING: RBT-110's merged report]** | — |
| Paper adversary rounds 1 and 2 | `docs/paper-9/adversary/PAPER-ADVERSARY.md`, `probe_paper.txt`, `probe_round2.txt` (PR #205, merged with or before this paper) | — |
| Instrument taxonomy | `docs/paper-7-five-instruments.md` | — |
