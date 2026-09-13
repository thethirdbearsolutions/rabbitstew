"""Is DIRECTION canalising, or is everything?

scripts/direction_canalisation.py finds offspring heading deviating less from
the parent as generations pass. That is consistent with direction being
canalised - but also with plain mutational robustness, which evolved genomes
are known to accumulate across the board. If every phenotype becomes less
mutation-sensitive at the same rate, direction is not special and there is no
story about protecting sensorimotor wiring.

This measures, on the SAME offspring (identical rng streams, so the identical
genotypes), the parent-to-offspring deviation in three phenotypes:

  heading    circular deviation of travel direction        (the trait in question)
  path       |log ratio| of distance travelled             (control)
  yaw        |log ratio| of mean absolute yaw rate         (control)

Log ratios because these are positive scale quantities; deviation is symmetric
in the ratio and not dominated by the parent's magnitude.

Read: if heading's decline with generation is steeper than the controls', the
trait is specifically canalised. If all three decline together, this is generic
mutational robustness and the direction story dissolves.

Usage: python scripts/canalisation_control.py [offspring] [procs]
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
PARENTS = list(range(10, 600, 20))
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


def phenotype(g):
    """(heading, path length, mean |yaw rate|) averaged over seeds."""
    T, paths, yaws = [], [], []
    for seed in range(9000, 9000 + SEEDS):
        c = replace(cfg, random_start=True)
        sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
        sim.set_food_seed(seed)
        idx = sim.robots[0]
        last = sim.data.xpos[idx.root_body][:2].copy()
        prev = None
        path = 0.0
        Y = []
        for _ in range(int(round(c.duration / c.control_dt))):
            sim.step()
            if sim.exploded[0]:
                break
            q = sim.data.xquat[idx.root_body]
            yaw = float(np.arctan2(2 * (q[0] * q[3] + q[1] * q[2]),
                                   1 - 2 * (q[2] ** 2 + q[3] ** 2)))
            pos = sim.data.xpos[idx.root_body][:2]
            d = pos - last
            step = float(np.linalg.norm(d))
            path += step
            if step > 1e-3:
                T.append(wrap(float(np.arctan2(d[1], d[0])) - yaw))
            if prev is not None:
                Y.append(abs(wrap(yaw - prev)) / c.control_dt)
            prev = yaw
            last = pos.copy()
        paths.append(path)
        yaws.append(float(np.mean(Y)) if Y else 0.0)
    if not T:
        return None, float(np.mean(paths)), float(np.mean(yaws))
    s, c_ = np.mean(np.sin(T)), np.mean(np.cos(T))
    return float(np.arctan2(s, c_)), float(np.mean(paths)), float(np.mean(yaws))


def child(task):
    gen, k = task
    p = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    # same seed stream as direction_canalisation.py -> the identical offspring
    c = mutate_controller(copy.deepcopy(p), np.random.default_rng([11, gen, k]), mutation_config())
    return (gen, k) + phenotype(c)


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx -= rx.mean(); ry -= ry.mean()
    d = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / d) if d else float("nan")


def perm_p(x, y, n=50000, seed=3):
    rng = np.random.default_rng(seed)
    obs = spearman(x, y)
    yy = np.asarray(y, float).copy()
    cnt = 0
    for _ in range(n):
        rng.shuffle(yy)
        if abs(spearman(x, yy)) >= abs(obs):
            cnt += 1
    return obs, (cnt + 1) / (n + 1)


def lr(a, b):
    if a is None or b is None or a <= 1e-9 or b <= 1e-9:
        return None
    return abs(float(np.log(a / b)))


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    par = {g: phenotype(Genotype.load(f"{RUN}/conventional/best_gen{g:04d}.json"))
           for g in PARENTS}
    with Pool(procs) as p:
        rows = p.map(child, [(g, k) for g in PARENTS for k in range(n)])

    print(f"Direction-specific canalisation vs generic mutational robustness")
    print(f"{RUN}, {len(PARENTS)} parents x {n} offspring, {SEEDS} seeds\n")
    print("| gen | heading dev (deg) | path dev (|log ratio|) | yaw dev (|log ratio|) |")
    print("|---|---|---|---|")
    gens, hd, pd, yd = [], [], [], []
    for g in PARENTS:
        pm, pp, py = par[g]
        sub = [r for r in rows if r[0] == g]
        H = [abs(np.degrees(wrap(r[2] - pm))) for r in sub if r[2] is not None and pm is not None]
        P = [v for v in (lr(r[3], pp) for r in sub) if v is not None]
        Y = [v for v in (lr(r[4], py) for r in sub) if v is not None]
        if not (H and P and Y):
            continue
        gens.append(g); hd.append(np.mean(H)); pd.append(np.mean(P)); yd.append(np.mean(Y))
        print(f"| {g} | {np.mean(H):.1f} | {np.mean(P):.3f} | {np.mean(Y):.3f} |")

    print(f"\nSpearman vs generation across {len(gens)} parents (permutation p):")
    for label, v in (("heading", hd), ("path (control)", pd), ("yaw (control)", yd)):
        r, p_ = perm_p(gens, v)
        print(f"  {label:16s} rho={r:+.3f}  p={p_:.4f}")
    print("\nIf heading declines and the controls do not, direction is specifically")
    print("canalised. If all three decline, this is generic mutational robustness.")
