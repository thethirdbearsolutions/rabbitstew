"""RBT-116 design adversary, r6 re-read: r6's own power.py (@ 1295195) row()/unit()/verdict(), unchanged, at r6's
registered K = 5, with holistic confirmed rates moved.  (r5_attack.py cannot run on r6: unit() now takes confirmed
rates and K.)  Plateaus are r6's D = 16 priors (Q_H 0.70, Q_P 0.50) unless stated.

    python3 runs/RBT-116/design-adversary/r6_attack.py [path/to/r6 power.py] > r6_attack.txt
"""
import importlib.util
import random
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-116/power.py"
spec = importlib.util.spec_from_file_location("p6", path)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
QH, QP, K = 0.70, 0.50, 5
S = min(P.SENS_C_TWO, P.SENS_C_ONE)
ROWS = [
    ("r6 null (EPS_C .005 both)", dict(pH=.04, qH=QH, sH=S, euH=P.EPS_C, enH=P.EPS_C, pP=.04, qP=QP)),
    ("gap at G4's cap .05 vs .01 (r6's registered row)", dict(pH=.04, qH=QH, sH=S, euH=.05, enH=.01, pP=.04, qP=QP)),
    ("gap at cap, N fully purged: .05 vs 0", dict(pH=.04, qH=QH, sH=S, euH=.05, enH=0.0, pP=.04, qP=QP)),
    ("gap beyond cap (U drifts up in evolution): .08 vs .01", dict(pH=.04, qH=QH, sH=S, euH=.08, enH=.01, pP=.04, qP=QP)),
    ("gap beyond cap: .10 vs .01", dict(pH=.04, qH=QH, sH=S, euH=.10, enH=.01, pP=.04, qP=QP)),
    ("bypass p .5, SENS_C .32 (r6 min)", dict(pH=.5, qH=QH, sH=S, euH=P.EPS_C, enH=P.EPS_C, pP=.04, qP=QP)),
    ("bypass p .5, SENS_C .20", dict(pH=.5, qH=QH, sH=.20, euH=P.EPS_C, enH=P.EPS_C, pP=.04, qP=QP)),
    ("bypass p .5, SENS_C .10 (G8(f) weak)", dict(pH=.5, qH=QH, sH=.10, euH=P.EPS_C, enH=P.EPS_C, pP=.04, qP=QP)),
    ("bypass p .5, SENS_C .32, plateau Q_H .41 (D 4 prior)", dict(pH=.5, qH=.41, sH=S, euH=P.EPS_C, enH=P.EPS_C, pP=.04, qP=QP)),
    ("bypass p .5, SENS_C .32, plateau Q_H .21 (designed u)", dict(pH=.5, qH=.21, sH=S, euH=P.EPS_C, enH=P.EPS_C, pP=.04, qP=QP)),
]


def main():
    rng = random.Random(11606)
    reps, n = 300, 24
    print(f"# r6_attack.py on {path}: n {n}, K {K}, {reps} readouts per row; r6's row()/verdict() unchanged")
    print("scenario".ljust(58) + "".join(f"{v.split(':')[0][:10]:>11s}" for v in P.VERDICTS))
    for lab, kw in ROWS:
        cnt, _ = P.row(rng, reps, n, K, **kw)
        print(lab.ljust(58) + "".join(f"{cnt[v] / reps:11.3f}" for v in P.VERDICTS), flush=True)
    print("\n# expected confirmed steerers of 40 at plateau Q x SENS_C (K = 5):")
    for q in (.70, .41, .21):
        print("#   Q " + f"{q:.2f}: " + "  ".join(f"SENS_C {s:.2f} -> {q * s * 40:4.1f}" for s in (.48, .32, .20, .10)))


if __name__ == "__main__":
    main()
