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
    return _TEMPLATE.replace("__TITLE__", title).replace("__THREE__", THREE_JS_URL).replace("__DATA__", payload)


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


_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>__TITLE__</title>
<style>
  html, body { margin: 0; height: 100%; background: #1c1e24; color: #eee; font: 13px system-ui, sans-serif; overflow: hidden; }
  #hud { position: absolute; left: 12px; top: 10px; right: 12px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
  button { background: #2f3340; color: #eee; border: 1px solid #555; border-radius: 4px; padding: 4px 10px; cursor: pointer; }
  input[type=range] { flex: 1; min-width: 120px; }
  #help { position: absolute; left: 12px; bottom: 10px; opacity: 0.7; }
</style>
</head>
<body>
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
const DATA = __DATA__;
(function () {
  if (typeof THREE === 'undefined') { document.body.innerHTML = '<p style="padding:2em">three.js failed to load (this page needs network access to the CDN).</p>'; return; }
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x1c1e24);
  const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.01, 200);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(innerWidth, innerHeight);
  document.body.appendChild(renderer.domElement);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x445566, 0.9));
  const sun = new THREE.DirectionalLight(0xffffff, 0.7); sun.position.set(3, 5, 4); scene.add(sun);
  // MuJoCo is Z-up; three.js is Y-up.  Everything lives in a group rotated so world Z becomes screen Y.
  const world = new THREE.Group(); world.rotation.x = -Math.PI / 2; scene.add(world);
  const grid = new THREE.GridHelper(20, 40, 0x666666, 0x3a3d46); grid.rotation.x = Math.PI / 2; world.add(grid);
  const centre = new THREE.Mesh(new THREE.RingGeometry(0.18, 0.22, 48), new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide }));
  centre.position.z = 0.002; world.add(centre);

  const meshes = DATA.units.map(u => {
    let geom;
    if (u.shape === 0) geom = new THREE.BoxGeometry(u.dims[0], u.dims[1], u.dims[2]);
    else if (u.shape === 1) geom = new THREE.SphereGeometry(u.dims[0], 24, 16);
    else { geom = new THREE.CylinderGeometry(u.dims[0], u.dims[0], u.dims[1], 24); geom.rotateX(Math.PI / 2); } // length along local Z
    const mat = new THREE.MeshStandardMaterial({ color: DATA.palette[u.robot % DATA.palette.length], roughness: 0.6 });
    const m = new THREE.Mesh(geom, mat); world.add(m); return m;
  });

  function applyFrame(k) {
    const f = DATA.frames[k];
    for (let i = 0; i < meshes.length; i++) {
      const s = f[i];
      meshes[i].position.set(s[0], s[1], s[2]);
      meshes[i].quaternion.set(s[4], s[5], s[6], s[3]); // (w,x,y,z) -> three.js (x,y,z,w)
    }
    document.getElementById('time').textContent = (k * DATA.dt).toFixed(2) + ' s';
    scrub.value = k;
  }

  // Minimal orbit controls.
  let theta = 0.8, phi = 1.1, radius = 5, target = new THREE.Vector3(0, 0.3, 0);
  function updateCamera() {
    camera.position.set(target.x + radius * Math.sin(phi) * Math.cos(theta), target.y + radius * Math.cos(phi), target.z + radius * Math.sin(phi) * Math.sin(theta));
    camera.lookAt(target);
  }
  let drag = null;
  renderer.domElement.addEventListener('mousedown', e => { drag = { x: e.clientX, y: e.clientY, button: e.button }; });
  addEventListener('mouseup', () => { drag = null; });
  addEventListener('mousemove', e => {
    if (!drag) return;
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag.x = e.clientX; drag.y = e.clientY;
    if (drag.button === 2) {
      const right = new THREE.Vector3().subVectors(camera.position, target).cross(camera.up).normalize();
      target.addScaledVector(right, -dx * 0.003 * radius).addScaledVector(camera.up, dy * 0.003 * radius);
    } else { theta += dx * 0.01; phi = Math.min(Math.max(phi - dy * 0.01, 0.05), Math.PI - 0.05); }
    updateCamera();
  });
  renderer.domElement.addEventListener('contextmenu', e => e.preventDefault());
  renderer.domElement.addEventListener('wheel', e => { radius = Math.min(Math.max(radius * (1 + e.deltaY * 0.001), 0.5), 60); updateCamera(); });
  addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });

  const scrub = document.getElementById('scrub'); scrub.max = DATA.frames.length - 1;
  let playing = true, frame = 0, acc = 0, last = performance.now();
  document.getElementById('play').onclick = function () { playing = !playing; this.textContent = playing ? 'Pause' : 'Play'; };
  document.getElementById('reset').onclick = () => { frame = 0; applyFrame(0); };
  scrub.oninput = () => { frame = +scrub.value; applyFrame(frame); };
  function loop(now) {
    const speed = +document.getElementById('speed').value;
    if (playing && DATA.frames.length > 1) {
      acc += (now - last) / 1000 * speed;
      while (acc >= DATA.dt) { acc -= DATA.dt; frame = (frame + 1) % DATA.frames.length; }
      applyFrame(frame);
    }
    last = now; updateCamera(); renderer.render(scene, camera); requestAnimationFrame(loop);
  }
  applyFrame(0); updateCamera(); requestAnimationFrame(loop);
})();
</script>
</body>
</html>
"""
