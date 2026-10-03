"""RBT-133 adversary: the harness branches the two packed bouts never take, checked against rabbitstew's Python.

    python spikes/wasm/adversary/semcheck.py WASM_RUN_ROOT      (WASM_RUN_ROOT/<bout>-bout/states.bin)

The packed bouts exercise only some sensor kinds and transfer functions (`evidence.txt` §1): no height, no joint_angle,
no ball-joint sensor on an actuated robot, no sin / sign / integrate unit, no static robot, no missing opponent,
no explosion.  This compiles semcheck.c (which #includes harness/rbt_wasm.c unchanged) natively and compares:

  sensors: EVERY source x axis on EVERY part of both robots of both bouts (hinge, slide, ball and free joints), at
           107 ticks of the harness's own WASM bout, against Simulation.sensor_values on the same state; then again
           with the opponent removed (`_opponent = None` / opp_root_body -1).
  brain:   random networks using all seven transfer functions, with exact zeros, -0.0, huge and NaN inputs, against
           RuntimeBrain.step.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import replace

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

import mujoco  # noqa: E402

from rabbitstew import simulation  # noqa: E402
from rabbitstew.brain import RuntimeBrain, SensorSpec  # noqa: E402
from rabbitstew.genotype import Genotype, JointType  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
KIND = {"contact": 0, "oscillator": 1, "target": 2, "opponent": 3, "target_distance": 4, "opponent_distance": 5, "up": 6, "velocity": 7, "height": 8, "joint_angle": 9, "joint_velocity": 10}
AXES = {"target": 3, "opponent": 3, "up": 3, "velocity": 3}
FUNCS = ["tanh", "sin", "abs", "relu", "sign", "integrate", "differentiate"]


def build_driver(tmp: str) -> str:
    exe = os.path.join(tmp, "semcheck")
    nb = os.environ.get("WASMBUILD_DIR", "/opt/rbt133-wasm")
    subprocess.run(["clang", "-O3", "-ffp-contract=off", "-fno-fast-math", f"-I{nb}/src/include", os.path.join(HERE, "semcheck.c"),
                    f"{nb}/build-native/lib/libmujoco.so", f"-Wl,-rpath,{nb}/build-native/lib", "-lm", "-o", exe], check=True)
    return exe


def sensors_check(exe: str, tmp: str, run_root: str) -> None:
    refs = os.path.join(ROOT, "spikes", "wasm", "locate", "ref-x86")
    for bout in ("conventional-0", "holistic-0"):
        rec = os.path.join(refs, bout)
        cfg = simulation.SimConfig.from_dict(json.load(open(os.path.join(rec, "simconfig.json"))))
        gs = [Genotype.load(os.path.join(rec, f"robot{k}.json")) for k in range(2)]
        sim = simulation.Simulation(gs, replace(cfg, settle_time=0.0), spawns=simulation.spawn_layout(2, cfg, None))
        m, d = sim.model, sim.data
        rows = np.fromfile(os.path.join(run_root, bout + "-bout", "states.bin"), dtype="<f8").reshape(-1, 1 + m.nq + 2 * m.nv + m.na)
        settle, sub = 200, cfg.control_substeps
        ticks = list(range(1, 750, 7))
        rng = np.random.default_rng(7)
        for no_opp in (False, True):
            for ri in range(2):
                idx, ph = sim.robots[ri], sim.phenotypes[ri]
                specs = []
                for p, part in enumerate(ph.parts):
                    for src in KIND:
                        for ax in range(AXES.get(src, 1)):
                            specs.append(SensorSpec(len(specs), p, src, ax, float(rng.uniform(0.2, 3.0)), float(rng.uniform(0, 6.3))))
                lines = [f"target {' '.join(float(v).hex() for v in sim._targets[ri])}"]
                opp = None if no_opp else sim._opponent[ri]
                lines.append(f"opp {sim.robots[opp].root_body if opp is not None else -1}")
                lines.append(f"n {len(specs)}")
                for s in specs:
                    part = ph.parts[s.part]
                    jid = idx.joints[s.part]
                    span = -1.0
                    if part.joint_range is not None:
                        span = max(abs(part.joint_range[0]), abs(part.joint_range[1]), 1e-6)
                    lines.append(f"{KIND[s.source]} {s.axis} {idx.bodies[s.part]} {idx.geoms[s.part]} {jid} {int(part.joint_type == JointType.BALL)} {float(span).hex()} {s.freq.hex()} {s.phase.hex()}")
                lines.append(f"cases {len(ticks)}")
                for t in ticks:
                    lines.append(f"{settle + sub * t - 2} {settle + sub * t - 1} {float(t * cfg.control_dt).hex()}")
                spec = os.path.join(tmp, "spec.txt")
                open(spec, "w").write("\n".join(lines) + "\n")
                out = os.path.join(tmp, "out.bin")
                mjb = os.path.join(ROOT, "spikes", "wasm", "packs", bout, "model.mjb")
                subprocess.run([exe, "sensors", mjb, spec, os.path.join(run_root, bout + "-bout", "states.bin"), out], check=True)
                C = np.fromfile(out, dtype="<f8").reshape(len(ticks), len(specs))
                brain = sim.brains[ri]
                saved = (brain.sensors, sim._opponent[ri])
                brain.sensors = specs
                sim._opponent[ri] = opp
                P = np.zeros_like(C)
                try:
                    for c, t in enumerate(ticks):
                        st = rows[settle + sub * t - 2]
                        o = 1
                        d.time = st[0]
                        for arr in (d.qpos, d.qvel, d.act, d.qacc_warmstart):
                            arr[:] = st[o : o + arr.size]
                            o += arr.size
                        mujoco.mj_forward(m, d)
                        post = rows[settle + sub * t - 1]
                        o = 1
                        for arr in (d.qpos, d.qvel, d.act):
                            arr[:] = post[o : o + arr.size]
                            o += arr.size
                        sim.time = t * cfg.control_dt
                        P[c] = sim.sensor_values(ri, sim.contact_bodies())
                finally:
                    brain.sensors, sim._opponent[ri] = saved
                gap = np.abs(P - C)
                bad = [(specs[k].source, specs[k].axis, specs[k].part, float(gap[:, k].max())) for k in range(len(specs)) if gap[:, k].max() > 1e-9]
                kinds = sorted({(s.source, ph.parts[s.part].joint_type.name if ph.parts[s.part].parent is not None else "root") for s in specs if s.source.startswith("joint")})
                print(f"{bout} robot {ri}{' (no opponent)' if no_opp else ''}: {len(specs)} sensors x {len(ticks)} ticks; "
                      f"bit-identical {np.mean(P == C):.3f}; max |gap| {gap.max():.1e}; sensors with gap > 1e-9: {bad if bad else 'none'}")
                print(f"    joint sensors covered: {kinds}")


def brain_check(exe: str, tmp: str) -> None:
    rng = np.random.default_rng(11)
    for trial in range(6):
        n, ns, T = 21, 4, 300
        func_of = [FUNCS[i % 7] for i in range(n)]
        W = rng.normal(0, 1.5, (n, n)) * (rng.random((n, n)) < 0.5)
        bias = rng.normal(0, 0.5, n)
        sens_units = sorted(rng.choice(n, ns, replace=False).tolist())
        S = rng.normal(0, 2, (T, ns))
        S[rng.random((T, ns)) < 0.1] = 0.0
        S[rng.random((T, ns)) < 0.05] = -0.0
        if trial >= 3:  # extreme inputs
            S[rng.random((T, ns)) < 0.05] = 1e300
        if trial == 5:
            S[150, 0] = np.nan
        b = RuntimeBrain.__new__(RuntimeBrain)
        b.n = n
        b.W = W
        b.bias = bias.copy()
        is_sensor = np.zeros(n, bool)
        is_sensor[sens_units] = True
        b.funcs = {}
        for i in range(n):
            if not is_sensor[i]:
                b.funcs.setdefault(func_of[i], []).append(i)
        b.funcs = {k: np.array(v, dtype=int) for k, v in b.funcs.items()}
        for i in sens_units:
            b.bias[i] = 0.0
        b.sensor_idx = np.array(sens_units, dtype=int)
        b.activation = np.zeros(n)
        b._prev_input = np.zeros(n)
        code = [-1 if is_sensor[i] else FUNCS.index(func_of[i]) for i in range(n)]
        L = [f"n {n}", "W " + " ".join(float(v).hex() for v in W.ravel()), "bias " + " ".join(float(v).hex() for v in b.bias),
             "func " + " ".join(map(str, code)), f"nsens {ns}", "units " + " ".join(map(str, sens_units)), f"steps {T}"]
        L += [" ".join(float(v).hex() for v in S[t]) for t in range(T)]
        spec = os.path.join(tmp, "brain.txt")
        open(spec, "w").write("\n".join(L) + "\n")
        out = os.path.join(tmp, "brain.bin")
        subprocess.run([exe, "brain", spec, out], check=True)
        C = np.fromfile(out, dtype="<f8").reshape(T, n)
        P = np.zeros((T, n))
        with np.errstate(all="ignore"):
            for t in range(T):
                b.step(S[t])
                P[t] = b.activation
        same = (P == C) | (np.isnan(P) & np.isnan(C))
        signbit = np.signbit(P) != np.signbit(C)
        gap = np.where(same, 0.0, np.abs(P - C))
        first = next(((t, i) for t in range(T) for i in range(n) if not same[t, i]), None)
        # per transfer function: the earliest step where its units first differ by more than 1e-9 (ULP noise feeds back
        # through W, so late gaps are not a semantic difference by themselves)
        big = {}
        for i in range(n):
            if is_sensor[i]:
                continue
            ts = np.nonzero(gap[:, i] > 1e-9)[0]
            if ts.size:
                big[func_of[i]] = min(big.get(func_of[i], T), int(ts[0]))
        nan_mis = int(np.sum(np.isnan(P) != np.isnan(C)))
        # baseline with the SAME semantics: numpy's brain with W @ a summed left to right (the harness's order) instead
        # of BLAS.  If this also parts from numpy's own run by > 1e-9 near the same step, the gap above is the
        # network's chaos amplifying ULPs, not a semantic difference.
        b2 = RuntimeBrain.__new__(RuntimeBrain)
        b2.__dict__.update({k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in b.__dict__.items()})
        b2.activation = np.zeros(n)
        b2._prev_input = np.zeros(n)
        Wl = W.copy()

        class _LoopW:
            def __matmul__(self, a):
                out = np.zeros(n)
                for i in range(n):
                    acc = 0.0
                    for j in range(n):
                        acc += Wl[i, j] * a[j]
                    out[i] = acc
                return out

        b2.W = _LoopW()
        b3 = RuntimeBrain.__new__(RuntimeBrain)
        b3.__dict__.update({k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in b.__dict__.items()})
        b3.activation = np.zeros(n)
        b3._prev_input = np.zeros(n)
        Q = np.zeros((T, n))
        P2 = np.zeros((T, n))
        with np.errstate(all="ignore"):
            for t in range(T):
                b2.step(S[t])
                b3.step(S[t])
                Q[t] = b2.activation
                P2[t] = b3.activation
        qgap = np.where((Q == P2) | (np.isnan(Q) & np.isnan(P2)), 0.0, np.abs(Q - P2))
        qfirst = next((t for t in range(T) if qgap[t].max() > 1e-9), None)
        print(f"brain trial {trial}: n {n}, {T} steps; bit-identical {same.mean():.3f}; first differing (step, unit) {first}"
              f"{' func ' + func_of[first[1]] if first else ''}; NaN mismatches {nan_mis}; "
              f"sign-bit mismatches among equal values {int(np.sum(signbit & same & ~np.isnan(P)))}; "
              f"first step with a gap > 1e-9, per function: {big if big else 'none'}; "
              f"numpy brain vs itself with left-to-right sums: first step with a gap > 1e-9 {qfirst}")


def main() -> None:
    run_root = sys.argv[1]
    with tempfile.TemporaryDirectory() as tmp:
        exe = build_driver(tmp)
        sensors_check(exe, tmp, run_root)
        brain_check(exe, tmp)


if __name__ == "__main__":
    main()
