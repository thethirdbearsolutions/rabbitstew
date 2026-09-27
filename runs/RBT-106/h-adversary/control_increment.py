"""RBT-106 H readout adversary, attack 3: is each HP install control's pass the INSTALLED compass, or only the host's own?

In HP the champion's own planted compass and the installed one add (RBT-104 readout adversary §5.2), so a control
could pass on the host's own F while the install itself is masked.  function-pc.txt (own world, --install 32) and the
arm's own-world function file score the same seven bests on the same 64 paired seeds (7000..7063), so per body the
increment F(pc) - F(own) is what the install adds.  t(6) over bodies; the install is DETECTED if the interval is above 0.

Usage: control_increment.py [RUNS_DIR]
"""
import math
import os
import re
import sys

D = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T6 = 2.446912   # t(0.975; 6), from rederive.py's own quantile


def per_body(path):
    return {int(m[1]): float(m[2]) for m in re.finditer(r"^g(\d+)\s+\S+\s+\S+\s+\S+ \|\s+([+-][\d.]+)", open(path).read(), re.M)}


print("| arm | own F per body mean | control F per body mean | increment [95% t(6)] | install detected |\n|---|---|---|---|---|")
for arm in ("HU", "HP"):
    for s in (801, 4, 804, 805, 806, 807, 1, 2, 3, 7):
        own = per_body(os.path.join(D, f"{arm}-{s}", f"function-{'patchy' if arm == 'HP' else 'uniform'}.txt"))
        pc = per_body(os.path.join(D, f"{arm}-{s}", "function-pc.txt"))
        d = [pc[g] - own[g] for g in sorted(pc)]
        m = sum(d) / len(d)
        h = T6 * math.sqrt(sum((x - m) ** 2 for x in d) / (len(d) - 1)) / math.sqrt(len(d))
        print(f"| {arm}-{s} | {sum(own.values()) / len(own):+.3f} | {sum(pc.values()) / len(pc):+.3f} | {m:+.3f} [{m - h:+.3f}, {m + h:+.3f}] | {m - h > 0} |")
