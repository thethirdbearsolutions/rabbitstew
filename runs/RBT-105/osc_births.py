"""RBT-105: the birth-level linked-oscillator rate of one arm, per 150-season block and over seasons 300-599 (R2's input).

The definition is the design adversary's probe (runs/RBT-105/adversary/probe_distinct.py, PR #154), unchanged:
  a birth is every holistic genome saved at birth that is not a founder (h0-*);
  its birth season is its first lineage.jsonl row's generation minus that row's age;
  it carries a linked oscillator if RBT-28's adversary_founders.wiring() gives osc_linked > 0 (RBT-84's instrument).

    python runs/RBT-105/osc_births.py RUN_DIR  > RUN_DIR/osc_births.txt

The last line is JSON: {"blocks": [[n, k], ...] for seasons 0-149, 150-299, 300-449, 450-599, "late_n", "late_k"}.
Reads the bulk; written by post_run.py while the bulk is here, and committed.
"""
import glob
import importlib.util
import json
import os
import pathlib
import sys

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("adv", ROOT / "runs" / "RBT-28" / "adversary_founders.py")
adv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adv)

LATE = (300, 600)  #: R2's window, [300, 600)


def main(run):
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    born = {}
    with open(os.path.join(run, "lineage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r.get("population") == "holistic" and r["name"] not in born:
                born[r["name"]] = r["generation"] - r.get("age", 0)
    blocks = [[0, 0] for _ in range(4)]
    late = [0, 0]
    for p in sorted(glob.glob(os.path.join(run, "holistic", "genomes", "*.json"))):
        name = pathlib.Path(p).stem
        if name.startswith("h0-"):
            continue
        s = max(0, born.get(name, 0))
        osc = int(adv.wiring(Genotype.load(p), cfg)["osc_linked"] > 0)
        blocks[min(3, s // 150)][0] += 1
        blocks[min(3, s // 150)][1] += osc
        if LATE[0] <= s < LATE[1]:
            late[0] += 1
            late[1] += osc
    print(f"{run} holistic births carrying a linked oscillator, per 150-season block (n births, k carrying, rate)")
    for i, (n, k) in enumerate(blocks):
        print(f"  seasons {150 * i:3d}-{150 * i + 149:3d}: n {n:4d} k {k:4d} rate {k / n if n else float('nan'):.3f}")
    print(f"  late {LATE[0]}-{LATE[1] - 1}: n {late[0]} k {late[1]} rate {late[1] / late[0] if late[0] else float('nan'):.3f}")
    print(json.dumps({"blocks": blocks, "late_n": late[0], "late_k": late[1]}))


if __name__ == "__main__":
    main(sys.argv[1])
