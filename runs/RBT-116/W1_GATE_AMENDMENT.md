# RBT-116: a proposed pre-data amendment to W1's reachability screen (§1.1)

*2026-09-28, the RBT-132 implementer. **Ruled ADOPT-WITH** (the coordinator on #484, comment 5875124551, after check
#485) and **implemented as RBT-116 Amendment 4** (PREREGISTRATION.md): the rule is "≥ 1 of 16 registered screen hosts",
with `ate_by_host` at W1. The text below is the proposal as checked; where it differs (N = 16 registered hosts), the
amendment governs.*

**Nothing changes on this branch and nothing is emitted.**
- `steer.py`, `tests/test_rbt116_steer.py` and `power.py` are untouched, and W1 stays byte-identical until a ruling.
- No RBT-116 output exists: no arm, gate cell, draw screen or battery of W1 has run (PREREGISTRATION.md, top note).
- The evidence is a fixture experiment only: `gate_diag.py`, Part 2, merged with #478. It used fixture draws and
  committed RBT-19 bodies, not W1's pool, W1's hosts or any arm.

## The registered rule, and why W1 is exposed

**§1.1, as registered:** "A draw is **admissible** if at least half of those hosts [the positive controls of G8(a)
and G8(c)] eat ≥ 1 item on it. … If fewer than 36 draws are admissible, the pool is extended by 32 more draws, once. If
that still fails, the world point fails its gate."

**W1 is PW's layout at 15 s** (§4.1: 12 items in 2 patches of radius 0.4 within 4 m, random terrain). That is the
layout where the rule failed at RBT-129's calibration:
- c0-p030-PW-G admitted 5 of 96 draws, while 0 of 96 draws had no eater;
- RBT-132's adopted rule (c) was ruled on #478 (comment 5874231890).

**In W1's own block** (RBT-116 §4.1, τ 1 s, random terrain), with RBT-19 controls on fixture draws (`gate_diag.txt`,
Part 2):

| W1 block, 12 fixture controls (6 G8(a), 6 G8(c)) | admitted, ≥ half (registered) | admitted, ≥ 1 | a control's P(ate \| admitted) ÷ P(ate) under ≥ half |
|---|---|---|---|
| random terrain, 15 s (W1) | **3 of 48 (6%)** | 45 of 48 (94%) | ×2.23 |
| random, 30 s | 8 of 48 | 46 of 48 | ×1.66 |
| random, 45 s | 12 of 48 | 48 of 48 | ×1.48 |

**This is indicative, not a measurement of W1's gate.**
- W1's controls are G8(a) and G8(c) plants on its own burn-in finals (§4.3 G8: 4 designed and 4 holistic per unit),
  not RBT-19's bodies.
- Its number of screen hosts also differs.
- But the mechanism does not depend on either. When the controls eat ≥ 1 item on about 20–35% of 15 s seasons,
  "at least half" admits only the upper tail of the per-draw count.
- A 36-draw battery then needs 36 of at most 96 draws in that tail.

## What the rule is for, and what it does here

**MUST 1** (the RBT-116 design adversary, `design-adversary/ADVERSARY.md`) asked to "drop or replace draws on which
the positive control eats 0 intact". That is reachability. The registered "at least half" is stricter, and in a patchy
15 s world it does two things MUST 1 did not ask for:
1. **It fails the gate for a reason unrelated to reachability.** In the fixture, 45 of 48 draws were reached by at
   least one control, and 3 were admitted.
2. **It selects on the controls' own intact seasons.** The screen's hosts are the G8(a) and G8(c) plants, which G8 then
   calls on the same draws; seasons are deterministic.
   - On admitted draws a control's intact eating is lifted **×2.23** in the fixture. RBT-129's cells gave ×1.88
     (PW) and ×1.42 (HP).
   - The arms' members are not screened, so G8's plants would be read on draws better for them than for the arms. G8's
     pass rules ((a) at 0.6 × c_G1, and (c) at ≥ 20%) would be judged optimistically.

## The proposal

**Amend §1.1 pre-data:** at W1, a draw is **admissible if at least one positive-control host eats ≥ 1 item on it
intact**. Everything else in §1.1 is unchanged: the 64-draw pool, pool order, the 4 + 16 + 16 assignment, extending
by 32 once, then failing.

This is the rule RBT-132 adopted at RBT-129's points (#478, ADOPT (c)), and its implementation already exists:
- `steer.admissible` with `steer.SCREEN_ANY`;
- the per-control `ate_by_host` column and the dispersion print (`planters.screen_line`).

**If ruled, the code change is exactly this:**
- **`steer.py`:** `SCREEN_ANY = frozenset(RBT129_POINTS) | {"W1"}`, and W1's table gains `ate_by_host`. The `world !=
  "W1"` guard in `screen_draws` is removed.
- **`tests/test_rbt116_steer.py` changes, and this is the amendment's real cost.** The registered test
  `test_screen_admits_by_half_the_hosts_and_assigns_in_pool_order` pins the half rule. On every third draw exactly one
  of four hosts eats: the registered rule rejects those draws (42 of 64 admitted), and ≥ 1 would admit them all.
  - So the amendment edits a registered RBT-116 test. That ends "`tests/test_rbt116_steer.py` has no diff against
    `ce69f17`", which every RBT-132 change has kept.
  - The edit is one test, and it is proposed here, not made:
    - the "bad" draws get zero eaters instead of one, so 42 of 64 are still admitted and the pool-order assertions are
      kept;
    - a new assertion checks that a one-eater draw is admitted at W1.
  - `test_screen_extends_once_then_fails` is unaffected: its two hosts always eat together.
  - In RBT-132's tests, `test_screen_rule_is_per_point_and_W1_keeps_half` is inverted for W1.
- **W1 byte-identity changes only in the screen,** and in that one registered test.
  - The seasons, the call and `power.py`/`power_tau1.txt` are untouched. `rbt132_w1_identity.py` does not screen, so
    it stays IDENTICAL.
  - The RBT-116 kill-sets (`steer_mutants.py`, `steer_mutants2.py`) must be re-run against the edited test file, and
    any screen mutant re-pointed.
  - `rbt132_battery_identity.py` would show W1's `screen_draws` differing in `admissible` only, at the four shares.
  - That is proved by re-running it with the rule set aside, as #478 did for the RBT-129 points.
- **The adversary's `rbt132_478_mutants.py`:** its `W1-in-SCREEN_ANY` mutant becomes the registered code. It is
  replaced by `W1-out-of-SCREEN_ANY`.

## Alternatives, briefly

- **Keep "at least half" and screen until 36 are admitted,** with a cap. This keeps the ×2 selection on G8's plants.
  At 6% admission it needs about 600 draws × the screen hosts per W1 gate.
- **A longer season at W1.** This changes W1's registered season (15 s) and every RBT-116 number priced on it. It is
  also not enough: 25% admitted at 45 s in the fixture.
- **A screen whose hosts are disjoint from G8's plants** (#478's ruling, item 4). This is the only route to a stricter
  screen without selection on G8's plants, if one is wanted. It needs a registered second host set.

## What the amendment does not solve

**The fixture's G8(c) controls never ate,** at any length or terrain in W1's block (`gate_diag.txt`, Part 2).
- If W1's own holistic G8(c) plants rarely eat, G8(c) ("STEERS on ≥ 20% of holistic hosts") may fail whatever the
  screen does.
- That is the gate measuring what it should, and it is not addressed here.
- #478's S-2 statement for RBT-129 (no post-data change to G8(c)'s layout, hosts, carrying rule or rung) has an
  obvious RBT-116 analogue. Whether to register it is the coordinator's call.
