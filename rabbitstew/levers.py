"""The body levers RBT-121's rule R8 says to print beside every holistic-against-designed result (RBT-124).

A fauna difference that goes with a lever difference is attributed to the lever until shown otherwise
(``runs/RBT-121/SYNTHESIS.md`` R8).  Per body, and per line as means, this measures:

* **resting drive**: the share of built Effectors with ``|tanh(bias)| > 0.9``, i.e. a motor held at 90% or more of
  full throttle with zero input (RBT-121 audit B, finding 1; the Effector-bias walk);
* **ghost-work shares**, over one intact season: the share of actuator work done on joints whose child geom
  touches nothing, and on joints whose child has at least half its volume inside its parent's geom (the RBT-121
  adversary's ``phys_ghost.py``: exact per-actuator work, booked by the child's state at the end of each tick);
  plus the share of parent-child pairs at least half inside at the season's start;
* **motors-off displacement and food**: the same season with every Effector output held at 0 (the "moves by
  itself" null of R3/R7), the centre of mass's horizontal displacement over the season and the items eaten;
* **span**: the body's largest horizontal extent after the settle (geom centres plus bounding radii);
* **reachable and recessive nodes**: genotype nodes reachable from the root, and the rest (which raise the part
  cap for free; audit A, A4);
* the seconds the settle used (``settle_until_rest`` logs them; the plain settle is its fixed ``settle_time``), and
  the deepest penetration between two of the body's own geoms after it (``self_pen``): a body whose parts are jammed
  into each other never comes to rest, because the contact solver keeps pushing them apart (runs/RBT-124/DESIGN.md).

    python -m rabbitstew.levers [--config CONFIG_JSON] [--draw TERRAIN:START] [--per-group K] [--workers W]
                                [--ball-cone RAD] [--hinge-range RAD] [--settle-until-rest EPS] NAME=DIR [NAME=DIR ...]

Each DIR holds genotype ``.json`` files (a run's ``final/``); the simulation config is read from ``--config`` or the
nearest ``config.json`` above the first DIR (an ``evolve`` run's, with its ``sim`` block, or a bare SimConfig).  The
season is one solo season on the draw's terrain seed and start seed, with ``random_start`` on, as RBT-113's
``decompose.py`` scores.  The RBT-124 flags may be switched on here to read a line under them.  Motor capacity
(Sum gear / (4 x mass), RBT-120) is ``python -m rabbitstew.motors``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from typing import Optional

import mujoco
import numpy as np

from .genotype import Genotype
from .simulation import SimConfig, Simulation, spawn_layout

RESTING = 0.9  #: |tanh(bias)| above which an Effector is at resting drive
NPTS = 256  #: Monte Carlo points per child geom for the inside-volume fraction (phys_ghost.py's)
KEYS = ("resting_drive", "effectors", "nodes", "reachable", "recessive", "parts", "span", "settle_s",
        "work", "work_free", "w_free", "w_v50", "start_v50", "food", "exploded", "off_disp", "off_food", "off_work", "reach_food", "self_pen")


def resting_drive(g: Genotype, sc: Optional[SimConfig] = None) -> tuple[float, int]:
    """Share of the built phenotype's Effector instances with |tanh(bias)| > 0.9, and how many there are."""
    from .synthesis import synthesize

    ph = synthesize(g, (sc or SimConfig()).synthesis)
    b = [ui.unit.bias for ui in ph.units if ui.unit.kind == "effector"]
    return (float(np.mean(np.abs(np.tanh(b)) > RESTING)) if b else 0.0), len(b)


def _local_samples(m, gid, rng) -> np.ndarray:
    t, s = m.geom_type[gid], m.geom_size[gid]
    u = rng.uniform(-1, 1, (NPTS * 4, 3))
    if t == mujoco.mjtGeom.mjGEOM_BOX:
        return u[:NPTS] * s
    if t == mujoco.mjtGeom.mjGEOM_SPHERE:
        return u[np.linalg.norm(u, axis=1) <= 1][:NPTS] * s[0]
    return u[np.linalg.norm(u[:, :2], axis=1) <= 1][:NPTS] * np.array([s[0], s[0], s[1]])


def _inside(m, d, gid, pts) -> np.ndarray:
    t, s = m.geom_type[gid], m.geom_size[gid]
    loc = (pts - d.geom_xpos[gid]) @ d.geom_xmat[gid].reshape(3, 3)
    if t == mujoco.mjtGeom.mjGEOM_BOX:
        return np.all(np.abs(loc) <= s, axis=1)
    if t == mujoco.mjtGeom.mjGEOM_SPHERE:
        return np.linalg.norm(loc, axis=1) <= s[0]
    return (np.linalg.norm(loc[:, :2], axis=1) <= s[0]) & (np.abs(loc[:, 2]) <= s[1])


def static_reach_food(sim: Simulation, ri: int = 0, grid: float = 0.01) -> float:
    """The items a body that never moves from its settled pose eats in expectation from the season's first placement.

    An item is placed uniformly in the food disc at least ``clearance`` from the robot's root, and is eaten when it lies
    within ``eat_radius`` of any geom centre (``Simulation._eat``).  So a still body eats, in expectation,
    ``items x A / (disc area - clearance area)``, where ``A`` is the area within ``eat_radius`` of a geom centre, outside
    the clearance disc and inside the food disc (measured on a ``grid`` m lattice).  Regrowth after an eat adds a second-
    order term, left out.  0 without a food world.  This is the floor motors-off food sits on once the body is at rest.
    """
    f = sim.config.food
    if f is None:
        return 0.0
    idx = sim.robots[ri]
    xy = sim.data.geom_xpos[idx.geoms][:, :2]
    root = sim.data.xpos[idx.root_body][:2]
    lo, hi = xy.min(axis=0) - f.eat_radius, xy.max(axis=0) + f.eat_radius
    gx, gy = np.meshgrid(np.arange(lo[0], hi[0], grid) + grid / 2, np.arange(lo[1], hi[1], grid) + grid / 2)
    pts = np.c_[gx.ravel(), gy.ravel()]
    near = (np.linalg.norm(pts[:, None, :] - xy[None, :, :], axis=2) < f.eat_radius).any(axis=1)
    ok = near & (np.linalg.norm(pts - root, axis=1) >= f.clearance) & (np.linalg.norm(pts, axis=1) <= f.radius)
    free = np.pi * f.radius ** 2 - np.pi * min(f.clearance, f.radius) ** 2
    return float(f.items * ok.sum() * grid * grid / free)


def _sim(g: Genotype, sc: SimConfig, start: int) -> Simulation:
    cfg = replace(sc, random_start=True)
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, start))
    if cfg.food is not None:
        sim.set_food_seed(start)
    return sim


def body_levers(g: Genotype, sc: SimConfig, start: int) -> dict:
    """Every lever of one body on one draw: ``sc`` carries the terrain seed, ``start`` seeds the spawn and food."""
    out = {}
    out["resting_drive"], out["effectors"] = resting_drive(g, sc)
    reach = len(g.reachable_nodes())
    out.update(nodes=len(g.nodes), reachable=reach, recessive=len(g.nodes) - reach)

    # intact season, with the ghost-work shares
    sim = _sim(g, sc, start)
    m, d, idx, ph = sim.model, sim.data, sim.robots[0], sim.phenotypes[0]
    out["parts"] = len(ph.parts)
    out["settle_s"] = float(sim.settle_seconds)
    xy = d.geom_xpos[idx.geoms][:, :2]
    rb = m.geom_rbound[idx.geoms]
    out["span"] = float(max(np.linalg.norm(xy[i] - xy[j]) + rb[i] + rb[j] for i in range(len(xy)) for j in range(len(xy))))
    out["reach_food"] = static_reach_food(sim)
    own = set(idx.geoms)
    pens = [-float(c.dist) for c in d.contact[: d.ncon] if c.geom1 in own and c.geom2 in own]
    out["self_pen"] = max(pens) if pens else 0.0  # the deepest self-contact after the settle (m): a body fighting itself
    rng = np.random.default_rng(0)
    acts: dict = {}
    for (pi, _dof), aid in idx.actuators.items():
        acts.setdefault(pi, []).append(aid)
    pairs = [(p.index, idx.geoms[p.index], idx.geoms[p.parent], _local_samples(m, idx.geoms[p.index], rng)) for p in ph.parts if p.parent is not None]

    def vfrac(gc, gp, loc):
        pts = d.geom_xpos[gc] + loc @ d.geom_xmat[gc].reshape(3, 3).T
        return float(_inside(m, d, gp, pts).mean())

    out["start_v50"] = float(np.mean([vfrac(gc, gp, loc) >= 0.5 for _, gc, gp, loc in pairs])) if pairs else 0.0
    sim.actuator_work = np.zeros(m.nu)
    w_free = w_v50 = 0.0
    n = int(round(sim.config.duration / sim.config.control_dt))
    for _ in range(n):
        before = sim.actuator_work.copy()
        sim.step()
        dw = sim.actuator_work - before
        touched = {int(c.geom1) for c in d.contact[: d.ncon]} | {int(c.geom2) for c in d.contact[: d.ncon]}
        for pi, gc, gp, loc in pairs:
            if pi not in acts:
                continue
            w = float(dw[acts[pi]].sum())
            if w == 0.0:
                continue
            if gc not in touched:
                w_free += w
            if vfrac(gc, gp, loc) >= 0.5:
                w_v50 += w
    W = float(sim.actuator_work.sum())
    out.update(work=W, work_free=w_free, w_free=w_free / W if W > 0 else 0.0, w_v50=w_v50 / W if W > 0 else 0.0, food=float(sim.food_eaten[0]),
               exploded=float(sim.exploded[0]))

    # motors-off season
    sim = _sim(g, sc, start)
    sim.brains[0].effector_output = lambda *a: 0.0
    com0 = sim.center_of_mass(0)[:2].copy()
    sim.run()
    out.update(off_disp=float(np.linalg.norm(sim.center_of_mass(0)[:2] - com0)), off_food=float(sim.food_eaten[0]), off_work=float(sim.work[0]))
    return out


def _job(args):
    gd, sc, start = args
    return body_levers(Genotype.from_dict(gd), sc, start)


def line_summary(rows: list[dict]) -> dict:
    """Means over a line's bodies; the work shares are also pooled (summed ghost work / summed work)."""
    s = {k: float(np.mean([r[k] for r in rows])) for k in KEYS}
    W = sum(r["work"] for r in rows)
    s["w_free_pooled"] = sum(r["w_free"] * r["work"] for r in rows) / W if W > 0 else 0.0
    s["w_v50_pooled"] = sum(r["w_v50"] * r["work"] for r in rows) / W if W > 0 else 0.0
    s["off_disp_max"] = max(r["off_disp"] for r in rows)
    s["off_over_005"] = sum(r["off_disp"] > 0.05 for r in rows)
    s["self_pen_over_1cm"] = sum(r["self_pen"] > 0.01 for r in rows)
    s["n"] = len(rows)
    return s


HEADER = (f"{'line':14s} {'n':>3s} {'rest.drive':>10s} {'w_free':>11s} {'w_v50':>11s} {'v50 pairs':>9s} {'work J':>8s} "
          f"{'off disp mean/max':>17s} {'>5cm':>4s} {'off food':>8s} {'food':>6s} {'span':>5s} {'reach':>5s} {'recess':>6s} {'settle s':>8s} {'pen>1cm':>6s}")


def format_row(name: str, s: dict) -> str:
    """One line of the table: shares as mean/pooled, displacement as mean/max."""
    return (f"{name:14s} {s['n']:3d} {s['resting_drive']:10.3f} {s['w_free']:.2f}/{s['w_free_pooled']:.2f}".ljust(40)
            + f" {s['w_v50']:.2f}/{s['w_v50_pooled']:.2f}".rjust(11) + f" {s['start_v50']:9.2f} {s['work']:8.0f} "
            + f"{s['off_disp']:.3f}/{s['off_disp_max']:.3f}".rjust(17) + f" {s['off_over_005']:4d} {s['off_food']:8.2f} {s['food']:6.2f} "
            + f"{s['span']:5.2f} {s['reachable']:5.1f} {s['recessive']:6.1f} {s['settle_s']:8.2f} {s['self_pen_over_1cm']:6d}")


def _find_config(path: str) -> Optional[str]:
    d = os.path.abspath(path)
    while True:
        c = os.path.join(d, "config.json")
        if os.path.exists(c):
            return c
        up = os.path.dirname(d)
        if up == d:
            return None
        d = up


def load_sim_config(path: str) -> SimConfig:
    """The SimConfig of a run's ``config.json`` (an ``evolve``/``ecology`` config's ``sim`` block, or a bare SimConfig)."""
    with open(path) as f:
        d = json.load(f)
    return SimConfig.from_dict(d["sim"] if "sim" in d else d)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m rabbitstew.levers", description="RBT-121 R8's per-line body levers (RBT-124)")
    ap.add_argument("lines", nargs="+", metavar="NAME=DIR")
    ap.add_argument("--config", default=None)
    ap.add_argument("--draw", default="1131:2131", metavar="TERRAIN:START", help="terrain seed and start seed of the season (default RBT-113's first draw)")
    ap.add_argument("--per-group", type=int, default=0, metavar="K", help="measure K bodies per line, drawn with rng 124 (0: all)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--ball-cone", type=float, default=0.0)
    ap.add_argument("--hinge-range", type=float, default=0.0)
    ap.add_argument("--settle-until-rest", type=float, default=0.0)
    ap.add_argument("--settle-max", type=float, default=5.0)
    a = ap.parse_args(argv)
    named = [x.split("=", 1) for x in a.lines]
    cfgp = a.config or _find_config(named[0][1])
    if cfgp is None:
        ap.error("no config.json found; pass --config")
    sc = load_sim_config(cfgp)
    terrain, start = (int(x) for x in a.draw.split(":"))
    if sc.world.terrain == "random":
        sc = replace(sc, world=replace(sc.world, terrain_seed=terrain))
    sc = replace(sc, world=replace(sc.world, ball_cone=a.ball_cone, hinge_range=a.hinge_range))
    if a.settle_until_rest:
        sc = replace(sc, settle_until_rest=a.settle_until_rest, settle_max=a.settle_max)
    rng = np.random.default_rng(124)
    tasks, keys = [], []
    for name, d in named:
        files = sorted(f for f in os.listdir(d) if f.endswith(".json"))
        if a.per_group and a.per_group < len(files):
            files = [files[i] for i in sorted(rng.choice(len(files), a.per_group, replace=False))]
        for f in files:
            tasks.append((Genotype.load(os.path.join(d, f)).to_dict(), sc, start))
            keys.append(name)
    if a.workers > 1:
        with ProcessPoolExecutor(a.workers) as pool:
            res = list(pool.map(_job, tasks, chunksize=1))
    else:
        res = [_job(t) for t in tasks]
    print(f"# rabbitstew.levers: config {cfgp}; draw ({terrain}, {start}); ball_cone {a.ball_cone:g}, hinge_range {a.hinge_range:g}, settle_until_rest {a.settle_until_rest:g}")
    print("# rest.drive: share of Effectors with |tanh(bias)| > 0.9 | w_free / w_v50: share of work on contact-free children / on children >= 50% inside their parent (mean/pooled)")
    print("# v50 pairs: share of parent-child pairs >= 50% inside at the start | off: motors-off season (displacement m, food) | span m | reachable / recessive nodes")
    print("# settle s: seconds the settle used | pen>1cm: bodies whose own geoms interpenetrate by more than 1 cm after it")
    print(HEADER)
    for name in dict.fromkeys(keys):
        print(format_row(name, line_summary([r for r, k in zip(res, keys) if k == name])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
