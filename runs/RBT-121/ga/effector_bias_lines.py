"""RBT-121 audit B, probe 5b: did the selected lines use the bias walk?  Effector resting drive by line.

    python runs/RBT-121/ga/effector_bias_lines.py CKPT_ARM_DIR > runs/RBT-121/ga/effector_bias_lines.txt

CKPT_ARM_DIR is an RBT-113 arm restored from its checkpoint (e.g. O1 from `ckpt/rbt-113-O1`).  For every final member
of every line: the share of Effectors whose resting drive |tanh(bias)| > 0.9, and the mean |bias|.  Genotype only.
"""
import os
import sys

import numpy as np

from rabbitstew.genotype import Genotype


def main(arm):
    for kind in ("holistic", "conventional"):
        for line in "UDC":
            eb = []
            for seed in sorted(os.listdir(arm)):
                p = os.path.join(arm, seed, line, kind, "final")
                if not os.path.isdir(p):
                    continue
                for f in sorted(os.listdir(p)):
                    g = Genotype.load(os.path.join(p, f))
                    eb += [u.bias for _, b in g.brains() for u in b.units if u.kind == "effector"]
            eb = np.array(eb)
            print(f"{kind:12s} {line}: {len(eb):4d} effectors, mean |bias| {np.abs(eb).mean():.2f}, resting drive > 0.9: {np.mean(np.abs(np.tanh(eb)) > 0.9) * 100:5.1f}%")


if __name__ == "__main__":
    main(sys.argv[1])
