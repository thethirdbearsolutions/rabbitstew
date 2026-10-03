"""RBT-133 adversary: is the C harness (harness/rbt_wasm.c) faithful to rabbitstew/simulation.py + brain.py?

    python spikes/wasm/adversary/faithful.py RUN_ROOT      (RUN_ROOT/<bout>-bout/{states.bin,ticks.bin} from a harness)

Three independent checks per packed bout, none of which relies on the closed loop staying together:

  A. closed loop, C against the Python reference recording (locate/ref-x86/<bout>/): per-tick max |diff| of sensors,
     activations and ctrl, and the first differing tick and its ULP gap.  Printed beside the cross-platform gap of the
     native Python bout (x86 vs linux-arm64, from locate/ci-run-37157969294/compare.txt) so that "diverges as another
     platform would" can be read off.

  B. teacher-forced sensors: for every tick, the harness's own physics state (states.bin) is loaded into a Python
     Simulation of the same bout, the kinematics are recomputed exactly as they stood when the harness read its sensors
     (the state at the start of the tick's last substep, + mj_forward, then that substep's integrated qpos/qvel/act on
     top, which is what mj_step leaves behind; tick 0 from the pack's post-settle state), and
     Simulation.sensor_values is evaluated there.  A semantic difference (sensor order, axis, body, opponent, clock,
     contact set) gives O(1) gaps; a faithful port gives ULP-level gaps at every tick, however far the bout has drifted.

  C. teacher-forced brain and effectors: the harness's sensor stream is fed to Python RuntimeBrain (open loop), and the
     harness's own activations are fed to effector_output; compared with the harness's activations and ctrl.

ticks.bin layout (rbt_wasm.c): per tick, for each non-exploded robot its sensor readings, then every robot's
activations, then ctrl (nu).
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import replace

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

import mujoco  # noqa: E402

from rabbitstew import simulation  # noqa: E402
from rabbitstew.brain import RuntimeBrain  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402

PACKS = os.path.join(ROOT, "spikes", "wasm", "packs")
REFS = os.path.join(ROOT, "spikes", "wasm", "locate", "ref-x86")


def ulp(x: float, y: float) -> int:
    return abs(int(np.float64(x).view(np.int64)) - int(np.float64(y).view(np.int64)))


def build(bout: str):
    rec = os.path.join(REFS, bout)
    cfg = simulation.SimConfig.from_dict(json.load(open(os.path.join(rec, "simconfig.json"))))
    gs = [Genotype.load(os.path.join(rec, f"robot{k}.json")) for k in range(2)]
    sim = simulation.Simulation(gs, replace(cfg, settle_time=0.0), spawns=simulation.spawn_layout(2, cfg, None))
    return cfg, sim


def split_ticks(sim, ticks: np.ndarray):
    ns = [len(b.sensors) for b in sim.brains]
    na = [b.n for b in sim.brains]
    nu = sim.model.nu
    w = sum(ns) + sum(na) + nu
    T = ticks.reshape(-1, w)
    S = T[:, : sum(ns)]
    A = T[:, sum(ns) : sum(ns) + sum(na)]
    C = T[:, sum(ns) + sum(na) :]
    return S, A, C, ns, na


def gap_table(name, X, Y, ticks=(0, 1, 2, 5, 10, 20, 50, 100, 200, 400, 749)):
    d = np.abs(X - Y)
    first = next((t for t in range(len(X)) if not np.array_equal(X[t], Y[t])), None)
    s = f"  {name:12s} first differing tick {first}"
    if first is not None:
        k = int(np.nonzero(X[first] != Y[first])[0][0])
        s += f" (index {k}: {X[first][k]!r} vs {Y[first][k]!r}, {ulp(X[first][k], Y[first][k])} ulp)"
    print(s)
    print("    " + "  ".join(f"t{t}:{d[t].max():.1e}" for t in ticks if t < len(d)))
    return d


def main() -> None:
    run_root = sys.argv[1]
    for bout in ("conventional-0", "holistic-0"):
        print(f"=== {bout}  (harness run {os.path.join(run_root, bout + '-bout')})")
        cfg, sim = build(bout)
        m, d = sim.model, sim.data
        run = os.path.join(run_root, bout + "-bout")
        S, A, C, ns, na = split_ticks(sim, np.fromfile(os.path.join(run, "ticks.bin"), dtype="<f8"))
        w = 1 + m.nq + 2 * m.nv + m.na
        rows = np.fromfile(os.path.join(run, "states.bin"), dtype="<f8").reshape(-1, w)
        rec = os.path.join(REFS, bout)
        PS, PA, PC = (np.load(os.path.join(rec, f)) for f in ("sensors.npy", "activations.npy", "ctrl.npy"))
        print(f"  shapes: harness sensors {S.shape} acts {A.shape} ctrl {C.shape}; python {PS.shape} {PA.shape} {PC.shape}; state rows {len(rows)}")

        print("A. closed loop, harness vs Python reference (max |diff| per tick)")
        gap_table("sensors", S, PS)
        gap_table("activations", A, PA)
        gap_table("ctrl", C, PC)

        print("B. teacher-forced sensors: Python sensor_values on the harness's own state, every tick")
        init = np.fromfile(os.path.join(PACKS, bout, "init_state.bin"), dtype="<f8")
        settle = cfg.control_substeps * int(round(cfg.settle_time / cfg.control_dt))
        sub = cfg.control_substeps
        worst = np.zeros(S.shape[1])
        worst_t = np.zeros(S.shape[1], dtype=int)
        over = 0
        for t in range(len(S)):
            st = init if t == 0 else rows[settle + sub * t - 2]  # state at the start of tick t-1's last substep
            o = 1
            d.time = st[0]
            for arr in (d.qpos, d.qvel, d.act, d.qacc_warmstart):
                arr[:] = st[o : o + arr.size]
                o += arr.size
            d.ctrl[:] = C[t - 1] if t else 0.0
            mujoco.mj_forward(m, d)
            if t:  # mj_step leaves the kinematics of the substep's start but the integrated qpos/qvel/act: so do we
                post = rows[settle + sub * t - 1]
                o = 1
                for arr in (d.qpos, d.qvel, d.act):
                    arr[:] = post[o : o + arr.size]
                    o += arr.size
            sim.time = t * cfg.control_dt
            touching = sim.contact_bodies()
            py = np.concatenate([sim.sensor_values(ri, touching) for ri in range(2)])
            g = np.abs(py - S[t])
            upd = g > worst
            worst[upd] = g[upd]
            worst_t[upd] = t
            if g.max() > 1e-9:
                over += 1
        print(f"  ticks with any sensor gap > 1e-9: {over} / {len(S)}")
        labels = [f"r{ri}:{s.source}[{s.axis}]" for ri, b in enumerate(sim.brains) for s in b.sensors]
        order = np.argsort(-worst)
        print("  worst gap per sensor (top 6): " + "; ".join(f"{labels[k]} {worst[k]:.1e} @t{worst_t[k]}" for k in order[:6]))

        print("C. teacher-forced brain: Python RuntimeBrain on the harness's sensor stream; effector_output on its activations")
        brains = [RuntimeBrain(ph) for ph in sim.phenotypes]
        first = None
        maxgap = 0.0
        for t in range(len(S)):
            o = 0
            for b, n in zip(brains, ns):
                b.step(S[t][o : o + n])
                o += n
            z = np.concatenate([b.activation for b in brains])
            g = np.abs(z - A[t]).max()
            maxgap = max(maxgap, g)
            if first is None and not np.array_equal(z, A[t]):
                k = int(np.nonzero(z != A[t])[0][0])
                first = (t, k, ulp(z[k], A[t][k]))
        print(f"  activations: first differing (tick, unit, ulp) {first}; max |gap| over 750 ticks {maxgap:.1e}")
        ctrl_gap = 0.0
        ctrl_neq = 0
        for t in range(len(S)):
            o = 0
            cpy = np.zeros(m.nu)
            for ri, (b, n) in enumerate(zip(brains, na)):
                b.activation = A[t][o : o + n].copy()
                o += n
                for key, aid in sim.robots[ri].actuators.items():
                    cpy[aid] = b.effector_output(*key)
            ctrl_gap = max(ctrl_gap, np.abs(cpy - C[t]).max())
            ctrl_neq += int(not np.array_equal(cpy, C[t]))
        print(f"  ctrl from the harness's activations: ticks not bit-identical {ctrl_neq} / {len(S)}; max |gap| {ctrl_gap:.1e}")
        print()


if __name__ == "__main__":
    main()
