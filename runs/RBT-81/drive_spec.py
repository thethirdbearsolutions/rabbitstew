"""What drive should the measured column use? Asserting 0.01 is the same move that
produced the drive=1 saturation defect. A fixed drive cannot be right for all gains:
saturation sets in when gain*drive ~ 1, so a robot at gain 64 saturates at a drive a
robot at gain 1 is fine with. Test an auto-halving rule that removes the parameter."""
import glob, json, os, sys
import numpy as np
sys.path.insert(0, "runs/RBT-78"); sys.path.insert(0, "runs/RBT-81")
from reconcile import POOLS, _nose_eff
from adversary import measured
from rabbitstew.analysis import steering_terms
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize

d0 = POOLS["W4b-801-bests"][0]
cfg = SimConfig.from_dict(json.load(open(os.path.join(d0, "config.json")))["sim"])
f0 = sorted(glob.glob(os.path.join(d0, "conventional", "*.json")))[3]

def install(w):
    ph = synthesize(Genotype.load(f0), cfg.synthesis)
    nose, eff = _nose_eff(ph)
    ph.links = list(ph.links) + [(nose[1], eff[1], w), (nose[1], eff[2], w),
                                 (nose[2], eff[1], -w), (nose[2], eff[2], -w)]
    return ph

def converged(ph, tol=0.01, start=0.1, floor=1e-7):
    """Halve the drive until the reading moves by less than tol; return (gain, drive, steps)."""
    d, prev, steps = start, measured(ph, drive=start), 0
    while d > floor:
        d /= 2; steps += 1
        cur = measured(ph, drive=d)
        if abs(cur - prev) <= tol * max(abs(cur), 1e-12):
            return cur, d, steps
        prev = cur
    return prev, d, steps

print("installed motif -- does a FIXED drive of 0.01 suffice at every gain?")
print(f"{'w':>5} {'true a=2w':>10} {'drive 0.1':>11} {'drive 0.01':>11} {'drive 0.001':>12} {'auto':>10} {'auto drive':>11}")
for w in (1.0, 8.0, 32.0, 128.0, 512.0):
    ph = install(w)
    g, dd, st = converged(ph)
    print(f"{w:5g} {2*w:10g} {measured(ph,drive=0.1):11.3f} {measured(ph,drive=0.01):11.3f} "
          f"{measured(ph,drive=0.001):12.3f} {g:10.3f} {dd:11.2e}")

print("\nevolved robots -- does auto-halving agree with a fixed 0.01?")
for label, (d, how) in POOLS.items():
    c = SimConfig.from_dict(json.load(open(os.path.join(d, "config.json")))["sim"])
    fs = (sorted(glob.glob(os.path.join(d, "conventional", "*.json"))) if how == "bests"
          else sorted(glob.glob(os.path.join(d, "conventional", "final", "*.json")))[:7])
    rows = []
    for f in fs:
        ph = synthesize(Genotype.load(f), c.synthesis)
        if steering_terms(ph) is None: continue
        fixed = measured(ph, drive=0.01)
        auto, dd, st = converged(ph)
        rows.append((fixed, auto, dd))
    if rows:
        mx = max(abs(a - fx) for fx, a, _ in rows)
        print(f"  {label:18} n={len(rows)}  max |auto - fixed(0.01)| = {mx:.6f}   "
              f"drives used {min(r[2] for r in rows):.1e}..{max(r[2] for r in rows):.1e}")
