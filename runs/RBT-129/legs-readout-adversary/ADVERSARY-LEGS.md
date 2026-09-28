# RBT-129 designed PAYS legs readout (#467 at 92f1baf): adversary report

*This is the coordinator's task of 11:36 UTC. Data comes only from the 36 `ckpt/rbt-129-stage0-pays-*` branches, the
host checkpoint `ckpt/rbt-113-O1`, and the tree at 29ab80b. No Stage P branch and no Stage 0 census branch was
fetched or read. Numbers are recomputed with this directory's own code in a clean `.[dev]` venv (numpy only, with
hard-coded t quantiles). The only new simulation is a diagnostic re-run of the steps leg's w3 base and speed arms, on
five cells, to find where r comes from.*

## Verdict: **CONFIRMED WITH CAVEATS**

| item | count |
|---|---|
| MUST | 2, of which MUST 1 needs a coordinator ruling before RBT-129 uses the c ≥ 1 PAYS calls |
| SHOULD | 4 |
| NIT | 3 |

**The computation is confirmed.**
- Every number in the 18-row table reproduces (`rederive.txt`): the prize t(9), the registered steps line and its
  reading, the nose and speed steps alone, the four PAYS calls, and the leave-one-out FRAGILE labels.
- Under the registered rule, as the plan operationalises it, the calls are exactly the readout's.

**The c ≥ 1 calls are not robust.** A1.4's realised-speed ratio r, which decides who enters the registered line and how
their speed steps are scaled, is driven at c = 1 and c = 2 by **exploded seasons**, not by speed (§3).
- On the extreme host, r = 943.448 reproduces exactly, and it comes from a single exploded season. Without it r is 1.266.
- A per-host diagnostic on five c ≥ 1 cells re-runs the same seasons with explosion-free r. It is **not** a registered
  treatment, and nothing is re-called here. Under it:
  - **c2-PW-G's PAYS becomes TIED;**
  - **c2-HP-G's not-PAYS becomes NOSE LEADS;**
  - c1-PW-G's lower bound falls to +0.000.
- The codebase already treats an exploded season as no measurement of the body. `food_score` (RBT-30): "the actuator
  work the integrator ran up on the way there is not a measurement of anything the body did". A1.4 did not foresee
  explosions entering r.
- So **the "PW-G at c0, c1 and c2" headline holds as computed, but only its c = 0 part is free of the artefact.**

**MUST 2:** "No COMPARABLE was read anywhere" is false as written.

## 1. Pre-data discipline

| check | finding |
|---|---|
| Plan before data | `c47403c` at 11:10:12, integrity at 11:14:24, readout at 11:17:50, in that commit order. The plan names only inputs |
| "At least comparably" = COMPARABLE or NOSE LEADS, supported *verbatim*? | **Yes, as quoted**, by three texts. **But none of them is RBT-129's registration** (SHOULD 1): |
| — RBT-125 REGISTRATION A1.4 | defines the four labels and their order, and makes the per-unit line the registered line. It does not define "at least comparably" |
| — ADVERSARY-PASS2 §3 (mine) | the heading reads "For RBT-129's PAYS rule (COMPARABLE or NOSE):". That parenthetical restated the coordinator's brief; it was not a ruling. The section's content says §B licenses nothing for RBT-129 |
| — ADVERSARY-RBT132 S7(b) | "The R4 test (COMPARABLE or NOSE) matches RBT-121 R4's text … It is not 'beats', so it is not stricter than the designed leg." This is the holistic leg's test, and it says the designed leg's is the same |
| — READOUT-BC §B scope | "The sweep's PAYS rule uses the same labels (COMPARABLE, NOSE LEADS) on its own legs" |
| — RBT-129 DESIGN §6.3 and §5.1 | only "pays at least comparably to a speed step" (RBT-121 R4's words); no labels |
| Did anything after the plan change a rule? | **No.** No commit on integration since 11:09 touches `runs/RBT-129/DESIGN.md`, `LEGS.md`, the lanes, or RBT-125's REGISTRATION |

**On the plan's "I judge the registered text to fix 'comparably' without ambiguity".**
- The labels are registered (A1.4). The *mapping* of "at least comparably" onto them rests on the three reports
  above, not on RBT-129's DESIGN.
- The mapping is consistent and was on record before the data, so the calls stand.
- The readout should say where the mapping comes from (SHOULD 1).
- This review proposes no other reading.

## 2. The 18 rows re-derived (`rederive.py` / `.txt`)

**My parsers**
- *Prize:* the harness's per-body income table, per population, all 10, with a missing ROW counted as 0 (none is
  missing).
- *Steps:* the per-host table, applying A1.4's per-unit formula and r ≥ 1.10 exclusion, with the reading in
  `steps.py`'s order.

**What reproduces**
- **Every row matches `READOUT-LEGS.md`** to the last printed digit, or within 0.001 where the 3-decimal table rounds.
  - At c1-HP-G and c1-PW-G one host prints r = 1.100. The tool excluded it, because its full-precision r is < 1.10. My
    parser matches the printed n by excluding it too, as the readout's does.
- **PAYS:** c0-HP-G, c0-PW-G, c1-PW-G and c2-PW-G, and nothing else.
- **Leave-one-out:**
  - c0-HP-G reaches NOSE LEADS / TIED, so it is FRAGILE.
  - c1-HP-G reaches TIED / NOSE LEADS, so it is FRAGILE.
  - The three PW-G calls stay NOSE LEADS.
  - The prize LOO minima match: +0.521, +0.070, +0.243 and +0.274 at the PAYS cells.
- **The speed step's own payoff** (per-unit, at w3) at the four PAYS cells matches the readout: +0.085, −0.132,
  −0.024 and +0.039. Every interval covers 0.
- **The prize is essentially untouched by explosions.** Exploded seasons are at most 43 of 4,480 per cell, and balanced
  between motif and base. At c0 there are none.

## 3. The realised-speed ratio r at c = 1 and c = 2: explosions, not speed

**The mechanism, shown on the extreme host.** `probe_r_outlier.py` / `.txt` re-runs c2-HP-L, host O1/1/016, w3 base
and speed@w3, with 29ab80b's `steps.py` and config:
- the committed table row reproduces exactly: items 1.469 / 1.711, **r 943.448**;
- **one exploded season** (seed 125001) moved the centre of mass at a mean of **52,340 m/s**, and it carries the whole
  mean;
- without the 3 seasons that exploded in either arm, **r = 1.266**, a normal +25% step (median ratio 1.277).

`steps.bout` sums the centre-of-mass path over the whole season, including the explosion, and r is a ratio of means
over 128 seasons. So one exploded season in either arm drives r to about 0 or to hundreds.

**What that does to A1.4's per-unit line at c ≥ 1:**
- **A host whose base arm exploded** gets r < 1.10, and it leaves the line, even though its real speed step was about
  +25%.
- **A smaller explosion in the speed arm inflates r modestly**, and can carry a host over 1.10 that would otherwise be
  out: c2-PW-G host 3/004 has r 1.420 registered, against 1.062 without explosions.
- **A host whose speed arm exploded** gets a huge r. It stays in, with its speed step multiplied by 0.25 ÷ (r − 1),
  which is about 0. Its nose − speed then becomes its bare nose step.

**Per host, explosion-free r** (`probe_r_clean.py`, per cell; a diagnostic of the rule's input, **not** a registered
treatment). Items per arm come from the committed table (all 128 seeds), and r from the seed pairs where neither arm
exploded:

| cell | hosts with ≥ 1 exploded season (either arm) | hosts in the line | registered line (n) | with explosion-free r (n) | call (registered → diagnostic) |
|---|---|---|---|---|---|
| c1-p030-PW-G | 13 of 15 | registered n 8 → explosion-free n 12 | +0.388 [+0.097, +0.679] (8) NOSE LEADS | +0.216 [+0.000, +0.432] (12) NOSE LEADS | PAYS → **PAYS** (prize LB > 0 at all five) |
| c2-p030-PW-G | 14 of 15 | registered n 7 → explosion-free n 8 | +0.210 [+0.078, +0.343] (7) NOSE LEADS | +0.096 [-0.130, +0.321] (8) TIED | PAYS → **not** (prize LB > 0 at all five) |
| c2-p030-U-G | 15 of 15 | registered n 7 → explosion-free n 11 | -0.004 [-0.166, +0.157] (7) TIED | -0.051 [-0.183, +0.080] (11) TIED | not → **not** (prize LB > 0 at all five) |
| c1-p030-HP-G | 10 of 15 | registered n 9 → explosion-free n 13 | +0.419 [-0.034, +0.872] (9) TIED | +0.329 [-0.032, +0.690] (13) TIED | not → **not** (prize LB > 0 at all five) |
| c2-p030-HP-G | 13 of 15 | registered n 7 → explosion-free n 10 | +0.160 [-0.054, +0.375] (7) TIED | +0.267 [+0.007, +0.527] (10) NOSE LEADS | not → **PAYS** (prize LB > 0 at all five) |

- **Reproduction.** The re-run reproduces every committed per-host row (items per arm and r) at all 75 hosts
  (5 cells × 15). The diagnostic runs on the same seasons the legs ran.
- **Most hosts have at least one exploded season at c ≥ 1:** 10 to 15 of 15 per cell.
- **Two calls flip under explosion-free r, in opposite directions:**
  - **c2-PW-G goes from PAYS to not.** Only 4 of its registered 7 hosts would still enter the line. Speed-arm
    explosions inflated the r of several others (3/004: registered 1.420, explosion-free 1.062), which let them in with
    shrunk speed steps.
  - **c2-HP-G goes from not to PAYS**, at +0.267 [+0.007, +0.527], with its prize lower bound > 0.
- **c1-PW-G stays NOSE LEADS**, but its lower bound falls to +0.000 (from +0.097).
- **The c = 0 calls are untouched:** no c = 0 cell logged a single warning.
- **Not re-run:** the other seven c ≥ 1 cells. Of those, c1-U-G is the only TIED line at s = G; the others are s = L,
  where the nose step is ≈ 0 and speed pays.

**Is the exclusion correlated with the outcome?** At the c ≥ 1 G cells, the hosts that the registered r excludes have
smaller nose steps than those it keeps:
- c1-PW-G: +0.232 (7 excluded) against +0.363 (8 kept);
- c2-PW-G: +0.052 (8) against +0.249 (7);
- c2-HP-G: +0.177 (8) against +0.329 (7).

The exclusion is driven partly by explosions (above), so it is not a neutral filter at c ≥ 1.

**Would a different *registered* treatment change a call?**
- The only other registered treatment is **the raw comparison**, which A1.4 prints beside the line and registers as
  descriptive.
- **None of the four PAYS calls changes.** The raw line reads NOSE LEADS at all four.
- **Three non-PAYS calls would change:**

  | cell | raw line | per-unit (registered) line |
  |---|---|---|
  | c1-HP-G | NOSE LEADS | TIED |
  | c2-HP-G | NOSE LEADS | TIED |
  | c2-U-G | **COMPARABLE** | TIED |

  All three have a prize lower bound > 0.
- Under the registration the per-unit line decides, so they stay "not PAYS". The raw line does not decide.

## 4. The MuJoCo warnings

- **Counts reproduce:** 1,653 QACC and 2 EPA, all at c = 1 and c = 2, none at c = 0.
- **They do touch the numbers.**
  - QACC "Nan, Inf or huge" is an integrator blow-up. The robot passes `explosion_speed` and is marked exploded, and
    the explosion step itself moves its centre of mass by up to tens of km.
  - **Items:** an exploded robot stops being stepped. Its items are those eaten before the blow-up, and the income
    tables include them. At ≤ 1% of prize seasons, balanced between arms, the effect on the prize is negligible.
  - **r:** this is where the warnings bite (§3). Every r outside [0.5, 2] in `rederive.txt`, and every host that
    crosses 1.10 in the explosion-free re-run, sits at c ≥ 1.
- **Attribution.** The steps `.err` files cannot attribute a warning to a host (one pool per cell); the re-run does.
  The prize `.err` files map to populations; the harness's "exploded x/n" counts per cell are in `prize_explosions.txt`.

## 5. What the four calls mean, and what §6.3's PAYS licenses

**At every PAYS cell, both things are true:**
- the nose step pays on its own, with a lower bound > 0 (+0.386, +0.270, +0.208 and +0.053);
- **the speed step does not pay**: its interval covers 0 at all four, and its point estimate is negative at PW-G c0
  and c1.

So NOSE LEADS here is a nose step that pays, set against a speed step that does not. It is never a nose step matching
a speed step that pays.

- **c0-U-G** is the one cell where both pay: nose +0.388 [+0.117, +0.659], speed +0.448 [+0.209, +0.687]. There the
  line reads TIED, a power result at a 90% half-width of about 0.28 against δ = 0.10. So the rule's "not PAYS" at
  c0-U-G does not mean the nose step failed to pay.

**What §6.3's PAYS layer licenses, within the registered rule.** At c0-HP-G (fragile) and PW-G c0–c2, "the designed
fauna's nose step pays at least comparably to a speed step, and its planted prize has a lower bound > 0". The wording
must disclose four things:
- **"Comparably" is met by NOSE LEADS against a speed step that does not pay there**, as the readout's "Not licensed"
  bullet already says. Keep it next to every PAYS.
- **At c ≥ 1 the registered line's r is explosion-contaminated.** State this, and that under explosion-free r (a
  diagnostic, §3) c2-PW-G would not pay and c2-HP-G would (MUST 1).
- **A "not PAYS" is not a finding that the nose step fails when its steps line is TIED.** 8 of the 14 not-PAYS cells
  are TIED, including c0-U-G, where the nose step pays +0.388. The cross-tab's "not PAYS, and NONE: the expected result
  in a coverage world" must not be read into a TIED cell as a finding about the world (SHOULD 2).
- **The step is the w3 rung of an installed compass on pre-fairness hosts.** The readout says this.

## 6. The rest

- **The decoy:** PW only, as registered. The PW-G motif − decoy lower bounds are > 0 (+0.312, +0.395, +0.359). U and HP
  are correctly labelled "not shown food-dependent". **c0-HP-G's prize has no decoy check**, which should sit beside its
  FRAGILE label (NIT 1).
- **Pre-fairness hosts (#443, S3):** stated, correctly, with every figure.
- **Multiplicity:** none registered, and none applied. The 18 × 2 count is stated. Correct.
- **The RBT-125 comparison stays descriptive.** It prints paired intervals but no verdicts, and it attributes nothing.
  Correct.
- **Integrity: confirmed.**
  - Every `tool:` blob in both `launch.txt` files, plus `mechanism.py` and `resign_rbt67.py`, is identical at 29ab80b,
    at 61cb19b and at integration. So are the `rabbitstew/`, `scripts/`, `runs/RBT-129/launch` and
    `worlds/config` trees.
  - Both `launch.txt` files record `commit 61cb19b` (the emit commit, an ancestor of 29ab80b with identical content).
    The readout's "ran from 29ab80b" should say that (NIT 2).
  - MANIFEST progress is "?" in all 36 snapshots, as the readout says. The provenance therefore rests on the runners'
    guards, as stated.
- **The headline wording:**
  - "No COMPARABLE was read anywhere" is wrong (MUST 2).
  - "a +25% speed step pays at c0 in every layout: U +0.362, HP +0.492 and PW +0.198 (the last with its interval
    covering 0)" contradicts itself (NIT 3).
  - "The PW-G row is robust at every clutter level" is true under leave-one-out, but not for the r treatment at c ≥ 1
    (MUST 1).

## MUST

1. **The c ≥ 1 PAYS calls rest on an explosion-contaminated r. Disclose it, and get a ruling before RBT-129 uses
   them.**
   - Under the registered rule the calls stand as computed: PW-G at c1 and c2.
   - The per-host diagnostic (§3) shows that the c ≥ 1 part of the PAYS layer is decided by numerical blow-ups:
     - c2-PW-G reads TIED with explosion-free r;
     - c2-HP-G reads NOSE LEADS;
     - c1-PW-G keeps a lower bound of only +0.000.
   - The readout must:
     - (a) state this beside the c1-PW-G and c2-PW-G calls and in the headline;
     - (b) replace "the PW-G row is robust at every clutter level" with "robust to leave-one-out; not robust to
       exploded seasons in r at c ≥ 1";
     - (c) leave the calls as computed.
   - **For the coordinator:** whether an exploded season is a valid input to A1.4's r. The RBT-30 `food_score`
     precedent says it is not a measurement of the body. That is a ruling, not something this review or the readout
     can supply. Until it is made, only the c = 0 calls (c0-PW-G, and c0-HP-G, fragile) are clean.
2. **Correct "No COMPARABLE was read anywhere".** The raw line at c2-U-G reads COMPARABLE (+0.007 [−0.070, +0.084]).
   Say "on the registered (per-unit) line".

## SHOULD

1. State the source of the "at least comparably" = COMPARABLE or NOSE LEADS mapping: A1.4's labels, plus the three
   reports (§1). RBT-129's DESIGN gives only R4's words.
2. In §5 and the cross-tab wording, mark TIED not-PAYS cells as **unresolved**, not as a world that does not pay. That
   is 8 of 14, including c0-U-G, where the nose step pays.
3. Report the raw-line readings beside the calls: c1-HP-G and c2-HP-G read NOSE LEADS raw, and c2-U-G COMPARABLE. They
   are descriptive, and they show which calls depend on the per-unit rescaling.
4. Say that exclusion at r < 1.10 correlates with smaller nose steps at the c ≥ 1 G cells (§3). It is not a neutral
   filter there.

## NIT

1. Put "no decoy" beside c0-HP-G's FRAGILE PAYS.
2. Say that `launch.txt` records 61cb19b, content-identical to 29ab80b.
3. Fix the self-contradiction "speed pays at c0 in every layout … PW's interval covering 0".

## Files (`runs/RBT-129/legs-readout-adversary/`)

| file | what it holds |
|---|---|
| `rederive.py` / `.txt` | all 18 rows from the branches: my parsers, hard-coded t, the readings, leave-one-out, and the raw readings |
| `probe_r_outlier.py` / `.txt` | c2-HP-L host O1/1/016: r 943.448 reproduced, and the one exploded season that makes it |
| `probe_r_clean.py`, `probe_r_clean_<cell>.txt`, `r_clean_summary.md` | per host, explosion-free r at c1-PW-G, c2-PW-G, c2-U-G, c1-HP-G and c2-HP-G, with each re-run checked against the committed row; the diagnostic line beside the registered one. In the per-host tables, the "registered in?" column tests the *printed* r ≥ 1.10, so a host printed at 1.100 shows "yes" although the tool excluded it. The registered n printed below each table is the tool's |
| `prize_explosions.txt` | exploded seasons per prize cell (motif and base), and the warning totals |
