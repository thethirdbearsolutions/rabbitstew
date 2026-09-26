"""RBT-99 (C2): the mechanical price per seed and fauna, from the baseline's own pre-onset seasons.

C2 lowers every individual's season gain by exactly 0.05 x its kJ (simulation.py food_gain), so part of
any C2 R-shift is arithmetic, not response.  This prints that part from the population C2 shocks, before
any RBT-99 arm has ended (RBT-99 adversary F4; PREREGISTRATION.md Amendment 1):

    kJ     mean actuator work per individual-season (lineage "work", J / 1000) over [T - 40, T) of the
           seed's RBT-90 part 2 arm; every season read is before T, so it is the same in every arm
    price  0.05 x kJ: what the shift takes from that fauna's mean income on day one if nobody changes

Reads the baselines' bulk (lineage.jsonl, restored with scripts/durable.sh restore BULKDIR/forage-SEED
rbt-90-SEED) and T from runs/RBT-92/onset.txt.  Its output is committed, so the readout needs no bulk.

    python runs/RBT-99/price.py BULKDIR > runs/RBT-99/price.txt
"""
import json
import os
import statistics as st
import sys

EXTRA = 0.05
KINDS = ("holistic", "conventional")
ONSET = os.environ.get("RBT92_ONSET", "runs/RBT-92/onset.txt")


def onsets():
    out = {}
    for line in open(ONSET):
        f = line.rstrip("\n").split("\t")
        if f[0].lstrip("-").isdigit() and len(f) > 1 and f[1].isdigit():
            out[int(f[0])] = int(f[1])
    return out


def main(bulk):
    print(__doc__.split("\n\n")[0])
    print("seed\tfauna\tT\twindow\trows\tkJ\tprice")
    for seed, T in onsets().items():
        kj = {k: [] for k in KINDS}
        for line in open(os.path.join(bulk, f"forage-{seed}", "lineage.jsonl")):
            r = json.loads(line)
            if T - 40 <= r["generation"] < T and "work" in r and r.get("death") != "cull":
                kj[r["population"]].append(r["work"] / 1000)
        for k in KINDS:
            m = st.fmean(kj[k]) if kj[k] else float("nan")
            print(f"{seed}\t{k}\t{T}\t{T - 40}-{T - 1}\t{len(kj[k])}\t{m:.3f}\t{EXTRA * m:.4f}")


if __name__ == "__main__":
    main(sys.argv[1])
