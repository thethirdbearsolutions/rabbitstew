# RBT-125 harness adversary: PR #437 (`results/RBT-125-nose-step-harness` at `5043750`)

**Verdict: MERGE.** None of the four checks finds a MUST. There are three SHOULD items: one is an interface gap on the
RBT-129 side, and two are one-line guards.

- **The PR** adds four flags to RBT-125 §B's nose-step harness (`runs/RBT-125/gate/steps.py`): `--config`,
  `--hosts-file`, `--seeds` and `--seed0`. It is for Stage 0's designed PAYS cells.
- **The evidence** is `probe_437_harness.py` → `probe_437_harness.txt`, in this directory.
- **The probe ran on a scratch tree:** #435 at `4464a4e`, plus RBT-128 #432 at `e7b8865` merged with the resolution
  ruled as L3 (#439), plus #437's `steps.py`. The integration branch's `steps.py` sits beside it for (d).
- **No physics bout ran.** For (a) and (d), the Pool is faked as in #437's own tests. For (b), a real fork Pool runs an
  introspection function.
- **#437's own tests** (`tests/test_rbt125_harness.py`, 3 tests) pass once `scipy` is installed.

## (a) Does everything a PAYS block sets live in `"sim"`? Yes

- **What `--fair` changes, all under `"sim"`.** In the Stage 0 PAYS cells `c2-p030-PW-G` and `c0-p030-HP-L`, `--fair`
  changes `sim.settle_max`, `sim.settle_until_rest`, `sim.world.ball_cone`, `sim.world.hinge_range` and
  `sim.world.motor_budget`, plus the top-level marker `fairness`.
- **The mass budget** (15.34, `sim.synthesis.mass_budget`) is already in the base world, so `--fair` leaves it
  unchanged.
- **Every smell and eat setting** is under `sim.food`: `smell_contrast` 2.5, `smell_tau` 2, `eat_from` root, `smell`,
  `decay`, the patches and `regrow_delay`.
- **The round trip is exact.** `SimConfig.from_dict(cfg["sim"]).to_dict()` returns every key.

**`effector_bias_sigma = 0`, which RBT-128's fix adds to `--fair`, is the one preset value outside `"sim"`.** It lands
in `mutation.effector_bias_sigma`. It is read only in `genetics.py` (4 lines, in `mutate`) and never in `simulation.py`
or `world.py`. It sets how an Effector's bias steps when a child is bred, and a §B bout runs fixed hosts and never
mutates. So `--config` reading only `"sim"` cannot lose it. **No PAYS bout can run unfair or on the wrong channel
through `--config`. Not a MUST.**

Three things remain.

**S1 (on the RBT-129 side): `stages.py pays` cannot feed `steps.py`.**
- `stages.py pays` (#435) formats `{world}` as `worlds/<id>.json`. That is a world **block** (`id`, `axes`, `fair`,
  `argv`, `block`, …), not a `config.json`.
- `steps.py --config` on it fails with **KeyError 'sim'**. It fails loudly, not silently, but Stage 0's designed PAYS
  cells cannot run as wired.
- **Fix:** either `emit` writes a real `config.json` per PAYS cell (for example `worlds/<id>.config.json`, from
  `blocks.config_dict`) and `pays` passes that, or `steps.py` accepts a block.

**S2: `--config` never checks fairness.**
- `steps.py --config` reads `"sim"` and ignores the `fairness` marker. So a `config.json` from a pre-RBT-128 or
  `--unfair-i-know` run is accepted, and its bouts run unfair.
- **Fix:** when `--config` is given, assert `cfg.get("fairness") == "fair"`, and print it in the header.

**S3, a note on the hosts: pre-fairness hosts carry the effector-bias walk.**
- The registered hosts are RBT-113's O1 U designed finals. Those evolved **without** `effector_bias_sigma = 0`.
- So they carry whatever resting-throttle bias the walk left. RBT-129 DESIGN §12.1 notes that the designed D line was 99% saturated.
- A PAYS figure on such hosts measures the nose and speed steps on bodies whose resting drive `--fair` would have
  closed.
- **Fix:** if Stage 0's `--hosts-file` draws on pre-fairness finals, say so beside every PAYS figure. Better, draw the
  hosts from finals evolved under `--fair`, once any exist, or zero the Effector biases on load as a stated variant.

## (b) Does the `SEEDS[:]` mutation reach the fork Pool's children? Yes

- **The probe:** it sets `SEEDS[:] = [900 … 903]`, `HOST` and `rp.RUN["cell"]` in the parent, then maps an
  introspection function over a real `get_context("fork")` Pool.
- **The result:** every child pid reports `SEEDS[:3] == [900, 901, 902]`, `len(SEEDS) == 4`, the `HOST` keys, and
  `rp.RUN["cell"]` as a `SimConfig`.
- **Why it is safe:** `steps.py` pins `get_context("fork")`. The paired bouts also carry their seed in the task tuple,
  so the children never need `SEEDS`. They do need `HOST` and `rp.RUN`, and fork gives them both.

## (c) Does the host refusal work both ways? Yes for the motif, but it does not check the body

`routed.unit_indices`, as `--hosts-file` calls it:

| host | result | `fair.is_designed` |
|---|---|---|
| Pioneer, evolved layout (a food nose and an effector on each drive wheel) | accepted, (2, 0) | True |
| Pioneer, default (no food nose) | **refused** (StopIteration) | True |
| Pioneer with the left wheel's nose removed | **refused** | True |
| random holistic genotype | **refused** | False |
| **the Pioneer's wheel brains on a reshaped chassis** | **accepted**, (2, 0) | **False** |

- **What it does:** it refuses every host that cannot carry the routed motif, and accepts one that can.
- **What it misses:** it checks only the wheel nodes' brain layout. A body that is not the designed one, with the same
  wheel brains, passes.

**S4:** also require `fair.is_designed(g)` for every `--hosts-file` line. The designed PAYS cells must run on the
designed body.

## (d) Are the defaults the registered §B run? Yes

The probe ran the registered command line (`steps.py HOSTS_ROOT U-G2.5`, no new flag) under the same faked Pool, once
with the integration branch's `steps.py` and once with #437's:
- **stdout** is identical;
- **every task** is identical: 17,760 tasks, seeds 125000–125127.

That matches the amended registration's 128 paired seeds (`REGISTRATION.md` §B: "Seeds: 128 paired per host
(125000–125127)"). The added lines change the output only when `--config` is given.

## The list

**MUST:** none.

**SHOULD**
- **S1:** give `steps.py --config` a real `config.json` from `stages.py pays`, or let it accept a block. Stage 0's
  designed PAYS cells need this before they are emitted.
- **S2:** assert `fairness == "fair"` when `--config` is given.
- **S3:** state beside every PAYS figure when the hosts are pre-fairness (the effector-bias walk). Prefer hosts
  evolved under `--fair`.
- **S4:** require `fair.is_designed` for each `--hosts-file` host.

---
_Generated by [Claude Code](https://claude.ai/code)_
