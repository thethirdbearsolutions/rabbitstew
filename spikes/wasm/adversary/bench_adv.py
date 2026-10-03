"""RBT-133 adversary: two checks on §5's cost arithmetic (bench.py), on this container's one core.

    python spikes/wasm/adversary/bench_adv.py [REPS]

1. bench.py times today's path with `simulation.mujoco` replaced by a timing proxy whose __getattr__ forwards every
   `mujoco.X` lookup in simulation.py through a Python call.  Does that inflate the "today" denominator?
   Time run_bout with and without the proxy.
2. §5 scales an ARENA bout (2 robots, no food) to DESIGN.md §11.2's arm-season, which is an ECOLOGY arm-season
   (foraging, group_size 4, food smell per sensor per tick).  What is the mj_step share of a foraging group bout?
   Measured on RBT-105 forage-2-b2's config with generation-0 founders, 4 robots (2 holistic, 2 conventional).
"""

from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "spikes", "wasm"))

import mujoco  # noqa: E402

from rabbitstew import simulation  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, EvolutionConfig, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402

import bench  # noqa: E402  (spikes/wasm/bench.py: its _Timed proxy)


def arena(reps: int) -> None:
    print("1. arena bouts (spikes/wasm/locate/ref-x86/*): run_bout s/bout, plain vs under bench.py's timing proxy")
    for b in ("conventional-0", "holistic-0"):
        rec = os.path.join(ROOT, "spikes", "wasm", "locate", "ref-x86", b)
        cfg = simulation.SimConfig.from_dict(json.load(open(os.path.join(rec, "simconfig.json"))))
        gs = [Genotype.load(os.path.join(rec, f"robot{k}.json")) for k in range(2)]
        simulation.run_bout(gs[0], gs[1], cfg)
        res = {}
        for label in ("plain", "proxy", "plain2", "proxy2"):
            proxy = bench._Timed() if label.startswith("proxy") else None
            if proxy:
                simulation.mujoco = proxy
            try:
                t0 = time.perf_counter()
                for _ in range(reps):
                    simulation.run_bout(gs[0], gs[1], cfg)
                res[label] = (time.perf_counter() - t0) / reps
                if proxy:
                    res[label + "_step"] = proxy.t / reps
            finally:
                simulation.mujoco = mujoco
        plain = min(res["plain"], res["plain2"])
        prox = min(res["proxy"], res["proxy2"])
        print(f"  {b:16s} plain {plain:.4f}  under proxy {prox:.4f}  (proxy overhead {prox / plain - 1:+.1%}); "
              f"mj_step {res['proxy_step']:.4f} = {res['proxy_step'] / prox:.0%} of the proxied bout, {res['proxy_step'] / plain:.0%} of the plain one")


def ecology(reps: int) -> None:
    print("2. foraging group bout (RBT-105 forage-2-b2 config, gen-0 founders, group of 4: 2 holistic + 2 conventional)")
    d = json.load(open(os.path.join(ROOT, "runs", "RBT-105", "forage-2-b2", "config.json")))
    d["workers"] = 1
    d.pop("ecology", None)  # the EcologyConfig half; only the evolution/sim half is needed for a group bout
    cfg = EvolutionConfig.from_dict(d)
    rngs = spawn_streams(cfg.seed, cfg.holistic_stream_salt)
    hol = initial_population(HOLISTIC, cfg, rngs[HOLISTIC]).members
    con = initial_population(CONVENTIONAL, cfg, rngs[CONVENTIONAL]).members
    rows = []
    for k in range(reps):
        group = [hol[2 * k], hol[2 * k + 1], con[2 * k], con[2 * k + 1]]
        proxy = bench._Timed()
        simulation.mujoco = proxy
        try:
            t0 = time.perf_counter()
            simulation.run_group(group, cfg.sim, start_seed=1000 + k, food_seed=k)
            el = time.perf_counter() - t0
        finally:
            simulation.mujoco = mujoco
        rows.append((el, proxy.t))
    el = np.array(rows)
    print(f"  {reps} group bouts: mean {el[:, 0].mean():.4f} s/bout, mj_step {el[:, 1].mean():.4f} s "
          f"= {el[:, 1].sum() / el[:, 0].sum():.0%} (per bout {np.min(el[:, 1] / el[:, 0]):.0%}-{np.max(el[:, 1] / el[:, 0]):.0%})")


def main() -> None:
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    print(f"# {mujoco.__version__} | numpy {np.__version__} | reps {reps}")
    arena(reps)
    ecology(reps)


if __name__ == "__main__":
    main()
