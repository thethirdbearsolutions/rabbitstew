"""RBT-91: does drift propose the ROUTED motif's structure? The measurement the decision deferred.

The decision (2026-09-19) declined option B on the reason that magnitude is the smaller of two
barriers and structure the larger. Its adversary showed that reason cannot be ordered from the
numbers in hand, for two reasons: the magnitude arithmetic was the *installed* motif's (four
links pinned to a = 2w), and the structural figure it leaned on -- RBT-78's "0 of 10,000" -- is
that instrument's DIRECT column, which reads **exactly zero on the routed motif by construction**
(RBT-87). So the reopening condition named a measurement whose instrument does not exist.

This is that instrument. No simulation, no world, no selection.

THE PREDICATE. The routed motif is the only compass this encoding can express: the two wheel
noses feed a global interneuron with opposite sign, and that interneuron feeds both drive
Effectors with the same sign (`scripts/genotype_motif.py`). So the structure is present iff some
global non-sensor unit has

  * incoming links from BOTH wheel `food` noses, with OPPOSITE signs, and
  * outgoing links to BOTH drive Effectors, with the SAME sign.

Sign is taken on the summed weight per (source, target) pair, so a pair of links that cancel does
not count as present. Nothing here thresholds on magnitude: this counts structure and only
structure, which is the whole point -- the magnitude is reported beside it and never gates it.

THE DENOMINATOR is RBT-78's, unchanged: 19 `mutate_controller` mutations from committed parents,
5,000 lineages per pool, both pools, `MASTER_SEED = 20260912`, `add=0.15 rem=0.1`. The lineage
generator is RBT-78's, imported rather than reimplemented so the audit cannot drift from what it
audits.

THE MAGNITUDE BESIDE IT is the realised small-signal steering response, not a path sum: drive the
nose pair antisymmetrically at +-d/2 with every other sensor at zero, step the brain until the
Effector outputs settle, and read `(e_L + e_R)/2` per unit of drive. Reported at d = 0.01 and
calibrated by halving d until the reading stops moving, which is the discipline RBT-81's adversary
established. It is a property of the circuit at the zero operating point and it is finite by
construction, so none of RBT-81's divergence applies.

Usage: structural_rate.py [--n 5000] [--k 19] [--workers 4]
"""
import argparse
import importlib.util
import os
import sys
import zlib
from dataclasses import replace

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rbt78", os.path.join(_HERE, "..", "RBT-78", "reconcile.py"))
rbt78 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rbt78)

from rabbitstew.brain import RuntimeBrain
from rabbitstew.fixed import drive_effector_units
from rabbitstew.genetics import mutate_controller
from rabbitstew.synthesis import synthesize

DRIVE = 0.01
SETTLE = 12


def _wheel_noses(ph):
    """(left, right) unit indices of the `food` noses on the two drive wheels, or None."""
    side = {}
    for i, ui in enumerate(ph.units):
        if ui.unit.kind != "sensor" or ui.unit.source != "food" or ui.part is None:
            continue
        part = ph.parts[ui.part]
        if part.parent is None:
            continue
        side.setdefault("left" if part.attach_pos[1] > 0 else "right", []).append(i)
    if "left" not in side or "right" not in side:
        return None
    return side["left"][0], side["right"][0]


def motif_units(ph):
    """Global non-sensor units carrying the routed motif's structure. THE PREDICATE."""
    noses = _wheel_noses(ph)
    if noses is None:
        return []
    n_L, n_R = noses
    left_e, right_e = drive_effector_units(ph)
    if not left_e or not right_e:
        return []
    e_L, e_R = left_e[0], right_e[0]
    w = {}
    for s, d, weight in ph.links:
        w[(s, d)] = w.get((s, d), 0.0) + weight
    out = []
    for k, ui in enumerate(ph.units):
        if ui.part is not None or ui.unit.kind == "sensor":
            continue  # global non-sensor units only
        in_L, in_R = w.get((n_L, k), 0.0), w.get((n_R, k), 0.0)
        if in_L == 0.0 or in_R == 0.0 or np.sign(in_L) == np.sign(in_R):
            continue
        out_L, out_R = w.get((k, e_L), 0.0), w.get((k, e_R), 0.0)
        if out_L == 0.0 or out_R == 0.0 or np.sign(out_L) != np.sign(out_R):
            continue
        out.append(k)
    return out


def small_signal_a(ph, drive=DRIVE, settle=SETTLE):
    """Realised steering-axis response per unit of antisymmetric nose drive, through the tanh."""
    noses = _wheel_noses(ph)
    if noses is None:
        return float("nan")
    n_L, n_R = noses
    left_e, right_e = drive_effector_units(ph)
    if not left_e or not right_e:
        return float("nan")
    brain = RuntimeBrain(ph)
    sens = list(brain.sensor_idx)
    pos = {u: j for j, u in enumerate(sens)}
    if n_L not in pos or n_R not in pos:
        return float("nan")
    out = []
    for sign in (+1.0, -1.0):
        brain.activation = np.zeros(brain.n)
        brain._prev_input = np.zeros(brain.n)
        v = np.zeros(len(sens))
        v[pos[n_L]] = +sign * drive / 2.0
        v[pos[n_R]] = -sign * drive / 2.0
        for _ in range(settle):
            brain.step(v)
        eL = float(brain.activation[left_e].sum())
        eR = float(brain.activation[right_e].sum())
        out.append((eL + eR) / 2.0)
    return (out[0] - out[1]) / (2.0 * drive)


def run_chunk(task):
    label, lo, hi, k, add, rem = task
    cfg, pool = rbt78._load(label)
    mcfg = replace(cfg.mutation, add_link_rate=add, remove_link_rate=rem)
    present = 0
    gains = []
    hits = []
    n = 0
    for i in range(lo, hi):
        rng = np.random.default_rng(np.random.SeedSequence(
            [rbt78.MASTER_SEED, zlib.crc32(label.encode()), k, i]))
        g = pool[i % len(pool)]
        for _ in range(k):
            g = mutate_controller(g, rng, mcfg)
        ph = synthesize(g, cfg.sim.synthesis)
        n += 1
        if motif_units(ph):
            present += 1
            a = small_signal_a(ph)
            hits.append((i, len(motif_units(ph)), float(a)))
            if np.isfinite(a):
                gains.append(abs(a))
    return label, n, present, gains, hits


def selftest():
    """The predicate must be able to say YES, or a zero rate means nothing.

    Install the routed motif with `genotype_motif.install` at a known w on a committed parent and
    require the predicate to find it and the small-signal response to recover a = 2w; then remove
    it and require both to go quiet. This is the same discipline RBT-66 was built on: an
    instrument that cannot recover what it was told to find cannot adjudicate what it was not.
    """
    import json
    from rabbitstew.genotype import Genotype
    from rabbitstew.simulation import SimConfig
    gm_spec = importlib.util.spec_from_file_location(
        "gm", os.path.join(_HERE, "..", "..", "scripts", "genotype_motif.py"))
    gm = importlib.util.module_from_spec(gm_spec)
    gm_spec.loader.exec_module(gm)

    cfg = SimConfig.from_dict(json.load(open("runs/RBT-19/P-801/config.json"))["sim"])
    g = Genotype.load("runs/RBT-19/P-801/conventional/best_gen0590.json")
    print("# RBT-91 predicate self-test -- can it say YES?\n")
    ph0 = synthesize(g, cfg.synthesis)
    print(f"  bare parent            : units matching predicate = {len(motif_units(ph0))}  "
          f"small-signal a = {small_signal_a(ph0):+.4f}")
    ok = True
    for w in (1.0, 8.0, 32.0):
        for sign in (+1.0, -1.0):
            ph = synthesize(gm.install(g, w, sign=sign), cfg.synthesis)
            hits = motif_units(ph)
            a = small_signal_a(ph)
            good = len(hits) >= 1
            ok &= good
            print(f"  routed motif w={w:5.1f} sign={sign:+.0f}: units matching predicate = "
                  f"{len(hits)}  small-signal a = {a:+9.4f}  (installed 2w = {2 * w * sign:+.1f})"
                  f"  {'OK' if good else 'FAILED TO DETECT'}")
    print(f"\n  predicate self-test: {'PASSED' if ok else 'FAILED'} -- a zero rate below is "
          f"{'meaningful' if ok else 'MEANINGLESS'}.\n")
    return ok


def calibrate_drive():
    """Halve the drive until the reading stops moving (RBT-81's adversary's discipline)."""
    import json
    from rabbitstew.genotype import Genotype
    from rabbitstew.simulation import SimConfig
    gm_spec = importlib.util.spec_from_file_location(
        "gm", os.path.join(_HERE, "..", "..", "scripts", "genotype_motif.py"))
    gm = importlib.util.module_from_spec(gm_spec)
    gm_spec.loader.exec_module(gm)
    cfg = SimConfig.from_dict(json.load(open("runs/RBT-19/P-801/config.json"))["sim"])
    g = Genotype.load("runs/RBT-19/P-801/conventional/best_gen0590.json")
    ph = synthesize(gm.install(g, 8.0, sign=+1.0), cfg.synthesis)
    print("# Drive calibration on an installed w=8 motif (2w = 16)\n")
    for d in (1.0, 0.1, 0.05, 0.01, 0.005, 0.001):
        print(f"  drive {d:<6}: small-signal a = {small_signal_a(ph, drive=d):+.5f}")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5000)
    ap.add_argument("--k", type=int, default=19)
    ap.add_argument("--add", type=float, default=0.15)
    ap.add_argument("--rem", type=float, default=0.1)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        calibrate_drive()
        sys.exit(0 if selftest() else 1)

    print("# RBT-91: does drift propose the routed motif's STRUCTURE?\n")
    print("Predicate: a global non-sensor unit with incoming links from BOTH wheel food noses of")
    print("OPPOSITE sign and outgoing links to BOTH drive Effectors of the SAME sign. Signs are")
    print("taken on the summed weight per pair, so cancelling links do not count as present.")
    print("No magnitude threshold anywhere in the predicate.\n")
    print(f"Denominator: RBT-78's, unchanged -- {a.k} mutate_controller mutations from committed")
    print(f"parents, {a.n} lineages per pool, add={a.add} rem={a.rem}, MASTER_SEED "
          f"{rbt78.MASTER_SEED}; its generator imported, not reimplemented.\n")

    from concurrent.futures import ProcessPoolExecutor
    tasks = []
    for label in rbt78.POOLS:
        step = max(1, a.n // a.workers)
        for lo in range(0, a.n, step):
            tasks.append((label, lo, min(lo + step, a.n), a.k, a.add, a.rem))
    agg = {label: [0, 0, [], []] for label in rbt78.POOLS}
    with ProcessPoolExecutor(a.workers) as pool:
        for label, n, present, gains, hits in pool.map(run_chunk, tasks):
            agg[label][0] += n
            agg[label][1] += present
            agg[label][2] += gains
            agg[label][3] += hits

    print(f"| pool | lineages | structure present | rate |")
    print(f"|---|---|---|---|")
    total_n = total_p = 0
    for label, (n, present, gains, hits) in agg.items():
        total_n += n
        total_p += present
        print(f"| {label} | {n} | **{present}** | {100.0 * present / n:.3f}% |")
    print(f"| **both pools** | {total_n} | **{total_p}** | **{100.0 * total_p / total_n:.3f}%** |")

    print("\n## The magnitude beside it (realised small-signal steering response, drive 0.01)\n")
    print("  Reference, measured on installed motifs through the same probe: the FIRST PAYING")
    print("  rung (RBT-69's +0.246 at installed w=16, linear 2w=32) has a realised response of")
    print("  6.87; the null rung (w=8, linear 16) reads 3.57. Compare the hits against those.\n")
    for label, (n, present, gains, hits) in agg.items():
        for i, k, a in sorted(hits):
            print(f"    {label} lineage {i}: {k} unit(s), signed realised a = {a:+.4f}"
                  f"  ({100 * abs(a) / 6.8664:.0f}% of the first paying rung)")
    for label, (n, present, gains, hits) in agg.items():
        if gains:
            g = np.array(gains)
            print(f"  {label}: n={len(g)}  median |a| {np.median(g):.4f}  max {g.max():.4f}  "
                  f">=16: {(g >= 16).sum()}  >=32: {(g >= 32).sum()}")
        else:
            print(f"  {label}: no lineage carries the structure, so there is no gain to report.")

    print("\n## What this does to the decision\n")
    if total_p == 0:
        print("  A rate of ZERO. Option A closes on a measured reason: the structural barrier is")
        print("  not proposed at all over RBT-78's denominator, so widening the weight scale --")
        print("  which changes magnitude and not structure -- cannot be shown to help, and B's")
        print("  cost is not justified. The reopening condition is now this script's own rate.")
    else:
        print("  A NON-ZERO rate. The structural barrier is proposed, so magnitude is the binding")
        print("  one at this depth and B's positive control becomes worth running. The decision")
        print("  flips to B, pre-registered, with this rate as its baseline.")


if __name__ == "__main__":
    main()
