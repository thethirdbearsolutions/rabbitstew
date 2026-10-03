"""RBT-133 step 4: cost of the WASM path against today's, per bout and per arm-season.

    python spikes/wasm/bench.py DIST [REPS]     (DIST holds rbt_wasm.js and, from NATIVE=1 build.sh, rbt_native)

Per packed bout (spikes/wasm/packs/*), three ways of running the same 15 s arena bout:
  python   today's path: rabbitstew.simulation.run_bout (Python sensors + numpy brain + the pip wheel's native MuJoCo);
           the time spent inside mujoco.mj_step is measured separately (perf_counter around each call)
  native   spikes/wasm/harness/rbt_wasm.c compiled natively against the same patched source (scalar, contraction off)
  wasm     the same C compiled to WASM, under Node (one process; the bench loop runs inside it)
All single-threaded, on one core, wall time.  Prints a table and the arm-season scaling against DESIGN.md §11.2.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

import mujoco  # noqa: E402

from rabbitstew import simulation  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402


class _Timed:
    def __init__(self):
        self.t = 0.0

    def __getattr__(self, name):
        return getattr(mujoco, name)

    def mj_step(self, m, d):
        t0 = time.perf_counter()
        mujoco.mj_step(m, d)
        self.t += time.perf_counter() - t0


def python_bout(rec: str, reps: int):
    cfg = simulation.SimConfig.from_dict(json.load(open(os.path.join(rec, "simconfig.json"))))
    gs = [Genotype.load(os.path.join(rec, f"robot{k}.json")) for k in range(2)]
    simulation.run_bout(gs[0], gs[1], cfg)  # warm up
    proxy = _Timed()
    simulation.mujoco = proxy
    try:
        t0 = time.perf_counter()
        for _ in range(reps):
            simulation.run_bout(gs[0], gs[1], cfg)
        el = time.perf_counter() - t0
    finally:
        simulation.mujoco = mujoco
    return el / reps, proxy.t / reps


def harness(cmd: list, pack: str, reps: int) -> float:
    out = subprocess.run(cmd + ["bench", pack, str(reps)], capture_output=True, text=True, check=True).stdout
    return float(re.search(r"([0-9.]+) s per bout", out).group(1))


def main() -> None:
    dist = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    from rabbitstew.provenance import _cpu_model

    print(f"# {_cpu_model()} | node {subprocess.run(['node', '--version'], capture_output=True, text=True).stdout.strip()} | mujoco {mujoco.__version__} | numpy {np.__version__} | {reps} bouts each, 15 s bouts, 3200 mj_steps incl. the settle")
    print(f"{'bout':16s} {'python s/bout':>14s} {'of which mj_step':>17s} {'native C s/bout':>16s} {'wasm s/bout':>12s} {'wasm/native':>12s} {'wasm/python':>12s}")
    ratios = []
    for b in sorted(os.listdir(os.path.join(ROOT, "spikes", "wasm", "packs"))):
        pack = os.path.join(ROOT, "spikes", "wasm", "packs", b)
        rec = os.path.join(ROOT, "spikes", "wasm", "locate", "ref-x86", b)
        py, py_step = python_bout(rec, reps)
        nat = harness([os.path.join(dist, "rbt_native")], pack, reps) if os.path.exists(os.path.join(dist, "rbt_native")) else float("nan")
        wa = harness(["node", os.path.join(dist, "rbt_wasm.js")], pack, reps)
        ratios.append((py, py_step, nat, wa))
        print(f"{b:16s} {py:14.4f} {py_step:12.4f} ({py_step / py:4.0%}) {nat:16.4f} {wa:12.4f} {wa / nat:12.2f} {wa / py:12.2f}")
    py, py_step, nat, wa = (float(np.mean([r[i] for r in ratios])) for i in range(4))
    print(f"{'mean':16s} {py:14.4f} {py_step:12.4f} ({py_step / py:4.0%}) {nat:16.4f} {wa:12.4f} {wa / nat:12.2f} {wa / py:12.2f}")
    # arm-season: DESIGN.md §11.2 budgets 20-25 core-s per arm-season on today's path
    for base in (20.0, 25.0):
        swap_physics = base * (1 - py_step / py) + base * (py_step / py) * (wa / nat)
        all_wasm = base * (wa / py)
        print(f"arm-season at {base:.0f} core-s today: physics-only swap (Python drives WASM MuJoCo) ~{swap_physics:.1f} core-s "
              f"(x{swap_physics / base:.2f}); whole bout in WASM ~{all_wasm:.1f} core-s (x{all_wasm / base:.2f}, bout share only)")


if __name__ == "__main__":
    main()
