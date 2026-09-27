"""RBT-125 world gate, part B: a nose step against a +25% speed step, on real RBT-113 hosts (REGISTRATION.md §B).

Hosts: RBT-113's designed-body (Pioneer) U-line finals, arm O1, seeds 1-3, K = 5 per seed drawn by a fixed rng
(default_rng(125)) from the 40 finals of each: 15 hosts, restored from ckpt/rbt-113-O1 into HOSTS_ROOT (bulk, never
committed).  World: runs/RBT-125/gate/worlds/<cell> (RBT-90 part 2's world, which is RBT-113's, with the cell's food
block).  Every host carries RBT-97's routed motif at output weight w (linear gain a = 2w), signed per host by the
RBT-103 harness's two direction probes, which must agree (else the host is UNDETERMINED and leaves every arm).

Arms, per host, on the same 32 paired start seeds (125000..125031), each a 15 s solo season:
  w0     the host as it is
  w0.4   the first weak nose           (a 0 -> 0.8: each of the motif's two output links one weight sigma, 0.4)
  w1, w1.4    one step at a = 2 -> 2.8
  w3, w3.4    one step at a = 6 -> 6.8  (the gate's rung)
  speed  the host as it is with world.joint_damping / 1.25: the Pioneer's wheels are torque motors whose free-spin
         speed is gear / damping, so this raises the top wheel speed by 25% at the same torque.  The REALISED speed
         change is measured (centre-of-mass path per second) and printed; the step is read per its realised size.
Per host: mean items (and net: items - 0.03 x kJ) per season in each arm; the steps are paired differences.  Across
hosts: mean and Student t(n - 1) 95% interval.

    steps.py HOSTS_ROOT CELL [--procs 4]    -> stdout
"""
import argparse
import json
import os
import sys
from dataclasses import replace
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prize_gate  # noqa: E402  (the harness module, with the decoy patch; only its direction probe is used here)

rp = prize_gate.rp
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402

SEEDS = [125000 + i for i in range(32)]
WS = (0.0, 0.4, 1.0, 1.4, 3.0, 3.4)
SPEED = 1.25
K = 5
HOST = {}


def hosts(root):
    rng = np.random.default_rng(125)
    out = []
    for seed in (1, 2, 3):
        d = os.path.join(root, "O1", str(seed), "U", "conventional", "final")
        fs = sorted(os.listdir(d))
        for i in sorted(rng.choice(len(fs), K, replace=False)):
            out.append(os.path.join(d, fs[i]))
    return out


def bout(task):
    h, w, sign, seed, speed = task
    cfg = rp.RUN["cell"]
    if speed:
        cfg = replace(cfg, world=replace(cfg.world, joint_damping=cfg.world.joint_damping / SPEED))
    g = Genotype.load(HOST[h])
    if w:
        g = rp.routed.install(g, w, sign=sign)
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    path, last = 0.0, sim.center_of_mass(0)[:2].copy()
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
        now = sim.center_of_mass(0)[:2]
        path += float(np.linalg.norm(now - last))
        last = now.copy()
    h_ = sim.harvest(0)
    return (h, w, speed), seed, h_["food"], sim.food_score(0), path / cfg.duration


def t_int(x):
    from scipy import stats
    x = np.asarray(x, float)
    hw = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return x.mean(), x.mean() - hw, x.mean() + hw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hosts_root")
    ap.add_argument("cell")
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    cfg = SimConfig.from_dict(json.load(open(os.path.join(HERE, "worlds", a.cell, "config.json")))["sim"])
    rp.RUN["cell"] = cfg
    paths = hosts(a.hosts_root)
    HOST.update({i: p for i, p in enumerate(paths)})
    rp.genotype = lambda run, kind, gen: Genotype.load(HOST[gen])  # the harness's direction probe, on these hosts
    print(f"# RBT-125 gate B: nose step against +25% speed step, cell {a.cell}: {json.dumps(json.load(open(os.path.join(HERE, 'worlds', a.cell, 'config.json')))['sim']['food'])}")
    print(f"# hosts: {len(paths)} RBT-113 O1 U designed finals ({', '.join(os.path.relpath(p, a.hosts_root) for p in paths)})")
    with get_context("fork").Pool(a.procs) as pool:
        rows = pool.map(rp.direction_bout, [("cell", "conventional", h, i, k) for k in rp.g500.PROBES for h in HOST for i in range(16)], chunksize=4)
    by = {}
    for r in rows:
        by.setdefault((r[1], r[0]), []).append(r[2:])
    sign = {}
    for h in HOST:
        backs = []
        for k in rp.g500.PROBES:
            sn, cs, n = (sum(x[j] for x in by[(k, h)]) for j in range(3))
            backs.append(abs(np.degrees(np.arctan2(sn / n, cs / n))) > 90 if n else None)
        if backs[0] is not None and backs[0] == backs[1]:
            sign[h] = +1.0 if backs[0] == rp.mech.rs.PUBLISHED_IS_BACKWARD else -1.0
    und = [h for h in HOST if h not in sign]
    print(f"# direction: {len(sign)} signed, {len(und)} UNDETERMINED (out of every arm): {[os.path.relpath(HOST[h], a.hosts_root) for h in und]}")
    tasks = [(h, w, sign[h], s, False) for h in sign for w in WS for s in SEEDS] + [(h, 0.0, sign[h], s, True) for h in sign for s in SEEDS]
    with get_context("fork").Pool(a.procs) as pool:
        rows = pool.map(bout, tasks, chunksize=8)
    got = {(k, s): (f, net, v) for k, s, f, net, v in rows}
    arms = [(w, False) for w in WS] + [(0.0, True)]
    name = lambda w, sp: "speed" if sp else f"w{w:g}"
    print("\n| host | " + " | ".join(name(*arm) for arm in arms) + " | speed ratio (realised) |")
    print("|---|" + "---|" * (len(arms) + 1))
    M = {}
    for h in sign:
        M[h] = {arm: np.array([[got[((h, arm[0], arm[1]), s)][j] for s in SEEDS] for j in range(3)]) for arm in arms}
        ratio = M[h][(0.0, True)][2].mean() / max(M[h][(0.0, False)][2].mean(), 1e-9)
        print(f"| {os.path.relpath(HOST[h], a.hosts_root)} | " + " | ".join(f"{M[h][arm][0].mean():.3f}" for arm in arms) + f" | {ratio:.3f} |")
    steps = {"first nose (w 0 -> 0.4)": ((0.4, False), (0.0, False)), "nose step w 1 -> 1.4": ((1.4, False), (1.0, False)),
             "nose step w 3 -> 3.4": ((3.4, False), (3.0, False)), "+25% speed (damping / 1.25)": ((0.0, True), (0.0, False)),
             "installed a = 6 (w 3) - host": ((3.0, False), (0.0, False))}
    print(f"\n## steps across {len(sign)} hosts, per-host means over {len(SEEDS)} paired seeds; mean [t 95%]")
    print("| step | items | net (items - work) |")
    print("|---|---|---|")
    per = {}
    for label, (hi, lo) in steps.items():
        per[label] = [(M[h][hi][0] - M[h][lo][0]).mean() for h in sign]
        net = [(M[h][hi][1] - M[h][lo][1]).mean() for h in sign]
        m, l, u = t_int(per[label]); mn, ln, un = t_int(net)
        print(f"| {label} | {m:+.3f} [{l:+.3f}, {u:+.3f}] | {mn:+.3f} [{ln:+.3f}, {un:+.3f}] |")
    sr = [M[h][(0.0, True)][2].mean() / max(M[h][(0.0, False)][2].mean(), 1e-9) for h in sign]
    m, l, u = t_int(sr)
    print(f"\nrealised speed ratio of the speed arm: {m:.3f} [{l:.3f}, {u:.3f}]  (the registered step is 1.25)")
    spd = per["+25% speed (damping / 1.25)"]
    print("\n## nose step - speed step (items), paired per host: mean [t 95%] -> reading (REGISTRATION.md §B)")
    for label in ("first nose (w 0 -> 0.4)", "nose step w 1 -> 1.4", "nose step w 3 -> 3.4"):
        d = np.subtract(per[label], spd)
        m, l, u = t_int(d)
        nl = t_int(per[label])[1]
        reading = ("NOSE LEADS" if l > 0 else "SPEED LEADS" if u < 0 else "COMPARABLE" if nl > 0 else "TIED, NOSE STEP UNRESOLVED")
        print(f"STEP {a.cell} | {label:24s} | {m:+.3f} [{l:+.3f}, {u:+.3f}] | {reading}")


if __name__ == "__main__":
    main()
