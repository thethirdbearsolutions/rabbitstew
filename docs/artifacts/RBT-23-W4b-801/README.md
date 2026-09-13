# RBT-23 / W4b-801 — the substrate behind the +0.897 compass figure

Committed for RBT-69, which could not replicate that figure and established that
the only remaining difference between its harness and the source was **the robot
population** — and that this run was committed nowhere. See RBT-68 for the general
problem: `runs/` is gitignored, so the artifacts backing published findings have
not been reachable from a fresh checkout.

## What this is

The conventional (fixed-body Pioneer) arm of `W4b-801`: **12 food items, no
patches, no regrowth**. This is the substrate `runs/sim-audit/verify_independent.py`
draws its seven robots from — `GENS = (90, 190, 290, 390, 490, 550, 590)`,
`SEEDS = 9000..9063`.

- `config.json` — the exact run config. `SimConfig.from_dict(json.load(open(...))["sim"])`.
- `conventional/best_gen0090.json` … `best_gen0590.json` — the seven bests, and only
  those seven. The other fifty-odd bests, the holistic arm and `lineage.jsonl` (14 MB)
  are not here; ask if an analysis needs them.
- `history.json` — per-season population history for the arm.

## Why only seven

These are the seven the disputed number was measured on. Committing exactly them
keeps the comparison honest: anyone re-running gets the same population, not a
superset they might subset differently.

## Caveat worth stating

RBT-69 ran against `runs/RBT-19/P-801` robots and, in a second arm, against RBT-19's
config *reshaped* toward this world — reaching a 1.219 baseline against this run's
1.516. That residual gap is one of the things these files settle: the reshaped world
was an approximation of this `config.json`, not this `config.json`.
