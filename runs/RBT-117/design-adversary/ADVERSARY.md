# RBT-117 design adversary

*The design adversary's review of PR #385 (`results/RBT-117-prereg` @ `0b411ea8`, based on `bba7c3f`), 2026-09-27, about
17:10 UTC. Branch `results/RBT-117-design-adversary`, cut from the PR head.*

**No-peek.** No `runs/RBT-113/O*/`, `runs/RBT-113/Z*/` or `ckpt/rbt-113-*` was opened; the checkout has none. Every probe
uses synthetic data, or the committed pre-data files: `pilot.txt`, RBT-113's `power.py` model, and the code.

## Overall call: **REGISTER AFTER FIXES**

The design is sound where it matters most:
- the raw units are genuinely identical across faunas;
- the paired, exact sign-flip test is valid and holds its level;
- σ0 cannot reach the verdict;
- the scored path, run end to end on a planted positive, returns the right verdict in both directions;
- the prediction that DESIGNED RESPONDS MORE is the likely outcome is stated honestly and before the data.

Two things must change before it is registered:
- **M1, the C-line VOID rule.** It is keyed to the observed primary, so it VOIDs about a third of outcomes near
  parity on a harmless, modelled bias, and it misses a gross fault 82% of the time at the predicted outcome.
- **M2, the seed set.** `compare.py` silently accepts a duplicated or foreign seed directory.

Both are small code changes with tests. Neither needs any data.

---

## MUST-FIX

### M1. The C-line VOID threshold is a fraction of the *observed* primary. It false-VOIDs near parity and misses faults where the verdict is predicted to land.

**What's registered.** `decide` VOIDs if `p_c < 0.05` **and** `|mean c| ≥ 0.5 × |mean d|`. The threshold is therefore
not fixed before the data: it moves with d.

**Where `power.txt` measured it, and where it didn't.** `power.txt` reports P(VOID) = 0.000 only at the modelled
d ≈ −2.8, where the bar is about 1.4 raw and nothing crosses it. The false-VOID rate at any other d is not stated.

**Probe** (`probe_stats.py` §C, `probe_stats_fixed08.txt`). c is drawn from RBT-113's own model, exactly as RBT-117's
`power.py` draws it: `sim_arm` with the −0.02 σ0/generation bias, scaled by the pilot's founder SDs. The drift that
model gives is harmless by the registration's own argument, since it cancels in U − D. Per seed, c has mean +0.23
raw and SD 0.46, and it is significant in 41% of 12-seed draws.

| true mean d (raw) | registered: P(VOID) | P(HOL) | fixed 0.8 raw: P(VOID) | P(HOL) |
|---|---|---|---|---|
| −2.80 (the model's prediction) | 0.000 | 0.000 | 0.000 | 0.000 |
| −0.40 | 0.330 | 0.000 | 0.000 | 0.000 |
| 0.00 | **0.350** | 0.020 | 0.000 | 0.030 |
| +0.40 | **0.355** | 0.263 | 0.000 | 0.340 |
| +0.80 (≈ MDE) | **0.135** | 0.757 | 0.000 | 0.848 |

**What this shows.**
- The registered rule VOIDs about 35% of runs near parity, and 13.5% of true holistic wins at the MDE, on a bias the
  registration argues is harmless. So the 80% power claimed at the MDE is really about 76% (0.757).
- It is also weak where it should bite. A gross fault (the holistic C line drifting a further +1.0 raw, as a selected
  control would; §D) is caught only **18%** of the time at the predicted d = −2.8, because the bar has risen to 1.4.
- The registration's rationale undercuts its own rule. If a fauna-specific drift cancels in U − D (§5), then c's size
  *relative to d* measures nothing that threatens d. The rule does work only as a gross-fault detector, and a
  gross-fault detector needs a fixed bar.

**Fix.**
- VOID if `p_c < 0.05` **and** `|mean c| ≥ C_BOUND`, with `C_BOUND = 0.8` raw fixed now. That is the registered MDE
  (0.76–0.83), and about 3× the modelled bias difference.
- In the same model this bound gives **P(false VOID) = 0.000 at every d tried**, and catches the +1.0 fault **100%**
  of the time at d = −2.8, 0 and +0.8.
- Add one `power.txt` line with the false-VOID rate across d, and a test for each side of the bound.

For the coordinator: the literal rule ("VOID if the C lines differ") fires 41–49% of the time in this model. That
agrees with the designer's 0.47, and I agree the literal rule should not be registered.

(`probe_stats_fixed04.txt` is the same probe at a 0.4 bound, which sits too close to the modelled bias: it
false-VOIDs 15–21% at every d. So the bound has to clear the bias; 0.8 does.)

### M2. `compare.py` does not check the seed set: a duplicate, or a foreign directory, is counted silently.

Probe (`probe_pipeline.py`, `probe_pipeline.txt`), on toy seed directories:
- **2a.** The same seed directory passed twice runs as "7 paired seeds", exit 0. That is pseudo-replication; it also
  moves the exact p.
- **2c.** A seed `13` under an arm named `O9` is accepted into the comparison, exit 0. Only a leading `Z` is checked.
- **2b.** Five seeds run silently to NOT DECIDED. At n ≤ 5 the exact test's smallest attainable p is 2/32 = 0.0625,
  so no directional verdict is possible at all, and nothing says so.

**Fix.**
- Refuse with a non-zero exit if a seed repeats; if a seed falls outside 1..12; or if a directory's parent is not the
  O arm that RUNNER §1 assigns to its seed (O1: 1–3, O2: 4–6, O3: 7–9, O4: 10–12).
- If fewer than 12 seeds are present, print the missing seeds on a `WARNING` line (the registration allows lost
  seeds). If n ≤ 5, also print that no directional verdict is attainable.
- A test for each.

---

## SHOULD-FIX

### S1. U − D in raw units includes the downward line's capacity to *waste* work, which is a body difference that scope sentence 3 does not name.

**Evidence** (`pilot.txt`):
- The designed founders do about 15× the actuator work of the holistic founders: work 19 053 J against 1 259 J, which
  costs 0.57 against 0.04 yield units.
- The holistic trait is zero-inflated: 62% of founders have |yield| ≤ 0.001.
- So the designed D line can lose raw yield fast by working harder, while a holistic D line starts near a floor. A
  DESIGNED RESPONDS MORE verdict can therefore come largely from downward selection on work. That is neither
  foraging nor variability.

**What already covers it.** The D1 food/work printout shows this, and it is registered as descriptive, which is right.
But scope sentence 3 attributes a larger raw response only to "more phenotypic variation, more heritability or both".

**Fix.**
- Append to SCOPE_3: "…or from the down line's room to lose yield by working harder, which differs between the
  bodies".
- Print each fauna's final-generation U − C and C − D (raw, not scored) beside d. These are the upward and downward
  halves, and `arm_stats` already computes the slopes.

### S2. Print the premise check beside the verdict: on this trait, the *designed* body is the more variable one.

**Why.** The ticket reads a designed win as "a clean no for reason (b)". But reason (b) is a mechanism: the more
variable population responds more. The registration's own prediction (§2) is that the designed founders are about 5×
more variable, so DESIGNED RESPONDS MORE is what the mechanism *predicts* here. A designed win refutes a holistic
advantage via reason (b) on this trait, not the mechanism. §2 says this in prose, but nothing in `compare.txt` does.

**Fix.** Add a SCOPE_4, printed under the verdict with the observed σ0 ratio: "Founder σ0 here: holistic X,
designed Y. Reason (b)'s premise, that the holistic population is the more variable, holds / does not hold on this
trait; a designed win is not by itself evidence against the mechanism."

### S3. Promote the planted-positive probe to a registered test.

**What the current tests cover.** The simulated positive in `test_verdict_rule_…` exercises `decide()` alone.
`test_end_to_end_…` runs `main()` but asserts no verdict. So nothing in the suite pins that `main()` forms
d = holistic − designed with the right sign from `lineage.jsonl`.

**What I found.** It does (probe 1a/1b):
- +5 raw planted in the holistic U line's final generation, over 6 toy seeds, gives HOLISTIC RESPONDS MORE;
- the same planted in the designed U line gives DESIGNED RESPONDS MORE;
- RBT-113's controls still pass, since generation G−1 is never a parent generation.

**Fix.** Commit this probe as a test, so that "shown passable" covers the path that will actually be scored.

---

## NOTE (what holds, with evidence)

- **N1. Units: identical. Raw is the right primary, as ruled.**
  - Both faunas: `Experiment.run` → `evaluate(pop, …, terrain_seed, start_seeds)`, with one `generation_sim` per
    generation (`evolution.py:286`, `:706`).
  - The score is `food_score` = items × value − work_cost × kJ (`simulation.py:514`), with no fauna term. An exploded
    body forfeits identically in both.
  - Every generation is solo: `locomotion_phase ≥ G` is enforced by `readout.controls`.
  - `elites 0`, and `survival` is off, so `fitness` is never a running mean.
  - The registration's test re-scores a member of each fauna and recovers its lineage fitness.
- **N2. Sign-flip validity.**
  - Seeds are independent: each has its own founders and worlds. Under H0, d(s) is symmetric iff the fauna labels
    are exchangeable within a seed; the test needs independence and symmetry, not identical distributions across
    O1–O4.
  - Ties and zeros: a zero d(s) adds 0 to every pattern; `≥ obs − 1e-12` makes p conservative on ties; all-zero d
    gives p = 1, which is NOT DECIDED.
  - Level (§A, 20 000 draws, N(0, 0.8)): P(directional verdict) = 0.052 (0.024 + 0.027), which is nominal. The
    designer's 0.067 over 300 draws is noise (SE 0.014).
  - **Caveat:** the null is symmetry, not mean = 0. Under the zero-inflated "escape" scenario that the registration
    names as live (§B: holistic D = +3 in Binomial(12, 1/6) seeds, otherwise 0, E[d] = 0), the level is 0.072, and
    the false DESIGNED rate is 0.063 against a nominal 0.025. This is mild, and it runs against the direction the
    registration is sympathetic to. Stating it in §3 is enough.
- **N3. The verdict rule is unambiguous.** It is three-valued on p < 0.05 and the sign of mean d. VOID takes
  precedence both from `decide`'s control and from any RBT-113 control failure, which `main()` applies after `decide`.
  An RBT-113 control failure in any of the 12 directories, for either fauna, VOIDs the comparison; that is consistent
  with RBT-113's D8, since this comparison touches both faunas in every directory.
- **N4. σ0 cannot leak into the verdict.**
  - `decide` receives only d and c; the σ0 line, `b_div` and h2 are printed after it.
  - One discrepancy: RBT-117's σ0 is the median over the 12 default directories only, while RBT-113's readout pools
    in the Z directories, whose holistic lines are independent replicates. The σ0-unit secondary will therefore not
    match `readout.txt`'s σ0 exactly. The registration states "over these 12 directories"; a comment in
    `compare.txt` would avoid confusion.
- **N5. Power.**
  - The MDE (0.76–0.83 raw) comes only from `pilot.txt` and RBT-113's `sim_arm`, and its assumptions are stated:
    designed h2 0.43, holistic h2 swept, V_m 0 or 0.01, and scaling by founder SD.
  - At 12 seeds, NOT DECIDED is *not* the model's likely outcome. The model predicts DESIGNED RESPONDS MORE with
    P ≈ 1, and the registration says so plainly (§2, §4).
  - After M1 the power at the MDE is unchanged (0.85 in my run); under the registered rule it is about 0.76.
- **N6. Pipeline.**
  - `compare.py` reads only the seed directories' `config.json`, `lineage.jsonl` and `history.json`, plus
    `decompose.json`, all through RBT-113's `readout.py` functions, and it writes nothing. The PR diff touches only
    `runs/RBT-117/` and `tests/test_rbt117.py`.
  - Z directories are refused (tested).
  - Exit code 1 on VOID is fine for `> compare.txt`.
- **N7. Timing and integrity.**
  - Commit `0b411ea8` at 2026-09-27T16:51:35Z; its parent is `bba7c3f`, the integration head with no arm data. No
    RBT-113 readout has run.
  - Nothing in the PR quotes an arm value: every number traces to `pilot.txt` or `power.txt`.
  - Cosmetic: the registration dates the ruling "about 16:55 UTC", but it is posted at 16:36.
- **N8. Holistic Z replicates.** These are discarded, which is correct for pairing. The holistic's contribution to
  the variance of d is small (founder SD 0.14 against 0.71), so little power is lost.
- **N9. Suite:** **396 passed** in 205 s, in a fresh `.[dev]` venv with no scipy (`import scipy` →
  ModuleNotFoundError), at the PR head (`suite.txt`).

## Probes (all synthetic, or pre-data only)

- `probe_stats.py`
  - §A: level under a symmetric null.
  - §B: level under a skewed null.
  - §C: false-VOID rate by d, registered rule against a fixed bound.
  - §D: gross-fault detection.
  - Outputs: `probe_stats_fixed04.txt` is the full run at a 0.4 bound; `probe_stats_fixed08.txt` is
    `ONLY=CD FIXED=0.8`.
- `probe_pipeline.py`
  - A planted positive through `compare.py main()`, both signs.
  - Duplicate, missing and foreign seed directories.
  - Output: `probe_pipeline.txt`.

---
_Generated by [Claude Code](https://claude.ai/code)_
