"""RBT-132 fix-check, item 4 follow-up: is rbt132_seen_real.py's low SEEN share on the (a) plants a SIGN error?

    python runs/RBT-116/design-adversary/rbt132_seen_signflip.py HOSTS_ROOT [WORKERS] > runs/RBT-116/design-adversary/rbt132_seen_signflip.txt

The same 8 RBT-113 O1 designed hosts (sorted order) in rbt132_seen_real.py's ``long`` fixture world, test-only point,
same battery: the (a) plant at compass_sign's sign and at the opposite sign, side by side (lbdT, F, SEEN).  If the
flipped plant climbs (lbdT > 0) where the signed one does not, compass_sign is inverted for these hosts in this world.
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rbt132_seen_real as R  # noqa: E402

planters, steer = R.planters, R.steer


def main():
    root = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    cfg = R.WORLDS["long"]
    plants = []
    for f in R.finals(root, "conventional"):
        if len(plants) == 2 * R.N:
            break
        g = R.Genotype.load(f)
        sign = planters.compass_sign(g, cfg)
        if sign is not None:
            plants += [(os.path.basename(f), sign, planters.plant_a(g, sign)), (os.path.basename(f), -sign, planters.plant_a(g, -sign))]
    args = [(g.to_dict(), cfg.to_dict(), R.BAT.to_dict(), R.PT, True) for _, _, g in plants]
    with ProcessPoolExecutor(w) as ex:
        recs = list(ex.map(planters._call, args, chunksize=1))
    print("# rbt132_seen_signflip.py: (a) at compass_sign's sign vs the opposite, long fixture world, test-only point")
    agg = {"signed": [], "flipped": []}
    for i, ((f, s, g), r) in enumerate(zip(plants, recs)):
        s2 = r.get("stage2") or {}
        which = "signed" if i % 2 == 0 else "flipped"
        agg[which].append((s2.get("lbdT", float("nan")), s2.get("F", float("nan")), planters.seen(r), r["call"]))
        print(f"  {g.name[-22:]:22s} {which:7s} sign {s:+g}: call {r['call']:9s} F {s2.get('F', float('nan')):+.3f} "
              f"dT {s2.get('dT', float('nan')):+.3f} lbdT {s2.get('lbdT', float('nan')):+.3f} | SEEN {planters.seen(r)}")
    for k, v in agg.items():
        a = R.np.array([x[:2] for x in v], float)
        print(f"# {k}: mean lbdT {a[:, 0].mean():+.3f}, mean F {a[:, 1].mean():+.3f}, SEEN {sum(x[2] for x in v)} of {len(v)}, "
              f"STEERS {sum(x[3] == steer.STEERS for x in v)}")


if __name__ == "__main__":
    main()
