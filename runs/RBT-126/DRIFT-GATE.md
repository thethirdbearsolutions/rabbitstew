# RBT-126 item 4: the drift arm's breeding gate

**Summary.**
- **In a `--neutral` arm, the test `energy >= birth_threshold` (`ecology.py:524`) bars children as well as founders.**
  - A **founder** starts at `initial_energy`, 3.0 (`:212`), so it is barred while its cumulative gain is below −3.
    This is the case RBT-121 ADVERSARY "also noticed" describes.
  - A **child** starts at `birth_cost` (`:539`), which is **0** in a neutral arm, so it is barred **from its first
    net-negative season**.
  - Children are about 91% of the lives in a 600-season arm, so most of the gate's bite is on them.
- **How often it bit:**
  - **RBT-80's drift arms: not measurable.** No lineage is committed and none is on a checkpoint branch (REGIME.md).
  - **RBT-99 has no drift arm.** Every one of its 20 arms runs the full economy (threshold 3).
  - **The committed threshold-0 arms with per-life data are RBT-71's neutral-804, 805 and 806.** There the gate
    barred:
    - designed fauna: **16–19% of member-seasons**, and 13–17% of all lives at their last season;
    - holistic fauna: **8–9% of member-seasons**.
  - **On RBT-99's own bodies and prices,** the share of births whose lifetime income is negative, i.e. who would be
    barred from their first seasons in a drift arm, is:
    - designed: 0.24 before the shift and 0.34 after it (to work cost 0.08);
    - holistic: 0.22 and 0.24.
- **Effect on a retention floor, in the replica at RBT-80's numbers:**
  - Non-carriers scoring −0.02 a season: the gate holds carriage at **0.914** where no gate gives **0.553**.
  - Non-carriers scoring +0.08, which is RBT-80 seed A's plateau non-carrier mean: **0.736** against **0.552**.
  - So the "no-selection" comparator is not free of selection wherever the lost trait leaves its bearer near or
    below zero net.
- **Proposed fix (a design only):** a flag `--breed-gate none`, off by default, allowed only with `--neutral`. It
  takes every living evaluated member as a breeder.

## Why the gate bites children at zero, not at −3

In `Ecology.step`, a neutral arm (`--neutral`, `cli.py:354-355`) sets `starvation False`, `birth_threshold 0`,
`birth_cost 0` and `living_cost 0`. Then:

- **Every member's energy is its starting energy plus its cumulative gross gain.** Gross gain is food minus work, and
  there is no living cost.
- **Founders start at `initial_energy`** (`ecology.py:212`): 3.0 in RBT-65, 71 and 80.
- **Children start at `eco.birth_cost`** (`ecology.py:539`): 0.0.
- **Breeders are `energy >= 0`** (`:524`). A child is therefore barred in every season its cumulative gain is
  negative.
  - This is not a "flailer" edge case. A holistic body that earns almost nothing, −0.003 a season, is barred for
    life.
  - The median lifetime income of RBT-71's barred holistic lives is **−0.002 to −0.006**.
- **The CLI's help text for `--neutral`** reads "free breeding (threshold and cost 0)". Breeding is free of *cost*,
  but it is not free of the gate.

## Measured: RBT-71's neutral arms (`drift_gate.py actual`, in `drift_gate.txt`)

These arms have threshold 0 and random founders, over 600 seasons, in the same world family as RBT-80 and RBT-99.
Only `lineage-last.txt` is committed, and there is no checkpoint branch, so the readings work as follows:
- **Barred at the last season** is exact: a life's final cumulative gain is `fitness × evals`.
- **Member-seasons barred** assumes a constant per-season rate for each life. A child with negative income counts
  every season. A founder counts from season ⌈3/|m|⌉ on.

| arm | fauna | founders barred at their last season | children barred at their last season | member-seasons barred (est.) | median income of the barred |
|---|---|---|---|---|---|
| neutral-804 | designed | 18 / 58 (0.31) | 115 / 599 (0.19) | **0.193** | −0.214 |
| neutral-805 | designed | 16 / 60 (0.27) | 103 / 598 (0.17) | **0.172** | −0.179 |
| neutral-806 | designed | 14 / 59 (0.24) | 94 / 599 (0.16) | **0.156** | −0.218 |
| neutral-804 | holistic | 1 / 58 (0.02) | 49 / 599 (0.08) | **0.078** | −0.003 |
| neutral-805 | holistic | 3 / 59 (0.05) | 50 / 600 (0.08) | **0.084** | −0.006 |
| neutral-806 | holistic | 1 / 58 (0.02) | 51 / 597 (0.09) | **0.085** | −0.002 |

- **In a neutral arm, births are fixed by deaths,** and deaths are by age alone. So the gate does not change the
  number of births or the depth. It changes **who** parents: the barred members' share of parentage goes from their
  share of the living to zero.
- **For the designed fauna this is 16–19% of the living** on the average season. It is not "small for the designed
  body", as ADVERSARY guessed: the wheeled body's work cost makes a do-little brain net-negative.

## Counterfactual: RBT-99's bodies and prices (`drift_gate.py counterfactual`)

**RBT-99 has no threshold-0 arm.** Its committed arms cannot show the gate either, because with a living cost a
net-negative member starves long before it matters.

What can be read is the share of the **children born** in a window whose lifetime income is negative. A drift arm run
on the same bodies and prices would bar such children from their first seasons. The medians over seeds, from
`drift_gate.txt` (every birth, windows with ≥ 30 births), are:

| fauna | before [T−100, T) | recovery [T+60, T+160) (work cost 0.08) |
|---|---|---|
| designed | 0.237 [0.185, 0.301] (10 seeds) | 0.337 [0.256, 0.390] (8 seeds) |
| holistic | 0.217 [0.170, 0.296] (10 seeds) | 0.239 [0.191, 0.292] (10 seeds) |

**This over-reads.** A child that lives one season has a lifetime income of one noisy draw.
- **Restricted to lives of ≥ 10 seasons,** the share is 0.000 on every seed and window. The committed sieve starves
  every net-negative life before its tenth season, so that restriction under-reads to zero.
- **RBT-71's measured 16–19% (designed) and 8–9% (holistic)** sit inside this bracket.

## Effect on a retention floor, in the replica (`retention_gate.txt`)

This uses RBT-80's numbers:
- carriers score 0.95 (gross 1.05);
- erosion u = 0.06 a birth;
- 300 seasons, 400 replicates.

The drift economy is run with the committed gate and without it.

| non-carrier score a season | carriage, committed gate | carriage, no gate |
|---|---|---|
| −0.10 | 0.937 ± 0.002 | 0.563 ± 0.009 |
| −0.02 | 0.914 ± 0.002 | 0.553 ± 0.009 |
| **+0.08 (RBT-80 seed A's plateau non-carriers)** | **0.736 ± 0.007** | **0.552 ± 0.010** |
| +0.20 | 0.618 ± 0.009 | 0.544 ± 0.009 |
| +0.47 | 0.577 ± 0.009 | 0.570 ± 0.009 |

- **Without the gate, the drift floor is flat at 0.55,** whatever the non-carriers earn. That is what a no-selection
  comparator is for.
- **With the gate, a drift arm retains a trait whose loss leaves its bearer near zero net.**
- **Even at +0.08 a season the gate lifts carriage by +0.18.**
  - A child starts at 0.
  - A non-carrier's Poisson income scores −0.1 in 84% of seasons.
  - So its cumulative score is negative for much of its life, although its mean is positive.
- **These are replica figures.** RBT-80's actual drift arms carry an unmeasured share of this.
  - Their compass-seeded designed founders had arm mean scores of about 1.0 early, falling to 0.05–0.47 by seasons
    290–299 (`RBT-80-series.txt`).
  - RBT-80's drift retention was 0.71 / 0.75 / 0.64 against a computed operator floor of 0.681. Those are its
    committed numbers, not re-read here.

## The fix (a design; no code in `rabbitstew/` here)

**The flag.**
- `EcologyConfig.breed_gate: str = "energy"`, CLI `--breed-gate {energy,none}`.
- **`energy`** is today's code path, byte-identical. That keeps RBT-65, RBT-71 and RBT-80's drift arms
  reproducible.
- **`none`**, in `Ecology.step` step 4 (`ecology.py:524`):
  `breeders = list(alive) if eco.breed_gate == "none" else [m for m in alive if m.record["energy"] >= eco.birth_threshold]`.
  - `alive` holds only members evaluated this season, because children are appended later in the loop. So "every
    living evaluated member" needs no further test.
  - `rng.shuffle(breeders)` and the rest of the loop are unchanged.

**Validation.**
- **`none` is refused unless the economy is the no-selection one:** `--neutral`, i.e. starvation off,
  `birth_cost` 0, `living_cost` 0.
  - With a birth cost, an ungated parent at negative energy would pay into further debt.
  - With a living cost, the gate is part of the economy under test.
- **Add it to `UNSHIFTABLE`.**

**Why a flag, and not a change to `--neutral`.** Changing what `--neutral` does would silently change three committed
arms on a re-run. A new drift registration instead writes `--neutral --breed-gate none`, and states it.

**Rejected alternatives.**
- **A large `--initial-energy`** lifts the founders only. Children still start at `birth_cost` 0 (`:539`).
- **A negative `--birth-threshold`** would work in `EcologyConfig`, but `--neutral` overwrites the threshold with 0
  (`cli.py:355`). There is also no `--no-starvation` flag to build the neutral economy without `--neutral`.
- **A positive `birth_cost` in the drift arm** changes the energy flows and still gates.

**Tests.**
1. With the flag unset, a 10-season `--neutral` run is byte-identical to today.
2. Under `--neutral --breed-gate none`, a population with one member at energy −5 and one free slot per season
   lets that member breed, where under `energy` it never does.
3. `--breed-gate none` without `--neutral` raises.

**Readout.** Every drift arm reports `drift_gate.py actual` on its own lineage. With `lineage.jsonl` that figure is
exact. Under `--breed-gate none` it must be 0.

---
_Generated by [Claude Code](https://claude.ai/code)_
