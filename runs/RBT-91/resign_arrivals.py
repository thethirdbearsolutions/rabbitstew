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

Usage: resign_arrivals.py [readout.txt] [weight_sigma]   (default: the four arrivals of the n=5000 run)

With a readout the arrivals are parsed from its per-lineage lines, so the whole set of a large
run can be re-signed rather than a sample of it. The chemotactic rate is the number the decision
turns on, and at four arrivals it has no interval worth quoting.
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
SIGMA = None  #: must match the --sigma of the run whose readout is being re-signed


def regenerate(label, i, sigma=None):
    """Regenerate one lineage EXACTLY. `sigma` must match the run that found it: a readout made
    with --sigma is a different drift process, and regenerating it at the default silently
    produces a different genotype. The assertion in main() is what caught that."""
    cfg, pool = sr.rbt78._load(label)
    mcfg = replace(cfg.mutation, add_link_rate=ADD, remove_link_rate=REM)
    if sigma is not None:
        mcfg = replace(mcfg, weight_sigma=sigma)
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


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    ph_ = k / n
    d = 1 + z * z / n
    c = (ph_ + z * z / (2 * n)) / d
    h = z * ((ph_ * (1 - ph_) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def from_readout(path):
    """Arrivals parsed from a structural_rate.py readout's per-lineage lines."""
    import re
    out = []
    for line in open(path):
        m = re.search(r"^\s+(\S+) lineage (\d+):", line)
        if m:
            out.append((m.group(1), int(m.group(2))))
    return out


def main():
    global SIGMA
    arrivals = ARRIVALS
    if len(sys.argv) > 2:
        SIGMA = float(sys.argv[2])
    if len(sys.argv) > 1:
        arrivals = from_readout(sys.argv[1])
        if SIGMA is not None:
            print(f"  regenerating with weight_sigma = {SIGMA}, matching the run that found these\n")
        print(f"# RBT-91 (a): compass or anti-compass? {len(arrivals)} arrivals from "
              f"{sys.argv[1]}, re-signed\n")
    else:
        print("# RBT-91 (a): compass or anti-compass? The four arrivals, re-signed\n")
    print("Shape is not direction. A motif steers TOWARD food only if its sign agrees with the way")
    print("its robot actually drives; W4b-801's founders drive backward (-174 deg), so a descendant")
    print("that drives forward needs the opposite steering sign to be chemotactic (RBT-80).")
    print(f"Probe: RBT-80's own, {rbt80.PROBE_SEEDS} seeds x {rbt80.PROBE_DUR:g}s, imported.")
    print(f"FOUNDER_BACKWARD = {rbt80.FOUNDER_BACKWARD}\n")
    print(f"| arrival | raw a | heading | drives | re-signed a | verdict |")
    print(f"|---|---|---|---|---|---|")
    comp = anti = unknown = 0
    COMPASS_GAINS = []
    for label, i in arrivals:
        g, cfg = regenerate(label, i, SIGMA)
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
        if signed > 0:
            COMPASS_GAINS.append(signed)
        print(f"| {label} #{i} | {a:+.4f} | {h:+.1f} deg | {'backward' if back else 'forward'} "
              f"| **{signed:+.4f}** | **{verdict}** |")
        assert units, "regeneration lost the motif -- the lineage seeding is not reproducible"
    tot = comp + anti
    lo_, hi_ = wilson(comp, tot) if tot else (float("nan"), float("nan"))
    print(f"\n  compasses {comp}, anti-compasses {anti}"
          + (f", undetermined {unknown}" if unknown else ""))
    print(f"  chemotactic fraction of structural arrivals: {100.0 * comp / tot:.1f}% "
          f"[{100 * lo_:.1f}%, {100 * hi_:.1f}%] (Wilson 95%)")
    print(f"\n  The structural rate counts shape and is unchanged. What this changes is what the")
    print(f"  rate MEANS: only the compasses are circuits a selection pressure could reward.")
    if comp:
        g = sorted((abs(x) for x in COMPASS_GAINS), reverse=True)
        print(f"  Realised gains of the compasses, largest first: "
              f"{', '.join(f'{x:.4f}' for x in g[:8])}"
              + (" ..." if len(g) > 8 else ""))
        print(f"  Against the first paying rung (6.8664): "
              f"{sum(1 for x in g if x >= 6.8664)} of {len(g)} reach it.")


if __name__ == "__main__":
    main()
