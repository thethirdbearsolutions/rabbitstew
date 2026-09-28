# RBT-124 design: the physics fairness pack

**Designer, 2026-09-27.** RBT-121's fix-list items 2, 3 and 6 (`runs/RBT-121/SYNTHESIS.md` R1–R3), plus R8's lever
report. Three flags, each **off by default and byte-identical when off** (MJCF and `config.json`), each with its own
tests in `tests/test_rbt124.py`.

**Nothing here changes a committed result.** No arm has run. The numbers below re-score restored RBT-113 genomes
under the flags; they say what each flag would change, not what a rerun would find.

| flag | where | CLI (`evolve`, `ecology`; `simulate` for the physics ones) | off |
|---|---|---|---|
| `ball_cone` (rad) | `WorldConfig` | `--ball-cone RAD` | 0: no `range` on a ball joint |
| `hinge_range` (rad) | `WorldConfig` | `--hinge-range RAD` | 0: unlimited hinges stay unlimited |
| `effector_bias_sigma` | `MutationConfig` | `--effector-bias-sigma S` | unset: the operator as it was |
| `settle_until_rest` (m/s) + `settle_max` (s) | `SimConfig` | `--settle-until-rest EPS [--settle-max S]` | 0: the plain 1 s settle |
| lever report | `rabbitstew/levers.py` | `python -m rabbitstew.levers NAME=DIR ...` | – |

**The sample.** Unless stated otherwise, "the RBT-113 sample" is the one the RBT-121 probes used: seed directories
O1/1–3 and Z1/Z1–Z3, restored at 216/216 with `scripts/durable.sh restore … rbt-113-{O1,Z1}`, the regenerated founders
plus the U, D and C lines' final generation (23), **both faunas**, 5 members per group per directory (rng 124), scored
on all four of `decompose.py`'s registered draws (terrains 1131–1134 with their start seeds). That is 120 holistic and
120 designed member-seasons per group. `sample.py` → `sample.txt` holds every row quoted.

## Amendments after the design adversary (#423) and the coordinator's ruling (23:35)

The adversary's verdict was MERGE AFTER FIXES; the ruling accepted all three MUST and all eight SHOULD items. Where
this file and the first draft (5c959ba) disagree, this file wins. The numbers in §1.3 and §7 are re-measured on the
amended tree.

| item | what changed | where |
|---|---|---|
| **M1** | a hinge wheel must be a **leaf**; a wheel carrying a part is a propeller and is ranged (tested: propellers fall to 0.006–0.009) | `world.is_wheel(part, leaf)`; §1.2 |
| **M2** (option 1) | under the cone, a **round leaf on a ball joint** is a steerable wheel: the cone on its mount, an unlimited spin hinge about its own axis; byte-identical off; its own tests. §1.2's false "the same wheel" claim is corrected, and the U line's food is re-reported: **0.14 a season under the ranges, 0.22 under the pack** (0.07 in the first draft) | `world.is_ball_wheel`; §1.2, §1.3 |
| **M3** | the lever report takes the motor budget, ranges and settle **from each run's `config.json`** unless overridden, and prints the physics used | `levers.main`, `apply_overrides`; §4 |
| S1 | registered: an airborne wheel is a contact-free rotor, for both faunas; the report books wheel work apart (`wheel J`, `wh.free`). **Under M2 it is 7.4 kJ a season on the holistic D line** | §1.2, §1.3, §4 |
| S2 | a cone outside (0, π), a range ≤ 0, a negative ε or `settle_max` < `settle_time` is refused; one range flag alone warns | `world.check_ranges`, `Simulation.__init__`, `cli` |
| S3 | the help and docstrings describe kinetic damping, not "velocities zeroed between chunks" | `cli`, `SimConfig` |
| S4 | "the designed body is bit-identical" is scoped to solo seasons (a bout moves its start by ≤ 6e-9) | §3.2 |
| S5 | registered side effect: before a locomotion or foraging reading under the pack, fix 12 is in or `pen>1cm` is printed per line | §3.3 |
| S6 | `--draw` repeats, and the rows pool the draws | §4 |
| S7 | "motors off" is ctrl 0: position servos hold, velocity servos brake | §3.2, `levers` docstring |
| S8 | exploded seasons are counted apart and kept out of the work, food and share means | `levers.line_summary` |

---

## 1. `ball_cone` + `hinge_range`: no free rotors

### 1.1 What is wrong (RBT-121 A2 as corrected by the adversary, §2)

- A ball joint has **no range** (`world.py`, `type="ball"` with no `range`), and 20% of founding hinges are unlimited
  (`genotype.py:540`). A driven limb on either can spin for ever.
- 97% of the holistic D line's work is on children that touch nothing; 94% is on ball joints. A motor loaded against
  the world cannot reach its free-spin ceiling; a free rotor can (ADVERSARY §2b).

### 1.2 Decisions

**Ball joints: MuJoCo's own cone, `range="0 ball_cone"`.**
- For a ball joint MuJoCo limits the **angle of the joint's whole rotation** (the axis-angle magnitude of its
  quaternion), so the limit binds swing *and* twist. A ball-jointed limb can no longer spin about any axis, its own
  long axis included; a constant torque drives it into the limit, where it stalls and does no work.
- `ball_cone = π/2`: the example auditor A gave, and the widest swing a founding limited hinge can have (founding
  limits are drawn from U(0.3, π/2)). It must be below π: at π the limit is the whole rotation group, i.e. no limit.
- The joint starts at the identity (angle 0), so no body starts outside its cone. Limit solver parameters are MuJoCo's
  defaults, as for every existing limited hinge.

**Unlimited hinges: `hinge_range` for every one that is not a leaf wheel.** *(Amended per the design adversary's M1.)*
- The designed Pioneer's four wheels are unlimited hinges. Ranging every unlimited hinge would stop them, so the rule
  must say what a wheel is.
- **A hinge wheel is a round part (cylinder or sphere) that carries no child part, hinged about the axis through its
  own centre along its length** (`world.is_wheel(part, leaf)`: shape, leaf, and |cos| ≥ 0.999 between the hinge axis
  and the child's x axis, on which the geom's centre and a cylinder's length lie). Turning such a part sweeps no new
  volume. **It must be a leaf**: everything fixed or jointed to a wheel turns with it, so a wheel carrying a blade is a
  propeller (the adversary's `launder.txt`: a bladed wheel, a sphere propeller and a hub of bladed wheels kept all
  their work before the leaf rule; with it they fall to 0.006–0.009, tested). The Pioneer's wheels are leaf cylinders
  on axis (1, 0, 0), so **its MJCF is byte-identical** with both flags on.
- Every other unlimited hinge gets `range = ±hinge_range`, with `hinge_range = π/2` to match the cone. Limited hinges
  and sliders keep their genotype's range. A position servo on a newly ranged hinge servos over ±hinge_range (as a
  limited hinge servos over its range) instead of ±π; its peak force is still its gear.
- `hinge_range` and `ball_cone` are separate flags because they bind different joints; setting only one now warns
  (S2), and a meaningless value (a cone outside (0, π), a range ≤ 0) is refused.

**Ball-mounted wheels: a round leaf on a ball joint gets free spin about its own axis** *(new, per the adversary's
M2, ruled for option 1: parity by construction, R6).*
- **What the first draft claimed, and why it was false.** DESIGN §1.2 said "a holistic body may evolve the same
  wheel under the same rule". The adversary measured it (`reach_wheel.txt`): **0 of 480** holistic bodies in RBT-113
  O1 meet the hinge-wheel rule, against all 480 designed bodies; a founding axis lands in the 2.6° cap with probability
  0.001 and a found wheel is lost at its next axis mutation with probability 0.995. The holistic encoding builds its
  wheels on **ball joints** (469 round parts on ball joints, 371 of them leaves). The first draft's cone took all of
  those away and left the Pioneer's.
- **The rule now.** Under `ball_cone`, a **round leaf part on a ball joint** (`world.is_ball_wheel`) keeps the cone on
  its ball joint, which now carries a steering mount, and gains an **unlimited hinge about its own x axis**: a
  steerable wheel. It is the ball joint's twist DOF re-expressed as a wheel's spin. The twist DOF's motor, if driven,
  drives the spin; the other two DOFs' motors stay on the coned ball.
- **How it is built.** MuJoCo allows no rotation after a ball joint in one body, so the ball joint goes on a mount body
  with a negligible inertial (1e-6 kg), and the part's own body (its name, its geom, its mass) hangs from it with the
  spin hinge. The mount breaks MuJoCo's parent filter between the part and its parent's weld group, so explicit
  `<exclude>` pairs restore exactly that set (the parent and every part FIXED to it). Off, none of this is written: the MJCF is byte-identical. DOFs, actuators, the unlimited spin and the
  coned mount are tested.
- **What each fauna now has.** The designed body: its four leaf hinge wheels, unchanged. The holistic fauna: every
  round leaf on a ball joint is a steerable wheel (the encoding's own wheel: 371 such parts across RBT-113 O1's 480
  holistic bodies), and a leaf hinge wheel if it ever evolves one. Neither fauna can hang a rotor on a wheel (the leaf rule), and
  neither can spin a non-round limb.
- **S1, registered: an airborne wheel is still a contact-free rotor, for both faunas.** A wheel spinning in the air
  sweeps no volume but burns its motor's work touching nothing, exactly as a free rotor does (the reference wheel:
  16 kJ a season at full throttle, all contact-free). No geometric rule can tell a wheel in the air from a wheel on
  the ground; the Pioneer's wheels would do the same if lifted. R8's report books it apart: `wheel J` (the work of
  wheels' spin motors) and `wh.free` (the part done touching nothing). **Under M2 this residual is large on the
  holistic D line** (§1.3): its free rotors were mostly round leaves, and they are now airborne wheels.

**No outward-orientation clamp at synthesis: not needed for free rotation, and not in this pack.**
- The adversary's finding stands: the waste is **unobstructed rotation, not embedding**. Under the cone, an embedded
  rotor and an outward one burn the same (`rotor.txt`: S1 with orientation (0, π/2, 0) burns 0.006 of its unfixed work,
  the same hub with orientation (0, 0, 0) 0.006).
- What a clamp would still remove is a limb that **oscillates** inside its parent, within the cone. Under the flags the
  holistic D line's work on children at least half inside their parent falls from 0.29 (pooled share) × 44.7 kJ ≈
  13 kJ a season to 0.08 × 11.8 kJ ≈ 0.9 kJ (`sample.txt`, `w_v50`, amended tree). That residual is an order below the rotor it
  replaces, and R8's report now prints it per line (`w_v50`, and the share of pairs ≥ 50% inside at the start), so a
  line that learns to exploit it will show it.
- A clamp would also have to act **at synthesis** (orientation mutation is unclamped, `genetics.py:209`), which
  changes the genotype-to-body map of every holistic body, founders included, and would not touch the grandparent
  pass-through below. It is a candidate for a later ticket if `w_v50` grows, not a precondition for this one.

**Weld-group filtering: unchanged, and now bounded.**
- MuJoCo never collides geoms of one weld group (a FIXED link welds the child into its parent's rigid body, so there
  is nothing for a contact to do), and `filterparent` filters a jointed child against its parent's whole weld group.
  So a limb passes through its grandparent across a fixed link, fixed siblings never collide, and the contact sensor
  is blind inside a weld group (ADVERSARY §2a).
- **Re-enabling parent contacts is not an option**: a child geom starts on its parent's surface, so every joint would
  start in contact and jam (auditor A reached the same conclusion). Excluding only the direct parent and re-enabling
  the grandparent would fail the same way wherever parent and grandparent overlap, which fixed links make common.
- **What the cone changes**: a limb passing through its grandparent can now do so only within ±π/2 of its build pose,
  so the pass-through is an oscillation, not a rotor, and its work is inside the `w_free` share R8 prints.
- **The contact sensor inside a weld group**: correct as physics (a rigid body cannot press on itself); it matters only
  if a registration reads contact as "touching the world", and then it should say so.

### 1.3 Evidence

**A's test: the embedded rotor** (`rotor.py` → `rotor.txt`; RBT-113's generation sim, terrain 1131, start 2131):

| body | work off (J) | work on (J) | on/off |
|---|---|---|---|
| S1 embedded (orientation (0, π/2, 0)), 1 child | 48,069 | 270 | **0.006** |
| S1 embedded, 3 children | 143,804 | 781 | 0.005 |
| S1 embedded, 12 children | 549,268 | 3,007 | 0.005 |
| S1 outward (orientation 0), 12 children | 549,686 | 2,899 | 0.005 |
| rod: 6.5 m arm on an unlimited hinge about the vertical | 3,872 | 51 | 0.013 |
| wheel: a cylinder on an unlimited hinge about its own axis | 16,026 | 16,026 | **1.000** |

Every rotor burns ≤ 0.013 of its unfixed work (the bar is 0.1). The wheel is untouched, bit for bit.

**The RBT-113 holistic lines, with the ball-mounted wheel (M2)** (`sample.txt`, re-run on the amended tree, 120
member-seasons per group, four draws; "work_free" is the work done on children touching nothing; "wheel, free" is the
part of it done by wheels' spin motors, S1; exploded seasons are kept out of the means, S8):

| holistic | work off (J) | work, ranges (J) | work_free off → ranges (J) | of which wheel, free (J) | non-wheel work_free: change | food off → ranges |
|---|---|---|---|---|---|---|
| founders | 770 | 487 | 630 → 376 | 76 | −52% | 0.03 → 0.04 |
| U | 5,665 | 1,192 | 4,519 → 806 | 664 | −97% | **0.98 → 0.14** |
| **D** | **44,716** | **11,803** | **41,729 → 9,747** | **7,430** | **−94%** | 0.10 → 0.07 |
| C | 6,266 | 1,715 | 5,800 → 1,349 | 72 | −78% | 0.16 → 0.06 |

- **The D line's work on contact-free children that are not wheels falls by 94%** (41.7 kJ → 2.3 kJ a season), as in
  the first draft. **Its total contact-free work falls by 77%, not 94%**: 7.4 kJ a season is now airborne wheels, its
  round leaves spinning on their new mounts (S1). Total D work falls 74% (44.7 → 11.8 kJ), against 94.5% before M2.
- **The designed fauna is unchanged in every group**, bit for bit: its only unlimited hinges are leaf wheels.

**The cone's value** (`cone.txt`: holistic sample, draw 0, 30 member-seasons a group, `hinge_range` set equal):

| cone = range | D work (J) | D work_free (J) | U work (J) | U food | exploded seasons |
|---|---|---|---|---|---|
| off | 44,816 | 41,721 | 5,650 | 0.70 | 0 |
| π/4 | 11,602 | 9,173 | 1,323 | 0.37 | 0 |
| **π/2** | 11,424 | 9,691 | 1,202 | 0.07 | 1 (the chattering C body) |
| 3π/4 | 11,615 | 10,029 | 1,334 | 0.03 | 0 |
| 0.95π | 41,487 | 34,895 | 2,315 | 0.73 | 0 |

(Amended tree, with the ball-mounted wheel: most of what is left of D's work at π/4–3π/4 is its airborne wheels.)
Anything up to 3π/4 removes the rotor (D's work flat across π/4–3π/4); near π the limit is nearly the whole rotation
group and the rotor comes back. π/2 sits in the flat middle; the explosion at π/2 alone is the one chaotic body below,
not a property of the value. U's food on this one draw and 30 members is noisy (0.03–0.37 across the flat region).

**The U line's food: 0.98 → 0.07 a season in the first draft, 0.14 with the ball-mounted wheel (0.22 under the whole
pack).** `wheels.py` → `wheels.txt` splits the U and D finals' work by joint and by what the child was doing (30 each,
draw 0; amended tree):

| | work (J) | food | COM travel (m) | ball, limb, touching | ball, limb, free | ball, round, touching | ball, round, free | hinge |
|---|---|---|---|---|---|---|---|---|
| U, off | 6,816 | 0.80 | 2.46 | 0.08 | 0.24 | 0.21 | 0.39 | 0.08 |
| U, ranges (first draft: no ball wheel) | 263 | 0.00 | 0.27 | | | | | |
| **U, ranges (M2)** | 1,236 | **0.33** | **0.68** | 0.01 | 0.03 | **0.44** | 0.50 | 0.01 |
| D, off | 49,899 | 0.13 | 0.25 | 0.01 | 0.34 | 0.04 | 0.60 | 0.00 |
| **D, ranges (M2)** | 14,579 | 0.17 | 0.26 | 0.02 | 0.15 | 0.14 | **0.69** | 0.00 |

- The U line **travels** (2.5 m a season) on spinning ball-jointed parts and eats by covering ground. Under M2 its
  ball-mounted wheels **roll** (the "ball, round, touching" work is 544 J a season, 38% of its 1,431 J off) and it
  travels 0.68 m, against 0.27 m in the first draft. What it loses is the rest of the gait: limbs tumbling on free ball
  joints (32% of its work off, 4% under the rule) and round parts spinning at angles the cone now bounds. The food
  that remains, 0.14–0.22 a season on four draws (0.33 on draw 0), is what the parity-by-construction wheel buys; **a rerun's U founders start
  slower**, as the adversary's walker probe also concludes.
- The D line's leftover work is mostly airborne wheel spin (0.69 of it), which R8 now reports as `wh.free`.

**Instability: one body, and it was already unstable.** Under the ranges, one of the 240 sampled holistic bodies
(O1/2's C line, member 0) is flagged exploded on 3 of its 4 draws, and no other. With the flags off that body already
burns 171 kJ a season with its motors *on*, in chatter between 0.06 kg sliders under position servos; the cone tips a
system on the edge. The explosion guard books such a season as 0, as it books every explosion (RBT-113 adversary §3).
Softening MuJoCo's limit (`solreflimit="0.05 1"`) removed it on draw 0, but that would make every limit softer for
every body, so it is not adopted; the design adversary may weigh it.

**The Pioneer** (`tests/test_rbt124.py`): its MJCF is byte-identical with both flags on, for 5 seeds of its random
controller, rich and plain; a season on the registered terrain has bit-identical final `qpos` and work.

---

## 2. `--effector-bias-sigma S`: the resting-throttle walk

### 2.1 What is wrong (RBT-121 B1)

A link weight resets with probability 0.02 when perturbed; **a bias has no reset and no clip**, so it walks for ever.
An Effector outputs `tanh(bias + input)`, so a walked Effector bias is a motor held at a constant throttle whatever the
sensors say. RBT-112's `global_bias_sigma` does not touch Effectors (they sit on segments, owner ≠ None).

### 2.2 Decisions: B's sketch, exactly

- `MutationConfig.effector_bias_sigma: Optional[float] = None`. When set, an Effector's bias step is
  `rng.normal(0, 1) × S` instead of `rng.normal(0, weight_sigma)`: **the same one draw**, so the random stream is
  unchanged at any S, and S = 0 freezes every Effector bias while every other gene mutates exactly as before.
- It is read in `mutate_weights` from the config, so **every** mutation path honours it: `mutate` (holistic),
  `mutate_controller` (designed, controller topology) and the ecology's plain `mutate_weights` path. Both faunas are
  bound, unlike `global_bias_sigma`, which is designed-body only.
- **A newly drawn Effector** (holistic `_random_unit`) keeps its founding bias N(0, 0.5): that is a gene's birth, not
  the walk; at S = 0 the share at resting drive then stays at the founders' level (below).
- Unset writes the old `config.json`: the key is dropped from the `mutation` block, as RBT-104 and RBT-112 did.

### 2.3 Evidence

**B's cheap test 1** (`bias_walk_s0.py` → `bias_walk_s0.txt`): RBT-121's `bias_walk.py`, same rng, 80 lineages of
RBT-113's seed-1 founders walked by the operator alone:

| | G 0 | G 23 | G 60 | G 150 |
|---|---|---|---|---|
| designed, unset (reproduces `bias_walk.txt`) | 0.0% | 16.9% | 27.5% | 54.4% |
| **designed, S = 0** | 0.0% | **0.0%** | **0.0%** | **0.0%** |
| holistic, unset (reproduces `bias_walk.txt`) | 0.8% | 8.1% | 18.2% | 26.1% |
| **holistic, S = 0** | 0.8% | **0.9%** | **0.0%** | **0.1%** |

(share of Effectors with |tanh(bias)| > 0.9.) The global-unit bias SD and the link-weight RMS are identical between
the unset and S = 0 rows at every G: the same draws, only the Effector biases held.

**Tests** (`tests/test_rbt124.py`): under S = 0, over 100 chained `mutate_controller` calls the designed body's
Effector biases never change while the same run unset walks them, and every other gene is where the unset run put it;
over 100 chained holistic `mutate` calls, every Effector that survives a step keeps its bias exactly (checked on every
step), and the structure matches the unset run draw for draw; S = weight_sigma is byte-identical to unset.

**What it changes on RBT-113's lines:** nothing retrospectively; it is an operator flag. R8's report shows what it would
have prevented: resting drive in the sample (`sample.txt`) is 96.7% on the designed D line (B: 99.2% over all 120 O1
finals), 16.7% U and 33.3% C, against 21.4% / 12.4% / 17.0% on the holistic D / U / C lines.

---

## 3. `settle_until_rest ε`: a body starts at rest

### 3.1 What is wrong (RBT-121 A3 as corrected, ADVERSARY §4)

`Simulation.settle` steps 1 s with zero command, zeroes the velocities and re-centres the COM on the spawn point. It
never checks that the body has stopped. 14 of 120 holistic bodies then drift more than 0.25 m with their motors off;
a fixed 5 s settle cut that to 5 but **lengthened some drifts**; and motors-off food fell to 0, unexplained.

### 3.2 Decisions

**The flag.** `SimConfig.settle_until_rest = ε` (m/s; 0 = off) and `SimConfig.settle_max` (s, default 10). With ε > 0:
1. the plain settle runs first, **exactly as now** (same steps), while the peak body speed of its last 0.25 s is
   measured (peak body speed: the largest per-step displacement of any body's centre of mass, over the timestep);
2. if that peak is below ε the settle ends there, so **a body already at rest is bit-identical** to the plain settle
   (the Pioneer, on every registered draw, is tested). **This holds for solo seasons only** (S4): the settle runs one
   world, so in a two-robot bout a drifting partner extends the settle for both, the kinetic damping zeroes both, and
   the Pioneer's start pose moves by 2e-10 to 6e-9 (the adversary's `settle_bout.txt`). That is physically nil, but not
   bit-identical, and a chaotic bout need not keep it nil; RBT-118's rematch is a bout;
3. otherwise velocities are zeroed and the settle continues in 0.25 s chunks, each read for its peak speed, until a
   chunk's peak is below ε or the whole settle reaches `settle_max`;
4. then velocities are zeroed and the COM re-centred, as now. The seconds used are kept as `Simulation.settle_seconds`
   (the lever report prints them) and the last chunk's peak as `settle_peak_speed`.

**Kinetic damping, not zeroing at chunk ends: a deviation from the ticket's wording, forced by the evidence.** Inside
the extra chunks the velocities are zeroed **whenever the robot's kinetic energy passes a peak** (the dynamic-relaxation
method), not at every chunk's end. Zeroing at fixed 0.25 s intervals, as first implemented, failed on exactly the
bodies the flag exists for:
- O1/1's D member #30 (a 13.5 kg cylinder on its side with a small ball-jointed limb) rocks with a period of about
  12 s and almost no damping. Restarted from rest every 0.25 s, it gains about 0.01 m/s per chunk, sheds almost nothing,
  never reaches the bottom of its well, and hits the cap still moving (peak 0.027 m/s at 5 s), then drifts 0.38 m in
  the season (the first implementation, measured in-session: 16 zeroings in 16 chunks).
- With kinetic damping it swings once to the bottom of its well, is stopped there, and is at rest at 4.75 s: 0.003 m
  in the season.

**This is also why a fixed 5 s settle lengthened some drifts.** A body in a slow, nearly undamped rocking mode that is
stopped at an arbitrary moment keeps the potential energy of wherever it was in its swing. A 1 s settle catches it
near the start of its first swing; a 5 s settle can catch it near the top. `passive.txt` shows it on the adversary's own
members: O1/1's D members #27, #4 and #30 drift 0.08 / 0.03 / 0.22 m after 1 s and **0.52 / 0.30 / 0.57 m after a fixed
5 s**, on terrain 1131; under `settle_until_rest` they drift 0.005 / 0.005 / 0.003 m.

**ε = 0.01 m/s, `settle_max` = 10 s.** `passive.txt` (the adversary's members, rng 121, all four draws, 480 holistic
member-seasons):

| settle | seasons > 5 cm | > 25 cm | mean settle (s, holistic) | motors-off food |
|---|---|---|---|---|
| plain 1 s (today) | 169 | 55 | 1.0 | 10 |
| fixed 5 s (the adversary's) | 57 | 16 | 5.0 | 1 |
| until rest, ε 0.01, cap 5 s | 50 | 9 | 2.6 | 1 |
| **until rest, ε 0.01, cap 10 s** | **36** | 9 | 3.3 | 3 |
| until rest, ε 0.003, cap 10 s | 36 | 6 | 4.5 | 2 |

- Cap 10 s settles 14 more seasons than cap 5 s, at about 0.7 s more settle per season on average (about 5% of a 15 s
  season's simulation); ε 0.003 buys nothing more on > 5 cm and costs another 1.2 s. The flag takes any ε; 0.01 with a
  10 s cap is the recommendation.
- **Designed bodies: 0 seasons over 5 cm under every settle, and their solo seasons are bit-identical** (they are at
  rest after 1 s, so the flag adds no step).
- **"Motors off" is ctrl 0** (S7), the settle's own condition and RBT-121's convention: a torque motor is slack, a
  position servo holds its joint at the build pose, and a velocity servo brakes. Position servos carry 27% of the
  holistic hinge and slider motors in RBT-113 O1/1's finals, so "off" is "held", not "limp", for those joints.
- **Validation** (S2): a negative ε, or a `settle_max` below `settle_time`, is refused.

### 3.3 What the flag cannot fix: the residual, named

**The closing test bar, "motors-off displacement below 0.05 m for every member", is not met on the full sample: 36
of 480 holistic member-seasons stay above it under the recommended setting** (444 of 480 pass, 93%). The test suite
checks the bar on seven fixture bodies that drift 0.18–0.43 m under the plain settle (all pass); the residual is shown
here rather than hidden. It is of three kinds (`passive.txt`'s per-member rows; diagnosis in-session with the contact
lists):

1. **Bodies jammed into themselves** (9 of the 36: self-penetration > 1 cm after the settle). Two of a body's own
   geoms that the weld/parent filter does not exempt interpenetrate by 1–4 cm; the contact solver pushes them apart
   for ever against the joints, the internal jitter never stops (joint speeds of 1–19 rad/s with every motor off), and
   ground friction turns it into a crawl. In the rng-124 sample, Z1/Z2's D member #35 moves 0.30–0.59 m a season this
   way at any settle length (checked to 15 s). **This is not settle residue but a contact-penetration defect**, the one
   Sims handled by discarding creatures with persistent interpenetration and Krčah by validity-testing before
   simulation (RBT-122 §4.2); it belongs with fix 12 (the penetration trip wire). The lever report now prints it per
   line (`pen>1cm`), and the flag leaves such a body at its cap rather than calling it settled (tested).
2. **Launches on terrain** (5 member-seasons of two bodies, 3 of them not already counted as jammed): Z1/Z2's U member #17 settles, then at t ≈ 7 s is thrown
   6.5 m through the air on terrain 1131 with every motor off (1.37 m after the plain settle, 7.3 m after the
   adversary's 5 s one; 0.00 m on flat ground per ADVERSARY §4); Z1/Z3's founder #11 is carried 0.6–1.7 m on all four
   terrains. That is the contact solver, not the settle: fix 12 again.
3. **Slow near-neutral modes** (the other 24, 0.06–0.40 m, most 0.06–0.12 m): a cylinder or sphere root resting on a
   prop limb that can still roll a little, with accelerations too small to show in a 0.25 s chunk. ε = 0.003 does not
   reduce their count (36 either way).

**Registered side effect (S5, R10).** Once free rotors are gone, a self-jammed body's contact jitter is free
locomotion that the pack does not touch (Z1/Z2's D #35: 0.30–0.59 m a season with every motor off), and the C line
already carries 36 of 120 jammed member-seasons. **Before any rerun registers a locomotion or foraging reading under
the pack, either fix 12 (the penetration trip wire) is in, or the lever report's `pen>1cm` column is printed per line
as a registered side effect beside the reading.**

**A bound on what the residual is worth.** Under the recommended setting, motors-off food over the 480 holistic
member-seasons is 3 items, and all three come from founder #11 of Z1/Z3 (kind 2) moving 1.7 m.

### 3.4 Why motors-off food fell to 0 under a longer settle: a body at rest cannot eat

- **Items are placed at least 0.8 m (`clearance`) from the robot's root after the settle, and eaten within 0.35 m of a
  geom centre.** A still body can therefore reach only the thin annulus where one of its geom centres lies more than
  0.45 m from its root. `levers.static_reach_food` measures that area on each settled pose and turns it into the
  expected items of the first placement: **summed over all 480 holistic member-seasons it is 0.43 items** under the
  plain settle (0.39–0.49 under the others). The typical holistic span is 0.65–0.70 m, so most bodies reach nothing.
- **So every motors-off item is eaten by motion.** All nine of the adversary's motors-off eaters on draw 0 (reproduced
  exactly: `passive.txt`) have a static-reach expectation of 0.000, except one with 0.023. ADVERSARY §4 read five of
  them as "static reach" because their **net** displacement was under 0.25 m; net displacement understates a rocking
  body's excursion (O1/1's D #30 nets 0.22 m but swings 0.93 m out and back in the season).
- **A longer settle removes the motion, so it removes the food**: 10 items under the plain settle, 1 under the fixed
  5 s, 3 under the recommended flag (one body, kind 2). The fall to (nearly) 0 is the expected consequence of bodies
  starting at rest, not a new effect; what remains is bounded by the residual above.

### 3.5 What it changes on the restored RBT-113 sample

`sample.txt`, `settle` variant against `off` (the rng-124 sample, four draws, 120 member-seasons a group):

| holistic | motors-off > 5 cm, off → flag | max motors-off displacement (m) | motors-off food / season | settle used (s, mean) | bodies with a > 1 cm self-penetration |
|---|---|---|---|---|---|
| founders | 39 → 5 | 1.05 → 0.36 | 0.02 → 0.00 | 3.06 | 16 → 15 |
| U | 51 → 3 | 0.39 → 0.19 | 0.02 → 0.01 | 3.92 | 8 → 4 |
| D | 30 → 10 | 0.55 → 0.59 | 0.03 → 0.00 | 3.47 | 7 → 7 |
| C | 40 → 8 | 1.90 → 0.45 | 0.03 → 0.01 | 3.14 | 36 → 36 |

- **Motors-off drift over 5 cm falls from 160 to 26 of 480 member-seasons** (the adversary's sample, `passive.txt`:
  169 → 36). The D line's maximum does not fall: its worst member is the self-jammed Z1/Z2 #35 (§3.3, kind 1).
- **Intact results barely move**: work changes by 0–8% per group, and food by at most one item per 100 seasons except on
  the C line (0.16 → 0.09 a season, 19 → 11 items in 120), whose drifting bodies were partly eating by drift. The
  designed fauna is bit-identical in every row.
- **The C line carries the most self-jammed bodies** (36 of 120 member-seasons): it is the line with no selection, so it
  keeps what the operator builds, and jammed parts are common in what it builds.


---

## 4. The lever report: R8 in one command

`rabbitstew/levers.py` (a sibling of RBT-120's `motors.py`, which covers R8's first lever, Σgear/(4M) and the share
capped). `python -m rabbitstew.levers [--config C] [--draw T:S] [--per-group K] [--workers W] NAME=DIR ...` prints, per
line:

| column | R8 lever | how |
|---|---|---|
| `rest.drive` | resting drive | share of the genome's Effectors with \|tanh(bias)\| > 0.9 (counted as auditor B and RBT-120's `motor_report.py` count it) |
| `w_free` (mean/pooled), `work_free` | ghost share: work on contact-free children | per-actuator work booked by whether the joint's child touches anything at the tick's end (the adversary's `phys_ghost.py` "free") |
| `w_v50`, `v50 pairs` | ghost share: work on children ≥ 50% inside their parent; share of such pairs at the start | 256-point Monte Carlo volume fraction, as `phys_ghost.py` |
| `off disp`, `>5cm`, `off food` | motors-off displacement and food | a second season with every Effector output held at 0 |
| `span` | span | largest horizontal extent after the settle (geom centres + bounding radii) |
| `reach`, `recess` | reachable and recessive node counts | `Genotype.reachable_nodes()` |
| `settle s`, `pen>1cm` | (new) the settle's seconds; bodies jammed into themselves | see §3 |

**The report reads each run's own physics** *(amended per M3)*: the motor budget, the ranges and the settle come
from each line's `config.json` unless `--motor-budget`, `--ball-cone`, `--hinge-range`, `--settle-until-rest` or
`--settle-max` overrides them, and the header prints, per line, the physics actually used. (The first draft replaced the
ranges with the command line's zeros, so a pack run was scored with its ranges off unless every flag was repeated.
Tested: the D fixture under a pack `config.json` reads exactly what the explicit flags read.) `--draw` repeats and the
rows pool every draw (S6). Exploded seasons are counted in their own column and kept out of the work, food and share
means (S8). Two new columns book wheel work (S1): `wheel J`, the work of wheels' spin motors, and `wh.free`, the part
done touching nothing. Per body, `levers.body_levers` returns the same fields, plus
`reach_food` (§3.4).

**One caveat on `w_free`.** It reads 0.83–0.89 for the **designed** body too: the Pioneer's drive wheels chatter on the
floor, touching it at the end of only about 8% of control ticks, so most of their work is booked as "free". `w_free` is
therefore a ghost measure only against the designed body's own value; the absolute `work_free` and its change under
the flags are the cleaner reading.

---

## 5. Coordination with RBT-120 (#409)

RBT-120's motor budget merged into `claude/new-session-4cao7d` (#409, then the adversary's fixes, #410) while this pack
was being built. This branch **merged the base before the PR**; the conflicts were in `world.py`, `simulation.py` and
`cli.py`, all additive, and both sets of changes are kept:

- `world.py`: `WorldConfig` carries `motor_budget`, `ball_cone` and `hinge_range`. The budget scales every driven gear
  (and the damping keyed to it) before the joint is written; the ranges add a `range` to the joint. They touch
  different attributes, so they compose: under both, a ball-jointed limb has a budgeted motor and a cone. The position
  servo's span uses the RBT-124 range, and its force clamp uses RBT-120's `_servo_limit`.
- `SimConfig.to_dict` / `EvolutionConfig.to_dict`: each flag drops its own key when off (`drop_default_flags` for
  RBT-124's, RBT-120's own line for `motor_budget`), so **all four off write the pre-flag `config.json`**.
- `levers.py` reads R8's first lever from RBT-120's `motors.capacity` (Σgear/(4M), and whether the budget scaled the
  body), so the one command prints every R8 lever. RBT-120's `runs/RBT-120/motor_report.py` counts resting drive the
  same way (the genome's Effectors); it stays where the RBT-120 ruling put it.
- Tests: RBT-120's 24 and this pack's pass together; one test asserts that with every RBT-124 flag off the budgeted
  MJCF is RBT-120's, and that the Pioneer's MJCF under the budget (1.77) and both ranges is its MJCF with everything
  off.

---

## 6. Tests and the suite

`tests/test_rbt124.py`, 26 tests (about 25 s):

| flag | test |
|---|---|
| all | off writes the old `config.json` (no RBT-124 key, CLI defaults included); on is written and round-trips; the CLI flags parse under `evolve`, `ecology` and `simulate` |
| all + RBT-120 | every RBT-124 flag off leaves the budgeted MJCF unchanged; the Pioneer's MJCF under budget + ranges equals its plain MJCF |
| 1 | off: every random body's MJCF unchanged and `joint_range` = the genotype's; **the Pioneer's MJCF is byte-identical with both ranges on** (5 controllers, rich and plain) |
| 1 | ranges are written where they should be: every ball joint `(0, cone)`, every unlimited non-wheel hinge ±range, wheels unlimited, limited hinges and sliders untouched |
| 1 | **A's embedded rotor burns ≤ 0.1 of its unfixed work** (S1 with orientation (0, π/2, 0), a 3-child hub, and a hinge rotor) |
| 1 | a wheel (cylinder and sphere on their own axis) is bit-identical under the ranges; the same cylinder hinged across its axis is not a wheel |
| 1 | **an RBT-113 holistic D final's contact-free work on non-wheels falls by ≥ 90%**; its round leaf's airborne spin is booked as wheel work (S1) (fixture from O1/1) |
| 1 | the Pioneer's season on the registered terrain is bit-identical under the ranges |
| 2 | **S = 0: the designed body's Effector biases never change over 100 mutations** while the unset run walks them; every other gene equals the unset run's and differs from the parent |
| 2 | S = 0, holistic `mutate`: over 100 chained mutations every surviving Effector keeps its bias; the structure matches the unset run draw for draw |
| 2 | S = weight_sigma is byte-identical to unset over 50 holistic mutations, and leaves the stream where unset leaves it |
| 2 | resting drive counts |
| 3 | off: the settle is the plain settle (`settle_seconds` = 1.0) |
| 3 | **the designed body's intact results are unchanged**: the Pioneer's season (qpos, work, food) is bit-identical under the flag on each of the four registered draws |
| 3 | the settle is capped and logged |
| 3 | **motors-off displacement < 0.05 m on the registered terrain** for seven RBT-113 bodies that drift 0.18–0.43 m under the plain settle |
| 3 | a self-jammed body runs to the cap and is flagged by the lever report (`self_pen` > 1 cm), not called settled |
| report | `body_levers` on the Pioneer; the `python -m rabbitstew.levers` command prints one row per line |
| M1 | a propeller on a wheel (blade fixed, or on a ball joint), a sphere propeller and a hub of bladed wheels are not wheels, and each falls to ≤ 0.02 (measured 0.006–0.009) of its unfixed work |
| M2 | a round leaf on a ball joint under the cone: one extra DOF (the spin hinge), the same three actuators, the twist motor on an unlimited hinge about x, the steering motors on the coned ball, the part keeps its body and geom, mass unchanged, and it rolls; off, nothing changes |
| M2 | the leaf rule stops a ball wheel carrying a blade: it is coned and falls to ≤ 0.02 of its work |
| M3 | the report scores a run under its `config.json`'s physics and prints it; the D fixture under a pack config reads what the explicit flags read |
| S2 | a cone outside (0, π), a range ≤ 0, a negative ε and `settle_max` < `settle_time` are refused; setting one range flag alone warns |
| S8 | an exploded season is counted and kept out of the work mean |

**Full suite: 560 passed** (`python -m pytest -q`, 6 min 40 s, a clean `.[dev]` venv: Python 3.11.15, x86_64, mujoco 3.14.0, numpy 2.4.6), on this branch after merging integration at 8d5e34a (RBT-120, RBT-125, RBT-126 and their flags included; every strip runs).

---

## 7. What the pack changes on the restored RBT-113 sample

`sample.txt` (rng-124 sample, four draws, 120 member-seasons a group; `pack` = both ranges at π/2, with M1's leaf rule
and M2's ball-mounted wheels, and the settle at ε 0.01, cap 10 s; exploded seasons out of the means). The designed
fauna is **bit-identical under every variant**, in every column, so it is shown once.

| | work (J/season) | work on contact-free children (J) | food / season | motors-off > 5 cm | motors-off food / season | exploded seasons |
|---|---|---|---|---|---|---|
| holistic founders, off → pack | 770 → 511 | 630 → 401 (wheels 95) | 0.03 → 0.03 | 39 → 4 | 0.02 → 0.00 | 0 → 0 |
| holistic U, off → pack | 5,665 → 1,308 | 4,519 → 935 (wheels 735) | **0.98 → 0.22** | 51 → 3 | 0.02 → 0.01 | 0 → 0 |
| **holistic D, off → pack** | **44,716 → 11,729** | **41,729 → 9,667 (wheels 7,333)** | 0.10 → 0.07 | 30 → 11 | 0.03 → 0.00 | 0 → 0 |
| holistic C, off → pack | 6,266 → 349 | 5,800 → 218 (wheels 71) | 0.16 → 0.03 | 40 → 11 | 0.03 → 0.03 | 0 → 4 (one body) |
| designed, any group, any variant | 17–31 k (unchanged) | unchanged (all wheel work) | unchanged | 0 | 0 | unchanged (1, a pre-existing C-line season) |

**R8's other levers do not move under the pack** (they are properties of the genome and the build): Σgear/(4M) is 3.31
on the holistic D line against the Pioneer's 1.76 (RBT-120's budget is the lever for that), resting drive is as in
§2.3, span 0.64–0.70 m, reachable nodes 1.9–2.7 and recessive nodes 1.1–2.4 per body. The share of parent–child pairs
at least half inside their parent at the start is 0.18 on the D line and 0.04–0.11 elsewhere; under the cone the work
those children do falls with everything else (§1.2).

**Reading.** The pack takes away what RBT-121 said was unearned: the D line's free-rotor work on limbs (−94% of its
non-wheel contact-free work) and the drift that fed motors-off food. Under the ruled parity rule (M2) both faunas keep
wheels, and a wheel spinning in the air remains a residual for both (S1: 7.3 kJ a season on the D line under the pack,
where the designed D line's wheels do 27.6 kJ contact-free). The U line keeps its rolling and loses its tumbling
(§1.3). A
holistic-against-designed comparison registered under the pack is a different experiment from RBT-113's, not a
correction of it; the designed side is untouched.

---

## 8. For the design adversary

*The first draft's list follows; the adversary's answers are ruled and applied (Amendments, at the top). For the
re-check, the new points are:*
- *M2's cost, stated plainly: the ruled parity wheel gives back the holistic D line **7.4 kJ a season of airborne wheel
  spin** (S1), so its contact-free work falls 77%, not 94%; the non-wheel part still falls 94%. The designed D line's
  wheels do 27.6 kJ contact-free under the same accounting. Whether that residual is acceptable is the ruling's (it
  was registered as S1), but it is now the largest term the pack leaves.*
- *The ball-wheel mount is built as a 1e-6 kg mount body plus explicit `<exclude>` pairs restoring the parent's weld
  group; `pen>1cm` under the ranges is then 14 / 8 / 7 / 40 member-seasons (founders / U / D / C) against 16 / 8 / 7 / 36
  with the flags off (it rose to 23 / 16 / 23 / 40 when only the parent body was
  excluded, which I caught and fixed before this push).*

Where I expected the argument in the first draft:

1. **The U line loses its gait under the cone** (§1.3). I read that as the rule working: the gait is ball-joint free
   rotation, 29% of it against the ground. The alternative, exempting "ball-joint wheels", is not available in MuJoCo
   (a ball limit binds twist and swing together) and would reopen the rotor: 39% of the U line's work is on round
   ball-jointed parts spinning in the air. Hinge wheels stay free for both faunas. Is that the fairness the programme
   wants, and should a rerun's power model expect U's founders to start slower?
2. **The wheel rule** (`is_wheel`): shape ∈ {cylinder, sphere} and |cos(axis, x)| ≥ 0.999. A near-wheel hinged 3° off
   its axis wobbles and is ranged; one at 2° is free. Is 0.999 the right place, and should a sphere also count when
   hinged off-centre (it does not: its centre is on the child's x axis, so only an x-parallel axis passes through it)?
3. **The cone's value** (π/2, with `hinge_range` matched): `cone.txt` has π/4, 3π/4 and 0.95π on the holistic sample.
4. **Kinetic damping** replaces the ticket's "zero velocities after each chunk" (§3.2), with the failing case measured.
   Is the energy-peak rule safe for multi-robot bouts (it zeroes every robot at the joint energy's peak)? In an arena
   bout both robots settle together, as they already did.
5. **The settle bar is not met on 36 of 480 holistic member-seasons** (§3.3); 9 are self-jammed bodies and 3 more are
   solver launches, both fix 12's; 24 are slow modes of 6–40 cm. I did not add a validity test or a penetration trip wire
   here: that is fix 12, and bundling it would put a body-rejection rule into a flag pack.
6. **One body explodes under the cone** (§1.3), a body already chattering at 171 kJ a season. `solreflimit="0.05 1"`
   removes it on draw 0, at the cost of every limit being softer.
7. **No outward clamp; weld filtering unchanged** (§1.2). The residual ghost work inside parents (`w_v50`) under the cone
   is about 0.9 kJ a season (amended tree) on the D line; R8's report prints it.
8. **`w_free` reads high for the designed body** (§4): the Pioneer's drive wheels chatter. The absolute `work_free` and
   its change are the reliable reading; a sub-step contact test would fix the share but cost a hook in `Simulation.step`.
9. **The settle's seconds are logged** on each `Simulation` (`settle_seconds`) and printed by the lever report, not
   written into `lineage.jsonl` or `history.json`; doing so changes those files' format, which I left for a ruling.

---

## Files

- **`rabbitstew/`**: `world.py` (`ball_cone`, `hinge_range`, `is_wheel`, `joint_range`), `genetics.py`
  (`effector_bias_sigma`), `simulation.py` (`settle_until_rest`, `settle_max`, `settle_seconds`, `actuator_work`, the
  config-key dropping), `evolution.py` and `cli.py` (the keys and the flags), `levers.py` (new).
- **`tests/`**: `test_rbt124.py`; `data/rbt124/` (nine RBT-113 genomes, with a README naming their sources).
- **`runs/RBT-124/`** (every probe reads restored checkpoints and writes nothing into any run):
  - `rotor.py` → `rotor.txt`: A's embedded rotor and the wheel;
  - `sample.py` → `sample.txt` (flags off / ranges / settle / pack, both faunas, four draws) and `cone.txt` (the cone's
    value);
  - `wheels.py` → `wheels.txt`: what the U and D lines' ball-joint work was doing;
  - `passive.py` → `passive.txt`: the adversary's motors-off members under five settles, with static reach and
    self-penetration;
  - `bias_walk_s0.py` → `bias_walk_s0.txt`: auditor B's test 1.
