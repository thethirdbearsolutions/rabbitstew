"""Is directional robustness under selection, or is 'lability' an artifact of binarising?

Six parents in scripts/direction_heritability.py gave flip rates 0.00-0.19, and
the three robust ones included the two latest generations - which suggests
lineages canalise their direction over evolutionary time, protecting any
sensorimotor wiring built on it.

There is a cheaper explanation that must be killed first. Direction is binarised
at +/-90 degrees, and a gait with low directional concentration R sits near that
boundary, so a tiny perturbation flips the MEASURED direction without the
behaviour changing much. In the six-parent run the labile parents did have lower
R (0.66, 0.73) than the robust ones (0.84, 0.82). If lability is just low R,
"robustness under selection" is an artifact of the measure.

So this records, per parent:
  R_parent       directional concentration of the parent itself
  flip_rate      binary flip rate among offspring (the suspect measure)
  mean_dev       MEAN ABSOLUTE ANGULAR DEVIATION of offspring from the parent's
                 heading, in degrees - continuous, no boundary, no binarisation

Pre-registered reads, fixed before running:
  - CANALISATION predicts mean_dev falls with generation.
  - ARTIFACT predicts flip_rate tracks R_parent (low R -> high flip rate) while
    mean_dev shows no generation trend.
  - Both can be false; report whichever.

Usage: python scripts/direction_canalisation.py [offspring] [procs]
"""
import copy, json, sys, numpy as np
from dataclasses import replace
from multiprocessing import Pool
from rabbitstew.genotype import Genotype, BrainVocabulary
from rabbitstew.genetics import mutate_controller, MutationConfig
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout

RUN = "runs/RBT-23/W4b-801"
raw = json.load(open(f"{RUN}/config.json"))
cfg = SimConfig.from_dict(raw["sim"])
MUT = raw["mutation"]
PARENTS = list(range(10, 600, 20))   # 30 parents spanning the run
SEEDS = 4


def mutation_config():
    import dataclasses
    names = {f.name for f in dataclasses.fields(MutationConfig)}
    vals = {k: v for k, v in MUT.items() if k in names}
    if isinstance(vals.get("vocab"), dict):
        vals["vocab"] = BrainVocabulary.from_dict(vals["vocab"])
    return dataclasses.replace(MutationConfig(), **vals)


def wrap(a):
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def heading(g):
    """Circular mean of (travel azimuth - body yaw), and its concentration R."""
    T = []
    for seed in range(9000, 9000 + SEEDS):
        c = replace(cfg, random_start=True)
        sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
        sim.set_food_seed(seed)
        idx = sim.robots[0]
        last = sim.data.xpos[idx.root_body][:2].copy()
        for _ in range(int(round(c.duration / c.control_dt))):
            sim.step()
            if sim.exploded[0]:
                break
            q = sim.data.xquat[idx.root_body]
            yaw = float(np.arctan2(2 * (q[0] * q[3] + q[1] * q[2]),
                                   1 - 2 * (q[2] ** 2 + q[3] ** 2)))
            pos = sim.data.xpos[idx.root_body][:2]
            d = pos - last
            if np.linalg.norm(d) > 1e-3:
                T.append(wrap(float(np.arctan2(d[1], d[0])) - yaw))
            last = pos.copy()
    if not T:
        return None, 0.0
    s, c_ = np.mean(np.sin(T)), np.mean(np.cos(T))
    return float(np.arctan2(s, c_)), float(np.hypot(s, c_))


def child(task):
    gen, k = task
    p = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    c = mutate_controller(copy.deepcopy(p), np.random.default_rng([11, gen, k]), mutation_config())
    m, R = heading(c)
    return gen, k, m, R


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx -= rx.mean(); ry -= ry.mean()
    d = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / d) if d else float("nan")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    par = {}
    for gen in PARENTS:
        m, R = heading(Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json"))
        par[gen] = (m, R)
    with Pool(procs) as p:
        rows = p.map(child, [(g, k) for g in PARENTS for k in range(n)])

    print(f"Directional canalisation vs binarisation artifact")
    print(f"{RUN}, {len(PARENTS)} parents x {n} offspring, {SEEDS} seeds each\n")
    print("| gen | parent heading | R_parent | flip rate | mean abs deviation (deg) |")
    print("|---|---|---|---|---|")
    gens, Rs, flips, devs = [], [], [], []
    for gen in PARENTS:
        pm, pR = par[gen]
        sub = [r for r in rows if r[0] == gen and r[2] is not None]
        if not sub or pm is None:
            continue
        pf = abs(np.degrees(pm)) > 90
        fl = sum(1 for _, _, m, _ in sub if (abs(np.degrees(m)) > 90) != pf) / len(sub)
        dv = float(np.mean([abs(np.degrees(wrap(m - pm))) for _, _, m, _ in sub]))
        gens.append(gen); Rs.append(pR); flips.append(fl); devs.append(dv)
        print(f"| {gen} | {np.degrees(pm):+.0f}° | {pR:.2f} | {fl:.2f} | {dv:.1f} |")

    print(f"\nSpearman correlations across {len(gens)} parents:")
    print(f"  flip rate   vs generation : {spearman(gens, flips):+.3f}")
    print(f"  mean dev    vs generation : {spearman(gens, devs):+.3f}   <- canalisation test")
    print(f"  flip rate   vs R_parent   : {spearman(Rs, flips):+.3f}   <- artifact test")
    print(f"  mean dev    vs R_parent   : {spearman(Rs, devs):+.3f}")
