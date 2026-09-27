# RBT-116 design adversary: re-read of revision 6 (PR #400 @ `1295195`), against R5-1 to R5-5

**Verdict: REGISTER.**
- Both remaining MUST items (R5-1 and R5-2) are closed, and so are the three SHOULD items asked about.
- Two new SHOULD items (R6-1 and R6-2) are wording and readout guards. Neither blocks registration.
- As ruled, REGISTER means the *design* is fit to register. Launch stays gated on the code prerequisites and the
  per-world gate.

*Probe:*
- `r6_attack.py` / `.txt` imports r6's `row()`, `unit()` and `verdict()` unchanged, at r6's registered K = 5 and
  D = 16 prior plateaus (Q_H 0.70, Q_P 0.50), and moves only the holistic rates. 300 readouts per row.
- `r5_attack.py` cannot run on r6 as written, because `unit()` now takes confirmed rates and K. This is its
  equivalent.

## The asked items

| item | question | status | evidence |
|---|---|---|---|
| R5-1 | Is EPS the confirmed rate, unsquared, with the gap-at-cap row < 0.01? | **CLOSED** | `power.py` has no squaring, and every rate is confirmed (`SENS_C_*`, `EPS_C`, `EPS_CAP`). G4 is enlarged to 200 members per fauna and gated on the exact upper 95% bound ≤ 0.05. K is chosen by a registered rule, and K = 5 on the priors. The gap-at-cap row is registered. r6 `power.txt` 2a gives false HOLISTIC 0.007 at K = 5 (600 readouts). `r6_attack.txt` gives **0.013** (300 readouts, SE about 0.007): at the bar, within noise. With N fully purged (0.05 against 0): 0.013. I8 uses the confirmed EPS_0. |
| R5-2 | Is G8(f) the one-nose control, with power at min(SENS)? | **CLOSED** | G8(f) is a one-nose temporal plant on every holistic host: the most-moving Part, 2 signs × 3 gains, best by F. `power.py` uses SENS_C,H = min((c), (f)) = 0.32 on the priors. `r6_attack.txt`, p_H 0.5: SENS_C 0.32 gives HOLISTIC 0.870; 0.20 gives 0.543; 0.10 gives 0.007 (NEITHER 0.780). |
| R5-2 | Is "the stronger no" conditional? | **CLOSED** | It is registered only if the gate's re-run detects a p_H 0.5 bypass at ≥ 0.8 at min(SENS). Otherwise NEITHER names the lone-nose sensitivity limit. The F_MIN exclusion of weak one-nose steering is stated. See R6-2 on *which plateau* that re-run uses. |
| R5-3 | Is G8(b) sign-blind? | **CLOSED** | It is keyed on the magnitude \|reading\|, with the reason stated. |
| R5-4 | Is G8(a)'s bar relative to G1? | **CLOSED** | Pooled confirmed share ≥ 0.6 × c_G1, where c_G1 is recorded at G1's first paying rung. |
| R5-5 | Are both costs registered? | **CLOSED** | `--draws-final K` becomes hook 5 and is tested at G6 beside D ∈ {8, 16}. Both costs are registered for the ruling: **about 510 CPU-h per world point at D = 16, and about 310 under `--draws-final`** (r6 L684; note both are up from r5's 420). The cheapest passing option is the default. |

R5-6 (the operator sentence) and R5-7 (evolved u printed beside the hand-built u_f, with a re-run if they differ by
more than 2×) are also taken in.

## New, both SHOULD

### R6-1: the null is protected up to G4's cap, measured at generation 0. U can drift past it

G4 measures the confirmed false-STEERS rate on **burn-in finals**. U then evolves for 48 generations under real
smell. Members that use smell without steering (SMELL-USE that sometimes clears T) are what U selects and N does not.
So EPS_U can rise during the run, above anything G4 saw. I8 watches N falling; nothing watches U rising.

`r6_attack.txt`, the null (p 0.04 on both bodies), K = 5:

| holistic confirmed EPS, U / N | HOLISTIC | INCONCL: H steers more | NEITHER |
|---|---|---|---|
| 0.005 / 0.005 (r6 null) | 0.000 | 0.000 | 0.897 |
| 0.05 / 0.01 (the cap, registered) | 0.013 | 0.230 | 0.743 |
| **0.08 / 0.01** | **0.353** | 0.550 | 0.097 |
| 0.10 / 0.01 | 0.777 | 0.210 | 0.013 |

This cannot be closed by design: EPS_U is not separately observable in U once real steerers may exist. **The guard is
a registered sensitivity.**
- A HOLISTIC verdict is headlined only if it also holds at **K + 2** (K = 7 on the priors). Checked with r6's
  `row()` (appended to `r6_attack.txt`):

  | K | false HOLISTIC, gap 0.08 / 0.01 | false HOLISTIC, gap 0.10 / 0.01 | detection, p_H 0.5 at SENS_C 0.32 |
  |---|---|---|---|
  | 6 | 0.043 | 0.303 | 0.80 |
  | 7 | **0.000** | 0.093 | **0.79** |

  K = 7 absorbs U rising to 0.08 at almost no power cost, against 0.87 at K = 5.
- A HOLISTIC that fails at K + 2 is headlined as "INCONCLUSIVE: holistic crossing not robust to a rise in U's
  false-positive rate".
- Also print the U − N difference in SMELL-USE share per probe, since SMELL-USE is the population a rising EPS_U
  would come from.
- r6's own table 2a agrees: at K = 7, p_H 0.5 detection is 0.94 at SENS_C 0.48 and 0.75 at 0.32. The remaining
  cost falls on weak one-nose sensitivity (0.06 at SENS_C 0.20), which R6-2's clause already names.

### R6-2: evaluate "the stronger no" at the realised plateau, not the prior 0.70

The ≥ 0.8 detection condition depends as much on the plateau as on SENS. `r6_attack.txt`, p_H 0.5 at SENS_C 0.32:

| plateau Q_H | expected confirmed steerers of 40 | HOLISTIC | NEITHER |
|---|---|---|---|
| 0.70 (D = 16 prior) | 9.0 | 0.870 | 0.000 |
| 0.41 (D = 4 prior, or a higher realised u) | 5.2 | 0.467 | 0.047 |
| 0.21 (holistic at the designed u) | 2.7 | 0.000 | **0.820** |

**The fix:**
- The stronger-no check (and the NEITHER sentence's sensitivity clause) uses the plateau from the **chosen** draws
  option (D, or `--draws-final`), and the **larger** of G6's hand-built u_f and the assay's evolved u (R5-7).
- It is recomputed at readout, when the evolved u exists.
- If it then fails, the NEITHER sentence falls back to naming the sensitivity limit, and states the plateau and SENS
  at which the instrument could see a crossing.
- **This matters most if the ruling picks the cheaper `--draws-final` option,** whose plateaus are unmeasured.

## Kept

Everything R5-CHECK listed as right, plus r6's:
- the registered K rule, and the choice of K by the worst case rather than the point estimate;
- 200-member G4;
- the one-nose control, with power at min(SENS);
- the relative G8(a) bar and the sign-blind G8(b);
- both costs registered.

## Files

| file | what | runtime |
|---|---|---|
| `r6_attack.py` / `.txt` | r6's `row()` / `verdict()` at K = 5: the EPS gap at, and beyond, the cap; one-nose SENS; realised plateaus | about 3 min |
