# Progress report 3: adversary and fact-check

- **Reviewed:** `docs/progress-reports/2026-10-11/index.html` and the new row in `docs/progress-reports/README.md`, on `claude/happy-ramanujan-0jka04` at `bc9780ffaf07d87f016bf36620e94977e85b89c6` (draft).
- **Base:** `ae54630d` (#560, the Stage-2a interim). `git diff ae54630d bc9780ff --stat` touches only the page and the README.
- **Sources checked:**
  - the two permitted Stage-2 result files, `runs/RBT-129/stage2/integrity-interim.txt` and `stage2a_interim.txt`, and the merge message of #560 (provenance and the drivers adversary's verdict);
  - `stage2-plan/`: STAGE2-PLAN (§0, §1–§2, §5.1), RULINGS-CITED-S2 (S2-R1 to S2-R4, the locks) and COORD-RULING-523;
  - `stage2-drivers-adversary/ADVERSARY.md` R-9;
  - `DESIGN.md` §4.1–§4.2 (R-A, R-B, M2), the T4 row, and W118-c;
  - `continuations/QUARANTINE.md`, `OVERFLOW-RULE.md` §1–§2, and the withdrawn `coordinator/DEVIATION-S2A-HOST0-LANE0.md` (from `a0ec49ef`);
  - `coordinator/`: COORD-RULING-527, COORD-RULING-RB-HELP-1, DISCLOSURE-2026-10-02 and -03, OWNER-DECISIONS-2026-10-03, -03b and -04;
  - `stage1-readout/READOUT-STAGE1-CORRECTIONS.md` A7, and `mn-crash/COORD-RULING-520.md`;
  - `calibration-final/DECISION.md`;
  - RBT-116: PREREGISTRATION (title, §4.3 gate table), W1_GATE_AMENDMENT, `gate/GATE_NOTES.md` (H11, RBT116-PILOT-10, RBT116-S2) and `gate/W1/READOUT-NOTES.md` (the gate's rows, quoted there verbatim);
  - RBT-134: DESIGN §0, §9 and amendment I5-a;
  - `docs/prior-art/REVIEW.md` and `citation-check/CHECK.md`;
  - report 2 (`2026-10-04/index.html`) and its review;
  - the commit messages of `a0ec49ef`, `7ebd66ff`, `f1faaf94`, `c31de0c5`, `327dfcfa`, `e37de62e`, `f58a8c12`, `ae54630d`, and the RBT-134 merges.
- **Facts taken on the coordinator's word**, which are not in committed docs:
  - 2a complete on 10-07;
  - RBT-116 closed at W1 on 10-05;
  - its ~500–680 core-h held for RBT-134's follow-on;
  - RBT-134 CONTINUE on 10-05;
  - RBT-134's lanes pushed at `eea50ce`, with no PR yet;
  - the interim run's 30-minute kill, the authorised re-run and the stderr line;
  - the drivers adversary's APPROVE-WITH-NITS.
- **Rules kept:**
  - narrow-refspec fetch of the draft branch only, and no `ckpt/` branch fetched;
  - no run directory, run log, EPA log, lane file, checkpoint, SCAN, GATE, g1 or screen file opened;
  - GATE.txt's rows were checked against READOUT-NOTES.md, which quotes them verbatim.

## Verdict: **PUBLISH WITH FIXES**

The page is careful, and most of it traces:
- every number in the interim section matches the two interim files;
- the skipped counts recompute to M 8 and N 5;
- the 10 points decode correctly from their labels;
- RB-HELP-1, COORD-RULING-527 T4, I5-a, RBT116-S2 and the 3 October disclosure are carried accurately;
- the gate's numbers match the readout notes;
- no call from Stage 2 is printed.

Four things must be fixed before the page goes out:
- M1: the account of what the W1 failure means leaves out half of it;
- M2: a claim about exposure labels is false, and is the same error report 2's review caught (m5 there);
- M3: the footer says every source is in the repository, and several are not;
- M4: there is no card for report 3 on the site's front page.

The MINORs are each a one- or two-line edit.

| severity | count |
|---|---|
| BLOCKING | 0 |
| MAJOR | 4 |
| MINOR | 11 |
| NOTE | 7 |

**Numbers found wrong:** none.

**Numbers right but misscoped:**
- the next batch's 180.6 / 338.1 core-hours includes merged runs at 2 points, but the page describes it as seeds alone (m3).

---

## MAJOR

### M1. "What it means" leaves out the fixed body's failure

**Page** (The bypass test, L225):
> In this world, the test could not be shown to detect a compass on the evolving bodies, so the comparison could not be run fairly. That is all.

**Evidence.** `gate/W1/READOUT-NOTES.md`, which quotes GATE.txt verbatim:
> G1 FAIL: first paying rung 2.0; 0/16 PASS there; c_G1 0.000

> G8 FAIL: (a) confirmed 0.042 (bar 0.6 x c_G1 = 0.000) ok; (b) 1 STEERS among 35 paying FAILS; (c) 0.000 pooled …

- G1 is a check on the **fixed** body (PREREGISTRATION §4.3: "Perception pays, on the Pioneer").
- At the strength where a planted compass first pays, the steering test confirmed it on 0 of 16 fixed-body hosts.
- G8(a) passes only because its bar is 0.6 × 0 = 0.
- G8(b) is a false positive on a directionless circuit.

So the instrument failed on both kinds of robot, and also once said "steers" where it must not. The page's own table shows this (rows 1 and 2), but the summary blames the evolving bodies alone. Followed by "That is all", the summary invites the reading that the evolving bodies' compasses are the problem. That is a body-specific inference the gate does not support.

**Replace with:**
> In this world, the steering test could not confirm a planted compass on either kind of robot at the strength where one first pays: 0 of 16 on the fixed body, and 0% on the evolving bodies. It also once read a circuit with no sense of direction as steering. So the comparison could not be run fairly. That is all. It says nothing either way about whether evolving bodies bypass the valley. That question is still unanswered.

### M2. Not every coordinator ruling since the slip is labelled

**Page** (One run unit set aside, L121):
> Like every coordinator ruling since the slip disclosed in report 2, it is labelled as made after that exposure.

**Evidence.**
- The slip is at 20:45 UTC on 2 October (`DISCLOSURE-2026-10-02.md`).
- `mn-crash/COORD-RULING-520.md` was ruled at ~13:00 UTC on 3 October. It carries no COORDINATOR-EXPOSED label (0 matches).
- Report 2's review found exactly this (m5: "COORD-RULING-520 (crash diagnosis) does not").
- Also, the ruling the page describes was not the coordinator's. `QUARANTINE.md` calls it an "owner's proxy ruling … approved first-hand by the owner". It is labelled COORDINATOR-EXPOSED.

**Replace with:**
> It is labelled as made after the coordinator's exposure disclosed in report 2.

### M3. The footer says every source is in the repository, and several are not

**Page** (footer, L303):
> … All are in the project repository.

**Evidence.** These statements trace to no committed doc or commit message. I searched `runs/`, `coordinator/` and the log back to #540.
- **L226:** "On 5 October the project decided to close the study at W1 rather than register another world point … That compute is now held for a follow-on."
  - READOUT-NOTES leaves the choice "to the owner and the coordinator", and records no decision.
- **L236:** "Decision, 5 October: continue."
- **L124:** "2a finished on 7 October." The nearest record is `327dfcfa`, dated 8 October.
- **L237:** the operator study's job lists "written and pushed for review … That waits on a step a person must take." The coordinator vouches for the push at `eea50ce`, with no PR. Nothing vouches for "a step a person must take".
- **L177:** "ran in a separate session". The #560 message says only that the interim was "produced … in the designated readout session".
- **L179:** the review's verdict, "approved, with minor notes". It is in the #560 merge message only, not in a committed review file.

I accept the coordinator's word for the facts. But a reader told "All are in the project repository" will not find them.

**Fix (preferred):** commit a short decisions record before publishing, for example `coordinator/OWNER-DECISIONS-2026-10-05.md`. It should hold:
- RBT-116 closed at W1;
- the core-hours held for RBT-134;
- RBT-134 CONTINUE;
- 2a complete on 7 October.

Then add it to the footer as "the project's recorded decisions of 3, 4 and 5 October".

Separately:
- either drop "That waits on a step a person must take", or source it;
- drop "in a separate session", or source it.

**Fix (fallback):** change the footer's last sentence to:
> All are in the project repository, except the project's decisions of 5 October, which are recorded by its coordinator.

### M4. Report 3 has no card on the site's front page

**Evidence.**
- Report 2 added a card to `docs/index.html` (L74), and its review checked it (n5).
- The draft does not touch `docs/index.html`. Its newest card is still report 2.
- The README sends readers to the Pages site, whose front page lists reports only through these cards. As things stand, report 3 can be reached only by typing its URL.

**Fix:** add a card above report 2's, in the same pattern:
```html
<a class="card" href="progress-reports/2026-10-11/"><span class="meta">11 OCTOBER 2026</span><strong>Half of Stage 2 is in, and nothing is read yet</strong>The world sweep’s Stage 2a is complete and passes its integrity check; a rule fixed in advance chose 10 points for more seeds, and no call is printed until the final readout. The bypass test’s world failed its gate, so that study closed; the study of mutation’s operators continues.</a>
```

If m1 is taken, apply it to the README row too: "no result is printed" becomes "no call is printed".

## MINOR

### m1. "Nobody, including us, sees any result" overstates the blinding

**Page:**
- lede (L88): "Under the plan, nobody, including us, sees any result from this half until the final readout."
- In brief (L96): "It prints no result by design."

**Evidence.**
- S2-R3 and plan §5.1 forbid printing "no provisional §8 and no verdict-relevant call". The 2a calls are "not printed to anyone".
- But the interim does print things computed from 2a's data, and people have seen them:
  - the R4 list;
  - each point's CP, a conditional power at the 2a estimate;
  - counts from which pre-merge survival at the gated points follows (drivers adversary R-9: "They are pre-merge survival at the gated points").
- "Any result" is broader than the rule.

**Replace with:**
- lede: "Under the plan, no call from this half is printed, to anyone, until the final readout."
- In brief: "It prints no call, by design."

### m2. "Being on this list says only that a point is not yet settled": the converse also informs (blinding)

**Page** (caption, L172):
> Being on this list says only that a point is not yet settled.

**Evidence.**
- Plan §1.1 lists the 12 Stage-2a points. The R4 list names 10, with the cap of 11 not binding.
- So a reader of the plan can tell that `c0-p018-HP-G` and `c1-p018-PW-L` were **not eligible**. Their 2a calls are neither UNDECIDED nor CONTINGENT (plan §1.2).
- `c1-p018-PW-L` is also the only null-arm point (plan §2.3). So the page's "5 skipped null runs" says that at that point, on 5 of 7 seeds, a kind had died out before season 59.
- That is permitted. The plan prints the R4 list by design, the skip counts follow from the committed interim, and the interim's review asked for them to be disclosed.
- But the caption's "only" is not true. See also n1.

**Replace the caption's last sentence with:**
> Being on this list says that a point’s call at 8 seeds is not yet settled. Being off it says the call is settled, one way or another. Neither says which body earns more.

**Append to "Skipped runs, stated plainly":**
> These are survival counts: a skipped run means one kind, or both, had died out on that seed before the merge. They say nothing about which kind, and nothing about income.

### m3. 2b is described as still to come, but its first part has already run, and its bound includes merged runs

**Page:**
- L109: "2b gives 8 more seeds … They come from Stage 1’s list (the extension below) and from 2a’s."
- L189: "Extending 9 Stage-1 points: run."
- L279: "Stage 2b | 8 more seeds at the 10 chosen points, within 180.6 / 338.1 core-hours".

**Evidence.**
- Plan §0: "2b: the 9 Stage-1 points are R-B GO-1". GO-1 finished on 4 October (OWNER-DECISIONS-2026-10-04 item 6, NOTE 17).
- So the remaining batch is 2b's second part, not "Stage 2b".
- Separately, `stage2a_interim.txt` gives the bound as "S, M at 2, N at 0". 10 × 8 × 300 S plus 2 × 8 × 240 M, at 23.35 / 43.72 core-s, gives 180.6 / 338.1. Seeds alone would give 155.7 / 291.5.

**Fix:**
- At L109, add: "The Stage-1 part has already run (below); what remains is 2a’s points."
- At L279, use "Stage 2b, second part" and "8 more seeds at the 10 chosen points, with merged runs at 2 of them, within 180.6 / 338.1 core-hours".
- In the same way, add ", with merged runs at 2 of them" at L96 and L154.

### m4. The holding pilot: "as first written" was the builder's reading, not the registration

**Page** (L247):
> As first written, the trial drew its 8 plants from one run unit’s robots only.

**Evidence.** `GATE_NOTES.md`, RBT116-PILOT-10:
> The refusal came from the builder's reading H11, not from the registration.

**Replace with:**
> As the gate’s code first read the registered rule, the trial drew its 8 plants from one run unit’s robots only.

Also, the ruling knew neither "the count nor the fauna". At the end of "not the counts", add "or which kind refused".

### m5. The first correction leaves out the rematch, and attaches the operator study to a sentence it does not correct

**Page** (Corrections, L264). Report 2's quoted sentence covers "The bypass test **and the rematch**". The "Now" column:
- says nothing about the rematch;
- adds the operator study, which that sentence never mentioned.

OWNER-DECISIONS-2026-10-04 item 4 wants the RBT-116 and RBT-134 decisions carried as forward corrections, but not necessarily under this quotation.

**Fix:**
- Split the row in two.
- Row 1 (bypass test and rematch): the W1 text as now, plus one clause on the rematch's status, for example "The rematch is unchanged: it waits on the final map."
- Row 2: Report 2 said nothing about the operator study. "Now": "Registered on 3–4 October, after report 2 was written, with its code then under review."

### m6. "A follow-on to the next study" is ambiguous

**Page** (L226):
> That compute is now held for a follow-on to the next study.

"The next study" reads as whatever comes next, rather than as the operator study, which is the next *section*.

**Replace with:**
> …held for a follow-on to the study of mutation’s operators, below.

See also n4 on the amount.

### m7. The Lehmacher and Wassmer citation is incomplete and unchecked

**Page** (Prior art, L296):
> Lehmacher and Wassmer (1999). The rule for combining …

- There is no title, venue, pages or initials. Every other entry has them.
- The entry is not in `docs/prior-art/REVIEW.md`, and `citation-check/CHECK.md` does not check it.
- Its only committed mention is DESIGN §4.2, "(Lehmacher & Wassmer 1999)".

**Fix:** give the full reference, after checking it against the publisher:
> W. Lehmacher and G. Wassmer (1999). Adaptive sample size calculations in group sequential trials. *Biometrics* 55(4): 1286–1290.

Keep the plain-language gloss, which matches DESIGN ("fixed weights, which is valid under data-dependent extension").

### m8. The accidental scratch start: "Nothing was read" is slightly too strong

**Page** (L200):
> Nothing was read, saved or pushed, and the scratch copy was deleted.

**Evidence.** `COORD-RULING-RB-HELP-1.md` NOTE:
> Nothing was read: only the runner's start line and a directory name were seen.

**Replace with:**
> Only the runner’s start line and a folder name were seen. Nothing was saved or pushed, and the scratch copy was deleted.

### m9. Phone width: two table columns are hidden behind an unmarked scroll, and one status is clipped

I rendered the page in Chromium at 390 px, light and dark.
- **The page itself is fine.** `scrollWidth` = `clientWidth` = 390 in both themes.
- **The integrity table** (L132–141) is 491 px inside a 334 px wrapper. "Unlogged" and "Crashed", the columns that carry the "nothing crashed" claim, sit off-screen behind a horizontal scroll with no visual cue.
- **The "What comes next" table** (L274–285) overflows its wrapper by 4 px. `td.when` is `white-space:nowrap`, so "decision pending" is clipped at its right edge, and the middle column wraps to one or two words per line.

**Fix:**
- In the integrity table, shorten the headers ("Excl.", "Overfl.", "Unlog.") or let them wrap below 520 px. Alternatively, put "Overflowed / Unlogged / Crashed: 0 in every arm" in the caption, so the claim does not depend on scrolling.
- For `td.when`, drop `nowrap` below 520 px.

At 1280 px, every wrapper fits (736 = 736). Both themes have an explicit body background: `rgb(246,247,244)` light and `rgb(20,24,32)` dark.

### m10. The interim's first run: say what it wrote

**Page** (L176):
> What it had begun writing was replaced by the re-run.

**Evidence.** #560's merge message: "It wrote no interim, and its integrity file was overwritten."

**Replace with:**
> It wrote no interim. The integrity file it had written was overwritten by the re-run.

### m11. "Reviewed before any data": 2a data now exist

**Page:**
- L278: "Reviewed before any data".
- L122: "The fix goes through the usual review before any data".

**Evidence.**
- QUARANTINE.md says the P-1 fix goes "through the normal pre-data adversary path" before 2b.
- "Pre-data" here means before any 2b data. 2a's data exist, and the interim was computed from them.

**Replace with** "before any 2b data", in both places.

## NOTE

### n1. Blinding: no breach found, and the page states no Stage-2 finding

- **No body or world named as winner.** The page names no point at which either body or world wins, and quotes no estimate, CP, t or p from Stage 2.
- **The scores are left out, rightly.** CP is a function of the 2a estimate, so it is closer to a result than the list is.
- **The table order hides the ranking.** The rows are sorted by dial, not by rank. I checked all 10 rows against `stage2a_interim.txt`:
  - c05 is between flat and normal, and c15 between normal and double;
  - HP is patchy, PW sparse, U uniform, G the new channel and L legacy;
  - p018 / 053 / 030 / 080 / 010 are 0.018 / 0.053 / 0.03 / 0.08 / 0.01.
- **What the list reveals is sanctioned.** As m2 notes, the list's complement, together with the null arm's skip count, lets a reader of the plan work out that the 2a calls at two points are settled, and that one of those points is survival-limited.
- I judge that this does not breach §5.1 or S2-R3:
  - the plan prints the R4 list by design;
  - the skip counts follow from the committed interim;
  - the drivers adversary asked for them to be disclosed;
  - 2b(2a) was committed before any 2a data existed, so nothing in Stage 2 can now depend on this knowledge;
  - the final map is mechanical.
- m2's wording makes that explicit rather than leaving "only" to mislead.
- If the coordinator would rather not make the inference easy, the lightest change is to state the skip counts for the merged arm only, together. Readers of the repository can still derive the null arm's count.

### n2. The excluded unit's first ruling was withdrawn

On 5 October:
- **The first proxy ruling ("A")**, `a0ec49ef`:
  - closed 2a with the lane INCOMPLETE;
  - ruled "no quarantine or exclusion";
  - left 19 jobs unrun, with an amendment proposed to complete them.
- **"A′"**, `7ebd66ff`, superseded it about two hours later. It excluded the unit and ran the other 15 jobs.

No data were read in between, and A′ is the ruling in force. The page describes only A′. That is defensible, but one clause would make the record complete:
> (A first ruling that day left the lane’s other jobs unrun; it was withdrawn in favour of this one.)

### n3. "Only adds logging": apart from a fail-closed write

**Page** (L187):
> It confirmed that the build only adds logging…

COORD-RULING-527 T1: "the patch is log-only, apart from the fail-closed write". This is optional, but exact:
> …only adds logging, and stops a run whose log cannot be written…

### n4. The core-hours held for the operator study

- OWNER-DECISIONS-2026-10-04 item 2 prices RBT-116 at ~500–680 core-h in total: "gate plus burn-ins ~88; arms 400–590".
- The gate and its burn-ins ran, so the whole 500–680 cannot still be unspent.
- The coordinator vouches for "~500–680 held". If the figure is the accepted allowance, not what remains, consider "the arms’ unspent allowance, about 400–590 core-hours".

### n5. W1's description

**"Random clutter" (L207).** Elsewhere the page calls this level "normal clutter". W1 is `c1-p030-PW-G` (DESIGN, W118-c), normal clutter, so use one word for it throughout.

**"Chosen in place of a Stage-1 point."** W1 is itself on Stage 1's grid. It is RBT-118's anchor W118-c. The source, READOUT-NOTES, says the coordinator "chose W1 rather than a Stage-1 point, because a point chosen after seeing Stage-1 results would be outcome-informed".

**Clearer:**
> It was kept, rather than replaced by a point picked from Stage 1’s map, because a point picked after seeing Stage-1 results would have been chosen with knowledge of the outcome.

### n6. Small items the page may want

- **The scratch start and the excluded unit are the same.** The reviewer's accidental scratch start (L200) was `S2A/c1-p018-PW-L/129001/S60`, the same unit later excluded (L116).
  - RB-HELP-1 records that the scratch clone ran against a local fake origin and touched no registered unit, so the two are unrelated.
  - A reader of the repository will notice the coincidence. Optional: "(by chance, the same unit as above; the scratch copy touched no registered run)."
- **The as-of stamp has no time.** The masthead reads "AS OF 9 OCTOBER". Report 2's carried one ("3 OCTOBER, 15:00 UTC").
  - Two pending items could change before the 11th: the side-by-side scan decision, and the operator study's PR.
  - Re-check both at publication, and add a time.
- **Brief list's "Pending" omits one item.** It leaves out the operator study's runs, which the "What comes next" table lists.

### n7. What was found right, in brief

**Interim integrity:**
- 356 / 350 / 6;
- S 95 / 1 / 0 / 0 / 0, M 23 / 1, N 7 / 1;
- 0 overflow events and 0 crash events;
- near misses in all three arms, with the largest horizon 24: all 24 slots, no overflow (OVERFLOW-RULE §1);
- the build PASS on the registered sha;
- the gate re-check PASS.

**Skipped counts:** M 23 − 15 − 0 − 0 − 0 = **8**; N 7 − 2 − 0 − 0 − 0 = **5**. "Done" includes the seed-rule skips (drivers adversary R-9).

**R4 list and bound:**
- 10 points, cap 11;
- 180.6 / 338.1 core-h against the plan's 221.0 / 413.9;
- 2B2A COMMITTED on 3 October, before any 2a data (OWNER-DECISIONS-2026-10-03b).

**The excluded unit** (QUARANTINE.md):
- the S60 phase stood at season 38;
- the gap in `s60_compare`;
- the probable pre-merge extinction, "not judged";
- per-folder exclusion of 6 jobs, with 15 that ran;
- S60 retained and unread;
- "EXCLUDED" with no crash event;
- P-1 before 2b;
- the owner's first-hand approval.

**The lane ran clean:** 15 of 15, 0 overflows, 0 refused (`327dfcfa`).

**Interim provenance** (#560):
- the 30-minute kill;
- the owner-authorised re-run, exit 0;
- one benign line, a cut-short restore redone through the sentinel;
- APPROVE-WITH-NITS;
- counts reconcile, the bound recomputes, no call printed, SKIPPED for disclosure.

**RB-HELP-1** (H6 disclosure complete):
- the overflow in S60, then two non-native failures;
- the blocked trace, not worked around;
- the owner's approval;
- OVERFLOWED and INCOMPLETE, n 15 of 16;
- one ceiling event;
- never re-run;
- ruled before any R-B outcome.

**COORD-RULING-527:**
- T4: 8 M forks, 140 / 262 → 153 / 286;
- T1: the build's independent rebuild with the same sha, and the forced overflow logged 10 of 10.

**A7 and OWNER-DECISIONS-2026-10-04 item 1:**
- 37 of 37 IDENTICAL and CLEAN over seasons 60–299;
- the crashed unit excluded;
- the S60 phase and the S arms UNSCANNED;
- the S scan DEFERRED until 2a's overflow count, which is now 0.

**DISCLOSURE-2026-10-03:**
- the bare fetch of 2 October;
- downloaded and never read;
- caught by the guard test;
- the local ref deleted on 3 October at 14:30Z, before report 2's 15:00 UTC cut-off.

**OWNER-DECISIONS-2026-10-04 item 4.** Both forward corrections are present (see m5 on their placement).

**The W1 gate** (READOUT-NOTES, verbatim rows):
- G1 0/16 at the first paying rung, a = 2, the weakest of {2, 6, 16, 32}, with the ≥ 12 of 16 bar;
- G8(c) 0.000 pooled and 0 of 24 units, against ≥ 20% and ≥ 18 of 24;
- G8(b) 1 of 35;
- 24 units flagged (> 4: no launch);
- G2 +0.426 against +0.184;
- G4 0 of 200 for each kind;
- G7 PASS;
- the G8(c) caveat in W1_GATE_AMENDMENT before any data;
- the adversary's "FAIL rows genuine" (`5d791cb9`).

**RBT116-PILOT-10:**
- ruled after the refusal, knowing neither count;
- pooled over measured units, with nothing re-run;
- fallback A;
- 105 against 7.

**RBT116-S2:** G1's first-rung rule and G8(c)'s layout are not changed; later variants are exploratory; a new point is an owner decision.

**I5-a:**
- the agent sham against own-food for the sensor-blind conditions;
- against B0's food count for C+ and P5;
- a failure VOIDs;
- ruled pre-data.

**RBT-134:**
- 84 arrivals reading 0 at every rung;
- the product ≤ 3.68 at the default step;
- the bias mechanism at σ 4.0;
- P2 and P3 the tested family, with four bounded checks;
- the census routes (a) and (b);
- registered 4 October, 02:13 UTC (#538/#539);
- the code merged with no condition run (#541).

**Stage-2 plan:**
- 12 points by R-A, registered in DESIGN §4.2 before Stage 1;
- 8 seeds and 300 seasons;
- M at 3 points and N at 1;
- T4 NOT MEASURED, p = 1, from the calibration's UNREADABLE at a = 6.

**Report 2's next steps:** there are four, and each is followed up.

**Prior art:**
- Conrad, Bongard & Paul and Braitenberg match REVIEW.md;
- the second-route Braitenberg gloss matches RBT-134 DESIGN §0 item 5(b);
- the upstream MuJoCo issue is linked by URL, without a bare number.

**House rules:**
- no tracker IDs, PR numbers, session IDs or AI model names on the page;
- study titles are used, and "W1", "2a" and "2b" are glossed;
- pending items are stated, subject to n6.

**HTML:**
- tags balance and there are no duplicate ids;
- no scripts, images or external resources other than Google Fonts;
- dark tokens are defined under `prefers-color-scheme` with the `:not([data-theme="light"])` guard, and again under `[data-theme="dark"]`;
- `color-scheme` is set in both themes;
- there is no page-level horizontal scroll at 390 or 1280 px in either theme (but see m9).

---

## Re-check (fixes at `5003d935` and `378e1372`)

- **Re-checked:** the page, `docs/index.html`, the README row and the new `runs/RBT-129/coordinator/OWNER-DECISIONS-2026-10-05.md`, on `claude/happy-ramanujan-0jka04` at `378e1372`, against this review at `46cf87c8`.
- **Same no-peek rules.** Nothing new was opened beyond the committed docs and commit messages.

### Final verdict: **PUBLISH WITH FIXES**

- Every original finding is FIXED.
- No MAJOR is outstanding.
- Two new MINORs remain, R1 and R2. Each is a one-line edit that needs no further review.

| finding | status | how |
|---|---|---|
| M1 the W1 meaning | FIXED | both bodies named (0 of 16; 0%), and the false positive added; "That is all" kept |
| M2 the exposure label | FIXED | "It is labelled as made after the coordinator's exposure disclosed in report 2." The proxy's role is stated in the sentence before it |
| M3 the sources | FIXED | the new decisions record holds the 5 October decisions, A′, 2a complete on 7 October, the interim's provenance and the operator study's status; the footer cites it. But see R2 |
| M4 the card | FIXED | the card is in `docs/index.html` above report 2's, links `progress-reports/2026-10-11/`, and says "no call is printed"; the README row now matches |
| m1 "any result" | FIXED | lede and brief now say "no call" |
| m2 the list caption, survival counts | FIXED | both sentences as proposed |
| m3 2b's second part, merged runs | FIXED | L109, L154, the brief and the next table |
| m4 the pilot's reading | FIXED | "As the gate's code first read the registered rule"; "or which kind refused" added |
| m5 the rematch and operator rows | FIXED, with a new error | the rows are split, but the new rematch text is unsourced (R1) |
| m6 "the next study" | FIXED | names the operator study |
| m7 Lehmacher and Wassmer | FIXED | full reference given. I did not re-verify it against the publisher here; it matches the standard citation |
| m8 the scratch start | FIXED | |
| m9 phone tables | FIXED | at 390 px every table wrapper is 334 = 334 in both themes, and all six integrity columns are visible. "Overflowed, unlogged and crashed: 0 in every arm" is in the caption, and `td.when` wraps |
| m10 the first interim run | FIXED | |
| m11 "any 2b data" | FIXED | both places |
| n1 blinding | FIXED (m2) | no new Stage-2 information; the 10 points and counts are unchanged |
| n2 the withdrawn ruling A | FIXED | page parenthetical, plus decisions record item 2 |
| n3 the fail-closed write | FIXED | |
| n4 the core-hours held | FIXED | page and record: about 88 spent, the arms' 400–590 held |
| n5 W1's wording | FIXED | "normal clutter"; "kept, rather than replaced by a point picked from Stage 1's map" |
| n6 the coincidence, as-of and pending | FIXED | the parenthetical on the scratch start; "AS OF 9 OCTOBER, 01:00 UTC"; operator runs added to Pending |
| n7 | — | nothing to fix |

### New findings

**R1 (MINOR, page, Corrections, rematch row).** The new text reads:
> The rematch is unchanged: it waits on the final map.

- It is unsourced, and I suggested it in m5 only as an example. I should have checked it first.
- `DESIGN.md` §9.1 gives the rematch three fixed anchor points (W118-a/b/c), plus "rule-chosen points (at most two, chosen by script after Stage 1)" from Stage 1's BH-significant income effects. So it does not wait on the final map.
- No registration for the rematch is committed: `runs/RBT-118/` holds only `prior/` and `prior-adversary/`.

**Replace with** (sourced):
> The rematch is not yet registered. The sweep’s design gives it three fixed points and up to two more, chosen by script from Stage 1’s results.

Alternatively, "Unchanged since report 2", if the coordinator can confirm that and record it.

**R2 (MINOR, decisions record, item 2 time).** Item 2 dates ruling A′ to "~21:45 UTC". But commit `7ebd66ff`, which records the ruled line and its text, is dated 21:35:58 UTC on 10-05. So the ruling cannot postdate its own record.

**Fix:** "~21:30 UTC", or "by 21:35 UTC (`7ebd66ff`)". The page gives no time, so the page is unaffected.

### Checked and clean

- **New page wording traces:**
  - "background time limit in the session's harness";
  - "designated readout session" (#560 and record item 4);
  - "an action by the operator of its design session" (record item 5);
  - the 88 and 400–590 (OWNER-DECISIONS-2026-10-04 item 2);
  - "has since merged" (#541).
- **The page has no IDs.** It carries no tracker IDs, PR numbers, session IDs or AI model names. The session IDs in the decisions record are in a repository doc, as in the earlier coordinator records, not on the page.
- **HTML:**
  - tags balance in the page and in `docs/index.html`;
  - the scroll-shadow backgrounds use `var(--paper)`, so they follow the theme;
  - the 520 px block is inside the existing media query.
- **Rendering**, in Chromium at 390 and 1280 px, light and dark:
  - no page-level horizontal scroll (`scrollWidth` = `clientWidth`);
  - no element past the viewport;
  - explicit body backgrounds `rgb(246,247,244)` and `rgb(20,24,32)`.
