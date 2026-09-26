# RBT-106 pre-registration: is it the size of the prize that decides whether a compass is held?

*Designer's pre-registration, 2026-09-26. **No arm has been launched.** Every number below is read from
a committed readout beside this file, or from a committed file of another ticket, named at the number.
The runs made for it are throwaway checks of at most 20 seasons, or probes that run no ecology (§8).
RBT-104's tooling is imported, never copied or edited (its design is PR #177, its adversary PR #181; this
branch merges #177's head so that the imports resolve, and this PR should merge after it). The adversary
is named by the coordinator.*

**The question** (ticket RBT-106). A correctly wired routed compass pays about 2.5× more in a patchy
world than in RBT-90's uniform one. Every evolution run of the recent phase, RBT-104 included, is in
the uniform world. **Is it the size of the prize, rather than reach, that decides whether selection holds
(or evolves) a compass?**

**The design in one paragraph.** The flag is the existing `--food-patches 3`: exactly one config field,
`sim.food.patches`, and the run is byte-identical at 0 (§1). Its prize, measured here on the ten part-2
populations with RBT-103's harness unchanged, is **+2.103 [+1.542, +2.663] items at a = 64, against
+0.844 [+0.618, +1.070] uniform: 2.49×** (§2). The primary contrast is a pair of arms on part 2's ten
seeds that load the same founders, RBT-104's seeded founders with the routed compass planted **at the
paying magnitude (w = 32, a = 64)** instead of RBT-104's w = 1, and differ in the flag alone: **HU**
(uniform) and **HP** (patchy). The readout is whether the planted compass is **held** above what the
operator alone leaves at the same depth (§5), with RBT-102's structure instrument and RBT-104's function
harness, both unchanged, beside it (§6). The ticket's suggested contrast, RBT-104's own w = 1 founders in
the patchy world (**P1**) against RBT-104's **S1**, is costed as an optional second pair; this design
recommends against it as a verdict arm, because it has no power against the hypothesis (§3.4).

**Three corrections to the ticket's premises, found before designing:**
1. **RBT-103's "12 items in 3 patches" world is two fields, not one.** It also has `regrow_delay 45`
   (`runs/RBT-103/adversary/worlds/sparse-patchy/config.json`), and `regrow_delay > 0` switches the
   ecology to persistent arenas that carry food between seasons (`Ecology.persistent`, RBT-19). The
   one-field world is `patches = 3` at part 2's instant regrowth. Its prize was unmeasured; it is
   measured here (§2), and it is 2.49×, close to the ticket's "~3×".
2. **The one-field patchy world is richer, not harder.** Base income on the part-2 champions rises
   by +0.229 [+0.170, +0.287] (§2), and the 20-season throwaway runs breed ~1.6× faster (§4). The
   ticket's "harder at 12 items" was read from the regrow-45 world, where nothing regrows within a bout.
   Faster breeding means a deeper window, so every "held" reading is matched by **depth**, not season.
3. **RBT-104's planted founders carry a sub-paying compass.** At w = 1 the motif's gain is a = 2, and
   the operator alone never takes it to a paying rung (RBT-104 adversary `persistence-801.txt`: 0–1% at
   a = 64 at every depth). S1-patchy against S1-uniform therefore cannot ask whether a **paying**
   compass is held when the prize is larger, which is the ticket's question. A paying compass has to be
   planted to ask it: w = 32, RBT-103's own a = 64 install, which is what the prize was measured at.

---

## 1. The flag: `--food-patches 3`, one field, byte-identical at 0 (ticket item 1)

`--food-patches N` already exists (RBT-19). It sets `sim.food.patches`; with N > 0, `set_food_seed`
draws N patch centres uniform in the disc from the bout's food seed, and every item, and every instant
regrowth, falls uniformly within `patch_radius` (0.6 m, the default and RBT-103's) of a randomly chosen
centre. The patches are redrawn each bout. At N = 0 `_draw_patch_centres` returns before drawing, so
the food stream is untouched. **No code is added.**

Checked (`one_field.py`, `one_field.txt`, seed 801, 20 seasons, x86_64, MuJoCo 3.14.0):
- **Check 1: byte identity at 0.** Part 2's command with `--food-patches 0` written out passes RBT-104's
  `byte_identity.default` (imported): `seasons.txt` is **byte-identical** to the first 40 rows of
  `runs/RBT-90/forage-801/seasons.txt`, and `config.json` equals the committed one outside seasons,
  generations and workers, with RBT-105's `ecology.breed_stream` (null) tolerated and named.
- **Check 2: one field.** With `--food-patches 3`, `config.json` differs from the committed part-2 one in
  **exactly one field, `sim.food.patches` 0 → 3**. `regrow_delay` stays 0, so persistent arenas stay off.
- **Check 3: the seeded pair differs in the world only.** Two runs loading the same seeded founders at
  patches 0 and 3 save **60 of 60** byte-identical founders of each fauna, and their seasons differ from
  season 0. Both faunas forage in the world, so the holistic fauna's rows differ too (unlike
  `--link-scale`, this flag is not the designed body's alone). That is the world, not a leak.

Tests (`tests/test_rbt106.py`, 8): the flag is one field of the sim config and leaves `regrow_delay` at 0;
`--food-patches 0` is the default; the uniform world draws no patch centre; RBT-106's S1 command is
RBT-104's `run_arm.sh` S1 command token for token; each pair differs by exactly `--food-patches 3`; the
H and P pairs differ only in their founders; `held.py`'s criterion.

## 2. The prize in the one-field patchy world, measured (the ticket's premise)

`prize.sh` runs RBT-103's `routed_populations.py`, unchanged, on each part-2 population's committed-rule
bodies (bests 0, 100, …, 590, restored from `ckpt/rbt-90-SEED` into scratch) with the world taken from
`runs/RBT-106/world-patchy/config.json` (its `--config-from`, RBT-103's own world control): a = 32 and 64,
the rotated decoy at a = 64, 64 paired seeds from 7000. **Harness check:** the restored bodies in their
own world reproduce RBT-103's committed seed-801 row to the digit. `prize.py` pairs each population with
RBT-103's committed uniform row (`prize.txt`):

| | uniform (RBT-103) | one-field patchy | patchy − uniform, t(9) |
|---|---|---|---|
| **a = 64** | +0.844 [+0.618, +1.070], PAYS 8/10 | **+2.103 [+1.542, +2.663]**, PAYS 8/10 | **+1.259 [+0.900, +1.617]; ratio 2.49×** |
| a = 32 | +0.419 [+0.234, +0.604] | +0.887 [+0.537, +1.236] | +0.467 [+0.246, +0.688] |
| base income | 1.308 [1.179, 1.438] | 1.537 [1.399, 1.675] | +0.229 [+0.170, +0.287] |
| gain per unit base income, a = 64 | 0.64 | 1.37 | 2.1× |

- Every population gains in the patchy world (per-population ratios 1.9–3.1×).
- **The patchy gain is chemotaxis:** the rotated decoy leaves it FOOD-DEPENDENT on 9 of 10 populations
  (retaining −21% to +6%), and UNRESOLVED on seed 2.
- Direction signs agree between the worlds on every body both signed. Seed 2 is paired over the 6
  bodies RBT-103 could sign.
- This is close to RBT-103's adversary's two-field figures (+2.267 in P-801's world, +2.489 for P-801's
  own bodies at 12 items in 3 patches with regrow 45). The one-field world keeps the prize.

{{REST}}
