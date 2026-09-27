# RBT-111 pre-registration: are the arena's stream keys exchangeable?

**Status: designed and not run.** No arm of RBT-111 exists. This file, the scripts and `readout.py` are fixed before any arm launches.

**The gate:**
1. A fresh adversary checks that this implements the ticket's design faithfully and that the power figures re-derive.
2. The coordinator rules.
3. Only then does any arm launch.

The design is the RBT-108 readout adversary's T3 (`runs/RBT-108/readout-adversary/READOUT-ADVERSARY.md` §c), as filed in RBT-111.

**Amendments before any arm.**
- **16 seeds, 217–232, not 12** (coordinator, 2026-09-27 00:50 UTC). The reason was power. Under the design as then filed (the sign-flip test on c0), c0's Holm power at δ = 0.082 was 0.959 / 0.792 / 0.817 at 16 seeds, against 0.617–0.859 at 12. The marginal cost is one runner session.
- **After the design adversary** (PR #262, `runs/RBT-111/adversary/ADVERSARY.md`; coordinator ruling on RBT-111, 01:25 UTC):
  - **c0 is tested by the exact within-seed permutation test** (F2), not the sign-flip test. It is exact whatever the run noise, and more powerful: at δ = 0.082, c0's Holm power is now 0.973 / 0.831 / 0.893 (§6).
  - **drive.sh no longer runs the readout after each slot** (F1). The interval inversion is guarded, so it always terminates.
  - **Durability** is documented and pinned (F6).
  - **NOT A RESULT is on the reading line itself** (F7).
  - **The gen-0 secondary has a stated consequence** (F8).
  - **The salt-1 misread rates are stated** (F9).
- The reading table and the predictions are otherwise unchanged.

## Files by role

| role | path |
|---|---|
| one arm, salts 0/1/2 | `scripts/rbt111_run.sh SEED s0\|s1\|s2 [WORKERS]`: a new script. RBT-96's `scripts/rbt96_run.sh` and `runs/RBT-96/drive.sh` are left byte-identical, so RBT-96 and RBT-108 still re-derive from them. |
| one session's arms, in pair-slots, with durable snapshots and summaries | `runs/RBT-111/drive.sh SEED...` |
| the sessions, slots, checkpoint labels and restore procedure | `runs/RBT-111/waves.txt` |
| readout (pure Python, no package) | `runs/RBT-111/readout.py [--write-summaries \| --from-summaries \| --summaries-only]` |
| power by simulation (numpy, run in the `.[dev]` venv) | `runs/RBT-111/power.py` → `power.txt` (16 seeds, the registered design); `python runs/RBT-111/power.py 10000 12` → `power-12.txt` (12 seeds, for comparison) |
| tests | `tests/test_rbt111.py` |

**What the tests check:**
- **Runner:** `rbt111_run.sh`'s evolve arguments are character-identical to `rbt96_run.sh`'s. Salt 2 parses, and it moves the holistic stream alone.
- **Design:** 16 seeds, 217–232, and `waves.txt` covers exactly those in 4 sessions.
- **The sign-flip test (c12):** it is an exact enumeration, and it reproduces RBT-108's 10/4096.
- **The permutation test (c0):**
  - At n ≤ 5, on data with a one-sided tail, it equals the 6ⁿ brute-force definition to 1e-12.
  - Its count on the design adversary's pinned 16-seed dataset is 150,463/3¹⁶, and its interval there is [+0.019, +0.085].
  - It is invariant to swapping s1 and s2 within a seed, to adding a constant to a seed's three runs, and to reordering the seeds.
  - Its interval is (−∞, +∞) at n ≤ 2 and finite and terminating at n = 3–6 and 16.
- **Holm and the reading table** behave as specified.
- **End to end,** synthetic summaries read as salt 0's offset (with c0 at 1/3¹⁶, and s1 − s0 and s2 − s0 printed beside the reading), as keys not exchangeable, and as chance.
- **The gen-0 secondary:** a generation-0 offset is reported with its consequence and, under "chance", the qualifier.
- **A missing arm** puts "(NOT A RESULT, n = 15 of 16)" on the reading line itself.
- **drive.sh:**
  - its exact per-slot command returns within a timeout on a tree shaped as after slot 2;
  - a full read of that partial tree also returns;
  - the checkpoint label is `rbt-111-ARM-SEED`;
  - the platform file is appended per slot with a UTC timestamp;
  - `waves.txt` gives the restore line.

## 1. Design

- **Seeds: 217–232.** These are sixteen fresh seeds, the next integers after RBT-108's 205–216, not chosen by any property. They are fresh because the offset hypothesis was formed on 205–216.
- **Arms:** each seed runs at `--holistic-stream-salt` 0, 1 and 2 (arms s0, s1, s2), 48 arms in all.
  - The configuration is RBT-96's exactly, which is RBT-85's unprotected arm: 250 generations.
  - The three arms of a seed differ in the salt alone.
  - There is no change to `rabbitstew/`.
- **No seed is dropped, re-run or replaced.** An interrupted arm resumes from its own state. A seed that fails the pairing check is reported and stays in the analysis.
- **Platform:** one platform throughout: x86_64 cloud, Python 3.11, numpy 2.4.6, MuJoCo 3.14.0.
  - Before each slot, `drive.sh` **appends** a platform record to `platform-A-D.txt`, stamped with UTC time and the slot number.
  - A resume on a different machine is therefore recorded, not overwritten.
- **Packing:** 4 sessions × 6 pair-slots (`waves.txt`). Each session runs `runs/RBT-111/drive.sh A B C D` once, at `--workers 2` per arm.
- **Snapshots:** labelled **`rbt-111-ARM-SEED`**, for example `rbt-111-s0-217`. The test suite pins this.
- **After each slot,** `drive.sh` writes that slot's summaries with `readout.py --summaries-only`, which writes and exits without reading: `generations.txt`, `opponent.txt` and `conventional-digest.txt`.
- **Restore** (`waves.txt`):
  1. For each arm without `analysis.json`, run `scripts/durable.sh restore runs/RBT-111/ARM-SEED rbt-111-ARM-SEED`.
  2. Re-run the same `drive.sh A B C D`.
- **Each session** commits its summaries, `config.json` and its platform file on `results/RBT-111-A-D`, and opens one PR.
- **Cost:** about 5–6 h wall for the four sessions together.

## 2. Measure and contrasts

Per run, y is the mean `champ_holistic_mean` over the checkpoints at generation ≥ 200. This is RBT-85's `summary()["final_fifth"]`, the measure RBT-96 and RBT-108 used. Per seed:

- **c0 = (y_s1 + y_s2)/2 − y_s0**: salt 0 against the non-zero salts;
- **c12 = y_s2 − y_s1**: two non-zero salts.

## 3. Tests

- **c0: the exact two-sided within-seed permutation test.**
  - Under key exchangeability, all 3! labellings of a seed's three runs are equally likely, whatever the run noise.
  - c0 depends only on which run carries the s0 label, so the 6¹⁶ labellings give **3¹⁶ = 43,046,721** equally likely values of sum(c0).
  - p is the share whose |sum| reaches the observed |sum|, with a 1e-12 tie tolerance.
  - It is enumerated exactly by meet in the middle: two halves of 3⁸ partial sums, one sorted, bisect. It takes well under a second in pure Python.
- **c12: the exact two-sided sign-flip test**, over all 2¹⁶ = 65,536 sign assignments. Under exchangeability c12 is symmetric about 0 whatever the noise, so this test is exact.
- **Multiplicity:** **Holm** over the two p values at α = 0.05. The smaller p must be ≤ 0.025, and then the larger must be ≤ 0.05.
- **Reported for each contrast:** the mean, median, 20%-trimmed mean (3 cut from each end at n = 16), the count positive, the exact p with its count and denominator (3¹⁶ for c0, 2¹⁶ for c12), and the Holm-adjusted p.
- **The ±0.10 reading is unchanged.** This ticket does not re-estimate h. Until it closes, arena claims cite the registered h = 0.159 (RBT-108), noting that t(16) gives 0.122.

## 4. The reading, fixed now

A contrast "≠ 0" means Holm rejects it at 0.05. A contrast "≈ 0" means Holm does not.

| c0 | c12 | reading |
|---|---|---|
| ≠ 0 | ≈ 0 | **Salt 0's offset.** Search outside the salt code path; every salt-0 run carries that stream family's bias. If c0 < 0, the readout says the sign is the opposite of RBT-108's. |
| any | ≠ 0 | **Keys not exchangeable.** This is the worst case: re-examine every key contrast in the programme (every A/A, RBT-105's replicate histories, possibly seeds). |
| ≈ 0 | ≈ 0 | **Chance at an offset the size of RBT-108's (δ ≈ 0.082).** RBT-108's offset was a post hoc false alarm, and the registered RMS null (h = 0.159) stands. |

- **A null result at δ = 0.05 is NOT DECIDED, not "chance".** The design's power at δ = 0.05 is 0.38–0.62 (c0 by Holm, N81 to N62; 0.53 under T; §6). The chance row is therefore never read as excluding an offset of 0.05, and the readout prints this beside the reading.
- **A qualifier to the chance row, printed by the readout.**
  - c0's 95% interval is got by inverting the permutation test: the shifts μ whose removal from c0 (y_s0 + μ) leaves p > 0.05, walking out from c0's mean in steps of 0.001.
  - If the reading is chance and that interval still contains 0.082, the readout says so: RBT-108's offset is then not excluded by these seeds.
  - The qualifier does not change the reading.
  - The interval is (−∞, +∞) when even the most extreme labelling has p > 0.05 (1/3ⁿ > 0.05, so n ≤ 2). It therefore always terminates.
- **"Salt 0's offset" can be a missed salt-1 or salt-2 excess** (design adversary F9).
  - A salt-1-only excess δ gives c0 = δ/2 > 0 and c12 = −δ. If c12 is missed and c0 rejected, the table reads "salt 0".
  - Under the registered test at 16 seeds this happens with probability **0.020 / 0.051 / 0.061** at δ = 0.082 and **0.060 / 0.060 / 0.075** at δ = 0.05 (N62 / N81 / T, `power.txt`).
  - So beside a "salt 0" reading the readout prints s1 − s0 and s2 − s0, as **description only**. A salt-0 offset predicts both of the same sign and similar size. This does not enter the rule, because adding it now would change the test's size.

**Completion.** If any of the 48 arms is missing or incomplete, the readout prints NOT A RESULT, and the reading line itself reads `3. READING (NOT A RESULT, n = k of 16): …` (F7). A partial read of a running arm is not a result.

## 5. The secondary, and what is only descriptive

**Secondary, stated before any arm:** c0 and c12 on **generation 0's champion row**, the founders.
- It uses the same tests (the permutation test for c0 and the sign-flip test for c12) and a separate Holm.
- The RBT-108 adversary found no offset at generation 0 over RBT-108's 16 seeds (−0.005, 7/16 positive, p = 0.40). This row asks whether that holds on fresh seeds and a third salt.
- **The consequence of a rejection, fixed now** (F8):
  - A generation-0 rejection **does not change the primary reading**.
  - It is reported as **"founders differ by salt"**, and it opens a code-path search at the draw level. Founder differences would contradict the RBT-108 adversary's 300-seed founder check.
  - If the primary reads "chance" while generation 0 rejects, the reading is qualified: **the founders differ by salt, but the final fifth does not.**

**The pairing check, per seed:**
- the three arms' conventional lineage hashes are identical;
- their holistic lineage hashes are pairwise different;
- the terrain and start seeds are identical at every generation.

**Descriptive only.** These are not in Holm, carry no reading, and are not a registered update of h:
- s1 − s0 on the fresh seeds, which is RBT-108's contrast out of sample;
- s2 − s0;
- the RMS of c12.

## 6. Power, re-derived by the designer

**Method** (`runs/RBT-111/power.py`, reproduced in `power.txt`):
- **Outcome model:** one run's outcome is y = e + offset, with e independent per run. The seed's level cancels in both contrasts.
- **Noise models:** the RBT-108 readout adversary's three.
  - N62: normal with SD 0.062;
  - N81: normal with SD 0.081;
  - T: normal with SD 0.040, plus a +0.25 discovery with probability 1/16.
- **Scenarios:**
  - null;
  - a salt-0 deficit, y_s0 − δ;
  - a salt-1-specific offset, y_s1 + δ, which should read "keys".

  δ takes the values 0.05 and 0.082.
- **The simulated test (PERM, registered):** exactly the one registered here: the permutation test on c0 (all 3¹⁶ labellings), the sign-flip test on c12 (all 2¹⁶), Holm, then the reading table.
- **Comparison column (SF):** the design as first filed, with the sign-flip test on c0 too.
- **Trials:** 10,000 per cell, `numpy.random.default_rng(111)`, with the same stream in every cell. The Monte Carlo SE is at most 0.005.
- **Checks before any cell:** the vectorised tests are asserted equal to `readout.sign_flip_p` and `readout.perm_c0_p`, with **identical counts** for the permutation test.
- **Agreement with the design adversary:** their independent code (a different generator seed and a different enumeration) gives PERM 0.972 / 0.829 / 0.887 at δ = 0.082. Mine is 0.973 / 0.831 / 0.893, within Monte Carlo error.

**At 16 seeds, the registered design (PERM)** (`power.txt`):

| scenario | N62 | N81 | T |
|---|---|---|---|
| null: size, c0 (Holm) | 0.027 | 0.027 | 0.028 |
| null: size, c12 (Holm) | 0.027 | 0.027 | 0.025 |
| null: size, c0 (unadjusted) | 0.049 | 0.049 | 0.051 |
| null: size, c12 (unadjusted) | 0.052 | 0.052 | 0.046 |
| null: P(reading = chance) | 0.949 | 0.949 | 0.950 |
| salt-0 δ = 0.082: **power, c0 (Holm)** | **0.973** | **0.831** | **0.893** |
| salt-0 δ = 0.082: P(reading = salt 0) | 0.922 | 0.786 | 0.852 |
| salt-0 δ = 0.05: power, c0 (Holm) | 0.621 | 0.379 | 0.531 |
| salt-0 δ = 0.05: P(reading = salt 0) | 0.586 | 0.357 | 0.505 |
| salt-1 δ = 0.082: power, c12 → "keys" | 0.897 | 0.664 | 0.780 |
| salt-1 δ = 0.082: misread as "salt 0" (F9) | 0.020 | 0.051 | 0.061 |
| salt-1 δ = 0.05: power, c12 → "keys" | 0.451 | 0.267 | 0.423 |
| salt-1 δ = 0.05: misread as "salt 0" (F9) | 0.060 | 0.060 | 0.075 |

**For comparison:**
- **SF at 16 seeds**, the design at the 00:50 amendment: c0's Holm power is 0.959 / 0.792 / 0.817 at δ = 0.082 and 0.572 / 0.347 / 0.491 at δ = 0.05.
- **PERM at 12 seeds** (`power-12.txt`): 0.905 / 0.691 / 0.795 and 0.475 / 0.276 / 0.440.
- **The ticket's figures:** its 0.93 / 0.74 / 0.79 at δ = 0.082 were the RBT-108 adversary's unadjusted t-test at 12 seeds. `power-12.txt` reproduces them: 0.928 / 0.749 / 0.783.
- **An offset of 0.05 is detected less than 2 times in 3** even at 16 seeds under the registered test. That is why a null at δ = 0.05 is NOT DECIDED.

**Validity: resolved, c0 uses the permutation test** (design adversary F2).
- **The problem it resolves:** the sign-flip test on c0 assumes c0 is symmetric about 0 under H0, and it is not when run noise is one-sided. A discovery in s0 moves c0 by −0.25, and one in s1 or s2 by only +0.125.
- **Where the sign-flip test's excess size falls:** under T it lands in **c0 > 0, the direction RBT-108 suggested**. The permutation test is exact overall.
- **Unadjusted c0 rejection under the null, split by c0's sign** (`power.txt`):

  | model | SF: total (c0 > 0 / c0 < 0) | PERM: total (c0 > 0 / c0 < 0) |
  |---|---|---|
  | N62, N81 | 0.050 (0.025 / 0.025) | 0.049 (0.025 / 0.024) |
  | T | **0.057 (0.043 / 0.014)** | 0.051 (0.017 / 0.034) |

  PERM's two tails are not 0.025 each under T, but the test is two-sided and its total is at nominal. So is the reading's false "salt 0" rate: 0.026 under T against SF's 0.029.
- c12 keeps the sign-flip test, which is exact for it.

## 7. The designer's predictions (before any arm)

- **Reading "chance", probability 0.75.** The RBT-108 adversary's code audit (F4) finds salts 0, 1 and 2 to be one code path with different SeedSequence keys. The offset appeared only on the seeds that suggested it, and the 4 earlier seeds show nothing.
- **"Salt 0's offset", 0.15. "Keys not exchangeable", 0.10.**
- **The gen-0 secondary rejects neither contrast, probability 0.9.**
- **c12's RMS lies in [0.07, 0.16], probability 0.8.** This is RBT-108's predicted range for an A/A RMS.

## 8. Not claimed and not changed

- No arm has run, and no RBT-111 output has been read, because none exists.
- RBT-96's and RBT-108's scripts and readouts are unchanged.
- This design does not re-estimate h and does not re-score any verdict.
