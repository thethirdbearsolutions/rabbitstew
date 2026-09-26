# RBT-100 adversary re-check of round 1, on integration `a65c492` (PR #103 merged)

I read Amendment 1, Amendment 2 and Amendment 2 continued in `runs/RBT-100/PREREGISTRATION.md`, together with `readout.py`, `own_table.py`, `founders6.sh` and `tests/test_rbt100_readout.py`.

**Checks run:**
- `pytest tests/test_rbt100_readout.py`: 6 passed.
- `split_deaths` and `own_table.py` on my P1 bulk (seed 901, T = 100):
  - `own.txt` reconciles on 318/318 cells for both arms;
  - `split_deaths` totals equal the history deaths exactly: 164, 427, 90 and 114 over [T, T+59), for shift holistic, shift designed, plain holistic and plain designed.

## Erratum to my round 1: my P1 cause-by-cohort counts were wrong

My `probe_read.py` §3 took the last lineage row as the death season, and it used an energy test for cause. The dead have no row for the season they die in, so the last row is the season *before* death. The designer's `split_deaths` handles this correctly.

**Corrected P1 counts, designed, over [T, T+60):**

| arm | starved recruits (born ≥ T) | starved residents | aged out |
|---|---|---|---|
| shift | **371** (I posted 267) | 31 (I posted 21) | 29 (I posted 28) |
| plain | 57 (I posted 31) | 10 | 50 |

The direction of F1 stands, and it is stronger. `probe_read.py` is fixed and `probe_read.txt` regenerated.

**§3.3 of the pre-registration quotes my wrong "267".** It should read 371. That is text only; no rule depends on it. Under the rescored claim 3 (split over [T, T+30)), P1 gives:
- recruits' excess +131 (shift 154, base 23);
- onset cohort's excess +12;
- so "yes".

## F1: fixed. Confirmed.
- §3.3 is rewritten: hoarding residents, starving recruits, collapse at T+40 or later. The "3 to 30 seasons" text is marked as superseded.
- UNDERSIZED is dropped and its prediction is withdrawn.
- NULL is diagnostics only: deaths split by cause and cohort from committed `lineage-last.txt`, and the alive deficit to T+100.
- The turnover guard is not interpretable a priori.
- Claim 3 is rescored on a criterion the arm can show, and is labelled as proposed after P1.
- `split_deaths` is verified above against true deaths.

## F5: fixed. Confirmed.
- **Ten founders-at-six arms** (`founders6.sh`: 60 seasons, the P2 command lengthened to one `max_age`). Founders HOLD if ≥ 12 co-evolved robots are alive at season 59.
- **The survival reading is the recovery window's only.** The established fauna HOLDs if min alive ≥ 12 over [T+60, T+160) and the survivors' own net is ≥ 0.25.
- **The contrast sentence prints only where the founders FAIL and the established fauna HOLDS.** Otherwise it prints "no contrast" or "no".
- A small caveat, not a blocker: the established HOLD uses the survivors' own net, which is survivor-conditioned (F3). It is paired with a min-alive floor held over 100 seasons, a stricter alive test than the founders' single-season one. I would keep it and say so in the report.

## F6: fixed and pinned by test. Confirmed.
`verdict_text` prints:
- the C3 and C2 claim lines and the §3 statement verbatim, which `test_quoted_claim_lines_and_statement_are_verbatim_from_the_protocol` checks against the doc;
- the owner's falsifier wording;
- "outlasts a bankrupt comparator" on D unless R-shift ≥ −r, with an unknown (nan) R-shift never reading as "holds up";
- forbidden readings 12 and 13.

The D, A and C sentences and the parse of part 1 are tested.

## Is P2 handled honestly in the restated claim? Yes in the pre-registration, with one gap in the readout.

The pre-registration handles P2 honestly. Amendment 2 continued:
- states plainly that random co-evolved founders cross six items on 2 of 4 seeds, and that the protocol's premise rests on one seed on the old generator;
- demotes the founders contrast from premise to a per-seed measurement;
- keeps the protocol's claim line verbatim instead of editing the protocol, but reads its founders clause per seed;
- adds a post-P2 prediction, labelled as such (founders HOLD on ≥ 3/10, 0.7);
- leaves the class probabilities untouched, which is correct: P2 bears on founders, not on the established response;
- commits the report to saying "C3 on this head answers the survivorship question, not the bootstrap-line question" if founders HOLD on most seeds.

**The gap:** that last sentence exists only as an instruction to the report writer. The readout does not print it.
- VERDICT TEXT prints the claim line "whether an established population holds where random founders could not" verbatim, with no per-seed qualifier beside it.
- "Most" is undefined.
- F6's point was that the readout itself carries the sentences the protocol requires.

**Fix before the readout runs** (text only, not a launch blocker):
- After the claim line, print "read per seed on founders6: founders HOLD on h/f seeds read; contrast on c/(f − h)".
- When h ≥ ⌈f/2⌉, also print: "C3 on this head answers the survivorship question, not the bootstrap-line question."
- Add a test.

## Verdicts after the re-check

| | round-1 verdict | now |
|---|---|---|
| F1 | must fix before launch | **fixed**. The P1 number quoted in §3.3 needs correcting from 267 to 371 (my error; text only) |
| F2 | report caveat | stated in §3.3 and in NULL's header |
| F3 | caveat plus a table | **built**. The upper bound in place of a mean is honest: the dead have no row. It is narrower than I asked, and says so |
| F4 | fix the text | fixed |
| F5 | must fix before launch | **fixed** |
| F6 | must fix before the readout | **fixed and tested**. One follow-on: print the per-seed founders qualifier and the "survivorship, not bootstrap line" sentence beside the claim line (before the readout; not a launch blocker) |

**On what is C3-specific, I have no remaining launch blocker.** The answer took every finding and argued none away. It also caught a real error in my own probe, and its instrument is the better of the two.
