"""Positive control for the compass manipulation check. RBT-76 mechanism 1.

The manipulation check (scripts/compass_manipulation_check.py) reports a
below-chance `frac_toward` on the *evolved* robots in every condition including
the untouched baseline. A measure whose baseline you cannot explain cannot carry
a conclusion, so before reading anything off it, point it at a robot whose
behaviour is known by construction.

That robot is a Pioneer with its evolved controller BLANKED to zero, carrying
nothing but a constant forward throttle (bias +p on one drive effector, -p on the
other - RBT-64's difference axis) and one of the two antisymmetric nose->wheel
motifs. It has no gait, no oscillator and no evolved wiring. Whatever steering it
does, the motif did.

Expected if the measure works: `base` reads ~0 (it drives straight, so there is
no yaw to correlate with anything), and the two motif signs read opposite. If
instead every condition reads negative, the measure is broken and every number
taken with it is void.

Usage: python scripts/compass_positive_control.py [seeds]
"""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN = "docs/artifacts/RBT-23-W4b-801"
GEN = 590
PARKED = 1e5
cfg = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])


def yaw_of(s):
    q = s.data.xquat[s.robots[0].root_body]
    return float(np.arctan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] ** 2 + q[3] ** 2)))


def wrap(a):
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def main(seeds=24, thr=0.6):
    g = Genotype.load(f"{RUN}/conventional/best_gen{GEN:04d}.json")
    ph = synthesize(g, cfg.synthesis)
    nose, eff = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == 'sensor' and u.unit.source == 'food':
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == 'effector':
            eff[u.part] = i

    def run(cond, w):
        tt, ft, ab, eaten = [], [], [], []
        for seed in range(seeds):
            c = replace(cfg, random_start=True)
            sim = Simulation([g], c, spawns=spawn_layout(1, c, 9000 + seed))
            sim.set_food_seed(9000 + seed)
            W = sim.brains[0].W
            W[:, :] = 0.0
            sim.brains[0].bias[:] = 0.0
            sim.brains[0].bias[eff[1]] = +thr
            sim.brains[0].bias[eff[2]] = -thr
            s = {'motif': +1.0, 'antimotif': -1.0}.get(cond, 0.0)
            if s:
                W[eff[1], nose[1]] += s * w
                W[eff[2], nose[1]] += s * w
                W[eff[1], nose[2]] -= s * w
                W[eff[2], nose[2]] -= s * w
            prev = yaw_of(sim)
            dt = c.control_dt
            T, A = [], []
            for _ in range(int(round(c.duration / c.control_dt))):
                sim.step()
                if sim.exploded[0]:
                    break
                pos = sim.data.xpos[sim.robots[0].root_body][:2]
                live = sim.food_pos[np.max(np.abs(sim.food_pos), axis=1) < PARKED]
                cur = yaw_of(sim)
                rate = wrap(cur - prev) / dt
                prev = cur
                if len(live) == 0:
                    continue
                d = live - pos
                j = int(np.argmin(np.linalg.norm(d, axis=1)))
                bb = wrap(float(np.arctan2(d[j, 1], d[j, 0])) - cur)
                T.append(np.sign(bb) * rate)
                A.append(abs(bb))
            if T:
                tt.append(np.mean(T)); ft.append(np.mean(np.asarray(T) > 0)); ab.append(np.mean(A))
            eaten.append(float(sim.food_eaten[0]))
        return np.mean(tt), np.mean(ft), np.mean(ab), np.mean(eaten)

    print(f"Positive control: gen {GEN} body, brain blanked, throttle bias {thr}, {seeds} seeds")
    print(f"nose units {nose}, effector units {eff}\n")
    print("| cond | w | turn_toward rad/s | frac_toward | mean abs bearing | items |")
    print("|---|---|---|---|---|---|")
    for cond, w in [('base', 0.0), ('motif', 8.0), ('motif', 32.0),
                    ('antimotif', 8.0), ('antimotif', 32.0)]:
        t, f, a, e = run(cond, w)
        print(f"| {cond} | {w:g} | {t:+.4f} | {f:.3f} | {a:.3f} | {e:.3f} |")
    print("\n`motif` is the sign published in RBT-64 and runs/sim-audit/verify_independent.py.")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 24)
