"""RBT-107 design adversary: re-run probe_refund.py's C0 refund for ONE seed and fauna exactly as that script does it
(its alive(), its draws, its shuffle, its run_group task, the run's own config), to locate the gap between its C0 refund
and the garden's Delta0.  Only the pre-onset (C0) population of the no-event base arm is read.

    python runs/RBT-107/adversary/probe_refund_c0.py BULK_BASE_DIR SEED KIND
"""
import importlib.util
import os
import random
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
INTEG = os.environ.get("PROBE_REFUND", os.path.join(ROOT, "runs", "RBT-101", "readout-adversary", "probe_refund.py"))
spec = importlib.util.spec_from_file_location("pr", INTEG)
PR = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PR)


def main(run, seed, kind):
    import json
    T = PR.TS[seed]
    cfgd = json.load(open(f"{run}/config.json"))["sim"]
    rnd = random.Random(f"RBT-101 refund {seed}")
    draws = [rnd.randrange(1, 2**31 - 1) for _ in range(4)]
    names = PR.alive(run, kind, T - 1)
    print(f"seed {seed} {kind}: C0 as probe_refund defines it (played season T-1 = {T - 1}): n = {len(names)}")
    acc = {"random": [], "flat": []}
    accf = {"random": [], "flat": []}
    per = []
    for d, sd in enumerate(draws):
        order = names[:]
        random.Random(f"{seed} C0 {kind} {d}").shuffle(order)
        g, full, part = {}, {}, {}
        for terrain in ("random", "flat"):
            v, vf, vp = [], [], []
            for gi in range(0, len(order), 4):
                out = PR.task((run, kind, order[gi:gi + 4], cfgd, terrain, sd))
                v += out
                (vf if len(out) == 4 else vp).extend(out)
            g[terrain], full[terrain], part[terrain] = v, vf, vp
            acc[terrain] += v
            accf[terrain] += vf
        per.append(st.fmean(g["flat"]) - st.fmean(g["random"]))
        pf = (f"; the short group of {len(part['flat'])}: random {st.fmean(part['random']):+.3f} flat {st.fmean(part['flat']):+.3f}"
              if part["flat"] else "")
        print(f"draw {d} seed {sd}: flat - random {per[-1]:+.4f}, full groups only {st.fmean(full['flat']) - st.fmean(full['random']):+.4f}"
              f" (full-group means random {st.fmean(full['random']):+.3f} flat {st.fmean(full['flat']):+.3f}){pf}", flush=True)
    print(f"C0 REFUND (probe_refund's way) seed {seed} {kind}: {st.fmean(acc['flat']) - st.fmean(acc['random']):+.4f}; "
          f"full groups of four only {st.fmean(accf['flat']) - st.fmean(accf['random']):+.4f}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
