# Errata

This is an index of **superseded figures, labels and claims** in the programme's record, listed by the file and line where a reader will meet them. Each entry gives what the file says, the correction, where the correction was made, and the date of the correction.

**Why it exists.** A correction is usually made in a *different* file from the one that holds the figure: an adversary report, a later paper, a ruling, a later ticket. Readers of the original file never see it. Auditor D (`runs/RBT-121/history/HISTORY.md`, P6) found about 75 such places across 76 incidents, H1–H76. This file puts the pointer next to the old figure.

**The rule.** Superseded text is **never edited in place.** Papers, reports, registered outputs and published progress reports stay as they were written; registered code is not changed after its readout (RBT-121 R11). The correction lives here and in its source. A **later** revision of a paper may fix its own text; when it does, keep the entry and add "fixed in `<file>` at `<sha>`".

**Platform records are evidence.** From RBT-127 on, every new run writes `platform.json` beside `config.json`: the OS, CPU model, Python, MuJoCo and numpy versions, and the git sha. It is tracked (`.gitignore`, `runs/README.md`), and a results PR commits it with the run's `config.json`. A runner's evidence allowlist should include it.

**Quoting rule.** Anyone who quotes a figure or label listed below must quote the correction with it. For a registered label, that means its ruled gloss (RBT-121 R14).

## How to add an entry

1. Find the table for the document's kind (papers, published reports, registered outputs, reports, docs, commit messages). Add a sub-heading for the file if it has none.
2. Add one row per location: **file:line** at the current head (check it with `sed -n '<line>p' <file>`), **what it says** (a short quotation), **the correction** (one or two sentences; for a registered label, the ruled gloss), **source** (the file:line, ruling or PR that made the correction), and **the date** of the correction (YYYY-MM-DD, UTC).
3. When a line number moves because the file was revised, update the row. Do not delete it.
4. Cite the source, not this file. This file is an index; it is not itself the authority for any correction.

**Conventions.**
- File and line numbers were checked against the tree at `dc57055` (2026-09-27). Every cited file is byte-identical to `152e2df`, the tree auditor D read, so HISTORY.md's line numbers hold except where a row says otherwise.
- Abbreviations: P3 `docs/paper-3-let-the-furniture-stop-me.md`, P4 `docs/paper-4-designed-quadrupeds-and-evolved-lumps.md`, P5 `docs/paper-5-the-blind-forager.md`, P6 `docs/paper-6-the-cow-is-the-correct-answer.md`, P7 `docs/paper-7-five-instruments.md`, P8 `docs/paper-8-the-prize-the-proposal-rate-and-the-magnitude-gap.md`, P9 `docs/paper-9-net-of-arithmetic.md`, P10 `docs/paper-10-held-not-spread.md`. "HISTORY" is `runs/RBT-121/history/HISTORY.md`; "REVIEW" is `docs/prior-art/REVIEW.md`; "CHECK" is `docs/prior-art/citation-check/CHECK.md`. `H<n>` is D's incident number and `E<n>` is REVIEW §8's erratum number.
- **Dates.** A date is the day the correction was made, taken from git or the ticket. The clone these were checked in is shallow (grafted at 2026-09-26), so older dates come from the tickets, from GitHub's commit history, or from HISTORY's date table. Where they disagree, the commit date is used. The rows sourced to `runs/RBT-38/REPORT.md` are dated 2026-09-12, the date of its commits on GitHub, although HISTORY's H22 cites the RBT-38 ruling at 2026-09-14T02:14Z.

**Not listed.** Claims whose own file already carries the correction were left out. For example:
- the follow-up paper's weight-class and spawn-drop figures (H1, H2, H4);
- P3's 0.74 (H6);
- P4's 0.4 best-of-generation (H9);
- P6's density table (H15, H22);
- `runs/RBT-58`'s compass criterion (H33);
- the REPORT.md files amended after their readout adversaries: RBT-74, RBT-85 (in part), RBT-92, RBT-99, RBT-100, RBT-101, RBT-102, RBT-104, RBT-113 and `RBT-107/hrep`.

Their **registered outputs** are listed, because a readout file cannot be amended.

---

## 1. Papers

### Paper 3 (`docs/paper-3-let-the-furniture-stop-me.md`)

| file:line | what it says | the correction | source | date |
|---|---|---|---|---|
| P3:98 | "one seed of two produced it" (holistic steering under condition A) | One steerer in **eight** seeds. P3:93 already says so; :98 and :108 contradict it. (H10) | `runs/RBT-9/REPORT.md:33` | 2026-09-12 |
| P3:108 | "as one seed of two did under condition A" | As above. (H10) | `runs/RBT-9/REPORT.md:33` | 2026-09-12 |
| P3:104 | "the same ancestry-only noise model predicts about 102, so there selection, not drift, thinned the ancestry" | `--founder-model` models tournament selection with two elites. It "says nothing about drift versus selection" under survival or lexicase. (H8) | `runs/RBT-11/REPORT.md:70` | 2026-09-12 |

### Paper 4 (`docs/paper-4-designed-quadrupeds-and-evolved-lumps.md`)

| file:line | what it says | the correction | source | date |
|---|---|---|---|---|
| P4:135 | "the sphere's target-vertical sensor drives one joint axis (weight −0.79)" | The linked unit is 21, **"opponent z"**. In solo evaluation the opponent sensors point at the target (`opponent_proxy`), so this is a second target oracle that no competitive bout offers. (H12) | `docs/lab-cap-403.txt:25,41`; HISTORY:91 | 2026-09-27 |

### Paper 5 (`docs/paper-5-the-blind-forager.md`)

| file:line | what it says | the correction | source | date |
|---|---|---|---|---|
| P5:23 | "the lead reverses at eight robots per arena" | Only the bests reverse. On population income the eight-robot result is **parity, not reversal**. (H26) | `docs/held-out-challenges.md:92-97` | 2026-09-19 |
| P5:92 | "a lead that reverses in a crowded arena (RBT-17)" | As above. (H26) | `docs/held-out-challenges.md:97` | 2026-09-19 |
| P5:244 | "holds at the four-robot baseline and reverses at eight" | As above. (H26) | `docs/held-out-challenges.md:97` | 2026-09-19 |
| P5:44-45 | "(Miconi, 2011; Utimula, 2025)" as "open-ended foraging with no explicit fitness" | **E1:** the EPIA 2011 paper (doi:10.1007/978-3-642-24769-9_10) is by **Tiago Baptista & Ernesto Costa**, not Miconi. P5:46-47 (Miconi & Channon 2006; Miconi 2008) are Miconi's and stand. **E4:** Utimula (2025) is about reproduction and development of 3-D cell creatures, not foraging; P5:69-70 describes it correctly. | REVIEW:578, 581; CHECK:81, 84 (#404, #406) | 2026-09-27 |
| P5:456 | "Miconi, T. (2011). The evolution of foraging in an open-ended simulation environment. EPIA 2011" | **E1:** Baptista, T. & Costa, E. (2011), *Progress in Artificial Intelligence* (EPIA 2011), LNCS: 125–137. | REVIEW:578; CHECK:81 | 2026-09-27 |
| P5:55-57 | "morphological innovation protection … this programme has never run it" | **E7** (REVIEW gives 56-57; the sentence starts at :55): it has, as RBT-74 (`--protect-morphology 4`). The paired verdict was null at four seeds and superseded by RBT-85. The within-run finding stands: a body change costs 0.05–0.13 of bout score, and four controller-only rounds recover none of it. | REVIEW:584; CHECK:87 | 2026-09-27 |
| P5:57 | "Mertan and Cheney (2025)" | **E5:** published online 2026-09-04, *Artificial Life*, doi:10.1162/ARTL.a.476. Cite it as 2026, adding "arXiv:2508.17464, 2025". | REVIEW:582; CHECK:85 | 2026-09-27 |
| P5:58-60 | the co-optimisers "reach morphology-controller pairs that fixed-morphology optimisation cannot, and then discard them" | **E3:** these are two separate findings. Suggested wording: "reaches pairs a fixed-morphology search cannot, yet regularly undervalues newly mutated bodies and eliminates promising morphologies." | REVIEW:580; CHECK:83 | 2026-09-27 |
| P5:189 | "0.246 in the persistent world (RBT-19)" | The persistent arm's standing crop is shared within a season, so its heritability can read high with no inheritance. The share was never measured: "0.246 should not be quoted again until that share is measured." (H25, H75) | `docs/foraging-world.md:309-325` | 2026-09-14 |
| P5:220 | "to 0.246, because patch luck is within-season variance" | As above. (H25, H75) | `docs/foraging-world.md:325` | 2026-09-14 |
| P5:303-305 | the **σ(d) law**: "the redraw truncates the walk at σ(d) ≈ √(1 + 0.0392·d) … the typical link at 16 only around depth 6,500" | The law omits the reset. The walk is **stationary**, at variance 8.84 (rms about 3; measured asymptote 3.016). It stops growing near depth 1,000, and w = 16 is never typical. (H40, H75) | P8:383-401; P8:662 (W6) | 2026-09-26 |
| P5:312-315 | "about one lineage in a thousand at a ≥ 32 … about one lineage in five thousand" | Every rate in this family is computed on the depth-4 path route, the truncation of a divergent series. It "has no value to compute". The direct-motif figure is zero. P5:308-312 retires the 0.70% but not these follow-on rates. (H31) | P7:469-474; P8:660 (W4) | 2026-09-14 |
| P5:316-318 (and the table row at :425) | "in 1 of 16 forty-mutation chains the motif crossed \|a\| ≥ 16 … peaked at 26.5 and ended at 6.1" | The race was read at DEPTH = 4 on brains with ρ > 1. The numbers are not gains and need re-reading at the circuit's depth. (H36) | P8:700-708 | 2026-09-26 |
| P5:414 | "Persistent world, peak forager 5.75 items on 4.2 kJ, heritability 0.246" | As at P5:189. (H25, H75) | `docs/foraging-world.md:325` | 2026-09-14 |
| P5:450 | Chaumont & Adami (2016), with no volume | **E6:** *GPEM* 17(4): 359–390. | REVIEW:583; CHECK:86 | 2026-09-27 |
| P5:453 | "Mertan, A. & Cheney, N. (2025) … *Artificial Life*, accepted" | **E5:** as at P5:57. | REVIEW:582; CHECK:85 | 2026-09-27 |
| P5:461 | Soros & Stanley, Chromaria, with no pages or DOI | **E6:** ALIFE 14: 793–800, doi:10.7551/978-0-262-32621-6-ch128. | REVIEW:583; CHECK:86 | 2026-09-27 |
| P5:463 | Utimula (2025), with no DOI | **E6:** doi:10.1162/artl_a_00466. | REVIEW:583; CHECK:86 | 2026-09-27 |

### Paper 6 (`docs/paper-6-the-cow-is-the-correct-answer.md`)

| file:line | what it says | the correction | source | date |
|---|---|---|---|---|
| P6:112-118 (the phrase at :113) | "all three ride on the **chassis nose alone**" | **False for the brake.** The baseline's season-500 Pioneer wires both wheel noses, one straight onto the drive effectors (a = +0.861, c = −0.861). Only RBT-19 g300 and RBT-10 802-free g590 ride on the chassis nose alone. The free-running lesion that built the brake/throttle/sweep taxonomy fails its positive control (2 of 4). (H37, H75) | `docs/foraging-world.md:282,288`; `runs/RBT-66/REPORT.md:11-15, 94-113` | 2026-09-19 |
| P6:126-128 | "What is rare is the **crossed** circuit a Braitenberg compass actually needs, at **1.3%**" | On the Pioneer the crossed pair (each wheel's nose to the other wheel's effector) **is the pirouette**: −1.502 items, 0 of 7 robots paying at w = 32. The compass is a four-link antisymmetric motif that RBT-45's classifier cannot see. The re-aim at the crossed pairing is withdrawn. (H29, H75) | `runs/sim-audit/CHAOTIC-DOC.md:113-130`; P8:657 (W1) | 2026-09-13 |
| P6:154 | "the smell squash saturated, so range was never tested" | Refuted three times out of three. `i/(1+i)` is strictly monotone and destroys no directional information, and removing it makes the mower worse (1.516 → 1.288). (H20) | `runs/sim-audit/CHAOTIC-DOC.md:182-188` | 2026-09-13 |
| P6:171 | "halved yield heritability from 0.51 to 0.246" | As at P5:189. (H25, H75) | `docs/foraging-world.md:325` | 2026-09-14 |
| P6:209-210 | "a crossed Braitenberg circuit that arrives in **1.3%** of lineages of that depth (RBT-45)" | As at P6:126-128. (H29, H75) | `runs/sim-audit/CHAOTIC-DOC.md:113-130`; P8:657 | 2026-09-13 |
| P6:213-215 | "a circuit that arrives in one lineage in seventy-seven" (1.3% restated) | As at P6:126-128. (H29, H75) | as above | 2026-09-13 |
| P6:399-400 | "RBT-45 measures at 1.3% per lineage … against 9.1% for the uncrossed one" | As at P6:126-128. (H29, H75) | as above | 2026-09-13 |

### Paper 7 (`docs/paper-7-five-instruments.md`)

| file:line | what it says | the correction | source | date |
|---|---|---|---|---|
| P7:38 (abstract) | "the reported **−1.154** was five anti-compasses averaged with two compasses" | The five-and-two split is the w = 32 (a = 64) measurement, whose published figure is **−0.549**. −1.154 is the w = 16 row. The paper's body is right (P7:333, 390); the abstract is not. (H35) | P7:333, 390 | 2026-09-14 |
| P7:309-312 (the figure at :311) | "a yoked phantom-food control … earns +0.163, so the taxis-specific gain is **+0.723, +48%**" | The +0.163 phantom has **no committed script or readout**, and the subtraction does not re-derive: 0.897 − 0.163 = +0.734 (+48.4%). **Do not quote +0.723.** The committed a = 64 phantom is RBT-67's +0.257, on different seeds. (H74) | P8:226-231, 724-725; `runs/RBT-72/rederive.txt:17-18` | 2026-09-26 |
| P7:416-418 | "largest steering gain observed was **2.075** … only **1 chain in 16**" | As at P5:316-318: read at depth 4. (H36) | P8:700-708 | 2026-09-26 |
| P7:781-783 | Cheney, Bongard, SunSpiral & Lipson (2016) "propose morphological innovation protection" | **E2, as corrected by CHECK F2:** the 2016 paper proposes protecting morphological innovations *as future work, with initial results*. The named, tested method (MIP) is Cheney et al. 2018, *J. R. Soc. Interface* 15: 20170937. Cite both, and cite 2018 for the mechanism. The first version of E2 wrongly said the 2016 paper "proposes nothing". **Lines:** the claim is at :781-783 (:780 is blank). REVIEW:579 and CHECK F2 give 780-782; REVIEW's first version had it right. | REVIEW:579 (as amended); CHECK:33 (F2), :82 (#404, #406) | 2026-09-27 |
| P7:784-785 | *Evolutionary Brain-Body Co-Optimization …* "(2025)", with no authors | **E5:** Mertan & Cheney, *Artificial Life*, published online 2026-09-04, doi:10.1162/ARTL.a.476. Cite it as 2026, adding "arXiv:2508.17464, 2025", and name the authors. | REVIEW:582; CHECK:85 | 2026-09-27 |
| P7:786-787 | "finds co-optimisation reaches pairs that fixed-morphology optimisation cannot, while the search discards them" | **E3:** as at P5:58-60. **Lines:** REVIEW gives 786-788 and CHECK gives 785-786; the claim is at :786-787. | REVIEW:580; CHECK:83 | 2026-09-27 |

---

## 2. Published progress reports

Published reports are not edited, and their corrections go in the next report (`docs/progress-reports/README.md:12`).

### Report 1 (`docs/progress-reports/2026-09-27/index.html`)

The corrections are in **report 2**, which is pending: `docs/progress-reports/2026-09-29/index.html:401-410` on `results/RBT-119-report2`, **PR #398, draft, unmerged**. When #398 merges, replace "PR #398 (pending)" with the merged path. The authority is paper 10, as corrected by its adversary. (H66)

| file:line | what it says | the correction | source | date |
|---|---|---|---|---|
| `docs/progress-reports/2026-09-27/index.html:279` | "The chance of 9 of 10 by luck is about **2 in 10,000**" | 2.2 × 10⁻⁴ is the **size of the registered count rule** (its false-positive rate), not the probability of this outcome. On each run's own genealogy the chance of 9 or more of 10 is about 10⁻¹⁶. | P10:327-328; HISTORY:165 (H66); report 2 draft, PR #398 (pending) | 2026-09-27 |
| `…/2026-09-27/index.html:290` | "only **2–3%** survives 16 generations of mutation alone" | **1.3%.** The working compass's persistence at depth 16 under the default operator is 0.0127. | P10:410; HISTORY:165 (H66); report 2 draft, PR #398 (pending) | 2026-09-27 |
| `…/2026-09-27/index.html:292` | "In the world where the compass pays more, **selection outran the erasure**" | **Withdrawn.** HELD is read against the operator-alone bound at two finite depths, not at a balance, and it fires below the balance point. So "HP's 9 of 10 does not by itself imply s of that order" (≈ 0.39, the balance point under the default operator). "No s was estimated for HP." | P10:506-511 (the quotations at :510-511); `docs/paper-10/adversary/PAPER-ADVERSARY.md:120-133` (F6); HISTORY:165 (H66, naming :279, :290, :292); report 2 draft, PR #398 (pending) | 2026-09-27 |
| `…/2026-09-27/index.html:251` | "'Pays enough' means the extra breeding it buys **outpaces mutation**" | This is the same reading as :292 and is withdrawn with it. Report 2's draft corrects it in the same row. | as above | 2026-09-27 |

---

## 3. Registered outputs

These are files printed by registered code. By rule they are never edited after the readout (RBT-121 R11), so the bare label stands in the file. **Always quote the ruled gloss with the label** (R14). (H76, and the incidents named in each row)

| file:line | what it says | the ruled gloss | source | date |
|---|---|---|---|---|
| `runs/RBT-117/compare.txt:46` | "## VERDICT: HOLISTIC RESPONDS MORE" | **M1, "always quote it with the verdict":** "The margin is entirely in the down line. It exists because the holistic body can grow motor capacity that the mass budget does not cap: ball-joint gear keyed to the heavier part gives the holistic D line a work ceiling about 2× the designed body's. With the holistic D line's work capped at the designed D line's, the difference is −0.02 (p 0.86)." It is not evidence for the proposal's reason (b). **Line:** HISTORY gives :37,44; the verdict is at :46. (H69) | `runs/RBT-113/REPORT.md:128` (within :124-136); ruling on RBT-113, 2026-09-27T19:49:36Z; #393, #394 | 2026-09-27 |
| `runs/RBT-112/readout.txt:40` | "VERDICT Z: FALSIFIED … did not let selection hold the compass; **the operator is not the stall**" | The ruled sentence: "**The bias walk is not what stops selection holding the compass in the population.**" Selection's advantage on it is below about 0.1 per generation. `--global-bias-sigma 0` froze the designed body's global biases, host and planted, and the host changed too (SE-Z failed: income +0.160). It is not "the operator is irrelevant": under S = 0 the best lines do carry and use the compass (5 COMPASS lines against 0). (H65) | `runs/RBT-112/READOUT.md:33-40` (the sentence at :35-36); P10:62; `runs/RBT-112/readout-adversary/ADVERSARY.md:33-43, 154-203`; P10:436-448 | 2026-09-27 |
| `runs/RBT-100/readout.txt:413` (printed by `verdict_text`, `runs/RBT-100/readout.py:230`) | "CLASS A: the co-evolved body earned more under the shift, **both surviving above the floor**" | "Both surviving" is **false on 7 seeds**: the designed fauna is extinct on 5 and below the floor on 2. An unchanged designed fauna is insolvent, so the arithmetic is a **bracket** (+0.12 to +0.32) and decides no response difference. Drop the class-D wording ("budget was exceeded"). The A sentence is "outlasts", not "holds up". (H55) | `runs/RBT-100/readout-adversary/READOUT-ADVERSARY.md:105-106, 217-252`; P9:401-411; `runs/RBT-100/REPORT.md:10` | 2026-09-26 |
| `runs/RBT-105/aa_spread.txt:4` | "this spread is therefore an **UPPER BOUND** on a challenge arm's own A/A spread" | The spread does not grow with time since divergence (time-matched 0.109). It is "a comparator of scale … not a bound in either direction, and not a null for any event". (H60) | `runs/RBT-105/readout-adversary/READOUT-ADVERSARY.md:236-287`; P9:846-858; `runs/RBT-105/REPORT.md:12` | 2026-09-26 |
| `runs/RBT-105/readout_posthoc.txt:96-97` | "for the recovery window this is an upper bound in time" | As above. (H60) | as above | 2026-09-26 |
| `runs/RBT-106/H-readout.txt:60` | "VERDICT H: SUPPORTED: **the larger prize** held the paying compass where the uniform prize did not" | Ruled sentence: in the world where a working compass pays about 2.5× more, which **also raised births, income and turnover**, the compass was held on 9 of 10 seeds, and on none in the uniform world. The design isolates patchiness, not the prize alone. (H64) | P10:347-365; `runs/RBT-106/h-adversary/ADVERSARY.md:221-242` | 2026-09-27 |
| `runs/RBT-104/readout.txt:58` | "VOID … the side effect, not link-weight reach, is what was measured" | The ruled wording: "**VOID, and the instrument could not see**". The install control never applied the arm's `--link-scale 8`, and a compass built at the default scale is invisible in a host built at ×8. The question is unanswered. Withdrawn from the first version: "the evolved hosts mask an installed compass" and "§1.4's bias gate, seen in evolved brains". (H63) | `runs/RBT-104/readout-adversary/READOUT-ADVERSARY.md:13-30, 292`; P10:243, 258-259; `runs/RBT-104/REPORT.md:36-60, 170-172` | 2026-09-27 |
| `runs/RBT-99/readout.txt:140` | "holistic shift : recovered within 180 on 9/10 seeds" | **A d = 0 artefact:** "recovered" at 0 means "had not yet diverged". No recovery claim is made from the registered rule. (H52) | `runs/RBT-99/REPORT.md:69-71, 199-203`; P9:216 | 2026-09-26 |
| `runs/RBT-92/readout.txt:137` | "holistic shift : recovered within 180 on 10/10 seeds; median of the recovered 0.0" | As above: every shift seed leaves the band, on both faunas. (H52) | `runs/RBT-92/readout-adversary/READOUT-ADVERSARY.md:140-150`; `runs/RBT-92/REPORT.md:126-144` | 2026-09-26 |
| `runs/RBT-90/part2-readout.txt:49` | "SPLITS: a founding-population property" | The gloss was withdrawn (PART2-VERDICT:16), and RBT-105 replaced PART2-VERDICT's own wording. The adopted sentence: "Oscillator fate is **not fixed by the founding population**: from byte-identical founders, a different breeding history reversed the fate in 5 of 14 decided replicates … on 3 of 8 founding populations. … **The founders shift the late oscillator birth rate** (R2, p = 0.011). How the variation divides between founders and history is not resolved at this n." (H49) | `runs/RBT-105/REPORT.md:42-45`; `runs/RBT-90/PART2-VERDICT.md:16` | 2026-09-26 |
| `runs/RBT-90/part2-readout.txt:54` | depth in [15, 26]: "A PROPERTY OF THE SEARCH" | "Relabelled: a property of this economy's **demography**, not of the search": a random-parentage null lands inside the interval in 98% of replicates. (H49) | `runs/RBT-90/PART2-VERDICT.md:15` | 2026-09-26 |
| `runs/RBT-90/part2-readout.txt:44` | drive is not an oscillator: "A PROPERTY OF THE SEARCH" | "Holds structurally": no champion carries an oscillator with a path to a live effector (10 of 10). The `no_osc` lesion is a no-op on all ten, and at n = 64 it lacks the power to contradict. (H49) | `runs/RBT-90/PART2-VERDICT.md:14` | 2026-09-26 |
| `runs/RBT-90/part2-readout.txt:34` | gait row: "A PROPERTY OF THE SEARCH" | This holds **by construction**: no champion's path responds to the food layout (10 of 10), so the row adds nothing. (H49) | `runs/RBT-90/PART2-VERDICT.md:13` | 2026-09-26 |
| `runs/RBT-85/readout.txt:32` | "0.046 (2 SE …). \|mean\| = 0.0485 is outside it." | With four differences, 2 SE is an 86% interval. Against the A/A null, −0.049 has p = 0.49. (H47) | `runs/RBT-85/REPORT.md:37`; `runs/RBT-96/REPORT.md:83` | 2026-09-26 |
| `runs/RBT-74/readout.txt:11, 18, 20` | "paired, protected minus unprotected … mean **+0.064** … SE of paired mean 0.073" | One RNG stream fed both populations and the terrain, so **pairing by seed paired only the founders**. The rerun with per-population streams (RBT-85) reads −0.049 [−0.122, +0.025]. (H46) | `runs/RBT-85/REPORT.md:9-18`; `runs/RBT-74/REPORT.md:3,5` | 2026-09-26 |
| `runs/RBT-102/aggregate.txt:3` | "drift reference … upper bound p_u = 0.0520%" | The ruled headline: the count stands, and the verdict is "**not informative about selection at** this n". The pre-registered p_u was built on the wrong population: RBT-91's 0.042% drift rate comes from evolved parents. The rate matched to these arms' founders and pedigrees is 0.0076%, about 5.5× lower than 0.042% (about 6.8× lower than the 0.0520% bound). Zero is the modal drift outcome (81%). The verdict does not move, since U = 0. (H61) | `runs/RBT-102/REPORT.md:7, 132-137`; `runs/RBT-102/adversary/ADVERSARY.md:70-148` | 2026-09-26 |
| `docs/artifacts/RBT-23-W4b-801/compass_race.txt:24` (from `scripts/compass_race.py:36`, `DEPTH = 4`) | "max \|a\| reached by any chain in 40 mutations: 26.52" | Read at depth 4 on brains with ρ > 1, so it is not a gain. (H36) | P8:700-708 | 2026-09-26 |
| `docs/artifacts/RBT-91-resigned-84-reference.txt:102` | "chemotactic fraction of RESOLVED structural arrivals: **42.2%** [32.1%, 52.9%]" | This used the whole-brain sign and counted zeros as anti. On the motif's own links: **30/28, 51.7%** [39.2, 64.1]. (H41) | P8:349-370, 668 (W12) | 2026-09-26 |
| `docs/artifacts/RBT-91-alone-baseline.txt:112-113`; `RBT-91-alone-1.6.txt:97-98`; `RBT-91-alone-4.0.txt:100-101`; `RBT-91-drift-baseline.txt:112-113`; `RBT-91-drift-widened.txt:97-98` | "The rung is **6.8664** … compares realised against realised" | 6.8664 is a **whole-brain** reading of the installed motif, so it is not like for like. The motif's own links read **12.52** at the paying rung (6.28 at the first). (H41) | P8:411-421, 669 (W13) | 2026-09-26 |
| `docs/artifacts/RBT-97-rbt67-resigned.txt:12-18` | "+0.674 [+0.438, +0.967] **12/12**" | "12/12" counts point estimates. Only **6 of 12** robots have their own interval above zero at a = 32 (10 of 12 at a = 64). (H43) | `runs/RBT-97/ADVERSARY.md:41-43`; P8:520-521 | 2026-09-26 |

---

## 4. Run reports and analysis files

| file:line | what it says | the correction | source | date |
|---|---|---|---|---|
| `runs/compass-spike/REPORT.md:50, 102, 106-110` | "Result: nothing, at any setting"; "a bolted-on compass earns nothing" | **Transposed drive.** The Pioneer's wheel hinge axes are antiparallel, so the spike installed a smell-gated pirouette. Wired correctly, the compass earns **+0.897 items (+59%, 7 of 7)**. The finding is "withdrawn, not amended". The report has **no erratum**. (H28) | `runs/sim-audit/CHAOTIC-DOC.md:14-22, 93-111`; P7:282-321 | 2026-09-13 |
| `runs/sim-audit/CHAOTIC-DOC.md:166` | "the taxis-specific gain is **+0.723, i.e. +48%**" | As at P7:309-312. (H74) | P8:226-231, 724-725; `runs/RBT-72/rederive.txt:17-18` | 2026-09-26 |
| `runs/sim-audit/CHAOTIC-DOC.md:214, 234, 247-249, 285, 323` | "drift reaches a gain that earns anything measurable (a ≥ 32) in **0.70%** of lineages" | 0.70% is a depth-4 truncation of a divergent series (ρ 1.565–4.92), and an information-free sensor pair clears it at the same rate. The direct motif arrives 0 of 10,000. (H31) | P7:421-430, 435, 469-474; `runs/RBT-78/REPORT.md:91-99`; P8:116-120, 660 (W4) | 2026-09-14 |
| `runs/RBT-45/REPORT.md:143-144` (also :8-10, 266-268, 320-324) | CROSSED is "the circuit that steers up a gradient", "the only one that steers"; re-aim RBT-42's operator "at the crossed pairing" | As at P6:126-128. The recommendation is withdrawn. (H29) | `runs/sim-audit/CHAOTIC-DOC.md:113-116`; P8:628-629, 657 | 2026-09-13 |
| `runs/RBT-59/REPORT.md:76-77` | "a multi-step circuit that arrives in one lineage in seventy-seven" | As at P6:126-128. (H29) | `runs/sim-audit/CHAOTIC-DOC.md:113-116` | 2026-09-13 |
| `runs/RBT-59/REPORT.md:77-78, 84-86` | "`max_age` 15 would buy **four times the search depth**" (recommended) | "The lever works and the recommendation was wrong": `--max-age 15` bought 3.4× the depth and a worse population (heritability 0.51 → 0.25; yield fell). (H39) | `runs/RBT-60/REPORT.md:27, 49, 65, 106-114` | 2026-09-13 |
| `runs/compass-gain/SUPERSEDED-FINDING.md:26-31` | "structural precondition … present in 7 to 17 percent … the bottleneck is **not** that the circuit is never proposed" | Only the filename marks this. `sensor_influence` sums `abs(w)` and clips at 3.0, so a compass and its twin read the same. Its author reversed it: sign structure and magnitude are missing, not topology. (H30) | `runs/compass-gain/REPORT.md:93-113`; P7:268-271; RBT-63, 2026-09-13T13:24:12Z | 2026-09-13 |
| `runs/compass-gain/REPORT.md:1, 84-91` | "It is 30 times too small"; w = 16 at "depth ≈ 6,500"; "P(\|a\| ≥ 32) ≈ **10⁻⁷⁷**" | The σ(d) law is wrong (as at P5:303-305). 10⁻⁷⁷ is moot, because the direct motif cannot be written, and its own stated derivation gives 10⁻¹⁹·⁹. "Thirty times" must carry its unit. (H40) | P8:458-461, 661-662 (W5, W6), 726-729 | 2026-09-26 |
| `runs/compass-gain/REPORT.md:117-118` | "The prize is +59% and the search cannot reach it" | +59% is a **floor**. There is no turnover, and it is still rising at a = 384 (+1.875, +148%). (H42) | `runs/RBT-67/REPORT.md:10-12`; P8:183-193 | 2026-09-14 |
| `runs/RBT-58/REPORT.md:62-64` | "No controller is called a compass unless its items per cell of newly visited ground exceeds `density × cell_area`" | The per-cell rule overstates by 1.67–1.91×: "a test a wide body passes for being wide". The rule is withdrawn. (H34) | `runs/RBT-39/REPORT.md:136-142` | 2026-09-14 |
| `runs/RBT-91/structural_rate.py:346-352` | `PAYING = 6.8664` "compares realised against realised" | As in the `RBT-91-alone-*` row of §3. (H41) | P8:413-421, 669 | 2026-09-26 |
| `runs/RBT-91/resign_arrivals.py:239-242` | "Against the first paying rung (6.8664)" | :241-242 flag the gains as whole-brain, but not the 42.2% classifier. As in §3. (H41) | P8:349-356, 669 | 2026-09-26 |
| `runs/RBT-102/PREREG.md:117`; `runs/RBT-102/analyse.py:47` | "against RBT-91's drift arrivals, 42.2% [32.1, 52.9]"; `PAYING = 6.8664` | As in §3. `runs/RBT-104/PREREGISTRATION.md:349` already calls 6.8664 superseded; RBT-102 does not. (H41) | P8:349-370, 668-669 | 2026-09-26 |
| `runs/RBT-5/REPORT.md:61-63, 173-175` | "2 founders observed against 102 expected under noise … Selection at this budget is real and strong" | As at P3:104. (H8) | `runs/RBT-11/REPORT.md:70` | 2026-09-12 |
| `runs/RBT-12/REPORT.md:34` | "a body that moves by rolling its sphere" | "It does not roll, it **flails**": a sphere on a crank the length of its radius, spun at 3.4 rev/s against the ground, dragging a box on its side. The contact-artefact test was not done. (H11) | `runs/RBT-37/REPORT.md:5-20` | 2026-09-12 |
| `runs/RBT-13/REPORT.md:90` | "A 57% cut, at about two standard errors" | At 64 paired seeds: 29%, t = +2.15. **Dies** under the 64-seed rule. (H22) | `runs/RBT-38/REPORT.md:37` | 2026-09-12 |
| `runs/RBT-13/REPORT.md:106` | "the strongest mower in the whole foraging series so far, **3.12** items alone" | At 64 draws: **2.03 ± 0.22**; 3.12 lies outside the interval. (H23) | `runs/RBT-28/REPORT.md:222, 229` | 2026-09-14 |
| `runs/RBT-15/REPORT.md:76` | "'the economy per unit of simulated time is unchanged', and it is" | True on the cost side only. Food per second falls to about 40%, because the standing crop resets at spawn. (H19) | `runs/RBT-20/REPORT.md:64` | 2026-09-12 |
| `runs/RBT-17/REPORT.md:54` | bests "lose a third and 58% of their solo yield" | The 590 best survives at 35%, not 58%. (H22) | `runs/RBT-38/REPORT.md:30` | 2026-09-12 |
| `runs/RBT-18/REPORT.md:68` | "Pioneer best at s0 only (57% of food lost…)" | **Dies** (t = +1.61). (H22) | `runs/RBT-38/REPORT.md:35` | 2026-09-12 |
| `runs/RBT-18/REPORT.md:73` | "the value at which a 1.1 kJ blind mower still breeds is about 0.1 per kJ" | Realised arena yield is 0.385, not 0.50. Break-even is 0.119, and the population ceiling is below 0.08. (H17) | `runs/RBT-21/REPORT.md:202-205` | 2026-09-12 |
| `runs/RBT-20/REPORT.md:60, 96` | "Blanking the food and agent sensors removes **74%** of its food" | Dies narrowly: 35%, t = +2.39. (H22) | `runs/RBT-38/REPORT.md:36` | 2026-09-12 |
| `runs/RBT-21/REPORT.md:126, 160, 185` | "c0-8 is nose-dependent … more than halves its yield"; "57%" | **Dies:** CI [−0.061, +0.623]. The correction is on the RBT-21 ticket only, not in the file. (H22) | `runs/RBT-38/REPORT.md:34` | 2026-09-12 |
| `runs/RBT-22/REPORT.md:3, 20` | "found that the i/(1+i) squash saturates"; "Normalising recovers most of what the saturation cost" | As at P6:154. (H20) | `runs/sim-audit/CHAOTIC-DOC.md:182-188` | 2026-09-13 |
| `runs/RBT-22/REPORT.md:112, 114` | below the blind-mow floor "is damning" | The floor is a point-robot rate. The honest own-gait null is 0.70–1.67× it, so it bounds nothing in either direction. g300's own null is 0.208, and g300 measures above it. (H21) | `runs/RBT-39/REPORT.md:52-118` | 2026-09-14 |
| `runs/RBT-23/REPORT.md:83` | "s590 only, and weakly (1.38 → 1.00, −28 %)" | **Dies and is vetoed:** 36 of 64 seeds unmoved. (H22) | `runs/RBT-38/REPORT.md:42` | 2026-09-12 |
| `runs/RBT-10/REPORT.md:271` | the lead "holds 450–566 of 600 seasons" | These were the two most favourable replicates. Fresh seeds read 411–571, with a margin from a fifth of an energy unit to nothing. (H27) | `runs/RBT-71/REPORT.md:143-146` | 2026-09-14 |
| `runs/RBT-85/REPORT.md:106` | "the ±0.10 rule is now a threshold the design can see" | The A/A RMS is 0.128, so h = 0.178 > 0.10, and the ±0.10 rule is unsound at n = 4. The same file's erratum at :35 fixes :33 but not :106. (H47) | `runs/RBT-96/REPORT.md:79-83` | 2026-09-26 |
| `runs/RBT-101/REPORT.md:20-24, 179-182, 322-323` | "Beyond the arithmetic the contrast moved back toward the co-evolved body … **+0.27**" | The same difference appears on the old random terrain (+0.248), so only new − old (+0.024 [−0.115, +0.163]) is a response. The cull20 turnover null reproduces +0.20 of it. Net +0.07, **NOT DECIDED**. (H57) | `runs/RBT-110/C4null/READOUT.md:47-48, 71-79`; P9:612-621 | 2026-09-26 |
| `runs/RBT-113/PREREGISTRATION.md:341-344` (the phrase at :343) | "the up line **learns to eat**" | M2: "learns to move, and eats by covering ground". Blind variants eat 0.913 and decoy variants 0.934, against 0.854 intact. 61% of up-line members carry no food sensor (39% carry one), and ground covered rises about 6× (5 → 29 cells). HISTORY's H70 reads it as "the blind mower (paper 6) evolving from random founders under imposed selection". (H70) | `runs/RBT-113/readout-adversary/ADVERSARY.md:214` (M2); `runs/RBT-113/readout-adversary/probe_food.txt:5-7`; `runs/RBT-113/REPORT.md:84, 179`; HISTORY:174 (#393, #394) | 2026-09-27 |
| `runs/RBT-113/design-adversary/ADVERSARY.md:65-66` | "It **learns to eat**, and its food rises 20-fold" | As above. (H70) | as above | 2026-09-27 |

---

## 5. Design notes and other docs

| file:line | what it says | the correction | source | date |
|---|---|---|---|---|
| `docs/foraging-world.md:101` | "since a lump's budget never depended on the work cost" | False for the tail. At 0.15 and 0.08 per kJ, random founders' work budgets "decide the outcome before evolution starts": 4–5 of 59 founders spend over 1.25 kJ, and one spends 21.6 kJ. (H17) | `runs/RBT-21/REPORT.md:195-200` | 2026-09-12 |
| `docs/foraging-world.md:122` | "holds the lead in 450 to 566 of 600 seasons" | As at `runs/RBT-10/REPORT.md:271`. (H27) | `runs/RBT-71/REPORT.md:143-146` | 2026-09-14 |
| `docs/foraging-world.md:145` | "the strongest mower of the series (**3.12** items …)"; "the i/(1+i) squash saturates at 3 m decay … (sensor design error, mine)" | 3.12 → 2.03 ± 0.22 (H23). The squash is not an error (H20). | `runs/RBT-28/REPORT.md:229`; `runs/sim-audit/CHAOTIC-DOC.md:182-188` | 2026-09-14 |
| `docs/foraging-world.md:152` | "yield heritability **0.246** against a 0.4 floor" | As at P5:189. It stands unqualified above the document's own caveat at :325. (H25) | `docs/foraging-world.md:325` | 2026-09-14 |
| `docs/foraging-world.md:225-226` | "too few to assemble a crossed Braitenberg circuit that arrives in **1.3%** of lineages" | As at P6:126-128. The qualifier at :199 covers depth 4 only, not the pirouette. (H29, H75) | `runs/sim-audit/CHAOTIC-DOC.md:113-130`; P8:657 | 2026-09-13 |
| `docs/foraging-world.md:288` | "a summed smell squashed by i/(1+i) saturates at long range" | As at P6:154. (H20) | `runs/sim-audit/CHAOTIC-DOC.md:182-188` | 2026-09-13 |
| `docs/runs/RBT-69-compass-replication.md:120-121` | "drive **forward** (pooled travel azimuth minus body yaw +5.1°, six of seven within ±10°)" | An independent re-implementation measures +12.0°, R = 0.430: five forward and two backward. HISTORY H35 adds the rule: direction of travel is a free population parameter, so measure it first and state the generation. (H35) | P7:396-400; HISTORY:124 (H35) | 2026-09-14 |
| `docs/rbt-91-weight-scale-decision.md:36, 66-69, 95-100, 133-135, 143-149` | "**43% of arrivals are chemotactic** (35 compasses, 48 anti-compasses…)"; "largest is 3.91 against a rung of 6.87" | As at `RBT-91-resigned-84-reference.txt:102`: 30/28, 51.7% on the motif's own links. The like-for-like rung is 12.52, not 6.87. (H41, H75) | P8:349-370, 411-421, 668-669 (W12, W13) | 2026-09-26 |
| `docs/rbt-91-weight-scale-decision.md:54` | "the motif's own links never reach the rung" | The verdict stands, and is strengthened. But "the rung" is the whole-brain 6.87; like for like it is 12.52. (H75) | P8:411-421, 606 | 2026-09-26 |
| `docs/rbt-91-weight-scale-decision.md:80-87` | "the compass does not pay on these populations at all … RBT-69 … negative at every magnitude" | RBT-69's negatives were the W4b sign installed on mostly forward-driving robots, which makes an anti-compass. Correctly signed, **12 of 12** robots pay from a = 32 (6 of 12 resolved). RBT-97 withdrew the premise. (H43, H75) | P8:508-523; `runs/RBT-97/ADVERSARY.md:153` | 2026-09-26 |
| `docs/rbt-91-weight-scale-decision.md:202-203` | "max 4.745 / 5.008"; "operator asymptote … rms **2.938**, 1.96% ≥ 8" | The committed readout re-runs byte-identical and gives depth-20 max **4.835** and rms **3.016**, with 2.17% ≥ 8. The document's figures come from an earlier, different census. (H40, H75) | P8:396-401, 730-734 | 2026-09-26 |
| `docs/rbt-91-weight-scale-decision.md:260-275` | item 1 (:261-265): "first paying rung … did not replicate … negative at every magnitude"; item 2 (:266-268): "**n = 4.** … the 92% figure is the maximum of four draws"; item 3 (:269-275): "Re-signing per individual … has not been done. Roughly half should be expected to be anti-compasses." | Item 1 as at :80-87. Item 2: **the 92% figure is withdrawn.** That arrival read the whole brain; the motif's own links read +0.0036, and it turned out to steer the wrong way (the same document at :96-98; P8:666, W10). The n = 4 rate is superseded by 84 in 200,000 (:26-33), and :61-62 notes the four were nearer two independent draws. Item 3: the same document later re-signed all 84 (:89-101), and P8 re-reads that on the motif's own links as 30/28, 51.7%. (H40, H41, H43, H75) | P8:349-370, 508-523, 666 (W10), 668 (W12); the same file :26-33, :89-101 | 2026-09-26 |

---

## 6. Commit messages

These cannot be amended. (H62)

| commit | what it says | the correction | source | date |
|---|---|---|---|---|
| `c42e4f7` | "RBT-90's world is 12 items on random terrain; P-801's is 26 in three patches on **flat**." | Terrain is random in every world. P-801 does not regrow within a bout, and RBT-90 regrows instantly. The world control was exploratory, with no pre-posted attribution rule. | `runs/RBT-103/REPORT.md:41, 43-53, 55-59, 192-206` | 2026-09-26 |
| `935bcbf` | "P-801 in its own world (26 items, 3 patches, **flat**)" | As above: the terrain word and the attribution are wrong. The gain figures in the same message (+0.507 to +1.324) are not corrected by any source. The attribution to patchiness, rather than density or regrowth, is exploratory. | `runs/RBT-103/REPORT.md:41, 43-53, 55-59, 83-91, 204-206` | 2026-09-26 |

---

## 7. Withdrawn before publication (noted for completeness)

| where | what it said | the correction | source | date |
|---|---|---|---|---|
| RBT-118 prior, first draft of `runs/RBT-118/prior/ANALYSIS.md:96` and the RBT-118 post (not in the current tree) | "**In income, the pattern is "behind early, ahead late".** That is the 2005 proposal's two-phase shape." (`d5e60a8:runs/RBT-118/prior/ANALYSIS.md:96`) | Withdrawn before merge. The early deficit is random founders that cannot move, set against working bodies (seasons 0–10, 30 of 30). The late lead is a work-price lead on **random terrain**. It reverses below a median 0.018 per kJ, and on flat ground on 21 of 29 histories. The faunas never compete, so this is **not** a test of the 2005 prediction. The merged ANALYSIS.md carries the replacement. | `runs/RBT-118/prior-adversary/ADVERSARY.md:51, 212-222` (MUST-FIX 1); PR #399, #402 | 2026-09-27 |

---

*Seeded under RBT-127 (RBT-121 fix list item 11; R12, R14; auditor D's P6) from `runs/RBT-121/history/HISTORY.md` H1–H76, REVIEW §8 as corrected by CHECK F2, the RBT-113 readout adversary, the RBT-118 prior adversary and the paper-10 adversary.*
