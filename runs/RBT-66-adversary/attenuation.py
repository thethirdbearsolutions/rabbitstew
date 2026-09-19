"""RBT-66 adversary: the frozen probe recovers the AXIS but not the MAGNITUDE, and the two
drive Effectors are attenuated by different amounts.

Effector units always take `tanh` (`Brain.__init__`: `func = u.func if u.kind == "neuron"
else "tanh"`), so an Effector's activation is `tanh(x)` and a perturbation `dx` arrives at
the output multiplied by `tanh'(x) = 1 - tanh(x)^2 = 1 - a^2`. The output CLIP in
`effector_output` never fires on these bodies (measured: 0 of 14,400 probe-ticks on three
champions), but the tanh underneath it is deep in saturation, and that is invisible in the
published readouts.

Two things measured here at the probe points the verdicts use:

1. `1 - a^2` per drive Effector: how much of the circuit's weight reaches the axis at all.
2. The RATIO between the two sides. Steering is (L+R)/2 and throttle is (L-R)/2, so if the
   two sides pass different fractions of what the circuit puts on them, a signal the circuit
   places symmetrically is read as an axis split that the circuit does not have. That is the
   probe's own analogue of the closed-loop leak it was built to avoid.

Usage: attenuation.py RUN KIND GEN [N_SEEDS]
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
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
ph = synthesize(g, cfg.synthesis)
lu, ru = drive_effector_units(ph)
eL, eR = lu[0], ru[0]

L, R, ratio = [], [], []
for s in range(N):
    c = replace(cfg, random_start=True)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, 4000 + s))
    sim.set_food_seed(4000 + s)
    b = sim.brains[0]
    for tick in range(int(round(c.duration / c.control_dt))):
        sim.step()
        if tick % 10:
            continue
        dl = 1.0 - float(b.activation[eL]) ** 2
        dr = 1.0 - float(b.activation[eR]) ** 2
        L.append(dl); R.append(dr)
        if max(dl, dr) > 1e-12:
            ratio.append(min(dl, dr) / max(dl, dr))

L, R, ratio = np.array(L), np.array(R), np.array(ratio)
print(f"# RBT-66 adversary: tanh attenuation at the drive Effectors — {run} {kind} gen {gen}")
print(f"n={N} seeds from 4000, at the probe points the verdicts use ({len(L)} samples)\n")
print("`1 - a^2` is the fraction of a perturbation that reaches the Effector output.\n")
print("| side | median | mean | p10 | p90 | fraction below 0.10 |")
print("|---|---|---|---|---|---|")
for name, v in (("left", L), ("right", R)):
    print(f"| {name} | {np.median(v):.4f} | {v.mean():.4f} | {np.percentile(v,10):.4f} | "
          f"{np.percentile(v,90):.4f} | {(v < 0.10).mean():.3f} |")
print(f"\n| symmetry min/max of the two sides | median {np.median(ratio):.4f} | "
      f"mean {ratio.mean():.4f} | p10 {np.percentile(ratio,10):.4f} | "
      f"fraction below 0.5: {(ratio < 0.5).mean():.3f} |")
print(f"\nA median of {np.median(L):.4f} / {np.median(R):.4f} means the probe reports roughly")
print(f"{100*np.median([L.mean(), R.mean()]):.1f}% of whatever weight the circuit puts on the")
print("Effector, and the figure moves with the operating point rather than with the circuit.")
