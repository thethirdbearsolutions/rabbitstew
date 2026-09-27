"""RBT-120 deliverable 2 for RBT-113-style runs: per line, Sum gear, Sum gear / (motor_strength x mass) and the free-spin
work ceiling, founders and the U/D/C lines' generation-G-1 `final/`, both faunas (rabbitstew.motors does the measuring).

    motor_report.py [--motor-budget C] [--world runs/RBT-1xx/world.py] SEED_DIR [SEED_DIR ...] > motors.txt

SEED_DIRs are RBT-113 or RBT-120 seed directories with `final/` restored.  Founders are regenerated from the seed
directory's own U/config.json (its seed, salt and world), so the table is what the physics of that run saw; pass
--motor-budget to report a run as if under a budget (e.g. RBT-113's lines at 1.77).  Per line it prints the mean over
seed directories of each directory's mean, and [min, max] over directories, as probe_gear.py did; the torque-only
columns reproduce probe_gear.py's.
"""
import argparse
import glob
import json
import os
import sys
from dataclasses import replace

import numpy as np

from rabbitstew import motors
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, EvolutionConfig, generation_sim, initial_population, spawn_streams
from rabbitstew.genotype import Genotype

TERRAIN = 1131  # decompose.py's first fixed draw: the world is irrelevant to the motors, the duration and work cost are not


def groups_of(sd):
    cfg = EvolutionConfig.from_dict(json.load(open(os.path.join(sd, "U", "config.json"))))
    streams = spawn_streams(cfg.seed, cfg.holistic_stream_salt)
    out = {}
    for kind in (HOLISTIC, CONVENTIONAL):
        out[kind] = {"founders": initial_population(kind, cfg, streams[kind]).members}
        for L in "UDC":
            files = sorted(glob.glob(os.path.join(sd, L, kind, "final", "*.json")))
            if not files:
                raise SystemExit(f"{sd}/{L}/{kind}/final is empty: restore the arm's checkpoint first")
            out[kind][L] = [Genotype.load(p) for p in files]
    return cfg, out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--motor-budget", type=float, default=None)
    ap.add_argument("seed_dirs", nargs="+")
    a = ap.parse_args(argv)
    rows = {}
    budgets = set()
    for sd in a.seed_dirs:
        cfg, groups = groups_of(sd)
        sc = generation_sim(cfg, TERRAIN)
        if a.motor_budget is not None:
            sc = replace(sc, world=replace(sc.world, motor_budget=a.motor_budget))
        budgets.add(sc.world.motor_budget)
        for kind, gs in groups.items():
            for g, ms in gs.items():
                rows.setdefault((kind, g), []).append(motors.summarise([motors.capacity(m, sc) for m in ms]))
    b = sorted(budgets)
    print(f"# RBT-120 motor report over {len(a.seed_dirs)} seed directories; motor budget {'off' if b == [0.0] else ', '.join(f'{x:g}' for x in b)}"
          f"{' (imposed by --motor-budget)' if a.motor_budget is not None else ' (as run)'}; per-directory means, then mean [min, max] over directories")
    print("# sum gear and gear/(ms*mass): every driven DOF, all motor modes; 'torque' = torque motors only (probe_gear.py's columns);"
          " ceiling = torque motors' full-throttle free-spin work per season, yield units; 'over' = share of members the budget scaled")
    for (kind, g), R in rows.items():
        v = lambda k: np.array([r[k] for r in R])  # noqa: E731
        s, r, rt, c = v("sum_gear"), v("ratio"), v("ratio_torque"), v("ceiling_yield")
        print(f"{kind:12s} {g:8s} sum gear {s.mean():6.1f} [{s.min():6.1f}, {s.max():6.1f}]  gear/(ms*mass) {r.mean():.2f} [{r.min():.2f}, {r.max():.2f}]"
              f"  torque {rt.mean():.2f}  ball share {v('ball_share').mean():.2f}  ceiling (yield) {c.mean():.2f} [{c.min():.2f}, {c.max():.2f}]"
              f"  unbudgeted {v('unbudgeted_ratio').mean():.2f}  over {v('budgeted_share').mean():.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
