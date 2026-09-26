# RBT-106 design adversary: report on PR #213

*Design adversary for RBT-106, 2026-09-26, dispatched by the coordinator (session_01WKXr6PgNkscGhVc7Bzth9k).
It attacks the pre-registration at PR #213's head, `1163d62` (`results/RBT-106-design`). It measures and
does not tune, and it edits no file of the designer's. Every probe is under `runs/RBT-106/adversary/`,
with its readout committed beside it. **No arm was launched.** The throwaway runs were at most 20
seasons, in scratch directories. Two reads touch RBT-104's live arms: the first 20 seasons of S1-801
and S1-4 (seasons rows and lineage records only), restored from their checkpoints for the cross-ticket
check, and nothing later.*

**Platform, for every number below:** `x86_64`, MuJoCo 3.14.0, numpy 2.4.6, on a four-core cloud
container. `rabbitstew/` at the head is byte-identical to c872e80, RBT-104's launch commit.

## Verdict in one paragraph

The flag is clean. The patchy world is exactly one field, keeps part 2's instant regrowth, and is
byte-identical at 0 on a second seed. RBT-106's S1 command reproduces RBT-104's **live** S1-801 and
S1-4 arms for 20 seasons, byte for byte, so the primary pair really is one flag apart today. The decoy
also holds in the patchy world: **none of ten unselected, compass-free part-2 lines reads
FOOD-DEPENDENT there**. **The design is not ready to launch.** There are four MUST-FIXes, and none
needs a new arm or a change to any arm's command:
- **F3:** the "held" null leaves out the operator's crossover, which moves the planted global unit
  between lineages in about 15% of births.
  - With crossover, the structure criterion's false-positive rate is **15.0%, not 6.0%**. The paying
    criteria keep 2.0% and 1.0%, but a third of their k is bare-rooted transfer.
  - The same fact explains RBT-104's six bare-rooted S8-801 payers, and puts that CONTINUE inside
    the null.
- **F5:** at the q the design itself states, the factorial returns NOT DECIDED about 85% of the time,
  and its registered predictions exceed its own model's ceiling.
- **F6:** the primary FD call counts any food use. In a patchy world selection can favour food use that
  is not a compass, so P-EVOLVED must ask the compass attribution or stop saying "compass".
- **F2:** the cross-ticket identity must be enforced at launch, not assumed.

Depth matching holds and errs conservative (F4). **Option H is the best-powered and cleanest test of
the ticket's question** (F7), and I recommend it ahead of the factorial.

---

## Findings

| # | severity | item | one line |
|---|---|---|---|
| F1 | NONE | 1 flag | One field; byte-identical at 0 on seeds 801 (designer) and 4 (here); `regrow_delay` 0 everywhere; `rabbitstew/` = c872e80; tests pass |
| F2 | **MUST-FIX** (small) | 2 cross-ticket | RBT-106's S1 command reproduces RBT-104's live S1-801 and S1-4 for 20 seasons byte for byte; nothing registered keeps it so when P1 launches later |
| F3 | **MUST-FIX** | 3 null | The null leaves out crossover, which moves the global compass between lineages. `same` false-positive rate **15.0%, not 6.0%**; 31–44% of k is bare-rooted transfer; season-150 gates 16–32% per seed. RBT-104's S8-801 CONTINUE sits inside this null |
| F4 | CAVEAT | 3 depth | At the arms' depths (proxy ×2, ×3) every rate falls (12.0 / 0.0 / 0.5%); the asymmetry cannot manufacture a patchy win; the patchy genealogy's clustering is unmeasured |
| F5 | **MUST-FIX** | 4 interaction | At the designer's own q, the factorial reads NOT DECIDED about 85% of the time (BOTH NEEDED 0.01–0.06); F-0's NEITHER 0.40 exceeds the model's ceiling of 0.26 |
| F6 | **MUST-FIX** (rule or wording) | 6 decoy | Ten unselected bare lines: 0 of 10 FD in the patchy scoring, so food-blind foragers do not pass. But the primary FD call does not ask for a compass, and patchy selection can favour non-compass smell use |
| F7 | CAVEAT | 5 option H | The cleanest test of the ticket's question; its null is unmoved by crossover (1.0%); SUPPORTED power 0.85. Recommend H before the factorial |
| F8 | CAVEAT | 7 power | Every "absent" has a matched-null figure. With the measured bare distribution, P-NULL misses "prize, weakly" at 0.37 (was 0.27) |

---

### F1: One flag. NONE

- **Byte identity at 0, on a second seed** (`one_field_4.txt`). Part 2's command (`command.part2()`) with
  `--food-patches 0`, seed 4, 6 seasons, passes RBT-104's `byte_identity.default` (imported). `seasons.txt`
  is BYTE-IDENTICAL to the first 12 rows of `runs/RBT-90/forage-4/seasons.txt`. `config.json` is equal to
  the committed config outside seasons, generations and workers; `ecology.breed_stream` is tolerated at
  its default. The designer's check covered seed 801, so the two seeds agree.
- **One field at 3.** Seed 4's `config.json` at `--food-patches 3` differs from the committed part-2
  config in `sim.food.patches` 0 → 3 and nothing else. Its `sim` block equals
  `runs/RBT-106/world-patchy/config.json`'s, which is the world the prize and the controls were
  measured in.
- **`regrow_delay` is 0.0 in all three:** part 2, the patchy run and `world-patchy`. `regrow` is true
  and `patch_radius` is 0.6. The patchy world keeps part 2's instant regrowth, so persistent arenas stay
  off.
- **Trial merge.** Integration (`origin/claude/new-session-4cao7d`, 7aa2628) is already an ancestor of
  the head. `rabbitstew/` is byte-identical to c872e80, RBT-104's launch commit.
  `tests/test_rbt106.py` and `tests/test_rbt104*.py` pass: 17 passed.

### F2: P1 against RBT-104's S1 crosses tickets. It is the same run today, but nothing registered keeps it so. MUST-FIX (small)

**Measured** (`cross_ticket.py`, `cross_ticket.txt`). I ran RBT-106's own S1 command, as `command.py`
builds it, for 20 seasons on seeds 801 and 4 at the head. I compared each run with RBT-104's **live**
S1-801 and S1-4 arms, restored from `ckpt/rbt-104-S1-SEED`, reading their first 20 seasons only:
- `seasons.txt`: **40 of 40 rows BYTE-IDENTICAL on both seeds**;
- `lineage.jsonl`, every record with generation < 20: **identical** (1,995 records on 801 and 2,329
  on 4);
- `config.json`: equal, except `ecology.seed_conventional`, which is the founders' directory
  (`runs/RBT-106/founders-w1-SEED` against `runs/RBT-104/founders-SEED`). Both launchers check the same
  digest, and the founders regenerate to it on all ten seeds;
- platform: x86_64, MuJoCo 3.14.0, numpy 2.4.6 on both.

**So today the uniform twin is exactly one flag away**: same founders, streams, code and platform.

**What is missing:** P1 will launch later than RBT-104's arms, from whatever the integration head
is then.
- `run_arm.sh` records the platform but not the commit.
- Nothing refuses a launch if `rabbitstew/` has moved since c872e80. Other tickets merge into
  integration continuously (RBT-96's salt, RBT-105's breed stream).
- The token-for-token test (`test_arm_commands_share_rbt104s_s1_command`) pins the **command**, not the
  **run**.
- The same applies to the §7.3 contingency S1/S8 arms, which RBT-106 would launch itself.

**Required:**
- (a) `run_arm.sh` writes `git rev-parse HEAD` and the tree hash of `rabbitstew/` beside
  `platform.txt`, and **refuses** if `git diff --quiet c872e80 HEAD -- rabbitstew` fails. Either that,
  or it re-runs `cross_ticket.py` (20 seasons, seeds 801 and 4) at the launch commit and refuses
  unless both read SAME RUN.
- (b) `readout.py` prints each arm's commit and drops a pair whose code differs.

This is a pre-launch check of about 4 minutes per seed.

### F3: The "held" null leaves out the operator's crossover. With crossover, the structure criterion's false-positive rate is 15.0%, not 6.0%. MUST-FIX

**The omission.** `null_genealogy.py`, the §5.1 baseline, and RBT-104's `persistence.py` all carry
a genome down its **first parent only**, "crossover left out". But the ecology's designed-body operator
is `crossover_controller` **then** `mutate_controller` (`ecology.py` `_breed`):
- a breeder takes a mate with `crossover_rate` 0.3. In part 2's genealogies, 30.3% of designed births
  record a mate (seed 801: 374 of 1,235);
- `crossover_controller` then hands the child **the mate's whole global brain** with probability 0.5
  (`genetics.py:434`).

RBT-97's routed motif is a global unit, so in about 15% of births **the compass a child carries comes
from `parents[1]`**. It does not come along the `parents[0]` chain that `held.py` uses for root, sign
and depth. As a result:
- **bare-rooted genomes carry planted compasses by crossover.** `held.py` counts them in k "at either
  sign", but they enter neither n nor μ;
- planted-rooted genomes lose theirs to bare mates, or carry a copy whose depth is not their
  `parents[0]` depth.

**Measured** (`null_xover.py`, `pool_xnull.txt`). This is the designer's null, imported, on the same
ten real part-2 genealogies, founders, plant and `held.py` arithmetic, with one change: the operator is
the ecology's own, crossover then mutation, with the mate taken from the recorded `parents[1]`. There
are 20 replicates per seed and cell. **The mutation-only branch reproduces the designer's committed
`null/` files, k, n and B at 300 and 599 for every replicate, in 30 of 30 seed-cells**, so the
difference below is crossover alone.

| cell (criterion) | HELD at 300 and 599: designer's operator | **the ecology's operator** | bare-rooted share of k | HELD at season 150 (the gate), per seed |
|---|---|---|---|---|
| P1, S1 (`same`) | 12/200 = 6.0% | **30/200 = 15.0%** | 1,240 / 2,824 = **44%** | 63/200 = 32% |
| P8, S8 (`pay64`) | 5/200 = 2.5% | 4/200 = 2.0% | 127/376 = 34% | **42/200 = 21%** (designer's operator 13%) |
| HU, HP (`pay32`) | 2/200 = 1.0% | 2/200 = 1.0% | 71/229 = 31% | 33/200 = 16.5% |

**What this changes:**
- **The structure criterion's false-positive rate is 15.0%, not 6.0%.** §5.3's "near the nominal 5%" is
  wrong, and so is the q it feeds. This hits P-1 and the structure HELD counts reported beside the
  primary. With q = 0.15 in each arm, |#HELD(P1) − #HELD(S1)| ≤ 1 is far from assured.
- **The paying criteria's arm-level rates stand** (2.0%, 1.0%). But a third to nearly half of their k
  comes from bare-rooted genomes under no selection at all. This k is transfer, not de novo arrival.
- **Every season-150 gate is looser than stated.** P8's gate has a per-seed false-positive rate of
  **21%**, so P(≥ 1 of 2 seeds CONTINUE | null) = **0.38**. Option H's is 16.5% per seed (0.30). These
  gates are futility-only, so this costs sessions, not verdicts.
- **RBT-104's own gate** (a CAVEAT for the coordinator, not RBT-106's to fix). S8-801 read
  CONTINUE at k = 18 (6 bare-rooted), n = 26, B = 8. In the full-operator null on seed 801's part-2
  genealogy, 6 of 20 replicates read HELD, at k = 11–18 with 5–9 of them bare-rooted (B = 10 there; `null_xover/xnull-w1-k8-801.txt`,
  season 150). **The six bare-rooted payers the coordinator asked about at 21:21 are what crossover
  produces with no selection**, and the split gate (FUTILE 4, CONTINUE 801) is what the null gives
  about 38% of the time.

**Required:**
- (a) Replace §5.3's null by the full-operator null (`null_xover.py`, or its logic in
  `null_genealogy.py`) and restate the rates as 15.0 / 2.0 / 1.0%.
- (b) Either score bare-rooted hits separately (k_planted against B, k_bare reported), or state that k
  includes transfer by crossover. The first is cleaner, because it makes k and n count the same
  population.
- (c) Revise P-1 and the gate rates in §7.2 and waves.txt. The §5.1 baseline tables (depth → fraction,
  one lineage) cannot carry crossover at all. They remain the right per-lineage expectation, but they are
  not the false-positive rate.

### F4: Depth matching. It holds, and deeper genealogies make "held" harder, not easier. CAVEAT

**The question.** The patchy arms breed faster, about 1.6–1.8× at K = 1 and 3.1–3.5× S1U's births for
P8 (§4). Are "held" and its false-positive rate right at the depths those arms will reach?
- `held.py` matches μ to each genome's own `parents[0]` depth, so the mean is depth-matched by
  construction.
- But §5.3's rates were measured on part 2's genealogies, at part 2's depths: mean living depth 5.0–5.2
  at season 150, 9.3–10.1 at 300 and 18.7–20.0 at 599 on seeds 801 and 4. They were not measured at
  the arms' depths.

**Measured** (`null_xover.py --deepen M`, `pool_xnull_deep.txt`):
- **the proxy:** each real part-2 birth applies the operator M times (crossover once, then M mutation
  draws) and counts M generations of depth for μ. This keeps part 2's clustering and multiplies the
  depth;
- **the settings:** M = 2 for the K = 1 cells (P1, HP), and M = 3 for P8, whose depth at 599
  (about 57) passes the baseline's cap at 40;
- **the operator:** the full one, crossover included.

| cell | HELD at 300 and 599, part-2 depth (F3) | **at the arm's depth (proxy)** | per-seed gate rate at 150: part-2 depth → proxy |
|---|---|---|---|
| `same` (P1, S1) | 15.0% | **12.0%** (×2) | 32% → 28% |
| `pay64` (P8, S8) | 2.0% | **0.0%** (×3) | 21% → 14% |
| `pay32` (HU, HP) | 1.0% | **0.5%** (×2) | 16.5% → 13.5% |

- **Deeper is more conservative at every criterion.** μ falls with depth, but so does the chance that a
  clustered clade still carries the unit. The cap at depth 40 also errs toward a larger μ.
- **The pairs are asymmetric, and in a direction that cannot manufacture a patchy win.** A patchy arm
  sits deeper than its uniform twin, so its null rate is the lower of the two: S1 15.0% against P1
  about 12%; HU 1.0% against HP about 0.5%. SUPPORTED and the P-pair structure contrast are therefore
  slightly harder to reach than a symmetric null would make them.
- **The caveat.** The proxy multiplies depth on part 2's clustering. The patchy genealogy's own
  clustering (faster turnover can mean faster coalescence) is not measured, and cannot be without an
  arm.
  - `held.py` should print, beside every reading, the arm's mean depth and its number of distinct
    planted roots among the living. Then the reader can see whether the living collapse onto a few
    clades.
  - §4's "baselines run to depth 40" should say that P8 will pass 40, and that the cap is
    conservative.


### F5: The factorial's predictions contradict its own power model, and at the designer's stated q it will almost surely read NOT DECIDED. MUST-FIX

§6.3 states q only as hypotheses: P1 ≈ 0.05, and **P8 ≈ 0.15–0.3 "if the prize matters"**. `power.txt`
tabulates layer 4 only at q_P8 = 0.3 and 0.5. I ran the designer's `power.factorial`, **imported
unchanged**, at the stated values (`power_adv.txt`, part A):

| q S1, P1, S8, P8 | n | P(I > 0) | BOTH NEEDED | NEITHER | **NOT DECIDED** |
|---|---|---|---|---|---|
| 0, 0.05, 0, 0.15 | 10 | 0.054 | 0.012 | 0.134 | **0.847** |
| 0, 0.05, 0, 0.2 | 10 | 0.083 | 0.022 | 0.107 | **0.864** |
| 0, 0.05, 0, 0.3 | 10 | 0.169 | 0.058 | 0.063 | **0.872** |
| 0, 0.05, 0, 0.3 | 7 | 0.102 | 0.035 | 0.211 | 0.752 |
| nothing holds (0, 0, 0, 0), from `power.txt` | 10 | 0.025 | 0.001 | **0.264** | 0.73 |

- **F-0 is incoherent with this table.** It gives NEITHER 0.40 and NOT DECIDED 0.34. But NEITHER
  cannot exceed 0.264 at n = 10 even when *nothing* holds. That ceiling is bare-line false positives:
  any cell with 2 FD lines, or any positive interval, blocks it. At the stated q, NEITHER is 0.06–0.13.
  Even at n = 7 it is at most 0.47.
- **F-1 (I's interval above zero, 0.20)** is above the model's 0.05–0.17 at the stated q.
- **What the factorial buys under the designer's own prior:** P(BOTH NEEDED) ≈ 0.01–0.06, and about
  85% NOT DECIDED. That is 5 sessions (A′ + B), or 9 with the S8 contingency, for an interaction the design
  says it cannot resolve.
- **RBT-104's split gate changes nothing about S8's contribution.** All 20 RBT-104 arms are running,
  so S8 exists on ten seeds and the §7.3 S8 contingency is moot. The gate reading is not evidence that
  S8 holds anything (F3).
- **P-NULL at 0.72 is coherent.** The designer states that it fires 0.72 under "nothing", "reach alone"
  and "both needed" alike, and the verdict table's order (PRIZE, REACH, EACH, BOTH, NEITHER) is
  exclusive and exhaustive. The problem is the factorial's predictions and value, not the table's logic.

**Required:**
- (a) Re-derive F-0 and F-1 from `power.factorial` at the stated q, or state a different q and argue it.
- (b) The coordinator should rule on the factorial knowing its expected yield is NOT DECIDED about 85%
  of the time (F7 on option H).

### F6: The decoy in a patchy world. Food-blind foragers do not pass it, but the primary FD call does not ask for a compass. MUST-FIX (rule or wording)

**The worry.** In a patchy world a forager can gain from smell without steering. Slowing where smell is
strong (kinesis) keeps it on a patch. The rotated-layout decoy moves the patches the noses smell, so
kinesis loses income under the decoy, and F = intact − decoy reads it as food use. Could a food-blind
or non-compass forager read FOOD-DEPENDENT?

**Measured on ten lines** (`bare_patchy/`, `pool_bare.txt`):
- **the bodies:** part 2's own champions, bests 300–590, never selected in the patchy world, with no
  compass anywhere;
- **the scoring:** readout (b) through the designer's `cross_world.py`, unchanged, in `world-patchy`,
  on 64 paired seeds.

The designer had one line (801).

| | result |
|---|---|
| line calls | **0 of 10 FOOD-DEPENDENT; 10 of 10 VETOED** by the zero count |
| line F | mean **−0.056**, SD 0.145 (designer's model: N(+0.10, 0.20)); one line, 806, has its interval below zero |
| zero-count share | 0.52–0.65, mean 0.58 (the veto fires above 0.50); **two lines (2, 807) sit at 0.52–0.53** |
| without the veto | still 0 of 10: no line's interval excludes zero from above |
| attribution | "no compass gain" on all 10: the compass lesion leaves income unchanged |
| per body | **26 of 70 bodies have |F| ≥ 0.25 with lesion = intact**, of both signs (−0.81 to +0.92) |

**What this says:**
- **Unselected food-blind lines do not pass the decoy in the patchy world**, with or without the veto.
  The designer's bare-line model (mean +0.10, FD 0.10) is conservative.
- **Their noses do matter, though, outside any compass.** A third of bodies move by a quarter of an item
  or more between real and decoy smell with the compass lesioned, and they do so symmetrically. This is
  trajectory sensitivity to local smell inputs, averaging to zero because nothing selected it.
- **In P1 something will have selected it.** P1's lines evolve 600 seasons in the patchy world, where
  local smell use that keeps a body on a patch (kinesis through the local brains) pays and is not a
  compass.
  - Readout (b)'s PRIMARY call (F = intact − decoy) credits it as FOOD-DEPENDENT.
  - The ATTRIBUTION rule (the compass lesion as base) is what separates it, but `readout.py` reads only
    the LINE's primary call.
  - P-EVOLVED says "the planted compass became food-dependent champions". A kinesis line would satisfy
    the rule and falsify the sentence.
  - The uniform twin S1 has much less to gain from kinesis, so the bias is toward P-EVOLVED.
- **The veto is doing most of the specificity on bare lines**, with two of ten within 0.03 of the
  threshold. A richer, selected P1 line with fewer tied bouts would not be vetoed on that ground. That is
  correct behaviour, and it is another reason the compass attribution must carry the "compass" claim.

**Required** (either one; the choice is the designer's):
- (a) P-EVOLVED, PRIZE SUFFICES, BOTH NEEDED and H's "function follows" count a line only if its
  ATTRIBUTION also reads `compass: FOOD-DEPENDENT` (the compass lesion removes the gain, and the decoy
  retains < 25%).
- (b) Keep the rule, but name the verdicts "food-dependent champions", and report the attribution count
  beside every count as the compass reading.

Option (a) costs nothing new, because function.py already prints the attribution. Its power is
unmeasured on evolved lines, though the installed-compass control reads attribution FOOD-DEPENDENT
(decoy retains 2.1%). Beside it, `readout.py` should print the lesioned-income gain per arm, to show
non-compass smell use directly.

**The veto logic itself** (more than half of the paired seeds exactly tied counts as vetoed, which means
not food-dependent) is as RBT-104 registered it. A vetoed line counts as not food-dependent in every
rule. NONE on that.


### F7: Option H is the cleanest test of the ticket's question, and its null survives crossover. CAVEAT (a recommendation on cost)

- **It answers a different question from P1 and P8.** P1 and P8 ask whether selection *grows* a
  sub-paying structure into a food-dependent compass, which needs reach. H asks whether selection
  *holds* a compass that already pays at founding, in both worlds: compass-signed H founders earn
  +1.0 [+0.4, +1.6] uniform and +1.6 [+0.6, +2.6] patchy on 801 (§3.3). Only s differs between HU and
  HP; u ≈ 0.29 is the same. That is the ticket's literal question, and the only arm pair here whose
  treatment acts from generation 0.
- **Its false-positive rate does not move with crossover:** 1.0% under both operators (F3).
- **Its power is the best in the design:** 0.85 for SUPPORTED's count at (q_U 0.15, q_P 0.60),
  against the factorial's ≤ 0.06 for BOTH NEEDED at its stated q (F5).
- **Its criterion (a = 32 rung) is justified.** The planted unit reads 24.1 on its own links at founding,
  just under the a = 64 rung, and a = 32 pays in both worlds (`prize.txt`). NONE on that.
- **Its likely outcome is informative either way:**
  - FALSIFIED-a ("the uniform prize already holds a paying compass") would locate RBT-104's failure in
    masking and reach, not in the prize;
  - FALSIFIED-b would locate it in the bias gate.
- **Recommendation:** if the budget covers one option, run H before the factorial. H0 is 2 sessions with
  its own gate (read at 16.5% per-seed false positive, F3).

### F8: Matched-null power on every "absent" verdict. CAVEAT

- P-NULL, P8-NULL, NEITHER and FALSIFIED-b each carry a P(absent | H) in `power.txt`. The designer's
  wording of P-NULL ("says nothing about the prize once reach is short") matches it.
- **Two inputs are borrowed rather than measured:**
  - (i) the layer-1 line power (uniform per-body spread);
  - (ii) the bare-line FD rate of 0.10 and F ~ N(0.10, 0.20).

  F6 measures (ii) in the patchy world: F ~ N(−0.056, 0.145) and 0 of 10 FD. Re-running the
  designer's layer 4 with those numbers (and FD 0.05) (`power_adv.txt`, part B):
  - it changes little under the alternatives;
  - **P-NULL's miss rate under "the prize suffices, weakly" (q = 0.25) rises from 0.27 to 0.37**,
    because a bare line's F sits lower, so the paired interval clears zero less often;
  - under "nothing holds", P-NULL rises from 0.72 to 0.89.

  Both belong in §6.3's P-NULL paragraph.
- **F3's 15% rate** replaces the 0.08 "allowed for clustering" wherever it feeds the structure
  criterion. The paying criteria's 0.08 remains conservative (2.0%, 1.0%).
- **Lesson 7 (brackets):** no cell is insolvent in the smoke runs (§4), so the point predictions are
  permitted. NONE there.


## What would clear the design

1. **F2:** a commit/tree record in `run_arm.sh`, and a refusal if `rabbitstew/` differs from c872e80 (or
   `cross_ticket.py` passing at the launch commit); `readout.py` prints each arm's commit.
2. **F3:**
   - the full-operator null (15.0 / 2.0 / 1.0%) in §5.3;
   - bare-rooted hits scored apart from k, or k's transfer stated;
   - P-1 and the gate rates revised.
3. **F5:** F-0 and F-1 re-derived from `power.factorial` at the stated q, and the coordinator told the
   factorial's expected yield.
4. **F6:** P-EVOLVED and the factorial's positive verdicts either require `compass: FOOD-DEPENDENT` on
   the counted lines, or are renamed "food-dependent" with the attribution count reported beside them.

The CAVEATs (F4, F7, F8) need a sentence each. F4 also needs `held.py` to print the mean depth and the
count of distinct planted roots, and F8 the revised P-NULL figures. The coordinator should rule on
H against the factorial.

## Files (all under `runs/RBT-106/adversary/`)

| file | what |
|---|---|
| `ADVERSARY.md` | this report |
| `cross_ticket.py`, `cross_ticket.txt` | F2: RBT-106's S1 command against RBT-104's live S1-801 and S1-4, 20 seasons |
| `one_field_4.txt` | F1: the flag on seed 4 (byte identity at 0; one field at 3; regrow_delay) |
| `null_xover.py` | F3, F4: the designer's null with the ecology's crossover put back (`--deepen M` sets the depth proxy) |
| `null_xover/`, `pool_xnull.py`, `pool_xnull.txt` | F3: ten seeds × three cells × 20 replicates at seasons 150, 300 and 599; the mutation-only branch reproduces the designer's `null/` in 30 of 30 seed-cells |
| `null_xover_deep/`, `pool_xnull_deep.txt` | F4: the same at depth ×2 (K = 1 cells) and ×3 (K = 8) |
| `bare_patchy/`, `pool_bare.py`, `pool_bare.txt` | F6: part 2's bare champions on ten seeds, scored by readout (b) in the patchy world (`cross_world.py`, unchanged) |
| `power_adv.py`, `power_adv.txt` | F5, F7: the designer's `power.factorial` at the q the pre-registration states; the power model with the measured bare-line distribution |
