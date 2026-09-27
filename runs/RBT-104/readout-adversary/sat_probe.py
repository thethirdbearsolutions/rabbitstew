"""RBT-104 readout adversary, POST HOC: does the host leave the drive Effectors in range for an installed compass?

For each run directory (a restored checkpoint or a make_host.py synthetic host) and each of the readout's
seven bests (300-590), the a = 64 install control's body is built exactly as function.py builds it
(function.install, signed +1: the sign does not change the magnitudes read here) and run on real smell for
SEEDS paired seeds from 7000. Before every control tick, for each drive Effector instance (the wheel
Effectors the motif feeds), the pre-activation that brain.step is about to squash is split into
  x_host = everything but the compass unit's link,   c = the compass unit's contribution (w * a_k),
and it records
  |x_host|                          the host's own drive on the Effector (median over ticks),
  sat = P(|x_host| > 2)             the fraction of ticks at which tanh's slope is below 0.07,
  slope = E[sech^2(x_host)]         the Effector's small-signal gain at the host's operating point,
  T = E|tanh(x_host + c) - tanh(x_host)| / E|tanh(c)|
                                    how much of the compass's effect reaches the Effector, against an idle Effector (1 = all).
POST HOC; it scores nothing and enters no rule.

  sat_probe.py [--seeds 4] [--install 32[,1]] LABEL=RUN_DIR ...
"""
import argparse
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("rbt104_function", os.path.join(os.path.dirname(HERE), "function.py"))
fn = importlib.util.module_from_spec(_s)
sys.modules["rbt104_function"] = fn
_s.loader.exec_module(fn)
rp, routed = fn.rp, fn.routed

from rabbitstew.simulation import Simulation, spawn_layout  # noqa: E402


def body_stats(run, cfg, gen, w, s, seeds):
    g = fn.install(rp.genotype(run, "conventional", gen), w, s, +1.0)
    k_geno = len(g.global_brain.units) - 1
    _, eff = routed.unit_indices(g)
    xs, cs = [], []
    for seed in seeds:
        sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
        sim.set_food_seed(seed)
        br = sim.brains[0]
        units = br.phenotype.units
        k = [i for i, u in enumerate(units) if u.part is None and u.ref.index == k_geno and u.unit.kind == "neuron"]
        assert len(k) == 1, k
        k = k[0]
        E = [i for i, u in enumerate(units) if u.unit.kind == "effector" and u.ref.node in routed.WHEELS and u.ref.index == eff]
        assert E and all(br.W[e, k] != 0 for e in E), (E, [br.W[e, k] for e in E])
        for _ in range(int(round(cfg.duration / cfg.control_dt))):
            if sim.exploded[0]:
                break
            a = br.activation
            for e in E:
                x = float(br.W[e] @ a + br.bias[e])
                c = float(br.W[e, k] * a[k])
                xs.append(x - c)
                cs.append(c)
            sim.step()
    return np.array(xs), np.array(cs)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, default=4)
    p.add_argument("--install", default="32")
    p.add_argument("runs", nargs="+")
    a = p.parse_args()
    w, s = (tuple(float(x) for x in (a.install.split(",") + ["1"])[:2]))
    seeds = [7000 + i for i in range(a.seeds)]
    print(f"# POST HOC: drive-Effector operating point under the install control (w = {w:g}, input +-{s:g}), "
          f"bests {list(fn.GENS)}, {a.seeds} seeds each, real smell\n")
    print("| host | median abs(x_host) | sat P(abs(x_host) > 2) | slope E[sech^2] | median abs(c) | T (share of the compass's effect reaching the Effector) |")
    print("|---|---|---|---|---|---|")
    for item in a.runs:
        label, run = item.split("=", 1)
        cfg = rp.config(run)
        X, C = [], []
        for gen in fn.GENS:
            x, c = body_stats(run, cfg, gen, w, s, seeds)
            X.append(x); C.append(c)
        x, c = np.concatenate(X), np.concatenate(C)
        slope = float(np.mean(1.0 / np.cosh(np.clip(x, -50, 50)) ** 2))
        T = float(np.mean(np.abs(np.tanh(x + c) - np.tanh(x))) / max(1e-12, np.mean(np.abs(np.tanh(c)))))
        print(f"| {label} | {np.median(np.abs(x)):.2f} | {np.mean(np.abs(x) > 2):.3f} | {slope:.3f} | {np.median(np.abs(c)):.2f} | {T:.3f} |")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
