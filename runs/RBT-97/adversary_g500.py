"""RBT-97 adversary, round 2: g500 per seed at a = 64 and 384, all five conditions, with the
author's bout() (runs/RBT-97/mechanism.py).  g500 is the one robot whose anti-compass also pays and
whose gain survives the ROTATED decoy at a = 64 (+1.250 against +1.031, adversary_rotated.txt).
Paired over its 64 seeds: each condition against base, and motif against each decoy.

Usage: python runs/RBT-97/adversary_g500.py
"""
import math, os, sys
from multiprocessing import get_context
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-97"))
import numpy as np
import mechanism as mech
from rabbitstew.paired import paired

POP, GEN = "p801", 500
SEEDS = [7000 + i for i in range(64)]
mech.CFG[POP] = mech.cds.config(POP)
mech.SIGN.update({(POP, g): s for g, s in mech.signs_for(POP, list(mech.cds.POPULATIONS[POP]["gens"]), "per-robot").items()})
tasks = [(POP, GEN, 0.0, s, "base") for s in SEEDS]
tasks += [(POP, GEN, a, s, c) for a in (64.0, 384.0) for s in SEEDS for c in ("motif", "phantom", "rotated", "antimotif")]
with get_context("fork").Pool(4) as pool:
    rows = pool.map(mech.bout, tasks, chunksize=8)
by = {(r[2], r[3], r[4]): r[9] for r in rows}
base = [by[(0.0, s, "base")] for s in SEEDS]
print(f"g500 (P-801), sign {mech.SIGN[(POP, GEN)]:+.0f}, 64 paired seeds from 7000; {sum(r[10] for r in rows)} exploded")
for a in (64.0, 384.0):
    print(f"a = {a:.0f}")
    arm = {c: [by[(a, s, c)] for s in SEEDS] for c in ("motif", "phantom", "rotated", "antimotif")}
    for c, v in arm.items():
        print("  " + paired(v, base).line(f"{c} - base"))
    for c in ("phantom", "rotated"):
        print("  " + paired(arm["motif"], arm[c]).line(f"motif - {c}"))
