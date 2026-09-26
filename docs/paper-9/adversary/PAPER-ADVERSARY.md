# Paper 9 adversary (RBT-109): findings on `docs/paper-9-net-of-arithmetic.md` at `6a04057`

Round 1 covers the frame, C1–C3, the post hoc C2 bracket, §8's power arithmetic and lessons 1–7. §3.4 (C4) and
the RBT-110 synthesis are placeholders at this head and are re-audited when the writer fills them. The paper is
not edited here.

**Sources read:**
- the paper;
- `docs/paper-9/rederive.py` / `.txt`;
- for each of RBT-92, RBT-99 and RBT-100: the merged `REPORT.md`, `readout.txt`, `score.txt`, `placebo.txt`,
  `price.txt`, `baseline_depth.txt` and `PREREGISTRATION.md`, as each ticket has them;
- `readout-adversary/READOUT-ADVERSARY.md` and `probe_readout.txt` for the same three tickets;
- `runs/RBT-96/REPORT.md` and `docs/held-out-challenges.md`;
- the coordinator's rulings and the designers' summaries on Chaotic: RBT-92 at 18:11, 18:45 and 18:50; RBT-99 at
  18:42, 19:05 and 19:10; RBT-100 at 20:06 and 20:14; RBT-109 at 20:50.

**Probe:** `probe_paper.py` → `probe_paper.txt` (sections A–F below).

**Bottom line:**
- Every C1–C3 number the paper prints traces to a committed file with the right value.
- The re-derivation round-trips byte for byte (A).
- The post hoc C2 insolvent end is derived correctly (D).
- **Seven sentences are stronger than their sources, and two citations are wrong.** Most are one-word or
  one-clause fixes. None of them needs a new run.

## MUST-FIX

**F1. §0, l.91: "the rule could not have said anything else about C1–C3."**
- No merged report says this. They say the rule's A "carries no information about the event" (RBT-99, 18:46),
  or "certifies … nothing about the shift" (RBT-100 headline).
- The placebo test shows the rule returns A *without* an event. It does not show the rule returns A *whatever*
  the event does. C and D were live classes: D fired on 4/10 seeds in C2 and 7/10 in C3.
- Fix: "the rule returns the same class with no event, so its A carries no information about the event."

**F2. Abstract, l.35–36: "The co-evolved body already led by +0.16 before the onset, and the rule measured that
lead." The same frame appears in the ticket, argument 1.**
- True of C1 and C3.
- On C2 the event arm's R-body is +0.519 against the base's +0.148. RBT-99 F4 says "Unlike C1, the paired
  contrast classifies A too … Here the event moved the contrast." §2 quotes that correctly; the abstract
  generalises past it.
- Fix: "the rule's A is returned with no event on every challenge; on C2 its size also carries the price
  arithmetic (§3.2)."

**F3. Abstract, l.43: "+0.32 if it went extinct as its arithmetic says it must".**
- The ruling (RBT-100, 20:06) and the REPORT (l.28, l.124) say "implies".
- The designed fauna survived on 5/10 seeds and stayed solvent on 3 (REPORT §4; adversary F5: "what was not
  predicted is survival on 5/10").
- The adversary adds that the truth "lies between these two, depending on when it would die out" (F2).
- "Must" reads as a claim about the real fauna. Use "implies". The table (l.69) and §3.3 (l.291) already do.

**F4. The C3 row, §3.3 and the abstract omit C3's event − null.**
- C3's event − null is **+0.106 [−0.045, +0.256], 7/10, unresolved** (`runs/RBT-100/REPORT.md` §2 l.84–85;
  `placebo.txt` P4; probe E).
- Lesson 2 (l.426) and the 18:45 ruling name "the paired event − base contrast against the random-cull null" as
  the event readout.
- The C2 row prints its event − null, which resolves. The C3 row prints only event − base, whose lower bound is
  +0.006 under one coding.
- Add the line to the C3 row and to §3.3.

**F5. §5, l.406: "The designed fauna's partial solvency is the one thing in C2–C3 that the arithmetic did not
predict".**
- Both bodies' nets (R-shift + price) resolve above 0 in both challenges:
  - C2: co-evolved +0.207 [+0.151, +0.262], designed +0.524 [+0.362, +0.687] (REPORT "Both nets");
  - C3: co-evolved +0.131 [+0.078, +0.185], designed +0.114 [+0.018, +0.210] (`score.txt` §1 l.24–27).
- C2's residual −0.318 resolves as well.
- Fix: "Neither body lost its full unchanged-gait price in C2 or C3, and the designed fauna stayed partly
  solvent. Whether that is sorting or survivor-conditioning, the committed tables do not separate."
- Also, "turnover of a lifetime mean" is not in either cited §8/§6. RBT-99 REPORT l.285–287 names only sorting
  on kJ and survivor-conditioning.

**F6. §7, l.481: RBT-105 "cannot move any class or paired sign in C1–C3 (RBT-92 F5; RBT-99 F9; RBT-100 F7)".**
- Only RBT-99 F9 says "the class or the paired sign".
- RBT-92 F5 says the class only.
- RBT-100 F7 says the class only, and finds that C3's paired 8/10 "survives jitter in only 46–49%" of draws: a
  coin flip.
- Fix: "cannot move any class in C1–C3, or C2's paired sign."

**F7. §7, l.469–471: "0.071 (cull − base) to 0.108 (cull20 − base), pooled 0.091", cited first to RBT-92 F5.**
- The 0.071 and the pooled 0.091 are RBT-100's (`probe_readout.txt` P5).
- RBT-92 F5 gives cull − base **0.113**, cull20 − base 0.108 and shift − base 0.102.
- l.478 then says "against the 0.08–0.11 used above", which does not match l.469's "0.077–0.10".
- Attribute each figure to its own ticket, and make the range 0.071–0.113 or say which ticket each end comes
  from.

**F8. §1, l.124: "cull20 … is the turnover reference (RBT-92 Amendment 2)".**
- It is Amendment 3 (`PREREGISTRATION.md` l.632: "cull20's income column is the turnover reference the report
  leans on").
- Amendment 2 (l.522–573) does not mention cull20.
- The merged wording is REPORT l.121: "The turnover reference is cull20 (F6)".

**F9. §0, l.94 and §8, l.496: "Inside the recovery window a lineage has had about five reproduction events".**
- `baseline_depth.txt` measures gain over **[T, T+160)**, which is the transient plus recovery.
- RBT-92 REPORT §5 says "Depth inside the transient and recovery windows is about 5". The protocol's §10 table
  has "transient + recovery 160 ≈ 5".
- The Sources row (l.605) has the window right.
- Also, "range 3–7" is the holistic range; the designed range is 3.5–6.0.

## The paper's own additions

**F10. CAVEAT. The C2 insolvent end (S11b, §3.2) is correct, but half of it is missing.**

The derivation is right (probe D; the C2 audit):
- column 13 of the RBT-99 adversary's P2 table is "base con inc", the base designed fauna's recovery-window
  `mean_lifetime_score`, the same axis and window as the R-shift;
- extinct = 0 is the report's coding (REPORT l.123);
- "−0.140 to +0.092, below 0.25 on every seed" is the adversary's printed figure (P2 l.61, F2);
- +0.631 [+0.577, +0.684] re-derives independently.

It is labelled post hoc in the table, §0, §3.2, §9 and the Sources, and it enters no verdict.

Three gaps:
- **(a)** The residual against the insolvent end, **S11c −0.260 [−0.448, −0.071], 2/10**, is printed nowhere in
  the paper.
  - Lesson 7 says the residual is read against both ends.
  - Read that way, C2's non-arithmetic part resolves toward the designed body at *both* ends.
  - "The arithmetic accounts for all of the effect, and more" (§3.2, §4) describes this from one side only: the
    "more" is the designed body beating its own unchanged arithmetic.
  - Print S11c beside S11b, in §3.2 and the §4 table.
- **(b)** Two places do not carry the post hoc label:
  - §4, l.371: "This paper's re-derivation sharpens 'inside' for C2";
  - lesson 7's "where it bit" cell, l.431: "C3 (and C2, §3.2)".
  - "Accounts for all of it and more" is already the RBT-99 adversary's reading at the alive end (F2: "the whole
    paired effect, and more"). It is not a sharpening from the re-derivation. Credit the adversary for it; what
    the re-derivation adds is the insolvent end.
- **(c)** Two smaller corrections:
  - "earns less than nothing" (l.254) holds on 9/10 seeds; seed 7 is +0.092.
  - The insolvent end uses the base arm's *recovery-window* income, not a pre-onset quantity as lesson 3 frames
    the arithmetic. Say so beside the post hoc label.

**F11. CAVEAT. §8, l.533: "Halving the MDE costs about four times the seeds on every row."**
- The table's own rows give n@0.05 ÷ n@0.10 = 3.1, 3.2, 3.9, 3.6 and 3.6 (probe F).
- Write "three to four times".
- The rest of §8 re-derives: every MDE and n in the table reproduces from `rederive.py`'s t quantiles, and the
  protocol's "smallest effect worth claiming, 0.10" is §7 l.399.
- Reading 1 is correctly conditional.

## The frame

**F12. CAVEAT. Abstract l.34–35, §2, table: "on 23 of 25 placebo onsets, in every challenge [S4, S9, S16]".**
- The three files hold the same computation on the same baseline arms and the same T. The sequence
  AAAAAAAAAAAAAAAAAAAAAAFFA is identical in all three (probe B; RBT-99 F4: "RBT-92's result by construction").
- §2 l.157 says so. The abstract and the ticket's "in every challenge" read as three replications.
- Say once that it is one test on the shared baseline, which serves all three challenges.
- Otherwise the frame is supported:
  - A on the base and on 23/25 placebo onsets is exact for C1–C3;
  - the paper confines itself to the ten populations and one economy (§0 l.97–98; §9 l.551–553).

**F13. CAVEAT. The abstract (l.48) and the §5 title: "survivorship of the co-evolved body's standing gait".**
- The C2 claim line (protocol §2) is "survivorship of the co-evolved **population**".
- What C2 and C3 show is population income: the co-evolved fauna paid its way on 10/10 seeds, as its pre-onset
  gait's arithmetic implies.
- The gait itself is not observed after T. RBT-99 F3 says "the base's kJ after T is unmeasured", and the
  co-evolved body recovered 79% of its C2 price, which the unchanged gait would not have.
- "Standing gait" asserts carriage that nothing measured (lesson 6's territory). Use "population, by income".

**F14. CAVEAT. Conclusion, l.583–584: "what the arithmetic of that gait predicted before either event".**
- The per-seed arithmetic was computed after the arms, from pre-onset data:
  - C2: `price.txt` is a disclosed late deviation (RBT-99 F11);
  - C3: "computed after the arms from pre-onset data" (the 20:06 ruling, item 4).
- Only the form, plus C2's `kj_baseline` probe and C3's §4 "below basal", came before the arms.
- Write "what that gait's pre-onset arithmetic implies".

**F15. CAVEAT. §6, l.419–420: the lessons are "the reusable result: none depends on the ecology's details".**
- Lesson 5 is about this ecology's within-season refill.
- Lesson 4 is about a lifetime-mean axis with lag-1 autocorrelation 0.69.
- The *rules* travel. The *failures* they caught depend on those details.
- Write "each is a rule a future event readout can follow; two of the failures they caught (4, 5) came from this
  ecology's axis and refill."

## Lessons 1–7: accuracy and attribution

**F16. NONE, with citation notes. Lessons 1–7 are stated accurately and attributed to the right adversary and
ruling.**

All the ruling quotes check out against Chaotic:
- "The class rule measures the level of the lead, not robustness to the event";
- "Every challenge readout … must report the class on the no-event baseline and on placebo onsets beside the
  event arm";
- "The paired event − base contrast against the random-cull null is the only readout that speaks to the event";
- the recovery-rule sentence.

All four are verbatim from RBT-92, 18:45. Lesson 3 is RBT-99, 19:05, and lesson 7 is RBT-100, 20:06 ("adopted
programme-wide": the 20:14 close).

The "what the registered readout said" quotes are from the designers' **Chaotic** summaries, not committed
files:
- lesson 1's "the co-evolved body survives crowding and keeps its lead" (RBT-92, 18:11);
- lesson 3's "got back about 80% of its price" (RBT-99, 18:42);
- lesson 4's "returned … within 180 seasons" table (RBT-99, 18:42) and "never left the band on 6 seeds" (RBT-92,
  18:11).

Cite them as such, since the paper's rule is "every number cited to a committed file". The committed pre-merge
wordings differ: "paid about 80% of its price back" (RBT-99 REPORT at `2e04ebd^`); "survives the shift"
(RBT-92 F2).

Small fixes:
- **Lesson 2.** Add RBT-99 F6 to "what caught it" for C2.
- **"Jitter the sign guard" (l.437).** "Coin flip" is RBT-100 F7's phrase, for C3's paired count at 46–49%.
  RBT-92 F6 found F at 10–20% for C1. Write "can be close to a coin flip; jitter it and report the rate."
- **§2, l.187–189 (C1 jitter).** Cite RBT-92 F6 / `probe_readout.txt` P5(e), "an illustration of the guard's
  margin, not a test", beside REPORT §7 item 9, which states the rate without the jitter.
- **Lesson 5, "the rule now".** "Only non-refilling facts count" is a synthesis, not a ruling's words.
  Attribute it to the RBT-99 designer (18:46) and RBT-100 F8, or drop the quotation form.
- **§6, l.417.** "C3's designer applied lessons 1–6 before its readout adversary saw it" needs "with two lapses
  the adversary caught (F8, F10)".

## Numbers, rounding and quotation

**F17. CAVEAT. Rounding under the [S] tags.**
- The paper prints the committed full-precision values correctly:
  - S1: −0.020 [−0.073, +0.034];
  - S7: +0.371 [+0.162, +0.581];
  - S13: +0.138 [+0.006, +0.271].
- But it tags rederive rows that print +0.033, +0.161 and +0.005, because they are computed from three-place
  per-seed values (probe C).
- Only S3's drift is footnoted (l.75–77). Extend the footnote to S1, S7 and S13, or make `rederive.py` read the
  full-precision lines.

**F18. CAVEAT. Quotations.**
- **The C3 table cell (l.69), "in the merged report's words".** It drops "therefore": REPORT l.29 reads "The
  arithmetic therefore brackets…".
- **§3.3, l.306.** The sentence is labelled "the adversary's F2 text", but the ", +0.12 to +0.32," is the
  designer's insertion (F2's proposed text has no numbers). Cite it as the REPORT headline.
- **§3.3, l.297–298.** "82%" is cited to "(same)", meaning REPORT §3. It is in the REPORT headline and §2, not
  §3.
- **§3.1, l.224.** "They lost the least" is quoted bare. The report scores that ordering "on the means (+0.032
  unresolved)" (REPORT l.205). Add "on the means; unresolved".

**F19. CAVEAT. Context dropped from §5 and §9.**
- **§5, C3 bullet.**
  - It omits REPORT §6's limit: random founders HOLD on 3/10 (804, 1, 4), so a general "bootstrap line" is not
    established.
  - The starved share, 1.2–2.5%, loses its comparison: 0.7–1.5% on the base.
- **§9, l.562.**
  - Linearity was checked over the first 1 to 10 post-onset seasons (P2), not only three.
  - The per-seed departure from 0.5 is −0.145 to +0.083, not a symmetric ±0.15.
- **§9, l.559–560.** Seed 806 "in every challenge" should also cite RBT-99 REPORT l.233 and RBT-100 REPORT l.152.
- **§7, l.463.** RBT-96's seed-201 reading is the designer's "description, not a result". Keep that qualifier.

**F20. NONE. Numbers checked and correct.**

C1:
- +0.180 [+0.077, +0.284], 8/10, r 0.104;
- +0.158 [+0.080, +0.236] and +0.148 [+0.051, +0.245];
- R-shifts, and −0.037 [−0.081, +0.006];
- +0.043, the 0.105 equivalence and 6.7%;
- alive = 60 in 37 runs, and 0.69;
- the F4 band counts, and k = 0 on 6/10 with n = 4;
- the two placebo misses at T+20 and T+30, F by the sign guard.

C2:
- +0.519 [+0.336, +0.702], r 0.183;
- kJ 19.0/5.2 (3.6), prices 0.950/0.261, +0.689 [+0.627, +0.751] and 54%;
- nets 79%/55%, −0.318 [−0.498, −0.138] and +0.29 [−0.02, +0.61];
- n = 7 at +0.315 [+0.161, +0.469];
- +0.79 to +1.22, −0.055 and −0.074, and +0.53 to +1.00;
- D 4/10, extinct 3, solvent 6, "3.9–6.7×" (the 10th seed is 3: D-bankrupt, 4 alive, not extinct);
- designed k ≥ 60 on three seeds;
- sign-guard ≥ 99.4%.

C3:
- +0.286 [+0.191, +0.382], r 0.095;
- prices 0.697/0.576, items 1.22–1.50 and 1.02–1.35, unchanged nets +0.08 to +0.18 and +0.29 to +0.59;
- linearity 0.488/0.497, variants +0.113 to +0.146;
- +0.121, +0.316, +0.017 and −0.178;
- the +0.090/−0.056 split, and the codings +0.061 and +0.190;
- nets +0.131 (23%) and +0.114 (16%), MDE 0.152 and 1.3×;
- survivors' net +0.50 to +0.66, founders6 7/10 with seed 7;
- designed 5/2/3 (804, 807, 7), ≥ 99.8%.

RBT-96: 0.128, h = 0.178, "three times".

Strength: every quoted merged sentence (the C1, C2 and C3 headlines, "Both nets", "Neither body can be said to
have adapted better") is verbatim and post-adversary. No "unresolved" reads as "equal": §4 says outright that
"not shown" is not "equal". No survival claim rests on alive = 60, and no recovery claim or carriage number
appears anywhere. The lesson 4, 5 and 6 checks hold.

## Pending

§3.4 (C4), lesson 8 and the [PENDING: RBT-110] synthesis are placeholders at `6a04057`. The coordinator's 20:50
comment on RBT-109 sets what they must carry:
- the arena's own arithmetic, −0.63 to −0.81, against −0.458;
- a residual toward the co-evolved body of +0.17 [+0.06, +0.29] or +0.27 [+0.05, +0.49], 8/10, **post hoc**;
- the abstract's "no difference in how the two bodies responded is shown", which needs a C4 qualifier.

Until they are filled, note that:
- the abstract l.44–47 and §4's heading, "No difference in response between the bodies is shown", are true of
  C1–C3 only, and §3.4 says so;
- §3.4's TODO item 4 still names "the solo-probe terrain prediction", which the 20:40 ruling replaced.

I will re-audit those sections against RBT-101's amended merged report and RBT-110's results when they land.

---

# Round 2: the paper at `9ec52bf` (the round-1 fixes; C4 and lesson 8 filled; RBT-110 pending)

**Sources.** Everything in round 1, plus:
- `runs/RBT-101/REPORT.md`, `arith.txt`, `placebo.txt`, and `readout-adversary/READOUT-ADVERSARY.md`, `probe_arena.txt`, `probe_refund.txt`;
- the RBT-101 thread on Chaotic: the designer's 19:38 summary, the adversary's 20:35 report, the 20:40 ruling and the 20:45 close;
- the RBT-109 thread: the 20:52 ruling and the writer's 20:54 answer.

**Probe.** `probe_round2.py` → `probe_round2.txt`, run from a checkout of `results/RBT-109-paper9`.

**Re-derivation.** `rederive.py` still round-trips byte for byte at `9ec52bf`.

**Round 1.** F1, F3–F11 and F13–F19 are applied correctly. F2 and F12 are partial; see F28 and F29.

## MUST-FIX

**F21. C4's registered residual is missing, and it runs the other way.**
- The merged `runs/RBT-101/REPORT.md` §4 table prints every predictor. Its registered prior with the registered half-discount (Amendment 2) predicts −0.163 and leaves **−0.296 [−0.511, −0.080], resolved toward the designed body**. The undiscounted prior leaves −0.133 [−0.486, +0.219]. Post hoc Z leaves +0.243 [−0.007, +0.493], 7/10, unresolved.
- The paper prints none of these residuals: not in the summary row (l.94), §3.4 (l.436–439), §4's table or the abstract (probe G). It prints only the two post hoc residuals that resolve toward the co-evolved body.
- So the direction of C4's non-arithmetic part depends on which predictor is chosen. The registered prior as registered points toward the designed body; the post hoc arena predictors point toward the co-evolved body. The 20:40 ruling adopts the arena reading, rightly, but the reader must see the registered line.
- Add the −0.296 and −0.133 residuals to the table, §3.4 and §4's table. §4's "No registered residual resolves in the co-evolved body's favour" is true, but it needs its companion clause: "the one registered C4 residual that resolves runs toward the designed body."

**F22. "C4 carries the first resolved non-arithmetic effect" contradicts the paper's own table.**
- The sentence is at §4 l.542. Related wording: §8 l.794–795, "the first sign that such a difference may exist"; §3.4 l.464 quotes the ruling's "the first resolved non-arithmetic effects in phase 2".
- C2's merged residual, −0.318 [−0.498, −0.138], resolved first; it closed at 19:10, before C4. S11c resolves as well, and the abstract (l.57) itself says two residuals resolve.
- The quote at l.464 is verbatim from the 20:40 ruling on Chaotic. Keep it, but qualify it beside the quote.
- In the paper's own voice, write "the first resolved residual in the co-evolved body's favour, on a post hoc predictor".

**F23. Abstract l.46–47: "each event is accounted for by what it does to two populations that change nothing".**
- Eleven lines later the abstract says two non-arithmetic residuals resolve.
- On C1 no arithmetic was registered. On C2 and C4 the arithmetic over-predicts and leaves resolved residuals.
- Write "no event's paired effect exceeds what its unchanged-population arithmetic predicts", and tag the C4 bullet "(reported apart)".

## CAVEAT

**F24. "Wholly by the furniture's arithmetic" rests on the post hoc arena predictors.**
- It is unlabelled at §0 l.124–125, §2 l.244, the §3.4 heading l.412, §8 l.716–717 and §10 l.848.
- §8 l.733 says "had to be measured in the arena itself before it was right".
- The merged REPORT also uses "wholly" unlabelled, so the paper is no stronger than its source. But under the registered prior (F21) the flip is not wholly arithmetic. Add "(post hoc arena arithmetic)" at least in the abstract, §0 and §10.
- Lesson 8's cell, "the arena predicts −0.63 to −0.81", needs the same label.

**F25. The same-season split is printed without its refund.**
- The response, +0.272, is measured against the T+110 refund, **−0.721 [−0.885, −0.558]** (`probe_refund.txt`). The paper prints that refund nowhere.
- The summary row's arithmetic cell pairs −0.806 (the simulated C0) with the +0.272 response, but −0.458 − (−0.806) = +0.348.
- Add −0.721 as the split's refund, as REPORT §4 and adversary F2 both do.

**F26. The designed decline "on flat and on random ground alike" (l.460–462) resolves on one terrain only.**
- On flat ground it is −0.222 [−0.445, +0.002], 2/10, unresolved. On random ground it is −0.174 [−0.312, −0.036].
- It is one simulated season (T+110), post hoc. The REPORT's wording is the same, so the paper is not stronger than its source. The numbers are printed, but "alike" should become "resolved on random ground only".

**F27. The abstract doesn't say which side carries C4's residual.**
- The abstract (l.59–60) says the contrast "moved back toward the co-evolved body".
- REPORT §4 puts the non-arithmetic part on the designed side: "the co-evolved body sits on its arithmetic" (+0.016 against Z10).
- Add that clause, so that no reader takes it as the co-evolved body responding better.

**F28. F2 is applied only in part: the §2 heading still generalises past C2.**
- l.202 reads "The registered rule measured the pre-existing lead on C1–C3".
- Write "…on C1 and C3; on C2 it also carries the price; on C4 the event flipped it".

**F29. F12 is applied only in part: the placebo citations are incomplete.**
- l.215–217 and the Sources row l.885 cite `probe_paper.txt` B for all four challenges, but B compares only C1–C3.
- C4's sequence is identical (checked: `runs/RBT-101/placebo.txt` P3). Cite that file for C4.
- RBT-92 has no `placebo.txt`; C1's calls are in `readout-adversary/probe_readout.txt` P3.

**F30. Adversary files are cited, but they are not on the paper's branch.**
- The header l.6, §2 l.217 and Sources l.885 cite `docs/paper-9/adversary/...`.
- Those files exist only on #205. Merge #205 with or before #204, or the citation points at nothing on integration.

**F31. "Two non-arithmetic residuals resolve" (abstract l.57, §10 l.851) states no criterion.**
- §4's table also marks C3's insolvent-end residual, −0.178, as resolving, toward the designed body.
- Under lesson 7 an effect inside the bracket is undecided, so "two" is right if the criterion is "resolves against every end of its prediction". Say so.

**F32. Smaller fixes.**
- **§4 l.498** cites "Amendment 2" for the C2 price. RBT-99 adopted the price and the net in **Amendment 1** (F4); Amendment 2 only gated `price.txt`.
- **§5 l.589**, "Neither body lost its full unchanged-gait price in C2 or C3", holds on the mean only. In C3 the designed share runs −0.16 to +0.43 per seed. Add "on the mean".
- **l.636**, "C1's class returned F in 10–20% of draws": this figure was my own round-1 wording (F16), and it is inexact. RBT-92 F6 gives F at 2%, 9% and 20% for s = 0.05, 0.08 and 0.11. Write "roughly 1 in 10 to 1 in 5", as §2 does.
- **§8 l.725**, "C4's re-wiring readout saw no change at that depth", needs its resolution: blind below about half of the installable co-evolved survivors and a fifth of the designed ones.
- **l.473** cites REPORT §5 for "no re-adaptation is claimed"; that wording is in the REPORT headline.
- **Lesson 8's "not about twice".** The quotation marks are misplaced. The source is: That is 4–7×, not "about twice".
- **§8 l.732**, "On C2–C4 …", is a joint statement. Tag C4 "(apart)".
- **Rederive coverage.** For C4, `rederive.py` covers only S18–S24. The preface says all summary-table figures are recomputed there, and the Sources cite S24 for +0.272 and −0.806, which it does not hold. Add rows, or soften the preface and the Sources.

## NONE

**F33. Checked and correct.**
- **Class C.** −0.310 [−0.481, −0.139], 9/10 negative, r 0.171, a margin of 1 seed; D, E1 and E2 are each 0/10.
  - The owner's §9 words are verbatim, and "gained less; it did not lose" stays beside every "wins".
  - The robustness checks hold: leave-one-out, every window, and 98.4% of jitters.
- **R-shifts.** +0.635 and +0.177.
- **Paired contrasts.** −0.458 [S18f], and −0.472 with its "≡ event − base on six k = 0/0 seeds; ~0.5%".
- **Placebo.** 23/25, the same shared-baseline sequence.
- **Arena predictors.** Z10 −0.630, Z −0.701, C0 −0.806; the refund +0.94 against +0.14–0.22.
- **Residuals.** +0.172 against Z10, 8/10, and the response +0.272, 8/10.
- **MDE.** 0.163 [S23].
- **Re-wiring.** NO CHANGE SEEN, blind below f ≈ 0.5 of the installable co-evolved survivors and 0.2 of the designed ones.
- **Lessons 4–6.** Applied.
- **Seed 806.** −0.270, 8/9.
- **Paired A/A.** 0.108–0.123.
- **Quotes.** The REPORT §9 sentence is verbatim, as is lesson 8's designer quote (RBT-101, 19:38, Chaotic).
- **Post hoc labels.** "Post hoc … a hypothesis, not a finding" labels +0.17 and +0.27 in the abstract, table, §3.4, §4, §9 and §10.
- **No pooling.** C4 is never pooled numerically with C1–C3.
- **Lesson 8.** Stated accurately. It is attributed correctly to RBT-101's adversary (F2) and to the 20:40 ruling.

## Pending

The RBT-110 placeholders are in the abstract, §4, §6 row 8, §8 and §10. They will be audited against RBT-110's merged report when filled.
