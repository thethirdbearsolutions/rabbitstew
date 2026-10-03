"""RBT-133: export one recorded bout (spikes/wasm/locate/probe.py `record` output) as inputs for the C harness.

    python spikes/wasm/pack.py REC_DIR OUT_DIR

Writes, into OUT_DIR:
  model.xml        the bout's final XML (copied; checked equal to what this checkout generates)
  model.mjb        the reference platform's compiled model (copied)
  init_state.bin   the reference's post-settle state: time, qpos, qvel, act, qacc_warmstart (float64, little endian)
  ctrl.bin         the reference's ctrl at every control tick (float64, ticks x nu)
  pack.txt         everything the closed loop needs beyond the XML: tick counts, target, and per robot the MuJoCo ids,
                   the sensor specs and the folded brain (W, bias, transfer function per unit, effector units per
                   actuator).  Floats are written as C99 hex literals (float.hex), so strtod reads them back exactly.

The harness (harness/rbt_wasm.c) implements Simulation.settle / Simulation.step / zero_sum_fitness for the arena's
'rich' sensor set (no food, no agent smell, no waypoints, settle_until_rest off); pack.py refuses anything else.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import replace

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from rabbitstew import simulation, world  # noqa: E402
from rabbitstew.genotype import Genotype, JointType  # noqa: E402

SENSOR_KIND = {"contact": 0, "oscillator": 1, "target": 2, "opponent": 3, "target_distance": 4, "opponent_distance": 5, "up": 6, "velocity": 7, "height": 8, "joint_angle": 9, "joint_velocity": 10}
FUNC = {"tanh": 0, "sin": 1, "abs": 2, "relu": 3, "sign": 4, "integrate": 5, "differentiate": 6}


def hx(x) -> str:
    return float(x).hex()


def main() -> None:
    rec, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    cfg = simulation.SimConfig.from_dict(json.load(open(os.path.join(rec, "simconfig.json"))))
    if cfg.food is not None or cfg.waypoints or cfg.settle_until_rest or cfg.opponent_proxy:
        raise SystemExit("pack.py: only the plain arena bout is implemented (no food, waypoints, settle_until_rest, opponent_proxy)")
    gs = [Genotype.load(os.path.join(rec, f"robot{k}.json")) for k in range(2)]
    xmls = []
    orig = world.build_xml

    def capture(*a, **k):
        x = orig(*a, **k)
        xmls.append(x)
        return x

    world.build_xml = capture
    try:  # no settle: only the ids, the brains and the XML are wanted
        sim = simulation.Simulation(gs, replace(cfg, settle_time=0.0), spawns=simulation.spawn_layout(2, cfg, None))
    finally:
        world.build_xml = orig
    ref_xml = open(os.path.join(rec, "model.xml")).read()
    if xmls[-1] != ref_xml:
        raise SystemExit("pack.py: this checkout generates a different XML from the recording's")
    for f in ("model.xml", "model.mjb"):
        shutil.copy(os.path.join(rec, f), os.path.join(out, f))
    np.load(os.path.join(rec, "init_state.npy")).astype("<f8").tofile(os.path.join(out, "init_state.bin"))
    ctrl = np.load(os.path.join(rec, "ctrl.npy")).astype("<f8")
    ctrl.tofile(os.path.join(out, "ctrl.bin"))
    m = sim.model
    L = []
    settle_steps = int(round(cfg.settle_time / cfg.control_dt)) * cfg.control_substeps
    ticks = int(round(cfg.duration / cfg.control_dt))
    L.append(f"substeps {cfg.control_substeps}")
    L.append(f"settle_steps {settle_steps}")
    L.append(f"ticks {ticks}")
    L.append(f"control_dt {hx(cfg.control_dt)}")
    L.append(f"explosion_speed {hx(cfg.explosion_speed)}")
    t = cfg.effective_target()
    L.append(f"target {hx(t[0])} {hx(t[1])} {hx(t[2])}")
    L.append(f"nu {m.nu}")
    L.append(f"robots {len(sim.robots)}")
    for ri, (idx, br) in enumerate(zip(sim.robots, sim.brains)):
        opp = sim._opponent[ri]
        L.append(f"robot {ri} root_body {idx.root_body} root_qpos_adr {idx.root_qpos_adr} static {int(idx.spawn.static)} spawn {hx(idx.spawn.position[0])} {hx(idx.spawn.position[1])} opp_root_body {sim.robots[opp].root_body if opp is not None else -1}")
        L.append("bodies " + " ".join(str(b) for b in idx.bodies))
        n = br.n
        L.append(f"units {n}")
        L.append("bias " + " ".join(hx(v) for v in br.bias))
        L.append("W " + " ".join(hx(v) for v in br.W.ravel()))
        func = [-1] * n
        for name, ids in br.funcs.items():
            for i in ids:
                func[int(i)] = FUNC[name]
        L.append("func " + " ".join(str(f) for f in func))
        L.append(f"sensors {len(br.sensors)}")
        ph = br.phenotype
        for s in br.sensors:
            if s.source not in SENSOR_KIND:
                raise SystemExit(f"pack.py: sensor source {s.source!r} is not implemented in the harness")
            part = ph.parts[s.part]
            jid = idx.joints[s.part]
            ball = int(part.joint_type == JointType.BALL)
            span = -1.0
            if part.joint_range is not None:
                span = max(abs(part.joint_range[0]), abs(part.joint_range[1]), 1e-6)
            L.append(f"s {s.unit} {SENSOR_KIND[s.source]} {s.axis} {idx.bodies[s.part]} {idx.geoms[s.part]} {jid} {ball} {hx(span)} {hx(s.freq)} {hx(s.phase)}")
        L.append(f"actuators {len(idx.actuators)}")
        for key, aid in idx.actuators.items():
            units = br.effectors.get(key, [])
            L.append(f"a {aid} {len(units)} " + " ".join(str(u) for u in units))
    with open(os.path.join(out, "pack.txt"), "w") as f:
        f.write("\n".join(L) + "\n")
    summ = json.load(open(os.path.join(rec, "summary.json")))
    print(f"packed {rec} -> {out}: nu {m.nu}, nq {m.nq}, nv {m.nv}, ticks {ticks}; reference distances {summ['distances_hex']}")


if __name__ == "__main__":
    main()
