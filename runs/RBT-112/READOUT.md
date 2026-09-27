# RBT-112 readout: is the operator the stall?

*Designer's readout, 2026-09-27, from integration `7557d23`. All ten HZ arm PRs (#362–#371) and the launch PR (#360)
are merged.*

**How it was run:**
- `runs/RBT-112/readout.py` ran **as registered**. It, RBT-106's `readout.py` that it imports, and `rabbitstew/` are
  unchanged since the launch PR (`git diff 6dfa780 7557d23` is empty on all three).
- Its verbatim output is `readout.txt`.
- Everything beyond the registered lines is in `sensitivity.py` → `sensitivity.txt`. It is POST HOC and print-only,
  written after `readout.txt` was seen, and it touches no scored path.
- No arm, and no ecology run, was made for this readout.

## 1. The registered verdict

```
usable paired seeds: 10 of 10 (viable, x86_64, both positive controls, code certified, no freeze.py FAULT, both held readings present)
HELD (each against its own operator's table): HU 0, HZ 1
HZ per seed (F14): n planted-rooted at 300 / 599 -> class: 801: 55 / 59 -> NOT HELD; 4: 1 / 0 -> LOST; 804: 52 / 60 -> NOT HELD; 805: 55 / 60 -> HELD; 806: 23 / 26 -> NOT HELD; 807: 40 / 42 -> NOT HELD; 1: 60 / 60 -> NOT HELD; 2: 20 / 3 -> NOT HELD; 3: 55 / 60 -> NOT HELD; 7: 29 / 16 -> NOT HELD
#LOST(HZ) = 1 of 10 usable (FALSIFIED needs <= 2; >= 3 is FALSIFIED-ROOTS)
side effects, HZ - HU over the window: designed income +0.160 [+0.050, +0.271]; alive +0.000 [+0.000, +0.000]; births +6.300 [-44.560, +57.160]; window depth +0.328 [-0.940, +1.597]
COMPASS lines (primary FD and attribution FD), patchy-scored: HU 0, HZ 5
paired F(HZ) - F(HU): patchy-scored +1.654 [+0.785, +2.523], uniform-scored +0.468 [+0.290, +0.646]

VERDICT Z: FALSIFIED: with the planted roots alive, freezing the global biases (erasure 0.282 -> 0.089 per generation) did not let selection hold the compass; the operator is not the stall
  SE-Z FAILED (window income HZ - HU excludes 0): the verdict is worded 'with the designed body's global biases frozen (host and planted)', not 'the planted unit's bias walk'; paired births and depth are printed above
  function (reported, not in the verdict): FUNCTION FOLLOWS   [FOLLOWS: HZ COMPASS >= 3 and paired F interval > 0]
```

**The scored verdict is FALSIFIED.** [Amended 12:20 per the readout adversary's A3 (PR #373) and the ruling; the
label and `readout.txt` are unchanged.]

> **FALSIFIED** (registered). With the designed body's global biases frozen (host and planted), selection did not
> hold the planted paying compass above what that operator alone leaves: 1 of 10 seeds held (805), against 0 of 10
> under the default operator, with planted roots alive on 9 of 10. **The bias walk is not what stops selection
> holding the compass in the population.** Selection's advantage on it is below ~0.1 per generation (the registered
> limit; the arms' own likelihood puts it at 0–0.08). With the global biases frozen the host also changed (SE-Z
> failed, income +0.160), so a change in s itself is not handled. **This does not say the operator is irrelevant:**
> under S = 0 the compass persists at the operator-alone level, and the income-best lines carry it and use it (5
> COMPASS lines against 0; champions carrying 31 of 70 against 5 of 70). Under the default operator they do neither.
> What the operator decides is how much compass is left for the best lines to use. What it does not decide is
> whether selection raises its frequency: it does not, under either operator.

**Which reading decided each non-HELD seed** (A1; `readout-adversary/instrument.txt`). Of the 8 HZ seeds neither
HELD nor LOST:
- **300 was binding on 7 of 8.** They fell further short of B at 300 than at 599.
- **Seed 1 was decided at 599.** It was 4 short at 300 (29 against 32) and 19 short at 599 (2 against 20).
- **Seed 807 was above B at 599** (16 > 14) and failed at 300 (18 ≤ 21).

This is the registered two-reading rule working as designed. Seed 4 is LOST (n = 1 at 300, 0 at 599), and seed 805 is
the one HELD.

**Usability.** All 10 pairs are usable. None was dropped: every arm is viable, on x86_64, passes both positive
controls, is code-certified and has both held readings. The HZ arms show no `freeze.py` FAULT.

**Function, reported beside the verdict and not in it: FUNCTION FOLLOWS.**
- 5 of 10 HZ lines are COMPASS lines (primary FD **and** compass attribution FD, patchy-scored), against 0 of 10 HU
  lines.
- The paired F(HZ) − F(HU) is +1.654 [+0.785, +2.523] patchy-scored, and +0.468 [+0.290, +0.646] uniform-scored.

**Side effect SE-Z (prediction 0.65: income interval includes 0): failed, upward.**
- HZ's window income is +0.160 [+0.050, +0.271] above HU's.
- Births (+6.3 [−44.6, +57.2]) and window depth (+0.33 [−0.94, +1.60]) do not differ.
- So the treatment is "global biases frozen (host and planted)", as registered. The host did not breed more slowly.

## 2. Power at the usable n (the programme rule)

The usable n is **10, the planned n**, so the registered figures (`power.txt`, §10.1) apply unchanged.

**FALSIFIED is the "not held" verdict.** It needs #HELD(HZ) ≤ 1. The planted roots were alive on 9 of 10 seeds,
so the n = 40 scenario is the relevant anchor rather than the genealogy's.

| selective advantage s per generation | 0 | 0.05 | 0.089 | 0.12 | 0.15 | 0.20 | 0.25 |
|---|---|---|---|---|---|---|---|
| P(#HELD(HZ) ≤ 1), n = 40 anchor (`power.txt`) | 0.960 | 0.696 | 0.331 | 0.128 | 0.041 | 0.005 | 0.001 |
| the same, genealogy anchor | 0.991 | 0.899 | 0.682 | 0.462 | 0.282 | 0.108 | 0.040 |
| the adversary's self-consistent model, M15 / M40 (§10.1) | | | | | 0.379 / 0.363 | 0.214 / 0.091 | 0.079 / 0.016 |

**[Amended 12:20, A6] At the arms' realised n and depth.** This is power.py's own model (`q_seed`, `x_of`,
`poibin`, unchanged), re-run by the readout adversary at each HZ arm's realised planted-rooted n and mean depth
(`readout-adversary/instrument.txt` (2)):

| s | 0 | 0.089 | 0.12 | 0.15 | **0.20** | 0.25 |
|---|---|---|---|---|---|---|
| P(#HELD(HZ) ≤ 1), realised n, ρ 0 / 0.10 / 0.30 | 1.000 / 0.971 / 0.904 | 0.320 / 0.380 / 0.431 | 0.038 / 0.160 / 0.263 | 0.002 / 0.056 / 0.151 | **0.000 / 0.008 / 0.054** | 0.000 / 0.001 / 0.019 |

**The arms' own likelihood of s** (`instrument.txt` (3)): the BetaBinomial log-likelihood of every observed k_planted
under x(d, s), over both readings and ten seeds.
- The MLE is s = 0.00.
- The 95% profile interval is **s ∈ [0.00, 0.08]**, with ρ profiled. The arms fit ρ ≈ 0.3.
- At ρ 0.10 the interval is [0.00, 0.03].

**Caveats (the adversary's):**
- **Model-based.** Both figures use the mutation–selection recursion with u fixed at 0.089, and treat the two
  readings as independent in the likelihood.
- **SE-Z failed**, so this s is HZ's host's s, and not necessarily s under the default operator.
- **A9's clade route.** Selection that acts by expanding planted clades early would show in n, not in k_planted/n,
  and HELD cannot see it. Planted-rooted n, paired HZ − HU, is +18.7 [−9.4, +46.8] at 599.

**What this says:**
- FALSIFIED is **strong evidence against a population-level selective advantage of s ≥ 0.2**. At s = 0.2 it fires
  with probability **0.000–0.054 at the realised n**, and 0.005 at the n = 40 anchor. M15's 0.214 is the pessimistic
  model.
- Below s ≈ 0.12 it is weaker, firing 0.04–0.26 at s = 0.12 at the realised n (the design anchors gave 0.13–0.70).
  The arms' own likelihood puts s at 0–0.08.
- In words, if selection held the compass in the population it did so weakly, below ~0.1–0.15 per generation, even
  with the erasure cut to 0.089.
- SUPPORTED's registered power over the window s = 0.15–0.30 is 0.34–0.63 (genealogy) and 0.78–0.98 (n = 40), and it
  did not fire.

## 3. The two readouts disagree: POST HOC, print-only (`sensitivity.txt`)

**The registered structure call says "not held". The registered function line says "function follows".** Both are
registered and both are printed; only the first is the verdict. The sensitivity section asks where the gap is, and
scores nothing.

**S1: the champions carry the planted compass in HZ, not in HU.**
- Of the seven window bests per arm (300, 350, …, 590), F12's print counts the champions carrying a paying planted
  unit.
- **HZ: 31 of 70. HU: 5 of 70.** Paired per seed, HZ − HU is +2.6 [+1.4, +3.8] of 7.
- Every HZ carrier rests at b = 0 (0 FAULTs), so F12's masking route is closed, as registered.

**S2: the population share is not above what the operator alone leaves, even against the crossover-inclusive null.**
- The registered B comes from the no-crossover lineage table.
- Against the crossover-inclusive S = 0 null's replicates instead (part 2's genealogy, so a caveat applies), HZ is
  above the null's 95th percentile at both readings on **1 of 10** seeds: 805, the same one.
- [Amended 12:20, A7] This 1 of 10 is at best 1 of 5 testable seeds, because the part-2-genealogy null is nan or
  saturated on 807, 4, 2, 3 and 7. The adversary's null on **each HZ arm's own genealogy**, with crossover
  (`readout-adversary/ownnull_pool.txt`), is informative on all nine non-LOST seeds. It finds 805 alone above its 95th
  percentile at both readings. On that basis the verdict does not turn on how the null treats crossover.

**S3: carriage over all living genomes at 599** (planted-rooted plus crossover transfers into bare roots) is
+0.167 [+0.001, +0.333] HZ − HU. HU is 0.000 on every seed. HZ's 12 bare-rooted carriers include seed 4, which is
**LOST** under the registered root rule, although 36 bare-rooted carriers held its compass at 300 and 9 at 599.

**A reading, labelled as one (not a finding).**
- With the global biases frozen, the planted compass stays unmasked, and **the champions, selected on income, carry
  it and use it**: 5 COMPASS lines against 0, and a higher mean income.
- **But selection does not raise its share in the population above the operator's own residual erasure.** The
  compass is kept at the top of the income distribution, and it is not spread through the population faster than
  mutation removes it.
- These are two different things: "held" (a population frequency above the no-selection null) and "used by the
  best" (function).
- RBT-112 registered the first as its question, and it reads FALSIFIED. The second is registered as the reported
  function line, and it reads FOLLOWS.
- **The contrast with HU is stark on the function side:**
  - HU has 0 COMPASS lines and 5 of 70 carrying champions.
  - Under the default operator the compass is erased from the champions too.
  - Under S = 0 it survives in them.
- Which of these two is "the stall" is a question for the adversary and the ruling, not for this readout.

## 4. Predictions (§6.4, §10), right and wrong

| # | prediction | confidence | outcome |
|---|---|---|---|
| Z-0 | SUPPORTED 0.40, FALSIFIED 0.17, FALSIFIED-ROOTS 0.08, NOT DECIDED 0.28, VOID 0.07 | — | **FALSIFIED** (registered at 0.17) |
| Z-1 | #HELD(HZ) ≥ #HELD(HU) + 1 | 0.70 | right (1 against 0) |
| Z-2 | FUNCTION FOLLOWS | 0.20 | **right** |
| Z-3 | no FAULT; carriers at b = 0 | 0.99 | right |
| Z-4 | HZ's raw carrier share at 599 above HU's, t interval above 0 | 0.80 | wrong, just: +0.168 [−0.007, +0.342] |
| SE-Z | income interval includes 0 | 0.65 | **wrong**: +0.160 [+0.050, +0.271] |
| SE-Z2 | no HZ arm extinct | 0.90 | right |

## 5. Files

| file | role |
|---|---|
| `readout.txt` | `readout.py`'s verbatim output (the scored verdict) |
| `sensitivity.py`, `sensitivity.txt` | POST HOC, print-only: S1–S4 |
| `READOUT.md` | this |
