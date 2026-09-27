# RBT-112 step 3: the pre-arm operator baseline's decision rule, fixed before it runs

*Committed before the S = 0 baseline ran. The only baseline numbers read before this commit are
RBT-106's committed default tables (`runs/RBT-106/baseline/baseline-w32-SEED.txt`), used below to pin
the estimator to the ticket's "u ≈ 0.29".*

## What runs

`runs/RBT-112/baseline.py` is RBT-106's `baseline.py` (w = 32, K = 1), with RBT-104's adversary's
`persistence.lineage()` unchanged. It runs on RBT-106's ten seeds (801, 804, 805, 806, 807, 1, 2, 3, 4, 7).
For each seed there are 30 planted w = 32 founders × 20 lineages = 600, read at depths 0–40. Each lineage
has the same `SeedSequence([104, seed, 1, rep, founder])`. The two arms of the comparison are:

- **default**: part 2's MutationConfig, exactly as RBT-106 ran it;
- **S = 0**: the same MutationConfig with `global_bias_sigma = 0`.

Because the flag leaves the random stream unchanged, each S = 0 lineage is its default twin, draw for
draw. The only difference is that the global units' biases never step. There is no selection and no
crossover. (The baseline never had crossover, so "crossover 0" is the same run, and it is not repeated.)

## Byte-identity precondition

The default run at this branch's code must reproduce RBT-106's committed `baseline-w32-SEED.txt`
below the header line, byte for byte, on all ten seeds. If it does not, the comparison is VOID and
nothing below is read.

## The statistic

- **f(d)** is the pooled pay32 fraction at depth d over the ten seeds (6,000 lineages). It is RBT-106 H's
  criterion `pay32`: the planted structure with its founder's sign, own-link |a| ≥ 12.5236.
- **The primary: u = 1 − f(8)^(1/8)**, the geometric per-generation loss over depths 0–8. f(0) = 1 by
  construction, since every planted founder pays.
  - On the committed default tables this reads **0.282**.
  - The ticket's 0.29 is 1 − f(1) = 0.292.
  - Depth 8 is chosen because it averages the first generations, where the ticket's figure was read, and
    because f(8) is still large enough to estimate (426 of 6,000 at the default).
- **Printed beside it, not decisive:**
  - u at depths 1, 2, 4 and 16, by the same formula;
  - per-seed u(8), with the t(9) interval over seeds;
  - the same estimator on the `same` column (the structure with its sign, any magnitude), which is the
    structure's own decay. On the committed default tables it reads 0.097 at depth 8 (0.083–0.098 over
    depths 1–16). The ticket's "0.07–0.08" came from the w = 1 founders.
  - pay-rung persistence f(d) by depth (0, 1, 2, 4, 8, 12, 16, 25, 40), default against S = 0.

## The rule (the ticket's, verbatim in effect)

| primary u at S = 0 | decision |
|---|---|
| **u ≤ 0.12** | The bias gate is most of the erasure. **The arm is worth running** (still gated on RBT-106 H reading not held, and on the ruling). |
| **u ≥ 0.20** | The flag does not address the erasure. **Stop, and report.** |
| 0.12 < u < 0.20 | **GREY.** Neither branch fires. Report, and the coordinator decides. |

The point estimate decides; the interval is printed and does not decide. If u(1) or u(4) falls on
the other side of a threshold from u(8), both are reported, and u(8) governs.
