# RBT-129 amendment F: founding (ruled ADOPT-WITH; fixes applied)

> ## ⚠ DATA-INFORMED: written after the Stage 0 census and the Stage P pilot were read (#490, #491)
>
> The author has read the census layer, `founders.txt` (both versions), `stage1_points.txt`, `power_eff.txt` and the
> pilot's per-seed outcomes. Every choice below was made knowing that holistic draws 129002, 129003, 129007 and 129008
> die by season 14 at `c0-p030-U-L`, and knowing which Stage-1 points lose a fauna on seed 129001. Nothing here is
> pre-data. Readers should weigh each choice as a choice made after seeing the data.
>
> **Status: DESIGN ONLY.** Nothing has run for this amendment, and nothing runs from this file.
>
> **Ruled ADOPT-WITH** (coordinator, #493 comment 5883124591; adversary #494, `founding-amendment-adversary/`). This
> revision applies MUST 1–5, SHOULD 1–8 and the ruling's binding choices (§10 lists each fix and where it is). Stage 1
> stays on hold until three things happen: RBT-129c passes its own implementer-then-adversary pass; the owner approves
> the cost; and the owner separately decides to launch.
>
> Date: 2026-09-29. First draft on base `b4f10e7`; this revision is on `9a457b2`. The numbers come from `founding-amendment/founding_expect.py` →
> `founding_expect.txt`, which reads committed text outputs only and runs no simulator.

## 0. In one table

| question | answer | § |
|---|---|---|
| recommended option | **(a) a per-seed founder screen**. Each fauna's RNG stream at seed j is redrawn from a registered salt sequence until that fauna founds at one benign anchor. The rule is symmetric: both faunas face it. | 2, 3 |
| anchor | **W118-b = `c0-p030-U-L`**: one point, under the sweep's block and `--fair`, arm S, seasons 0–59. It is not a Stage-1 point. | 3 F1 |
| criterion | **≥ 30 of 60 members alive at season 59** in the fauna's own ecology, counted before same-season refill (ruling item 3). On draws 1–8 it gives the same verdict as ≥ 1, because they are bimodal. | 3 F2 |
| sub-stream | holistic: the existing `holistic_stream_salt` s (spawn key (holistic index, s), RBT-96). Designed: a new `designed_stream_salt` t built the same way (RBT-129c). Both are tried in order 0, 1, 2, … and the first that passes is kept. | 3 F3 |
| cap and stop | 20 redraws (salts 1–20). A capped fauna keeps salt 0 and is labelled SCREEN-CAPPED; its seed enters Stage 1 under the registered rules. **Stage 1 does not launch if ≥ 3 of the 16 seeds are capped, or if ≥ 2 of seeds 1…8 are capped** (ruling item 4). The fallback is (b), which needs its own amendment. | 3 F4 |
| seeds | 129001–129016 keep their numbers. All 16 are screened **before Stage 1**, so R-B's seeds 9–16 are fixed in advance and nothing collides. | 3 F5 |
| resume | 129001 resumes from the census S 0–59 at all 36 points: both salts are 0, so it is the same run. Every other seed runs fresh from season 0. The designed half of 129002/129003 is byte-compared with the census (K-SALT). | 3 F7 |
| salt-0 re-run | **REQUIRED** (ruling item 8). Salt 0 is re-run with each fauna alone for seeds 1–8 at W118-b, and each run is byte-compared with the matching half of the census and pilot runs (129001–129004). A mismatch re-opens RBT-130's stream claim. | 3 F5 |
| anchor-fallback fork source | a **two-fauna** S 0–59 at W118-b at (s_j, t_j); the single-fauna screen states cannot be forked into M/N (MUST 3) | 3 F5 |
| §6.1 | unchanged. The thresholds are generalised to any n: EXCLUDED at ≥ ⌈5n/8⌉ seeds, PARTIAL at < ⌈3n/4⌉ valid seeds. Both formulas reproduce 5/6 at n = 8 and 10/12 at n = 16. | 4 |
| expected valid seeds at n = 8 | **about 5.4–7.7 valid of 8** at the 24 points where 129001 has both faunas at season 59. The top of that range, 7.7, assumes perfect transfer, because the plug-in transfer rate is 1 there by construction. At the other 12 points: **0.00–0.85**. Registered, without the amendment: 3.9 and 0.00. | 5 |
| expected calls | **about 15–20 of 24 points escape PARTIAL** (22.5 at the plug-in top). The 12 world-lethal points stay survival calls (EXCLUDED-H, EXCLUDED-D or NEITHER) **by design**. Under shuffle the share layer remains SATURATED or NOT RUN at most points (§6.2). | 5 |
| income power at \|H − D\| = 0.4, BH half | mean over the 24 points: **about 0.56–0.79 at SD 0.334 / 0.68–0.90 at SD 0.275**. This is an **upper bound**, because it is priced at validity at season 59 while the income test needs survival through 239. At 8 valid seeds: 0.826 / 0.939. Registered, 24-point mean: 0.365 / 0.488. | 5 |
| cost (upper bounds) | screen: **about 5–14 core-h expected**. It is ≤ 27 / 47 only if failed attempts die by season 15; the **true bound is 94 / 162**. Two-fauna fork source: **+3–12**. Salt-0 re-run: **+3–5**. Stage 1 gated at n = 8: **878–985 core-h** at 23.35 core-s, **1,504–1,611** at 43.72. That is +28 / +52 over the nominal gated figure. It includes about **171 / 320 of M + N that T5 re-admits**: the registered gate, read literally, would have run no M or N at all. | 6 |
| what it can claim | the comparison is among holistic and designed **stream draws (founders and their early history)** that establish at W118-b. It says nothing about unscreened holistic founders. Founding itself becomes a separately reported layer. | 2 |

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
  - At those points the designed fauna also dies on the other census draws.
  - In the pilot, a second founding draw (129004) dies at **both** PW-G points where it was tried:
    - at `c2-p030-PW-G`, both faunas are dead by season 32;
    - at `c1-p030-PW-G`, its holistic fauna is dead by season 16 (corrected, MUST 1). Its designed fauna is alive at the
      merge (10 members) and dead by 93 (`stageP0-readout-adversary/founders.txt`, `pilot.txt` (b)).
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
- with a screen, it is holistic evolution against designed evolution, each **from stream draws (founders and their
  early history) that establish at W118-b**.

Here the screen bites only on the holistic side (0 of 8 designed draws fail, 4 of 8 holistic draws fail). Its effect is
therefore asymmetric even though the rule is symmetric.

**What the screened comparison can claim:**
- among stream draws (founders and their early history) that establish in a benign flat world, which body earns more
  where (EARNS-*), and which gains share where a share call is resolvable (WIN / TIE);
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
  worlds, where the stream meets different terrain and food; the founders do. At PW points the holistic arenas' food
  seeds are holistic draws too, so the salt also redraws them (adversary §2), though they are not selected at W118-b.
  **This is why the claim label reads "stream draws (founders and their early history)", not "founders"** (MUST 4,
  ruling item 5).

**How the RBT-121 rules apply:**
- **R5 (state the regime):** founding is part of the regime. Every map, table and verdict carries the label
  "among holistic and designed stream draws (founders and their early history) that establish at W118-b" (amendment F). The screen's rejection rate per fauna is reported as the **founding layer**, beside the census's
  FOUNDING-FAIL layer.
- **R6 (state the parity), by analogy:** every holistic-against-designed statement says it is made at screened
  founding. It is never made at unscreened founding.
- **R10 (a manipulation prints its side effects against the control):** at W118-b, the accepted and rejected draws of
  each fauna are printed side by side over seasons 0–14 (founder solvency, node count, income, births). The designed
  half of every salted holistic run is byte-compared with its unsalted twin (K-SALT, F7).
- **R11 (no single seed carries a claim):** today the census's founding layer rests on 129001 at most points, and the
  valid-seed count, not the bodies, decides every Stage-1 call. The screen removes that. The transfer estimate in §5
  itself rests on one or two draws. On the 24 class-A points the plug-in estimate is 1 **by construction**, so §5
  reports a range, not a point.
- **R12 (the record keeps its evidence):** the census's holistic FOUNDING-FAIL at 150 of 150 stays in the record. It is
  not relabelled. Stage 1 stands **beside** it; it does not override it (T3).

### 2.1 The comparison

The expected-valid, calls and power rows are from `founding_expect.txt`, with 129004's input corrected (MUST 1).
"Plug-in" is the top of the range: its transfer rate is 1 on the 24 points by construction. "Pessimistic" shrinks both
the transfer rate p_H and the designed rate p_D (Jeffreys; SHOULD 8). Power is an upper bound (validity at season 59).

| | **(a) per-seed screen at W118-b** | (b) founding runway | (c) per-point screen | (d) replace failing draws by the next seed numbers |
|---|---|---|---|---|
| what | at each seed, each fauna's stream is redrawn (salt 0, 1, …) until the fauna founds at the one anchor; the salts then hold at every point | a protected establishment period (for example, no living cost and no starvation deaths for seasons 0–R) before competition, at every point | at each point and seed, the holistic stream is redrawn until it founds **at that point** | a seed whose draw fails at the anchor is dropped, and the next seed number takes its place |
| fairness between faunas | symmetric rule; so far it bites only on the holistic side (§2.0). Justified: the question needs two established populations, and the asymmetry is reported as the founding layer | symmetric in form; in effect a subsidy to whichever fauna fails to earn early, which is the holistic one | symmetric in form. In effect it bites only on the holistic side, and hardest at the harsh points | the screen is on the holistic fauna, but a new seed number redraws the **designed founders and the terrain stream too**, so they are selected jointly with holistic founding |
| selection bias | on establishment at one benign world, which is **not** a Stage-1 point; see §2.0 | none by selection, but it changes the world at every point and masks early world-driven deaths, so EXCLUDED changes meaning | **selection on the outcome at the measured point.** Survival there is true by construction, so EXCLUDED-H becomes impossible short of the cap, and the survival layer is erased | as (a), **plus** the shared terrain stream is selected. Terrain sequences that favour holistic founding carry over to every Stage-1 point through §5.2's common seeds |
| §5.2 common seeds | **kept**: one (seed, salt_H, salt_D) per j at every point | kept | **broken**: founders differ by point, so the axis contrasts lose their pairing | kept, but with different seed identities |
| E[valid] at n = 8, 24 points where 129001 has both faunas (plug-in / pessimistic) | **7.67 / 5.61** (the adversary's full range is 5.41–7.67) | not estimable from existing data. If the runway only delays death (the failing draws die at 10–14, about when the founders' own energy runway ends), the registered 3.9; if it rescues every draw, about (c) | 7.67 / 7.10 | 7.71 / 5.47 |
| E[valid], the other 12 points | 0.00 / 0.69 | as above | 1.80 / 2.90, bought by selecting at the point itself | 0.00 / 0.72 |
| §6.1 calls | benign points: about 15–20 of 24 escape PARTIAL (22.5 plug-in top, 13.8 pessimistic); `c1-p080-U-G` is PARTIAL-H because the designed fauna dies; world-lethal points: EXCLUDED or NEITHER | unknown until a feasibility run | PARTIAL escaped at some lethal points only by selection; EXCLUDED-H cannot be called | as (a) |
| income power, upper bound (mean over the 24; SD 0.334 / 0.275; plug-in, then pessimistic) | **0.789 / 0.901** (0.587 / 0.725) | unknown | 0.789 / 0.901 (0.744 / 0.869) | 0.794 / 0.907 (0.571 / 0.709) |
| R-B seeds 9–16 | **no collision**: seeds 9–16 keep their numbers and are screened now | no collision | no collision (salts) | **collides**: "the next seed numbers" are 129009+. R-B must move (for example to 129101+) and be re-registered, and the RBT-118 coordination changes |
| resume from census states | 129001 only (salts 0) | **none**: the census ran without a runway | 129001 only, at points where it founds | 129001 only |
| cost of the screen | 5–14 core-h expected; bound 94 / 162 | new code, a feasibility run, and R extra seasons at every arm (+4% at R = 12) | high: 36 × 8 screens, many at PW points to the cap (q low); up to about 380 core-h | as (a), but screens are two-fauna runs, and the terrain is redrawn |
| code | RBT-129c: a designed salt; both salts wired through `ecology` and `stages.py`; the screen launcher; the two-fauna fork source | a new runway mechanism, with tests | as (a) | none |

**Why (a).** It is the only option that:
- removes draw failures;
- leaves world failures as survival calls;
- keeps common seeds and R-B's seeds;
- selects at a world that is not measured by Stage 1;
- uses a stream mechanism already in the code and tested byte-identical at salt 0 (`tests/test_salt0_golden.py`,
  `tests/test_rng_streams.py::test_holistic_stream_salt_moves_only_the_holistic_stream`).

(b) is the only option with no selection. However, it has no evidence of working, it changes every world, and it
forfeits every census state. It is the registered fallback if (a)'s stop rule fires (F4), and it **needs its own
amendment** (with its own adversary and ruling) before it could run (ruling item 1).

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
- **The sources of the salt-0 attempts share the census config.** This is not asserted but tested: the REQUIRED salt-0
  re-run (F5) byte-compares against them.

**F2. The founding criterion.**
- A fauna founds when **≥ 30 of its 60 members are alive at season 59, counted before same-season refill** (ruling
  item 3; adversary SHOULD 2). The criterion is registered now.
- **Why not §5.1's "≥ 1 alive".** The stated purpose is two *established* populations. A draw with 1–3 survivors at
  W118-b would pass "≥ 1", and would then almost surely be an invalid seed at every Stage-1 point.
- **It costs nothing on the known draws.** They are bimodal (0 against 58–60), so ≥ 30 gives the same verdict as ≥ 1
  on draws 1–8. This keeps one-survivor passes out.
- The alive count is printed for every attempt. The census's own FOUNDING-FAIL layer keeps §5.1's definition,
  unchanged.

**F3. The sub-stream and the draw order.**
- **Holistic:** `holistic_stream_salt = s`. `spawn_streams` then replaces the holistic stream with
  `SeedSequence(seed, spawn_key=(STREAMS.index(HOLISTIC), s))`; the designed and terrain streams do not move.
- **Designed:** a new `designed_stream_salt = t`, the mirror image, with spawn key `(STREAMS.index(CONVENTIONAL), t)`.
  It comes from RBT-129c.
- **Key safety.** The two-long salt keys, `(0, s)` for the holistic fauna and `(1, t)` for the designed, cannot equal:
  - the unsalted children `(i,)`;
  - `breed_seed_sequence`'s `(0, 0, K)`;
  - `merge_null_seed_sequence`'s `(i, 1, 0)`;
  - each other.

  Existing tests:
  - the breed key: `tests/test_ecology_switches.py::test_the_breed_key_never_collides_with_a_salt_key_or_a_founder_stream`;
  - the null key: `tests/test_rbt130.py::test_the_null_stream_is_independent_of_every_other_stream`, which covers
    holistic salts 1–5.

  **RBT-129c extends both tests to the designed keys `(1, t)`** (SHOULD 6). `breed_stream` is refused with a salt, and
  the sweep does not use it.
- **Order.** For each seed j = 1…16 and each fauna independently, try s (or t) = 0, 1, 2, …, 20 in that order, and keep
  the first that founds. No later salt is run once one passes.
- **Recorded values.** The pair (s_j, t_j) is written into every Stage-1/2 arm's `config.json`. It is also posted as
  the **screen table** before any Stage-1 arm runs.
  *(RBT-129c, ruling on #495.)* A salt is written to `config.json` only when it is non-zero: **absent means 0**, the
  pre-salt config byte for byte. The provenance of every seed's pair is `launch.txt`'s `salts` line together with the
  screen table.

**F4. The cap, and what happens when it is hit.**
- **Per seed and fauna:** after salts 0–20 all fail, that fauna keeps salt 0 at seed j and the seed is labelled
  **SCREEN-CAPPED**. It enters Stage 1 exactly as registered: its invalidity is counted and reported, never averaged.
  Seeds are never skipped or replaced.
- **Programme stop** (ruling item 4). Stage 1 does not launch if either of these holds, counting either fauna:
  - **≥ 3 of the 16 seeds are SCREEN-CAPPED**; or
  - **≥ 2 of seeds 1…8 are SCREEN-CAPPED**, because two capped Stage-1 seeds leave every point at most 6 valid, one
    world loss from PARTIAL.

  The screen table then goes to the coordinator. The fallback is (b), and it **needs its own amendment** (ruling
  item 1).
- **Rates** (`founding_expect.txt`). At q = 0.16, the lower end of the anchor's CI:
  - P(one seed capped) = 0.031;
  - P(≥ 3 of 16) = 0.004;
  - P(≥ 2 of seeds 1–8) = 0.005 (the adversary gives 0.0046 and 0.0062 at q = 0.157).

  At q = 0.5, all are below 10⁻⁵.
- **No kill rule is added** (ruling item 9). Killing an attempt early would change the criterion.

**F5. Seeds and known outcomes.**
- **Seeds 1–16 are screened before Stage 1.** Screening R-B's seeds now means an R-B extension never adds an
  unscreened seed, and no seed is chosen after Stage 1 is seen (§4.2's last line holds).
- **Salt 0 is REQUIRED to be re-run with each fauna alone for seeds 1–8** (ruling item 8; SHOULD 3). This makes the
  screen uniform: every attempt is a single-fauna S 0–59 at W118-b under the same config.
  - The existing two-fauna runs at W118-b predict the outcomes: holistic passes at salt 0 on seeds 1, 4, 5 and 6 (58–60
    alive), and designed passes on seeds 1–8 (58–60). Those runs are the census S for 129001–129003, the pilot S for
    129004, and the A-stage S for 129005–129008.
  - **The re-run, not those runs, is the screen's record.**
  - Each re-run fauna is byte-compared, seasons 0–59, with its half of the census runs (129001–129003) and the pilot run
    (129004). The comparison covers that fauna's rows of `history.json` and its lines in `lineage.jsonl`.
  - **A mismatch re-opens RBT-130's stream claim** (that a fauna alone equals its half of a two-fauna run) at the
    sweep's block, and Stage 1 does not launch until it is resolved. This also tests that the source runs share the
    census config (SHOULD 3).
  - Cost: 2.9 / 5.1 core-h.
- **New attempts after the re-run:**
  - holistic at every seed of 1–8 that fails salt 0 (expected: 2, 3, 7 and 8), from salt 1;
  - holistic and designed at seeds 9–16, from salt 0.
- **The anchor-fallback fork source** (MUST 3). The screen's attempts run one fauna, so their state cannot be forked
  into M or N, which need both faunas.
  - The fork source is therefore a **two-fauna S 0–59 at W118-b at (s_j, t_j)**, run once for each seed after its salts
    are fixed. It replaces the old A-stage run for that seed.
  - It is needed only if the anchor fallback runs (§9.1): for 8 seeds, or 16 if R-B extends.
  - Cost: 3.1 / 6.2 core-h at 23.35 core-s, 5.8 / 11.7 at 43.72.
  - The alternative, code that composes two single-fauna states, is not chosen.

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
  - **plug-in** uses that record directly. **On the 24 class-A points it is 1 by construction.** Class A is defined
    by 129001's record, and that record is also p_H's source (129004 adds only `c1-p030-U-L`, where it also survived).
    So the plug-in assumes perfect transfer: it is the top of the range, not an estimate (MUST 2);
  - **pessimistic** uses the Jeffreys mean (k + 0.5)/(m + 1) for **both** p_H and p_D (SHOULD 8).
- **The weak point: p_H rests on one or two draws per point (R11).** Other models give a range:
  - pooling p_H by food family;
  - a count threshold T at season 59, standing in for survival to 239.

  Those models are the adversary's (`founding-amendment-adversary/rederive.txt` §3). The evidence at PW is poor:
  - 129001's holistic fauna is alive at only 3 of 12 PW Stage-1 points, with 3, 10 and 18 members;
  - 129004 died at both PW points where it was tried.
- **Income validity is survival through 239, not alive at 59** (§6.1). The census stops at 59, so every power figure
  below is an **upper bound**.
- **Correction (MUST 1).** 129004's holistic fauna is dead by season 16 at `c1-p030-PW-G`, not alive at the merge.

**The headline, in the adversary's form** (ruling):
- **about 5.4–7.7 valid of 8**;
- **about 15–20 of 24 points escape PARTIAL**;
- **mean income power about 0.56–0.79 / 0.68–0.90** (SD 0.334 / 0.275). This is an **upper bound**, because it is
  priced at validity at season 59.

The 24 class-A points at n = 8, rows from `founding_expect.txt` (this amendment) and `rederive.txt` §3 (the adversary):

| model | E[valid] | points not PARTIAL | mean income power, upper bound |
|---|---|---|---|
| registered (no amendment) | 3.88 | 0.0 | 0.365 / 0.487 |
| (a), plug-in: p_H = 1 by construction, the top of the range | 7.67 | 22.5 | 0.789 / 0.901 |
| (a), p_H pooled by food family, plug-in (adversary) | 7.21 | 20.5 | 0.735 / 0.842 |
| (a), T = 10 at season 59, plug-in (adversary) | 7.11 | 20.5 | 0.729 / 0.834 |
| (a), T = 30 at season 59, plug-in (adversary) | 6.67 | 19.0 | 0.679 / 0.776 |
| (a), p_H pooled by family, Jeffreys on both (adversary) | 5.81 | 15.8 | 0.607 / 0.739 |
| (a), pessimistic: Jeffreys on p_H and p_D | 5.61 | 13.8 | 0.587 / 0.725 |
| (a), T = 30, pooled by family, Jeffreys on both (adversary) | 5.41 | 14.8 | 0.559 / 0.679 |

On the other 12 points, mean E[valid] is:
- 0.00 on the plug-in (MUST 1 corrects it from 0.29);
- 0.56 with Jeffreys on p_H alone;
- 0.69 with Jeffreys on both;
- 0.34–0.85 across the adversary's models.

The registered design gives 0.00 there. EXCLUDED by 59, which is a lower bound on EXCLUDED, is expected at 11.9–12.0
of the 12.

(a) roughly doubles the valid seeds against the registered design under every model.

**Income power by valid n** (exact noncentral t, |H − D| = 0.4, BH half). It is computed as E_Z[F_χ²(df (Z+δ)²/c²)],
which matches the adversary's route. The chi-square-grid quadrature used before is wrong at df = 1: it gave 0.148 / 0.185
at n = 2 (SHOULD 7).

| valid n | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|
| power at SD 0.334 / 0.275 | 0.108 / 0.129 | 0.230 / 0.303 | 0.382 / 0.510 | 0.529 / 0.686 | 0.653 / 0.810 | 0.752 / 0.891 | 0.826 / 0.939 |

**The calls this gives:**
- **About 15–20 of the 24 benign points** get a share test and an income test at close to full n.
- **Two class-A points are PW** and fragile, although the plug-in counts them as sure:
  - `c0-p030-PW-G`: 129001's holistic fauna has 3 members at 59;
  - `c1-p010-PW-L`: 129001's holistic fauna has 10 members at 59.

  Pooled by family, both have P(PARTIAL) ≈ 0.98.
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
| **F: the screen** (holistic-only or designed-only S 0–59 at W118-b; 12 holistic and 8 designed screens), expected | **5.2 (q 0.5), 8.1 (q 0.16)** | **9.0, 13.9** |
| — ≤ this **if failed attempts die by season 15** (an assumption resting on 4 draws) | ≤ 27 | ≤ 47 |
| — **true bound**: every screened seed capped, every attempt alive to season 59 (MUST 5; no kill rule, ruling item 9) | **94** | **162** |
| **REQUIRED salt-0 single-fauna re-run, seeds 1–8** (F5) | 2.9 | 5.1 |
| **two-fauna fork source at W118-b, 8 / 16 seeds** (F5, MUST 3; only if the anchor fallback runs) | 3.1 / 6.2 | 5.8 / 11.7 |
| Stage 1 gated, n = 8 (36 × 8 S + probes 0.46–0.83; M ≤ 12 points; N ≤ 4; plants) | 892–999 | 1,530–1,637 |
| − census resume credit, registered (129001–129003) | −42 → 850–957 | −79 → 1,452–1,558 |
| **− census resume credit, amended (129001 only)** | **−14 → 878–985** | **−26 → 1,504–1,611** |
| difference, amended − registered (nominal gated) | +28 | +52 |
| of the Stage-1 total: M + N that T5 re-admits (SHOULD 4) | 171 | 320 |
| for reference: ungated Stage 1, `power_eff` formula | 1,361–1,467 | 2,407–2,513 |

- **The +28 / +52 is measured against the nominal gated figure.** Read literally, the registered gate ("neither fauna
  FOUNDING-FAIL") would have run **no M or N at all**. Against that literal reading, T5 adds about 171 / 320 core-h of
  M + N, and that sum is included in the Stage-1 total above.
- **Every Stage-1 figure is an upper bound.** At 6 points, 129001 has both faunas dead by 59. Seeds that die early cost
  almost nothing.
- The registered Stage 1 would in practice cost somewhat less than its nominal figure. On the 4 of 8 seeds where the
  holistic fauna is dead, its arms run one fauna. The amended Stage 1 runs two faunas on those seeds, so it costs the
  nominal figure.
- §11.2's other rows (2a, 2b, R) were not re-costed at the pilot's core-s by #490 (SHOULD 1). This amendment does not
  re-cost them either. It changes none of their arm counts.

## 7. DESIGN sections touched, with exact replacement text

The texts below are adopted by the coordinator's ruling (#493, comment 5883124591), as fixed in this revision. DESIGN.md
§15 incorporates them by reference and takes precedence over the unedited sections it names. They take effect when this
PR merges.

**T1. §0, the one-table: add a row after "selection":**
> | founding (amendment F, DATA-INFORMED) | each seed's holistic and designed streams are redrawn by a registered salt until the fauna founds at W118-b (seasons 0–59, ≥ 30 of 60 alive at 59); the same salts at every point; ≤ 20 redraws; seeds 129001–129016 screened before Stage 1; claims read "among holistic and designed stream draws (founders and their early history) that establish at W118-b" | 5.2, AMENDMENT-FOUNDING |

**T2. §4.1, the stage table: add a row between "0 census" and "1 coarse map":**
> | **F** founder screen (amendment F) | W118-b only | 129001–129016, each fauna alone (salt 0 re-run REQUIRED for 1–8) | 60 | fix each seed's salts (s_j, t_j) by AMENDMENT-FOUNDING F1–F5 (≥ 30 of 60 alive at 59) | **none** (the screen table and the founding layer are printed, not called) |

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
> Every call, and every map, reads "among holistic and designed stream draws (founders and their early history) that
> establish at W118-b".

**T5. §5.2, the M/N gate, item 1: replace "with neither fauna FOUNDING-FAIL." with:**
> with the designed fauna not FOUNDING-FAIL in the census (the holistic census layer is unscreened and is not used here,
> amendment F).
>
> **The gate's g0 is fixed** (ruling item 6; SHOULD 4). It is the census g0 exactly as the Stage-0 readout computed it
> (`stageP0-readout/stageP0_readout.py`, which gives the counts 46 / 63 / 11):
> - the mean season net income (food − p · kJ) over **every member-season in seasons 30–59**;
> - pooled over **all three census seeds, 129001–129003, and both faunas**;
> - plus 0.35.
>
> Because the holistic fauna is absent on 129002 and 129003, this g0 is mostly the designed fauna's regime. It is used
> as a ranking only.
>
> At a gated point, M is forked only on seeds valid at the merge (both faunas alive at season 59 in S).
>
> **DATA-INFORMED (ruling item 6):** a point where M runs on no seed frees its slot for the next point in the ranking.
> This reallocation rule is new, and it was chosen after the census was seen.
>
> This gate re-admits about 171 / 320 core-h of M + N (23.35 / 43.72 core-s). The literal registered gate would have
> spent none of it.

and in item 2, after "up to 4 Stage-1 points, 2 Stage-2a points and 2 R-B points", add:
> , with the same seed rule as M.

**T6. §6.1, items 1 and 2: replace "on ≥ 5 of 8 seeds (≥ 10 of 16)" with "on ≥ ⌈5n/8⌉ of n seeds (5 of 8, 8 of 12, 10
of 16)", and replace "fewer than 6 of 8 (12 of 16) seeds" with "fewer than ⌈3n/4⌉ of n seeds (6 of 8, 9 of 12, 12 of
16)".**

**T7. §9.1: after the "coordinate seeds" bullet, add** (ruling item 7; SHOULD 5):
> - *(Amendment F.)* The sweep's seeds are (seed, s_j, t_j) triples. RBT-118 is asked to run them with their salts.
>   Its n = 20 at each anchor then **mixes 8 (or 16) screened sweep seeds with 12 (or 4) unscreened seeds of its own,
>   at all three anchors, W118-a, W118-b and W118-c**. The "RBT-118" anchor column handles the mix as follows:
>   - **the sweep's seeds are reported separately** at every anchor, labelled "screened (amendment F)". They are the
>     only ones that enter the sweep's map.
>   - RBT-118's own unscreened seeds are reported beside them as RBT-118's.
>   - Pooled figures, if RBT-118 reports any, are labelled as mixed. The sweep does not use them.
>   - **At W118-a and W118-c**, the sweep's seeds carry the same claim label as every Stage-1 point.
>   - **At W118-b**, the screen's own point, the sweep's screened seeds are **selected on survival**, so their founding
>     and survival there are not evidence. That column reports income and share only, labelled "screened here".
>   - **The anchor fallback** forks M and N from a **two-fauna** S 0–59 at W118-b at (s_j, t_j) (F5; MUST 3). It does
>     not fork from the single-fauna screen states.
>   - If RBT-118 declines to carry the salts, the sweep's own anchor fallback applies, as §9.1 already provides.

**T8. §4.2, R-B: replace "gets seeds 9–16" with "gets seeds 9–16 (screened before Stage 1, amendment F5; for a Stage-1 n
other than 8, seeds n + 1 … 2n)".**

**T9. §5.6: add item 7:**
> 7. **RBT-129c (amendment F).** RBT-129c needs its own implementer-then-adversary pass. It delivers:
>    - a `designed_stream_salt` mirroring `holistic_stream_salt`;
>    - both salts on the `ecology` subcommand and in `stages.py`'s configs;
>    - a Stage-F screen driver implementing F1–F5, including the salt-0 single-fauna re-run and its byte-compare;
>    - the two-fauna fork source at W118-b;
>    - the K-SALT comparison (F7).
>
>    **Tests:**
>    - the breed-key test and `tests/test_rbt130.py::test_the_null_stream_is_independent_of_every_other_stream`,
>      extended to the designed keys `(1, t)`;
>    - salt 0 is byte-identical to today (golden);
>    - a designed salt moves only the designed stream;
>    - both salts survive the season-59 fork and a `--resume`;
>    - salts compose with `merge_null` and `only_fauna`;
>    - the screen stops at the first passing salt and at the cap.

**T10. §11.1:**
- **In item 1, add a gate:**
  > RBT-129c merged, after its own adversary pass. Stage F run, with the salt-0 single-fauna byte-compare passing. Its
  > screen table posted, with the stop rule (F4: ≥ 3 of 16, or ≥ 2 of seeds 1…8, capped) not fired.
- **In item 2, replace "and the coordinator rules n for Stage 1." with:**
  > then Stage F (amendment F); and the coordinator rules n for Stage 1.
- **In the 02:22 pre-data note, replace "Stage 1's S arms at seeds 129001–129003 resume" with:**
  > Stage 1's S arms at seed 129001 (amendment F: the only census seed whose salts are both 0) resume

  and replace "(about −36 core-h)" with "(about −14 to −26 core-h at the pilot's cost)".

**T11. §11.2, the table: add the row**
> | F founder screen (W118-b, single-fauna S 0–59, seeds 1–16; salt-0 re-run of 1–8; two-fauna fork source) | 5–8 expected + 3 + 3–6 (bound 94 + 3 + 6) | 9–14 expected + 5 + 6–12 (bound 162 + 5 + 12) |

and add below the table:
> *(Amendment F.)* Stage 1 at n = 8, re-costed at the pilot's 23.35 / 43.72 core-s with the census resume for 129001
> only: 878–985 / 1,504–1,611 core-h. These are upper bounds, and they include about 171 / 320 of M + N that the T5
> gate re-admits. The other rows are not re-costed.

**T12. §13: add "New in amendment F":**
> 1. p_H, the anchor-to-point transfer rate, rests on one or two draws per point. Its plug-in value is 1 on the 24
>    class-A points by construction. Stage 1 measures it; it is not a gate. Expected validity is therefore a range,
>    5.4–7.7 of 8.
> 2. The screen selects the whole holistic stream, not the founders alone. A founders-only salt would need new code; it
>    was judged not worth it (AMENDMENT-FOUNDING §2.0).
> 3. If the stop rule fires, (b) the runway is the fallback. It has no feasibility evidence yet, and it needs its own
>    amendment.

**T13. §14: add rows for** `AMENDMENT-FOUNDING.md`, `founding-amendment/founding_expect.py → founding_expect.txt` and
`founding-amendment-adversary/` (#494).

Unchanged: §3, §6.2–6.4, §7, §8, §10 and §12. §8's verdicts inherit the claim label of §2.0.

## 8. Ruled; what remains for the owner

**The coordinator's ruling** (#493, comment 5883124591) adopted:
- option (a);
- n = 8, conditional on the owner approving the cost;
- the criterion of ≥ 30 of 60 alive;
- the stop rule, with the added "≥ 2 of seeds 1…8";
- the claim label;
- T5 and T7 as fixed here;
- the salt-0 re-run as REQUIRED;
- the relabelled bound, with no kill rule;
- (b) as the fallback, with its own amendment.

**Next:**
- **RBT-129c** (the designed salt, the screen launcher and the fork source) needs its own implementer-then-adversary
  pass after this merges.
- **The owner approves the cost** (upper bounds):
  - RBT-129c: code only, no core-h;
  - **Stage F: about 5–14 core-h expected, bound 94 / 162;**
  - **the REQUIRED salt-0 single-fauna re-run: +3–5;**
  - **the two-fauna fork source: +3–12** (only if the anchor fallback runs);
  - **Stage 1 at n = 8, gated: 878–985 core-h** at the pilot median, **1,504–1,611** at the pilot ceiling. This is
    +28 / +52 over the nominal registered figure, and it includes about 171 / 320 of M + N re-admitted by T5.

**The launch is a separate owner decision**, taken after the cost approval. Nothing in this amendment launches
anything.

## 9. Files

| file | what |
|---|---|
| `AMENDMENT-FOUNDING.md` | this amendment |
| `founding-amendment/founding_expect.py` → `founding_expect.txt` | expected valid seeds, P(PARTIAL), income power and cost per option and per Stage-1 point. It reads `stageP0-readout/founders.txt` and runs no simulator (stdlib; about 2 s) |
| `founding-amendment-adversary/` (#494) | the adversary's report, `rederive.py → rederive.txt` (the validity-model range) and the Monte Carlo power check |

Reproduce: `python3 runs/RBT-129/founding-amendment/founding_expect.py > runs/RBT-129/founding-amendment/founding_expect.txt`.

## 10. Fixes applied (ruling #493 comment 5883124591; adversary #494)

| item | fix | where |
|---|---|---|
| MUST 1 | 129004 at `c1-p030-PW-G`: holistic dead by 16, designed alive at the merge and dead by 93; class-B E[valid] 0.00 (plug-in) / 0.56 (Jeffreys on p_H) / 0.69 (on both) | §1, §5, §2.1, script |
| MUST 2 | plug-in p_H = 1 on class A by construction; the range 5.4–7.7 / 15–20 / 0.56–0.79 and 0.68–0.90 in the adversary's form; power labelled an upper bound (validity at 59); "nearer the plug-in" deleted | §0, §5, §2.1 |
| MUST 3 | the anchor-fallback fork source is a two-fauna S 0–59 at (s_j, t_j) at W118-b, costed | F5, T7, §6 |
| MUST 4 | the claim label "stream draws (founders and their early history)" | §0, §2.0, T1, T4, T7 |
| MUST 5 | "≤ 47" relabelled as "if failed attempts die by season 15"; the true bound 94 / 162; no kill rule | §0, F4, §6, T11 |
| SHOULD 1 | stop at ≥ 3 of 16 or ≥ 2 of seeds 1…8 capped | §0, F4, T10 |
| SHOULD 2 | criterion ≥ 30 of 60 alive at 59 | §0, F2, T1, T2 |
| SHOULD 3 | salt-0 single-fauna re-run of seeds 1–8, REQUIRED, byte-compared with the census and pilot halves | §0, F1, F5, T2, T9, T10 |
| SHOULD 4 | T5's g0 fixed; the slot-freeing rule labelled DATA-INFORMED; M + N of 171 / 320 disclosed | T5, §6, T11 |
| SHOULD 5 | T7 covers W118-a/b/c with mixed seeds; the sweep's seeds reported separately | T7 |
| SHOULD 6 | the null-key test cited; RBT-129c extends it and the breed-key test to designed keys (1, t) | F3, T9 |
| SHOULD 7 | registered 24-point mean 0.365 / 0.488; n = 2 power 0.108 / 0.129 (quadrature fixed in the script) | §0, §5, script |
| SHOULD 8 | the pessimistic row shrinks p_D as well as p_H | §2.1, §5, script |
| ruling 1 | (b) is the fallback and needs its own amendment | §2.1, F4, T12 |
