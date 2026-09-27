"""RBT-126: what scripts/regime.py reads on the replica (breeding_rules.py, committed shuffle rule), across resident
gross income g0, so a committed run's saturation figure can be placed on the adversary's band (ADVERSARY 1d:
saturated for g0 >~ 0.8).  Window 150-449 of 600 seasons; 4 replica seeds per g0, mean (min-max).

python3 runs/RBT-126/calibrate.py [TMPDIR]"""
import importlib.util, pathlib, sys, tempfile
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
br = _load("breeding_rules", HERE / "breeding_rules.py")
rg = _load("regime", HERE.parents[1] / "scripts" / "regime.py")
tmp = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp())
keys = ("saturation", "viability", "solvent_share", "eligible_breeders", "median_energy", "q5_over_q4_children", "generations_per_season")
print("# g0 | saturation, window-local (eligible net / cost) | saturation, per life (solvent net / cost) | viability (net per birth / cost) | solvent share | age-death share | eligible breeders | median energy | Q5/Q4 children | gen/season")
for g0 in br.G0S:
    got = []
    for seed in range(4):
        d = tmp / f"g{g0}-s{seed}"
        br.write_lineage(str(d), g0, seasons=600, seed=100 + seed)
        ws = rg.regime(str(d), windows=((150, 449),))["fauna"].get("replica") or []
        if not ws:
            continue  # extinct before the window
        w = ws[0]
        w["age_death"] = w["death_share"]["age"]
        got.append(w)
    if not got:
        print(f"g0 {g0:4.2f} | extinct before season 150 on every seed"); continue
    def f(k):
        v = [x.get(k) for x in got if x.get(k) is not None]
        return f"{np.mean(v):.2f} ({min(v):.2f}-{max(v):.2f})" if v else "-"
    print(f"g0 {g0:4.2f} | " + " | ".join(f(k) for k in ("saturation_local", "saturation", "viability", "solvent_share", "age_death", "eligible_breeders", "median_energy", "q5_over_q4_children", "generations_per_season")), flush=True)
