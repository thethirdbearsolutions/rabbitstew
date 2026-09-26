"""Adversary check on RBT-78's truncation finding, and on what should replace the path column.

Three questions, in order:

1. REPRODUCE. Is the recurrent core's spectral radius really above 1 on every committed best?
   rho(M) > 1 means sum_k M^k has no limit and the depth-4 value is a truncation artifact.

2. IS DIVERGENCE THE RIGHT DIAGNOSIS? The network is a = tanh(W a + b), which cannot diverge:
   activations live in [-1, 1] by construction. So the linearisation diverges where the thing
   it linearises does not, and the question is not "does the series converge" but "does any
   truncation of it bound the realised gain". Compare the linear path sum against the network's
   own behaviour: drive the food sensors apart by a known amount, run the real recurrent update
   to a fixed point, and read the actual steering response.

3. WHAT SHOULD steering_gain.py REPORT? (the script is mine; RBT-62's PATH column uses it.)
   Candidate: the measured Jacobian above -- finite, tanh included, no depth parameter to choose.

No simulation of a world; this is the controller alone. Usage: adversary_truncation.py
"""
import glob, json, os, sys

import numpy as np

sys.path.insert(0, "runs/RBT-78")
from reconcile import _load, _nose_eff, POOLS

from rabbitstew.brain import RuntimeBrain
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize


def spectral(ph):
    """rho of the full signed weight matrix, and of the recurrent (non-sensor) core."""
    n = len(ph.units)
    M = np.zeros((n, n))
    for s, d, w in ph.links:
        M[d, s] += w
    rho_full = float(np.abs(np.linalg.eigvals(M)).max()) if n else 0.0
    core = [i for i, u in enumerate(ph.units) if u.unit.kind != "sensor"]
    rho_core = float(np.abs(np.linalg.eigvals(M[np.ix_(core, core)])).max()) if core else 0.0
    return rho_full, rho_core


def measured_steering(ph, drive=1.0, ticks=400):
    """The network's ACTUAL steering response to a known nose differential.

    Runs the real update a <- f(W a + b) with the food noses clamped to +-drive/2, to a fixed
    point, and reads (e1 + e2) -- the steering axis. Differenced against the same run with the
    noses clamped equal, so only the differential matters. tanh included; no depth choice.
    """
    nose, eff = _nose_eff(ph)
    if len(nose) != 2 or len(eff) != 2:
        return None
    out = []
    for d in (0.0, drive):
        b = RuntimeBrain(ph)
        vals = np.zeros(len(b.sensors))
        for j, s in enumerate(b.sensors):
            if s.part == 1 and s.source == "food":
                vals[j] = 0.5 + d / 2
            elif s.part == 2 and s.source == "food":
                vals[j] = 0.5 - d / 2
        for _ in range(ticks):
            b.step(vals)
        out.append(b.activation[eff[1]] + b.activation[eff[2]])
    return (out[1] - out[0]) / drive        # steering response per unit nose differential


def linear_a(ph, depth):
    nose, eff = _nose_eff(ph)
    n = len(ph.units)
    M = np.zeros((n, n))
    for s, d, w in ph.links:
        M[d, s] += w
    sg = {}
    for part, si in nose.items():
        v = np.zeros(n); v[si] = 1.0; tot = np.zeros(n)
        for _ in range(depth):
            v = M @ v; tot += v
            if not v.any():
                break
        sg[part] = tot[eff[1]] + tot[eff[2]]
    return (sg[1] - sg[2]) / 2.0


print(f"{'genotype':38} {'rho(full)':>10} {'rho(core)':>10} "
      f"{'a@d1':>9} {'a@d4':>10} {'a@d8':>12} {'measured':>10}")
rows = []
for label, (d, how) in POOLS.items():
    cfg = SimConfig.from_dict(json.load(open(os.path.join(d, "config.json")))["sim"])
    files = (sorted(glob.glob(os.path.join(d, "conventional", "*.json"))) if how == "bests"
             else sorted(glob.glob(os.path.join(d, "conventional", "final", "*.json")))[:7])
    for f in files:
        ph = synthesize(Genotype.load(f), cfg.synthesis)
        rf, rc = spectral(ph)
        m = measured_steering(ph)
        a1, a4, a8 = linear_a(ph, 1), linear_a(ph, 4), linear_a(ph, 8)
        rows.append((rf, rc, m, a1, a4, a8))
        print(f"{os.path.basename(f)[:28]:38} {rf:10.3f} {rc:10.3f} "
              f"{a1:9.4f} {a4:10.3f} {a8:12.2f} {('%.4f' % m) if m is not None else 'n/a':>10}")

rf = np.array([r[0] for r in rows]); rc = np.array([r[1] for r in rows])
mm = np.array([r[2] if r[2] is not None else 0.0 for r in rows])
print(f"\nn = {len(rows)} genotypes")
print(f"  rho(full) range [{rf.min():.3f}, {rf.max():.3f}]   above 1: {int((rf > 1).sum())}/{len(rf)}")
print(f"  rho(core) range [{rc.min():.3f}, {rc.max():.3f}]   above 1: {int((rc > 1).sum())}/{len(rc)}")
print(f"  MEASURED steering response per unit nose differential: "
      f"median {np.median(np.abs(mm)):.4f}, max {np.abs(mm).max():.4f}")
print("  (the effector sum is bounded by 2 by construction, so the realised gain cannot exceed")
print("   2 per unit differential however large the linear path sum grows)")

# --------------------------------------------------------------------------- #
# Calibration (rule II): put the KNOWN-GOOD motif on the same instrument, at the three
# weights RBT-61 measured behaviourally, and see what realised steering gain each buys.
# Without this the measured column has no scale and cannot be compared to a=16/32/64,
# which are weight-space numbers, not realised-gain numbers.
# --------------------------------------------------------------------------- #
print("\n=== calibration: the RBT-61 motif installed at its three measured weights ===")
print("    NOTE against my own first proposal: at drive=1 this instrument SATURATES -- all three")
print("    weights read the same number, so it cannot separate RBT-61's null point from its")
print("    paying one. tanh is linear near zero, so the probe must be small-signal. Both shown.")
cfg0 = SimConfig.from_dict(json.load(open(os.path.join(POOLS["W4b-801-bests"][0], "config.json")))["sim"])
f0 = sorted(glob.glob(os.path.join(POOLS["W4b-801-bests"][0], "conventional", "*.json")))[3]
print(f"    host: {os.path.basename(f0)}   (a@d1 = {linear_a(synthesize(Genotype.load(f0), cfg0.synthesis), 1):.4f} before install)")
print(f"    {'installed w':>12} {'a (=2w)':>9} {'RBT-61 items':>14} {'measured gain':>15}")
for drive in (1.0, 0.01):
    print(f"    --- drive = {drive:g} {'(saturated, unusable)' if drive == 1.0 else '(small-signal)'}")
    for w, items in ((8.0, "+0.054 (null)"), (16.0, "+0.246"), (32.0, "+0.897")):
        ph0 = synthesize(Genotype.load(f0), cfg0.synthesis)
        nose, eff = _nose_eff(ph0)
        ph0.links = list(ph0.links) + [(nose[1], eff[1], w), (nose[1], eff[2], w),
                                       (nose[2], eff[1], -w), (nose[2], eff[2], -w)]
        print(f"    {w:12g} {2*w:9g} {items:>14} {measured_steering(ph0, drive=drive):15.4f}")

print("\n=== the evolved population on the calibrated (small-signal) instrument ===")
for label, (d, how) in POOLS.items():
    c = SimConfig.from_dict(json.load(open(os.path.join(d, "config.json")))["sim"])
    fs = (sorted(glob.glob(os.path.join(d, "conventional", "*.json"))) if how == "bests"
          else sorted(glob.glob(os.path.join(d, "conventional", "final", "*.json")))[:7])
    mv = [measured_steering(synthesize(Genotype.load(f), c.synthesis), drive=0.01) for f in fs]
    mv = np.array([x for x in mv if x is not None])
    print(f"    {label:18} median |gain| {np.median(np.abs(mv)):8.4f}   max {np.abs(mv).max():8.4f}"
          f"   (w=32, the paying weight, reads 32.2)")

# how well does each linear depth predict the realised response?
print("\n=== which linear depth tracks the network's actual behaviour? ===")
d1 = np.array([r[3] for r in rows]); d4 = np.array([r[4] for r in rows]); d8 = np.array([r[5] for r in rows])
for tag, v in (("depth 1 (direct)", d1), ("depth 4 (the path column)", d4), ("depth 8", d8)):
    nz = (np.abs(v) > 1e-9) | (np.abs(mm) > 1e-9)
    agree = np.sign(v[nz]) == np.sign(mm[nz])
    r = np.corrcoef(v, mm)[0, 1] if np.std(v) > 0 else float("nan")
    print(f"    {tag:26} corr with measured {r:+.4f}   sign agreement {int(agree.sum())}/{int(nz.sum())}")
