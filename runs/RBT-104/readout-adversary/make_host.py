"""RBT-104 readout adversary, POST HOC probe: a synthetic host for function.py.

Writes a scratch run directory holding the source run's config.json and its conventional bests at
the readout's seven gens (300-590), with every link weight of every brain multiplied by FACTOR
(rabbitstew.genetics.scale_links, the flag's own founder transform; biases untouched). function.py
is then pointed at the scratch directory unchanged.

  FACTOR 8    on an S1 arm: the S1 host at the S8 arm's link scale ("synthetic S8 host")
  FACTOR 0.125 on an S8 arm: the S8 host brought back to default link scale ("desaturated")

Never writes into runs/RBT-104/ARM-SEED; the output directory must be outside the arm directories.

With --plant W,BIAS (RBT-106 option H's question): after scaling, each best also gets RBT-97's routed
motif at output W, input +-1 (routed.install, as RBT-106's H founders carry it), with that unit's bias
then set to BIAS: an H host whose planted w = 32 unit's bias has walked away from 0. Its sign per best is
the one the source arm's committed function-pc.txt printed ("signs: g300 +1, ..."), so the planted
compass agrees with the install control function.py will sign by direction of travel on the bare host.

  make_host.py SRC_RUN OUT_DIR FACTOR [--plant W,BIAS SIGNS_FILE]
"""
import json
import os
import sys

from rabbitstew.genetics import scale_links
from rabbitstew.genotype import Genotype

_HERE = os.path.dirname(os.path.abspath(__file__))

GENS = (300, 350, 400, 450, 500, 550, 590)


def main():
    src, out, k = sys.argv[1], sys.argv[2], float(sys.argv[3])
    plant = None
    if "--plant" in sys.argv:
        plant = tuple(float(x) for x in sys.argv[sys.argv.index("--plant") + 1].split(","))
        import re
        sgn = {int(g): float(v) for g, v in re.findall(r"g(\d+) ([-+]1)", re.search(r"signs: (.*)", open(sys.argv[sys.argv.index("--plant") + 2]).read()).group(1))}
        import importlib.util
        spec = importlib.util.spec_from_file_location("rbt97_routed", os.path.join(os.path.dirname(os.path.dirname(_HERE)), "RBT-97", "routed_p801.py"))
        routed = importlib.util.module_from_spec(spec)
        sys.modules["rbt97_routed"] = routed
        spec.loader.exec_module(routed)
    assert "/runs/RBT-104/S" not in os.path.abspath(out), "refusing to write into an arm directory"
    os.makedirs(os.path.join(out, "conventional"), exist_ok=True)
    cfg = json.load(open(os.path.join(src, "config.json")))
    cfg.setdefault("adversary_probe", f"POST HOC synthetic host: {src} links x {k:g}")
    json.dump(cfg, open(os.path.join(out, "config.json"), "w"), indent=1)
    for gen in GENS:
        g = Genotype.load(os.path.join(src, "conventional", f"best_gen{gen:04d}.json"))
        scale_links(g, k)
        if plant:
            g = routed.install(g, plant[0], sign=sgn[gen])
            g.global_brain.units[-1].bias = plant[1]
        g.save(os.path.join(out, "conventional", f"best_gen{gen:04d}.json"))
    print(f"{out}: {src} bests {list(GENS)}, every link x {k:g}" + (f"; planted motif w = {plant[0]:g}, bias {plant[1]:g}" if plant else ""))


if __name__ == "__main__":
    main()
