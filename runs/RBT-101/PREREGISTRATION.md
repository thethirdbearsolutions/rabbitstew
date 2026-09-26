# RBT-101 pre-registration: epoch C4, the furniture removed (`--shift terrain=flat`)

**Status.** Design only. No C4 arm has been run. This is built **on RBT-92's instrument** (`runs/RBT-92/`), as
RBT-99's description sets out for every sibling. The only runs made for this document were two short throwaway
pairs for the start-seed check (§3, 20 seasons each). The only other measurements read the RBT-90 part 2
checkpoints' **genomes and lineage, never an income column**: the positive control (§6.4) and the endpoint probe
(§1). **Gate (RBT-99's, per RBT-101):** nothing launches until all of these hold:
- RBT-92's instrument has cleared its adversary and senior review;
- RBT-90 part 2's readout is posted;
- this design has had its own adversary round, with an adversary the coordinator names.

**What carries over from RBT-92 by construction.** C4 calls RBT-92's code, not copies of it: `onset.txt`,
`cull_k.py`, `tables.py` and `readout.py` (through `readout.sh`). So an amendment RBT-92's adversary forces on
any of those binds C4 with no edit here, and §15 lists what is pending.

---

## Summary

| | |
|---|---|
| challenge | **C4, the furniture removed**: `--shift-at T --shift terrain=flat` |
| perceivable? | **yes**, the only one in the set (§2). Reported separately from C1–C3 and never pooled with them |
| seeds | RBT-92's rule, **all ten** RBT-90 part 2 seeds (801 804 805 806 807 1 2 3 4 7). The only exclusion is extinction by T − 1 |
| baseline | the seed's RBT-90 part 2 arm. It is byte-identical before T (RBT-92 §3), and **under a terrain shift it keeps the same start seeds after T** (§3, PASS) |
| T | RBT-92's `onset.txt`, the same seeds, baselines and rule |
| new arms per seed | **shift** and **cull** (the null, k by RBT-89 §8 through RBT-92's `cull_k.py`). **cull20 is RBT-92's arm, cited**: it carries no challenge flag, so it is the same arm for every challenge (§7) |
| income verdict | RBT-89 §9 classes A–F on R-body in the recovery window, by RBT-92's `readout.py`, unchanged |
| **re-wiring readout** | **`new`**: the fraction of survivors at T + 160 carrying a direct posture link that none of their onset ancestors had. Contrasts are shift − base and shift − cull, and the verdict needs both t(n−1) intervals to exclude 0. **Validated by a positive control on real evolved bodies at the n used** (§6) |
| falsifier | **"the designed body wins after the shift"**: class C |
| cost | 20 arms × 600 seasons, about **21 session-hours**; about **2 h 10 min wall** on 10 four-core sessions |

## 1. Challenge and flag

`world.terrain` goes from `random` to `flat` at T for both faunas, on `docs/held-out-challenges.md` §1's
baseline command. That is exactly `runs/RBT-90/part2_run.sh` and RBT-92's `run_arm.sh`.
`runs/RBT-101/run_arm.sh` differs from RBT-92's only in `$EVENT` (`shift` → `--shift terrain=flat`) and in the
output directory. Its `exec python …` line is identical. The shift's CLI alias `terrain` maps to
`world.terrain` (`rabbitstew/ecology.py`, `SHIFT_ALIASES`).

**The baseline's terrain:** fourteen random obstacles, heights 0.03–0.3 m and footprints 0.15–0.7 m, resampled
every season. **The challenge removes them**, and the food and the economy are untouched.

**Endpoint on random founders: none measured in the ecology** (§2 table, §13). The protocol's §13 names the
measurement that would supply a prior: "`scripts/forage_probe.py` with the run's config at `--terrain flat` on
committed bests, 64 paired draws, before the arm: a probe, not a run of the arm". `runs/RBT-101/flat_probe.py`
is that probe. It runs each seed's season-300 best of each fauna alone in the arena on 64 paired draws, on the
baseline's random terrain and on flat ground, and reads items eaten and displacement. The bodies are the RBT-90
part 2 checkpoints' `best_gen0300.json`: genomes only, no income column read. Readout: `flat_probe.txt`.
{{PROBE}}

**Kind: perceivable.** Obstacles reach the brain through `contact`, `height`, `up` and the joint sensors, at
weights the operator reaches.

## 2. Perception, claim line and forbidden readings (verbatim)

`docs/held-out-challenges.md` §2, C4, the perception paragraph and the claim line:

{{Q_C4}}

§3, the C4 bullet:

{{Q_S3}}

**So C4's pre-registration carries no "survivorship of standing morphology and gait only" sentence.** That
sentence is required of C1–C3. For C4, "re-adapts" *could* mean a new use of an existing sensor, and §6
measures whether it does. The income axis and the falsifier remain claims about realised income. A class-A
result says the co-evolved body earned more on open ground. It does not say the body perceived open ground,
unless §6 returns RE-WIRED as well, and even then only at the depth §12 states.

§14, the readings this protocol forbids, verbatim:

{{Q_14}}

How C4 meets them:
- Item 7: every C4 table and sentence is labelled C4 and reported apart.
- Item 10: §6's scored statistic is exactly "a lineage … acquired something it did not carry at onset", read
  with RBT-84's descent rule (RBT-92's `Arm.anc0`).
- Items 1–6, 8, 9 and 11 are met as RBT-92 meets them. The challenge was named by RBT-89 before any control
  ran. The windows, classes and the r rule are RBT-92's. The arms are paired on RBT-95's streams (§3).

## 3. Comparator, shared baseline, and the start seeds after T

The comparator is the designed fauna of the same run, exactly as RBT-92 §3 sets it up.

**Shared baseline before T:** RBT-92 §3's check, PASS on two seeds, covering lineage, cohorts, history and
born genomes (`runs/RBT-92/shared_baseline_check.txt`). RBT-92's V0 re-checks it on every real seed.

**Past T, for what the terrain stream feeds: PASS** (`start_seed_check.txt`, from `start_seed_runs.sh` and
`start_seed_check.py`). At seeds 801 and 9901 I ran plain and `--shift-at 10 --shift terrain=flat` for 20
seasons each, RBT-90 part 2's command otherwise (the `BASE` string is identical to RBT-92's check, verified
with `diff`). On both seeds:

- **Before 10:** `lineage.jsonl` is byte-identical (1185 lines at 801, sha256 `6018e0a9f5ec7965`, the same
  digest RBT-92's check printed for its plain arm), as are `cohorts.jsonl` (20/20) and `history.json` (20/20).
- **Start seeds:** `history.json` `start_seed` is equal in **20/20 seasons, 10/10 of them after the onset**,
  on both seeds. `cohorts.jsonl` `start_seed` is equal in **40/40 rows (20/20 after the onset)** on both.
- **Terrain seeds:** equal before 10. From 10 the flat arm records `None` and plain records its draw, so the
  stream advances identically whatever the terrain. This is RBT-95's amendment, now observed on the
  ecology's own output rather than only in `test_a_flat_terrain_shift_keeps_the_start_seeds_paired_with_the_control`.
- **Group sizes:** equal in every row where the member counts are equal (34/34 at 801, 32/32 at 9901). The
  rows that differ in member count (6 and 8) are all at or after the onset. A different death is the challenge
  acting, and the grouping rule is the same.
- **Seat assignments:** first differ at season 11 on both seeds. They are drawn from each fauna's own
  stream, so they diverge once a birth or death differs. That is the challenge acting, not a stream
  misalignment: the start seeds stay equal.
- **Config:** the arms differ only in `ecology.shift` and `ecology.shift_at`.

**So a C4 arm and its RBT-90 baseline share every start position before and after T.** Every difference after
T is the terrain, or its consequences through who lives and breeds.

## 4. Seeds

RBT-92's seed rule (`runs/RBT-92/SEED-RULE.md`, `66f5ab3`) is adopted unchanged: **all ten**, and the only
exclusion is extinction by T − 1 in the baseline. It is decided by the shared prefix, so it is the same in
every arm and every challenge. Below 6/10, no verdict is issued. Class B needs ≥ 8 surviving seeds on the prior
SD (RBT-92 §8 and the senior review).

## 5. Onset

**T per seed is RBT-92's `onset.txt`.** It is the same file, because the seeds and baselines are the same, and
`run_arm.sh` reads it from `runs/RBT-92/`. The coordinator ruled at 13:10 that RBT-92's onset rule reads
pre-onset deaths only, D(T) over [T − 20, T), which replaces [T − 10, T + 10). C4 takes the resulting T
automatically, from whatever `onset.txt` RBT-92 commits before launch.

## 6. The re-wiring readout (C4-specific)

C4 is the only challenge where "was anything re-wired during the challenge" is live (§2 claim line; §3). The
readout compares **the survivors before the onset against the survivors after it**, per fauna, and asks
whether posture-to-motor wiring was **acquired along descent** after T more often than in the baseline and in
a same-size random turnover.

### 6.1 The per-individual digest (`wiring.py`)

For every individual, from its genome at birth, `wiring.py` writes `wiring.txt`, one row per individual, the
same way RBT-92's `tables.py` writes `bodysig.txt`. It uses `rabbitstew.analysis.signed_influence` (RBT-63) on
the phenotype, over the pairs (posture sensor, live effector). The posture sensors are `contact`, `height`,
`up` (three axes), `joint_angle` and `joint_velocity`, the ticket's list:

- **g1**: Σ |gain| at depth 1, the direct links. These are exact (a "direct" link is a two-tick path, RBT-66).
- **g2**: Σ |gain| through depth 2. This is an upper bound through tanh (the docstring). Depth 2 is chosen by
  the circuit under test: the designed fauna's founders carry **no** direct posture link, so their posture
  wiring runs through the hidden layer (checked on the 40 founders of the throwaway run: 0 depth-1 posture
  pairs on the designed side). Deeper sums are not used, because the recurrent core's spectral radius exceeds 1
  (RBT-81).
- **n1, n2, ns**, and g2 split by sensor class.

**Sign is dropped:** a sign is comparable only across bodies with the same effector layout, and these bodies
differ.

### 6.2 The statistics (`rewire.py`)

C0 is the individuals alive at T − 1, the same in all three arms (checked, gate V-W). P(s) is those alive at
s. Descent follows RBT-84's rule, every parent followed, through RBT-92's `Arm.anc0` on `lineage-last.txt`.

- **new(s), scored.** The fraction of P(s) whose g1 is at least **0.5** above the largest g1 among its C0
  ancestors: a new direct posture link, of at least half the operator's typical weight (RBT-62: median |w|
  0.85–1.13). This is §14 item 10's "acquired something it did not carry at onset", counted per survivor.
- **wired(s)**: the fraction of P(s) with any direct posture link, minus that fraction in C0. This carries the
  SORTED verdict.
- **lost(s)**, printed and not scored: the mirror of new, g1 at least 0.5 below every C0 ancestor's. The
  positive control installs links and removes none, so a loss is not validated.
- **W-acq and W-sort on g1 and g2**, printed and not scored (§6.3): the mean change along descent, and in the
  population mean.

These are read at **T + 160 (primary**, the end of the recovery window), with T + 60 and T + 199 beside it.
The contrasts per seed are **shift − base** (the challenge), **shift − cull** (the challenge against the same
turnover) and cull − base. Each mean over seeds is printed with its t(n−1) 95% interval and the sign counts
k/n.

### 6.3 Why `new`, and why no sign guard: measured on a development window before any C4 arm existed

I first built the readout on the mean statistics (W-acq and W-sort on g2). Before writing any prediction, I
ran the positive control on a development window: C0 alive at 14, P alive at 175, on the seven checkpoints
then past 175. **On the holistic fauna, the mean statistics could not see a reflex installed on every
survivor.**
- The holistic g2 is heavy-tailed: mean 2.75, median 0.06 over P.
- Its between-seed drift over 161 seasons has sd **1.56** (W-acq) and **5.39** (W-sort), against an installed
  +1.0.
- Detection at f = 1.0 was **0/100** on g2 and **18/100** on g1, with the sign guard on, at n = 7.

**The count `new` is not dominated by a few very large bodies.** Its natural drift sd was 0.14 (holistic) and
0.05 (designed), and it detected the installed reflex at f = 1.0 on **100/100** replicates for both faunas at
n = 7 without the sign guard. On the designed fauna it detected it from **f = 0.1**.

**The sign guard (≥ ⌈0.8n⌉/n) is dropped for this readout, and the sign counts are still printed.** A seed
whose fauna carries no posture sensor cannot be re-wired in C4's sense. Development seed 807's holistic
survivors: 3/60 could carry the reflex. A seed like that reads 0, so the sign count punishes the absence of
substrate, not the absence of an effect. With the guard on, `new` detected f = 1.0 on 79/100 at n = 7.

The development numbers are in the commit history (`control.py` with `RBT101_STAT`/`RBT101_SIGN_GUARD`, the
same tables at a different window). The committed control (§6.4) is re-run at the pre-registered window.
**This choice was made on the baseline's bodies, before any C4 arm existed and without any income column. It
is a choice of instrument, not of outcome.**

### 6.4 The positive control (`control.py`; RBT-66's rule; ticket item (b))

**Bodies.** These are real evolved bodies in this exact economy: the RBT-90 part 2 baselines, read from their
`ckpt/rbt-90-SEED` checkpoints (genomes and lineage only). C0 is the individuals alive at 139 and P those alive
at 300: `T_cal = 140`, read at `T_cal + 160`. These are the two groups `rewire.py` compares, at a
pre-registered onset-like distance. The genomes at those seasons are fixed, since descent in a run never
changes after it is written. So `control/SEED.txt` re-derives from each finished RBT-90 arm, not only from
the checkpoint. The checkpoint commit per seed is in the table's header.

**The installed reflex.** For each survivor in P, one **direct link from one of its own posture sensors to one
of its live effectors**:
- at w = 1.0 (the operator's typical weight) and at w = 0.5;
- the pair drawn by a stream seeded from the individual's name, so it is fixed;
- installed on the phenotype, so it is a new use of a sensor the body already carries, which is what §3 says
  re-adaptation in C4 could be;
- not possible on a body with no posture sensor or no live effector (installable = 0).

**The test.** For each n from 10 down to 6, and each installed fraction f of P's installable bodies, 400
replicates:
1. Draw n seeds and install the reflex on a random fraction f of each seed's P (the pseudo-shift).
2. Pair each drawn seed with another by a random derangement, twice. These give the pseudo-base and the
   pseudo-cull, with no install.
3. Apply `rewire.py`'s RE-WIRED rule on `new`.

**The noise is between seeds, which is conservative.** A real seed's shift and base share C0 byte for byte;
here they come from different seeds.

**The false-positive check** uses a random half-split of each seed's P, with no install. The between-seed model
has zero mean without an install, by construction: every drawn seed appears once on each side.

**PASS at n (pre-registered):**
- at f = 1.0 and w = 1.0, RE-WIRED fires in the right direction on ≥ 95% of replicates, for each fauna;
- and the half-split false-positive rate is ≤ 10%.

`control.txt` prints `CONTROL n=N PASS|FAIL` and the smallest f detected on ≥ 80% of replicates. `rewire.py`
reads that line at the realised n: if the control did not pass at that n, the verdict is **UNVALIDATED** and
nothing enters a sentence.

**Liveness, reported and not gated.** RBT-66's frozen-trajectory probe is generalised to any body. It saves
the state, steps 8 ticks with the posture sensors live and again with them zeroed, holding every other sensor,
and takes the peak mean |Δ| over the driven degrees of freedom. It runs in one bout on flat ground, on 3
installable survivors per fauna per seed, with and without the reflex. It shows how often an installed reflex
is also functionally live on open ground. A reflex on a contact sensor that is never touched on flat ground is
present in the wiring and silent in the bout. **"RE-WIRED" means wiring acquired, not wiring shown to be
used**, and the report says so.

{{CONTROL}}

### 6.5 The verdict rule (per fauna, on `new` at T + 160)

- **RE-WIRED:** both conditions hold, and the positive control passed at the realised n. The direction is
  reported.
  - new, shift − base: the t(n−1) 95% interval excludes 0;
  - new, shift − cull: the interval excludes 0, with the same sign.
- **SORTED:** wired, shift − base excludes 0, and RE-WIRED does not hold. The survivors' posture wiring moved,
  but not along descent.
- **NO CHANGE SEEN:** otherwise. The half-width and the control's smallest detected f are printed.
- **UNVALIDATED:** the control failed at this n. Nothing from `rewire.py` enters a sentence.

Gates, printed first:
- **V-W:** every individual in C0 and every P(s) has a wiring row, in every arm.
- **C0 identical** across base, shift and cull, in membership and wiring.

`rewire.py` reads only committed tables:
- `seasons.txt`, `lineage-last.txt` and `events.txt` (RBT-92's `tables.py`);
- `wiring.txt`, per arm, and for the baseline at `runs/RBT-101/base-SEED/`;
- `control.txt`.

### 6.6 Depth limits: what "re-wired" can mean at about five reproduction events

- T → T + 160 is **about five reproduction events** along a lineage (RBT-89 §10: 2 × 160 / 60 ≈ 5.3), and
  RBT-92 §12 carries the same figure.
- A RE-WIRED verdict therefore means one thing: within about five mutations of the onset, the fraction of
  survivors carrying a new direct posture link rose above the baseline's own drift and a same-size cull's, by
  more than the between-seed noise.
- **It does not mean a reflex was searched for, and it does not show the link is used.** Liveness is
  reported, not gated.
- The installed reflex is a single link. A re-wiring that changes weights on links the body already carries,
  by less than 0.5, is below `new`'s threshold. W-acq prints it, unscored.
- **The readout resolves** at n = 10 an f of about {{FMIN}} of installable survivors on the holistic fauna and
  {{FMIN_C}} on the designed (§6.4). **A re-wiring reaching fewer survivors than that is invisible**, and NO
  CHANGE SEEN does not exclude it.
- The natural rate of `new` on the baseline over 161 seasons is {{NATRATE}} (`control.txt`, unscored). A
  challenge must beat that rate by the resolved f.

## 7. The null, and cull20

- **Null:** per fauna, k = max(0, the shift arm's deaths over [T, T+10) − the baseline's), by RBT-92's
  `cull_k.py` pointed at this ticket's shift arm: `python runs/RBT-92/cull_k.py SEED runs/RBT-101/shift-SEED >
  runs/RBT-101/cull-k-SEED.txt`. It reads deaths only.
- The cull is impulse form, at T. A fauna with k = 0 draws nothing, and its R-null equals its R-shift, which
  the report says.
- **cull20** (k = 20 each, at T) carries no challenge flag. Its command is identical at a given seed and T for
  every challenge, and runs are deterministic (workers 1 and 4 are byte-identical), so it is the same arm.
  **C4 cites RBT-92's `runs/RBT-92/cull20-SEED`**, through `readout.sh`'s links, for RBT-92's V0–V3.
- `rewire.py` has its own validation: the positive control, since the readout is structural.

## 8. Axis, windows, income classes

These are RBT-92 §6 and §9, unchanged, computed by RBT-92's `readout.py` through `readout.sh`. That script
links this ticket's shift and cull arms beside RBT-92's cull20 and baseline digests.
- **Axis:** `mean_lifetime_score`.
- **Windows:** before [T−100, T), transient [T, T+60), recovery [T+60, T+160) primary, tail [T+160, T+200).
- **Readouts:** R-body, R-shift, R-null, recovery time, carriage L/B/S, alive, and the V0–V3 gates.
- **Classes:** E, D, A, C, B, F in that order, with ⌈0.8n⌉/n.
- **Printed lines:** "holds up" (co-evolved R-shift ≥ −r) and the turnover guard (|R-null| < r).

## 9. Resolvable effect size

RBT-92 §8: r is the t(n−1) 95% half-width on RBT-89's SD 0.108 (±40%). That gives **0.077 at ten seeds**,
0.090 at eight and 0.113 at six. Class B needs r ≤ 0.10, so ≥ 8 seeds. The readout prints the realised r.

## 10. Point predictions, with confidence

Every prediction is scored against the readouts above, as its author's (mine).

{{PRED}}

## 11. Falsifier, in the owner's words

**"The designed body wins after the shift": class C.** For C4 in particular it reads "the designed body wins
on open ground". A class-C result would mean the co-evolved bodies' income lead was bought by the clutter, the
designed body is the better forager without it, and the aesthetic bet does not hold on this challenge. **Also
falsified**, on my most exposed claim in §10:
- if `rewire.py` returns RE-WIRED on the holistic fauna **and** the positive control passed at that n. I
  predict NO CHANGE SEEN.
- if flat ground costs the co-evolved body income: co-evolved R-shift in the recovery window < −r. I predict
  it does not (§10).

## 12. Depth

This is RBT-92 §12's statement, and it binds here more tightly because C4 is the one challenge where
adaptation is not excluded by the weight ceiling.
- Before the onset: 2T/60 = 11.3–13.3 events. After it: 6.7–8.7. Transient plus recovery: about 5.3.
- **The report says "survives" or "is sorted" unless `rewire.py` returns RE-WIRED.** Even then it says "posture
  wiring was acquired along descent within about five mutations", not "the population adapted to open ground".
  That stronger sentence would need the link to be shown to carry income, which no readout here measures.

## 13. Per-arm command, sequencing and cost

0. **Before launch** (the coordinator, or me when the gate clears): RBT-92's `onset.txt` must exist, which is
   RBT-92's step 0. Then commit the baseline wiring tables, for each seed:
   `scripts/durable.sh restore runs/RBT-90/forage-SEED rbt-90-SEED && python runs/RBT-101/wiring.py runs/RBT-90/forage-SEED --to runs/RBT-101/base-SEED`.
   The tables are kilobytes, and RBT-92's `base-SEED/bodysig.txt` is made the same way. Then re-run
   `control.py analyse` and confirm `CONTROL n=10 PASS`, which is already committed (§6.4).
1. **Session A, per seed:** `WORKERS=4 runs/RBT-101/run_arm.sh SEED shift`, with
   `DURABLE_WATCH_PID=<pid> scripts/durable.sh every 20 runs/RBT-101/shift-SEED rbt-101-shift-SEED` beside it.
   - At T + 10, about 38 minutes in: `python runs/RBT-92/cull_k.py SEED runs/RBT-101/shift-SEED > runs/RBT-101/cull-k-SEED.txt`, then push.
   - At the end: `python runs/RBT-92/tables.py runs/RBT-101/shift-SEED && python runs/RBT-101/wiring.py runs/RBT-101/shift-SEED`, then push.
2. **Session B, per seed:** pull the k file, then `WORKERS=4 runs/RBT-101/run_arm.sh SEED cull` (label
   `rbt-101-cull-SEED`). Then run `tables.py` and `wiring.py` as above, and push.
3. **After every arm has ended:** `runs/RBT-101/readout.sh > runs/RBT-101/readout.txt` and
   `python runs/RBT-101/rewire.py > runs/RBT-101/rewire.txt`.

**Cost**, at RBT-92 §13's measured ~6 s per season on four cores:

| | |
|---|---|
| arms | 20 (shift and cull × 10) × 600 seasons |
| per arm | 60–70 min |
| total | **about 21 session-hours** |
| wall on 10 sessions | **about 2 h 10 min**: cull starts at T + 10 of shift, about 40 min behind |
| wall on 20 sessions | the same, because cull waits on shift's k |
| cull20 | none; RBT-92's is cited (§7) |

Flat terrain has no obstacle geoms, so a season can only be as fast or faster; I have not measured it at
600 seasons. The throwaway runs ran at about 20 s per season at one worker with two processes on four cores,
the same as plain in the same run (`data/ssc-*/run.log`, not committed).

## 14. What is committed

- **Now:** `PREREGISTRATION.md`; `start_seed_runs.sh`, `start_seed_check.py` and `start_seed_check.txt`;
  `wiring.py`, `rewire.py`, `control.py`, `control/SEED.txt` and `control.txt`; `flat_probe.py` and
  `flat_probe.txt`; `run_arm.sh`, `readout.sh`, `smoke.sh` and `smoke.txt`.
- **Per arm:** RBT-92's set (`config.json`, `seasons.txt`, `lineage-last.txt`, `bodysig.txt`, `events.txt`,
  `event.txt`) plus `wiring.txt`.
- **Per seed:** `cull-k-SEED.txt` and `base-SEED/wiring.txt`.
- **Once:** `readout.txt`, `rewire.txt` and `REPORT.md`.

**Smoke test** (`smoke.sh` → `smoke.txt`): `wiring.py` and `rewire.py` ran end to end on the throwaway
start-seed runs, standing in for all three arms, with read points shrunk. The result was exit 0, V-W PASS, and
C0 identical across arms. The runs were read for nothing and are not committed.

## 15. Carried over from RBT-92: what is settled, and what is pending there

| RBT-92 item | status there (at this writing) | effect here |
|---|---|---|
| ten seeds, t(n−1) r, B needs ≥ 8 | accepted by the coordinator (12:55) | adopted (§4, §9) |
| claim line and §14 quoted verbatim | Amendment 1, PR #76 | C4's quoted here (§2) |
| (1) an extinct fauna's income counts as 0 in every later season and test | **ruled by the coordinator 13:10**, to land in RBT-92's amendment PR | automatic: `readout.sh` calls RBT-92's `readout.py`. `rewire.py` has no income term; an extinct fauna has an empty P(s), prints "extinct", and drops out of that seed's re-wiring contrast (no survivors, nothing to re-wire), with the n printed |
| (2) onset T minimises deaths over [T − 20, T) only; a fixed-T = 370 sensitivity line | **ruled 13:10** | automatic: `run_arm.sh` reads RBT-92's `onset.txt`; whatever sensitivity line RBT-92's readout prints, `readout.sh` prints for C4 |
| (3) V0 also compares `lineage-last.txt` rows that end before T | **ruled 13:10** | automatic, in RBT-92's `readout.py`; `rewire.py`'s own gate already requires C0 identical across arms |
| (4) class B needs ≥ 8 surviving seeds | **ruled 13:10** | adopted (§4, §9) |
| RBT-92 adversary round (`session_011DaJxngAQoRRuQ4wTE11cC`) | not posted at this writing | **I watch RBT-92.** Whatever it forces on the shared instrument I carry here as an amendment, before any C4 arm, and say so on RBT-101 |

## 16. For the adversary: where I am most exposed

1. **The re-wiring statistic was chosen after a development run of its own positive control.** It was run on
   baseline bodies, never an income column, and before any C4 arm. The mean statistics failed the control, and
   the count passed it. That is instrument selection, but it is selection, so attack whether `new`'s 0.5
   threshold, or depth 1 for `new` against depth 2 for g2, is load-bearing.
2. **No sign guard on the re-wiring verdict** (§6.3). Two intervals, shift − base and shift − cull, stand in
   for it.
3. **The control's noise model is between seeds.** I argue it is conservative, but it cannot produce a false
   positive by construction, so the false-positive rate comes from a different model, the half-split.
4. **Structural, not functional.** A link acquired and never used counts as RE-WIRED. The liveness line shows
   how often an installed link is silent on flat ground.
5. **The designed fauna's posture wiring runs through hidden units** (depth ≥ 2), and `new` reads depth 1. The
   designed side can re-wire by reweighting hidden paths without registering in `new`. W-acq(g2) prints that,
   unscored.
6. **cull20 is cited, not re-run.** This rests on the claim that a challenge-free arm is identical across
   challenges. That is true by construction, if RBT-92's cull20 is run on the same head as C4's arms. V0 checks
   the baseline, not cull20 against C4.

## D. Deviations from RBT-89 and from RBT-92

1. **No "survivorship of standing morphology and gait only" sentence**, because C4 is the perceivable challenge
   (§2, §3 of the protocol). A re-wiring readout takes its place.
2. **cull20 cited from RBT-92**, not re-run (§7).
3. **The re-wiring verdict drops the ⌈0.8n⌉ sign guard** (§6.3). The income classes keep it.
