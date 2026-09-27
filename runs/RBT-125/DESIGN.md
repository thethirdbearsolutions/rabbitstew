# RBT-125: the perception pack

*This is the smell contrast channel, the eating rules and the world gate: RBT-121 fix-list items 5 and 7 (R4).
Epic RBT-123.*

- **Code:** `rabbitstew/simulation.py` (`FoodConfig`, `Simulation._food_contrast`, `_log_smell`, `_eating_geoms`,
  `_surface_distance` and `_clearance_points`), with the CLI flags in `rabbitstew/cli.py`.
- **Tests:** `tests/test_rbt125.py`.
- **The world gate:** `runs/RBT-125/gate/`. It is registered before its data (`REGISTRATION.md`), and its readout
  follows in a second PR.

**Every flag is off by default, and byte-identical when off:**
- RBT-113's golden `evolve` digests pass with each flag passed explicitly at its off value;
- a config at the defaults writes the config.json it wrote before the fields existed (`strip_default_perception`,
  as RBT-104, RBT-112, RBT-113 and RBT-120 did for theirs);
- a Pioneer bout is bitwise the same.

## 1. The smell contrast channel

**Definition.** With `food.smell_contrast = G > 0`, every `food` sensor of robot r reads

    c_nose = tanh( G · (x_nose − b_r) ),     x_nose = ln S(nose) = ln Σ_items exp(−d / decay)   (floored at ln 1e-12)
    b_r    ← b_r + (1 − e^(−Δt/τ)) · ( mean over r's own food noses of x − b_r )

- **The baseline.** b_r starts at that mean on r's first reading. It is advanced once per control tick, *before* the
  noses are read against it, with τ = `food.smell_tau` = 2 s.
- It restarts with every `Simulation`, which means every season.
- This is RBT-121 audit C's `probe_gprop.py` sensor, with running-baseline centring. The one change is the exact
  EMA factor 1 − e^(−Δt/τ) in place of Δt/τ. The difference is 0.5% at the simulator's Δt of 0.02 s.
- With G = 0, the reading is the legacy squashed intensity, and the baseline is never touched.
- The `smell` mode (sum, mean or log) plays no part under the contrast.
  - Sum and mean differ by a constant (ln n) in ln S, and the baseline cancels it.
  - Log mode's `log1p(S)/log1p(n)` is not a log of S, and is not used.
  - The PW layout's `smell = log` therefore matters only at G = 0.
  - `decay` still sets the length scale.
- The decoy (RBT-97's `RotatedSmell`) has to rotate `_log_smell` as well as `_intensity`. The gate's wrapper does
  this, and asserts it (§3).

### Why a running baseline, and not root-centring

**Root-centring is refused.** It reads each nose against ln S at the root, so:
- a root nose reads 0 for ever;
- a body whose only nose is on its root is blind;
- the temporal route (a lone nose read through a `differentiate` unit) and the absolute level both vanish.

It turns "perception" into "bilateral spatial contrast only" (RBT-121 adversary §6b). On the Pioneer it also
zeroes the chassis nose. That makes RBT-116's G8(b) throttle plant identically silent, a control that cannot fail
(RBT-116 design adversary §2.3).

**The running baseline keeps every nose informative.**
- Every nose reads its own ln S against the body's recent mean, so spatial contrast, temporal contrast and root
  noses all survive.
- In the kinematic model, which has no root or lone nose, the two centrings score alike (`probe_gprop.txt`). The
  choice therefore rests on the parity argument, as the audit says, not on that probe.

### Why a single contrast channel, and no level channel beside it

The ticket asks us to consider a level channel. **We considered it and deferred it:** it is not refused, and it
is not in this PR.

1. **A level channel needs a new sensor source** (for example `food_level`) in the genotype vocabulary.
   - Adding a source changes what the mutation operators draw, so it is not byte-identical for evolution unless it
     is behind its own vocabulary flag.
   - It also changes the Pioneer's mounted sensor set, which is a new parity question in its own right.
   - The contrast channel changes only what an existing `food` sensor reads. Every committed body, and the routed
     compass installed by the gate, reads it with no rewiring.
2. **What a level channel would add is small.** The absolute level is used by area-restricted search on level
   ("I am in a rich place, so turn more").
   - The contrast keeps the version of it that runs on change ("it is getting richer", with G·τ·d ln S/dt).
   - It drops only "rich, and not changing". Neither the gate nor R4 needs that.
3. **The sweep can add it as a measured axis.** If the world sweep (RBT-129) finds the loss of level matters, then
   `food_level` as a separate, vocabulary-flagged source is the fix, measured on its own.

### Registered G

**G = 2.5 is registered, and tested at G ∈ {2.5, 10}** (R4).
- 2.5 is the kinematic candidate. In PW, every one-σ nose step pays about +0.17 to +0.19 items, and so does +25%
  speed (`probe_gprop.txt`).
- At G = 10, per-nose contrasts saturate: median |c| is about 0.6 and p90 about 0.94 on real bodies (adversary §6b).
  The first weak nose pays more, and the later steps pay less (+0.08).
- **G = 10 also gates steering on approach speed** (the gate adversary's `probe_motion.txt`).
  - The three noses share one baseline, so moving along the gradient puts every nose on the flank of the tanh.
  - L − R is then multiplied by about sech²(G·c).
  - At G = 10, 0.25 m/s and 45° toward the food, L − R is 7% of its static value. At G = 2.5 and 0.5 m/s it is
    30%.
  - So at G = 10 a body steers least when it is approaching food fastest.
- The world gate decides on real bodies (§3). G = 10 is the registered fallback, with its saturation stated.
- τ = 2 s is the audit's value. It is a registered constant, not tuned.

### Parity: what each nose reads, on each body (RBT-116 design adversary M5)

**The Pioneer geometry** used below, measured in the simulator:
- the chassis (root, part 0) nose is at the body centre;
- the two drive-wheel noses are at (+0.10, ±0.19) m, so they are 0.39 m apart and 0.10 m ahead of the chassis.

**Notation:**
- **∇** is the gradient of ln S. Its magnitude is at most 1/decay: 0.67 m⁻¹ in PW, and 1 m⁻¹ in U and HP.
- **v** is the body's speed, **θ** the angle between its velocity and ∇, and **δx** a nose's offset from the
  noses' mean position.

| body, nose | legacy (G = 0) | **contrast, running baseline (this PR)** | root-centred (refused) |
|---|---|---|---|
| **Pioneer, chassis (root) nose** | the level S/(1+S) | the fore–aft contrast against the wheels' mean, plus the common temporal term | **0, always** |
| **Pioneer, left and right wheel noses** | two levels; L − R has a median of about 0.03 | G·(x − b) each: L − R ≈ 2·tanh(G·Δx/2), with Δx = ∇·(0.39 m lateral) ≤ 0.26 in PW. At G = 2.5, \|L − R\| ≤ 0.63; at G = 10, ≤ 1.72 (saturating). The common temporal term cancels in L − R only to first order: moving along ∇ scales L − R by about sech²(G·c) (see "Registered G") | each wheel against the chassis |
| **a lone nose** (one food sensor), anywhere | the level; the temporal gradient needs a `differentiate` unit | **the temporal gradient, free:** tanh(G·(x − EMA(x))) → tanh(G·τ·v·\|∇\|·cos θ) at steady speed. It is 0 at rest in a static field, and approaching one item head-on it is tanh(G·τ·v/decay) | the lever contrast (nose − root); **0 if the lone nose is on the root** |
| **two noses, symmetric in a symmetric field** | equal levels | **exactly 0 at rest, from the first reading.** Moving, the two read the same common temporal term, so L − R = 0 | each against the root |
| **n noses in general** | n levels | each: G·(spatial offset δx·∇ + the common temporal lag), squashed | each against the root |

**The parity consequence, stated as registered (M5).**
- The running baseline **turns every lone nose into a temporal-gradient detector**, with no `differentiate` unit
  needed.
  - This favours one-nosed bodies. A single-nose body is necessarily holistic, because the foraging Pioneer always carries three. 39% of holistic
    bodies carry any food nose (RBT-116 design, PR L301).
  - It also gives the Pioneer's chassis nose a temporal signal it did not have (a new one-step route for G7:
    chassis nose → throttle).
- Root-centring would have had the opposite bias: anti-holistic, and fatal to the chassis nose.
- **Any comparison between bodies run on this channel must report STEERS and the steps by nose count and nose
  placement.** The gate's §B hosts are all three-nosed Pioneers.

### Tests (`tests/test_rbt125.py`)

- **Off:**
  - `test_off_is_byte_identical_to_the_pre_pack_code`: the RBT-113 golden digests, with every flag given
    explicitly at off;
  - `test_off_reading_is_the_legacy_squashed_intensity`: S/(1+S), written out independently;
  - the Pioneer bout is bitwise the same;
  - config keys are absent when off, and round-trip when on.
- **A lone nose moving up a gradient reads > 0** (`test_a_lone_nose_reads_the_temporal_gradient`).
  - Moving away, it reads < 0. At rest, it decays to 0.
  - At steady speed, it equals tanh(G·v·τ/decay) to 2% (`test_the_lone_nose_signal_is_g_times_tau_times_the_log_slope`).
- **Two symmetric noses in a symmetric field read exactly 0** at rest, from the first reading. Moving, they read
  equal values (`test_two_symmetric_noses_in_a_symmetric_field_read_zero`).
- **The spatial contrast is** 2·tanh(G·Δx/2) (`test_two_noses_read_the_spatial_contrast_with_gain_g`).
- **A root nose is not zeroed.**
- The Pioneer's three noses: the left–right order follows the food.
- The smell mode is ignored under the contrast.
- The baseline restarts with each simulation.

## 2. The eating rules

**The flags:**

| flag | values | effect |
|---|---|---|
| `food.eat_from` | `any` (legacy) | every geom eats |
| | `root` | only Part 0 eats |
| | `sensor` | only Parts that carry a `food` Sensor eat |
| `food.eat_rule` | `centre` (legacy) | an item within `eat_radius` in xy of an eating geom's centre |
| | `surface` | an item within `eat_radius` in 3-D of the geom's *surface*, with the item lying at z = 0. The distance is exact for box, sphere and cylinder, and is 0 inside |
| `food.clear_from` | `root` (legacy) | food is placed at least `clearance` from each robot's root body |
| | `geoms` | at least `clearance` from every geom centre, both at placement and at every regrowth |

**Not covered by `clear_from`:** `clear_spawn_layout`, the persistent arenas' spawn redraw, still measures from the
spawn point, because no body exists yet when it runs. With `geoms`, the first tick can therefore still find an item
under a limb in a carried-over arena. That is a small, stated gap.

### "Root" on a holistic body

**Definition: the root is Part 0.** It is the first Part synthesis creates, the root Node's first instance
(`Phenotype.root`), and the MuJoCo body that carries the free joint (`RobotIndex.root_body`).
- **Why not the heaviest Part?**
  - It is not stable under mutation: a dims change could move the mouth from one limb to another.
  - It is not what the controller, the direction probes or the clearance rule call the root.
- **Pinned by tests:**
  - `test_the_pioneers_root_is_its_chassis`: the Pioneer's Part 0 is node `CHASSIS`, a box with no parent, and the
    free-joint body;
  - on six random holistic genotypes, Part 0 is `g.root`'s first instance.
- Every root has the same volume, set by `root_size` (0.3 m): the Pioneer's chassis is 0.42 × 0.35 × 0.19 m, which
  is 0.3³. What differs between bodies is how much of the eating footprint lies *outside* the root.
  - On the Pioneer, the rest of the footprint is two wheels and two casters close to the chassis.
  - On a holistic body, it can be most of the body.
  - §C measures the income lost to root eating, per fauna, at generation 0 (RBT-116 design adversary SHOULD 6).

**`sensor` on the Pioneer** eats from the chassis and the two drive wheels, not the casters (tested). A body with no
food sensor eats nothing (tested).

### What each rule does to the blind tumbler (RBT-121 adversary §7)

The tumbler is one full-throttle hinge with no sensor. It nets about +0.7 a season at any arm length from 0.45 m to
6.46 m, because it is a blind, spinning, tumbling body with 5–10 m of path.

| rule | expected effect on the tumbler | does it stop coverage? |
|---|---|---|
| `root` | The arm no longer eats, so a long arm's sweep is gone. The tumbling cube still covers its own path, and eats what that path crosses | **No.** It removes span and thrash-sweep, not the tumbling |
| `sensor` | The noseless rod eats nothing. **But one unused food nose on its root restores its root-eating income**, so the rule taxes noselessness, not coverage. §C measures this directly | **No** |
| `surface` | The reach is measured from the surface, so a long arm eats along its whole length. **This can raise a long sweeper's income.** Airborne parts no longer eat | **No.** It is a physical-honesty rule; it is not comparable across the flag for any body, the Pioneer included |
| `clear_from = geoms` | It removes the static-reach free lunch: motors-off food from items placed within a far limb's reach, about 0.1 a season | **No.** It fixes a placement leak |

**So the rules stop span and thrash-sweep from standing in for steering (C4, A5). They do not stop a tumbler's
coverage income. That is the work price (C3) and the layout (PW) at work (SYNTHESIS M4).**

The gate's §C (as amended) measures:
- every rule on the tumbler in the committed world;
- in PW: `any`, `root`, `sensor` (with and without an unused root nose) and `surface`. `clear_from = geoms` on the
  tumbler is run in the committed world only.
- For founders: every rule in the committed world, and `root`, `sensor`, `surface` and `clear_from = geoms` in
  PW-G2.5.

### Tests

- The Pioneer's root is the chassis, and a holistic body's root is Part 0 of its root Node.
- `sensor` means the chassis plus the drive wheels.
- A noseless body eats nothing under `sensor`.
- An item reachable only by a caster is eaten only under `any`.
- `surface` eats under a long rod's end, where `centre` does not, and does not eat from the air, where `centre`
  does.
- The surface distance equals the analytic nearest-point distance, and no sampled point of the solid is closer
  (box, sphere and cylinder, under a rotated pose).
- `clear_from = geoms` keeps every new item at least `clearance` from every geom.
- Bad values are refused.

## 3. The world gate on real bodies (registered: `runs/RBT-125/gate/REGISTRATION.md`)

- **§A, the gate.** RBT-106's prize harness (RBT-103's `routed_populations.py`, unchanged) runs on RBT-90 part 2's
  ten populations.
  - The installed compass is at **a = 6** (w = 3), with 64 paired seeds.
  - The world is **PW** (2 × 0.4 m patches, radius 4, own-spot regrowth at 60 s, log, decay 1.5) at G = 2.5 and 10,
    with the legacy G = 0 as the control.
  - **PASS** needs both the prize's t(9) lower bound > 0 **and** (motif − decoy)'s lower bound > 0.
  - The committed HP and U layouts are run at each G as well.
  - Before anything is read, two harness checks must reproduce committed rows to the digit, or the script stops:
    RBT-103's seed-801 row in its own world, and RBT-106's HP-801 row through `--config-from` with the decoy.
  - PASS reads all ten populations; a missing one counts as 0. PASS is a claim about the world. A claim that the
    channel pays also needs (PW-G − PW-G0), paired by population, to have a lower bound > 0 (amendment 1).
- **The decoy patch.** RBT-97's `RotatedSmell` rotates the layout only inside `_intensity`, so under G > 0 it would
  smell the true food and return the intact income: a decoy that cannot fail. `prize_gate.py` adds the same rotation
  to `_log_smell`, and asserts before running that the decoy changes the reading.
- **§B.** A nose step (a first weak nose, and one-σ steps at a = 2 and a = 6) against a +25% speed step taken at the
  same base w.
  - The speed step is joint damping ÷ 1.25, with the realised speed measured and the step rescaled to +25% realised.
  - It runs on 15 of RBT-113's O1 designed U finals, over 128 seeds, in PW at G ∈ {2.5, 10, 0}, after §A and §C.
  - It is descriptive: the expected reading is TIED, UNRESOLVED.
- **§C, the R6 side effects:**
  - founder income and solvency, per fauna, under every flag;
  - the income ÷ living-cost regime of the committed corpus's living (RBT-90 seed 801 at season 600);
  - the tumbler under every eating rule;
  - the channel's saturation on the real bodies (median and p90 of |c|);
  - births and depth are out of scope, because the seasons are solo.

## 4. What this PR does not do

- It does not register any evolution run on the channel. That belongs to the sweep (RBT-129) and RBT-116, which
  take G and the eating rule from the gate's verdict.
- It does not add the level channel (§1). It does not add `eat_max_speed` or `max_extent` (audit A5's third flag).
  Both are listed for the fairness-set follow-up if the sweep needs them.
- It does not change any committed result: every flag is off by default.
