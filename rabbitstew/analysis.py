"""Analysis of evolved bodies and brains, independent of who won.

Three layers:

* **Descriptors** of a genotype's morphology (:func:`morphology_descriptors`)
  and controller (:func:`controller_descriptors`), computed from the
  synthesised phenotype and its rest pose.
* **Solo capability trials** (:func:`capability_profile`): the robot alone in
  fixed situations -- approaching a goal on flat ground, steering to goals at
  several bearings, crossing a fixed bank of random terrains, pushing a
  passive block -- scored by distance, success, stability and actuator work.
* **Functional network analysis**: a static *influence* of each sensor on the
  effectors (:func:`sensor_influence`) and an opt-in *lesion map*
  (:func:`lesion_map`) that silences each unit in turn and measures the
  capability lost.

:func:`analyze_run` applies all of this to an experiment directory (every
generation's best of both populations, the checkpoint champions for
diversity, and the lineage log for ancestry) and writes ``analysis.json``
and ``analysis.html``.
"""

from __future__ import annotations

import json
import math
import os
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass, field, replace
from typing import Callable, Optional

import numpy as np

from .evolution import CONVENTIONAL, HOLISTIC
from .genotype import Genotype, JointType, Node, Segment, Shape, VECTOR_SOURCES
from .simulation import SimConfig, Simulation
from .synthesis import Phenotype, synthesize
from .world import Spawn, WorldConfig, build_model


# --------------------------------------------------------------------------- #
# Descriptors
# --------------------------------------------------------------------------- #


def rest_pose(ph: Phenotype, sim: SimConfig, settle: float = 0.0):
    """Geom centres (n_parts, 3) of the robot alone at the origin; ``settle`` > 0 lets it drop first."""
    cfg = replace(sim, world=replace(sim.world, terrain="flat"))
    s = Simulation([ph.genotype], cfg, spawns=[Spawn()])
    for b in s.brains:  # passive: the pose of the body, not of its behaviour
        b.W[:] = 0.0
        b.bias[:] = 0.0
    if settle > 0:
        s.run(settle)
    idx = s.robots[0]
    pos = np.array([s.data.geom_xpos[g] for g in idx.geoms])
    touching = s.contact_bodies()
    footprint = sum(1 for b in idx.bodies if b in touching)
    return pos, footprint


def _symmetry(pos: np.ndarray) -> float:
    """Best mirror symmetry of the part centres across the two vertical planes through the root (1 = perfect)."""
    if len(pos) < 2:
        return 1.0
    p = pos - pos[0]
    extent = max(float(np.ptp(p, axis=0).max()), 1e-6)
    best = 0.0
    for axis in (0, 1):
        m = p.copy()
        m[:, axis] *= -1
        d = np.array([np.min(np.linalg.norm(p - q, axis=1)) for q in m])
        best = max(best, 1.0 - float(d.mean()) / extent)
    return round(best, 4)


def morphology_descriptors(g: Genotype, sim: SimConfig) -> dict:
    ph = synthesize(g, sim.synthesis)
    parts = ph.parts
    children = {p.index: 0 for p in parts}
    for p in parts:
        if p.parent is not None:
            children[p.parent] += 1
    pos, footprint = rest_pose(ph, sim, settle=1.0)
    joints = [p.joint_type for p in parts if p.parent is not None]
    motors = [p.motor for p in parts if p.parent is not None and p.joint_type != JointType.FIXED]
    n_j = max(1, len(joints))
    extent = np.ptp(pos, axis=0) if len(pos) > 1 else np.zeros(3)
    return {
        "nodes": len(g.nodes),
        "expressed_nodes": len(ph.node_instances),
        "recessive_fraction": round(1.0 - len(ph.node_instances) / len(g.nodes), 4),
        "parts": len(parts),
        "truncated": ph.truncated,
        "max_depth": max(p.depth for p in parts),
        "max_branching": max(children.values()),
        "mass": round(ph.total_mass(), 3),
        "extent_xy": round(float(max(extent[0], extent[1])), 3),
        "height": round(float(extent[2] + max(p.dims[0] for p in parts) * 0.0), 3),
        "footprint": footprint,
        "symmetry": _symmetry(pos),
        "joint_fractions": {jt.name.lower(): round(sum(1 for j in joints if j == jt) / n_j, 3) for jt in JointType},
        "motor_fractions": {m: round(sum(1 for x in motors if x == m) / max(1, len(motors)), 3) for m in ("torque", "position", "velocity")},
        "shape_fractions": {sh.name.lower(): round(sum(1 for p in parts if p.shape == sh) / len(parts), 3) for sh in Shape},
    }


def _adjacency(ph: Phenotype):
    n = len(ph.units)
    out = [[] for _ in range(n)]
    inn = [[] for _ in range(n)]
    for s, d, w in ph.links:
        out[s].append((d, w))
        inn[d].append((s, w))
    return out, inn


def _reachable(start: list[int], out) -> set:
    seen = set(start)
    q = deque(start)
    while q:
        u = q.popleft()
        for v, _ in out[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return seen


def sensor_influence(ph: Phenotype, depth: int = 4) -> list:
    """Static influence of every sensor on the live effectors: total absolute weight along paths up to ``depth`` links."""
    n = len(ph.units)
    if n == 0:
        return []
    M = np.zeros((n, n))
    for s, d, w in ph.links:
        M[d, s] += abs(w)
    M = np.minimum(M, 3.0)
    live = np.array([i for i, ui in enumerate(ph.units) if ui.unit.kind == "effector" and ui.part is not None and ph.parts[ui.part].parent is not None and ph.parts[ui.part].joint_type != JointType.FIXED], dtype=int)
    out = []
    for i, ui in enumerate(ph.units):
        if ui.unit.kind != "sensor":
            continue
        v = np.zeros(n)
        v[i] = 1.0
        total = 0.0
        for _ in range(depth):
            v = M @ v
            total += float(v[live].sum()) if len(live) else 0.0
            if not v.any():
                break
        out.append({"unit": i, "part": ui.part, "label": ui.unit.label, "influence": round(total, 4)})
    return out


def controller_descriptors(g: Genotype, sim: SimConfig) -> dict:
    ph = synthesize(g, sim.synthesis)
    out, inn = _adjacency(ph)
    units = ph.units
    kinds = [u.unit.kind for u in units]
    n = len(units)
    linked = set()
    for s, d, _ in ph.links:
        linked.add(s)
        linked.add(d)
    live = [i for i, u in enumerate(units) if u.unit.kind == "effector" and u.part is not None and ph.parts[u.part].parent is not None and ph.parts[u.part].joint_type != JointType.FIXED]
    driven = [i for i in live if inn[i]]
    active = [i for i in live if inn[i] or abs(getattr(units[i].unit, "bias", 0.0)) > 1e-9]  # driven by inputs or by a constant bias
    sensors = [i for i, k in enumerate(kinds) if k == "sensor"]
    env = [i for i in sensors if units[i].unit.source != "oscillator"]
    osc = [i for i in sensors if units[i].unit.source == "oscillator"]
    reach_env = _reachable(env, out) if env else set()
    reach_osc = _reachable(osc, out) if osc else set()
    # shortest sensor -> live effector path
    path_lengths = []
    for i in driven:
        best = None
        frontier = {i}
        seen = {i}
        d = 0
        while frontier and best is None and d < 12:
            d += 1
            nxt = set()
            for u in frontier:
                for v, _ in inn[u]:
                    if v in seen:
                        continue
                    if kinds[v] == "sensor":
                        best = d
                        break
                    seen.add(v)
                    nxt.add(v)
                if best is not None:
                    break
            frontier = nxt
        if best is not None:
            path_lengths.append(best)
    # units on cycles: reachable from themselves
    cyclic = sum(1 for i in range(n) if any(i in _reachable([v], out) for v, _ in out[i]))
    weights = np.array([w for _, _, w in ph.links]) if ph.links else np.zeros(0)
    global_links = sum(1 for s, d, _ in ph.links if units[s].part is None or units[d].part is None)
    src_hist: dict = {}
    for i in sensors:
        src = units[i].unit.source
        src_hist[src] = src_hist.get(src, 0) + 1
    return {
        "units": n,
        "sensors": len(sensors),
        "neurons": kinds.count("neuron"),
        "effectors": kinds.count("effector"),
        "live_effectors": len(live),
        "driven_effectors": len(driven),
        "active_effectors": len(active),
        "connected_fraction": round(len(linked) / n, 4) if n else 0.0,
        "links": len(ph.links),
        "mean_abs_weight": round(float(np.abs(weights).mean()), 4) if len(weights) else 0.0,
        "centralisation": round(global_links / len(ph.links), 4) if ph.links else 0.0,
        "global_neurons": sum(1 for u in units if u.part is None),
        "cyclic_units": cyclic,
        "mean_sensor_path": round(float(np.mean(path_lengths)), 3) if path_lengths else None,
        "env_driven_effectors": sum(1 for i in driven if i in reach_env),
        "oscillator_driven_effectors": sum(1 for i in driven if i in reach_osc),
        "sensor_sources": src_hist,
        "neuron_funcs": {f: sum(1 for u in units if u.unit.kind == "neuron" and u.unit.func == f) for f in sorted({u.unit.func for u in units if u.unit.kind == "neuron"})},
    }


# --------------------------------------------------------------------------- #
# Solo capability trials
# --------------------------------------------------------------------------- #


@dataclass
class TrialConfig:
    approach_duration: float = 15.0
    steering_bearings: tuple = (90.0, -90.0, 180.0)  #: degrees relative to the initial heading
    steering_distance: float = 2.0
    steering_duration: float = 12.0
    terrain_seeds: tuple = (0, 1, 2, 3, 4, 5)
    terrain_duration: float = 15.0
    push_duration: float = 10.0
    lesion_duration: float = 6.0
    success_radius: float = 0.5
    opponent_proxy: bool = True  #: alone, the opponent sensors point at the goal, as at the start of a bout


def _block_genotype() -> Genotype:
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0)))], name="block")


def _flat(sim: SimConfig, trials: Optional["TrialConfig"] = None) -> SimConfig:
    return replace(sim, world=replace(sim.world, terrain="flat"), target=(0.0, 0.0, 0.0), opponent_proxy=trials.opponent_proxy if trials else False)


def _fell(s: Simulation, ri: int = 0) -> bool:
    R = s.data.xmat[s.robots[ri].root_body].reshape(3, 3)
    return bool(R[2, 2] < 0.0)


def capability_profile(g: Genotype, sim: SimConfig, trials: Optional[TrialConfig] = None) -> dict:
    """Solo trials; every number is about this robot alone."""
    trials = trials or TrialConfig()
    flat = _flat(sim, trials)
    start = np.array([-2.0, 0.0])
    # 1. approach: from (-2, 0) facing the centre, on flat ground
    s = Simulation([g], flat, spawns=[Spawn((-2.0, 0.0, 0.0), 0.0)])
    s.start_recording(every=5)
    s.run(trials.approach_duration)
    path = s.trajectory.as_array()[:, : len(s.phenotypes[0].parts), :3].mean(axis=1)  # centre of the parts per frame
    steps = np.linalg.norm(np.diff(path[:, :2], axis=0), axis=1)
    path_len = float(steps.sum())
    displacement = float(np.linalg.norm(path[-1, :2] - path[0, :2]))
    d_final = s.distance_from_center(0)
    approach = {
        "progress": round(2.0 - d_final, 3),  #: metres gained towards the goal (negative = moved away)
        "final_distance": round(d_final, 3),
        "displacement": round(displacement, 3),
        "path_length": round(path_len, 3),
        "straightness": round(displacement / path_len, 3) if path_len > 1e-6 else 0.0,
        "mean_speed": round(path_len / trials.approach_duration, 3),
        "fell": _fell(s),
        "height_std": round(float(path[:, 2].std()), 4),
        "work": round(float(s.work[0]), 2),
        "work_per_metre": round(float(s.work[0]) / max(path_len, 0.05), 2),
        "exploded": bool(s.exploded[0]),
    }
    # 2. steering: goals at several bearings, same distance
    steer = []
    for bearing in trials.steering_bearings:
        ang = math.radians(bearing)
        target = (float(start[0] + trials.steering_distance * math.cos(ang)), float(start[1] + trials.steering_distance * math.sin(ang)), 0.0)
        cfg = replace(flat, target=target)
        s2 = Simulation([g], cfg, spawns=[Spawn((-2.0, 0.0, 0.0), 0.0)])
        s2.run(trials.steering_duration)
        d = s2.distance_from_center(0)
        steer.append({"bearing": bearing, "final_distance": round(d, 3), "success": bool(d < trials.success_radius)})
    steering = {
        "trials": steer,
        "successes": sum(1 for t in steer if t["success"]),
        "mean_final_distance": round(float(np.mean([t["final_distance"] for t in steer])), 3),
        "mean_progress": round(float(np.mean([trials.steering_distance - t["final_distance"] for t in steer])), 3),
    }
    # 3. terrain: a fixed bank of random terrains, alone
    terr = []
    for seed in trials.terrain_seeds:
        cfg = replace(sim, world=replace(sim.world, terrain="random", terrain_seed=int(seed)), target=(0.0, 0.0, 0.0), opponent_proxy=trials.opponent_proxy)
        s3 = Simulation([g], cfg, spawns=[Spawn((-2.0, 0.0, 0.0), 0.0)])
        s3.run(trials.terrain_duration)
        d = s3.distance_from_center(0)
        terr.append({"seed": int(seed), "final_distance": round(d, 3), "success": bool(d < trials.success_radius)})
    terrain = {
        "trials": terr,
        "success_rate": round(sum(1 for t in terr if t["success"]) / max(1, len(terr)), 3),
        "mean_final_distance": round(float(np.mean([t["final_distance"] for t in terr])), 3),
        "mean_progress": round(float(np.mean([2.0 - t["final_distance"] for t in terr])), 3),
    }
    # 4. pushing: a passive block in the way
    s4 = Simulation([g, _block_genotype()], flat, spawns=[Spawn((-2.0, 0.0, 0.0), 0.0), Spawn((-1.2, 0.0, 0.0), 0.0)])
    block0 = s4.center_of_mass(1)[:2].copy()
    s4.run(trials.push_duration)
    push = {"block_displacement": round(float(np.linalg.norm(s4.center_of_mass(1)[:2] - block0)), 3), "block_mass": round(s4.phenotypes[1].total_mass(), 2)}
    return {"approach": approach, "steering": steering, "terrain": terrain, "push": push}


def capability_score(profile: dict) -> float:
    """One number for lesion comparisons: approach progress plus mean steering progress (metres)."""
    return float(profile["approach"]["progress"]) + float(profile["steering"]["mean_progress"])


def _quick_score(g: Genotype, sim: SimConfig, trials: TrialConfig, lesion: Optional[int] = None) -> float:
    """Approach progress over a short trial, optionally with one unit silenced."""
    flat = _flat(sim, trials)
    s = Simulation([g], flat, spawns=[Spawn((-2.0, 0.0, 0.0), 0.0)])
    if lesion is not None:
        b = s.brains[0]
        b.W[lesion, :] = 0.0
        b.W[:, lesion] = 0.0
        b.bias[lesion] = 0.0
    s.run(trials.lesion_duration)
    return 2.0 - s.distance_from_center(0)


def lesion_map(g: Genotype, sim: SimConfig, trials: Optional[TrialConfig] = None) -> dict:
    """Silence each unit in turn (no inputs, no outputs, no bias) and measure the approach progress lost."""
    trials = trials or TrialConfig()
    ph = synthesize(g, sim.synthesis)
    base = _quick_score(g, sim, trials)
    rows = []
    for i, ui in enumerate(ph.units):
        loss = base - _quick_score(g, sim, trials, lesion=i)
        rows.append({"unit": i, "part": ui.part, "kind": ui.unit.kind, "label": getattr(ui.unit, "label", None) or (ui.unit.func if ui.unit.kind == "neuron" else f"effector {ui.unit.dof}"), "loss": round(loss, 3)})
    losses = np.array([r["loss"] for r in rows]) if rows else np.zeros(0)
    return {
        "baseline": round(base, 3),
        "units": rows,
        "essential_units": int((losses > 0.1).sum()) if len(losses) else 0,  #: units whose loss costs more than 10 cm
        "harmful_units": int((losses < -0.1).sum()) if len(losses) else 0,  #: units whose removal helps
        "effective_fraction": round(float((np.abs(losses) > 0.05).mean()), 3) if len(losses) else 0.0,
    }


# --------------------------------------------------------------------------- #
# Population-level
# --------------------------------------------------------------------------- #


def descriptor_vector(g: Genotype, sim: SimConfig) -> np.ndarray:
    m = morphology_descriptors(g, sim)
    c = controller_descriptors(g, sim)
    return np.array(
        [m["parts"], m["nodes"], m["expressed_nodes"], m["max_depth"], m["mass"], m["extent_xy"], m["symmetry"], m["footprint"]]
        + [m["joint_fractions"][k] for k in ("hinge", "ball", "slider", "fixed")]
        + [m["shape_fractions"][k] for k in ("box", "sphere", "cylinder")]
        + [c["units"], c["links"], c["driven_effectors"], c["connected_fraction"], c["centralisation"], c["cyclic_units"]],
        dtype=float,
    )


def diversity(vectors: list) -> float:
    """Mean pairwise distance of z-scored descriptor vectors, per dimension (0 = identical population)."""
    if len(vectors) < 2:
        return 0.0
    X = np.array(vectors)
    sd = X.std(axis=0)
    sd[sd == 0] = 1.0
    Z = (X - X.mean(axis=0)) / sd
    d = [np.linalg.norm(Z[i] - Z[j]) for i in range(len(Z)) for j in range(i + 1, len(Z))]
    return round(float(np.mean(d)) / math.sqrt(Z.shape[1]), 4)


def read_lineage(run_dir: str) -> dict:
    """``{(population, name): record}`` from lineage.jsonl (empty when the run predates parent tracking)."""
    path = os.path.join(run_dir, "lineage.jsonl")
    out: dict = {}
    if not os.path.exists(path):
        return out
    with open(path) as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                out[(r["population"], r["name"])] = r
    return out


def ancestry(lineage: dict, population: str, name: str) -> list:
    """The chain of first parents from ``name`` back to generation 0 (most recent first)."""
    chain = []
    seen = set()
    cur = name
    while cur and (population, cur) in lineage and cur not in seen:
        seen.add(cur)
        rec = lineage[(population, cur)]
        chain.append({k: rec[k] for k in ("generation", "name", "parents", "fitness", "distance", "parts", "units", "mass") if k in rec})
        cur = rec["parents"][0] if rec["parents"] else None
    return chain


def founders(lineage: dict, population: str, names: list) -> dict:
    """How many distinct generation-0 ancestors the given individuals descend from (all parents followed)."""
    roots = set()
    for name in names:
        stack = [name]
        seen = set()
        while stack:
            cur = stack.pop()
            if cur in seen or (population, cur) not in lineage:
                continue
            seen.add(cur)
            rec = lineage[(population, cur)]
            if not rec["parents"]:
                roots.add(cur)
            stack.extend(rec["parents"])
    return {"founders": len(roots), "of": len(names)}


# --------------------------------------------------------------------------- #
# Whole-run analysis
# --------------------------------------------------------------------------- #


def analyze_individual(g: Genotype, sim: SimConfig, trials: Optional[TrialConfig] = None, lesions: bool = False) -> dict:
    out = {"name": g.name, "parents": list(g.parents), "morphology": morphology_descriptors(g, sim), "controller": controller_descriptors(g, sim), "capability": capability_profile(g, sim, trials)}
    ph = synthesize(g, sim.synthesis)
    out["influence"] = sensor_influence(ph)
    if lesions:
        out["lesions"] = lesion_map(g, sim, trials)
    return out


def _task(args) -> dict:
    gen, kind, gdict, simdict, trials, lesions = args
    g = Genotype.from_dict(gdict)
    sim = SimConfig.from_dict(simdict)
    r = analyze_individual(g, sim, TrialConfig(**trials), lesions)
    r["generation"] = gen
    r["population"] = kind
    return r


def analyze_run(run_dir: str, out_json: Optional[str] = None, out_html: Optional[str] = None, every: int = 5, workers: int = 1, lesions: str = "final", trials: Optional[TrialConfig] = None, log: Optional[Callable[[str], None]] = print) -> dict:
    """Analyse every ``every``-th generation's best of both populations, plus diversity and lineage.

    ``lesions`` is ``"none"``, ``"final"`` (the last generation's bests) or ``"all"``.
    """
    log = log or (lambda s: None)
    trials = trials or TrialConfig()
    with open(os.path.join(run_dir, "config.json")) as f:
        config = json.load(f)
    with open(os.path.join(run_dir, "history.json")) as f:
        history = json.load(f)
    sim = SimConfig.from_dict(config["sim"])
    gens = sorted({e["generation"] for e in history["history"]})
    selected = [g for i, g in enumerate(gens) if i % max(1, every) == 0]
    if gens and gens[-1] not in selected:
        selected.append(gens[-1])
    tasks = []
    for gen in selected:
        for kind in (HOLISTIC, CONVENTIONAL):
            path = os.path.join(run_dir, kind, f"best_gen{gen:04d}.json")
            if not os.path.exists(path):
                continue
            do_lesions = lesions == "all" or (lesions == "final" and gen == gens[-1])
            tasks.append((gen, kind, Genotype.load(path).to_dict(), sim.to_dict(), asdict(trials), do_lesions))
    log(f"analysing {len(tasks)} individuals from {len(selected)} generations" + (f" with {workers} workers" if workers > 1 else ""))
    if workers > 1:
        with ProcessPoolExecutor(workers) as pool:
            results = list(pool.map(_task, tasks, chunksize=1))
    else:
        results = []
        for t in tasks:
            results.append(_task(t))
            log(f"  gen {t[0]} {t[1]}: approach {results[-1]['capability']['approach']['progress']:+.2f} m, steering {results[-1]['capability']['steering']['successes']}/{len(trials.steering_bearings)}, terrain {results[-1]['capability']['terrain']['success_rate']:.2f}")

    # diversity: checkpoint champions and the final population
    div = []
    for kind in (HOLISTIC, CONVENTIONAL):
        for gen in gens:
            d = os.path.join(run_dir, kind, f"champions_gen{gen:04d}")
            if os.path.isdir(d):
                vecs = [descriptor_vector(Genotype.load(os.path.join(d, fn)), sim) for fn in sorted(os.listdir(d)) if fn.endswith(".json")]
                div.append({"generation": gen, "population": kind, "scope": "champions", "n": len(vecs), "diversity": diversity(vecs)})
        final = os.path.join(run_dir, kind, "final")
        if os.path.isdir(final):
            vecs = [descriptor_vector(Genotype.load(os.path.join(final, fn)), sim) for fn in sorted(os.listdir(final)) if fn.endswith(".json")]
            div.append({"generation": gens[-1] if gens else 0, "population": kind, "scope": "final", "n": len(vecs), "diversity": diversity(vecs)})
    # lineage
    lineage = read_lineage(run_dir)
    lin = {}
    if lineage:
        for kind in (HOLISTIC, CONVENTIONAL):
            path = os.path.join(run_dir, kind, f"best_gen{gens[-1]:04d}.json")
            if not os.path.exists(path):
                continue
            best = Genotype.load(path)
            final_names = [r["name"] for (k, _), r in lineage.items() if k == kind and r["generation"] == gens[-1]]
            lin[kind] = {"chain": ancestry(lineage, kind, best.name), "founders": founders(lineage, kind, final_names)}
    out = {"run": os.path.basename(os.path.normpath(run_dir)), "config": {"seed": config.get("seed"), "brain_model": config.get("brain_model"), "terrain": sim.world.terrain, "generations": config.get("generations"), "population_size": config.get("population_size"), "mass_budget": sim.synthesis.mass_budget}, "trials": asdict(trials), "individuals": results, "diversity": div, "lineage": lin}
    if out_json:
        with open(out_json, "w") as f:
            json.dump(out, f)
    if out_html:
        write_analysis_html(out, out_html)
    return out


def write_analysis_html(analysis: dict, path: str, title: Optional[str] = None) -> None:
    from .analysis_page import render

    with open(path, "w") as f:
        f.write(render(analysis, title))


# --------------------------------------------------------------------------- #
# Brain-body synergy: ablations and transplants
# --------------------------------------------------------------------------- #


def _links_zeroed(g: Genotype) -> Genotype:
    c = g.copy()
    for _, b in c.brains():
        for l in b.links:
            l.weight = 0.0
    c.name = g.name + "/bias-only"
    return c


def _links_random(g: Genotype, rng: np.random.Generator) -> Genotype:
    c = g.copy()
    for _, b in c.brains():
        for l in b.links:
            l.weight = float(rng.normal(0.0, 1.0))
    c.name = g.name + "/random-links"
    return c


def _body_perturbed(g: Genotype, rng: np.random.Generator, sigma: float = 0.2) -> Genotype:
    c = g.copy()
    for node in c.nodes:
        seg = node.segment
        seg.dims = tuple(float(np.clip(d * math.exp(rng.normal(0, sigma)), 0.05, 5.0)) for d in seg.dims)
        for conn in node.connections:
            conn.scale = float(np.clip(conn.scale * math.exp(rng.normal(0, sigma)), 0.25, 1.2))
    c.name = g.name + "/body-perturbed"
    return c


def transplant_brain(body: Genotype, donor: Genotype) -> Optional[Genotype]:
    """``body`` with ``donor``'s weights and biases, where the two share network structure.

    Works for genotypes of the same lineage (same node count, same unit
    counts per node, same link lists); returns None when they do not align.
    """
    if len(body.nodes) != len(donor.nodes):
        return None
    c = body.copy()
    for (o1, b1), (o2, b2) in zip(c.brains(), donor.brains()):
        if o1 != o2 or len(b1.units) != len(b2.units) or len(b1.links) != len(b2.links):
            return None
        for u1, u2 in zip(b1.units, b2.units):
            if u1.kind != u2.kind:
                return None
            if u1.kind != "sensor":
                u1.bias = u2.bias
        for l1, l2 in zip(b1.links, b2.links):
            if l1.src != l2.src or l1.dst != l2.dst:
                return None
            l1.weight = l2.weight
    c.name = f"{body.name}/brain-of-{donor.name}"
    return c


def _score(profile: dict) -> dict:
    return {"approach": profile["approach"]["progress"], "steering": profile["steering"]["mean_progress"], "terrain": profile["terrain"]["mean_progress"], "capability": round(capability_score(profile), 3)}


def synergy_profile(g: Genotype, sim: SimConfig, trials: Optional[TrialConfig] = None, donors: Optional[list] = None, seed: int = 0) -> dict:
    """How much of a champion's solo capability survives when its brain or body is replaced.

    ``donors`` are other genotypes whose brains are transplanted into this
    body where the structures align (e.g. other members or ancestors of the
    same run).  A brain that matters shows up as a large drop under
    ``bias_only`` and ``random_links``; a coupled pair shows a drop under
    ``body_perturbed`` and under every transplant.
    """
    trials = trials or TrialConfig()
    rng = np.random.default_rng(seed)
    full = _score(capability_profile(g, sim, trials))
    out = {
        "full": full,
        "bias_only": _score(capability_profile(_links_zeroed(g), sim, trials)),
        "random_links": _score(capability_profile(_links_random(g, rng), sim, trials)),
        "body_perturbed": _score(capability_profile(_body_perturbed(g, rng), sim, trials)),
        "transplants": [],
    }
    for d in donors or []:
        t = transplant_brain(g, d)
        if t is None:
            continue
        out["transplants"].append({"donor": d.name, **_score(capability_profile(t, sim, trials))})
    base = max(full["capability"], 1e-6)
    out["brain_dependence"] = round(1.0 - out["bias_only"]["capability"] / base, 3) if full["capability"] > 0.05 else None
    out["body_dependence"] = round(1.0 - out["body_perturbed"]["capability"] / base, 3) if full["capability"] > 0.05 else None
    if out["transplants"] and full["capability"] > 0.05:
        out["transplant_dependence"] = round(1.0 - float(np.mean([t["capability"] for t in out["transplants"]])) / base, 3)
    return out


def synergy_for_run(run_dir: str, kind: str = HOLISTIC, trials: Optional[TrialConfig] = None, n_donors: int = 3) -> dict:
    """Synergy profile of a run's final best, with brains transplanted from the other final members that align."""
    with open(os.path.join(run_dir, "config.json")) as f:
        config = json.load(f)
    sim = SimConfig.from_dict(config["sim"])
    gens = sorted(int(fn[len("best_gen") : -5]) for fn in os.listdir(os.path.join(run_dir, kind)) if fn.startswith("best_gen"))
    best = Genotype.load(os.path.join(run_dir, kind, f"best_gen{gens[-1]:04d}.json"))
    final = os.path.join(run_dir, kind, "final")
    donors = []
    if os.path.isdir(final):
        for fn in sorted(os.listdir(final)):
            g = Genotype.load(os.path.join(final, fn))
            if g.name != best.name and transplant_brain(best, g) is not None:
                donors.append(g)
            if len(donors) >= n_donors:
                break
    # Ancestors share the champion's structure until a structural mutation; those that were their
    # generation's best are on disk, and the lineage log says which.
    if len(donors) < n_donors:
        lineage = read_lineage(run_dir)
        with open(os.path.join(run_dir, "history.json")) as f:
            best_names = {(e["population"], e["generation"]): e["best_name"] for e in json.load(f)["history"]}
        for anc in ancestry(lineage, kind, best.name)[1:]:
            if best_names.get((kind, anc["generation"])) != anc["name"]:
                continue
            g = Genotype.load(os.path.join(run_dir, kind, f"best_gen{anc['generation']:04d}.json"))
            if transplant_brain(best, g) is not None and abs(anc.get("fitness", 0.0)) > 0:
                donors.append(g)
            if len(donors) >= n_donors:
                break
    res = synergy_profile(best, sim, trials, donors)
    res["name"] = best.name
    res["population"] = kind
    return res
