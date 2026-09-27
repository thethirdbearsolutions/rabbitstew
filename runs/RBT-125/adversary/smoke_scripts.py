"""RBT-125 adversary: smoke test of the gate scripts' non-data paths (imports, configs, one season per condition)."""
import os, sys, json
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "runs/RBT-125/gate"))
for mod in ("prize_readout",):
    try:
        __import__(mod); print(f"import {mod}: ok")
    except Exception as e:
        print(f"import {mod}: FAILS -- {type(e).__name__}: {e}")
import side_effects as se
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, generation_sim, initial_population, spawn_streams
evo = se.rbt113.evolution_config("U", "", seed=1)
streams = spawn_streams(1)
f = {k: initial_population(k, evo, streams[k]).members for k in (HOLISTIC, CONVENTIONAL)}
print("founders", {k: len(v) for k, v in f.items()})
for c in se.CONDS_FOUNDERS:
    cfg = se.cond_cfg(c)
    fd = cfg.food
    for k in f:
        m = f[k][0]; gd = m.genotype.to_dict() if hasattr(m, "genotype") else m.to_dict()
        r = se.season(((c, k, 0), gd, cfg, 126000))
    print(f"{c:18s} G={fd.smell_contrast:g} tau={fd.smell_tau:g} eat_from={fd.eat_from} eat_rule={fd.eat_rule} clear_from={fd.clear_from} smell={fd.smell} decay={fd.decay:g} patches={fd.patches} last={r[1:]}")
base = generation_sim(evo, 1131)
for L in (0.45, 6.46):
    aa = (L / 0.3) ** 1.5
    for nose in (False, True):
        c = "U-G0/sensor" if nose else "PW-G2.5/root"
        r = se.season(((L, c, nose), se.rod(aa, nose).to_dict(), se.cond_cfg(c, base), 2131))
        print("tumbler", L, c, nose, r[1:])
