# RBT-107 pre-registration: can adaptation after a challenge be seen at all? C4 (flat ground) at ~20 reproduction events

**Status. Design only. No RBT-107 arm has been launched.** Written by the RBT-107 designer on 2026-09-26, against
integration `84c0423` plus RBT-101's arm branches for seeds 1, 2 and 4 (PRs #184, #189, #191, merging). The gate is the
ticket's: an adversary named by the coordinator, before any arm. RBT-88's rules apply.

**What was run for this document, and what was read.**
- Two 20-season throwaways (`extend_check.sh`) and two replays of short checkpoints against committed tables
  (`extend_check.sh ckpt`). Nothing from them is read but byte equality.
- **The common garden, on pre-onset bodies and on no-challenge arms only** (`garden_run.sh design`, `c2control`):
  C0 (the fauna alive at T − 1), the RBT-90 base at 599, RBT-92's cull20 at 599, and the positive control on
  RBT-99's C2 arms (§6).
- `depth.py` read the committed `lineage-last.txt` of the ten RBT-101 shift arms: births and parents only.
- **No C4 shift arm's income or genome was read.** No `seasons.txt` income column of a shift arm was opened.
  RBT-101's readout is not posted at this writing, and nothing here uses it (§1).

---

## Summary

| | |
|---|---|
| challenge | **C4, the furniture removed** (`--shift-at T --shift terrain=flat`), RBT-101's arms (§1) |
| route | **no new arm from season 0.** Every arm is a **continuation** of a committed 600-season arm from its checkpoint to **1200 seasons** (§2). Resume-and-extend is byte-identical to a longer run (`extend_check.txt`, PASS) |
| depth | **2.7–3.3 reproduction events per 100 seasons** after T (`depth.txt`). The scored read point **T + 800** holds **~22 events** on the conservative count (fewest births back to C0), ~26 by first parent (§3) |
| arms | per seed: **shift** (C4), **base** (RBT-90), **cull20** (RBT-92, the divergence null), all ten seeds; plus RBT-101's **k-cull** on 801, 1, 2, 4 (report-only). **34 continuations** |
| arithmetic first | **Δ0 = G_C0^flat − G_C0^random**, the unchanged population's income step on flat ground, from pre-onset bodies: co-evolved **+0.165**, designed **+0.754**; for an unchanged pair, R-body moves **−0.589** (§4) |
| resolution | designed **0.19–0.34** income per bout (0.25–0.45 × Δ0); co-evolved **0.44–0.80** (2.7–4.9 × Δ0), nearly blind (§9) |
| primary readout | **the common garden** (§5): the fauna alive at T + 800 of shift, base and cull20, each run on the same eight fixed worlds, flat and random, by the ecology's own group bout. **A_SB = G_S^flat − G_B^flat** and **A_SN = G_S^flat − G_N^flat**. Both populations descend from the same C0, so Δ0 cancels and an unchanged pair reads 0 |
| verdict | **ADAPTED** if both t(n−1) intervals are above 0, split into **SPECIFIC** or **GENERAL** by the specialisation I; **MALADAPTED**; **NOT SEEN** with its resolution; per fauna |
| secondary | the paired income trajectory: slope of x_S − x_B over [T+200, T+800] against the cull20 null; and its level net of Δ0 (§7) |
| null | cull20 − base on every seed (matched in seed, T and depth); RBT-101's k-culls; **RBT-105's founder-sharing replicates at 599, a depth-matched holistic A/A** (§8) |
| positive control | **C2 in the same garden** (§6): RBT-99's shift arms against base at 599, both priced at 0.08. **PASS**: co-evolved +0.22 [+0.10, +0.35] 10/10, designed +0.47 [+0.25, +0.68] 7/7. Net of the price arithmetic, C2's populations responded |
| falsifier | §10 |
| cost | 34 continuations × ~600 seasons: **17 sessions at two arms per session, WORKERS=2, about 1 h 45 min each**, in two waves (10 + 7); then the garden, about 3 h on one four-core session or ~20 min per seed in parallel (§11) |

---

## 1. Which challenge: C4, argued (item 1)

**C4 stays, and the argument does not depend on RBT-101's readout.** RBT-101's readout is pending
(designer `session_01XLdtXN6rsCKsjbEgiy7KtV`). I did not read its income tables, and I did not wait for it. Here is why
C4 is still the best candidate whatever the readout says:

1. **It is the one challenge with something to re-learn that the robots can see.** Obstacles reach the brain through
   `contact`, `height`, `up` and the joint sensors at w ≈ 1 (RBT-101 §2). On open ground those readings change, and
   a gait built among furniture has a new optimum to climb toward. C1 (crowding) and C2 (price) are unperceived. A
   response there can only be sorting on standing gait or morphology.
2. **Its arithmetic is small, measured, and does not dominate.** RBT-99 was decided by price arithmetic: the price
   took 0.95 a season from the designed body. RBT-101's solo probe puts flat ground's step at +0.57 designed and
   +0.25 co-evolved, and §4 measures it on whole C0 populations in the ecology's bout. A response has to beat
   drift, not a wall of arithmetic.
3. **Nobody dies of it.** RBT-101's k is 0/0 on six of ten seeds (`cull-k-*.txt`). No survivor-conditioning,
   no extinction, all ten seeds read. C2 lost three seeds to extinction and pinned four more by D.
4. **The arms exist, and all ten checkpoints restore** (§2). That makes it the cheapest route to depth.
5. **The readout here is new, so RBT-101's verdict does not pre-empt it.** RBT-101 reads RBT-92's income classes in
   [T+60, T+160) and a structural re-wiring count at T + 160. **Whatever it finds, the question here is different:
   is there a genotypic response to flat ground at 20 events, in a common garden?**
   - If RBT-101 returns NO CHANGE SEEN and class B or F, that is the ticket's premise (too shallow), and C4 is the
     right place to go deeper.
   - If RBT-101 returns RE-WIRED or an income response, C4 is the challenge where a deep window can ask whether it
     carries through and grows. The case strengthens.
   - **The one result that would weaken it:** RBT-101's garden-free income evidence that flat ground changes nothing
     at all, R-shift ≈ 0 on both faunas. Even then Δ0 (§4) says whether the unchanged population's income moved.
     If Δ0 ≈ 0 as well, the challenge exerts no selection on income, and I say so in an amendment before launch.
     **Pre-registered:** if |mean Δ0| < its own half-width on both faunas, I propose C2 instead, on the same
     instrument (the garden at 0.08; §6 is already that instrument's control), and the coordinator rules.

**What the design-stage measurements add to the choice** (§4, §6, measured after I first wrote this section; I am
stating what they changed):
- **C2's garden control shows a genotypic response by ~6.5 events on both faunas, net of the price.** So the
  ticket's "at all" already has a *yes* on an unperceived challenge at shallow depth. That makes C4 the sharper
  question: **does a perceivable challenge produce a response that grows with depth?** I keep C4, and I propose the
  C2 garden readout to the coordinator as its own small ticket (§6).
- **C4's arithmetic is large for the designed body (Δ0 = +0.75), and the garden cancels it by construction.** So
  RBT-101's income verdict will be mostly arithmetic (posted there at 20:44), and the garden is the way to see past it.

**Why not C2 as the subject?** C2 has the strongest, best-understood selection gradient (kJ per item). But the
designed fauna is extinct on 3/10 seeds, which breaks pairing, and its survivors are survivor-conditioned.
C2 is used here instead as the **positive control** (§6): a response of known direction, on real bodies, in this
ecology, which the garden must see.

## 2. Depth route: continuations, not re-runs (item 2)

**The ecology resumes byte for byte, including to a larger `--seasons`.** Checked two ways:

1. **Throwaway** (`extend_check.sh throwaway` / `compare` → `extend_check.txt`). At seed 801 on RBT-92's command, three
   pairs: plain, C4 shift at 5, and a 5/5 cull at 5. `long` runs 20 seasons uninterrupted. `ext` runs 10 to its
   natural end, then `--resume --seasons 20`.
   - `lineage.jsonl`, `cohorts.jsonl`, `history.json`, `state.json`, `seasons.txt`, `lineage-last.txt`, and every
     genome at birth and champion: **IDENTICAL, on all three**. `EXTEND-CHECK PASS`.
   - **One difference, stated:** `final/`, the end-of-run population dump (one file per living member), keeps stale
     higher-numbered files from the first end (35, 4 and 4 files). Every file the longer run wrote there is identical.
     Nothing resumes from it (`state.json` carries the population), and nothing in RBT-107 reads it.
2. **Real checkpoints** (`ckpt_check.sh` → `ckpt_check.txt`, MANIFESTs only):
   - **600/600 on 27 of the 30 core checkpoints**: all ten `rbt-90-SEED`, eight `rbt-101-shift-SEED`, nine
     `rbt-92-cull20-SEED`. The k-culls `rbt-101-cull-{801,1,2,4}` are also 600/600. The other six seeds have k = 0/0
     and no cull arm.
   - **Short, the RBT-99-806 lesson:** `rbt-101-shift-804` at **548**, `rbt-101-shift-805` at **599**,
     `rbt-92-cull20-806` at **565**. A short checkpoint is not lost: the run replays the missing seasons first.
   - **The replay reproduces the committed tables** (`extend_check.sh ckpt` → `ckpt_replay.txt`). shift-804 was
     restored at 548 and cull20-806 at 565, both resumed to 600. **CKPT-CHECK PASS on both:** `seasons.txt`,
     `lineage-last.txt`, `bodysig.txt`, `events.txt` and `groups.txt` are byte-identical to the committed files.
     shift-805 at 599 replays one season, by the same path.
   - **Every continuation carries the same gate at its end** (`prefix_check.py`, V-EXT). Its `seasons.txt` rows before
     600 must equal the committed arm's on the five shared columns. Its `lineage-last.txt` rows of individuals dead
     before 600 must be identical, and those alive at 599 continued. `bodysig.txt` and `wiring.txt` rows born before 600
     must be identical.
3. **Platform:** numpy 2.4.6 and mujoco 3.14.0, as RBT-105's throwaway and RBT-101's runners recorded. The replays
   above ran on them.

**So no arm starts from season 0.** `extend_arm.sh SEED ARM` restores the source checkpoint into
`runs/RBT-107/ARM-SEED`, resumes it to 1200 with `durable.sh every 20` beside it (label `rbt-107-ARM-SEED`), and
writes the tables, `wiring.txt` and `prefix.txt`. It then saves once more. Every flag of the original command,
the shift and the cull included, rides in the restored `config.json` and `state.json`; nothing is re-typed.

## 3. Depth, measured (item 2)

`depth.py` → `depth.txt`, from committed `lineage-last.txt` only, the ten RBT-90 bases and the ten RBT-101 shift
arms, T from `onset.txt`. There are three counts per living individual, from C0 (alive at T − 1):
- **few:** the fewest births back to any C0 member, every parent followed. This is conservative, and it is RBT-101's
  depth.
- **fp:** the first-parent chain, as in RBT-92's `baseline_depth.py`, which gave "about 5".
- **most:** the most births back.

The rate is the least-squares slope over T+40 … 599 (about 240 seasons).

| arm, fauna | few, events / 100 seasons (range over seeds) | seasons to 20 events | fp | most |
|---|---|---|---|---|
| base, co-evolved | 2.69 (2.53–3.11) | 743 (644–791) | 2.76 → 725 | 3.57 → 560 |
| base, designed | 2.73 (2.43–3.09) | 732 (647–823) | 3.25 → 615 | 3.61 → 554 |
| **shift, co-evolved** | **2.78 (2.45–2.94)** | **718 (680–818)** | 3.29 → 609 | 3.89 → 514 |
| **shift, designed** | **2.84 (2.39–3.24)** | **705 (617–836)** | 3.50 → 571 | 3.90 → 512 |

- At T + 160 this reproduces RBT-92's "about 5" (fp 4–7, few ~4.3).
- **The scored read point is T + 800.** At the median conservative rate that is **~22 events** (few), ~26 (fp)
  and ~31 (most). At the slowest seed's rate (2.39) it is 19.
- **So 1200 seasons is the season count.** T is 352–382, so T + 800 is 1152–1182, and every seed reaches it.
- The readout re-measures depth at T + 800 on the realised arms. A fauna whose median few-births depth there is
  below 15 carries **DEPTH SHORT** on its verdict line.
- The trajectory is read at T + 200, 400, 600 and 800, which is about 5.5, 11, 16.5 and 22 events.

## 4. The arithmetic first (item 3)

**What flat ground does to an unchanged population** comes from pre-onset quantities only. It is C0, the fauna
alive at T − 1, identical in every arm by RBT-92's V0, each individual from its genome at birth, run in the
common garden (§5) on the same eight worlds, flat and random:

> **Δ0 = G_C0^flat − G_C0^random**, in income per robot-bout, the ecology's own season gain (items − 0.03 × kJ).

Measured (`design_power.txt`, from `garden/c0-*`):

| seed | 801 | 804 | 805 | 806 | 807 | 1 | 2 | 3 | 4 | 7 | mean, 95% t(9) | positive |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| co-evolved Δ0 | +0.11 | +0.24 | +0.06 | +0.17 | +0.17 | +0.22 | +0.11 | +0.13 | +0.21 | +0.23 | **+0.165** [+0.121, +0.210] | 10/10 |
| designed Δ0 | +0.90 | +0.69 | +1.03 | +0.98 | +0.76 | +0.49 | +0.61 | +0.47 | +0.69 | +0.93 | **+0.754** [+0.612, +0.897] | 10/10 |
| **co-evolved − designed** | | | | | | | | | | | **−0.589** [−0.749, −0.430] | 0/10 |

- **Flat ground is a boon to both bodies, and nearly doubles the designed body's income.** The designed C0 earns
  +0.61 to +1.03 on furniture and +1.08 to +2.06 on flat ground. The co-evolved C0 gains a sixth.
- **So, by arithmetic alone, flat ground moves R-body by −0.59**, about four times RBT-92's r. The direction is
  RBT-101's class C. **I posted this on RBT-101 at 20:44, before its readout.** There, a C (or "designed R-shift >
  co-evolved R-shift") is what an unchanged pair of populations would show.

- **For the income readout (§7):** an unchanged pair of populations would show x_S − x_B = Δ0 from T onward.
  **The response is the residual, never the level.** The paired R-body shift − base for an unchanged pair is
  Δ0(co-evolved) − Δ0(designed) (printed). **This is also the arithmetic RBT-101's income readout needs**, and I
  post it there.
- **For the garden (§5):** S and B both descend from this C0, so the arithmetic cancels in A_SB by construction.
  An unchanged pair reads A_SB = 0, and a drifting pair reads the null. Δ0 is still the natural size of the
  challenge, so every resolution is also printed in units of |Δ0|.

## 5. The adaptation readout: the common garden (item 4)

**Why not the class rule, the recovery rule or survival.** RBT-92 and RBT-99's adversaries showed:
- the class rule reads the lead's level;
- recovery d = 0 is an artifact;
- survival is uninformative;
- a paired income step can be arithmetic.

A common garden sidesteps all four:
- it measures **genotypes**, not a lifetime mean of the survivors;
- every population is scored on **the same worlds, at the same price, by the same bout**;
- it is read at **one pre-registered depth**.

In this ecology genotype is phenotype (no lifetime learning across seasons), so a garden difference between two
living populations is a difference in who is alive. That can arise by sorting of standing variation or by new
variants, and §5.4 prints the split.

### 5.1 The instrument (`garden.py`)

- **Population:** every individual of fauna f alive at season s in arm a (RBT-92's `Arm.alive_at` on
  `lineage-last.txt`), each loaded from `a/f/genomes/NAME.json`.
- **Worlds:** eight, j = 0…7. Terrain and start seeds come from `default_rng([107, 1000 + j])`. The grouping, a
  permutation of the population sorted by name into groups of four, comes from `default_rng([107, j])`. The same
  worlds serve every population, arm, seed and season.
- **Each world twice,** on the baseline's random terrain (that terrain seed) and on flat ground, with the same start
  seed and the same groups.
- **The bout is the ecology's:** `BoutRunner.run_groups` on the RBT-90 base config's `sim`, with gain =
  items − work_cost × kJ, and an exploder gains 0.
- **G_a^w(s)** is the mean gain per robot-bout over the population and the eight worlds.
- One row per individual is written to `garden/LABEL.txt`, a few kilobytes. It is committed.

### 5.2 The statistics, per seed and fauna, at s* = T + 800 (scored)

- **A_SB = G_S^flat − G_B^flat.** Flat-lived against furniture-lived, both on flat ground.
- **A_SN = G_S^flat − G_N^flat.** Flat-lived against cull20: same seed, same T, same depth, a turnover shock of a
  third, and no terrain change.
- **A_NB = G_N^flat − G_B^flat.** The null's own size (printed).
- **I = (G_S^flat − G_S^random) − (G_B^flat − G_B^random).** The specialisation: flat relative to furniture. Its
  null, I_NB, is printed.
- Also printed, not scored: **G_S^random − G_B^random**, whether the flat-lived fauna lost its furniture skill.

### 5.3 The verdict, per fauna (`readout.py`)

- **ADAPTED:** mean A_SB has its t(n−1) 95% interval above 0, **and** mean A_SN has its interval above 0.
  - **SPECIFIC** if I's interval is also above 0. The flat-lived fauna gained on flat ground relative to furniture:
    adaptation to *this* change.
  - **GENERAL** otherwise. It is better on both grounds: selection on open ground improved foraging in general, or
    selected harder. It is still a response to the challenge, and the report says which.
- **MALADAPTED:** both intervals below 0.
- **NOT SEEN:** otherwise. It is always printed with the **resolution**: the smallest true A the rule detects on
  ≥ 80% of replicates on the realised null (`readout.py mde`), and that as a multiple of |Δ0|. A bare NOT SEEN is
  never written, and it never reads as "did not adapt".
- **UNREAD:** fewer than 6 seeds.
- **No sign guard** (RBT-101 §6.3's reasoning): two intervals against two independent references stand in for it.
  The sign counts are printed.
- **Gates, printed first:**
  - V-EXT, every arm's `prefix.txt`;
  - V-G, every garden population complete (n = `seasons.txt` alive at s);
  - C0 identical across arms (RBT-92's V0);
  - DEPTH.

  **If any gate fails, nothing below it enters a sentence.**

### 5.4 Printed, not scored

- **The trajectory:** A_SB, A_SN, A_NB and I at T + 200, 400, 600 and 800. That is how the response builds with
  depth, if it does.
- **Sorting against novelty.** From the C0 rows, each C0 member's garden value is weighted by its share of the
  ancestry of P_S(s*) and P_B(s*) (RBT-92's `anc0`, every parent followed). This is the value pure sorting of C0
  would give. The residual, (G_S − sort_S) − (G_B − sort_B), is the part carried by what C0 did not have. It is
  approximate (ancestry shares, not an additive model) and is labelled so.

## 6. Positive control: C2 in the same garden (RBT-66's rule, before use)

**A readout is validated on a response it must see, on real bodies, before it is used.** RBT-101 installed a reflex.
Here the control is a real response:
- RBT-99's C2 raised the price 0.03 → 0.08 per kJ at T.
- By 599 both faunas had recovered part of that price net of the arithmetic: co-evolved +0.21, designed +0.52
  (RBT-99 REPORT, F2).
- RBT-99 could not say whether that was a genotypic response or survivor-conditioning. **The garden can**, because it
  prices both populations at 0.08 on the same worlds.

The arithmetic cancels exactly as in §5. **The control reads A_SB(C2) = G_{C2 shift}^{0.08} − G_{base}^{0.08}** at 599
(d ≈ 240, about 6.5 events), on random ground, all ten seeds for the co-evolved fauna and the survivors for the
designed. `garden_run.sh c2control`, `design_power.txt`:

| seed | 801 | 804 | 805 | 806 | 807 | 1 | 2 | 3 | 4 | 7 | mean, 95% t(n−1) | positive |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| co-evolved A_SB(C2) | +0.15 | +0.45 | +0.38 | +0.08 | +0.03 | +0.24 | +0.04 | +0.38 | +0.43 | +0.04 | **+0.221** [+0.097, +0.345] | **10/10** |
| designed A_SB(C2) | +0.35 | +0.44 | +0.50 | extinct | extinct | +0.66 | extinct | +0.33 | +0.84 | +0.14 | **+0.467** [+0.252, +0.681] | **7/7** |

- **PASS** (pre-registered): the co-evolved A_SB(C2) interval is above 0 at n = 10.
- **What PASS certifies:** the garden detects, at n = 10 and d ≈ 240, a genotypic response of the size one real
  selection pressure produced here. That is the instrument's sensitivity on a response we know exists.
- **What it does not certify:** that C4's response, if any, is that large.

**Result: PASS on both faunas** (co-evolved at n = 10; designed at n = 7).

**What it says, and its limits:**
- **The instrument sees a real genotypic response in this ecology at ~6.5 events.**
- **It is also, in passing, a result about C2.** Priced alike at 0.08, the populations that lived under the dearer
  work earn more than the base's: +0.22 co-evolved, +0.47 designed. That is **net of the arithmetic that decided
  RBT-99**. So C2 did produce a response in who is alive, whether by sorting of standing gait or by new variants
  (§5.4's split would tell). **"C2's effect is price arithmetic"** (RBT-99 F2) is right about the *paired income
  contrast*. It is not the whole story of the populations.
  - This is a design-stage control, not a registered C2 readout.
  - The designed figure is on the 7 surviving seeds, a subset that extinction chose.
  - I flag it to the coordinator as a candidate for its own short, registered readout. It needs no arm, only
    garden populations.
- **The control is a one-contrast test (S − B), on random ground at 0.08.** C4's rule needs two intervals, on
  flat ground at 0.03, where the co-evolved null is wider (RMS 0.39, §8). **A co-evolved response of C2's size,
  +0.22, would sit below C4's co-evolved resolution** (0.44 at d ≈ 240, §9). It would be NOT SEEN there. A
  designed response of C2's size, +0.47, would be seen (resolution 0.19 to 0.34).

## 7. Secondary: the paired income trajectory (the ticket's example)

- **D_SB(s) = x_S(s) − x_B(s)** on `mean_lifetime_score`, with an extinct fauna earning 0 (RBT-92's ruling).
- **The statistic:** its least-squares slope over [T + 200, T + 800], per 100 seasons, per seed and fauna. The matched
  null is the slope of D_NB.
- **RISING:** the slope_SB interval and the (slope_SB − slope_NB) interval are both above 0. **FALLING:** both are
  below 0. Otherwise **FLAT (not resolved)**.
- **Printed beside it:** the residual level, mean D_SB over [T + 700, T + 800) minus Δ0, and over RBT-101's
  recovery window [T + 60, T + 160). That is the paired income net of the arithmetic.
- **Why secondary:** income is a lifetime mean of survivors in a same-fauna group of four. It carries
  survivor-conditioning and group effects that the garden removes. It is kept because the ticket asked for it, and
  because a garden response with no income trace (or the reverse) is itself a finding.

## 8. The null (item 5)

1. **cull20 − base, on every seed: the scored null.**
   - It is matched in seed, founders, worlds, T and depth.
   - It diverges at T through a turnover shock of a third, with no terrain change.
   - It is harsher than an A/A (it removes 20 of each fauna), so its spread is, if anything, an over-estimate. That
     makes A_SN conservative.
   - **Measured at d ≈ 240 now** (`design_power.txt`, `garden/*-s599`): 

  | | A_NB = G_N^flat − G_B^flat | RMS | drift sd per arm | I_NB | RMS |
  |---|---|---|---|---|---|
  | co-evolved | +0.163 [−0.103, +0.428], 7/10 | **0.388** | 0.274 | +0.036 [−0.131, +0.203] | 0.224 |
  | designed | −0.003 [−0.128, +0.121], 6/10 | **0.165** | 0.117 | +0.066 [−0.037, +0.169] | 0.152 |

  - **The co-evolved null is heavy-tailed.** Seed 3 alone gives A_NB +1.15: its **base** population at 599 earns
    +0.44 on flat ground against +0.86 on furniture. That is a furniture-dependent population produced by drift
    since T, which C0 was not: C0-3's Δ0 is +0.13. Without seed 3 the co-evolved RMS is about 0.14.
  - That population is exactly the phenomenon the ticket is after ("a gait tuned to furniture"), arising in the
    *base*. It is also why the co-evolved garden is noisy. The readout prints a leave-one-seed-out line under each
    verdict (not scored).
  - **Designed:** the null is centred on 0 and moderate.
2. **RBT-101's k-cull** on 801, 1, 2 and 4, extended too.
   - A cull of 1–3 robots of one fauna is the closest A/A in the committed data (RBT-92 adversary F5). The other
     fauna stays byte-identical to base (RBT-92 F10).
   - G_cull^flat − G_base^flat at T + 800 is printed, report-only.
3. **RBT-105's founder-sharing replicates**, report-only.
   - Its `aa_spread.txt` is printed verbatim if committed by the readout. It is not committed at this writing, and
     was due about 20:00 UTC.
   - Better for this readout: **the replicates diverge from season 0, so at season 599 they are ~17 events apart**
     (the base rate, §3). That is close to s*'s ~22. A garden on each replicate's holistic fauna at 599
     (`garden_run.sh aa105`), against the original, is **a depth-matched A/A for the co-evolved fauna**. It is
     printed as an RMS beside A_NB.
   - The designed fauna is byte-identical across RBT-105's replicates, so it has no A/A there.
4. **How the null enters the rule:** through A_SN's interval (a per-seed paired reference) and through the realised
   resolution (§5.3). **It never enters as an assumed figure.** The design-stage spread is used for the power line
   below and nowhere in the verdict.

## 9. Power (on the measured null)

`design_power.txt`, by `readout.py`'s own `mde`. Under the null each arm's G is μ_seed + e_arm with e iid
N(0, s²). So A_SB and A_SN share e_S, and var(A_NB) = 2s². The simulation runs 1000 replicates per step:

| fauna | n | resolution, null as measured (d ≈ 240) | × \|Δ0\| | null scaled to d = 800 | × \|Δ0\| |
|---|---|---|---|---|---|
| co-evolved | 10 | 0.439 | 2.7 | 0.801 | 4.9 |
| co-evolved | 8 | 0.507 | 3.1 | 0.926 | 5.6 |
| co-evolved | 6 | 0.631 | 3.8 | 1.151 | 7.0 |
| **designed** | **10** | **0.187** | **0.25** | **0.342** | **0.45** |
| designed | 8 | 0.216 | 0.29 | 0.395 | 0.52 |
| designed | 6 | 0.269 | 0.36 | 0.491 | 0.65 |

Also measured, for scale (`design_power.txt`):
- The standing between-individual sd of flat-specific income in C0 is 0.41 co-evolved and 0.73 designed. These are
  medians over seeds, and upper bounds because they include world noise.
- The base's own movement on flat from C0 to 599 is co-evolved −0.06 [−0.28, +0.17] and designed **+0.14**
  [−0.06, +0.35], 8/10. The base keeps evolving, which is why A_SB is measured against B at the same depth and not
  against C0.
- The same two-interval rule on the specialisation I, not scored: co-evolved 0.25 (0.46 scaled), designed 0.17
  (0.31 scaled).

- The null at d = 800 is not measurable now. I scale the d ≈ 240 null by √(800/240) = 1.83, on the assumption that
  neutral divergence variance grows linearly with depth. **This is an assumption.** The readout uses the realised
  null at d = 800.
- **In words:** **the designed fauna is where "can adaptation be seen at all" is answerable.** At 22 events the
readout sees a designed response of about **0.34 income per bout**, less than half of the challenge's own step Δ0.
**The co-evolved fauna's garden is close to blind.** It resolves only a response several times its small Δ0,
because the co-evolved populations wander far more between arms than flat ground moves them. A co-evolved NOT
SEEN will say exactly that. **This is stated before any arm, so a co-evolved NOT SEEN cannot be read as "the
co-evolved body did not adapt".**

## 10. Predictions, with confidence, and the falsifier

Scored as mine, against `readout.txt`.

| prediction | point (range I expect) | confidence |
|---|---|---|
| **designed verdict at T + 800** | NOT SEEN 0.60, ADAPTED-SPECIFIC 0.15, ADAPTED-GENERAL 0.15, MALADAPTED 0.10 | as listed |
| **co-evolved verdict at T + 800** | NOT SEEN 0.85, ADAPTED (either) 0.10, MALADAPTED 0.05 | as listed |
| designed A_SB at T + 800 | **+0.15** (−0.10 to +0.40) | 0.6 that it lies in the range |
| co-evolved A_SB at T + 800 | **+0.05** (−0.30 to +0.40) | 0.6 |
| designed I at T + 800 | **+0.05** (−0.15 to +0.25) | 0.6 |
| income, secondary | FLAT on both faunas | 0.75 designed, 0.85 co-evolved |
| residual level, designed, [T+60, T+160) (D_SB − Δ0) | within ±0.25 of 0 | 0.6 |
| DEPTH: median few-births depth at T + 800 ≥ 15, both faunas in S | ~22 | 0.9 |
| the null's own mean, A_NB at T + 800, interval covers 0 | | 0.8 co-evolved, 0.85 designed |
| every V-EXT gate passes on all 34 continuations | | 0.9 |

**Why these numbers:**
- **For a designed response:**
  - flat ground changes the designed body's world a lot (Δ0 = +0.75);
  - the standing flat-specific variation is large (sd ≤ 0.73);
  - 22 events of selection on it is real depth;
  - the readout resolves ~0.34.
- **Against:**
  - the designed body is fixed, so only its brain can respond;
  - the base keeps improving on flat by itself (+0.14 in 240 seasons), and A_SB is net of that;
  - the co-evolved null shows that populations wander;
  - RBT-101's own control showed acquired wiring near its noise at 5 events.
- **The co-evolved call is mostly the instrument:** at 2.7–4.9 × Δ0 resolution, NOT SEEN is nearly assured
  unless the response is very large.

**The falsifier, in the ticket's terms.** The ticket asks whether adaptation is visible at all, given depth.
- **My answer, pre-registered: on C4, at ~22 events, probably not at the resolution this instrument has** (NOT SEEN on
  both faunas, 0.6 × 0.85 ≈ 0.5 jointly).
- **Falsified by:** an **ADAPTED** verdict on either fauna at T + 800, with every gate passing and the C2 positive
  control PASS (§6).
- **My most exposed single claim is "neither fauna returns ADAPTED, SPECIFIC" (0.80).** It is falsified if either does.
- **A NOT SEEN on both is not a negative for adaptation in general.** It is an exclusion: "no flat-ground response
  larger than X income per bout at ~22 events", with X the realised resolution. For the designed fauna that is a
  statement worth having (X ≈ 0.45 |Δ0|). For the co-evolved it is not, and it is written so.

## 11. Cost and packing (item 6)

- **Per continuation:** ~600 seasons, plus 52 on shift-804, 1 on shift-805 and 35 on cull20-806. At two arms per
  four-core session with WORKERS=2 each, that is **~10.2 s per season per arm** (RBT-105 `waves.txt`, measured).
  So **~1 h 45 min per session.** Workers do not change a run.
- **34 continuations → 17 sessions**, in two waves of ≤ 10 (`waves.txt`):
  - **Wave 1**, 10 sessions: the 10 shift and 10 base continuations, the scored contrast A_SB.
  - **Wave 2**, 7 sessions: the 10 cull20 and 4 k-cull continuations, the null.
- **Packing:** two arms of *different* seeds per session, so a lost container never takes both sides of one seed's
  contrast.
- **Garden, after the arms:** per seed, 2 C0 + 3 arms × 4 depths × 2 faunas = 26 populations (8 more on the four
  k-cull seeds), plus 16 RBT-105 replicate populations. About 140 core-seconds each, so **~11 core-hours**: ~20 min
  per seed on a four-core session, or ~3 h on one. `garden_run.sh readout SEED` in the session that holds the seed's
  bulk, or after `durable.sh restore`.
- **Total: about 30 session-hours of arms and 3 of garden. Wall: about 3 h 40 min** (two waves of 1 h 45 min),
  plus the garden.
- **One platform:** the same container image, numpy 2.4.6 and mujoco 3.14.0. Every session records
  `pip freeze | grep -iE 'numpy|mujoco'` in its first ticket comment.
- **durable.sh:** `extend_arm.sh` starts `every 20` beside the run with DURABLE_WATCH_PID, and saves once more after the
  post-run step (README rule 6). Name the label on RBT-107 at launch.
- **Per arm, commit:** `config.json`, `extension.txt`, `seasons.txt`, `lineage-last.txt`, `bodysig.txt`,
  `events.txt`, `groups.txt`, `wiring.txt`, `prefix.txt`. Then `garden/*.txt` and, once, `readout.txt`.

## 12. What is committed now

- `PREREGISTRATION.md` (this file).
- The depth measurement: `depth.py` → `depth.txt`.
- The checkpoints: `ckpt_check.sh` → `ckpt_check.txt`.
- The extension check: `extend_check.sh` → `extend_check.txt` (throwaway) and `ckpt_replay.txt` (the two real
  replays).
- The extender: `extend_arm.sh`, with the gate `prefix_check.py`.
- The instrument: `garden.py` and `garden_run.sh`.
- The design-stage garden: `garden/c0-*`, `garden/base-*-s599`, `garden/cull20-*-s599`, `garden/c2*-s599`.
- The readout, `readout.py`, and the power: `design_power.py` → `design_power.txt`.
- The packing: `waves.txt`.

## 13. For the adversary: where I am most exposed

1. **The garden is not the ecology.**
   - Groups of four of one population, on eight fixed worlds, are not the season's random worlds or its energy
     economy.
   - It measures what the genotypes do, not what they earn in their own history.
   - I argue that this is exactly what separates a response from arithmetic and survivor-conditioning. But a
     response that exists only through the ecology's dynamics, such as frequency dependence within the group, is
     invisible to it.
2. **cull20 is not an A/A.** A third of each fauna removed at T is a bigger perturbation than drift. If it moves
   G^flat systematically (a bottleneck that lowers quality), A_SN is biased *up*. The k-cull and RBT-105 lines are
   there to check that. The readout prints mean A_NB, and a mean A_NB interval off 0 is a flag I will report.
3. **The null is scaled for power** (√depth), not measured, until the readout.
4. **ADAPTED, GENERAL is a response I could call adaptation too generously.** "Selection on open ground selected
   harder" is a response to the challenge but not a new skill. The report names which, and only SPECIFIC is
   "adapted to flat ground".
5. **Sorting against novelty (§5.4) is approximate.** It is printed, not scored.
6. **Depth** assumes the post-600 rate equals the 240-season rate measured. The readout re-measures it.
7. **The positive control is at d ≈ 240 and on a price challenge.** It certifies sensitivity to a response of that
   size, not to a flat-ground response of any size.
