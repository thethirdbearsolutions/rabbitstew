# RBT-129: readout of the designed PAYS legs (`pays-prize`, `pays-steps`)

*Rules: `READOUT-PLAN.md`, committed and pushed pre-data at `c47403c` (11:10:12Z). Integrity was committed at `8c243fe`
(11:14:24Z), before any readout number was computed. Every number below is a line of `legs_readout.txt` or
`integrity.txt`, both printed by `legs_readout.py`. The legs ran from `29ab80b`. Only the 36
`ckpt/rbt-129-stage0-pays-*` branches were read: no Stage P branch and no Stage 0 census branch.*

## Headline

**Designed PAYS holds at 4 of 18 cells: `c0-p030-HP-G`, and `PW-G` at all three clutter levels (`c0`, `c1`, `c2`).
Every one of the four is at s = G, and every one is a NOSE LEADS. No COMPARABLE was read anywhere, as RBT-125 A1.4's
power statement predicted. The HP-G call is FRAGILE.**

- **The PAYS layer is for the designed fauna only for now.** Holistic PAYS and the holistic nose step are **NOT RUN**:
  they are blocked by LEGS.md B1–B4.
- **The prize condition passes at 15 of 18 cells.** It fails at `c2-U-L`, `c2-HP-L` and `c0-PW-L`.
  **The steps condition passes at 4 of 18**, and it decides every PAYS call.
- **The speed step's own payoff at the four PAYS cells** (per-unit, at w3, t 95%):

  | cell | speed step | nose step |
  |---|---|---|
  | HP-G c0 | +0.085 [−0.308, +0.477] | +0.966 [+0.386, +1.545] |
  | PW-G c0 | −0.133 [−0.348, +0.083] | +0.571 [+0.270, +0.872] |
  | PW-G c1 | −0.024 [−0.319, +0.270] | +0.302 [+0.208, +0.396] |
  | PW-G c2 | +0.039 [−0.105, +0.182] | +0.144 [+0.053, +0.235] |

  - At all four cells the speed step's interval covers 0, so the speed step does not pay there.
  - At all four the nose step's own lower bound is > 0. So no lead is carried by a speed step that fails alone.
  - **But none of the four is a nose step matching a speed step that pays.** At PW-G c0 the speed step's point
    estimate is negative. This fits the sech² approach-gating caveat, and it matches RBT-125's PW-G2.5 pattern.
- **Robustness.** Under leave-one-out, the three PW-G calls hold. For them, the lowest prize lower bound is +0.070 and
  the lowest steps lower bound is +0.019.
  - **`c0-HP-G` is FRAGILE:** leaving out any one of 5 of its 15 hosts turns NOSE LEADS into TIED. Its steps lower
    bound ranges from −0.062 to +0.227.
  - **`c1-HP-G` (not PAYS) is also FRAGILE:** leaving out host O1/3/028 turns TIED into NOSE LEADS.
- **Caveats that go with every figure:**
  - **Pre-fairness hosts** (#443, S3). RBT-90's bests and RBT-113 O1's finals evolved with the effector-bias walk.
  - **No multiplicity correction:** none was registered, and there are 18 cells × 2 conditions.
  - **The PAYS lines at PW-G c1 and c2 rest on 8 and 7 hosts.** Seven to eight hosts leave the per-unit comparison
    at r < 1.10.
  - **U and HP ran no decoy**, so the prize there is not shown to be food-dependent.

## 1. Integrity (`integrity.txt`): PASS

- **All 18 cells are complete in each leg.** There are 180 of 180 prize ROW rows (10 populations × 18) and 54 of 54
  STEP rows (3 × 18). They were counted against each leg's `launch.txt` `cells` line, and the two legs' lists are
  identical.
  - Every prize output carries its `<seed>-<cell>` ROW, the `forage-<seed>` bodies, the cell's world, 64 seeds from
    7000 and w = 3. The decoy appears at the six PW cells and nowhere else.
  - Every steps output has the cell label, 128 seeds from 125000, and three STEP rows.
  - No `.tmp` file was left behind. Every MANIFEST reads "consistent".
- **The flags.** Both `launch.txt` files carry `--fair` and `--eat-from root --eat-rule surface`.
  - Every prize output names `runs/RBT-129/worlds/config/<cell>/config.json`. Every steps header prints
    `# fairness: 'fair'`, the same path, and a food block equal to that config at `29ab80b`.
  - All 18 of those configs have `fairness: fair`, `eat_from: root` and `eat_rule: surface`. At s = G they have
    G = 2.5 and τ = 2; at s = L, G = 0.
- **The blobs:**
  - **Pinned tools.** Every tool in `PRIZE_TOOLS` and `STEP_TOOLS` equals `git rev-parse 29ab80b:<path>`. That is
    `prize_gate.py`, `routed_populations.py`, `routed_p801.py` and `g500_direction.py`, plus `steps.py` for the steps
    leg.
  - **The unpinned RBT-97 files** (the DESIGN §12 post-hoc check). `mechanism.py` is `6eb642b` and `resign_rbt67.py`
    is `08ac982`. Each is the same at `29ab80b`, at the emit commit `61cb19b`, and at integration.
  - **The pinned trees.** The `rabbitstew/`, `scripts/` and `runs/RBT-129/launch/` trees all equal `29ab80b`'s.
- **What the branches cannot show.** The durable snapshots record no commit: MANIFEST progress is "?". So the tie
  between an output and `29ab80b` rests on three things:
  - the runners' own guards: `verify` exits 5 on a moved tree, and the runner exits 6 on a changed blob;
  - the checkout the coordinator reports;
  - the provenance headers above.
- **MuJoCo warnings.** The `.err` files hold only MuJoCo warnings: 1,653 "Nan, Inf or huge value in QACC" and 2 "EPA:
  out of memory". Every c = 0 cell's `.err` is empty. All the warnings come from the c = 1 and c = 2 terrains.

## 2. Per cell (`legs_readout.txt` §2), p = 0.03

- **prize:** RBT-106's at a = 6, over 10 populations, t(9) 95%.
- **steps:** the registered line, the w 3 → 3.4 nose step minus the per-unit +25% speed step at w3, paired per host,
  t 95%. The reading is `steps.py`'s.
- **Printed beside it:** the nose step's own payoff and **the speed step's own payoff** (coordinator, 08:10).

| cell | prize [t(9) 95%] | LB > 0 | nose − speed (n) | reading | nose step w3→3.4 | **speed step, per-unit @w3 (n)** | raw speed @w3 (net) | r@w3 (range; out) | **PAYS** |
|---|---|---|---|---|---|---|---|---|---|
| c0-U-L | +0.224 [+0.074, +0.375] | yes | −0.389 [−0.626, −0.153] (14) | SPEED LEADS | −0.027 [−0.110, +0.056] | +0.362 [+0.119, +0.606] (14) | +0.450 (+0.307) | 1.30 (1.19–1.56; 0) | no |
| c1-U-L | +0.102 [+0.012, +0.192] | yes | −0.172 [−0.269, −0.076] (10) | SPEED LEADS | −0.019 [−0.062, +0.024] | +0.145 [+0.024, +0.265] (10) | +0.155 (+0.014) | 1.18 (0.57–1.63; 4) | no |
| c2-U-L | +0.043 [−0.015, +0.102] | no | −0.104 [−0.234, +0.026] (10) | TIED | −0.003 [−0.058, +0.052] | +0.108 [−0.030, +0.246] (10) | +0.083 (−0.056) | 1.16 (0.52–1.47; 4) | no |
| c0-U-G | +1.070 [+0.637, +1.502] | yes | −0.060 [−0.396, +0.277] (15) | TIED | +0.388 [+0.117, +0.659] | **+0.448 [+0.209, +0.687]** (15) | +0.441 (+0.312) | 1.26 (1.17–1.38; 0) | no |
| c1-U-G | +0.531 [+0.304, +0.759] | yes | +0.052 [−0.112, +0.216] (13) | TIED | +0.132 [−0.011, +0.274] | +0.051 [−0.099, +0.201] (13) | +0.033 (−0.095) | 1.19 (1.06–1.45; 2) | no |
| c2-U-G | +0.307 [+0.185, +0.430] | yes | −0.004 [−0.166, +0.157] (7) | TIED | +0.116 [+0.038, +0.194] | +0.106 [−0.070, +0.282] (7) | +0.108 (−0.022) | 2.10 (0.53–16.35; 8) | no |
| c0-HP-L | +0.306 [+0.153, +0.458] | yes | −0.458 [−0.751, −0.165] (15) | SPEED LEADS | +0.034 [−0.099, +0.167] | +0.492 [+0.222, +0.762] (15) | +0.568 (+0.424) | 1.30 (1.18–1.49; 0) | no |
| c1-HP-L | +0.179 [+0.112, +0.246] | yes | −0.192 [−0.379, −0.006] (13) | SPEED LEADS | +0.055 [−0.074, +0.184] | +0.284 [+0.073, +0.496] (13) | +0.242 (+0.104) | 2.84 (0.24–25.67; 2) | no |
| c2-HP-L | +0.056 [−0.024, +0.135] | no | −0.189 [−0.368, −0.010] (9) | SPEED LEADS | +0.005 [−0.084, +0.094] | +0.208 [+0.009, +0.407] (9) | +0.139 (+0.003) | 64.00 (0.01–943.45; 6) | no |
| **c0-HP-G** | +1.882 [+0.765, +3.000] | yes | +0.881 [+0.079, +1.683] (15) | **NOSE LEADS** | +0.966 [+0.386, +1.545] | +0.085 [−0.308, +0.477] (15) | −0.041 (−0.169) | 1.27 (1.19–1.38; 0) | **PAYS (FRAGILE)** |
| c1-HP-G | +1.013 [+0.486, +1.540] | yes | +0.419 [−0.034, +0.872] (9) | TIED | +0.617 [+0.391, +0.844] | +0.200 [−0.163, +0.563] (9) | +0.132 (+0.004) | 1.11 (0.50–1.56; 6) | no (FRAGILE) |
| c2-HP-G | +0.717 [+0.340, +1.094] | yes | +0.160 [−0.054, +0.375] (7) | TIED | +0.248 [+0.151, +0.345] | +0.169 [−0.104, +0.442] (7) | +0.052 (−0.078) | 1.08 (0.78–1.56; 8) | no |
| c0-PW-L | +0.093 [−0.062, +0.248] | no | −0.250 [−0.479, −0.022] (14) | SPEED LEADS | −0.052 [−0.163, +0.059] | +0.198 [−0.052, +0.449] (14) | +0.243 (+0.099) | 1.29 (1.21–1.56; 0) | no |
| c1-PW-L | +0.087 [+0.040, +0.135] | yes | −0.035 [−0.177, +0.107] (9) | TIED | −0.061 [−0.140, +0.018] | −0.032 [−0.183, +0.119] (9) | +0.061 (−0.075) | 1.18 (0.94–1.81; 5) | no |
| c2-PW-L | +0.071 [+0.007, +0.136] | yes | −0.104 [−0.237, +0.028] (9) | TIED | −0.015 [−0.101, +0.071] | +0.071 [−0.014, +0.157] (9) | +0.043 (−0.090) | 1.17 (0.36–2.32; 5) | no |
| **c0-PW-G** | +0.785 [+0.200, +1.370] | yes | +0.704 [+0.281, +1.127] (15) | **NOSE LEADS** | +0.571 [+0.270, +0.872] | −0.133 [−0.348, +0.083] (15) | −0.179 (−0.308) | 1.26 (1.18–1.38; 0) | **PAYS** |
| **c1-PW-G** | +0.580 [+0.304, +0.857] | yes | +0.388 [+0.097, +0.679] (8) | **NOSE LEADS** | +0.302 [+0.208, +0.396] | −0.024 [−0.319, +0.270] (8) | +0.032 (−0.097) | 16.79 (0.51–236.83; 7) | **PAYS** |
| **c2-PW-G** | +0.500 [+0.315, +0.686] | yes | +0.210 [+0.078, +0.343] (7) | **NOSE LEADS** | +0.144 [+0.053, +0.235] | +0.039 [−0.105, +0.182] (7) | +0.005 (−0.121) | 1.08 (0.44–1.45; 8) | **PAYS** |

**The decoy, at the PW cells only.** (motif − decoy), t(9) 95%, is descriptive:

| cell | motif − decoy |
|---|---|
| c0-PW-G | +0.808 [+0.312, +1.304] |
| c1-PW-G | +0.605 [+0.395, +0.815] |
| c2-PW-G | +0.504 [+0.359, +0.650] |
| c0-PW-L | +0.126 [−0.006, +0.258] |
| c1-PW-L | +0.096 [+0.030, +0.161] |
| c2-PW-L | +0.077 [+0.031, +0.122] |

- All three PW-G PAYS calls have a food-dependent prize by this measure.
- No plan flag fired:
  - "lead carried by the speed step" (per-unit speed upper bound < 0, or nose lower bound ≤ 0) fired nowhere;
  - "not shown food-dependent" fired at no PAYS cell with a decoy.

The w1 and first-nose readings, the raw-speed readings, the installed a = 6 step, the signed counts and the
per-population prizes are in `legs_readout.txt` §2.

### Marginals (descriptive; `legs_readout.txt` §2b)

| factor | level | PAYS | prize LB > 0 | NOSE LEADS / COMPARABLE / TIED / SPEED LEADS | mean prize | mean (nose − speed) | mean per-unit speed step |
|---|---|---|---|---|---|---|---|
| L | U | 0/6 | 5 | 0 / 0 / 4 / 2 | +0.380 | −0.113 | +0.203 |
| L | HP | 1/6 | 5 | 1 / 0 / 2 / 3 | +0.692 | +0.103 | +0.240 |
| L | PW | 3/6 | 5 | 3 / 0 / 2 / 1 | +0.353 | +0.152 | +0.020 |
| s | L | 0/9 | 6 | 0 / 0 / 3 / 6 | +0.129 | −0.210 | +0.204 |
| s | G | 4/9 | 9 | 4 / 0 / 5 / 0 | +0.821 | +0.306 | +0.105 |
| c | c0 | 2/6 | 5 | 2 / 0 / 1 / 3 | +0.727 | +0.071 | +0.242 |
| c | c1 | 1/6 | 6 | 1 / 0 / 3 / 2 | +0.416 | +0.077 | +0.104 |
| c | c2 | 1/6 | 4 | 1 / 0 / 4 / 1 | +0.283 | −0.005 | +0.117 |
| all | | 4/18 | 15 | 4 / 0 / 8 / 6 | +0.475 | +0.048 | +0.154 |

**Read descriptively:**
- **The smell reading separates the steps condition cleanly.**
  - Every SPEED LEADS (6) is at s = L, where a +25% speed step pays at c0 in every layout: U +0.362, HP +0.492 and PW
    +0.198 (the last with its interval covering 0).
  - Every NOSE LEADS (4) is at s = G.
  - No s = L cell pays.
- **Under s = G, the speed step collapses where the layout rewards steering, and not in U.**
  - At c0, the per-unit speed step is +0.448 [+0.209, +0.687] in U-G, +0.085 in HP-G and −0.133 in PW-G.
  - In U-G the nose step pays (+0.388 [+0.117, +0.659]), but so does speed, and the line reads TIED.
  - This is the coordinator's 08:10 point, seen per cell: **HP-G and PW-G lead partly because speed stops paying
    there.** Each nose step's own lower bound is still > 0.
- **Clutter lowers everything.** The mean prize is +0.727 at c0, +0.416 at c1 and +0.283 at c2.
  - At c ≥ 1, the realised speed ratio becomes erratic: r reaches 943 at c2-HP-L, and 0.01 at the bottom of the same
    range. This points to hosts that barely move in one arm.
  - That erratic r sends 2–8 of 15 hosts out of the per-unit comparison at r < 1.10.
  - The MuJoCo QACC warnings come only from c ≥ 1.
  - So the c ≥ 1 lines rest on fewer, and more erratically rescaled, hosts.

## 3. Holistic PAYS and the holistic nose step: NOT RUN

They are blocked by LEGS.md B1–B4:
- `steer.py` refuses τ = 2 and RBT-129's points;
- there are no draw pools;
- the G8(c) planter and a holistic step harness are not in the tree;
- the probe members wait on Stage P.

**So PAYS is a designed-fauna layer only.** Every cross-tab cell of §6.3 for the holistic fauna is empty until those
legs run.

## 4. Descriptive comparison with RBT-125's gate (`legs_readout.txt` §4; no verdicts)

RBT-125 ran the committed eating rule, without `--fair`, on RBT-90's random terrain. The cells here run the sweep's
block. G2.5 is matched to s = G, and G0 to s = L. No cell here is an exact match for the gate: c0 is the nearest
clutter level.
- **The prize at c0 is higher than the gate's in U and HP,** paired by population:
  - U-G, c0 − gate: +0.573 [+0.327, +0.819];
  - HP-G: +0.920 [+0.308, +1.532];
  - U-L: +0.123 [+0.019, +0.227].
- **In PW the difference is unresolved:** PW-G +0.171 [−0.121, +0.463]; PW-L −0.032 [−0.148, +0.084].
- **Across layouts,** the prizes are near the gate's at c1, and below it in every layout at c2.
- **The §B line in PW:**
  - At G2.5 the gate read +0.317 [+0.032, +0.602] (13), NOSE LEADS, with a per-unit speed step of −0.075. PW-G here
    reads NOSE LEADS at all three c. At c0 it is +0.704, with speed at −0.133. Paired here − gate at c0 it is
    +0.440 [+0.101, +0.778] (13 hosts).
  - At G0 the gate read SPEED LEADS (−0.266); c0-PW-L reads SPEED LEADS (−0.250), paired difference
    +0.003 [−0.220, +0.225].
- **Nothing here is tested, and nothing re-reads RBT-125.** The worlds differ in the eating rule, `--fair`, the
  terrain and the motor budget together, so no difference is attributed to any one of them.

## 5. Robustness (`legs_readout.txt` §5)

- **The check against the tool.** The registered line, recomputed from each steps output's per-host table (3-decimal
  inputs), reproduces every STEP row's interval to within 0.001, with the same reading and the same n.
  - At `c1-HP-G` and `c1-PW-G`, one host's r is printed as 1.100. `steps.py` excluded it, because its true value is
    below 1.10. The recompute drops it to match the printed n, and says so.

**Leave one out.** Prize: leave one population out, t(8). Steps: leave one host out, t(n − 2).

| cell | PAYS | prize LB range (min at) | steps LB range | readings reached | call flips? |
|---|---|---|---|---|---|
| c0-HP-G | PAYS | +0.521 .. +1.083 (805) | **−0.062 .. +0.227** | NOSE LEADS, TIED | **FRAGILE:** omitting O1/2/003, O1/2/029, O1/3/009, O1/3/023 or O1/3/031 gives TIED |
| c1-HP-G | no | +0.381 .. +0.706 (805) | −0.142 .. **+0.073** | NOSE LEADS, TIED | **FRAGILE:** omitting O1/3/028 gives NOSE LEADS, and so PAYS |
| c0-PW-G | PAYS | +0.070 .. +0.306 (805) | +0.211 .. +0.331 | NOSE LEADS | no |
| c1-PW-G | PAYS | +0.243 .. +0.369 (805) | +0.019 .. +0.140 | NOSE LEADS | no |
| c2-PW-G | PAYS | +0.274 .. +0.352 (7) | +0.037 .. +0.186 | NOSE LEADS | no |

- **At five non-PAYS cells the prize condition alone flips under one omission:** c1-U-L, c2-U-L, c2-HP-L, c0-PW-L
  and c2-PW-L.
  - Their steps condition fails in every leave-one-out, so the PAYS call does not change.
  - These prizes sit near 0, with lower bounds within ±0.10 of it.
- **So, of the 18 PAYS calls, 16 are stable under a single omission, and 2 (both HP-G) are fragile.** The PW-G row is
  robust at every clutter level, although c1's lowest steps lower bound is only +0.019.

## What this licenses, and what it does not

**Licensed:** under the sweep's block (the fair set, root + surface eating), RBT-106's prize at a = 6 and a one-σ nose
step at the w3 rung meet the registered designed PAYS rule:
- in PW-G at c = 0, 1 and 2, robustly;
- in HP-G at c = 0, fragile to one host.

**Licensed:** no s = L cell pays.
- At all six s = L cells at c ≤ 1, a +25% speed step leads or ties the nose step.
- The legacy reading pays speed over noses in these hosts, as RBT-125 §B found in PW-G0.

**Not licensed:**
- **That the nose step pays in absolute terms "comparably to a speed step that pays."** At all four PAYS cells the
  speed step does not pay (its intervals cover 0, and its point estimate is negative at PW-G c0 and c1). The PAYS calls rest on
  nose steps with lower bounds > 0, set against collapsed speed steps.
- **That the path from no compass pays.** The first-nose and w1 lines read TIED at every PAYS cell. This is RBT-125's
  pass-2 point again: the step path is shown from an installed compass, not from none.
- **A holistic statement of any kind.**
- **Claims for evolved bodies under the fair set.** The hosts are pre-fairness (#443, S3).
- **Any claim of equivalence.** No COMPARABLE was read. That is a power result.

## Files

| file | what |
|---|---|
| `READOUT-PLAN.md` | the pre-data plan (`c47403c`) |
| `legs_readout.py` | reads the 36 branches; `integrity` → `integrity.txt`, `readout` → `legs_readout.txt`. It refuses to read unless integrity passes |
| `integrity.txt` | step 1: blobs, trees, flags, configs, completeness, provenance, `.err` kinds |
| `legs_readout.txt` | steps 2–5: per cell, marginals, the RBT-125 comparison, the leave-one-out results, the computed headline |

Reproduce:

```
git fetch origin '+refs/heads/ckpt/rbt-129-stage0-pays-*:refs/remotes/origin/ckpt/rbt-129-stage0-pays-*'
python runs/RBT-129/legs-readout/legs_readout.py integrity > runs/RBT-129/legs-readout/integrity.txt
python runs/RBT-129/legs-readout/legs_readout.py readout > runs/RBT-129/legs-readout/legs_readout.txt
```

This needs numpy only.
