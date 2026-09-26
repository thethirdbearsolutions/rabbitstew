# RBT-96 adversary report

This attacks PR #146 (`results/RBT-96`, head `3f7ccec`). Every number below re-derives from a file in this directory.

- **Compute:** about 2 h of four cores for the champion re-measurement (`champions.py`, 7,043 s). The rest was minutes.
- **Platform:** Intel Xeon @ 2.80 GHz, x86_64, Python 3.11.15, MuJoCo 3.14.0, numpy 2.4.6. This is a different container from the delegate's.
- **No new arms were run.**

## Files by role

| role | file |
|---|---|
| item 1: champions re-measured from the restored bulk (rule 6: it reads `history.json` and genomes, never a checkpoint's tables) | `champions.py` → `champions.txt` |
| item 2: flip-rule verdict under each estimator (committed summaries only) | `estimators.py` → `estimators.txt` |
| item 3: founders against luck, and the power of the proposed follow-up (committed summaries only) | `founders.py` → `founders.txt` |
| item 4: build (salt 0 against the pre-salt code, a mutant, suites) | `item4.sh` → `item4.txt`; `test_salt0_golden.py` |
| item 5: `--from-summaries` in a bulk-free worktree, plus four perturbations | `rederive.sh` → `rederive.txt` |
| item 6: platform scope | `platform.md` |

## Findings

| # | claim attacked | verdict | the number | file |
|---|---|---|---|---|
| F1 | Seed 201's s1 found a better locomotor, not an artefact | **holds, and is stronger than stated** | See F1 below | `champions.txt` §201 |
| F2 | The spread is between lineages, not within runs | **holds** | See F2 below | `champions.txt` summary |
| F3 | h = 0.178 > 0.10: the ±0.10 rule is unsound at n = 4 | **holds** under the pre-registered estimator and every defensible one; it rests on seed 201 alone | See F3 below | `estimators.txt` |
| F4 | RBT-85's −0.049 is inside the null (p = 0.49) | **holds** | See F4 below | `estimators.txt` |
| F5 | The A/B-versus-A/A inversion: shared founders or luck, "not separable", and the lean towards founders | **partly holds.** "Not separable at n = 4" stands. The lean towards founders **fails** on the committed data, which favour luck | See F5 below | `founders.txt` |
| F6 | The proposed follow-up, a founder-sharing A/A (one flag, ~4 h) | **fails as the next measurement** | See F6 below | `founders.txt` §5 |
| F7 | Salt 0 is the unsalted stream exactly, and the tests pin it | **partly holds.** The property holds; **the tests do not pin it** | See F7 below | `item4.txt`, `test_salt0_golden.py` |
| F8 | `--from-summaries` re-derives the readout; it is a derivation, not a replay | **holds** | See F8 below | `rederive.txt` |
| F9 | Cross-machine reproduction fails at generation 0; "a seed is an artifact of its platform" | **partly holds.** It is established for ARM M4 against x86 in the arena, and refuted, as far as tested, between x86 cloud containers. **No programme comparison crosses platforms** except the RBT-85 ↔ RBT-96 juxtaposition | See F9 below | `platform.md`; `champions.txt` §B |

### F1. Seed 201's s1 is a genuine discovery

The harness is calibrated first. Gen 249's round robin, replayed on its own terrain seed, equals `history.json` **exactly** in all 8 runs, on a different x86 container.

Seed 201, s1 against s0, on 5 fresh terrains the run never saw (2,750 bouts per arm):

| measure | s0 | s1 | d |
|---|---|---|---|
| fresh-draw mean fitness | 0.248 | 0.579 | **+0.331** (in-run +0.246) |

- d is positive on every fresh terrain (+0.21 to +0.43) and in every one of the 11 checkpoints (+0.15 to +0.41).
- **Against other seeds' wheeled champions**, d is +0.086 (202's runaway), +0.172 (203) and +0.286 (204's driver). So the edge is general, not specific to one opponent.
- **Solo**, over all 55 final-fifth champions per arm:

  | measure | s0 | s1 |
  |---|---|---|
  | approach | +0.55 m | +1.62 m |
  | steering (of 3) | 0.00 | **2.00** |
  | fresh-terrain success (12 terrains) | 0.05 | 0.68 |

- Explosions are rare and balanced: 2 against 5 of 2,750 fresh bouts, and 0 in solo.

s1-201 grew a steering locomotor and s0-201 did not.

### F2. The spread is between lineages

The four d re-measured on fresh terrains correlate with the in-run d at **r = +0.994**:

| seed | in-run d | fresh d |
|---|---|---|
| 201 | +0.246 | +0.331 |
| 202 | −0.024 | −0.059 |
| 203 | +0.029 | +0.032 |
| 204 | −0.063 | −0.062 |

The fresh RMS is 0.172, so h would be 0.239. d is a property of the lineage pair, not of the terrain draw. If anything, the in-run RMS understates the null.

### F3. The ±0.10 rule is unsound at n = 4

The pre-registration committed to the **RMS with the mean fixed at 0 (4 df)**.

| estimator | h | verdict |
|---|---|---|
| RMS, mean 0 (pre-registered) | 0.178 | unsound |
| SD (3 df) | 0.191 | unsound |
| random-effects model on the 44 checkpoints | 0.178 | unsound. Identical to the RMS: the checkpoints add df only to the within-run term (sd 0.081), while the between-lineage sd is 0.126 on 4 df |
| sign-flip bootstrap | 0.131 | unsound |
| robust median\|d\|/0.6745 | 0.094 | edge |
| without seed 201 | 0.059 | sound |
| checkpoints as 44 iid draws (pseudo-replication) | 0.063 | sound |

- P(σ ≤ 0.072, i.e. h ≤ 0.10 | RMS on 4 df) = **0.013**.
- **The two estimators that flip the verdict are not defensible:**
  - the robust one discards the tail, and F1 shows the tail is real;
  - the pseudo-replicated one treats autocorrelated checkpoints of one lineage as independent.
- **The verdict rests on seed 201.** Without it the data cannot tell (P(σ ≤ 0.072) = 0.79).
- A minor point: the report's P(|mean| ≥ 0.10) = 0.194 is the t(4) predictive probability. With σ taken as known it is 0.119. Both exceed 0.05.

### F4. RBT-85's −0.049 is inside the null

| estimator | RBT-85 p |
|---|---|
| RMS | 0.49 |
| SD | 0.53 |
| robust | 0.15 |
| pseudo-replication only | 0.037 |

### F5. The inversion: luck fits the committed data better than founders

- **Founders are shared in RBT-85 and not here.** RBT-85's gen-0 rows are identical in all four seeds and diverge at gen 2. RBT-96's differ at gen 0.
- **If shared founders tightened the pairs, the first fifth should show it most. It does not.** Per-fifth RMS of the paired difference:

  | design | fifth 1 | fifth 2 | fifth 3 | fifth 4 | fifth 5 |
  |---|---|---|---|---|---|
  | A/A, independent founders | 0.029 | 0.052 | 0.070 | 0.104 | 0.128 |
  | A/A without seed 201 | 0.029 | 0.031 | 0.065 | 0.065 | 0.042 |
  | A/B, shared founders | 0.036 | 0.043 | 0.060 | 0.065 | 0.063 |

- Cross-seed arm correlation without seed 201 is 0.963 (A/A) against 0.958 (A/B), nearly identical.
- The only difference between the designs is one discovery event.
- **How likely is luck?** P(four pairs' SD ≤ 0.046 | A/A σ) = 0.058. If one run in eight discovers, as observed here, P(none of RBT-85's 8 runs does) = 0.34.

### F6. A founder-sharing A/A is not the right next measurement

- F5 finds no founder effect to measure.
- At 4 seeds its power to show a tighter null is **0.15–0.58**, for a founder-sharing σ between 0.090 and 0.046. At 8 seeds it is 0.21–0.74.
- It also needs a code change (salt applied after `initial_population`). At RBT-96's rate that is about 4 h 15 min on four cores per 4 seeds. The report's own figure is 3.2 h in one place and ~4 h in another.
- **Better:** more *independent* A/A seeds. The quantity that decides the rule is the rate of discovery events, the tail, and every extra seed of any founder design samples it.

### F7. The salt-0 property holds, but the tests do not pin it

The property holds:
- On the PR head, salt 0 writes `lineage.jsonl` and `history.json` byte-identical to the pre-salt code `852dcac`, over 6 generations at seed 201.
- An old `config.json` resumes.

**The tests do not pin it.** Both tests compare the new function with itself. A mutant that re-spawns salt 0 at key (i, 0) changes every earlier run's holistic lineage (byte 90 of line 1), yet it passes `tests/test_rng_streams.py` 8/8 and **the full suite 259/259**.

`test_salt0_golden.py` pins salt 0 in two ways:
- against the pre-salt construction, written out independently;
- against literal draws recorded on `852dcac`, whose terrain draws are s0-201's committed terrain seeds.

It passes on the head and fails 2/2 on the mutant. **Recommended to add to `tests/` before merge.**

Suites: PR head **259 passed**; trial merge with `claude/new-session-4cao7d` merges clean, **286 passed**.

### F8. Re-derivability holds

- From a worktree at `3f7ccec` with 0 bulk files, `--from-summaries` is **byte-identical** to `readout-from-summaries.txt`.
- The readout regenerated from the restored bulk equals `readout.txt`, less the "wrote" line.
- Four one-cell perturbations each move the readout:

  | cell perturbed | effect on the readout |
  |---|---|
  | s1-201 gen 245 +0.11 | d +0.246 → +0.256, RMS 0.128 → 0.133 |
  | one digit of a conventional hash | pairing check False |
  | one opponent approach | covariate and correlations move |
  | one terrain seed | "terrain identical" False |

### F9. The platform finding: scope

What is established:
- RBT-96 showed ARM M4 against x86 diverging at generation 0 in 4/4 seeds, in the physics; the RNG draws are identical.
- **Between x86 cloud containers, runs reproduce as far as tested:**
  - this adversary's exact replay of 8 runs' gen-249 bouts;
  - RBT-92's shared-baseline sha256, agreeing across at least five cloud sessions (ecology).
- The ecology has **never** been compared between ARM and x86, so there the effect is untested, not refuted.

Where the programme's arms ran:
- **Every ecology arm and cited control ran on cloud x86:** RBT-90 part 2, RBT-92/99/100/101, and RBT-104's design check. No seed-paired comparison crosses platforms.
- **The one laptop↔cloud juxtaposition is RBT-85 against RBT-96.** It is legitimate as a comparison of spreads. It is unpaired per seed: seed 201's wheeled side is a runaway on the laptop and a driver here.
- **Residual gap:** configs record no platform, CPU or version. The proposed `config.json` fields should include the CPU model and numpy's version, not only `platform.machine()` and MuJoCo's version.

## What survives

- **The four headline claims survive**: RMS 0.128, the rule unsound at n = 4 with h = 0.178, RBT-85's p = 0.49, and generation-0 cross-machine failure.
- **Seed 201 is a real lineage property.** Re-measured on fresh draws, it makes the null wider, not narrower.
- **What does not survive:**
  - the report's lean towards shared founders as the explanation of the inversion;
  - the founder-sharing A/A as the proposed follow-up;
  - the tests' claim to pin salt 0.
- **"A seed is an artifact of its platform"** should read *ARM against x86*. Cloud x86 containers agree with each other.
