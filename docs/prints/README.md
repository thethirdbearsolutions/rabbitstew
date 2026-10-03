# Prints

Champions as physical figurines, made by `scripts/print_champion.py` (install with `pip install -e .[print]`).
Each print has three files: the STL, a shaded preview (`.png`) and its provenance (`.txt`: run, generation,
seed, frame, MuJoCo version, scale). The pose is the robot's own, taken from a re-simulated solo bout,
so a print can be checked against its replay the same way the progress-report stills are.

| Print | Run | Pose | Size |
|---|---|---|---|
| `rbt19-p801-holistic-g590` | RBT-19 P-801, holistic, best of generation 590 | seed 3, t = 7.52 s | 108 × 108 × 52 mm incl. plinth |

Printing notes (FDM, 0.4 mm nozzle): PLA, 0.16–0.2 mm layers, 3 walls, 15 % infill. The plinth is the base, so
no supports are needed under it; spheres that overhang the plinth may want tree supports. Every unit is at least
1.6 mm thick (`--min-wall`), and parts that only touch in the simulation are fused, so the figure is one solid.
