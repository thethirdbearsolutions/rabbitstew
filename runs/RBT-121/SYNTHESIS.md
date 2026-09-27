# RBT-121 synthesis: the rules a fair experiment in this simulator must satisfy

*The coordinator's synthesis of the RBT-121 loophole audit, 2026-09-27. Every factual statement below is stated as
the audit adversary left it. Where the adversary corrected an auditor, the corrected form is used and the audit is
cited with "(corr.)".*

**Sources:**

| role | file | PR |
|---|---|---|
| A: physics and body | `runs/RBT-121/physics/AUDIT.md` | #396 |
| B: GA operators and selection | `runs/RBT-121/ga/AUDIT.md` | #395 |
| C: ecology and economy | `runs/RBT-121/ecology/AUDIT.md` | #397 |
| D: history of the record | `runs/RBT-121/history/HISTORY.md` | #401 |
| **the audit adversary** (verdicts on A–C) | `runs/RBT-121/adversary/ADVERSARY.md` | #403 |
| related: the terrain finding | `runs/RBT-118/prior/ANALYSIS.md` §4a; `runs/RBT-118/prior-adversary/ADVERSARY.md` §3 | #399, #402 |
| related: the prior art | `docs/prior-art/REVIEW.md` (pending its citation check) | #404 |

## Why this exists

The programme's headline results have deflated repeatedly. Each time, an allowance of the simulator or the world did
the work, rather than the behaviour the experiment meant.

| allowance | what it inflated |
|---|---|
| mass | the arena's weight-class mismatch |
| potential energy at spawn | the spawn drop |
| motor capacity | RBT-113's holistic down line, and all of RBT-117's margin |
| coverage paid as foraging | papers 5–6 and RBT-113's up line |
| the clutter tax on wheels | paper 9's C1–C3 lead; today, RBT-118's late holistic income lead, which reverses on flat ground on 21 of 29 paired histories |

Auditor D counts 73 walked-back claims across the record. **None was caught by a review before the run.** Every one
was caught by measuring bodies away from the score.

Evolution is an optimiser, and it finds what the simulator pays for most cheaply. Read with the adversary's
corrections, the audits say:

> **At present the simulator pays more readily for blind motion than for perception.** That means coverage, full
> throttle and free-spinning limbs. At a mutation's scale, speed pays 13–40% where a nose step pays nothing
> measurable, in every one of 18 steering regimes.
>
> **The ecology selects hard on staying alive, and weakly on anything above that.** How weakly depends on each
> world's net income relative to the living cost.

**Most of the remedies are not new** (RBT-122, `docs/prior-art/REVIEW.md`, as corrected by its citation check,
`docs/prior-art/citation-check/CHECK.md`):
- **Sims (1994a):**
  - scaled each effector's maximum strength with the cross-sectional area of the two parts it joins, and clamped
    forces to it;
  - Sims's cap is **per effector, i.e. per DOF** (CHECK F1), so a 3-DOF joint gets three full caps. It fixes what
    strength is keyed to, not its multiplication by DOF or by branching. A per-joint or whole-body cap is our
    addition;
  - settled creatures, with no friction and no force, to a stable centre-of-mass minimum before scoring;
  - shrank the timestep to bound penetration.
- **Taylor & Massey (2001)** added stability checks.
- **Krčah (2008)** validity-tested bodies before simulation.
- **Cheney et al. (2013)** charged for actuated material.
- **Auerbach & Bongard (2014)** showed that a capacity which costs nothing is bought whether or not it helps.
- **Lehman et al. (2020)** catalogue the pattern.

What the programme adds is the discipline of measuring the body apart from the score, and doing it before the claim.

## The rules

### R1. Budget every capacity a body can multiply by adding parts, per body

| allowance | evidence (as corrected) | rule | fix |
|---|---|---|---|
| **Motor gear**: 4 × the heavier mass per driven DOF, up to 3 per ball joint (A1, B2) | holistic D Σgear/(4M) 3.57 (max 6.35) against the Pioneer's 1.7605; a 12-child hub reaches 30.3; B's shared rule alone leaves it at 10.1 | a whole-body cap on Σgear, rescaled with damping and the servo gains. Sims's area keying is optional on top: it is per DOF, so it does not bound a hub | **RBT-120.** A's c = 1.77 leaves the Pioneer only 0.5% of margin, so the test must pin it. |
| **Resting throttle**: the unbounded Effector-bias walk (B1) | designed D line 99% saturated | Effector biases bounded, or frozen, in any experiment that reads work | `--effector-bias-sigma S` |
| **Part count**: recessive nodes raise the cap (A4) | the part cap is about 2× the parts built | cap on reachable nodes | `cap_on_reachable` |
| **Extent** (A5) | a 6.5 m arm is legal, but earns nothing over a 0.45 m arm (adversary §7) | low priority; cap it if spans start to grow | `max_extent` |

### R2. Joints have ranges, so a limb cannot become a free rotor (A2 corr.)

- **Evidence:** 97% of the holistic D line's work is on children touching nothing, and 94% is on ball joints, which
  have no range.
  - About a third of the work is on children genuinely inside their parent: centre inside, or at least half their
    volume.
  - Filtering is by **weld group**: fixed links let limbs pass through grandparents.
  - Orientation mutation is unclamped (`genetics.py:209`).
- **Rule:** ball joints get a cone and hinges get ranges. This is the load-bearing fix.
- **Secondary:** an outward-orientation clamp applied at synthesis, not at genesis.

### R3. A body starts at rest (A3 corr.)

- **Evidence:** with motors off, 14 of 120 holistic bodies drift more than 0.25 m; none of 120 designed bodies do.
  Part of the drift is terrain rolling. Motors-off food is small-number static reach.
- **Rule:** settle until at rest, as Sims did.
- **Reporting now:** a motors-off season is the "moves by itself" null.

### R4. The world must pay perception more than its blind substitutes, along the path

- **Evidence** (C2 corr.):
  - at the peak, a well-steered forager eats several times a blind one of equal speed;
  - on the path, +25% speed pays +13–40% in all 18 cells of a 3 × 3 × 2 regime grid;
  - a one-σ nose step pays 0–10%, which is unresolved from zero at the calibrated cell;
  - a blind body spinning one motor at full throttle nets about +0.7 a season, at any arm length (adversary §7).
- **Rule:** a perception experiment registers a world, and measures it on real bodies at a **world gate**, in which:
  - the steering margin clears the selection threshold of R5 at the registered draws;
  - a nose step pays at least comparably to a speed step.
- **Levers, in order of evidence:**
  - concentrated patches with own-spot regrowth, i.e. depletion (C's PW layout);
  - a centred smell contrast, **with G stated and tested at G ∈ {2.5, 10}**, centred on a per-robot running baseline
    or given as a centred channel beside a level channel. Root-centring deletes root, single-nose and temporal smell
    (adversary §6b).
    - C's follow-up probe (`probe_gprop.txt`: kinematic, n = 300) uses the proposal's own sensor with running-baseline
      centring. In PW at G = 2.5, each nose step pays +0.17 to +0.19 items a season, about as much as +25% speed
      (+0.17).
    - At G = 10 the second step falls to +0.08.
    - In the committed worlds, speed still leads (HP: +0.36 against steps of +0.20 to +0.36; uniform: +0.19 against
      +0.09).
    - G = 2.5 with a running baseline is therefore the default candidate. The world gate confirms it on real bodies;
  - a work price that makes the speed optimum interior (C3);
  - eating rules that stop blind tumbling from paying: `eat_from`, surface eating, and clearance from the geoms (C4,
    A5).

### R5. Selection must be able to see the gain it tests, and the regime must be stated

- **Imposed selection (`evolve`; B3 corr.):** s ≈ 1.27 Δ/σ_P, with σ_P ≈ 0.7 (designed) to 1.2 (holistic) at 2
  draws.
  - A trait is held only if s > u/(1 − u).
  - Size the draws from this relation, or re-score the boundary (`--draws-final`).
  - The designed rep₂ of "0.004" is an estimator floor; the true value is about 0.03–0.1.
- **Ecology (B4 / C1 corr.):** the economy is a **strong viability sieve**.
  - In P-801, 60% of births starve, and only 39% of holistic deaths are from age.
  - Above viability it saturates once resident net income is ≳ 2× the living cost.
  - **Rule:**
    - every ecology registration reports its regime: net income per birth ÷ living cost, offspring by income
      quintile, and the share of deaths by age (`adv_p801_births.py`);
    - an experiment that needs selection *above* viability must operate below saturation, or change the breeding
      rule;
    - **a breeding-rule change reports its depth cost.** `energy` order is a gerontocracy: parents fall from 137 to
      71, and the age at breeding rises from 31 to 54. Prefer `energy_leak` or tickets, and match realised depth
      across arms. Depth mismatch is what sank RBT-80's comparison.

### R6. Compare bodies at stated operator parity (B2)

- The holistic operator erodes wiring about 5× faster per child.
- **Rule:** state whether a comparison is made at the default operators or at matched erosion
  (`--structural-rate-scale K`).

### R7. Name behaviour by instrument, not by yield (C7, D P3)

- "Forages", "steers" or "perceives" needs intact − decoy (RotatedSmell), items per new cell covered, and, where it
  applies, a chemotaxis index.
- **A planted-negative set** runs beside every such instrument: a blind full-throttle spinner, a kinesis-only body,
  and a motors-off body.
- Every income or lead statement names its world: terrain and work price (RBT-118 §4a).

### R8. Report the body levers with every holistic-against-designed result

Per line:
- Σgear/(4M), and the share capped;
- resting drive;
- the share of work on contact-free children, and the share at least half inside (adversary `phys_ghost.py`);
- motors-off displacement and food;
- span;
- the reachable and recessive node counts.

A fauna difference that goes with a lever difference is attributed to the lever until shown otherwise.

### R9. Fairness defaults are defaults for new work (D P2, R2)

- Fixes land as flags: off by default, byte-identical when off, and reviewed.
- **A new holistic-against-designed registration refuses to start without the ruled fairness set**: a `--fair`
  preset, or a missing-budget guard. The mass budget has been set by hand in 439 of 439 configs.

### R10. Controls shown able to fail; side effects registered (D P3, P4, R6, R7)

- Each instrument fires on a planted positive, and stays silent on the planted negatives of R7, on the arm's own
  founders, at the n in use.
- A world or operator manipulation prints income, births, depth, saturation and solvency against the control.
- **Terrain is a primary factor, not a robustness arm** (H56; RBT-118 §4a).

### R11. Power from a bounded model at the realised n; no single seed carries a claim (D P5, R10)

### R12. Corrections propagate; the record keeps its evidence (D P6, P7, R11, R13)

- An `ERRATA.md` index covers superseded figures by file and line, including registered bare labels (D H76) and the
  prior-art errata E1–E7.
- The progress reports correct forward.
- `config.json` records the platform and library versions.

## Prioritised fix list

Each fix is its own ticket: a designer, a design adversary, a ruling, and a flag that is byte-identical when off.

| # | fix | why first | cost |
|---|---|---|---|
| 1 | **Gear budget** (RBT-120), with the per-line lever report (R8) | the only allowance with committed damage; gates RBT-116 and RBT-118 | small |
| 2 | **Ball-joint cone + hinge ranges** (R2) | removes free rotors, the sink for motor capacity | small–medium |
| 3 | **`effector_bias_sigma`** (R1) | resting throttle is the designed body's allowance | tiny |
| 4 | **Ecology regime readout** (R5): offspring by income quintile, deaths by age, net income per birth ÷ cost | no code in `rabbitstew/`; makes every ecology claim state its regime | tiny |
| 5 | **Smell contrast channel** (centred on a running baseline, G stated) + the PW layout + the world gate (R4) | the lever for perception from scratch; feeds RBT-116 | medium |
| 6 | **Settle until rest** + a motors-off null (R3) | arena bouts, and the RBT-118 rematch | small |
| 7 | **Eating rules** (`eat_from`, surface, clearance from geoms) (R4) | stops blind tumbling paying as foraging | medium |
| 8 | **Breeding rule** (`energy_leak` / tickets / `energy`, with its depth cost) (R5) | only for experiments that need selection above viability | small |
| 9 | `--fair` preset / missing-budget guard (R9) | after 1–3 land | small |
| 10 | `cap_on_reachable`, `structural_rate_scale`, `crossover_cut aligned` | parity and long runs | small |
| 11 | `ERRATA.md` + platform in config (R12) | the record | small |
| 12 | Contact-penetration trip wire (A B9, D H71) + conservative-physics re-score (Koos; Lipson & Pollack) + randomisation of what must not be exploited (Jakobi) | champion-level claims; RBT-116 terrain | small |
| 13 | Work price; explosion floor | when a steeper price is registered | small |

## Committed results: what to re-read (nothing is retracted here)

- **RBT-80 NO VERDICT:** **not** re-read through the breeding lottery.
  - Its seeded arms held carriage (0.96 / 0.72 / 0.92, against floors of about 0.52).
  - The verdict failed on the drift comparator's depth mismatch, as paper 8 §2.4 already says.
  - Also noted: RBT-80's drift arm still bars net-negative workers from breeding (adversary, "also noticed").
- **Paper 10's HP / HU:** H8's confound stands as written. The lottery adds nothing to it.
- **RBT-113 and RBT-117:** ruled with the motor-allowance caveat. Its mechanism is now more specific: free rotation
  on range-less ball joints.
- **Papers 5–6 and RBT-113's up line:** consistent with R4 (blind motion pays). This is vocabulary only (R7).
- **Paper 9's C1–C3 lead, and any random-terrain fauna comparison:** a wheel tax (D H56). RBT-118's step-1 prior shows
  it directly.
- **Published progress report 1:** three readings withdrawn by paper 10's adversary (D H66). They are corrected in
  report 2.
- **Registered bare labels and the prior-art errata** go into `ERRATA.md` (fix 11).
