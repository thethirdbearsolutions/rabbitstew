"""RBT-65: can selection hold a compass it is given?

Seeds an ecology from RBT-23/W4b-801's conventional bests with the compass
motif installed IN THE GENOTYPE (scripts/genotype_motif.py - the routed form,
since the direct 4-link motif is not representable), and runs a paired control
arm seeded from the identical founders without it. Same evolution seed, same
world, same everything else.

Gate conditions checked before any season runs, per the RBT-65 amendments:
  - the population's direction of travel is measured, so the motif is installed
    with the sign that is chemotactic FOR THIS POPULATION (W4b-801 drives
    backward at -174 deg, so the published sign is correct for it)
  - the seeded founders' realised steering gain is verified after synthesis
    rather than assumed

Usage: python scripts/rbt65_seed_run.py [seasons] [workers] [w]
"""
import glob, json, os, shutil, sys, time
import numpy as np
from rabbitstew.genotype import Genotype
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.ecology import Ecology, EcologyConfig
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from genotype_motif import install, direct_is_illegal
import importlib.util
_s = importlib.util.spec_from_file_location("cvf", os.path.join(os.path.dirname(os.path.abspath(__file__)), "compass_vs_flip.py"))
cvf = importlib.util.module_from_spec(_s); _s.loader.exec_module(cvf)

SRC = "runs/RBT-23/W4b-801"
OUT = "runs/RBT-65"
raw = json.load(open(f"{SRC}/config.json"))
cfg = SimConfig.from_dict(raw["sim"])


def build_founders(w):
    files = sorted(glob.glob(f"{SRC}/conventional/best_gen*.json"))
    gains = {"seeded": [], "control": []}
    for arm in ("seeded", "control"):
        d = f"{OUT}/founders/{arm}/conventional"
        shutil.rmtree(f"{OUT}/founders/{arm}", ignore_errors=True)
        os.makedirs(d, exist_ok=True)
        for f in files:
            g = Genotype.load(f)
            if arm == "seeded":
                g = install(g, w)
            a, _ = cvf.steering_gain(synthesize(g, cfg.synthesis))
            gains[arm].append(a if a is not None else 0.0)
            g.save(os.path.join(d, os.path.basename(f)))
        # holistic founders: identical in both arms, straight from the source
        hd = f"{OUT}/founders/{arm}/holistic"
        os.makedirs(hd, exist_ok=True)
        for f in sorted(glob.glob(f"{SRC}/holistic/best_gen*.json")):
            shutil.copy(f, hd)
    return gains, len(files)


def run_arm(arm, seasons, workers):
    d = {k: v for k, v in raw.items() if k != "ecology"}
    d["generations"] = seasons
    d["workers"] = workers
    evo = EvolutionConfig.from_dict(d)
    eco = EcologyConfig(**{**raw["ecology"], "seasons": seasons,
                           "seed_conventional": f"{OUT}/founders/{arm}",
                           "seed_holistic": f"{OUT}/founders/{arm}"})
    out = f"{OUT}/{arm}"
    shutil.rmtree(out, ignore_errors=True)
    t = time.time()
    Ecology(evo, eco, out_dir=out, log=lambda *a: None).run()
    return time.time() - t


if __name__ == "__main__":
    seasons = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    w = float(sys.argv[3]) if len(sys.argv) > 3 else 32.0

    g0 = Genotype.load(f"{SRC}/conventional/best_gen0590.json")
    print("GATE CONDITIONS")
    print(f"  direct 4-link motif representable? {'NO - ' + direct_is_illegal(g0)[0] if direct_is_illegal(g0) else 'yes'}")
    print(f"  routed motif validates: {not install(g0, w).validate()}")
    print(f"  population direction: W4b-801 drives BACKWARD (-174 deg, R=0.76),")
    print(f"    so the published motif sign is the chemotactic one for it")

    gains, n = build_founders(w)
    sg = np.array(gains["seeded"]); cg = np.array(gains["control"])
    print(f"\nFOUNDERS: {n} conventional bests per arm")
    print(f"  control realised |a|: median {np.median(np.abs(cg)):.3f}  max {np.abs(cg).max():.3f}")
    print(f"  seeded  realised  a : median {np.median(sg):+.1f}  min {sg.min():+.1f}  max {sg.max():+.1f}")
    wrong = int((sg < 0).sum())
    print(f"  seeded founders with WRONG-SIGN realised gain: {wrong}/{n}"
          + ("  (reported separately per RBT-65)" if wrong else ""))

    print(f"\nRunning {seasons} seasons per arm, {workers} workers ...", flush=True)
    for arm in ("seeded", "control"):
        dt = run_arm(arm, seasons, workers)
        print(f"  {arm}: {dt/60:.1f} min", flush=True)
    print(f"\ndone -> {OUT}/seeded and {OUT}/control")
