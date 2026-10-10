"""RBT-134b design-time checks on the COMMITTED PARENTS only (DESIGN-134b.md section 1).

No lineage is mutated, no condition is run, no MASTER_SEED is used, and nothing under runs/RBT-134/out/ or any
RBT-129 output is read.  Inputs: RBT-78's two parent pools (via runs/RBT-91/structural_rate.py) and the merged code.

For every parent it checks or measures:
  V   plant visibility: a pair-event unit planted on the parent (genetics._pair_event's own wiring, both sign
      combinations) is a predicate unit of the synthesised phenotype.  If V holds on every parent, a plant is
      structure at the depth it is made, so an ever-structured exclusion removes every C+ remnant (section 3).
  S1  swap precondition 1: both a `food` and an `agent` sensor on each drive wheel.
  S2  swap precondition 2: synthesising the food<->agent relabelled parent gives the original phenotype with only
      the two sources swapped (same unit order, same links).
  G   the global brain's units and links, and each drive wheel's local links (refusal and erosion arithmetic).
  bE  the drive Effectors' biases (the C+ plant's slope factor sech^2(b_E) at depth 0).
  Y0  the depth-0 yield of a C+ plant: the share of plants on this parent whose links-alone |a| >= 12.5236, over
      DRAWS magnitude draws |N(0,1)| x 16 from a DESIGN seed (SeedSequence([134, 2, parent]); not a lineage seed).

    python runs/RBT-134/design-134b/parent_checks.py > runs/RBT-134/design-134b/parent_checks.txt
"""
import importlib.util
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
sys.path.insert(0, _ROOT)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    argv, sys.argv = sys.argv, [path]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    return mod


sr = _load("sr91", os.path.join(_ROOT, "runs", "RBT-91", "structural_rate.py"))
rbt78 = sr.rbt78

from rabbitstew import genetics  # noqa: E402
from rabbitstew.fixed import drive_effector_units  # noqa: E402
from rabbitstew.genotype import Link, Neuron, UnitRef  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

RUNG = 12.5236
SCALE = 16.0
DRAWS = 200


def plant(g, s_in, s_out, m, bias=0.0):
    """genetics._pair_event's wiring, deterministic: returns a planted copy and the new unit's genotype ref."""
    g = g.copy()
    (nL, sL, eL), (nR, sR, eR) = genetics._wheel_pairs(g)
    gb = g.global_brain
    gb.units.append(Neuron(bias, "tanh"))
    k = UnitRef(None, len(gb.units) - 1)
    gb.links.append(Link(UnitRef(nL, sL), k, s_in * m[0]))
    gb.links.append(Link(UnitRef(nR, sR), k, -s_in * m[1]))
    g.nodes[nL].segment.brain.links.append(Link(k, UnitRef(nL, eL), s_out * m[2]))
    g.nodes[nR].segment.brain.links.append(Link(k, UnitRef(nR, eR), s_out * m[3]))
    return g, k


def ph_index(ph, ref):
    return [i for i, ui in enumerate(ph.units) if ui.part is None and ui.ref == ref]


def swapped(g):
    g = g.copy()
    for _, brain in g.brains():
        for u in brain.units:
            if u.kind == "sensor" and u.source in ("food", "agent"):
                u.source = "agent" if u.source == "food" else "food"
    return g


def phen_sig(ph, swap=False):
    def src(u):
        s = getattr(u, "source", None)
        if swap and s in ("food", "agent"):
            return "agent" if s == "food" else "food"
        return s
    return ([(ui.part, ui.ref, ui.unit.kind, src(ui.unit), getattr(ui.unit, "func", None),
              getattr(ui.unit, "bias", None)) for ui in ph.units], list(ph.links))


def main():
    print(__doc__.split("\n\n")[0])
    t_syn = []
    tot = {"parents": 0, "V": 0, "S1": 0, "S2": 0, "no_pair": 0}
    for label in rbt78.POOLS:
        cfg, pool = rbt78._load(label)
        syn = cfg.sim.synthesis
        m = cfg.mutation
        print(f"\n## {label}: {len(pool)} parents; weight_rate {m.weight_rate}, weight_reset_rate {m.weight_reset_rate}, "
              f"weight_sigma {m.weight_sigma}, func_rate {m.func_rate}, remove_unit_rate {m.remove_unit_rate}, "
              f"add_unit_rate {m.add_unit_rate}, max_units_per_brain {m.max_units_per_brain}, "
              f"funcs {list(m.vocab.neuron_funcs)}\n")
        print("| parent | V | S1 | S2 | global units | global links | wheel local links L/R | b_E (drive) | Y0 at a32 |")
        print("|---|---|---|---|---|---|---|---|---|")
        for p, g in enumerate(pool):
            tot["parents"] += 1
            t0 = time.process_time()
            ph = synthesize(g, syn)
            t_syn.append(time.process_time() - t0)
            pairs = genetics._wheel_pairs(g)
            if pairs is None:
                tot["no_pair"] += 1
                print(f"| {p} | no wheel pair | | | | | | | |")
                continue
            vis = True
            for s_in in (1.0, -1.0):
                for s_out in (1.0, -1.0):
                    gp, k = plant(g, s_in, s_out, [SCALE] * 4)
                    php = synthesize(gp, syn)
                    idx = ph_index(php, k)
                    vis &= len(idx) == 1 and idx[0] in sr.motif_units(php)
            tot["V"] += vis
            s1 = _both(ph)
            tot["S1"] += s1
            phs = synthesize(swapped(g), syn)
            s2 = phen_sig(phs) == phen_sig(ph, swap=True)
            tot["S2"] += s2
            (nL, _, _), (nR, _, _) = pairs
            le, re_ = drive_effector_units(ph)
            be = [float(ph.units[e].unit.bias) for e in le + re_]
            rng = np.random.default_rng(np.random.SeedSequence([134, 2, tot["parents"]]))
            hit = 0
            for _ in range(DRAWS):
                mm = [abs(float(rng.normal())) * SCALE for _ in range(4)]
                gp, k = plant(g, 1.0 if rng.random() < 0.5 else -1.0, 1.0 if rng.random() < 0.5 else -1.0, mm)
                php = synthesize(gp, syn)
                a = sr.links_alone_a(php, ph_index(php, k)[0])
                hit += np.isfinite(a) and abs(a) >= RUNG
            print(f"| {p} | {'yes' if vis else 'NO'} | {'yes' if s1 else 'NO'} | {'yes' if s2 else 'NO'} "
                  f"| {len(g.global_brain.units) if g.global_brain else 0} | {len(g.global_brain.links) if g.global_brain else 0} "
                  f"| {len(g.nodes[nL].segment.brain.links)}/{len(g.nodes[nR].segment.brain.links)} "
                  f"| {', '.join(f'{b:+.2f}' for b in be)} | {hit / DRAWS:.3f} |")
    print(f"\n## Totals\n\nparents {tot['parents']}; no wheel pair {tot['no_pair']}; V (plant visible) {tot['V']}; "
          f"S1 {tot['S1']}; S2 {tot['S2']}")
    print(f"synthesize: median {1e3 * float(np.median(t_syn)):.2f} ms CPU per parent phenotype")


def _both(ph):
    noses_f = sr._wheel_noses(ph)
    side = {}
    for i, ui in enumerate(ph.units):
        if ui.unit.kind != "sensor" or ui.part is None or ui.unit.source not in ("food", "agent"):
            continue
        part = ph.parts[ui.part]
        if part.parent is None:
            continue
        side.setdefault(("left" if part.attach_pos[1] > 0 else "right", ui.unit.source), []).append(ui.part)
    if noses_f is None or any((s, src) not in side for s in ("left", "right") for src in ("food", "agent")):
        return False
    return all(sorted(side[(s, "food")]) == sorted(side[(s, "agent")]) for s in ("left", "right"))


if __name__ == "__main__":
    main()
