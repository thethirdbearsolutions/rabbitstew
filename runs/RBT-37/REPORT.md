# RBT-37: seed 403's lump to the lab

Follow-on to RBT-12 (commit 18ef016). Subject: cap-403's final holistic best h199-15, a box (0.42 x 0.16 x 0.41 m, 11.1 kg) with a sphere (radius 0.135 m, 4.25 kg) on a ball joint, 35 units, 5 links, fresh-draw time at target 0.68. Control subject: cap-404's final holistic best h199-12, three cylinders in a chain, fresh-draw 0.02. All numbers on fresh draws; nothing tuned. Scripts used beyond the CLI are in `runs/RBT-37/` as logs and JSON; the helper scripts (parameterised four-lesion protocol, rolling checks, founders) are in `runs/RBT-37/scripts/`.

## 1. Replay and mechanism: it does not roll, it flails

Replay: `runs/RBT-37/h199-15.html` (solo, random terrain, seed 5000). Measured from recorded solo trajectories (`rolling.json`, `rolling2.json`; 15 s bouts, fresh start layouts 6000 to 6002, flat and random terrain):

| quantity | value |
|---|---|
| sphere centre offset from its ball-joint anchor | 0.135 m, equal to its radius: the joint is on the sphere's surface |
| sphere rotation | 49 to 52 turns per 15 s bout, about 3.4 rev/s, almost all of it relative to the box |
| sphere rotation x radius vs sphere-centre path | ratio 2.3: it spins more than twice as fast as rolling would need |
| sphere centre orbit about the box | 25 to 27 m per bout (a 0.135 m crank at 3.4 rev/s) |
| sphere height | min 0.13, mean 0.16, max 0.27 to 0.36 m; within 1 cm of the ground 50 to 70% of frames |
| box orientation | local up-vector's world z averages -0.03 to +0.09: the box lies on its side the whole bout, height 0.13 m |
| box travel | path 8.4 to 9.2 m per bout (0.6 m/s), net displacement 1.9 to 2.8 m |
| explosions | none, on flat or random terrain |

So the sphere is not a wheel. It is a ball on a crank the length of its own radius, spun at about three and a half turns a second, striking the ground on roughly every other frame and lifting off in between, and the box it is bolted to lies on its side and is dragged and hopped along at 0.6 m/s. Steering comes from modulating that spin with the target-direction sensor in the sphere's own frame. This is a flail-driven vibrobot, and it works the same on flat and random terrain (time at target 0.73 to 0.78 flat, 0.66 to 0.72 random). It is real physics as far as these numbers can tell: no explosions, consistent across draws and terrains, and the box speed of 0.6 m/s is unremarkable. It is also not what the paper's sentence "a body the search designs for itself" pictures, and the paper should say so: the search designed a crank.

## 2. Four-lesion protocol (paper 4's nine-bests table, eight fresh draws, seeds 6000 to 6007)

| Best | Units (global/local, parts) | Links same-part / cross-part / global | Reflex arcs | Env-driven effectors | Intact | No env sensors | No oscillators | No global | No local |
|---|---|---|---|---|---|---|---|---|---|
| cap-403 final (flails, steers) | 35 (11/24, 2) | 2 / 0 / 3 | 2 | 3 of 5 | +0.83 m, 0.70 | +0.25, 0.00 | +0.83, 0.70 | +0.79, 0.27 | +0.25, 0.00 |
| cap-404 final | 48 (12/36, 3) | 0 / 0 / 17 | 0 | 2 of 4 | +0.19, 0.03 | +0.08, 0.02 | +0.19, 0.03 | +0.01, 0.00 | +0.08, 0.02 |

cap-403 is situated and local as the paper predicts for solo-evolved bests: blank its environmental sensors or silence its local brains and it is a lump (+0.25 m, 0.00). Oscillators do nothing. Two things differ from the paper's "global brain is always inert" line. First, silencing cap-403's global brain keeps the approach (+0.79 m) but cuts the hold from 0.70 to 0.27: the global brain contributes to holding the target, not to reaching it, through the one global tanh neuron the RBT-12 unit-by-unit lesion found essential (0.31 m). Second, cap-404's controller is all global links (17 of 17) with zero reflex arcs, and silencing the global brain removes what little it does; it is the first best in the table whose behaviour lives in the global brain, and it is also the worst. No best in the table, these two included, has a link between the local brains of different parts.

## 3. Synergy (`rabbitstew synergy`, flat-ground capability in metres; no aligned transplant donors in either run)

| final best | full | bias-only brain | random links | body perturbed | brain dependence | body dependence |
|---|---|---|---|---|---|---|
| cap-403 holistic h199-15 | +3.52 | -0.50 | +1.38 | +3.00 | 1.14 | 0.15 |
| cap-403 quadruped c199-7 | +0.07 | +0.04 | -0.14 | -0.11 | 0.41 | 2.59 |
| cap-404 holistic h199-12 | +0.59 | -3.99 | -1.51 | -3.04 | 7.80 | 6.19 |
| cap-404 quadruped c199-7 | +1.14 | +0.05 | -0.04 | -0.05 | 0.96 | 1.05 |

cap-403's flail keeps 85% of its capability when its body is perturbed and loses everything when its brain is reduced to bias: the discovery is the controller on this crank, and the crank is robust to its own dimensions. Randomising the link weights still leaves +1.38 m, which says the body plus any non-zero drive on the sphere moves forward, and the specific weights supply the steering. cap-404's best is the opposite, fragile to everything, which is what a +0.59 m flat-ground crawler that fails the task looks like.

## 4. Fresh weights on the 403 body and wiring (`reevolve-403body`, 100 generations, seed 403, identical regime)

Protocol note: `--fixed-body <genotype>` keeps h199-15's whole genotype, body and brain wiring (35 units, 5 links, 2 reflex arcs), and redraws only the connection weights, so this measures how hard the weights are to find given the body and the wiring diagram, not how hard a controller is to find from scratch. The holistic side of the same run starts from random bodies and is the control. Fresh-draw time at target, 12 draws, every 20 generations (g0, g20, g40, g60, g80, g99):

- 403 body with redrawn weights: **0.27**, 0.48, 0.61, 0.63, 0.66, 0.59 (max 0.66 at g80; native controller 0.68)
- random bodies, same run: 0.05, 0.03, 0.02, 0.02, 0.00, 0.00

The weights are cheap. One of twenty random weight draws on this body and wiring already holds the goal 27% of the bout on fresh draws at generation 0, and forty generations bring it to 0.61, within noise of the native 0.68. The random-body control finds nothing in the same hundred generations, as 402, 404 and the first 140 generations of 403 found nothing. Together with the synergy row (85% of capability survives a body perturbation, none survives a bias-only brain, random links still give +1.38 m), the discovery in seed 403 is the crank plus the two reflex arcs that drive it; the numbers on those arcs are a few generations' work. What took 140 generations was shedding twelve parts to arrive at that crank.

Realised heritability over the run: 0.38 for the weights-only population against 0.14 for the random-body control; founders at generation 99: 5 of 20 and 2 of 20. Training-draw bests for the weights-only population ran 0.43 to 0.85, against 0.27 to 0.66 fresh, so the winner's curse is still worth about 0.15 even on a body that works.

## 5. Seed 404 to 400 generations (`cap-404-ext`, resumed from RBT-12's generation-200 state with the solo phase extended to 400)

Protocol note: RBT-12's command had `--locomotion-phase 200`, so a plain resume switches to competitive bouts at generation 200; the first attempt did (kept as `cap-404-ext.competitive-mistake.log`) and was discarded. The copy's saved config has `locomotion_phase` set to 400 and the run is solo time-at-target throughout.

Fresh-draw time at target, 12 draws, generations 200 to 399 (g200, g220, … g380, g399):

- lump: 0.01 0.00 0.06 0.00 0.01 0.00 0.00 0.00 0.00 **0.17 0.50**
- quadruped: 0.05 0.10 0.01 0.09 0.07 0.04 0.07 0.15 0.03 0.16 0.04 (max 0.16 at g380)

| | heritability 201-400 | heritability 1-400 | founders at g399 (of 20) |
|---|---|---|---|
| lump | 0.46 | 0.41 | 3 |
| quadruped | 0.19 | 0.22 | 4 |

**404 found it too, and it found the same thing.** The final best h399-0 is two parts: a box (0.38 x 0.19 x 0.37 m, 12.3 kg) with a flat paddle (0.22 x 0.31 x 0.10 m, 3.1 kg) on a ball joint whose centre is 0.11 m from the anchor. In solo bouts (`rolling-404ext.json`; the "sphere" labels in that file are the script's, the part is a box) the paddle orbits 17 m per bout, about 1.7 turns a second, the body lies on its side (up-vector z 0.04 to 0.06) and is dragged at 0.25 to 0.32 m/s for 2.3 to 2.8 m of displacement; time at target 0.24 to 0.45 on those four bouts, no explosions. Its lineage had been two-part since generation 250 (four parts briefly at 300) with training fitness at 0.02 to 0.06 for 120 generations on that body, then 0.45 at 370, 0.55 at 390, 0.70 at 399. The foothold is 20 to 30 generations old at the end of the run: founders are still at the drift baseline (3 of 20 against 3.6 expected under noise), the 0.50 is one generation's best on 12 draws, and whether it holds at 0.5 or climbs to 403's 0.68 is not known. The quadruped over the same 200 generations did what it did in the first 200: peaks of 0.15 and 0.16 that it does not keep, 0.04 at the end.

## What changes in paper 4

1. **The lump's ceiling is not 0.2 to 0.3 and "or nothing" is wrong.** Both seeds carried far enough found a solution scoring 0.5 to 0.7 on fresh draws; 403 at generation 140 to 160, 404 at 370 to 399. 402 stopped at 200 and is untested. The doc's "coin flipped once by generation 40" should go: 404 looked identical to a dead seed at 200 and at 360.
2. **What the search finds is a crank.** Twice, independently, the winning body is a heavy box lying on its side with one part on a ball joint whose centre is offset from the anchor (a ball one radius out in 403, a paddle 0.11 m out in 404), spun continuously and slapped against the ground; steering is a reflex from the target-direction sensor in the spinning part's own frame. It does not roll and it does not walk; it flails. The paper's phrase "a body the search designs for itself" should say what it designed. Both lineages went through the same sequence: shed parts down to two (403 at 140, 404 at 250), then sit on the two-part body at noise for anywhere from five to 120 generations until the weights on the crank came together.
3. **Given the body and the wiring, the weights are cheap.** Redrawn weights on 403's body and wiring score 0.27 fresh at generation 0 and 0.61 by 40; the random-body control in the same run finds nothing in 100. The hard part is the morphology, and morphology is what the designed quadruped is not allowed to change.
4. **The quadruped's ceiling and its inability to keep a peak now have 800 generations behind them** (403 to 200, 404 to 400, plus 401 and 402 to 100): fresh best 0.09, 0.14, 0.21, 0.16, never held, never steering (0 of 3 in every final). "The designed body is the safer start and the lower ceiling" stands, and the ceiling gap is now 0.15 to 0.2 against 0.5 to 0.7.
5. **Two lesion-section sentences need qualifying.** The global brain is not always inert: 403's holds the target through one tanh neuron (silence it, hold drops 0.70 to 0.27, approach unchanged). Proprioception's measured influence is not zero in every best: 404's generation-199 best (RBT-12) has joint-angle units with lesion losses of 0.6 to 1.0 m on flat ground, in a best that fails the task. Both are still consistent with the paper's larger claim that competence lives in local reflex arcs and no evolved brain has a link between parts (both new rows: zero cross-part links).

Not done here: a controller evolved from scratch on the 403 body (needs a builder for arbitrary evolved bodies; the fixed-body path keeps the wiring), 402 past generation 200, and any test of whether the flail is a contact artefact beyond the checks above (no explosions, consistent across draws, terrains and two independent seeds, box speeds of 0.3 to 0.6 m/s).

## Files

`h199-15.html` (replay), `rolling.json`, `rolling2.json`, `rolling-404ext.json` and logs (mechanism), `situated.json` and log (four-lesion rows), `synergy-403.json`, `synergy-404.json`, `reevolve-403body/` (run, `fresh_eval.json`, log), `cap-404-ext/` (run to 400, `fresh_eval.json`, log), heritability and founders text files. Trajectory files (`*.traj`) are not committed.
