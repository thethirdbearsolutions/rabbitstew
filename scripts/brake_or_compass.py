"""Is a nose-dependent forager a compass or a brake?  (RBT-13's check, as RBT-2 states it.)

A robot that eats less with its food sensors blanked has a nose that matters, but that is not yet
chemotaxis.  Two ways to lose food when the noses go:

- a **brake** wanders out of the food disc and never comes back, so it eats less because it is
  somewhere else.  Its nose is a one-bit "stay here" gate.
- a **compass** steers toward food.  With its noses on it covers the same ground more profitably:
  more items per metre of path *inside the disc*, and it spends its time nearer the nearest
  standing item.

So the discriminating numbers are measured per metre of in-disc path, not per season, and the
distance to the nearest item is measured only while the robot is in the disc, where both versions
of it are comparable.

usage: brake_or_compass.py RUN_DIR KIND GEN [N_SEEDS]     e.g. brake_or_compass.py runs/RBT-19/P-801 conventional 590 16
"""
import json
import sys
from dataclasses import replace

import numpy as np

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

run, kind, gen = sys.argv[1], sys.argv[2], int(sys.argv[3])
n = int(sys.argv[4]) if len(sys.argv) > 4 else 16
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
ph = synthesize(g, cfg.synthesis)
disc = cfg.food.radius


def trial(seed: int, blank: bool) -> dict:
    c = replace(cfg, random_start=True)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    if blank:
        b = sim.brains[0]
        for i, ui in enumerate(ph.units):
            if ui.unit.kind == "sensor" and ui.unit.source in ("food", "agent"):
                b.W[:, i] = 0
    steps = int(round(c.duration / c.control_dt))
    last = sim.center_of_mass(0)[:2].copy()
    in_disc_ticks = in_path = 0.0
    centre_d, near_d = [], []
    for _ in range(steps):
        sim.step()
        p = sim.center_of_mass(0)[:2]
        r = float(np.linalg.norm(p))
        step_len = float(np.linalg.norm(p - last))
        last = p.copy()
        centre_d.append(r)
        if r <= disc:
            in_disc_ticks += 1
            in_path += step_len
            live = sim.food_pos[sim.food_alive] if len(sim.food_alive) else sim.food_pos
            if len(live):
                near_d.append(float(np.linalg.norm(live - p, axis=1).min()))
    food = float(sim.food_eaten[0])
    return {"food": food, "time_in_disc": in_disc_ticks / steps, "in_disc_path": in_path,
            "items_per_m": food / in_path if in_path > 0.05 else 0.0,
            "centre_dist": float(np.mean(centre_d)), "near_dist": float(np.mean(near_d)) if near_d else float("nan")}


rows = {}
for label, blank in (("noses on", False), ("noses blanked", True)):
    rs = [trial(9000 + s, blank) for s in range(n)]
    rows[label] = {k: float(np.nanmean([r[k] for r in rs])) for k in rs[0]}

print(f"{run} {kind} gen {gen}, {n} seeds, food disc {disc:.1f} m")
print(f"{'':16s} {'items':>6s} {'in disc':>8s} {'in-disc m':>10s} {'items/m':>8s} {'from centre':>12s} {'to nearest':>11s}")
for label, r in rows.items():
    print(f"{label:16s} {r['food']:6.2f} {100 * r['time_in_disc']:7.0f}% {r['in_disc_path']:10.2f} {r['items_per_m']:8.3f}"
          f" {r['centre_dist']:11.2f} m {r['near_dist']:10.2f} m")

on, off = rows["noses on"], rows["noses blanked"]
lost = (on["food"] - off["food"]) / on["food"] if on["food"] > 0 else 0.0
better_rate = on["items_per_m"] > off["items_per_m"]
closer = on["near_dist"] < off["near_dist"]
print(f"\nyield lost when blanked: {100 * lost:.0f}%")
print(f"items per metre of in-disc path: {on['items_per_m']:.3f} on vs {off['items_per_m']:.3f} off  -> {'better with noses' if better_rate else 'no better with noses'}")
print(f"distance to the nearest item:    {on['near_dist']:.2f} m on vs {off['near_dist']:.2f} m off  -> {'closer with noses' if closer else 'no closer with noses'}")
print(f"time in the disc:                {100 * on['time_in_disc']:.0f}% on vs {100 * off['time_in_disc']:.0f}% off")
verdict = "COMPASS" if (better_rate and closer) else ("BRAKE" if on["time_in_disc"] > off["time_in_disc"] + 0.1 else "NEITHER")
print(f"\nverdict: {verdict}  (compass needs both more items per in-disc metre and a shorter distance to the nearest item)")
