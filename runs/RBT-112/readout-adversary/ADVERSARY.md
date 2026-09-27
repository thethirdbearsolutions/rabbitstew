# RBT-112 readout adversary: PR #372 (`results/RBT-112-readout`, head `1052c38`)

*Fresh readout adversary, 2026-09-27. POST HOC throughout: nothing here changes a registered rule or number, and
nothing here is scored.*
- No file on #372's branch, no registered file and no arm was modified. No ecology run was made.
- The probes ran on this branch (cut from `7557d23`) in a clean `pip install -e '.[dev]'` venv without scipy, on
  x86_64 with MuJoCo 3.14.0 and numpy 2.4.6.
- All ten HZ arms were restored from `ckpt/rbt-112-HZ-SEED` (`scripts/durable.sh restore`). The w = 32 founders were
  rebuilt with `runs/RBT-106/founders.py`; all ten digests match the committed ones. `ownnull.sh` records every command.
- Nothing from RBT-107 was read, run or rendered.

## Bottom line: **CONFIRMED-WITH-CAVEATS**

**VERDICT Z: FALSIFIED stands, and the instrument could have fired.**
- **Every number re-derives** (A2).
  - `readout.txt` and `sensitivity.txt` regenerate byte for byte.
  - All 20 HZ `held-*.txt` regenerate byte for byte from the checkpoints.
  - Independent stdlib code gives the same HELD, LOST, COMPASS, paired F and SE-Z.
- **HELD was reachable, and not low-power, on 8 of 10 HZ seeds** (A1).
  - To be HELD, k_planted had to exceed about 53% of the planted-rooted genomes at 300 and about 29% at 599. That
    is a real bar, not a ceiling.
  - Run on each HZ arm's **own** genealogy, the S = 0 null puts its 95th percentile of k_planted **at or above** the
    registered B at every usable reading. The registered bar is, if anything, too *lenient*, not too strict.
  - 805's HELD is above every one of the 200 own-genealogy null replicates at both readings.
- **Power at the arms' realised n** (A6).
  - FALSIFIED fires with probability 0.000–0.054 at s = 0.2.
  - The arms' own likelihood puts the selective advantage s in [0.00, 0.08].
  - The "strong evidence against s ≥ 0.2" claim holds, and holds more strongly than §2 states.
- **FUNCTION FOLLOWS is robust** (A4).
  - It survives losing its two most marginal COMPASS lines.
  - The paired F interval stays above 0 with any one or any two seeds removed.

**The caveat is the wording, and it is one MUST-FIX (A3).**
- `readout.py`'s line "the operator is not the stall" is the registered label and stays.
- READOUT.md must not leave it unglossed. It must also carry the two limits the pre-registration attached to it:
  - §6.2: "selection's advantage on the compass is below ~0.1 per generation";
  - §10.4 F3: under SE-Z, "a change in s itself is not handled".
- The evidence supports a narrower sentence: **the bias walk is not what stops selection holding the compass in the
  population**.
- It does not support the unscoped plain-English reading that the operator does not matter. Under S = 0:
  - the compass persists at the operator-alone level;
  - the income-best lines carry it and use it (5 COMPASS lines against 0);
  - under the default operator they do neither.

| # | finding | class |
|---|---|---|
| A1 | HELD could fire under S = 0. B/n was 0.48–0.60 at 300 and 0.22–0.38 at 599; the own-genealogy null's 95th pct was ≥ B; unreachable only on seed 4 (LOST) and at 599 on seed 2 (n = 3). The pre-launch "positive control" (d) was arithmetic reachability at k = n, not passability | NOTE (programme: SHOULD-FIX for future designs) |
| A2 | Every registered number re-derives; `readout.txt`, `sensitivity.txt` and 20/20 held files are byte-identical; `readout.py`, RBT-106's `readout.py`/`held.py`, RBT-104's `peek.py`, `baseline/` and `rabbitstew/` are unchanged since `6dfa780` | NONE |
| A3 | "The operator is not the stall" goes unglossed in READOUT.md. The registered worded limit (s < ~0.1) and SE-Z's "a change in s is not handled" are missing from §1 | **MUST-FIX (wording)** |
| A4 | FUNCTION FOLLOWS is robust: COMPASS 5, ≥ 3 even after losing the two most marginal lines (804, F lo +0.121); paired F lower bound ≥ +0.372 with any two seeds removed; 9 of 10 seeds positive | NONE |
| A5 | Seed 4 LOST is a genuine edge of the registered root rule, not a parsing artefact: all 36 / 9 bare-rooted hits have a planted ancestor through crossover. Counting them would not make seed 4 HELD. 805 HELD is genuine: one clade (c0-12, 53 of 60 at 599), p < 1/200 against its own null | NONE |
| A6 | Power at the realised n is higher than §2's anchors. §2's range "0.005–0.21" at s = 0.2 leans on M15's 0.214. At realised n it is 0.000–0.054; the arms' likelihood gives s ∈ [0.00, 0.08] | SHOULD-FIX |
| A7 | The sensitivity section is print-only and labelled. But S2's "the verdict does not turn on how the null treats crossover" rests on a comparison that is uninformative on 5 of 10 seeds. The own-genealogy null (A1) supports the conclusion; cite it instead | SHOULD-FIX |
| A8 | The power model's layer 3 tied champion carriage to population HELD. The arms break that tie: 5 COMPASS lines with 1 HELD. This is why Z-2 was priced at 0.20 | NOTE |
| A9 | Planted-rooted n is larger in HZ than in HU (599: 386 against 199 of 600). That would be selection acting through clade expansion, which k_planted/n cannot see. The paired interval includes 0 | NOTE |

---

## A1. The instrument: could HELD fire at all under S = 0? — NOTE

**The concern.** Freezing the global biases cuts the operator-alone erasure (u 0.282 → 0.089 per generation), so the
S = 0 no-selection table leaves more paying genomes at each depth, and B = binom_q95(n, μ) rises with it. With n at
55–60 on several seeds, is B near n, so that k_planted > B is unreachable?

**What the bar was** (`instrument.txt` (1)). Per HZ seed, k_planted / n / μ / B at 300 and 599:

| seed | 300: k/n, μ, B, **B/n** | 599: k/n, μ, B, **B/n** | shortfall (k_planted must exceed B) |
|---|---|---|---|
| 801 | 23/55, 0.407, 28, **0.51** | 11/59, 0.176, 15, **0.25** | 6 at 300, 5 at 599 |
| 4 | 1/1, 0.498, 1, **1.00** | 0/0 | LOST (unreachable by construction) |
| 804 | 13/52, 0.377, 25, **0.48** | 11/60, 0.143, 13, **0.22** | 13 at 300, 3 at 599 |
| 805 | 44/55, 0.382, 27, **0.49** | 46/60, 0.179, 16, **0.27** | **HELD** |
| 806 | 0/23, 0.391, 13, **0.57** | 0/26, 0.165, 8, **0.31** | 14 at 300, 9 at 599 |
| 807 | 18/40, 0.396, 21, **0.53** | 16/42, 0.214, 14, **0.33** | 4 at 300; above B at 599 |
| 1 | 29/60, 0.429, 32, **0.53** | 2/60, 0.245, 20, **0.33** | 4 at 300, 19 at 599 |
| 2 | 6/20, 0.417, 12, **0.60** | 0/3, 0.215, 2, **0.67** | 7 at 300; needs 3 of 3 at 599 |
| 3 | 3/55, 0.378, 27, **0.49** | 0/60, 0.155, 14, **0.23** | 25 at 300, 15 at 599 |
| 7 | 8/29, 0.418, 17, **0.59** | 2/16, 0.225, 6, **0.38** | 10 at 300, 5 at 599 |

**Reading it:**
- **There is no ceiling on 8 of 10 seeds.** With n ≥ 10, B/n is 0.48–0.60 at 300 and 0.22–0.38 at 599. HELD needed
  the compass in just over half the planted-rooted living at depth ~10, and in about a third at depth ~20.
  Mutation–selection balance at s = 0.2 gives 0.60 and 0.51 (`instrument.txt` (2), x(d = 10) / x(d = 20)).
- **Seed 4** could not be HELD: n = 1 at 300, 0 at 599. The registered rule counts it as LOST (F14), not as NOT HELD.
- **Seed 2** at 599 had n = 3 and B = 2, so it needed every planted-rooted genome paying. It is near-ceiling there,
  but it failed at 300 anyway (6 of 20 against B = 12).
- **The binding reading was 300.** Of the 8 seeds neither HELD nor LOST, 7 fell further short at 300 than at 599;
  seed 1 is the exception. 807 was above B at 599 (16 > 14) and failed at 300 (18 ≤ 21). This is the registered two-reading rule working as designed, not a
  defect. But READOUT.md should say which reading decided the seeds.

**Is B the right bar? The own-genealogy null** (`ownnull_pool.txt`, `ownnull/`). This is RBT-106 h-adversary H1's
check, moved to the S = 0 arm:
- `runs/RBT-112/null_xover_s0.py` (unchanged, `--global-bias-sigma 0`) ran on **each HZ arm's own lineage.jsonl**,
  with the arm's own founders, 200 replicates per arm.
- The null's n and B equal the arm's at every reading (asserted).
- Each replicate is re-scored under the registered rule (k_planted = k − k_bare > B).

| arm | B at 300 / null 95th pct | B at 599 / null 95th pct | observed k_planted 300 / 599 | P(null ≥ observed) at both |
|---|---|---|---|---|
| 801 | 28 / 28 | 15 / 23 | 23 / 11 | 0.115 |
| 804 | 25 / 25 | 13 / 20 | 13 / 11 | 0.085 |
| **805** | 27 / 33 | 16 / 34 | **44 / 46** | **0.000 (0 of 200)** |
| 806 | 13 / 10 | 8 / 5 | 0 / 0 | 1.000 |
| 807 | 21 / 25 | 14 / 19 | 18 / 16 | 0.060 |
| 1 | 32 / 29 | 20 / 26 | 29 / 2 | 0.065 |
| 2 | 12 / 9 | 2 / 0 | 6 / 0 | 0.250 |
| 3 | 27 / 33 | 14 / 28 | 3 / 0 | 0.985 |
| 7 | 17 / 17 | 6 / 4 | 8 / 2 | 0.140 |

**What the own-genealogy null shows:**
- **The registered B is not too strict.**
  - On the six seeds with n ≥ 40 at both readings, the own-genealogy null's 95th percentile is ≥ B at every reading
    but one (seed 1 at 300: 29 against 32). At 599 it is far above B (e.g. 34 against 16, 28 against 14).
  - The arms' living are clustered into 2–4 planted clades (`ancestry.txt`), and the binomial B ignores that
    clustering. That makes the registered call *easier* to pass by drift, not harder.
  - Under no selection, the registered HELD fires on the arms' own genealogies in **2.4%** of replicates (47/2000,
    full operator), against the 1.5% measured on part 2's genealogies. Under mutation only it fires in 10.5%.
- **No seed was denied HELD by the bar.** Against its own null's 95th percentile at both readings, exactly one seed is
  above: 805, the same one.
- **805's HELD is genuine.** No replicate of 200 reaches its k_planted at either reading.

**The pre-launch "positive control" for HELD.** `prelaunch.py` (d) is the only per-arm HELD control. It showed that
HELD *can* fire when k_planted = n (every planted-rooted genome paying), at n = 20 and depths 2–40. That is
arithmetic reachability, not passability at a plausible s:
- at depth 2, B20 = 19, so it needs 20 of 20;
- it says nothing about whether mutation–selection at, say, s = 0.2 clears B at depth 10.

The design's power model (layer 1) is where passability was actually shown. A1's realised-n re-run (A6) confirms it
was adequate here. This is **not a defect in this readout**. For the programme, "shown passable" should mean a
modelled or simulated positive (k from a stated s), not k = n. **NOTE; SHOULD-FIX for future designs.**

**What this does to FALSIFIED: nothing.**
- The instrument could fire on 8 of 10 seeds, and did on one.
- The bar was, if anything, lenient.
- The one unreachable seed (4) is counted as LOST, not as NOT HELD. FALSIFIED allows up to 2 LOST.

## A2. Re-derivation and replicability — NONE

- `git diff 6dfa780 7557d23` is empty on `runs/RBT-112/readout.py`, `runs/RBT-106/readout.py`, `rabbitstew/`,
  `runs/RBT-106/held.py`, `runs/RBT-112/held.py`, `runs/RBT-104/peek.py` and `runs/RBT-112/baseline/`.
- `readout.py` at `7557d23` reproduces #372's `readout.txt` **byte for byte**. #372's `sensitivity.py` reproduces
  its `sensitivity.txt` byte for byte.
- **All 20 HZ `held-300/599.txt` regenerate byte for byte** from `ckpt/rbt-112-HZ-SEED` through `runs/RBT-112/held.py`.
  The S = 0 table path is named in each header.
- **Independent code** (`rederive.py`: own regexes, standard library only, no readout.py import) gives the same
  numbers (`rederive.txt`):
  - HELD HU 0, HZ 1; #LOST 1 (seed 4); COMPASS HU 0, HZ 5;
  - paired F +1.654 [+0.785, +2.523] patchy-scored, +0.468 [+0.290, +0.646] uniform-scored;
  - income +0.160 [+0.050, +0.271]; births +6.300 [−44.560, +57.160].
- **Not regenerated:** the function readouts (function.py's bouts) and `resting.txt` / `freeze.txt`. They were
  re-parsed, not re-run.
- **The full suite** at this branch's head, in the clean venv without scipy: **364 passed**.

## A3. The wording: "the operator is not the stall" — **MUST-FIX (wording)**

**What the registered sentence means.**
- §6.5 defines FALSIFIED as "the bias walk was not what stopped [selection holding the compass]... With the walk
  gone, selection still did not keep the compass above the operator's own residual erasure".
- §6.2 attaches a worded limit: "this also reads 'selection's advantage on the compass is below ~0.1 per
  generation'".
- §10.4 (F3) adds: "A change in s itself is not handled, and the wording says so."

**What the evidence supports:**
- **Supported: the bias walk is not what stops selection holding the compass in the population.**
  - With the walk gone, the planted-rooted carrier share tracks the S = 0 operator-alone table: HZ log-excess at
    599 is −0.487 [−1.410, +0.435]; the paired HZ − HU log-excess is −0.301 [−1.049, +0.448].
  - Against each arm's own-genealogy null, 9 of 10 seeds are unremarkable (A1).
  - The arms' own likelihood puts s in [0.00, 0.08] (A6).
- **Not supported: the plain-English "the operator does not matter".** The operator is what sets how much compass
  remains, and whether the best lines use it:
  - under the default operator, planted-rooted k_planted is 0 at 599 on every HU seed;
  - under S = 0 it sits at the operator-alone level (e.g. 801: 0.19 against μ 0.18);
  - champions carrying the paying planted unit: **HZ 31 of 70, HU 5 of 70**;
  - COMPASS lines: **HZ 5, HU 0**; paired F +1.654 [+0.785, +2.523].
- **So both registered lines are true, about different things.**
  - The structure question is registered as population frequency above the no-selection null. It reads that
    selection adds nothing measurable to what the operator leaves.
  - The function line reads that what the operator leaves is used.
  - READOUT.md §3 draws exactly this distinction, but only as "a reading". §1 then states the verdict with the bare
    registered phrase.
- **What READOUT.md §1 omits:**
  - §6.2's worded limit. §2 has "below ~0.1–0.15", but not beside the verdict.
  - F3's "a change in s itself is not handled". SE-Z *failed*: window income rose by +0.160. So the host changed,
    and s may differ from the default operator's s. That weakens any inference from HZ's s to "s under the default
    operator".

**The wording I would accept** (READOUT.md §1, replacing the paragraph under "The scored verdict is FALSIFIED"; the
verdict label and `readout.txt` unchanged):

> **FALSIFIED** (registered). With the designed body's global biases frozen (host and planted), selection did not
> hold the planted paying compass above what that operator alone leaves: 1 of 10 seeds held (805), against 0 of 10
> under the default operator, with planted roots alive on 9 of 10. **The bias walk is not what stops selection
> holding the compass in the population.** Selection's advantage on it is below ~0.1 per generation (the registered
> limit; the arms' own likelihood puts it at 0–0.08). With the global biases frozen the host also changed (SE-Z
> failed, income +0.160), so a change in s itself is not handled. **This does not say the operator is irrelevant:**
> under S = 0 the compass persists at the operator-alone level, and the income-best lines carry it and use it (5
> COMPASS lines against 0; champions carrying 31 of 70 against 5 of 70). Under the default operator they do neither.
> What the operator decides is how much compass is left for the best lines to use. What it does not decide is
> whether selection raises its frequency: it does not, under either operator.

I would also accept the verdict's gloss in one line: *"the operator is not the stall (selection is too weak, s <
~0.1, to hold the compass even against the reduced erasure); the operator does set whether the best lines keep and
use it."*

## A4. FUNCTION FOLLOWS: robustness — NONE

(`function_robust.txt`)
- **The COMPASS lines are 801, 4, 804, 805 and 1.**
  - The most marginal is 804: F [+0.121, +3.254], gain lower bound +0.147, decoy retains 10.6%. Its bodies are
    uneven (g400 +4.98, g550 +2.42, three below +0.4), but its t(6) call is registered.
  - The only near miss is 7: F [−0.052, +3.856], attribution UNRESOLVED.
  - Losing the two most marginal lines leaves **3**, still FOLLOWS. Gaining 7 gives 6.
  - No HU line has a primary F interval above 0.
- **The paired F is not driven by one or two seeds.**
  - Per seed, F(HZ) − F(HU) is positive on 9 of 10: sign test two-sided P = 0.022. The only negative is seed 3
    (−0.102).
  - Leaving out any one seed, the lower bound is +0.598 to +0.996.
  - Leaving out the worst pair (4 and 805), it is +1.446 [+0.372, +2.520].
  - Seed 1 is the largest single contribution (+4.174). Without it: +1.374 [+0.696, +2.052].
- **Attribution per line is the lesion, not the decoy.**
  - On every COMPASS line the decoy retains 13.8% or less of the gain (−2.4% to 13.8%).
  - The gain lower bounds are +0.147 to +2.448.
- **Seed 4's COMPASS line runs on crossover-carried compasses.**
  - Its champions carry the planted structure (7 of 7 in `resting.txt`, 3 paying), while the root rule counts 0
    planted-rooted living at 599 (A5).
  - Function and HELD score different genomes here, as RBT-106 h-adversary H3 found for HP-806. It does not affect
    either call.

## A5. Seed 4 LOST and seed 805 HELD — NONE

(`ancestry.txt`, from the restored arms, through RBT-106's `held.py` reader, unchanged)

**Seed 4 LOST is a genuine edge case of the registered root rule, not a parsing artefact.**
- At 300, only 1 of 60 living is planted-rooted along parents[0] (c0-2); at 599, none is.
- **All 36 (300) and 9 (599) bare-rooted pay32 hits have a planted founder in their ancestry.** The compass came in
  through crossover (the mate's global brain), which the registered rule (RBT-106 F3) excludes by design.
- Counted over all living, the share would be 36/60 at 300 and 9/60 at 599. At 599 that is below any B for n = 60
  at μ ≈ 0.16 (≈ 14), so seed 4 would not be HELD under the wider rule either.
- LOST = 1 is ≤ 2 either way, so FALSIFIED against FALSIFIED-ROOTS does not turn on it.
- READOUT §3 S3's description matches.

**805 HELD is genuine, and clade-driven.**
- Planted roots at 300: c0-16 28, c0-12 18, c0-26 9. At 599: c0-12 53, c0-16 7.
- k_planted 44/55 and 46/60 against B 27 and 16.
- Its own-genealogy null (A1) never reaches either count in 200 replicates. Clade collapse under drift does not
  explain it.
- It is one seed. The verdict counts ≤ 1, and the pooled own-genealogy false-positive rate (2.4% per seed) makes one
  chance HELD in ten plausible in general. 805's per-seed p (< 0.005) says this one is not chance.

## A6. Power at the usable n — SHOULD-FIX

**§2's anchors are the design's (part 2's genealogy, and n = 40), not the arms' realised n.** `instrument.txt` (2)
re-runs power.py's own model (its `q_seed`, `x_of`, `poibin`, imported unchanged) at each HZ arm's realised n and
mean depth:

| s | P(#HELD(HZ) ≤ 1), ρ 0 / 0.10 (fit) / 0.30 | E#HELD(HZ), ρ 0.10 |
|---|---|---|
| 0 | 1.000 / 0.971 / 0.904 | 0.28 |
| 0.089 | 0.320 / 0.380 / 0.431 | 1.95 |
| 0.12 | 0.038 / 0.160 / 0.263 | 2.84 |
| 0.15 | 0.002 / 0.056 / 0.151 | 3.66 |
| **0.20** | **0.000 / 0.008 / 0.054** | 4.82 |
| 0.25 | 0.000 / 0.001 / 0.019 | 5.67 |

**The arms' own likelihood of s** (`instrument.txt` (3)): the BetaBinomial log-likelihood of every observed
k_planted under x(d, s), with both seasons and ten seeds.
- At ρ 0.10: MLE s = 0.00, 95% profile interval [0.00, 0.03].
- At ρ 0.30: [0.00, 0.08].
- With ρ profiled: [0.00, 0.08]. The log-likelihood drops by 7.1 at s = 0.2.
- The arms fit ρ ≈ 0.3 better than the design's 0.10. The living are 2–4 clades; see A1.

**So:**
- "Strong evidence against s ≥ 0.2" holds, and more strongly than §2's "0.005–0.21". The upper end is M15's 0.214,
  which alone is a likelihood ratio of about 4.5 against s = 0, not "strong".
- "Weak evidence below s ≈ 0.12 (fires 0.13–0.70)" understates what the arms say: at realised n, s = 0.12 fires
  0.04–0.26.
- **Caveats, to be stated:**
  - Both figures are model-based: the mutation–selection recursion with u fixed at 0.089, and seasons treated as
    independent in the likelihood.
  - SE-Z failed, so this s is HZ's host's s.
  - A9: selection acting through clade expansion would not appear in k_planted/n at all.
- **Proposed:** add the realised-n row and the likelihood interval to §2 beside the design anchors. Cite §2's range
  at s = 0.2 as 0.000–0.054 (realised n) and 0.005 (n = 40), with M15 as the pessimistic model.

## A7. The sensitivity section — SHOULD-FIX (S2's sentence only)

- **Print-only, confirmed.**
  - `sensitivity.py` imports `readout.py` and `pool_xnull.py` through importlib and only prints. It writes no file
    and touches no scored path.
  - #372's diff adds only READOUT.md, `readout.txt`, `sensitivity.py` and `sensitivity.txt`.
  - Its header, and READOUT §3, label it POST HOC. The "reading" is labelled "not a finding".
- **S1** (31/70 against 5/70; paired +2.6 [+1.4, +3.8]) and **S3** (+0.167 [+0.001, +0.333]) re-derive.
- **S2 overstates.** It compares each arm's share with the part-2-genealogy null's 95th percentile. On 5 of 10 HZ
  seeds that threshold is useless:
  - 807 has no planted-rooted genome in part 2's genealogy (nan);
  - 4 is nan at 599;
  - 2, 3 and 7 have n = 3–7 there, so the 95th percentile at 300 is 1.000.
  - "1 of 10 above" is therefore at best 1 of 5 testable, and does not support "the verdict does not turn on how the
    null treats crossover".
- **The conclusion is nonetheless right.** The own-genealogy null with crossover (A1) is informative on all nine
  non-LOST seeds, and finds 805 alone above its 95th percentile at both readings.
- **Proposed:** cite `readout-adversary/ownnull_pool.txt` for that sentence, or drop it.

## A8. The power model's layer 3 assumed the wrong coupling — NOTE

`power.py` layer 3 gave a seed's champions carriers at p_held when the seed is HELD, and at 1/7 when it is not. So
P(COMPASS ≥ 3) was tiny unless HELD was common. The arms break that coupling:
- 5 COMPASS lines with 1 HELD;
- 31 of 70 carrying champions, against pooled population carrier shares of 0.35 at 300 and 0.17 at 599 over all
  living.

The champions are enriched for the compass, because it pays in income, without selection raising its frequency. That
is why Z-2 (FOLLOWS) was priced at 0.20. It is also the quantitative core of A3's wording: what the income-best
express and what the population holds are separate questions. This is for future designs, not a defect here.

## A9. Planted clades expanded under S = 0: a selection route HELD cannot see — NOTE

- **Planted-rooted n** (the denominator, not the test):
  - 300: HZ 390 of 600 living, HU 235, part 2's genealogy 235;
  - 599: HZ 386, HU 199, part 2's 242.
- **Paired HZ − HU:** +15.5 [−5.5, +36.5] at 300 and +18.7 [−9.4, +46.8] at 599. Not distinguishable from 0 at this
  n.
- If planted clades out-reproduce bare ones early, while the compass still pays, and are then eroded inside at the
  operator's rate, selection acts on the compass through n, and k_planted/n misses it.
- This is outside the registered question. It is not evidence for SUPPORTED; it is a caution against reading
  FALSIFIED as "selection never acts on the compass".

## Files

| file | what |
|---|---|
| `ADVERSARY.md` | this |
| `ownnull.sh` | every command behind the files below (restores, founders, the null, the probes) |
| `ownnull/ownnull-HZ-SEED.txt` | `null_xover_s0.py --global-bias-sigma 0` on each HZ arm's own genealogy, 200 replicates |
| `ownnull_pool.py` → `ownnull_pool.txt` | A1: the own-genealogy null against B and the observed k_planted |
| `instrument.py` → `instrument.txt` | A1 / A6: B/n per seed, power.py's model at realised n, the likelihood of s |
| `function_robust.py` → `function_robust.txt` | A4 |
| `ancestry.py` → `ancestry.txt` | A5 (and clade counts for A1 / A9), from the restored arms |
| `rederive.py` → `rederive.txt` | A2: independent stdlib re-derivation |

Every script is print-only and scores nothing.
