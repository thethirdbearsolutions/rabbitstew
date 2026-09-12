"""RBT-45: how far does the mutation operator reach, with no world and no selection?

Counts how often a two-nose (Braitenberg) pairing is *proposed* by the mutation
operator alone.  No Simulation, no bouts, no ranking: a parent is drawn from an
evolved population, the operator is applied ``k`` times in succession (the child
of one mutation is the parent of the next, which is what drift does), and the
final genotype is synthesised and scored for wiring.  Nothing is ever kept for
being better than anything else.

Wiring is read with the same quantity the evolved runs reported as 0.0:
``analysis.sensor_influence`` -- total absolute weight along paths of up to four
links from a sensor to the live effectors.  The one thing this script adds is a
per-effector decomposition of that same sum, so that a pairing can be split into
uncrossed (each wheel nose reaching its own wheel) and crossed (each reaching the
other's, which is the circuit that actually steers up a gradient).  The
decomposition is asserted equal to ``sensor_influence`` at startup.

Usage:  python reach.py [--out DIR] [--n 2000] [--workers 4] [--smoke]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import zlib
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

from rabbitstew.analysis import _parent_pool, _run_config, read_lineage, sensor_influence
from rabbitstew.genetics import mutate, mutate_controller
from rabbitstew.genotype import JointType
from rabbitstew.synthesis import synthesize

RUN_DIR = "runs/RBT-23/W4b-801"
MASTER_SEED = 20260912  # stated in the report; every lineage's seed derives from it
K_VALUES = (1, 2, 5, 10, 20, 50, 100, 200)
ADD_RATES = (0.0, 0.15, 0.3, 0.6, 1.0)
REMOVE_RATES = (0.0, 0.05, 0.1, 0.2)
#: extra checkpoints at the median and maximum ancestral depth the real run reaches,
#: so the headline sentence can be read off directly rather than interpolated.
REALISTIC_K = (19, 23)
DEPTH = 4  # matches sensor_influence's default

_CFG = None
_POOLS = {}


def config():
    global _CFG
    if _CFG is None:
        _CFG = _run_config(RUN_DIR)
    return _CFG


def parents(kind):
    if kind not in _POOLS:
        _POOLS[kind] = _parent_pool(RUN_DIR, kind)
    return _POOLS[kind]


# --------------------------------------------------------------------------- #
# Wiring readout
# --------------------------------------------------------------------------- #


def _live_effectors(ph):
    """Exactly the ``live`` set sensor_influence uses."""
    return [
        i
        for i, ui in enumerate(ph.units)
        if ui.unit.kind == "effector"
        and ui.part is not None
        and ph.parts[ui.part].parent is not None
        and ph.parts[ui.part].joint_type != JointType.FIXED
    ]


def influence_split(ph, depth=DEPTH):
    """``(sensor_idx_list, live_idx_list, totals)`` where ``totals[s][e]`` is the part
    of ``sensor_influence``'s number for sensor ``s`` that lands on live effector ``e``.

    Same matrix, same 3.0 clamp, same path depth as ``analysis.sensor_influence``;
    the only difference is that the live effectors are not summed over.
    """
    n = len(ph.units)
    sensors = [i for i, ui in enumerate(ph.units) if ui.unit.kind == "sensor"]
    live = _live_effectors(ph)
    if n == 0 or not sensors:
        return sensors, live, np.zeros((len(sensors), len(live)))
    M = np.zeros((n, n))
    for s, d, w in ph.links:
        M[d, s] += abs(w)
    M = np.minimum(M, 3.0)
    if not live:
        return sensors, live, np.zeros((len(sensors), len(live)))
    V = np.zeros((n, len(sensors)))
    for col, s in enumerate(sensors):
        V[s, col] = 1.0
    totals = np.zeros((len(live), len(sensors)))
    for _ in range(depth):
        V = M @ V
        totals += V[live, :]
        if not V.any():
            break
    return sensors, live, totals.T


def _food_sensors(ph):
    return [i for i, ui in enumerate(ph.units) if ui.unit.kind == "sensor" and ui.unit.source == "food"]


def measure_conventional(ph):
    """PAIR / HALF / CHASSIS plus the crossed / uncrossed split, for the Pioneer."""
    sensors, live, totals = influence_split(ph)
    pos = {s: i for i, s in enumerate(sensors)}
    food = _food_sensors(ph)
    total_by_sensor = totals.sum(axis=1)

    def wired(u):
        return bool(total_by_sensor[pos[u]] > 0)

    chassis = [u for u in food if ph.units[u].part == 0]
    wheels = [u for u in food if ph.units[u].part != 0]
    wheel_parts = [ph.units[u].part for u in wheels]
    # the live effector on each wheel part (the Pioneer has exactly one per wheel)
    eff_of_part = {}
    for j, e in enumerate(live):
        eff_of_part.setdefault(ph.units[e].part, j)

    n_wired = sum(1 for u in food if wired(u))
    out = {
        "pair": False,
        "half": False,
        "chassis": bool(chassis) and wired(chassis[0]),
        "uncrossed": False,
        "crossed": False,
        "food_wired": n_wired,
        "links": sum(len(b.links) for _, b in ph.genotype.brains()),
        "units": len(ph.units),
    }
    if len(wheels) != 2 or len(set(wheel_parts)) != 2:  # pragma: no cover - body is fixed
        raise RuntimeError(f"expected two wheel noses on two parts, got parts {wheel_parts}")
    a, b = wheels
    pa, pb = wheel_parts
    out["pair"] = wired(a) and wired(b)
    out["half"] = wired(a) != wired(b)
    # The magnitudes behind the booleans.  "Wired" is influence > 0, which is what the
    # evolved runs reported, but an evolved wheel nose can be wired at 0.2 against a
    # chassis nose at 350, so the strength a pairing arrives at is worth carrying.
    out["chassis_infl"] = round(float(total_by_sensor[pos[chassis[0]]]), 4) if chassis else 0.0
    out["pair_strength"] = round(float(min(total_by_sensor[pos[a]], total_by_sensor[pos[b]])), 4)
    if pa in eff_of_part and pb in eff_of_part:
        ea, eb = eff_of_part[pa], eff_of_part[pb]
        out["uncrossed"] = bool(totals[pos[a], ea] > 0 and totals[pos[b], eb] > 0)
        out["crossed"] = bool(totals[pos[a], eb] > 0 and totals[pos[b], ea] > 0)
        out["uncrossed_strength"] = round(float(min(totals[pos[a], ea], totals[pos[b], eb])), 4)
        out["crossed_strength"] = round(float(min(totals[pos[a], eb], totals[pos[b], ea])), 4)
    else:  # pragma: no cover - the Pioneer always has a live effector on each wheel
        out["uncrossed_strength"] = out["crossed_strength"] = 0.0
    return out


def measure_holistic(ph):
    """The same readout where the body is not fixed.

    There is no chassis and no pair of wheels to name, so: PAIR = food sensors on
    two or more *distinct parts* are wired (two noses in two places, which is what
    a pairing needs); HALF = exactly one food sensor is wired anywhere; CHASSIS =
    a food sensor on the root part is wired.  Crossed / uncrossed is undefined
    without a designated left and right wheel and is not reported.
    """
    sensors, live, totals = influence_split(ph)
    pos = {s: i for i, s in enumerate(sensors)}
    food = _food_sensors(ph)
    total_by_sensor = totals.sum(axis=1)
    wired = [u for u in food if total_by_sensor[pos[u]] > 0]
    parts_wired = {ph.units[u].part for u in wired}
    return {
        "pair": len(parts_wired) >= 2,
        "half": len(wired) == 1,
        "chassis": any(ph.units[u].part == 0 for u in wired),
        "uncrossed": None,
        "crossed": None,
        "food_wired": len(wired),
        "food_sensors": len(food),
        "links": sum(len(b.links) for _, b in ph.genotype.brains()),
        "units": len(ph.units),
    }


# --------------------------------------------------------------------------- #
# One cell of the grid
# --------------------------------------------------------------------------- #


def cell_id(cell):
    return f"{cell['kind']}|add{cell['add']}|rem{cell['rem']}|k{cell['k']}"


def run_chunk(task):
    cell, lo, hi = task
    cfg = config()
    pool = parents(cell["kind"])
    mcfg = replace(cfg.mutation, add_link_rate=cell["add"], remove_link_rate=cell["rem"])
    op = mutate if cell["kind"] == "holistic" else mutate_controller
    measure = measure_holistic if cell["kind"] == "holistic" else measure_conventional
    cid = cell_id(cell)
    rows = []
    for i in range(lo, hi):
        # crc32, not hash(): Python's string hash is randomised per process, so
        # hash() would make the seeds irreproducible across invocations.
        rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, zlib.crc32(cid.encode()), i]))
        g = pool[i % len(pool)]
        for _ in range(cell["k"]):
            g = op(g, rng, mcfg)
        rows.append(measure(synthesize(g, cfg.sim.synthesis)))
    return cid, rows


def summarise(cell, rows):
    n = len(rows)
    out = {
        "kind": cell["kind"],
        "add_link_rate": cell["add"],
        "remove_link_rate": cell["rem"],
        "k": cell["k"],
        "n": n,
        "pair": sum(r["pair"] for r in rows) / n,
        "half": sum(r["half"] for r in rows) / n,
        "chassis": sum(r["chassis"] for r in rows) / n,
        "pair_count": int(sum(r["pair"] for r in rows)),
        "half_count": int(sum(r["half"] for r in rows)),
        "chassis_count": int(sum(r["chassis"] for r in rows)),
        "mean_links": round(float(np.mean([r["links"] for r in rows])), 3),
        "mean_food_wired": round(float(np.mean([r["food_wired"] for r in rows])), 4),
        "food_wired_hist": {str(k): int(v) for k, v in zip(*np.unique([r["food_wired"] for r in rows], return_counts=True))},
    }
    if cell["kind"] != "holistic":
        out["uncrossed"] = sum(r["uncrossed"] for r in rows) / n
        out["crossed"] = sum(r["crossed"] for r in rows) / n
        out["uncrossed_count"] = int(sum(r["uncrossed"] for r in rows))
        out["crossed_count"] = int(sum(r["crossed"] for r in rows))
    for key in ("pair", "half", "chassis", "uncrossed", "crossed"):
        if key in out:
            p = out[key]
            out[key + "_se"] = round(float(np.sqrt(max(p * (1 - p), 0) / n)), 5)
    if cell["kind"] != "holistic":
        # How strong is the wiring when it arrives?  A ">0" pairing whose influence is
        # 0.01 against a chassis nose's 350 is not the same object as one at 50.
        for name in ("pair", "uncrossed", "crossed"):
            v = np.array([r[name + "_strength"] for r in rows], dtype=float)
            out[name + "_at"] = {str(t): round(float((v > t).mean()), 5) for t in (0.0, 0.1, 1.0, 10.0)}
            nz = v[v > 0]
            out[name + "_strength_q"] = (
                [round(float(q), 4) for q in np.percentile(nz, [25, 50, 75, 95])] if len(nz) else None
            )
        out["mean_chassis_infl"] = round(float(np.mean([r["chassis_infl"] for r in rows])), 2)
    return out


def build_grid(n):
    cells = []
    for add in ADD_RATES:  # conventional, the primary case
        for k in K_VALUES:
            cells.append({"kind": "conventional", "add": add, "rem": 0.1, "k": k, "n": n})
    for k in REALISTIC_K:  # the two depths the real run actually reaches, at the default rate
        cells.append({"kind": "conventional", "add": 0.15, "rem": 0.1, "k": k, "n": n})
    for k in K_VALUES:  # holistic, default operator only, secondary
        cells.append({"kind": "holistic", "add": 0.15, "rem": 0.1, "k": k, "n": n})
    for rem in REMOVE_RATES:  # the removal sweep, at k = 50
        if rem == 0.1:
            continue  # already in the grid above
        cells.append({"kind": "conventional", "add": 0.15, "rem": rem, "k": 50, "n": n})
    return cells


# --------------------------------------------------------------------------- #
# Checks that the readout is the quantity the evolved runs reported
# --------------------------------------------------------------------------- #


def self_test():
    cfg = config()
    pool = parents("conventional")
    hpool = parents("holistic")
    rng = np.random.default_rng(0)
    checked = 0
    for g in list(pool[:8]) + list(hpool[:8]) + [mutate_controller(pool[0], rng, cfg.mutation) for _ in range(4)]:
        ph = synthesize(g, cfg.sim.synthesis)
        ref = {r["unit"]: r["influence"] for r in sensor_influence(ph)}
        sensors, live, totals = influence_split(ph)
        mine = dict(zip(sensors, totals.sum(axis=1)))
        assert set(ref) == set(mine), "sensor sets differ"
        for u in ref:
            assert abs(ref[u] - round(float(mine[u]), 4)) < 1e-3, f"unit {u}: {ref[u]} vs {mine[u]}"
        checked += 1
    print(f"self-test: per-effector split matches sensor_influence on {checked} phenotypes", flush=True)


def parent_baseline():
    """What the 60 saved parents already carry, before any mutation."""
    cfg = config()
    out = {}
    for kind, measure in (("conventional", measure_conventional), ("holistic", measure_holistic)):
        rows = [measure(synthesize(g, cfg.sim.synthesis)) for g in parents(kind)]
        out[kind] = summarise({"kind": kind, "add": None, "rem": None, "k": 0, "n": len(rows)}, rows)
    return out


# --------------------------------------------------------------------------- #
# Lineage depth in the real run: the yardstick
# --------------------------------------------------------------------------- #


def lineage_depth(population="conventional"):
    lin = read_lineage(RUN_DIR)
    recs = {name: r for (pop, name), r in lin.items() if pop == population}
    alive = [r for r in recs.values() if r["generation"] == 599]
    first, longest, shortest = [], [], []
    missing = 0
    for r in alive:
        # depth along the chain of first parents, which is what analysis.ancestry follows
        d, seen, cur = 0, {r["name"]}, r
        while cur["parents"]:
            nxt = cur["parents"][0]
            if nxt not in recs or nxt in seen:
                missing += 1  # a chain that stopped short of a founder, not at one
                break
            seen.add(nxt)
            cur = recs[nxt]
            d += 1
        first.append(d)
        # and over every ancestral path, since crossover makes the ancestry a DAG
        memo = {}

        def walk(name, agg):
            if name in memo:
                return memo[name]
            rec = recs.get(name)
            if rec is None or not rec["parents"]:
                return 0
            memo[name] = 0  # cycle guard
            v = 1 + agg(walk(p, agg) for p in rec["parents"] if p in recs)
            memo[name] = v
            return v

        longest.append(walk(r["name"], lambda xs: max(list(xs) or [0])))
        memo = {}
        shortest.append(walk(r["name"], lambda xs: min(list(xs) or [0])))
    return {
        "population": population,
        "alive_at_599": len(alive),
        "missing_parent_records": missing,
        "first_parent": {
            "median": float(np.median(first)),
            "mean": round(float(np.mean(first)), 2),
            "min": int(min(first)),
            "max": int(max(first)),
            "p25": float(np.percentile(first, 25)),
            "p75": float(np.percentile(first, 75)),
        },
        "longest_path": {"median": float(np.median(longest)), "max": int(max(longest))},
        "shortest_path": {"median": float(np.median(shortest)), "max": int(max(shortest))},
        "first_parent_values": sorted(first),
    }


# --------------------------------------------------------------------------- #


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="runs/RBT-45")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--chunk", type=int, default=100)
    ap.add_argument("--smoke", action="store_true", help="tiny grid, for checking the plumbing")
    args = ap.parse_args()

    n = 40 if args.smoke else args.n
    self_test()

    cells = build_grid(n)
    if args.smoke:
        cells = [c for c in cells if c["k"] in (1, 20)]
    by_id = {cell_id(c): c for c in cells}
    tasks = []
    for c in cells:
        for lo in range(0, c["n"], args.chunk):
            tasks.append((c, lo, min(lo + args.chunk, c["n"])))
    print(f"{len(cells)} cells, {len(tasks)} chunks, n={n} lineages per cell", flush=True)

    t0 = time.time()
    collected = {cid: [] for cid in by_id}
    done = 0
    with Pool(args.workers) as p:
        for cid, rows in p.imap_unordered(run_chunk, tasks, chunksize=1):
            collected[cid].extend(rows)
            done += 1
            if done % 25 == 0 or done == len(tasks):
                print(f"  {done}/{len(tasks)} chunks  {time.time() - t0:.0f}s", flush=True)

    results = [summarise(by_id[cid], collected[cid]) for cid in by_id]
    payload = {
        "master_seed": MASTER_SEED,
        "run_dir": RUN_DIR,
        "n_per_cell": n,
        "depth": DEPTH,
        "k_values": list(K_VALUES),
        "add_rates": list(ADD_RATES),
        "remove_rates": list(REMOVE_RATES),
        "parents": {k: len(parents(k)) for k in ("conventional", "holistic")},
        "parent_baseline": parent_baseline(),
        "lineage_depth": lineage_depth("conventional"),
        "lineage_depth_holistic": lineage_depth("holistic"),
        "cells": sorted(results, key=lambda r: (r["kind"], r["remove_link_rate"], r["add_link_rate"], r["k"])),
        "seconds": round(time.time() - t0, 1),
    }
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "smoke.json" if args.smoke else "cells.json")
    with open(path, "w") as f:
        json.dump(payload, f, indent=1)
    print(f"wrote {path} in {payload['seconds']}s", flush=True)


if __name__ == "__main__":
    sys.exit(main())
