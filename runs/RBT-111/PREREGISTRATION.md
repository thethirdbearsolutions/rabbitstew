# RBT-111 pre-registration: are the arena's stream keys exchangeable?

**Status: designed and not run.** No arm of RBT-111 exists. This file, the scripts and `readout.py` are fixed before any arm launches.

**The gate:**
1. A fresh adversary checks that this implements the ticket's design faithfully and that the power figures re-derive.
2. The coordinator rules.
3. Only then does any arm launch.

The design is the RBT-108 readout adversary's T3 (`runs/RBT-108/readout-adversary/READOUT-ADVERSARY.md` §c), as filed in RBT-111.

## Files by role

| role | path |
|---|---|
| one arm, salts 0/1/2 | `scripts/rbt111_run.sh SEED s0\|s1\|s2 [WORKERS]`: a new script. RBT-96's `scripts/rbt96_run.sh` and `runs/RBT-96/drive.sh` are left byte-identical, so RBT-96 and RBT-108 still re-derive from them. |
| one session's arms, in pair-slots, with durable snapshots and summaries | `runs/RBT-111/drive.sh SEED...` |
| the sessions and slots | `runs/RBT-111/waves.txt` |
| readout (pure Python, no package) | `runs/RBT-111/readout.py [--write-summaries \| --from-summaries]` |
| power by simulation (numpy, run in the `.[dev]` venv) | `runs/RBT-111/power.py` → `power.txt` (12 seeds), `power-16.txt` (16 seeds, for comparison) |
| tests | `tests/test_rbt111.py` |

**What the tests check:**
- `rbt111_run.sh`'s evolve arguments are character-identical to `rbt96_run.sh`'s.
- Salt 2 parses, and it moves the holistic stream alone.
- The sign-flip test is an exact enumeration, and it reproduces RBT-108's 10/4096.
- Holm's step-down and the reading table behave as specified.
- End to end, synthetic summaries read as salt 0's offset, as keys not exchangeable, and as chance.
- A missing arm prints NOT A RESULT.

## 1. Design

- **Seeds: 217–228.** These are twelve fresh seeds, the next integers after RBT-108's 205–216, not chosen by any property. They are fresh because the offset hypothesis was formed on 205–216.
- **Arms:** each seed runs at `--holistic-stream-salt` 0, 1 and 2 (arms s0, s1, s2), 36 arms in all.
  - The configuration is RBT-96's exactly, which is RBT-85's unprotected arm: 250 generations.
  - The three arms of a seed differ in the salt alone.
  - There is no change to `rabbitstew/`.
- **No seed is dropped, re-run or replaced.** An interrupted arm resumes from its own state. A seed that fails the pairing check is reported and stays in the analysis.
- **Platform:** one platform throughout: x86_64 cloud, Python 3.11, numpy 2.4.6, MuJoCo 3.14.0. `drive.sh` writes `platform-A-D.txt`.
- **Packing:** 3 sessions × 6 pair-slots (`waves.txt`).
  - Each session runs `runs/RBT-111/drive.sh A B C D` once, at `--workers 2` per arm, with snapshots labelled `rbt-111-SEED-ARM`.
  - After each slot, `drive.sh` writes the summaries: `generations.txt`, `opponent.txt` and `conventional-digest.txt`.
  - Each session commits those summaries, `config.json` and its platform file on `results/RBT-111-A-D`, and opens one PR.
  - Estimated cost is about 5–6 h wall for the three sessions together.

## 2. Measure and contrasts

Per run, y is the mean `champ_holistic_mean` over the checkpoints at generation ≥ 200. This is RBT-85's `summary()["final_fifth"]`, the measure RBT-96 and RBT-108 used. Per seed:

- **c0 = (y_s1 + y_s2)/2 − y_s0**: salt 0 against the non-zero salts;
- **c12 = y_s2 − y_s1**: two non-zero salts.

## 3. Test

- **Test:** the exact two-sided **sign-flip test** on the mean of each contrast, enumerating all 2¹² sign assignments. p is the share of assignments whose |sum| reaches the observed |sum|.
- **Multiplicity:** **Holm** over the two contrasts at α = 0.05. The smaller p must be ≤ 0.025, and then the larger must be ≤ 0.05.
- **Reported for each contrast:** the mean, median, 20%-trimmed mean (2 cut from each end at n = 12), the count positive, the exact p with its count, and the Holm-adjusted p.
- **The ±0.10 reading is unchanged.** This ticket does not re-estimate h. Until it closes, arena claims cite the registered h = 0.159 (RBT-108), noting that t(16) gives 0.122.

## 4. The reading, fixed now

A contrast "≠ 0" means Holm rejects it at 0.05. A contrast "≈ 0" means Holm does not.

| c0 | c12 | reading |
|---|---|---|
| ≠ 0 | ≈ 0 | **Salt 0's offset.** Search outside the salt code path; every salt-0 run carries that stream family's bias. If c0 < 0, the readout says the sign is the opposite of RBT-108's. |
| any | ≠ 0 | **Keys not exchangeable.** This is the worst case: re-examine every key contrast in the programme (every A/A, RBT-105's replicate histories, possibly seeds). |
| ≈ 0 | ≈ 0 | **Chance at an offset the size of RBT-108's (δ ≈ 0.082).** RBT-108's offset was a post hoc false alarm, and the registered RMS null (h = 0.159) stands. |

- **A null result at δ = 0.05 is NOT DECIDED, not "chance".** The design's power at δ = 0.05 is 0.25–0.44 (§6). The chance row is therefore never read as excluding an offset of 0.05, and the readout prints this beside the reading.
- **A qualifier to the chance row, printed by the readout.** c0's 95% interval is got by inverting the sign-flip test, walking out from the mean in steps of 0.001. If the reading is chance and that interval still contains 0.082, the readout says so: RBT-108's offset is then not excluded by these seeds. This qualifier does not change the reading.

**Completion.** If any of the 36 arms is missing or incomplete, the readout prints NOT A RESULT. A partial read of a running arm is not a result.

## 5. The secondary, and what is only descriptive

**Secondary, stated before any arm:** c0 and c12 on **generation 0's champion row**, the founders. It uses the same test and a separate Holm. The RBT-108 adversary found no offset at generation 0 over 16 seeds (−0.005, 7/16 positive, p = 0.40). This row asks whether that holds on fresh seeds and a third salt.

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
- **Noise models:** the adversary's three.
  - N62: normal with SD 0.062;
  - N81: normal with SD 0.081;
  - T: normal with SD 0.040, plus a +0.25 discovery with probability 1/16.
- **Scenarios:**
  - null;
  - a salt-0 deficit, y_s0 − δ;
  - a salt-1-specific offset, y_s1 + δ, which should read "keys".

  δ takes the values 0.05 and 0.082.
- **The simulated test:** the one registered here, not a t-test: the exact sign-flip test on both contrasts, Holm, then the reading table.
- **Trials:** 10,000 per cell, `numpy.random.default_rng(111)`, with the same stream in every cell. The Monte Carlo SE is at most 0.005.
- **Check:** the vectorised test is asserted equal to `readout.sign_flip_p`.

**At 12 seeds, the registered design:**

| scenario | N62 | N81 | T |
|---|---|---|---|
| null: size, c0 (Holm) | 0.025 | 0.025 | 0.029 |
| null: size, c12 (Holm) | 0.027 | 0.027 | 0.025 |
| null: P(reading = chance) | 0.949 | 0.949 | 0.948 |
| salt-0 δ = 0.082: **power, c0 (Holm)** | **0.859** | **0.617** | **0.675** |
| salt-0 δ = 0.082: P(reading = salt 0) | 0.811 | 0.580 | 0.638 |
| salt-0 δ = 0.05: power, c0 (Holm) | 0.419 | 0.247 | 0.441 |
| salt-1 δ = 0.082: power, c12 → "keys" | 0.756 | 0.495 | 0.658 |
| salt-1 δ = 0.05: power, c12 → "keys" | 0.320 | 0.191 | 0.372 |

**These are lower than the ticket's figures, and the reason is Holm.**
- The ticket's 0.93 / 0.74 / 0.79 at δ = 0.082 are the adversary's **unadjusted t-test**. `power.txt` reproduces them: 0.928 / 0.749 / 0.783 for the t-test, and 0.926 / 0.748 / 0.777 for the unadjusted sign-flip test.
- **Holm over two contrasts costs about 0.07–0.13 of power.** The registered test's power for c0 at the observed offset is **0.62–0.86**, not 0.74–0.93.
- At 16 seeds (`power-16.txt`, 4,000 trials), the registered test gives 0.960 / 0.796 / 0.816 at δ = 0.082 and 0.36–0.58 at δ = 0.05.
- The ticket fixes 12 seeds, so this design keeps 12. **Whether to widen to 16 seeds (48 arms, 24 slots) is the coordinator's call, and it should be made before any arm.**

**A validity note for the adversary: c0's sign-flip test is exact only for symmetric run noise.**
- Under exchangeable keys, **c12** is symmetric about 0 whatever the noise, so its test is exact.
- **c0 = (e1 + e2)/2 − e0 is symmetric only if e is.** RBT-108's tail is one-sided (discoveries are gains), and a discovery in s0 moves c0 by −0.25 but one in s1 by only +0.125.
- Under model T, c0's unadjusted size is **0.056** at 12 seeds and 0.057 at 16, against 0.049–0.050 for the normal models. That is about 2.7 Monte Carlo SE above 0.05. Its size inside Holm is 0.029.
- An exact alternative exists: the within-seed permutation test over the 3! labellings. It is not substituted here, because the ticket fixes the sign-flip test, but it is named so the adversary and the coordinator can rule on it.

## 7. The designer's predictions (before any arm)

- **Reading "chance", probability 0.75.** The RBT-108 adversary's code audit (F4) finds salts 0, 1 and 2 to be one code path with different SeedSequence keys. The offset appeared only on the seeds that suggested it, and the 4 earlier seeds show nothing.
- **"Salt 0's offset", 0.15. "Keys not exchangeable", 0.10.**
- **The gen-0 secondary rejects neither contrast, probability 0.9.**
- **c12's RMS lies in [0.07, 0.16], probability 0.8.** This is RBT-108's predicted range for an A/A RMS.

## 8. Not claimed and not changed

- No arm has run, and no RBT-111 output has been read, because none exists.
- RBT-96's and RBT-108's scripts and readouts are unchanged.
- This design does not re-estimate h and does not re-score any verdict.
