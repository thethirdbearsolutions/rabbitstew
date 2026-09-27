"""RBT-120 design adversary: how large are the clamp-only changes?  For RBT-113's O founders (seeds given), one 15 s
flat solo season off and under the registered budget; for founders WITHIN the cap that carry a servo, the season's
work (yield units, 0.03 per kJ) and score off vs on."""
import os, sys
from dataclasses import replace
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import world as W120
import rabbitstew.world as rw
from rabbitstew.evolution import initial_population, spawn_streams, generation_sim
from rabbitstew.simulation import run_group
from rabbitstew.synthesis import synthesize

rows = []
for seed in [int(s) for s in sys.argv[1:]]:
    cfg = W120.evolution_config("D", seed=seed)
    pop = initial_population("holistic", cfg, spawn_streams(cfg.seed, cfg.holistic_stream_salt)["holistic"])
    base = generation_sim(cfg, 1131, 0)
    off = replace(base, world=replace(base.world, motor_budget=0.0))
    on = replace(base, world=replace(base.world, motor_budget=W120.MOTOR_BUDGET))
    for g in pop.members:
        ph = synthesize(g, base.synthesis)
        if rw.motor_scale(ph, on.world) < 1.0:
            continue
        if not any(ph.parts[i].motor in ("position", "velocity") for i, _ in rw.driven_dofs(ph) if ph.parts[i].joint_type != rw.JointType.BALL):
            continue
        a, b = run_group([g], off, 2131)[0], run_group([g], on, 2131)[0]
        rows.append((a["work"] * 0.03 / 1000, b["work"] * 0.03 / 1000, a["score"], b["score"]))
r = np.array(rows)
d = r[:, 1] - r[:, 0]
print(f"# within-cap servo founders, seeds {sys.argv[1:]}, draw (1131, 2131): n = {len(r)}")
print(f"  work off {r[:,0].mean():.4f}  on {r[:,1].mean():.4f} yield; per-founder |d work| mean {np.abs(d).mean():.4f}, max {np.abs(d).max():.4f}; "
      f"work falls in {np.mean(d < -1e-9):.0%}, rises in {np.mean(d > 1e-9):.0%}")
ds = r[:, 3] - r[:, 2]
print(f"  score off {r[:,2].mean():+.4f}  on {r[:,3].mean():+.4f}; |d score| mean {np.abs(ds).mean():.4f}, max {np.abs(ds).max():.4f}; "
      f"changed in {np.mean(np.abs(ds) > 1e-12):.0%}")
