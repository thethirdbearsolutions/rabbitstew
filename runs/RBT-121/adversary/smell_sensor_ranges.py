"""RBT-121 adversary on audit C finding 2 / the smell_gain proposal: what the SIMULATOR's food sensors actually read.

    python runs/RBT-121/adversary/smell_sensor_ranges.py /tmp/claude-0/adv_noise/O1/1 > runs/RBT-121/adversary/smell_sensor_ranges.txt

Runs real RBT-113 O1 seed-1 U-line final bodies (both faunas; RBT-113's committed world: 12 items, sum, decay 1) solo
for a few draws and wraps Simulation.sensor_values (read-only) to log every food sensor's reading and position each
tick.  Reports: how many food sensors each body has and how many sit on the root part; the reading's level and
spread; the per-tick max differential between two food sensors of one body with their separation; and what the
proposed centred contrast c_i = tanh(G (ln S_i - ln S_root)), G = 10, would read at the same points (S = the sum of
exp(-d/decay), recomputed from the food positions).  Also C's model quantity for comparison: 0.3 m nose spacing.
"""
import os
import sys

import numpy as np

sys.path.insert(0, "/home/user/rabbitstew/runs/RBT-113")
import world as W  # noqa: E402
from rabbitstew import simulation as SIM  # noqa: E402
from rabbitstew.evolution import generation_sim  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import run_group  # noqa: E402

LOG = []
_orig = SIM.Simulation.sensor_values


def logged(self, ri, touching):
    vals = _orig(self, ri, touching)
    brain, idx = self.brains[ri], self.robots[ri]
    rows = []
    for k, s in enumerate(brain.sensors):
        if s.source == "food":
            p = np.array(self.data.geom_xpos[idx.geoms[s.part]][:2])
            rows.append((s.part, p, vals[k]))
    if rows:
        root = np.array(self.data.xpos[idx.root_body][:2])
        LOG.append((rows, root, self.food_pos.copy(), self.config.food.decay))
    return vals


SIM.Simulation.sensor_values = logged


def S(p, food, decay):
    return float(np.exp(-np.linalg.norm(food - p, axis=1) / decay).sum())


def main(d):
    cfg = W.evolution_config("U", "", seed=1)
    print(f"# RBT-113 world: food {cfg.sim.food}")
    for kind in ("conventional", "holistic"):
        p = os.path.join(d, "U", kind, "final")
        fs = sorted(os.listdir(p))[:10]
        nsens, onroot, diffs, seps, levels, Ss, contr, contr_root, diffs30 = [], [], [], [], [], [], [], [], []
        for f in fs:
            g = Genotype.load(os.path.join(p, f))
            for j in range(3):
                LOG.clear()
                run_group([g], generation_sim(cfg, 8131 + j), 9131 + j)
                for t, (rows, root, food, dec) in enumerate(LOG):
                    if t % 5:
                        continue
                    if t == 0:
                        nsens.append(len(rows)); onroot.append(sum(r[0] == 0 for r in rows))
                    v = np.array([r[2] for r in rows]); P_ = np.array([r[1] for r in rows])
                    levels += v.tolist()
                    sr = S(root, food, dec)
                    for r in rows:
                        si = S(r[1], food, dec); Ss.append(si)
                        c = np.tanh(10 * (np.log(si) - np.log(sr)))
                        (contr_root if r[0] == 0 else contr).append(c)
                    if len(rows) > 1:
                        i, k = np.unravel_index(np.argmax(np.abs(v[:, None] - v[None, :])), (len(v), len(v)))
                        diffs.append(abs(v[i] - v[k])); seps.append(np.linalg.norm(P_[i] - P_[k]))
                    # C's model quantity at this root: two noses 0.3 m apart across a random heading
                    h = np.random.default_rng(t).uniform(0, 2 * np.pi); lat = 0.15 * np.array([-np.sin(h), np.cos(h)])
                    a, b = S(root + lat, food, dec), S(root - lat, food, dec)
                    diffs30.append(abs(a / (1 + a) - b / (1 + b)))
        pr = lambda x: f"median {np.median(x):.4f}  p90 {np.percentile(x, 90):.4f}"
        print(f"\n== {kind} (first {len(fs)} final members x 3 draws, every 5th tick)")
        print(f"   food sensors per body: {sorted(set(nsens))} (bodies with none are not logged); of these on the root part: {sorted(set(onroot))}")
        print(f"   reading level (sum mode, squashed): {pr(levels)}, min {np.min(levels):.3f} max {np.max(levels):.3f}; raw S {pr(Ss)}")
        if diffs:
            print(f"   per-tick max differential between two food sensors of one body: {pr(diffs)}; their separation {pr(seps)} m")
        print(f"   C's 0.3 m two-nose differential at the root's actual positions: {pr(diffs30)}")
        if contr:
            print(f"   proposed centred contrast tanh(10 (ln S_i - ln S_root)) on non-root food sensors: |c| {pr(np.abs(contr))}")
        if contr_root:
            print(f"   ... on root-part food sensors: max |c| {np.max(np.abs(contr_root)):.4f} (always ~0: the geom centre is the root body's)")


if __name__ == "__main__":
    main(sys.argv[1])
