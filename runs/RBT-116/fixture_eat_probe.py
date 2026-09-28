"""RBT-116: do steer.py's fixtures depend on the eating distance rule?  (The coordinator's 03:10 addendum: W1 eats by
`--eat-from root --eat-rule surface`, RBT-125's re-ruled rule.)

On the test fixtures only (tests/test_rbt116_steer.py: FIXTURE and ONE_NOSE_WORLD, now at the registered τ = 1 s) and
the test battery (4 + 16 + 16), the full call_genome under two eating rules: the fixtures' own (`any`, `centre`) and
W1's (`root`, `surface`).  Bodies: the two planted positives, the two planted negatives, and the nine plants of
design-adversary/g8f_probe.py (the evidence Amendment 2's G8(f) grid cites; that probe ran at the fixture's former
τ = 2 s).  No W1 draw, pool season or RBT-116 host.

    python runs/RBT-116/fixture_eat_probe.py [workers] > runs/RBT-116/fixture_eat_probe.txt
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
spec.loader.exec_module(T)
steer = T.steer
from rabbitstew.fixed import LEFT_DRIVE, RIGHT_DRIVE  # noqa: E402
from rabbitstew.genotype import Link, UnitRef  # noqa: E402

RULES = {"any/centre": dict(eat_from="any", eat_rule="centre"), "root/surface": dict(eat_from="root", eat_rule="surface")}


def g8f_plant(func, a, w, both):
    """design-adversary/g8f_probe.py's plant, verbatim."""
    g = T._pioneer(noses=(LEFT_DRIVE,), throttle=0.8)
    k = T._unit(g, func)
    g.global_brain.links.append(Link(UnitRef(LEFT_DRIVE, 1), UnitRef(None, k), a))
    for nd in ((LEFT_DRIVE, RIGHT_DRIVE) if both else (LEFT_DRIVE,)):
        g.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, 0), w))
    return g


BODIES = [("planted two-nose (FIXTURE)", "FIXTURE", ("two",)), ("planted one-nose (ONE_NOSE_WORLD)", "ONE", ("one",)),
          ("negative: no food sensor", "FIXTURE", ("blind",)), ("negative: unwired noses", "FIXTURE", ("unwired",))]
BODIES += [(f"g8f: registered tanh, in 1, one wheel, w {w:+g}", "ONE", ("g8f", "tanh", 1.0, w, False)) for w in (4.0, -4.0, 16.0, -16.0, 64.0, -64.0)]
BODIES += [("g8f: fixture relu, in -128, both wheels, w 2", "ONE", ("g8f", "relu", -128.0, 2.0, True)),
           ("g8f: tanh, in -128, both wheels, w 2", "ONE", ("g8f", "tanh", -128.0, 2.0, True)),
           ("g8f: relu, in -1, one wheel, w 16", "ONE", ("g8f", "relu", -1.0, 16.0, False))]


def build(spec_):
    kind = spec_[0]
    if kind == "two":
        return T.two_nose_steerer()
    if kind == "one":
        return T.one_nose_steerer()
    if kind == "blind":
        return T.sensorless_mover()
    if kind == "unwired":
        return T.unwired_noses()
    return g8f_plant(*spec_[1:])


def job(task):
    label, world, spec_, rule = task
    base = T.FIXTURE if world == "FIXTURE" else T.ONE_NOSE_WORLD
    cfg = replace(base, food=replace(base.food, **RULES[rule]))
    rec = steer.call_genome(build(spec_), cfg, T.BATTERY)
    s2 = rec.get("stage2") or {}
    return label, rule, rec["call"], rec["stage"], s2.get("F"), s2.get("lbdT"), s2.get("food_intact")


def main():
    tasks = [(lab, w, sp, r) for lab, w, sp in BODIES for r in RULES]
    with ProcessPoolExecutor(int(sys.argv[1]) if len(sys.argv) > 1 else 4) as ex:
        rows = list(ex.map(job, tasks, chunksize=1))
    print(f"# fixture_eat_probe.py: steer.call_genome on the test fixtures at τ = {steer.SMELL_TAU} s, test battery 4 + 16 + 16;"
          " eating rule: the fixtures' any/centre against W1's root/surface")
    print(f"{'body':48s} {'eating':13s} {'call':10s} {'stage':>5s} {'F (st.2)':>9s} {'lb dT':>8s} {'food_i':>7s}")
    f = lambda x: "" if x is None else f"{x:+.3f}"
    for lab, rule, call, stage, F, lb, fi in rows:
        print(f"{lab:48s} {rule:13s} {call:10s} {stage:5d} {f(F):>9s} {f(lb):>8s} {'' if fi is None else f'{fi:.2f}':>7s}")


if __name__ == "__main__":
    main()
