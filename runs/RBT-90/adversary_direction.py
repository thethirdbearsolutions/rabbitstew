"""Can direction of travel be defined for a HOLISTIC founder at all?  (RBT-90 part 1, adversary)

The report names the direction-of-travel split as the missing measurement, on the grounds that
"for a random body the axis 'forward' is read against has to be defined first; RBT-69's is the
Pioneer chassis yaw."  The coordinator asked me to confirm that or propose an axis.

**Half of it is confirmed and half is too strong.**  `scripts/travel_direction.py::yaw_of` reads the
root body's own quaternion -- `data.xquat[robots[0].root_body]` -- and nothing about the Pioneer's
designed front, so the probe's machinery runs unchanged on any body with a root segment, which every
holistic founder has.  What genuinely fails for a random body is the ZERO POINT: the Pioneer's yaw
has a designed front, so a circular mean near 0 deg reads as "drives nose-first" and near 180 as
"tail-first".  A holistic founder's root-segment frame is an arbitrary product of synthesis order, so
its circular mean is not comparable across founders and RBT-69's forward/backward SPLIT is not
definable on this population.

What survives, and is the quantity that actually decides whether an installed circuit has a
well-defined sign, is the CONCENTRATION.  Per founder, R = |mean exp(i * (travel azimuth - own root
yaw))| over its own bouts answers "does this body travel in a fixed direction in its own frame?"  It
needs no shared axis, because it is computed within one body.  A body with R near 1 has a travel
direction a circuit can be signed against; a body with R near 0 does not, and for it the question
RBT-69 asks has no answer rather than an unmeasured one.

So this probe reports, per founder: R, the bout count, and the exploded count; and for the
population, the distribution of R and of the per-founder mean angle.  An isotropic distribution of
per-founder means is the positive evidence that no forward/backward split exists to be measured --
which is a stronger statement than "not measured", and it is measurable now.

usage: adversary_direction.py [SEED] [N_FOUNDERS] [N_BOUTS]        (default 801 10 16)
"""
import importlib.util
import pathlib
import sys
from dataclasses import replace

import numpy as np

from rabbitstew.simulation import Simulation, spawn_layout

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ART = ROOT / "docs" / "artifacts"
spec = importlib.util.spec_from_file_location("fd", ROOT / "runs" / "RBT-90" / "founder_diversity.py")
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)
spec2 = importlib.util.spec_from_file_location("td", ROOT / "scripts" / "travel_direction.py")
td = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(td)


def offsets_of(g, cfg, n_bouts):
    """travel azimuth minus the root segment's own yaw, per control tick, over n_bouts bouts.

    The body-frame version of scripts/travel_direction.py::offsets, taking a genotype rather than a
    run directory and reusing that module's yaw_of and wrap so the convention is identical.
    """
    out, exploded = [], 0
    for seed in range(9000, 9000 + n_bouts):
        c = replace(cfg, random_start=True)
        sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
        sim.set_food_seed(seed)
        last = sim.data.xpos[sim.robots[0].root_body][:2].copy()
        for _ in range(int(round(c.duration / c.control_dt))):
            sim.step()
            if sim.exploded[0]:
                exploded += 1
                break
            pos = sim.data.xpos[sim.robots[0].root_body][:2]
            d = pos - last
            if np.linalg.norm(d) > 1e-3:
                out.append(td.wrap(float(np.arctan2(d[1], d[0])) - td.yaw_of(sim)))
            last = pos.copy()
    return np.array(out), exploded


def main(seed=801, n_founders=10, n_bouts=16):
    evo, F = fd.founders(seed)
    F = F[:n_founders]
    L = [f"RBT-90 adversary: is a travel direction definable for holistic founders?  seed {seed}, "
         f"first {len(F)} founders, {n_bouts} bouts each.",
         "Convention imported from scripts/travel_direction.py (yaw_of reads the ROOT BODY quaternion, "
         "nothing Pioneer-specific).",
         "R is computed WITHIN one body, so it needs no shared forward axis.  The per-founder mean angle "
         "is NOT comparable across",
         "founders -- each root frame is an arbitrary product of synthesis order -- and is printed only to "
         "show whether it is isotropic.",
         "",
         f"  {'founder':9s} {'ticks':>6s} {'exploded':>8s} {'R':>6s} {'mean angle':>11s}  travel direction in its own frame"]
    rows = []
    for g in F:
        o, ex = offsets_of(g, evo.sim, n_bouts)
        if not len(o):
            L.append(f"  {g.name:9s} {0:6d} {ex:8d} {'--':>6s} {'--':>11s}  never moved 1 mm in a tick: no direction to define")
            continue
        m, R = td.circ(o)
        rows.append((g.name, len(o), ex, R, m))
        verdict = ("fixed in its own frame" if R >= 0.6 else
                   "weak" if R >= 0.3 else "NONE -- travels every way relative to itself")
        L.append(f"  {g.name:9s} {len(o):6d} {ex:8d} {R:6.3f} {m:+10.1f}  {verdict}")
    if rows:
        Rs = np.array([r[3] for r in rows])
        ang = np.radians([r[4] for r in rows])
        popR = float(np.hypot(np.mean(np.sin(ang)), np.mean(np.cos(ang))))
        L += ["",
              f"  per-founder R: min {Rs.min():.3f} median {np.median(Rs):.3f} max {Rs.max():.3f}; "
              f"{int((Rs >= 0.6).sum())}/{len(Rs)} at or above 0.6",
              f"  resultant of the per-founder MEAN angles: {popR:.3f} over {len(rows)} founders "
              f"(0 = isotropic, 1 = one shared direction)",
              f"    expectation under exact isotropy at this n: 0.886/sqrt({len(rows)}) = {0.8862/np.sqrt(len(rows)):.3f}"
              f"   -> observed is {'BELOW it: isotropic' if popR < 0.8862/np.sqrt(len(rows)) else 'above it'}",
              f"  founders that never moved 1 mm in a tick: {n_founders - len(rows)}/{n_founders} "
              f"-- for these the statistic is undefined by immobility, whatever axis is chosen",
              "",
              "  Reading: a per-founder R near 1 means that body has a travel direction an installed circuit",
              "  could be signed against.  A near-isotropic resultant of the per-founder means is positive",
              "  evidence that there is no population-level forward axis, so RBT-69's forward/backward SPLIT",
              "  is not merely unmeasured on this population -- it is undefined, and this is how to show it.",
              "  The split remains measurable on the conventional Pioneer population, which has a designed front."]
    text = "\n".join(L)
    (ART / f"RBT-90-adversary-direction-{seed}.txt").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(int(a[0]) if a else 801, int(a[1]) if len(a) > 1 else 10, int(a[2]) if len(a) > 2 else 16)
