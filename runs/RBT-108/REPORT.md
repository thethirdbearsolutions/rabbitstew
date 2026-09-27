# RBT-108: the arena's A/A null at n = 16

This report is scored against the RBT-108 pre-registration, the ticket text written before any arm ran. Every number here comes from the committed summaries under `runs/RBT-96/{s0,s1}-SEED/` (`generations.txt`, `opponent.txt`, `conventional-digest.txt`). No arm was run, and no seed was dropped or re-run. The arms themselves are the six runner PRs: #212, #217, #219, #221, #224 and #248.

## Files by role

| role | path |
|---|---|
| launcher (writes the readout) | `runs/RBT-108/readout.sh` |
| extra statistics | `runs/RBT-108/readout.py` (pure Python; its t, χ² and beta quantiles are asserted against tabled values on import) |
| readout | `runs/RBT-108/readout.txt`. Part A is `runs/RBT-96/readout.py --seeds 201,…,216 --from-summaries`, unchanged. Part B is `runs/RBT-108/readout.py`. |

**Re-derivation.** `sh runs/RBT-108/readout.sh` run in a fresh worktree reproduces `readout.txt` byte for byte. The readout is a derivation, not a replay: adding 0.11 to `s1-212`'s last checkpoint moves d(212) from +0.225 to +0.235 and the 12-seed RMS from 0.1097 to 0.1115.

**One caution on part A.** RBT-96's script hard-codes its n = 4 labels ("3 df", "4 df", "a 4-seed mean must clear"), but at `--seeds` ×16 it computes those lines with n = 16. So its "0.0796" is t(4)·RMS/√16. That is **not** the registered h. The registered figures are in part B.

## Registered readouts

**1. Out of sample: the 12 new seeds.** The d values are +0.119, +0.029, +0.152, +0.044, +0.026, +0.027, −0.011, +0.225, −0.017, +0.105, +0.137 and +0.149.
- **RMS d = 0.110**, with a 95% χ² CI (12 df) of **[0.079, 0.181]**.
- The CI contains 0.128, so **RBT-96's null replicates**.

**2. Pooled over 16 seeds.**
- **RMS d = 0.115**, with a χ² CI (16 df) of [0.085, 0.174].
- **h = t(4)·RMS/√4 = 0.159.** RBT-96 had 0.178.
- **Fresh-terrain analogue: not computed.** The champions probe (`runs/RBT-96/adversary/champions.txt`) covers seeds 201–204 only. It was not repeated for 205–216, and no committed file holds a fresh-terrain d for those seeds.
- **Seeds needed for ±0.10 at 95%: 8.** That is the smallest n with t(n−1)·RMS/√n ≤ 0.10, which is RBT-96's convention and gave 9 at 0.128. At the pooled CI's ends the answer is 6 or 15.

**3. The tail.**
- |d| ≥ 0.20 in **1 of 12** new seeds (seed 212, d = +0.225). The Clopper–Pearson 95% interval is **[0.002, 0.385]**. Pooled with RBT-96's four seeds, it is 2 of 16.
- **Seed 212's s1/s0 solo steering is not available.** The summaries do not hold it; RBT-96's adversary measured steering for seed 201 from the bulk.
- What the summaries do hold for seed 212, s0 → s1:
  - holistic solo approach: +0.88 → +1.45 m;
  - holistic terrain success: 0.030 → 0.621;
  - the wheeled opponent is identical in both arms (approach +1.76 m, steering 2.64 of 3).

**4. Pairing check: 12/12 pairs pass** (16/16 with RBT-96's four). In every pair:
- the conventional lineage hashes are identical (5,000 lines each);
- the holistic lineages differ;
- the terrain and start seeds are identical at all 250 generations;
- both arms are complete.

**5. Earlier verdicts against the pooled null.** A verdict clears if its 4-seed mean satisfies |mean| > h = 0.159. No verdict is re-scored here.

| verdict | committed mean | source | verdict by its rule | t(4) vs null | p | against h = 0.159 |
|---|---|---|---|---|---|---|
| RBT-74 | +0.064 | `runs/RBT-74/readout.txt:18` | null | +1.12 | 0.33 | does not clear |
| RBT-85 | −0.0485 | `runs/RBT-85/readout-from-summaries.txt:25` | null | −0.85 | 0.45 | does not clear |
| RBT-94 | none | never run (backlog, coordinator 2026-09-19); `runs/RBT-94/` does not exist | — | — | — | no verdict to re-read |

RBT-94's registered size is 8 seeds. Against this null that would give a 95% half-width of 0.096.

**Registered predictions: 3 of 3 right.**

| prediction | outcome |
|---|---|
| 12-seed RMS in [0.07, 0.16] | 0.110, **right** |
| 1–4 of 12 seeds with \|d\| ≥ 0.20 | 1, **right** |
| pooled n for ±0.10 in [6, 14] | 8, **right** |

## Post hoc diagnostic: not registered, kept separate

The coordinator asked for this after the runners posted d. An A/A contrast should centre on zero.

| set | mean d | 95% t CI | t-test p | signs +/− | exact sign-test p | RMS² = mean² + var |
|---|---|---|---|---|---|---|
| 12 new | **+0.082** | [+0.034, +0.130] | 0.003 | 10 / 2 | 0.039 | 0.0120 = 0.0068 + 0.0053 (56% mean²) |
| all 16 | **+0.073** | [+0.025, +0.122] | 0.006 | 12 / 4 | 0.077 | 0.0131 = 0.0054 + 0.0078 (41% mean²) |
| RBT-96's 4 | +0.047 | [−0.172, +0.266] | 0.54 | 2 / 2 | 1.00 | 0.0164 = 0.0022 + 0.0142 (13% mean²) |

**Across the 12 new seeds and the 16 pooled, the mean is resolved away from 0 by the t CI.** The sign test resolves it at 0.05 on the 12 new seeds (p = 0.039) but not on all 16 (p = 0.077).

The solo measures in `opponent.txt` lean the same way, and this is descriptive only:
- s1's holistic solo approach exceeds s0's in 11/12 new seeds (14/16 overall, sign p = 0.004);
- terrain success is higher in s1 in 8/12 new seeds (10/16 overall), which is not resolved.

**So the salt-0/salt-1 contrast may not be a pure A/A.** If the offset is systematic, RMS d is not a pure null spread:
- A systematic offset adds mean² to RMS², and here the mean² term is 41–56% of RMS².
- "A/A" would then carry a bias: in these seeds the arm label tends to predict the sign of d.
- Without the mean, the pooled spread is 0.088, not 0.115. h would then be 0.126 instead of 0.159, and ±0.10 would need 6 seeds instead of 8.

Neither RBT-74 (+0.064) nor RBT-85 (−0.049) clears either h, so the table in §5 reads the same on both.

**This is a finding for the readout adversary.** Is the offset real? If it is, does it belong to the salt pair (salt 1 against salt 0 as fixed labels) or is it chance? The t-test assumes normality against a tail this ticket exists to measure, and the sign tests are 0.039 and 0.077. The committed files cannot decide it, and **no mechanism is claimed here**. What would decide it is more salts per seed, or arms with swapped salt labels. Either is the coordinator's call.

## Scope

- **Claimed:** the registered readouts above, from the committed summaries, and the post hoc diagnostic as labelled.
- **Not claimed:**
  - a fresh-terrain h;
  - the tail seed's solo steering;
  - any cause for the mean offset;
  - any re-scoring of RBT-74 or RBT-85.
