"""RBT-116 design adversary: can the STEERS call (PREREGISTRATION §1.2-1.3) fail, and can it pass?

A kinematic caricature of PW (auditor C's point-forager model, runs/RBT-121/ecology/probe_world.py, rules
restated here so the file stands alone): 12 items in 2 patches of 0.4 m, centres uniform in the 4 m disc,
0.8 m clearance, regrow 60 s (> the 15 s season, so no regrowth), smell=log, decay 1.5; random_start
(1.5-2.5 m out, heading within +-135 deg of the centre, simulation.py:585-601); eating from the root only
(eat_from=root: radius 0.35 about the mouth point).  NOT a simulator run.

The battery is the registration's: per genome, 16 paired draws of intact vs decoy (the LIVE layout rotated
about the origin by theta ~ U[30, 330] deg, RBT-97 RotatedSmell), F = mean(food_i - food_d),
T = sum|v| cos(v, g) / sum|v| over ticks with |v| > 0.05 m/s, g the analytic gradient of the REAL live
field sum exp(-d/1.5) at the centre of mass, dT = mean(T_i - T_d).  STEERS iff F >= 0.25 with one-sided 95%
t lower bound > 0, dT lower bound > 0, and at most 8 of 16 draws with food_i == food_d exactly.

Controllers (no body; a point centre of mass with a mouth):
  blind        coverage: speed v0, heading diffusion 1 rad/sqrt(s)                      (must be NONE)
  ortho-a      orthokinesis: speed v0 * max(0.1, 1 - a * I_root); heading as blind   (no heading term)
  klino-b      klinokinesis: heading diffusion x (1 + b * I_root); undirected turning
  steer2-k     two-nose klinotaxis, C's smell-k at gain 10 (positive control)
  steer1-k     one nose, temporal: turn rate k * max(0, -dI/dt) (run-and-tumble on a falling reading)
  orbit        constant arc (radius 0.6 m), speed modulated as ortho-1.0
  ars-q        area-restricted search: v 0.08 and diffusion 4 when I_root > q, else v 0.30 and diffusion 0.5
                 (klino- plus orthokinesis on the reading's level; no heading term, no gradient term)
  sweep        CoM creeps at 0.03 m/s (below the T threshold); the mouth (a limb-borne root) sweeps a 0.4 m
               circle at 1.5 rad/s, sweep rate x max(0.1, 1 - I_root)

python3 runs/RBT-116/design-adversary/steer_probe.py [genomes]  > steer_probe.txt
"""
import sys

import numpy as np

ITEMS, RADIUS, PATCHES, PRAD, DECAY, CLEAR, EAT, DUR, DT = 12, 4.0, 2, 0.4, 1.5, 0.8, 0.35, 15.0, 0.05
V0, NOISE, GAIN, OMEGA = 0.25, 1.0, 10.0, 0.5
T_MIN_SPEED = 0.05
T95_15 = 1.753  # one-sided 95% t, df 15


def layout(rng, start):
    r = RADIUS * np.sqrt(rng.random(PATCHES)); a = rng.uniform(0, 2 * np.pi, PATCHES)
    centres = np.c_[r * np.cos(a), r * np.sin(a)]
    out = []
    while len(out) < ITEMS:
        c = centres[rng.integers(0, PATCHES)]
        rr = PRAD * np.sqrt(rng.random()); aa = rng.uniform(0, 2 * np.pi)
        p = c + rr * np.array([np.cos(aa), np.sin(aa)])
        if np.linalg.norm(p) > RADIUS or np.linalg.norm(p - start) < CLEAR:
            continue
        out.append(p)
    return np.array(out)


def smell(pt, food):
    d = np.linalg.norm(food - pt, axis=1)
    return float(np.clip(np.log1p(np.exp(-d / DECAY).sum()) / np.log1p(ITEMS), 0, 1))


def grad_dir(pt, food):
    diff = food - pt
    d = np.linalg.norm(diff, axis=1) + 1e-12
    w = np.exp(-d / DECAY) / DECAY
    g = (w[:, None] * diff / d[:, None]).sum(0)
    n = np.linalg.norm(g)
    return g / n if n > 1e-15 else np.zeros(2)


def season(ctrl, par, seed, theta):
    """One solo season.  theta None = intact; else the food sensors smell the live layout rotated by theta."""
    rng = np.random.default_rng(seed)
    bearing = rng.uniform(0, 2 * np.pi); dist = rng.uniform(1.5, 2.5)
    pos = dist * np.array([np.cos(bearing), np.sin(bearing)])
    head = np.arctan2(-pos[1], -pos[0]) + rng.uniform(-0.75 * np.pi, 0.75 * np.pi)
    food = layout(np.random.default_rng(seed + 7919), pos)
    alive = np.ones(ITEMS, bool)
    nrng = np.random.default_rng(seed + 104729)  # the body's own noise: the SAME stream intact and decoy
    R = None
    if theta is not None:
        c, s = np.cos(theta), np.sin(theta); R = np.array([[c, -s], [s, c]])
    eaten, num, den, prev_I, phase = 0, 0.0, 0.0, None, 0.0

    def sensed(pt):
        live = food[alive]
        if not len(live):
            return 0.0
        src = live if R is None else live @ R.T
        return smell(pt, src)

    for _ in range(int(round(DUR / DT))):
        I = sensed(pos)
        noise = NOISE
        v = V0
        om = 0.0
        if ctrl == "ortho":
            v = V0 * max(0.1, 1 - par * I)
        elif ctrl == "klino":
            noise = NOISE * (1 + par * I)
        elif ctrl == "steer2":
            cc, ss = np.cos(head), np.sin(head)
            fwd, lat = np.array([cc, ss]), np.array([-ss, cc])
            diff = GAIN * (sensed(pos + 0.1 * fwd + 0.15 * lat) - sensed(pos + 0.1 * fwd - 0.15 * lat))
            om = OMEGA * np.tanh(par * diff)
        elif ctrl == "steer1":
            dI = 0.0 if prev_I is None else (I - prev_I) / DT
            om = min(3.0, par * max(0.0, -GAIN * dI))
        elif ctrl == "orbit":
            v = V0 * max(0.1, 1 - par * I)
            om = v / 0.6
        elif ctrl == "sweep":
            v = 0.03
        elif ctrl == "ars":  # area-restricted search: slow and tortuous above a threshold; no heading term
            if I > par:
                v, noise = 0.08, 4.0
            else:
                v, noise = 0.30, 0.5
        prev_I = I
        head += om * DT + noise * np.sqrt(DT) * nrng.standard_normal()
        step = v * DT * np.array([np.cos(head), np.sin(head)])
        live = food[alive]
        if len(live) and v > T_MIN_SPEED:
            g = grad_dir(pos, live)
            num += v * float(np.dot(step / (v * DT), g)); den += v
        pos = pos + step
        mouth = pos
        if ctrl == "sweep":
            phase += 1.5 * max(0.1, 1 - par * I) * DT
            mouth = pos + 0.4 * np.array([np.cos(phase), np.sin(phase)])
        d = np.linalg.norm(food - mouth, axis=1)
        hit = alive & (d < EAT)
        eaten += int(hit.sum()); alive &= ~hit
    return eaten, (num / den if den > 0 else 0.0)


def call(ctrl, par, g):
    """One genome's 16-draw call; g indexes a disjoint block of registered draws."""
    fi, fd, ti, td = [], [], [], []
    trng = np.random.default_rng(900000 + g)
    for k in range(16):
        seed = 10_000 * (g + 1) + k
        th = np.radians(trng.uniform(30, 330))
        a, b = season(ctrl, par, seed, None), season(ctrl, par, seed, th)
        fi.append(a[0]); fd.append(b[0]); ti.append(a[1]); td.append(b[1])
    dF, dT = np.array(fi) - np.array(fd), np.array(ti) - np.array(td)

    def lb(x):
        s = x.std(ddof=1)
        return x.mean() - T95_15 * s / 4 if s > 0 else (x.mean() if x.mean() != 0 else 0.0)
    F, T, zero = dF.mean(), dT.mean(), int((dF == 0).sum())
    c1 = F >= 0.25 and lb(dF) > 0
    c3 = zero <= 8
    if c1 and c3 and lb(dT) > 0:
        lab = "STEERS"
    elif c1 and c3:
        lab = "SMELL-USE"
    else:
        lab = "NONE"
    nov = "STEERS" if (c1 and lb(dT) > 0) else ("SMELL-USE" if c1 else "NONE")
    return lab, F, T, lb(dT), zero, np.mean(fi), np.mean(ti), np.mean(td), nov


BODIES = [("blind", "blind", 0), ("ortho-a0.6", "ortho", 0.6), ("ortho-a0.9", "ortho", 0.9),
          ("ortho-a1.2", "ortho", 1.2), ("klino-b3", "klino", 3.0), ("klino-b8", "klino", 8.0),
          ("steer2-k6", "steer2", 6.0), ("steer2-k32", "steer2", 32.0),
          ("steer1-k2", "steer1", 2.0), ("steer1-k8", "steer1", 8.0),
          ("orbit-a0.9", "orbit", 0.9), ("sweep-a0.9", "sweep", 0.9),
          ("ars-0.50", "ars", 0.50), ("ars-0.60", "ars", 0.60), ("ars-0.70", "ars", 0.70)]

if __name__ == "__main__":
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    print(f"# RBT-116 design adversary, steer_probe.py: {G} genomes (disjoint 16-draw batteries) per body")
    print(f"# PW caricature; v0 {V0}, heading noise {NOISE}, eat from root 0.35 m, T threshold {T_MIN_SPEED} m/s")
    print("body          STEERS  SMELL-USE  NONE   mean F   mean dT  mean T_intact  mean T_decoy  food_intact  zero-veto-draws  STEERS-if-no-veto")
    for lab, ctrl, par in BODIES:
        rows = [call(ctrl, par, g) for g in range(G)]
        n = {k: sum(r[0] == k for r in rows) / G for k in ("STEERS", "SMELL-USE", "NONE")}
        m = lambda i: np.mean([r[i] for r in rows])
        print(f"{lab:12s} {n['STEERS']:6.2f}  {n['SMELL-USE']:9.2f}  {n['NONE']:4.2f}  {m(1):+7.3f}  {m(2):+8.3f}  {m(6):+13.3f}  {m(7):+12.3f}  {m(5):11.2f}  {m(4):6.1f}  {sum(r[8] == 'STEERS' for r in rows) / G:6.2f}", flush=True)
