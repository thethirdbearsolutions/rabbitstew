# RBT-124 design adversary: the physics fairness pack (PR #420 @ 5c959ba)

**Design adversary, 2026-09-27.** This reviews `runs/RBT-124/DESIGN.md` and its code against RBT-121's
`SYNTHESIS.md` R1–R3, R6, R8 and R10, auditor A's `physics/AUDIT.md`, auditor B's `ga/AUDIT.md`, and RBT-120's
motor budget. Every probe is in this directory, and each has its output beside it. The probes run on the PR's tree
(5c959ba) against restored RBT-113 O1 (`scripts/durable.sh restore runs/RBT-113/O1 rbt-113-O1`, 216/216). None of
them writes into any run.

## Verdict: **MERGE AFTER FIXES**

The effector-bias flag and the settle flag are sound, and every flag is byte-identical when off, alone and combined
with RBT-120, RBT-125 and RBT-126. The cone does what R2 asks for, and an honest ball-jointed gait survives it
untouched. Two things block the merge:
- **the wheel exemption**, which is both a laundering route and, in practice, a Pioneer-only rule;
- **the lever report**, which silently reads a pack run with the pack's ranges off.

The U line's food collapse is correct, but it needs a stated ruling, because the pack takes away the holistic
fauna's only wheels while keeping the designed body's.

| # | | item |
|---|---|---|
| M1 | MUST | `is_wheel` must require a **leaf** part: a wheel that carries children is a propeller (§1a) |
| M2 | MUST | **Wheel parity (R6)**: the holistic fauna must be given a reachable wheel, or the asymmetry must be registered and ruled; correct DESIGN §1.2/§1.3's "a holistic body may evolve the same wheel" (§1b) |
| M3 | MUST | `rabbitstew.levers` must take `ball_cone`/`hinge_range`/`settle_until_rest` **from the run's config** unless overridden, and print the physics it actually used (§6) |
| S1 | SHOULD | Register that a bare wheel spinning in the air is still a contact-free rotor (16 kJ a season at full throttle), for both faunas; R8's `w_free` shows it (§1a) |
| S2 | SHOULD | Validate the flags: `0 < ball_cone < π`, `hinge_range > 0`, `settle_max ≥ settle_time`; warn when only one of cone/range is set (§5) |
| S3 | SHOULD | Fix the stale help and docstrings: "velocities zeroed between them" describes the rejected implementation, not kinetic damping (§3) |
| S4 | SHOULD | Scope the "bit-identical" claim to solo seasons: in a two-robot bout the designed body's start moves by ≤ 6e-9 (§3) |
| S5 | SHOULD | Before any rerun registers a *locomotion* reading under the pack, schedule fix 12 (penetration trip wire), or print `pen>1cm` per line as a registered side effect (R10) (§3) |
| S6 | SHOULD | `levers` should take several draws (`--draw` repeated) and pool them, as the design's own sample does (§6) |
| S7 | SHOULD | State that "motors off" (ctrl 0) holds position servos at the build pose and brakes velocity servos, as the settle does (§6) |
| S8 | SHOULD | `levers.line_summary`: keep exploded seasons out of the work means (one exploded season adds 25 MJ to a line's mean, §2b) |

---

## 1. Is each flag fair (R6)? The wheel rule

### 1a. A "wheel" launders a free rotor (`launder.py` → `launder.txt`, `launder_leaf.txt`)

`is_wheel` looks only at the part itself: a round shape, hinged about its own x axis. **It does not look at what
the part carries.** Everything fixed or jointed to a wheel turns with it. Each body below is driven at full throttle
(bias 3), on RBT-113's generation sim (terrain 1131, start 2131), with ranges at π/2:

| body | wheels by the rule | work off (J) | work on (J) | on/off | contact-free work on (J) |
|---|---|---|---|---|---|
| wheel (rotor.py's reference) | 1 | 16,026 | 16,026 | 1.000 | 16,026 (w_free 1.00) |
| **prop-fixed**: wheel carrying a FIXED 1.2 m blade | 1 | 16,020 | **16,020** | **1.000** | 16,020 |
| **prop-ball**: blade on an undriven ball joint | 1 | 12,774 | **14,526** | 1.137 | 14,526 |
| **sphere-prop**: sphere on an x hinge carrying a blade | 1 | 16,027 | **16,027** | 1.000 | 16,027 |
| **hub12-wheels**: S1's hub with 12 wheels, 3 carrying blades | 12 | 130,010 | **130,010** | **1.000** | 117,494 |
| hub12-ball: S1 embedded k=12 on ball joints (rotor.py) | 0 | 549,268 | 3,007 | 0.005 | 2,508 |
| Pioneer (rng 0) | 4 | 27,662 | 27,662 | 1.000 | 6,832 |

- The cone stops S1's hub on ball joints (0.005). **The same hub on "wheels" keeps all 130 kJ**, and a propeller
  blade on a wheel is untouched. A's test passes only because A's rotor sits on ball joints.
- **Fix (M1): a wheel must also be a leaf.** With that one condition (`launder_leaf.txt`, patched in-process):
  - every propeller falls to 0.006–0.008 of its unfixed work;
  - the Pioneer is bit-identical, because its wheels are leaves.
  - Implementation: `joint_range` needs the phenotype's parent set, or `is_wheel(part, has_children)`.
- **What no geometric rule can close (S1).** A bare wheel spinning in the air is itself a contact-free rotor. The
  design's reference "wheel" row has `w_free` 1.00 (16 kJ a season), and in `launder_leaf.txt` the hub's nine
  bladeless leaf wheels still burn 94.5 kJ contact-free. The flag is symmetric for both faunas here: the Pioneer's
  wheels could do the same if lifted. The design calls the wheel "not a rotor", but for work accounting it is one.
  Register it, and let R8's `w_free` watch it.

### 1b. The rule is reachable in name only for the holistic fauna (`reach_wheel.py` → `reach_wheel.txt`)

DESIGN §1.2 says "a holistic body may evolve the same wheel under the same rule". Measured on the 480 holistic and 480
designed bodies of RBT-113 O1 (founders plus every U/D/C final, seeds 1–3):

| | bodies | hinges | unlimited | **wheels by the rule** | bodies with a wheel |
|---|---|---|---|---|---|
| holistic (all groups) | 480 | 201 | 36 | **0** | **0** |
| designed (all groups) | 480 | 1,920 | 1,920 | **1,920** | 480 |

- **The genetic route is a lottery with no gradient.** A founding axis is uniform on the sphere, so
  P(|a_x| ≥ 0.999) = **0.001** per founding unlimited hinge (20% of hinges are unlimited). One axis mutation (a +
  N(0, 0.5)³, renormalised) lands in the 2.6° cap with probability 0.001 from anywhere, and 0.005 from 5° off.
  - A near-wheel 3° off is ranged, with no partial credit.
  - A wheel keeps its status through an axis mutation with probability **0.005**, so a found wheel is lost at its
    next axis mutation (`axis_rate` 0.15 per connection).
  - The designed body's morphology does not mutate, so its wheels are permanent.
- **Loosening the tolerance does not help.** Across the 480 holistic bodies there are only 22 unlimited hinges on
  round parts, and 1 of them lies within 30° of x. The holistic encoding mounts round parts on **ball joints**: 469
  round parts, 371 of them leaves. Those are the "ball-mounted wheels" of `wheels.txt`, and they carry the U line's
  gait.
- **Net effect.** The pack removes the holistic fauna's only wheels, the ball-mounted ones, and keeps the designed
  body's hinge wheels behind a rule the holistic fauna meets in 0 of 480 bodies. Under R6, a comparison registered
  under the pack is not at stated parity until this is either fixed or stated. **M2: pick one, before any
  registration uses the pack:**
  1. **Give the holistic fauna the same wheel it already builds** (recommended): under the flag, a round **leaf**
     part on a **ball** joint keeps the cone on the joint and gains free spin about its own x axis, as a hinge on a
     cone-bounded mount. That is the ball joint's twist DOF re-expressed as an unlimited child hinge, i.e. a steerable
     wheel. It is byte-identical when off, and the leaf rule stops it carrying a rotor. The U line's
     "ball, round, touching" work (21% of its season, `wheels.txt`) would survive, and its "ball, round, free" work
     is exactly S1's airborne-wheel residual. This changes DOFs and actuators under the flag, so it needs its own
     tests.
  2. **Register the asymmetry** as a stated operator/body difference (R6), with a ruling. The U line's food collapse
     (0.98 → 0.07) is then partly a fairness effect of the rule, not only "the cone doing its job".
- The alignment threshold itself (0.999 vs 0.99) is immaterial beside this. Keep 0.999 (the Pioneer is exact), and
  pair it with a leaf rule.

## 2. Does the cone remove the loophole without breaking honest locomotion?

### 2a. A planted honest walker (`walker.py` → `walker.txt`)

A box torso has four box legs on driven ball joints, run by a scripted trot. Only the joint limit changes.

- **Servo gait (honest).** Each leg tracks a stride target within ±0.6 rad under a PD law; the largest joint angle
  reached is 1.13–1.27 rad. **Under π/2 and 3π/4 the season is bit-identical to off** on flat ground and on terrain
  1131: the limit never binds. Travel is 0.92–1.39 m (flat) and 0.90–1.57 m (terrain) a season. Under π/4 the limit
  binds (max 0.86–0.98 rad), and the walker still travels 1.3–2.3 m.
- **Open-loop gait, for contrast.** A sinusoidal torque at the gear the rule gives (4 × the torso's mass) **whirls
  the legs round**, reaching the maximum angle π at every amplitude tried (0.25–1). That is the loophole itself. The
  cone cuts it to 0.4–0.6 m of travel at π/2. It is also chaotic: a one-ulp change in the phase's summation order
  moves its off travel from 3.36 to 2.31 m, and repeated runs are bit-identical.
- **Reading:** π/2 leaves an honest stride (up to about 1.3 rad) untouched, and π/4 would bind it. π/2 is justified
  both by this and by `cone.txt`'s flat region (π/4–3π/4). A founding holistic body's Effectors are tanh units at
  its gear, closer to the open-loop case than to a servo. So **a rerun's founders start slower**, as DESIGN §8.1
  says, and the registration's power model should expect that.

### 2b. The explosion (`explode.py` → `explode.txt`)

All 480 holistic bodies of RBT-113 O1 (founders and every U/D/C final, seeds 1–3), on all four registered draws,
with the ranges off and at π/2, for 1,920 seasons each way:

| ranges | exploded seasons |
|---|---|
| off | 4 / 1,920 |
| π/2 | 6 / 1,920 |

- **The only body the cone tips over is the designer's O1/2 C #00**, on 3 of its 4 draws. It was already burning
  154–174 kJ a season with its flags off.
- The cone also **stops** one explosion: O1/1 founder #17 on draw 1131 goes from 20.9 MJ (exploded) to 153 J.
- **Not a new failure mode at this n.** Softening `solreflimit` for every limit to save one body is not warranted,
  and I agree with not adopting it.
- One side effect: an exploded season's `work` reads 2–755 MJ, and it enters the lever report's line means
  (`cone.txt`'s C line: 25 MJ). **S8: exclude exploded seasons from the work means** in `levers.line_summary`, or
  report them apart, as the explosion guard does for fitness.

## 3. Settle until rest

- **Soundness of kinetic damping.** It is the standard dynamic-relaxation rule, applied only after the plain settle
  and only while the last chunk's peak is ≥ ε. Off, the code path is the old loop, so no committed result changes.
  On, a body at rest after 1 s takes no extra step, so solo it is bit-identical: confirmed for the Pioneer
  (`settle_bout.txt`, solo row) and by the designer's four-draw test.
  - KE is translational (body COMs) only. A part spinning in place is invisible to the rest test, but ctrl is 0
    during the settle and velocities are zeroed at its end, so nothing is lost.
- **S4: multi-robot bouts** (`settle_bout.py` → `settle_bout.txt`).
  - The settle runs one world, so a drifting partner extends the settle for both robots (2.25–8 s), and the kinetic
    damping zeroes both.
  - The Pioneer's start pose then moves by 2e-10 to 6e-9 (joint coordinates and root orientation). That is physically
    nil, but it is **not bit-identical**, and in a chaotic season it need not stay nil.
  - DESIGN §3.2 and §8.4 should say that the "designed body bit-identical" claim is solo only. RBT-118's rematch is a
    bout.
- **S3: stale wording.** The CLI help for `--settle-until-rest` and the `SimConfig.settle_until_rest` comment still
  say "in 0.25 s chunks (velocities zeroed between them)". That is the rejected implementation.
- **The unmet bar is honestly reported.** DESIGN §3.3 states 36 of 480 above 5 cm and names the three kinds, and
  the test checks only fixture bodies. This review accepts the report as stated; not re-run in full.
- **Self-jammed bodies (fix 12).** Discarding them at birth is a body-rejection rule, so it is out of scope for a
  flag pack, and the designer was right to leave it out.
  - But a jammed body's contact jitter is **free locomotion** (Z1/Z2 D #35 moves 0.30–0.59 m a season with every
    motor off), and the pack does not touch it. Once free rotors are gone, jitter-crawl is the next exploit a U line
    can select.
  - The C line already carries 36/120 jammed member-seasons.
  - **S5:** schedule fix 12 before a rerun registers a locomotion or foraging reading under the pack, or make
    `pen>1cm` per line a registered side effect under R10.

## 4. `--effector-bias-sigma`

**Sound.**
- It is one `rng.normal` draw in either branch (`normal(0, σ)` is `σ·z` on the same variate), so the stream is
  unchanged at any S. The designer's tests show S = weight_sigma byte-identical to unset over 50 holistic mutations.
- The `global_bias_sigma` branch comes first, but it cannot shadow an Effector: `Genotype.validate` allows only
  Neurons in the global brain.
- Every mutation path reaches `mutate_weights` with the config: `mutate`, `mutate_brain`, `mutate_controller` and
  the plain weight path, in both `evolution.py` and `ecology.py`. **Both faunas are bound.**
- Founding biases (`random_units`, `_random_unit` N(0, 0.5), and `fixed.randomize_weights`) are births, not the
  walk, as stated.
- Unset drops the key, and 0 is kept and written.

## 5. Byte-identity when off, and the strips combined (`combo.py`; `combo_*.json`)

Run in three trees: integration `e7606db`, the PR `5c959ba`, and a **trial merge of the PR + #414 (RBT-125 @
b6a47cd) + #419 (RBT-126 @ f03d830)**.

- **Merge.** Conflicts arise only with #414 (`simulation.py`: two new methods side by side, and `evolution.py`'s
  import line), and both are additive. `SimConfig.to_dict` auto-merges into
  `strip_default_perception(drop_default_flags(asdict))` with RBT-120's line between, so all three strips run.
  #419 merges clean.
- **Default `config.json`** (a bare `evolve`, and RBT-113's foraging command line) is **identical in all three
  trees**, both bare and with every flag the tree knows passed explicitly at its off value.
- **RBT-113's goldens** (`test_rbt113.py`'s A and B runs: config, lineage, history, state) match the recorded
  digests in all three trees, with every flag passed explicitly off (RBT-120/124 in the PR; RBT-120/124/125 in the
  trial).
- **The Pioneer's MJCF** is identical, rich and plain, under `ball_cone` + `hinge_range` π/2 + `motor_budget` 1.77.
- **Every flag on at once** (cone, range, settle 0.01, budget 1.77, effector S = 0, smell contrast 2.5, eat
  root/surface, clear geoms): `to_dict`/`from_dict` round-trips, and a Pioneer season runs.
- **Full suite, clean `.[dev]` venv (Python 3.11.15, mujoco 3.14.0, numpy 2.4.6, no scipy):**
  - PR `5c959ba`: **450 passed** (5 min 51 s);
  - trial merge (PR + #414 + #419, conflicts resolved as above): **540 passed** (6 min 37 s).
- **S2.** No flag is validated. `--ball-cone -1` writes `range="0 -1"`, and `--ball-cone 4` (> π) is no limit at
  all. `settle_max` below `settle_time` is silently raised to it. A cone set without a hinge range (or the reverse)
  leaves half the rotor open; the design says a registration "should set them together". Refuse or warn.

## 6. The lever report (R8)

**What it computes is what R8 asks for**, per line:
- Σgear/(4M) and the share capped, via RBT-120's `motors.capacity`;
- resting drive, counted over the genome's Effectors as B and RBT-120 count it;
- the contact-free and ≥ 50%-inside work shares, as `phys_ghost.py` books them;
- motors-off displacement and food;
- span;
- reachable and recessive nodes;
- plus the settle seconds and `pen>1cm`.

The designer's own caveat on `w_free` for the designed body (its wheels chatter) is right; read the absolute
`work_free`.

**M3: it reads a pack run under the wrong physics** (`levers_config.py` → `levers_config.txt`).
- `main()` replaces `ball_cone`/`hinge_range` with the command line's defaults (0), so a run registered under the
  pack is scored with its ranges **off** unless every flag is repeated by hand. On the RBT-113 D fixture under a
  pack `config.json`:
  - no flags: **32,273 J**, `w_free` 0.99;
  - flags repeated: 183 J, `w_free` 0.79.
- `settle_until_rest` is taken from the config when the flag is absent, so the two physics flags and the settle
  behave differently.
- The header prints the command-line values (`ball_cone 0 … settle_until_rest 0`), not the physics used; in case
  (a) the settle ran at 5.00 s under a header saying 0.
- **Fix:** default each flag to `None` and fall back to the config; print `sc`'s values.

S6: one invocation scores one draw. R8's levers are season quantities (work shares, motors-off displacement), and
the design's sample pools four draws, so let `--draw` repeat and pool.

S7: "motors off" is `effector_output = 0`, i.e. ctrl 0. For the holistic fauna's position servos, which carry 27% of
the hinge and slider motors in RBT-113 O1/1's holistic finals, that holds the build pose rather than going slack; velocity servos
brake. That is the settle's own condition and RBT-121's convention, so it is consistent. Say so in the docstring.

## Files

| probe | output | question |
|---|---|---|
| `launder.py` (`--leaf`) | `launder.txt`, `launder_leaf.txt` | §1a: laundering through a wheel; the leaf fix |
| `reach_wheel.py` | `reach_wheel.txt` | §1b: can a holistic body meet `is_wheel`? |
| `walker.py` | `walker.txt` | §2a: an honest ball-jointed gait under the cone |
| `explode.py` | `explode.txt` | §2b: explosions under the cone, 480 bodies × 4 draws |
| `settle_bout.py` | `settle_bout.txt` | §3: the settle in a two-robot world |
| `combo.py` | `combo_base.json`, `combo_pr.json`, `combo_trial.json` | §5: byte-identity and the strips combined |
| `levers_config.py` | `levers_config.txt` | §6: which physics the lever report reads |

`launder.py` imports `runs/RBT-124/rotor.py`, and every probe imports the PR's `rabbitstew`, so run them on the PR's
tree (5c959ba) or after it merges.
