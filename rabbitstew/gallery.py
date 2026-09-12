"""Bout gallery: one page, one slider, every generation's champion bout.

:func:`build_gallery` reads an experiment directory written by
:class:`~rabbitstew.evolution.Experiment`, re-simulates the bout between the
best holistic and the best conventional genotype of every generation (bouts
are deterministic, so nothing needs to be stored during evolution) and
writes a single self-contained HTML page.  The page has a generation slider
drawn over the champion curve, a 3-D replay of the selected bout, cards for
the two contenders, and the round-robin results of the checkpoint when the
generation was one.

An ecology run (:class:`~rabbitstew.ecology.Ecology`) is read the same way,
with seasons in place of generations.  There the run is not a duel: under
the foraging challenge a cohort shares one arena with the food, so the page
replays a group arena of ``group_size`` seats filled by cycling the season's
two champions, in that season's terrain and food draw.  The cards then count
items eaten rather than distance from the centre, and the panel under them
carries the season's ecology --- who was alive, who was born, who died, what
living cost the season charged --- in place of a round-robin checkpoint.
"""

from __future__ import annotations

import json
import os
from typing import Callable, Optional

import numpy as np

from .evolution import CONVENTIONAL, HOLISTIC
from .genotype import Genotype
import mujoco

from .genotype import JointType
from .simulation import SimConfig, run_bout, run_group
from .synthesis import Phenotype, describe, synthesize
from .visualizer import SCENE_JS, THREE_JS_URL, food_payload, scenery_payload
from .world import Spawn, build_model


def _rest_pose(ph: Phenotype, sim: SimConfig) -> dict:
    """The robot alone at the origin, resting on the ground: one frame in trajectory layout."""
    model, data, (idx,) = build_model([ph], [Spawn()], sim.world)
    q = np.zeros(4)
    rows = []
    for gid in idx.geoms:
        mujoco.mju_mat2Quat(q, data.geom_xmat[gid])
        rows.append(np.round(np.concatenate([data.geom_xpos[gid], q]), 4).tolist())
    return {"dt": 0.0, "units": [{"shape": int(p.shape), "dims": [round(float(d), 4) for d in p.dims], "robot": 0} for p in ph.parts], "frames": [rows]}


def _network(ph: Phenotype) -> dict:
    """Units and links of the synthesised brains, for the inspector."""
    units = []
    for ui in ph.units:
        u = ui.unit
        entry = {"kind": u.kind[0], "part": ui.part, "bias": round(getattr(u, "bias", 0.0), 3)}
        if u.kind == "sensor":
            entry["label"] = u.label
        elif u.kind == "neuron":
            entry["label"] = u.func
        else:
            part = ph.parts[ui.part]
            live = part.parent is not None and part.joint_type != JointType.FIXED
            entry["label"] = f"effector {u.dof % part.joint_type.ndof if live else u.dof}" + (f" ({part.motor})" if live and part.motor != "torque" else "")
            entry["live"] = live
            entry["joint"] = part.joint_type.name.lower() if part.parent is not None else "root"
        units.append(entry)
    parts = [{"index": p.index, "node": p.node, "parent": p.parent, "shape": p.shape.name.lower(), "joint": p.joint_type.name.lower() if p.parent is not None else "root"} for p in ph.parts]
    return {"units": units, "links": [[s, d, round(w, 3)] for s, d, w in ph.links], "parts": parts, "global": ph.genotype.global_brain is not None}


def _contender(kind: str, g: Genotype, sim: SimConfig) -> dict:
    ph = synthesize(g, sim.synthesis)
    live = sum(1 for ui in ph.units if ui.unit.kind == "effector" and ui.part is not None and ph.parts[ui.part].parent is not None and ph.parts[ui.part].joint_type != JointType.FIXED)
    return {
        "live_effectors": live,
        "rest": _rest_pose(ph, sim),
        "net": _network(ph),
        "kind": kind,
        "name": g.name,
        "nodes": len(g.nodes),
        "parts": len(ph.parts),
        "mass": round(ph.total_mass(), 2),
        "units": len(ph.units),
        "links": len(ph.links),
        "truncated": ph.truncated,
        "description": describe(ph),
    }


ECOLOGY_STATS = [("alive", "alive"), ("births", "births"), ("deaths", "deaths"), ("mean_age", "mean age"), ("max_age", "oldest"), ("living_cost", "living cost"), ("total_energy", "total energy"), ("capacity", "slots")]


def _run_kind(run_dir: str) -> tuple:
    """Read a run directory and say what shape of run it is.

    Returns ``(config, history, mode, eco)``: ``mode`` is ``"seasons"`` for an
    ecology and ``"generations"`` for the genetic algorithm, and ``eco`` is the
    ecology settings (``None`` for a GA run).
    """
    with open(os.path.join(run_dir, "config.json")) as f:
        config = json.load(f)
    with open(os.path.join(run_dir, "history.json")) as f:
        history = json.load(f)
    eco = config.get("ecology")
    ecology = bool(history.get("ecology")) or eco is not None
    return config, history, ("seasons" if ecology else "generations"), (eco or {} if ecology else None)


def _pop_stats(entry: dict) -> dict:
    """Best and mean of a population this step, whichever pair of names the run wrote."""
    best = entry.get("best_fitness", entry.get("best_lifetime_score", 0.0))
    mean = entry.get("mean_fitness", entry.get("mean_lifetime_score", 0.0))
    return {"best": round(float(best), 3), "mean": round(float(mean), 3)}


def _seats(group_size: int) -> list:
    """Who sits where in a group arena: the two fauna alternate, so seat colours
    (``robot % palette``) and the cards agree, and neither fauna gets the same
    corner every time."""
    return [HOLISTIC if i % 2 == 0 else CONVENTIONAL for i in range(group_size)]


def _seat_label(kind: str, copy: int) -> str:
    base = "Holistic best" if kind == HOLISTIC else "Conventional best"
    return base if copy == 0 else f"{base} (copy {copy + 1})"


def build_gallery(
    run_dir: str,
    out_path: str,
    every: int = 1,
    record_every: int = 4,
    title: Optional[str] = None,
    log: Optional[Callable[[str], None]] = print,
    gens: Optional[list] = None,
) -> dict:
    """Re-simulate the champion bout (or foraging arena) of every ``every``-th
    generation or season and write the page.

    ``gens`` adds specific generations or seasons to the selection (or replaces
    it when ``every`` is 0).  Returns a summary dict with the number of steps
    rendered and the output size in bytes.
    """
    log = log or (lambda s: None)
    config, history, mode, eco = _run_kind(run_dir)
    ecology = mode == "seasons"
    key = "season" if ecology else "generation"
    sim = SimConfig.from_dict(config["sim"])
    sim.record_every = max(1, record_every)
    group = bool(ecology and eco.get("challenge") == "foraging")
    seats = _seats(int(eco.get("group_size", 4))) if group else [HOLISTIC, CONVENTIONAL]

    by_step: dict[int, dict] = {}
    for e in history["history"]:
        by_step.setdefault(e[key], {})[e["population"]] = e
    checkpoints = {c["generation"]: c for c in history.get("champions") or []}
    all_steps = sorted(by_step)
    selected = set(g for i, g in enumerate(all_steps) if every > 0 and i % every == 0)
    if all_steps and every > 0:
        selected.add(all_steps[-1])
    if gens:
        selected.update(g for g in gens if g in by_step)
    selected = sorted(selected)

    entries = []
    for step in selected:
        h_path = os.path.join(run_dir, HOLISTIC, f"best_gen{step:04d}.json")
        c_path = os.path.join(run_dir, CONVENTIONAL, f"best_gen{step:04d}.json")
        if not (os.path.exists(h_path) and os.path.exists(c_path)):
            log(f"{key} {step}: best genotypes missing, skipped")
            continue
        champions = {HOLISTIC: Genotype.load(h_path), CONVENTIONAL: Genotype.load(c_path)}
        row = by_step[step].get(HOLISTIC, {}) or by_step[step].get(CONVENTIONAL, {})
        gen_sim = sim
        seed = row.get("terrain_seed")
        if seed is not None and sim.world.terrain == "random":
            from dataclasses import replace

            gen_sim = replace(sim, world=replace(sim.world, terrain_seed=int(seed)))
        start_seed = row.get("start_seed") if ecology else (row.get("start_seeds") or [None])[0]

        seen: dict = {}
        contenders = []
        for i, kind in enumerate(seats):
            copy = seen.get(kind, 0)
            seen[kind] = copy + 1
            c = _contender(kind, champions[kind], sim)
            c["label"] = _seat_label(kind, copy)
            c["seat"] = i
            contenders.append(c)

        if group:
            rows, traj = run_group([champions[k] for k in seats], gen_sim, start_seed=start_seed, record=True)
            best = int(np.argmax([r["score"] for r in rows]))
            bout = {
                "food": [round(r["food"], 1) for r in rows],
                "score": [round(r["score"], 3) for r in rows],
                "work": [round(r["work"] / 1000.0, 2) for r in rows],
                "moved": [round(r["path"], 2) for r in rows],
                "exploded": [r["exploded"] for r in rows],
                "winner": best,
                "terrain_seed": seed,
                "start_seed": start_seed,
            }
            log(f"season {step}: {' vs '.join(c['name'] for c in contenders)}: food {'/'.join(str(f) for f in bout['food'])}, {traj.n_frames} frames")
        else:
            res = run_bout(champions[HOLISTIC], champions[CONVENTIONAL], gen_sim, record=True, start_seed=start_seed)
            traj = res.trajectory
            bout = {
                "distances": [round(d, 3) for d in res.distances],
                "fitness": [round(f, 3) for f in res.fitness],
                "exploded": res.exploded,
                "winner": res.winner,
                "terrain_seed": seed,
                "start_seed": start_seed,
                "time_at_target": [round(t, 3) for t in res.time_at_target],
            }
            log(f"{key} {step}: {champions[HOLISTIC].name} vs {champions[CONVENTIONAL].name}: fitness {res.fitness[0]:.3f} / {res.fitness[1]:.3f}, {traj.n_frames} frames")

        frames = np.round(traj.as_array(), 3)
        entry = {
            "gen": step,
            "contenders": contenders,
            "bout": bout,
            "stats": {k: _pop_stats(v) for k, v in by_step[step].items()},
            "traj": {"dt": traj.dt, "units": [{"shape": int(u.shape), "dims": [round(float(d), 4) for d in u.dims], "robot": traj.robot_of_unit(i)} for i, u in enumerate(traj.units)], "frames": frames.tolist(), "scenery": scenery_payload(traj), "food": food_payload(traj)},
        }
        if ecology:
            entry["eco"] = {k: {name: v.get(name) for name, _ in ECOLOGY_STATS} | {"merged": bool(v.get("merged"))} for k, v in by_step[step].items()}
        cp = checkpoints.get(step)
        if cp:
            entry["checkpoint"] = {
                "mode": cp["mode"],
                "mean": round(cp["holistic_mean_fitness"], 3),
                "wins": cp["holistic_wins"],
                "losses": cp["conventional_wins"],
                "n": cp["n_bouts"],
                "bouts": [{"h": b["holistic"], "c": b["conventional"], "swapped": b["swapped"], "f": round(b["holistic_fitness"], 3)} for b in cp["bouts"]],
            }
        entries.append(entry)

    if ecology:
        curve = [{"gen": s, "holistic": round(float(by_step[s].get(HOLISTIC, {}).get("mean_lifetime_score", 0.0)), 3), "conventional": round(float(by_step[s].get(CONVENTIONAL, {}).get("mean_lifetime_score", 0.0)), 3)} for s in all_steps]
    else:
        curve = [{"gen": c["generation"], "mean": round(c["holistic_mean_fitness"], 3)} for c in history.get("champions") or []]
    payload = {
        "run": os.path.basename(os.path.normpath(run_dir)),
        "mode": mode,
        "group": group,
        "config": {"seed": config.get("seed"), "population_size": config.get("population_size"), "generations": config.get("generations"), "duration": sim.duration, "champions": config.get("champions"), "champion_mode": config.get("champion_mode"), "seasons": (eco or {}).get("seasons"), "capacity": (eco or {}).get("capacity"), "challenge": (eco or {}).get("challenge"), "group_size": len(seats) if group else None},
        "copy": _copy(mode, group, len(seats)),
        "curve": curve,
        "entries": entries,
    }
    data = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    html = _TEMPLATE.replace("__TITLE__", title or f"Rabbitstew {'seasons' if ecology else 'bouts'}, {payload['run']}").replace("__THREE__", THREE_JS_URL).replace("__SCENE__", SCENE_JS).replace("__DATA__", data)
    with open(out_path, "w") as f:
        f.write(html)
    size = os.path.getsize(out_path)
    log(f"wrote {out_path}: {len(entries)} {mode}, {size / 1e6:.1f} MB")
    return {mode: len(entries), "generations": len(entries), "bytes": size}


def _copy(mode: str, group: bool, seats: int) -> dict:
    """The words on the page, which differ between a duel and an ecology."""
    if mode == "generations":
        return {
            "step": "Generation",
            "h1": "Champion bouts, generation by generation",
            "lead": "Each generation's best holistic creature (blue) meets the best fixed-body Pioneer (orange) in the arena. Bouts are re-simulated from the saved genotypes, so the replay is exactly the physics the experiment ran. Slide through the run to watch what evolution came up with.",
            "trackNote": "Line: holistic mean fitness at each round-robin checkpoint. Dots: this generation's replayed best-versus-best bout, coloured by the winner. Dashed: parity.",
            "sceneHelp": "Drag to orbit, wheel to zoom, right-drag to pan. The white ring marks the centre both robots are racing for.",
        }
    if group:
        return {
            "step": "Season",
            "h1": "Foraging seasons, one arena at a time",
            "lead": f"An ecology has no ranking round: each season a cohort shares one arena and eats what it can find. Here the season's best holistic forager (blue) and best fixed-body forager (orange) fill {seats} seats between them, in that season's terrain and food draw. Green spheres are food; a ring blooms in the eater's colour wherever an item goes.",
            "trackNote": "Lines: mean lifetime score of each fauna, season by season. Dots: the best score in this season's replayed arena, coloured by the fauna that took it.",
            "sceneHelp": "Drag to orbit, wheel to zoom, right-drag to pan. Green spheres are food; the bloom marks the moment an item was eaten.",
        }
    return {
        "step": "Season",
        "h1": "Champion bouts, season by season",
        "lead": "An ecology has no ranking round: individuals gain energy from the season's challenge, breed when they can afford to, and die of starvation or old age. Each season's best holistic creature (blue) meets the best fixed-body Pioneer (orange), re-simulated from the saved genotypes.",
        "trackNote": "Lines: mean lifetime score of each fauna, season by season. Dots: this season's replayed best-versus-best bout, coloured by the winner.",
        "sceneHelp": "Drag to orbit, wheel to zoom, right-drag to pan. The white ring marks the centre both robots are racing for.",
    }


_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@500;600&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root {
  color-scheme: light;
  --surface: #fbfbf9; --surface-2: #f1f1ed; --line: #dcdcd5; --grid: #e8e8e2;
  --ink: #15161a; --ink-2: #4f5158; --ink-3: #7e8088;
  --holistic: #2a78d6; --conventional: #eb6834; --parity: #8d8e90;
  --holistic-2: #14539b; --conventional-2: #a2400f; --food: #4f9d5d;
  --scene: #eeeeea; --scene-grid-1: #b9b9b1; --scene-grid-2: #dcdcd5; --scene-ring: #15161a;
  --unit-sensor: #1baf7a; --unit-neuron: #4a3aa7; --unit-effector: #eda100; --w-pos: #2a78d6; --w-neg: #e34948;
  --font-display: 'Spectral', Georgia, 'Times New Roman', serif;
  --font-body: 'Source Sans 3', 'Segoe UI', Helvetica, Arial, sans-serif;
  --font-mono: 'IBM Plex Mono', ui-monospace, 'SF Mono', Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --surface: #1a1b1e; --surface-2: #232428; --line: #35363b; --grid: #2b2c31;
    --ink: #f2f2ee; --ink-2: #c2c2bb; --ink-3: #8c8d92;
    --holistic: #3987e5; --conventional: #d95926; --parity: #8d8e90;
    --holistic-2: #8fc0f5; --conventional-2: #f0996b; --food: #6bc47a;
    --scene: #202124; --scene-grid-1: #55565c; --scene-grid-2: #303136; --scene-ring: #f2f2ee;
    --unit-sensor: #199e70; --unit-neuron: #9085e9; --unit-effector: #c98500; --w-pos: #3987e5; --w-neg: #e66767;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --surface: #1a1b1e; --surface-2: #232428; --line: #35363b; --grid: #2b2c31;
  --ink: #f2f2ee; --ink-2: #c2c2bb; --ink-3: #8c8d92;
  --holistic: #3987e5; --conventional: #d95926; --parity: #8d8e90;
  --holistic-2: #8fc0f5; --conventional-2: #f0996b; --food: #6bc47a;
  --scene: #202124; --scene-grid-1: #55565c; --scene-grid-2: #303136; --scene-ring: #f2f2ee;
  --unit-sensor: #199e70; --unit-neuron: #9085e9; --unit-effector: #c98500; --w-pos: #3987e5; --w-neg: #e66767;
}
* { box-sizing: border-box; }
[hidden] { display: none !important; }
body { margin: 0; background: var(--surface); color: var(--ink); font-family: var(--font-body); font-size: 15px; line-height: 1.45; padding-block: 28px 48px; padding-inline: 20px; }
main { max-width: 1180px; margin: 0 auto; display: grid; gap: 22px; }
header { display: grid; gap: 6px; }
.eyebrow { font-family: var(--font-mono); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-3); }
h1 { font-family: var(--font-display); font-weight: 600; font-size: clamp(24px, 3.4vw, 32px); line-height: 1.15; margin: 0; text-wrap: balance; }
p { margin: 0; color: var(--ink-2); max-width: 70ch; }
.mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }

.timeline { display: grid; gap: 6px; }
.timeline-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.timeline-head .gen { font-family: var(--font-display); font-size: 22px; }
.timeline-head .gen b { font-family: var(--font-mono); font-weight: 500; }
.timeline-head .hint { font-size: 13px; color: var(--ink-3); }
.track { position: relative; height: 92px; }
.track svg { position: absolute; inset: 0; width: 100%; height: 100%; display: block; overflow: visible; }
.track svg text { font-family: var(--font-mono); font-size: 10px; fill: var(--ink-3); }
.track input[type=range] { position: absolute; left: 0; right: 0; bottom: 0; width: 100%; margin: 0; height: 26px; cursor: pointer; accent-color: var(--holistic); }
.track-note { font-size: 12px; color: var(--ink-3); }
.nav { display: flex; gap: 8px; align-items: center; }
button, select { font: inherit; font-size: 13px; background: var(--surface-2); color: var(--ink); border: 1px solid var(--line); border-radius: 4px; padding: 5px 12px; cursor: pointer; }
button:hover { border-color: var(--ink-3); }
button:focus-visible, select:focus-visible, input:focus-visible, summary:focus-visible { outline: 2px solid var(--holistic); outline-offset: 2px; }

.stage { display: grid; grid-template-columns: minmax(0, 2fr) minmax(280px, 1fr); gap: 20px; align-items: start; }
.viewport { position: relative; aspect-ratio: 16 / 10; max-width: 100%; background: var(--scene); border: 1px solid var(--line); border-radius: 4px; overflow: hidden; }
.viewport canvas { display: block; width: 100%; height: 100%; }
.viewport .fallback { position: absolute; inset: 0; display: grid; place-items: center; color: var(--ink-3); padding: 24px; text-align: center; }
.transport { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-top: 10px; font-size: 13px; color: var(--ink-2); }
.transport input[type=range] { flex: 1; min-width: 140px; accent-color: var(--ink-2); }
.transport .time { min-width: 56px; text-align: right; }
.scenehelp { font-size: 12px; color: var(--ink-3); margin-top: 6px; }

.side { display: grid; gap: 14px; align-content: start; }
#cards { display: grid; gap: 14px; }
#wide:empty { display: none; }
#wide #cards { grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
#wide .mini { aspect-ratio: 4 / 3; }
.card { border: 1px solid var(--line); border-radius: 4px; padding: 12px 14px; display: grid; gap: 8px; position: relative; }
.mini { aspect-ratio: 5 / 3; max-width: 100%; background: var(--scene); border: 1px solid var(--line); border-radius: 3px; overflow: hidden; cursor: grab; }
.mini canvas { display: block; width: 100%; height: 100%; }
.actions { display: flex; align-items: center; gap: 10px; }
.minihelp { font-size: 12px; color: var(--ink-3); }
dialog { width: min(1100px, calc(100vw - 32px)); max-height: calc(100vh - 32px); background: var(--surface); color: var(--ink); border: 1px solid var(--line); border-radius: 6px; padding: 18px 20px; }
dialog::backdrop { background: rgba(0, 0, 0, 0.45); }
.inspector-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.inspector-head h2 { font-family: var(--font-display); font-weight: 500; font-size: 20px; margin: 4px 0 0; }
.insp-summary { margin-top: 6px; font-size: 14px; }
.insp-legend { display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: 12px; color: var(--ink-2); margin: 10px 0 6px; align-items: center; }
.insp-legend span { display: inline-flex; align-items: center; gap: 6px; }
.insp-hint { color: var(--ink-3); }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.dot.sensor { background: var(--unit-sensor); } .dot.neuron { background: var(--unit-neuron); } .dot.effector { background: var(--unit-effector); }
.dot.inert { background: transparent; border: 2px solid var(--unit-effector); box-sizing: border-box; }
.w { width: 18px; height: 0; border-top: 2px solid; display: inline-block; } .w.pos { border-color: var(--w-pos); } .w.neg { border-color: var(--w-neg); }
.insp-graph { position: relative; overflow: auto; max-height: 60vh; border: 1px solid var(--line); border-radius: 4px; background: var(--surface-2); }
.insp-graph svg { display: block; }
.insp-graph text { font-family: var(--font-mono); font-size: 10px; fill: var(--ink-2); pointer-events: none; }
.insp-graph text.row { font-size: 11px; fill: var(--ink); }
.insp-graph .link { fill: none; opacity: 0.55; }
.insp-graph .link.dim { opacity: 0.06; }
.insp-graph .link.lit { opacity: 1; }
.insp-graph .unit { cursor: default; }
.insp-graph .unit.dim { opacity: 0.25; }
.insp-tip { position: absolute; pointer-events: none; background: var(--surface); border: 1px solid var(--line); border-radius: 4px; padding: 6px 9px; font-size: 12px; color: var(--ink-2); box-shadow: 0 2px 8px rgba(0,0,0,0.15); z-index: 2; white-space: nowrap; }
.insp-tip b { font-family: var(--font-mono); font-weight: 500; color: var(--ink); }
.card { border-left: 4px solid var(--line); }
.card .swatch { width: 9px; height: 9px; border-radius: 2px; display: inline-block; margin-right: 7px; vertical-align: baseline; }
.eco { display: grid; grid-template-columns: auto repeat(2, minmax(0, 1fr)); gap: 2px 10px; font-size: 13px; color: var(--ink-2); }
.eco b { font-family: var(--font-mono); font-weight: 500; color: var(--ink); font-variant-numeric: tabular-nums; }
.eco .hd { font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; }
.eco .hd.h { color: var(--holistic); } .eco .hd.c { color: var(--conventional); }
.eco .num { text-align: right; }
.food-key { display: inline-flex; align-items: center; gap: 6px; }
.food-key i { width: 9px; height: 9px; border-radius: 50%; background: var(--food); display: inline-block; }
.card .who { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.card .who .kind { font-family: var(--font-display); font-size: 17px; }
.card .who .name { font-family: var(--font-mono); font-size: 12px; color: var(--ink-3); }
.card .result { display: flex; gap: 14px; align-items: baseline; }
.card .result .fit { font-family: var(--font-mono); font-size: 26px; font-weight: 500; line-height: 1; font-variant-numeric: tabular-nums; }
.card .result .dist { font-size: 13px; color: var(--ink-2); }
.badge { font-family: var(--font-mono); font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; padding: 2px 6px; border-radius: 3px; border: 1px solid currentColor; }
.badge.win { color: var(--ink); }
.badge.lose { color: var(--ink-3); }
.badge.exploded { color: var(--conventional); }
.facts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2px 12px; font-size: 13px; color: var(--ink-2); }
.facts b { font-family: var(--font-mono); font-weight: 500; color: var(--ink); font-variant-numeric: tabular-nums; }
.checkpoint { border-top: 1px solid var(--line); padding-top: 12px; display: grid; gap: 8px; }
.checkpoint h3 { font-family: var(--font-display); font-weight: 500; font-size: 16px; margin: 0; }
.checkpoint .sum { font-size: 13px; color: var(--ink-2); }
.checkpoint .sum b { font-family: var(--font-mono); font-weight: 500; color: var(--ink); }
.rr { display: grid; grid-template-columns: auto repeat(var(--cols, 3), 1fr); gap: 3px; font-family: var(--font-mono); font-size: 11px; }
.rr div { padding: 3px 4px; text-align: center; border-radius: 3px; font-variant-numeric: tabular-nums; }
.rr .h { color: var(--holistic); text-align: left; }
.rr .c { color: var(--conventional); }
.rr .cell { background: var(--surface-2); color: var(--ink); }
.rr .cell.hw { box-shadow: inset 0 -2px 0 var(--holistic); }
.rr .cell.cw { box-shadow: inset 0 -2px 0 var(--conventional); }
.rr .cell.na { color: var(--ink-3); }
.rr-note { font-size: 12px; color: var(--ink-3); }
details { border-top: 1px solid var(--line); padding-top: 10px; }
summary { cursor: pointer; color: var(--ink-2); font-size: 14px; }
.descs { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; margin-top: 12px; }
pre { margin: 0; font-family: var(--font-mono); font-size: 12px; line-height: 1.5; color: var(--ink-2); white-space: pre; overflow-x: auto; padding: 10px 12px; background: var(--surface-2); border-radius: 4px; }
pre b { color: var(--ink); font-weight: 500; }
@media (max-width: 760px) { .stage { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<main>
<header>
  <div class="eyebrow" id="eyebrow"></div>
  <h1 id="h1"></h1>
  <p id="lead"></p>
</header>

<section class="timeline" id="timeline">
  <div class="timeline-head">
    <div class="gen"><span id="stepWord">Generation</span> <b id="genLabel">0</b></div>
    <div class="nav"><button id="prev" type="button">Previous</button><button id="next" type="button">Next</button><span class="hint">or use the arrow keys, space to pause</span></div>
  </div>
  <div class="track"><svg id="curve" aria-hidden="true"></svg><input id="genSlider" type="range" min="0" max="0" step="1" value="0"></div>
  <div class="track-note" id="trackNote"></div>
</section>

<section class="stage">
  <div>
    <div class="viewport" id="view"><div class="fallback" id="fallback" hidden>three.js did not load. The replay needs network access to the CDN; the contender details on the right still work.</div></div>
    <div class="transport">
      <button id="play" type="button">Pause</button>
      <button id="reset" type="button">Restart</button>
      <label>Speed <select id="speed"><option>0.25</option><option>0.5</option><option selected>1</option><option>2</option><option>4</option></select></label>
      <input id="scrub" type="range" min="0" max="0" step="1" value="0" aria-label="Bout time">
      <span class="time mono" id="time">0.00 s</span>
    </div>
    <div class="scenehelp" id="sceneHelp"></div>
  </div>
  <div class="side">
    <div id="cards"></div>
    <div id="checkpoint"></div>
  </div>
</section>

<section id="wide"></section>

<dialog id="inspector">
  <div class="inspector-head">
    <div><div class="eyebrow" id="insp-eyebrow"></div><h2 id="insp-title"></h2></div>
    <button type="button" id="insp-close">Close</button>
  </div>
  <p class="insp-summary" id="insp-summary"></p>
  <div class="insp-legend">
    <span><i class="dot sensor"></i>sensor</span><span><i class="dot neuron"></i>neuron</span><span><i class="dot effector"></i>effector</span><span><i class="dot effector inert"></i>inert effector (root or fixed joint)</span>
    <span><i class="w pos"></i>positive weight</span><span><i class="w neg"></i>negative weight</span><span class="insp-hint">hover a unit to trace its links; width is |weight|</span>
  </div>
  <div class="insp-graph" id="insp-graph"><div class="insp-tip" id="insp-tip" hidden></div></div>
</dialog>

<details>
  <summary id="descSummary">Phenotype details</summary>
  <div class="descs" id="descs"></div>
</details>
</main>
<script src="__THREE__"></script>
<script>
__SCENE__
const DATA = __DATA__;
(function () {
  const $ = id => document.getElementById(id);
  const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const E = DATA.entries;
  const cfg = DATA.config;
  const COPY = DATA.copy;
  const ECO = DATA.mode === 'seasons';        // an ecology: seasons, not generations
  const GROUP = !!DATA.group;                 // one shared arena with food, not a duel
  const SEATS = E.length ? E[0].contenders.length : 2;
  $('h1').textContent = COPY.h1;
  $('lead').textContent = COPY.lead;
  $('trackNote').textContent = COPY.trackNote;
  $('sceneHelp').textContent = COPY.sceneHelp;
  $('stepWord').textContent = COPY.step;
  $('descSummary').textContent = 'Phenotype details for this ' + COPY.step.toLowerCase();
  $('timeline').setAttribute('aria-label', COPY.step);
  $('genSlider').setAttribute('aria-label', COPY.step);
  const bits = ['Rabbitstew', DATA.run, 'seed ' + cfg.seed];
  bits.push(ECO ? cfg.capacity + ' slots per fauna' : cfg.population_size + ' per population');
  if (ECO && cfg.challenge) bits.push(cfg.challenge + ' challenge');
  bits.push(cfg.duration + ' s ' + (GROUP ? 'seasons' : 'bouts'), E.length + ' ' + (ECO ? 'seasons' : 'generations') + ' shown');
  $('eyebrow').textContent = bits.join(' · ');

  // ---- replay ----------------------------------------------------------
  let replay = null, transport = null;
  // Seats alternate holistic / conventional, so seat i takes palette[i]: the two
  // fauna keep their colours and a second occupant of either is a distinct shade.
  const palette = () => [css('--holistic'), css('--conventional'), css('--holistic-2'), css('--conventional-2')];
  const themeFor = () => ({ background: css('--scene'), grid1: css('--scene-grid-1'), grid2: css('--scene-grid-2'), ring: css('--scene-ring'), ringVisible: !GROUP, food: css('--food'), palette: palette(), radius: GROUP ? 7 : 3.4, phi: 1.2 });
  if (typeof THREE !== 'undefined') {
    replay = new RabbitstewReplay($('view'), themeFor());
    transport = new RabbitstewTransport(replay, { play: $('play'), reset: $('reset'), scrub: $('scrub'), speed: $('speed'), time: $('time') });
    const mq = matchMedia('(prefers-color-scheme: dark)');
    (mq.addEventListener ? mq.addEventListener.bind(mq) : mq.addListener.bind(mq))('change', () => replay.setTheme(themeFor()));
    new MutationObserver(() => replay.setTheme(themeFor())).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  } else {
    $('fallback').hidden = false;
  }

  // ---- champion curve behind the slider ---------------------------------
  const svg = $('curve'), NS = 'http://www.w3.org/2000/svg';
  const W = 1000, H = 92, padL = 8, padR = 8, top = 6, bottom = 30;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('preserveAspectRatio', 'none');
  const g0 = E[0].gen, g1 = E[E.length - 1].gen;
  const sx = g => padL + (g1 === g0 ? 0.5 : (g - g0) / (g1 - g0)) * (W - padL - padR);
  // A duel's fitness is already a share of one; an ecology's score is energy, so its
  // axis is scaled to the run (and reaches below zero when work costs more than food).
  const dot = e => GROUP ? Math.max.apply(null, e.bout.score) : e.bout.fitness[0];
  const vals = ECO ? DATA.curve.map(p => p.holistic).concat(DATA.curve.map(p => p.conventional), E.map(dot)) : [0, 1];
  const vlo = Math.min.apply(null, vals.concat(ECO ? [0] : [])), vhi = Math.max.apply(null, vals);
  const span = Math.max(vhi - vlo, 1e-6);
  const sy = v => top + (1 - (v - vlo) / span) * (H - top - bottom);
  const add = (n, a) => { const e = document.createElementNS(NS, n); for (const k in a) e.setAttribute(k, a[k]); svg.appendChild(e); return e; };
  const rule = (v, dash) => add('line', { x1: padL, x2: W - padR, y1: sy(v), y2: sy(v), stroke: css('--parity'), 'stroke-dasharray': dash, 'stroke-width': 1, 'vector-effect': 'non-scaling-stroke' });
  rule(ECO ? 0 : 0.5, ECO ? '2 4' : '4 4');   // parity in a duel, the break-even line in an ecology
  const line = (key, colour) => { if (DATA.curve.length > 1) add('path', { d: DATA.curve.map((p, i) => (i ? 'L' : 'M') + sx(p.gen) + ',' + sy(p[key])).join(' '), fill: 'none', stroke: colour, 'stroke-width': 1.5, 'vector-effect': 'non-scaling-stroke' }); };
  if (ECO) { line('holistic', css('--holistic')); line('conventional', css('--conventional')); } else line('mean', css('--holistic'));
  for (const e of E) add('circle', { cx: sx(e.gen), cy: sy(dot(e)), r: 2.2, fill: palette()[e.bout.winner % 4], opacity: 0.85 });
  const marker = add('line', { x1: 0, x2: 0, y1: top - 2, y2: H - bottom + 4, stroke: css('--ink'), 'stroke-width': 1.5, 'vector-effect': 'non-scaling-stroke' });

  // ---- one persistent card per seat, each with its own small viewer -------
  // Two seats sit beside the arena; a group arena's cards go in a row under it, where
  // there is room for four without pushing the ecology panel off the screen.
  const cards = [], minis = [];
  if (SEATS > 2) $('wide').appendChild($('cards'));
  for (let i = 0; i < SEATS; i++) {
    const card = el('div', 'card'), mini = el('div', 'mini');
    const who = el('div', 'who'), kind = el('span', 'kind'), swatch = el('i', 'swatch'), kindText = el('span'), name = el('span', 'name');
    kind.append(swatch, kindText); who.append(kind, name);
    const result = el('div', 'result'), fit = el('span', 'fit'), sub = el('span', 'dist'), badge = el('span', 'badge');
    result.append(fit, sub, badge);
    const facts = el('div', 'facts'), actions = el('div', 'actions'), inspect = el('button', null, 'Inspect brain');
    inspect.type = 'button';
    inspect.addEventListener('click', () => openInspector(E[idx], i));
    actions.append(inspect, el('span', 'minihelp', 'drag the model to rotate it'));
    card.append(mini, who, result, facts, actions);
    $('cards').appendChild(card);
    cards.push({ card, mini, swatch, kindText, name, fit, sub, badge, facts });
  }
  if (replay) {
    for (let i = 0; i < SEATS; i++) {
      const m = new RabbitstewReplay(cards[i].mini, Object.assign(themeFor(), { gridSize: 4, ringVisible: false, radius: 3.4, phi: 1.15, theta: 0.6 }));
      minis.push(m);
    }
    (function idle() { for (const m of minis) m.spin(0.006); requestAnimationFrame(idle); })();
    const retheme = () => { replay.setTheme(themeFor()); for (const m of minis) m.setTheme(Object.assign(themeFor(), { gridSize: 4, ringVisible: false })); for (let i = 0; i < cards.length; i++) paintCard(i); };
    const mq2 = matchMedia('(prefers-color-scheme: dark)');
    (mq2.addEventListener ? mq2.addEventListener.bind(mq2) : mq2.addListener.bind(mq2))('change', retheme);
    new MutationObserver(retheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  }
  function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }
  function paintCard(i) {
    const colour = palette()[i % 4];
    cards[i].card.style.borderLeftColor = colour;
    cards[i].swatch.style.background = colour;
  }
  function fillCard(entry, i) {
    const c = entry.contenders[i], b = entry.bout, k = cards[i];
    paintCard(i);
    k.kindText.textContent = c.label || (c.kind === 'holistic' ? 'Holistic best' : 'Conventional best');
    k.name.textContent = c.name;
    if (GROUP) {
      k.fit.textContent = b.food[i].toFixed(0);
      k.sub.textContent = 'items eaten · net score ' + b.score[i].toFixed(2);
      k.badge.className = 'badge ' + (b.exploded[i] ? 'exploded' : 'win');
      k.badge.textContent = b.exploded[i] ? 'unstable' : b.winner === i ? 'best forager' : '';
    } else {
      k.fit.textContent = b.fitness[i].toFixed(3);
      k.sub.textContent = 'fitness · ' + b.distances[i].toFixed(2) + ' m from centre';
      k.badge.className = 'badge ' + (b.exploded[i] ? 'exploded' : b.winner === i ? 'win' : 'lose');
      k.badge.textContent = b.exploded[i] ? 'unstable' : b.winner === i ? 'winner' : 'lost';
    }
    k.badge.hidden = !k.badge.textContent;
    k.facts.replaceChildren();
    const fact = (key, v) => { const s = el('span'); s.append(document.createTextNode(key + ' ')); s.appendChild(el('b', null, v)); k.facts.appendChild(s); };
    fact('parts', c.parts + (c.truncated ? '*' : '') + ' from ' + c.nodes + ' nodes'); fact('mass', c.mass + ' kg');
    fact('neural units', c.units); fact('links', c.links);
    fact('live effectors', c.live_effectors);
    if (GROUP) { fact('work', b.work[i].toFixed(2) + ' kJ'); fact('moved', b.moved[i].toFixed(2) + ' m'); }
    const st = entry.stats[c.kind]; if (st) fact(ECO ? 'best / mean lifetime' : 'best / mean in pop.', st.best.toFixed(2) + ' / ' + st.mean.toFixed(2));
    if (minis[i]) { c.rest.units.forEach(u => { u.robot = i; }); minis[i].load(c.rest); minis[i].frameContent(2.4); }
  }
  const ECO_ROWS = [['alive', 'alive'], ['births', 'births'], ['deaths', 'deaths'], ['mean_age', 'mean age'], ['max_age', 'oldest'], ['living_cost', 'living cost'], ['total_energy', 'total energy'], ['capacity', 'slots']];
  function ecology(entry, host) {
    const e = entry.eco; if (!e) return false;
    const root = el('div', 'checkpoint');
    root.appendChild(el('h3', null, 'The ecology in season ' + entry.gen));
    const grid = el('div', 'eco');
    grid.append(el('div', 'hd', ''), el('div', 'hd h num', 'holistic'), el('div', 'hd c num', 'conventional'));
    const fmt = v => v === null || v === undefined ? '–' : (Math.round(v) === v ? String(v) : v.toFixed(2));
    for (const [key, label] of ECO_ROWS) {
      grid.appendChild(el('div', null, label));
      for (const kind of ['holistic', 'conventional']) {
        const cell = el('div', 'num'); cell.appendChild(el('b', null, fmt((e[kind] || {})[key]))); grid.appendChild(cell);
      }
    }
    root.appendChild(grid);
    const merged = Object.keys(e).some(k => e[k].merged);
    root.appendChild(el('div', 'rr-note', merged
      ? 'The two fauna share one arena and one pooled capacity from here on: a slot freed by either is open to the next breeder of either.'
      : 'Nobody is culled by rank. A slot opens only when an individual starves or dies of age, and only then can a breeder spend energy on a child.'));
    if (GROUP) {
      const key = el('div', 'rr-note');
      const dot = el('span', 'food-key'); dot.append(el('i'), document.createTextNode('food'));
      key.append(dot, document.createTextNode(' · ' + entry.contenders.length + ' seats in one arena, filled by the two champions of the season, twice over.'));
      root.appendChild(key);
    }
    host.appendChild(root);
    return true;
  }
  function checkpoint(entry) {
    const host = $('checkpoint'); host.replaceChildren();
    const cp = entry.checkpoint; if (!cp) { ecology(entry, host); return; }
    const root = el('div', 'checkpoint');
    root.appendChild(el('h3', null, 'Checkpoint: champions of generation ' + entry.gen));
    const sum = el('div', 'sum');
    sum.append(document.createTextNode('Holistic mean fitness '), el('b', null, cp.mean.toFixed(3)), document.createTextNode(' over ' + cp.n + ' bouts, '), el('b', null, cp.wins + '–' + cp.losses), document.createTextNode(' wins'));
    root.appendChild(sum);
    if (cp.mode === 'roundrobin') {
      const hs = [...new Set(cp.bouts.map(b => b.h))], cs = [...new Set(cp.bouts.map(b => b.c))];
      const grid = el('div', 'rr'); grid.style.setProperty('--cols', cs.length);
      grid.appendChild(el('div', null, ''));
      for (const c of cs) grid.appendChild(el('div', 'c', c));
      for (const h of hs) {
        grid.appendChild(el('div', 'h', h));
        for (const c of cs) {
          const fs = cp.bouts.filter(b => b.h === h && b.c === c).map(b => b.f);
          const m = fs.length ? fs.reduce((a, b) => a + b, 0) / fs.length : null;
          const cell = el('div', 'cell' + (m === null ? ' na' : m > 0.5 ? ' hw' : m < 0.5 ? ' cw' : ''), m === null ? '–' : m.toFixed(2));
          cell.title = fs.length ? 'both sides: ' + fs.map(f => f.toFixed(3)).join(' / ') : '';
          grid.appendChild(cell);
        }
      }
      root.appendChild(grid);
      root.appendChild(el('div', 'rr-note', 'Holistic fitness per pair, averaged over both starting sides; underlined by the side that won the pair.'));
    }
    host.appendChild(root);
  }

  // ---- neural network inspector --------------------------------------------
  const dialog = $('inspector');
  $('insp-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
  function openInspector(entry, i) {
    const c = entry.contenders[i], net = c.net;
    $('insp-eyebrow').textContent = (c.label || (c.kind === 'holistic' ? 'Holistic best' : 'Conventional best')) + ' · ' + COPY.step.toLowerCase() + ' ' + entry.gen;
    $('insp-title').textContent = c.name + ': controller';
    const nS = net.units.filter(u => u.kind === 's').length, nN = net.units.filter(u => u.kind === 'n').length, nE = net.units.filter(u => u.kind === 'e').length;
    const linked = new Set(); for (const [a, b] of net.links) { linked.add(a); linked.add(b); }
    $('insp-summary').textContent = `${nS} sensors, ${nN} neurons and ${nE} effectors (${c.live_effectors} on live joints) in ${net.parts.length} body parts` + (net.global ? ' plus a global brain' : '') + `, joined by ${net.links.length} links. ${net.units.length - linked.size} units have no links at all.`;
    drawNetwork($('insp-graph'), net);
    if (typeof dialog.showModal === 'function') dialog.showModal(); else dialog.setAttribute('open', '');
  }

  function drawNetwork(host, net) {
    const keep = $('insp-tip'); host.replaceChildren(keep);
    const NS = 'http://www.w3.org/2000/svg';
    const rows = net.parts.map(p => ({ key: p.index, label: `part ${p.index} · ${p.shape} · ${p.joint}`, units: [] }));
    if (net.global) rows.push({ key: null, label: 'global brain', units: [] });
    const rowOf = new Map(rows.map((r, k) => [r.key, k]));
    net.units.forEach((u, i) => rows[rowOf.get(u.part)].units.push(i));
    const colX = { s: 300, n: 560, e: 800 }, W = 980, rowGap = 14, unitGap = 20, padTop = 28;
    const pos = new Array(net.units.length); let y = padTop; const bands = [];
    for (const r of rows) {
      const groups = { s: [], n: [], e: [] };
      for (const i of r.units) groups[net.units[i].kind].push(i);
      const height = Math.max(1, groups.s.length, groups.n.length, groups.e.length) * unitGap;
      for (const k of ['s', 'n', 'e']) groups[k].forEach((i, j) => { pos[i] = { x: colX[k], y: y + (j + 0.5) * unitGap + (height - groups[k].length * unitGap) / 2 }; });
      bands.push({ y, height, label: r.label });
      y += height + rowGap;
    }
    const H = y + 6;
    const svg = document.createElementNS(NS, 'svg'); svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('width', W); svg.setAttribute('height', H); host.appendChild(svg);
    const add = (n, a, parent) => { const e = document.createElementNS(NS, n); for (const k in a) e.setAttribute(k, a[k]); (parent || svg).appendChild(e); return e; };
    bands.forEach((b, k) => {
      if (k % 2 === 1) add('rect', { x: 0, y: b.y - rowGap / 2, width: W, height: b.height + rowGap, fill: css('--surface'), opacity: 0.5 });
      const t = add('text', { x: 8, y: b.y + 12, class: 'row' }); t.textContent = b.label;
    });
    for (const [k, label] of [['s', 'sensors'], ['n', 'neurons'], ['e', 'effectors']]) { const t = add('text', { x: colX[k], y: 14, 'text-anchor': 'middle', class: 'row' }); t.textContent = label; }
    const linkEls = net.links.map(([a, b, w]) => {
      const p = pos[a], q = pos[b];
      let d;
      if (Math.abs(p.x - q.x) < 1) { const bulge = 24 + Math.abs(p.y - q.y) * 0.15; d = `M${p.x},${p.y} C${p.x + bulge},${p.y} ${q.x + bulge},${q.y} ${q.x},${q.y}`; }
      else { const mx = (p.x + q.x) / 2; d = `M${p.x},${p.y} C${mx},${p.y} ${mx},${q.y} ${q.x},${q.y}`; }
      const e = add('path', { d, class: 'link', stroke: css(w >= 0 ? '--w-pos' : '--w-neg'), 'stroke-width': (0.6 + 2.4 * Math.min(Math.abs(w), 3) / 3).toFixed(2) });
      e.dataset.a = a; e.dataset.b = b; return e;
    });
    const tip = $('insp-tip');
    const unitEls = net.units.map((u, i) => {
      const p = pos[i], g = add('g', { class: 'unit', transform: `translate(${p.x},${p.y})` });
      const inert = u.kind === 'e' && !u.live;
      add('circle', { r: 6, fill: inert ? 'none' : css(u.kind === 's' ? '--unit-sensor' : u.kind === 'n' ? '--unit-neuron' : '--unit-effector'), stroke: inert ? css('--unit-effector') : css('--surface'), 'stroke-width': inert ? 2 : 1.5 }, g);
      const t = add('text', { x: u.kind === 'e' ? 10 : u.kind === 's' ? -10 : 0, y: u.kind === 'n' ? -9 : 3, 'text-anchor': u.kind === 'e' ? 'start' : u.kind === 's' ? 'end' : 'middle' }, g);
      t.textContent = u.kind === 'n' ? (u.label === 'tanh' ? '' : u.label) : u.label;
      add('circle', { r: 11, fill: 'transparent' }, g); // hit target
      g.addEventListener('pointerenter', e => {
        const ins = net.links.filter(l => l[1] === i), outs = net.links.filter(l => l[0] === i);
        linkEls.forEach(le => { const on = +le.dataset.a === i || +le.dataset.b === i; le.classList.toggle('lit', on); le.classList.toggle('dim', !on); });
        const touched = new Set([i]); for (const l of ins) touched.add(l[0]); for (const l of outs) touched.add(l[1]);
        unitEls.forEach((ue, j) => ue.classList.toggle('dim', !touched.has(j)));
        tip.replaceChildren();
        const head = el('div'); head.appendChild(el('b', null, `#${i} ${u.label}`)); head.append(document.createTextNode(u.part === null ? ' · global' : ` · part ${u.part}`)); tip.appendChild(head);
        if (u.kind !== 's') { const bl = el('div'); bl.append('bias ', el('b', null, u.bias.toFixed(2))); tip.appendChild(bl); }
        if (u.kind === 'e') { const jl = el('div'); jl.append(u.live ? `drives its ${u.joint} joint` : `inert: ${u.joint === 'root' ? 'the root has no parent joint' : 'fixed joint'}`); tip.appendChild(jl); }
        const io = el('div'); io.append(el('b', null, ins.length), ' in · ', el('b', null, outs.length), ' out'); tip.appendChild(io);
        for (const l of ins.slice(0, 8)) { const r = el('div'); r.append('← #' + l[0] + ' ', el('b', null, (l[2] >= 0 ? '+' : '') + l[2].toFixed(2))); tip.appendChild(r); }
        if (ins.length > 8) tip.appendChild(el('div', null, '… ' + (ins.length - 8) + ' more inputs'));
        tip.hidden = false;
        const hr = host.getBoundingClientRect();
        tip.style.left = (e.clientX - hr.left + host.scrollLeft + 14) + 'px'; tip.style.top = (e.clientY - hr.top + host.scrollTop + 10) + 'px';
      });
      g.addEventListener('pointerleave', () => { linkEls.forEach(le => le.classList.remove('lit', 'dim')); unitEls.forEach(ue => ue.classList.remove('dim')); tip.hidden = true; });
      return g;
    });
  }

  // ---- generation selection ------------------------------------------------
  const slider = $('genSlider'); slider.max = E.length - 1;
  let idx = -1;
  function show(i, keepPlaying) {
    i = Math.min(Math.max(0, i), E.length - 1); if (i === idx) return; idx = i;
    const entry = E[i];
    slider.value = i; $('genLabel').textContent = entry.gen;
    marker.setAttribute('x1', sx(entry.gen)); marker.setAttribute('x2', sx(entry.gen));
    for (let k = 0; k < cards.length; k++) fillCard(entry, k);
    checkpoint(entry);
    const descs = $('descs'); descs.replaceChildren();
    for (const c of entry.contenders.slice(0, 2)) { const pre = el('pre'); pre.appendChild(el('b', null, (c.kind === 'holistic' ? 'Holistic best ' : 'Conventional best ') + c.name + '\\n')); pre.appendChild(document.createTextNode(c.description)); descs.appendChild(pre); }
    if (replay) { replay.load(entry.traj); transport.reload(); if (keepPlaying !== false) transport.toggle(true); }
  }
  slider.addEventListener('input', () => show(+slider.value));
  $('prev').addEventListener('click', () => show(idx - 1));
  $('next').addEventListener('click', () => show(idx + 1));
  addEventListener('keydown', e => {
    if (e.target.tagName === 'SELECT' || e.target.tagName === 'INPUT') return;
    if (e.key === 'ArrowLeft') { show(idx - 1); e.preventDefault(); }
    else if (e.key === 'ArrowRight') { show(idx + 1); e.preventDefault(); }
    else if (e.key === ' ' && transport) { transport.toggle(); e.preventDefault(); }
  });
  show(E.length - 1);
})();
</script>
</body>
</html>
"""
