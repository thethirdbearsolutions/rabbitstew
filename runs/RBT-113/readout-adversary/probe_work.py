"""RBT-113 readout adversary, probe 3: is the holistic down line's work genuine actuation or a physics artefact?

    probe_work.py [--per-group K] [--workers W] SEED_DIR [SEED_DIR ...] > probe_work.txt

Replays, solo, on decompose.py's FIRST fixed draw (terrain 1131, start 2131), K members of each group
(founders, U, D, C; both faunas; members chosen by a fixed rng) and records, per individual:
  * work_J at the registered integration (timestep 0.005 s x 4 substeps), checked against a plain run_group;
  * work_J at timestep 0.0025 x 8 and 0.00125 x 16 (the SAME control interval, 0.02 s, so the brain sees the same
    clock): genuine actuation converges under refinement, integrator chatter does not;
  * the share of |F.v| done by torque motors / position servos / velocity servos;
  * the share of |F.v| that is NEGATIVE (the actuator absorbing energy: braking, or fighting itself);
  * the share of |F.v| done in substeps where that actuator's velocity changed sign since the previous substep
    (chatter at the physics rate, 200 Hz, faster than the 50 Hz controller can command);
  * max body speed (explosion is 200 m/s), deepest contact penetration, MuJoCo's bad-QACC warning count,
    whether the season exploded (and so booked 0).
Needs the arms restored (RUNNER §6). Nothing here writes into a run.
"""
import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import decompose  # noqa: E402
import world  # noqa: E402

import mujoco  # noqa: E402
import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402

TERRAIN, START = decompose.DRAWS[0]
REFINE = [(0.005, 4), (0.0025, 8), (0.00125, 16)]


def _modes(model):
    """0 torque motor, 1 position servo, 2 velocity servo (from the MJCF world.py writes)."""
    out = np.zeros(model.nu, int)
    for a in range(model.nu):
        if model.actuator_biastype[a] == mujoco.mjtBias.mjBIAS_AFFINE:
            out[a] = 1 if model.actuator_biasprm[a, 1] != 0 else 2
    return out


def replay(gd, sim_cfg, dt, sub, diag):
    g = Genotype.from_dict(gd)
    cfg = replace(sim_cfg, random_start=True, control_substeps=sub, world=replace(sim_cfg.world, timestep=dt))
    spawns = S.spawn_layout(1, cfg, START)
    sim = S.Simulation([g], cfg, spawns=spawns)
    sim.set_food_seed(START)
    if not diag:
        sim.run()
        return {"work_J": float(sim.work[0]), "exploded": bool(sim.exploded[0]), "food": float(sim.food_eaten[0])}
    m, d = sim.model, sim.data
    modes = _modes(m)
    acc = {"by_mode": np.zeros(3), "neg": 0.0, "flip": 0.0, "tot": 0.0, "vmax": 0.0, "pen": 0.0, "limit_steps": 0, "sat_pos": 0.0}
    prev = [None]
    real = mujoco.mj_step

    def step(model, data):
        real(model, data)
        if not model.nu:
            return
        f, v = data.actuator_force, data.actuator_velocity
        p = f * v * model.opt.timestep
        ap = np.abs(p)
        acc["tot"] += ap.sum()
        acc["neg"] += ap[p < 0].sum()
        np.add.at(acc["by_mode"], modes, ap)
        if prev[0] is not None:
            acc["flip"] += ap[np.sign(v) != np.sign(prev[0])].sum()
        prev[0] = v.copy()
        acc["vmax"] = max(acc["vmax"], float(np.linalg.norm(data.cvel[1:, 3:], axis=1).max()))
        if data.ncon:
            acc["pen"] = min(acc["pen"], float(data.contact.dist[: data.ncon].min()))
        acc["limit_steps"] += int(np.any(data.efc_type[: data.nefc] == mujoco.mjtConstraint.mjCNSTR_LIMIT_JOINT))
        # torque motors pinned at |ctrl| ~ 1 (saturated effector output)
        tm = modes == 0
        if tm.any():
            acc["sat_pos"] += ap[tm & (np.abs(data.ctrl) > 0.98)].sum()

    class Proxy:
        def __getattr__(self, k):
            return step if k == "mj_step" else getattr(mujoco, k)

    S.mujoco = Proxy()
    try:
        sim.run()
    finally:
        S.mujoco = mujoco
    t = max(acc["tot"], 1e-12)
    return {"work_J": float(sim.work[0]), "exploded": bool(sim.exploded[0]), "food": float(sim.food_eaten[0]),
            "abs_J": float(acc["tot"]), "frac_torque": acc["by_mode"][0] / t, "frac_pos": acc["by_mode"][1] / t,
            "frac_vel": acc["by_mode"][2] / t, "frac_neg": acc["neg"] / t, "frac_flip": acc["flip"] / t,
            "frac_sat": acc["sat_pos"] / t, "vmax": acc["vmax"], "pen": acc["pen"],
            "limit_frac": acc["limit_steps"] / max(1, sim.tick * sub), "badqacc": int(d.warning[mujoco.mjtWarning.mjWARN_BADQACC].number),
            "nu": int(m.nu), "nparts": int(m.nbody - 1 - 0), "mass": float(m.body_mass[1:].sum()),
            "sum_gear": float(sum(abs(m.actuator_gear[a, :3]).max() for a in range(m.nu) if modes[a] == 0)),
            "ceiling_J": _ceiling(m, modes, sim.config.duration)}


def _ceiling(m, modes, duration):
    """Free-spin work of every torque motor held at full throttle: terminal speed gear / damping, power gear^2 / damping
    (the joint damper is the motor's speed limit, world.py); servos are left out (0 in this study's D lines)."""
    tot = 0.0
    for a in range(m.nu):
        if modes[a] != 0:
            continue
        j = m.actuator_trnid[a, 0]
        k = int(np.argmax(np.abs(m.actuator_gear[a, :3])))
        dof = m.jnt_dofadr[j] + (k if m.jnt_type[j] == mujoco.mjtJoint.mjJNT_BALL else 0)
        g = abs(m.actuator_gear[a, k])
        tot += g * g / max(m.dof_damping[dof], 1e-9)
    return float(tot * duration)


def job(args):
    gd, sim_cfg = args
    out = {}
    for k, (dt, sub) in enumerate(REFINE):
        out[f"r{k}"] = replay(gd, sim_cfg, dt, sub, diag=(k == 0))
    ref = S.run_group([Genotype.from_dict(gd)], sim_cfg, START)[0]
    out["registered_work_J"] = 0.0 if ref["exploded"] else ref["work"]
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-group", type=int, default=4)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("seed_dirs", nargs="+")
    a = ap.parse_args(argv)
    rng = np.random.default_rng(113117)
    tasks, keys = [], []
    for d in a.seed_dirs:
        op, seed = decompose.parse_seed_dir(d)
        cfg = world.evolution_config("U", op, seed=seed)
        sim_cfg = generation_sim(cfg, TERRAIN)
        streams = spawn_streams(seed, cfg.holistic_stream_salt)
        for kind in (HOLISTIC, CONVENTIONAL):
            groups = {"founders": initial_population(kind, cfg, streams[kind]).members}
            for L in "UDC":
                fs = sorted(os.listdir(os.path.join(d, L, kind, "final")))
                groups[L] = [Genotype.load(os.path.join(d, L, kind, "final", f)) for f in fs]
            for gname, ms in groups.items():
                for i in rng.choice(len(ms), a.per_group, replace=False):
                    tasks.append((ms[i].to_dict(), sim_cfg))
                    keys.append((d, kind, gname, ms[i].name))
    with ProcessPoolExecutor(a.workers) as pool:
        res = list(pool.map(job, tasks, chunksize=1))
    rows = [dict(seed_dir=k[0], fauna=k[1], group=k[2], name=k[3], **r) for k, r in zip(keys, res)]
    json.dump(rows, open(os.path.join(HERE, "probe_work.json"), "w"), indent=1, default=float)
    print(f"# probe_work.py: {len(rows)} replays on draw ({TERRAIN}, {START}); per group {a.per_group} per seed dir per fauna")
    for kind in (HOLISTIC, CONVENTIONAL):
        for gname in ("founders", "U", "D", "C"):
            R = [r for r in rows if r["fauna"] == kind and r["group"] == gname]
            if not R:
                continue
            w0 = np.array([r["r0"]["work_J"] for r in R]); w1 = np.array([r["r1"]["work_J"] for r in R]); w2 = np.array([r["r2"]["work_J"] for r in R])
            ex = [r["r0"]["exploded"] or r["r1"]["exploded"] or r["r2"]["exploded"] for r in R]
            ok = (w0 > 1.0) & ~np.array(ex)
            f = lambda key: np.mean([r["r0"][key] for r in R])  # noqa: E731
            print(f"\n{kind} {gname}: n={len(R)}  match registered {np.mean([abs(r['r0']['work_J'] - r['registered_work_J']) < 1e-6 * max(1, r['registered_work_J']) or r['r0']['exploded'] for r in R]):.2f}")
            print(f"  work kJ at dt 0.005: median {np.median(w0) / 1e3:.3f}  mean {w0.mean() / 1e3:.3f}  -> yield {0.03 * w0.mean() / 1e3:.3f}")
            if ok.any():
                print(f"  refinement ratio (work>1 J, none exploded; n={ok.sum()}): dt/2 median {np.median(w1[ok] / w0[ok]):.3f} [{np.min(w1[ok] / w0[ok]):.3f}, {np.max(w1[ok] / w0[ok]):.3f}]"
                      f"  dt/4 median {np.median(w2[ok] / w0[ok]):.3f} [{np.min(w2[ok] / w0[ok]):.3f}, {np.max(w2[ok] / w0[ok]):.3f}]")
            print(f"  |F.v| share: torque {f('frac_torque'):.2f} position {f('frac_pos'):.2f} velocity {f('frac_vel'):.2f};  negative {f('frac_neg'):.2f};  sign-flip substeps {f('frac_flip'):.2f};  torque at |ctrl|>0.98 {f('frac_sat'):.2f}")
            print(f"  max body speed m/s: median {np.median([r['r0']['vmax'] for r in R]):.2f} max {max(r['r0']['vmax'] for r in R):.2f};  deepest penetration mm {1e3 * min(r['r0']['pen'] for r in R):.1f};"
                  f"  joint-limit substeps {f('limit_frac'):.2f};  bad-QACC warnings {sum(r['r0']['badqacc'] for r in R)};  exploded {sum(ex)}/{len(R)}")
            print(f"  actuators {f('nu'):.1f}  bodies {f('nparts'):.1f}  mass {f('mass'):.2f} kg  sum of torque-motor gears {f('sum_gear'):.1f} (4 x mass = {4 * f('mass'):.1f})")
            cr = np.array([r["r0"]["work_J"] / r["r0"]["ceiling_J"] for r in R if r["r0"]["ceiling_J"] > 0])
            if len(cr):
                print(f"  work / full-throttle free-spin ceiling: median {np.median(cr):.2f} [{cr.min():.2f}, {cr.max():.2f}]; ceiling kJ median {np.median([r['r0']['ceiling_J'] for r in R]) / 1e3:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
