"""RBT-121 adversary: an independent replica of Ecology.step's demography (ecology.py:505-548), written from the
code, not from audit C's probe_demography.py.  Differences from C's replica, each a thing Ecology.step does:

  * crossover: with probability crossover_rate (0.3) a breeder mates with a uniformly drawn eligible individual
    of its fauna (ecology.py:531-535); for a one-locus type the child takes either parent's type with p = 1/2;
  * initial energy and staggered ages as in the run's config (initial_energy 3.0, ages U[0, max_age));
  * an optional per-birth erosion u (a carrier's child is a non-carrier with probability u), for RBT-80's
    *retention* design (all founders seeded) rather than C's *invasion* design (6 mutants planted).

Gain = Poisson(g) - 0.1 work, as C, so the two replicas differ only in the rules above.

Modes:
  invasion  C's design: 6 mutants (income x mult) among 60, report mean share and fixation at the horizon,
            swept over resident income g0, capacity and horizon; also Ne proxies under energy order.
  retention RBT-80's design: all 60 founders carriers (income gc), erosion u per birth to a non-carrier
            (income gn), 300 seasons; carriage under the committed lottery vs no selection (the drift arm's
            economy: cost 0, threshold 0, birth cost 0, no starvation) vs energy order.

python3 runs/RBT-121/adversary/adv_demography.py [invasion|retention|ne] [reps]
"""
import sys

import numpy as np

THR, BCOST, AGE, INIT, XRATE = 3.0, 1.0, 60, 3.0, 0.3


def season_gain(rng, g):
    return rng.poisson(g) - 0.1


def run(rng, *, cap=60, g_of, n_mut, seasons, rule="lottery", cost=0.25, thr=THR, bcost=BCOST,
        starvation=True, u=0.0, track=False):
    # [type, energy, age, id]
    pop = [[1 if i < n_mut else 0, INIT, int(rng.integers(0, AGE)), i] for i in range(cap)]
    nid = cap
    parents, parent_ages = set(), []
    for s in range(seasons):
        for p in pop:
            p[1] += season_gain(rng, g_of(p[0])) - cost
            p[2] += 1
        pop = [p for p in pop if (p[1] > 0 or not starvation) and p[2] < AGE]
        elig = [p for p in pop if p[1] >= thr]
        if rule == "energy":
            rng.shuffle(elig)
            elig.sort(key=lambda p: -p[1])  # stable: ties keep the shuffle
        else:
            rng.shuffle(elig)
        mates = list(elig)
        for p in elig:
            if len(pop) >= cap:
                break
            t = p[0]
            if XRATE > 0 and len(mates) > 1 and rng.random() < XRATE:
                o = mates[int(rng.integers(0, len(mates)))]
                if o is not p and rng.random() < 0.5:
                    t = o[0]
            if t == 1 and u > 0 and rng.random() < u:
                t = 0
            p[1] -= bcost
            pop.append([t, bcost, 0, nid]); nid += 1
            if track and s >= seasons // 2:
                parents.add(p[3]); parent_ages.append(p[2])
        if not pop:
            break
        if n_mut and not u:
            f = sum(p[0] for p in pop) / len(pop)
            if f in (0.0, 1.0) and not track:
                break
    frac = sum(p[0] for p in pop) / max(1, len(pop))
    return frac, parents, parent_ages


def invasion(reps):
    print("# INVASION (C's design): 6 mutants x mult among cap; share / fixation at horizon; reps =", reps)
    print("# columns: rule, g0 (resident income), mult, cap, horizon -> mean share, fixation rate; neutral share = 6/cap")
    rng = np.random.default_rng(121)
    cells = []
    for g0 in (0.35, 0.5, 0.7, 1.0, 1.3):
        for mult in (1.0, 1.25, 2.0):
            cells.append(("lottery", g0, mult, 60, 400))
    for g0 in (0.5, 1.3):
        cells.append(("energy", g0, 1.25, 60, 400))
        cells.append(("energy", g0, 1.0, 60, 400))
    for cap in (30, 120):
        cells.append(("lottery", 1.3, 2.0, cap, 400))
    cells.append(("lottery", 1.3, 2.0, 60, 1500))
    cells.append(("lottery", 0.5, 2.0, 60, 1500))
    for rule, g0, mult, cap, hor in cells:
        fr = [run(rng, cap=cap, g_of=lambda t, g0=g0, m=mult: g0 * (m if t else 1.0), n_mut=6 if cap == 60 else cap // 10,
                  seasons=hor, rule=rule)[0] for _ in range(reps)]
        fr = np.array(fr)
        print(f"{rule:8s} g0 {g0:4.2f} x{mult:4.2f} cap {cap:3d} T {hor:4d}:  share {fr.mean():.3f}  fix {np.mean(fr == 1.0):.2f}", flush=True)


def retention(reps):
    print("# RETENTION (RBT-80's design): 60 founders all carriers; per-birth erosion u; 300 seasons; reps =", reps)
    print("# carrier income gc, non-carrier income gn (RBT-80 within-arm plateau: carriers 0.97-1.22, non-carriers 0.08-0.64)")
    rng = np.random.default_rng(80)
    for u in (0.06,):
        for gc, gn in ((1.05, 0.08), (1.05, 0.47), (1.05, 0.64), (1.05, 0.84), (1.05, 1.05)):
            out = {}
            for name, kw in (("lottery", dict(rule="lottery")),
                             ("energy", dict(rule="energy")),
                             ("no-sel", dict(cost=0.0, thr=0.0, bcost=0.0, starvation=False))):
                fr = [run(rng, g_of=lambda t, gc=gc, gn=gn: gc if t else gn, n_mut=60, seasons=300, u=u, **kw)[0]
                      for _ in range(reps)]
                out[name] = (np.mean(fr), np.std(fr) / np.sqrt(reps))
            print(f"u {u:.2f} gc {gc:.2f} gn {gn:.2f}:  " + "   ".join(f"{k} {m:.3f}+-{e:.3f}" for k, (m, e) in out.items()), flush=True)


def ne(reps):
    print("# Ne proxies over seasons 200-400 of a neutral population (g0 = 1.3, 60 slots): distinct parents, mean parent age")
    rng = np.random.default_rng(7)
    for rule in ("lottery", "energy"):
        P, A = [], []
        for _ in range(reps):
            _, parents, ages = run(rng, g_of=lambda t: 1.3, n_mut=0, seasons=400, rule=rule, track=True)
            P.append(len(parents)); A.append(np.mean(ages))
        print(f"{rule:8s}: distinct parents in 200 seasons {np.mean(P):6.1f}   mean age at breeding {np.mean(A):5.1f}", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "invasion"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    {"invasion": invasion, "retention": retention, "ne": ne}[mode](reps)
