# RBT-39: what a gait meets by accident — every items-per-metre verdict, re-read

The family's brake-or-compass test compared a champion's items per metre of in-disc path against
`2 × eat_radius × density`. This ticket said that is a point robot's rate and asked for a null that
describes the actual robot. Built, validated against the simulator, and run on **every champion whose
items-per-metre figure is standing in a report or in `docs/foraging-world.md`**: ten of them, across
RBT-13, RBT-17, RBT-22, the baseline, RBT-16 and RBT-19.

Branch `claude/rbt-lowest-unclaimed-ticket-ems6yl`. Helper `rabbitstew/forage_null.py`, harness
`runs/RBT-39/trajectory_null.py`, raw output `runs/RBT-39/null.txt`, positive control
`runs/RBT-39/power_check.py`. No champion, config or seed was changed.

## 1. The answer to the bold question

> **Does any robot in this family collect food faster than its own gait would by accident?**

**No. Not one of the ten, and not one of their blanked counterparts.** The paired t over 16 seeds
runs from −0.91 to +1.63 against a bar of 2.5. The positive control in §6 shows the same test at the
same sample size flags a robot with a quarter of the crop on its own path at t = +9.3, and would
flag one with about **7%** of the crop on its path. The negative result is a measurement, not a
shortage of power.

## 2. The null, and why it is the robot's own

Replay the champion's **own recorded path** — every geom, every control tick — past layouts the world
could equally have dealt it. The gait, the circling, the retracing and the body geometry are held
exactly as they were; the only thing removed is any correlation between where the robot went and
where the food actually was.

Three things make it the same measurement as the family's, rather than a new one:

- **The bout conditions are `scripts/brake_or_compass.py`'s, unchanged** — the arm's own
  `config.json`, `random_start=True`, one robot on `spawn_layout(1, c, seed)`, `set_food_seed(seed)`,
  seeds 9000+s, in-disc path from the centre of mass every control tick. Run side by side on RBT-13's
  g590 at four seeds the two scripts agree bout for bout (0.25/1.50 items, 3.77/5.23 m in disc,
  58%/96% of the season in the disc), and the harness reproduces RBT-19's published 0.990 items/m
  for its g590 Pioneer to three decimals.
- **The null layouts come from the world's own generator**, not from a uniform guess:
  `Simulation.draw_food_spot` is now public and the null calls it, so a patchy world (RBT-19: three
  patches of radius 0.6) is nulled as a patchy world and the 0.8 m clearance rule is the world's own.
  The draws are taken at the spawn, before anything moves, so the clearance rule sees the same start
  positions the real bout did; re-seeding then restores the bout's own layout bit for bit (asserted
  every run).
- **The eat rule is the simulator's, proved rather than asserted.** Three tests in
  `tests/test_forage_null.py`: replaying the recorded per-frame food positions recovers the recorded
  eating events frame for frame, with and without regrowth; replaying the *starting* layout of a
  depleting bout reproduces the simulator's own total and event frames end to end; and the stacked
  replay used for the draws agrees with the one-at-a-time replay draw for draw. The second test also
  pins the frame offset — frame 0 is the spawn, recorded before any step and never tested for eating,
  so the replay starts at frame 1. Including it would have added up to +0.07 items on the widest lump.

## 3. The central result: the floor is wrong in both directions

The point-robot floor makes three wrong assumptions. Two of them can be separated, and they **pull
opposite ways**. `body width` is the same body, held in its spawn pose, sweeping a fresh straight
chord of the same disc past the same layouts — the floor with the point assumption repaired and
nothing else. `own gait` is the full trajectory null.

| champion | swept corridor | point floor | + body width | + its own gait | measured | paired t | verdict |
|---|---|---|---|---|---|---|---|
| RBT-13 Pioneer g590 | 1.14 m | 0.297 | 0.530 (×1.78) | **0.208 (×0.70)** | 0.219 | +0.22 | indistinguishable |
| RBT-13 lump g390 | 2.25 m | 0.297 | 0.853 (×2.87) | **0.448 (×1.51)** | 0.472 | +0.24 | indistinguishable |
| RBT-17 Pioneer g590 | 1.14 m | 0.297 | 0.531 (×1.79) | **0.288 (×0.97)** | 0.333 | +0.67 | indistinguishable |
| RBT-17 Pioneer g500 | 1.14 m | 0.297 | 0.531 (×1.79) | **0.308 (×1.04)** | 0.395 | +1.63 | indistinguishable |
| baseline-801 Pioneer g500 | 1.14 m | 0.297 | 0.530 (×1.78) | **0.291 (×0.98)** | 0.310 | +0.33 | indistinguishable |
| RBT-22 Pioneer g300 | 1.14 m | 0.297 | 0.530 (×1.78) | **0.208 (×0.70)** | 0.279 | +1.62 | indistinguishable |
| RBT-22 lump g590 | 2.86 m | 0.297 | 0.458 (×1.54) | **0.495 (×1.67)** | 0.532 | +0.42 | indistinguishable |
| RBT-16 Pioneer g590 (`ce861`) | 1.14 m | 0.594 | 0.964 (×1.62) | **0.761 (×1.28)** | 0.761 | +0.00 | indistinguishable |
| RBT-19 Pioneer g590 | 1.14 m | 0.644 | 1.056 (×1.64) | **0.805 (×1.25)** | 0.759 | −0.18 | indistinguishable |
| RBT-19 lump g590 | 1.97 m | 0.644 | 1.163 (×1.81) | **0.648 (×1.01)** | 0.546 | −0.91 | indistinguishable |

Rates are items per metre of in-disc path, pooled over 16 seeds × 200 null layouts. `t` is the paired
t of items eaten minus the bout's own null mean, over the 16 seeds. The multipliers are against the
point-robot floor.

**Body width raises the expectation by ×1.54 to ×2.87.** The ticket was right about that, and even the
narrowest body here — the Pioneer, whose geoms reach only 0.22 m from its root, less than the 0.35 m
eat radius — clears the floor by ×1.78 on width alone, because eating on the minimum over geoms
extends the swept corridor in every direction at once.

**The gait cuts it back by ×0.39 to ×1.08, and on nine of ten bodies the cut is the larger term.**
These robots circle, retrace, and leave the disc; a fresh straight chord is a generous idealisation of
what they do. Net, the honest null lands anywhere from **0.70× to 1.67×** the point-robot floor.

### Two corrections to this ticket's own premise

The ticket closed its defect section with what it called the one thing that could be said safely:

> falling *below* the point-robot floor is damning under any correction, since a wider body can only
> raise the expectation. Exceeding it proves nothing.

The second half is right and now has a number: the true null exceeds the floor on eight of ten
champions, so a rate above 0.297 is no evidence of anything.

**The first half is wrong, and measurably so.** A wider body can only raise the expectation *for a
fixed path*, but the path is not fixed — it is the robot's own, and retracing lowers the expectation
by more than width raises it. On three of ten champions the honest null sits **below** the
point-robot floor (×0.70, ×0.70, ×0.97), so falling below the floor is not damning either: RBT-22's
Pioneer g300, the very robot the ticket cites as "damning under any correction" at 0.247 against
0.297, has an own-gait null of **0.208** and measures 0.279 — *above* its own expectation, not below.
The floor is not a lower bound on the null. It is not a bound at all. **It should be quoted as
neither, and that is what §7 changes in the scripts and the docs.**

## 4. The four arms re-read, claim by claim

| arm | the claim as published | re-read against its own gait | verdict on that leg |
|---|---|---|---|
| **RBT-13**, Pioneer g590 | "it eats 0.276 items per metre of in-disc path, which is what a blind mow of that path should meet (0.297), so it is not finding food faster than chance, it is staying where the food is" | 0.219 measured against a **0.208** own-gait null, t = +0.22 | **right conclusion, wrong reason.** It is not finding food faster than chance — but its own chance is 0.208, not 0.297, and it is *level* with it, not below it. The published margin was luck. |
| **RBT-13**, lump g390 | a mower that "carries a nose it never reads" | 0.472 against 0.448, t = +0.24 | **strengthens.** RBT-38 found 64 of 64 bouts bit-identical with the nose blanked; this adds that the mow itself is exactly what its gait meets. |
| **RBT-17**, Pioneer g590 | brake, the items-per-metre leg quoted against the floor | 0.333 against 0.288, t = +0.67 | **the brake stands; the items-per-metre leg never supported it.** The brake signature is time in the disc (98% intact, RBT-38's t = +6.54), which this ticket does not touch. |
| **RBT-17**, Pioneer g500 | brake | 0.395 against 0.308, t = +1.63 | same: **brake stands on time in the disc, not on the rate.** |
| **baseline-801**, Pioneer g500 | the baseline's brake, 88% published, 83% at 64 paired seeds | 0.310 against 0.291, t = +0.33 | **brake stands, rate leg unsupported.** Its 60% time in the disc against a blanked robot's is what carries it. |
| **RBT-22**, Pioneer g300 | "eats *below* the blind-mow floor with its nose on, 0.247 against 0.297 — falling below the floor is damning" | 0.279 against **0.208**, t = +1.62 | **the leg inverts.** Corrected, this robot is at or slightly above its own gait's expectation. Nothing survives either way: RBT-38 killed the nose effect itself at 64 paired seeds (+0.031 items, t = +0.14). |
| **RBT-22**, lump g590 | "the noseless holistic g590 clears it at 0.48 to 0.52 on body width alone" | 0.532 against 0.495, t = +0.42 | **right about the conclusion, wrong about the mechanism.** Its null is 1.67× the floor, but body width alone accounts for only ×1.54 — uniquely in this set, its gait *adds* (×1.08 on the straight line). It is a better-than-straight-line mower, not a wide one. |

Nothing in any brake verdict moves. Every one of them rested independently on time inside the disc and
mean distance from the centre, and this ticket does not touch those channels. What moves is that
**the items-per-metre leg of each argument should never have been quoted**, in either direction.

## 5. `ce861` and RBT-58: the verdict confirmed, the rule still rejected

RBT-16's season-590 Pioneer is the family's strongest nose effect (93% of yield, t = +8.18 at 64
paired seeds) and the only champion RBT-38 could not call a brake. RBT-58 read it as a throttle on
the ground that its items per cell of new ground, 0.406, sits 2% below the 0.416 density expectation.

This null reaches the same verdict from a different direction, and more sharply:

**`ce861` measures 0.761 items per in-disc metre against an own-gait null of 0.761. Paired t = +0.00.**

Its whole apparent advantage is gait. Blanked it is nearly stationary and measures 0.104 against its
own null of 0.069 (t = +0.55) — also indistinguishable. So **both states sit exactly on their own
gait's expectation, and the +0.615 items-per-metre "rise" that RBT-58's pre-registration counted as a
compass leg is entirely the null rising**: the intact gait covers fresh ground, the blanked one
shuffles, and nothing is left over for steering. RBT-58's conclusion was right and its criterion's
items-per-metre leg was, as it suspected, satisfiable by mobility alone.

My interim comment on this ticket measured the other half: RBT-58's per-cell statistic carries this
ticket's defect too, overstating items per cell by 1.67× to 1.91× on the two RBT-19 bests, because its
denominator counts cells the centre of mass entered while its numerator counts eating by any geom.
**That leaves RBT-58's verdict strengthened and its proposed standing rule still unsafe** — as
implemented, "items per cell of new ground above `density × cell_area`" is a test a wide body passes
for being wide. The replacement rule is in §7.

## 6. Would this null find a compass? (the positive control)

A null that answers "indistinguishable" ten times out of ten is worth nothing until it is shown
capable of the other answer at the sample size actually used. `power_check.py` takes a champion's real
recorded path and deals it a layout with a stated fraction of the items planted *on that path* — which
is what a perfect compass would have achieved, since a robot that steers to food ends up with food
where it went. Everything else is held: same bouts, same seeds, same 200 null layouts, same paired t.

| planted on its own path | `ce861` t | RBT-22 lump g590 t |
|---|---|---|
| 0% (a layout the world dealt) | −1.08, indistinguishable | −1.32, indistinguishable |
| 25% | **+9.32, above** | **+4.17, above** |
| 50% | +19.00, above | +13.18, above |
| 100% | +42.14, above | +22.38, above |

The 0% row is the control on the control and reads as it must. Taking the response as linear in the
planted fraction, t crosses 2.5 at roughly **7%** of the crop for `ce861` and **15%** for the lump. No
champion in §3 reads above +1.63. **A compass that steered even a fifteenth of the crop onto its own
path would have shown up in this test, and none did.**

## 7. What changes in the scripts and the docs

- `scripts/paired_lesion.py` printed `blind-mow chance rate` with an RBT-39 caveat saying only
  falling below it is damning. The rate now prints labelled as a point-robot rate that **bounds
  nothing in either direction**, pointing at `rabbitstew.forage_null`.
- `scripts/brake_or_compass.py`'s compass criterion ("more items per metre of in-disc path") now says
  what that has to be measured against.
- `docs/foraging-world.md` and `docs/paper-5-the-blind-forager.md` carry the correction beside the
  original wording rather than a silent edit.
- **The rule this leaves behind, replacing RBT-58's:** no controller is called a compass unless it
  beats **its own trajectory-preserving null** — its own recorded path replayed against layouts the
  world could equally have dealt it — by a stated paired margin over a stated number of seeds, with a
  positive control showing the test can detect planting at that sample size. Neither the per-metre
  floor nor the per-cell expectation is a null; both are properties of a point robot, and every real
  body here differs from a point by more than the effect being tested for.

## 8. Caveats, stated rather than buried

- **The trajectory is not independent of the layout it was collected against.** A robot that senses
  food went where it went partly *because* of where the food was, so holding its path fixed while
  redrawing food is conservative in an unquantified direction: it gives the robot credit for a path
  that a compass earned. This makes the null harder to beat, not easier, so it cannot manufacture the
  negative result — but it is the reason to read "indistinguishable" as "no evidence of steering"
  rather than "proof of none".
- **The straight-chord body-width term holds the body in its spawn pose.** A lump that changes shape
  as it walks sweeps more than that, so ×1.54 to ×2.87 is a floor on the width term, which makes the
  gait term's dominance a conservative reading too.
- **Regrowth inside a replay draws from the world's generator but at a different RNG state** than the
  real bout's. Distributionally identical, bit-wise different; it is why the frame-0 correction is
  measured directly rather than by differencing two replays.
- **16 seeds, 200 draws, one arm each.** The per-seed null mean carries its own sampling error from
  the 200 draws; it is small beside the across-seed spread, which is what the paired t uses.
- RBT-19's persistent world is nulled with **full fresh arenas**, because that is what
  `brake_or_compass.py` measured (`set_food_seed` on a new arena) and therefore what the published
  0.990 items/m is. A season inside the running ecology starts from carried-over state and about half
  the spots standing empty; this report says nothing about that bout, and any items-per-metre figure
  read there needs its own draw.

## 9. Files

`runs/RBT-39/trajectory_null.py` (the harness), `sweep.sh` (the ten champions), `null.txt` (raw),
`summarise.py`, `power_check.py`. Helper `rabbitstew/forage_null.py`; `Simulation.draw_food_spot`
made public in `rabbitstew/simulation.py`; twelve tests in `tests/test_forage_null.py`. Champions are
regenerated byte-identically from their own branches by `runs/RBT-38/extract.sh`, plus RBT-22's
holistic g590 and RBT-19's own committed run dir; none is committed here.
