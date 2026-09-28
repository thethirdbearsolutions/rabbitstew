"""RBT-116 Amendment 3, item 1 (FC-M1): G8(f)'s build by a rule applied to fixtures only.

Candidates, on a Pioneer host with ONE food sensor (the left drive wheel), a rectified (relu) global unit fed by the
reading at input -g, g in {32, 128}:
  (A) Amendment 2's one-side turn: +-w, w in {4, 16, 64}, to the left drive Effector only        (12 builds)
  (B) a turn on both sides: +-w, w in {1, 2, 4, 16, 64}, to both drive Effectors (the Pioneer's steering axis)  (20)
Fixture variants, tau = 1 s, full 4 + 16 + 16 battery:
  F1  ONE_NOSE_WORLD, the test battery (tests/test_rbt116_steer.py BATTERY)
  F2  ONE_NOSE_WORLD under W1's eating block (root, surface, root clearance + the eating guard), the test battery
  F3  ONE_NOSE_WORLD, a second test battery (draws 40-75 of the test stream)
The registered build is every candidate reading STEERS on at least 2 of the 3.  Fixture only: no W1 draw or host.

    python runs/RBT-116/g8f_rule_probe.py [workers] > runs/RBT-116/g8f_rule_probe.txt
"""
import importlib.util
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
spec = importlib.util.spec_from_file_location("tsteer", os.path.join(ROOT, "tests", "test_rbt116_steer.py"))
T = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = T
spec.loader.exec_module(T)
steer = T.steer
from rabbitstew.fixed import LEFT_DRIVE, RIGHT_DRIVE  # noqa: E402
from rabbitstew.genotype import Link, UnitRef  # noqa: E402

D2 = [steer.Draw(100 + i, 200 + i) for i in range(40, 76)]
VARIANTS = {
    "F1": (T.ONE_NOSE_WORLD, T.BATTERY),
    "F2": (replace(T.ONE_NOSE_WORLD, food=replace(T.ONE_NOSE_WORLD.food, eat_from="root", eat_rule="surface", clear_from="root")), T.BATTERY),
    "F3": (T.ONE_NOSE_WORLD, steer.Battery(D2[:4], D2[4:20], D2[20:36])),
}
CANDIDATES = [("A", g, w) for g in (32.0, 128.0) for w in (4.0, -4.0, 16.0, -16.0, 64.0, -64.0)]
CANDIDATES += [("B", g, w) for g in (32.0, 128.0) for w in (1.0, -1.0, 2.0, -2.0, 4.0, -4.0, 16.0, -16.0, 64.0, -64.0)]


def plant(side, g, w):
    body = T._pioneer(noses=(LEFT_DRIVE,), throttle=0.8)
    k = T._unit(body, "relu")
    body.global_brain.links.append(Link(UnitRef(LEFT_DRIVE, 1), UnitRef(None, k), -g))
    for nd in ((LEFT_DRIVE,) if side == "A" else (LEFT_DRIVE, RIGHT_DRIVE)):
        body.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, 0), w))
    assert body.is_valid(), body.validate()
    return body


def job(task):
    cand, var = task
    cfg, bat = VARIANTS[var]
    rec = steer.call_genome(plant(*cand), cfg, bat)
    s2, c = rec.get("stage2") or {}, rec.get("confirm") or {}
    return cand, var, rec["call"], s2.get("F"), c.get("F"), c.get("lbF"), rec.get("theta_refused", 0)


def main():
    tasks = [(c, v) for c in CANDIDATES for v in VARIANTS]
    with ProcessPoolExecutor(int(sys.argv[1]) if len(sys.argv) > 1 else 4) as ex:
        res = list(ex.map(job, tasks, chunksize=1))
    got = {(c, v): r for c, v, *r in res}
    f = lambda x: "    —  " if x is None else f"{x:+7.3f}"
    print(f"# g8f_rule_probe.py: Amendment 3's G8(f) rule; tau = {steer.SMELL_TAU} s; relu unit on the left-wheel nose at input -g")
    print("# per variant: call | stage-2 F | confirmation F, its lower bound | θ refused")
    print(f"{'side':4s} {'g':>5s} {'w':>5s} | " + " | ".join(f"{v:^40s}" for v in VARIANTS) + " | STEERS on")
    registered = []
    for cand in CANDIDATES:
        cells, n = [], 0
        for v in VARIANTS:
            call, F, Fc, lbc, ref = got[(cand, v)]
            n += call == steer.STEERS
            cells.append(f"{call:9s} {f(F)} {f(Fc)} {f(lbc)} {ref:2d}")
        if 2 * n > len(VARIANTS):
            registered.append(cand)
        print(f"{cand[0]:4s} {cand[1]:5.0f} {cand[2]:+5.0f} | " + " | ".join(cells) + f" | {n}/{len(VARIANTS)}" + ("  REGISTERED" if 2 * n > len(VARIANTS) else ""))
    print(f"# registered (STEERS on a majority of F1-F3): {len(registered)} of {len(CANDIDATES)}: "
          + (", ".join(f"{s} g {g:.0f} w {w:+.0f}" for s, g, w in registered) or "NONE"))


if __name__ == "__main__":
    main()
