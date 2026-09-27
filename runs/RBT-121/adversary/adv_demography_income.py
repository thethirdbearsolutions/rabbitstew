"""RBT-121 adversary: the committed lottery at paper 10's incomes (HU ~1.3-1.5, HP ~ HU + 1.77) and between.
Uses adv_demography.run (the independent replica).  python3 adv_demography_income.py [reps]"""
import sys
import numpy as np
from adv_demography import run
reps = int(sys.argv[1]) if len(sys.argv) > 1 else 100
rng = np.random.default_rng(10)
print(f"# committed lottery, cost 0.25, 60 slots, 400 seasons, 6 mutants; reps {reps}; mean mutant share / fixation rate at season 400")
for g0 in (0.3, 0.4, 0.6, 0.8, 1.5, 3.0):
    for mult in (1.25, 2.0):
        fr = np.array([run(rng, g_of=lambda t, g0=g0, m=mult: g0 * (m if t else 1.0), n_mut=6, seasons=400)[0] for _ in range(reps)])
        print(f"g0 {g0:4.2f} x{mult:4.2f}: share {fr.mean():.3f} fix {np.mean(fr == 1.0):.2f}", flush=True)
