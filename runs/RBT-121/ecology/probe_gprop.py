"""RBT-121 audit C, after adversary #403 (6b): the PW proposal with the *proposal's* sensor, not the model's GAIN.
Each nose reads c = tanh(G * (ln S_nose - b)); b is a per-robot running mean of ln S (tau 2 s) or, for comparison,
ln S at the robot's centre (root-centring, which #403 shows deletes root, single-nose and temporal smell in real
bodies).  Calibrated regime (turn 0.5 rad/s, noise 1.0), v = 0.25, n paired seeds (same seed across controllers).
Columns, items per season (one 15 s bout): blind best; k6 - blind; first weak nose k0.4 - blind; steps k1->1.4 and
k2->2.4, each a paired mean difference with its SE; and +25% speed for the blind straight mover.

python3 probe_gprop.py <world> <centre> <G> [n]"""
import sys
import numpy as np
import probe_world as P
WORLDS = {"uniform": P.World("committed uniform"), "HP": P.World("committed HP", patches=3),
          "PW": P.World("PW", patches=2, patch_radius=0.4, smell="log", decay=1.5, regrow="delay", regrow_delay=60.0, radius=4.0)}
wname, centre, G = sys.argv[1], sys.argv[2], float(sys.argv[3])
n = int(sys.argv[4]) if len(sys.argv) > 4 else 300
w = WORLDS[wname]
P.OMEGA, P.NOISE, P.CENTRE, P.G_PROP = 0.5, 1.0, centre, G
seeds = [50000 + s for s in range(n)]
def v(ctrl, k, speed=0.25): return np.array([P.bout(w, speed, ctrl, k, s) for s in seeds], float)
st, ar = v("straight", 0), v("arc", 0)
blind = st if st.mean() >= ar.mean() else ar
fast = v("straight", 0, 0.3125)
K = {k: v("smell", k) for k in (0.4, 1.0, 1.4, 2.0, 2.4, 6.0)}
def d(a, b): x = a - b; return f"{x.mean():+.3f}±{x.std(ddof=1) / np.sqrt(n):.3f}"
print(f"{w.name:18s} {centre:7s} G {G:4.1f}  blind {blind.mean():5.2f}  k6-blind {d(K[6.0], blind)}  k0.4-blind {d(K[0.4], blind)}  "
      f"k1->1.4 {d(K[1.4], K[1.0])}  k2->2.4 {d(K[2.4], K[2.0])}  | +25% speed {d(fast, st)} ({100 * (fast.mean() / st.mean() - 1):+.0f}%)", flush=True)
