"""RBT-116 FIX-CHECK item 4 (and 6): does Amendment 2's G8(f) build steer on the fixture across the registered grid?

Amendment 2 (177e052): one food sensor; a global RELU unit fed by the reading at input weight −g, g ∈ {32, 128}; a turn
command ±w, w ∈ {4, 16, 64}, to the Effectors on ONE side of the measured heading; best of 12 by F on screening draws.
Here on the PR's fixture (tests/test_rbt116_steer.py ONE_NOSE_WORLD, now at τ = 1 s; its battery), with a Pioneer host,
a nose on the left wheel, and "one side" = the left drive Effector.  Two eating rules:
  default   the fixture's (eat_from any, centre; clear_from root)
  W1-eat    W1's reconciled rule (addendum 03:10): eat_from root, eat_rule surface, clear_from geoms
Full call_genome on every variant.  Fixture worlds only.
    python3 g8f_grid.py PR_TREE [workers] > g8f_grid.txt
"""
import importlib.util
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

tree = sys.argv[1]
sys.path.insert(0, tree)
spec = importlib.util.spec_from_file_location("tsteer", os.path.join(tree, "tests/test_rbt116_steer.py"))
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
steer = T.steer
from rabbitstew.fixed import LEFT_DRIVE  # noqa: E402
from rabbitstew.genotype import Link, UnitRef  # noqa: E402

WORLDS = {"default": T.ONE_NOSE_WORLD,
          "W1-eat": replace(T.ONE_NOSE_WORLD, food=replace(T.ONE_NOSE_WORLD.food, eat_from="root", eat_rule="surface", clear_from="geoms"))}


def plant(g_in, w):
    g = T._pioneer(noses=(LEFT_DRIVE,), throttle=0.8)
    k = T._unit(g, "relu")
    g.global_brain.links.append(Link(UnitRef(LEFT_DRIVE, 1), UnitRef(None, k), -g_in))
    g.nodes[LEFT_DRIVE].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(LEFT_DRIVE, 0), w))
    assert g.is_valid(), g.validate()
    return g


def job(v):
    wname, g_in, w = v
    try:
        rec = steer.call_genome(plant(g_in, w), WORLDS[wname], T.BATTERY)
    except RuntimeError as e:  # N5: draw_theta found no clear θ on some draw
        return wname, g_in, w, "θ-REFUSED", float("nan"), float("nan"), float("nan")
    s2 = rec.get("stage2") or {}
    return wname, g_in, w, rec["call"], s2.get("F", float("nan")), s2.get("lbdT", float("nan")), s2.get("food_intact", float("nan"))


if __name__ == "__main__":
    grid = [(wn, g_in, w) for wn in WORLDS for g_in in (32.0, 128.0) for w in (4.0, -4.0, 16.0, -16.0, 64.0, -64.0)]
    with ProcessPoolExecutor(int(sys.argv[2]) if len(sys.argv) > 2 else 4) as ex:
        res = list(ex.map(job, grid))
    print(f"# g8f_grid.py: Amendment 2's G8(f) grid, Pioneer host, left-wheel nose, one side; fixture ONE_NOSE_WORLD at τ = {T.ONE_NOSE_WORLD.food.smell_tau}")
    print("world     in gain     w   call        F(stage 2)  lb dT   intact food")
    for wn, g_in, w, call, F, lbt, fi in res:
        print(f"{wn:8s} {-g_in:8.0f} {w:6.0f}   {call:10s} {F:+8.3f}  {lbt:+7.3f}   {fi:6.2f}")
    for wn in WORLDS:
        rows = [r for r in res if r[0] == wn]
        ok = [r for r in rows if r[3] != "θ-REFUSED"] or rows
        best = max(ok, key=lambda r: (r[4] == r[4], r[4]))
        print(f"# {wn}: STEERS on {sum(r[3] == 'STEERS' for r in rows)} of 12; best by F: in {-best[1]:.0f}, w {best[2]:.0f} -> {best[3]} (F {best[4]:+.3f})")
