"""RBT-129 legs-readout adversary: how much do exploded seasons drive r@w3, per host, at a cell?  (Diagnostic; not a
registered treatment.)

For every signed host of CELL, re-runs the w3 base arm and the w3 speed arm on the steps leg's 128 paired seeds with
29ab80b's steps.py and config (sign from the two direction probes, as steps.main).  Prints per host: the committed-
table r (to check reproduction), the number of exploded seasons per arm, r over the seed pairs where neither arm
exploded, and whether each r crosses the registered 1.10 exclusion.  Then the A1.4 line recomputed with the
explosion-free r (items per arm still from the committed per-host table, i.e. over all 128 seeds), beside the
registered STEP row.  This is a DIAGNOSTIC of the registered rule's input, not a replacement for it.

    python probe_r_clean.py TREE_29ab80b HOSTS_ROOT PAYS_DIR CELL
"""
import os, sys
import numpy as np
sys.argv, (T, H, P, CELL) = sys.argv[:1], [os.path.abspath(a) if i < 3 else a for i, a in enumerate(sys.argv[1:5])]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_r_outlier as po  # noqa: E402  (same season(); its module-level imports use T)
import rederive as rd  # noqa: E402  (the per-host-table parser, reading() and ci())
from multiprocessing import get_context  # noqa: E402
import json  # noqa: E402


def main():
    rows, st = rd.steps_table(os.path.join(P, f"{CELL}-steps", "steps", "designed.txt"))
    po.rp.RUN["cell"] = po.SimConfig.from_dict(json.load(open(os.path.join(T, "runs/RBT-129/worlds/config", CELL, "config.json")))["sim"])
    hosts = sorted(rows)
    po.steps.HOST.update({i: os.path.join(H, h) for i, h in enumerate(hosts)})
    po.rp.genotype = lambda run, kind, gen: po.Genotype.load(po.steps.HOST[gen])
    with get_context("fork").Pool(4) as pool:
        d = pool.map(po.rp.direction_bout, [("cell", "conventional", i, j, k) for k in po.rp.g500.PROBES for i in range(len(hosts)) for j in range(16)])
    sign = {}
    for i in range(len(hosts)):
        backs = []
        for k in po.rp.g500.PROBES:
            sn = sum(r[2] for r in d if r[0] == i and r[1] == k); cs = sum(r[3] for r in d if r[0] == i and r[1] == k); n = sum(r[4] for r in d if r[0] == i and r[1] == k)
            backs.append(abs(np.degrees(np.arctan2(sn / n, cs / n))) > 90 if n else None)
        if backs[0] is not None and backs[0] == backs[1]:
            sign[i] = +1.0 if backs[0] == po.rp.mech.rs.PUBLISHED_IS_BACKWARD else -1.0
    assert len(sign) == len(hosts), f"signed {len(sign)} of {len(hosts)} (the committed table has {len(hosts)})"
    res = {}
    for i, h in enumerate(hosts):
        po.HOST = po.steps.HOST[i]
        with get_context("fork").Pool(4) as pool:
            out = pool.map(po.season, [(3.0, sign[i], s, sp) for sp in (False, True) for s in po.steps.SEEDS], chunksize=4)
        vb = np.array([o[3] for o in out if not o[0][1]]); vs = np.array([o[3] for o in out if o[0][1]])
        xb = np.array([o[4] for o in out if not o[0][1]]); xs = np.array([o[4] for o in out if o[0][1]])
        ib = np.mean([o[2] for o in out if not o[0][1]]); isp = np.mean([o[2] for o in out if o[0][1]])
        keep = ~(xb | xs)
        res[h] = dict(r=vs.mean() / vb.mean(), rc=vs[keep].mean() / vb[keep].mean(), xb=int(xb.sum()), xs=int(xs.sum()), ib=ib, isp=isp)
    print(f"# {CELL}: per host, w3 and speed@w3 re-run (128 seeds, 29ab80b); r = mean path/s ratio; r_clean over seed pairs with no explosion in either arm")
    print("| host | table r | re-run r | items w3 / speed@w3 (table; re-run) | exploded base/speed | r_clean | registered in? | clean in? |")
    print("|---|---|---|---|---|---|---|---|")
    for h in hosts:
        v, t = res[h], rows[h]
        print(f"| {h.split('final/')[0].split('/')[1]}/{h.split('/')[-1][:3]} | {t['r@w3']:.3f} | {v['r']:.3f} | {t['w3']:.3f}/{t['speed@w3']:.3f}; {v['ib']:.3f}/{v['isp']:.3f} | "
              f"{v['xb']}/{v['xs']} | {v['rc']:.3f} | {'yes' if t['r@w3'] >= 1.10 else 'no'} | {'yes' if v['rc'] >= 1.10 else 'no'} |")
    nose = {h: rows[h]["w3.4"] - rows[h]["w3"] for h in hosts}
    inc = [h for h in hosts if res[h]["rc"] >= 1.10]
    dd = [nose[h] - (rows[h]["speed@w3"] - rows[h]["w3"]) * 0.25 / (res[h]["rc"] - 1.0) for h in inc]
    m, lo, hi = rd.ci(dd)
    print(f"\nregistered STEP (per-unit, n {st['n']}): {st['pu_ci'][0]:+.3f} [{st['pu_ci'][1]:+.3f}, {st['pu_ci'][2]:+.3f}] {st['pu']}")
    print(f"with explosion-free r (diagnostic, n {len(dd)}): {m:+.3f} [{lo:+.3f}, {hi:+.3f}] {rd.reading(dd)}")


if __name__ == "__main__":
    main()
