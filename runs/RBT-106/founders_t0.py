"""RBT-106: the seeded founders at t = 0, in both worlds (PREREGISTRATION.md section 3.3).

What selection sees in season 0: for each of a seed's 30 planted founders, three genotypes,

  U    the bare part-2 founder (its twin)
  S1   RBT-104's planted founder, motif at w = 1 (a = 2)            -- the P1 arm's founders
  H    the same founder with the motif at w = 32 (a = 64), same sign -- the H arms' founders

each scored by RBT-103's `income_bout` (imported through the RBT-104 adversary's `founders_t0.py`,
whose `bout` is used unchanged), on SEEDS paired seeds from 7000, under real smell and under
RBT-97's rotated decoy, in two worlds that differ in `sim.food.patches` alone:

  uniform  RBT-90 part 2's world (runs/RBT-90/forage-801/config.json)
  patchy   the same with patches = 3 (runs/RBT-106/world-patchy/config.json)

Reported per world, t over the 30 founders:
  cost      X - U under real smell (income the seed adds or costs at founding)
  F(X)-F(U) the planted compass's own food dependence: (real - decoy) of X minus that of U
and for H also split by whether the planted sign is the compass sign for the founder's direction
of travel (RBT-97's two direction probes on the bare founder, RBT-104 function.py's signing rule),
because a founder drives whichever way its random gait takes it and half the plants are
anti-compasses for their host.

Usage: founders_t0.py SEED [--seeds 16] [--procs 4]
"""
import argparse
import importlib.util
import os
import platform
import sys
from multiprocessing import get_context

import mujoco
import numpy as np
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ft0 = _load("rbt104_founders_t0", os.path.join(_ROOT, "runs", "RBT-104", "adversary", "founders_t0.py"))
fd = _load("rbt106_founders", os.path.join(_HERE, "founders.py"))
rp, sf = ft0.rp, ft0.sf
g500, mech = rp.g500, rp.mech

from rabbitstew.evolution import CONVENTIONAL  # noqa: E402

WORLDS = {"uniform": os.path.join(_ROOT, "runs", "RBT-90", "forage-801"),
          "patchy": os.path.join(_HERE, "world-patchy")}
DIR = {}  # i -> +1/-1 compass sign for the bare founder's direction of travel, or absent


def bout(task):
    world, i, cond, seed, decoy = task
    ft0.RUN = WORLDS[world]
    return (world,) + ft0.bout((i, cond, seed, decoy))


def direction(task):
    i, k, j = task
    orig = rp.genotype
    rp.genotype = lambda run_, kind_, gen_: ft0.BODY[(gen_, "U")]
    try:
        return rp.direction_bout((WORLDS["uniform"], "conventional", i, j, k))
    finally:
        rp.genotype = orig


def t_int(v):
    v = np.asarray(v, float)
    se = v.std(ddof=1) / np.sqrt(len(v))
    t = float(stats.t.ppf(0.975, len(v) - 1))
    return v.mean(), v.mean() - t * se, v.mean() + t * se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", type=int)
    ap.add_argument("--seeds", type=int, default=16)
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    for w, d in WORLDS.items():
        rp.RUN[d] = rp.config(d)
    assert rp.RUN[WORLDS["patchy"]].food.patches == 3 and rp.RUN[WORLDS["uniform"]].food.patches == 0
    e = sf.part2_ecology(a.seed)
    bare = [g.copy() for g in e.populations[CONVENTIONAL]]
    e.runner.close()
    s1, h = fd.seeded(a.seed, 1.0), fd.seeded(a.seed, 32.0)
    planted = [i for i in range(len(bare)) if i % 2 == 0]
    for i in planted:
        ft0.BODY[(i, "U")], ft0.BODY[(i, "S1")], ft0.BODY[(i, "H")] = bare[i], s1[i], h[i]

    with get_context("fork").Pool(a.procs) as pool:
        drows = pool.map(direction, [(i, k, j) for i in planted for k in g500.PROBES for j in range(16)], chunksize=8)
    by = {}
    for gen, probe, sn, cs, n in drows:
        by.setdefault((gen, probe), []).append((sn, cs, n))
    for i in planted:
        backs = []
        for k in g500.PROBES:
            sn = sum(x[0] for x in by[(i, k)]); cs = sum(x[1] for x in by[(i, k)]); n = sum(x[2] for x in by[(i, k)])
            backs.append(abs(float(np.degrees(np.arctan2(sn / n, cs / n)))) > 90 if n else None)
        if backs[0] is not None and backs[0] == backs[1]:
            DIR[i] = +1.0 if backs[0] == mech.rs.PUBLISHED_IS_BACKWARD else -1.0

    seeds = [7000 + j for j in range(a.seeds)]
    tasks = [(w, i, c, s, d) for w in WORLDS for i in planted for c in ("U", "S1", "H") for s in seeds for d in (False, True)]
    with get_context("fork").Pool(a.procs) as pool:
        rows = pool.map(bout, tasks, chunksize=8)
    got = {(w, i, c, d, s): v for w, i, c, d, s, v, _ in rows}
    blew = sum(1 for *_, x in rows if x)
    m = lambda w, i, c, d: float(np.mean([got[(w, i, c, d, s)] for s in seeds]))
    cost = lambda w, i, c: m(w, i, c, False) - m(w, i, "U", False)
    fdep = lambda w, i, c: (m(w, i, c, False) - m(w, i, c, True)) - (m(w, i, "U", False) - m(w, i, "U", True))
    fmt = lambda x: f"{x[0]:+.3f} [{x[1]:+.3f}, {x[2]:+.3f}]"
    sgn = {i: (+1.0 if i % 4 == 0 else -1.0) for i in planted}
    right = [i for i in planted if i in DIR and DIR[i] == sgn[i]]
    wrong = [i for i in planted if i in DIR and DIR[i] != sgn[i]]

    print(f"# RBT-106: the seeded founders at t = 0 in both worlds, seed {a.seed}\n")
    print(f"platform {platform.machine()}, MuJoCo {mujoco.__version__}; {len(planted)} planted founders, each against "
          f"its bare twin; {a.seeds} paired seeds from 7000; RBT-103's income_bout; exploded bouts {blew}/{len(rows)}")
    print(f"direction of travel (bare founder, two probes agree): {len(DIR)}/{len(planted)} determined; "
          f"the planted sign is the compass sign on {len(right)}, the anti-compass on {len(wrong)}\n")
    print("| quantity (items per bout; t over founders) | uniform | patchy |")
    print("|---|---|---|")
    lines = [
        ("bare founder income", lambda w, i: m(w, i, "U", False), planted),
        ("S1 (w = 1) cost: S1 - U", lambda w, i: cost(w, i, "S1"), planted),
        ("S1 food dependence: F(S1) - F(U)", lambda w, i: fdep(w, i, "S1"), planted),
        ("H (w = 32) cost: H - U, all 30", lambda w, i: cost(w, i, "H"), planted),
        ("H food dependence: F(H) - F(U), all 30", lambda w, i: fdep(w, i, "H"), planted),
        (f"H cost, compass-signed ({len(right)})", lambda w, i: cost(w, i, "H"), right),
        (f"H F(H) - F(U), compass-signed ({len(right)})", lambda w, i: fdep(w, i, "H"), right),
        (f"H cost, anti-signed ({len(wrong)})", lambda w, i: cost(w, i, "H"), wrong),
        (f"H F(H) - F(U), anti-signed ({len(wrong)})", lambda w, i: fdep(w, i, "H"), wrong),
    ]
    for name, f, idx in lines:
        if len(idx) < 2:
            print(f"| {name} | n < 2 | n < 2 |")
            continue
        print(f"| {name} | {fmt(t_int([f('uniform', i) for i in idx]))} | {fmt(t_int([f('patchy', i) for i in idx]))} |")
    for name, c, idx in (("S1", "S1", planted), ("H", "H", planted), ("H compass-signed", "H", right)):
        if len(idx) >= 2:
            print(f"patchy - uniform, {name} cost: {fmt(t_int([cost('patchy', i, c) - cost('uniform', i, c) for i in idx]))}")
    print("\nROW " + " ".join(f"{w}:{c}:{k}={v:+.4f}" for w in WORLDS for c in ("S1", "H") for k, v in (
        ("cost", float(np.mean([cost(w, i, c) for i in planted]))),
        ("F", float(np.mean([fdep(w, i, c) for i in planted]))),
        ("cost_right", float(np.mean([cost(w, i, c) for i in right])) if right else float("nan")),
        ("F_right", float(np.mean([fdep(w, i, c) for i in right])) if right else float("nan")))))


if __name__ == "__main__":
    main()
