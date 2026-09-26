"""RBT-74 adversary: the report diagnoses its own confound and then does not price it.

Named adversary: the tp6zdu lead, assigned by the coordinator at 03:40.

The report finds that the paired design pairs founders only -- both populations share one RNG
stream, the protected arm consumes it differently, so from generation 1 the wheeled opponent is
an independent draw -- and that the eight runs split by whether that opponent ended as a §4.5
runaway driver. It calls this "the design's largest limitation" and stops there, reporting the
paired mean of +0.064 as the headline with the verdict read off it.

Two things follow that it does not compute.

1. If the pairing is void, the paired SE should not beat the unpaired SE. Pairing only helps when
   pairs are positively correlated; if the dominant variable is assigned independently across the
   pair, pairing costs a degree of freedom and buys nothing. That is a testable claim about the
   numbers already in the readout, and it is a sharper demonstration than the argument from RNG
   streams because it needs no knowledge of the implementation.

2. The opponent split is not just a caveat, it is a quantity. If the runaway/driving gap and the
   composition of each arm are both known, the difference that composition alone predicts can be
   computed and compared against the observed one, and the effect can be stratified on opponent
   type to see what survives.

Numbers are the report's own, from runs/RBT-74/readout.txt and toolkit.txt. No simulation.
"""
import numpy as np
from itertools import combinations

# (seed, base final-fifth, prot final-fifth) -- readout.txt
PAIRS = [(201, 0.469, 0.407), (202, 0.367, 0.593), (203, 0.390, 0.333), (204, 0.326, 0.474)]
# runs whose WHEELED opponent ended as a runaway driver (toolkit.txt: approach < 0)
RUNAWAY = {("base", 201), ("prot", 204), ("prot", 202), ("prot", 201)}

base = np.array([b for _, b, _ in PAIRS]); prot = np.array([p for _, _, p in PAIRS])
d = prot - base

print("=== 1. reproduce the headline ===")
print(f"  differences {[f'{x:+.3f}' for x in d]}  mean {d.mean():+.4f}  "
      f"SE {d.std(ddof=1)/np.sqrt(len(d)):.4f}  positive {(d>0).sum()}  zeros {(np.abs(d)<0.01).sum()}")
print(f"  report: mean +0.064, SE 0.073, 2 positive, 0 zeros -> "
      f"{'MATCHES' if abs(d.mean()-0.064)<5e-4 else 'DIFFERS'}")

print("\n=== 2. is the pairing doing anything? ===")
se_paired = d.std(ddof=1) / np.sqrt(len(d))
se_unpaired = np.sqrt(base.var(ddof=1)/len(base) + prot.var(ddof=1)/len(prot))
r = np.corrcoef(base, prot)[0, 1]
print(f"  paired SE   {se_paired:.4f}")
print(f"  unpaired SE {se_unpaired:.4f}")
print(f"  corr(base, prot) across seeds: {r:+.4f}")
print(f"  -> pairing {'COSTS' if se_paired > se_unpaired else 'buys'} precision here "
      f"({se_paired/se_unpaired:.2f}x the unpaired SE), which is what an independently")
print(f"     assigned dominant variable does. The report's RNG-stream diagnosis is visible")
print(f"     in its own headline number.")

print("\n=== 3. what does the opponent draw alone predict? ===")
lab = lambda arm, s: (arm, s) in RUNAWAY
vals = [(arm, s, v) for (s, b, p) in PAIRS for arm, v in (("base", b), ("prot", p))]
run_v = np.array([v for a, s, v in vals if lab(a, s)])
dri_v = np.array([v for a, s, v in vals if not lab(a, s)])
gap = run_v.mean() - dri_v.mean()
f_prot = sum(1 for a, s, v in vals if a == "prot" and lab(a, s)) / 4
f_base = sum(1 for a, s, v in vals if a == "base" and lab(a, s)) / 4
print(f"  runaway opponents n={len(run_v)} mean {run_v.mean():.4f};  "
      f"driving n={len(dri_v)} mean {dri_v.mean():.4f};  gap {gap:+.4f}")
print(f"  runaway share: protected {f_prot:.2f}, baseline {f_base:.2f}")
print(f"  difference predicted by composition alone: {(f_prot-f_base)*gap:+.4f}")
print(f"  difference observed:                       {d.mean():+.4f}")
print(f"  -> composition accounts for {100*(f_prot-f_base)*gap/d.mean():.0f}% of the headline")

print("\n=== 4. stratify on opponent type: what survives? ===")
strata = []
for name, keep in (("runaway", True), ("driving", False)):
    b = [v for a, s, v in vals if a == "base" and lab(a, s) == keep]
    p = [v for a, s, v in vals if a == "prot" and lab(a, s) == keep]
    if b and p:
        strata.append(np.mean(p) - np.mean(b))
        print(f"  {name:8} base n={len(b)} mean {np.mean(b):.4f}   "
              f"prot n={len(p)} mean {np.mean(p):.4f}   diff {np.mean(p)-np.mean(b):+.4f}")
print(f"  stratified estimate (unweighted mean of the two strata): {np.mean(strata):+.4f}")
print(f"  against the unstratified {d.mean():+.4f}")

print("\n=== 5. the report's own probability claim ===")
n = sum(1 for _ in combinations(range(8), 4))
ge3 = sum(1 for c in combinations(range(8), 4) if len([i for i in c if i >= 4]) >= 3)
print(f"  P(>=3 of the 4 runaways are protected runs | no effect) = {ge3}/{n} = {ge3/n:.4f}"
      f"   report says 0.24 -> {'MATCHES' if abs(ge3/n-0.24)<0.01 else 'DIFFERS'}")

# --------------------------------------------------------------------------- #
# 6. The report's own instrument-hygiene line says "the summary step collapses two wheeled
# populations into one 'opponent'". Runaway/driving is a dichotomy over a continuous
# variable (wheeled approach, -19.08 to +1.84 m), so the stratified estimate in 4 inherits
# that collapse and rests on n=1 cells. Use the continuous covariate instead: regress the
# holistic final fifth on the opponent's approach, and ask whether ARM adds anything to the
# residual. If the arm effect is real it should survive; if it is opponent draw it should not.
# --------------------------------------------------------------------------- #
print("\n=== 6. continuous covariate, not the dichotomy ===")
APPROACH = {("base", 201): -19.08, ("prot", 204): -13.42, ("prot", 202): -7.72,
            ("prot", 201): -6.97, ("base", 203): 1.05,
            ("base", 204): 1.48, ("base", 202): 1.82, ("prot", 203): 1.84}
x = np.array([APPROACH[(a, s)] for a, s, v in vals])
y = np.array([v for a, s, v in vals])
arm = np.array([1.0 if a == "prot" else 0.0 for a, s, v in vals])
b1, b0 = np.polyfit(x, y, 1)
resid = y - (b0 + b1 * x)
print(f"  holistic = {b0:+.4f} {b1:+.5f} * wheeled_approach    r = {np.corrcoef(x, y)[0,1]:+.4f}")
print(f"  residual mean, protected {resid[arm==1].mean():+.4f}   baseline {resid[arm==0].mean():+.4f}"
      f"   difference {resid[arm==1].mean()-resid[arm==0].mean():+.4f}")
X = np.column_stack([np.ones(8), x, arm])
coef, *_ = np.linalg.lstsq(X, y, rcond=None)
print(f"  two-covariate fit: arm coefficient {coef[2]:+.4f} (vs the raw {d.mean():+.4f})")
print(f"  -> once the opponent enters as a number rather than a label, the arm term is"
      f" {abs(coef[2])/abs(d.mean()):.2f}x the raw difference")
