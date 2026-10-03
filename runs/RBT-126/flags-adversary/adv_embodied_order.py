"""RBT-126 flags adversary, probe 2: in a real (embodied) Ecology run, does every season's breeding order do what the
PR says, and nothing else?

Wraps rabbitstew.ecology.order_breeders for the length of an Ecology.run() and, at every call, with the breeders'
energies as the embodied code sees them (after the leak and the gain, before births):
  (a) RNG: the generator's state after the call equals its state after a bare ``rng.shuffle`` of the same list, for
      every rule except tickets (tickets: exactly one extra ``choice`` per fauna with >= 2 breeders, replayed with the same weights);
  (b) interleaving: the sequence of fauna in the returned list equals the bare shuffle's, so each fauna takes the same
      number of the season's free slots as under shuffle (the loop takes a prefix of the list);
  (c) within fauna: energy / leakx are in non-increasing energy order, ties in the shuffle's order; shuffle / leak
      return the bare shuffle exactly;
  (d) one fauna (before a merge): the order equals the replica's ``breeding_rules.order`` given the same generator
      state and energies (the replica is the file on the integration branch, passed as argv[1]).
Then, on the run's own outputs, the energy books: energy_t = energy_{t-1} - leak + last_score - cost - birth_cost x
children paid; and each history entry's ``leaked`` = the sum of the rule's leak over that fauna's members entering the
season.  Runs every rule, with and without --merge-after.

python3 adv_embodied_order.py REPLICA_PY OUT_DIR [stress] > adv_embodied_order[_stress].txt   (from a venv with the flags tree installed)
"""
import collections, copy, importlib.util, json, os, sys
import numpy as np

import rabbitstew.ecology as E
from rabbitstew.ecology import Ecology, EcologyConfig, leak_energy, parse_breed_rule
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.simulation import SimConfig, WorldConfig, FoodConfig

spec = importlib.util.spec_from_file_location("breeding_rules", sys.argv[1])
br = importlib.util.module_from_spec(spec)
spec.loader.exec_module(br)
OUT = sys.argv[2]


def evo():
    return EvolutionConfig(seed=11, brain_model="foraging", conventional_topology=True,
                           sim=SimConfig(duration=1.5, random_start=True, score="food", world=WorldConfig(terrain="random"),
                                         food=FoodConfig(items=4, radius=1.5, eat_radius=0.4)))


STRESS = len(sys.argv) > 3 and sys.argv[3] == "stress"  # more merged seasons: longer, larger, cheaper living


def eco(rule, merge):
    if STRESS:
        return EcologyConfig(seasons=14, capacity=12, challenge="foraging", group_size=2, max_age=6, initial_energy=4.0,
                             birth_threshold=1.2, birth_cost=0.5, living_cost=0.02, crossover_rate=0.5, log_every=1000,
                             breed_rule=rule, merge_after=2 if merge else None)
    return EcologyConfig(seasons=8, capacity=8, challenge="foraging", group_size=2, max_age=5, initial_energy=3.0,
                         birth_threshold=1.2, birth_cost=0.5, living_cost=0.05, crossover_rate=0.5, log_every=1000,
                         breed_rule=rule, merge_after=3 if merge else None)


def clone(rng):
    g = np.random.Generator(type(rng.bit_generator)())
    g.bit_generator.state = copy.deepcopy(rng.bit_generator.state)
    return g


stats = collections.Counter()
fails = []
real = E.order_breeders


def checked(breeders, kind, rng, **kw):
    before = list(breeders)
    energies = {id(m): m.record["energy"] for m in before}
    r0 = clone(rng)
    bare = list(before)
    r0.shuffle(bare)
    r_rep = clone(rng)
    got = real(breeders, kind, rng, **kw)
    fau = lambda m: m.record["kind"]
    faunas = {fau(m) for m in before}
    stats["calls"] += 1
    stats["merged calls"] += len(faunas) > 1
    # (a) RNG
    if kind == "tickets":
        for f in sorted(faunas, key=str):
            w = np.array([max(energies[id(m)], 1e-9) for m in bare if fau(m) == f])
            if len(w) > 1:  # the draw's consumption depends on p, so it is replayed with the same weights
                r0.choice(len(w), size=len(w), replace=False, p=w / w.sum())
    if rng.bit_generator.state != r0.bit_generator.state:
        fails.append(f"{kind}: generator state differs from the bare shuffle's (+ tickets draws)")
    # (b) interleaving
    if [fau(m) for m in got] != [fau(m) for m in bare]:
        fails.append(f"{kind}: fauna interleaving differs from the shuffle's")
    if sorted(map(id, got)) != sorted(map(id, before)):
        fails.append(f"{kind}: not a permutation")
    # (c) within fauna
    for f in faunas:
        g = [m for m in got if fau(m) == f]
        s = [m for m in bare if fau(m) == f]
        if kind in ("shuffle", "leak"):
            ok = [id(m) for m in g] == [id(m) for m in s]
        elif kind in ("energy", "leakx"):
            ok = [id(m) for m in g] == [id(m) for m in sorted(s, key=lambda m: -energies[id(m)])]
        else:
            ok = True
        if not ok:
            fails.append(f"{kind}: within-fauna order wrong")
    # (d) the replica, one fauna
    if len(faunas) == 1 and before:
        rule = kind if kind in ("shuffle", "energy", "tickets") else f"{kind}:0.3"
        rep = br.order(r_rep, [[0, energies[id(m)], 0, i, 0, 0.0, 0, None, 0.0, 0.0, 0.0] for i, m in enumerate(before)], rule)
        if [id(before[p[3]]) for p in rep] != [id(m) for m in got]:
            fails.append(f"{kind}: differs from the replica's order")
        stats["replica compared"] += 1
    return got


def books(out, rule):
    kind, lam = parse_breed_rule(rule)
    cfg = eco(rule, False)  # the economy's numbers only
    rows = [json.loads(l) for l in open(os.path.join(out, "lineage.jsonl"))]
    hist = json.load(open(os.path.join(out, "history.json")))["history"]
    by = {(r["population"], r["generation"], r["name"]): r for r in rows if r.get("death") != "cull"}
    kids = collections.Counter((r["population"], r["generation"], r["parents"][0]) for r in rows if r["evals"] == 0 and r["parents"])
    n = worst = 0
    for (p, g, name), r in by.items():
        prev = by.get((p, g - 1, name))
        if prev is None or r["evals"] == 0:
            continue
        e0 = prev["energy"]
        want = e0 - leak_energy(e0, kind, lam, cfg.birth_threshold) + r["last_score"] - cfg.living_cost - cfg.birth_cost * kids[(p, g, name)]
        worst = max(worst, abs(want - r["energy"]))
        n += 1
    lw = 0.0
    nl = 0
    for h in hist:
        if h["season"] == 0 or "leaked" not in h:
            continue
        ent = [r["energy"] for (p, g, _), r in by.items() if p == h["population"] and g == h["season"] - 1]
        lw = max(lw, abs(h["leaked"] - sum(leak_energy(x, kind, lam, cfg.birth_threshold) for x in ent)))
        nl += 1
    has = sum(1 for h in hist if "leaked" in h)
    return f"energy books {n} steps worst {worst:.4f}; leaked entries {has}/{len(hist)}, {nl} checked, worst {lw:.4f}"


E.order_breeders = checked
for merge in ((True,) if STRESS else (False, True)):
    for rule in ("shuffle", "energy", "tickets", "leak:0.3", "leakx:0.3"):
        stats.clear()
        fails.clear()
        out = os.path.join(OUT, f"{rule.replace(':', '_')}{'-merge' if merge else ''}")
        Ecology(evo(), eco(rule, merge), out_dir=out, log=None).run()
        hist = json.load(open(os.path.join(out, "history.json")))["history"]
        births = collections.Counter()
        for h in hist:
            births[h["population"]] += h["births"]
        print(f"{rule:9s} merge={merge!s:5s} | calls {stats['calls']} (merged {stats['merged calls']}, replica compared {stats['replica compared']}) "
              f"| births {dict(births)} | failures {len(fails)} {sorted(set(fails))[:3]} | {books(out, rule)}", flush=True)
