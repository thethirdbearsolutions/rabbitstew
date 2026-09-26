"""RBT-106 §3.3: the factorial's four cells at t = 0, pooled over the ten seeds.

Uniform: RBT-104's `t0_pool.read` (imported), which reads RBT-104's committed founders_t0 readouts.
Patchy: `t0/patchy-t0-SEED.txt` (t0_patchy.py: the same adversary script, unchanged, in the patchy world),
parsed with RBT-104 t0_pool's own row patterns.  Printed per seed and with t(9) over seeds: the seed's cost
(seeded - bare) and the planted compass's own food dependence (F seeded - F bare), at K = 1 and K = 8, in each
world, and patchy - uniform.
"""
import importlib.util
import os
import re

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
_s = importlib.util.spec_from_file_location("rbt104_t0_pool", os.path.join(ROOT, "runs", "RBT-104", "t0_pool.py"))
tp = importlib.util.module_from_spec(_s)
_s.loader.exec_module(tp)


def patchy(seed):
    txt = open(os.path.join(HERE, "t0", f"patchy-t0-{seed}.txt")).read()
    out = {}
    for key, lab in tp.ROWS.items():
        m = re.search(rf"^\| {lab}\s*\| {tp.num} \| {tp.num} \|", txt, re.M)
        out[key] = (float(m.group(1)), float(m.group(4)))
    return out


def t_int(x):
    x = np.asarray(x, float)
    h = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return f"{x.mean():+.3f} [{x.mean() - h:+.3f}, {x.mean() + h:+.3f}]"


def main():
    seeds = [s for s in tp.SEEDS if os.path.exists(os.path.join(HERE, "t0", f"patchy-t0-{s}.txt"))]
    print(f"# RBT-106: the seeded founders (w = 1) at t = 0, both worlds, K = 1 and 8; seeds {seeds}\n")
    print("| seed | cost K1 uniform | cost K1 patchy | F K1 uniform | F K1 patchy | cost K8 uniform | cost K8 patchy | F K8 uniform | F K8 patchy |")
    print("|---|---|---|---|---|---|---|---|---|")
    col = {k: [] for k in ("cu1", "cp1", "fu1", "fp1", "cu8", "cp8", "fu8", "fp8")}
    for s in seeds:
        u, p = tp.read(s), patchy(s)
        vals = dict(cu1=u["cost"][0], cp1=p["cost"][0], fu1=u["F"][0], fp1=p["F"][0],
                    cu8=u["cost"][1], cp8=p["cost"][1], fu8=u["F"][1], fp8=p["F"][1])
        for k, v in vals.items():
            col[k].append(v)
        print(f"| {s} | " + " | ".join(f"{vals[k]:+.3f}" for k in col) + " |")
    if len(seeds) < 2:
        return
    print(f"\nt({len(seeds) - 1}) over seeds (items per bout):")
    for name, k in (("cost, K = 1, uniform", "cu1"), ("cost, K = 1, patchy", "cp1"), ("F seeded - F bare, K = 1, uniform", "fu1"),
                    ("F seeded - F bare, K = 1, patchy", "fp1"), ("cost, K = 8, uniform", "cu8"), ("cost, K = 8, patchy", "cp8"),
                    ("F seeded - F bare, K = 8, uniform", "fu8"), ("F seeded - F bare, K = 8, patchy", "fp8")):
        print(f"  {name:36s} {t_int(col[k])}")
    for name, a, b in (("patchy - uniform, F at K = 1", "fp1", "fu1"), ("patchy - uniform, F at K = 8", "fp8", "fu8"),
                       ("patchy - uniform, cost at K = 8", "cp8", "cu8")):
        print(f"  {name:36s} {t_int(np.subtract(col[a], col[b]))}")


if __name__ == "__main__":
    main()
