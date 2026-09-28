# RBT-120 readout: the holistic selection response under the motor budget

**Designer, 2026-09-28, about 01:55 UTC.** This readout was run exactly as registered (`PREREGISTRATION.md` §3–§5,
`RUNNER.md` §6). No scored code changed.

**Amended after the coordinator's ruling (02:44, CONFIRMED WITH CAVEATS)** on the readout adversary
(#442, `readout-adversary/ADVERSARY.md`). MUST 1–2 and SHOULD 1–6 are applied in place, and NITs 3, 5 and 6 are taken.
**No number changes.**
- The adversary reproduced every output byte for byte at `9132b78` (the only difference is paths in `budget.txt`).
- An independent recompute matches Q1, Q2, Q3, the split and K1/K2/K3/K7.
- M3 holds at every generation: 864 of 864 holistic champions reproduce under the budget, against 524 without it.

## Headline (the registered rules' output)

| question | verdict | numbers |
|---|---|---|
| **Q1** (primary): the holistic response under the motor budget (Σgear cap 1.77 + servo clamp) | **RESPONDS** | b_div_B **+0.0712** [+0.0600, +0.0824] yield per generation = **+0.322** [+0.271, +0.373] frozen σ0; p 0.0005; 12 of 12 seeds positive; **73% [57%, 95%]** of the O lines' +0.0975 (Fieller) |
| **Q2** (registered test): how much of RBT-113's holistic response the motor budget removed | **THE BUDGET LOWERS THE HOLISTIC RESPONSE** | Δ = b_div_O − b_div_B **+0.119** [+0.019, +0.219] σ0 per generation (+0.0263 raw); exact two-sided sign-flip p 0.019; **27% [5%, 43%]** of the O lines' +0.0975 |
| **Q3** (RBT-117's comparison, `compare.py` unchanged) | **NOT DECIDED** | d = holistic − designed final U − D **+0.126** [−0.194, +0.446] raw; p 0.40. C-line control +0.168, p 0.069: no VOID. |

**Controls:** K1–K7 **PASS at all 12 seeds** (`budget.txt`), and so do RBT-113's own controls (`readout.txt`; K5).

**Where the drop is** (the registered descriptive split, §3; these p-values are descriptive, not registered tests).
- b_down fell from +0.0645 to **+0.0327**, which is **51% [38%, 71%]** of O's (O − B +0.0318, p 0.0015, descriptive).
  That is what §7 predicted ("about a third to a half").
- b_up did not change detectably: +0.0385 against O's +0.0330 (O − B −0.0056, p 0.38, descriptive).
- h2 is 0.071 against 0.091 (p 0.096, descriptive).

**Scope, which binds wherever this is quoted.** This is the holistic response **without the gear allowance and the
servo wind-up**, and not without every lever.
- **The arms have no joint ranges.** Ball joints stay range-less, so limbs can still spin freely inside or through
  their parents: the cone was out of RBT-120's scope.
- RBT-124's pending pack, which is not in these arms, finds that the holistic U line's food largely rode
  free-rotating ball joints.
  - **On all 120 RBT-113 O1 U finals over four draws:** 1.18 → 0.34 under the ranges → 0.38 under the whole pack.
  - **In RBT-124's own sample:** 0.98 → 0.14 under the ranges (the cone alone) → 0.22 under the whole pack.
  - The ruling registered this figure as a range.
  - These are O genomes, unbudgeted. B's U line was not probed under the pack; RBT-124 finds that adding the budget
    costs nothing to that figure (0.37).
- **So B's locomotion is not "fair physics". It is fair motor budget only.**
- The Effector-bias walk (resting throttle) is also on, for both faunae.
- As RBT-113's disclaimers say, this is the response to imposed selection in this design, not natural selection in
  the ecology, and h2 is a property of this design.

## 1. What was run

- **Arms B1–B4** (#426–#429; 216/216 each) are RBT-113's O-arm command lines plus `--motor-budget 1.77`. They were
  launched at `9132b78`, on rabbitstew tree `7f4fe72`.
- **The readout was computed on a checkout of `9132b78`**, so the tree is `7f4fe72`, which K6 requires. The
  integration branch has since moved `rabbitstew/` (RBT-126, RBT-127, RBT-130), but no readout script changed
  between `9132b78` and `2be348a`. The outputs are committed on a branch cut from `2be348a`.
- **Restore.** The four B arms were restored at 216/216. **All 152 committed evidence files match the restored ones
  byte for byte.** The O arms were restored at 216/216, and `git diff --quiet -- runs/RBT-113` passes.
- **Steps, in RUNNER §6 order:**
  1. `decompose_budgeted.py` (RBT-113's `decompose.py`, unchanged, under RBT-120's `world.py`): 12 `decompose.json`
     files and `decompose.txt`.
  2. `readout.py --reference` (the frozen σ0): `readout.txt`.
  3. `budget.py`: `budget.txt`.
  4. `compare_budgeted.py`: `compare.txt`.
  5. `motor_report.py`: `motors_B.txt`.
  6. The lever probes, through `levers_budgeted.py`: `levers_{static,ghost,passive}_B.txt`.
  7. `apportion.py`: `apportion_B.txt`.
- **Budget checks (M3).** Every step on B asserted `motor_budget == 1.77`, or built its config from the seed
  directory's `config.json`.
- **The evidence that the arms ran budgeted is K1, K7 and the adversary's every-generation check [SHOULD 5]:**
  - K1: all 36 line configs carry `motor_budget` 1.77, and so do all 36 `command.txt` files;
  - K7: generation-0 rows moved at every seed;
  - `readout-adversary/m3_every_generation.txt`: 864 of 864 champions reproduce under the budget, against 524
    without it.

  K4 is an implementation check at readout: it recompiles under the run's config, so it cannot by itself detect an
  arm that ran unbudgeted.

## 2. The controls

| | result |
|---|---|
| K1 config = the O config + `motor_budget` 1.77 | PASS ×12 |
| K2 designed body byte-identical to O (every conventional lineage row, U/D/C) | PASS ×12. The designed side of every table is RBT-113's. |
| K3 same holistic founders (names, body hashes) | PASS ×12 |
| K4 every holistic `final/` member within the budget, compiled (an implementation check at readout) | PASS ×12. The budget binds on 0–55% of U members, **10–92% of D members** and 0–18% of C members. That spread is heterogeneity, not a failure: Q2 compares the budget intention-to-treat. Δb_down is larger where the budget binds more (+0.038 at the 8 seeds with ≥ 50% bound, against +0.020 at the 4 below; Spearman +0.35, p 0.26, n.s.). |
| K5 RBT-113's per-directory controls and selection checks | PASS ×12 |
| K6 the arm's `commit.txt` tree = the readout tree (`7f4fe72`) | PASS ×12 |
| K7 the clamp and cap were live: generation-0 holistic rows moved | PASS ×12. Between 7 and 18 of 40 founders moved per seed, inside probe_clamp's predicted 7–19. |

## 3. Against the registered prediction (PREREGISTRATION §6–§7)

| | predicted | observed |
|---|---|---|
| Q1 | RESPONDS, b_div_B +0.058 to +0.069, 59–70% of O, nearer 70% | **RESPONDS**, +0.0712, **73%** of O |
| Q2 | LOWERS by +0.13 to +0.18 σ0; power 0.69–1.00 | **LOWERS** by **+0.119** [+0.019, +0.219] σ0 |
| Q3 | NOT DECIDED (E d −0.16 to +0.09) | **NOT DECIDED** (d +0.126) |

**Which §7 branch [MUST 1].** The point estimate and the interval disagree, so both branches are reported.
- **By the point estimate** (73%, above 70%), the branch is "Q2 LOWERS by less than the ceiling scenario".
- **The interval covers the predicted range as well.** The share's 95% interval is [57%, 95%] (Fieller), and Δ's is
  [+0.02, +0.22] σ0; both contain the whole predicted 59–70% and +0.13 to +0.18 σ0.
- **The whole excess over 70% is the up half's non-significant +0.0056** [−0.0076, +0.0187] (p 0.38). With b_up held
  at O's value, the share would be **67%** and Δ **+0.144 σ0**, both inside the predicted range.
- **The down half fell to 51% [38%, 71%] of O's**, as §7 predicted (about a third to a half).

So the data do not separate "LOWERS within the predicted range" from "LOWERS by less than the ceiling", and no branch
is chosen on the point. **The requirements of both are met:**
- the budgeted b_div is quoted beside RBT-113's, with `apportion_*.txt`'s split (§4–§5);
- the lever report is read below, descriptively.

**The lever report, read by the registered descriptive rule [SHOULD 2, 3].**
- **Free rotors: the branch applies.** 0.92 of the budgeted D line's work, about 0.67 yield, is done on contact-free
  children (O 0.96); 0.34 is on children at least half inside their parent (O 0.39). These come from
  `levers_ghost_*.txt`, pooled, n = 36 members per group (3 per directory, one draw), with no interval.
  - **This locates the work. It does not show that free rotors cause the remaining down response.** The
    contact-free share is also 0.81–0.87 in the founders, U and C lines (O: 0.76–0.90), so the branch could hardly
    have failed to fire.
  - The informative number is the absolute one: about 0.67 yield on contact-free children in D, against about 0.02
    in C.
  - Showing cause needs the cone arm (A2), which is the registered next fix.
- **The bias walk: the registered branch does not fire.** The holistic D line's resting drive is 0.18 (O 0.24), not
  well above O's.
  - Resting drive is a share of Effectors, not of work. The work routed through biased Effectors was not measured.
  - The two means are compared without an interval.
  - 0.18 is still above the holistic U line (0.14) and C line (0.11).
  - The designed D line stays at 0.94 (it is RBT-113's line, K2).

**The D line's ceiling.** On average over directories, the budgeted D line's final work is 0.73 yield, about 86% of
its budgeted free-spin ceiling of 0.85 (`motors_B.txt`; per-directory ceilings 0.79–0.92). O's D line was at 1.58,
about 79% of its ceiling of 1.99. So on average the D line did not reach 0.99 of its ceiling in 24 generations.

## 4. The per-line lever report (R8; registered as descriptive)

**Motor capacity** (`motors_B.txt` against `motors_O.txt`; holistic, per-directory means):

| line | Σgear/(4M) B (O) | capped share B | free-spin ceiling B (O) | resting drive B (O) |
|---|---|---|---|---|
| founders | 0.62 (0.63) | 0.06 | 0.22 (0.22) | 0.00 (0.00) |
| U | 1.16 (1.17) | 0.19 | 0.57 (0.59) | 0.14 (0.13) |
| **D** | **1.60 (3.72)** | **0.59** | **0.85 (1.99)** | **0.18 (0.24)** |
| C | 0.38 (0.40) | 0.05 | 0.13 (0.14) | 0.11 (0.11) |
| designed, every line | 1.76 (1.76) | 0 | 0.97 (0.97) | D 0.94, U 0.16, C 0.20 (as O) |

- **The holistic C line's genomes are the O C line's.** The control line draws parents without regard to fitness, so
  the budget changes its scores but not its lineage.
- **So is the founders' motor capacity.**

**Food and work at generation 23** (decompose.json, 4 fixed draws; holistic):

| group | food B (O) | work B (O) | net B (O) |
|---|---|---|---|
| U | 1.224 (0.943) | 0.176 (0.160) | +1.049 (+0.782) |
| D | 0.078 (0.199) | **0.729 (1.576)** | −0.652 (−1.377) |
| C | 0.052 (0.058) | 0.020 (0.031) | +0.032 (+0.026) |

- The D line wastes less than half of its unbudgeted work, and less than the designed D line's 0.925.
- The U line still gains by moving. Its food rises 0.08 → 1.22, and U − C is 88% food. RBT-113's reading stands: it
  learns to move and eats by covering ground. B adds no smell test, and RBT-124's cone finding (scope above) bears on
  that gain directly.

**Cap and clamp, apportioned** (`apportion_B.txt` against `apportion_O.txt`; 10 members per group per directory, one
draw; work in yield, off / cap / cap + clamp):
- On O's D line, the cap does the work: 1.68 → 0.72 → 0.72.
- B's own D line is barely over its budget: 0.76 → 0.72 → 0.72.
- The clamp is negligible on D (≤ 0.003) and on the founders (0.003). On B's U line it costs net yield: +0.599 with
  the cap alone against +0.559 with cap + clamp.

**Out of scope, as registered (extras):**
- **Motors-off** (`levers_passive_B.txt`): 19 of 240 holistic bodies drift more than 0.25 m with motors zeroed
  (O 31), with no explosion.
- **Span and nodes:** `levers_static_B.txt`.

## 5. What did and did not change against RBT-113 and RBT-117

- **RBT-113's holistic RESPONDS stands, at a smaller magnitude.**
  - Under the motor budget, b_div is +0.0712 against +0.0975 at the same seeds (salt 0).
  - RBT-113's published +0.095 pooled salt 0 and salt 1. The comparable number here is the salt-0 +0.0975.
  - **Under the registered test, LOWERS.** The share removed is 27% [5%, 43%]. The descriptive split puts it in
    b_down; b_up is n.s.
- **The designed body's results are unchanged,** byte for byte (K2).
- **RBT-117's HOLISTIC RESPONDS MORE does not survive the motor budget: Q3 is NOT DECIDED.**
  - Had the margin survived, a NOT DECIDED would have come up only 4–16% of the time (power.txt, [S1]).
  - The halves: up, holistic 0.92 against designed 0.66; down, holistic 0.69 against designed 0.82. In food, U − D is
    1.15 against 1.16, a tie.
  - Either way it is not evidence for reason (b): the holistic founders are the less variable (SCOPE_4). The observed
    founder SDs over these directories are 0.219 against 0.755; these are not the frozen σ0 of 0.2212.
- **Not changed, because the budget does not reach it:**
  - free rotation on range-less joints (92% of the D line's work is done on contact-free children; descriptive);
  - the up line's coverage foraging;
  - the resting throttle of the designed D line (0.94).

## 6. `readout.py` artefacts, not registered

`readout.py` was reused unchanged, and it expects Z directories. With none present:
- its "designed body, `--global-bias-sigma 0`" group reads INCONCLUSIVE on **0 units**;
- its operator comparison reads NOT RUN.

Neither is a finding. The holistic and designed-default groups read RESPONDS. The designed default is RBT-113's own
line (K2).

**Not a new reference.** `readout.txt` also prints a `SIGMA0 REFERENCE` line computed from B (holistic 0.2187). It is
**not** a new frozen reference: every registered number here is on RBT-113's frozen 0.2212. `compare.txt`'s
"b_div (sigma0 units)" line uses per-directory SDs and is unscored.

**Header typo.** `compare.txt`'s header cites "PREREGISTRATION.md §5.3", which does not exist. Q3 is registered in §3,
and its order in §5. The line is printed by the registered `compare_budgeted.py`, which is left unchanged.

## Files

- `decompose.txt` and the 12 `B*/*/decompose.json`;
- `readout.txt`, `budget.txt`, `compare.txt`;
- `motors_B.txt`, `levers_static_B.txt`, `levers_ghost_B.txt`, `levers_passive_B.txt`, `apportion_B.txt`;
- this file.

The O baselines were committed with the design (#409).
