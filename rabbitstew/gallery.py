"""Bout gallery: one page, one slider, every generation's champion bout.

:func:`build_gallery` reads an experiment directory written by
:class:`~rabbitstew.evolution.Experiment`, re-simulates the bout between the
best holistic and the best conventional genotype of every generation (bouts
are deterministic, so nothing needs to be stored during evolution) and
writes a single self-contained HTML page.  The page has a generation slider
drawn over the champion curve, a 3-D replay of the selected bout, cards for
the two contenders, and the round-robin results of the checkpoint when the
generation was one.
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
from .simulation import SimConfig, run_bout
from .synthesis import Phenotype, describe, synthesize
from .visualizer import SCENE_JS, THREE_JS_URL, scenery_payload
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


def build_gallery(
    run_dir: str,
    out_path: str,
    every: int = 1,
    record_every: int = 4,
    title: Optional[str] = None,
    log: Optional[Callable[[str], None]] = print,
) -> dict:
    """Re-simulate the best-versus-best bout of every ``every``-th generation and write the page.

    Returns a summary dict with the number of generations rendered and the
    output size in bytes.
    """
    log = log or (lambda s: None)
    with open(os.path.join(run_dir, "config.json")) as f:
        config = json.load(f)
    with open(os.path.join(run_dir, "history.json")) as f:
        history = json.load(f)
    sim = SimConfig.from_dict(config["sim"])
    sim.record_every = max(1, record_every)

    by_gen: dict[int, dict] = {}
    for e in history["history"]:
        by_gen.setdefault(e["generation"], {})[e["population"]] = e
    checkpoints = {c["generation"]: c for c in history["champions"]}
    gens = sorted(by_gen)
    selected = [g for i, g in enumerate(gens) if i % max(1, every) == 0]
    if gens and gens[-1] not in selected:
        selected.append(gens[-1])

    entries = []
    for gen in selected:
        h_path = os.path.join(run_dir, HOLISTIC, f"best_gen{gen:04d}.json")
        c_path = os.path.join(run_dir, CONVENTIONAL, f"best_gen{gen:04d}.json")
        if not (os.path.exists(h_path) and os.path.exists(c_path)):
            log(f"gen {gen}: best genotypes missing, skipped")
            continue
        h, c = Genotype.load(h_path), Genotype.load(c_path)
        res = run_bout(h, c, sim, record=True)
        traj = res.trajectory
        frames = np.round(traj.as_array(), 3)
        entry = {
            "gen": gen,
            "contenders": [_contender(HOLISTIC, h, sim), _contender(CONVENTIONAL, c, sim)],
            "bout": {"distances": [round(d, 3) for d in res.distances], "fitness": [round(f, 3) for f in res.fitness], "exploded": res.exploded, "winner": res.winner},
            "stats": {k: {"best": round(v["best_fitness"], 3), "mean": round(v["mean_fitness"], 3)} for k, v in by_gen[gen].items()},
            "traj": {"dt": traj.dt, "units": [{"shape": int(u.shape), "dims": [round(float(d), 4) for d in u.dims], "robot": traj.robot_of_unit(i)} for i, u in enumerate(traj.units)], "frames": frames.tolist(), "scenery": scenery_payload(traj)},
        }
        cp = checkpoints.get(gen)
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
        log(f"gen {gen}: {h.name} vs {c.name}: fitness {res.fitness[0]:.3f} / {res.fitness[1]:.3f}, {traj.n_frames} frames")

    curve = [{"gen": c["generation"], "mean": round(c["holistic_mean_fitness"], 3)} for c in history["champions"]]
    payload = {
        "run": os.path.basename(os.path.normpath(run_dir)),
        "config": {"seed": config.get("seed"), "population_size": config.get("population_size"), "generations": config.get("generations"), "duration": sim.duration, "champions": config.get("champions"), "champion_mode": config.get("champion_mode")},
        "curve": curve,
        "entries": entries,
    }
    data = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    html = _TEMPLATE.replace("__TITLE__", title or f"Rabbitstew bouts, {payload['run']}").replace("__THREE__", THREE_JS_URL).replace("__SCENE__", SCENE_JS).replace("__DATA__", data)
    with open(out_path, "w") as f:
        f.write(html)
    size = os.path.getsize(out_path)
    log(f"wrote {out_path}: {len(entries)} generations, {size / 1e6:.1f} MB")
    return {"generations": len(entries), "bytes": size}


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
    --scene: #202124; --scene-grid-1: #55565c; --scene-grid-2: #303136; --scene-ring: #f2f2ee;
    --unit-sensor: #199e70; --unit-neuron: #9085e9; --unit-effector: #c98500; --w-pos: #3987e5; --w-neg: #e66767;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --surface: #1a1b1e; --surface-2: #232428; --line: #35363b; --grid: #2b2c31;
  --ink: #f2f2ee; --ink-2: #c2c2bb; --ink-3: #8c8d92;
  --holistic: #3987e5; --conventional: #d95926; --parity: #8d8e90;
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

.side { display: grid; gap: 14px; }
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
.card.holistic { border-left: 4px solid var(--holistic); }
.card.conventional { border-left: 4px solid var(--conventional); }
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
  <h1>Champion bouts, generation by generation</h1>
  <p>Each generation's best holistic creature (blue) meets the best fixed-body Pioneer (orange) in the arena. Bouts are re-simulated from the saved genotypes, so the replay is exactly the physics the experiment ran. Slide through the run to watch what evolution came up with.</p>
</header>

<section class="timeline" aria-label="Generation">
  <div class="timeline-head">
    <div class="gen">Generation <b id="genLabel">0</b></div>
    <div class="nav"><button id="prev" type="button">Previous</button><button id="next" type="button">Next</button><span class="hint">or use the arrow keys, space to pause</span></div>
  </div>
  <div class="track"><svg id="curve" aria-hidden="true"></svg><input id="genSlider" type="range" min="0" max="0" step="1" value="0" aria-label="Generation"></div>
  <div class="track-note">Line: holistic mean fitness at each round-robin checkpoint. Dots: this generation's replayed best-versus-best bout, coloured by the winner. Dashed: parity.</div>
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
    <div class="scenehelp">Drag to orbit, wheel to zoom, right-drag to pan. The white ring marks the centre both robots are racing for.</div>
  </div>
  <div class="side">
    <div class="card holistic" id="card0">
      <div class="mini" id="mini0"></div>
      <div class="who"><span class="kind">Holistic best</span><span class="name" id="name0"></span></div>
      <div class="result"><span class="fit" id="fit0"></span><span class="dist" id="dist0"></span><span class="badge" id="badge0"></span></div>
      <div class="facts" id="facts0"></div>
      <div class="actions"><button type="button" id="inspect0">Inspect brain</button><span class="minihelp">drag the model to rotate it</span></div>
    </div>
    <div class="card conventional" id="card1">
      <div class="mini" id="mini1"></div>
      <div class="who"><span class="kind">Conventional best</span><span class="name" id="name1"></span></div>
      <div class="result"><span class="fit" id="fit1"></span><span class="dist" id="dist1"></span><span class="badge" id="badge1"></span></div>
      <div class="facts" id="facts1"></div>
      <div class="actions"><button type="button" id="inspect1">Inspect brain</button><span class="minihelp">drag the model to rotate it</span></div>
    </div>
    <div id="checkpoint"></div>
  </div>
</section>

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
  <summary>Phenotype details for this generation</summary>
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
  $('eyebrow').textContent = `Rabbitstew · ${DATA.run} · seed ${cfg.seed} · ${cfg.population_size} per population · ${cfg.duration} s bouts · ${E.length} generations`;

  // ---- replay ----------------------------------------------------------
  let replay = null, transport = null;
  const themeFor = () => ({ background: css('--scene'), grid1: css('--scene-grid-1'), grid2: css('--scene-grid-2'), ring: css('--scene-ring'), palette: [css('--holistic'), css('--conventional')], radius: 3.4, phi: 1.2 });
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
  const sy = v => top + (1 - v) * (H - top - bottom);
  const add = (n, a) => { const e = document.createElementNS(NS, n); for (const k in a) e.setAttribute(k, a[k]); svg.appendChild(e); return e; };
  add('line', { x1: padL, x2: W - padR, y1: sy(0.5), y2: sy(0.5), stroke: css('--parity'), 'stroke-dasharray': '4 4', 'stroke-width': 1, 'vector-effect': 'non-scaling-stroke' });
  if (DATA.curve.length > 1) add('path', { d: DATA.curve.map((p, i) => (i ? 'L' : 'M') + sx(p.gen) + ',' + sy(p.mean)).join(' '), fill: 'none', stroke: css('--holistic'), 'stroke-width': 1.5, 'vector-effect': 'non-scaling-stroke' });
  for (const e of E) add('circle', { cx: sx(e.gen), cy: sy(e.bout.fitness[0]), r: 2.2, fill: e.bout.winner === 0 ? css('--holistic') : css('--conventional'), opacity: 0.85 });
  const marker = add('line', { x1: 0, x2: 0, y1: top - 2, y2: H - bottom + 4, stroke: css('--ink'), 'stroke-width': 1.5, 'vector-effect': 'non-scaling-stroke' });

  // ---- side panel: two persistent cards, each with its own small viewer -------
  const minis = [];
  if (replay) {
    for (let i = 0; i < 2; i++) {
      const m = new RabbitstewReplay($('mini' + i), Object.assign(themeFor(), { gridSize: 4, ringVisible: false, phi: 1.15, theta: 0.6 }));
      minis.push(m);
    }
    (function idle() { for (const m of minis) m.spin(0.006); requestAnimationFrame(idle); })();
    const retheme = () => { replay.setTheme(themeFor()); for (const m of minis) m.setTheme(Object.assign(themeFor(), { gridSize: 4, ringVisible: false })); };
    const mq2 = matchMedia('(prefers-color-scheme: dark)');
    (mq2.addEventListener ? mq2.addEventListener.bind(mq2) : mq2.addListener.bind(mq2))('change', retheme);
    new MutationObserver(retheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  }
  function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }
  function fillCard(entry, i) {
    const c = entry.contenders[i], b = entry.bout;
    $('name' + i).textContent = c.name;
    $('fit' + i).textContent = b.fitness[i].toFixed(3);
    $('dist' + i).textContent = 'fitness · ' + b.distances[i].toFixed(2) + ' m from centre';
    const badge = $('badge' + i);
    badge.className = 'badge ' + (b.exploded[i] ? 'exploded' : b.winner === i ? 'win' : 'lose');
    badge.textContent = b.exploded[i] ? 'unstable' : b.winner === i ? 'winner' : 'lost';
    const facts = $('facts' + i); facts.replaceChildren();
    const fact = (k, v) => { const s = el('span'); s.append(document.createTextNode(k + ' ')); s.appendChild(el('b', null, v)); facts.appendChild(s); };
    fact('parts', c.parts + (c.truncated ? '*' : '') + ' from ' + c.nodes + ' nodes'); fact('mass', c.mass + ' kg');
    fact('neural units', c.units); fact('links', c.links);
    fact('live effectors', c.live_effectors);
    const st = entry.stats[c.kind]; if (st) fact('best / mean in pop.', st.best.toFixed(2) + ' / ' + st.mean.toFixed(2));
    if (minis[i]) { c.rest.units.forEach(u => { u.robot = i; }); minis[i].load(c.rest); minis[i].frameContent(2.4); }
  }
  function checkpoint(entry) {
    const host = $('checkpoint'); host.replaceChildren();
    const cp = entry.checkpoint; if (!cp) return;
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
    $('insp-eyebrow').textContent = (c.kind === 'holistic' ? 'Holistic best' : 'Conventional best') + ' · generation ' + entry.gen;
    $('insp-title').textContent = c.name + ': controller';
    const nS = net.units.filter(u => u.kind === 's').length, nN = net.units.filter(u => u.kind === 'n').length, nE = net.units.filter(u => u.kind === 'e').length;
    const linked = new Set(); for (const [a, b] of net.links) { linked.add(a); linked.add(b); }
    $('insp-summary').textContent = `${nS} sensors, ${nN} neurons and ${nE} effectors (${c.live_effectors} on live joints) in ${net.parts.length} body parts` + (net.global ? ' plus a global brain' : '') + `, joined by ${net.links.length} links. ${net.units.length - linked.size} units have no links at all.`;
    drawNetwork($('insp-graph'), net);
    if (typeof dialog.showModal === 'function') dialog.showModal(); else dialog.setAttribute('open', '');
  }
  $('inspect0').addEventListener('click', () => openInspector(E[idx], 0));
  $('inspect1').addEventListener('click', () => openInspector(E[idx], 1));

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
    fillCard(entry, 0); fillCard(entry, 1); checkpoint(entry);
    const descs = $('descs'); descs.replaceChildren();
    for (const c of entry.contenders) { const pre = el('pre'); pre.appendChild(el('b', null, (c.kind === 'holistic' ? 'Holistic best ' : 'Conventional best ') + c.name + '\\n')); pre.appendChild(document.createTextNode(c.description)); descs.appendChild(pre); }
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
