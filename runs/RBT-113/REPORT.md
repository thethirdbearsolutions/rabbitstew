# RBT-113 readout report (with RBT-117's registered comparison)

*Designer's report, 2026-09-27. Branch `results/RBT-113-readout`, cut from integration `b1f7690` (all 8 arms
merged).*

**How it was run.** Everything was run exactly as registered, with no change to any scored code:
- `runs/RBT-113/PREREGISTRATION.md` with §11 governing, and RUNNER §6;
- the 8 checkpoints restored at 216/216, with the tracked evidence byte-identical after restore;
- `decompose.py` on all 24 seed directories, then `readout.py`;
- RBT-117's `compare.py` on the 12 default-operator seed directories, CONFIRMATORY.

**Environment.** The `rabbitstew/` tree was `5dbfbcd373ca` on all 8 arms, which is the tree the pre-launch controls
certified. Platform: x86_64, mujoco 3.14.0, numpy 2.4.6.

**Files:** `readout.txt`, `decompose.txt`, the 24 `decompose.json` files and `sigma0_reference.json`; and
`runs/RBT-117/compare.txt`.

---

## 1. The fixed headline (printed by `readout.py`, verbatim)

> Under imposed truncation selection (top / bottom / random 10 of 40, discrete generations, solo scoring, 24
> generations from random founders, paper 5's world), over 12 seeds (two replicates each), holistic, per seed (both
> operators: the operator does not reach it): the up and down lines diverged by +0.430 [+0.375, +0.484] sigma0 per
> generation (+0.0951 [+0.0830, +0.1072] yield per generation; sigma0 = 0.2212), with realised h2 +0.093 [+0.080,
> +0.106]; against the control, the up line moved +0.148 [+0.114, +0.182] and the down line +0.282 [+0.231, +0.332]
> sigma0 per generation. At generation 23, food was 35% of the U − D change in net yield (88% of U − C, 7% of C − D),
> and work the rest (food share = |delta food| / (|delta food| + |delta work|); signs U − D food +, work -, U − C
> food +, work +, C − D food -, work -). Verdict: RESPONDS. RESPONDS is the expected verdict, since mutation alone
> supplies heritable variance; the finding is the magnitude, the asymmetry and the food/work split. "this is the
> response to imposed selection in this design; it is not a measurement of natural selection in the ecology (paper 5
> §2–§4)"; "realised h2 of this design only; not comparable with paper 5's parent–offspring r".
>
> (h2 is an index of this design (standing and new mutational variance mixed over 24 generations, eroded by drift
> and the Bulmer effect), not an estimate of a heritability. No before-and-after operator number exists for the
> holistic fauna: RBT-112's operator does not reach it.)

The designed body's two headlines, one per operator, are in `readout.txt` under "HEADLINES".

## 2. Verdicts (per fauna, per operator), and the controls

| comparison | verdict | divergence per generation (raw yield) | realised h2 |
|---|---|---|---|
| holistic (12 seeds, 2 replicates each) | **RESPONDS** | +0.095 [+0.083, +0.107] | 0.093 [0.080, 0.106] |
| designed body, default operator (12) | **RESPONDS** | +0.038 [+0.027, +0.048] | 0.067 [0.061, 0.074] |
| designed body, `--global-bias-sigma 0` (12) | **RESPONDS** | +0.036 [+0.028, +0.045] | 0.066 [0.061, 0.071] |
| operator comparison, designed body (Z − default, 12 pairs) | **NO CHANGE within ±0.05 σ0** | −0.001 [−0.012, +0.009] σ0 | |

- **No VOID.** All 24 seed directories passed every per-directory control:
  - configs;
  - per-generation worlds;
  - pairing;
  - pool membership of every parent;
  - the manipulation check;
  - an unselected control.

  The default-versus-Z operator pairing also held at every seed.
- **Sign-flip p values.** For every divergence (b_div) and realised h2 in the table, p = 2/4096 = 0.0005, the
  smallest attainable: all 12 units are positive. The one-sided responses are at p ≤ 0.003. `readout.txt` has them
  all.
- **The control lines** barely moved in the holistic fauna: b_C +0.0004 raw per generation [−0.0003, +0.0011]. In the
  designed body they drifted slightly down (−0.008 [−0.013, −0.002] under the default operator).

**The frozen σ0 reference** (`sigma0_reference.json`, D4): holistic 0.2212, designed body 0.7545, in raw yield
units. Later benchmarks report their rates against these values as well as their own.

## 3. What responded: the food/work decomposition (D1; generation 23, 4 fixed draws)

| | founders | U | D | C |
|---|---|---|---|---|
| **holistic** food (items) | 0.086 | **0.912** | 0.179 | 0.065 |
| holistic work cost (yield) | 0.033 | 0.143 | **1.522** | 0.029 |
| **designed** food, default operator | 0.786 | **1.224** | 0.061 | 0.769 |
| designed work cost | 0.582 | 0.575 | 0.925 | 0.645 |

**Holistic up line.** Selection made the holistic up line **learn to eat**: food rose about tenfold, from 0.09 to
0.91 items per season, while work cost rose a little. U − C is 88% food.

**Holistic down line.** Selection made the holistic down line **burn energy**: work cost rose about fiftyfold, while
food stayed where it was. C − D is 7% food. The holistic fauna's larger down response (b_down about twice b_up) is
almost entirely this.

**Designed body.** Its response is mostly food in both directions:
- U − D is 77% food;
- the down line stops eating (0.06 items).

**Summary.** The benchmark's single number for the holistic fauna mixes two things of very different interest:
- a real gain in foraging (the up line);
- a large, easily bought loss through wasted work (the down line).

Quote b_up with its food share when the question is "can evolution improve foraging here".

## 4. RBT-117: holistic against designed (registered before the readout; CONFIRMATORY)

**Verdict: HOLISTIC RESPONDS MORE.** d = D_holistic − D_designed, the final-generation U − D divergence in raw net
yield: mean **+0.77 [+0.40, +1.13]**, 11 of 12 seeds positive, exact sign-flip p = 0.0015. The C-line control
(+0.16 [−0.02, +0.33], p = 0.073) does not VOID it.

**Scope sentences, verbatim from `compare.py`:**
1. This compares the two populations as built: body, controller topology and mutation operator all differ between
   them. It does not test the variability mechanism in isolation.
2. RBT-113's D2 disclaimers apply: "this is the response to imposed selection in this design; it is not a
   measurement of natural selection in the ecology (paper 5 §2–§4)"; "realised h2 of this design only; not
   comparable with paper 5's parent–offspring r".
3. The primary quantity is in raw net-yield units, the currency both faunas are scored in: a larger raw response can
   come from more phenotypic variation, more heritability or both, or from the down line's room to lose yield by
   working harder, which differs between the bodies; the sigma0-unit line beside it is the per-unit-of-variation
   reading and is not scored.
4. Founder sigma0 here: holistic 0.2290, designed 0.7545. Reason (b)'s premise, that the holistic population is the
   more variable, does not hold on this trait; a designed win is not by itself evidence against the mechanism.

**How to read it.** This went against the registration's pre-data prediction (DESIGNED RESPONDS MORE). But the
printed halves and the decomposition show where the holistic margin comes from:
- **Up (U − C):** holistic +0.77, designed +0.66. These are close.
- **Down (C − D):** holistic +1.48, designed +0.82. This is where the margin is. The holistic down response is 93%
  work cost (flailing), which is scope sentence 3's third case.
- **Food alone:** the designed body's U − D food divergence (+1.16 items) is *larger* than the holistic's (+0.74).

So the holistic fauna responds more to imposed selection on net yield, mostly because its down line can waste far
more work.

**What it does not support.** It is not evidence for reason (b):
- the holistic founders were *less* variable (scope sentence 4);
- the margin is not in foraging.

## 5. What is claimed, and what is not

**Claimed:**
- **Both faunas respond to imposed truncation selection on solo net foraging yield,** in both directions, on every
  seed. At 12 seeds and 24 generations, for each:
  - realised h2 is 0.093 (holistic) and 0.067 (designed); these are indices of this design;
  - divergence is 0.095 and 0.038 raw yield per generation.
- **The holistic up line learns to eat** from random founders that almost never eat.
- **The holistic down response is mostly wasted work.**
- **Freezing the designed body's global biases (RBT-112's Z) does not change its response** in this benchmark: NO
  CHANGE within ±0.05 σ0 per generation. That is the before-and-after number, and it is for the designed body only.
- **RBT-117:** the holistic fauna's raw U − D divergence exceeds the designed body's, as registered. The margin is in
  the down line, as work.

**Not claimed:**
- anything about natural selection in the ecology;
- a heritability comparable with paper 5's r;
- an operator effect on the holistic fauna, which the operator does not reach;
- that the holistic fauna is more evolvable at foraging (in food it diverges less);
- support for reason (b)'s variability mechanism.

These are **readouts awaiting their adversary** (a fresh readout adversary reviews RBT-113 and RBT-117 together),
not ruled results.
