# RBT-92 pre-registration: the first epoch (C1, crowding, `--group-size 4 → 8`)

Posted on RBT-92 before any RBT-92 arm exists. The designer runs no full arm. The only simulations
behind this document are two throwaway checks, each 20 seasons with the event at season 10:

- the shared-baseline check, three runs at each of seeds 801 and 9901;
- the readout smoke test on those same six runs, read for nothing. All six runs were then deleted.

The template follows `docs/held-out-challenges.md` §12 (RBT-89), field by field. Deviations from
RBT-89 are listed in §D, each with the measurement that forced it.

Branch `results/RBT-92-design`. Scripts:

- `run_arm.sh`: the launcher;
- `onset.py`: the rule for T;
- `cull_k.py`: the rule for k;
- `tables.py`: what an arm commits;
- `readout.py`: the readout;
- `cohort_cycle.py` / `.txt`: the cycle, measured;
- `shared_baseline_runs.sh`, `shared_baseline_check.py` / `.txt`: the byte check;
- `smoke.sh` / `smoke.txt`;
- `SEED-RULE.md`: committed at 12:26 UTC, before any RBT-90 output was read.

---

## Summary of the design

| | |
|---|---|
| challenge | C1 crowding: `--shift-at T --shift group-size=8` (RBT-89 §2; RBT-95 maps `group-size` → `group_size`) |
| seeds | **all ten** of RBT-90 part 2 (801 804 805 806 807 1 2 3 4 7). The rule was committed before any output was read, and the only exclusion is extinction by T − 1. |
| baseline (control) | **the seed's RBT-90 part 2 arm**. Shift and cull arms are byte-identical to it before the event (verified, §3). |
| new arms per seed | **shift** and **cull** (the null, k by RBT-89 §8's rule). Also **cull20**, the instrument's validation cull at k = 20 (RBT-89 §8, "validation before use"). |
| T | per seed, by a committed rule: the deaths trough in [340, 400] of the seed's finished baseline (§5). |
| windows | transient [T, T+60), **recovery [T+60, T+160) primary**, tail [T+160, T+200). All inside 600 seasons because T ≤ 400. |
| verdict | RBT-89 §9 classes A–F on R-body in the recovery window. r is the t(n−1) 95% half-width. |
| falsifier | **"the designed body wins after the shift"**: class C |
| cost | 30 arms × 600 seasons, about 31 session-hours. About **2 h 10 min wall** on 20 four-core cloud sessions (§13). |

---

## 1. Challenge and flag

One flag changes at T: `group_size` goes 4 → 8 (`--shift group-size=8`). It applies to both faunas, and it runs on the
baseline command of `docs/held-out-challenges.md` §1, which is exactly `runs/RBT-90/part2_run.sh`. `run_arm.sh`'s
command differs from `part2_run.sh`'s only by `$EVENT`, checked by a whitespace-normalised diff.

**Measured endpoint on random founders:** RBT-17, one seed (801), eight robots from season 0. There was no
extinction. Population-mean incomes were at parity: holistic +0.98 / +0.93 / +1.00 against designed
+0.81 / +0.92 / +0.96 over seasons 100–199 / 300–399 / 500–599. The designed *bests* out-ate the co-evolved bests
2.34 to 1.14 items. **Kind: competition.** Capacity 60 ÷ 8 leaves a remainder group; the smoke run shows groups
of `[4, 5, 8]` at the shift season. The readout reports which robots that group held via `cohorts.jsonl` (bulk).

## 2. Perception

**This challenge selects on standing morphology and gait only. Robust means survivorship of standing morphology
and gait through the shift, not adaptation during it. The axis and the falsifier are claims about income, not
perception.**

Crowding is perceivable in principle through the `agent` smell. In practice, no co-evolved individual among
RBT-17's final 60 carried an `agent` sensor. Blanking the designed side's three `agent` sensors cost 0.12 of 2.34
items, inside the seed noise (RBT-17 §3). **RBT-91 option in force: A.**

## 3. Comparator, and the shared baseline

The designed population of the same run is the comparator. Its brain evolved for T seasons under
`--conventional-topology`, and no controller is loaded or hand-set. It sits in separate arena banks and is never
merged. The ecology's RNG streams are RBT-95's.

**Shared baseline, verified** (`runs/RBT-92/shared_baseline_check.txt`, **PASS on both seeds**). At seed 801 (and
again at the throwaway seed 9901), 20 seasons, event at season 10, `--workers 1`, three runs:

- plain;
- `--shift-at 10 --shift group-size=8`;
- `--cull-at 10 --cull holistic=20,conventional=20`.

Against plain, **both event arms are byte-identical before season 10**:

- `lineage.jsonl`: 1185/1185 lines, same sha256;
- `cohorts.jsonl`: 20/20 lines;
- `history.json`: 20/20 entries;
- born genomes of all 183 individuals born before 10.

Seed 9901 gives the same result: 1200/1200 lines and 185 genomes.

Every file first differs at season 10. The configs differ only in `ecology.shift`/`shift_at` or
`ecology.cull`/`cull_at`.

Manipulation checks:

- The shift arm's groups are `[4]` at season 9 and `[4, 5, 8]` at season 10. The 4 and 5 are remainder groups.
- The cull arm writes exactly 20 `death: cull` rows per fauna, all at season 10.
- `shift` is on history entries 10..19. `culled` is on entry 10 only.

The coordinator's check (RBT-90 part 2) established that `--workers` 1 and 4 give byte-identical output.
**So each seed's RBT-90 part 2 arm is its no-event baseline, and RBT-92 adds two arms per seed plus the
validation cull.**

The readout re-checks this on every real seed from committed tables (V0, §7). Every arm's `seasons.txt` row for
every season < T must equal the baseline's. A code drift between the RBT-90 head (`852dcac`) and the head the
RBT-92 arms run on would fail V0 and stop the read. PR #72, merged after `852dcac`, touched `runs/RBT-90` and
`tests/` only.

## 4. Seeds

All ten: **801 804 805 806 807 1 2 3 4 7** (`SEED-RULE.md`, commit `66f5ab3`, 12:26 UTC). The ten pass RBT-90's
clauses 1 and 2 on the founders this head founds: composite 26/60 to 37/60, oscillator 7/60 to 18/60, all bodies
distinct (`docs/artifacts/RBT-90-head-founders.txt`; coordinator ruling, option A).

- **Exclusion:** either fauna at alive = 0 at T − 1 in the baseline. This is identical across arms, because the
  prefix is shared.
- **Underpowered rule:** if fewer than 6/10 remain, no verdict is issued.

**Why ten and not six:** at t(5), six seeds cannot reach class B (§8).

## 5. Onset: the natural cohort cycle, measured, and T placed off it

**Measured from committed data** (`runs/RBT-92/cohort_cycle.py` → `cohort_cycle.txt`; no run). The data are the
six committed 600-season ecology runs on this exact config:

- RBT-71 `forage-804/805/806`: selected, the RBT-90/92 economy;
- `neutral-804/805/806`: no starvation, turnover by `max_age` only. These are the ecology's drift arms.

Mean age per season is rebuilt from `lineage-last.txt`. An individual last seen at g with age a lived [g − a, g].
The rebuild's alive count equals `seasons.txt`'s in every season of every run (asserted).

- **The cycle is a 60-season mortality wave.** The deaths autocorrelation over seasons 100–599 peaks at lag 60 in
  **12/12** population-runs. Selected arms: +0.415 to +0.670, against a median |acf| of 0.06–0.16 at other lags.
  Drift arms: +0.878 to +0.883.
- **On the selected arms the wave is large.** Every selected population-run (**6/6**) has 10-season deaths windows
  of 20/60 or more after season 100, recurring every cycle, with a maximum of 47/60 (805 holistic, [140, 150)).
  The largest 10-season fall in holistic mean age is 20.1–24.5 years.
- **On the drift arms it is not.** 0/6 cross 20/60 (maximum 18/60), and mean-age falls are 5–8. So in this
  ecology, starvation synchronises the cohort that `max_age` then retires together. This is the reverse of
  RBT-80's GA reading, where the 40/60 transient was in the drift arms and not the selected ones.
- **Consequence:** RBT-89 §8's "T at least 20 seasons after the last 20/60 peak" **has no solution on a selected
  arm**. A peak recurs every 60 seasons to the end of every run.

**The rule, committed (`onset.py`).** Per seed, T is the season in **[340, 400]** that minimises D(T). D(T) is the
deaths of both faunas together over [T − 10, T + 10) in **the seed's finished baseline arm**; ties go to the
larger T.

- [340, 400] is one full cycle, so a trough always exists in it.
- 400 is the latest T whose tail window still ends by season 599.
- 340 keeps ≥ 11 reproduction events of depth before the onset.
- The rule reads deaths only, and only after the baseline arm has finished. No income column is read.

**Dry run on the committed RBT-71 arms** (for the design only, not RBT-92's seeds):

| seed | T | D(T) | range of D over [340, 400] |
|---|---|---|---|
| 804 | 370 | 58 | 58..88 |
| 805 | 375 | 33 | 33..113 |
| 806 | 362 | 30 | 30..81 |

In each case the next natural wave arrives 10–25 seasons after T. For example, 805 holistic has 41 deaths in
[T+10, T+20). The k window [T, T+10) sits in the trough, and the paired contrasts (shift − base, cull − base)
cancel the natural wave season by season, to the extent that the event does not re-phase it. **The event will
re-phase it:** it kills or crowds a cohort out of step. That is exactly why the null is a same-size cull at the
same season and not the baseline alone.

"Before" is the shared seasons [T − 100, T). The stagger seasons of RBT-89 §8 (371, 431, 491, 551 on RBT-71) do
not carry the peaks on these arms: the phase drifts by about 3 seasons a cycle and differs per seed. So the rule
reads the seed's own deaths rather than a formula.

## 6. Axis and windows

`mean_lifetime_score` from `seasons.txt`. Windows are relative to T:

| window | seasons | role |
|---|---|---|
| before | [T − 100, T) | the pre-event plateau; identical in all arms |
| transient | [T, T + 60) | the "at" window |
| recovery | [T + 60, T + 160) | **primary** |
| tail | [T + 160, T + 200) | reported, not scored |

**The readouts, all in `readout.py`:**

- **Contrast before, at and after:** R-body (holistic − designed, window mean) for every arm and window, per seed,
  and its mean with the t(n−1) 95% interval.
- **R-shift** (shift − base), **R-null** (shift − cull), **R-cull** (cull − base) and **R-cull20**. Each is per
  fauna and per window, the window mean of the per-season paired difference.
- **Recovery time to the pre-event income plateau**, per fauna and per arm:
  - P is the fauna's mean over [T − 100, T), and h is 2 SD of its per-season values there.
  - Recovery is the first d ≥ 0 with |x(t) − P| ≤ h for all t in [T + d, T + d + 20).
  - The value is "none" if no such d ≤ 180.
  - It is printed for base as well: the base's value is the instrument's floor. The paired form (x_arm − x_base
    against 0) is printed beside it.
  - Under a permanent shift, "none" is a legitimate and expected value (§10).
- **Survivors' carriage of pre-event body structure**, through RBT-84's descent rule (every parent followed, not
  `parents[0]`), on `lineage-last.txt`. C0 is the onset cohort, alive at T − 1.
  - **L(s):** the fraction of C0 with a living descendant at s, for both faunas.
  - **B(s):** the fraction of living holistic individuals whose **body structure** equals that of ≥ 1 of their C0
    ancestors.
  - **S(s):** the fraction of C0's distinct holistic body structures still present.
  - They are read at s = T + 60, T + 160 and T + 199, for shift − base, shift − cull and cull20 − base.
  - Body structure is `body_signature` (`rabbitstew/genetics.py`) with every continuous value dropped. It keeps the
    root, each node's shape, each connection's child, joint type, recursive limit, motor and mirror, and each
    node's non-neuron units. It is digested from each individual's genome at birth by `tables.py` into
    `bodysig.txt`.
- **Alive:** the minimum per window, and deaths over [T, T + 10).
- **Readouts reported beside every income number:** alive, births and deaths; per-seed lists; zero counts.

## 7. The null, and the instrument validated on the cull before it reads the shift

**Null (`cull`):** `--cull-at T --cull holistic=K1,conventional=K2`. Each k is that fauna's excess deaths in the
shift arm over [T, T + 10) against the baseline, floored at 0 (`cull_k.py`, RBT-89 §8). The rule reads deaths
only, as soon as the shift arm's first ten post-onset seasons exist, and before any window is read. It is
impulse form. If k = 0 for a fauna, that fauna draws nothing, and the report says R-null = R-shift for it.

**Validation arm (`cull20`):** k = 20 of each fauna at T. This is RBT-89 §8's own validation size, a third of
capacity. It does not depend on the shift, so it launches at once.

**Gates, printed first.** `readout.py` stops before the shift section if V0–V2 fail on any seed.

- **V0, pre-onset identity (A/A, exact zero):** every arm's `seasons.txt` row equals the baseline's for every
  season < T, both faunas, all five columns.
- **V1, manipulation:** `events.txt` has exactly min(20, alive) culled per fauna at T in cull20, and exactly the
  `cull-k` counts in cull, with no cull at any other season. The shift arm's entries carry the shift from T.
- **V2, round trip:** the alive count rebuilt from `lineage-last.txt` equals `seasons.txt`'s in every season of
  [T − 100, T + 200), every arm and fauna. So the descent tracer reads the population the table reports.
  - **V2 already caught one bug in the smoke test.** A culled individual's row, logged at the top of season T,
    repeats its season-(T−1) age, so its birth season was rebuilt one season late. The fix is in `readout.py`.
- **V3, sensitivity (the known-present effect):** the carriage instrument must resolve a random removal of a third
  of the onset cohort. The gate has two parts:
  - cull20 − base on L(T + 60), holistic, must have a t(n−1) 95% interval entirely below 0;
  - the paired alive dip, min over [T, T + 10) of alive_cull20 − alive_base, must be below 0 on n/n seeds, both
    faunas.
  - If V3 fails, the carriage readouts of the shift are printed but labelled UNVALIDATED. They do not enter any
    sentence of the report.

**Deviation from RBT-89 §8's validation sentence.** It asks that "R-null … at k = 20 be resolvable" on income. A
*random* cull selects on nothing, so its effect on `mean_lifetime_score` is not known to be non-zero: removing
random individuals leaves the mean unchanged in expectation, and the age-structure change moves it by an unknown
amount of either sign. An instrument that "fails" to see it may be right. So income is not the gate; the
validation uses effects that are known to be present. R-cull20 on income is printed with its interval as a
calibration of what a same-size turnover does to the axis. This is RBT-89 §9's second bullet, the "class-A about
turnover" check.

## 8. Resolvable effect size

The readout prints RBT-89 §7's line from each seed's baseline over [T − 100, T): the season-noise figure, and the
figure from the observed between-seed spread of per-seed R-body. **r is the larger, as a t(n−1) 95% half-width,
not 2 SE.**

**Before the run, from RBT-89's measured 100-season windowed spread (SD 0.108, three seeds, ±40%):**

| n | t(n−1) | half-width t·0.108/√n | class B reachable (r ≤ 0.10)? |
|---|---|---|---|
| 6 | 2.571 | **0.113** | **no** |
| 7 | 2.447 | 0.100 | at the edge |
| 8 | 2.365 | 0.090 | yes |
| 10 | 2.262 | **0.077** | yes |

**Six seeds resolve 0.113, not 0.10.** The t(5) half-width is 28% wider than RBT-89's 2 SE line (0.088 at six).
That is why the seed rule takes all ten. **At ten seeds the design resolves an R-body of about 0.077**, which is
below the 0.10 worth claiming, so a draw is distinguishable from an unresolved result. The SD itself is known to
±40%. The realised r is printed and used, and if it exceeds 0.10 the arm can return only A, C, D, E or F.

## 9. Verdict rule

RBT-89 §9's classes on shift-arm R-body in the recovery window, with r from §8:

| class | rule |
|---|---|
| **A**, co-evolved wins | mean ≥ +0.10, positive on ≥ ⌈0.8n⌉/n seeds, and \|mean\| ≥ r |
| **B**, draw | \|mean\| < 0.10 and r ≤ 0.10 |
| **C**, designed wins | **the falsifier**: mean ≤ −0.10, negative on ≥ ⌈0.8n⌉/n, and \|mean\| ≥ r |
| **D**, designed bankrupt | on ≥ ⌈0.8n⌉/n seeds, the designed fauna's transient or recovery mean < 0.25, **or** its alive < 12, while the co-evolved does neither |
| **E**, both fail | both faunas reach 0, or co-evolved recovery mean < 0.25, on ≥ ⌈0.8n⌉/n |
| **F**, unresolved | otherwise |

- **Order:** E, then D, then A, then C, then B, then F.
- **B takes precedence over F** when r ≤ 0.10. RBT-89's B and F overlap at \|mean\| < r ≤ 0.10, and its B text
  intends a draw there.
- **The sign guard** is ⌈0.8n⌉: 5/6 and 8/10, as RBT-89 wrote it. It is a guard, not the verdict.
- **Two further lines, printed whatever the class:**
  - "holds up" is earned only if the co-evolved R-shift (recovery) ≥ −r. Otherwise a class-A result reads
    "outlasts".
  - **Turnover guard:** if \|co-evolved R-null\| < r, the shift did no more to co-evolved income than a same-size
    random cull, and the report says so.
- **No R-body is computed before every arm of every seed has ended.** A partial read of a running arm is not a
  result. `cull_k.py`'s read of deaths over [T, T + 10) is the one pre-registered exception. It reads no income.

## 10. Point predictions, with confidence

Stated so they can embarrass their author.

- **Class B (draw), 0.45.** Otherwise F 0.20, A 0.15, C 0.12, D/E 0.08.
- **R-body in the recovery window:** mean **+0.03**, per-seed range −0.15 to +0.20. "Before" is +0.12 (RBT-71's
  100–599 leads average +0.12). At the transient it is **+0.02**. In the tail it is +0.04.
  - Reasons: at eight robots from founders, RBT-17 read parity, +0.02 to +0.17. The shift costs the cheap mowers
    more than the designed body, because a mower's yield is path × eat width × *remaining* density, and density
    is what doubling the group halves. The designed side's income was flat at +0.8 to +1.1 in every run.
  - What would embarrass this prediction: the evolved population's mowing gait carrying a lead into crowding that
    RBT-17's random founders did not have. Then the result would be class A.
- **R-shift, recovery:** holistic **−0.20** (range −0.35 to −0.05), designed **−0.08** (−0.20 to +0.05),
  confidence 0.55 that holistic < designed. Designed survives the shift on 10/10 seeds (0.85).
- **k (the null's size):** K1 holistic median **6** of 60 (range 0–20). K2 designed median **3** (0–15).
  Confidence 0.6 that K1 ≤ 10 on ≥ 8/10 seeds.
- **R-null (shift − cull):** \|holistic R-null\| > r, and close to R-shift, 0.6. A random cull of k ≤ 10 returns
  to the income plateau within 20 seasons. The crowding stays.
- **Recovery time to the pre-event plateau:**
  - shift, holistic: **"none"** on ≥ 7/10 seeds (0.6), because the crowding is permanent;
  - shift, designed: ≤ 60 seasons on ≥ 6/10 (0.5), because its drop is about h;
  - cull and cull20, both faunas: ≤ 20 on ≥ 8/10 (0.7);
  - base: 0 on 10/10 (0.8).
- **Carriage:**
  - L(T + 160), shift − cull: within ±0.10 (0.55). The crowding sorts lineages about as much as a same-size random
    cull.
  - B(T + 160), shift − base: within ±0.10 (0.55). Bodies are carried, not re-sorted, at ≤ 5 events of depth.
  - V3 passes (L(T + 60) cull20 − base clearly negative): 0.85.
- **Class-D test:** not met (0.9).

## 11. Falsifier, in the owner's words

**"The designed body wins after the shift."** That is class C by the rule in §9, written before any arm exists.

**Also falsified if** the designer's secondary prediction fails. The author is most exposed on "the shift costs the
co-evolved body more than the designed one". The prediction is falsified if holistic R-shift ≥ designed R-shift in
the recovery window with the difference's t(n−1) interval above 0.

## 12. Expected depth

- **Before the onset:** 2T/60, which is **11.3–13.3** events for T in [340, 400].
- **After:** 2(600 − T)/60, which is 6.7–8.7.
- **Inside the transient plus recovery window:** about 5.3.

"Re-adapts" therefore means at most about five sequential mutations. The report says "survives" or "is sorted"
unless carriage shows a body structure acquired after T (B < 1 among survivors, with the new structure traced).
Depth is measured afterwards with RBT-71's `measure.py` depth on each arm's `lineage-last.txt`.

## 13. Per-arm command, sequencing and cost

Per seed, after its RBT-90 arm has finished and been pushed, the steps run in this order.

**Step 0: onset.** Run once for all seeds, by the designer or the coordinator, before any RBT-92 arm launches.
It commits `runs/RBT-92/onset.txt`.

```
python runs/RBT-92/onset.py > runs/RBT-92/onset.txt
```

**Session A: the shift arm.**

1. Launch as harness background tasks:
   ```
   WORKERS=4 runs/RBT-92/run_arm.sh SEED shift
   DURABLE_WATCH_PID=<pid> scripts/durable.sh every 20 runs/RBT-92/shift-SEED rbt-92-shift-SEED
   ```
2. At season T + 10, about 38 minutes in, run
   ```
   python runs/RBT-92/cull_k.py SEED > runs/RBT-92/cull-k-SEED.txt
   ```
   Then commit and push it.
3. At the end, run `python runs/RBT-92/tables.py runs/RBT-92/shift-SEED`, then commit and push.

**Session B: the validation cull, then the null.**

1. Run the validation cull:
   ```
   WORKERS=4 runs/RBT-92/run_arm.sh SEED cull20
   ```
   Keep the durable loop beside it (label `rbt-92-cull20-SEED`), and run `tables.py` when it ends.
2. Pull `cull-k-SEED.txt`.
3. Run the null:
   ```
   WORKERS=4 runs/RBT-92/run_arm.sh SEED cull
   ```
   Keep the durable loop beside it (label `rbt-92-cull-SEED`), then run `tables.py` and push.
4. Also produce the baseline's body digests:
   ```
   scripts/durable.sh restore runs/RBT-90/forage-SEED rbt-90-SEED
   python runs/RBT-92/tables.py runs/RBT-90/forage-SEED --bodysig-only --to runs/RBT-92/base-SEED
   ```

**Readout:** after all arms of all seeds have ended, run
`python runs/RBT-92/readout.py > runs/RBT-92/readout.txt`.

**Cost.** The rate is about 6 s per season on four cloud cores (state doc §2). The throwaway runs showed no
slowdown at group size 8: 14.7 s per season shifted against 15.5 s plain, at one worker with three runs side by
side.

| arm | arms | seasons | wall per arm |
|---|---|---|---|
| shift | 10 | 600 | ~60–70 min |
| cull20 | 10 | 600 | ~60 min |
| cull | 10 | 600 | ~60 min |
| **total** | **30** | **18,000** | **~31 session-hours** |

On 20 sessions (A and B per seed), wall time is **~2 h 10 min**: session B runs cull20 and then cull, and k is
ready at about 40 minutes. On 30 sessions it is about 1 h 45 min. If cull20 is dropped to save compute, the
instrument has no known-present effect to be validated on whenever the rule's k is small, which is the predicted
case (K1 median 6). I recommend keeping it.

## 14. What is committed

Per arm: `config.json`, `seasons.txt` (with `mean_age` and `max_age`, and alive = 0 rows for an extinct fauna),
`lineage-last.txt`, `bodysig.txt`, `events.txt`, `event.txt`. Per seed: `cull-k-SEED.txt`, `base-SEED/bodysig.txt`.
Also `onset.txt`, `readout.txt` and `REPORT.md`. Bulk stays out.

The readout reads only these files. The round trip will be checked from a clean checkout, with one cell perturbed.

## 15. Adversary

The adversary is named by the coordinator. The readings the designer is most exposed to:

1. **The onset rule reads the baseline's deaths around T.** Is choosing a trough a way to choose a favourable
   start?
2. **Replacing RBT-89's income validation with carriage and alive** (§7).
3. **The body-structure digest's granularity:** too coarse, and B is trivially 1; too fine, and it is trivially 0.
   The readout prints S and B at T + 60 on the base, which shows the scale.
4. **R-body's window mean skips seasons where either fauna is extinct**, which class D and E must catch.

## 16. Amendments

None are allowed after the arms launch, except amendments that touch data that does not yet exist, posted as such
with the reason.

## D. Deviations from RBT-89, each forced by a measurement

1. **§8 onset rule → trough rule.** "≥ 20 after the last 20/60 peak" has no solution on 6/6 selected
   population-runs (`cohort_cycle.txt`).
2. **§8 validation on income → V0–V3 on known-present effects** (§7 above).
3. **§7 r = 2 SE → the t(n−1) half-width** (the resumption guide's rule). Six seeds resolve 0.113, not 0.088.
4. **The control is not a third run.** It is the seed's RBT-90 arm, byte-identical before T (§3). The validation
   cull is added in its place.
5. **B/F overlap resolved in favour of B** when r ≤ 0.10. The sign guard is ⌈0.8n⌉/n.

---

## Amendment 1 (posted before any RBT-92 arm exists): the coordinator's 12:43 notes folded in

**1. Six seeds.** The notes ask for six from the committed ten. The committed seed rule (`SEED-RULE.md`,
`66f5ab3`) takes **all ten**, and the ruling says it stays as committed; ten contains every six. The
notes quote the draw margin as r = 0.088 at n = 6: that is RBT-89 §7's 2 SD/√n. Under the programme's
rule, a t-interval at that n, six seeds give t(5) · 0.108/√6 = **0.113**, which exceeds 0.10, so class B
(the draw) is unreachable at six. Ten give 0.077 (§8). If the coordinator prefers six, the rule for
choosing them must be committed before part 2's readout is read. I propose the first six in the
committed order (801 804 805 806 807 1). I recommend ten.

**2. The cohort cycle on each seed's own baseline run.** `onset.py` already chooses T from each seed's
own baseline deaths. The cycle readout is now available per seed too:
`cohort_cycle.py --baselines` gives peaks, period, mean-age falls and deaths at the candidate onset,
read from the seed's committed RBT-90 tables. It is committed beside `onset.txt` as
`cohort_cycle_baselines.txt` before any arm launches.

**3. Per-fauna cull.** This is already in place (§7, `cull_k.py`). k is each fauna's own excess deaths
over [T, T+10), floored at 0. A fauna at 0 draws nothing, and the report says R-null = R-shift for it.

**4. Class D by income, with the 12-of-60 floor.** This is already in place (§9, `readout.py`). D is met
by transient or recovery income < 0.25, or alive < 12, and not by extinction.

**5. The claim line and the forbidden readings, quoted from `docs/held-out-challenges.md`.**

The claim tested for C1 (§2):

> **Claim tested:** the owner's own, in full: under a shift both bodies survive, does the co-evolved
> body out-earn the designed one, draw, or lose. C1 is the only challenge in the set that can
> return every class in §9.

The statement required in every C1–C3 pre-registration (§3):

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
>     arithmetic on cited numbers.

**6. "Robust" means survivorship of standing morphology and gait** (§2). RBT-97's first result, that a
compass pays when it is installed, does not change this: no standing population carries a paying
compass, so none can express one during the shift.

**7. The ruling: no RBT-92 arm launches until RBT-90 part 2's readout is posted.**
- After the readout posts, I will state on the ticket whether it changes which seeds are informative:
  an extinct holistic fauna, or a founding-population split the set samples badly.
- Any change is posted as Amendment 2, with its reason, before any RBT-92 arm exists.
- I will also measure the reproduction-event depth per seed and per fauna from part 2's committed
  `lineage-last.txt` (RBT-71's `measure.py` depth), and say whether the post-event window of RBT-89
  (transient 60, recovery 100, tail 40) still holds about five events. The window is not re-chosen
  unless depth departs from 2 × seasons ÷ 60 by more than RBT-90's pre-registered band [15, 26] at 600
  seasons, and any such change is an amendment made before any arm exists.
