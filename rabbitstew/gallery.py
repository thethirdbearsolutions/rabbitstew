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
from .simulation import SimConfig, run_bout
from .synthesis import describe, synthesize
from .visualizer import SCENE_JS, THREE_JS_URL


def _contender(kind: str, g: Genotype, sim: SimConfig) -> dict:
    ph = synthesize(g, sim.synthesis)
    return {
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
            "traj": {"dt": traj.dt, "units": [{"shape": int(u.shape), "dims": [round(float(d), 4) for d in u.dims], "robot": traj.robot_of_unit(i)} for i, u in enumerate(traj.units)], "frames": frames.tolist()},
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
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --surface: #1a1b1e; --surface-2: #232428; --line: #35363b; --grid: #2b2c31;
  --ink: #f2f2ee; --ink-2: #c2c2bb; --ink-3: #8c8d92;
  --holistic: #3987e5; --conventional: #d95926; --parity: #8d8e90;
  --scene: #202124; --scene-grid-1: #55565c; --scene-grid-2: #303136; --scene-ring: #f2f2ee;
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
  <div class="side" id="side"></div>
</section>

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

  // ---- side panel ---------------------------------------------------------
  function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }
  function card(entry, i) {
    const c = entry.contenders[i], b = entry.bout;
    const root = el('div', 'card ' + c.kind);
    const who = el('div', 'who'); who.append(el('span', 'kind', c.kind === 'holistic' ? 'Holistic best' : 'Conventional best'), el('span', 'name', c.name)); root.appendChild(who);
    const res = el('div', 'result');
    res.append(el('span', 'fit', b.fitness[i].toFixed(3)));
    const d = el('span', 'dist'); d.textContent = 'fitness · ' + b.distances[i].toFixed(2) + ' m from centre'; res.appendChild(d);
    const badge = b.exploded[i] ? el('span', 'badge exploded', 'unstable') : el('span', 'badge ' + (b.winner === i ? 'win' : 'lose'), b.winner === i ? 'winner' : 'lost');
    res.appendChild(badge); root.appendChild(res);
    const facts = el('div', 'facts');
    const fact = (k, v) => { const s = el('span'); s.append(document.createTextNode(k + ' ')); s.appendChild(el('b', null, v)); facts.appendChild(s); };
    fact('parts', c.parts + (c.truncated ? '*' : '') + ' from ' + c.nodes + ' nodes'); fact('mass', c.mass + ' kg'); fact('neural units', c.units); fact('links', c.links);
    const st = entry.stats[c.kind]; if (st) { fact('best in pop.', st.best.toFixed(3)); fact('mean in pop.', st.mean.toFixed(3)); }
    root.appendChild(facts);
    return root;
  }
  function checkpoint(entry) {
    const cp = entry.checkpoint; if (!cp) return null;
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
    return root;
  }

  // ---- generation selection ------------------------------------------------
  const slider = $('genSlider'); slider.max = E.length - 1;
  let idx = -1;
  function show(i, keepPlaying) {
    i = Math.min(Math.max(0, i), E.length - 1); if (i === idx) return; idx = i;
    const entry = E[i];
    slider.value = i; $('genLabel').textContent = entry.gen;
    marker.setAttribute('x1', sx(entry.gen)); marker.setAttribute('x2', sx(entry.gen));
    const side = $('side'); side.replaceChildren(card(entry, 0), card(entry, 1));
    const cp = checkpoint(entry); if (cp) side.appendChild(cp);
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
