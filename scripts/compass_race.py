"""Does steering gain accumulate faster than the sign it must match inverts?

The single-mutation comparison (scripts/compass_vs_flip.py) is not the whole
argument: a compass accumulates over many mutations, so a zero acquisition rate
in one step is expected and proves little on its own. This runs the race.

Independent mutation chains from one parent, each step the run's own
mutate_controller with the run's own MutationConfig. At every step the
structural steering gain |a| is recorded (free, no simulation). Every
`dir_every` steps the direction of travel is measured (one bout set), so the
number of sign inversions along each chain is counted on the same timeline.

The hypothesis predicts: |a| stays far below the useful magnitude (~16) while
direction inverts repeatedly, so no chain ever holds a useful gain and a
consistent sign at the same time.

It is falsified if |a| climbs to useful magnitudes within a few inversion
intervals - that would mean a compass can be built faster than its sign decays.

Usage: python scripts/compass_race.py [chains] [steps] [procs]
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
PARENT = int(__import__("os").environ.get("RACE_PARENT", 590))
SEEDS = 4
DEPTH = 4
DIR_EVERY = 8


def mutation_config():
    import dataclasses
    names = {f.name for f in dataclasses.fields(MutationConfig)}
    vals = {k: v for k, v in MUT.items() if k in names}
    if isinstance(vals.get("vocab"), dict):
        vals["vocab"] = BrainVocabulary.from_dict(vals["vocab"])
    return dataclasses.replace(MutationConfig(), **vals)


def steering_gain(ph):
    n = len(ph.units)
    nose, eff = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "food":
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "effector":
            eff[u.part] = i
    if len(nose) != 2 or len(eff) != 2:
        return 0.0
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
    return float((s1 - s2) / 2.0)


def wrap(a):
    return float((a + np.pi) % (2 * np.pi) - np.pi)


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
    if not T:
        return None
    return float(np.degrees(np.arctan2(np.mean(np.sin(T)), np.mean(np.cos(T)))))


def chain(task):
    cid, steps = task
    mc = mutation_config()
    g = Genotype.load(f"{RUN}/conventional/best_gen{PARENT:04d}.json")
    rng = np.random.default_rng([7, cid])
    gains, dirs = [], []
    for s in range(steps):
        g = mutate_controller(copy.deepcopy(g), rng, mc)
        gains.append(abs(steering_gain(synthesize(g, cfg.synthesis))))
        if (s + 1) % DIR_EVERY == 0:
            m = direction_of(g)
            dirs.append(None if m is None else ("BACK" if abs(m) > 90 else "fwd"))
    return cid, gains, dirs


if __name__ == "__main__":
    nchains = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    p0 = Genotype.load(f"{RUN}/conventional/best_gen{PARENT:04d}.json")
    d0 = direction_of(p0)
    f0 = "BACK" if abs(d0) > 90 else "fwd"
    with Pool(procs) as p:
        rows = p.map(chain, [(i, steps) for i in range(nchains)])

    print(f"Compass race: {nchains} independent mutation chains x {steps} steps "
          f"from gen {PARENT} ({f0}, |a|={abs(steering_gain(synthesize(p0,cfg.synthesis))):.2f})")
    print(f"direction sampled every {DIR_EVERY} steps\n")
    print("| chain | max abs a | final abs a | direction samples | inversions |")
    print("|---|---|---|---|---|")
    allmax, allinv = [], []
    for cid, gains, dirs in rows:
        seq = [f0] + [d for d in dirs if d]
        inv = sum(1 for i in range(1, len(seq)) if seq[i] != seq[i - 1])
        allmax.append(max(gains)); allinv.append(inv)
        print(f"| {cid} | {max(gains):.2f} | {gains[-1]:.2f} | "
              f"{'->'.join(seq)} | {inv} |")
    print(f"\nmax |a| reached by any chain in {steps} mutations: {max(allmax):.2f}")
    print(f"median max |a|: {np.median(allmax):.2f}")
    print(f"useful magnitudes: |a|>=16 measurable, |a|>=32 is the +0.897 circuit")
    reached = sum(1 for m in allmax if m >= 16)
    print(f"chains reaching |a|>=16: {reached}/{nchains}")
    print(f"mean inversions per chain over {steps} mutations: {np.mean(allinv):.2f}")
    print(f"\nVERDICT: ", end="")
    if reached == 0:
        print(f"no chain built a useful compass in {steps} mutations, while direction")
        print(f"inverted {np.mean(allinv):.1f} times on average. The sign a compass must match")
        print("decays faster than the gain accumulates - RBT-77's mechanism holds.")
    else:
        print(f"{reached} chain(s) reached useful gain; compare against inversions before")
        print("concluding. RBT-77 may not hold.")
