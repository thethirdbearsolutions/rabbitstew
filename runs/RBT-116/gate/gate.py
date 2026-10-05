"""RBT-116: W1's per-world gate, G1-G9 (PREREGISTRATION.md §4.3, with Amendments 1-4), as runnable cells.

    gate.py CELL [--out runs/RBT-116/gate/W1] [--base runs/RBT-116/W1] [--hosts-root runs/RBT-113] [--workers W]
                 [--shard I/N]

The cells, in the order ``lanes.py`` sequences them (each reads what the cells before it wrote under ``--out``):

    config      write W1's intact world block (config.json) and check it against W1_SIM_HASH
    fixture     the registered G8(f) planter check, at run time (A2/A3: "shown to steer on the fixture world before
                any gate cell"): STEERS on Amendment 3's F2 and F3; every later cell refuses without its PASS
    hosts       per unit: 4 designed hosts (signed) and 4 holistic hosts (G8(c) and G8(f) layouts) from B's gen-12
    screen      the reachability screen (§1.1, Amendment 4): 16 registered screen hosts -> battery.json
    g1          G1 (the rung ladder on 16 designed hosts) and G2 (perception against the burn-in's coverage gain)
    g8          G8 (a)-(f) on every unit's hosts (shardable by unit); g8-controls: (d), (e) once
    g4          G4: 200 burn-in-final members per fauna, all four conditions, confirmed (shardable)
    g6-noise    G6: sigma_P by auditor B's noise.py method on every unit's burn-in finals (shardable by unit)
    g6-u        G6: u_f from 40 children of every STEERS G8(a) and G8(c) plant (shardable by parent)
    g5          G5: seconds per generation from the two-generation timing runs (lanes.py runs them)
    g6-pick     G6: (1 + s)(1 - u) per draws option, the plateaus, the cheapest passing option
    pilot-prep  G6 SHOULD 11: unit 1 with 8 planted steerers per fauna at F ~ F_MIN (the populations to run)
    pilot-probe G6 SHOULD 11: the pilot's generation-24 members, confirmed share against 0.25 x SENS
    g7          G7: the Pioneer's four one-step intermediates against the unmodified host (shardable by host)
    g9          G9: the census in W1, HP and RBT-113's world (with root eating), and the income lost to root eating
    readout     every row's pass or fail, power.py re-run at the measured inputs (K, SENS, EPS, plateaus), GATE.txt

**Nothing here runs on import, and nothing runs an arm.**  The burn-in (B) is the arms' first run; the gate needs its
finals (§4.3: "burn-in-final hosts"), so ``lanes.py`` puts the 24 B runs first.  The tests run every builder on
fixture worlds and fixture bodies only.

Readings the registration leaves open are listed in GATE_NOTES.md (H1-H19), each with the coordinator's ruling
(2026-10-05, on the #540 adversary's recommendations).
"""
from __future__ import annotations

import argparse
import copy
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
R116 = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(R116))
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


steer = _load("rbt116_steer", os.path.join(R116, "steer.py"))
planters = _load("rbt116_planters", os.path.join(R116, "planters.py"))
W = _load("rbt116_world", os.path.join(R116, "world.py"))
power = _load("rbt116_power", os.path.join(R116, "power.py"))
routed, g500 = planters.routed, planters.g500

from rabbitstew.evolution import generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.fair import is_designed  # noqa: E402
from rabbitstew.genetics import mutate, mutate_controller  # noqa: E402
from rabbitstew.genotype import Brain, Genotype, Link, Neuron, Sensor, UnitRef  # noqa: E402
from rabbitstew.simulation import FoodConfig, SimConfig, Simulation, run_solo, spawn_layout  # noqa: E402

POINT = "W1"
#: steer.sim_hash of W1's intact block as world.py builds it (``gate.py config`` refuses any other)
W1_SIM_HASH = "4784ef27e0c0f44c"
N_DESIGNED, N_HOLISTIC = 4, 4  #: §4.3 G8: 4 designed and 4 holistic burn-in-final hosts from every unit (192)
HOST_KEY = (116, 8)  #: + (unit, fauna): each unit's host permutation (fauna 0 designed, 1 holistic)
G1_KEY, G1_UNITS_N = (116, 1, 16), 16  #: G1: 16 hosts from 16 units, drawn by this key
G4_KEY, G4_N = (116, 4), 200  #: G4: 200 burn-in-final members per fauna (+ fauna index)
U_KEY, U_CHILDREN = (116, 6), 40  #: G6: 40 children per STEERS plant (+ unit, slot, fauna)
RUNGS = (2.0, 6.0, 16.0, 32.0)  #: G1: a = 2w
SCREEN_RUNG = 6.0  #: reading H3: the screen's G8(a) plants are built at a = 6 before G1 can name the first paying rung
C_W = (4.0, 16.0, 64.0)  #: G8(c): ±w per link, 2 signs
F_BUILDS = ((32.0, 16.0), (32.0, 64.0), (128.0, 2.0), (128.0, 16.0))  #: G8(f), Amendment 3 item 4: (g, w), 2 signs
F_PATTERNS = ("common", "diff")  #: reading H9: the two senses "either side" can turn a body; the measured one is used
PILOT_UNIT, PILOT_N, PILOT_GENS = 1, 8, 24  #: G6 SHOULD 11
NOISE_DRAWS = tuple((3131 + j, 4131 + j) for j in range(6))  #: auditor B's noise.py draws (terrain, start)
OPTION_D = {"D8": 8, "D16": 16, "DF16": 20}  #: the draws a boundary member is ranked on (DF16: 4 + 16 at the boundary)
G6_BAR, G8A_FRAC, G8C_POOLED, G8C_UNITS, G8_MAX_FLAGGED, G4_CAP = 1.25, 0.6, 0.20, 18, 4, 0.05
G7_PRIZE = 0.10  #: SHOULD 7: G7's power is printed at a prize of +0.10 items per season
CENSUS_PER_UNIT = 1  #: reading H8: G9's members, one per unit per fauna and group


# --------------------------------------------------------------------------- #
# Paths, config, helpers
# --------------------------------------------------------------------------- #


def b_dir(j: int, kind: str, base: str) -> str:
    return os.path.join(W.unit_dir(j, base), "B", kind, f"gen{W.GEN_B - 1:04d}")


def member_files(d: str) -> list:
    return [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".json")]


def host_perm(j: int, fauna: int, n: int) -> list:
    return [int(i) for i in np.random.default_rng([*HOST_KEY, j, fauna]).permutation(n)]


def w1_config() -> SimConfig:
    return W.w1_sim_config()


def load_cfg(out: str) -> SimConfig:
    raw = json.load(open(os.path.join(out, "config.json")))
    if steer.sim_hash(raw["sim"]) != W1_SIM_HASH:
        raise ValueError(f"{out}/config.json is not W1's block (hash {steer.sim_hash(raw['sim'])}, registered {W1_SIM_HASH})")
    cfg = SimConfig.from_dict(raw["sim"])
    steer.assert_world_point(cfg, POINT)
    steer.assert_registered_channel(cfg, POINT)
    steer.assert_rotation_invariant(cfg, steer.DecoySimulation)
    return cfg


def load_battery(out: str):
    b = steer.Battery.from_dict(json.load(open(os.path.join(out, "battery.json"))))
    steer.assert_battery_size(b, POINT)
    return b


def tune_draws() -> list:
    return steer.draw_pool(POINT)[:planters.N_TUNE]


def pmap(fn, tasks: list, workers: int) -> list:
    if workers > 1 and len(tasks) > 1:
        with ProcessPoolExecutor(workers) as ex:
            return list(ex.map(fn, tasks, chunksize=1))
    return [fn(t) for t in tasks]


def _call(args) -> dict:
    gd, cfg_d, bat_d = args
    return steer._strip(steer.call_genome(gd, SimConfig.from_dict(cfg_d), steer.Battery.from_dict(bat_d)))


def call_all(genomes: list, cfg: SimConfig, battery, workers: int) -> list:
    return pmap(_call, [(g.to_dict(), cfg.to_dict(), battery.to_dict()) for g in genomes], workers)


def _stage2_F(args) -> Optional[float]:
    gd, cfg_d, bat_d = args
    cfg, bat = SimConfig.from_dict(cfg_d), steer.Battery.from_dict(bat_d)
    runs, _ = steer._pairs(gd, cfg, bat.stage2, steer.run_season)
    return steer.battery_stats(runs)["F"] if len(runs["intact"]) >= steer.MIN_USABLE else None


def stage2_F(rec: dict, g: Genotype, cfg: SimConfig, battery) -> Optional[float]:
    """A genome's stage-2 F: from its call when the call reached stage 2, else computed on the stage-2 draws."""
    if rec.get("stage2"):
        return rec["stage2"]["F"]
    return _stage2_F((g.to_dict(), cfg.to_dict(), battery.to_dict()))


def shard_of(items: list, shard: str) -> list:
    i, n = (int(x) for x in shard.split("/"))
    if not 0 <= i < n:
        raise ValueError(f"shard {shard}: need 0 <= I < N")
    return [x for k, x in enumerate(items) if k % n == i]


def write(out: str, name: str, obj) -> None:
    os.makedirs(out, exist_ok=True)
    tmp = os.path.join(out, name + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    os.replace(tmp, os.path.join(out, name))


def done(out: str, name: str) -> bool:
    """A shard's output already written (a re-launched lane skips it: every cell is deterministic)."""
    return os.path.exists(os.path.join(out, name))


def read(out: str, name: str):
    return json.load(open(os.path.join(out, name)))


def exact_upper(k: int, n: int) -> float:
    """The exact (Clopper-Pearson) one-sided upper 95% bound on a binomial rate."""
    return power.binom_upper(k, n)


# --------------------------------------------------------------------------- #
# Planters: (a), (b), (c) and (d), (e) are planters.py's; (c) at RBT-116's w grid; (f) and G7 are new here
# --------------------------------------------------------------------------- #


def tune(variants: list, cfg: SimConfig, draws: list, season=None) -> tuple:
    """planters.tune (the variant with the largest intact - decoy F on the screening draws; ties: the first), except
    that a draw whose decoy has no clear theta (steer.ThetaRefused) is excluded from that variant's mean, as the call
    excludes it (FC-M2; the #540 adversary's F10).  A variant with every draw refused scores -inf.  Returns
    ``(genome, F, table)``, the table's rows ``(name, F, refused)``."""
    season = season or steer.run_season
    table = []
    for g in variants:
        diffs, refused = [], 0
        for d in draws:
            try:
                dec = season(g, cfg, d, "decoy").food
            except steer.ThetaRefused:
                refused += 1
                continue
            diffs.append(season(g, cfg, d, "intact").food - dec)
        table.append((g.name, float(np.mean(diffs)) if diffs else -math.inf, refused))
    best = int(np.argmax([f for _, f, _ in table]))
    return variants[best], table[best][1], table


def plant_c(g: Genotype, layout: dict, sign: float, w: float) -> Genotype:
    """G8(c) as RBT-116 registers it: ±w on EVERY output link (not RBT-129's total gain split over the links), via
    planters.plant_c with a = w × n."""
    return planters.plant_c(g, layout, sign, a=w * len(planters.c_links(g, layout)))


def motion_profile(g: Genotype, cfg: SimConfig, draw) -> dict:
    """One intact season of ``g`` on ``draw``: each Part's mean geom speed (m/s, 3-D, per control tick), the root's net
    yaw (rad, the sum of wrapped per-tick changes) and how far the CoM moved (m).  A body spinning in place turns
    without moving, so nothing is filtered here."""
    c = replace(steer.draw_sim(cfg, draw), opponent_proxy=True)
    sim = Simulation([g], c, spawns=[spawn_layout(2, c, draw.start_seed)[0]])
    sim.set_food_seed(draw.start_seed)
    idx = sim.robots[0]
    geoms = list(idx.geoms)
    com0 = np.array(sim.center_of_mass(0)[:2])
    prev = np.array(sim.data.geom_xpos[geoms])
    speed = np.zeros(len(geoms))
    yaw = last = g500.td.yaw_of(sim)
    net = 0.0
    n = int(round(c.duration / c.control_dt))
    for _ in range(n):
        sim.step()
        cur = np.array(sim.data.geom_xpos[geoms])
        speed += np.linalg.norm(cur - prev, axis=1) / c.control_dt
        prev = cur
        yaw = g500.td.yaw_of(sim)
        net += g500.td.wrap(yaw - last)
        last = yaw
    moved = float(np.linalg.norm(np.array(sim.center_of_mass(0)[:2]) - com0))
    return {"speed": (speed / n).tolist(), "yaw": net, "moved": moved, "phenotype": sim.phenotypes[0]}


def f_layout(g: Genotype, cfg: SimConfig, draw, geom: Optional[dict] = None) -> Optional[dict]:
    """G8(f)'s Effectors "either side": every Effector Node whose instances all lie on one side of the host's measured
    CoM heading (planters.c_layout's rule, without (c)'s two-nose requirement: F3 of the #540 adversary, (f) runs on
    every holistic host).  None if the body has no heading or no one-sided Effector Node."""
    geom = geom if geom is not None else planters.body_geometry(g, cfg, draw)
    if geom is None:
        return None
    lat = geom["lat"]
    sides = {}
    for nd, parts in geom["phenotype"].node_instances.items():
        if not any(u.kind == "effector" for u in g.nodes[nd].segment.brain.units):
            continue
        sg = np.sign(lat[parts])
        if np.all(sg > 0) or np.all(sg < 0):
            sides[nd] = float(sg[0])
    return {"sides": sides} if sides else None


def f_nose(g: Genotype, cfg: SimConfig, draw) -> Optional[int]:
    """G8(f)'s nose Node: the most-moving expressed Part (the largest mean geom speed in one intact season), among
    Parts of single-instance Nodes (reading H10: a Node's Sensor is expressed on every instance, so a multi-instance
    Node cannot carry exactly one nose)."""
    prof = motion_profile(g, cfg, draw)
    if prof["moved"] < 0.05:  # as planters.body_geometry: a body that does not move has no most-moving Part
        return None
    single = [(nd, parts[0]) for nd, parts in prof["phenotype"].node_instances.items() if len(parts) == 1]
    if not single:
        return None
    return int(max(single, key=lambda x: (prof["speed"][x[1]], -x[0]))[0])


def _drive(g: Genotype, links: list, pattern: str, sign: float, w: float, bias: float = 1.0) -> Genotype:
    """A probe: a constant global unit (tanh of ``bias``) driving the one-sided Effectors in ``pattern``."""
    out = copy.deepcopy(g)
    gb = out.global_brain if out.global_brain is not None else Brain()
    out.global_brain = gb
    gb.units.append(Neuron(bias=bias, func="tanh"))
    k = len(gb.units) - 1
    for nd, i, side in links:
        out.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, i), sign * w * (side if pattern == "diff" else 1.0)))
    return out


def turning_pattern(g: Genotype, layout: dict, cfg: SimConfig, draw, w: float = 4.0) -> str:
    """Reading H9 (Amendment 3: "linked ±w to the Effectors either side, in the sense that turns the body the same
    way"): of the two senses a unit can drive the one-sided Effectors in -- the same command to every one
    (``common``: on the Pioneer its steering axis) or opposite commands either side (``diff``: G8(c)'s linking) --
    the one whose constant drive changes the root's net yaw over one intact season the more, against the host's own.
    Ties go to ``common``."""
    links = planters.c_links(g, layout)
    y0 = motion_profile(g, cfg, draw)["yaw"]
    turn = {p: abs(motion_profile(_drive(g, links, p, +1.0, w), cfg, draw)["yaw"] - y0) for p in F_PATTERNS}
    return "diff" if turn["diff"] > turn["common"] else "common"


def plant_f(g: Genotype, nose: int, layout: dict, pattern: str, sign: float, gin: float, w: float) -> Genotype:
    """G8(f) (Amendment 3, item 4): one food sensor on Node ``nose``; a global rectified unit (``relu``) fed by it at
    input −g; linked ±w to the one-sided Effectors in the measured turning ``pattern``."""
    out = copy.deepcopy(g)
    units = out.nodes[nose].segment.brain.units
    units.append(Sensor("food"))
    s = len(units) - 1
    gb = out.global_brain if out.global_brain is not None else Brain()
    out.global_brain = gb
    gb.units.append(Neuron(bias=0.0, func="relu"))
    k = len(gb.units) - 1
    gb.links.append(Link(UnitRef(nose, s), UnitRef(None, k), -gin))
    for nd, i, side in planters.c_links(g, layout):
        out.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, i), sign * w * (side if pattern == "diff" else 1.0)))
    problems = out.validate()
    if problems:
        raise RuntimeError("G8(f) is invalid: " + "; ".join(problems))
    out.name = f"{g.name}+f(n{nose},{pattern},g{gin:g},w{w:g}{'+' if sign > 0 else '-'})"
    return out


def f_variants(g: Genotype, nose: int, layout: dict, pattern: str) -> list:
    return [plant_f(g, nose, layout, pattern, s, gin, w) for gin, w in F_BUILDS for s in (+1.0, -1.0)]


def c_variants(g: Genotype, layout: dict) -> list:
    return [plant_c(g, layout, s, w) for w in C_W for s in (+1.0, -1.0)]


INTERMEDIATES = ("pirouette", "throttle", "same-sign", "one-wheel")


def plant_g7(g: Genotype, kind: str, sign: float, w: float) -> Genotype:
    """G7's one-step intermediates on a designed host, a tanh global unit with ±1 inputs and ±w outputs (routed.install's
    conventions): (i) pirouette: the left wheel's nose → both drive Effectors, the same command (the steering axis);
    (ii) throttle: the left nose → left +, right − (the difference axis); (iii) same-sign: both wheel noses + → both
    drive Effectors (steering); (iv) one-wheel: the left nose → the left wheel's Effector only."""
    nose, eff = routed.unit_indices(g)
    left, right = routed.WHEELS
    out = copy.deepcopy(g)
    gb = out.global_brain if out.global_brain is not None else Brain()
    out.global_brain = gb
    gb.units.append(Neuron(bias=0.0, func="tanh"))
    k = len(gb.units) - 1
    ins = [left, right] if kind == "same-sign" else [left]
    for nd in ins:
        gb.links.append(Link(UnitRef(nd, nose), UnitRef(None, k), 1.0))
    outs = {"pirouette": ((left, 1.0), (right, 1.0)), "throttle": ((left, 1.0), (right, -1.0)),
            "same-sign": ((left, 1.0), (right, 1.0)), "one-wheel": ((left, 1.0),)}[kind]
    for nd, s in outs:
        out.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, eff), sign * s * w))
    problems = out.validate()
    if problems:
        raise RuntimeError(f"G7 {kind} is invalid: " + "; ".join(problems))
    out.name = f"{g.name}+g7-{kind}{'+' if sign > 0 else '-'}{w:g}"
    return out


# --------------------------------------------------------------------------- #
# Cells
# --------------------------------------------------------------------------- #


def cell_config(a) -> int:
    cfg = w1_config()
    raw = {"point": POINT, "sim": cfg.to_dict()}
    h = steer.sim_hash(raw["sim"])
    if h != W1_SIM_HASH:
        raise SystemExit(f"W1's block hashes {h}, registered {W1_SIM_HASH}: world.py and gate.py disagree")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "config.json"), "w") as f:
        json.dump(raw, f, indent=1)
    load_cfg(a.out)
    print(f"W1 block written to {a.out}/config.json (sim hash {h})")
    return 0


def designed_hosts(files: list, j: int, cfg: SimConfig, n: int) -> tuple:
    """Unit j's first ``n`` designed hosts of ``files`` in the registered permutation that carry the routed motif and
    whose two direction probes agree (H4).  The one procedure for B's hosts and for G2's RBT-113 side (H5 as ruled).
    Returns ``(hosts, refused)``."""
    hosts, refused = [], []
    for i in host_perm(j, 0, len(files)):
        if len(hosts) == n:
            break
        g = Genotype.load(files[i])
        try:
            if not is_designed(g):
                raise ValueError("not a designed body")
            routed.unit_indices(g)
        except (AssertionError, StopIteration, ValueError) as e:
            refused.append([files[i], f"(a): {e}"])
            continue
        backs = [planters._direction(g, cfg, probe) for probe in g500.PROBES]
        sign = planters.compass_sign(g, cfg, backs)
        if sign is None:
            refused.append([files[i], "(a): UNDETERMINED direction (the two probes disagree or see no travel)"])
            continue
        hosts.append({"file": files[i], "sign": sign, "backward": bool(backs[0])})
    return hosts, refused


def _hosts_unit(args) -> dict:
    j, cfg_d, base = args
    cfg = SimConfig.from_dict(cfg_d)
    draw0 = tune_draws()[0]
    out = {"unit": j, "designed": [], "holistic": [], "refused": []}
    out["designed"], out["refused"] = designed_hosts(member_files(b_dir(j, "conventional", base)), j, cfg, N_DESIGNED)
    files = member_files(b_dir(j, "holistic", base))
    for i in host_perm(j, 1, len(files))[:N_HOLISTIC]:  # F3: the first 4 of the permutation, whatever they carry
        g = Genotype.load(files[i])
        geom = planters.body_geometry(g, cfg, draw0)
        lay = planters.c_layout(g, geom) if geom is not None else None
        if lay is None:
            out["refused"].append([files[i], f"(c) NONE: {'no heading' if geom is None else 'no two-sided layout'}"])
        flay = f_layout(g, cfg, draw0, geom)
        nose = f_nose(g, cfg, draw0) if flay is not None else None
        pattern = turning_pattern(g, flay, cfg, draw0) if nose is not None else None
        if nose is None:
            out["refused"].append([files[i], f"(f) NONE: {'no heading' if geom is None else 'no one-sided Effector Node' if flay is None else 'no single-instance moving Part'}"])
        out["holistic"].append({"file": files[i],
                                "layout": None if lay is None else {"left": lay["left"], "right": lay["right"], "sides": {str(k): v for k, v in lay["sides"].items()}},
                                "f_sides": None if flay is None else {str(k): v for k, v in flay["sides"].items()},
                                "f_nose": nose, "f_pattern": pattern})
    return out


def _layout(h: dict) -> Optional[dict]:
    if h["layout"] is None:
        return None
    return {"left": h["layout"]["left"], "right": h["layout"]["right"], "sides": {int(k): v for k, v in h["layout"]["sides"].items()}}


def _f_layout(h: dict) -> Optional[dict]:
    return None if h.get("f_sides") is None else {"sides": {int(k): v for k, v in h["f_sides"].items()}}


# --------------------------------------------------------------------------- #
# The registered G8(f) planter check, at run time (tests/test_rbt116_steer.py's one-nose fixture; Amendment 3's F2, F3)
# --------------------------------------------------------------------------- #

FIXTURE = SimConfig(duration=10.0, random_start=True, start_distance_range=(1.0, 1.5),
                    food=FoodConfig(items=4, radius=2.0, decay=1.0, smell_contrast=2.5, smell_tau=steer.SMELL_TAU))
ONE_NOSE_WORLD = replace(FIXTURE, duration=15.0, food=replace(FIXTURE.food, items=8))
FIX_DRAWS = [steer.Draw(100 + i, 200 + i) for i in range(76)]
FIXTURE_VARIANTS = {
    "F2": (replace(ONE_NOSE_WORLD, food=replace(ONE_NOSE_WORLD.food, eat_from="root", eat_rule="surface", clear_from="root")),
           steer.Battery(FIX_DRAWS[:4], FIX_DRAWS[4:20], FIX_DRAWS[20:36])),
    "F3": (ONE_NOSE_WORLD, steer.Battery(FIX_DRAWS[40:44], FIX_DRAWS[44:60], FIX_DRAWS[60:76])),
}


def fixture_host(throttle: float = 0.8) -> Genotype:
    """The one-nose fixture's Pioneer without its nose (test_rbt116_steer._pioneer(noses=(), throttle=0.8))."""
    from rabbitstew.fixed import LEFT_DRIVE, RIGHT_DRIVE, pioneer_genotype

    g = pioneer_genotype(np.random.default_rng(0), hidden=0, sources=("contact",))
    for _, b in g.brains():
        for link in b.links:
            link.weight = 0.0
    g.nodes[LEFT_DRIVE].segment.brain.units[0].bias = +throttle
    g.nodes[RIGHT_DRIVE].segment.brain.units[0].bias = -throttle
    return g


def fixture_plant(cfg: SimConfig, bat) -> tuple:
    """G8(f)'s planter on the fixture host, as the gate runs it on a holistic host: the nose, the measured turning
    sense, the 8 builds tuned on the screening draws.  Returns ``(nose, pattern, best)``."""
    host = fixture_host()
    d0 = bat.stage1[0]
    lay = f_layout(host, cfg, d0)
    nose = f_nose(host, cfg, d0)
    pattern = turning_pattern(host, lay, cfg, d0)
    best, _, _ = tune(f_variants(host, nose, lay, pattern), cfg, bat.stage1)
    return nose, pattern, best


def cell_fixture(a) -> int:
    res = {}
    for k, (cfg, bat) in FIXTURE_VARIANTS.items():
        nose, pattern, best = fixture_plant(cfg, bat)
        rec = steer._strip(steer.call_genome(best, cfg, bat))
        res[k] = {"nose": nose, "pattern": pattern, "plant": best.name, "call": rec["call"], "row": steer.format_call(best.name, rec)}
        print(f"G8(f) fixture {k}: {res[k]['row']}")
    res["pass"] = all(res[k]["call"] == steer.STEERS for k in FIXTURE_VARIANTS)
    write(a.out, "fixture_check.json", res)
    print(f"G8(f) FIXTURE CHECK {'PASS' if res['pass'] else 'FAIL: no gate cell may run (A2/A3)'}")
    return 0 if res["pass"] else 12


def require_fixture(out: str) -> None:
    p = os.path.join(out, "fixture_check.json")
    if not os.path.exists(p) or not json.load(open(p)).get("pass"):
        raise SystemExit("REFUSED: the G8(f) planter check (gate.py fixture) has not passed in this gate directory; "
                         "the registration requires it before any gate cell (Amendments 2 and 3)")


def cell_hosts(a) -> int:
    cfg = load_cfg(a.out)
    units = [j for j in shard_of(list(W.UNITS), a.shard) if not done(os.path.join(a.out, "hosts"), f"unit{j:02d}.json")]
    res = pmap(_hosts_unit, [(j, cfg.to_dict(), a.base) for j in units], a.workers)
    for r in res:
        write(os.path.join(a.out, "hosts"), f"unit{r['unit']:02d}.json", r)
        print(f"unit {r['unit']:2d}: designed {len(r['designed'])}/{N_DESIGNED} (signed by both probes, H4), holistic "
              f"{len(r['holistic'])}/{N_HOLISTIC}; (c) carried by {sum(h['layout'] is not None for h in r['holistic'])}, "
              f"(f) by {sum(h['f_nose'] is not None for h in r['holistic'])}", flush=True)
        for h in r["holistic"]:
            print(f"    holistic {h['file']}: (f) nose {h['f_nose']}, turning sense {h['f_pattern']} (H9)", flush=True)
        for f, why in r["refused"]:
            print(f"    refused {f}: {why}", flush=True)
    return 0


def all_hosts(out: str) -> dict:
    hs = {}
    for j in W.UNITS:
        p = os.path.join(out, "hosts", f"unit{j:02d}.json")
        if not os.path.exists(p):
            raise FileNotFoundError(f"{p}: run the hosts cell for unit {j} first")
        hs[j] = json.load(open(p))
    return hs


def registered_plant_lists(hs: dict) -> tuple:
    """W1's G8(a) and G8(c) host lists, each in registered order (unit 1..24, then host order): Amendment 4's input to
    steer.w1_screen_hosts."""
    da = [(j, k) for j in W.UNITS for k in range(len(hs[j]["designed"]))]
    dc = [(j, k) for j in W.UNITS for k, h in enumerate(hs[j]["holistic"]) if h["layout"] is not None]  # hosts with a (c) plant
    return da, dc


def tuned_c(g: Genotype, lay: dict, cfg: SimConfig) -> tuple:
    return tune(c_variants(g, lay), cfg, tune_draws())


def cell_screen(a) -> int:
    cfg = load_cfg(a.out)
    hs = all_hosts(a.out)
    da, dc = registered_plant_lists(hs)
    picks = steer.w1_screen_hosts(da, dc)
    plants, names = [], []
    for (j, k) in picks[: steer.W1_SCREEN_N]:
        h = hs[j]["designed"][k]
        plants.append(planters.plant_a(Genotype.load(h["file"]), h["sign"], SCREEN_RUNG / 2))
        names.append(f"(a) unit {j} {h['file']}")
    for (j, k) in picks[steer.W1_SCREEN_N:]:
        h = hs[j]["holistic"][k]
        best, F, _ = tuned_c(Genotype.load(h["file"]), _layout(h), cfg)
        plants.append(best)
        names.append(f"(c) unit {j} {h['file']} -> {best.name} (tuning F {F:+.3f})")
    screen = steer.screen_draws(plants, cfg, POINT)
    write(a.out, "reachability.json", screen["table"])
    with open(os.path.join(a.out, "screen.txt"), "w") as f:
        f.write(f"# RBT-116 W1 screen: 16 registered screen hosts (Amendment 4), (a) at a = {SCREEN_RUNG:g} (reading H3)\n")
        for i, n in enumerate(names):
            f.write(f"host {i}: {n}\n")
        f.write(planters.screen_line(screen, POINT, names) + "\n")
        for r in screen["table"]:
            f.write(f"draw {r['terrain_seed']} {r['start_seed']}: ate {r['ate']}/{r['hosts']} admissible {r['admissible']} by host {r['ate_by_host']}\n")
        f.write(f"SCREEN {'PASS' if screen['passed'] else 'FAIL'}: {screen['admissible']} admissible of {len(screen['table'])}"
                f"{' (extended)' if screen['extended'] else ''}\n")
    if not screen["passed"]:
        print(f"W1 FAILS ITS GATE at the screen: {screen['admissible']} admissible draws")
        return 8
    write(a.out, "battery.json", screen["battery"].to_dict())
    print(f"screen PASS: {screen['admissible']} admissible of {len(screen['table'])}")
    return 0


def g1_hosts(hs: dict) -> list:
    """G1's 16 designed hosts: the first designed host of each of 16 units drawn by G1_KEY (in drawn order)."""
    units = [int(u) + 1 for u in np.random.default_rng(list(G1_KEY)).choice(len(W.UNITS), G1_UNITS_N, replace=False)]
    return [(j, hs[j]["designed"][0]) for j in units]


def _blind(args) -> float:
    """Blind (lesion) yield in items: mean food over the stage-2 draws (H5 as ruled: F is in items, so the coverage gain
    is too)."""
    gd, cfg_d, bat_d = args
    cfg, bat = SimConfig.from_dict(cfg_d), steer.Battery.from_dict(bat_d)
    return float(np.mean([steer.run_season(gd, cfg, d, "lesion").food for d in bat.stage2]))


def g1_decide(F_by_rung: dict) -> Optional[float]:
    """G1's rule: the smallest rung whose mean F over hosts has a one-sided 95% t lower bound > 0 is the first paying
    rung; G1 passes iff at it >= 12 of 16 hosts PASS on stage 2.  Returns the rung or None (no rung pays)."""
    for a in RUNGS:
        Fs = [f for f in F_by_rung[a] if f is not None]
        if Fs and steer.lower_bound(Fs) > 0:
            return a
    return None


def cell_g1(a) -> int:
    cfg, bat = load_cfg(a.out), load_battery(a.out)
    hs = all_hosts(a.out)
    hosts = g1_hosts(hs)
    genomes = [Genotype.load(h["file"]) for _, h in hosts]
    rows, recs = {}, {}
    for rung in RUNGS:
        plants = [planters.plant_a(g, h["sign"], rung / 2) for g, (_, h) in zip(genomes, hosts)]
        rs = call_all(plants, cfg, bat, a.workers)
        Fs = [stage2_F(r, p, cfg, bat) for r, p in zip(rs, plants)]
        recs[rung] = rs
        rows[rung] = {"F": Fs, "passes": [bool((r.get("stage2") or {}).get("passes")) for r in rs],
                      "steers": [r["call"] == steer.STEERS for r in rs]}
    first = g1_decide({k: v["F"] for k, v in rows.items()})
    n_pass = sum(rows[first]["passes"]) if first else 0
    c_g1 = sum(rows[first]["steers"]) / len(hosts) if first else 0.0
    g1_ok = bool(first and n_pass >= 12)
    # G2: the first paying rung's F against the coverage gain the burn-in bought, blind, on the same hosts' units
    b_blind = pmap(_blind, [(g.to_dict(), cfg.to_dict(), bat.to_dict()) for g in genomes], a.workers)
    r113, r113_files = [], []
    for j, _ in hosts:
        files = member_files(os.path.join(W.unit_start(j, a.hosts_root), "conventional", "final"))
        picked, refused = designed_hosts(files, j, cfg, 1)  # picked as the B side's host was (H5 as ruled)
        if not picked:
            raise SystemExit(f"G2: unit {j}'s RBT-113 finals give no designed host by the hosts rule ({len(refused)} refused)")
        r113.append(Genotype.load(picked[0]["file"]))
        r113_files.append(picked[0]["file"])
    r_blind = pmap(_blind, [(g.to_dict(), cfg.to_dict(), bat.to_dict()) for g in r113], a.workers)
    gain = float(np.mean(b_blind) - np.mean(r_blind))
    F1 = float(np.mean([f for f in rows[first]["F"] if f is not None])) if first else float("nan")
    g2_ok = bool(first and F1 >= gain)
    res = {"hosts": [[j, h["file"]] for j, h in hosts], "rows": {str(k): v for k, v in rows.items()},
           "first_rung": first, "n_pass": n_pass, "c_G1": c_g1, "G1": g1_ok,
           "G2": {"F_first": F1, "blind_B": b_blind, "blind_R113": r_blind, "R113_hosts": r113_files, "coverage_gain": gain, "pass": g2_ok},
           "calls": {str(k): v for k, v in recs.items()}}
    write(a.out, "g1.json", res)
    lines = [f"# G1: the routed compass at a in {RUNGS} on 16 burn-in-final designed hosts; stage-2 F per host, mean and t bound"]
    for rung in RUNGS:
        Fs = [f for f in rows[rung]["F"] if f is not None]
        lines.append(f"a = {rung:4g}: mean F {np.mean(Fs):+.3f} lb {steer.lower_bound(Fs):+.3f}; stage-2 PASS "
                     f"{sum(rows[rung]['passes'])}/16; confirmed STEERS {sum(rows[rung]['steers'])}/16")
    if first and first != SCREEN_RUNG:
        lines.append(f"NOTE (H3): the first paying rung is a = {first:g}, not the screen's a = {SCREEN_RUNG:g}; the screen's (a) plants "
                     "were built at a = 6 and the battery stands as ruled")
    lines.append(f"G1 {'PASS' if g1_ok else 'FAIL'}: first paying rung {first}; {n_pass}/16 PASS there; c_G1 {c_g1:.3f}")
    lines.append(f"G2 {'PASS' if g2_ok else 'FAIL'}: F at the first paying rung {F1:+.3f} items against the coverage gain {gain:+.3f} items "
                 f"(blind food: burn-in finals {np.mean(b_blind):.3f}, RBT-113 finals {np.mean(r_blind):.3f}, each side's host picked by the hosts rule)")
    open(os.path.join(a.out, "g1.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if g1_ok else 9


def first_rung(out: str) -> float:
    g1 = read(out, "g1.json")
    if not g1["first_rung"]:
        raise SystemExit("G1 found no paying rung: G8(a), G7 and G9's planted Pioneers cannot be built (the gate has failed)")
    return float(g1["first_rung"])


def cell_g8(a) -> int:
    cfg, bat = load_cfg(a.out), load_battery(a.out)
    hs = all_hosts(a.out)
    rung = first_rung(a.out)
    td = tune_draws()
    for j in shard_of(list(W.UNITS), a.shard):
        if done(os.path.join(a.out, "g8"), f"unit{j:02d}.json"):
            continue
        plants = {"a": [], "b": [], "c": [], "f": []}
        notes = []
        for h in hs[j]["designed"]:
            g = Genotype.load(h["file"])
            plants["a"].append(planters.plant_a(g, h["sign"], rung / 2))
            best, F, _ = tune([planters.plant_b(g, *v, planters.slowing_sign(h["backward"])) for v in planters.B_GRID], cfg, td)
            plants["b"].append(best)
            notes.append(f"(b) {h['file']}: {best.name} tuning F {F:+.3f}")
        for h in hs[j]["holistic"]:
            g = Genotype.load(h["file"])
            lay = _layout(h)
            if lay is None:
                plants["c"].append(None)
                notes.append(f"(c) {h['file']}: cannot carry (c) (NONE, counted; F3)")
            else:
                best, F, _ = tuned_c(g, lay, cfg)
                plants["c"].append(best)
                notes.append(f"(c) {h['file']}: {best.name} tuning F {F:+.3f}")
            if h["f_nose"] is None:
                plants["f"].append(None)
                notes.append(f"(f) {h['file']}: cannot carry (f) (NONE, counted; F3)")
                continue
            best, F, _ = tune(f_variants(g, h["f_nose"], _f_layout(h), h["f_pattern"]), cfg, td)
            plants["f"].append(best)
            notes.append(f"(f) {h['file']}: {best.name} (turning sense {h['f_pattern']}) tuning F {F:+.3f}")
        flat = [(k, i, p) for k in ("a", "b", "c", "f") for i, p in enumerate(plants[k]) if p is not None]
        recs = call_all([p for _, _, p in flat], cfg, bat, a.workers)
        calls = {k: [None] * len(plants[k]) for k in plants}
        for (k, i, _), r in zip(flat, recs):
            calls[k][i] = r
        write(os.path.join(a.out, "g8"), f"unit{j:02d}.json", {"unit": j, "rung": rung, "notes": notes, "calls": calls,
              "plants": {k: [None if p is None else p.to_dict() for p in v] for k, v in plants.items()}})
        print(f"unit {j:2d}: " + "; ".join(f"({k}) {sum(1 for r in calls[k] if r and r['call'] == steer.STEERS)}/{len(calls[k])} STEERS" for k in calls), flush=True)
    return 0


def cell_g8_controls(a) -> int:
    cfg, bat = load_cfg(a.out), load_battery(a.out)
    bodies = {"d": [planters.tumbler(j) for j in ("rod", "hinge", "ball")], "e": [planters.tumbler(j, noses=True) for j in ("rod", "hinge", "ball")]}
    out = {k: call_all(v, cfg, bat, a.workers) for k, v in bodies.items()}
    write(a.out, "g8_controls.json", out)
    for k, v in out.items():
        for b, r in zip(bodies[k], v):
            print(f"({k}) {steer.format_call(b.name, r)}")
    return 0


def g4_members(base: str, fauna: int) -> list:
    """G4's 200 members of one fauna (0 designed, 1 holistic): drawn without replacement by G4_KEY from the 960
    burn-in finals in unit order, file order."""
    kind = ("conventional", "holistic")[fauna]
    allm = [f for j in W.UNITS for f in member_files(b_dir(j, kind, base))]
    pick = np.random.default_rng([*G4_KEY, fauna]).choice(len(allm), G4_N, replace=False)
    return [allm[int(i)] for i in pick]


def cell_g4(a) -> int:
    cfg, bat = load_cfg(a.out), load_battery(a.out)
    for fauna in (0, 1):
        files = g4_members(a.base, fauna)
        idx = shard_of(list(range(len(files))), a.shard)
        tag = a.shard.replace("/", "of")
        if done(os.path.join(a.out, "g4"), f"fauna{fauna}_{tag}.json"):
            continue
        recs = call_all([Genotype.load(files[i]) for i in idx], cfg, bat, a.workers)
        write(os.path.join(a.out, "g4"), f"fauna{fauna}_{tag}.json", {"fauna": fauna, "index": idx, "files": [files[i] for i in idx], "calls": recs})
        print(f"G4 fauna {('designed', 'holistic')[fauna]} shard {a.shard}: {sum(r['call'] == steer.STEERS for r in recs)} STEERS of {len(recs)}", flush=True)
    return 0


def noise_components(A: np.ndarray) -> tuple:
    """Auditor B's noise.py arithmetic on a members x draws net-yield matrix: (between-member SD, member x draw SD)
    with the draws' main effects removed (a shared draw cannot mis-rank)."""
    nd = A.shape[1]
    sw = float(np.sqrt((A - A.mean(axis=0)).var(axis=1, ddof=1).mean() * nd / (nd - 1)))
    sb2 = max(float(A.mean(axis=1).var(ddof=1)) - sw ** 2 / nd, 0.0)
    return float(np.sqrt(sb2)), sw


def _solo_net(args) -> float:
    gd, sim_d, seed = args
    return float(run_solo(Genotype.from_dict(gd), SimConfig.from_dict(sim_d), seed)["score"])


def cell_g6_noise(a) -> int:
    ecfg = W.evolution_config("U")
    for j in shard_of(list(W.UNITS), a.shard):
        if done(os.path.join(a.out, "g6_noise"), f"unit{j:02d}.json"):
            continue
        res = {"unit": j}
        for kind in ("holistic", "conventional"):
            ms = [Genotype.load(f) for f in member_files(b_dir(j, kind, a.base))]
            tasks = [(g.to_dict(), generation_sim(ecfg, t).to_dict(), s) for g in ms for t, s in NOISE_DRAWS]
            A = np.array(pmap(_solo_net, tasks, a.workers)).reshape(len(ms), len(NOISE_DRAWS))
            sb, sw = noise_components(A)
            res[kind] = {"net": A.tolist(), "sb": sb, "sw": sw}
        write(os.path.join(a.out, "g6_noise"), f"unit{j:02d}.json", res)
        print(f"unit {j:2d}: holistic sb {res['holistic']['sb']:.3f} sw {res['holistic']['sw']:.3f}; "
              f"designed sb {res['conventional']['sb']:.3f} sw {res['conventional']['sw']:.3f}", flush=True)
    return 0


def u_parents(out: str) -> list:
    """G6's parents: every STEERS G8(a) (designed) and G8(c) (holistic) plant, in unit and host order."""
    ps = []
    for j in W.UNITS:
        g8 = read(os.path.join(out, "g8"), f"unit{j:02d}.json")
        for key, fauna in (("a", 0), ("c", 1)):
            for i, (r, gd) in enumerate(zip(g8["calls"][key], g8["plants"][key])):
                if r and r["call"] == steer.STEERS:
                    ps.append({"unit": j, "slot": i, "fauna": fauna, "genome": gd})
    return ps


def children(parent: Genotype, fauna: int, unit: int, slot: int, mut) -> list:
    """40 children of one parent by its fauna's mutation operator at crossover 0 (designed: mutate_controller under
    --conventional-topology; holistic: mutate), each from its own registered stream."""
    out = []
    for c in range(U_CHILDREN):
        rng = np.random.default_rng([*U_KEY, unit, slot, fauna, c])
        child = (mutate_controller if fauna == 0 else mutate)(parent.copy(), rng, mut)
        child.name = f"{parent.name}~u{c}"
        out.append(child)
    return out


def cell_g6_u(a) -> int:
    cfg, bat = load_cfg(a.out), load_battery(a.out)
    mut = W.evolution_config("U").mutation
    ps = u_parents(a.out)
    for k, p in enumerate(ps):
        if k not in shard_of(list(range(len(ps))), a.shard) or done(os.path.join(a.out, "g6_u"), f"parent{k:04d}.json"):
            continue
        kids = children(Genotype.from_dict(p["genome"]), p["fauna"], p["unit"], p["slot"], mut)
        recs = call_all(kids, cfg, bat, a.workers)
        lost = sum(r["call"] != steer.STEERS for r in recs)
        write(os.path.join(a.out, "g6_u"), f"parent{k:04d}.json", {**{x: p[x] for x in ("unit", "slot", "fauna")}, "lost": lost, "n": len(recs),
              "calls": [r["call"] for r in recs]})
        print(f"parent {k} (unit {p['unit']}, {'designed' if p['fauna'] == 0 else 'holistic'}): {lost}/{len(recs)} children not STEERS", flush=True)
    return 0


def cell_g5(a) -> int:
    """Seconds per generation from each timing run's run.log ("gen N took Xs"), one run per draws option."""
    res = {}
    for opt in W.DRAWS_OPTIONS:
        p = os.path.join(a.out, "g5", opt, "run.log")
        if not os.path.exists(p):
            continue
        took = [float(l.split("took")[1].strip().rstrip("s")) for l in open(p) if " took " in l]
        res[opt] = {"seconds": took, "per_generation": float(np.mean(took)) if took else float("nan"), "workers": a.workers}
    write(a.out, "g5.json", res)
    for k, v in res.items():
        print(f"G5 {k}: {v['per_generation']:.1f} s per generation (wall, {v['workers']} workers) over {len(v['seconds'])} generations")
    return 0


def pooled_noise(out: str) -> dict:
    sb2 = {"holistic": [], "conventional": []}
    sw2 = {"holistic": [], "conventional": []}
    for j in W.UNITS:
        r = read(os.path.join(out, "g6_noise"), f"unit{j:02d}.json")
        for k in sb2:
            sb2[k].append(r[k]["sb"] ** 2)
            sw2[k].append(r[k]["sw"] ** 2)
    return {k: (float(np.sqrt(np.mean(sb2[k]))), float(np.sqrt(np.mean(sw2[k])))) for k in sb2}


def measured_u(out: str) -> dict:
    lost = {0: 0, 1: 0}
    n = {0: 0, 1: 0}
    d = os.path.join(out, "g6_u")
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        r = json.load(open(os.path.join(d, f)))
        lost[r["fauna"]] += r["lost"]
        n[r["fauna"]] += r["n"]
    return {"conventional": (lost[0] / n[0] if n[0] else float("nan"), n[0]), "holistic": (lost[1] / n[1] if n[1] else float("nan"), n[1])}


def g6_table(noise: dict, u: dict, costs: dict) -> list:
    """Per draws option: s_f = 1.27 F_MIN / sigma_P,f(D) (D at the truncation boundary for DF16), (1 + s)(1 - u), and
    whether it passes for both faunas; the plateau Q_f from power.py part 1 at the measured inputs; the cost."""
    rows = []
    for opt, D in OPTION_D.items():
        r = {"option": opt, "D": D, "cost_s_per_gen": costs.get(opt)}
        ok = True
        for kind, fauna in (("holistic", "holistic"), ("conventional", "designed")):
            sb, sw = noise[kind]
            s = 1.27 * steer.F_MIN / math.sqrt(sb ** 2 + sw ** 2 / D)
            uu = u[kind][0]
            gr = (1 + s) * (1 - uu)
            r[kind] = {"s": s, "u": uu, "growth": gr}
            ok = ok and gr >= G6_BAR
        r["passes"] = ok
        rows.append(r)
    return rows


def plateau(sb: float, sw: float, u: float, D: int, reps: int = 60, seed: int = 1166) -> float:
    """power.py part 1's plateau (power.hold) at measured noise and u."""
    import random

    rng = random.Random(seed)
    return sum(power.hold(power.F_MIN, u, sb, sw, D, rng, power.N) for _ in range(reps)) / reps


def cell_g6_pick(a) -> int:
    g5 = read(a.out, "g5.json") if os.path.exists(os.path.join(a.out, "g5.json")) else {}
    if any(o not in g5 for o in W.DRAWS_OPTIONS):  # F10: the cheapest passing option needs every option's measured cost
        raise SystemExit(f"REFUSED: G6's choice needs G5's timing under every draws option; g5.json has {sorted(g5)}")
    noise = pooled_noise(a.out)
    u = measured_u(a.out)
    costs = {k: v["per_generation"] for k, v in g5.items()}
    rows = g6_table(noise, u, costs)
    for r in rows:
        for kind in ("holistic", "conventional"):
            r[kind]["Q"] = plateau(*noise[kind], r[kind]["u"], r["D"])
    passing = [r for r in rows if r["passes"]]
    by_cost = sorted(passing, key=lambda r: (r["cost_s_per_gen"] if r["cost_s_per_gen"] is not None else math.inf, r["D"]))
    chosen = by_cost[0]["option"] if by_cost else "D16"
    res = {"noise": noise, "u": u, "rows": rows, "chosen": chosen, "conditional": not passing}
    write(a.out, "g6.json", res)
    lines = [f"# G6: sigma_P components (pooled over units): holistic sb {noise['holistic'][0]:.3f} sw {noise['holistic'][1]:.3f}; "
             f"designed sb {noise['conventional'][0]:.3f} sw {noise['conventional'][1]:.3f}",
             f"# u_f (children of STEERS plants not STEERS): designed {u['conventional'][0]:.3f} of {u['conventional'][1]}, "
             f"holistic {u['holistic'][0]:.3f} of {u['holistic'][1]}"]
    for r in rows:
        lines.append(f"{r['option']:5s} (D at the boundary {r['D']:2d}): " + "; ".join(
            f"{k} s {r[k]['s']:.3f} u {r[k]['u']:.3f} (1+s)(1-u) {r[k]['growth']:.3f} Q {r[k]['Q']:.2f}" for k in ("holistic", "conventional"))
            + f" | {'PASSES' if r['passes'] else 'fails'} {G6_BAR} | {r['cost_s_per_gen'] or 'cost not measured'} s/gen")
    lines.append("# H14 (ruled): DF16's s and plateau are computed at D = 20 (4 + 16 at the truncation boundary); power.py's holding "
                 "model re-ranks everyone on 20 draws, not only the boundary: an APPROXIMATION")
    lines.append(f"G6 default (the cheapest passing option): {chosen}" + ("" if passing else
                 " -- NO option passes: D = 16 with the conditional sentence (§2.4)"))
    open(os.path.join(a.out, "g6.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


def _plant_F(args) -> Optional[float]:
    return _stage2_F(args)


def pilot_candidates(out: str, hs: dict) -> dict:
    """RBT116-PILOT-10 (H11 amended, D): the pilot's candidate plants per fauna, from EVERY unit, each with the stage-2 F
    the gate already recorded (no new season, no refit, no re-tuning).  Designed (0): every G8(a) plant in the g8
    records (each host's, at the first paying rung) and every G1 plant in g1.json (the 16 G1 hosts at every rung; the G1
    plant at the first paying rung is the g8 plant of the same host, listed once).  Candidates are keyed by (unit,
    host, rung or w), never by name: hosts' names repeat across units.  Holistic (1): every G8(c) plant in the g8 records (each carrying
    host's tuned build; a host that cannot carry (c) contributes nothing).  In BOTH pools a candidate's call must have
    reached stage 2 (a G1 plant stopped at stage 1 has an F in g1's rows, computed for the rung's mean, but is not a
    candidate: M1).  Each candidate is ``(key, F, genome dict)``, key = (unit, host, rung or
    w), the fixed tie-break order."""
    cand = {0: {}, 1: {}}
    for j in W.UNITS:
        g8 = read(os.path.join(out, "g8"), f"unit{j:02d}.json")
        rung = float(g8["rung"])
        for key, fauna in (("a", 0), ("c", 1)):
            for k, (rec, gd) in enumerate(zip(g8["calls"][key], g8["plants"][key])):
                F = ((rec or {}).get("stage2") or {}).get("F")
                if gd is None or F is None:  # no plant (cannot carry), or the call stopped before stage 2: no recorded F
                    continue
                third = rung if fauna == 0 else c_w(gd)
                cand[fauna].setdefault((j, k, third), ((j, k, third), float(F), gd))
    g1 = read(out, "g1.json")
    for h_i, (j, f) in enumerate(g1["hosts"]):
        k = next(i for i, h in enumerate(hs[j]["designed"]) if h["file"] == f)
        h = hs[j]["designed"][k]
        g = Genotype.load(f)
        for r_s, row in g1["rows"].items():
            F = row["F"][h_i]
            # M1 (#555 adversary): g1's F was computed for every call (stage2_F), so admit only a call that reached
            # stage 2 -- the G8 pool's rule, and SHOULD 11's "planted steerers"
            if F is None or not (g1["calls"][r_s][h_i] or {}).get("stage2"):
                continue
            p = planters.plant_a(g, h["sign"], float(r_s) / 2)
            cand[0].setdefault((j, k, float(r_s)), ((j, k, float(r_s)), float(F), p.to_dict()))
    return {fauna: sorted(c.values(), key=lambda x: x[0]) for fauna, c in cand.items()}


def c_w(gd: dict) -> float:
    """A G8(c) plant's per-link w, from its name (planters.plant_c: "+c{a}/{n}{sign}", w = a / n)."""
    a_n = gd["name"].rsplit("+c", 1)[1][:-1]
    a, n = a_n.split("/")
    return float(a) / float(n)


def pick_pilot(cands: list, n: int = None) -> list:
    """The n candidates with F > 0 nearest F_MIN; ties broken by the fixed (unit, host, rung or w) order."""
    n = PILOT_N if n is None else n
    ok = sorted((abs(F - steer.F_MIN), key, F, gd) for key, F, gd in cands if F > 0)
    return [(key, F, gd) for _, key, F, gd in ok[:n]]


def pilot_refused(out: str) -> bool:
    p = os.path.join(out, "pilot.json")
    return os.path.exists(p) and bool(json.load(open(p)).get("refused"))


def cell_pilot_prep(a) -> int:
    """SHOULD 11 (RBT116-PILOT-10: H11 amended): PILOT_UNIT's B gen-12 populations with members 0..7 of each fauna
    replaced by the 8 planted steerers, pooled over every unit, with recorded stage-2 F > 0 nearest F_MIN
    (:func:`pilot_candidates`, :func:`pick_pilot`).  Fallback (A): if either fauna has fewer than 8 such candidates
    (both faunas are counted first), pilot.json records {"refused": true, "paying": ...} and nothing is planted or run;
    the readout then sets the conditional sentence (the registered "Otherwise")."""
    hs = all_hosts(a.out)
    j = PILOT_UNIT
    cands = pilot_candidates(a.out, hs)
    paying = {("designed", "holistic")[f]: sum(F > 0 for _, F, _ in c) for f, c in cands.items()}
    for stale in ("pilot.json",):
        if os.path.exists(os.path.join(a.out, stale)):
            os.remove(os.path.join(a.out, stale))
    if any(v < PILOT_N for v in paying.values()):
        write(a.out, "pilot.json", {"refused": True, "paying": paying, "ruling": "RBT116-PILOT-10 (A)"})
        print(f"pilot: paying candidates {paying} (fewer than {PILOT_N} in a fauna): the holding pilot could not be built; "
              "pilot.json records the refusal; nothing is planted or run (RBT116-PILOT-10, fallback A)")
        return 0
    picked = {f: [(Genotype.from_dict(gd), F, key) for key, F, gd in pick_pilot(c)] for f, c in cands.items()}
    root = os.path.join(a.out, "pilot")
    for fauna, kind in ((0, "conventional"), (1, "holistic")):
        src = member_files(b_dir(j, kind, a.base))
        d = os.path.join(root, "start", kind)
        os.makedirs(d, exist_ok=True)
        for i, f in enumerate(src):
            g = Genotype.load(f)
            if i < PILOT_N:
                p, F, key = picked[fauna][i]
                p = p.copy()
                p.name = f"pilot{i}-{p.name}"
                p.record = {"pilot_F": F, "pilot_from": list(key)}
                g = p
            g.save(os.path.join(d, f"{i:03d}.json"))
    write(root, "pilot_prep.json", {"paying": paying, "picked": {k: [[g.name, F, list(key)] for g, F, key in v] for k, v in picked.items()}})
    print(f"pilot (RBT116-PILOT-10, D): paying candidates {paying}; start populations in {root}/start: "
          + "; ".join(f"{('designed', 'holistic')[k]} F " + ", ".join(f"{F:+.2f}" for _, F, _ in v) for k, v in picked.items()))
    return 0


def pilot_command(out: str, draws_option: str, workers: int = 4) -> list:
    """The pilot's evolve command: unit PILOT_UNIT's U run from the pilot start populations, 24 generations (25
    evaluated, reading H1), at the chosen draws option.  If pilot-prep recorded a refusal (RBT116-PILOT-10, A), a no-op
    the lane's evolve step runs instead (it carries ``--generations 0`` for the lane's parser): nothing is evolved."""
    if pilot_refused(out):
        return ["python", "-c", "print('pilot refused (RBT116-PILOT-10, A): no evolve run')", "--generations", "0"]
    f = W.flags("U", PILOT_UNIT, draws_option, workers, generations=PILOT_GENS + 1)
    i = f.index("--from-population")
    f[i + 1] = f"holistic={os.path.join(out, 'pilot', 'start', 'holistic')}"
    f[i + 3] = f"conventional={os.path.join(out, 'pilot', 'start', 'conventional')}"
    return ["python", "-m", "rabbitstew.cli", "evolve", *f, "--out", os.path.join(out, "pilot", "run")]


def cell_pilot_probe(a) -> int:
    if pilot_refused(a.out):  # RBT116-PILOT-10 (A): pilot.json keeps the refusal
        print("pilot refused (RBT116-PILOT-10, A): nothing to probe; pilot.json keeps the refusal")
        return 0
    cfg, bat = load_cfg(a.out), load_battery(a.out)
    res = {}
    for kind in ("conventional", "holistic"):
        d = os.path.join(a.out, "pilot", "run", kind, f"gen{PILOT_GENS:04d}")
        recs = call_all([Genotype.load(f) for f in member_files(d)], cfg, bat, a.workers)
        res[kind] = {"steers": sum(r["call"] == steer.STEERS for r in recs), "n": len(recs), "calls": [r["call"] for r in recs]}
        print(f"pilot {kind}: {res[kind]['steers']}/{res[kind]['n']} confirmed STEERS at generation {PILOT_GENS}")
    write(a.out, "pilot.json", res)
    return 0


def _g7_host(args) -> dict:
    """One G1 host: its unmodified net yield on the 16 stage-2 draws, and each intermediate's paired difference (the
    prize, in the selection's currency) at every G1 rung (finding 8: the full rungs x intermediates table)."""
    gd, rungs, cfg_d, bat_d = args
    cfg, bat = SimConfig.from_dict(cfg_d), steer.Battery.from_dict(bat_d)
    g = Genotype.from_dict(gd)
    base = [steer.run_season(g, cfg, d, "intact").net for d in bat.stage2]
    out = {"base": base, "rungs": {}}
    for rung in rungs:
        row = {}
        for kind in INTERMEDIATES:
            for s in (+1.0, -1.0):
                p = plant_g7(g, kind, s, rung / 2)
                row[f"{kind}{'+' if s > 0 else '-'}"] = [steer.run_season(p, cfg, d, "intact").net - b for d, b in zip(bat.stage2, base)]
        out["rungs"][f"{rung:g}"] = row
    return out


def g7_power(sd: float, n: int, prize: float = G7_PRIZE) -> float:
    """The paired t's power to see ``prize`` at a one-sided 5% (normal approximation, host-mean SD ``sd``)."""
    if not sd > 0:
        return 1.0
    z = prize / (sd / math.sqrt(n)) - steer.t_quantile(0.95, n - 1)
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def cell_g7(a) -> int:
    cfg, bat = load_cfg(a.out), load_battery(a.out)
    rung = first_rung(a.out)
    hosts = [h for _, h in g1_hosts(all_hosts(a.out))]
    idx = [i for i in shard_of(list(range(len(hosts))), a.shard) if not done(os.path.join(a.out, "g7"), f"host{i:02d}.json")]
    res = pmap(_g7_host, [(Genotype.load(hosts[i]["file"]).to_dict(), list(RUNGS), cfg.to_dict(), bat.to_dict()) for i in idx], a.workers)
    for i, r in zip(idx, res):
        write(os.path.join(a.out, "g7"), f"host{i:02d}.json", {"host": hosts[i]["file"], "first_rung": rung, **r})
        print(f"G7 host {i} at the first paying rung a = {rung:g}: " + "; ".join(f"{k} {np.mean(v):+.3f}" for k, v in r["rungs"][f"{rung:g}"].items()), flush=True)
    return 0


CENSUS_WORLDS = ("W1", "HP", "R113", "R113-root")


def census_config(world: str) -> SimConfig:
    """G9's worlds: W1; HP (RBT-129's HP layout, 3 patches of 0.6 m in the 3 m disc at decay 1.0, otherwise W1's
    block); RBT-113's committed world (its own command line: legacy smell, any-part centre eating); and that world with
    W1's root surface eating (SHOULD 6: the income lost from the committed rule to root eating)."""
    w1 = w1_config()
    if world == "W1":
        return w1
    if world == "HP":
        return replace(w1, food=replace(w1.food, patches=3, patch_radius=0.6, radius=3.0, decay=1.0, regrow_delay=0.0))
    r113 = _load("rbt113_world", os.path.join(ROOT, "runs", "RBT-113", "world.py")).evolution_config("U").sim
    if world == "R113":
        return r113
    if world == "R113-root":
        return replace(r113, food=replace(r113.food, eat_from="root", eat_rule="surface"))
    raise ValueError(world)


def census_members(out: str, base: str, hosts_root: str) -> dict:
    """G9's groups (reading H8: one member per unit per fauna): RBT-113 founders, RBT-113 U finals (intact and blind),
    burn-in finals, and the G8(a) planted Pioneers at the first paying rung."""
    r113w = _load("rbt113_world", os.path.join(ROOT, "runs", "RBT-113", "world.py"))
    hs = all_hosts(out)
    rung = first_rung(out)
    groups = {f"{g}/{k}": [] for g in ("founders", "r113-final", "burn-in-final") for k in ("holistic", "conventional")}
    groups["g8a/conventional"] = []
    for j in W.UNITS:
        op, s = ("", j) if j <= 12 else ("Z", j - 12)
        ecfg = r113w.evolution_config("U", op, seed=s)
        rngs = spawn_streams(ecfg.seed, ecfg.holistic_stream_salt, ecfg.designed_stream_salt)
        for fauna, kind in ((1, "holistic"), (0, "conventional")):
            founders = initial_population(kind, ecfg, rngs[kind]).members
            groups[f"founders/{kind}"].append(founders[host_perm(j, fauna, len(founders))[0]].to_dict())
            fin = member_files(os.path.join(W.unit_start(j, hosts_root), kind, "final"))
            groups[f"r113-final/{kind}"].append(Genotype.load(fin[host_perm(j, fauna, len(fin))[0]]).to_dict())
            bf = member_files(b_dir(j, kind, base))
            groups[f"burn-in-final/{kind}"].append(Genotype.load(bf[host_perm(j, fauna, len(bf))[0]]).to_dict())
        h = hs[j]["designed"][0]
        groups["g8a/conventional"].append(planters.plant_a(Genotype.load(h["file"]), h["sign"], rung / 2).to_dict())
    return groups


def _census_member(args) -> list:
    gd, cfg_d, draws, condition = args
    cfg = SimConfig.from_dict(cfg_d)
    rows = []
    for t, s in draws:
        se = steer.run_season(gd, cfg, steer.Draw(t, s), condition)
        rows.append([se.food, se.work, se.net, se.cells, se.items_per_100_cells, float(np.mean(se.speed)) if len(se.speed) else 0.0])
    return rows


def cell_g9(a) -> int:
    bat = load_battery(a.out)
    groups = census_members(a.out, a.base, a.hosts_root)
    draws = [[d.terrain_seed, d.start_seed] for d in bat.stage2]
    for world in shard_of(list(CENSUS_WORLDS), a.shard):
        if done(os.path.join(a.out, "g9"), f"{world}.json"):
            continue
        cfg = census_config(world)
        res = {}
        for name, gs in groups.items():
            conds = ("intact", "lesion") if name.startswith("r113-final") else ("intact",)
            for cond in conds:
                rows = pmap(_census_member, [(g, cfg.to_dict(), draws, cond) for g in gs], a.workers)
                res[f"{name}/{cond}"] = rows
        write(os.path.join(a.out, "g9"), f"{world}.json", res)
        print(f"G9 {world}: {len(res)} groups", flush=True)
    return 0


def census_summary(res: dict) -> dict:
    """Per group: mean food, work, net, cells, items per 100 cells, speed, and solvency (the share of members whose
    mean net > 0)."""
    out = {}
    for k, rows in res.items():
        A = np.array(rows, dtype=float)  # members x draws x 6
        m = A.mean(axis=(0, 1))
        out[k] = {"food": m[0], "work": m[1], "net": m[2], "cells": m[3], "items_per_100": m[4], "speed": m[5],
                  "solvency": float((A[:, :, 2].mean(axis=1) > 0).mean())}
    return out


def asymmetric_moves(summ: dict, threshold: float = 0.25) -> list:
    """G9's flag (reading H12): for each census quantity, the relative move of the RBT-113 U finals' intact mean from
    RBT-113's world to W1, per fauna; a move whose holistic and designed values differ by more than 25 points is named
    "not the only difference"."""
    flags = []
    for q in ("food", "work", "net", "cells", "items_per_100", "speed", "solvency"):
        mv = {}
        for kind in ("holistic", "conventional"):
            a0 = summ["R113"][f"r113-final/{kind}/intact"][q]
            a1 = summ["W1"][f"r113-final/{kind}/intact"][q]
            mv[kind] = (a1 - a0) / abs(a0) if a0 else (0.0 if a1 == a0 else math.inf)
        if abs(mv["holistic"] - mv["conventional"]) > threshold:
            flags.append(f"{q}: holistic {mv['holistic']:+.0%}, designed {mv['conventional']:+.0%}")
    return flags


# --------------------------------------------------------------------------- #
# The readout
# --------------------------------------------------------------------------- #


def g8_summary(out: str) -> dict:
    """G8's rows from every unit's calls: pooled confirmed shares, per-unit flags (reading H7), SENS_C,P and SENS_1."""
    c_g1 = read(out, "g1.json")["c_G1"]
    share = {k: [0, 0] for k in ("a", "b", "c", "f")}
    b_paying, b_steers, c_units, flagged = 0, 0, 0, []
    for j in W.UNITS:
        g8 = read(os.path.join(out, "g8"), f"unit{j:02d}.json")
        st = {k: [r is not None and r["call"] == steer.STEERS for r in g8["calls"][k]] for k in share}
        for k in share:
            share[k][0] += sum(st[k])
            share[k][1] += len(st[k])
        pay = [r for r in g8["calls"]["b"] if r and (r.get("stage2") or {}).get("F", 0) >= steer.F_MIN]
        b_paying += len(pay)
        b_steers += sum(r["call"] == steer.STEERS for r in pay)
        c_units += any(st["c"])
        why = []
        if len(g8["calls"]["a"]) < N_DESIGNED or len(g8["calls"]["c"]) < N_HOLISTIC:
            why.append("short of hosts")
        if not any(st["a"]):
            why.append("no (a) STEERS")
        if not any(st["c"]):
            why.append("no (c) STEERS")
        if any(r and r["call"] == steer.STEERS for r in g8["calls"]["b"]):
            why.append("(b) STEERS")
        if why:
            flagged.append((j, why))
    ctrl = read(out, "g8_controls.json")
    de = all(r["call"] == steer.NONE for k in ("d", "e") for r in ctrl[k])
    sa, sc, sf = (share[k][0] / share[k][1] if share[k][1] else 0.0 for k in ("a", "c", "f"))
    return {"share": share, "SENS_C_P": sa, "SENS_c": sc, "SENS_1": sf, "SENS_C_H": min(sc, sf),
            "a_pass": sa >= G8A_FRAC * c_g1, "a_bar": G8A_FRAC * c_g1,
            "b_paying": b_paying, "b_steers": b_steers, "b_pass": b_steers == 0,
            "c_pass": sc >= G8C_POOLED and c_units >= G8C_UNITS, "c_units": c_units,
            "de_pass": de, "flagged": flagged, "flag_pass": len(flagged) <= G8_MAX_FLAGGED}


def g4_summary(out: str) -> dict:
    res = {}
    d = os.path.join(out, "g4")
    for fauna, kind in ((0, "designed"), (1, "holistic")):
        calls = []
        for f in sorted(os.listdir(d)):
            if f.startswith(f"fauna{fauna}_"):
                calls += json.load(open(os.path.join(d, f)))["calls"]
        k = sum(r["call"] == steer.STEERS for r in calls)
        ub = exact_upper(k, len(calls)) if calls else 1.0
        res[kind] = {"k": k, "n": len(calls), "EPS_C": k / len(calls) if calls else float("nan"), "upper": ub,
                     "pass": len(calls) == G4_N and ub <= G4_CAP}
    return res


def g7_summary(out: str) -> dict:
    """G7: per rung and intermediate, the mean prize, its one-sided 95% t bound over the 16 host means (H6) and over the
    256 pairs, and the power at +0.10.  It passes iff, at the first paying rung, no bound over hosts is > 0; the other
    rungs are the printed table (the Pioneer's valley at W1)."""
    d = os.path.join(out, "g7")
    hosts = [json.load(open(os.path.join(d, f))) for f in sorted(os.listdir(d))]
    first = f"{hosts[0]['first_rung']:g}" if hosts else None
    table = {}
    for rung in (f"{r:g}" for r in RUNGS):
        rows = {}
        for kind in INTERMEDIATES:
            for s in "+-":
                key = kind + s
                means = [float(np.mean(h["rungs"][rung][key])) for h in hosts]
                allp = [x for h in hosts for x in h["rungs"][rung][key]]
                sd = float(np.std(means, ddof=1)) if len(means) > 1 else 0.0
                rows[key] = {"mean": float(np.mean(means)), "lb_hosts": steer.lower_bound(means), "lb_pairs": steer.lower_bound(allp),
                             "power_0.10": g7_power(sd, len(means))}
        table[rung] = rows
    ok = bool(hosts) and len(hosts) == G1_UNITS_N and all(r["lb_hosts"] <= 0 for r in table[first].values())
    return {"table": table, "first_rung": first, "rows": table.get(first, {}), "n_hosts": len(hosts), "pass": ok}


def power_rerun(sens_p: float, sens_h: float, eps: dict, noise: dict, u: dict, D: int, reps: int = 300) -> dict:
    """power.py at the gate's measured inputs (§7): part 1's plateaus at the measured sigma_P and u and the chosen D;
    part 2a's K rule (false HOLISTIC <= 0.01 at the U/N gap at G4's cap, 600 readouts); part 2c's half-lines bypass at K
    and headlined at K + 2, at SENS_C,H = min(G8(c), G8(f)): "the stronger no" is registered iff the headlined
    detection is >= 0.8."""
    import random

    rng = random.Random(1166)
    QH = plateau(*noise["holistic"], u["holistic"][0], D)
    QP = plateau(*noise["conventional"], u["conventional"][0], D)
    e = max(eps["holistic"]["EPS_C"], eps["designed"]["EPS_C"])
    K = None
    kt = []
    for k in (3, 4, 5, 6, 7, 8, 9):
        f_cap, _ = power.row(rng, 2 * reps, 24, k, 0.04, QH, sens_h, power.EPS_CAP, 0.01, 0.04, QP, sP=sens_p, eP=e)
        fc = f_cap["HOLISTIC MORE READILY"] / (2 * reps)
        kt.append((k, fc))
        if K is None and fc <= 0.01:
            K = k
    if K is None:  # F2: no fallback; the readout prints the table and stops for a ruling
        return {"Q_H": QH, "Q_P": QP, "EPS_C": e, "K_table": kt, "K": None}
    at_k = both = 0
    for _ in range(reps):
        UH = [power.unit(0.5, QH, sens_h, e, e, K, rng) for _ in range(24)]
        UP = [power.unit(0.04, QP, sens_p, e, e, K, rng) for _ in range(24)]
        v1 = power.verdict(UH, UP, rng, 1) == "HOLISTIC MORE READILY"
        at_k += v1
        both += v1 and power.verdict(UH, UP, rng, 2) == "HOLISTIC MORE READILY"
    return {"Q_H": QH, "Q_P": QP, "EPS_C": e, "K_table": kt, "K": K, "detect_at_K": at_k / reps,
            "detect_headlined": both / reps, "stronger_no": both / reps >= 0.8}


READOUT_INPUTS = (["screen.txt", "g1.json", "g1.txt", "g8_controls.json", "g6.json", "g6.txt", "g5.json", "pilot.json"]
                  + [os.path.join("g9", f"{w}.json") for w in CENSUS_WORLDS])


def cell_readout(a) -> int:
    missing = [f for f in READOUT_INPUTS if not os.path.exists(os.path.join(a.out, f))]
    g5 = read(a.out, "g5.json") if "g5.json" not in missing else {}
    missing += [f"g5.json:{o}" for o in W.DRAWS_OPTIONS if "g5.json" not in missing and o not in g5]
    if missing:  # F1, F10: the readout is never written on part of the gate
        raise SystemExit("REFUSED: the gate readout needs every cell's output; missing: " + ", ".join(missing))
    lines = ["# RBT-116 W1 gate readout (PREREGISTRATION.md §4.3); every row from the cells' files under " + a.out]
    ok = {}
    scr = open(os.path.join(a.out, "screen.txt")).read().strip().splitlines()[-1]
    ok["screen"] = scr.startswith("SCREEN PASS")
    lines.append(scr)
    g1 = read(a.out, "g1.json")
    ok["G1"], ok["G2"] = g1["G1"], g1["G2"]["pass"]
    lines += [l for l in open(os.path.join(a.out, "g1.txt")).read().splitlines() if l.startswith(("NOTE", "G1 ", "G2 "))]
    g8 = g8_summary(a.out)
    ok["G8"] = g8["a_pass"] and g8["b_pass"] and g8["c_pass"] and g8["de_pass"] and g8["flag_pass"]
    lines.append(f"G8 {'PASS' if ok['G8'] else 'FAIL'}: (a) confirmed {g8['SENS_C_P']:.3f} (bar 0.6 x c_G1 = {g8['a_bar']:.3f}) "
                 f"{'ok' if g8['a_pass'] else 'FAILS'}; (b) {g8['b_steers']} STEERS among {g8['b_paying']} paying "
                 f"{'ok' if g8['b_pass'] else 'FAILS'}" + ("" if g8["b_paying"] >= 4 else " (fewer than 4 pay: undirected kinesis cannot pay in W1; T's discrimination untested but unneeded)")
                 + f"; (c) {g8['SENS_c']:.3f} pooled, a STEERS host in {g8['c_units']}/24 units {'ok' if g8['c_pass'] else 'FAILS'}; "
                 f"(d), (e) {'all NONE' if g8['de_pass'] else 'NOT all NONE'}; (f) SENS_1 {g8['SENS_1']:.3f}; "
                 f"units flagged {len(g8['flagged'])} {'ok' if g8['flag_pass'] else '(> 4: NO LAUNCH)'}")
    for j, why in g8["flagged"]:
        lines.append(f"    unit {j} flagged: {', '.join(why)}")
    g4 = g4_summary(a.out)
    ok["G4"] = all(v["pass"] for v in g4.values())
    lines.append(f"G4 {'PASS' if ok['G4'] else 'FAIL'}: " + "; ".join(f"{k} {v['k']}/{v['n']} confirmed false STEERS, exact upper "
                 f"{v['upper']:.3f} (cap {G4_CAP})" for k, v in g4.items()))
    g6 = read(a.out, "g6.json")
    lines += open(os.path.join(a.out, "g6.txt")).read().strip().splitlines()
    pil = read(a.out, "pilot.json")
    sens = {"conventional": g8["SENS_C_P"], "holistic": g8["SENS_C_H"]}
    # F1: the pilot is not a pass/fail row: a steerer not held -- or a pilot that could not be built (RBT116-PILOT-10,
    # the registered "Otherwise") -- puts the verdict in conditional-sentence mode (§2.4)
    if pil.get("refused"):
        conditional = True
        lines.append(f"G6 pilot (SHOULD 11; not pass/fail): the holding pilot could not be built (paying candidates {pil.get('paying')}, "
                     f"fewer than {PILOT_N} in a fauna; RBT116-PILOT-10)")
    else:
        held = {k: pil[k]["steers"] / pil[k]["n"] >= 0.25 * sens[k] for k in ("conventional", "holistic")}
        conditional = bool(g6.get("conditional")) or not all(held.values())
        lines.append("G6 pilot (SHOULD 11; not pass/fail): " + "; ".join(f"{k} {pil[k]['steers']}/{pil[k]['n']} at generation {PILOT_GENS} against "
                     f"0.25 x {sens[k]:.3f} {'held' if held[k] else 'NOT held'}" for k in ("conventional", "holistic")))
    lines.append(f"G6 conditional_sentence: {'YES (§2.4: the headline carries the holding sentence)' if conditional else 'no'}"
                 + (" -- holding pilot could not be built" if pil.get("refused") else ""))
    g7 = g7_summary(a.out)
    ok["G7"] = g7["pass"]
    lines.append(f"G7 {'PASS' if g7['pass'] else 'FAIL (the valley is not there: W1 is reported as such, not run)'}: the Pioneer's valley at W1 "
                 f"({g7['n_hosts']} hosts x 16 draws; pass/fail at the first paying rung a = {g7['first_rung']}; the full table, rungs x intermediates:)")
    for rung, rows in g7["table"].items():
        for k, r in rows.items():
            lines.append(f"    a = {rung:>2s} {k:11s} prize {r['mean']:+.3f}  lb (hosts) {r['lb_hosts']:+.3f}  lb (pairs) {r['lb_pairs']:+.3f}  "
                         f"power at +0.10 {r['power_0.10']:.2f}" + ("  <- decides" if rung == g7["first_rung"] else ""))
    summ = {w: census_summary(read(os.path.join(a.out, "g9"), f"{w}.json")) for w in CENSUS_WORLDS}
    lines.append("G9 census (food, work, net, cells, items/100 cells, speed, solvency).  HP is RBT-129's HP layout with "
                 "RBT-129's regrow_delay of 0 (H8: an eaten item regrows at once, elsewhere), otherwise W1's block:")
    for w in CENSUS_WORLDS:
        for k, v in summ[w].items():
            lines.append(f"    {w:9s} {k:34s} " + " ".join(f"{v[q]:8.3f}" for q in ("food", "work", "net", "cells", "items_per_100", "speed", "solvency")))
    for kind in ("holistic", "conventional"):
        a0 = summ["R113"][f"r113-final/{kind}/intact"]["food"]
        a1 = summ["R113-root"][f"r113-final/{kind}/intact"]["food"]
        lines.append(f"    income lost to root eating, {kind} RBT-113 finals: {a0:.3f} -> {a1:.3f} items ({(a1 - a0) / a0 if a0 else 0:+.0%})")
    fl = asymmetric_moves(summ)
    lines.append("    body-asymmetric moves > 25%: " + ("; ".join(fl) + " -> the headline names W1 'not the only difference'" if fl else "none"))
    nz = pooled_noise(a.out)
    u = measured_u(a.out)
    D = OPTION_D[g6["chosen"]]
    pw = power_rerun(g8["SENS_C_P"], g8["SENS_C_H"], g4, nz, u, D)
    if pw["K"] is None:  # F2
        lines.append("    K rule (false HOLISTIC at the gap at G4's cap): " + ", ".join(f"K {k}: {f:.3f}" for k, f in pw["K_table"]))
        lines.append("W1 GATE: STOPPED FOR A RULING: no K in 3..9 meets the R5-1 rule (false HOLISTIC <= 0.01 at the gap at G4's cap)")
        open(os.path.join(a.out, "GATE.txt"), "w").write("\n".join(lines) + "\n")
        print("\n".join(lines))
        return 13
    lines.append(f"power.py at the gate's inputs (D {D}, {g6['chosen']}): Q_H {pw['Q_H']:.2f}, Q_P {pw['Q_P']:.2f}; SENS_C,P {g8['SENS_C_P']:.3f}, "
                 f"SENS_C,H = min({g8['SENS_c']:.3f}, {g8['SENS_1']:.3f}); EPS_C {pw['EPS_C']:.4f}")
    lines.append("    K rule (false HOLISTIC at the gap at G4's cap): " + ", ".join(f"K {k}: {f:.3f}" for k, f in pw["K_table"]) + f" -> K = {pw['K']}")
    lines.append(f"    half-lines bypass: detected {pw['detect_at_K']:.3f} at K, {pw['detect_headlined']:.3f} headlined (K and K + 2): "
                 + ("'the stronger no' is REGISTERED" if pw["stronger_no"] else "'the stronger no' is NOT registered; NEITHER names the lone-nose limit")
                 + " (re-checked at readout, R6-2)")
    passed = all(v for k, v in ok.items())
    lines.append(f"W1 GATE: {'PASS' if passed else 'FAIL'} (" + ", ".join(f"{k} {'ok' if v else 'FAIL'}" for k, v in ok.items()) + ")")
    write(a.out, "gate.json", {"ok": ok, "conditional_sentence": conditional, "g8": {k: v for k, v in g8.items() if k != "share"}, "g4": g4,
                               "g7": g7, "power": pw, "chosen": g6["chosen"]})
    open(os.path.join(a.out, "GATE.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if passed else 11


CELLS = {"config": cell_config, "fixture": cell_fixture, "hosts": cell_hosts, "screen": cell_screen, "g1": cell_g1, "g8": cell_g8,
         "g8-controls": cell_g8_controls, "g4": cell_g4, "g6-noise": cell_g6_noise, "g6-u": cell_g6_u, "g5": cell_g5,
         "g6-pick": cell_g6_pick, "pilot-prep": cell_pilot_prep, "pilot-probe": cell_pilot_probe, "g7": cell_g7,
         "g9": cell_g9, "readout": cell_readout}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("cell", choices=sorted(CELLS))
    ap.add_argument("--out", default=os.path.join("runs", "RBT-116", "gate", "W1"))
    ap.add_argument("--base", default=os.path.join("runs", "RBT-116", "W1"), help="where the units' B runs are")
    ap.add_argument("--hosts-root", default=os.path.join("runs", "RBT-113"), help="the RBT-113 checkpoints, restored")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--shard", default="0/1", help="I/N: this process's share of a shardable cell")
    a = ap.parse_args(argv)
    if a.cell not in ("config", "fixture"):
        require_fixture(a.out)
    return CELLS[a.cell](a)


if __name__ == "__main__":
    sys.exit(main())
