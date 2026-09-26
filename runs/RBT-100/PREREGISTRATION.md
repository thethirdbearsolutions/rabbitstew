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

### 3.3 What does change: C3's excess mortality is spread out, and partly missing births rather than deaths

C1 adds competition at once: the first season at eight robots already pays less. **C3 is a budget shift.** An individual dies when its energy reaches zero, and the energy it carries at T is a buffer.

- Energy is at most a little above the birth threshold of 3. A parent keeps its energy minus the birth cost of 1, and a newborn starts at 1.
- A robot whose post-shift net falls δ below the basal cost therefore dies about e/δ seasons after T. At δ = 0.1–0.3 and e = 1–3 that is **3 to 30 seasons**.
- This is the same mechanism as the founders' season-11 wave, which came when initial energy 3 ran out at about 0.25 a season (`docs/foraging-world.md`, "Six items" and "First forty seasons").

Breeding needs energy ≥ 3, so a halved income also **cuts births**. A population can shrink with no excess deaths at all, simply by ageing out unreplaced.

**Consequence for the null.** RBT-89 §8's k counts excess deaths over [T, T+10), so it sees only the front of C3's cost. The impulse cull of k is then likely smaller than what the shift does. **The rule for k is the protocol's and is not changed** (measure, do not tune; changing k's rule would be a second deviation, decided after the shift arm's first ten seasons exist). Instead the C3 readout prints, beside k, three deficits (§6 NULL):

- excess deaths over [T, T+30) and [T, T+60);
- the births deficit;
- the alive deficit, base − shift, at T+10, T+30 and T+60.

**Pre-registered test.** If a fauna's median alive deficit at T+30 exceeds 2 × its median k + 2, the null is printed **UNDERSIZED** for that fauna. The turnover guard ("|R-null| < r: the shift did no more than a same-size cull") is then printed as **not interpretable** for it. The guard was built for C1, where the shift's cost is turnover. For C3 the income loss is arithmetic on the density, which no cull reproduces, so the guard is expected to read "no" (§8).

### 3.4 What does change: the 60-season wave after T

- **The windows stay valid.** `max_age` = 60 is not the flag, so everyone alive at T is dead by age by T+60, and the transient window keeps its meaning. The recovery window is still "the first hundred seasons in which nobody alive evolved under the baseline".
- **The wave's phase after T is not the baseline's.** A starvation pulse spread over T+3…T+30, followed by the refill births of whoever can still breed, sets a new cohort. That cohort ages out about 60 seasons later, which is **T+60 to T+90, the opening of the recovery window**.
- The baseline's own wave also crosses that window: a 100-season window always contains at least one wave. So both arms carry a wave in the recovery window, **at different phases**, and the 60-season structure of the shift arm is the shift's, not the baseline's.
- **On a designed fauna shrunk below about 20 alive, RBT-89's 20/60 peak threshold cannot be reached at all.** "No peak" there is uninformative.
- **Consequence.** The cohort-cycle reading (lag-60 acf, 20/60 peaks) is **not** read off a C3 shift arm as if it were the baseline's cycle. The readout prints the post-onset peaks per arm, fauna and seed (§6 ECHO), and counts the seeds where the shift arm has a holistic peak starting inside the recovery window, against the baseline.
- If shift has one on ≥ ⌈0.8n⌉/n seeds and base on fewer, the report says **"the recovery window contains the shift's own echo"** beside the class. The class is not changed: the recovery window is fixed by the protocol (forbidden reading 4). The within-arm contrast R-body compares two faunas that meet the same world, and a 100-season mean spans about 1.7 cycles.

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
2. **NULL** (§3.3): k; excess deaths over [T, +10), [T, +30), [T, +60); births deficit over [T, +60); alive deficit at T+10, +30, +60; and the UNDERSIZED test.
3. **ECHO** (§3.4): post-onset 20/60 peaks per seed, arm and fauna, and the recovery-window count, shift against base.
4. **CLASS D triggers** (§4): per seed and fauna in the shift arm, the transient and recovery means, the minimum alive over [T, T+160), the extinction season relative to T, and which of the three triggers fired.
5. **DEPTH** (§7): median reproduction events after T along lineages alive at T+160, per arm and fauna.

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
- **k** (`cull_k.py` on the shift arm): K1 median **2**/60 (0–12); K2 median **10** (0–30). **UNDERSIZED** printed for the designed fauna, 0.55, and for the holistic fauna, 0.45.
- **Turnover guard:** holistic |R-null| ≥ r (the shift did more to income than the cull), 0.95.
- **Recovery time:** "none" on ≥ 9/10 seeds for both faunas in the shift arm, 0.85; cull ≤ 20 on ≥ 8/10, 0.7.
- **ECHO:** base has a holistic peak starting inside the recovery window on ≥ 8/10, 0.7; the echo sentence printed, 0.25.
- **Carriage:** L(T+160) shift − cull, holistic, below −0.10 (the shift prunes more lines of descent than its null), 0.5.
- **Depth:** holistic shift median ≤ base median, 0.7.

**What would embarrass this.** The designed fauna holding above 12 with living-mean income ≥ 0.25 on most seeds, which is class A or F rather than D. That would mean evolved designed brains are much cheaper than every probed best. The other embarrassment is co-evolved extinction, which C3's arithmetic says should not happen.

## 9. Falsifier, and the designer's most exposed claims

- **The owner's falsifier:** "the designed body wins on the held-out challenge": class C.
- **Most exposed claim 1:** C3 bankrupts the designed population first. It is falsified if the class-D test counts ≤ 5/10 seeds, with the co-evolved not bankrupt on them.
- **Most exposed claim 2:** an established co-evolved population holds at the bootstrap line. It is falsified if the co-evolved fauna trips a D trigger (income < 0.25 in a window, or alive < 12) on ≥ 3/10 seeds.
- **Most exposed claim 3:** the impulse null is undersized for a budget shift. It is falsified if UNDERSIZED prints for neither fauna.

## 10. Arms, commands, cost, gate

**Arms per seed:**

- **shift:** `WORKERS=4 runs/RBT-100/run_arm.sh SEED shift`, durable label `rbt-100-shift-SEED`. At T+10: `python runs/RBT-92/cull_k.py SEED runs/RBT-100/shift-SEED > runs/RBT-100/cull-k-SEED.txt`, then push.
- **cull:** `WORKERS=4 runs/RBT-100/run_arm.sh SEED cull`, durable label `rbt-100-cull-SEED`, launched once the k file is pushed.
- After each arm: `python runs/RBT-92/tables.py runs/RBT-100/ARM-SEED`, then push.
- Once every C3 arm and RBT-92's cull20 and base digests are committed: `python runs/RBT-100/readout.py > runs/RBT-100/readout.txt`.
- Every arm runs as a harness background task with `DURABLE_WATCH_PID=<pid> scripts/durable.sh every 20 runs/RBT-100/ARM-SEED rbt-100-ARM-SEED` beside it.

**Cost.** RBT-92's rate is about 6 s per season on four cores, so 60–70 min an arm. A C3 shift arm should be no slower after T: fewer robots live, and the arenas hold the same four.

| | |
|---|---|
| arms | **20** (shift, cull × 10) × 600 seasons |
| total | **about 21 session-hours** |
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
- **Per seed:** `cull-k-SEED.txt`.
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
