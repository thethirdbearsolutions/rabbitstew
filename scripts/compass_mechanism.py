"""What is the antisymmetric motif actually doing? RBT-69 / RBT-76 follow-up.

Established so far: the motif earns +0.835 items on the evolved W4' bests while
aiming WORSE at the nearest item (1.722 -> 2.001), travelling LESS (6.16 m
against 7.26), and with a 0.0% explosion rate. So the gain is real, and it is
neither chemotaxis, nor coverage, nor numerical damage.

Two things are tested here.

A. WHICH TARGET, IF ANY, DOES IT TRACK?
   The circuit's whole input to the steering axis is 2w(n1 - n2): a finite
   difference of the smell field across the wheelbase. That field is
   squash(sum_i exp(-d_i/decay)) over ALL items, so its gradient points at the
   local centroid of the smell pile, not at the nearest item. "Bearing to
   nearest item" - the metric that produced the dissociation - may simply be
   the wrong target. So we compute the true ascent direction analytically,

       grad sum_i exp(-d_i/L) = (1/L) * sum_i exp(-d_i/L) * (x_i - p)/d_i

   (the squash is monotone, so it cannot change the direction) and report
   alignment against BOTH targets.

B. IS THE GAIN ABOUT FOOD LOCATION AT ALL?
   The decisive control: `phantom`. The motif is installed exactly as in the
   winning condition, but the food sensors smell a DECOY layout drawn from a
   different seed, while the real items stay where they are and stay edible.
   The n1 - n2 signal keeps its character - same item count, same decay, same
   spatial statistics - and loses its correlation with the food actually
   present. If +0.835 survives that, the motif is not a food-direction circuit
   in any sense; it is a gait perturbation that happens to pay.

Usage: python scripts/compass_mechanism.py [seeds] [procs]
"""
import json, sys, numpy as np
from dataclasses import replace
from multiprocessing import Pool
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN = "docs/artifacts/RBT-23-W4b-801"
GENS = (90, 190, 290, 390, 490, 550, 590)
PARKED = 1e5
W = 32.0
cfg = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
DECAY = cfg.food.decay if cfg.food is not None else 1.0


class DecoySmell(Simulation):
    """Simulation whose food sensors smell `self._decoy` instead of the real items.

    Only the food branch of sensor_values is affected: it is the one call that
    passes self.food_pos as `sources` (simulation.py:269). Eating, regrowth and
    every other sensor are untouched.
    """
    _decoy = None

    def _intensity(self, point, sources):
        if self._decoy is not None and sources is self.food_pos:
            sources = self._decoy
        return super()._intensity(point, sources)


def units(gen):
    ph = synthesize(Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json"), cfg.synthesis)
    nose, eff = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == 'sensor' and u.unit.source == 'food':
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == 'effector':
            eff[u.part] = i
    return nose, eff


def wrap(a):
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def yaw_of(sim):
    q = sim.data.xquat[sim.robots[0].root_body]
    return float(np.arctan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] ** 2 + q[3] ** 2)))


def ascent_bearing(pos, live):
    """Bearing of steepest ascent of sum_i exp(-d_i/DECAY) at `pos`."""
    d = live - pos
    r = np.linalg.norm(d, axis=1)
    ok = r > 1e-9
    if not ok.any():
        return None
    wgt = (np.exp(-r[ok] / DECAY) / r[ok])[:, None]
    g = (wgt * d[ok]).sum(axis=0)
    if np.linalg.norm(g) < 1e-12:
        return None
    return float(np.arctan2(g[1], g[0]))


def bout(task):
    gen, seed, cond = task
    c = replace(cfg, random_start=True)
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim = DecoySmell([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    if cond == 'phantom':
        # a decoy layout from a different seed: same count, same statistics,
        # decorrelated from the items actually on the ground
        probe = Simulation([g], c, spawns=spawn_layout(1, c, seed))
        probe.set_food_seed(seed + 5000)
        sim._decoy = np.array(probe.food_pos, dtype=float).reshape(-1, 2).copy()
    nose, eff = units(gen)
    Wm = sim.brains[0].W
    if cond in ('motif', 'phantom'):
        Wm[eff[1], nose[1]] += W; Wm[eff[2], nose[1]] += W
        Wm[eff[1], nose[2]] -= W; Wm[eff[2], nose[2]] -= W
    elif cond == 'antimotif':
        Wm[eff[1], nose[1]] -= W; Wm[eff[2], nose[1]] -= W
        Wm[eff[1], nose[2]] += W; Wm[eff[2], nose[2]] += W

    prev = yaw_of(sim)
    dt = c.control_dt
    b_near, b_grad, al_near, al_grad = [], [], [], []
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
        if sim.exploded[0]:
            break
        pos = sim.data.xpos[sim.robots[0].root_body][:2]
        live = sim.food_pos[np.max(np.abs(sim.food_pos), axis=1) < PARKED]
        cur = yaw_of(sim); rate = wrap(cur - prev) / dt; prev = cur
        if len(live) == 0:
            continue
        d = live - pos
        j = int(np.argmin(np.linalg.norm(d, axis=1)))
        bn = wrap(float(np.arctan2(d[j, 1], d[j, 0])) - cur)
        b_near.append(abs(bn)); al_near.append(np.sign(bn) * rate)
        ab = ascent_bearing(pos, live)
        if ab is not None:
            bg = wrap(ab - cur)
            b_grad.append(abs(bg)); al_grad.append(np.sign(bg) * rate)
    f = lambda v: float(np.mean(v)) if v else np.nan
    return (gen, seed, cond, f(b_near), f(b_grad), f(al_near), f(al_grad),
            float(sim.food_eaten[0]))


if __name__ == "__main__":
    nseeds = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    seeds = [9000 + i for i in range(nseeds)]
    conds = ['base', 'motif', 'phantom', 'antimotif']
    tasks = [(gn, s, c) for gn in GENS for s in seeds for c in conds]
    with Pool(procs) as p:
        rows = p.map(bout, tasks, chunksize=16)

    by = {(r[0], r[1], r[2]): r for r in rows}
    base = {(gn, s): by[(gn, s, 'base')][7] for gn in GENS for s in seeds}
    rng = np.random.default_rng(5)
    print(f"Mechanism probe - {len(GENS)} robots x {nseeds} seeds x {len(conds)} conditions "
          f"= {len(rows)} bouts, motif w={W:g}")
    print(f"substrate {RUN}; smell decay {DECAY}, mode {cfg.food.smell if cfg.food else 'sum'}\n")
    print("| condition | abs bearing NEAREST | abs bearing GRADIENT | align near | align grad | items | delta | 95% CI |")
    print("|---|---|---|---|---|---|---|---|")
    for c in conds:
        sub = [r for r in rows if r[2] == c]
        per = [float(np.mean([by[(gn, s, c)][7] - base[(gn, s)] for s in seeds])) for gn in GENS]
        bs = np.array([rng.choice(per, len(per)).mean() for _ in range(20000)])
        lo, hi = np.percentile(bs, 2.5), np.percentile(bs, 97.5)
        print(f"| {c} | {np.nanmean([r[3] for r in sub]):.3f} | {np.nanmean([r[4] for r in sub]):.3f} "
              f"| {np.nanmean([r[5] for r in sub]):+.4f} | {np.nanmean([r[6] for r in sub]):+.4f} "
              f"| {np.mean([r[7] for r in sub]):.3f} | {np.mean(per):+.3f} | [{lo:+.3f}, {hi:+.3f}] |")
