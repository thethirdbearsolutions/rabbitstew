"""Fresh-draw solo evaluation of every 10th generation's best: removes the winner's curse of the training draws."""
import json, os, sys, numpy as np
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, run_solo
run = sys.argv[1]; every = int(sys.argv[2]) if len(sys.argv) > 2 else 10; n = int(sys.argv[3]) if len(sys.argv) > 3 else 12
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
seeds = list(range(5000, 5000 + n))
out = {}
for kind in ("holistic", "conventional"):
    files = sorted(f for f in os.listdir(f"{run}/{kind}") if f.startswith("best_gen"))
    rows = []
    for f in files:
        gen = int(f[8:12])
        if gen % every and f != files[-1]:
            continue
        g = Genotype.load(f"{run}/{kind}/{f}")
        rs = [run_solo(g, cfg, s) for s in seeds]
        rows.append({"gen": gen, "score": float(np.mean([r["score"] for r in rs])), "tat": float(np.mean([r["time_at_target"] for r in rs])), "progress": float(np.mean([r["progress"] for r in rs])), "waypoints": float(np.mean([r.get("waypoints", 0) for r in rs]))})
    out[kind] = rows
    print(kind, " ".join(f"g{r['gen']}:{r['score']:.2f}" for r in rows))
json.dump(out, open(f"{run}/fresh_eval.json", "w"))
