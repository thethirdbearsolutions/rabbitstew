"""Paired per-seed lesion reading for one or more champions (RBT-38).

The family's probes ran every mode over the same seed list and then reported
each mode's own standard error, which is the wrong error term and hides the
shape of the effect.  This reports through `rabbitstew.paired`: per-seed
differences, the paired SE beside the old unpaired one, a sign-flip permutation
test, an exact sign test, and the count of seeds the lesion did not move at all.

The trial itself is RBT-10's `paired_nose.py` unchanged in substance, so the
numbers stay comparable with the 16-seed readings already posted.

With two champions it also reports the difference of their differences, which
is the contrast paper 6's centrepiece actually rests on: not that either
Pioneer is nose-dependent, but that one gains and one loses and the two can be
told apart.

usage: paired_lesion.py RUN KIND GEN[,GEN...] [SEEDS=64] [MODE=no_noses]
"""

import json
import sys
from dataclasses import replace

import numpy as np

from rabbitstew.genotype import Genotype
from rabbitstew.paired import ci95, difference_of_differences, paired
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

KEYS = ["items", "path_in", "cells", "items_per_cell", "items_per_m", "near_in", "time_in"]
BASE_SEED = 7000  #: the precursor's seed origin, so the first 16 seeds are the same bouts


def trial(g, ph, cfg, seed: int, mode: str) -> dict:
    c = replace(cfg, random_start=True)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    b = sim.brains[0]
    for i, ui in enumerate(ph.units):
        if ui.unit.kind != "sensor":
            continue
        s = ui.unit.source
        if (mode == "no_noses" and s in ("food", "agent")) or (mode == "no_env" and s != "oscillator"):
            b.W[:, i] = 0
    R, CELL = c.food.radius, 2 * c.food.eat_radius
    steps = int(round(c.duration / c.control_dt))
    path_in, cells, near_in, ticks_in = 0.0, set(), [], 0
    last = sim.center_of_mass(0)[:2].copy()
    for t in range(steps):
        sim.step()
        if t % 10 == 0:
            p = sim.center_of_mass(0)[:2]
            if float(np.linalg.norm(p)) <= R:
                ticks_in += 1
                path_in += float(np.linalg.norm(p - last))
                cells.add((int(np.floor(p[0] / CELL)), int(np.floor(p[1] / CELL))))
                live = sim.food_pos[np.abs(sim.food_pos).max(axis=1) < 1e5]
                if len(live):
                    near_in.append(float(np.linalg.norm(live - p, axis=1).min()))
            last = p.copy()
    food = float(sim.food_eaten[0])
    return dict(items=food, path_in=path_in, cells=len(cells), items_per_cell=food / max(len(cells), 1),
                items_per_m=food / max(path_in, 1e-9), near_in=float(np.mean(near_in)) if near_in else float("nan"),
                time_in=ticks_in / max(1, steps // 10))


def read(run: str, kind: str, gen: int, n: int, mode: str) -> dict:
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
    ph = synthesize(g, cfg.synthesis)
    out = {m: [trial(g, ph, cfg, BASE_SEED + s, m) for s in range(n)] for m in ("intact", mode)}
    res = {k: paired([r[k] for r in out["intact"]], [r[k] for r in out[mode]]) for k in KEYS}
    return {"name": g.name, "gen": gen, "raw": out, "paired": res, "cfg": cfg}


if __name__ == "__main__":
    run, kind = sys.argv[1], sys.argv[2]
    gens = [int(x) for x in sys.argv[3].split(",")]
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 64
    mode = sys.argv[5] if len(sys.argv) > 5 else "no_noses"
    reads = []
    for gen in gens:
        r = read(run, kind, gen, n, mode)
        reads.append(r)
        cfg = r["cfg"]
        chance = 2 * cfg.food.eat_radius * cfg.food.items / (np.pi * cfg.food.radius**2)
        print(f"\n=== {r['name']} ({kind} g{gen}), intact minus {mode}, {n} paired seeds "
              f"(blind-mow chance rate {chance:.3f} items/m; RBT-39: a real body sweeps wider than a "
              f"point, so exceeding it proves nothing and only falling below it is damning) ===", flush=True)
        print(f"  {'intact':>8} {mode[:8]:>8} | paired comparison")
        for k in KEYS:
            a = np.array([x[k] for x in r["raw"]["intact"]], dtype=float)
            b = np.array([x[k] for x in r["raw"][mode]], dtype=float)
            print(f"  {np.nanmean(a):8.3f} {np.nanmean(b):8.3f} | " + r["paired"][k].line(k))
        d = r["paired"]["items"]
        lo, hi = ci95(d)
        print(f"  items 95% CI [{lo:+.3f}, {hi:+.3f}]")
        print(f"  items per-seed differences: {' '.join(f'{int(v):+d}' if float(v).is_integer() else f'{v:+.2f}' for v in d.diffs)}")
        intact = np.array([x["items"] for x in r["raw"]["intact"]])
        lesion = np.array([x["items"] for x in r["raw"][mode]])
        print(f"  intact mean {intact.mean():.3f}   {mode} mean {lesion.mean():.3f}"
              f"   old-style unpaired t {(intact.mean() - lesion.mean()) / max(d.unpaired_se, 1e-12):+.2f}")
    if len(reads) == 2:
        a, b = reads
        dod = difference_of_differences(a["paired"]["items"], b["paired"]["items"])
        print(f"\n=== difference of differences: {a['name']} effect minus {b['name']} effect ===")
        print(f"  mean {dod.mean:+.3f}  SE {dod.paired_se:.3f}  t {dod.t:+.2f}  permutation p {dod.perm_p:.4f}")
        lo, hi = dod.mean - 1.96 * dod.paired_se, dod.mean + 1.96 * dod.paired_se
        print(f"  95% CI [{lo:+.3f}, {hi:+.3f}]  ->  {'separable' if lo * hi > 0 else 'NOT separable (interval spans zero)'}")
