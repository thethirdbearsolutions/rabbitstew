"""RBT-132 fix-check, item 4: K3's SEEN share on REAL planted hosts, against the caricature's 1.00 / 0.96.

    python runs/RBT-116/design-adversary/rbt132_seen_real.py HOSTS_ROOT [WORKERS] > runs/RBT-116/design-adversary/rbt132_seen_real.txt

probe_power.py takes K3's per-plant SEEN share from the design-stage kinematic caricature (k3_seen_probe.txt: two-nose
1.00, one-nose 0.96 at tau 2 s), and so prints K3 false-VOID 0.000.  Here the planted (a) and (c) plants are built by
planters.py itself (plant_a signed by compass_sign; c_layout, then plant_c at a = 6 split over n links, tuned over its
2 signs on the first 4 draws) on RBT-113 O1's committed U finals, taken in SORTED order (not planters.py's registered
permutation), 8 of each, and called by planters._call with K3's confirmation, exactly as ``planted`` does.

No RBT-129 point, pool, screen, battery or config: a test-only point ``ADV-G`` is registered in this process only (tau 2
s, G 2.5, root + surface), in two fixture worlds: ``short`` (tests/test_rbt132's FIX_G: 4 s, 6 items, radius 2) and
``long`` (15 s, 12 items, radius 3; flat; not --fair).  The battery is 4 + 16 + 16 fixture draws (Draw(700 + i, 800 + i)),
unscreened.
"""
import importlib.util
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-116"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


T = load("t132", os.path.join(ROOT, "tests", "test_rbt132.py"))
planters, steer = T.planters, T.steer
pp = load("pp", os.path.join(ROOT, "runs", "RBT-116", "probe_power.py"))
from rabbitstew.genotype import Genotype  # noqa: E402

PT = "ADV-G"
steer.REGISTERED_POINTS[PT] = {"smell_contrast": 2.5, "smell_tau": 2.0, "eat_from": "root", "eat_rule": "surface",
                               "clear_from": "root", "eat_radius": 0.35}
WORLDS = {"short": T.FIX_G,
          "long": replace(T.FIX_G, duration=15.0, food=replace(T.FIX_G.food, items=12, radius=3.0))}
DR = [steer.Draw(700 + i, 800 + i) for i in range(36)]
BAT = steer.Battery(DR[:4], DR[4:20], DR[20:36])
N = 8


def finals(root, kind):
    out = []
    for s in planters.HOST_SEEDS:
        d = os.path.join(root, "O1", str(s), "U", kind, "final")
        out += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f[:-5].isdigit()]
    return out


def build(root, cfg):
    season = steer.point_season(PT)
    a, c = [], []
    for f in finals(root, "conventional"):
        if len(a) == N:
            break
        g = Genotype.load(f)
        sign = planters.compass_sign(g, cfg)
        if sign is not None:
            a.append(planters.plant_a(g, sign))
    for f in finals(root, "holistic"):
        if len(c) == N:
            break
        g = Genotype.load(f)
        geom = planters.body_geometry(g, cfg, DR[0])
        lay = planters.c_layout(g, geom) if geom is not None else None
        if lay is None:
            continue
        best, _, _ = planters.tune([planters.plant_c(g, lay, s) for s in (+1.0, -1.0)], cfg, DR[:4], season)
        c.append(best)
    return a, c


def main():
    root = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    print("# rbt132_seen_real.py: K3 SEEN on planters.py's own (a) and (c) plants, RBT-113 O1 hosts (sorted order), test-only point, fixture worlds")
    for wname, cfg in WORLDS.items():
        a, c = build(root, cfg)
        args = [(g.to_dict(), cfg.to_dict(), BAT.to_dict(), PT, True) for g in a + c]
        with ProcessPoolExecutor(w) as ex:
            recs = list(ex.map(planters._call, args, chunksize=1))
        ra, rc = recs[:len(a)], recs[len(a):]
        print(f"\n## world {wname} (duration {cfg.duration} s, {cfg.food.items} items, radius {cfg.food.radius})")
        for key, gs, rs in (("a", a, ra), ("c", c, rc)):
            for g, r in zip(gs, rs):
                s2 = r.get("stage2") or {}
                cf = r.get("confirm") or r.get("k3_confirm") or {}
                print(f"  ({key}) {g.name[-34:]:34s} call {r['call']:9s} stage {r['stage']} F {s2.get('F', float('nan')):+.3f} "
                      f"lbdT {s2.get('lbdT', float('nan')):+.3f} c3 {s2.get('c3')} | confirm c2 {cf.get('c2')} c3 {cf.get('c3')} | SEEN {planters.seen(r)}")
        sa = np.mean([planters.seen(r) for r in ra]) if ra else float("nan")
        sc = np.mean([planters.seen(r) for r in rc]) if rc else float("nan")
        kk = planters.k3_k4({"a": ra, "c": rc})
        print(f"# {wname}: SEEN share (a) {sa:.2f} of {len(ra)}, (c) {sc:.2f} of {len(rc)}; confirmed STEERS (a) "
              f"{np.mean([r['call'] == steer.STEERS for r in ra]):.2f}, (c) {np.mean([r['call'] == steer.STEERS for r in rc]):.2f}; "
              f"K3 on these 16: {'PASS' if kk['K3'] else 'FAIL'} {kk['K3_seen']}; K3 false-VOID at these shares {pp.k3_false_void(sa, sc):.3f}")
    print("\n## K3 false-VOID (probe_power.k3_false_void) at a common per-plant SEEN share p")
    print("  " + "  ".join(f"p {p:.2f}: {pp.k3_false_void(p, p):.3f}" for p in (1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1)))
    print("  (a) at p, (c) at 0: " + "  ".join(f"p {p:.2f}: {pp.k3_false_void(p, 0.0):.3f}" for p in (1.0, 0.5)))


if __name__ == "__main__":
    main()
