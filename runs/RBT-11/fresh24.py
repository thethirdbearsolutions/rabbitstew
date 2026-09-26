"""Tighter fresh-draw estimate for the candidate bests: 24 draws the run never saw (seeds 7000-7023),
disjoint from eval_fresh.py's 5000-5011 and situated.py's 6000-6007.  Per-draw tat listed."""
import json, numpy as np
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, run_solo
RUN = "runs/RBT-11/sims-901"
cfg = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
seeds = list(range(7000, 7024))
out = {}
for kind, gen in (("holistic", 149), ("holistic", 140), ("holistic", 120), ("holistic", 90), ("conventional", 149)):
    g = Genotype.load(f"{RUN}/{kind}/best_gen{gen:04d}.json")
    rs = [run_solo(g, cfg, s) for s in seeds]
    tats = [r["time_at_target"] for r in rs]
    out[f"{kind}/{gen}"] = {"score": float(np.mean([r["score"] for r in rs])), "tat": float(np.mean(tats)), "tat_sd": float(np.std(tats)), "progress": float(np.mean([r["progress"] for r in rs])), "tat_per_draw": [round(float(t), 2) for t in tats]}
    o = out[f"{kind}/{gen}"]
    print(f"{kind} g{gen}: score {o['score']:.2f} tat {o['tat']:.2f} (sd {o['tat_sd']:.2f}) progress {o['progress']:+.2f}  draws>=0.5: {sum(1 for t in tats if t >= 0.5)}/24  zero: {sum(1 for t in tats if t == 0)}/24", flush=True)
json.dump(out, open("runs/RBT-11/fresh24.json", "w"), indent=1)
