"""Analyse the RBT-65 paired arms: did selection hold the compass?

Reports, per arm, across the saved best-of-season genotypes:

  realised a   the signed steering gain, structural (free, no simulation),
               RE-SIGNED against that individual's own direction of travel so
               that a carrier whose gait inverted is counted as loss-by-
               inversion and not as loss-by-selection (RBT-65 amendment 3)
  direction    travel azimuth minus body yaw, per best
  yield        from history.json, per season, both arms

and the realised search depth, because "selection did not hold it over N
seasons" means nothing without knowing how many reproduction events N bought
(RBT-59: 600 seasons is a median of ~20).

Usage: python scripts/rbt65_analyse.py [out-dir]
"""
import glob, json, os, sys, numpy as np
from dataclasses import replace
from multiprocessing import Pool
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
import importlib.util
_d = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("cvf", os.path.join(_d, "compass_vs_flip.py"))
cvf = importlib.util.module_from_spec(_s); _s.loader.exec_module(cvf)

OUT = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-65"
ARMS = tuple(a for a in ("seeded", "control", "drift")
             if os.path.isdir(f"{OUT}/{a}/conventional"))
SEEDS = 4


def wrap(a):
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def probe(task):
    arm, gen = task
    cfg = SimConfig.from_dict(json.load(open(f"{OUT}/{arm}/config.json"))["sim"])
    g = Genotype.load(f"{OUT}/{arm}/conventional/best_gen{gen:04d}.json")
    a, c = cvf.steering_gain(synthesize(g, cfg.synthesis))
    T = []
    for seed in range(9000, 9000 + SEEDS):
        sc = replace(cfg, random_start=True)
        sim = Simulation([g], sc, spawns=spawn_layout(1, sc, seed))
        sim.set_food_seed(seed)
        idx = sim.robots[0]
        last = sim.data.xpos[idx.root_body][:2].copy()
        for _ in range(int(round(sc.duration / sc.control_dt))):
            sim.step()
            if sim.exploded[0]:
                break
            q = sim.data.xquat[idx.root_body]
            yaw = float(np.arctan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] ** 2 + q[3] ** 2)))
            pos = sim.data.xpos[idx.root_body][:2]
            d = pos - last
            if np.linalg.norm(d) > 1e-3:
                T.append(wrap(float(np.arctan2(d[1], d[0])) - yaw))
            last = pos.copy()
    if T:
        head = float(np.degrees(np.arctan2(np.mean(np.sin(T)), np.mean(np.cos(T)))))
    else:
        head = float("nan")
    return arm, gen, (a or 0.0), (c or 0.0), head


def depth(arm):
    """Median generations of descent from a founder: the realised search depth."""
    par = {}
    for line in open(f"{OUT}/{arm}/lineage.jsonl"):
        r = json.loads(line)
        if r["population"] == "conventional":
            par.setdefault(r["name"], r["parents"] or [])
    def up(n, cap=500):
        d, seen = 0, set()
        while par.get(n) and n not in seen and d < cap:
            seen.add(n); n = par[n][0]; d += 1
        return d
    last = [json.loads(l) for l in open(f"{OUT}/{arm}/lineage.jsonl")]
    gmax = max(r["generation"] for r in last)
    final = [r["name"] for r in last if r["population"] == "conventional" and r["generation"] == gmax]
    return np.median([up(n) for n in final]) if final else float("nan")


if __name__ == "__main__":
    gens = sorted(int(f.split("best_gen")[1][:4])
                  for f in glob.glob(f"{OUT}/seeded/conventional/best_gen*.json"))
    with Pool(4) as p:
        rows = p.map(probe, [(a, g) for a in ARMS for g in gens])
    R = {(a, g): (aa, cc, h) for a, g, aa, cc, h in rows}

    print("RBT-65: can selection hold a compass it is given?")
    print(f"arms present: {', '.join(ARMS)}\n")
    head = " | ".join(f"{a} a | {a} dir" for a in ARMS)
    print(f"| season | {head} |")
    print("|---" * (1 + 2 * len(ARMS)) + "|")
    for g in gens:
        cells = []
        for a in ARMS:
            aa, _, hh = R[(a, g)]
            cells.append(f"{aa:+.2f}")
            cells.append(f"{hh:+.0f}° {'BACK' if abs(hh) > 90 else 'fwd'}")
        print(f"| {g} | " + " | ".join(cells) + " |")

    print("\n### Gain retention, re-signed against each champion's own direction\n")
    print("| arm | a at start | a at end | >= +16 | >= +32 | wrong sign | median |")
    print("|---|---|---|---|---|---|---|")
    summ = {}
    for a in ARMS:
        vals = np.array([R[(a, g)][0] for g in gens])
        heads = np.array([R[(a, g)][2] for g in gens])
        # re-sign: a compass is "correct" relative to the direction THIS champion drives.
        # The founders drove backward; a champion that flipped needs the opposite sign,
        # so flip its measured gain before asking whether it still carries a compass.
        base_back = abs(np.nanmedian([R[("seeded", g)][2] for g in gens])) > 90
        signed = np.array([v if ((abs(h) > 90) == base_back) else -v for v, h in zip(vals, heads)])
        summ[a] = signed
        print(f"| {a} | {signed[0]:+.1f} | {signed[-1]:+.1f} | {int((signed>=16).sum())}/{len(signed)} | "
              f"{int((signed>=32).sum())}/{len(signed)} | {int((signed<0).sum())}/{len(signed)} | {np.median(signed):+.1f} |")

    if "drift" in ARMS and "seeded" in ARMS:
        sd, dr = summ["seeded"], summ["drift"]
        print(f"\n### THE KEY COMPARISON: seeded (selection on) vs drift (economy flattened)\n")
        print(f"  seeded median a {np.median(sd):+.1f}, still >= +16 in {int((sd>=16).sum())}/{len(sd)} snapshots")
        print(f"  drift  median a {np.median(dr):+.1f}, still >= +16 in {int((dr>=16).sum())}/{len(dr)} snapshots")
        if (dr >= 16).mean() > 0.8:
            print("\n  Drift retains the compass too. Retention is therefore NOT evidence of")
            print("  selection: ~11 reproduction events is simply too few for mutation to")
            print("  destroy it. This arm CANNOT separate 'held and tuned up' from 'held but")
            print("  inert', and saying otherwise would be reading a null as a result.")
        elif (sd >= 16).mean() - (dr >= 16).mean() > 0.3:
            print("\n  Drift loses it while selection keeps it: selection is ACTIVELY")
            print("  maintaining the compass. That is outcome 1 proper.")
        else:
            print("\n  Intermediate: report the two rates and do not force a verdict.")

    for arm in ARMS:
        h = json.load(open(f"{OUT}/{arm}/history.json"))["history"]
        conv = [e for e in h if e["population"] == "conventional"]
        early = [e["mean_lifetime_score"] for e in conv[:20]]
        late = [e["mean_lifetime_score"] for e in conv[-20:]]
        print(f"{arm}: mean lifetime score {np.mean(early):.3f} (first 20) -> {np.mean(late):.3f} (last 20)"
              f"   realised search depth {depth(arm):.0f} reproduction events")
