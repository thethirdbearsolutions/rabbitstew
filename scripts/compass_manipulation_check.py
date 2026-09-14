"""Manipulation check: does the antisymmetric motif actually steer toward food?

RBT-76 mechanism 2, and its worked example. Every measurement of the compass so
far has been a *yield* measurement - items eaten, against a baseline, over
thousands of bouts. Yield is many-to-one over the thing the question turns on: a
circuit that steers toward food, one that steers away, and one that does nothing
can all return a small negative delta, for entirely different reasons.

This asks the prior question directly, and cheaply: with the circuit installed,
does the robot turn *toward* the nearest live item? If the answer is no, no
amount of yield measurement means anything, and 14,336 bouts of it mean nothing
very precisely.

Conditions:
  base      nothing installed
  motif     W[e1,n1]=W[e2,n1]=+w, W[e1,n2]=W[e2,n2]=-w  (RBT-64's antisymmetric motif)
  antimotif the same with the sign flipped - included because which physical side
            part 1 sits on decides whether `motif` is a compass or an anti-compass,
            and nothing in the source ever checked
  common    W[e1,n1]=W[e2,n1]=W[e1,n2]=W[e2,n2]=+w - the RBT-61 error, expected to
            pirouette; it is the positive control for the instrument detecting a
            gross steering effect at all

Reported per condition:
  turn_toward  mean over control ticks of sign(bearing) * yaw_rate, rad/s.
               > 0 is chemotaxis, < 0 is negative chemotaxis, ~0 is no steering.
  frac_toward  fraction of ticks turning the correct way. 0.5 is chance.
  mean|bearing| mean absolute bearing to the nearest live item, rad. Lower is better aimed.
  exploded     fraction of bouts that went numerically unstable. An exploded robot
               stops eating (simulation.py:463), so this silently suppresses yield
               and no yield measurement in this programme has ever reported it.

Usage: python scripts/compass_manipulation_check.py [seeds] [procs]
"""
import json, sys, numpy as np
from dataclasses import replace
from multiprocessing import Pool
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN = "docs/artifacts/RBT-23-W4b-801"
GENS = (90, 190, 290, 390, 490, 550, 590)
PARKED = 1e5  # items are parked at 1e6 when eaten; anything past this is not live
cfg = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])


def units(gen):
    ph = synthesize(Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json"), cfg.synthesis)
    nose, eff = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == 'sensor' and u.unit.source == 'food':
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == 'effector':
            eff[u.part] = i
    return nose, eff


def install(W, nose, eff, cond, w):
    if cond == 'base':
        return
    s2 = {'motif': -1.0, 'antimotif': +1.0, 'common': +1.0}[cond]
    s1 = {'motif': +1.0, 'antimotif': -1.0, 'common': +1.0}[cond]
    W[eff[1], nose[1]] += s1 * w
    W[eff[2], nose[1]] += s1 * w
    W[eff[1], nose[2]] += s2 * w
    W[eff[2], nose[2]] += s2 * w


def yaw_of(sim):
    q = sim.data.xquat[sim.robots[0].root_body]
    # yaw from a wxyz quaternion
    return float(np.arctan2(2 * (q[0] * q[3] + q[1] * q[2]),
                            1 - 2 * (q[2] ** 2 + q[3] ** 2)))


def wrap(a):
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def bout(task):
    gen, seed, cond, w = task
    c = replace(cfg, random_start=True)
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    nose, eff = units(gen)
    install(sim.brains[0].W, nose, eff, cond, w)

    prev = yaw_of(sim)
    dt = c.control_dt
    toward, absb = [], []
    start = sim.data.xpos[sim.robots[0].root_body][:2].copy()
    last = start.copy()
    path = 0.0
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
        if sim.exploded[0]:
            break
        pos = sim.data.xpos[sim.robots[0].root_body][:2]
        path += float(np.linalg.norm(pos - last)); last = pos.copy()
        live = sim.food_pos[np.max(np.abs(sim.food_pos), axis=1) < PARKED] if len(sim.food_pos) else np.zeros((0, 2))
        cur = yaw_of(sim)
        rate = wrap(cur - prev) / dt
        prev = cur
        if len(live) == 0:
            continue
        d = live - pos
        j = int(np.argmin(np.linalg.norm(d, axis=1)))
        b = wrap(float(np.arctan2(d[j, 1], d[j, 0])) - cur)
        toward.append(np.sign(b) * rate)
        absb.append(abs(b))
    net = float(np.linalg.norm(last - start))
    if not toward:
        return (gen, seed, cond, w, np.nan, np.nan, np.nan, float(sim.exploded[0]),
                float(sim.food_eaten[0]), path, net)
    return (gen, seed, cond, w,
            float(np.mean(toward)),
            float(np.mean(np.asarray(toward) > 0)),
            float(np.mean(absb)),
            float(sim.exploded[0]),
            float(sim.food_eaten[0]), path, net)


if __name__ == "__main__":
    nseeds = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    seeds = [9000 + i for i in range(nseeds)]

    conds = [('base', 0.0)]
    for w in (8.0, 16.0, 32.0):
        conds += [('motif', w), ('antimotif', w)]
    conds += [('common', 4.0)]
    if len(sys.argv) > 3:   # e.g. "base,motif:32,antimotif:32"
        want = []
        for tok in sys.argv[3].split(','):
            n, _, ww = tok.partition(':')
            want.append((n, float(ww or 0.0)))
        conds = [cw for cw in conds if cw in want]

    tasks = [(gn, s, c, w) for gn in GENS for s in seeds for c, w in conds]
    with Pool(procs) as p:
        rows = p.map(bout, tasks, chunksize=16)

    print(f"Manipulation check - {len(GENS)} robots x {nseeds} seeds x {len(conds)} conditions "
          f"= {len(rows)} bouts")
    print(f"substrate: {RUN} (12 items, no patches, no regrowth)\n")
    print("| condition | w | turn_toward rad/s | mean abs bearing | path m | net m | exploded | items |")
    print("|---|---|---|---|---|---|---|---|")
    for c, w in conds:
        sub = [r for r in rows if r[2] == c and r[3] == w]
        tt = np.nanmean([r[4] for r in sub])
        ft = np.nanmean([r[5] for r in sub])
        ab = np.nanmean([r[6] for r in sub])
        ex = np.mean([r[7] for r in sub])
        it = np.mean([r[8] for r in sub])
        # bootstrap turn_toward over robots, the unit of analysis
        per = [np.nanmean([r[4] for r in sub if r[0] == gn]) for gn in GENS]
        rng = np.random.default_rng(5)
        bs = np.array([rng.choice(per, len(per)).mean() for _ in range(20000)])
        lo, hi = np.percentile(bs, 2.5), np.percentile(bs, 97.5)
        pa = np.mean([r[9] for r in sub]); ne = np.mean([r[10] for r in sub])
        print(f"| {c} | {w:g} | {tt:+.4f} [{lo:+.4f}, {hi:+.4f}] | {ab:.3f} | {pa:.2f} | {ne:.2f} | {ex:.3f} | {it:.3f} |")
