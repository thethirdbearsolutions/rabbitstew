# Progress report 2: adversary and fact-check

- **Reviewed:** `docs/progress-reports/2026-10-04/index.html` on `results/RBT-119-report2` at `d3b944278b1c9c8bc1156fe4bf914d597654752f` (PR #398, draft).
- **Sources read:** on `claude/new-session-4cao7d` at `b8e6a01` (after #525). This file edits nothing on the report branch.
- **Sources checked:**
  - `runs/RBT-121/SYNTHESIS.md`, `adversary/SYNTHESIS-CHECK.md` and `history/HISTORY.md`;
  - `runs/RBT-113/REPORT.md` (the benchmark) and `runs/RBT-120/REPORT.md`;
  - `docs/paper-10-held-not-spread.md`;
  - `docs/prior-art/REVIEW.md` and `citation-check/CHECK.md`;
  - `runs/RBT-129/DESIGN.md`;
  - `stage1-readout/`: READOUT-STAGE1, CORRECTIONS A1–A7, COORD-RULING-517 and RULINGS;
  - `mn-crash/`: DIAGNOSIS r2, RULING and COORD-RULING-520;
  - `mn-crash-diagnosis-adversary/ADVERSARY.md`;
  - `coordinator/DISCLOSURE-2026-10-02.md` and `OWNER-DECISIONS-2026-10-03.md`;
  - PR #523, for Stage 2.
- **Rules kept:** no bare fetch or pull, and no `ckpt/` branch read.

**On `stage1_readout.txt`.** The auto-mode permission classifier blocked one direct `grep` of this file. So the 36 map cells were checked against `READOUT-STAGE1.md` §3. That table reproduces the script's per-point header lines field by field, each tagged with its line number (L6–L299), and the run adversary reproduced both files byte for byte (COORD-RULING-517). I did not open `stage1_readout.txt` itself for the cell check, beyond its first lines.

## Verdict: **PUBLISH WITH FIXES**

The page is careful, and most of it traces:
- the Stage-1 framing is provisional throughout;
- the A1 fragility is stated in full;
- all 36 income-map cells are correct;
- the benchmark, the rerun and the audit numbers match their sources.

Four statements are wrong or now stale, and must be fixed before the page goes out:
- M1: the logging build is "identical, overflow included", which contradicts the crash ruling;
- M2: "unlikely" is unsupported;
- M3: a scope error, "across the whole map";
- M4: the "not yet merged" footer is stale.

The MINORs are each a one-line edit.

| severity | count |
|---|---|
| BLOCKING | 0 |
| MAJOR | 4 |
| MINOR | 7 |
| NOTE | 5 |

**Numbers found wrong:**
- "four times on resume" (m1): the unit crashed four times in all, three of them on resume.

**Numbers right but misscoped:**
- the clutter and world-effect tests (M3) cover the 15 habitable points, not the whole map.

---

## MAJOR

### M1. The logging build is not identical to stock at an overflow

**Page** (What changes going forward):
> Its physics is identical to the stock engine, overflow included, so new runs stay comparable with Stage 1, but no overflow can now pass unseen.

**Evidence.** `mn-crash/COORD-RULING-520.md` D3, FC-2, adopted by the coordinator:
> The log-only build is byte-identical to stock **on non-overflowing trajectories**. At an overflow, both builds are undefined behaviour and build-specific, so post-overflow behaviour is not evidence about stock. **The `RBT_HZN` overflow record is the reliable signal.**

DIAGNOSIS (c)'s "UB included" is the wording that FC-2 corrected. The page repeats the superseded form.

**Replace with:**
> On runs without an overflow its physics is byte-for-byte identical to the stock engine, so new runs stay comparable with Stage 1. At an overflow neither engine's behaviour is defined, so what follows one is not evidence about the stock engine. What counts is the logged record of the overflow, and a rule registered in advance says how such a run is handled. No overflow can now pass unseen.

Then extend the next sentence:
> Before anything launches on it, the build must be reproducible from a committed recipe and shown identical to the stock engine, and every launch must check that the engine it loads is that registered build.

The last clause is FC-3.

### M2. "Unlikely" is not supported

**Page** (What it means for the results):
> So silent corruption elsewhere in Stage 1 is unlikely but not yet ruled out.

**Evidence.**
- `READOUT-STAGE1-CORRECTIONS.md` A7 and COORD-RULING-520 D2 say only "**not ruled out** outside the scanned coverage".
- DIAGNOSIS (d): "Not ruled out: a silent overflow anywhere else in Stage 1. That covers roughly 1e5 unit-seasons." The scans cover 90 + 528 + 240 = 858 unit-seasons, under 1% of that.
- DIAGNOSIS (e): "One observed overflow in roughly 1.0–1.4e5 unit-seasons to date, plus an unknown number of silent ones". It also retracts the r1 tail extrapolation: "That extrapolation must not be used for any rate."
- Near misses reach 23 against a cap of 24, in ordinary S and M units.

So no committed source quantifies the chance of silent corruption in Stage 1. The one rate it gives (about one overflow per 1e5 unit-seasons, over a stage of about 1e5) does not make a second, silent one "unlikely".

**Replace with:**
> One overflow has been seen, and it crashed. Scans of about 860 run-seasons, under 1% of Stage 1, found no other, but they did find near misses of 23 edges, one short of the limit, in ordinary runs. So silent corruption elsewhere in Stage 1 is not ruled out, and the scans so far cannot say how likely it is.

### M3. The world-effect and clutter tests are not "across the whole map"

**Page** (The provisional result):
> Clutter moves the balance. Of the registered tests across the whole map, the overall test that the world matters rejects "no effect" (p 1 × 10⁻¹³), and so does the test for clutter: each step up in clutter shifts the income difference towards the evolving bodies by 0.50 [0.28, 0.72].

**Evidence.**
- `READOUT-STAGE1.md` §6, M2: "**The fit.** 15 habitable points, 100 seeds", with the dropped term "L = PW (no habitable PW point)".
- T1, T2 and T3 are tests within that fit. The values are right: T1 p 1.181e-13, c +0.5022 [+0.2800, +0.7243], and T3 z −0.789.
- But they are fitted only where both kinds establish, which are the same 15 points at which the fixed body wins every call (A1).
- A reader of "across the whole map" would take the clutter trend to cover the sparse-patch and dear-work corners. It does not.

**Replace with:**
> Clutter moves the balance. In the registered model of income, fitted at the 15 points where both kinds establish, the overall test that the world matters rejects "no effect" (p 1 × 10⁻¹³), and so does the test for clutter: each step up in clutter, from flat to normal or from normal to double, shifts the income difference towards the evolving bodies by 0.50 [0.28, 0.72]. The price of work shows no clear effect (z −0.79).

Optionally, add "against the registered prediction that dearer work favours the evolving bodies" (scorecard L609: NOT SHOWN).

### M4. The crash diagnosis is now merged and ruled: the footer and the as-of stamp are stale

**Page** (Sources footer):
> All are in the project repository; the crash diagnosis and its review are still open, not yet merged.

The masthead reads "AS OF 3 OCTOBER, 13:00 UTC".

**Evidence.**
- #520 merged at `d4212f0` and #521 at `6ef42d8`.
- COORD-RULING-520, ruled ~13:00 UTC and merged in #525 at `b8e6a01`, accepts the root cause (D1), adds disclosure A7 (D2) and adopts FC-2 and FC-3 (D3).

**Replace the footer's last clause with:**
> …the diagnosis of the crashed run, its independent review and the ruling on them; and the simulator's code (…). All are in the project repository.

**In "A bug in the physics engine".** After "not in our code", add:
> The diagnosis passed independent review, and has been accepted.

**Masthead.** Move the as-of time to when these fixes land, for example "AS OF 3 OCTOBER, 15:00 UTC".

## MINOR

### m1. The crash count: four crashes, three of them resumes

**Page:**
> …on one seed crashed inside the physics engine, four times on resume and again on a second machine.

**Evidence.** `mn-crash/RULING.md`:39–42: "Four attempts, four native crashes … Attempts 2–4 were resumes." `integrity.txt` I-6 reads `x4`.

**Replace with:**
> …crashed inside the physics engine four times, once in the run and then on each of three resumes, and again on a second machine.

### m2. The map legend's "neither failed to establish" says the opposite of what it means

**Page** (figure legend):
> no E, no F, none: the evolving bodies, the fixed body, or neither failed to establish on most seeds, and income could not be tested.

"Neither failed" means both established. The cells marked "none" are NEITHER body calls (READOUT §3: L73, L123, L148, L199, L223, L273, L299), where neither kind established.

**Replace with:**
> no E: the evolving bodies failed to establish on most seeds; no F: the fixed body did; none: neither kind established. At these points income could not be tested.

Keep the E* footnote as it is.

### m3. "Word for word" is not word for word

**Page:**
> Every Stage-1 call carries this label, word for word: "among holistic and designed stream draws … that establish at W118-b; earns, not persists; provisional, not a verdict".

**Evidence.**
- READOUT §8 reads "*Among holistic and designed stream draws (founders and their early history) that establish at W118-b; earns, not persists; provisional.*"
- §1 reads "*provisional: Stage-1 calls only; not a verdict.*"
- The page splices the two, and elides the middle.

**Replace with:**
> Every Stage-1 call carries this label: "among holistic and designed stream draws (founders and their early history) that establish at W118-b; earns, not persists; provisional", and the whole stage is "provisional: Stage-1 calls only; not a verdict".

Keep the plain-language gloss that follows. Alternatively, drop "word for word" and keep the ellipsis.

### m4. "Only where they barely live" overstates

**Page:**
> …the evolving bodies earn more only where they barely live.

**Evidence.**
- At `c1-p080-HP-L` (PARTIAL-D), the evolving bodies are alive at season 59 on 6 of 8 seeds (READOUT §9), and income-valid on 3.
- A1 and Observation 5 say "points where H does not persist", not "barely live".

**Replace with:**
> …the evolving bodies earn more only at points where they do not persist.

### m5. The disclosure sentence claims more labelling than the record shows

**Page:**
> The readout plan and its script were written and committed before any Stage-1 output was opened … The plan had already been committed, and every later ruling by the coordinator is labelled as made after that exposure.

**Evidence.**
- `DISCLOSURE-2026-10-02.md`: the plan-only commit `a250b72` (19:26 UTC) and COORD-RULING-512 (~20:20) came before the 20:45 exposure.
- "Any coordinator ruling **on the plan** made after 20:45 UTC is labelled COORDINATOR-EXPOSED."
- COORD-RULING-517 carries the label. COORD-RULING-520 (crash diagnosis) does not.
- The plan's final fix-check round, `f000c2c` (21:13), was committed after the exposure, by sessions that were not exposed.
- So "every later ruling" is too broad, and "committed before any Stage-1 output was opened" needs "by its authors".

**Replace with:**
> The readout plan and its script were written by sessions that never saw any Stage-1 output, and the integrity check was committed before the readout ran. One slip is on the record: on 2 October, before the readout, the project's coordinator saw one aggregate count from Stage 1. It was disclosed the same day. The plan had first been committed, and the coordinator's ruling on it made, before that exposure. The coordinator's later ruling on the readout, which adopted the corrections below, is labelled as made after it.

### m6. Upstream issue and PR numbers on the page

**Page:**
> Others have reported it (google-deepmind/mujoco#3646), and a fix is proposed but not yet merged (#3650).

The house rule is no tracker IDs or PR numbers on the page. The PR body calls these intentional, but the rule makes no exception, and a bare "#3650" reads as one of ours.

**Replace with**, with links:
> <a href="https://github.com/google-deepmind/mujoco/issues/3646">Others have reported it upstream</a>, and <a href="https://github.com/google-deepmind/mujoco/pull/3650">a fix is proposed</a> but not yet merged.

### m7. The integrity pass needs its A7 qualifier where it is stated

**Page** (Stage 1 is complete):
> All 973 units are accounted for, and the integrity check passes: …

**Evidence.** A7: "The integrity verdict (I-1, I-15) stands as scripted. **This annotation qualifies it.**" The qualifier is only reached three sections later.

**Append:**
> …and all 72 reproducibility checks pass. One qualification, explained below: a bug in the physics engine that can corrupt a run without crashing it has not been ruled out.

## NOTE

### n1. Stage 2's status

**Page:**
> The plan is written and under independent review.

PR #523 was opened at 12:14 UTC today, and no adversary file is committed yet.

**Safer:**
> The plan is written, and goes to independent review before anything launches.

Also, the plan proposes that perception is not measured at Stage 2 either, so T4 enters at p = 1 permanently. If that is ruled, the next report should say it.

### n2. Two pieces of the design were set after data were seen

**Founder screen.** It was adopted after the census and pilot were read. `DESIGN.md`:1410 is labelled "**DATA-INFORMED**". The page's "The design went through several rounds of independent review before anything ran" is true of Stage 1, but a reader may take the screen to be pre-data.

**Suggest adding** to "Seeds":
> The screen was added after a brief census and a pilot had been read, and is labelled as such.

**The R-B extension.** It is likewise DATA-INFORMED (COORD-RULING-512 R4). In "What comes next", consider adding "chosen after Stage 1 was read".

### n3. The nose figure is unresolved from zero

**Page:**
> …against 0–10% for a one-step better nose…

SYNTHESIS R4 adds that it is "unresolved from zero at the calibrated cell".

**Optional:**
> …against 0–10% for a one-step better nose, not distinguishable from zero at the committed setting, …

### n4. The 55–75% estimate rests on one event

DIAGNOSIS (e): "a Jeffreys-prior posterior on one event, so the intervals are very wide."

**Optional:**
> The review's rough estimate, from a single event, is a 55–75% chance…

### n5. The index card and README row

The links are correct:
- the README row points to `…/progress-reports/2026-10-04/`;
- the `docs/index.html` card points to `progress-reports/2026-10-04/`.

The headline is fair. Consider adding "on thin evidence for the evolving bodies" after "depends on the world", to match the hero.

---

## What was checked and passed

**The 36-point map.** Every cell agrees with READOUT §3 (L6–L299):

| world | rows read |
|---|---|
| Uniform · new channel | FFF / ??? / ??noF |
| Patchy · new channel | ?FF / ?F? / ??noF |
| Sparse · new channel | noE noE none / noE none none / noE none none |
| Legacy, normal clutter | ??? / ??E* / E* none none |

- The six F cells are the six EARNS-D calls (L6, L31, L39, L57, L65, L115). Their leads, 0.386 to 1.653, round to "0.39 to 1.65".
- The two E* cells are L247 and L290.
- The figure is captioned "provisional", and sits under a "provisional" section label.
- F is shown in the page's "solid" green, and E in the "new" amber. Both are muted and labelled with a letter, so colour is not the only cue. The amber E* cells are the most salient on the grid, but the asterisk and footnote put them in context. Acceptable.

**A1 fragility.** Stated in full:
- 2 EARNS-H calls, both at non-habitable points, on 2 and 3 seeds;
- p 0.0335 against 0.0348, a margin of 0.0013;
- no EARNS-H at the 15 habitable points;
- DEPENDS ONLY THROUGH HABITABILITY, as non-registered;
- the final BH after Stage 2 can change it.

**Other Stage-1 items:**
- A3: MARGINAL is a censoring artefact.
- A4 and K2: the share layer is VOID, and no call changes.
- "Perception was not measured".
- 973 units, 72 of 72 K-SALT, M at 9 points, N at 4, M 7 of 8.
- K = 23 points tested, the |x̄| ≥ 0.10 threshold, and income tested at ≥ 2 seeds (O-11).
- 150 = 5 × 5 × 3 × 2, a census of 3 seeds × 60 seasons, 36 points at 8 seeds × 300 seasons.
- W118-b is `c0-p030-U-L`, which matches "flat ground, the committed price, uniform food, legacy smell". The founder screen is ≥ 30 of 60 at season 59.

**MuJoCo, apart from M1 and M2.** These match DIAGNOSIS and COORD-RULING-520 D1:
- `int[24]` and 25 edges;
- about 0.1 m of overlap against parts of 0.1–0.16 m;
- no NaN or Inf;
- reproduced on 4 hosts;
- the list grew with the step limit up to 3.7.0, and is fixed at 24 from 3.8.0;
- 55–75%;
- about 100 and 600–800 core-hours;
- R-B: 9 points, 8 more seeds, 140–262 core-hours, with its gates (OWNER-DECISIONS).

**Benchmark** (RBT-113 REPORT §1–§4, as amended under its ruling):
- divergence +0.095 [0.083, 0.107] and +0.038 [0.027, 0.048];
- h² 0.093 [0.080, 0.106] and 0.067 [0.061, 0.074];
- founder SD 0.22 and 0.75;
- the food and work table;
- 10.6×, 0.91 / 0.93 / 0.85, 61%, about 6×, 45.9×, 94%, about 10×, 98%, about 2×;
- the fixed body's response is 77% food;
- +0.77 [0.40, 1.13] on 11 of 12 seeds, p 0.0015;
- capped −0.02 (p 0.86), up half +0.11 (p 0.53), food −0.42 (p 0.010);
- operator −0.001 [−0.012, +0.009].

The binding caveats (scope sentences 2–4, and the M1 mechanism) are all carried.

**Rerun** (RBT-120 REPORT, CONFIRMED WITH CAVEATS):
- +0.0712 [0.0600, 0.0824] on 12 of 12 seeds, 73% [57%, 95%];
- 27% [5%, 43%];
- Q3 +0.126 [−0.194, +0.446], with food tied;
- the D line's work 1.58 → 0.73;
- 92% contact-free;
- no joint ranges.

The scope sentence ("not without every lever") is reflected.

**Audit** (SYNTHESIS as corrected, and HISTORY:197–205):
- the headline;
- 30.3 / 1.7605 ≈ 17;
- 97%, 94%, about a third;
- 14 of 120, partly terrain rolling;
- +0.7;
- 13–40% and 0–10% in 18 cells;
- 60% starve;
- 5× erosion;
- 73 = 23 + 14 + 12 + 11 + 7 + 6;
- "none caught before the run";
- 21 of 29.

**Corrections to report 1** (paper 10):
- the size 2.2 × 10⁻⁴;
- about 10⁻¹⁶ at q 0.013;
- 0.0127 at depth 16;
- the "No s was estimated for HP" quotation, verbatim (paper 10:509–511).

**Prior art.** Each entry matches REVIEW.md as revised under CHECK.md:
- Sims 1994a, SIGGRAPH ’94: 15–22;
- Sims 1994b, *Artificial Life* 1(4): 353–372;
- Conrad 1990, *BioSystems* 24: 61–81;
- Bongard & Paul 2001, LNCS 2159: 401–412, softened per F5;
- Watson, Ficici & Pollack 1999, CEC: 335–342, with the full title;
- Bredeche, Haasdijk & Prieto 2018, *Frontiers* 5: 12;
- Cheney, Bongard, SunSpiral & Lipson 2018, *JRSI* 15: 20170937;
- Mertan & Cheney 2026, *Artificial Life* (E5);
- Lehman et al. 2020, 26(2): 274–306;
- Taylor & Massey 2001, 7(1): 77–87;
- Krčah 2008, ICES, LNCS 5216: 153–164;
- Cheney et al. 2013, GECCO: 167–174;
- Auerbach & Bongard 2014, *PLoS CB* 10(1): e1003399;
- Pagliuca & Nolfi 2022, 30(3): 245–255;
- Falconer & Mackay 1996, 4th edition, Longman;
- Braitenberg 1984;
- Salmon 2003.

The prose is also consistent with CHECK.md: 106 DOIs, no phantoms, quotations verbatim, the F1 per-DOF correction, and the F3 and F3b novelty hedges.

**House rules:**
- No tracker IDs, PR numbers of ours, session IDs or owner references, apart from m6 (upstream numbers) and the quoted label's "W118-b", which the page glosses.
- The page never refers to its intended reader.
- Rendered in Chromium 1194 (Playwright), light and dark, at 900 and 390 px:
  - `scrollWidth` equals `clientWidth` in all four views;
  - no element extends past the viewport;
  - the body background is explicit in both themes (`rgb(246,247,244)` and `rgb(20,24,32)`);
  - the map's four grids stack to one column at 390 px with no clipping.
- `git diff --stat` against the base touches only `docs/`: `docs/index.html`, `docs/progress-reports/README.md` and the new page.

---
_Generated by [Claude Code](https://claude.ai/code)_
