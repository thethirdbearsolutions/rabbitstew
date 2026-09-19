"""RBT-66 adversary: how much of the frozen probe's axis signal survives the Effector clip,
and does the clip fall asymmetrically on the two drive Effectors?

`Brain.effector_output` returns `clip(activation[units].sum(), -1, 1)`. The frozen probe
reads its axes THROUGH that clip. Two consequences the RBT-66 report does not address:

1. A clipped Effector contributes ZERO to the probe's delta no matter what the circuit puts
   on it, so the probe's magnitudes are attenuated by an amount that depends on the
   operating point rather than on the circuit.
2. If the clip falls on ONE drive Effector and not the other, a signal that the circuit puts
   equally on both is read as an axis SPLIT that the circuit does not have -- because
   steering is (L+R)/2 and throttle is (L-R)/2, so killing one side moves exactly half the
   magnitude from one axis onto the other. That is a mechanism for manufacturing an axis
   verdict, and it is the probe's analogue of the closed-loop leak the report found in the
   free-running lesion.

Measured here, on the same bodies, seeds and probe points the verdicts use.

Usage: saturation.py RUN KIND GEN [N_SEEDS] [HORIZON]
"""
import json, sys
from dataclasses import replace

import numpy as np

from rabbitstew.fixed import drive_effector_units
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

run, kind, gen = sys.argv[1], sys.argv[2], int(sys.argv[3])
N = int(sys.argv[4]) if len(sys.argv) > 4 else 16
H = int(sys.argv[5]) if len(sys.argv) > 5 else 8
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
ph = synthesize(g, cfg.synthesis)
lu, ru = drive_effector_units(ph)
eL, eR = lu[0], ru[0]
noses = [i for i, ui in enumerate(ph.units)
         if ui.unit.kind == "sensor" and ui.unit.source == "food"]
key = lambda i: (ph.units[i].part, ph.units[i].unit.dof)
lk, rk = key(eL), key(eR)

tot = both = oneside = neither = 0
asym = []                 # probe-ticks where exactly one side is clipped in the nose-on arm
for s in range(N):
    c = replace(cfg, random_start=True)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, 4000 + s))
    sim.set_food_seed(4000 + s)
    b = sim.brains[0]
    units = {"L": b.effectors.get(lk, []), "R": b.effectors.get(rk, [])}
    nose_set = set(noses)
    nose_pos = [j for j, u in enumerate(b.sensor_idx) if u in nose_set]
    if not nose_pos:
        continue
    for tick in range(int(round(c.duration / c.control_dt))):
        sim.step()
        if tick % 10:
            continue
        sens = sim.sensor_values(0, sim.contact_bodies())
        keep = (b.activation.copy(), b._prev_input.copy())
        raw = {}
        for kill in (False, True):
            b.activation, b._prev_input = keep[0].copy(), keep[1].copy()
            v = sens.copy()
            if kill:
                v[nose_pos] = 0.0
            seq = []
            for _ in range(H):
                b.step(v)
                seq.append((float(np.sum(b.activation[units["L"]])),
                            float(np.sum(b.activation[units["R"]]))))
            raw[kill] = seq
        b.activation, b._prev_input = keep
        for j in range(H):
            l_on, r_on = raw[False][j]
            l_off, r_off = raw[True][j]
            cl = abs(l_on) > 1.0 or abs(l_off) > 1.0
            cr = abs(r_on) > 1.0 or abs(r_off) > 1.0
            tot += 1
            if cl and cr:
                both += 1
            elif cl or cr:
                oneside += 1
                asym.append((l_on - l_off, r_on - r_off))
            else:
                neither += 1

print(f"# RBT-66 adversary: Effector saturation inside the frozen probe")
print(f"{run} {kind} gen {gen}; n={N} seeds, horizon {H}, same probe points as the verdicts\n")
print(f"| probe-ticks examined | neither side clipped | ONE side clipped | both clipped |")
print(f"|---|---|---|---|")
print(f"| {tot} | {neither} ({100*neither/tot:.1f}%) | **{oneside} ({100*oneside/tot:.1f}%)** "
      f"| {both} ({100*both/tot:.1f}%) |\n")
print("A probe-tick with ONE side clipped is the dangerous case: the clip removes that")
print("side's contribution, and since steering is (L+R)/2 and throttle is (L-R)/2, half the")
print("surviving side's magnitude is moved onto the other axis. Both axes then read equal in")
print("magnitude, so a one-sided clip cannot by itself pick a winner -- but it caps how far")
print("either axis can exceed the other, which is exactly the clause the verdict rule tests.")
if asym:
    a = np.array(asym)
    print(f"\nOn those {len(asym)} probe-ticks the raw (pre-clip) nose-on minus nose-off sums were")
    print(f"left {a[:,0].mean():+.5f} (|.| {np.abs(a[:,0]).mean():.5f}), "
          f"right {a[:,1].mean():+.5f} (|.| {np.abs(a[:,1]).mean():.5f}).")
print(f"\n| {'both clipped' if both else ''} | a probe-tick with BOTH sides clipped contributes "
      f"exactly zero to the delta on both axes, whatever the circuit does. |")
