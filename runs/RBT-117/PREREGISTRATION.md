# RBT-117 registration: does the holistic fauna respond more strongly to selection than the designed body?

*Designer's registration, 2026-09-27, on branch `results/RBT-117-prereg` cut from **`bba7c3f`**, the integration head
before any RBT-113 arm data. **No RBT-113 arm output was opened:** no `runs/RBT-113/<ARM>/`, no `ckpt/rbt-113-*`. The
only material used is what the coordinator's ruling lists as pre-data: RBT-113's `pilot.txt`, `h2_committed.txt`,
`power.py`, `readout.py`, `world.py`, `decompose.py`, and the code. This registration is **additive**: it changes
nothing in RBT-113, whose registration, readout and verdicts stand as merged.*

**Amended before any arm was read, per the coordinator's ruling on the design adversary (PR #390,
`runs/RBT-117/design-adversary/ADVERSARY.md`, REGISTER AFTER FIXES): M1, M2, S1–S3, N2, N4, N7. In-place markers
read "[amended]".**

**Status rule (the coordinator's ruling, RBT-117, about 16:36 UTC [amended: N7]).** This is CONFIRMATORY only if it is reviewed,
ruled and merged before RBT-113's readout is run (about 19:00). Otherwise it falls back automatically to
EXPLORATORY: the same `compare.py` is run with `--post-hoc`, every verdict line says "EXPLORATORY, post hoc", and it
enters no verdict. RBT-113's readout never waits for this.

**The question** (the 2005 proposal's reason (b); `docs/origins/`): a more variable population should respond more
strongly to selection. RBT-113 already runs both faunas at matched settings: every default-operator seed directory
holds a holistic and a designed-body U, D and C line, with the same seeds, the same worlds every generation, and the
same design (N = 40, k = 10, G = 24). RBT-113 reports the faunas separately and compares them nowhere. This
registration fixes that comparison before the data.

---

## 1. Arms and pairing

- **RBT-113's default-operator seed directories only:** `O1/1..3`, `O2/4..6`, `O3/7..9`, `O4/10..12`, 12 seeds.
- **Paired by seed.** Within a seed directory the two faunas are evaluated in one `Experiment`, on the same
  generation's terrain and start seeds (`evolution.py:706`, `evaluate(pop, …, terrain_seed, start_seeds)` for both
  kinds). The seed is the unit.
- **The Z directories are excluded.** RBT-112's operator reaches only the designed body, and the Z directories'
  holistic lines are salted replicates. A Z directory is therefore not a matched pair, and `compare.py` refuses one.
- **If a session was lost,** the comparison runs on the seeds present and prints n. The power in §4 is for 12.
- [amended: M2] **The seed set is checked; `compare.py` exits non-zero on:**
  - a repeated seed;
  - a seed outside 1..12;
  - a seed directory not under the O arm that RUNNER §1 assigns to its seed (O1: 1–3, O2: 4–6, O3: 7–9, O4: 10–12).
  A `WARNING` line names any missing seeds. At n ≤ 5 it prints that no directional verdict is attainable: the exact
  test's smallest p is then 2/2^n ≥ 0.0625. Each case has a test.

## 2. The quantity, and why raw units are primary

**Confirmed against the code: both faunas' fitness is in one raw currency.**
- `Experiment.run` evaluates both populations with one `EvolutionConfig` (`evolution.py:706`).
- `evaluate` builds a single `SimConfig` per generation, `generation_sim(config, terrain_seed, generation)`
  (`evolution.py:286`), and a solo evaluation's fitness is `run_solo`'s `sim.score`. Under `--score food` that is
  `food_score` (`simulation.py:527`): `food_eaten x value − work_cost x work / 1000`, with nothing fauna-specific in it.
- `world.py` gives one `WORLD` flag list for the whole run, and `readout.py` reads both faunas' `fitness` from the
  same `lineage.jsonl` field.
- A test pins it: `test_both_faunas_are_scored_in_one_raw_currency` re-scores a member of each fauna with `run_solo`
  under the generation's `SimConfig` and draws, and recovers its lineage fitness.

So the coordinator's reading holds, and **raw units are primary**, as ruled.

- **Primary quantity**, per seed s:
  `d(s) = D_holistic(s) − D_designed(s)`, with `D_f(s) = m_U(G−1) − m_D(G−1)`.
  This is the final-generation up-minus-down divergence in raw net yield, where `m` is RBT-113's line mean
  (`readout.line_series`).
- **Why raw is the right reading of the claim.** "A more variable population responds more strongly" is a claim
  about the total response, about h²·i·σ_P, in which the variation is part of the mechanism. Scaling by σ0 would
  divide the premise out.
- **Secondary**, printed and not scored:
  - the same d in σ0 units, each fauna's D over its own σ0 (RBT-113's pooled median generation-0 SD, over these 12
    directories), which is the per-unit-of-variation reading;
  - the differences in RBT-113's `b_div` (σ0 units) and realised h2.

**Prediction, stated before any data, from the pilot.** On this trait the premise runs the other way at founding.
The designed body's founders are about **5× more variable** in yield than the holistic founders: SD 0.709 against
0.136 at D = 2 (`pilot.txt`). The holistic founders are zero-inflated non-foragers. In RBT-113's power model the
raw comparison therefore predicts **DESIGNED RESPONDS MORE** at every holistic h2 tried, from 0.05 to 0.8
(`power.txt`). A holistic win in raw units would need its lines to escape the model, for example by discovering
eating, a new mode, and so growing their own variance. That is a live possibility for a zero-inflated trait, and
it is exactly what the test can detect.

## 3. The test and the verdict (fixed in `compare.py`)

- **Test:** exact two-sided sign-flip permutation on the 12 paired `d(s)`, all 2^12 = 4096 patterns
  (`readout.sign_flip_p`, no scipy); α = 0.05.
- **Verdict, three-valued:**
  - **HOLISTIC RESPONDS MORE** if p < 0.05 and mean d > 0;
  - **DESIGNED RESPONDS MORE** if p < 0.05 and mean d < 0;
  - **NOT DECIDED** otherwise.
- **VOID** overrides all three:
  - if any RBT-113 control fails in any default-operator seed directory, for either fauna. `compare.py` re-runs
    RBT-113's own `controls` and `selection_checks`;
  - or if the C-line control fails (§5).
- **Mean and CI printed:** the t CI of mean d, RBT-113's `ci_text`, beside the p.
- [amended: N2] **The null is symmetry, not mean = 0.** The sign-flip test assumes d(s) symmetric about 0 under H0
  (the fauna labels exchangeable within a seed), with independent seeds. It holds its level under a symmetric null:
  0.052 over 20,000 draws, in the adversary's probe. Under the zero-inflated "escape" scenario §2 names as live
  (holistic D = +3 in a Binomial(12, 1/6) number of seeds, otherwise 0, so E[d] = 0), the level is 0.072, and the
  false DESIGNED RESPONDS MORE rate is 0.063 against a nominal 0.025. The excess runs against the holistic side.
- [amended: S1] **The two halves are printed beside d, raw and not scored:** each fauna's final-generation U − C
  (up) and C − D (down), with t CIs.

## 4. Power and MDE (pre-data only; `power.py` → `power.txt`)

**Model.**
- RBT-113's `sim_arm` for each fauna, run in phenotypic-SD units and scaled to raw by the pilot's founder SD.
- The designed body's h2 is the pilot's 0.43.
- The holistic founders' h2 is **not identified** by the pilot (slope −0.06 [−2.5, +1.1]), so it is swept over
  0.05, 0.2, 0.43 and 0.8, with and without mutational variance.
- RBT-113's committed ecology estimates (`h2_committed.txt`, r 0.34–0.40) are of a different quantity (lifetime yield
  in the ecology, parent-offspring r) and are not used as h2.

**Results.**
- **Per-seed SD of d:** 0.79–0.88 raw yield units across the eight scenarios.
- **MDE at 80% power**, holistic larger: **0.76–0.83 raw yield units** of mean d (power at the MDE 0.80–0.86). That
  is close to one item of food per season in the final-generation divergence, or about 6 holistic founder SDs.
- **Null** (both faunas the same model): P(either directional verdict) = 0.067 over 300 draws (SE about 0.014). The
  exact sign-flip test is level 0.05 by construction when d is symmetric about 0; an earlier 30-draw run of the same
  script read 0.033.
- **At the modelled means**, the test returns DESIGNED RESPONDS MORE with probability 1.00 in every row; see §2's
  prediction.

**Shown passable** (a simulated positive at a stated effect): `test_verdict_rule_detects_simulated_positives_and_holds_the_null`.
- A mean difference of +0.9 raw, with per-seed SD 0.8 (the power table's scale), gives HOLISTIC RESPONDS MORE.
- −0.9 gives DESIGNED RESPONDS MORE.
- A centred null gives NOT DECIDED.
- All 12 seeds positive gives p = 2/4096.

The end-to-end test runs `compare.py` on tiny real seed directories.

## 5. The control: the unselected lines, and an argued change to the rule

**The statistic.**
- `c(s) = C_holistic(s) − C_designed(s)`, with `C_f(s) = m_C(G−1) − m_C(0)`: the unselected control lines' drift over
  the run, holistic minus designed, in raw units, tested the same way.

**Why the literal rule "VOID if it differs" is not registered.**
- The C lines carry each fauna's own **mutational bias**: the tendency of mutation alone to move yield. The two faunas
  have different operators (holistic `mutate`, designed `mutate_controller`) on different bodies, so their biases
  are expected to differ.
- In raw units, even an equal bias in SD units differs by the 5× SD ratio.
- Such a bias acts on U and D alike within a fauna, so it **cancels in `D_f = m_U − m_D`**. A C-line difference is
  therefore not, by itself, a threat to the primary quantity.
- **The literal rule would VOID a valid comparison.** In RBT-113's power model, with its −0.02 σ0-per-generation bias
  on every line, it fires with probability **0.47** (the adversary: 0.41–0.49). The modelled drift is `sim_arm`'s
  control slope `b_C` × 23, a smoothed version of `m_C(G−1) − m_C(0)`.

**What the control still guards.**
- It guards against a fauna difference big enough, without selection, to account for the claimed one; for example,
  if the selected lines' difference were mostly a drift that selection merely failed to stop.

**Registered rule [amended: M1].**
- VOID **iff** the C-line difference is significant (sign-flip p < 0.05) **and** `|mean c| ≥ C_BOUND = 0.8` raw.
  That is a **fixed** bar: the registered MDE, and about 3× the modelled bias difference.
- Otherwise `c` is printed with its CI and p beside the verdict.
- Tests: significant at 0.85 VOIDs, and does so whatever d is; significant at 0.75 does not; beyond the bound but
  not significant does not.

**Why fixed.** The first draft keyed the bar to the observed primary (0.5 × |mean d|). The design adversary showed
that this rule:
- false-VOIDs about 35% of outcomes near parity, on the model's harmless bias;
- false-VOIDs 13.5% of true holistic wins at the MDE;
- misses a gross fault (+1.0 raw of C drift) 82% of the time at the predicted d.

A fixed 0.8 has a false-VOID rate of 0.000 at every d tried and catches that fault every time (the adversary's
`probe_stats_fixed08.txt`). `power.txt`'s "M1" lines give this rule's false-VOID rate across d in RBT-117's own
model: **0.000 at mean d = −2.8, −0.4, 0, +0.4 and +0.8**. The HOLISTIC RESPONDS MORE rate is 0.877 at +0.8, the
MDE, so the 80% power claim stands under the fixed rule.

## 6. Scope sentences (fixed in code, printed under every verdict)

1. "This compares the two populations as built: body, controller topology and mutation operator all differ between
   them. It does not test the variability mechanism in isolation."
2. RBT-113's D2 disclaimers, verbatim, from `readout.DISCLAIMER_1` and `readout.DISCLAIMER_2`.
3. [amended: S1] "The primary quantity is in raw net-yield units, the currency both faunas are scored in: a larger
   raw response can come from more phenotypic variation, more heritability or both, or from the down line's room to
   lose yield by working harder, which differs between the bodies; the sigma0-unit line beside it is the
   per-unit-of-variation reading and is not scored."
4. [amended: S2] The premise check, with the observed founder σ0 of each fauna filled in: "Founder sigma0 here:
   holistic X, designed Y. Reason (b)'s premise, that the holistic population is the more variable, holds / does not
   hold on this trait; a designed win is not by itself evidence against the mechanism." On this trait the pilot
   predicts "does not hold" (§2). DESIGNED RESPONDS MORE is then what the mechanism itself predicts. It refutes a
   holistic advantage via reason (b) on this trait, not the mechanism.

[amended: N4] `compare.txt` also prints that its σ0 is the median over the 12 default directories only. It
therefore differs from `readout.txt`'s σ0, which also pools the Z directories.

## 7. Food against work (D1), descriptive only

`compare.py` reads each seed directory's `decompose.json`, written by RBT-113's readout step 2. It prints per fauna
the U − D contrast in food and in work at the final generation, with t CIs, and the food share
(`readout.food_share`). If the file is missing, it says so rather than dropping the line.

A holistic response that is mostly work (flailing) is not the proposal's "general, adaptable strategies". The
decomposition is how a reader tells. It is not a score and does not enter the verdict.

## 8. Order at readout

1. RBT-113's readout runs first, per its RUNNER §6: restore, `decompose.py`, then `readout.py`.
2. Then:
   `python runs/RBT-117/compare.py runs/RBT-113/O[1-4]/[0-9]* > runs/RBT-117/compare.txt`,
   with `--post-hoc` if RBT-117 was not merged before RBT-113's readout was run.
3. `compare.txt` is committed with RBT-113's readout, and RBT-113's readout adversary reviews it alongside.

## 9. Side effects

- None on RBT-113: no file under `runs/RBT-113/` or `rabbitstew/` changes.
- `compare.py` imports RBT-113's `readout.py` and uses its functions as they are.
- New files: `runs/RBT-117/{PREREGISTRATION.md, compare.py, power.py, power.txt}` and `tests/test_rbt117.py`
  (7 tests, about 75 s).
- [amended: S3] The adversary's planted-positive probe is now a test,
  `test_a_planted_positive_through_main_in_both_directions`. It plants +5 raw in one fauna's U line at the final
  generation, over 6 seeds, runs `main()`, and gets HOLISTIC RESPONDS MORE or DESIGNED RESPONDS MORE as planted, with
  RBT-113's controls passing.
