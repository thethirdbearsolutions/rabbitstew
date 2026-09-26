# RBT-100 pre-registration: epoch C3, scarce food, on RBT-92's instrument

**Designer's pre-registration, 2026-09-26, before any RBT-100 arm exists.** The ticket is RBT-100 and the branch is `results/RBT-100-design`. I designed this and will run no full arm. The only run made for it is a 20-season throwaway at seed 801 with the event at season 10 (§3.6). It was read for the byte check and the pipeline's exit status only.

**Design rule: this is RBT-92's instrument, used unchanged, with one flag changed.** I read RBT-92's pre-registration (12:42 UTC, PR #74, `292d6c5`), its Amendment 1 (`a3658f9`, PR #76), the coordinator's notes (12:43, 12:55) and the senior review (13:20). **Everything below that is not marked "C3" is RBT-92's and is not restated.** Where RBT-92's adversary round, its answer or the senior review's fixes change that instrument, C3 inherits the change. The mechanism is §1.2, and each inherited change is recorded in an amendment here (§10).

## Summary

| | |
|---|---|
| challenge | **C3, scarce food:** `--shift-at T --shift food-items=6` (12 → 6 items in the 3 m disc) |
| seeds | RBT-92's: **all ten** of RBT-90 part 2 (801 804 805 806 807 1 2 3 4 7). The rule was committed at `66f5ab3` before any part 2 output was read. The only exclusion is extinction by T − 1. |
| baseline (control) | the seed's RBT-90 part 2 arm. It is byte-identical to the C3 shift and cull arms before T (§3.6). |
| T | **RBT-92's T per seed**, read from `runs/RBT-92/onset.txt`: same rule, same baseline, same number |
| new arms per seed | **shift** (C3) and **cull** (the null; k by RBT-89 §8's rule on C3's shift arm). **cull20 is RBT-92's arm and is reused**: it is the same command at the same seed and T. |
| windows | RBT-92's: transient [T, T+60), **recovery [T+60, T+160) primary**, tail [T+160, T+200) |
| verdict | RBT-89 §9 classes A–F on R-body in the recovery window, by RBT-92's `readout.py`. r is the t(n−1) 95% half-width. |
| falsifier | **"the designed body wins on the held-out challenge"**: class C |
| prediction | **class D (designed bankrupt), 0.45**, reached through the 12-of-60 floor rather than income. A 0.30. |
| cost | 20 arms × 600 seasons, **about 21 session-hours**; about 1 h 50 min wall on 20 four-core sessions |

## 1. The instrument, reused

### 1.1 What is reused, file by file

| RBT-92 file | C3 use |
|---|---|
| `SEED-RULE.md` | unchanged: all ten seeds |
| `onset.py` → `onset.txt` | **read, not re-run**: `runs/RBT-100/run_arm.sh` and `readout.py` read `runs/RBT-92/onset.txt` |
| `cull_k.py` | unchanged; run as `python runs/RBT-92/cull_k.py SEED runs/RBT-100/shift-SEED > runs/RBT-100/cull-k-SEED.txt` |
| `tables.py` | unchanged; run as `python runs/RBT-92/tables.py runs/RBT-100/ARM-SEED` |
| `readout.py` | **imported and run unchanged** by `runs/RBT-100/readout.py`, which redirects shift and cull to `runs/RBT-100/`, cull20 and the baseline body digests to `runs/RBT-92/`, and V1's k file to C3's own, then prints the C3 lines (§6) after RBT-92's verdict |
| `cull20-SEED/` | **RBT-92's arm is C3's cull20**: the command does not depend on the challenge, so RBT-92's cull20 at a seed is byte-for-byte the arm C3 would run (§1.3) |
| `base-SEED/bodysig.txt` | RBT-92's |
| `run_arm.sh` | C3's `runs/RBT-100/run_arm.sh` is it with `--shift group-size=8` → `--shift food-items=6`, no cull20 case, and T from RBT-92's `onset.txt`; the ecology command line is identical (checked by diff) |
| `shared_baseline_check.py` | C3's imports its comparison functions unchanged and replaces only the manipulation check, because C1's check (groups of eight) does not apply to a change in the item count |

### 1.2 How changes to the shared instrument reach C3

C3 has no copy of `onset.py`, `cull_k.py`, `tables.py` or `readout.py`. It runs RBT-92's files on the head it launches from. So whatever RBT-92's adversary round or the senior review's fixes (a) and (b) change in those files, C3 runs that change:

- **(a):** an extinct fauna earns 0 in every window.
- **(b):** T is chosen on pre-onset deaths only.
- The `lineage-last.txt` V0 extension.

Each such change is still **posted here as an amendment, with the commit, before any C3 arm launches**. That way the pre-registration a C3 report cites states the instrument it ran. One change would bind C3 without appearing in a file: if RBT-92's answer changes the seed set or the windows by ruling rather than by code, it is carried over by amendment in the same way.

### 1.3 Why RBT-92's cull20 serves C3

`--cull-at T --cull holistic=20,conventional=20` at seed s is the same command in both tickets. The ecology is deterministic at four workers (RBT-92 §3, and the coordinator's worker check). So a C3 cull20 would be RBT-92's arm again, byte for byte. V3 (the carriage instrument resolves a k = 20 cull) is a property of the instrument and the seeds, not of the challenge. **If V3 fails on RBT-92's cull20 arms, the carriage lines of C3's readout print as UNVALIDATED**, exactly as they would for C1. RBT-99's description asks for the same arrangement ("cull20 only if RBT-92's V3 needs it per challenge; otherwise cite RBT-92's"). V3 does not need a per-challenge cull, for the reason above.

**Dependency:** C3's readout cannot run before RBT-92's cull20 arms and `base-SEED/bodysig.txt` are committed.

## 2. C3: the protocol's words, quoted verbatim (`docs/held-out-challenges.md`)

The row for C3 in §2's table:

> | **C3** | scarce food, at the bootstrap line | `--food-items 6` | co-evolved starved out by season 15; designed bottlenecked to 11 by 17 and extinct at 51 (`docs/foraging-world.md`, "Six items") | in principle by `food`; the evolved side does not read it | budget |

The claim tested for C3 (§2, C3). It refers to C2's, so C2's is quoted beneath it:

> **Claim tested:** as C2, survivorship at a boundary, here the bootstrap line for food; whether an
> established population holds where random founders could not. Not the owner's contest claim.

> **Claim tested:** survivorship of the co-evolved population at an economic boundary the designed
> body's budget is not expected to survive. That is a different claim from the owner's (it is about
> one body's cheapness, not two bodies' contest), and a C2 result is reported as such.

The protocol's expectation for C3 (§2, C3):

> **C3, like C2, is expected to bankrupt the designed population first**,
> and a future arm predicts that in its template. The untested question C3 poses is whether an
> *established* population, unlike random founders, can hold at the bootstrap line: the six-item arm
> above is the founders' number, not an evolved population's.

The statement required in every C1–C3 pre-registration (§3), in its words:

> - **C1, C2 and C3 are unperceived.** C2 by construction (no sensor reads energy or work); C1 and
>   C3 because the sensor that could read them is carried and not wired on the evolved side, and,
>   on the designed side, wired at magnitudes that do not steer. **These challenges select on
>   standing morphology and gait only.** "Robust against a novel challenge" then means
>   **survivorship of standing morphology and gait through a shift, not adaptation during it** (the
>   words of the RBT-91 decision), which is faithful to Gould, whose events select on what is
>   already there. This must be written in every C1–C3 pre-registration in those words, and the
>   axis (§6) and the falsifier (§9) are claims about realised income, never about perception: a
>   class-A result says the co-evolved body earned more under the shift, not that it sensed the
>   shift.

So, for C3: **this challenge selects on standing morphology and gait only. Robust means survivorship of standing morphology and gait through the shift, not adaptation during it.** The axis and the falsifier are claims about income, not perception. RBT-97 §1 (a compass pays when installed) changes none of this, because no standing population carries a paying compass.

Class D's rule for C3 (§9, "Rules that bind the classes"):

> - **Class D is not a win, and it is tested by income, not by extinction.** A challenge that
>   bankrupts the designed body measures its energy budget (C2 and C3 are expected to; §2), which is
>   a fact about wheels at 14–29 kJ, not about the co-evolved body's robustness. A comparator that
>   survives at four robots on 0.05 a season is bankrupt in every sense but the literal one, and the
>   D test says so; class A is reachable only against a comparator that is neither extinct, nor
>   below a fifth of capacity, nor below its basal cost. It is reported as D, with the co-evolved side's own R-shift beside
>   it, and the sentence "holds up against the challenge" is earned only if the co-evolved side's
>   income in the recovery window is within r of its control (R-shift ≥ −r). Otherwise it is
>   "outlasts a bankrupt comparator", which is a different sentence.

The readings this protocol forbids (§14), verbatim:

> The adversary's brief is to find the reading a hopeful author could still take. The ones this
> document has tried to close:
>
> 1. **Picking the challenge after seeing the population.** The set is fixed here; an arm names its
>    challenge from §2 before its control arm runs.
> 2. **Choosing a challenge that bankrupts the comparator and calling it a win.** Class D exists for
>    C2 and C3, is tested by income and by a capacity floor and not only by extinction (the
>    adversary's finding: an extinction-only D let a four-robot starving comparator read as class A),
>    and "holds up" needs R-shift ≥ −r on the co-evolved side.
> 3. **Reading the champion where the population lost.** The axis is population income; the bests'
>    two-to-one reversal at eight robots (RBT-17) is not R-body.
> 4. **Choosing the readout window after the curve is drawn.** Windows are fixed relative to onset;
>    "disruption curves are the most readable curves there are" (*Research goals*, cautions).
> 5. **Reading the transient.** Onset is placed off the measured cohort cycle; the recovery window is
>    primary; a class-A result at the transient is class F.
> 6. **Calling a draw what the instrument could not see.** Class B requires r ≤ 0.10; otherwise F.
> 7. **Pooling a perceived challenge (C4) with the unperceived three.** Reported separately.
> 8. **Pairing by seed without the streams.** The ecology's per-fauna streams landed (RBT-95) and
>    the three arms of a seed are paired on founders, worlds and each fauna's own draws; an arm that
>    merges the faunas says the comparator's income and demography are covariates after the merge.
> 9. **A graft that is not a graft.** The comparator's brain comes from the same run, same seasons,
>    same operator; nothing loaded, nothing constant.
> 10. **"Re-adapts" for what is sorting.** Depth inside the recovery window is ≈ 5 events; the
>     report uses "survives" or "is sorted" unless a lineage can be shown to have acquired something
>     it did not carry at onset, by RBT-84's descent tracer, which runs across the onset now that
>     descent is intact (§5).
> 11. **A run made for this document.** None was. Every number above is cited or is labelled
>     arithmetic on cited numbers.

**What C3 adds to the list, for its adversary:**

- **12.** Reading "the co-evolved population held at the bootstrap line" when the comparator was bankrupt. That is class D with the co-evolved side's R-shift beside it: "outlasts a bankrupt comparator", not "holds up" (§5).
- **13.** Reading the recovery-time metric as the population "not recovering". Under a budget shift the pre-event plateau was earned at twice the density, so it is out of reach by arithmetic (§3.5).

## 3. C3: does halving the food, and what happens to the food after the shift, change the onset rule's assumptions? (ticket item 3)

**Short answer.** The onset trough rule is untouched. It reads only baseline (or pre-onset) deaths, and it protects the onset season, which the shift cannot reach. The windows stay valid as defined, because `max_age` is not the flag. **Three readings built on C1's shape of disruption do not carry over, and the design says so rather than tuning anything:**

- the ten-season k window (§3.3);
- the 60-season wave's phase after T (§3.4);
- the recovery-time metric (§3.5).

The class rule is not changed by any of them.

### 3.1 What actually changes after the shift: the count, not the structure

The premise was checked against the code first, per the protocol's rule: "a ticket's premise is checked against the record it cites".

- **There is no patch structure to change.** The baseline runs `patches = 0` and `regrow_delay = 0` (`FoodConfig` defaults, `rabbitstew/simulation.py:57–59`; the baseline command sets neither). Food is laid fresh for every bout, uniformly over the disc, from the bout's start seed (`set_food_seed`, `simulation.py:375–385`). An eaten item regrows **instantly** at a fresh uniform spot.
- **`--shift food-items=6` changes `food.items` and nothing else.** The shift code refuses an items shift in the persistent world, where food state would carry across seasons (`rabbitstew/ecology.py:381–383`). In this world it is legal because nothing carries.
- **So after T the standing crop is exactly six items throughout every bout.** Nothing depletes and nothing regrows slowly. The density halves exactly, which is the condition the protocol's mower arithmetic ("path × twice the eat radius × the food density") needs.
- The terrain stream still draws once a season (`ecology.py:462–465`), so every arm's start seeds, and with them each bout's food seed, stay paired with the baseline's season by season.
- **One side effect belongs to the flag and is not controlled:** the `food` sensor sums `exp(−d/decay)` over the items and squashes the sum (`smell = "sum"`). Six items give a lower reading than twelve. A designed nose wired as a brake, throttle or sweep modulator (RBT-66) receives a shifted input. That is part of C3 as the protocol defines it (one flag), not a second change. It is not perception in §3's sense.

### 3.2 The onset trough rule: unaffected

The rule chooses T from the seed's baseline deaths. It uses RBT-92's window, or pre-onset deaths only if the senior review's fix (b) is adopted, and either is inherited (§1.2). **No quantity it reads is produced by a C3 arm**, so C3 cannot move T. What the rule assumes is that the onset should not sit on the baseline's own 60-season mortality wave (`runs/RBT-92/cohort_cycle.txt`: a lag-60 peak on 12/12 population-runs). That is a property of the baseline, not of the challenge, and it holds for C3 as for C1. T is shared with RBT-92 by reading its `onset.txt`.

### 3.3 What does change: C3's excess mortality is recruits starving while residents spend a hoard (rewritten in Amendment 2)

*The text posted at `c456dd0` said energy is "at most a little above the birth threshold of 3" and put the deaths "3 to 30 seasons after T". Adversary round 1 (F1) showed from the code and a probe that both are wrong. This section is the corrected mechanism; the original is in git.*

- **Energy is uncapped.** A breeder breeds only into a free slot (`ecology.py:498–507`), and at capacity slots open only through deaths. An established robot therefore banks most of its surplus. The adversary's probe P1 measured, at T−1 on an established population (seed 901, T = 100, not a C3 arm): holistic mean **10.7** a head, designed **16.0**. RBT-19's committed persistent-world history gives about 27 and 18.
- **So the residents do not die first.** After the shift they live off the hoard for tens of seasons, and keep breeding into every slot a death frees. **Their newborns start at energy 1 and starve** before reaching 3. In P1, 371 of the designed shift arm's deaths over [T, T+60) were starved recruits, against 31 starved residents and 29 aged out (the plain arm: 57, 10, 50). *Corrected in Amendment 3 from 267 and 21, the adversary's erratum to its own P1 counts (re-check, PR #105).*
- **The alive count can hold flat for about 40 seasons** (P1: designed 60 through T+30, 44 at T+55), and the births deficit can be negative. The shift arm breeds more, into the slots its starving young free.
- **So the collapse, if it comes, comes when the hoard is spent**, at or after T+40, and at a registered T (340–395, with larger hoards than P1's) most likely inside the recovery window [T+60, T+160).

**Consequence for the null (F1, F2).** k counts excess deaths over [T, T+10), which under C3 are mostly starving recruits. The cull arm removes k individuals at random at T, mostly established residents carrying 10–16 energy, from a population that refills from other hoarders' births. **The shift and its null differ in who dies, not only in how many**: the shift keeps every resident and starves the young; the cull removes residents and lets the young live. **k's rule is the protocol's and is not changed.** But for C3, R-null is not "a same-size cull"; the report states what it is: a random impulse on residents, against a starvation of recruits.

- **C3's turnover guard is not interpretable, a priori.** The income loss is density arithmetic, not turnover (§4), and the null is the wrong shape. Part 1 still prints RBT-92's guard line; part 2 says it is not interpretable, and it enters no sentence.
- **NULL is printed as diagnostics only.** Excess deaths (shift − base) over [T, +10), [T, +30), [T, +60), split by cause (starved or aged) and by cohort (born < T, born ≥ T); the births deficit; the alive deficit at T+10, +30, +40, +60 and +100.
- **The UNDERSIZED test is dropped.** It could not fire where it was needed: in P1 the alive deficit at T+30 was 0 against k = 26 designed and 9 holistic.

### 3.4 What does change: the 60-season wave after T (corrected in Amendment 2)

- **The windows stay valid.** `max_age` = 60 is not the flag, so everyone alive at T is dead by age by T+60, and the transient window keeps its meaning. The recovery window is still "the first hundred seasons in which nobody alive evolved under the baseline".
- **The wave's phase after T is not the baseline's.** The designed collapse starts when the hoard is spent, at about T+40 or later (§3.3). Whoever refills after it is born at about T+40 to T+100 and ages out at about **T+100 to T+160: across the whole recovery window**, not only its opening (the text at `c456dd0` said T+60 to T+90; F4).
- The baseline's own waves also cross that window (T sits half a period after the last baseline wave, so they fall at about T+30, T+90, T+150; Amendment 1). So both arms carry waves in the recovery window, **at different phases**.
- **On a designed fauna shrunk below about 20 alive, RBT-89's 20/60 peak threshold cannot be reached at all.** "No peak" there is uninformative.
- **Consequence.** The cohort-cycle reading is **not** read off a C3 shift arm as if it were the baseline's cycle. ECHO prints the post-onset peaks per arm, fauna and seed, and counts the seeds where the shift arm has a holistic peak starting inside the recovery window, against the baseline. If shift has one on ≥ ⌈0.8n⌉/n seeds and base on fewer, the report says **"the recovery window contains the shift's own echo"** beside the class. The class is not changed.

### 3.5 What does change: the recovery-time metric is out of reach by arithmetic

"Recovery to the pre-event plateau" (RBT-92 §6: within 2 SD of the [T−100, T) mean for 20 seasons) was meant for a shock the population might absorb. Under C3 the plateau was earned at twice the density. The arithmetic in §4 puts post-shift income 0.4–0.7 below it on both faunas, against an h of order 0.1–0.2. **So "none" is expected on both faunas and every seed, and it is a statement about the density, not about recovery** (forbidden reading 13). It is printed as RBT-92's readout prints it and enters no sentence about robustness. The paired form (shift − base) is in the same position.

### 3.6 The shared baseline for C3's shift, and the smoke run

- **Byte check:** `runs/RBT-100/shared_baseline_check.txt`.
- **Runs:** `shared_baseline_runs.sh 801`. These are three 20-season runs (plain; `--shift-at 10 --shift food-items=6`; the k = 20 cull at 10), throwaway and not committed.
- **Pipeline:** `runs/RBT-100/smoke.sh 801` → `smoke.txt`. It ran RBT-92's `tables.py` and `cull_k.py` and C3's `readout.py` end to end on those runs, with shrunk windows. **Read for nothing:** numbers are withheld and only exit status and section headers are kept.
- **Results.** The byte check is **PASS**: the C3 shift arm and the cull arm are byte-identical to plain before season 10 in `lineage.jsonl` (1185/1185 lines, same sha256), `cohorts.jsonl` (20/20), `history.json` (20/20) and the born genomes (183). The configs differ only in the event fields. `food.items = 6` is recorded on every shift-arm entry from 10 to 19 and on no plain entry, and the groups stay at four. The smoke run is **exit 0** with no stderr, and every section and the C3-V1 gate printed. V3 "FAIL" at n = 1 on a 20-season run is expected and is read for nothing.

## 4. C3: the arithmetic the predictions rest on (not a measurement)

`mean_lifetime_score` under `--score food` is **net of work**: `food_eaten × value − work_cost × work_kJ` per season (`simulation.py:527`), averaged over each living individual's life. Basal cost 0.25 comes off after that. The cited inputs:

- holistic income +1.0 to +1.3 a season on 2–6 kJ (RBT-10 §5; `docs/held-out-challenges.md` §2, C2), so a work charge of 0.06–0.18;
- designed income +0.8 to +1.1 on 14–29 kJ, so a work charge of 0.42–0.87 (RBT-10 §2, §5).

Halving the density halves the **gross** food, not the work:

| fauna | gross now | gross at 6 items | net at 6 items (the axis) | net − basal |
|---|---|---|---|---|
| holistic, 2–6 kJ | 1.06–1.48 | 0.53–0.74 | **0.35–0.68** | +0.10 to +0.43 |
| designed, 14 kJ | 1.22–1.52 | 0.61–0.76 | **0.19–0.34** | −0.06 to +0.09 |
| designed, 29 kJ | 1.67–1.97 | 0.84–0.99 | **−0.03 to +0.12** | −0.28 to −0.13 |

**This is sharper than §2's C3 figure**, which halves the designed side's *net* income to 0.4–0.55. §2's own C2 paragraph shows that work is the designed body's larger cost, and a density shift leaves work where it was. So the typical designed robot is at or below basal after the shift. The typical co-evolved mower is above it.

**Survivor conditioning.** The axis is the mean over the *living*. Under a budget shift those below basal die within §3.3's buffer time, so the living mean is pulled up towards what breeders earn. In a population that persists it sits near or above 0.25 almost by construction. **So class D is expected to be reached through the 12-of-60 floor (or extinction) more often than through income.** The floor exists in RBT-89 §9 for exactly this case: "a comparator that survives at four robots on 0.05 a season is bankrupt in every sense but the literal one". The C3 readout prints which trigger fired, per seed and fauna (§6 CLASS D).

## 5. What the verdict means for C3, in the protocol's words

- **D** (predicted): the challenge exceeded the designed body's energy budget. It is reported **as D**, with the co-evolved R-shift beside it. The sentence is "**outlasts a bankrupt comparator**", unless co-evolved R-shift ≥ −r, which §4's arithmetic makes all but impossible (predicted "does not hold up", 0.95). It answers C3's own question only in the survivorship form the protocol asked for: **did an established co-evolved population hold at the bootstrap line where random founders starved by season 15?** That is read from the co-evolved side's alive and income lines, not from R-body.
- **A:** the co-evolved body earned more under the shift, both surviving above the floor. It is still "outlasts" unless R-shift ≥ −r. It is not the owner's contest claim (§2's claim line).
- **C:** the falsifier.
- **E:** neither holds.
- **B / F:** as RBT-92.

**For C3, B needs at least eight surviving seeds on the prior SD, as in C1.** A shrunken designed fauna widens the between-seed spread of R-body, so the realised r may exceed 0.10. The readout prints it before the class.

## 6. C3: what the readout adds (`runs/RBT-100/readout.py`, part 2; none of it changes the class)

1. **C3-V1:** the shift arm's `events.txt` records `{"flag": "food.items", "value": 6}` from T. This supplements RBT-92's V1, which checks only the season.
2. **NULL** (§3.3, as amended), diagnostics only: k; excess deaths over [T, +10), [T, +30), [T, +60) split by cause (starved, aged) and cohort (born < T, born ≥ T); births deficit over [T, +60); alive deficit at T+10, +30, +40, +60, +100; C3's turnover guard declared not interpretable. **CLAIM 3** as rescored (§9).
2a. **OWN** (Amendment 2, F3): from `own.txt` (`own_table.py`, written from each arm's bulk and committed), per seed, arm (shift, base) and fauna: stored energy a head at T−1, T+30, T+60; the season's own net over the survivors of the season in the transient and recovery windows; its upper bound over everyone who ran the season, the starved included; and "own net (all who ran, upper bound) below basal in the recovery window: k/n seeds" per fauna and arm.
3. **ECHO** (§3.4): post-onset 20/60 peaks per seed, arm and fauna, and the recovery-window count, shift against base.
4. **CLASS D triggers** (§4): per seed and fauna in the shift arm, the transient and recovery means, the minimum alive over [T, T+160), the extinction season relative to T, and which of the three triggers fired.
5. **DEPTH** (§7): median reproduction events after T along lineages alive at T+160, per arm and fauna.
6. **FOUNDERS** (Amendment 2, F5): per seed, the founders-at-six arm's outcome (HOLD if ≥ 12 co-evolved alive at season 59, else FAIL), the established co-evolved fauna's recovery-window reading (HOLD if its minimum alive over [T+60, T+160) is ≥ 12 and its survivors' own net there averages ≥ 0.25), and the contrast sentence "an established population holds where random founders could not" **only** on seeds where the founders FAIL and the established fauna HOLDS; counted k/n over the seeds whose founders fail.
7. **VERDICT TEXT** (Amendment 2, F6): after the class, verbatim, C3's and C2's claim lines, §3's unperceived statement, the owner's falsifier wording, the sentence the class rule picks (for D: "outlasts a bankrupt comparator" unless co-evolved R-shift ≥ −r), and forbidden readings 12 and 13. Pinned by `tests/test_rbt100_readout.py`.

## 7. Depth

Before the onset: 2T/60 = 11.3–13.3 events (T ∈ [340, 400]), as RBT-92. After it, C3 lowers depth: fewer births per individual, and breeding delayed until energy 3 is reached at half the income. The readout measures it from `lineage-last.txt` (§6.5). The prediction is shift ≤ base on the holistic side. **"Re-adapts" is at most about five, and likely fewer, sequential mutations in the recovery window**, so the report says "survives" or "is sorted" unless carriage traces a structure acquired after T (forbidden reading 10).

## 8. Point predictions, fixed before any C3 arm

All are read on the shift arm in the recovery window unless stated, on ten seeds.

**Class** (the readout's order: E, D, A, C, B, F):

| class | D | A | F | E | B | C |
|---|---|---|---|---|---|---|
| probability | **0.45** | 0.30 | 0.10 | 0.07 | 0.04 | 0.04 |

- **Class D, by trigger.** If D, the floor (min designed alive < 12 over [T, T+160)) fires on more seeds than either income trigger, 0.7. The designed fauna reaches alive = 0 by T+200 on **≥ 3/10** seeds, 0.5. Its minimum alive over [T, T+160) has a median of **9** (range 0–35).
- **Co-evolved.** It survives to T+200 on **10/10** seeds, 0.8. Its minimum alive over [T, T+160) has a median of **38** (range 15–60). Its recovery income has a median of **+0.48** (+0.33 to +0.65). It trips no D trigger on ≥ 8/10, 0.75.
- **Designed recovery income, living mean:** median **+0.28** (+0.10 to +0.45), survivor-conditioned (§4). Below 0.25 on ≥ 8/10 seeds, 0.2.
- **R-body:** before +0.12 (RBT-71); transient **+0.15**; recovery **+0.22** (per-seed −0.05 to +0.50), where both survive.
- **R-shift:**
  - holistic recovery **−0.60** (−0.85 to −0.35);
  - designed **−0.70** (−1.0 to −0.40), or lower if fix (a) scores an extinct fauna at 0;
  - holistic R-shift > designed R-shift (the co-evolved loses less), 0.65.
  - **"holds up" (holistic R-shift ≥ −r) not earned, 0.95.**
- **k** (`cull_k.py` on the shift arm): K1 median **2**/60 (0–12); K2 median **10** (0–30). *(The UNDERSIZED prediction posted at `c456dd0` is withdrawn with the test, Amendment 2.)*
- **Turnover guard** (printed, not interpretable for C3): holistic |R-null| ≥ r, 0.95.
- *Added in Amendment 2, after the adversary's probes P1 and P2, and labelled as such:* **CLAIM 3** (§9) holds, 0.75. Designed own net (all who ran, upper bound) below basal in the recovery window on ≥ 8/10 shift-arm seeds, 0.6; holistic on ≤ 2/10, 0.7. Co-evolved founders at six items FAIL on 3–7/10 seeds, 0.7 (P2: 2 of 4); designed founders FAIL on ≥ 8/10, 0.8. The contrast sentence prints on at least half of the seeds whose founders fail, 0.6.
- **Recovery time:** "none" on ≥ 9/10 seeds for both faunas in the shift arm, 0.85; cull ≤ 20 on ≥ 8/10, 0.7.
- **ECHO:** base has a holistic peak starting inside the recovery window on ≥ 8/10, 0.7; the echo sentence printed, 0.25.
- **Carriage:** L(T+160) shift − cull, holistic, below −0.10 (the shift prunes more lines of descent than its null), 0.5.
- **Depth:** holistic shift median ≤ base median, 0.7.

**What would embarrass this.** The designed fauna holding above 12 with living-mean income ≥ 0.25 on most seeds, which is class A or F rather than D. That would mean evolved designed brains are much cheaper than every probed best. The other embarrassment is co-evolved extinction, which C3's arithmetic says should not happen.

## 9. Falsifier, and the designer's most exposed claims

- **The owner's falsifier:** "the designed body wins on the held-out challenge": class C.
- **Most exposed claim 1:** C3 bankrupts the designed population first. It is falsified if the class-D test counts ≤ 5/10 seeds, with the co-evolved not bankrupt on them.
- **Most exposed claim 2:** an established co-evolved population holds at the bootstrap line. It is falsified if the co-evolved fauna trips a D trigger (income < 0.25 in a window, or alive < 12) on ≥ 3/10 seeds.
- **Most exposed claim 2, conditioned (Amendment 2, F5):** the survival reading is the **recovery window's only**, where every robot alive was born after T at energy 1 and the pre-T hoard is spent. The contrast with random founders is issued **seed by seed**, only where that seed's founders at six items FAIL (§6.6); on a seed whose founders hold, an established population's holding shows nothing beyond them.
- **Most exposed claim 3, rescored (Amendment 2, F1):** under C3 the excess mortality falls on recruits, not on the onset cohort. It is falsified unless the designed excess deaths of individuals born ≥ T exceed those of individuals born < T over [T, T+30) on ≥ ⌈0.8n⌉/n seeds. *This is the adversary's wording, proposed after its probe P1 (n = 1, seed 901, T = 100, not a C3 arm); the posted claim 3 was scored on the UNDERSIZED test, which could not fire where it was needed, and is withdrawn.*

## 10. Arms, commands, cost, gate

**Arms per seed:**

- **shift:** `WORKERS=4 runs/RBT-100/run_arm.sh SEED shift`, durable label `rbt-100-shift-SEED`. At T+10: `python runs/RBT-92/cull_k.py SEED runs/RBT-100/shift-SEED > runs/RBT-100/cull-k-SEED.txt`, then push.
- **cull:** `WORKERS=4 runs/RBT-100/run_arm.sh SEED cull`, durable label `rbt-100-cull-SEED`, launched once the k file is pushed.
- **founders6** (Amendment 2, F5): `WORKERS=4 runs/RBT-100/founders6.sh SEED` (60 seasons, `--food-items 6` from season 0, no event), durable label `rbt-100-founders6-SEED`; independent of every other arm and of T, so it may run first.
- After each arm: `python runs/RBT-92/tables.py runs/RBT-100/ARM-SEED`, then push.
- **Own-net tables** (Amendment 2, F3), from bulk, before the bulk is dropped: `python runs/RBT-100/own_table.py runs/RBT-100/shift-SEED` for each shift arm; for the baseline, after `scripts/durable.sh restore runs/RBT-90/forage-SEED rbt-90-SEED`, `python runs/RBT-100/own_table.py runs/RBT-90/forage-SEED --to runs/RBT-100/base-SEED`. Each prints its reconciliation with `history.json`'s deaths, which must be n/n.
- Once every C3 arm and RBT-92's cull20 and base digests are committed: `python runs/RBT-100/readout.py > runs/RBT-100/readout.txt`.
- Every arm runs as a harness background task with `DURABLE_WATCH_PID=<pid> scripts/durable.sh every 20 runs/RBT-100/ARM-SEED rbt-100-ARM-SEED` beside it.

**Cost.** RBT-92's rate is about 6 s per season on four cores, so 60–70 min an arm. A C3 shift arm should be no slower after T: fewer robots live, and the arenas hold the same four.

| | |
|---|---|
| arms | **20** (shift, cull × 10) × 600 seasons, plus **10 founders6** × 60 seasons (Amendment 2) |
| total | **about 22 session-hours** (founders6 about 6 min each at `WORKERS=4`, about 1 session-hour in all) |
| wall, 20 sessions | about **1 h 50 min** (cull starts at shift's T+10, about 40 min in) |
| wall, 10 sessions | about 2 h 20 min (shift then cull on the same session) |

No cull20 is run: RBT-92's is reused (§1.3). That saves 10 arms against running C3 standalone.

**Gate** (as RBT-99): nothing launches until all of the following hold.

1. RBT-92's instrument has cleared its adversary and senior review.
2. `runs/RBT-92/onset.txt` is committed.
3. RBT-90 part 2's readout is posted.
4. This design has had its own adversary round, named by the coordinator.

**The readout additionally waits for RBT-92's cull20 arms and base digests.**

## 11. Committed

- **Per C3 arm:** `config.json`, `seasons.txt`, `lineage-last.txt`, `bodysig.txt`, `events.txt`, `event.txt` (RBT-92 §14).
- **Per shift arm** (Amendment 2): `own.txt`.
- **Per seed:** `cull-k-SEED.txt`; `base-SEED/own.txt` (Amendment 2); `founders6-SEED/` with `config.json`, `seasons.txt`, `lineage-last.txt`, `events.txt`, `event.txt` (Amendment 2).
- **Once:** `shared_baseline_check.txt`, `smoke.txt`, `readout.txt`, `REPORT.md`.

The readout reads only these files and RBT-92's committed ones.

## Amendments

### Amendment 1 (posted before any C3 arm exists): RBT-92's Amendment 2 carried over, as the coordinator's 13:10 ruling on RBT-100 requires

RBT-92's Amendment 2 is at `63518d9` and `9699cd1` on `results/RBT-92-design`. It changes the shared instrument in six ways. **Five reach C3 with no C3 code**, because C3 runs RBT-92's `onset.py`, `cull_k.py` and `readout.py` (§1.2). **One needed a C3 delta.**

| RBT-92 change | how it reaches C3 |
|---|---|
| **An extinct fauna earns 0** in every season from extinction on, in every window and test (R-body, R-shift, R-null, recovery time, and the D and E income tests); never skipped | `readout.py`'s `Arm`, which C3's `Arm` subclasses; C3's part 2 reads the same `Arm.x` |
| **The onset rule reads only pre-onset seasons.** p is the peak 10-season deaths window in [280, 330], c = p + 5, and T = c + 30 (or c + 90), in [340, 395]. It reads seasons [280, 340) only. | C3 reads T from `runs/RBT-92/onset.txt` |
| **V0 also covers `lineage-last.txt`:** every row with generation < T − 1 is identical to the baseline's | `readout.py` |
| **Class B needs n ≥ 8 seeds read** | `readout.py` (BMIN) |
| `cull_k.py` prints the unselected reference (the baseline's mean deaths per 10 seasons over [T−100, T)) beside k | `cull_k.py` |
| **A k = 0/0 null is the baseline itself.** No cull arm is run, and R-null = R-shift on that seed. | **C3 delta:** `runs/RBT-100/run_arm.sh` exits 0 on 0/0. `runs/RBT-100/readout.py` part 2 reads the baseline as the cull arm on such a seed, where before it would have dropped the seed. `smoke.sh` exercises the path, as RBT-92's does. |

**Checked.** C3's `smoke.sh` was run on integration with `results/RBT-92-design` merged in: exit 0, no stderr, V0–V2 PASS with the new `lineage-last` V0, the 0/0 path named once, and C3-V1 PASS. `tests/test_rbt92_readout.py` gives 4 passed there. The committed `smoke.txt` is that run. Its numbers are read for nothing.

**What this changes in §3 (item 3): nothing in the answer, and one sentence sharpens.**

- The new onset rule reads even less, [280, 340) only, so the C3 shift still cannot move T.
- T now sits half a period after the last baseline wave. The baseline's next waves therefore fall at about T+30 (inside the transient) and T+90 and T+150 (inside the recovery window).
- The ECHO comparison of §3.4 is unchanged: the shift arm's echo of its own starvation pulse against those baseline waves.

**What this changes in §8 (predictions): two restatements, made before any C3 arm exists because extinct-earns-0 changes what two of them measure.**

1. "If D, the floor fires on more seeds than either income trigger, 0.7" is **restated**: among seeds where the designed fauna is **not extinct by T+160**, the floor fires on more seeds than the recovery-income trigger, 0.65. Under extinct-earns-0, extinction trips the income triggers too, so the original comparison would hold by construction on extinct seeds.
2. "Designed R-shift −0.70, or lower if fix (a)" is **restated**: designed R-shift in recovery, with extinct seasons at 0, median **−0.75** (−1.05 to −0.40).

The class probabilities are unchanged: D 0.45, A 0.30, F 0.10, E 0.07, B 0.04, C 0.04. B at n < 8 now falls to F by rule, and C3 expects all ten seeds to be read.

**Still to come:** RBT-92's adversary round (in progress on `results/RBT-92-adversary`) and C3's own adversary round (`session_01S5ugw4uRpKFG1khYtu6PvW`, `results/RBT-100-adversary`). Their answers are carried here as Amendment 2, before any C3 arm.

### Amendment 2 (posted before any C3 arm exists): the answer to adversary round 1 (PR #93)

The round is `runs/RBT-100/adversary/ROUND-1.md` and its P2 addendum. The coordinator's 14:08 ruling: fix F1 and F5 before launch, F6 before the readout with a test, and state or argue the rest. **Every finding is accepted; none is argued away.** The credit the round gives (verbatim quotes, the code premise, byte identity at another seed and onset, §4's gross-halves-work-does-not arithmetic reproduced to within 2–6%) is noted and not repeated.

| | finding | what changed | where |
|---|---|---|---|
| **F1** | the buffer is 10–16 a head, not about 3; UNDERSIZED cannot fire; claim 3 mis-scored | **Fixed.** §3.3's mechanism rewritten (hoarding residents, starving recruits, collapse at T+40 or later). UNDERSIZED dropped and its prediction withdrawn. NULL is diagnostics only: excess deaths split by cause and by cohort (born < T, ≥ T) from committed `lineage-last.txt`, alive deficit to T+100. C3's turnover guard declared not interpretable a priori. Claim 3 rescored on the adversary's criterion, labelled as proposed after P1. | §3.3, §6.2, §8, §9; `readout.py` (`split_deaths`, NULL, CLAIM 3) |
| **F2** | k counts recruit churn; the cull removes residents; the null is the wrong shape | **Stated** as a caveat in §3.3: R-null for C3 is "a random impulse on residents, against a starvation of recruits". k's rule unchanged (the protocol's). | §3.3; printed in NULL's header |
| **F3** | the axis lags own net in the transient and is survivor-conditioned in recovery; D-by-income is near blind | **Built.** `own_table.py` writes `own.txt` from each arm's bulk: stored energy a head, own net over the season's survivors, and an **upper bound** on own net over everyone who ran the season, the starved included (a starved individual's net is at most 0.25 minus its stored energy). Dead individuals have no lineage row for the season they die in (`Ecology._record` logs the living), so a bound, not a mean, is what the bulk supports; this is a narrower build than F3 asked for, and it says so. It reconciles starved + aged (+ culled) with `history.json`'s deaths on every cell but season 0. The readout prints "own net below basal in the recovery window: k/n" per fauna and arm. The class rule is unchanged, as the adversary asks. | §6.2a, §10, §11; `own_table.py`, `readout.py` OWN |
| **F4** | the echo spans the whole recovery window | **Fixed** in §3.4's text (T+100 to T+160 after a collapse at T+40 or later). The ECHO count and its 0.25 prediction stand. | §3.4 |
| **F5** | "where random founders could not" rests on one seed on the old generator; the hoard confounds the contrast; P2: founders bootstrap on 2 of 4 seeds | **Fixed.** (a) A **founders-at-six arm per seed** (`founders6.sh`: 60 seasons, `--food-items 6` from season 0, the adversary's P2 command lengthened to one `max_age`), ten arms, about 1 session-hour. (b) The survival reading is the **recovery window's only**. The contrast sentence prints **only on seeds whose founders FAIL** (< 12 co-evolved alive at 59) **and whose established fauna HOLDS** in the recovery window (min alive ≥ 12, survivors' own net ≥ 0.25). The adversary's cross-ticket point on `docs/held-out-challenges.md` §2, C3 is the coordinator's to file. | §6.6, §9, §10, §11; `founders6.sh`, `readout.py` FOUNDERS |
| **F6** | the readout omits C3's claim line, the D sentence and the owner's falsifier wording | **Fixed**, with a test. Part 2 ends with VERDICT TEXT: C3's and C2's claim lines and §3's statement verbatim, the owner's falsifier wording, the sentence the rule picks ("outlasts a bankrupt comparator" on D unless co-evolved R-shift ≥ −r; an unknown R-shift never reads as "holds up"), and forbidden readings 12 and 13. `tests/test_rbt100_readout.py` pins the verbatim quotes against the doc, the D/A/C sentences, the parse of part 1's verdict block, the death split, and the own-net bound and reconciliation. | §6.7; `readout.py` VERDICT TEXT; `tests/test_rbt100_readout.py` |

**What is not changed, and why.** The class rule, T, the windows, k's rule and the seeds are the shared instrument's. The §8 predictions posted at `c456dd0` are **not re-tuned** from P1 or P2 (the adversary asks the same). The one prediction tied to a withdrawn test (UNDERSIZED) is withdrawn. The new predictions for CLAIM 3, OWN and FOUNDERS are added and **labelled as made after the adversary's probes**; a reader should weigh them accordingly.

**The coordinator's 13:55 note** (RBT-92's `readout.py` moved with PR #87, including RBT-99's V1 cap fix): C3's readout was re-run on integration at `4662cf3` with this branch merged. `smoke.sh` exits 0 with no stderr; V0–V2 pass; C3-V1 passes; the 0/0 path, the own-net tables (38/38 cells reconciled) and a founders6 stand-in are exercised; every part-2 section and VERDICT TEXT print. `pytest -q`: **279 passed**, including the 6 new tests. Importing C3's readout no longer writes to `os.environ` (it sets RBT-92's module globals instead), so it cannot change what RBT-92's own readout reads in the same process.


#### Amendment 2, continued: what C3 tests, restated after P2 (the coordinator's 14:01 request; pre-data)

**P2** (`runs/RBT-100/adversary/founders6_read.txt`) ran random founders at six items for 40 seasons on the head's generator:
- 801: co-evolved extinct at 16;
- 1: 21 alive at 39, bootstrapping;
- 901: 2 alive, moribund;
- 804: back to 60, bootstrapped.

So **on this head the bootstrap line is not a wall for random co-evolved founders**: they cross it on 2 of 4 seeds. The premise behind the protocol's C3 framing, "Below roughly six to twelve items … nothing random forms a breeding population", rests on one seed (801) on the pre-RBT-95 generator. The designed founders' line does hold on P2's seeds: 3 of 4 extinct by 34–36, and 1 alive on the fourth.

**What C3 tests, restated.** This is a pre-data amendment, made before any C3 arm or founders6 arm exists.

1. **The class is unchanged.** The class on R-body in the recovery window, with class D by income and the 12-of-60 floor, is the protocol's and does not depend on the founders' premise.
2. **Survivorship of an established population at six items.** This is read per seed in the recovery window only (§6.6): does the co-evolved fauna, whose every living member was born after T at energy 1, keep ≥ 12 alive while its survivors earn ≥ 0.25?
   - This is what C3 measures on its own. It is **not** a contrast with founders.
   - The designed fauna's survivorship is read the same way, and feeds class D.
3. **The founders contrast, demoted from premise to measurement.** "Where random founders could not" is no longer assumed. It is measured seed by seed by founders6.
   - On a seed whose founders HOLD at six items, the established population's holding shows nothing beyond the founders. The readout prints "no contrast" there.
   - The contrast sentence prints only where the founders FAIL.
   - If founders HOLD on most seeds, then C3 on this head answers the survivorship question (2) and not the "bootstrap line" question. The report must say so in those words.

**The claim line** in §2 stays as quoted: it is the protocol's text, verbatim, and this pre-registration does not edit the protocol. **Its clause "whether an established population holds where random founders could not" is read per seed, conditioned on founders6**, as item 3 says. Whether `docs/held-out-challenges.md` §2, C3 should be amended (the adversary's cross-ticket flag) is the coordinator's call.

**The predictions:**

- **Class probabilities are unchanged:** D 0.45, A 0.30, F 0.10, E 0.07, B 0.04, C 0.04. P2 bears on the co-evolved founders, not on either fauna's established response to the shift. The designed founders' outcome on P2's seeds (3 of 4 extinct) is consistent with the D prediction.
- **Co-evolved survival** (10/10 to T+200, 0.8) is unchanged.
- **Founders predictions** stand as added in Amendment 2, and are labelled as made after P2:
  - co-evolved founders FAIL on 3–7/10, 0.7;
  - designed founders FAIL on ≥ 8/10, 0.8;
  - the contrast sentence prints on at least half the founder-fail seeds, 0.6.
- **One addition, labelled post-P2:** the co-evolved founders HOLD on ≥ 3/10 seeds, 0.7. On those seeds C3 cannot show a contrast.

### Amendment 3 (posted before any C3 arm exists): the re-check's text items, the protocol's new class E2, and RBT-92's Amendment 3 carried over

The coordinator's 14:55 comment: C3's design review is complete, with no C3-specific launch blocker. Four items are owed before the readout runs. RBT-92's Amendment 3 (`55cc86d`, merged with PR #76 at `d2aa6e0`) also changes the shared instrument.

**1. The per-seed founders qualifier (re-check).** VERDICT TEXT now prints, directly beneath C3's claim line: "read per seed on founders6: founders HOLD on h/f seeds read; contrast on c/(f − h)". If no founders arm was read, it says the clause is read on no seed. **"Most" is now defined:** when h ≥ ⌈f/2⌉ it also prints **"C3 on this head answers the survivorship question, not the bootstrap-line question."** `founders_qualifier` in `readout.py` is pinned by a test, including the ⌈9/2⌉ = 5 boundary.

**2. §3.3's P1 counts corrected** from 267 and 21 to **371** starved recruits and **31** starved residents, per the adversary's erratum. No rule depends on these numbers.

**3. Class E2** (`docs/held-out-challenges.md` §9, PR #76). The protocol now splits E:
- **E1, both fail:** both faunas fail D's test.
- **E2, co-evolved bankrupt, designed not:** D's test mirrored. It is **reported with the falsifier as its strongest form.**

The order is E1 > D > E2 > A > C > B > F. C3 runs RBT-92's `classify()`, so it inherits this with no C3 code. VERDICT TEXT gains the E1 and E2 sentences, the E2 one with the owner's falsifier wording, and is pinned by a test.

**The class prediction is restated, pre-data**, because the posted E (0.07) was the old "both fail". E2 is split out of E and F:

| class | D | A | F | E1 | B | C | E2 |
|---|---|---|---|---|---|---|---|
| probability | **0.45** | 0.30 | 0.09 | 0.06 | 0.04 | 0.04 | 0.02 |

E2 is unlikely for C3 because of §4's arithmetic: the co-evolved mower keeps 0.35–0.68 against the designed side's −0.03 to +0.34. Most exposed claim 2 (the co-evolved fauna trips a D trigger on ≥ 3/10 seeds) is unchanged. On seeds where the designed fauna passes, a trip there is E2's per-seed test.

**4. RBT-92's Amendment 3, carried over.** C3 runs RBT-92's scripts, so each change arrives by construction:

| RBT-92 change | effect on C3 |
|---|---|
| onset range [340, 399]; a drift FLAG per seed if the baseline's [T, T+10) deaths exceed 1.5 × its [T−100, T) mean | inherited through `onset.txt` and the readout. A caveat, not a re-pick |
| B and S dropped; carriage is L alone, both faunas | inherited. C3 had no B or S prediction; the L prediction (shift − cull, holistic, below −0.10, 0.5) stands |
| V3 renamed a manipulation check on the tracer | inherited. C3 relies on RBT-92's cull20 arms (§1.3) |
| **recovery time: the paired form (against the control) primary**; the P-form secondary with the base's own d as its floor | inherited. **C3's prediction is restated:** paired recovery "none" within 180 for both faunas in the shift arm on ≥ 9/10 seeds, 0.8, because the halved density is permanent. Cull, paired ≤ 20 on ≥ 8/10, 0.6 (was 0.7 against P). Forbidden reading 13 applies to both forms |
| turnover guard scored only on seeds with co-evolved k > 0 | inherited. C3 already declares it not interpretable (Amendment 2) |
| the equivalence line beside B | inherited |
| remainder groups (`groups.txt`) | inherited. C3 keeps groups of four, so the section prints no remainder effect; it is C1's |
| **`run_arm.sh` runs `tables.py` as a post-run step** | **C3 delta:** `runs/RBT-100/run_arm.sh` now runs RBT-92's `tables.py` **and C3's `own_table.py`** after the ecology, so `own.txt` is written while the bulk is there. `founders6.sh` runs `tables.py` the same way |
| the base digest step dropped | C3's §10 baseline step is now `own_table.py` only (after `durable.sh restore`) |

**5. A shared-instrument bug found by C3's smoke run, fixed here, and flagged on RBT-92.** In `runs/RBT-92/readout.py`'s `main()`, the remainder-group section (RBT-92 Amendment 3, F5) looped `for r in tsv(gp)`. That rebinds `r`, the resolvable effect, to a `groups.txt` row. The verdict line then crashed (`TypeError: unsupported format string passed to dict.__format__`) on any arm with a `groups.txt`, which is every arm now that `run_arm.sh` runs `tables.py` post-run. It fails loudly, not silently, but it would have stopped every challenge's readout, C1's included.
- **The fix:** the loop variable is renamed `row`, one line.
- **The test:** `test_rbt92_main_assigns_r_once` checks that `main()` binds `r` exactly once, outside comprehensions. It fails on `d2aa6e0` and passes with the fix.

**Checked.** Integration at `d2aa6e0` with this branch merged: `smoke.sh 801` exits 0 with no stderr, and every section prints, including VERDICT TEXT with the founders qualifier (before item 5's fix, it exited 1 at the verdict line). `pytest -q`: **283 passed**.

