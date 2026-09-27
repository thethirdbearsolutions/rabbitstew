"""RBT-113 readout adversary, probe 4: does the holistic up line eat by foraging, or by a loophole / blind coverage?

    probe_food.py [--per-dir K] [--workers W] SEED_DIR [SEED_DIR ...] > probe_food.txt

For K members (fixed rng) of each seed directory's U line and founders, both faunas, on all four of decompose.py's
fixed draws, solo, three conditions:
  * intact: the registered season (items eaten must equal decompose.py's scoring of the same member and draw);
  * blind: every `food` sensor reads 0 (smell removed; body, brain and world otherwise unchanged);
  * decoy: every `food` sensor smells a MIRRORED layout (each live item at (-x, -y)): input statistics are kept, the
    information about where the real items are is not.
If the up line eats by following smell, blind and decoy eat less than intact.  If it eats by blind coverage
(moving a lot through a disc of 12 regrowing items), they eat about the same.  Also reported: the ground each
season covers (distinct 0.35 m cells under any part, xy), and items eaten per 100 cells.
"""
import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import decompose  # noqa: E402
import world  # noqa: E402

import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402

_orig = S.Simulation._intensity


def season(gd, sim_cfg, start, mode):
    g = Genotype.from_dict(gd)
    cfg = replace(sim_cfg, random_start=True)
    sim = S.Simulation([g], cfg, spawns=S.spawn_layout(1, cfg, start))
    sim.set_food_seed(start)
    if mode != "intact":
        def fake(self, pos, pts, _s=sim):
            if pts is _s.food_pos:
                return 0.0 if mode == "blind" else _orig(self, pos, -pts)
            return _orig(self, pos, pts)
        sim._intensity = fake.__get__(sim)
    n = int(round(cfg.duration / cfg.control_dt))
    cells = set()
    nsens = sum(1 for u in sim.phenotypes[0].units if u.unit.kind == "sensor" and getattr(u.unit, "source", None) == "food")
    for _ in range(n):
        sim.step()
        for x, y in sim.data.geom_xpos[sim.robots[0].geoms][:, :2]:
            cells.add((int(np.floor(x / 0.35)), int(np.floor(y / 0.35))))
    food = 0.0 if sim.exploded[0] else float(sim.food_eaten[0])
    return food, len(cells), nsens


def job(args):
    gd, sims = args
    out = {}
    for mode in ("intact", "blind", "decoy"):
        r = [season(gd, sims[j], s, mode) for j, (_, s) in enumerate(decompose.DRAWS)]
        out[mode] = float(np.mean([x[0] for x in r]))
        if mode == "intact":
            out["cells"] = float(np.mean([x[1] for x in r]))
            out["food_sensors"] = r[0][2]
            out["registered"] = float(np.mean([S.run_group([Genotype.from_dict(gd)], sims[j], s)[0]["food"] for j, (_, s) in enumerate(decompose.DRAWS)]))
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-dir", type=int, default=3)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("seed_dirs", nargs="+")
    a = ap.parse_args(argv)
    rng = np.random.default_rng(113004)
    tasks, keys = [], []
    for d in a.seed_dirs:
        op, seed = decompose.parse_seed_dir(d)
        cfg = world.evolution_config("U", op, seed=seed)
        sims = [generation_sim(cfg, t) for t, _ in decompose.DRAWS]
        streams = spawn_streams(seed, cfg.holistic_stream_salt)
        for kind in (HOLISTIC, CONVENTIONAL):
            groups = {"founders": initial_population(kind, cfg, streams[kind]).members}
            fs = sorted(os.listdir(os.path.join(d, "U", kind, "final")))
            groups["U"] = [Genotype.load(os.path.join(d, "U", kind, "final", f)) for f in fs]
            for gname, ms in groups.items():
                for i in rng.choice(len(ms), a.per_dir, replace=False):
                    tasks.append((ms[i].to_dict(), sims))
                    keys.append((d, kind, gname))
    with ProcessPoolExecutor(a.workers) as pool:
        res = list(pool.map(job, tasks, chunksize=1))
    print(f"# probe_food.py: {len(res)} members x 4 draws x 3 conditions; items eaten per 15 s solo season (mean over the 4 draws)")
    for kind in (HOLISTIC, CONVENTIONAL):
        for gname in ("founders", "U"):
            R = [r for k, r in zip(keys, res) if k[1] == kind and k[2] == gname]
            I, B, Dc = (np.array([r[m] for r in R]) for m in ("intact", "blind", "decoy"))
            cells = np.array([r["cells"] for r in R])
            match = np.mean([abs(r["intact"] - r["registered"]) < 1e-9 for r in R])
            print(f"\n{kind} {gname}: n={len(R)}  intact matches run_group {match:.2f};  with >=1 food sensor {np.mean([r['food_sensors'] > 0 for r in R]):.2f}")
            print(f"  items eaten: intact {I.mean():.3f}  blind {B.mean():.3f}  decoy {Dc.mean():.3f}   (intact - decoy {np.mean(I - Dc):+.3f}, members intact > decoy {np.mean(I > Dc):.2f}, < {np.mean(I < Dc):.2f})")
            print(f"  ground covered: {cells.mean():.0f} cells of 0.35 m;  items per 100 cells {100 * I.sum() / max(cells.sum(), 1):.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
