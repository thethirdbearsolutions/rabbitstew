"""RBT-39: re-read a champion's items per metre against its own gait's expectation.

The bout conditions are `scripts/brake_or_compass.py`'s, unchanged, because that is the script every
items-per-metre figure in the family was read off: the arm's own `config.json`, `random_start=True`,
one robot on `spawn_layout(1, c, seed)`, `set_food_seed(seed)`, seeds 9000+s, and in-disc path
measured from the centre of mass every control tick.  The only additions are that the bout is
recorded frame by frame and that, at the spawn and before anything moves, the world is asked for
`--draws` further layouts it could equally have dealt -- which the recorded path is then replayed
against.  That is the null: the gait, the circling, the retracing and the body geometry are the
robot's own, and the one thing removed is any correlation between where it went and where the food
actually was.

usage: trajectory_null.py DATA_DIR KIND GEN [N_SEEDS] [N_DRAWS]
       trajectory_null.py runs/RBT-38/data/RBT-13 conventional 590 16 120
"""
import json
import sys
from dataclasses import replace

import numpy as np

from rabbitstew.forage_null import (NullResult, body_line_rate, in_disc_path, replay_many,
                                    swept_width, within_season_regrowth, world_layouts, world_spot_fn)
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

run, kind, gen = sys.argv[1], sys.argv[2], int(sys.argv[3])
n = int(sys.argv[4]) if len(sys.argv) > 4 else 16
draws = int(sys.argv[5]) if len(sys.argv) > 5 else 120

cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
ph = synthesize(g, cfg.synthesis)
food = cfg.food
disc, eat = food.radius, food.eat_radius
density = food.items / (np.pi * disc ** 2)
point_floor = 2 * eat * density
regrow_in_season = within_season_regrowth(food)


def bout(seed: int, blank: bool) -> dict:
    c = replace(cfg, random_start=True)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    # The world's own layouts, drawn at the spawn so the clearance rule sees the real start
    # positions; re-seeding puts the bout's own layout back bit for bit (asserted).
    real = sim.food_pos.copy()
    layouts = world_layouts(sim, [600000 + 997 * seed + d for d in range(draws)])
    sim.set_food_seed(seed)
    assert np.array_equal(sim.food_pos, real), "re-seeding did not restore the bout's layout"
    if blank:
        b = sim.brains[0]
        for i, ui in enumerate(ph.units):
            if ui.unit.kind == "sensor" and ui.unit.source in ("food", "agent"):
                b.W[:, i] = 0
    sim.start_recording(every=1)
    steps = int(round(c.duration / c.control_dt))
    last = sim.center_of_mass(0)[:2].copy()
    in_path = in_disc_ticks = 0.0
    for _ in range(steps):
        sim.step()
        p = sim.center_of_mass(0)[:2]
        step_len = float(np.linalg.norm(p - last))
        last = p.copy()
        if float(np.linalg.norm(p)) <= disc:
            in_disc_ticks += 1
            in_path += step_len
    geoms = sim.trajectory.as_array()[:, :, :2]
    observed = float(sim.food_eaten[0])
    # Frame 0 is the spawn, recorded before any step and never tested for eating: the replay starts
    # at frame 1.  `frame0_takes` measures what including it would have added, so the size of that
    # correction is reported rather than asserted away.
    counts = replay_many(geoms[1:], layouts, eat, regrow=regrow_in_season, spot_fn=world_spot_fn(sim))
    # Measured directly rather than by differencing two replays: the regrowth draws consume the
    # world's RNG, so two replays of the same layouts are not comparable draw for draw.
    frame0 = float((np.linalg.norm(geoms[0][None, :, None, :] - layouts[:, None, :, :], axis=3)
                    .min(axis=1) < eat).sum(axis=1).mean())
    res = NullResult(observed=observed, null_mean=float(counts.mean()),
                     null_sd=float(counts.std(ddof=1)), draws=len(counts),
                     path=in_disc_path(geoms, disc))
    # The body-width term on its own: this body, held in its spawn pose, sweeping a fresh straight
    # chord of the same disc past the same layouts.  Only needed once per body, so intact only.
    line = (body_line_rate(geoms[0], layouts, eat, disc, regrow=regrow_in_season,
                           spot_fn=world_spot_fn(sim)) if not blank else float("nan"))
    return {"items": observed, "null_items": res.null_mean, "null_sd": res.null_sd,
            "in_path": in_path, "com_path": res.path, "time_in_disc": in_disc_ticks / steps,
            "swept": swept_width(geoms, eat), "frame0_takes": frame0, "line_rate": line,
            "exploded": bool(sim.exploded[0])}


rows = {}
for label, blank in (("intact", False), ("noses blanked", True)):
    rs = [bout(9000 + s, blank) for s in range(n)]
    rows[label] = rs

print(f"{run} {kind} gen {gen}: {n} seeds x {draws} null layouts, "
      f"{food.items} items in a {disc:.1f} m disc ({density:.3f} items/m^2)")
print(f"point-robot floor 2*eat*density = {point_floor:.3f} items/m; "
      f"within-season regrowth {'on' if regrow_in_season else 'off'}; "
      f"body parts {len(ph.parts)}, swept corridor {np.mean([r['swept'] for r in rows['intact']]):.2f} m "
      f"against the floor's assumed {2 * eat:.2f} m")
hdr = f"{'':15s} {'items':>6s} {'null':>7s} {'in-disc m':>10s} {'items/m':>8s} {'null/m':>8s} {'ratio':>6s} {'t':>7s}"
print(hdr)
out = {}
for label, rs in rows.items():
    obs = float(np.sum([r["items"] for r in rs]))
    nul = float(np.sum([r["null_items"] for r in rs]))
    path = float(np.sum([r["in_path"] for r in rs]))
    per_seed = np.array([r["items"] - r["null_items"] for r in rs])
    se = float(per_seed.std(ddof=1) / np.sqrt(len(per_seed))) if len(per_seed) > 1 else 0.0
    t = float(per_seed.mean() / se) if se > 0 else float("nan")
    o_m, n_m = (obs / path if path > 0.05 else 0.0), (nul / path if path > 0.05 else 0.0)
    # `brake_or_compass.py` averages each seed's own ratio (guarded at 0.05 m), and that is the
    # statistic every published items-per-metre figure is, so it is reported beside the pooled rate.
    per_seed_rate = float(np.mean([r["items"] / r["in_path"] if r["in_path"] > 0.05 else 0.0 for r in rs]))
    per_seed_null = float(np.mean([r["null_items"] / r["in_path"] if r["in_path"] > 0.05 else 0.0 for r in rs]))
    out[label] = {"items": obs / len(rs), "null": nul / len(rs), "items_per_m": o_m, "null_per_m": n_m,
                  "ratio": o_m / n_m if n_m > 0 else float("nan"), "t": t,
                  "published_rate": per_seed_rate, "published_null_rate": per_seed_null,
                  "in_path": path / len(rs), "time_in_disc": float(np.mean([r["time_in_disc"] for r in rs])),
                  "frame0": float(np.mean([r["frame0_takes"] for r in rs]))}
    r = out[label]
    print(f"{label:15s} {r['items']:6.3f} {r['null']:7.3f} {r['in_path']:10.2f} {r['items_per_m']:8.3f}"
          f" {r['null_per_m']:8.3f} {r['ratio']:6.2f} {r['t']:+7.2f}")

i = out["intact"]
print(f"\nas brake_or_compass.py reports it (mean of per-seed ratios): "
      f"intact {out['intact']['published_rate']:.3f} vs own-gait null {out['intact']['published_null_rate']:.3f}, "
      f"blanked {out['noses blanked']['published_rate']:.3f} vs {out['noses blanked']['published_null_rate']:.3f}")
line = float(np.nanmean([r["line_rate"] for r in rows["intact"]]))
print(f"\npoint-robot floor   {point_floor:.3f} items/m   (what the family compared against)")
print(f"  + body width      {line:.3f} items/m   (this body, fresh straight chord: x{line / point_floor:.2f})")
print(f"  + its own gait    {i['null_per_m']:.3f} items/m   (the trajectory null: x{i['null_per_m'] / line:.2f} on the line,"
      f" x{i['null_per_m'] / point_floor:.2f} on the floor)")
print(f"measured, intact    {i['items_per_m']:.3f} items/m")
verdict = ("ABOVE its own gait" if i["t"] >= 2.5 else
           "BELOW its own gait" if i["t"] <= -2.5 else "INDISTINGUISHABLE from its own gait")
print(f"paired over {n} seeds: mean items - null = {i['items'] - i['null']:+.3f}, t = {i['t']:+.2f}  ->  {verdict}")
print(f"(frame-0 correction, items the replay would add by testing the spawn frame: {i['frame0']:+.4f})")
print(json.dumps({"run": run, "kind": kind, "gen": gen, "seeds": n, "draws": draws,
                  "point_floor": point_floor, "line_rate": line, "swept": float(np.mean([r['swept'] for r in rows['intact']])),
                  "rows": out}))
