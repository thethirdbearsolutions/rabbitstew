"""Do the cross-part (neighbour) links matter?  Fresh-draw solo trials of the holistic bests under:
intact; cross-part links cut (every link whose two ends sit in different parts' local brains);
part 0's local brain silenced; part 1's local brain silenced; all local brains silenced.
Same eight draws (seeds 6000-6007) as situated.py.  Effectors keep their bias, as in situated.py."""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN = "runs/RBT-11/sims-901"
GENS = [int(x) for x in sys.argv[1:]] or [50, 100, 149]
SEEDS = list(range(6000, 6008))
cfg = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])

def trial(g, seed, mode):
    c = replace(cfg, opponent_proxy=True)
    spawn = spawn_layout(2, c, seed)[0]
    sim = Simulation([g], c, spawns=[spawn])
    b = sim.brains[0]
    ph = synthesize(g, c.synthesis)
    U = ph.units
    if mode == "no_cross_part":
        for s, d, w in ph.links:
            if U[s].part is not None and U[d].part is not None and U[s].part != U[d].part:
                b.W[d, s] = 0.0
    elif mode.startswith("no_local_p") or mode == "no_local":
        which = None if mode == "no_local" else int(mode[len("no_local_p"):])
        for i, ui in enumerate(U):
            if ui.part is None or ui.unit.kind == "effector": continue
            if which is None or ui.part == which:
                b.W[i, :] = 0.0; b.W[:, i] = 0.0; b.bias[i] = 0.0
    sim.run()
    return {"progress": float(sim.progress(0)), "tat": float(sim.time_at_target(0))}

# sanity: W orientation.  situated.py zeroes b.W[:, i] to blank a sensor's outputs, so W[dst, src].
out = {}
for gen in GENS:
    g = Genotype.load(f"{RUN}/holistic/best_gen{gen:04d}.json")
    ph = synthesize(g, cfg.synthesis); U = ph.units
    ncross = sum(1 for s, d, _ in ph.links if U[s].part is not None and U[d].part is not None and U[s].part != U[d].part)
    row = {}
    for mode in ("intact", "no_cross_part", "no_local_p0", "no_local_p1", "no_local"):
        rs = [trial(g, s, mode) for s in SEEDS]
        row[mode] = {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}
    out[gen] = {"cross_part_links": ncross, "scores": row}
    print(f"g{gen} (cross-part links {ncross}): " + "  ".join(f"{m} {v['progress']:+.2f}/{v['tat']:.2f}" for m, v in row.items()), flush=True)
json.dump(out, open("runs/RBT-11/crosspart.json", "w"), indent=1)
