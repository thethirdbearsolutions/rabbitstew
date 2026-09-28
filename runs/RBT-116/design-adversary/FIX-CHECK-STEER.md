# RBT-116 `steer.py` FIX-CHECK: PR #434 @ `d276ef6`, trial-merged on integration `42261bd`

**Verdict: MERGE AFTER FIXES. The code is ready; the registration is not.**
- `steer.py`'s fixes are real. S-M1 to S-M3 are closed. The mutants die: 16 of 16 of the original set, including
  the five survivors, and 7 of the 8 new mutants aimed at the fixes. The rotation-invariance check survives a
  module-level monkeypatch. The τ guard works. The full suite passes in a clean venv without scipy.
- **Two MUST items remain, both in the registration text, and both found by running what it now says:**
  - **FC-M1: Amendment 2's G8(f) grid does not steer on the fixture.** 0 of 12 registered variants are called
    STEERS.
  - **FC-M2: W1's eating rule is not reconciled** to root + surface (the 03:10 addendum). And under that rule, the
    one-nose fixture cannot run its decoy on 14–16% of draws.

*Nothing here ran an RBT-116 arm, gate cell or W1 pool draw.* Seasons ran only on the PR's fixture worlds and its
test battery. `theta_refusal.py` builds layouts with W1's layout *parameters* on the PR's *test* seeds, and steps
no season. Probes are under `runs/RBT-116/design-adversary/`.

## The seven checks

| # | check | result | evidence |
|---|---|---|---|
| 1 | every MUST closed; mutants die, including the 3 (5) survivors and a monkeypatch | **PASS, with one SHOULD** | `steer_mutants2.txt`: **23 of 24 killed** on the trial merge. All 16 of `steer_mutants.py` die, including stage1-any, decoy-own-bar, T-against-decoy-field, lesion-not-applied and F_MIN-halved. Of 8 new mutants aimed at the fixes, 7 die: clearance root-only, surface rule ignored, τ guard off, τ guard not called in the season, the fingerprint back to identity, the clear_from/eat_rule check dropped, and the lesion recorder off. **One survives:** dropping the fingerprint's module/qualname clause. Only a patch applied *before* `steer.py` is imported exercises that clause (FC-S2). |
| 2 | both amendments pre-data, each in its own commit before the code, r7 text struck through | **PASS** | `fb2b8ef` (A1 revised) and `177e052` (A2) touch only `PREREGISTRATION.md`, plus A2's two power output files. Both precede `d276ef6` (the code). The superseded τ = 2 s text is kept, struck through (~~…~~), in every place it was changed, and c5fbe93's heading is recorded verbatim. |
| 3 | `power_tau1.txt` reproduces r7 on the current code: 0.847 at K, 0.793 headlined | **PASS** | On the trial merge, `power.py` regenerates `power_tau1.txt` **byte-identically**, and `--tau2-priors` regenerates `power_tau2.txt` byte-identically. `power_tau1.txt` equals r7's committed `power.txt`. The bypass row reads 0.847 (2b) and 0.873 at K / **0.793 headlined** (2c). |
| 4 | the G8(f) rectified build steers on fixtures across the registered grid | **FAIL: FC-M1** | `g8f_grid.txt`, `g8f_sides.txt` |
| 5 | `steer.py` refuses a world whose `smell_tau` ≠ 1.0 | **PASS** | `assert_registered_channel` is called in `run_season` and in `main`. Both of its mutants are killed by `test_a_world_at_another_tau_is_refused`. NIT: it lets `smell_contrast = 0` through, the legacy channel, where τ is moot (FC-S3). |
| 6 | W1's eating rule reconciled to root + surface; priors, fixtures and power inputs checked | **FAIL: FC-M2** | PREREGISTRATION L505 and L819 still read `--eat-from root`, with no `--eat-rule surface` and no explicit `--clear-from`. `theta_refusal.txt`, `g8f_grid.txt` |
| 7 | full suite in a clean `.[dev]` venv without scipy, trial-merged on integration | **PASS** | Fresh venv, `pip install -e .[dev]`, `import scipy` fails. Merge of `origin/results/RBT-116-steer` into `42261bd` (clean). **649 passed**, 16 warnings (RBT-126 breed-rule UserWarnings), 542 s. Integration has since moved to `cad50e8` (#437, #446, #448). `git diff 42261bd cad50e8 -- rabbitstew/` is **empty**, so every probe here stands on the current package code; the suite was not re-run there. |

## MUST

### FC-M1: Amendment 2's G8(f) grid cannot build a one-nose steerer on the fixture

Amendment 2 registers:
- a rectified (`relu`) unit fed by the reading at input −g, g ∈ {32, 128};
- a turn command ±w, w ∈ {4, 16, 64}, to the Effectors on **one side** of the heading;
- best of 12 by F.

`g8f_grid.txt` runs that grid on the PR's own `ONE_NOSE_WORLD` fixture, now at τ = 1 s, with the full 4 + 16 + 16
battery (a Pioneer host, the nose on the left wheel, one side = the left drive Effector):

| grid | STEERS | F (stage 2) |
|---|---|---|
| Amendment 2's 12 variants, one side | **0 of 12** | −0.94 to +0.06 |

`g8f_sides.txt` runs the same rectified unit to **both** drive Effectors, at τ = 1 s:

| w (input −128 unless stated) | call | F |
|---|---|---|
| **2** (the PR's test plant; not in the grid) | **STEERS** | +3.31 |
| 4, 16, 64 | NONE | +3.75, +3.13, +3.00 |
| −4, −16 | NONE | −1.06, −1.56 |
| input −32, w 4 and 16 | NONE | +3.94, +3.00 |

**What this shows:**
- My S-M4 evidence steered only with **both** wheels (`g8f_probe.txt`), and Amendment 2 moved the output to one
  side. One side does not steer here.
- Driving both wheels, every w in the registered grid earns F of +3 or more, but is not called STEERS. Only w = 2,
  outside the grid, is. I did not isolate which condition fails at w ≥ 4 (the ΔT bound or the confirmation) within
  the time.
- So as registered, G8(f) measures SENS_1 ≈ 0 on a body that plainly steers by smell, and the holistic power collapses.
- A2 already requires `gate.py`'s planter to be shown to steer on the fixture before any gate cell. That requirement
  would now block the gate, correctly, but the grid itself needs fixing first.

**Fix:** Amendment 3 (pre-data), with the grid chosen from fixture probes only:
- the output goes to both drive-side Effectors (or to "one side, and the other side at the opposite sign");
- w includes the low gains (for example w ∈ {1, 2, 4});
- a test in this PR, or in `gate.py`'s, shows that the registered grid's best-by-F variant is called STEERS on the
  fixture;
- find out why F ≈ +3 plants at w ≥ 4 are NONE, and state it. If it is the ΔT bound, that is worth knowing for G8(c)
  too.

### FC-M2: W1's eating rule is not reconciled, and the fixtures never test it

**The text.** §4.1's W1 block (L505) reads `--eat-radius 0.35 --eat-from root`, and the fairness row (L819)
reads `--eat-from root`. There is no `--eat-rule surface` (the 03:10 addendum) and no explicit `--clear-from`, whose
code default is `root`. The surface clearance marker applies only under `clear_from=geoms`, so W1 must name both. The
fix is a pre-data reconciliation that sets `--eat-from root --eat-rule surface --clear-from geoms` explicitly.

**What depends on it.** Every fixture in `tests/test_rbt116_steer.py` uses the defaults (`eat_from=any`, `centre`,
`clear_from=root`). So does every probe behind the priors and the G8(f) grid: `g8f_probe`, `tau_probe`, `r5_probe`
(a point mouth, centre rule). None ran under W1's rule. Under it:
- **The one-nose fixture cannot run its decoy on some draws.** `theta_refusal.txt` (layout geometry only) shows that
  under `surface` (and under `geoms`) `draw_theta` finds **no clear θ** on 14–16% of the fixture's draws, for the
  Pioneer and the RBT-113 finals alike. So `call_genome` raises. `g8f_grid.txt` shows every W1-eat variant
  **θ-REFUSED**.
- **With W1's own layout parameters** (12 items, 2 patches, a 4 m disc, start 1.5–2.5 m, on test seeds), refusals
  are **0 of 612 draws** under all three rules, with about 0.2 re-draws. So W1 itself is not at risk. But denser
  world points (RBT-129's sweep) and the fixtures are.
- **The priors** (SENS_C_TWO and SENS_C_ONE in `power.py`) come from a centre-rule point mouth. Under surface eating
  the root's mouth is its geom surface plus 0.35 m, which changes income and F. They remain priors, and are
  gate-measured, but this should be stated.

**Fix:**
- Reconcile the W1 block and the fairness row (pre-data, struck through).
- Add a `W1_EAT` fixture variant, `eat_from=root, eat_rule=surface, clear_from=geoms`, on a layout where θ is
  available, and run the planted positives and negatives, and G8(f) (FC-M1), on it.
- Have `steer.py` refuse a world point whose eating rule is not the registered one, as it now does for τ.

## SHOULD

- **FC-S1: θ refusal is fatal and body-dependent.** A draw with no clear θ raises inside `call_genome`, so one bad
  draw loses the whole genome's call. Which draws refuse depends on the body (its geoms and surfaces). `screen_draws`
  runs intact only, so it cannot catch this. Either:
  - screen θ-availability per host as well (a draw is admissible only if θ exists for every screened host);
  - or have `call_genome` record a refused draw as a flagged, excluded pair, with a count, rather than raise.

  W1's geometry shows 0 refusals, so this bites at other world points first.
- **FC-S2:** add a test that imports `steer.py` *after* monkeypatching a layout method, which the surviving mutant
  shows is untested. It is the one path the module/qualname clause exists for.
- **FC-S3:** `assert_registered_channel` passes `smell_contrast = 0`, the legacy intensity. A W1 command line that
  lost `--smell-contrast` would run silently on the wrong channel. Refuse G ≠ the world point's registered G (2.5
  at W1).

## Files

| file | what |
|---|---|
| `steer_mutants2.py` / `.txt` | 24 mutants (16 carried over + 8 new) on the trial merge: 23 killed |
| `g8f_grid.py` / `.txt` | Amendment 2's 12-variant G8(f) grid, τ = 1 fixture, under default and W1 eating |
| `g8f_sides.py` / `.txt` | the same rectified unit to both wheels |
| `theta_refusal.py` / `.txt` | θ availability under root, geoms and surface clearance; fixture and W1-parameter layouts; geometry only |
