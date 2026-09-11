"""Experiment report: the champion curve and within-population statistics as one HTML page.

``build_report`` accepts one or more experiment directories.  With a single
run it draws that run's champion curve with the spread of individual bouts;
with several (different seeds of the same configuration) it draws each seed
as a thin line and the across-seed mean as the emphasised one, so a claim
about holistic versus conventional evolution rests on more than one random
start.
"""

from __future__ import annotations

import json
import os
from typing import Optional

import numpy as np


def _load(run_dir: str) -> dict:
    with open(os.path.join(run_dir, "history.json")) as f:
        hist = json.load(f)
    with open(os.path.join(run_dir, "config.json")) as f:
        cfg = json.load(f)
    champ = []
    for c in hist["champions"]:
        f = [b["holistic_fitness"] for b in c["bouts"]]
        champ.append({"gen": c["generation"], "mean": round(c["holistic_mean_fitness"], 4), "lo": round(min(f), 4), "hi": round(max(f), 4), "wins": c["holistic_wins"], "losses": c["conventional_wins"], "n": c["n_bouts"]})
    pops: dict = {"holistic": [], "conventional": []}
    for e in hist["history"]:
        pops[e["population"]].append({k: (round(v, 4) if isinstance(v, float) else v) for k, v in e.items() if k != "population"})
    return {"name": os.path.basename(os.path.normpath(run_dir)), "seed": cfg.get("seed"), "config": cfg, "champ": champ, "pops": pops}


def summarize(run_dirs: list[str]) -> dict:
    """Load runs and compute the across-seed mean champion curve (on the generations all runs share)."""
    runs = [_load(d) for d in run_dirs]
    if not runs:
        raise ValueError("no runs given")
    shared = None
    for r in runs:
        gens = {c["gen"] for c in r["champ"]}
        shared = gens if shared is None else shared & gens
    mean_curve = []
    for g in sorted(shared or []):
        vals = [next(c["mean"] for c in r["champ"] if c["gen"] == g) for r in runs]
        mean_curve.append({"gen": g, "mean": round(float(np.mean(vals)), 4), "lo": round(float(min(vals)), 4), "hi": round(float(max(vals)), 4)})
    totals = {"wins": sum(c["wins"] for r in runs for c in r["champ"]), "losses": sum(c["losses"] for r in runs for c in r["champ"]), "n": sum(c["n"] for r in runs for c in r["champ"])}
    # Split the run into thirds to see whether the holistic side gains ground.
    thirds = []
    for r in runs:
        gens = [c["gen"] for c in r["champ"]]
        if not gens:
            continue
        g_max = max(gens)
        for k in range(3):
            lo, hi = k * g_max / 3, (k + 1) * g_max / 3
            sel = [c["mean"] for c in r["champ"] if lo <= c["gen"] <= hi] if k < 2 else [c["mean"] for c in r["champ"] if lo <= c["gen"]]
            thirds.append((k, float(np.mean(sel)) if sel else float("nan")))
    third_means = [round(float(np.nanmean([m for kk, m in thirds if kk == k])), 4) if thirds else None for k in range(3)]
    return {"runs": runs, "mean_curve": mean_curve, "totals": totals, "thirds": third_means}


def build_report(run_dirs: list[str], out_path: str, title: Optional[str] = None) -> dict:
    summary = summarize(run_dirs)
    runs = summary["runs"]
    cfg = runs[0]["config"]
    multi = len(runs) > 1
    payload = {
        "multi": multi,
        "runs": [{"name": r["name"], "seed": r["seed"], "champ": r["champ"], "pops": r["pops"]} for r in runs],
        "mean_curve": summary["mean_curve"],
        "totals": summary["totals"],
        "thirds": summary["thirds"],
        "config": {"generations": cfg.get("generations"), "population_size": cfg.get("population_size"), "duration": cfg.get("sim", {}).get("duration"), "champions": cfg.get("champions"), "champion_mode": cfg.get("champion_mode"), "champion_interval": cfg.get("champion_interval")},
    }
    data = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    if title is None:
        title = f"Holistic vs Conventional, {cfg.get('generations')} Generations" + (f", {len(runs)} Seeds" if multi else "")
    html = _TEMPLATE.replace("__TITLE__", title).replace("__DATA__", data)
    with open(out_path, "w") as f:
        f.write(html)
    return {"runs": len(runs), "bytes": os.path.getsize(out_path), "totals": summary["totals"], "thirds": summary["thirds"]}


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
  --holistic: #2a78d6; --holistic-band: rgba(42,120,214,0.14);
  --conventional: #eb6834; --parity: #8d8e90;
  --font-display: 'Spectral', Georgia, 'Times New Roman', serif;
  --font-body: 'Source Sans 3', 'Segoe UI', Helvetica, Arial, sans-serif;
  --font-mono: 'IBM Plex Mono', ui-monospace, 'SF Mono', Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --surface: #1a1b1e; --surface-2: #232428; --line: #35363b; --grid: #2b2c31;
    --ink: #f2f2ee; --ink-2: #c2c2bb; --ink-3: #8c8d92;
    --holistic: #3987e5; --holistic-band: rgba(57,135,229,0.20);
    --conventional: #d95926; --parity: #8d8e90;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --surface: #1a1b1e; --surface-2: #232428; --line: #35363b; --grid: #2b2c31;
  --ink: #f2f2ee; --ink-2: #c2c2bb; --ink-3: #8c8d92;
  --holistic: #3987e5; --holistic-band: rgba(57,135,229,0.20);
  --conventional: #d95926; --parity: #8d8e90;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--surface); color: var(--ink); font-family: var(--font-body); font-size: 16px; line-height: 1.5; padding-block: 40px 64px; padding-inline: 20px; }
main { max-width: 880px; margin: 0 auto; display: grid; gap: 40px; }
header { display: grid; gap: 10px; }
.eyebrow { font-family: var(--font-mono); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-3); }
h1 { font-family: var(--font-display); font-weight: 600; font-size: clamp(26px, 4vw, 36px); line-height: 1.15; margin: 0; text-wrap: balance; }
h2 { font-family: var(--font-display); font-weight: 500; font-size: 22px; margin: 0 0 4px; text-wrap: balance; }
p { margin: 0; max-width: 62ch; color: var(--ink-2); }
.lede { font-size: 17px; }
.figures { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.figure { padding: 16px 16px 16px 0; display: grid; gap: 2px; }
.figure + .figure { border-left: 1px solid var(--line); padding-left: 16px; }
.figure .value { font-family: var(--font-mono); font-size: 30px; font-weight: 500; line-height: 1.1; font-variant-numeric: tabular-nums; }
.figure .label { font-size: 13px; color: var(--ink-2); }
.figure .sub { font-size: 12px; color: var(--ink-3); font-variant-numeric: tabular-nums; }
section { display: grid; gap: 14px; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 20px; font-size: 13px; color: var(--ink-2); }
.legend span { display: inline-flex; align-items: center; gap: 8px; }
.key { display: inline-block; width: 22px; height: 0; border-top: 2px solid var(--holistic); }
.key.thin { border-top-width: 1px; opacity: 0.5; }
.key.dashed { border-top-style: dashed; }
.key.conv { border-top-color: var(--conventional); }
.key.parity { border-top: 1px dashed var(--parity); }
.key.band { height: 10px; border: 0; background: var(--holistic-band); }
.chart { position: relative; }
svg { width: 100%; height: auto; display: block; overflow: visible; }
svg text { font-family: var(--font-mono); font-size: 11px; fill: var(--ink-3); }
svg .axis-title { font-family: var(--font-body); font-size: 12px; fill: var(--ink-2); }
svg .grid line { stroke: var(--grid); stroke-width: 1; }
svg .axis line { stroke: var(--line); }
.crosshair { stroke: var(--ink-3); stroke-width: 1; stroke-dasharray: 3 3; opacity: 0; }
.tip { position: absolute; pointer-events: none; background: var(--surface-2); border: 1px solid var(--line); border-radius: 4px; padding: 8px 10px; font-size: 12px; color: var(--ink-2); display: none; min-width: 150px; box-shadow: 0 2px 8px rgba(0,0,0,0.12); }
.tip .t { font-family: var(--font-mono); color: var(--ink-3); margin-bottom: 4px; }
.tip .row { display: flex; align-items: center; gap: 8px; font-variant-numeric: tabular-nums; }
.tip .row b { font-family: var(--font-mono); font-weight: 500; color: var(--ink); min-width: 44px; }
.tip .k { width: 14px; border-top: 2px solid; }
details { border-top: 1px solid var(--line); padding-top: 10px; }
summary { cursor: pointer; color: var(--ink-2); font-size: 14px; }
summary:focus-visible { outline: 2px solid var(--holistic); outline-offset: 2px; }
.tablewrap { overflow-x: auto; margin-top: 12px; }
table { border-collapse: collapse; width: 100%; font-size: 13px; font-variant-numeric: tabular-nums; }
th, td { text-align: right; padding: 6px 10px; border-bottom: 1px solid var(--grid); font-family: var(--font-mono); font-weight: 400; }
th { color: var(--ink-3); font-size: 11px; letter-spacing: 0.05em; text-transform: uppercase; }
th:first-child, td:first-child { text-align: left; }
.note { font-size: 13px; color: var(--ink-3); }
@media (max-width: 560px) { .figures { grid-template-columns: 1fr; } .figure + .figure { border-left: 0; border-top: 1px solid var(--line); padding-left: 0; } }
</style>
</head>
<body>
<main>
<header>
  <div class="eyebrow" id="eyebrow"></div>
  <h1 id="title"></h1>
  <p class="lede" id="lede"></p>
</header>
<div class="figures" id="figures"></div>
<section>
  <h2>Champion curve</h2>
  <div class="legend" id="legend1"></div>
  <div class="chart" id="c1"></div>
  <p class="note">A robot's fitness is the opponent's final distance from the centre divided by the sum of both distances, so each bout is zero-sum: 0.5 is parity and 1 means the opponent never got closer than the robot did.</p>
</section>
<section>
  <h2>Body and brain size of each generation's best</h2>
  <div class="legend"><span><i class="key"></i>Holistic: neural units</span><span><i class="key dashed"></i>Holistic: links</span><span><i class="key conv"></i>Conventional: neural units</span><span><i class="key conv dashed"></i>Conventional: links</span></div>
  <div class="chart" id="c3"></div>
  <p class="note">Units and links of the synthesised phenotype of the best individual, averaged across seeds when several are shown. The conventional controller's topology never changes; the holistic side is free to add units and links, and a unit is only useful if something links to it.</p>
</section>
<section>
  <h2>Mass of each generation's best</h2>
  <div class="legend"><span><i class="key"></i>Holistic best</span><span><i class="key conv"></i>Conventional best</span></div>
  <div class="chart" id="c4"></div>
  <p class="note">Total body mass in kilograms. The fixed body never changes; the holistic side can grow, and in a shoving contest mass is an asset.</p>
</section>
<section>
  <h2>Inside each population</h2>
  <div class="legend"><span><i class="key"></i>Holistic best</span><span><i class="key dashed"></i>Holistic mean</span><span><i class="key conv"></i>Conventional best</span><span><i class="key conv dashed"></i>Conventional mean</span></div>
  <div class="chart" id="c2"></div>
  <p class="note">Within a population every member fights the previous generation's best and the best fights the runner-up, so these scores are relative to a moving opponent and say how spread out each population is rather than how strong it is.</p>
</section>
<details>
  <summary>Checkpoint table</summary>
  <div class="tablewrap"><table id="tbl"><thead><tr><th>Run</th><th>Generation</th><th>Holistic mean</th><th>Worst bout</th><th>Best bout</th><th>Wins</th><th>Losses</th></tr></thead><tbody></tbody></table></div>
</details>
</main>
<script>
const DATA = __DATA__;
(function () {
  const NS = 'http://www.w3.org/2000/svg';
  const $ = id => document.getElementById(id);
  function mk(name, attrs, parent) { const e = document.createElementNS(NS, name); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
  function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }
  const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const R = DATA.runs, cfg = DATA.config, multi = DATA.multi;
  const lastGen = Math.max(...R.map(r => r.pops.holistic[r.pops.holistic.length - 1].generation));
  const nBouts = R[0].champ.length ? R[0].champ[0].n : 0;

  $('eyebrow').textContent = `Rabbitstew · ${multi ? R.length + ' seeds (' + R.map(r => r.seed).join(', ') + ')' : R[0].name + ' · seed ' + R[0].seed} · ${cfg.population_size} per population · ${cfg.duration} s bouts · ${cfg.champion_mode === 'roundrobin' ? 'round-robin' : 'best-vs-best'} champions, top ${cfg.champions}`;
  $('title').textContent = `Holistic against conventional evolution over ${lastGen + 1} generations` + (multi ? `, ${R.length} seeds` : '');
  $('lede').textContent = `Every ${cfg.champion_interval === 1 ? '' : cfg.champion_interval + ' '}generation${cfg.champion_interval === 1 ? '' : 's'} the top ${cfg.champions} holistic creatures met the top ${cfg.champions} fixed-body Pioneers${cfg.champion_mode === 'roundrobin' ? ', each pair from both starting sides, for ' + nBouts + ' bouts' : ''}. The curve is the holistic side's mean zero-sum fitness across those bouts${multi ? ', and the emphasised line is the mean over ' + R.length + ' independent seeds' : ''}. 0.5 is parity; above it the evolved bodies are getting closer to the centre than the wheeled box.`;

  // ---- headline figures ----------------------------------------------------
  const figs = $('figures');
  function figure(value, label, sub) { const f = el('div', 'figure'); f.append(el('div', 'value', value), el('div', 'label', label), el('div', 'sub', sub)); figs.appendChild(f); }
  const t = DATA.thirds;
  const curve = multi ? DATA.mean_curve : R[0].champ;
  const first = curve[0], last = curve[curve.length - 1];
  figure(last.mean.toFixed(3), (multi ? 'Final champion fitness, mean of seeds' : 'Final holistic champion fitness'), `generation ${last.gen}, from ${first.mean.toFixed(3)} at generation ${first.gen}`);
  figure(t.map(x => x === null ? '–' : x.toFixed(2)).join(' → '), 'By thirds of the run', 'mean champion fitness in the first, second and last third');
  figure(DATA.totals.wins + '–' + DATA.totals.losses, 'Holistic wins over all champion bouts', `${DATA.totals.n} bouts` + (multi ? ` across ${R.length} seeds` : ''));

  // ---- generic line chart --------------------------------------------------
  function lineChart(container, opts) {
    const W = 880, H = opts.height || 340, m = { t: 16, r: 20, b: 44, l: 56 };
    const iw = W - m.l - m.r, ih = H - m.t - m.b;
    const svg = mk('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': opts.label }, container);
    const x = g => m.l + (g - opts.x0) / (opts.x1 - opts.x0 || 1) * iw;
    const y = v => m.t + (1 - (v - opts.y0) / (opts.y1 - opts.y0 || 1)) * ih;
    const grid = mk('g', { class: 'grid' }, svg);
    for (let v = opts.y0; v <= opts.y1 + 1e-9; v += opts.ystep) {
      mk('line', { x1: m.l, x2: W - m.r, y1: y(v), y2: y(v) }, grid);
      const tt = mk('text', { x: m.l - 8, y: y(v) + 4, 'text-anchor': 'end' }, svg); tt.textContent = opts.yfmt ? opts.yfmt(v) : v.toFixed(2);
    }
    const ax = mk('g', { class: 'axis' }, svg);
    mk('line', { x1: m.l, x2: W - m.r, y1: y(opts.y0), y2: y(opts.y0) }, ax);
    for (let g = opts.x0; g <= opts.x1; g += opts.xstep) { const tt = mk('text', { x: x(g), y: H - m.b + 18, 'text-anchor': 'middle' }, svg); tt.textContent = g; }
    const xt = mk('text', { x: m.l + iw / 2, y: H - 6, 'text-anchor': 'middle', class: 'axis-title' }, svg); xt.textContent = 'Generation';
    const yt = mk('text', { x: 12, y: m.t + ih / 2, 'text-anchor': 'middle', class: 'axis-title', transform: `rotate(-90 12 ${m.t + ih / 2})` }, svg); yt.textContent = opts.ylabel;
    if (opts.parity != null) mk('line', { x1: m.l, x2: W - m.r, y1: y(opts.parity), y2: y(opts.parity), stroke: css('--parity'), 'stroke-dasharray': '4 4', 'stroke-width': 1 }, svg);
    if (opts.band) {
      const up = opts.band.map(p => `${x(p.gen)},${y(p.hi)}`), dn = opts.band.slice().reverse().map(p => `${x(p.gen)},${y(p.lo)}`);
      mk('polygon', { points: up.concat(dn).join(' '), fill: css('--holistic-band'), stroke: 'none' }, svg);
    }
    for (const s of opts.series) {
      if (!s.pts.length) continue;
      const d = s.pts.map((p, i) => (i ? 'L' : 'M') + x(p.gen) + ',' + y(p.v)).join(' ');
      mk('path', { d, fill: 'none', stroke: css(s.color), 'stroke-width': s.thin ? 1 : 2, opacity: s.thin ? 0.4 : 1, 'stroke-linejoin': 'round', 'stroke-linecap': 'round', 'stroke-dasharray': s.dashed ? '6 4' : 'none' }, svg);
      if (!s.thin) { const p = s.pts[s.pts.length - 1]; mk('circle', { cx: x(p.gen), cy: y(p.v), r: 4, fill: css(s.color), stroke: css('--surface'), 'stroke-width': 2 }, svg); }
    }
    // hover: crosshair snaps to nearest x, tooltip lists every non-thin series
    const main = opts.series.filter(s => !s.thin);
    const cross = mk('line', { class: 'crosshair', y1: m.t, y2: m.t + ih }, svg);
    const dots = main.map(s => mk('circle', { r: 4, fill: css(s.color), stroke: css('--surface'), 'stroke-width': 2, opacity: 0 }, svg));
    const tip = el('div', 'tip'); container.appendChild(tip);
    const xs = [...new Set(main.flatMap(s => s.pts.map(p => p.gen)))].sort((a, b) => a - b);
    function show(clientX, clientY) {
      const r = svg.getBoundingClientRect(); const px = (clientX - r.left) / r.width * W;
      let best = 0; for (let i = 1; i < xs.length; i++) if (Math.abs(x(xs[i]) - px) < Math.abs(x(xs[best]) - px)) best = i;
      const g = xs[best];
      cross.setAttribute('x1', x(g)); cross.setAttribute('x2', x(g)); cross.style.opacity = 1;
      tip.replaceChildren(); tip.appendChild(el('div', 't', 'Generation ' + g));
      main.forEach((s, i) => {
        const p = s.pts.find(q => q.gen === g); if (!p) { dots[i].setAttribute('opacity', 0); return; }
        dots[i].setAttribute('cx', x(p.gen)); dots[i].setAttribute('cy', y(p.v)); dots[i].setAttribute('opacity', 1);
        const row = el('div', 'row'); const k = el('i', 'k'); k.style.borderTopColor = css(s.color); k.style.borderTopStyle = s.dashed ? 'dashed' : 'solid';
        row.append(k, el('b', null, opts.yfmt ? opts.yfmt(p.v) : p.v.toFixed(3)), el('span', null, s.name + (p.extra ? ' · ' + p.extra : ''))); tip.appendChild(row);
      });
      tip.style.display = 'block';
      const cr = container.getBoundingClientRect(); let left = clientX - cr.left + 14; if (left + 200 > cr.width) left = clientX - cr.left - 200;
      tip.style.left = left + 'px'; tip.style.top = Math.max(0, clientY - cr.top - 20) + 'px';
    }
    function hide() { cross.style.opacity = 0; tip.style.display = 'none'; dots.forEach(d => d.setAttribute('opacity', 0)); }
    svg.addEventListener('pointermove', e => show(e.clientX, e.clientY)); svg.addEventListener('pointerleave', hide);
    svg.setAttribute('tabindex', '0'); let fi = -1;
    svg.addEventListener('keydown', e => { if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return; fi = Math.min(xs.length - 1, Math.max(0, fi + (e.key === 'ArrowRight' ? 1 : -1))); const r = svg.getBoundingClientRect(); show(r.left + x(xs[fi]) / W * r.width, r.top + r.height / 3); e.preventDefault(); });
    svg.addEventListener('blur', hide);
  }
  const xstep = lastGen >= 40 ? 10 : 5;

  // ---- champion curve ------------------------------------------------------
  const leg = $('legend1');
  function legend(host, items) { for (const [cls, text] of items) { const s = el('span'); s.append(el('i', 'key ' + cls), text); host.appendChild(s); } }
  const series1 = [];
  if (multi) {
    for (const r of R) series1.push({ name: 'seed ' + r.seed, color: '--holistic', thin: true, pts: r.champ.map(c => ({ gen: c.gen, v: c.mean })) });
    series1.push({ name: 'mean of seeds', color: '--holistic', pts: DATA.mean_curve.map(c => ({ gen: c.gen, v: c.mean, extra: 'seeds span ' + c.lo.toFixed(2) + '–' + c.hi.toFixed(2) })) });
    legend(leg, [['', 'Mean of seeds'], ['thin', 'Each seed'], ['band', 'Lowest to highest seed'], ['parity', 'Parity']]);
  } else {
    series1.push({ name: 'holistic mean', color: '--holistic', pts: R[0].champ.map(c => ({ gen: c.gen, v: c.mean, extra: c.wins + '–' + c.losses + ' of ' + c.n })) });
    legend(leg, [['', 'Holistic mean fitness'], ['band', 'Worst to best single bout'], ['parity', 'Parity']]);
  }
  lineChart($('c1'), { label: 'Holistic champion fitness against the fixed body, by generation', x0: 0, x1: lastGen, xstep, y0: 0, y1: 1, ystep: 0.25, ylabel: 'Holistic mean fitness', parity: 0.5,
    band: (multi ? DATA.mean_curve : R[0].champ).map(c => ({ gen: c.gen, lo: c.lo, hi: c.hi })), series: series1 });

  // ---- averaged per-generation series over runs -----------------------------
  function avg(kind, key) {
    const gens = R[0].pops[kind].map(e => e.generation);
    return gens.map(g => { const vals = R.map(r => { const e = r.pops[kind].find(q => q.generation === g); return e ? e[key] : undefined; }).filter(v => v !== undefined); return { gen: g, v: vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0 }; });
  }
  const hasSize = R[0].pops.holistic[0].best_units !== undefined;
  if (hasSize) {
    const maxU = Math.max(...['holistic', 'conventional'].flatMap(k => ['best_units', 'best_links'].flatMap(key => avg(k, key).map(p => p.v))));
    const top = Math.ceil(maxU / 25) * 25 || 25;
    lineChart($('c3'), { label: 'Neural units and links of the best individual', x0: 0, x1: lastGen, xstep, y0: 0, y1: top, ystep: top / 5, yfmt: v => v.toFixed(0), ylabel: 'Count', parity: null, series: [
      { name: 'holistic units', color: '--holistic', pts: avg('holistic', 'best_units') }, { name: 'holistic links', color: '--holistic', dashed: true, pts: avg('holistic', 'best_links') },
      { name: 'conventional units', color: '--conventional', pts: avg('conventional', 'best_units') }, { name: 'conventional links', color: '--conventional', dashed: true, pts: avg('conventional', 'best_links') } ] });
    const maxM = Math.max(...avg('holistic', 'best_mass').map(p => p.v), ...avg('conventional', 'best_mass').map(p => p.v));
    const topM = Math.ceil(maxM / 25) * 25 || 25;
    lineChart($('c4'), { label: 'Mass of the best individual', x0: 0, x1: lastGen, xstep, y0: 0, y1: topM, ystep: topM / 5, yfmt: v => v.toFixed(0) + ' kg', ylabel: 'Mass', parity: null, height: 260, series: [
      { name: 'holistic best', color: '--holistic', pts: avg('holistic', 'best_mass') }, { name: 'conventional best', color: '--conventional', pts: avg('conventional', 'best_mass') } ] });
  } else { $('c3').parentElement.remove(); $('c4').parentElement.remove(); }
  lineChart($('c2'), { label: 'Best and mean within-population fitness for both populations, by generation', x0: 0, x1: lastGen, xstep, y0: 0, y1: 1, ystep: 0.25, ylabel: 'Fitness vs previous best', parity: null, series: [
    { name: 'holistic best', color: '--holistic', pts: avg('holistic', 'best_fitness') }, { name: 'holistic mean', color: '--holistic', dashed: true, pts: avg('holistic', 'mean_fitness') },
    { name: 'conventional best', color: '--conventional', pts: avg('conventional', 'best_fitness') }, { name: 'conventional mean', color: '--conventional', dashed: true, pts: avg('conventional', 'mean_fitness') } ] });

  const tb = document.querySelector('#tbl tbody');
  for (const r of R) for (const c of r.champ) { const tr = el('tr'); for (const v of [r.name, c.gen, c.mean.toFixed(3), c.lo.toFixed(3), c.hi.toFixed(3), c.wins, c.losses]) tr.appendChild(el('td', null, v)); tb.appendChild(tr); }
})();
</script>
</body>
</html>
"""
