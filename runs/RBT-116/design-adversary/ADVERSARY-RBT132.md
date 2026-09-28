# RBT-132 design adversary: PR #459 (`results/RBT-116-steer` at `fe6d59b`)

*2026-09-28. Target: `runs/RBT-116/RBT132.md`, and the code it adds (`steer.py`'s per-point changes, `planters.py`,
`probe_members.py`, `probe_power.py`). Read beside the RBT-132 ticket, RBT-129 `DESIGN.md` (§5.3(c), §5.5, §6.3),
`LEGS.md` on #455 (B1–B4), RBT-121 `SYNTHESIS.md` (R4, R6) and RBT-125 §B `steps.py`.*

**No-peek.** Nothing here ran on an RBT-129 or RBT-116 point, pool, battery, config, host or arm. The probes use only:
- the RBT-116 and RBT-132 test fixtures;
- RBT-113 O1's committed U finals, walked in sorted order, not in `planters.py`'s registered permutation, in the
  fixture world;
- the committed `worlds/<id>.config.json` files, read as text and never simulated;
- exact binomial arithmetic.

One probe draws W1's pool keys, but runs only fixture bodies in the fixture world. No Stage P or `ckpt/rbt-129-*`
branch was fetched or read.

## Verdict: **MERGE AFTER FIXES**

- **The hard constraint holds.** I reproduced every piece of it independently (§1).
- **Two MUST findings** need a coordinator ruling before any probe is emitted:
  - **M1:** K3, as registered and as coded, can pass only on confirmed STEERS. This restores "VOID by construction"
    at every point that does not pay.
  - **M2:** the PERCEIVES null question. My recommendation differs from both of the designer's readings.
- **One MUST code finding (M3):** RBT-132's own tests kill only 15 of 43 faults in RBT-132's own code. Most of the
  planted and probe command paths are untested.

## 1. W1 is byte-identical: CONFIRMED

| check | result | evidence |
|---|---|---|
| `tests/test_rbt116_steer.py` has no diff against `ce69f17` | no diff (nor in `power.py`, `rabbitstew/`, `design-adversary/`) | `git diff ce69f17 fe6d59b` |
| tests pass | **57 passed** (42 RBT-116 + 15 RBT-132), clean `.[dev]` venv | — |
| `power.py` regenerates `power_tau1.txt` | **byte-identical**; also `power.txt`, and `--tau2-priors` → `power_tau2.txt` | `cmp` |
| mutant kill-sets | re-run `rbt132_mutants.py` on a clean worktree of `fe6d59b`: output **byte-identical** to the committed `rbt132_mutants.txt`, 16 / 16 and 24 / 24 | `diff` |
| re-pointed anchors | **legitimate**. `no-clearance-redraw` and `surface-rule-ignored` are the same fault on moved lines. `tau-guard-off` sets the whole new condition to `False`, which is a superset of the old fault. `tau-guard-not-called-in-season` deletes the call, as before | read |
| `rbt132_w1_identity.txt` | re-run: **byte-identical**, 672 fields and 2 call records | `diff` |
| paths the identity run does not cover | `screen_draws(W1)` (the new default-season branch), `_job` (old 3-tuple against new 4-tuple, and new 3-tuple) and `main` (stdout and exit code): **all IDENTICAL**, `ce69f17` against now, on a 3 s fixture | `rbt132_w1_identity_extra.py/.txt` |
| `probe_power.py` | regenerates `probe_power.txt` byte for byte | `diff` |

## 2. Findings

### MUST

**M1. K3 cannot pass at a point that does not pay, which is the case RBT-129 M7a registered K3 to make readable.**
- **The registration.** RBT-129 §5.5 K3 reads a plant as seen when it passes the veto, has a ΔT lower bound > 0, and
  is called SMELL-USE or STEERS. It adds that **"F ≥ F_MIN is not required here: … a planted steerer that reads
  SMELL-USE shows the instrument can see steering and the world does not pay it"**.
- **What `steer.py` does.**
  - SMELL-USE is `c1 ∧ c3 ∧ ¬c2`, with `c2 = (lbdT > 0)` (`battery_stats`, `call_genome`), and `c1 = (F ≥ F_MIN ∧
    lbF > 0)`.
  - So "SMELL-USE with a ΔT bound > 0" is **empty by construction**.
  - The only way to be seen is **confirmed STEERS**, which needs `c1`, that is F ≥ F_MIN.
- **Consequence.** `planters.k3_k4` implements the registered sentence literally, and so requires exactly the F ≥ F_MIN
  that K3 says it does not. At any point where a planted steerer's F < 0.25, it reads NONE and is not seen. K3 then
  VOIDs the perception layer, which is M7a's "VOID by construction" again. The "not PAYS, NONE is now readable" cell of
  §6.3 is not readable.
- **Two further ways a plant is not seen:**
  - A behavioural stage-2 pass that the confirmation does not repeat reads NONE, `pass_unconfirmed`, so it is not seen.
    The fixture shows it: RBT-116's two-nose steerer at 2 s has c1, c2 and c3 all True and reads NONE.
  - `rbt132_k3_probe.txt` shows the synthetic cases and the fixture case.
- **K3's power claim needs the same qualification.** `probe_power.py`'s K3 false-VOID (0.011 at τ 2 s) is computed
  from the single-battery **PASS** shares, which include F ≥ F_MIN. It holds only where the plants' F clears F_MIN,
  that is roughly where the world pays.
- **Fix (RBT-129's ruling, pre-data; then code and a test here).** Define "seen" on the behavioural legs only: stage 2
  `c3 ∧ c2` (veto and ΔT bound), with the call printed beside it. Optionally require the confirmation to repeat
  `c2 ∧ c3`. Nothing about F. Add a `k3_k4` test with an F < F_MIN record, and one with a `pass_unconfirmed` record.

**M2. The PERCEIVES STEERS clause: the designer's finding reproduces, but the reading is mis-framed, and neither
printed reading should be adopted.** My own code (`rbt132_perceives_null.py/.txt`: scipy, Clopper–Pearson by beta
quantiles, exact sums over both binomials, founders N = evolved N). Null rate is P(clause fires | evolved rate =
founders' rate = ε):

| N | ε | A: plug-in (designer's "registered") | B: CP rate, then 95% quantile (designer's "exact-bound") | C: count > N × CP upper | D: one-sided Fisher exact, 0.05 |
|---|---|---|---|---|---|
| 80 | 0.005 | **0.221** | 0.000 | 0.005 | 0.000 |
| 80 | 0.010 | **0.250** | 0.000 | 0.021 | 0.001 |
| 80 | 0.030 | 0.139 | 0.001 | 0.061 | 0.011 |
| 80 | 0.050 (K5's cap) | 0.118 | 0.003 | 0.067 | 0.022 |
| 160 | 0.005 | **0.251** | 0.000 | 0.022 | 0.001 |
| 160 | 0.050 | 0.129 | 0.006 | 0.080 | 0.028 |

Power at N 80 with the τ 2 s caricature priors, ε 0.005 (for A, B and C, the threshold is what the evolved count must
exceed; at a founders' count of 0 it is 0, 6 and 2.94):

| route, q | A | B | C | D |
|---|---|---|---|---|
| two-nose, 0.10 / 0.25 / 0.50 | 0.79 / 0.98 / 1.00 | 0.05 / 0.63 / 0.99 | 0.55 / 0.96 / 1.00 | 0.21 / 0.85 / 1.00 |
| one-nose, 0.10 / 0.25 / 0.50 | 0.66 / 0.89 / 0.99 | 0.01 / 0.19 / 0.78 | 0.29 / 0.77 / 0.98 | 0.06 / 0.47 / 0.93 |

- **Both of the designer's columns reproduce to the third decimal.** The 22% figure is right at ε 0.005.
- **But "22–25%" is not a general null.** It is the worst case, at ε ≈ 0.005–0.01. At K5's cap it is 0.12–0.13.
- **What the registration text supports.** The clause reads "exceeds the upper 95% binomial bound of **the count
  expected** from the founders' own confirmed false-STEERS rate". Its source is RBT-129 adversary S7 (`ADVERSARY.md`
  §4.2): "PERCEIVES' false-STEERS rate must come from the founders (**a G4-style confirmed rate, with its exact
  bound**)". S7's stated worry was a rate biased toward 0 that "make[s] PERCEIVES easier".
  - In RBT-116 (G4) and RBT-129 (K5), "exact upper bound" always means the Clopper–Pearson bound on the rate.
  - An expected count is a parameter, and a 95% binomial bound on a parameter is a confidence bound.
  - So the most literal single-bound reading is **C**: the evolved count must exceed N × the founders' CP upper rate.
  - **A (plug-in)** is a possible parse of the sentence alone. It contradicts the provenance: a founders' count of 0
    is exactly the "rate biased toward 0" S7 warned about.
  - **B** stacks a confidence bound on a prediction quantile. **No reading of the text gives B.** Its null is about 0,
    and it throws away power: one-nose at q 0.25 is 0.19 against Fisher's 0.47.
- **C is not a 5% test either.** It exceeds 0.05 once ε ≥ 0.03 at N 80, or ε ≥ 0.01 at N 160, and reaches 0.08 at
  K5's cap.
- **Recommendation for the pre-data amendment:** replace the clause with **a one-sided Fisher exact test at α = 0.05
  of the pooled evolved confirmed-STEERS count against the pooled founders' count** (same members per seed). It is
  level at every ε (≤ 0.028), and it is more powerful than B at every row.
  - If the coordinator prefers to keep the sentence, rule it as **C** and print its null beside every call.
  - A is not acceptable: 12–25% of null points pass the clause.
  - The f conditions (BH and mean f ≥ F_MIN) still gate the call, as the designer notes. They limit the damage but do
    not make the clause a test.
- **NIT.** `probe_power.py`'s headline line hardcodes `null 0.22` and `null 0.00` as literals, and prints them at
  N 160 too, where A's null is 0.25. Compute them.

**M3. RBT-132's own tests kill 15 of 43 faults in RBT-132's own code** (`rbt132_new_mutants.py/.txt`).
- **Harness soundness.** An unmutated control copy passes all 57 tests; each mutant is one textual fault; the harness
  uses hard-linked private trees.
- **Killed (15).** The τ registry and its guard, the screen's default season, the fair check, the pool keys, the
  motors-off body, G8(b)'s `abs`, `tune`'s argmax, K4 including (b), `power_line`, and the member draw.
- **Survived (28).** Grouped by whether the fault would pass silently:

| group | survivors | silent? |
|---|---|---|
| per-point call path | `_job-ignores-point`, `cli-drops-world-in-tasks`, `cli-channel-check-at-W1`, `planted-calls-at-W1`, `probe-at-W1` | **loud** at G points (τ refused). **Silent** at L points, where it is harmless: the season does not depend on the point |
| fair marker | `cli-fair-check-dropped`, `planted-fair-check-dropped`, `probe-fair-check-dropped` | **silent**: a non-`--fair` config runs |
| G8(a) | `compass-sign-inverted`, `compass-probes-need-not-agree`, `rung-a-8` | **silent**: every (a) plant anti-steers or is mis-signed; K3 loses its (a) half |
| G8(b) | `b-no-threshold`, `b-nose-on-root` (against M5's non-root rule) | **silent** |
| G8(c) | `c-multi-instance-noses`, `c-straddling-effectors-wired`, `c-noses-same-sign` (no longer a difference unit), `c-w-doubled` | **silent** |
| tuning | `tune-on-draws-5-8` (tuning draws move into stage 2: selection bias in K3 and K4), `host-perm-no-fauna-term` | **silent** |
| K3 | `k3-lbdT-ignored`, `k3-veto-ignored`, `k3-threshold-3` | **silent**, and K3 decides VOID |
| planted command | `planted-screen-hosts-a-only`, `planted-no-refusal-when-short` (runs with fewer than 8 hosts) | **silent** |
| probe command | `missing-below-1`, `f-on-stage1`, `f-on-4-draws`, `rng-offset` (a different RNG than 129300 + j) | **silent** |

- **Fix.** Add an end-to-end fixture test of `planted()` and `probe()`:
  - a fixture HOSTS_ROOT built from committed RBT-19 bodies;
  - a fixture config carrying the fair marker, at a registered point name. Or add a test-only point, so no RBT-129
    pool season runs.
  - Assert the host counts, the refusal paths, the screen's host list, the per-plant keys and the calls' τ.
- **Unit tests for the rest:**
  - `compass_sign` on a body whose direction is known;
  - `plant_b`'s wiring (the relu bias −q, the nose on the LEFT wheel);
  - `plant_c`'s ± inputs and one-sided effectors;
  - `k3_k4`'s veto, ΔT and ≥ 4 bars;
  - `probe_members`' N_F, stage-2 draws, N_MIN and RNG.
- **Re-run `rbt132_new_mutants.py`** against the added tests. Every silent survivor should die.

### SHOULD

**S1. The registry pins the smell and eating block, not the world, so a mismatched point slips through**
(`rbt132_registry_probe.txt`).
- All 18 rows equal their committed configs as `SimConfig` parses them. This is also the designer's test, and it
  passes.
- Of the 306 (config of A, run as point B) pairs, **144 pass all three guards**: every G config is accepted as any
  other G point, and every L config as any other L point. All 144 pairs run a different world (layout, clutter)
  under B's pool key and label.
- The emitted templates derive the config from `{point}`, so the risk is a hand-run or a template edit.
- **Fix:** register a hash of each point's committed `sim` block (or at least its layout and clutter fields). Check it
  in `planted`, `probe` and the CLI.
- **NIT.** The raw JSON omits `smell_contrast` and `smell_tau` at L points, and `clear_from` everywhere, so the rows
  are the code's defaults. They are right, but "each row is what the committed config holds" should say "as
  `SimConfig` reads it".
- **Unregistered points are refused.** For example, `c0-p010-U-G` raises KeyError, and W1 claimed on a τ 2 config is
  refused. Good.

**S2. `probe_members.members` reads `final/` for every season ≠ 0, and does not know about EXTINCT.**
- A probe line for season 60, or for any stale run, silently probes the final population.
- **LEGS.md (#455, fix1b note):** "a unit with `EXTINCT.txt` has no season-300 S and must be skipped (and reported as
  extinct pre-merge, per DESIGN M2), never probed". Today such a unit reads MISSING for both faunas, which is a
  different reading.
- **Fix:** refuse unless `season` equals the run's last completed season (from `history.json`, or the ecology
  config's `seasons`). Write `EXTINCT` (not MISSING) when `EXTINCT.txt` exists.
- **Add as launcher change (iv)** for RBT-129: `probe_jobs` skips EXTINCT units.

**S3. `k3_k4` drops K4's "intact − decoy CI covers 0" clause without saying so.**
- For (d), (e) and motors-off the clause is vacuous: their trajectories are identical.
- For (b) it contradicts itself. A paying kinesis plant (F ≥ 0.25, the only case where K4's (b) test is live) has a
  CI that excludes 0, so the clause would VOID the point exactly when (b) is informative.
- Dropping it is the right call, but it is a change to RBT-129 §5.5. State it in RBT132.md §3 and put it in the
  ruling.

**S4. G8(c) runs on a narrow, body-selected minority of holistic hosts** (`rbt132_host_carry.txt`).
- In the fixture world, **20 of RBT-113 O1's 120 holistic U finals** carry G8(c):
  - 76 have fewer than 2 single-instance Nodes;
  - 19 do not move 5 cm;
  - 5 fail the two-sided layout.
- Carriage is a property of the body, consistent over 3 draws. All 120 designed finals can carry the motif.
- Eight hosts are available, but holistic PAYS and K3's (c) half are measured on about 17% of the holistic pool,
  selected by body plan. R5's single-instance restriction is a narrowing of RBT-116's G8(c), which says "distinct
  Nodes".
- **Fix:** print the carrying share per point beside holistic PAYS. Put R5 in the ruling as a change to G8(c). Word
  holistic PAYS as "on holistic hosts with two single-instance noses".

**S5. The rung for G8(c) is undefined, and taken per link.**
- RBT-116 registers (c) at w ∈ {4, 16, 64}. RBT-129 fixes "a = 6", a quantity defined for the two-link compass
  (a = 2w).
- The design takes w = 3 per output link. G8(c) has as many links as it has one-sided Effectors, so its total gain,
  and its nose step (+0.4 per link), are both larger than the compass's. The design says so for the step, but not
  for the rung.
- **Fix:** rule on per-link w = 3, or a total gain of 6 split over the links. Print the link count per host, as
  §4 already proposes.

**S6. G8(b)'s grid is 16, and RBT-116 registers 8.**
- RBT-116 G8 registers threshold × gain × **turn sign**, with the throttle fixed to **slow** above the threshold.
- `planters.B_GRID` also tunes the brake's sign s_B, so half the variants speed up above the threshold.
- **Fix:** fix s_B to the slowing sign, which gives 8 variants, or argue in the ruling why "speed up near food" is
  still the registered plant.
- Either way, the survival of `b-no-threshold` and `b-nose-on-root` (M3) means nothing tests the wiring.

**S7. §4, the holistic nose step. It is honest, but three things need fixing before it is ruled:**
- **(a) Arm count.** The arm table lists 5 arms (c0, c3, c3.4, speed@c0, speed@c3), but the cost counts 7. Reconcile
  them.
- **(b) The rules.**
  - The R4 test (COMPARABLE or NOSE) matches RBT-121 R4's text: "a nose step pays at least comparably to a speed
    step". It is not "beats", so it is not stricter than the designed leg. Good.
  - RBT-121 **R6** is *operator* parity: "state whether a comparison is made at the default operators or at matched
    erosion". The design's "R6 (parity)" row is measurement parity, which is fine to have, but R6 itself is not
    answered. State that both faunas' hosts come from O1 at the default operators.
- **(c) The holistic F statistic is not defined.** "F with a lower bound > 0" over 8 hosts could be the mean of the
  per-host stage-2 F with a t bound over hosts, or pooled draws. Say which. Also give the `pays` template that
  `stages.py pays_jobs` needs for the holistic plant: RBT132.md gives only `--planted-cmd` and `--steer-cmd`.
- **The fallback is labelled honestly.** "information only; no speed comparison" says what it cannot show. It should
  also say that it cannot exclude a blind-motion premium, so it cannot enter any §8 statement that needs R4.

**S8. Launcher change (ii), the pins, names the wrong files.**
- `planters.py` imports **no RBT-103 file**. It re-implements RBT-103's `direction_bout`. I checked it line for line
  against `routed_populations.direction_bout` and `steps.py`'s signing: the same probes, pooled sums and agreement
  rule.
- The real import chain is:
  - `steer.py`, `planters.py`, `probe_members.py`;
  - RBT-97's `routed_p801.py`, `g500_direction.py`, `mechanism.py`, `resign_rbt67.py`;
  - through `mechanism.py`, `scripts/compass_*.py`, which #455's pinned `scripts/` tree covers.
- `probe_power.json` is read at run time by `power_line`. Pin it too, or build the line from `probe_power.py`.
- (For #455, not this PR: `PRIZE_TOOLS` omits `mechanism.py` and `resign_rbt67.py` from the same chain.)

### NIT

- **`planters.py`'s docstring:** `default_rng([129, 132])`. The code, and RBT132.md, use `[129, 132, fauna]`.
- **R3.** "pays-steps' own designed hosts": this is the same pool (O1 U finals), not the same hosts. `steps.py` draws
  15 with `default_rng(125)`.
- **`draw_members` reseeds `default_rng(RNG)` for each fauna.** With equal pool sizes, both faunas get the same index
  set. This is harmless, but deliberate is better: use `default_rng([RNG, fauna])`, or say so.
- **`_probe` recomputes f** from 8 intact and 8 decoy seasons that `call_genome` runs again on the same stage-2
  draws. That is about 16 extra seasons per member; the f values are in the call record.

## 3. The readings R1–R8

| # | verdict |
|---|---|
| R1 | **accept.** W1 is the default everywhere; §1 shows it is inert at W1 |
| R2 | **accept.** It is the safer failure |
| R3 | **accept**, with S4 (a selected minority for (c)) and the NIT. O1 finals are committed, restorable, and outside Stage P's no-peek, and they decouple the controls from the probed population |
| R4 | **accept.** The tuning draws are the first 4 **pool** draws, and stage 1 is the first 4 **admissible** draws. So every tuning draw is in stage 1 or inadmissible, and **never in stage 2 or the confirmation**, where F, ΔT and the veto are read. The tuning's selection cannot bias K3 or K4. (No test pins this: `tune-on-draws-5-8` survives.) |
| R5 | **accept the mechanics** (a Node's sensor sums over its instances), but it is a narrowing of G8(c) and goes in the ruling (S4) |
| R6 | **accept** |
| R7 | **accept.** G8(f) is not in RBT-129's list |
| R8 | **accept.** Note that f and the STEERS call share the stage-2 draws, so PERCEIVES' two conditions are not independent. That is fine for a conjunction, but do not describe them as two independent tests |

## 4. The three launcher changes for RBT-129

- **(i) Order: correct.** `probe_jobs` appends the planted line after the seeds' probe lines, and `probe_members`
  needs the battery. Planted must go first, or the probe step should wait on `battery.json`.
- **(ii) Pins: incomplete** (S8).
- **(iii) Hosts: correct.** `ckpt/rbt-113-O1` restores as `O1/<seed>/U/<kind>/final`, with 120 finals per fauna. I
  checked this from the committed tarball.
- **Add (iv):** skip EXTINCT units and report them (S2).
- **Add (v):** the holistic PAYS `pays` template (S7c).

## 5. What to rule, pre-data (for the coordinator)

1. **K3's "seen"**, on the behavioural legs (M1).
2. **The PERCEIVES STEERS clause** (M2): recommend one-sided Fisher exact at 0.05. The alternative is reading C, with
   its null printed. Not A, and not B.
3. **G8(c)'s rung** (S5), **G8(b)'s grid** (S6), **R5's narrowing** (S4), and **dropping K4's CI clause** (S3).

Then, in code on #459: M3's tests, S1's world pin, and S2's season and EXTINCT checks. None of this touches W1.

## Files

In `runs/RBT-116/design-adversary/`. Each script runs from the repo root on #459's tree; the `.txt` files are their
outputs.
- `rbt132_perceives_null.py/.txt`: M2, independent null rates and power, four readings.
- `rbt132_k3_probe.py/.txt`: M1, synthetic records and the fixture steerer through `k3_k4`.
- `rbt132_new_mutants.py/.txt`: M3, 43 mutants plus a control.
- `rbt132_registry_probe.py/.txt`: S1, the rows against the raw configs, and the 306-pair cross-matrix.
- `rbt132_host_carry.py/.txt`: S4, O1 finals carrying their plants in the fixture world.
- `rbt132_w1_identity_extra.py/.txt`: §1, W1 identity on `screen_draws`, `_job` and `main`.
