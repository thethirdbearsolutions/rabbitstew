"""RBT-66: which axis does a nose circuit actually drive? Measured, not computed.

The taxonomy in ``docs/foraging-world.md`` calls three champions a **brake**, a **throttle**
and a **sweep modulator**.  Those are claims about which axis a nose circuit drives, and all
three were made while assuming a textbook differential drive.  This body does not have one:
the two drive hinges are antiparallel, so the effector **sum** steers and the **difference**
throttles (``rabbitstew.fixed``).

Per the pre-registration on RBT-66 (2026-09-14 12:21), the instrument is a **measurement**,
not a path sum, for two reasons stated there: the recurrent core's spectral radius is
1.57-4.92 on every committed Pioneer best, so any depth > 1 linearisation is a property of
where the counting stopped (RBT-81); and RBT-45's calibration found the same installed
circuit delivering nominal gain on five robots of seven, double on one and sign-reversed on
one, so the realised coefficient must be read rather than inferred from topology.

So: run the bout, read the two drive commands the brain actually sends each tick, resolve
them onto (steering, throttle) with ``fixed.steering_throttle``, and compare nose-live
against nose-blanked on the same paired seed -- the same lesion the behavioural results use
(``scripts/brake_or_compass.py``), read on the axes instead of on the food count.

SCORING QUANTITIES, fixed here before any champion is read.  Each axis is reported two ways
per bout: the **signed mean** over ticks, and the **mean absolute** value.  The verdict rule
scores on the **signed mean**, because the rule attaches signs to it ("brake means
`dthrottle < 0`").  The mean-absolute columns are reported beside it and are *not* scored;
they are there because "a straighter, wider sweep" is a claim about the size of the steering
excursion rather than its direction, and a reader should be able to see both.  Stating which
column scores, before looking, is the point.

Usage:
  axis_lesion.py control [N_SEEDS]            # positive control, run first
  axis_lesion.py champion RUN KIND GEN [N]    # one champion
"""
import json
import math
import sys
from dataclasses import replace

import numpy as np

from rabbitstew.fixed import drive_commands, drive_effector_units, steering_throttle
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

SEED0 = 4000


def drive_keys(ph):
    """``(left_key, right_key)`` actuator keys ``(part, dof)`` for the two drive Effectors."""
    left_u, right_u = drive_effector_units(ph)
    if len(left_u) != 1 or len(right_u) != 1:
        raise RuntimeError(f"expected one drive Effector per side, got {len(left_u)}/{len(right_u)}")
    key = lambda i: (ph.units[i].part, ph.units[i].unit.dof)
    return key(left_u[0]), key(right_u[0])


def nose_units(ph, sources=("food",)):
    """Unit indices of the sensors this lesion blanks."""
    return [i for i, ui in enumerate(ph.units)
            if ui.unit.kind == "sensor" and ui.unit.source in sources]


def frozen_probe(b, sens, nose_pos, lk, rk, horizon):
    """Nose-on minus nose-off drive commands with the TRAJECTORY HELD FIXED.

    The free-running lesion lets the robot diverge, so its delta is the whole behavioural
    consequence of the nose -- including the native controller reacting to being somewhere
    else. That is the right quantity for "what does this nose earn" and the WRONG one for
    "which axis does this circuit drive", which is what the taxonomy claims.

    So: save the brain state, step it `horizon` ticks with the nose at its true value and
    again with the nose zeroed, holding every other sensor at its current reading, and read
    the difference on each axis. Tick 1 is the direct nose->Effector path, exact and with no
    linearisation. Later ticks pick up routing through the interneurons -- which matters
    because the sweep modulator is described as acting "through the global neurons" -- and
    the run is finite by construction, so none of RBT-81's divergence applies.
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
    return [(p[0] - q[0], p[1] - q[1]) for p, q in zip(on, off)]


def bout(g, cfg, ph, seed, blank, install=None, probe_every=10, horizon=8):
    """One bout. Returns per-axis summaries of the drive commands actually sent."""
    c = replace(cfg, random_start=True)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    b = sim.brains[0]
    if install is not None:
        install(b, ph)
    if blank:
        for i in nose_units(ph):
            b.W[:, i] = 0.0
    lk, rk = drive_keys(ph)
    nose_set = set(nose_units(ph))
    nose_pos = [j for j, u in enumerate(b.sensor_idx) if u in nose_set]
    steer, thr, d1, dk = [], [], [], []
    for tick in range(int(round(c.duration / c.control_dt))):
        sim.step()
        s, t = steering_throttle(b.effector_output(*lk), b.effector_output(*rk))
        steer.append(s)
        thr.append(t)
        if not blank and nose_pos and tick % probe_every == 0:
            tr = frozen_probe(b, sim.sensor_values(0, sim.contact_bodies()), nose_pos, lk, rk, horizon)
            d1.append(tr[1])
            dk.append(max(tr, key=lambda v: abs(v[0]) + abs(v[1])))
    steer, thr = np.array(steer), np.array(thr)
    out = {"steer": float(steer.mean()), "throttle": float(thr.mean()),
           "abs_steer": float(np.abs(steer).mean()), "abs_throttle": float(np.abs(thr).mean()),
           "food": float(sim.food_eaten[0])}
    for tag, rows in (("d1", d1), ("dk", dk)):
        out[f"{tag}_steer"] = float(np.mean([r[0] for r in rows])) if rows else 0.0
        out[f"{tag}_throttle"] = float(np.mean([r[1] for r in rows])) if rows else 0.0
    return out


def paired(g, cfg, ph, n, install=None):
    """n paired seeds, nose live minus nose blanked, per axis."""
    rows = []
    for s in range(n):
        on = bout(g, cfg, ph, SEED0 + s, False, install)
        off = bout(g, cfg, ph, SEED0 + s, True, install)
        FROZEN = ("d1_steer", "d1_throttle", "dk_steer", "dk_throttle")
        rows.append({k: (on[k] if k in FROZEN else on[k] - off[k]) for k in on} | {"seed": SEED0 + s,
                    "zero": all(abs(on[k] - off[k]) < 1e-12 for k in ("steer", "throttle"))})
    return rows


def tstat(xs):
    xs = np.asarray(xs, float)
    sd = xs.std(ddof=1)
    return float(xs.mean() / (sd / math.sqrt(len(xs)))) if sd > 0 else float("inf" if xs.mean() else 0.0)


def report(label, rows):
    out = {}
    COLS = ("steer", "throttle", "abs_steer", "abs_throttle", "food",
            "d1_steer", "d1_throttle", "dk_steer", "dk_throttle")
    for k in COLS:
        v = [r[k] for r in rows]
        out[k] = (float(np.mean(v)), tstat(v))
    zeros = sum(r["zero"] for r in rows)
    print(f"\n### {label}   (n={len(rows)} paired seeds, {zeros} with both axes bit-identical)")
    print(f"| quantity | mean delta (nose on - off) | t |")
    print(f"|---|---|---|")
    for k in COLS:
        m, t = out[k]
        star = {"steer": "  free-running", "throttle": "  free-running",
                "d1_steer": "  <-- DIRECT (frozen, tick 2)", "d1_throttle": "  <-- DIRECT (frozen, tick 2)",
                "dk_steer": "  frozen, peak over 8", "dk_throttle": "  frozen, peak over 8"}.get(k, "")
        print(f"| {k:12} | {m:+.5f} | {t:+7.2f} |{star}")
    # The rule's second clause: does the winning axis EXCEED the other on a paired
    # comparison? Computed per seed on each instrument separately, because the two
    # instruments disagree and only the one that passes its control may be scored.
    for tag, a, b in (("free-running", "steer", "throttle"),
                      ("frozen tick-2", "d1_steer", "d1_throttle"),
                      ("frozen peak-8", "dk_steer", "dk_throttle")):
        d = [abs(r[a]) - abs(r[b]) for r in rows]
        print(f"| |steer|-|throttle| paired, {tag:13} | {np.mean(d):+.5f} | {tstat(d):+7.2f} |")
    print(f"per-seed steer deltas (free-running): {[round(r['steer'], 5) for r in rows]}")
    print(f"per-seed throttle deltas (free-running): {[round(r['throttle'], 5) for r in rows]}")
    print(f"per-seed steer deltas (frozen peak-8): {[round(r['dk_steer'], 5) for r in rows]}")
    print(f"per-seed throttle deltas (frozen peak-8): {[round(r['dk_throttle'], 5) for r in rows]}")
    return out


def installer(k, steering, throttle):
    """Install a hand-made circuit of known axis and sign from the chassis nose.

    The weights are never typed out: they come from ``fixed.drive_commands``, so the control
    tests the same convention the analysis uses.
    """
    def go(b, ph):
        noses = nose_units(ph)
        chassis = [i for i in noses
                   if ph.units[i].part is not None and ph.parts[ph.units[i].part].parent is None]
        src = (chassis or noses)[0]
        # Zero every native nose pathway first, so the delta is the installed circuit ALONE.
        # Without this the control measures circuit + native nose, and on this body the native
        # nose is the same size as the circuit (steer -0.19, throttle +0.32 at n=2), which would
        # make the control unreadable. The blanked arm zeroes these same columns, so it is this
        # body with no nose wiring at all and the pair differs by exactly the installed circuit.
        for i in noses:
            b.W[:, i] = 0.0
        wl, wr = drive_commands(steering=steering * k, throttle=throttle * k)
        left_u, right_u = drive_effector_units(ph)
        b.W[left_u[0], src] += wl
        b.W[right_u[0], src] += wr
    return go


def load(run, kind, gen):
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
    return g, cfg, synthesize(g, cfg.synthesis)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "control":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 16
        run, kind, gen = "runs/RBT-19/P-801", "conventional", 590
        g, cfg, ph = load(run, kind, gen)
        print(f"# RBT-66 POSITIVE CONTROL -- can the instrument recover an axis it was told to drive?")
        print(f"body: {run} {kind} gen {gen}; n={n} paired seeds from {SEED0}; k=1.0")
        print(f"weights from fixed.drive_commands, never typed out; blanking removes the installed")
        print(f"circuit along with the native nose, so each delta is that circuit's own contribution.")
        for name, s, t in (("pure STEERING +", 1.0, 0.0), ("pure STEERING -", -1.0, 0.0),
                           ("pure THROTTLE +", 0.0, 1.0), ("pure THROTTLE -", 0.0, -1.0)):
            report(f"control: {name} (k=1.0)", paired(g, cfg, ph, n, installer(1.0, s, t)))
        print("\n### native (no circuit installed) -- the same body's own nose, for reference")
        report("control: native nose, no install", paired(g, cfg, ph, n))
    elif mode == "champion":
        run, kind, gen = sys.argv[2], sys.argv[3], int(sys.argv[4])
        n = int(sys.argv[5]) if len(sys.argv) > 5 else 64
        g, cfg, ph = load(run, kind, gen)
        print(f"# RBT-66 champion: {run} {kind} gen {gen}, n={n} paired seeds from {SEED0}")
        report(f"{run} {kind} gen{gen}", paired(g, cfg, ph, n))
