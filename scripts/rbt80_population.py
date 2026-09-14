"""RBT-80: compass carriage over the LIVING POPULATION, per season.

RBT-65 could not answer whether selection holds a seeded compass, because the
only witness it saved was the best-of-season champion and `best_lifetime_score`
selects carriers in every arm including drift (RBT-79). The RBT-27 telemetry
(commit 285d9a3) writes every individual's genotype at birth under
`<kind>/genomes/<name>.json`, and `lineage.jsonl` names who is alive each
season, so the population is reconstructable post hoc.

For each living individual: synthesise, compute the realised steering gain `a`
(structural, free), and RE-SIGN it against that individual's own direction of
travel, so a descendant whose gait inverted counts as loss-by-inversion rather
than as a carrier. Threshold at a >= +16.

COST. Direction needs simulation, but it is a property of the genotype, so it
is measured once per NAME and cached - not once per individual-season. The
probe is 2 seeds x 3 s rather than the 4 x 15 s reference; validated at 14/14
agreement on the BACK/fwd classification over the W4b-801 bests, angles within
~10 degrees. That is a tenth of the cost and the classification is what the
re-signing needs.

Usage: python scripts/rbt80_population.py <seed-dir> [every] [procs]
  e.g. python scripts/rbt80_population.py runs/RBT-80/seedA 10 4
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

ROOT = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-80/seedA"
EVERY = int(sys.argv[2]) if len(sys.argv) > 2 else 10
PROCS = int(sys.argv[3]) if len(sys.argv) > 3 else 4
ARMS = [a for a in ("seeded", "control", "drift") if os.path.isdir(f"{ROOT}/{a}")]
THRESH = 16.0
PROBE_SEEDS, PROBE_DUR = 2, 3.0
# The founder population drives BACKWARD (W4b-801, -174 deg). A descendant that
# drives forward needs the opposite steering sign to be chemotactic, so its
# measured `a` is flipped before thresholding.
FOUNDER_BACKWARD = True


def wrap(a):
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def genome_path(arm, name):
    p = f"{ROOT}/{arm}/conventional/genomes/{name}.json"
    return p if os.path.exists(p) else None


def probe(task):
    """(name, re-signed a, c, heading) for one genotype. Direction cached by name."""
    arm, name, cfgd = task
    p = genome_path(arm, name)
    if p is None:
        return name, None, None, None
    cfg = SimConfig.from_dict(cfgd)
    g = Genotype.load(p)
    a, c = cvf.steering_gain(synthesize(g, cfg.synthesis))
    if a is None:
        return name, None, None, None
    T = []
    for s in range(9000, 9000 + PROBE_SEEDS):
        sc = replace(cfg, random_start=True, duration=PROBE_DUR)
        sim = Simulation([g], sc, spawns=spawn_layout(1, sc, s))
        sim.set_food_seed(s)
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
    if not T:
        return name, float(a), float(c or 0.0), None
    head = float(np.degrees(np.arctan2(np.mean(np.sin(T)), np.mean(np.cos(T)))))
    back = abs(head) > 90
    signed = float(a) if (back == FOUNDER_BACKWARD) else -float(a)
    return name, signed, float(c or 0.0), head


def alive_by_season(arm):
    out = {}
    for line in open(f"{ROOT}/{arm}/lineage.jsonl"):
        r = json.loads(line)
        if r["population"] == "conventional":
            out.setdefault(r["generation"], []).append(r["name"])
    return out


if __name__ == "__main__":
    print(f"RBT-80 population carriage — {ROOT}")
    print(f"arms: {', '.join(ARMS)}; seasons sampled every {EVERY}; "
          f"direction probe {PROBE_SEEDS} seeds x {PROBE_DUR:g}s, cached per genotype\n")
    summary = {}
    for arm in ARMS:
        cfgd = json.load(open(f"{ROOT}/{arm}/config.json"))["sim"]
        alive = alive_by_season(arm)
        seasons = sorted(s for s in alive if s % EVERY == 0 or s == max(alive))
        names = sorted({n for s in seasons for n in alive[s]})
        with Pool(PROCS) as p:
            rows = p.map(probe, [(arm, n, cfgd) for n in names], chunksize=8)
        info = {n: (a, c, h) for n, a, c, h in rows}
        missing = sum(1 for n in names if info[n][0] is None)
        print(f"### {arm}: {len(names)} distinct genotypes over {len(seasons)} sampled seasons"
              + (f"  ({missing} genomes missing)" if missing else ""))
        print("| season | alive | carriers | fraction | median a | grad-dominant | inverted |")
        print("|---|---|---|---|---|---|---|")
        traj = []
        for s in seasons:
            live = [info[n] for n in alive[s] if info.get(n, (None,))[0] is not None]
            if not live:
                continue
            A = np.array([x[0] for x in live])
            C = np.array([x[1] for x in live])
            H = [x[2] for x in live]
            carr = int((A >= THRESH).sum())
            inv = sum(1 for a_, h in zip(A, H)
                      if h is not None and ((abs(h) > 90) != FOUNDER_BACKWARD) and abs(a_) >= THRESH)
            gd = int((np.abs(A) > np.abs(C)).sum())
            traj.append((s, len(live), carr / len(live)))
            print(f"| {s} | {len(live)} | {carr} | {carr/len(live):.3f} | {np.median(A):+.1f} "
                  f"| {gd/len(live):.2f} | {inv} |")
        summary[arm] = traj[-1] if traj else None
    print("\n### Carrier fraction at the final sampled season")
    for arm in ARMS:
        if summary.get(arm):
            s, n, f = summary[arm]
            print(f"  {arm:8s} season {s}: {f:.3f}  (n={n})")
    if summary.get("seeded") and summary.get("drift"):
        d = summary["seeded"][2] - summary["drift"][2]
        print(f"\n  seeded − drift = {d:+.3f}   (pre-registered: HELD if >= +0.20, "
              f"NOT HELD if |d| < 0.10; mutation-only floor 0.575 at 11 mutations)")
