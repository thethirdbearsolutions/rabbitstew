"""RBT-77's decisive comparison, on one denominator.

The hypothesis is that a compass cannot accumulate because the sign it must
match inverts faster than the search reaches it. That is a claim about two
rates, and it is only meaningful if both are measured per the SAME event.

So: apply the run's own mutate_controller with the run's own MutationConfig to
the same parents, and for every offspring measure BOTH

  - does it flip the direction of travel (sign the compass must match), and
  - does it acquire a gradient coefficient |a| at or above a useful magnitude,
    with the sign that is chemotactic for its OWN direction of travel.

Same operator, same config, same parents, same denominator. If acquisition is
far rarer than inversion, the mechanism is demonstrated. If it is not, RBT-77
dies.

|a| is the signed, unclamped path sum from the two noses onto the steering axis
(e1 + e2), decomposed as a*(n1-n2) + c*(n1+n2). `a` steers, `c` is the
common-mode pirouette term. Lifted from runs/RBT-45/motif.py, which was itself
corrected for a factor of two by the RBT-8 delegate.

Usage: python scripts/compass_vs_flip.py [offspring_per_parent] [procs]
"""
import copy, json, sys, numpy as np
from dataclasses import replace
from multiprocessing import Pool
from rabbitstew.genotype import Genotype, BrainVocabulary
from rabbitstew.genetics import mutate_controller, MutationConfig
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN = "runs/RBT-23/W4b-801"
raw = json.load(open(f"{RUN}/config.json"))
cfg = SimConfig.from_dict(raw["sim"])
MUT = raw["mutation"]
PARENTS = [140, 200, 300, 400, 500, 590]
SEEDS = 5
DEPTH = 4
THRESHOLDS = (8.0, 16.0, 32.0)


def mutation_config():
    import dataclasses
    names = {f.name for f in dataclasses.fields(MutationConfig)}
    vals = {k: v for k, v in MUT.items() if k in names}
    if isinstance(vals.get("vocab"), dict):
        vals["vocab"] = BrainVocabulary.from_dict(vals["vocab"])
    return dataclasses.replace(MutationConfig(), **vals)


def steering_gain(ph):
    """Signed coefficient on (n1 - n2) arriving at the steering axis e1 + e2."""
    n = len(ph.units)
    nose, eff = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "food":
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "effector":
            eff[u.part] = i
    if len(nose) != 2 or len(eff) != 2:
        return None, None
    M = np.zeros((n, n))
    for s, d, w in ph.links:
        M[d, s] += w
    out = {}
    for part, si in nose.items():
        v = np.zeros(n); v[si] = 1.0
        tot = np.zeros(n)
        for _ in range(DEPTH):
            v = M @ v
            tot += v
            if not v.any():
                break
        out[part] = tot
    s1 = out[1][eff[1]] + out[1][eff[2]]
    s2 = out[2][eff[1]] + out[2][eff[2]]
    return float((s1 - s2) / 2.0), float((s1 + s2) / 2.0)


def wrap(a):
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def circ(v):
    return float(np.degrees(np.arctan2(np.mean(np.sin(v)), np.mean(np.cos(v)))))


def direction_of(g):
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
    return (circ(T) if T else None)


def child(task):
    gen, k = task
    p = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    c = mutate_controller(copy.deepcopy(p), np.random.default_rng([gen, k]), mutation_config())
    m = direction_of(c)
    a, cm = steering_gain(synthesize(c, cfg.synthesis))
    return gen, k, m, a, cm


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    par = {}
    for gen in PARENTS:
        g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
        m = direction_of(g)
        a, cm = steering_gain(synthesize(g, cfg.synthesis))
        par[gen] = ("BACK" if abs(m) > 90 else "fwd", m, a)
    tasks = [(gen, k) for gen in PARENTS for k in range(n)]
    with Pool(procs) as p:
        rows = p.map(child, tasks)

    print("P(flip direction) vs P(acquire compass), per mutation event, same denominator")
    print(f"{RUN}, {len(PARENTS)} parents x {n} offspring\n")
    print("| parent | dir | parent |a| | flip rate | " +
          " | ".join(f"P(|a|>={t:g})" for t in THRESHOLDS) + " |")
    print("|---|---|---|---|" + "---|" * len(THRESHOLDS))
    flips, acq = [], {t: [] for t in THRESHOLDS}
    for gen in PARENTS:
        sub = [r for r in rows if r[0] == gen and r[2] is not None]
        pf = par[gen][0]
        fl = sum(1 for _, _, m, _, _ in sub if ("BACK" if abs(m) > 90 else "fwd") != pf) / len(sub)
        flips.append(fl)
        cells = []
        for t in THRESHOLDS:
            hit = sum(1 for _, _, m, a, _ in sub if a is not None and abs(a) >= t)
            acq[t].append(hit / len(sub))
            cells.append(f"{hit}/{len(sub)}")
        pa = par[gen][2]
        print(f"| {gen} | {pf} | {abs(pa):.2f} | **{fl:.2f}** | " + " | ".join(cells) + " |")
    rng = np.random.default_rng(5)
    def ci(v):
        bs = np.array([rng.choice(v, len(v)).mean() for _ in range(20000)])
        return np.mean(v), np.percentile(bs, 2.5), np.percentile(bs, 97.5)
    m, lo, hi = ci(flips)
    print(f"\npooled P(flip direction)     {m:.4f}  [{lo:.4f}, {hi:.4f}]")
    for t in THRESHOLDS:
        m2, lo2, hi2 = ci(acq[t])
        print(f"pooled P(|a| >= {t:>4g})        {m2:.4f}  [{lo2:.4f}, {hi2:.4f}]"
              + (f"   ratio flip/acquire = {m/m2:.1f}x" if m2 > 0 else "   (zero acquisitions)"))
    allа = [r[3] for r in rows if r[3] is not None]
    print(f"\noffspring |a| distribution: median {np.median(np.abs(allа)):.3f}, "
          f"p95 {np.percentile(np.abs(allа),95):.3f}, max {np.max(np.abs(allа)):.3f}")
