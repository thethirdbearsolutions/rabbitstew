"""RBT-120 design adversary: two checks on runs/RBT-120/power.py (imported unchanged; nothing re-derived).

1. Q3 under the null for Q3's reading: the budget changes nothing (rho_up = rho_down = 1, E d = RBT-117's +0.768).
   PREREGISTRATION §7 reads Q3 NOT DECIDED as "RBT-117's HOLISTIC RESPONDS MORE does not survive the budget"; that
   reading needs P(NOT DECIDED | the margin survives) to be small.
2. The replicate-noise assumption.  power.py draws B's per-seed deviation from (O - Z)/sqrt 2 and holds O at its
   observed value, so Var(Delta) = sigma^2.  If B, once it diverges at generation 0 (a third of founders move;
   probe_clamp.txt), is an independent replicate of O at the same founders, Var(Delta) = 2 sigma_w^2, sigma_w^2 the
   within-founder replicate variance, which is <= sigma^2 but not shown <= sigma^2 / 2.  Bound: noise x sqrt 2
   (founders explain none of the replicate variance).
    python runs/RBT-120/design-adversary/power_adv.py > runs/RBT-120/design-adversary/power_adv.txt
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import power as P  # noqa: E402

rows = P.per_seed()
S = P.SEEDS
_noise = P.noise


def run(scale):
    P.RNG = np.random.default_rng(120)
    P.noise = lambda rows, key: scale * _noise(rows, key)
    print(f"\n## replicate noise x {scale:.3f}")
    bO = np.mean([rows[s]["b_div"] for s in S])
    for k in ("floor", "ceiling"):
        E = np.array([rows[s]["rho_up"] * rows[s]["b_up"] + rows[s]["rho"][k] * rows[s]["b_down"] for s in S])
        _, q1, _, q2 = P.verdicts(E, rows)
        print(f"  {k:8s} E Delta {(bO - E.mean()) / P.B.SIGMA0_REF:+.3f} sigma0  Q2 " + "  ".join(f"{a} {b:.3f}" for a, b in q2.items())
              + f"   Q1 RESPONDS {q1['RESPONDS']:.3f}")
    for rd in (1.0, 0.7, 0.5):
        E = np.array([rows[s]["b_up"] + rd * rows[s]["b_down"] for s in S])
        _, _, _, q2 = P.verdicts(E, rows)
        print(f"  rho_down {rd:.1f}  Q2 " + "  ".join(f"{a} {b:.3f}" for a, b in q2.items()))
    for lab, E_UD in (("Q3 null: budget changes nothing (E d = RBT-117's)", np.array([rows[s]["UC"] + rows[s]["CD"] for s in S])),
                      ("Q3 floor", np.array([rows[s]["rho_up"] * rows[s]["UC"] + rows[s]["rho"]["floor"] * rows[s]["CD"] for s in S])),
                      ("Q3 ceiling", np.array([rows[s]["rho_up"] * rows[s]["UC"] + rows[s]["rho"]["ceiling"] * rows[s]["CD"] for s in S]))):
        dm, v = P.q3(E_UD, rows)
        print(f"  {lab}: E d {dm:+.3f}  " + "  ".join(f"{a} {b:.3f}" for a, b in v.items()))


print("# RBT-120 design adversary: power.py (unchanged) under two stated alternatives; 2000 reruns each, RNG 120")
run(1.0)
run(np.sqrt(2))
