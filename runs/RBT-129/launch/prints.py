"""RBT-129 pre-launch prints (DESIGN section 3.1's last bullet, section 5.3(a), adversary S4): what clutter does to the
food, per clutter level and layout, on committed fixtures only.  No sweep arm, cell or founder is run or read.

  footprint     the share of food items lying inside an obstacle's footprint (DESIGN 3.1's "unreachable"), apart
                inside one taller than 0.1 m, and the REACH-LIMITED share (launch adversary S8): inside one taller than
                0.1 m AND deeper than the root's reach from its edge.  Under the centre rule eating is xy-only (an item
                within 0.35 m of an eating geom's centre), so a 0.3 m root standing at the edge reaches 0.35 - 0.15 =
                0.20 m in; under the surface rule (the ruled rule, root + surface) the distance is from the root's
                surface, so it reaches 0.35 m in.  A bump of 0.1 m or less can be driven over.  Only the reach-limited
                share is out of reach.  Terrain, spawns and food are each world's own draws: the point's
                world block (``blocks.py``), terrain seed and start seed k for k in 0..DRAWS-1 (not the sweep's seeds),
                four robots spawned as the ecology spawns a group (``spawn_layout``), the food placed as a fresh arena
                places it (``set_food_seed``).  An item is a point on the ground; the footprint is each obstacle's
                cross-section at z = 0 (a box's rotated rectangle, a cylinder's disc, a sunk sphere's circle).
  per cell      food per new cell: one committed fixture alone in the point's world for one 15 s season, items eaten per
                100 new 0.35 m cells covered (cells under any of its geoms, per control step, less those under it at the
                start; the RBT-113 readout adversary's probe_food.py count).  Fixtures: the designed body driving straight
                (``fixed.drive_straight_genotype(0.6)``, the Pioneer) and the blind full-throttle rod (RBT-121 adversary
                section 7, RBT-125 section C's tumbler, arm 0.45 m).  Neither has a food sensor, so the smell level does
                not matter and the price does not enter food; each (clutter, layout) is read at p = 0.03, smell L.

The fixtures stand in for "each fauna's food per new cell" before launch; the sweep's own per-fauna figure is read from
``steer.py``'s probed members (DESIGN section 5.3(a)).

    python runs/RBT-129/launch/prints.py [--draws 100] [--cell-draws 16] [--procs 4] [--fair '...'] [--eat '...']
        > runs/RBT-129/launch/prints.txt
"""
import argparse
import os
import sys
from dataclasses import replace
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import blocks  # noqa: E402

from rabbitstew.fixed import drive_straight_genotype  # noqa: E402
from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Node, Segment, Shape  # noqa: E402
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402
from rabbitstew.world import Shape as WShape, scenery  # noqa: E402

CELL = 0.35
TALL = 0.1


def sim_config(pid: str, fair=None, eat=blocks.EAT_RULED) -> SimConfig:
    """The point's SimConfig, from its world block's config.json (``blocks.config_dict``)."""
    return SimConfig.from_dict(blocks.config_dict(blocks.world_argv(pid, fair=fair, eat=eat))["sim"])


#: how far into a footprint a root at its edge still eats, by eating rule: under "centre" the eat radius 0.35 m less
#: the 0.3 m root's half-width; under "surface" the eat radius itself (the distance is from the root's surface)
DEEP = {"centre": 0.20, "surface": 0.35}


def footprint_mask(items: np.ndarray, obstacles: list, tall: float = 0.0, margin: float = 0.0) -> np.ndarray:
    """Per item (xy on the ground), whether it lies inside the ground cross-section of an obstacle taller than ``tall``,
    by more than ``margin`` from its edge."""
    inside = np.zeros(len(items), dtype=bool)
    for sc in obstacles:
        x, y = items[:, 0] - sc.pos[0], items[:, 1] - sc.pos[1]
        if sc.shape == WShape.BOX:
            height = sc.dims[2]
            w, h, (qw, qx, qy, qz) = sc.dims[0], sc.dims[1], sc.quat
            yaw = np.arctan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz))
            u = np.cos(yaw) * x + np.sin(yaw) * y
            v = -np.sin(yaw) * x + np.cos(yaw) * y
            hit = (np.abs(u) <= w / 2 - margin) & (np.abs(v) <= h / 2 - margin)
        elif sc.shape == WShape.CYLINDER:
            height = sc.dims[1]
            hit = np.hypot(x, y) <= sc.dims[0] - margin
        else:  # a sphere sunk so that its top is at pos.z + r
            r, zc = sc.dims[0], sc.pos[2]
            height = zc + r
            hit = (np.hypot(x, y) <= np.sqrt(r * r - zc * zc) - margin) if abs(zc) < r else np.zeros(len(items), dtype=bool)
        if height > tall:
            inside |= hit
    return inside


def unreachable(pid: str, draws: int, fair=None, eat=blocks.EAT_RULED) -> tuple:
    """(share inside any footprint, share inside one taller than 0.1 m, the reach-limited share (taller than 0.1 m and
    deeper than 0.20 m), items) over ``draws`` fresh arenas."""
    base = sim_config(pid, fair=fair, eat=eat)
    deep_margin = DEEP[base.food.eat_rule]
    fixtures = [drive_straight_genotype(0.6)] * 4
    any_in = tall_in = deep_in = total = 0
    for k in range(draws):
        cfg = replace(base, random_start=True, world=replace(base.world, terrain_seed=k))
        sim = Simulation(fixtures, cfg, spawns=spawn_layout(4, cfg, k))
        sim.set_food_seed(k)
        items = np.asarray(sim.food_spots, dtype=float).reshape(-1, 2)
        obs = scenery(sim.config.world) if sim.config.world.terrain == "random" else []
        any_in += int(footprint_mask(items, obs).sum())
        tall_in += int(footprint_mask(items, obs, tall=TALL).sum())
        deep_in += int(footprint_mask(items, obs, tall=TALL, margin=deep_margin).sum())
        total += len(items)
    return any_in / total, tall_in / total, deep_in / total, total


def rod(a: float = 0.45) -> Genotype:
    """RBT-125 section C's blind tumbler (side_effects.py's ``rod``): a 0.3 m cube with one box arm on an unlimited
    hinge at full throttle, no sensor."""
    arm = Segment(Shape.BOX, (float(a), 1.0, 1.0), Brain(units=[Effector(dof=0, bias=3.0)]))
    conn = Connection(child=1, position=(1.0, 0.0, 0.0), scale=1.0, joint_type=JointType.HINGE, axis=(0.0, 0.0, 1.0), joint_limit=None)
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=[])), [conn]), Node(arm)], name="rod")


FIXTURES = {"pioneer-drive": lambda: drive_straight_genotype(0.6), "rod-0.45": rod}


def cell_season(task) -> tuple:
    """One solo season of a fixture: (items eaten, new 0.35 m cells covered)."""
    key, pid, fixture, k, fair, eat = task
    base = sim_config(pid, fair=fair, eat=eat)
    cfg = replace(base, random_start=True, world=replace(base.world, terrain_seed=k))
    sim = Simulation([FIXTURES[fixture]()], cfg, spawns=spawn_layout(1, cfg, k))
    sim.set_food_seed(k)
    geoms = sim.robots[0].geoms
    start = {(int(np.floor(x / CELL)), int(np.floor(y / CELL))) for x, y in sim.data.geom_xpos[geoms][:, :2]}
    cells = set()
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
        for x, y in sim.data.geom_xpos[geoms][:, :2]:
            cells.add((int(np.floor(x / CELL)), int(np.floor(y / CELL))))
    food = 0.0 if sim.exploded[0] else float(sim.food_eaten[0])
    return key, food, len(cells - start)


def per_cell(tasks: list, procs: int) -> dict:
    if procs > 1:
        with get_context("fork").Pool(procs) as pool:
            rows = pool.map(cell_season, tasks, chunksize=2)
    else:
        rows = [cell_season(t) for t in tasks]
    out: dict = {}
    for key, food, cells in rows:
        out.setdefault(key, []).append((food, cells))
    return {k: np.array(v, dtype=float) for k, v in out.items()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draws", type=int, default=100, help="fresh arenas per (clutter, layout) for the unreachable share")
    ap.add_argument("--cell-draws", type=int, default=16, help="solo seasons per (clutter, layout, fixture) for food per new cell")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--fair", default="", help="the fairness flags (RBT-128's '--fair', written --fair=--fair); empty = pending")
    ap.add_argument("--eat", default=" ".join(blocks.EAT_RULED))
    a = ap.parse_args(argv)
    fair, eat = a.fair.split(), a.eat.split()
    print("# RBT-129 pre-launch prints (DESIGN 3.1, 5.3(a), S4): committed fixtures only; no sweep arm, cell or founder")
    print(f"# fairness flags: {' '.join(fair) if fair else 'none given: re-run with --fair=--fair (stages.py prelaunch)'}")
    print(f"# eating rule: {' '.join(eat)}" + ("  (RBT-125 section C, as re-ruled 03:10)" if tuple(eat) == blocks.EAT_RULED else "  (NOT the ruled rule)"))
    print(f"\n## items inside a footprint, and out of reach ({a.draws} fresh arenas each, terrain and start seeds 0..{a.draws - 1})")
    rule = sim_config(blocks.point_id(1.0, 0.03, "U", "L"), fair=fair, eat=eat).food.eat_rule
    print("# 'inside a footprint' is DESIGN 3.1's 'unreachable'.  Only the reach-limited share is out of reach of a root at the")
    print(f"# edge: inside a footprint taller than {TALL} m and deeper than {DEEP[rule]} m from its edge (eat_rule {rule}: "
          + ("the xy eat radius less the root's half-width" if rule == "centre" else "the eat radius, from the root's surface;"
             " footprints are at most 0.7 m across, so no item is deeper than 0.35 m and this share is 0 by geometry") + "; S8)")
    if rule == "surface":
        import stages
        print(f"# surface clearance under clear_from = root (RBT-125 #446) in this tree: {'yes' if stages.surface_clearance_ok() else 'NO: a pre-#446 print'}")
    print("# layout  c    N   R_o   inside a footprint   inside one taller than 0.1 m   reach-limited   items")
    for layout in blocks.LAYOUTS:
        for c in blocks.CLUTTER:
            pid = blocks.point_id(c, 0.03, layout, "L")
            n, radius = blocks.obstacles(c, layout)
            share, tall, deep, total = unreachable(pid, a.draws, fair=fair, eat=eat)
            print(f"  {layout:5s} {c:3.1f} {n:3d}  {radius if n else 0:.1f}   {share:6.3f}               {tall:6.3f}                          {deep:6.3f}          {total}")
    tasks = [((layout, c, fx), blocks.point_id(c, 0.03, layout, "L"), fx, 1000 + k, fair, eat)
             for layout in blocks.LAYOUTS for c in blocks.CLUTTER for fx in FIXTURES for k in range(a.cell_draws)]
    res = per_cell(tasks, a.procs)
    print(f"\n## food per new cell: solo 15 s seasons, {a.cell_draws} draws each (terrain and start seeds 1000..{999 + a.cell_draws})")
    print("# layout  c    fixture         items/season (SE)   new cells/season (SE)  items per 100 new cells")
    for layout in blocks.LAYOUTS:
        for c in blocks.CLUTTER:
            for fx in FIXTURES:
                r = res[(layout, c, fx)]
                se = r.std(axis=0, ddof=1) / np.sqrt(len(r))
                print(f"  {layout:5s} {c:3.1f}  {fx:14s}  {r[:, 0].mean():6.3f} ({se[0]:.3f})     {r[:, 1].mean():7.1f} ({se[1]:5.1f})         {100 * r[:, 0].sum() / max(r[:, 1].sum(), 1):6.2f}")


if __name__ == "__main__":
    main()
