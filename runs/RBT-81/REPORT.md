# RBT-81 — steering_gain: the depth-4 path sum and the `|a| > |c|` test, retired

**Delegate report, 2026-09-14.** Branch `results/RBT-81` off the integration head `526ae7c`.
No world, no simulation; no accepted number changed. 206 tests before, **212 after** (six new).

## What changed

**One instrument, in the library, tested.** `rabbitstew.analysis.steering_terms(ph, depth=1,
source="food")` returns, for a Pioneer-shaped body with a nose on both drive wheels:

| field | what | note |
|---|---|---|
| `a`, `c`, `s_left`, `s_right` | the **depth-1** terms: weight on the direct nose→Effector links, `a = (s_L − s_R)/2`, `c = (s_L + s_R)/2` | exact on every brain; a four-link motif at `w` is `a = 2w, c = 0` |
| `balance` | `r = min(|s_L|,|s_R|) / max(|s_L|,|s_R|)` | 1 for a true motif, 0 for a single wired nose; **a number, no threshold** |
| `opposed` | `sign(s_L · s_R)`: −1 opposed, +1 aligned, 0 if a nose is unwired | everything `|a| > |c|` ever measured, named as the sign it is |
| `rho` | spectral radius of the recurrent core (every non-sensor unit) | the path series converges only if `rho < 1` |
| `path` | `(a, c)` of the path sum truncated at `depth` | kept so old readouts can be reproduced and labelled; `a`, `c` never depend on `depth` |

Noses and Effectors are located by which side of the chassis their wheel sits on (as
`drive_effector_units` does), not by Node index. The function sits beside `signed_influence`,
whose docstring now carries the same caution: its depth-4 sum is a bound on nothing where
`rho > 1`, which is every committed best.

**`runs/compass-gain/steering_gain.py`** now calls it. The DIRECT block is the depth-1 term with
`|a|` median/max, both-noses-wired, the opposed-sign count, and the balance median with IQR; the
`a ≥ 16/32/64` counts stay (on `|a|`, as before — RBT-78 §"third convention difference"). The PATH
block is still printed, labelled *"depth 4, linearised; NOT a quantity where rho > 1"*, with
`rho` median, range and the count above 1 beside it. The `|a|>|c|` columns and the
"gradient-dominant … AND" column are gone; `BEST=1` reports opposed-sign pairs, the largest `|a|`
among them and their balance, with the RBT-61/67 payoff points quoted as calibration, not as a
pass mark.

**`runs/RBT-45/motif.py`** lives on PR #5's branch, which is not merged, so it cannot be edited
here. `docs/artifacts/RBT-81/motif.py` is the corrected file and `motif.py.patch` the diff for PR
#5's author: `steering_gain()` becomes a call to the library function returning
`(a, c, r, sign)`, `summarise()` drops `frac_gradient_dominant` and every `_dominant` key and adds
`median_balance_r` and `frac_opposed`, the table replaces the "a≥32 AND gradient-dominant" column
with the balance median and the opposed-sign fraction, and the docstring carries the correction
dated today beside the one dated yesterday. `motif.json` on that branch was produced by the old
version and is left as it is; the file's header says so.

**Round-trip tests**, `tests/test_steering_terms.py`, all on a nosed Pioneer with its links
replaced by hand:

1. antisymmetric motif at `w ∈ {1, 8, 32}` → `a = 2w`, `c = 0`, `r = 1`, sign −1, and the path term
   equals it (no recurrence);
2. the common-mode twin → `a = 0`, `c = 2w`, `r = 1`, sign +1 — the balance alone does not tell a
   compass from a pirouette, the sign does;
3. a single wired nose → `|a| = |c|`, `r = 0`, sign 0;
4. `s_L = +100, s_R = −0.001` → the old filter passes it, `r = 1e-5`; and on 10,000 random pairs
   `(|a| > |c|) == (s_L·s_R < 0)` exactly;
5. the motif plus a self-loop of −1.83 on the left drive Effector (W4b-801 g490's) → `rho > 1`,
   `a = 16` at `depth ∈ {1, 4, 8, 12}`, the path term at depth 4 equals `w(2 + q + q² + q³)`
   analytically and grows in magnitude from 4 to 8 to 12;
6. `None` without a nose on both wheels; `a = 0` (not `None`) when the noses exist and are unwired.

**Pointers, one line each, beside every downstream quotation found by grep**, none of the
figures rewritten: `runs/compass-gain/REPORT.md` (RBT-62, after the "PATH is an upper bound"
paragraph and after the §3 table), `runs/RBT-78/REPORT.md` (after the gradient-dominant table),
`docs/paper-5-the-blind-forager.md` §6 (the 0.548 sentence), `docs/paper-7-five-instruments.md`
(before "the same thing happened a third time"), `docs/foraging-world.md` (RBT-45's 1.3% crossed
rate, a depth-4 connectivity count), `runs/README.md`, a docstring note in
`runs/compass-gain/check_k_convention.py`, and a note in `runs/RBT-78/reconcile.py`'s docstring
(its code is left as it is: RBT-78 is in review and its readouts must reproduce).
`runs/RBT-45/REPORT.md` is on PR #5's branch, with `motif.py`, so its pointer is not applied
here; the line to add beside its §2 PATH paragraph and its k = 19 rates is given in
`docs/artifacts/RBT-81/README.md` for PR #5's author.

## Before and after on a committed population

`docs/artifacts/RBT-81/steering_gain_P-801_{before,after}.txt`, `runs/RBT-19/P-801`'s final
sixty. No individual there carries a two-nose pair, so every gain is zero in both; the line that
changed is the one that was missing:

```
PATH (depth 4, linearised; NOT a quantity where rho > 1)   rho median 2.23  range [1.12, 3.30]   rho > 1: 60/60
```

Sixty of sixty. The adversary's fourteen bests were not the exception.

## What this does not do

- It does not touch `sensor_influence` (absolute, clipped, depth 4): a connectivity count, which
  the truncation makes a *count at depth 4* rather than a bound. Its docstring already sends any
  question of sign or magnitude elsewhere; noted, not changed.
- It does not change `reconcile.py`'s computation. RBT-78's tables must reproduce from its script
  as posted; the docstring says what the PATH and dominance columns are.
- It does not define what balance is "enough". RBT-78's adversary declined to derive a threshold
  from two linearised payoff points; the ticket says not to, and the payoff curve (RBT-67) was
  measured at `r = 1` only.
- Rule-II line: frame n/a (file analysis); calibration is the round-trip test file, run before
  and after; manipulation n/a; effect: none claimed.

## Files

| file | what |
|---|---|
| `rabbitstew/analysis.py` | `steering_terms` added; `signed_influence` docstring caution |
| `tests/test_steering_terms.py` | the six round-trips |
| `runs/compass-gain/steering_gain.py` | rewritten on the library function |
| `docs/artifacts/RBT-81/motif.py`, `motif.py.patch` | the corrected `runs/RBT-45/motif.py` for PR #5's branch |
| `docs/artifacts/RBT-81/steering_gain_P-801_{before,after}.txt` | the instrument on P-801, both versions |
| eight one-line pointers | listed above |
