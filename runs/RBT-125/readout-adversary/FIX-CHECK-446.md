# FIX-CHECK of #446 (dd43d52): surface clearance under `clear_from = root`

*This is the check the coordinator asked for at 03:05 UTC. The fix is at `results/RBT-125-eat-clearance`, dd43d52,
and changes only `rabbitstew/simulation.py`. The probes ran on #446's tree, with integration (4c32cec) as the
comparison where one was needed.*

## Verdict: **FIX CORRECT, BUT OVER-STRICT FOR `root` + `surface`**

The leak is closed and nothing else moves, but the fix costs `root` + `surface` its founder solvency (0.38 → 0.25).
A minimal guard closes the same leak at no cost.

| check | result |
|---|---|
| (a) leak closed | **yes** |
| (b) centre paths and `geoms` + surface unchanged | **yes, byte-identical** |
| (c) no deadlock | **yes.** A fallback that predates #446 is noted |
| (d) designed-founder solvency under `root` + `surface` | **0.25, down from 0.38.** The fix makes the rule's clearance stricter than `root` + centre's. The rule itself had no leak |

**MUST (before RBT-129 uses `root` + `surface`).**
- **The problem.** For `eat_from = root`, #446 clears items **0.8 m from the root's surface**. That is about 0.2 m farther than `root` + centre clears them, which is 0.8 m from the root's centre. So it is not like-for-like.
- **The fix.** For `eat_from = root`, replace the surface clearance with the minimal guard: the root-centre clearance, plus "no item placed within `eat_radius` of an eating surface". Keep #446's full surface clearance for `eat_from ∈ {any, sensor}`, which is where the leak was.
- **The minimal guard is enough.** It is leak-free (the motors-off rod eats 0 in U and PW), and for compact roots it is bitwise the pre-fix placement. The founders are then 0.656 items (+0%) and **0.38 solvent**, exactly as in #445.
- **The alternative.** Keep #446 as it is, and record that `root` + `surface` then costs the designed founders −26% items, with 0.25 solvent. That is still better than `root` + centre's 0.12, but it is not the #445 figure the ruling used.

## (a) The leak is closed (`fixcheck_tumbler.txt`, the #445 tumbler probe on #446's tree)

The 6.46 m rod in U-G0, net per season, 20 draws:

| rule | moving, before (#445) | moving, #446 | **motors off, before** | **motors off, #446** |
|---|---|---|---|---|
| any / surface / root clearance | +5.31 | **+1.91** | 2.10 | **0.10** |
| any / surface / geoms clearance | +1.91 | +1.91 | 0.10 | 0.10 |
| root / surface / root clearance | +0.66 | +0.71 | 0 | 0 |

- Under `any` + `surface`, the default clearance now matches the fixed `geoms` clearance exactly. The residual 0.10 is
  the same as the committed rule's (the rod's own settle and roll).
- A correction to the PR's description: `root` + `surface` did **not** leak before the fix (motors-off 0, in U and PW).
  The "+5.31" was `any` + `surface`.
- PW rows: `any` + `surface` + root clearance now gives +0.71 (motors-off 0.15), the same as `geoms`. `root` +
  `surface` gives +0.06.

## (b) Byte identity (`fixcheck_identity.py` / `.txt`)

- **The fixture:** a committed Pioneer (P-801 g590) and a holistic founder, in U-G0 and PW-G2.5, 3 seeds each, 15 s
  seasons with regrowth.
- **The digest:** `qpos`, work, items, `food_pos` and `food_spots`, computed on integration and on #446.

| rule | integration | #446 |
|---|---|---|
| committed any / centre / root | 0d7dcf44… | 0d7dcf44… **same** |
| root / centre / root | 27cfb071… | 27cfb071… **same** |
| sensor / centre / root | 0d7dcf44… | 0d7dcf44… **same** |
| any / centre / geoms | 8cf4cf1b… | 8cf4cf1b… **same** |
| any / surface / geoms | ee9ec2cd… | ee9ec2cd… **same** |
| any / surface / root | a45a2d92… | ee9ec2cd… changed, now equal to `geoms` (as intended) |
| root / surface / root | 58d5f6f8… | 12d7b4d1… changed (see (d)) |

**Why `any` / `surface` / `root` now equals `geoms`:** surface clearance from every eating geom already implies
clearance from the root centre. The centre term is redundant there.

## (c) Deadlock (`fixcheck_deadlock.txt`)

**There is no deadlock.** `_food_spot` tries 256 draws, then returns the **last draw unchecked**.

**The worst case:** a food disc of radius 0.5 m, smaller than the 0.8 m clearance around a robot at the centre.
- Every rule returns: 1.7 s for `root` + `surface`, 14 s for `any` + `surface` + `geoms` (256 surface-distance tries
  per regrowth), and 1.2 s for centre.
- **All 12 items land inside the clearance, and the robot eats every tick:** 288 items a season under `surface`, and
  141 under the committed centre rule.
- At radius 1.2 m and 3.0 m, nothing is placed inside the clearance.

**What the stated case adds.** In the gate worlds, food placement tests only robots, not scenery. So clutter c = 2
(obstacles) cannot make a spot infeasible. Only a food disc that is small against clearance plus body size can, and
the fallback then becomes a free-food fountain.

**This predates #446** (the centre rule does it too), so it is not a regression.

**SHOULD:** count the fallbacks, and warn on them, or refuse a config where clearance cannot be met. RBT-129's
habitability census should report the count. A cheap alternative is to return the draw farthest from the clearance
set instead of the last draw.

## (d) Designed-founder solvency (`fixcheck_founders.txt`, `fixcheck_variant.txt`)

RBT-113 seed-1 generation-0 designed founders, 40 × 8 draws, U-G0. The tumbler rows are net per season:

| `root` + `surface` clearance | items (net) | vs committed | **solvent** | tumbler 0.45 m, U | 6.46 m, U | 6.46 m motors-off, U | 6.46 m, PW |
|---|---|---|---|---|---|---|---|
| pre-fix (root centre only) | 0.656 (+0.079) | +0% | **0.38** | +1.30 | +0.66 | 0 | +0.06 |
| **#446** (root centre + 0.8 m from the eating surfaces) | 0.484 (−0.091) | −26% | **0.25** | +1.10 | +0.71 | 0 | +0.06 |
| **minimal** (root centre + `eat_radius` from the eating surfaces) | 0.656 (+0.079) | +0% | **0.38** | +1.30 | +0.66 | 0 | +0.06 |

For comparison: committed 0.653 items with 0.30 solvent, and `root` + centre 0.372 with 0.12 solvent (#445).

**Why #446 costs 26%.** It forces every item to stay 0.8 m from the chassis *surface*, about 1.0 m from its centre.
That is a stricter placement rule than `root` + centre gets, not a closed leak: before the fix, a motors-off body under
`root` + `surface` ate nothing.

**The minimal guard.** It forbids only what matters, an item placed inside eating reach. For compact roots it never
binds, and gives the pre-fix placement exactly. For an elongated root, whose surface could reach past the 0.8 m
centre clearance, it would bind and close that case.

**By the coordinator's condition ("the ruling holds unless it falls well below 0.38"), #446 as written trips it:
0.25.** The minimal guard keeps 0.38.

## Files (`runs/RBT-125/readout-adversary/`)

| file | what it holds |
|---|---|
| `fixcheck_tumbler.txt` | the #445 tumbler probe (`probe_tumbler_rules.py`) on #446's tree |
| `fixcheck_identity.py` / `.txt` | the per-rule byte-identity digests, integration against #446 |
| `fixcheck_deadlock.py` / `.txt` | infeasible, tight and committed food discs: wall time and in-clearance placements |
| `fixcheck_founders.py` / `.txt` | the designed founders under the four rules on #446's tree |
| `fixcheck_variant.py` / `.txt` | `root` + `surface` under the pre-fix, #446 and minimal clearances, as a monkeypatched probe with no code change |
