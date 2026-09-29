# RBT-129 amendment F: founding (DRAFT, for adversary and ruling)

> ## ⚠ DATA-INFORMED: written after the Stage 0 census and the Stage P pilot were read (#490, #491)
>
> The author has read the census layer, `founders.txt` (both versions), `stage1_points.txt`, `power_eff.txt` and the
> pilot's per-seed outcomes. Every choice below was made knowing that holistic draws 129002, 129003, 129007 and 129008
> die by season 14 at `c0-p030-U-L`, and knowing which Stage-1 points lose a fauna on seed 129001. Nothing here is
> pre-data. Readers should weigh each choice as a choice made after seeing the data.
>
> **Status: DESIGN ONLY.** Nothing has run for this amendment, and nothing runs from this file. Stage 1 stays on hold
> (coordinator ruling on #490, comment 5880596624, item 4) until: this amendment passes its adversary, the coordinator
> rules on it, the owner approves its cost, and the owner separately decides to launch.
>
> Date: 2026-09-29. Base: `b4f10e7`. The numbers come from `founding-amendment/founding_expect.py` →
> `founding_expect.txt`, which reads committed text outputs only and runs no simulator.

## 0. In one table

| question | answer | § |
|---|---|---|
| recommended option | **(a) a per-seed founder screen**. Each fauna's RNG stream at seed j is redrawn from a registered salt sequence until that fauna founds at one benign anchor. The rule is symmetric: both faunas face it. | 2, 3 |
| anchor | **W118-b = `c0-p030-U-L`**: one point, under the sweep's block and `--fair`, arm S, seasons 0–59. It is not a Stage-1 point. | 3 F1 |
| criterion | the fauna has ≥ 1 member alive at season 59 in its own ecology, counted before same-season refill. This is §5.1's census founding definition, unchanged. | 3 F2 |
| sub-stream | holistic: the existing `holistic_stream_salt` s (spawn key (holistic index, s), RBT-96). Designed: a new `designed_stream_salt` t built the same way (RBT-129c). Both are tried in order 0, 1, 2, … and the first that passes is kept. | 3 F3 |
| cap | 20 redraws (salts 1–20). A capped fauna keeps salt 0 and is labelled SCREEN-CAPPED. Its seed enters Stage 1 under the registered rules. If ≥ 3 of the 16 seeds are capped, Stage 1 does not launch. | 3 F4 |
| seeds | 129001–129016 keep their numbers. All 16 are screened **before Stage 1**, so R-B's seeds 9–16 are fixed in advance and nothing collides. | 3 F5 |
| resume | 129001 resumes from the census S 0–59 at all 36 points: both salts are 0, so it is the same run. Every other seed runs fresh from season 0. The designed half of 129002/129003 is byte-compared with the census (K-SALT). | 3 F7 |
| §6.1 | unchanged. The thresholds are generalised to any n: EXCLUDED at ≥ ⌈5n/8⌉ seeds, PARTIAL at < ⌈3n/4⌉ valid seeds. Both formulas reproduce 5/6 at n = 8 and 10/12 at n = 16. | 4 |
| expected valid seeds at n = 8 | **about 7.7 of 8** at the 24 points where 129001 has both faunas at season 59 (6.0 on the pessimistic transfer rate). **About 0.3** at the other 12 points. Registered, without the amendment: 3.9 and 0.15. | 5 |
| expected calls | about 22–23 of 24 points escape PARTIAL (17 on the pessimistic rate). The 12 world-lethal points stay survival calls (EXCLUDED-H, EXCLUDED-D or NEITHER) **by design**. Under shuffle the share layer remains SATURATED or NOT RUN at most points (§6.2). | 5 |
| income power at \|H − D\| = 0.4, BH half | at a point with 8 valid seeds: **0.826** at SD 0.334, **0.939** at SD 0.275. Mean over the 24 points: 0.790 / 0.902 (0.636 / 0.774 on the pessimistic rate). Registered: 0.381 / 0.510. | 5 |
| cost | screen: **about 5–14 core-h expected, ≤ 47 worst case**. Stage 1 gated at n = 8: **878–985 core-h** at 23.35 core-s, **1,504–1,611** at 43.72. That is +28 / +52 over the registered figure, because the census resume is lost for 129002 and 129003. | 6 |
| what it can claim | the comparison is between faunas **established from founder draws that found at W118-b**. It says nothing about unscreened holistic founders. Founding itself becomes a separately reported layer. | 2 |

## 1. The problem (facts, with sources)

- **The holistic founders are one draw per seed across all 150 points** (`stageP0-readout/founders.txt`; adversary
  SHOULD 5). `ecology.py` never re-seeds a population.
- **Draws 129001–129008 at W118-b** (`stageP0-readout-adversary/founders.txt`):
  - holistic alive at season 59: 60, 0, 0, 60, 60, 58, 0, 0;
  - the four failing draws are last alive at seasons 10, 14, 14 and 14;
  - the designed fauna is alive at 59 on **all 8 draws** (58–60 each).
  So 4 of 8 holistic draws found (q ≈ 0.5, 95% CI about 0.16–0.84) and 8 of 8 designed draws found.
- **129002 and 129003 die at all 150 census points.** Their failure is a property of the draw, not of the world.
- **129001 loses a fauna by season 59 at 12 of the 36 Stage-1 points** (`stage1_points.txt`):
  - holistic lost at 8 PW-G points and at `c1-p080-PW-L`;
  - designed lost at `c2-p080-U-G`, `c2-p080-HP-G` and `c1-p030-PW-L`.
  - At those points the designed fauna also dies on the other census draws, and in the pilot a second founding draw
    (129004) dies at `c2-p030-PW-G` (both faunas, season 32). It survives to the merge at `c1-p030-PW-G` but is extinct
    by the window.
  **These are world-driven losses.** Screening at a benign anchor cannot remove them, and should not: they are the map's
  survival layer.
- **The designed fauna is FOUNDING-FAIL at 34 of 150 census points** (26 PW, 5 U, 3 HP). The same argument applies: the
  designed founders are fine at W118-b on every draw, so these losses come from the worlds.
- **Consequence under §6.1** (READOUT-STAGEP0 §5; ruling item 3): every Stage-1 point is PARTIAL or EXCLUDED at n ≤ 12.
  The body call cannot be made at any n the registration allows.
- **A second consequence the readout did not state.** §5.2's M/N gate requires "neither fauna FOUNDING-FAIL". With the
  holistic fauna FOUNDING-FAIL at 150 of 150 points, **no M or N arm would run anywhere**, so the one-world income column
  and the share layer are empty whatever n is. §7 (T5) below amends the gate.

## 2. The options compared

The founding failures are of two kinds, and they must not be confused:
- **draw failures**: a holistic founder set that dies everywhere, even in the most benign world;
- **world failures**: an established fauna that a harsh world kills.

A founding fix should remove the first and leave the second alone. A world failure is a finding: EXCLUDED and PARTIAL are
how the map reports it.

### 2.0 What any screen does to the claim (RBT-121 synthesis rules)

Screening for viable founders **changes the population being compared**:
- without a screen, the comparison is "holistic evolution from random founders" against "designed evolution from random
  founders";
- with a screen, it is "holistic evolution from founders that can establish at W118-b" against the designed equivalent.

Here the screen bites only on the holistic side (0 of 8 designed draws fail, 4 of 8 holistic draws fail). Its effect is
therefore asymmetric even though the rule is symmetric.

**What the screened comparison can claim:**
- among founder draws that establish in a benign flat world, which body earns more where (EARNS-*), and which gains share
  where a share call is resolvable (WIN / TIE);
- where an **established** fauna of each body dies (EXCLUDED, PARTIAL). This is a stronger world statement than before,
  because the founders are known to be viable elsewhere.

**What it cannot claim:**
- **anything about unscreened holistic founders.** It cannot say how often random holistic founders get evolution
  started (the answer, "about half of draws die by season 14 in the most benign world", is its own layer, below). It
  cannot say that "the holistic body" earns or persists from a random start;
- **that the bodies are compared at equal founding luck.** The designed body gets establishment for free on every draw;
  the holistic body gets it by selection;
- **that the screened founders are representative of holistic founders at other worlds.** The screen selects on
  establishment in a flat, uniform, legacy-smell world. It may favour founders suited to that world. The PW and G-smell
  points are therefore read with screened founders that were never selected there.
- **that only the founders were selected.** The salt replaces the whole holistic stream (RBT-96), so the screen also
  selects the stream's first seasons of groupings and breeding draws at the anchor. Those draws do not transfer to other
  worlds, where the stream meets different terrain and food; the founders do.

**How the RBT-121 rules apply:**
- **R5 (state the regime):** founding is part of the regime. Every map, table and verdict states "founders screened at
  W118-b (amendment F)". The screen's rejection rate per fauna is reported as the **founding layer**, beside the census's
  FOUNDING-FAIL layer.
- **R6 (state the parity), by analogy:** every holistic-against-designed statement says it is made at screened
  founding. It is never made at unscreened founding.
- **R10 (a manipulation prints its side effects against the control):** at W118-b, the accepted and rejected draws of
  each fauna are printed side by side over seasons 0–14 (founder solvency, node count, income, births). The designed
  half of every salted holistic run is byte-compared with its unsalted twin (K-SALT, F7).
- **R11 (no single seed carries a claim):** today the census's founding layer rests on 129001 at most points, and the
  valid-seed count, not the bodies, decides every Stage-1 call. The screen removes that. The transfer estimate in §5
  itself rests on one or two draws, and is labelled as such.
- **R12 (the record keeps its evidence):** the census's holistic FOUNDING-FAIL at 150 of 150 stays in the record. It is
  not relabelled. Stage 1 stands **beside** it; it does not override it (T3).

### 2.1 The comparison

The expected-valid, calls and power rows are from `founding_expect.txt`. "Plug-in" and "pessimistic" differ only in how
the anchor-to-point transfer rate is estimated (§5).

| | **(a) per-seed screen at W118-b** | (b) founding runway | (c) per-point screen | (d) replace failing draws by the next seed numbers |
|---|---|---|---|---|
| what | at each seed, each fauna's stream is redrawn (salt 0, 1, …) until the fauna founds at the one anchor; the salts then hold at every point | a protected establishment period (for example, no living cost and no starvation deaths for seasons 0–R) before competition, at every point | at each point and seed, the holistic stream is redrawn until it founds **at that point** | a seed whose draw fails at the anchor is dropped, and the next seed number takes its place |
| fairness between faunas | symmetric rule; so far it bites only on the holistic side (§2.0). Justified: the question needs two established populations, and the asymmetry is reported as the founding layer | symmetric in form; in effect a subsidy to whichever fauna fails to earn early, which is the holistic one | symmetric in form. In effect it bites only on the holistic side, and hardest at the harsh points | the screen is on the holistic fauna, but a new seed number redraws the **designed founders and the terrain stream too**, so they are selected jointly with holistic founding |
| selection bias | on establishment at one benign world, which is **not** a Stage-1 point; see §2.0 | none by selection, but it changes the world at every point and masks early world-driven deaths, so EXCLUDED changes meaning | **selection on the outcome at the measured point.** Survival there is true by construction, so EXCLUDED-H becomes impossible short of the cap, and the survival layer is erased | as (a), **plus** the shared terrain stream is selected. Terrain sequences that favour holistic founding carry over to every Stage-1 point through §5.2's common seeds |
| §5.2 common seeds | **kept**: one (seed, salt_H, salt_D) per j at every point | kept | **broken**: founders differ by point, so the axis contrasts lose their pairing | kept, but with different seed identities |
| E[valid] at n = 8, 24 points where 129001 has both faunas (plug-in / pessimistic) | **7.67 / 6.03** | not estimable from existing data. If the runway only delays death (the failing draws die at 10–14, about when the founders' own energy runway ends), the registered 3.9; if it rescues every draw, about (c) | 7.67 / 7.67 | 7.71 / 6.06 |
| E[valid], the other 12 points | 0.29 / 0.78 | as above | 1.97 / 2.72, bought by selecting at the point itself | 0.27 / 0.76 |
| §6.1 calls | benign points: about 22.5 of 24 escape PARTIAL (17.0 pessimistic); `c1-p080-U-G` is PARTIAL-H because the designed fauna dies; world-lethal points: EXCLUDED or NEITHER | unknown until a feasibility run | PARTIAL escaped at some lethal points only by selection; EXCLUDED-H cannot be called | as (a) |
| income power (mean over the 24; SD 0.334 / 0.275) | **0.790 / 0.902** (0.636 / 0.774) | unknown | 0.790 / 0.902 | 0.795 / 0.908 |
| R-B seeds 9–16 | **no collision**: seeds 9–16 keep their numbers and are screened now | no collision | no collision (salts) | **collides**: "the next seed numbers" are 129009+. R-B must move (for example to 129101+) and be re-registered, and the RBT-118 coordination changes |
| resume from census states | 129001 only (salts 0) | **none**: the census ran without a runway | 129001 only, at points where it founds | 129001 only |
| cost of the screen | 5–14 core-h expected, ≤ 47 | new code, a feasibility run, and R extra seasons at every arm (+4% at R = 12) | high: 36 × 8 screens, many at PW points to the cap (q low); up to about 380 core-h | as (a), but screens are two-fauna runs, and the terrain is redrawn |
| code | RBT-129c: a designed salt, and both salts wired through `ecology` and `stages.py` | a new runway mechanism, with tests | as (a) | none |

**Why (a).** It is the only option that:
- removes draw failures;
- leaves world failures as survival calls;
- keeps common seeds and R-B's seeds;
- selects at a world that is not measured by Stage 1;
- uses a stream mechanism already in the code and tested byte-identical at salt 0 (`tests/test_salt0_golden.py`,
  `tests/test_rng_streams.py::test_holistic_stream_salt_moves_only_the_holistic_stream`).

(b) is the only option with no selection. However, it has no evidence of working, it changes every world, and it
forfeits every census state. It is the registered fallback if (a)'s stop rule fires (F4).

**Screening at more anchors** (for example, also at a PW point) is rejected. It would turn world failures into selection
on the very outcome the PW points measure. That the one-anchor screen does not rescue 129001's 12 points is the design
working, not a gap in it.

## 3. The rule, with every free parameter fixed

**F1. The anchor.**
- The point is W118-b, `c0-p030-U-L`, under the sweep's world block and `--fair` exactly as the census ran it. It uses
  arm S, seasons 0–59, the census's config, and 60 slots per fauna.
- Each fauna is screened in **its own ecology alone**, using RBT-130's `only_fauna` path. That path is byte-identical to
  the fauna's half of a two-fauna run before any merge (§5.6 item 6).
- W118-b is not a Stage-1 point. The sweep makes no founding or survival call at W118-b from screened seeds (§7, T7).

**F2. The founding criterion.**
- A fauna founds when **≥ 1 member is alive at season 59, counted before same-season refill**. This is §5.1's census
  founding definition, and no new constant is introduced.
- The alive count is printed for every attempt.
- On the known draws the outcome is bimodal (0 against 58–60). Any threshold from 1 to 58 would give the same result on
  draws 1–8.

**F3. The sub-stream and the draw order.**
- **Holistic:** `holistic_stream_salt = s`. `spawn_streams` then replaces the holistic stream with
  `SeedSequence(seed, spawn_key=(STREAMS.index(HOLISTIC), s))`; the designed and terrain streams do not move.
- **Designed:** a new `designed_stream_salt = t`, the mirror image, with spawn key `(STREAMS.index(CONVENTIONAL), t)`.
  It comes from RBT-129c.
- **Key safety.** The two-long salt keys cannot equal `breed_seed_sequence`'s `(i, 0, K)` or
  `merge_null_seed_sequence`'s `(i, 1, 0)` (the breed key's test is `tests/test_ecology_switches.py::test_the_breed_key_never_collides_with_a_salt_key_or_a_founder_stream`; the null key's is argued in `ecology.py`'s docstring, and RBT-129c adds its test). `breed_stream` is refused with a salt,
  and the sweep does not use it.
- **Order.** For each seed j = 1…16 and each fauna independently, try s (or t) = 0, 1, 2, …, 20 in that order, and keep
  the first that founds. No later salt is run once one passes.
- **Recorded values.** The pair (s_j, t_j) is written into every Stage-1/2 arm's `config.json`. It is also posted as
  the **screen table** before any Stage-1 arm runs.

**F4. The cap, and what happens when it is hit.**
- **Per seed and fauna:** after salts 0–20 all fail, that fauna keeps salt 0 at seed j and the seed is labelled
  **SCREEN-CAPPED**. It enters Stage 1 exactly as registered: its invalidity is counted and reported, never averaged.
  Seeds are never skipped or replaced.
- **Programme stop:** if ≥ 3 of the 16 seeds are SCREEN-CAPPED (either fauna), Stage 1 does not launch. The screen table
  goes to the coordinator, and (b) becomes the candidate.
- **Rates.** At q = 0.16, the lower end of the anchor's CI, P(one seed capped) = 0.031 and P(stop) = 0.004. At q = 0.5
  both are below 10⁻⁵.

**F5. Seeds and known outcomes.**
- **Seeds 1–16 are screened before Stage 1.** Screening R-B's seeds now means an R-B extension never adds an
  unscreened seed, and no seed is chosen after Stage 1 is seen (§4.2's last line holds).
- **Salt 0 is already known** for seeds 1–8 at W118-b:
  - the census S (129001–129003), the pilot S (129004) and the A-stage anchor-fallback S (129005–129008) are the salt-0
    attempts;
  - holistic passes at salt 0 on seeds 1, 4, 5 and 6; designed passes at salt 0 on seeds 1–8.
- **New attempts:**
  - holistic at seeds 2, 3, 7 and 8, from salt 1;
  - holistic and designed at seeds 9–16, from salt 0.
- The passing attempt's S 0–59 state at W118-b replaces the old A-stage run as the anchor-fallback fork source for its
  seed (§9.1).

**F6. n other than 8 or 16.** See §4: EXCLUDED at ≥ ⌈5n/8⌉ and PARTIAL at < ⌈3n/4⌉. If the coordinator rules a
Stage-1 n other than 8, R-B's extension adds seeds n + 1 … 2n, all of them screened by F5 before Stage 1. The combined
test keeps Z = (Z₁ + Z₂)/√2 over the two halves.

**F7. What Stage 1 resumes from.**
- **129001:** Stage 1's S arm resumes from the census S 0–59 state at the same point, at all 36 points, as ruled at 02:22.
  This is exact, because (s, t) = (0, 0) is the census's own config.
- **Every other seed:** runs fresh from season 0 with its (s_j, t_j) in the config.
  - The census states for 129002 and 129003 have no holistic member, and `ecology.py` never re-seeds.
  - The pilot's 129004 runs are not reused (the pilot is exploratory, §4.1).
- **K-SALT (a free control).** The census and the Stage-1 runs overlap for 129002 and 129003 (and 129007 and 129008 at
  W118-b). Wherever a seed runs with s ≥ 1 and t = 0 at a point the census also ran, the designed fauna's rows of
  `history.json` and `lineage.jsonl` for seasons 0–59 must equal the census's, byte for byte. That gives 72 Stage-1
  point-seeds.
  - A mismatch voids the point for the seed (§6.1 item 3, VOID), and RBT-129c's stream claim is re-opened.

**F8. What is printed** (R5, R10):
- the screen table: per seed and fauna, every salt tried, its alive count at season 59, and its last season alive;
- the founding layer: per fauna, attempts and passes, the rate with a Clopper–Pearson 95% interval, and the census's
  FOUNDING-FAIL layer beside it;
- the side-effect table: accepted against rejected draws at W118-b, seasons 0–14 — founder solvency, founder node
  count, income and births.

## 4. §6.1 is unchanged, except for thresholds at any n

§6.1's EXCLUDED and PARTIAL logic is kept as it is. Under (a), a seed that is invalid at a Stage-1 point is invalid
because **that world** killed an established fauna. That is exactly what EXCLUDED and PARTIAL were written to report.
Redefining validity, for example by counting a seed valid if either fauna lives, would bring back the problem the screen
removes, and it would do so at the measured points.

The only change is to register the thresholds for any n, as proportions that reproduce the registered pairs:

| n | EXCLUDED (extinct by 299 on ≥ ⌈5n/8⌉) | PARTIAL (< ⌈3n/4⌉ valid at the merge) |
|---|---|---|
| 6 (the lean option) | ≥ 4 | < 5 |
| 8 | ≥ 5 (as registered) | < 6 (as registered) |
| 12 | ≥ 8 | < 9 |
| 16 | ≥ 10 (as registered) | < 12 (as registered) |

## 5. What to expect at n = 8 under (a)

`founding_expect.txt` gives the per-point table. The model:
- A seed is valid at a point when both faunas are alive at season 59 there.
- **Designed fauna:**
  - seeds 1–3 are known from the census, because the holistic salt does not move the designed stream;
  - seed 4 is known at the pilot's Stage-1 points;
  - other seeds are Bernoulli at the point's census rate (k of 3).
- **Holistic fauna:**
  - seed 1 is known;
  - a screened draw is alive at the point at rate p_H, the record at that point of the draws known to found at W118-b.
    That record is 129001 at every point, and also 129004 at the pilot's Stage-1 points;
  - **plug-in** uses that record directly;
  - **pessimistic** uses the Jeffreys mean (k + 0.5)/(m + 1). This caps p_H at 0.75 where a single draw founded.
- **The weak point: p_H rests on one or two draws per point (R11).** The truth probably lies between the two rows, nearer
  the plug-in. At the U-L pilot points, every draw alive at season 59 was alive at 239 (4 of 4).

| | registered | **(a), plug-in** | (a), pessimistic |
|---|---|---|---|
| 24 points where 129001 has both faunas at 59: mean E[valid] | 3.88 | **7.67** | 6.03 |
| — expected points not PARTIAL | 0.0 | **22.5** | 17.0 |
| — mean E[income power], SD 0.334 / 0.275 | 0.365 / 0.488 | **0.790 / 0.902** | 0.636 / 0.774 |
| 12 other points: mean E[valid] | 0.15 | 0.29 | 0.78 |
| — expected EXCLUDED by 59 (a lower bound on EXCLUDED) | 12.0 | 11.5 | 11.3 |

**Income power by valid n** (exact noncentral t, |H − D| = 0.4, BH half; `power_eff`'s method):

| valid n | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|
| power at SD 0.334 / 0.275 | 0.381 / 0.510 | 0.529 / 0.686 | 0.653 / 0.810 | 0.752 / 0.891 | 0.826 / 0.939 |

**The calls this gives:**
- **About 22 of the 24 benign points** get a full-n income test and a share test.
- **`c1-p080-U-G` is PARTIAL-H** (the designed fauna dies on 2 of 3 census draws), and **`c1-p080-U-L` is a coin toss**
  (P(PARTIAL) = 0.54). Both are world findings about the designed body.
- **The 12 world-lethal points** read:
  - EXCLUDED-H at the holistic-lethal PW points;
  - EXCLUDED-D or PARTIAL-H at `c2-p080-U/HP-G` and `c1-p030-PW-L`;
  - NEITHER where both faunas die (`c2-p030-PW-G`, `c1-p080-PW-G`, `c2-p080-PW-G`).
- **This does not make the share layer decide.** Under shuffle, 0–2 of 36 points are expected RESOLVING (§6.2,
  `prior_regime.txt`). The share call is still SATURATED or NOT RUN at most points, and the map is carried by the income
  and survival layers, as r4 already said. The amendment makes that map **readable**; without it, validity rather than
  the bodies decides every call.

## 6. Cost

| item | 23.35 core-s (pilot median) | 43.72 core-s (pilot ceiling) |
|---|---|---|
| **F: the screen** (holistic-only or designed-only S 0–59 at W118-b; failed attempts stop by about season 15; 12 holistic and 8 designed screens) | **5.2 expected (q 0.5), 8.1 (q 0.16); ≤ 27 worst** | **9.0, 13.9; ≤ 47 worst** |
| Stage 1 gated, n = 8 (36 × 8 S + probes 0.46–0.83; M ≤ 12 points; N ≤ 4; plants) | 892–999 | 1,530–1,637 |
| − census resume credit, registered (129001–129003) | −42 → 850–957 | −79 → 1,452–1,558 |
| **− census resume credit, amended (129001 only)** | **−14 → 878–985** | **−26 → 1,504–1,611** |
| difference, amended − registered | +28 | +52 |
| for reference: ungated Stage 1, `power_eff` formula | 1,361–1,467 | 2,407–2,513 |

- The registered Stage 1 would in practice cost somewhat less than its nominal figure. On the 4 of 8 seeds where the
  holistic fauna is dead, its arms run one fauna. The amended Stage 1 runs two faunas on those seeds, so it costs the
  nominal figure.
- §11.2's other rows (2a, 2b, R) were not re-costed at the pilot's core-s by #490 (SHOULD 1). This amendment does not
  re-cost them either. It changes none of their arm counts.

## 7. DESIGN sections touched, with exact replacement text

The texts below take effect on the coordinator's ruling. Until then, DESIGN.md carries only the appended pointer section
(§15), and the sections themselves are not edited.

**T1. §0, the one-table: add a row after "selection":**
> | founding (amendment F, DATA-INFORMED) | each seed's holistic and designed streams are redrawn by a registered salt until the fauna founds at W118-b (seasons 0–59, alive at 59); the same salts at every point; ≤ 20 redraws; seeds 129001–129016 screened before Stage 1; claims read "among founder draws that establish at W118-b" | 5.2, AMENDMENT-FOUNDING |

**T2. §4.1, the stage table: add a row between "0 census" and "1 coarse map":**
> | **F** founder screen (amendment F) | W118-b only | 129001–129016, each fauna alone | 60 | fix each seed's salts (s_j, t_j) by AMENDMENT-FOUNDING F1–F5 | **none** (the screen table and the founding layer are printed, not called) |

and replace the table's 1 row's "seeds" cell `8` with `8 (screened, F)`.

**T3. §5.1, C2: append after "Stage 1 overrides the census wherever both exist.":**
> *(Amendment F.)* For the holistic fauna, Stage 1's founding is **screened** and the census's is not. At Stage-1 points,
> the two layers are printed side by side, and Stage 1 does not override the census's holistic FOUNDING-FAIL. The
> designed stream is unchanged at seeds 129001–129003, so for the designed fauna the census and Stage 1 remain the same
> draws.

**T4. §5.2, the first paragraph: replace it with:**
> Seeds are **common across points** (j = 1…16, seed 129000 + j, with the holistic salt s_j and the designed salt t_j
> fixed by the founder screen, AMENDMENT-FOUNDING F3–F5): the same founders and terrain stream everywhere, so the axis
> contrasts are paired by founder set. This makes the per-point tests dependent; §7.1 says how BH is checked against it.
> Every call reads "among founder draws that establish at W118-b".

**T5. §5.2, the M/N gate, item 1: replace "with neither fauna FOUNDING-FAIL." with:**
> with the designed fauna not FOUNDING-FAIL in the census (the holistic census layer is unscreened and is not used here,
> amendment F). At a gated point, M is forked only on seeds valid at the merge (both faunas alive at season 59 in S). A
> point where M runs on no seed frees its slot for the next point in the ranking.

and in item 2, after "up to 4 Stage-1 points, 2 Stage-2a points and 2 R-B points", add:
> , with the same seed rule as M.

**T6. §6.1, items 1 and 2: replace "on ≥ 5 of 8 seeds (≥ 10 of 16)" with "on ≥ ⌈5n/8⌉ of n seeds (5 of 8, 8 of 12, 10
of 16)", and replace "fewer than 6 of 8 (12 of 16) seeds" with "fewer than ⌈3n/4⌉ of n seeds (6 of 8, 9 of 12, 12 of
16)".**

**T7. §9.1: after the "coordinate seeds" bullet, add:**
> - *(Amendment F.)* The sweep's seeds are (seed, s_j, t_j) triples; RBT-118 is asked to run them with their salts. At
>   **W118-b**, which is the screen's own point, the sweep's screened seeds are **selected on survival**, so their
>   founding and survival there are not evidence. The anchor column at W118-b reports income and share only, labelled
>   "screened here". The anchor fallback forks from the passing screen attempt's S 0–59 state.

**T8. §4.2, R-B: replace "gets seeds 9–16" with "gets seeds 9–16 (screened before Stage 1, amendment F5; for a Stage-1 n
other than 8, seeds n + 1 … 2n)".**

**T9. §5.6: add item 7:**
> 7. **RBT-129c (amendment F).** A `designed_stream_salt` mirroring `holistic_stream_salt`; both salts on the `ecology`
>    subcommand and in `stages.py`'s configs; a Stage-F screen driver implementing F1–F5; the K-SALT comparison (F7).
>    **Tests:**
>    - salt 0 is byte-identical to today (golden);
>    - a designed salt moves only the designed stream;
>    - both salts survive the season-59 fork and a `--resume`;
>    - salts compose with `merge_null` and `only_fauna`;
>    - the screen stops at the first passing salt and at the cap.

**T10. §11.1:**
- **In item 1, add a gate:**
  > RBT-129c merged; Stage F run and its screen table posted, with the stop rule (F4) not fired.
- **In item 2, replace "and the coordinator rules n for Stage 1." with:**
  > then Stage F (amendment F); and the coordinator rules n for Stage 1.
- **In the 02:22 pre-data note, replace "Stage 1's S arms at seeds 129001–129003 resume" with:**
  > Stage 1's S arms at seed 129001 (amendment F: the only census seed whose salts are both 0) resume

  and replace "(about −36 core-h)" with "(about −14 to −26 core-h at the pilot's cost)".

**T11. §11.2, the table: add the row**
> | F founder screen (W118-b, single-fauna S 0–59, seeds 1–16) | 5–8 (≤ 27) | 9–14 (≤ 47) |

and add below the table:
> *(Amendment F.)* Stage 1 at n = 8, re-costed at the pilot's 23.35 / 43.72 core-s with the census resume for 129001
> only: 878–985 / 1,504–1,611 core-h. The other rows are not re-costed.

**T12. §13: add "New in amendment F":**
> 1. p_H, the anchor-to-point transfer rate, rests on one or two draws per point. Stage 1 measures it; it is not a gate.
> 2. The screen selects the whole holistic stream, not the founders alone. A founders-only salt would need new code; it
>    was judged not worth it (AMENDMENT-FOUNDING §2.0).
> 3. If the stop rule fires, (b) the runway is the fallback. It has no feasibility evidence yet.

**T13. §14: add rows for** `AMENDMENT-FOUNDING.md` and `founding-amendment/founding_expect.py → founding_expect.txt`.

Unchanged: §3, §6.2–6.4, §7, §8, §10 and §12. §8's verdicts inherit the claim label of §2.0.

## 8. For the coordinator and the owner

**The coordinator rules on:**
1. **Option (a)** as specified in F1–F8, or another option.
2. **n for Stage 1.** The recommendation is **n = 8**: about 7.7 expected valid seeds at the 24 benign points, and
   income power 0.79–0.90 there. If n is not 8, F6 and T6 apply.
3. **The M/N gate change (T5).** Without it, no M or N arm runs anywhere.
4. **The claim label (§2.0)** and the W118-b handling asked of RBT-118 (T7).
5. **The stop rule** (≥ 3 of 16 seeds capped) and its fallback, (b).
6. That this amendment goes to an adversary before the ruling. That is the usual order, and Stage 1 stays on hold
   meanwhile.

**The owner approves the cost:**
- RBT-129c: code only, no core-h;
- **Stage F: about 5–14 core-h expected, 47 at most;**
- **Stage 1 at n = 8: 878–985 core-h** at the pilot median, **1,504–1,611** at the pilot ceiling. That is +28 / +52 over
  the registered Stage 1, and gated as in §11.2.

**The launch is a separate owner decision**, taken after the ruling and the cost approval. Nothing in this amendment
launches anything.

## 9. Files

| file | what |
|---|---|
| `AMENDMENT-FOUNDING.md` | this amendment |
| `founding-amendment/founding_expect.py` → `founding_expect.txt` | expected valid seeds, P(PARTIAL), income power and cost per option and per Stage-1 point. It reads `stageP0-readout/founders.txt` and runs no simulator (stdlib; about 2 s) |

Reproduce: `python3 runs/RBT-129/founding-amendment/founding_expect.py > runs/RBT-129/founding-amendment/founding_expect.txt`.
