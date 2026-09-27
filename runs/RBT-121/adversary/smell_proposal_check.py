"""RBT-121 adversary: does auditor C's model implement C's own proposed smell_gain the way the simulator would?

    PYTHONPATH=<dir holding C's probe_world.py> python runs/RBT-121/adversary/smell_proposal_check.py [n]

C's probe_proposal.py applies GAIN as diff = GAIN * (I_left - I_right) on the SQUASHED intensities.  C's AUDIT.md
proposes a per-sensor centred log contrast c_i = tanh(G (ln S_i - ln S_root)).  This runs C's kinematic model
unchanged except that the two nose readings are replaced by that contrast (root = the point 0.10 m behind the nose
midpoint, i.e. the model's body centre), so the controller sees omega = OMEGA tanh(k (c_L - c_R)).  Same seeds as
C's probe_proposal (30000+), calibrated cell (turn 0.5, noise 1.0), v 0.25.
"""
import sys

import numpy as np

import probe_world as P

n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
P.OMEGA, P.NOISE = 0.5, 1.0
_state = {}


def lnS(w, pt, food):
    return np.log(max(float(np.exp(-np.linalg.norm(food - pt, axis=1) / w.decay).sum()), 1e-300))


def contrast_intensity(w, pt, food):
    if "left" not in _state:
        _state["left"] = pt
        return 0.0
    pl, pr = _state.pop("left"), pt
    lat = (pl - pr) / (2 * P.NOSE_LAT)
    fwd = np.array([lat[1], -lat[0]])
    root = (pl + pr) / 2 - P.NOSE_FWD * fwd
    G = _state["G"]
    r = lnS(w, root, food)
    cl, cr = np.tanh(G * (lnS(w, pl, food) - r)), np.tanh(G * (lnS(w, pr, food) - r))
    return -(cl - cr)  # C's bout computes diff = GAIN * (il - ir) = 0 - (-(cl - cr))


orig = P.intensity


def m(w, c, k, v=0.25):
    x = np.array([P.bout(w, v, c, k, 30000 + s) for s in range(n)], float)
    return x.mean(), x.std(ddof=1) / np.sqrt(n)


PW = dict(patches=2, patch_radius=0.4, smell="log", decay=1.5, regrow="delay", regrow_delay=60.0, radius=4.0)
print(f"# n = {n}; turn 0.5 rad/s, noise 1.0; v 0.25; seeds 30000+ (C's probe_proposal)")
for wname, w in (("uniform", P.World("W0")), ("HP", P.World("W0p", patches=3)), ("PW", P.World("PW", **PW))):
    P.intensity = orig
    blind = max(m(w, "straight", 0)[0], m(w, "arc", 0)[0])
    rows = []
    for label, setup in (("C model GAIN 10 x (I_L - I_R)", ("gain", 10.0)), ("proposal tanh(10 ln-contrast)", ("contrast", 10.0)),
                         ("proposal tanh(2.5 ln-contrast)", ("contrast", 2.5))):
        if setup[0] == "gain":
            P.intensity, P.GAIN = orig, setup[1]
        else:
            P.intensity, P.GAIN = contrast_intensity, 1.0
            _state.clear(); _state["G"] = setup[1]
        r = {k: m(w, "smell", k) for k in (1.0, 1.4, 2.0, 2.4, 6.0)}
        rows.append(f"   {label:32s} k6 {r[6.0][0]:4.2f}±{r[6.0][1]:4.2f} (x{r[6.0][0] / blind:4.2f})  k1->1.4 {100 * (r[1.4][0] / r[1.0][0] - 1):+4.0f}%  "
                    f"k2->2.4 {100 * (r[2.4][0] / r[2.0][0] - 1):+4.0f}%  k1 {r[1.0][0]:4.2f}")
    P.GAIN = 1.0; P.intensity = orig
    print(f"{wname}: blind-best {blind:4.2f}", flush=True)
    print("\n".join(rows), flush=True)
