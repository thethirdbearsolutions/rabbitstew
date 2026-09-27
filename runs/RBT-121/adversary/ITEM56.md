## 5. B §3: evaluation noise

**Verdict: HOLDS-WITH-CAVEAT.** The size of s holds. The designed body's "0.004" and "ranked on noise" are
**OVERSTATED**: that number is the estimator's floor.

**Method.** RBT-113 O1 was restored with B's command. B's estimator was checked, and U seed 1 was re-scored on 12
fresh draws: terrains 5131+, 40 members per fauna. Outputs are `noise_components.txt` and `noise_resample.txt`.

**How B's repeatability is computed** (`noise.py`):
- sb² = max(var(member means) − sw²/6, 0);
- rep₂ = sb² / (sb² + sw²/2), from 6 draws.

It floors at 0.

| RBT-113 U seed 1 | holistic | designed |
|---|---|---|
| B's rep₂ | 0.14 | **0.004** |
| B's estimator, all 12 of my draws | 0.21 | 0.078 |
| B's estimator on every 6-of-12 subset: median [5–95%] | 0.16 [0.05, 0.28] | **0.031 [0.000, 0.141]**; exactly 0 in **29%** of subsets |
| between-member SD (two-way ANOVA) | 0.56, F = 2.76, p ≈ 0 | **0.21** (B: 0.056), **F = 1.60, p = 0.015** |
| member × draw SD | 1.47 | 0.95 |
| runs eating 0 items | 49% | 45% |
| distinct genomes | 40/40 | 40/40 |

**What this shows:**
- The designed population is not a set of clones, and its genotypic spread is real (p = 0.015).
- 0.004 is a 6-draw ICC on a zero-inflated score, sitting on its floor. It is not a property of the population.
- **Corrected value:** designed rep₂ is about 0.03–0.1, poorly determined. Holistic is about 0.15–0.25.
- Also, "heritable" is the wrong word for this between-member variance: it is not h².

**Repeatability is not what sets s.**
- B's Monte Carlo s is truncation selection on one carrier. It equals i·Δ/σ_P, with i = 1.27 at the top 25%, to
  within about 0.01.
- Setting the between-member SD to 0 hardly moves it: designed, Δ 0.05 gives 0.090 → 0.101.
- The 0.14 / 0.004 headline is therefore decorative. Δ/σ_P is what matters.

**B's own `selection_s` on the re-measured components:**

| Δ | s, holistic | s, designed |
|---|---|---|
| +0.02 | 0.023 | 0.036 |
| +0.05 | 0.056 | **0.090** |
| +0.10 | 0.115 | 0.188 |

**Erosion units.**
- RBT-113 runs with elites 0, so per-child loss u is per-generation loss, and the units match.
- The hold condition is (1 + s)(1 − u) > 1, i.e. s > u/(1 − u). That is 0.098 at u 0.089, 0.18 at 0.15 and 0.39 at
  0.28, so B's "s > u" is slightly lenient.
- The u values are imported from paper 10 and RBT-112. They have not been re-measured for RBT-113's operator.

**Corrected statement:** "At 2 draws, s ≈ 1.27 Δ/σ_P, with σ_P ≈ 0.7 (designed) to 1.2 (holistic). A +0.02 to
+0.05 gain gets s ≈ 0.02–0.09. That is below u/(1 − u) for u = 0.15 or 0.28, and at the boundary for the designed
body at u_Z = 0.089."

## 6. C finding 2 (the flat nose gradient) and the PW proposal

### 6a. "A nose step buys 0–7%, +25% speed buys 12–37%"

**Verdict: HOLDS-WITH-CAVEAT.** The ordering is robust, but the individual percentages are not resolved.

**The grid** (`smell_grid.txt`): C's model was run unchanged on 3 turn limits (0.25 / 0.5 / 1 rad/s) × 3 heading
noises (0.5 / 1 / 2) × 2 worlds, with n = 200 paired seeds and paired-bootstrap CIs.
- **Speed beats the nose step in all 18 cells.**
  - +25% speed: +13 to +40%, with the lower CI ≥ +5.6 points everywhere.
  - k 1→1.4: −0.8 to +7.6%.
  - k 2→2.4: −1.7 to +9.9%.

**Not resolved:**
- At C's calibrated cell (uniform), k 1→1.4 gives +0.0% [−2.0, +2.0] and k 2→2.4 gives +0.5% [−1.8, +3.0]. C's "+1%
  against +5%" cannot be told apart, from each other or from zero.
- C's own two probes give **+12%** (`probe_gradient`) and **+31%** (`probe_proposal`) for +25% speed in the same
  cell. The Monte Carlo spread is about ±10 points.

**The calibration** is flat across neighbouring cells, not a sharp optimum:
- log-error 0.31–0.36 for (0.25, 1), (0.5, 1) and (0.5, 2);
- C's grid stopped at its noise edge.

The conclusion survives this, but the calibration does not pin the regime.

**"Mutation-sized" differs between the two sides:**
- k + 0.4 is one absolute weight σ (`genetics.py:48`) on a signal of about 0.02.
- +25% speed is a relative change in a phenotype. Per B, one gear mutation has a log-ratio SD of about 1.0, so +25%
  is if anything *small* for speed.

The asymmetry is therefore real, and if anything understated.

**Corrected statement:** "Across a 3×3 neighbourhood of the calibration, +25% speed pays +13–40%, and a one-σ nose
step pays about 0–10%. Single values of a few percent are within Monte Carlo error at n = 200."

### 6b. Does the proposed `smell_gain` (centred log contrast) do what C says?

**Verdict: OVERSTATED.** The numbers are for a different G, and the centring has costs C does not state.

**What holds:**
- The model's `intensity` is `simulation.py:492–512` exactly (sum / mean / log).
- Regrowth matches, both instant and delayed (`simulation.py:421–434` and `:443–486`).
- The reading reaches the brain raw as an activation (`brain.py:97–98`).
- Real bodies see a common mode of about 0.55 against a differential of about 0.03, so **the case for centring is
  sound**.

**What does not:**
1. **The model's GAIN is not the proposal's G** (`smell_proposal_check.txt`).
   - The model computes GAIN·(I_L − I_R) on squashed intensities. The proposal is tanh(G·(ln Σ − ln Σ_root)).
   - In sum mode, d ln Σ/dI ≈ 4 at the typical Σ, so model GAIN 10 ≈ proposal G 2.5. G = 2.5 reproduces C's rows:
     PW k6 2.10 against C's 2.16.
   - At the **proposed G = 10**, per-sensor contrasts saturate. In the simulator, median |c| is 0.56–0.64 and p90 is
     0.93–0.95.
   - Then **k 2→2.4 pays only +2–3%**, against C's +8 to +13%.
   - So C's 846f913 claim that "in PW every single step clears B's 0.1 threshold" (`probe_margin.txt`) describes
     G ≈ 2.5, not the proposed 10. At G = 10 the second step is about +0.05 items.
2. **Root-centring zeroes a root sensor for ever.**
   - Every sampled designed body has 3 food sensors, one of them on the root.
   - A single-nose or root-nose body therefore loses all smell.
   - So does the temporal route (a `differentiate` unit on one sensor, which is klinokinesis), and the absolute food
     level that area-restricted search would use.
   - The proposal turns "perception" into "bilateral spatial contrast only". A per-robot running baseline, or a
     centred channel alongside a level channel, avoids this.
3. **"Exact food rules" is OVERSTATED for eating.**
   - The model eats from the centre of mass + 0.15 m.
   - The simulator eats from **any geom centre** within 0.35 m (`simulation.py:466–475`).
   - Real food-sensor spans are 0.39 m (designed) and 0.54 m (holistic).
   - The model under-credits blind swath, which would favour speed further, so the direction of the conclusion
     is safe.
4. **The nose differential.**
   - C's 0.017 holds for C's 0.3 m geometry (simulator: 0.022 designed / 0.018 holistic).
   - Real bodies' own sensors are further apart and read a median of **0.029 / 0.033** (`smell_sensor_ranges.txt`).

**Corrected statement:** "The model's 'gain 10' corresponds to a centred log-contrast G of about 2.5. At G = 10
contrasts saturate and later nose steps pay about 2%. Root-centring deletes root-sensor, single-sensor and temporal
smell. A PW registration should state G, test at least G ∈ {2.5, 10}, and centre on a running baseline rather than
on the root."
