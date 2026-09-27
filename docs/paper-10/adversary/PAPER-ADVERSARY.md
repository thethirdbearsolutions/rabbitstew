# Paper 10 adversary (RBT-114), round 1: findings on `docs/paper-10-held-not-spread.md` at `e9db310`

I checked the paper sentence by sentence against the committed files on integration `cad78cb` and against
the Chaotic tickets. I did not edit the paper, run a simulation or ecology run, or read anything from RBT-107.

**Sources read:**
- the paper, `docs/paper-10/rederive.py` and `rederive.txt`;
- RBT-114's description (the brief);
- RBT-102: `REPORT.md`, `PREREG.md`, `informative_n.txt`, `adversary/ADVERSARY.md`;
- RBT-103: `REPORT.md`, `routed_populations.py`, `report.py`, `adversary/world_matrix.txt` and every committed
  `adversary/*.txt` body-plan line;
- RBT-104: `REPORT.md`, `readout.txt`, `readout-adversary/READOUT-ADVERSARY.md`;
- RBT-105: `REPORT.md`;
- RBT-106: `PREREGISTRATION.md`, `prize.txt`, `one_field.txt`, `P1-READOUT.md`, `P1-readout.txt`,
  `p1-adversary/ADVERSARY.md`, `power_n7.txt`, `H-READOUT.md`, `H-readout.txt`, `H-sensitivity.txt`,
  `h-adversary/ADVERSARY.md`;
- RBT-112: `READOUT.md`, `readout.txt`, `erasure.txt`, `power.txt`, `sensitivity.txt`, `DECISION.md`,
  `PREREGISTRATION.md`, `readout-adversary/ADVERSARY.md`, `instrument.txt`, `adversary/ADVERSARY.md`;
- `rabbitstew/genetics.py`; paper 5; paper 8;
- Chaotic RBT-104 (01:52, 02:00), RBT-106 (06:06, 08:20), RBT-112 (08:28, 12:20) and RBT-113 (description).

**Probe:** `probe_paper.py` → `probe_paper.txt`. It is print-only; the sections are cited below as A–F.

**What holds:**
- `rederive.py` reproduces `rederive.txt`.
- Every [row] tag I checked carries the number the text gives it.
- The erasure table, the P1 and H verdicts, the power figures, the A3 block quote in §5.2 (identical to
  `READOUT.md` §1), the 06:06 and 12:20 quotations, and the §4 block quote of H8 are all correct.
- The limits section has all five of the brief's must-haves.
- Every null or "not held" verdict carries a power figure at its usable n.

**What fails:**
- **Seven sentences state more than their source or the ruling allows (MUST-FIX).** Three of them are in the
  abstract, the conclusion or §9.
- One sentence is contradicted outright by a committed row (P1-805).
- Every fix is a wording change, and none needs a new run.

Line numbers are the paper's at `e9db310`.

---

## MUST-FIX

**F1. "Every compass that paid was planted at the paying magnitude" is contradicted by P1-805.**
- The sentences:
  - §0, l.110: "Every compass that paid in these arms was planted at the paying magnitude."
  - §8, l.514: "Every compass that paid was planted at a = 64."
- **The contradicting files:**
  - `runs/RBT-106/P1-readout.txt`, row `805 | P1`: "+1.942 FD, FOOD-DEPENDENT", lesion gain +2.221 (probe F).
  - `P1-READOUT.md` l.95: "The one COMPASS line among all 20 arms is **P1-805**".
- P1-805 descends from the **w = 1 (a = 2), sub-paying** founders. It is outside the scored rules only because
  its pair's (S1-805's) install control failed. The paper names it itself at l.265, so §0 and §8 contradict §3.3.
- **Fix:** "Every compass that paid in a *scored* arm was planted at the paying magnitude. The one exception
  outside the rules is P1-805, a COMPASS line grown from the sub-paying w = 1 founders, whose pair is unusable
  (P1-READOUT.md; not scored, and not uniform-scored FD: +0.529)."
- Also correct §0 l.111–112, "Nothing here is de novo evolution (RBT-106 h-adversary H9)". See F14.

**F2. §10, l.581–582: "Where it paid less, the operator eroded it from every population, out of surviving
planted lineages as well as with them."**
- This attributes lineage loss to the operator, and "every population" overstates what the committed readings
  show (probe B, from `runs/RBT-112/readout.txt`'s HU rows):
  - **Planted-rooted lineages gone by 599:** HU-801, 804, 805, 807 and 7.
  - **Above the operator-alone bound at 300, before the lineage vanished:** 804 (3 > 1), 805 (2 > 1) and 7
    (3 > 2).
  - **Champions carrying a paying planted unit:** 801, 804, 805 and 7, 5 of 70 in all.
  - Losing a lineage is demography, not the operator's per-generation erosion.
- **What the source says:** h-adversary H1 says only that "HU's 'not held' is **not just** lineage loss". In
  the five surviving lineages the compass was eroded "too".
- **Fix:** "Where it paid less, it was held on no seed. Five of ten lost their planted-rooted lineages by
  season 599, three of them after reading above the operator-alone bound at 300. In the five where planted
  lineages survived, none of their living carried a paying compass."
- §6 l.453–454 ("eroded out of surviving planted lineages as well as lost with them") is acceptable as
  written.

**F3. §9 item 1, l.550–553: the heading and one clause go beyond the ruling. §9 says it makes no new claim.**
- (a) **The heading.** "Selection strength, **rather than** the operator." The 12:20 ruling it quotes on the
  next line says "**not only** the operator". A3 exists to stop the operator being read as irrelevant.
  - RBT-114's own brief uses "selection strength rather than the operator". That phrase is the ticket's
    shorthand, not the ruled wording, so the coordinator decides which governs.
  - **Fix:** "Selection strength, not only the operator."
- (b) **The clause.** "Under the frozen operator … the population share does not rise; under the default
  operator in the patchy world **it does**."
  - HELD is k_planted > B at two depths. It is not a rising share. HP's planted-rooted paying share fell from
    300 to 599 on 5 of the 9 held seeds (probe D), for example HP-1 0.62 → 0.12 and HP-805 0.58 → 0.14.
  - No committed file says the share rose in HP.
  - **Fix:** "under the default operator in the patchy world it is held above the operator-alone bound on 9 of
    10 seeds."
- The same reading sits in l.64 ("it does not decide whether selection raises the compass's share") and in the
  title gloss, l.125–126. Those are A3's words about the uniform world and can stay; see F5 for their scope.

**F4. Abstract l.55–58 and the summary table's RBT-112 cell (l.84) drop both limits that A3 made MUST-FIX.**
- **The abstract:** "In the accepted wording, the bias walk is not what stops selection holding the compass in
  the population; selection's advantage on it is below ~0.1 per generation, and the arms' own likelihood puts
  it at 0–0.08."
- **What A3 requires** (`runs/RBT-112/readout-adversary/ADVERSARY.md`, A3 row and l.33–37): the MUST-FIX was
  precisely that READOUT.md carry
  - the §6.2 limit, marked as the registered limit, and
  - §10.4 F3's "a change in s itself is not handled" under SE-Z.
- **What the abstract does:**
  - It drops "(the registered limit …)", so "below ~0.1" reads as a measurement.
  - It omits the SE-Z sentence.
  - It still says "In the accepted wording".
- The summary-table cell's "…" elides exactly those two sentences.
- **Fix, for the abstract:** "…selection's advantage on it is below ~0.1 per generation (the registered limit;
  the arms' own model-based likelihood puts it at 0–0.08). With the global biases frozen the host also changed
  (SE-Z failed), so a change in s itself is not handled."
- **Fix, for the table:** keep the s-limit sentence and the SE-Z sentence in the A3 cell.
- §10 l.584–585 has the same gap: "On the arms' own likelihood its advantage there is between nothing and about
  eight percent a generation." Add "(model-based, for the frozen-bias host; the registered limit is below
  ~0.1)".

**F5. l.63–65: "on this body and in these two worlds, the operator decides how much compass is left …; it does
not decide whether selection raises the compass's share".**
- A3's sentence ("it does not, under either operator") rests on HU against HZ. That is the uniform world only.
- No frozen-operator arm was run in the patchy world, so "in these two worlds" extends A3 to a world where the
  operator was never varied.
- **Fix:** "So, on this body **and in the uniform world**, the operator decides …; it does not decide whether
  selection raises the compass's share. In the patchy world only the default operator was run."

**F6. §6, l.469–472 (post hoc [M1]): "If the recursion applied to the patchy world unchanged, HP's HELD on 9 of
10 against that erosion would imply a per-generation advantage of that order there."**
- The model the paper borrows contradicts this inference.
- HELD is k_planted > B at two finite depths, not a share held above 0 at a balance. Under the same recursion,
  HELD fires **below** the balance point:
  - at S = 0 the balance point is 0.098;
  - at s = 0.089, just below it, `instrument.txt` (2) gives E#HELD(HZ) ≈ 2 of 10, and P(#HELD ≤ 1) is only
    0.320–0.431.
- So HP's 9 of 10 does not imply s ≈ 0.39. The paragraph's own caveat ("HELD is read at two depths rather than
  at a balance") names the flaw, and the sentence then asserts the implication anyway.
- **Fix:** "HELD is read against the operator-alone bound at two finite depths, not at a balance, and under the
  same recursion it fires below the balance point (at S = 0, s = 0.089 gives E#HELD ≈ 2 of 10;
  `instrument.txt` (2)). So HP's 9 of 10 does not by itself imply s of that order. No s was estimated for HP."
- §8's "Model-based s" bullet can keep "§6's default-operator arithmetic is this paper's, post hoc".

**F7. The summary table, l.84: FUNCTION FOLLOWS sits in the "registered verdict" cell.**
- The cell reads "**FALSIFIED**, function FOLLOWS".
- **The source:** `runs/RBT-112/readout.txt` l.42 reads "function (reported, not in the verdict): FUNCTION
  FOLLOWS". The coordinator's brief for this round says the same.
- §5.2 gets this right ("reported beside it"). The table does not.
- **Fix:** "**FALSIFIED** (function FOLLOWS is reported beside the verdict, not in it)."

---

## SHOULD-FIX

**F8. Abstract l.29–31: the holistic claim traces only to prose. No committed output records the check.**
- The sentence: "the instrument that installs it raises on every holistic champion checked (RBT-103, 'What is
  not answered')".
- It matches `runs/RBT-103/REPORT.md` l.211–213, and the docstring of `routed_populations.py`, l.27–28 ("on
  RBT-90's seeds the holistic champion raises StopIteration here").
- **Probe A:**
  - All 22 committed RBT-103 body-plan lines read "7 of 7 bests can carry the circuit". Every one is a
    Pioneer run.
  - No committed file names the holistic champions checked, or how many there were.
  - `runs/RBT-90/forage-*` commits no genome files, so the check cannot be re-run from the repository.
- **What the check tests:**
  - `unit_indices` (`runs/RBT-97/routed_p801.py` l.62–81) looks for a food Sensor and an Effector at node
    indices 1 and 2 (`WHEELS = (1, 2)`), and asserts the Pioneer's pinned layout.
  - "Raises" therefore means "does not have the Pioneer's wheel layout". It does not mean "cannot carry any
    compass".
  - RBT-102 states the same scope for the fauna generally (`PREREG.md` l.25–27; `adversary/ADVERSARY.md` F6:
    "The holistic fauna has no wheel noses, so the predicate is undefined there").
- The claim is accurately quoted, so it passes the house form. It is not verified by any committed artefact.
- Because it bears on how the programme is pitched, say what it is.
- **Fix:** "the compass instrument is defined on the Pioneer's wheel layout. RBT-103's report states that it
  raises on every holistic champion checked, though no committed file records which or how many (RBT-102 F6:
  the holistic fauna has no wheel noses). Nothing here says whether an evolved body could carry a compass of
  another shape."

**F9. The abstract l.48–51 is introduced as "In the words of the ruling's required sentence" but is not
verbatim. The table's H8 cell (l.83) quotes only half the sentence.**
- **The abstract** drops "(u ≈ 0.29)" and re-punctuates both sentences.
  - The ruling (RBT-106, 08:20) allows "or its equivalent", so a paraphrase is fine, but not under "In the words
    of".
  - §4's block quote, l.319–321, is verbatim.
- **The table cell** starts at "in the world where…". It drops "The operator erodes the compass at the same rate
  per generation in both worlds (u ≈ 0.29), and the patchy arms bred more generations", which is the clause H8
  made mandatory.
- **Fix:** quote exactly as in §4, or say "in substance". Put the full sentence in the "wording, as ruled" cell.

**F10. 0.834 is the probability of FALSIFIED-a's count, not of the verdict.**
- The sentences:
  - l.83: "FALSIFIED-a … would have fired with probability 0.834";
  - l.346–348 (same);
  - l.491 (§7).
- **The source:** `runs/RBT-106/H-readout.txt` l.71 heads the column "P(FALSIFIED-a count)". l.78 adds "(the
  paired log-excess condition only lowers SUPPORTED and FALSIFIED-a)".
- **Fix:** "FALSIFIED-a's count (#HELD(HU) ≥ 5) would have been met with probability 0.834; the verdict also
  needs the log-excess condition, which can only lower it."

**F11. The best lines, overgeneralised.**
- **§10 l.583–584:** "Freezing it left the compass in the uniform world's best lines, which used it."
  - Only 5 of 10 HZ lines are COMPASS lines [Z2], and champions carry it 31 of 70 [Z4].
  - **Fix:** "…in the best lines of half the uniform-world populations (5 of 10), which used it".
- **§0 l.124–125:** "the best lines kept and used the compass". Same fix: "on five seeds of ten".
- **§10 l.580–581:** "every line's best robots steered through it".
  - `H-READOUT.md` l.37–38 makes a line-level call: "all ten lines' champions are food-dependent through the
    compass".
  - Not every champion carries the unit: h-adversary H2 says "HP-805's g350 carries no planted unit".
  - **Fix:** "every line's champions were food-dependent through it".

**F12. The post hoc labels are missing where two figures reach the abstract.**
- **l.52:** "The operator's erosion is **mostly** the global-bias walk." "Mostly" is this paper's post hoc [E4]
  (68%). It is labelled in §5.1 and not in the abstract.
  - **Fix:** add "(post hoc, this paper: 68% of u(8) [E4])", or quote the 08:28 ruling's "about two thirds".
- **l.60 and the table's l.84:** "carrying champions 31 of 70 against 5 of 70".
  - This is `sensitivity.txt` S1, which is post hoc and print-only. §5.2 l.399–400 labels it; the abstract and
    the table do not.
  - It is inside A3's accepted wording, which does not label it either.
  - **Fix:** give the label once, beside its first use.

**F13. §5.2 A1, l.417–420: two claims are broader than the adversary's own table.**
- (a) "On each HZ arm's own genealogy the S = 0 null's 95th percentile is at or above B."
  - The table (`readout-adversary/ADVERSARY.md` l.98–108; probe E) has five readings where it is below B:
    806 at both seasons, 1 at 300, 2 at both, and 7 at 599.
  - The adversary's scoped sentence (l.111–112) is "On the six seeds with n ≥ 40 at both readings … ≥ B at every
    reading but one (seed 1 at 300)". Its A1 row gives the unscoped form, and the paper copied that.
  - **Fix:** use the scoped sentence.
- (b) "B/n of 0.48–0.60 at 300 and 0.22–0.38 at 599 on the eight seeds that were neither HELD nor LOST".
  - `instrument.txt` l.28 scopes that range to "seeds with n >= 10". That set includes 805, which is HELD.
  - Seed 2 at 599 has n = 3 and B = 2, and needed every genome. The adversary calls it near-ceiling (l.47,
    l.85).
  - **Fix:** "at readings with n ≥ 10 (seed 2 at 599, n = 3, needed every genome)".

**F14. "Holding, not de novo" is attributed to H9, which says something narrower.**
- The sentences:
  - l.112: "Nothing here is de novo evolution (RBT-106 h-adversary H9)";
  - l.516: "(RBT-106 H9; §3)".
- **The source:** H9 (h-adversary l.244–246) is a finding about wording: no sentence in the readout claims de novo
  evolution.
- The positive statement "This is **holding, not de novo evolution**" is the coordinator's 08:20 ruling, and it
  covers H.
- **Fix:** cite the 08:20 ruling for H. For P1, rest on P-NULL, and name P1-805 (F1).

**F15. "Caveats, recorded in the report" (l.334) lists an item the report does not record, and omits that item's
actual caveat.**
- The ruling (08:20) put **H3 and H4** into the report, and `H-READOUT.md` l.48–56 carries only those two.
- The paper's third bullet, "F12's masking heuristic … (H5)", comes from the h-adversary, not the report.
- It also omits H5's actual caveat (h-adversary l.183–184): the heuristic's premise, that resting drive > 1
  masks the control, "failed on evolved hosts … Don't reuse it as a masking criterion without the increment
  test".
- **Fix:** move the F12 bullet under "What the readout adversary established", with H5's caveat.

**F16. §8 l.530–531: the 02:00 RBT-104 rule is truncated.**
- The paper: "RBT-104's rule to run every per-arm control on the arm's own founders before launch (02:00,
  Chaotic)".
- The 02:00 comment on Chaotic RBT-104: "run every per-arm control on the arm's own founders before launch, **and
  show it can pass**."
- The dropped clause is exactly what the 12:20 "shown passable" rule defines.
- **Fix:** restore it.

**F17. §3.2 l.233–241: one probe-derived figure is not labelled post hoc, and the paper goes past the ruling's
"only".**
- **The unlabelled figure.** `runs/RBT-104/REPORT.md` heads its whole "Why VOID" block "POST HOC probes", and
  the 91–96% saturation figure is the adversary's §1.2 probe.
  - The paper labels only the third bullet as post hoc.
- **The "only".** The 01:52 ruling says "Paper 10 cites RBT-104 **only** as 'VOID; the instrument could not
  see', with §1's probes post hoc." Beyond that, the paper prints:
  - the mechanism bullets;
  - the counterfactual matched-null power (l.245–246 and §7);
  - F4, in §3.2 and §9.
  - F4 is "of record" as post hoc in the 02:00 closure, so it is defensible. The power figure is in the report,
    but the ruling's "only" arguably excludes it. The coordinator decides.
- **Fix:** label bullets 1–3 as the report's post hoc account, and either drop the counterfactual power figure or
  mark it as the report's, not a reading.

**F18. §2 l.199 and l.202 print recomputed third decimals where the readout differs, against the paper's own
Precision rule (l.93–95: "The text prints the readout's figure").**
- The readout figures (`runs/RBT-106/prize.txt` l.25, l.29):
  - the paired difference is **+1.259 [+0.900, +1.617]**, not [+0.901, …];
  - the uniform base income is **+1.308**, not +1.309.
- **Fix:** print the readout's figures.

**F19. Omissions a reader needs.**
- **The ≤ 0.020 size needs H7's qualifier** (l.345–346). h-adversary l.217–218: "The '≤ 0.020' size holds at
  q ≤ 0.08; the worst case over q (q_U = q_P) is 0.132 at q = 0.5." The own-genealogy 2.2 × 10⁻⁴ softens this
  but does not replace it.
- **HP-807's pass** (§4 H4 bullet and §7 row, l.492). h-adversary l.152–153: "Its pass may be carried by its
  host's own compass." The §7 row gives F +4.538 "food-dependent through the compass" without this.
- **HU was above the bound at 300 on three seeds** (probe B). §4 and §6 give HU as "0 of 10 held". A reader
  should know that 804, 805 and 7 read above B at 300 and then lost their planted lineages. It bears on F2 and on
  what "not held in the uniform world" means.

---

## NOTE

**F20. The MLE (l.462).** The paper gives s = 0.01, from `instrument.txt` (3) with ρ profiled. READOUT.md l.89
says "The MLE is s = 0.00", which is the ρ = 0.10 line. Either is committed. Say which one the paper uses.

**F21. l.466: "Both are model-based, treat the two readings as independent".**
- This follows READOUT.md l.94–95 ("Both figures use the mutation–selection recursion … and treat the two
  readings as independent in the likelihood"), so it is not stronger than its source.
- It drops "in the likelihood", and the balance point makes no independence assumption.
- Optional: restore "in the likelihood".

**F22. §7 RBT-112 row (l.493) and Sources l.611.**
- "M15's pessimistic 0.214" is in READOUT.md l.77 and l.102. It originates in the design adversary
  (`runs/RBT-112/adversary/ADVERSARY.md` l.228; `power_adv.txt`), not in `instrument.txt` or `power.txt`, to
  which the Sources row credits "the design anchors".
- READOUT.md l.70–71 names n = 40 as the relevant anchor. The genealogy case, 0.108, would read
  FALSIFIED-ROOTS (PREREGISTRATION §10.1).

**F23. Citation labels.**
- **l.149 and l.203, "§2 item 3" and "§2 item 2".** Those items are in `runs/RBT-106/PREREGISTRATION.md`'s
  preamble list, "Three corrections to the ticket's premises" (l.35–47), not in §2. The 1.6× itself is §4
  (l.264), and the t = 0 table is §3.3. Suggested: "PREREGISTRATION.md, 'Three corrections', item 3; §3.3".
- **l.424–425.** "Seed 4's champions run on compasses carried in by crossover" is A4's finding in substance;
  A5 is about the living. §8 l.535 cites "(A4, A5)", which is right. §5.2 cites A5 alone.
- **l.362–364.** The v·tanh(b) resting-drive mechanism is in READOUT-ADVERSARY §5.2 (quoting RBT-106 §5.1),
  not §5.1.
- **l.329–330.** "not the only thing that differed" is h-adversary H8's phrase. The ruling says "not the only
  difference".

**F24. Small precision points.**
- **l.261–262.** "median transmission 0.39–0.60" is P1's range; S1's is 0.35–0.61 (`P1-READOUT.md` l.61–62).
  The three failing arms read 0.390, 0.406 and 0.443.
- **l.167–168.** The usability definition omits "analyse.py's control passed" (`P1-readout.txt` header;
  `H-READOUT.md` l.84).

**F25. RBT-103's two carried residuals are omitted in §2** (`REPORT.md` l.94–97):
- heterogeneity (seeds 807 and 2 barely rise in P-801's world);
- a home advantage is not excluded.
The size finding is labelled exploratory, so this is minor.

**F26. l.28, paper 5: "selection for locomotion and metabolism".** Paper 5's result is locomotion evolved
from survival alone, plus a heritable foraging yield on the co-evolved side. "Metabolism" is part of the world,
not a selected result. Suggested: "evolved locomotion and a heritable foraging yield".

**F27. §9 item 2, the RBT-113 trigger.** The quote is verbatim, but RBT-113 names a second trigger ("Or the
funder asks for one headline number…"). Not misleading.

**F28. `rederive.py`.**
- It hard-codes P1's usable list (`usable = [4, 804, 806, 807, 1, 2, 3]`) rather than parsing it from
  `P1-readout.txt`.
- [P3]'s "0 COMPASS lines among the 7 usable" therefore depends on that list. It matches the readout, so the
  results are unaffected.

---

## Checked and clear
- **Brief item 1 (numbers):** every [row] tag checked, and `rederive.py` against its source files. The erasure
  table, E5, 68%, u(1) 0.292, WORTH RUNNING, D1/D2, V1/V2, W1–W8, P1–P4, H1–H11, Z1–Z12, M1/M2 and A1/A2 all
  trace. The exceptions are F18 and F20.
- **Brief item 2 (claim strength):**
  - RBT-104: "VOID; the instrument could not see". See F17.
  - RBT-106 P1: P-NULL with power at n = 7 (0.215, 0.579, 0.116; "0.83–0.93 under both needed").
  - RBT-106 H: SUPPORTED; H3 and H4 text matches `H-READOUT.md`; the §4 H8 quote is verbatim.
  - RBT-112: A3's block quote in §5.2 is verbatim, and no sentence says the operator is irrelevant.
  - The failures are F3–F7, F9 and F11.
  - The 06:06, 08:20 (§4), 08:28, 12:20 and 01:52 quotations match the tickets.
- **Brief item 3 (population):** every compass result is named as the fixed-body (Pioneer) population
  (`seed_conventional`, checked in `HP-4` and `HZ-4` `config.json`). The holistic claim is F8.
- **Brief item 4 (power):**
  - RBT-102: 91/100 and ~184,000.
  - P1: at n = 7.
  - HU's zero: 0.834, see F10.
  - HP-807: one seed.
  - RBT-112: 0.000–0.054 at s = 0.2, and s ∈ [0.00, 0.08] (`instrument.txt` (2), (3); READOUT.md §2 as
    amended).
- **Brief item 5 (post hoc labels):** E4, M1, Z4 and the RBT-104 probes are labelled in the body. F12 and F17
  cover the gaps.
- **Brief item 6 (limits and next steps):**
  - All five must-list limits are present: holding is not invention; the patchy world changed births, income
    and turnover; SE-Z; A9; "shown passable".
  - All three must-list next steps are present.
  - §9 item 1 smuggles in one claim (F3).
- **RBT-105:** 5 of 14, 0.13–0.65, cited only in its permitted form. The A/A spread is correctly kept off the
  designed-fauna incomes.

---

## Bottom line

**NOT CLEAR.** MUST-FIX:
- **F1:** P1-805 contradicts "every compass that paid was planted at a = 64" (§0, §8).
- **F2:** §10's "the operator eroded it from every population", when five HU arms lost their lineages, three
  after reading above the bound.
- **F3:** §9.1's "rather than the operator", and "under the default operator in the patchy world it does".
- **F4:** the abstract, table and §10 drop A3's two required limits: the registered s-limit and SE-Z.
- **F5:** "in these two worlds" extends A3's uniform-world sentence to the patchy world.
- **F6:** post hoc M1's "would imply a per-generation advantage of that order", which its own recursion
  contradicts.
- **F7:** FUNCTION FOLLOWS in the summary table's "registered verdict" cell.

All seven are wording fixes. No new run is needed.

---

# Round 2: the amendment at `f11ea5a`

**What I checked:**
- the author's amendment commit on `results/RBT-114-paper` (`e9db310..f11ea5a`: the paper, `rederive.py` and
  `rederive.txt`);
- every changed sentence against the files and rulings it cites;
- the coordinator's 13:05 ruling on RBT-114.

I did not edit the paper or run a simulation, and I read nothing from RBT-107.

**Re-derivation.** `python docs/paper-10/rederive.py` at `f11ea5a` reproduces the committed `rederive.txt`
**byte for byte**. The diff adds three rows:
- **[W3q] and [W5q]** quote `prize.txt` l.25 and l.29 verbatim.
- **[P0]** parses the unusable pairs from `P1-readout.txt` (`P1-801`, `P1-7` and `S1-805: UNUSABLE`), so
  the usable list is no longer hard-coded (F28). The result, `[4, 804, 806, 807, 1, 2, 3]`, is unchanged.

## The round-1 findings, one by one

Each entry quotes the new sentence at `f11ea5a`.

| # | fixed as ruled? | the new sentence (abridged where long) | checked against |
|---|---|---|---|
| F1 | **yes** | §0: "Every compass that paid in a *scored* arm was planted at the paying magnitude. The one exception outside the rules is **P1-805**, a COMPASS line grown from the sub-paying w = 1 founders, whose pair is unusable … (not scored, and not food-dependent when uniform-scored, +0.529)". It is also in §3.3 and §8. | `P1-readout.txt` 805 row: "+0.529 -", "+1.942 FD, FOOD-DEPENDENT"; `P1-READOUT.md` l.94–99, "**Sensitivity**", "a single case, not a pattern" |
| F2 | **yes** | §10: "Where it paid less, it was held on no seed. Five of ten lost their planted-rooted lineages by season 599, three of them after reading above the operator-alone bound at 300. In the five where planted lineages survived, none of their living carried a paying compass." | probe B; the five survivors read k_planted = 0 and k_bare = 0 at 599 (`runs/RBT-112/readout.txt` HU rows) |
| F3 | **yes**, (a) as ruled | §9.1 heading: "Selection strength, not only the operator." Body: "under the default operator in the patchy world it is held above the operator-alone bound on 9 of 10 seeds." | the 12:20 ruling; the 13:05 ruling on F3(a) |
| F4 | **yes** | Abstract: "below ~0.1 per generation (the registered limit; the arms' own model-based likelihood puts it at **0–0.08** [Z10]). With the global biases frozen the host also changed (SE-Z failed), so a change in s itself is not handled." The table's A3 cell now carries both sentences, verbatim from `READOUT.md` §1. §10 adds "(model-based, for the frozen-bias host …; the registered limit is below ~0.1) … and a change in s itself is not handled." | `READOUT.md` §1; readout-adversary A3 |
| F5 | **yes** | "So, on this body **and in the uniform world**, … In the patchy world only the default operator was run, so this sentence says nothing about it." §9.1 and §10 ("**not spread**, in the uniform world") are scoped the same way. | 13:05 ruling on F5 |
| F6 | **yes** | "This does **not** say what s was in HP. HELD is read … at two finite depths, not at a balance, and under the same recursion it fires below the balance point (at S = 0, s = 0.089, just under 0.098, gives E#HELD ≈ 2 of 10 at ρ 0.10; `instrument.txt` (2)). So HP's 9 of 10 does not by itself imply s of that order." | `instrument.txt` (2), row 0.089: E#HELD 1.95 |
| F7 | **yes** | Table: "**FALSIFIED** (function FOLLOWS is reported beside the verdict, not in it)". | `readout.txt` l.42 |
| F8 | **yes**, as ruled | Abstract: "**The compass instrument is defined on the Pioneer's wheel layout.** RBT-103's report states that it raises on every holistic champion checked, though no committed file records which or how many (RBT-102 adversary F6: the holistic fauna has no wheel noses). Nothing here says whether an evolved body could carry a compass of another shape." | the 13:05 ruling's wording; probe A |
| F9 | **yes** | The abstract and the table's H8 cell now quote the full sentence, including "(u ≈ 0.29)", matching §4's verbatim block quote character for character. | h-adversary l.236–239; the 08:20 ruling |
| F10 | **yes** | "FALSIFIED-a's count (#HELD(HU) ≥ 5) would have been met with probability 0.834 … the verdict also needs the log-excess condition, which can only lower it". This appears in the table, §4 and §7. | `H-readout.txt` l.71, l.78 |
| F11 | **yes** | §10: "every line's champions were food-dependent through it"; "the best lines of half the uniform-world populations (5 of 10)". §0: "on five seeds of ten". §5.2's heading: "… on half the seeds". §6 HZ row: "used by the best on 5 of 10 seeds". | `H-READOUT.md` l.37–38; [Z2] |
| F12 | **yes** | Abstract: "**About two thirds of the operator's erosion is the global-bias walk** (the coordinator's 'about two thirds', 08:28 …; 68% of u(8) by this paper's post hoc division [E4])". The abstract and table label 31/70 as "a post hoc, print-only count from RBT-112's `sensitivity.txt` S1". | 08:28 ruling; `sensitivity.txt` header |
| F13 | **yes** | "At readings with n ≥ 10, … 0.48–0.60 at 300 and 0.22–0.38 at 599 … (seed 2 at 599, n = 3, needed every genome). On each HZ arm's own genealogy, on the six seeds with n ≥ 40 at both readings, the S = 0 null's 95th percentile is at or above B at every reading but one (seed 1 at 300)". See NOTE R2-N2. | `instrument.txt` l.28; readout-adversary l.111–112; probe E |
| F14 | **yes** | "H is 'holding, not de novo evolution' (the 08:20 ruling on RBT-106, Chaotic)". This appears in §0, §8 and the abstract. | the 08:20 ruling |
| F15 | **yes** | "**Caveats, recorded in the report (H3 and H4, as the 08:20 ruling required)**". F12/H5 now sits under the adversary's findings, with H5's caveat quoted verbatim. | `H-READOUT.md` l.48–56; h-adversary l.183–184 |
| F16 | **yes** | "… before launch, 'and show it can pass' (02:00, Chaotic)". | Chaotic RBT-104, 02:00 |
| F17 | **yes**, as ruled | "**Why: the report's post hoc account** (… which heads it as POST HOC probes …). Bullets 1–3 are all post hoc". The power is "a counterfactual figure, **the report's, not a reading**", in §3.2 and §7. F4 is "post hoc and of record (… adopted at 01:52 and recorded at the 02:00 closure)". The sources (`sat_probe.txt`, §1.2; the probes, §1.3) match READOUT-ADVERSARY's section heads. See NOTE R2-N1. | 13:05 ruling on F17 |
| F18 | **yes** | "+1.259 [+0.900, +1.617] … [W3q]"; "+1.537 against +1.308 [W5q]". | `prize.txt` l.25, l.29 |
| F19 | **yes** | Three additions: "the worst case over q, with q_U = q_P, is 0.132 at q = 0.5 (H7)"; the HP-807 caveat "may be carried by its host's own compass" in §4 and §7; and the HU seeds "804 (k_planted 3 > B 1), 805 (2 > 1) and 7 (3 > 2), read above the operator-alone bound at 300 before the lineage vanished". | h-adversary l.217–218 (under H7), l.152–153; probe B |
| F20 | **yes** | "with ρ profiled, an MLE of s = 0.01 … (`instrument.txt` (3), 'rho profile' line …). `READOUT.md` §2's 'The MLE is s = 0.00' is the ρ = 0.10 line of the same section, whose interval is [0.00, 0.03]." | `instrument.txt` l.52, l.54 |
| F23 | **yes** | "`PREREGISTRATION.md`, 'Three corrections to the ticket's premises', item 3; §3.3" and "… item 2; §4". "`READOUT-ADVERSARY.md` §5.1(i). The mechanism is in its §5.2". A5's seed-4 champions are cited "(A4)". The ruling's "not the only difference" is quoted, with H8's own phrase beside it. | PREREGISTRATION l.35–47; READOUT-ADVERSARY l.252, §5.2; readout-adversary l.223 (A4) |
| F24 | **yes** | "median transmission 0.39–0.60 across P1 arms and 0.35–0.61 across S1 arms, 0.390–0.443 on the three failing ones"; and usability adds "analyse.py's control passed". | `P1-READOUT.md` l.61–62; `f12.txt` l.289, l.294, l.307 |
| F26 | **yes** | "Paper 5's positive result, evolved locomotion and a heritable foraging yield". | paper 5, abstract |

The optional NOTEs F21, F22, F25 and F28 were also applied, and each one checks out:
- **F21:** "the likelihood treats the two readings as independent".
- **F22:** "0.005 at n = 40, the anchor `READOUT.md` names as relevant; 0.108 in the genealogy scenario, where
  the count would read FALSIFIED-ROOTS". This matches `READOUT.md` l.70–71 and PREREGISTRATION l.540. M15's
  0.214 is sourced to the design adversary.
- **F25:** RBT-103's residuals (a) and (b), matching `REPORT.md` l.95–96.
- **F28:** the new row [P0].

## New overstatements, or numbers that do not trace

Every new number traces:
- W3q and W5q;
- P0;
- E#HELD 1.95 at ρ 0.10;
- the ρ = 0.10 interval [0.00, 0.03];
- 0.35–0.61 and 0.390–0.443;
- 0.132;
- the HU readings at 300 (3 > 1, 2 > 1, 3 > 2);
- "0 of 200".

No fix introduced a new overstatement.

My re-read of the whole amended paper found one sentence that **predates the amendment** and that I missed in
round 1.

**R2-F1 (MUST-FIX). §10, closing paragraph: "So the planted compass is **held** where it pays enough, …"**
- The sentence reads: "So the planted compass is **held** where it pays enough, **used** by the best where the
  operator leaves it, and **not spread**, in the uniform world, where selection on it is weak."
- "Held where it pays enough" makes the prize the reason for holding. That is the claim H8 narrowed, and the
  ruling forbade it:
  - "The first readout said … 'the size of the prize decided' holding. That is false by the readout's own
    side effects" (the paper's own §4);
  - "not the only difference" (the 08:20 ruling);
  - RBT-114's brief: "Where an adversary narrowed a claim, use the narrowed form: RBT-106 H8".
- The paragraph just before it has the narrowed form: "in a world that was also richer and bred faster". The
  summary sentence drops it.
- **Fix:** "So the planted compass is **held** in the world where it pays about 2.5× more, which is also
  richer and faster-breeding, **used** by the best where the operator leaves it, and **not spread**, in the
  uniform world, where selection on it is weak."
- This is one clause. No number changes.

## NOTEs, optional

**R2-N1. §3.2: "The ruling cites RBT-104 as 'VOID; the instrument could not see' …"** The 01:52 ruling said
"Paper 10 cites RBT-104 only as …". It was an instruction to this paper, not the ruling's own citation.
Suggested: "The ruling had this paper cite RBT-104 as …".

**R2-N2. §5.2, A1: "The 300 reading was binding on 7 of those 8 seeds."** The amendment removed "the eight
seeds that were neither HELD nor LOST", so "those 8 seeds" no longer has an antecedent. Suggested: "on 7 of the
8 seeds that were neither HELD nor LOST".

## Checks

- `rederive.py` at `f11ea5a` reproduces `rederive.txt` byte for byte.
- `probe_paper.py` reproduces `probe_paper.txt`.
- Suite on this branch: **364 passed**, in a clean `.[dev]` venv with no scipy.

## Bottom line, round 2

**NOT CLEAR.** One MUST-FIX remains:
- **R2-F1:** §10's closing "held where it pays enough" restates the prize-decided reading that H8 and the
  08:20 ruling narrowed. The fix is one clause.

F1–F19 are fixed as ruled, and so are F23, F24 and F26. No new number fails to trace. With R2-F1 applied as
proposed, I would read the paper as CLEAR. R2-N1 and R2-N2 are optional.
