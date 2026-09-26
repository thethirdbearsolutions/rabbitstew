"""RBT-101 (C4, flat terrain): the posture-wiring digest, one row per individual, from its genome at birth.

    python runs/RBT-101/wiring.py ARM_DIR [--to DIR]      ->  ARM_DIR/wiring.txt (or DIR/wiring.txt)

C4 is the one challenge in RBT-89's set that the robots can perceive with the wiring they carry: obstacles
reach the brain through contact, height, up and the joint sensors (docs/held-out-challenges.md section 2 C4,
section 3).  The re-wiring readout (rewire.py) asks whether the use of those sensors changed across the
onset.  It needs, per individual, how strongly its posture sensors drive anything that moves, and this
writes it, the same way RBT-92's tables.py writes bodysig.txt: from each genome at birth, so the readout
reads committed text and never the bulk.

Per individual, with rabbitstew.analysis.signed_influence (RBT-63) on its phenotype, over the pairs
(posture sensor s, live effector e), POSTURE = contact, height, up (all three axes), joint_angle,
joint_velocity:

  g1   sum over pairs of |gain| at depth 1: the direct links, exact (a "direct" link is a two-tick path,
       RBT-66's architectural fact).
  g2   sum over pairs of |gain| of the path sum to depth 2 (direct plus routed through one unit).  Through
       tanh this is an upper bound on the realised gain (signed_influence's docstring); depth 2 is chosen
       because the designed fauna's topology reaches its Effectors only through its hidden layer (its
       founders carry no direct posture link), and it is the depth the routed motif reads at (RBT-87).
       Deeper sums are not used: the recurrent core's spectral radius is above 1 on every committed best
       (RBT-81), so a longer truncated sum is a property of where the counting stopped.
  n1, n2   the number of pairs with a non-zero gain at depth 1 and at depth <= 2.
  ns   the number of posture sensor units the body carries (a re-wiring can only be a new use of one).
  g2_contact, g2_height, g2_up, g2_joint   g2 split by the sensor's class (joint = angle + velocity).
  g1_other   the placebo (adversary round 1, F1): g1 over the non-posture sensors food, agent and oscillator,
             which flat ground gives no posture-specific reason to wire.  A change in how fast lineages turn over
             moves it as it moves g1; a new use of a posture sensor does not.
  g1_vel     g1 over velocity, apart: obstacles change what velocity reads, so it is neither posture nor placebo.

Absolute values, because a sign is only comparable across bodies with the same effector layout, and
these bodies differ; the readout asks about the amount of posture-to-motor wiring, in either direction.
"""
import json
import os
import sys

import numpy as np

POSTURE = ("contact", "height", "up", "joint_angle", "joint_velocity")
#: the placebo (RBT-101 adversary F1): non-posture sensors flat ground gives no posture-specific reason to wire;
#: velocity is kept apart because obstacles change it too
OTHER = ("food", "agent", "oscillator")
VELOCITY = ("velocity",)
CLASSES = (("contact", ("contact",)), ("height", ("height",)), ("up", ("up",)), ("joint", ("joint_angle", "joint_velocity")))
COLS = ("g1", "g2", "n1", "n2", "ns") + tuple(f"g2_{c}" for c, _ in CLASSES) + ("g1_other", "g1_vel")


def digest(ph):
    """The posture-wiring row of one phenotype, as a dict over COLS."""
    from rabbitstew.analysis import signed_influence
    src = {i: ui.unit.source for i, ui in enumerate(ph.units) if ui.unit.kind == "sensor"}
    d1 = [r for r in signed_influence(ph, depth=1) if src[r["sensor"]] in POSTURE]
    d2 = [r for r in signed_influence(ph, depth=2) if src[r["sensor"]] in POSTURE]
    row = {"g1": sum(abs(r["gain"]) for r in d1), "g2": sum(abs(r["gain"]) for r in d2),
           "n1": len(d1), "n2": len(d2), "ns": sum(1 for s in src.values() if s in POSTURE)}
    for c, members in CLASSES:
        row[f"g2_{c}"] = sum(abs(r["gain"]) for r in d2 if src[r["sensor"]] in members)
    all1 = signed_influence(ph, depth=1)
    row["g1_other"] = sum(abs(r["gain"]) for r in all1 if src[r["sensor"]] in OTHER)
    row["g1_vel"] = sum(abs(r["gain"]) for r in all1 if src[r["sensor"]] in VELOCITY)
    return row


def sim_config(run):
    from rabbitstew.simulation import SimConfig
    return SimConfig.from_dict(json.load(open(os.path.join(run, "config.json")))["sim"])


def fmt(v):
    return str(v) if isinstance(v, int) else f"{v:.6f}"


def write(run, to=None):
    from rabbitstew.genotype import Genotype
    from rabbitstew.synthesis import synthesize
    syn = sim_config(run).synthesis
    born = {}
    with open(os.path.join(run, "lineage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            k = (r["population"], r["name"])
            if k not in born:
                born[k] = r["generation"] - r["age"]
    out, missing = [], 0
    for (pop, name), b in born.items():
        p = os.path.join(run, pop, "genomes", f"{name}.json")
        if not os.path.exists(p):
            missing += 1
            out.append([pop, name, str(b)] + ["-"] * len(COLS))
            continue
        row = digest(synthesize(Genotype.load(p), syn))
        out.append([pop, name, str(b)] + [fmt(row[c]) for c in COLS])
    os.makedirs(to or run, exist_ok=True)
    with open(os.path.join(to or run, "wiring.txt"), "w") as f:
        f.write("\t".join(("population", "name", "born") + COLS) + "\n")
        for r in out:
            f.write("\t".join(r) + "\n")
    return len(out), missing


if __name__ == "__main__":
    a = sys.argv[2:]
    n, missing = write(sys.argv[1], a[a.index("--to") + 1] if "--to" in a else None)
    print(f"wrote wiring.txt for {sys.argv[1]}: {n} individuals" + (f", {missing} genomes missing" if missing else ""))
