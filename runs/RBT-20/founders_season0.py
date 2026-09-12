"""Diagnostic, not part of the arm: rebuild the run's 120 founders (seed 801, same rng sequence as the ecology) and
replay season 0 exactly (same terrain seed, start seed and groups) with starvation switched off so that the dead
founders' gains are visible too; then the same season with 15 s bouts, the baseline's season length, for comparison."""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.ecology import Ecology, EcologyConfig
run = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-20/W3b-801"
d = json.load(open(f"{run}/config.json")); eco_d = d.pop("ecology")
evo = EvolutionConfig.from_dict(d)

def season0(duration):
    e = replace(evo, sim=replace(evo.sim, duration=duration), workers=3)
    eco = EcologyConfig(**eco_d); eco.starvation = False
    E = Ecology(e, eco, out_dir=None, log=None)
    E.step(); E.runner.close()
    return {kind: {m.name: m.record["last_score"] for m in members if m.record["evals"] == 1} for kind, members in E.populations.items()}

g60, g15 = season0(60.0), season0(15.0)
for kind in ("holistic", "conventional"):
    names = sorted(set(g60[kind]) & set(g15[kind]))
    a, b = np.array([g60[kind][n] for n in names]), np.array([g15[kind][n] for n in names])
    print(f"{kind:12s} founders {len(names)} (those dying of age in season 0 excluded)")
    print(f"   60 s season: gain mean {a.mean():+.2f} median {np.median(a):+.2f} min {a.min():+.2f} max {a.max():+.2f}", end="")
    print(f"  starve in season 0 (3 + gain - 1.0 <= 0): {int((a <= -2.0).sum())}  breed after season 0 (>= 3): {int((3 + a - 1.0 >= 3).sum())}")
    print(f"   15 s season: gain mean {b.mean():+.2f} median {np.median(b):+.2f} min {b.min():+.2f} max {b.max():+.2f}  starve in season 0 (3 + gain - 0.25 <= 0): {int((b <= -2.75).sum())}  breed after season 0: {int((3 + b - 0.25 >= 3).sum())}")
    print(f"   ratio of population mean gain, 60 s / 15 s: {a.mean() / b.mean() if abs(b.mean()) > 1e-9 else float('nan'):.2f} (4.0 if a long season were four short ones); per-founder r(gain60, gain15) = {np.corrcoef(a, b)[0, 1]:.2f}")
    print(f"   net of basal: mean 60 s gain - 1.0 = {a.mean() - 1.0:+.2f}; 4 x (mean 15 s gain - 0.25) = {4 * (b.mean() - 0.25):+.2f}")
