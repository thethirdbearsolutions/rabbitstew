"""RBT-116 design adversary, r5 re-read: r5's own power.py (@ 8ad0162) verdict() and unit(), attacked.

    python3 runs/RBT-116/design-adversary/r5_attack.py [path/to/r5 power.py] > r5_attack.txt

r5's unit() squares the per-call EPS and SENS (two independent calls).  Two things that can break that:
  * false passes that are a property of the GENOME (a body that passes once tends to pass again): the confirmed
    rate is EPS x P(repeat | pass), not EPS^2.  And G4 (§4.3) measures the CONFIRMED rate and caps it at 0.05, which
    power.py then squares again.  Rows below feed a confirmed rate c by passing eps = sqrt(c).
  * the steering route's own sensitivity: SENS 0.63 is steer_probe's two-nose steerer; the one-nose route (the one
    r5's transform is said to favour) may be far lower (r5_probe.txt).
Plateaus are r5's own D = 16 priors (power.txt part 1): Q_H 0.70, Q_P 0.468.
"""
import importlib.util
import math
import random
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-116/power.py"
spec = importlib.util.spec_from_file_location("p5", path)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

QH, QP = 0.70, 0.468
r = math.sqrt
# label, pH, QH, eps_u(H), eps_n(H), SENS for H
ROWS = [
    ("r5 null as registered (EPS .02/call, squared)", .04, QH, .02, .02, .63),
    ("null; confirmed H gap .02 vs .005 (repeat-given-pass .5)", .04, QH, r(.02), r(.005), .63),
    ("null; confirmed H gap .05 vs .01 (G4 cap read as confirmed)", .04, QH, r(.05), r(.01), .63),
    ("null; confirmed H .05 in U and N (no gap)", .04, QH, r(.05), r(.05), .63),
    ("bypass p .5, two-nose SENS .63 (r5's row)", .5, QH, .02, .02, .63),
    ("bypass p .5, one-nose SENS .35", .5, QH, .02, .02, .35),
    ("bypass p .5, one-nose SENS .20", .5, QH, .02, .02, .20),
    ("bypass p .75, one-nose SENS .20", .75, QH, .02, .02, .20),
    ("bypass p .5, one-nose SENS .10", .5, QH, .02, .02, .10),
]


def main():
    rng = random.Random(11605)
    reps, n = 300, 24
    s0 = P.SENS
    print(f"# r5_attack.py on {path}: n {n}, {reps} readouts per row; r5's verdict() and unit() unchanged")
    print("scenario".ljust(62) + "".join(f"{v.split(':')[0][:10]:>11s}" for v in P.VERDICTS))
    for lab, pH, qH, eu, en, sens in ROWS:
        cnt = dict.fromkeys(P.VERDICTS, 0)
        for _ in range(reps):
            P.SENS = sens
            UH = [P.unit(pH, qH, eu, en, rng) for _ in range(n)]
            P.SENS = s0
            UP = [P.unit(.04, QP, P.EPS, P.EPS, rng) for _ in range(n)]
            cnt[P.verdict(UH, UP, rng)] += 1
        print(lab.ljust(62) + "".join(f"{cnt[v] / reps:11.3f}" for v in P.VERDICTS), flush=True)
    print("\n# expected confirmed steerers of 40 in a line at plateau Q_H 0.70: SENS^2 x 0.70 x 40 =")
    for s in (.63, .35, .20, .10):
        print(f"#   SENS {s:.2f}: {s * s * .7 * 40:5.2f}  (CROSS_K = 3)")


if __name__ == "__main__":
    main()
