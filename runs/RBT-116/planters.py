"""RBT-132: the planted set, in the tree (RBT-116 §4.3 G8(a)–(e); RBT-129 DESIGN §5.3(c), §5.5 K3/K4), and the planted
command per point.

    planters.py planted POINT CONFIG OUT --hosts HOSTS_ROOT [--workers W]

The planters build genomes and nothing else; ``steer.py`` calls them.  The command, per registered point:
1. **hosts**: 8 designed and 8 holistic hosts from RBT-113's committed O1 U-line finals (``ckpt/rbt-113-O1``, restored
   into HOSTS_ROOT; seeds 1-3, 40 finals each per fauna), walked in a fixed permutation (``default_rng([129, 132, fauna])``, fauna 0 designed, 1 holistic)
   and taken in that order when they can carry their plant (the refusals are printed).  STEER_NOTES R3 says why these.
2. **tuning** on the point's first 4 pool draws (the "screening draws"; W1's stage-1 size), intact against decoy F:
   G8(b) over its 8 variants, G8(c) over its 2 signs; G8(a) is signed by RBT-103's two direction probes, which must
   agree (else the host is UNDETERMINED and replaced), as RBT-125 §B signs it.  The same probes give each designed
   host's travel direction, which fixes G8(b)'s brake to the slowing sign.
3. **the reachability screen** (``steer.screen_draws``) with the G8(a) and G8(c) plants as the positive-control hosts,
   on the point's own pool, at the point's own τ; the battery and the per-draw table are written to OUT.
4. **the calls**: every plant through ``steer.call_genome`` on that battery: (a) and (c) at a = 6 (8 hosts each), (b)
   (8 designed hosts), (d) the three sensorless tumblers, (e) the same with two unwired food sensors, and the
   motors-off body (the 8 G8(a) plants with every Effector silenced).  K3 and K4 are read from them (``k3_k4``, as the
   coordinator ruled at 07:10: a plant is SEEN when stage 2's veto and ΔT bound hold and the confirmation battery
   repeats both; F plays no part, so the (a) and (c) plants' confirmation is run whenever stage 2 shows c2 and c3).

Plants (all at the fixed registered rung a = 6 where a rung applies; RBT-129 §5.3(c), M7a):
- **(a)** RBT-97's routed compass (``routed.install``, w = 3, a = 2w) on a designed host, signed per host.
- **(b)** the paying kinesis plant (MUST 3, R5-3; non-root nose, M5): the left drive wheel's food sensor → a unit on its
  **magnitude** (``abs``, input gain k) → a thresholded unit (``relu``, bias −q) → a turn (both drive Effectors, the
  steering axis, sign s_T) and a brake (the difference axis, sign s_B, half weight): area-restricted search with no
  heading term.  The brake is fixed to the slowing sign (against the host's measured travel direction; RBT-116 G8(b)
  "throttle (slow)"; the 07:10 ruling, S6).  Grid q ∈ {0.2, 0.5} × k ∈ {2.5, 10} × s_T: 8 variants, best by F.
- **(c)** the holistic tuned two-nose plant: two food sensors on the two expressed Parts of distinct single-instance
  Nodes most separated across the host's measured CoM heading (one intact season on the first screening draw), a
  global tanh unit fed + and −, linked ± to the Effectors either side (each Effector Node's instances all on one side),
  at a **total** gain a = 6 split evenly over the n output links (w = 6 / n; the 07:10 ruling, S5; n is printed), 2
  signs, best by F.  The single-instance restriction narrows RBT-116's G8(c) (ruled, S4); the carrying share of the
  holistic pool is printed per point.
- **(d)** the sensorless full-throttle tumblers (RBT-121 auditor A's S2 rod: a 5 m arm, bias 3): ``rod`` (vertical
  hinge), ``hinge`` (horizontal hinge) and ``ball`` (ball joint, three Effectors).
- **(e)** the same three with two unwired food sensors (root and arm).
- **motors-off**: the (a) plants with every Effector's bias and inputs removed; they never actuate.

Nothing here runs on import.  The tests use fixture worlds and committed RBT-19 bodies only.
"""
from __future__ import annotations

import argparse
import copy
import functools
import importlib.util
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from typing import Optional

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


steer = _load("rbt116_steer", os.path.join(HERE, "steer.py"))
routed = _load("rbt97_routed", os.path.join(ROOT, "runs", "RBT-97", "routed_p801.py"))
g500 = _load("rbt97_g500", os.path.join(ROOT, "runs", "RBT-97", "g500_direction.py"))

from rabbitstew.fair import is_designed  # noqa: E402
from rabbitstew.genotype import (Brain, Connection, Effector, Genotype, JointType, Link, Neuron, Node, Segment,  # noqa: E402
                                 Sensor, Shape, UnitRef)
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

HOSTS_KEY = (129, 132)  #: the host permutation's registered key
N_HOSTS = 8  #: RBT-129 §5.3(c): 8 hosts per plant
HOST_SEEDS = (1, 2, 3)  #: RBT-113 O1's seed directories (as RBT-125 §B's steps.py draws its designed hosts)
W_RUNG = 3.0  #: a = 2w = 6, the fixed registered rung (RBT-129 M7a)
A_RUNG = 2 * W_RUNG  #: G8(c)'s rung as a total gain, split evenly over its output links (the 07:10 ruling, S5)
N_TUNE = 4  #: the screening draws: the point's first 4 pool draws
B_GRID = [(q, k, sT) for q in (0.2, 0.5) for k in (2.5, 10.0) for sT in (1.0, -1.0)]  #: s_B is fixed per host (slowing)
LEFT, RIGHT = routed.WHEELS


# --------------------------------------------------------------------------- #
# Hosts
# --------------------------------------------------------------------------- #


def host_pool(root: str, kind: str) -> list:
    """Every RBT-113 O1 U-line final of ``kind``, in the registered permutation."""
    files = []
    for seed in HOST_SEEDS:
        d = os.path.join(root, "O1", str(seed), "U", kind, "final")
        files += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".json")]
    order = np.random.default_rng(list(HOSTS_KEY) + [0 if kind == "conventional" else 1]).permutation(len(files))
    return [files[i] for i in order]


# --------------------------------------------------------------------------- #
# (a) the routed compass, signed per host
# --------------------------------------------------------------------------- #


def _direction(g: Genotype, cfg: SimConfig, probe: str, n: int = 16) -> Optional[bool]:
    """RBT-103's direction probe (``routed_populations.direction_bout``) on one host: is its travel backward?"""
    P = g500.PROBES[probe]
    sn = cs = 0.0
    k = 0
    for i in range(n):
        seed = P["seed0"] + i
        sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
        sim.set_food_seed(seed)
        pos_of = (lambda s_: s_.center_of_mass(0)[:2]) if P["com"] else (lambda s_: s_.data.xpos[s_.robots[0].root_body][:2])
        last = np.array(pos_of(sim), dtype=float).copy()
        for t in range(int(round(cfg.duration / cfg.control_dt))):
            sim.step()
            if P["stop_on_explode"] and sim.exploded[0]:
                break
            if t % P["every"]:
                continue
            pos = np.array(pos_of(sim), dtype=float)
            d = pos - last
            if np.linalg.norm(d) > 1e-3:
                o = g500.td.wrap(float(np.arctan2(d[1], d[0])) - g500.td.yaw_of(sim))
                sn += np.sin(o)
                cs += np.cos(o)
                k += 1
            last = pos.copy()
    return None if not k else bool(abs(np.degrees(np.arctan2(sn / k, cs / k))) > 90)


def travel_backward(g: Genotype, cfg: SimConfig) -> Optional[bool]:
    """Whether the host travels chassis-backward, by RBT-103's two probes (both must agree), or None."""
    backs = [_direction(g, cfg, probe) for probe in g500.PROBES]
    if backs[0] is None or backs[0] != backs[1]:
        return None
    return backs[0]


def compass_sign(g: Genotype, cfg: SimConfig, backs: Optional[list] = None) -> Optional[float]:
    """+1 / −1 as RBT-125 §B signs a host (both probes must agree), or None (UNDETERMINED)."""
    backs = [_direction(g, cfg, probe) for probe in g500.PROBES] if backs is None else backs
    if backs[0] is None or backs[0] != backs[1]:
        return None
    return +1.0 if backs[0] == routed.mech.rs.PUBLISHED_IS_BACKWARD else -1.0


def slowing_sign(backward: bool) -> float:
    """G8(b)'s brake sign: against the travel direction on the Pioneer's throttle axis (left − right is forward).

    The forward branch is checked physically (the fix-check's ``rbt132_brake_probe.txt``: on 5 of 5 O1 hosts it slows
    the host against the opposite sign).  The backward branch has no physical test: every O1 host probed travels
    forward, and RBT-19's P-801 speeds up under either sign, so it is pinned by the constant alone (N2); harmless for
    O1's hosts, and a backward host is logged as such in ``planted``."""
    return +1.0 if backward else -1.0


def plant_a(g: Genotype, sign: float, w: float = W_RUNG) -> Genotype:
    """G8(a): RBT-97's routed compass at a = 2w."""
    out = routed.install(g, w, sign=sign)
    out.name = f"{g.name}+a{2 * w:g}{'+' if sign > 0 else '-'}"
    return out


def motors_off(g: Genotype) -> Genotype:
    """The motors-off body: every Effector's bias 0 and every link into an Effector removed; it never actuates."""
    out = copy.deepcopy(g)
    for nd, node in enumerate(out.nodes):
        effs = {i for i, u in enumerate(node.segment.brain.units) if u.kind == "effector"}
        for i in effs:
            node.segment.brain.units[i].bias = 0.0
        node.segment.brain.links = [l for l in node.segment.brain.links if not (l.dst.index in effs and l.dst.node in (None, nd))]
    problems = out.validate()
    if problems:
        raise RuntimeError("motors-off body is invalid: " + "; ".join(problems))
    out.name = f"{g.name}+motors-off"
    return out


# --------------------------------------------------------------------------- #
# (b) the paying kinesis plant (sign-blind)
# --------------------------------------------------------------------------- #


def plant_b(g: Genotype, q: float, k: float, sT: float, sB: float) -> Genotype:
    """G8(b): |reading| of the left wheel's nose → threshold q → turn sT (steering axis) and brake sB (difference axis)."""
    nose, eff = routed.unit_indices(g)
    out = copy.deepcopy(g)
    gb = out.global_brain if out.global_brain is not None else Brain()
    out.global_brain = gb
    gb.units.append(Neuron(bias=0.0, func="abs"))
    mag = len(gb.units) - 1
    gb.units.append(Neuron(bias=-q, func="relu"))
    arsu = len(gb.units) - 1
    gb.links.append(Link(UnitRef(LEFT, nose), UnitRef(None, mag), k))
    gb.links.append(Link(UnitRef(None, mag), UnitRef(None, arsu), 1.0))
    for nd, side in ((LEFT, +1.0), (RIGHT, -1.0)):  # left = steering + throttle, right = steering − throttle (fixed.py)
        out.nodes[nd].segment.brain.links.append(Link(UnitRef(None, arsu), UnitRef(nd, eff), sT * 1.0 + side * sB * 0.5))
    problems = out.validate()
    if problems:
        raise RuntimeError("G8(b) is invalid: " + "; ".join(problems))
    out.name = f"{g.name}+b(q{q:g},k{k:g},{sT:+g},{sB:+g})"
    return out


# --------------------------------------------------------------------------- #
# (c) the holistic tuned two-nose plant
# --------------------------------------------------------------------------- #


def body_geometry(g: Genotype, cfg: SimConfig, draw) -> Optional[dict]:
    """One intact season on ``draw``: the CoM heading (unit, start → end), and each Part's lateral coordinate across it
    at the settled start (+ is left of the heading).  None if the body moves less than 5 cm."""
    cfg = replace(steer.draw_sim(cfg, draw), opponent_proxy=True)
    sim = Simulation([g], cfg, spawns=[spawn_layout(2, cfg, draw.start_seed)[0]])
    sim.set_food_seed(draw.start_seed)
    idx = sim.robots[0]
    com0 = np.array(sim.center_of_mass(0)[:2])
    pos0 = np.array([sim.data.geom_xpos[gid][:2] for gid in idx.geoms])
    sim.run()
    d = np.array(sim.center_of_mass(0)[:2]) - com0
    if np.linalg.norm(d) < 0.05:
        return None
    h = d / np.linalg.norm(d)
    rel = pos0 - com0
    lat = h[0] * rel[:, 1] - h[1] * rel[:, 0]
    return {"heading": h, "lat": lat, "phenotype": sim.phenotypes[0]}


def c_layout(g: Genotype, geom: dict) -> Optional[dict]:
    """Where G8(c) goes on this body: the two noses (Node, and its one Part) most separated across the heading, on
    distinct single-instance Nodes, one each side; and every Effector Node whose instances all lie on one side."""
    ph = geom["phenotype"]
    lat = geom["lat"]
    single = [(nd, parts[0]) for nd, parts in ph.node_instances.items() if len(parts) == 1]
    if len(single) < 2:
        return None
    left = max(single, key=lambda x: lat[x[1]])
    right = min(single, key=lambda x: lat[x[1]])
    if left[0] == right[0] or not (lat[left[1]] > 0 > lat[right[1]]):
        return None
    sides = {}
    for nd, parts in ph.node_instances.items():
        if not any(u.kind == "effector" for u in g.nodes[nd].segment.brain.units):
            continue
        s = np.sign(lat[parts])
        if np.all(s > 0) or np.all(s < 0):
            sides[nd] = float(s[0])
    if not any(v > 0 for v in sides.values()) or not any(v < 0 for v in sides.values()):
        return None
    return {"left": left[0], "right": right[0], "sides": sides}


def c_links(g: Genotype, layout: dict) -> list:
    """G8(c)'s output links: (Node, Effector unit, side) for every Effector unit of a one-sided Effector Node."""
    return [(nd, i, side) for nd, side in layout["sides"].items() for i, u in enumerate(g.nodes[nd].segment.brain.units) if u.kind == "effector"]


def plant_c(g: Genotype, layout: dict, sign: float, a: float = A_RUNG) -> Genotype:
    """G8(c): a food sensor on each chosen Node; a global tanh unit fed +left −right; ± to the Effectors either side, at a
    total gain ``a`` split evenly over the n output links (w = a / n)."""
    links = c_links(g, layout)
    w = a / len(links)
    out = copy.deepcopy(g)
    gb = out.global_brain if out.global_brain is not None else Brain()
    out.global_brain = gb
    gb.units.append(Neuron(bias=0.0, func="tanh"))
    k = len(gb.units) - 1
    for nd, s in ((layout["left"], +1.0), (layout["right"], -1.0)):
        units = out.nodes[nd].segment.brain.units
        units.append(Sensor("food"))
        gb.links.append(Link(UnitRef(nd, len(units) - 1), UnitRef(None, k), s))
    for nd, i, side in links:
        out.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, i), sign * side * w))
    problems = out.validate()
    if problems:
        raise RuntimeError("G8(c) is invalid: " + "; ".join(problems))
    out.name = f"{g.name}+c{a:g}/{len(links)}{'+' if sign > 0 else '-'}"
    return out


# --------------------------------------------------------------------------- #
# (d), (e): the sensorless tumblers, and with two unwired noses
# --------------------------------------------------------------------------- #


def tumbler(joint: str, noses: bool = False) -> Genotype:
    """RBT-121 auditor A's S2 rod sweeper (a 5 m arm, full throttle) on a ``rod`` (vertical hinge), ``hinge``
    (horizontal hinge) or ``ball`` joint; ``noses`` adds two unwired food sensors (root and arm)."""
    effs = [Effector(dof=d, bias=3.0) for d in range(3 if joint == "ball" else 1)]
    arm = Segment(Shape.BOX, (5.0, 0.05, 0.05), Brain(units=effs + ([Sensor("food")] if noses else [])))
    jt = JointType.BALL if joint == "ball" else JointType.HINGE
    axis = (0.0, 0.0, 1.0) if joint == "rod" else (0.0, 1.0, 0.0)
    conn = Connection(child=1, position=(1.0, 0.0, 0.0), scale=1.0, joint_type=jt, axis=axis, joint_limit=None)
    root = Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=[Sensor("food")] if noses else []))
    g = Genotype(nodes=[Node(root, [conn]), Node(arm)], name=f"tumbler-{joint}{'+noses' if noses else ''}")
    problems = g.validate()
    if problems:
        raise RuntimeError("tumbler is invalid: " + "; ".join(problems))
    return g


# --------------------------------------------------------------------------- #
# Tuning, and K3 / K4
# --------------------------------------------------------------------------- #


def tune(variants: list, cfg: SimConfig, draws: list, season) -> tuple:
    """The variant with the largest intact − decoy F on ``draws`` (ties: the first).  Returns ``(genome, F, table)``."""
    table = []
    for g in variants:
        F = float(np.mean([season(g, cfg, d, "intact").food - season(g, cfg, d, "decoy").food for d in draws]))
        table.append((g.name, F))
    best = int(np.argmax([f for _, f in table]))
    return variants[best], table[best][1], table


def seen(rec: dict) -> bool:
    """K3's SEEN (the coordinator's 07:10 ruling, item 1): on stage 2 the veto passes (c3) and the ΔT lower bound is > 0
    (c2), and the confirmation battery repeats c2 and c3.  F plays no part; the call is printed beside it."""
    s2 = rec.get("stage2") or {}
    conf = rec.get("confirm") or rec.get("k3_confirm") or {}
    return bool(s2.get("c3") and s2.get("c2") and conf.get("c3") and conf.get("c2"))


def dT_sd(s2: dict) -> float:
    """A plant's per-draw ΔT SD, recovered exactly from its ``battery_stats`` record (whose bound is dT − t·σ/√n,
    ``steer.lower_bound``): the calibration lane reports it beside each plant's ΔT mean (§12's K3 calibration)."""
    n = s2["n"]
    if n < 2 or not math.isfinite(s2["lbdT"]):
        return float("nan")
    if s2["lbdT"] == s2["dT"]:
        return 0.0
    return (s2["dT"] - s2["lbdT"]) * math.sqrt(n) / steer.t_quantile(0.95, n - 1)


def k3_line(rec: dict) -> str:
    """K3's verdict for an (a) or (c) plant, with its stage-2 ΔT mean and SD (the calibration lane's report)."""
    s2 = rec.get("stage2")
    tail = f"; stage-2 dT {s2['dT']:+.4f} sd {dT_sd(s2):.4f} over {s2['n']}" if s2 else "; stopped at stage 1 (no dT)"
    return f" | K3 {'SEEN' if seen(rec) else 'not seen'}{tail}"


def k3_k4(calls: dict) -> dict:
    """RBT-129 §5.5 as ruled at 07:10.  K3: of the pooled (a) + (c) plants, ≥ 4 are SEEN (:func:`seen`), with ≥ 1 of each
    kind.  K4: no STEERS among (b), (d), (e) and motors-off; (d), (e) and motors-off are instrument checks (they cannot
    fail by construction), and (b) is a test only where it reaches F ≥ F_MIN.  K4's "intact − decoy CI covers 0" clause
    is dropped (ruled, S3): vacuous for (d), (e) and motors-off, and self-defeating for a paying (b)."""
    a = [r for r in calls.get("a", []) if seen(r)]
    c = [r for r in calls.get("c", []) if seen(r)]
    k3 = len(a) + len(c) >= 4 and len(a) >= 1 and len(c) >= 1
    neg = [r for key in ("b", "d", "e", "motors-off") for r in calls.get(key, [])]
    b_paying = [r for r in calls.get("b", []) if (r.get("stage2") or {}).get("F", 0) >= steer.F_MIN]
    return {"K3": bool(k3), "K3_seen": (len(a), len(c)), "K4": not any(r["call"] == steer.STEERS for r in neg),
            "K4_b_testable": len(b_paying), "K4_b_note": "" if b_paying else "T's discrimination is untested here (no G8(b) plant reached F >= F_MIN)"}


# --------------------------------------------------------------------------- #
# The planted command, per point
# --------------------------------------------------------------------------- #


#: RBT-129 §12's K3 calibration cells (stages.py CALIB_CELLS): the only cells where ``--calibration`` may run
CALIBRATION_CELLS = ("c0-p030-PW-G", "c0-p030-HP-G")


def _call(args):
    gd, cfg_d, bat_d, point = args[:4]
    k3 = len(args) > 4 and args[4]
    calibration = len(args) > 5 and args[5]
    cfg, bat = SimConfig.from_dict(cfg_d), steer.Battery.from_dict(bat_d)
    rec = steer.call_genome(gd, cfg, bat, steer.point_season(point))
    s2 = rec.get("stage2") or {}
    # K3's SEEN needs the confirmation's c2 and c3.  At the calibration's second stage (#471's ruling, S2), every (a)
    # and (c) plant gets its confirmation battery, gate or no gate, so the projection has 32 draws per plant; SEEN is
    # unchanged (it still needs stage 2's c2 and c3)
    if k3 and "confirm" not in rec and (calibration or (s2.get("c2") and s2.get("c3"))):
        runs, refused = steer._pairs(gd, cfg, bat.confirm, steer.point_season(point))
        if len(runs["intact"]) >= steer.MIN_USABLE:
            rec["k3_confirm"] = steer.battery_stats(runs)
    return rec


def planted(point: str, config: str, out: str, hosts_root: str, workers: int = 1, calibration: bool = False) -> int:
    path = os.path.join(config, "config.json") if os.path.isdir(config) else config
    raw = json.load(open(path))
    cfg = SimConfig.from_dict(raw.get("sim", raw))
    steer.assert_world_point(cfg, point)
    steer.assert_registered_channel(cfg, point)
    steer.assert_fair_config(raw, point)
    steer.assert_point_world(raw, point)
    if calibration and point not in CALIBRATION_CELLS:
        raise ValueError(f"--calibration runs only at the K3 calibration cells {CALIBRATION_CELLS}, not {point}")
    season = steer.point_season(point)
    pool = steer.draw_pool(point)
    tune_draws = pool[:N_TUNE]
    os.makedirs(out, exist_ok=True)
    log = open(os.path.join(out, "planted.txt"), "w")

    def say(*x):
        print(*x, file=log, flush=True)

    say(f"# RBT-132 planted set at {point}: {path}; tau {cfg.food.smell_tau} (registered {steer.registered_tau(point)}), "
        f"G {cfg.food.smell_contrast}; hosts {hosts_root}; tuning draws {[(d.terrain_seed, d.start_seed) for d in tune_draws]}")
    plants = {"a": [], "b": [], "c": [], "motors-off": []}
    tried = {"a": 0, "c": 0}
    for f in host_pool(hosts_root, "conventional"):
        if len(plants["a"]) == N_HOSTS:
            break
        tried["a"] += 1
        g = Genotype.load(f)
        if not is_designed(g):
            say(f"host {f}: not a designed body, skipped")
            continue
        try:
            routed.unit_indices(g)
        except (AssertionError, StopIteration) as e:
            say(f"host {f}: cannot carry the routed motif ({e}), skipped")
            continue
        backs = [_direction(g, cfg, probe) for probe in g500.PROBES]
        sign = compass_sign(g, cfg, backs)
        if sign is None:
            say(f"host {f}: UNDETERMINED direction, skipped")
            continue
        plants["a"].append(plant_a(g, sign))
        plants["motors-off"].append(motors_off(plants["a"][-1]))
        sB = slowing_sign(backs[0])
        best, F, table = tune([plant_b(g, *v, sB) for v in B_GRID], cfg, tune_draws, season)
        plants["b"].append(best)
        say(f"host {f}: sign {sign:+g}; travels {'backward' if backs[0] else 'forward'}; G8(b) best {best.name} F {F:+.3f}")
    for f in host_pool(hosts_root, "holistic"):
        if len(plants["c"]) == N_HOSTS:
            break
        tried["c"] += 1
        g = Genotype.load(f)
        geom = body_geometry(g, cfg, tune_draws[0])
        lay = c_layout(g, geom) if geom is not None else None
        if lay is None:
            say(f"host {f}: cannot carry G8(c) ({'no heading' if geom is None else 'no two-sided layout'}), skipped")
            continue
        best, F, table = tune([plant_c(g, lay, s) for s in (+1.0, -1.0)], cfg, tune_draws, season)
        plants["c"].append(best)
        say(f"host {f}: G8(c) noses on nodes {lay['left']}/{lay['right']}, {len(c_links(g, lay))} output links "
            f"(w = {A_RUNG / len(c_links(g, lay)):.3g} each), best {best.name} F {F:+.3f}")
    plants["d"] = [tumbler(j) for j in ("rod", "hinge", "ball")]
    plants["e"] = [tumbler(j, noses=True) for j in ("rod", "hinge", "ball")]
    share = {k: f"{len(plants[k])} of {tried[k]}" for k in ("a", "c")}
    say(f"carrying share (hosts that carry their plant, of those tried): (a) {share['a']}; (c) {share['c']} "
        "(holistic PAYS is on holistic hosts with two single-instance noses)")
    short = {k: len(v) for k, v in plants.items() if k in ("a", "c") and len(v) < N_HOSTS}
    if short:
        say(f"REFUSED: too few hosts carry their plant: {short}")
        return 7
    screen = steer.screen_draws(plants["a"] + plants["c"], cfg, point, season)
    with open(os.path.join(out, "reachability.json"), "w") as fh:
        json.dump(screen["table"], fh, indent=1)
    if not screen["passed"]:
        say(f"GATE FAILED at {point}: {screen['admissible']} admissible draws of {len(screen['table'])} (need {steer.battery_size(point)['battery']})")
        return 8
    with open(os.path.join(out, "battery.json"), "w") as fh:
        json.dump(screen["battery"].to_dict(), fh, indent=1)
    steer.assert_battery_size(screen["battery"], point)
    z = steer.battery_size(point)
    say(f"screen: {screen['admissible']} admissible of {len(screen['table'])}{' (extended)' if screen['extended'] else ''}; "
        f"battery {z['stage1']} + {z['stage2']} + {z['confirm']}"
        + ("; CALIBRATION: the confirmation runs on every (a) and (c) plant (#471 S2)" if calibration else ""))
    tasks = [(key, g) for key in ("a", "b", "c", "d", "e", "motors-off") for g in plants[key]]
    args = [(g.to_dict(), cfg.to_dict(), screen["battery"].to_dict(), point, key in ("a", "c"), calibration and key in ("a", "c"))
            for key, g in tasks]
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            recs = list(ex.map(_call, args, chunksize=1))
    else:
        recs = [_call(x) for x in args]
    calls = {}
    for (key, g), rec in zip(tasks, recs):
        calls.setdefault(key, []).append(rec)
        say(f"{key:10s} " + steer.format_call(g.name, rec) + (k3_line(rec) if key in ("a", "c") else ""))
    kk = k3_k4(calls)
    say(f"K3 {'PASS' if kk['K3'] else 'FAIL'} (a, c seen: {kk['K3_seen']}); K4 {'PASS' if kk['K4'] else 'FAIL'}"
        + (f"; {kk['K4_b_note']}" if kk["K4_b_note"] else ""))
    say(power_line(point))
    with open(os.path.join(out, "planted.json"), "w") as fh:
        json.dump({"point": point, "calibration": calibration, "K": kk, "carrying": share, "calls": {k: [steer._strip(r) for r in v] for k, v in calls.items()}}, fh, indent=1)
    return 0


def _stage2_F(args):
    gd, cfg_d, bat_d, point = args
    cfg, bat = SimConfig.from_dict(cfg_d), steer.Battery.from_dict(bat_d)
    runs, refused = steer._pairs(gd, cfg, bat.stage2, steer.point_season(point))
    return (steer.battery_stats(runs)["F"] if len(runs["intact"]) >= steer.MIN_USABLE else None), len(refused)


def pays(point: str, config: str, out: str, hosts_root: str, workers: int = 1) -> int:
    """Holistic PAYS' F leg at one PAYS cell (RBT-129 §5.1, as ruled at 07:10, S7(c)): G8(c) at a = 6 on 8 holistic
    hosts carrying two single-instance noses; each host's stage-2 F (intact − decoy food, mean over the stage-2 draws of
    the cell's screened battery); holistic F = the mean over hosts, with a one-sided 95% t bound over hosts (the host is
    the replication unit).  The screen's positive controls are the (c) plants themselves.  Writes OUT/holistic/."""
    path = os.path.join(config, "config.json") if os.path.isdir(config) else config
    raw = json.load(open(path))
    cfg = SimConfig.from_dict(raw.get("sim", raw))
    steer.assert_world_point(cfg, point)
    steer.assert_registered_channel(cfg, point)
    steer.assert_fair_config(raw, point)
    steer.assert_point_world(raw, point)
    season = steer.point_season(point)
    tune_draws = steer.draw_pool(point)[:N_TUNE]
    out = os.path.join(out, "holistic")
    os.makedirs(out, exist_ok=True)
    log = open(os.path.join(out, "pays.txt"), "w")

    def say(*x):
        print(*x, file=log, flush=True)

    say(f"# RBT-132 holistic PAYS (F leg) at {point}: {path}; tau {cfg.food.smell_tau} (registered {steer.registered_tau(point)})")
    plants, tried, used = [], 0, []
    for f in host_pool(hosts_root, "holistic"):
        if len(plants) == N_HOSTS:
            break
        tried += 1
        g = Genotype.load(f)
        geom = body_geometry(g, cfg, tune_draws[0])
        lay = c_layout(g, geom) if geom is not None else None
        if lay is None:
            continue
        best, F, _ = tune([plant_c(g, lay, sgn) for sgn in (+1.0, -1.0)], cfg, tune_draws, season)
        plants.append(best)
        used.append(f)
        say(f"host {f}: {len(c_links(g, lay))} output links, best {best.name}")
    say(f"carrying share: {len(plants)} of {tried} holistic hosts tried carry two single-instance noses")
    if len(plants) < N_HOSTS:
        say(f"REFUSED: {len(plants)} hosts carry G8(c), {N_HOSTS} needed")
        return 7
    screen = steer.screen_draws(plants, cfg, point, season)
    if not screen["passed"]:
        say(f"GATE FAILED at {point}: {screen['admissible']} admissible draws")
        return 8
    bat = screen["battery"]
    steer.assert_battery_size(bat, point)
    args = [(g.to_dict(), cfg.to_dict(), bat.to_dict(), point) for g in plants]
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            res = list(ex.map(_stage2_F, args, chunksize=1))
    else:
        res = [_stage2_F(x) for x in args]
    Fs = [F for F, _ in res if F is not None]
    for g, (F, ref) in zip(plants, res):
        say(f"{g.name}: stage-2 F {'--' if F is None else f'{F:+.3f}'} (θ refused {ref})")
    mean, lb = (float(np.mean(Fs)), steer.lower_bound(Fs)) if Fs else (float("nan"), float("-inf"))
    say(f"HOLISTIC F {mean:+.3f}, one-sided 95% t lower bound over {len(Fs)} hosts {lb:+.3f}: "
        f"{'PAYS (F leg)' if lb > 0 else 'does not pay (F leg)'}; holistic PAYS is on holistic hosts with two single-instance noses; "
        "the nose-step leg is RBT-132 item 4 (after its fix-check)")
    with open(os.path.join(out, "pays.json"), "w") as fh:
        json.dump({"point": point, "hosts": used, "carrying": f"{len(plants)} of {tried}", "F": Fs, "mean": mean, "lb": lb, "battery": bat.to_dict()}, fh, indent=1)
    return 0


def power_line(point: str) -> str:
    """The probe leg's power at this point's τ (RBT-132 item 5), computed by ``probe_power.py`` (no file read at run
    time; S8), printed beside every call."""
    probe_power = _load("rbt132_probe_power", os.path.join(HERE, "probe_power.py"))
    if steer.REGISTERED_POINTS[point]["smell_contrast"] > 0:
        return "# power at this point: " + probe_power.line(steer.registered_tau(point))
    return "# power at this point: " + probe_power.LEGACY


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("planted")
    p.add_argument("point")
    p.add_argument("config", help="the point's config.json, or a directory holding one")
    p.add_argument("out")
    p.add_argument("--hosts", required=True, help="HOSTS_ROOT: ckpt/rbt-113-O1 restored (O1/<seed>/U/<kind>/final)")
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--calibration", action="store_true",
                   help="the K3 calibration's second stage (#471 S2): the confirmation on every (a) and (c) plant; calibration cells only")
    q = sub.add_parser("pays", help="holistic PAYS' F leg at one PAYS cell")
    q.add_argument("point")
    q.add_argument("config")
    q.add_argument("out")
    q.add_argument("--hosts", required=True)
    q.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    if a.cmd == "planted":
        return planted(a.point, a.config, a.out, a.hosts, a.workers, a.calibration)
    return pays(a.point, a.config, a.out, a.hosts, a.workers)


if __name__ == "__main__":
    sys.exit(main())
