"""Replay visualizer for trajectory files.

The paper's visualizer reads the unit data, builds one model per unit, then
loops over the recorded states updating every model's position and
orientation.  Here the same procedure is compiled into a self-contained HTML
page (three.js is loaded from a CDN) so a recorded bout can be opened in any
browser without a Python graphics stack.  :func:`launch_live` offers an
interactive MuJoCo viewer when one is available.

The orientation helpers implement the quaternion method from the paper: a
unit's axis vector is the X axis of its frame and its up vector the Y axis,
obtained by rotating ``(1, 0, 0)`` and ``(0, 1, 0)`` by the unit's quaternion.
(The paper writes the product as ``q' v q``; with the ``(w, x, y, z)``
convention used by ODE and MuJoCo the active rotation is ``q v q'``, which
is what the physics engine reports and what is used here.)
"""

from __future__ import annotations

import json
from typing import Optional

import numpy as np

from . import quat
from .genotype import Shape
from .trajectory import Trajectory

THREE_JS_URL = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"


def orientation_axes(q) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(axis, up)``: the unit's local X and Y axes in world coordinates."""
    return quat.rotate(q, (1.0, 0.0, 0.0)), quat.rotate(q, (0.0, 1.0, 0.0))


def cylinder_end_position(center, q, length: float) -> np.ndarray:
    """Position of one end of a cylinder given its centre (the physics engine's
    reference point) and orientation.  A cylinder's length runs along its local
    Z axis; this is the adjustment the paper notes is needed for renderers that
    anchor cylinders at an end point instead of the centre of mass."""
    z_axis = quat.rotate(q, (0.0, 0.0, 1.0))
    return np.asarray(center, dtype=float) - 0.5 * length * z_axis


PALETTE = ["#d94f3d", "#3f73d9", "#4db35a", "#d9a632", "#9a5fc0", "#3fb8c2"]


def to_html(traj: Trajectory, title: str = "Rabbitstew replay", decimals: int = 4) -> str:
    """Render a trajectory as a self-contained HTML replay page."""
    units = [{"shape": int(u.shape), "dims": [round(float(d), 5) for d in u.dims], "robot": traj.robot_of_unit(i)} for i, u in enumerate(traj.units)]
    frames = np.round(traj.as_array(), decimals).tolist()
    payload = json.dumps({"dt": traj.dt, "units": units, "frames": frames, "palette": PALETTE}, separators=(",", ":"))
    return _TEMPLATE.replace("__TITLE__", title).replace("__THREE__", THREE_JS_URL).replace("__SCENE__", SCENE_JS).replace("__DATA__", payload)


def write_html(traj: Trajectory, path, title: Optional[str] = None) -> None:
    with open(path, "w") as f:
        f.write(to_html(traj, title or "Rabbitstew replay"))


def launch_live(sim) -> None:
    """Open the interactive MuJoCo viewer on a :class:`~rabbitstew.simulation.Simulation`
    and run it in real time until the window is closed."""
    import time

    import mujoco.viewer  # noqa: WPS433 (optional dependency on a display)

    with mujoco.viewer.launch_passive(sim.model, sim.data) as viewer:
        while viewer.is_running():
            t0 = time.time()
            sim.step()
            viewer.sync()
            lag = sim.config.control_dt - (time.time() - t0)
            if lag > 0:
                time.sleep(lag)


# JavaScript shared by every replay page: a three.js scene that shows the units of a
# trajectory, and a transport (play / pause / scrub / speed) that drives it.
SCENE_JS = r"""
class RabbitstewReplay {
  constructor(container, theme) {
    this.container = container;
    this.theme = Object.assign({ background: '#1c1e24', grid1: '#666666', grid2: '#3a3d46', ring: '#ffffff',
      palette: ['#d94f3d', '#3f73d9', '#4db35a', '#d9a632', '#9a5fc0', '#3fb8c2'] }, theme || {});
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(this.theme.background);
    this.camera = new THREE.PerspectiveCamera(50, 1, 0.01, 200);
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    container.appendChild(this.renderer.domElement);
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x445566, 0.9));
    const sun = new THREE.DirectionalLight(0xffffff, 0.7); sun.position.set(3, 5, 4); this.scene.add(sun);
    // MuJoCo is Z-up; three.js is Y-up.  Everything lives in a group rotated so world Z becomes screen Y.
    this.world = new THREE.Group(); this.world.rotation.x = -Math.PI / 2; this.scene.add(this.world);
    this.grid = new THREE.GridHelper(20, 40, this.theme.grid1, this.theme.grid2); this.grid.rotation.x = Math.PI / 2; this.world.add(this.grid);
    this.ring = new THREE.Mesh(new THREE.RingGeometry(0.18, 0.22, 48), new THREE.MeshBasicMaterial({ color: this.theme.ring, side: THREE.DoubleSide }));
    this.ring.position.z = 0.002; this.world.add(this.ring);
    this.meshes = []; this.data = null; this.frame = 0;
    this.theta = 0.8; this.phi = this.theme.phi || 1.1; this.radius = this.theme.radius || 5; this.target = new THREE.Vector3(0, 0.3, 0);
    this._controls(); this._resize();
    if (typeof ResizeObserver !== 'undefined') new ResizeObserver(() => this._resize()).observe(container);
    else addEventListener('resize', () => this._resize());
  }
  _resize() {
    const w = Math.max(1, this.container.clientWidth), h = Math.max(1, this.container.clientHeight);
    this.renderer.setSize(w, h, false); this.camera.aspect = w / h; this.camera.updateProjectionMatrix(); this.render();
  }
  _controls() {
    const el = this.renderer.domElement; let drag = null;
    el.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY, button: e.button }; el.setPointerCapture(e.pointerId); });
    el.addEventListener('pointerup', () => { drag = null; });
    el.addEventListener('pointermove', e => {
      if (!drag) return;
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag.x = e.clientX; drag.y = e.clientY;
      if (drag.button === 2) {
        const right = new THREE.Vector3().subVectors(this.camera.position, this.target).cross(this.camera.up).normalize();
        this.target.addScaledVector(right, -dx * 0.003 * this.radius).addScaledVector(this.camera.up, dy * 0.003 * this.radius);
      } else { this.theta += dx * 0.01; this.phi = Math.min(Math.max(this.phi - dy * 0.01, 0.05), Math.PI - 0.05); }
      this.render();
    });
    el.addEventListener('contextmenu', e => e.preventDefault());
    el.addEventListener('wheel', e => { e.preventDefault(); this.radius = Math.min(Math.max(this.radius * (1 + e.deltaY * 0.001), 0.5), 60); this.render(); }, { passive: false });
  }
  setTheme(theme) {
    Object.assign(this.theme, theme);
    this.scene.background = new THREE.Color(this.theme.background);
    this.world.remove(this.grid);
    this.grid = new THREE.GridHelper(20, 40, this.theme.grid1, this.theme.grid2); this.grid.rotation.x = Math.PI / 2; this.world.add(this.grid);
    this.ring.material.color.set(this.theme.ring);
    this.render();
  }
  load(data) {
    for (const m of this.meshes) { this.world.remove(m); m.geometry.dispose(); m.material.dispose(); }
    this.data = data; this.frame = 0;
    this.meshes = data.units.map(u => {
      let geom;
      if (u.shape === 0) geom = new THREE.BoxGeometry(u.dims[0], u.dims[1], u.dims[2]);
      else if (u.shape === 1) geom = new THREE.SphereGeometry(u.dims[0], 24, 16);
      else { geom = new THREE.CylinderGeometry(u.dims[0], u.dims[0], u.dims[1], 24); geom.rotateX(Math.PI / 2); } // length along local Z
      const mat = new THREE.MeshStandardMaterial({ color: this.theme.palette[u.robot % this.theme.palette.length], roughness: 0.6 });
      const m = new THREE.Mesh(geom, mat); this.world.add(m); return m;
    });
    this.applyFrame(0);
  }
  get frameCount() { return this.data ? this.data.frames.length : 0; }
  applyFrame(k) {
    if (!this.data || !this.data.frames.length) return;
    k = Math.min(Math.max(0, k | 0), this.data.frames.length - 1); this.frame = k;
    const f = this.data.frames[k];
    for (let i = 0; i < this.meshes.length; i++) {
      const s = f[i];
      this.meshes[i].position.set(s[0], s[1], s[2]);
      this.meshes[i].quaternion.set(s[4], s[5], s[6], s[3]); // (w,x,y,z) -> three.js (x,y,z,w)
    }
    this.render();
  }
  render() {
    this.camera.position.set(this.target.x + this.radius * Math.sin(this.phi) * Math.cos(this.theta), this.target.y + this.radius * Math.cos(this.phi), this.target.z + this.radius * Math.sin(this.phi) * Math.sin(this.theta));
    this.camera.lookAt(this.target);
    this.renderer.render(this.scene, this.camera);
  }
}

class RabbitstewTransport {
  constructor(replay, ui) {
    this.replay = replay; this.ui = ui; this.playing = true; this.acc = 0; this.last = performance.now(); this.onFrame = null;
    ui.play.addEventListener('click', () => this.toggle());
    if (ui.reset) ui.reset.addEventListener('click', () => this.seek(0));
    ui.scrub.addEventListener('input', () => { this.seek(+ui.scrub.value); });
    requestAnimationFrame(t => this._loop(t));
  }
  get speed() { return this.ui.speed ? +this.ui.speed.value : 1; }
  toggle(force) { this.playing = force === undefined ? !this.playing : force; this.ui.play.textContent = this.playing ? 'Pause' : 'Play'; }
  seek(k) { this.replay.applyFrame(k); this._sync(); }
  reload() { this.ui.scrub.max = Math.max(0, this.replay.frameCount - 1); this.acc = 0; this.seek(0); }
  _sync() {
    this.ui.scrub.value = this.replay.frame;
    if (this.ui.time) this.ui.time.textContent = (this.replay.frame * (this.replay.data ? this.replay.data.dt : 0)).toFixed(2) + ' s';
    if (this.onFrame) this.onFrame(this.replay.frame);
  }
  _loop(now) {
    const dt = this.replay.data ? this.replay.data.dt : 0.05;
    if (this.playing && this.replay.frameCount > 1) {
      this.acc += (now - this.last) / 1000 * this.speed;
      let k = this.replay.frame, moved = false;
      while (this.acc >= dt) { this.acc -= dt; k = (k + 1) % this.replay.frameCount; moved = true; }
      if (moved) { this.replay.applyFrame(k); this._sync(); }
    }
    this.last = now; requestAnimationFrame(t => this._loop(t));
  }
}
"""

_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>__TITLE__</title>
<style>
  html, body { margin: 0; height: 100%; background: #1c1e24; color: #eee; font: 13px system-ui, sans-serif; overflow: hidden; }
  #view { position: absolute; inset: 0; }
  #view canvas { display: block; width: 100%; height: 100%; }
  #hud { position: absolute; left: 12px; top: 10px; right: 12px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
  button { background: #2f3340; color: #eee; border: 1px solid #555; border-radius: 4px; padding: 4px 10px; cursor: pointer; }
  input[type=range] { flex: 1; min-width: 120px; }
  #help { position: absolute; left: 12px; bottom: 10px; opacity: 0.7; }
</style>
</head>
<body>
<div id="view"></div>
<div id="hud">
  <strong>__TITLE__</strong>
  <button id="play">Pause</button>
  <button id="reset">Reset</button>
  <label>Speed <select id="speed"><option>0.25</option><option>0.5</option><option selected>1</option><option>2</option><option>4</option></select></label>
  <input id="scrub" type="range" min="0" value="0" step="1">
  <span id="time">0.00 s</span>
</div>
<div id="help">drag to orbit, wheel to zoom, right-drag to pan</div>
<script src="__THREE__"></script>
<script>
__SCENE__
const DATA = __DATA__;
(function () {
  if (typeof THREE === 'undefined') { document.body.innerHTML = '<p style="padding:2em">three.js failed to load (this page needs network access to the CDN).</p>'; return; }
  const replay = new RabbitstewReplay(document.getElementById('view'), { palette: DATA.palette });
  const transport = new RabbitstewTransport(replay, { play: document.getElementById('play'), reset: document.getElementById('reset'), scrub: document.getElementById('scrub'), speed: document.getElementById('speed'), time: document.getElementById('time') });
  replay.load(DATA); transport.reload();
})();
</script>
</body>
</html>
"""
