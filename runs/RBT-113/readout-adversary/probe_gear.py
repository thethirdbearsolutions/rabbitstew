"""RBT-113 readout adversary, probe 3b: where the holistic lines' motor capacity comes from (no simulation, model build only).

    probe_gear.py SEED_DIR [...] > probe_gear.txt

world.py gives every driven DOF a gear of motor_strength (4) x the LARGER of the two masses the joint connects, and a
ball joint up to three such motors.  The mass budget caps total mass, not total gear: a heavy part carrying several
driven joints counts its own mass once per driven DOF.  Per line (all 40 members of generation 23, both faunas) this
prints the summed torque-motor gear, its ratio to 4 x body mass, the share of it on ball-joint DOFs, and the
full-throttle free-spin work ceiling (gear^2 / damping x 15 s, in yield units at 0.03 per kJ).
"""
import os
import sys

import mujoco
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import decompose  # noqa: E402
import world  # noqa: E402

import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402


def gear(g, sc):
    sim = S.Simulation([g], sc, spawns=S.spawn_layout(1, sc, 2131))
    m = sim.model
    tot = ball = ceil = 0.0
    for a in range(m.nu):
        if m.actuator_biastype[a] != 0:
            continue
        j = m.actuator_trnid[a, 0]
        k = int(np.argmax(np.abs(m.actuator_gear[a, :3])))
        isball = m.jnt_type[j] == mujoco.mjtJoint.mjJNT_BALL
        dof = m.jnt_dofadr[j] + (k if isball else 0)
        gv = abs(m.actuator_gear[a, k])
        tot += gv
        ball += gv if isball else 0.0
        ceil += gv * gv / max(m.dof_damping[dof], 1e-9)
    return tot, ball, float(m.body_mass[1:].sum()), ceil * sc.duration * 0.03 / 1000


def main(argv):
    rows = {}
    for d in argv:
        op, seed = decompose.parse_seed_dir(d)
        cfg = world.evolution_config("U", op, seed=seed)
        sc = generation_sim(cfg, 1131)
        streams = spawn_streams(seed, cfg.holistic_stream_salt)
        for kind in (HOLISTIC, CONVENTIONAL):
            groups = {"founders": initial_population(kind, cfg, streams[kind]).members}
            for L in "UDC":
                p = os.path.join(d, L, kind, "final")
                groups[L] = [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
            for gname, ms in groups.items():
                rows.setdefault((kind, gname), []).append(np.array([gear(g, sc) for g in ms]))
    print(f"# probe_gear.py over {len(argv)} seed directories, every member; per-directory means, then mean [min, max] over directories")
    for (kind, gname), A in rows.items():
        s = np.array([a[:, 0].mean() for a in A]); r = np.array([(a[:, 0] / (4 * a[:, 2])).mean() for a in A])
        b = np.array([a[:, 1].sum() / max(a[:, 0].sum(), 1e-9) for a in A]); c = np.array([a[:, 3].mean() for a in A])
        print(f"{kind:12s} {gname:8s} sum gear {s.mean():6.1f} [{s.min():6.1f}, {s.max():6.1f}]  / (4 x mass) {r.mean():.2f} [{r.min():.2f}, {r.max():.2f}]"
              f"  ball-joint share {b.mean():.2f}  free-spin ceiling (yield) {c.mean():.2f} [{c.min():.2f}, {c.max():.2f}]")


if __name__ == "__main__":
    main(sys.argv[1:])
