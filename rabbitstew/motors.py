"""Motor capacity per body and per line (RBT-120): the lever the mass budget does not cap.

``world.py`` gives every driven DOF a gear of ``motor_strength`` x the larger of the two masses its joint
connects, and a ball joint up to three such motors, so a body can grow motor capacity that its mass does not
bound.  RBT-113's holistic down line did (Sum gear about 10x its founders', a free-spin work ceiling about 2x
the designed body's), and that was RBT-117's whole margin.  Every holistic-against-designed readout should
print this table beside its verdict, with or without ``--motor-budget``.

    python -m rabbitstew.motors [--config CONFIG_JSON] [--motor-budget C] NAME=DIR [NAME=DIR ...]

Each DIR holds genotype ``.json`` files (a run's ``final/`` or a generation's genomes); the simulation config is
read from ``--config`` or from the nearest ``config.json`` above the first DIR.  The numbers are measured on the
compiled MuJoCo model, so they are what the physics sees, budget included.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, replace
from typing import Optional

import mujoco
import numpy as np

from .genotype import Genotype
from .simulation import SimConfig
from .synthesis import synthesize
from .world import Spawn, build_model, dof_gears, motor_scale

TORQUE, POSITION, VELOCITY = "torque", "position", "velocity"


@dataclass
class MotorCapacity:
    """One body's motor capacity, as compiled."""

    sum_gear: float  #: summed gear of every driven DOF, all motor modes (each mode's peak force is its gear)
    sum_gear_torque: float  #: the torque motors' share of it (RBT-113's probe_gear.py counted these)
    mass: float  #: total body mass (kg), after any mass budget
    ratio: float  #: sum_gear / (motor_strength x mass): 1.7605 for the designed Pioneer, the quantity the budget caps
    ratio_torque: float  #: sum_gear_torque / (motor_strength x mass), probe_gear.py's "/ (4 x mass)"
    ball_share: float  #: share of sum_gear_torque on ball-joint DOFs
    ceiling_J: float  #: full-throttle free-spin work ceiling of the torque motors over one bout: sum gear^2 / damping x duration
    ceiling_yield: float  #: ceiling_J in yield units (work_cost per kJ); 0 when the world has no work cost
    unbudgeted_ratio: float  #: the ratio the mass-keyed rule gives before any motor budget
    budget_scale: float  #: the factor the motor budget multiplied every gear by (1.0 within budget or off)
    n_driven: int  #: driven DOFs
    resting_drive: float  #: share of the genome's Effectors whose resting drive |tanh(bias)| > 0.9 (RBT-121 auditor B): motor capacity is gear AND throttle


def _modes(model) -> np.ndarray:
    """0 torque motor, 1 position servo, 2 velocity servo, from the MJCF world.py writes."""
    out = np.zeros(model.nu, int)
    for a in range(model.nu):
        if model.actuator_biastype[a] == mujoco.mjtBias.mjBIAS_AFFINE:
            out[a] = 1 if model.actuator_biasprm[a, 1] != 0 else 2
    return out


def capacity(genotype: Genotype, sim: Optional[SimConfig] = None) -> MotorCapacity:
    """Compile ``genotype`` alone on flat ground and measure its motor capacity."""
    sim = sim or SimConfig()
    world = replace(sim.world, terrain="flat", arena_radius=0.0)  # scenery is irrelevant to the body's motors
    ph = synthesize(genotype, sim.synthesis)
    model, _, _ = build_model([ph], [Spawn()], world)
    modes = _modes(model)
    tot = torq = ball = ceil = 0.0
    for a in range(model.nu):
        j = model.actuator_trnid[a, 0]
        isball = model.jnt_type[j] == mujoco.mjtJoint.mjJNT_BALL
        if modes[a] == 0:
            k = int(np.argmax(np.abs(model.actuator_gear[a, :3])))
            g = abs(float(model.actuator_gear[a, k]))
            dof = model.jnt_dofadr[j] + (k if isball else 0)
            torq += g
            ball += g if isball else 0.0
            ceil += g * g / max(float(model.dof_damping[dof]), 1e-9)
        else:  # a servo's peak force: gainprm[0] (kp x span, or kv x vmax) is the gear world.py keyed it to
            g = abs(float(model.actuator_gainprm[a, 0]))
        tot += g
    mass = float(model.body_mass[1:].sum())
    per_kg = world.motor_strength * mass
    raw = sum(dof_gears(ph, world).values())
    work_cost = sim.food.work_cost if sim.food is not None else 0.0
    ceiling_J = ceil * sim.duration
    return MotorCapacity(
        sum_gear=tot, sum_gear_torque=torq, mass=mass, ratio=tot / per_kg, ratio_torque=torq / per_kg,
        ball_share=ball / torq if torq > 0 else 0.0, ceiling_J=ceiling_J, ceiling_yield=ceiling_J * work_cost / 1000.0,
        unbudgeted_ratio=raw / per_kg, budget_scale=motor_scale(ph, world), n_driven=model.nu,
        resting_drive=resting_drive(genotype),
    )


def resting_drive(genotype: Genotype, threshold: float = 0.9) -> float:
    """Share of the genome's Effector units held near full throttle at rest, |tanh(bias)| > threshold.

    The Effector-bias walk is unbounded (RBT-121 auditor B), so a motor can sit at constant throttle whatever the
    sensors read; RBT-113's designed D line is 99% saturated.  Counted on the genome, as auditor B's
    effector_bias_lines.py counts it (0 when there is no Effector)."""
    b = np.array([u.bias for _, br in genotype.brains() for u in br.units if u.kind == "effector"], float)
    return float(np.mean(np.abs(np.tanh(b)) > threshold)) if len(b) else 0.0


def summarise(caps: list) -> dict:
    """Per-line summary: means, and min/max where they matter."""
    a = lambda f: np.array([getattr(c, f) for c in caps], float)  # noqa: E731
    r = a("ratio")
    torq = a("sum_gear_torque").sum()
    return {
        "n": len(caps), "sum_gear": float(a("sum_gear").mean()), "sum_gear_min": float(a("sum_gear").min()), "sum_gear_max": float(a("sum_gear").max()),
        "mass": float(a("mass").mean()), "ratio": float(r.mean()), "ratio_min": float(r.min()), "ratio_max": float(r.max()),
        "ratio_torque": float(a("ratio_torque").mean()), "ball_share": float(a("sum_gear_torque").dot(a("ball_share")) / torq) if torq > 0 else 0.0,
        "ceiling_yield": float(a("ceiling_yield").mean()), "ceiling_yield_max": float(a("ceiling_yield").max()),
        "unbudgeted_ratio": float(a("unbudgeted_ratio").mean()), "budgeted_share": float((a("budget_scale") < 1.0).mean()),
        "resting_drive": float(a("resting_drive").mean()),
    }


HEADER = (f"{'line':24s} {'n':>4s} {'sum gear':>9s} {'[min, max]':>17s} {'mass':>6s} {'gear/(ms*mass)':>15s} {'[min, max]':>13s} "
          f"{'ball share':>10s} {'ceiling (yield)':>15s} {'max':>6s} {'unbudgeted':>10s} {'resting':>7s} {'over budget':>11s}")


def format_row(name: str, s: dict) -> str:
    return (f"{name:24s} {s['n']:4d} {s['sum_gear']:9.1f} [{s['sum_gear_min']:6.1f}, {s['sum_gear_max']:6.1f}] {s['mass']:6.2f} "
            f"{s['ratio']:15.2f} [{s['ratio_min']:4.2f}, {s['ratio_max']:4.2f}] {s['ball_share']:10.2f} {s['ceiling_yield']:15.2f} "
            f"{s['ceiling_yield_max']:6.2f} {s['unbudgeted_ratio']:10.2f} {s['resting_drive']:7.2f} {s['budgeted_share']:11.2f}")


def report(groups: dict, sim: SimConfig) -> str:
    """The table for ``{line name: [Genotype, ...]}`` under ``sim`` (its world's motor budget included)."""
    budget = sim.world.motor_budget
    lines = [f"# motor capacity (RBT-120); motor budget {'off' if not budget else f'C = {budget:g}'}; "
             f"ms = motor_strength {sim.world.motor_strength:g}; ceiling = torque motors' full-throttle free-spin work over a {sim.duration:g} s bout"
             + (f" at {sim.food.work_cost:g} per kJ" if sim.food is not None else ""),
             "# 'unbudgeted' = gear/(ms*mass) under the mass-keyed rule alone; 'resting' = share of Effectors with |tanh(bias)| > 0.9 "
             "(the throttle half of motor capacity); 'over budget' = share of members the budget scaled",
             HEADER]
    for name, gs in groups.items():
        lines.append(format_row(name, summarise([capacity(g, sim) for g in gs])))
    return "\n".join(lines)


def _find_config(path: str) -> str:
    d = os.path.abspath(path)
    while True:
        c = os.path.join(d, "config.json")
        if os.path.isfile(c):
            return c
        if os.path.dirname(d) == d:
            raise FileNotFoundError(f"no config.json above {path}; pass --config")
        d = os.path.dirname(d)


def load_sim(config_json: str) -> SimConfig:
    """The SimConfig of an experiment's config.json (an evolve or ecology run) or of a bare SimConfig dict."""
    d = json.load(open(config_json))
    return SimConfig.from_dict(d["sim"] if "sim" in d else d)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m rabbitstew.motors", description=__doc__.split("\n\n")[0])
    p.add_argument("groups", nargs="+", metavar="NAME=DIR")
    p.add_argument("--config", default=None, help="config.json to take the simulation config from (default: the nearest above the first DIR)")
    p.add_argument("--motor-budget", type=float, default=None, metavar="C", help="report as if under this budget (default: the config's own)")
    args = p.parse_args(argv)
    pairs = [g.split("=", 1) if "=" in g else (g, g) for g in args.groups]
    sim = load_sim(args.config or _find_config(pairs[0][1]))
    if args.motor_budget is not None:
        sim = replace(sim, world=replace(sim.world, motor_budget=args.motor_budget))
    groups = {name: [Genotype.load(os.path.join(d, f)) for f in sorted(os.listdir(d)) if f.endswith(".json")] for name, d in pairs}
    print(report(groups, sim))
    return 0


if __name__ == "__main__":
    sys.exit(main())
