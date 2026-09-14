"""RBT-80 re-analysis: the carrier predicate under depth-1, depth-2 and depth-4.

The adversary (RBT-80, 10:18) showed the depth-4 truncated path sum used by
`rbt80_population.py` is manufactured by depth on this ticket's founding pool
(RBT-81: rho = 1.6-4.9, so sum_k W^k diverges), and demonstrated it on the
ticket's own data: seed A's DRIFT arm, with nothing selecting on `a`, climbs
from the installed +64.0 to +71.6 at median while seed C's falls to 1.2.

The coordinator required the predicate re-run on the depth-1 term via
`rabbitstew.analysis.steering_terms`, reporting the verdict quantity under both
predicates side by side.

THE DEPTH-1 TERM IS IDENTICALLY ZERO ON EVERY GENOME IN THIS TICKET, INCLUDING
THE SEEDED FOUNDERS. The motif RBT-65 installs is not the direct four-link
motif: the encoding forbids it (a link into node N may source only from N, the
global brain, or a neighbour, and the two drive wheels are siblings --
genotype.py:496), so `genotype_motif.install` routes it through a global tanh
interneuron. The nose-to-Effector path is therefore length TWO. Depth 1 reads
only direct nose-to-Effector links, of which this population has none:
balance = 0.000 and opposed = 0 on every founder.

So depth 2 -- not depth 1 -- is the shortest-path term that contains the
installed motif, and it is the honest analogue here of what depth 1 is for a
direct motif. All three are reported.

Usage: ./v/bin/python scripts/rbt80_predicates.py <seed-dir> [every] [procs]
"""
import glob, json, os, sys, numpy as np
from dataclasses import replace
from multiprocessing import Pool
from rabbitstew.analysis import steering_terms
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

ROOT = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-80/seedA"
EVERY = int(sys.argv[2]) if len(sys.argv) > 2 else 10
PROCS = int(sys.argv[3]) if len(sys.argv) > 3 else 4
ARMS = [a for a in ("seeded", "control", "drift") if os.path.isdir(f"{ROOT}/{a}")]
THRESH = 16.0
PROBE_SEEDS, PROBE_DUR = 2, 3.0
FOUNDER_BACKWARD = True          # W4b-801 drives BACKWARD (-174 deg)
DEPTHS = (1, 2, 4)
CACHE = os.path.join(ROOT, "dircache.json")


def wrap(a):
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def measure(task):
    """(name, {depth: a}, c, balance, opposed, rho, heading) for one genotype."""
    arm, name, cfgd, known_head = task
    if known_head == "__none__":
        known_head = None
    elif known_head is None:
        known_head = "__probe__"
    p = f"{ROOT}/{arm}/conventional/genomes/{name}.json"
    if not os.path.exists(p):
        return name, None, None, None, None, None, None
    cfg = SimConfig.from_dict(cfgd)
    g = Genotype.load(p)
    ph = synthesize(g, cfg.synthesis)
    st = steering_terms(ph, depth=1)
    if st is None:
        return name, None, None, None, None, None, None
    gains = {1: st["a"]}
    for d in DEPTHS:
        if d != 1:
            gains[d] = steering_terms(ph, depth=d)["path"]["a"]
    base = (st["c"], st["balance"], st["opposed"], st["rho"])
    if known_head != "__probe__":
        return name, gains, base[0], base[1], base[2], base[3], known_head
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
    head = (float(np.degrees(np.arctan2(np.mean(np.sin(T)), np.mean(np.cos(T)))))
            if T else None)
    return name, gains, base[0], base[1], base[2], base[3], head


def alive_by_season(arm):
    out = {}
    for line in open(f"{ROOT}/{arm}/lineage.jsonl"):
        r = json.loads(line)
        if r["population"] == "conventional":
            out.setdefault(r["generation"], []).append(r["name"])
    return out


def resign(a, head):
    """Re-sign the gain against the individual's own direction of travel."""
    if head is None:
        return None
    back = abs(head) > 90
    return float(a) if (back == FOUNDER_BACKWARD) else -float(a)


if __name__ == "__main__":
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    print(f"RBT-80 carrier predicate under depths {DEPTHS} — {ROOT}")
    print(f"arms: {', '.join(ARMS)}; seasons sampled every {EVERY}; "
          f"direction probe {PROBE_SEEDS} seeds x {PROBE_DUR:g}s, cached per genotype")
    print(f"carrier iff re-signed a >= +{THRESH:g}; founder direction BACKWARD\n")
    store = {}
    for arm in ARMS:
        cfgd = json.load(open(f"{ROOT}/{arm}/config.json"))["sim"]
        alive = alive_by_season(arm)
        seasons = sorted(s for s in alive if s % EVERY == 0 or s == max(alive))
        names = sorted({n for s in seasons for n in alive[s]})
        ck = cache.setdefault(arm, {})
        tasks = [(arm, n, cfgd,
                  ("__none__" if ck[n] is None else ck[n]) if n in ck else None)
                 for n in names]
        with Pool(PROCS) as p:
            rows = p.map(measure, tasks, chunksize=8)
        info = {}
        for name, gains, c, bal, opp, rho, head in rows:
            if gains is None:
                continue
            info[name] = dict(gains=gains, c=c, balance=bal, opposed=opp, rho=rho, head=head)
            ck[name] = head
        json.dump(cache, open(CACHE, "w"))
        store[arm] = dict(info=info, alive=alive, seasons=seasons)
        print(f"### {arm}: {len(info)}/{len(names)} genotypes measured over {len(seasons)} seasons")
        print("| season | alive | " + " | ".join(
            f"carr d{d} | frac d{d} | med a d{d}" for d in DEPTHS)
            + " | inverted d2 | balance>0 | opposed<0 | median rho |")
        print("|---" * (2 + 3 * len(DEPTHS) + 4) + "|")
        for s in seasons:
            live = [info[n] for n in alive[s] if n in info]
            if not live:
                continue
            cells = []
            for d in DEPTHS:
                A = np.array([resign(x["gains"][d], x["head"]) for x in live
                              if x["head"] is not None], dtype=float)
                if A.size == 0:
                    cells += ["-", "-", "-"]; continue
                carr = int((A >= THRESH).sum())
                cells += [str(carr), f"{carr/A.size:.3f}", f"{np.median(A):+.1f}"]
            H = [x["head"] for x in live]
            A2 = np.array([resign(x["gains"][2], x["head"]) for x in live
                           if x["head"] is not None], dtype=float)
            inv = sum(1 for a_, h in zip(A2, [h for h in H if h is not None])
                      if ((abs(h) > 90) != FOUNDER_BACKWARD) and abs(a_) >= THRESH)
            bal = sum(1 for x in live if x["balance"] > 0)
            opp = sum(1 for x in live if x["opposed"] < 0)
            rho = np.median([x["rho"] for x in live])
            print(f"| {s} | {len(live)} | " + " | ".join(cells)
                  + f" | {inv} | {bal} | {opp} | {rho:.2f} |")
    json.dump(cache, open(CACHE, "w"))

    # --- verdict quantity, plateau 250-299 and season 299, under each depth ---
    print("\n### Verdict quantity  seeded - drift,  under each predicate")
    print("| readout | " + " | ".join(f"d{d} seeded | d{d} drift | d{d} diff" for d in DEPTHS) + " |")
    print("|---" * (1 + 3 * len(DEPTHS)) + "|")

    def frac(arm, s, d):
        st = store[arm]
        live = [st["info"][n] for n in st["alive"][s] if n in st["info"]]
        A = np.array([resign(x["gains"][d], x["head"]) for x in live
                      if x["head"] is not None], dtype=float)
        return None if A.size == 0 else float((A >= THRESH).mean())

    if "seeded" in store and "drift" in store:
        plateau = [s for s in store["seeded"]["seasons"] if 250 <= s <= 299]
        for label, seasons in (("plateau 250-299", plateau),
                               ("season 299", [max(store['seeded']['seasons'])])):
            cells = []
            for d in DEPTHS:
                sv = np.mean([frac("seeded", s, d) for s in seasons])
                dv = np.mean([frac("drift", s, d) for s in seasons])
                cells += [f"{sv:.3f}", f"{dv:.3f}", f"{sv-dv:+.3f}"]
            print(f"| {label} | " + " | ".join(cells) + " |")
