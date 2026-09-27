# RBT-117 registration: does the holistic fauna respond more strongly to selection than the designed body?

*Designer's registration, 2026-09-27, on branch `results/RBT-117-prereg` cut from **`bba7c3f`**, the integration head
before any RBT-113 arm data. **No RBT-113 arm output was opened:** no `runs/RBT-113/<ARM>/`, no `ckpt/rbt-113-*`. The
only material used is what the coordinator's ruling lists as pre-data: RBT-113's `pilot.txt`, `h2_committed.txt`,
`power.py`, `readout.py`, `world.py`, `decompose.py`, and the code. This registration is **additive**: it changes
nothing in RBT-113, whose registration, readout and verdicts stand as merged.*

**Status rule (the coordinator's ruling, RBT-117, about 16:55 UTC).** This is CONFIRMATORY only if it is reviewed,
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
  on every line, it fires with probability **0.47**. The registered rule fires with probability **0.00** in the same
  model (`power.txt`, "control" line; the modelled drift is `sim_arm`'s control slope `b_C` x 23, a smoothed
  version of `m_C(G−1) − m_C(0)`).

**What the control still guards.**
- It guards against a fauna difference big enough, without selection, to account for the claimed one; for example,
  if the selected lines' difference were mostly a drift that selection merely failed to stop.

**Registered rule.**
- VOID if the C-line difference is significant (sign-flip p < 0.05) **and** its mean is at least
  `CONTROL_FRACTION = 0.5` of the primary mean difference's size.
- Otherwise `c` is printed with its CI and p beside the verdict.
- Tests: a large significant `c` VOIDs; a small significant one and a large non-significant one do not.

**If the adversary or the coordinator prefers the literal rule,** it is one line in `decide`. The registration's
view is that it would turn an expected, harmless property of the operators into a VOID.

## 6. Scope sentences (fixed in code, printed under every verdict)

1. "This compares the two populations as built: body, controller topology and mutation operator all differ between
   them. It does not test the variability mechanism in isolation."
2. RBT-113's D2 disclaimers, verbatim, from `readout.DISCLAIMER_1` and `readout.DISCLAIMER_2`.
3. "The primary quantity is in raw net-yield units, the currency both faunas are scored in: a larger raw response
   can come from more phenotypic variation, more heritability or both; the sigma0-unit line beside it is the
   per-unit-of-variation reading and is not scored."

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
  (5 tests, about 45 s).
