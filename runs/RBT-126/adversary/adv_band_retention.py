"""RBT-126 adversary, probe 1: does REGIME.md's band say whether selection *could* hold a trait?

The bands are calibrated on a homogeneous invasion replica (6 mutants among 60).  The selection-dependent headlines
of RBT-80, RBT-106 and RBT-112 are *retention* designs: every founder carries the trait, the operator erodes it,
and the question is whether selection holds it above a floor.  Here the PR's own replica
(runs/RBT-126/breeding_rules.py, committed shuffle rule) is run as a retention design, its lineage is read by the
PR's own scripts/regime.py, and the band it would be given is printed beside the carriage it actually retained.

Design: 60 founders all carriers with gross income gc; each birth erodes a carrier's child to a non-carrier with
probability u = 0.06; non-carriers earn gross gn = f * gc.  Carriage is read at season 300 (floor = the same run
with f = 1, no edge).  regime.py reads window 150-299.  Cells: gc in {1.05 (RBT-80), 1.1 (HU-like ratio ~3),
1.3 (HZ/P1-like ~3.8), 3.0 (HP-like ~10.7)}, f in {0.1, 0.45, 0.6, 0.8, 1.0}.

python3 runs/RBT-126/adversary/adv_band_retention.py [reps] > runs/RBT-126/adversary/adv_band_retention.txt
"""
import importlib.util, pathlib, sys, tempfile, json, os
from multiprocessing import Pool
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


br = _load("breeding_rules", ROOT / "runs/RBT-126/breeding_rules.py")
rg = _load("regime", ROOT / "scripts/regime.py")
U, SEASONS = 0.06, 300


def one(args):
    gc, f, seed, read_band = args
    rng = np.random.default_rng(seed)
    log = [] if read_band else None
    out = br.run(rng, g_of=lambda t: gc if t else gc * f, n_mut=br.CAP, seasons=SEASONS, u=U, log=log)
    res = {"carriage": out["share"]}
    if read_band:
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "lineage.jsonl"), "w") as fh:
            for r in log:
                fh.write(json.dumps(r) + "\n")
        with open(os.path.join(d, "config.json"), "w") as fh:
            json.dump({"ecology": {"living_cost": br.COST, "birth_threshold": br.THR, "birth_cost": br.BCOST,
                                   "max_age": br.AGE, "initial_energy": br.INIT, "starvation": True}}, fh)
        w = rg.regime(d, windows=((150, 299),))["fauna"]["replica"][0]
        res.update(sat=w.get("saturation_local"), viab=w.get("viability"), elig=w.get("eligible_breeders"),
                   q54=w.get("q5_over_q4_children"), starve=w["death_share"]["starvation"])
    return res


def band(x, elig):
    if elig is None or elig < 10:
        return "few"
    return "saturated" if x >= 1.9 else ("transition" if x >= 1.2 else "selecting")


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    GC = (1.05, 1.1, 1.3, 3.0)
    FS = (0.1, 0.45, 0.6, 0.8, 1.0)
    print(f"# retention replica (shuffle), u {U}, {SEASONS} seasons, {reps} reps a cell (carriage), 8 of them read by regime.py (band, window 150-299)")
    print("# gc | f (gn = f*gc) | carriage ± SE | floor (f=1) | carriage - floor | regime.py window-local saturation [min,max] -> band | viability | starvation share of deaths | Q5/Q4")
    with Pool(4) as pool:
        for gc in GC:
            floor = None
            rows = {}
            for f in FS:
                cells = [(gc, f, 10_000 + int(gc * 100) * 100 + int(f * 100) * 7 + i, i < 8) for i in range(reps)]
                rows[f] = pool.map(one, cells)
            fl = np.array([r["carriage"] for r in rows[1.0]])
            for f in FS:
                rs = rows[f]
                c = np.array([r["carriage"] for r in rs])
                banded = [r for r in rs if "sat" in r and r["sat"] is not None]
                sats = [r["sat"] for r in banded]
                el = np.mean([r["elig"] for r in banded])
                vi = np.mean([r["viab"] for r in banded])
                st = np.mean([r["starve"] for r in banded if r["starve"] is not None])
                q = [r["q54"] for r in banded if r["q54"] is not None]
                print(f"gc {gc:4.2f} | f {f:4.2f} (gn {gc*f:4.2f}) | {c.mean():.3f}±{c.std()/np.sqrt(len(c)):.3f} | {fl.mean():.3f} | "
                      f"{c.mean()-fl.mean():+.3f} | {np.median(sats):.2f} [{min(sats):.2f},{max(sats):.2f}] -> {band(np.median(sats), el)} "
                      f"| {vi:+.2f} | {st:.2f} | {np.median(q) if q else float('nan'):.2f}", flush=True)
