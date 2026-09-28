# RBT-125 world gate: readout of the τ cell, §C, the committed layouts and §B

*This is the follow-up to #430 (§A, merged), per the coordinator's ruling of 01:31 UTC. The rules are
`REGISTRATION.md` with amendments 1 and 2. The parts are added as they finish. They all come from the same launch
as §A: the worktree pinned at c591a75, started at 23:01:31, with the parity result in `launch.txt`.*

## τ = 1 s sensitivity (PW-G2.5-tau1; descriptive)

The cell is PW at G = 2.5 with `smell_tau` = 1 s, the value in RBT-116's draft. All 10 of 10 populations are
readable, and 70 of 70 bodies are signed.

| quantity | t(9) 95% |
|---|---|
| prize at a = 6 | +0.812 [+0.414, +1.210] |
| motif − decoy | +0.930 [+0.563, +1.297] (the decoy retains −14%) |
| τ1 − PW-G0, paired (the channel's contribution) | +0.687 [+0.296, +1.078] |
| **τ1 − τ2 (PW-G2.5), paired** | **+0.199 [+0.064, +0.333]** |

- The base income is 1.052, and 2822 of 4480 pairs tie.
- **At this rung, τ = 1 s pays the installed compass more than the registered τ = 2 s,** and the interval excludes 0.
- **This is descriptive, and it does not change the registered transform.**
  - The 22:28 ruling kept τ = 2 s and had RBT-116 amended to match.
  - Whether to move τ is the coordinator's call. It would need a new registration, because this cell was run as a
    sensitivity check, not as a comparison.
- **A plausible mechanism**, consistent with the saturation table below: a shorter baseline tracks the noses' mean
  faster, so the common temporal term is smaller, and less of each nose's tanh range is spent on it.
  - The median |c| is 0.27 at τ = 1 s, against 0.37 at τ = 2 s.
  - The median |c_L − c_R| is 0.35 against 0.29.

## §C, saturation (`saturation.txt`)

This is the registered readout: the median and p90 of |c| over every food nose and every tick. It uses the §A bodies
(70 designed bests × 2 seasons, seeds 7000 and 7001), as they are, with no motif.

| cell | median \|c\| | p90 \|c\| | share \|c\| > 0.9 | median \|c_L − c_R\| | p90 \|c_L − c_R\| |
|---|---|---|---|---|---|
| PW-G2.5 | 0.368 | 0.862 | 0.077 | 0.292 | 0.529 |
| PW-G10 | 0.887 | 1.000 | 0.486 | 0.325 | 1.505 |
| PW-G2.5-tau1 | 0.270 | 0.703 | 0.024 | 0.349 | 0.549 |
| HP-G2.5 | 0.384 | 0.933 | 0.127 | 0.255 | 0.631 |
| HP-G10 | 0.923 | 1.000 | 0.530 | 0.248 | 1.579 |
| U-G2.5 | 0.398 | 0.923 | 0.116 | 0.326 | 0.677 |
| U-G10 | 0.916 | 1.000 | 0.526 | 0.353 | 1.697 |

- **G = 10 saturates the individual noses on real bodies.**
  - About half of all readings exceed 0.9, and the median is about 0.9 in every layout. This confirms adversary §6b
    (median 0.56–0.64 and p90 0.93–0.95 there) and puts it higher.
  - The wheel difference |c_L − c_R| is still graded at the median (0.25–0.35), but its p90 reaches 1.5–1.7, close
    to the maximum of 2.
- **At G = 2.5, the median |c| is about 0.37–0.40, and 8–13% of readings exceed 0.9.** It sits mostly in the graded
  range.
- Together with §A (G10 not detectably worse than G2.5 at a = 6), this says the G = 10 cost, if there is one, lies in the step
  path and in the evolved wiring the nose feeds. It does not lie in an installed compass's prize. §B tests the step
  path.

## §C, the R6 side effects (`side_effects.txt`)

*The seasons are solo, so births and realised depth are out of scope (amendment 1, A1.7). The full tables are in
`side_effects.txt`, and the rows that decide things are below. Net = items − 0.03 × kJ, and the living cost is 0.25
per season.*

### Founders (RBT-113 seed 1, generation 0; 40 per fauna × 8 draws)

- **The holistic founders earn essentially nothing in every condition.** Their mean is 0.00–0.03 items, and no more
  than 3% of them are solvent anywhere. So every rule's relative effect on them ("+150%", "−100%") is a change of one
  or two items over 320 seasons. It is noise, and it cannot rank the rules.
- **The designed founders:**

| condition | items | net | solvent | items vs U-G0 |
|---|---|---|---|---|
| U-G0 (committed) | 0.653 | +0.074 | 0.30 | — |
| U-G2.5 | 0.691 | +0.127 | 0.40 | +6% |
| U-G0 / root | 0.372 | −0.207 | 0.12 | **−43%** |
| U-G0 / sensor | 0.634 | +0.056 | 0.30 | −3% |
| U-G0 / surface | 0.703 | +0.125 | 0.45 | +8% |
| U-G0 / clear-geoms | 0.494 | −0.084 | 0.25 | −24% |
| PW-G0 | 0.362 | −0.206 | 0.25 | −44% |
| **PW-G2.5** | 0.522 | −0.043 | 0.35 | −20% |
| PW-G2.5 / root | 0.344 | −0.222 | 0.23 | −47% (−34% against PW-G2.5) |
| PW-G2.5 / sensor | 0.531 | −0.033 | 0.35 | −19% (+2% against PW-G2.5) |

**Findings:**
- **The channel raises the designed founders' income.** In U it is +6% items and +0.05 net. In PW it is +44% items
  against PW-G0 (0.522 against 0.362), and the solvent share goes from 0.25 to 0.35.
- **PW is a poor world for founders** even with the channel: the net is −0.04, and only 35% are solvent. A PW point
  needs its living cost recalibrated (the sweep's habitability census).

### The committed corpus (RBT-90 part 2, seed 801, the living at season 600; 60 per fauna × 4 draws)

| condition | holistic net (÷ cost) | designed net (÷ cost) | holistic items vs U-G0 | designed items vs U-G0 |
|---|---|---|---|---|
| U-G0 (committed) | +0.835 (3.34) | +0.492 (1.97) | — | — |
| U-G2.5 | +0.863 (3.45) | +0.623 (2.49) | +2% | +12% |
| U-G10 | +0.810 (3.24) | +0.608 (2.43) | −3% | +11% |
| PW-G0 | +0.136 (0.54) | −0.332 (−1.33) | −69% | −78% |
| PW-G2.5 | +0.036 (0.15) | −0.419 (−1.67) | −78% | −87% |
| U-G0 / root | +0.548 (2.19) | −0.008 (−0.03) | **−28%** | **−47%** |
| U-G0 / sensor | +0.631 (2.52) | +0.416 (1.67) | −20% | −7% |
| U-G0 / surface | +1.140 (4.56) | +0.650 (2.60) | +30% | +15% |
| U-G0 / clear-geoms | +0.669 (2.67) | +0.282 (1.13) | −16% | −20% |

These are survivor-weighted, because they are the living. **Findings:**
- **In the committed world the channel shifts the regime toward saturation**, mostly for the designed fauna:
  designed net ÷ cost goes from 1.97 to 2.49, and holistic from 3.34 to 3.45.
- **The committed corpus is not viable in PW**, with or without the channel. Its bodies evolved in U.
  - With the channel, the designed fauna's items fall further (−87% against −78%). The bodies' evolved food-sensor
    wiring reads the contrast differently. §A's base-income contrast on the RBT-90 bests (−0.069, unresolved) points
    the same way.
  - **Any PW point needs its own founders and its own living cost**, not the committed corpus.
- **`root` costs the designed fauna more than the holistic one:** −47% against −28% in the corpus, and −43% in the
  designed founders. The Pioneer loses the footprint of its wheels and casters. The corpus Pioneers fall to net ≈ 0,
  with 78% of them below the living cost.
- **`surface` raises everyone's income.** See the tumbler below. These rows were first measured before #446;
  the founder and corpus `surface` rows and every `root` + `surface` row were re-run on the fixed code (next
  subsection). The corpus U-G0 / surface row and the designed founders' U-G0 / surface row reproduce to the digit on
  it: the minimal guard did not bind on those draws.

### The blind tumbler (RBT-121 adversary §7; one full-throttle hinge, no sensor, 20 draws)

| arm | U-G0 | root | sensor | sensor + an unused root nose | surface | clear-geoms | PW-G0 | PW root | PW surface |
|---|---|---|---|---|---|---|---|---|---|
| 0.45 m | +0.75 | +0.70 | −0.15 | +0.70 | +1.45 | +0.70 | +0.55 | +0.50 | +0.80 |
| 6.46 m | +0.71 | +0.36 | −0.09 | +0.36 | ~~+5.31~~ **+2.96** | +0.46 | +0.41 | **+0.01** | ~~+2.21~~ **+1.71** |

(Net per season; the SE is about 0.2–0.4, and 0.5–0.7 for the long sweeper under `surface`.)

**Correction, per the §C readout adversary (#445).** The struck `surface` values were measured before #446, when a
limb's surface could reach food placed clear of the root's centre. That was a clearance leak, not the surface rule
itself. The corrected values come from `side_effects_surface.txt`, run on integration 01f113d with #446's minimal guard
merged. That run reproduces every non-surface row here to the digit (U-G0, U-G0/root and PW-G2.5 for founders; U-G0
and the sensor + root-nose rows for the tumbler).

- **`root` removes span:** the 6.46 m arm falls from +0.71 to +0.36 in U, and to +0.01 in PW. It does **not** remove
  the tumbling body's own coverage: the short arm is unchanged, at +0.70. This is as DESIGN §2 said: the rules stop
  span, and not coverage.
- **`sensor` taxes noselessness, not coverage.** The noseless tumbler earns nothing. **One unused nose on its root
  restores exactly its root-rule income** (+0.70 and +0.36).
  - And, by the rule's own definition, a nose on the *arm* would restore the arm's sweep. That is the "pays
    nose-carrying for its own sake" loophole of the RBT-116 adversary §2.3.
- **`surface` alone still pays a long arm's length.**
  - With the leak closed, the long sweeper nets +2.96 a season in U (4× legacy) and +1.71 in PW, because the whole
    length of the arm eats.
  - Under `root` + `surface` only the root eats, and that span disappears: +0.66 in U, and +0.06 in PW (below).
- **`clear_from = geoms`** trims the long arm (from +0.71 to +0.46) by removing static reach. It is secondary to
  `root`.
- **PW itself cuts coverage:** the short tumbler goes from +0.75 to +0.55, and the long one from +0.71 to +0.41. Only
  `root` + PW together brings the long sweeper to zero.

### `root` + `surface`, on the fixed code (`side_effects_surface.txt`; integration 01f113d, #446 merged)

This is the coordinator's re-ruled eating rule (03:10). The designed founders' solvency under it is **0.38**, exactly
#445's figure, so the STOP condition (well below 0.38) is not met.

| rows | condition | holistic | designed |
|---|---|---|---|
| founders: items / net / solvent | U-G0 (legacy) | 0.013 / −0.012 / 0.00 | 0.653 / +0.074 / 0.30 |
| | U-G0 / root (centre) | 0.003 / −0.021 / 0.00 | 0.372 / −0.207 / 0.12 |
| | **U-G0 / root + surface** | 0.009 / −0.015 / 0.00 | **0.656 / +0.079 / 0.38** |
| | PW-G2.5 | 0.006 / −0.017 / 0.00 | 0.522 / −0.043 / 0.35 |
| | **PW-G2.5 / root + surface** | 0.006 / −0.017 / 0.00 | **0.512 / −0.052 / 0.33** |
| corpus: net (÷ cost) | U-G0 (legacy) | +0.835 (3.34) | +0.492 (1.97) |
| | **U-G0 / root + surface** | +0.998 (3.99) | +0.620 (2.48) |
| | PW-G2.5 / root + surface | +0.065 (0.26) | −0.314 (−1.26) |

| tumbler, net | legacy | root (centre) | **root + surface** | surface alone |
|---|---|---|---|---|
| 0.45 m, U | +0.75 | +0.70 | **+1.30** | +1.40 |
| 6.46 m, U | +0.71 | +0.36 | **+0.66** | +2.96 |
| 0.45 m, PW | +0.55 | +0.50 | **+0.80** | +0.80 |
| 6.46 m, PW | +0.41 | +0.01 | **+0.06** | +1.71 |

**What root + surface does:**
- **It restores the designed founders to their legacy income and solvency** (0.656 items; 0.38 against 0.30 legacy
  and 0.12 under root + centre).
  - The Pioneer's chassis surface reaches about as far as its wheels and casters did under the centre rule, so the
    mouth-geometry tax of root + centre goes away. This is #445's point, and it holds on the fixed code.
- **It still removes span:** in PW the long arm earns nothing more than its root's own path.
- **It does not remove, and in fact raises, a compact tumbler's blind coverage.**
  - The short tumbler goes from +0.75 to +1.30 in U, and from +0.55 to +0.80 in PW. The surface rule adds the root
    cube's half-size (about 0.15 m) to its reach.
  - The same holds in the corpus: in U, holistic net ÷ cost rises from 3.34 to 3.99 and designed from 1.97 to 2.48.
    So root + surface moves the committed world further toward saturation.
  - **The work price and the layout remain the only levers against blind coverage.** PW brings the short tumbler down
    to +0.80.
- **The holistic founders earn about 0 under every rule** (≤ 0.03 items), so they still cannot rank the rules.

### The eating-rule recommendation for the sweep (RBT-129): superseded by the ruling

*My first recommendation (02:26) was `--eat-from root` with the centre rule, as below. The coordinator re-ruled it at
03:10, on #445, to **`--eat-from root --eat-rule surface`**, with #446's minimal guard. The rows above confirm the
re-ruled rule's R6 side effects on the fixed code. The earlier reasoning is kept for the record.*

**`--eat-from root`, with the centre rule and the root clearance** (both left at their defaults). `surface` is
refused. **The price of `root` must be stated at registration, and the living cost recalibrated per point.**

**Why root:**
- It is the only rule that removes span without creating a new loophole.
  - `sensor` hands span back to any limb that carries a nose. The tumbler rows show that a nose buys eating
    capacity.
  - `surface` multiplies a long sweeper's income 7-fold.
- Under root, the mouth is where the body is, which is what steering has to move.

**Its cost, which is the R6 side effect to carry into the sweep:**
- It falls harder on the Pioneer than on holistic bodies: the designed corpus loses 47% against the holistic
  corpus's 28%, and the designed founders lose 43%.
- In both the committed world and PW, the designed founders' solvency drops to 12–23%.
- So with root on, **every sweep point must recalibrate the living cost to the founders' root-eating income**, and
  report the fauna gap as a result of the rule, not of the bodies.
- It does **not** stop blind coverage by the body itself. The work price and the layout remain the levers for that.

**Recorded for the ruling:** `clear_from = geoms` is not needed with root. Only the root eats, and clearance is
already measured from the root.

## §A, the committed layouts (HP and U at G ∈ {2.5, 10}, then G = 0; `prize.txt`, final re-render)

The registration runs these cells without the decoy, so there is no motif − decoy column. They are not gate cells.
They say what the channel does to an installed compass's prize in the committed worlds. All 10 of 10 populations are
readable in every cell.

| cell | bodies signed | prize at a = 6, t(9) 95% | base income | the channel: cell − its G0, paired | the same, on bodies signed alike |
|---|---|---|---|---|---|
| HP-G2.5 | 69/70 | +0.962 [+0.435, +1.489] | 1.532 | **+0.797 [+0.314, +1.279]** | +0.866 [+0.304, +1.428] |
| HP-G10 | 68/70 | +1.035 [+0.582, +1.489] | 1.495 | +0.870 [+0.471, +1.269] | +1.019 [+0.537, +1.502] |
| HP-G0 | 70/70 | +0.166 [+0.066, +0.265] | 1.531 | — | — |
| U-G2.5 | 70/70 | +0.497 [+0.292, +0.702] | 1.196 | **+0.395 [+0.204, +0.586]** | +0.425 [+0.222, +0.628] |
| U-G10 | 69/70 | +0.502 [+0.266, +0.738] | 1.166 | +0.400 [+0.144, +0.656] | +0.532 [+0.287, +0.777] |
| U-G0 | 69/70 | +0.101 [+0.016, +0.187] | 1.308 | — | — |

- The unsigned bodies (806, 801 and 1 in HP; 807 and 2 in U) leave both the numerator and the denominator, per the
  harness. That U-G0 leaves seed 2's g0 undetermined matches RBT-103 in the same world.

**Findings (descriptive; amended per the readout adversary's pass 1, #458):**
- **The channel raises the installed compass's prize in every layout**, not only in PW. The paired contrast's lower
  bound is > 0 in HP and U at both G.
  - **HP and U have no decoy** (by registration), so there the gain is *not shown to be food-dependent*. Only PW's is.
  - **Which layout the channel pays most is resolved only for HP.** Channel contributions at G2.5, paired by
    population:

    | contrast | t(9) 95% |
    |---|---|
    | HP − PW | +0.308 [+0.080, +0.536] |
    | HP − U | +0.401 [+0.050, +0.752] |
    | **PW − U** | **+0.093 [−0.127, +0.314] (unresolved)** |

    So HP pays most, resolved against both PW and U; PW against U is unresolved. The legacy G0 prizes' ranking is not
    resolved at a = 6 either. *Conjecture, not shown:* the channel scales with what a layout already rewards.
  - **In absolute income (base + prize), (cell − G0)**, since U's base falls under the channel:

    | layout | G2.5 | G10 |
    |---|---|---|
    | U | +0.283 [+0.122, +0.444] | +0.258 [+0.005, +0.511] |
    | HP | +0.798 [+0.412, +1.183] | +0.833 [+0.447, +1.220] |
    | PW | +0.420 [+0.158, +0.682] | +0.520 [+0.253, +0.787] |

- **At a = 6 the legacy reading pays a little in every layout** (+0.10 to +0.17, all with lower bounds > 0).
  - **U-G0 passing, +0.101 [+0.016, +0.187], is audit C's second failed prediction** ("at a = 6 in the committed HU it
    should not", AUDIT L451). PW-G0 passing (§A, #430) was the first.
  - The installed weight registers without the contrast. What the contrast changes is the size.
- **G = 10 is not detectably worse than G = 2.5 in either committed layout:**
  - HP: G10 − G2.5 is +0.073 [−0.078, +0.225];
  - U: G10 − G2.5 is +0.005 [−0.112, +0.122].

  As in PW, no saturation cost of G = 10 is detectable at an installed weight. The saturation table puts it in the
  noses, and §B asks whether it shows on the step path.
- **The base income falls under the channel in U, and the fall is resolved:** base (G) − base (G0), paired, is
  −0.113 [−0.213, −0.013] at G2.5 and −0.142 [−0.259, −0.025] at G10.
  - It is unresolved in PW (−0.069 [−0.198, +0.060]) and flat in HP (+0.001 [−0.264, +0.266]).
  - The cause is the RBT-90 bests' own evolved food-sensor wiring reading a different signal (the R6 side effect of
    §A). The absolute-income contrasts above include it.

## §B: a nose step against a +25% speed step (descriptive; expected TIED, UNRESOLVED)

*Pending. It runs last, at 128 seeds per host.*

## Output timestamps (UTC, gate worktree)

- `prize/HP-G2.5-801.txt` 2026-09-28 02:27:40Z
- `prize/U-G0-7.txt` 2026-09-28 05:43:24Z
- `prize.txt` (final re-render) 2026-09-28 05:43:26Z

- `side_effects_surface.txt` 2026-09-28 04:17Z (the scratchpad worktree at integration 01f113d, not the gate's pinned tree)

- `side_effects.txt` 2026-09-28 02:24:55Z

- `saturation.txt` 2026-09-28 01:52:53Z
- `prize/PW-G2.5-tau1-1.txt` 2026-09-28 01:35:07Z
- `prize/PW-G2.5-tau1-2.txt` 2026-09-28 01:38:55Z
- `prize/PW-G2.5-tau1-3.txt` 2026-09-28 01:42:49Z
- `prize/PW-G2.5-tau1-4.txt` 2026-09-28 01:46:44Z
- `prize/PW-G2.5-tau1-7.txt` 2026-09-28 01:50:32Z
- `prize/PW-G2.5-tau1-801.txt` 2026-09-28 01:15:46Z
- `prize/PW-G2.5-tau1-804.txt` 2026-09-28 01:19:40Z
- `prize/PW-G2.5-tau1-805.txt` 2026-09-28 01:23:29Z
- `prize/PW-G2.5-tau1-806.txt` 2026-09-28 01:27:19Z
- `prize/PW-G2.5-tau1-807.txt` 2026-09-28 01:31:10Z
