# RBT-125 §C / τ = 1 s readout adversary on #436 (partial)

*This reviews #436 (`results/RBT-125-gate-readout-bc` at 4d35f1f) under the coordinator's task of 02:29 UTC. It
covers the τ = 1 s cell, §C saturation, §C side effects and the eating-rule evidence. §B and the committed layouts
are still running and are not reviewed. Every number here is either a recomputation from #436's committed outputs,
or a run of the gate's own `side_effects.py` functions (`rod`, `season`, `cond_cfg`, `run`) on committed bodies from
`ckpt/rbt-90-801` and RBT-113's seed-1 founders.*

## Verdicts

| part | verdict |
|---|---|
| τ = 1 s cell | **CONFIRMED.** It reproduces to the digit |
| §C saturation | **CONFIRMED** (code read; the table's inputs are as registered) |
| §C side-effect *numbers* | **CONFIRMED.** Every row I re-ran reproduces exactly |
| **The eating-rule evidence behind the ruling (`root`, `surface` refused)** | **PARTLY OVERTURNED.** The +5.31 "surface exploit" is mostly a placement leak. The fauna asymmetry and solvency collapse under `root` come from the mouth being measured from the root's *centre*: `root` + `surface` removes them, and removes span just as well |

**MUST 1.** Before RBT-129 registers its eating rule, the coordinator should re-rule between `root` + centre (as
ruled) and `root` + surface, on the evidence in §2 below. Under the ruling as it stands (root + centre, living cost
not recalibrated), the designed founders start 12% solvent, against 30% committed. So the fauna gap the sweep
measures would partly be the rule's.

## 1. What reproduces

**The side-effects rows.** My runs use `side_effects.py`'s own functions and draws. Each row below matches
`side_effects.txt` to the printed digit:

| population | rule | this review | `side_effects.txt` |
|---|---|---|---|
| tumbler, U-G0 | committed / root / surface, 0.45 m | +0.75 / +0.70 / +1.45 | same |
| tumbler, U-G0 | committed / root / surface, 6.46 m | +0.71 / +0.36 / **+5.31** | same |
| tumbler, PW-G0 | committed / root / surface, 0.45 m | +0.55 / +0.50 / +0.80 | same |
| tumbler, PW-G0 | committed / root / surface, 6.46 m | +0.41 / +0.01 / +2.21 | same |
| corpus (801, season 600), U-G0 | committed / root, holistic | +0.835 / +0.548 (−28%) | same |
| corpus (801, season 600), U-G0 | committed / root, designed | +0.492 / −0.008 (−47%) | same |
| designed founders, U-G0 | committed / root | 0.653 / 0.372 items (−43%), solvent 0.30 / 0.12 | same |

**The asymmetric root cost is measured correctly.** "Items vs U-G0" is a ratio of fauna sums, over the living corpus
(survivor-weighted, as stated) and over the founders.

**The τ = 1 s cell** (`recompute_tau1.py` / `.txt`, the §A parser):
- prize +0.812 [+0.414, +1.210];
- motif − decoy +0.930 [+0.563, +1.297];
- τ1 − PW-G0 +0.687 [+0.296, +1.078];
- τ1 − τ2 +0.199 [+0.064, +0.333].

These are exact. Added here: τ1 − τ2 in *absolute* motif income is +0.202 [+0.102, +0.302], so τ = 1 s's advantage is
not produced by the base.

The ruling keeps τ = 2 s. That is defensible as registered, since the τ1 cell is descriptive and was run once.
**SHOULD 1:** record in RBT-129 that the only τ comparison on real bodies favours 1 s at this rung. The mechanism
READOUT-BC gives (a smaller common temporal term, so less of each tanh range is spent on it) matches
`probe_motion.txt`'s sech² gating.

**Saturation.**
- `saturation.py` wraps the simulator's own `_food_contrast` and records every food nose on every tick.
- It identifies the wheel noses by node (1, 2), as `routed_p801` does, and uses the §A bodies, with no motif and
  seeds 7000/7001, as registered.
- The table follows from that. I did not re-run all 980 seasons.
- The reading ("G = 10 saturates the individual noses, while L − R stays graded at the median") is supported.

## 2. The eating-rule evidence (`probe_tumbler_rules.txt`, `probe_corpus_rules.txt`)

### 2a. "`surface` is a new exploit (+5.31, 7×)" is mostly the placement leak

`side_effects.py` runs `surface` with the **default root clearance**. C1 established, and c591a75's fix confirms,
that under `surface` a limb's surface reaches spots that are clear of the root. The c591a75 fix applies only when
`clear_from = geoms`.

A **motors-off** rod, which cannot move, measures the leak directly (U-G0, net per season, 20 draws, SE in brackets):

| 6.46 m rod | moving | motors off (pure static reach) |
|---|---|---|
| committed (any / centre / root clearance) | +0.71 (0.23) | +0.10 |
| **any / surface / root clearance (the side-effects row)** | **+5.31 (0.87)** | **+2.10** |
| any / surface / geoms clearance (the fixed clearance) | **+1.91 (0.40)** | +0.10 |
| root / centre (ruled) | +0.36 (0.17) | 0 |
| **root / surface** | **+0.66 (0.25)** | 0 |

- About 2.1 items of the +5.31 are items placed within the arm's reach, which a rod with its motor off also eats.
- With the correct clearance, the sweep premium of `surface` in U is **+1.91 against +0.71**. That is real (about
  2.7×, well outside the SE), but it is not 7×.
- In PW, any / surface / geoms gives the long arm **+0.71 (0.57) against legacy +0.41 (0.35)**, which is **not
  resolved**. READOUT-BC's "+2.21, still 5× the PW baseline" is the leak again: the motors-off rod eats 1.15 there.
- **Refusing any-part `surface` still stands** on the U premium. The number and the mechanism in READOUT-BC must be
  corrected.
- **MUST 2 (code, small).** Under `eat_rule = surface`, the default `clear_from = root` still leaks: C1 was fixed
  only for `geoms`. Either make `surface` imply surface-distance clearance for any eating geom, or refuse
  `surface` with `clear_from = root` unless `eat_from = root`. With `eat_from = root`, the motors-off rod eats 0
  (above), because a compact root's surface reach (≈ 0.35 + 0.15–0.26 m) is inside the 0.8 m root clearance. An
  elongated root, if synthesis allows one at the fixed root volume, could still reach past 0.8 m. The safe fix is the
  first one: under `surface`, always clear by surface distance from the eating geoms.

### 2b. Is the sweeper exploit real on committed bodies? No

In the corpus and the founders, per body, span is the farthest geom point from the root centre:

| population | span, median [p90] | any / surface / geoms against committed, items | corr(per-body surface gain, span) |
|---|---|---|---|
| corpus, holistic (60) | 0.40 [0.48] m | −10% | +0.07 |
| corpus, designed (60) | 0.32 [0.32] m | −4% | −0.00 |
| designed founders (40) | 0.32 [0.32] m | −22% | (no span variance) |

- No committed body is a sweeper; the p90 span is under half a metre.
- On them, correctly cleared `surface` *lowers* income slightly (the surface clearance places food farther away), and
  the gain has no relation to span.
- The 6.46 m rod is a planted negative. The exploit it shows is a *capability of the rule* that evolution could find,
  which is a fair reason to refuse any-part `surface`. It is not something committed bodies do.

### 2c. The asymmetric root cost comes from measuring the mouth from the root's centre

The same bodies, U-G0, items per season (net), with the change against the committed rule:

| population | committed | **root / centre (ruled)** | **root / surface** |
|---|---|---|---|
| corpus, holistic | 1.021 (+0.835) | 0.733 (+0.548) **−28%** | 1.183 (+0.998) **+16%** |
| corpus, designed | 1.058 (+0.492) | 0.558 (−0.008) **−47%** | 1.188 (+0.620) **+12%** |
| designed founders | 0.653 (+0.074) | 0.372 (−0.207) **−43%** | 0.656 (+0.079) **+0%** |

Share solvent:

| population | committed | root / centre | root / surface |
|---|---|---|---|
| corpus, holistic | 0.82 | 0.70 | 0.83 |
| corpus, designed | 0.63 | **0.22** | 0.72 |
| designed founders | 0.30 | **0.12** | 0.38 |

- **Why it is asymmetric.** Under `root` + centre, the Pioneer's mouth is a 0.35 m disc around the chassis centre.
  Its committed eating width came from the wheels and casters that stand beside the chassis. Holistic roots are the
  hub their limbs grow from, and lose less. With the mouth measured from the root's *surface*, the chassis (0.42 m
  long) eats at its own edge, and the width comes back.
- **`root` + surface keeps every property the ruling wanted from `root`:**
  - span is removed. The long arm eats nothing, and the rod's income is the root cube's own: +0.66 in U (legacy
    +0.71) and **+0.06 in PW** (root / centre +0.01);
  - there is no static reach: motors-off 0 in U and PW;
  - no limb eats, so there is no sweeper exploit, and the nose loophole of `sensor` does not arise.
- **Its costs, to state if it is chosen:**
  - **The blind body's own coverage is paid a little more.** The short tumbler earns +1.30 (0.35) against +0.70
    (0.23) under root / centre and +0.75 committed, in U. In PW it is +0.80 (0.54) against +0.50: unresolved. This is
    the coverage lever that R4 and SYNTHESIS M4 leave to the work price and the layout, not to the eating rule.
  - **C4's terrain bias applies:** the item lies at z = 0, so a root raised on an obstacle reaches less.
- **The answer to "is it an artefact of the Pioneer's geometry that a different centre definition would remove?":
  yes.** The −47% / −28% gap and the fall to 12–22% solvency are properties of *centre* distance from the root.
  They are not properties of root-only eating.

## 3. The READOUT-BC text

**MUST 3.**
- Correct "`surface` is a new exploit … +5.31 a season … 7× its legacy income" and "PW … +2.21, still 5×". Both
  include the placement leak.
- Give the correctly cleared numbers: +1.91 in U (≈2.7×) and +0.71 in PW (unresolved).
- State that no committed body is a sweeper (the span table).

**SHOULD 2.** READOUT-BC says "a nose on the *arm* would restore the arm's sweep", but that was not measured. It
follows from `_eating_geoms`, so say so, or measure it.

**SHOULD 3.** Say explicitly that the ruling departs from READOUT-BC's own recommendation (recalibrating the living
cost per point), and give its consequence: with `root` + centre and no recalibration, the designed founders start at
12% solvent in U-G0.

**Confirmed as written:**
- the tumbler's `root` row (removes span, not the body's own coverage);
- `sensor` taxes noselessness;
- PW cuts coverage;
- the committed corpus is not viable in PW;
- the channel raises the designed founders' income (+44% items against PW-G0 in PW);
- births and depth are out of scope.

## Files (`runs/RBT-125/readout-adversary/`)

| file | what it does |
|---|---|
| `probe_tumbler_rules.py` / `.txt` | the tumbler, moving and motors-off, under 5 rule × clearance combinations in U-G0 and PW-G0, with `side_effects.py`'s own functions and draws |
| `probe_corpus_rules.py` / `.txt` | the corpus and the designed founders under committed, root / centre, any / surface / geoms and root / surface, with per-body span |
| `recompute_tau1.py` / `.txt` | the τ = 1 s cell, from the committed harness outputs |

All of them run in #436's tree, from `runs/RBT-125/gate` for the gate scripts, with bodies from `ckpt/rbt-90-801`.
