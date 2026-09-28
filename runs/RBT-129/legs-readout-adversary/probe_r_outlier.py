"""RBT-129 legs-readout adversary: what produces an r@w3 of 943 (c2-p030-HP-L, host O1/1/U/.../016)?

Re-runs that host's w3 base arm and w3 speed arm (joint damping / 1.25) on the steps leg's 128 paired seeds
(125000..125127), with steps.py at 29ab80b (the legs' pinned tool) and the cell's config at 29ab80b, the host from
ckpt/rbt-113-O1.  The sign comes from the harness's two direction probes, exactly as steps.main computes it.
Per season it records items, the centre-of-mass path per second (steps.bout's r ingredient), and sim.exploded.
Checks first that the per-arm mean items reproduce the committed table row (w3 1.469, speed@w3 1.711, r 943.448).

    python probe_r_outlier.py TREE_29ab80b HOSTS_ROOT
"""
import json, os, sys
from dataclasses import replace
from multiprocessing import get_context
import numpy as np
T, H = (os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])) if __name__ == "__main__" else (os.environ["RT_TREE"], os.environ["RT_HOSTS"])
sys.path.insert(0, T); sys.path.insert(0, os.path.join(T, "runs/RBT-125/gate"))
import steps  # noqa: E402  (29ab80b's; imports prize_gate and the RBT-97 chain from that tree)
import rabbitstew  # noqa: E402
assert rabbitstew.__file__.startswith(T), rabbitstew.__file__
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402
CELL = "c2-p030-HP-L"
HOST = os.path.join(H, "O1/1/U/conventional/final/016.json")
rp = steps.rp


def season(task):
    w, sign, seed, speed = task
    cfg = rp.RUN["cell"]
    if speed:
        cfg = replace(cfg, world=replace(cfg.world, joint_damping=cfg.world.joint_damping / steps.SPEED))
    g = rp.routed.install(Genotype.load(HOST), w, sign=sign)
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    path, last, first_x = 0.0, sim.center_of_mass(0)[:2].copy(), None
    for t in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
        now = sim.center_of_mass(0)[:2]
        path += float(np.linalg.norm(now - last))
        last = now.copy()
        if sim.exploded[0] and first_x is None:
            first_x = t
    return (w, speed), seed, sim.harvest(0)["food"], path / cfg.duration, bool(sim.exploded[0]), first_x


def main():
    raw = json.load(open(os.path.join(T, "runs/RBT-129/worlds/config", CELL, "config.json")))
    rp.RUN["cell"] = SimConfig.from_dict(raw["sim"])
    steps.HOST.update({0: HOST})
    rp.genotype = lambda run, kind, gen: Genotype.load(steps.HOST[gen])
    with get_context("fork").Pool(4) as pool:
        rows = pool.map(rp.direction_bout, [("cell", "conventional", 0, i, k) for k in rp.g500.PROBES for i in range(16)])
    backs = []
    for k in rp.g500.PROBES:
        sn = sum(r[2] for r in rows if r[1] == k); cs = sum(r[3] for r in rows if r[1] == k); n = sum(r[4] for r in rows if r[1] == k)
        backs.append(abs(np.degrees(np.arctan2(sn / n, cs / n))) > 90 if n else None)
    assert backs[0] is not None and backs[0] == backs[1], backs
    sign = +1.0 if backs[0] == rp.mech.rs.PUBLISHED_IS_BACKWARD else -1.0
    seeds = steps.SEEDS
    tasks = [(3.0, sign, s, sp) for sp in (False, True) for s in seeds]
    with get_context("fork").Pool(4) as pool:
        out = pool.map(season, tasks, chunksize=4)
    print(f"# {CELL}, host O1/1/U/conventional/final/016.json, sign {sign:+.0f}, {len(seeds)} seeds from {seeds[0]}; steps.py and config at 29ab80b")
    for sp in (False, True):
        R = [o for o in out if o[0] == (3.0, sp)]
        it = np.array([o[2] for o in R]); v = np.array([o[3] for o in R]); x = [o for o in R if o[4]]
        big = sorted(R, key=lambda o: -o[3])[:3]
        print(f"arm {'speed@w3' if sp else 'w3      '}: mean items {it.mean():.3f}; mean path/s {v.mean():.4g}; median path/s {np.median(v):.4g}; "
              f"exploded seasons {len(x)}; top path/s seasons: " + ", ".join(f"seed {o[1]} {o[3]:.4g} m/s (exploded {o[4]}, tick {o[5]})" for o in big))
    vb = np.array([o[3] for o in out if o[0] == (3.0, False)]); vs = np.array([o[3] for o in out if o[0] == (3.0, True)])
    xb = np.array([o[4] for o in out if o[0] == (3.0, False)]); xs = np.array([o[4] for o in out if o[0] == (3.0, True)])
    print(f"r = mean(speed) / mean(base) = {vs.mean() / vb.mean():.3f}   (committed table: 943.448)")
    keep = ~(xb | xs)
    print(f"r over the {keep.sum()} seed pairs where neither arm exploded: {vs[keep].mean() / vb[keep].mean():.3f};  "
          f"r of medians: {np.median(vs) / np.median(vb):.3f}")


if __name__ == "__main__":
    main()
