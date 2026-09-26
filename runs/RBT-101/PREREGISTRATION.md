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
| **re-wiring readout** | **`new`**: the fraction of survivors at T + 160 carrying a direct posture link that none of their onset ancestors had. Contrasts are shift − base and shift − cull, and RE-WIRED needs both t(n−1) intervals above 0. **Validated by a positive control on real evolved bodies at the n used** (§6) |
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
part 2 checkpoints' `best_gen0300.json`. The run chose each best by its lifetime score, but no income column is
read here. Readout: `flat_probe.txt`, whose last lines (`flat_probe.py --summary`) give the across-seed figures.

**Probe result** (`flat_probe.txt`, 10/10 seeds; flat minus random, items per 15 s bout, mean over 64 paired
draws):

| | per seed (801 804 805 806 807 1 2 3 4 7) | mean over seeds, 95% t(9) | positive |
|---|---|---|---|
| designed best | +0.52 +0.89 +0.16 +0.89 +1.11 +0.45 +0.45 +0.44 +0.27 +0.55 | **+0.57** [+0.36, +0.79] | 10/10 |
| co-evolved best | +0.41 +0.44 +0.73 +0.06 +0.17 −0.16 +0.20 +0.42 +0.17 +0.02 | **+0.25** [+0.06, +0.43] | 9/10 |
| co-evolved − designed | | **−0.33** [−0.64, −0.01] | negative 9/10 |

- **Open ground helps both bodies alone, and the wheeled designed body about twice as much.**
- **The co-evolved bests do not depend on the furniture for yield.** On 9/10 seeds they eat more without it,
  and "let the furniture stop me" does not carry over from the arena to the foraging economy as a dependence.
- These are solo bests. In the ecology four same-fauna robots share an arena, so §10 discounts the gain.
  The probe enters no verdict.

**Kind: perceivable.** Obstacles reach the brain through `contact`, `height`, `up` and the joint sensors, at
weights the operator reaches.

## 2. Perception, claim line and forbidden readings (verbatim)

`docs/held-out-challenges.md` §2, C4, the perception paragraph and the claim line:

> Perception: obstacles are perceived through `contact`, `height`, `up`, `joint_angle` and
> `joint_velocity`, sensors that evolved bests do wire and do use: RBT-10's 803 season-100 best loses
> 59% of its yield when its height input is blanked; RBT-17's holistic bests carry `height` and
> `joint_angle`; 802's season-590 designed best is a 16 m runaway with every sensor blanked. These
> are one-bit contact and posture readings, expressible at the w ≈ 1 the operator lives at (RBT-62:
> median |w| 0.85–1.13), not a gradient. **C4 is the one challenge the robots can perceive with
> the wiring they have**, so it is a different kind from C1–C3: adaptation *during* the challenge is
> not excluded by the weight ceiling, only by depth (§10). A future arm reports C4 separately from
> the unperceived three and does not pool them.
> 
> **Claim tested:** whether gaits built among clutter hold on open ground, on both bodies, with the
> contest of C1 available if both survive; and, alone in the set, whether anything is re-wired
> during the challenge.

§3, the C4 bullet:

> - **C4 is perceivable**, because contact and posture are one-bit readings at w ≈ 1. It is the one
>   challenge on which "re-adapts" could mean a new use of an existing sensor.

**So C4's pre-registration carries no "survivorship of standing morphology and gait only" sentence.** That
sentence is required of C1–C3. For C4, "re-adapts" *could* mean a new use of an existing sensor, and §6
measures whether it does. The income axis and the falsifier remain claims about realised income. A class-A
result says the co-evolved body earned more on open ground. It does not say the body perceived open ground,
unless §6 returns RE-WIRED as well, and even then only at the depth §12 states.

§14, the readings this protocol forbids, verbatim:

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

### 6.3 Why `new`, and why no sign guard: the candidates, each put through the same positive control

**The history.** I first built the readout on mean statistics (W-acq and W-sort of g2). Before writing any
prediction, I ran their positive control on a development window: C0 at 14, P at 175, on the seven checkpoints
then past 175. They could not see a reflex installed on every holistic survivor. I then tried the count
`new`, which could.

**The committed comparison** (`control_stats.sh` → `control_stats.txt`) re-runs every candidate on the
committed tables at the committed window (§6.4). Detection of RE-WIRED at n = 10, with the reflex installed on
every installable survivor (f = 1.0, w = 1.0), 400 replicates:

| statistic | sign guard | holistic | designed | control |
|---|---|---|---|---|
| W-acq(g2) | on / off | 0.000 / 0.000 | 0.000 / 0.000 | FAIL |
| W-acq(log(1 + g2)) | on | 0.020 | 0.000 | FAIL |
| W-acq(g1) | on / off | 0.033 / 0.072 | 1.000 / 1.000 | FAIL (holistic) |
| **`new`** | on | 0.990 (smallest f ≥ 0.8: 1.0) | 1.000 (0.2) | PASS |
| **`new`** | **off (scored)** | **1.000 (0.5)** | **1.000 (0.1)** | **PASS** |

- **Why the mean statistics fail:** the holistic g2 is heavy-tailed, so a few very large bodies set the mean.
  Its baseline drift, per seed, runs from −2.95 to +6.58 (sd 2.94) against an installed +1.0 (median).
- **Why the count passes:** `new` is a count, so no single body carries it. Its baseline drift is 0.017 to
  0.467 (sd 0.15) holistic and 0.017 to 0.217 (sd 0.063) designed.

**The sign guard (≥ ⌈0.8n⌉/n) is off for this readout, and the sign counts are still printed.** `new` passes
with the guard on as well, but at half the resolution: holistic f 1.0 against 0.5, designed 0.2 against 0.1.
The guard punishes absent substrate: a seed whose fauna carries no posture sensor cannot be re-wired in C4's
sense and reads 0. On seed 807, 12/60 holistic survivors can carry the reflex. The re-wiring verdict instead
needs two intervals to agree, shift − base and shift − cull.

**This choice was made on the baseline's bodies, before any C4 arm existed, and with no income column read. It
is a choice of instrument, not of outcome.** It is still a choice made after looking, and §16 lists it first.

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

`control.txt` prints `CONTROL-FAUNA n=N KIND PASS|FAIL` and the smallest f detected on ≥ 80% of replicates.
`rewire.py` reads that line for each fauna at the realised n. If the control did not pass there, that fauna's
verdict is **UNVALIDATED**, and none of it enters a sentence.

**Liveness, reported and not gated.** RBT-66's frozen-trajectory probe is generalised to any body. It saves
the state, steps 8 ticks with the posture sensors live and again with them zeroed, holding every other sensor,
and takes the peak mean |Δ| over the driven degrees of freedom. It runs in one bout on flat ground, on 3
installable survivors per fauna per seed, with and without the reflex. It shows how often an installed reflex
is also functionally live on open ground. A reflex on a contact sensor that is never touched on flat ground is
present in the wiring and silent in the bout. **"RE-WIRED" means wiring acquired, not wiring shown to be
used**, and the report says so.

**Result** (`control.txt`; 400 replicates per cell; tables `control/SEED.txt`, all ten seeds, C0 alive at 139
and P alive at 300):

| | holistic (co-evolved) | designed |
|---|---|---|
| survivors in P that can carry the reflex | 534/600 (per seed 12 to 60; seed 807 is 12/60) | 600/600 |
| g2 raised by the installed reflex, median | +1.00 at w = 1.0, +0.50 at w = 0.5 | +1.00, +0.50 |
| baseline `new` over C0 → P, no install | mean 0.167, sd 0.152 (0.017 to 0.467) | mean 0.090, sd 0.063 (0.017 to 0.217) |
| **n = 10, w = 1.0: detected at f = 0.3 / 0.5 / 1.0** | 0.037 / **0.978** / **1.000** | f = 0.1: **0.895**; f = 0.2 to 1.0: 1.000 |
| n = 10, w = 0.5: f = 0.5 / 1.0 | 0.287 / 1.000 | f = 0.1 0.378; f = 0.2 1.000 |
| half-split false positives, n = 10 | 5/400 = 0.013 | 6/400 = 0.015 |
| liveness on flat ground (reflex changes the posture response by ≥ 0.01) | 23/30; median 0.002 without, 0.113 with | 22/30; median 0.695 without, 0.705 with |

**`CONTROL n=10 PASS`, and PASS at n = 9, 8 and 7.** At n = 7 to 9 the smallest detected f is 1.0 for the
holistic fauna and 0.2 for the designed. **At n = 6 it FAILS on the holistic fauna** (f = 1.0 detected on
0.797), and passes on the designed. The pass is per fauna (`CONTROL-FAUNA` lines, which `rewire.py` reads).
So a holistic re-wiring verdict needs ≥ 7 seeds. With six the holistic verdict prints UNVALIDATED, which is
stated here before any arm exists.

- **Liveness:** about three in four installed reflexes are live on open ground, on both faunas. The rest sit
  on sensors that read nothing there.
- **The two faunas differ in their own posture response, before any install.** The sampled holistic
  survivors' posture response on open ground is near zero (median 0.002). The designed survivors' is large
  (median 0.695), consistent with §6.1: their posture sensors reach the Effectors through the hidden layer.

### 6.5 The verdict rule (per fauna, on `new` at T + 160)

- **RE-WIRED:** both conditions hold, and the positive control passed at the realised n. The direction is
  reported.
  - new, shift − base: the t(n−1) 95% interval excludes 0;
  - new, shift − cull: the interval excludes 0, with the same sign.
- **SORTED:** wired, shift − base excludes 0, and RE-WIRED does not hold. The survivors' posture wiring moved,
  but not along descent.
- **NO CHANGE SEEN:** otherwise. The half-width and the control's smallest detected f are printed.
- **UNVALIDATED:** the control failed for this fauna at this n. Nothing of that fauna's re-wiring readout
  enters a sentence.

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
- **The readout resolves** at n = 10 an f of about **0.5** of installable survivors on the holistic fauna (**1.0** at n = 7 to 9) and
  **0.1** on the designed (0.2 at n = 7 to 9) (§6.4). **A re-wiring reaching fewer survivors than that is invisible**, and NO
  CHANGE SEEN does not exclude it.
- The natural rate of `new` on the baseline over 161 seasons is 0.167 holistic (sd 0.152) and 0.090 designed (sd 0.063) (`control.txt`, unscored). A
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

**The prior** is the endpoint probe (§1, `flat_probe.txt`). It is solo and on season-300 bests, so it is a
prior and not a measurement of the arm. In it, flat ground raises the designed best's yield more than the
co-evolved best's: designed **+0.57** [+0.36, +0.79] items a bout, positive on 10/10 seeds; co-evolved **+0.25** [+0.06, +0.43], 9/10; the difference **−0.33** [−0.64, −0.01], co-evolved behind on 9/10.

In the ecology each fauna forages in its own arenas, four to a group, so the gain is shared with three rivals
of the same fauna. I take about half of the solo gain to survive into population income. That is a guess,
stated as one.

**Income (RBT-92's readout on this ticket's arms):**

| quantity | point | range I expect | confidence |
|---|---|---|---|
| R-body, before [T−100, T) | +0.12 (RBT-71's 100–599 average, as RBT-92) | | |
| R-body, recovery [T+60, T+160) | **−0.05** | −0.30 to +0.15 per seed | |
| R-shift, recovery, designed | **+0.28** | +0.05 to +0.55 | designed > 0 on ≥ 8/10 seeds, 0.7 |
| R-shift, recovery, co-evolved | **+0.10** | −0.05 to +0.30 | |
| designed R-shift > co-evolved R-shift | | | **0.75** (my most exposed claim, §11) |
| "holds up" (co-evolved R-shift ≥ −r) | | | **0.85** |
| k, per fauna | **0** (median), K1 0–8, K2 0–5 | | k = 0/0 on ≥ 6/10 seeds, 0.55. Flat ground removes an impediment and kills nobody directly |
| recovery time, shift, designed | "none" on ≥ 5/10 | | 0.5. A boon also leaves the pre-event band, and the metric does not know the sign |
| carriage L(T+160), shift − base | within ±0.10 | | 0.65 |
| RBT-92's V3 on the cited cull20 | passes | | 0.85, as RBT-92's |

**Class** (RBT-89 §9, in RBT-92's order):

| B | C | F | A | D or E |
|---|---|---|---|---|
| **0.35** | **0.30** | 0.25 | 0.05 | 0.05 |

- **C is live** because the probe runs the designed side's way on 9/9 seeds. It is not the favourite because
  the group halves the gain, and R-body starts at +0.12.
- **What would embarrass this:** class A, which would mean the evolved gaits used clutter as scaffolding and
  do better still without it. Or co-evolved R-shift < −r, which would mean the gaits were built on the
  furniture ("let the furniture stop me", paper 3) and lose income without it.

**Re-wiring (`rewire.py`, `new` at T + 160):**

| fauna | NO CHANGE SEEN | SORTED | RE-WIRED | FEWER NEW LINKS |
|---|---|---|---|---|
| co-evolved (holistic) | **0.85** | 0.08 | 0.05 | 0.02 |
| designed (conventional) | **0.65** | 0.15 | 0.10 | 0.10 |

- **Point predictions for `new`, shift − base:** holistic **0.00** (−0.10 to +0.10), designed **−0.01**
  (−0.05 to +0.05).
- **Reasons:**
  - Open ground makes the contact and height channels quieter, so if anything the pressure for posture wiring
    relaxes rather than grows.
  - Five reproduction events is shallow.
  - On the holistic fauna the control shows the readout sees an acquired link only near fixation (§6.4).
    So NO CHANGE SEEN there is close to guaranteed unless the link sweeps. That says as much about the
    instrument as about the robots, and the report will say so.
  - The designed fauna is where the readout can see something: a new link on 10–20% of survivors.

## 11. Falsifier, in the owner's words

**"The designed body wins after the shift": class C.** For C4 in particular it reads "the designed body wins
on open ground". A class-C result would mean the co-evolved bodies' income lead was bought by the clutter, the
designed body is the better forager without it, and the aesthetic bet does not hold on this challenge. **My most
exposed claim** (§10), falsified if either holds:
- the co-evolved R-shift ≥ the designed R-shift in the recovery window, with the difference's t(n−1)
  interval above 0. This is the direction the solo probe gives, and it is my claim;
- or flat ground costs the co-evolved body income: co-evolved R-shift < −r.

`rewire.py` returning RE-WIRED on the holistic fauna, with the control passing at that n, would also falsify
my 0.85 on NO CHANGE SEEN.

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
  `wiring.py`, `rewire.py`, `control.py`, `control/SEED.txt` and `control.txt`; `control_stats.sh` and
  `control_stats.txt`; `flat_probe.py` and
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

1. **The re-wiring statistic was chosen after running its own positive control** (§6.3,
   `control_stats.txt`). It was run on baseline bodies, never an income column, and before any C4 arm. The mean
   statistics failed the control, and the count passed it. That is instrument selection, but it is selection,
   so attack whether `new`'s 0.5 threshold, or depth 1 for `new` against depth 2 for g2, is load-bearing.
   The control installs at w = 1.0 and 0.5, so a threshold of 0.5 is reachable by construction at w = 0.5 only
   when the pair had no link before.
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

---

## Amendment 1 (posted before any C4 arm exists): RBT-92's moved instrument carried over

On 2026-09-26 at 13:50 the shared instrument moved: PR #87 merged RBT-92's amendments 1 and 2, including the
coordinator's four 13:10 rulings and the V1 cap fix. It is on integration at `862c7d4`. What changes here:

1. **`run_arm.sh` is now RBT-92's launcher, called and not copied.** It sets `SHIFT=terrain=flat
   OUTROOT=runs/RBT-101` on `runs/RBT-92/run_arm.sh`, which RBT-92's amendment 2 made reusable by siblings.
   The exec'd command is RBT-92's, byte for byte. `cull20` is refused here, because C4 cites RBT-92's (§7).
   I checked this in a scratch copy with a stub `python`:
   - shift → `--shift-at T --shift terrain=flat`;
   - k = 3/0 → `--cull-at T --cull holistic=3,conventional=0`;
   - k = 0/0 → exit 0, no arm run.
2. **k = 0/0 is now RBT-92's rule on the shared instrument**, citing the gap flagged here. RBT-92's launcher
   runs nothing, and RBT-92's `readout.py` reads `cull-k-SEED.txt` and uses the baseline as the null, saying
   R-null = R-shift. **This closes the gap for C4.** My own k = 0/0 staging in `readout.sh` is removed. That
   script now links this ticket's `cull-k-SEED.txt` files into the staged directory, which the moved
   `readout.py` reads for k = 0/0 and for V1. **Without that link, V1 would have failed on every C4 cull
   arm.** `rewire.py`'s own k = 0/0 rule reads the same file and does the same thing.
3. **The 13:10 rulings and the V1 cap fix bind C4 through `readout.sh`**, which calls RBT-92's `readout.py`:
   - an extinct fauna earns 0 in every later season;
   - V0 also compares `lineage-last.txt`;
   - class B needs n ≥ 8;
   - V1 expects min(k, alive).
   The onset rule on [T − 20, T) reaches C4 through `onset.txt`. `rewire.py` imports RBT-92's `Arm`, whose
   extinct-fauna change touches income only; `rewire.py` reads no income.
4. **Smoke test re-run on integration's instrument** (`smoke.sh` → `smoke.txt`). `rewire.py` exits 0 with V-W
   and C0 PASS. `readout.sh` runs RBT-92's `readout.py` on the k = 0/0 path. It prints "cull-k is 0/0: the null
   is the baseline itself" for both seeds, with no V0 failure and no V1 failure on the cull. The only
   validation failures are V1 and V3 on the cull20 stand-in, which carries no cull, so exit 1 there is
   expected.

---

## Amendment 2 (posted before any C4 arm exists): the answer to adversary round 1, and RBT-92's shared fixes

The adversary's round is `runs/RBT-101/adversary/ADVERSARY.md`, merged in PR #101. I re-read every probe it
cites; I did not re-run them. **F1, F2 and F3 are fixed below, F4 is fixed and F6 is stated.** On F5 there is
nothing to do: PASS, re-run by the adversary to the byte.

### F1: a divergence null and a turnover null for the re-wiring readout. Fixed, in three parts, as asked.

1. **Placebo.**
   - `wiring.py` adds `g1_other`: g1 over the non-posture sensors `food`, `agent` and `oscillator`, which flat
     ground gives no posture reason to wire. It also adds `g1_vel` for `velocity`, kept apart, since obstacles
     change it.
   - `rewire.py` counts `new_other` exactly as it counts posture hits.
   - **RE-WIRED now also needs the placebo contrast, (new_existing − new_other) shift − base, with its t(n−1)
     interval above 0.** If the two posture intervals hold and the placebo contrast does not, the verdict is
     **TURNOVER, NOT RE-WIRING**.
   - The install touches only posture links, so the placebo cannot absorb a real re-wiring. The control below
     runs the full rule, placebo included.
   - Caveat, as the adversary says: the placebo tracks posture `new` loosely in the baseline (r +0.12). It is a
     noisy guard, not a perfect one.
2. **Reproduction depth per arm.** `rewire.py` prints the mean fewest-births path from each P(T + 160)
   individual back to C0 (RBT-84's descent rule), per arm, and its shift − base contrast. If the latter exceeds
   ±0.5 event, the verdict line itself carries "reproduction depth moved … so turnover may carry part of it". The
   baseline's own depth over 369 → 530 is **3.83–4.70** holistic and **4.20–4.75** designed per seed
   (`control370.txt`), consistent with the adversary's 4.2–4.6.
3. **cull20 as the divergence null, on every seed.** RBT-92's cull20 is a same-seed, same-T arm that diverges
   with no terrain change. `rewire.py` now reads it as a fourth arm. **RE-WIRED needs new_existing shift −
   cull20 with its interval above 0**, beside shift − base. cull20 − base is printed as the null's own size.
   - This needs `wiring.txt` on each `runs/RBT-92/cull20-SEED`, written while its genomes exist. **I asked for
     that line in RBT-92's post-run step on RBT-92 at 14:10** (`python runs/RBT-101/wiring.py
     runs/RBT-92/cull20-SEED`).
   - If the line is not added, `rewire.py` finds the table missing, reads no seed, and prints nothing that can
     enter a sentence. That is safe but useless, so **it is a launch condition for RBT-92's cull20 arms**, stated
     here and there.

### F2: a new use of an existing sensor, not a grown limb. Fixed.

- The scored statistic is now **new_existing**: a survivor whose g1 is at least 0.5 above every C0
  ancestor's, **and** whose posture-sensor count `ns` is not above every C0 ancestor's.
- **new_grown** (the same gain with `ns` above every ancestor's) and **new_all** are printed, not scored.
- The verdict is about new_existing, the protocol's §3 "new use of an existing sensor". new_grown is a body
  change, and the report may describe it as one but never calls it re-wiring.
- In the onset region, **172/600** holistic survivors at 530 carry more posture sensors than every C0 ancestor,
  against **0/600** designed (`control370.txt`). The adversary's 52/100 among hits was the same fact.

### F3: the two-interval rule collapsed to one on k = 0/0 seeds. Fixed.

The second guard is now **shift − cull20 on every seed**, the same arm everywhere, so it is not a mixture.
shift − cull is still printed. On a k = 0/0 seed it is identical to shift − base, and `rewire.py` says so on
that seed's line. It no longer enters the rule.

### F4: control window and the resolution caveat. Fixed; one step remains at launch.

- **The control is re-run in the onset region**, with the full three-part rule: **T_cal = 370** (C0 alive at
  369, P at 530), the middle of Amendment 2's range [340, 399]. The tables are `control370/SEED.txt`, all ten
  seeds from their `ckpt/rbt-90-SEED` checkpoints, whose commit and season are in each header (nine at
  600/600, seed 2 at 533/600). The analysis is `control370.txt`, and `rewire.py` now reads it.
- **Results, 400 replicates per cell:**

| | holistic | designed |
|---|---|---|
| installable in P | 542/600 | 600/600 |
| baseline new_existing, 369 → 530 | 0.027 (sd 0.042) | 0.058 (sd 0.029) |
| **n = 10, w = 1.0: f = 0.3 / 0.5 / 1.0** | 0.185 / **0.970** / **1.000** | f = 0.1: 0.352; f = 0.2: **1.000** |
| `CONTROL-FAUNA` PASS at n | **10, 9, 8, 7** (6: FAIL, 0.877) | **10, 9, 8, 7, 6** |
| smallest f detected on ≥ 0.8 | 0.5 at n = 9–10; 1.0 at n = 7–8 | 0.2 at every n |
| false positives, full rule, half-split | 0/400 at every n | ≤ 1/400 |
| liveness on flat ground | 19/30 | 23/30 |

  - The resolution at n = 10 matches round 1's (0.5 and 0.1–0.2), under a stricter rule.
  - **The holistic verdict still needs ≥ 7 seeds.**
- **Every verdict line now carries the resolution:** "…; blind below f ~ X of survivors (positive
  control)". **A bare NO CHANGE SEEN is never written**, and it never reads as "did not re-wire".
- **At launch (step 0):** once RBT-92 commits `onset.txt`, `control.py extract` is re-run at the median onset
  of the ten seeds, if that differs from 370, and committed before any arm. `rewire.py` reads that file. The
  checkpoints hold all 600 seasons.
- The round-1 control (T_cal = 140, `control/`, `control.txt`, `control_stats.txt`) stays committed as the
  record of §6.3's choice. It no longer gates anything.

### F6: the probe script. Stated.

`flat_probe.py` is a **re-implementation** of `scripts/forage_probe.py`'s trial, the intact mode only, with the
terrain switched. It is not the script the protocol's §13 names. It is a prior and enters no verdict.

### The verdict rule, as amended (replaces §6.5 and `rewire.py`'s docstring is the executable form)

Per fauna, on **new_existing at T + 160**:
- **RE-WIRED:** all of the following, with the direction reported:
  - shift − base: interval above 0;
  - **shift − cull20**: interval above 0;
  - **the placebo contrast** (new_existing − new_other), shift − base: interval above 0;
  - the fauna's `CONTROL-FAUNA` line PASS at the realised n.
- **TURNOVER, NOT RE-WIRING:** the first two hold, and the placebo contrast does not.
- **FEWER NEW LINKS:** both posture intervals are below 0. This direction is not validated.
- **SORTED:** wired, shift − base excludes 0.
- **NO CHANGE SEEN**, or **UNVALIDATED**.
- A depth caveat is appended when |depth shift − base| > 0.5 event. The resolution is appended always.

### RBT-92's shared fixes, carried

They reach C4 by call, through `readout.sh`, `onset.txt` and `run_arm.sh`:
- the four 13:10 rulings;
- **the 14:12 onset ruling:** Amendment 2's rule reads deaths in [280, 340) only, T is in [340, 399], and a
  seed is flagged if its [T, T+10) deaths exceed its pre-onset mean by half;
- the #87 V1 cap.

RBT-92's round-1 answer is not merged at this writing. The coordinator's 14:20 and 14:35 rulings name what it
carries, and each binds C4 through `readout.py`:
- E2 (co-evolved bankrupt, designed not), which enters the protocol's §9 in its own PR;
- **recovery scored against the control, the paired form primary**;
- **L the only carriage measure**, with B and S dropped or graded;
- the k ≈ 0 caveat: R-null scored on k > 0 seeds only, and cull20's income column as the turnover reference.

Whatever else that answer changes on the shared instrument I will state here as a further amendment before
any C4 arm.

### Predictions restated for the amended readouts (before any arm)

- **Class:**

| B | C | F | A | D | E1 | E2 |
|---|---|---|---|---|---|---|
| 0.35 | 0.30 | 0.25 | 0.05 | 0.02 | 0.02 | 0.01 |

- **Recovery, paired form (arm − base against 0):**
  - designed "none within the window" on ≥ 5/10 seeds, **0.5**. A boon keeps it off the control, and paired
    recovery does not know the sign.
  - co-evolved ≤ 60 seasons on ≥ 6/10, **0.5**.
- **Carriage: L** only, as before. L(T+160) shift − base within ±0.10, **0.65**.
- **R-null:** scored on k > 0 seeds only. I expect k = 0/0 on ≥ 6/10 seeds, **0.55**. Where it is, cull20's
  income column is the turnover reference, and no R-null prediction is scored on that seed.
- **Re-wiring, `new_existing` at T + 160:**

| fauna | NO CHANGE SEEN | SORTED | TURNOVER, NOT RE-WIRING | RE-WIRED | FEWER NEW LINKS |
|---|---|---|---|---|---|
| holistic | **0.85** | 0.05 | 0.05 | 0.03 | 0.02 |
| designed | **0.65** | 0.12 | 0.08 | 0.08 | 0.07 |

  - new_existing, shift − base: holistic **0.00** (−0.04 to +0.04), designed **−0.01** (−0.04 to +0.03).
  - **Depth, shift − base:** **−0.1 event** on both faunas (−0.5 to +0.3). Flat ground is a boon on the probe,
    so I expect slightly fewer deaths and slower turnover. The adversary rightly says nobody has measured this
    direction.
