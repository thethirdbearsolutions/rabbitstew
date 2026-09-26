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
   founder lumps above 1.25 kJ and one at 21.6. That tail would die, which raises k1 (§7) without
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

- **T** comes from `runs/RBT-92/onset.txt`. Whatever rule RBT-92 finally commits there (the senior
  review's pre-onset window, if adopted) is C2's T by construction.
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

- **(a) Reading D as the co-evolved body's win.** Readings 2 and 8's C2 line cover this.
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

State of RBT-92's instrument at the time of posting (13:45 UTC):

- the pre-registration is merged (PR #74);
- Amendment 1 (the verbatim quotations) is in PR #76;
- the senior review posted at 13:20, and **the coordinator adopted it in full at 13:10** (the ruling
  comment): four fixes, which go into RBT-92's next amendment PR together with its answer to the
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

None yet.
