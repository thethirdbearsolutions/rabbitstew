# RBT-132 fix-check: PR #459 at `e0f31ec`

*2026-09-28, the design adversary. Checked against:*
- *the coordinator's ruling on #459 (comment 5865175843);*
- *the §12 amendment in RBT-129 `DESIGN.md` (integration `3d7e8be`);*
- *the implementer's summary (comment 5866438429).*

**No-peek held.** Nothing ran on an RBT-129 or RBT-116 point, pool, battery, config, host or arm. I used:
- fixture worlds;
- a test-only point `ADV-G`, registered in-process only;
- committed RBT-19 bodies;
- RBT-113 O1's committed finals, in **sorted** order, not `planters.py`'s registered permutation;
- exact arithmetic.

No `ckpt/rbt-129-*` branch was fetched.

## Verdict: **MERGE AFTER FIXES**, with one pre-launch item for the coordinator

**The code implements every ruled item as ruled.** W1 is byte-identical. The mutant story holds: all 43 of my
original mutants and all 22 of the implementer's re-pointed and new ones die.

**One claimed number is not supported:** "K3 false-VOID 0.000 at τ 1 and 2 s".
- It comes from the kinematic caricature's SEEN shares (1.00 / 0.96).
- On `planters.py`'s own (a) and (c) plants, built on real O1 hosts in two fixture worlds, the SEEN share is
  **0.00–0.12**. At that share K3 false-VOID is about **1.0**.
- The ruling says that a K3 false-VOID above 0.05 at τ 2 s is **reported before launch, not absorbed**. This is that
  report (M1).

## 1. Every ruled item: implemented as ruled

| item | ruled | on `e0f31ec` | verdict |
|---|---|---|---|
| §12.1 K3 SEEN | stage-2 c3 ∧ c2, **and** the confirmation repeats c2 ∧ c3; no F | `planters.seen`: `s2.c3 ∧ s2.c2 ∧ conf.c3 ∧ conf.c2`, where `conf` is the call's own `confirm` or `k3_confirm`. `_call` runs the confirmation for (a) and (c) when stage 2 shows c2 ∧ c3 and the call ran none (for example F < F_MIN). A pass the confirmation drops (`pass_unconfirmed`) still has `rec["confirm"]`, and is SEEN iff that confirmation shows c2 ∧ c3 | **as ruled** |
| §12.2 PERCEIVES | one-sided Fisher exact at 0.05, pooled evolved against pooled founders, same N | `probe_power.reject`: the hypergeometric upper tail at 0.05. Reproduced with scipy's `fisher_exact` (§4) | **as ruled** (the call itself is RBT-129's readout, not in this PR) |
| §12.3 K4 | no CI clause | `k3_k4`: no STEERS among (b), (d), (e) and motors-off; the dropped clause is documented | **as ruled** |
| §12.4 G8(c) | a total a = 6 split over the n links; the step is a total; n printed; the narrowing worded; carrying share printed | `plant_c`: w = a / n over `c_links`. The name carries `c6/n`. §4's nose step is a total of 6 → 6.8 (§B's +0.8 in total). The carrying share is printed in `planted` and `pays` | **as ruled** |
| §12.5 G8(b) | s_B slowing, 8 variants | `B_GRID` has 8 entries; `sB = slowing_sign(backs[0])` from the direction probes. **The physics checks out** (`rbt132_brake_probe.txt`): on 5 of 5 O1 hosts the slowing sign gives a lower speed than the opposite sign, and on 4 of 5 lower than the host alone. Every O1 host tested travels forward, so the backward branch is pinned by the test's constant only | **as ruled** (NIT N2) |
| holistic F | the mean over hosts of per-host stage-2 F, with a one-sided t bound over hosts | `planters.pays`: `_stage2_F` per host on `bat.stage2`, then `np.mean` and `steer.lower_bound` over hosts | **as ruled** (tests thin: S1) |
| S1 hash | sim hash checked in planted, probe and the CLI | `POINT_SIM_HASH` has 18 entries (the test checks each against its committed file). `assert_point_world` is called in `planted`, `pays`, `probe` and `main`. W1 has no entry, so it is a no-op there | **as ruled** |
| S2 | season 0 or the last completed season; EXTINCT, not MISSING | `check_season` against `history.json`: the max season + 1 is 300 for a 300-season run (I checked `Ecology.step` and `_record`: seasons are logged 0…299). `extinct()` looks beside S and in the unit, and `stages.py` writes `<unit>/EXTINCT.txt`. MISSING is now judged on the **living** count before the draw | **as ruled** |
| launcher (iv), (v) | (iv): `probe_jobs` skips EXTINCT units. (v): the pays template | (v) is supplied (`--pays-cmd`). (iv) and (i), the order, are documented in RBT132.md §3 as **RBT-129's `stages.py` changes, not made here**; `stages.py` on this head is unchanged. `probe_members` writes EXTINCT itself if an EXTINCT unit is emitted | **documented, not made** (S2 below) |
| S7 | 5 arms; R6; the F definition; the pays template; the fallback label | 5 arms, 92,160 seasons. R6 is answered (O1, default operators). The fallback is "barred from any §8 statement that needs R4" | **as ruled** |
| S8 | the real import chain pinned, or the line built from `probe_power.py` | `power_line` imports `probe_power.py` and computes the line; no JSON is read (`probe_power.json` is deleted). RBT132.md lists the RBT-97 chain | **as ruled** |
| NITs | all five | the docstring RNG is fixed; R3 is reworded; the shared RNG is documented as deliberate; f is cached and reused (`cached`, keyed by terrain, start and condition); the nulls are computed, not literals | **as ruled** |

## 2. Mutants

- **My 43 mutants, re-run unchanged on `e0f31ec`** (`rbt132_new_mutants_e0f31ec.txt`): **34 killed**. The other 9
  are `BAD-MUTANT`: their anchors moved, and they are exactly the implementer's 9 re-pointed ones. The control passes
  all 70 tests.
- **Every one of the 28 survivors from my first pass now dies** (on the original or the re-pointed anchor), the
  loud-at-G ones included.
- **The implementer's 9 re-pointed and 13 new mutants, re-run by me** (`rbt132_fix_mutants_rerun.txt`): **22 / 22
  killed**, control sound.
- **The re-pointed anchors are legitimate.**
  - Each is the same fault moved to its new line: `k3-lbdT-ignored` and `k3-veto-ignored` now drop `s2.c2` and
    `s2.c3` inside `seen`; `planted-calls-at-W1` drops the point in `_call`; `missing-below-1` sits on the living
    count.
  - Its 13 new mutants are real faults. The exception is `f-not-shared`, which changes only the cost, not a result; its
    test pins the season count, which is fair for a NIT.
- **My further mutants of the ruled code** (`rbt132_fixcheck_mutants.txt`): **8 of 17 killed.** The 9 survivors:

| survivor | real? |
|---|---|
| `pays-refusal-when-short-off` | **yes, silent**: holistic PAYS runs on fewer than 8 hosts |
| `pays-sim-hash-dropped` | **yes, silent**: another cell's config passes `pays` |
| `pays-F-on-confirm-draws` | **yes, silent**, a registration deviation: F is read on the confirmation draws, not stage 2. It is unbiased, but not what the ruling says |
| `pays-gate-failure-ignored` | real, but **loud**: `None.to_dict()` raises |
| `k3-confirm-min-usable-dropped` | edge: `battery_stats` on fewer than 2 usable confirmation draws. Its t bound is undefined, so c2 is almost surely False; not silent in practice |
| `k3-confirm-for-b-too` | equivalent in result (K3 counts only (a) and (c)); cost only |
| `b-sign-from-second-probe` | equivalent: a host is signed only when both probes agree |
| `extinct-only-in-unit` | equivalent: RBT-129 writes the marker in the unit; the check beside S is redundant |
| `cache-ignores-terrain` | near-equivalent: two pool draws sharing a 31-bit start seed |

**The `pays` F leg has one end-to-end test and no refusal tests** (S1 below).

## 3. W1 byte-identity on `e0f31ec`: CONFIRMED (`rbt132_fixcheck_w1.txt`)

- `tests/test_rbt116_steer.py` and `power.py` have no diff against `ce69f17`.
- `power.py` gives `power_tau1.txt` exactly, and `--tau2-priors` gives `power_tau2.txt` exactly.
- `rbt132_w1_identity.py ce69f17` reproduces the committed file byte for byte.
- `rbt132_w1_identity_extra.py` finds `screen_draws(W1)`, `_job` (old and new tuples) and `main` IDENTICAL. The CLI's
  new `assert_point_world` is a no-op at W1.
- `rbt132_mutants.py` gives the committed `rbt132_mutants.txt` exactly (16 / 16 and 24 / 24).
- `probe_power.py` gives the committed `probe_power.txt` exactly.

## 4. The numbers

**PERCEIVES (Fisher): reproduced exactly** (`rbt132_fisher_check.txt`: scipy `fisher_exact`, not `probe_power`'s own
sums).

| | ε 0.005 | 0.01 | 0.03 | 0.05 (K5's cap) | 0.10 | 0.30 |
|---|---|---|---|---|---|---|
| null, N 80 | 0.0000 | 0.0006 | 0.0111 | 0.0216 | **0.0277** | 0.0358 |
| null, N 160 | 0.0006 | 0.0050 | 0.0211 | 0.0276 | **0.0331** | 0.0390 |

- The null stays below 0.05 at every ε, and is ≤ 0.028 within K5's cap at both N.
- Power at τ 2 s, N 80, ε 0.005, q 0.25: **0.853** two-nose and **0.465** one-nose, as claimed.
- At N 160: 0.996 and 0.884.

**K3 false-VOID: the caricature is not a fair stand-in. It is optimistic by about the whole range.**

**The claim.** "0.000 at τ 1 and 2 s" from `k3_seen_probe.txt`. That is the r5 kinematic caricature: an idealised
two-nose steerer at gain 6 (`steer2-k6`) and a one-nose one at gain 32, with 25 genomes. Its SEEN shares are 1.00 and
0.96.

**What I measured** (`rbt132_seen_real.py/.txt`):
- `planters.py`'s own plants: 8 (a) plants (`plant_a`, signed by `compass_sign`) and 8 (c) plants (`c_layout` and
  `plant_c` at a total a = 6 over n, tuned over 2 signs) on RBT-113 O1's committed finals.
- Called through `planters._call` with K3's confirmation, at a test-only τ 2 s point.
- Battery: 4 + 16 + 16 fixture draws.

| fixture world | (a) SEEN | (c) SEEN | confirmed STEERS (a) / (c) | K3 on these 16 | false-VOID at these shares |
|---|---|---|---|---|---|
| short (4 s, 6 items, radius 2) | 0 / 8 | 0 / 8 | 0 / 0 | FAIL (0, 0) | 1.000 |
| long (15 s, 12 items, radius 3) | 1 / 8 | 0 / 8 | 1 / 0 | FAIL (1, 0) | 1.000 |

**It is not a sign error** (`rbt132_seen_signflip.txt`). The same 8 (a) hosts at the opposite sign are worse
everywhere: mean F +0.73 against −0.27, and mean lbdT −0.08 against −0.19. `compass_sign` is right.

**Why SEEN fails.**
- The plants do steer weakly: mean ΔT > 0 on 7 of 8 signed (a) plants, and F > 0 on all 8.
- But the per-plant ΔT lower bound over 16 draws is < 0. So **c2 fails for lack of per-plant power at a = 6**, and the
  veto (c3) passes everywhere.
- This matches RBT-121 R4's evidence: "a one-σ nose step pays 0–10%".
- The caricature has no body, no terrain and no motor noise, which is why its ΔT bound clears.

**How much it could matter** (`k3_false_void` at a common SEEN share p, 8 + 8 plants):

| p | 1.0 | 0.6 | 0.5 | 0.4 | 0.3 | 0.25 | 0.2 | 0.1 | (c) at 0 |
|---|---|---|---|---|---|---|---|---|---|
| false-VOID | 0.000 | 0.002 | 0.016 | **0.079** | 0.268 | 0.428 | 0.617 | 0.936 | **1.000** |

- K3 stays under 0.05 only if the real SEEN share is about 0.45 or more for both kinds.
- The fixture shares are 0–0.12. The (c) share is 0 in both worlds, and K3 needs at least one (c) plant seen, so any
  point where (c) is 0 is VOID with certainty.
- **Caveats, which cut toward the sweep being better, but not by 4×:**
  - these are fixture worlds: flat, uniform food, not `--fair`, unscreened draws;
  - the sweep's PW and HP layouts may give steeper gradients;
  - the hosts are the first carriers in sorted order, not the registered 8.
- **On this evidence K3 would VOID the perception layer at most or all points.** The probe leg would then say nothing
  whatever the evolved members do.

## 5. Findings

### MUST

**M1. K3's false-VOID claim (0.000) rests on the caricature; on real planted hosts it is about 1.0.**
- **Report it before launch,** as the ruling requires. Replace the printed "K3 false-VOID 0.000" with the caveat that
  the caricature is a kinematic idealisation, and print the fixture figure beside it. Not a quiet loosening: that is
  the coordinator's call.
- **Options for the coordinator, pre-data:**
  - **(a) Measure first.** Run the `planted` command at one or two PAYS cells before any probe line. It reads only
    controls, not Stage P members, so K3's real SEEN share is known before the probe leg spends its budget.
  - **(b) Raise the plants' rung for K3 only.** The rung a = 6 was chosen so the world gate and the prize agree, not
    for per-plant ΔT power.
  - **(c) Pool K3's evidence across plants.** For example, the ΔT bound over the pooled 8 (a) + 8 (c) instead of
    per plant. That is a different test, so it needs a ruling.
  - **(d) Accept that the perception layer will mostly read VOID,** and say so in RBT-129 §6.3.
- I recommend (a) now, and (b) or (c) only on its result. None of these is for the implementer to choose.

### SHOULD

**S1. The holistic PAYS F leg (`pays`) is thinly tested.**
- `pays-refusal-when-short-off`, `pays-sim-hash-dropped` and `pays-F-on-confirm-draws` all survive silently.
- **Fix:** add a `pays` refusal test (too few carrying hosts; a foreign sim block) and assert that F is read on
  `bat.stage2`. For example, stub `_pairs` and check the draws it receives.

**S2. Launcher changes (i) order and (iv) EXTINCT are still unmade.**
- As emitted today, every probe line precedes its planted line. `probe_members` then refuses on the missing battery,
  loudly. EXTINCT units are emitted and get written EXTINCT by `probe_members`.
- Both are documented as RBT-129's changes. The ruling listed (iv) under #459's fixes, so **confirm the owner**, and
  make both before `stages.py probes` is emitted.

### NIT

- **N1.** The §12 amendment and the printed line say "null ≤ 0.028 across ε". That is N 80's maximum over a grid up to
  0.10. At N 160 it is 0.033, and it reaches 0.036–0.039 at ε 0.3, though never 0.05. Say "≤ 0.028 at N 80, ≤ 0.033
  at N 160, for ε ≤ 0.10; below 0.05 everywhere".
- **N2.** `slowing_sign` is correct on the 5 O1 hosts tested (all travel forward). The backward branch has no physical
  test, only the constant, and RBT-19's P-801 speeds up under either brake sign. Harmless for O1's hosts; say so.
- **N3.** `k3-confirm-min-usable-dropped` and `cache-ignores-terrain` survive, as expected (§2). No action needed.

## Files

In `runs/RBT-116/design-adversary/`, run on the `e0f31ec` tree:

| file | what |
|---|---|
| `rbt132_seen_real.py/.txt` | K3 SEEN on real plants (M1) |
| `rbt132_seen_signflip.py/.txt` | the sign check |
| `rbt132_fisher_check.py/.txt` | the Fisher null and power, independently |
| `rbt132_fixcheck_mutants.py/.txt` | 17 further mutants |
| `rbt132_fix_mutants_rerun.py/.txt` | the implementer's 22, re-run |
| `rbt132_new_mutants_e0f31ec.txt` | my 43, unchanged |
| `rbt132_brake_probe.py/.txt` | the G8(b) slowing sign |
| `rbt132_fixcheck_w1.txt` | W1 identity |
| `rbt132_fixcheck_suite.txt` | the full suite: **738 passed, 1 skipped**, clean `.[dev]` venv without scipy, as claimed |
