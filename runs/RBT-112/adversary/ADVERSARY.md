# RBT-112 design adversary: PR #277 (`results/RBT-112-design`, head `61356dc`)

*Fresh session, 2026-09-27. I did not design RBT-112 or RBT-106. **No arm was launched.** No output of a running
or finished RBT-106 or RBT-107 arm was read: no `runs/RBT-106/H*-*` or `P1-*` directory was opened, and no
`ckpt/rbt-106-*` branch was restored. Their existence was checked only by `git ls-remote` branch names (§6, F15).
The only runs made were throwaway ones in scratch: 20- and 40-season HU/HZ ecology runs on seeds 801 and 4
(§1), the design's `baseline.sh` and S = 0 null re-run unchanged (§2, §3), and numpy models (§4). Platform
x86_64, MuJoCo 3.14.0, numpy 2.4.6, as the arms.*

## Verdict

**CLEAR WITH AMENDMENTS: three MUST-FIXes, all to the pre-registration's rules (no code in `rabbitstew/`, no
new run), and six CAVEATs.**
- **The flag is sound.** It is stream-preserving and byte-identical when unset, against c872e80's code on two
  seeds, genome for genome. At S = 0 it freezes the global biases and nothing else, and no global bias leaks in.
- **The decisive pre-arm step is sound.** All 20 baseline tables regenerate byte for byte. u = 0.282 → 0.089
  re-derives with independent code, and the default reproduces RBT-106's tables. DECISION.md was committed before
  the tables, and no estimator the designer could have picked after seeing them changes the decision.
- **The null is faithful.** 1.0% and 1.5% re-count exactly, and the S = 0 null regenerates byte for byte.
- **What must change before launch:**
  - **F7:** the SUPPORTED count. The registered "#HELD(HZ) ≥ 5" costs 0.2–0.5 of power in the informative window,
    and buys a null already far below need. RBT-106's own count form, "#HELD(HZ) − #HELD(HU) ≥ 3", fixes it at no
    cost.
  - **F11:** the gate, pinned to RBT-106's registered H readout line by line.
  - **F14:** FALSIFIED split by whether the planted roots survived, so the verdict cannot be read two ways.
- **More seeds (F9): not recommended.** Twenty HZ seeds would add 0–0.2 of power over F7's free change, at twice
  the cost (+5 sessions, +7.5–11 session-hours), and the extra seeds would have no measured null.

| # | item | finding | severity |
|---|---|---|---|
| F1 | 1 | Flag unset = c872e80's code, genome for genome (801, 4; package asserted in-process); S = `weight_sigma` = unset; the draw is the same one standard normal | NONE |
| F2 | 1 | S = 0 freezes only global biases. `crossover_controller` moves whole global brains, so no bias leaks. An added unit keeps its birth bias. `func` re-typing still acts, but every transfer function has f(0) = 0, so the planted unit's resting drive stays 0 | NONE |
| F3 | 1 | SE-Z: the host's 6 founder global neurons (biases −1.4 to +1.3) freeze too. The treatment is "global biases frozen", not "the planted unit's bias frozen", and the verdict's wording must carry that when SE-Z fails | CAVEAT |
| F4 | 2 | DECISION.md (`daca7fd`, 01:57:40) precedes the tables (`bb1455c`, 02:01:49), and its content is the rule. Git cannot prove the run followed the commit (249 s gap, against my 250–278 s re-run), but every estimator gives 0.080–0.089, so the decision is immune | NONE |
| F5 | 2 | u re-derived: 20/20 tables byte-identical on re-run; u(8) 0.282 → 0.089 by independent code; the default equals RBT-106's tables (10/10 below the header; whole file for 801 and 4) | NONE |
| F6 | 3 | Each arm is read against its own operator's table, which is right. 2/200 and 3/200 re-counted; the S = 0 null regenerates byte for byte. Its upper 95% bound is 4.3% | NONE (a CAVEAT on the 200 replicates, absorbed by F7's null) |
| **F7** | 4 | **"#HELD(HZ) ≥ 5" is the binding cost.** In the window, SUPPORTED's power is 0.07–0.28 (genealogy) and 0.72–0.97 (n = 40). With "#HZ − #HU ≥ 3" it is 0.53–0.63 and 0.91–0.98. The null is 3.7 × 10⁻⁴ at the measured rate, and 7.6 × 10⁻³ at its upper bound | **MUST-FIX** |
| F8 | 4 | The anchors. The genealogy scenario is internally inconsistent (selection on the compass is selection on planted roots). n = 40 overstates the carrier share, because it omits crossover mixing. A self-consistent individual model brackets the truth, and puts the gate's window up to s ≈ 0.3–0.4 | CAVEAT |
| F9 | 4 | 20 seeds: see F7. Not worth it once F7 is made; figures and cost below | CAVEAT (recommendation) |
| F10 | 5 | `prelaunch.sh` shows the controls can pass on the arm's own S = 0 hosts. The refusals were re-exercised: exit 7 on a tree mismatch or FAIL, exit 6 on a partial certification. Evolved hosts at 300–590 are untestable pre-arm, but no constructional failure route exists. The clean check covers `rabbitstew/` only | CAVEAT |
| **F11** | 6 | **§7.1 is not pinned to RBT-106's registered H verdict.** SUPPORTED is unnamed, VOID is uncovered, FALSIFIED-b with #HU 3–4 conflicts with "coordinator decides", and it is unclear whose #HELD(HU) the gate reads | **MUST-FIX** |
| F12 | 7 | `resting.py --frozen` calls any paying carrier with b ≠ 0 a FAULT, which makes the arm unusable. A unit added under S = 0 legitimately carries its birth bias, so a de novo paying carrier would void a seed for a positive event. The birth-level freeze test is the right fault | CAVEAT |
| F13 | 7 | A Z pair needs HU's install control to pass. F12's masking route, the very bias walk under test, can fail it and censor the control arm toward VOID. HELD does not use function | CAVEAT |
| **F14** | 7 | **FALSIFIED has two registered-but-unruled readings:** "the operator is not the stall" and "the planted roots died out". §6.5 leaves the choice to the report | **MUST-FIX** |
| F15 | — | Merge timing: all 20 RBT-106 H arms already have `ckpt/` branches, so merging #277's `rabbitstew/` change cannot disturb an RBT-106 launch | NONE |

---

## 1. The flag (checklist 1)

**Code** (`git diff 5edf771 61356dc -- rabbitstew/`).
- The only behavioural line is in `mutate_weights`. For `owner is None and global_bias_sigma is not None` it runs
  `u.bias += float(rng.normal(0.0, 1.0)) * S`; otherwise `rng.normal(0.0, weight_sigma)`, unchanged.
- Both consume one standard normal. numpy's `normal(0, σ)` is `0 + σ·z`, so S = 0.4 is bit-identical to the
  default. At S = 0 the step is `b + 0.0·z = b`, exact, for finite z.
- `mutate_controller` passes `config.global_bias_sigma`, and the ecology's non-conventional path passes it too.
  `mutate` (holistic) and `mutate_brain` do not.
- `to_dict` drops the field when None.

**My byte-identity runs** (`bi.sh` → `bi_compare.py` → `bi_compare.txt`):
- RBT-106's HU command, built by RBT-106's `command.py`, run in-process by `run_code.sh`. Each run writes
  `code.txt`: the path of the `rabbitstew` package actually imported, and whether `MutationConfig` has the field.
- This closes a gap in the design's check 3. There, "c872e80's code" rests on `python -m` resolving the
  package from the worktree's cwd, asserted in a separate `python -c`. Here it is asserted in the process that
  runs.

| check | runs | result |
|---|---|---|
| A. flag unset against **c872e80** | 20 seasons, seeds **801 and 4**; `code.txt`: `d112/rabbitstew has_flag True` vs `wt-c872e80/rabbitstew has_flag False` | 801: **270 genomes** (both faunas, saved at birth), lineage.jsonl, cohorts.jsonl, history, config: **0 differing files**. 4: **311 genomes**, the same: **0 differing** |
| B. `--global-bias-sigma 0.4` (= `weight_sigma`) against unset | 20 seasons, 801 | every genome, lineage and cohort byte-identical; config differs only in `mutation.global_bias_sigma` |
| C. S = 0, every designed-body birth | 40 seasons, 801 and 4 | see below |

**C. Does S = 0 freeze only global biases, and does anything leak a bias in?**
- For every designed-body birth in the S = 0 runs, the child's global biases (as a multiset) must come from its
  parents' global biases, plus at most one new value, a unit added at that birth.
- Results (`bi_compare.txt`):
  - **S = 0, 801:** 128 births, **0** with more than one global bias no parent carried, 14 new values in all (the
    added units).
  - **S = 0, 4:** 121 births, **0**, 12 new values.
  - **The planted unit.** Of the children whose parents[0] carries it at b = 0, 58/63 and 61/66 still carry
    b = 0. The rest took a mate's whole global brain, or lost the unit.
  - **The default twins, for contrast:** 81/151 and 67/139 births with a global bias new at birth; 273 and 236
    new values.

**Why nothing leaks:**
- **Crossover.** The designed body with `--conventional-topology` (HU's command) breeds by `crossover_controller`,
  which moves the mate's **whole** global brain (`child.global_brain = b.global_brain.copy()`). It never mixes
  biases.
  - The index-aligned bias mixer `crossover_weights` (`ua.bias = ub.bias` by unit position) is on the other
    path only, the ecology without `--conventional-topology`.
  - That path *could* graft a mate's non-zero bias onto the planted unit's index, but no RBT-112 arm uses it
    (`tests/test_rbt112.py` pins HZ's command).
- **Unit addition.** A new global unit is `random_neuron`, with bias N(0, 0.5) drawn at birth, and at S = 0 it
  keeps that bias for life. This is a leak only in the trivial sense that the population's set of global biases
  grows. The planted unit is never touched.
- **What still acts on the planted unit:** removal (`remove_unit_rate` 0.06), link changes, and `func` re-typing
  (`func_rate` 0.05). For every transfer function in `rabbitstew.brain`, f(0) = 0 (tanh, sin, abs, relu, sign,
  integrate, differentiate; `resting.py`'s `transfer`). **So a re-typed planted unit at b = 0 still rests at 0.**
  F12's masking route is closed by construction.
  - What re-typing does do is break the compass's sign or gain. That is in the measured u = 0.089, the
    structure's own decay, and is correct to leave in.

**F3 (CAVEAT): the host freezes too.**
- Every w = 32 founder carries **six host global neurons** besides the planted one. For example `801/000`:
  0.361, 0.413, −0.182, 0.547, −0.053, 0.301, 0.0; `4/003`: 1.294, −0.753, 0.508, 0.923, −0.260, −0.087.
  At S = 0 none of them can be tuned.
- SE-Z (0.65) is registered, and the readout prints window income HZ − HU. But no rule says what a failed SE-Z
  does to the verdict.
- **Anecdote** from my 40-season pairs, not a test:
  - **S = 0 had 15% and 13% fewer designed births:** 128 against 151 (801), 121 against 139 (4).
  - The mean lifetime score was slightly higher (0.917 against 0.888; 0.966 against 0.918).
  - So the HZ host may breed more slowly. That lowers depth, which the own-depth μ handles, and it may change s,
    which nothing handles.
- **Recommended pre-registered sentence.** If SE-Z's interval excludes 0, the verdict is worded "with the
  designed body's global biases frozen (host and planted)", not "the planted unit's bias walk". The
  paired births and depth are printed beside it.
  - The depth effect on erasure is already handled: each genome's μ is read at its own depth.
  - What is not handled is a change in s itself, since the host's gait sets the compass's relative worth.

## 2. The baseline and the decision (checklist 2)

**Commit order.**
- `ce1e9ce` (the flag) and `daca7fd` (DECISION.md + `baseline.py`) both have commit date 01:57:40. `bb1455c` (the
  20 tables, `baseline.sh`, `erasure.py`/`.txt`) is 02:01:49, 249 s later.
- `git show daca7fd:runs/RBT-112/DECISION.md` is the rule as registered. `baseline.py` is unchanged from
  `daca7fd` to the head.

**Could the run have come after the commit?**
- My re-run of `baseline.sh`, unchanged, took **278 s** for 20 tables on a 4-core box, partly contended; the
  uncontended tables took 12–13 s each (≈ 250 s).
- So the designer's gap is just enough for the run and not much more. Git proves the order of commits, not of
  runs.
- **Why this is NONE anyway:**
  - The thresholds (≤ 0.12 / ≥ 0.20) are the **ticket's**, filed at 01:52 before any design work.
  - The designer's only freedom was the estimator, and every one gives the same side of 0.12 by a wide margin.
    From my `rederive_u.txt`:
    - u(1), u(2), u(4), u(8), u(16): 0.083, 0.089, 0.087, 0.089, 0.084;
    - f(0)-normalised: 0.080–0.089;
    - log-linear fit over depths 1–16: 0.085;
    - per-seed u(8): 0.083–0.096.

**Re-derivation (F5).**
- `rebaseline.sh` re-ran `baseline.sh` into scratch: **20 of 20 tables byte-identical** to the committed ones.
- The default tables equal RBT-106's `baseline/baseline-w32-SEED.txt` below the header on 10 of 10 seeds, and
  whole-file for 801 and 4.
- `rederive_u.py` (independent parsing and pooling by column name) gives:
  - **default u(8) 0.282, per seed 0.282 [0.274, 0.290];**
  - **S = 0 0.089 [0.086, 0.092];**
  - the structure's own decay at S = 0 0.067.
- **DECISION: u ≤ 0.12, worth running. Confirmed.**

## 3. The null for HELD with crossover (checklist 3)

**Each arm against its own operator's table is right.**
- HELD asks whether selection keeps more than *this* operator alone leaves. HZ's operator leaves 0.245 at depth 16
  against 0.013, so reading HZ against the default table would call HELD with no selection at all.
- The price is that HZ's bar is higher in raw carriers. §5.1 states this, and it is the correct price.

**Faithful.**
- `null_recount.py` re-parses the committed `null/` tables independently of `pool_xnull.parse`:
  - default, crossover: **2/200 = 1.0% [0.1%, 3.6%]**;
  - **S = 0, crossover: 3/200 = 1.5% [0.3%, 4.3%]**;
  - default, mutation only: 2/200;
  - S = 0, mutation only: 26/200 = 13.0%.
  All exactly as §5.2.
- The default tables equal the RBT-106 adversary's committed `xnull-w32-SEED.txt` on 10 of 10 seeds, below the
  header.
- `renull.sh` restored `ckpt/rbt-90-SEED` (RBT-90 part 2, a finished run) and re-ran `null_xover_s0.py
  --global-bias-sigma 0`, unchanged: **10 of 10 S = 0 null tables byte-identical** (`renull.txt`).
- **The 13% → 1.5% reading is right, and important.** In the S = 0 mutation-only null, compasses persist in whole
  clades and overdisperse k. Crossover breaks the clades by handing bare mates' brains into planted roots. The arm
  runs at crossover 0.3, so 1.5% is the matched rate.
- **The one soft spot:** 200 replicates, with an exact upper 95% bound of 4.3%. F7's null is computed at both.

## 4. Power (checklist 4)

**Re-derived cells.** `power_alt.py` imports the design's `power.py` unchanged and reproduces its registered cells
exactly: genealogy s = 0.2 / 0.3: 0.071 / 0.284; n = 40: 0.719 / 0.965; FALSIFIED 0.108 / 0.005.

**F7 (MUST-FIX): the "≥ 5" floor, not the seed count, is what starves SUPPORTED.**
- With #HELD(HU) ≤ 2 (the gate), SUPPORTED = "#HZ ≥ 5 and #HZ − #HU ≥ 3" is "#HZ ≥ 5". RBT-106's own SUPPORTED
  count form is the gap alone. The design adopted ≥ 5 from FALSIFIED-a's "≥ 5", and justified it by its null,
  1.8 × 10⁻⁷. That null is far below any need.
- **Replace with #HELD(HZ) − #HELD(HU) ≥ 3.** Given the gate, this is #HZ ≥ 3–5. It stays disjoint from
  FALSIFIED (#HZ ≤ 1).

The count nulls at the per-seed rate q0 (`power_alt.txt`):

| q0 | P(#HZ ≥ 5 of 10) | **P(#HZ ≥ 3 of 10)** | P(#HZ ≥ 6 of 20) |
|---|---|---|---|
| 0.015 (measured) | 1.8e-07 | **3.7e-04** | 3.7e-07 |
| 0.043 (its exact upper 95%) | 3.1e-05 | **7.6e-03** | 1.5e-04 |

Power given the gate (#HELD(HU) ≤ 2), the design's own model, ρ = 0.10 (`power_alt.txt`):

| scenario | s | registered SUPPORTED | **gap ≥ 3** | FALSIFIED | 20 HZ seeds, #HZ ≥ 6 |
|---|---|---|---|---|---|
| genealogy | 0.15 | 0.017 | **0.337** | 0.282 | 0.220 |
| genealogy | 0.20 | 0.071 | **0.534** | 0.108 | 0.556 |
| genealogy | 0.25 | 0.167 | **0.617** | 0.040 | 0.788 |
| genealogy | 0.30 | 0.284 | **0.626** | 0.015 | 0.893 |
| n = 40 | 0.15 | 0.380 | **0.779** | 0.041 | 0.884 |
| n = 40 | 0.20 | 0.719 | **0.909** | 0.005 | 0.990 |
| n = 40 | 0.25 | 0.898 | **0.956** | 0.001 | 0.999 |
| n = 40 | 0.30 | 0.965 | **0.980** | 0.000 | 1.000 |

- As registered, at genealogy s = 0.2 the arm reads **SUPPORTED 0.07, FALSIFIED 0.11 and NOT DECIDED 0.82**. It
  most likely spends 7.5–11 session-hours to say nothing.
- With the gap rule, SUPPORTED is 0.53.

**F8 (CAVEAT): the anchor. Neither scenario is self-consistent.** I built an independent individual-based model
(`power_adv.py`) in which the genealogy is made by the same selection that acts on the compass:
- N = 60, 30 planted and 30 bare;
- drift from a uniform breeding pool of M;
- selection with weight 1 + s on paying carriers when a child picks parents[0] (so E[x'] = x(1 + s)/(1 + sx),
  the design's recursion);
- the ecology's crossover: 0.3 × 0.5 of births take a mate's whole global brain;
- loss u per birth; readings at depths 10 and 19; B from the operator's pooled table.

M is calibrated two ways, and no single M fits both:
- **M = 15** fits part 2's neutral spread of the planted-rooted share (sd 0.35 / 0.43 at 300 / 599; 3 of 10 seeds
  with none at 599). Its null is 4%, three times too high.
- **M = 40** fits the measured S = 0 null (1.3% against 1.5%), but under-drifts the roots.

| s | P(#HU ≤ 2) M15 / M40 | registered SUPPORTED M15 / M40 | **gap ≥ 3** M15 / M40 | FALSIFIED M15 / M40 | 20 HZ, #HZ ≥ 6, M15 / M40 |
|---|---|---|---|---|---|
| 0.15 | 1.00 / 1.00 | 0.032 / 0.036 | **0.270 / 0.279** | 0.379 / 0.363 | 0.192 / 0.214 |
| 0.20 | 1.00 / 0.98 | 0.096 / 0.242 | **0.431 / 0.600** | 0.214 / 0.091 | 0.440 / 0.743 |
| 0.25 | 0.99 / 0.93 | 0.268 / 0.556 | **0.633 / 0.784** | 0.079 / 0.016 | 0.778 / 0.964 |
| 0.30 | 0.95 / 0.79 | 0.462 / 0.854 | **0.741 / 0.927** | 0.028 / 0.001 | 0.932 / 0.999 |
| 0.40 | 0.80 / 0.29 | 0.828 / 0.995 | 0.911 / 0.997 | 0.002 / 0.000 | 0.998 / 1.000 |

What this says about the anchors:
- **n (the planted-rooted living at 599).** Under selection it averages **38–45**, with every root lost on 15–20%
  of seeds at M = 15, and on ≤ 3% at M = 40.
  - So the genealogy scenario, where 3–4 of 10 seeds lose every root *whatever s is*, is a pessimistic bound.
    Selection on the compass *is* selection on planted roots.
  - n ≈ 40 is the better anchor for n.
- **x (the carrier share among the planted-rooted).** It is lower than the design's recursion (at s = 0.2:
  0.36–0.42 against 0.52). The recursion treats the planted-rooted as a closed class starting at x = 1.
  Crossover mixes it with the bare half, whose starting carrier share is 0.
  - So the n = 40 scenario's 0.72–0.97 is optimistic by 0.1–0.5 at s = 0.2–0.25.
- **The truth for the registered rule** in the window s = 0.15–0.3: **0.03–0.46 (M15) / 0.04–0.85 (M40).**
- **With F7's gap rule: 0.27–0.74 / 0.28–0.93.**
- **The informative window is wider than §6.3 says.** In the self-consistent model, HU stays not-held (the gate
  premise, #HU ≤ 2) with probability ≥ 0.8 up to s ≈ 0.3 (M40) or 0.4 (M15). There HZ's power under the gap rule
  is 0.6–0.9.
- A population-level alternative, HELD-ALL (k_planted + k_bare against the arm's full-operator null percentile),
  was checked and is **not** better: 0.03–0.28 (M15) and 0.19–0.99 (M40) at s = 0.15–0.3, `power_adv.txt`.

**F9: twenty seeds, and the cost.**
- 10 more HZ arms is 5 more sessions of about 1.5–2.2 h, **+7.5–11 session-hours**, doubling the arm's cost.
- **What they would buy, once F7 is made:**
  - **SUPPORTED:** #HZ ≥ 6 of 20, null 3.7 × 10⁻⁷. That is **+0.0 to +0.2** over the gap rule at 10 seeds for
    s = 0.2–0.3 (M15: 0.44 / 0.78 / 0.93 against 0.43 / 0.63 / 0.74; M40: 0.74 / 0.96 / 1.00 against
    0.60 / 0.78 / 0.93). It is *lower* at s = 0.15 (0.19–0.21 against 0.27–0.28).
  - **FALSIFIED:** a sharper one. #HZ ≤ 2 of 20 misses a real s = 0.15 effect with 0.12 against 0.28 (the design's
    model, genealogy).
- **Why the extra seeds are costly:**
  - RBT-106 has only ten founder sets (part 2's seeds). The extra arms would have to be the same founders at a
    new ecology `--seed`, which is new code in `held.py` and `readout.py`.
  - They would have **no measured null**, since part 2's genealogies exist only for the ten, and no HU twin.
- **Recommendation: make F7, keep ten seeds.** Revisit only if the arm reads NOT DECIDED with #HZ = 2.

**Can the design as it stands yield an answer worth the arm?** Barely. Over the plausible window its likeliest
verdict is NOT DECIDED. With F7 it is a real test for s ≳ 0.2. Below that, it reads FALSIFIED often, and F14's split
is what keeps that FALSIFIED honest.

## 5. The RBT-104 lesson (checklist 5)

**What `prelaunch.sh` shows, and does not.**
- It shows that each per-arm control *can pass on the arm's own S = 0 hosts*:
  - two 61-season HZ smoke runs, bests at 0–60, seven bodies, the readout's t(6);
  - the install control FD on 2 of 2 lines and F > 0 on 14 of 14 bodies (+0.92 to +2.45);
  - analyse.py 40/40 on both;
  - resting 0 faults.
- **The hosts are near-founders** (depth ≲ 3 at season 60). The arm reads its bests at 300–590, and no pre-arm run
  can show those.
- What matters is that **no constructional failure route exists**, which is what RBT-104's S8 lacked:
  - K = 1, so the install is at the hosts' own scale;
  - the planted unit rests at 0, as shown in §1 with re-typing included;
  - the install control needs no global bias.
- **HELD's reachability** is shown in `prelaunch.txt` (d) by arithmetic on the S = 0 tables (n > B at n = 20,
  depths 2–40). I also ran `runs/RBT-112/held.py` end to end on my 40-season S = 0 run (`held-e2e.txt`, seed 4, season 39, a smoke reading):
  - it names the S = 0 table, reads μ = 0.867 at mean depth 1.66 (the S = 0 table's 0.91/0.84 at depths 1/2,
    against the default's 0.71/0.52), and calls the rule;
  - so the arm's own-table path works on a real run directory.

**The refusals, re-exercised** (`launcher-refusals-adv.txt`, a throwaway worktree of `61356dc`, SEASONS=1 as a
guard, nothing launched):

| case | exit |
|---|---|
| a stand-in certification, with `prelaunch.txt`'s `rabbitstew_tree` changed | **7** ("made on another rabbitstew/ tree") |
| a stand-in certification, with `PRELAUNCH: FAIL` | **7** |
| a certification reading SAME RUN on HU-801 only | **6** |

The designer's own record covers exits 2, 5, 6 (no file) and 7 (no `prelaunch.txt`).

**F10 CAVEAT: the clean check covers `rabbitstew/` only.**
- An uncommitted edit to `runs/RBT-112/command.py`, `runs/RBT-106/command.py`, `runs/RBT-106/founders.py` or
  `runs/RBT-104/seed_founders.py` would change the arm's command silently.
- `command.txt` records the command, but `readout.py` does not compare it with `command.py HZ SEED`.
- **Suggest:** extend exit 5 to those four files, or have `readout.py` check `command.txt` against `command.py`.
  Both are one line.

## 6. The gating (checklist 6)

**F11 (MUST-FIX).** RBT-106's H readout (`runs/RBT-106/readout.py` l. 207–218) decides, in order:
1. **VOID** (fewer than 7 usable HU–HP pairs);
2. **SUPPORTED** (nP − nU ≥ 3 and the log-excess > 0);
3. **FALSIFIED-a** (nU ≥ 5 and the log-excess not > 0);
4. **FALSIFIED-b** (nP ≤ 1);
5. **NOT DECIDED**.

It prints `HELD: HU nU, HP nP` over the **usable HU–HP pairs**. §7.1's "FALSIFIED-b, or NOT DECIDED with
#HELD(HU) ≤ 2; HELD or FALSIFIED-a closes; at #HELD(HU) ≥ 3 the coordinator decides" leaves four holes:
- **SUPPORTED is not named.** "HELD" is not an RBT-106 verdict. Under SUPPORTED, nU ≤ 2 is quite possible: HU
  not held, HP held. The premise HZ needs is exactly "HU not held", and SUPPORTED satisfies it.
- **VOID is not covered.** For example, F12's route failing the HU/HP install controls.
- **FALSIFIED-b with nU = 3 or 4** launches under the first clause, and is "coordinator decides" under the third.
- **"#HELD(HU)" is not defined.** It could be RBT-106's count over HU–HP pairs, or RBT-112's over HU–HZ pairs,
  which differ as soon as usability differs.

**Proposed text** (it reads one printed number and is fixed before H reads):
> RBT-112 launches iff RBT-106's `readout.txt` (H) is not VOID and its line `HELD: HU nU, HP nP` has **nU ≤ 2**,
> whatever the H verdict label (SUPPORTED, FALSIFIED-b or NOT DECIDED). It closes as not needed iff nU ≥ 3,
> FALSIFIED-a included. If H is VOID, the premise is read from the HU arms alone: launch iff at least 7 HU arms are
> viable, on x86_64, of c872e80's code and pass analyse.py's control, and at most 2 of them are HELD; otherwise
> close as unread. No other branch.

If the coordinator rules that SUPPORTED closes the ticket, which is the ticket's "If H reads HELD", that must be
written now in the same form.

## 7. What lets the result be read two ways (checklist 7)

**F14 (MUST-FIX): FALSIFIED's two readings.**
- §6.5 names them: "the operator is not the stall (s < ~0.1)" and "the planted lineages die out for reasons that
  have nothing to do with the compass". It then leaves the choice to the report.
- An HZ seed with no planted-rooted genome at 300 or 599 cannot read HELD, whatever the compass did.
- **Pre-register the split.** Per HZ seed, class it:
  - **LOST:** n_planted = 0 at 300 or 599;
  - **NOT HELD:** n > 0 and k_planted ≤ B at either reading;
  - **HELD.**
- Then:
  - **FALSIFIED** = #HELD(HZ) ≤ 1 and #LOST(HZ) ≤ 2;
  - **FALSIFIED-ROOTS** = #HELD(HZ) ≤ 1 and #LOST(HZ) ≥ 3, read as "the planted lineages were lost; the operator
    question is unanswered on those seeds".
- This costs nothing, and removes the post hoc choice.

**F12 (CAVEAT): the frozen-bias FAULT.**
- `resting.py --frozen` marks any champion whose paying predicate unit has b ≠ 0 as FAULT, and `readout.py` then
  makes the HZ arm unusable.
- Under S = 0 a unit added at birth keeps its drawn N(0, 0.5) bias (§1). A champion whose best routed unit is
  such a unit, de novo or rewired, would void the seed for a *positive* event. It is rare, since RBT-102 puts de
  novo arrivals at ~0.26 per 600 seasons, but it is a false VOID route.
- **The fault the flag can actually commit** is a global bias that changed after birth. That is the birth-level
  test of §1 C: `bi_compare.freeze`, run by `postrun.sh HZ` over the arm's own saved genomes.
- **Suggest:** make that the FAULT, and keep resting's b print as information.

**F13 (CAVEAT): the control arm censored by the mechanism under test.**
- A Z pair is usable only if **HU's** install control passes.
- F12's route is a drifted planted unit masking the control on HU champions, and that drift is the bias walk this
  arm tests. So it drops HU pairs exactly when the walk bites, pushing toward VOID.
- HELD, the verdict, reads structure, not function.
- **Suggest:** for the HELD verdict, an HU arm is usable if viable, on x86_64, of c872e80's code and passing
  analyse.py's control. Its install control gates only the function comparison, and is printed with F12's line.
  - This makes RBT-112's HU count possibly differ from RBT-106's. F11's gate reads RBT-106's own number, so the
    two uses stay separate.

**F15 (NONE): merge timing.** `git ls-remote` shows `ckpt/rbt-106-HU-*` and `HP-*` for all ten seeds each, so
every RBT-106 H arm has launched. RBT-106's `readout.py` requires each arm's recorded tree to be c872e80's, and
that comes from the arm's own `commit.txt`. So merging #277's `rabbitstew/` change into integration cannot
disturb RBT-106.

**Otherwise clean:**
- HZ's command is HU's plus one flag (pinned by test).
- HELD per arm against its own table.
- The paired log-excess and the raw share are reported, not scored.
- The function verdict is reported, not in the verdict, and patchy-scored for the attribution weakness §6.3
  documents.

## 8. Scripts and outputs, by role

| file | role |
|---|---|
| `run_code.sh` | runs RBT-106's HU command in-process on a given `rabbitstew/` checkout, recording the imported package (`code.txt`) |
| `bi.sh` → runs in scratch; `bi_compare.py` → `bi_compare.txt` | §1: A (unset against c872e80, 801 and 4), B (S = weight_sigma), C (the birth-level freeze test), D (SE-Z anecdote) |
| `rebaseline.sh` → `rebaseline.txt` | §2: `baseline.sh` re-run unchanged into scratch, timed; `cmp` against the committed 20 tables |
| `rederive_u.py` → `rederive_u.txt` | §2: u by independent code, several estimators |
| `null_recount.py` → `null_recount.txt` | §3: the null re-counted from the committed tables, with exact intervals |
| `renull.sh` → `renull.txt` | §3: the S = 0 null re-run unchanged from restored `ckpt/rbt-90-SEED`; `cmp` |
| `power_alt.py` → `power_alt.txt` | §4: the design's `power.py`, imported unchanged, re-read for the gap rule and twenty seeds |
| `power_adv.py` → `power_adv.txt` | §4: the independent self-consistent model (numpy only) |
| `launcher-refusals-adv.txt` | §5: exits 7, 7 and 6 re-exercised |
| `held-e2e.txt` | §5: `held.py` end to end on an S = 0 run directory |

These are run from a checkout of #277's head with this directory merged in. The paths to scratch are variables
at the top of each script.

**Suite:**
- **342 passed** on this branch (`origin/claude/new-session-4cao7d` + `runs/RBT-112/adversary/` only), in a clean
  `pip install -e '.[dev]'` venv with no scipy.
- **358 passed** on #277's head `61356dc`, in the same kind of venv.
