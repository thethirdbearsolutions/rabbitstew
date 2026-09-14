"""Are champion direction changes lineage turnarounds, or hops between branches?

RBT-77 proposed that evolved chemotactic wiring cannot accumulate because the
gait's direction of travel flips underneath it, inverting the sign that makes a
nose->wheel circuit a compass. That requires direction to change WITHIN a
lineage - a descendant driving opposite to its ancestor.

This tests it directly. Every saved best is measured for travel direction, then
each change in the champion sequence is classified by the pedigree relationship
between the outgoing and incoming champion.

Verdict rule, fixed before running: if direction changes occur on
ancestor->descendant transitions, the trait is labile within a lineage and the
RBT-77 mechanism is available. If every change is a lateral hop between
branches while ancestor->descendant transitions preserve direction, the trait is
stably inherited, the population is a direction POLYMORPHISM rather than a
drifting trait, and the mechanism is not available.

Usage: python scripts/direction_pedigree.py <run-dir>
"""
import json, glob, sys, numpy as np
from dataclasses import replace
from multiprocessing import Pool
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout

RUN = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-23/W4b-801"
cfg = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])


def wrap(a):
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def circ(v):
    return float(np.degrees(np.arctan2(np.mean(np.sin(v)), np.mean(np.cos(v)))))


def direction(gen):
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    T = []
    for seed in range(9000, 9008):
        c = replace(cfg, random_start=True)
        sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
        sim.set_food_seed(seed)
        idx = sim.robots[0]
        last = sim.data.xpos[idx.root_body][:2].copy()
        for _ in range(int(round(c.duration / c.control_dt))):
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
    R = float(np.hypot(np.mean(np.sin(T)), np.mean(np.cos(T)))) if T else 0.0
    return gen, (circ(T) if T else float("nan")), R


def load_pedigree():
    par = {}
    for line in open(f"{RUN}/lineage.jsonl"):
        r = json.loads(line)
        if r["population"] == "conventional":
            par.setdefault(r["name"], r["parents"] or [])
    return par


def ancestors(par, n, maxdepth=400):
    """All ancestors of n with their minimum depth. Handles 1- and 2-parent records."""
    seen, frontier = {}, [(n, 0)]
    while frontier:
        x, d = frontier.pop()
        if x in seen and seen[x] <= d:
            continue
        seen[x] = d
        if d < maxdepth:
            for p in par.get(x, []):
                frontier.append((p, d + 1))
    return seen


def classify(par, a, b):
    if a == b:
        return "same individual", "same"
    A, B = ancestors(par, a), ancestors(par, b)
    if a in B:
        return f"descendant (depth {B[a]})", "lineage"
    if b in A:
        return f"ancestor (depth {A[b]})", "lineage"
    common = set(A) & set(B)
    if not common:
        return "unrelated", "lateral"
    m = min(common, key=lambda x: A[x] + B[x])
    return f"cousins, MRCA {m} at {A[m]}/{B[m]}", "lateral"


if __name__ == "__main__":
    gens = sorted(int(f.split("best_gen")[1][:4])
                  for f in glob.glob(f"{RUN}/conventional/best_gen*.json"))
    with Pool(4) as p:
        rows = p.map(direction, gens)
    par = load_pedigree()
    nparents = [len(v) for v in par.values()]
    name = {g: json.load(open(f"{RUN}/conventional/best_gen{g:04d}.json"))["name"] for g in gens}
    face = {g: ("BACK" if abs(m) > 90 else "fwd") for g, m, R in rows}

    print(f"{RUN}: {len(gens)} champions, "
          f"{sum(1 for g in gens if face[g]=='BACK')} backward / "
          f"{sum(1 for g in gens if face[g]=='fwd')} forward")
    print(f"parents per individual: "
          f"{ {n: nparents.count(n) for n in sorted(set(nparents))} }  "
          f"(reproduction is not purely asexual)")

    changes = lineage = lateral = 0
    same_dir_lineage = 0
    print("\n| gens | champions | direction | relationship | kind |")
    print("|---|---|---|---|---|")
    for i in range(1, len(gens)):
        g0, g1 = gens[i - 1], gens[i]
        desc, kind = classify(par, name[g0], name[g1])
        changed = face[g0] != face[g1]
        if changed:
            changes += 1
            if kind == "lineage":
                lineage += 1
            elif kind == "lateral":
                lateral += 1
            print(f"| {g0}->{g1} | {name[g0]} -> {name[g1]} | "
                  f"{face[g0]} -> {face[g1]} | {desc} | {kind} |")
        elif kind == "lineage":
            same_dir_lineage += 1

    # Consecutive pairs sample every 10th generation, so the champion is almost
    # never a direct descendant of the previous one. That leaves the
    # within-lineage cell EMPTY rather than favourable. Test every ancestor /
    # descendant pair among the champions instead - that is the only cell that
    # speaks to whether the trait is stably inherited.
    anc_pairs = []
    for i in range(len(gens)):
        for j in range(i + 1, len(gens)):
            a, b = name[gens[i]], name[gens[j]]
            if a == b:
                continue
            A = ancestors(par, b)
            if a in A:
                anc_pairs.append((gens[i], gens[j], a, b, A[a],
                                  face[gens[i]], face[gens[j]]))
    print(f"\nAncestor->descendant pairs anywhere among the champions: {len(anc_pairs)}")
    if anc_pairs:
        kept = sum(1 for *_, f0, f1 in anc_pairs if f0 == f1)
        print(f"  direction PRESERVED: {kept}/{len(anc_pairs)}")
        print("\n| ancestor gen | descendant gen | depth | direction |")
        print("|---|---|---|---|")
        for g0, g1, a, b, d, f0, f1 in anc_pairs[:25]:
            print(f"| {g0} ({a}) | {g1} ({b}) | {d} | {f0} -> {f1}"
                  f"{'' if f0==f1 else '  <-- CHANGED'} |")
    else:
        print("  NONE. Within-lineage inheritance of direction is UNTESTED by this data.")

    print(f"\n{changes} direction changes among consecutive champions.")
    print(f"  within a lineage (ancestor<->descendant): {lineage}")
    print(f"  lateral (cousins or unrelated branches):  {lateral}")
    print(f"ancestor<->descendant transitions that PRESERVED direction: {same_dir_lineage}")
    print("\nVERDICT")
    if changes and lineage == 0:
        print("  Every change among consecutive champions is a hop between coexisting")
        print("  branches, not a lineage turning around. So the RBT-77 reading of the")
        print("  50-generation trace - a trait drifting within a lineage - is WRONG.")
    if anc_pairs:
        kept = sum(1 for *_, f0, f1 in anc_pairs if f0 == f1)
        if kept == len(anc_pairs):
            print("  Direction is preserved across every ancestor/descendant pair, so it is")
            print("  stably inherited and the RBT-77 sabotage mechanism is NOT available.")
        else:
            print(f"  But {len(anc_pairs)-kept} ancestor/descendant pair(s) DO differ, so the")
            print("  trait is labile within a lineage after all and the mechanism survives.")
    else:
        print("  Within-lineage inheritance is UNTESTED: no champion is an ancestor of")
        print("  another. Whether a lineage can turn around is not answered by this data,")
        print("  and settling it needs genotypes of non-champions.")
