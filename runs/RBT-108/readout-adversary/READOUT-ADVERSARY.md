# RBT-108 readout adversary

This report attacks the RBT-108 readout, PR #253 (`results/RBT-108-readout`), against the ticket's binding pre-registration. It then takes up the coordinator's post hoc question: is the salt-0/salt-1 contrast a pure A/A? No arena arm was run. The one simulation is a labelled 1-generation probe (§a), written to scratch.

## Files by role

| role | path | how it was run |
|---|---|---|
| independent re-derivation, exact tests, bootstrap, per-fifth timing, power | `rederive.py` → `rederive.txt` | `python3 runs/RBT-108/readout-adversary/rederive.py`: pure Python with its own parser and quantiles, asserted against tabled t and χ² values; about 40 s |
| code-path probe: stream identity, key collisions, founders at salts 0/1/2, a 1-generation replay | `codepath.py` → `codepath.txt` | `python runs/RBT-108/readout-adversary/codepath.py --probe SCRATCH` in a `.[dev]` venv (numpy 2.4.6, MuJoCo 3.14.0, x86_64); about 1 min |

`rederive.py` was written without reading `runs/RBT-108/readout.py`. It shares only the definition of d: the mean `champ_holistic_mean` over the checkpoints at generation ≥ 200, s1 − s0.

## Findings

| # | severity | one line |
|---|---|---|
| F1 | NONE | The readout reproduces byte for byte, and all five registered items re-derive to the printed digit. |
| F2 | CAVEAT | h uses t(4), the registered convention. The null's own df gives 0.122. The replication criterion accepts any 12-seed RMS in [0.078, 0.179]. |
| F3 | MUST-FIX | The post hoc section understates the evidence. The exact sign-flip test, valid under the heavy tail, gives p = 0.0024 (12 seeds) and 0.0055 (16), not the sign test's 0.039 and 0.077. |
| F4 | NONE (the central answer to a) | Salt 0 is not a different code path. The only difference is the SeedSequence spawn key, (0,) against (0, 1), and forcing salt 0 through the salted branch replays byte for byte. |
| F5 | CAVEAT | The offset is absent at founding (gen 0: −0.005, 7/16 positive) and grows over the run with the spread. |
| F6 | CAVEAT | The solo-approach "11/12" is not independent corroboration: corr(d, approach d) = +0.72. |
| F7 | CAVEAT | Chance or systematic cannot be decided from committed files. The hypothesis was formed on the 12 seeds that test it. A decisive test is designed and costed in §c. |
| F8 | CAVEAT | Keep the registered RMS null. The spread-only null (0.088–0.091) is right only if the offset is real, and it is anti-conservative if the offset is chance. No verdict changes under either. |

### F1. Re-derivation (NONE)

- **Byte for byte.** `sh runs/RBT-108/readout.sh`, run in a fresh worktree of `origin/results/RBT-108-readout`, writes `readout.txt` with sha256 `c5d2dbc9b22d…`, identical to the committed file. `runs/RBT-96/` on that branch is identical to integration.
- **The items, re-derived independently** (`rederive.txt`, "registered items"):
  1. The 12 new seeds give RMS **0.1097**, with χ²(12) CI **[0.0787, 0.1812]**. The CI contains 0.128, so the null replicates.
  2. The 16 pooled seeds give RMS **0.1146**, with χ²(16) CI [0.0854, 0.1744]. **h = 0.1591**, and **8 seeds** give ±0.10 (6 or 15 at the CI's ends).
  3. The tail is **1/12**, seed 212. Clopper–Pearson gives **[0.0021, 0.3848]**; pooled it is 2/16, [0.0155, 0.3835].
  4. The pairing check passes **12/12** on the new seeds and 16/16 overall. The check was redone from the files: environment rows, both digests in `conventional-digest.txt`, and additionally the conventional `c_best` and `c_mean` columns, identical over 250 rows.
  5. Against RBT-74 (+0.064, `runs/RBT-74/readout.txt:18`), t(4) is +1.12, p = 0.327. Against RBT-85 (−0.0485, `runs/RBT-85/readout-from-summaries.txt:25`), t(4) is −0.85, p = 0.445. Neither clears h. RBT-94 has no `runs/` directory.
- **Quantiles.** The t and χ² quantiles come from my own incomplete-beta and incomplete-gamma code, asserted to 1e-3 against t(4) 2.7764, t(7) 2.3646, t(11) 2.2010, t(15) 2.1314, and χ² 4.4038/23.3367 (12 df) and 6.9077/28.8454 (16 df). The CP bounds are beta quantiles.
- **Predictions.** All 3 of 3 are right, as the readout scored them.

### F2. Conventions (CAVEAT)

- **h's df.** `h = t(4)·RMS/√4` uses 4 df, but the null SD is estimated from 16 seeds. With the null's own df, t(16)·RMS/2 = **0.122**; with a normal quantile it is 0.112. The registered 0.159 is conservative. No committed verdict lies between 0.122 and 0.159, so no reading changes. The next A/B read against this null should state which quantile it uses.
- **The replication criterion is weak.** The 12-df CI is RMS × [0.717, 1.651], so "the CI contains 0.128" passes for any 12-seed RMS in [0.078, 0.179], which is nearly the whole predicted range [0.07, 0.16]. "Replicates" is correct by the registration, but it is weak evidence.
- **A small mix-up in the post hoc text.** REPORT.md:80 puts the spread 0.088 (divisor n) beside h 0.126, which is computed from SD 0.091 (divisor n − 1). At 0.088, h is 0.122. Both values support the same conclusion.

### F3. The evidence for an offset is stronger than the readout says (MUST-FIX, post hoc section only)

REPORT.md hedges: "the t-test assumes normality against a tail this ticket exists to measure, and the sign tests are 0.039 and 0.077." The sign test discards magnitudes, which makes it the weakest valid test here.

Under a pure A/A the two arms are **exchangeable**, so d is symmetric about 0 **exactly**, whatever its tail. The exact sign-flip (randomization) test on the mean is therefore the test that matches the null. It needs no normality assumption. Enumerated in full (`rederive.txt`, "post hoc offset"):

| set | mean d | exact sign-flip p | exact signed-rank p | sign test p | bootstrap 95% (BCa) | median / 20%-trimmed |
|---|---|---|---|---|---|---|
| 12 new | +0.082 | **0.0024** (10/4096) | 0.0024 | 0.039 | [+0.044, +0.126] | +0.074 / +0.080 |
| all 16 | +0.073 | **0.0055** (360/65536) | 0.0042 | 0.077 | [+0.034, +0.120] | +0.037 / +0.066 |
| 16 without tail seeds 201 and 212 | +0.050 | **0.022** | 0.017 | 0.18 | [+0.016, +0.087] | +0.029 / +0.049 |
| RBT-96's 4 | +0.047 | 0.75 | 0.88 | 1.00 | — | — |

- **The tail does not rescue "chance".** The exact test agrees with the t-test (0.0032 and 0.0057). Dropping both discovery seeds leaves p = 0.022.
- **A bootstrap at n = 12–16 under-covers** under a heavy tail. It is shown only for completeness; the exact test is the one to cite.
- **The fix.** Add the exact sign-flip line to the post hoc section and replace the sentence above. The registered readouts are unaffected.

### F4. (a) The code: salt 0 and salt 1 are one path with a different key (NONE)

`spawn_streams` (`rabbitstew/evolution.py:539`) builds `SeedSequence(seed).spawn(3)` and, for salt S > 0, replaces the holistic child alone with `SeedSequence(seed, spawn_key=(0, S))`.

- **One constructor.** The unsalted child *is* `SeedSequence(seed, spawn_key=(0,))`: the same entropy, key and pool size, and the same generated state. This holds for 16/16 seeds (`codepath.txt` §1). Both routes are SeedSequence → PCG64, differing only in the key.
- **The 1-generation probe.** The probe was labelled and run to scratch, not as an arm. It ran seed 205's RBT-96 configuration for one generation twice: once as shipped, and once with salt 0 forced through the salted branch with key (0,). `lineage.jsonl` and the history came out **byte-identical** (sha256 `777e0cff…`, `6cea9e36…`). The run also reproduces the committed `s0-205` generation-0 row: terrain 1674391996, h_best 0.554556 (§4). "Salt 0 writes the pre-salt config" is only `to_dict` dropping the key from `config.json`. Nothing reads its absence except `from_dict`, which defaults it to 0.
- **The other streams, byte for byte.** The conventional and terrain generator states are identical at salt 0 and salt 1. The committed files agree: conventional digests match, and so do the `c_*` columns and the environment rows.
- **No key collision.** An s0 run draws from keys (0,), (1,) and (2,). Salt 1's key (0, 1) would equal a grandchild of (0,) only if something spawned from a stream. Nothing does: there are no `.spawn(` or `seed_seq` calls outside `spawn_streams`.
- **Draw order and consumers are identical by construction.** The same `evaluate` and `reproduce` calls consume the holistic stream in both arms, and `champion_bouts` draws nothing. The salt has no other reader in `rabbitstew/`. `ecology.py` uses the same `spawn_streams` and refuses to combine the salt with `breed_stream`.
- **Nothing outside the streams differs.** There is no wall-clock dependence (`time` appears only in log lines). drive.sh runs s0 and s1 **concurrently** on one machine, so load is symmetric. The runners report clean exits (four of six say explicitly that there were no restarts), and resume restores the saved generator states in any case.
- **The founders are indistinguishable across salts.** Over seeds 1..300, the gen-0 holistic population at salts 0, 1 and 2 has the same mean nodes, parts, units, links and mass: paired t for 1 − 0 and 2 − 0 is within ±1.4 on all five (§3).

**Conclusion for (a).** Nothing but the holistic breeding stream differs between salt 0 and salt 1. It differs only by which PCG64 state a SeedSequence key hashes to. The stream's statistical quality, draw order, consumers and config are all the same. **No code path can give the salt-1 label an expected advantage.** For the A/A as built, E[d] = 0 is a property of the construction, not an assumption.

### F5. When the offset appears (CAVEAT)

Per fifth of the run, over 16 seeds (`rederive.txt`, "when does the offset appear?"):

| generations | mean d | RMS | positive | sign-flip p |
|---|---|---|---|---|
| gen 0 (founders) | −0.005 | — | 7/16 | 0.40 |
| 0–49 | −0.005 | 0.028 | 6/16 | 0.50 |
| 50–99 | +0.010 | 0.056 | 9/16 | 0.47 |
| 100–149 | +0.041 | 0.081 | 12/16 | 0.042 |
| 150–199 | +0.055 | 0.103 | 11/16 | 0.029 |
| 200–249 | +0.073 | 0.115 | 12/16 | 0.0055 |

- **No stream-quality effect.** A difference in founder draws would show at generation 0, and none does. The offset builds as the lineages diverge, in step with the spread. That pattern is what chance compounding through selection produces.
- **It would also fit an effect acting through reproduction.** But F4 leaves no such effect that could tell salt 0 from salt 1.
- **The fifths are not independent tests.** They share lineages.

### F6. The solo measures are the same signal (CAVEAT)

- **The correlations are strong.** Across the 16 seeds, corr(d, holistic solo-approach d) = **+0.72** and corr(d, terrain d) = **+0.74**. Of the 14 seeds with positive approach d, 12 also have d > 0.
- **So they do not add evidence.** "s1's solo approach exceeds s0's in 11/12" re-reads the same lineage outcomes. It is not a second test (exact sign-flip p = 0.009).

### F7. (b) Chance or systematic

- **Against chance: the exact test.** It is exact under the heavy tail and gives p = 0.0055 over the 16 seeds. The data are unlikely under a symmetric null.
- **Against a systematic cause: the construction.** F4 shows the salt-0/salt-1 contrast cannot carry an expected offset without a mechanism, and the code has none. The only difference is two SeedSequence keys, which are interchangeable.
- **The hypothesis is post hoc.** It was formed after the runners posted 10/12 positive, on the same 12 seeds that test it. The 4 earlier seeds, the only ones not used to form it, show nothing (+0.047, p = 0.75). An observer free to notice any of several oddities (the mean, the variance, the tail rate, one arm's approach) will find one at nominal p ≈ 0.005 more often than 1 in 200.
- **Verdict: undecided.** The committed files cannot separate "chance at a low but honest-after-selection p" from "a systematic cause outside the salt code path that this audit did not find". I searched for such a cause (§F4) and found none. **I do not claim a mechanism.** On the code evidence, chance is the better-supported reading, but not by a margin that should decide the null. The test in §c decides it.

### §c. A decisive test (designed and costed, not run)

The powers below come from simulation in `rederive.txt` (design (c)): 4000 trials per cell, a t-test at 5% two-sided, and three noise models:
- **N62:** normal σ_run = 0.062, the spread 0.088/√2;
- **N81:** normal σ_run = 0.081, RMS/√2, the pure-chance reading;
- **T:** normal 0.040 plus a +0.25 discovery with probability 1/16, matching the observed tail.

δ is a salt-0 deficit: 0.082 as observed, or 0.05 allowing for winner's curse.

| design | arms | pair-slots (40–60 min each) | power at δ 0.082 (N62 / N81 / T) | at δ 0.05 |
|---|---|---|---|---|
| **T3**, 12 fresh seeds (217–228), salts 0, 1, 2 | 36 | 18: about 12–18 h of session time, about 3 h wall across 6 runners | c0: **0.93 / 0.74 / 0.79**; c12 keeps its size (0.04–0.05) | 0.35–0.54 |
| T3, 16 fresh seeds | 48 | 24 | 0.98 / 0.87 / 0.89 | 0.47–0.69 |
| **T2**, 12 fresh seeds, salts 0 and 2 | 24 | 12: 8–12 h, about 2 h wall across 6 | 0.83 / 0.61 / 0.72 | 0.28–0.44 |
| R2, add one salt-2 arm to each of 205–216 | 12 | 6: 4–6 h, about 1 h wall across 6 | 0.39 / 0.25 / 0.32 | 0.12–0.18 |

- **The recommended design is T3 at 12 fresh seeds.** It needs one line of script change and no package change: an `s2` arm in `scripts/rbt96_run.sh`, and three arms per seed in drive.sh, or s2 run as a second pair.
- **The two contrasts:**
  - **c0 = (s1 + s2)/2 − s0**: salt 0 against non-zero salts;
  - **c12 = s2 − s1**: two non-zero salts.
- **The test.** Use the exact sign-flip test on each contrast, pre-registered, with the ±0.10 reading unchanged.
- **Reading the outcomes:**
  - **c0 ≠ 0 and c12 ≈ 0 means the offset is salt 0's.** Given F4 that would be a genuine surprise, so look for something outside the salt path that differs between the unsalted and salted stream families. Every salt-0 run in the programme would then carry that family's bias, relative to the salted runs and to RBT-105's `breed_stream` replicates, whose key is (0, 0, K).
  - **c12 ≠ 0 means the label matters between any two salts**, the salt-1-specific or any-key case. That would mean stream keys are not exchangeable, which is worse: seeds would carry it too.
  - **c0 ≈ 0 and c12 ≈ 0 means chance.** RBT-108's offset was a post hoc false alarm, and the registered RMS null stands.
- **R2 is cheap but underpowered** (≤ 0.39 at δ = 0.082). Its contrast is orthogonal to the observed s1 − s0, so it is unbiased despite reusing arms. It is not decisive on its own.
- **T2 cannot tell chance from a salt-1-specific effect.** That case is implausible, but T3 closes it for 12 more arms.
- **Power is only adequate at the observed δ.** If the true δ is 0.05, even T3 at 16 seeds has 0.47–0.69.

### F8. (d) Consequences for h, n and the verdicts (CAVEAT)

- **If the offset is real (a salt-0 deficit δ):**
  - Every committed arena A/B compares arms at **the same salt**. RBT-74 and RBT-85 predate the salt and are both salt 0. So δ never enters an A/B d, and the right null for an A/B is the A/A's spread about its mean. That is SD 0.091 (divisor n − 1; 0.088 with divisor n), giving h = **0.126** (0.122), **6 seeds** for ±0.10, and RBT-94's 8-seed half-width 0.076.
  - "A/A" would then need renaming, since it would be an A/A′ with a known bias. Any design that contrasts stream keys (RBT-105's replicate histories) would inherit the problem.
- **If the offset is chance, which the code evidence of F4 favours:**
  - The true mean of d is 0 by construction, so **RMS about 0 is the unbiased estimator of the null SD** (E[RMS²] = σ²_d). Subtracting a sample mean that is itself noise removes a genuine noise component, here an unusually large one. That understates the null and makes h anti-conservative: 0.126 against 0.159.
  - **So the "pure spread" null is right only if the offset is real.** Until §c is run, the registered RMS null (0.115, h 0.159, 8 seeds) should stand, as the conservative choice. F2's df point lowers h to 0.122 on other grounds.
- **The verdicts do not flip.** RBT-74's |+0.064| and RBT-85's |−0.0485| clear none of 0.159, 0.126, 0.122 or 0.112. RBT-94 has no verdict.
- **What does change is the future sizing.** At 8 seeds, a ±0.10 A/B needs its effect to clear 0.096 under the registered null, or 0.076 under the spread-only null. A borderline RBT-94 result would read differently under the two, so §c is worth running before RBT-94, not after.

## What survives

- All five registered readouts, at their printed values: the null replicates, h = 0.159, 8 seeds, a tail of 1/12, pairing 16/16, and no earlier verdict clears.
- The readout's refusal to claim a mechanism, which is correct.
- **Its post hoc strength of evidence needs F3's correction:** exact p = 0.0024 (12 seeds) and 0.0055 (16).
- The salt contrast *as code* is a pure A/A (F4). Whether the realised offset is chance is open, and T3 at 12 fresh seeds (36 arms) decides it.

---
_Generated by [Claude Code](https://claude.ai/code)_
