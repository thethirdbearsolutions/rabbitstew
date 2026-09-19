"""RBT-66 adversary: the frozen probe blanks the nose OUTRIGHT. Is its axis verdict a
small-signal property of the circuit, or a large-signal artifact of the operating point?

The RBT-66 pre-registration promised "the realised small-signal response of the two axes to
its nose". What `axis_lesion.py` implements is a full blanking: the nose goes from its true
reading (about 1.5 on these bodies) to zero. Everything on the path is `tanh`, so that is a
LARGE-signal perturbation whose answer depends on where the brain already sits -- exactly
the defect RBT-81's adversary found in their own proposed drive value and fixed with
"halve the drive until the reading moves by less than a stated tolerance, and report the
drive used beside the number."

So: scale the lesion. Replace the nose reading `r` with `r*(1-k)` for a ladder of k, take
the same (steer, throttle) delta, and divide by k. If the normalised gain and the axis
winner converge as k falls, the verdict is a property of the circuit and the full blanking
is safe here. If they move, the published verdict is a property of k = 1.

At k -> 0 the tick-2 normalised gain must converge to the one multiply `W[e, nose]` resolved
onto the axes (runs/RBT-66-adversary/one_multiply.py), which is a calibration this probe has
never been given.

Usage: small_signal.py RUN KIND GEN [N_SEEDS] [HORIZON]
"""
import json, sys
from dataclasses import replace

import numpy as np

from rabbitstew.fixed import drive_effector_units, steering_throttle
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

KS = (1.0, 0.5, 0.25, 0.1, 0.05, 0.01, 0.001)
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

W = np.zeros((len(ph.units), len(ph.units)))
for s, d, w in ph.links:
    W[d, s] += w
pred = steering_throttle(sum(W[eL, n] for n in noses), sum(W[eR, n] for n in noses))


def tstat(xs):
    xs = np.asarray(xs, float)
    sd = xs.std(ddof=1)
    return float(xs.mean() / (sd / np.sqrt(len(xs)))) if sd > 0 else float("inf" if xs.mean() else 0.0)


rows = {k: {"d1": [], "dk": []} for k in KS}
for s in range(N):
    c = replace(cfg, random_start=True)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, 4000 + s))
    sim.set_food_seed(4000 + s)
    b = sim.brains[0]
    nose_set = set(noses)
    nose_pos = [j for j, u in enumerate(b.sensor_idx) if u in nose_set]
    if not nose_pos:
        continue
    acc = {k: {"d1": [], "dk": []} for k in KS}
    for tick in range(int(round(c.duration / c.control_dt))):
        sim.step()
        if tick % 10:
            continue
        sens = sim.sensor_values(0, sim.contact_bodies())
        keep = (b.activation.copy(), b._prev_input.copy())

        def traj(scale):
            b.activation, b._prev_input = keep[0].copy(), keep[1].copy()
            v = sens.copy()
            v[nose_pos] = v[nose_pos] * scale
            out = []
            for _ in range(H):
                b.step(v)
                out.append(steering_throttle(b.effector_output(*lk), b.effector_output(*rk)))
            return np.array(out)

        on = traj(1.0)
        for k in KS:
            off = traj(1.0 - k)
            d = (on - off) / k
            j = int(np.argmax(np.abs(d[1:, 0]) + np.abs(d[1:, 1]))) + 1
            acc[k]["d1"].append(tuple(d[1]))
            acc[k]["dk"].append(tuple(d[j]))
        b.activation, b._prev_input = keep
    for k in KS:
        for tag in ("d1", "dk"):
            if acc[k][tag]:
                a = np.array(acc[k][tag])
                rows[k][tag].append((a[:, 0].mean(), a[:, 1].mean()))

print(f"# RBT-66 adversary: is the axis verdict small-signal? — {run} {kind} gen {gen}")
print(f"n={len(rows[1.0]['dk'])} seeds from 4000, horizon {H}; lesion scaled by k and the")
print(f"delta divided by k, so every row is a gain per unit of nose signal removed.")
print(f"k = 1.0 is the published instrument (full blanking).\n")
print(f"One multiply on this genome predicts, as k -> 0 at tick 2: "
      f"steering {pred[0]:+.5f}, throttle {pred[1]:+.5f}.\n")
for tag, name in (("d1", "tick 2 (the direct path)"), ("dk", "peak-joint over the horizon — THE COMMITTED RULE")):
    print(f"### {name}\n")
    print("| k | steer / k | throttle / k | winner | |steer|-|throttle| paired | t |")
    print("|---|---|---|---|---|---|")
    for k in KS:
        v = rows[k][tag]
        if not v:
            continue
        s = np.array([x[0] for x in v]); t = np.array([x[1] for x in v])
        d = np.abs(s) - np.abs(t)
        win = "steer" if abs(s.mean()) > abs(t.mean()) else "throttle"
        sign = "+" if (s if win == "steer" else t).mean() > 0 else "-"
        print(f"| {k:g} | {s.mean():+.5f} | {t.mean():+.5f} | **{win} {sign}** | "
              f"{d.mean():+.5f} | {tstat(d):+7.2f} |")
    print()
