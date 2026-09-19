"""RBT-66 adversary, coordinator's line 3: do the probe's tick indexing and
`steering_terms`' depth indexing agree by exactly one multiply, on one genome?

RBT-66's report says a "direct" sensor->Effector link is a TWO-TICK path here, because
`Brain.step` does `x = W @ activation` and only then writes the new sensor readings into
`activation` -- so a reading supplied at step N first reaches an Effector at step N+1.
RBT-81's and RBT-87's "depth-1 term" is one multiply by W. If those are the same arithmetic,
the two tickets are consistent; if not, one of them is off by one and downstream numbers
move.

This checks it three ways on the same genome and the same sensor, and also pins down a
NAMING collision that is a live hazard: RBT-66's ticket text assigns `a` to the steering
axis and `c` to the throttle axis, while `steering_terms` assigns `a` to the gradient
ACROSS the two wheel noses and `c` to their common mode -- both of which live on the
steering axis, because `onto_steering` sums both Effectors. `steering_terms` has no
throttle channel at all.

Usage: one_multiply.py RUN KIND GEN
"""
import json, sys
from dataclasses import replace

import numpy as np

from rabbitstew.analysis import steering_terms
from rabbitstew.fixed import drive_effector_units, steering_throttle
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

run, kind, gen = sys.argv[1], sys.argv[2], int(sys.argv[3])
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
ph = synthesize(g, cfg.synthesis)

lu, ru = drive_effector_units(ph)
eL, eR = lu[0], ru[0]
noses = [i for i, ui in enumerate(ph.units)
         if ui.unit.kind == "sensor" and ui.unit.source == "food"]

print(f"# RBT-66 adversary: one multiply — {run} {kind} gen {gen}\n")
print(f"drive Effector units: left {eL}, right {eR}   (one per side: "
      f"{len(lu)}/{len(ru)})")

# --- 1. the weight matrix, read directly: W[effector, nose] is one multiply -----------
W = np.zeros((len(ph.units), len(ph.units)))
for s, d, w in ph.links:
    W[d, s] += w
print("\n## 1. One multiply, read straight off W\n")
print("| nose unit | part | W[eL,n] | W[eR,n] | steering (L+R)/2 | throttle (L-R)/2 |")
print("|---|---|---|---|---|---|")
for n in noses:
    l, r = W[eL, n], W[eR, n]
    s, t = steering_throttle(l, r)
    part = ph.units[n].part
    tag = "chassis" if part is not None and ph.parts[part].parent is None else f"part {part}"
    print(f"| {n} | {tag} | {l:+.5f} | {r:+.5f} | {s:+.5f} | {t:+.5f} |")
tot_l = sum(W[eL, n] for n in noses)
tot_r = sum(W[eR, n] for n in noses)
tot_s, tot_t = steering_throttle(tot_l, tot_r)
print(f"\nAll food noses together: steering {tot_s:+.5f}, throttle {tot_t:+.5f} per unit reading.")

# --- 2. steering_terms, same genome, depth 1 ------------------------------------------
st = steering_terms(ph, depth=1)
print("\n## 2. `steering_terms(ph, depth=1)` on the same phenotype\n")
if st is None:
    print("returns None")
else:
    print(f"| s_left | s_right | a = (s_L-s_R)/2 | c = (s_L+s_R)/2 | balance | opposed | rho |")
    print("|---|---|---|---|---|---|---|")
    print(f"| {st['s_left']:+.5f} | {st['s_right']:+.5f} | {st['a']:+.5f} | {st['c']:+.5f} | "
          f"{st['balance']:.4f} | {st['opposed']} | {st['rho']:.3f} |")
    print(f"\nnose units it used: left {st['noses'][0]}, right {st['noses'][1]}; "
          f"Effectors {st['effectors']}")
    print("`onto_steering` sums BOTH Effectors, so s_left and s_right are both on the")
    print("STEERING axis. The quantity comparable to a single-nose steering gain is")
    print(f"s_left + s_right = {st['s_left']+st['s_right']:+.5f} on the Effector sum, i.e.")
    print(f"{0.5*(st['s_left']+st['s_right']):+.5f} in (L+R)/2 units — which is `c`, the")
    print("letter RBT-66's ticket text assigns to THROTTLE. Naming collision, not an error.")

# --- 3. the frozen probe's tick 1 and tick 2, divided by the sensor delta -------------
c = replace(cfg, random_start=True)
sim = Simulation([g], c, spawns=spawn_layout(1, c, 4000))
sim.set_food_seed(4000)
b = sim.brains[0]
key = lambda i: (ph.units[i].part, ph.units[i].unit.dof)
lk, rk = key(eL), key(eR)
nose_set = set(noses)
nose_pos = [j for j, u in enumerate(b.sensor_idx) if u in nose_set]
print("\n## 3. The frozen probe, tick by tick, divided by the sensor delta it was given\n")
print("| probe at sim tick | sensor delta (sum) | tick 1 steer/thr | tick 2 steer/thr | "
      "tick 2 / sensor: steer | throttle |")
print("|---|---|---|---|---|---|")
shown = 0
for tick in range(int(round(c.duration / c.control_dt))):
    sim.step()
    if tick % 10 or shown >= 4:
        continue
    sens = sim.sensor_values(0, sim.contact_bodies())
    dsens = float(np.sum(sens[nose_pos]))
    if abs(dsens) < 1e-9:
        continue
    keep = (b.activation.copy(), b._prev_input.copy())
    out = []
    for kill in (False, True):
        b.activation, b._prev_input = keep[0].copy(), keep[1].copy()
        s = sens.copy()
        if kill:
            s[nose_pos] = 0.0
        traj = []
        for _ in range(2):
            b.step(s)
            traj.append(steering_throttle(b.effector_output(*lk), b.effector_output(*rk)))
        out.append(traj)
    b.activation, b._prev_input = keep
    on, off = out
    t1 = (on[0][0] - off[0][0], on[0][1] - off[0][1])
    t2 = (on[1][0] - off[1][0], on[1][1] - off[1][1])
    print(f"| {tick} | {dsens:+.5f} | {t1[0]:+.6f} / {t1[1]:+.6f} | "
          f"{t2[0]:+.6f} / {t2[1]:+.6f} | {t2[0]/dsens:+.5f} | {t2[1]/dsens:+.5f} |")
    shown += 1
print(f"\nPredicted from one multiply (section 1, all noses): steering {tot_s:+.5f}, "
      f"throttle {tot_t:+.5f}.")
print("Tick 1 must be exactly 0.000000; tick 2 divided by the sensor delta must equal the")
print("one-multiply prediction up to the Effector's clip and any tanh on the path.")
