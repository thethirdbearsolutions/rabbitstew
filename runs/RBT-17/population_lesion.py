"""How many of the final population depend on their noses?  Every individual in <kind>/final/
alone in the arena over a few seeds, intact and with both noses (food + agent sensors) blanked.
Usage: python population_lesion.py RUN [SEEDS=3] [WORKERS=4]"""
import glob, json, os, sys, numpy as np
from dataclasses import replace
from multiprocessing import Pool
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
run = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 3; workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
def one(path):
    g = Genotype.load(path); ph = synthesize(g, cfg.synthesis)
    srcs = [u.unit.source for u in ph.units if u.unit.kind == "sensor"]
    out = {"file": os.path.basename(path), "name": g.name, "noses": sum(s in ("food", "agent") for s in srcs), "agent": srcs.count("agent"), "food": srcs.count("food")}
    for mode in ("intact", "no_noses"):
        ys = []
        for s in range(n):
            c = replace(cfg, random_start=True)
            sim = Simulation([g], c, spawns=spawn_layout(1, c, 8000 + s)); sim.set_food_seed(8000 + s)
            if mode == "no_noses":
                for i, ui in enumerate(ph.units):
                    if ui.unit.kind == "sensor" and ui.unit.source in ("food", "agent"): sim.brains[0].W[:, i] = 0
            sim.run(); ys.append(float(sim.food_eaten[0]))
        out[mode] = float(np.mean(ys))
    return out
if __name__ == "__main__":
    res = {}
    for kind in ("holistic", "conventional"):
        files = sorted(glob.glob(f"{run}/{kind}/final/*.json"))
        with Pool(workers) as p: rows = p.map(one, files)
        res[kind] = rows
        with_n = [r for r in rows if r["noses"]]
        dep = [r for r in with_n if r["intact"] - r["no_noses"] >= 0.5]
        hurt = [r for r in with_n if r["no_noses"] - r["intact"] >= 0.5]
        print(f"{kind:12s} n {len(rows)}  with a nose {len(with_n)}  mean items alone intact {np.mean([r['intact'] for r in rows]):.2f} / noses blanked {np.mean([r['no_noses'] for r in rows]):.2f}"
              f"  nose-dependent (loses >= 0.5 items) {len(dep)}  nose-hindered (gains >= 0.5) {len(hurt)}  (over {n} seeds each)")
        for r in sorted(with_n, key=lambda r: r["no_noses"] - r["intact"])[:8]:
            print(f"    {r['name']:12s} food x{r['food']} agent x{r['agent']}  intact {r['intact']:.2f}  no_noses {r['no_noses']:.2f}")
    json.dump(res, open(f"{run}/../population_lesion.json", "w"), indent=1)
