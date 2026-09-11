"""HTML rendering of an analysis (see :mod:`rabbitstew.analysis`)."""

from __future__ import annotations

import json
from typing import Optional

from .report import _TEMPLATE as _REPORT_TEMPLATE

_HEAD = _REPORT_TEMPLATE.split("<main>")[0]

_BODY = """<main>
<header>
  <div class="eyebrow" id="eyebrow"></div>
  <h1>__TITLE__</h1>
  <p class="lede">What evolved, measured with the robot alone: solo capability trials, structural descriptors of body and brain, a lesion map of the final controllers, population diversity and the ancestry of the final best.</p>
</header>

<section>
  <h2>Solo capability of each generation's best</h2>
  <div class="legend"><span><i class="key"></i>Holistic best</span><span><i class="key conv"></i>Conventional best</span></div>
  <div class="grid2" id="cap"></div>
  <p class="note">Approach: metres gained towards a goal 2 m ahead on flat ground in 15 s. Steering: goals at 90°, −90° and 180° from the initial heading, successes out of 3. Terrain: success rate over a fixed bank of 6 random terrains. Push: displacement of a 13.5 kg block in the way. Work per metre: mechanical actuator work per metre of path. Straightness: displacement over path length.</p>
</section>

<section>
  <h2>Structure of each generation's best</h2>
  <div class="legend"><span><i class="key"></i>Holistic</span><span><i class="key conv"></i>Conventional</span><span><i class="key dashed"></i>secondary series (dashed)</span></div>
  <div class="grid2" id="struct"></div>
  <p class="note">Expressed nodes are genotype nodes that produced at least one part. Connected fraction is the share of units with any link. Centralisation is the share of links touching the global brain. Driven effectors are effectors on live joints that have an input; those reachable from an oscillator are shown dashed.</p>
</section>

<section>
  <h2>Final bests side by side</h2>
  <div class="tablewrap"><table id="final"><thead><tr><th>Measure</th><th>Holistic</th><th>Conventional</th></tr></thead><tbody></tbody></table></div>
</section>

<section id="lesion-section">
  <h2>Lesion map of the final controllers</h2>
  <p class="note">Each unit silenced in turn; the bar is the approach progress lost over a 6 s trial (positive = the unit helps, negative = removing it helps). Only units with an effect beyond 5 cm are listed.</p>
  <div class="grid2" id="lesions"></div>
</section>

<section>
  <h2>Sensor influence in the final controllers</h2>
  <p class="note">Static influence: total absolute weight along all paths of up to four links from the sensor to a live effector. A sensor with zero influence cannot affect behaviour.</p>
  <div class="grid2" id="influence"></div>
</section>

<section>
  <h2>Diversity and ancestry</h2>
  <div class="legend"><span><i class="key"></i>Holistic</span><span><i class="key conv"></i>Conventional</span></div>
  <div class="grid2" id="pop"></div>
  <p class="note" id="lineage-note"></p>
</section>
</main>
<script>
const A = __DATA__;
(function () {
  const NS = 'http://www.w3.org/2000/svg';
  const $ = id => document.getElementById(id);
  const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }
  function mk(name, attrs, parent) { const e = document.createElementNS(NS, name); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
  const I = A.individuals, H = I.filter(r => r.population === 'holistic').sort((a, b) => a.generation - b.generation), C = I.filter(r => r.population === 'conventional').sort((a, b) => a.generation - b.generation);
  const lastGen = Math.max(...I.map(r => r.generation));
  $('eyebrow').textContent = `Rabbitstew · ${A.run} · seed ${A.config.seed} · ${A.config.brain_model} brain · ${A.config.terrain} terrain · ${I.length} individuals analysed`;

  function small(host, title, series, opts) {
    opts = opts || {};
    const card = el('div', 'small'); card.appendChild(el('h3', null, title)); host.appendChild(card);
    const W = 420, Hh = 190, m = { t: 10, r: 12, b: 28, l: 44 }, iw = W - m.l - m.r, ih = Hh - m.t - m.b;
    const all = series.flatMap(s => s.pts.map(p => p.v)).filter(v => v !== null && v !== undefined && isFinite(v));
    let y0 = opts.y0 !== undefined ? opts.y0 : Math.min(0, ...all), y1 = opts.y1 !== undefined ? opts.y1 : Math.max(...all, y0 + 1e-6);
    if (y1 === y0) y1 = y0 + 1;
    const svg = mk('svg', { viewBox: `0 0 ${W} ${Hh}` }, card);
    const x = g => m.l + g / (lastGen || 1) * iw, y = v => m.t + (1 - (v - y0) / (y1 - y0)) * ih;
    for (let k = 0; k <= 4; k++) { const v = y0 + (y1 - y0) * k / 4; mk('line', { x1: m.l, x2: W - m.r, y1: y(v), y2: y(v), stroke: css('--grid') }, svg); const t = mk('text', { x: m.l - 6, y: y(v) + 4, 'text-anchor': 'end' }, svg); t.textContent = (opts.fmt || (q => q.toFixed(2)))(v); }
    for (const g of [0, Math.round(lastGen / 2), lastGen]) { const t = mk('text', { x: x(g), y: Hh - 8, 'text-anchor': 'middle' }, svg); t.textContent = g; }
    if (opts.ref !== undefined) mk('line', { x1: m.l, x2: W - m.r, y1: y(opts.ref), y2: y(opts.ref), stroke: css('--parity'), 'stroke-dasharray': '4 4' }, svg);
    for (const s of series) {
      const pts = s.pts.filter(p => p.v !== null && p.v !== undefined && isFinite(p.v));
      if (!pts.length) continue;
      mk('path', { d: pts.map((p, i) => (i ? 'L' : 'M') + x(p.gen) + ',' + y(p.v)).join(' '), fill: 'none', stroke: css(s.color), 'stroke-width': 2, 'stroke-dasharray': s.dashed ? '5 4' : 'none', 'stroke-linejoin': 'round' }, svg);
      for (const p of pts) { const c = mk('circle', { cx: x(p.gen), cy: y(p.v), r: 2.5, fill: css(s.color) }, svg); const tt = mk('title', {}, c); tt.textContent = `${s.name} · gen ${p.gen}: ${p.v}`; }
    }
  }
  const pick = (rows, f) => rows.map(r => ({ gen: r.generation, v: f(r) }));
  const two = (title, f, opts) => small($('cap'), title, [{ name: 'holistic', color: '--holistic', pts: pick(H, f) }, { name: 'conventional', color: '--conventional', pts: pick(C, f) }], opts);
  two('Approach progress (m)', r => r.capability.approach.progress, { ref: 0 });
  two('Steering successes (of 3)', r => r.capability.steering.successes, { y0: 0, y1: 3, fmt: v => v.toFixed(0) });
  two('Terrain success rate', r => r.capability.terrain.success_rate, { y0: 0, y1: 1 });
  two('Push: block displacement (m)', r => r.capability.push.block_displacement, { y0: 0 });
  two('Work per metre (J/m)', r => Math.min(r.capability.approach.work_per_metre, 5000), { y0: 0, fmt: v => v.toFixed(0) });
  two('Straightness', r => r.capability.approach.straightness, { y0: 0, y1: 1 });

  const st = (title, fh, fc, opts, fh2, fc2) => small($('struct'), title, [
    { name: 'holistic', color: '--holistic', pts: pick(H, fh) }, { name: 'conventional', color: '--conventional', pts: pick(C, fc || fh) },
    ...(fh2 ? [{ name: 'holistic (dashed)', color: '--holistic', dashed: true, pts: pick(H, fh2) }, { name: 'conventional (dashed)', color: '--conventional', dashed: true, pts: pick(C, fc2 || fh2) }] : [])], opts);
  st('Parts (solid) and expressed nodes (dashed)', r => r.morphology.parts, null, { y0: 0, fmt: v => v.toFixed(0) }, r => r.morphology.expressed_nodes);
  st('Mirror symmetry', r => r.morphology.symmetry, null, { y0: 0, y1: 1 });
  st('Connected fraction (solid), centralisation (dashed)', r => r.controller.connected_fraction, null, { y0: 0, y1: 1 }, r => r.controller.centralisation);
  st('Driven effectors (solid), oscillator-driven (dashed)', r => r.controller.driven_effectors, null, { y0: 0, fmt: v => v.toFixed(0) }, r => r.controller.oscillator_driven_effectors);
  st('Neural units (solid) and links (dashed)', r => r.controller.units, null, { y0: 0, fmt: v => v.toFixed(0) }, r => r.controller.links);
  st('Mean sensor-to-effector path (links)', r => r.controller.mean_sensor_path, null, { y0: 0, fmt: v => v.toFixed(1) });

  const fh = H[H.length - 1], fc = C[C.length - 1], tb = document.querySelector('#final tbody');
  const row = (k, a, b) => { const tr = el('tr'); tr.append(el('td', null, k), el('td', null, a), el('td', null, b)); tb.appendChild(tr); };
  if (fh && fc) {
    row('name', fh.name, fc.name);
    row('approach progress (m)', fh.capability.approach.progress, fc.capability.approach.progress);
    row('mean speed (m/s)', fh.capability.approach.mean_speed, fc.capability.approach.mean_speed);
    row('straightness', fh.capability.approach.straightness, fc.capability.approach.straightness);
    row('fell over', fh.capability.approach.fell, fc.capability.approach.fell);
    row('steering successes', fh.capability.steering.successes + ' of ' + fh.capability.steering.trials.length, fc.capability.steering.successes + ' of ' + fc.capability.steering.trials.length);
    row('terrain success rate', fh.capability.terrain.success_rate, fc.capability.terrain.success_rate);
    row('block displacement (m)', fh.capability.push.block_displacement, fc.capability.push.block_displacement);
    row('work per metre (J/m)', fh.capability.approach.work_per_metre, fc.capability.approach.work_per_metre);
    row('parts / nodes (expressed)', `${fh.morphology.parts} / ${fh.morphology.nodes} (${fh.morphology.expressed_nodes})`, `${fc.morphology.parts} / ${fc.morphology.nodes} (${fc.morphology.expressed_nodes})`);
    row('mass (kg)', fh.morphology.mass, fc.morphology.mass);
    row('symmetry', fh.morphology.symmetry, fc.morphology.symmetry);
    row('units / links', `${fh.controller.units} / ${fh.controller.links}`, `${fc.controller.units} / ${fc.controller.links}`);
    row('driven effectors (env / oscillator)', `${fh.controller.driven_effectors} (${fh.controller.env_driven_effectors} / ${fh.controller.oscillator_driven_effectors})`, `${fc.controller.driven_effectors} (${fc.controller.env_driven_effectors} / ${fc.controller.oscillator_driven_effectors})`);
    row('connected fraction', fh.controller.connected_fraction, fc.controller.connected_fraction);
    row('cyclic units', fh.controller.cyclic_units, fc.controller.cyclic_units);
    if (fh.lesions && fc.lesions) { row('essential units (lesion > 10 cm)', fh.lesions.essential_units, fc.lesions.essential_units); row('effective fraction of units', fh.lesions.effective_fraction, fc.lesions.effective_fraction); }
  }

  function bars(host, title, rows, color, valueKey, labelFn) {
    const card = el('div', 'small'); card.appendChild(el('h3', null, title)); host.appendChild(card);
    if (!rows.length) { card.appendChild(el('p', 'note', 'nothing to show')); return; }
    const maxAbs = Math.max(...rows.map(r => Math.abs(r[valueKey])), 1e-6);
    const list = el('div', 'bars'); card.appendChild(list);
    for (const r of rows) {
      const line = el('div', 'bar');
      line.appendChild(el('span', 'lbl', labelFn(r)));
      const track = el('span', 'track'); const fill = el('i');
      const w = Math.abs(r[valueKey]) / maxAbs * 50;
      fill.style.width = w + '%'; fill.style.left = (r[valueKey] >= 0 ? 50 : 50 - w) + '%'; fill.style.background = css(r[valueKey] >= 0 ? color : '--w-neg');
      track.appendChild(fill); line.appendChild(track);
      line.appendChild(el('span', 'val', (r[valueKey] >= 0 ? '+' : '') + r[valueKey].toFixed(2)));
      list.appendChild(line);
    }
  }
  for (const [r, color, name] of [[fh, '--holistic', 'Holistic'], [fc, '--conventional', 'Conventional']]) {
    if (!r) continue;
    if (r.lesions) {
      const rows = r.lesions.units.filter(u => Math.abs(u.loss) > 0.05).sort((a, b) => b.loss - a.loss).slice(0, 18);
      bars($('lesions'), `${name} ${r.name}: ${r.lesions.essential_units} essential of ${r.lesions.units.length} units (baseline ${r.lesions.baseline} m)`, rows, color, 'loss', u => `#${u.unit} ${u.label}${u.part === null ? ' (global)' : ' p' + u.part}`);
    }
    const inf = r.influence.slice().sort((a, b) => b.influence - a.influence).slice(0, 18);
    bars($('influence'), `${name} ${r.name}: ${r.influence.filter(s => s.influence > 0).length} of ${r.influence.length} sensors reach an effector`, inf, color, 'influence', s => `#${s.unit} ${s.label} p${s.part}`);
  }
  if (!fh || !fh.lesions) $('lesion-section').hidden = true;

  const dv = A.diversity.filter(d => d.scope === 'champions');
  small($('pop'), 'Diversity of checkpoint champions', [{ name: 'holistic', color: '--holistic', pts: dv.filter(d => d.population === 'holistic').map(d => ({ gen: d.generation, v: d.diversity })) }, { name: 'conventional', color: '--conventional', pts: dv.filter(d => d.population === 'conventional').map(d => ({ gen: d.generation, v: d.diversity })) }], { y0: 0 });
  const L = A.lineage || {};
  const chainSeries = [];
  for (const [kind, color] of [['holistic', '--holistic'], ['conventional', '--conventional']]) if (L[kind]) chainSeries.push({ name: kind + ' ancestor fitness', color, pts: L[kind].chain.map(c => ({ gen: c.generation, v: c.fitness })) });
  if (chainSeries.length) small($('pop'), 'Ancestry of the final best: fitness of each ancestor', chainSeries, { y0: 0, y1: 1, ref: 0.5 });
  const notes = [];
  for (const kind of ['holistic', 'conventional']) if (L[kind]) notes.push(`${kind}: the final best descends through ${L[kind].chain.length} generations; the final population traces back to ${L[kind].founders.founders} of the ${A.config.population_size} generation-0 founders.`);
  const fd = A.diversity.filter(d => d.scope === 'final');
  for (const d of fd) notes.push(`${d.population} final population diversity ${d.diversity} (n = ${d.n}).`);
  $('lineage-note').textContent = notes.join(' ') || 'No lineage log in this run (it predates parent tracking).';
})();
</script>
</body>
</html>
"""

_EXTRA_CSS = """
.grid2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px 24px; }
.small h3 { font-family: var(--font-body); font-weight: 600; font-size: 13px; margin: 0 0 4px; color: var(--ink-2); }
.small svg { width: 100%; height: auto; }
.bars { display: grid; gap: 4px; font-size: 12px; font-family: var(--font-mono); }
.bar { display: grid; grid-template-columns: minmax(0, 1.2fr) 2fr 52px; gap: 8px; align-items: center; }
.bar .lbl { color: var(--ink-2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bar .track { position: relative; height: 10px; background: var(--surface-2); border-radius: 2px; }
.bar .track i { position: absolute; top: 0; height: 100%; border-radius: 2px; }
.bar .val { text-align: right; color: var(--ink); font-variant-numeric: tabular-nums; }
h3 { text-wrap: balance; }
"""


def render(analysis: dict, title: Optional[str] = None) -> str:
    title = title or f"What Evolved, {analysis.get('run', 'run')}"
    data = json.dumps(analysis, separators=(",", ":")).replace("</", "<\\/")
    head = _HEAD.replace("__TITLE__", title).replace("</style>", _EXTRA_CSS + "</style>")
    # the report head declares --w-neg only in the gallery; add it here
    head = head.replace("--conventional: #eb6834; --parity: #8d8e90;", "--conventional: #eb6834; --parity: #8d8e90; --w-neg: #e34948;", 1)
    head = head.replace("--conventional: #d95926; --parity: #8d8e90;", "--conventional: #d95926; --parity: #8d8e90; --w-neg: #e66767;")
    return head + _BODY.replace("__TITLE__", title).replace("__DATA__", data)
