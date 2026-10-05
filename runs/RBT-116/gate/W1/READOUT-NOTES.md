# RBT-116 W1 gate readout: the registered result

*Recorded 2026-10-05 by the RBT-116 builder, at the coordinator's request, after the gate completed. No code changed.
The four evidence files beside this note are copied byte for byte from the readout lane's checkpoint (sha256 below).
Nothing here reinterprets them.*

## Provenance

**The files' source.** They come from checkpoint `ckpt/rbt-116-w1-gate-readout`, commit `9beb3e2f8b43c3ba7f624c3ffd22a6cdbf583021`.
That checkpoint is a snapshot of `runs/RBT-116/gate/W1`. Its MANIFEST reads `2026-10-05T08:21:46Z` and `consistent`.
The readout lane builds that directory by merging every earlier lane's checkpoint, for example:
- `ckpt/rbt-116-w1-gate-a`, `3cf56e7c47ee995ed957c9aae96c8bd392f9b249`;
- `ckpt/rbt-116-w1-gate-pilot`, `c4d1fa388567be95c1de037f4e94939cd4475701`.

The remote holds 54 `ckpt/rbt-116-w1-*` labels.

| file | sha256 |
|---|---|
| `GATE.txt` | `a44dbcf6964c8a375dbb6e056b0712f9e6ac78555ffe549419a32ac451e785d7` |
| `g1.txt` | `9a340e8cac874d32670b481e2e89bc2ad5d4ab868e63d7bd79f6802d71a6c5f0` |
| `g6.txt` | `a6daae129f51de8cbb74b1da74b1657d3f5c82a5af51d17225809f53c1d00695` |
| `screen.txt` | `83d24fecb9e4de5f334529c40f8ce0b315a9b486b4d00c3512455b79886302e8` |

**The code the gate ran on.** Each lane refuses (exit 6) unless `HEAD:rabbitstew` and the blob of every script it
loads match its pins.
- `rabbitstew/` tree: `5c69daac35105f3230163c804141e25cab42946a`, throughout.
- Waves 0–3 (B, gate-a, g6-noise, g5, g8, g4, g7, g9, g6u): the lanes emitted at #548 (merged `5cae97b`), gate.py blob
  `2096a8ea`.
- Wave 4 (g6-pilot) and wave 5 (readout): the lanes re-emitted at #555 (merged `3ee3d83`), gate.py blob `e1c20f5c`,
  after ruling RBT116-PILOT-10. The coordinator relays that W4 and W5 ran on `3ee3d83`.
- Between the two gate.py blobs, only the pilot and the readout code differ.
- The runners' exact checkout shas are the coordinator's record. The builder can confirm only the pins the lanes
  enforce.

## The verdict (GATE.txt, verbatim)

> W1 GATE: FAIL (screen ok, G1 FAIL, G2 ok, G8 FAIL, G4 ok, G7 ok)

**The failing rows**, quoted verbatim:

> G1 FAIL: first paying rung 2.0; 0/16 PASS there; c_G1 0.000

> G8 FAIL: (a) confirmed 0.042 (bar 0.6 x c_G1 = 0.000) ok; (b) 1 STEERS among 35 paying FAILS; (c) 0.000 pooled, a STEERS host in 0/24 units FAILS; (d), (e) all NONE; (f) SENS_1 0.000; units flagged 24 (> 4: NO LAUNCH)

GATE.txt lists all 24 unit flags, one per line under the G8 row.

**The rows that passed**, quoted verbatim:

> SCREEN PASS: 56 admissible of 64

> G2 PASS: F at the first paying rung +0.426 items against the coverage gain +0.184 items (blind food: burn-in finals 0.941, RBT-113 finals 0.758, each side's host picked by the hosts rule)

> G4 PASS: designed 0/200 confirmed false STEERS, exact upper 0.015 (cap 0.05); holistic 0/200 confirmed false STEERS, exact upper 0.015 (cap 0.05)

> G7 PASS: the Pioneer's valley at W1 (16 hosts x 16 draws; pass/fail at the first paying rung a = 2; the full table, rungs x intermediates:)

GATE.txt also records `NOTE (H3): the first paying rung is a = 2, not the screen's a = 6; the screen's (a) plants were
built at a = 6 and the battery stands as ruled`.

## The pilot and the conditional sentence (GATE.txt, verbatim)

The pilot was **refused**: fallback A of ruling RBT116-PILOT-10. `pilot.json` is
`{"refused": true, "paying": {"designed": 105, "holistic": 7}, "ruling": "RBT116-PILOT-10 (A)"}`.

> G6 default (the cheapest passing option): D16 -- NO option passes: D = 16 with the conditional sentence (§2.4)

> G6 pilot (SHOULD 11; not pass/fail): the holding pilot could not be built (paying candidates {'designed': 105, 'holistic': 7}, fewer than 8 in a fauna; RBT116-PILOT-10)

> G6 conditional_sentence: YES (§2.4: the headline carries the holding sentence) -- holding pilot could not be built

`gate.json` records `conditional_sentence: true` and `chosen: D16`.

The power re-run, verbatim:

> half-lines bypass: detected 0.000 at K, 0.000 headlined (K and K + 2): 'the stronger no' is NOT registered; NEITHER names the lone-nose limit (re-checked at readout, R6-2)

## The registered consequence of a W1 gate FAIL

- **PREREGISTRATION.md §4.1:** "A point that fails its gate is reported as "world point failed the gate: [row]". It is
  not run." W1's failing rows are G1 and G8.
- **§4.3, G8's pass rule:** "More than 4 units flagged: no launch." GATE.txt flags 24 units.
- **§4.2, the only registered fallback within a world point:** "G = 10 is used only if G = 2.5 fails G2 and G = 10
  passes both G2 and G7, and it is then a different world point, with its own column." G2 **passed** at W1, so this
  fallback is not triggered.
- **§4.1, further points:** "Each world point is a separate registered comparison … Points are not pooled. If the
  owner's world sweep … is adopted, RBT-116 runs at the 2–3 sweep points the coordinator names. Each is registered by
  adding a column to the table above, before any of its arms."

**Decisions this hands on.** The registration gives no further step at W1: the point is reported and not run. Whether
RBT-116 goes to another world point is a decision outside W1's registration:
- The owner's decision of 2026-10-03 ungated RBT-116 at "one world point … One point only".
- The coordinator's ruling chose W1 rather than a Stage-1 point, because a point chosen after seeing Stage-1 results
  would be outcome-informed.
- A new point would need its own registered column and gate, before any of its arms (§4.1).

Choosing one, or closing RBT-116 at W1's report, belongs to the owner and the coordinator.

**G8(c)'s failure was anticipated before any W1 data.** `W1_GATE_AMENDMENT.md` lines 100–105 ("What the amendment
does not solve") recorded it pre-data:

> - If W1's own holistic G8(c) plants rarely eat, G8(c) ("STEERS on ≥ 20% of holistic hosts") may fail whatever the
>   screen does.
> - That is the gate measuring what it should, and it is not addressed here.

The same passage left registering an RBT-116 analogue of #478's S-2 statement to the coordinator. It is now ruling
RBT116-S2, recorded in `../GATE_NOTES.md`. It allows no post-data change to G1's first-rung rule, or to G8(c)'s layout,
hosts, carrying rule, rung or denominator, for W1.

## A known numerical instability in G9 (descriptive only; it affects no row)

**The season behind the outlier.** G9's census line `HP g8a/conventional/intact` reports a mean speed of `12.848`. That
comes from one blown-up season: member 2, draw 15 (0-based), mean speed 4745.4 m/s, food 0.
- Without that season, the group's mean speed is 0.491, in line with every other designed row (0.39–0.57).
- The adversary found it, and the builder confirmed it from `g9/HP.json` in the readout checkpoint.

**The wider pattern.** The same signature recurs at a much smaller scale:
- 21 other designed-body seasons across the four census worlds have work 0, food 0 and a mean speed of 3.2–21.6 m/s;
- that is what an exploded season books, since `Simulation.harvest` books neither food nor work once a robot has
  exploded;
- the census does not record the exploded flag, so this is an inference;
- each of these shifts its group's mean speed by 0.06 m/s or less.

(The holistic rows' work-0 seasons are different: their speeds are about 0, some eat, and they are bodies without
actuators.)

G9 is descriptive and decides nothing, so none of this touches a gate row. It is recorded as a known numerical
instability of the simulator's rare explosions.
