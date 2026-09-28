# RBT-120 readout: the holistic selection response under the motor budget

**Designer, 2026-09-28, about 01:55 UTC.** This readout was run exactly as registered (`PREREGISTRATION.md` §3–§5,
`RUNNER.md` §6). No scored code changed. It awaits a readout adversary and the coordinator's ruling.

## Headline (the registered rules' output)

| question | verdict | numbers |
|---|---|---|
| **Q1** (primary): the holistic response under the motor budget (Σgear cap 1.77 + servo clamp) | **RESPONDS** | b_div_B **+0.0712** [+0.0600, +0.0824] yield per generation = **+0.322** [+0.271, +0.373] frozen σ0; p 0.0005; 12 of 12 seeds positive |
| **Q2** (registered test): how much of RBT-113's holistic response the motor budget removed | **THE BUDGET LOWERS THE HOLISTIC RESPONSE** | Δ = b_div_O − b_div_B **+0.119** [+0.019, +0.219] σ0 per generation (+0.0263 raw); exact sign-flip p 0.019; **27%** of the O lines' +0.0975 |
| **Q3** (RBT-117's comparison, `compare.py` unchanged) | **NOT DECIDED** | d = holistic − designed final U − D **+0.126** [−0.194, +0.446] raw; p 0.40. C-line control +0.168, p 0.069: no VOID. |

**Controls:** K1–K7 **PASS at all 12 seeds** (`budget.txt`), and so do RBT-113's own controls (`readout.txt`; K5).

**Where the drop is.** It is in the down half.
- b_down fell from +0.0645 to **+0.0327** (O − B +0.0318, p 0.0015), which is **51%** of O's.
- b_up did not fall: +0.0385 against O's +0.0330 (O − B −0.0056, p 0.38).
- h2 is 0.071 against 0.091 (p 0.096).

**Scope, which binds wherever this is quoted.** This is the holistic response **without the gear allowance and the
servo wind-up**, and not without every lever.
- **The arms have no joint ranges.** Ball joints stay range-less, so limbs can still spin freely inside or through
  their parents: the cone was out of RBT-120's scope.
- RBT-124's pending pack, which is not in these arms, finds that the holistic U line's food largely rode
  free-rotating ball joints (0.98 → 0.22 under the cone).
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

## 2. The controls

| | result |
|---|---|
| K1 config = the O config + `motor_budget` 1.77 | PASS ×12 |
| K2 designed body byte-identical to O (every conventional lineage row, U/D/C) | PASS ×12. The designed side of every table is RBT-113's. |
| K3 same holistic founders (names, body hashes) | PASS ×12 |
| K4 every holistic `final/` member within the budget, compiled | PASS ×12. The budget binds on 0–55% of U members, **10–92% of D members** and 0–18% of C members. |
| K5 RBT-113's per-directory controls and selection checks | PASS ×12 |
| K6 the arm's `commit.txt` tree = the readout tree (`7f4fe72`) | PASS ×12 |
| K7 the clamp and cap were live: generation-0 holistic rows moved | PASS ×12. Between 7 and 18 of 40 founders moved per seed, inside probe_clamp's predicted 7–19. |

## 3. Against the registered prediction (PREREGISTRATION §6–§7)

| | predicted | observed |
|---|---|---|
| Q1 | RESPONDS, b_div_B +0.058 to +0.069, 59–70% of O, nearer 70% | **RESPONDS**, +0.0712, **73%** of O |
| Q2 | LOWERS by +0.13 to +0.18 σ0; power 0.69–1.00 | **LOWERS** by **+0.119** [+0.019, +0.219] σ0 |
| Q3 | NOT DECIDED (E d −0.16 to +0.09) | **NOT DECIDED** (d +0.126) |

**The registered §7 reading that applies** is "Q2 LOWERS by less than the ceiling scenario (above 70%)". The
registration says the channel is to be read from the lever report, not assumed.
- **Free rotors.** The holistic B D line does 0.92 of its work on contact-free children (O 0.96) and 0.34 on children
  at least half inside their parent (O 0.39), per `levers_ghost_*.txt` (pooled shares). That is near O's, so by the
  registered rule **free rotors carry what remains of the D line's waste, and A2's cone is the next fix.**
- **The bias walk.** The holistic D line's resting drive is 0.18 (O 0.24), per `motors_*.txt`. It did not rise, so
  the bias walk is not the channel. The designed D line stays at 0.94 (it is RBT-113's line, K2).

**A precision the §7 fork does not make:** Q1's 73% comes from the up half, not from a smaller cut to the down half.
- b_up_B is +0.0056 above O's (n.s., p 0.38).
- The down half fell to 51% of O's, between the counterfactual and ceiling scenarios.
- The budgeted D line's final work is 0.73 yield, about 86% of its budgeted free-spin ceiling of 0.85
  (`motors_B.txt`). O's D line was at 1.58, about 79% of its ceiling of 1.99.
- So the D line did not reach 0.99 of its ceiling in 24 generations.

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
  - **The motor budget removed 27% of it**, all from the down half.
- **The designed body's results are unchanged,** byte for byte (K2).
- **RBT-117's HOLISTIC RESPONDS MORE does not survive the motor budget: Q3 is NOT DECIDED.**
  - Had the margin survived, a NOT DECIDED would have come up only 4–16% of the time (power.txt, [S1]).
  - The halves: up, holistic 0.92 against designed 0.66; down, holistic 0.69 against designed 0.82. In food, U − D is
    1.15 against 1.16, a tie.
  - Either way it is not evidence for reason (b): the holistic founders are the less variable (SCOPE_4, σ0 0.219
    against 0.755).
- **Not changed, because the budget does not reach it:**
  - the free-rotor channel (92% of the D line's work on contact-free children);
  - the up line's coverage foraging;
  - the resting throttle of the designed D line (0.94).

## 6. `readout.py` artefacts, not registered

`readout.py` was reused unchanged, and it expects Z directories. With none present:
- its "designed body, `--global-bias-sigma 0`" group reads INCONCLUSIVE on **0 units**;
- its operator comparison reads NOT RUN.

Neither is a finding. The holistic and designed-default groups read RESPONDS. The designed default is RBT-113's own
line (K2).

## Files

- `decompose.txt` and the 12 `B*/*/decompose.json`;
- `readout.txt`, `budget.txt`, `compare.txt`;
- `motors_B.txt`, `levers_static_B.txt`, `levers_ghost_B.txt`, `levers_passive_B.txt`, `apportion_B.txt`;
- this file.

The O baselines were committed with the design (#409).
