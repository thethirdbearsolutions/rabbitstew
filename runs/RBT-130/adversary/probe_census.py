"""RBT-130 adversary: the clutter census's free area with the generator's real exclusion radius.

`world.random_terrain` rejects an obstacle whose centre lies within 0.6 m + foot/2 of a spawn, foot ~ U(0.15, 0.7);
`runs/RBT-130/clutter_census.py` measures the free area with 0.6 m alone.  Here the acceptance probability of a
uniform centre is measured with the footprint drawn per point, as the generator does, and N_free recomputed.
python runs/RBT-130/adversary/probe_census.py > runs/RBT-130/adversary/probe_census.txt"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from clutter_census import SEEDS, LEVELS, LAYOUTS, keep_clear, free_area

def free_area_foot(radius, clears, n=20000):
    rng = np.random.default_rng(1)
    r = radius * np.sqrt(rng.uniform(size=n)); a = rng.uniform(0, 2 * np.pi, n)
    x, y = r * np.cos(a), r * np.sin(a)
    foot = rng.uniform(0.15, 0.7, n)
    fr = []
    for kc in clears:
        ok = np.ones(n, bool)
        for cx, cy, cr in kc:
            ok &= (x - cx) ** 2 + (y - cy) ** 2 >= (cr + foot / 2) ** 2
        fr.append(ok.mean())
    return float(np.pi * radius ** 2 * np.mean(fr))

clears = [keep_clear(s) for s in SEEDS]
for label, fa in (("census (0.6 m)", free_area), ("generator (0.6 m + foot/2)", free_area_foot)):
    base = fa(2.6, clears)
    print(f"{label}: A_free(2.6) = {base:.2f} m^2, excluded {1 - base / (np.pi * 2.6 ** 2):.1%}")
    for name, r_food in LAYOUTS:
        r_o = r_food - 0.4; af = fa(r_o, clears)
        print(f"  {name:5s} R_o {r_o:.1f}: A_free {af:.2f} m^2, excluded {1 - af / (np.pi * r_o ** 2):.1%}; N_free at c = "
              + " / ".join(str(round(14 * c * af / base)) for c in LEVELS))
