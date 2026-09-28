# RBT-120 readout adversary on #433 (head 758cb43)

**Readout adversary, 2026-09-28.** Reviewed `REPORT.md` and its outputs against `PREREGISTRATION.md` (§3–§7),
`RUNNER.md` §6 (K1–K7, rule M3), `runs/RBT-121/SYNTHESIS.md` (R1–R12), `runs/RBT-113/` (the O arms and
`sigma0_reference.json`) and the merged `runs/RBT-124/DESIGN.md`. No evolution arm was run. Only committed genomes
and checkpoints were re-scored.

## Verdict: CONFIRMED WITH CAVEATS

- **The three registered verdicts reproduce exactly.** Q1 RESPONDS, Q2 THE BUDGET LOWERS and Q3 NOT DECIDED each come
  out of two routes: the registered scripts, re-run at the arms' launch tree, and an independent recompute. Every
  number in `budget.txt` and `compare.txt` matches to the last printed digit. K1–K7 pass under both routes.
- **M3 holds at every generation**, not only at `final/`. All 864 per-generation holistic champions (36 lines × 24
  generations) reproduce their recorded fitness under the budget. Many would not reproduce without it.
- **The caveats are in the interpretation (MUST 1–2).**
  - The REPORT picks the §7 branch "LOWERS by less than the ceiling scenario (above 70%)". That choice rests on the
    point estimate, 73% against 70%. The 73% [57%, 95%] is 67% plus a non-significant up-half excess, and the data
    fit the "within the predicted range" branch as well.
  - A scope line cites RBT-124 as "0.98 → 0.22 under the cone". In the merged DESIGN, that number is the pack
    sample's. It is not the cone's, and the ruling registered the figure as a range.
- **The SHOULDs** put intervals on the ratios and restate the lever reading as descriptive. The REPORT's causal
  wording on free rotors and on the bias walk goes beyond what the registered descriptive rule licenses.

## 1. Reproduction

### 1.1 Restore and tree

- **The checkout** was a worktree at `9132b78`, where `HEAD:rabbitstew` = `7f4fe72` (K6). The committed B evidence
  was taken from the integration branch (`626ca4c`).
  - Between `9132b78` and `626ca4c`, nothing under `runs/RBT-113`, `runs/RBT-117`, `runs/RBT-121` or `runs/RBT-120`
    changed except the B evidence.
  - So the readout scripts are the registered ones.
- **Platform:** x86_64, mujoco 3.14.0, numpy 2.4.6. That is the arms' `platform.txt`.
- **Restore:** `scripts/durable.sh restore` gave 216/216 for B1–B4 and O1–O4.
  - The 152 committed B evidence files match the restored ones byte for byte (0 differ).
  - `git diff --quiet -- runs/RBT-113` passes.

### 1.2 The registered readout, re-run (RUNNER §6 steps 2–7)

| step | output | against #433's committed file |
|---|---|---|
| `decompose_budgeted.py --workers 4` | `decompose.txt` and 12 `decompose.json` | **identical**; all 12 `decompose.json` are byte-identical |
| `readout.py --reference` | `readout.txt` | **identical** |
| `budget.py` | `budget.txt` | **identical** except the O-directory column's absolute path prefix (12 lines) |
| `compare_budgeted.py` | `compare.txt` | **identical** |
| `motor_report.py` | `motors_B.txt` | **identical** |
| `levers_budgeted.py` (static, ghost, passive), `apportion.py` | `levers_*_B.txt`, `apportion_B.txt` | **identical** (all four files) |

The diffs are in `repro_diff.txt`.

### 1.3 The independent recompute (`recompute.py` → `recompute.txt`)

**How it was written.** It was written from the registration's text. It imports no designer script: not
`readout.py`, not `budget.py`, not `compare.py`.
- It reads only `lineage.jsonl`, `config.json`, `decompose.json` and the frozen σ0 file.
- The slopes are closed-form OLS, and the CIs are scipy t intervals.
- The sign-flip enumerates all 4096 patterns, and is reported both two-sided and one-sided.

| quantity | #433 | recompute |
|---|---|---|
| b_div_B (raw; σ0) | +0.07121 [+0.05998, +0.08244]; +0.3218 [+0.2711, +0.3726]; p 0.0005 | identical; 12/12 seeds > 0 |
| Δ = b_div_O − b_div_B (raw; σ0) | +0.02628 [+0.00416, +0.04840]; +0.119 [+0.019, +0.219]; p 0.0190 | identical; p 0.0190 two-sided (0.0095 one-sided); 8/12 seeds > 0 |
| b_up O − B | −0.00556 [−0.01873, +0.00762], p 0.3765 | identical |
| b_down O − B | +0.03184 [+0.01432, +0.04935], p 0.0015 | identical; 11/12 seeds > 0 |
| b_down_B, b_down_O | +0.0327, +0.0645 | identical |
| h2 O − B | +0.0196, p 0.0962 | identical |
| Q3: d | +0.1260 [−0.1944, +0.4464], p 0.4033 | identical → NOT DECIDED |
| Q3: c | +0.1677 [−0.0138, +0.3492], p 0.0688 | identical → no VOID (p ≥ 0.05, and \|c\| < 0.8) |
| K1, K2, K3 | PASS ×12 | PASS ×12 (re-derived from `config.json` and `lineage.jsonl`) |
| K7 rows moved | 9, 10, 14, 7, 13, 13, 14, 9, 15, 18, 17, 14 | identical. Of those, 3–13 moved in fitness. |
| designed side of B = O's | K2 | true for every per-seed statistic |

- **The C line.** The holistic C line's lineage (names, parents, body hashes) and its `final/` genomes are byte-equal
  between B and O at all 12 seeds. That confirms REPORT §4's "the holistic C line's genomes are the O C line's".
- **The regenerated decompose** gives the food/work table in REPORT §4. Its holistic generation-23 means are founders 0.080 / 0.036, U 1.224 / 0.176, D 0.078 / 0.729 and C 0.052 / 0.020 (food / work). All match. The designed D line's work is 0.925, also matching.

## 2. Did the registered rules fire as written?

- **Q1: yes.** RBT-113's rule is applied on the frozen σ0: lo > 0 and p < 0.05 → RESPONDS.
  - σ0 is 0.22124901500441427, from `runs/RBT-113/sigma0_reference.json`.
  - The NO RESPONSE bar is MDE 0.05 σ0. The CI is not inside ±0.05, so there is no "within margin" tag.
- **Q2: yes.** Δ is per seed, O − B, on the same frozen σ0. LOWERS takes lo > 0 and p < 0.05.
  - The test is `readout.sign_flip_p`, which is **two-sided** and exact over 2^12. The registration says "exact
    sign-flip over 2^12 patterns", not the sidedness. The code fixed before launch is two-sided, so p 0.019 is the
    conservative reading. One-sided it is 0.0095. Either way the verdict is unchanged.
  - The precedence LOWERS → RAISES → NO CHANGE → INCONCLUSIVE is as registered.
- **Q3: yes.** RBT-117's `compare.py` is unchanged: `compare_budgeted.py` swaps only `ARM_OF`.
  - d is the final U − D, holistic minus designed, raw. The exact sign-flip gives p 0.40 → NOT DECIDED.
  - VOID needs both p_c < 0.05 and |c| ≥ 0.8. Here p_c is 0.069 and c is +0.168, so neither holds.
  - RBT-113's per-directory controls pass at all 12 B directories.
- **The σ0 conversions are all on the frozen reference.** Two unscored lines use other σ0s (NIT 3).
- **The b_up / b_down split is registered as descriptive** (§3: "Δ is also printed on b_up and b_down (descriptive;
  the prediction below says where it should fall)"), and §7 predicts "the drop is in b_down, not b_up".
  - `budget.txt` labels them "(descriptive)". The REPORT headline's "Where the drop is" block quotes their p-values
    (0.0015, 0.38, 0.096) without that label (SHOULD 4).
  - The "51% of O's" ratio and the "Q1's 73% comes from the up half" decomposition are post-hoc arithmetic on
    descriptive quantities (MUST 1, SHOULD 1).

## 3. Findings

### MUST

**MUST 1. The §7 branch is chosen on a point estimate that the data cannot separate from the predicted range.**

REPORT §3 says: *"The registered §7 reading that applies is 'Q2 LOWERS by less than the ceiling scenario (above
70%)'."* It then draws the free-rotor conclusion from that branch.

The evidence (`recompute.txt`):
- **b_div_B / b_div_O = 0.730**, with bootstrap 95% [0.585, 0.900] and Fieller [0.568, 0.949]. The interval covers
  the whole predicted 59–70%. In the bootstrap, P(> 0.70) is 0.66 and P(in 59–70%) is 0.32.
- **Δ = +0.119 [+0.019, +0.219] σ0.** The CI contains the whole predicted +0.13 to +0.18. The ceiling scenario's
  E Δ = +0.131 sits 0.012 σ0 above the point, against a CI half-width of 0.10.
- **The whole excess over 70% is the up half's non-significant rise.** b_up_B − b_up_O is +0.0056 [−0.0076, +0.0187]
  (p 0.38). With b_up held at O's, b_div_B would be 0.03297 + 0.03268 = 0.0657, which is **67% of O**. The matching
  Δ = 0.03184 raw = **0.144 σ0**. Both are inside the predicted range.
- **The down half fell to 0.507 [0.379, 0.709] of O's.** §7 predicted "about a third to a half". So the registered
  prediction's own mechanism (up unchanged, down to about a half) is what was observed, within noise.

The registration does not say whether a §7 branch is read on the point or the CI. But it asks the readout to say
which branch applies. The honest reading at n = 12 is that **the point falls just past the ceiling scenario, and the
interval does not distinguish "LOWERS within the predicted range" from "LOWERS by less than the ceiling"**.

The consequences differ:
- The "within the predicted range" branch asks that the budgeted b_div become the benchmark, **quoted beside
  RBT-113's with `apportion_*.txt`'s split**. The REPORT already does this.
- The "less than the ceiling" branch sends the reader to the lever report for the channel.

**Fix.** Restate §3 as follows: *"By the point estimate, 73%, the branch is 'LOWERS by less than the ceiling
scenario'. The CI of the share, [57%, 95%], and of Δ, [0.02, 0.22] σ0, also covers the predicted range, and the
excess over 70% is the up half's n.s. +0.0056. So both §7 branches are reported. Their requirements are met: the
benchmark number is quoted beside RBT-113's, and the lever report is read below (descriptive)."* Rewrite the
"A precision the §7 fork does not make" block the same way (SHOULD 1).

**MUST 2. The RBT-124 scope figure is attributed to the cone, and it is a single sample of a figure that was
registered as a range.**

The REPORT's scope block says: *"RBT-124's pending pack … finds that the holistic U line's food largely rode
free-rotating ball joints (0.98 → 0.22 under the cone)."* In the merged `runs/RBT-124/DESIGN.md` (after M2 and F1):
- **Under the cone (the ranges, M2)**, RBT-124's own sample reads **0.98 → 0.14** (§6 table, line 169; and line 196:
  "0.14 with the ball-mounted wheel").
- **0.98 → 0.22 is the whole pack**: the ranges, the leaf rule, the ball-mounted wheels and the settle (§7 table,
  line 510; line 196: "(0.22 under the whole pack)").
- **The ruling registered the U-line food as a range** (line 212 onward: "Registered as a range (the ruling)"). On
  all 120 RBT-113 O1 U finals over four draws, the RBT-124 adversary measures **1.18 → 0.34 (ranges) → 0.38
  (pack)**. RBT-124's sample (rng-124, O1 and Z1) gives 0.98 → 0.14 → 0.22.
- **The 0.07 is the first draft**, superseded by M2.

So "0.98 → 0.22 under the cone" mixes the pack figure with the cone label, and quotes one end of a registered range.
Because the REPORT says this scope "binds wherever this is quoted", the error would propagate.

**Fix.** *"(RBT-124, on RBT-113's unbudgeted genomes: U-line food 0.98 → 0.14 under the ranges and 0.22 under the
whole pack in its own sample; 1.18 → 0.34 → 0.38 on all 120 O1 U finals; registered as a range)."* Also note that
these are O genomes. B's U line was not probed under the pack, and RBT-124 finds that adding the budget "costs
nothing" to that figure (0.37).

### SHOULD

**SHOULD 1. Give intervals for every ratio the REPORT states as a point.**

These are the paired Fieller 95% intervals (bootstrap in `recompute.txt`):

| REPORT | point | 95% |
|---|---|---|
| "73% of O" (headline, §3, §5) | 0.730 | [0.568, 0.949] |
| "27% of the O lines'" / "removed 27% of it" | 0.270 | [0.051, 0.432] |
| "b_down fell … which is 51% of O's" | 0.507 | [0.379, 0.709] |
| b_up_B / b_up_O (implicit in "b_up did not fall") | 1.169 | [0.821, 1.869] |

- **"Q1's 73% comes from the up half, not from a smaller cut to the down half"** decomposes the point estimate
  correctly. But its only support is a +0.0056 difference with p 0.38.
- Replace it with: *"the down half fell to 51% [38%, 71%] of O's, as §7 predicted (about a third to a half); the up
  half did not change detectably (+0.0056, p 0.38); with it held at O's the share would be 67%."*
- Likewise, **"the motor budget removed 27% of it, all from the down half"** (§5) should read: *"under the
  registered test, LOWERS; the share is 27% [5%, 43%]; the descriptive split puts it in b_down (b_up n.s.)"*.

**SHOULD 2. The free-rotor reading is descriptive, and the metric barely discriminates. The REPORT states it
causally.**

The REPORT says: *"by the registered rule free rotors carry what remains of the D line's waste, and A2's cone is the
next fix."* The registered rule (§7) says only that the channel is "read from the lever report", as "free rotors (A2)
if the contact-free work share of the B D line stays near O's 0.96". §5 says "All levers are descriptive".

Two problems:
- **"Carry" is a causal claim.** The data are a share of work by where it is done, measured on 3 members per group per
  directory on one draw. No arm removed the free rotors.
- **The contact-free share is high in every group, not only in D.** In `levers_ghost_B.txt` (pooled), the founders
  read 0.83, U 0.81, D 0.92 and C 0.87. On O they read 0.84, 0.76, 0.96 and 0.90.
  - A share that is 0.8–0.9 in unselected founders and in the drift line would "stay near 0.96" for nearly any D line.
  - So the registered branch can hardly fail to fire. That is R10's point about instruments, applied to a
    descriptive reading.
  - The informative number is absolute. D's 0.73 yield of work at 0.92 is about 0.67 yield on contact-free children,
    against about 0.02 on C.

**Fix.** Write: *"by the registered descriptive reading (§7), the free-rotor branch applies: 0.92 of the budgeted D
line's work (≈ 0.67 yield) is done on contact-free children (O 0.96). The share is 0.81–0.87 in the founders, U and C
as well, so this locates the work and does not show that free rotors cause the remaining down response. That needs
the cone arm (A2), which is the registered next fix."*

**SHOULD 3. "The bias walk is not the channel" goes further than the registered rule.**

The registered branch is: *"the bias walk if the holistic D line's resting drive rises well above O's 0.24 (towards
the designed D line's 0.94)"*. B's D line is at 0.18, so that branch **does not fire**. That is all 0.18 against
0.24 licenses. Three reasons:
1. Resting drive is the share of Effectors with |tanh(bias)| > 0.9, not a share of work. It does not measure how
   much of D's work flows through biased Effectors.
2. 0.18 is still above the holistic U (0.14) and C (0.11) lines, so some saturation remains under down-selection.
3. `motors_B.txt` gives no per-directory spread for resting drive, so "did not rise" is a comparison of two means with
   no interval.

**Fix.** *"The registered bias-walk branch does not fire: the D line's resting drive is 0.18 (O 0.24), not well
above it. The work routed through biased Effectors was not measured."*

**SHOULD 4. The descriptive split's tests appear in the headline without their label.**

The "Where the drop is" block quotes p 0.0015, p 0.38 and p 0.096. `budget.txt` marks these tests "(descriptive)"
under §3. The headline should too, so that they are not read as registered tests.

**SHOULD 5. K4 cannot detect an unbudgeted run. Name the controls that can.**

K4 recompiles `final/` under the run's config, and the compile applies the cap. So K4 passes for any run, budgeted or
not, as long as `world.py` caps at readout time. Its "can fail" cases are a broken `world.py` and a planted body, not
an arm that ran without the budget.
- **The evidence that the arms ran budgeted is K1** (`config.json`) **and K7** (generation-0 rows moved). But K7 sees
  generation 0 only.
- **This review adds the every-generation check** (`m3_every_generation.py` → `m3_every_generation.txt`; §4). It
  re-scores each generation's champion on that generation's worlds, with the budget on and off.
- **The REPORT's "Budget checks (M3)"** should cite K1, K7 and this check, and describe K4 as what it is: an
  implementation check at readout.

**SHOULD 6. K4's binding range (10–92% of D members) is heterogeneity, not a control failure. It should be quoted as
such.**

Q2 is an intention-to-treat comparison of the budget, not of binding, so heterogeneity in how much the budget binds
does not invalidate the paired test. It does qualify §3's picture of a D line that "reaches its budgeted ceiling":
- **Four of 12 D lines have under 50% of final members over the cap:** seed 5 at 10%, seed 10 at 22%, seed 1 at 35%
  and seed 11 at 48%.
- **Their mean Δb_down is +0.020**, against +0.038 at the eight seeds with 50% or more.
- **Across seeds**, the Spearman correlation of D binding with Δb_down is +0.35 (p 0.26; n.s.).

Add a line: *"the budget binds on 10–92% of the D lines' final members; the Δb_down is larger where it binds more
(n.s.)"*.

### NIT

1. **`budget.py` discards the O directories' K5 failures.** `controls()` computes `bad_o` and never uses it. The O
   directories' RBT-113 controls do pass: RBT-117's `compare.txt` reads "RBT-113 controls PASS" at all 12, and so
   does RBT-113's `readout.txt`. So this changes nothing here, but the REPORT's "and so do RBT-113's own controls"
   is carried by those files, not by `budget.py`.
2. **`decompose_budgeted.py` checks only `U/config.json`.** All 36 configs (U/D/C × 12) carry `motor_budget` 1.77,
   and every `command.txt` carries `--motor-budget 1.77` (verified).
3. **Two σ0 scales in unscored lines.**
   - `compare.txt` prints "b_div (sigma0 units) +0.276", on per-directory SDs. `budget.txt` prints +0.322 on the
     frozen σ0.
   - `readout.txt` prints a new `SIGMA0 REFERENCE {"holistic": 0.21868, …} (frozen for later benchmarks; D4)` line
     computed from B.
   - Neither is registered. The REPORT uses the frozen σ0 correctly, but it should say that the B-derived "SIGMA0
     REFERENCE" line is not a new reference.
   - In §5, "σ0 0.219 against 0.755" is B's observed founder SD, not the frozen 0.2212. Say so.
4. **`compare.txt`'s header cites "PREREGISTRATION.md §5.3"**, which does not exist. Q3 is registered in §3, and §5
   gives the order. The line is printed by `compare_budgeted.py`, which is a registered script and is left as is.
   The REPORT could note the misreference.
5. **"The D line did not reach 0.99 of its ceiling"** (§3) is 0.73 / 0.85 = 86%, a ratio of across-directory means.
   Say "on average". The per-directory ceilings are 0.79–0.92.
6. **The ghost and passive probes sample 3 and 5 members per group per directory on one draw.** The lever table's
   0.92 against 0.96 and 0.34 against 0.39 carry no interval. State n = 36 beside them.

## 4. Budget integrity (M3)

- **`config.json`:** all 36 B line configs have `sim.world.motor_budget` = 1.77, and all 36 `command.txt` have
  `--motor-budget 1.77`. No `run.log` records a resume.
- **Every generation** (`m3_every_generation.txt`): each line's holistic champion was re-scored at every generation,
  from `best_genNNNN.json`, on that generation's own `terrain_seed` and `start_seeds` from `history.json`.
  - **864 of 864 champions reproduce their recorded `best_fitness` under the budget**, with max |recorded − re-scored| = 0.
  - With the budget off, only 524 reproduce. At the other 340, the budget changes the score, and the recorded score is the budgeted one.
  - At 35 of the 36 lines, the budget changes the score at some generation. The exception is the U line of seed 4, whose champions are all inside the budget.
  - So every generation of every B line was scored under the budget, and the check could have failed: an unbudgeted
    generation would show as a mismatch.
- **Every B step in the readout builds its config from the seed directory's `config.json`, or asserts
  `motor_budget == 1.77`.** Verified by reading `decompose_budgeted.py`, `budget.py` (K4), `levers_budgeted.py` and
  `apportion.py`, and by the re-run in §1.2 reproducing their outputs.

## 5. Scope statements

- **RBT-124:** MUST 2.
- **"The bias walk is not the channel":** SHOULD 3.
- **"The arms have no joint ranges":** true. The command line carries no `--ball-cone` or `--hinge-range`, and the
  configs carry none.
- **"The Effector-bias walk is also on":** true, since no `--effector-bias-sigma` is set.

## Files

| file | what |
|---|---|
| `recompute.py` → `recompute.txt` | the independent Q1/Q2/Q3, the b_up/b_down split, the ratio intervals and K1/K2/K3/K7 |
| `m3_every_generation.py` → `m3_every_generation.txt` | M3 at every generation |
| `repro_diff.txt` | the registered readout re-run at `9132b78` against #433's files |
