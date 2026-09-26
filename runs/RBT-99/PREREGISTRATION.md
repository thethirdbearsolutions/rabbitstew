# RBT-99 pre-registration: epoch C2, dearer work, on RBT-92's instrument

**Posted before any RBT-99 arm exists.** Designer only; I run no full arm. The integration head this
design is written against is `509c16c`. **This design is built on RBT-92's instrument**
(`runs/RBT-92/`, pre-registration `runs/RBT-92/PREREGISTRATION.md`, PR #74 merged at `292d6c5`, and
Amendment 1 in PR #76). Everything not stated here is RBT-92's, section for section.
**Any change that RBT-92's adversary round, its answer, or its senior review makes to that instrument
binds this ticket too.** Each such change is carried over in an amendment below and said so (§15).

## Summary

| | |
|---|---|
| challenge | **C2 dearer work:** `--shift-at T --shift work-cost=0.08` (0.03 → 0.08 per kJ). **The magnitude stays at 0.08**; no smaller rung (§3). |
| seeds | RBT-92's: **all ten** of RBT-90 part 2 (801 804 805 806 807 1 2 3 4 7), under its committed seed rule (`runs/RBT-92/SEED-RULE.md`, `66f5ab3`). The only exclusion is extinction by T − 1 in the baseline. |
| baseline (control) | the seed's RBT-90 part 2 arm. It is byte-identical to the shift arm before T (RBT-92 §3; re-checked for this flag by the smoke run, §13). |
| T | RBT-92's, read from `runs/RBT-92/onset.txt`. The onset is a property of the shared baseline, so C2's T is C1's T on every seed. |
| new arms per seed | **shift** (C2) and **cull** (the null; k by RBT-89 §8's rule on C2's own shift arm). **No cull20:** RBT-92's `cull20-SEED` is the same command at the same seed and T, so it is the same run and is cited (§6). |
| windows, readouts, V0–V3, carriage, classes A–F | RBT-92's, unchanged (`runs/RBT-92/readout.py` run by `runs/RBT-99/readout.sh`) |
| predicted class | **D, designed bankrupt, 0.75** (§10) |
| falsifier | **"the designed body wins on the held-out challenge"**: class C |
| cost | 20 arms × 600 seasons, about 20–22 session-hours; **about 2 h 10 min wall** on 10 four-core sessions, or about 1 h 45 min on 20 (§14) |

## 1. Challenge and flag

`food.work_cost` goes 0.03 → 0.08 at T, for both faunas, on `docs/held-out-challenges.md` §1's
baseline command. The launcher is RBT-92's `run_arm.sh`, unchanged but for two variables with
RBT-92's defaults: `SHIFT` (the one `FLAG=VALUE`) and `OUTROOT`. `runs/RBT-99/run_arm.sh` sets them to
`work-cost=0.08` and `runs/RBT-99`. RBT-92's own commands are unaffected; a dry run printed identical
`event.txt` lines for its three arms before and after the change.

**What the flag changes, exactly.** A robot's season gain is
`items eaten × 1 − work_cost × kJ` (`rabbitstew/simulation.py`, `food_gain`), before the 0.25 basal cost.
The shift therefore lowers every individual's gain by **exactly 0.05 × its kJ that season** and changes
nothing else. That gain is the axis the readout scores (`mean_lifetime_score` is the lifetime mean of
it), so part of any C2 effect on income is this mechanical price. The rest is what the population
does about the price: deaths, fewer births, and sorting on kJ per item.

**Endpoint on random founders** (RBT-21, W6′, seed 801, 0.08 from season 0): both populations went
extinct. The designed population died at season 13 and the co-evolved at 26.
**Kind: budget.** The C2 claim line, verbatim (`docs/held-out-challenges.md` §2, C2):

> **Claim tested:** survivorship of the co-evolved population at an economic boundary the designed
> body's budget is not expected to survive. That is a different claim from the owner's (it is about
> one body's cheapness, not two bodies' contest), and a C2 result is reported as such.

And the protocol's instruction for C2, verbatim (same section):

> **C2 is therefore
> expected to bankrupt the designed population unless its evolved brains are already far cheaper
> than any probed best, and a future arm must predict that outright** (§9, outcome class D).

## 2. Perception

Nothing, by construction: no sensor reads energy or work (`docs/held-out-challenges.md` §1; the
foraging vocabulary is `contact`, `up`, `velocity`, `joint_angle`, `joint_velocity`, `height`,
`oscillator`, `food`, `agent`). The statement the protocol requires, in its words (§12 field 2):
**"this challenge selects on standing morphology and gait only; robust means survivorship of standing
morphology and gait through the shift, not adaptation during it; the axis and the falsifier are claims
about income, not perception."** RBT-91 option A is in force. RBT-97's result that a compass pays when
it is installed does not change this, because no standing population carries a paying compass.

The §3 statement, verbatim:

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

## 3. Item 3: is class E the likely outcome at 0.08 on an evolved population? No. The shift stays at 0.08.

This is answered from committed data, with no run: `runs/RBT-99/work_budget.py` →
`runs/RBT-99/work_budget.txt`. It uses two sources, both on this exact economy. **kJ per season** comes
from RBT-10's solo probes of the per-season bests at seeds 802 and 803, w = 0.03, eight draws each
(`runs/RBT-10/forage-w0.03-80x.probe.txt`). These are the only committed per-kJ figures for evolved
individuals of this economy. **Population income** comes from RBT-71's `mean_lifetime_score`, seeds
804–806, seasons 100–599 (`runs/RBT-71/forage-80x/seasons.txt`).

| | evolved bests' kJ (seasons 100–590, n = 6 per fauna) | added charge at 0.08 | population income at 0.03, seasons 100–599, seeds 804/805/806 | the same less the added charge (range over the kJ range) |
|---|---|---|---|---|
| co-evolved | 2.3–7.8, median 3.75 | 0.115–0.390, median 0.188 | 1.057 / 1.012 / 0.941 | 0.551–0.942: **above the basal 0.25 on every row**, the worst by 0.30 |
| designed | 17.1–27.0, median 19.90 | 0.855–1.350, median 0.995 | 0.845 / 0.903 / 0.896 | −0.505 to +0.048: **below the basal 0.25 on every row** |

**Class E is not the likely outcome.** E needs both faunas at 0, or co-evolved window income below 0.25
on ≥ 8/10 seeds. On the committed figures the co-evolved fauna's income stays above the basal cost after
the shift. The margin is 0.30 in the worst case: the lowest-income seed charged at the costliest
evolved best's kJ. **RBT-21's extinction does not transfer**, because it was an extinction of founders:

- 73% of holistic founders ate nothing and starved on birth energy at the season-11 wave, as they do at
  0.03.
- Every newborn came from a non-eater or from a single eater, `h0-7`, whose realised yield was 0.385
  items and whose net at 0.08 was +0.044. All ten holistic children died under the basal cost
  (RBT-21 report).

An evolved population at T is 60 eaters, and a newborn inherits an eating body of 2–8 kJ.

**Class D is the likely outcome, as the protocol requires this arm to predict outright.** Every probed
evolved Pioneer best spends 17–27 kJ, and the shift takes 0.86–1.35 a season more from a population
whose mean income is +0.85 to +0.90. So the designed fauna's mean gain falls below the basal cost at
once. Selection can sort for cheaper brains, as it did on RBT-21's designed founders, whose mean gain
climbed from −1.16 to +0.50 over 13 seasons. To stay solvent at 0.08 the fauna needs a brain far cheaper
than any on record, and it must find it within about two reproduction events. The cheapest intact
Pioneer bests on record are 12.7 kJ (RBT-13, another economy) and 15.0 kJ (RBT-21's economy-selected
`c0-4`). And a newborn Pioneer starts with 1 energy (RBT-21's newborn trap).

**Why not a smaller shift.** The ticket asks for a smaller single-flag shift only if E is likely, and it
is not. 0.08 is the protocol's named C2 value, and it has a measured endpoint on founders (RBT-21).
The alternative rung, 0.05, has none (§2). A smaller shift would also weaken the one thing C2 can test
that C1 cannot: whether the co-evolved body's cheapness carries it through at a price the designed body
cannot pay. **The size is fixed here at 0.08, before any arm.**

**Limits of this prior, stated so they can be attacked:**

1. The kJ figures are bests, not population means, from two seeds, 802 and 803. Those seeds are not in
   the ten, and were run on the pre-RBT-95 streams.
2. The probes are solo; RBT-21 shows a shared arena lowers yield: `h0-7` ate 0.50 alone against 0.385
   shared. The kJ is less affected.
3. The co-evolved population may carry a costly tail that the bests do not show. RBT-21 found 5 of 59
   founder lumps above 1.25 kJ and one at 21.6. That tail would die, which raises k1 (§6) without
   threatening the fauna.

The arm measures all three. None of them could plausibly move the co-evolved fauna's income by the 0.30
needed to reach E.

## 4. Comparator, shared baseline, seeds

These are RBT-92 §3 and §4, unchanged. The comparator is the designed fauna of the same run, in separate
arena banks and never merged. **Because the banks are separate, the designed fauna's collapse does not
change the co-evolved fauna's arenas**: group size is fixed at 4 and density per arena is unchanged. So
the co-evolved R-shift is that body's own response to the price. This is what "one body's cheapness"
requires.

**Class B needs at least eight seeds read** on the prior SD (the coordinator's 13:10 ruling on RBT-92, item 4): r =
t(n−1) · 0.108/√n is 0.090 at eight and 0.100 at seven. If fewer than eight seeds are read, the result
is declared unable to return B before its readout is run. **If fewer than six seeds are read, no verdict
is issued.**

## 5. Onset, windows, axis, readouts

All of these are RBT-92's (§5 and §6), unchanged, and read by RBT-92's `readout.py`:

- **T** comes from `runs/RBT-92/onset.txt`. Whatever rule RBT-92 finally commits there (the pre-onset window
  of the coordinator's 13:10 ruling) is C2's T by construction.
- **Windows:** before [T−100, T), transient [T, T+60), recovery [T+60, T+160) primary, tail
  [T+160, T+200).
- **Readouts:** R-body, R-shift, R-null, R-cull, R-cull20; recovery time; carriage L, B and S; alive.

**C2-specific notes on reading them, fixed now:**

- **The lifetime-mean axis lags inside the transient.** An individual alive at T carries its pre-T
  seasons, priced at 0.03, in its lifetime mean. So transient-window income understates the shift's
  immediate price. By T+60 every individual alive was born after T, and the recovery window is priced
  wholly at 0.08. This is one more reason the recovery window is primary. Class D's income trigger is
  read on the transient **or** the recovery window, and its capacity trigger (alive < 12) does not lag.
- **An extinct fauna earns 0.** This is the coordinator's 13:10 ruling on RBT-92 (item 1), carried over by §15 once RBT-92
  commits it. It binds harder here than on C1, because the designed fauna is predicted to die out on
  some seeds. Until the fix is committed, `readout.py` skips extinct seasons in window means. D's
  capacity trigger catches a dead fauna either way, but the designed R-shift, R-null and R-body would
  read survivors only.

## 6. Null, validation

**Null:** k per fauna is the excess deaths of C2's shift arm over the baseline in [T, T+10), floored at
0. It is computed by RBT-92's `cull_k.py` on this ticket's shift arm:

    python runs/RBT-92/cull_k.py SEED runs/RBT-99/shift-SEED > runs/RBT-99/cull-k-SEED.txt

It reads deaths only, in impulse form, and the cull mechanism takes min(k, alive).

**k may be large here, and that is expected (item 4).** The designed fauna's excess deaths in ten
seasons may be most of the 60 (§10: median predicted 35). A null that removes 35 designed robots at
random is a harsh one, and it refills by breeding from the rest. If k2 ≥ the designed fauna's alive at
T, the null extinguishes the designed fauna too. In that case designed R-null compares two extinct arms,
reads 0 by construction, and the report says so. **The class-D verdict does not depend on R-null**: it
is read on the shift arm against the income floor and the capacity floor. The co-evolved k1 is
predicted small (median 3), so co-evolved R-null ≈ co-evolved R-shift, and the turnover guard reads
this directly.

**Validation (V0–V3):**

- **V0–V2** are per arm and run on C2's own shift and cull arms.
- **V3** (cull20 − base on carriage and the alive dip) is a property of the instrument, not of the
  challenge. RBT-92's cull20 arm is the same run C2's would be: the same command, seed, T and k = 20,
  and the shift flag does not enter it. So **V3 is RBT-92's, cited**, and `readout.sh` links
  `runs/RBT-92/cull20-SEED` into the readout.
- If RBT-92's V3 fails, C2's carriage readouts print as UNVALIDATED, exactly as C1's do.
- **cull20 is re-run for C2 only if RBT-92's cull20 arms are not committed** by the time C2's shift arms
  end. That would be the same run, so it would reproduce RBT-92's to the byte.

## 7. Resolvable effect size

This is RBT-92 §8, unchanged: r is the larger of the season-noise figure and the between-seed figure,
as a t(n−1) half-width. **Ten seeds resolve about 0.077** on the prior SD of 0.108 (±40%). The
season-noise figure divides by √100 as if seasons were independent, and they are not (the 60-season
wave). The between-seed figure is the binding one and r takes the larger, so nothing turns on it
(senior review).

**C2-specific:** under class D the verdict does not use r. **The line C2 is actually about does use r:
"holds up" needs co-evolved R-shift ≥ −r.** The predicted co-evolved R-shift (§10) is about two to
three times r, so that line is resolvable at n = 10 in either direction.

## 8. Verdict

RBT-89 §9 on the shift arm's R-body in the recovery window, in RBT-92 §9's order: E, D, A, C, B, F.

**What the verdict means, in the protocol's words (item 5):**

- **D** (predicted): "the challenge exceeded the comparator's energy budget; **not** class A, whatever
  R-body reads on the seeds where both survive." It is reported "as D, with the co-evolved side's own
  R-shift beside it, and the sentence 'holds up against the challenge' is earned only if the co-evolved
  side's income in the recovery window is within r of its control (R-shift ≥ −r). Otherwise it is
  'outlasts a bankrupt comparator', which is a different sentence" (§9). It is "a fact about wheels at
  14–29 kJ, not about the co-evolved body's robustness" (§9).
- Per the C2 claim line, whatever the class, the result is reported as a finding about **one body's
  cheapness, not two bodies' contest**. It is never reported as the owner's "outcompete or fight to a
  draw".
- **E:** "neither body holds up". **A**, **B**, **C** and **F** read as RBT-89 §9 words them. A class A
  is possible only if the designed fauna stays solvent and above 12. It would then say the co-evolved
  body earned more under the price, and nothing about sensing it.

## 9. Falsifier

**In the owner's words: "the designed body wins on the held-out challenge"**: class C.

**Also falsified**, on this author's most exposed claim (§3), if either of these happens:

- **(i)** the designed fauna is **not** bankrupt: D's test fails, with the designed fauna's recovery
  income ≥ 0.25 and alive ≥ 12 on ≥ 3/10 seeds. That would show the evolved Pioneer brains are "already
  far cheaper than any probed best", which is the protocol's named exception.
- **(ii)** the co-evolved fauna fails: E, or co-evolved recovery income < 0.25 on ≥ 3/10 seeds. That
  would show §3's answer to item 3 was wrong.

## 10. Point predictions (item 2)

**Class: D, 0.75.** The rest: F 0.10, A 0.07, E 0.04, B 0.02, C 0.02.

**Designed fauna:**

- Transient or recovery income < 0.25, or alive < 12, on ≥ 8/10 seeds (D's designed half): 0.8.
- Alive < 12 at some season inside the transient on ≥ 7/10 seeds: 0.65.
- Extinct by T+160 on ≥ 5/10 seeds: 0.5.
- Designed R-shift, recovery, with extinct seasons at 0 once §5's fix is in: **−0.75** (−1.0 to −0.35).

**Co-evolved fauna:**

- Survives, with alive ≥ 12 throughout and recovery income ≥ 0.25, on 10/10 seeds: 0.85.
- **R-shift, recovery: −0.17** (per-seed range −0.35 to −0.05). This is 0.05 × the population's mean
  kJ, taken as the bests' median 3.75 (−0.19), less a small sorting gain on kJ over the ≈ 5 events of
  transient plus recovery.
- **"Holds up" (R-shift ≥ −r): 0.25. "Outlasts a bankrupt comparator": 0.75 given D.**
- What would embarrass this: the co-evolved population turns out cheaper than its bests, at mean kJ
  under ~1.5. Then R-shift is inside r and C2 reads "holds up".

**k:**

- K1 (co-evolved) median **3** (0–12).
- K2 (designed) median **35** (15–60).
- K2 ≥ 20 on ≥ 7/10 seeds: 0.65.
- K2 ≥ the designed fauna's alive at T on some seed: 0.3.

**R-null:** co-evolved |R-null| ≥ r and within 0.05 of co-evolved R-shift: 0.65. The turnover guard
therefore reads "the shift did more than a same-size cull" for the co-evolved fauna.

**R-body, recovery** (not the verdict under D): mean **+0.7**, per-seed range +0.4 to +1.1, with
extinct designed seasons at 0.

**Recovery time:**

- Co-evolved shift "none" on ≥ 6/10 seeds: 0.55. The price is a standing offset of about 0.19 against
  h = 2 SD of the pre-window.
- Designed shift "none" on ≥ 8/10: 0.8.
- The cull arm, co-evolved ≤ 20 on ≥ 8/10: 0.7.

**Carriage:**

- L(T+160) shift − cull within ±0.10, co-evolved: 0.5.
- B(T+160) shift − base within ±0.10: 0.55.
- Sorting on kJ could shift body structure, and this is the one place where C2 could show "is sorted"
  in the body rather than only in income.

**Depth** (RBT-92 §12, the same T): before the onset 2T/60 = 11.3–13.3 events; after it 6.7–8.7;
transient plus recovery about 5.3. The report says "survives" or "is sorted" unless carriage traces a
structure acquired after T.

## 11. Forbidden readings, verbatim (`docs/held-out-challenges.md` §14; item 1)

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

**C2's own readings to forbid,** added here:

- **(a) Reading D as the co-evolved body's win.** Reading 2 covers this, and so does §8's C2 line.
- **(b) Reading the mechanical price as maladaptation.** Part of co-evolved R-shift is 0.05 × kJ by
  arithmetic. The report prints the arithmetic figure from the co-evolved population's own
  pre-shift kJ, if the arm's lineage bulk is read for it, beside the measured R-shift. "The population
  failed to adapt" is not said of the part the price takes by construction.
- **(c) Pooling C2 with C1 or C3 into one "holds up" count.** Each challenge's claim is different, and
  C2's is about one body.

## 12. Items the ticket lists, mapped

| item | where |
|---|---|
| 1. C2 claim line and forbidden readings, verbatim | §1, §11 |
| 2. point prediction per class with confidence; D read by income with the 12-of-60 floor | §10; D's test is RBT-92's `readout.py` (income < 0.25 in the transient or recovery window, or alive < 12) |
| 3. is E likely at 0.08 on an evolved population; smaller shift if so | §3: no, and the size stays at 0.08 |
| 4. per-fauna cull null by §8's rule; k may be large | §6 |
| 5. what the verdict means, and depth | §8, §10 |
| 6. cost and arms; cull20 only if needed | §14; cull20 cited from RBT-92 (§6) |

## 13. Smoke run (read for nothing)

`runs/RBT-99/smoke_runs.sh 801` ran two 20-season runs at seed 801, one plain and one with
`--shift-at 10 --shift work-cost=0.08`, on RBT-90 part 2's command. `runs/RBT-99/smoke_check.py` →
`runs/RBT-99/smoke.txt` checks the following, and prints no contrast of income, deaths or alive:

- the pre-10 prefix is byte-identical to plain: lineage, cohorts and history;
- the config records the shift;
- history carries `shift` from season 10 on;
- every lineage row's `last_score` equals `food − w × work/1000`, with w = 0.03 before season 10 and in
  plain, and w = 0.08 in the shift arm from season 10.

The bulk was deleted.

## 14. Arms, sequencing, cost (item 6)

0. **Gate** (ticket): RBT-92's instrument has cleared its adversary and senior review; RBT-90 part 2's
   readout is posted; `runs/RBT-92/onset.txt` is committed; this design has had its own adversary round.
   Nothing launches before all of these.
1. **Per seed, session A:** `WORKERS=4 runs/RBT-99/run_arm.sh SEED shift` as a harness background task,
   with `DURABLE_WATCH_PID=<pid> scripts/durable.sh every 20 runs/RBT-99/shift-SEED rbt-99-shift-SEED`
   beside it.
   - At T+10: `python runs/RBT-92/cull_k.py SEED runs/RBT-99/shift-SEED > runs/RBT-99/cull-k-SEED.txt`,
     then push.
   - At the end: `python runs/RBT-92/tables.py runs/RBT-99/shift-SEED`, then push.
2. **Per seed, session B** (or session A afterwards): pull the k file, then
   `WORKERS=4 runs/RBT-99/run_arm.sh SEED cull` (durable label `rbt-99-cull-SEED`), then `tables.py`.
3. After every arm has ended: `runs/RBT-99/readout.sh > runs/RBT-99/readout.txt`. It needs RBT-92's
   `cull20-SEED` and `base-SEED` committed.

**Cost** is about 6 s per season on four cores (RBT-92 §13). C2's shift arm may run faster once the
designed fauna thins, because fewer robots are simulated; that is not relied on.

| | |
|---|---|
| arms | 20 (shift and cull × 10) × 600 seasons |
| per arm | about 60–70 min |
| total | **about 20–22 session-hours** |
| wall on 10 sessions (shift then cull) | about 2 h 10 min |
| wall on 20 sessions (cull waits ~40 min for its k) | about 1 h 45 min |
| cull20 | 0 (cited from RBT-92) |

**Committed per arm,** as RBT-92 §14: `config.json`, `seasons.txt`, `lineage-last.txt`, `bodysig.txt`,
`events.txt`, `event.txt`. Per seed: `cull-k-SEED.txt`. Once: `readout.txt`, `REPORT.md`.

## 15. Carried over from RBT-92, and amendments

State of RBT-92's instrument at the time of posting (13:05 UTC):

- the pre-registration is merged (PR #74);
- Amendment 1 (the verbatim quotations) is in PR #76;
- the senior review is posted (headed 13:20), and **the coordinator adopted it in full** (the ruling headed 13:10): four fixes, which go into RBT-92's next amendment PR together with its answer to the
  adversary;
- the adversary round (`session_011DaJxngAQoRRuQ4wTE11cC`) has not posted.

**The coordinator's 13:10 ruling, carried over item by item.** Each item binds C2 the moment RBT-92
commits it, because C2 runs RBT-92's scripts unchanged.

1. **An extinct fauna counts as 0 income** in every window and every test, pinned by a test. Stated in
   §5. It binds harder here than on C1.
2. **The onset rule reads only seasons before T:** D(T) over [T−20, T), in [340, 400], ties to the
   larger T. Inherited automatically, because C2 reads `runs/RBT-92/onset.txt`. **The fixed-T = 370
   sensitivity line** is also inherited if RBT-92 implements it in `readout.py`. It enters no verdict,
   here as there. If it needs arms run at T = 370, those are RBT-92's to specify, and C2 adds the
   matching C2 arms only by amendment.
3. **V0 also compares the `lineage-last.txt` rows** that end before T. Inherited if RBT-92 commits it
   to `readout.py`.
4. **Class B requires at least eight surviving seeds.** Stated in §4.
5. The record correction (a draw needs eight or ten seeds under the t rule) is already in RBT-92 §8,
   which §7 cites.

**Watched:** every later change to RBT-92's instrument, from its adversary round or its answer, is
carried over in an amendment below, before any RBT-99 arm exists, each stated as such.

### Amendments

## Amendment 1 (posted before any RBT-99 arm exists): the adversary's round 1 answered, and RBT-92's 13:10 fixes carried over

The adversary's round 1 is on RBT-99 (13:25 UTC), with its probes in `runs/RBT-99/adversary/` (PR #83). It
re-derived `work_budget.txt`, the smoke check, the launcher's identity at RBT-92's defaults and the
quotations, and it agreed with item 3 and with the 0.08 size. **I take its findings as follows.**
F1–F3 are fixed in code and text. F4–F7 are adopted as caveats; each is printed by the readout, not only
stated here. **This amendment supersedes §3's "why D", §6's R-null text and §10 where it says so.** The
original text stays above for the record. The report scores the amended predictions and prints the
original §10 beside them.

**Probes 1–4 read the running baselines' bulk, pre-onset seasons only (< 340).** I use their numbers
below. They print nothing RBT-90 part 2 scores, and every season they read is before any T. The
coordinator has not objected, so they stand. If the coordinator withdraws them, the amended predictions
revert to §10.

### F1 (must fix): a cull k at or above alive halted the readout for every seed. Fixed in the shared readout.

- **Before:** `ecology.py` removes min(k, alive). `readout.py`'s V1 demanded exactly k for the cull arm,
  so one capped seed printed "INSTRUMENT FAILED VALIDATION" and stopped the shift readout for all seeds.
- **After:** V1 compares the cull arm with **min(k, alive at T − 1)** per fauna, as it already did for
  cull20. It prints a `V1 note` naming every capped seed and fauna.
- **Pinned by a test:** `tests/test_rbt92_readout_cap.py` uses a synthetic seed with k = 41 against 3
  alive. On the old readout the test fails with "INSTRUMENT FAILED VALIDATION" (reproduced before the
  fix). On the new one V0–V2 pass and R-null reads n/a.
- **This is a shared-instrument change.** RBT-92, RBT-100 and RBT-101 carry it; C3 is exposed the same
  way. It changes nothing on a seed where k < alive.

### F2 (must fix): D was predicted for a reason the data do not support. Reasoning and predictions amended.

§3 read "the designed population's mean re-priced gain is below basal" as bankruptcy. That holds only if
the robots sit near the mean, and on the ten baselines they do not:

- **kJ varies:** designed q10–q90 is 15–24 kJ at 801 and 6–24 at seed 7 (`kj_baseline.txt`).
- **kJ is each robot's own:** its ICC is 0.73–0.94.
- **kJ is heritable:** the parent-to-child slope is 0.47–0.92 (`kj_heritability.txt`).
- **29–36% of designed robot-seasons stay above basal at 0.08.**
- **Designed newborns earn like adults** (−0.184 against −0.175 re-priced; `newborn_gain.txt`). So
  RBT-21's newborn route to extinction does not apply to either evolved fauna. That is the argument §3
  made for the co-evolved side, and it cuts both ways.

**The rival mechanism, named: churn at capacity.** The designed fauna loses its costly majority, about
5–8 a season, and refills from its solvent, cheap and heritable tail. In the adversary's resampling
model at b = 0.5, min alive is 60 and recovery income is 0.80–1.49. The model reads income about
0.1–0.2 high (no mutation load, no age wave), but those incomes still clear 0.25 after that correction.
D's designed half is met on 0/10 seeds at b = 0.5 and on 1/10 at b = 0.

**My weight on the model.** It re-prices each robot's own 0.03 rows exactly, which is right, because no
robot can perceive the price. It has no mutation load beyond b, no age wave, no competition change and
no new mutants. I treat it as the better prior than §3's mean-based arithmetic, but not as certain. The
fauna's recovery income is conditioned on survival (F6), and the arm decides.

**Why D, amended.** D is now the outcome if heritable cheapness is too rare, or too diluted by mutation,
to refill 60 slots within about two reproduction events. Churn is the outcome otherwise, and then the
verdict is read on R-body among survivors, with turnover beside it (F6). **Falsifier (i) (designed not
bankrupt on ≥ 3/10 seeds) stays registered as the original design's most exposed claim and is scored.
Under this amendment I expect it to fire, at 0.65.**

### F3 (must fix, with F1): designed R-null under a capped cull. Option (a) pre-registered and implemented.

On any seed and fauna where k ≥ alive at T − 1, the null empties that fauna; it has no breeders, so it
stays extinct and earns 0 from T. Its R-null is then shift − extinction, which measures nothing about
turnover.

- **Pre-registered:** option (a). That fauna's R-null is **n/a** on that seed. It is excluded from the
  R-null mean and printed as "n/a on [seeds]: the cull emptied the fauna". If it is the co-evolved fauna,
  that seed is also dropped from the turnover guard. `readout.py` does this, and the test covers it.
- **Option (b) is rejected.** Capping k at alive − 1 would change RBT-89 §8's rule, which is k = excess
  deaths floored at 0. The rule stays; only its reading changes.
- **Near the cap** (k within a few of alive), R-null is read and printed with k and alive beside it
  (the V1 note and `cull-k-SEED.txt`).
- §6's sentence "designed R-null compares two extinct arms, reads 0" is withdrawn: under churn the shift
  arm's designed fauna is not extinct.

### F4 (caveat, adopted): the mechanical price nearly decides "holds up". Forbidden reading (b) is now unconditional.

The co-evolved population's own pre-onset kJ is 2.90–7.31. Its price, 0.05 × kJ, is **0.145–0.366,
median about 0.27**. That is 2–5 r on every seed (`kj_baseline.txt`), so "holds up" (R-shift ≥ −r)
needs the population to more than halve its kJ within about five events.

- **Committed before any arm ends:** `runs/RBT-99/price.py BULKDIR > runs/RBT-99/price.txt`, the per-seed
  and per-fauna mean kJ over [T − 40, T) of the baseline, and its price. It runs once `onset.txt` exists
  and the baselines have finished. It reads only pre-T seasons, which are the same in every arm. With it
  committed, the readout needs no bulk and does not depend on `ckpt/*` surviving.
- **Printed per seed beside R-shift** by `runs/RBT-99/c2_block.py`: the price, and **net** = R-shift +
  price, the part of R-shift that is not arithmetic.
- **Stated now:** a co-evolved "does not hold up" no larger than its printed price is the price, not
  maladaptation. The "holds up" line itself is the protocol's and is not changed.
- **Correction:** §3's worst co-evolved margin is **0.245** (801, population kJ 7.31), not 0.30. RBT-10's
  bests understate the population: the population's mean kJ exceeds the bests' median on 8/10 seeds. E
  remains unlikely: the re-priced co-evolved gain is +0.495 to +0.946, and 0/10 seeds are below basal.

### F5 (caveat, adopted): the printed verdict carries C2's framing

`readout.sh` now runs `c2_block.py` after `readout.py`. The block prints, whatever the class:

- the C2 claim line verbatim ("one body's cheapness, not two bodies' contest");
- the falsifier in the owner's words, "the designed body wins on the held-out challenge", with a note
  that `readout.py`'s class-C string uses RBT-92's "after the shift" for the same class;
- forbidden reading (b)'s sentence.

`readout.sh` still exits with `readout.py`'s status.

### F6 (caveat, adopted): turnover is invisible to D. It is printed, and it binds the sentence.

`c2_block.py` prints, per seed and fauna, the shift arm's deaths and births over the transient and the
recovery window against the baseline's, with the ratio. **D's test is the protocol's and is not
changed.** Two sentence rules bind the report:

- **Any class A or C** with a designed transient-deaths ratio ≥ 2 is reported with that number in the
  same sentence, and the block flags it.
- **A designed fauna that passes D by churn** (ratio ≥ 2, alive ≥ 12, income ≥ 0.25) is described as
  "solvent by turnover", never as "unaffected".

### F7 (caveat, adopted): the impulse null sees only the first ten seasons of the designed deaths

`c2_block.py` prints, per seed, the shift arm's designed deaths over [T, T + 10), which is k's window,
and over [T + 10, T + 60). Wherever the second is the larger, R-null is read as "the shift did more than
an impulse cull of its first ten seasons' excess", not as "more than turnover". RBT-92 chose the impulse
form and the protocol names the spread form as the fairer, unbuilt null (§8). C2 makes that gap starkest,
and the report says so.

### Nits, fixed

- **`runs/RBT-92/run_arm.sh`:** under `set -e`, awk's exit status 2 on a missing onset or cull-k file
  killed the script before its message. Both reads now end in `|| true`, so the messages print; the exit
  code is still 2. This is pre-existing, shared, and has no other behaviour change.
- **`runs/RBT-99/run_arm.sh` and `readout.sh`** now `cd` to the repository root, so they launch from
  anywhere; `OUTROOT` is relative.
- **`readout.sh` did not link `cull-k-SEED.txt`** into the arm directory `readout.py` reads. V1 would
  have failed on every real seed, and the k = 0/0 rule would not have fired. Found in this answer's
  end-to-end test and fixed.

### RBT-92's 13:10 fixes, carried over: now in the shared scripts

PR #76 (RBT-92 amendments 1 and 2, `63518d9` and `9699cd1`, not yet merged) implements the coordinator's
13:10 ruling. **This branch merges it, so C2 runs the same code.**

1. **Extinct fauna earn 0** in every window and test (`readout.py` `Arm`, with a test).
2. **T is chosen on [T − 20, T) deaths only** (`onset.py`, with a test).
3. **V0 also compares `lineage-last.txt` rows** ending before T − 1.
4. **Class B needs ≥ 8 seeds** (`BMIN`).

Also carried over: RBT-92's rule that **a cull-k of 0/0 means the null is the baseline itself** (no arm is
run and R-null = R-shift). For C2 that needs no excess deaths in either fauna, which §10 makes unlikely.

### §10, amended predictions (these supersede §10; the original is printed beside them in the report)

- **Class:** D **0.30**, F **0.33**, A **0.12**, C **0.12**, B **0.10**, E **0.03**. Originally D 0.75.
  - Reason: churn at capacity is now the likelier designed response (F2).
  - With churn, R-body is read among survivors of two sorted faunas. Its sign across seeds is uncertain,
    so F is the modal class.
  - C is live because a designed fauna sorted to its cheap tail can earn a survivor-conditioned income
    above a co-evolved fauna paying about 0.27 in price.
- **Designed fauna:**
  - D's designed half met on ≥ 8/10 seeds: **0.35** (was 0.8);
  - alive < 12 inside the transient on ≥ 7/10: **0.15** (was 0.65);
  - extinct by T+160 on ≥ 5/10: **0.10** (was 0.5);
  - designed transient deaths ≥ 2 × base on ≥ 8/10 seeds: **0.8**;
  - designed R-shift, recovery: **−0.25** (−0.8 to +0.3) (was −0.75).
- **Co-evolved fauna:**
  - survives on 10/10 seeds: 0.85 (unchanged);
  - **R-shift, recovery: −0.24** (−0.40 to −0.10) (was −0.17). This is the population's price, median
    about 0.27, less a small sorting gain; co-evolved kJ is heritable too (slope 0.29–0.74);
  - **net of the price** (R-shift + price): **+0.03** (−0.08 to +0.15);
  - **"holds up": 0.12** (was 0.25).
- **k:**
  - K1 median **6** (0–15) (was 3);
  - K2 median **50** (30–60, capped at alive) (was 35);
  - K2 ≥ alive at T − 1 on at least one seed: **0.55** (was 0.3). That F1/F3 path is now the expected
    one, and the readout handles it.
- **R-null, co-evolved:** |R-null| ≥ r and within 0.05 of R-shift: 0.65 (unchanged; K1 stays small).
- **R-body, recovery:** **+0.10** (−0.40 to +0.60) (was +0.7).
- Recovery time, carriage and depth are unchanged from §10.

### §14, the sequence, amended

Add step **0b**, before any RBT-99 arm ends:
`scripts/durable.sh restore BULKDIR/forage-SEED rbt-90-SEED` for each seed, then
`python runs/RBT-99/price.py BULKDIR > runs/RBT-99/price.txt`, committed.

## Amendment 2 (posted before any RBT-99 arm exists): RBT-92's Amendment 3 carried over, and the re-check's two caveats

The coordinator approved C2's design at 14:08 UTC, subject to the shared gate. Since then, RBT-92's answer to
its own adversary round (its Amendment 3, commit `55cc86d` on `results/RBT-92-design`) has changed the shared
instrument. **C2 runs those scripts unchanged, so every change binds here.** This branch merges RBT-92's
design branch so that C2's code is the code RBT-92 will run. Each change and its effect on C2:

1. **The onset range is [340, 399]**, and a per-seed drift FLAG is printed. The FLAG fires when the
   baseline's deaths over [T, T+10) exceed 1.5 × its mean per ten seasons over [T−100, T). It is a caveat,
   not a re-pick. Inherited through `onset.py` and `readout.py`. The depth statement (§10) is unchanged to
   the stated precision.
2. **Carriage is L alone**, for both faunas; B and S are dropped. **§10's carriage prediction
   "B(T+160) shift − base within ±0.10, 0.55" is withdrawn.** "L(T+160) shift − cull within ±0.10,
   co-evolved, 0.5" stands. C2 makes no claim of a body structure acquired after T; the report says
   "survives" or "is sorted".
3. **Class E is split** in `readout.py`'s `classify()`, and the order is now E1 > D > E2 > A > C > B > F.
   - **E1:** both faunas bankrupt by D's test.
   - **E2:** co-evolved bankrupt, designed not, reported with the falsifier as its strongest form.
   - For C2, `c2_block.py`'s framing line now names E2 beside class C.
   - **Amended class predictions: E1 0.02, E2 0.01**, replacing E 0.03. The others are as in Amendment 1:
     D 0.30, F 0.33, A 0.12, C 0.12, B 0.10.
   - Falsifier (ii), "the co-evolved fauna fails on ≥ 3/10 seeds", stays as registered. E2 on
     ≥ ⌈0.8n⌉/n seeds implies it.
4. **V3 is renamed a manipulation check on the tracer.** C2 cites RBT-92's cull20 for it, as before.
5. **k per seed** is printed in SEEDS. **The turnover guard and the R-null predictions are scored only on
   seeds with co-evolved k > 0**, and the readout prints that count.
   - For C2 the designed k is expected to be large (Amendment 1: median 50). The co-evolved k may be small:
     Amendment 1 put K1's median at 6.
   - If co-evolved k is 0 on most seeds, the report says the co-evolved null could not test turnover.
6. **Recovery time: the paired form, against the control, is primary.** §10's recovery predictions are
   restated in that form:
   - **co-evolved shift:** paired recovery "none" within 180 on ≥ 7/10 seeds, **0.65**. The price is
     permanent, about 0.27 at the median, against h, so the shift arm stays apart from the control unless
     kJ halves. (Was "none" on ≥ 6/10 in the P form, 0.55.)
   - **designed shift:** paired recovery "none" on ≥ 8/10, **0.7**. This is lower than §10's 0.8, because
     under churn the survivor-conditioned income can return near the control's (Amendment 1).
   - **cull arm, co-evolved:** paired recovery ≤ 20 on ≥ 8/10, **0.6** (was 0.7, in the P form).
7. **The equivalence line** |mean| + r < 0.10 prints beside the class, and a draw is reported with it.
8. **`tables.py` writes `groups.txt`**, and **`run_arm.sh` runs `tables.py` as a post-run step.**
   - C2's wrapper execs RBT-92's launcher, so C2's arms get the step too. A dry run with python stubbed
     shows it writing into `runs/RBT-99/shift-SEED`.
   - C2's group size never changes, so `groups.txt` records the constant bank of fours.
   - §14's per-arm `tables.py` step is now automatic; a resumed arm runs it by hand.

**The adversary re-check's two caveats (13:50 UTC), adopted:**

- **R-cull on a capped fauna is labelled.** `readout.py` prints "(capped on [seeds]: extinction, not
  turnover; see the V1 note)" on the R-cull line of any fauna whose cull emptied it. The value is still
  printed, because it is what the cull did, but it is not quoted as turnover.
  `tests/test_rbt92_readout_cap.py` pins the label. This is a shared-instrument change, and it changes
  nothing where k < alive.
- **`price.txt` is a gate item.** §14's gate now reads: RBT-92's instrument cleared; RBT-90 part 2's
  readout posted; `runs/RBT-92/onset.txt` committed; **`runs/RBT-99/price.txt` committed** (step 0b); and
  this design adversaried, which is done. No RBT-99 readout runs without `price.txt`: `c2_block.py` prints
  an empty price column and says so.

**Checked:**

- `pytest` passes; the count is on the ticket.
- `readout.sh` ran end to end on the amended readout with a synthetic capped seed: V0–V2 pass, R-cull is
  labelled, the E1/D/E2 tests print, and the C2 block prints.
- The launcher dry run prints `--shift work-cost=0.08 --out runs/RBT-99/shift-801` followed by the
  post-run `tables.py`.
