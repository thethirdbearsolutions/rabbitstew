"""RBT-116 design adversary, r5 re-read: the r5 call (trajectory veto + confirmation battery) under r5's NAMED
transform (§4.2: reading_i = tanh(G (ln S_i - b_r)), b_r an EMA (tau 1 s) of the robot's mean ln S over its noses,
initialised at spawn; G 2.5), in the same PW kinematic caricature as steer_probe.py (layout, spawn, root eating).

Bodies:
  steer2-k      two noses (0.15 m either side, 0.10 m ahead): omega = 0.5 tanh(k (r_L - r_R))      (G8(c)'s kind)
  steer1-k      ONE nose at the root: omega = min(3, k max(0, -r)): turn when the contrast is negative, i.e.
                run-and-tumble on the temporal contrast (the §1.1 lone-nose route, the one r5 says the transform favours)
  ars-signed    G8(b) as r5 specifies it: one nose -> threshold -> slow and turn more when r > q (signed contrast)
  ars-abs       the same on |r| (sign-blind): undirected kinesis under this transform
  blind         no nose
Per genome: stage 2 (16 draws) and a confirmation battery (16 fresh draws); PASS = F >= 0.25 & lbF > 0 & lbdT > 0
& trajectory veto (intact and decoy paths differ on > 8 of 16 draws).  STEERS = PASS on both.
python3 runs/RBT-116/design-adversary/r5_probe.py [genomes] > r5_probe.txt
"""
import sys

import numpy as np

import steer_probe as S

G_TR, TAU = 2.5, 1.0


def season(ctrl, par, seed, theta):
    rng = np.random.default_rng(seed)
    bearing = rng.uniform(0, 2 * np.pi); dist = rng.uniform(1.5, 2.5)
    pos = dist * np.array([np.cos(bearing), np.sin(bearing)])
    head = np.arctan2(-pos[1], -pos[0]) + rng.uniform(-0.75 * np.pi, 0.75 * np.pi)
    food = S.layout(np.random.default_rng(seed + 7919), pos)
    alive = np.ones(S.ITEMS, bool)
    nrng = np.random.default_rng(seed + 104729)
    R = None
    if theta is not None:
        c, s = np.cos(theta), np.sin(theta); R = np.array([[c, -s], [s, c]])

    def lnS(pt):
        live = food[alive]
        src = live if R is None else live @ R.T
        return float(np.log(np.exp(-np.linalg.norm(src - pt, axis=1) / S.DECAY).sum() + 1e-6)) if len(src) else np.log(1e-6)

    def noses():
        if ctrl == "steer2":
            cc, ss = np.cos(head), np.sin(head)
            fwd, lat = np.array([cc, ss]), np.array([-ss, cc])
            return [lnS(pos + 0.1 * fwd + 0.15 * lat), lnS(pos + 0.1 * fwd - 0.15 * lat)]
        return [lnS(pos)] if ctrl != "blind" else []

    ls = noses()
    b = float(np.mean(ls)) if ls else 0.0
    eaten, num, den, path = 0, 0.0, 0.0, []
    for _ in range(int(round(S.DUR / S.DT))):
        ls = noses()
        if ls:
            b += (float(np.mean(ls)) - b) * S.DT / TAU
        r = [np.tanh(G_TR * (l - b)) for l in ls]
        v, noise, om = S.V0, S.NOISE, 0.0
        if ctrl == "steer2":
            om = S.OMEGA * np.tanh(par * (r[0] - r[1]))
        elif ctrl == "steer1":
            om = min(3.0, par * max(0.0, -r[0]))
        elif ctrl in ("ars-signed", "ars-abs"):
            x = r[0] if ctrl == "ars-signed" else abs(r[0])
            if x > par:
                v, noise = 0.08, 4.0
            else:
                v, noise = 0.30, 0.5
        head += om * S.DT + noise * np.sqrt(S.DT) * nrng.standard_normal()
        step = v * S.DT * np.array([np.cos(head), np.sin(head)])
        live = food[alive]
        if len(live):
            g = S.grad_dir(pos, live)
            num += float(np.dot(step / S.DT, g)); den += v
        pos = pos + step
        path.append(pos.copy())
        hit = alive & (np.linalg.norm(food - pos, axis=1) < S.EAT)
        eaten += int(hit.sum()); alive &= ~hit
    return eaten, (num / den if den > 0 else 0.0), np.array(path)


def passes(ctrl, par, block):
    fi, fd, ti, td, diff = [], [], [], [], 0
    trng = np.random.default_rng(900000 + block)
    for k in range(16):
        seed = 10_000 * (block + 1) + k
        a, b = season(ctrl, par, seed, None), season(ctrl, par, seed, np.radians(trng.uniform(30, 330)))
        fi.append(a[0]); fd.append(b[0]); ti.append(a[1]); td.append(b[1])
        diff += int(np.abs(a[2] - b[2]).max() > 1e-9)
    dF, dT = np.array(fi, float) - fd, np.array(ti) - np.array(td)

    def lb(x):
        s = x.std(ddof=1)
        return x.mean() - S.T95_15 * s / 4 if s > 0 else x.mean()
    ok = dF.mean() >= 0.25 and lb(dF) > 0 and lb(dT) > 0 and diff > 8
    return ok, dF.mean(), dT.mean(), np.mean(fi)


BODIES = [("blind", "blind", 0), ("steer2-k6", "steer2", 6.0), ("steer2-k32", "steer2", 32.0),
          ("steer1-k2", "steer1", 2.0), ("steer1-k8", "steer1", 8.0), ("steer1-k32", "steer1", 32.0),
          ("ars-signed-0.2", "ars-signed", 0.2), ("ars-signed-0.5", "ars-signed", 0.5),
          ("ars-abs-0.2", "ars-abs", 0.2), ("ars-abs-0.5", "ars-abs", 0.5)]

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    print(f"# r5_probe.py: {n} genomes per body; r5 transform (G {G_TR}, tau {TAU} s); r5 call; PW caricature")
    print("body             single-call PASS   confirmed STEERS   mean F    mean dT   food_intact")
    for lab, ctrl, par in BODIES:
        r1 = [passes(ctrl, par, g) for g in range(n)]
        r2 = [passes(ctrl, par, 5000 + g) for g in range(n)]
        p1 = np.mean([x[0] for x in r1]); pc = np.mean([a[0] and b[0] for a, b in zip(r1, r2)])
        print(f"{lab:16s} {p1:16.2f}   {pc:16.2f}   {np.mean([x[1] for x in r1]):+7.3f}  {np.mean([x[2] for x in r1]):+8.3f}  {np.mean([x[3] for x in r1]):8.2f}", flush=True)
