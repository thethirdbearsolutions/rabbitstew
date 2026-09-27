# RBT-113 design adversary: PR #377 (`results/RBT-113-design` @ 087732e)

*Fresh design adversary, 2026-09-27. I rule on nothing; the coordinator rules. No arm was run. Nothing from RBT-107
was read. The probes are in this directory. They are throwaway and are not evidence about the benchmark: one
8-generation U/D/C triplet at seed 1 with the arms' own command line (`probe_lines.sh`), a food/work re-scoring of
that triplet (`decompose.py`), a controls-can-fail harness (`controls_can_fail.py`) and a resume test
(`test_probe_resume.py`). All ran against #377's tree.*

**Bottom line: LAUNCH AFTER FIXES.** The code is sound. I re-derived the byte identity, confirmed where the operator
reaches and checked resume on the one path the tests missed. The design is the right shape, the power is honest and
the timetable fits. Two things must be fixed before launch, and both are cheap. First, the readout cannot say
**what** responded: lineage records net yield only, and the probe shows the holistic down line responds almost
entirely through **work**. That split cannot be recovered per generation once the arms have run (D1). Second, the
headline sentence is not fixed in code, so a reader can take it as a statement about natural selection (D2). Neither
fix touches the arms' command line, and neither needs a new pre-launch run unless D1 is taken in its logging form.

---

## Verified (no finding)

- **Byte identity, re-derived.** I checked out `5d69581` and ran the test's two golden runs through the pre-hook
  `python -m rabbitstew.cli evolve` in a clean `.[dev]` venv with no scipy (x86_64, mujoco 3.14.0, numpy 2.4.6). All
  eight sha256 digests (`a/`, `b/` × config, lineage, history, state) equal `GOLDEN` in `tests/test_rbt113.py`. So the
  digests were genuinely recorded on the pre-hook code, and the hook's off path (flags absent, `--truncation 0`,
  `--truncation 0 --line down`) writes those bytes.
- **§3 mechanics match the code.** `truncation_pool` returns the top k (`ranked()`: stable sort, ties by index), the
  bottom k (ties by index), or k drawn without replacement from the fauna's own stream. Both the parent and the
  crossover partner (p = 0.5) are drawn uniformly from the pool. Elites, survival, archive and morph protection are
  refused. The pool is drawn once per generation, before the child loop.
  - Ties by index in the up line (many holistic founders sit at exactly 0) are not a hidden bias: a child's index is
    independent of its genotype, because its parent is a uniform draw from the pool. So a tie-break by index is a
    random tie-break.
- **`--global-bias-sigma 0` does not reach the holistic fauna.** The holistic `genetics.mutate` calls
  `mutate_weights(g, rng, config)` without `global_bias_sigma`. The parameter reaches only `mutate_controller` (the
  designed body). `mutate_brain` is reached only under morph protection, which truncation refuses. The claim is
  right.
- **Worlds are shared.** Start seeds and terrain come from the TERRAIN stream (`draw_start_seeds(cfg,
  self.rngs[TERRAIN])`). The control line's extra `rng.choice` and the lines' different mutation draws are on the
  population streams, so they cannot move the worlds.
- **Resume on the path the tests missed.** The resume test covers the down line, but the control line is the only
  line whose pool consumes the population stream. `test_probe_resume.py` resumes a control line, plain and under
  Z + salt 1: `lineage.jsonl`, `state.json` and `history.json` are byte-identical to an uninterrupted run (2 passed).
- **Suite:** 364 passed on `5d69581` in a clean `.[dev]` venv with no scipy. The coordinator's trial merge of #377
  gave 386 (364 + 22).

## Findings

### D1 — MUST-FIX. The readout cannot say whether food or work responded, and the down line is a work response

The trait is `food − 0.03 × kJ`, and lineage records only that net. The pilot already shows that in holistic
founders the net itself is **not** shown heritable (slope −0.06 [−2.5, +1.1]); food is not either (+0.39 [−0.18,
+0.95]); work is (+1.04). The design's answer is "report b_up and b_down separately". That separates the lines, not
the two currencies.

The probe (`decompose.txt`) re-scored founders and each line's last generation (8 generations, seed 1, N = 40, 4
fixed draws):

| holistic | food (items) | work (yield units) | net |
|---|---|---|---|
| founders | 0.050 | 0.025 | +0.025 |
| U, gen 7 | **0.781** | 0.257 | +0.524 |
| D, gen 7 | 0.056 | **0.296** | −0.240 |
| C, gen 7 | 0.038 | 0.006 (95% at zero work) | +0.031 |

- **Reassuring.** At N = 40 the holistic **up** line does not stall at "stand still". It learns to eat, and its
  food rises 20-fold. The pre-launch smoke's stall (§10.5) was an artefact of N = 12.
- **The catch.** The down response (C − D) is **entirely work**, flailing: D's food equals C's. In the designed
  body, D stops eating (food 0.14 against C's 0.92), so there the down response is mostly food. U − D at gen 7 is
  mostly food in the holistic fauna (+0.72 items against +0.04 of work), but that depends on the generation and the
  seed.
- **The control drifts to stillness.** C collapsed from 40% to 95% zero-work bodies. `b_C` will show it as mutational
  bias, but it also means U − C partly measures "not becoming still".

Without the split, a holistic RESPONDS with a large `b_down` reads as "the simulator is evolvable" when half of it is
"selection can make bodies burn more energy". That is a true response, but it is not what the funder's "holistic
evolution working" means. It is also the half that an operator or world tweak could inflate without improving
foraging at all.

**Why before launch.** Genomes are not saved per generation, so the per-generation split cannot be recovered
afterwards. The last generation (`final/`) and the founders can be recovered. `final/` stays on the checkpoint branch.

**Fix (the designer picks one; both keep the arms' command line):**
- **(a) Minimum, no change to `rabbitstew/`.**
  - Pre-register an endpoint decomposition script now, like `decompose.py`: founders plus each line's `final/`, both
    faunas, on fixed draws.
  - The readout step runs it on the `final/` populations restored from `ckpt/rbt-113-*`, and RUNNER.md says so.
  - Report per unit, with t CIs: the U − D, U − C and C − D differences at generation 23 in food and in work.
  - The headline must state the food share of the divergence and of each one-sided response.
  - `final/` is already written and saved (run_arm.sh requires `holistic/final`).
- **(b) Better, a small code change.** When `truncation` is on, log `food` and `work` per member in `lineage.jsonl`.
  - Gating it on truncation keeps every default byte identical, and the golden test still guards that.
  - Add `b_div_food`, `b_div_work`, `b_up_food`, `b_down_work` and so on to `arm_stats`.
  - This needs a test and a new `prelaunch.txt`, because the `rabbitstew` tree changes. Estimate: 30–45 minutes.

If the timetable is tight, take (a). A per-generation split is a nice-to-have. An endpoint split is not optional.

### D2 — MUST-FIX. Fix the headline sentence and the asymmetry in code, with the framing inside it

§6 says the headline is "the holistic `b_div` and `h2` with CIs, with the asymmetry stated". But `readout.py` prints
`RESPONDS: divergence X sigma0/generation [..], realised h2 Y [..]`, with no one-sided responses, no framing, and the
label "holistic (both operators…)".

Several pieces of text, each true, add up to a misreading:
- the funder's question is "holistic evolution working";
- the designer's comment calls this "its headline figure";
- §1 says solo yield "is the quantity natural selection acts on in the ecology (so the benchmark measures the currency
  the programme cares about)".

Together they invite a reader to take "h2 = Y" as a statement about the ecology's natural selection. They also invite
a comparison of Y with paper 5's 0.34–0.51, which is a parent–offspring r of lifetime yield in the ecology: a
different statistic, population and regime.

**Fix.** `readout.py` prints one fixed headline sentence per fauna:
- **What was imposed:** "Under imposed truncation selection (top / bottom / random 10 of 40, discrete generations,
  solo scoring, 24 generations from random founders, paper 5's world), …".
- **The numbers:** `b_div` and `h2`, each with its CI, **and** `b_up` and `b_down`, each with its CI, and the D1
  food/work shares.
- **Two fixed disclaimers:** "this is the response to imposed selection in this design; it is not a measurement of
  natural selection in the ecology (paper 5 §2–§4)", and "realised h2 of this design only; not comparable with paper
  5's parent–offspring r".

In §1, soften "so the benchmark measures the currency the programme cares about" to "so the benchmark selects on the
same currency the ecology rewards".

§8's interpretation paragraph is good. Move it into the headline, because that is the only part that travels.

### D3 — SHOULD-FIX. Two controls cannot fail on the failures they exist for

The programme rule asks that controls be shown passable. They should also be able to fail, and #377 shows them
passing only. `controls_can_fail.txt` corrupts a real 8-generation arm one way at a time and runs the readout's own
`controls()` plus its manipulation check. Eight of ten corruptions are caught:
- a U parent swapped for the worst member;
- a D parent swapped for the best;
- C bred from everyone;
- the wrong line in the config;
- the wrong operator;
- generation 0 differing between lines;
- a missing generation;
- U and D replaced by C.

The last of these is caught by control 3, not control 4. Two are **not** caught:
- **A "control" that secretly selects** (C bred from the top k every generation) passes. Nothing checks that C is
  unselected: its realised differential `S_C` is printed but never tested. Fix: a readout check that the CI across
  units of mean `S_C` covers 0, or that `|S_C| < 0.25 × (S_U − S_D)` on average. Add a test that feeds the readout a
  selected C.
- **Worlds that differ between lines after generation 0** are not checked. The readout reads no `history.json`, yet
  §4.1 and control 2 claim that every generation's worlds are shared. Fix: compare `start_seeds` and `terrain_seed`
  per generation across U, D and C, and across the default and Z arms at a seed. `history.json` is already committed.

Also add the probe's corruptions as a unit test, so that "can fail" is part of the suite.

### D4 — SHOULD-FIX. σ0 is a per-benchmark scale; freeze it, and print raw units

The median over arms of generation-0 SDs is robust enough within this benchmark: 24 holistic and 12 designed-body
values. With an even count, the median is the mean of the two middle values. But the ticket's use is **later**
comparisons. A world tweak changes the founders' SD, so a re-run would re-scale itself, and "σ0 per generation" would
not be comparable across benchmarks. The holistic σ0 is also set by how many founders happen to eat: one item is 0.5
yield at D = 2, against a work term of about 0.03.

**Fix:**
- Print `b_div` in raw yield units (items per generation) beside the σ0 value.
- Record this benchmark's σ0 per fauna as the frozen constant that any later benchmark reports against, alongside
  that benchmark's own σ0.

The verdicts do not depend on σ0, apart from `MDE_DIV` and `EQUIV_OP`.

### D5 — NOTE. The null is one the simulator never meets, so RESPONDS is near-certain; say so

The null (h2 = 0 and V_m = 0) is honest as a test of the statistics. But `power.txt` shows that V_m = 0.01 alone
gives P(RESPONDS) = 1.00, and every real mutation operator has V_m > 0. So RESPONDS is the expected verdict and not the
finding. The finding is the magnitude, its asymmetry and its food/work split (D1).

§5.3 half-says this ("mutational input is itself heritable variance"). The headline should say it plainly, so that no
one reads "RESPONDS, p < 0.001" as the achievement. NO RESPONSE is practically unreachable. That is fine, but say so.

**The power model is not the risk.** The `floor` variant censors the wrong side (its docstring admits it), and the
holistic trait is zero-inflated. Neither matters much, because the probe's effect sizes are many times the powered
ones. For the same reason, the `floor` rows are not evidence that the holistic trait is well modelled.

### D6 — NOTE. h2 and exhaustion are worded correctly; keep it that way in the headline

- §5.3 says the realised h2 reads 0.3–0.5 of the founders' h2 in the model (drift, Bulmer), and that it is compared
  across operators only at this design. That is correct.
- In the real system, mutation replenishes variance, so the realised h2 over 24 generations mixes standing and new
  variance. It is an index of this design, not an estimate of a heritability. D2's fixed sentence carries this.
- The cumulative differential is offspring-weighted. That is the right choice (§10.1): it is what the parents actually
  contributed, and the round-trip test pins it.

### D7 — NOTE. The operator comparison is honestly weak, and it is designed-body only

- §5.3 states 0.53 power at Δh2 = 0.2 and calls INCONCLUSIVE the expected outcome. That is honest.
- **The operator number is on the designed body only.** RBT-112's operator does not reach the holistic fauna, so the
  funder-facing fauna gets no before-and-after number from this benchmark. §4.3 says so; keep it next to the headline.
- **Pairing is real but shallow.** Founders and worlds are shared (checked on generation 0 by the readout, and worlds
  per generation by D3's fix). Mutation draws diverge after generation 0.

### D8 — NOTE. Pairing and replication are correct; make VOID per fauna

- **Unit of replication.** The seed is the right unit for the holistic fauna. The salt-0 and salt-1 replicates share
  worlds through the TERRAIN stream, so averaging them is correct and conservative.
- **If a session is lost,** a seed's holistic unit falls to one replicate: a noisier unit, not a biased one.
- **VOID is global.** A designed-body operator-pairing failure voids the holistic headline too. Suggest VOID per
  fauna and per comparison. That is optional, and the current rule is conservative.

### D9 — NOTE. Cost and timetable fit, with less margin than stated

- **Measured per generation.** The probe took 15.5 s per generation at N = 40, D = 2 and 4 workers alone (U 129 s,
  D 120 s, C 121 s for 8 generations; `probe_lines.log`), against the 12.6 s in §9.
- **Per arm.** Two arms side by side at WORKERS=2 give about 31 s per generation, and 216 generations give about
  **1.9 h per arm**, inside the 2.25 h budget.
- **Timetable.**
  - Arms launched by about 16:45–17:00 finish by about 18:50–19:15.
  - The readout by about 20:30 holds.
  - D1(a) adds a few minutes of re-scoring: 3 lines × 2 faunas × 40 genomes × 4 draws per seed directory, about
    1 minute each on 4 cores, so about 25 minutes for all 24 seed directories. Budget it into the readout slot.
- **Other checks.**
  - RUNNER.md, `run_arm.sh`, durable checkpointing, and the 38-file list per arm plus `resumes.txt` are coherent.
  - The resume path is re-checked above.
  - **Terminology.** `run_arm.sh` calls O1 (3 seeds) an "arm", while `readout.py` and §5.1 call one seed directory an
    "arm". The readout glob in RUNNER.md is correct, but make the vocabulary consistent before the readout adversary
    trips on it.

### D10 — NOTE. Minor corrections

- **Units.** `pilot.txt`'s `work_kJ` column is in **J** (`sim.work`; `food_score` divides by 1000). So §1's "median
  work is 4 kJ" is 4 J. The rejection of distance per kJ stands, since the tenth percentile is still 0.
- **`--line` is silently ignored without `--truncation`.** It is harmless and the byte test covers it. A warning would
  be kinder.
- **Correlated responses** are computed per arm, not per seed, for the holistic fauna, so the two salted replicates
  are counted as independent in a CI. They are descriptive only, but average per seed as the main table does.

## Summary for the ruling

| # | severity | one line |
|---|---|---|
| D1 | MUST-FIX | pre-register a food/work split (endpoint from `final/`, or per-generation logging); the holistic down response is flailing |
| D2 | MUST-FIX | fix the headline sentence in `readout.py`: imposed truncation, not natural selection; b_up and b_down with CIs; h2 not comparable with paper 5 |
| D3 | SHOULD-FIX | a selected control and mismatched worlds pass the controls; add both checks and a can-fail test |
| D4 | SHOULD-FIX | print raw units and freeze σ0 for future comparisons |
| D5 | NOTE | RESPONDS is near-certain under any V_m > 0; the finding is magnitude and composition |
| D6 | NOTE | h2 is a design index; the wording is right |
| D7 | NOTE | operator comparison: weak and designed-body only, stated honestly |
| D8 | NOTE | seed as the unit is right; VOID could be per fauna |
| D9 | NOTE | 15.5 s per generation measured, about 1.9 h per arm; fits |
| D10 | NOTE | units (J, not kJ), a `--line` warning, correlated responses per seed |

**LAUNCH AFTER FIXES**: D1 (either form) and D2. D3 and D4 are cheap and are best done in the same pass.
