# RBT-121 audit A: physics and body model

## Corrections after the adversary (#403)

The RBT-121 adversary (PR #403, `runs/RBT-121/adversary/ADVERSARY.md` at e9096cb) re-derived this audit, and the
coordinator accepted its verdicts. **The body below is the record as it was first filed and has not been rewritten.**
Where the body and this block disagree, this block wins. Quotations are from #403.

| # | #403 verdict | corrected statement |
|---|---|---|
| **A1** | **HOLDS** | The numbers stand: 1.7605, 30.3, 10.1, and rule (c) spares the Pioneer. There are two caveats. (1) *"(c) leaves the Pioneer untouched by a 0.5% margin (1.7605 against 1.77). Any change to the Pioneer's masses or to the budget will cap it."* The closing test must assert that margin explicitly. (2) *"Power = 20 × gear holds for torque and ball motors only; velocity servos give 2.81 × gear."* So "power budget ≡ gear budget" is exact only for torque actuators. Ball joints carry 96% of the D line's gear, so the recommendation stands, and the cap must still scale servo gains. |
| **A2** | **OVERSTATED** | *"83% of the D line's work is on joints whose child overlaps its parent by more than 2 cm, usually a tilted attachment. About 35% is on children genuinely inside (centre inside, or at least half their volume). 97% is on children touching nothing."* The sd < −2 cm metric counts any tilted attachment: only 17% of the D line's pairs are at least half inside, and they carry 34% of its work. **The waste is unobstructed rotation on range-less ball joints (94% of the D line's work), not embedding.** Two further points: *"The filter is weld-group, not parent: 45–120% more pairs are filtered."* Fixed links let limbs pass through grandparents, fixed siblings never collide, and the contact sensor is blind inside a weld group. *"Orientation mutation is unclamped (`genetics.py:209`)"*, so the ±π/2 range holds only at founding. **The load-bearing fix is the ball-joint cone plus a range on unlimited hinges.** The outward clamp is secondary, and it would have to act at synthesis. |
| **A3** | **HOLDS-WITH-CAVEAT / OVERSTATED** | *"14 of 120 holistic bodies drift more than 0.25 m with motors off, and none of 120 designed bodies do. Motors-off food is 1–4 items over 30 bouts per group, mostly static reach, and is not evidence that drift buys food."* The "240" in the body is wrong: it included the 120 designed members. *"Part of the drift is terrain rolling"*: a 5 s settle cuts the drifters from 14 to 5, but some bodies then drift more. So settle-until-rest is a partial fix, and the motors-off readout column stands. |
| **A4** | not separately re-derived | Unchanged. |
| **A5** | **OVERSTATED (misattributed)** | *"A single constant full-throttle motor, with no sensor, nets about +0.7 per season at any arm length from 0.45 m to 6.5 m. […] Long-arm reach is not reached by selection in steps; the allowance is blind tumbling, which belongs with finding C2/C3 (coverage), not with the eating geometry."* The geometry facts stand (a 6.46 m arm is legal, and clearance is measured from the root), but the rod sweeper is not an eating-geometry exploit. **Blind full-throttle tumbling goes to auditor C's coverage finding.** The eating-geometry flags remain hardening, not a demonstrated allowance. |

### Revised recommended order (supersedes the one at the end of this document)

1. **A1 cap (c = 1.77)**, with Σgear/(4M) reported per line, a test that pins the Pioneer's 0.5% margin, and servo
   gains scaled by the same factor.
2. **Ghost rotors: a ball-joint cone (`ball_cone`), plus a range on unlimited hinges.** This is the load-bearing fix.
3. **The outward-limb clamp, applied at synthesis** (mutation is unclamped), together with a decision on weld-group
   filtering. This is secondary.
4. **A3:** a motors-off season in every readout. Settle-until-rest is a partial fix, because some of the drift is
   terrain rolling.
5. **A4:** the part cap on reachable nodes, with auditor B.
6. **A5:** report span and eating footprint. The eating-rule, clearance and extent flags are optional hardening.
   Blind tumbling goes to auditor C's coverage finding.

---

**Scope:** `world.py`, `simulation.py`, `synthesis.py` and `genotype.py`, read against RBT-113's committed lines.

**Question:** where can body evolution buy fitness through an allowance of the physics or body model, rather than
through the behaviour the experiment means?

**Method:** read-only. The probes are in this folder and write nothing into any run.
- They use RBT-113 arms O1 and Z1: 6 seed directories, all restored at 216/216 with `scripts/durable.sh restore`
  into a scratch copy.
- They cover generation 23 of the U, D and C lines plus the regenerated founders, for both faunas.
- They run on decompose.py's first fixed draw (terrain 1131, start 2131).

| probe | what it measures | cost |
|---|---|---|
| `probe_static.py` → `probe_static.txt` | build-time only, every member (1,920 bodies): gear under each RBT-120 rule, part cap, recessive nodes, mass scale, extent, eating footprint, self-overlap at build | 20 s |
| `probe_passive.py` → `probe_passive.txt` | 5 members per group per directory (240): a full season with **every motor command held at 0**, on the draw's terrain and on flat ground, next to the intact season | 2 min |
| `probe_ghost.py` → `probe_ghost.txt` | 3 per group per directory (144): parent–child interpenetration per tick, and the share of work done on joints whose child is inside its parent | 1 min |
| `probe_synthetic.py` → `probe_synthetic.txt` | hand-built bodies that reach allowances no committed line has reached yet: a star hub and a rod sweeper | 15 s |

## Summary: the ranked list

| # | allowance | already exploited? | how easily evolution reaches it | size | fix cost |
|---|---|---|---|---|---|
| **A1** | **Motor capacity is not budgeted** (RBT-120). Gear = 4 × the heavier mass, per driven DOF: a hub's mass is counted once per DOF per child. | **Yes.** RBT-113's holistic D line, and all of RBT-117's margin. | Already reached at every seed. One child on a driven ball joint gives 2.95 × the Pioneer's 1.76. | **Unbounded in branching.** A 12-child hub reaches 30× and burns 16.5 yield per season (Pioneer: 0.97). | Small: one flag, one scale factor in `build_xml` |
| **A2** | **Ghost limbs.** A child never collides with its parent. Ball joints have no range, and a child's orientation (±π/2) can point it back into its parent, so limbs are built inside their parent and spin through it freely. | **Yes, as the engine of A1.** 79% of holistic parent–child pairs start embedded. **83% of the D line's work is done on joints whose child is inside its parent.** Designed body: 0. | It is the default outcome: 73% of pairs are already embedded in the founders. | It turns A1's capacity into pure free spin: unobstructed rotors at 20 rad/s. Whether it also buys locomotion is untested. | Medium: an orientation clamp and a ball-joint cone, in synthesis and world |
| **A3** | **The settle ends before the body is at rest.** Velocities are zeroed after 1 s, but a body that has not reached a static pose keeps toppling or creeping after the clock starts. This is what remains of the spawn drop. | **Partly.** With motors off, 14 of 240 holistic bodies drift more than 0.25 m (up to 1.37 m; 0.82 m on flat ground). Designed body: 0 m. Motors-off food equals, or exceeds, the intact food of the holistic founders and C line on this draw. | Free: it needs only an unstable pose. | Up to 0.8 m on flat ground, against a 2 m start distance in bouts. In foraging it is a floor about the size of the founders' food. | Small: settle until kinetic energy falls below ε |
| **A4** | **Recessive nodes raise the part cap for free.** `max_parts = ceil(2 × len(nodes))` counts nodes that are never built. | **Yes, carried.** Holistic lines hold 1.0–2.5 unreachable nodes each, and their part cap (6.9–10.5) is about twice the parts they build (4.3–5.9). | Any node-add mutation that is not connected. | It multiplies A1 (the hub needs it beyond 3 children) and any per-part allowance (A5). | Trivial: count reachable nodes. Shared with auditor B |
| **A5** | **Eating geometry.** Eating is from a geom **centre**, **xy only**, and food clearance is measured from the **root**, not from any geom. Unit-volume normalisation with dims clipped to [0.05, 5] allows a 6.5 m arm at 15 kg. | **Not yet.** Committed spans are at most 1.6 m, and there is no footprint beyond clearance. | Reachable by `dims` mutation (σ 0.2, log-normal) over about 20 steps. | A 2-part rod with **one hinge and no sensor nets +0.61 per season**; the holistic U line eats 0.85. It gets **0.10 per season with its motor off.** | Medium: an eating rule, a clearance rule, an extent cap |

**Lower-ranked allowances (examined, with evidence below):**
- servo force is unbounded on unlimited position hinges;
- an exploded season books 0, which acts as a floor under a negative net;
- passive joints are unbilled and nearly undamped;
- the mass budget dilutes density rather than size;
- self-contact and the sensor count;
- soft contacts, which let the designed body sink up to 0.35 m into the terrain (the readout adversary's N1).

I found **no allowance in the integrator or timestep.** probe_work showed that the work converges under dt/2 and
dt/4, and neither the probes here nor probe_work saw an explosion.

---

## A1. Motor capacity (RBT-120)

**Mechanism** (`world.py:202–223`):
- `gear = motor_strength × max(child mass, parent mass)` for every driven DOF, and a ball joint carries up to three.
- A driven joint's damping is `0.05 × gear` (`world.py:206`). So the no-load speed is 20 rad/s for every motor, and
  the full-throttle free-spin power is gear²/damping = 20 × gear.
- **Power is therefore proportional to gear.** Under the current damping rule, "budget power" and "budget gear" are
  the same rule.
- The mass budget scales masses, so gear scales with them. But **the heavier part's mass is counted once per driven
  DOF of each of its children**, with no bound:

  Σgear ≤ 12 × M × (1 + the largest number of driven children on one part).

**Evidence** (`probe_gear.txt`, from the RBT-113 readout adversary; this folder's `probe_static.txt`):
- The holistic D line reads Σgear/(4 × mass) = 3.57, with a maximum of 6.35 on these 6 directories, against the
  Pioneer's 1.7605.
- This is RBT-117's whole margin: with the D line's work capped at the designed D line's, d = −0.02.

**How far it goes** (`probe_synthetic.txt` S1): a 13.5 kg sphere with k light boxes on driven ball joints, full
throttle.

| k children | Σgear/(4 × mass) | free-spin ceiling (yield per 15 s) | work actually burnt (yield) |
|---|---|---|---|
| 1 | 2.95 | 1.46 | 1.44 |
| 3 | 8.60 | 4.37 | 4.33 |
| 12 | 30.3 | 16.7 | 16.5 |
| Pioneer | 1.76 | 0.97 | 0.93 (the designed D line) |

Nothing explodes. At k ≥ 24 the children jam each other and the burnt work falls.

### The RBT-120 budget options, with numbers

**A note on the ticket's figure.** The ticket's "Σgear/mass = 1.76" is **Σgear / (4 × mass)**. The Pioneer's raw
Σgear/mass is 108 / 15.337 = 7.04, and exactly Σgear/(4M) = 2 × 13.5 / 15.337 = **1.7605**. Each drive wheel is keyed
to the 13.5 kg chassis.

Each rule was evaluated on every member of the six restored directories (`probe_static.txt`; ratios are Σgear/(4M)):

| rule | Pioneer | holistic D | holistic U | founders | 12-child star | verdict |
|---|---|---|---|---|---|---|
| current | 1.7605 | 3.57 (max 6.35) | 1.05 (max 3.66) | 0.56 | 30.3 | |
| (a) key to the **child's** mass | **0.060** | 0.22 | 0.62 | 0.16 | 0.47 | **Rejected.** It cuts the Pioneer's motors by 29× (its wheels weigh 0.46 kg). Recalibrating `motor_strength` would restore the Pioneer, but it would then pay heavy children instead of heavy hubs. |
| (b) **share** one gear across a ball joint's DOFs | 1.7605 | 1.46 | 0.69 | 0.50 | **10.1** | Not enough alone: it removes the ×3, not the hub multiplier. |
| (c) **cap** Σgear ≤ c × 4 × M, rescaled uniformly when over, **c = 1.77** | **1.7605 (untouched)** | 1.66 (91% of members capped) | 1.02 (7% capped) | 0.55 (5% capped) | **1.77** | **Recommended.** It is one dimensionless constant, blind to topology, and it bounds the ceiling at the Pioneer's 0.97 yield exactly. |
| (d) budget power (gear²/damping) | — | — | — | — | — | The same as (c) while damping = 0.05 × gear. Prefer (c): it does not depend on the damping rule. |
| (b) + (c) | 1.7605 | 1.37 | 0.69 | 0.50 | 1.77 | Optional hardening. It changes more founders than (c), so it moves more committed baselines under the flag. |

**The recommended flag.** Add `WorldConfig.gear_budget: Optional[float] = None`, in units of motor_strength × total
mass.
- **When it is set:** `build_xml` computes the robot's Σgear over driven DOFs first. If that exceeds
  `gear_budget × motor_strength × M`, it multiplies every driven gear, and the damping keyed to it, by the ratio.
  Scaling damping with gear keeps the no-load speed at 20 rad/s, so the cap bounds torque and power together.
- **When it is None:** the XML is byte-identical.
- **Also cap the servos.** Position and velocity servos take their gains from `gear` (`_add_scalar_actuator`), so the
  same factor caps them too.
- **Reporting, now:** add Σgear/(4M) per line to every holistic-against-designed readout. `probe_static.py`'s
  `measure()` is enough.

**Cheap test** (`tests/`):
1. The Pioneer's MJCF is byte-identical with the flag off, and also with `gear_budget = 1.77` (its ratio is 1.7605).
2. S1's 12-child star reads Σgear/(4M) ≤ 1.77 + 1e-9 and a free-spin ceiling of at most 0.98 yield with the flag on.
3. One RBT-113 holistic D member's season work drops to at most the designed D line's (about 31 kJ).

**Committed results it could affect:**
- RBT-113's holistic D and divergence estimates (b_down, b_div);
- RBT-117's HOLISTIC RESPONDS MORE;
- any holistic "waste" or work-cost result since `--work-cost` existed (papers 8–10, if they compare work across
  faunas);
- arena bouts: the follow-up paper and RBT-9 onwards, where torque wins shoving contests.

## A2. Ghost limbs: children built inside their parents, spinning through them

**Mechanism:**
- MuJoCo filters out every contact between a body and its parent. `world.py` never re-enables it, and no other
  exclusion exists.
- `synthesis.py:232` sets `rel = align_x_to(normal) · euler(orientation)`, with `orientation` drawn from ±π/2 on each
  axis (`genotype.py:535`). A child therefore often points **into** its parent. Its geom sits at `geom_offset =
  half_length` along the child's own +x, which lies inside the parent.
- A ball joint gets **no range** (`world.py:217`). Hinges are unlimited 20% of the time.
- **Result:** a limb can sit inside the torso and rotate through it without any contact: a free internal rotor.

**Evidence** (`probe_ghost.txt`, 18 members per group; shares of parent–child pairs or ticks with more than 2 cm
interpenetration):

| | pairs embedded at the start | ticks with an embedded child | deepest (× part size) | **share of work done on embedded joints** |
|---|---|---|---|---|
| holistic founders | 0.73 | 0.83 | 0.57 | 0.66 |
| holistic U | 0.79 | 0.92 | 0.98 | 0.85 |
| **holistic D** | **0.79** | **0.92** | **1.05** | **0.83** |
| holistic C | 0.52 | 0.72 | 0.80 | 0.56 |
| designed (all lines) | 0 | 0 to 0.004 | 0 to 0.10 | 0.000 |

**Reading:**
- The D line's "full-throttle free spin" (the readout adversary's §3: 60% of work at saturated command, and a work
  ceiling of 85%) is mostly **rotors spinning inside their parents**, where nothing can obstruct them.
- A motor that is loaded against the world cannot reach its free-spin ceiling. A ghost rotor can.
- So **A2 is what makes A1's capacity cashable as waste.** Under A1's cap, A2 alone gives no more than the Pioneer's
  ceiling.
- Whether ghost rotors also buy **positive** fitness (reaction-wheel steering, or an embedded paddle that protrudes
  and rows) is **not tested here**. That is the next probe: the U line's intact food with parent–child collision on,
  against off.

**Fix** (`SynthesisConfig.outward_limbs: bool = False`, plus `WorldConfig.ball_cone: Optional[float] = None`):
1. At synthesis, clamp the child's orientation so its +x axis stays in the outward hemisphere of the attachment
   normal. Equivalently, reject an Euler rotation whose rotated x has a negative dot product with the normal, and
   reflect it.
2. Give ball joints a MuJoCo `range="0 ball_cone"`, for example π/2. MuJoCo's ball-joint range is a cone.

Contact filtering can stay as it is: an anchor contact would jam every joint. Both flags are off by default and
byte-identical when off.

**Test:** `probe_ghost.py` with the flags on reads 0 for "pairs embedded at the start". A spinning embedded-rotor
genotype (S1 with orientation (0, π/2, 0)) burns at most 0.1 of the work it burns with the flags off.

**Committed results it could affect:** the same as A1. Also every holistic morphology description that counts
"limbs": a limb inside the torso is not a limb.

## A3. The settle leaves bodies moving: the spawn drop's remainder

**Mechanism:**
- `Simulation.settle` (`simulation.py:166`) steps for 1 s with zero command, then zeroes the velocities and
  re-centres the COM.
- It does **not** check that the body has reached a static pose. A body that was still toppling, rocking on a passive
  ball joint or sliding keeps going after the velocities are zeroed, from its remaining potential energy.
- Passive joints carry damping of only `0.05 × 4 × child mass` (`world.py:206`), about 0.1 N·m·s. They take seconds
  to come to rest.

**Evidence** (`probe_passive.txt`, 30 members per group, motors held at 0 for the whole season):

| | disp, motors off (mean / max, m) | same on flat ground (max) | food, motors off | food, controller on |
|---|---|---|---|---|
| holistic founders | 0.08 / 1.13 | 0.82 | 0.033 | 0.033 |
| holistic U | 0.13 / 1.37 | 0.40 | 0.033 | 0.700 |
| holistic D | 0.07 / 0.30 | 0.30 | **0.133** | 0.233 |
| holistic C | 0.08 / 0.79 | 0.79 | **0.100** | **0.067** |
| designed (all lines) | **0.000** / 0.000 | 0.000 | 0 | 0.03–0.30 |

- 14 of 240 holistic bodies drift more than 0.25 m with no motor output. Most of them move as far on flat ground as
  on the terrain, so this is the protocol, not a roll off an obstacle.
- **On this draw, the holistic founders' and C line's entire intake is matched by the motors-off intake.**
- The designed body never moves.

**Size and reach:**
- It is small in foraging on average, but it is a floor that needs no controller.
- In **arena bouts** it is the follow-up paper's spawn artefact in slow motion. Up to 0.8 m of free, body-determined
  displacement against a 2 m start distance, and the spawn yaw faces the centre, so a topple direction fixed in the
  body frame is aimable.
- The follow-up paper's post-fix champions gained −0.25 to −0.07 m alone from rest, so it was **not** exploited
  there. It is reachable, though, because nothing penalises it.

**Fix** (`SimConfig.settle_until_rest: float = 0.0`): when it is > 0, keep settling in 0.25 s chunks, zeroing
velocities after each chunk, until the robot's peak body speed over a chunk falls below this threshold (for example
0.01 m/s), up to a cap of 5 s. Log the seconds used. At 0.0 the behaviour is the current one, byte-identical.

**Reporting, now:** a **motors-off season** (`probe_passive.py`'s `season(..., off=True)`) belongs in every readout
next to blind and decoy. It is the null for "moves by itself".

**Test:** `probe_passive.py` with the flag on shows motors-off displacement below 0.05 m for every member, and the
designed body's intact results are unchanged.

**Committed results it could affect:**
- every arena-bout result (the follow-up paper, RBT-9 onwards) at the margin;
- in foraging, the floor of the founders' and C lines' food. RBT-113's founders and C-line baselines include it.

## A4. Recessive nodes raise the part cap for free

**Mechanism:** `SynthesisConfig.max_parts(len(genotype.nodes))` (`synthesis.py:194`) counts every node, including
nodes that no connection reaches and that are never built. One unreachable node raises the cap by 2 parts, at zero
cost.

**Evidence** (`probe_static.txt`):

| | recessive nodes (mean) | part cap | parts built |
|---|---|---|---|
| holistic U | 1.9 | 8.9 | 4.7 |
| holistic C | 2.5 | 10.5 | 5.9 |

In S1, beyond 3 children the only way the hub gets more motors is through added unreachable nodes: k = 12 needs 5 of
them. The cap is therefore the only brake on A1's branching, and recessive nodes release it.

**Fix** (`SynthesisConfig.cap_on_reachable: bool = False`): pass `len(genotype.reachable_nodes())` to `max_parts`.
Off is byte-identical. **Hand this to auditor B**: the operators decide how cheaply nodes accumulate.

**Test:** S1's k = 12 genotype synthesises at most 4 parts with the flag on.

**Committed results it could affect:** none directly. It is a multiplier on A1 and A5.

## A5. Eating geometry: centres, xy, root clearance, and 6 m limbs

**Mechanisms** (`simulation.py:466–490`, `synthesis.py:124`, `genetics.py:201`):
1. **An item is eaten when a geom's *centre* is within 0.35 m in xy.** Height is ignored, so a part held 1 m up eats.
   Part surfaces are also ignored: a 0.6 m part eats only around its middle, and a long thin part's centre sits at
   half its length from its joint.
2. **Food clearance is measured from each robot's root body** (`_robot_positions`), not from its geoms. This applies
   to the initial placement and to every regrowth. An item can therefore appear inside the reach of a far limb, and
   be eaten on the next tick with no motion.
3. **The size clamp bounds `size`, the cube root of the volume, not the extent.** Relative dims are clipped to
   [0.05, 5] and then normalised to unit volume. A (5, 0.05, 0.05) box at size 0.3 is **6.46 × 0.065 × 0.065 m**, and
   the mass budget scales its mass to 15.34 kg without touching the geometry.

**Evidence** (`probe_synthetic.txt` S2): a 0.3 m cube with **one** such arm on an unlimited vertical hinge, full
throttle, **no sensor**. The arm's centre sweeps a 3.4 m circle. Results over 20 start draws:
- **motor on:** food 0.70, work 0.09, **net +0.61**. For comparison, the holistic U line's intact food is 0.85 and the
  designed U line's is 1.3 (`probe_food.txt`).
- **motor off:** food 0.10 per season, all from items placed within reach of the arm's centre, which is 3.4 m from
  the root. For comparison, the holistic founders' food is 0.11.

**It is not yet exploited:**
- No committed body spans more than 1.6 m.
- The footprint beyond clearance is 0 to 0.11 m².
- The eating footprint is smaller for holistic bodies than for the Pioneer: 0.60–0.67 m² against 0.86 m².

**Reach:** about 20 successive dims mutations in one direction, each rewarded because coverage pays (papers 5–6, and
RBT-113 §4). It is a direct route to the "blind mower" that auditor C's economy already rewards.

**Fixes:**

| flag | what it does | test |
|---|---|---|
| `FoodConfig.eat_rule: str = "centre"` | "surface" uses MuJoCo's geom-to-point distance (a tiny sphere probe at the item, z = 0), with eat_radius measured from the **surface**, and requires the geom to be within 0.1 m of the ground. It gives size its physical reach and removes airborne eating. | S2's motor-on food falls to what a 6.5 m sweeping edge should earn, which is the honest rule. The Pioneer's food changes, so it is **not** comparable across the flag, and that has to be said at registration. |
| `FoodConfig.clear_from: str = "root"` | "geoms" measures clearance from every geom centre | S2's motor-off food falls to 0 |
| `SynthesisConfig.max_extent: Optional[float] = None` | clamps any absolute dimension to this value, for example 0.6 m, after normalisation | S2's arm is at most 0.6 m, and the Pioneer is untouched (its largest extent is 0.42 m) |

**Committed results it could affect:** none that are measured yet. Any future foraging result is at risk once a line
grows long parts. At minimum, **report span and eating-footprint area per line** (`probe_static.py` gives both).

---

## Lower-ranked allowances: examined, and not worth a fix before RBT-116/118

- **B1. Servo force is not bounded by gear.**
  - A position servo's bias is `−kp·q` (`world.py:271`). On an **unlimited** hinge, q winds without bound, and so
    does the torque.
  - A velocity servo gives up to 2 × gear when it is back-driven.
  - Work is billed as |F·v| both ways, so this does not help net yield. It could help arena bouts, where nothing is
    billed.
  - **Fix:** add `forcerange = ±gear` under a flag. **Test:** the actuator force never exceeds gear.
- **B2. An exploded season books 0** (`simulation.py:525`). For any member whose net would be negative, exploding is
  a floor.
  - RBT-30 saw about 1 in 60 founders explode. No explosions appeared in these probes, in probe_work, or in the
    lineages.
  - Worth one line in auditor C's economy. A physics fix is not needed.
- **B3. Passive joints are free and nearly undamped.** Only actuators are billed. Passive dynamics (A3) and gravity
  are unbilled by design.
- **B4. The mass budget dilutes density, not size.**
  - The holistic U line's mass is scaled to 0.62 of its build, so its bodies are about 1.6× the volume a
    15.34 kg body of this density would have.
  - It is harmless now: the eating footprint is smaller than the Pioneer's. It is the channel through which A5 would
    become cheap.
  - The follow-up paper's limitations section already says the budget "equalises mass but not size".
- **B5. Build-time overlap between non-parent parts.**
  - Holistic bodies average 1.3–4.1 same-robot contacts at build, up to 0.27 m deep. The designed body has none.
  - The settle resolves them: during the season, same-robot penetration is at most 0.095 m, and the group means are
    under 1 cm (`probe_passive.txt`, `selfpen`).
- **B9. Soft contacts let a body push deep into the terrain.**
  - The readout adversary's N1 (0.27–0.57 m) is **not** self-contact. On this draw the deepest penetrations of any
    kind are the **designed U line's: 0.35 m**, with the controller on. Every holistic group stays at or below
    0.095 m.
  - With `solref 0.01 1` and `solimp 0.9 0.95 0.001` (`world.py:171`), a 13.5 kg chassis driven at full torque
    against an obstacle can sink into it. That is partial passage through terrain that should block, and it helps
    whichever body pushes hardest, which today is the designed one.
  - **Fix:** add `WorldConfig.contact_solref` / `solimp` as flags, and a probe of the deepest robot–scenery
    penetration per line.
  - **Test:** the deepest penetration stays below 2 cm on the same replays.
  - This is ranked low because it has not been shown to change food or bout outcomes, but it is worth one probe
    before RBT-116/118 if they use random terrain.
- **B6. Sensors.**
  - `contact` fires on self-contact, but never parent–child, because of the filter in A2.
  - Every geom can carry its own smell sensor, so the sensor count is unbudgeted.
  - The foraging vocabulary has no target oracle.
  - None of this pays today: smell is unused (probe_food, blind ≈ decoy ≈ intact).
- **B7. Integrator and timestep.** Work converges at dt/2 and dt/4 (probe_work). The explosion cut is at 200 m/s,
  and the largest speed seen here was 10.4 m/s. I found no gain from instability.
- **B8. Slider joints.** The range is `joint_limit × size`, at most π × 0.6 = 1.9 m after mutation (`genetics.py:223`).
  With the A2 filter, a slider can drive its child through its parent. It is covered by A2's fix: the outward clamp
  only has to keep `geom_offset` outside at the neutral position.

## Recommended order

1. **A1 cap (c = 1.77)**, with Σgear/(4M) reported per line. This is RBT-120. It is the only allowance with committed
   damage.
2. **A2 outward limbs and ball cone**, which removes the free-spin rotor that made A1's damage cashable.
3. **A3 settle-until-rest**, plus a motors-off season in every readout.
4. **A4 part cap on reachable nodes**, with auditor B.
5. **A5 eating rule, clearance from geoms and max extent**, with auditor C. At minimum, report span and footprint now.

Each of these is a flag that is off by default and byte-identical when off. Each still needs a designer, a design
adversary and a ruling before it touches `rabbitstew/`.
