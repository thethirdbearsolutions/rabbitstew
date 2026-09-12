"""Lab study of the cap-401 final lump: per-unit lesions, the bias-equivalence test for the global brain,
and behavioural metrics (path, straightness, arrival, hold) on fresh draws."""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
run = "solo/cap-401"; n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
cfg = replace(SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"]), opponent_proxy=True)
g = Genotype.load(f"{run}/holistic/best_gen0199.json")
ph = synthesize(g, cfg.synthesis)
GLOBAL = [i for i, u in enumerate(ph.units) if u.part is None]
def trial(seed, mode):
    sp = spawn_layout(2, cfg, seed)[0]
    sim = Simulation([g], cfg, spawns=[sp]); b = sim.brains[0]
    def silence(i): b.W[i, :] = 0; b.W[:, i] = 0; b.bias[i] = 0
    if mode.startswith("lesion:"):
        for i in map(int, mode[7:].split("+")): silence(i)
    elif mode == "no_global":
        for i in GLOBAL: silence(i)
    elif mode == "no_global+bias14":
        for i in GLOBAL: silence(i)
        b.bias[14] = 0.34  # the global constants' net contribution folded into the effector bias
    elif mode == "no_global+bias14=0":
        for i in GLOBAL: silence(i)
        b.bias[14] = 0.0
    steps = int(round(cfg.duration / cfg.control_dt)); path = 0.0; last = sim.center_of_mass(0)[:2].copy(); p0 = last.copy()
    arrive = None; hold = 0
    for t in range(steps):
        sim.step()
        p = sim.center_of_mass(0)[:2]
        if t % 5 == 0: path += float(np.linalg.norm(p - last)); last = p.copy()
        d = sim.distance_from_center(0)
        if d < cfg.target_radius:
            if arrive is None: arrive = sim.time
            hold += 1
    disp = float(np.linalg.norm(sim.center_of_mass(0)[:2] - p0))
    return {"progress": float(sim.progress(0)) * float(sim.start_distances[0]), "tat": float(sim.time_at_target(0)), "path": path, "straight": disp / max(path, 1e-6), "arrive": arrive if arrive is not None else float("nan"), "hold_after": hold / max(1, steps - int(round(arrive / cfg.control_dt))) if arrive is not None else 0.0, "work": float(sim.work[0]) / 1000}
modes = ["intact", "no_global", "no_global+bias14", "no_global+bias14=0", "lesion:11", "lesion:15", "lesion:12", "lesion:22", "lesion:27", "lesion:29", "lesion:31", "lesion:23+24", "lesion:0", "lesion:10", "lesion:21"]
seeds = list(range(8000, 8000 + n))
print(f"{'mode':22s} progress  tat   path  straight arrive hold_after work")
for m in modes:
    rs = [trial(s, m) for s in seeds]
    mean = lambda k: float(np.nanmean([r[k] for r in rs]))
    print(f"{m:22s} {mean('progress'):+.2f}  {mean('tat'):.2f}  {mean('path'):5.1f}  {mean('straight'):.2f}   {mean('arrive'):5.1f}  {mean('hold_after'):.2f}   {mean('work'):.1f}", flush=True)
