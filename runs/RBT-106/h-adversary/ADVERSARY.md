# RBT-106 H readout adversary: PR #354 (`results/RBT-106-H-readout`, head `a7cf94c`)

*Readout adversary, 2026-09-27. POST HOC throughout: nothing here changes a registered rule or number.*
- `runs/RBT-112/gate.py` was not run. No arm, and nothing on #354's branch, was modified.
- The probes ran from a scratch worktree of `a7cf94c` with `rabbitstew/` checked out at c872e80 (tree `9cc84cde`),
  in a clean `.[dev]` venv without scipy, on x86_64 with MuJoCo 3.14.0 and numpy 2.4.6.
- All 20 H arms were restored from `ckpt/rbt-106-ARM-SEED` (`replicate.sh` records every command).

## Overall verdict: **CONFIRMED-WITH-CAVEATS**

**VERDICT H: SUPPORTED stands.** I attacked it on five fronts and it held on each:
- **HELD is not demography.** Run on each patchy arm's **own** genealogy, the no-selection null gives HELD in
  0.7% of replicates (full operator) and 1.3% (mutation only). The registered rate is 1.0%.
- **The function is the planted unit steering by smell.** The planted unit's input carries 99–101% of the compass
  gain on two F12-flagged and two unflagged arms. Other units carry none of it, and the drifted bias's resting drive
  earns nothing by itself.
- **Every number re-derives** with independent code.
- **`b8edb98` prints only.**
- **The files are replicable.** 40 of 40 `held-*.txt` and 3 of 3 function readouts regenerate byte-identically.

**One MUST-FIX, wording only (H8).** H-READOUT.md's plain-words paragraph says "with the erosion the same and only
the prize different". That is false by the readout's own side effects: the patchy world also raised births, income
and depth. **Three CAVEATs** (H3, H4, H5).

| # | finding | class |
|---|---|---|
| H1 | HELD's null is valid for HP: own-genealogy null 0.7% / 1.3%; n and B match each arm's; HU's non-HELD is not only lineage loss | NONE |
| H2 | The FD function is the planted unit acting as a compass (split lesion), on flagged and unflagged arms | NONE |
| H3 | In drifted arms, HELD and function score different genomes: HP-806's champions are 0/7 `pay32` hits yet steer through the planted unit | CAVEAT |
| H4 | HP-807's install control passes, but the install's own increment is not detected; dropping HP-807 still gives SUPPORTED | CAVEAT |
| H5 | F12 applied exactly as registered; the flagged arms' controls are genuine (install increment detected on all three) | NONE (the heuristic's premise failed, CAVEAT for future use) |
| H6 | `readout.py`: only printing since the registered state (d114d87 → a7cf94c) | NONE |
| H7 | Arithmetic: every H number, the power table and the sensitivity re-derived exactly | NONE |
| H8 | "only the prize different" / "the prize decided" overstates what one flag isolated | **MUST-FIX (wording)** |
| H9 | Hold vs evolve: no sentence claims de novo evolution | NONE |
| H10 | Replicability: 40/40 held files, 3/3 function readouts, 242/242 evidence files identical | NONE |

## H1. Is HELD's null right for HP? (attack 1) — NONE

**The concern.** The registered null (`null_rates.txt`, `pay32` 1.0%) ran the operator down **part 2's** ten
genealogies, from the uniform world with no compass anywhere. HP's genealogies differ:
- 1,668–1,861 births against HU's 1,132–1,341;
- deeper windows;
- the living collapse onto 1–3 planted roots (n = 60 of 60 at 599 on six HP arms).

Clustered descent inflates the variance of k, and B is binomial. So HELD could fire on HP's demography alone.

**The direct test** (`ownnull/`, `ownnull_pool.py` → `ownnull_pool.txt`):
- **The null.** The design adversary's `null_xover.py`, unchanged, run on **every H arm's own `lineage.jsonl`**, with
  that arm's own w = 32 founders (`founders.py`; digests match), 100 replicates per arm, under both operators.
- **Re-scoring.** `null_xover.py` prints HELD under the *registered* k > B, so `ownnull_pool.py` re-scores every
  replicate under the *amended* rule (k_planted > B at 300 and 599).
- **The conditioning is exact.** For all 20 arms, the null's n and B at 300 and 599 equal the committed held files'
  (asserted). So the table *is* conditioned on each arm's own genealogy: its n, its depths, its roots.

| | no-selection HELD, full operator | mutation only | per-arm range (full) |
|---|---|---|---|
| **HP, own genealogies** | **7/1000 = 0.7%** | 13/1000 = 1.3% | 0–4 of 100 |
| HU, own genealogies | 2/1000 = 0.2% | 9/1000 = 0.9% | 0–1 of 100 |
| registered (part 2's genealogies) | 1.0% | 1.0% | |

**What this rules out.** At q = 0.013:
- P(SUPPORTED's count) = 2.2 × 10⁻⁴;
- P(#HELD(HP) ≥ 9) ≈ 10⁻¹⁶ (`rederive.txt`).

HP's deeper, more clustered genealogies do not make HELD fire, so **demography does not produce HP's HELD**.
- On 7 of the 9 HELD HP arms, the observed k_planted at 599 exceeds **every** one of 100 own-genealogy null
  replicates. The exceptions are HP-806 (7 against a null max of 9) and HP-1 (6 against 8).
- Those two are clustering tails at a single season. The null reaches HELD at both seasons on them in only
  0/100 and 4/100 replicates.

**HU's "not held" is not just lineage loss.**
- In five HU arms the planted-rooted lineages were lost by 599 (n = 0).
- In the other five they survived, with n = 19–60 (HU-1: 60 of 60 living, HU-2: 56), and **every one** reads
  k_planted = 0.
- So in the uniform world the compass was eroded out of surviving planted lineages too.

**What the conditional null does not cover.** HP's genealogy is itself shaped by selection: planted roots took over.
This null asks the right question for "held": *given who lived, did the compass outlast the operator?* It does not
separate why the planted roots won. That is part of the effect, not an artefact.

## H2. Is the function the planted compass? (attack 2) — NONE

**Why the registered attribution is not specific.** `function.py`'s lesion cuts every nose → global link, so it
does not say *which* unit steers. F12's flagged arms carry the planted unit with a drifted bias (resting drive 3–7),
which could pay as a static turning bias.

**The probe.** `attrib.py` splits the lesion on the same bests, harness and 64 paired seeds, importing
`function.py`'s `bout`. It ran on two flagged arms (HP-806, HP-805) and two unflagged (HP-4, HP-3), restored at
c872e80. Every value is a t(n − 1) interval over bests (`attrib/`):

| arm | F (reproduces function-patchy) | gain, all nose links cut | **gain, planted unit's input only** | gain, other units' input | resting drive alone (input cut − unit removed) | intact − bias reset to 0 |
|---|---|---|---|---|---|---|
| HP-806 (F12) | +3.652 | +4.252 | **+4.299 [+2.231, +6.368]** | +0.042 [−0.061, +0.146] | −0.317 [−0.908, +0.274] | +2.507 [−1.091, +6.104] |
| HP-805 (F12) | +3.228 | +3.676 | **+4.203 [+1.584, +6.822]** (6 bests) | +0.000 | −0.021 [−0.333, +0.291] | +1.740 [−1.359, +4.838] |
| HP-4 | +5.763 | +6.246 | **+6.203 [+5.245, +7.161]** | +0.127 [−0.184, +0.439] | +0.098 [−0.653, +0.850] | +1.212 [−1.166, +3.590] |
| HP-3 | +4.759 | +5.545 | **+5.547 [+3.851, +7.243]** | +0.016 [−0.023, +0.054] | 0 (b = 0 in every best) | 0 |

The planted unit is identified per best as the nose-fed global unit with an output weight of |v| ≥ 16 to a drive
Effector. Its share of the compass gain is **1.01, 1.00, 0.99 and 1.00**.

**Reading.**
- **It is the planted unit.** Cutting only its input removes the whole gain, and cutting every other unit's input
  removes none.
  - Other nose → global links are rare: 4 of 28 bests carry any. So `function.py`'s lesion was in practice already
    specific to the planted unit.
  - HP-805's g350 carries no planted unit; it is 1 of 7 bests and enters the full lesion only.
- **It is steering by smell, not a turning bias.**
  - With the input cut and the drifted bias kept, the unit's constant drive earns nothing beyond removing the unit
    (−0.32 to +0.10, every interval spans zero).
  - The decoy retains 0.1–15.4% across HP lines (`rederive.txt`), under the 25% rule.
- **The drifted bias is co-adapted, not a defect.** Resetting it to 0 *lowers* income on drifted bests. For
  example, HP-806 g450 falls from 6.33 to 0.14, and g590 from 6.97 to 1.89. The rest of the evolved brain works
  around the resting drive. This is why RBT-104 readout adversary §5.2's expectation ("the drift cripples the
  host's gait… a population's best is unlikely to be one") failed here.

## H3. HELD and function score different genomes in the drifted arms — CAVEAT

`held.py`'s hit reads the planted unit's links alone (`links_alone_a`). A resting drive above ~1 saturates the
Effector in isolation, so a drifted unit reads as lost. Own-links of the window champions:

| arm | g300 | g350 | g400 | g450 | g500 | g550 | g590 |
|---|---|---|---|---|---|---|---|
| HP-806 | +11.4 | none | −0.7 | −0.0 | −0.3 | −13.8 | −0.2 |
| HP-805 | +29.4 | none | −6.9 | −3.6 | none | −10.5 | −14.1 |
| HP-4 | +5.3 | +22.6 | +14.5 | +17.4 | +12.7 | +17.0 | +17.0 |

A `pay32` hit needs |a| ≥ 12.52 with the root's sign.
- **HP-806's seven champions include no `pay32` hit** under either sign, yet all steer through the planted unit
  (H2). Its HELD rests on 7 non-champion members.
- **Consequence for the verdict: none.** HELD is structural and uses the same criterion in both worlds and in the
  null.
- **Consequences for the wording.**
  - "nine of ten held it" and "all ten lines' champions are food-dependent through the compass" count different
    genomes. HELD **under-counts** what selection kept working in HP.
  - The operator-alone erosion (u ≈ 0.29 per generation) treats a bias step as loss, but evolved hosts keep such
    units working.
- H-READOUT.md already notes this (its "detail on the drift"). I ask only that the plain-words paragraph not
  equate the two counts.

## H4. HP-807's install control — CAVEAT

In HP, the host's own compass adds to the installed one, so a control could pass on the host alone. Both
`function-pc.txt` and the arm's own-world file score the same 7 bests on the same 64 paired seeds.
`control_increment.py` computes, per body, F(control) − F(own), which is what the install adds, with t(6) over
bodies (`control_increment.txt`):

- **The install is detected on 9 of 10 HP arms**, including all three F12-flagged ones:
  - HP-804 +1.509 [+0.341, +2.677];
  - HP-805 +1.971 [+0.712, +3.230];
  - HP-806 +1.172 [+0.288, +2.055].
- **HP-807's increment is +0.935 [−0.124, +1.995]: not detected.** Its pass may be carried by its host's own
  compass. HP-807 is the one HP arm not HELD. It counts as a COMPASS line and enters the paired intervals.
- **In HU**, own F is about 0, so a pass is the install itself. Three HU increments are not significant on their
  own, but their controls pass on the registered rule.
- **Under the registered rule (§6.1) HP-807 is usable.** This is a stricter post hoc reading and is not scored.

**Sensitivity** (`rederive.txt`):

| subset | n | HELD HU, HP | paired log-excess | verdict |
|---|---|---|---|---|
| without HP-807 | 9 | 0, 9 | +2.496 [+2.081, +2.912] | **SUPPORTED** |
| without HP-804, 805, 806 (the designer's) | 7 | 0, 6 | +2.304 [+1.257, +3.352] | SUPPORTED |
| without all four | 6 | 0, 6 | +2.699 [+2.197, +3.201] | VOID (n < 7) |

The last row falls below MIN_USABLE only by construction of this post hoc drop. Its counts are unchanged in
direction.

## H5. Usability and F12 — NONE (CAVEAT on the heuristic's premise)

- **F12 is applied as registered.** My own parse of `f12-H.txt` reproduces every flag:
  - "≥ 4 of 7 bests with a planted-type unit driving > 1, or median T < 0.10" gives HP-804 4/7, HP-805 6/7 and
    HP-806 7/7;
  - every other arm is at 0–3/7;
  - median T is 0.273–0.743.
- **The controls are genuine, on each arm's own founders' descendants.** Every control:
  - installs on the arm's own 7 bests, with every sign determined (7 bodies each);
  - passes the zero-count veto (68–143 of 448 zeros);
  - sits beside an analyse.py control that passes;
  - is on c872e80's tree (`commit.txt`, re-checked).
- **The designer's handling is correct.** Usability is the control (§6.1), and the flag was reported, not acted on.
  H4 confirms that the flagged arms' installs are detected.
- **CAVEAT for future use:** the heuristic's premise, that resting drive > 1 masks the control, failed on evolved
  hosts. The drift is co-adapted (H2). Don't reuse it as a masking criterion without the increment test.

## H6. `b8edb98` — NONE

- **`git diff d114d87 a7cf94c -- runs/RBT-106/readout.py`**, from the last registered state (the scipy-lazy fix
  after the 22:40 amendment) to #354's head, adds:
  - the usability print;
  - `--no-peek` (90fd963, ruled on by the P1 adversary);
  - `predictions_p` and `predictions_h`, and their two call sites after `VERDICT` is printed.
- **Unchanged:** every constant (MIN_USABLE, H_HELD_GAP, H_HELD_MANY, FEW, P_FD_MANY, REF_TREE), `held()`,
  `function()`, `read_arm()`, the `use` filter, the counts and the verdict branches.
- `predictions_h` reads only `held-150.txt` and `power.py` and returns nothing. It cannot change a verdict.
- One printed label says "~3x prize" in FALSIFIED-a's text. It predates H and never fires here.

## H7. Arithmetic — NONE

`rederive.py` → `rederive.txt` re-derives everything from the committed per-arm files. It uses its own regexes, its
own Student-t quantile (t₉ = 2.262157, t₆ = 2.446912) and its own binomials, and imports nothing from `readout.py`,
`held.py` or `power.py`. It needs no scipy.

- **The primary numbers:**
  - HELD HU 0, HP 9, with every B recomputed from n and μ;
  - log-excess +2.240 [+1.556, +2.925];
  - COMPASS lines HU 0, HP 10, with primary calls and attributions re-derived from the printed intervals, zero
    counts and decoy share, not the labels;
  - paired F: patchy +3.858 [+2.965, +4.750], uniform +0.925 [+0.610, +1.241];
  - lesion gain HU +0.520 [−0.041, +1.080], HP +4.804 [+4.059, +5.549];
  - income +1.771 [+1.419, +2.122]; births 10/10;
  - the gate (HP-801: 15 > 11; HP-4: 30 > 10);
  - the n = 7 sensitivity.
- **Usability:** 10/10 re-derived from seasons.txt, platform.txt, rbt102.txt, function-pc.txt and commit.txt.
- **H-0:** the registered wording scores "SUPPORTED occurred". The registered lean toward FALSIFIED-a was wrong,
  as stated.
- **Power / size:** the n = 10 table reproduces to 3 d.p. The "≤ 0.020" size holds at q ≤ 0.08; the worst case over
  q (q_U = q_P) is 0.132 at q = 0.5. H1 measures q ≈ 0.01 on HP's own genealogies, giving a size of 2.2 × 10⁻⁴.
  The claim stands.

## H8. Wording — MUST-FIX (H-READOUT.md and the ticket post)

**H-READOUT.md l. 34 and 40, and the ticket post's "So the prize decided holding".** "The operator erodes the
compass at the same rate in both" and "**With the erosion the same and only the prize different**, the size of the
prize decided…". This is contradicted by the readout's own side effects. The one flag (`--food-patches 3`) also
changed:
- births: HP more on 10/10 seeds, 1,668–1,861 against 1,132–1,341;
- window income: +1.771;
- window depth.

The operator's rate is the same **per generation**, and HP breeds more generations per season. So per season the
erosion was, if anything, higher in HP. That strengthens the result, but it makes "only the prize different" false.
The design isolates *patchiness*. The ~2.5× prize is its measured, hypothesised mechanism (§2, §3.3), not the only
thing that differed.

**Required replacement** (or equivalent): *"The operator erodes the compass at the same rate per generation in both
worlds (u ≈ 0.29), and the patchy arms bred more generations. In the world where a working compass pays about 2.5×
more, which also raised income and turnover, the paying compass was held on 9 of 10 seeds; in the uniform world on
none."* The ticket post should say the patchy world, where the compass pays ~2.5× more, held it, rather than "the
prize decided".

The registered verdict label ("the larger prize held the paying compass…") is the pre-registration's and stays.

## H9. Hold, not evolve — NONE

No sentence in H-READOUT.md or the designer's ticket post claims de novo evolution.
- The Scope paragraph says H "says nothing about whether the prize makes a compass from a sub-paying structure", and
  points to P-NULL.
- "Each population evolved for 600 seasons" describes the run.
- The k_bare line ("spread the compass across lineages") correctly says crossover transfer, not origin.

H3 bears on "held": what was held was a planted compass that stayed working as its bias drifted. That is consistent
with holding, and is not new evolution of a compass.

## H10. Replicability (attack 7) — NONE (`replicate.txt`)

- **`held.py` at 300 and 599 on all 20 restored arms:** 40 of 40 byte-identical to the committed files.
- **Function readouts, byte-identical:**
  - HP-806 (flagged) and HP-4, via `function.py` in their own world;
  - HU-4, via `cross_world.py` patchy (`replicate/`).
- **Every committed evidence file of the 20 arms** equals the checkpoint's copy: 242 of 242.
- `attrib.py`'s intact/decoy/full-lesion rows reproduce each arm's committed per-body `function-patchy.txt` table.

## Files

| file | what |
|---|---|
| `ADVERSARY.md` | this |
| `rederive.py` → `rederive.txt` | H7, H4 sensitivity, and the size at the own-genealogy null |
| `ownnull/ownnull-ARM-SEED.txt` | H1: `adversary/null_xover.py` (unchanged) on each arm's own genealogy, 100 reps |
| `ownnull_pool.py` → `ownnull_pool.txt` | H1: amended-rule re-scoring, pooled rates, observed against its own null |
| `attrib.py`, `attrib/attrib-HP-*.txt` | H2: split lesion (planted input / other inputs / unit removed / bias reset) |
| `control_increment.py` → `control_increment.txt` | H4: what each install adds per body |
| `replicate.sh`, `replicate.txt`, `replicate/` | H10: the commands run, and the regenerated files |
