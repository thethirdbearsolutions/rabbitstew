"""Lab a champion: wiring dump, per-unit lesions and behavioural metrics on fresh draws.

Standing rule: every evolved robot that reaches competence (fresh-draw time at target >= 0.2, or a
nose-dependent forager) gets this treatment before anything is claimed about it.

usage: lab.py RUN_DIR KIND GEN [N_DRAWS]      e.g. lab.py redesign/A-301 holistic 199 12
Prints: the phenotype's units and links; then a table of modes (intact, env sensors blanked,
oscillators blanked, global brain silenced, local brains silenced, and every unit that touches a link
lesioned alone) with progress (m), time at target, path length, straightness, arrival time, hold
fraction after arrival and actuator work, each averaged over N fresh start/terrain draws."""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

run, kind, gen = sys.argv[1], sys.argv[2], int(sys.argv[3]); n = int(sys.argv[4]) if len(sys.argv) > 4 else 12
cfg = replace(SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"]), opponent_proxy=True)
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
ph = synthesize(g, cfg.synthesis)
units = ph.units
print(f"# {run} {kind} gen {gen}: {len(ph.parts)} parts, {len(units)} units, {len(ph.links)} links")
for p in ph.parts:
    print(f"part {p.index}: {p.shape.name.lower()} dims={tuple(round(float(x), 3) for x in p.dims)} joint={p.joint_type.name} parent={p.parent} mass={p.mass:.2f}")
linked = set()
for s, d, _ in ph.links: linked.add(s); linked.add(d)
for i, u in enumerate(units):
    k = u.unit.kind; lab = getattr(u.unit, "label", None) or (u.unit.func if k == "neuron" else f"effector dof{u.unit.dof}")
    b = f" bias={getattr(u.unit, 'bias', 0.0):+.2f}" if k != "sensor" else ""
    print(f"unit {i:3d} part {str(u.part):4s} {k:8s} {lab:16s}{b}{'' if i in linked else '   (unlinked)'}")
print("links:")
for s, d, w in ph.links: print(f"  {s:3d} -> {d:3d} : {w:+.2f}")
GLOBAL = [i for i, u in enumerate(units) if u.part is None]
ENV = [i for i, u in enumerate(units) if u.unit.kind == "sensor" and u.unit.source != "oscillator"]
OSC = [i for i, u in enumerate(units) if u.unit.kind == "sensor" and u.unit.source == "oscillator"]
LOCAL_BRAIN = [i for i, u in enumerate(units) if u.part is not None and u.unit.kind != "effector"]

def trial(seed, mode):
    sp = spawn_layout(2, cfg, seed)[0]
    sim = Simulation([g], cfg, spawns=[sp]); b = sim.brains[0]
    def silence(i): b.W[i, :] = 0; b.W[:, i] = 0; b.bias[i] = 0
    if mode == "no_env":
        for i in ENV: b.W[:, i] = 0
    elif mode == "no_osc":
        for i in OSC: b.W[:, i] = 0
    elif mode == "no_global":
        for i in GLOBAL: silence(i)
    elif mode == "no_local":
        for i in LOCAL_BRAIN: silence(i)
    elif mode.startswith("lesion:"):
        silence(int(mode[7:]))
    steps = int(round(cfg.duration / cfg.control_dt)); path = 0.0
    last = sim.center_of_mass(0)[:2].copy(); p0 = last.copy(); arrive = None; hold = 0
    for t in range(steps):
        sim.step(); p = sim.center_of_mass(0)[:2]
        if t % 5 == 0: path += float(np.linalg.norm(p - last)); last = p.copy()
        if sim.distance_from_center(0) < cfg.target_radius:
            if arrive is None: arrive = sim.time
            hold += 1
    disp = float(np.linalg.norm(sim.center_of_mass(0)[:2] - p0))
    hold_after = hold / max(1, steps - int(round(arrive / cfg.control_dt))) if arrive is not None else 0.0
    return {"progress": float(sim.progress(0)) * float(sim.start_distances[0]), "tat": float(sim.time_at_target(0)), "path": path, "straight": disp / max(path, 1e-6), "arrive": arrive if arrive is not None else float("nan"), "hold": hold_after, "work": float(sim.work[0]) / 1000}

modes = ["intact", "no_env", "no_osc", "no_global", "no_local"] + [f"lesion:{i}" for i in sorted(linked)]
seeds = list(range(8000, 8000 + n))
print(f"\n{'mode':12s} {'progress':>8s} {'tat':>5s} {'path':>6s} {'straight':>8s} {'arrive':>6s} {'hold':>5s} {'work':>5s}  unit")
for m in modes:
    rs = [trial(s, m) for s in seeds]
    mean = lambda k: float(np.nanmean([r[k] for r in rs]))
    who = ""
    if m.startswith("lesion:"):
        i = int(m[7:]); u = units[i]; who = f"part {u.part} {u.unit.kind} {getattr(u.unit, 'label', None) or (u.unit.func if u.unit.kind == 'neuron' else 'effector dof%d' % u.unit.dof)}"
    print(f"{m:12s} {mean('progress'):+8.2f} {mean('tat'):5.2f} {mean('path'):6.1f} {mean('straight'):8.2f} {mean('arrive'):6.1f} {mean('hold'):5.2f} {mean('work'):5.1f}  {who}", flush=True)
