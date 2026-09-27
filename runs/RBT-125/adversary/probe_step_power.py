"""RBT-125 adversary probe: the power of §B (a nose step against a +25% speed step) at its registered n.

§B's hosts (RBT-113 O1 finals) are not in the repo, so this uses committed Pioneers of the same design
(runs/RBT-19/P-801/conventional best_gen 0, 200, 300, 400, 500, 590; RBT-97's bodies) as stand-ins, in the registered
PW-G2.5 world, with steps.py's own bout() (same arms, same damping step, same seeds 125000..125031).  Signs are those
the RBT-103 harness gave these bodies in PW-G2.5 (all -1, runs/RBT-125/adversary/p801_PW-G2.5.txt).

Printed: per body, the paired per-season SD of each step, the per-host SE at 32 seeds, and the realised speed ratio;
then the implied t(14) 95% half-width for 15 hosts (per-host SE and the between-host SD of the step means combined)
and the power to read the registered line's nose-step lower bound > 0 at the kinematic expectation (+0.17).

    python runs/RBT-125/adversary/probe_step_power.py
"""
import json
import os
import sys
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "runs/RBT-125/gate"))
import steps  # noqa: E402
from scipy import stats  # noqa: E402

from rabbitstew.simulation import SimConfig  # noqa: E402

GENS = (0, 200, 300, 400, 500, 590)


def main():
    cfg = SimConfig.from_dict(json.load(open(os.path.join(ROOT, "runs/RBT-125/gate/worlds/PW-G2.5/config.json")))["sim"])
    steps.rp.RUN["cell"] = cfg
    steps.HOST.update({g: os.path.join(ROOT, f"runs/RBT-19/P-801/conventional/best_gen{g:04d}.json") for g in GENS})
    arms = [(3.0, False), (3.4, False), (0.0, False), (0.0, True)]
    tasks = [(g, w, -1.0, s, sp) for g in GENS for (w, sp) in arms for s in steps.SEEDS]
    with get_context("fork").Pool(4) as pool:
        rows = pool.map(steps.bout, tasks, chunksize=8)
    got = {(k, s): (f, v) for k, s, f, net, v in rows}
    X = lambda g, w, sp: np.array([got[((g, w, sp), s)][0] for s in steps.SEEDS])
    Vv = lambda g, w, sp: np.array([got[((g, w, sp), s)][1] for s in steps.SEEDS])
    print("| body | w3 items | nose step w3->3.4 mean (sd) | speed step mean (sd) | nose - speed sd | realised speed ratio | zero pairs w3/w3.4 |")
    print("|---|---|---|---|---|---|---|")
    ns, sp, sd_n, sd_d = [], [], [], []
    for g in GENS:
        n = X(g, 3.4, False) - X(g, 3.0, False)
        s = X(g, 0.0, True) - X(g, 0.0, False)
        ns.append(n.mean()); sp.append(s.mean()); sd_n.append(n.std(ddof=1)); sd_d.append((n - s).std(ddof=1))
        r = Vv(g, 0.0, True).mean() / Vv(g, 0.0, False).mean()
        z = int(np.sum(n == 0))
        print(f"| g{g} | {X(g, 3.0, False).mean():.3f} | {n.mean():+.3f} ({n.std(ddof=1):.3f}) | {s.mean():+.3f} ({s.std(ddof=1):.3f}) | "
              f"{(n - s).std(ddof=1):.3f} | {r:.3f} | {z}/{len(n)} |")
    k, m = 15, len(steps.SEEDS)
    for label, sd_seed, means in (("nose step", np.mean(sd_n), ns), ("nose - speed", np.mean(sd_d), np.subtract(ns, sp))):
        se_host = sd_seed / np.sqrt(m)
        sd_between = np.sqrt(max(np.var(means, ddof=1) - se_host ** 2, 0.0))
        sd_host_mean = np.sqrt(se_host ** 2 + sd_between ** 2)
        hw = stats.t.ppf(0.975, k - 1) * sd_host_mean / np.sqrt(k)
        print(f"\n{label}: per-season sd {sd_seed:.3f}; per-host SE at {m} seeds {se_host:.3f}; between-host sd {sd_between:.3f}; "
              f"t({k - 1}) 95% half-width at {k} hosts ~ {hw:.3f}")
        if label == "nose step":
            eff = 0.17
            ncp = eff / (sd_host_mean / np.sqrt(k))
            pw = 1 - stats.nct.cdf(stats.t.ppf(0.975, k - 1), k - 1, ncp)
            need = (stats.norm.ppf(0.975) + stats.norm.ppf(0.8)) ** 2 * sd_host_mean ** 2 / eff ** 2
            print(f"  power for the nose step's lower bound > 0 at a true +{eff}: {pw:.2f}; hosts x 32 seeds for 80%: ~{need:.0f} hosts "
                  f"(or ~{need * m / k:.0f} seeds per host at 15 hosts if between-host sd is small)")


if __name__ == "__main__":
    main()
