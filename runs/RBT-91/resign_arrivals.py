"""RBT-91 (a): are the drift-proposed motifs compasses or anti-compasses?

`structural_rate.py` counts the motif's SHAPE -- opposite-sign in from the two wheel noses,
same-sign out to the two drive Effectors. Shape is not direction: whether a given circuit steers
its robot TOWARD food depends on which way that robot drives, and W4b-801's founders drive
backward (-174 deg), so a descendant that drives forward needs the opposite steering sign to be
chemotactic. RBT-80 established this and re-signs per individual; this does the same for the four
arrivals, which is the first thing I said I would attack in my own result.

Each arrival is regenerated from its (pool, lineage index) -- the lineage seeding is
`SeedSequence([MASTER_SEED, crc32(label), k, i])` and the parent is `pool[i % len(pool)]`, both
independent of how the work was chunked, so the regeneration is exact. Direction is measured with
RBT-80's own probe (2 seeds x 3 s, travel heading against body yaw), imported rather than
reimplemented.

Positive after re-signing is a COMPASS; negative is an ANTI-COMPASS.

Usage: resign_arrivals.py
"""
import importlib.util
import math
import os
import sys
import zlib
from dataclasses import replace

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("sr", os.path.join(_HERE, "structural_rate.py"))
sr = importlib.util.module_from_spec(_s)
_argv, sys.argv = sys.argv, ["structural_rate.py"]
_s.loader.exec_module(sr)
_r = importlib.util.spec_from_file_location("rbt80", os.path.join(_HERE, "..", "..", "scripts", "rbt80_population.py"))
rbt80 = importlib.util.module_from_spec(_r)
_r.loader.exec_module(rbt80)
sys.argv = _argv

from rabbitstew.genetics import mutate_controller
from rabbitstew.simulation import Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

#: the arrivals found by structural_rate.py at --n 5000, as (pool label, lineage index)
ARRIVALS = [("W4b-801-bests", 176), ("W4b-801-bests", 2430), ("W4b-801-bests", 3550),
            ("P-801-final60", 109)]
K, ADD, REM = 19, 0.15, 0.1


def regenerate(label, i):
    cfg, pool = sr.rbt78._load(label)
    mcfg = replace(cfg.mutation, add_link_rate=ADD, remove_link_rate=REM)
    rng = np.random.default_rng(np.random.SeedSequence(
        [sr.rbt78.MASTER_SEED, zlib.crc32(label.encode()), K, i]))
    g = pool[i % len(pool)]
    for _ in range(K):
        g = mutate_controller(g, rng, mcfg)
    return g, cfg


def heading(g, cfg):
    """Mean travel direction relative to body yaw, in degrees. RBT-80's probe."""
    T = []
    for s in range(9000, 9000 + rbt80.PROBE_SEEDS):
        sc = replace(cfg.sim, random_start=True, duration=rbt80.PROBE_DUR)
        sim = Simulation([g], sc, spawns=spawn_layout(1, sc, s))
        sim.set_food_seed(s)
        idx = sim.robots[0]
        last = sim.data.xpos[idx.root_body][:2].copy()
        for _ in range(int(round(sc.duration / sc.control_dt))):
            sim.step()
            if sim.exploded[0]:
                break
            q = sim.data.xquat[idx.root_body]
            yaw = float(np.arctan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] ** 2 + q[3] ** 2)))
            pos = sim.data.xpos[idx.root_body][:2]
            d = pos - last
            if np.linalg.norm(d) > 1e-3:
                T.append(rbt80.wrap(float(np.arctan2(d[1], d[0])) - yaw))
            last = pos.copy()
    if not T:
        return None
    return float(np.degrees(np.arctan2(np.mean(np.sin(T)), np.mean(np.cos(T)))))


def main():
    print("# RBT-91 (a): compass or anti-compass? The four arrivals, re-signed\n")
    print("Shape is not direction. A motif steers TOWARD food only if its sign agrees with the way")
    print("its robot actually drives; W4b-801's founders drive backward (-174 deg), so a descendant")
    print("that drives forward needs the opposite steering sign to be chemotactic (RBT-80).")
    print(f"Probe: RBT-80's own, {rbt80.PROBE_SEEDS} seeds x {rbt80.PROBE_DUR:g}s, imported.")
    print(f"FOUNDER_BACKWARD = {rbt80.FOUNDER_BACKWARD}\n")
    print(f"| arrival | raw a | heading | drives | re-signed a | verdict |")
    print(f"|---|---|---|---|---|---|")
    comp = anti = unknown = 0
    for label, i in ARRIVALS:
        g, cfg = regenerate(label, i)
        ph = synthesize(g, cfg.sim.synthesis)
        units = sr.motif_units(ph)
        a = sr.small_signal_a(ph)
        h = heading(g, cfg)
        if h is None:
            unknown += 1
            print(f"| {label} #{i} | {a:+.4f} | (never moved) | ? | — | UNDETERMINED |")
            continue
        back = abs(h) > 90
        signed = a if (back == rbt80.FOUNDER_BACKWARD) else -a
        verdict = "COMPASS" if signed > 0 else "ANTI-COMPASS"
        comp += signed > 0
        anti += signed <= 0
        print(f"| {label} #{i} | {a:+.4f} | {h:+.1f} deg | {'backward' if back else 'forward'} "
              f"| **{signed:+.4f}** | **{verdict}** |")
        assert units, "regeneration lost the motif -- the lineage seeding is not reproducible"
    print(f"\n  compasses {comp}, anti-compasses {anti}"
          + (f", undetermined {unknown}" if unknown else ""))
    print(f"\n  The structural rate counts shape and is unchanged. What this changes is what the")
    print(f"  rate MEANS: only the compasses are circuits a selection pressure could reward, so")
    print(f"  the chemotactic arrival rate is {comp}/4 of the structural one.")


if __name__ == "__main__":
    main()
