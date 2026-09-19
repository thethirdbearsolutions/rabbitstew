"""RBT-66 adversary: does the axis verdict survive the frozen probe's two free parameters?

The RBT-66 verdicts rest on ONE column of `runs/RBT-66/axis_lesion.py`: `dk`, the tick of
maximum |steer|+|throttle| within a horizon of 8. The tick-2 column adjudicates nothing --
it is exactly 0.000 on three of the four champions, and on the fourth it is an exact tie by
construction (one wired nose gives |steer| = |throttle|; RBT-78's calibration). So the whole
taxonomy now rests on routing through the recurrent core over ticks 2-8, summarised by an
argmax, with the horizon chosen in advance and never varied.

That is the same shape of free parameter the RBT-66 pre-registration objected to in path
sums ("a property of where the counting stopped"). The probe is finite so nothing diverges,
but "finite" is not "insensitive". This measures the sensitivity directly.

One bout, one long frozen trajectory per probe point, every summary derived from it:

  tick-h          the signed delta at exactly tick h
  peak-joint-h    argmax over ticks 2..h of |steer|+|throttle|, both axes read there
                  -- THE COMMITTED RULE, at h = 8
  peak-sep-h      each axis at its own argmax over 2..h
  mean-h          mean over ticks 2..h

and for each, the axis winner, its sign, and the paired |steer|-|throttle| t across seeds,
which is the clause the verdict rule actually tests.

Usage: horizon.py RUN KIND GEN [N_SEEDS] [MAXH]
"""
import json, sys
from dataclasses import replace

import numpy as np

from rabbitstew.fixed import drive_effector_units, steering_throttle
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

SEED0 = 4000                       # identical to runs/RBT-66/axis_lesion.py
HS = (2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64)


def drive_keys(ph):
    l, r = drive_effector_units(ph)
    key = lambda i: (ph.units[i].part, ph.units[i].unit.dof)
    return key(l[0]), key(r[0])


def nose_units(ph, sources=("food",)):
    return [i for i, ui in enumerate(ph.units)
            if ui.unit.kind == "sensor" and ui.unit.source in sources]


def frozen_traj(b, sens, nose_pos, lk, rk, horizon):
    """Full nose-on minus nose-off (steer, throttle) trajectory, trajectory held fixed.

    Byte-for-byte the state handling of runs/RBT-66/axis_lesion.py::frozen_probe, with the
    horizon opened up and the whole trajectory returned instead of two summaries.
    """
    keep = (b.activation.copy(), b._prev_input.copy())
    out = []
    for kill in (False, True):
        b.activation, b._prev_input = keep[0].copy(), keep[1].copy()
        s = sens.copy()
        if kill:
            s[nose_pos] = 0.0
        traj = []
        for _ in range(horizon):
            b.step(s)
            traj.append(steering_throttle(b.effector_output(*lk), b.effector_output(*rk)))
        out.append(traj)
    b.activation, b._prev_input = keep
    on, off = out
    return np.array([(p[0] - q[0], p[1] - q[1]) for p, q in zip(on, off)])


def bout(g, cfg, ph, seed, maxh, probe_every=10):
    """Per-seed mean over probe points of every summary, for every horizon in HS."""
    c = replace(cfg, random_start=True)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    b = sim.brains[0]
    lk, rk = drive_keys(ph)
    nose_set = set(nose_units(ph))
    nose_pos = [j for j, u in enumerate(b.sensor_idx) if u in nose_set]
    acc = {}
    n = 0
    for tick in range(int(round(c.duration / c.control_dt))):
        sim.step()
        if not nose_pos or tick % probe_every:
            continue
        tr = frozen_traj(b, sim.sensor_values(0, sim.contact_bodies()), nose_pos, lk, rk, maxh)
        n += 1
        for h in HS:
            w = tr[1:h]                      # ticks 2..h; tick 1 is structurally zero
            if not len(w):
                continue
            j = int(np.argmax(np.abs(w[:, 0]) + np.abs(w[:, 1])))
            for tag, val in (
                ("tick", tuple(tr[h - 1])),
                ("joint", tuple(w[j])),
                ("sep", (w[int(np.argmax(np.abs(w[:, 0]))), 0],
                         w[int(np.argmax(np.abs(w[:, 1]))), 1])),
                ("mean", (float(w[:, 0].mean()), float(w[:, 1].mean()))),
            ):
                k = (tag, h)
                a = acc.setdefault(k, [0.0, 0.0])
                a[0] += float(val[0]); a[1] += float(val[1])
    return {k: (v[0] / n, v[1] / n) for k, v in acc.items()} if n else {}


def tstat(xs):
    xs = np.asarray(xs, float)
    sd = xs.std(ddof=1)
    return float(xs.mean() / (sd / np.sqrt(len(xs)))) if sd > 0 else float("inf" if xs.mean() else 0.0)


if __name__ == "__main__":
    run, kind, gen = sys.argv[1], sys.argv[2], int(sys.argv[3])
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 64
    maxh = int(sys.argv[5]) if len(sys.argv) > 5 else max(HS)
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
    ph = synthesize(g, cfg.synthesis)
    rows = [bout(g, cfg, ph, SEED0 + s, maxh) for s in range(n)]
    rows = [r for r in rows if r]
    print(f"# RBT-66 adversary: horizon sensitivity — {run} {kind} gen {gen}")
    print(f"n={len(rows)} paired seeds from {SEED0}; frozen probe, horizons {HS}")
    print(f"control_dt {cfg.control_dt:g}s, so h=8 holds the other sensors {8*cfg.control_dt:g}s "
          f"and h={maxh} holds them {maxh*cfg.control_dt:g}s\n")
    for tag, name in (("joint", "peak-joint (THE COMMITTED RULE at h=8)"),
                      ("sep", "peak per axis, each at its own argmax"),
                      ("mean", "mean over ticks 2..h"),
                      ("tick", "the single tick h")):
        print(f"### {name}\n")
        print("| h | steer | throttle | winner | |steer|-|throttle| paired | t |")
        print("|---|---|---|---|---|---|")
        for h in HS:
            k = (tag, h)
            if k not in rows[0]:
                continue
            s = np.array([r[k][0] for r in rows]); t = np.array([r[k][1] for r in rows])
            d = np.abs(s) - np.abs(t)
            win = "steer" if abs(s.mean()) > abs(t.mean()) else "throttle"
            sign = "+" if (s if win == "steer" else t).mean() > 0 else "-"
            print(f"| {h} | {s.mean():+.5f} | {t.mean():+.5f} | **{win} {sign}** | "
                  f"{d.mean():+.5f} | {tstat(d):+7.2f} |")
        print()
