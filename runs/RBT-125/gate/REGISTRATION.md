# RBT-125 world gate: registration

*Written and committed before any gate data exists. Compute opens at 23:01 UTC on 2026-09-27; `run_gate.sh` refuses
to start before then. The design of the channel is in `runs/RBT-125/DESIGN.md`.*

**The question (R4 in `runs/RBT-121/SYNTHESIS.md`):** with the smell contrast channel on, at a stated G, does a
nose pay on **real bodies** in the perception-demanding layout, at a weight evolution reaches? And does a nose step
pay comparably to a speed step?

**Everything below uses the committed eating rule** (any geom centre within 0.35 m). The gate belongs to the smell
channel. The eating rules' side effects are read in §C.

## The worlds

All cells use RBT-90 part 2's committed world (`runs/RBT-90/forage-801/config.json`): random terrain, 12 items, work
cost 0.03 per kJ, 15 s seasons, random start, and mass budget 15.34. Only the food block changes (`worlds.py`, which
writes `worlds/<cell>/config.json`).

| layout | food block |
|---|---|
| **U** | as committed: uniform, instant random regrowth, sum smell, decay 1 |
| **HP** | RBT-106's one-field patchy world: `patches = 3` |
| **PW** | 2 patches of 0.4 m in a 4 m disc, own-spot regrowth after 60 s, log smell, decay 1.5 |

**G** is `food.smell_contrast` with τ = 2 s. G = 0 is the legacy reading.

- **The registered G is 2.5.** This is RBT-121 audit C's kinematic candidate (`probe_gprop.txt`: in PW every step ties +25% speed).
- **The registered alternative is G = 10**, the value that saturates.

## §A. The prize at a = 6 (the gate)

**Instrument.** RBT-103's harness, `runs/RBT-103/routed_populations.py`, is used unchanged. The wrapper
`prize_gate.py` adds one patch: RBT-97's rotated decoy also rotates what the contrast channel smells
(`Simulation._log_smell`). Without the patch, the decoy would read the true layout under G > 0 and could not fail. The
wrapper asserts that the patched decoy changes the reading before it runs anything.

**Bodies.** These are RBT-106's: each of RBT-90 part 2's ten populations (seeds 801, 804, 805, 806, 807, 1, 2, 3, 4
and 7), with the designed-body bests at generations 0, 100, …, 590, restored from `ckpt/rbt-90-SEED`.
- Each body carries the routed compass at **w = 3, i.e. a = 2w = 6**, signed by the harness's two direction
  probes, re-measured in each cell.
- It is compared with its own base on **64 paired seeds from 7000**.
- In the PW cells, the rotated decoy also runs at w = 3.

**Statistic** (RBT-106's): per population, the mean over its signed bodies of (motif − base) items per season.
Across populations, the mean with a Student t(n − 1) 95% interval. The decoy's statistic is (motif − decoy),
computed the same way.

**Cells, in run order:**
1. PW-G2.5, PW-G10 and PW-G0 (with the decoy);
2. then HP-G2.5, U-G2.5, HP-G10 and U-G10;
3. then HP-G0 and U-G0.

**PASS rule, read at each PW cell.** A cell passes when both hold:
- the prize's t lower bound is > 0;
- the lower bound of (motif − decoy) is > 0.

A prize that the decoy keeps is not a perception prize, so the second condition is required.

**The gate's verdict:**
- **PASS at G = 2.5** if PW-G2.5 passes.
- Otherwise, **PASS at G = 10** if PW-G10 passes (a fallback, reported as such, with the saturation caveat of
  adversary §6b).
- Otherwise, **FAIL**.
- Both cells are reported either way.
- PW-G0 is the legacy control. Audit C predicts it does *not* pass at a = 6. Its result does not change the verdict.
  The channel's own contribution is (PW-G − PW-G0), paired by population.

**Controls:**
- **The harness check.** This tree, with the flags off, must reproduce RBT-103's committed seed-801 ROW
  (a = 32 / 64, in its own uniform world) to the digit: `prize/harness-801-uniform.txt` against
  `docs/artifacts/RBT-103-seed-801.txt`. **If it differs, nothing in §A is read.**
- `run_gate.sh` refuses to run if `worlds/` differs from the committed files.

**Also printed but not gating:**
- the per-population verdicts of the harness;
- RBT-38's zero-count (pairs where motif = base), pooled per cell. PW's sparse eating makes ties common. The gate
  reads the across-population t bound, as RBT-106's PRIZE line did.

**What the result can and cannot say:**
- The installed motif is a planted positive, so this tests the *world and the channel*, not evolution.
- A PASS means that a weight evolution has reached (6, the top of paper 5's range) now pays on real Pioneer bodies,
  with a food-dependent mechanism.
- It does **not** say that the Pioneer or a holistic body will evolve the motif, or that the step path to it
  pays (§B).

## §B. A nose step against a +25% speed step (real RBT-113 hosts)

**Hosts:**
- RBT-113's designed-body U-line finals, arm O1, seeds 1–3.
- K = 5 per seed, drawn by `default_rng(125)`: 15 hosts, restored from `ckpt/rbt-113-O1`.
- Each is signed by the same two direction probes. An UNDETERMINED host leaves every arm.

**Arms, per host,** on 32 paired seeds (125000–125031), in PW at G ∈ {2.5, 10, 0}:

| arm | what it is |
|---|---|
| **w0** | the host as it is |
| **w0.4** | the first weak nose (a = 0.8) |
| **w1 → w1.4** | a one-σ step on each of the motif's two output links (σ = 0.4, `genetics.py`) |
| **w3 → w3.4** | the same step at the gate's rung |
| **speed** | `world.joint_damping` ÷ 1.25 |

**The speed arm.** The Pioneer's wheels are torque motors, so their free-spin speed is gear ÷ damping. Dividing the
damping by 1.25 gives +25% top wheel speed at the same torque. The **realised** centre-of-mass speed ratio is
measured and printed. If it is not 1.25 ± 0.1, the comparison is also stated per unit of realised speed.

**Statistic:** per host, the paired mean difference in items per season (net printed beside it). Across hosts, the
mean with a t(n − 1) 95% interval. The nose step minus the speed step is also computed paired per host.

**Reading** (R4: "a nose step pays at least comparably to a speed step"), per step:

| reading | condition |
|---|---|
| **NOSE LEADS** | the lower bound of (nose − speed) > 0 |
| **SPEED LEADS** | its upper bound < 0 |
| **COMPARABLE** | the interval includes 0 and the nose step's own lower bound > 0 |
| **TIED, NOSE STEP UNRESOLVED** | otherwise |

The w 3 → 3.4 step at G = 2.5 is the registered line. The first nose and w 1 → 1.4 are reported beside it.

**The kinematic expectation** (`probe_gprop.txt`, PW, G = 2.5): steps of about +0.17 to +0.19 items against a speed
step of +0.17, which would read COMPARABLE. At G = 10 the later step should fall to about +0.08 (saturation).

## §C. The R6 side effects (descriptive; no pass rule)

All solo seasons, stated as such. The ecology runs 4 per arena.

- **Founders.** RBT-113's seed-1 generation 0: 40 per fauna, drawn as `Experiment` draws them, with 8 draws each.
  - The conditions are U-G0, U-G2.5, U-G10, PW-G0, PW-G2.5 and PW-G10, plus each eating flag on U-G0 (root,
    sensor, surface, clearance from the geoms), and root and sensor on PW-G2.5.
  - Reported per fauna: items, net, the share solvent (mean net ≥ the living cost of 0.25), the share with any
    food, and items against U-G0.
  - The income lost to root eating is RBT-116 adversary SHOULD 6.
- **The committed ecology corpus.** RBT-90 part 2's seed-801 run: its living population at season 600 (60 per
  fauna), with 4 draws each.
  - The conditions are U-G0, U-G2.5, U-G10, and each eating flag on U-G0.
  - Reported per fauna: net, net ÷ living cost (R5's regime measure; survivor-weighted, because these are the
    living), and the share below cost.
- **The blind tumbler** (RBT-121 adversary §7). One full-throttle hinge and no sensor, with an arm of 0.45 m or
  6.46 m, over 20 draws, in RBT-113's generation-1131 world.
  - The conditions are every eating rule on U-G0; PW-G0 with any and with root; and PW-G2.5 with root.
  - Also run: the same rod with an unused food nose on its root, under `eat_from = sensor`.
  - This shows whether the sensor rule taxes coverage or only noselessness.

## §D. Order, budget and stopping

- **Order:** `run_gate.sh`, as written (§A's harness check, then the PW cells, then §B, then §C, then §A's
  committed layouts).
- **Estimated cost:** about 5 hours on 4 cores, at 0.5 s per Pioneer season. The gate verdict (the PW cells and the
  harness check) is ready after about 1.7 hours.
- **Stopping:** a harness check that is DIFFERENT, or a decoy self-check that fails, stops the script. Anything else
  runs to the end. A deviation from this file is logged in `DEVIATIONS.md` beside it, with the reason, before the
  deviating output is read.
- **Outputs:** `launch.txt`, `prize/`, `prize.txt`, `steps/`, `side_effects.txt`. The readout goes to `READOUT.md`,
  in a second PR.
