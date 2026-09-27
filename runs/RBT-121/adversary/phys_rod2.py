"""RBT-121 adversary (physics): rod sweeper, short vs long arm, 20 draws: food, net, COM displacement and path (m).

    phys_rod2.py > phys_rod2.txt      (uses phys_rod.py's rod(); nothing is written into any run)
"""
import os
import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phys_rod import SC, S, rod  # noqa: E402

print("# length(m)  food  net  disp(m)  path(m)   (20 draws 2131..2150, motor on)")
for L in (0.45, 1.5, 6.46):
    a = (L / 0.3) ** 1.5
    R = []
    for s in range(2131, 2151):
        cfg = replace(SC, random_start=True)
        sim = S.Simulation([rod(a)], cfg, spawns=S.spawn_layout(1, cfg, s))
        sim.set_food_seed(s)
        c0 = sim.center_of_mass(0)[:2].copy()
        prev, path = c0.copy(), 0.0
        n = int(round(cfg.duration / cfg.control_dt))
        for _ in range(n):
            sim.step()
            c = sim.center_of_mass(0)[:2].copy()
            path += float(np.linalg.norm(c - prev))
            prev = c
        R.append((sim.food_eaten[0], sim.food_score(0), float(np.linalg.norm(prev - c0)), path))
    R = np.array(R)
    print(f"  {L:5.2f}  {R[:,0].mean():.2f}±{R[:,0].std()/np.sqrt(len(R)):.2f}  {R[:,1].mean():+.2f}  {R[:,2].mean():.2f}  {R[:,3].mean():.2f}")
