# RBT-125 world gate: readout

*Read under the coordinator's release of 01:15 UTC on 2026-09-28, which lifted no-peek for §A. §C and §B are added
here as they finish. The rules are those of `REGISTRATION.md` with amendments 1 and 2.*

## The audit trail

| event | when (UTC) | where |
|---|---|---|
| registration (§A–§D) | 2026-09-27 21:47:29 | 5749e97, pushed |
| amendment 1 (the 22:28 ruling) | 22:30:26 | 5f3c8e2, pushed |
| amendment 2 and the code fixes (the 22:45 ruling) | 22:42:02 | c591a75, pushed, and in #414 |
| the gate started (worktree pinned at c591a75) | 23:01:31 | `launch.txt` |
| tree parity written: every §A cell IDENTICAL | 23:02:58 | `parity.txt`, copied into `launch.txt` |
| first gate output (the harness check) | 23:06:45 | `prize/harness-801-uniform.txt` |
| §A computed | 01:11:47 | `launch.txt` |
| no-peek lifted for §A | 01:15 | the coordinator's release |

- Two earlier launchers were stopped before 23:01 (at 22:25 and 22:31), so no gate output predates either amendment.
- **Environment** (`launch.txt`): Linux x86_64, Python 3.11.15, mujoco 3.14.0, numpy 2.4.6 and scipy 1.17.1.
- **Code:**
  - the gate ran from `rabbitstew/` tree `2e2e505` (c591a75);
  - the parity reference is 0ec395f's tree, `81540b6`;
  - all 10 cells digest IDENTICAL.
- Integration's `simulation.py` has changed since, through a later merge. The gate ran on the pinned tree and is not
  affected.

## §A: the prize at a = 6 (`prize.txt`)

**The harness checks come first, and both are IDENTICAL to the digit:**
- RBT-103's seed-801 row: a = 32 +0.609, a = 64 +0.857, 7/7 bodies.
- RBT-106's HP-801 row, through `--config-from` with the decoy: a = 32 +0.879, a = 64 +2.355, 7/7 bodies.

**Every cell has all 10 populations readable, and all 70 of 70 bodies signed:**

| cell | n | prize at a = 6, t(9) 95% | base income | motif − decoy, t(9) 95% | decoy retains | zero pairs |
|---|---|---|---|---|---|---|
| **PW-G2.5** | 10/10 | **+0.614 [+0.276, +0.951]** | 1.049 | **+0.702 [+0.413, +0.991]** | −14% | 2861/4480 |
| PW-G10 | 10/10 | +0.708 [+0.381, +1.034] | 1.056 | +0.912 [+0.654, +1.169] | −29% | 2806/4480 |
| PW-G0 (legacy) | 10/10 | +0.125 [+0.056, +0.194] | 1.118 | +0.167 [+0.050, +0.284] | −33% | 3345/4480 |

**The channel's own contribution**, (cell − PW-G0) paired by population, t(9):

| contrast | all bodies | bodies signed the same in both cells |
|---|---|---|
| **PW-G2.5 − PW-G0** | **+0.488 [+0.155, +0.822]** | +0.526 [+0.155, +0.897] (10 populations) |
| PW-G10 − PW-G0 | +0.582 [+0.255, +0.910] | +0.676 [+0.310, +1.042] (10 populations) |

**GATE VERDICT: PASS at G = 2.5, and the channel pays.**
- At the registered G, the world pays an installed compass at a = 6 through a food-dependent mechanism: the prize's
  lower bound is +0.28, and motif − decoy's is +0.41, over all 10 populations.
- The channel is responsible for most of it: the paired contrast against the legacy reading has a lower bound of
  +0.16.
- **The fallback to G = 10 was not used.** The familywise one-sided α over the two registered shots is at most 5%.

### Per population (PW, items per season at a = 6; a population's prize is its mean over its 7 bodies)

| seed | PW-G2.5 prize | motif − decoy | PW-G10 prize | motif − decoy | PW-G0 prize | motif − decoy | base, PW-G2.5 |
|---|---|---|---|---|---|---|---|
| 801 | +0.730 | +0.929 | +0.911 | +1.159 | +0.107 | +0.390 | 1.261 |
| 804 | +0.491 | +0.712 | +0.960 | +1.264 | +0.103 | +0.206 | 1.145 |
| 805 | +1.049 | +0.940 | +1.181 | +1.025 | −0.009 | +0.109 | 0.902 |
| 806 | +0.683 | +0.739 | +0.621 | +0.677 | +0.185 | +0.125 | 0.902 |
| 807 | −0.054 | +0.288 | −0.060 | +0.411 | +0.181 | +0.299 | 1.393 |
| 1 | +0.438 | +0.878 | +0.393 | +0.837 | +0.216 | +0.032 | 1.270 |
| 2 | +0.121 | −0.071 | +0.063 | +0.314 | −0.069 | −0.174 | 1.002 |
| 3 | +0.156 | +0.350 | +0.681 | +0.842 | +0.143 | +0.103 | 1.085 |
| 4 | +1.170 | +0.942 | +1.080 | +1.332 | +0.228 | +0.284 | 0.701 |
| 7 | +1.353 | +1.315 | +1.248 | +1.255 | +0.167 | +0.296 | 0.828 |

### What §A does and does not say

- **PW-G0 also passes, by the world rule.** The legacy reading pays the installed compass +0.125 [+0.056, +0.194] at
  a = 6, with (motif − decoy) +0.167 [+0.050, +0.284].
  - RBT-121 audit C predicted no pass at a = 6 without the contrast, so that prediction is wrong on real bodies. The
    PW layout alone already makes a weak, installed compass pay a little.
  - The contrast multiplies that prize by about 5 (+0.614 against +0.125). **That multiplication, not the pass
    itself, is what M1's paired test attributes to the channel.**
- **G = 10 is not worse at this rung.** G10 − G2.5, paired by population, is +0.094 [−0.072, +0.260]. That comparison
  was not registered, so it is descriptive.
  - The saturation and approach-speed caveats at G = 10 (sech²: L − R falls to about 7% of its static value at
    0.25 m/s and 45° toward the food; DESIGN §1) are about the *step* path, meaning later steps and the steering of a
    body already approaching.
  - The prize at one installed weight does not test them. §B and the saturation readout (§C) do.
- **The decoy retains a negative share at every cell.** The rotated decoy *costs* income (the mean decoy − base is
  −0.09 at G2.5 and −0.20 at G10). A steerer that follows a rotated field is pulled away from the food.
  - So motif − decoy exceeds the prize itself. The FOOD-DEPENDENT reading is conservative in the prize column and
    generous in the (motif − decoy) column. Both lower bounds are > 0.
- **The channel lowers these evolved bodies' own base income in PW** (1.049 at G2.5 and 1.056 at G10, against 1.118
  under legacy smell). The RBT-90 bests carry evolved wiring on their food sensors, and the contrast changes what that
  wiring reads. This is an R6 side effect; §C measures it on founders and the corpus.
- **The per-population harness verdicts are not used.** 64% of pairs tie at G2.5 (2861/4480), so RBT-38's zero-count
  veto fires almost everywhere in PW. The t bound over populations is the registered statistic.
- **Scope.** The motif is installed; it is a planted positive. §A shows that the world and the channel pay a compass
  that exists, at a weight evolution has reached. It does not show that a compass evolves, or that the step path to
  it pays. That is §B's question, and the sweep's.
- **The τ = 1 s sensitivity cell** (PW-G2.5-tau1, descriptive) is running. It is added below when finished.

## §A, sensitivity: τ = 1 s (descriptive)

*Pending.*

## §C: saturation and the R6 side effects

*Pending. It runs after the τ cell. Births and depth are out of scope: the seasons are solo.*

## §A: the committed layouts (HP, U at G ∈ {2.5, 10, 0})

*Pending.*

## §B: a nose step against a +25% speed step (descriptive; expected TIED, UNRESOLVED)

*Pending. It runs last.*

## Files

- `launch.txt`: the launch record (commit, both tree hashes, platform, parity).
- `parity.txt`: the per-cell tree parity.
- `prize.txt`: the §A readout (`prize_readout.py`). It is re-rendered with every cell at the end.
- `prize/<cell>-<seed>.txt`: the harness output per cell and population. `.err` holds MuJoCo's warnings.
- `prize/harness-801-{uniform,HP}.txt`: the two harness checks.
