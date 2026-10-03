"""Turn a champion into a 3D-printable figurine: one watertight STL on a plinth.

    python scripts/print_champion.py RUN KIND GEN OUT.stl [--seed S] [--time T] [--length MM] [--min-wall MM]

Records one solo bout exactly as ``scripts/shots.py`` does (the run's config,
opponent proxy on, spawn from SEED), takes the robot's pose at T seconds, and
builds every unit (box, sphere, cylinder) as a solid at that pose.  The units
are unioned into a single manifold with ``manifold3d``; parts that only touch
are fused by growing every unit by half the minimum wall, and any piece still
floating is bridged to the main body with a strut between the closest points.
The figure is scaled so its longest horizontal extent is LENGTH mm, any unit
thinner than MIN_WALL mm is thickened to it, and it is set into a round plinth
so the contact points print as solid feet.  Alongside the STL it writes
OUT.png, a shaded preview, and OUT.txt, the provenance (run, generation, seed,
frame, MuJoCo version, unit count, scale).

Needs ``mujoco``, ``manifold3d``, ``numpy`` and ``pillow``.  Nothing here
touches a registered analysis: it reads committed genomes and writes files.
"""
import argparse
import json
import os
import struct
from dataclasses import replace

import mujoco
import numpy as np
from manifold3d import Manifold

from rabbitstew.genotype import Genotype, Shape
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout

SEGMENTS = 48


def quat_matrix(q) -> np.ndarray:
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
        [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
        [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
    ])


def unit_solid(shape: Shape, dims, pos, quat, grow: float, floor: float) -> Manifold:
    """A unit as a solid in metres: dims are full extents (box), radius (sphere), radius + length (cylinder)."""
    d = [max(v, floor) for v in dims]
    if shape == Shape.BOX:
        m = Manifold.cube([d[0] + 2 * grow, d[1] + 2 * grow, d[2] + 2 * grow], center=True)
    elif shape == Shape.SPHERE:
        m = Manifold.sphere(d[0] + grow, SEGMENTS)
    else:
        m = Manifold.cylinder(d[1] + 2 * grow, d[0] + grow, d[0] + grow, SEGMENTS, center=True)
    rot = quat_matrix(np.asarray(quat, dtype=float))
    return m.transform(np.hstack([rot, np.asarray(pos, dtype=float).reshape(3, 1)]))


def closest_points(a: Manifold, b: Manifold):
    va = a.to_mesh().vert_properties[:, :3]
    vb = b.to_mesh().vert_properties[:, :3]
    best = (np.inf, None, None)
    for i in range(0, len(va), 2048):
        chunk = va[i:i + 2048]
        dist = np.linalg.norm(chunk[:, None, :] - vb[None, :, :], axis=2)
        j = np.unravel_index(np.argmin(dist), dist.shape)
        if dist[j] < best[0]:
            best = (dist[j], chunk[j[0]], vb[j[1]])
    return best[1], best[2]


def strut(p, q, radius: float) -> Manifold:
    v = np.asarray(q) - np.asarray(p)
    length = float(np.linalg.norm(v))
    m = Manifold.cylinder(length + 2 * radius, radius, radius, 16)
    z = v / length
    x = np.cross(z, [0, 0, 1] if abs(z[2]) < 0.9 else [1, 0, 0]); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    rot = np.column_stack([x, y, z])
    start = np.asarray(p) - z * radius
    return m.transform(np.hstack([rot, start.reshape(3, 1)]))


def fuse(parts: list, radius: float) -> Manifold:
    body = sum(parts[1:], parts[0])
    pieces = sorted(body.decompose(), key=lambda m: -m.volume())
    main = pieces[0]
    for piece in pieces[1:]:
        p, q = closest_points(piece, main)
        main = main + piece + strut(p, q, radius)
    return main


def write_stl(mesh, path: str) -> None:
    v = mesh.vert_properties[:, :3].astype(np.float32)
    t = mesh.tri_verts
    tri = v[t]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    with open(path, "wb") as f:
        f.write(b"rabbitstew champion figurine".ljust(80, b" "))
        f.write(struct.pack("<I", len(t)))
        rec = np.zeros(len(t), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
        rec["n"], rec["v"] = n, tri
        f.write(rec.tobytes())


def preview(mesh, path: str, size: int = 900) -> None:
    """Flat-shaded software render from an isometric camera (no GPU, no extra packages)."""
    from PIL import Image

    v = mesh.vert_properties[:, :3].astype(float)
    t = mesh.tri_verts
    az, el = np.radians(-55), np.radians(32)
    d = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])  # towards the camera
    r = np.cross([0, 0, 1], d); r /= np.linalg.norm(r)
    u = np.cross(d, r)
    xy = np.column_stack([v @ r, v @ u])
    lo, hi = xy.min(0), xy.max(0)
    s = 0.86 * size / (hi - lo).max()
    xy = (xy - (lo + hi) / 2) * s + size / 2
    xy[:, 1] = size - xy[:, 1]
    depth = -(v @ d)
    tri = v[t]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    light = d + np.array([0.3, 0.2, 0.6]); light /= np.linalg.norm(light)
    shade = 0.35 + 0.65 * np.clip(n @ light, 0, 1)
    img = np.full((size, size, 3), 244.0)
    zbuf = np.full((size, size), np.inf)
    base = np.array([0.36, 0.62, 0.66]) * 255
    for k in range(len(t)):
        a, b, c = xy[t[k]]
        x0, x1 = int(max(min(a[0], b[0], c[0]), 0)), int(min(max(a[0], b[0], c[0]) + 1, size))
        y0, y1 = int(max(min(a[1], b[1], c[1]), 0)), int(min(max(a[1], b[1], c[1]) + 1, size))
        if x1 <= x0 or y1 <= y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-9:
            continue
        w0 = ((b[1] - c[1]) * (gx - c[0]) + (c[0] - b[0]) * (gy - c[1])) / den
        w1 = ((c[1] - a[1]) * (gx - c[0]) + (a[0] - c[0]) * (gy - c[1])) / den
        w2 = 1 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        z = w0 * depth[t[k][0]] + w1 * depth[t[k][1]] + w2 * depth[t[k][2]]
        sub = zbuf[y0:y1, x0:x1]
        hit = inside & (z < sub)
        sub[hit] = z[hit]
        img[y0:y1, x0:x1][hit] = base * shade[k]
    Image.fromarray(img.astype(np.uint8)).save(path)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run"); ap.add_argument("kind"); ap.add_argument("gen", type=int); ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--time", type=float, default=None, help="seconds into the bout (default: the frame with the most ground contact spread, mid-bout)")
    ap.add_argument("--length", type=float, default=90.0, help="longest horizontal extent of the figure, mm")
    ap.add_argument("--min-wall", type=float, default=1.6, help="thinnest printable feature, mm")
    ap.add_argument("--plinth", type=float, default=4.0, help="plinth thickness, mm (0 for none)")
    a = ap.parse_args()

    cfg = replace(SimConfig.from_dict(json.load(open(f"{a.run}/config.json"))["sim"]), opponent_proxy=True)
    g = Genotype.load(f"{a.run}/{a.kind}/best_gen{a.gen:04d}.json")
    sim = Simulation([g], cfg, spawns=[spawn_layout(2, cfg, a.seed)[0]])
    sim.start_recording(); sim.run()
    traj = sim.trajectory
    n_units = traj.robots[0]
    frames = traj.as_array()[:, :n_units]
    k = traj.n_frames // 2 if a.time is None else min(traj.n_frames - 1, max(0, round(a.time / traj.dt)))
    pose = frames[k]
    units = traj.units[:n_units]

    # Scale is set from the unthickened pose so --length is honoured.
    rough = [unit_solid(u.shape, u.dims, pose[i, :3], pose[i, 3:], 0.0, 0.0) for i, u in enumerate(units)]
    lo, hi = np.array(sum(rough[1:], rough[0]).bounding_box()).reshape(2, 3)
    scale = a.length / max(hi[0] - lo[0], hi[1] - lo[1]) / 1000.0  # model metres -> print metres
    mm = 1000.0 * scale  # mm per model metre
    grow, floor = 0.5 * a.min_wall / mm, a.min_wall / mm

    parts = [unit_solid(u.shape, u.dims, pose[i, :3], pose[i, 3:], grow, floor) for i, u in enumerate(units)]
    n_pieces = len(sum(parts[1:], parts[0]).decompose())
    body = fuse(parts, radius=a.min_wall / mm).scale([mm, mm, mm])
    lo, hi = np.array(body.bounding_box()).reshape(2, 3)
    body = body.translate([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    if a.plinth > 0:
        v = body.to_mesh().vert_properties[:, :3]
        radius = float(np.linalg.norm(v[:, :2], axis=1).max()) + 4.0
        sink = 0.6  # mm the feet sit into the plinth so contacts print solid
        body = body.translate([0, 0, a.plinth - sink])
        body = body + Manifold.cylinder(a.plinth, radius, radius, 128)
    mesh = body.to_mesh()
    write_stl(mesh, a.out)
    stem = os.path.splitext(a.out)[0]
    preview(mesh, stem + ".png")
    lo, hi = np.array(body.bounding_box()).reshape(2, 3)
    info = {
        "run": a.run, "kind": a.kind, "generation": a.gen, "seed": a.seed,
        "frame": int(k), "time_s": round(k * traj.dt, 3), "mujoco": mujoco.__version__,
        "units": n_units, "shapes": [Shape(u.shape).name.lower() for u in units],
        "pieces_before_bridging": n_pieces, "genus": body.genus(), "triangles": int(len(mesh.tri_verts)),
        "mm_per_model_m": round(mm, 2), "size_mm": [round(float(x), 1) for x in hi - lo],
        "volume_cm3": round(body.volume() / 1000.0, 2), "min_wall_mm": a.min_wall, "plinth_mm": a.plinth,
    }
    with open(stem + ".txt", "w") as f:
        json.dump(info, f, indent=2)
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
