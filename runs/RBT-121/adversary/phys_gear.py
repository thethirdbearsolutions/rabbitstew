"""RBT-121 adversary (physics): re-derive audit A's A1 gear arithmetic from the COMPILED MuJoCo models.

    phys_gear.py SEED_DIR [...] > phys_gear.txt

1. Free-spin check: a one-hinge MJCF built exactly as world.py builds a driven joint (torque motor, gear G, joint
   damping 0.05 G, armature 0.005), zero gravity, ctrl = 1, for G in {5, 54, 200}: steady speed and |F v| power, to test
   "no-load speed 20 rad/s, power = 20 G".  Also a velocity servo and a position servo on the same hinge, ctrl = 1.
2. For every holistic and designed member of generation 23 (U, D, C) and the founders: Sigma|gear| over the compiled
   model's actuators (driven DOFs) / (4 x robot mass from model.body_mass), per actuator mode, and the ratio under rule
   (b) (one gear per ball joint, max of its DOF gears) and rule (c) (cap 1.77).  Compared with probe_static's figures.
Nothing is written into any run.
"""
import os
import sys
from dataclasses import replace

import mujoco
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "RBT-113"))
import decompose  # noqa: E402
import world  # noqa: E402

import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402

TERRAIN, START = decompose.DRAWS[0]


def spin(G, mode):
    act = {"torque": f'<motor joint="j" gear="{G}" ctrllimited="true" ctrlrange="-1 1"/>',
           "velocity": f'<general joint="j" gaintype="fixed" biastype="affine" gainprm="{G}" biasprm="0 0 {-G / 12}" ctrllimited="true" ctrlrange="-1 1"/>',
           "position": f'<general joint="j" gaintype="fixed" biastype="affine" gainprm="{G}" biasprm="0 {-G / np.pi} {-0.1 * G / np.pi}" ctrllimited="true" ctrlrange="-1 1"/>'}[mode]
    xml = f"""<mujoco><option timestep="0.005" gravity="0 0 0"/><worldbody><body><joint name="j" type="hinge" axis="0 0 1"
      damping="{0.05 * G}" armature="0.005"/><geom type="box" size="0.2 0.05 0.05" pos="0.2 0 0" mass="0.5"/></body></worldbody>
      <actuator>{act}</actuator></mujoco>"""
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    d.ctrl[0] = 1.0
    for _ in range(3000):
        mujoco.mj_step(m, d)
    return float(d.qvel[0]), float(abs(d.actuator_force[0] * d.actuator_velocity[0]))


def measure(g, sc):
    cfg = replace(sc, random_start=True, settle_time=0.0)
    sim = S.Simulation([g], cfg, spawns=S.spawn_layout(1, cfg, START))
    m, idx = sim.model, sim.robots[0]
    M = float(sum(m.body_mass[b] for b in idx.bodies))
    tot, bymode, perjoint = 0.0, {}, {}
    for aid in range(m.nu):
        G = float(np.abs(m.actuator_gear[aid]).sum())
        j = int(m.actuator_trnid[aid, 0])
        jt = int(m.jnt_type[j])
        if m.actuator_gaintype[aid] == mujoco.mjtGain.mjGAIN_FIXED and m.actuator_biastype[aid] == mujoco.mjtBias.mjBIAS_AFFINE:
            # servo: world.py passes gear=1 and puts the capacity in gainprm (kp*span or kv*vmax), = the part's gear
            G = float(m.actuator_gainprm[aid, 0])
            mode = "vel" if m.actuator_biasprm[aid, 1] == 0 else "pos"
        else:
            mode = "ball" if jt == mujoco.mjtJoint.mjJNT_BALL else "torque"
        tot += G
        bymode[mode] = bymode.get(mode, 0.0) + G
        perjoint[j] = max(perjoint.get(j, 0.0), G)
    r = tot / (4 * M)
    share = sum(perjoint.values()) / (4 * M)
    return r, share, min(r, 1.77), bymode, M


def main():
    print("# phys_gear.py")
    print("# 1. one hinge, ctrl = 1, zero gravity, 15 s: G, mode -> steady speed (rad/s), |F v| (W), power / G")
    for mode in ("torque", "velocity", "position"):
        for G in (5.0, 54.0, 200.0):
            w, p = spin(G, mode)
            print(f"   {mode:8s} G={G:6.1f}  speed {w:8.3f}  power {p:9.2f}  power/G {p / G:6.3f}")
    rows = {}
    for dd in sys.argv[1:]:
        op, seed = decompose.parse_seed_dir(dd)
        cfg = world.evolution_config("U", op, seed=seed)
        sc = generation_sim(cfg, TERRAIN)
        streams = spawn_streams(seed, cfg.holistic_stream_salt)
        for kind in (HOLISTIC, CONVENTIONAL):
            groups = {"founders": initial_population(kind, cfg, streams[kind]).members}
            for L in "UDC":
                p = os.path.join(dd, L, kind, "final")
                groups[L] = [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
            for k, ms in groups.items():
                rows.setdefault((kind, k), []).extend(measure(g, sc) for g in ms)
    print("# 2. from compiled models: Sigma gear / (4 M), mean/max | rule (b) share-per-ball | rule (c) cap 1.77 | share of Sigma gear by actuator kind | M")
    for (kind, k), R in rows.items():
        r = np.array([x[0] for x in R])
        sh = np.array([x[1] for x in R])
        cp = np.array([x[2] for x in R])
        tot = {}
        for x in R:
            for mm, v in x[3].items():
                tot[mm] = tot.get(mm, 0.0) + v
        T = sum(tot.values())
        print(f"{kind:12s} {k:8s} n={len(R):3d} cur {r.mean():.4f}/{r.max():.3f}  (b) {sh.mean():.3f}  (c) {cp.mean():.3f} capped {np.mean(r > 1.77):.3f}  "
              + " ".join(f"{mm}={v / T:.2f}" for mm, v in sorted(tot.items())) + f"  M={np.mean([x[4] for x in R]):.3f}")


if __name__ == "__main__":
    main()
