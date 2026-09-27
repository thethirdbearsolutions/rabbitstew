"""RBT-120 DESIGN.md §2: the four candidate budgets applied, by arithmetic on the synthesised bodies (no simulation), to
the designed Pioneer and to every member of RBT-113's O-arm holistic founders and U/D/C final populations.

    options.py SEED_DIR [...] > options.txt       (restored runs/RBT-113/O*/<seed>)

Per body, the summed driven gear over (motor_strength x mass), under:
  now       gear = ms x max(child, parent mass) per driven DOF (world.py today)
  child     gear = ms x child mass per driven DOF (option 2)
  joint     a ball joint's ms x max(...) shared across its driven DOFs, so a joint carries one DOF's worth (option 3)
  sum-cap   now, then the summed gear capped at C = 1.77 x ms x mass (option 1, the recommendation)
  power     under the damping rule (driven damping = joint_damping x gear) a torque motor's free-spin power is
            gear^2 / damping = gear / joint_damping, so a power budget IS a summed-gear budget (option 4): not tabulated
"""
import glob
import json
import os
import sys

import numpy as np

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, EvolutionConfig, initial_population, spawn_streams
from rabbitstew.genotype import Genotype, JointType
from rabbitstew.synthesis import synthesize
from rabbitstew.world import driven_dofs

C = 1.77


def ratios(g, syn, ms=4.0):
    ph = synthesize(g, syn)
    mass = sum(p.mass for p in ph.parts)
    dr = driven_dofs(ph)
    now = child = joint = 0.0
    per_joint = {}
    for i, dof in dr:
        p, q = ph.parts[i], ph.parts[ph.parts[i].parent]
        now += ms * max(p.mass, q.mass)
        child += ms * p.mass
        per_joint.setdefault(i, []).append(ms * max(p.mass, q.mass))
    joint = sum(v[0] for v in per_joint.values())  # one DOF's worth per joint, shared
    k = ms * mass
    return now / k, child / k, joint / k, min(now, C * k) / k


def main(argv):
    rows = {}
    for sd in argv:
        cfg = EvolutionConfig.from_dict(json.load(open(os.path.join(sd, "U", "config.json"))))
        syn = cfg.sim.synthesis
        for kind in (HOLISTIC, CONVENTIONAL):
            groups = {"founders": initial_population(kind, cfg, spawn_streams(cfg.seed, cfg.holistic_stream_salt)[kind]).members}
            for L in "UDC":
                groups[L] = [Genotype.load(p) for p in sorted(glob.glob(os.path.join(sd, L, kind, "final", "*.json")))]
            for g, ms in groups.items():
                rows.setdefault((kind, g), []).append(np.array([ratios(m, syn) for m in ms]).mean(axis=0))
    print(f"# RBT-120 options.py over {len(argv)} seed directories: summed driven gear / (4 x mass), per-directory means, then mean [min, max] over directories")
    print(f"{'':22s} {'now':>18s} {'child-keyed':>18s} {'per-joint':>18s} {'sum-cap 1.77':>18s}")
    for (kind, g), A in rows.items():
        A = np.array(A)
        cells = [f"{A[:, j].mean():5.2f} [{A[:, j].min():4.2f}, {A[:, j].max():4.2f}]" for j in range(4)]
        print(f"{kind:12s} {g:9s} " + " ".join(f"{c:>18s}" for c in cells))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
