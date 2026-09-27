"""RBT-121 audit C: does the foraging world pay perception more than coverage?

A kinematic forager model (numpy only; no bodies, no physics).  Each agent is a point that moves at
constant speed ``v`` with a bounded turn rate and eats any item within ``R = eat_radius + halfspan`` of
it: ``halfspan`` stands in for "any geom centre" in ``Simulation._eat`` (simulation.py:466).  The food
reproduces ``Simulation``'s rules: items uniform in the 3 m disc or uniform within ``patches`` clusters
whose centres are uniform in the disc (simulation.py:388-464), the 0.8 m clearance from the robot on
every placement, instant regrowth at a fresh random spot (regrow_delay 0), regrowth at its own spot after
``regrow_delay`` s, or no regrowth.  Spawns follow ``spawn_layout`` under random_start: 1.5-2.5 m out,
heading within +-135 deg of the centre.  Smell is ``Simulation._intensity`` exactly (sum / mean / log of
exp(-d/decay), squashed), read at two nose points 0.15 m either side of the heading and 0.10 m ahead.

Controllers, all at the same speed and turn limit:
  blind-straight   holds its spawn heading (the cheapest "mower"; leaves the disc if it runs long)
  blind-arc        a constant gentle turn (radius 1.5 m), the circling lump
  blind-best       per world, the better of the two blind means (reported, not a controller)
  smell-k          omega = omega_max * tanh(k * (I_left - I_right)): a two-nose klinotaxis with link
                   gain k.  k = 6 is the top of the weights evolution has reached (paper 5: 4.65-6.11);
                   k = 32 is where paper 5's hand motif paid; k = inf is the sign of the difference.
  smell-k+home     the same, plus a blind pull back toward the centre when outside 2.8 m (so the
                   comparison is not won by the blind agent leaving the disc)

Output: mean items per 15 s solo bout and the sighted/blind ratio, per world.  Solo, one robot:
the group questions are argued in AUDIT.md.  Run from the repo root:  python3 runs/RBT-121/ecology/probe_world.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, replace

import numpy as np


@dataclass
class World:
    name: str
    items: int = 12
    radius: float = 3.0
    eat_radius: float = 0.35
    decay: float = 1.0
    smell: str = "sum"
    clearance: float = 0.8
    patches: int = 0
    patch_radius: float = 0.6
    regrow: str = "instant"  # "instant" | "delay" | "none"
    regrow_delay: float = 0.0
    duration: float = 15.0


DT = 0.05
HALFSPAN = 0.15   # geom centres reach this far from the COM (a small lump)
OMEGA = 2.0       # rad/s turn limit
GAIN = 1.0        # food-sensor gain: the nose reads GAIN x the world's intensity difference (a proposed FoodConfig knob)
CENTRE = None     # None: the legacy model (GAIN x squashed difference).  "running" or "root": the proposal's sensor,
                  # each nose reads tanh(G_PROP * (ln S_nose - b)), with b a per-robot running mean of ln S over the
                  # two noses (time constant TAU) or ln S at the robot's centre (root-centring; adversary #403 6b)
G_PROP = 2.5
TAU = 2.0         # s
NOISE = 0.0       # heading diffusion, rad / sqrt(s): a body that cannot hold a line
NOSE_LAT, NOSE_FWD = 0.15, 0.10


def draw_spot(rng, w: World, centres, avoid):
    for _ in range(256):
        if len(centres):
            c = centres[rng.integers(0, len(centres))]
            r = w.patch_radius * np.sqrt(rng.random()); a = rng.uniform(0, 2 * np.pi)
            p = c + np.array([r * np.cos(a), r * np.sin(a)])
            if np.linalg.norm(p) > w.radius:
                continue
        else:
            r = w.radius * np.sqrt(rng.random()); a = rng.uniform(0, 2 * np.pi)
            p = np.array([r * np.cos(a), r * np.sin(a)])
        if avoid is None or np.linalg.norm(avoid - p) >= w.clearance:
            return p
    return p


def intensity(w: World, pt, food):
    n = len(food)
    d = np.linalg.norm(food - pt, axis=1)
    total = float(np.exp(-d / w.decay).sum())
    if w.smell == "mean":
        i = total / n
        return i / (1 + i)
    if w.smell == "log":
        return float(np.clip(np.log1p(total) / np.log1p(n), 0, 1))
    return total / (1 + total)


def log_total(w: World, pt, food):
    """ln of the summed exp(-d/decay) terms (the quantity the proposal's centred contrast is built on)."""
    d = np.linalg.norm(food - pt, axis=1)
    return float(np.log(np.exp(-d / w.decay).sum() + 1e-12))


def bout(w: World, v: float, ctrl: str, k: float, seed: int) -> int:
    rng = np.random.default_rng(seed)
    bearing = rng.uniform(0, 2 * np.pi); dist = rng.uniform(1.5, 2.5)
    pos = dist * np.array([np.cos(bearing), np.sin(bearing)])
    head = np.arctan2(-pos[1], -pos[0]) + rng.uniform(-0.75 * np.pi, 0.75 * np.pi)
    frng = np.random.default_rng(seed + 7919)
    centres = np.zeros((0, 2))
    if w.patches:
        r = w.radius * np.sqrt(frng.random(w.patches)); a = frng.uniform(0, 2 * np.pi, w.patches)
        centres = np.c_[r * np.cos(a), r * np.sin(a)]
    spots = np.array([draw_spot(frng, w, centres, pos) for _ in range(w.items)])
    food = spots.copy()
    timer = np.zeros(w.items)
    alive = np.ones(w.items, bool)
    PARK = 1e6
    eaten = 0
    R = w.eat_radius + HALFSPAN
    base_run = None
    for t in range(int(round(w.duration / DT))):
        # steer
        if ctrl == "straight":
            om = 0.0
        elif ctrl == "arc":
            om = min(v / 1.5, OMEGA)
        else:
            c, s = np.cos(head), np.sin(head)
            fwd, lat = np.array([c, s]), np.array([-s, c])
            if CENTRE is None:
                il = intensity(w, pos + NOSE_FWD * fwd + NOSE_LAT * lat, food)
                ir = intensity(w, pos + NOSE_FWD * fwd - NOSE_LAT * lat, food)
                diff = GAIN * (il - ir)
            else:
                xl = log_total(w, pos + NOSE_FWD * fwd + NOSE_LAT * lat, food)
                xr = log_total(w, pos + NOSE_FWD * fwd - NOSE_LAT * lat, food)
                if CENTRE == "root":
                    base = log_total(w, pos, food)
                else:
                    base = 0.5 * (xl + xr) if base_run is None else base_run + (DT / TAU) * (0.5 * (xl + xr) - base_run)
                    base_run = base
                diff = np.tanh(G_PROP * (xl - base)) - np.tanh(G_PROP * (xr - base))
            om = OMEGA * (np.sign(diff) if np.isinf(k) else np.tanh(k * diff))
            if ctrl == "smell+home" and np.linalg.norm(pos) > w.radius - 0.2:
                want = np.arctan2(-pos[1], -pos[0])
                om = OMEGA * np.sign(np.sin(want - head))
        head += np.clip(om, -OMEGA, OMEGA) * DT + (NOISE * np.sqrt(DT) * rng.standard_normal() if NOISE else 0.0)
        pos = pos + v * DT * np.array([np.cos(head), np.sin(head)])
        # regrow on own spot
        if w.regrow == "delay":
            due = ~alive
            timer[due] -= DT
            back = due & (timer <= 0)
            alive[back] = True; food[back] = spots[back]
        # eat
        d = np.linalg.norm(food - pos, axis=1)
        for j in np.nonzero(d < R)[0]:
            eaten += 1
            if w.regrow == "instant":
                food[j] = spots[j] = draw_spot(frng, w, centres, pos)
            elif w.regrow == "delay":
                alive[j] = False; timer[j] = w.regrow_delay; food[j] = (PARK, PARK)
            else:
                alive[j] = False; food[j] = (PARK, PARK)
    return eaten


CTRLS = [("blind-straight", "straight", 0), ("blind-arc", "arc", 0),
         ("smell-k6", "smell", 6.0), ("smell-k32", "smell", 32.0), ("smell-kinf", "smell", np.inf),
         ("smell-kinf+home", "smell+home", np.inf)]


def evaluate(w: World, v: float, n: int, ctrls=CTRLS):
    out = {}
    for label, ctrl, k in ctrls:
        xs = np.array([bout(w, v, ctrl, k, 1000 + s) for s in range(n)], float)
        out[label] = (xs.mean(), xs.std(ddof=1) / np.sqrt(n))
    return out


def report(w: World, v: float, n: int):
    res = evaluate(w, v, n)
    blind = max(res["blind-straight"][0], res["blind-arc"][0])
    best_smell = max(res[l][0] for l, *_ in CTRLS if l.startswith("smell"))
    cells = "  ".join(f"{l} {m:5.2f}±{se:4.2f}" for l, (m, se) in res.items())
    print(f"{w.name:34s} v={v:.2f}  {cells}  | blind-best {blind:5.2f}  smell-k6/blind {res['smell-k6'][0] / max(blind, 1e-9):5.2f}  best-smell/blind {best_smell / max(blind, 1e-9):5.2f}", flush=True)
    return res


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    base = World("default uniform (12, sum)")
    worlds = [
        base,
        replace(base, name="default uniform, smell=log", smell="log"),
        replace(base, name="RBT-106 HP (12 in 3 patches, sum)", patches=3),
        replace(base, name="RBT-19 persistent (26/3p, delay 45)", items=26, patches=3, regrow="delay", regrow_delay=45.0),
    ]
    print(f"# n = {n} bouts per cell; items per 15 s solo bout; halfspan {HALFSPAN} m, turn limit {OMEGA} rad/s")
    print("## A. Committed worlds, speed sweep")
    for w in worlds:
        for v in (0.1, 0.25, 0.5):
            report(w, v, n)
