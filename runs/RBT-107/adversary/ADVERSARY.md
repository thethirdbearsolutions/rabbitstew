# RBT-107 design adversary: round 1, on PR #207 (`results/RBT-107-design` at `5032cdd`)

The design adversary for RBT-107 wrote this on 2026-09-26. The coordinator (`session_01WKXr6PgNkscGhVc7Bzth9k`)
dispatched this role. **No arm has been launched.** No RBT-107 arm and no C4 shift-arm genome or income was read.

**What I read.**
- All of `runs/RBT-107/`: `PREREGISTRATION.md` with Addendum A, and every script and table in it.
- Chaotic RBT-107, including the coordinator's notes at 20:28 and 20:41 and the design post at 21:15; Chaotic RBT-110.
- RBT-101's `readout-adversary/READOUT-ADVERSARY.md` F2, `probe_refund.py` and its outputs.
- Lessons 1–8 in `docs/paper-9-net-of-arithmetic.md` on integration `707d27b`.

**What I ran.**
- Only no-event populations: C0 at T − 1 of the RBT-90 base arms 804 and 4, restored from `ckpt/rbt-90-{804,4}`.
- A pure simulation of power on the design's own committed null.
- Platform: numpy 2.4.6 and mujoco 3.14.0, the design's.

Every probe is in this directory, and each output file names its command.

| probe | what it measures |
|---|---|
| `probe_check.py` → `probe_check.txt` | whether garden.py's own harness reproduces a recorded season of the ecology, bout for bout |
| `probe_worlds.py` → `probe_worlds-{804,4}-conventional.txt` | Δ0 on the garden's 8 worlds against fresh worlds from the same generator, and against probe_refund's draws |
| `probe_refund_c0.py` → `probe_refund_c0-804-conventional.txt` | probe_refund.py's C0 refund for one seed, re-run exactly as that script runs it |
| `probe_grouping.py` → `probe_grouping-*.txt` | how much of one population's garden mean, on one world, is the draw of who shares an arena |
| `probe_power.py` → `probe_power.txt` | the power of the one-sided tests the coordinator asked for, on the design's measured null with its heavy tail kept, and the n each needs |

## Summary

| # | finding | class |
|---|---|---|
| F1 | The confirmatory test the coordinator asked for at 20:41 is not registered. There is no direction, no one-sided statistic, no power for H, and no alternative. Addendum A declines it ("nothing in the rule moves") | **MUST-FIX** |
| F2 | T + 800 on the same ten seeds is not out of sample for a pattern found on those seeds at T + 110: the populations at T + 800 descend from them. A confirmatory test needs fresh seeds, and fresh seeds also give a clean replication at T + 110 itself | **MUST-FIX** |
| F3 | Power. "Nearly blind" is mostly the statistic: a mean-based two-interval rule on a null with one outlier seed. A 20% trimmed-mean or signed-rank one-sided test recovers the power. **The question needs n ≈ 20 fresh seeds** (30 for effects of about 0.15) | **MUST-FIX** |
| F4 | The garden's 8 worlds. The grouping draw alone moves a population's mean by 0.11–0.26 per world, so on 8 worlds it is a large share of the designed null. The world effect is shared across seeds (r = +0.50), so the 8 registered worlds shift every seed's Δ0 together: they run 0.09–0.17 low on the two seeds measured. "Δ0 matches Z10" is not a validation | **MUST-FIX** (cheap) |
| F5 | A_SB is `probe_refund.py`'s RESPONSE in definition. The garden harness reproduces the ecology 32/32. Four implementation differences are listed; none biases A_SB. T + 110 should be added as a labelled post hoc anchor | CAVEAT |
| F6 | Δ0 cancels in A_SB and I by construction. Lesson 8 is met (the arena, groups of four, the population at T − 1) except for the fixed worlds (F4). The bracket (lesson 7) does not arise on C4 | CAVEAT |
| F7 | The C2 "positive control" is a result, not a control. It has already read RBT-110's C2 hypothesis near r ≈ 240, and **against it**: paired −0.17 [−0.35, +0.00], 2/7 | CAVEAT (disclose on RBT-110) |
| F8 | SPECIFIC/GENERAL: GENERAL absorbs a resolved negative I; MALADAPTED is not split; I is not netted of its null. The post hoc pattern is a MALADAPTED-GENERAL shape | CAVEAT |
| F9 | Extensions. Byte identity, the three short checkpoints and the code version check out. V-EXT is nearly vacuous on a 600/600 checkpoint and blind after 600. Add a post-join world gate and an explicit no-peek rule | CAVEAT |
| F10 | §10 was committed at 20:45:12, ten minutes after the coordinator's 20:35 note carried the post hoc numbers. It points the other way (designed A_SB +0.15), so it is not tuned. One of its lines is on committed data | CAVEAT |
| F11 | Cost, packing, durability: sound for the 34 continuations. The fresh-seed option is costed here | NONE |

---

## F1 MUST-FIX: the confirmatory hypothesis is not registered

**What was asked** (coordinator, 20:41, items 1–3):
- Pre-register the test of RBT-101 F2's post hoc pattern: the designed RESPONSE is negative, and the paired response
  favours the co-evolved body. Give its sign, size, statistic, null and power before any extension.
- Pre-register the alternative, that the designed fauna re-adapts.
- Name the intermediate read points.

**What the design does:**
- The registered verdict (§5.3) is two-sided and two-interval. MALADAPTED needs A_SB's **and** A_SN's 95% intervals
  both below 0.
- There is no paired (co-evolved − designed) statistic anywhere in `readout.py`.
- There is no one-sided test and no power for H.
- The trajectory at T + 200/400/600 is "printed, not scored".
- Addendum A §4 says "Nothing in the rule moves".
- The §10 prior points the other way: designed A_SB +0.15, MALADAPTED 0.10. That is honest and should stay as the
  scored prior (F10), but it is not a test of H.

**Why it matters.** A two-interval, two-sided rule is not a test of a directional hypothesis. Its power in H's
direction is lower than a one-sided test's. `probe_power.txt`, column `2s-int`: designed −0.22 at n = 10 on the scaled
null gives 0.48 on A_SB alone, before the A_SN interval is also required. And it has no statement for the paired
contrast RBT-110 is testing on C1–C3. Without these, RBT-107 cannot serve as the prospective test the programme
now needs it to be (paper 9, lesson 8 [PENDING]).

**Required: a §5.5 "Confirmatory", fixed before any arm, in RBT-110's form so the two can be read together.**
1. **H1-DES:** designed A_SB(T + 800) < 0. **H1-PAIR:** A_SB^co(T + 800) − A_SB^des(T + 800) > 0, which is
   RBT-110's H.
   - **Primary statistic:** one-sided, α = 0.05, Holm over the two.
   - It should be robust to the co-evolved tail (F3): the **20% trimmed mean (Yuen)** or the **Wilcoxon signed-rank**.
     Pick one now. The t-test is printed beside it.
   - **Net of the null:** the same tests on A_SN, which is RBT-110's "net of the null", (S − B) − (N − B) = S − N.
     Secondary.
2. **Sample:** the confirmatory set is the fresh seeds (F2). The ten extended seeds are read by the same rule and
   reported as **persistence**; they are secondary, and they are pooled only as a stated secondary.
3. **The alternative, H-ALT (the designed fauna re-adapts):** the increment Δ_des = A_SB^des(T + 800) −
   A_SB^des(T + 110) > 0, one-sided, same statistic. Name the outcomes and what each means:
   - **PERSISTS:** H1-DES supported, the increment not resolved.
   - **DEEPENS:** H1-DES supported, and the increment resolved below 0.
   - **REVERSES:** the increment resolved above 0 and H1-DES not supported.
   - **OVERSHOOTS:** A_SB resolved above 0. That is ADAPTED on the design's own rule.
   - **NOT DECIDED:** anything else, printed with the MDE.
4. **Read points:**
   - **T + 110** is RBT-101's read point, re-measured by the registered garden. It is post hoc on the ten old seeds
     and prospective on the fresh ones.
   - T + 400 and T + 600 are secondary (time course), and prospective only after season 600.
   - T + 800 is scored.
   - T + 200 is not prospective on the old seeds (see F9).
5. **Power at the chosen n** comes from `probe_power.txt`'s method on the null as re-measured at J = 32 (F4), with
   the effect sizes named: designed −0.22 and paired +0.27, the T + 110 post hoc sizes, and an effect of 0.15.
6. **No mechanism is named.** That is consistent with the coordinator's item 4, and the design names none. If a
   diagnostic is wanted, such as the selection differential on flat-ground income, register it separately.

## F2 MUST-FIX: same seeds, same lineages. T + 800 is not out of sample for a T + 110 finding

- RBT-101 F2's pattern was found on these ten seeds' populations at T + 110.
- Their T + 800 populations descend from exactly those populations. Any composition that differed by chance at
  T + 110 is inherited forward.
- Under the design's own null model (§9: neutral divergence variance grows linearly with depth), the correlation
  between a seed's null A at T + 110 and at T + 800 is √(110/800) ≈ **0.37**. So a chance deviation at T + 110 is
  about 37% carried into T + 800 on the same seeds. A "confirmation" there is biased toward the post hoc sign.
- The data after 600 are new, but the units are not. This is exactly the problem RBT-110 solves for C1–C3 with other
  challenges. **Nobody is testing C4's own finding on new C4 seeds.**

**Required:**
- **Fresh seeds as the confirmatory sample**, with RBT-90-style base arms and C4 shift arms to 1200 seasons, as the
  coordinator's 20:28 note costed.
- Pre-register the seed list and T. A fixed **T = 360** for every fresh seed is simplest. The existing T is 352–382,
  and RBT-92's onset rule was built for C1's death waves, not for C4.
- A cull20 arm per fresh seed is optional for H1: under H0, S and B are exchangeable, so A_SB is symmetric about 0.
  It is needed only for A_SN and the design's own two-interval verdict. I recommend it for the n used in the
  ADAPTED verdict.
- **A bonus:** the fresh seeds reach T + 110 (season 470) about 1 h 20 min into their wave. A registered **H-REP at
  T + 110** on them, using the same garden, is the fastest clean replication of RBT-101 F2. It is also the missing
  C4 row beside RBT-110's C1–C3.

## F3 MUST-FIX: power. "Nearly blind" is the statistic, and n ≈ 20 fresh seeds is what the question needs

**The design's power model** (§9, `readout.py mde`):
- It is Gaussian with the null's RMS. The co-evolved RMS is 0.388, almost all from **one seed**: seed 3's base went
  furniture-dependent, A_NB = +1.153. Without seed 3 the RMS is 0.139.
- The rule is mean-based. So one outlier seed sets the co-evolved resolution, 2.7–4.9 × Δ0.
- And through the paired contrast it would set the paired resolution too. The paired co − des null RMS is 0.506
  (0.159 without seed 3), with r(co, des) = −0.66 across seeds.

**`probe_power.py`** resamples the ten committed A_NB rows (smoothed bootstrap, one sign flip per row) and keeps the
tail. The table gives one-sided power at α = 0.05, **null scaled to d = 800** (the design's ×1.83), with test size
at or below 0.06 in every cell (the sign test and the mean tests run conservative under the tail).

| quantity, effect | n | t | Wilcoxon | Yuen 20% | design's two-sided interval |
|---|---|---|---|---|---|
| **designed A_SB, −0.22** | 10 | 0.63 | 0.58 | 0.59 | 0.48 |
| | 20 | **0.89** | 0.88 | 0.87 | 0.81 |
| | 30 | 0.97 | 0.97 | 0.96 | 0.94 |
| designed A_SB, −0.15 | 20 | 0.64 | 0.63 | 0.62 | 0.50 |
| | 30 | 0.79 | 0.78 | 0.78 | 0.68 |
| | 40 | 0.88 | 0.87 | 0.87 | 0.79 |
| **paired, +0.27** (empirical tail) | 10 | 0.43 | 0.53 | 0.65 | 0.28 |
| | 20 | 0.41 | 0.82 | **0.89** | 0.34 |
| | 40 | 0.59 | 0.98 | 0.99 | 0.47 |
| paired, +0.27 (Gaussian at the full RMS: the design's model, worst case) | 20 | 0.33 | 0.32 | 0.31 | 0.23 |
| | 40 | 0.56 | 0.54 | 0.51 | 0.43 |
| co-evolved A_SB, +0.20 (empirical tail) | 10 | 0.40 | 0.63 | **0.82** | 0.26 |

**What this means for the paired verdict:**
- **On a mean statistic it is hostage to one seed.** The t-test's power does not rise with n: 0.43 at 10, 0.41 at 20.
  An outlier's frequency, not its size, then decides the answer.
- **A rank or trimmed statistic fixes most of this.** At n = 20 the paired +0.27 has power 0.82–0.89 on the
  empirical tail.
- **More seeds fix the rest.**
- If the tail is not a one-off (the Gaussian worst case), even n = 40 falls short for the paired contrast. Only the
  designed contrast is then answerable. Say so before the arms.

**The n the question needs (cost is not the constraint):**
- **20 fresh seeds as the confirmatory set** for H1-DES at −0.22 and H1-PAIR at +0.27, on a robust statistic,
  power ≈ 0.87–0.89.
- **30 fresh seeds** if the effect worth detecting is 0.15, the size at which the programme's other contrasts sat.
- The ten extended seeds add persistence and a pooled secondary (n = 30–40).

**Also required:**
- Replace "the co-evolved fauna is nearly blind … NOT SEEN is nearly assured" (§9, §10) with the robust-statistic
  resolution. On the empirical tail it is 0.82 at +0.20, n = 10.
- Base the d = 800 null on a **measured** deep A/A, not on √d alone. RBT-105's replicates at 599 are about 17 events
  from season 0, and `garden_run.sh aa105` can run on them now (16 checkpoints exist: `ckpt/rbt-105-{1,2,4,7,804,
  805,806,807}-b{1,2}`, and 7-b0). That is a co-evolved A/A at about 17 events before any arm. Scale only the drift
  part of the null (F4), not the measurement part.

## F4 MUST-FIX (cheap): 8 worlds carry grouping noise, and a world effect shared by every seed

**Grouping noise** (`probe_grouping-*.txt`). This is one population, one world, the garden's bout, and only the
random split into fours changes. The sd of the population's mean gain across 6–8 groupings:

| C0, seed | flat | random | flat − random |
|---|---|---|---|
| designed 804 | 0.256 | 0.187 | 0.220 |
| designed 4 | 0.152 | 0.120 | 0.142 |
| co-evolved 804 | 0.108 | 0.122 | 0.103 |
| co-evolved 4 | 0.154 | 0.142 | 0.125 |

**What this does to the null:**
- On 8 worlds that is 0.04–0.09 per population mean, and **0.05–0.13 on each seed's A_SB** (two populations,
  independent groupings).
- Against the designed null RMS of 0.165, measurement is **about 20–60% of the designed null's variance**, and less
  for the co-evolved.
- None of it is drift. So §9's scaling of the *whole* RMS by √(800/240) over-states the d = 800 null by the
  measurement part. More worlds shrink it; more seeds are not needed for it.

**The world effect is common to all seeds** (`probe_worlds-*.txt`):
- The per-world flat − random step correlates **+0.50** across seeds 804 and 4 over 16 worlds.
- The registered worlds 0–7 give Δ0 = +0.694 and +0.688. Worlds 8–15 give +0.823 and +0.854, and seed 804's worlds
  8–39 give +0.779.
- So the 8 registered worlds put every seed's Δ0 about 0.1–0.17 low together. The t(9) interval across seeds does
  not contain that error.
- It cancels in A_SB, because both populations use the same worlds. It does not cancel in the **level** of Δ0.

**The probe_refund gap is sampling:**
- probe_refund's C0 refund (designed +0.942) and the garden's Δ0 (+0.754) differ on 9/10 seeds.
- `probe_refund_c0.py` reproduces probe_refund's seed-804 value exactly: +1.0172.
- The same four draws under the garden's population and grouping give +0.671.
- The short group of two is not the cause: +1.027 on full groups only.
- So the gap between the two instruments is world choice plus grouping noise.
- The Addendum's "two independent methods give the same arithmetic" (garden −0.589 against Z10 −0.630) is therefore
  **partly luck**. The same simulation on other worlds gives −0.806 (probe_refund) and, here, higher designed Δ0.
  It does not validate §4's instrument.

**Required:**
- **J = 32 worlds** in the readout garden, fixed now. It costs about 4× the garden, roughly 33 core-hours more, and
  nothing on the arms.
- Print a **split-half** A (worlds 0–15 against 16–31) per seed. Their difference estimates the measurement noise, and
  the readout reports it.
- Re-run the design-stage garden (C0, base and cull20 at 599) at J = 32. Recompute the null and power from it.
- Report Δ0 with a world-sampling term, and withdraw "validates §4's instrument" in Addendum A.

## F5 CAVEAT: A_SB is RESPONSE. Listing the differences, and adding T + 110

Both are G(event population, new world) − G(base population, same season, new world), by the ecology's group bout.
They are the same quantity.

`probe_check.txt`: garden.py's own pieces (`base_sim`, `BoutRunner.run_groups`, the exploder forfeit) reproduce base
804's recorded season 357 **32/32 bouts to four decimals**. The garden had no such check.

**Differences:**

| | garden | probe_refund | matters? |
|---|---|---|---|
| population | alive at the end of s (`alive_at`: includes that season's newborns, excludes its dead) | played season s | no bias; a few individuals. Say which in §5.1 |
| worlds | 8 fixed worlds shared by all seeds; terrain seed ≠ start seed | 4 draws per seed; terrain seed = start seed | F4 |
| grouping | `default_rng([107, j])` permutation | string-seeded shuffle | noise only (F4) |
| exploder | gains 0 (the ecology's `_gain`) | raw score | rare (≤ 2 per garden population) |

**Required:**
- Name A_SB as RESPONSE in §5.
- Add **T + 110** to `READS`, labelled *post hoc on the ten extended seeds* (it re-measures RBT-101 F2's −0.22 with
  the registered instrument) and *prospective on fresh seeds*.

## F6 CAVEAT: Δ0 cancels, and lesson 8 is met but for the worlds

**A_SB** = G_S^flat − G_B^flat contains no flat − random term. S and B descend from the same C0 and are scored on
the same worlds, so Δ0 cancels exactly. **I** is also free of Δ0.

**Lesson 8** asks for the arithmetic in the axis's own setting, and the design meets it:
- Δ0 is measured in the arena, in groups of four of one fauna, on the population at T − 1, by the ecology's bout.
- That bout is verified to reproduce the ecology (F5).
- The only departure is F4's fixed worlds.

**§7's residual level (D_SB − Δ0)** is income from the ecology's own seasons. Its arithmetic should be the
in-ecology **Z10** (RBT-101 readout adversary: season-T pairs by name), which the ecology's worlds generated. Print Z10
first and the garden Δ0 beside it.

**Lesson 7 (the bracket) does not arise.** No C4 fauna is insolvent: k = 0/0 on 6/10 seeds, and every fauna is
alive. State that in §4, so the omission reads as checked and not as missed.

## F7 CAVEAT: the C2 "positive control" is a result, it has read RBT-110's C2 question, and it disagrees with H

**Why it is not a control:**
- A positive control needs a known effect.
- RBT-99 F2's "recovery net of arithmetic" was an income figure. It was never shown to be genotypic. That is the
  design's own reason for running the garden.
- So PASS certifies that the C2 and base populations differ genotypically. It does not certify the instrument's
  sensitivity to an effect of known size.
- The instrument's mechanics are certified by F5's 32/32 instead.
- The PASS criterion *was* committed before the numbers: `26ad711` at 20:45 has the rule with `C2_TABLE`
  unfilled. That is to the design's credit.

**What it already says about RBT-110:**
- The same rows give the paired contrast RBT-110 registers as H on C2, at r ≈ 240 instead of 110/190, on the garden's
  worlds:
  - paired co − des = **−0.173 [−0.348, +0.002], 2/7 positive**;
  - designed A_SB(C2) = +0.47 (H says negative).
- RBT-110's pre-registration (20:45) predates it, so its rule is not tuned by this. But the C2 analyst and the
  coordinator are no longer blind near r = 190.
- The designed figure is on the 7 surviving seeds. Three seeds' designed C2 bases earn below 0 at 0.08 in the garden
  (805, 1, 4 at −0.12 to −0.38; 801 and 804 at +0.06 to +0.12), so lesson 7's survivor conditioning applies.

**Required:**
- Relabel §6 "a design-stage C2 garden result (post hoc for C2)".
- Print the paired value.
- Post a disclosure on RBT-110 (a proposed text is in the Chaotic comment).
- Do **not** open "its own registered readout" on the same C2 arms: it cannot be confirmatory now. A confirmatory C2
  garden needs fresh C2 seeds.

## F8 CAVEAT: SPECIFIC/GENERAL is not quite well defined

**The problems:**
- **GENERAL is "otherwise",** so it includes I's interval resolved **below** 0. That case is a flat-lived fauna
  better on flat but relatively *better on furniture*. It is not "general" improvement.
- **I is not netted of its null.** A_SB has A_SN beside it; I has only I_NB, printed.
- **MALADAPTED is not split.** RBT-101 F2's post hoc shape (−0.22 flat, −0.17 random) is a *general* decline.

**Required:**
- Three-way I: SPECIFIC (I > 0 and I − I_N > 0), GENERAL (I's interval covers 0), and FURNITURE-BIASED (I < 0).
- Apply the same split under MALADAPTED.

## F9 CAVEAT: extensions. Sound, with two gaps in the gate

**What checks out:**
- `extend_check.txt`: resume-and-extend is byte-identical on plain, **C4 shift resumed after its event** (shift at 5,
  resumed at 10) and a cull resumed after its cull. That is the post-event path the continuations take.
- `ckpt_replay.txt`: shift-804 from 548 and cull20-806 from 565 replay to 600 byte-identical to the committed tables
  **on the current code**. shift-805 at 599 replays one season by the same path and is gated.
- The code changed after RBT-90's runs (`--breed-stream`, 17:04). RBT-105's `repro805.txt` shows K = 0 reproduces an
  RBT-90 arm byte for byte, so the base continuations run the same dynamics.

**Gap 1: V-EXT is nearly vacuous on a 600/600 checkpoint.** It compares tables regenerated from the restored files
with the committed ones. It checks the restore, which is useful, but it exercises no code, and it cannot see
anything after 600. A wrong **prefix** cannot pass it. A wrong **continuation** could, for example a shift arm whose
world reverted after 600. Nothing suggests one would, but it costs nothing to check.

**Add V-POST** from `history.json` or `seasons.txt`:
- shift: `terrain_seed` is null for every s ≥ T through the last season;
- base and cull20: non-null throughout;
- no cull event after T in `events.txt`;
- the last season ≥ T + 800.

**Gap 2: no-peek is implicit.** Make it a rule:
- Runner sessions post only progress and platform. No income, `seasons.txt` or garden numbers from season 600 on
  are posted or read until every arm of the wave has ended and V-EXT/V-POST pass.
- The garden runs every read point in one pass.
- T + 200 (552–582) lies inside committed seasons that RBT-101's time course has already read (to T + 199), so it is
  not a prospective read on the old seeds.

**Durability detail:** `RESUME=1` restores `ckpt/rbt-107-ARM-SEED`. If a container dies before the first 20-minute
save, that branch does not exist yet. Say "rerun without RESUME" in `waves.txt`.

## F10 CAVEAT: §10's timing, and one line on committed data

- The §10 table is in `26ad711` at **20:45:12 UTC**, unchanged at `8e4bb6b`.
- The coordinator's note summarising RBT-101 F2 (designed RESPONSE −0.22, "forages worse on both terrains") was
  posted at **20:35:55**.
- "Committed before reading RBT-101's REPORT" is true of the REPORT. The key numbers were already on the ticket. Say
  so.
- It does not matter for tuning: §10 points *against* the post hoc pattern (designed A_SB +0.15, MALADAPTED 0.10), and
  Addendum A keeps it. That is the right call.
- **One line is not a prediction:** "residual level, designed, [T+60, T+160) within ±0.25". It is computable now from
  committed RBT-101 files and Δ0. Mark it "post-diction on committed data" or drop it.

## F11 NONE: cost, packing, durability

**The 34 continuations:**
- 17 sessions, 2 arms of *different* seeds each, `durable.sh every 20` beside every run with `DURABLE_WATCH_PID`, a
  final save after the post-run step, and one platform recorded per session. Sound.
- Under `set -e`, a failing `tables.py` exits before the final save. But `every` has already saved at the run's end,
  so no bulk is lost.

**Costed for F2/F3:**
- **20 fresh seeds × (base + shift) = 40 arms of 1200 seasons.**
  - At 10.2 s per arm-season that is about 3.4 h per session, 2 arms each: **20 sessions**, 2 waves of 10, **about
    7 h of wall time**.
  - With cull20 per fresh seed, add 10 sessions and one wave.
  - Branching shift from base's checkpoint at T saves about 30%, but it is more mechanism. I would not.
- **Garden at J = 32:**
  - about 4 × 140 core-seconds per population;
  - per fresh seed, 2 faunas × (C0 + 2–3 arms × 4 read points) populations;
  - **about 60–90 core-hours** in all, or about 1–1.5 h of wall time on 16 four-core sessions in parallel.
- **This fits in the ~27 h of hive time left.** The 34 continuations can run in parallel with wave 1 of the fresh
  seeds.

---

**Verdict.** The instrument is right: A_SB is RESPONSE, and it reproduces the ecology. So is the route: extension is
byte-identical and the checkpoints hold. **The design is not yet the confirmatory test it now has to be (F1–F3).**
- It needs a registered one-sided H1 in RBT-110's form, with the re-adaptation alternative.
- It needs fresh seeds as the confirmatory sample (about 20) and a robust statistic.
- It needs a 32-world garden, with the null and power re-measured from it (F4) and from RBT-105's deep A/A.

None of this needs an arm first. **No arm should launch until F1–F4 are in the pre-registration.**

_Generated by [Claude Code](https://claude.ai/code)_
