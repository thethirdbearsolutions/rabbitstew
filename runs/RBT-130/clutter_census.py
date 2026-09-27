"""RBT-130 (RBT-129 DESIGN section 3.1 and 5.6 item 4; design adversary S3): the realised clutter of each registered
level and layout, over 100 terrain seeds, so that the obstacle count N can be set from the FREE area.

The terrain generator (`world.random_terrain`) places obstacles uniformly within `random_radius`, skipping any within
0.6 m + footprint/2 of a spawn (`keep_clear`), with at most 50 x N tries.  With four spawns that removes part of the
disc, more of the small one.  This script measures, per layout's obstacle radius R_o = R_food - 0.4 and per clutter
level c:
  * the nominal N = round(14 c (R_o / 2.6)^2) (DESIGN section 3.1);
  * the free area (the disc less the keep-clear discs, by Monte Carlo over the seeds' spawn layouts);
  * N_free = round(14 c A_free(R_o) / A_free(2.6)), the count that holds the committed density on free ground;
  * the realised count and free-ground density at N_free, and how often the 50N-try cap binds.

Spawns are the ecology's own: `spawn_layout(4, sim, start_seed)` under `random_start` (the committed foraging season).
DESIGN ONLY: no simulator run.  python3 runs/RBT-130/clutter_census.py > runs/RBT-130/clutter_census.txt
"""
from dataclasses import replace

import numpy as np

from rabbitstew.simulation import SimConfig, spawn_layout
from rabbitstew.world import WorldConfig, random_terrain

SEEDS = range(100)
LEVELS = (0.5, 1.0, 1.5, 2.0)
LAYOUTS = (("U/HP", 3.0), ("PW", 4.0))


def keep_clear(start_seed: int) -> tuple:
    sim = SimConfig(random_start=True)
    return tuple((float(sp.position[0]), float(sp.position[1]), 0.6) for sp in spawn_layout(4, sim, start_seed))


def free_area(radius: float, clears: list, n: int = 20000) -> float:
    rng = np.random.default_rng(1)
    r = radius * np.sqrt(rng.uniform(size=n))
    a = rng.uniform(0, 2 * np.pi, n)
    x, y = r * np.cos(a), r * np.sin(a)
    fr = []
    for kc in clears:
        ok = np.ones(n, bool)
        for cx, cy, cr in kc:
            ok &= (x - cx) ** 2 + (y - cy) ** 2 >= cr ** 2
        fr.append(ok.mean())
    return float(np.pi * radius ** 2 * np.mean(fr))


def main():
    clears = [keep_clear(s) for s in SEEDS]
    base = free_area(2.6, clears)
    print(f"# committed obstacle disc R_o 2.6 m: area {np.pi * 2.6 ** 2:.1f} m^2, free {base:.1f} m^2 (four spawns, 0.6 m keep-clear)")
    print("# layout  R_o   c    N_nominal  A_free  N_free  realised mean [min, max]  cap binds  density on free ground (per m^2; committed 14/A_free(2.6))")
    for name, r_food in LAYOUTS:
        r_o = r_food - 0.4
        a_free = free_area(r_o, clears)
        for c in LEVELS:
            n_nom = round(14 * c * (r_o / 2.6) ** 2)
            n_free = round(14 * c * a_free / base)
            got, capped = [], 0
            for s, kc in zip(SEEDS, clears):
                w = replace(WorldConfig(terrain="random", terrain_seed=s, random_obstacles=n_free, random_radius=r_o), keep_clear=kc)
                k = len(random_terrain(w))
                got.append(k)
                capped += k < n_free
            got = np.array(got)
            print(f"  {name:5s} {r_o:.1f}  {c:.1f}  {n_nom:9d}  {a_free:6.1f}  {n_free:6d}  {got.mean():7.2f} [{got.min()}, {got.max()}]"
                  f"  {capped:3d}/100  {got.mean() / a_free:.3f} (target {14 * c / base:.3f})")


if __name__ == "__main__":
    main()
