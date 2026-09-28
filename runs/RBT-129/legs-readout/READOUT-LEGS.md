# RBT-129: readout of the designed PAYS legs (`pays-prize`, `pays-steps`)

*Rules: `READOUT-PLAN.md`, committed and pushed pre-data at `c47403c` (11:10:12Z). Integrity was committed at `8c243fe`
(11:14:24Z), before any readout number was computed. First readout: `92f1baf`. **Revised under the coordinator's ruling
of 12:58 on #467** (comment 5870339780), after the adversary's report #473 (`runs/RBT-129/legs-readout-adversary/`,
CONFIRMED WITH CAVEATS). Nothing new was run for the revision.*

*Every number below is a line of `legs_readout.txt` or `integrity.txt`, both printed by `legs_readout.py`, except the
adversary's explosion-free diagnostic, which is cited from its own files and marked as such. The legs ran from `29ab80b`
(both `launch.txt` files record their emit commit, `61cb19b`, which is an ancestor with identical content; see §1).
Only the 36 `ckpt/rbt-129-stage0-pays-*` branches were read: no Stage P branch and no Stage 0 census branch.*

## Headline

**Designed PAYS is decided only at c = 0, and holds at 2 of those 6 cells: `c0-p030-PW-G`, and `c0-p030-HP-G`, which
is FRAGILE and has no decoy check. At all 12 c ≥ 1 cells designed PAYS is UNDECIDED.** There the steps condition is
NOT READABLE, because its input is contaminated: exploded seasons drive A1.4's realised-speed ratio r (ruling of
12:58; adversary #473, MUST 1). The steps leg is to be re-run at those cells on fresh seeds, with exploded seeds dropped
from both arms.

- **The PAYS layer is for the designed fauna only for now.** Holistic PAYS and the holistic nose step are **NOT RUN**:
  they are blocked by LEGS.md B1–B4.
- **The c = 0 calls, as computed and ruled:**

  | cell | call |
  |---|---|
  | c0-PW-G | **PAYS** |
  | c0-HP-G | **PAYS**, FRAGILE, no decoy |
  | c0-U-L, c0-U-G, c0-HP-L, c0-PW-L | not PAYS |

- **Withdrawn:** the first readout's PAYS calls at c1-PW-G and c2-PW-G. They were computed under the registered rule
  on an explosion-contaminated r, and are now UNDECIDED. c2-HP-G is not promoted either.
- **The prize condition stands at all 18 cells.** Its lower bound is > 0 at 15 and fails at c2-U-L, c2-HP-L and
  c0-PW-L. Explosions touch the prize in at most 1% of its seasons, balanced between the arms, and in none at c = 0
  (#473 §2).
- **The speed step's own payoff at the two PAYS cells** (per-unit, at w3, t 95%):

  | cell | speed step | nose step |
  |---|---|---|
  | c0-HP-G | +0.085 [−0.308, +0.477] | +0.966 [+0.386, +1.545] |
  | c0-PW-G | −0.133 [−0.348, +0.083] | +0.571 [+0.270, +0.872] |

  - At both cells the speed step does not pay: its interval covers 0.
  - At both, the nose step pays on its own, with a lower bound > 0.
  - **So each NOSE LEADS is a nose step that pays, set against a speed step that does not** (the coordinator's 08:10
    point). Neither is a nose step matching a speed step that pays.
- **No COMPARABLE on the registered (per-unit) line** at any cell. This is a power result, as A1.4 predicted. The raw
  line, which is descriptive, reads COMPARABLE at c2-U-G (+0.007 [−0.070, +0.084]).
- **The caveats that go with every figure:**
  - **Pre-fairness hosts** (#443, S3): RBT-90's bests and RBT-113 O1's finals evolved with the effector-bias walk.
  - **No multiplicity correction:** none is registered (18 cells × 2 conditions).
  - **U and HP ran no decoy**, so the prize there is not shown to be food-dependent. That includes c0-HP-G's PAYS.

### Where "at least comparably" = NOSE LEADS or COMPARABLE comes from (#473, SHOULD 1)

- **RBT-129's DESIGN** (§5.1, §6.3) gives only RBT-121 R4's words, "pays at least comparably to a speed step". It does
  not name labels.
- **The labels, their order and the registered line** are RBT-125 REGISTRATION A1.4's.
- **The mapping onto the labels** comes from three reports, all on record before the data:
  - RBT-125 ADVERSARY-PASS2 §3, "For RBT-129's PAYS rule (COMPARABLE or NOSE)". Its author says this restated the
    coordinator's brief; it was not a ruling.
  - RBT-116 ADVERSARY-RBT132 S7(b), for the holistic leg's test: "not stricter than the designed leg".
  - RBT-125 READOUT-BC §B scope, as amended under the coordinator's ruling.
- The adversary found this mapping consistent and proposed no other reading, and the coordinator accepted the calls
  under it.

## 1. Integrity (`integrity.txt`): PASS

- **All 18 cells are complete in each leg.** There are 180 of 180 prize ROW rows (10 populations × 18) and 54 of 54
  STEP rows (3 × 18). They were counted against each leg's `launch.txt` `cells` line, and the two legs' lists are
  identical.
  - Every prize output carries its `<seed>-<cell>` ROW, the `forage-<seed>` bodies, the cell's world, 64 seeds from
    7000 and w = 3. The decoy appears at the six PW cells and nowhere else.
  - Every steps output has the cell label, 128 seeds from 125000 and three STEP rows.
  - No `.tmp` file was left behind. Every MANIFEST reads "consistent".
- **The flags.** Both `launch.txt` files carry `--fair` and `--eat-from root --eat-rule surface`.
  - Every prize output names `runs/RBT-129/worlds/config/<cell>/config.json`. Every steps header prints
    `# fairness: 'fair'`, the same path, and a food block equal to that config at `29ab80b`.
  - All 18 configs have `fairness: fair`, `eat_from: root` and `eat_rule: surface`. At s = G they have G = 2.5 and
    τ = 2; at s = L, G = 0.
- **The blobs:**
  - **Pinned tools.** Every tool in `PRIZE_TOOLS` and `STEP_TOOLS` equals `git rev-parse 29ab80b:<path>`.
  - **The unpinned RBT-97 files** (the DESIGN §12 post-hoc check). `mechanism.py` (`6eb642b`) and `resign_rbt67.py`
    (`08ac982`) are each the same at `29ab80b`, at `61cb19b` and at integration.
  - **The pinned trees.** The `rabbitstew/`, `scripts/` and `runs/RBT-129/launch/` trees all equal `29ab80b`'s.
- **Which commit the legs name (#473, NIT 2).** Both `launch.txt` files record `commit 61cb19b`, the commit the legs
  were emitted on. `29ab80b` is its child, which re-emitted the lanes. Every pinned tree and blob is identical at the
  two, so "ran from `29ab80b`" and "`launch.txt` records `61cb19b`" describe the same code.
- **What the branches cannot show.** The durable snapshots record no commit: MANIFEST progress is "?". So the tie
  between an output and `29ab80b` rests on three things:
  - the runners' own guards: `verify` exits 5 on a moved tree, and the runner exits 6 on a changed blob;
  - the checkout the coordinator reports;
  - the provenance headers above.
- **MuJoCo warnings.** The `.err` files hold only MuJoCo warnings: 1,653 "Nan, Inf or huge value in QACC" and 2 "EPA:
  out of memory". Every c = 0 cell's `.err` is empty.
  - The first readout called these harmless noise. They are not: they are integrator blow-ups, and at c ≥ 1 they
    decide r (§2a).

## 2. Per cell (`legs_readout.txt` §2), p = 0.03

- **prize:** RBT-106's at a = 6, over 10 populations, t(9) 95%.
- **steps:** the registered line, the w 3 → 3.4 nose step minus the per-unit +25% speed step at w3, paired per host,
  t 95%. The reading is `steps.py`'s.
- **"as computed"** is the registered rule applied to the legs' output. **"ruled call"** applies the 12:58 ruling.
- **At c ≥ 1** the steps columns are printed for description only (NOT READABLE).
- **The raw-line reading** (A1.4, descriptive) is printed beside every call (#473, SHOULD 3).

| cell | prize [t(9) 95%] | LB > 0 | nose − speed, per-unit (n) | reading | raw line | nose step w3→3.4 | **speed step, per-unit @w3 (n)** | raw speed @w3 (net) | r@w3 (range; out) | as computed | **ruled call** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| c0-U-L | +0.224 [+0.074, +0.375] | yes | −0.389 [−0.626, −0.153] (14) | SPEED LEADS | SPEED LEADS | −0.027 [−0.110, +0.056] | +0.362 [+0.119, +0.606] (14) | +0.450 (+0.307) | 1.30 (1.19–1.56; 0) | no | **not PAYS** |
| c1-U-L | +0.102 [+0.012, +0.192] | yes | *−0.172 [−0.269, −0.076] (10)* | *SPEED LEADS* | SPEED LEADS | −0.019 [−0.062, +0.024] | *+0.145 [+0.024, +0.265] (10)* | +0.155 (+0.014) | 1.18 (0.57–1.63; 4) | no | **UNDECIDED** |
| c2-U-L | +0.043 [−0.015, +0.102] | no | *−0.104 [−0.234, +0.026] (10)* | *TIED* | SPEED LEADS | −0.003 [−0.058, +0.052] | *+0.108 [−0.030, +0.246] (10)* | +0.083 (−0.056) | 1.16 (0.52–1.47; 4) | no | **UNDECIDED** |
| c0-U-G | +1.070 [+0.637, +1.502] | yes | −0.060 [−0.396, +0.277] (15) | TIED | TIED | +0.388 [+0.117, +0.659] | **+0.448 [+0.209, +0.687]** (15) | +0.441 (+0.312) | 1.26 (1.17–1.38; 0) | no | **not PAYS (unresolved)** |
| c1-U-G | +0.531 [+0.304, +0.759] | yes | *+0.052 [−0.112, +0.216] (13)* | *TIED* | TIED | +0.132 [−0.011, +0.274] | *+0.051 [−0.099, +0.201] (13)* | +0.033 (−0.095) | 1.19 (1.06–1.45; 2) | no | **UNDECIDED** |
| c2-U-G | +0.307 [+0.185, +0.430] | yes | *−0.004 [−0.166, +0.157] (7)* | *TIED* | **COMPARABLE** | +0.116 [+0.038, +0.194] | *+0.106 [−0.070, +0.282] (7)* | +0.108 (−0.022) | 2.10 (0.53–16.35; 8) | no | **UNDECIDED** |
| c0-HP-L | +0.306 [+0.153, +0.458] | yes | −0.458 [−0.751, −0.165] (15) | SPEED LEADS | SPEED LEADS | +0.034 [−0.099, +0.167] | +0.492 [+0.222, +0.762] (15) | +0.568 (+0.424) | 1.30 (1.18–1.49; 0) | no | **not PAYS** |
| c1-HP-L | +0.179 [+0.112, +0.246] | yes | *−0.192 [−0.379, −0.006] (13)* | *SPEED LEADS* | SPEED LEADS | +0.055 [−0.074, +0.184] | *+0.284 [+0.073, +0.496] (13)* | +0.242 (+0.104) | 2.84 (0.24–25.67; 2) | no | **UNDECIDED** |
| c2-HP-L | +0.056 [−0.024, +0.135] | no | *−0.189 [−0.368, −0.010] (9)* | *SPEED LEADS* | SPEED LEADS | +0.005 [−0.084, +0.094] | *+0.208 [+0.009, +0.407] (9)* | +0.139 (+0.003) | 64.00 (0.01–943.45; 6) | no | **UNDECIDED** |
| **c0-HP-G** | +1.882 [+0.765, +3.000] | yes | +0.881 [+0.079, +1.683] (15) | **NOSE LEADS** | NOSE LEADS | +0.966 [+0.386, +1.545] | +0.085 [−0.308, +0.477] (15) | −0.041 (−0.169) | 1.27 (1.19–1.38; 0) | PAYS | **PAYS (FRAGILE; no decoy)** |
| c1-HP-G | +1.013 [+0.486, +1.540] | yes | *+0.419 [−0.034, +0.872] (9)* | *TIED* | NOSE LEADS | +0.617 [+0.391, +0.844] | *+0.200 [−0.163, +0.563] (9)* | +0.132 (+0.004) | 1.11 (0.50–1.56; 6) | no | **UNDECIDED** |
| c2-HP-G | +0.717 [+0.340, +1.094] | yes | *+0.160 [−0.054, +0.375] (7)* | *TIED* | NOSE LEADS | +0.248 [+0.151, +0.345] | *+0.169 [−0.104, +0.442] (7)* | +0.052 (−0.078) | 1.08 (0.78–1.56; 8) | no | **UNDECIDED** |
| c0-PW-L | +0.093 [−0.062, +0.248] | no | −0.250 [−0.479, −0.022] (14) | SPEED LEADS | SPEED LEADS | −0.052 [−0.163, +0.059] | +0.198 [−0.052, +0.449] (14) | +0.243 (+0.099) | 1.29 (1.21–1.56; 0) | no | **not PAYS** |
| c1-PW-L | +0.087 [+0.040, +0.135] | yes | *−0.035 [−0.177, +0.107] (9)* | *TIED* | TIED | −0.061 [−0.140, +0.018] | *−0.032 [−0.183, +0.119] (9)* | +0.061 (−0.075) | 1.18 (0.94–1.81; 5) | no | **UNDECIDED** |
| c2-PW-L | +0.071 [+0.007, +0.136] | yes | *−0.104 [−0.237, +0.028] (9)* | *TIED* | TIED | −0.015 [−0.101, +0.071] | *+0.071 [−0.014, +0.157] (9)* | +0.043 (−0.090) | 1.17 (0.36–2.32; 5) | no | **UNDECIDED** |
| **c0-PW-G** | +0.785 [+0.200, +1.370] | yes | +0.704 [+0.281, +1.127] (15) | **NOSE LEADS** | NOSE LEADS | +0.571 [+0.270, +0.872] | −0.133 [−0.348, +0.083] (15) | −0.179 (−0.308) | 1.26 (1.18–1.38; 0) | PAYS | **PAYS** |
| c1-PW-G | +0.580 [+0.304, +0.857] | yes | *+0.388 [+0.097, +0.679] (8)* | *NOSE LEADS* | NOSE LEADS | +0.302 [+0.208, +0.396] | *−0.024 [−0.319, +0.270] (8)* | +0.032 (−0.097) | 16.79 (0.51–236.83; 7) | PAYS (withdrawn) | **UNDECIDED** |
| c2-PW-G | +0.500 [+0.315, +0.686] | yes | *+0.210 [+0.078, +0.343] (7)* | *NOSE LEADS* | NOSE LEADS | +0.144 [+0.053, +0.235] | *+0.039 [−0.105, +0.182] (7)* | +0.005 (−0.121) | 1.08 (0.44–1.45; 8) | PAYS (withdrawn) | **UNDECIDED** |

*Italics:* the per-unit line at c ≥ 1, NOT READABLE under the ruling and printed for description only.

**The decoy, at the PW cells only.** (motif − decoy), t(9) 95%, is descriptive:

| cell | motif − decoy |
|---|---|
| c0-PW-G | +0.808 [+0.312, +1.304] |
| c1-PW-G | +0.605 [+0.395, +0.815] |
| c2-PW-G | +0.504 [+0.359, +0.650] |
| c0-PW-L | +0.126 [−0.006, +0.258] |
| c1-PW-L | +0.096 [+0.030, +0.161] |
| c2-PW-L | +0.077 [+0.031, +0.122] |

- c0-PW-G's prize is food-dependent by this measure.
- **c0-HP-G's prize has no decoy check** (#473, NIT 1).

**"not PAYS" at a TIED cell means unresolved** (#473, SHOULD 2). It does not mean a world where the nose step does not
pay.
- **c0-U-G** is the one decided cell like this. Both steps pay there: the nose step +0.388 [+0.117, +0.659] and the
  speed step +0.448 [+0.209, +0.687]. The line reads TIED at a 90% half-width of about 0.28, against δ = 0.10. That is
  a power result.
- §6.3's "not PAYS, and NONE: the expected result in a coverage world" must not be read into c0-U-G as a finding about
  the world. The same holds for any TIED cell once the re-run is read.
- The three decided not-PAYS cells at s = L (c0-U-L, c0-HP-L, c0-PW-L) read SPEED LEADS, a resolved reading.

**The raw line against the per-unit line** (#473, SHOULD 3). It is descriptive, and it shows which calls depend on the
per-unit rescaling:
- **At the two decided PAYS cells the raw line agrees:** both read NOSE LEADS.
- **At c ≥ 1 the raw line reads NOSE LEADS at c1-HP-G and c2-HP-G, and COMPARABLE at c2-U-G,** where the per-unit line
  reads TIED. All three are UNDECIDED under the ruling. The raw line does not decide anything.

The w1 and first-nose readings, the installed a = 6 step, the signed counts and the per-population prizes are in
`legs_readout.txt` §2. At both PAYS cells the first nose and w 1 → 1.4 read TIED.

### 2a. Why c ≥ 1 is NOT READABLE (#473 §3; the ruling)

- **A1.4's r is a ratio of mean centre-of-mass path over whole seasons, exploded seasons included.** At c ≥ 1, 10 to
  15 of 15 hosts per cell have at least one exploded season. One explosion moves r to about 0 or into the hundreds.
  - On the extreme host, c2-HP-L O1/1/016, r = 943.448 comes from one season, whose centre of mass moved at 52,340 m/s.
    Without the exploded seasons, its r is 1.266 (`legs-readout-adversary/probe_r_outlier.txt`).
- **The RBT-30 precedent is that an exploded season is not a measurement of the body.** So at c ≥ 1 the input to the
  per-unit line is not a measurement.
- **The adversary's explosion-free r is cited as descriptive only.** It was computed on the same seasons after the data
  were seen, and the coordinator did not adopt it (`r_clean_summary.md`). At five c ≥ 1 cells it gives:

  | cell | explosion-free line |
  |---|---|
  | c1-PW-G | +0.216 [+0.000, +0.432] (12), NOSE LEADS |
  | c2-PW-G | +0.096 [−0.130, +0.321] (8), TIED |
  | c2-HP-G | +0.267 [+0.007, +0.527] (10), NOSE LEADS |
  | c1-HP-G | TIED |
  | c2-U-G | TIED |

  It flips calls in both directions. It decides nothing.
- **The exclusion at r < 1.10 is not a neutral filter at c ≥ 1** (#473, SHOULD 4; `legs_readout.txt` §2c). At the
  c ≥ 1 G cells, compare the mean w3 → 3.4 nose step of the hosts excluded with that of the hosts kept:

  | cell | excluded (n) | kept (n) |
  |---|---|---|
  | c1-PW-G | +0.232 (7) | +0.363 (8) |
  | c2-PW-G | +0.052 (8) | +0.249 (7) |
  | c2-HP-G | +0.177 (8) | +0.329 (7) |
  | c1-HP-G | +0.615 (6) | +0.619 (9) |
  | c1-U-G | +0.316 (2) | +0.103 (13) |
  | c2-U-G | +0.128 (8) | +0.102 (7) |

  - At the three cells in the first rows (c1-PW-G, c2-PW-G, c2-HP-G), the excluded hosts had smaller nose steps.
  - At c1-HP-G the two groups are equal. At c1-U-G and c2-U-G the excluded hosts had larger nose steps.
  - So the direction is not uniform, but the filter does move the line, and explosions partly drive it.
- **The registered re-measurement (ruling of 12:58).**
  - The steps leg is re-run at the 12 c ≥ 1 cells on fresh seeds starting at 126000, with the same hosts, configs and
    flags.
  - Exploded seeds are dropped from both arms of each comparison, and r is taken over the remaining paired seeds.
  - A host with more than 25% of its paired seeds exploded leaves the line.
  - Everything else in A1.4 is unchanged.
  - Designed PAYS at c ≥ 1 is then read from that line with this readout's prize condition, under this plan.
  - The c = 0 cells are not re-run.

### Marginals (descriptive; `legs_readout.txt` §2b)

| factor | level | PAYS (ruled) | UNDECIDED | PAYS (as computed) | prize LB > 0 | mean prize |
|---|---|---|---|---|---|---|
| L | U | 0/6 | 4 | 0 | 5 | +0.380 |
| L | HP | 1/6 | 4 | 1 | 5 | +0.692 |
| L | PW | 1/6 | 4 | 3 | 5 | +0.353 |
| s | L | 0/9 | 6 | 0 | 6 | +0.129 |
| s | G | 2/9 | 6 | 4 | 9 | +0.821 |
| c | c0 | 2/6 | 0 | 2 | 5 | +0.727 |
| c | c1 | 0/6 | 6 | 1 | 6 | +0.416 |
| c | c2 | 0/6 | 6 | 1 | 4 | +0.283 |
| all | | 2/18 | 12 | 4 | 15 | +0.475 |

**At c = 0 (decided):**
- **Speed pays under the legacy reading.** At the three s = L cells the per-unit speed step is:

  | layout | per-unit speed step |
  |---|---|
  | U | +0.362 [+0.119, +0.606] |
  | HP | +0.492 [+0.222, +0.762] |
  | PW | +0.198 [−0.052, +0.449] |

  - It pays in U and HP, with lower bounds > 0.
  - In PW its interval covers 0 (#473, NIT 3, which corrects "in every layout").
  - All three s = L lines read SPEED LEADS.
- **Under s = G, speed stops paying where the layout rewards steering, and not in U.** The per-unit speed step is:

  | layout | per-unit speed step |
  |---|---|
  | U-G | +0.448 |
  | HP-G | +0.085 |
  | PW-G | −0.133 |

- **The mean prize falls with clutter:** +0.727 at c0, +0.416 at c1 and +0.283 at c2. The prize is the part of the
  c ≥ 1 cells that stands.

## 3. Holistic PAYS and the holistic nose step: NOT RUN

They are blocked by LEGS.md B1–B4:
- `steer.py` refuses τ = 2 and RBT-129's points;
- there are no draw pools;
- the G8(c) planter and a holistic step harness are not in the tree;
- the probe members wait on Stage P.

**So PAYS is a designed-fauna layer only, decided at c = 0.** Nothing downstream may use a c ≥ 1 PAYS call until the
re-run is read (ruling of 12:58).

## 4. Descriptive comparison with RBT-125's gate (`legs_readout.txt` §4; no verdicts)

RBT-125 ran the committed eating rule, without `--fair`, on RBT-90's random terrain. The cells here run the sweep's
block. G2.5 is matched to s = G, and G0 to s = L. No cell here is an exact match for the gate: c0 is the nearest
clutter level, and it is the only one whose steps line is readable.

- **The prize at c0 is higher than the gate's in U and HP,** paired by population:
  - U-G, c0 − gate: +0.573 [+0.327, +0.819];
  - HP-G: +0.920 [+0.308, +1.532];
  - U-L: +0.123 [+0.019, +0.227].
- **In PW the difference is unresolved:** PW-G +0.171 [−0.121, +0.463]; PW-L −0.032 [−0.148, +0.084].
- **Across layouts,** the prizes are near the gate's at c1, and below it in every layout at c2.
- **The §B line at c0-PW:**
  - At G2.5 the gate read +0.317 [+0.032, +0.602] (13), NOSE LEADS, with a per-unit speed step of −0.075. c0-PW-G
    reads NOSE LEADS at +0.704, with speed at −0.133. Paired here − gate it is +0.440 [+0.101, +0.778] (13 hosts).
  - At G0 the gate read SPEED LEADS (−0.266); c0-PW-L reads SPEED LEADS (−0.250), paired difference
    +0.003 [−0.220, +0.225].
  - The c ≥ 1 rows of that table are NOT READABLE.
- **Nothing here is tested, and nothing re-reads RBT-125.** The worlds differ in the eating rule, `--fair`, the
  terrain and the motor budget together, so no difference is attributed to any one of them.

## 5. Robustness (`legs_readout.txt` §5)

**The check against the tool.** The registered line, recomputed from each steps output's per-host table (3-decimal
inputs), reproduces every STEP row's interval to within 0.001, with the same reading and the same n. The adversary
reproduced every row independently (#473 §2).
- At `c1-HP-G` and `c1-PW-G`, one host's r is printed as 1.100. `steps.py` excluded it, because its true value is below
  1.10. The recompute drops it to match the printed n.

**Leave one out, at the decided (c = 0) cells.** Prize: leave one population out, t(8). Steps: leave one host out,
t(n − 2).

| cell | ruled call | prize LB range (min at) | steps LB range | readings reached | call flips? |
|---|---|---|---|---|---|
| c0-HP-G | PAYS | +0.521 .. +1.083 (805) | **−0.062 .. +0.227** | NOSE LEADS, TIED | **FRAGILE:** omitting O1/2/003, O1/2/029, O1/3/009, O1/3/023 or O1/3/031 gives TIED |
| c0-PW-G | PAYS | +0.070 .. +0.306 (805) | +0.211 .. +0.331 | NOSE LEADS | no |
| c0-U-L, c0-U-G, c0-HP-L | not PAYS | lower bound > 0 throughout | — | the full-sample reading only | no |
| c0-PW-L | not PAYS | −0.097 .. +0.030 (4) | — | SPEED LEADS, TIED | no: the prize crosses 0 when population 2 is left out, but the steps condition fails in every omission |

- **Of the 6 decided calls, 5 are stable under a single omission and 1 (c0-HP-G) is fragile.**
- **c0-PW-G is the only decided PAYS call that is robust to leave-one-out.** It is also clean of explosions: no c = 0
  cell logged a warning.
- **At c ≥ 1, the as-computed line's leave-one-out** (for example c1-HP-G flipping to NOSE LEADS without host
  O1/3/028) is printed in `legs_readout.txt` for the record. It is moot under the ruling: the first readout's "PW-G is
  robust at every clutter level" held only for leave-one-out, not for exploded seasons in r (#473, MUST 1).

## What this licenses, and what it does not

**Licensed:** under the sweep's block (the fair set, root + surface eating), RBT-106's prize at a = 6 and a one-σ nose
step at the w3 rung meet the registered designed PAYS rule:
- at **c0-PW-G**, robust to leave-one-out, and food-dependent by the decoy;
- at **c0-HP-G**, fragile to one host, and with no decoy.

**Licensed:** at c = 0 no s = L cell pays. All three read SPEED LEADS.

**Not licensed:**
- **Any PAYS call at c ≥ 1, either way.** They are UNDECIDED until the registered re-run is read.
- **That the nose step pays "comparably to a speed step that pays."** At both PAYS cells the speed step does not pay
  (its intervals cover 0). The calls rest on nose steps with lower bounds > 0, set against collapsed speed steps.
- **That a TIED not-PAYS cell is a world where the nose step does not pay.** c0-U-G's nose step pays +0.388; its
  reading is unresolved.
- **That the path from no compass pays.** The first-nose and w1 lines read TIED at both PAYS cells.
- **A holistic statement of any kind.**
- **Claims for evolved bodies under the fair set.** The hosts are pre-fairness (#443, S3).
- **Any claim of equivalence.** There is no COMPARABLE on the registered line; that is a power result.

## Files

| file | what |
|---|---|
| `READOUT-PLAN.md` | the pre-data plan (`c47403c`) |
| `legs_readout.py` | reads the 36 branches; `integrity` → `integrity.txt`, `readout` → `legs_readout.txt`. It refuses to read unless integrity passes. The 12:58 ruling is applied in code (the `contam` / `call` fields) |
| `integrity.txt` | step 1: blobs, trees, flags, configs, completeness, provenance, `.err` kinds (unchanged by the revision) |
| `legs_readout.txt` | steps 2–5: per cell (as computed and ruled, with the raw line), marginals, the §2c exclusion table, the RBT-125 comparison, leave-one-out, the computed headline |
| `../legs-readout-adversary/` | #473: the re-derivation, the explosion probes and the explosion-free diagnostic, which is descriptive |

Reproduce:

```
git fetch origin '+refs/heads/ckpt/rbt-129-stage0-pays-*:refs/remotes/origin/ckpt/rbt-129-stage0-pays-*'
python runs/RBT-129/legs-readout/legs_readout.py integrity > runs/RBT-129/legs-readout/integrity.txt
python runs/RBT-129/legs-readout/legs_readout.py readout > runs/RBT-129/legs-readout/legs_readout.txt
```

This needs numpy only.
