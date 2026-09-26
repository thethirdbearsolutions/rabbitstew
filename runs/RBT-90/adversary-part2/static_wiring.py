"""RBT-90 part 2 adversary, probe S: what the champions and the births can *causally* do, statically.

No simulation.  The brain (rabbitstew/brain.py) is a dense recurrent net ``a <- f(W a + b)`` whose
sensor rows are overwritten every tick, so a signal reaches an effector only along a directed chain of
links that never passes *into* a sensor.  For each unit class this asks: is there such a chain from it
to a live effector (one RuntimeBrain.effectors would drive: on a part with a parent and a jointed dof)?

  - "linked" oscillator is RBT-28's ``wiring()['osc_linked']`` (any outgoing link), the definition
    oscillator_rate.py and so the part-2 SPLIT use;
  - "live" oscillator / smell sensor has a chain to a live effector.  A lesion of a sensor that is not
    live is a byte-for-byte no-op by construction (forage_lab.trial zeroes its outgoing column only).

Also, for the oscillator SPLIT: where the linked oscillators of the distinct bests came from.  Each
linked-oscillator genome born is either *inherited* (some parent carries a linked oscillator) or
*de novo* (no parent does: mutation or crossover made it).  Following the carrying parent back from
each distinct best reaches its origin: a founder (season 0) or a de novo birth in the run.

usage: static_wiring.py BULK_ROOT [SEED ...]     (BULK_ROOT/forage-SEED as restored by durable.sh)
"""
import glob
import importlib.util
import json
import os
import pathlib
import re
import sys
from collections import Counter, deque

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize

ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("adv", ROOT / "runs" / "RBT-28" / "adversary_founders.py")
adv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adv)

SMELL = ("food", "agent")
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)


def facts(g, cfg):
    ph = synthesize(g, cfg.synthesis)
    us = ph.units
    sensor = {i for i, u in enumerate(us) if u.unit.kind == "sensor"}
    live_eff = {i for i, u in enumerate(us) if u.unit.kind == "effector" and u.part is not None
                and ph.parts[u.part].parent is not None and ph.parts[u.part].joint_type.ndof > 0}
    out = {}
    for s, d, _ in ph.links:
        out.setdefault(s, set()).add(d)

    def reaches(i):
        seen, q = {i}, deque([i])
        while q:
            x = q.popleft()
            for y in out.get(x, ()):
                if y in live_eff:
                    return True
                if y in seen or y in sensor:      # a sensor's row is overwritten: nothing passes through it
                    continue
                seen.add(y)
                q.append(y)
        return False

    osc = [i for i, u in enumerate(us) if u.unit.kind == "sensor" and u.unit.source == "oscillator"]
    sm = [i for i, u in enumerate(us) if u.unit.kind == "sensor" and u.unit.source in SMELL]
    env = [i for i, u in enumerate(us) if u.unit.kind == "sensor" and u.unit.source != "oscillator"]
    w = adv.wiring(g, cfg)
    return {"osc": len(osc), "osc_linked": w["osc_linked"] > 0, "osc_live": any(reaches(i) for i in osc),
            "smell": len(sm), "smell_linked": any(i in out for i in sm), "smell_live": any(reaches(i) for i in sm),
            "env_live": any(reaches(i) for i in env)}


def seed_report(bulk, seed):
    run = pathlib.Path(bulk) / f"forage-{seed}"
    cfg = SimConfig.from_dict(json.load(open(run / "config.json"))["sim"])
    L = [f"== seed {seed}"]
    champ = Genotype.load(run / "holistic" / "best_gen0590.json")
    c = facts(champ, cfg)
    L.append(f"  champion {champ.name}: oscillators {c['osc']} linked {c['osc_linked']} LIVE {c['osc_live']} | "
             f"smell sensors {c['smell']} linked {c['smell_linked']} LIVE {c['smell_live']} | any env sensor live {c['env_live']}")
    genomes = {}
    for p in glob.glob(str(run / "holistic" / "genomes" / "*.json")):
        g = Genotype.load(p)
        d = json.load(open(p))
        genomes[g.name] = (d.get("parents") or [], d["record"].get("born", 0), facts(g, cfg))
    founders = [n for n, (par, born, _) in genomes.items() if not par]
    births = [n for n, (par, born, _) in genomes.items() if par]
    cnt = lambda names, k: sum(genomes[n][2][k] for n in names)
    L.append(f"  founders {len(founders)}: osc linked {cnt(founders, 'osc_linked')}, live {cnt(founders, 'osc_live')}; "
             f"smell linked {cnt(founders, 'smell_linked')}, live {cnt(founders, 'smell_live')}")
    L.append(f"  births {len(births)}: osc linked {cnt(births, 'osc_linked')}, live {cnt(births, 'osc_live')}; "
             f"smell linked {cnt(births, 'smell_linked')}, live {cnt(births, 'smell_live')}")
    names = set()
    for p in sorted(glob.glob(str(run / "holistic" / "best_gen*.json"))):
        if int(re.search(r"best_gen(\d+)", p)[1]) == 0:
            continue
        names.add(Genotype.load(p).name)
    lk = [n for n in names if genomes[n][2]["osc_linked"]]
    lv = [n for n in names if genomes[n][2]["osc_live"]]
    sl = [n for n in names if genomes[n][2]["smell_live"]]
    L.append(f"  distinct bests {len(names)}: osc linked {len(lk)}, osc LIVE {len(lv)}, smell LIVE {len(sl)}")
    # origin of the linked oscillator: inherited vs de novo
    denovo = [n for n in births if genomes[n][2]["osc_linked"] and not any(genomes.get(p, (0, 0, {}))[2].get("osc_linked") for p in genomes[n][0])]
    inher = [n for n in births if genomes[n][2]["osc_linked"] and n not in denovo]
    L.append(f"  linked-oscillator births: de novo {len(denovo)} (no parent carries one), inherited {len(inher)}")

    def origin(n):
        cur, seen = n, set()
        while cur not in seen:
            seen.add(cur)
            par = [p for p in genomes[cur][0] if p in genomes and genomes[p][2]["osc_linked"]]
            if not par:
                return cur
            cur = par[0]
        return cur
    orig = Counter(origin(n) for n in lk)
    L.append("  origins of the distinct bests' linked oscillators: " + (", ".join(
        f"{o} ({'founder' if not genomes[o][0] else 'de novo, born season ' + str(genomes[o][1])}) x{k}" for o, k in orig.most_common()) or "none"))
    return L, {"seed": seed, "champ": c, "founders_osc": cnt(founders, "osc_linked"), "births": len(births),
               "births_osc": cnt(births, "osc_linked"), "births_osc_live": cnt(births, "osc_live"),
               "births_smell_live": cnt(births, "smell_live"), "bests": len(names), "bests_osc": len(lk),
               "bests_osc_live": len(lv), "bests_smell_live": len(sl), "denovo": len(denovo),
               "origins_founder": sum(k for o, k in orig.items() if not genomes[o][0]),
               "origins_denovo": sum(k for o, k in orig.items() if genomes[o][0])}


if __name__ == "__main__":
    bulk = sys.argv[1]
    seeds = [int(a) for a in sys.argv[2:]] or SEEDS
    for s in seeds:
        L, j = seed_report(bulk, s)
        print("\n".join(L))
        print(json.dumps(j), flush=True)
