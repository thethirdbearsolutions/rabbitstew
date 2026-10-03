# RBT-125 world gate: registration

*Written and committed before any gate data exists. Compute opens at 23:01 UTC on 2026-09-27; `run_gate.sh` refuses
to start before then. The design of the channel is in `runs/RBT-125/DESIGN.md`.*

**The question (R4 in `runs/RBT-121/SYNTHESIS.md`):** with the smell contrast channel on, at a stated G, does a
nose pay on **real bodies** in the perception-demanding layout, at a weight evolution reaches? And does a nose step
pay comparably to a speed step?

**Everything below uses the committed eating rule** (any geom centre within 0.35 m). The gate belongs to the smell
channel. The eating rules' side effects are read in §C.

## Amendment 2: the coordinator's ruling of 22:45 on the adversary's full report (#418)

*Committed before any gate output exists. The gate still has never run: the launcher re-armed at 22:30 was stopped
at 22:31 UTC, before 23:01.*

**A2.1: the gate runs on #414's fixed tree, not on 0ec395f.** The fixed tree carries:
- **C1.** Under `eat_rule = surface`, `clear_from = geoms` now measures from every geom's surface. A test pins a
  motionless 6.46 m rod at 0 items.
- **C2.** The config-strip combination is pinned by tests.
- **G5.** `smell_tau` is written whenever `smell_contrast > 0`.

It also carries RBT-120's motor budget, which is off by default.

**A2.2: the parity condition.**
- `parity.py` runs every §A cell (all prize cells use the legacy eating rules) under 0ec395f's `rabbitstew/` and under
  the fixed tree. The cells are read from the same `worlds/`. Each digest covers P-801 g590 with and without the
  a = 6 motif, over 3 seeds, plus the patched decoy in the PW cells.
- Every cell must be IDENTICAL. Otherwise `run_gate.sh` stops (exit 5) before any gate cell runs, and the
  coordinator is woken.
- `parity.txt`, with both tree hashes, is copied into `launch.txt`.
- `launch.txt` records the fixed tree's `rabbitstew/` hash and 0ec395f's. They differ now, by design. The
  amendment 1 guard that they be equal is replaced by this parity condition.

**A2.3: §C's `surface` + `geoms` cells run on the fixed tree,** so they measure the rule as intended. The legacy-rule
cells are unaffected: the parity condition covers the rules the §A cells use, and C1 changes only surface + geoms.

**A2.4: the wording of any negative (C6).** A negative at a cell with G > 0 means "*contrast-only* perception does not
pay". The level channel is deferred (DESIGN §4).

## Amendment 1: the coordinator's ruling of 22:28 on the adversary's registration findings

*Committed before any gate output exists. The gate has never run: its armed launcher was stopped at 22:25 UTC, before
23:01. This amendment supersedes the sections below wherever they differ. The adversary's findings (RBT-125, 22:24) were
accepted: REGISTER AFTER FIXES, with all 7 MUST and all SHOULD items.*

**A1.1 (M1): the channel against the world.**
- The §A PASS rule, unchanged, is a claim about the **world**: "PW pays an installed compass at a = 6 through a
  food-dependent mechanism". It does not attribute anything to the channel.
- A sentence saying **the channel pays** also needs the channel's contribution, (PW-G − PW-G0) paired by population
  over all ten, to have a t(9) lower bound > 0. Otherwise the channel's contribution is reported as unresolved.
- Bodies are re-signed in each cell, so a body can change sign between G and G0. The contribution is therefore also
  reported on the bodies signed the same in both cells. This is descriptive.

**A1.2 (M2): all ten populations.**
- PASS is read over all 10 populations, and the decoy over the same 10.
- A population with no readable ROW counts as prize 0 and as (motif − decoy) 0: every body UNDETERMINED, a STOPPING,
  or a crash.
- The readable n and the missing seeds are printed for every cell.

**A1.3 (M3): the harness-check stop is implemented.** `run_gate.sh` compares the ROW lines and exits on DIFFERENT
before any gate cell runs. There are now **two** checks:
- (a) RBT-103's committed seed-801 row, in its own uniform world, at a = 32 / 64;
- (b) RBT-106's committed HP-801 row (`runs/RBT-106/prize/patchy-801.txt`), through `--config-from
  runs/RBT-106/world-patchy`, at a = 32 / 64, with the legacy decoy at a = 64. This one exercises the config-from path
  and the decoy (SHOULD).

**A1.4 (M4): §B, the nose step against the speed step, is rebuilt and moved to the end.** It now runs after §A and §C,
so it does not delay the gate verdict.
- **Seeds:** 128 paired per host (125000–125127).
- **Speed arms:** at w0, w1 and w3, so that each nose step is compared with a speed step taken **at the same base w**.
- **The damping step:** joint damping ÷ 1.25. This also lowers the casters' passive damping by the same factor
  (SHOULD).
- **Per unit of realised speed.** For each host and each base w:
  - r = the mean centre-of-mass path speed of speed@w ÷ that of w, over the 128 seeds;
  - the speed step, rescaled to a realised +25%, is (items of speed@w − items of w) × 0.25 ÷ (r − 1);
  - a host with **r < 1.10** leaves the per-unit comparison at that w, and is counted.
  - **The per-unit comparison is the registered line.** The raw comparison is printed beside it.
- **Readings of (nose − speed)**, paired per host, over hosts:

  | reading | condition |
  |---|---|
  | NOSE LEADS | the 95% lower bound > 0 |
  | SPEED LEADS | the 95% upper bound < 0 |
  | COMPARABLE | equivalence: two one-sided t tests at 5%, i.e. the 90% interval inside ±δ, with **δ = 0.10 items per season** (auditor B's ~0.1 threshold) |
  | TIED, UNRESOLVED | otherwise |

- **Power, stated.** The adversary measured a per-season SD of about 2.4 for the w3 → 3.4 step.
  - At 128 seeds, the per-host SE is about 0.21, and the across-host half-width at 15 hosts is at least about ±0.12,
    and about ±0.17 for (nose − speed).
  - The 90% half-width is therefore expected to exceed δ.
  - **The expected reading is TIED, UNRESOLVED**, unless one step leads by about 0.17 or more. §B is registered as
    descriptive in that sense: it can show a lead, but it is not expected to show equivalence.
- **Estimated wall time:** about 7 h in all. That is under the ruling's 9 h, so the full 128 seeds are run.

**A1.5 (M5): τ.**
- The gate validates the code's transform: τ = 2 s, floor ln(Σ + 1e-12). The coordinator will amend RBT-116's
  registration to it.
- **A sensitivity cell, PW-G2.5-tau1 (τ = 1 s, with decoy), is descriptive.** It runs after the §A verdict.
- **The 1e-6 floor is not run, because it would need a code change.** Its magnitude is negligible:
  - Whenever any item stands in PW's 4 m disc, the nearest one is at most about 8 m from a nose, so
    Σ ≥ e^(−8/1.5) ≈ 5e-3. U and HP regrow instantly, so an item always stands there.
  - The two floors then change ln S by less than 1e-6 ÷ 5e-3 = 2e-4, which is below 1e-3 of G = 2.5's unit.
  - They differ materially only when *every* item is parked. Then every nose reads the same floor, and both
    transforms decay to 0 after the same saturated transient.

**A1.6 (M6): the environment.**
- scipy is required: `run_gate.sh` refuses without it, and `launch.txt` records its version.
- `launch.txt` records the gate commit, `rabbitstew/`'s tree hash, and 0ec395f's. They must be equal (the adversary's
  parity check), or the script refuses.
- Every output is written to `.tmp` and promoted only when its program exits 0 and the output carries its completion
  marker. A crash can never promote a truncated file.

**A1.7 (M7): §C.**
- **Births and realised depth are out of scope.** They need an ecology, and §C's seasons are solo.
- **Saturation (`saturation.py`), added.** For every contrast cell, on the §A bodies (70 designed bests × 2 seasons, no
  motif), it reports:
  - the median and p90 of |c| over all noses and ticks;
  - the share with |c| > 0.9;
  - the median and p90 of the wheel difference |c_L − c_R|.
- **PW coverage, added:**
  - founders under `surface` and `clear_from = geoms` in PW-G2.5;
  - the corpus in PW-G0 and PW-G2.5;
  - the tumbler under `sensor` (with and without an unused root nose) and `surface` in PW-G0.
- DESIGN §2's sentence is corrected to match.

**A1.8 (SHOULD):**
- **Familywise α.** The fallback is two shots (G2.5, then G10 only if G2.5 fails). The familywise one-sided α is at
  most 2 × 2.5% = 5%.
- **The G = 10 caveat is approach-speed gating as well as saturation.** The three noses share one baseline, so moving
  along the gradient puts every nose on the flank of the tanh. L − R is then multiplied by about sech²(G·c): 7% of its
  static value at G = 10, 0.25 m/s and 45° toward the food (adversary `probe_motion.txt`).
- `check_decoy` now also asserts two things:
  - the patch is a bitwise no-op on a legacy world;
  - the unpatched decoy reads the true layout under G > 0.
- **The per-population verdicts are uninformative in PW.** RBT-38's zero-count veto fires on nearly every PW
  population (P-801: 256/384 and 343/448 zero pairs), so they are not used.

**A1.9: the new order (§D).**
1. the two harness checks, stopping on DIFFERENT;
2. PW-G2.5, PW-G10 and PW-G0, with the decoy;
3. `prize.txt`: the §A verdict is computed;
4. PW-G2.5-tau1;
5. saturation;
6. the side effects;
7. HP and U at G2.5 and G10, then HP-G0 and U-G0, then the final `prize.txt`;
8. §B at PW-G2.5, PW-G10 and PW-G0.

No gate output is read until the coordinator rules on the adversary's full report.


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
